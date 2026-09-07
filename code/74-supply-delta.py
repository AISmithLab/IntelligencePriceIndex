#!/usr/bin/env python3
"""
Step 74: How much archive supply do the v2 labels actually add IN THE WINDOW the
index uses?

72-reclassify-v2.py reports its effect over all years, and most of it is
pre-2015: the URL-parse defect it found only touches the `http://fiverr.com:80/`
capture form, which the CDX index carries for 2010-2014 and not after. The
balanced collection starts 2018Q3, so a headline like "+126% writing gigs" is
mostly outside the window and says nothing about what the published series could
gain.

The quantity that matters is supply per (category, adjacent quarter pair) --
the ceiling 41-balanced-manifest.py runs into, and the thing marked `*` in
`balanced-coverage.md`. This recomputes it from both gig summaries and reports
the delta, separating the pairs where supply was already above target (more
supply buys nothing) from the pairs where it was the binding constraint.

Input:  data/cdx-index/gig-quarter-summary.tsv      (v1, from step 41)
        data/cdx-index/gig-quarter-summary-v2.tsv   (v2, from step 41 --gigsum)
Output: runs/uncollected-headroom/supply-delta.md
"""

import argparse
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
V1 = BASE_DIR / "data" / "cdx-index" / "gig-quarter-summary.tsv"
V2 = BASE_DIR / "data" / "cdx-index" / "gig-quarter-summary-v2.tsv"
OUTDIR = BASE_DIR / "runs" / "uncollected-headroom"

COLLECTED = ["audio", "coding", "design", "marketing", "translation", "video", "writing"]


def qnum(q):
    return int(q[:4]) * 4 + int(q[5]) - 1


def qstr(n):
    return f"{n // 4}Q{n % 4 + 1}"


def supply(path, floor, keep):
    """Matched gigs per (category, adjacent pair) at/after `floor`."""
    out = defaultdict(int)
    with open(path) as f:
        for line in f:
            gid, cat, lo, mask, _m = line.rstrip("\n").split("\t")
            if cat not in keep:
                continue
            lo, mask = int(lo), int(mask)
            qs = {lo + i for i in range(mask.bit_length()) if mask >> i & 1}
            qs = {q for q in qs if q >= floor}
            for q in qs:
                if q + 1 in qs:
                    out[(cat, q)] += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2018Q3")
    ap.add_argument("--end", default="2026Q1")
    ap.add_argument("--target", type=int, default=1200)
    args = ap.parse_args()

    floor, ceil = qnum(args.start), qnum(args.end)
    keep = set(COLLECTED)
    s1, s2 = supply(V1, floor, keep), supply(V2, floor, keep)

    pairs = sorted({q for _c, q in s1} | {q for _c, q in s2})
    pairs = [q for q in pairs if floor <= q < ceil]

    # A pair only benefits if v1 supply was BELOW target -- above it, the quota
    # already had spare candidates and extra supply changes nothing.
    binding = [(c, q) for c in COLLECTED for q in pairs if s1.get((c, q), 0) < args.target]
    gained = [(c, q) for c, q in binding if s2.get((c, q), 0) > s1.get((c, q), 0)]
    lifted = [(c, q) for c, q in binding if s2.get((c, q), 0) >= args.target]

    tot_add = sum(s2.get(k, 0) - s1.get(k, 0) for k in binding)

    L = [f"# Supply the v2 labels add inside the collection window", "",
         f"Window {args.start}-{args.end}, target {args.target} matched gigs per "
         f"(category, adjacent quarter pair). Supply recomputed from the two gig "
         f"summaries, so this is the ceiling `41-balanced-manifest.py` sees, not a "
         f"selection.", "",
         f"- Pairs where v1 supply was **below target** (the ones a bigger archive "
         f"could help): **{len(binding)}** of {len(pairs) * len(COLLECTED)}",
         f"- Of those, pairs where v2 supply is **higher**: **{len(gained)}**",
         f"- Of those, pairs v2 lifts **to or above target**: **{len(lifted)}**",
         f"- Total matched gigs added across binding pairs: **{tot_add:,}**", "",
         "## Supply per adjacent pair, v1 -> v2", "",
         "Bold where v1 was under target. `+` marks a pair v2 lifts to target.", "",
         "| pair | " + " | ".join(COLLECTED) + " |",
         "|---|" + "---|" * len(COLLECTED)]
    for q in pairs:
        cells = []
        for c in COLLECTED:
            a, b = s1.get((c, q), 0), s2.get((c, q), 0)
            cell = f"{a:,}->{b:,}" if b != a else f"{a:,}"
            if a < args.target:
                cell = f"**{cell}**" + ("+" if b >= args.target else "")
            cells.append(cell)
        L.append(f"| {qstr(q)}->{qstr(q + 1)} | " + " | ".join(cells) + " |")

    L += ["", "## Per category, over binding pairs only", "",
          "| category | binding pairs | pairs improved | pairs lifted to target | "
          "matched gigs added | mean supply v1 -> v2 |", "|---|---:|---:|---:|---:|---|"]
    for c in COLLECTED:
        bp = [q for q in pairs if s1.get((c, q), 0) < args.target]
        if not bp:
            L.append(f"| {c} | 0 | 0 | 0 | 0 | -- |")
            continue
        add = sum(s2.get((c, q), 0) - s1.get((c, q), 0) for q in bp)
        imp = sum(1 for q in bp if s2.get((c, q), 0) > s1.get((c, q), 0))
        lif = sum(1 for q in bp if s2.get((c, q), 0) >= args.target)
        m1 = sum(s1.get((c, q), 0) for q in bp) / len(bp)
        m2 = sum(s2.get((c, q), 0) for q in bp) / len(bp)
        L.append(f"| {c} | {len(bp)} | {imp} | {lif} | {add:,} | "
                 f"{m1:,.0f} -> {m2:,.0f} ({(m2/m1-1)*100:+.0f}%) |")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "supply-delta.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
