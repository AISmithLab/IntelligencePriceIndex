# Plan: Expanded recent-window collection (rule B)

**Status:** active
**Created:** 2026-08-09
**Goal:** Take the recent panel from 2,930 gigs to ~25,051 by dropping the survivor filter, using headroom that already exists in the March CDX index.

## Scope

**Covers:** re-selecting the recent-window manifest without the trailing-window
survival requirement, downloading the additional pages, and the storage/status
apparatus that makes the larger collection affordable and auditable.

**Does not cover:** rebuilding the index off the new panel (steps 19 → 21 → 23 →
18), refreshing `docs/data.json`, or any change to the paper. The pilot paper's
numbers are frozen (`data/pilot/paper-numbers.md`) and this collection is
**paper 2's** frame, per the 2026-08-05 decision. Nothing here touches the
submission draft.

## The finding that drove the design

The binding constraint was never the archive — it was the selection rule.
`runs/collection-headroom/census.md`: the existing index holds **91,849 distinct
gigs** in the 2024Q3+ window and the shipped panel uses **2,930 of them (3.2%)**.

| rule | criterion | gigs | snapshot-months |
|---|---|---:|---:|
| A shipped | ≥2 quarters AND ≥1 snapshot in 2025Q3–2026Q2 | 2,930 | 11,424 |
| **B no-survivor** | **≥2 quarters anywhere in window** | **25,051** | **79,191** |
| C any-pair | ≥2 distinct months | 34,458 | 100,596 |
| D all | any capture | 91,849 | 157,987 |

Rule A reproduces the production panel exactly (2,930 post-`gigfilter`), which is
what validates the census.

## Steps

- [x] Census the headroom in the existing index — `code/37-collection-headroom.py`
- [x] Probe whether a fresh CDX crawl would add a trailing edge — **it would not** (below)
- [x] Build the rule-B manifest — `code/38-expanded-manifest.py` → `data/pilot/expanded-manifest.tsv` (79,191 rows)
- [x] Build the full-status ledger from the raw CDX — `code/39-status-ledger.py`
- [x] Add gzip storage to `08-download-html.py` and gzip reading to `09-extract-prices.py`
- [x] Pilot 500 pages and measure — 440 ok, **0 failures, 0 retries, 5.71 pages/s**
- [x] Full download — **DONE 2026-08-10.** **67,377 newly captured** of 79,191 manifest rows
      (178 replay 404s, 27 hard failures, 6 403s); the balance were already on disk from the
      original recent crawl and were not re-fetched.
- [x] Re-extract prices over the combined corpus — **DONE 2026-08-10**, to
      `data/pilot/expanded-prices.csv` (**not** over `recent-prices.csv`, which is untouched).
      82,967 files (67,377 new + 15,150 original + 440 pilot) → **82,966 rows, 1
      `no_price_found`**.
- [ ] Re-measure matched gigs per bilateral per category against the ±5% requirement ← here
- [ ] Decide whether the enlarged panel changes the recent index enough to warrant rebuilding 19 → 21 → 23 → 18

## Decision Log

- **2026-08-09: rule B, not C or D.** C adds 9,407 gigs seen in ≥2 months but
  only one quarter, which contribute nothing to a *quarterly* matched-model
  index; D adds singletons, which cannot yield a price relative at all. B is
  also the rule `plans/todo.md` asks for on independent grounds — it is the one
  that removes the survivor selection.
- **2026-08-09: do not re-crawl the CDX index.** Direct probes of the Wayback
  CDX for 2026Q2–Q3 return almost exclusively **403** on Fiverr gig URLs (prefix
  `ba`, 2026Q2: 21 captures, **zero status-200**). Our own index shows the same
  collapse from the other side — 280,779 status-200 snapshots in 202409 against
  **66** in 202603. The trailing edge is not recoverable by re-harvesting; the
  data that exists is already on disk. This retires the assumption that the
  index was stale because it was harvested in March.
- **2026-08-09: store gzipped.** Measured **5.0×** on this corpus. Rule B plain
  would be ~93 GB against 115 GB free; gzipped it is ~17.6 GB. `08` writes
  `.html.gz` under `--gzip` and reuses plain files already on disk, so the
  15,150 existing pages are not re-fetched; `09` reads both forms transparently.
- **2026-08-09: 10 concurrent / 10 req/s, not the previous run's 20/20.** The
  June–July run logged **12,336 failures against 15,150 successes (45%)**. The
  pilot at 10/10 had **zero**. Sustained throughput is 5.71 pages/s either way,
  so the gentler setting is strictly better here.

## Progress

- **2026-08-09:** apparatus built and validated; full download launched.
  Extraction smoke-tested over the combined corpus — 15,590 files (15,150 plain
  + 440 gzipped), **100% success, 0 errors**, and the gzip-derived rows carry
  clean `seller`/`slug`/`date` fields (the `.html.gz` double suffix would
  otherwise have left `.html` inside the slug; handled explicitly).

## Open issue this collection does NOT fix

**Exit remains unmeasurable, and now that is a measured fact rather than a
suspicion.** `plans/todo.md` asks that the full-scale crawl "record the 404s" so
takedown can be told apart from non-archival. `code/39-status-ledger.py` streams
all 60M raw CDX rows and tallies every status class for the 25,051 selected
gigs. Across **509,339 in-window captures: `n_404 = 0`**, with 1,155 403s, 1,588
3xx and 1,662 5xx. The archive stops re-requesting a delisted URL rather than
recording its death, so no amount of additional archive collection can produce
an exit hazard. **That requirement can only be met by a live forward crawl on a
fixed schedule**, and it should be specified as such rather than as a property of
the Wayback pipeline.
