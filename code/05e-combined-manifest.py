#!/usr/bin/env python3
"""
Step 1.5e: Build combined download manifest with three cohorts.

- Survivors (pre+post 2023): ~1 snapshot/month (full trajectory)
- Casualties (pre-only): first + last snapshot (entry & exit price)
- Entrants (post-only): first + last snapshot (market entry pricing)

Uses external sort + streaming.

Input:  data/cdx-index/gig-pages-classified.tsv
Output: data/cdx-index/download-manifest-combined.tsv
"""

import subprocess
import sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
OUTPUT = BASE_DIR / "data" / "cdx-index" / "download-manifest-combined.tsv"
SORTED_TMP = BASE_DIR / "data" / "cdx-index" / "combined-manifest-sorted.tmp"

AI_CATEGORIES = {"writing", "coding", "design", "translation", "data_analysis"}
CHATGPT_YEAR = 2023


def extract_seller(urlkey):
    try:
        path = urlkey.split(")/", 1)[1]
        return path.split("/", 1)[0]
    except (IndexError, ValueError):
        return ""


def main():
    print("Building combined three-cohort manifest...")
    print(f"  Categories: {', '.join(sorted(AI_CATEGORIES))}")
    print(f"  Survivors: ~1/month | Casualties & Entrants: first+last snapshot")
    print()

    # Step 1: Sort
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

    # Step 2: Stream, classify cohorts, sample accordingly
    print("Step 2: Streaming cohort assignment + sampling...")

    # We need to buffer each gig's records to determine cohort,
    # then decide what to keep. Each gig group is small enough to buffer.

    total_in = 0
    total_out = 0

    cohort_gigs = defaultdict(int)
    cohort_records = defaultdict(int)
    cat_gigs = defaultdict(lambda: defaultdict(int))
    cat_records = defaultdict(lambda: defaultdict(int))
    year_records = defaultdict(int)
    sellers = defaultdict(set)  # seller -> set of cohorts

    current_urlkey = None
    group_lines = []      # (line, timestamp, year)
    group_category = None

    # Output header with cohort column
    out_header = header + "\tcohort"

    def flush_group(urlkey, lines, category, fout):
        nonlocal total_out

        if category not in AI_CATEGORIES:
            return
        if not lines:
            return

        years = [y for _, _, y in lines if y > 0]
        if not years:
            return

        has_pre = any(y < CHATGPT_YEAR for y in years)
        has_post = any(y >= CHATGPT_YEAR for y in years)

        if has_pre and has_post:
            cohort = "survivor"
        elif has_pre:
            cohort = "casualty"
        else:
            cohort = "entrant"

        cohort_gigs[cohort] += 1
        cat_gigs[category][cohort] += 1

        seller = extract_seller(urlkey)
        if seller:
            sellers[seller].add(cohort)

        if cohort == "survivor":
            # Monthly downsample
            seen_months = set()
            for line, ts, year in lines:
                month_key = ts[:6]
                if month_key not in seen_months:
                    seen_months.add(month_key)
                    fout.write(f"{line}\t{cohort}\n")
                    total_out += 1
                    cohort_records[cohort] += 1
                    cat_records[category][cohort] += 1
                    year_records[year] += 1
        else:
            # First + last snapshot only
            # lines are already sorted by timestamp
            to_write = [lines[0]]
            if len(lines) > 1:
                to_write.append(lines[-1])
            for line, ts, year in to_write:
                fout.write(f"{line}\t{cohort}\n")
                total_out += 1
                cohort_records[cohort] += 1
                cat_records[category][cohort] += 1
                year_records[year] += 1

    with open(SORTED_TMP, "r") as fin, open(OUTPUT, "w") as fout:
        fout.write(out_header + "\n")

        for line in fin:
            line = line.strip()
            if not line:
                continue
            total_in += 1

            parts = line.split("\t")
            urlkey = parts[0]
            timestamp = parts[1] if len(parts) > 1 else ""
            category = parts[6] if len(parts) > 6 else "unknown"
            year = int(timestamp[:4]) if len(timestamp) >= 4 else 0

            if urlkey != current_urlkey:
                if current_urlkey is not None:
                    flush_group(current_urlkey, group_lines, group_category, fout)
                current_urlkey = urlkey
                group_lines = []
                group_category = category

            if category in AI_CATEGORIES:
                group_lines.append((line, timestamp, year))
                group_category = category

            if total_in % 5_000_000 == 0:
                print(f"  Processed {total_in:,} records...")

        # Flush last
        if current_urlkey is not None:
            flush_group(current_urlkey, group_lines, group_category, fout)

    # Clean up
    SORTED_TMP.unlink(missing_ok=True)
    try:
        tmp_dir.rmdir()
    except OSError:
        pass

    # Stats
    avg_page_kb = 590
    est_gb = total_out * avg_page_kb / 1024 / 1024
    total_gigs = sum(cohort_gigs.values())
    total_sellers = len(sellers)
    cross_cohort_sellers = sum(1 for s, cohorts in sellers.items() if len(cohorts) > 1)

    print()
    print("=" * 70)
    print("COMBINED MANIFEST")
    print("=" * 70)
    print()
    print(f"Total gigs:       {total_gigs:,}")
    print(f"Total snapshots:  {total_out:,}")
    print(f"Est. download:    {est_gb:.0f} GB raw, ~{est_gb / 3:.0f} GB compressed")
    print()

    print("BY COHORT:")
    print(f"  {'Cohort':<15} {'Gigs':>10} {'Snapshots':>12} {'Avg snaps':>10}")
    print(f"  {'-'*15} {'-'*10} {'-'*12} {'-'*10}")
    for cohort in ["survivor", "casualty", "entrant"]:
        g = cohort_gigs[cohort]
        r = cohort_records[cohort]
        avg = r / g if g > 0 else 0
        print(f"  {cohort:<15} {g:>10,} {r:>12,} {avg:>10.1f}")
    print()

    print("BY CATEGORY × COHORT (gigs):")
    print(f"  {'Category':<20} {'Survivor':>10} {'Casualty':>10} {'Entrant':>10} {'Total':>10}")
    print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*10} {'-'*10}")
    for cat in sorted(AI_CATEGORIES):
        s = cat_gigs[cat].get("survivor", 0)
        c = cat_gigs[cat].get("casualty", 0)
        e = cat_gigs[cat].get("entrant", 0)
        print(f"  {cat:<20} {s:>10,} {c:>10,} {e:>10,} {s+c+e:>10,}")
    print()

    print("BY YEAR:")
    for year in sorted(year_records.keys()):
        print(f"  {year}: {year_records[year]:>10,}")
    print()

    print(f"SELLERS: {total_sellers:,} unique")
    print(f"  Sellers appearing in multiple cohorts: {cross_cohort_sellers:,}")
    print(f"  (same seller with gigs that survived AND gigs that died)")
    print()
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
