---
name: paper-readers-guide
description: Generate a treasure-hunt style reading guide for an academic paper — a typeset PDF of 20 quest questions that pulls the reader through the paper. Use when the user has a paper PDF and wants a reading guide, study guide, reading quest, questions to work through while reading, or "help me actually read this paper" — English or Korean output.
---

# Paper Reader's Guide

Turn any academic paper into a playful-but-rigorous reading quest. The output is a typeset PDF with 20 treasure-hunt style questions that pull the reader through the paper from opening hook to critical reflection.

## What this skill produces

A single-file Typst document compiled to PDF, containing:

1. **Cover block** — paper title, authors, venue, year, and a 2–3 sentence TL;DR teaser that sets the stage without spoiling the main result.
2. **Reading roadmap** — a short suggested path through the paper: what to skim, what to read closely, where to slow down, where to re-read.
3. **Three-level quest sheet** — 20 questions split as **8 / 8 / 4** across three thematic levels, each in a format matched to its purpose (see below).
4. **Closing note** — a light encouragement plus a "share what you found" prompt.

## The three quest levels

Treasure hunt, not exam. Every question points at a concrete target in the paper and is phrased to _motivate_ the reader to go look.

**Level 1 — Scout the Terrain (8 MC, 5 options).** Pulls readers across the paper's surface: abstract, methods, figures, results, discussion, supplementary. Coverage target: ~2 abstract/intro, 1–2 methods, 2–3 results/figures (different figures), 1 discussion, 1 supplementary/tables/bibliography. Numeric-retrieval cap: **max 2 of 8** — the rest should ask about named mechanisms, specific figure panels, chosen methods/tools, limitations, prior references, etc.

**Level 2 — Decode the Map (8 short-answer).** One-sentence answers that stitch pieces together. Coverage target: 2 on logical flow, 2 on methodological choices, 2 on figures→claim laddering, 1 cross-paper, 1 prior-work. The template gives exactly two ruled lines — if your answer needs a paragraph, rewrite the question.

**Level 3 — Face the Dragon (4 open-ended).** Real critical provocations, not generic extensions. Coverage target: 1 hidden/under-defended assumption, 1 missing experiment/control/ablation, 1 relation to the wider field (contradicts / confirms / complicates), 1 practical or conceptual limit.

**Shared rules (all levels).** Specific and concrete — cite §/figure/equation. Motivating, not evaluative — "according to the paper…", "the authors hide in §4…". Vary the surface across numbers, figures, sentences, and relationships.

**L1 distractor rules.** All five options plausible at first glance; ideally drawn from the paper itself but answering a different question. Mix the position of the correct answer across a–e. No "None of the above" / "All of the above". Never reveal the answer in the guide.

See `references/question_patterns.md` for worked examples across fields and all three formats.

## Workflow

### Step 1 — Confirm language with the user

Use the `AskUserQuestion` tool (not prose) with two options: **English** and **Korean**. If the user has been clearly writing in Korean, you may pre-select Korean as the default — still confirm.

If **Korean** is selected: all **technical and academic terms stay in English** — method names, gene/protein names, statistical terms (p-value, ROC, …), model/dataset names, jargon (CRISPR, transformer, …). Only prose connectors and quest narration are Korean. See `references/korean_localization.md` for examples.

### Step 2 — Delegate paper reading to a subagent

**Do not `Read` the full paper yourself.** Papers run 30–100k tokens; loading one into your own context inflates every downstream step. Instead, extract the paper and hand it to a subagent that returns a compact digest.

First, extract the paper to markdown (uses `markitdown`, which preserves headings, lists, and tables better than a plain text dump):

```bash
python scripts/extract_pdf.py <paper.pdf> > <working_dir>/paper.md
```

Then spawn a subagent via the `Agent` tool (general-purpose subagent is fine). Give it the path to `paper.md` and ask it to return a **paper digest** with exactly these sections, in plain text under ~600 lines total:

1. **One-paragraph TL;DR** — what the paper claims and why it matters. No spoilers worth more than a sentence.
2. **Key numbers** — 10–20 numeric facts with ≤10 words of context each (used for L1 numeric distractors and correct answers). Format: `value · context · location`.
3. **Figure inventory** — every main figure and notable supplementary figure: figure number, one-line caption of what it actually shows, what claim it supports.
4. **Methodological choices** — 5–10 bullets: the method/model/tool/control/dataset the authors picked and (briefly) why, including named alternatives they did not pick.
5. **Central claim chain** — the logical ladder from background → hypothesis → key experiments → main result → interpretation, in 6–12 lines.
6. **Limitations and open flanks** — hidden assumptions, missing controls/ablations, limits the paper acknowledges, tensions with prior work. Be specific: cite §/figure where possible.
7. **Prior-work anchors** — 3–6 references the paper frames itself against, with one-line "what this paper says about them".
8. **Paper anatomy skeleton** — a proposed node+edge layout for the anatomy graph (see Step 4 schema for node `kind` values and the edge format). The subagent suggests the structure; you refine it in Step 4.

Tell the subagent to be _specific and concrete_ (cite §/figure numbers, exact numeric values, exact phrasings of claims) and to include supplementary material if present. You will use the digest as the sole input to Steps 3 and 4 — the raw paper never enters your context.

### Step 3 — Draft the 20 questions

Work the question-crafting rules above. Lay out the 8 / 8 / 4 split. For Level 1, write the correct answer first, then write 4 plausible distractors (ideally from the paper). For Level 2, make sure each question is genuinely answerable in one sentence — if the answer would run longer, trim the question. After drafting, re-read and cull anything that feels generic.

### Step 4 — Write the content JSON

You do **not** edit any Typst files per paper. Author a single `content.json` that describes paper metadata, roadmap, the 20 questions, closing, and the anatomy graph. `build_guide.py` turns it into a PDF.

Get the full schema reference on demand (instead of keeping it in your context):

```bash
python scripts/render_content.py --print-schema
```

And the canonical filled-in example lives at `assets/content_example.json` — read it once if you need a concrete layout. Top-level shape at a glance:

```
{ lang, asset_dir, paper, roadmap, level1, level2, level3, closing, paper_anatomy }
```

Key constraints:

- `level1.questions` must have 8 items, each with exactly 5 `options`.
- `level2.questions` has 8 items; `level3.questions` has 4. Each is `{text, hint}`.
- `paper_anatomy.nodes[*].kind` is one of the nine labels listed in the schema; `pos` is `[x, y]` in grid units; edges are `[from, to]` or `[from, to, "dashed"]`.
- Typst markup (`_italic_`, `*bold*`) works in `tldr`, `roadmap`, `closing`, question `text`, each option, every `hint`, and anatomy node `label`. Never use `**bold**` — that's Markdown.
- You can leave `asset_dir` as `"."` — `build_guide.py` overrides it to stage assets correctly.

**Design the anatomy graph from the paper's actual logical structure** — not a placeholder. The shape should mirror the argument: parallel experiment→evidence tracks converging on a supporting spine, a linear chain, or a branching Y. Keep labels ≤ ~12 words and the graph ≤ ~18 nodes.

Flip `lang` to `"ko"` for a Korean guide. The engine switches headings, the how-to-use copy, anatomy-node kind labels, and the font stack accordingly. Keep technical/English terms in English (see `references/korean_localization.md`).

### Step 5 — Build the PDF

One command. `build_guide.py` renders the JSON to a Typst file, stages the template and asset files, and compiles to PDF — all in one shot:

```bash
python scripts/build_guide.py <working_dir>/content.json <output.pdf>
```

It also warns if the 8/8/4 question split is off. Korean fonts and Goonies-mood illustrations are auto-staged from the skill's `assets/` folder, so Korean output renders correctly even in sandboxes without system CJK fonts.

### Step 6 — Present the PDF to the user

Use the `present_files` tool (Cowork) or link the file directly (Claude Code). Include a brief one-line summary — the user is about to look at the PDF themselves.

## Reference files

- `references/question_patterns.md` — worked examples for each of the three formats, across different fields, with commentary on why each works (and why weak ones fail).
- `references/korean_localization.md` — rules for Korean output: which terms to keep in English, example sentences, punctuation conventions.
- `references/typst_styling.md` — notes on modifying the template (page color, accent, fonts) if the user asks for customization.

## Assets and scripts

- `assets/content_example.json` — a filled-out placeholder JSON showing the exact structure the renderer expects. Use it as the schema reference when authoring `content.json`.
- `assets/template.typ` — the rendering engine (layouts, styling, localized strings, Fletcher anatomy renderer, quest-box components). Exposes `render_guide(...)`. **Do not read this file into context** — treat it as an opaque library. `build_guide.py` stages it automatically; only touch it for visual customization.
- `assets/img-{cover,roadmap,level1,level2,level3,finished}.jpeg` — Goonies-mood illustrations for the cover, roadmap inset, level openers, and closing scene.
- `assets/SeedKRex-*.otf` — bundled Korean font family (Regular / Regular Italic / Bold / Bold Italic) so Korean guides render with proper Korean typography _and_ italic/bold emphasis, even in sandboxes without system CJK fonts. The engine's Korean font stack is `("SeedKRex", "Lato")`.
- `scripts/extract_pdf.py` — pulls Markdown-formatted text from the input PDF using `markitdown`.
- `scripts/render_content.py` — turns `content.json` into a filled `paper_content.typ`. Supports `--print-schema` to print the schema reference on demand. Keeps the Typst template out of your model context.
- `scripts/compile_guide.py` — low-level Typst→PDF compiler with the bundled font path.
- `scripts/build_guide.py` — one-shot wrapper: renders JSON, stages assets, and compiles in a single invocation. Use this from Step 5.

## Common pitfalls to avoid

- **Spoilers in the TL;DR.** Make the reader _want_ to find the answer, don't hand it over.
- **Bunching L1 questions in one section.** If all 8 come from the abstract, you've failed the "pull them through the paper" objective.
- **Shallow L3 provocations.** "How would you extend this work?" is weaker than "Figure 4's claim rests on an assumption stated only in §2.1 — is it defensible?"
- **Editing generated files.** Never edit `paper_content.typ` — it's overwritten. Edit `content.json` and re-run `build_guide.py`.
