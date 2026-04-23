# Korean Localization

When the user selects Korean, the guide uses Korean for prose and connective tissue, but **all technical and academic terms stay in English**. The reader will encounter those terms written in English in the paper itself — translating them would introduce friction, not ease it.

## What to keep in English

Keep the original English form (no translation, no transliteration) for:

- **Method names and model names** — RNA-seq, CRISPR-Cas9, scRNA-seq, Bowtie2, STAR, transformer, BERT, GPT, ResNet, diffusion model, VAE, Monte Carlo.
- **Gene, protein, molecule, drug, and strain names** — TP53, BRCA1, p53, mTOR, insulin, rapamycin, E. coli, C. elegans.
- **Statistical and quantitative terms** — p-value, confidence interval, standard error, ROC, AUC, F1, precision, recall, BLEU, perplexity, sample size, batch size, effect size.
- **Field-specific jargon used in the paper** — self-attention, cross-attention, pretraining, fine-tuning, zero-shot, few-shot, ablation, benchmark, latent space, embedding.
- **Section names when citing a location in the paper** — write "§2.1" or "Introduction", not "서론" (this keeps the pointer aligned with what the reader will actually see on the page).
- **Figure/Table/Equation references** — "Figure 3B", "Table 2", "Eq. (4)" — keep as English.
- **Unit labels and SI prefixes when they appear in the paper** — µM, nm, kcal/mol.
- **Dataset and benchmark names** — ImageNet, GLUE, COCO, TCGA.

## What to translate / write in Korean

Translate into Korean:

- General connective prose — "다음 질문에 답해 보세요", "논문을 읽으면서", "어떤 가정이 숨어 있는지".
- The treasure-hunt narration ("Scout the Terrain" becomes "지형 정찰" or similar).
- General-purpose verbs — read, find, compare, reconstruct, connect, challenge.
- Document structure labels — cover title, roadmap heading, level headings.

## Tone

Use a friendly, slightly literary but not casual register — the `-요` / `-습니다` level varies, prefer `-요` for quest narration and `-습니다` for the more formal cover block and roadmap. Avoid overly textbook-ish phrasing; this is a companion document, not a problem set.

## Example translations of the three level names

Good options (pick one set per guide, be consistent):

| English                    | Korean (Option A — literary) | Korean (Option B — plain) |
| -------------------------- | ---------------------------- | ------------------------- |
| Level 1: Scout the Terrain | 1단계: 지형 정찰             | Level 1: 훑어보기         |
| Level 2: Decode the Map    | 2단계: 지도 해독             | Level 2: 꿰뚫어보기       |
| Level 3: Face the Dragon   | 3단계: 용과 맞서기           | Level 3: 비판적으로 읽기  |

## Example quest questions in Korean

### Level 1 — multiple choice (지형 정찰)

> **Q1.** Abstract에서 저자들은 기존 방법 대비 기법의 우수함을 하나의 수치로 요약합니다. 그 수치는 다음 중 어느 것일까요?
>   (a) baseline 대비 3배
>   (b) baseline 대비 15배
>   (c) 상대 개선 47%
>   (d) 두 order of magnitude 차이
>   (e) F1 기준 0.3 percentage point

_Notes: `Abstract`, `baseline`, `order of magnitude`, `F1`, `percentage point` — all kept in English. Korean carries the narration. Distractors are plausible numbers from adjacent contexts in the paper._

> **Q3.** Figure 2의 panel C는 제안 기법과 baseline 하나를 비교합니다. 본문에 따르면 그 baseline은 무엇인가요?
>   (a) random initialization
>   (b) 참고문헌 [14]의 _method Y_
>   (c) pretraining 없는 supervised fine-tuning
>   (d) naive MAP estimate
>   (e) 저자들이 자체 구현한 _method Z_

### Level 2 — short answer (지도 해독)

> **Q10.** 저자들이 더 표준적인 _method Y_ 대신 _method X_를 선택한 이유를 한 문장으로 설명해 보세요.

> **Q13.** Discussion은 이 방법이 "benchmark를 넘어서까지 generalize한다"고 주장합니다. 이 주장을 가장 강하게 뒷받침하는 figure 두 개를 짚어 보세요.

> **Q14.** §2.1에 조용히 놓인 assumption 하나가 Figure 3의 결론을 떠받치고 있어요. 그 assumption을 한 구절로 적어 보세요.

### Level 3 — open reflection (용과 맞서기)

> **Q17.** 이 논문의 핵심 주장은 §2.1에서 거의 지나가듯 언급된 _assumption A_에 기대고 있어요. 이 assumption이 현실적으로 어떤 setting에서 깨질 수 있고, 그러면 Figure 3의 결론은 어떻게 흔들릴까요?

> **Q18.** 참고문헌 [7]의 결과는 표면적으로 이 논문의 핵심 주장과 충돌하는 것처럼 보이는데, 저자들은 [7]을 인용만 하고 tension에 대해서는 논의하지 않습니다. 가장 우호적인(charitable) 화해 방식과 가장 비판적인 시각을 각각 어떻게 구성하시겠어요?

## Punctuation and formatting

- Use Korean full-width punctuation for Korean sentences: `.`, `,`, `?`, `!` are fine; don't mix with `。` or `，` (those are Japanese/Chinese).
- Quotation marks: `"..."` is OK; `「...」` is uncommon in scientific writing.
- Keep English terms in the running Korean sentence without parentheses or Korean transliteration in parentheses unless the user asks for it. E.g., write "RNA-seq data" not "RNA-seq (알엔에이-시퀀싱) 데이터".
- Spacing: Korean spacing rules apply to Korean words; English terms follow English spacing. A space before and after an English term embedded in Korean text is standard: "이 논문은 transformer architecture를 사용합니다" (note the space before `transformer` and between `architecture` and `를`).

## Typst italic/bold inside Korean strings

Same as English — `_word_` for italic, `*word*` for bold. Works for both English terms and Korean words embedded in a single string. Example:

```typst
text: "저자들은 더 표준적인 _method Y_ 대신 _method X_를 선택했어요."
```

renders with italic on the two English method names and plain text on the Korean.

## Fonts

The skill bundles the **SeedKRex** family in `assets/` — four styles: Regular, Regular Italic, Bold, Bold Italic. This is the default Korean font and renders both Hangul and Latin glyphs, so `_italic_` and `*bold*` markup works uniformly across a mixed Korean/English string like `"저자들이 _method X_를 왜 *선택했는지*를 한 문장으로 설명해 보세요."`.

The template's Korean font stack is `("SeedKRex", "Lato")` — SeedKRex first, Lato as a safety fallback for any glyph SeedKRex doesn't cover. Do not change this without a good reason; if the user asks for a different Korean typeface, make sure the chosen family ships at least Regular + Italic so Typst `_italic_` still works.
