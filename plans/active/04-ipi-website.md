# Plan: CSRankings-style IPI website

**Status:** blocked (waiting on recent trailing-12-month index, step 14)
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
- [ ] Wait for download → 09 → 14 to finish; confirm `recent-category-indices.csv`, `recent-category-weights.csv`, `recent-ipi.csv` exist and are sane.
- [ ] Write `code/15-build-site-data.py` — CSVs → `site/data.json`.
- [ ] Build `site/index.html` + `site/ipi.js`: category checklist (with per-category Δ12mo), Plotly line chart (one line per checked category + bold composite), live recompute on toggle, trailing-12mo headline for the selection.
- [ ] "Select all / none" + sensible default (all categories checked).
- [ ] Sanity-check numbers match `recent-ipi-summary.md`.
- [ ] Deploy to GitHub Pages.

## Decision Log
- 2026-06-26: Stack = vanilla JS + Plotly; build on recent data only (user choices via AskUserQuestion).
- 2026-06-26: Scope output to LAST 12 MONTHS ONLY (user). Keep 2024 as anchor data on disk; filter it out of index/summary/site display. Do NOT restart the download to drop 2024 (already-pulled files are sunk; remaining queue is interleaved recent data; restarting is slower).
- 2026-06-26: Composite recomputed client-side from per-category indices + weights, so checkbox toggles need no server.

## Progress
- 2026-06-26: Plan created. Step 14 patched to export weights and fixed to compile. Site build deferred until the recent index lands; watcher (bg task) will signal completion.
