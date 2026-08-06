# Plan: CSRankings-style IPI website

**Status:** dropped 2026-06-27 — frontend taken down (page wasn't working; user building their own site). Data layer (`code/15-build-site-data.py` → `site/data.json`) retained for the user's own frontend.
**Created:** 2026-06-26
**Goal:** A static, client-side website where users check/uncheck Fiverr categories and watch the Intelligence Price Index time series recompute live — analogous to csrankings.com.

## Scope
Covers: a static site (`site/`) + a data-generator (`code/15-build-site-data.py`) that turns the pipeline's recent index CSVs into a single `data.json`, plus deployment to GitHub Pages.
Does not cover: any backend/server, live scraping, or auth. All computation is client-side.

## Decisions (locked 2026-06-26)
- **Data source:** the *recent* trailing-12-month index, NOT the March pilot. User chose "wait for real data" — do not build the prototype on pilot data.
- **Display window: LAST 12 MONTHS ONLY (~2025Q1 → 2026Q1).** User: "I just need last 12 months, I don't need 2024 data." 2024 snapshots stay on disk as matched-model *anchor* data (so single-recent-snapshot gigs can still be paired) but must NOT appear in the published index, summary, or website. Scope the displayed series, not the download.
- **Stack:** Vanilla JS + **Plotly** (no build step, deploys to GitHub Pages as-is, rich interactive charts).
- **Client-side recompute:** ship per-category index series + per-category weights; composite over the checked subset = `exp( Σ wᶜ·ln(indexᶜ) / Σ wᶜ )` (mirrors step 14's `composite()`).

## Data contract (what the site consumes)
`site/data.json`:
```
{
  "categories": ["audio","coding","design","marketing","translation","video","writing"],
  "weights":   { "design": 0.41, "coding": 0.18, ... },   // from recent-category-weights.csv
  "quarters":  ["2024Q3","2024Q4","2025Q1", ...],
  "index":     { "design": [100, 104.2, ...], "coding": [...] },  // recent-category-indices.csv
  "composite": [100, ...],                                  // recent-ipi.csv (all-categories default)
  "monthly":   { "months": [...], "composite": [...] }      // recent-ipi-monthly.csv, if present
}
```

## Steps
- [x] Patch step 14 to emit `recent-category-weights.csv` (done 2026-06-26).
- [x] Fix pre-existing SyntaxError in step 14 (global decl before use) that would have crashed the pipeline (done 2026-06-26).
- [x] Wait for download → 09 → 14 to finish; confirm `recent-category-indices.csv`, `recent-category-weights.csv`, `recent-ipi.csv` exist and are sane (done 2026-06-27).
- [x] Write `code/15-build-site-data.py` — reuses step 14's machinery to emit the MONTHLY per-category index (which step 14 computes but never wrote), trailing 12 months only, re-based to window-start=100 → `site/data.json` (2.2 KB). (done 2026-06-27)
- [x] Build `site/index.html` + `site/ipi.js`: category checklist (per-category Δ12mo + weight + panel gigs), Plotly **monthly** line chart (thin line per checked category + bold composite), live recompute on toggle, trailing-12mo headline for the selection. (done 2026-06-27)
- [x] "Select all / none" + sensible default (all categories checked). (done 2026-06-27)
- [x] Sanity-check numbers: client recompute over all categories reproduces `composite_all` exactly; verified via offline replication. (done 2026-06-27)
- [ ] Deploy to GitHub Pages.

## Build decisions (2026-06-27)
- **Monthly, not quarterly** (user: "show the IPI per month"). Step 14 already runs a full monthly `build()` internally — step 15 imports it via `importlib`, so no re-download or pipeline change was needed.
- **Trailing 12 months only**: window = last 13 months *with a real composite* (`m["ipi"]` keys) = 2025-02 → 2026-02. No forward-filled phantom tail; 2024 stays on disk as anchor data only.
- **Re-based to window-start = 100** so the chart reads as a clean "past-year" index; re-basing is a pure rescale of matched-model relatives, so the composite formula is preserved and client recompute stays exact.
- **Known caveat shipped on the page**: thin categories (audio/marketing/video; translation drops out monthly) have sparse month-to-month matched pairs and read near-flat at monthly cadence. Design dominates basket weight (71%). Quarterly figures in `recent-ipi-summary.md` are more robust.

## Decision Log
- 2026-06-26: Stack = vanilla JS + Plotly; build on recent data only (user choices via AskUserQuestion).
- 2026-06-26: Scope output to LAST 12 MONTHS ONLY (user). Keep 2024 as anchor data on disk; filter it out of index/summary/site display. Do NOT restart the download to drop 2024 (already-pulled files are sunk; remaining queue is interleaved recent data; restarting is slower).
- 2026-06-26: Composite recomputed client-side from per-category indices + weights, so checkbox toggles need no server.

## Progress
- 2026-06-27: **Site built and validated.** `code/15-build-site-data.py` → `site/data.json` (2.2 KB, monthly, trailing 12mo, rebased). `site/index.html` + `site/ipi.js` (CSRankings-style: heaviest-weighted-first checklist, live composite recompute, Plotly monthly chart, select-all/none, headline that updates with the basket). Verified: JS syntax OK; client composite over all categories reproduces `composite_all` exactly; unchecking design (71% wt) moves the basket −2.1% → +0.8%. Composite all-categories trailing-12mo = −2.1% (2025-02→2026-02). Only deploy remains.
- 2026-06-26: Plan created. Step 14 patched to export weights and fixed to compile. Site build deferred until the recent index lands; watcher (bg task) will signal completion.
