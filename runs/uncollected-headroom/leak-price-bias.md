# Does step 04's leak bias price? Measured on the category-blind pilot

Corpus: `data/pilot/pilot-prices.csv` — the 500-seller pilot, the only collection sampled by SELLER rather than by step-04 label, so it is the only one that contains leaked gigs at all. No crawl.

`KEPT` = step 04 assigned the domain. `LEAKED` = step 04 said `uncategorized`, step 68's broader stems say the domain. Gigs matching a genuinely new family (photography, gaming, legal, …) are excluded, not counted as leaks.

## Price level (median of each gig's median log price)

| domain | kept n | leaked n | kept median $ | leaked median $ | log gap | Mann-Whitney p |
|---|---:|---:|---:|---:|---:|---:|
| design | 524 | 29 | 15.00 | 35.00 | **+0.847** | 0.007 |
| coding | 177 | 50 | 25.00 | 15.00 | **-0.511** | 0.037 |
| writing | 235 | 32 | 10.00 | 15.00 | +0.405 | 0.133 |
| marketing | 102 | 11 | 25.72 | 10.00 | -0.945 | 0.156 |
| audio | 86 | 25 | 25.00 | 15.00 | -0.511 | 0.054 |
| video | 130 | 3 | — | — | — | too thin |
| translation | 44 | 0 | — | — | — | too thin |

## Price trend (within-gig log change, first to last observed quarter)

| domain | kept n | leaked n | kept mean Δlog | leaked mean Δlog | difference | t-test p |
|---|---:|---:|---:|---:|---:|---:|
| design | 350 | 18 | +0.383 | +0.440 | +0.056 | 0.734 |
| coding | 120 | 33 | +0.501 | +0.485 | -0.016 | 0.924 |
| writing | 154 | 25 | +0.403 | +0.146 | -0.257 | 0.138 |
| marketing | 57 | 7 | +0.259 | +0.138 | -0.121 | 0.326 |
| audio | 61 | 17 | +0.719 | +0.504 | -0.215 | 0.279 |
| video | 94 | 2 | — | — | — | too thin |
| translation | 28 | 0 | — | — | — | too thin |

## AI vocabulary in slug or title

This is the mechanism to rule out: if leaked listings are more AI-era than kept ones, the miss correlates with the treatment.

| domain | kept AI share | leaked AI share | Fisher p |
|---|---:|---:|---:|
| design | 2/524 (0.4%) | 0/29 (0.0%) | 1.000 |
| coding | 5/177 (2.8%) | 0/50 (0.0%) | 0.589 |
| writing | 2/235 (0.9%) | 0/32 (0.0%) | 1.000 |
| marketing | 0/102 (0.0%) | 0/11 (0.0%) | 1.000 |
| audio | 0/86 (0.0%) | 0/25 (0.0%) | 1.000 |
| video | — | — | too thin |
| translation | — | — | too thin |

## Verdict

- Domains where LEAKED price **level** differs from KEPT at p<0.05: **design, coding**
- Domains where LEAKED price **trend** differs at p<0.05: **none**
- Domains where LEAKED **AI-vocabulary rate** differs at p<0.05: **none**

Power caveat: the pilot is 500 sellers, so per-domain leaked cells are tens of gigs, not thousands. A null here bounds the bias loosely — it does not prove the leak is innocuous at the scale of the 88,320-gig population.
