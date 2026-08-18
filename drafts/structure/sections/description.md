## 3. The five predictions, tested

We state the commoditisation hypothesis as five directional predictions and take
each to the data in turn. Every claim below is read off a fixed or balanced
panel; every break date is **searched, not assumed**; and each candidate finding
was run against a guard capable of destroying it, in the same script that
produced it. Across the two analysis scripts, **eleven candidate findings were
generated and seven were killed by their own guards** [CITE-lock].

| # | prediction | verdict | evidence |
|---|---|---|---|
| P1 | prices fall | **rejected in sign** | real listed prices **+40.7%** (±3.7%) |
| P2 | quantities rise | **rejected in sign** | buyers **−36%** from peak; implied orders −18% vs 2020 |
| P3 | the cheap tier widens | **rejected in sign; and mis-timed** | \$5 tier 27.3% → 10.3%, steepest decline **2021Q2** |
| P4 | price competition intensifies | **rejected in sign** | repricing 23.6% → 18.3%, *entirely* fewer increases |
| P5 | sales concentrate | **rejected** | Gini flat among trading listings **and** trading sellers |

### 3.1 P1 — Prices rose, in real terms, in every category

Matched-model index, 2020Q1 = 100, terminal 2026Q1 [CITE-ipi]:

| series | nominal | real | real Δ | ±95% |
|---|---:|---:|---:|---:|
| **composite** | 178.4 | 140.7 | **+40.7%** | ±3.7% |
| design | 156.1 | 123.2 | +23.2% | ±4.8% |
| writing | 201.8 | 159.2 | +59.2% | ±8.3% |
| marketing | 294.3 | 232.2 | +132.1% | ±7.7% |
| coding | 250.1 | 197.3 | +97.3% | ±17.1% |
| video | 265.6 | 209.5 | +109.5% | ±11.9% |
| audio | 322.3 | 254.2 | +154.2% | ±13.9% |
| translation | 299.5 | 236.3 | +136.3% | ±29.2% |

CPI-U over the same window is +26.8%.

**The categories may not be ranked.** Six of seven miss the ±5% precision
standard the index paper sets, and the top three intervals overlap completely.
Translation — the *most* AI-exposed category on the pre-registered measure
(β 0.840) — carries a ±29.2% band on 28 panel listings. Any claim of the form
"AI hit translation hardest" is unsupported by these data whichever way it points.

**What the rise is made of.** Roughly half the nominal increase is general
inflation. A large further share is reputation accumulation: within a listing,
price rises **+7.7% per doubling of cumulative reviews**, and rebuilding the
index on reputation-adjusted prices gives a composite band of **+39.7% to
+79.0%** whose floor is itself imprecise (moving between about +50% and +28%
across β's own confidence interval). The residual is not attributed; see §4.

### 3.2 P2 — Quantities fell, and the decline is externally corroborated

| period | buyers (M) | \$/buyer | GMV (\$M) | buyers YoY |
|---|---:|---:|---:|---:|
| 2020 | 3.40 | 205 | 699 | +44.7% |
| 2021 | **4.20** | 242 | 1,020 | +23.5% |
| 2022 | 4.20 | 262 | 1,090 | **+0.0%** |
| 2023 | 4.10 | 278 | **1,140** | −2.4% |
| 2024 | 3.60 | 302 | 1,087 | −12.2% |
| 2025 | 3.10 | 342 | 1,060 | −13.9% |
| 2026 TTM-Q2 | **2.70** | 368 | 994 | −12.9% |

Buyers peaked in 2021 and are **−36%**; GMV is only −12.8% from its peak. The
entire gap is spend per buyer, which rose *every single year* from \$119 (2017)
to \$368. **Fewer, larger buyers.** Deflating GMV by CPI-U and dividing by the
real index gives real GMV +11.3% against real price +35.8%, hence implied
**orders −18.0% versus 2020 and −38.6% from the 2021 peak** — an upper bound on
the decline, per §2.6.

Within the archive, quarterly review accrual per listing breaks sharply at 2022Q4
in **all seven categories** (listing FE + linear trend, listing-clustered SEs):
writing −42.9% (t −23.00), translation −37.2%, audio −35.5%, coding −35.2%,
video −28.6%, marketing −23.7%, design −13.1% (t −6.65). Note already that the
*least* exposed category of the seven (audio, β 0.248) has the third largest
fall — §4 returns to this.

The two sources are independent in the way that matters: a fall in the archive's
review accrual could have been reviewing behaviour rather than transactions,
whereas the operator's buyer and GMV series have nothing to do with reviewing.
They fall together, so the **direction** is corroborated. The magnitudes differ
(−18% platform-wide against −13% to −43% per surviving listing), which is
informative rather than fatal: per-listing accrual falls faster than platform
orders if the listing population grew. That population question is unanswerable
here, because exit is unmeasurable (§2.6).

### 3.3 P3 — The cheap tier did empty, but the timing rejects an AI account

Share of listings at each price point, fixed panel:

| | 2019Q3 | 2024Q4 |
|---|---:|---:|
| \$5 tier | **27.3%** | **10.3%** |
| \$100+ | 15.6% | 22.4% |
| median listed price | \$15 | \$30 |

On all listings the \$5 tier runs 32.0% → 11.4%. This is the one prediction whose
*sign* is right: the commodity end of the market genuinely hollowed out.

**The date is wrong for AI.** With the break date searched rather than assumed,
on the balanced panel:

- the steepest trend break is **2021Q2**;
- the ChatGPT quarter carries the **opposite sign**;
- the decline **slows** after 2022Q4.

Assuming 2022Q4 returns a significant coefficient and would have produced exactly
the headline the hypothesis predicts. The form matters as much as the date: the
series is a decline whose slope changes, not a step, so a level-shift search
reports curvature and picks an endpoint (2023Q1) while a trend-break search
answers the question asked. Both are reported.

### 3.4 P4 — Sellers stopped raising prices; they did not start cutting

Consecutive-quarter pairs for the same listing, balanced panel, pre
(2020Q4–2022Q3) against post (2022Q4–2023Q4):

| | pre | post |
|---|---:|---:|
| any price change | **23.6%** | **18.3%** |
| …an increase | **18.1%** | **12.4%** |
| …a cut | 5.4% | 5.9% |
| mean Δlog price per quarter | **+0.0565** | **+0.0239** |
| mean \|Δlog price\| given change | 0.454 | 0.405 |

**The entire fall in repricing is a fall in price increases.** Cuts are flat.
The engine that produced the nominal index throttled back after 2022 without
reversing: downward nominal rigidity in a market with falling demand, not a price
war.

**This is not thinning capture coverage.** The 80%-coverage panel still permits
a listing to be missing in up to 3 of 14 quarters, so the fall could in principle
be a measurement artefact. On a **strict panel of 936 listings present in every
quarter of the window**, where coverage cannot vary, the same pattern holds:
any change 24.1% → 18.1%, increases 18.5% → 12.0%, cuts 5.6% → 6.1%. Observed
pairs per listing move −1.9% across the break, which is far too small to generate
a 5.3-point fall.

And again the timing is not ChatGPT's. Searching the break date on the balanced
panel, the best break for "any change" is **2021Q3** (coefficient −0.0429,
t −5.23), while the ChatGPT quarter is insignificant and *positively* signed
(t 1.90). For price cuts the best break is 2022Q3 — one quarter *before* ChatGPT
— and the ChatGPT-quarter coefficient is −0.0005.

A companion measure points the same way and is reported as *not* independent
evidence: the Spearman correlation of a listing's within-category price rank
across four quarters **rises** (0.898 → 0.940, balanced panel), i.e. the price
ordering became *more* rigid, the opposite of a technology reshuffling who can
charge what. Because a listing that never reprices cannot change rank except
through what others do, this is the repricing fact restated rather than a second
one.

### 3.5 P5 — Sales did not concentrate, at listing level or at seller level

The Gini of quarterly review accrual across listings rises 0.63 → 0.75, which
looks like a winner-take-all result and is not one. The Gini **among listings
with any accrual** is flat: 0.64 (2021) → 0.61 (2023). The entire rise is the
zero-accrual share, and that rises only in 2024 — the trailing edge where
captures collapse from ~9,300 to ~700 per quarter. It is dormancy at the edge of
the crawl.

The obvious objection is that this is the wrong unit: a seller may run several
listings, so listing-level concentration would understate seller-level
concentration. Aggregating accrual to the seller (29,835 sellers) changes
nothing:

| | 2021 | 2022 | 2023 | 2024 |
|---|---:|---:|---:|---:|
| Gini across all sellers | 0.666 | 0.660 | 0.646 | 0.713 |
| Gini among **trading** sellers | 0.637 | 0.625 | **0.618** | 0.651 |
| top-decile share of seller accrual | 51.5% | 50.6% | 50.5% | 56.4% |
| listings per seller (in frame) | 1.14 | 1.15 | 1.09 | 1.11 |

Same flat series, same 2024-only rise, same trailing-edge explanation. A null
that survives its strongest objection is a result, and is reported as one.

### 3.6 What did change: product lines got deeper

Two structural facts move, and neither is predicted by commoditisation. Fixed
panel, 2019Q3 → 2024Q4: the share of listings offering three tiers rises
**82.1% → 90.6%**, while the premium/basic ratio among three-tier listings
compresses **4.06× → 3.80×**. Sellers version more, and spread their own menu
less widely.

Price dispersion falls and then partly recovers — sd of log price 1.428 (2019Q3)
→ 1.150 (2023Q3) → 1.233 (2024Q4). This is **descriptive only**: the attempt to
convert it into a price-convergence result is one of the six failures in §4.

### 3.7 One lead we decline to report as a finding

The within-listing price return to reputation is **+11.3% per doubling of reviews
before 2022Q4 and +18.5% after** on the balanced panel (difference +0.091,
t 2.04), and it clears a placebo split at a false 2021Q2 break (−0.012, t −0.54).
If real, it would be the most economically interesting claim available here:
incumbency becoming more valuable exactly as output became cheap to produce.

**On all 37,888 listings the same difference is +0.0060 (t 0.79) — a precise
zero.** A result that appears on 2,750 listings and vanishes on the frame that
contains them is a lead, not a finding. Its promotion rule is fixed in advance
[CITE-lock]: it becomes reportable only if significant on a frame not selected on
panel balance.
