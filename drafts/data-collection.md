# Data Collection — the complete account

**What this is.** The full record of how the IPI's data was collected: source selection,
scoping, the pipeline stage by stage with the parameters needed to re-run it, every
revision the collection went through, the ceilings the archive imposes, and the two
enlarged collections that contribute nothing to the current paper.

**Relationship to the paper.** §3.1–3.2 of `drafts/sections/method.md` is the publishable
compression of this document. Where the two differ in emphasis, `method.md` is the paper
and this is the appendix. **Where they differ in a number, `method.md` wins** — it is
governed by the frozen table (`data/pilot/paper-numbers.md`, enforced by
`code/32-check-draft-numbers.py`); this file is not, and it deliberately carries
operational figures that are not paper figures.

**Structure.** Follows `drafts/templates/data-collection-section.md`.

**Last updated:** 2026-08-10. Collection status as of this date is in §6.

---

## 1. Source and window

### 1.1 The source

Archived Fiverr gig pages retrieved from the Internet Archive's Wayback Machine. Fiverr
is the largest marketplace for freelance digital services, and sellers offer standardized
"gigs" at posted price tiers (Basic, Standard, Premium) across writing, design,
programming, video, translation, audio and marketing.

Three properties make it suitable, each tied to a requirement the estimator has rather
than to a generic virtue:

1. **Posted prices.** Prices are set by sellers and publicly visible, not negotiated per
   project as on Upwork. A matched-model index needs a price attached to a persistent
   item; a negotiated platform has no such object.
2. **Granular task decomposition.** A gig is a specific, well-defined task ("write a
   1000-word blog post", "design a minimalist logo"), which is the unit the AI-and-labor
   literature works in and which makes prices comparable across time.
3. **Longitudinal coverage.** The Wayback Machine has archived Fiverr since 2011,
   predating the generative AI era by a decade.

### 1.2 The qualification that constrains everything downstream

The third property is weaker than it appears. **The archive is an opportunistic crawl,
not a sampling frame.** Pages are captured when the Internet Archive happens to capture
them, at rates varying by page popularity and by year, and nothing about the resulting
density is designed.

In the pilot manifest the consequence is severe at the early end. Distinct gigs per
quarter run 9, 12, 23 and 43 across 2016Q1–Q4 and 18 in 2017Q1, against 408 in 2020Q1.
**2017Q2, 2017Q4, 2018Q1 and 2018Q2 contain no captures at all.**

The matched chain is not merely thin there but *severed*. Measured over the whole index
rather than a sample (`code/40-history-headroom.py`), matched gigs per adjacent quarter
pair — the unit a chained matched-model index actually consumes:

| link | matched gigs | link | matched gigs |
|---|---:|---|---:|
| 2015Q3→Q4 | 18 | 2018Q1→Q2 | 4 |
| 2016Q3→Q4 | 2,277 | 2018Q2→Q3 | 10 |
| 2017Q1→Q2 | **5** | 2018Q3→Q4 | **8,084** |
| 2017Q3→Q4 | **1** | 2019Q4→2020Q1 | 28,838 |

2017Q1 holds 5,451 snapshots and yields **5** matched gigs: Wayback re-crawled the site
but almost never the same gig twice across those boundaries. In the pilot panel the same
collapse appears as 2017Q1→2017Q3 and 2017Q3→2018Q3 sharing **zero** matched gigs, with
only 65 of 1,066 historical panel gigs observed on both sides of the gap.

**2018Q3 is therefore a hard floor on any matched-model estimate from this archive**, and
it is imposed by the data rather than chosen. §3.7 of the paper shows that even
2018Q3–2020Q1 is too fragile to publish in the headline series, so the published window
is **2020Q1–2026Q1**.

### 1.3 How the source was chosen

Fiverr was not assumed. Before any collection code was written, three pass/fail criteria
were set and tested on a 20-page probe drawn across categories and years.

| criterion | threshold, set in advance | result |
|---|---|---|
| Coverage | ≥10 snapshots spanning ≥3 years for ≥3 categories | writing and programming each returned 50+ snapshots spanning 2012–2025 |
| Extraction | ≥80% of probed pages yield a price | **20 of 20** yielded title, seller handle and ≥1 price tier, via the embedded `packageList` JSON |
| Longitudinal tracking | ≥5 sellers observable at ≥3 dates | 6 found, moving in both directions (architecture gig $50 → $20 over four years; web-development gig $5 → $25) |

Alternatives probed and rejected, each with a measured reason:

- **Upwork** — archival coverage moderate (2019–2024), and posted prices frequently absent
  from the archived page, because the platform's prices are negotiated per project.
- **Freelancer.com** — archival coverage sparse.

Probe artifacts: `runs/pilot-data-feasibility/`.

### 1.4 What that gate did not establish

The gate established that the source is **parseable and longitudinal**. It established
nothing about whether it is *dense enough to identify an index*, which is a separate
question, is answered in §3.6 and §3.7 of the paper, and is answered largely in the
negative. A feasibility criterion cleared at 20 pages is a weak instrument and is treated
as one throughout.

### 1.5 How the collection was scoped

A size estimate over the archive found roughly **2.5 million distinct Fiverr gig URLs and
4–20 TB of raw HTML** — beyond what could be retrieved or stored, and beyond what it would
be polite to request.

Rather than crawl opportunistically and stop when disk filled, the collection was split in
two: **download the index first**, which is cheap and complete, and **build the manifest
offline**; then download only the pages the manifest names. Every sampling decision below
is therefore made against a full census of what the archive holds rather than against
whatever a crawler reached first, and the sampling frame is a file that can be published
and re-sampled from by others.

**What the harvest then found, against that estimate** (measured 2026-08-12,
`runs/index-census/`). The index holds **1,778,505 distinct gig base URLs** carrying
**22,739,659** deduplicated status-200 captures, totalling **2.474 TB** of archived
compressed bytes — ≈12 TB raw at this corpus's measured 5.0× ratio. **The estimate was
1.4× high on URLs and correct on volume.** Both figures belong in the write-up: the
estimate is what forced the two-phase design, the measurement is what the archive turned
out to hold.

> **A 3.1× trap in that count.** CDX urlkeys retain query strings, so the file's
> **5,587,932** distinct urlkeys collapse to 1,778,505 distinct gigs (4.2M of 22.7M rows
> carry a tracking parameter). Stripping `?…` also breaks the file's sort order —
> `/a/b-c` sorts between `/a/b` and `/a/b?x` — so `uniq` over-counts and the distinct
> count needs a hash set.

### 1.6 Two crawls, not one

| crawl | selected for | window | rule |
|---|---|---|---|
| **Historical** | depth | 2011–2026 | 500-seller pilot; sellers qualifying on longitudinal depth |
| **Recent** | density | 2024Q3–2026Q1 | anchored at 2024Q3, capture required in the trailing window |

They are not a single sample and are not treated as one: they are estimated separately and
spliced (§3.4 of the paper). §4 below explains why the second crawl exists.

---

## 2. The pipeline

Each stage writes its output to disk, so the pipeline is resumable at any stage and every
intermediate count is recoverable from released artifacts. Parameters below are the ones a
replicator needs.

### Stage 1 — CDX index retrieval (`code/01-download-cdx-index.py`)

Query the Wayback CDX API once per first-letter prefix (`fiverr.com/a*` … `z*`), paginating
each prefix to exhaustion, at a **maximum of three concurrent queries** with exponential
backoff on failure. Six fields retained per record: `urlkey`, `timestamp`, `original`,
`statuscode`, `digest`, `length`.

**Out: 60 million raw index entries**, covering the full archival history.

### Stage 2 — Filtering, deduplication, classification (`code/02`–`05`)

- **URL shape.** A gig is addressed `fiverr.com/<seller>/<slug>`, so keep only URLs with
  exactly two path segments and status 200, excluding ~60 reserved first segments
  (`/categories`, `/search`, `/pro`, `/business`, `/blog`, …). *This is the pipeline's
  load-bearing assumption about what a gig is, and it is not airtight — see Stage 5b.*
- **Deduplication.** Collapse to one record per (URL, day); drop consecutive captures
  carrying an identical content digest. **Out: 22.7 million unique (URL, month).**
- **Classification.** Keyword-match each slug against `data/task-taxonomy.md`.
- **Longitudinal filter.** A seller qualifies if they hold at least one gig with **≥5
  monthly snapshots spanning ≥2 years**. **Out: 48,643 qualifying sellers.**

**Implementation note.** Deduplication and filtering run as an external `sort` followed by
a single streaming pass over the sorted file. The in-memory implementations written first
exhausted RAM at 22M records and were replaced.

### Stage 3 — Pilot sampling (`code/06c-pilot-longitudinal.py`, `code/07-pilot-500.py`)

**Sellers are sampled, not gigs.** This is deliberate and it costs coverage: drawing gigs
directly would spread the same download budget over more of the category space, but it
would break the within-seller panel that the reputation and upskilling analyses require.

From 48,643 qualifying sellers, draw **5,000 uniformly at random (fixed seed)**, then
subsample **500** by the same procedure — two stages for operational reasons, the
5,000-seller manifest having been built first. Extract every gig snapshot belonging to
them, downsampled to **one capture per gig per calendar month**.

**Out: 26,603 monthly snapshots across 14,938 unique gigs.**

> **Correction carried forward.** An earlier version of the paper described this as a
> *stratified* sample. It is not. Both draws are simple uniform random samples from the
> qualifying pool, seeded for reproducibility. A stratification by snapshot count was
> written for an earlier sampling design and did not survive into the production pipeline.

### Stage 4 — HTML download (`code/08-download-html.py`)

Request the **raw capture** rather than the rendered archive page:
`web.archive.org/web/<timestamp>id_/<url>`, where the `id_` suffix suppresses the Wayback
toolbar and returns the bytes as originally archived.

- Rate-limited with exponential backoff (**12 req/s** on the historical crawl; see §4 for
  what the recent crawl used and why it was wrong).
- Responses stored gzipped.
- **Successes are appended to a checkpoint file**, so an interrupted run resumes without
  re-requesting anything already held. **Transient failures (429s, timeouts) are
  deliberately not checkpointed**, so simply re-running the downloader retries exactly
  those and nothing else.

**Out: 22,632 of 26,603 (85.1%) historical; 15,150 of 15,309 (99.0%) recent.**

> **Correction carried forward.** The historical crawl's 15% shortfall was previously
> attributed to 404 attrition — pages indexed but no longer served. The download log does
> not support that: it records **102 hard failures and no 404s at all**. The bulk of the
> gap is manifest rows collapsing onto a gig-day file already retrieved, which is
> deduplication rather than loss. The 22,632 figure and everything downstream are
> unaffected; only the explanation was wrong.

### Stage 5 — Price extraction (`code/09-extract-prices.py`)

Fiverr's markup changed twice over the window, so the extractor is a cascade of four
methods ordered by reliability, each page falling through only when the one above finds
nothing:

| Method | Era | Mechanism | Share |
|---|---|---|---:|
| `packageList` JSON | 2020+ | Embedded JSON array, price in cents | 72.9% |
| Old-style JSON | Pre-2017 | JSON with price as string dollars | 15.2% |
| HTML `<span>` | 2018–2020 | `class="price"` DOM elements | 0.7% |
| Dollar fallback | All eras | `$X` pattern in page text | 11.2% |

Shares are historical-crawl figures. **Extraction succeeded on 100% of downloaded files**
(22,632/22,632 historical; 15,150/15,150 recent).

**The share table is not decoration.** It is the instrument that makes a parsing defect
visible — a success rate alone would not have surfaced Stage 5b.

### Stage 5b — Excluding non-gig pages

Several of Fiverr's own section pages satisfy the two-segment URL rule — `/hire/<category>`
(Pro category directories) and `/agencies/<name>` — where the leading segment is a reserved
site section rather than a seller handle. These carry no `packageList` blob, so extraction
fell through to the dollar fallback and recorded the page's **budget-filter default** as if
it were a price.

**The artifact is diagnostic:** 2,436 such rows sit at exactly **$500** and 330 at
**$1,000**. Fiverr changed that widget's default between 2024Q4 and 2025Q1, which imposed a
spurious **−50% step** on every affected category.

**The exclusion:** drop all observations whose leading path segment is a reserved section —
**3,846 of 37,782 observations (10.2%)**, falling entirely in the recent crawl (the
historical pilot contains none).

Two things about how the rule was chosen:

- **Audited for siblings first.** Two independent tests — reserved leading path segment,
  and a page title that is not gig-shaped — agree exactly and find **no third family**.
- **Keys on the URL family, not the extraction method.** The dollar fallback also recovers
  genuine prices from pre-2017 pages where no other method applies: **2,527 of 2,531**
  historical dollar-fallback rows are valid gig observations, clustered at $5 because that
  was Fiverr's original price floor. A rule keying on `dollar_fallback` would have destroyed
  them.

The single rule now lives in `code/gigfilter.py` (`is_gig` / `is_gig_id` over a 27-entry
`RESERVED` set) and is applied on **all seven** price-reading paths, including the crawl
manifest builder, so the URLs are never fetched again.

### Stage 6 — Deduplication to unique gigs

Collapse to unique (seller, slug) pairs with at least one valid price extraction.
**Out: 1,908 unique gigs across the 500 sellers.**

### Stage 7 — Service item clustering (`code/10-cluster-items.py`)

Cluster the 1,908 gigs into **150 service items** by TF-IDF vectorization of cleaned titles
with agglomerative clustering (cosine distance, average linkage). Examples: "logo design"
(73 gigs), "WordPress website" (62), "voice narration" (47).

**Silhouette at k=150 is 0.114 — low.** The clustering is therefore used **only for category
assignment and descriptive tables, never for the index**, which matches gigs to themselves.

### Stage 8 — Panel construction

Collapse multiple within-quarter snapshots to the **gig-quarter median**, apply a price
guard **0 < p ≤ $10,000**, and retain gigs observed in **at least two quarters**.

**Out: 1,066 historical panel gigs and 2,908 recent panel gigs.**

### The funnel, in one line

**Historical:** 60M raw CDX → 22.7M deduplicated → 48,643 qualifying sellers → 500 sampled
→ 26,603 manifest snapshots → 22,632 downloaded → 1,908 unique gigs with prices → **1,066
panel gigs**.

**Recent:** 15,309 manifest snapshots → 15,150 downloaded → (Stage 5b removes 3,846 rows)
→ **2,908 panel gigs**.

### Categories and weights

Gigs are classified into **seven** categories — writing, coding, design, translation, video,
audio, marketing — by keyword matching on descriptions and cluster labels for the historical
crawl, and from the crawl manifest for the recent crawl, using an identical map. Two
categories present in earlier drafts, **data entry and data analysis, are excluded**: both
are too thin to estimate (46 and 38 panel gigs) and data entry is explicitly dropped from
the recent crawl, so neither has a post-2024 segment.

Weights come from maximum observed review counts per category, normalized to sum to one —
analogous to CPI expenditure weights.

| Category | Recent panel gigs | Weight |
|---|---:|---:|
| Design | 1,466 | 0.706 |
| Writing | 368 | 0.111 |
| Marketing | 294 | 0.063 |
| Coding | 462 | 0.053 |
| Video | 235 | 0.046 |
| Audio | 55 | 0.019 |
| Translation | 28 | 0.003 |

**Design's 0.706 is the single most consequential feature of the composite.** The composite
is, to a first approximation, a design index with six minority components — which is why it
meets the precision standard when six of seven categories do not, and why it is robust to
estimator choices that move the categories substantially.

---

## 3. What the collection cost, and what settings it runs at

| setting | value | why |
|---|---|---|
| Concurrency / rate | **10 / 10 req/s** | 20/20 logged 45% transient failures at identical sustained throughput (§4) |
| Sustained throughput | **5.71 pages/s** | measured, and independent of the two settings above |
| Storage | **gzip, 5.0× measured** | 93 GB → 17.6 GB on the rule-B corpus |
| Page size | **37 KB (2018) → 268 KB (2026) gzipped** | ~7× growth; a flat average overstated one campaign's disk by 2.2× |
| Resumption | checkpoint on success only | a re-run retries exactly the failures |

Page size by year, gzipped, measured on the balanced pilot:

| year | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| avg KB | 37 | 39 | 61 | 94 | 131 | 172 | 244 | 248 | 268 |

**Never cost a crawl at a flat per-page average.** Weight by the manifest's own year
distribution. Doing so cut one campaign's disk estimate from 78 GB to 35.1 GB and reversed
the target decision that estimate had blocked.

---

## 4. How the collection changed

The pipeline above is the collection as it now stands, not as it was first built. It was
revised five times, and because **each revision was forced by something the data revealed
rather than chosen in advance**, the sequence is itself evidence about what archival price
collection costs.

| # | When | Change | What forced it |
|---|---|---|---|
| 1 | Mar 2026 | Sampling rule: sellers stratified by capture count → sellers qualifying on longitudinal depth, drawn uniformly | Stratifying on capture count selects on the archive's crawl intensity, not on panel usefulness |
| 2 | Jun 2026 | Second crawl added, anchored at 2024Q3 | The historical pilot goes sparse after 2024Q4 and cannot support a trailing index |
| 3 | Jul–Aug 2026 | Request rate reduced 20/s → 10/s | The 20/s run failed 45% of attempts; 10/s fails none at the same sustained throughput |
| 4 | Aug 2026 | Storage moved to gzip | Measured 5.0× on this corpus — the difference between 93 GB and 17.6 GB |
| 5 | Aug 2026 | Non-gig section pages excluded (Stage 5b) | A parsing defect that had put a false −50% step into every category |

Three deserve more than a table row.

### 4.1 The second crawl, and why the paper has a splice

The original design was one collection: 500 sellers, whole history. **It cannot measure the
recent period**, because sellers selected for long histories are precisely those whose
captures thin out at the trailing edge.

So the recent crawl was built on a different rule — anchor at 2024Q3, require a capture in
the trailing window — giving 15,309 snapshots over 3,589 gigs at far higher density than the
historical pilot achieves anywhere.

**Nearly every asymmetry in the paper's results traces to this**, including which categories
are identified at all: one crawl was selected for depth, the other for density, and they are
spliced rather than pooled.

### 4.2 The rate lesson, which cost nothing but was luck

The recent crawl ran at **20 concurrent requests at 20/second** and logged **12,336 transient
failures against 15,150 successes** — a **45% per-attempt failure rate**, absorbed only
because failures are un-checkpointed and a re-run retries them.

A later pilot at **10 concurrent and 10/second logged zero failures at the same sustained
throughput of 5.71 pages/second.** The faster setting bought nothing and merely converted
successes into retries.

Across both crawls' ~38,000 logged responses, exactly **3 were 403s**, so there is no
evidence of having been blocked. But the correct reading is that the crawl was running well
past the point of diminishing returns and this was not known until it was measured.

### 4.3 The exclusion that retracted a finding

Stage 5b is the only revision that changed a published result. An earlier version of the
paper reported the 2024Q4→2025Q1 step as a real 2025 reversal in the price of cognitive
labor. **It was a parsing artifact, it is retracted, and §4.6 of the paper reports the full
before-and-after rather than quietly restating the corrected numbers.**

The magnitude of the correction, for scale: the composite over 2020Q1→2026Q1 moved from
**+44.7% to +78.4% nominal** and **+14.1% to +40.7% real**; the recent segment inverted from
falling to flat-or-rising in six of seven categories; and bootstrap standard errors
*narrowed* in five of seven.

---

## 5. What the collection cannot fix

Three limits are properties of the archive. **No larger crawl reaches them**, and they are
reported rather than worked around.

### 5.1 Exit is unmeasurable

`code/39-status-ledger.py` streams all 60.0M raw CDX rows — the only place non-200 statuses
survive, since `code/02-filter-gig-pages.py` drops them — and tallies every status class for
the 25,051 rule-B gigs. Across **509,339 in-window captures: `n_404 = 0`**, with 1,155 403s,
1,588 3xx and 1,662 5xx.

**The archive stops re-requesting a delisted URL rather than recording its death**, so a
takedown and a lapse in crawling are indistinguishable. No volume of additional archive
collection produces an exit hazard; only **a live forward crawl on a fixed schedule** can.

> **Do not confuse this with download-time 404s.** The download logs *do* record 404s — 178
> on the expanded crawl, 11,501 on the balanced crawl. Those are **replay** failures from
> `web.archive.org/web/<ts>id_/<url>`: the Wayback endpoint could not serve that capture.
> The `n_404 = 0` figure is about the **origin** status recorded in the CDX index at capture
> time. They are different quantities and only the second bears on gig exit.

### 5.2 The trailing edge is closed

Status-200 captures fall from **280,779 in September 2024 to 66 in March 2026**. Direct
probes of the CDX for 2026Q2–Q3 return almost exclusively **403** on Fiverr gig URLs (prefix
`ba`, 2026Q2: 21 captures, **zero status-200**).

**Re-harvesting the index recovers nothing** — the data that exists is already on disk. This
retires the standing assumption that the index was stale because it was harvested in March.

### 5.3 The chain is severed before 2018Q3

See §1.2. A chain cannot pass through a 1-matched-gig link. 2018Q3 is archive-imposed, not a
budget choice.

### 5.4 One category cannot reach the precision standard at any budget

The paper's adequacy rule is **±5% at 95% on the category index at the terminal quarter**.
Requirements, from the finite-population-corrected precision curve: writing ≈900, design
≈1,100, video ≈1,600, **coding ≈7,400** matched gigs per pair.

**Coding's entire supply in the index peaks at 6,142.** Taking every coding gig the archive
holds still misses the standard. That is a result to publish, not a shortfall to work
around. Translation and audio are likewise archive-exhausted on most 2018–19 links —
translation tops out near 1,100, audio near 550.

---

## 6. The two enlarged collections — quarantined from this paper

**Every number in the current paper comes from the frozen table of the original two crawls.**
Both enlarged collections write to separate files and none of their output enters the
submission draft. They are paper 2's frame, per the 2026-08-05 decision.

### 6.1 What the census found

Censusing the *existing* index before crawling anything showed the binding constraint was
never the archive but the selection rule:

| window | gigs in index | gigs the shipped panel used | share |
|---|---:|---:|---:|
| Recent (2024Q3+) | 91,849 | 2,930 | **3.2%** |
| Full history | 786,717 (249,022 spanning ≥2 quarters) | 1,912 | **0.24%** |

The recent census was validated by reproducing the shipped panel exactly under the rule that
produced it (rule A → 2,930 post-`gigfilter`). **A census that cannot regenerate a known
answer is not evidence about the unknown ones.**

### 6.2 Expanded recent-window collection (rule B)

Drops the survivor filter: **≥2 distinct quarters anywhere in the window**, with no trailing
window requirement. Rules C (≥2 distinct months) and D (any capture) were rejected — C adds
gigs that cannot contribute a *quarterly* price relative, D adds singletons that cannot
contribute one at all.

| rule | criterion | gigs | snapshot-months |
|---|---|---:|---:|
| A (shipped) | ≥2 quarters AND ≥1 snapshot in 2025Q3–2026Q2 | 2,930 | 11,424 |
| **B (adopted)** | **≥2 quarters anywhere in window** | **25,051** | **79,191** |
| C | ≥2 distinct months | 34,458 | 100,596 |
| D | any capture | 91,849 | 157,987 |

**Status: download and extraction complete.**

- 79,191 manifest rows; **67,377 newly captured** (178 replay 404s, 27 hard failures, 6
  403s); the balance were already on disk from the original recent crawl and were not
  re-fetched.
- Extraction over the **combined** corpus: 82,967 files (67,377 new + 15,150 original + 440
  pilot) → **82,966 priced rows, 1 `no_price_found`**.
- Output: `data/pilot/expanded-prices.csv`. `recent-prices.csv` is untouched.

### 6.3 Balanced historical collection (2018Q3–2026Q1)

Quota-samples on **(category, adjacent quarter pair)** rather than on gigs, with greedy
selection weighted by pair rarity, so long-lived gigs in the oversupplied 2021–22 quarters do
not crowd out the short-lived gigs that are a thin pair's only support. **One page per
gig-quarter, not per gig-month** — the index is quarterly, so monthly captures cost 2× and
buy nothing it consumes.

Where supply is below target the manifest takes everything available and **records the
shortfall**. Thin pairs are published as thin (§3.7's not-identified marking), never silently
backfilled.

**Status: download and extraction complete.**

- Pre-crawl pilot: 1,946 pages stratified to **over-weight the oldest layouts** (equal per
  quarter, not proportional) → 1,936 rows, **10 `no_price_found` (99.5%)**, and it surfaced
  an `old_json` extraction path carrying 96 rows that no modern-corpus page uses.
- Full download: 298,009 manifest rows → **291,997 captured** (11,501 replay 404s, 507 403s,
  253 hard failures across three passes).
- Extraction: 293,943 files → **292,447 priced rows, 1,496 `no_price_found` (0.51%)**.
- Disk: **36 GB**, against the year-weighted estimate of 35.1 GB.
- Output: `data/pilot/balanced-prices.csv`. `pilot-prices.csv` is untouched.

### 6.4 Current inventory — everything on disk, measured 2026-08-10

| collection | rows | gigs | sellers | gig-quarters | span | pages | disk |
|---|---:|---:|---:|---|---:|---:|---|
| `pilot-prices.csv` (historical) | 22,632 | 1,912 | 500 | 7,977 | 2011Q3–2026Q1 | 22,632 | — |
| `recent-prices.csv` (shipped) | 15,150 | 2,930 | 2,577 | 8,343 | 2024Q3–2026Q1 | — | — |
| `expanded-prices.csv` (rule B) | 82,966 | 25,051 | 20,154 | 54,384 | 2024Q3–2026Q1 | 82,967 | 39 GB |
| `balanced-prices.csv` (historical) | 292,447 | 39,933 | 31,452 | 292,447 | 2018Q3–2026Q1 | 293,943 | 36 GB |

Gig and seller counts are post-`gigfilter`. `recent-prices.csv` is **25.4% non-gig rows**
before that filter — the Stage 5b families — against 4.6% in the rule-B re-selection and
**0.0%** in both historical collections, which is the exclusion behaving as documented.
`balanced-prices.csv` has exactly one row per gig-quarter by construction (§6.3).

**Matched gigs per adjacent quarter pair — the unit that binds.** Panel definition: post-
`gigfilter`, price guard 0 < p ≤ $10,000, gig observed in ≥2 quarters.

| collection | panel gigs | quarters | pairs | median/pair | min | pairs < `MIN_MATCH` |
|---|---:|---:|---:|---:|---:|---:|
| Historical pilot | 1,249 | 53 | 52 | 36 | **0** | 6 / 52 |
| Recent (shipped) | 2,908 | 7 | 6 | 425 | 214 | 0 / 6 |
| Expanded (rule B) | 25,014 | 7 | 6 | **578** | 362 | 0 / 6 |
| Balanced (historical) | 39,380 | 31 | 30 | **8,457** | 334 | 0 / 30 |

This reproduces the published recent panel exactly at **2,908** gigs, which is what
validates the measurement. The historical pilot's 1,249 is wider than the paper's 1,066
because this count applies no category restriction and no window floor.

Two readings:

- **The balanced collection moves the historical segment by more than two orders of
  magnitude** — median 36 → 8,457 matched gigs per pair, no pair below `MIN_MATCH`, and the
  severed 2017 links are gone because the window now starts at the 2018Q3 floor.
- **Both enlarged collections are thinnest at the trailing edge** (2025Q2→Q3: 362 and 334),
  which is the 403 wall of §5.2 arriving from the other side. That is the region no
  collection improves.

These are all-category figures. **The ±5% adequacy rule binds per category**, and coding's
requirement of ≈7,400 is not met by any of these medians once the panel is split seven ways
— §5.4.

### 6.5 What is deliberately not done

Rebuilding the index on either enlarged panel (steps 19 → 21 → 23 → 18), refreshing
`docs/data.json`, and re-freezing the paper numbers are **a separate, deliberate decision**,
gated on whether the enlarged panels move the index enough to justify it. Nothing rebuilds
automatically.

---

## 7. The caution about all of these counts

**Panel gigs are not the quantity that governs precision.** A matched-model index is
identified by the gigs shared between *pairs* of quarters, and the two diverge by orders of
magnitude in the historical panel — design has 330 panel gigs but a **median of 1 matched
gig per pair**, with 67% of pairs below `MIN_MATCH = 3`; writing has 229 gigs and a median
of **0**.

Wherever this project makes a claim about sample size, the unit is **matched gigs per
bilateral**, and §3.6 of the paper reports it in that form.

---

## 8. Artifacts

| artifact | path |
|---|---|
| Feasibility probe | `runs/pilot-data-feasibility/` |
| Census notes | `runs/collection-headroom/`, `runs/history-headroom/` |
| Per-stage scripts | `code/01`–`code/10`, `code/gigfilter.py` |
| Manifest builders | `code/13-recent-manifest.py`, `code/38-expanded-manifest.py`, `code/41-balanced-manifest.py` |
| Pilot samplers | `code/42-balanced-pilot.py` |
| Campaign drivers | `code/run-expanded-pipeline.sh`, `code/run-balanced-pipeline.sh` |
| Manifests | `data/pilot/*-manifest*.tsv` |
| Pages | `data/pilot/html-recent/`, `data/pilot/html-balanced/` |
| Download logs + checkpoints | `data/pilot/*-download-{log.tsv,checkpoint.txt}` |
| Prices + extraction errors | `data/pilot/*-{prices.csv,extract-errors.tsv}` |
| CDX status ledger | `code/39-status-ledger.py` → `data/pilot/gig-status-ledger.tsv` |
| Frozen paper figures | `data/pilot/paper-numbers.md` / `.json` |
| Campaign plans | `plans/active/expanded-collection.md`, `plans/active/balanced-history.md` |
| Templates | `plans/templates/data-collection.md`, `drafts/templates/data-collection-section.md` |
