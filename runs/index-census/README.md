# What the harvested CDX index actually holds

**Measured:** 2026-08-12. Replaces the 2026-03-21 *estimate* in
`runs/archive-size-estimation/report.md` for the quantities below. Both are now
reported in §3.1 of `drafts/sections/method.md`, because only the estimate existed
when the two-phase collection design was decided.

## Figures

| quantity | value | file |
|---|---:|---|
| Raw CDX records harvested (`fiverr.com/a*`…`z*`, all statuses and path shapes) | 59,994,121 | `data/cdx-index/raw/download-summary.txt` |
| Status-200 captures of gig-shaped URLs (2 path segments) | 23,269,218 | `gig-pages.tsv` |
| After collapsing (URL, day) + identical content digest | 22,739,659 | `gig-pages-deduped.tsv` |
| Distinct urlkeys (query-param variants counted separately) | 5,587,932 | `gig-pages-deduped.tsv` |
| **Distinct gig base URLs** (query strings stripped) | **1,778,505** | `gig-pages-deduped.tsv` |
| Rows carrying a query string | 4,201,200 | `gig-pages-deduped.tsv` |
| Sum of CDX `length` — compressed WARC record bytes, deduped | 2.474 TB | `gig-pages-deduped.tsv` |
| Same, pre-dedup | 2.535 TB | `gig-pages.tsv` |

Raw HTML implied by the 2.474 TB at the 5.0× gzip ratio measured on this corpus:
**≈12 TB**.

## Estimate vs measurement

The 2026-03-21 report projected ~2,520,000 unique gig base URLs and 4.2–19.5 TB raw
("best estimate 10–20 TB"). Measured, it is **1,778,505 URLs** — the estimate was
1.4× high — and the volume call was right.

The two are not perfectly like-for-like: the measurement counts only URLs with at
least one status-200 capture surviving the two-segment filter in the letter-prefix
harvest, while the estimate counted gig URLs present in the index at all.

**The urlkey/base-URL gap is the thing to watch.** CDX urlkeys retain query strings,
so 5.59M urlkeys collapse to 1.78M distinct gigs — a 3.1× factor. Any count taken off
field 1 without stripping `?…` overstates gigs by roughly that much.

## Commands

`gig-pages-deduped.tsv` is sorted by urlkey, but stripping the query string breaks
that ordering (`/a/b-c` sorts between `/a/b` and `/a/b?x`), so the distinct base-URL
count needs a hash set rather than `uniq`.

```bash
# rows, distinct urlkeys, archived bytes
awk -F'\t' 'NR>1{n++; s+=($6+0); if($1!=p){u++;p=$1}}
  END{printf "rows=%d distinct_urlkeys=%d sum_length_bytes=%.0f\n", n,u,s}' \
  data/cdx-index/gig-pages-deduped.tsv

# distinct gig base URLs
awk -F'\t' 'NR>1{k=$1; if(index(k,"?")){q++; sub(/\?.*/,"",k)}
  if(!(k in a)){a[k]=1;n++}}
  END{printf "distinct_base_gig_urls=%d rows_with_query=%d\n", n, q}' \
  data/cdx-index/gig-pages-deduped.tsv
```

## Caveat

The two-segment filter in `code/02-filter-gig-pages.py` predates
`code/gigfilter.py`'s 27-entry `RESERVED` set, so the 1.78M includes a small number of
non-gig section pages of the Stage 5b families (13,588 such snapshots were dropped in
the recent-window census alone). The figure is an upper bound on distinct gigs.
