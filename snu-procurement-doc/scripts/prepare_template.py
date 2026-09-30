#!/usr/bin/env python3
"""
prepare_template.py — SNU 구매문서 HWPX 양식의 "빈칸 개수"를 맞춰주는 전처리 스크립트.

배경
----
문서의 텍스트를 채우는 일은 kordoc MCP(patch_document)가 원본 서식을 100% 보존한 채
처리한다. 다만 kordoc은 문단(블록)을 새로 만들지 못한다:

  - 블록 추가는 미지원 (v1)
  - 셀 내 줄 추가는 문단 생성 미지원 — 마지막 문단에 병합 적용

그래서 양식이 기본 제공하는 슬롯 수(규격 8개, 기타조건 3개 등)보다 많이 쓰려면
채우기 "전에" 빈 문단을 미리 복제해 두어야 한다. 이 스크립트는 그 일만 한다.
텍스트는 한 글자도 쓰지 않는다.

또 하나: 양식의 빈 문단("")은 kordoc이 파싱할 때 사라지므로 patch_document가
건드릴 수 없다. 그래서 이 스크립트는 빈 슬롯에 자리표시자(GS01, PS01, UD01 …)를
넣어 kordoc이 볼 수 있게 만든다.
(별지 제2호의 품명/모델명/제조사/제작국가 칸도 마찬가지로 PNAME-EN, MODEL,
MAKER, COUNTRY 자리표시자를 넣는다. 마지막 열이 비어 있으면 파싱 때 열 자체가 사라진다.)

사용법
------
  python3 prepare_template.py --form 3 --in assets/form3.hwpx --out work/규격서.hwpx \
      --specs 12 --remarks 6 --accessories 3

  python3 prepare_template.py --form 2 --in assets/form2.hwpx --out work/용도설명서.hwpx \
      --general 12 --performance 8 --usage 3

이후 kordoc parse_document → 마크다운 편집 → patch_document 로 채운다.
자리표시자(GS01 …)는 편집 단계에서 전부 실제 내용으로 바꿀 것. 남으면 문서에 그대로 보인다.
"""
import argparse
import copy
import shutil
import sys
import zipfile
from pathlib import Path

from lxml import etree

HP = '{http://www.hancom.co.kr/hwpml/2011/paragraph}'
SECTION = 'Contents/section0.xml'


# --------------------------------------------------------------------------
# 문단 기본 조작
# --------------------------------------------------------------------------
def para_text(p):
    """문단의 모든 <hp:t> 텍스트를 이어붙여 반환."""
    return ''.join(t.text or '' for t in p.iter(f'{HP}t')).strip()


def strip_layout_cache(p):
    """<hp:linesegarray>(줄바꿈 레이아웃 캐시)를 제거.

    남겨 두면 한글이 새 텍스트를 원래 한 줄 높이에 욱여넣으려고 글꼴을 줄인다.
    지우면 한글이 다시 계산해서 정상적으로 줄바꿈한다.
    """
    for lsa in p.findall(f'{HP}linesegarray'):
        p.remove(lsa)


def set_para_text(p, text):
    """문단의 첫 run에 텍스트를 넣고 나머지 run의 텍스트는 비운다."""
    first = True
    for run in p.iter(f'{HP}run'):
        t = run.find(f'{HP}t')
        if t is None:
            t = etree.SubElement(run, f'{HP}t')
        for child in list(t):
            t.remove(child)
        t.text = text if first else ''
        first = False
    strip_layout_cache(p)
    return p


def retarget_block(parent, paragraphs, texts):
    """parent 안의 연속된 paragraphs 구간을 texts 개수에 맞춰 늘리거나 줄인다.

    늘릴 때는 첫 문단을 deep copy 해서 서식을 그대로 물려준다.
    """
    if not paragraphs:
        raise ValueError('대상 문단을 찾지 못했습니다')

    template = paragraphs[0]
    current = list(paragraphs)

    # 부족하면 복제해서 마지막 뒤에 삽입
    while len(current) < len(texts):
        clone = copy.deepcopy(template)
        idx = list(parent).index(current[-1])
        parent.insert(idx + 1, clone)
        current.append(clone)

    # 남으면 제거
    while len(current) > len(texts):
        parent.remove(current.pop())

    for p, text in zip(current, texts):
        set_para_text(p, text)
    return current


# --------------------------------------------------------------------------
# 위치 찾기
# --------------------------------------------------------------------------
def body_paragraphs(root):
    """본문(hs:sec)의 직계 문단 목록."""
    return [ch for ch in root if ch.tag == f'{HP}p']


def find_index(paras, needle, start=0):
    for i in range(start, len(paras)):
        if needle.lower() in para_text(paras[i]).lower():
            return i
    raise ValueError(f'문단을 찾지 못했습니다: {needle!r}')


def collect_numbered(paras, start):
    """start부터 '1.' '2.' … 형태가 이어지는 동안의 문단을 모은다."""
    out = []
    n = 1
    i = start
    while i < len(paras) and para_text(paras[i]).rstrip() == f'{n}.':
        out.append(paras[i])
        n += 1
        i += 1
    return out


def find_cell(root, col, row):
    for tc in root.iter(f'{HP}tc'):
        addr = tc.find(f'{HP}cellAddr')
        if addr is not None and int(addr.get('colAddr')) == col and int(addr.get('rowAddr')) == row:
            return tc
    raise ValueError(f'셀({col},{row})을 찾지 못했습니다')


def set_cell_paragraphs(tc, texts):
    """셀 안의 문단 수를 texts에 맞추고 텍스트를 채운다."""
    sublist = tc.find(f'{HP}subList')
    if sublist is None:
        raise ValueError('셀에 subList가 없습니다')
    paras = sublist.findall(f'{HP}p')
    return retarget_block(sublist, paras, texts)


# --------------------------------------------------------------------------
# 양식별 처리
# --------------------------------------------------------------------------

def make_table_splittable(root, mode='TABLE'):
    """표가 쪽 경계에서 나뉘도록 만든다. 두 가지를 모두 손봐야 한다.

    (1) hp:pos/@treatAsChar = "0"  — "글자처럼 취급" 해제

        이것이 핵심이다. 글자처럼 취급된 개체는 한 글자와 같이 다뤄지므로
        한글은 이를 쪼개지 않는다. 표가 쪽에 안 들어가면 통째로 다음 쪽으로 밀리거나
        쪽 밖으로 넘쳐 잘린다. 이 값이 "1"이면 pageBreak를 무엇으로 두든 소용이 없다.
        배포 양식 중 별지 제3호는 "0"(자리 차지)이라 정상 동작하고,
        별지 제2호만 "1"로 되어 있어 넘침이 발생했다.

    (2) hp:tbl/@pageBreak = "TABLE"  — 쪽 경계에서 "나눔"

    한글 UI의 세 가지 선택지가 HWPX 속성값과 이렇게 대응한다.

        NONE  = 나누지 않음      표가 한 쪽에 안 들어가면 통째로 다음 쪽으로 밀린다
        CELL  = 셀 단위로 나눔   셀 경계에서만 끊는다. 셀 하나가 한 쪽보다 크면 그대로 넘친다
        TABLE = 나눔             셀 하나의 내용도 쪽 경계에서 갈라져 이어진다

    별지 제2호는 문서 전체가 표 하나이고 규격 셀과 용도설명 셀이 각각 한 쪽을 넘길 수
    있으므로 반드시 TABLE이어야 한다. CELL로는 부족하다.

    조판 캐시(linesegarray)를 남겨 두면 한글이 예전 줄 배치를 재사용해서 다시 계산하지
    않으므로 함께 지운다.
    """
    changed = 0
    for tbl in root.iter(f'{HP}tbl'):
        touched = False
        pos = tbl.find(f'{HP}pos')
        if pos is not None and pos.get('treatAsChar') != '0':
            pos.set('treatAsChar', '0')
            touched = True
        if tbl.get('pageBreak') != mode:
            tbl.set('pageBreak', mode)
            touched = True
        for p in tbl.iter(f'{HP}p'):
            strip_layout_cache(p)
        changed += 1 if touched else 0
    return changed


# 이전 이름 호환
def allow_cell_page_break(root):
    return make_table_splittable(root)


def set_table_page_break(root, mode='TABLE'):
    return make_table_splittable(root, mode)


# 양식이 제공하는 작성 안내문 — 최종 문서에 남으면 안 된다.
# Ⅰ. 용도의 '- 어떤 업무에 사용되는 지 기술 -'은 여기 넣지 않는다.
# 그 문단이 용도 본문이 들어갈 유일한 자리라서, 지우면 채울 곳이 사라진다.
GUIDE_NOTES = (
    '특정 모델명이나 특정 방식',
    '설치조건, 보증조건, 훈련 조건, 납기',
)


def remove_guide_notes(root):
    """'- 특정 모델명이나 ... 기재 -' 같은 양식 안내문 문단을 지운다.

    kordoc은 문단을 지우지 못하므로(블록 삭제는 미지원) 채우기 전에 여기서 없앤다.
    Ⅲ, Ⅳ의 안내문은 그 아래 번호 항목이 따로 있어서 덮어쓸 내용이 없으므로 삭제한다.
    """
    removed = 0
    for p in body_paragraphs(root):
        text = para_text(p)
        if any(note in text for note in GUIDE_NOTES):
            root.remove(p)
            removed += 1
    return removed


def prepare_form3(root, specs, remarks, accessories):
    """구매규격서(별지 제3호): 규격/기타조건/부속품 슬롯 수를 맞춘다."""
    make_table_splittable(root)
    paras = body_paragraphs(root)

    # Ⅱ. 장비의 구성 — 'accessories' 아래의 '-' 줄
    acc_start = find_index(paras, 'accessories') + 1
    acc = []
    i = acc_start
    while i < len(paras) and para_text(paras[i]) == '-':
        acc.append(paras[i])
        i += 1
    retarget_block(root, acc, ['-'] * accessories)

    # 인덱스가 바뀌었으므로 다시 읽는다
    paras = body_paragraphs(root)

    # Ⅲ. 성능 및 규격 — '1.' ~ '8.'
    spec_start = find_index(paras, 'Ⅲ. 성능 및 규격') + 2   # 헤딩 + 안내문 다음
    spec_paras = collect_numbered(paras, spec_start)
    retarget_block(root, spec_paras, [f'{n}.' for n in range(1, specs + 1)])

    paras = body_paragraphs(root)

    # Ⅳ. 기타 조건 — '1.' ~ '3.'
    rem_start = find_index(paras, 'Ⅳ. 기타 조건') + 2
    rem_paras = collect_numbered(paras, rem_start)
    retarget_block(root, rem_paras, [f'{n}.' for n in range(1, remarks + 1)])

    # 슬롯 위치를 다 잡은 뒤에 지운다 (먼저 지우면 헤딩 기준 오프셋이 어긋난다)
    notes = remove_guide_notes(root)

    return {'규격': specs, '기타조건': remarks, '부속품': accessories, '안내문 삭제': notes}


def prepare_form2(root, general, performance, usage):
    """용도설명서(별지 제2호): 일반사양/성능/용도설명 줄 수를 맞춘다.

    규격 셀(0,3)은 한 셀 안에 헤딩과 내용이 문단으로 섞여 있다:
        4. 규  격(성능 및 사양) / Ⅰ. 일반사양 / …내용… / Ⅱ. 성능 / …내용…
    """
    make_table_splittable(root)

    # 값 칸을 비워 두면 kordoc 파싱 때 사라지거나(마지막 열) 정렬이 어긋난다.
    # 자리표시자를 넣어 두면 patch_document가 정확히 찾아서 바꿀 수 있다.
    set_cell_paragraphs(find_cell(root, 1, 0), ['(영문) PNAME-EN', '(국문) PNAME-KR'])
    set_cell_paragraphs(find_cell(root, 1, 1), ['MODEL'])
    set_cell_paragraphs(find_cell(root, 1, 2), ['MAKER'])
    set_cell_paragraphs(find_cell(root, 3, 2), ['COUNTRY'])

    spec_cell = find_cell(root, 0, 3)
    texts = ['4. 규  격(성능 및 사양)', 'Ⅰ. 일반사양']
    texts += [f'GS{n:02d}' for n in range(1, general + 1)]
    texts += ['Ⅱ. 성능']
    texts += [f'PS{n:02d}' for n in range(1, performance + 1)]
    set_cell_paragraphs(spec_cell, texts)

    usage_cell = find_cell(root, 0, 4)
    set_cell_paragraphs(
        usage_cell,
        ['5. 사용 용도설명'] + [f'UD{n:02d}' for n in range(1, usage + 1)],
    )

    # 양식의 규격 셀과 용도 셀은 슬롯마다 문단 서식이 다르다(줄간격 130%/160%/고정/230%).
    # 그대로 두면 채운 뒤 줄간격이 들쭉날쭉해지므로 두 셀의 모든 문단을
    # 'Ⅰ. 일반사양' 문단의 서식(160%, 왼쪽 여백 500)으로 통일한다.
    unified = unify_cell_paragraph_style(spec_cell, usage_cell)

    return {'일반사양': general, '성능': performance, '용도설명': usage, '서식 통일': unified}


def unify_cell_paragraph_style(*cells, anchor_text='Ⅰ. 일반사양'):
    """cells 안의 모든 문단 paraPrIDRef를 anchor_text 문단의 값으로 맞춘다."""
    anchor = None
    for tc in cells:
        for p in tc.find(f'{HP}subList').findall(f'{HP}p'):
            if para_text(p) == anchor_text:
                anchor = p.get('paraPrIDRef')
                break
        if anchor:
            break
    if anchor is None:
        return 0
    n = 0
    for tc in cells:
        for p in tc.find(f'{HP}subList').findall(f'{HP}p'):
            if p.get('paraPrIDRef') != anchor:
                p.set('paraPrIDRef', anchor)
                n += 1
    return n


# --------------------------------------------------------------------------
def rewrite_hwpx(src: Path, dst: Path, transform):
    """HWPX(zip) 안의 section0.xml만 바꿔 새 파일로 저장. 나머지는 그대로 복사."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as zin:
        items = zin.infolist()
        section = zin.read(SECTION)
        root = etree.fromstring(section)
        summary = transform(root)
        new_section = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in items:
                data = new_section if item.filename == SECTION else zin.read(item.filename)
                zout.writestr(item, data)
    return summary


def main():
    ap = argparse.ArgumentParser(description='SNU 구매문서 HWPX 양식 슬롯 수 맞추기')
    ap.add_argument('--form', choices=['2', '3'], required=True, help='2=용도설명서, 3=구매규격서')
    ap.add_argument('--in', dest='src', required=True, help='원본 양식 경로')
    ap.add_argument('--out', dest='dst', required=True, help='작업본 저장 경로')
    # form3
    ap.add_argument('--specs', type=int, default=8, help='[form3] Ⅲ. 성능 및 규격 항목 수')
    ap.add_argument('--remarks', type=int, default=3, help='[form3] Ⅳ. 기타 조건 항목 수')
    ap.add_argument('--accessories', type=int, default=2, help='[form3] 부속품 줄 수')
    # form2
    ap.add_argument('--general', type=int, default=10, help='[form2] Ⅰ. 일반사양 줄 수')
    ap.add_argument('--performance', type=int, default=8, help='[form2] Ⅱ. 성능 줄 수')
    ap.add_argument('--usage', type=int, default=3, help='[form2] 사용 용도설명 단락 수')
    args = ap.parse_args()

    src, dst = Path(args.src), Path(args.dst)
    if not src.exists():
        sys.exit(f'원본 양식이 없습니다: {src}')

    if args.form == '3':
        fn = lambda root: prepare_form3(root, args.specs, args.remarks, args.accessories)
    else:
        fn = lambda root: prepare_form2(root, args.general, args.performance, args.usage)

    summary = rewrite_hwpx(src, dst, fn)
    parts = ', '.join(f'{k} {v}칸' for k, v in summary.items())
    print(f'✓ 별지 제{args.form}호 작업본 생성 — {parts}\n  → {dst}')


if __name__ == '__main__':
    main()
