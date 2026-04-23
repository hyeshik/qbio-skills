# Question Patterns

Worked examples for each of the three question formats. Use these as _patterns_, not templates — always ground the actual wording in the specific paper you're reading.

**Typst italic convention:** in all example text below, `_word_` means italic. Never use `*word*` for italic — Typst renders `*word*` as bold.

## Level 1 — Scout the Terrain (8 multiple-choice questions)

Level 1 exists to pull the reader across the paper. Each question points at a concrete, findable thing, and gives five plausible options — the reader has to actually look at the paper to pick correctly.

### Coverage target across the 8 questions

- 2 from the abstract + introduction
- 1–2 from methods
- 2–3 from results / figures (ideally pointing at different figures)
- 1 from discussion / limitations
- 1 from supplementary, tables, or the bibliography

### Cap numeric retrieval at 2/8 — on purpose

Numbers are the easiest thing to turn into plausible-looking 5-way MC ("five percentages that could appear in the paper" writes itself). Resist the pull. **At least 6 of the 8 Level 1 questions should ask about something other than a number.** The treasure hunt feels repetitive when every quest is "pick the right percentage." Mix in:

- Which **chemical mechanism / physical process** does the paper invoke?
- Which **figure panel** carries the central argument for claim X?
- Which **baseline / control / tool / software / dataset** did the authors choose?
- Which **named state, regime, or condition** does the paper resolve?
- Which **limitation** does the discussion explicitly flag?
- Which **prior reference** does the paper frame itself against?
- Which **sentence / claim / phrase** does a figure support?

When drafting, mark each question with its "target type" (number / mechanism / panel / tool / state / limitation / reference / claim) and count. If numeric is > 2, rewrite a couple of them toward a different target type from the list above.

### Distractor-writing rules

- All five options should read as plausible at first glance. No obvious throwaways.
- Prefer distractors that are actually in the paper but in a different context — another benchmark's number, a baseline's accuracy, a quantity from a different figure, a related citation.
- Mix the correct-answer position across the 8 questions — don't always make it (c).
- Avoid "None of the above" or "All of the above". They break the treasure-hunt feel.
- Keep options short — one line each, roughly parallel in form.

### Good examples

> **Q1.** The abstract makes one headline quantitative claim about the method's advantage over prior work. According to the abstract, that advantage is:
>   (a) 3-fold over the baseline
>   (b) 15-fold over the baseline
>   (c) 47% relative improvement
>   (d) 2 orders of magnitude
>   (e) 0.3 percentage points on F1

_Why it works: all five numbers are plausible, the reader must actually look at the abstract to pick. The correct one is something the paper really says; the others are realistic enough that guessing fails._

> **Q3.** Figure 2 has four panels. Panel C shows a comparison between the proposed method and a baseline. According to the text that describes Panel C, the baseline is:
>   (a) Random initialization
>   (b) _Method Y_ from reference [14]
>   (c) Supervised fine-tuning with no pretraining
>   (d) The naive MAP estimate
>   (e) An in-house implementation of _method Z_

_Why it works: asks for a specific fact (which baseline), distractors are all baselines that realistically could have been used. The reader is pulled to Figure 2's caption and the adjacent prose._

> **Q6.** In the methods, the authors disclose the training batch size. It is:
>   (a) 32
>   (b) 64
>   (c) 256
>   (d) 1024
>   (e) 4096

_Why it works: plain retrieval; all five are common batch sizes. The reader has to find it in methods — exactly the behavior we want._

### Bad examples (avoid)

- ❌ "What is the main result?" — too open; MC doesn't suit it.
- ❌ "Which figure shows the results?" — trivially answerable by flipping through.
- ❌ "What is the method called? (a) BERT (b) Frobnicator (c) 42 (d) a unicorn (e) None of the above." — distractors are not plausible.

## Level 2 — Decode the Map (8 short-answer questions)

Answerable in a few words or one sentence. Each question forces the reader to connect two or more parts of the paper, but the answer is compact.

### Coverage target

- 2 on the logical flow from background/motivation to the central claim
- 2 on why specific methodological choices were the right ones
- 2 on how figures/tables ladder up to the discussion's claims
- 1 on a relationship between parts of the paper that aren't side-by-side
- 1 on how this paper's claim relates to the cited prior work

### Good examples

> **Q10.** In one sentence, why did the authors use _method X_ instead of the more standard _method Y_?

_Why it works: the paper states the reason in §2.3 — one sentence is enough. Asks for synthesis but constrains the answer._

> **Q13.** The discussion claims the approach "generalizes beyond the benchmark." Which two figures carry the strongest version of that argument?

_Why it works: answer is two figure numbers. Forces the reader to cross-reference the discussion against the results._

> **Q16.** In a single sentence, what is the limitation of reference [9] that this paper's design specifically addresses?

_Why it works: answer is one crisp sentence. Ties paper-to-paper comprehension._

> **Q14.** Name the single assumption (stated in §2.1) on which the Figure 3 conclusion depends.

_Why it works: answer is a short phrase. Requires reading §2.1 carefully and connecting it to Figure 3._

### Bad examples (avoid)

- ❌ "Summarize the results in your own words." — too open, and the answer won't fit in one sentence.
- ❌ "Why did the authors do this study?" — the intro literally says so; no stitching.
- ❌ "Describe the method step by step." — needs a paragraph, not a sentence.

## Level 3 — Face the Dragon (4 open-ended reflection questions)

Deep questions. The reader should be able to form an answer, but there's no single right one. Each question gets a larger note box for reflection.

### Coverage target

- 1 on a hidden assumption or a load-bearing claim that's not fully defended
- 1 on a missing experiment, control, or ablation
- 1 on how this result sits in the wider field (contradicts / confirms / complicates other work)
- 1 on a practical or conceptual limitation of the approach

### Good examples

> **Q17.** The main claim rests on the assumption that _assumption A_ (introduced almost in passing in §2.1) holds in the regime the authors test. Where would it fail in a realistic setting, and what would that do to Figure 3's conclusion?

_Why it works: points at a real load-bearing assumption and asks for a failure case._

> **Q18.** Reference [7] reports a result that, on the surface, contradicts this paper's central finding. The authors cite [7] but don't engage with the tension. What's the most charitable reconciliation you can construct — and the least charitable one?

_Why it works: grounds the critical question in a specific citation rather than vague "compare to other work"._

> **Q19.** The method has no ablation for component _C_, which on paper seems like the most important part. Design the missing ablation in two sentences — what would you hold fixed, what would you vary, what result would confirm or challenge the authors' interpretation?

_Why it works: asks the reader to do the critical-design work, not just complain._

### Bad examples (avoid)

- ❌ "What are the limitations?" — paper often lists these literally.
- ❌ "Could this be applied to other domains?" — generic, answerable without reading.
- ❌ "Is the sample size large enough?" — too common, rarely the actual weakness.

## Phrasing ledger — motivating verbs

Use these across the 20 questions to keep the treasure-hunt feel without overdoing any single one:

- "Somewhere in §X, …"
- "According to the paper, …"
- "Which of these does the paper actually claim?"
- "The authors hide the answer in §X — …"
- "Pick the one that matches the paper's wording"
- "In one sentence, why…"
- "Name the two figures that…"
- "See if you can reconstruct …"
- "Try to catch the authors …"

Avoid using any single phrase more than twice in one guide.

## Ordering within each level

Within a level, order questions by _where they live in the paper_ — roughly abstract → intro → methods → results → discussion → supplementary. The reader will often work the quest sheet linearly while reading, so the order should align with their path through the paper.

## Typst markup inside question text and options

You can use Typst emphasis in question text and MC options:

- `_italic_` — for method names, concepts, figure references
- `*bold*` — for sparing emphasis
- Backticks don't render as code in markup mode — use `raw("...")` if you need monospace

Keep markup light. Italic on a single term per question is usually enough.
