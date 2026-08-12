#!/usr/bin/env bash
# Driver: the full link-balanced historical collection (2018Q3 -> 2026Q1).
#   1. download the balanced manifest (target 1200 matched gigs per pair)
#   2. two retry passes (re-runs 08 — skips on-disk successes, re-attempts fails)
#   3. extract prices over the WHOLE balanced corpus -> balanced-prices.csv
#
# Writes to a NEW prices file. `pilot-prices.csv` is the historical panel behind
# the frozen paper numbers; nothing here may move a published figure. Rebuilding
# the index (19 -> 21 -> 23 -> 18) is a separate, deliberate decision — see
# plans/active/balanced-history.md.
#
# The 1,946 pilot pages already on disk are reused, not re-fetched: step 08's
# existing_path() check matches either storage form.
#
# Idempotent: every step resumes from its checkpoint, safe to re-run.
set -uo pipefail
cd /home/exouser/IntelligencePriceIndex
log() { echo "[$(date '+%F %T')] $*"; }

MANIFEST=data/pilot/balanced-manifest.tsv
HTML_DIR=data/pilot/html-balanced
DLOG=data/pilot/balanced-download-log.tsv
CKPT=data/pilot/balanced-download-checkpoint.txt
TOTAL=$(( $(wc -l < "$MANIFEST") - 1 ))
MIN_FREE_GB=10

# Disk watchdog. Projected footprint is 35 GB against 95 GB free, but this is an
# ~11 h unattended run and a full root filesystem would take the box down, not
# just the crawl. Poll every 5 min; stop the download cleanly if headroom goes.
watchdog() {
  while true; do
    sleep 300
    free_gb=$(df -BG --output=avail / | tail -1 | tr -dc '0-9')
    if [ "$free_gb" -lt "$MIN_FREE_GB" ]; then
      log "WATCHDOG: only ${free_gb} GB free (< ${MIN_FREE_GB}); stopping download."
      pkill -f "08-download-html.py.*balanced-manifest"
      return 1
    fi
  done
}
watchdog &
WATCHDOG_PID=$!
trap 'kill $WATCHDOG_PID 2>/dev/null' EXIT

log "Balanced historical collection: $TOTAL rows, target 1200/pair, 2018Q3-2026Q1."
log "Free disk: $(df -h / | tail -1 | awk '{print $4}'); projected need ~35 GB."

# 1 + 2. download, then two retry passes over transient failures
for pass in 1 2 3; do
  log "Pass $pass: $( [ -f "$CKPT" ] && wc -l < "$CKPT" || echo 0 )/$TOTAL captured."
  python3 code/08-download-html.py --manifest "$MANIFEST" --html-dir "$HTML_DIR" \
    --log "$DLOG" --checkpoint "$CKPT" --gzip --concurrency 10 --max-rate 10
done
log "Download complete: $(wc -l < "$CKPT")/$TOTAL captured."
log "Disk: $(du -sh "$HTML_DIR" | cut -f1)"

# 3. extract prices over the combined corpus (plain + gzipped, all layouts)
log "Extracting prices -> data/pilot/balanced-prices.csv"
python3 code/09-extract-prices.py --html-dir "$HTML_DIR" \
  --output data/pilot/balanced-prices.csv \
  --errors-log data/pilot/balanced-extract-errors.tsv

log "Done. Rows: $(( $(wc -l < data/pilot/balanced-prices.csv) - 1 ))"
log "Next (deliberate, not automatic): re-measure matched gigs per bilateral on"
log "the balanced panel, then decide whether to rebuild 19 -> 21 -> 23 -> 18."
