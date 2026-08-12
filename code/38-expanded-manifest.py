#!/usr/bin/env python3
"""
Step 38: Build an expanded recent-window download manifest.

Supersedes `13-recent-manifest.py` for collection. Two changes, both of which
`plans/todo.md` flags as necessary and one of which is impossible to retrofit:

1. NO SURVIVOR FILTER (default).
   Step 13 required >= 1 snapshot in the trailing window 2025Q3..2026Q2, which
   selects the recent panel on survival: 36.5% of its gigs are last seen in the
   final quarter vs 0.4% historically, and "first captured" is truncated at both
   window edges (1,747 of 2,930 gigs enter at WINDOW_START by construction).
   The default rule here (`B`) requires only >= 2 distinct quarters anywhere in
   the window, so entry and exit are no longer selected on.

2. A COVERAGE LEDGER (`--status-ledger`).
   One row per gig-month actually archived, whether or not the gig was selected,
   so the manifest's selection can be audited against the frame it was drawn
   from. NOTE: this file records status-200 coverage only, because its input
   `gig-pages-classified.tsv` was already filtered to status 200 back in step 02.
   Non-200 captures — the 403s and 404s that distinguish "taken down" from "not
   archived", and without which no exit hazard is estimable — live only in the
   raw CDX, and `39-status-ledger.py` builds that from `data/cdx-index/raw/`.

Selection rules (--rule):
  A  shipped      >= 2 distinct quarters AND >= 1 snapshot in the trailing window
                  (reproduces step 13's panel exactly: 2,930 gigs post-gigfilter)
  B  no-survivor  >= 2 distinct quarters anywhere in the window   [DEFAULT]
  C  any-pair     >= 2 distinct months (weakest rule yielding a price relative)
  D  all          every gig in the window, singletons included

Headroom under each rule is measured in `runs/collection-headroom/census.md`.

One snapshot per gig-month is kept (the latest in the month), matching step 13,
so the output is a strict superset of `recent-manifest.tsv` under rules B/C/D and
the 15,150 already-downloaded files are reused rather than re-fetched.

Input:  data/cdx-index/gig-pages-classified.tsv  (6 GB; streamed once)
Output: data/pilot/expanded-manifest.tsv      (timestamp, original, category, gig_id, month)
        data/pilot/expanded-gig-status.tsv    (gig_id, category, month, n_200, n_403, n_404, n_other)
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gigfilter import is_gig_id

BASE_DIR = Path(__file__).resolve().parent.parent
CLASSIFIED = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
OUTPUT = BASE_DIR / "data" / "pilot" / "expanded-manifest.tsv"
LEDGER = BASE_DIR / "data" / "pilot" / "expanded-gig-status.tsv"

WINDOW_START = "202407"
TRAILING = {"2025Q3", "2025Q4", "2026Q1", "2026Q2"}
SKIP_CATEGORIES = {"uncategorized", "data_entry", "data_analysis"}


def quarter(ym):
    return f"{ym[:4]}Q{(int(ym[4:6]) - 1) // 3 + 1}"


def gig_id(urlkey):
    """Key by seller/slug only — drop the query string, as step 13 does, so the
    same gig merges across snapshots regardless of tracking params."""
    tail = urlkey.split(")/", 1)[1] if ")/" in urlkey else urlkey
    return tail.split("?", 1)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule", choices=["A", "B", "C", "D"], default="B")
    ap.add_argument("--window-start", default=WINDOW_START)
    ap.add_argument("--categories", default=None,
                    help="Comma-separated subset, e.g. 'coding,writing'. Default: all.")
    ap.add_argument("--max-months-per-gig", type=int, default=0,
                    help="Cap snapshots per gig (0 = no cap). Keeps the spread by "
                         "taking evenly spaced months, so endpoints survive.")
    ap.add_argument("--output", type=Path, default=OUTPUT)
    ap.add_argument("--status-ledger", type=Path, default=LEDGER)
    ap.add_argument("--input", type=Path, default=CLASSIFIED)
    args = ap.parse_args()

    only = set(args.categories.split(",")) if args.categories else None

    # gig -> {"cat":, "months": {ym: (ts, original)}, "status": {ym: [n200,n403,n404,noth]}}
    gigs = {}
    n_rows = n_reserved = 0

    with open(args.input) as f:
        next(f, None)
        for line in f:
            n_rows += 1
            p = line.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            urlkey, ts, original, status, cat = p[0], p[1], p[2], p[3], p[6]
            ym = ts[:6]
            if ym < args.window_start:
                continue
            if cat in SKIP_CATEGORIES or (only and cat not in only):
                continue
            gid = gig_id(urlkey)
            if not is_gig_id(gid):
                n_reserved += 1
                continue
            g = gigs.get(gid)
            if g is None:
                g = gigs[gid] = {"cat": cat, "months": {}, "status": defaultdict(
                    lambda: [0, 0, 0, 0])}
            slot = {"200": 0, "403": 1, "404": 2}.get(status, 3)
            g["status"][ym][slot] += 1
            if status != "200":
                continue
            prev = g["months"].get(ym)
            if prev is None or ts > prev[0]:
                g["months"][ym] = (ts, original)     # latest 200 in the month

    print(f"Scanned {n_rows:,} rows; {len(gigs):,} gigs touched in window "
          f"(from {args.window_start}); dropped {n_reserved:,} reserved-path rows")

    # Apply the selection rule. Only status-200 months count toward selection —
    # a gig archived twice as a 403 yields no price and cannot be chained.
    selected = {}
    for gid, g in gigs.items():
        months = sorted(g["months"])
        quarters = {quarter(m) for m in months}
        if args.rule == "A":
            ok = len(quarters) >= 2 and bool(quarters & TRAILING)
        elif args.rule == "B":
            ok = len(quarters) >= 2
        elif args.rule == "C":
            ok = len(months) >= 2
        else:
            ok = len(months) >= 1
        if ok:
            selected[gid] = g

    per_cat = defaultdict(int)
    per_cat_dl = defaultdict(int)
    for g in selected.values():
        per_cat[g["cat"]] += 1
        per_cat_dl[g["cat"]] += len(g["months"])
    print(f"Rule {args.rule}: selected {len(selected):,} gigs")
    for c in sorted(per_cat, key=lambda x: -per_cat[x]):
        print(f"    {c:<14}{per_cat[c]:>8,} gigs  {per_cat_dl[c]:>9,} snapshots")

    cap = args.max_months_per_gig
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    with open(args.output, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["timestamp", "original", "category", "gig_id", "month"])
        for gid, g in selected.items():
            months = sorted(g["months"])
            if cap and len(months) > cap:
                # Evenly spaced including both endpoints — the endpoints carry
                # the base and terminal links the index is built from.
                step = (len(months) - 1) / (cap - 1)
                months = [months[round(i * step)] for i in range(cap)]
                months = sorted(set(months))
            for ym in months:
                ts, original = g["months"][ym]
                w.writerow([ts, original, g["cat"], gid, ym])
                rows += 1
    print(f"Wrote {rows:,} snapshot rows -> {args.output}")

    # Coverage ledger over ALL gigs touched in the window, not just the selected
    # ones, so the selection can be audited against its own frame. Status-200
    # only — see the module docstring and 39-status-ledger.py.
    led = 0
    with open(args.status_ledger, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["gig_id", "category", "month", "n_200", "selected"])
        for gid, g in gigs.items():
            sel = 1 if gid in selected else 0
            for ym in sorted(g["status"]):
                w.writerow([gid, g["cat"], ym, g["status"][ym][0], sel])
                led += 1
    print(f"Wrote {led:,} gig-month coverage rows -> {args.status_ledger}")


if __name__ == "__main__":
    main()
