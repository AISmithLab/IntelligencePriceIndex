#!/usr/bin/env python3
"""
Step 1.5: Apply longitudinal filter.

Keep only gigs with ≥3 unique snapshots spanning ≥2 years.

Uses external sort + streaming to avoid loading all records into memory.

Input:  data/cdx-index/gig-pages-classified.tsv
Output: data/cdx-index/download-manifest.tsv
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
OUTPUT = BASE_DIR / "data" / "cdx-index" / "download-manifest.tsv"
SORTED_TMP = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified-sorted.tmp"

MIN_SNAPSHOTS = 3
MIN_YEAR_SPAN = 2


def main():
    print(f"Applying longitudinal filter (≥{MIN_SNAPSHOTS} snapshots, ≥{MIN_YEAR_SPAN} year span)...")

    # Step 1: Sort by urlkey (col 1) so we can stream by group
    # The classified file has a 'category' column appended, but urlkey is still col 1
    print("Step 1: Sorting by urlkey (disk-backed)...")
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

    # Step 2: Stream through sorted file, grouping by urlkey
    print("Step 2: Streaming longitudinal filter...")
    total_in = 0
    total_out = 0
    gigs_in = 0
    gigs_passing = 0

    current_urlkey = None
    group_lines = []
    group_years = []

    def flush_group(lines, years, fout):
        nonlocal total_out, gigs_passing
        if len(lines) < MIN_SNAPSHOTS:
            return
        valid_years = [y for y in years if y > 0]
        if not valid_years:
            return
        if max(valid_years) - min(valid_years) < MIN_YEAR_SPAN:
            return
        gigs_passing += 1
        for line in lines:
            fout.write(line + "\n")
            total_out += 1

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
            year = int(timestamp[:4]) if len(timestamp) >= 4 else 0

            if urlkey != current_urlkey:
                if group_lines:
                    flush_group(group_lines, group_years, fout)
                    gigs_in += 1
                current_urlkey = urlkey
                group_lines = []
                group_years = []

            group_lines.append(line)
            group_years.append(year)

            if total_in % 5_000_000 == 0:
                print(f"  Processed {total_in:,} records...")

        # Flush last group
        if group_lines:
            flush_group(group_lines, group_years, fout)
            gigs_in += 1

    # Clean up
    SORTED_TMP.unlink(missing_ok=True)
    try:
        tmp_dir.rmdir()
    except OSError:
        pass

    print(f"\nLongitudinal filter results:")
    print(f"  Input:  {total_in:,} records ({gigs_in:,} unique gigs)")
    print(f"  Passing: {total_out:,} records ({gigs_passing:,} gigs)")
    print(f"  Filtered out: {gigs_in - gigs_passing:,} gigs")
    print(f"  Gig retention: {gigs_passing / gigs_in * 100:.1f}%")
    print(f"  Record retention: {total_out / total_in * 100:.1f}%")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
