# To-Do

## Active

- [ ] **Decide how the chained-Jevons comparison series should be built, then fix `code/12-panel-ipi.py`** (see `plans/tech-debt-tracker.md` TD1). The script credits a gig's whole multi-quarter price change to the single quarter it reappears, inflating the historical segment on top of genuine chain drift (design 2020Q1→2024Q3: 326 as-built vs 229 adjacent-only vs 154 direct-matched vs 147 GEKS). Removed from the site on 2026-07-27, so this is now a **paper** issue: §3.4 quantifies chain drift as chained +217.7% vs GEKS +44.6%, but part of that gap is the defect, not drift. Three candidate constructions with different coverage/comparability costs — pick one, re-run 12 → 18, refresh §3.4 and the elasticity/structural-break tables.
- [ ] **Refresh paper numbers after the 2026-07-07 chaining-bug fix** — `code/12-panel-ipi.py` now chains gap-tolerantly, so `panel-ipi.csv`/`panel-elasticity.csv`/`panel-summary.md` changed: peak composite **311.6→325.8 (2024Q4)**, elasticity table now **8 categories (was 5)** (added translation, data_entry, data_analysis). Draft sections still cite the old figures (312 peak, 5 categories). Update abstract/findings/methods + relevant `tests/*.test.md`, or decide to restrict the paper's elasticity table to the original 5 basket categories.
- [ ] **IPI website (deploy)** — Self-contained CSRankings-style frontend (`site/index.html`, `site/ipi.js`, inline-SVG charts, no external libs), committed on `mockup`. Data layer: `code/15-build-site-data.py` → `site/data.json`. **2026-06-30: repo made public; chose GitHub Actions deploy from `mockup`.** Added `.github/workflows/pages.yml` (uploads `site/`, deploys on push). **Blocked on one manual step:** user must set Settings → Pages → Build and deployment → Source = "GitHub Actions" (one-time). Then the workflow auto-publishes to https://aismithlab.github.io/IntelligencePriceIndex/.
- [ ] **Validation & robustness checks** — compare IPI to GPTs-are-GPTs exposure scores, Anthropic index, BLS wage data. Sensitivity analysis with alternative benchmark choices.
- [ ] **Forward-looking forecasts** — project IPI under AI scaling scenarios (smooth scaling, punctuated improvement, plateau).
- [ ] **Worker-level analysis** — same worker over time: upskilling vs. price reduction. Panel within-seller regressions.
- [ ] **Generate figures** — IPI time series plot, category panels with AI overlay, elasticity forest plot. Replace `<!-- FIGURE -->` placeholders.
- [ ] **Full-scale data collection** — expand from 500-seller pilot to full sample (48,643 qualifying sellers or stratified subsample). Current results are pilot-scale.

## Backlog

- [ ] Heterogeneity analysis: routine vs. judgment-intensive tasks (formal prediction-judgment decomposition)
- [ ] Quality-adjusted IPI variant using rating data
- [ ] New task category analysis: AI-created gig categories (prompt engineering, AI humanization)
- [ ] Render paper HTML with `drafts/render.py`

## Done

- [x] **Data feasibility pilot** → `plans/completed/01-data-feasibility-pilot.md`
- [x] **Scoping & taxonomy** → `plans/completed/02-scoping-and-taxonomy.md`
- [x] **Fiverr archive download (Phase 1: CDX index)** — 60M raw → 22.7M deduped → classified → filtered. Complete.
- [x] **Fiverr archive download (Phase 2: HTML download)** — 22,632/26,603 snapshots downloaded (85.1%). Complete.
- [x] **Fiverr archive download (Phase 3: extraction)** — 22,632/22,632 prices extracted (100%). `data/pilot/pilot-prices.csv`.
- [x] **Collect AI benchmark score histories** — `data/ai-benchmarks.csv` with 8 benchmarks spanning 2017–2025.
- [x] **Build linked panel dataset** — `code/12-panel-ipi.py`, panel of 1,245 gigs × 21,461 observations.
- [x] **Estimate price elasticity of intelligence** — 5 categories estimated, all significant p<0.01. Audio β=−0.49, Design β=+1.10.
- [x] **Trailing-12-month IPI (past-year data retrieval)** — DONE 2026-06-27. 15,150/15,309 snapshots downloaded (99%), 100% price extraction, matched-model index across 7 categories. Composite −0.3% over 2025Q1→2026Q1. Outputs: `data/pilot/recent-ipi*.csv`, `recent-category-*.csv`, `recent-ipi-summary.md`.
- [x] **Construct the IPI** — Matched-model Jevons/Törnqvist index. IPI peaked 312 (Q4 2024), declined to 246 (Q2 2025).
- [x] **Draft all paper sections** — abstract, introduction, related work, methods, findings, discussion, limitations, conclusion.
- [x] **Self-review and polish** — Fixed number inconsistencies, section numbering, redundancy, missing cross-references.

## Dropped

- ~~Consider supplementary platforms (Upwork, Freelancer, 99designs)~~ — dropped 2026-03-21: pilot confirmed Fiverr has sufficient coverage; no pivot needed.
- ~~Build Fiverr scraping pipeline (page-by-page)~~ — dropped 2026-03-21: replaced by bulk Wayback Machine archive download approach.

## Change Log

- 2026-07-27: User flagged design's index tripling as implausible. Diagnosed: the site's headline chart was still the naive chained-Jevons series (`DATA.index`, design 100→304) while the drift-free GEKS-Jevons series below it read 134; direct matched-pair comparisons corroborate GEKS in every category. Collapsed the two charts into one GEKS-only chart and moved the Δ column, sparklines and inspector onto `index_geks`/`delta_geks`. Also found and characterised TD1 (gap double-counting in step 12); attempted fix reverted as a methods decision — new to-do added.
- 2026-07-07: Fixed a forward-chaining bug in step 12 that silently dropped translation's entire historical series (gap in 2019Q2–Q4 broke the chain). Fix is gap-tolerant + purely additive; translation now spans 2020Q1–2026Q1 on the site. Added a graph quarter-inspector (dropdown + click-to-pin → QoQ/YoY/vs-base readout). Added a to-do to refresh paper numbers (peak 311.6→325.8, elasticity 5→8 categories).
- 2026-06-30: Rebuilt frontend committed on `mockup` (previously untracked). Now fully self-contained — inline-SVG charts, no Plotly/CDN. Validated (JS syntax, data contract, composite recompute = −2.1% headline). Website item narrowed to "deploy" (hosting is the only open step). Branch also carries `scripts/make_mock_ipi.py` (20-category synthetic mockup, separate exploration).
- 2026-06-27: Website taken down (page wasn't working; user building own). Deleted `gh-pages` branch + frontend (`site/index.html`, `site/ipi.js`, `scripts/deploy-site.sh`). Kept `code/15-build-site-data.py` + `site/data.json` as the data layer for the user's own site.
- 2026-06-27: CSRankings-style website built (`site/`, monthly + live recompute, validated). Only GitHub Pages deploy remains. Added `code/15-build-site-data.py`.
- 2026-06-27: Trailing-12-month IPI retrieval+build complete (moved to Done). Website item unblocked. Fixed a path bug in `code/09-extract-prices.py` that had silently produced an empty prices CSV.
- 2026-06-26: Added CSRankings-style IPI website item (plan 04, blocked on recent index; vanilla JS + Plotly, build on recent data). Fixed crash-bug in step 14 and added weights export.
- 2026-03-23: Massive progress — extraction, clustering, IPI construction, full paper draft, and self-review all completed. Moved 8 items to Done. Active items now focus on validation, forecasting, figures, and scale-up.
- 2026-03-22: Expanded plan 03 into 3 phases. Size estimation done; Phase 1 active.
- 2026-03-21: Both plans completed in parallel. Pilot: GO. Scoping: taxonomy + related work drafted.
- 2026-03-21: Consolidated into 2 concrete plans. Added draft-section items to backlog.
- 2026-03-21: Initial to-do list created from paper plan.
