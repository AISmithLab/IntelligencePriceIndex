#!/usr/bin/env python3
"""
Step 1.5c: Downsample the research manifest to ~1 snapshot per month per gig.

This preserves the longitudinal signal while drastically reducing download size.
Keeps the first snapshot in each calendar month for each gig.

Input:  data/cdx-index/download-manifest-research.tsv
Output: data/cdx-index/download-manifest-final.tsv
"""

import subprocess
import sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "download-manifest-research.tsv"
OUTPUT = BASE_DIR / "data" / "cdx-index" / "download-manifest-final.tsv"
SORTED_TMP = BASE_DIR / "data" / "cdx-index" / "research-downsample-sorted.tmp"


def extract_seller(urlkey):
    try:
        path = urlkey.split(")/", 1)[1]
        return path.split("/", 1)[0]
    except (IndexError, ValueError):
        return ""


def main():
    print("Downsampling to ~1 snapshot per month per gig...")

    # Step 1: Sort (input should already be sorted, but ensure it)
    print("Step 1: Sorting by urlkey + timestamp...")
    tmp_dir = BASE_DIR / "data" / "cdx-index" / "sort-tmp"
    tmp_dir.mkdir(exist_ok=True)

    with open(INPUT, "r") as f:
        header = f.readline().strip()

    sort_cmd = (
        f"tail -n +2 '{INPUT}' | "
        f"sort -t'\t' -k1,1 -k2,2 -T '{tmp_dir}' -S 1G > '{SORTED_TMP}'"
    )
    result = subprocess.run(sort_cmd, shell=True)
    if result.returncode != 0:
        print("ERROR: sort failed")
        sys.exit(1)

    # Step 2: Stream, keeping first snapshot per month per gig
    print("Step 2: Streaming monthly downsample...")
    total_in = 0
    total_out = 0
    gig_count = 0

    cat_gigs = defaultdict(int)
    cat_records = defaultdict(int)
    year_records = defaultdict(int)
    sellers = defaultdict(int)

    current_urlkey = None
    seen_months = set()
    current_category = None

    with open(SORTED_TMP, "r") as fin, open(OUTPUT, "w") as fout:
        fout.write(header + "\n")

        for line in fin:
            line = line.strip()
            if not line:
                continue
            total_in += 1

            parts = line.split("\t")
            urlkey = parts[0]
            timestamp = parts[1] if len(parts) > 1 else ""
            category = parts[6] if len(parts) > 6 else "unknown"

            if urlkey != current_urlkey:
                if current_urlkey is not None:
                    gig_count += 1
                    cat_gigs[current_category] += 1
                    seller = extract_seller(current_urlkey)
                    if seller:
                        sellers[seller] += 1
                current_urlkey = urlkey
                current_category = category
                seen_months = set()

            # Keep first snapshot per YYYYMM
            month_key = timestamp[:6]  # YYYYMM
            if month_key not in seen_months:
                seen_months.add(month_key)
                fout.write(line + "\n")
                total_out += 1
                cat_records[category] += 1
                year = int(timestamp[:4]) if len(timestamp) >= 4 else 0
                year_records[year] += 1

        # Count last gig
        if current_urlkey is not None:
            gig_count += 1
            cat_gigs[current_category] += 1
            seller = extract_seller(current_urlkey)
            if seller:
                sellers[seller] += 1

    # Clean up
    SORTED_TMP.unlink(missing_ok=True)
    try:
        tmp_dir.rmdir()
    except OSError:
        pass

    avg_page_kb = 590
    est_size_gb = total_out * avg_page_kb / 1024 / 1024
    multi_gig_sellers = sum(1 for c in sellers.values() if c >= 2)

    print()
    print("=" * 60)
    print("DOWNSAMPLED MANIFEST")
    print("=" * 60)
    print()
    print(f"Input:            {total_in:,} records ({gig_count:,} gigs)")
    print(f"Output:           {total_out:,} records (1 per month per gig)")
    print(f"Reduction:        {(1 - total_out / total_in) * 100:.1f}%")
    print(f"Avg snaps/gig:    {total_out / gig_count:.1f}")
    print(f"Est. download:    {est_size_gb:.0f} GB raw, ~{est_size_gb / 3:.0f} GB compressed")
    print()
    print("BY CATEGORY:")
    print(f"  {'Category':<20} {'Gigs':>8} {'Snapshots':>12} {'Avg':>6}")
    print(f"  {'-'*20} {'-'*8} {'-'*12} {'-'*6}")
    for cat in sorted(cat_gigs.keys(), key=lambda x: -cat_records[x]):
        g = cat_gigs[cat]
        r = cat_records[cat]
        print(f"  {cat:<20} {g:>8,} {r:>12,} {r/g:>6.1f}")
    print()
    print("BY YEAR:")
    for year in sorted(year_records.keys()):
        print(f"  {year}: {year_records[year]:>8,}")
    print()
    print(f"SELLERS: {len(sellers):,} unique, {multi_gig_sellers:,} with ≥2 gigs")
    print(f"\nOutput: {OUTPUT}")


if __name__ == "__main__":
    main()
