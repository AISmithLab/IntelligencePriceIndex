## 6. Limitations

This is a pilot-scale measurement paper, and several of its limitations are quantified rather than acknowledged. We state the bound wherever we have one, because a limitation with a number attached is a result and one without is a disclaimer.

### 6.1 What the sample cannot resolve

**Precision fails the standard we set.** Section 3.6 states a ±5% adequacy criterion and **six of seven categories miss it** at the terminal quarter, from marketing at ±7.7% to translation at ±29.2%. Only design (±4.8%) and the composite (±3.7%) pass, and the composite passes only because design carries 70.6% of the weight. Reaching ±5% would require roughly **900 matched gigs for writing, 1,100 for design and 1,600 for video—and about 7,400 for coding**, whose per-gig information content is far lower. Current panels run from 1,466 gigs (design) down to 28 (translation), with matched-gigs-per-quarter-pair medians of 208 down to 3. A full-frame collection must be sized on the worst category, not the average.

**No category ranking is supported.** The top three categories' intervals overlap one another completely, so their ordering is not determined by these data. Only design's separation from the top of the distribution is robust. We say this in Section 4.3 and repeat it here because point-estimate orderings are what get quoted onward.

**The quantity margins return nulls with wide bounds.** No category's sales rate broke by more than roughly **±23% to ±66%** after ChatGPT, and dormancy is likewise null once trend and composition are held fixed. These bounds are informative—they rule out very large effects—but they do not distinguish a moderate effect from none. The **raw** dormancy ranking (writing +6.1pp, marketing +5.6, audio +5.0, translation +5.0) reverses sign for three of seven categories under the adjusted specification and must not be quoted.

**The one identified design is underpowered.** The gig-level exposure difference-in-differences passes parallel trends but returns a 95% interval of **−14.8% to +87.6%** on the high-versus-low contrast. It cannot distinguish "AI did nothing" from "AI did a great deal."

**And scale does not rescue it.** Re-estimating the pre-registered exposure specification on the full balanced panel — **169,337 gig-quarters across 15,676 gigs**, roughly fifty times the pilot — returns `Exposure × Post` = −0.0333 ($t$ −1.35), still **below its own minimum detectable effect of 0.0689**. Extending four quarters further on recovered 2025 data moves it to −0.0324. At that scale the design also *loses* two gates it passed on the pilot: parallel trends fails (4 of 11 pre-launch interactions significant) and the coefficient reverses sign when raced against a linear trend. We therefore state a limitation more serious than low power: **on this platform the pre-registered design is not identified**, because every category is treated to some degree and a category-specific trend explains the exposure gap better than the launch date does. A larger crawl inherits this defect; what a successor design needs instead is a genuine control group of categories no capability improvement should plausibly touch, specified in §7.

**The 2025 and 2026 points on every series are continuity checks, not measurements.** Matched-pair counts collapse after 2024Q3 for the reasons given in §4.9 — the realised-order series alone falls from 40,393 orders in 2024Q3 to 420 in 2026Q1. Category-level results in this paper are identified through **2024Q3** and the composite through **2024Q4**. Points beyond that are plotted for continuity and must not be read as evidence about the post-2024 market, in either direction.

### 6.2 Survivorship: the paper's most serious unresolved threat

The matched-model design eliminates compositional confounds by holding the gig fixed, but it thereby follows **ageing incumbents**, and this cuts against the paper's headline in a way we cannot currently bound.

New gigs entering with ≤10 reviews at first capture show **flat prices from 2019 to 2025** in design, writing, video and marketing, while the incumbent index over the same span rises **+47% to +167%**. If the market's *entry* price is flat while its *incumbent* price climbs, the index is measuring the life-cycle of surviving gigs at least as much as the price of the service. We cannot yet settle how much, because the two crawls give different entry medians for the same year (2024: \$50 on n=102 versus \$30 on n=2,389), so the series must be built within a crawl or the frames reconciled first. Until that is done, **the entry-price gap is an open problem, not a decomposition**, and the index should be read as a price for continuing gigs rather than for the category.

This interacts with the difference-in-differences design of Section 4.8 in a way worth stating explicitly: within-gig first differences **condition on survival**, so if highly exposed gigs *exit* rather than cut price, the design returns a null by construction. The observed null is exactly what that would produce. The entry-price companion series is therefore a prerequisite for the causal design, not a robustness check on it.

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

**Price is not transaction value, and the partial answer has its own limits.** The index measures the posted Basic-tier price, not what buyers paid. Section 4.6 narrows this gap for the first time using 681,668 realised orders recovered from archived pages, and finds the realised distribution flat over 2022–2026 on every band whose definition is stable. That evidence carries four constraints of its own, stated there and repeated here because they bound what it settles: it is **silent on the sub-\$50 segment**, roughly half of all orders and unmeasurable before 2024 — which is precisely the thin, cheap end a commoditization hypothesis concerns; it samples roughly 4 of a median 124 reviews per page under Fiverr's own relevance ranking, and **display selection remains untested**; the gig set changes each quarter and thins sharply after 2024Q3; and it is a different price object from the IPI that must never be chained onto it.

**Quality adjustment remains unsolved.** A seller who uses AI to raise output quality at an unchanged price has experienced quality-adjusted deflation neither series captures; a seller who raises prices because AI lets them bundle more work may show inflation even as price-per-unit-of-value falls. This is the oldest problem in index construction and nothing here addresses it. It is the single largest reason to be cautious about reading either flat series as evidence that AI did not affect this market: **a constant price for a changing product is not a constant price.**

**A known data defect in a field we do not use for the index.** The `rating` column carries a scale error—217 historical rows report values in (5, 10] because pre-2019 Fiverr displayed a 10-point scale that the extractor wrote into the same column as the 5-point one. It does not affect the index, which uses prices only, and it does not move the hedonic result of Section 3.8 (only 167 affected rows survive to a gig's latest capture), but any future row-level use of `rating` on this data must correct it first.

### 6.6 The data source closed during the study

This paper's instrument depends on a third party continuing to archive a commercial website, and over the study period that dependency failed. Section 4.9 reports the measurements: Internet Archive 403 rates on this domain rise from 1.0% (2025Q4) to 89.3% (2026Q2); adjacent-quarter revisit rates fall from a stable 74–82% across 2018–2024 to 44.1% in 2025 and 34.5% in 2026; and a full re-collection of the 2025–2026 window raised matched pairs across the seven published domains by a factor of 1.01, moving no figure in this paper. Common Crawl, the obvious alternative, never crawled the site's gig pages at all.

Three limitations follow. **The post-2024 window is not recoverable retrospectively** — not by us, and not by a better-resourced replication, which is an unusual property for a limitation to have. **The paper's null results are therefore confounded with the closure**: in-market AI diffusion on this platform dates to 2023Q1, so the archive supports roughly six quarters of post-treatment observation on a treatment that had barely spread, and we cannot distinguish that from a true absence of effect. And **the archive's own selection changes over the window** in ways we can measure but not correct: capture volume falls roughly eightfold from 2026Q1, and what survives is not a random subsample of what came before.

We report this as a finding about the infrastructure of economic measurement rather than as an inconvenience. It is also the reason the collection design in §6.3 is the most perishable contribution here: it is only executable going forward.

### 6.7 What this paper does not claim

We do not claim to have identified an effect of AI on the price of cognitive labor. The index rises in real terms; reputation accumulation and general inflation account for a large and imprecisely bounded share of that rise; the residual is not separately attributable; and every margin that might have separated the categories returns either a wide interval, a failed identification test, or a structural impossibility.

**We equally do not claim to have shown that AI had no such effect**, and we want to be explicit because two flat series invite that reading. Both nulls are silences. The posted-price estimate is smaller than the minimum effect its design could detect. The realised-value series is silent on the sub-\$50 segment where an effect is most expected, and neither series is quality-adjusted, so a constant price for a changing product would appear here as no change at all. The observation window also closes roughly six quarters after in-market diffusion begins. Any of these alone would prevent the inference; together they make it unavailable.

The contribution is the instrument, the bounds, the two artifacts we document at length because they would mislead the next person to touch this data, and the design requirements—not the causal claim the instrument was built to eventually support.
