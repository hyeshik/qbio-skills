#!/usr/bin/env python3
"""
prepare_review.py — 연구시설장비 심의요청서(별표 4)와 붙임 유사장비 검토표 양식의
문단·표 행 수를 맞춰주는 전처리 스크립트.

배경
----
두 양식은 assets/ 에 "예시 내용이 채워진" 상태로 들어 있다. 채우기는 kordoc
patch_document가 하지만 kordoc은 문단(블록)을 만들거나 지우지 못하므로,
채우기 전에 여기서 각 칸의 문단 수와 표의 행 수를 새 내용에 맞게 바꾸고
자리표시자를 넣어 둔다. 텍스트 본문은 한 글자도 쓰지 않는다.

문단 서식은 양식이 쓰는 두 종류를 그대로 물려받는다.
  O  = '○ ' 로 시작하는 항목 문단 (paraPr 32)
  -  = '- ' 로 시작하는 세부 문단  (paraPr 33)

사용법
------
심의요청서(별표 4):
  python3 prepare_review.py --form request --in assets/form_review.hwpx --out work/심의요청서_작업본.hwpx \
      --cell t2:r18c2=O--O--O- --cell t2:r21c2=O---O---O--O-O--O-- --cell t2:r22c2=O--O-- \
      --cell t3:r1c1=O---O--- --cell t3:r2c1=O-------O--O--O-O--O --cell t3:r3c1=O-----O--O--- \
      --cell t3:r4c1=O----O---O--O---O--O --cell t3:r8c1=O--O---O--O---

  tN = 본문에서 N번째 표(1부터), rXcY = 셀의 rowAddr/colAddr.
  자리표시자는 "T2R18C2-01" 형식으로 들어간다. 채울 때 전부 바꿀 것.

붙임 검토표:
  python3 prepare_review.py --form attachment --in assets/form_review_attachment.hwpx \
      --out work/붙임_작업본.hwpx --body "□○--○----□○T1:18○---□○T2:3○○□○----○---○--○--○---※"

  --body 는 본문 문단을 앞에서부터 한 글자씩 적은 것이다.
  □ ○ - ※ 는 각각 그 표식으로 시작하는 문단, T1:18 은 1번 표를 데이터 18행으로,
  T2:3 은 2번 표를 데이터 3행으로 만든다는 뜻이다. 제목 표(맨 앞)는 건드리지 않는다.
  자리표시자는 본문 "B01" …, 표 셀 "T1R01C1" … 형식이다.
"""
import argparse
import copy
import re
import sys
import zipfile
from pathlib import Path

from lxml import etree

HP = '{http://www.hancom.co.kr/hwpml/2011/paragraph}'
SECTION = 'Contents/section0.xml'


def para_text(p):
    return ''.join(t.text or '' for t in p.iter(f'{HP}t')).strip()


def strip_layout_cache(p):
    for lsa in p.findall(f'{HP}linesegarray'):
        p.remove(lsa)


def set_para_text(p, text):
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


def make_table_splittable(tbl, mode='TABLE'):
    """표가 쪽 경계에서 나뉘게 한다. TABLE = 셀 안에서도 나눔(긴 서술 셀),
    CELL = 행 경계에서만 나눔(짧은 행이 많은 데이터 표)."""
    pos = tbl.find(f'{HP}pos')
    if pos is not None:
        pos.set('treatAsChar', '0')
    tbl.set('pageBreak', mode)
    for p in tbl.iter(f'{HP}p'):
        strip_layout_cache(p)


def body_tables(root):
    out = []
    for p in root:
        if p.tag != f'{HP}p':
            continue
        for tbl in p.findall(f'.//{HP}tbl'):
            out.append(tbl)
    return out


def find_cell(tbl, row, col):
    for tc in tbl.iter(f'{HP}tc'):
        addr = tc.find(f'{HP}cellAddr')
        if addr is not None and int(addr.get('rowAddr')) == row and int(addr.get('colAddr')) == col:
            return tc
    raise ValueError(f'셀 r{row}c{col} 을 찾지 못했습니다')


# --------------------------------------------------------------------------
# 심의요청서: 셀 안 문단을 O/- 패턴에 맞춰 재구성
# --------------------------------------------------------------------------
def rebuild_cell(tc, pattern, tag):
    sublist = tc.find(f'{HP}subList')
    paras = sublist.findall(f'{HP}p')
    tmpl = {}
    for p in paras:
        txt = para_text(p)
        if txt.startswith('○') and 'O' not in tmpl:
            tmpl['O'] = p
        elif txt.startswith('-') and '-' not in tmpl:
            tmpl['-'] = p
    if 'O' not in tmpl:
        tmpl['O'] = paras[0]
    if '-' not in tmpl:
        tmpl['-'] = paras[-1]
    for p in paras:
        sublist.remove(p)
    for i, ch in enumerate(pattern, 1):
        if ch not in tmpl:
            raise ValueError(f'패턴 문자 {ch!r} 는 O 또는 - 여야 합니다')
        clone = copy.deepcopy(tmpl[ch])
        set_para_text(clone, f'{tag}-{i:02d}')
        sublist.append(clone)
    return len(pattern)


def prepare_request(root, cell_specs):
    tables = body_tables(root)
    summary = {}
    for spec in cell_specs:
        m = re.fullmatch(r't(\d+):r(\d+)c(\d+)=([O\-]+)', spec)
        if not m:
            sys.exit(f'--cell 형식 오류: {spec!r} (예: t3:r2c1=O--O-)')
        ti, row, col, pattern = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
        tbl = tables[ti - 1]
        tc = find_cell(tbl, row, col)
        n = rebuild_cell(tc, pattern, f'T{ti}R{row}C{col}')
        summary[f't{ti}:r{row}c{col}'] = n
    # 개요·목적 표는 셀 하나가 한 쪽을 넘길 수 있으므로 쪽 경계에서 나뉘게 한다.
    for tbl in tables[1:]:
        make_table_splittable(tbl)
    return summary


# --------------------------------------------------------------------------
# 붙임 검토표: 본문 문단 시퀀스와 표 행 수 재구성
# --------------------------------------------------------------------------
def _set_cell_single_text(tc, text):
    sublist = tc.find(f'{HP}subList')
    ps = sublist.findall(f'{HP}p')
    for extra in ps[1:]:
        sublist.remove(extra)
    set_para_text(ps[0], text)


def set_table_rows(tbl, n_data, tag, data=None):
    """데이터 행 수를 n_data로 맞춘다. data가 있으면 {'header': [...], 'rows': [[...], ...]}의
    텍스트를 바로 써 넣고, 없으면 자리표시자(T1R01C1 …)를 넣는다.

    붙임 양식은 맨 앞에 제목 표가 하나 더 있어서 kordoc patch_document가 표 개수를
    맞추지 못하고(표 개수 불일치) 표 편집을 건너뛴다. 그래서 표 내용은 여기서 채운다.
    """
    trs = tbl.findall(f'{HP}tr')
    header, rows = trs[0], trs[1:]
    template = rows[0]
    for tr in rows:
        tbl.remove(tr)
    if data and data.get('header'):
        for tc, text in zip(header.findall(f'{HP}tc'), data['header']):
            _set_cell_single_text(tc, text)
    for r in range(1, n_data + 1):
        tr = copy.deepcopy(template)
        for c, tc in enumerate(tr.findall(f'{HP}tc'), 1):
            tc.find(f'{HP}cellAddr').set('rowAddr', str(r))
            text = data['rows'][r - 1][c - 1] if data else f'{tag}R{r:02d}C{c}'
            _set_cell_single_text(tc, text)
        tbl.append(tr)
    tbl.set('rowCnt', str(n_data + 1))
    make_table_splittable(tbl, 'CELL')   # 데이터 표는 행 경계에서만 나눈다


def set_column_widths(tbl, weights):
    """열 너비를 weights 비율로 다시 나눈다(표 전체 너비는 유지).

    예시 양식의 2열('설치장소')은 '105동' 정도만 들어가게 좁아서, 모델명을 넣으면
    여러 줄로 꺾인다. JSON의 "widths": [10, 15, 7, 6, 8] 처럼 비율만 주면 된다.
    """
    rows = tbl.findall(f'{HP}tr')
    total = sum(int(tc.find(f'{HP}cellSz').get('width')) for tc in rows[0].findall(f'{HP}tc'))
    wsum = float(sum(weights))
    widths = [int(round(total * w / wsum)) for w in weights]
    widths[-1] += total - sum(widths)          # 반올림 오차는 마지막 열에
    for tr in rows:
        for tc, w in zip(tr.findall(f'{HP}tc'), widths):
            tc.find(f'{HP}cellSz').set('width', str(w))


def prepare_attachment(root, body_pattern, tables=None):
    paras = [ch for ch in root if ch.tag == f'{HP}p']
    # 템플릿: 표식별 첫 문단, 표 문단, 제목 표 문단
    tmpl = {}
    table_paras = []
    for p in paras:
        txt = para_text(p)
        has_tbl = p.find(f'.//{HP}tbl') is not None
        if has_tbl:
            table_paras.append(p)
            continue
        for mark in ('□', '○', '-', '※'):
            if txt.startswith(mark) and mark not in tmpl:
                tmpl[mark] = p
    title_para, data_tables = table_paras[0], table_paras[1:]
    missing = [m for m in ('□', '○', '-', '※') if m not in tmpl]
    if missing:
        sys.exit(f'양식에서 템플릿 문단을 찾지 못했습니다: {missing}')

    tokens = re.findall(r'T(\d+):(\d+)|([□○\-※])', body_pattern)
    for p in paras:
        if p is not title_para:
            root.remove(p)

    insert_at = list(root).index(title_para) + 1
    n_body = 0
    used_tables = set()
    for tnum, nrows, mark in tokens:
        if tnum:
            ti = int(tnum)
            tbl_para = data_tables[ti - 1]
            data = (tables or {}).get(str(ti))
            n = len(data['rows']) if data else int(nrows)
            tbl = tbl_para.find(f'.//{HP}tbl')
            set_table_rows(tbl, n, f'T{ti}', data)
            if data and data.get('widths'):
                set_column_widths(tbl, data['widths'])
            strip_layout_cache(tbl_para)
            root.insert(insert_at, tbl_para)
            used_tables.add(ti)
        else:
            n_body += 1
            clone = copy.deepcopy(tmpl[mark])
            set_para_text(clone, f'B{n_body:02d}')
            root.insert(insert_at, clone)
        insert_at += 1
    return {'본문 문단': n_body, '표': sorted(used_tables)}


# --------------------------------------------------------------------------
def rewrite_hwpx(src, dst, transform):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as zin:
        items = zin.infolist()
        root = etree.fromstring(zin.read(SECTION))
        summary = transform(root)
        new_section = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in items:
                data = new_section if item.filename == SECTION else zin.read(item.filename)
                zout.writestr(item, data)
    return summary


def main():
    ap = argparse.ArgumentParser(description='심의요청서/붙임 검토표 양식 문단·행 수 맞추기')
    ap.add_argument('--form', choices=['request', 'attachment'], required=True)
    ap.add_argument('--in', dest='src', required=True)
    ap.add_argument('--out', dest='dst', required=True)
    ap.add_argument('--cell', action='append', default=[], help='[request] tN:rXcY=패턴 (여러 번)')
    ap.add_argument('--body', help='[attachment] 본문 패턴 문자열')
    ap.add_argument('--tables', help='[attachment] 표 내용 JSON 파일: {"1": {"header": [...], "rows": [[...], ...]}, "2": {...}}')
    args = ap.parse_args()

    src, dst = Path(args.src), Path(args.dst)
    if not src.exists():
        sys.exit(f'원본 양식이 없습니다: {src}')
    if args.form == 'request':
        if not args.cell:
            sys.exit('--cell 을 하나 이상 주세요')
        fn = lambda root: prepare_request(root, args.cell)
    else:
        if not args.body:
            sys.exit('--body 패턴을 주세요')
        tables = None
        if args.tables:
            import json
            tables = json.loads(Path(args.tables).read_text(encoding='utf-8'))
        fn = lambda root: prepare_attachment(root, args.body, tables)
    summary = rewrite_hwpx(src, dst, fn)
    print(f'✓ 작업본 생성 — {summary}\n  → {dst}')


if __name__ == '__main__':
    main()
