# Plan: a task taxonomy, a reference task value, and what reputation is worth

**Status:** active
**Created:** 2026-09-03
**Goal:** move task value out of step 76's gig fixed effect and into a reportable
taxonomy node, then estimate reputation's price effect against that anchor.

## Scope

Covers `code/77-task-taxonomy.py` (the two-level taxonomy and the reference task
values) and `code/78-reputation-price.py` (the three-level reputation model).
Does **not** cover AI exposure — nothing here interacts with `Post`, and the
panel deliberately drops step 76's before/after balance requirement because
nothing here is a difference-in-differences.

## Why this exists

Step 76 put task value in a gig fixed effect. That was the honest home for it,
but a fixed effect that ABSORBS task value can never REPORT it: `a_i` came back
with an SD of 1.249 log points and no way to say what any part of it was. Worse,
a gig fixed effect also absorbs the permanent component of reputation, so step 76
could only ever see a listing repricing itself.

## Steps
- [x] Extract the deliverable phrase from the title (`<seller>: I will <X> for $N on fiverr.com`)
- [x] Build ordered, first-match-wins subcategory rules per domain
- [x] Fold nodes under 30 gigs into `<domain>/other`; report coverage honestly
- [x] Reference task value per node, raw (mean ln p) and reputation-adjusted (node FE)
- [x] Reputation at three levels: between nodes, between gigs within node, within gig
- [x] Per-node reputation slopes
- [x] Variance decomposition: domain vs node vs gig
- [x] Put it in `notebooks/00-explore.ipynb` as §11, importing steps 77/78
- [ ] Decide whether the B-vs-C sign reversal is the paper's reputation result
- [ ] Repair the domain assignment — `translation/voiceover_leak` is 721 gigs of step 04's leak
- [ ] Validate the taxonomy against a hand-labelled sample before it carries a claim

## Decision Log

- 2026-09-03: **Titles, not slugs.** Step 04 matches keywords on the URL slug.
  Titles are richer, present on 99.99% of rows here, and regular enough to strip
  to a deliverable phrase. Subcategory rules match on that phrase.
- 2026-09-03: **Rules are ORDERED and first-match-wins**, most specific first, so
  `shopify dropshipping store` reaches `ecommerce` before `web_dev` sees `store`.
  The order is part of the definition and must not be sorted.
- 2026-09-03: **The reference task value is reported twice.** The raw node mean is
  what was asked for, but it is contaminated: a node full of well-reviewed
  veterans carries their standing in its mean. The adjusted version is the node
  fixed effect from a joint fit. Correlation 0.970, mean absolute gap 0.094 log
  points — so the ranking survives, but individual nodes move up to 0.375.
- 2026-09-03: **No balance requirement.** Step 76 needed gigs on both sides of
  2022Q4 for its DiD. Nothing here does, so the panel is 35,826 gigs against
  step 76's 15,676.
- 2026-09-03: **`translation/voiceover_leak` is named for what it is.** 721 gigs
  in the translation domain whose deliverable is a voice over. The subcategory
  layer makes step 04's classifier leak countable rather than repairing it.

## Progress

- 2026-09-03: Built and run. **65 nodes**, 77.5% of gigs in a named subcategory.
  Reference task value runs **$6.66** (`translation/subtitling`) to **$59.38**
  (`marketing/content_strategy`), a spread of 2.188 log points. Domain explains
  5.7% of price variance, the node 10.9%, the gig 91.4%.
- 2026-09-03: **The headline is a sign reversal.** Reputation is +7.62% per
  doubling WITHIN a gig (t 31) and **−9.08% BETWEEN gigs in the same node**
  (t −28). Step 25 found this at category level as "near zero versus positive";
  holding the task fixed at node level sharpens it to significantly negative.
  Reading: a high review count marks both a seller who has been around (raises
  price) and one running a cheap high-volume operation (lowers it). Between
  sellers the second dominates; within one listing only the first can move.
- 2026-09-03: Per-node slopes are **positive in all 58 estimated nodes**, 45
  significant, ranging +1.84% (`translation/localization`) to +27.11%
  (`translation/interpreting`). Commodity translation clusters at the bottom
  (subtitling +2.97%, transcription +2.65%), consultative work at the top.

- 2026-09-03: **Reference values moved to the estimation sample.** Step 77 was
  reporting them on the full panel while step 78 fit on rows carrying both
  reputation columns; `marketing/content_strategy` read \$67.11 in one place and
  \$59.38 in the other. One number, defined where it is used.
- 2026-09-03: **§11.3's scatter is near-mechanical and is now labelled as such.**
  `adjusted` comes from a fit containing β₁, so the gap is approximately
  β₁ × (node mean log reviews − grand mean); the measured correlation is 0.978.
  It shows which nodes move, not that they move. The sign belongs to spec B.
- 2026-09-03: Added to the notebook as **§11** (15 cells, four charts), importing
  steps 77 and 78. Every printed number reproduces `runs/taxonomy/*.md`.
