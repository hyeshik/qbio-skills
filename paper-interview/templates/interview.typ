// Paper Interview — Journal-Style Typst Template (Two-Column)
// Inspired by Nature/Science two-column review layout
//
// Usage: typst compile interview.typ interview.pdf
// Parameters injected by the build script: PARAM_TITLE, PARAM_AUTHORS,
// PARAM_JOURNAL, PARAM_DOI, PARAM_AUTHOR_NAME, PARAM_LANG, PARAM_FONT

// ─── Page & Font Setup ───────────────────────────────────────────────────────

#set page(
  paper: "a4",
  margin: (top: 2.2cm, bottom: 2.2cm, left: 1.6cm, right: 1.6cm),
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 7.5pt, fill: rgb("#888888"))
      #smallcaps[Paper Interview]
      #h(1fr)
      #counter(page).display()
    ]
  },
  footer: context {
    if counter(page).get().first() == 1 [
      #set text(size: 7pt, fill: rgb("#999999"))
      PARAM_FOOTER_TEXT
      #h(1fr)
      #counter(page).display()
    ]
  },
)

#set text(
  font: (PARAM_FONT),
  size: 9pt,
  lang: "PARAM_LANG",
)

#set par(
  justify: true,
  leading: PARAM_LEADING,
  first-line-indent: 0em,
)

// ─── Heading Styles ──────────────────────────────────────────────────────────

#show heading.where(level: 1): it => {
  set text(size: 20pt, weight: "bold", fill: rgb("#1a1a2e"))
  set block(above: 0em, below: 0.6em)
  it
}

#show heading.where(level: 2): it => {
  set text(size: 10pt, weight: "bold", fill: rgb("#c0392b"))
  set block(above: 1.4em, below: 0.4em)
  upper(it)
}

// ─── Blockquote Styling ──────────────────────────────────────────────────────

#show quote: it => {
  set text(size: 8pt)
  block(
    width: 100%,
    inset: (left: 10pt, right: 10pt, top: 6pt, bottom: 6pt),
    fill: rgb("#f8f9fa"),
    stroke: (left: 2.5pt + rgb("#c0392b")),
    radius: 2pt,
    it.body,
  )
}

// ─── Data Parameters (injected by the build script) ──────────────────────────

#let article-title = "PARAM_TITLE"
#let article-authors = "PARAM_AUTHORS"
#let article-journal = "PARAM_JOURNAL"
#let article-doi = "PARAM_DOI"
#let author-name = "PARAM_AUTHOR_NAME"

// ─── Title Block (full width, above columns) ─────────────────────────────────

#v(0.8cm)

// Accent bar
#block(width: 100%, height: 3.5pt, fill: rgb("#c0392b"))

#v(0.3cm)

#block(width: 100%)[
  #set text(size: 8.5pt, fill: rgb("#c0392b"), weight: "bold")
  #smallcaps[PARAM_SECTION_LABEL]
]

#v(0.15cm)

#block(width: 100%)[
  #set text(size: 18pt, weight: "bold", fill: rgb("#1a1a2e"))
  #article-title
]

#v(0.25cm)

// Metadata box
#block(
  width: 100%,
  inset: (x: 12pt, y: 8pt),
  fill: rgb("#f8f9fa"),
  radius: 3pt,
  stroke: 0.5pt + rgb("#dddddd"),
)[
  #set text(size: 7.5pt, fill: rgb("#444444"))
  *PARAM_LABEL_PAPER*: #article-authors

  *PARAM_LABEL_PUBLISHED*: #article-journal

  *DOI*: #link("https://doi.org/" + article-doi)[#article-doi]
]

#v(0.2cm)

// Thin rule
#line(length: 100%, stroke: 0.5pt + rgb("#cccccc"))

#v(0.3cm)

// ─── Interview Body — Two-Column Layout ──────────────────────────────────────

#columns(2, gutter: 18pt)[

// INTERVIEW_CONTENT_START
// This marker is replaced by the build script with the full Typst-formatted
// interview content.
// INTERVIEW_CONTENT_END

]

// ─── Closing ─────────────────────────────────────────────────────────────────

#v(0.8em)
#line(length: 100%, stroke: 0.5pt + rgb("#cccccc"))
#v(0.3em)

#block(width: 100%)[
  #set text(size: 7pt, fill: rgb("#888888"), style: "italic")
  PARAM_CLOSING_NOTE
]
