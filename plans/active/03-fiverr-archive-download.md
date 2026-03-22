# Plan: Fiverr Archive Download

**Status:** active
**Created:** 2026-03-21
**Goal:** Download Fiverr gig-page snapshots from the Wayback Machine for offline price analysis.

## Context

Size estimation (2026-03-21) found ~2.5M unique gig URLs, 4–20 TB raw. Full download is impractical. We use a two-phase approach: first download the CDX index to build a filtered manifest, then download only the HTML pages we need.

## Phase 1: CDX Index Download & Filtering

Build a local manifest of exactly which (URL, timestamp) pairs to download.

### Steps

- [ ] **1.1 Download raw CDX index** — Query CDX API for all `fiverr.com/<letter>*` prefixes (a–z), storing raw CDX records. Fields needed: `urlkey`, `timestamp`, `original`, `statuscode`, `digest`, `length`. Parallelize across letter prefixes.
  - Output: `data/cdx-index/raw/` (one file per letter prefix)
  - Estimated time: 2–4 hours
  - Script: `code/01-download-cdx-index.py`

- [ ] **1.2 Filter to gig pages** — Keep only URLs with exactly 2 path segments (`/<username>/<gig-slug>`), status 200. Exclude known non-gig prefixes (categories, search, support, pro, logo-maker, etc.).
  - Output: `data/cdx-index/gig-pages.tsv`
  - Script: `code/02-filter-gig-pages.py`

- [ ] **1.3 Deduplicate** — For each unique (base_url, timestamp_date) pair, keep only one record (prefer smallest digest if duplicates exist from query-param variants). Also collapse consecutive snapshots with identical content digest.
  - Output: `data/cdx-index/gig-pages-deduped.tsv`

- [ ] **1.4 Classify by category** — Match gig slugs against keyword lists from the taxonomy (`data/task-taxonomy.md`) to assign categories. Tag each row with category.
  - Output: `data/cdx-index/gig-pages-classified.tsv`

- [ ] **1.5 Apply longitudinal filter** — Keep only gigs with ≥ 3 unique snapshots spanning ≥ 2 years. This ensures we have enough temporal data per gig for price trajectory analysis.
  - Output: `data/cdx-index/download-manifest.tsv`

- [ ] **1.6 Generate download stats** — Report: total gigs, total snapshots, by category, by year, estimated download size. Decide whether to download all categories or Tier 1 only.
  - Output: `runs/archive-download/manifest-stats.md`

### Phase 1 Decision Gate

| Manifest size (snapshots) | Estimated download | Action |
|---------------------------|-------------------|--------|
| < 500K | < 100 GB | Download all categories |
| 500K – 2M | 100–400 GB | Download Tier 1 categories (writing, coding, design, translation) |
| > 2M | > 400 GB | Further filter: top-50K gigs by snapshot count, or sample within categories |

## Phase 2: HTML Download

Download the actual archived pages from the Wayback Machine.

### Steps

- [ ] **2.1 Build download script** — Parallel downloader that reads the manifest, constructs Wayback URLs (`https://web.archive.org/web/<timestamp>id_/<original_url>`), downloads HTML, stores locally. Must handle: retries, rate limiting (≤ 15 req/s), resume from interruption, progress logging.
  - Script: `code/03-download-html.py`
  - Storage: `data/fiverr-archive/<username>/<slug>/<timestamp>.html`

- [ ] **2.2 Run download** — Execute in batches. Log progress to `runs/archive-download/download-log.tsv` (timestamp, url, status, file_path, size).
  - Use `id_` flag in Wayback URL to get raw HTML without the Wayback toolbar injection
  - Estimated time: 1–3 days continuous (depending on manifest size and concurrency)

- [ ] **2.3 Verify completeness** — Compare downloaded files against manifest. Report: total expected, total downloaded, missing, failed. Re-download failures.
  - Output: `runs/archive-download/verification.md`

- [ ] **2.4 Log final stats** — Total files, date range, disk usage, category breakdown.
  - Output: `runs/archive-download/final-stats.md`

## Phase 3: Extraction

Parse downloaded HTML into structured data. (Runs after download is complete.)

### Steps

- [ ] **3.1 Build extraction script** — Parse each HTML file using the JSON `packageList` method (primary, 100% success in pilot). Fallback to HTML `<span class="price">` and `og:title`. Extract: seller, gig_slug, title, category, date, price_basic, price_standard, price_premium, rating, review_count.
  - Script: `code/04-extract-prices.py`

- [ ] **3.2 Run extraction** — Process all downloaded HTML files. Log extraction success/failure.
  - Output: `data/fiverr-prices.csv`

- [ ] **3.3 Quality checks** — Validate extracted data: missing fields, outlier prices ($0, $99999), date coverage per gig, category distribution. Generate quality report.
  - Output: `runs/archive-download/extraction-quality.md`

## Technical Notes

- **Wayback URL format**: `https://web.archive.org/web/<timestamp>id_/<original_url>` — the `id_` suffix returns raw HTML without the Wayback toolbar
- **Rate limiting**: Wayback Machine tolerates ~15 req/s for polite crawling. Use exponential backoff on 429/503 errors
- **Storage layout**: `data/fiverr-archive/<username>/<slug>/<YYYYMMDD>.html` — one file per snapshot date
- **Resume support**: Download script must write progress to a checkpoint file so interrupted downloads can resume
- **Disk space**: Ensure ≥ 500 GB free before starting Phase 2. Check with `df -h` before launching

## Decision Log

- 2026-03-21: Size estimation complete. Archive is > 500 GB tier (~2.5M gigs, 4–20 TB raw). Decision: two-phase filtered download.
- 2026-03-22: Detailed download plan created with 3 phases (CDX index, HTML download, extraction).

## Progress

- 2026-03-21: Step 1 (size estimation) complete. Report: `runs/archive-size-estimation/report.md`.
