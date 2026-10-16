# Real price, task value, reputation, and AI exposure

**Exploratory run `ext2025`.** Panels: `balanced-prices.csv`, `expanded-prices.csv`, `refresh2025-prices.csv`. Window 2019Q4-2025Q4. The pre-registered estimates live in `model.md`; this is a declared robustness, not a replacement.

Panel: **170,681 gig-quarter observations**, **15,516 gigs**, 2019Q4–2025Q4, restricted to gigs seen both before and after 2022Q4.
Prices deflated to 2020Q1 dollars with CPI-U (SA, quarterly mean), as `23-real-index.py`. Rows without a rating or review count are dropped (79,781 of 250,462 in-window rows).

| category | gigs | obs | median real price | median reviews |
|---|---:|---:|---:|---:|
| audio | 2,492 | 23,503 | $20.44 | 145 |
| coding | 2,471 | 26,810 | $27.25 | 142 |
| design | 2,800 | 38,324 | $21.48 | 391 |
| marketing | 2,113 | 16,869 | $28.61 | 86 |
| translation | 933 | 7,985 | $4.96 | 206 |
| video | 2,355 | 26,459 | $24.72 | 121 |
| writing | 2,352 | 30,731 | $24.09 | 232 |

## 1. Deflation

Mean ln price falls from **3.3038** nominal to **3.1952** real (-10.3%): that is the general price level over the window, removed before anything else is estimated.

## 2. Reputation (z) and task value (x)

Baseline, no AI term: `ln(real price) ~ gig FE + quarter FE + ln(1+reviews) + rating`. SEs clustered on gig.

| term | coef | se | t | 95% CI | effect |
|---|---:|---:|---:|---|---:|
| ln(1+reviews) | +0.0995 | 0.0040 | +25.12*** | [+0.0918, +0.1073] | +10.46% |
| rating | +0.1091 | 0.0331 | +3.30*** | [+0.0442, +0.1739] | +11.52% |

**Reputation.** A doubling of cumulative reviews carries **+7.14%** in real price. Step 22/27 measured +7.7% on the shipped panels; this is the same treadmill re-estimated on the balanced panel in real terms.

Within-gig R² = 0.1351. Residual SD = 0.3501 log points.

**Task value.** Time-invariant by construction, so it is the gig fixed effect, recovered after fitting as the per-gig intercept — the log real price this particular piece of work commands net of inflation, the common quarter path and reputation. Written to `runs/price-model/task-value.csv`.

| category | n | median x | implied real price | IQR of x |
|---|---:|---:|---:|---:|
| audio | 2,492 | +1.712 | $5.54 | +1.032 … +2.424 |
| coding | 2,471 | +2.091 | $8.09 | +1.220 … +3.022 |
| design | 2,800 | +1.699 | $5.47 | +1.023 … +2.506 |
| marketing | 2,113 | +2.071 | $7.93 | +1.157 … +3.195 |
| translation | 933 | +0.444 | $1.56 | +0.280 … +0.955 |
| video | 2,355 | +1.951 | $7.04 | +1.162 … +2.751 |
| writing | 2,352 | +1.847 | $6.34 | +0.995 … +2.661 |

Task value spans **1.252** log points SD across 15,516 gigs — far more variation than anything time-varying in this model, which is why it belongs in the fixed effect rather than a proxy.

## 3. AI exposure after ChatGPT

**PRIMARY — pre-registered exposure.** Eloundou human-annotated occupation exposure (`exposure_primary`), constant per category, interacted with `Post = 1[quarter >= 2022Q4]`.

| term | coef | se | t | 95% CI | effect |
|---|---:|---:|---:|---|---:|
| Exposure x Post | -0.0172 | 0.0257 | -0.67 | [-0.0675, +0.0332] | -1.70% |
| ln(1+reviews) | +0.0995 | 0.0040 | +25.10*** | [+0.0917, +0.1072] | +10.46% |
| rating | +0.1089 | 0.0331 | +3.29*** | [+0.0441, +0.1737] | +11.50% |

Exposure runs 0.25 (audio) to 0.84 (translation), a spread of 0.59, so the coefficient scales to a **-1.01%** real-price gap between the least and most exposed category after the launch.

## 4. The battery

`29-chained-elasticity-audit.py` found the project's earlier AI result was a spurious regression. Nothing here is reported as a finding until it survives all of this.

**A · Parallel trends (gate).** Exposure interacted with each pre-launch quarter: **FAIL** — 2 of 11 significant. The pre-registration makes this pass/fail, with synthetic control the only authorised fallback.

| pre-period interaction | coef | t |
|---|---:|---:|
| Exp x 2021Q3 | -0.1158 | -1.96 |
| Exp x 2021Q4 | -0.1226 | -2.00 |

**B · Linear-trend horse race.** Adding `Exposure x trend` moves `Exposure x Post` from **-0.0172** (t -0.67) to **+0.0157** (t +0.59). `Exposure x trend` itself is -0.00374 (t -1.03). **FAIL** — the coefficient changes SIGN. Whatever `Exposure x Post` was picking up, a trend explains it better.

**C · Placebo break at 2021Q2** — a false break inside the pre-period (92,726 obs / 15,516 gigs, 2019Q4–2022Q3). The prereg's 2019Q2 sits before this panel opens, which would make `Post` all-ones and the interaction collinear; the pre-period midpoint is used instead. Estimate -0.0518 (t -1.51) — **PASS**.

**D · First differences** (155,165 within-gig changes): +0.0101 (t +0.69) — **does not survive** differencing.

**E · Inference.** Gig-clustered SE **0.0257** against unclustered 0.0125 — clustering inflates it 2.05x. Step 22 shipped the unclustered one; this reports the clustered one.

**F · Power.** MDE at 80% power is **0.0720** log points on the interaction, i.e. **4.35%** across the exposure spread. The point estimate is 0.0172, **BELOW** that. So this null does not rule out an effect up to the MDE — it is a silence, not a zero, and must be reported as one.

## 5. Secondary, exploratory — step 75's market-measured exposure

**Not pre-registered.** Step 75's AI-branded share varies by category AND quarter, so it enters directly and is identified against both fixed effects with no Post interaction. It also ranks the categories nearly opposite to the pre-registration, which is why it cannot be promoted to primary after the fact.

Sample 170,675 obs / 15,516 gigs.

| term | coef | se | t | 95% CI | effect |
|---|---:|---:|---:|---|---:|
| AI share (cat x quarter) | +1.2931 | 0.1144 | +11.30*** | [+1.0688, +1.5173] | +264.39% |
| ln(1+reviews) | +0.0993 | 0.0039 | +25.15*** | [+0.0915, +0.1070] | +10.44% |
| rating | +0.1071 | 0.0330 | +3.24*** | [+0.0423, +0.1718] | +11.30% |

Scaled: a 10pp rise in a category's AI-branded share is associated with **+13.80%** in real price (95% CI +11.28% to +16.38%).

That is a large, tightly-estimated coefficient — which is precisely when step 29's lesson applies hardest. `AI share` varies at the category-by-quarter level, so it will absorb ANY category-specific time path, AI-driven or not. Two tests decide whether it is measuring AI or measuring trend.

**Category-specific linear trends.** Adding one trend per category moves the coefficient from **+1.2931** (t +11.30) to **+0.0532** (t +0.60); the 10pp effect goes from +13.80% to +0.53%. **FAIL** — most of it was a category-specific trend, not AI.

**First differences** (155,159 within-gig changes): +0.1462 (t +2.09) — survives differencing.

