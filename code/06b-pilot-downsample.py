#!/usr/bin/env python3
"""
Downsample pilot manifest to ~1 snapshot per month per gig.

Input:  data/pilot/pilot-manifest.tsv
Output: data/pilot/pilot-manifest-monthly.tsv
"""

import subprocess
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "pilot" / "pilot-manifest.tsv"
OUTPUT = BASE_DIR / "data" / "pilot" / "pilot-manifest-monthly.tsv"
SORTED_TMP = BASE_DIR / "data" / "pilot" / "pilot-sorted.tmp"


def main():
    print("Downsampling pilot to ~1/month per gig...")

    tmp_dir = BASE_DIR / "data" / "pilot" / "sort-tmp"
    tmp_dir.mkdir(exist_ok=True)

    with open(INPUT, "r") as f:
        header = f.readline().strip()

    sort_cmd = (
        f"tail -n +2 '{INPUT}' | "
        f"sort -t'\t' -k1,1 -k2,2 -T '{tmp_dir}' -S 1G > '{SORTED_TMP}'"
    )
    subprocess.run(sort_cmd, shell=True, check=True)

    total_in = 0
    total_out = 0
    current_urlkey = None
    seen_months = set()

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

            if urlkey != current_urlkey:
                current_urlkey = urlkey
                seen_months = set()

            month_key = timestamp[:6]
            if month_key not in seen_months:
                seen_months.add(month_key)
                fout.write(line + "\n")
                total_out += 1

    SORTED_TMP.unlink(missing_ok=True)
    try:
        tmp_dir.rmdir()
    except OSError:
        pass

    est_gb = total_out * 590 / 1024 / 1024
    print(f"Input:  {total_in:,} snapshots")
    print(f"Output: {total_out:,} snapshots (monthly)")
    print(f"Est. download: {est_gb:.1f} GB raw, ~{est_gb/3:.1f} GB compressed")


if __name__ == "__main__":
    main()
