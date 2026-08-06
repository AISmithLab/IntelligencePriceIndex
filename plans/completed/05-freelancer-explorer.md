# Plan: Freelancer Explorer (per-seller gig price histories on the site)

**Status:** completed
**Created:** 2026-07-06
**Goal:** Widen the site's freelancer rankings (12→25/category) and make each freelancer expandable to show the gigs they sell with a per-gig price-over-time chart (all 3 tiers).

## Scope
Covers: data build (per-seller → per-gig price series from the price CSVs), a
lazily-loaded `docs/freelancers.json`, and the nested dropdown UI in `ipi.js`.
Also fixes broken freelancer links by adding a Wayback archived-page URL per gig.
Does NOT cover: growing the priced panel itself (still the 500-seller + recent
crawl); the full 822K-seller CDX pool has no downloaded prices, so only sellers
present in the price CSVs can be shown with history.

## Decisions
- Top 25 freelancers/category (user pick), ranked by distinct priced gigs.
- Each gig chart plots Basic/Standard/Premium as 3 lines (user pick).
- Price series compressed to change-points (dedupe consecutive equal tiers) →
  ~332 KB for 152 sellers / 813 gigs. Delivered as a separate `freelancers.json`
  fetched once on first rankings expand, so initial page load stays light.
- Gig links point to the archived snapshot
  `https://web.archive.org/web/{lastdate}/https://www.fiverr.com/{seller}/{slug}`
  (guaranteed to resolve) rather than the live profile (link rot).

## Steps
- [x] Pilot data build + payload estimate (1 cat → all cats). 332 KB.
- [x] Extend `code/18-build-site-data-long.py`: TOP_N=25, build price series from
      both price CSVs, emit `docs/freelancers.json`; keep `rankings` summary in
      `data.json` consistent with it.
- [x] Re-render `docs/data.json` + `docs/freelancers.json`; sanity-check counts.
- [x] UI: nested freelancer dropdown in `ipi.js` (lazy-fetch freelancers.json,
      render per-gig 3-tier price charts), styles in `index.html`.
- [x] Verify in-browser (Playwright Chromium; screenshot runs/freelancer-explorer.png) (dark + light), then update progress.md + tests.

## Decision Log
- 2026-07-06: Show-with-history limited to priced sellers (not the 822K CDX pool)
  because price-over-time requires downloaded+extracted prices.

## Progress
- 2026-07-06: Piloted the build across all 7 categories; validated series shape
  and 332 KB compressed payload. Proceeding to real implementation.
