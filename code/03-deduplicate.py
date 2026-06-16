#!/usr/bin/env python3
"""
Step 1.3: Deduplicate gig page records.

For each unique (base_url, timestamp_date) pair, keep only one record.
Also collapse consecutive snapshots with identical content digest.

Uses external sort + streaming to avoid loading all records into memory.

Input:  data/cdx-index/gig-pages.tsv
Output: data/cdx-index/gig-pages-deduped.tsv
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages.tsv"
OUTPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-deduped.tsv"
SORTED_TMP = BASE_DIR / "data" / "cdx-index" / "gig-pages-sorted.tmp"


def main():
    print("Step 1: Sorting by urlkey + timestamp (disk-backed)...")
    # Sort by urlkey (col 1), then timestamp (col 2), skipping header
    # Use -T to put temp files on the same filesystem (avoids /tmp running out)
    tmp_dir = BASE_DIR / "data" / "cdx-index" / "sort-tmp"
    tmp_dir.mkdir(exist_ok=True)

    # Extract header, sort the rest
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

    print("Step 2: Streaming dedup on sorted data...")
    total_in = 0
    total_out = 0
    unique_gigs = 0

    current_urlkey = None
    group_records = []  # (timestamp, digest, line) for current urlkey

    def flush_group(records, fout):
        """Deduplicate a single gig's records and write survivors."""
        nonlocal total_out

        # Sort by timestamp (should already be sorted, but be safe)
        records.sort(key=lambda x: x[0])

        # Step 1: Deduplicate by date — keep first per YYYYMMDD
        seen_dates = set()
        date_deduped = []
        for ts, digest, line in records:
            date = ts[:8]
            if date not in seen_dates:
                seen_dates.add(date)
                date_deduped.append((ts, digest, line))

        # Step 2: Collapse consecutive identical digests
        prev_digest = None
        for ts, digest, line in date_deduped:
            if digest != prev_digest:
                fout.write(line + "\n")
                total_out += 1
                prev_digest = digest

    with open(SORTED_TMP, "r") as fin, open(OUTPUT, "w") as fout:
        fout.write(header + "\n")

        for line in fin:
            line = line.strip()
            if not line:
                continue
            total_in += 1

            parts = line.split("\t")
            if len(parts) < 5:
                continue

            urlkey = parts[0]
            timestamp = parts[1]
            digest = parts[4]

            if urlkey != current_urlkey:
                # Flush previous group
                if group_records:
                    flush_group(group_records, fout)
                    unique_gigs += 1
                current_urlkey = urlkey
                group_records = []

            group_records.append((timestamp, digest, line))

            if total_in % 5_000_000 == 0:
                print(f"  Processed {total_in:,} records...")

        # Flush last group
        if group_records:
            flush_group(group_records, fout)
            unique_gigs += 1

    # Clean up
    SORTED_TMP.unlink(missing_ok=True)
    tmp_dir.rmdir()

    print(f"\nDeduplication results:")
    print(f"  Input:  {total_in:,} records")
    print(f"  After date dedup + digest collapse: {total_out:,} records")
    print(f"  Reduction: {(1 - total_out / total_in) * 100:.1f}%")
    print(f"  Unique gig URLs: {unique_gigs:,}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
