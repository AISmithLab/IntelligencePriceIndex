## 3. Data and Methods

### 3.1 Data Source: Fiverr via the Wayback Machine

Our primary data source is archived Fiverr gig pages retrieved from the Internet Archive's Wayback Machine. Fiverr is the world's largest marketplace for freelance digital services, with sellers offering standardized "gigs" at posted prices across categories including writing, graphic design, programming, video production, translation, and marketing. Three features make Fiverr particularly well-suited for constructing a price index of cognitive labor:

1. **Posted prices.** Unlike platforms where prices are negotiated per-project (e.g., Upwork), Fiverr gigs have explicit, publicly visible price tiers (Basic, Standard, Premium). These are *revealed prices*—set by sellers in response to market competition—not survey responses or expert estimates.

2. **Granular task decomposition.** Fiverr's category structure maps naturally onto the task-level analysis that the AI-labor literature emphasizes [CITE-autor-levy-murnane-2003, CITE-acemoglu-restrepo-2019]. A "gig" represents a specific, well-defined cognitive task (e.g., "write a 1000-word blog post," "design a minimalist logo," "translate 500 words English to Spanish"), making prices directly comparable across time.

3. **Longitudinal coverage.** The Wayback Machine has archived Fiverr pages extensively since 2011, providing over a decade of snapshots that predate the generative AI era. This pre-treatment baseline is essential for identifying the causal effect of AI capability improvements on prices.

### 3.2 Sample Construction

We constructed our dataset through a multi-stage pipeline:

**Stage 1: CDX Index Retrieval.** We queried the Wayback Machine's CDX API for all archived URLs matching `fiverr.com/*` gig page patterns, retrieving **60 million raw index entries** covering the full archival history.

**Stage 2: Deduplication and Filtering.** We deduplicated entries by URL and timestamp, retaining unique (URL, month) combinations. We then classified URLs into 9 service categories using keyword matching on URL slugs and filtered to gigs with longitudinal coverage (≥5 monthly snapshots spanning ≥2 years). This yielded **48,643 qualifying sellers**.

**Stage 3: Pilot Sampling.** From the qualifying pool, we drew a stratified random sample of **500 sellers**, generating a download manifest of **26,603 monthly snapshots** across **14,938 unique gigs**.

**Stage 4: HTML Download.** We retrieved archived HTML pages from the Wayback Machine at a rate-limited 12 requests/second with exponential backoff retry logic. Of 26,603 manifest entries, **22,632 (85.1%)** were successfully downloaded; the remainder returned 404 errors (page archived in index but content no longer available), consistent with normal Wayback Machine attrition rates.

**Stage 5: Price Extraction.** We extracted prices from downloaded HTML using a cascade of four methods ordered by reliability:

| Method | Era | Mechanism | Success Rate |
|--------|-----|-----------|-------------|
| `packageList` JSON | 2020+ | Embedded JSON array with price in cents | 72.9% |
| Old-style JSON | Pre-2017 | JSON with price as string dollars | 15.2% |
| HTML `<span>` | 2018–2020 | `class="price"` DOM elements | 0.7% |
| Dollar fallback | All eras | `$X` pattern in page text | 11.2% |

Extraction succeeded on **100% of downloaded files** (22,632/22,632), yielding price observations spanning 2011–2026.

**Stage 6: Deduplication to Unique Gigs.** Many of the 14,938 manifest gigs map to the same seller-slug combination observed across multiple snapshots. After collapsing to unique (seller, slug) pairs with at least one valid price extraction, we retain **1,908 unique gigs** across the 500 sellers.

**Stage 7: Service Item Clustering.** To construct CPI-style "items" (comparable service bundles), we clustered 1,908 unique gigs into **150 service items** using TF-IDF vectorization of cleaned gig titles with agglomerative clustering (cosine distance, average linkage). Examples: "logo design" (73 gigs), "WordPress website" (62 gigs), "voice narration" (47 gigs). Silhouette score at the optimal k=150 was 0.114.

**Stage 8: Panel Construction.** For the matched-model IPI, we retain only gigs observed in at least two quarters, yielding a final panel of **1,245 gigs** with **21,461 price observations**.

The full data pipeline: 60M raw CDX entries → 22.7M deduplicated → 48,643 qualifying sellers → 500 sampled → 26,603 manifest snapshots → 22,632 downloaded → 1,908 unique gigs with prices → 1,245 panel gigs → 21,461 panel observations.

### 3.3 Category Classification

We classified gigs into 9 broad service categories using keyword matching on gig descriptions and cluster labels: writing, coding, design, translation, video, audio, marketing, data entry, and data analysis. The distribution of the final panel is:

| Category | Panel Gigs | Observations | Weight |
|----------|-----------|-------------|--------|
| Design | 313 | 6,957 | 0.464 |
| Video | 158 | 2,704 | 0.138 |
| Writing | 226 | 3,388 | 0.120 |
| Coding | 184 | 3,152 | 0.083 |
| Audio | 62 | 1,181 | 0.076 |
| Marketing | 71 | 1,272 | 0.051 |
| Data Entry | 46 | 561 | 0.028 |
| Translation | 26 | 277 | 0.025 |
| Data Analysis | 38 | 542 | 0.016 |

Weights are computed from maximum observed review counts per category (a proxy for transaction volume), normalized to sum to 1, analogous to CPI expenditure weights.

### 3.4 Index Construction

We construct the IPI using a **matched-model panel approach**, following the methodology the Bureau of Labor Statistics uses for CPI items where direct quality adjustment is difficult [CITE-bls-handbook-2018].

**Elementary aggregates (within category).** For each gig observed in two or more quarters, we compute the price relative $r_{i,t} = p_{i,t} / p_{i,t-1}$ for each consecutive pair of observed quarters. We filter extreme outliers (price changes exceeding 10×) and require a minimum of 3 gig-level observations per category-quarter pair.

The category-level elementary price index is the **Jevons index** (geometric mean of price relatives), chained quarter-to-quarter:

$$I^c_t = I^c_{t-1} \times \left( \prod_{i \in S_{c,t}} r_{i,t} \right)^{1/|S_{c,t}|}$$

where $S_{c,t}$ is the set of gigs in category $c$ observed in both quarter $t-1$ and quarter $t$. The geometric mean is preferred over the arithmetic mean because it handles the asymmetry between price increases and decreases (the Jevons formula satisfies time-reversal symmetry) and is the BLS's standard for elementary CPI aggregates [CITE-bls-handbook-2018].

**Composite IPI.** The composite index aggregates category indices using a **Törnqvist-style weighted geometric mean**:

$$\text{IPI}_t = \exp\left( \frac{\sum_c w_c \ln I^c_t}{\sum_c w_c} \right)$$

where $w_c$ is the category weight based on transaction volume. We set 2019Q1 as the base period (IPI = 100), chosen because it predates major generative AI deployments while having sufficient data density across categories.

**Chain drift and the multilateral (GEKS-Jevons) index.** The chained index above compares each gig only between its *consecutive observed* quarters, so the matched sample $S_{c,t}$ differs from link to link. Because Wayback Machine captures are irregular, gigs are sampled at heterogeneous frequencies and over different, only partially overlapping windows: when a gig is observed in quarter $t$ and not again until $t+k$, its entire multi-quarter price change is attributed to a single transition (approximately 26% of historical and 39% of recent price changes are such gap-spanning transitions). The resulting link-level errors do not cancel—they compound multiplicatively along the chain, the phenomenon known as **chain drift** [CITE-ivancic-diewert-fox-2011]. In our data the effect is first-order, not second: the chained composite rises 217.7% over 2020Q1–2026Q1 against 44.6% for the drift-free estimate, a level ratio of 2.2× by 2026Q1.

We therefore estimate the reported index with **GEKS-Jevons**, the multilateral estimator introduced by Ivancic, Diewert and Fox [CITE-ivancic-diewert-fox-2011] precisely to eliminate chain drift in high-frequency scanner data. For each ordered pair of quarters $(s,t)$ we form the direct bilateral Jevons comparison over the gigs matched in both,

$$P_{s,t} = \exp\left( \frac{1}{|S_{c,s,t}|} \sum_{i \in S_{c,s,t}} \ln \frac{p_{i,t}}{p_{i,s}} \right),$$

and then make these bilaterals transitive by taking the geometric mean of the direct comparison with every indirect route through a link quarter $\ell$:

$$I^c_t = 100 \times \prod_{\ell \in L_{c}} \left( P_{0,\ell} \cdot P_{\ell,t} \right)^{1/|L_{c}|},$$

with $0$ the base quarter. Because each gig's price *level* cancels inside the ratio $p_{i,t}/p_{i,s}$, gigs at very different price points are pooled without any level term to estimate; and because there is no chain, there is nothing along which error can accumulate. GEKS is the appropriate multilateral choice for our setting: we observe posted prices but no quantities or expenditure shares at the gig-quarter level, which rules out GEKS-Törnqvist and Geary–Khamis and leaves the unweighted Jevons bilateral that the ILO CPI Manual recommends for elementary aggregates when quantity information is unavailable [CITE-ilo-cpi-manual-2004].

*Sample construction and estimation window.* We collapse multiple within-quarter snapshots to their gig-quarter median (neutralizing differences in capture frequency), require at least 2 observed quarters per gig and at least 3 distinct gigs per quarter, and require at least 3 matched gigs for a bilateral $P_{s,t}$ to be used (`MIN_MATCH = 3`, matching the minimum-relatives rule applied to the chained index). Estimation runs over the reported 2020Q1–2026Q1 window rather than the full 2011– panel: quarter $t$ is reachable from the base only when both $P_{0,\ell}$ and $P_{\ell,t}$ are populated, and the pre-2015 quarters hold 2–4 gigs per category, which leaves most later quarters unidentified when included. Restricting to the published window—already standard practice for GEKS, and here coincident with the base period—yields full coverage in six of seven categories. We report bootstrap standard errors (200 replications resampling gigs with replacement), since the averaged bilaterals admit no closed-form joint variance; the resulting 95% bands are ±7.6% for design and ±10.3% for writing, widening to ±24–26% for the thin audio, marketing and translation panels.

*Comparison with the imputation alternative and known biases.* The natural regression alternative, a time-product-dummy (two-way fixed-effects) specification $\ln p_{i,t} = \alpha_i + \delta_t + \varepsilon_{i,t}$, is also drift-free and yields a composite change of 66.1% ($r = 0.983$ with GEKS across categories, mean absolute difference 9.4 index points). The two differ only through imputation: the time-dummy index is implicitly an *imputation* index that collapses to the matched-model index under complete data [CITE-de-haan-2004], and our gig-quarter panel is only 10.9% filled, so the regression imputes roughly 89% of cells under a constant-$\alpha$ assumption. We prefer GEKS, which declines to impute and uses matched pairs only; the 66.1%-versus-44.6% gap is the price of that assumption rather than an arithmetic disagreement. The principal documented weakness of GEKS—downward bias when disappearing products are dumped at clearance prices, to which TPD is insensitive [CITE-chessa-verburg-willenborg-2017]—we test rather than assume: a gig's *final* observed price change averages $+0.090$ log points against $+0.070$ for its other transitions ($t = 1.34$, n.s.), with no category showing a significant terminal drop. This is expected structurally, since 99% of gigs cease to be observed mid-panel, making "disappearance" an artifact of crawl attrition rather than seller delisting. We use the full-window rather than a rolling-window variant [CITE-krsinich-2016] because this is a retrospective research index over a fixed window with no published history to revise, so full-window estimation uses all available data and avoids an arbitrary splice.

*Implementation validation.* Our implementation reproduces the `PriceIndexCalc` reference implementation exactly (maximum absolute difference 0.0000 index points, correlation 1.0000) on the four categories the reference can process. It fails on the remaining three with a division-by-zero: coding, design and translation contain quarter pairs sharing *zero* matched gigs (25 of translation's pairs, 15%), which the reference assumes cannot occur. Averaging over available link routes only, as we do, is therefore a requirement of this panel's sparsity rather than a stylistic choice.

### 3.5 AI Capability Measurement

We construct category-specific AI capability indices from published benchmark scores:

| Category | Benchmarks Used | Source |
|----------|----------------|--------|
| Coding | HumanEval, SWE-bench | evalplus.github.io, swebench.com |
| Writing | AlpacaEval 2.0, Chatbot Arena Elo | tatsu-lab GitHub, lmsys.org |
| Translation | WMT BLEU | statmt.org |
| Design | FID (MS-COCO) | Published papers |
| Data Analysis | GSM8K | llm-stats.com |
| Audio | Whisper WER | OpenAI papers |
| Marketing | AlpacaEval 2.0 | tatsu-lab GitHub |

For each category, we average across relevant benchmarks and normalize to a 0–100 scale (min-max over the observation period). We interpolate benchmark scores to quarterly frequency using linear interpolation between release dates. For FID and WER (lower is better), we invert the scale so that higher values indicate greater capability.

### 3.6 Econometric Specification

**Price elasticity of intelligence.** We estimate the following log-log specification:

$$\ln(I^c_t) = \alpha_c + \beta_c \ln(A^c_t + 1) + \varepsilon_{c,t}$$

where $I^c_t$ is the category price index and $A^c_t$ is the normalized AI capability index. The coefficient $\beta_c$ is the **price elasticity of intelligence** for category $c$: the percentage change in the category price index associated with a 1% improvement in the AI capability index. The +1 offset in the log of AI capability handles zero baseline values.

A negative $\beta_c$ indicates that AI improvements are associated with price deflation (substitution dominates). A positive $\beta_c$ indicates that prices rise alongside AI capability (complementarity dominates, or the category experiences general inflation that outweighs any AI-driven deflation). We estimate this specification separately for each category using OLS, reporting heteroskedasticity-robust standard errors.

**Structural break analysis.** To assess the immediate impact of major AI model releases, we compare category price indices in the 4 quarters before and 4 quarters after each event (ChatGPT: November 2022; GPT-4: March 2023; Stable Diffusion: August 2022; GPT-4o/Claude 3.5: June 2024), computing the percentage change in the mean index level.
