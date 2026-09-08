# Real price, task value, reputation, and AI exposure

**Exploratory run `basecheck`.** Panels: `balanced-prices.csv`. Window 2019Q4-2024Q4. The pre-registered estimates live in `model.md`; this is a declared robustness, not a replacement.

Panel: **169,337 gig-quarter observations**, **15,676 gigs**, 2019Q4–2024Q4, restricted to gigs seen both before and after 2022Q4.
Prices deflated to 2020Q1 dollars with CPI-U (SA, quarterly mean), as `23-real-index.py`. Rows without a rating or review count are dropped (79,876 of 249,213 in-window rows).

| category | gigs | obs | median real price | median reviews |
|---|---:|---:|---:|---:|
| audio | 2,235 | 21,452 | $20.99 | 139 |
| coding | 2,446 | 26,295 | $26.63 | 141 |
| design | 2,718 | 36,623 | $21.67 | 388 |
| marketing | 2,033 | 16,156 | $27.25 | 84 |
| translation | 1,598 | 12,590 | $5.05 | 153 |
| video | 2,305 | 25,887 | $24.78 | 121 |
| writing | 2,341 | 30,334 | $24.09 | 229 |

## 1. Deflation

Mean ln price falls from **3.2929** nominal to **3.1858** real (-10.2%): that is the general price level over the window, removed before anything else is estimated.

## 2. Reputation (z) and task value (x)

Baseline, no AI term: `ln(real price) ~ gig FE + quarter FE + ln(1+reviews) + rating`. SEs clustered on gig.

| term | coef | se | t | 95% CI | effect |
|---|---:|---:|---:|---|---:|
| ln(1+reviews) | +0.1021 | 0.0039 | +25.95*** | [+0.0944, +0.1098] | +10.75% |
| rating | +0.0990 | 0.0352 | +2.81*** | [+0.0301, +0.1679] | +10.40% |

**Reputation.** A doubling of cumulative reviews carries **+7.33%** in real price. Step 22/27 measured +7.7% on the shipped panels; this is the same treadmill re-estimated on the balanced panel in real terms.

Within-gig R² = 0.1348. Residual SD = 0.3476 log points.

**Task value.** Time-invariant by construction, so it is the gig fixed effect, recovered after fitting as the per-gig intercept — the log real price this particular piece of work commands net of inflation, the common quarter path and reputation. Written to `runs/price-model/task-value.csv`.

| category | n | median x | implied real price | IQR of x |
|---|---:|---:|---:|---:|
| audio | 2,235 | +1.801 | $6.05 | +1.129 … +2.500 |
| coding | 2,446 | +2.135 | $8.46 | +1.258 … +3.066 |
| design | 2,718 | +1.751 | $5.76 | +1.065 … +2.562 |
| marketing | 2,033 | +2.113 | $8.27 | +1.200 … +3.238 |
| translation | 1,598 | +0.804 | $2.23 | +0.399 … +1.563 |
| video | 2,305 | +1.998 | $7.38 | +1.203 … +2.789 |
| writing | 2,341 | +1.888 | $6.61 | +1.033 … +2.705 |

Task value spans **1.249** log points SD across 15,676 gigs — far more variation than anything time-varying in this model, which is why it belongs in the fixed effect rather than a proxy.

## 3. AI exposure after ChatGPT

**PRIMARY — pre-registered exposure.** Eloundou human-annotated occupation exposure (`exposure_primary`), constant per category, interacted with `Post = 1[quarter >= 2022Q4]`.

| term | coef | se | t | 95% CI | effect |
|---|---:|---:|---:|---|---:|
| Exposure x Post | -0.0333 | 0.0246 | -1.35 | [-0.0814, +0.0149] | -3.27% |
| ln(1+reviews) | +0.1020 | 0.0039 | +25.92*** | [+0.0943, +0.1097] | +10.74% |
| rating | +0.0988 | 0.0351 | +2.81*** | [+0.0300, +0.1677] | +10.39% |

Exposure runs 0.25 (audio) to 0.84 (translation), a spread of 0.59, so the coefficient scales to a **-1.95%** real-price gap between the least and most exposed category after the launch.

## 4. The battery

`29-chained-elasticity-audit.py` found the project's earlier AI result was a spurious regression. Nothing here is reported as a finding until it survives all of this.

**A · Parallel trends (gate).** Exposure interacted with each pre-launch quarter: **FAIL** — 4 of 11 significant. The pre-registration makes this pass/fail, with synthetic control the only authorised fallback.

| pre-period interaction | coef | t |
|---|---:|---:|
| Exp x 2021Q3 | -0.1367 | -2.36 |
| Exp x 2021Q4 | -0.1388 | -2.30 |
| Exp x 2022Q1 | -0.1436 | -2.36 |
| Exp x 2022Q2 | -0.1251 | -2.05 |

**B · Linear-trend horse race.** Adding `Exposure x trend` moves `Exposure x Post` from **-0.0333** (t -1.35) to **+0.0358** (t +1.38). `Exposure x trend` itself is -0.00804 (t -2.24, significant). **FAIL** — the coefficient changes SIGN. Whatever `Exposure x Post` was picking up, a trend explains it better.

**C · Placebo break at 2021Q2** — a false break inside the pre-period (93,247 obs / 15,676 gigs, 2019Q4–2022Q3). The prereg's 2019Q2 sits before this panel opens, which would make `Post` all-ones and the interaction collinear; the pre-period midpoint is used instead. Estimate -0.0595 (t -1.78) — **PASS**.

**D · First differences** (153,661 within-gig changes): +0.0081 (t +0.59) — **does not survive** differencing.

**E · Inference.** Gig-clustered SE **0.0246** against unclustered 0.0121 — clustering inflates it 2.03x. Step 22 shipped the unclustered one; this reports the clustered one.

**F · Power.** MDE at 80% power is **0.0689** log points on the interaction, i.e. **4.16%** across the exposure spread. The point estimate is 0.0333, **BELOW** that. So this null does not rule out an effect up to the MDE — it is a silence, not a zero, and must be reported as one.

## 5. Secondary, exploratory — step 75's market-measured exposure

**Not pre-registered.** Step 75's AI-branded share varies by category AND quarter, so it enters directly and is identified against both fixed effects with no Post interaction. It also ranks the categories nearly opposite to the pre-registration, which is why it cannot be promoted to primary after the fact.

Sample 169,337 obs / 15,676 gigs.

| term | coef | se | t | 95% CI | effect |
|---|---:|---:|---:|---|---:|
| AI share (cat x quarter) | +1.2888 | 0.1148 | +11.23*** | [+1.0639, +1.5138] | +262.86% |
| ln(1+reviews) | +0.1018 | 0.0039 | +25.97*** | [+0.0942, +0.1095] | +10.72% |
| rating | +0.0981 | 0.0351 | +2.79*** | [+0.0292, +0.1669] | +10.30% |

Scaled: a 10pp rise in a category's AI-branded share is associated with **+13.76%** in real price (95% CI +11.23% to +16.34%).

That is a large, tightly-estimated coefficient — which is precisely when step 29's lesson applies hardest. `AI share` varies at the category-by-quarter level, so it will absorb ANY category-specific time path, AI-driven or not. Two tests decide whether it is measuring AI or measuring trend.

**Category-specific linear trends.** Adding one trend per category moves the coefficient from **+1.2888** (t +11.23) to **+0.0727** (t +0.84); the 10pp effect goes from +13.76% to +0.73%. **FAIL** — most of it was a category-specific trend, not AI.

**First differences** (153,661 within-gig changes): +0.1434 (t +2.03) — survives differencing.

