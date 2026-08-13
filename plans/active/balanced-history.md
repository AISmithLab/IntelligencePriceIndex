# Plan: Balanced historical collection (2018Q3 onward)

**Status:** active
**Created:** 2026-08-09
**Goal:** Replace the 1,912-gig historical pilot with a panel whose precision is
roughly constant across quarters, by quota-sampling on bilateral links instead
of accepting whatever coverage the archive's crawl intensity happens to produce.

## Scope

**Covers:** censusing the full-history headroom in the existing CDX index,
designing a link-balanced manifest, validating extraction against pre-2020 page
layouts, and the collection itself.

**Does not cover:** rebuilding the index (19 → 21 → 23 → 18), `docs/data.json`,
or the submission draft. The pilot paper's numbers are frozen
(`data/pilot/paper-numbers.md`); this is **paper 2's** frame, same as the
expanded recent-window collection. See `plans/active/expanded-collection.md`.

## The finding that drove the design

The historical panel used **1,912 gigs / 22,632 rows**. The same CDX index
already holds **786,717 distinct gigs**, **249,022 of them spanning ≥2
quarters**, and **2,224,257 snapshot-months** — the pilot used **0.24%** of the
gigs available. As with the recent window, the binding constraint was the
selection rule, not the archive.

But unlike the recent window, there is a hard ceiling at both ends, and it is a
property of the archive that no collection can move.

### The chain is severed before 2018Q3

Matched gigs per adjacent quarter pair — the unit a chained matched-model index
actually consumes — measured over the whole index, not a sample:

| link | matched gigs | | link | matched gigs |
|---|---:|---|---|---:|
| 2015Q3→Q4 | 18 | | 2018Q1→Q2 | 4 |
| 2016Q3→Q4 | 2,277 | | 2018Q2→Q3 | 10 |
| 2017Q1→Q2 | **5** | | 2018Q3→Q4 | 8,084 |
| 2017Q3→Q4 | **1** | | 2019Q4→2020Q1 | 28,838 |

2017Q1 holds 5,451 snapshots and **5** matched gigs: Wayback re-crawled the site
but almost never the same gig twice across those boundaries. This confirms at
full-index scale what `plans/todo.md` recorded from a 1,066-gig sample on
2026-08-03 — **2018Q3 is a hard floor**, and it is not a sampling artifact.

The same collapse bounds the other end: 2024Q4→2025Q1 falls to 2,571 and
2026Q1→next is **0**, which is the 403 wall already documented in
`plans/active/expanded-collection.md`.

**So the achievable balanced window is 2018Q3 → 2026Q1, 31 quarters** — against
the paper's published 2020Q1 base.

## Design

Quota on **(category, adjacent quarter pair)**, not on gigs. Greedy selection
weighted by pair rarity, so long-lived gigs in the oversupplied 2021–22 quarters
do not crowd out short-lived gigs that are the only support a thin pair has.
Where supply is below target the manifest takes everything and records the
shortfall — those pairs stay thin and must be published as thin (§3.7's
not-identified marking).

**One page per gig-quarter, not per gig-month.** The index is quarterly; monthly
captures cost 2× and buy nothing it consumes. At target 1200 the monthly variant
is 583,506 pages / ~146 GB, which **does not fit** in the 96 GB free.

## Costs measured

Pre-pilot estimates, both of which the pilot corrected downward:

| option | gigs | pages | crawl (est.) | disk (est.) |
|---|---:|---:|---:|---:|
| target 600/pair | 17,377 | 168,033 | ~6.4 h | ~44 GB |
| target 1200/pair | 41,235 | 298,009 | ~11.4 h | ~78 GB |

**Both disk figures were wrong, and by enough to change the decision.** They
applied a flat ~275 KB/page, taken from the 2024Q3+ gzipped corpus. Fiverr gig
pages have grown by roughly 7× over the window, and the pilot measures it:

| year | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| avg gz KB | 37 | 39 | 61 | 94 | 131 | 172 | 244 | 248 | 268 |

Weighting those by the manifest's own year distribution gives **35.1 GB for
target 1200**, not 78 GB — against 95 GB free.

## Steps

- [x] Full-history census — `code/40-history-headroom.py` → `runs/history-headroom/`
- [x] Link-balanced manifest builder — `code/41-balanced-manifest.py`
- [x] Stratified pilot sampler — `code/42-balanced-pilot.py` (equal per quarter,
      not proportional — a proportional draw would put almost nothing in the
      2018–19 quarters this pilot exists to test)
- [x] **Pilot 2,000 pages and validate extraction against pre-2020 layouts** —
      1,946 pages, 1,936 rows, **10 `no_price_found` (99.5%)**; a new `old_json`
      path carries 96 rows that no modern-corpus page uses
- [x] Decide target (600 vs 1200) — **1200**, on the corrected disk figure
- [x] **Full download** — **DONE 2026-08-10.** 298,009 manifest rows → **291,997 captured**
      across three passes (11,501 replay 404s, 507 403s, 253 hard failures). Disk **36 GB**,
      against the year-weighted estimate of 35.1 GB.
- [x] Re-extract over the combined corpus → `balanced-prices.csv` — **DONE 2026-08-10.**
      293,943 files → **292,447 rows, 1,496 `no_price_found` (0.51%)**, no other error class.
- [x] Re-measure matched gigs per bilateral per category against the ±5% requirement —
      **DONE 2026-08-13**, `code/43-enlarged-results.py` → `drafts/sections/results.md` §2. Matched gigs per
      bilateral rise **32× to 112×** (design 25 → 1,056, translation 2 → 224), and terminal
      bands fall 3–7×: coding **±61.1% → ±13.1%**, video ±75.8% → ±11.5%, audio ±118.6% →
      ±31.5%. **No category reaches ±5%**, but the historical segment moves from
      uninterpretable to merely imprecise.
- [x] Decide whether to rebuild 19 → 21 → 23 → 18 on the enlarged panel — **YES, decided
      2026-08-13.** See the Decision Log entry below.

## Decision Log

- **2026-08-13: rebuild paper 2's index on this panel.** Bands fall 3–7× in every category;
  the three series §3.7 marks **not identified** (coding, translation, audio) become
  reportable with finite intervals; and the point estimates move enough to matter. Compared
  at a common 2024Q3 — necessary because the shipped categories terminate at seven different
  quarters — the composite goes 166.4 → 184.3, and the pattern is the one §3.7 predicts:
  **the thinnest categories came down hardest** (audio −103.4 index points, video −87.2,
  translation −87.1, marketing −56.9) while the densest went *up* (design +29.0, coding
  +28.5). Two findings to carry forward: §3.7's window defect is **reduced but not
  eliminated** — audio's 76-point spread collapses to 2.8, but coding, translation,
  marketing and video still move 45–57 points between a 2018Q3 and a 2020Q1 start — and
  §3.6's matched-gig requirements are **window-specific**, since design reaches the stated
  1,100 and still bands at ±6.8% over 25 quarters.
- **2026-08-09: floor at 2018Q3, and treat it as archive-imposed.** Not a budget
  choice. A chain cannot pass through a 1-matched-gig link.
- **2026-08-09: quota per gig-quarter, not gig-month.** 2× cheaper and matches
  what the index consumes. Makes the difference between fitting on disk and not.
- **2026-08-09: pilot before committing.** The download and extraction path has
  only ever been validated on 2024Q3+ pages. The historical corpus is where
  `dollar_fallback` clusters at the old $5 floor and where the 10-point rating
  scale appears (`plans/todo.md`), so `packageList` coverage on 2018–2019 pages
  is genuinely unknown and would invalidate the crawl after the fact.
- **2026-08-09: target 1200, not 600.** The pilot cleared extraction (99.5% on a
  sample stratified to *over*-weight the oldest layouts), and the disk estimate
  that made 1200 look marginal was measured wrong — 35 GB, not 78. With the
  binding constraint gone, 1200 is chosen because the thin pairs are where the
  panel is unidentified (§6.4) and 600 leaves most of them thin. Note this does
  **not** double coverage everywhere: 2018Q3–2019Q2 and translation/audio are
  archive-exhausted at either target, so 1200 buys density in the middle years
  and nothing at the ends.
- **2026-08-09: separate output file, `balanced-prices.csv`.** `pilot-prices.csv`
  is the historical panel behind the frozen paper numbers and is not touched.

## Known ceilings to report, not fix

- **Coding cannot reach ±5% at any target.** Its requirement is ≈7,400 matched
  gigs per pair; supply peaks at **6,142**. Taking every coding gig in the index
  still misses it.
- **Translation and audio are archive-exhausted on most pairs** even at target
  1200 — translation tops out near 1,100, audio near 550 on the 2018–19 links.

## Progress

- **2026-08-09:** census, manifest builder and pilot sampler built; costs
  measured; 2,000-page stratified pilot downloading.
