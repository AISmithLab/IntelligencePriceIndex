# How does generative AI diffusion change long-run pricing and competitive structure in online freelancer markets?

**Answer assembled 2026-08-18 from data already collected.** Sources: the IPI
panel (`data/pilot/paper-numbers.md`, frozen 2026-07-31), the balanced archival
frame (`data/pilot/balanced-prices.csv`, 257,208 gig-quarter observations on
37,888 listings, 2019Q3–2024Q4), Fiverr Inc.'s reported metrics
(`data/fiverr-inc-metrics.csv`), and steps 46–51.

---

## 0. The answer in one page

**On pricing, the data are decisive and the direction is the opposite of the
standard prediction.** Listed prices for cognitive-labour services rose
**+40.7% in real terms** over 2020Q1–2026Q1 (+78.4% nominal, ±3.7%), against
CPI-U of +26.8%. Roughly half the nominal rise is general inflation and a large
further share is reputation accumulation; a reputation-adjusted composite floors
the real rise at about **+39.7%** on a raw ceiling of **+79.0%**. Prices did not
fall in any category, in any specification, at any point in the diffusion window.

**On competitive structure, four of the five things a commoditisation story
predicts did not happen, and the fifth happened too early to be caused by
generative AI.**

| what a commoditisation story predicts | what the data show |
|---|---|
| prices fall | real prices **+40.7%** |
| quantities rise | Fiverr buyers **−36%** from the 2021 peak; implied orders **−18%** vs 2020 |
| the cheap tier widens | the **$5 tier emptied**, 27.3% → 10.3% of listings — but its steepest decline is **2021Q2**, and the decline **slows** after ChatGPT |
| price competition intensifies | repricing **fell** (23.6% → 18.3% of listing-quarters), and the fall is **entirely fewer price increases**; price cuts are flat at ~5–6% |
| sales concentrate on winners | Gini among trading listings **flat** (0.64 → 0.61); among trading **sellers** flat too (0.637 → 0.618) |

**On attribution, the honest answer is that this project cannot assign any of it
to generative AI, and it now knows precisely why.** Six identification designs
have failed (§4). The most informative failure — the sixth, pre-registered before
it ran — establishes a specific fact rather than a shrug: **there is an
exposure-correlated differential trend that predates ChatGPT, and there is no
break at ChatGPT.**

**So the defensible answer is a joint description, not a causal claim.** Across
the generative-AI diffusion window this market moved *upmarket*: fewer and larger
buyers, higher listed prices, a hollowed-out commodity tier, deeper product
menus, no price war, and no change in who captures the sales. That is the shape
of a market being **repositioned** — by sellers, by the platform, and by a
composition shift in demand — not the shape of a market being **commoditised**.
Whether generative AI caused the repositioning is not identified on this data,
and the timing evidence (§4.3) is actively unhelpful to an AI account.

---

## 1. The pricing half

### 1.1 Level

Matched-model GEKS-Jevons index over seven categories, 2020Q1 = 100.

| series | terminal 2026Q1 nominal | real | real Δ | ±95% |
|---|---:|---:|---:|---:|
| **composite** | 178.4 | 140.7 | **+40.7%** | ±3.7% |
| design | 156.1 | 123.2 | +23.2% | ±4.8% |
| writing | 201.8 | 159.2 | +59.2% | ±8.3% |
| marketing | 294.3 | 232.2 | +132.1% | ±7.7% |
| coding | 250.1 | 197.3 | +97.3% | ±17.1% |
| video | 265.6 | 209.5 | +109.5% | ±11.9% |
| audio | 322.3 | 254.2 | +154.2% | ±13.9% |
| translation | 299.5 | 236.3 | +136.3% | ±29.2% |

**Do not rank the categories.** Six of seven miss the ±5% precision standard the
project sets; the top three intervals overlap completely. In particular
translation — the most AI-exposed category on the pre-registered exposure
measure (β 0.840) — carries a ±29.2% band on 28 panel gigs.

### 1.2 What the rise is made of

- **General inflation** accounts for roughly half the nominal increase
  (CPI-U +26.8% against nominal +78.4%).
- **Reputation accumulation** accounts for a large further share. Within a gig,
  price rises **+7.7% per doubling of cumulative reviews**; rebuilding the index
  on reputation-adjusted prices gives a composite band of **+39.7% to +79.0%**.
  The floor is soft — β's own 95% CI moves it between roughly +50% and +28% —
  and it is a lower bound rather than a correction, because review counts are
  cumulative sales and so β absorbs demand as well as standing.
- **What remains** is not attributable. See §4.

### 1.3 The critical caveat on what "price" means here

The IPI reads **listed basic-package prices**, not realised order value. Fiverr's
spend-per-buyer path (§2) and its stated upmarket push both suggest buyers moved
to higher tiers, so realised prices likely rose *faster* than the IPI. Every
quantity figure derived by dividing revenue by the IPI is therefore an **upper
bound on the quantity decline**.

---

## 2. The quantity half — the only real transaction data in the project

The archive contains no transactions; `review_count` is a proxy. The one source
of actual quantities is Fiverr Inc. (NYSE: FVRR), where GMV = active buyers ×
spend per buyer is an accounting identity, not an estimate (it reproduces every
independently reported GMV to within rounding).

| period | buyers (M) | $/buyer | GMV ($M) | buyers YoY |
|---|---:|---:|---:|---:|
| 2020 | 3.40 | 205 | 699 | +44.7% |
| 2021 | **4.20** | 242 | 1,020 | +23.5% |
| 2022 | 4.20 | 262 | 1,090 | **+0.0%** |
| 2023 | 4.10 | 278 | **1,140** | −2.4% |
| 2024 | 3.60 | 302 | 1,087 | −12.2% |
| 2025 | 3.10 | 342 | 1,060 | −13.9% |
| 2026 TTM-Q2 | **2.70** | 368 | 994 | −12.9% |

Three facts matter for the structure question.

1. **Buyers peaked in 2021 and are −36%.** GMV is only −12.8% from its peak. The
   entire gap is spend per buyer, which rose *every single year* from $119 (2017)
   to $368. **Fewer, larger buyers.**
2. **Implied order count.** Deflating GMV by CPI-U and dividing by the IPI real
   composite gives real GMV +11.3%, real price +35.8%, and therefore
   **orders −18.0% vs 2020, −38.6% from the 2021 peak.** Treat as an upper bound
   on the decline, per §1.3.
3. **This kills the leading rival explanation for the archive's demand result.**
   The 13–43% fall in per-gig review accrual at 2022Q4 was equally consistent
   with a real transaction decline and with review-propensity drift. Fiverr's
   buyer and GMV series have nothing to do with reviewing behaviour, and they
   fall too. **The direction is externally corroborated.**

The archive's own demand result, for completeness (step 46, gig FE + linear
trend, gig-clustered SEs, break at 2022Q4):

| category | exposure arm | break in review accrual | t |
|---|---|---:|---:|
| writing | HIGH | −42.9% | −23.00 |
| translation | HIGH | −37.2% | −13.48 |
| audio | **LOW** | −35.5% | −15.28 |
| coding | mid | −35.2% | −17.63 |
| video | **LOW** | −28.6% | −14.49 |
| marketing | mid | −23.7% | −8.49 |
| design | mid | −13.1% | −6.65 |

**Every category fell, including the least exposed ones**, and the least-exposed
category of the seven (audio, β 0.248) has the third-largest fall. Spearman ρ
between exposure rank and break size is +0.429 over seven categories, where
|ρ| > 0.79 is needed for p < 0.05. That is what a **platform-wide** shock looks
like.

---

## 3. The structure half — five facts, each with the guard that could have killed it

All figures are read off a **balanced panel** wherever a change over time is
claimed. This is not a formality: the quota manifest adds ~1,250 net listings at
2022Q3 and the added ones are cheaper, which manufactures a +5.7pp jump in the
≤$10 share one quarter before the break of interest. **Gig fixed effects do not
protect against composition.**

### 3.1 The commodity tier emptied — but before ChatGPT

Share of listings priced at $5, fixed panel: **27.3% (2019Q3) → 10.3% (2024Q4)**.
On all listings, 32.0% → 11.4%. The $100+ tier moved the other way, 15.6% → 22.4%.
Median listed price $15 → $30.

The break date was **searched, not assumed**, and this decides the interpretation:

- best trend break on the balanced panel is **2021Q2**;
- the ChatGPT quarter carries the **opposite sign**;
- the decline **slows** after 2022Q4.

Assuming 2022Q4 returns a significant coefficient and would have produced a wrong
headline. The commodity tier emptied on a schedule that generative AI cannot
explain — the steepest decline is eighteen months before ChatGPT's release.

### 3.2 Product lines got deeper and the ladder compressed

Fixed panel, 2019Q3 → 2024Q4: share of listings offering three tiers
**82.1% → 90.6%**; the premium/basic ratio among three-tier listings
**4.06× → 3.80×**. Sellers version more and spread their own menu less widely —
consistent with menu design converging on a platform template, and with sellers
raising the floor faster than the ceiling.

### 3.3 Dispersion fell, then partly recovered

sd of log price, fixed panel: **1.428 (2019Q3) → 1.150 (2023Q3) → 1.233 (2024Q4)**.
The trough is mid-2023. **Descriptive only** — an attempt to convert this into a
convergence result died in §4.

### 3.4 Sales did not concentrate — at listing level or at seller level

Listing-level Gini of quarterly review accrual rises 0.63 → 0.75, which looks
like a winner-take-all result and is not one. Gini **among listings with any
sales** is flat (2021 0.64 → 2023 0.61). The whole rise is the zero-sales share,
and that rises only in 2024 — the trailing edge where captures per quarter
collapse from ~9,300 to ~700. It is dormancy at the edge of the crawl, not a
shift of share.

Step 51 closed the obvious objection: that is *listing*-level, and the
competitive question is about *sellers*. Aggregating accrual to the seller
(29,835 distinct sellers) changes nothing — Gini among trading sellers
**0.637 (2021) → 0.618 (2023) → 0.651 (2024)**, top-decile share of seller
accrual 51.5% → 50.5% → 56.4%, on the same 2024-only pattern. Listings per seller
in frame is flat at 1.09–1.15, though that number is a property of the quota
sample rather than of Fiverr.

### 3.5 Sellers stopped raising prices — they did not start cutting them

This is the one new fact in this assembly (step 51), and it is the seller-conduct
counterpart to the price level in §1. Consecutive-quarter pairs for the same
listing, balanced panel, pre (2020Q4–2022Q3) vs post (2022Q4–2023Q4):

| | pre | post |
|---|---:|---:|
| share of listing-quarters with any price change | **23.6%** | **18.3%** |
| …an increase | **18.1%** | **12.4%** |
| …a cut | 5.4% | 5.9% |
| mean Δlog price per quarter | **+0.0565** | **+0.0239** |

**The fall in repricing is almost entirely a fall in price increases. Cuts are
flat.** The engine that produced the +78% nominal index throttled back after 2022
without reversing: this is downward nominal rigidity in a market with falling
demand, not a price war. A searched break confirms it is not a ChatGPT event —
the best break for any-change is **2021Q3** and the ChatGPT quarter is
insignificant and *positively* signed; for price cuts the best break is 2022Q3,
one quarter *before* ChatGPT, and the ChatGPT-quarter coefficient is −0.0005.

**Not a coverage artefact.** On a strict panel of **936 listings present in every
quarter** of the balanced window, the same pattern holds — any change 24.1% →
18.1%, increases 18.5% → 12.0%, cuts 5.6% → 6.1% — while observed pairs per
listing move only −1.9% across the break.

A companion measure — the Spearman correlation of a listing's within-category
price rank across four quarters — **rises** (0.898 → 0.940 balanced), i.e. the
price ordering became *more* rigid, the opposite of a technology reshuffling who
can charge what. It is recorded as **not independent evidence**: a listing that
never reprices cannot change rank except through what others do, so rising rank
persistence is the §3.5 fact restated.

### 3.6 One lead, explicitly not a finding

The within-listing price return to reputation is **+11.3% per doubling of reviews
pre-ChatGPT and +18.5% post** on the balanced panel (difference +0.091, t 2.04),
and it clears a placebo split at a false 2021Q2 break (−0.012, t −0.54). If real,
it would say incumbency became more valuable exactly when output became cheap to
produce — the most economically interesting structural claim available here.

**On all 37,888 listings the same difference is +0.0060 (t 0.79), a precise
zero.** A result that appears on 2,750 listings and vanishes on the frame that
contains them is a lead, not a finding, and is recorded as one.

---

## 4. Attribution: six designs, six failures, and what they establish

Nothing above is causally attributed to generative AI, because nothing can be. The
failures are listed with what killed each, because their pattern is itself the
result.

| # | design | step | killed by |
|---|---|---|---|
| 1 | category DiD, HIGH vs LOW exposure | 46 | parallel trends (6/16 pre-period coefficients significant) |
| 2 | trend horse race | 46 | HIGH × POST collapses −7.9% → −0.8% once HIGH × trend enters |
| 3 | CPI-U placebo | 46 | significant (−3.6%, t −2.93) — the design tracks any smooth series |
| 4 | synthetic control + in-space placebos | 48 | translation ranks **last of 7**; p-floor 1/7 = 0.143 by construction |
| 5 | within-category price-tier DiD | 49 | parallel trends (10/11 pre-period coefficients significant); wrong-signed anyway |
| 6 | gig-level continuous exposure (pre-registered) | 50 | trend horse race (sign flip) and CPI-U placebo (t −2.86) |

### 4.1 Why designs 1–4 could never have worked

They share one defect: **seven units.** With seven categories the smallest
attainable one-sided p-value is 1/7 = 0.143, so the test cannot reach 5% no
matter what the data say. That is a property of the design space, not of the
result.

### 4.2 Design 6 is the informative one

It was **pre-registered before any outcome was estimated**
(`plans/active/exposure-continuous-prereg.md`), with five gates whose failure
consequences were fixed in advance. Continuous text-derived exposure at the gig
level, external to our data, with category × quarter fixed effects absorbing
every platform-wide shock.

It is the **first design in the project to pass parallel trends** (Wald χ²(11) =
9.99, p = 0.53; 0 of 11 pre-period coefficients significant). It also passes the
not-a-price-proxy gate and the placebo window. **Three of the four ways the
previous designs died are ruled out.** The primary estimate is −0.168 (t −2.52)
on 121,414 observations, stable across the entire pre-registered robustness grid.

It dies on the fourth: `exposure × trend` is significant (t −2.54) and
`exposure × POST` **flips sign** once it enters, and the CPI-U placebo is
significant at t −2.86. The pre-registered descriptive fallback says the same
thing independently — decile changes run −13.3% to +3.5% with **no monotone
gradient**, and the *least*-exposed decile falls more than the most-exposed.

Three qualifications, so the failure is not overstated: the estimate was
underpowered against its own standard (|β| = 0.90× the realised MDE); the
composition gate failed on power, not sign (balanced-frame β = −0.202, *larger*,
losing significance only because n falls to 1,715 gigs); and the collapsed
difference series returns the opposite sign, which is itself a reason not to read
−0.168 as an effect.

### 4.3 What the six failures jointly establish

**There is an exposure-correlated differential trend that predates ChatGPT, and
there is no break at ChatGPT.** Two independent pieces of §3 agree: the commodity
tier's steepest decline is 2021Q2 (§3.1), and the repricing break is 2021Q3
(§3.5). The structural transformation in this market was already underway before
generative AI was publicly available.

### 4.4 Rival explanations that this data cannot separate from AI

Post-pandemic normalisation (2020–21 was a freelance boom, and the buyer series
peaks exactly at its end); the 2022 rate shock and tech downturn; and Fiverr's own
strategy — Pro, subscriptions, ads, an explicit upmarket push — which predicts
*every* structural fact in §3 as well as an AI account does, and predicts the
2021 timing better.

---

## 5. What is not measurable on this data, at any effort

- **Entry and exit.** `n_404 = 0` across 509,339 captures: the crawl records no
  removals, so nothing here can be labelled entry or exit. This is the single
  largest gap for a competitive-structure question, because entry is how a
  commoditising shock usually shows up first.
- **Realised order value.** §1.3.
- **Anything after 2024Q4** on the structure side. The treatment window is eight
  quarters and stops before the 2025–26 agentic period. (The price index itself
  reaches 2026Q1 on the thinner recent crawl.)
- **Which categories.** Fiverr publishes no category split, and the archive's
  category comparison is not identified (§4).
- **Sales.** `review_count` is a proxy.

---

## 6. What would change the answer, in order of value

1. **O*NET task statements** in place of occupation titles. The current exposure
   measure is both thin (36.8% of gigs get a zero match) and selected (dropped
   gigs accrue 23.7% more pre-period than kept ones). This weakness was declared
   in the pre-registration *before* design 6 ran, precisely so it could not
   become a post-hoc excuse. It is the one input change that alters the treatment
   measure itself.
2. **Reach past 2024Q4** with a live forward crawl. The whole agentic period is
   outside the structure window.
3. **A collection design that records 404s** on a fixed schedule, with manifests
   not selected on survival. That is the only route to entry and exit, and hence
   to the part of competitive structure this data cannot see at all.
4. **Sub-category or gig-population data.** Seven categories caps inference at
   p = 0.143 by construction.

---

## 7. Reader's guide to which claims carry what weight

| claim | status |
|---|---|
| real listed prices +40.7% (±3.7%) over 2020Q1–2026Q1 | measured, published, frozen |
| buyers −36%, spend/buyer +79%, implied orders −18% | external company data + an identity; orders is an upper bound |
| per-gig review accrual broke −13% to −43% at 2022Q4 in all seven categories | measured; direction externally corroborated |
| $5 tier 27.3% → 10.3%, steepest decline 2021Q2 | measured on a balanced panel, break searched |
| three-tier share 82% → 91%, ladder 4.06× → 3.80× | measured on a balanced panel |
| repricing 23.6% → 18.3%, entirely fewer increases; cuts flat | measured on a balanced panel, break searched |
| sales concentration flat among trading listings and trading sellers | measured; the apparent rise is 2024 dormancy at the trailing edge |
| dispersion U-shaped, trough mid-2023 | descriptive only |
| return to reputation rose post-2022 | **lead only** — balanced panel t 2.04, full frame t 0.79 |
| any of this was caused by generative AI | **not identified**; six designs, six failures |
| the price ordering was reshuffled | **rejected** — rank persistence rose |
| the market commoditised | **rejected in sign** on four of five margins |

---

## 8. Provenance

| element | script | output |
|---|---|---|
| price index, categories, bands | `code/21`, `code/23`, `code/30` | `data/pilot/paper-numbers.md` |
| reputation band | `code/27-reputation-band.py` | frozen numbers §2 |
| demand break by category | `code/46-balanced-demand.py` | `runs/phase0-demand.out` |
| Fiverr Inc. transactions | `code/47-fiverr-inc-external.py` | `runs/fvrr-external.out` |
| category attribution (synthetic control) | `code/48-category-impact.py` | `runs/category-impact.out` |
| price distribution, versioning, dispersion, concentration | `code/49-market-structure.py` | `runs/market-structure.out` |
| continuous-exposure design (pre-registered) | `code/50-continuous-exposure.py` | `runs/continuous-exposure.out` |
| repricing, mobility, seller concentration, reputation split | `code/51-seller-structure.py` | `runs/seller-structure.out` |
