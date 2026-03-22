# Plan: Scoping & Taxonomy

**Status:** completed
**Created:** 2026-03-21
**Goal:** Define the task taxonomy, map categories to AI benchmarks, and produce a literature review draft.

## Scope

Three deliverables:

1. **Task taxonomy**: A table of gig-economy task categories we will track, with examples from Fiverr/Upwork.
2. **Benchmark mapping**: For each task category, which AI benchmark(s) measure the relevant capability (e.g., coding → SWE-bench, writing → various LLM benchmarks, image gen → FID/CLIP scores).
3. **Related work draft**: A draft of `drafts/sections/related-work.md` covering AI & labor economics, gig economy pricing, AI benchmarks as capability proxies.

Out of scope: data collection, analysis, other draft sections.

## Steps

- [x] Survey Fiverr/Upwork category pages to identify major task categories
- [x] Draft task taxonomy table: category, example tasks, example platforms, candidate AI benchmarks
- [x] For each category, identify 1–3 AI benchmarks with historical scores available
- [x] Verify benchmark score histories are accessible (papers, leaderboard archives, APIs)
- [x] Literature search: AI labor market impact papers (Autor, Acemoglu, Brynjolfsson, Felten, Frey & Osborne)
- [x] Literature search: gig economy pricing and platform economics
- [x] Literature search: AI benchmarks as capability measures, scaling laws
- [x] Draft `drafts/sections/related-work.md`
- [x] Update `tests/related-work.test.md` with reviewer simulation items
- [x] Think about potential attacks to the work, improve the produced text, and repeat the process for 5 loops

## Decision Log

- **2026-03-21:** Identified 12 task categories spanning both Fiverr and Upwork platforms. Organized into 3 priority tiers based on benchmark data depth, platform volume, and existing displacement evidence.
- **2026-03-21:** Tier 1 (strongest data): Writing, Coding, Graphic Design, Translation. These have deep benchmark histories and empirical displacement evidence (Demirci et al. 2024, Hui et al. 2023).
- **2026-03-21:** Tier 2 (good data): Data Entry, Data Analysis, Customer Service. Strong general LLM benchmarks apply.
- **2026-03-21:** Tier 3 (emerging): Digital Marketing, Legal, Video, Audio, Accounting. Benchmarks are newer or fragmented.
- **2026-03-21:** Selected Epoch AI benchmark tracker as primary source for historical benchmark scores -- covers 37 benchmarks with Epoch Capabilities Index as composite fallback.
- **2026-03-21:** Decided to use both task-specific benchmarks (SWE-bench for coding, WMT for translation) and composite ECI for robustness. Will test sensitivity to benchmark choice.
- **2026-03-21:** Related work structured as 5 subsections: (2.1) AI & labor market, (2.2) gig economy empirical evidence, (2.3) AI benchmarks, (2.4) scaling laws & forecasting, (2.5) positioning table. Mirrors model paper's thematic subsection structure.
- **2026-03-21:** 5 iterative improvement loops completed. Key weaknesses addressed: endogeneity, quality vs. price, benchmark ecological validity, emergent abilities debate, geographic heterogeneity, confounding factors, scope limitations, CPI analogy grounding, prediction-judgment spectrum operationalization.

## Progress

- **2026-03-21:** All 3 deliverables produced:
  - `data/task-taxonomy.md` — 12-category taxonomy with benchmark mapping, priority tiers, and benchmark availability summary
  - `drafts/sections/related-work.md` — ~3,500-word draft with 5 subsections, 30+ citations, comparison table
  - `tests/related-work.test.md` — 18 reviewer simulation items (R1–R18), 10 quality checks (Q1–Q10)
- **2026-03-21:** 5 critique-and-improve iterations completed:
  - Iteration 1: Platform pricing mechanisms, confounds, benchmark-to-task validity, price elasticity grounding
  - Iteration 2: Quality vs. price distinction, geographic heterogeneity, emergent abilities debate, Noy & Zhang citation
  - Iteration 3: New task creation (reinstatement effect), CPI methodology citations, image/video/audio benchmarks, tone adjustment
  - Iteration 4: Endogeneity in AI research direction, Wayback Machine methodology precedents, hedonic pricing, prediction-judgment operationalization
  - Iteration 5: GPT theory (Bresnahan & Trajtenberg), scope limitation flagging, complementarity thesis (Autor 2015), open-source vs. closed-source
