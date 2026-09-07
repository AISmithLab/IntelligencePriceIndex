# Order panel — reach of the HTML already on disk (all)

Captures scanned: **397,698** over data/pilot/html-refresh2025, data/pilot/html-recent, data/pilot/html-balanced. Pages parsed: 397,698, of which **211,982** carried at least one displayed order. Distinct gigs: 76,884.

Distinct orders after dedupe on `encrypted_order_id`: **681,668**.

## Orders by ORDER quarter (not capture quarter)

| quarter | orders | distinct gigs | priced | median paid (mid) |
|---|---:|---:|---:|---:|
| 2010Q4 | 2 | 2 | 0 | - |
| 2011Q1 | 7 | 2 | 0 | - |
| 2011Q2 | 3 | 1 | 0 | - |
| 2011Q3 | 7 | 5 | 0 | - |
| 2011Q4 | 9 | 4 | 0 | - |
| 2012Q1 | 10 | 6 | 0 | - |
| 2012Q2 | 14 | 7 | 0 | - |
| 2012Q3 | 12 | 6 | 0 | - |
| 2012Q4 | 17 | 9 | 0 | - |
| 2013Q1 | 22 | 9 | 0 | - |
| 2013Q2 | 31 | 19 | 0 | - |
| 2013Q3 | 28 | 16 | 0 | - |
| 2013Q4 | 23 | 14 | 0 | - |
| 2014Q1 | 26 | 19 | 2 | $12 |
| 2014Q2 | 43 | 19 | 0 | - |
| 2014Q3 | 25 | 10 | 1 | $75 |
| 2014Q4 | 24 | 14 | 0 | - |
| 2015Q1 | 26 | 16 | 1 | $12 |
| 2015Q2 | 44 | 17 | 4 | $112 |
| 2015Q3 | 39 | 19 | 4 | $112 |
| 2015Q4 | 43 | 25 | 3 | $150 |
| 2016Q1 | 57 | 33 | 3 | $150 |
| 2016Q2 | 63 | 33 | 6 | $112 |
| 2016Q3 | 48 | 33 | 6 | $150 |
| 2016Q4 | 66 | 39 | 4 | $75 |
| 2017Q1 | 58 | 34 | 2 | $268 |
| 2017Q2 | 83 | 50 | 4 | $75 |
| 2017Q3 | 77 | 53 | 16 | $150 |
| 2017Q4 | 125 | 78 | 19 | $75 |
| 2018Q1 | 158 | 94 | 26 | $150 |
| 2018Q2 | 157 | 99 | 38 | $300 |
| 2018Q3 | 171 | 116 | 49 | $300 |
| 2018Q4 | 217 | 138 | 59 | $150 |
| 2019Q1 | 254 | 172 | 66 | $150 |
| 2019Q2 | 279 | 182 | 92 | $150 |
| 2019Q3 | 415 | 259 | 118 | $150 |
| 2019Q4 | 414 | 276 | 131 | $150 |
| 2020Q1 | 499 | 330 | 149 | $150 |
| 2020Q2 | 763 | 471 | 219 | $150 |
| 2020Q3 | 1,109 | 709 | 338 | $150 |
| 2020Q4 | 1,356 | 871 | 396 | $150 |
| 2021Q1 | 2,037 | 1,235 | 589 | $75 |
| 2021Q2 | 3,401 | 1,966 | 937 | $75 |
| 2021Q3 | 9,176 | 4,473 | 1,439 | $75 |
| 2021Q4 | 42,751 | 11,510 | 4,381 | $75 |
| 2022Q1 | 44,119 | 11,720 | 29,589 | $150 |
| 2022Q2 | 48,225 | 12,858 | 29,405 | $150 |
| 2022Q3 | 52,027 | 12,819 | 28,324 | $150 |
| 2022Q4 | 51,319 | 12,657 | 28,563 | $150 |
| 2023Q1 | 48,904 | 12,642 | 27,070 | $150 |
| 2023Q2 | 42,516 | 12,276 | 24,770 | $150 |
| 2023Q3 | 51,848 | 13,005 | 30,734 | $150 |
| 2023Q4 | 48,776 | 13,066 | 29,974 | $150 |
| 2024Q1 | 38,058 | 11,750 | 25,448 | $150 |
| 2024Q2 | 55,570 | 16,240 | 52,409 | $75 |
| 2024Q3 | 80,391 | 17,341 | 80,218 | $75 |
| 2024Q4 | 23,374 | 9,159 | 23,332 | $25 |
| 2025Q1 | 10,236 | 4,479 | 10,220 | $25 |
| 2025Q2 | 7,360 | 3,296 | 7,348 | $25 |
| 2025Q3 | 7,233 | 2,912 | 7,220 | $25 |
| 2025Q4 | 6,602 | 2,250 | 6,601 | $25 |
| 2026Q1 | 898 | 450 | 898 | $25 |
| 2026Q2 | 12 | 3 | 8 | $50 |
| 2026Q3 | 11 | 6 | 10 | $25 |

## What this is not

This is a transaction series on **bucketed realised values**, not the IPI, which is a matched-model index on **listed** basic-package prices. They are different price objects and must not be chained together.

## Three limits, from steps 59 and 63

1. The paid-amount field appears **from 2022** only.
2. A page displays ~4 of ~124 reviews, ranked by `relevancy_score`, so this is a sample of each gig's orders. Step 63A found no **price** selection in that ranking (late minus early +0 USD, CI [+0, +0]).
3. Fiverr publishes a **range**, so `paid_mid` is the midpoint of a closed bucket and is an assumption; open-topped buckets are excluded from medians.
