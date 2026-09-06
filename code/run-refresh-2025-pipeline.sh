#!/usr/bin/env bash
# Driver: recover the 2025-2026 right edge, end to end.
#
# Ordering matters here and is not the obvious one. The bulk of the manifest
# (35,030 of ~35k captures) comes from the March 2026 all-time pull and does not
# depend on the CDX refresh at all, so the HTML download is started FIRST and runs
# alongside the refresh. The refresh only adds a further ~0.5-19%, and waiting
# hours for it before fetching anything would have bought nothing.
#
#   0. (already running, started by hand) 08-download-html.py pass 1, rate-limited
#      to 6/6 so it does not fight the CDX pull for web.archive.org
#   1. wait for the CDX refresh to exit
#   2. 81-cdx-refresh-delta.py -> manifest over the UNION of both pulls (atomic
#      rename, so pass 1 can be mid-flight)
#   3. wait for download pass 1 to exit
#   4. two more 08 passes at full rate: picks up the refresh's new captures and
#      re-attempts transient failures (the checkpoint skips everything on disk)
#   5. 09-extract-prices.py -> data/pilot/refresh2025-prices.csv
#
# Writes to a NEW prices file. `balanced-prices.csv` and `expanded-prices.csv` feed
# the frozen paper numbers; nothing here may move a published figure. Folding the
# recovered supply into the index is a separate, deliberate decision --
# see plans/active/fiverr-2025-2026-backfill.md.
#
# Idempotent: every step resumes from its checkpoint, safe to re-run.
set -uo pipefail
cd /home/exouser/IntelligencePriceIndex
log() { echo "[$(date '+%F %T')] $*"; }

MANIFEST=data/pilot/refresh-2025-manifest.tsv
HTML_DIR=data/pilot/html-refresh2025
DLOG=data/pilot/refresh2025-download-log.tsv
CKPT=data/pilot/refresh2025-download-checkpoint.txt
RUNDIR=runs/cdx-refresh-2025
captured() { [ -f "$CKPT" ] && wc -l < "$CKPT" || echo 0; }

# Anchor every pgrep on `python3` so the bash -c wrappers that carry the same
# string in their own command line -- and this script's own pgrep -- are not
# mistaken for the job. Waiting on a wrapper would let a step run too early.
wait_for() {                     # $1 = pgrep pattern, $2 = label
  local pid; pid=$(pgrep -f "$1" | head -1 || true)
  if [ -n "${pid:-}" ]; then
    log "Waiting for $2 (PID $pid)..."
    while kill -0 "$pid" 2>/dev/null; do sleep 60; done
    log "$2 exited."
  else
    log "$2 not running, continuing."
  fi
}

# 1. the CDX refresh
wait_for '^python3 .*01-download-cdx-index\.py' "CDX refresh"
log "Refresh records: $(cat data/cdx-index/raw-2025/*.tsv 2>/dev/null | wc -l)"

# 2. rebuild the manifest over the union of the March pull and the refresh
log "Step 81: re-sizing the delta over both pulls"
python3 -u code/81-cdx-refresh-delta.py > "$RUNDIR/delta.out" 2> "$RUNDIR/delta.err" \
  || { log "step 81 FAILED, see $RUNDIR/delta.err"; exit 1; }
TOTAL=$(( $(wc -l < "$MANIFEST") - 1 ))
log "Manifest now $TOTAL captures; $(captured) already on disk."

# 3. let the in-flight download finish before starting another pass on the same
#    checkpoint -- two writers on one checkpoint file would interleave and corrupt it
wait_for '^python3 code/08-download-html\.py .*refresh-2025-manifest' "download pass 1"

# 4. remaining passes at full rate, now that nothing else is hitting the archive
for pass in 2 3; do
  log "Download pass $pass ($(captured)/$TOTAL captured)"
  python3 code/08-download-html.py --manifest "$MANIFEST" --html-dir "$HTML_DIR" \
    --log "$DLOG" --checkpoint "$CKPT" --gzip --concurrency 10 --max-rate 10
done
log "Download complete: $(captured)/$TOTAL captured."
log "Disk: $(du -sh "$HTML_DIR" | cut -f1)"

# 5. extract prices
log "Extracting prices -> data/pilot/refresh2025-prices.csv"
python3 code/09-extract-prices.py --html-dir "$HTML_DIR" \
  --output data/pilot/refresh2025-prices.csv \
  --errors-log data/pilot/refresh2025-extract-errors.tsv

log "Done. Rows: $(( $(wc -l < data/pilot/refresh2025-prices.csv) - 1 ))"
log "Next (deliberate, not automatic): re-measure matched gigs per adjacent pair"
log "against runs/uncollected-headroom/supply-delta.md, and check whether audio"
log "re-identifies after 2024Q4 and translation after 2025Q1 -- that is the test."
