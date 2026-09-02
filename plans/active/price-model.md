# Plan: real price on task value, inflation, AI exposure and reputation

**Status:** active
**Created:** 2026-09-01
**Goal:** after deflating and netting out task value and reputation, test whether real price moves with AI exposure post-ChatGPT.

## Scope

Covers `code/76-price-model.py` — the panel, the deflation, the reputation and
task-value estimates, the AI test and the step-29 battery. Does **not** cover a
causal claim: the design has no control group beyond cross-category exposure, and
the parallel-trends gate fails, so nothing here is causal.

## Specification as built

    ln(real price)_it = a_i + d_t + b1*ln(1+reviews)_it + b2*rating_it
                        + g*(Exposure_c x Post_t) + e_it

- Real = nominal * CPI_base/CPI_t, SA quarterly mean, 2020Q1 base (matches step 23).
- Task value x = the gig fixed effect `a_i`, recovered post-fit. No observable in
  this data measures task value; a fixed effect is the honest home for it.
- Reputation z = `ln(1+reviews)` (the step-22/27 treadmill) and `rating`.
- Exposure primary = Eloundou human annotation (pre-registered). Secondary =
  step 75's market-measured AI-branded share, declared exploratory.
- SEs clustered on gig throughout.

## Steps
- [x] Build the gig-quarter panel with reputation columns and real prices
- [x] Estimate reputation, recover task value
- [x] Fit the pre-registered AI specification
- [x] Run the step-29 battery on the primary spec
- [x] Run it on the exploratory spec too
- [x] Put the model in `notebooks/00-explore.ipynb` as §10, importing step 76 rather
      than reimplementing it, with the event-study chart of the failing gate
- [ ] Decide whether the reputation and task-value results enter the paper
- [ ] If the market-measured exposure is to be used as treatment, pre-register it first
- [ ] Consider a synthetic-control fallback — the only one the prereg authorises

## Decision Log

- 2026-09-01: **The notebook imports step 76, it does not restate it.** §10 calls
  `build_panel`, `design`, `fe_ols`, `qdummies`, `mde` and `load_slug_exposure`
  from the script, so the notebook and `runs/price-model/model.md` are one fit.
  Every number in §10 reproduces the script's to the printed digit. Step 76's
  `PRICES` gained a `.csv.gz` fallback and `build_panel` gained path arguments so
  §10 runs from a fresh clone, where only the gzipped panels are tracked.

- 2026-09-01: **Eloundou primary, step 75 secondary.** Step 75's measure is better
  in every technical respect (in-market, time-varying) but ranks the categories
  nearly opposite to the pre-registration. Promoting it after seeing outcomes is
  the specification search the prereg exists to prevent, so it is reported as a
  declared, labelled robustness.
- 2026-09-01: **Placebo break moved to the pre-period midpoint (2021Q2).** The
  prereg's 2019Q2 sits before this panel opens, which makes `Post` all-ones and
  the interaction collinear with the gig effects — the first run reported a
  vacuous PASS with a NaN t-statistic. Deviation recorded rather than silently taken.
- 2026-09-01: **Battery extended to the exploratory spec.** Its raw coefficient
  was +13.76% per 10pp with t=11.2 and would have been quotable; category-specific
  trends cut it to +0.73% (t 0.84). Any category-by-quarter regressor gets this
  test from now on.

## Progress

- 2026-09-01: Built and run. 169,337 gig-quarter observations, 15,676 gigs,
  2019Q4–2024Q4. Reputation replicates (+7.33% per doubling vs step 22/27's
  +7.7%). The AI test is null and **underpowered** — point estimate 0.0333 against
  an MDE of 0.0689 — and fails the parallel-trends gate, the trend race and first
  differences. Reported as a silence, not a zero.
- 2026-09-01: Added to the notebook as **§10** (15 cells: the specification, the
  panel, deflation/reputation/task value, the pre-registered test, the battery, the
  exploratory measure, and a reading). Three charts, of which the event study —
  `Exposure x` every quarter, base 2019Q4 — is the one that carries the argument:
  the exposure gap opens across 2021, entirely before ChatGPT, and is flat for the
  whole post-period. The four ringed pre-launch points are exactly gate A's four.
