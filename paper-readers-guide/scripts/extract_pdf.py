#!/usr/bin/env python3
"""Extract plain text from a PDF so the skill can read the paper's content.

Usage:
    python extract_pdf.py <paper.pdf> [--pages N]

Writes plain text to stdout.  Tries pdftotext first (fast, layout-preserving),
falls back to pypdf if pdftotext is not on the PATH.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def extract_with_pdftotext(path: Path) -> str:
    # -layout preserves column structure reasonably well for most papers.
    out = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return out.stdout


def extract_with_pypdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pypdf", "--break-system-packages"],
            check=True,
            capture_output=True,
        )
        from pypdf import PdfReader  # type: ignore
    reader = PdfReader(str(path))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--pages", type=int, default=None,
                    help="Only return the first N pages of extracted text.")
    args = ap.parse_args()

    if shutil.which("pdftotext"):
        text = extract_with_pdftotext(args.pdf)
    else:
        text = extract_with_pypdf(args.pdf)

    if args.pages is not None:
        # crude page split — pdftotext uses form-feed between pages.
        pages = text.split("\x0c")
        text = "\x0c".join(pages[: args.pages])

    sys.stdout.write(text)


if __name__ == "__main__":
    main()
