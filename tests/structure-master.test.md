# Tests: Structure paper — master (cross-cutting)

**Draft:** `drafts/structure/main.md` → `drafts/structure-draft-YYYY-MM-DD.html`
**Assembled answer this paper is built from:** `drafts/market-structure-answer.md`
**Claim lock:** `plans/active/structure-descriptive-lock.md`
**Last reviewed:** 2026-08-18

## User Requirements

| # | Instruction | Date | Status | Location |
|---|---|---|---|---|
| U1 | "Answer: how does the diffusion of generative AI change long-run pricing and competitive structure of online freelancer markets?" | 2026-08-18 | PASS | whole paper; answered directly in §6 |
| U2 | "Help me do this with data we already have" — no new collection | 2026-08-18 | PASS | §2; every figure traces to an existing run file (see provenance table in `drafts/market-structure-answer.md` §8) |
| U3 | Ship this as a **second paper**, not a section of the IPI paper | 2026-08-18 | PASS | `drafts/structure/`; the IPI is cited as the instrument [CITE-ipi], not restated |
| U4 | "Make the wording easy to understand and clearly explain findings" | 2026-08-20 | PASS | `drafts/market-structure-answer.md`: a plain-language glossary added as "How to read this document" (defines listed vs realised price, real vs nominal, matched-model, balanced panel, fixed effects, searched break, placebo, parallel trends, exposure, MDE, Gini, gate); "**In plain terms:**" glosses added at §3 intro, §3.4, §4.3, §4.4.1 gate A, §4.5; §4's opening now explains what an identification design *is* and what "fails" means; GEKS-Jevons, downward nominal rigidity and review-propensity drift glossed on first use. **Not yet propagated to `drafts/structure/`** |
| U5 | "Make a summary similar to market-structure-answer summarizing the data collected and the findings" | 2026-08-20 | PASS | `drafts/plain-summary.md` — a standalone non-technical companion: Part 1 is the data collection (archive scale, the three built datasets, outside sources, the newly found order records), Part 2 the findings (prices, quantities, structure, AI diffusion, the timing mismatch, the twenty-launch test, the positive control, why nine designs failed), Parts 3–4 the limits and what would change the answer. Every figure is the same figure as the full document, with a cross-reference table at the end |
| U6 | Correct the reading that "prices rose **during** AI launches but transactions decreased" | 2026-08-20 | PASS | `drafts/plain-summary.md` §"About the way you summarised it" — both directions confirmed, and the equivocation on *during* named explicitly: the level movements span the AI years, the **turning points** are 2020Q3–2021Q4. This is the reading the whole document exists to separate, so it is stated before Part 1 rather than buried in the attribution section |

## Cross-cutting criteria

| # | Criterion | Status | Note |
|---|---|---|---|
| M1 | Every number in the draft traces to a run file or a frozen-numbers file | PASS | provenance table maintained in the answer doc §8 |
| M2 | No claim exceeds its frame: fixed/balanced panel stated wherever change over time is claimed | PASS | §3 states the frame on every row |
| M3 | Break dates are searched, never assumed | PASS | §3.3, §3.4 print the search |
| M4 | Nulls are reported as results, not omitted | PASS | §3.5, §3.7, §4 |
| M5 | No causal language survives anywhere outside §5.2's explicit rival discussion | PASS | scanned 2026-08-18; the only hit is §1's explicit disclaimer |
| M6 | Notation and terminology consistent (listing vs gig, sales proxy vs sales) | PASS | glossary paragraph added to §2.1 |
| M7 | The paper does not restate the IPI paper; it cites it | PASS | §3.1 quotes frozen figures and cites |
| M8 | Figures exist for the five headline series | BLOCKED | no figures drafted yet — see §Figures below |
| M9 | Every technical term is glossed on first use, and every dense result carries a plain-language statement of what it means | PASS in `market-structure-answer.md` (2026-08-20), FAIL in `drafts/structure/` | the answer doc carries the glossary and the "in plain terms" glosses; the paper tree does not yet |

## Figures still to draw

<!-- FIGURE: $5 tier share and $100+ tier share, fixed panel, 2019Q3-2024Q4, with the searched break at 2021Q2 marked and ChatGPT marked separately -->
<!-- FIGURE: repricing decomposition — share of listing-quarters with an increase vs a cut, balanced panel -->
<!-- FIGURE: buyers and spend-per-buyer, 2017-2026, twin axes -->
<!-- FIGURE: gate card for design I6 as a visual pass/fail strip -->
