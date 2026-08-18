## 2. Data

### 2.1 The panel

The frame is a longitudinal archive of Fiverr listing pages retrieved from the
Internet Archive and parsed into listed package prices. After applying the
listing filter and dropping unpriced captures, the working panel is:

| | |
|---|---:|
| listing-quarter observations, 2019Q3–2024Q4 | **257,208** |
| distinct listings | **37,888** |
| distinct sellers | **29,835** |
| listings observed both before and after 2022Q4 ("fixed panel") | 16,206 |
| listings in ≥80% of quarters 2020Q3–2023Q4 ("balanced panel") | 2,765 |

**Terminology.** We say **listing** for what the platform calls a *gig* (a single
priced service offering, which a seller may hold several of) and **sales proxy**
for cumulative review count, which is what the archive records in place of
transactions. The analysis scripts use the platform's own word, `gig`.

One observation per listing-quarter, taking the latest capture in the quarter.
Each observation carries the basic, standard and premium package prices, the
displayed rating, and the cumulative review count.

The price index used for the level results in §4.1 is a matched-model
GEKS-Jevons index estimated on the same archive over 2020Q1–2026Q1 [CITE-ipi];
this paper takes its published figures as given rather than re-estimating them.

### 2.2 Window, and why it is not longer

**Start 2019Q3.** Price extraction is 100% `packageList` from that quarter
onward. Before it the frame is a three-way mix of parse paths whose three-tier
detection rates differ by 19 percentage points, so any versioning series crossing
that seam is a parser artefact rather than a fact about menus.

| quarter | packageList | old JSON | dollar fallback |
|---|---:|---:|---:|
| 2018Q3 | 11.8% | 40.7% | 47.4% |
| 2019Q1 | 41.8% | 26.1% | 32.0% |
| 2019Q2 | 75.5% | 10.9% | 13.6% |
| **2019Q3** | **99.8%** | 0.0% | 0.1% |

From 2019Q3 on, the `packageList` share never falls below 99.7%.

**End 2024Q4.** Captures per quarter collapse from roughly 9,300 to roughly 700
after it, and every category's measured sales proxy drops steeply into the edge.
Results that appear only in 2024 are treated as trailing-edge artefacts until
shown otherwise — which is what disposes of the apparent concentration result in
§4.5.

### 2.3 Two sampling properties that determine how every number must be read

**The manifest is quota-sampled** on (category, adjacent quarter pair). A
within-quarter cross-section is therefore *not* a random sample of live listings,
and counts such as listings per seller are properties of the sample rather than
of the platform. Every claim about change over time is read off a fixed or
balanced panel, and both columns are printed throughout.

**Listing fixed effects do not protect against composition.** This is not a
formality: the quota manifest adds roughly 1,250 net listings at 2022Q3 and the
added ones are cheaper. On all listings the ≤\$10 share **jumps +5.7pp at 2022Q3**
— one quarter before the break of interest — and a level-shift search then reports
a significant *positive* break at 2022Q4. On a strictly balanced panel of 3,106
listings present in all seven quarters 2021Q4–2023Q2, the same series falls
monotonically, 19.8% → 19.1% → 18.6%, with no jump at all.

### 2.4 External transaction data

The archive contains no transactions. The one source of realised quantities is
the platform operator's reported metrics, where GMV = active buyers × spend per
buyer is an accounting identity rather than an estimate: it reproduces every
independently reported GMV figure to within rounding (2022: 4.2M × \$262 =
\$1,100M against \$1,090M reported). Revenue is not a substitute, because it also
carries Pro, subscriptions, advertising and acquired services — 2024 revenue over
GMV is 36% against a 27.6% take rate.

### 2.5 Exposure measure

AI exposure is external to our data by construction: occupation-level exposure
ratings from [CITE-eloundou2023] (923 O\*NET-SOC occupations), used two ways —
as a pre-registered ranking of the seven categories, and as a continuous
gig-level score built by TF-IDF cosine similarity between cleaned listing titles
and occupation titles, taking the similarity-weighted mean of the top K = 3
matches (§5.6). **36.8% of listings get a zero match**, and the dropped listings
accrue 23.7% more pre-period sales proxy than the kept ones — a selection threat
declared in the pre-registration before estimation, not discovered afterwards.

### 2.6 What these data cannot measure, at any effort

- **Entry and exit.** `n_404 = 0` across 509,339 captures: the crawl records no
  removals. Nothing in this paper is labelled entry or exit. For a competitive
  structure question this is the single largest gap, because entry is where a
  commoditising shock would usually appear first.
- **Realised order value.** The index reads listed basic-package prices. The
  buyer-mix evidence in §4.2 suggests realised prices rose *faster*, so every
  quantity figure derived by dividing spend by price is an **upper bound on the
  quantity decline**.
- **Sales.** `review_count` is a proxy for sales, not sales.
- **Category detail in the external data.** The operator publishes no category
  split, so §4.2 is platform-wide only.
- **Anything after 2024Q4** on the structural margins.
