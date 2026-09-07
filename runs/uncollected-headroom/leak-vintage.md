# Is step 04's leak correlated with listing vintage or AI vocabulary?

Full population from `data/cdx-index/gig-pages-classified.tsv` (22,739,659 index rows). No crawl. `KEPT` = step 04 assigned the domain; `LEAKED` = step 04 said `uncategorized` and step 68's broader stems say the domain; gigs matching a genuinely new family are excluded.

Vintage = quarter of the gig's EARLIEST capture. `2023Q1+` is the share first seen in 2023Q1 or later — the window step 04's keyword lists predate.

## AI vocabulary in the slug

| domain | kept n | kept AI | leaked n | leaked AI | Fisher p |
|---|---:|---:|---:|---:|---:|
| design | 266,849 | 264 (0.10%) | 31,668 | **242 (0.76%)** | 6.33e-99 |
| coding | 154,034 | 6,179 (4.01%) | 24,087 | **87 (0.36%)** | 2.50e-274 |
| writing | 167,861 | 1,321 (0.79%) | 11,960 | **48 (0.40%)** | 4.79e-07 |
| marketing | 79,934 | 40 (0.05%) | 10,478 | 6 (0.06%) | 6.50e-01 |
| audio | 32,940 | 41 (0.12%) | 8,465 | **105 (1.24%)** | 8.19e-41 |
| video | 62,330 | 137 (0.22%) | 1,662 | 0 (0.00%) | 5.42e-02 |
| translation | 22771 | — | 0 | — | too thin |

## Vintage

| domain | kept median 1st qtr | leaked median 1st qtr | kept 2023Q1+ | leaked 2023Q1+ | Fisher p |
|---|---|---|---:|---:|---:|
| design | 2021Q2 | 2021Q3 | 15.1% | **19.6%** | 3.69e-92 |
| coding | 2021Q4 | 2021Q3 | 23.5% | **18.1%** | 1.31e-80 |
| writing | 2021Q2 | 2021Q2 | 16.7% | 17.1% | 3.62e-01 |
| marketing | 2021Q4 | 2021Q3 | 19.4% | **15.8%** | 8.98e-20 |
| audio | 2021Q2 | 2021Q1 | 13.6% | **15.6%** | 3.05e-06 |
| video | 2021Q2 | 2021Q3 | 17.3% | **14.9%** | 9.30e-03 |
| translation | — | — | — | — | too thin |

## Verdict

- Domains where LEAKED slugs carry AI vocabulary at a different rate (p<0.05): **design, coding, writing, audio**
- Domains where LEAKED gigs are of different vintage (p<0.05): **design, coding, marketing, audio, video**

Read with step 70, which tested the same leak for price bias on the category-blind 500-seller pilot: level differs in design and coding, trend differs nowhere.
