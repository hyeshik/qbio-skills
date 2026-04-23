// ============================================================
// Paper Reader's Guide — rendering engine (DO NOT EDIT per paper)
//
// Exposes a single function `render_guide(...)` that takes the
// paper-specific content as keyword arguments and produces the
// full typeset document.  Called from `paper_content.typ`.
// ============================================================

#import "@preview/fletcher:0.5.3" as fletcher: diagram, node, edge

#let accent = rgb("#8B4513")  // warm brown accent

#let render_guide(
  lang: "en",
  asset_dir: ".",
  paper: (title: "", authors: "", venue: "", year: "", tldr: ""),
  roadmap: [],
  level1: (name: "", intro: "", questions: ()),
  level2: (name: "", intro: "", questions: ()),
  level3: (name: "", intro: "", questions: ()),
  closing: [],
  paper_anatomy_nodes: (:),
  paper_anatomy_edges: (),
) = {

  // -----------------------------------------------------------
  // Localized UI strings
  // -----------------------------------------------------------
  let ui = if lang == "ko" {
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
        Each question is a pointer into a specific part of the paper.  Level 1
        is multiple choice (one of five), Level 2 asks for a one-sentence
        answer, Level 3 is open-ended reflection.  This is not a test — it's a
        quest sheet designed to pull you through the paper end to end.  Work
        them in order, or pick the ones that catch your eye.
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

  // -----------------------------------------------------------
  // Page and typography setup
  // -----------------------------------------------------------
  let body_font = if lang == "ko" { ("SeedKRex", "Lato") } else { ("EB Garamond", "Lato") }

  set document(title: paper.title)
  set page(
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
  set text(font: body_font, size: 11pt, lang: if lang == "ko" { "ko" } else { "en" })
  set par(leading: 0.75em, justify: true)

  show heading.where(level: 1): it => {
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

  show heading.where(level: 2): it => {
    set text(size: 13pt, weight: "semibold")
    block(above: 1.4em, below: 0.6em, it.body)
  }

  // -----------------------------------------------------------
  // Paper-anatomy diagram helpers
  // -----------------------------------------------------------
  let _kind_fill(kind) = {
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

  let _anatomy_node_dyn(spec) = {
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

  // Build the raw diagram content; the caller wraps it in a width-fit box.
  let _anatomy_diagram_raw = {
    let nodes = paper_anatomy_nodes
    let edges = paper_anatomy_edges

    let node_args = nodes.values().map(_anatomy_node_dyn)
    let edge_args = edges.map(e => {
      let from_pos = nodes.at(e.at(0)).pos
      let to_pos   = nodes.at(e.at(1)).pos
      let style    = if e.len() > 2 { e.at(2) } else { "solid" }
      if style == "dashed" {
        edge(from_pos, to_pos, "->", stroke: (paint: accent.lighten(30%), thickness: 0.5pt, dash: "dashed"))
      } else {
        edge(from_pos, to_pos, "->", stroke: 0.6pt + accent.lighten(20%))
      }
    })

    diagram(
      spacing: (1.0em, 2.0em),
      node-outset: 2pt,
      ..node_args,
      ..edge_args,
    )
  }

  // Render the diagram scaled to fit the text column width.  The diagram is
  // ALWAYS fit within the available text column: we measure its natural width
  // and proportionally scale down when needed, leaving a small safety margin
  // (0.96) so fletcher's em-based internal layout can't push past the page
  // edge during final rendering.  Never upscale — at most 1.0.
  let paper_anatomy_diagram() = layout(container => {
    let available = container.width
    let natural = measure(_anatomy_diagram_raw).width
    let safety = 0.96
    let factor = calc.min(1.0, (available * safety) / natural)
    align(center, block(width: available, align(center, scale(
      factor * 100%,
      origin: top + center,
      reflow: true,
      _anatomy_diagram_raw,
    ))))
  })

  // -----------------------------------------------------------
  // Scene-illustration helper
  // -----------------------------------------------------------
  let scene(name, width: 100%, height: none) = {
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

  // -----------------------------------------------------------
  // Quest box components
  // -----------------------------------------------------------
  let _badge(num) = box(
    fill: accent,
    inset: (x: 6pt, y: 3pt),
    radius: 3pt,
    text(fill: white, weight: "bold", size: 9pt)[#num],
  )

  let _hint_line(hint) = {
    if hint != none {
      text(style: "italic", fill: luma(45%), size: 10pt, eval(hint, mode: "markup"))
    }
  }

  let quest_mc(num, text_body, options, hint: none) = {
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

  let quest_short(num, text_body, hint: none) = {
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
          line(length: 100%, stroke: 0.4pt + luma(60%))
          v(1.1em)
          line(length: 100%, stroke: 0.4pt + luma(60%))
        },
      ),
    )
  }

  let quest_open(num, text_body, hint: none) = {
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
          for _ in range(4) {
            line(length: 100%, stroke: 0.4pt + luma(65%))
            v(1.1em)
          }
        },
      ),
    )
  }

  let _level_opener(img_name, name, intro) = block(breakable: false, {
    scene(img_name)
    v(20pt)
    heading(level: 1, name)
    text(fill: luma(45%), style: "italic", intro)
    v(0.4em)
  })

  let level1_block(level, start_num) = {
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

  let level2_block(level, start_num) = {
    _level_opener("img-level2.jpeg", level.name, level.intro)
    for (i, q) in level.questions.enumerate() {
      quest_short(
        start_num + i,
        eval(q.text, mode: "markup"),
        hint: if q.at("hint", default: none) == none { none } else { q.hint },
      )
    }
  }

  let level3_block(level, start_num) = {
    _level_opener("img-level3.jpeg", level.name, level.intro)
    for (i, q) in level.questions.enumerate() {
      quest_open(
        start_num + i,
        eval(q.text, mode: "markup"),
        hint: if q.at("hint", default: none) == none { none } else { q.hint },
      )
    }
  }

  // -----------------------------------------------------------
  // Cover block
  // -----------------------------------------------------------
  align(center, block(width: 100%, {
    set par(justify: false, leading: 0.5em)
    text(size: 10pt, fill: accent, weight: "bold", tracking: 1.5pt, upper(ui.cover_kicker))
    v(0.6em)
    text(size: 22pt, weight: "bold", paper.title)
    v(0.4em)
    text(size: 11pt, fill: luma(40%))[
      #paper.authors · #paper.venue · #paper.year
    ]
  }))

  v(0.8em)
  scene("img-cover.jpeg")
  v(0.6em)

  block(
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

  v(1.0em)

  heading(level: 2, ui.how_to_use_title)
  ui.how_to_use

  heading(level: 2, ui.roadmap_title)
  scene("img-roadmap.jpeg")
  v(0.8em)
  roadmap

  v(0.8em)

  heading(level: 2, ui.anatomy_title)
  paper_anatomy_diagram()

  v(0.8em)

  // -----------------------------------------------------------
  // Quest levels
  // -----------------------------------------------------------
  pagebreak()
  level1_block(level1, 1)

  pagebreak()
  level2_block(level2, 1 + level1.questions.len())

  pagebreak()
  level3_block(level3, 1 + level1.questions.len() + level2.questions.len())

  // -----------------------------------------------------------
  // Closing
  // -----------------------------------------------------------
  v(1.5em)
  heading(level: 2, ui.closing_title)
  scene("img-finished.jpeg")
  v(0.8em)
  closing
}
