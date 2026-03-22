# Plan: Data Feasibility Pilot

**Status:** completed
**Created:** 2026-03-21
**Goal:** Determine whether Wayback Machine + Fiverr yields a viable longitudinal dataset before committing to full collection.

## Scope

Three questions to answer, each with a clear pass/fail:

1. **Coverage**: Does the Wayback Machine have enough Fiverr snapshots? Need ≥ 10 snapshots spanning ≥ 3 years for at least 3 task categories.
2. **Extraction**: Can we reliably parse task price, title, seller info from archived HTML? Need ≥ 80% extraction success on a 20-page sample.
3. **Worker tracking**: Can we track the same seller across snapshots to observe price changes? Need ≥ 5 sellers with 3+ snapshots each.

Out of scope: full pipeline, benchmark mapping, analysis.

## Steps

- [x] ~~Install and test `wayback-machine-downloader` tool~~ Used CDX API + curl directly instead (more flexible)
- [x] Pick 3 Fiverr category URLs to probe (e.g., logo design, article writing, web development)
- [x] Query Wayback Machine CDX API for snapshot counts and date ranges per category
- [x] Download ~20 archived pages across categories and time periods
- [x] Attempt price/title/seller extraction — document what HTML structure looks like, what's parseable
- [x] For the froggy92 example from idea.md, pull multiple snapshots and check if price/offering changed
- [x] Find 5+ additional sellers with multiple snapshots
- [x] Write up findings: pass/fail on each question, sample data, recommended next steps
- [x] If Fiverr fails: quick check on Upwork, Freelancer coverage as fallback

## Decision Gate

After this plan completes, one of three outcomes:

| Outcome | Criteria | Next step |
|---------|----------|-----------|
| **Go** | All 3 questions pass | Move to full data collection (promote backlog items in todo.md) |
| **Pivot** | Fiverr fails but alternatives look viable | New pilot plan for alternative platform |
| **Rethink** | No platform has sufficient coverage | Revisit data strategy — consider API-based approaches, platform partnerships, or scope change |

## Decision Log

- **2026-03-21:** Decision gate outcome: **GO**. All three criteria pass. Fiverr + Wayback Machine is a viable data source for longitudinal price tracking. Proceed to full data collection.

## Results Summary

### Q1: Coverage — PASS
- Writing & Translation: 50+ snapshots, 2012-2025 (13 years)
- Programming & Tech: 50+ snapshots, 2012-2025 (13 years)
- Graphics & Design: Sparse category pages, but individual gig pages well-archived
- Individual gig pages confirmed across 4+ categories with 3+ year spans

### Q2: Extraction — PASS (100%, 20/20)
- Primary method: JSON `packageList` embedded in page source (2018+), prices in cents
- Backup: HTML `<span class="price">` elements
- Fallback: `og:title` meta tag always contains starting price
- All 20 sample pages yielded: title, seller username, and at least one price tier

### Q3: Worker Tracking — PASS (6 sellers with 3+ snapshots)
| Seller | Category | Snapshots | Span | Price change |
|--------|----------|-----------|------|-------------|
| froggy92 | Architecture | 4 | 2020-2024 | $50 -> $20 (-60%) |
| joydeeproni | UI/UX | 4 | 2020-2022 | $5 -> $30 (+500%) |
| webexpert107 | Web Dev | 4 | 2018-2024 | $5 -> $25 (+400%) |
| seowriting94 | Writing | 3 | 2018-2023 | $50 -> $40 -> $50 |
| design_pro066 | Logo Design | 3 | 2020-2021 | $15 -> $10 (-33%) |
| writingexpert25 | SEO Writing | 3 | 2021-2022 | $50 (stable) |

### Key technical findings
- Fiverr embeds structured JSON pricing data (packageList) in page source — highly reliable for extraction
- Wayback Machine CDX API enables programmatic discovery of archived URLs
- Seller usernames are stable identifiers for longitudinal tracking
- Both price increases (reputation building) and decreases (potential AI competition) observed

### Fallback assessment
- Upwork: Moderate Wayback coverage (2019-2024), pricing visibility unclear
- Freelancer.com: Sparse coverage, lower priority
- Fiverr is clearly the best option — no pivot needed

## Data artifacts
- 20+ sample HTML pages: `runs/pilot-data-feasibility/*.html`
- Extraction results CSV: `runs/pilot-data-feasibility/extraction_results.csv`
- Full findings report: `runs/pilot-data-feasibility/findings.md`

## Progress

- 2026-03-21: Pilot completed. All steps executed. Decision: **GO**.

