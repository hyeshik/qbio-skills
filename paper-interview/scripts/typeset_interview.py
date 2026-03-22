#!/usr/bin/env python3
"""
Paper Interview Typesetter — Figure Extraction + Mermaid Rendering + Typst PDF

Takes the markdown interview, the original paper PDF, and produces a
professionally typeset PDF using Typst.

Pipeline:
  1. Parse the interview markdown to identify <diagram> and <figure_ref> blocks
  2. Extract referenced figures from the paper PDF as PNG (Figure Extract Agent)
  3. Render Mermaid diagrams to PNG via mermaid-cli
  4. Convert the markdown interview into Typst markup
  5. Compile with Typst to produce the final PDF

Usage:
    python typeset_interview.py \
        --interview interview_final.md \
        --paper paper.pdf \
        --structure paper_structure.json \
        --template /path/to/skill/templates/interview.typ \
        --output-dir typeset_output/ \
        --output interview.pdf
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Parse interview markdown — identify visual blocks
# ---------------------------------------------------------------------------

def parse_visual_blocks(md_text: str) -> list:
    """Extract all <diagram> and <figure_ref> blocks from the markdown."""
    blocks = []

    # Find <diagram> blocks
    for m in re.finditer(
        r"<diagram>\s*\n(.*?)\n\s*</diagram>",
        md_text, re.DOTALL
    ):
        content = m.group(1).strip()
        # Extract mermaid code
        mermaid_match = re.search(
            r"```mermaid\s*\n(.*?)\n\s*```", content, re.DOTALL
        )
        # Extract caption
        caption_match = re.search(
            r">\s*\*\*Figure:\s*(.*?)\*\*", content
        )
        blocks.append({
            "type": "diagram",
            "full_match": m.group(0),
            "mermaid_code": mermaid_match.group(1).strip() if mermaid_match else "",
            "caption": caption_match.group(1).strip() if caption_match else "",
            "start": m.start(),
            "end": m.end(),
        })

    # Find <figure_ref> blocks
    for m in re.finditer(
        r"<figure_ref>\s*\n(.*?)\n\s*</figure_ref>",
        md_text, re.DOTALL
    ):
        content = m.group(1).strip()
        # Extract figure ID (e.g., "Figure 3B", "Graphical Abstract")
        fig_match = re.search(
            r"\*\*See\s+(.*?)\s+in the original paper\*\*", content
        )
        # Extract caption text after the colon
        caption_match = re.search(
            r"in the original paper\*\*:\s*(.*?)$", content, re.MULTILINE
        )
        # Extract the "why" italic text
        why_match = re.search(r"\*([^*]+)\*\s*$", content)

        blocks.append({
            "type": "figure_ref",
            "full_match": m.group(0),
            "figure_id": fig_match.group(1).strip() if fig_match else "Figure",
            "caption": caption_match.group(1).strip() if caption_match else "",
            "why": why_match.group(1).strip() if why_match else "",
            "start": m.start(),
            "end": m.end(),
        })

    blocks.sort(key=lambda b: b["start"])
    return blocks


# ---------------------------------------------------------------------------
# 2. Extract figures from the paper PDF
# ---------------------------------------------------------------------------

def extract_figure_from_pdf(pdf_path: str, figure_id: str, output_dir: Path,
                            structure: dict) -> str | None:
    """
    Extract a cropped figure region from the paper PDF as a PNG file.

    Strategy:
      1. Locate the page containing the figure caption
      2. Find the caption text block bounding box
      3. Estimate the figure region using layout heuristics
      4. Render only that cropped region at high resolution

    Returns the path to the extracted PNG, or None on failure.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print(f"  ⚠ PyMuPDF not available; skipping extraction of {figure_id}")
        return None

    doc = fitz.open(pdf_path)
    fig_id_lower = figure_id.lower().strip()
    output_path = output_dir / f"fig_{_sanitize_filename(figure_id)}.png"
    zoom = 2.5  # Higher zoom for cropped regions

    result = None
    if "graphical abstract" in fig_id_lower:
        result = _extract_graphical_abstract(doc, output_path, zoom)
    else:
        result = _extract_figure_by_caption(doc, figure_id, output_path, zoom)

    doc.close()
    return result


def _find_caption_block(page, figure_id: str):
    """
    Find the text block(s) containing a figure caption on the given page.

    Returns (fitz.Rect, str) of the caption bounding box and matched text,
    or (None, None) if not found.
    """
    import fitz
    fig_id_lower = figure_id.lower().strip()
    blocks = page.get_text("blocks")

    # Build search pattern
    if "graphical abstract" in fig_id_lower:
        pattern = re.compile(r"graphical\s+abstract", re.IGNORECASE)
    else:
        # Extract figure number and optional panel letters
        num_match = re.search(r"figure\s*(\d+)", fig_id_lower)
        if num_match:
            fig_num = num_match.group(1)
            pattern = re.compile(
                rf"Figure\s+{re.escape(fig_num)}\b", re.IGNORECASE
            )
        else:
            pattern = re.compile(re.escape(figure_id), re.IGNORECASE)

    # Find caption blocks — figure captions are typically descriptive text
    # starting with "Figure N." and are longer than passing references
    best_block = None
    best_rect = None
    for block in blocks:
        if len(block) < 5 or not isinstance(block[4], str):
            continue
        text = block[4].strip()
        if not pattern.search(text):
            continue
        rect = fitz.Rect(block[:4])
        # Prefer blocks where the figure ID appears at the start (= actual caption)
        # over blocks that merely reference the figure in running text
        starts_with = bool(re.match(
            rf"^\s*Figure\s+\d+", text, re.IGNORECASE
        ))
        if starts_with:
            return rect, text
        if best_block is None:
            best_block = text
            best_rect = rect

    return best_rect, best_block


def _extract_graphical_abstract(doc, output_path: Path, zoom: float) -> str | None:
    """
    Extract the Graphical Abstract region from page 1.

    Cell/Elsevier layout: GA is in the LEFT column, between the
    "Graphical abstract" header and "Highlights" section.  The right
    column contains Authors / Correspondence / In-brief — exclude it.
    """
    import fitz
    page = doc[0]
    page_rect = page.rect
    blocks = page.get_text("blocks")

    # Find "Graphical abstract" label — marks the top of the GA
    ga_label_y1 = None
    ga_label_x1 = None
    for block in blocks:
        if len(block) >= 5 and isinstance(block[4], str):
            if "graphical abstract" in block[4].lower():
                ga_label_y1 = block[3]   # bottom of the label text
                ga_label_x1 = block[2]   # right edge of "Graphical abstract"
                break

    if ga_label_y1 is None:
        ga_label_y1 = 170
        ga_label_x1 = 160

    # Find "Highlights" or similar section that marks the END of the GA area
    ga_end_y = page_rect.height * 0.60
    for block in blocks:
        if len(block) >= 5 and isinstance(block[4], str):
            text_lower = block[4].lower().strip()
            if text_lower.startswith("highlights") or \
               (text_lower.startswith("in brief") and block[0] < page_rect.width / 2):
                ga_end_y = block[1]
                break

    # Find the column boundary: "Authors" / "Correspondence" blocks on the
    # right typically start at x ≈ 340-360 in Cell papers.
    right_col_x = page_rect.width * 0.55  # default
    for block in blocks:
        if len(block) >= 5 and isinstance(block[4], str):
            text = block[4].strip().lower()
            if text.startswith("authors") or text.startswith("correspondence"):
                right_col_x = min(right_col_x, block[0] - 8)
                break

    # Crop: LEFT column only, from below GA label to above Highlights
    margin_x = 40
    clip = fitz.Rect(
        margin_x,
        ga_label_y1 + 3,
        right_col_x,
        ga_end_y - 5,
    )

    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(clip=clip, matrix=mat)
    pix.save(str(output_path))

    print(f"  ✓ Extracted Graphical Abstract → {output_path.name} "
          f"({pix.width}×{pix.height}px, cropped region from page 1)")
    return str(output_path)


# Header height constant — Cell papers have citation line + journal logo
# + "Article" label all within the first ~85pt.
_HEADER_Y = 88


def _extract_figure_by_caption(doc, figure_id: str, output_path: Path,
                                zoom: float) -> str | None:
    """
    Extract a numbered figure by finding its caption and computing the
    panel-only region (no caption text, no page header, no other column).

    Supports two common journal layouts:
      A) Side-caption: caption in right column, figure panels in left column
      B) Bottom-caption: caption below panels, spanning full page width
    """
    import fitz

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        caption_rect, caption_text = _find_caption_block(page, figure_id)
        if caption_rect is None or caption_text is None:
            continue

        # Skip passing references (too short to be a real caption)
        if len(caption_text) < 40:
            continue

        page_rect = page.rect
        page_center_x = page_rect.width / 2

        # ── Layout A: Side-caption (caption in right column) ──
        if caption_rect.x0 > page_center_x * 0.60:
            # Figure panels live in the LEFT column only.
            # Find the bottom of the figure panels: look for body text
            # (two-column paragraphs) below the figure area.
            panel_bottom = _find_body_text_top(page, below_y=_HEADER_Y)
            clip = fitz.Rect(
                40,                          # left margin (skip gutter)
                _HEADER_Y,                   # below page header
                caption_rect.x0 - 6,         # left of caption column
                panel_bottom,                 # above body text
            )

        # ── Layout B: Bottom-caption (caption spans full width) ──
        elif caption_rect.y0 > page_rect.height * 0.55:
            clip = fitz.Rect(
                40,
                _HEADER_Y,
                page_rect.width - 40,
                caption_rect.y0 - 5,         # just above caption text
            )

        # ── Layout C: Caption at top or unknown ──
        else:
            fig_bottom = _find_body_text_top(page, below_y=caption_rect.y1)
            clip = fitz.Rect(
                40,
                _HEADER_Y,
                page_rect.width - 40,
                fig_bottom,
            )

        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(clip=clip, matrix=mat)
        pix.save(str(output_path))

        print(f"  ✓ Extracted {figure_id} → {output_path.name} "
              f"({pix.width}×{pix.height}px, cropped from page {page_idx + 1})")
        return str(output_path)

    print(f"  ⚠ Could not locate {figure_id} caption in PDF")
    return None


def _find_body_text_top(page, below_y: float) -> float:
    """
    Find the y-coordinate where two-column body text starts below the
    figure panels.  Body text is identified as multi-line paragraph
    blocks that span roughly half the page width (one column).
    Returns the y0 of the first such block, or a sensible fallback.
    """
    blocks = page.get_text("blocks")
    page_rect = page.rect

    # Collect candidate body-text blocks below 'below_y'
    for block in sorted(blocks, key=lambda b: b[1]):
        if len(block) < 5 or not isinstance(block[4], str):
            continue
        y0, text = block[1], block[4].strip()
        block_width = block[2] - block[0]
        # Body text: starts below the figure area, is a real paragraph,
        # and occupies roughly one column width (not axis labels).
        if y0 > below_y + 30 and len(text) > 120 and \
                block_width > page_rect.width * 0.30:
            return y0 - 3

    return page_rect.height * 0.80  # fallback


def _sanitize_filename(name: str) -> str:
    """Convert a figure ID to a safe filename component."""
    return re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()


# ---------------------------------------------------------------------------
# 3. Render Mermaid diagrams to PNG
# ---------------------------------------------------------------------------

def _preprocess_mermaid(mermaid_code: str) -> str:
    """
    Preprocess Mermaid code for two-column PDF rendering:
      1. Convert literal \\n in node labels to <br/> for line breaks
      2. Convert horizontal (LR/RL) layouts to vertical (TD)
      3. Force vertical stacking of subgraphs by adding hidden links
    """
    code = re.sub(r'\\n', '<br/>', mermaid_code)
    code = re.sub(r'\bgraph\s+LR\b', 'graph TD', code)
    code = re.sub(r'\bgraph\s+RL\b', 'graph TD', code)

    # Detect subgraphs — Mermaid places them side-by-side by default.
    # Add an invisible link between the last node of one subgraph and
    # the first node of the next to force vertical stacking.
    subgraph_blocks = list(re.finditer(
        r'subgraph\s+(.+?)\n(.*?)\n\s*end',
        code, re.DOTALL
    ))
    if len(subgraph_blocks) >= 2:
        # Extract the first node ID from each subgraph
        sg_first_nodes = []
        for sg in subgraph_blocks:
            body = sg.group(2).strip()
            # Find first node reference (e.g., "A[..." or just "A ")
            node_match = re.search(r'^\s*(\w+)', body)
            if node_match:
                sg_first_nodes.append(node_match.group(1))

        # Add invisible links between consecutive subgraph entry nodes
        if len(sg_first_nodes) >= 2:
            links = []
            for i in range(len(sg_first_nodes) - 1):
                links.append(f"    {sg_first_nodes[i]} ~~~ {sg_first_nodes[i+1]}")
            code = code.rstrip() + "\n" + "\n".join(links) + "\n"
            print(f"    (added {len(links)} invisible link(s) to stack subgraphs vertically)")

    return code


# Maximum acceptable aspect ratio (width/height) for a diagram rendered
# into a single column.  Beyond this, text will be too small to read.
_MAX_ASPECT_RATIO = 2.5


def render_mermaid_diagram(mermaid_code: str, output_path: str,
                           mmdc_path: str = "mmdc",
                           font_family: str = "sans-serif") -> tuple[bool, int]:
    """
    Render a Mermaid diagram to PNG.

    Strategy:
      1. Try local mermaid-cli (mmdc) first
      2. Fall back to mermaid.ink web API
      3. After rendering, check aspect ratio; reject if too wide

    Parameters
    ----------
    font_family : str
        CSS font-family used in Mermaid theme.  Pass ``"Pretendard"``
        (or another CJK-capable font) when Korean text appears in
        node labels.

    Returns
    -------
    (success, render_scale) : tuple[bool, int]
        render_scale is 2 for mmdc (``-s 2``) and 1 for mermaid.ink.
    """
    # --- Attempt 1: local mermaid-cli ---
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".mmd", delete=False
    ) as f:
        f.write(mermaid_code)
        mmd_file = f.name

    # Write mmdc JSON config to set fontFamily
    mmdc_config = None
    try:
        cfg = {"theme": "neutral", "themeVariables": {"fontFamily": font_family}}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as cf:
            json.dump(cfg, cf)
            mmdc_config = cf.name

        result = subprocess.run(
            [mmdc_path, "-i", mmd_file, "-o", output_path,
             "-b", "white", "-s", "2", "-w", "1200",
             "-c", mmdc_config],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and Path(output_path).exists():
            if _check_diagram_aspect(output_path):
                print(f"  ✓ Rendered Mermaid diagram (mmdc) → {Path(output_path).name}")
                return True, 2  # mmdc uses -s 2
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    finally:
        os.unlink(mmd_file)
        if mmdc_config:
            os.unlink(mmdc_config)

    print(f"  ⚠ mmdc not available, trying mermaid.ink API...")

    # --- Attempt 2: mermaid.ink web API with preprocessing ---
    fixed_code = _preprocess_mermaid(mermaid_code)
    success = _render_mermaid_ink(fixed_code, output_path,
                                  font_family=font_family)

    if success and not _check_diagram_aspect(output_path):
        print(f"  ⚠ Diagram too wide (aspect ratio > {_MAX_ASPECT_RATIO}), "
              f"rejecting render")
        Path(output_path).unlink(missing_ok=True)
        return False, 2

    return success, 2  # mermaid.ink now renders at 2x (scale=2)


def _check_diagram_aspect(image_path: str) -> bool:
    """
    Verify the rendered diagram has an acceptable aspect ratio for
    single-column layout.  Returns True if OK, False if too wide.
    """
    try:
        from PIL import Image
        img = Image.open(image_path)
        w, h = img.size
        ratio = w / max(h, 1)
        print(f"    (rendered {w}×{h}px, aspect ratio {ratio:.1f})")
        return ratio <= _MAX_ASPECT_RATIO
    except Exception:
        return True  # can't check, assume OK


def _render_mermaid_ink(mermaid_code: str, output_path: str,
                         font_family: str = "sans-serif") -> bool:
    """Render a Mermaid diagram via mermaid.ink SVG + Playwright local rasterization.

    Strategy:
      1. Fetch SVG from mermaid.ink (text is in foreignObject → needs a real browser)
      2. Build an HTML page that loads ``@font-face`` for local Pretendard
         (or falls back to the requested ``font_family``)
      3. Render to PNG at 2× device-scale via Playwright headless Chromium
    """
    import base64
    import urllib.request
    import urllib.error
    import zlib

    # --- Step 1: Fetch SVG from mermaid.ink ---
    try:
        payload = json.dumps({
            "code": mermaid_code,
            "mermaid": {
                "theme": "neutral",
                "themeVariables": {"fontFamily": font_family},
            },
        })
        compressed = zlib.compress(payload.encode("utf-8"), 9)
        b64 = base64.urlsafe_b64encode(compressed).decode("ascii")
        url = f"https://mermaid.ink/svg/pako:{b64}?bgColor=white"

        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "image/svg+xml",
        })

        svg_data = None
        for attempt in range(3):
            try:
                timeout = 30 + attempt * 15
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    svg_data = resp.read()
                if svg_data and len(svg_data) > 200:
                    break
            except (urllib.error.URLError, OSError) as e:
                if attempt < 2:
                    print(f"  ⚠ Attempt {attempt + 1} failed ({e}), retrying...")
                    import time
                    time.sleep(2)
                else:
                    print(f"  ⚠ mermaid.ink SVG fetch failed after 3 attempts: {e}")
                    return False

        if not svg_data:
            return False
    except Exception as e:
        print(f"  ⚠ mermaid.ink SVG fetch error: {e}")
        return False

    # --- Step 2: Build HTML with embedded SVG + @font-face ---
    svg_text = svg_data.decode("utf-8")
    # Remove the @import url for font-awesome if present (not needed, slows render)
    svg_text = svg_text.replace(
        '@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css");',
        ''
    )

    # Discover local Pretendard font files for @font-face
    font_face_css = ""
    fc_dir = Path.home() / ".local" / "share" / "fonts"
    regular = fc_dir / "Pretendard-Regular.otf"
    bold = fc_dir / "Pretendard-Bold.otf"
    if regular.exists():
        reg_b64 = base64.b64encode(regular.read_bytes()).decode("ascii")
        font_face_css += (
            f"@font-face {{ font-family: 'Pretendard'; font-weight: 400; "
            f"src: url('data:font/otf;base64,{reg_b64}') format('opentype'); }}\n"
        )
    if bold.exists():
        bold_b64 = base64.b64encode(bold.read_bytes()).decode("ascii")
        font_face_css += (
            f"@font-face {{ font-family: 'Pretendard'; font-weight: 700; "
            f"src: url('data:font/otf;base64,{bold_b64}') format('opentype'); }}\n"
        )

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
{font_face_css}
* {{ font-family: Pretendard, '{font_family}', sans-serif !important; }}
body {{ margin: 0; padding: 0; background: white; display: inline-block; }}
svg {{ display: block; }}
</style>
</head><body>{svg_text}</body></html>"""

    # --- Step 3: Render with Playwright ---
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(device_scale_factor=2)
            page.set_content(html, wait_until="networkidle")
            # Wait a moment for fonts to load
            page.wait_for_timeout(500)
            # Get bounding box of the SVG
            svg_el = page.query_selector("svg")
            if svg_el:
                svg_el.screenshot(path=output_path, type="png")
            else:
                page.screenshot(path=output_path, type="png", full_page=True)
            browser.close()

        if Path(output_path).exists() and Path(output_path).stat().st_size > 500:
            kb = Path(output_path).stat().st_size // 1024
            print(f"  ✓ Rendered Mermaid diagram (playwright @2x) → "
                  f"{Path(output_path).name} ({kb} KB)")
            return True
        else:
            print(f"  ⚠ Playwright render produced empty/small image")
            return False
    except ImportError:
        print(f"  ⚠ Playwright not available")
        return False
    except Exception as e:
        print(f"  ⚠ Playwright render error: {e}")
        return False


# ---------------------------------------------------------------------------
# 3b. Diagram sizing — keep text ≤ body text size
# ---------------------------------------------------------------------------

# Mermaid renders text at ~16px logical size.  With ``-s 2`` the PNG
# contains glyphs at ~32px.  The two-column Typst layout yields a
# column width of roughly 227pt.  To keep diagram labels at or below
# the 9pt body text, we set the Typst image width so that the scale
# factor (typst_width / png_width) doesn't enlarge the 32px glyphs
# beyond 9pt ≈ 12px at 72 dpi.
#
# Formula:  max_width_pt = png_width_px / render_scale * (body_pt / mermaid_base_px)
#                        = png_width_px / 2 * (9 / 16) * (72/96)
#                        ≈ png_width_px * 0.21
# We round up a touch (×0.24) so diagrams aren't uncomfortably tiny.

_BODY_TEXT_PT = 9.0
_MERMAID_BASE_PX = 16.0             # Mermaid default font size in CSS px
_COLUMN_WIDTH_PT = 227.0            # approximate column width in 2-col A4
_MAX_DIAGRAM_HEIGHT_PT = 300.0      # cap diagram height (~40% of usable column)

def _diagram_width_typst(image_path: str, render_scale: int = 1) -> str:
    """Return a Typst width (e.g. ``'74%'``) so that the Mermaid base font
    appears at approximately ``_BODY_TEXT_PT`` in the PDF.

    Primary goal: diagram text ≈ body text size (9 pt).

    Secondary constraint: if the resulting height would exceed
    ``_MAX_DIAGRAM_HEIGHT_PT``, scale down to fit.  This prevents
    tall narrow diagrams from dominating the page while keeping
    wide compact diagrams at a comfortable reading size.

    Result is clamped to [50 %, 100 %] of the column width.
    """
    try:
        from PIL import Image
        img = Image.open(image_path)
        w_px, h_px = img.size
    except Exception:
        return "100%"  # can't read → fall back to full width

    # Width (in pt) at which Mermaid text == body text size
    target_w_pt = _BODY_TEXT_PT * w_px / (_MERMAID_BASE_PX * render_scale)

    # Check resulting height; if too tall, shrink to fit max height
    target_h_pt = target_w_pt * (h_px / w_px)
    if target_h_pt > _MAX_DIAGRAM_HEIGHT_PT:
        target_w_pt = _MAX_DIAGRAM_HEIGHT_PT * (w_px / h_px)

    # As percentage of column width, clamped to [50%, 100%]
    pct = max(50, min(100, int(target_w_pt / _COLUMN_WIDTH_PT * 100)))
    return f"{pct}%"


# ---------------------------------------------------------------------------
# 4. Convert markdown interview to Typst markup
# ---------------------------------------------------------------------------

def md_interview_to_typst(md_text: str, visual_blocks: list,
                           image_map: dict,
                           render_scales: dict | None = None) -> str:
    """
    Convert the interview markdown body into Typst markup.

    - **Host**: → styled host label
    - **Al-Hashimi**: → styled author label
    - <diagram> blocks → #figure with rendered PNG
    - <figure_ref> blocks → styled callout box
    - Inline **bold** and *italic* → Typst equivalents
    """
    # IMPORTANT: Replace visual blocks with unique placeholder tokens FIRST
    # (while positions are still valid on the original md_text).
    # After dialogue conversion (which escapes # and other Typst chars),
    # swap the placeholders back in with actual Typst markup.
    body = md_text
    placeholder_map = {}  # token → Typst markup

    # Replace visual blocks with placeholders; process in reverse to preserve positions
    for block in reversed(visual_blocks):
        replacement = ""
        block_id = id(block)

        if block["type"] == "diagram" and block_id in image_map:
            img_path_full = image_map[block_id]
            img_path = Path(img_path_full).name  # use filename only (relative to .typ)
            caption = _escape_typst(block["caption"])
            rscale = (render_scales or {}).get(block_id, 1)
            width = _diagram_width_typst(img_path_full, render_scale=rscale)
            replacement = (
                f'\n#figure(\n'
                f'  image("{img_path}", width: {width}),\n'
                f'  caption: [#text(size: 7.5pt)[{caption}]],\n'
                f')\n'
            )
        elif block["type"] == "diagram":
            # Fallback: render as styled box with description if image not available
            caption = _escape_typst(block["caption"])
            desc_lines = []
            for line in block["mermaid_code"].split("\n"):
                line = line.strip()
                if not line or line.startswith("style ") or line.startswith("graph "):
                    continue
                line = re.sub(r'\["?([^"\]]*)"?\]', r'(\1)', line)
                line = re.sub(r'\s*-->\|"?([^"|]*)"?\|\s*', r' → [\1] → ', line)
                line = re.sub(r'\s*-->\s*', r' → ', line)
                if line:
                    desc_lines.append(line)
            description = " / ".join(desc_lines[:6])
            replacement = (
                f'\n#block(\n'
                f'  width: 100%,\n'
                f'  inset: (x: 10pt, y: 8pt),\n'
                f'  fill: rgb("#f0f4f8"),\n'
                f'  radius: 3pt,\n'
                f'  stroke: (left: 2.5pt + rgb("#1565c0")),\n'
                f')[\n'
                f'  #set text(size: 8pt)\n'
                f'  *Conceptual Diagram*: {caption}\n\n'
                f'  #set text(size: 7pt, fill: rgb("#555555"))\n'
                f'  {_escape_typst(description)}\n'
                f']\n'
            )
        elif block["type"] == "figure_ref":
            fig_id = _escape_typst(block["figure_id"])
            caption = _escape_typst(block["caption"])
            why = _escape_typst(block["why"])

            if block_id in image_map:
                # We have an extracted figure image — embed it
                img_path = Path(image_map[block_id]).name  # relative to .typ
                replacement = (
                    f'\n#figure(\n'
                    f'  image("{img_path}", width: 100%),\n'
                    f'  caption: [#text(size: 7.5pt)[*{fig_id}*: {caption}]],\n'
                    f')\n'
                    f'#block(\n'
                    f'  width: 100%,\n'
                    f'  inset: (x: 10pt, y: 5pt),\n'
                    f'  fill: rgb("#fff8e1"),\n'
                    f'  radius: 3pt,\n'
                    f'  stroke: (left: 2.5pt + rgb("#f9a825")),\n'
                    f')[\n'
                    f'  #set text(size: 7.5pt, style: "italic", fill: rgb("#555555"))\n'
                    f'  {why}\n'
                    f']\n'
                )
            else:
                # No extracted image — render as a styled reference box
                replacement = (
                    f'\n#block(\n'
                    f'  width: 100%,\n'
                    f'  inset: (x: 10pt, y: 8pt),\n'
                    f'  fill: rgb("#fff8e1"),\n'
                    f'  radius: 3pt,\n'
                    f'  stroke: (left: 2.5pt + rgb("#f9a825")),\n'
                    f')[\n'
                    f'  #set text(size: 8pt)\n'
                    f'  *See {fig_id} in the original paper*: {caption}\n\n'
                    f'  #set text(size: 7.5pt, style: "italic", fill: rgb("#555555"))\n'
                    f'  {why}\n'
                    f']\n'
                )

        # Store actual Typst markup and insert a unique placeholder token
        token = f"__VISUAL_PLACEHOLDER_{block['start']}__"
        placeholder_map[token] = replacement
        body = body[:block["start"]] + f"\n{token}\n" + body[block["end"]:]

    # Now strip the header/footer (AFTER visual block replacement)
    # Remove the title heading
    body = re.sub(r"^#\s+.*?\n", "", body, count=1)

    # Remove the metadata blockquote (English or Korean)
    body = re.sub(
        r"^>\s+\*\*(?:Paper|논문)\*\*:.*?(?=\n---|\n\n\*\*Host)",
        "", body, flags=re.DOTALL | re.MULTILINE
    )

    # Remove horizontal rules
    body = re.sub(r"\n---\n", "\n", body)

    # Remove the closing italic note (English or Korean)
    body = re.sub(
        r"\n\*This interview was generated.*?\*\s*$", "", body, flags=re.DOTALL
    )
    body = re.sub(
        r"\n\*이 인터뷰는.*?\*\s*$", "", body, flags=re.DOTALL
    )

    # Convert dialogue lines, preserving placeholder tokens
    lines = body.split("\n")
    typst_lines = []
    in_dialogue = False  # track if we're inside a speaker's turn
    in_paragraph = False  # track multi-paragraph within same speaker
    for line in lines:
        stripped = line.strip()
        if not stripped:
            # Empty line: if mid-paragraph within a speaker's turn,
            # add paragraph spacing.  Otherwise just skip (block above/
            # below on the next Host/Author handles inter-turn gaps).
            if in_paragraph:
                typst_lines.append("#v(8pt)")
                in_paragraph = False
            else:
                typst_lines.append("")
            continue

        # Placeholder tokens — pass through verbatim (will be replaced later)
        if stripped.startswith("__VISUAL_PLACEHOLDER_") and stripped.endswith("__"):
            typst_lines.append(stripped)
            in_paragraph = False
            continue

        # Host dialogue — starts a new turn
        host_match = re.match(r"\*\*Host\*\*:\s*(.*)", stripped)
        if host_match:
            in_dialogue = True
            in_paragraph = True
            text = _convert_inline_formatting(host_match.group(1))
            typst_lines.append(
                f'#block(above: 1.6em, below: 0.3em)[\n'
                f'  #text(weight: "bold", fill: rgb("#c0392b"), size: 8.5pt)[Host:] '
                f'#text(size: 9pt)[{text}]\n'
                f']'
            )
            continue

        # Author dialogue — follows host, tighter gap (Q&A is one unit)
        author_match = re.match(r"\*\*([^*]+)\*\*:\s*(.*)", stripped)
        if author_match:
            in_dialogue = True
            in_paragraph = True
            name = _escape_typst(author_match.group(1))
            text = _convert_inline_formatting(author_match.group(2))
            typst_lines.append(
                f'#block(above: 0.6em, below: 0.3em)[\n'
                f'  #text(weight: "bold", fill: rgb("#1a1a2e"), size: 8.5pt)[{name}:] '
                f'#text(size: 9pt)[{text}]\n'
                f']'
            )
            continue

        # Regular text (shouldn't appear much in a pure dialogue interview)
        in_dialogue = False
        in_paragraph = False
        typst_lines.append(_convert_inline_formatting(stripped))

    result = "\n".join(typst_lines)

    # Final step: replace placeholder tokens with actual Typst markup
    for token, typst_markup in placeholder_map.items():
        result = result.replace(token, typst_markup)

    return result


def _escape_typst(text: str) -> str:
    """Escape characters that are special in Typst."""
    # Escape #, @, <, >, $ but NOT * (handled by inline formatting)
    text = text.replace("\\", "\\\\")
    text = text.replace("#", "\\#")
    text = text.replace("@", "\\@")
    text = text.replace("<", "\\<")
    text = text.replace(">", "\\>")
    text = text.replace("$", "\\$")
    return text


def _convert_inline_formatting(text: str) -> str:
    """Convert markdown inline formatting to Typst."""
    text = _escape_typst(text)
    # **bold** → #strong[...]  (process before single *)
    text = re.sub(r"\*\*(.+?)\*\*", r"#strong[\1]", text)
    # *italic* → #emph[...]
    text = re.sub(r"\*(.+?)\*", r"#emph[\1]", text)
    # `code` → #raw("...")
    text = re.sub(r"`([^`]+)`", r'#raw("\1")', text)
    return text


# ---------------------------------------------------------------------------
# 5. Build the final Typst document and compile to PDF
# ---------------------------------------------------------------------------

def build_typst_document(template_path: str, typst_body: str,
                          structure: dict, output_typ: str,
                          language: str = "en"):
    """
    Read the template, inject parameters and the interview body,
    and write the final .typ file.

    Parameters
    ----------
    language : str
        "en" for English, "ko" for Korean.  Controls font, UI labels,
        and the Typst ``lang`` attribute.
    """
    template = Path(template_path).read_text(encoding="utf-8")

    # ── Language-dependent parameters ────────────────────────────────────
    LANG_PARAMS = {
        "en": {
            "PARAM_FONT": '"Pretendard", "Inter", "Noto Sans"',
            "PARAM_LANG": "en",
            "PARAM_LEADING": "0.6em",
            "PARAM_SECTION_LABEL": "In-Depth Interview",
            "PARAM_LABEL_PAPER": "Paper",
            "PARAM_LABEL_PUBLISHED": "Published in",
            "PARAM_FOOTER_TEXT": "Generated by Paper Interview — an AI-assisted science communication tool.",
            "PARAM_CLOSING_NOTE": "This interview was generated as an accessible introduction to the paper for scientists in the field.",
        },
        "ko": {
            "PARAM_FONT": '"Pretendard", "Noto Sans KR", "Noto Sans"',
            "PARAM_LANG": "ko",
            "PARAM_LEADING": "0.72em",  # +20% line height for Korean readability
            "PARAM_SECTION_LABEL": "심층 인터뷰",
            "PARAM_LABEL_PAPER": "논문",
            "PARAM_LABEL_PUBLISHED": "게재지",
            "PARAM_FOOTER_TEXT": "Paper Interview로 생성 — AI 기반 과학 커뮤니케이션 도구.",
            "PARAM_CLOSING_NOTE": "이 인터뷰는 해당 분야 연구자들을 위해 논문을 소개하는 목적으로 AI를 활용하여 생성되었습니다.",
        },
    }
    params = LANG_PARAMS.get(language, LANG_PARAMS["en"])

    for key, value in params.items():
        template = template.replace(key, value)

    # ── Metadata parameters ──────────────────────────────────────────────
    authors_str = ", ".join(structure.get("authors", ["Unknown"]))
    template = template.replace("PARAM_TITLE", _escape_typst(structure.get("title", "Interview")))
    template = template.replace("PARAM_AUTHORS", _escape_typst(authors_str))
    template = template.replace("PARAM_JOURNAL", _escape_typst(
        f"{structure.get('journal', 'Journal')} {structure.get('volume', '')}, "
        f"{structure.get('pages', '')}, {structure.get('date', '')}"
    ))
    template = template.replace("PARAM_DOI", structure.get("doi", ""))

    # Determine author last name for label
    corresponding = structure.get("authors", ["Author"])[-1]  # last listed is often corresponding
    template = template.replace("PARAM_AUTHOR_NAME", _escape_typst(corresponding))

    # Replace the content placeholder with the actual interview body
    template = re.sub(
        r"// INTERVIEW_CONTENT_START.*?// INTERVIEW_CONTENT_END",
        typst_body,
        template,
        flags=re.DOTALL
    )

    Path(output_typ).write_text(template, encoding="utf-8")
    print(f"  ✓ Typst source written → {output_typ} (language={language})")


def compile_typst_to_pdf(typ_path: str, pdf_path: str,
                          font_paths: list[str] | None = None) -> bool:
    """Compile a .typ file to PDF using the typst Python package."""
    try:
        import typst as typst_mod
        kwargs = {}
        if font_paths:
            kwargs["font_paths"] = font_paths
        pdf_bytes = typst_mod.compile(typ_path, **kwargs)
        Path(pdf_path).write_bytes(pdf_bytes)
        print(f"  ✓ PDF compiled → {pdf_path}")
        return True
    except Exception as e:
        print(f"  ✗ Typst compilation failed: {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Font management — auto-download Pretendard if needed
# ---------------------------------------------------------------------------

_PRETENDARD_VERSION = "1.3.9"
_PRETENDARD_URL = (
    f"https://github.com/orioncactus/pretendard/releases/download/"
    f"v{_PRETENDARD_VERSION}/Pretendard-{_PRETENDARD_VERSION}.zip"
)


def ensure_pretendard_fonts(skill_dir: Path) -> list[str]:
    """
    Return a list of font directories containing Pretendard.

    Priority:
      1. Bundled fonts in ``skill_dir / assets / fonts``
      2. Auto-downloaded OTF from GitHub (cached in ``~/.cache/pretendard``)

    The caller should pass these to ``typst.compile(font_paths=...)``.
    """
    font_dirs: list[str] = []

    # 1) Bundled fonts shipped with the skill
    bundled = skill_dir / "assets" / "fonts"
    if bundled.is_dir() and any(bundled.glob("Pretendard-Regular.*")):
        font_dirs.append(str(bundled))
        print(f"  ✓ Found bundled Pretendard fonts → {bundled}")

    # 2) Auto-download cache
    cache_dir = Path.home() / ".cache" / "pretendard" / _PRETENDARD_VERSION
    cached_font = cache_dir / "Pretendard-Regular.otf"
    if cached_font.exists():
        font_dirs.append(str(cache_dir))
        print(f"  ✓ Found cached Pretendard fonts → {cache_dir}")
    else:
        print(f"  ⬇ Downloading Pretendard v{_PRETENDARD_VERSION} from GitHub...")
        try:
            import urllib.request
            import zipfile
            import io

            with urllib.request.urlopen(_PRETENDARD_URL, timeout=60) as resp:
                zip_data = resp.read()
            zf = zipfile.ZipFile(io.BytesIO(zip_data))
            cache_dir.mkdir(parents=True, exist_ok=True)
            for name in zf.namelist():
                if name.endswith(".otf") and "/static/" in name:
                    data = zf.read(name)
                    out_name = Path(name).name
                    (cache_dir / out_name).write_bytes(data)
            font_dirs.append(str(cache_dir))
            print(f"  ✓ Downloaded and cached Pretendard → {cache_dir}")
        except Exception as e:
            print(f"  ⚠ Failed to download Pretendard: {e}")

    if not font_dirs:
        print("  ⚠ No Pretendard fonts found; PDF text may not render correctly")

    # Also install to fontconfig so cairosvg (Mermaid SVG→PNG) can use them
    fc_dir = Path.home() / ".local" / "share" / "fonts"
    try:
        fc_dir.mkdir(parents=True, exist_ok=True)
        installed = False
        for d in font_dirs:
            for f in Path(d).glob("Pretendard-*.*"):
                dest = fc_dir / f.name
                if not dest.exists():
                    import shutil
                    shutil.copy2(f, dest)
                    installed = True
        if installed:
            subprocess.run(["fc-cache", "-f", str(fc_dir)],
                           capture_output=True, timeout=30)
            print(f"  ✓ Registered Pretendard with fontconfig → {fc_dir}")
    except Exception as e:
        print(f"  ⚠ Could not register fonts with fontconfig: {e}")

    return font_dirs


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Typeset Interview to PDF")
    parser.add_argument("--interview", required=True,
                        help="Path to interview markdown file")
    parser.add_argument("--paper", required=True,
                        help="Path to the original paper PDF")
    parser.add_argument("--structure", required=True,
                        help="Path to paper structure JSON")
    parser.add_argument("--template", required=True,
                        help="Path to Typst template (.typ)")
    parser.add_argument("--output-dir", required=True,
                        help="Working directory for intermediate files")
    parser.add_argument("--output", required=True,
                        help="Path for the final PDF output")
    parser.add_argument("--mmdc", default="mmdc",
                        help="Path to mermaid-cli (mmdc) executable")
    parser.add_argument("--language", default="en", choices=["en", "ko"],
                        help="Output language: 'en' (English) or 'ko' (Korean)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Font setup ───────────────────────────────────────────────────────
    print("=" * 60)
    print("STAGE 6: Font Setup")
    print("=" * 60)
    skill_dir = Path(args.template).resolve().parent.parent
    font_dirs = ensure_pretendard_fonts(skill_dir)

    # Load inputs
    md_text = Path(args.interview).read_text(encoding="utf-8")
    with open(args.structure, "r", encoding="utf-8") as f:
        structure = json.load(f)

    print()
    print("=" * 60)
    print("STAGE 6a: Parsing Visual Blocks")
    print("=" * 60)
    blocks = parse_visual_blocks(md_text)
    print(f"  Found {len(blocks)} visual blocks: "
          f"{sum(1 for b in blocks if b['type'] == 'diagram')} diagrams, "
          f"{sum(1 for b in blocks if b['type'] == 'figure_ref')} figure refs")

    # Map block id → image path
    image_map = {}        # block id → image path
    render_scales = {}    # block id → render scale (for Mermaid diagrams)

    print()
    print("=" * 60)
    print("STAGE 6b: Extracting Figures from Paper PDF")
    print("=" * 60)
    for block in blocks:
        if block["type"] == "figure_ref":
            img_path = extract_figure_from_pdf(
                args.paper, block["figure_id"], output_dir, structure
            )
            if img_path:
                image_map[id(block)] = img_path

    print()
    print("=" * 60)
    print("STAGE 6c: Rendering Mermaid Diagrams")
    print("=" * 60)
    # SVG from mermaid.ink is rasterized locally via Playwright headless
    # Chromium, so we can use the locally-installed Pretendard font.
    mermaid_font = "Pretendard"
    for i, block in enumerate(blocks):
        if block["type"] == "diagram":
            png_path = str(output_dir / f"diagram_{i}.png")
            success, rscale = render_mermaid_diagram(
                block["mermaid_code"], png_path, mmdc_path=args.mmdc,
                font_family=mermaid_font,
            )
            if success:
                image_map[id(block)] = png_path
                render_scales[id(block)] = rscale

    print()
    print("=" * 60)
    print("STAGE 6d: Converting to Typst Markup")
    print("=" * 60)
    typst_body = md_interview_to_typst(md_text, blocks, image_map,
                                       render_scales=render_scales)
    print(f"  ✓ Converted {len(typst_body)} chars of Typst markup")

    print()
    print("=" * 60)
    print("STAGE 6e: Building & Compiling PDF")
    print("=" * 60)
    final_typ = str(output_dir / "interview.typ")
    build_typst_document(args.template, typst_body, structure, final_typ,
                         language=args.language)
    success = compile_typst_to_pdf(final_typ, args.output,
                                    font_paths=font_dirs)

    if success:
        pdf_size = Path(args.output).stat().st_size / 1024
        print()
        print(f"✓ Final typeset PDF: {args.output} ({pdf_size:.0f} KB)")
    else:
        print("\n✗ PDF generation failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
