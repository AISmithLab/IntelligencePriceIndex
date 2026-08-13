# Results from the Enlarged Collections

**Generated:** 2026-08-13
**Scripts:** `code/43-enlarged-results.py`, `code/44-entry-price-series.py`
**Data:** `data/pilot/enlarged-results.json`, `data/pilot/entry-price-series.json`

> **These are not paper figures.** The paper is governed by the frozen table
> `data/pilot/paper-numbers.md` and is built from the original two crawls only (§3.2).
> Everything here comes from the two enlarged collections, which are paper 2's frame.
> Nothing below has been written into any draft section.

Both `plans/active/expanded-collection.md` and `plans/active/balanced-history.md` stopped
at the same unstarted step — *"re-measure matched gigs per bilateral per category against
the ±5% requirement"*, and then decide whether to rebuild the index. This document answers
that question for both.

**How these were computed.** Panel construction, the GEKS-Jevons estimator and the
bootstrap are imported from `code/21-geks-index.py` (which imports `19-tpd-index.py`), so
nothing is reimplemented — only the input file and the category source differ. That is
deliberate: any difference from the paper's numbers must be the data, not the code.
Bootstrap is 200 replications resampling gigs with replacement, `MIN_MATCH = 3`, seed 7 —
the paper's conventions throughout.

**Validation that the harness is the paper's.** Run on the shipped historical panel, this
code returns coding **312.8 at ±61.1%** and translation **227.8** — the same figures §3.7
and §3.4 report. The estimator is behaving identically; only the panels below are new.

---

## 1. The headline: one collection worked, the other largely did not

The two enlarged collections were sized the same way — take the headroom the census found
and use it — but they sampled on different units, and the results diverge sharply.

| | Expanded recent (rule B) | Balanced historical (quota) |
|---|---|---|
| Sampled on | **gigs** (≥2 quarters anywhere in window) | **(category × adjacent quarter pair)** |
| Panel gigs | 2,908 → **25,014** (8.6×) | 1,066 → **39,380** (37×) |
| Matched gigs per bilateral | **1.2× to 2.0×** | **32× to 112×** |
| Terminal bands | essentially unmoved | **cut by 3× to 7×** |

**Adding gigs did not add precision; adding gigs *to the pairs that were thin* did.** This
is the clearest confirmation the project has produced of §3.6's claim that panel gigs are
the wrong unit. Rule B raised the recent panel 8.6-fold and moved design's median matched
gigs per quarter pair only from 208 to 300, because most of the gigs it adds are
short-lived and contribute to few bilaterals. The balanced crawl raised the historical
panel 37-fold and moved design's median from 25 to 1,056, because its quota was defined on
the bilateral itself.

If a full-frame collection is ever specified, this is the design lesson: **quota on
adjacent quarter pairs, not on gigs.**

---

## 2. Matched gigs per bilateral, against the ±5% requirement

The `need` column is §3.6's inverted precision fit. It was estimated on the recent panel,
so applying it to the historical window is indicative rather than exact.

### Recent window (2024Q3 base, terminal 2026Q1)

| Category | Need | Shipped | Expanded | Gain | Band before | Band after | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Design | 1,100 | 208 | 300 | 1.4× | ±4.8% | **±4.5%** | meets ±5%, as before |
| Writing | 900 | 48 | 66 | 1.4× | ±8.0% | ±6.9% | short by 13.6× |
| Marketing | — | 35 | 49 | 1.4× | ±9.0% | ±8.0% | — |
| Video | 1,600 | 32 | 50 | 1.6× | ±12.8% | ±12.6% | short by 32× |
| Coding | 7,400 | 58 | 74 | 1.3× | ±20.7% | ±21.8% | short by 100× |
| Translation | — | 3 | 6 | 2.0× | ±34.4% | ±22.1% | — |
| Audio | — | 5 | 6 | 1.2× | ±16.0% | ±14.1% | — |

Six of seven categories still miss ±5%, and **coding's band got slightly wider**, not
narrower. Rule B bought translation and audio a little (their thin-pair shares fall from
33.3% to 23.8% and 23.8% to 14.3%), and bought the dense categories almost nothing.

### Historical window (2020Q1 base, terminal 2026Q1)

| Category | Need | Shipped | Balanced | Gain | Band before | Band after | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Design | 1,100 | 25 | **1,056** | 42× | ±23.3% | **±6.8%** | at the requirement, band still misses |
| Writing | 900 | 20 | **820** | 42× | ±38.1% | ±10.9% | short by 1.1× |
| Video | 1,600 | 13 | 558 | 43× | ±75.8% | ±11.5% | short by 2.9× |
| Coding | 7,400 | 16 | 526 | 32× | **±61.1%** | **±13.1%** | short by 14× |
| Marketing | — | 6 | 258 | 43× | ±86.5% | ±15.4% | — |
| Audio | — | 8 | 405 | 51× | ±118.6% | ±31.5% | — |
| Translation | — | 2 | 224 | 112× | ±83.8% | ±38.2% | — |

This is a large, real gain: coding's historical band falls from ±61.1% to ±13.1%, video's
from ±75.8% to ±11.5%, audio's from ±118.6% to ±31.5%. **No category reaches ±5%**, but
the historical segment moves from uninterpretable to merely imprecise.

**A caution on design.** It reaches 1,056 matched gigs per pair — essentially §3.6's stated
requirement of 1,100 — and still bands at ±6.8%, not ±5%. The precision fit was estimated
on the recent panel over 7 quarters; the historical window spans 25, and a level further
from its base carries more accumulated variance. **The §3.6 requirement figures should be
treated as window-specific and re-derived before being used to size anything.**

---

## 3. Do the enlarged panels change the index?

Levels are nominal, each panel based at its own first quarter = 100. The composite uses the
**shipped weights** (design 0.706) so the comparison isolates the panel change; recomputing
weights on the enlarged panels is a separate decision and has not been made.

### Recent segment, 2024Q3 = 100

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
1.5 index points, well inside its own band, and the composite moves 0.8 points on a ±4.5%
band. Dropping the survivor filter — the design defect §6.3 calls impossible to retrofit —
**changes the recent price level essentially not at all.**

That is a substantive finding, not a null result to be buried: it says the recent segment's
level was not an artifact of conditioning on survival. It does **not** say survivorship is
harmless for the paper's headline, which is about incumbents versus entrants (§5 below).

### Historical segment

The balanced panel is a different frame from the 500-seller pilot, so this is not
before-and-after on the same object; it is two measurements of the same market.

**These must be compared at a common quarter.** The shipped historical categories terminate
at seven *different* quarters — translation at 2024Q3, marketing and audio at 2024Q4,
coding and writing at 2025Q1, video 2025Q3, design 2025Q4 — because each series ends where
its captures run out. Comparing each panel at its own terminal quarter would compare 2025Q1
with 2026Q1 and read the difference as a panel effect. The table below is therefore struck
at **2024Q3**, the last quarter every shipped category reaches, which is also the splice
point. Both panels are based at 2020Q1 = 100.

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

**The shipped panel overstated the thin categories and understated the dense ones.** The
four categories §3.6 identifies as thinnest — audio, translation, video, marketing, at 8, 2,
13 and 6 matched gigs per pair — all come down sharply on the denser panel, audio by 103
index points and video by 87. The three densest — design, writing, coding — go *up*. That
is exactly the signature §3.7 predicts: where a level rests on two to five link paths it is
a property of which path survived, and the error has no consistent sign.

Every shipped estimate still lies inside the balanced panel's terminal-quarter interval and
vice versa, so the frames do not contradict each other. But the point estimates move by
more than a third in four categories, which is a stronger warning against quoting the
shipped historical per-category levels than the paper currently gives.

For reference, each panel at its own terminal quarter, with bands:

| Category | Shipped (own terminal) | Balanced 2020Q1→2026Q1 | Balanced 2018Q3→2026Q1 |
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

## 4. The §3.7 window sensitivity, re-tested

§3.7's sharpest evidence was that growth over an **identical span** moved with the
estimation window — audio +103.9% from a 2018Q3 start against +258.7% from 2020Q1, a
spread of 76 points, because only 2–5 link paths supported the level. Re-running that test
on the balanced panel:

| Category | From 2018Q3 | From 2020Q1 | Spread |
|---|---:|---:|---:|
| Design | 193.5 | 174.2 | 19.3 |
| Writing | 228.4 | 211.7 | 16.7 |
| Coding | 286.4 | 229.1 | 57.3 |
| Marketing | 275.2 | 226.7 | 48.5 |
| Video | 219.5 | 174.5 | 45.0 |
| Audio | 216.8 | 219.6 | **2.8** |
| Translation | 127.0 | 175.8 | 48.8 |

**Audio, the paper's worst case, is fixed**: its 76-point spread collapses to 2.8 points
once the panel is dense. But coding, marketing, translation and video still move 45–57
points across the same two window choices, and those spreads are of the same order as their
bands. **The identification defect is reduced by density but not eliminated**, so §3.7's
central claim — that a band is the wrong object where link support is thin — survives the
enlarged collection and should not be softened in the paper.

---

## 5. Entry prices: the survivorship threat, measured inside one crawl

§6.2 calls the entry-price gap the paper's most serious unresolved threat and states the
condition for resolving it: *"the series must be built within a crawl or the frames
reconciled first."* The balanced collection is a single frame spanning 2018Q3–2026Q1, so
the series can now be built as §6.2 asks.

**A contamination check had to come first, and it changed the answer.** `review_count` is
only reliable where the `packageList` blob supplies it. On pre-2020 layouts the extractor
falls through to `dollar_fallback`/`old_json`, which report review counts erratically — so
a "≤10 reviews" filter there selects on *parse failure*, not on newness. Measured: the 2018
"new gig" cohort is only **16.0% packageList** and returns a median entry price of **\$395**
against \$10 for established gigs the same year. That is an artifact, not a price. Only
2020 onward, where packageList supplies ≥95% of the cohort, is interpretable.

Median entry price, gigs with ≤10 reviews at first capture, packageList only:

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

*(n in parentheses; cells with n < 10 suppressed.)*

**Entry prices are not flat on this frame.** Pooled across categories they double, \$10 to
\$20 between 2020 and 2024, against a balanced incumbent composite of 184.5 over roughly the
same span. Entry and incumbent prices move at a broadly similar rate, which is the opposite
of what §6.2's evidence suggested and would substantially weaken the survivorship threat.

**But the result is heterogeneous, and it splits exactly where it matters.** Coding entry
prices rise 8× (\$10 → \$80) while **design entry prices are flat (\$10 → \$10)** — and design
carries 70.6% of the composite weight. On this evidence the survivorship threat is
*discharged for coding and translation* and *intact for design*, which is the category that
determines the headline.

**Four reasons this must not yet be written into the paper.**

1. It is a median of a coarse price grid (\$5/\$10/\$15/\$20 dominate), not a matched index. A
   one-notch shift in the grid moves it a long way.
2. Cohort composition is uncontrolled — the 2020 cohort is a COVID-era mass-entry cohort and
   need not be comparable to 2024's.
3. First capture is truncated at both window edges: **11.8% of all first captures land in
   2018Q3**, the first quarter, and 2025 onward collapses to 0.2% at the 403 wall. Cohorts
   near either edge are not entry cohorts.
4. Cell counts fall sharply after 2022 (712 in 2023, 788 in 2024, 60 in 2025), and the
   per-category cells behind the strongest claims are small — coding's 2024 cohort is n=58.

The right next step is to rebuild this as a **matched entry-cohort index** on the same
estimator rather than as a median, and only then compare it with the incumbent series.

---

## 6. What this settles for the two blocked plans

**`plans/active/expanded-collection.md` — do not rebuild the index on rule B.** The recent
panel's precision barely improved (1.2–2.0× on the binding unit) and the index did not move
(composite +0.8 points on a ±4.5% band). The collection was still worth running: it is what
*demonstrates* that the survivor filter did not distort the recent level, and it supplies
the entry-price sample. But rebuilding 19 → 21 → 23 → 18 on it would change no published
figure.

**`plans/active/balanced-history.md` — this one justifies a rebuild.** Bands fall 3–7×
across every category, three categories currently marked *not identified* (coding,
translation, audio) become reportable with finite intervals, the historical composite moves
from 166.4 to 184.3 at a common 2024Q3, and four category levels move by more than a third.
A paper-2 index should be built on this panel.

**Both plans' remaining checkbox — "re-measure matched gigs per bilateral" — is now done**
and can be closed.

**One ceiling is confirmed unmovable.** Coding needs ≈7,400 matched gigs per pair for ±5%
and reaches 526 on the balanced panel and 74 on the expanded one. The census's own maximum
is 6,142. No collection from this archive reaches ±5% for coding.

---

## 7. Open questions this raises

- **The ±5% requirement figures are window-specific.** Design hits the stated 1,100 matched
  gigs and still bands at ±6.8% over 25 quarters. The precision fit must be re-derived per
  window before it is used to size a future collection.
- **Weights have not been recomputed** on the enlarged panels. Design's 0.706 comes from the
  shipped recent panel; the enlarged panels have a very different category mix (design is
  7,980 of 25,014 recent gigs but only 4,181 of 39,380 balanced gigs).
- **Real terms not computed here.** All levels above are nominal. CPI-U rises 26.8% over
  2020Q1–2026Q1 and would be applied unchanged, the deflator adding no sampling variance.
- **The entry-cohort index** described in §5 is the single highest-value analysis the new
  data supports, and it is not yet built.
