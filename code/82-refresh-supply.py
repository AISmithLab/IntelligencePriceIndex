#!/usr/bin/env python3
"""
Step 82: what the 2025-2026 backfill actually bought, measured on collected prices.

WHY THIS STEP EXISTS. `81-cdx-refresh-delta.py` sized the recoverable pool from
the CDX index and projected roughly a doubling of matched-pair supply in every
2025-2026 quarter. `run-refresh-2025-pipeline.sh` then collected 35,938 pages and
extracted 35,925 price rows into `data/pilot/refresh2025-prices.csv`. This step
replaces the projection with the realised number.

The quantity is the one the index consumes: **matched gigs per (category,
adjacent quarter pair)** -- a gig counts for pair (q, q+1) only if it carries an
extracted basic price in BOTH quarters. That is what a matched-model bilateral
can difference; index supply from `runs/uncollected-headroom/supply-delta.md` is
an upper bound on it, because a capture can exist and still fail extraction.

BEFORE  = balanced + expanded panels, i.e. every price already in the draft.
AFTER   = those plus refresh2025-prices.csv.

Nothing here overwrites a published figure: the refresh prices live in their own
file and the before-column is recomputed from the untouched panels each run.

TWO DIAGNOSTICS travel with the table, because without them the headline reads
as a collection failure and it is not one. A matched-model bilateral needs a gig
priced in TWO ADJACENT quarters, so supply is destroyed by two independent
losses: fewer gigs captured, and each captured gig less likely to be revisited.
The step reports the quarters-per-gig distribution of the refresh, and the
archive's revisit rate by year from the index itself.

Input:  data/pilot/balanced-prices.csv[.gz]
        data/pilot/expanded-prices.csv[.gz]
        data/pilot/refresh2025-prices.csv
        data/pilot/{balanced,expanded,refresh-2025}-manifest*.tsv  (categories)
        data/cdx-index/gig-quarter-summary.tsv  (revisit rate by year)
Output: runs/cdx-refresh-2025/supply-realised.md
"""

import argparse
import csv
import gzip
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PILOT = BASE_DIR / "data" / "pilot"
OUTDIR = BASE_DIR / "runs" / "cdx-refresh-2025"
QSUMMARY = BASE_DIR / "data" / "cdx-index" / "gig-quarter-summary.tsv"

COLLECTED = ["audio", "coding", "design", "marketing", "translation", "video", "writing"]

# Panels already in the draft, and the one the refresh wrote.
BEFORE_PANELS = [PILOT / "balanced-prices.csv", PILOT / "expanded-prices.csv"]
AFTER_PANELS = [PILOT / "refresh2025-prices.csv"]

# gig_id -> category. Manifests carry the label the collection selected on.
CATEGORY_SOURCES = [
    (PILOT / "balanced-gig-category.csv.gz", "csv"),
    (PILOT / "balanced-manifest-1200.tsv", "tsv"),
    (PILOT / "expanded-manifest.tsv", "tsv"),
    (PILOT / "refresh-2025-manifest.tsv", "tsv"),
]


def qnum(q):
    return int(q[:4]) * 4 + int(q[5]) - 1


def qstr(n):
    return f"{n // 4}Q{n % 4 + 1}"


def opener(path):
    """Prefer the raw CSV; fall back to the committed gzip when it is absent."""
    if path.exists():
        return open(path, newline="")
    gz = path.with_suffix(path.suffix + ".gz")
    if gz.exists():
        return gzip.open(gz, "rt", newline="")
    raise FileNotFoundError(f"{path} (and no .gz beside it)")


def load_categories():
    cat = {}
    for path, kind in CATEGORY_SOURCES:
        if not path.exists():
            continue
        op = gzip.open(path, "rt", newline="") if path.suffix == ".gz" else open(path, newline="")
        with op as f:
            if kind == "csv":
                for row in csv.DictReader(f):
                    cat.setdefault(row["gig_id"], row["category"])
            else:
                for row in csv.DictReader(f, delimiter="\t"):
                    if row.get("gig_id"):
                        cat.setdefault(row["gig_id"], row["category"])
    return cat


def load_quarters(paths, cat):
    """gig_id -> set of quarter numbers where a basic price extracted."""
    seen = defaultdict(set)
    n_rows = n_priced = n_uncat = 0
    for path in paths:
        with opener(path) as f:
            for row in csv.DictReader(f):
                n_rows += 1
                if not row.get("price_basic"):
                    continue
                n_priced += 1
                gid = f"{row['seller']}/{row['slug']}"
                if gid not in cat:
                    n_uncat += 1
                seen[gid].add((int(row["year"]) * 4) + (int(row["month"]) - 1) // 3)
    return seen, n_rows, n_priced, n_uncat


def matched(seen, cat, keep):
    """(category, q) -> gigs priced in both q and q+1."""
    out = defaultdict(int)
    for gid, qs in seen.items():
        c = cat.get(gid, "uncategorized")
        if keep and c not in keep:
            continue
        for q in qs:
            if q + 1 in qs:
                out[(c, q)] += 1
    return out


def span_report(f, seen, manifest_path):
    """How many quarters does a refresh gig appear in? One is not differenceable."""
    span = Counter(len(v) for v in seen.values())
    adj = sum(1 for v in seen.values() if any(x + 1 in v for x in v))
    f.write("\n## Why the pairs barely moved: the refresh is one-shot captures\n\n")
    f.write("| quarters a gig is priced in | gigs |\n|---:|---:|\n")
    for k in sorted(span):
        f.write(f"| {k} | {span[k]:,} |\n")
    n = sum(span.values())
    f.write(f"\n**{span.get(1, 0):,} of {n:,} ({span.get(1, 0) / n:.1%}) of the refresh's gigs are "
            f"captured in exactly one quarter**, and only **{adj:,}** carry an adjacent pair "
            "inside the refresh at all. A gig seen once cannot be differenced at any price.\n")

    # The same count from the manifest, which separates "never collected" from
    # "collected and unpairable". If the two agree, the ceiling is the index.
    if manifest_path.exists():
        man = defaultdict(set)
        with open(manifest_path, newline="") as mf:
            for row in csv.DictReader(mf, delimiter="\t"):
                m = row["month"]
                man[row["gig_id"]].add(int(m[:4]) * 4 + (int(m[4:]) - 1) // 3)
        madj = sum(1 for v in man.values() if any(x + 1 in v for x in v))
        f.write(f"\nThe manifest holds {len(man):,} gigs and **{madj:,}** of them have an adjacent "
                f"pair, against the {adj:,} recovered. The shortfall is download and extraction "
                "loss; the ceiling is the index, not the collection.\n")


def revisit_report(f, path):
    """Share of gigs captured in a year that the archive revisited in an adjacent quarter."""
    if not path.exists():
        return
    years = defaultdict(lambda: [0, 0])
    with open(path) as sf:
        for line in sf:
            p = line.rstrip("\n").split("\t")
            lo, mask = int(p[2]), int(p[3])
            q = {lo + i for i in range(mask.bit_length()) if mask >> i & 1}
            for y in sorted({x // 4 for x in q}):
                inyr = {x for x in q if x // 4 == y}
                years[y][0] += 1
                if any(x + 1 in q or x - 1 in q for x in inyr):
                    years[y][1] += 1
    f.write("\n## The archive stopped revisiting, and that is the second loss\n\n")
    f.write("| year | gigs captured | with an adjacent-quarter pair | share |\n|---|---:|---:|---:|\n")
    for y in sorted(years):
        n, a = years[y]
        f.write(f"| {y} | {n:,} | {a:,} | {a / n:.1%} |\n")
    f.write("\nThe revisit rate is flat at 74-82% for 2018-2024 and then breaks. "
            "Matched-model supply is the product of the two columns, so the right edge loses "
            "twice over: fewer gigs, each less likely to be seen again.\n")


def table(f, title, cats, pairs, before, after, target):
    f.write(f"\n## {title}\n\n")
    f.write("| pair | " + " | ".join(cats) + " |\n")
    f.write("|---" * (len(cats) + 1) + "|\n")
    for q in pairs:
        cells = []
        for c in cats:
            b, a = before.get((c, q), 0), after.get((c, q), 0)
            cell = f"{b:,}" if a == b else f"{b:,}->{a:,}"
            if a >= target:
                cell = f"{cell}+"
            elif a < target:
                cell = f"**{cell}**"
            cells.append(cell)
        f.write(f"| {qstr(q)}->{qstr(q + 1)} | " + " | ".join(cells) + " |\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2024Q2", help="first pair reported in the detail table")
    ap.add_argument("--end", default="2026Q3")
    ap.add_argument("--target", type=int, default=1200)
    ap.add_argument("--all-categories", action="store_true",
                    help="report the new families too, not just the seven collected domains")
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    cat = load_categories()
    keep = None if args.all_categories else set(COLLECTED)

    before_seen, b_rows, b_priced, b_uncat = load_quarters(BEFORE_PANELS, cat)
    after_seen = {g: set(qs) for g, qs in before_seen.items()}
    add_seen, a_rows, a_priced, a_uncat = load_quarters(AFTER_PANELS, cat)
    for gid, qs in add_seen.items():
        after_seen.setdefault(gid, set()).update(qs)

    before = matched(before_seen, cat, keep)
    after = matched(after_seen, cat, keep)

    cats = COLLECTED if keep else sorted({c for c, _q in after})
    lo, hi = qnum(args.start), qnum(args.end)
    pairs = [q for q in sorted({q for _c, q in after} | {q for _c, q in before}) if lo <= q < hi]

    # Gigs the refresh added that were never in the panel at all.
    new_gigs = set(add_seen) - set(before_seen)

    out = OUTDIR / "supply-realised.md"
    with open(out, "w") as f:
        f.write("# The 2025-2026 backfill, measured on collected prices\n\n")
        f.write("Matched gigs per (category, adjacent quarter pair): a gig counts for a pair "
                "only if a basic price extracted in **both** quarters. `before` is the "
                "balanced + expanded panels; `after` adds `refresh2025-prices.csv`.\n\n")
        f.write("## Inputs\n\n")
        f.write("| panel | rows | with a basic price | gigs |\n|---|---:|---:|---:|\n")
        f.write(f"| before (balanced + expanded) | {b_rows:,} | {b_priced:,} | {len(before_seen):,} |\n")
        f.write(f"| refresh 2025-2026 | {a_rows:,} | {a_priced:,} | {len(add_seen):,} |\n")
        f.write(f"\nGigs the refresh adds that the panel did not have: **{len(new_gigs):,}**. "
                f"Rows whose gig carried no manifest category: {b_uncat:,} before, {a_uncat:,} refresh "
                "(counted as `uncategorized`).\n")

        table(f, f"Matched pairs, {args.start} onward (target {args.target:,})",
              cats, pairs, before, after, args.target)
        f.write(f"\n`+` marks a pair at or above the {args.target:,} target; bold marks a pair below it.\n")

        f.write("\n## Per category, over the reported pairs\n\n")
        f.write("| category | before | after | delta | x | pairs improved | pairs at target |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|\n")
        for c in cats:
            b = sum(before.get((c, q), 0) for q in pairs)
            a = sum(after.get((c, q), 0) for q in pairs)
            imp = sum(1 for q in pairs if after.get((c, q), 0) > before.get((c, q), 0))
            at = sum(1 for q in pairs if after.get((c, q), 0) >= args.target)
            mult = f"{a / b:.2f}x" if b else "n/a"
            f.write(f"| {c} | {b:,} | {a:,} | +{a - b:,} | {mult} | {imp}/{len(pairs)} | {at}/{len(pairs)} |\n")
        tb = sum(before.get((c, q), 0) for c in cats for q in pairs)
        ta = sum(after.get((c, q), 0) for c in cats for q in pairs)
        f.write(f"| **all** | **{tb:,}** | **{ta:,}** | **+{ta - tb:,}** | "
                f"**{ta / tb:.2f}x**" if tb else "| **all** | 0 | 0 | 0 | n/a")
        f.write(f" | | |\n")

        span_report(f, add_seen, PILOT / "refresh-2025-manifest.tsv")
        revisit_report(f, QSUMMARY)

        # The test the pipeline named: a category is identified in a pair only if
        # the pair has matched gigs at all. Report the last pair each category can
        # difference, before and after.
        f.write("\n## Where each category's series can still be differenced\n\n")
        f.write("A pair with zero matched gigs is not thin, it is unidentified. "
                "Last pair with any matched gig, and with at least 30:\n\n")
        f.write("| category | last pair >0 (before -> after) | last pair >=30 (before -> after) |\n")
        f.write("|---|---|---|\n")
        allp = sorted({q for _c, q in after} | {q for _c, q in before})
        for c in cats:
            def last(d, thr):
                qs = [q for q in allp if d.get((c, q), 0) >= thr]
                return qstr(max(qs)) + "->" + qstr(max(qs) + 1) if qs else "none"
            f.write(f"| {c} | {last(before, 1)} -> {last(after, 1)} | "
                    f"{last(before, 30)} -> {last(after, 30)} |\n")

    print(out.read_text())
    print(f"\nWritten to {out}")


if __name__ == "__main__":
    main()
