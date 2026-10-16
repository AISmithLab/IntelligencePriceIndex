# Real price, task value, reputation, and AI exposure

Panel: **167,113 gig-quarter observations**, **15,333 gigs**, 2019Q4–2024Q4, restricted to gigs seen both before and after 2022Q4.
Prices deflated to 2020Q1 dollars with CPI-U (SA, quarterly mean), as `23-real-index.py`. Rows without a rating or review count are dropped (76,565 of 243,678 in-window rows).

| category | gigs | obs | median real price | median reviews |
|---|---:|---:|---:|---:|
| audio | 2,479 | 23,322 | $20.44 | 144 |
| coding | 2,446 | 26,295 | $26.63 | 141 |
| design | 2,718 | 36,623 | $21.67 | 388 |
| marketing | 2,083 | 16,502 | $28.46 | 84 |
| translation | 928 | 7,918 | $4.96 | 207 |
| video | 2,338 | 26,119 | $24.72 | 121 |
| writing | 2,341 | 30,334 | $24.09 | 229 |

## 1. Deflation

Mean ln price falls from **3.2996** nominal to **3.1927** real (-10.1%): that is the general price level over the window, removed before anything else is estimated.

## 2. Reputation (z) and task value (x)

Baseline, no AI term: `ln(real price) ~ gig FE + quarter FE + ln(1+reviews) + rating`. SEs clustered on gig.

| term | coef | se | t | 95% CI | effect |
|---|---:|---:|---:|---|---:|
| ln(1+reviews) | +0.1025 | 0.0040 | +25.85*** | [+0.0947, +0.1102] | +10.79% |
| rating | +0.1004 | 0.0353 | +2.84*** | [+0.0311, +0.1697] | +10.56% |

**Reputation.** A doubling of cumulative reviews carries **+7.36%** in real price. Step 22/27 measured +7.7% on the shipped panels; this is the same treadmill re-estimated on the balanced panel in real terms.

Within-gig R² = 0.1355. Residual SD = 0.3479 log points.

**Task value.** Time-invariant by construction, so it is the gig fixed effect, recovered after fitting as the per-gig intercept — the log real price this particular piece of work commands net of inflation, the common quarter path and reputation. Written to `runs/price-model/task-value.csv`.

| category | n | median x | implied real price | IQR of x |
|---|---:|---:|---:|---:|
| audio | 2,479 | +1.747 | $5.73 | +1.062 … +2.458 |
| coding | 2,446 | +2.127 | $8.39 | +1.248 … +3.057 |
| design | 2,718 | +1.741 | $5.71 | +1.056 … +2.553 |
| marketing | 2,083 | +2.114 | $8.28 | +1.194 … +3.236 |
| translation | 928 | +0.477 | $1.61 | +0.310 … +0.984 |
| video | 2,338 | +1.987 | $7.29 | +1.194 … +2.780 |
| writing | 2,341 | +1.880 | $6.55 | +1.024 … +2.696 |

Task value spans **1.253** log points SD across 15,333 gigs — far more variation than anything time-varying in this model, which is why it belongs in the fixed effect rather than a proxy.

## 3. AI exposure after ChatGPT

**PRIMARY — pre-registered exposure.** Eloundou human-annotated occupation exposure (`exposure_primary`), constant per category, interacted with `Post = 1[quarter >= 2022Q4]`.

| term | coef | se | t | 95% CI | effect |
|---|---:|---:|---:|---|---:|
| Exposure x Post | -0.0199 | 0.0256 | -0.78 | [-0.0700, +0.0303] | -1.97% |
| ln(1+reviews) | +0.1024 | 0.0040 | +25.84*** | [+0.0946, +0.1102] | +10.78% |
| rating | +0.1002 | 0.0353 | +2.84*** | [+0.0310, +0.1695] | +10.54% |

Exposure runs 0.25 (audio) to 0.84 (translation), a spread of 0.59, so the coefficient scales to a **-1.17%** real-price gap between the least and most exposed category after the launch.

## 4. The battery

`29-chained-elasticity-audit.py` found the project's earlier AI result was a spurious regression. Nothing here is reported as a finding until it survives all of this.

**A · Parallel trends (gate).** Exposure interacted with each pre-launch quarter: **FAIL** — 1 of 11 significant. The pre-registration makes this pass/fail, with synthetic control the only authorised fallback.

| pre-period interaction | coef | t |
|---|---:|---:|
| Exp x 2021Q4 | -0.1207 | -1.96 |

**B · Linear-trend horse race.** Adding `Exposure x trend` moves `Exposure x Post` from **-0.0199** (t -0.78) to **+0.0199** (t +0.74). `Exposure x trend` itself is -0.00458 (t -1.23). **FAIL** — the coefficient changes SIGN. Whatever `Exposure x Post` was picking up, a trend explains it better.

**C · Placebo break at 2021Q2** — a false break inside the pre-period (92,082 obs / 15,333 gigs, 2019Q4–2022Q3). The prereg's 2019Q2 sits before this panel opens, which would make `Post` all-ones and the interaction collinear; the pre-period midpoint is used instead. Estimate -0.0518 (t -1.51) — **PASS**.

**D · First differences** (151,780 within-gig changes): +0.0095 (t +0.64) — **does not survive** differencing.

**E · Inference.** Gig-clustered SE **0.0256** against unclustered 0.0125 — clustering inflates it 2.04x. Step 22 shipped the unclustered one; this reports the clustered one.

**F · Power.** MDE at 80% power is **0.0717** log points on the interaction, i.e. **4.34%** across the exposure spread. The point estimate is 0.0199, **BELOW** that. So this null does not rule out an effect up to the MDE — it is a silence, not a zero, and must be reported as one.

## 5. Secondary, exploratory — step 75's market-measured exposure

**Not pre-registered.** Step 75's AI-branded share varies by category AND quarter, so it enters directly and is identified against both fixed effects with no Post interaction. It also ranks the categories nearly opposite to the pre-registration, which is why it cannot be promoted to primary after the fact.

Sample 167,113 obs / 15,333 gigs.

| term | coef | se | t | 95% CI | effect |
|---|---:|---:|---:|---|---:|
| AI share (cat x quarter) | +1.3026 | 0.1155 | +11.27*** | [+1.0761, +1.5290] | +267.87% |
| ln(1+reviews) | +0.1022 | 0.0039 | +25.88*** | [+0.0944, +0.1099] | +10.76% |
| rating | +0.0994 | 0.0353 | +2.81*** | [+0.0302, +0.1685] | +10.45% |

Scaled: a 10pp rise in a category's AI-branded share is associated with **+13.91%** in real price (95% CI +11.36% to +16.52%).

That is a large, tightly-estimated coefficient — which is precisely when step 29's lesson applies hardest. `AI share` varies at the category-by-quarter level, so it will absorb ANY category-specific time path, AI-driven or not. Two tests decide whether it is measuring AI or measuring trend.

**Category-specific linear trends.** Adding one trend per category moves the coefficient from **+1.3026** (t +11.27) to **+0.0901** (t +1.03); the 10pp effect goes from +13.91% to +0.90%. **FAIL** — most of it was a category-specific trend, not AI.

**First differences** (151,780 within-gig changes): +0.1409 (t +1.99) — survives differencing.

