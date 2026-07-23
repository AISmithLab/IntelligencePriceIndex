# Tests: Method

**Draft file:** drafts/sections/method.md
**Last reviewed:** 2026-07-23

## Reviewer Simulation

| # | Critique | Severity | Status | Response |
|---|----------|----------|--------|----------|
| R1 | "Gigs are captured at irregular Wayback intervals and cover different windows; the chained Jevons index dumps multi-quarter changes into the single quarter a gig reappears, biasing timing." | major | PASS | §3.4 now reports **GEKS-Jevons** as the index: all quarter pairs compared directly and made transitive by averaging over link routes, so no chain exists to drift along. Quantified: ~26% hist / ~39% recent changes are gap-spanning; chained composite +217.7% vs GEKS +44.6% (2.2× level ratio by 2026Q1). |
| R2 | "Why GEKS rather than a time-dummy/hedonic regression, or a weighted multilateral (Törnqvist, Geary–Khamis)?" | major | PASS | §3.4 comparison paragraph: no gig-quarter quantities ⇒ weighted multilaterals unavailable, ILO manual recommends Jevons elementary aggregates. TPD reported as the alternative (66.1%, r=0.983 with GEKS); the two differ only through imputation (de Haan 2004) and the 10.9%-filled panel means TPD imputes ~89% of cells. |
| R3 | "GEKS is biased downward when disappearing products are dumped at clearance prices (Chessa et al. 2017), and your GEKS sits below TPD — exactly that direction." | major | PASS | §3.4 tests rather than assumes: final observed price change +0.090 log pts vs +0.070 for other transitions (t=1.34, n.s.), no category with a significant terminal drop. Structural reason given: 99% of gigs stop being observed mid-panel, so disappearance is crawl attrition, not delisting. |
| R4 | "Estimating over 2020Q1– rather than the full panel looks like a window chosen to get the answer you want." | minor | PASS | §3.4 gives the identification reason (pre-2015 quarters hold 2–4 gigs per category, leaving later quarters unreachable from the base), notes full-window GEKS over the reported window is standard practice, and that the window coincides with the already-published base period. |
| R5 | "MIN_MATCH = 3 is an arbitrary threshold." | minor | FAIL | §3.4 documents the choice and its provenance (mirrors MIN_RELATIVES=3 in steps 12/14) but the sensitivity check is not yet in the draft. Known magnitude: relaxing 3→1 moves audio's final level +17 pts and marketing's −13 pts. Needs a reported sensitivity table. |
| R6 | "Translation is estimated off very thin overlap — is that index meaningful?" | major | BLOCKED | 43% of translation quarter pairs clear the 3-gig bar, 15% have zero overlap, 22/25 quarters identified, bootstrap band ±26%. §3.4 reports the coverage and the band honestly, but the publication decision (report with wide band vs suppress) is still open. |
| R7 | "How do we know the GEKS implementation is correct?" | minor | PASS | §3.4 implementation-validation paragraph: exact agreement with `PriceIndexCalc` 0.7 (max abs diff 0.0000, r=1.0000) on the four categories the reference can process; the reference's ZeroDivisionError on the other three is explained as a panel-sparsity assumption it makes and ours violates. |
| R8 | "The base period is stated as 2019Q1 for the composite but the reported index runs from 2020Q1." | minor | FAIL | Pre-existing inconsistency in the composite-IPI paragraph of §3.4 (2019Q1) against the published 2020Q1 base used by the site and the GEKS window. Needs one base period stated throughout. |

## User Requirements

| # | Instruction | Date | Status | Location |
|---|-------------|------|--------|----------|
| U1 | "Explain exactly how you aggregate data across freelancers sampled at different rates / covering different time ranges" | 2026-07-14 | PASS | §3.4 (GEKS-Jevons paragraphs); FAQ §8 Step 5 |
| U2 | "Use another method besides fixed effects" | 2026-07-15 | PASS | §3.4 — GEKS-Jevons built (`code/21-geks-index.py`) |
| U3 | "Drop fixed effects entirely; GEKS-Jevons is the approach" | 2026-07-15 | PASS | §3.4 no longer presents FE/TPD as the index; it appears only as the imputation alternative in the comparison paragraph. Site (`docs/index.html`, `docs/faq.html`, `docs/gallery.html`, `ipi.js`, `gallery.js`) reads `index_geks` and names GEKS-Jevons throughout. |
