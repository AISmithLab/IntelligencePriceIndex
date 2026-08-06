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

**Figure 3.** The composite index in real terms (headline) and nominal, with the CPI-U reference line and a 95% band on the real series. Base 2020Q1 = 100. ChatGPT's release is marked for reference only; Section 4.7 reports that we cannot attribute any part of the path to it.

Over 2020Q1–2026Q1 the composite index rises from 100 to **140.7 in real terms (+40.7%)** and to **178.4 in nominal terms (+78.4%)**, against CPI-U of **+26.8%**. The 95% band on the composite is **±3.7%** (nominal level 171.8–185.2), the one series in this paper that meets the ±5% adequacy standard of Section 3.6.

The headline result is therefore that **the price of the cognitive services in this basket rose substantially in real terms over six years, and general consumer inflation accounts for roughly 48% of the nominal rise but not the remainder**. We state this as a description of a market, not as an AI result. Section 4.4 measures the rival explanations we can measure; Section 4.5 reports that we cannot identify AI's contribution at this sample size.

Two features of the path are worth naming.

**There is no reversal.** Earlier versions of this work reported a sharp 2025 decline—a composite peak of 312 falling 21% in early 2025. **That finding was an artifact and is retracted.** It came from two sources, both now removed: the naive chained series described in Section 3.4, and a set of Fiverr landing pages that were not gigs at all whose budget-filter default changed between 2024Q4 and 2025Q1 (Section 3.2, Stage 5b). On the corrected index the recent segment is flat to rising in six of seven categories. Section 4.6 gives the full before-and-after, because the episode is itself a finding about this data source.

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

**The historical segment's per-category levels for coding, translation and audio are not reported.** Section 3.7 shows they are not identified: coding's historical terminal level moves +129% on a one-step change in the matching threshold, far outside its own band. We report those three categories only from 2024Q3 forward.

### 4.4 What the Rise Is Not

The composite rises +40.7% in real terms. This section removes what can be removed.

**Reputation accumulation is first-order.** Within a gig, price rises **+7.7% per doubling of cumulative reviews** ($\beta = +0.1068$, se 0.0201, $t = 5.32$, gig-clustered, 9,762 transitions across 3,419 gigs). Rebuilding the index on reputation-adjusted prices gives a composite of **+39.7% nominal against +79.0% raw**—a band 39.3 points wide.

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

### 4.6 What the Non-Gig Exclusion Changed

The Stage 5b exclusion (Section 3.2) removed 10.2% of observations and moved every headline figure. We report the before-and-after in full, because a reader assessing an archival price index needs to know how large a plausible-looking parsing defect can be.

| | Before | After |
|---|---:|---:|
| Composite, nominal | +44.7% | **+78.4%** |
| Composite, real | +14.1% | **+40.7%** |
| Inflation's share of nominal rise | ~68% | ~48% |
| Recent panel gigs | 3,566 | 2,908 |

The recent segment inverted from falling to flat-or-rising in **six of seven categories** (2024Q3 = 100, at 2026Q1): audio 60.6 → 104.9, coding 78.5 → 121.4, writing 75.6 → 108.5, marketing 77.6 → 109.9, design 91.4 → 106.4, translation 120.8 → 131.5; video (83.3 → 96.9) remains below 100.

Two things corroborate the fix rather than merely following from it. **Bootstrap standard errors narrowed in five of seven categories**—audio 0.155 → 0.071 (−54%), writing −51%, marketing −49%, design −35%—so the removed rows were injecting variance, not carrying signal. And the **historical panel outputs were byte-identical** before and after, which is the independent confirmation that the defect was confined to the recent crawl, exactly as the URL-family diagnosis predicted.

### 4.7 What We Cannot Determine

The question this project set out to answer is which categories AI has most affected. **At pilot scale we cannot answer it on any margin**, and we regard stating that clearly as part of the contribution.

- **Price** is imprecise in six of seven categories (±7.7% to ±29.2%) and confounded by reputation and inflation, both of which are first-order.
- **Demand and dormancy** are null with minimum detectable effects of ±23% to ±66%.
- **Entry and exit** are unmeasurable by crawl construction.
- **The one design that would identify an effect is underpowered rather than invalid.** A gig-level continuous-exposure difference-in-differences—scoring gigs on whether a general-purpose model could produce the deliverable end to end, with category × quarter fixed effects absorbing every platform- and category-wide shock—**passes its parallel-trends test**: the pre-period placebo returns $\beta = -0.0082$ (se 0.0093), and every pre-year in an event study is insignificant (2019 +0.017, 2020 −0.042, 2022 +0.003). This is a genuine contrast with a category-level design, where pre-trends run from −38%/yr to +13%/yr and parallel trends fails outright. But the estimate is $\beta_1 = +0.0147$ (se 0.0126, $t = 1.17$), and over the eight quarters 2023Q1–2024Q4 the 95% interval on the high-versus-low contrast spans **−14.8% to +87.6%**. It is robust to a binary contrast (+0.031), a leaner exposure lexicon (+0.012) and leave-one-category-out (+0.006 to +0.020)—robustly uninformative. The interval is wider than every effect this paper reports.

Four independent routes—price precision, the quantity margins, the difference-in-differences interval, and the retracted elasticity regression of Section 3.9—converge on the same conclusion, and they fail for the same reason. **The binding constraint is sample size and crawl design, not estimator choice.** No amount of further estimation on this pilot will produce a category ranking, and Section 6 specifies the collection that would.
