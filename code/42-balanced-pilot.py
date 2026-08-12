#!/usr/bin/env python3
"""
Step 42: Draw a stratified pilot from the balanced manifest.

The expanded 2026-08-09 collection validated the download and extraction path
against 2024Q3+ pages only. The balanced manifest reaches back to 2018Q3, and
Fiverr's gig page changed materially over that span -- the historical corpus is
where `dollar_fallback` clusters at the old $5 floor and where the 10-point
rating scale appears (plans/todo.md). Whether `09-extract-prices.py` finds
`packageList` on a 2018 page is simply not known, and it is the one thing that
would invalidate the whole crawl after 11 hours of fetching.

So: sample per quarter rather than at random. A proportional sample would put
most of its rows in 2021-2022 (where supply is thickest) and only a handful in
2018-2019 -- precisely inverting the coverage this pilot exists to buy. Equal
allocation per quarter with the remainder going to the oldest quarters gives
every era enough rows to measure an extraction rate on.

Input:  data/pilot/balanced-manifest.tsv   (or --manifest)
Output: data/pilot/balanced-pilot-manifest.tsv
"""

import argparse
import random
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = BASE_DIR / "data" / "pilot" / "balanced-manifest.tsv"
OUT = BASE_DIR / "data" / "pilot" / "balanced-pilot-manifest.tsv"

RANDOM_SEED = 42


def quarter_of(ym):
    return f"{ym[:4]}Q{(int(ym[4:6]) - 1) // 3 + 1}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    rng = random.Random(RANDOM_SEED)

    by_q = defaultdict(list)
    header = None
    with open(args.manifest) as f:
        header = f.readline().rstrip("\n")
        for line in f:
            p = line.rstrip("\n").split("\t")
            by_q[quarter_of(p[2])].append(line)

    quarters = sorted(by_q)
    per = args.n // len(quarters)
    print(f"{len(quarters)} quarters, {per} rows each (+ remainder to oldest)")

    picked = []
    remainder = args.n - per * len(quarters)
    for i, q in enumerate(quarters):
        want = per + (1 if i < remainder else 0)
        rows = by_q[q]
        picked.extend(rows if len(rows) <= want else rng.sample(rows, want))

    with open(args.out, "w") as f:
        f.write(header + "\n")
        f.writelines(picked)

    print(f"Wrote {len(picked):,} rows to {args.out}")
    for q in quarters:
        got = sum(1 for r in picked if quarter_of(r.split('\t')[2]) == q)
        print(f"  {q}  {got:>4} of {len(by_q[q]):,} available")


if __name__ == "__main__":
    main()
