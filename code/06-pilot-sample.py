#!/usr/bin/env python3
"""
Step 2.0: Sample 5K users (sellers) for pilot test.

Strategy: sample users stratified by snapshot count (mix of high/medium/low activity)
to get a representative basket. Extract all their gig snapshots from the deduped dataset.

Uses external sort + streaming.

Input:  data/cdx-index/gig-pages-deduped.tsv
Output: data/pilot/sample-users.txt         (5K usernames)
        data/pilot/pilot-manifest.tsv        (all snapshots for sampled users)
        data/pilot/pilot-stats.txt           (summary stats)
"""

import subprocess
import sys
import random
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-deduped.tsv"
PILOT_DIR = BASE_DIR / "data" / "pilot"
PILOT_DIR.mkdir(parents=True, exist_ok=True)

USERS_OUT = PILOT_DIR / "sample-users.txt"
MANIFEST_OUT = PILOT_DIR / "pilot-manifest.tsv"
STATS_OUT = PILOT_DIR / "pilot-stats.txt"
SORTED_TMP = BASE_DIR / "data" / "cdx-index" / "pilot-sorted.tmp"

SAMPLE_SIZE = 5000
RANDOM_SEED = 42


def extract_seller(urlkey):
    """Extract seller username from urlkey like 'com,fiverr)/username/slug'."""
    try:
        path = urlkey.split(")/", 1)[1]
        return path.split("/", 1)[0]
    except (IndexError, ValueError):
        return ""


def main():
    print("PILOT SAMPLING: 5K users from deduped gig dataset")
    print()

    # Step 1: Count snapshots per user (streaming)
    print("Step 1: Counting snapshots per user...")
    user_snaps = defaultdict(int)
    user_gigs = defaultdict(set)
    total = 0

    with open(INPUT, "r") as f:
        header = f.readline().strip()
        for line in f:
            line = line.strip()
            if not line:
                continue
            total += 1
            parts = line.split("\t")
            urlkey = parts[0]
            seller = extract_seller(urlkey)
            if seller:
                user_snaps[seller] += 1
                user_gigs[seller].add(urlkey)

            if total % 5_000_000 == 0:
                print(f"  {total:,} records...")

    print(f"  Total records: {total:,}")
    print(f"  Total unique users: {len(user_snaps):,}")
    print()

    # Step 2: Stratified sampling by snapshot count
    # Divide users into terciles by snapshot count, sample proportionally
    print("Step 2: Stratified sampling...")
    all_users = list(user_snaps.keys())
    all_users.sort(key=lambda u: user_snaps[u])

    n = len(all_users)
    tercile_1 = all_users[:n // 3]           # low activity
    tercile_2 = all_users[n // 3:2 * n // 3]  # medium activity
    tercile_3 = all_users[2 * n // 3:]         # high activity

    rng = random.Random(RANDOM_SEED)

    # Sample proportionally: ~1667 from each tercile
    per_tercile = SAMPLE_SIZE // 3
    remainder = SAMPLE_SIZE - 3 * per_tercile

    s1 = rng.sample(tercile_1, min(per_tercile, len(tercile_1)))
    s2 = rng.sample(tercile_2, min(per_tercile, len(tercile_2)))
    s3 = rng.sample(tercile_3, min(per_tercile + remainder, len(tercile_3)))

    sampled = set(s1 + s2 + s3)
    print(f"  Sampled {len(sampled):,} users")
    print(f"    Low activity:    {len(s1):,} (median {user_snaps[tercile_1[len(tercile_1)//2]]} snaps)")
    print(f"    Medium activity: {len(s2):,} (median {user_snaps[tercile_2[len(tercile_2)//2]]} snaps)")
    print(f"    High activity:   {len(s3):,} (median {user_snaps[tercile_3[len(tercile_3)//2]]} snaps)")
    print()

    # Save user list
    with open(USERS_OUT, "w") as f:
        for u in sorted(sampled):
            f.write(u + "\n")

    # Step 3: Extract all snapshots for sampled users
    print("Step 3: Extracting snapshots for sampled users...")
    snap_count = 0
    gig_urls = set()
    year_counts = defaultdict(int)

    with open(INPUT, "r") as fin, open(MANIFEST_OUT, "w") as fout:
        first_line = True
        fin.seek(0)
        fout.write(fin.readline().strip() + "\n")  # header

        for line in fin:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            urlkey = parts[0]
            seller = extract_seller(urlkey)

            if seller in sampled:
                fout.write(line + "\n")
                snap_count += 1
                gig_urls.add(urlkey)
                ts = parts[1] if len(parts) > 1 else ""
                year = ts[:4] if len(ts) >= 4 else "?"
                year_counts[year] += 1

    # Compute stats for sampled users
    sampled_gig_counts = {u: len(user_gigs[u]) for u in sampled}
    multi_gig = sum(1 for u in sampled if sampled_gig_counts[u] >= 2)
    avg_gigs = sum(sampled_gig_counts.values()) / len(sampled)
    avg_snaps = snap_count / len(sampled)

    est_gb = snap_count * 590 / 1024 / 1024

    # Print & save stats
    stats = []
    def p(s=""):
        print(s)
        stats.append(s)

    p()
    p("=" * 60)
    p("PILOT SAMPLE STATS")
    p("=" * 60)
    p()
    p(f"Users sampled:      {len(sampled):,}")
    p(f"Total gigs:         {len(gig_urls):,}")
    p(f"Total snapshots:    {snap_count:,}")
    p(f"Avg gigs/user:      {avg_gigs:.1f}")
    p(f"Avg snaps/user:     {avg_snaps:.1f}")
    p(f"Users with ≥2 gigs: {multi_gig:,} ({multi_gig/len(sampled)*100:.1f}%)")
    p(f"Est. download:      {est_gb:.1f} GB raw, ~{est_gb/3:.1f} GB compressed")
    p()
    p("BY YEAR:")
    for year in sorted(year_counts.keys()):
        p(f"  {year}: {year_counts[year]:>8,}")
    p()
    p(f"Files:")
    p(f"  Users:    {USERS_OUT}")
    p(f"  Manifest: {MANIFEST_OUT}")

    with open(STATS_OUT, "w") as f:
        f.write("\n".join(stats))


if __name__ == "__main__":
    main()
