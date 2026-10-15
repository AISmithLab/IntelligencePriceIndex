# Real (CPI-deflated) Fiverr prices

All prices are deflated with **CPI-U, US city average, seasonally adjusted** (BLS
`CPIAUCSL`), averaged to quarters, and expressed in **2020Q1 dollars**:
`real = nominal × CPI(2020Q1) / CPI(t)`. Built by `code/92-export-real-prices.py`; nothing
here is re-estimated, so every number matches the paper.

| File | Rows | Contents |
|---|---:|---|
| `real-indices.csv` | 200 | GEKS-Jevons indices, **composite + 7 categories**, 2020Q1–2026Q1, 2020Q1 = 100 (except translation: 2024Q3–2026Q1 only, 2024Q3 = 100; see Notes). Columns: `quarter, series, index_nominal, index_real, se_log` (bootstrap SE of the log index), `cpi_index` (2020Q1 = 100), `cpi_imputed` (1 = a month of CPI was imputed). Source: `docs/data.json`, the paper's and website's source of truth (§4.2–4.3). |
| `narrow-real-indices.csv` | 700 | The **35 narrow categories**, balanced panel, 2020Q1–2024Q4: `category, quarter, index_nominal, index_real, se_log` (§4.3, Appendix A.10). |
| `gig-quarter-real-prices.csv.gz` | 287,618 | **Gig-level** panel, 39,593 gigs, 2018Q3–2026Q1: `gig_id` (seller/slug), `category`, `quarter`, `price_nominal` (median listed basic-package price in the quarter, USD), `price_real_2020q1`, `cpi` (index level), `reviews` (cumulative at quarter end), `rating`. Built by step 76's `build_panel`: non-gig pages dropped, 0 < price ≤ $10,000. |
| `gig-counts-by-quarter.csv` | 25 | **Gigs collected per quarter**, 2020Q1–2026Q1: `quarter`, `total`, then one column per category. Counted from `gig-quarter-real-prices.csv.gz` (distinct `gig_id` per quarter). Collection is dense through 2024Q4 (9k–13k gigs a quarter) and thin from 2025Q1 (650–2,700). The `translation` column uses the balanced panel's classification, which still over-counts translation (TD6). |
| `cpi-quarterly.csv` | — | The deflator: quarterly CPI-U, SA and NSA. |

## Notes

- **Translation (rebuilt 2026-10-14, TD5).** The translation classifier used to match bare language
  names, so 12 of 26 historical "translation" gigs were voice-overs, legal advice and the like. With
  those removed, the 17 genuine gigs do not link 2021Q4–2022Q2, so translation has no 2020Q1-based
  series: it is blank before 2024Q3 and indexed 2024Q3 = 100. Audio (which received the
  voice-overs) and the composite moved too. Do not compare translation levels with the other series.
- **`translation-other` in `narrow-real-indices.csv` is mostly not translation** (TD6, not yet fixed):
  the balanced panel has the same language-name leak. Treat the three translation narrow cells, and
  `translation-other` especially, with caution.
- **Publication window.** The index is published from 2020Q1; the gig panel reaches back to
  2018Q3, but §3.7 shows the index is not identified before 2020Q1.
- **Collected is not the same as used.** `gig-counts-by-quarter.csv` counts every gig the
  collection priced. The published indices use the subset that can be matched across quarters,
  which is smaller (translation's published index rests on 17 gigs before 2024Q3).
- **The gig panel is broader than any single regression.** The reputation model (§4.4) uses
  169,337 of these rows: 2019Q4–2024Q4, gigs observed both before and after the AI break, with a
  rating and review count.
- **Listed, not realised, prices.** These are asking prices for the basic package. What buyers
  actually paid is a separate series (`data/pilot/realised-value-series.csv`, §4.6) and must not be
  chained onto these.
- Source: archived Fiverr gig pages from the Internet Archive Wayback Machine. Seller usernames
  are public on Fiverr and appear in `gig_id` as they do in the archived URLs.
