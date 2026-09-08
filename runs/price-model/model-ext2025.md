# Real price, task value, reputation, and AI exposure

**Exploratory run `ext2025`.** Panels: `balanced-prices.csv`, `expanded-prices.csv`, `refresh2025-prices.csv`. Window 2019Q4-2025Q4. The pre-registered estimates live in `model.md`; this is a declared robustness, not a replacement.

Panel: **172,934 gig-quarter observations**, **15,864 gigs**, 2019Q4–2025Q4, restricted to gigs seen both before and after 2022Q4.
Prices deflated to 2020Q1 dollars with CPI-U (SA, quarterly mean), as `23-real-index.py`. Rows without a rating or review count are dropped (83,091 of 256,025 in-window rows).

| category | gigs | obs | median real price | median reviews |
|---|---:|---:|---:|---:|
| audio | 2,246 | 21,619 | $20.81 | 140 |
| coding | 2,471 | 26,810 | $27.25 | 142 |
| design | 2,800 | 38,324 | $21.48 | 391 |
| marketing | 2,061 | 16,515 | $27.85 | 86 |
| translation | 1,612 | 12,709 | $5.05 | 152 |
| video | 2,322 | 26,226 | $24.78 | 122 |
| writing | 2,352 | 30,731 | $24.09 | 232 |

## 1. Deflation

Mean ln price falls from **3.2971** nominal to **3.1884** real (-10.3%): that is the general price level over the window, removed before anything else is estimated.

## 2. Reputation (z) and task value (x)

Baseline, no AI term: `ln(real price) ~ gig FE + quarter FE + ln(1+reviews) + rating`. SEs clustered on gig.

| term | coef | se | t | 95% CI | effect |
|---|---:|---:|---:|---|---:|
| ln(1+reviews) | +0.0993 | 0.0039 | +25.23*** | [+0.0916, +0.1070] | +10.44% |
| rating | +0.1080 | 0.0329 | +3.28*** | [+0.0435, +0.1726] | +11.41% |

**Reputation.** A doubling of cumulative reviews carries **+7.13%** in real price. Step 22/27 measured +7.7% on the shipped panels; this is the same treadmill re-estimated on the balanced panel in real terms.

Within-gig R² = 0.1343. Residual SD = 0.3498 log points.

**Task value.** Time-invariant by construction, so it is the gig fixed effect, recovered after fitting as the per-gig intercept — the log real price this particular piece of work commands net of inflation, the common quarter path and reputation. Written to `runs/price-model/task-value.csv`.

| category | n | median x | implied real price | IQR of x |
|---|---:|---:|---:|---:|
| audio | 2,246 | +1.758 | $5.80 | +1.095 … +2.466 |
| coding | 2,471 | +2.097 | $8.14 | +1.227 … +3.029 |
| design | 2,800 | +1.706 | $5.51 | +1.030 … +2.512 |
| marketing | 2,061 | +2.073 | $7.95 | +1.160 … +3.193 |
| translation | 1,612 | +0.771 | $2.16 | +0.366 … +1.534 |
| video | 2,322 | +1.962 | $7.11 | +1.169 … +2.758 |
| writing | 2,352 | +1.854 | $6.38 | +1.002 … +2.668 |

Task value spans **1.248** log points SD across 15,864 gigs — far more variation than anything time-varying in this model, which is why it belongs in the fixed effect rather than a proxy.

## 3. AI exposure after ChatGPT

**PRIMARY — pre-registered exposure.** Eloundou human-annotated occupation exposure (`exposure_primary`), constant per category, interacted with `Post = 1[quarter >= 2022Q4]`.

| term | coef | se | t | 95% CI | effect |
|---|---:|---:|---:|---|---:|
| Exposure x Post | -0.0324 | 0.0247 | -1.31 | [-0.0807, +0.0160] | -3.18% |
| ln(1+reviews) | +0.0992 | 0.0039 | +25.20*** | [+0.0915, +0.1069] | +10.43% |
| rating | +0.1078 | 0.0329 | +3.28*** | [+0.0434, +0.1723] | +11.39% |

Exposure runs 0.25 (audio) to 0.84 (translation), a spread of 0.59, so the coefficient scales to a **-1.90%** real-price gap between the least and most exposed category after the launch.

## 4. The battery

`29-chained-elasticity-audit.py` found the project's earlier AI result was a spurious regression. Nothing here is reported as a finding until it survives all of this.

**A · Parallel trends (gate).** Exposure interacted with each pre-launch quarter: **FAIL** — 4 of 11 significant. The pre-registration makes this pass/fail, with synthetic control the only authorised fallback.

| pre-period interaction | coef | t |
|---|---:|---:|
| Exp x 2021Q3 | -0.1455 | -2.51 |
| Exp x 2021Q4 | -0.1445 | -2.40 |
| Exp x 2022Q1 | -0.1510 | -2.48 |
| Exp x 2022Q2 | -0.1326 | -2.17 |

**B · Linear-trend horse race.** Adding `Exposure x trend` moves `Exposure x Post` from **-0.0324** (t -1.31) to **+0.0332** (t +1.29). `Exposure x trend` itself is -0.00753 (t -2.13, significant). **FAIL** — the coefficient changes SIGN. Whatever `Exposure x Post` was picking up, a trend explains it better.

**C · Placebo break at 2021Q2** — a false break inside the pre-period (93,907 obs / 15,864 gigs, 2019Q4–2022Q3). The prereg's 2019Q2 sits before this panel opens, which would make `Post` all-ones and the interaction collinear; the pre-period midpoint is used instead. Estimate -0.0600 (t -1.79) — **PASS**.

**D · First differences** (157,070 within-gig changes): +0.0081 (t +0.59) — **does not survive** differencing.

**E · Inference.** Gig-clustered SE **0.0247** against unclustered 0.0121 — clustering inflates it 2.04x. Step 22 shipped the unclustered one; this reports the clustered one.

**F · Power.** MDE at 80% power is **0.0691** log points on the interaction, i.e. **4.18%** across the exposure spread. The point estimate is 0.0324, **BELOW** that. So this null does not rule out an effect up to the MDE — it is a silence, not a zero, and must be reported as one.

## 5. Secondary, exploratory — step 75's market-measured exposure

**Not pre-registered.** Step 75's AI-branded share varies by category AND quarter, so it enters directly and is identified against both fixed effects with no Post interaction. It also ranks the categories nearly opposite to the pre-registration, which is why it cannot be promoted to primary after the fact.

Sample 172,921 obs / 15,864 gigs.

| term | coef | se | t | 95% CI | effect |
|---|---:|---:|---:|---|---:|
| AI share (cat x quarter) | +1.2810 | 0.1137 | +11.27*** | [+1.0582, +1.5039] | +260.04% |
| ln(1+reviews) | +0.0991 | 0.0039 | +25.27*** | [+0.0914, +0.1068] | +10.41% |
| rating | +0.1062 | 0.0329 | +3.23*** | [+0.0417, +0.1707] | +11.20% |

Scaled: a 10pp rise in a category's AI-branded share is associated with **+13.67%** in real price (95% CI +11.16% to +16.23%).

That is a large, tightly-estimated coefficient — which is precisely when step 29's lesson applies hardest. `AI share` varies at the category-by-quarter level, so it will absorb ANY category-specific time path, AI-driven or not. Two tests decide whether it is measuring AI or measuring trend.

**Category-specific linear trends.** Adding one trend per category moves the coefficient from **+1.2810** (t +11.27) to **+0.0343** (t +0.39); the 10pp effect goes from +13.67% to +0.34%. **FAIL** — most of it was a category-specific trend, not AI.

**First differences** (157,057 within-gig changes): +0.1492 (t +2.14) — survives differencing.

