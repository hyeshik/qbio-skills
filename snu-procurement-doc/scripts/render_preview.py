#!/usr/bin/env python3
"""
render_preview.py — 완성된 HWPX를 rhwp로 렌더해 PNG로 저장한다 (눈으로 검증용).

kordoc의 render_document가 이 양식들(별지 제2·3호)에서는 실패하므로,
rhwp-python으로 직접 렌더한다.

준비:
    pip install --user rhwp-python

rhwp의 확장 모듈은 시스템 freetype 심볼을 늦게 찾는 경우가 있어
(ImportError: undefined symbol: FT_Palette_*) libfreetype을 먼저 올려 줘야 한다.
이 스크립트는 그 처리를 스스로 하므로 그냥 실행하면 된다.

사용법:
    python3 render_preview.py 문서.hwpx                 # 문서_p1.png … 저장
    python3 render_preview.py 문서.hwpx --out preview   # preview_p1.png … 저장
    python3 render_preview.py 문서.hwpx --scale 2.0
"""
import argparse
import contextlib
import ctypes.util
import io
import os
import subprocess
import sys
from pathlib import Path


def ensure_rhwp():
    """rhwp를 import 한다. freetype 심볼 문제면 LD_PRELOAD를 붙여 한 번만 재실행."""
    try:
        import rhwp  # noqa: F401
        return
    except ImportError as exc:
        if 'FT_' not in str(exc) or os.environ.get('_RHWP_PRELOADED'):
            raise
    lib = ctypes.util.find_library('freetype')
    if not lib:
        sys.exit('freetype 라이브러리를 찾지 못했습니다. libfreetype6를 설치하세요.')
    for base in ('/usr/lib/x86_64-linux-gnu', '/usr/lib/aarch64-linux-gnu', '/usr/lib', '/lib'):
        path = Path(base) / lib
        if path.exists():
            env = dict(os.environ, LD_PRELOAD=str(path), _RHWP_PRELOADED='1')
            sys.exit(subprocess.call([sys.executable, *sys.argv], env=env))
    sys.exit(f'{lib} 의 실제 경로를 찾지 못했습니다.')


def main():
    ap = argparse.ArgumentParser(description='HWPX를 PNG로 렌더 (rhwp)')
    ap.add_argument('source', help='렌더할 HWPX 경로')
    ap.add_argument('--out', help='출력 파일 접두사 (기본: 원본 이름)')
    ap.add_argument('--scale', type=float, default=1.5, help='배율 (기본 1.5)')
    ap.add_argument('--pages', type=int, default=0, help='최대 페이지 수 (0=전부)')
    args = ap.parse_args()

    ensure_rhwp()
    import rhwp

    src = Path(args.source)
    if not src.exists():
        sys.exit(f'파일이 없습니다: {src}')
    prefix = Path(args.out) if args.out else src.with_suffix('')

    doc = rhwp.parse(str(src))
    total = getattr(doc, 'page_count', 1) or 1
    limit = min(total, args.pages) if args.pages else total

    written = []
    warnings = []
    for page in range(limit):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            png = doc.render_png(page, scale=args.scale)
        for line in buf.getvalue().splitlines():
            if line.strip():
                warnings.append(line.strip())
        out = Path(f'{prefix}_p{page + 1}.png')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(png)
        written.append(out)

    if warnings:
        print('!! 조판 경고 — 내용이 쪽 밖으로 넘쳤다는 뜻이다. 무시하지 말 것.')
        for w in dict.fromkeys(warnings):
            print(f'   {w}')
        print()
    print(f'✓ {total}쪽 중 {len(written)}쪽 렌더')
    for w in written:
        print(f'  {w}')
    if not warnings:
        print('\n조판 경고 없음. 표가 쪽 경계에서 정상적으로 이어진다.')


if __name__ == '__main__':
    main()
