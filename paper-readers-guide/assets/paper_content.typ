// ============================================================
// Paper Reader's Guide — paper-specific content
//
// This is the ONLY file you need to edit per paper.  Fill the `#let`
// blocks below, then compile THIS file (not template.typ) to get the
// PDF.  The rendering engine lives in template.typ — you do not need
// to read or modify it.
//
// Copy BOTH this file AND template.typ to your working directory.
// ============================================================

#import "./template.typ": render_guide

#let lang = "en"  // "en" or "ko"

// Absolute (or working-dir-relative) path to the skill's assets/ folder.
// Must point at the folder containing img-*.jpeg and the SeedKRex fonts.
#let asset_dir = "."

#let paper = (
  title: "Paper Title Goes Here",
  authors: "Authors, et al.",
  venue: "Venue / Journal",
  year: "Year",
  tldr: "A 2-3 sentence teaser that makes the reader want to dig in, without spoiling the main result.",
)

// Reading roadmap — a short guided path through the paper, in the chosen
// language.  Typst markup is active here (`_italic_`, `*bold*`).
#let roadmap = [
  Start with the _abstract_ and the first two paragraphs of the _introduction_
  to lock in the motivation.  Then flip forward to _Figure 1_ and read its
  caption slowly — it usually frames the whole story.  Skim _methods_ once,
  come back to it after you understand the results.  Read _results_ in the
  order the figures appear, pausing at each figure before reading the
  paragraph that describes it.  Read the _discussion_ carefully — the
  authors' honest framing lives there.
]

// ============================================================
// The twenty quest questions — 8 / 8 / 4 across three levels.
//
// Level 1 — Multiple choice.  `text` + exactly five `options`.
// Level 2 — Short answer.  `text` only; two ruled lines are drawn.
// Level 3 — Open reflection.  `text` only; four lines are drawn.
//
// Every question can optionally include a `hint` string.
// ============================================================

#let level1 = (
  name: "Level 1 — Scout the Terrain",
  intro: "Eight multiple-choice quests that pull you across the paper — pick the option the paper actually supports.",
  questions: (
    (text: "Placeholder Level-1 question 1?",
     options: ("Option A", "Option B", "Option C", "Option D", "Option E"),
     hint: none),
    (text: "Placeholder Level-1 question 2?",
     options: ("Option A", "Option B", "Option C", "Option D", "Option E"),
     hint: none),
    (text: "Placeholder Level-1 question 3?",
     options: ("Option A", "Option B", "Option C", "Option D", "Option E"),
     hint: none),
    (text: "Placeholder Level-1 question 4?",
     options: ("Option A", "Option B", "Option C", "Option D", "Option E"),
     hint: none),
    (text: "Placeholder Level-1 question 5?",
     options: ("Option A", "Option B", "Option C", "Option D", "Option E"),
     hint: none),
    (text: "Placeholder Level-1 question 6?",
     options: ("Option A", "Option B", "Option C", "Option D", "Option E"),
     hint: none),
    (text: "Placeholder Level-1 question 7?",
     options: ("Option A", "Option B", "Option C", "Option D", "Option E"),
     hint: none),
    (text: "Placeholder Level-1 question 8?",
     options: ("Option A", "Option B", "Option C", "Option D", "Option E"),
     hint: none),
  ),
)

#let level2 = (
  name: "Level 2 — Decode the Map",
  intro: "Eight short-answer quests — a few words or a single sentence is plenty.",
  questions: (
    (text: "Placeholder Level-2 question 9?", hint: none),
    (text: "Placeholder Level-2 question 10?", hint: none),
    (text: "Placeholder Level-2 question 11?", hint: none),
    (text: "Placeholder Level-2 question 12?", hint: none),
    (text: "Placeholder Level-2 question 13?", hint: none),
    (text: "Placeholder Level-2 question 14?", hint: none),
    (text: "Placeholder Level-2 question 15?", hint: none),
    (text: "Placeholder Level-2 question 16?", hint: none),
  ),
)

#let level3 = (
  name: "Level 3 — Face the Dragon",
  intro: "Four open-ended provocations — hidden assumptions, missing controls, tensions with the wider field.",
  questions: (
    (text: "Placeholder Level-3 question 17?", hint: none),
    (text: "Placeholder Level-3 question 18?", hint: none),
    (text: "Placeholder Level-3 question 19?", hint: none),
    (text: "Placeholder Level-3 question 20?", hint: none),
  ),
)

#let closing = [
  Found something surprising, delightful, or infuriating?  Share it with
  whoever sent you this paper — half the value of reading closely is the
  conversation that follows.
]

// ============================================================
// Paper-anatomy graph — describes the paper's actual logical structure
// as a directed graph that renders under the reading roadmap.
//
// Node `kind` must be one of:
//   "motivation", "assumptions", "logical_flow", "experiments",
//   "supporting", "evidence", "interpretations", "implications",
//   "conclusions"
// Multiple nodes of the same kind are allowed — e.g. parallel experiment
// tracks each feeding their own evidence.
//
// `label` is the paper-specific body text (≤ ~12 words; Typst markup ok).
// `pos` is (x, y) in grid units — real numbers allowed; x grows right,
// y grows down.  The graph should visually mirror the argument's shape.
//
// Edges are `(from_key, to_key)` or `(from_key, to_key, "dashed")`.
// ============================================================

#let paper_anatomy_nodes = (
  motiv:   (kind: "motivation",     pos: (2, 0),   label: "One-line open question the paper tackles."),
  assum:   (kind: "assumptions",    pos: (0, 1.2), label: "Key assumption(s) the argument rests on."),
  flow:    (kind: "logical_flow",   pos: (4, 1.2), label: "The paper's top-level chain of reasoning."),
  exp:     (kind: "experiments",    pos: (2, 2.4), label: "Main experiments · separated · by · dots."),
  evid:    (kind: "evidence",       pos: (2, 3.4), label: "Top observations that carry the paper."),
  supp:    (kind: "supporting",     pos: (2, 4.4), label: "Critical controls/rescues tying evidence to claim."),
  interp:  (kind: "interpretations",pos: (2, 5.4), label: "Authors' reading of what the data mean."),
  impl:    (kind: "implications",   pos: (0, 6.6), label: "What this implies for the wider field."),
  concl:   (kind: "conclusions",    pos: (4, 6.6), label: "The bottom-line claim."),
)

#let paper_anatomy_edges = (
  ("motiv", "assum", "dashed"),
  ("motiv", "flow",  "dashed"),
  ("assum", "exp"),
  ("flow",  "interp", "dashed"),
  ("exp",   "evid"),
  ("evid",  "supp"),
  ("supp",  "interp"),
  ("interp","impl"),
  ("interp","concl"),
)

// ============================================================
// Hand off to the rendering engine.  Do NOT edit template.typ.
// ============================================================

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
