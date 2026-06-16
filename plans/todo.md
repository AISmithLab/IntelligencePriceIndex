# To-Do

## Active

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
- [x] **Construct the IPI** — Matched-model Jevons/Törnqvist index. IPI peaked 312 (Q4 2024), declined to 246 (Q2 2025).
- [x] **Draft all paper sections** — abstract, introduction, related work, methods, findings, discussion, limitations, conclusion.
- [x] **Self-review and polish** — Fixed number inconsistencies, section numbering, redundancy, missing cross-references.

## Dropped

- ~~Consider supplementary platforms (Upwork, Freelancer, 99designs)~~ — dropped 2026-03-21: pilot confirmed Fiverr has sufficient coverage; no pivot needed.
- ~~Build Fiverr scraping pipeline (page-by-page)~~ — dropped 2026-03-21: replaced by bulk Wayback Machine archive download approach.

## Change Log

- 2026-03-23: Massive progress — extraction, clustering, IPI construction, full paper draft, and self-review all completed. Moved 8 items to Done. Active items now focus on validation, forecasting, figures, and scale-up.
- 2026-03-22: Expanded plan 03 into 3 phases. Size estimation done; Phase 1 active.
- 2026-03-21: Both plans completed in parallel. Pilot: GO. Scoping: taxonomy + related work drafted.
- 2026-03-21: Consolidated into 2 concrete plans. Added draft-section items to backlog.
- 2026-03-21: Initial to-do list created from paper plan.
