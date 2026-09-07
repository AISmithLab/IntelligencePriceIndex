# Realised order value, $50+ segment, 2022Q1-2026Q1

From **617,456** orders recovered by step 86 out of HTML already on disk — no new collection, and unaffected by the wall that closed 2025-2026 to the crawler.

## The series

| quarter | n ($50+) | gigs | $50-100 | $100-200 | $200-400 | $400-800 | $800+ | median bin |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2022Q1 | 25,687 | 8,654 | 35.7% | 32.9% | 19.4% | 8.5% | 3.6% | $100-200 |
| 2022Q2 | 29,415 | 9,828 | 36.2% | 32.8% | 19.5% | 7.8% | 3.7% | $100-200 |
| 2022Q3 | 28,336 | 9,716 | 39.5% | 32.0% | 18.1% | 7.0% | 3.4% | $100-200 |
| 2022Q4 | 28,572 | 9,554 | 38.6% | 32.5% | 18.5% | 7.3% | 3.1% | $100-200 |
| 2023Q1 | 27,075 | 9,385 | 39.4% | 32.4% | 18.4% | 7.0% | 2.9% | $100-200 |
| 2023Q2 | 24,243 | 9,094 | 39.1% | 32.4% | 18.2% | 7.1% | 3.3% | $100-200 |
| 2023Q3 | 29,250 | 9,736 | 38.3% | 32.5% | 18.6% | 7.5% | 3.0% | $100-200 |
| 2023Q4 | 28,031 | 9,691 | 38.0% | 32.6% | 19.1% | 7.3% | 3.0% | $100-200 |
| 2024Q1 | 22,136 | 8,385 | 36.8% | 32.5% | 19.3% | 8.0% | 3.4% | $100-200 |
| 2024Q2 | 30,233 | 11,391 | 39.1% | 31.4% | 18.7% | 7.4% | 3.5% | $100-200 |
| 2024Q3 | 40,393 | 12,352 | 40.7% | 31.0% | 17.9% | 7.2% | 3.3% | $100-200 |
| 2024Q4 | 11,171 | 5,337 | 39.5% | 30.5% | 18.0% | 7.7% | 4.3% | $100-200 |
| 2025Q1 | 4,483 | 2,368 | 40.3% | 29.9% | 17.8% | 8.2% | 3.9% | $100-200 |
| 2025Q2 | 3,197 | 1,751 | 41.1% | 28.1% | 16.7% | 9.0% | 5.1% | $100-200 |
| 2025Q3 | 3,474 | 1,725 | 39.4% | 30.6% | 17.6% | 7.8% | 4.6% | $100-200 |
| 2025Q4 | 3,161 | 1,404 | 39.5% | 29.3% | 18.3% | 7.5% | 5.3% | $100-200 |
| 2026Q1 | 420 | 253 | 40.5% | 29.3% | 16.9% | 8.1% | 5.2% | $100-200 |

## Reading it

The median bin is **$100-200** in every one of the 17 quarters. Over the full window the composition drifts by **$50-100 +4.8pp**, **$100-200 -3.6pp**, **$200-400 -2.5pp**, **$400-800 -0.4pp**, **$800+ +1.6pp**.

That is a mild hollowing of the middle — the two ends thicken slightly while $100-400 thins — and it is not a collapse in what buyers pay. Any claim of a realised-price decline over this window has to survive this table first.

## Two artefacts this series exists to avoid

**1. Sub-$50 orders carried no bucket before ~2024Q2.** Coverage — the share of orders with any price field — runs:

| quarter | coverage | orders with no price |
|---|---:|---:|
| 2022Q1 | 67% | 14,526 |
| 2022Q2 | 61% | 18,810 |
| 2022Q3 | 54% | 23,691 |
| 2022Q4 | 56% | 22,747 |
| 2023Q1 | 55% | 21,829 |
| 2023Q2 | 58% | 17,745 |
| 2023Q3 | 59% | 21,112 |
| 2023Q4 | 62% | 18,799 |
| 2024Q1 | 67% | 12,609 |
| 2024Q2 | 94% | 3,159 |
| 2024Q3 | 100% | 173 |
| 2024Q4 | 100% | 40 |
| 2025Q1 | 100% | 16 |
| 2025Q2 | 100% | 12 |
| 2025Q3 | 100% | 13 |
| 2025Q4 | 100% | 0 |
| 2026Q1 | 100% | 0 |

In 2022Q3 the cheapest bucket that exists at all is `$50-$100` and 46% of orders are unpriced; by 2024Q3 missingness is ~0 and `$0-$50` alone is 50% of orders. The apparent `<$50` share therefore tracks coverage almost exactly (54-67% coverage -> 0-13%; 94% -> 42%; 100% -> ~50%). **Plotting raw bucket shares would report a dramatic collapse in realised value that is entirely a reporting change.**

**2. The bucket labels changed.** `$5-$20` and `$20-$50` disappear and `$0-$50` appears around 2024Q2. Bins built on published labels are not comparable across that break; the boundaries 50/100/200/400/800 are.

Conditioning on $50+ removes both. The cost is that **this series says nothing about the sub-$50 segment**, which is roughly half of all orders and is unmeasurable before 2024.

## Other limits, carried from steps 59 and 63

- A page displays ~4 of ~124 reviews, ranked by `relevancy_score`, so this samples each gig's orders. Step 63A found no **price** selection in that ranking (late minus early +0 USD, CI [+0, +0]).
- The gig set behind each quarter is whatever the archive captured, and it thins sharply after 2024Q3 — n falls from 40,393 ($50+ orders in 2024Q3) to 420 in 2026Q1. Later quarters are noisier, not just smaller.
- **This is not the IPI.** The IPI is a matched-model index on listed basic-package prices; this is a composition series on realised bucketed values over a changing gig set. Do not chain them.
