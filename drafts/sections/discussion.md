## 5. Discussion

### 5.1 What a price index adds to the AI-and-labor literature

The empirical AI-labor literature has two dominant instruments. **Exposure indices** [CITE-eloundou-2023, CITE-felten-2021, CITE-webb-2020] score occupations or tasks by what a model could in principle do; they are available immediately, cover the whole economy, and are judgments rather than observations. **Platform outcome studies** [CITE-hui-reshef-2023, CITE-demirci-2024] observe real markets—earnings, posting volume—but at aggregates that mix price and quantity and that arrive with a lag.

A price index sits between them and answers a question neither does: *conditional on the work still being sold, what does it cost?* That conditioning is the point and also the catch. Holding the gig fixed is what makes the comparison meaningful across periods, and it is also what makes the index blind to the margin where displacement would most plausibly appear. We show in Section 4.5 that this is not a hypothetical concern: entry prices are flat over the same span in which the incumbent index rises 47–167%.

The honest description of what we have built is therefore narrower than "a measure of AI's effect on cognitive labor." It is a well-measured intensive-margin price series with an explicit accounting of its confounds, plus quantified bounds on the extensive margins it cannot see. We think that is worth having, and we think overselling it is what would make it worthless.

### 5.2 Reconciling a rising price with a disruption narrative

The single most counterintuitive result is that the price of cognitive services on this platform **rose substantially in real terms** across exactly the period in which generative AI became widely capable. Four readings are consistent with our data, and we cannot distinguish among them.

**Reading 1: composition within the survivor set.** The index follows continuing gigs. If AI displaced the low end of each category, surviving gigs would be systematically more complex over time, and a matched-model index reads that as price growth. Our matching holds the gig identifier fixed, which blocks entry-mix effects but not a *gig* repositioning upmarket while keeping its URL.

**Reading 2: reputation, not price.** Within-gig prices rise +7.7% per doubling of reviews, and the reputation-adjusted composite is +39.7% against +79.0% raw. A large share of what the index calls price growth is a gig ageing on the platform. Because reviews are cumulative sales, this reading and an AI-suppressed-demand reading are entangled by construction—which is why we publish a band.

**Reading 3: general inflation and platform maturation.** CPI-U accounts for roughly half the nominal rise, and Fiverr's transition from a "\$5 for everything" marketplace to a professional services platform is visible in the raw medians (Section 4.1). Both are real and neither is about AI.

**Reading 4: genuine complementarity.** Sellers who use AI tools may deliver more per gig and price accordingly. This is the reading the earlier version of this work adopted, and we now think the data cannot support choosing it over the other three.

What we can say is that the residual left after removing inflation and reputation is **smaller than the headline and not separately identified**. A reader who wants a one-line summary should take: *prices for continuing cognitive-service gigs rose in real terms; most of the rise is attributable to inflation and reputation accumulation; what remains is not large enough, relative to its uncertainty, to adjudicate between complementarity and no effect.*

### 5.3 Why the negative results are the transferable part

Three of our findings generalize beyond Fiverr and beyond this window.

**Archival price data has a specific and severe failure mode.** Section 4.6 documents a defect that moved the composite by 26 percentage points in real terms and inverted the direction of the recent trend in six of seven categories. It arose because a platform's own landing pages share the URL grammar of its product pages, and because a widget default was parsed as a price. Nothing about the extraction pipeline was obviously wrong; the artifact was found only because a category-level move looked implausible against individual gig charts. Any project building prices from web archives should expect a defect of this class and should audit by URL family and by page shape independently, as we did.

**Multilateral indices can be unidentified on sparse panels, and the standard diagnostics do not reveal it.** GEKS is drift-free, which is why we use it, but its level for a quarter is an average over link paths, and where only two to five paths exist the level is a property of which paths happened to survive. We found that the matching threshold, the base quarter, and the estimation window are three faces of one sensitivity, and that the published growth over a *fixed* span moves by up to 76% as a function of where estimation *starts*. Bootstrap standard errors do not detect this: coding's band is ±61% while a one-step threshold change moves its level by +129%. Practitioners should report link-path support per quarter alongside standard errors.

**A trending price index regressed on a trending capability score will produce a significant coefficient regardless of whether any relationship exists.** Section 3.9 gives the full diagnostics. We emphasize it because the specification is intuitive, easy to run, and produces a headline number with a memorable name. Our own earlier draft reported it. The minimum defenses are a placebo regressor with no substantive content, a first-differenced specification, and a serial-correlation diagnostic; the specification failed all three.

### 5.4 Comparison to prior work

Our results are compatible with the platform-level literature once the margin is made explicit. Hui, Reshef and Zhou [CITE-hui-reshef-2023] report a 5.2% earnings decline for writing freelancers after ChatGPT; we find writing's *posted price* rising (+59.2% real over our window) with no detectable break in its sales rate (−3%, $|t| < 1.1$, minimum detectable ±27%). These are not in conflict: earnings are price × quantity over all sellers, while we measure price for continuing gigs, and our bound on the quantity margin is far too wide to rule out a decline of the magnitude they report. Demirci, Hannane and Zhu [CITE-demirci-2024] document a 21% fall in postings for automation-prone tasks—an extensive-margin result that our crawl construction makes us structurally unable to check (Section 4.5).

The methodological reference class is online price measurement rather than the AI literature. The Billion Prices Project and successors [CITE-cavallo-rigobon-2016, CITE-cavallo-2017] established that scraped web prices can support serious index work provided coverage and matched-item counts are reported honestly; our contribution to that line is a demonstration of what happens when matched-item counts fall to single digits, and a stated adequacy criterion for deciding when they have.

### 5.5 Implications, stated at the confidence they warrant

**For measurement.** A cognitive-labor price index is feasible from public archival data, at meaningful precision, for a well-sampled category. It is not feasible at ±5% for thin categories at pilot scale, and the shortfall is a sample-size problem with a known solution rather than an estimator problem.

**For the AI-and-labor literature.** Price and quantity margins should not be substituted for one another. Our price series rises while the quantity margins are null and the extensive margin is unobservable; a study reporting any one of these alone would tell a confident and different story.

**For platforms and policymakers.** We are not able to offer a category-level early-warning signal, and we would caution against treating point-estimate orderings from data of this precision as one. What we can offer is the design specification in Section 6.3: an index of this kind becomes a leading indicator only if the underlying collection records non-resolving URLs and does not select on survival.
