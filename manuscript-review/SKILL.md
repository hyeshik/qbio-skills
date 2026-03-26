---
name: manuscript-review-panel
description: >
  Run a multi-perspective review panel on a manuscript draft to help authors
  improve it for high-impact publication. Simulates 13 specialist reviewers
  who each review the paper, discuss disagreements, and produce a synthesized
  improvement roadmap. Agents search PubMed, bioRxiv, and the web for
  references. MANDATORY TRIGGERS: manuscript review, paper review, review my
  paper, review this manuscript, review panel, improve my paper,
  pre-submission review, mock peer review, reviewer feedback, review draft,
  multi-agent review, help me improve this paper, feedback on my manuscript,
  strengthen my paper. Use when the user uploads a manuscript (PDF, DOCX, or
  text) and asks for review, feedback, or improvement suggestions — even
  casually like "what do you think of this paper" or "can you review this
  draft". Also trigger for anticipating reviewer comments or pre-submission
  checks.
---

# Manuscript Review Panel

A multi-agent review system that helps authors improve their manuscript
for high-impact publication. Thirteen specialist personas review the paper
from different angles, discuss disagreements, and produce a unified
improvement roadmap delivered as an interactive HTML report with Mermaid
diagram support.

## Philosophy

This is NOT a mock peer review for accept/reject. The entire panel exists
to help the authors make their research stronger — better writing, clearer
presentation, stronger evidence, better positioning. Even the harshest
persona (the devil's advocate) frames criticism as "here's what a hostile
reviewer will say, and here's how to preempt it."

## How It Works

The review runs in four phases:

1. **Individual Reviews** — 13 agents each review the manuscript from their
   unique perspective (editor, strategist, devil's advocate, methods expert,
   trend watcher, narrative architect, writing specialist, etc.)
2. **Disagreement Detection** — An analysis agent identifies where reviewers
   disagree on substance
3. **Moderated Discussion** — A discussion facilitator works through each
   disagreement and produces actionable recommendations
4. **Final Synthesis** — A meta-reviewer synthesizes everything into a
   structured improvement roadmap

## Before You Start

1. Read `references/personas.md` to understand the 13 reviewer personas,
   their focus areas, and review structures.

2. If you have an Anthropic API key and want to use the automated pipeline,
   see `references/script-usage.md`. Otherwise, use Manual Orchestration
   below (the preferred approach in Cowork and Claude.ai).

## Optional: Ask the user what they need

Before launching the full panel, you can ask:

- **Target journal or venue?** (affects framing advice from editor persona)
- **Submission timeline?** (affects whether "do more experiments" is useful)
- **Specific concerns?** (any areas they already know are weak?)
- **Which reviewers to emphasize?** (they can pick a subset — see Customization)

This is optional — if the user just says "review my paper," run the full
panel with sensible defaults.

## Manual Orchestration

Run the review by role-playing each agent persona yourself. This is the
preferred approach in Cowork and Claude.ai — no API key or script needed.

### Manual Phase 1: Read the manuscript carefully

Read the full manuscript. Extract and note:
- The main claim / contribution
- Methods used
- Key results and figures
- Target audience and field

### Manual Phase 2: Run each reviewer perspective

For each persona in `references/personas.md`, adopt that persona's
viewpoint and write a review. The minimum useful set is:

**Core 7 (always run these):**
1. 😈 Devil's Advocate — anticipate hostile reviewer attacks
2. 🔬 Methods & Logic — check technical rigor
3. 📊 Trend Expert — check literature and novelty (USE WEB SEARCH)
4. 🤝 Collaborator — identify what's undersold or missing
5. ✍️ Professional Editor — improve writing and structure
6. 📝 Tech Writer — improve figures and presentation
7. 🏛️ Narrative Architect — build immersive, compelling, logically valid narrative

**Extended (run if time allows):**
8. 📰 Editor Perspective — journal fit and impact framing
9. 🎯 Strategic Advisor — broader impact narrative
10. 🔭 Adjacent Field — accessibility check
11. 🧪 Lab Colleague — practical quick wins
12. 🚀 Visionary — ambitious framing suggestions
13. 🛠️ Technical Expert — methods optimization

For agents marked with web search, actively search PubMed and the web:
- Search for recent papers on the same topic
- Check if key claims are supported by current literature
- Look for missing references
- Check for competing/overlapping preprints on bioRxiv

### Manual Phase 3: Identify and discuss disagreements

After all reviews, compare them and identify where they disagree.
For each disagreement:
1. State both positions
2. Classify: factual, methodological preference, or judgment call
3. Give a clear recommendation to the authors

### Manual Phase 4: Synthesize the final report

Produce the final report following this structure:

```
## Executive Summary
(Overview: what works, what needs improvement, top 3 priorities)

## Strengths (Don't Change These)
(What's working well — authors need to know what to preserve)

## Critical Improvements (Must-Do)
(Ranked by impact. Each: issue → why it matters → how to fix)

## Recommended Improvements (Should-Do)
(Important but not deal-breaking)

## Experiments & Analyses to Consider
(Additional work that would strengthen claims. Note feasibility.)

## Writing & Presentation
(Clarity, figures, structure, narrative improvements)

## Literature & Positioning
(Missing refs, novelty concerns, positioning advice)

## Points of Disagreement
(Where panel members disagreed, with discussion)

## Minor Points
(Small fixes)

## Recommended Action Plan
(Prioritized checklist: immediate → short-term → longer-term)
```

## Customization

### Running a subset of agents

Users may not need all 13 perspectives. Common subsets:

- **Quick review** (3 agents): devils_advocate, professional_editor, trend_expert
- **Technical deep-dive** (4): devils_advocate, methods_obsessive, technical_expert, collaborator
- **Writing focus** (4): professional_editor, tech_writer, narrative_architect, adjacent_field
- **Pre-submission check** (7): the Core 7 listed above
- **Full panel** (13): all agents

### Adding context

If the user provides additional context (cover letter, target journal,
specific concerns), prepend it to each agent's review prompt so every
persona has the same background information.

### Using PubMed and bioRxiv searches

Agents with search capability (trend_expert, devils_advocate, technical_expert,
methods_obsessive, strategic_advisor, narrative_architect) should actively
search PubMed and the web:
- `[main topic] [key method] site:pubmed.ncbi.nlm.nih.gov` — recent papers
- `[topic] site:biorxiv.org` — preprints that might scoop or overlap
- `[specific claim or method]` — fact-checking specific assertions
- `[author names] [topic]` — the authors' prior related work

When PubMed MCP tools are available, use `search_articles` with relevant
queries.

## Output Format

The primary deliverable is an **interactive HTML report** saved to the
user's output directory as `review_report_<manuscript_name>.html`.
A supplementary Markdown version is saved alongside it.

The HTML report supports Mermaid diagrams (action-plan flowcharts,
priority matrices, etc.), collapsible reviewer cards, dark mode, and
print-friendly layout. For details on producing and customising the HTML
output, see `references/html-output.md`.

The report contains:
1. The synthesized improvement roadmap (the main deliverable)
2. Full individual reviews from each agent (collapsible appendix)
3. Panel discussion notes (appendix)

Present the `.html` report using `present_files`, then walk the user
through the executive summary and top priorities conversationally.

## Important Reminders

- **This is for improvement, not judgment.** Never frame the output as
  accept/reject. Frame everything as "here's how to make it stronger."
- **Every criticism needs a suggestion.** No reviewer should raise a
  problem without suggesting a solution or workaround.
- **Be specific.** "The writing needs improvement" is useless. "The third
  paragraph of the introduction buries the key motivation — lead with the
  clinical need instead" is actionable.
- **Respect the authors' expertise.** They know their research better than
  any AI. Frame suggestions as options, not mandates. Use language like
  "consider," "the panel suggests," "one approach would be."
- **Use web search actively.** The trend expert and devil's advocate
  personas should always search for recent literature. Outdated novelty
  assessments are worse than none.
- **Preserve what works.** Explicitly call out strengths. Authors need to
  know what NOT to change during revision.

## Error Handling

- If PDF extraction produces garbled text, try pdfplumber, pymupdf, or
  rasterize-and-OCR.
- If you can't complete a persona (context too long, etc.), skip it and
  note the gap. The synthesis can work with incomplete reviews.
- If the manuscript is very long (>50 pages), consider reviewing sections
  separately or truncating supplementary material.
