# Plan: thicken the 2025–26 frame — which collection routes actually exist

**Status:** active (route audit done; one decision open)
**Created:** 2026-08-19
**Goal:** establish, on measurement rather than assumption, every route to more 2025–26 Fiverr price data, and cost each one.

## Why this exists

`plans/todo.md` PRIORITY 1: the 2024Q3–2026Q1 frame is 4–6× too thin to test the
operators' claims (realised MDE 0.131 / 0.083 vs balanced-frame effects −0.033 /
−0.014). The todo asserted a live forward crawl was the only route. That was an
inference from one observation ("2026Q2 captures are ~all 403"). This plan
measures every route instead.

## Route audit, 2026-08-19 — all findings are measured, not assumed

### R1. Re-harvest the Wayback CDX index — REAL BUT SMALL

Our index was harvested **2026-03-22**. Wayback's CDX index lags, so a re-pull
recovers captures that existed then but were not yet indexed. Measured on prefix
`z` (0.95% of the 60.0M-record corpus), status-200 gig pages per month, ours vs
live today:

| month | our index | live CDX today | gain |
|---|---:|---:|---|
| 202507 | 20 | 19 | 1.0× |
| 202508 | 62 | 69 | 1.1× |
| 202509 | 18 | 51 | 2.8× |
| 202510 | 16 | 67 | 4.2× |
| 202511 | 31 | 54 | 1.7× |
| 202512 | 45 | 47 | 1.0× |
| 202601 | 43 | 85 | 2.0× |
| 202602 | 29 | 29 | 1.0× |
| 202603+ | 0 | 0 | — |

Pooled 202507–202603: **202 → 314, i.e. 1.55×.** Free, already scripted
(`code/01-download-cdx-index.py` is wired for a 2025 window), ~hours of runtime.

### R2. Exhaust the archive we have ALREADY indexed — ~2×, and it is the cheapest real gain

Distinct gigs in the index vs distinct gigs we actually hold prices for:

| quarter | index supply | downloaded | captured |
|---|---:|---:|---:|
| 2025Q1 | 7,789 | 3,777 | 48% |
| 2025Q2 | 4,589 | 2,037 | 44% |
| 2025Q3 | 4,769 | 2,101 | 44% |
| 2025Q4 | 3,867 | 1,799 | 47% |
| 2026Q1 | 2,377 | 1,304 | 55% |

Roughly half the indexed recent supply has never been downloaded. No new source,
no new code — rebuild the recent manifest without the selection rule and re-run
`08` → `09`.

**R1 + R2 ceiling is ~2–3× in n**, which on 1/√n is **1.4–1.7× on the MDE**. That
is short of the ~6× the todo asks for, and it buys **nothing after 2026Q1**.

### R3. Common Crawl — DEAD, do not pursue

`CC-MAIN-2026-30` (July 2026) holds **414** fiverr.com URLs; 195 are 403, 191 are
301, and all **28** status-200 records are `robots.txt`. **Zero gig pages.**
`CC-MAIN-2025-38` is the same shape (363 records, 232× 403, 34× 200, zero gigs).
Fiverr 403s CCBot. Closed on evidence.

### R4. Why the archive died — measured, and it is not going to recover

A plain GET of a live gig page returns **HTTP 403, PerimeterX, title
"It needs a human touch"**. Wayback's crawler hits the same wall, which is what
the collapse in the census actually is. Status-200 gig captures per month, live
CDX, prefix `a` (~9% of corpus): 202604 **9**, 202605 **8**, 202606 **13**,
202607 **31**, 202608 **8** — platform-wide on the order of **100–350/month**,
against ~20,000/month in 2024Q3. **The archive route to 2026Q2+ does not exist.**

### R5. The gig sitemap — free, open, and it was not on the agenda

`robots.txt` publishes `sitemap_gigs.xml.gz`. It is **not behind the bot wall**
(200 to plain curl), is regenerated **daily**, and resolves to 7 sub-sitemaps
holding **288,976 distinct `seller/slug` gig URLs**, 5.9 MB gzipped.

`code/56-sitemap-snapshot.py` written and **first snapshot taken 2026-08-19**
(`data/sitemap/gigs-2026-08-19.txt.gz`). It is append-only and dated; a day not
snapshotted is lost forever, which is why it ran before the crawl decision.

What it gives:
- the live gig universe on the snapshot date
- a **target list** for any live crawl — 289k listed, well-reviewed gigs
- cohort entry/exit signal from snapshot differences

**Two results already, from the first snapshot alone:**

1. **Archive dropout is not exit.** Share of panel gigs still listed today, by
   the quarter they were *last archived*: 2023Q1 **27.8%**, 2023Q4 36.6%, 2024Q3
   57.2%, 2024Q4 60.8%, 2025Q1 36.1%, 2026Q1 **40.6%**. Near-flat. A gig that
   vanished from the archive in 2023 is about as likely to be trading today as
   one that vanished in 2026 — so disappearance from the archive is a sampling
   artifact, and the dormancy proxy inherits that.
2. **The sitemap is rank-selected, so it is NOT a clean exit measure.** Share
   listed today by review-count decile of the balanced panel: **3.2%** (0–1
   reviews) rising monotonically to **63.3%** (716+). Fiverr publishes its best
   ~289k gigs, not all of them; absence conflates delisting with demotion. Using
   it as an exit hazard requires the live page to separate the two.

### R6. Wayback Save Page Now — untested, expected to fail

SPN would fetch the same page Wayback's crawler already 403s on. Cheap to test,
low expected value.

## The one open decision

**Do we run a live browser crawl?** It is the only route that produces 2026Q2+
prices and the only one that reaches the todo's target.

- `robots.txt` does **not** disallow `/seller/gig-slug`.
- Plain HTTP is 403; it needs a real browser fingerprint (Playwright/stealth, or
  the user's own Chrome). Neither Playwright nor Selenium is installed; Firefox is.
- CLAUDE.md requires the user's sign-off before crawling a site where the IP may
  get banned. **This is that case.**
- Timing reality: a crawl started today yields 2026Q3 and 2026Q4, so the first
  within-gig link lands ~January 2027. **It does not retroactively fill 2025.**

## Steps

- [x] Audit every collection route on measurement (R1–R6)
- [x] Write `code/56-sitemap-snapshot.py`; take the 2026-08-19 snapshot
- [x] Test archive-dropout-vs-exit and sitemap selection on the first snapshot
- [ ] Put the sitemap snapshot on a daily schedule (1 request/day, ~6 MB)
- [ ] R2: rebuild the recent manifest without the selection rule, re-run `08`→`09`
- [ ] R1: re-harvest CDX for 202501+ into `data/cdx-index/raw-2025/`, merge, re-census
- [ ] DECISION: live browser crawl — yes/no, and at what rate
- [ ] Re-run designs 7 and 8 on the thickened frame; report the new realised MDE

## Decision Log
- 2026-08-19: Common Crawl closed on evidence (zero gig pages in two crawls).
- 2026-08-19: Snapshotted the sitemap before asking, because the option decays
  daily and the action is one public GET.

## Progress
- 2026-08-19: Route audit complete. R1 1.55×, R2 ~2×, R3 dead, R4 explains the
  collapse, R5 new and free, R6 untested. Live crawl decision open.
