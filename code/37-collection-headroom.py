#!/usr/bin/env python3
"""
Step 37: Census the collection headroom that already exists in the CDX index.

Before crawling anything new, measure how many gigs the *existing* index makes
available in the recent window under progressively looser selection rules, and
what each rule costs in downloads. Answers: is the binding constraint the index
(needs a fresh CDX crawl), the selection rule (13-recent-manifest.py), or the
download budget?

Rules costed, per category:
  A  shipped      >= 2 distinct quarters AND >= 1 snapshot in 2025Q3..2026Q2
                  (this is what data/pilot/recent-manifest.tsv used: 3,589 gigs)
  B  no-survivor  >= 2 distinct quarters anywhere in the window
                  (drops the trailing-window requirement, which makes the recent
                  panel a survivor panel — see plans/todo.md)
  C  any-pair     >= 2 distinct *months* (the weakest rule that can still yield a
                  within-gig price relative)
  D  all          every gig seen in the window, including singletons

Also reports the index's month coverage, so the gap between the last archived
month and today is visible (the CDX index was harvested 2026-03-22).

Input:  data/cdx-index/gig-pages-classified.tsv   (6 GB, streamed once)
Output: stdout + runs/collection-headroom/census.md
"""

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gigfilter import is_gig_id

BASE_DIR = Path(__file__).resolve().parent.parent
CLASSIFIED = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
OUT_DIR = BASE_DIR / "runs" / "collection-headroom"

WINDOW_START = "202407"
TRAILING = {"2025Q3", "2025Q4", "2026Q1", "2026Q2"}
SKIP_CATEGORIES = {"uncategorized", "data_entry", "data_analysis"}

# Month index so a gig's coverage fits in two ints (bitmasks) instead of sets.
MONTHS = [f"{y}{m:02d}" for y in range(2024, 2027) for m in range(1, 13)]
MONTHS = [m for m in MONTHS if m >= WINDOW_START]
MONTH_IX = {m: i for i, m in enumerate(MONTHS)}
QUARTERS = sorted({f"{m[:4]}Q{(int(m[4:6]) - 1) // 3 + 1}" for m in MONTHS})
QUARTER_IX = {q: i for i, q in enumerate(QUARTERS)}
TRAILING_MASK = sum(1 << QUARTER_IX[q] for q in TRAILING if q in QUARTER_IX)


def gig_id(urlkey):
    tail = urlkey.split(")/", 1)[1] if ")/" in urlkey else urlkey
    return tail.split("?", 1)[0]


def popcount(x):
    return bin(x).count("1")


def main():
    # gig -> [category, quarter_mask, month_mask]
    gigs = {}
    month_snaps = defaultdict(int)
    n_rows = n_window = n_reserved = n_skipcat = 0

    with open(CLASSIFIED) as f:
        next(f, None)
        for line in f:
            n_rows += 1
            p = line.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            ts, status, cat = p[1], p[3], p[6]
            if status != "200":
                continue
            ym = ts[:6]
            if ym < WINDOW_START:
                continue
            month_snaps[ym] += 1
            n_window += 1
            if cat in SKIP_CATEGORIES:
                n_skipcat += 1
                continue
            gid = gig_id(p[0])
            if not is_gig_id(gid):
                n_reserved += 1
                continue
            mi = MONTH_IX.get(ym)
            if mi is None:
                continue          # month beyond the table (shouldn't happen)
            qi = QUARTER_IX[f"{ym[:4]}Q{(int(ym[4:6]) - 1) // 3 + 1}"]
            g = gigs.get(gid)
            if g is None:
                gigs[gid] = [cat, 1 << qi, 1 << mi]
            else:
                g[1] |= 1 << qi
                g[2] |= 1 << mi
            if n_window % 200_000 == 0:
                print(f"  ...{n_window:,} window snapshots, {len(gigs):,} gigs",
                      file=sys.stderr, flush=True)

    # Cost each rule. "Downloads" = one snapshot per month per selected gig,
    # which is what 13-recent-manifest.py emits.
    rules = ["A_shipped", "B_no_survivor", "C_any_pair", "D_all"]
    gigs_by = {r: defaultdict(int) for r in rules}
    dls_by = {r: defaultdict(int) for r in rules}

    for cat, qmask, mmask in gigs.values():
        nq, nm = popcount(qmask), popcount(mmask)
        hits = []
        if nq >= 2 and (qmask & TRAILING_MASK):
            hits.append("A_shipped")
        if nq >= 2:
            hits.append("B_no_survivor")
        if nm >= 2:
            hits.append("C_any_pair")
        hits.append("D_all")
        for r in hits:
            gigs_by[r][cat] += 1
            dls_by[r][cat] += nm

    cats = sorted({c for c, _, _ in gigs.values()})
    lines = []
    lines.append("# Collection headroom in the existing CDX index\n")
    lines.append(f"Window: {WINDOW_START} onward. Source: `{CLASSIFIED.name}`\n")
    lines.append(f"- Rows scanned: {n_rows:,}")
    lines.append(f"- Status-200 snapshots in window: {n_window:,}")
    lines.append(f"- Dropped, skipped category: {n_skipcat:,}")
    lines.append(f"- Dropped, reserved path (/hire/, /agencies/, ...): {n_reserved:,}")
    lines.append(f"- Distinct gigs in window: {len(gigs):,}\n")

    lines.append("## Index month coverage (status-200 snapshots)\n")
    lines.append("| month | snapshots |")
    lines.append("|---|---:|")
    for m in sorted(month_snaps):
        lines.append(f"| {m} | {month_snaps[m]:,} |")
    lines.append("")

    lines.append("## Gigs available per selection rule\n")
    lines.append("| category | " + " | ".join(rules) + " |")
    lines.append("|---" * (len(rules) + 1) + "|")
    for c in cats:
        lines.append(f"| {c} | " + " | ".join(f"{gigs_by[r][c]:,}" for r in rules) + " |")
    lines.append("| **total** | " + " | ".join(
        f"**{sum(gigs_by[r].values()):,}**" for r in rules) + " |")
    lines.append("")

    lines.append("## Download cost per rule (snapshot-months)\n")
    lines.append("| category | " + " | ".join(rules) + " |")
    lines.append("|---" * (len(rules) + 1) + "|")
    for c in cats:
        lines.append(f"| {c} | " + " | ".join(f"{dls_by[r][c]:,}" for r in rules) + " |")
    lines.append("| **total** | " + " | ".join(
        f"**{sum(dls_by[r].values()):,}**" for r in rules) + " |")
    lines.append("")
    gb_per = 1.45 / 1024  # observed: 22 GB / 15,150 files
    for r in rules:
        n = sum(dls_by[r].values())
        lines.append(f"- {r}: {n:,} downloads ≈ {n * gb_per:.0f} GB uncompressed, "
                     f"{n / 20 / 3600:.1f} h at 20 req/s")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "census.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nWrote {OUT_DIR / 'census.md'}")


if __name__ == "__main__":
    main()
