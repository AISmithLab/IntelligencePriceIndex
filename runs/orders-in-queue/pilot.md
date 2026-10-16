# Orders in Queue — pilot

Captures: **70,759** across **7,807 gigs** (design, translation), balanced panel. Source: `data/pilot/queue-pilot.csv`.

## 1. Coverage by year

| year | captures | json | text only | none | coverage | share 0 | median | p90 | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 3,493 | 299 | 2,251 | 943 | 73% | 4% | 3 | 11 | 402 |
| 2019 | 9,130 | 6,808 | 1,622 | 700 | 92% | 27% | 2 | 9 | 437 |
| 2020 | 12,163 | 12,149 | 3 | 11 | 100% | 33% | 1 | 8 | 326 |
| 2021 | 11,918 | 11,913 | 3 | 2 | 100% | 30% | 1 | 8 | 396 |
| 2022 | 11,937 | 11,937 | 0 | 0 | 100% | 30% | 1 | 8 | 483 |
| 2023 | 9,937 | 9,937 | 0 | 0 | 100% | 23% | 2 | 10 | 841 |
| 2024 | 9,388 | 9,387 | 0 | 1 | 100% | 34% | 1 | 9 | 852 |
| 2025 | 2,477 | 2,474 | 0 | 3 | 100% | 53% | 0 | 12 | 624 |
| 2026 | 316 | 316 | 0 | 0 | 100% | 43% | 1 | 10 | 580 |

*Text-only rows (2018) cannot record a 0 — the page hides the line — so 2018 values are conditional on a positive queue and are excluded below.*

## 2. Does the queue track demand?

Gig-quarter panel (JSON captures only): **65,220** gig-quarters, **7,705** gigs, 2018Q3–2026Q1; 0% of gig-quarters average more than one capture.

`dReviews (into q)` = reviews gained from q-1 to q; `dReviews (out of q)` = reviews gained from q to q+1 — orders in the queue at q are completed, and reviewed, after it. Consecutive quarters only.

| association | n | Spearman ρ (pooled) | within-quarter ρ (median over quarters) | within-gig ρ |
|---|---:|---:|---:|---:|
| queue vs dReviews (into q) | 46,893 | +0.529 | +0.548 | +0.233 |
| queue vs dReviews (out of q) | 46,893 | +0.534 | +0.566 | +0.239 |

Mean reviews gained in the next quarter, by queue level:

| queue at q | gig-quarters | mean dReviews (out of q) | median |
|---|---:|---:|---:|
| 0 | 12,404 | 12.8 | 4 |
| (0, 1] | 9,230 | 23.8 | 13 |
| (1, 3] | 10,667 | 36.1 | 22 |
| (3, 10] | 10,458 | 61.6 | 39 |
| > 10 | 4,134 | 205.5 | 94 |

## 3. Raw quarterly path (JSON captures, gig-quarter means)

Composition is not held fixed here; the gig-FE contrast below is.

| quarter | design n | design mean | design % > 0 | translation n | translation mean | translation % > 0 |
|---|---:|---:|---:|---:|---:|---:|
| 2019Q1 | 339 | 3.73 | 64% | 166 | 1.78 | 66% |
| 2019Q2 | 1,061 | 6.29 | 73% | 258 | 2.47 | 70% |
| 2019Q3 | 1,541 | 5.71 | 72% | 397 | 1.37 | 52% |
| 2019Q4 | 1,930 | 4.37 | 72% | 1,116 | 1.20 | 48% |
| 2020Q1 | 2,142 | 3.97 | 69% | 1,227 | 0.99 | 47% |
| 2020Q2 | 2,075 | 4.46 | 69% | 914 | 1.54 | 63% |
| 2020Q3 | 2,055 | 5.60 | 73% | 875 | 1.65 | 66% |
| 2020Q4 | 1,986 | 5.62 | 74% | 875 | 1.75 | 68% |
| 2021Q1 | 1,920 | 5.54 | 73% | 855 | 1.69 | 62% |
| 2021Q2 | 2,077 | 5.55 | 74% | 914 | 1.77 | 65% |
| 2021Q3 | 2,293 | 5.03 | 74% | 967 | 1.47 | 62% |
| 2021Q4 | 2,039 | 5.32 | 75% | 848 | 1.24 | 54% |
| 2022Q1 | 2,078 | 4.95 | 71% | 842 | 1.16 | 52% |
| 2022Q2 | 2,060 | 5.65 | 74% | 795 | 1.34 | 55% |
| 2022Q3 | 2,326 | 5.39 | 74% | 968 | 1.59 | 61% |
| 2022Q4 | 2,166 | 5.91 | 74% | 702 | 1.95 | 71% |
| 2023Q1 | 2,185 | 5.92 | 76% | 672 | 1.77 | 67% |
| 2023Q2 | 1,906 | 7.62 | 81% | 531 | 1.91 | 64% |
| 2023Q3 | 1,749 | 8.15 | 83% | 557 | 1.74 | 62% |
| 2023Q4 | 1,793 | 7.67 | 83% | 544 | 1.52 | 60% |
| 2024Q1 | 1,790 | 6.91 | 80% | 515 | 1.32 | 52% |
| 2024Q2 | 1,676 | 7.80 | 71% | 400 | 1.17 | 46% |
| 2024Q3 | 2,155 | 6.35 | 69% | 505 | 1.35 | 50% |
| 2024Q4 | 2,030 | 5.77 | 61% | 316 | 1.23 | 47% |
| 2025Q1 | 1,044 | 6.26 | 40% | 44 | 1.64 | 48% |
| 2025Q2 | 388 | 9.69 | 43% | 12 | 0.17 | 17% |
| 2025Q3 | 500 | 9.88 | 56% | 7 | 1.29 | 29% |
| 2025Q4 | 471 | 7.65 | 56% | 8 | 1.12 | 62% |
| 2026Q1 | 312 | 9.73 | 57% | 4 | 1.00 | 50% |

## 4. Within-gig change across 2022Q4 (descriptive, no exposure contrast)

Gigs with JSON captures both in 2021Q1–2022Q3 and 2023Q1–2024Q3 (the post window skips the launch quarter; both end before the 2024Q4 capture thinning). Change in each gig's mean queue and in its share of quarters with a queue.

| category | gigs | pre mean | post mean | Δ mean (gig-paired) | 95% CI | pre % > 0 | post % > 0 |
|---|---:|---:|---:|---:|---|---:|---:|
| design | 2,612 | 5.08 | 6.05 | +0.97 | [+0.42, +1.57] | 74% | 73% |
| translation | 814 | 1.95 | 1.66 | -0.29 | [-0.40, -0.17] | 71% | 66% |

*Survivor panel: gigs seen on both sides. A demand loss that shows up as exit is invisible here, as in every within-gig test in this project.*

## 5. Event study: translation minus design, gig-demeaned, 2022Q3 = 0

Gig bootstrap, 200 draws; * = 95% interval excludes 0. Window 2019Q4–2024Q4. Two categories only — this is a contrast, not the exposure DiD.

| quarter | log(1+queue) | 95% CI | P(queue > 0) | 95% CI |
|---|---:|---|---:|---|
| 2019Q4 | +0.017 | [-0.033, +0.064] | -0.007 | [-0.041, +0.032] |
| 2020Q1 | -0.004 | [-0.049, +0.043] | -0.021 | [-0.054, +0.018] |
| 2020Q2 | +0.031 | [-0.027, +0.090] | +0.021 | [-0.021, +0.059] |
| 2020Q3 | -0.035 | [-0.096, +0.014] | +0.006 | [-0.032, +0.047] |
| 2020Q4 | -0.008 | [-0.067, +0.039] | +0.013 | [-0.024, +0.045] |
| 2021Q1 | -0.029 | [-0.096, +0.023] | -0.009 | [-0.045, +0.027] |
| 2021Q2 | -0.000 | [-0.053, +0.052] | +0.013 | [-0.031, +0.048] |
| 2021Q3 | -0.010 | [-0.070, +0.048] | +0.010 | [-0.023, +0.047] |
| 2021Q4 | -0.034 | [-0.080, +0.007] | -0.002 | [-0.038, +0.034] |
| 2022Q1 | +0.014 | [-0.036, +0.061] | +0.009 | [-0.024, +0.044] |
| 2022Q2 | -0.039 | [-0.089, +0.010] | +0.005 | [-0.032, +0.040] |
| 2022Q3 | +0.000 | [+0.000, +0.000] | +0.000 | [+0.000, +0.000] |
| 2022Q4 | +0.031 | [-0.021, +0.081] | +0.042* | [+0.009, +0.080] |
| 2023Q1 | -0.014 | [-0.074, +0.032] | -0.003 | [-0.039, +0.032] |
| 2023Q2 | -0.099* | [-0.156, -0.048] | -0.027 | [-0.060, +0.017] |
| 2023Q3 | -0.143* | [-0.203, -0.084] | -0.035 | [-0.074, +0.002] |
| 2023Q4 | -0.124* | [-0.184, -0.066] | -0.047* | [-0.091, -0.004] |
| 2024Q1 | -0.134* | [-0.200, -0.076] | -0.067* | [-0.110, -0.028] |
| 2024Q2 | -0.052 | [-0.108, +0.010] | -0.011 | [-0.057, +0.037] |
| 2024Q3 | -0.050 | [-0.107, +0.010] | +0.011 | [-0.029, +0.047] |
| 2024Q4 | -0.066* | [-0.122, -0.005] | -0.010 | [-0.055, +0.034] |

Pre-period (2019Q4–2022Q2): **0 of 11** quarters significant on log(1+queue); mean -0.008. Post 2023Q1–2024Q3 mean -0.088.

