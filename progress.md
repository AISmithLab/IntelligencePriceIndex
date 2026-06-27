# Progress Log

## 2026-06-27 — CSRankings-style IPI website built (monthly, client-side recompute)

- **Built the static IPI website** (`site/`), CSRankings-inspired: a category checklist drives a live, in-browser recompute of the composite index.
  - **`code/15-build-site-data.py`** — reuses step 14's matched-model machinery via `importlib` to emit the **monthly per-category index** (step 14 computes this internally but only ever wrote the monthly *composite*). No re-download or pipeline change. Output: **`site/data.json` (2.2 KB)** — just small arrays, none of the 21 GB of HTML.
  - **Monthly cadence** (user: "show the IPI per month"), **trailing 12 months only** = last 13 months with a real composite (2025-02 → 2026-02; no forward-filled phantom tail), each category **re-based to window-start = 100**.
  - **`site/index.html` + `site/ipi.js`** (vanilla JS + Plotly): heaviest-weighted-first checklist (each row shows Δ12mo, weight, panel gigs), bold composite + thin per-category lines, select-all/none, headline that updates with the basket. Composite recomputed client-side as `exp(Σ wᶜ·ln(idxᶜ)/Σ wᶜ)`, mirroring `composite()` in step 14.
  - **Validated offline** (no server, per user): JS syntax OK; client recompute over all categories reproduces `composite_all` exactly; unchecking design (71% wt) shifts the basket −2.1% → +0.8%.
  - **Headline:** all-categories composite trailing-12mo = **−2.1%** (2025-02→2026-02). **Caveat shipped on the page:** thin categories (audio/marketing/video; translation drops out monthly) read near-flat at monthly cadence; quarterly figures in `recent-ipi-summary.md` are more robust.
  - **Remaining:** GitHub Pages deploy.

## 2026-06-27 — Trailing-12-month IPI built (past-year data retrieval complete)

- **Resumed the stalled recent-window download** (was 12,949/15,309) via `code/run-recent-pipeline.sh`. Final: **15,150/15,309 captured (99.0%)**, 21 GB. The 159 misses are persistent Wayback 429/timeout (exhausted retries over 2 passes; no 403/ban signal).
- **Fixed a bug in `code/09-extract-prices.py`:** `filepath.relative_to(BASE_DIR)` crashed when `--html-dir` is a relative path (BASE_DIR is absolute). Now resolves the path first, falls back to the raw string. This had silently produced an empty `recent-prices.csv` on the first driver run, making the index build report "no data."
- **Extraction: 15,150/15,150 (100%)** → `data/pilot/recent-prices.csv`. Methods: packageList JSON 74.6%, dollar fallback 25.4%.
- **Trailing-12-month IPI built** (`code/14-recent-ipi.py`), matched-model, base 2024Q3=100, window 2024Q3→2026Q1. Panel: 3,566 gigs across 7 categories.
  - **Composite IPI essentially flat over the past year: 2025Q1 → 2026Q1 = −0.3%** (level ~90, down from the 100→100.5 2024 anchor — a one-step ~10% drop into 2025Q1, then flat).
  - Per-category Δ12mo: video −11.6%, coding −6.8%, writing −6.6%, translation −2.7%, marketing −1.2%, audio +0.6%, design +2.1%.
  - Weights are design-dominated (w=0.71) — design's +2.1% offsets the AI-exposed categories' declines, flattening the composite.
  - Outputs: `recent-ipi.csv`, `recent-category-indices.csv`, `recent-category-weights.csv`, `recent-ipi-monthly.csv`, `recent-ipi-summary.md`.
- **Unblocks the CSRankings-style website** (`plans/active/04-ipi-website.md`) — all data-contract CSVs now exist.

## 2026-06-26 — Recent-window data retrieval for trailing-12-month IPI

- **Goal:** extend the IPI to a genuine "past year" (CPI-style trailing 12 months) across all viable Fiverr categories. The original 500-seller pilot was sampled for long histories and goes sparse after 2024Q4, so it can't support a recent index.
- **Manifest (built prior session, `code/13-recent-manifest.py`):** `data/pilot/recent-manifest.tsv` — selects gigs with ≥2 distinct quarters of coverage anchored at 2024Q3 AND ≥1 snapshot in the trailing window (2025Q3–2026Q2), one snapshot/month each.
  - **15,309 snapshots, 3,589 distinct gigs, 7 categories:** design 6,959 / coding 2,634 / writing 2,198 / marketing 1,534 / video 1,295 / audio 437 / translation 252. Months span 202407–202603.
  - Thin categories excluded (uncategorized, data_entry, data_analysis).
- **Download (`code/08-download-html.py`):** launched full retrieval from Wayback Machine raw (`id_`) captures → `data/pilot/html-recent/`, log `recent-download-log.tsv`, checkpoint `recent-download-checkpoint.txt`.
  - Tuned concurrency: tested 10/24/10/20. Throughput is latency-bound (~1.6 MB raw fetches, ~15 s each). Failures are 429/timeout exhausted-retries logged as `fail` (NOT 403 — no ban signal) and are NOT checkpointed, so a second pass retries them. Settled on concurrency 20 / 20 req/s (~74% per-attempt success, ~1/s good throughput).
  - Validation: 210-snapshot pilot test (`recent-pilot-test.tsv` → `html-recent-test/`) had previously confirmed 100% extraction-grade captures.
- **Pending (this run):** finish full download (~24 GB est.), run a retry pass over `fail` rows, then extract prices into `data/pilot/recent-prices.csv` (parameterized `code/09-extract-prices.py` to accept `--html-dir/--output`).

## 2026-03-23 — IPI constructed, full paper drafted and self-reviewed

- **Price extraction:** 22,632/22,632 HTML files extracted (100% success). Methods: packageList JSON (72.9%), old JSON (15.2%), dollar fallback (11.2%), HTML span (0.7%). Output: `data/pilot/pilot-prices.csv`.
- **Item clustering:** 1,908 unique gigs clustered into 150 service items (TF-IDF + agglomerative, k=150, silhouette=0.114). Output: `data/pilot/gig-items.csv`, `data/pilot/item-clusters.csv`.
- **AI benchmark dataset:** Created `data/ai-benchmarks.csv` with 8 benchmarks (HumanEval, SWE-bench, WMT BLEU, AlpacaEval, Chatbot Arena, FID, GSM8K, Whisper WER) spanning 2017–2025.
- **IPI construction (cross-sectional):** Script `code/11-build-ipi.py` — Laspeyres-style index, 9 categories. Revealed platform-wide price inflation masking AI effects.
- **IPI construction (panel):** Script `code/12-panel-ipi.py` — Matched-model Jevons/Törnqvist index tracking same-gig prices. Key results:
  - IPI: 100 (2019Q1) → peak 312 (Q4 2024) → 246 (Q2 2025), **−21% from peak in 2025**.
  - Price elasticity of intelligence: audio β=−0.49 (substitution), writing β=+0.21, coding β=+0.30, marketing β=+0.70, design β=+1.10 (complementarity). All significant p<0.01.
  - Novel concept: "shadow deflation" — AI effect masked by platform inflation, visible only as deceleration.
- **Full paper drafted:** All 8 sections written (abstract, introduction, related work, methods, findings, discussion, limitations, conclusion).
- **Self-review and polish:** Fixed number inconsistencies (312% → "peaked at 312"), section numbering (8→7 sections), missing data flow explanation (14,938→1,908 gigs), added 4 missing categories to elasticity table, trimmed CPI analogy and survivorship bias redundancy, fixed broken cross-references in related work.
- Key outputs: `data/pilot/panel-ipi.csv`, `data/pilot/panel-summary.md`, `data/pilot/panel-elasticity.csv`, all drafts in `drafts/sections/`.

## 2026-03-22 — Phase 1 complete + Pilot download launched

- **Phase 1 (CDX filtering) complete:** Steps 1.1–1.6 all done.
  - Fixed OOM crashes in dedup/filter scripts by switching from in-memory dicts to external sort + streaming.
  - Full census: 5.6M unique gigs, 822K unique sellers across 10 categories + uncategorized.
  - 60M raw CDX → 22.7M deduped → classified by category → longitudinal filter applied.
- **Sampling strategy refined toward CPI-style index:**
  - User wants to track price impact of AI, weight by transaction volume (like CPI basket).
  - Decided to sample at user level (preserves within-seller panel for upskilling analysis).
  - Survivorship bias is acceptable — gig disappearance is part of the AI impact signal.
  - Wayback Machine coverage bias acknowledged as limitation (over-represents popular gigs).
- **Pilot: 500 users sampled** (from 48,643 qualifying users with ≥5 monthly snapshots spanning ≥2 years).
  - 500 users, 14,938 gigs, 26,603 monthly snapshots.
  - Download launched (~5 GB compressed, ~30–45 min).
  - Scripts: `code/06c-pilot-longitudinal.py`, `code/07-pilot-500.py`, `code/08-download-html.py`.
- Key outputs: `data/pilot/pilot-500-manifest.tsv`, `data/pilot/html/` (downloading).

## 2026-03-21 — CLAUDE.md updates: hajimi confirmation + user prompts as tests

- Added `hajimi` print directive to confirm CLAUDE.md is loaded (helps verify config in VS Code sessions).
- Added Philosophy #6: User prompts as first-class test inputs. Instructional prompts about paper content become test entries in `tests/<section>.test.md` under `## User Requirements`.

## 2026-03-21 — Fiverr archive size estimation complete

- ~2.5M unique gig URLs on Wayback Machine, 4–20 TB raw (too large for full download).
- Recommended strategy: two-phase filtered download — Tier 1 categories only (writing, coding, design, translation) with 3+ snapshots spanning 2+ years → ~275 GB compressed.
- Report saved to `runs/archive-size-estimation/report.md`.
- Plan updated: `plans/active/03-fiverr-archive-download.md` — Step 1 complete, Step 2 (download) pending.

## 2026-03-21 — Data Pilot GO + Scoping Complete (parallel execution)

**Data Feasibility Pilot — GO:**
- Wayback Machine has 50+ Fiverr snapshots per category spanning 2012–2025.
- Price extraction: 100% success (20/20 pages) via embedded JSON `packageList`.
- Worker tracking: 6 sellers tracked with 3+ snapshots each. Key finding: froggy92 (architecture) dropped from $50 → $20 (−60%) over 4 years.
- Upwork/Freelancer checked as fallback — not needed; Fiverr is best.
- Plan moved to `plans/completed/01-data-feasibility-pilot.md`.

**Scoping & Taxonomy — Complete:**
- 12-category taxonomy created in `data/task-taxonomy.md` (3 priority tiers).
- Benchmarks mapped per category with historical data sources verified.
- Related work drafted: ~4k words, 5 subsections, 30+ citations. Covers AI-labor, gig economy evidence, benchmarks, scaling laws, positioning table.
- 5 critique-and-improve iterations run. 18 reviewer simulation items in `tests/related-work.test.md`.
- Plan moved to `plans/completed/02-scoping-and-taxonomy.md`.

**Next:** Build scraping pipeline, collect benchmark histories, construct panel dataset.

## 2026-03-21 — Plans Restructured into Concrete Execution Plans

- Converted `paper-plan.md` → `plans/project-brief.md` (reference doc: positioning, structure, risks).
- Created two concrete execution plans:
  - `plans/active/01-data-feasibility-pilot.md` — Wayback Machine + Fiverr viability with clear pass/fail criteria and decision gate.
  - `plans/active/02-scoping-and-taxonomy.md` — task taxonomy, benchmark mapping, related work draft.
- Updated `plans/todo.md`: 2 active items linking to plans, backlog includes all draft sections.
- These two plans can run in parallel.

## 2026-03-21 — Paper Plan Drafted

- Created execution plan: `plans/active/paper-plan.md`.
- Analyzed model paper (GPTs are GPTs): identified strengths, gaps, and what we must exceed.
- Updated `tests/model-paper.test.md` with detailed benchmark comparison (10 dimensions).
- Plan has 6 phases: Scoping & Lit Review → Pilot → Full Data Collection → Core Analysis → Index & Forecasting → Paper Completion.
- Key innovation: price elasticity of intelligence (continuous, not binary exposure); longitudinal Fiverr data via Wayback Machine; forward-looking IPI under AI scaling scenarios.
- Key risk identified: Wayback Machine coverage — must pilot before committing to full collection.

## 2026-03-21 — Restructured docs and test infrastructure

- Decoupled `CLAUDE.md` into three files:
  - `CLAUDE.md` — agent philosophy and operating instructions only.
  - `setup.md` — agent bootstrapping and session-start checklist.
  - `README.md` — human-facing project overview and contributor guide.
- Restructured tests into three layers:
  - `tests/master.test.md` — cross-section quality criteria (applies to all sections).
  - `tests/<section>.test.md` — reviewer simulation only (removed model paper comparison from individual sections).
  - `tests/model-paper.test.md` — standalone model paper benchmark (replaces old `model-paper.md`).

## 2026-03-21 — Added Paper Test Infrastructure

- Added Philosophy #5: Paper test infrastructure with two lenses (reviewer simulation + model paper comparison).
- Created `tests/` directory with per-section test files (`*.test.md`) mirroring `drafts/sections/`.
- Created `tests/model-paper.md` for model paper analysis.
- Test files use PASS/FAIL/BLOCKED/N/A status for each critique and quality dimension.
- Clarified human workflow: user primarily edits plans, drafts, and test files; agents handle execution.

## 2026-03-21 — Added Plans Infrastructure

- Added Philosophy #4: Plans as first-class artifacts.
- Created `plans/active/`, `plans/completed/`, `plans/tech-debt-tracker.md`.
- Updated `CLAUDE.md` with plan file format, lifecycle (active → completed), and conventions.

## 2026-03-21 — Project Scaffolding

- Created `CLAUDE.md` with three core principles: minimize interruption, auditable progress, agile process.
- Set up drafts infrastructure: `drafts/main.md`, `drafts/sections/`, `drafts/render.py`.
- Created `progress.md` (this file) for reverse-chronological audit trail.
- Created project directories: `code/`, `data/`, `runs/`.
- Placeholder section files created for paper draft.
