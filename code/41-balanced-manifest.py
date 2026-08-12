#!/usr/bin/env python3
"""
Step 41: Build a history-wide manifest that equalises support across quarters
instead of taking whatever the archive happens to hold.

WHY THIS EXISTS. Every manifest so far selected *gigs* and accepted whatever
per-quarter coverage fell out. `06c`/`07` sampled 500 sellers with longitudinal
depth; `38` took all gigs with >= 2 quarters in the recent window. Both produce
the same shape: snapshots pile up wherever Wayback crawled hardest (2024Q3 has
20,490 extracted rows; 2025Q2 has 110) and the index inherits that unevenness as
precision that swings by an order of magnitude across the series.

WHAT "BALANCED" MEANS HERE. Not equal snapshots per quarter -- equal *bilateral
links*. A chained matched-model index consumes gigs observed in BOTH quarter Q
and Q+1; a quarter with 20,000 snapshots and 12 matched gigs contributes a link
with +-50% precision regardless of its row count. So the quota is per
(category, adjacent-quarter-pair), and the objective is to bring every pair up
to TARGET matched gigs where supply allows, spending nothing on pairs already
past it.

That inverts the usual cost profile: the quarters that need downloading are the
ones the archive covered *worst*, and the ones already oversupplied get sampled
down. The result costs far less than "collect everything" and buys precision
exactly where the series is weakest.

SUPPLY IS A CEILING. Where the archive has fewer than TARGET gigs spanning a
pair, this takes all of them and records the shortfall in the coverage report.
Those pairs stay thin and must be published as thin -- see the not-identified
marking convention in the paper's SS3.7. Collection cannot manufacture a link
the archive never captured.

MEMORY: ~3 GB free, millions of distinct gigs. Pass A reduces the sorted
projection to one row per multi-quarter gig (a quarter bitmask), which does fit
in RAM; the greedy selection runs over that; pass B re-streams the projection to
emit snapshot rows for the chosen gigs.

Input:  data/cdx-index/gig-month-index.tsv   (from 40-history-headroom.py)
Output: data/pilot/balanced-manifest.tsv
        runs/history-headroom/balanced-coverage.md
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTION = BASE_DIR / "data" / "cdx-index" / "gig-month-index.tsv"
GIGSUM = BASE_DIR / "data" / "cdx-index" / "gig-quarter-summary.tsv"
OUT_MANIFEST = BASE_DIR / "data" / "pilot" / "balanced-manifest.tsv"
OUT_DIR = BASE_DIR / "runs" / "history-headroom"

DEFAULT_TARGET = 400        # matched gigs per (category, adjacent pair)
DEFAULT_START = "2018Q3"    # hard floor: the chain is severed before this


def quarter_of(ym):
    return f"{ym[:4]}Q{(int(ym[4:6]) - 1) // 3 + 1}"


def qnum(q):
    """2019Q3 -> integer index, so adjacency is +1."""
    return int(q[:4]) * 4 + int(q[5]) - 1


def qstr(n):
    return f"{n // 4}Q{n % 4 + 1}"


def build_gig_summary():
    """Pass A: sorted projection -> one row per multi-quarter gig."""
    if GIGSUM.exists():
        print(f"Reusing {GIGSUM}", file=sys.stderr)
        return

    print("Pass A: summarising gigs to quarter bitmasks...", file=sys.stderr)
    n_in = n_out = 0
    cur_gid = cur_cat = None
    quarters = set()
    months = set()

    def flush(fout):
        nonlocal n_out
        if cur_gid is None or len(quarters) < 2:
            return
        lo = min(quarters)
        mask = 0
        for q in quarters:
            mask |= 1 << (q - lo)
        # `months` is the DOWNLOAD COST of this gig: one page per distinct
        # month, not one per capture. The projection holds every capture, so
        # counting rows here overstates the crawl ~7x.
        fout.write(f"{cur_gid}\t{cur_cat}\t{lo}\t{mask}\t{len(months)}\n")
        n_out += 1

    with open(PROJECTION) as fin, open(GIGSUM, "w") as fout:
        for line in fin:
            gid, ym, _ts, cat = line.rstrip("\n").split("\t")
            if gid != cur_gid:
                flush(fout)
                cur_gid, cur_cat = gid, cat
                quarters, months = set(), set()
            quarters.add(qnum(quarter_of(ym)))
            months.add(ym)
            n_in += 1
            if n_in % 5_000_000 == 0:
                print(f"  ...{n_in:,} rows, {n_out:,} multi-quarter gigs",
                      file=sys.stderr, flush=True)
        flush(fout)
    print(f"  {n_in:,} rows -> {n_out:,} multi-quarter gigs", file=sys.stderr)


def load_gigs(start_q):
    """Load the summary, keeping only gigs with >=2 quarters at/after start."""
    floor = qnum(start_q)
    gigs = []
    with open(GIGSUM) as f:
        for line in f:
            gid, cat, lo, mask, months = line.rstrip("\n").split("\t")
            lo, mask, months = int(lo), int(mask), int(months)
            qs = [lo + i for i in range(mask.bit_length()) if mask >> i & 1]
            qs = [q for q in qs if q >= floor]
            if len(qs) < 2:
                continue
            gigs.append((gid, cat, qs, months))
    return gigs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=DEFAULT_TARGET,
                    help="matched gigs wanted per (category, adjacent pair)")
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--max-downloads", type=int, default=None,
                    help="stop selecting once the manifest reaches this many rows")
    ap.add_argument("--per", choices=("month", "quarter"), default="quarter",
                    help="one page per gig-month (the legacy convention) or per "
                         "gig-quarter. The index is quarterly, so 'quarter' is "
                         "the granularity it consumes and costs ~2x less.")
    args = ap.parse_args()

    build_gig_summary()

    print(f"Loading gig summaries (>= {args.start})...", file=sys.stderr)
    gigs = load_gigs(args.start)
    print(f"  {len(gigs):,} candidate gigs", file=sys.stderr)

    # Pairs a gig can serve: consecutive quarters it is present in both of.
    def pairs_of(qs):
        s = set(qs)
        return [q for q in qs if q + 1 in s]

    # Supply per (category, pair), so shortfalls can be reported as ceilings.
    supply = defaultdict(int)
    for _gid, cat, qs, _m in gigs:
        for q in pairs_of(qs):
            supply[(cat, q)] += 1

    # Greedy: repeatedly take the gig closing the most deficient pairs. Scoring
    # by *deficit* rather than raw pair count stops long-lived gigs in the
    # oversupplied 2024 quarters from crowding out short-lived ones that are the
    # only support a thin pair has.
    need = {k: min(args.target, v) for k, v in supply.items()}
    filled = defaultdict(int)
    selected = set()
    n_rows = 0

    # Cheap approximation to full greedy (which would be O(n^2)): score every
    # gig once against the initial deficits, take them in that order, and skip
    # any whose pairs have since filled. One pass, and it converges because
    # deficits only shrink.
    print("Scoring candidates...", file=sys.stderr)
    scored = []
    for gid, cat, qs, months in gigs:
        ps = pairs_of(qs)
        if not ps:
            continue
        # rarity weight: a pair with little supply is worth more
        score = sum(1.0 / supply[(cat, q)] for q in ps)
        # cost is pages fetched: one per month, or one per quarter
        cost = months if args.per == "month" else len(qs)
        scored.append((score, gid, cat, tuple(ps), cost))
    scored.sort(reverse=True)

    print("Selecting...", file=sys.stderr)
    for score, gid, cat, ps, cost in scored:
        if any(filled[(cat, q)] < need[(cat, q)] for q in ps):
            selected.add(gid)
            n_rows += cost
            for q in ps:
                filled[(cat, q)] += 1
            if args.max_downloads and n_rows >= args.max_downloads:
                print(f"  hit --max-downloads at {n_rows:,}", file=sys.stderr)
                break

    print(f"  selected {len(selected):,} gigs, {n_rows:,} snapshot-months",
          file=sys.stderr)

    # Pass B: emit manifest rows for the selected gigs.
    print("Pass B: writing manifest...", file=sys.stderr)
    floor = qnum(args.start)
    written = 0
    last_key = None
    with open(PROJECTION) as fin, open(OUT_MANIFEST, "w") as fout:
        # Column names match what 08-download-html.py reads: `timestamp` and
        # `original` (the plain Fiverr URL -- 08 wraps it in the wayback
        # id_/ template itself).
        fout.write("gig_id\ttimestamp\tmonth\tcategory\toriginal\n")
        for line in fin:
            gid, ym, ts, cat = line.rstrip("\n").split("\t")
            if gid not in selected:
                continue
            if qnum(quarter_of(ym)) < floor:
                continue
            # One page per (gig, period) -- the projection is sorted by ts, so
            # the first capture in each period wins. Without this the manifest
            # carries every capture and the crawl is ~7x larger than costed.
            key = (gid, ym) if args.per == "month" else (gid, quarter_of(ym))
            if key == last_key:
                continue
            last_key = key
            fout.write(f"{gid}\t{ts}\t{ym}\t{cat}\t"
                       f"https://www.fiverr.com/{gid}\n")
            written += 1
    print(f"  wrote {written:,} rows to {OUT_MANIFEST}", file=sys.stderr)

    # Coverage report: where the target is met and where supply is the ceiling.
    cats = sorted({c for _, c, _, _ in gigs})
    allq = sorted({q for _c, q in supply})
    lines = ["# Balanced manifest coverage\n",
             f"Target: **{args.target}** matched gigs per (category, adjacent "
             f"quarter pair), from {args.start}.\n",
             f"- Candidate gigs: {len(gigs):,}",
             f"- Selected gigs: {len(selected):,}",
             f"- Manifest rows (snapshot-months): {written:,}\n",
             "## Matched gigs per adjacent pair (selected / supply available)\n",
             "`supply` is the ceiling the archive imposes. Where selected < "
             "target and selected == supply, the archive is exhausted and the "
             "pair stays thin no matter what we download.\n",
             "| pair | " + " | ".join(cats) + " |",
             "|---" * (len(cats) + 1) + "|"]
    for q in allq:
        cells = []
        for c in cats:
            s, sup = filled[(c, q)], supply.get((c, q), 0)
            mark = "" if s >= args.target else ("*" if s == sup else "?")
            cells.append(f"{s:,}/{sup:,}{mark}" if sup else "--")
        lines.append(f"| {qstr(q)}->{qstr(q + 1)} | " + " | ".join(cells) + " |")
    lines.append("\n`*` = archive exhausted (selected all available, still under target).\n")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "balanced-coverage.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote {OUT_DIR / 'balanced-coverage.md'}", file=sys.stderr)


if __name__ == "__main__":
    main()
