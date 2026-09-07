#!/usr/bin/env python3
"""
Step 67: How much panel is available in the categories the two collections skipped?

`expanded-collection.md` (recent frame) and `balanced-history.md` (2018Q3+) both
quota only over the seven broad domains — design, coding, writing, marketing,
video, audio, translation. The classifier in step 04 also emits `data_entry` and
`data_analysis`, and leaves 30% of snapshots `uncategorized` because those two
tiers plus taxonomy rows T9/T10/T12 never got keyword lists.

This censuses what is in the skipped labels, in the unit a chained matched-model
index actually consumes: matched gigs per adjacent quarter pair.

Input:  data/cdx-index/gig-pages-classified.tsv
Output: runs/uncollected-headroom/census.md  (+ per-pair TSV)
"""

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gigfilter import is_gig

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
OUTDIR = BASE_DIR / "runs" / "uncollected-headroom"

# the window the balanced collection established as achievable
QLO, QHI = (2018, 3), (2026, 1)

COLLECTED = {"design", "coding", "writing", "marketing", "video", "audio", "translation"}


def qkey(ts):
    y = int(ts[:4])
    q = (int(ts[4:6]) - 1) // 3 + 1
    return y * 4 + (q - 1)


QLO_K, QHI_K = QLO[0] * 4 + QLO[1] - 1, QHI[0] * 4 + QHI[1] - 1


def gig_id(url):
    url = url.split("?")[0].split("#")[0]
    path = url.split("fiverr.com/", 1)[-1] if "fiverr.com/" in url else url
    parts = path.strip("/").split("/")
    if len(parts) < 2:
        return None
    seller = parts[0]
    if seller.startswith(":"):          # host:80 forms leave an empty first segment
        return None
    return f"{seller}/{parts[1]}" if is_gig(seller) else None


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # category -> gig -> quarter bitmask (31 quarters fits in an int)
    seen = defaultdict(dict)
    snaps = defaultdict(int)
    rows = 0

    with open(INPUT) as f:
        f.readline()
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            rows += 1
            k = qkey(p[1])
            if not (QLO_K <= k <= QHI_K):
                continue
            g = gig_id(p[2])
            if g is None:
                continue
            cat = p[6]
            snaps[cat] += 1
            d = seen[cat]
            d[g] = d.get(g, 0) | (1 << (k - QLO_K))

    nq = QHI_K - QLO_K + 1
    lines = ["# Headroom in the categories both collections skipped", "",
             f"Source: `{INPUT.relative_to(BASE_DIR)}` ({rows:,} rows scanned)  ",
             f"Window: {QLO[0]}Q{QLO[1]}-{QHI[0]}Q{QHI[1]} ({nq} quarters), gig URLs only "
             "(`gigfilter.is_gig`)", "",
             "| category | collected? | in-window snapshots | distinct gigs | gigs >=2 quarters "
             "| median matched gigs / adjacent pair | min | max |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]

    pair_rows = ["category\tpair\tmatched_gigs"]
    summary = []
    for cat, d in seen.items():
        multi = 0
        pair = [0] * (nq - 1)
        for m in d.values():
            if m & (m - 1):             # more than one quarter set
                multi += 1
            for i in range(nq - 1):
                if (m >> i) & 3 == 3:   # both ends of link i present
                    pair[i] += 1
        med = sorted(pair)[len(pair) // 2]
        summary.append((cat, snaps[cat], len(d), multi, med, min(pair), max(pair)))
        for i, v in enumerate(pair):
            k = QLO_K + i
            k2 = k + 1
            pair_rows.append(f"{cat}\t{k//4}Q{k%4+1}->{k2//4}Q{k2%4+1}\t{v}")

    for cat, sn, n, multi, med, lo, hi in sorted(summary, key=lambda r: -r[4]):
        mark = "yes" if cat in COLLECTED else "**no**"
        lines.append(f"| {cat} | {mark} | {sn:,} | {n:,} | {multi:,} | **{med:,}** | {lo:,} | {hi:,} |")

    skipped = [r for r in summary if r[0] not in COLLECTED]
    lines += ["",
              f"**Skipped-label totals:** {sum(r[1] for r in skipped):,} snapshots, "
              f"{sum(r[2] for r in skipped):,} distinct gigs, "
              f"{sum(r[3] for r in skipped):,} of them spanning >=2 quarters.", ""]

    (OUTDIR / "census.md").write_text("\n".join(lines) + "\n")
    (OUTDIR / "pairs.tsv").write_text("\n".join(pair_rows) + "\n")
    print("\n".join(lines))
    print(f"\nWrote {OUTDIR/'census.md'} and {OUTDIR/'pairs.tsv'}")


if __name__ == "__main__":
    main()
