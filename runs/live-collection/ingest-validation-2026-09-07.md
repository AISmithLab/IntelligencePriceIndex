# Ingest validation — dry run on archived HTML, 2026-09-07

Not a live capture. 60 stored 2025 gig pages from `data/pilot/html-refresh2025/`
were pushed through the SAME JavaScript slicer step 84 embeds in the collector
and then through step 85, to prove the chain works before anyone spends a
browser session on it. It found and fixed two defects: the `reviews` slice
matched an inner object (2 bytes instead of 12 KB), and `title` was taking the
PACKAGE name rather than the gig's og:title.

The 0 orders in 2026Q2-Q3 below is the expected result for 2025 archive pages —
it is the counter that a real capture is meant to move.

---


Part-files read: 1. Gigs attempted: **37**. HTTP status: 200 37.

Pages with no `packageList`: 0. With no `reviews` blob: 0.

## What came back

- **37** listed-price rows (one per gig, dated by fetch).
- **35** order records from **11** gigs (3.2 per gig with any).
- **32** carry a closed price bucket (91.4%).
- **0** orders fall in **2026Q2-Q3** — the quarters neither archive holds (0.0% of the haul).

## Orders by quarter

| quarter | orders | priced | median paid (mid) |
|---|---:|---:|---:|
| 2020Q4 | 1 | 0 | - |
| 2022Q1 | 1 | 1 | 75 |
| 2022Q2 | 4 | 2 | 225 |
| 2022Q3 | 2 | 2 | 112 |
| 2023Q2 | 1 | 1 | 75 |
| 2023Q3 | 1 | 1 | 75 |
| 2024Q2 | 5 | 5 | 25 |
| 2024Q3 | 1 | 1 | 25 |
| 2024Q4 | 8 | 8 | 25 |
| 2025Q1 | 6 | 6 | 25 |
| 2025Q2 | 5 | 5 | 75 |

## 2026Q2-Q3 orders by category

| category | 2026Q2 | 2026Q3 |
|---|---:|---:|
| coding | 0 | 0 |

## Three selections that travel with every number above

1. **Survivorship.** Only still-listed gigs are reachable. Step 63B: 26-32% of the panel, and skewed — 43.8% of the top listed-price quartile against 22.4% of the bottom, 55.0% of the top review-count quartile against 20.8% of the bottom. Orders placed at listings that have since died are unreachable, so a recovered quarter looks healthier than the quarter was.
2. **Display.** A page shows ~4 of ~124 reviews, ranked by `relevancy_score`, not at random (step 59). Step 63A found no detectable PRICE selection in that ranking (late minus early median realised value +0 USD, CI [+0, +0]), which is why the price levels are usable; it does not make the sample of orders complete.
3. **Bucketing.** Fiverr publishes a range, not an amount. `paid_mid` is the midpoint of a closed bucket and is an assumption; open-topped buckets (`$X+`) have no midpoint and are excluded from every median above.

These are properties of the source. Collecting more pages narrows the confidence interval and does not touch any of the three.
