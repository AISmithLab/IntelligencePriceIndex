# Plan: recover what 2025-2026 Fiverr data still exists

**Status:** active
**Created:** 2026-09-06
**Goal:** lift the panel's starved 2025Q1-2026Q3 right edge as far as the archive allows, and establish what the ceiling actually is.

## The problem, stated in the project's own numbers

`runs/uncollected-headroom/supply-delta.md` — matched gigs per adjacent quarter pair:

| pair | design | coding | writing |
|---|---:|---:|---:|
| 2024Q3->2024Q4 | 7,093 | 5,276 | 5,083 |
| 2024Q4->2025Q1 | 1,122 | 644 | 435 |
| 2025Q1->2025Q2 | 329 | 165 | 98 |
| 2025Q4->2026Q1 | 320 | 63 | 55 |

Every 2025-2026 pair is below every target any balanced manifest has used.

## Diagnosis (2026-09-06)

Not a collection failure — the archive itself. Of fiverr.com captures timestamped
2025+, **38% are HTTP 403** and only **19% are 200**. The PerimeterX wall that
`80-fiverr-sitemap-census.py` measured against live gig pages in 2026-09 was already
turning the Wayback crawler away through 2025. Gig snapshots/month collapse from
~250k (2024Q3) to ~1-5k (2025+).

Three pools are nevertheless recoverable:

1. **Late ingestion.** Wayback keeps absorbing captures after the fact. Re-querying
   prefix `q` on 2026-09-06 returns 252 gig-shaped 200-status captures in 2025+ against
   the 212 the 2026-03-22 pull saw — **+19%**, invisible from inside the March files.
2. **The right edge.** The March pull stops at 2026-03 (13 records that month, none
   after). 2026Q2 and 2026Q3 are absent, not thin.
3. **Never-requested captures.** The balanced and expanded manifests quota over seven
   domains and drop `uncategorized`, so indexed 2025+ captures outside that set were
   never downloaded.

## Scope

Covers: refreshing the CDX index over 2025-01-01 -> now, sizing the three pools,
downloading and price-extracting what they hold, and re-running the supply projection.

Does **not** cover: live Fiverr collection (hard-blocked, refused — see step 80), any
splicing of Mercor rates into the IPI (different price object, see step 79), or a
decision about whether the thinned right edge should be reported or truncated. That
last one is a paper question and belongs to whoever writes §4.

## Steps

- [x] Parameterize `01-download-cdx-index.py` with `--from` / `--to` / `--out` / `--prefixes`
- [x] Pilot the late-ingestion gain on one prefix before committing to a full pull
- [~] Run the refresh: `--from 20250101` into `data/cdx-index/raw-2025/` (running; slower than estimated — prefix `a` alone is 914 CDX pages, so 5-8h not 2-3h)
- [x] Write `81-cdx-refresh-delta.py` — separates the three pools, emits a step-08 manifest
- [ ] Run step 81 against the completed refresh
- [~] `08-download-html.py --manifest data/pilot/refresh-2025-manifest.tsv --gzip` (running in parallel with the refresh at 6/6; ~300 captures/min, ETA ~2h, 99.6% HTTP 200)
- [ ] `09-extract-prices.py` over the new HTML
- [ ] Re-run the supply projection and update `supply-delta.md` with the new right edge
- [ ] Decide whether the recovered supply changes the index window, or only its error bars

## Decision Log

- 2026-09-06: **Pilot one prefix before the full pull.** `q` is the second-smallest
  prefix and cost one request. It returned +19% and 36 records in the 2026Q2-Q3 gap,
  which is what justified the 2-3h job. Had it returned ~0, the honest answer would
  have been "the archive is exhausted, and here is the evidence."
- 2026-09-06: **Refresh into `raw-2025/`, not into `raw/`.** The March pull is the
  provenance record for every number already in the draft; overwriting it would make
  those numbers unreproducible. The two directories are unioned at read time by step 81.
- 2026-09-06: **403 captures are dropped, not counted as supply.** A 403 capture exists
  and has a digest and a length, so a naive census counts it. Its body is a CAPTCHA page
  and carries no price. Counting them would inflate 2025-2026 supply by ~2x on paper
  while yielding nothing.
- 2026-09-06: ~~**Do not run downloads concurrently with the CDX pull.**~~ **Reversed
  the same day** on the user's instruction, and the reversal was right: 35,030 of the
  ~35k manifest captures come from the *March* pull and do not depend on the refresh at
  all, so serialising bought nothing and cost hours. The download runs alongside at
  `--concurrency 6 --max-rate 6` instead of 10/10, which leaves headroom for the CDX
  pull. Observed: 300 captures/min, 471/473 HTTP 200, no 429s on either job.
- 2026-09-06: **Step 81 writes the manifest atomically** (temp + rename). Step 08 loads
  its manifest once at startup, so a rename swaps safely under a live pass; a plain
  `open(..., "w")` would have let pass 1 read a half-written file.
- 2026-09-06: **One writer per checkpoint.** The driver waits for the in-flight
  download to exit before starting pass 2 — two step-08 processes appending to one
  checkpoint would interleave lines and corrupt the resume set.

## Progress

- 2026-09-06: Diagnosis complete, downloader parameterized, refresh launched, step 81
  written and smoke-tested.
- 2026-09-06: Verified the premise end-to-end before committing to the download —
  fetched three manifest captures and parsed them. 2025-01 and **2026-07** captures are
  real gig pages with real `packageList` prices and no `px-captcha` wall; one 2025-12
  capture returned 200 with no price block, so **35,030 is an upper bound on extraction
  yield, not a forecast**. The 2026-07 capture is past the right edge of everything
  currently in the index.
- 2026-09-06: Download pass 1 started alongside the refresh. Three jobs live: CDX pull,
  step 08, and the driver waiting to sequence 81 -> passes 2-3 -> 09.
