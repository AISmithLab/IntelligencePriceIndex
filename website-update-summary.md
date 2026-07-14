# Website changes & the fixed-effects price index

**Intelligence Price Index — project update**

- **Prepared:** 14 Jul 2026
- **Site:** aismithlab.com/IntelligencePriceIndex
- **Branch:** mockup

A summary of the recent work on the IPI site, and the method it now uses to correct for freelancers being sampled at uneven times.

---

## What changed on the site

Recent work centered on the second chart — the fixed-effects index — plus its documentation, data validation, and a new per-category gallery.

### Live on the site

- **Per-category Gallery page.** One card per category showing its fixed-effects price trend (with a 95% confidence band) alongside a real featured gig's package-price history and a Wayback link.
- **Confidence bands on the fixed-effects chart.** Per-quarter regression standard errors now draw a shaded 95% band — wide for thin categories (translation ±34%), tight for dense ones (design ±4%).
- **Price-extraction validation.** An independent spot-check (n=300) confirms 100% presence and reproducibility; the displayed 2020Q1+ window validates at 100%. Remaining noise is confined to a pre-2017 era the charts don't show.
- **Chart & header polish.** The fixed-effects chart got its own quarter dropdown and readout; the page header was condensed to two boxes; the quarter readout now lists the composite plus all seven categories.

### In progress (edited, not yet published)

- **Plain-language method in the FAQ.** A new "Step 5" explains the fixed-effects correction with a worked two-gig example.
- **Gallery ordering uses the drift-free number.** Category badges and card order now use the fixed-effects change (`delta_tpd`) so they agree with the trend chart, instead of the naive chained change that overstates thin panels.
- **Paper & tests updated.** A robustness paragraph added to the Methods section (§3.4); the section's reviewer-simulation tests now pass for the irregular-sampling critique.

---

## The fixed-effects index

*How the site accounts for gaps in time coverage across different gigs — the second chart on the home page.*

### The problem

The main index is a **chained matched-model (Jevons) index**: each gig is compared only between the consecutive quarters we actually captured it in. But Wayback Machine snapshots are irregular — some gigs are caught every quarter, others once every year or two. When a gig disappears for several quarters and returns at a new price, the chain is forced to dump that entire multi-quarter change into the single quarter it reappears. That creates spikes that **mislocate when prices actually moved.**

| | Naive chained index | Fixed-effects index |
|---|---|---|
| **Where the change lands** | All in one quarter — the moment the gig was re-observed (a spike) | Spread across the quarters it truly spanned (a smooth path) |
| **Timing** | Wrong | Trustworthy |

Roughly **26% of historical** and **39% of recent** price changes span such a sampling gap — a measure of how much timing the naive chain was getting wrong.

### The method — a time-product-dummy (two-way fixed-effects) regression

For each category we fit a single pooled regression on log prices, estimating every quarter's price level jointly from every gig at once:

$$\ln p_{i,t} = \alpha_i + \delta_t + \varepsilon_{i,t}$$

- **α_i — the gig effect** absorbs each service's own price *level*, so a \$5 gig and a \$500 gig can be pooled and only their percentage moves count.
- **δ_t — the quarter effect** is the common price level in quarter *t*. Because all quarters are solved *simultaneously*, a rarely-seen gig only constrains the difference between its two observed quarters — and that difference is allocated across the intervening quarters through other, densely-observed gigs that span the same periods.
- **ε_{i,t} — the residual.** The published index for quarter *t* is `100 × exp(δ_t)`, with the base quarter pinned to zero.

The upshot: the gigs we captured frequently reveal the true *shape* of the price path, and the regression uses them to place each rarely-captured gig's change in the quarter it occurred, rather than the quarter of re-observation.

### Safeguards so gaps aren't guessed

- **Connectedness.** A quarter is included only if it links back to the base period through overlapping gigs (the largest connected component of the gig–quarter graph). Disconnected quarters are dropped rather than guessed.
- **Density thresholds.** A quarter needs at least 3 distinct gigs, and a gig at least 2 observations, to earn an effect.
- **Capture-frequency neutrality.** Multiple snapshots within one quarter collapse to the gig–quarter median, so a heavily-archived gig doesn't count more than a lightly-archived one.
- **Honest uncertainty.** Each quarter carries a regression standard error, so quarters resting on thinner samples get visibly wider confidence bands.

The two indices track closely in level — but the fixed-effects specification removes the spurious quarter-to-quarter spikes the naive chain produces under sparse sampling, so the *timing* of price movements is trustworthy.

---

*Implementation: `code/19-tpd-index.py` (estimation), `code/18-build-site-data-long.py` (splice into the site data), `docs/ipi.js` (chart). Documented in Methods §3.4 and FAQ Step 5.*
