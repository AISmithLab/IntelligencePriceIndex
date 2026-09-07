# The 2025-2026 backfill, measured on collected prices

Matched gigs per (category, adjacent quarter pair): a gig counts for a pair only if a basic price extracted in **both** quarters. `before` is the balanced + expanded panels; `after` adds `refresh2025-prices.csv`.

## Inputs

| panel | rows | with a basic price | gigs |
|---|---:|---:|---:|
| before (balanced + expanded) | 375,413 | 375,413 | 55,695 |
| refresh 2025-2026 | 35,924 | 35,924 | 24,345 |

Gigs the refresh adds that the panel did not have: **21,768**. Rows whose gig carried no manifest category: 3,846 before, 331 refresh (counted as `uncategorized`).

## Matched pairs, 2024Q4 onward (target 1,200)

| pair | accounting_consulting | audio | coding | customer_service_va | data_analysis | data_entry | design | ecommerce_ops | education_tutoring | engineering_cad | gaming | legal | lifestyle_control | marketing | photography | social_engagement | translation | uncategorized | video | writing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024Q4->2025Q1 | **0** | **48** | **537** | **0** | **0** | **0** | **1,037** | **0** | **0** | **0** | **0** | **0** | **0** | **272->274** | **0** | **0** | **37** | **163** | **217** | **421** |
| 2025Q1->2025Q2 | **0->1** | **3->4** | **145->165** | **0** | **0** | **0->22** | **301->329** | **0->4** | **0->3** | **0->3** | **0->9** | **0** | **0** | **41->46** | **0->27** | **0->7** | **9** | **447->507** | **50->51** | **97->98** |
| 2025Q2->2025Q3 | **0->1** | **5** | **76->86** | **0->1** | **0->2** | **0->10** | **171->195** | **0->4** | **0->1** | **0->2** | **0->3** | **0->1** | **0->1** | **29->31** | **0->18** | **0->2** | **3** | **334->370** | **28->32** | **50->56** |
| 2025Q3->2025Q4 | **0->2** | **5->10** | **55->73** | **0** | **0->3** | **0->3** | **289->337** | **0->2** | **0->1** | **0->3** | **0->10** | **0->2** | **0->3** | **39->41** | **0->9** | **0->6** | **5** | **255->300** | **11->21** | **39->54** |
| 2025Q4->2026Q1 | **0->1** | **6->8** | **59->70** | **0** | **0->4** | **0->9** | **301->334** | **0->4** | **0** | **0->4** | **0->13** | **0->1** | **0** | **59->61** | **0->8** | **0->9** | **6** | **115->160** | **31->38** | **50->62** |

`+` marks a pair at or above the 1,200 target; bold marks a pair below it.

## Per category, over the reported pairs

| category | before | after | delta | x | pairs improved | pairs at target |
|---|---:|---:|---:|---:|---:|---:|
| accounting_consulting | 0 | 5 | +5 | n/a | 4/5 | 0/5 |
| audio | 67 | 75 | +8 | 1.12x | 3/5 | 0/5 |
| coding | 872 | 931 | +59 | 1.07x | 4/5 | 0/5 |
| customer_service_va | 0 | 1 | +1 | n/a | 1/5 | 0/5 |
| data_analysis | 0 | 9 | +9 | n/a | 3/5 | 0/5 |
| data_entry | 0 | 44 | +44 | n/a | 4/5 | 0/5 |
| design | 2,099 | 2,232 | +133 | 1.06x | 4/5 | 0/5 |
| ecommerce_ops | 0 | 14 | +14 | n/a | 4/5 | 0/5 |
| education_tutoring | 0 | 5 | +5 | n/a | 3/5 | 0/5 |
| engineering_cad | 0 | 12 | +12 | n/a | 4/5 | 0/5 |
| gaming | 0 | 35 | +35 | n/a | 4/5 | 0/5 |
| legal | 0 | 4 | +4 | n/a | 3/5 | 0/5 |
| lifestyle_control | 0 | 4 | +4 | n/a | 2/5 | 0/5 |
| marketing | 440 | 453 | +13 | 1.03x | 5/5 | 0/5 |
| photography | 0 | 62 | +62 | n/a | 4/5 | 0/5 |
| social_engagement | 0 | 24 | +24 | n/a | 4/5 | 0/5 |
| translation | 60 | 60 | +0 | 1.00x | 0/5 | 0/5 |
| uncategorized | 1,314 | 1,500 | +186 | 1.14x | 4/5 | 0/5 |
| video | 337 | 359 | +22 | 1.07x | 4/5 | 0/5 |
| writing | 657 | 691 | +34 | 1.05x | 4/5 | 0/5 |
| **all** | **5,846** | **6,520** | **+674** | **1.12x** | | |

## Why the pairs barely moved: the refresh is one-shot captures

| quarters a gig is priced in | gigs |
|---:|---:|
| 1 | 22,947 |
| 2 | 1,101 |
| 3 | 229 |
| 4 | 46 |
| 5 | 21 |
| 6 | 1 |

**22,947 of 24,345 (94.3%) of the refresh's gigs are captured in exactly one quarter**, and only **884** carry an adjacent pair inside the refresh at all. A gig seen once cannot be differenced at any price.

The manifest holds 24,557 gigs and **893** of them have an adjacent pair, against the 884 recovered. The shortfall is download and extraction loss; the ceiling is the index, not the collection.

## The archive stopped revisiting, and that is the second loss

| year | gigs captured | with an adjacent-quarter pair | share |
|---|---:|---:|---:|
| 2010 | 14 | 11 | 78.6% |
| 2011 | 219 | 35 | 16.0% |
| 2012 | 695 | 336 | 48.3% |
| 2013 | 6,389 | 5,448 | 85.3% |
| 2014 | 7,047 | 5,692 | 80.8% |
| 2015 | 6,143 | 1,699 | 27.7% |
| 2016 | 9,231 | 4,800 | 52.0% |
| 2017 | 3,866 | 2,350 | 60.8% |
| 2018 | 15,276 | 11,323 | 74.1% |
| 2019 | 50,507 | 41,212 | 81.6% |
| 2020 | 87,884 | 70,461 | 80.2% |
| 2021 | 108,706 | 82,387 | 75.8% |
| 2022 | 100,068 | 76,501 | 76.4% |
| 2023 | 57,931 | 43,665 | 75.4% |
| 2024 | 60,009 | 44,557 | 74.3% |
| 2025 | 8,132 | 3,583 | 44.1% |
| 2026 | 1,482 | 512 | 34.5% |

The revisit rate is flat at 74-82% for 2018-2024 and then breaks. Matched-model supply is the product of the two columns, so the right edge loses twice over: fewer gigs, each less likely to be seen again.

## Where each category's series can still be differenced

A pair with zero matched gigs is not thin, it is unidentified. Last pair with any matched gig, and with at least 30:

| category | last pair >0 (before -> after) | last pair >=30 (before -> after) |
|---|---|---|
| accounting_consulting | none -> 2025Q4->2026Q1 | none -> none |
| audio | 2025Q4->2026Q1 -> 2025Q4->2026Q1 | 2024Q4->2025Q1 -> 2024Q4->2025Q1 |
| coding | 2025Q4->2026Q1 -> 2025Q4->2026Q1 | 2025Q4->2026Q1 -> 2025Q4->2026Q1 |
| customer_service_va | none -> 2025Q2->2025Q3 | none -> none |
| data_analysis | none -> 2025Q4->2026Q1 | none -> none |
| data_entry | none -> 2025Q4->2026Q1 | none -> none |
| design | 2025Q4->2026Q1 -> 2025Q4->2026Q1 | 2025Q4->2026Q1 -> 2025Q4->2026Q1 |
| ecommerce_ops | none -> 2025Q4->2026Q1 | none -> none |
| education_tutoring | none -> 2025Q3->2025Q4 | none -> none |
| engineering_cad | none -> 2025Q4->2026Q1 | none -> none |
| gaming | none -> 2025Q4->2026Q1 | none -> none |
| legal | none -> 2025Q4->2026Q1 | none -> none |
| lifestyle_control | none -> 2025Q3->2025Q4 | none -> none |
| marketing | 2025Q4->2026Q1 -> 2025Q4->2026Q1 | 2025Q4->2026Q1 -> 2025Q4->2026Q1 |
| photography | none -> 2025Q4->2026Q1 | none -> none |
| social_engagement | none -> 2025Q4->2026Q1 | none -> none |
| translation | 2025Q4->2026Q1 -> 2025Q4->2026Q1 | 2024Q4->2025Q1 -> 2024Q4->2025Q1 |
| uncategorized | 2025Q4->2026Q1 -> 2025Q4->2026Q1 | 2025Q4->2026Q1 -> 2025Q4->2026Q1 |
| video | 2025Q4->2026Q1 -> 2025Q4->2026Q1 | 2025Q4->2026Q1 -> 2025Q4->2026Q1 |
| writing | 2025Q4->2026Q1 -> 2025Q4->2026Q1 | 2025Q4->2026Q1 -> 2025Q4->2026Q1 |
