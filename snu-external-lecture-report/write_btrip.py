#!/usr/bin/env python3
"""
출장신청서 HWPX 템플릿에 데이터를 채워 새 파일을 생성하는 스크립트.

Usage:
    python3 write_btrip.py --template btrip-form.hwpx --output output.hwpx --json data.json

JSON 형식:
{
  "department": "OO학부",
  "rank": "교수",
  "name": "홍길동",
  "purpose": "2026년도 제1차 과학기술분야 연구기획과제 선정평가 참석",
  "period": "2026. 3. 23.(일)",
  "destination": "대전광역시 유성구",
  "route": "서울 → 대전 → 서울"
}
"""
import argparse
import json
import os
import shutil
import tempfile
import zipfile
from lxml import etree


NS = {
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
    'hc': 'http://www.hancom.co.kr/hwpml/2011/core',
}


def find_cell(table_el, row, col):
    """Find a <hp:tc> element by its cellAddr rowAddr and colAddr."""
    for tc in table_el.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}tc'):
        addr = tc.find('{http://www.hancom.co.kr/hwpml/2011/paragraph}cellAddr')
        if addr is not None:
            if int(addr.get('rowAddr', -1)) == row and int(addr.get('colAddr', -1)) == col:
                return tc
    return None


def set_cell_text(tc, text):
    """Set the text of a table cell's first <hp:t> element, creating one if needed."""
    # Find the first <hp:run> inside the cell's <hp:p>
    for p in tc.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}p'):
        for run in p.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}run'):
            # Look for existing <hp:t>
            t_el = run.find('{http://www.hancom.co.kr/hwpml/2011/paragraph}t')
            if t_el is not None:
                t_el.text = text
                return True
            else:
                # Create <hp:t> element
                t_el = etree.SubElement(run, '{http://www.hancom.co.kr/hwpml/2011/paragraph}t')
                t_el.text = text
                return True
    return False


def find_text_cell(root, search_text):
    """Find a <hp:tc> that contains the given text in its <hp:t> elements."""
    for tc in root.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}tc'):
        for t in tc.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}t'):
            if t.text and search_text in t.text:
                return tc
    return None


def find_next_cell_in_row(table_el, row, after_col):
    """Find the next cell in the same row after the given column."""
    best = None
    best_col = 999
    for tc in table_el.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}tc'):
        addr = tc.find('{http://www.hancom.co.kr/hwpml/2011/paragraph}cellAddr')
        if addr is not None:
            r = int(addr.get('rowAddr', -1))
            c = int(addr.get('colAddr', -1))
            if r == row and c > after_col and c < best_col:
                best = tc
                best_col = c
    return best


def main():
    parser = argparse.ArgumentParser(description='Fill business trip form HWPX')
    parser.add_argument('--template', required=True, help='Template HWPX file')
    parser.add_argument('--output', required=True, help='Output HWPX file')
    parser.add_argument('--json', required=True, help='JSON data file')
    args = parser.parse_args()

    with open(args.json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create temp directory and extract HWPX
    tmpdir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(args.template, 'r') as zin:
            zin.extractall(tmpdir)

        # Parse section0.xml
        section_path = os.path.join(tmpdir, 'Contents', 'section0.xml')
        tree = etree.parse(section_path)
        root = tree.getroot()

        # Find the main table (the one containing "다음과 같이 출장을 명함")
        table = None
        for tbl in root.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}tbl'):
            for t in tbl.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}t'):
                if t.text and '출장을 명함' in t.text:
                    table = tbl
                    break
            if table is not None:
                break

        if table is None:
            print("ERROR: Could not find the main table")
            return

        # Data row 5 is the first data row after headers
        # Column mapping (from template analysis):
        # col 0: 순번 (leave empty)
        # col 1: 학부(과)
        # col 2 (span 2): 직급
        # col 4 (span 3): 출장목적
        # col 7 (span 2): 기간
        # col 9 (span 2): 출장지
        # col 11: 서명/날인 (leave empty)

        DATA_ROW = 5

        # Fill department (학부과)
        cell = find_cell(table, DATA_ROW, 1)
        if cell is not None:
            set_cell_text(cell, data.get('department', ''))

        # Fill rank (직급)
        cell = find_cell(table, DATA_ROW, 2)
        if cell is not None:
            set_cell_text(cell, data.get('rank', ''))

        # Fill name (성명) - based on structure, name might be in col 2 with rank
        # Actually looking at the header: 학부(과), 직급, 성명 are separate columns
        # But data row has: col0, col1, col2(span2), col4(span3)...
        # So col2(span2) covers 직급+성명? No.
        # Let me check: the header row has separate cells for 직급 and 성명
        # but the data cells might combine differently.
        # From the XML: data row 5 has col2 with colSpan=2 (covering cols 2-3)
        # So this is ONE cell for... let's say 직급.
        # And col4(span3) might be 성명? Let's check by looking at widths.
        # Header: 학부(과)=col1, 직급=col2-3, 성명=col4-6? 출장목적=col7-8?
        # That doesn't match either. Let me use the simpler approach:
        # Just write 성명 into the cell that has the right position.

        # Actually from the header text order and column widths:
        # col1: 학부(과) - width 3728
        # col2(span2): 직급 - width 4824
        # col4(span3): 성명+출장목적 combined? No...
        #
        # Looking at it differently - the header has these cells:
        # "학 부 (과)" "직급" "성 명" "출장목적" "기간" "출장지" "서명날인"
        # These map to 7 data columns. But data row has cells at:
        # col0(1), col1(1), col2(2), col4(3), col7(2), col9(2), col11(1) = 7 cells
        #
        # The most logical mapping:
        # col0 = 번호 (순번)
        # col1 = 학부(과)
        # col2 = 직급
        # col4 = 출장목적    (Note: 성명 is skipped because it's the same person info)
        # col7 = 기간
        # col9 = 출장지
        # col11 = 서명날인
        # But this skips 성명!
        #
        # OR maybe the header has:
        # 순번 | 학부과 | 직급 | 성명 | 출장목적 | 기간 | 출장지 | 서명
        # And data cells: col0 | col1 | col2(span2 covers 직급+성명?) | col4 | col7 | col9 | col11
        # No, span2 means it takes 2 grid columns but is ONE cell.
        #
        # Let me just use the actual column positions and fill based on what the user specified:
        # The user said only 1 person, and gave: 학부과, 직급, 성명, 출장목적, 기간, 출장지

        # Fill 성명 - likely col 2 is combined 직급+성명? Or maybe:
        # I'll put 성명 as part of the data. Let me just fill what we know:

        # For safety, let me fill all cells we care about:
        fill_map = {
            1: data.get('department', ''),    # 학부(과)
            2: data.get('rank', ''),          # 직급
            4: data.get('purpose', ''),       # 출장목적 (or 성명, see below)
            7: data.get('period', ''),        # 기간
            9: data.get('destination', ''),   # 출장지
        }

        # Check if there's a separate 성명 cell - look at the header to decide
        # If the header has 성명 as a separate column, there should be more cells
        # For the template given, based on the analysis the first data row has
        # exactly 7 cells (cols 0,1,2,4,7,9,11)
        # So the mapping with 8 header labels and 7 data cells means one header
        # spans two columns. Most likely "서명/날인" is one cell spanning 2 header labels.
        # That gives us:
        # col0=번호, col1=학부과, col2=직급, col4=성명, col7=기간, col9=출장지, col11=서명날인
        # But what about 출장목적??
        # Actually col4 has colSpan=3 (covers 3 grid columns), which is wider.
        # That's more likely to be 출장목적 (the widest field).
        # And col2 has colSpan=2 which could be 직급+성명 combined.

        # OK let me just look at widths:
        # col1: 3728 (narrow) = 학부과
        # col2: 4824 (medium) = 직급? or combined?
        # col4: 14529 (very wide!) = must be 출장목적
        # col7: 8682 (wide) = 기간
        # col9: 8230 (wide) = 출장지
        # col11: 4116 (medium) = 서명날인

        # 14529 is definitely 출장목적. 4824 (col2) is too narrow for both 직급+성명.
        # So maybe col2 is just 성명 (or 직급), and 성명 is somewhere else.

        # Given the user said the fields are: 학부과, 직급, 성명, 출장목적, 기간, 출장지, 서명날인
        # And we have 7 cells... I think the header "번호" row doesn't exist and
        # col0 is actually 학부과, not 번호.

        # Wait, col0 has width 5723 and the "이동사항" row also starts at col0.
        # Let me re-examine. col0 at row 5 has colSpan=1, width=5723.
        # The header text says row 4 has: "학 부 (과)", "직급", "성 명",
        # "출장목적", "기간", "출장지", "서명날인"
        # That's 7 items. If there's no "번호" column, then:
        # col0 = 학부과
        # col1 = 직급
        # col2(span2) = 성명
        # col4(span3) = 출장목적
        # col7(span2) = 기간
        # col9(span2) = 출장지
        # col11(span1) = 서명날인

        # This makes much more sense! Let me use this mapping.
        fill_map = {
            0: data.get('department', ''),    # 학부(과)
            1: data.get('rank', ''),          # 직급
            2: data.get('name', ''),          # 성명
            4: data.get('purpose', ''),       # 출장목적
            7: data.get('period', ''),        # 기간
            9: data.get('destination', ''),   # 출장지
            # 11: 서명날인 - leave empty
        }

        for col, text in fill_map.items():
            cell = find_cell(table, DATA_ROW, col)
            if cell is not None:
                set_cell_text(cell, text)
            else:
                print(f"WARNING: Could not find cell at row={DATA_ROW}, col={col}")

        # Fill 이동사항 row
        # Find the cell containing "이 동 사 항" text, then the next cell in same row
        route_label = find_text_cell(root, '이 동 사 항')
        if route_label is not None:
            addr = route_label.find('{http://www.hancom.co.kr/hwpml/2011/paragraph}cellAddr')
            if addr is not None:
                row = int(addr.get('rowAddr'))
                col = int(addr.get('colAddr'))
                # The route text goes in the same cell after the label,
                # or in the next cell. Let's check the label text.
                # "  이 동 사 항 : " - the colon suggests we append to same cell
                # Actually, looking at the XML, the label cell spans the full row
                # So we need to append the route to the existing text
                for t in route_label.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}t'):
                    if t.text and '이 동 사 항' in t.text:
                        t.text = f"  이 동 사 항 : {data.get('route', '')}"
                        break

        # Fill 여비계산 - find "원" cell and set to "0"
        # The 여비계산 row has "여 비 계 산" label and "             원" value cell
        for tc in table.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}tc'):
            for t in tc.iter('{http://www.hancom.co.kr/hwpml/2011/paragraph}t'):
                if t.text and t.text.strip() == '원':
                    t.text = '           0 원'
                    break

        # Write back section0.xml
        tree.write(section_path, xml_declaration=True, encoding='UTF-8',
                   standalone=True)

        # Repack HWPX
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED) as zout:
            for dirpath, dirnames, filenames in os.walk(tmpdir):
                for fn in filenames:
                    full = os.path.join(dirpath, fn)
                    arcname = os.path.relpath(full, tmpdir)
                    zout.write(full, arcname)

        print(f"Created: {args.output}")

    finally:
        shutil.rmtree(tmpdir)


if __name__ == '__main__':
    main()
