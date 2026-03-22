---
name: paper-interview
description: >
  Generate a podcast-style in-depth scientific interview that introduces an academic
  paper. Uses multi-agent analysis (field expert, methods specialist, context historian,
  critical reviewer, accessibility translator, impact assessor) to prepare rich source
  material, then an editor agent curates the narrative, and a writer agent composes the
  final interview between a professional science interviewer and the paper's author.
  The user drops a PDF of the paper; all supplementary context is gathered via web search
  and PubMed/bioRxiv. MANDATORY TRIGGERS: "paper interview", "podcast interview for paper",
  "introduce this paper", "generate interview for this paper", "paper podcast", "deep dive
  interview", "interview about this paper", "논문 인터뷰", "논문 소개 인터뷰", "paper
  introduction interview". Also trigger when the user uploads a PDF and asks for a podcast,
  interview, deep dive, or accessible introduction of a scientific paper.
---

# Paper Interview Generator

Generate a dense, engaging, podcast-style interview that introduces an academic paper to
scientists in the same field. The interview should provide enough depth for specialists
while remaining compelling throughout.

## Language Selection

**At the very beginning of the workflow**, ask the user to choose the output language:

- **English** (`en`) — Interview text, UI labels, and PDF in English. Uses Pretendard font.
- **Korean** (`ko`, 한국어) — Interview text, UI labels, and PDF in Korean. Uses Pretendard font
  (which has full Korean glyph coverage).

Store the choice as a variable (e.g., `LANG="en"` or `LANG="ko"`) and pass it to both
`generate_interview.py --language $LANG` and `typeset_interview.py --language $LANG`.

If the user does not express a preference, default to English.

## Architecture Overview

The pipeline has 6 stages:

1. **Extract** — Read the PDF and extract structured content (including figure/table inventory)
2. **Research** — Gather background via web search and PubMed/bioRxiv
3. **Analyze** — Run 6 specialist sub-agents to prepare diverse material
4. **Curate** — Editor agent selects topics, structures the narrative, and creates a Visual Plan (deciding where to place embedded diagrams and original-paper figure references)
5. **Compose** — Writer agent produces the final interview transcript with Mermaid diagrams and figure placeholders interspersed in the dialogue
6. **Typeset** — Extract referenced figures from the paper PDF, render Mermaid diagrams to images, and compile everything into a professionally typeset PDF via Typst

## Stage 1: Extract Paper Content

Read the uploaded PDF. Use `pdftotext` first; if it produces garbled output, fall back to `pypdf`:

```python
from pypdf import PdfReader
reader = PdfReader("<paper_pdf_path>")
text = "\n".join(page.extract_text() or "" for page in reader.pages)
```

Then parse the text to identify these structural elements and save as JSON (`paper_structure.json`):

```python
{
    "title": "...",
    "authors": ["..."],
    "abstract": "...",
    "introduction": "...",
    "methods_summary": "...",        # first ~2000 chars of methods
    "results_summary": "...",        # first ~3000 chars of results
    "discussion_summary": "...",     # first ~2000 chars of discussion
    "figures_tables": ["captions"],  # extracted figure/table captions (see below)
    "has_graphical_abstract": true,  # whether the paper has a graphical abstract
    "references_sample": ["..."],    # first 20 references
    "keywords": ["..."]
}
```

### Figure and Table Extraction

Pay special attention to `figures_tables`. For each figure and table, extract:
- The identifier (e.g., "Figure 1", "Figure 2A-C", "Table 1", "Graphical Abstract")
- The full caption text
- A brief note on what type of visual it is (e.g., "bar chart", "heatmap",
  "microscopy image", "schematic", "flow diagram", "gel image", "scatter plot")

Format each entry as: `"Figure 1: [caption] [type: bar chart]"`

This metadata feeds into the editor's Visual Plan, which decides where to reference
original figures and where to generate explanatory diagrams in the interview.

If the paper has a **graphical abstract** (common in Cell, Elsevier, and Nature journals),
set `has_graphical_abstract: true` and include it as the first entry in `figures_tables`.

Extraction does NOT need to be perfect. Capture the gist of each section; the sub-agents
work well even with imperfect extraction. Spend at most 2 tool calls on this step.

## Stage 2: Research Background

Use web_search and PubMed tools to gather context. This material will be injected into
each sub-agent so they can make informed, grounded analyses.

### 2a. Search for the paper itself
Search for the paper by title to find:
- The published version (DOI, journal, publication date)
- Any preprint on bioRxiv/medRxiv
- Press coverage or blog posts about it

### 2b. Search for related work
Based on the paper's topic and references, run 3-5 targeted searches:
- Key prior work the paper builds on (search by first author names + topic keywords)
- Competing or complementary recent papers in the same area
- Any controversies or debates in this sub-field

### 2c. PubMed search (if PubMed tool is available)
Use the PubMed tool to find:
- Recent reviews in this area (for background context)
- The authors' related publications (for their research arc)

Save all research findings to `background_research.md` as structured notes.
Aim for 1-2 pages of relevant context. Do NOT over-research — 5-8 search calls total is
enough. The sub-agents need context, not exhaustive literature review.

## Stage 3: Multi-Agent Analysis

This is the heart of the skill. Run the orchestration script that calls the Anthropic API
to get diverse analytical perspectives on the paper.

### Setup and run

```bash
pip install anthropic --break-system-packages -q
python <skill_dir>/scripts/generate_interview.py \
    --paper paper_text.txt \
    --structure paper_structure.json \
    --background background_research.md \
    --output-dir agent_outputs/ \
    --language $LANG   # "en" or "ko"
```

The `--model` flag defaults to `claude-sonnet-4-20250514` but you can pass any Anthropic
model ID (e.g. `--model claude-opus-4-6`).

The script will call 6 specialist agents, 1 editor agent, and 1 writer agent.
Read `references/agent_prompts.md` for the detailed role definitions.

**If the script fails** (API key not available, network issue, etc.), fall back to the
manual agent simulation described below.

### Fallback: Manual Agent Simulation

If the Python script cannot run, simulate the sub-agents yourself. For each of the 6
specialist roles defined in `references/agent_prompts.md`, write a focused analysis
(300-500 words each) from that agent's perspective. Save each to a separate file in
the `agent_outputs/` directory. Then proceed to Stage 4 yourself.

The 6 specialist roles are:
1. **Field Expert** — Technical significance, novelty, positioning in the field
2. **Methods Specialist** — Experimental design, analytical rigor, technical innovation
3. **Context Historian** — Historical arc, how this work connects to the field's evolution
4. **Critical Reviewer** — Limitations, alternative interpretations, open questions
5. **Accessibility Translator** — Analogies, explanations for complex concepts, jargon
6. **Impact Assessor** — Real-world implications, future directions, broader significance

## Stage 4: Editorial Curation

Whether sub-agent outputs came from the script or manual simulation, now act as the
**Editor Agent**. Read all 6 analyses and the figure inventory, then produce an
editorial plan. Follow the detailed Editor prompt in `references/agent_prompts.md`
(Agent 7). The editorial plan must include:

- **Hook**: the single most compelling opening angle
- **Narrative Arc**: 4-5 acts with themes, topics, sources, and visual annotations
- **Visual Plan**: 3-6 visual elements (mix of `diagram` for concepts and `figure_ref`
  for original data). Space them out — consecutive visuals without dialogue between them
  break reading rhythm and feel like a slideshow rather than a conversation.
- **Must-Include Topics**: 5-8 non-negotiable points
- **Tension Points**: 2-3 moments for pushback or devil's advocate

Save to `editorial_plan.md`.

## Stage 5: Compose the Interview

Act as the **Writer Agent** defined in `references/agent_prompts.md` (Agent 8).
Using the editorial plan and all agent outputs, compose the final interview. This is the
most important stage — the output quality depends entirely on the writing here.

Key principles (see the full Writer prompt in `agent_prompts.md` for details):
- **Density**: every exchange advances understanding — no filler
- **Progressive disclosure**: layer complexity gradually so a reader who stops at any
  point has learned something proportional
- **Natural dialogue**: vary exchange lengths, include pushback moments, show candor
- **Visual embedding**: embed `<diagram>` and `<figure_ref>` blocks between dialogue
  turns as specified in the Visual Plan. Diagrams illustrate concepts (like whiteboard
  sketches); figure refs point to data in the original paper.

Save the final interview to `interview_final.md` and present to the user.

## Stage 6: Typeset to PDF

The final stage converts the markdown interview into a professionally typeset PDF that
resembles the layout of high-quality science journals (Nature, Science, Cell). This stage
has four sub-steps handled by the typesetting script.

### Prerequisites

```bash
pip install pymupdf typst --break-system-packages -q
npm install @mermaid-js/mermaid-cli  # provides mmdc
```

### 6a. Figure Extract Agent — Extract referenced figures from the paper PDF

Parse the markdown interview for `<figure_ref>` blocks, extract the `figure_id` from each
(e.g., "Figure 3B", "Graphical Abstract"), and use PyMuPDF to locate and render the
corresponding page from the original paper PDF as a high-resolution PNG (288 DPI).

Strategy for locating figures:
- **Graphical Abstract**: always page 1 of Cell/Elsevier papers
- **Figure N**: search PDF page text for the caption string "Figure N." and render that page
- **Fallback**: scan all pages for the figure ID string

The extracted PNGs are saved to the working directory as `fig_<sanitized_id>.png`.

Not every figure extraction will succeed (e.g., multi-panel figures spanning pages, or
figures with no text-searchable caption). When extraction fails, the typesetter falls back
to a styled reference callout box (gold accent bar) that directs the reader to the original
paper — this ensures the visual plan is always represented even on extraction failure.

### 6b. Render Mermaid Diagrams to PNG

Parse the markdown for `<diagram>` blocks, extract the Mermaid code from each, and render
to PNG using `mermaid-cli` (`mmdc`):

```bash
mmdc -i diagram.mmd -o diagram.png -b white -s 2 -w 1200
```

The `-s 2` flag produces 2× scale for crisp diagrams. If mermaid-cli is unavailable or
rendering fails, the typesetter falls back to a monospace code block showing the Mermaid
source with caption.

### 6c. Convert Markdown Interview to Typst Markup

The build script converts the interview markdown to Typst markup:

- `**Host**: text...` → red-accented host label with body text
- `**[Author Name]**: text...` → dark author label with body text
- `<diagram>` blocks → `#figure(image("diagram_N.png"), caption: [...])` if a rendered
  PNG is available, otherwise a styled code block
- `<figure_ref>` blocks → `#figure(image("fig_X.png"), caption: [...])` with a gold-accent
  annotation box if an extracted PNG is available, otherwise a gold-accent callout box
  citing the original figure
- Inline `**bold**`, `*italic*`, `` `code` `` → Typst equivalents

### 6d. Compile with Typst

The converted markup is injected into the Typst template at
`templates/interview.typ`, which defines:

- **Page layout**: A4, generous margins, page numbers in header (from page 2)
- **Title block**: Red accent bar, "In-Depth Interview" section label, article title,
  metadata box (authors, journal, DOI link)
- **Typography**: Pretendard (Inter-based sans-serif with full Korean coverage), 9pt
  body text, justified paragraphs. Fonts are auto-downloaded and cached by the script
  (see `ensure_pretendard_fonts()` in `typeset_interview.py`).
- **Dialogue styling**: Host labels in red (`#c0392b`), author labels in dark navy
  (`#1a1a2e`)
- **Figures**: Standard Typst `#figure()` with captions
- **Figure reference callouts**: Gold-accented boxes (`#fff8e1` fill, `#f9a825` left bar)
- **Closing**: Thin rule followed by italic generation note

Compilation uses the `typst` Python package:

```python
import typst
pdf_bytes = typst.compile("interview.typ")
```

### Running the typesetting script

```bash
python <skill_dir>/scripts/typeset_interview.py \
    --interview interview_final.md \
    --paper <paper_pdf_path> \
    --structure paper_structure.json \
    --template <skill_dir>/templates/interview.typ \
    --output-dir typeset_output/ \
    --output interview.pdf \
    --mmdc ./node_modules/.bin/mmdc \
    --language $LANG   # "en" or "ko" — must match generate_interview.py
```

### Fallback: Manual Typesetting

If the script fails, you can manually perform each sub-step:

1. **Extract figures**: Use PyMuPDF interactively:
   ```python
   import fitz
   doc = fitz.open("paper.pdf")
   page = doc[3]  # page containing Figure 1
   pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
   pix.save("fig_figure_1.png")
   ```

2. **Render diagrams**: Save each Mermaid block to a `.mmd` file and run:
   ```bash
   ./node_modules/.bin/mmdc -i diagram.mmd -o diagram.png -b white -s 2
   ```

3. **Build Typst file**: Copy the template, replace `PARAM_*` placeholders with actual
   metadata, replace the `INTERVIEW_CONTENT_START/END` block with hand-converted Typst
   markup, and compile:
   ```python
   import typst
   pdf_bytes = typst.compile("interview.typ")
   open("interview.pdf", "wb").write(pdf_bytes)
   ```

## Quality Checklist (verify before delivering)

Before presenting the final output, verify these key areas:

**Content quality** — Opening hook is compelling (not generic); all Must-Include Topics
are covered; technical claims match the paper (no hallucinated results); dialogue feels
natural with varied exchange lengths; host asks at least 2 challenging questions; author
acknowledges at least 1 limitation; length is 3000-5000 words.

**Visuals** — 3-6 visual elements embedded (at least 1 diagram + 1 figure ref); all
Mermaid diagrams use valid syntax; figure refs cite correct IDs from the paper; no two
visuals appear back-to-back without dialogue between them.

**PDF output** — Compiles without Typst errors; figures and diagrams appear at correct
positions; metadata (title, authors, journal, DOI) is accurate in the header; layout
has clean typography and spacing.

## Notes

- The skill works best for empirical research papers with clear methods and results.
  For review articles or theoretical papers, the Methods Specialist agent's output
  may be thin — compensate by expanding the Context Historian's role.
- Language selection (`--language en` or `--language ko`) controls: (a) the editor
  and writer agent prompts (Korean output when `ko`), (b) PDF UI labels and footer
  text, (c) the Typst `lang` attribute, and (d) font priority order. The Pretendard
  font family supports both Latin and Korean glyphs and is auto-downloaded by the
  typeset script if not already cached.
- For very long papers (>30 pages), focus extraction on the abstract, intro,
  results, and discussion. Methods can be summarized briefly.
