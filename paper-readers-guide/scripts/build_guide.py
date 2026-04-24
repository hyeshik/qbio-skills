#!/usr/bin/env python3
"""One-shot build: content.json -> paper_content.typ -> PDF.

Usage:
    python build_guide.py <content.json> <output.pdf>

This script wraps the full pipeline so the agent only needs to invoke
a single command after writing content.json:

  1. Render the JSON into a filled ``paper_content.typ`` in a sibling
     working directory (alongside the output PDF).
  2. Make sure ``template.typ`` and the Korean fonts are reachable to
     the Typst compiler.  The script does not copy asset files around
     on disk — it invokes ``compile_guide.py`` with ``--asset-dir`` so
     imports and font lookups resolve to the skill's ``assets/`` folder
     directly.
  3. Compile to PDF.

The skill's ``assets/`` folder is auto-detected relative to this script.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPTS_DIR.parent
ASSETS_DIR = SKILL_ROOT / "assets"

RENDER_CONTENT = SCRIPTS_DIR / "render_content.py"
COMPILE_GUIDE = SCRIPTS_DIR / "compile_guide.py"


def build(content_json: Path, output_pdf: Path) -> None:
    if not content_json.exists():
        raise FileNotFoundError(f"content JSON not found: {content_json}")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    # Build in a temporary directory next to the output so ``./template.typ``
    # (the relative import written by render_content.py) resolves.  We
    # symlink (or copy, as a fallback on Windows/readonly mounts) the
    # template and fonts from the skill's assets/ folder.
    with tempfile.TemporaryDirectory(prefix="reader_guide_build_") as tmp:
        work = Path(tmp)
        typ_path = work / "paper_content.typ"

        # Force asset_dir="." in the generated typ — Typst treats absolute
        # path strings as project-root-relative, so we symlink assets into
        # the working directory instead.
        subprocess.run(
            [
                sys.executable,
                str(RENDER_CONTENT),
                str(content_json),
                str(typ_path),
                "--asset-dir",
                ".",
            ],
            check=True,
        )

        # Make template.typ and the image/font assets reachable from the
        # working directory so ``#import "./template.typ"`` and
        # ``image("./img-*.jpeg")`` both resolve.  Symlink where possible,
        # fall back to copy on filesystems that forbid symlinks.
        def _link_or_copy(src: Path, dst: Path) -> None:
            try:
                dst.symlink_to(src)
            except OSError:
                shutil.copy2(src, dst)

        _link_or_copy(ASSETS_DIR / "template.typ", work / "template.typ")
        for asset in ASSETS_DIR.iterdir():
            if asset.suffix.lower() in (".jpeg", ".jpg", ".png", ".otf", ".ttf"):
                _link_or_copy(asset, work / asset.name)

        subprocess.run(
            [
                sys.executable,
                str(COMPILE_GUIDE),
                str(typ_path),
                str(output_pdf),
            ],
            check=True,
        )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("content", type=Path, help="Input content.json")
    ap.add_argument("output", type=Path, help="Path to write the PDF")
    args = ap.parse_args()

    build(args.content, args.output)
    print(f"Built {args.output}  ({args.output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
