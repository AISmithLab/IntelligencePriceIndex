#!/usr/bin/env python3
"""
Check survivorship bias: how many AI-category gigs exist only pre-2023 vs post-2023?
This tells us what we lose by requiring cross-milestone coverage.

Streams through the classified (post-dedup) file.
"""

import subprocess
import sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
SORTED_TMP = BASE_DIR / "data" / "cdx-index" / "survivorship-check-sorted.tmp"

AI_CATEGORIES = {"writing", "coding", "design", "translation", "data_analysis"}
CHATGPT_YEAR = 2023


def main():
    print("Checking survivorship bias in longitudinal filter...")

    tmp_dir = BASE_DIR / "data" / "cdx-index" / "sort-tmp"
    tmp_dir.mkdir(exist_ok=True)

    with open(INPUT, "r") as f:
        header = f.readline()

    sort_cmd = (
        f"tail -n +2 '{INPUT}' | "
        f"sort -t'\t' -k1,1 -k2,2 -T '{tmp_dir}' -S 1G > '{SORTED_TMP}'"
    )
    result = subprocess.run(sort_cmd, shell=True)
    if result.returncode != 0:
        print("ERROR: sort failed")
        sys.exit(1)

    # Stream through, categorize each gig
    current_urlkey = None
    current_category = None
    has_pre = False
    has_post = False
    min_year = 9999
    max_year = 0
    snap_count = 0

    # Counters per category
    # Groups: both_eras, pre_only, post_only, insufficient (single snapshot etc)
    stats = defaultdict(lambda: {"both": 0, "pre_only": 0, "post_only": 0,
                                  "both_snaps": 0, "pre_only_snaps": 0, "post_only_snaps": 0})

    total_gigs = 0

    def flush():
        nonlocal total_gigs
        if current_category not in AI_CATEGORIES:
            return
        total_gigs += 1
        cat = current_category
        if has_pre and has_post:
            stats[cat]["both"] += 1
            stats[cat]["both_snaps"] += snap_count
        elif has_pre:
            stats[cat]["pre_only"] += 1
            stats[cat]["pre_only_snaps"] += snap_count
        elif has_post:
            stats[cat]["post_only"] += 1
            stats[cat]["post_only_snaps"] += snap_count

    with open(SORTED_TMP, "r") as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            urlkey = parts[0]
            timestamp = parts[1] if len(parts) > 1 else ""
            category = parts[6] if len(parts) > 6 else "unknown"
            year = int(timestamp[:4]) if len(timestamp) >= 4 else 0

            if urlkey != current_urlkey:
                if current_urlkey is not None:
                    flush()
                current_urlkey = urlkey
                current_category = category
                has_pre = False
                has_post = False
                min_year = 9999
                max_year = 0
                snap_count = 0

            snap_count += 1
            if year > 0:
                if year < CHATGPT_YEAR:
                    has_pre = True
                else:
                    has_post = True
                min_year = min(min_year, year)
                max_year = max(max_year, year)

        # Flush last
        if current_urlkey is not None:
            flush()

    # Clean up
    SORTED_TMP.unlink(missing_ok=True)
    try:
        tmp_dir.rmdir()
    except OSError:
        pass

    # Print results
    print()
    print("=" * 75)
    print("SURVIVORSHIP BIAS ANALYSIS")
    print("=" * 75)
    print()
    print(f"Total AI-category gigs: {total_gigs:,}")
    print()
    print(f"{'Category':<20} {'Both eras':>10} {'Pre-only':>10} {'Post-only':>10} {'Pre-only %':>10}")
    print(f"{'-'*20} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")

    totals = {"both": 0, "pre_only": 0, "post_only": 0,
              "both_snaps": 0, "pre_only_snaps": 0, "post_only_snaps": 0}

    for cat in sorted(AI_CATEGORIES):
        s = stats[cat]
        total_cat = s["both"] + s["pre_only"] + s["post_only"]
        pre_pct = s["pre_only"] / total_cat * 100 if total_cat > 0 else 0
        print(f"{cat:<20} {s['both']:>10,} {s['pre_only']:>10,} {s['post_only']:>10,} {pre_pct:>9.1f}%")
        for k in totals:
            totals[k] += s[k]

    total_all = totals["both"] + totals["pre_only"] + totals["post_only"]
    pre_pct_all = totals["pre_only"] / total_all * 100 if total_all > 0 else 0
    print(f"{'-'*20} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
    print(f"{'TOTAL':<20} {totals['both']:>10,} {totals['pre_only']:>10,} {totals['post_only']:>10,} {pre_pct_all:>9.1f}%")
    print()
    print("Pre-only gigs = disappeared before 2023 (potential AI casualties)")
    print("Post-only gigs = appeared after 2023 (potential AI-era entrants)")
    print()
    print(f"Pre-only snapshot count: {totals['pre_only_snaps']:,} (would add ~{totals['pre_only_snaps'] * 590 / 1024 / 1024:.0f} GB raw)")
    print(f"Post-only snapshot count: {totals['post_only_snaps']:,}")
    print()
    print("VERDICT: If pre-only % is high, survivorship bias is a serious threat.")
    print("Consider including pre-only gigs (they show AI displacement) and")
    print("post-only gigs (they show AI-era market entry).")


if __name__ == "__main__":
    main()
