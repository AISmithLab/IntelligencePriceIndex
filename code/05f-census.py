#!/usr/bin/env python3
"""
Quick census: count unique gigs and snapshots by category from the classified file.
Streaming — no memory issues.
"""

from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"

def main():
    cat_gigs = defaultdict(set)  # category -> set of urlkeys (use set incrementally)
    cat_snaps = defaultdict(int)
    total = 0

    # We can't hold all urlkeys in a set per category for 22M records.
    # Instead, do a two-pass: count snaps in pass 1, count unique gigs via sorted stream.
    # Actually, let's just count snaps and unique urlkeys overall.

    # Pass 1: count snapshots per category
    print("Counting snapshots per category...")
    with open(INPUT, "r") as f:
        f.readline()  # skip header
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            parts = line.split("\t")
            category = parts[6] if len(parts) > 6 else "unknown"
            cat_snaps[category] += 1
            if total % 5_000_000 == 0:
                print(f"  {total:,}...")

    print(f"Total snapshots: {total:,}")
    print()

    # Pass 2: count unique gigs per category using sorted urlkeys
    # The file may not be sorted, so use unix sort on urlkey+category
    import subprocess
    SORTED_TMP = BASE_DIR / "data" / "cdx-index" / "census-sorted.tmp"
    tmp_dir = BASE_DIR / "data" / "cdx-index" / "sort-tmp"
    tmp_dir.mkdir(exist_ok=True)

    print("Sorting for unique gig count...")
    # Extract urlkey (col1) and category (col7), sort, count unique pairs
    sort_cmd = (
        f"tail -n +2 '{INPUT}' | "
        f"cut -f1,7 | "
        f"sort -t'\t' -k2,2 -k1,1 -u -T '{tmp_dir}' -S 1G > '{SORTED_TMP}'"
    )
    subprocess.run(sort_cmd, shell=True, check=True)

    print("Counting unique gigs per category...")
    cat_gig_count = defaultdict(int)
    total_gigs = 0
    with open(SORTED_TMP, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            cat = parts[1] if len(parts) > 1 else "unknown"
            cat_gig_count[cat] += 1
            total_gigs += 1

    SORTED_TMP.unlink(missing_ok=True)
    try:
        tmp_dir.rmdir()
    except OSError:
        pass

    # Print results
    print()
    print("=" * 70)
    print("FULL GIG CENSUS (all categories, post-dedup)")
    print("=" * 70)
    print()
    print(f"{'Category':<20} {'Unique gigs':>12} {'Snapshots':>12} {'Avg snaps':>10} {'% gigs':>8}")
    print(f"{'-'*20} {'-'*12} {'-'*12} {'-'*10} {'-'*8}")

    for cat in sorted(cat_gig_count.keys(), key=lambda x: -cat_gig_count[x]):
        g = cat_gig_count[cat]
        s = cat_snaps.get(cat, 0)
        avg = s / g if g > 0 else 0
        pct = g / total_gigs * 100
        print(f"{cat:<20} {g:>12,} {s:>12,} {avg:>10.1f} {pct:>7.1f}%")

    print(f"{'-'*20} {'-'*12} {'-'*12} {'-'*10} {'-'*8}")
    print(f"{'TOTAL':<20} {total_gigs:>12,} {total:>12,} {total/total_gigs:>10.1f}")


if __name__ == "__main__":
    main()
