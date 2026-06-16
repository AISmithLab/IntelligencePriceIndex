#!/usr/bin/env python3
"""
Step 1.5b: Research-driven longitudinal filter.

Selects gigs most valuable for studying AI's impact on prices and worker upskilling.

Criteria:
  - AI-exposed categories only (writing, coding, design, translation, data_analysis)
  - Must have snapshots in BOTH pre-ChatGPT (before 2023) AND post-ChatGPT (2023+)
  - ≥2 snapshots in each era (so we can see within-era trends too)
  - Extracts seller username for worker-level panel tracking

Uses external sort + streaming to stay within memory limits.

Input:  data/cdx-index/gig-pages-classified.tsv
Output: data/cdx-index/download-manifest-research.tsv
        data/cdx-index/research-filter-stats.txt
"""

import subprocess
import sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
OUTPUT = BASE_DIR / "data" / "cdx-index" / "download-manifest-research.tsv"
STATS_OUT = BASE_DIR / "data" / "cdx-index" / "research-filter-stats.txt"
SORTED_TMP = BASE_DIR / "data" / "cdx-index" / "classified-research-sorted.tmp"

# AI-exposed categories worth downloading
AI_CATEGORIES = {"writing", "coding", "design", "translation", "data_analysis"}

# ChatGPT launch: Nov 30, 2022. Use 2023 as clean boundary.
CHATGPT_YEAR = 2023

# Minimum snapshots per era
MIN_PRE = 2
MIN_POST = 2


def extract_seller(urlkey):
    """Extract seller username from urlkey like 'com,fiverr)/username/slug'."""
    try:
        path = urlkey.split(")/", 1)[1]
        return path.split("/", 1)[0]
    except (IndexError, ValueError):
        return ""


def main():
    print("Research-driven longitudinal filter")
    print(f"  Categories: {', '.join(sorted(AI_CATEGORIES))}")
    print(f"  Requires ≥{MIN_PRE} pre-{CHATGPT_YEAR} + ≥{MIN_POST} post-{CHATGPT_YEAR} snapshots")
    print()

    # Step 1: Sort by urlkey
    print("Step 1: Sorting by urlkey + timestamp (disk-backed)...")
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

    # Step 2: Stream through sorted file
    print("Step 2: Streaming research filter...")

    total_in = 0
    total_category_match = 0
    total_out = 0
    gigs_in = 0
    gigs_passing = 0

    # Stats accumulators
    cat_gigs = defaultdict(int)
    cat_records = defaultdict(int)
    year_records = defaultdict(int)
    sellers = defaultdict(int)  # seller -> number of passing gigs

    current_urlkey = None
    group_lines = []
    group_years = []
    group_category = None

    def flush_group(urlkey, lines, years, category, fout):
        nonlocal total_out, gigs_passing

        pre = sum(1 for y in years if 0 < y < CHATGPT_YEAR)
        post = sum(1 for y in years if y >= CHATGPT_YEAR)

        if pre < MIN_PRE or post < MIN_POST:
            return

        gigs_passing += 1
        cat_gigs[category] += 1
        seller = extract_seller(urlkey)
        if seller:
            sellers[seller] += 1

        for line, year in zip(lines, years):
            fout.write(line + "\n")
            total_out += 1
            cat_records[category] += 1
            year_records[year] += 1

    with open(SORTED_TMP, "r") as fin, open(OUTPUT, "w") as fout:
        fout.write(header + "\n")

        for line in fin:
            line = line.strip()
            if not line:
                continue
            total_in += 1

            parts = line.split("\t")
            urlkey = parts[0] if parts else ""
            timestamp = parts[1] if len(parts) > 1 else ""
            category = parts[6] if len(parts) > 6 else "unknown"
            year = int(timestamp[:4]) if len(timestamp) >= 4 else 0

            if urlkey != current_urlkey:
                # Flush previous group
                if group_lines and group_category in AI_CATEGORIES:
                    flush_group(current_urlkey, group_lines, group_years, group_category, fout)
                    gigs_in += 1
                elif group_lines:
                    gigs_in += 1
                current_urlkey = urlkey
                group_lines = []
                group_years = []
                group_category = category

            # Only accumulate if category matches (save memory)
            if category in AI_CATEGORIES:
                group_lines.append(line)
                group_years.append(year)
                group_category = category
                total_category_match += 1

            if total_in % 5_000_000 == 0:
                print(f"  Processed {total_in:,} records...")

        # Flush last group
        if group_lines and group_category in AI_CATEGORIES:
            flush_group(current_urlkey, group_lines, group_years, group_category, fout)
            gigs_in += 1
        elif group_lines:
            gigs_in += 1

    # Clean up
    SORTED_TMP.unlink(missing_ok=True)
    try:
        tmp_dir.rmdir()
    except OSError:
        pass

    # Seller panel stats
    multi_gig_sellers = sum(1 for s, c in sellers.items() if c >= 2)
    total_sellers = len(sellers)

    # Estimate download size
    avg_page_kb = 590
    est_size_gb = total_out * avg_page_kb / 1024 / 1024

    # Print stats
    stats_lines = []
    def p(s=""):
        print(s)
        stats_lines.append(s)

    p()
    p("=" * 60)
    p("RESEARCH FILTER RESULTS")
    p("=" * 60)
    p()
    p(f"Input:            {total_in:,} records")
    p(f"Category match:   {total_category_match:,} records")
    p(f"Passing filter:   {total_out:,} records ({gigs_passing:,} gigs)")
    p(f"Record retention: {total_out / total_in * 100:.1f}%")
    p(f"Est. download:    {est_size_gb:.0f} GB raw, ~{est_size_gb / 3:.0f} GB compressed")
    p()
    p("BY CATEGORY:")
    p(f"  {'Category':<20} {'Gigs':>8} {'Snapshots':>12} {'Avg snaps':>10}")
    p(f"  {'-'*20} {'-'*8} {'-'*12} {'-'*10}")
    for cat in sorted(cat_gigs.keys(), key=lambda x: -cat_records[x]):
        g = cat_gigs[cat]
        r = cat_records[cat]
        p(f"  {cat:<20} {g:>8,} {r:>12,} {r/g:>10.1f}")
    p()
    p("BY YEAR:")
    p(f"  {'Year':<6} {'Snapshots':>12}")
    p(f"  {'-'*6} {'-'*12}")
    for year in sorted(year_records.keys()):
        p(f"  {year:<6} {year_records[year]:>12,}")
    p()
    p("SELLER PANEL:")
    p(f"  Total unique sellers:     {total_sellers:,}")
    p(f"  Sellers with ≥2 gigs:     {multi_gig_sellers:,}")
    p(f"  (enables within-seller analysis of upskilling)")
    p()
    p(f"Output: {OUTPUT}")

    with open(STATS_OUT, "w") as f:
        f.write("\n".join(stats_lines))


if __name__ == "__main__":
    main()
