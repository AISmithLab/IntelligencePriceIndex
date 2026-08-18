# Plan: competitive structure of the market, not just its price level

**Status:** active
**Created:** 2026-08-18
**Goal:** answer "how does the diffusion of generative AI change long-run pricing
and competitive structure of online freelancer markets?" using data already
collected, and state precisely which half of that question the data can carry.

## Why this plan exists

The user asked the question above. The project already answers the **pricing**
half — the IPI is +40.7% real / +78.4% nominal over 2020Q1–2026Q1 (±3.7%), with
inflation and the reputation treadmill measured as rivals rather than waved away.
It had never asked the **structure** half: what happened to the price
*distribution*, to product-line depth, to dispersion, and to the concentration of
sales.

Steps 46 and 48 closed the category-level AI attribution: four designs failed
(parallel trends, the trend horse race, the CPI-U placebo, synthetic control with
in-space placebos whose p-floor is 1/7 = 0.143). So this plan does two separate
things and keeps them separate:

- **(a) describe** structural change across the diffusion window, with the
  sampling caveat attached to each number; and
- **(b) test two identification routes that do not use the seven-category
  exposure ranking at all** — both of which failed, for reasons now specific.

## Scope

**Covers.** `data/pilot/balanced-prices.csv` on the balanced frame, 2019Q3–2024Q4
(257,208 gig-quarter observations, 37,888 listings). Price distribution,
versioning, dispersion, sales concentration, and two new within-category designs.
Reuses `data/fiverr-inc-metrics.csv` for the demand-side composition fact.

**Does not cover.** Exit and entry (unmeasurable: `n_404 = 0` across 509,339
captures). Realised order value (the IPI reads listed basic-package prices).
Anything post-2024Q4 (trailing edge). Nothing here is pre-registered.

## Window

- **Start 2019Q3.** Extraction is 100% `packageList` from that quarter; before it
  the frame is a 3-way mix whose 3-tier detection rates differ by 19 points, so a
  versioning series across the seam is a parser artefact.
- **End 2024Q4**, for step 48's reason: captures per quarter collapse ~9,300 → ~700.

## Steps

- [x] Frame audit; fix the window on extraction homogeneity
- [x] Price distribution over time, all listings vs a fixed panel
- [x] Date the commodity-tier collapse with a searched break, not an assumed one
- [x] Versioning: 3-tier share and the premium/basic ladder
- [x] Dispersion: sd log price, P90–P10
- [x] Sales concentration, and whether it is mechanical
- [x] New design 1: within-category price-tier DiD ("does AI eat the cheap end?")
- [x] New design 2: price convergence, with a ranking-window placebo
- [x] Seller-conduct margins: repricing, price-rank mobility, seller-level
      concentration, the reputation gradient before vs after
      (`code/51-seller-structure.py`)
- [x] Assemble the answer to the user's question from everything collected
      (`drafts/market-structure-answer.md`)
- [x] Pre-register the surviving descriptive claims before any further
      specification search (`plans/active/structure-descriptive-lock.md`)
- [x] Gig-level continuous exposure — RAN as step 50, pre-registered, FAILED on
      the trend horse race and the CPI-U placebo. Scored gigs directly rather
      than the 151 item clusters, which turned out to be built on the superseded
      500-seller pilot
- [x] Decide framing — **USER CHOSE A SECOND PAPER**, 2026-08-18
- [x] Scaffold it with real content: `drafts/structure/` (7 sections) +
      `tests/structure-*.test.md` (9 files) + `--main` support in `render.py`
- [ ] Close the four open test FAILs: platform representativeness (§2 R3), the
      category classifier reference (§2 R7), the pre-2020 normalisation baseline
      (§5 R3), and the downward-nominal-rigidity claim (§5 R4)
- [ ] Figures — four are marked in `tests/structure-master.test.md` M8
- [ ] Point `code/32-check-draft-numbers.py` at the second paper tree

## Decision Log

- 2026-08-18: **Window starts 2019Q3, not 2018Q3.** The balanced frame reaches
  back to 2018Q3 but extraction method is a 3-way mix before 2019Q3 and the
  mix correlates with tier detection. Losing four quarters is cheaper than
  publishing a versioning series with a parser seam in it.
- 2026-08-18: **Every candidate finding is run against a placebo that could
  destroy it, in the same script.** Three of six were destroyed. This is the
  step-29/step-46 precedent applied before drafting rather than after.
- 2026-08-18: **Break dates are searched, not assumed.** Assuming 2022Q4 and
  finding a significant coefficient would have produced a wrong headline on the
  commodity-tier result, whose actual steepest decline is 2021.
- 2026-08-18: **The trend-break form, not the level-shift form, matches the
  question.** The commodity-tier series is a decline whose slope changes, so a
  level-shift search reports curvature and picks an endpoint. Both are printed.
- 2026-08-18: **The seller-level concentration null is reported, not dropped.**
  Aggregating accrual from listings to sellers was the obvious objection to step
  49's null, and it changes nothing. A null that survives its own strongest
  objection is a result, so it is locked as N2 rather than left in a run file.
- 2026-08-18: **A lead that clears its own placebo but disagrees with the full
  frame stays a lead.** The reputation-gradient rise (L1) is the most interesting
  structural claim available here and is deliberately not reported as a finding.
- 2026-08-18: **Gig fixed effects do not protect against composition.** The quota
  manifest adds ~1,250 net listings at 2022Q3 and the added ones are cheaper,
  manufacturing a +5.7pp jump in the ≤$10 share at almost exactly the break
  quarter. All distributional claims are read off a balanced panel.

## Progress

- 2026-08-18: Built `code/49-market-structure.py` → `runs/market-structure.out`.
  Nine sections, six candidate findings, three killed. See `progress.md`.
- 2026-08-18 (night): Built `code/51-seller-structure.py` →
  `runs/seller-structure.out`, covering the seller-conduct margins step 49 left
  out. Five candidates, three killed, one demoted to a lead, one survivor:
  **repricing fell 23.6% → 18.3% of listing-quarters and the fall is entirely
  fewer price INCREASES — cuts are flat.** Searched break is 2021Q3, not 2022Q4.
  Assembled the whole answer into `drafts/market-structure-answer.md` and locked
  the descriptive survivors in `plans/active/structure-descriptive-lock.md`.
- 2026-08-18 (night, later): User chose **a second paper**. Built
  `drafts/structure/` end to end, nine test files, and `--main` rendering.
  Reviewer simulation immediately produced three FAILs that were closed the same
  session — including S2c, a new strict-panel check that could have killed the
  repricing finding and did not (D7a in the lock).
