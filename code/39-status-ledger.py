#!/usr/bin/env python3
"""
Step 39: Build a full-status ledger for the collected gigs, from the RAW CDX.

`plans/todo.md` flags this as cheap now and impossible to retrofit: absence of a
gig in a Wayback-derived panel means "not archived", not "taken down", so exit
cannot be estimated from the manifest. The distinction is recoverable only from
the non-200 captures — a gig that Wayback kept requesting and got 404 for is
gone; a gig with no capture at all is merely unobserved.

Those non-200 rows exist ONLY in `data/cdx-index/raw/*.tsv`. Every downstream
file is status-200 by construction: `02-filter-gig-pages.py` dropped the rest,
so `gig-pages-classified.tsv` cannot answer this question and neither can any
manifest built from it.

Method: load the gig ids of interest (default: every gig in the expanded
manifest) into a set, then stream the raw CDX once and tally each gig-month by
status class. Memory is bounded by the gig set, not by the 11 GB input.

Input:  data/cdx-index/raw/*.tsv     (space-separated:
                                      urlkey timestamp original status digest length)
        data/pilot/expanded-manifest.tsv   (for the gig set + category)
Output: data/pilot/gig-status-ledger.tsv
          gig_id, category, month, n_200, n_3xx, n_403, n_404, n_4xx_other, n_5xx, n_other
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "cdx-index" / "raw"
MANIFEST = BASE_DIR / "data" / "pilot" / "expanded-manifest.tsv"
OUTPUT = BASE_DIR / "data" / "pilot" / "gig-status-ledger.tsv"

WINDOW_START = "202407"
CLASSES = ["n_200", "n_3xx", "n_403", "n_404", "n_4xx_other", "n_5xx", "n_other"]


def gig_id(urlkey):
    tail = urlkey.split(")/", 1)[1] if ")/" in urlkey else urlkey
    return tail.split("?", 1)[0]


def status_slot(s):
    if s == "200":
        return 0
    if s == "403":
        return 2
    if s == "404":
        return 3
    if len(s) == 3 and s.isdigit():
        c = s[0]
        if c == "3":
            return 1
        if c == "4":
            return 4
        if c == "5":
            return 5
    return 6            # "-", "0", junk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    ap.add_argument("--window-start", default=WINDOW_START)
    ap.add_argument("--output", type=Path, default=OUTPUT)
    args = ap.parse_args()

    cat_of = {}
    with open(args.manifest) as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            cat_of[row["gig_id"]] = row["category"]
    print(f"Tracking {len(cat_of):,} gigs from {args.manifest.name}")

    # gig -> {month: [counts per class]}
    ledger = defaultdict(lambda: defaultdict(lambda: [0] * len(CLASSES)))
    files = sorted(p for p in args.raw_dir.glob("*.tsv"))
    n_rows = n_hit = 0
    for path in files:
        before = n_hit
        with open(path, errors="replace") as f:
            for line in f:
                n_rows += 1
                p = line.split()
                if len(p) < 4:
                    continue
                ts = p[1]
                if ts[:6] < args.window_start:
                    continue
                gid = gig_id(p[0])
                cat = cat_of.get(gid)
                if cat is None:
                    continue
                n_hit += 1
                ledger[gid][ts[:6]][status_slot(p[3])] += 1
        print(f"  {path.name}: {n_rows:,} rows scanned, "
              f"{n_hit - before:,} in-window hits", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    tot = [0] * len(CLASSES)
    with open(args.output, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["gig_id", "category", "month"] + CLASSES)
        for gid in sorted(ledger):
            for ym in sorted(ledger[gid]):
                c = ledger[gid][ym]
                w.writerow([gid, cat_of[gid], ym] + c)
                for i, v in enumerate(c):
                    tot[i] += v
                rows += 1
    print(f"\nWrote {rows:,} gig-month rows -> {args.output}")
    print("Capture totals by status class:")
    for name, v in zip(CLASSES, tot):
        print(f"  {name:<14}{v:>10,}")
    gigs_seen = len(ledger)
    print(f"\n{gigs_seen:,}/{len(cat_of):,} tracked gigs appear in the raw CDX "
          f"in-window ({gigs_seen / max(len(cat_of), 1):.1%})")


if __name__ == "__main__":
    main()
