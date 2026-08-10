# Template: data collection campaign

**How to use:** copy to `plans/active/<name>.md`, delete this header block, fill the
`<>` placeholders, and delete any section that genuinely does not apply — but delete
it explicitly rather than leaving it blank, so a reader can tell "not applicable"
from "not yet done".

**When to use:** any collection that fetches a new corpus or re-selects an existing
manifest. Not needed for re-running an existing pipeline unchanged.

**Where it came from:** the shape below is what the recent, rule-B expanded, and
link-balanced historical campaigns independently converged on. The ordering is not
cosmetic — three of the four decisions that changed a campaign's design came from
steps 1, 3 and 4, and each would have been discovered *after* the crawl if those
steps had come later. Worked examples: `plans/active/expanded-collection.md`
(re-selection, no new source) and `plans/active/balanced-history.md` (quota design
against a hard archive ceiling).

---

# Plan: <collection name>

**Status:** active
**Created:** <YYYY-MM-DD>
**Goal:** <one line: what panel this produces, and the one number that motivates it —
e.g. "take the recent panel from 2,930 gigs to ~25,051 by dropping the survivor filter">

## Scope

**Covers:** <selection rule, download, extraction, and the apparatus built for them>

**Does not cover:** <name the downstream steps this deliberately stops short of —
normally rebuilding the index (19 → 21 → 23 → 18), refreshing `docs/data.json`, and
the draft>.

**Published-figure guard:** <which existing outputs must not move, and why. The pilot
paper's numbers are frozen in `data/pilot/paper-numbers.md` and enforced by
`code/32-check-draft-numbers.py`; any collection that writes over a file feeding them
is a paper revision, not a collection.> Write to a **new** prices file.

## The finding that drove the design

> Fill this in *after* step 1, not before. If there is nothing here, the campaign is
> being run on an assumption that has not been checked.

<The census result that determines the design, with the number. State plainly whether
the binding constraint is the archive or the selection rule — for every campaign so
far it has been the selection rule, and assuming otherwise is the failure mode this
section exists to prevent.>

## Steps

### 1. Census the headroom before assuming the source binds

- [ ] Count what the **existing index** already holds under each candidate rule —
      distinct gigs, snapshot-months, and matched gigs per adjacent quarter pair.
      Pattern: `code/37-collection-headroom.py`, `code/40-history-headroom.py`.
- [ ] **Validate the census by reproducing the shipped panel exactly** under the rule
      that produced it. A census that cannot regenerate a known answer is not evidence
      about the unknown ones.

| rule | criterion | gigs | snapshot-months | matched gigs / pair (median) |
|---|---|---:|---:|---:|
| A (shipped) | <> | | | |
| B | <> | | | |
| C | <> | | | |

- [ ] Probe whether a **fresh harvest** would add anything, before budgeting for one.
      Check status-code composition at the trailing edge; a collapse in status-200
      captures means re-harvesting recovers nothing (measured: 280,779 in 202409 → 66
      in 202603).

### 2. Choose the selection rule, and say what each rejected rule would have bought

- [ ] State the rule in one sentence, in terms of what the **index consumes** (matched
      gigs per adjacent quarter pair for a chained matched-model index) — not in terms
      of gigs collected. The two diverge by orders of magnitude and only the former
      governs precision.
- [ ] Record why the looser rules were rejected. Gigs that cannot contribute a price
      relative (singletons; multi-month but single-quarter) are cost, not coverage.
- [ ] Where supply is below target, the manifest takes everything available and
      **records the shortfall**. Thin cells get published as thin (§3.7 not-identified
      marking) — never silently backfilled from a different rule.

### 3. Measure the cost, and do not assume per-page size is flat

- [ ] Pages, wall-clock at the chosen rate, and disk. Compare disk against `df` free,
      not against nothing.
- [ ] **Break the size estimate out by year.** Fiverr pages grew ~7× across 2018–2026
      (37 → 268 KB gzipped); a flat per-page average taken from the recent corpus
      overstated a historical campaign's footprint by 2.2× and nearly killed it.
- [ ] Weight by the manifest's own year distribution.

| option | gigs | pages | crawl | disk |
|---|---:|---:|---:|---:|

### 4. Pilot before scale — always, and pilot the part that is *unvalidated*

- [ ] Sample **stratified to over-weight the layouts the extractor has never seen**,
      not proportionally. A proportional draw puts almost nothing in the quarters the
      pilot exists to test. Pattern: `code/42-balanced-pilot.py`.
- [ ] Run download + extraction end to end. Record: pages ok, failures, retries,
      sustained pages/s, gzipped KB/page by year, extraction success %, and the
      distribution over `extraction_method`.
- [ ] **Gate:** extraction ≥ <95>% on the oldest stratum, and zero systematic failure
      mode in the errors log. A `dollar_fallback` cluster is a red flag — that is the
      path that scraped Fiverr Pro budget-filter widgets and put a fake `1000 → 500`
      move into a published series.
- [ ] Re-cost from the pilot's measurements and revisit step 3's decision. Two of
      three campaigns changed a design choice here.

### 5. Full download

- [ ] Driver script in `code/run-<name>-pipeline.sh` (skeleton below). Launch with
      `nohup`/background and tee to `runs/<tag>/`.
- [ ] **10 concurrent / 10 req/s.** The 20/20 setting logged **12,336 failures against
      15,150 successes (45%)** at the *same* 5.71 pages/s sustained throughput. Faster
      settings buy nothing here.
- [ ] `--gzip` (5.0× measured). Step 08 reuses on-disk pages in either storage form,
      so overlapping manifests are not re-fetched; step 09 reads both transparently.
- [ ] Checkpointed and idempotent — successes checkpoint, transient failures
      deliberately do not, so a re-run retries exactly the failures.
- [ ] Two retry passes after the main pass.
- [ ] Disk watchdog if the run is unattended and long.

### 6. Extract over the **combined** corpus

- [ ] `code/09-extract-prices.py --html-dir <> --output data/pilot/<name>-prices.csv
      --errors-log data/pilot/<name>-extract-errors.tsv` — a new output file, never
      over the published one.
- [ ] Check the errors log by *category of error*, not just its line count.
- [ ] Confirm `seller`/`slug`/`date` parse cleanly from whatever filename form the new
      pages use (the `.html.gz` double suffix leaves `.html` inside the slug unless
      handled).

### 7. Adequacy check — the point of the whole exercise

- [ ] Matched gigs per bilateral per category, against the **±5% at 95%** rule (§3.6).
      Requirement by category: writing ≈900, design ≈1,100, video ≈1,600,
      coding ≈7,400.
- [ ] Report which categories now clear it, which improved without clearing, and which
      are **archive-exhausted** — at the ceiling regardless of budget. Coding's supply
      peaks at 6,142 against a 7,400 requirement: taking every coding gig in the index
      still misses, and that is a result to publish, not a shortfall to work around.

### 8. Decision gate — rebuilding downstream is deliberate, never automatic

- [ ] Does the enlarged panel move the index enough to justify rebuilding
      19 → 21 → 23 → 18, refreshing `docs/data.json`, and re-freezing numbers?
- [ ] If yes, that is a separate plan with its own published-figure guard.

## Decision Log

- **<YYYY-MM-DD>: <decision>.** <Rationale, with the measurement that forced it. Record
  decisions *not* to do something too — "do not re-crawl the CDX index" retired a
  standing assumption and saved the campaign.>

## Known ceilings — to report, not fix

<Limits the collection cannot move at any budget, with the number that bounds each.
Distinguish these from things not yet attempted; a reader must be able to tell an
archive-imposed floor from a resource choice.>

## What this collection does NOT fix

<Requirements a reader might expect this to satisfy and it does not, with evidence.
Example: exit is unmeasurable from Wayback — `n_404 = 0` across 509,339 in-window
captures, because the archive stops re-requesting a delisted URL rather than recording
its death. Needs a live forward crawl; no volume of archive collection produces it.>

## Progress

- **<YYYY-MM-DD>:** <what ran, what it measured, what it changed>

---

## Appendix: driver script skeleton

Adapt from `code/run-balanced-pipeline.sh` (watchdog + full download) or
`code/run-expanded-pipeline.sh` (attaches to a download already in flight).

```bash
#!/usr/bin/env bash
# Driver: <campaign>.
#   1. download the manifest
#   2. two retry passes (re-runs 08 — skips on-disk successes, re-attempts fails)
#   3. extract prices over the WHOLE corpus -> <name>-prices.csv
#
# Writes to a NEW prices file. <published file> feeds docs/data.json and the frozen
# paper numbers; nothing here may move a published figure. Rebuilding the index
# (19 -> 21 -> 23 -> 18) is a separate, deliberate decision — see plans/active/<name>.md.
#
# Idempotent: every step resumes from its checkpoint, safe to re-run.
set -uo pipefail
cd /home/exouser/IntelligencePriceIndex
log() { echo "[$(date '+%F %T')] $*"; }

MANIFEST=data/pilot/<name>-manifest.tsv
HTML_DIR=data/pilot/html-<name>
DLOG=data/pilot/<name>-download-log.tsv
CKPT=data/pilot/<name>-download-checkpoint.txt
TOTAL=$(( $(wc -l < "$MANIFEST") - 1 ))
MIN_FREE_GB=10

# Disk watchdog — a full root filesystem takes the box down, not just the crawl.
watchdog() {
  while true; do
    sleep 300
    free_gb=$(df -BG --output=avail / | tail -1 | tr -dc '0-9')
    if [ "$free_gb" -lt "$MIN_FREE_GB" ]; then
      log "WATCHDOG: only ${free_gb} GB free (< ${MIN_FREE_GB}); stopping download."
      pkill -f "08-download-html.py.*<name>-manifest"
      return 1
    fi
  done
}
watchdog & WATCHDOG_PID=$!
trap 'kill $WATCHDOG_PID 2>/dev/null' EXIT

log "<campaign>: $TOTAL rows. Free disk: $(df -h / | tail -1 | awk '{print $4}'); need ~<N> GB."

for pass in 1 2 3; do
  log "Pass $pass: $( [ -f "$CKPT" ] && wc -l < "$CKPT" || echo 0 )/$TOTAL captured."
  python3 code/08-download-html.py --manifest "$MANIFEST" --html-dir "$HTML_DIR" \
    --log "$DLOG" --checkpoint "$CKPT" --gzip --concurrency 10 --max-rate 10
done
log "Download complete: $(wc -l < "$CKPT")/$TOTAL captured. Disk: $(du -sh "$HTML_DIR" | cut -f1)"

log "Extracting prices -> data/pilot/<name>-prices.csv"
python3 code/09-extract-prices.py --html-dir "$HTML_DIR" \
  --output data/pilot/<name>-prices.csv \
  --errors-log data/pilot/<name>-extract-errors.tsv

log "Done. Rows: $(( $(wc -l < data/pilot/<name>-prices.csv) - 1 ))"
log "Next (deliberate, not automatic): re-measure matched gigs per bilateral, then"
log "decide whether to rebuild 19 -> 21 -> 23 -> 18."
```

## Appendix: artifacts a campaign leaves behind

| artifact | path |
|---|---|
| plan | `plans/active/<name>.md` → `plans/completed/` when done |
| manifest builder | `code/NN-<name>-manifest.py` |
| pilot sampler | `code/NN-<name>-pilot.py` |
| driver | `code/run-<name>-pipeline.sh` |
| manifest | `data/pilot/<name>-manifest.tsv` |
| pages | `data/pilot/html-<name>/` (gzipped) |
| download log + checkpoint | `data/pilot/<name>-download-{log.tsv,checkpoint.txt}` |
| prices + extraction errors | `data/pilot/<name>-{prices.csv,extract-errors.tsv}` |
| census / cost / run notes | `runs/<tag>/` |
| audit trail | `progress.md` entry; `plans/todo.md` Change Log |

## Appendix: the checks that have actually caught something

Each of these is a real failure from a past campaign, in the order it would bite.

1. **Census before crawling.** Every campaign so far found the binding constraint was
   the selection rule, not the archive — the shipped recent panel used **3.2%** of the
   gigs already on disk.
2. **Reproduce the shipped panel** under the old rule as the census's control.
3. **Cost per page by year**, never a flat average — off by 2.2× on the historical run.
4. **Pilot the oldest / least familiar stratum**, over-weighted. The historical pilot
   surfaced an `old_json` extraction path that no modern page uses.
5. **Watch `extraction_method` shares, not just the success rate.** The `hire/*` Pro
   landing pages parsed "successfully" at 25.1% of rows and inverted the recent trend
   in 6 of 7 categories.
6. **Rate discipline.** 45% transient failures at 20/20, zero at 10/10, same throughput.
7. **New output file**, every time.
8. **Sample size means matched gigs per bilateral**, never panel gigs.
9. **Log what the rule dropped** — a shortfall recorded is a result; a shortfall
   silently absorbed reads as coverage.
