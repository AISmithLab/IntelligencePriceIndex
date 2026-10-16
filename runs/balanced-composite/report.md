# Balanced-panel composite, 2020Q1-2024Q4

Built by `code/99-balanced-composite.py` from step 98's category indices. 34,967 gigs, 231,757 gig-quarters. No headline-index input. Fixed-weight geometric mean of the 7 category GEKS-Jevons indices, 2020Q1 = 100; band = 1.96 x sqrt(sum w^2 se^2) (categories are independent bootstraps).

## Weights

| category | sales (primary) | equal | gigs |
|---|---:|---:|---:|
| design | 0.290 | 0.143 | 0.117 |
| coding | 0.194 | 0.143 | 0.138 |
| writing | 0.165 | 0.143 | 0.106 |
| video | 0.120 | 0.143 | 0.135 |
| marketing | 0.115 | 0.143 | 0.228 |
| audio | 0.106 | 0.143 | 0.179 |
| translation | 0.011 | 0.143 | 0.097 |

Sales = median nominal price x reviews gained 2020Q1-2024Q4, per gig, summed; 27,161 of 34,967 gigs gained reviews.

## 2024Q4 under each weighting

| weights | nominal | real | real 95% band | half-width | meets ±5% | quarters meeting (of 19) |
|---|---:|---:|---|---:|---|---:|
| sales | +102.5% | +65.5% | [+62.0%, +69.1%] | ±2.1% | **yes** | 19 |
| equal | +92.5% | +57.4% | [+53.9%, +61.0%] | ±2.3% | **yes** | 19 |
| gigs | +97.8% | +61.7% | [+57.7%, +65.9%] | ±2.5% | **yes** | 19 |

## Sales-weighted composite by quarter

| quarter | nominal | real | real 95% band | half-width |
|---|---:|---:|---|---:|
| 2020Q1 | 100.0 | 100.0 | [100.0, 100.0] | ±0.0% |
| 2020Q2 | 102.1 | 103.1 | [101.8, 104.3] | ±1.2%* |
| 2020Q3 | 109.7 | 109.5 | [107.9, 111.2] | ±1.5%* |
| 2020Q4 | 115.5 | 114.5 | [112.7, 116.3] | ±1.5%* |
| 2021Q1 | 121.5 | 119.2 | [117.4, 121.1] | ±1.6%* |
| 2021Q2 | 129.5 | 124.8 | [122.8, 126.8] | ±1.6%* |
| 2021Q3 | 134.5 | 127.5 | [125.5, 129.6] | ±1.6%* |
| 2021Q4 | 142.3 | 132.1 | [129.9, 134.3] | ±1.7%* |
| 2022Q1 | 149.9 | 136.2 | [134.0, 138.4] | ±1.6%* |
| 2022Q2 | 157.5 | 139.8 | [137.4, 142.1] | ±1.7%* |
| 2022Q3 | 160.4 | 140.5 | [138.1, 142.9] | ±1.7%* |
| 2022Q4 | 164.3 | 142.4 | [139.9, 144.9] | ±1.7%* |
| 2023Q1 | 168.2 | 144.5 | [142.0, 147.1] | ±1.7%* |
| 2023Q2 | 174.4 | 148.8 | [146.1, 151.5] | ±1.8%* |
| 2023Q3 | 181.8 | 153.8 | [150.9, 156.7] | ±1.9%* |
| 2023Q4 | 189.4 | 159.0 | [156.0, 162.1] | ±1.9%* |
| 2024Q1 | 194.0 | 161.4 | [158.4, 164.6] | ±1.9%* |
| 2024Q2 | 198.7 | 164.3 | [161.0, 167.6] | ±2.0%* |
| 2024Q3 | 199.8 | 164.7 | [161.5, 167.9] | ±2.0%* |
| 2024Q4 | 202.5 | 165.5 | [162.0, 169.1] | ±2.1%* |

\* = meets ±5%.
