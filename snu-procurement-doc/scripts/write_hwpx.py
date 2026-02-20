#!/usr/bin/env python3
"""
write_hwpx.py - HWPX 양식 기반 구매문서 생성 스크립트

HWPX는 ZIP+XML 형식으로, HWP5 바이너리 OLE보다 훨씬 안정적으로 수정 가능하다.
원본 HWPX 템플릿을 복사한 뒤 Contents/section0.xml의 <hp:t> 텍스트만 교체한다.

지원 기능:
  - 구매규격서(form3): 무제한 스펙/기타조건 항목 (템플릿 슬롯 초과 시 자동 복제)
  - 용도설명서(form2): 멀티 라인 일반사양/성능/용도설명 (단락 자동 복제)

Usage:
    python3 write_hwpx.py --template-dir assets/ --output-dir output/ --data-json data.json

Output:
    구매규격서_{item_name_en}.hwpx
    용도설명서_{item_name_en}.hwpx
"""
import argparse
import copy
import json
import os
import re
import sys
import zipfile

from lxml import etree

# HWPX XML namespaces
HP = '{http://www.hancom.co.kr/hwpml/2011/paragraph}'
HS = '{http://www.hancom.co.kr/hwpml/2011/section}'


# =========================================================================
# XML Helper Functions
# =========================================================================

def get_all_text(elem):
    """Get concatenated text from all <hp:t> descendants."""
    texts = []
    for t in elem.iter(f'{HP}t'):
        if t.text:
            texts.append(t.text)
        for child in t:
            if child.tail:
                texts.append(child.tail)
    return ''.join(texts).strip()


def strip_linesegarray(p):
    """Remove <hp:linesegarray> from a paragraph.

    This element is a layout cache that tells Hancom Word how to render text
    without recalculating. If present after text replacement, Hancom Word will
    shrink the font to fit long text into the original one-line layout instead
    of wrapping. Removing it forces Hancom Word to recalculate and wrap properly.
    """
    for lsa in p.findall(f'{HP}linesegarray'):
        p.remove(lsa)


def find_cell(table, col, row):
    """Find <hp:tc> element by cellAddr colAddr/rowAddr."""
    for tc in table.iter(f'{HP}tc'):
        addr = tc.find(f'{HP}cellAddr')
        if addr is not None:
            if int(addr.get('colAddr')) == col and int(addr.get('rowAddr')) == row:
                return tc
    return None


def set_cell_text(tc, text):
    """Set text of a table cell's first run."""
    sublist = tc.find(f'{HP}subList')
    if sublist is None:
        return
    for p in sublist.iter(f'{HP}p'):
        for run in p.iter(f'{HP}run'):
            t_elem = run.find(f'{HP}t')
            if t_elem is not None:
                for child in list(t_elem):
                    t_elem.remove(child)
                t_elem.text = text
            else:
                t_elem = etree.SubElement(run, f'{HP}t')
                t_elem.text = text
            strip_linesegarray(p)
            return


def set_cell_multi_para_text(tc, texts_by_label):
    """Set text for cells with multiple labeled paragraphs."""
    sublist = tc.find(f'{HP}subList')
    if sublist is None:
        return
    for p in sublist.findall(f'{HP}p'):
        para_text = get_all_text(p)
        for label, new_text in texts_by_label.items():
            if label in para_text:
                for run in p.findall(f'{HP}run'):
                    t = run.find(f'{HP}t')
                    if t is not None and t.text and label in t.text:
                        t.text = new_text
                        break
                strip_linesegarray(p)
                break


def find_para_by_text(root, search_text):
    """Find <hp:p> element containing search_text."""
    for p in root.iter(f'{HP}p'):
        if search_text in get_all_text(p):
            return p
    return None


def set_para_text(p, new_text):
    """Set text of a paragraph's first run."""
    for run in p.iter(f'{HP}run'):
        t_elem = run.find(f'{HP}t')
        if t_elem is not None:
            for child in list(t_elem):
                t_elem.remove(child)
            t_elem.text = new_text
            strip_linesegarray(p)
            return True
        else:
            t_elem = etree.SubElement(run, f'{HP}t')
            t_elem.text = new_text
            strip_linesegarray(p)
            return True
    return False


def clone_para_after(parent, template_para, new_text):
    """Deep-copy a paragraph and insert it right after the template.
    Returns the new paragraph element."""
    new_p = copy.deepcopy(template_para)
    set_para_text(new_p, new_text)
    # Find position of template in parent and insert after it
    idx = list(parent).index(template_para)
    parent.insert(idx + 1, new_p)
    return new_p


def clone_para_in_sublist(sublist, template_para, new_text):
    """Deep-copy a paragraph within a subList and insert after template."""
    new_p = copy.deepcopy(template_para)
    set_para_text(new_p, new_text)
    idx = list(sublist).index(template_para)
    sublist.insert(idx + 1, new_p)
    return new_p


# =========================================================================
# Form3: 구매규격서
# =========================================================================

def modify_form3(section_xml, data):
    """Modify form3 (구매규격서) section0.xml.

    Supports:
      - Unlimited spec items (clones paragraphs beyond 8 template slots)
      - Unlimited remark items (clones paragraphs beyond 3 template slots)
      - Multiple config items and sub-items
    """
    root = etree.fromstring(section_xml)
    tbl = root.find(f'.//{HP}tbl')
    if tbl is None:
        raise ValueError("Table not found in form3")

    # === Table data row (row 1) ===
    # Col 0: 품목번호
    tc = find_cell(tbl, 0, 1)
    if tc is not None:
        set_cell_text(tc, data.get('item_no', '1'))

    # Col 1: HSK code
    tc = find_cell(tbl, 1, 1)
    if tc is not None:
        set_cell_text(tc, f"({data['hsk_code']})")

    # Col 2: 정부물품분류번호
    tc = find_cell(tbl, 2, 1)
    if tc is not None:
        set_cell_text(tc, data['gov_code'])

    # Col 3: 품명 (may have multiple runs - consolidate to one)
    tc = find_cell(tbl, 3, 1)
    if tc is not None:
        sublist = tc.find(f'{HP}subList')
        if sublist is not None:
            p = sublist.find(f'{HP}p')
            if p is not None:
                runs = p.findall(f'{HP}run')
                if runs:
                    first_run = runs[0]
                    for run in runs[1:]:
                        p.remove(run)
                    t = first_run.find(f'{HP}t')
                    if t is not None:
                        for child in list(t):
                            t.remove(child)
                        t.text = data['item_name_en']
                    else:
                        t = etree.SubElement(first_run, f'{HP}t')
                        t.text = data['item_name_en']

    # Col 4: 단위
    tc = find_cell(tbl, 4, 1)
    if tc is not None:
        set_cell_text(tc, data['unit'])

    # Col 5: 수량
    tc = find_cell(tbl, 5, 1)
    if tc is not None:
        set_cell_text(tc, data['quantity'])

    # === Body sections ===
    # Find the section parent (<hs:sec>)
    sec = root.find(f'.//{HS}sec')
    if sec is None:
        # Fallback: use root
        sec = root

    # --- Ⅰ. 용도 ---
    usage_p = find_para_by_text(root, '어떤 업무에 사용되는 지 기술')
    if usage_p is not None:
        set_para_text(usage_p, f" - {data['usage']} -")

    # --- Ⅱ. 장비의 구성 ---
    config = data.get('config', [])
    config_sub = data.get('config_sub', [])

    config1_p = find_para_by_text(root, '본체(Main body)')
    if config1_p is not None and len(config) > 0:
        set_para_text(config1_p, f" 1.  {config[0]}")

    config2_p = find_para_by_text(root, 'accessories')
    if config2_p is not None and len(config) > 1:
        set_para_text(config2_p, f" 2.  {config[1]}")

    # Additional config items beyond 2 - clone after config2_p
    if config2_p is not None:
        last_config_p = config2_p
        for i in range(2, len(config)):
            last_config_p = clone_para_after(
                last_config_p.getparent(), last_config_p,
                f" {i + 1}.  {config[i]}"
            )

    # Sub-items ("-" lines)
    sub_count = 0
    for p in root.iter(f'{HP}p'):
        text = get_all_text(p)
        if text.strip() == '-' and sub_count < len(config_sub):
            set_para_text(p, f"   - {config_sub[sub_count]}")
            sub_count += 1

    # --- Ⅲ. 성능 및 규격 ---
    specs = data.get('specs', [])
    spec_section = find_para_by_text(root, '성능 및 규격')
    remark_section = find_para_by_text(root, '기타 조건')

    # Collect existing numbered spec paragraphs
    spec_paras = []
    if spec_section is not None:
        found_spec = False
        for p in sec.iter(f'{HP}p'):
            if p is spec_section:
                found_spec = True
                continue
            if p is remark_section:
                break
            if found_spec:
                text = get_all_text(p)
                if re.match(r'^\s*\d+\.\s*$', text):
                    spec_paras.append(p)

    # Fill existing slots
    for i, sp in enumerate(spec_paras):
        if i < len(specs):
            set_para_text(sp, f" {i + 1}. {specs[i]}")

    # Clone additional spec paragraphs beyond template slots
    if len(specs) > len(spec_paras) and spec_paras:
        last_spec_p = spec_paras[-1]
        parent = last_spec_p.getparent()
        for i in range(len(spec_paras), len(specs)):
            last_spec_p = clone_para_after(
                parent, last_spec_p,
                f" {i + 1}. {specs[i]}"
            )

    # --- Ⅳ. 기타 조건 ---
    remarks = data.get('remarks', [])

    # Collect existing numbered remark paragraphs
    remark_paras = []
    if remark_section is not None:
        found_remark = False
        for p in sec.iter(f'{HP}p'):
            if p is remark_section:
                found_remark = True
                continue
            if found_remark:
                text = get_all_text(p)
                if re.match(r'^\s*\d+\.\s*$', text):
                    remark_paras.append(p)

    # Fill existing slots
    for i, rp in enumerate(remark_paras):
        if i < len(remarks):
            set_para_text(rp, f" {i + 1}. {remarks[i]}")

    # Clone additional remark paragraphs beyond template slots
    if len(remarks) > len(remark_paras) and remark_paras:
        last_remark_p = remark_paras[-1]
        parent = last_remark_p.getparent()
        for i in range(len(remark_paras), len(remarks)):
            last_remark_p = clone_para_after(
                parent, last_remark_p,
                f" {i + 1}. {remarks[i]}"
            )

    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)


# =========================================================================
# Form2: 용도설명서
# =========================================================================

def modify_form2(section_xml, data):
    """Modify form2 (용도설명서) section0.xml.

    Supports:
      - Multi-line general_specs (list of strings)
      - Multi-line performance_specs (list of strings)
      - Multi-paragraph usage_desc (list of strings)
    """
    root = etree.fromstring(section_xml)
    tbl = root.find(f'.//{HP}tbl')
    if tbl is None:
        raise ValueError("Table not found in form2")

    # Row 0, Col 1: 품명 (영문)/(국문)
    tc = find_cell(tbl, 1, 0)
    if tc is not None:
        set_cell_multi_para_text(tc, {
            '(영문)': f"(영문) {data['item_name_en']}",
            '(국문)': f"(국문) {data['item_name_kr']}",
        })

    # Row 1, Col 1: 모델명
    tc = find_cell(tbl, 1, 1)
    if tc is not None:
        set_cell_text(tc, data['model'])

    # Row 2, Col 1: 제조사
    tc = find_cell(tbl, 1, 2)
    if tc is not None:
        set_cell_text(tc, data['manufacturer'])

    # Row 2, Col 3: 제작국가
    tc = find_cell(tbl, 3, 2)
    if tc is not None:
        set_cell_text(tc, data['country'])

    # Row 3: 규격 (colAddr=0, rowAddr=3, colSpan=4)
    tc = find_cell(tbl, 0, 3)
    if tc is not None:
        sublist = tc.find(f'{HP}subList')
        if sublist is not None:
            paras = sublist.findall(f'{HP}p')
            current_section = None
            gen_spec_empty = []
            perf_empty = []

            for p in paras:
                text = get_all_text(p)
                if 'Ⅰ. 일반사양' in text:
                    current_section = 'gen'
                    continue
                if 'Ⅱ. 성능' in text:
                    current_section = 'perf'
                    continue
                if current_section == 'gen' and not text:
                    gen_spec_empty.append(p)
                elif current_section == 'perf' and not text:
                    perf_empty.append(p)

            # --- 일반사양: support list of strings ---
            general_specs = data.get('general_specs', '')
            if isinstance(general_specs, str):
                general_specs = [general_specs] if general_specs else []

            last_gen_p = gen_spec_empty[-1] if gen_spec_empty else None
            for i, spec_line in enumerate(general_specs):
                if i < len(gen_spec_empty):
                    set_para_text(gen_spec_empty[i], spec_line)
                    last_gen_p = gen_spec_empty[i]
                elif last_gen_p is not None:
                    last_gen_p = clone_para_in_sublist(sublist, last_gen_p, spec_line)

            # --- 성능: support list of strings ---
            performance_specs = data.get('performance_specs', '')
            if isinstance(performance_specs, str):
                performance_specs = [performance_specs] if performance_specs else []

            last_perf_p = perf_empty[-1] if perf_empty else None
            for i, perf_line in enumerate(performance_specs):
                if i < len(perf_empty):
                    set_para_text(perf_empty[i], perf_line)
                    last_perf_p = perf_empty[i]
                elif last_perf_p is not None:
                    last_perf_p = clone_para_in_sublist(sublist, last_perf_p, perf_line)

    # Row 4: 용도설명 (colAddr=0, rowAddr=4)
    tc = find_cell(tbl, 0, 4)
    if tc is not None:
        sublist = tc.find(f'{HP}subList')
        if sublist is not None:
            paras = sublist.findall(f'{HP}p')
            empty_paras = [p for p in paras if not get_all_text(p)]

            usage_desc = data.get('usage_desc', '')
            if isinstance(usage_desc, str):
                usage_desc = [usage_desc] if usage_desc else []

            for i, usage_line in enumerate(usage_desc):
                if i < len(empty_paras):
                    set_para_text(empty_paras[i], usage_line)
                elif empty_paras:
                    clone_para_in_sublist(sublist, empty_paras[-1], usage_line)

    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)


# =========================================================================
# HWPX File Writer
# =========================================================================

def write_hwpx(template_path, output_path, modify_fn, data):
    """Copy HWPX template and modify section0.xml."""
    entries = {}
    with zipfile.ZipFile(template_path, 'r') as zin:
        for info in zin.infolist():
            entries[info.filename] = (info, zin.read(info.filename))

    section_xml = entries['Contents/section0.xml'][1]
    new_section = modify_fn(section_xml, data)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for filename, (info, content) in entries.items():
            if filename == 'Contents/section0.xml':
                zout.writestr(info, new_section)
            elif filename == 'mimetype':
                zout.writestr(info, content, compress_type=zipfile.ZIP_STORED)
            else:
                zout.writestr(info, content)

    return output_path


# =========================================================================
# CLI
# =========================================================================

def main():
    parser = argparse.ArgumentParser(description='HWPX 구매문서 생성')
    parser.add_argument('--template-dir', required=True, help='HWPX 템플릿 디렉토리')
    parser.add_argument('--output-dir', required=True, help='출력 디렉토리')
    parser.add_argument('--data-json', required=True, help='데이터 JSON 파일 경로')
    args = parser.parse_args()

    with open(args.data_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    os.makedirs(args.output_dir, exist_ok=True)

    item_name = data.get('item_name_en', 'Equipment').replace(' ', '_')

    # Generate 구매규격서
    form3_tpl = os.path.join(args.template_dir, 'form3.hwpx')
    form3_out = os.path.join(args.output_dir, f'구매규격서_{item_name}.hwpx')
    write_hwpx(form3_tpl, form3_out, modify_form3, data)
    print(f'구매규격서: {form3_out}')

    # Generate 용도설명서
    form2_tpl = os.path.join(args.template_dir, 'form2.hwpx')
    form2_out = os.path.join(args.output_dir, f'용도설명서_{item_name}.hwpx')
    write_hwpx(form2_tpl, form2_out, modify_form2, data)
    print(f'용도설명서: {form2_out}')


if __name__ == '__main__':
    main()
