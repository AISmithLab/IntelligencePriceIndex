# Collection headroom in the existing CDX index

Window: 202407 onward. Source: `gig-pages-classified.tsv`

- Rows scanned: 22,739,659
- Status-200 snapshots in window: 1,053,705
- Dropped, skipped category: 290,620
- Dropped, reserved path (/hire/, /agencies/, ...): 13,588
- Distinct gigs in window: 91,849

## Index month coverage (status-200 snapshots)

| month | snapshots |
|---|---:|
| 202407 | 256,471 |
| 202408 | 267,599 |
| 202409 | 280,779 |
| 202410 | 74,426 |
| 202411 | 70,363 |
| 202412 | 36,740 |
| 202501 | 27,616 |
| 202502 | 1,701 |
| 202503 | 2,247 |
| 202504 | 6,292 |
| 202505 | 7,070 |
| 202506 | 543 |
| 202507 | 1,125 |
| 202508 | 6,834 |
| 202509 | 1,553 |
| 202510 | 1,616 |
| 202511 | 2,331 |
| 202512 | 3,888 |
| 202601 | 2,860 |
| 202602 | 1,585 |
| 202603 | 66 |

## Gigs available per selection rule

| category | A_shipped | B_no_survivor | C_any_pair | D_all |
|---|---|---|---|---|
| audio | 55 | 886 | 1,885 | 3,651 |
| coding | 463 | 5,375 | 7,618 | 21,813 |
| design | 1,481 | 7,992 | 10,491 | 29,763 |
| marketing | 295 | 2,197 | 2,982 | 9,241 |
| translation | 28 | 586 | 881 | 2,246 |
| video | 237 | 2,747 | 3,535 | 7,653 |
| writing | 371 | 5,268 | 7,066 | 17,482 |
| **total** | **2,930** | **25,051** | **34,458** | **91,849** |

## Download cost per rule (snapshot-months)

| category | A_shipped | B_no_survivor | C_any_pair | D_all |
|---|---|---|---|---|
| audio | 189 | 2,717 | 5,284 | 7,050 |
| coding | 1,804 | 16,819 | 21,827 | 36,022 |
| design | 5,825 | 26,162 | 31,696 | 50,968 |
| marketing | 1,087 | 6,688 | 8,391 | 14,650 |
| translation | 100 | 1,775 | 2,449 | 3,814 |
| video | 974 | 8,351 | 10,162 | 14,280 |
| writing | 1,445 | 16,679 | 20,787 | 31,203 |
| **total** | **11,424** | **79,191** | **100,596** | **157,987** |

- A_shipped: 11,424 downloads ≈ 16 GB uncompressed, 0.2 h at 20 req/s
- B_no_survivor: 79,191 downloads ≈ 112 GB uncompressed, 1.1 h at 20 req/s
- C_any_pair: 100,596 downloads ≈ 142 GB uncompressed, 1.4 h at 20 req/s
- D_all: 157,987 downloads ≈ 224 GB uncompressed, 2.2 h at 20 req/s
