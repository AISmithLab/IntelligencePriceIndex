#!/usr/bin/env python3
"""
Step 13: Build a recent-window download manifest to extend the IPI into the
trailing 12 months (true "past year").

The 500-seller pilot was sampled for long histories and goes sparse after 2024Q4.
To compute a genuine last-12-months per-category index we need gigs that are
actually archived in the recent quarters. This script selects, per category,
gigs that have:
  - >= 2 distinct quarters of coverage in the window (2024Q3 onward), AND
  - >= 1 snapshot in the trailing window (2025Q3..2026Q2),
so each selected gig yields a chainable price path reaching into the recent year.

For each selected gig we keep one snapshot per month (latest in the month),
across the full window, so the matched-model index can chain quarter-to-quarter.

Input:  data/cdx-index/gig-pages-classified.tsv  (6 GB; streamed once)
        (or a pre-filtered TSV via --prefiltered: category,timestamp,original,urlkey)
Output: data/pilot/recent-manifest.tsv  (timestamp, original, category, gig_id, month)
"""

import argparse
import csv
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gigfilter import is_gig_id

BASE_DIR = Path(__file__).resolve().parent.parent
CLASSIFIED = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
OUTPUT = BASE_DIR / "data" / "pilot" / "recent-manifest.tsv"

WINDOW_START = "202407"          # 2024Q3 — anchor quarters for chaining
TRAILING_QUARTERS = {"2025Q3", "2025Q4", "2026Q1", "2026Q2"}
# Categories too thin in the recent window to support an index (see 06f census).
SKIP_CATEGORIES = {"uncategorized", "data_entry", "data_analysis"}


def quarter(ts):
    y, m = int(ts[:4]), int(ts[4:6])
    return f"{y}Q{(m - 1) // 3 + 1}"


def gig_id(urlkey):
    # urlkey looks like "com,fiverr)/seller/slug?sorted&query".
    # Key by seller/slug only (drop query string) so the same gig merges
    # across snapshots regardless of tracking params — matches the price
    # pipeline, which keys by (seller, slug) from the URL path.
    tail = urlkey.split(")/", 1)[1] if ")/" in urlkey else urlkey
    return tail.split("?", 1)[0]


def iter_rows(prefiltered):
    """Yield (category, timestamp, original, urlkey) over the recent window."""
    if prefiltered:
        with open(prefiltered) as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) >= 4:
                    yield p[0], p[1], p[2], p[3]
        return
    # Stream the classified file directly (status 200, recent window only).
    with open(CLASSIFIED) as f:
        next(f, None)  # header
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            ts, status, cat = p[1], p[3], p[6]
            if status != "200" or ts[:6] < WINDOW_START:
                continue
            yield cat, ts, p[2], p[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefiltered", type=Path, default=None,
                    help="Optional pre-filtered TSV: category,timestamp,original,urlkey")
    args = ap.parse_args()

    print("Building recent-window manifest...")
    # gig -> {"cat":, "quarters": set, "months": {YYYYMM: (timestamp, original)}}
    gigs = {}
    n = 0
    n_reserved = 0
    for cat, ts, original, urlkey in iter_rows(args.prefiltered):
        n += 1
        if cat in SKIP_CATEGORIES:
            continue
        gid = gig_id(urlkey)
        if not is_gig_id(gid):
            n_reserved += 1     # /hire/, /agencies/ etc. — landing pages, not gigs
            continue
        g = gigs.get(gid)
        if g is None:
            g = gigs[gid] = {"cat": cat, "quarters": set(), "months": {}}
        g["quarters"].add(quarter(ts))
        ym = ts[:6]
        # keep latest timestamp within the month
        prev = g["months"].get(ym)
        if prev is None or ts > prev[0]:
            g["months"][ym] = (ts, original)
    print(f"  Scanned {n:,} snapshots; {len(gigs):,} distinct gigs in window")
    print(f"  Excluded {n_reserved:,} reserved-path snapshots (/hire/, /agencies/, ...)")

    # Select gigs with multi-quarter coverage reaching the trailing window.
    selected = {gid: g for gid, g in gigs.items()
                if len(g["quarters"]) >= 2 and (g["quarters"] & TRAILING_QUARTERS)}

    per_cat = defaultdict(int)
    for g in selected.values():
        per_cat[g["cat"]] += 1
    print(f"  Selected {len(selected):,} gigs:")
    for c in sorted(per_cat, key=lambda x: -per_cat[x]):
        print(f"    {c:<16}{per_cat[c]:>7,} gigs")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    with open(OUTPUT, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["timestamp", "original", "category", "gig_id", "month"])
        for gid, g in selected.items():
            for ym, (ts, original) in sorted(g["months"].items()):
                w.writerow([ts, original, g["cat"], gid, ym])
                rows += 1
    print(f"  Wrote {rows:,} snapshot rows -> {OUTPUT}")
    print(f"  (~{rows} downloads; avg {rows/max(len(selected),1):.1f} snapshots/gig)")


if __name__ == "__main__":
    main()
