# Headroom in the categories both collections skipped

Source: `data/cdx-index/gig-pages-classified.tsv` (22,739,659 rows scanned)  
Window: 2018Q3-2026Q1 (31 quarters), gig URLs only (`gigfilter.is_gig`)

| category | collected? | in-window snapshots | distinct gigs | gigs >=2 quarters | median matched gigs / adjacent pair | min | max |
|---|---|---:|---:|---:|---:|---:|---:|
| uncategorized | **no** | 5,113,398 | 253,491 | 87,061 | **7,146** | 96 | 14,930 |
| design | yes | 5,479,926 | 249,623 | 83,215 | **6,420** | 171 | 12,271 |
| writing | yes | 3,128,609 | 150,875 | 49,198 | **4,302** | 39 | 7,244 |
| coding | yes | 2,156,407 | 148,212 | 41,724 | **3,000** | 55 | 6,142 |
| video | yes | 1,723,033 | 54,959 | 22,297 | **2,091** | 11 | 4,131 |
| audio | yes | 851,030 | 29,195 | 11,693 | **1,217** | 3 | 2,347 |
| marketing | yes | 996,535 | 76,132 | 19,054 | **1,134** | 29 | 2,725 |
| translation | yes | 439,895 | 19,869 | 7,412 | **715** | 3 | 1,211 |
| data_entry | **no** | 227,155 | 24,255 | 5,880 | **346** | 3 | 777 |
| data_analysis | **no** | 129,166 | 6,132 | 2,373 | **180** | 0 | 490 |

**Skipped-label totals:** 5,469,719 snapshots, 283,878 distinct gigs, 95,314 of them spanning >=2 quarters.

