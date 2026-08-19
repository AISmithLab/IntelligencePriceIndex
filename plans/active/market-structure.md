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
- [x] **Date the AI timeline properly — RAN as step 52.** Searched the break in
      the transaction proxy over 15 candidate quarters instead of assuming
      2022Q4. Proxy peaks **2020Q3**; ChatGPT ranks **11 of 15**, the image
      models last. Converts "no break at ChatGPT" from an absence of evidence
      into a falsification of dates.
- [x] **Test the operators' own two claims on the recent frame — RAN as steps
      53-55.** Design 7 (Fiverr's "weakness in AI-exposed categories") dies on
      category-level randomisation (4th of 21 pairs) and a flat exposure
      gradient (rho +0.04). Design 8 (Upwork's under-$500 erosion) is correctly
      signed and monotone on 2023-24, then dies on a significant opposite-signed
      pre-AI placebo and a searched break at **2020Q3**. Eight designs, eight
      failures.
- [x] **Audit every route to more 2025-26 data — DONE as step 56**, →
      `plans/active/recent-frame-collection.md`. R3 Common Crawl dead on
      evidence; R5 the gig sitemap is free, open and was not on the agenda.
      First snapshot taken (288,976 gig URLs). One decision open: the live crawl.
- [x] **Measure AI diffusion INSIDE the market — RAN as step 57.** The answer to
      "what is already held that no design uses" was `title`, on 100.0% of
      384,983 observations. Entry-cohort AI share 0.0-0.5% → **5.98% at 2023Q1**;
      diffusion through **entry** (22 of 11,425 incumbents ever relabelled);
      entry **above** the median price; an **anti-AI segment from exactly zero**
      before 2023Q2. Written up as answer §3.7.
- [x] **THE POSITIVE CONTROL — the finding that changes the paper's standing.**
      The identical searched-break procedure ranks ChatGPT **1 of 19** on the
      diffusion series (top four candidates all AI milestone quarters, SSR
      spread 227%) against **11 of 15** and **16 of 17** on the outcome series.
      The instrument is not blind. The null is a fact about the market, not the
      method. Answer §4.3.1.
- [ ] **Fold §3.7 and §4.3.1 into the second paper** (`drafts/structure/`). The
      answer document has them; the paper tree does not. §4.3.1 in particular
      should be *early* in the identification section, not late — it is the
      reason a reader should believe the null at all.
- [ ] **Design 9: niche-level AI penetration** → `plans/active/ai-penetration-prereg.md`,
      pre-registered 2026-08-19, nothing estimated. The first treatment measure
      in the project that varies within category and within quarter.
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
- 2026-08-19: Steps 52-55 ran. The AI *timing* claim is falsified rather than
  merely unsupported, and both operators' specific public claims were tested
  directly and failed. Scope of the null dated to **2024Q4** throughout, because
  the period the operators describe is one this frame barely reaches.
- 2026-08-19 (later): Step 56 audited every collection route on measurement.
  The 2025-26 frame is 4-6x too thin (realised MDE 0.131 / 0.083) and the
  archive route to 2026Q2+ is closed by PerimeterX.
- 2026-08-19 (latest): **Step 57 answers the plan's own question from a new
  direction.** The user asked to answer the standing question on data already
  held; auditing for unused held data returned `title`. Two things follow.
  (i) Generative AI *is* in this market, dated to 2023Q1, arriving through entry
  and above the median price, and it created an anti-AI segment from nothing —
  so the answer now has a diffusion half it never had. (ii) The searched-break
  machinery gets a **positive control**: it resolves the AI date to within one
  quarter when asked about a variable AI moved. That retires the strongest
  objection to the whole identification argument and is recorded as R13 in
  `tests/structure-identification.test.md`.
