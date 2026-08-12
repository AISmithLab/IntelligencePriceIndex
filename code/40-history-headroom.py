#!/usr/bin/env python3
"""
Step 40: Census the collection headroom across the FULL history, not just the
recent window, and measure how uneven the archive's supply actually is.

`37-collection-headroom.py` answered the same question for 202407+ and found the
binding constraint was the selection rule, not the index. This asks whether that
also holds for 2011-2024 -- i.e. whether the thin early years in
`data/pilot/pilot-prices.csv` (302 rows in 2011, 4,888 in 2020) are a sampling
artifact we can fix by collecting more, or a property of what Wayback archived,
which no amount of collection can fix.

The distinction matters because a matched-model index is built from *bilateral
links*: a gig observed in both quarter Q and quarter Q+1. Total snapshots in a
quarter can look healthy while the links across it are empty. So the headline
number here is the adjacent-quarter matched-gig count, not the snapshot count.

MEMORY: this box has ~3 GB free, and the full history has far more distinct gigs
than the 91,849 that fit in RAM for the recent window. So the pass is
disk-based: project to (gig, month, timestamp, category), external-sort, then
stream one gig-group at a time in constant memory. The sorted projection is kept
-- `41-balanced-manifest.py` builds the actual download list from it rather than
re-streaming the 5.8 GB index.

Input:  data/cdx-index/gig-pages-classified.tsv   (5.8 GB, streamed once)
Output: runs/history-headroom/history-census.md
        runs/history-headroom/quarter-supply.tsv     (machine-readable)
        data/cdx-index/gig-month-index.tsv           (sorted projection, reused)
"""

import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gigfilter import is_gig_id

BASE_DIR = Path(__file__).resolve().parent.parent
CLASSIFIED = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
PROJECTION = BASE_DIR / "data" / "cdx-index" / "gig-month-index.tsv"
SORT_TMP = BASE_DIR / "data" / "cdx-index" / "sort-tmp"
OUT_DIR = BASE_DIR / "runs" / "history-headroom"

# Same category exclusions as step 37, so the two censuses are comparable.
SKIP_CATEGORIES = {"uncategorized", "data_entry", "data_analysis"}


def quarter_of(ym):
    return f"{ym[:4]}Q{(int(ym[4:6]) - 1) // 3 + 1}"


def build_projection():
    """Stream the classified index down to unique (gig, month) rows, sorted.

    Emits one line per (gig_id, month, timestamp, category) for status-200 gig
    captures, then external-sorts by gig then month then timestamp. Downstream
    takes the first timestamp in each (gig, month) run, which is the same
    one-snapshot-per-month convention 13-recent-manifest.py uses.
    """
    if PROJECTION.exists():
        print(f"Reusing existing projection: {PROJECTION}", file=sys.stderr)
        return

    SORT_TMP.mkdir(parents=True, exist_ok=True)
    raw = PROJECTION.with_suffix(".raw.tmp")

    print("Pass 1: projecting classified index -> (gig, month, ts, cat)...", file=sys.stderr)
    n_rows = n_kept = n_skipcat = n_reserved = n_status = 0
    with open(CLASSIFIED) as fin, open(raw, "w") as fout:
        next(fin, None)
        for line in fin:
            n_rows += 1
            p = line.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            urlkey, ts, status, cat = p[0], p[1], p[3], p[6]
            if status != "200":
                n_status += 1
                continue
            if cat in SKIP_CATEGORIES:
                n_skipcat += 1
                continue
            gid = urlkey.split(")/", 1)[1] if ")/" in urlkey else urlkey
            gid = gid.split("?", 1)[0]
            if not is_gig_id(gid):
                n_reserved += 1
                continue
            fout.write(f"{gid}\t{ts[:6]}\t{ts}\t{cat}\n")
            n_kept += 1
            if n_rows % 2_000_000 == 0:
                print(f"  ...{n_rows:,} rows, {n_kept:,} kept", file=sys.stderr, flush=True)

    print(f"  scanned {n_rows:,}; kept {n_kept:,}; dropped "
          f"{n_status:,} non-200 / {n_skipcat:,} skip-category / {n_reserved:,} reserved",
          file=sys.stderr)

    print("Pass 2: external sort by gig, month, timestamp...", file=sys.stderr)
    cmd = (f"sort -t'\t' -k1,1 -k2,2 -k3,3 -T '{SORT_TMP}' -S 512M "
           f"'{raw}' > '{PROJECTION}'")
    subprocess.run(["bash", "-c", cmd], check=True)
    raw.unlink()
    (OUT_DIR / "projection-stats.txt").parent.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "projection-stats.txt").write_text(
        f"rows_scanned\t{n_rows}\nrows_kept\t{n_kept}\n"
        f"dropped_non200\t{n_status}\ndropped_skipcat\t{n_skipcat}\n"
        f"dropped_reserved\t{n_reserved}\n")


def iter_gigs():
    """Yield (gig_id, category, {month: first_ts}) per gig from the projection."""
    cur_gid = None
    cur_cat = None
    months = {}
    with open(PROJECTION) as f:
        for line in f:
            gid, ym, ts, cat = line.rstrip("\n").split("\t")
            if gid != cur_gid:
                if cur_gid is not None:
                    yield cur_gid, cur_cat, months
                cur_gid, cur_cat, months = gid, cat, {}
            if ym not in months:          # first timestamp wins (sorted)
                months[ym] = ts
    if cur_gid is not None:
        yield cur_gid, cur_cat, months


def main():
    build_projection()

    print("Pass 3: censusing quarters...", file=sys.stderr)

    q_snaps = defaultdict(int)        # snapshot-months available per quarter
    q_gigs = defaultdict(int)         # distinct gigs seen per quarter
    q_linked = defaultdict(int)       # gigs in this quarter that are also in >=1 adjacent quarter
    pair_match = defaultdict(int)     # (Q, Q+1) -> gigs present in both
    q_gigs_cat = defaultdict(int)     # (quarter, category) -> gigs
    n_gigs = 0
    n_multi_q = 0
    total_months = 0

    for gid, cat, months in iter_gigs():
        n_gigs += 1
        total_months += len(months)
        qs = sorted({quarter_of(m) for m in months})
        qset = set(qs)
        if len(qs) >= 2:
            n_multi_q += 1
        for m in months:
            q_snaps[quarter_of(m)] += 1
        for q in qs:
            q_gigs[q] += 1
            q_gigs_cat[(q, cat)] += 1
        # adjacent-quarter links: the unit a chained matched-model index consumes
        for q in qs:
            y, qq = int(q[:4]), int(q[5])
            nxt = f"{y}Q{qq + 1}" if qq < 4 else f"{y + 1}Q1"
            prv = f"{y}Q{qq - 1}" if qq > 1 else f"{y - 1}Q4"
            if nxt in qset:
                pair_match[(q, nxt)] += 1
            if nxt in qset or prv in qset:
                q_linked[q] += 1
        if n_gigs % 500_000 == 0:
            print(f"  ...{n_gigs:,} gigs", file=sys.stderr, flush=True)

    quarters = sorted(q_snaps)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUT_DIR / "quarter-supply.tsv", "w") as f:
        f.write("quarter\tsnapshot_months\tdistinct_gigs\tlinked_gigs\tmatched_to_next\n")
        for q in quarters:
            y, qq = int(q[:4]), int(q[5])
            nxt = f"{y}Q{qq + 1}" if qq < 4 else f"{y + 1}Q1"
            f.write(f"{q}\t{q_snaps[q]}\t{q_gigs[q]}\t{q_linked[q]}\t"
                    f"{pair_match.get((q, nxt), 0)}\n")

    lines = []
    lines.append("# Full-history collection headroom\n")
    lines.append(f"Source: `{CLASSIFIED.name}`, all years. "
                 f"Same category/reserved-path exclusions as step 37.\n")
    lines.append(f"- Distinct gigs, all history: **{n_gigs:,}**")
    lines.append(f"- Gigs spanning >= 2 quarters (rule B): **{n_multi_q:,}**")
    lines.append(f"- Total snapshot-months available: **{total_months:,}**\n")

    lines.append("## Supply per quarter\n")
    lines.append("`matched_to_next` is the count of gigs observed in both this "
                 "quarter and the next -- the bilateral link a chained "
                 "matched-model index actually consumes. A quarter with many "
                 "snapshots but few matches contributes nothing to the chain.\n")
    lines.append("| quarter | snapshot-months | distinct gigs | linked gigs | matched to next |")
    lines.append("|---|---:|---:|---:|---:|")
    for q in quarters:
        y, qq = int(q[:4]), int(q[5])
        nxt = f"{y}Q{qq + 1}" if qq < 4 else f"{y + 1}Q1"
        lines.append(f"| {q} | {q_snaps[q]:,} | {q_gigs[q]:,} | {q_linked[q]:,} | "
                     f"{pair_match.get((q, nxt), 0):,} |")
    lines.append("")

    lines.append("## Category mix per quarter (distinct gigs)\n")
    cats = sorted({c for _, c in q_gigs_cat})
    lines.append("| quarter | " + " | ".join(cats) + " |")
    lines.append("|---" * (len(cats) + 1) + "|")
    for q in quarters:
        lines.append(f"| {q} | " + " | ".join(
            f"{q_gigs_cat.get((q, c), 0):,}" for c in cats) + " |")
    lines.append("")

    (OUT_DIR / "history-census.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nWrote {OUT_DIR / 'history-census.md'}", file=sys.stderr)
    print(f"Wrote {OUT_DIR / 'quarter-supply.tsv'}", file=sys.stderr)
    print(f"Projection retained at {PROJECTION}", file=sys.stderr)


if __name__ == "__main__":
    main()
