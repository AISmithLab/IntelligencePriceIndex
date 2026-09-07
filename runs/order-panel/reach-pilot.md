# Order panel — reach of the HTML already on disk (pilot)

Captures scanned: **1,500** over data/pilot/html-refresh2025. Pages parsed: 1,500, of which **716** carried at least one displayed order. Distinct gigs: 1,466.

Distinct orders after dedupe on `encrypted_order_id`: **2,958**.

## Orders by ORDER quarter (not capture quarter)

| quarter | orders | distinct gigs | priced | median paid (mid) |
|---|---:|---:|---:|---:|
| 2012Q4 | 1 | 1 | 0 | - |
| 2013Q1 | 2 | 1 | 0 | - |
| 2013Q2 | 1 | 1 | 0 | - |
| 2013Q3 | 1 | 1 | 0 | - |
| 2013Q4 | 1 | 1 | 0 | - |
| 2014Q2 | 2 | 1 | 0 | - |
| 2015Q3 | 2 | 1 | 0 | - |
| 2015Q4 | 6 | 2 | 0 | - |
| 2016Q1 | 2 | 1 | 0 | - |
| 2016Q3 | 1 | 1 | 0 | - |
| 2016Q4 | 8 | 3 | 0 | - |
| 2017Q1 | 1 | 1 | 0 | - |
| 2017Q2 | 8 | 3 | 0 | - |
| 2017Q3 | 2 | 2 | 0 | - |
| 2017Q4 | 3 | 3 | 0 | - |
| 2018Q1 | 11 | 4 | 2 | $75 |
| 2018Q2 | 5 | 4 | 3 | $75 |
| 2018Q3 | 4 | 2 | 4 | $112 |
| 2018Q4 | 5 | 4 | 2 | $188 |
| 2019Q1 | 7 | 6 | 2 | $112 |
| 2019Q2 | 3 | 3 | 3 | $75 |
| 2019Q3 | 5 | 5 | 3 | $150 |
| 2019Q4 | 13 | 6 | 1 | $75 |
| 2020Q1 | 10 | 7 | 6 | $112 |
| 2020Q2 | 8 | 5 | 1 | $75 |
| 2020Q3 | 11 | 7 | 4 | $75 |
| 2020Q4 | 13 | 7 | 0 | - |
| 2021Q1 | 19 | 11 | 6 | $75 |
| 2021Q2 | 24 | 18 | 6 | $75 |
| 2021Q3 | 23 | 16 | 2 | $150 |
| 2021Q4 | 26 | 16 | 11 | $150 |
| 2022Q1 | 33 | 19 | 10 | $300 |
| 2022Q2 | 35 | 21 | 14 | $150 |
| 2022Q3 | 36 | 22 | 15 | $150 |
| 2022Q4 | 38 | 23 | 16 | $112 |
| 2023Q1 | 53 | 36 | 19 | $75 |
| 2023Q2 | 54 | 38 | 31 | $75 |
| 2023Q3 | 56 | 40 | 56 | $25 |
| 2023Q4 | 80 | 54 | 77 | $25 |
| 2024Q1 | 105 | 72 | 105 | $25 |
| 2024Q2 | 149 | 85 | 149 | $25 |
| 2024Q3 | 120 | 82 | 120 | $25 |
| 2024Q4 | 488 | 214 | 487 | $25 |
| 2025Q1 | 420 | 209 | 420 | $25 |
| 2025Q2 | 328 | 146 | 326 | $25 |
| 2025Q3 | 370 | 151 | 367 | $25 |
| 2025Q4 | 312 | 114 | 312 | $25 |
| 2026Q1 | 48 | 26 | 48 | $75 |
| 2026Q2 | 4 | 1 | 0 | - |
| 2026Q3 | 1 | 1 | 0 | - |

## What this is not

This is a transaction series on **bucketed realised values**, not the IPI, which is a matched-model index on **listed** basic-package prices. They are different price objects and must not be chained together.

## Three limits, from steps 59 and 63

1. The paid-amount field appears **from 2022** only.
2. A page displays ~4 of ~124 reviews, ranked by `relevancy_score`, so this is a sample of each gig's orders. Step 63A found no **price** selection in that ranking (late minus early +0 USD, CI [+0, +0]).
3. Fiverr publishes a **range**, so `paid_mid` is the midpoint of a closed bucket and is an assumption; open-topped buckets are excluded from medians.
