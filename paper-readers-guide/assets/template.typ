// ============================================================
// Paper Reader's Guide — Typst Template
// Fill in the #let blocks below; layout and styling are handled
// further down.
// ============================================================

#let lang = "en"  // "en" or "ko"

#let accent = rgb("#8B4513")  // a calm warm brown by default

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
// Localized UI strings
// ============================================================

#let ui = if lang == "ko" {
  (
    cover_kicker: "논문 읽기 가이드",
    roadmap_title: "읽기 경로",
    how_to_use_title: "이 가이드 사용법",
    how_to_use: [
      각 질문은 논문의 특정 부분을 향한 안내입니다.  Level 1은 5지선다형,
      Level 2는 한 문장짜리 짧은 답, Level 3은 깊이 생각해 볼 열린 질문이에요.
      정답을 평가하려는 것이 아니라, 논문을 끝까지 읽도록 끌고 가기 위한
      quest입니다.  순서대로 풀어도 좋고, 마음에 드는 것부터 골라 풀어도 좋습니다.
    ],
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

#let level1_block(level, start_num) = {
  heading(level: 1, level.name)
  text(fill: luma(45%), style: "italic", level.intro)
  v(0.4em)
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
  heading(level: 1, level.name)
  text(fill: luma(45%), style: "italic", level.intro)
  v(0.4em)
  for (i, q) in level.questions.enumerate() {
    quest_short(
      start_num + i,
      eval(q.text, mode: "markup"),
      hint: if q.at("hint", default: none) == none { none } else { q.hint },
    )
  }
}

#let level3_block(level, start_num) = {
  heading(level: 1, level.name)
  text(fill: luma(45%), style: "italic", level.intro)
  v(0.4em)
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

#align(center)[
  #text(size: 10pt, fill: accent, weight: "bold", tracking: 1.5pt, upper(ui.cover_kicker))
  #v(0.6em)
  #text(size: 22pt, weight: "bold", paper.title)
  #v(0.4em)
  #text(size: 11pt, fill: luma(40%))[
    #paper.authors · #paper.venue · #paper.year
  ]
]

#v(1.2em)
#block(
  fill: luma(96%),
  inset: 14pt,
  radius: 4pt,
  stroke: 0.4pt + luma(80%),
  {
    set par(leading: 0.7em)
    set text(size: 11pt)
    paper.tldr
  },
)

#v(1.2em)

// How to use
#heading(level: 2, ui.how_to_use_title)
#ui.how_to_use

// Roadmap
#heading(level: 2, ui.roadmap_title)
#roadmap

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
#closing
