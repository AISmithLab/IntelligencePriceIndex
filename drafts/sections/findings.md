## 4. Findings

All figures in this section come from `data/pilot/paper-numbers.md`. Bands are 95% and are reported for every quantity we quote.

### 4.1 Descriptive Statistics

The historical panel comprises **1,066 gigs** across **6,450 gig-quarters**; the recent panel comprises **2,908 gigs** across **8,320 gig-quarters**. Median basic price is **\$20** in the historical panel (IQR \$10–\$50) and **\$25** in the recent panel (IQR \$10–\$75).

| Category | Hist. gigs | Hist. gig-quarters | Hist. median | Recent gigs | Recent gig-quarters | Recent median |
|---|---:|---:|---:|---:|---:|---:|
| Design | 330 | 2,055 | \$20 | 1,466 | 4,236 | \$20 |
| Writing | 229 | 1,325 | \$17.50 | 368 | 1,038 | \$25 |
| Coding | 190 | 1,121 | \$20 | 462 | 1,303 | \$80 |
| Video | 158 | 937 | \$30 | 235 | 710 | \$20 |
| Marketing | 71 | 414 | \$25 | 294 | 809 | \$40 |
| Audio | 62 | 462 | \$15 | 55 | 145 | \$20 |
| Translation | 26 | 136 | \$5 | 28 | 79 | \$10 |

Dispersion within categories is wide—coding spans \$4 to \$7,950—which is precisely why the index matches gigs to themselves rather than comparing category means across periods.

One descriptive fact is worth stating before any index appears, because it sets up the paper's central methodological point. **Raw median posted prices rise steeply over the full archive and the matched index does not follow them.** Medians run \$5 in 2016Q1–Q3, \$10 in 2016Q4–2017Q1, \$20 by 2018Q3–2019Q2 and \$25 by 2019Q3. Almost all of that is the death of Fiverr's "\$5 for everything" floor—an entry-mix and platform-policy change, not a price change for any particular service. Over the same span the matched-model index moves the *other way*. Composition, not price, dominates the raw series.

### 4.2 The Intelligence Price Index, 2020Q1–2026Q1

![Composite Intelligence Price Index](outputs/figures/fig1-composite.svg)

**Figure 3.** The composite index in real terms (headline) and nominal, with the CPI-U reference line and a 95% band on the real series. Base 2020Q1 = 100. ChatGPT's release is marked for reference only; Section 4.8 reports that we cannot attribute any part of the path to it.

Over 2020Q1–2026Q1 the composite index rises from 100 to **140.7 in real terms (+40.7%)** and to **178.4 in nominal terms (+78.4%)**, against CPI-U of **+26.8%**. The 95% band on the composite is **±3.7%** (nominal level 171.8–185.2), the one series in this paper that meets the ±5% adequacy standard of Section 3.6.

The headline result is therefore that **the price of the cognitive services in this basket rose substantially in real terms over six years, and general consumer inflation accounts for roughly 48% of the nominal rise but not the remainder**. We state this as a description of a market, not as an AI result. Section 4.4 measures the rival explanations we can measure; Section 4.8 reports that we cannot identify AI's contribution, and that this is not solely a matter of sample size.

Two features of the path are worth naming.

**There is no reversal.** Earlier versions of this work reported a sharp 2025 decline—a composite peak of 312 falling 21% in early 2025. **That finding was an artifact and is retracted.** It came from two sources, both now removed: the naive chained series described in Section 3.4, and a set of Fiverr landing pages that were not gigs at all whose budget-filter default changed between 2024Q4 and 2025Q1 (Section 3.2, Stage 5b). On the corrected index the recent segment is flat to rising in six of seven categories. Section 4.7 gives the full before-and-after, because the episode is itself a finding about this data source.

**The real series is much flatter than the nominal one, and the gap is not uniform.** Design, the heaviest component, rises **+56.1% nominal but only +23.2% real**—barely above the level a reader would attribute to inflation plus reputation accumulation alone. Reporting only nominal prices would have made the market look roughly two and a half times more dynamic than it was.

### 4.3 Category Trajectories

![Category indices in real terms](outputs/figures/fig2-categories.svg)

**Figure 4.** The seven category indices in real terms, each drawn with its own 95% band, on a common vertical scale and ordered by review weight. Six of the seven miss the ±5% adequacy criterion of Section 3.6 and are marked. The width of these bands, not the ordering of the lines, is the point of the figure.

| Category | Nominal Δ | Real Δ | Real level 2026Q1 | ±95% | Meets ±5% |
|---|---:|---:|---:|---:|:--:|
| Composite | +78.4% | +40.7% | 140.7 | ±3.7% | yes |
| Design | +56.1% | +23.2% | 123.2 | ±4.8% | yes |
| Writing | +101.8% | +59.2% | 159.2 | ±8.3% | no |
| Coding | +150.1% | +97.3% | 197.3 | ±17.1% | no |
| Video | +165.6% | +109.5% | 209.5 | ±11.9% | no |
| Marketing | +194.3% | +132.1% | 232.2 | ±7.7% | no |
| Translation | +199.5% | +136.3% | 236.3 | ±29.2% | no |
| Audio | +222.3% | +154.2% | 254.2 | ±13.9% | no |

**We do not rank these categories, and the table above should not be read as a ranking.** Ordering by the point estimate puts audio first, translation second and marketing third—but their intervals overlap one another *completely*. Audio's real level is 221–292, translation's 190–307, marketing's 214–252. Which of the three is highest is not determined by these data. We verified the overlap pairwise, and we state it here rather than in a footnote because the ordering is exactly the kind of result that gets quoted onward.

**One separation is genuine.** Design (real 117–129) does not overlap audio (221–292), and the gap is far wider than any estimation choice in Section 3.7 moves either series. Design's prices rose much less than audio's. That is the strongest category-level statement this pilot supports.

**Design's precision is not a virtue of the design category.** It has 1,466 recent panel gigs and a median of 208 matched gigs per quarter pair; audio has 55 and a median of 5. The precision ordering tracks matched-gig density almost exactly, and coding—which has eight times audio's panel gigs but fails worse (±17.1% vs ±13.9%)—is the exception that proves the rule, since panel gigs are not what binds.

**The published levels depend on two choices we now report rather than leave to a reader with both files.** The first is the averaging. A Jevons bilateral is the mean of within-gig *log* price ratios, and that distribution is heavily right-skewed: coding's matched 2020Q1→2024Q4 log changes are 0.00, 0.69 and 2.07 at the 20th, 50th and 90th percentiles. The plotted mean-of-logs level (+145% nominal) therefore sits far above the median-of-logs read of **+74%**. This is not outlier contamination — trimming 1% of the tail moves the level by 0.5 index points — it is the entire right tail, and a reader entitled to know the typical gig's experience should be given the median beside the mean. The second is the sampling frame: the same estimator ranks coding **first (+145%) on the balanced frame and fourth (+112%) on the published panel frame**, where audio leads at +259%. Neither is a defect in the estimator. Both are reasons the table above is not a ranking, and they are stronger reasons than the overlapping intervals we gave first.

**At a finer cut, the two most AI-exposed cells are the only two that do not move.** Splitting the seven domains into **35 narrow categories** — each of which clears all 20 quarters at full pair density on the balanced panel — and deflating to real terms gives changes from +3.1% to +155.1% over 2020Q1–2024Q4. Thirty-three of the 35 intervals exclude zero. The two that do not are **subtitling and transcription (+3.1%, 95% CI −11.6% to +20.3%)** and **translation (+5.5%, −2.4% to +14.1%)**: flat real prices in the cell that every published exposure crosswalk ranks most automatable, and the finest cut this project has taken of it.

We flag this as suggestive and decline to read it as an AI effect, for two reasons. There is **no break at the ChatGPT line** in either series — both are flat across the whole window, including the two years before the launch. And the counter-evidence sits inside the same family: `translation · other`, the keyword remainder and the family's largest bucket, rises **+51.2% real (+33.3% to +71.5%)**. A commoditization account has to explain why it stops at the subcategory boundary.

**The historical segment's per-category levels for coding, translation and audio are not reported.** Section 3.7 shows they are not identified: coding's historical terminal level moves +129% on a one-step change in the matching threshold, far outside its own band. We report those three categories only from 2024Q3 forward.

### 4.4 What the Rise Is Not

The composite rises +40.7% in real terms. This section removes what can be removed.

**Reputation accumulation is first-order.** Within a gig, price rises **+7.33% per doubling of cumulative reviews**. The estimate comes from a two-way fixed-effects model on the **balanced panel — 169,337 gig-quarter observations across 15,676 gigs, 2019Q4–2024Q4**, in CPI-deflated real terms, regressing log real price on gig and quarter fixed effects, $\ln(1+R)$ and rating, with gig-clustered errors: $\beta = +0.1021$ (se 0.0039, $t = 25.95$; within-gig $R^2 = 0.135$, residual SD 0.348 log points).

This **replicates the pilot estimate on roughly fifty times the data**. The original pilot regression returned $\beta = +0.1068$ (se 0.0201, $t = 5.32$, 9,762 transitions across 3,419 gigs) — +7.7% per doubling in nominal terms. That the coefficient barely moves when the panel grows from three thousand gigs to fifteen thousand, and when prices are deflated, is the strongest internal validation in the paper. The reputation treadmill is the one first-order quantity here that is precisely estimated.

Two qualifications. The elasticity is **not constant across the review range**: strict log-linearity is rejected, and on the finer taxonomy panel the implied slope tapers from about **+8.1% per doubling at 10 reviews to +4.7% at 5,000**. The pooled coefficient is a fair summary over the mass — the median gig-quarter carries 111 reviews — but it is an approximation to a concave relationship, not a rate. And **linear tenure is not separably identified** from gig and quarter fixed effects, since it decomposes into a gig component and a time component; $\beta$ is identified off curvature in review accumulation, and stripping each gig's own linear trend leaves 45.4% of the within-gig variation and *raises* the coefficient to +0.150 ($t = 30$).

Rebuilding the index on reputation-adjusted prices gives a composite of **+39.7% nominal against +79.0% raw**—a band 39.3 points wide.

![Raw and reputation-adjusted composite](outputs/figures/fig3-reputation-band.svg)

**Figure 5.** The composite published as a band: the raw index above, the reputation-adjusted lower bound below, and beneath them the sensitivity of the full-window change to β. The adjusted line is a bound rather than a correction, and the strip shows why its floor should not be quoted as a single number.

We publish this as a **range, not a correction**, for the reason given in Section 3.8: reviews are cumulative sales, so the adjustment absorbs demand alongside reputation, and if AI suppressed demand it consumes part of what the index is trying to show. The adjustment is largest in the historical segment (writing −27%, translation −26%, marketing −21% at 2024Q3) and small in the recent one (−3% to −4%), simply because seven quarters allow little review accumulation. And the floor is soft: across $\beta$'s own confidence interval the adjusted bound ranges from about +50% to +28%. The honest summary is that **somewhere between a third and all of the real rise may be reputation rather than price**, and this pilot cannot narrow that further.

**General inflation accounts for roughly 48% of the nominal rise** and is removed in the headline (Section 3.5).

**Composition does not explain it, but survivorship may.** The matched design holds the gig fixed, so entry mix cannot drive the result. But the panel follows ageing incumbents, and **new gigs entering with ≤10 reviews show flat prices from 2019 to 2025** in design, writing, video and marketing while the incumbent index rises 47% to 167%. We cannot currently reconcile the two series—the historical and recent crawls return different entry medians for the same year (2024: \$50 on n=102 versus \$30 on n=2,389), so the comparison must be made within a crawl or the frames reconciled—and we therefore report the gap as an open problem rather than a decomposition. It is the paper's most serious unresolved threat, and Section 6 says why.

Taken together: of a **+78.4% nominal** rise, CPI-U accounts for about half, reputation accumulation for a substantial and imprecisely bounded further share, and the residual—which is what an AI account would have to explain—is smaller than the headline and is not separately identified.

### 4.5 The Quantity Margins, and Why We Report Nulls

Price is only one margin. If AI reduced demand for a category, we would expect it in sales volume or in gigs going dormant before we saw it in posted prices. Cumulative `review_count` gives a usable sales proxy: coverage is **88.7% (historical) and 90.7% (recent)** after the Stage 5b exclusion, and the series is effectively monotone—only 0.4% and 0.1% of within-gig transitions decrease—so its accrual rate is a demand series.

**Demand: null in every category, with a bound.** A within-gig interrupted time series on reviews accrued per quarter (gig fixed effects, linear trend, post-2022Q4 indicator, gig-clustered errors; 4,874 transitions, 887 gigs) returns nothing significant: translation −18%, design −11%, writing −3%, coding −2%, marketing +12%, audio +13%, video +24% of pre-period rate, all $|t| < 1.1$. The **minimum detectable break** ranges from **±23% (coding) to ±66% (translation)**, with audio, writing and design at ±27–28%.

The bound is the deliverable, not the null. **No category's sales rate broke by more than roughly a quarter to two-thirds** after ChatGPT. That is a real constraint on how large an effect could be hiding, and it is not evidence of no effect.

**Dormancy: the raw ranking looked like the AI story and did not survive adjustment.** The share of gig-quarters with zero review accrual rose pre-to-post by writing +6.1pp, marketing +5.6, audio +5.0, translation +5.0, while coding (−0.8), video (−1.7) and design (−2.3) fell—an ordering that lines up suspiciously well with text-deliverable exposure. Under the same trend- and composition-adjusted specification, marketing (+7.9, $t = 1.35$), audio (+7.8, $t = 1.68$) and writing (+4.5, $t = 1.27$) stay on top but **nothing reaches significance and translation flips sign** (−0.6). Dormancy rises with gig age and the post window is simply later. **The raw ranking must not be quoted.**

**Pooling does not buy back the power.** Contrasting high-exposure categories (writing, translation, marketing—text deliverable, specified before looking) against low (audio, coding, design, video) with gig and quarter fixed effects gives a demand-rate effect of **+28.7% [−2.9%, +60.4%]**—wrong-signed, with high-exposure categories accruing *more* reviews after ChatGPT—and a dormancy effect of **+32.6% [−17.2%, +82.4%]**. Both groups are treated, so this is a contrast rather than identification.

**Entry and exit are not measurable from this data at all**, and this is a constraint of crawl design rather than of sample size. A gig's absence in a Wayback-derived crawl means "not archived," not "taken down," so no exit hazard is estimable. Worse, the recent manifest requires at least one snapshot in a trailing window, so the recent panel **conditions on survival by construction**: 36.5% of its gigs are last seen in the final quarter against 0.4% in the historical panel. Entry is truncated at both window edges—**1,747 of 2,930 recent-panel gigs are "first captured" in the manifest's first quarter and 5 in its last**—so the apparent entry profile runs from ~100% to ~0% mechanically. We report this as a closed question and give the fix in Section 6.

### 4.6 What Buyers Actually Paid

Every figure to this point is a **posted** price. Section 6.5 lists that as a limitation of the instrument, and it is the one limitation this pilot can now partially answer. Fiverr's gig pages embed a `reviews` object in which each entry is dated by **order** date and carries the price band the buyer paid. Nothing in the pipeline had read those fields at scale.

Rescanning the **397,698 stored captures** already on disk and deduplicating on `encrypted_order_id` recovers **681,668 distinct realised orders**, of which **617,456** fall in 2022Q1–2026Q1. This required no new collection, and it is therefore unaffected by the archive failures of Section 4.9 — the orders were inside HTML retrieved years earlier.

**The obvious way to use them is wrong, and the error is large enough to report before the result.** Plotting the share of orders in each published band shows orders under \$50 rising from near zero in 2022–23 to roughly **54% of the market by 2025** — a collapse in realised value arriving almost exactly on the AI timeline. It is an artifact, twice over.

First, **sub-\$50 orders carried no band at all before roughly 2024Q2**. In 2022Q3, 46% of orders have no price field and the cheapest band that exists is `$50-$100`; by 2024Q3 missingness is ~0% and `$0-$50` alone is 50% of orders. The apparent `<$50` share tracks *coverage*, not price: 54–67% coverage returns a 0–13% share, 94% coverage returns 42%, and 100% coverage returns ~50%. Second, **the labels themselves changed**: `$5-$20` and `$20-$50` disappear and `$0-$50` appears at the same moment, so any bin built on published labels straddles a break.

We therefore condition on orders of **\$50 or more**, where the boundaries 50/100/200/400/800 exist unchanged in every era, and report composition within that segment.

| Quarter | n (\$50+) | Gigs | \$50–100 | \$100–200 | \$200–400 | \$400–800 | \$800+ | Median bin |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2022Q1 | 25,687 | 8,654 | 35.7% | 32.9% | 19.4% | 8.5% | 3.6% | \$100–200 |
| 2022Q3 | 28,336 | 9,716 | 39.5% | 32.0% | 18.1% | 7.0% | 3.4% | \$100–200 |
| 2023Q1 | 27,075 | 9,385 | 39.4% | 32.4% | 18.4% | 7.0% | 2.9% | \$100–200 |
| 2023Q3 | 29,250 | 9,736 | 38.3% | 32.5% | 18.6% | 7.5% | 3.0% | \$100–200 |
| 2024Q1 | 22,136 | 8,385 | 36.8% | 32.5% | 19.3% | 8.0% | 3.4% | \$100–200 |
| 2024Q3 | 40,393 | 12,352 | 40.7% | 31.0% | 17.9% | 7.2% | 3.3% | \$100–200 |
| 2025Q1 | 4,483 | 2,368 | 40.3% | 29.9% | 17.8% | 8.2% | 3.9% | \$100–200 |
| 2025Q3 | 3,474 | 1,725 | 39.4% | 30.6% | 17.6% | 7.8% | 4.6% | \$100–200 |
| 2026Q1 | 420 | 253 | 40.5% | 29.3% | 16.9% | 8.1% | 5.2% | \$100–200 |

*Alternate quarters shown; the full 17-quarter series is in Appendix A.*

<!-- FIGURE: stacked-area chart of the five $50+ bands, 2022Q1-2026Q1, with the median-bin line overlaid and the post-2024Q3 thinning of n marked -->

**On a stable band scheme the series is flat.** The median bin is **\$100–200 in all seventeen quarters**. Over the full window the composition drifts by \$50–100 **+4.8pp**, \$100–200 **−3.6pp**, \$200–400 **−2.5pp**, \$400–800 **−0.4pp** and \$800+ **+1.6pp** — a mild hollowing of the middle with both tails thickening slightly, not a decline in what buyers pay.

**This is a second, independent non-result, and it is the one that matters most.** The listed-price exposure model of Section 4.8 returns a silence on posted prices. Realised order values on a stable band scheme are flat across the same window, over a different price object, a different sample construction, and a set of gigs the listed-price panel does not follow. A claim that generative AI produced a collapse in the realised price of this work now has to explain this table first.

Four limits travel with the series and none of them are small.

- **It says nothing about the sub-\$50 segment**, which is roughly half of all orders and is unmeasurable before 2024. That is precisely the thin, cheap end a commoditization hypothesis is about, so the series is silent on the segment where an effect is most expected.
- **It is a sample of each gig's orders, not a census.** A page displays about 4 of a median 124 reviews, ranked by Fiverr's own `relevancy_score`. A direct test finds no *price* selection in that ranking (late minus early +0 USD), but the bootstrap interval on that test is degenerate on band discreteness and must not be quoted as precision. Display selection remains the central untested threat.
- **The gig set changes every quarter** and thins sharply after 2024Q3, from 40,393 orders in 2024Q3 to 420 in 2026Q1. The later quarters are noisier, not merely smaller, and the 2026 column rests on 253 gigs.
- **This is not the IPI and must never be chained onto it.** The IPI is a matched-model index on listed basic-package prices; this is a composition series on realised, banded values over a changing set of gigs. Different object, different unit, no splice.

### 4.7 What the Non-Gig Exclusion Changed

The Stage 5b exclusion (Section 3.2) removed 10.2% of observations and moved every headline figure. We report the before-and-after in full, because a reader assessing an archival price index needs to know how large a plausible-looking parsing defect can be.

| | Before | After |
|---|---:|---:|
| Composite, nominal | +44.7% | **+78.4%** |
| Composite, real | +14.1% | **+40.7%** |
| Inflation's share of nominal rise | ~68% | ~48% |
| Recent panel gigs | 3,566 | 2,908 |

The recent segment inverted from falling to flat-or-rising in **six of seven categories** (2024Q3 = 100, at 2026Q1): audio 60.6 → 104.9, coding 78.5 → 121.4, writing 75.6 → 108.5, marketing 77.6 → 109.9, design 91.4 → 106.4, translation 120.8 → 131.5; video (83.3 → 96.9) remains below 100.

Two things corroborate the fix rather than merely following from it. **Bootstrap standard errors narrowed in five of seven categories**—audio 0.155 → 0.071 (−54%), writing −51%, marketing −49%, design −35%—so the removed rows were injecting variance, not carrying signal. And the **historical panel outputs were byte-identical** before and after, which is the independent confirmation that the defect was confined to the recent crawl, exactly as the URL-family diagnosis predicted.

### 4.8 What We Cannot Determine

The question this project set out to answer is which categories AI has most affected. **At pilot scale we cannot answer it on any margin**, and we regard stating that clearly as part of the contribution.

- **Price** is imprecise in six of seven categories (±7.7% to ±29.2%) and confounded by reputation and inflation, both of which are first-order.
- **Demand and dormancy** are null with minimum detectable effects of ±23% to ±66%.
- **Entry and exit** are unmeasurable by crawl construction.
- **The one design that would identify an effect is underpowered rather than invalid.** A gig-level continuous-exposure difference-in-differences—scoring gigs on whether a general-purpose model could produce the deliverable end to end, with category × quarter fixed effects absorbing every platform- and category-wide shock—**passes its parallel-trends test**: the pre-period placebo returns $\beta = -0.0082$ (se 0.0093), and every pre-year in an event study is insignificant (2019 +0.017, 2020 −0.042, 2022 +0.003). This is a genuine contrast with a category-level design, where pre-trends run from −38%/yr to +13%/yr and parallel trends fails outright. But the estimate is $\beta_1 = +0.0147$ (se 0.0126, $t = 1.17$), and over the eight quarters 2023Q1–2024Q4 the 95% interval on the high-versus-low contrast spans **−14.8% to +87.6%**. It is robust to a binary contrast (+0.031), a leaner exposure lexicon (+0.012) and leave-one-category-out (+0.006 to +0.020)—robustly uninformative. The interval is wider than every effect this paper reports.

**The pre-registered exposure model, estimated at panel scale, is a silence rather than a zero.** The design above was built on the pilot. We re-estimate the pre-registered specification on the full balanced panel — **169,337 gig-quarter observations across 15,676 gigs, 2019Q4–2024Q4**, in real terms — regressing log real price on gig and quarter fixed effects, reputation, rating, and the interaction of Eloundou human-annotated occupational exposure with a post-2022Q4 indicator, clustering on gig.

| Term | Coef | SE | $t$ | 95% CI |
|---|---:|---:|---:|---|
| Exposure × Post | **−0.0333** | 0.0246 | −1.35 | [−0.0814, +0.0149] |
| $\ln(1+\text{reviews})$ | +0.1020 | 0.0039 | +25.92 | [+0.0943, +0.1097] |
| Rating | +0.0988 | 0.0351 | +2.81 | [+0.0300, +0.1677] |

Exposure runs from 0.25 (audio) to 0.84 (translation), so the coefficient scales to a **−1.95%** real-price gap between the least and most exposed category after the launch. **We report this as a non-result, and the pre-registered diagnostics say it is a weak one.** Of six gates specified in advance, three fail:

| Gate | Result | Verdict |
|---|---|:--|
| A · Parallel trends | 4 of 11 pre-launch interactions significant | **FAIL** |
| B · Linear-trend race | Adding Exposure × trend moves the estimate to **+0.0358** ($t$ +1.38) — the sign flips | **FAIL** |
| C · Placebo break (2021Q2) | −0.0595 ($t$ −1.78) | PASS |
| D · First differences | +0.0081 ($t$ +0.59) on 153,661 within-gig changes | **FAIL** |
| E · Inference | Gig-clustered SE 0.0246 vs unclustered 0.0121 — clustering inflates it 2.03× | reported clustered |
| F · Power | MDE at 80% power is **0.0689** log points; the estimate is 0.0333 | **below MDE** |

Gate F is the one that governs the reading. **The point estimate is smaller than the minimum effect the design could detect**, so the interval does not exclude an effect of up to roughly ±4.2% across the exposure spread. This is a silence, not a zero, and it must not be cited as evidence that AI had no effect on these prices. Gate B is the more damaging failure: whatever `Exposure × Post` was picking up, a single linear trend per exposure level explains it better.

**Extending the window into the recovered 2025 data does not move it.** Pooling the 2025 archival refresh with the balanced panel and re-estimating through 2025Q4 — **172,934 observations across 15,864 gigs** — returns `Exposure × Post` = **−0.0324** ($t$ −1.31), against −0.0333 ($t$ −1.35) on the shorter window. Every gate behaves identically, including the sign flip under a trend. Four additional quarters of data, collected specifically to extend the right edge, changed the third decimal place. That is worth stating plainly: **the null here is not a window artifact of ending in 2024Q4**, and adding data at this rate will not resolve it.

**One exploratory specification looks like a large effect and is not one.** A market-measured exposure variable — the share of a category's listings that brand themselves as AI services, varying by category *and* quarter — enters at **+1.2888** ($t$ +11.23), implying **+13.76%** in real price per 10pp rise in AI-branded share, with a tight interval. Adding one linear trend per category moves it to **+0.0727** ($t$ +0.84), and the 10pp effect from +13.76% to **+0.73%**. Because the regressor varies at the category-by-quarter level it absorbs any category-specific time path, AI-driven or not. We report it because it is an obvious specification to attempt on data of this kind and it is badly wrong; the general rule — **any category-by-quarter regressor must be raced against category-specific trends before it is believed** — is applied to every such specification in this paper.

Six independent routes now converge on the same conclusion: price precision, the quantity margins, the pilot difference-in-differences interval, the pre-registered exposure model at panel scale, the flat realised-value series of Section 4.6, and the retracted elasticity regression of Section 3.9.

**We stated in earlier drafts that the binding constraint was sample size rather than estimator choice. The panel-scale results require us to qualify that.** Sample size is still what defeats the *category ranking*, and it is still what the collection requirements of Section 6 address. But it is no longer a sufficient account of the exposure null. Fifty times the pilot's data leaves the estimate below the minimum detectable effect, and four further quarters move it by 0.0009. More decisively, the pre-registered design fails parallel trends and reverses sign against a linear trend — failures of *identification*, which more of the same data does not repair. The honest statement is that this design cannot separate an AI effect from a category-specific trend on this platform, and that a larger version of the same design would inherit the same defect. What Section 6 specifies is therefore not merely a bigger crawl but a different one, and the case for a genuine control group — categories no capability improvement should touch — is now the binding requirement rather than a refinement.

### 4.9 The Observation Window Is Closing

The instrument this paper builds depends on a third party continuing to archive a commercial website. Over the period of this study that stopped being true, and we report the failure quantitatively because it bears on whether anyone can answer this question from archival data at all.

**The archive's coverage of Fiverr degrades sharply from 2025 and is effectively closed by 2026.** Requests to the Internet Archive's index return HTTP 403 at a rate that rises monotonically through the window. Measured on 79,853 index records:

| Quarter | Captures | 403 share | Status 200 | Distinct gig pages |
|---|---:|---:|---:|---:|
| 2025Q4 | 12,601 | 1.0% | 2,239 | 940 |
| 2026Q1 | 9,734 | 18.1% | 1,180 | 563 |
| 2026Q2 | 1,204 | **89.3%** | 9 | **1** |
| 2026Q3 | 1,209 | 59.1% | 152 | 50 |

The archive kept requesting the site throughout and was refused. Capture volume falls roughly eightfold across the same span, so **the right edge of any archival panel loses twice** — fewer pages requested, and a smaller share of those returned.

**A matched-model index fails before the raw capture count does.** A bilateral comparison needs the same gig priced in two adjacent quarters, which is a far stricter requirement than a capture. The revisit rate — the share of captured gigs seen again in an adjacent quarter — runs **74–82% and flat for 2018 through 2024, then falls to 44.1% in 2025 and 34.5% in 2026**. In the recovered 2025 refresh, **22,947 of 24,345 gigs (94.3%) are priced in exactly one quarter** and only 884 carry an adjacent pair. This is not collection failure: the underlying manifest contains only 893 such pairs, so **99.0% of what was recoverable was recovered**. With 2026Q2 holding a single gig-shaped successful capture against 2026Q3's fifty, adjacent-quarter matched pairs for 2026 are approximately zero at any collection effort.

**A full re-collection of the 2025–2026 window confirmed the ceiling rather than raising it.** We collected 35,938 additional pages at 100.0% extraction. All-category matched pairs at 2025Q1→Q2 rose from 1,093 to 1,285 — a factor of **1.12, against a projected 1.83** — and across the seven published domains from 34,164 to 34,433, a factor of **1.01**. No figure in this paper moves. The projection had been right about the level and wrong about the gain, because most of the pairs it forecast were already on disk.

**The obvious alternative source does not exist.** Common Crawl, which we had not previously tested, returns a single index block for `fiverr.com/*` in August 2026, August 2025 *and* August 2024, and its only successful responses are `robots.txt`. Common Crawl never crawled Fiverr gig pages. We record this so it is not re-attempted.

Two consequences follow, and they point in opposite directions.

The first is a **scope restriction we now impose on the paper's own claims**. Category-level results are identified through 2024Q3 and the composite through 2024Q4; the 2025 and 2026 points on any series in this paper rest on matched-pair counts an order of magnitude thinner than the quarters before them, and should be read as continuity checks rather than measurements. Section 6.1 restates the precision requirement accordingly.

The second is that **the window closed at almost exactly the moment the question became answerable**. In-market AI diffusion on this platform dates to 2023Q1, so the archive supports roughly six quarters of post-treatment observation on a treatment that had barely spread — which is an alternative reading of every null in Section 4.8, and one we cannot distinguish from a true absence of effect. That the historical record of a commercial market becomes unavailable precisely when researchers need it is a finding about the infrastructure of economic measurement, not merely an inconvenience for this study. It is also the strongest available argument for the prospective collection design of Section 6.3: a fixed-schedule panel begun today is the only instrument that observes what the archive can no longer reach.
