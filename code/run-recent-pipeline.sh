#!/usr/bin/env bash
# Driver: finish the recent-window IPI pipeline once the in-flight download ends.
#   1. wait for the currently-running step-08 download to exit
#   2. retry pass (re-run 08 — skips checkpointed successes, re-attempts fails)
#   3. extract prices -> recent-prices.csv
#   4. build the trailing-12-month IPI
# Idempotent: every step resumes from its checkpoint/output, safe to re-run.
set -uo pipefail
cd /home/exouser/IntelligencePriceIndex
log() { echo "[$(date '+%F %T')] $*"; }

MANIFEST=data/pilot/recent-manifest.tsv
HTML_DIR=data/pilot/html-recent
DLOG=data/pilot/recent-download-log.tsv
CKPT=data/pilot/recent-download-checkpoint.txt

# 1. wait for the active download (if any) to finish
PID=$(pgrep -f "08-download-html.py.*html-recent" | head -1 || true)
if [ -n "${PID:-}" ]; then
  log "Waiting for active download PID $PID to finish..."
  while kill -0 "$PID" 2>/dev/null; do sleep 30; done
  log "Download PID $PID exited."
fi

# 2. retry pass over transient fails (429/timeout). Two passes max.
for pass in 1 2; do
  done_n=$(wc -l < "$CKPT")
  total_n=$(( $(wc -l < "$MANIFEST") - 1 ))
  log "Retry pass $pass: $done_n/$total_n captured. Re-running downloader for the remainder."
  python3 code/08-download-html.py --manifest "$MANIFEST" --html-dir "$HTML_DIR" \
    --log "$DLOG" --checkpoint "$CKPT" --concurrency 20 --max-rate 20
done
log "Download complete: $(wc -l < "$CKPT")/$(( $(wc -l < "$MANIFEST") - 1 )) captured."

# 3. extract prices
log "Extracting prices -> data/pilot/recent-prices.csv"
python3 code/09-extract-prices.py --html-dir "$HTML_DIR" \
  --output data/pilot/recent-prices.csv \
  --errors-log data/pilot/recent-extract-errors.tsv

# 4. build the trailing-12-month IPI
log "Building trailing-12-month IPI"
python3 code/14-recent-ipi.py \
  --prices data/pilot/recent-prices.csv \
  --manifest "$MANIFEST"

log "Pipeline complete. See data/pilot/recent-ipi-summary.md"
