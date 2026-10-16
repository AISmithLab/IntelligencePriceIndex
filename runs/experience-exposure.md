# Step 95 — AI exposure × freelancer experience (EXPLORATORY)

169,489 gig-quarters, 15,684 gigs observed both before and after 2022Q4, 33 cells, 2019Q4–2024Q4. Experience = reviews at the gig's last pre-ChatGPT quarter; terciles: **novice ≤ 60**, mid ≤ 269, **veteran > 269** reviews. High/low exposure split at the median cell (0.53).

## E1 · Within-gig real price change, post-ChatGPT mean vs pre mean

| Experience | Low exposure | High exposure | High − low |
|---|---:|---:|---:|
| novice | +19.2% (n 2,653) | +22.8% (n 2,609) | +2.9 log pts |
| mid | +24.7% (n 2,639) | +25.7% (n 2,570) | +0.8 log pts |
| veteran | +18.0% (n 2,870) | +26.4% (n 2,343) | +6.9 log pts |

## E2 · gig + quarter FE

| Term | Exposure | Coef | SE (gig) | t (gig) | wild p (cells) |
|---|---|---:|---:|---:|---:|
| Exp×Post (mid tercile) | human | -0.0328 | 0.0397 | -0.83 | **0.806** |
| Exp×Post×Novice | human | +0.1206 | 0.0591 | +2.04 | **0.340** |
| Exp×Post×Veteran | human | +0.0928 | 0.0552 | +1.68 | **0.447** |
| Post×Novice | human | -0.0747 | 0.0326 | -2.29 | — |
| Post×Veteran | human | -0.1268 | 0.0307 | -4.13 | — |
| Exp×Post (mid tercile) | gpt4 | +0.0918 | 0.0415 | +2.21 | **0.706** |
| Exp×Post×Novice | gpt4 | +0.0595 | 0.0624 | +0.95 | **0.799** |
| Exp×Post×Veteran | gpt4 | +0.0950 | 0.0557 | +1.70 | **0.223** |
| Post×Novice | gpt4 | -0.0481 | 0.0411 | -1.17 | — |
| Post×Veteran | gpt4 | -0.1386 | 0.0372 | -3.73 | — |

## E3 · + reputation control ln(1+reviews)

| Term | Exposure | Coef | SE (gig) | t (gig) | wild p (cells) |
|---|---|---:|---:|---:|---:|
| Exp×Post (mid tercile) | human | -0.0208 | 0.0396 | -0.53 | **0.864** |
| Exp×Post×Novice | human | +0.1200 | 0.0587 | +2.04 | **0.302** |
| Exp×Post×Veteran | human | +0.0839 | 0.0550 | +1.53 | **0.491** |
| Post×Novice | human | -0.0901 | 0.0324 | -2.78 | — |
| Post×Veteran | human | -0.0745 | 0.0307 | -2.43 | — |
| Exp×Post (mid tercile) | gpt4 | +0.0996 | 0.0413 | +2.41 | **0.705** |
| Exp×Post×Novice | gpt4 | +0.0608 | 0.0619 | +0.98 | **0.757** |
| Exp×Post×Veteran | gpt4 | +0.0835 | 0.0556 | +1.50 | **0.304** |
| Post×Novice | gpt4 | -0.0646 | 0.0408 | -1.58 | — |
| Post×Veteran | gpt4 | -0.0834 | 0.0372 | -2.24 | — |

## E4 · + linear trend per experience tercile × cell

| Term | Exposure | Coef | SE (gig) | t (gig) | wild p (cells) |
|---|---|---:|---:|---:|---:|
| Exp×Post (mid tercile) | human | +0.0317 | 0.0410 | +0.77 | **0.570** |
| Exp×Post×Novice | human | +0.0242 | 0.0633 | +0.38 | **0.746** |
| Exp×Post×Veteran | human | -0.0158 | 0.0566 | -0.28 | **0.800** |
| Post×Novice | human | +0.0421 | 0.0350 | +1.20 | — |
| Post×Veteran | human | -0.0074 | 0.0315 | -0.23 | — |
| Exp×Post (mid tercile) | gpt4 | -0.0105 | 0.0416 | -0.25 | **0.885** |
| Exp×Post×Novice | gpt4 | -0.0283 | 0.0629 | -0.45 | **0.782** |
| Exp×Post×Veteran | gpt4 | +0.0837 | 0.0558 | +1.50 | **0.239** |
| Post×Novice | gpt4 | +0.0730 | 0.0421 | +1.73 | — |
| Post×Veteran | gpt4 | -0.0706 | 0.0376 | -1.88 | — |

Reading: `Exp×Post×Novice` < 0 would mean AI exposure lowered novices' prices relative to mid-experience sellers in the same cell; > 0 the reverse. Coefficients are per unit of exposure; the 35 cells span 0.23–0.84 (human).
