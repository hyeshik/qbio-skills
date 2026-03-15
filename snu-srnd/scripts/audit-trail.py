#!/usr/bin/env python3
"""
SRnD Audit Trail — HTML 기록 생성기

사용법:
  python3 audit-trail.py init    --output <path.html>
  python3 audit-trail.py log     --file <path.html> --action <action> --category <cat> --page <page> --detail <detail> [--result <result>]
  python3 audit-trail.py finalize --file <path.html>
"""
import argparse, html, sys
from datetime import datetime

INIT_HTML = """\
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>SRnD Audit Trail — {timestamp}</title>
<style>
  :root {{ --bg: #f8f9fa; --card: #fff; --border: #dee2e6; --accent: #0d6efd;
           --danger: #dc3545; --success: #198754; --muted: #6c757d; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
          sans-serif; background: var(--bg); color: #212529; padding: 2rem; }}
  h1 {{ font-size: 1.4rem; margin-bottom: .3rem; }}
  .meta {{ color: var(--muted); font-size: .85rem; margin-bottom: 1.5rem; }}
  .status {{ display: inline-block; padding: .15rem .5rem; border-radius: .25rem;
             font-size: .8rem; font-weight: 600; }}
  .status-active {{ background: #fff3cd; color: #664d03; }}
  .status-done   {{ background: #d1e7dd; color: #0f5132; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  th {{ background: #e9ecef; text-align: left; padding: .5rem .75rem;
       font-size: .8rem; text-transform: uppercase; letter-spacing: .03em;
       border-bottom: 2px solid var(--border); }}
  td {{ padding: .5rem .75rem; border-bottom: 1px solid var(--border);
       font-size: .88rem; vertical-align: top; }}
  tr:hover td {{ background: #f1f3f5; }}
  .cat {{ display: inline-block; padding: .1rem .4rem; border-radius: .2rem;
          font-size: .75rem; font-weight: 600; }}
  .cat-조회     {{ background: #cfe2ff; color: #084298; }}
  .cat-저장     {{ background: #f8d7da; color: #842029; }}
  .cat-데이터변경 {{ background: #fff3cd; color: #664d03; }}
  .cat-네비게이션 {{ background: #e2e3e5; color: #41464b; }}
  .cat-내보내기  {{ background: #d1e7dd; color: #0f5132; }}
  .cat-팝업     {{ background: #e0cffc; color: #3d0a91; }}
  .cat-자가학습  {{ background: #fce4ec; color: #880e4f; }}
  .cat-기타     {{ background: #e9ecef; color: #495057; }}
  .detail {{ color: #495057; font-size: .82rem; }}
  .result {{ color: var(--muted); font-size: .8rem; font-style: italic; }}
  .action-code {{ font-family: 'SF Mono', 'Cascadia Code', Consolas, monospace;
                  font-size: .82rem; background: #f1f3f5; padding: .1rem .3rem;
                  border-radius: .15rem; }}
  .summary {{ margin-top: 1.5rem; padding: 1rem; background: var(--card);
              border: 1px solid var(--border); border-radius: .5rem; }}
  .summary h2 {{ font-size: 1rem; margin-bottom: .5rem; }}
  #entries-body {{ }}
</style>
</head>
<body>
<h1>SRnD Audit Trail</h1>
<p class="meta">
  시작: {timestamp} &nbsp;|&nbsp;
  <span id="status" class="status status-active">진행 중</span>
</p>
<table>
  <thead>
    <tr>
      <th style="width:7rem">시각</th>
      <th style="width:5rem">분류</th>
      <th style="width:8rem">페이지</th>
      <th style="width:9rem">작업</th>
      <th>상세</th>
      <th style="width:10rem">결과</th>
    </tr>
  </thead>
  <tbody id="entries-body">
<!-- ENTRIES -->
  </tbody>
</table>
<div id="summary" class="summary" style="display:none">
  <h2>요약</h2>
  <p id="summary-text"></p>
</div>
</body>
</html>
"""

ROW_TEMPLATE = (
    '    <tr>'
    '<td>{time}</td>'
    '<td><span class="cat cat-{cat_class}">{category}</span></td>'
    '<td>{page}</td>'
    '<td><span class="action-code">{action}</span></td>'
    '<td class="detail">{detail}</td>'
    '<td class="result">{result}</td>'
    '</tr>\n'
)

FINALIZE_SUMMARY = (
    '\n<script>'
    'document.getElementById("status").className="status status-done";'
    'document.getElementById("status").textContent="완료";'
    'var s=document.getElementById("summary");s.style.display="block";'
    'document.getElementById("summary-text").textContent='
    '"총 {count}건 기록 | 종료: {timestamp}";'
    '</script>\n'
)

MARKER = "<!-- ENTRIES -->"


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_time():
    return datetime.now().strftime("%H:%M:%S")


def cat_class(category):
    known = {"조회", "저장", "데이터변경", "네비게이션", "내보내기", "팝업", "자가학습"}
    return category if category in known else "기타"


def cmd_init(args):
    content = INIT_HTML.format(timestamp=now_str())
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    print(args.output)


def cmd_log(args):
    with open(args.file, "r", encoding="utf-8") as f:
        content = f.read()
    row = ROW_TEMPLATE.format(
        time=now_time(),
        category=html.escape(args.category),
        cat_class=cat_class(args.category),
        page=html.escape(args.page or ""),
        action=html.escape(args.action),
        detail=html.escape(args.detail or ""),
        result=html.escape(args.result or ""),
    )
    content = content.replace(MARKER, row + MARKER)
    with open(args.file, "w", encoding="utf-8") as f:
        f.write(content)
    print("logged:", args.action)


def cmd_finalize(args):
    with open(args.file, "r", encoding="utf-8") as f:
        content = f.read()
    count = content.count("<tr><td>")
    snippet = FINALIZE_SUMMARY.format(count=count, timestamp=now_str())
    content = content.replace("</body>", snippet + "</body>")
    with open(args.file, "w", encoding="utf-8") as f:
        f.write(content)
    print(args.file)


def main():
    parser = argparse.ArgumentParser(description="SRnD Audit Trail")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init")
    p_init.add_argument("--output", required=True)

    p_log = sub.add_parser("log")
    p_log.add_argument("--file", required=True)
    p_log.add_argument("--action", required=True)
    p_log.add_argument("--category", required=True)
    p_log.add_argument("--page", default="")
    p_log.add_argument("--detail", default="")
    p_log.add_argument("--result", default="")

    p_fin = sub.add_parser("finalize")
    p_fin.add_argument("--file", required=True)

    args = parser.parse_args()
    if args.command == "init":
        cmd_init(args)
    elif args.command == "log":
        cmd_log(args)
    elif args.command == "finalize":
        cmd_finalize(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
