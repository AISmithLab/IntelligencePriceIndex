#!/usr/bin/env python3
"""
Pilot: 500 users with longitudinal depth.

Reuses the 5K qualifying user list, subsamples 500.
Extracts monthly snapshots for all their gigs.

Input:  data/pilot/sample-users-v2.txt (5K users)
        data/cdx-index/gig-pages-deduped.tsv
Output: data/pilot/pilot-500-users.txt
        data/pilot/pilot-500-manifest.tsv
"""

import random
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
USERS_5K = BASE_DIR / "data" / "pilot" / "sample-users-v2.txt"
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-deduped.tsv"
PILOT_DIR = BASE_DIR / "data" / "pilot"

USERS_OUT = PILOT_DIR / "pilot-500-users.txt"
MANIFEST_OUT = PILOT_DIR / "pilot-500-manifest.tsv"

SAMPLE_SIZE = 500
RANDOM_SEED = 42


def extract_seller(urlkey):
    try:
        path = urlkey.split(")/", 1)[1]
        return path.split("/", 1)[0]
    except (IndexError, ValueError):
        return ""


def main():
    # Load 5K users, subsample 500
    with open(USERS_5K) as f:
        users_5k = [line.strip() for line in f if line.strip()]

    rng = random.Random(RANDOM_SEED)
    sampled = set(rng.sample(users_5k, SAMPLE_SIZE))

    with open(USERS_OUT, "w") as f:
        for u in sorted(sampled):
            f.write(u + "\n")

    print(f"Sampled {len(sampled)} users from {len(users_5k)} qualifying")

    # Extract monthly snapshots
    print("Extracting monthly snapshots...")
    total_out = 0
    gig_urls = set()
    year_counts = defaultdict(int)
    current_urlkey = None
    seen_months = set()

    with open(INPUT, "r") as fin, open(MANIFEST_OUT, "w") as fout:
        header = fin.readline().strip()
        fout.write(header + "\n")

        for line in fin:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            urlkey = parts[0]
            timestamp = parts[1] if len(parts) > 1 else ""
            seller = extract_seller(urlkey)

            if seller not in sampled:
                continue

            if urlkey != current_urlkey:
                current_urlkey = urlkey
                seen_months = set()

            month_key = timestamp[:6]
            if month_key not in seen_months:
                seen_months.add(month_key)
                fout.write(line + "\n")
                total_out += 1
                gig_urls.add(urlkey)
                year_counts[timestamp[:4]] += 1

    est_gb = total_out * 590 / 1024 / 1024

    print()
    print(f"Users:       {len(sampled):,}")
    print(f"Gigs:        {len(gig_urls):,}")
    print(f"Snapshots:   {total_out:,}")
    print(f"Avg gigs/user: {len(gig_urls)/len(sampled):.1f}")
    print(f"Est. download: {est_gb:.1f} GB raw, ~{est_gb/3:.1f} GB compressed")
    print()
    for year in sorted(year_counts.keys()):
        print(f"  {year}: {year_counts[year]:>6,}")


if __name__ == "__main__":
    main()
