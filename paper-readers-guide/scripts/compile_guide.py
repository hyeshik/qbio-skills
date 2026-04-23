#!/usr/bin/env python3
"""Compile a filled reader's-guide Typst file to PDF.

Usage:
    python compile_guide.py <input.typ> <output.pdf>

Uses the ``typst`` Python package and points its font loader at ``assets/`` so
the bundled ``NotoSansKR-Regular.otf`` is available for Korean guides even in
sandboxes without system CJK fonts.  Installs the ``typst`` package on first
use if it isn't already available.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_ROOT / "assets"


def ensure_typst() -> None:
    try:
        import typst  # noqa: F401
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "typst", "--break-system-packages"],
            check=True,
        )


def compile_typst(input_path: Path, output_path: Path) -> None:
    ensure_typst()
    import typst  # type: ignore

    font_paths = [str(ASSETS_DIR)]
    compiler = typst.Compiler(str(input_path), font_paths=font_paths)
    pdf_bytes = compiler.compile()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(pdf_bytes)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="Path to filled template.typ")
    ap.add_argument("output", type=Path, help="Path to write the PDF")
    args = ap.parse_args()

    compile_typst(args.input, args.output)
    print(f"Wrote {args.output}  ({args.output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
