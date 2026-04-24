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

The levels are framed as a treasure hunt, not an exam. Questions are phrased to _motivate_ the reader to look somewhere specific in the paper, not to test whether they already know the answer.

### Level 1 — Scout the Terrain (8 questions, multiple choice with 5 options)

Easy-entry quests that pull the reader across every major section: abstract, figures, methods, results, discussion, supplementary. Each one points to a concrete fact, number, figure panel, or sentence, and asks the reader to pick which of five options the paper actually supports.

**Why multiple choice works for treasure-hunt feel.** The distractors are the game. A good MC question gives five plausible-sounding options — ideally all drawn from the paper itself but placed in different contexts, or common misreadings, or near-misses from adjacent work. The reader has to actually find the right place in the paper to pick correctly. Guessing from the question alone should not work.

**Distractor-writing rules:**
- All 5 options should be plausible at first glance. No obvious throwaways like "42" or "a unicorn".
- Prefer distractors that are _actually in the paper_ but answer a different question. Example: if the question is "what is the method's top-1 accuracy on the benchmark?", use 4 other numbers that appear in the paper (a baseline's accuracy, a different benchmark's accuracy, a loss value, etc.).
- Mix the position of the correct answer — don't always make it (c). Roughly randomize across a, b, c, d, e over the 8 questions.
- Never include "(e) None of the above" or "(e) All of the above" — those are exam clichés and break the treasure-hunt feel.
- Don't reveal the answer in the guide. The reader's satisfaction comes from hunting it down.

**Coverage target across the 8 questions:** 2 from abstract/intro, 1–2 from methods, 2–3 from results/figures (different figures), 1 from discussion, 1 from supplementary/tables/bibliography.

**Diversify what the questions target — cap numeric retrieval at 2/8.** Numbers are the easiest type to turn into MC (five plausible-looking percentages, batch sizes, fold-changes), so there's a real pull toward writing 4–6 numeric questions out of 8. Resist it. At least **6 of the 8 Level 1 questions should ask about something other than a number** — a named concept or mechanism, a specific figure panel that does a specific job, which method/software/tool was chosen, which prior reference the authors engage with, a named state or condition, a specific sentence's claim in the discussion, the identity of a control experiment. The treasure hunt feels richer when the answers vary in shape.

Non-numeric L1 targets that work well:
- Which chemical mechanism / physical process does the paper invoke for phenomenon X?
- Which figure panel carries the authors' strongest evidence for claim Y?
- Which baseline / control / method did the authors choose (from 5 plausible choices)?
- Which named structural state, condition, or regime does the paper resolve?
- Which limitation does the discussion explicitly call out?
- Which software / dataset / tool is used?
- Which prior reference does the paper frame itself against?

### Level 2 — Decode the Map (8 questions, short answer)

Questions that require stitching pieces together but whose answer fits in **a few words or one sentence**. These reward careful reading without demanding long written answers.

**Good short-answer patterns:**
- "In one sentence, why did the authors use _method X_ instead of _method Y_?"
- "Name the two figures that together support the 'generalizes beyond benchmark' claim."
- "What single assumption in §2.1 does the Figure 3 result depend on?"
- "Which prior reference does this paper most directly respond to, and with what one-line objection?"

**Coverage target:** 2 on logical flow (background → claim), 2 on why methodological choices were right, 2 on how figures/tables ladder up to discussion claims, 1 on a cross-paper relationship, 1 on relation to cited prior work.

The template renders two ruled lines after each Level 2 question — enough for a single sentence, not enough for a paragraph. That constraint is the point.

### Level 3 — Face the Dragon (4 questions, open-ended reflection)

Deep questions: what would break this result? What's the weakest link? What happens if the main assumption is relaxed? How does this sit with the broader field? Each Level 3 question gets a larger note box for reflection.

**Coverage target:** 1 on a hidden or under-defended assumption, 1 on a missing experiment/control/ablation, 1 on how this sits in the wider field (contradicts / confirms / complicates prior work), 1 on a practical or conceptual limit of the approach.

### Shared question-crafting rules (applies to all levels)

- Be **specific and concrete** — cite the section, figure, or equation where the reader should look. Good: "In Figure 3B, two curves cross at a surprising point — according to the paper, at what x-value?". Bad: "What does Figure 3 show?"
- Be **motivating, not evaluative** — phrasing like "can you spot…", "according to the paper…", "the authors hide in §4…", "which of these does the paper actually claim?" works well.
- Each question should have a **concrete target** — a specific answer exists in the paper (levels 1–2) or is a genuine open question the reader can think through (level 3).
- **Vary the surface** — some questions look at a specific number, some at a figure, some at a sentence, some at a relationship between two parts of the paper.
- **Level 3 questions should gesture at real weaknesses or extensions** — e.g., a hidden assumption, a missing control, a limitation the paper underplays, a contradiction with prior work. Read carefully enough to find real things, not generic filler.

For worked examples across multiple fields and all three formats, see `references/question_patterns.md`.

## Workflow

### Step 1 — Confirm language with the user

Ask the user which language they want the guide in: **English** or **Korean**. Do not default silently. If the conversation has strong signals (e.g., the user has been writing entirely in Korean), you can still ask briefly but propose the matching default.

If **Korean** is selected: all **technical and academic terms stay in English**. This includes method names, gene/protein names, molecule names, statistical terms (p-value, confidence interval, ROC), model names, dataset names, field-specific jargon (e.g., "CRISPR", "transformer", "self-attention", "single-cell RNA-seq"), and anything the reader will encounter in the paper written in English. Prose connectors, framing, and quest narration are in Korean. See `references/korean_localization.md` for examples.

### Step 2 — Read the paper

Extract the text of the PDF so you can identify the real content to hunt for. Use the bundled helper (which uses Microsoft's `markitdown` under the hood — it preserves headings, lists, and table structure better than a plain text dump):

```bash
python scripts/extract_pdf.py <paper.pdf> > /tmp/paper.md
```

Read it carefully enough to find:
- Specific numbers, figure panels, and sentences worth pointing at (Level 1) — and plausible distractor numbers or claims pulled from other parts of the paper.
- The central claim and how the figures/methods chain supports it (for Level 2).
- Real weaknesses, unstated assumptions, or tensions with other work (for Level 3).

Skim the full body. Don't skip the supplementary if available — often the best Level 1 quests hide there.

### Step 3 — Draft the 20 questions

Work the question-crafting rules above. Lay out the 8 / 8 / 4 split. For Level 1, write the correct answer first, then write 4 plausible distractors (ideally from the paper). For Level 2, make sure each question is genuinely answerable in one sentence — if the answer would run longer, trim the question. After drafting, re-read and cull anything that feels generic.

### Step 4 — Write the content JSON

You do **not** edit any Typst files per paper. Instead, author a single JSON file (`content.json`) that describes the paper-specific content — metadata, roadmap, the 20 questions, closing, and the anatomy graph. A Python script turns it into a filled Typst file; the template is never loaded into your context.

**Minimal schema** (see `assets/content_example.json` for a filled-out placeholder):

```json
{
  "lang": "en",
  "asset_dir": "<absolute path to the skill's assets/ folder>",
  "paper": {
    "title": "...",
    "authors": "...",
    "venue": "...",
    "year": "...",
    "tldr": "2-3 sentence teaser (Typst markup allowed)"
  },
  "roadmap": "Reading roadmap paragraph (Typst markup allowed)",
  "level1": {
    "name": "Level 1 — Scout the Terrain",
    "intro": "Eight multiple-choice quests that pull you across the paper...",
    "questions": [
      {
        "text": "Question text? (Typst markup allowed)",
        "options": ["Distractor", "Correct", "Distractor", "Distractor", "Distractor"],
        "hint": null
      }
      /* ... 8 total ... */
    ]
  },
  "level2": {
    "name": "Level 2 — Decode the Map",
    "intro": "Eight short-answer quests...",
    "questions": [
      { "text": "...", "hint": null }
      /* ... 8 total ... */
    ]
  },
  "level3": {
    "name": "Level 3 — Face the Dragon",
    "intro": "Four open-ended provocations...",
    "questions": [
      { "text": "...", "hint": null }
      /* ... 4 total ... */
    ]
  },
  "closing": "Closing paragraph (Typst markup allowed)",
  "paper_anatomy": {
    "nodes": {
      "key1": { "kind": "motivation", "pos": [2, 0], "label": "..." }
      /* more nodes ... */
    },
    "edges": [
      ["key1", "key2"],
      ["key1", "key3", "dashed"]
    ]
  }
}
```

Rules:

- `lang` — `"en"` or `"ko"`.
- `asset_dir` — absolute path (or working-dir-relative) to the skill's `assets/` folder. The illustrations (`img-cover.jpeg`, `img-roadmap.jpeg`, `img-level1.jpeg`, `img-level2.jpeg`, `img-level3.jpeg`, `img-finished.jpeg`) and the SeedKRex Korean fonts live there.
- `options` — exactly five strings for every Level 1 question.
- `hint` — either `null` or a short string.
- `paper_anatomy.nodes[*].kind` — one of `motivation`, `assumptions`, `logical_flow`, `experiments`, `supporting`, `evidence`, `interpretations`, `implications`, `conclusions`. Multiple nodes of the same kind are allowed.
- `paper_anatomy.nodes[*].pos` — `[x, y]` in grid units (reals are fine); x grows right, y grows down.
- `paper_anatomy.edges[*]` — `[from_key, to_key]` for a solid edge, or `[from_key, to_key, "dashed"]` for a dashed edge.

**Design the paper's anatomy graph.** The anatomy diagram under the roadmap must reflect _this paper's actual logical structure_ — do not ship a placeholder. Lay the graph out so the shape tells the paper's story: parallel experiment→evidence tracks converging on a supporting spine, a linear chain, or a branching Y — whatever matches the actual argument. The renderer auto-scales the diagram down if it is wider than the text column, so wide graphs are fine. Keep labels ≤ ~12 words and the graph ≤ ~18 nodes.

**Typst markup in text fields.** `tldr`, `roadmap`, `closing`, every question `text`, each option string, every `hint`, and each anatomy node `label` are passed through Typst's markup evaluator, so you can use:

- `_word_` → _italic_ (single underscores).
- `*word*` → **bold** (single asterisks).

Never use `**word**` for bold — that's Markdown, and Typst will render the asterisks literally. For emphasis of method names, concepts, or figure references in question text, use `_italic_` (the running convention in this skill).

Flip `lang` to `"ko"` for a Korean guide. The engine switches headings, the how-to-use copy, anatomy-node kind labels, and the font stack (to the bundled SeedKRex family) accordingly. Paper-specific content (TL;DR, roadmap, questions, anatomy node labels) is whatever _you_ write — follow the Korean localization rule of keeping technical/English terms in English.

### Step 5 — Render the Typst file, then compile to PDF

Two commands: first render the JSON into a filled `paper_content.typ`, then compile it. Write both outputs into your working directory.

```bash
python scripts/render_content.py <working_dir>/content.json <working_dir>/paper_content.typ
python scripts/compile_guide.py <working_dir>/paper_content.typ <output.pdf>
```

`render_content.py` also prints a warning if the 8/8/4 question split is off. The generated `paper_content.typ` does `#import "./template.typ"`, so copy `assets/template.typ` into the same working directory beside it before calling `compile_guide.py`.

The `compile_guide.py` script bundles the Korean font path automatically so Korean output renders correctly even in sandboxes without system CJK fonts.

### Step 6 — Present the PDF to the user

Use the `present_files` tool (Cowork) or link the file directly (Claude Code). Include a brief one-line summary — the user is about to look at the PDF themselves.

## Styling philosophy

The document should feel like a well-designed game manual crossed with a scholarly pamphlet — professional but warm. The template already encodes this: serif body text, a single accent color, clean quest-number badges, tasteful answer spaces, generous line height. The treasure-hunt feel comes from the _question phrasing_ and the _plausibility of the MC distractors_, not from visual kitsch. No emojis, no clip art, no heavy color blocks.

## Reference files

- `references/question_patterns.md` — worked examples for each of the three formats, across different fields, with commentary on why each works (and why weak ones fail).
- `references/korean_localization.md` — rules for Korean output: which terms to keep in English, example sentences, punctuation conventions.
- `references/typst_styling.md` — notes on modifying the template (page color, accent, fonts) if the user asks for customization.

## Assets and scripts

- `assets/content_example.json` — a filled-out placeholder JSON showing the exact structure the renderer expects. Use it as the schema reference when authoring `content.json`.
- `assets/template.typ` — the rendering engine (layouts, styling, localized strings, Fletcher anatomy renderer, quest-box components). Exposes `render_guide(...)`. **You do not need to read this file into context** — treat it as an opaque library. Copy it next to the generated `paper_content.typ` so the relative import resolves. Only edit for visual customization.
- `assets/img-{cover,roadmap,level1,level2,level3,finished}.jpeg` — Goonies-mood illustrations for the cover, roadmap inset, level openers, and closing scene.
- `assets/SeedKRex-*.otf` — bundled Korean font family (Regular / Regular Italic / Bold / Bold Italic) so Korean guides render with proper Korean typography _and_ italic/bold emphasis, even in sandboxes without system CJK fonts. The engine's Korean font stack is `("SeedKRex", "Lato")`.
- `scripts/extract_pdf.py` — pulls Markdown-formatted text from the input PDF using `markitdown`.
- `scripts/render_content.py` — turns a `content.json` into a filled `paper_content.typ`. Keeps the Typst template out of your model context.
- `scripts/compile_guide.py` — compiles the generated `paper_content.typ` to PDF with the bundled font path.

## Common pitfalls to avoid

- **Generic questions.** "What is the methodology?" is a textbook question, not a quest. Point at something specific.
- **Weak MC distractors.** "(a) 91% (b) 0% (c) π (d) 42 (e) impossible to know" — the distractors need to be plausible. Draw them from the paper.
- **Too many numeric L1 questions.** Numbers are the easiest target to turn into MC, so you'll unconsciously write 4–6 numeric ones. Cap is 2 out of 8. Check before submitting.
- **Level 2 that needs a paragraph.** If you can't answer your own Level 2 question in one sentence, rewrite it.
- **Spoilers in the TL;DR.** The cover teaser should make the reader _want_ to find the answer, not hand it to them.
- **Unbalanced sections.** If all 8 Level 1 questions come from the abstract, you've failed the "pull them through the whole paper" objective. Spread them.
- **Level 3 that isn't actually critical.** "How would you extend this work?" is weaker than "Figure 4's claim rests on an assumption stated only in §2.1 — is it actually defensible?"
- **Translating technical terms in Korean output.** Never "단백질 접힘" for "protein folding" if the paper uses "protein folding". Keep the English term and only translate the connective tissue.
- **Using `*` for italic in Typst.** It's bold. Use `_word_` for italic.
- **Trying to edit `paper_content.typ` directly.** Don't. Edit the JSON and re-run `scripts/render_content.py`. The generated Typst file is overwritten on every render.
