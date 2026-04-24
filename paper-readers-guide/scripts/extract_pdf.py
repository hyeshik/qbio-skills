#!/usr/bin/env python3
"""Extract text from a PDF so the skill can read the paper's content.

Usage:
    python extract_pdf.py <paper.pdf> [--pages N]

Writes Markdown-formatted text to stdout.  Uses Microsoft's ``markitdown``
library, which preserves headings, lists, and table structure better than a
plain text dump — auto-installs the package on first use if needed.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def ensure_markitdown():
    try:
        from markitdown import MarkItDown  # type: ignore
    except ImportError:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "markitdown[pdf]",
                "--break-system-packages",
            ],
            check=True,
            capture_output=True,
        )
        from markitdown import MarkItDown  # type: ignore
    return MarkItDown


def extract_with_markitdown(path: Path) -> str:
    MarkItDown = ensure_markitdown()
    md = MarkItDown()
    result = md.convert(str(path))
    # markitdown returns an object whose ``.text_content`` is the extracted text.
    text = getattr(result, "text_content", None)
    if text is None:
        # Older versions expose ``.markdown`` instead.
        text = getattr(result, "markdown", "")
    return text or ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument(
        "--pages",
        type=int,
        default=None,
        help="Only return the first N pages of extracted text "
        "(heuristic, based on form-feed characters if present).",
    )
    args = ap.parse_args()

    text = extract_with_markitdown(args.pdf)

    if args.pages is not None:
        # Best-effort page split: markitdown typically does not insert form
        # feeds, so this is only useful for sources that do.
        pages = text.split("\x0c")
        text = "\x0c".join(pages[: args.pages])

    sys.stdout.write(text)


if __name__ == "__main__":
    main()
