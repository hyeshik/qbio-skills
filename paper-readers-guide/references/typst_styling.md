# Typst Styling Notes

The template (`assets/template.typ`) is designed to be "fill in the blanks" — you mostly edit text and a few `#let` variables at the top. This file covers how to tweak it if the user asks for customization.

## Structure of `template.typ`

```
#let lang = "en"         // "en" or "ko" — switches headings and typography
#let accent = rgb(...)   // single accent color used throughout
#let paper = (           // paper metadata block
  title: "...",
  authors: "...",
  venue: "...",
  year: "...",
  tldr: "...",
)
#let roadmap = [...]     // reading roadmap (a Typst content block)
#let level1 = (name: "...", intro: "...", questions: (...))
#let level2 = ...
#let level3 = ...
#let closing = [...]
```

The rest of the file is page setup and layout — you rarely need to touch it.

## Per-question structure

Each level has its own question dictionary shape:

```typst
// Level 1 — multiple choice
(text: "Question?", options: ("a", "b", "c", "d", "e"), hint: none)

// Level 2 — short answer
(text: "Question?", hint: none)

// Level 3 — open reflection
(text: "Question?", hint: none)
```

`hint` can be `none` or a short pointer shown in muted italics below the question. Use it sparingly.

## Typst markup in strings

Use Typst syntax, not Markdown:

- `_word_` → _italic_
- `*word*` → *bold*
- Never `**word**` — Typst will render the asterisks literally.

This applies to `text`, `options`, `hint`, `roadmap`, `tldr`, and `closing`.

## Changing the accent color

Set `#let accent = rgb("#...")` at the top. The template uses this color for:
- Level heading underlines
- Quest number badges
- Small ornamental flourishes

Good defaults: warm browns (`#8B4513`), deep indigo (`#3B3B7A`), dark teal (`#1F6F6F`). Avoid bright saturated colors — the document should feel like a library.

## Changing fonts

Body font is set via the `#let body_font = ...` block near the top. Defaults:

- English: `("EB Garamond", "Lato")` with a serif preference
- Korean: `("SeedKRex", "Lato")` — SeedKRex is bundled in `assets/` with Regular, Regular Italic, Bold, and Bold Italic so `_italic_` and `*bold*` render correctly on Hangul as well as Latin glyphs.

If the user wants a different Korean typeface, make sure the chosen family ships at least Regular + Italic, otherwise Typst's `_italic_` markup will silently fall back to upright. Drop the font files into `assets/` and update the font stack — the compile script already points Typst at `assets/`.

## Page layout

The template uses A4 with moderate margins (2.5 cm). For longer guides (if the user asks for more questions), you may want to reduce to 2 cm. For a printed handout feel, 2.5–3 cm margins read better.

## Quest box components

There are three components, one per level:

- `quest_mc(num, text_body, options, hint)` — Level 1. Renders the question followed by five labeled options, each with a circle (U+25EF) the reader can fill in.
- `quest_short(num, text_body, hint)` — Level 2. Renders the question followed by two ruled lines for a one-sentence answer.
- `quest_open(num, text_body, hint)` — Level 3. Renders the question followed by four ruled lines for an open-ended reflection.

The circled number badge on the left and the bordered box are common across all three. The numeric question index is auto-computed from the level's position so the 20 questions are numbered 1–20 end-to-end.

## Page breaks

The template places Level 2 on a fresh page and Level 3 on a fresh page. If the user wants it all on continuous pages, remove the `pagebreak()` calls between levels.

## Compiling

Always use the bundled compile script:

```
python scripts/compile_guide.py <input.typ> <output.pdf>
```

It passes `--font-path assets/` so the bundled Korean font is picked up.
