#!/usr/bin/env python3
"""Render a paper reader's-guide Typst content file from a JSON spec.

Usage:
    python render_content.py <content.json> <output.typ>

Reads a JSON file that describes the paper-specific content (metadata,
roadmap, the 20 quest questions, closing, and anatomy graph) and writes
a filled ``paper_content.typ`` that imports ``template.typ`` and calls
``render_guide``.  The generated Typst file can then be compiled with
``scripts/compile_guide.py``.

This lets the skill's AI-authored step produce a small structured JSON
file instead of a full Typst document — the Typst template never has to
be loaded into the model's context.

JSON schema (top-level keys):
  lang          : "en" | "ko"
  asset_dir     : string path to the skill's assets/ folder
  paper         : { title, authors, venue, year, tldr }   (all strings)
  roadmap       : string (Typst markup allowed)
  level1        : { name, intro, questions: [ { text, options[5], hint? }, ... ] }
  level2        : { name, intro, questions: [ { text, hint? }, ... ] }
  level3        : { name, intro, questions: [ { text, hint? }, ... ] }
  closing       : string (Typst markup allowed)
  paper_anatomy : {
    nodes: { key: { kind, pos: [x, y], label }, ... },
    edges: [ [from, to] | [from, to, "dashed"], ... ],
  }

``text``, ``options``, ``hint``, ``tldr``, and anatomy-node ``label`` are
passed through Typst's ``eval(..., mode: "markup")`` in the template, so
they may contain Typst markup (``_italic_``, ``*bold*``).  ``roadmap`` and
``closing`` are written as Typst content blocks, so they also support
markup.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


VALID_KINDS = {
    "motivation",
    "assumptions",
    "logical_flow",
    "experiments",
    "supporting",
    "evidence",
    "interpretations",
    "implications",
    "conclusions",
}


# ---------------------------------------------------------------------------
# Typst value emitters
# ---------------------------------------------------------------------------


def typst_string(value) -> str:
    """Encode a Python value as a Typst string literal."""
    if value is None:
        return "none"
    s = str(value)
    # Escape backslashes first, then double quotes.  Newlines inside a Typst
    # string literal are allowed, but normalise CRLF to LF for cleanliness.
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def typst_content_block(value) -> str:
    """Encode a string as a Typst content block ``[...]`` preserving markup."""
    if value is None:
        return "[]"
    s = str(value).replace("\r\n", "\n").replace("\r", "\n")
    # Inside a content block, the only characters that can accidentally break
    # the parser are ``\`` (Typst escape) and ``]`` (block terminator).  Leave
    # markup characters like ``_``, ``*`` alone so ``_italic_`` works.
    s = s.replace("\\", "\\\\").replace("]", "\\]")
    return f"[{s}]"


def typst_hint(value) -> str:
    """Encode an optional hint as a Typst string or ``none``."""
    if value is None or value == "":
        return "none"
    return typst_string(value)


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------


def render_paper_block(paper: dict) -> str:
    required = ("title", "authors", "venue", "year", "tldr")
    missing = [k for k in required if k not in paper]
    if missing:
        raise ValueError(f"paper is missing keys: {missing}")
    return (
        "#let paper = (\n"
        f"  title: {typst_string(paper['title'])},\n"
        f"  authors: {typst_string(paper['authors'])},\n"
        f"  venue: {typst_string(paper['venue'])},\n"
        f"  year: {typst_string(paper['year'])},\n"
        f"  tldr: {typst_string(paper['tldr'])},\n"
        ")"
    )


def render_l1_question(idx: int, q: dict) -> str:
    if "text" not in q:
        raise ValueError(f"Level 1 question #{idx} is missing 'text'")
    options = q.get("options")
    if not isinstance(options, list) or len(options) != 5:
        raise ValueError(
            f"Level 1 question #{idx} needs exactly 5 options, got {options!r}"
        )
    opts = ", ".join(typst_string(o) for o in options)
    return (
        f"    (text: {typst_string(q['text'])},\n"
        f"     options: ({opts}),\n"
        f"     hint: {typst_hint(q.get('hint'))}),"
    )


def render_short_question(idx: int, q: dict, level: int) -> str:
    if "text" not in q:
        raise ValueError(f"Level {level} question #{idx} is missing 'text'")
    return (
        f"    (text: {typst_string(q['text'])}, "
        f"hint: {typst_hint(q.get('hint'))}),"
    )


def render_level(var: str, value: dict, question_renderer) -> str:
    for key in ("name", "intro", "questions"):
        if key not in value:
            raise ValueError(f"{var} is missing key '{key}'")
    questions = "\n".join(
        question_renderer(i + 1, q) for i, q in enumerate(value["questions"])
    )
    return (
        f"#let {var} = (\n"
        f"  name: {typst_string(value['name'])},\n"
        f"  intro: {typst_string(value['intro'])},\n"
        f"  questions: (\n"
        f"{questions}\n"
        f"  ),\n"
        f")"
    )


def _format_pos(pos) -> str:
    if not isinstance(pos, (list, tuple)) or len(pos) != 2:
        raise ValueError(f"anatomy node 'pos' must be [x, y], got {pos!r}")
    x, y = pos
    return f"({x}, {y})"


def render_anatomy_nodes(nodes: dict) -> str:
    if not isinstance(nodes, dict) or not nodes:
        raise ValueError("paper_anatomy.nodes must be a non-empty object")
    lines = ["#let paper_anatomy_nodes = ("]
    for key, node in nodes.items():
        for required in ("kind", "pos", "label"):
            if required not in node:
                raise ValueError(
                    f"anatomy node '{key}' is missing '{required}'"
                )
        kind = node["kind"]
        if kind not in VALID_KINDS:
            raise ValueError(
                f"anatomy node '{key}' has invalid kind '{kind}'. "
                f"Must be one of: {sorted(VALID_KINDS)}"
            )
        lines.append(
            f"  {key}: ("
            f"kind: {typst_string(kind)}, "
            f"pos: {_format_pos(node['pos'])}, "
            f"label: {typst_string(node['label'])}),"
        )
    lines.append(")")
    return "\n".join(lines)


def render_anatomy_edges(edges: list, node_keys: set) -> str:
    if not isinstance(edges, list):
        raise ValueError("paper_anatomy.edges must be a list")
    lines = ["#let paper_anatomy_edges = ("]
    for idx, edge in enumerate(edges):
        if not isinstance(edge, (list, tuple)) or len(edge) not in (2, 3):
            raise ValueError(
                f"Edge #{idx} must be [from, to] or [from, to, style]: {edge!r}"
            )
        from_key, to_key = edge[0], edge[1]
        for k in (from_key, to_key):
            if k not in node_keys:
                raise ValueError(
                    f"Edge #{idx} references unknown node '{k}'"
                )
        if len(edge) == 3:
            style = edge[2]
            lines.append(
                f"  ({typst_string(from_key)}, {typst_string(to_key)}, "
                f"{typst_string(style)}),"
            )
        else:
            lines.append(
                f"  ({typst_string(from_key)}, {typst_string(to_key)}),"
            )
    lines.append(")")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Top-level renderer
# ---------------------------------------------------------------------------


HEADER = """\
// ============================================================
// Paper Reader's Guide — paper-specific content
//
// THIS FILE IS AUTO-GENERATED by scripts/render_content.py from a
// JSON content spec.  Do not edit by hand; edit the JSON source and
// re-render.  The rendering engine lives in template.typ.
// ============================================================
"""


FOOTER = """\
#render_guide(
  lang: lang,
  asset_dir: asset_dir,
  paper: paper,
  roadmap: roadmap,
  level1: level1,
  level2: level2,
  level3: level3,
  closing: closing,
  paper_anatomy_nodes: paper_anatomy_nodes,
  paper_anatomy_edges: paper_anatomy_edges,
)
"""


def render_typ(content: dict) -> str:
    for key in (
        "paper",
        "roadmap",
        "level1",
        "level2",
        "level3",
        "closing",
        "paper_anatomy",
    ):
        if key not in content:
            raise ValueError(f"Top-level JSON is missing key '{key}'")

    lang = content.get("lang", "en")
    if lang not in ("en", "ko"):
        raise ValueError(f"lang must be 'en' or 'ko', got {lang!r}")

    asset_dir = content.get("asset_dir", ".")

    anatomy = content["paper_anatomy"]
    if not isinstance(anatomy, dict) or "nodes" not in anatomy or "edges" not in anatomy:
        raise ValueError(
            "paper_anatomy must be an object with 'nodes' and 'edges'"
        )

    node_keys = set(anatomy["nodes"].keys())

    def _l2(idx, q):
        return render_short_question(idx, q, level=2)

    def _l3(idx, q):
        return render_short_question(idx, q, level=3)

    parts = [
        HEADER,
        '#import "./template.typ": render_guide',
        "",
        f"#let lang = {typst_string(lang)}",
        f"#let asset_dir = {typst_string(asset_dir)}",
        "",
        render_paper_block(content["paper"]),
        "",
        "#let roadmap = " + typst_content_block(content["roadmap"]),
        "",
        render_level("level1", content["level1"], render_l1_question),
        "",
        render_level("level2", content["level2"], _l2),
        "",
        render_level("level3", content["level3"], _l3),
        "",
        "#let closing = " + typst_content_block(content["closing"]),
        "",
        render_anatomy_nodes(anatomy["nodes"]),
        "",
        render_anatomy_edges(anatomy["edges"], node_keys),
        "",
        FOOTER,
    ]
    return "\n".join(parts)


def validate_counts(content: dict) -> None:
    """Warn (but don't fail) if the standard 8/8/4 question counts drift."""
    expected = {"level1": 8, "level2": 8, "level3": 4}
    for level, want in expected.items():
        got = len(content.get(level, {}).get("questions", []))
        if got != want:
            print(
                f"[warn] {level} has {got} questions; expected {want}",
                file=sys.stderr,
            )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("json", type=Path, help="Input content.json")
    ap.add_argument("output", type=Path, help="Path to write the filled .typ file")
    args = ap.parse_args()

    content = json.loads(args.json.read_text(encoding="utf-8"))
    validate_counts(content)

    typ_source = render_typ(content)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(typ_source, encoding="utf-8")
    print(f"Wrote {args.output}  ({args.output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
