# Download Manifest Statistics

**Generated:** 2026-03-22
**Input:** `data/cdx-index/download-manifest.tsv`

## Summary

| Metric | Value |
|--------|-------|
| Total gig URLs | 117,871 |
| Total snapshots | 9,422,324 |
| Avg snapshots/gig | 79.9 |
| Estimated download size | 5302 GB (raw HTML) |
| Estimated compressed | 1767 GB (gzip ~3:1) |

## Decision Gate

| Gate | Action |
|------|--------|
| > 2M snapshots | **Further filter: top-50K gigs by snapshot count, or sample within categories** |

## By Category

| Category | Gigs | Snapshots | % of total | Est. size (GB) |
|----------|------|-----------|-----------|----------------|
| design | 25,110 | 2,588,269 | 27.5% | 1456 |
| uncategorized | 48,348 | 2,389,569 | 25.4% | 1345 |
| writing | 14,866 | 1,452,858 | 15.4% | 817 |
| video | 7,411 | 934,379 | 9.9% | 526 |
| coding | 8,937 | 811,210 | 8.6% | 456 |
| audio | 4,512 | 498,997 | 5.3% | 281 |
| marketing | 4,019 | 381,115 | 4.0% | 214 |
| translation | 2,884 | 234,774 | 2.5% | 132 |
| data_entry | 1,211 | 73,697 | 0.8% | 41 |
| data_analysis | 573 | 57,456 | 0.6% | 32 |

**Tier 1 subtotal:** 51,797 gigs, 5,087,111 snapshots, ~2862 GB

## By Year

| Year | Gigs active | Snapshots | % of total |
|------|------------|-----------|-----------|
| 2010 | 1 | 1 | 0.0% |
| 2011 | 5,740 | 16,199 | 0.2% |
| 2012 | 9,676 | 17,666 | 0.2% |
| 2013 | 13,694 | 48,770 | 0.5% |
| 2014 | 15,105 | 50,864 | 0.5% |
| 2015 | 11,129 | 46,769 | 0.5% |
| 2016 | 8,972 | 49,635 | 0.5% |
| 2017 | 1,703 | 8,106 | 0.1% |
| 2018 | 10,051 | 115,490 | 1.2% |
| 2019 | 27,594 | 446,009 | 4.7% |
| 2020 | 48,057 | 2,017,003 | 21.4% |
| 2021 | 54,574 | 1,780,294 | 18.9% |
| 2022 | 57,336 | 1,970,374 | 20.9% |
| 2023 | 40,462 | 1,871,057 | 19.9% |
| 2024 | 36,079 | 979,102 | 10.4% |
| 2025 | 2,289 | 4,279 | 0.0% |
| 2026 | 579 | 706 | 0.0% |

## Recommendations

Based on the decision gate (> 2M snapshots):
- **Recommended action:** Further filter: top-50K gigs by snapshot count, or sample within categories
- Tier 1 categories alone: 5,087,111 snapshots (~2862 GB)
