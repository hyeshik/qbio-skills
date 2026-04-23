// ============================================================
// Paper Reader's Guide — Typst Template
// Fill in the #let blocks below; layout and styling are handled
// further down.
// ============================================================

#import "@preview/fletcher:0.5.3" as fletcher: diagram, node, edge

#let lang = "en"  // "en" or "ko"

#let accent = rgb("#8B4513")  // a calm warm brown by default

// Path to the folder holding the img-*.jpeg scene illustrations.  These ship
// in the skill's ``assets/`` directory.  When copying this template outside
// the skill, set ``asset_dir`` to the absolute path of that folder (or to a
// relative path that resolves from this .typ file's location).
#let asset_dir = "."

#let paper = (
  title: "Paper Title Goes Here",
  authors: "Authors, et al.",
  venue: "Venue / Journal",
  year: "Year",
  tldr: "A 2-3 sentence teaser that makes the reader want to dig in, without spoiling the main result.",
)

// The reading roadmap — a short guided path.  Write in the chosen language.
#let roadmap = [
  Start with the _abstract_ and the first two paragraphs of the _introduction_ to
  lock in the motivation.  Then flip forward to _Figure 1_ and read its caption
  slowly — it usually frames the whole story.  Skim _methods_ once, come back to
  it after you understand the results.  Read _results_ in the order the figures
  appear, pausing at each figure before reading the paragraph that describes it.
  Read the _discussion_ carefully — the authors' honest framing lives there.
]

// ============================================================
// The three quest levels
//
// Level 1 — Multiple choice.  Each question has a `text` and exactly 5
//           `options` (strings).  The reader circles the right answer.
//           No answer key is printed — that's part of the quest.
//
// Level 2 — Short answer.  Each question has `text` only.  Two ruled
//           lines are drawn for the reader's one-sentence answer.
//
// Level 3 — Open reflection.  Each question has `text` only.  A larger
//           note box is drawn for the reader's thinking.
//
// Every question can optionally include a `hint` string shown below the
// question in muted italics.
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
  Found something surprising, delightful, or infuriating?  Share it with whoever
  sent you this paper — half the value of reading closely is the conversation
  that follows.
]

// ============================================================
// Paper-specific anatomy graph
//
// Describe the paper's actual logical structure as a directed graph.
// Every node has:
//   - `kind`  — one of "motivation", "assumptions", "logical_flow",
//               "experiments", "supporting", "evidence",
//               "interpretations", "implications", "conclusions".
//               (Multiple nodes of the same kind are allowed — e.g. a paper
//               may have several parallel experiment tracks, each feeding
//               its own evidence node.)
//   - `label` — short paper-specific text (≤ ~12 words, Typst markup ok).
//   - `pos`   — (x, y) grid coordinate.  x grows right, y grows down.
//               Real numbers are allowed; nothing is forced to a 3×3 grid.
//
// Edges are written as tuples (from_key, to_key) or (from_key, to_key, style),
// where style is "solid" (default) or "dashed".
//
// Both collections can be empty for papers with no anatomy diagram, or can
// grow arbitrarily large for papers whose argument branches across many
// parallel lines of evidence.
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
  ("flow", "interp", "dashed"),
  ("exp", "evid"),
  ("evid", "supp"),
  ("supp", "interp"),
  ("interp", "impl"),
  ("interp", "concl"),
)

// ============================================================
// Localized UI strings
// ============================================================

#let ui = if lang == "ko" {
  (
    cover_kicker: "논문 읽기 가이드",
    roadmap_title: "읽기 경로",
    how_to_use_title: "이 가이드 사용법",
    how_to_use: [
      각 질문은 논문 속 한 지점을 가리키는 이정표입니다. Level 1은 다섯 개의
      보기에서 정답을 고르는 객관식, Level 2는 한 문장으로 답하는 짧은 질문,
      Level 3은 깊이 곱씹어 볼 만한 열린 질문입니다. 정답을 채점하려는
      시험이 아니라, 논문을 처음부터 끝까지 따라가며 읽도록 이끌어 주는
      quest이니, 순서대로 풀어도 좋고 마음 가는 것부터 골라 풀어도 좋습니다.
    ],
    anatomy_title: "논문의 골격",
    anatomy_labels: (
      motivation: "동기",
      assumptions: "핵심 가정",
      logical_flow: "논리 전개",
      experiments: "실험",
      supporting: "뒷받침 논리",
      evidence: "근거",
      interpretations: "해석",
      implications: "함의",
      conclusions: "결론",
    ),
    closing_title: "마치며",
    authors_prefix: "저자",
    venue_prefix: "출처",
  )
} else {
  (
    cover_kicker: "A Reader's Guide",
    roadmap_title: "Reading roadmap",
    how_to_use_title: "How to use this guide",
    how_to_use: [
      Each question is a pointer into a specific part of the paper.  Level 1 is
      multiple choice (one of five), Level 2 asks for a one-sentence answer,
      Level 3 is open-ended reflection.  This is not a test — it's a quest sheet
      designed to pull you through the paper end to end.  Work them in order,
      or pick the ones that catch your eye.
    ],
    anatomy_title: "Anatomy of the paper",
    anatomy_labels: (
      motivation: "Motivation",
      assumptions: "Key Assumptions",
      logical_flow: "Logical Flow",
      experiments: "Experiments",
      supporting: "Logical Supporting",
      evidence: "Evidence",
      interpretations: "Interpretations",
      implications: "Implications",
      conclusions: "Conclusions",
    ),
    closing_title: "Closing",
    authors_prefix: "Authors",
    venue_prefix: "Venue",
  )
}

// ============================================================
// Page and typography setup
// ============================================================

#let body_font = if lang == "ko" {
  // SeedKRex is bundled in assets/ and is the Korean default.  It ships
  // Regular / Regular Italic / Bold / Bold Italic so _italic_ and *bold* in
  // Typst markup render correctly on both Hangul and Latin glyphs.
  ("SeedKRex", "Lato")
} else {
  ("EB Garamond", "Lato")
}

#set document(title: paper.title)
#set page(
  paper: "a4",
  margin: (x: 2.5cm, y: 2.5cm),
  footer: context {
    set text(size: 8pt, fill: luma(50%))
    grid(
      columns: (1fr, 1fr),
      align: (left, right),
      paper.title,
      [#counter(page).display()],
    )
  },
)
#set text(font: body_font, size: 11pt, lang: if lang == "ko" { "ko" } else { "en" })
#set par(leading: 0.75em, justify: true)

#show heading.where(level: 1): it => {
  set text(size: 20pt, weight: "bold")
  block(
    below: 0.8em,
    above: 0em,
    stack(
      dir: ttb,
      spacing: 0.35em,
      it.body,
      line(length: 2.2em, stroke: 1.5pt + accent),
    ),
  )
}

#show heading.where(level: 2): it => {
  set text(size: 13pt, weight: "semibold")
  block(above: 1.4em, below: 0.6em, it.body)
}

// ============================================================
// Paper-anatomy diagram — a 3×3 Fletcher diagram that sits under the
// reading roadmap.  Three columns group the paper's elements:
//   Framing   → Motivation     · Key Assumptions  · Logical Flow
//   Argument  → Experiments    · Logical Support. · Evidence
//   Takeaway  → Interpretations· Implications     · Conclusions
// Vertical arrows carry each framing element into its argument element
// and then down to its takeaway; horizontal edges show co-dependence
// (dashed at the top, flow arrows at the bottom).  Roughly 4:3.
// ============================================================

// Subtle per-kind fill tints keep all nodes in the same warm palette while
// letting the reader's eye group together nodes of the same role.
#let _kind_fill(kind) = {
  let k = kind
  if k == "motivation"            { accent.lighten(78%) }
  else if k == "logical_flow"     { accent.lighten(82%) }
  else if k == "assumptions"      { accent.lighten(86%) }
  else if k == "experiments"      { accent.lighten(93%) }
  else if k == "evidence"         { accent.lighten(90%) }
  else if k == "supporting"       { accent.lighten(84%) }
  else if k == "interpretations"  { accent.lighten(80%) }
  else if k == "implications"     { accent.lighten(84%) }
  else if k == "conclusions"      { accent.lighten(70%) }
  else                            { accent.lighten(90%) }
}

// Render a single node given its spec (dict with `kind`, `label`, `pos`).
// Header line: uppercase role tag from `ui.anatomy_labels`.
// Body line:   paper-specific text from `label`, evaluated as Typst markup
// so that _italics_ and *bold* work inside node content.
#let _anatomy_node_dyn(spec) = {
  let header = ui.anatomy_labels.at(spec.kind)
  node(
    spec.pos,
    box(width: 7em, {
      set par(justify: false, leading: 0.42em)
      align(center, text(size: 6.5pt, weight: "bold", tracking: 0.8pt, fill: accent,
        hyphenate: false, upper(eval(header, mode: "markup"))))
      v(0.25em)
      align(center, text(size: 7pt, eval(spec.label, mode: "markup")))
    }),
    inset: 4.5pt,
    stroke: 0.6pt + accent.lighten(20%),
    fill: _kind_fill(spec.kind),
    corner-radius: 3.5pt,
    shape: rect,
  )
}

// Build the diagram from `paper_anatomy_nodes` and `paper_anatomy_edges`.
// The structure — which nodes exist, how they connect — is paper-specific.
#let paper_anatomy_diagram() = {
  let nodes = paper_anatomy_nodes
  let edges = paper_anatomy_edges

  let node_args  = nodes.values().map(_anatomy_node_dyn)
  let edge_args  = edges.map(e => {
    let from_pos = nodes.at(e.at(0)).pos
    let to_pos   = nodes.at(e.at(1)).pos
    let style    = if e.len() > 2 { e.at(2) } else { "solid" }
    if style == "dashed" {
      edge(from_pos, to_pos, "->", stroke: (paint: accent.lighten(30%), thickness: 0.5pt, dash: "dashed"))
    } else {
      edge(from_pos, to_pos, "->", stroke: 0.6pt + accent.lighten(20%))
    }
  })

  align(center, diagram(
    spacing: (1.0em, 2.0em),
    node-outset: 2pt,
    ..node_args,
    ..edge_args,
  ))
}

// ============================================================
// Scene-illustration helper
//
// Renders a landscape scene image with a thin warm frame and light top/bottom
// breathing space — enough to sit inside the flow of typography without
// reading as a standalone plate.  Used by the cover banner, each level
// opener, the roadmap inset, and the closing.
// ============================================================

#let scene(name, width: 100%, height: none) = {
  let img = if height == none {
    image(asset_dir + "/" + name, width: width)
  } else {
    image(asset_dir + "/" + name, height: height)
  }
  box(
    stroke: 0.4pt + accent.lighten(55%),
    clip: true,
    radius: 6pt,
    img,
  )
}

// ============================================================
// Quest box components — one per level
// ============================================================

#let _badge(num) = box(
  fill: accent,
  inset: (x: 6pt, y: 3pt),
  radius: 3pt,
  text(fill: white, weight: "bold", size: 9pt)[#num],
)

#let _hint_line(hint) = {
  if hint != none {
    text(style: "italic", fill: luma(45%), size: 10pt, eval(hint, mode: "markup"))
  }
}

// Level 1: multiple-choice, 5 options
#let quest_mc(num, text_body, options, hint: none) = {
  let letters = ("a", "b", "c", "d", "e")
  block(
    above: 0.8em,
    below: 0.8em,
    stroke: (left: 1.5pt + accent, rest: 0.4pt + luma(70%)),
    inset: (x: 10pt, y: 9pt),
    radius: (right: 3pt),
    grid(
      columns: (auto, 1fr),
      column-gutter: 10pt,
      _badge(num),
      {
        set par(leading: 0.65em)
        text_body
        if hint != none {
          parbreak()
          _hint_line(hint)
        }
        v(0.35em)
        for (i, opt) in options.enumerate() {
          let letter = letters.at(i)
          grid(
            columns: (1.2em, auto, 1fr),
            column-gutter: 5pt,
            row-gutter: 0.15em,
            text(size: 13pt, fill: accent)[◯],
            text(weight: "bold", size: 10pt)[(#letter)],
            text(size: 10.5pt, eval(opt, mode: "markup")),
          )
        }
      },
    ),
  )
}

// Level 2: short-answer, two ruled lines
#let quest_short(num, text_body, hint: none) = {
  block(
    above: 0.8em,
    below: 0.8em,
    stroke: (left: 1.5pt + accent, rest: 0.4pt + luma(70%)),
    inset: (x: 10pt, y: 9pt),
    radius: (right: 3pt),
    grid(
      columns: (auto, 1fr),
      column-gutter: 10pt,
      _badge(num),
      {
        set par(leading: 0.65em)
        text_body
        if hint != none {
          parbreak()
          _hint_line(hint)
        }
        v(0.4em)
        // two ruled answer lines
        line(length: 100%, stroke: 0.4pt + luma(60%))
        v(1.1em)
        line(length: 100%, stroke: 0.4pt + luma(60%))
      },
    ),
  )
}

// Level 3: open reflection, larger note box
#let quest_open(num, text_body, hint: none) = {
  block(
    above: 0.8em,
    below: 0.8em,
    stroke: (left: 1.5pt + accent, rest: 0.4pt + luma(70%)),
    inset: (x: 10pt, y: 9pt),
    radius: (right: 3pt),
    grid(
      columns: (auto, 1fr),
      column-gutter: 10pt,
      _badge(num),
      {
        set par(leading: 0.65em)
        text_body
        if hint != none {
          parbreak()
          _hint_line(hint)
        }
        v(0.4em)
        // four ruled reflection lines
        for _ in range(4) {
          line(length: 100%, stroke: 0.4pt + luma(65%))
          v(1.1em)
        }
      },
    ),
  )
}

// Section opener: image banner, heading sitting tight below it, italic intro.
// Kept as a non-breaking unit so the illustration never separates from its
// heading across a page break.
#let _level_opener(img_name, name, intro) = block(breakable: false, {
  scene(img_name)
  v(20pt)
  heading(level: 1, name)
  text(fill: luma(45%), style: "italic", intro)
  v(0.4em)
})

#let level1_block(level, start_num) = {
  _level_opener("img-level1.jpeg", level.name, level.intro)
  for (i, q) in level.questions.enumerate() {
    quest_mc(
      start_num + i,
      eval(q.text, mode: "markup"),
      q.options,
      hint: if q.at("hint", default: none) == none { none } else { q.hint },
    )
  }
}

#let level2_block(level, start_num) = {
  _level_opener("img-level2.jpeg", level.name, level.intro)
  for (i, q) in level.questions.enumerate() {
    quest_short(
      start_num + i,
      eval(q.text, mode: "markup"),
      hint: if q.at("hint", default: none) == none { none } else { q.hint },
    )
  }
}

#let level3_block(level, start_num) = {
  _level_opener("img-level3.jpeg", level.name, level.intro)
  for (i, q) in level.questions.enumerate() {
    quest_open(
      start_num + i,
      eval(q.text, mode: "markup"),
      hint: if q.at("hint", default: none) == none { none } else { q.hint },
    )
  }
}

// ============================================================
// Cover block
// ============================================================

#align(center, block(width: 100%, {
  set par(justify: false, leading: 0.5em)
  text(size: 10pt, fill: accent, weight: "bold", tracking: 1.5pt, upper(ui.cover_kicker))
  v(0.6em)
  text(size: 22pt, weight: "bold", paper.title)
  v(0.4em)
  text(size: 11pt, fill: luma(40%))[
    #paper.authors · #paper.venue · #paper.year
  ]
}))

#v(0.8em)

// Cover banner: the party at the mouth of the paper-grotto.  Sized to slot
// between the title block and the TL;DR without any separator — it reads as
// part of the masthead rather than a plated illustration.
#scene("img-cover.jpeg")

#v(0.6em)

#block(
  fill: luma(96%),
  inset: 14pt,
  radius: 4pt,
  stroke: 0.4pt + luma(80%),
  {
    set par(leading: 0.7em)
    set text(size: 11pt)
    eval(paper.tldr, mode: "markup")
  },
)

#v(1.0em)

// How to use
#heading(level: 2, ui.how_to_use_title)
#ui.how_to_use

// Roadmap — text on the left, the map-cabin scene on the right as a running
// marginal illustration.  The two columns share a top edge with the heading
// so the image sits inside the paragraph rather than alongside it.
#heading(level: 2, ui.roadmap_title)
#scene("img-roadmap.jpeg")
#v(0.8em)
#roadmap

#v(0.8em)

// Paper-anatomy diagram: shows how the pieces of a paper hang together.
// Sits directly under the roadmap, visually extending the "how to read"
// guidance into a "what's inside" schematic.
#heading(level: 2, ui.anatomy_title)
#paper_anatomy_diagram()

#v(0.8em)

// ============================================================
// Quest levels
// ============================================================

#pagebreak()
#level1_block(level1, 1)

#pagebreak()
#level2_block(level2, 1 + level1.questions.len())

#pagebreak()
#level3_block(level3, 1 + level1.questions.len() + level2.questions.len())

// ============================================================
// Closing
// ============================================================

#v(1.5em)
#heading(level: 2, ui.closing_title)
#scene("img-finished.jpeg")
#v(0.8em)
#closing
