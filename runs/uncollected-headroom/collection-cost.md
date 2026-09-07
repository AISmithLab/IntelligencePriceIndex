# What a candidate collection costs

Constants measured on the two completed crawls, not estimated: **98.0%** of manifest rows return a page, **7.83 rows/s** end-to-end (set by `08-download-html.py --max-rate 10`, so it does not improve with concurrency), **128 KB/page** gzipped.

Disk free: **53 GB**. Pages already on disk: `html-balanced` 293,943, `html-recent` 82,967, `html` 22,632 (386,440 distinct).

`to fetch` counts only rows with no matching `<seller>/<date>_<slug>` file in any of those trees -- what the crawl would actually request. Disk and wall-clock are quoted on that, not on the row count.

| manifest | rows | to fetch | gigs | new gigs | disk (gz) | wall-clock | fits? |
|---|---:|---:|---:|---:|---:|---:|---|
| `leakfix-manifest-1200.tsv` | 303,147 | **33,187** | 39,445 | 5,502 | 4.2 GB | 1h11m | yes |

**`leakfix-manifest-1200.tsv` by label** (rows / of those, still to fetch)

| label | rows | to fetch | disk (gz) | wall-clock |
|---|---:|---:|---:|---:|
| design | 53,700 | 4,089 | 0.5 GB | 0h09m |
| coding | 47,278 | 9,140 | 1.1 GB | 0h19m |
| writing | 46,582 | 3,486 | 0.4 GB | 0h07m |
| video | 44,017 | 1,123 | 0.1 GB | 0h02m |
| marketing | 41,611 | 5,883 | 0.7 GB | 0h13m |
| audio | 40,429 | 9,227 | 1.2 GB | 0h20m |
| translation | 29,530 | 239 | 0.0 GB | 0h01m |

| `newfam-manifest-1200.tsv` | 103,131 | **102,677** | 26,285 | 26,210 | 12.9 GB | 3h39m | yes |

**`newfam-manifest-1200.tsv` by label** (rows / of those, still to fetch)

| label | rows | to fetch | disk (gz) | wall-clock |
|---|---:|---:|---:|---:|
| photography | 20,041 | 19,966 | 2.5 GB | 0h42m |
| gaming | 19,654 | 19,568 | 2.5 GB | 0h42m |
| education_tutoring | 15,392 | 15,339 | 1.9 GB | 0h33m |
| legal | 10,257 | 10,113 | 1.3 GB | 0h22m |
| ecommerce_ops | 8,963 | 8,935 | 1.1 GB | 0h19m |
| social_engagement | 8,321 | 8,293 | 1.0 GB | 0h18m |
| lifestyle_control | 7,628 | 7,610 | 1.0 GB | 0h16m |
| accounting_consulting | 6,769 | 6,749 | 0.8 GB | 0h14m |
| engineering_cad | 3,493 | 3,491 | 0.4 GB | 0h07m |
| customer_service_va | 2,613 | 2,613 | 0.3 GB | 0h06m |

