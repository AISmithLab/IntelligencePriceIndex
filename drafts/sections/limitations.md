## 6. Limitations

This is a pilot-scale measurement paper, and several of its limitations are quantified rather than acknowledged. We state the bound wherever we have one, because a limitation with a number attached is a result and one without is a disclaimer.

### 6.1 What the sample cannot resolve

**Precision fails the standard we set.** Section 3.6 states a ±5% adequacy criterion and **six of seven categories miss it** at the terminal quarter, from marketing at ±7.7% to translation at ±29.2%. Only design (±4.8%) and the composite (±3.7%) pass, and the composite passes only because design carries 70.6% of the weight. Reaching ±5% would require roughly **900 matched gigs for writing, 1,100 for design and 1,600 for video—and about 7,400 for coding**, whose per-gig information content is far lower. Current panels run from 1,466 gigs (design) down to 28 (translation), with matched-gigs-per-quarter-pair medians of 208 down to 3. A full-frame collection must be sized on the worst category, not the average.

**No category ranking is supported.** The top three categories' intervals overlap one another completely, so their ordering is not determined by these data. Only design's separation from the top of the distribution is robust. We say this in Section 4.3 and repeat it here because point-estimate orderings are what get quoted onward.

**The quantity margins return nulls with wide bounds.** No category's sales rate broke by more than roughly **±23% to ±66%** after ChatGPT, and dormancy is likewise null once trend and composition are held fixed. These bounds are informative—they rule out very large effects—but they do not distinguish a moderate effect from none. The **raw** dormancy ranking (writing +6.1pp, marketing +5.6, audio +5.0, translation +5.0) reverses sign for three of seven categories under the adjusted specification and must not be quoted.

**The one identified design is underpowered.** The gig-level exposure difference-in-differences passes parallel trends but returns a 95% interval of **−14.8% to +87.6%** on the high-versus-low contrast. It cannot distinguish "AI did nothing" from "AI did a great deal."

### 6.2 Survivorship: the paper's most serious unresolved threat

The matched-model design eliminates compositional confounds by holding the gig fixed, but it thereby follows **ageing incumbents**, and this cuts against the paper's headline in a way we cannot currently bound.

New gigs entering with ≤10 reviews at first capture show **flat prices from 2019 to 2025** in design, writing, video and marketing, while the incumbent index over the same span rises **+47% to +167%**. If the market's *entry* price is flat while its *incumbent* price climbs, the index is measuring the life-cycle of surviving gigs at least as much as the price of the service. We cannot yet settle how much, because the two crawls give different entry medians for the same year (2024: \$50 on n=102 versus \$30 on n=2,389), so the series must be built within a crawl or the frames reconciled first. Until that is done, **the entry-price gap is an open problem, not a decomposition**, and the index should be read as a price for continuing gigs rather than for the category.

This interacts with the difference-in-differences design of Section 4.7 in a way worth stating explicitly: within-gig first differences **condition on survival**, so if highly exposed gigs *exit* rather than cut price, the design returns a null by construction. The observed null is exactly what that would produce. The entry-price companion series is therefore a prerequisite for the causal design, not a robustness check on it.

### 6.3 Exit and entry are not measurable from this data

A gig's absence from a Wayback-derived crawl means "not archived," not "taken down." No exit hazard is estimable from either crawl at any sample size. The problem is compounded by manifest construction: the recent crawl requires at least one snapshot in a trailing window, so the panel **conditions on survival by construction** (36.5% of recent-panel gigs are last seen in the final quarter, against 0.4% historically), and entry is truncated at both window edges (1,747 of 2,930 gigs "first captured" in the manifest's first quarter, 5 in its last), making the entry profile run from ~100% to ~0% mechanically.

Two design requirements follow. Both are cheap to specify now and **impossible to retrofit**:

1. **Sample gig URLs on a fixed schedule regardless of whether they still resolve, and record the 404s.** That alone makes exit measurable.
2. **Do not select the manifest on survival into a trailing window.** This is what makes both entry and exit uninterpretable today.

### 6.4 The estimator is not fully identified on the historical segment

Section 3.7 reports that the historical per-category levels for coding, translation and audio move far more than their stated bands under changes to the matching threshold, the base quarter, or the estimation window—up to +129% from a one-step threshold change, against a ±61% band. The cause is that GEKS averages over link paths and the historical panel supports only two to five of them per quarter. We mark these series **not identified** and do not quote them as point estimates.

This is a limitation of the *panel*, not of GEKS: the recent segment, where bilaterals are dense, is stable under all three perturbations, and the composite is exempt because the splice truncates the fragile historical leg at 2024Q3. But it means the paper's pre-2024 category detail is weaker than a band alone would suggest, and readers should treat the historical segment as establishing the composite path rather than category-level facts.

### 6.5 Platform, crawl, and measurement limitations

**Platform coverage.** Fiverr represents one segment of the cognitive labor market—relatively standardized, low-to-mid-complexity tasks at posted prices. Results may not generalize to enterprise freelancing (Upwork, Toptal), to formal employment, or to work requiring deep domain expertise. The IPI is a *gig-economy* price index, not a universal price index for cognitive labor.

**Wayback sampling is opportunistic.** The Internet Archive does not crawl pages with equal frequency; popular gigs are archived more often than niche ones, biasing the panel toward high-visibility sellers—precisely those most likely to show price resilience. The pilot's early years are severely affected: four quarters in 2017–2018 contain no captures at all, and the matched chain is severed there, which is why 2018Q3 is a hard floor and why we publish from 2020Q1.

**Price is not transaction value.** We measure the posted Basic-tier price, not what buyers paid or what they received. A seller who uses AI to raise output quality at an unchanged price has experienced quality-adjusted deflation the index does not capture; a seller who raises prices because AI lets them bundle more work may show inflation even as price-per-unit-of-value falls. Quality adjustment is the oldest problem in index construction and we do not solve it.

**A known data defect in a field we do not use for the index.** The `rating` column carries a scale error—217 historical rows report values in (5, 10] because pre-2019 Fiverr displayed a 10-point scale that the extractor wrote into the same column as the 5-point one. It does not affect the index, which uses prices only, and it does not move the hedonic result of Section 3.8 (only 167 affected rows survive to a gig's latest capture), but any future row-level use of `rating` on this data must correct it first.

### 6.6 What this paper does not claim

We do not claim to have identified an effect of AI on the price of cognitive labor. The index rises in real terms; reputation accumulation and general inflation account for a large and imprecisely bounded share of that rise; the residual is not separately attributable at this sample size; and every margin that might have separated the categories returns either a wide interval or a structural impossibility. The contribution is the instrument, the bounds, and the design requirements—not the causal claim the instrument was built to eventually support.
