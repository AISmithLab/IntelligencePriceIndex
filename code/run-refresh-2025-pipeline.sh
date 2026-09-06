#!/usr/bin/env bash
# Driver: recover the 2025-2026 right edge, end to end.
#   1. wait for the in-flight CDX refresh (01-download-cdx-index.py --from 20250101)
#   2. 81-cdx-refresh-delta.py -> the final manifest over the union of both pulls
#   3. 08-download-html.py, then two retry passes
#   4. 09-extract-prices.py -> data/pilot/refresh2025-prices.csv
#
# Writes to a NEW prices file. `balanced-prices.csv` and `expanded-prices.csv` feed
# the frozen paper numbers; nothing here may move a published figure. Folding the
# recovered supply into the index is a separate, deliberate decision --
# see plans/active/fiverr-2025-2026-backfill.md.
#
# Downloads are NOT started while the CDX pull is live: both hit web.archive.org and
# probing the CDX API during the pull already produced 429s.
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

# 1. wait for the CDX refresh to finish
# Anchor on `python3` so the bash -c wrappers that carry the same string in their
# own command line (and this script's own pgrep) are not mistaken for the job --
# waiting on a wrapper would let the download start while the pull is still live.
PID=$(pgrep -f '^python3 .*01-download-cdx-index\.py' | head -1 || true)
if [ -n "${PID:-}" ]; then
  log "Waiting for CDX refresh PID $PID..."
  while kill -0 "$PID" 2>/dev/null; do sleep 60; done
  log "CDX refresh exited. Records: $(cat data/cdx-index/raw-2025/*.tsv | wc -l)"
fi

# 2. rebuild the manifest over the union of the March pull and the refresh
log "Step 81: sizing the delta and writing the manifest"
python3 -u code/81-cdx-refresh-delta.py > "$RUNDIR/delta.out" 2> "$RUNDIR/delta.err" \
  || { log "step 81 FAILED, see $RUNDIR/delta.err"; exit 1; }
TOTAL=$(( $(wc -l < "$MANIFEST") - 1 ))
log "Manifest: $TOTAL captures to download"

# 3. download, then two retry passes over transient failures
for pass in 1 2 3; do
  log "Download pass $pass ($( [ -f "$CKPT" ] && wc -l < "$CKPT" || echo 0 )/$TOTAL captured)"
  python3 code/08-download-html.py --manifest "$MANIFEST" --html-dir "$HTML_DIR" \
    --log "$DLOG" --checkpoint "$CKPT" --gzip --concurrency 10 --max-rate 10
done
log "Download complete: $(wc -l < "$CKPT")/$TOTAL captured."
log "Disk: $(du -sh "$HTML_DIR" | cut -f1)"

# 4. extract prices
log "Extracting prices -> data/pilot/refresh2025-prices.csv"
python3 code/09-extract-prices.py --html-dir "$HTML_DIR" \
  --output data/pilot/refresh2025-prices.csv \
  --errors-log data/pilot/refresh2025-extract-errors.tsv

log "Done. Rows: $(( $(wc -l < data/pilot/refresh2025-prices.csv) - 1 ))"
log "Next (deliberate, not automatic): re-measure matched gigs per adjacent pair"
log "against runs/uncollected-headroom/supply-delta.md, then decide whether the"
log "recovered right edge changes the index window or only its error bars."
