## 3. Data and Methods

All figures here and in Section 4 come from one frozen table, `data/pilot/paper-numbers.md` (`code/30-freeze-numbers.py`); no section recomputes its own. Two companion documents carry the detail this section compresses: **`drafts/data-collection.md`**, the complete collection record, and **Appendix A**, the estimation diagnostics.

*Terminology.* In §3.1–3.2, **index** unqualified means the Wayback Machine's capture index — its catalogue of archived pages; from §3.3 it means the price index we estimate. **Pilot** means the 500-seller crawl of §3.2, not the 20-page probe of §3.1.

### 3.1 Data Source: Fiverr via the Wayback Machine

We use archived Fiverr gig pages from the Internet Archive's Wayback Machine. Fiverr is the largest marketplace for freelance digital services; sellers post standardized "gigs" at listed price tiers. Three properties suit the estimator: prices are **posted** rather than negotiated per project as on Upwork, so a price attaches to a persistent item; tasks are **granular** — "write a 1000-word blog post" — the unit the AI-and-labor literature works in [CITE-autor-levy-murnane-2003, CITE-acemoglu-restrepo-2019]; and coverage is **longitudinal**, Fiverr having been archived since 2011.

Fiverr was not assumed. Before any collection code we set three pass/fail criteria — ≥10 snapshots spanning ≥3 years for ≥3 categories, ≥80% of pages yielding a price, ≥5 sellers observable at ≥3 dates — and tested them on a 20-page probe. All three cleared, **20 of 20** pages yielding title, seller handle and ≥1 price tier via the embedded `packageList` JSON; Upwork (posted prices frequently absent) and Freelancer.com (sparse coverage) were rejected. That gate established the source is *parseable and longitudinal*, and nothing about whether it is dense enough to identify a price index — which §3.6–3.7 answer largely in the negative.

**Scoping forced a two-phase design.** A pre-collection projection put the archive at roughly 2.5 million gig URLs and 4–20 TB of raw HTML, beyond what we could retrieve or politely request. Rather than crawl until the disk filled, we downloaded the archive's **capture index** first — its catalogue, one row per archived page, carrying no page content — then fetched only the pages a manifest built offline named. Every sampling decision is therefore made against a census rather than against whatever a crawler reached first, and the sampling frame is a file others can re-sample from. Counted from that index, the archive holds **1,778,505 distinct gig URLs** carrying **22.7 million** deduplicated status-200 captures — roughly 12 TB raw. The projection was 1.4× high on URLs and correct on volume.

**What the census then revealed.** *The archive is an opportunistic crawl, not a sampling frame.* Pages are captured when the Internet Archive happens to capture them; nothing about the density is designed, and a 20-page probe cannot detect it. At the early end the consequence is severe: **2017Q2, 2017Q4, 2018Q1 and 2018Q2 contain no captures at all**, the quarter pairs 2017Q1→2017Q3 and 2017Q3→2018Q3 share **zero** matched gigs, and adjacent pairs over the whole index hold **1** matched gig at 2017Q3→Q4 against 8,084 at 2018Q3→Q4. **2018Q3 is a hard floor on any matched-model estimate from this archive**, imposed by the data rather than chosen. §3.7 shows even 2018Q3–2020Q1 is too fragile to publish, so we report **2020Q1–2026Q1**.

### 3.2 Sample Construction

**Two crawls, not one**, estimated separately and spliced (§3.4): a **historical** crawl selected for depth (2011–2026, 500 sellers qualifying on longitudinal depth) and a **recent** crawl selected for density (2024Q3–2026Q1, a capture required in the trailing window). The pipeline runs in five phases, the first two consuming the capture index alone and only the third requesting a page.

| Phase | Operation | In → out (historical crawl) |
|---|---|---|
| 1 | Retrieve the capture index per first-letter prefix (`code/01`) | → **60M** entries |
| 2 | URL shape (2 path segments, status 200, ~60 reserved first segments); dedup per (URL, day) on content digest; classify slugs; keep sellers holding a gig with ≥5 monthly snapshots over ≥2 years; uniform random draw, fixed seed, 48,643 → 5,000 → **500 sellers** (`code/02`–`07`) | 60M → **22.7M** unique (URL, month) → **26,603** snapshots over 14,938 gigs |
| 3 | Download at 12 req/s with backoff, gzipped (`code/08`) | 26,603 → **22,632 (85.1%)**; recent 15,309 → 15,150 (99.0%) |
| 4 | Extraction cascade, then drop reserved-segment pages (`code/09`, `gigfilter.py`) | **100%** priced; 37,782 → **33,936** both crawls (−10.2%) |
| 5 | Unique (seller, slug) → **1,908** gigs; gig-quarter median, 0 < *p* ≤ \$10,000, gigs in ≥2 quarters | → **1,066 historical**, 2,908 recent panel gigs |

Four choices there carry weight rather than mechanics. **The URL-shape rule is the load-bearing assumption about what a gig is**, and phase 4's exclusion shows it is not airtight. **We sample sellers, not gigs**: drawing gigs would cover more of the category space but break the within-seller panel §3.8 requires, and both draws are simple uniform random samples, not stratified. **Failures are not checkpointed**, so re-running the downloader retries exactly the failures. And **the 150-item TF-IDF clustering is not used for the index** (silhouette 0.114).

**The exclusion that changed a result.** Several of Fiverr's own section pages — `/hire/<category>`, `/agencies/<name>` — satisfy the two-segment rule, carrying a reserved site section where a seller handle should be. Having no `packageList`, they fell through to the dollar-amount fallback, which recorded the page's **budget-filter default** as if it were a price, and Fiverr's change of that default between 2024Q4 and 2025Q1 imposed a spurious **−50%** step on every category. We drop all observations whose leading segment is reserved — **3,846 of 37,782 (10.2%)**, entirely within the recent crawl. The rule keys on the URL family, not the extraction method, because the same fallback recovers genuine pre-2017 prices (**2,527 of 2,531** historical fallback rows are valid). §4.6 reports the effect; it is large. Its detection is the transferable part: the defect survived every check we had until the table of extraction-method **shares** exposed it, a success rate having shown nothing wrong.

**The collection was revised five times, each time by something the data had just shown** — the sampling rule, the second crawl, the request rate (after a **45%** per-attempt failure rate), gzip storage, and the exclusion above. `drafts/data-collection.md` narrates the sequence in full.

**Three limits no revision reaches**, being properties of the archive rather than of our budget, are carried into §6: gig *exit* is unmeasurable, streaming all 60M records across **509,339 captures returning `n_404 = 0`** because the archive ceases to re-request a delisted URL rather than recording its death; the trailing edge is closed, status-200 captures falling from 280,779 in September 2024 to **66** in March 2026; and the chain is severed before 2018Q3. Two **enlarged collections** (**25,051** and **39,933** gigs) are complete as of August 2026 and **contribute no number to this paper**. Note throughout that panel gigs do not govern precision: a matched-model index is identified by gigs shared between *pairs* of quarters, which §3.6 reports wherever this paper claims a sample size.

### 3.3 Category Classification and Weights

We classify gigs into **seven** categories by keyword matching on descriptions and cluster labels for the historical crawl and from the crawl manifest for the recent one, using an identical map. Two categories present in earlier drafts, data entry and data analysis, are **excluded**: both are too thin to estimate (46 and 38 panel gigs) and data entry is dropped from the recent crawl, so neither has a post-2024 segment. Weights come from maximum observed review counts per category, a proxy for transaction volume, normalized to sum to one — analogous to CPI expenditure weights.

| Category | Recent panel gigs | Weight |
|----------|------------------:|-------:|
| Design | 1,466 | 0.706 |
| Writing | 368 | 0.111 |
| Marketing | 294 | 0.063 |
| Coding | 462 | 0.053 |
| Video | 235 | 0.046 |
| Audio | 55 | 0.019 |
| Translation | 28 | 0.003 |

Design's weight of **0.706** is the single most consequential feature of the composite: to a first approximation the composite is a design index with six minority components. §3.6 shows this is why it meets our precision standard when six of seven categories do not, and §3.7 why it is robust to estimator choices that move the categories substantially. Readers should not treat it as a summary of the seven categories' typical behaviour, which is why they are reported individually.

### 3.4 Index Construction: GEKS-Jevons

We construct the IPI as a **matched-model index**, following BLS practice for CPI items where direct quality adjustment is difficult [CITE-bls-handbook-2018]: the same gig is compared to itself across periods, so its own price *level* — and with it unobserved quality, seller identity and task specificity — cancels.

**Why not a chained index.** The natural elementary aggregate is a chained Jevons, and we do not report one. Because captures are irregular, **24–35% of within-gig links span more than one quarter**, with a longest span of **35 quarters**; a chained index books that entire multi-quarter change as a single-quarter change on top of growth already contributed by gigs observed in between, and the errors compound multiplicatively — **chain drift** [CITE-ivancic-diewert-fox-2011]. In our data the chained composite rises **+283.0%** against **+78.4%** drift-free. We do not present that gap as a measurement of drift, because decomposing it shows it is not one: the gap-spanning defect's share of the log gap ranges from **7% (audio) to 802% (translation)**, and the chained index diverges by **−43% to +93% with no consistent sign** (Appendix A). That argues for a multilateral estimator rather than being a quantity we can report.

**The estimator.** For each ordered pair of quarters $(s,t)$ we form the direct bilateral Jevons comparison over the gigs matched in both,

$$P_{s,t} = \exp\left( \frac{1}{|S_{c,s,t}|} \sum_{i \in S_{c,s,t}} \ln \frac{p_{i,t}}{p_{i,s}} \right),$$

and make these bilaterals transitive by averaging the routes through every link quarter $\ell$:

$$\ln I^c_t = \frac{1}{|L_{c,t}|} \sum_{\ell \in L_{c,t}} \left( \ln P_{0,\ell} + \ln P_{\ell,t} \right),$$

with $0$ the base quarter and $L_{c,t}$ the link quarters for which both legs are populated. This is **GEKS-Jevons** [CITE-ivancic-diewert-fox-2011], introduced to eliminate chain drift in high-frequency scanner data. Because each gig's level cancels inside the ratio, gigs at very different price points pool with no level term to estimate, and with no chain there is nothing along which error can accumulate. It is the appropriate multilateral choice here: we observe no quantities or expenditure shares, which rules out GEKS-Törnqvist and Geary–Khamis and leaves the unweighted Jevons bilateral the ILO CPI Manual recommends [CITE-ilo-cpi-manual-2004]. We use full-window rather than rolling-window estimation [CITE-krsinich-2016], this being a retrospective index with no published history to revise.

**Estimation choices.** A quarter must contain at least 3 distinct gigs, a gig must appear in at least 2 quarters, and a bilateral must rest on at least **3 matched gigs** (`MIN_MATCH = 3`). That threshold is usually defended as buying precision at the cost of coverage; tested across eight values, **the trade-off does not exist in that form**. Precision is flat to within 0.2 percentage points across `MIN_MATCH` = 1…10 in the five dense categories, and raising it makes precision strictly *worse* in the thin ones, because the threshold does not add matched gigs to a comparison — it **deletes comparisons**. We keep 3 because lowering it to 1 would let a bilateral rest on a single gig; the composite is robust across the range (**+76.4% to +78.4%**). The thin-category problem is one of sample adequacy (§3.6), not of thresholds.

**Splicing.** The panels are spliced at their earliest shared quarter, **2024Q3**, the composite re-based to 2020Q1 = 100 and aggregated as a weighted geometric mean, $\text{IPI}_t = \exp\left(\sum_c w_c \ln I^c_t \big/ \sum_c w_c\right)$.

**Alternatives and known biases, tested rather than assumed.** A time-product-dummy specification is also drift-free and yields **+89.6%** ($r = 0.996$ with GEKS). The two differ through imputation: the time-dummy index implicitly imputes, collapsing to the matched-model index only under complete data [CITE-de-haan-2004], and our panel is **14.9% filled**, so it imputes roughly 85% of cells. We prefer GEKS, which declines to. GEKS's documented weakness is downward bias when disappearing products are dumped at clearance prices [CITE-chessa-verburg-willenborg-2017]; we test rather than assume — a gig's *final* price change averages +0.051 log points against +0.051 for its other transitions ($t = 0.07$, n.s.) — and note that 99% of gigs cease to be observed mid-panel, making disappearance an artifact of crawl attrition (§6). A third check shares none of GEKS's machinery: the **direct bilateral Jevons** between base and terminal quarters. On the recent panel GEKS agrees closely, median absolute gap **2.7%**; on the historical panel only **1 to 4** gigs survive both endpoints and the check is uninformative — which is precisely why GEKS routes through link quarters.

**Implementation.** Our code reproduces the `PriceIndexCalc` reference exactly (max absolute difference 0.0000) on the four categories that reference can process, and fails on the other three with a division-by-zero because coding, design and translation contain quarter pairs sharing *zero* matched gigs. We report **bootstrap standard errors** (200 replications, resampling gigs with replacement); bands are 1.96 × the standard error of the *log* level as a ±% half-width.

### 3.5 Deflation to Real Terms

Posted prices are nominal and the window contains the largest inflation episode in four decades, so we report the index in **real terms as the headline**, with nominal alongside. We deflate by the US CPI for All Urban Consumers, FRED series `CPIAUCSL` (seasonally adjusted), averaged to quarterly frequency and re-based to 2020Q1 = 100; the not-seasonally-adjusted series is a robustness check and the two never diverge by more than **0.36%**. The deflator is a fixed sequence of constants, not an estimated quantity, so it adds no sampling variance and the bootstrap standard errors apply unchanged. CPI-U rises **+26.8%** over the window, so general inflation accounts for roughly **48%** of the composite's nominal rise — the single largest rival explanation for the level path.

### 3.6 Sample Adequacy: a Stated Precision Criterion

A sample size is not interpretable on its own; what matters is precision relative to the effect claimed. We therefore state a criterion and report that the pilot mostly fails it. **A category-quarter is *adequately sampled* if the 95% band on its index level is within ±5%**, and any cell missing the standard is reported as a band and excluded from ranking claims. At the terminal quarter, **six of seven categories fail**:

| Series | ±95% | Meets ±5%? |
|---|---:|:--:|
| Composite | ±3.7% | yes |
| Design | ±4.8% | yes |
| Marketing | ±7.7% | no |
| Writing | ±8.3% | no |
| Video | ±11.9% | no |
| Audio | ±13.9% | no |
| Coding | ±17.1% | no |
| Translation | ±29.2% | no |

Two features are easy to misread. **The composite passes while six of its seven components fail** — not a contradiction, but design's 0.706 weight propagating design's precision into the basket. And **coding fails worse than audio** (±17.1% vs ±13.9%) despite eight times the panel gigs, demonstrating that panel gigs are the wrong unit.

**Precision is governed by matched gigs *per bilateral*.** In the recent panel design's median quarter pair shares **208** matched gigs, coding's 58 and writing's 48, but audio's is **5** and translation's **3**. In the historical panel the divergence is extreme: design has 330 panel gigs but a **median of 1** matched gig per quarter pair, with 67% of pairs below `MIN_MATCH`, and writing a median of **0** with 79% of pairs unusable.

![Precision versus matched sample size](outputs/figures/fig4-precision-curve.svg)

**Figure 1.** Index precision against sampled gigs, log-log, recent panel at the terminal quarter, with a $1/\sqrt{n}$ reference and the ±5% and ±10% adequacy rules marked, finite-population corrected (Appendix A).

Measuring the precision-vs-*n* relationship directly (Appendix A) inverts to a design requirement: **±5% needs roughly 900 (writing), 1,100 (design) and 1,600 (video) matched gigs**, with **coding an outlier at roughly 7,400** — so a full-frame collection should size on the *worst* category. That curve also validates the published standard errors by a route sharing none of the bootstrap's machinery, agreeing within 3 percentage points. We borrow the CPI's *rules* [CITE-ilo-cpi-manual-2004, CITE-bls-handbook-2018] rather than benchmarking against its precision, and take our reference class from online-price measurement [CITE-cavallo-rigobon-2016, CITE-cavallo-2017].

### 3.7 What the Estimator Identifies, and What It Does Not

This section reports a defect that a confidence band does not express, and in our view the most important methodological finding in the paper. GEKS sets a quarter's level as an average over *link paths*, so how many paths support a quarter is a property of the data — and in the historical panel it is often very small. Three estimation choices perturb that support, and all three move the historical per-category levels far more than their stated bands. **The matching threshold**: coding's historical terminal quarter rests on 8 link paths at `MIN_MATCH` = 3 and exactly **one** at 4, moving the level **312.8 → 717.7**, a +129% swing against a stated band of ±61%. **The base quarter**: bases at 2016Q4, 2018Q3 and 2019Q1 give 2020Q1 levels of **75.7, 96.0 and 75.5**. **The estimation window**, sharpest because it moves a quantity that ought to be invariant: over the *identical* span 2020Q1→terminal, audio's growth reads **+103.9%** from a 2018Q3 start and **+258.7%** from 2020Q1. Levels here are deterministic, so this is the estimator, not noise.

**These are one defect, not three.** Decomposing the window case (Appendix A), the *gig-set* channel contributes nothing — the maximum absolute difference between the two windows' shared bilaterals is **0.0000** in all seven categories — and the *link-set* channel contributes all of it, on shared link sets numbering **2 to 5** quarters. Base quarter, threshold and window are three ways of perturbing one quantity: how many link paths support a level. Where that number is small the level is **not identified**, a stronger and different statement from *imprecise*. A ±61% band invites the reader to believe the truth lies within it; a +129% swing says the band is not the right object.

**Consequences we adopt.** The historical segment's per-category levels for **coding, translation and audio are marked not identified** and never quoted as point estimates. The **recent segment is unaffected** — five of seven categories do not move at all under the threshold sweep, and its bilaterals are dense. The **composite is exempt, and verifiably so**: the splice truncates the historical leg at 2024Q3, and that leg's spread across window choices is 4.0% for design and 4.5% for video, against 27.6% and 16.4% over the full historical span. Its robustness follows from splice geometry and weighting, not from the categories being well identified.

![Link-path support per quarter](outputs/figures/fig5-linkpath.svg)

**Figure 2.** The number of populated GEKS link paths supporting each quarter's level, by category, for both panels. A quarter resting on a single path is not identified: its level is a property of which path happened to survive.

### 3.8 Measuring the Rival Explanations

Because this paper is descriptive, the burden it accepts is to *measure* the leading alternatives to an AI account rather than to argue them away.

**Reputation accumulation ("the treadmill").** A gig's price rises partly because it accumulates reviews, not because the service became dearer. We estimate the within-gig elasticity of price to reviews, $\Delta \ln p_{i,t} = \beta \, \Delta \ln (1 + R_{i,t}) + \varepsilon_{i,t}$, with gig-clustered standard errors: $\beta = +0.1068$ ($t = 5.32$) over 9,762 transitions — **+7.7% per doubling of reviews**. We then publish a **band**: raw, and reputation-adjusted by rescaling each cell as $p \cdot \exp(-\beta \ln(1+R))$ and re-estimating. The composite runs **+79.0% raw and +39.7% adjusted**. Three properties travel with it. The adjusted series is a **lower bound, not a correction** — reviews are cumulative sales, so $\beta$ absorbs demand as well as reputation, and if AI suppressed demand the adjustment consumes part of the effect the index is trying to show; raw remains the headline. $\beta$ is **pooled**, forced rather than preferred: estimated per category, audio and translation return the wrong sign. And the **floor is soft** — across $\beta$'s own 95% interval the adjusted bound moves between roughly +50% and +28%, so it must not be quoted as a single number.

**General inflation.** Measured and removed by deflation (§3.5): CPI-U accounts for roughly 48% of the nominal rise.

**Composition and survivorship.** The matched-model design holds the gig fixed, so it cannot be explained by entry mix — but it follows *ageing incumbents*. New gigs (≤10 reviews at first capture) enter at flat prices from 2019 to 2025 in design, writing, video and marketing while the incumbent index rises +47% to +167%. If the market's *entry* price is flat while its *incumbent* price climbs, the index measures the life-cycle of surviving gigs at least as much as the price of the service. **§6.2 treats this as the paper's most serious unresolved limitation**, the two crawls giving different entry medians for the same year.

**Why a hedonic cross-section would not do this better.** It is natural to ask why we do not simply regress price on observable seller characteristics. We estimated that model — $\ln p_i = b_0 + b_1 \,\text{rating}_i + b_2 \ln(1 + V_i) + \sum_c \gamma_c \,\text{taskType}_{ic} + \varepsilon_i$, on 3,753 gigs at their latest capture with seller-clustered errors — and it makes the case for the matched-model design better than argument could. **Appendix A carries the full three-column table.** Rating is priced at **+3.15% per 0.1 rating point** and is the only seller-level variable that is; task type dominates the fit, coding **+124%** relative to design against translation **−40%**; yet $R^2$ is only **0.065**. And the volume coefficient **reverses between specifications**: indistinguishable from zero across sellers at +0.022 ($t = 1.64$), but **+0.133 ($t = 7.87$) within a gig over time**, reproducing the treadmill estimate on a different sample cut. The cross-section does not inflate a real effect; it **cancels** one, because across sellers high volume is also what cheap high-throughput sellers have. A hedonic reading would conclude experience is unpriced. It is priced; the cross-section cannot see it.

### 3.9 A Regression We Do Not Report, and Why

Earlier versions estimated a *price elasticity of intelligence*: a log-log regression of a category price index on a category-matched AI benchmark score, producing coefficients from −0.49 to +1.10, all significant at $p < 0.01$. **We retract it** as a spurious regression — two trending series, roughly twenty quarterly observations, no control group. A linear time trend fits better than the AI score in **every** category; so does CPI-U, returning "elasticities" of **+4.56 to +8.73** on the same data; in first differences the relationship disappears. **Appendix A reports the five diagnostics in full rather than quietly dropping the table**, the specification being an obvious thing for others to try on data of this kind. The benchmark series remain in our released data and we use them descriptively, but estimate no elasticity from them.

### 3.10 Corrections to Earlier Versions of This Work

Six figures or descriptions in earlier drafts were wrong, and **Appendix A tabulates all six** — the earlier claim, what is correct, the effect on results — rather than silently restating corrected values. Five changed no estimate: the archive's size was a projection, not a count (~2.5M against the measured **1,778,505**); the download shortfall was deduplication, not 404 attrition; the 500 sellers were called *stratified* when both draws are simple uniform random ones; the panel fill rate was 10.9% when it is **14.9%**; and the reputation elasticity was reported unclustered as $t = 10.19$ when gig-clustered errors give $t = 5.32$.

**One correction changed a published finding.** We had reported a real −21% fall in cognitive-labor prices in 2025 from a composite peak of 312. It was an artifact of two defects now removed — the naive chained series (§3.4) and the non-gig section pages (§3.2). **It is retracted**, and §4.6 gives the before-and-after. Separately, the `rating` column carries a scale error in **217 historical rows** from Fiverr's pre-2019 10-point scale; it touches no result but is not yet fixed upstream.
