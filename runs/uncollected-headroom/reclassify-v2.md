# v2 labels: what the re-classification moves

Source: `data/cdx-index/gig-pages-classified.tsv` (22,739,659 rows scanned, status-200 gig URLs only). Distinct gigs: **1,772,000**.

## The defect this found

`04-classify-categories.py` takes the slug from the `original` column with a `"fiverr.com/" in url` test. The index also carries the pre-HTTPS capture form `http://fiverr.com:80/<seller>/<slug>`, which does not contain that substring, so the fallback path splits the whole URL on `/` and returns the empty string between the scheme's two slashes. **Every `:80` snapshot is classified on an empty slug and labelled `uncategorized` regardless of content.**

- Gigs step 04 labelled **inconsistently across their own snapshots** (correct in the https captures, `uncategorized` in the `:80` ones): **26,075**
- Gigs step 04 left `uncategorized` that its own keyword rule labels once the slug is read from `urlkey` instead: **431,196**

This is a labelling defect, not a keyword one -- no new stems are involved in recovering these.

## What each stage contributes (distinct gigs)

| stage | gigs | what it is |
|---|---:|---|
| 1. parse fix | 1,226,319 | step 04's own rule, slug read from `urlkey` |
| 2. new families | 184,722 | taxonomy rows T9/T10/T12 + families never listed |
| 3. leakage stems | 143,507 | step 68's broader stems for the seven collected domains |
| residual | 217,452 | genuine long tail, not projected |

## Distinct gigs per label

| label | v1 (step 04) | v2 | change |
|---|---:|---:|---:|
| **design** | 260,679 | 384,799 | +48% |
| **writing** | 160,360 | 362,215 | +126% |
| **coding** | 152,175 | 243,445 | +60% |
| uncategorized | 976,877 | 217,452 | -78% |
| **marketing** | 78,269 | 145,691 | +86% |
| **video** | 59,354 | 102,744 | +73% |
| social_engagement | 0 | 57,122 | **new** |
| **audio** | 31,487 | 56,991 | +81% |
| photography | 0 | 38,256 | **new** |
| **translation** | 21,775 | 37,391 | +72% |
| data_entry | 24,747 | 29,432 | +19% |
| education_tutoring | 0 | 26,370 | **new** |
| gaming | 0 | 19,580 | **new** |
| lifestyle_control | 0 | 12,625 | **new** |
| ecommerce_ops | 0 | 9,972 | **new** |
| legal | 0 | 9,815 | **new** |
| data_analysis | 6,277 | 7,118 | +13% |
| accounting_consulting | 0 | 6,105 | **new** |
| engineering_cad | 0 | 3,048 | **new** |
| customer_service_va | 0 | 1,829 | **new** |

## Snapshots per label

| label | v1 | v2 |
|---|---:|---:|
| design | 5,657,948 | 6,324,373 |
| writing | 3,291,827 | 3,871,447 |
| coding | 2,219,777 | 2,771,079 |
| uncategorized | 6,734,910 | 2,261,917 |
| video | 1,789,757 | 1,898,691 |
| marketing | 1,033,998 | 1,280,474 |
| audio | 907,479 | 1,206,184 |
| translation | 475,917 | 501,606 |
| photography | 0 | 366,154 |
| gaming | 0 | 358,066 |
| education_tutoring | 0 | 313,303 |
| data_entry | 234,371 | 241,926 |
| social_engagement | 0 | 239,833 |
| legal | 0 | 196,465 |
| ecommerce_ops | 0 | 154,845 |
| lifestyle_control | 0 | 141,378 |
| data_analysis | 131,647 | 133,055 |
| accounting_consulting | 0 | 108,538 |
| engineering_cad | 0 | 72,240 |
| customer_service_va | 0 | 36,057 |

Projection written: `data/cdx-index/gig-month-index-v2.tsv` (20,215,714 rows). Feed it to `41-balanced-manifest.py --projection` to cost a collection.

