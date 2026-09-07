# The 2025-2026 CDX refresh: what it adds, what is left to collect

Window: 202501 onward. Gig URLs with HTTP 200 only, deduplicated to one capture per gig per day.

## Where the captures come from

| pool | gig-days |
|---|---:|
| in the March 2026 all-time pull | 43,170 |
| in the 12-prefix refresh | 5,756 |
| **union** | **44,586** |
| of which the refresh adds outright | 1,416 (3.2%) |

## What is already on disk, and what is not

| pool | gig-days |
|---|---:|
| already downloaded by a past collection | 8,363 |
| indexed since March but never collected | 34,807 |
| newly visible in the refresh | 1,416 |
| **manifest total** | **36,223** |

The middle row is the cost of quota-ing over seven domains: those captures sat in the index the whole time and no manifest ever asked for them.

## Why the archive is thin here, in its own numbers

| status | March pull, 2025+ | refresh |
|---|---:|---:|
| 403 | 226,306 | 7,181 |
| - | 113,256 | 15,387 |
| 200 | 111,925 | 11,491 |
| 302 | 60,798 | 31,670 |
| 301 | 44,481 | 12,380 |
| 429 | 29,370 | 273 |
| 404 | 7,565 | 1,394 |
| 504 | 1,351 | 54 |

403 is the PerimeterX wall. A capture exists; its body is a CAPTCHA page and carries no price. Those rows are dropped here, not counted as supply.

## Manifest by quarter

| quarter | gig-days to collect |
|---|---:|
| 2025Q1 | 14,513 |
| 2025Q2 | 5,755 |
| 2025Q3 | 6,946 |
| 2025Q4 | 5,732 |
| 2026Q1 | 3,224 |
| 2026Q2 | 1 |
| 2026Q3 | 52 |

## Manifest by category

| category | gig-days | collected before? |
|---|---:|---|
| design | 12,352 | yes |
| coding | 6,593 | yes |
| writing | 4,055 | yes |
| uncategorized | 3,041 | **no** |
| marketing | 2,757 | yes |
| video | 1,933 | yes |
| data_entry | 1,013 | **no** |
| photography | 837 | **no** |
| gaming | 792 | **no** |
| audio | 686 | yes |
| translation | 441 | yes |
| social_engagement | 310 | **no** |
| ecommerce_ops | 306 | **no** |
| data_analysis | 241 | **no** |
| education_tutoring | 237 | **no** |
| legal | 182 | **no** |
| lifestyle_control | 145 | **no** |
| engineering_cad | 141 | **no** |
| accounting_consulting | 133 | **no** |
| customer_service_va | 28 | **no** |

Manifest written to `data/pilot/refresh-2025-manifest.tsv`. Feed it to `08-download-html.py --manifest ... --gzip`, then `09-extract-prices.py`.
