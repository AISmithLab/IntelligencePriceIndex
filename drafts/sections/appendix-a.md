## Appendix A. Estimation Diagnostics

This appendix holds the detail Section 3 compresses. It is referenced from §3.4, §3.6, §3.7, §3.8, §3.9 and §3.10. The complete *collection* record — pipeline parameters, intermediate counts, the revision history and the two enlarged collections — is a separate document, `drafts/data-collection.md`.

### A.1 The chained-index decomposition (§3.4)

The chained composite rises +283.0% over 2020Q1–2026Q1 against +78.4% for the drift-free estimate. We do not report that gap as a measurement of chain drift, because decomposing it on the production panel — separating the gap-spanning defect from genuine drift by re-estimating with links restricted to adjacent quarters — gives a defect share ranging from **7% (audio) to 802% (translation)**, exceeding 100% wherever the residual runs the other way. In two categories the residual does run the other way: with gap-spanning links removed the chained level lands *below* GEKS (coding 273.7 vs 312.8; translation 130.4 vs 227.8). Across the seven categories the chained index diverges from GEKS by **−43% to +93% with no consistent sign**. The honest statement is that a chained index on irregularly-archived data is unstable in both directions relative to a multilateral one.

### A.1b The extraction cascade, by method share (§3.2)

Fiverr's markup changed twice over the window, so the extractor is a cascade of four methods ordered by reliability, each page falling through only when the one above finds nothing. Extraction succeeded on **100% of downloaded files** (22,632/22,632 historical; 15,150/15,150 recent).

| Method | Era | Mechanism | Share |
|--------|-----|-----------|-------|
| `packageList` JSON | 2020+ | Embedded JSON array, price in cents | 72.9% |
| Old-style JSON | Pre-2017 | JSON with price as string dollars | 15.2% |
| HTML `<span>` | 2018–2020 | `class="price"` DOM elements | 0.7% |
| Dollar fallback | All eras | `$X` pattern in page text | 11.2% |

**This table, not the success rate, is what exposed the non-gig defect of §3.2.** The dollar fallback's share was implausibly high in the recent crawl, and 2,436 of those rows sat at exactly \$500 with 330 at \$1,000 — the budget-filter default. A success rate of 100% would have shown nothing wrong. The rule that removes them keys on the URL family rather than on `dollar_fallback`, because that method also recovers **2,527 of 2,531** valid historical prices, clustered at \$5, Fiverr's original floor.

### A.2 The `MIN_MATCH` sweep (§3.4)

Eight values tested. In the five dense categories precision is flat to within 0.2 percentage points across `MIN_MATCH` = 1…10. In the thin ones raising the threshold makes precision strictly **worse**: audio's terminal band runs ±11.3% at 1, ±16.0% at 3, ±30.3% at 5 and ±34.1% at 6. The mechanism is that `MIN_MATCH` does not add matched gigs to a comparison — it **deletes comparisons**, shrinking the support of the average over link paths. The headline composite is robust across the range, **+76.4% to +78.4%** for `MIN_MATCH` = 1…6.

### A.3 Precision versus sample size (§3.6)

Measured by subsampling gigs and re-estimating, 60 independent subsamples per point, terminal quarter, recent panel.

**One correction matters and is easy to miss.** Subsampling *without* replacement has variance $(1 - n/N)$ times the with-replacement variance, so the raw subsample spread understates the precision loss as $n$ approaches $N$ — at $n = N$ it is zero by construction. Since the published standard errors come from a bootstrap that resamples *with* replacement, we divide the subsample standard deviation by $\sqrt{1 - n/N}$. The corrected curve is what we report.

| Category | *N* | n=25 | n=50 | n=100 | n=200 | n=400 | n=800 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Design | 1,466 | ±37.2% | ±24.7% | ±19.5% | ±16.4% | ±9.0% | ±5.9% |
| Coding | 462 | ±49.3% | ±41.0% | ±38.8% | ±30.4% | — | — |
| Writing | 368 | ±27.4% | ±21.9% | ±16.4% | ±10.6% | — | — |
| Video | 235 | ±33.8% | ±22.7% | ±19.7% | — | — | — |

**The curve validates the published standard errors independently.** Extrapolating each corrected curve to its own full *N* gives design **±4.4%**, writing **±7.8%**, video **±12.9%** and coding **±20.0%**, against published bootstrap values of ±4.8%, ±8.3%, ±11.9% and ±17.1% — two procedures sharing no machinery, agreeing to within 3 percentage points in every case.

Inverting the fit gives the design requirement: ±5% needs roughly **900** (writing), **1,100** (design) and **1,600** (video) matched gigs per bilateral, and ±10% needs 225–390. **Coding is the outlier at roughly 7,400**, because its per-gig information content is far lower — its prices are more dispersed and its matched pairs thinner.

### A.4 The identification defect, decomposed (§3.7)

Widening the estimation window changes two things at once: the **gig set** (a gig is retained only if it has two observations inside the window) and the **link set**. We separate them.

- **The gig-set channel contributes nothing.** The maximum absolute difference between the two windows' shared bilaterals is **0.0000** in all seven categories, because a gig with one in-window observation enters no bilateral.
- **The link-set channel contributes all of it.** Recomputing the same growth on the link quarters both windows share, with the base term cancelled algebraically, gives **exactly identical** answers — audio 142.0% under both, a figure neither published number matches. The shared link sets number **2 to 5** quarters.

Full window-start spread, over the identical span 2020Q1→terminal: audio 76.0%, marketing 42.1%, design 27.6%, writing 26.3%, coding 21.3%, video 16.4%. The composite's splice-truncated leg (2020Q1→2024Q3) moves only 4.0% for design, 4.5% for video and 10.7% for writing.

**Base-quarter sensitivity.** Estimating the pooled index with the base at 2016Q4, 2018Q3 and 2019Q1 gives 2020Q1 levels of 75.7, 96.0 and 75.5, on standard errors of **0.12–0.24 in logs** — same estimator, same panel, three incompatible answers. Coding's direct 2020Q1→2025Q1 bilateral carries a single matched gig and is never used at any threshold.

**The ceiling no collection reaches.** Coding requires roughly **7,400** matched gigs per bilateral for ±5%, and the entire capture index supplies at most **6,142**. No collection from this archive can measure coding to the stated criterion.

### A.5 The hedonic cross-section, full results (§3.8)

Estimated on 3,753 gigs taken at their latest capture — one row per gig, so heavily archived gigs do not dominate — with seller-clustered standard errors and design as the omitted category.

| Term | (1) Cross-section | (2) + quarter FE | (3) Within-gig |
|---|---:|---:|---:|
| Rating | **+0.310** (2.76) | **+0.338** (3.10) | — |
| ln(1 + reviews) | +0.022 (1.64) | −0.001 (−0.07) | **+0.133** (7.87) |
| Coding | **+0.808** (9.92) | **+0.796** (9.68) | — |
| Marketing | **+0.625** (6.47) | **+0.574** (6.02) | — |
| Video | **+0.337** (3.66) | **+0.341** (3.76) | — |
| Audio | +0.179 (1.25) | +0.111 (0.92) | — |
| Writing | **+0.153** (2.08) | +0.140 (1.91) | — |
| Translation | **−0.506** (−2.61) | **−0.487** (−2.55) | — |
| $R^2$ | 0.065 | 0.096 | 0.038 |
| $n$ | 3,753 gigs | 3,753 gigs | 9,726 transitions |
| Clusters | 2,745 sellers | 2,745 sellers | 3,415 gigs |

*$t$-statistics in parentheses; bold marks $|t| > 1.96$. Task-type coefficients are price levels relative to design and carry no AI-exposure content. Column (3) re-estimates the volume slope on within-gig first differences with quarter fixed effects, holding the seller fixed.*

Two features of the data bound how column (1)'s rating slope should be read. **`rating` is nearly degenerate at gig level** — standard deviation 0.26, interquartile range 4.80–5.00, and 41% of gigs at exactly 5.0 — so a "per rating point" coefficient extrapolates far outside the data, and we report it per 0.1 point (+3.15%). And **"prior gigs" has two readings that are negatively correlated (−0.333)**: distinct gigs a seller offers, near-constant at a median of 1, and cumulative reviews, which varies and is the notion the specification intends. The table uses reviews; substituting seller gig counts gives −0.051 ($t = -0.59$) and leaves every other coefficient unchanged.

**The pooled reputation elasticity (§3.8).** $\beta = +0.1068$ with a gig-clustered standard error of **0.0201** ($t = 5.32$), over **9,762 transitions and 3,419 gigs** — +7.7% per doubling of a gig's reviews. Estimated separately by category, audio (−0.089) and translation (−0.080) return the wrong sign, so adjusting them with their own $\beta$ would *raise* their index, which is not interpretable. The remaining five spread from marketing +0.206 to design +0.075. Pooling is therefore a stated assumption, not a formality. Sensitivity across $\beta$'s own 95% confidence interval moves the adjusted bound between roughly +50% and +28%.

**The direct bilateral check, per category (§3.4).** Recent panel: writing +1.4% (n = 65 matched gigs), coding +1.9% (n = 58), design +2.7% (n = 275), marketing −4.7% (n = 47), video −5.0% (n = 63), audio +1.7% (n = 6); median absolute gap 2.7%. Historical panel: only 1 to 4 gigs survive both endpoints per category, and the direct figure disagrees with GEKS by up to 64% (writing, on a single gig).

### A.6 The retracted elasticity: five diagnostics (§3.9)

The specification was $\ln I^c_t = \alpha_c + \beta_c \ln (A^c_t + 1) + \varepsilon_{c,t}$, with $A^c_t$ built by interpolating published benchmark series (HumanEval and SWE-bench for coding, AlpacaEval and Chatbot Arena for writing, WMT BLEU for translation, FID for design, Whisper WER for audio) to quarterly frequency and min-max normalizing. It produced coefficients from −0.49 to +1.10, all significant at $p < 0.01$. It fails five ways.

1. **The residuals are almost perfectly serially correlated.** Durbin–Watson runs **0.22 to 1.08** across the six estimable categories, invalidating every standard error in the original table. Newey–West at lag 4 shrinks the $t$-statistics by 1.3–1.8× but cannot repair the specification, because the problem is the trend rather than the standard error.
2. **A linear time trend fits better than the AI score, in every category.** $R^2$(time) vs $R^2$(AI): design 0.979 vs 0.412, marketing 0.981 vs 0.934, coding 0.974 vs 0.909, writing 0.941 vs 0.864, audio 0.925 vs 0.805, translation 0.913 vs 0.882.
3. **So does CPI-U.** Substituting the consumer price index for the AI score fits at least as well in five of six categories and returns "elasticities" of **+4.56 to +8.73** — a claim no one would publish, from the same regression on the same data.
4. **In first differences the relationship disappears.** Regressing $\Delta \ln I$ on $\Delta \ln A$ gives $t$-statistics of 0.26, −0.02, 0.48, 2.24, −0.34 and 0.20 — one marginal result in six tests, which is what chance produces.
5. **The resulting ranking is not stable to anything.** Re-estimated on the production panel at the published base, the ordering correlates with the original at Spearman $\rho = +0.314$ ($p = 0.544$): design falls from the most elastic of eight categories (+1.139) to fourth of six (+0.295). Re-estimated on a different price series it correlates at $\rho = +0.657$ ($p = 0.156$).

### A.7 Corrections to earlier versions of this work (§3.10)

| # | Earlier claim | What is correct | Effect on results |
|---|---|---|---|
| 1 | The archive holds ~2.5M distinct gig URLs | **1,778,505**, counted directly from the harvested index. The earlier figure was a pre-index projection from four calibration prefixes, 1.4× high on URLs and correct on volume | None. The projection forced the two-phase design, which was right on either figure |
| 2 | The 15% historical download shortfall is 404 attrition | The download log records **102 hard failures and no 404s at all**. The bulk of the gap is manifest rows collapsing onto a gig-day file already retrieved — deduplication, not loss | None. The 22,632 figure and everything downstream are unaffected; only the explanation was wrong |
| 3 | The 500 sellers are a *stratified* sample | Both draws are simple uniform random samples from the qualifying pool, seeded for reproducibility. A stratification by snapshot count was written for an earlier sampling design and did not survive into the production pipeline | None on any estimate; the description was wrong |
| 4 | The gig-quarter panel is 10.9% filled | **14.9%** filled on gigs × 25 quarters, and 15.0% before the non-gig exclusion. The earlier figure could not be reproduced under any definition we could recover | None. Bears only on how much the TPD alternative imputes |
| 5 | Reputation elasticity $\beta = +0.103$, $t = 10.19$ | $\beta = +0.1068$, $t = 5.32$. The earlier standard error was unclustered on first differences drawn from the same gigs; gig-clustered errors are 1.93× larger | The coefficient survives comfortably; the $t$-statistic does not. We report the clustered one |
| 7 | The exposure null is a power problem, not an identification problem | On 169,337 gig-quarters the estimate is still below its MDE, and the design now **fails** parallel trends and reverses sign against a linear trend — gates it passed at pilot scale | **Revised.** §4.8, §6.1 and §7 now state that more data of the same kind does not resolve this, and that a control group is the binding requirement |
| 6 | A real −21% fall in cognitive-labor prices in 2025, from a composite peak of 312 | An artifact of two defects now removed: the naive chained series (§3.4) and the non-gig section pages (§3.2) | **Retracted.** This is the only correction that changed a published finding; §4.7 gives the full before-and-after |

One further defect is recorded here because it affects any future row-level use of these data, though it enters no result. The `rating` column carries a scale error: **217 historical rows report values in (5, 10]**, because pre-2019 Fiverr displayed a 10-point scale that the extractor wrote into the same column as the 5-point one. It does not touch the index, which uses prices only, and it does not move the hedonic result of §3.8 — halving those rows, dropping them, and leaving them raw give $b_1 = +0.310$, $+0.311$ and $+0.302$, since only 167 affected rows survive to a gig's latest capture — but it is not yet fixed upstream.

### A.8 The pre-registered exposure model: full diagnostics (§3.8, §4.8)

Balanced panel, 169,337 gig-quarter observations across 15,676 gigs, 2019Q4–2024Q4, real terms, gig-clustered standard errors.

| Gate | Specified test | Result | Verdict |
|---|---|---|:--|
| A | Exposure interacted with each pre-launch quarter; all insignificant | 4 of 11 significant (Exp × 2021Q3 −0.1455, $t$ −2.51; 2021Q4 −0.1445, $t$ −2.40; 2022Q1 −0.1510, $t$ −2.48; 2022Q2 −0.1326, $t$ −2.17) | **FAIL** |
| B | Coefficient stable when Exposure × linear trend is added | Moves −0.0333 ($t$ −1.35) → **+0.0358** ($t$ +1.38); Exposure × trend is −0.00804 ($t$ −2.24) | **FAIL — sign flips** |
| C | Placebo break inside the pre-period returns null | 2021Q2 break: −0.0595 ($t$ −1.78), 93,247 obs | PASS |
| D | Estimate survives first differencing | +0.0081 ($t$ +0.59), 153,661 within-gig changes | **FAIL** |
| E | Inference clustered on gig | Clustered SE 0.0246 vs unclustered 0.0121 — a 2.03× inflation | reported clustered |
| F | Point estimate exceeds the minimum detectable effect | MDE at 80% power = 0.0689 log points; $|\hat\theta|$ = 0.0333 | **below MDE** |

Window extension (pooling the 2025 archival refresh, 172,934 obs / 15,864 gigs, through 2025Q4): $\hat\theta$ = **−0.0324** ($t$ −1.31); gate B moves it to +0.0332 ($t$ +1.29); MDE 0.0691. Every gate returns the same verdict as on the shorter window.

Secondary exploratory specification (market-measured AI-branded share, category × quarter, **not pre-registered**): +1.2888 ($t$ +11.23), implying +13.76% per 10pp. With one linear trend per category: **+0.0727 ($t$ +0.84)**, implying +0.73%. It survives first differencing (+0.1434, $t$ +2.03), which is why the trend race rather than differencing is the decisive test here.

### A.9 Realised order value, full series (§4.6)

All 17 quarters; §4.6 shows alternate quarters. Conditioned on orders of \$50 or more, the only band boundaries stable across every era of Fiverr's reporting.

| Quarter | n (\$50+) | Gigs | \$50–100 | \$100–200 | \$200–400 | \$400–800 | \$800+ | Median bin |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2022Q1 | 25,687 | 8,654 | 35.7% | 32.9% | 19.4% | 8.5% | 3.6% | \$100-200 |
| 2022Q2 | 29,415 | 9,828 | 36.2% | 32.8% | 19.5% | 7.8% | 3.7% | \$100-200 |
| 2022Q3 | 28,336 | 9,716 | 39.5% | 32.0% | 18.1% | 7.0% | 3.4% | \$100-200 |
| 2022Q4 | 28,572 | 9,554 | 38.6% | 32.5% | 18.5% | 7.3% | 3.1% | \$100-200 |
| 2023Q1 | 27,075 | 9,385 | 39.4% | 32.4% | 18.4% | 7.0% | 2.9% | \$100-200 |
| 2023Q2 | 24,243 | 9,094 | 39.1% | 32.4% | 18.2% | 7.1% | 3.3% | \$100-200 |
| 2023Q3 | 29,250 | 9,736 | 38.3% | 32.5% | 18.6% | 7.5% | 3.0% | \$100-200 |
| 2023Q4 | 28,031 | 9,691 | 38.0% | 32.6% | 19.1% | 7.3% | 3.0% | \$100-200 |
| 2024Q1 | 22,136 | 8,385 | 36.8% | 32.5% | 19.3% | 8.0% | 3.4% | \$100-200 |
| 2024Q2 | 30,233 | 11,391 | 39.1% | 31.4% | 18.7% | 7.4% | 3.5% | \$100-200 |
| 2024Q3 | 40,393 | 12,352 | 40.7% | 31.0% | 17.9% | 7.2% | 3.3% | \$100-200 |
| 2024Q4 | 11,171 | 5,337 | 39.5% | 30.5% | 18.0% | 7.7% | 4.3% | \$100-200 |
| 2025Q1 | 4,483 | 2,368 | 40.3% | 29.9% | 17.8% | 8.2% | 3.9% | \$100-200 |
| 2025Q2 | 3,197 | 1,751 | 41.1% | 28.1% | 16.7% | 9.0% | 5.1% | \$100-200 |
| 2025Q3 | 3,474 | 1,725 | 39.4% | 30.6% | 17.6% | 7.8% | 4.6% | \$100-200 |
| 2025Q4 | 3,161 | 1,404 | 39.5% | 29.3% | 18.3% | 7.5% | 5.3% | \$100-200 |
| 2026Q1 | 420 | 253 | 40.5% | 29.3% | 16.9% | 8.1% | 5.2% | \$100-200 |

Recovered from 397,698 stored captures, deduplicated on `encrypted_order_id`: **681,668** distinct orders, **617,456** in this window. Field coverage — the share of orders carrying any price band — runs 54–67% through 2022–2023, 94% at 2024Q2, and 100% from 2024Q3 onward; the apparent sub-\$50 share tracks that coverage almost exactly, which is the artifact §4.6 describes.

### A.10 The 35 narrow categories, real terms (§4.3)

Each cell clears all 20 quarters at full pair density on the balanced panel. Deflated to 2020Q1 dollars with CPI-U. Sorted by real change; 33 of 35 intervals exclude zero.

| Narrow category | Real Δ 2020Q1→2024Q4 | 95% CI | Excludes 0 |
|---|---:|---|:--:|
| translation · subtitle | +3.1% | [-11.6%, +20.3%] | **no** |
| translation · translation | +5.5% | [-2.4%, +14.1%] | **no** |
| design · illustration | +19.9% | [+8.2%, +32.9%] | yes |
| design · logo brand | +30.2% | [+22.0%, +38.9%] | yes |
| marketing · seo | +38.7% | [+23.1%, +56.4%] | yes |
| design · threed product | +41.6% | [+22.8%, +63.2%] | yes |
| video · motion intro | +45.9% | [+23.0%, +73.1%] | yes |
| audio · podcast | +50.2% | [+20.5%, +87.3%] | yes |
| design · print merch | +50.7% | [+41.7%, +60.4%] | yes |
| translation · other | +51.2% | [+33.3%, +71.5%] | yes |
| video · video editing | +53.2% | [+25.1%, +87.5%] | yes |
| marketing · social media | +53.8% | [+37.0%, +72.7%] | yes |
| video · animation | +56.0% | [+44.6%, +68.3%] | yes |
| design · other | +56.1% | [+43.9%, +69.3%] | yes |
| audio · other | +61.7% | [+21.0%, +116.1%] | yes |
| video · other | +63.4% | [+52.8%, +74.8%] | yes |
| writing · content seo | +65.4% | [+48.3%, +84.4%] | yes |
| audio · voiceover | +66.2% | [+45.8%, +89.3%] | yes |
| writing · ebook book | +67.8% | [+54.7%, +82.0%] | yes |
| writing · other | +68.2% | [+54.3%, +83.5%] | yes |
| writing · editing | +71.5% | [+55.7%, +88.9%] | yes |
| coding · data ml ai | +72.8% | [+11.9%, +166.6%] | yes |
| writing · copywriting | +73.1% | [+40.9%, +112.6%] | yes |
| coding · other | +77.8% | [+55.0%, +103.8%] | yes |
| writing · resume bio | +81.7% | [+54.6%, +113.5%] | yes |
| audio · music prod | +83.4% | [+69.7%, +98.3%] | yes |
| marketing · other | +89.7% | [+63.7%, +119.8%] | yes |
| design · social graphics | +97.4% | [+68.6%, +131.1%] | yes |
| coding · web dev | +100.0% | [+85.1%, +116.1%] | yes |
| coding · mobile app | +110.9% | [+63.5%, +172.2%] | yes |
| coding · backend api | +120.9% | [+78.4%, +173.6%] | yes |
| coding · automation bot | +142.1% | [+68.3%, +248.2%] | yes |
| design · ui ux web | +143.9% | [+82.6%, +225.9%] | yes |
| marketing · ads ppc | +144.1% | [+97.0%, +202.4%] | yes |
| marketing · email funnel | +155.1% | [+83.6%, +254.4%] | yes |
