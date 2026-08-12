#!/usr/bin/env bash
# Driver: finish the rule-B expanded collection once the download ends.
#   1. wait for the in-flight step-08 download to exit
#   2. two retry passes (re-runs 08 — skips on-disk successes, re-attempts fails)
#   3. extract prices over the WHOLE recent corpus -> expanded-prices.csv
#
# Writes to a NEW prices file. `recent-prices.csv` feeds docs/data.json and the
# frozen paper numbers, and the pilot paper is mid-submission; nothing here may
# move a published figure. Rebuilding the index (19 -> 21 -> 23 -> 18) is a
# separate, deliberate decision — see plans/active/expanded-collection.md.
#
# Idempotent: every step resumes from its checkpoint, safe to re-run.
set -uo pipefail
cd /home/exouser/IntelligencePriceIndex
log() { echo "[$(date '+%F %T')] $*"; }

MANIFEST=data/pilot/expanded-manifest.tsv
HTML_DIR=data/pilot/html-recent
DLOG=data/pilot/expanded-download-log.tsv
CKPT=data/pilot/expanded-download-checkpoint.txt
TOTAL=$(( $(wc -l < "$MANIFEST") - 1 ))

# 1. wait for the active download
PID=$(pgrep -f "08-download-html.py.*expanded-manifest" | head -1 || true)
if [ -n "${PID:-}" ]; then
  log "Waiting for download PID $PID ($(wc -l < "$CKPT")/$TOTAL captured)..."
  while kill -0 "$PID" 2>/dev/null; do sleep 60; done
  log "Download PID $PID exited."
fi

# 2. retry passes over transient failures
for pass in 1 2; do
  log "Retry pass $pass: $(wc -l < "$CKPT")/$TOTAL captured."
  python3 code/08-download-html.py --manifest "$MANIFEST" --html-dir "$HTML_DIR" \
    --log "$DLOG" --checkpoint "$CKPT" --gzip --concurrency 10 --max-rate 10
done
log "Download complete: $(wc -l < "$CKPT")/$TOTAL captured."
log "Disk: $(du -sh "$HTML_DIR" | cut -f1)"

# 3. extract prices over the combined corpus (plain + gzipped)
log "Extracting prices -> data/pilot/expanded-prices.csv"
python3 code/09-extract-prices.py --html-dir "$HTML_DIR" \
  --output data/pilot/expanded-prices.csv \
  --errors-log data/pilot/expanded-extract-errors.tsv

log "Done. Rows: $(( $(wc -l < data/pilot/expanded-prices.csv) - 1 ))"
log "Next (deliberate, not automatic): re-measure matched gigs per bilateral,"
log "then decide whether to rebuild 19 -> 21 -> 23 -> 18."
