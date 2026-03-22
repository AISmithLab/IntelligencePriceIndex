# Fiverr Wayback Machine Archive -- Size Estimation Report

**Date:** 2026-03-21
**Method:** CDX API queries + calibrated extrapolation from letter-prefix sampling

## 1. Unique Gig-Page URLs

**Estimated unique gig base URLs: ~2.5 million**

### Methodology

Fiverr gig pages follow the pattern `fiverr.com/<username>/<gig-slug>` (exactly 2 path segments after the domain). We estimated the count through:

1. **CDX page counts per letter prefix (a-z):** Queried `showNumPages=true` for each `fiverr.com/<letter>` prefix match. Total: 9,989 CDX index pages across all letters.

2. **Calibration samples:** For 4 letters (/q, /w, /o, /z), downloaded all unique urlkeys (collapsed by urlkey) to establish a scaling factor:

   | Prefix | CDX pages | Unique urlkeys | urlkeys/page |
   |--------|-----------|----------------|-------------|
   | /q | 26 | 29,722 | 1,143 |
   | /w | 174 | 195,216 | 1,122 |
   | /o | 107 | 125,104 | 1,169 |
   | /z | 96 | 93,684 | 976 |
   | **Average** | | | **1,103** |

3. **Gig-page fraction:** Analyzed URL structure in large samples (500-2000 URLs per letter). Results:

   | Metric | Value |
   |--------|-------|
   | Profile pages (1 path segment) | ~24% |
   | Gig pages (2 path segments) | ~76% |
   | Deep pages (3+ segments) | ~1% |

   However, many gig URLs are duplicates with different query parameters (tracking/referrer params). After deduplication by base path:

   | Prefix | Unique urlkeys | Unique gig base URLs | Gig/urlkey ratio |
   |--------|---------------|---------------------|-----------------|
   | /q | 29,722 | 7,558 | 25.4% |
   | /w | 195,216 | 51,269 | 26.3% |
   | **Average** | | | **25.8%** |

4. **Non-gig path subtraction:** Subtracted CDX pages for known non-gig prefixes (categories: 617, search: 59, gigs: 276, support: 20, pro: 69, logo-maker: 52, etc. -- 1,145 pages total).

5. **Final estimate:**
   - Adjusted letter-prefix pages: 9,989 - 1,145 = 8,844 user-content pages
   - Unique urlkeys: 8,844 x 1,103 = 9,754,932
   - Unique gig base URLs: 9,754,932 x 25.8% = **~2,520,000**

### Per-letter CDX page counts

| Letter | Pages | Letter | Pages | Letter | Pages |
|--------|-------|--------|-------|--------|-------|
| a | 905 | j | 343 | s | 1,402 |
| b | 333 | k | 253 | t | 365 |
| c | 1,114 | l | 339 | u | 586 |
| d | 411 | m | 719 | v | 155 |
| e | 243 | n | 311 | w | 174 |
| f | 243 | o | 107 | x | 27 |
| g | 525 | p | 327 | y | 72 |
| h | 292 | q | 26 | z | 96 |
| i | 210 | r | 411 | | |

Domain total (including subdomains): 39,695 pages.

## 2. Total Snapshots

**Estimated total gig-page snapshots: 7.5M -- 35.5M (depending on counting method)**

### Snapshots per unique gig URL

Sampled snapshot counts for 35 randomly selected gig pages (exact URL match):

| Statistic | Value |
|-----------|-------|
| Median | 2 |
| Mean | 14.1 |
| Min | 1 |
| Max | 246 |
| 25th percentile | 1 |
| 75th percentile | 14 |

The distribution is extremely heavy-tailed: ~50% of gigs have only 1-2 snapshots, while a few popular gigs have 50-250+ snapshots.

### Cross-validation from aggregate data

For the /q prefix (complete data):
- Total CDX records: 150,482
- Unique gig base URLs: 7,558
- Records per unique gig: 19.9 (includes all query-param variants and timestamps)
- Exact-match snapshots per gig: ~15 (excluding query-param variants)

### Deduplication considerations

Many snapshots are near-duplicates:
- Same gig URL with different query parameters (tracking/referrer) returns identical HTML
- Consecutive snapshots of an unchanged page have identical content
- CDX `collapse=digest` can eliminate content-identical snapshots

Estimated unique-content factor: ~50% (after deduplication by content hash).

## 3. Storage Estimates

**Average HTML page size: 590 KB** (from 32 pilot files in `runs/pilot-data-feasibility/`)

| Scenario | Snapshots per gig | Dedup | Total downloads | Raw HTML | Compressed (gzip 3:1) |
|----------|-------------------|-------|-----------------|----------|----------------------|
| LOW (median, exact match) | 3.0 | none | 7.6M | 4.2 TB | 1.4 TB |
| MID (mean, deduplicated) | 14.1 | 50% | 17.8M | 9.8 TB | 3.3 TB |
| HIGH (mean, all variants) | 14.1 | none | 35.5M | 19.5 TB | 6.5 TB |

**Best estimate for practical download: 10-20 TB raw, 3-7 TB compressed.**

This falls in the **> 500 GB** tier from the decision gate.

## 4. Category Breakdown

Analyzed 6,097 unique gig slugs sampled from 8 letter prefixes. Categorized by keyword matching on the gig slug (e.g., "design-a-logo-for-your-business" matches "logo" and "design").

| Category | % of gigs | Est. unique gigs | Est. snapshots (mean) | Est. raw size |
|----------|-----------|-------------------|----------------------|---------------|
| Design (all) | 30.6% | 771K | 10.9M | 6.1 TB |
| Web & Software Dev | 21.8% | 549K | 7.7M | 4.3 TB |
| Writing & Translation | 18.3% | 460K | 6.5M | 3.6 TB |
| Marketing & SEO | 16.5% | 417K | 5.9M | 3.3 TB |
| Video & Animation | 8.4% | 211K | 3.0M | 1.7 TB |
| Voice & Music | 6.0% | 150K | 2.1M | 1.2 TB |
| Data & Admin | 2.6% | 66K | 0.9M | 0.5 TB |
| Uncategorized | 26.5% | 669K | 9.4M | 5.3 TB |

**Note:** Categories overlap (a gig can match multiple categories). The "uncategorized" portion includes gigs with non-standard slug keywords.

### Top keywords in gig slugs

| Keyword | Count (in 6,097 sample) | Keyword | Count |
|---------|------------------------|---------|-------|
| design | 909 | seo | 197 |
| website | 595 | facebook | 195 |
| logo | 378 | app | 188 |
| video | 337 | article | 179 |
| blog | 293 | marketing | 100 |
| wordpress | 235 | data-entry | 87 |

### AI-relevant categories (Tier 1 for IPI project)

For the Intelligence Price Index, the most relevant categories are those where AI capabilities have been advancing:

| Tier 1 Category | Keywords | Est. gigs | Relevance |
|-----------------|----------|-----------|-----------|
| Writing & Content | article, blog, copywriting, seo-writing, content | ~460K | GPT/LLM-exposed |
| Programming & Tech | code, python, javascript, app, website, wordpress | ~549K | Copilot/SWE-bench |
| Design | logo, graphic, illustration, banner | ~771K | DALL-E/Midjourney |
| Translation | translate, interpreter | ~50K | MT systems |

Combined Tier 1: ~1.4M gigs (55% of total), ~5.4 TB raw (MID scenario).

## 5. Filtered Download Estimate

For the IPI project, we likely only need gigs with sufficient longitudinal data:

| Filter | Effect |
|--------|--------|
| Tier 1 categories only | 2.5M -> 1.4M gigs |
| 3+ snapshots (for price trajectory) | 1.4M -> ~420K gigs (est. 30% have 3+) |
| 2+ year span | 420K -> ~210K gigs (est. 50% with multi-year coverage) |

**Filtered download estimate:**
- ~208,000 gig URLs
- ~1.5M downloads (after deduplication)
- **~825 GB raw HTML, ~275 GB compressed**

## 6. Practical Considerations

### Download time
- Wayback Machine rate limit: ~15 requests/second (with polite crawling)
- At 590 KB/page: ~8.6 MB/s
- For 1.5M pages: ~28 hours continuous download

### Two-phase approach recommended
1. **Phase 1: CDX index download** (~hours)
   - Download the full CDX index for `fiverr.com` (all letter prefixes)
   - Filter to gig-page URLs (2 path segments, status 200)
   - Deduplicate by base URL and content digest
   - Apply category + longitudinal filters
   - Output: download manifest (~200K-1.4M URLs with timestamps)

2. **Phase 2: HTML download** (~1-3 days)
   - Parallel curl/wget from Wayback Machine using manifest
   - Store as `data/fiverr-archive/<username>/<slug>/<timestamp>.html`
   - Verify completeness against manifest

### Storage path
- Use `data/fiverr-archive/` within project directory
- Consider external storage if downloading more than the filtered set

## Appendix: Raw CDX API Query Examples

```bash
# Count CDX pages for a prefix
curl "https://web.archive.org/cdx/search/cdx?url=fiverr.com/a&matchType=prefix&showNumPages=true"

# Get unique URLs (collapsed by urlkey)
curl "https://web.archive.org/cdx/search/cdx?url=fiverr.com/a&matchType=prefix&output=text&fl=original&collapse=urlkey&limit=1000"

# Get all snapshots for a specific gig
curl "https://web.archive.org/cdx/search/cdx?url=www.fiverr.com/froggy92/create-amazing-architecture-design-ideas&matchType=exact&output=text"

# Total domain pages
curl "https://web.archive.org/cdx/search/cdx?url=fiverr.com&matchType=domain&showNumPages=true"
# Returns: 39,695
```
