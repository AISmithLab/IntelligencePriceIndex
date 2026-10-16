# Real (CPI-deflated) Fiverr prices

All prices are deflated with **CPI-U, US city average, seasonally adjusted** (BLS
`CPIAUCSL`), averaged to quarters, and expressed in **2020Q1 dollars**:
`real = nominal × CPI(2020Q1) / CPI(t)`. Built by `code/92-export-real-prices.py`; nothing
here is re-estimated, so every number matches the paper — except `balanced-composite.csv`, which is new (see Notes).

| File | Rows | Contents |
|---|---:|---|
| `real-indices.csv` | 200 | GEKS-Jevons indices, **composite + 7 categories**, 2020Q1–2026Q1, 2020Q1 = 100 (except translation: 2024Q3–2026Q1 only, 2024Q3 = 100; see Notes). Columns: `quarter, series, index_nominal, index_real, se_log` (bootstrap SE of the log index), `cpi_index` (2020Q1 = 100), `cpi_imputed` (1 = a month of CPI was imputed). Source: `docs/data.json`, the paper's and website's source of truth (§4.2–4.3). |
| `narrow-real-indices.csv` | 680 | The **34 narrow categories**, balanced panel, 2020Q1–2024Q4: `category, quarter, index_nominal, index_real, se_log` (§4.3, Appendix A.10). |
| `gig-quarter-real-prices.csv.gz` | 281,844 | **Gig-level** panel, 38,085 gigs, 2018Q3–2026Q1: `gig_id` (seller/slug), `category`, `quarter`, `price_nominal` (median listed basic-package price in the quarter, USD), `price_real_2020q1`, `cpi` (index level), `reviews` (cumulative at quarter end), `rating`. Built by step 76's `build_panel`: non-gig pages dropped, 0 < price ≤ $10,000. |
| `gig-counts-by-quarter.csv` | 25 | **Gigs collected per quarter**, 2020Q1–2026Q1: `quarter`, `total`, then one column per category. Counted from `gig-quarter-real-prices.csv.gz` (distinct `gig_id` per quarter). Collection is dense through 2024Q4 (9k–13k gigs a quarter) and thin from 2025Q1 (650–2,700). Categories are the balanced panel's, after the TD6 translation fix (2026-10-16). |
| `cpi-quarterly.csv` | — | The deflator: quarterly CPI-U, SA and NSA. |
| `balanced-composite.csv` | 60 | **Balanced-panel composite**, 2020Q1–2024Q4, 2020Q1 = 100, under three fixed weightings (`weights` = `sales` (primary), `equal`, `gigs`). Columns: `weights, quarter, index_nominal, index_real, se_log, half_width_pct` (1.96 × se_log, in %), `real_lo, real_hi` (95% band on the real level), `meets_5pct` (half-width ≤ 5%; blank at the base). Built by `code/99-balanced-composite.py`. **Not a paper figure** (see Notes). |

## Notes

- **Balanced-panel composite (added 2026-10-16, not in the paper).** Unlike the other files, `balanced-composite.csv` is a new estimate, not a paper figure, and it uses none of the headline index's inputs. It is a fixed-weight geometric mean of seven category GEKS-Jevons indices (`code/98-broad-trajectories.py`) estimated on the balanced panel: 34,967 gigs, 231,757 gig-quarters. Primary weights are a sales proxy (each gig's median price × reviews gained 2020Q1–2024Q4): design 0.290, coding 0.194, writing 0.165, video 0.120, marketing 0.115, audio 0.106, translation 0.011. The band is 1.96 × sqrt(Σ w² se²), from a gig-level bootstrap with the weights held fixed, so it is likely too narrow. Sales-weighted 2024Q4: +65.5% real [+62.0, +69.1]. **Do not compare its level with `real-indices.csv`'s composite**: the gigs, the weights and the end quarter all differ (§3.7).
- **Translation (rebuilt 2026-10-14, TD5).** The translation classifier used to match bare language
  names, so 12 of 26 historical "translation" gigs were voice-overs, legal advice and the like. With
  those removed, the 17 genuine gigs do not link 2021Q4–2022Q2, so translation has no 2020Q1-based
  series: it is blank before 2024Q3 and indexed 2024Q3 = 100. Audio (which received the
  voice-overs) and the composite moved too. Do not compare translation levels with the other series.
- **Balanced-panel translation (rebuilt 2026-10-16, TD6).** The balanced panel had the same
  language-name leak: 6,368 "translation" gigs, of which only 3,684 are translation, subtitling or
  transcription. The rest moved to audio (voice-overs), video, marketing, or out of the seven
  categories. `translation-other` is gone (every remaining translation gig is in `translation-translation`
  or `translation-subtitle`), so there are now 34 narrow cells, and the gig panel and per-quarter
  counts are smaller (translation roughly 300–770 fewer gigs a quarter through 2024).
- **Publication window.** The index is published from 2020Q1; the gig panel reaches back to
  2018Q3, but §3.7 shows the index is not identified before 2020Q1.
- **Collected is not the same as used.** `gig-counts-by-quarter.csv` counts every gig the
  collection priced. The published indices use the subset that can be matched across quarters,
  which is smaller (translation's published index rests on 17 gigs before 2024Q3).
- **The gig panel is broader than any single regression.** The reputation model (§4.4) uses
  167,113 of these rows: 2019Q4–2024Q4, gigs observed both before and after the AI break, with a
  rating and review count.
- **Listed, not realised, prices.** These are asking prices for the basic package. What buyers
  actually paid is a separate series (`data/pilot/realised-value-series.csv`, §4.6) and must not be
  chained onto these.
- Source: archived Fiverr gig pages from the Internet Archive Wayback Machine. Seller usernames
  are public on Fiverr and appear in `gig_id` as they do in the archived URLs.
