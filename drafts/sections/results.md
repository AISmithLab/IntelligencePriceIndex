# Results from the Two Enlarged Collections

**Generated:** 2026-08-13
**Scripts:** `code/43-enlarged-results.py`, `code/44-entry-price-series.py`
**Data:** `data/pilot/enlarged-results.json`, `data/pilot/entry-price-series.json`

> **These are not paper figures, and this file is not part of the paper.** It sits in
> `drafts/sections/` alongside the paper's sections but is deliberately **not** included by
> `drafts/main.md`, so it never enters a rendered draft, and it is outside the set
> `code/32-check-draft-numbers.py` governs. The paper is built from the original two crawls
> only (§3.2) and its figures are frozen in `data/pilot/paper-numbers.md`. Everything below
> comes from the two enlarged collections, which are **paper 2's** frame. Nothing here has
> been written into any draft section.
>
> If any of this is ever promoted into the paper, it must go through the frozen-table
> route — `code/30-freeze-numbers.py` — not by copying figures out of this file.

---

## 0. What this file is, in plain terms

### The question it answers

We collected two much larger batches of data than the paper uses. This file asks one
question about them: **did collecting more data actually make the price index more
accurate, and did it change the answer?**

The short version: **one batch worked, the other mostly did not** — and the reason why is
the single most useful thing this project has learned about how to collect these data.

### The words you need

The rest of this file uses eight terms in a specific way. They are defined here once.

| Term | What it means |
|---|---|
| **Gig** | One freelancer's fixed-price offer on Fiverr — "write a 1000-word blog post, \$25". |
| **Panel gigs** | How many distinct gigs we can use at all. A gig is usable only if we caught it at two or more different quarters, because one sighting tells you nothing about a price *change*. |
| **Quarter pair** (a "bilateral") | One direct comparison between two quarters — say 2024Q3 against 2024Q4. The index is built by stitching many of these together. |
| **Matched gigs per pair** | How many gigs appear in **both** quarters of such a comparison. **This is the number that determines accuracy**, and it is not the same as panel gigs: a collection of 25,000 gigs is useless for comparing two quarters if none of those gigs happens to appear in both. |
| **Band** | The margin of error on a reported price level, at 95% confidence. "±13%" means the true level could plausibly sit 13% above or below the number we print. Smaller is better. |
| **The ±5% requirement** | The accuracy standard §3.6 of the paper sets: a category is adequately measured only if its band is within ±5%. |
| **Index level / index points** | The price level, with a chosen starting quarter set to 100. A level of 184.3 means prices are 84.3% higher than in the starting quarter. "Moves 17.9 index points" means the two numbers differ by 17.9 on that scale. |
| **Not identified** | Worse than merely imprecise. It means the reported number depends on which comparison route happened to survive in the data, so putting a margin of error around it would mislead — the number is not pinned down at all. Three of the paper's historical categories are marked this way in §3.7. |

### The three data sets being compared

| Name | What it is | Period | Panel gigs |
|---|---|---|---:|
| **Shipped** | What the current paper uses | historical + recent | 1,066 / 2,908 |
| **Expanded** (also called "rule B") | A bigger re-collection of the recent period. It drops the paper's requirement that a gig still be visible at the end of the window — so it includes gigs that disappeared partway through | 2024Q3–2026Q1 | 25,014 |
| **Balanced** | A bigger re-collection of the history. Instead of sampling gigs, it fills a **quota for every combination of category and neighbouring quarter pair** — i.e. it deliberately goes looking for gigs that bridge each specific comparison | 2018Q3–2026Q1 | 39,380 |

### What we found, in four sentences

1. **Collecting more gigs did almost nothing; collecting gigs that bridge specific quarter comparisons did a great deal.** The expanded batch is 8.6× bigger and barely improved accuracy. The balanced batch is 37× bigger and cut the margins of error by 3–7×.
2. **The recent half of the paper's index is confirmed correct.** Re-measuring it on a much larger sample that includes the gigs it had excluded moves the headline by 0.8 index points, well inside its own margin of error.
3. **The historical half of the paper's index is confirmed shaky**, in the specific way §3.7 warned. Four of seven category levels move by more than a third on the better data, and they move in both directions.
4. **One category can never be measured well enough from this archive.** Coding needs roughly 7,400 matched gigs per comparison to hit ±5%; the entire archive can supply at most 6,142.

### How to read the rest

Sections 1–4 are about accuracy and whether the index moves. Section 5 is a separate
investigation into the paper's biggest known weakness. Sections 6–7 say what to do next.

---

## How these numbers were produced

Panel construction, the GEKS-Jevons estimator and the bootstrap are imported from
`code/21-geks-index.py` (which imports `19-tpd-index.py`), so nothing is reimplemented —
only the input file and the category source differ. That is deliberate: **any difference
from the paper's numbers must come from the data, not from the code.** Bootstrap is 200
replications resampling gigs with replacement, `MIN_MATCH = 3`, seed 7 — the paper's
conventions throughout.

**Proof that this is the paper's own machinery.** Run on the paper's shipped historical
data, this code returns coding **312.8 at ±61.1%** and translation **227.8** — exactly the
figures §3.7 and §3.4 report. The estimator behaves identically; only the data below is new.

**Why this file exists.** Both `plans/active/expanded-collection.md` and
`plans/active/balanced-history.md` stopped at the same unstarted step — *"re-measure matched
gigs per bilateral per category against the ±5% requirement"*, and then decide whether to
rebuild the index. This document answers that question for both.

---

## 1. The headline: one collection worked, the other largely did not

Both enlarged collections were sized the same way — find the spare capacity in the archive
and use it. But they chose **what to sample** differently, and that difference decided
everything.

| | Expanded recent (rule B) | Balanced historical (quota) |
|---|---|---|
| What it sampled | **gigs** (any gig seen in ≥2 quarters) | **each category × each neighbouring quarter pair** |
| Panel gigs | 2,908 → **25,014** (8.6× bigger) | 1,066 → **39,380** (37× bigger) |
| Matched gigs per pair | **1.2× to 2.0×** better | **32× to 112×** better |
| Margins of error | essentially unchanged | **cut by 3× to 7×** |

**Adding gigs did not add accuracy; adding gigs *to the comparisons that were thin* did.**
This is the clearest confirmation the project has produced of §3.6's claim that panel gigs
are the wrong unit to count.

Why the difference is so stark: the expanded collection raised the recent panel 8.6-fold but
moved design's typical matched gigs per quarter pair only from 208 to 300, because most of
the gigs it adds are short-lived and so bridge very few comparisons. The balanced collection
raised the historical panel 37-fold and moved design's typical figure from 25 to 1,056,
because its quota was defined on the comparison itself rather than on gigs.

If a full-scale collection is ever specified, **this is the design lesson: set quotas on
neighbouring quarter pairs, not on gigs.**

---

## 2. Accuracy, measured against the ±5% requirement

The `need` column is §3.6's accuracy formula run backwards — how many matched gigs per
comparison a category would need to reach ±5%. That formula was fitted on the recent data,
so applying it to the longer historical window is indicative rather than exact.

### Recent window (2024Q3 base, ending 2026Q1)

| Category | Need | Shipped | Expanded | Gain | Band before | Band after | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Design | 1,100 | 208 | 300 | 1.4× | ±4.8% | **±4.5%** | meets ±5%, as it did before |
| Writing | 900 | 48 | 66 | 1.4× | ±8.0% | ±6.9% | still 13.6× short |
| Marketing | — | 35 | 49 | 1.4× | ±9.0% | ±8.0% | — |
| Video | 1,600 | 32 | 50 | 1.6× | ±12.8% | ±12.6% | still 32× short |
| Coding | 7,400 | 58 | 74 | 1.3× | ±20.7% | ±21.8% | still 100× short |
| Translation | — | 3 | 6 | 2.0× | ±34.4% | ±22.1% | — |
| Audio | — | 5 | 6 | 1.2× | ±16.0% | ±14.1% | — |

Six of seven categories still miss ±5%, and **coding's margin of error actually got slightly
wider**. The expanded collection bought translation and audio a little — the share of their
comparisons resting on too few gigs falls from 33.3% to 23.8% and from 23.8% to 14.3% — and
bought the well-populated categories almost nothing.

### Historical window (2020Q1 base, ending 2026Q1)

| Category | Need | Shipped | Balanced | Gain | Band before | Band after | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Design | 1,100 | 25 | **1,056** | 42× | ±23.3% | **±6.8%** | reaches the target count, band still misses |
| Writing | 900 | 20 | **820** | 42× | ±38.1% | ±10.9% | 1.1× short |
| Video | 1,600 | 13 | 558 | 43× | ±75.8% | ±11.5% | 2.9× short |
| Coding | 7,400 | 16 | 526 | 32× | **±61.1%** | **±13.1%** | 14× short |
| Marketing | — | 6 | 258 | 43× | ±86.5% | ±15.4% | — |
| Audio | — | 8 | 405 | 51× | ±118.6% | ±31.5% | — |
| Translation | — | 2 | 224 | 112× | ±83.8% | ±38.2% | — |

This is a large, real gain: coding's historical margin of error falls from ±61.1% to ±13.1%,
video's from ±75.8% to ±11.5%, audio's from ±118.6% to ±31.5%. **No category reaches ±5%**,
but the historical half moves from uninterpretable to merely imprecise.

**A warning about design.** It reaches 1,056 matched gigs per comparison — essentially the
1,100 §3.6 says it needs — and still comes out at ±6.8% rather than ±5%. The reason is that
the accuracy formula was fitted on the recent data, which spans 7 quarters, while the
historical window spans 25; a level further from its starting quarter accumulates more
uncertainty along the way. **§3.6's "how many you need" figures are specific to the window
they were fitted on and must be re-derived before being used to size anything.**

---

## 3. Do the bigger samples change the index itself?

All levels here are nominal (not inflation-adjusted), each data set based at its own first
quarter = 100. The composite uses the **paper's existing category weights** (design 0.706)
so that the comparison isolates the effect of the data change; recomputing weights on the
enlarged samples is a separate decision and has not been made.

### Recent half, 2024Q3 = 100

| Category | Shipped | Expanded | Difference |
|---|---:|---:|---:|
| Design | 106.4 | 107.8 | +1.4 |
| Writing | 108.5 | 107.5 | −1.0 |
| Coding | 121.4 | 121.4 | **0.0** |
| Marketing | 109.9 | 109.2 | −0.7 |
| Video | 96.9 | 97.7 | +0.8 |
| Audio | 104.9 | 105.4 | +0.5 |
| Translation | 131.5 | 123.8 | −7.7 |
| **Composite** | **107.2** | **108.0** | **+0.8** |

**The recent index does not move.** Every category except translation shifts by less than
1.5 index points — comfortably inside its own margin of error — and the headline composite
moves 0.8 points against a ±4.5% band.

This matters because of *what* the expanded collection changed. The paper's recent sample
only includes gigs that were still visible at the end of the window, which risks measuring
the prices of survivors rather than of the market; §6.3 calls this impossible to retrofit.
The expanded collection removes that requirement, and **the price level barely responds.**

That is a real finding, not a null result to be buried: it says the recent level was **not**
an artifact of only looking at survivors. It does **not** say survivorship is harmless
generally — the paper's remaining survivorship worry is about long-established gigs versus
newly created ones, which is Section 5 below.

### Historical half

The balanced collection is a **different sample of the same market** — drawn on a quota
rule, not from the paper's 500-seller pilot — so this is not a before-and-after on the same
object. It is two independent measurements that ought to agree.

**They must be compared at a shared quarter, and this is easy to get wrong.** The paper's
historical categories each stop at a *different* quarter — translation at 2024Q3, marketing
and audio at 2024Q4, coding and writing at 2025Q1, video 2025Q3, design 2025Q4 — because
each series ends wherever its captures run out. Comparing each data set at its own final
quarter would put 2025Q1 next to 2026Q1 and read the resulting difference as a data effect.
The table below is therefore struck at **2024Q3**, the last quarter every paper category
reaches, which is also where the paper splices its two halves. Both are based at
2020Q1 = 100.

| Category | Shipped @2024Q3 | Balanced @2024Q3 | Difference |
|---|---:|---:|---:|
| Design | 146.7 | 175.7 | **+29.0** |
| Writing | 186.0 | 203.0 | +17.0 |
| Coding | 206.0 | 234.5 | +28.5 |
| Marketing | 267.7 | 210.8 | −56.9 |
| Video | 274.2 | 187.0 | **−87.2** |
| Audio | 307.4 | 204.0 | **−103.4** |
| Translation | 227.8 | 140.7 | −87.1 |
| **Composite** | **166.4** | **184.3** | **+17.9** |

**The paper's thin categories were overstated and its dense ones understated.** The four
categories §3.6 flags as thinnest — audio, translation, video and marketing, resting on 8,
2, 13 and 6 matched gigs per comparison — all come down sharply on the better data, audio by
103 index points and video by 87. The three best-populated — design, writing, coding — go
*up*. This is exactly the signature §3.7 predicts: where a level rests on only two to five
comparison routes, it reflects which route happened to survive, and the resulting error has
no consistent direction.

Every paper estimate still falls inside the balanced sample's margin of error and vice
versa, so the two do not formally contradict each other. But the central estimates move by
more than a third in four categories, **which is a stronger warning against quoting the
paper's historical per-category levels than the paper currently gives.**

For reference, each data set at its own final quarter, with margins of error:

| Category | Shipped (own final quarter) | Balanced 2020Q1→2026Q1 | Balanced 2018Q3→2026Q1 |
|---|---|---:|---:|
| Design | 156.6 ±23.3% (2025Q4) | 174.2 ±6.8% | 193.5 ±11.2% |
| Writing | 196.4 ±38.1% (2025Q1) | 211.7 ±10.9% | 228.4 ±17.3% |
| Coding | 312.8 ±61.1% (2025Q1) | 229.1 ±13.1% | 286.4 ±20.6% |
| Marketing | 282.2 ±86.5% (2024Q4) | 226.7 ±15.4% | 275.2 ±24.7% |
| Video | 244.2 ±75.8% (2025Q3) | 174.5 ±11.5% | 219.5 ±18.9% |
| Audio | 358.7 ±118.6% (2024Q4) | 219.6 ±31.5% | 216.8 ±37.3% |
| Translation | 227.8 ±83.8% (2024Q3) | 175.8 ±38.2% | 127.0 ±44.4% |
| **Composite** | **166.4 (2024Q3)** | **184.5 (2026Q1)** | **207.1 (2026Q1)** |

---

## 4. Re-testing the paper's most serious methodological finding

§3.7 reports a defect that a margin of error cannot express: **the measured growth over a
fixed span changes depending on where you start estimating**, which ought to be impossible.
Audio grew +103.9% over 2020Q1→terminal when estimation began in 2018Q3, but +258.7% over
that same span when it began in 2020Q1 — a 76-point spread, caused by only 2–5 comparison
routes supporting the level.

Re-running that test on the balanced data:

| Category | Starting 2018Q3 | Starting 2020Q1 | Spread |
|---|---:|---:|---:|
| Design | 193.5 | 174.2 | 19.3 |
| Writing | 228.4 | 211.7 | 16.7 |
| Coding | 286.4 | 229.1 | 57.3 |
| Marketing | 275.2 | 226.7 | 48.5 |
| Video | 219.5 | 174.5 | 45.0 |
| Audio | 216.8 | 219.6 | **2.8** |
| Translation | 127.0 | 175.8 | 48.8 |

**Audio, the paper's worst case, is fixed**: its 76-point spread collapses to 2.8 points once
the data is dense. But coding, marketing, translation and video still move 45–57 points
across the same two choices, and those spreads are as large as their own margins of error.

**More data reduces the defect but does not remove it.** §3.7's central claim — that a margin
of error is the wrong thing to report where comparison routes are few — survives the
enlarged collection and **should not be softened in the paper.**

---

## 5. Entry prices: measuring the paper's biggest unresolved threat

### What the threat is

The paper's index follows gigs that already exist and watches their prices rise. But an
established gig raises its own price as it accumulates reviews and reputation. So the index
might be measuring **the career of surviving freelancers rather than the price of the
service** — if brand-new gigs are still entering at the same price year after year while
established ones climb, the index is telling us about ageing, not about the market.

§6.2 calls this the paper's most serious unresolved limitation and states exactly what would
settle it: *"the series must be built within a crawl or the frames reconciled first"* — i.e.
the comparison has to be made inside a single data set, because the paper's two crawls
disagree about entry prices. The balanced collection is a single data set spanning
2018Q3–2026Q1, so the comparison can finally be made.

### A trap that had to be cleared first, and it changed the answer

Identifying a "new" gig requires its review count, and **review counts are only trustworthy
where the modern page format supplies them.** On pre-2020 page layouts the extractor falls
back to older, less reliable methods that report review counts erratically. So filtering for
"≤10 reviews" on old pages does not select new gigs — it selects **pages we failed to parse
properly.**

Measured: the 2018 "new gig" group is only **16.0%** modern-format pages, and returns a
median entry price of **\$395** against \$10 for established gigs in the same year. That is a
parsing artifact, not a price. **Only 2020 onward, where the modern format supplies ≥95% of
each cohort, is interpretable**, so the table below starts there.

### The result

Median entry price — gigs with ≤10 reviews at first sighting, modern-format pages only:

| Category | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|---:|
| Design | 10 (204) | 15 (151) | 18 (78) | 10 (25) | **10 (84)** | 15 (26) |
| Writing | 15 (235) | 20 (224) | 20 (119) | 20 (24) | 12 (28) | 15 (10) |
| Coding | 10 (413) | 20 (241) | 30 (183) | 45 (117) | **80 (58)** | 30 (11) |
| Marketing | 10 (943) | 20 (504) | 20 (311) | 20 (235) | 25 (261) | 25 (10) |
| Video | 15 (485) | 20 (320) | 20 (210) | 22 (78) | 20 (78) | — |
| Audio | 10 (751) | 15 (406) | 15 (235) | 10 (104) | 30 (160) | — |
| Translation | 5 (551) | 10 (640) | 10 (369) | 20 (129) | 20 (119) | — |
| **All** | **10** (3,582) | **15** (2,486) | **15** (1,505) | **20** (712) | **20** (788) | 20 (60) |

*(number of gigs in parentheses; cells with fewer than 10 gigs suppressed.)*

**Entry prices are not flat on this data.** Pooled across categories they double, \$10 to
\$20 between 2020 and 2024, against a balanced incumbent composite of 184.5 over roughly the
same span. New and established prices rise at a broadly similar rate — the opposite of what
the evidence behind §6.2 suggested, and enough to substantially weaken the threat.

**But the result splits exactly where it hurts most.** Coding entry prices rise 8×
(\$10 → \$80) while **design entry prices are flat (\$10 → \$10)** — and design carries 70.6%
of the composite's weight. On this evidence the survivorship threat is **discharged for
coding and translation** and **intact for design**, the one category that drives the
headline.

### Four reasons this must not go into the paper yet

1. It is a median over a coarse price grid (\$5/\$10/\$15/\$20 dominate), not a proper matched
   index. A one-notch shift in the grid moves it a long way.
2. The cohorts are not comparable to each other — 2020's is a COVID-era mass-entry cohort.
3. "First sighting" is distorted at both ends of the window: **11.8% of all first sightings
   land in 2018Q3**, the very first quarter, and 2025 onward collapses to 0.2% where the
   archive stops returning pages (the "403 wall" of §5.2). Cohorts near either edge are not
   really entry cohorts.
4. Counts fall sharply after 2022 (712 in 2023, 788 in 2024, 60 in 2025), and the cells
   behind the strongest claims are small — coding's 2024 cohort is only 58 gigs.

The right next step is to rebuild this as a **matched entry-cohort index** using the same
estimator as the main index, rather than as a median, and only then compare it against the
established-gig series.

---

## 6. What this settles for the two blocked plans

**`plans/active/expanded-collection.md` — do not rebuild the index on it.** Accuracy barely
improved (1.2–2.0× on the number that matters) and the index did not move (composite +0.8
points against a ±4.5% band). The collection was still worth running: it is what
*demonstrates* that excluding non-surviving gigs did not distort the recent level, and it
supplies the entry-price sample. But rebuilding the index pipeline on it — `code/19` → `21`
→ `23` → `18` — would change no published figure.

**`plans/active/balanced-history.md` — this one justifies a rebuild.** Margins of error fall
3–7× across every category; three categories currently marked *not identified* (coding,
translation, audio) become reportable with real intervals; the historical composite moves
from 166.4 to 184.3 at a shared 2024Q3; and four category levels move by more than a third.
A paper-2 index should be built on this data.

**Both plans' remaining checkbox — "re-measure matched gigs per bilateral" — is now done**
and can be closed.

**One ceiling is confirmed unmovable.** Coding needs roughly 7,400 matched gigs per
comparison to reach ±5%. It reaches 526 on the balanced data and 74 on the expanded data,
and the entire archive can supply at most 6,142. **No collection from this archive will ever
measure coding to ±5%.**

---

## 7. Open questions this raises

- **§3.6's "how many gigs you need" figures are window-specific.** Design hits the stated
  1,100 and still comes out at ±6.8% over 25 quarters. The formula must be re-fitted per
  window before it is used to size any future collection.
- **Category weights have not been recomputed** on the enlarged data. Design's 0.706 comes
  from the paper's recent sample, and the enlarged samples have a very different mix — design
  is 7,980 of 25,014 recent gigs but only 4,181 of 39,380 balanced gigs.
- **Nothing here is inflation-adjusted.** All levels above are nominal. CPI-U rises 26.8%
  over 2020Q1–2026Q1 and would apply unchanged, since the deflator adds no sampling error.
- **The entry-cohort index** described in Section 5 is the single highest-value analysis the
  new data supports, and it has not been built.
