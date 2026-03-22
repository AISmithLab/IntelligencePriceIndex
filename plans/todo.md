# To-Do

## Active

- [ ] **Fiverr archive download (Phase 1: CDX index)** → [`plans/active/03-fiverr-archive-download.md`](active/03-fiverr-archive-download.md) — Download CDX index, filter to gig pages, classify by category, apply longitudinal filter, generate manifest. Size estimation done; download plan ready.
- [ ] **Collect AI benchmark score histories** — gather historical scores for benchmarks mapped in taxonomy (SWE-bench, Chatbot Arena, AlpacaEval, WMT, FID/CLIP, MATH). Source: Epoch AI, leaderboard archives, papers.

## Backlog

- [ ] Fiverr archive download (Phase 2: HTML download) — download filtered HTML pages from Wayback Machine using manifest from Phase 1
- [ ] Fiverr archive download (Phase 3: extraction) — parse downloaded HTML into `data/fiverr-prices.csv` using JSON `packageList` method
- [ ] Build linked panel dataset — join (task_category, date, price) with (benchmark, date, score) into analysis-ready dataset in `data/`.
- [ ] Estimate price elasticity of intelligence per task category
- [ ] Heterogeneity analysis: routine vs. judgment-intensive tasks
- [ ] Worker-level analysis: same worker over time — upskilling vs. price reduction
- [ ] Construct the IPI: weighted index across categories
- [ ] Forward-looking forecasts under AI scaling scenarios
- [ ] Validation: compare IPI to GPTs-are-GPTs exposure scores, Anthropic index, BLS wage data
- [ ] Draft introduction section (after results are known)
- [ ] Draft methods section (after data pipeline is built)
- [ ] Draft findings sections (after analysis)
- [ ] Draft discussion, limitations, conclusion
- [ ] Draft abstract (last)

## Done

- [x] **Data feasibility pilot** → `plans/completed/01-data-feasibility-pilot.md` — Decision: **GO**. All 3 criteria pass. Fiverr + Wayback Machine viable. JSON `packageList` extraction 100% success. 6 sellers tracked with price changes over time.
- [x] **Scoping & taxonomy** → `plans/completed/02-scoping-and-taxonomy.md` — 12-category taxonomy in `data/task-taxonomy.md`. Benchmark mapping complete. Related work drafted (~4k words, 30+ citations, 5 subsections). 18 reviewer simulation items addressed. 5 critique-and-improve iterations completed.

## Dropped

- ~~Consider supplementary platforms (Upwork, Freelancer, 99designs)~~ — dropped 2026-03-21: pilot confirmed Fiverr has sufficient coverage; no pivot needed.
- ~~Build Fiverr scraping pipeline (page-by-page)~~ — dropped 2026-03-21: replaced by bulk Wayback Machine archive download approach. Parse offline instead of scrape live.

## Change Log

- 2026-03-22: Expanded plan 03 into 3 phases (CDX index → HTML download → extraction). Size estimation done; Phase 1 active, Phases 2–3 in backlog.
- 2026-03-21: Replaced page-by-page scraping approach with bulk Wayback Machine archive download. New plan 03 for size estimation + download. Moved extraction pipeline to backlog (runs after download).
- 2026-03-21: Both plans completed in parallel. Pilot: GO. Scoping: taxonomy + related work drafted. Promoted 3 new active items for data collection phase. Dropped supplementary platform investigation.
- 2026-03-21: Consolidated 6 active items into 2 concrete plans (data pilot, scoping/taxonomy). Added draft-section items to backlog. Moved paper-plan.md to project-brief.md.
- 2026-03-21: Initial to-do list created from paper plan.
