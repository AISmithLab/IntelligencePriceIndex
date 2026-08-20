# Technical Debt Tracker

## Retired

**TD1 — retired by decision 2026-08-06 (publication plan D4, `code/29-chained-elasticity-audit.py`). Not fixed: superseded.**

The defect is real and was re-measured — 24–35% of within-gig links span more than one quarter (translation 34.5%, marketing 27.7%, coding 26.1%, audio 25.5%, design 24.8%, writing 24.1%, video 23.9%), with a longest span of **35 quarters**. But repairing `code/12-panel-ipi.py` is the wrong move, because its *other* two properties — its own panel construction and its 2019Q1 base — are independent sources of divergence, and D3 settled the published base at 2020Q1. The paper's chain-drift exhibit should instead be computed on the production panel at the production base, which step 29 already does and which reproduces step 12's shipped per-category level exactly in four of seven categories.

The decomposition also shows the exhibit cannot say what §3.4 claims. Splitting the chained-vs-GEKS gap into as-built → adjacent-only (the defect) and adjacent-only → GEKS (genuine drift) gives a defect share ranging from **7% (audio) to 802% (translation)** — above 100% wherever drift runs the other way, and **in coding and translation the adjacent-only chain lands below GEKS** (273.7 vs 312.8; 130.4 vs 227.8). The residual drift has no consistent sign, so the honest statement is that the chained index diverges from GEKS by **−43% to +93%** across categories — an argument for GEKS rather than a measurement of drift.

`code/12-panel-ipi.py` stays in the repo for the audit trail and is not to be used for paper figures. Its downstream `panel-elasticity.csv` is cut outright (D4).

## Open

| # | What | Why Deferred | Priority | Added |
|---|------|-------------|----------|-------|
| TD2 | **The site's seven category colours are not distinguishable pairwise.** `data.json.colors` fails a colour-vision-deficiency check on all 21 pairs: worst CVD pair translation `#e87ba4` vs audio `#1baf7a` at **ΔE 6.1 (deutan)**, and translation vs video `#e34948` at **ΔE 13.2 for NORMAL vision** — below the 15 floor, i.e. hard to tell apart even with full colour vision. Three colours are also under 3:1 contrast on the card surface (audio 2.74, marketing 2.11, translation 2.62). This affects the **existing hero price chart**, where seven lines are overlaid and hue is the only identity cue. | Repainting changes the look of a chart the user built, and the category→colour mapping is used in the table sparklines and freelancer panels too, so it is a site-wide edit rather than a one-file fix. Step 62's new panel **sidesteps it by faceting** (one series per panel, identity in the title), so nothing new depends on the fix. | medium | 2026-08-20 |

<details><summary>TD1 as originally filed (kept for the audit trail)</summary>

| # | What | Why Deferred | Priority | Added |
|---|------|-------------|----------|-------|
| TD1 | **`code/12-panel-ipi.py` double-counts price growth across coverage gaps.** Within-gig relatives are keyed by destination quarter alone (`quarter_relatives[q_curr].append(relative)`, line 184), so a gig unobserved for k quarters files its whole k-quarter change as a single-quarter change — and the chain then applies it on top of the growth already contributed by gigs that *were* observed in between. 22–31% of links span >1 quarter in every category. Measured on design 2020Q1→2024Q3: as-built **326**, adjacent-only **229**, direct matched comparison **154**, GEKS **147**. `code/14-recent-ipi.py` is not affected (adjacent pairs only, lines 149–151). | Attempted the fix on 2026-07-27 and reverted it. Keying by the ordered pair `(q_prev, q_curr)` is the correct estimator but it changes what the chain can identify: anchoring at 2019Q1 drops audio/translation/data_* entirely (no link out of the base), and anchoring at each category's first linkable quarter leaves the composite with holes at 2022Q4/2023Q1, breaking `panel-summary.md`. Choosing between adjacent-only (loses the sparse tail), pair-keyed with a per-category anchor (loses cross-category comparability pre-2020), and windowing to 2020Q1+ is a **methods decision** that moves the paper's peak-composite and chain-drift figures. Not a mechanical fix. | medium — the series is no longer published on the site (2026-07-27), but §3.4 attributes the full chained-vs-GEKS gap (+217.7% vs +44.6%) to chain drift when part of it is this defect | 2026-07-27 |

</details>
