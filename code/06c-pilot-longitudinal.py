#!/usr/bin/env python3
"""
Revised pilot sampling: focus on users with longitudinal depth.

Criteria:
- User must have at least 1 gig with ≥5 monthly snapshots spanning ≥2 years
- Sample 5K such users
- Keep ~1 snapshot/month per gig

Input:  data/cdx-index/gig-pages-deduped.tsv
Output: data/pilot/pilot-manifest-v2.tsv
"""

import subprocess
import random
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-deduped.tsv"
PILOT_DIR = BASE_DIR / "data" / "pilot"
PILOT_DIR.mkdir(parents=True, exist_ok=True)
SORTED_TMP = BASE_DIR / "data" / "cdx-index" / "pilot-v2-sorted.tmp"

SAMPLE_SIZE = 5000
RANDOM_SEED = 42
MIN_MONTHLY_SNAPS = 5
MIN_YEAR_SPAN = 2


def extract_seller(urlkey):
    try:
        path = urlkey.split(")/", 1)[1]
        return path.split("/", 1)[0]
    except (IndexError, ValueError):
        return ""


def main():
    print("Revised pilot: users with longitudinal depth")
    print(f"  Criteria: ≥1 gig with ≥{MIN_MONTHLY_SNAPS} unique months spanning ≥{MIN_YEAR_SPAN} years")
    print()

    # Step 1: Sort by urlkey + timestamp
    print("Step 1: Sorting...")
    tmp_dir = BASE_DIR / "data" / "cdx-index" / "sort-tmp"
    tmp_dir.mkdir(exist_ok=True)

    with open(INPUT, "r") as f:
        header = f.readline().strip()

    sort_cmd = (
        f"tail -n +2 '{INPUT}' | "
        f"sort -t'\t' -k1,1 -k2,2 -T '{tmp_dir}' -S 1G > '{SORTED_TMP}'"
    )
    subprocess.run(sort_cmd, shell=True, check=True)

    # Step 2: Stream through sorted file, identify qualifying users
    print("Step 2: Identifying qualifying users...")

    # For each gig (urlkey), compute unique months and year span
    # Track which users have at least one qualifying gig
    qualifying_users = set()
    user_gig_count = defaultdict(int)
    total_users = set()

    current_urlkey = None
    current_months = set()
    current_years = set()
    records_processed = 0

    with open(SORTED_TMP, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records_processed += 1
            parts = line.split("\t")
            urlkey = parts[0]
            timestamp = parts[1] if len(parts) > 1 else ""
            seller = extract_seller(urlkey)

            if not seller:
                continue
            total_users.add(seller)

            if urlkey != current_urlkey:
                # Check previous gig
                if current_urlkey is not None:
                    prev_seller = extract_seller(current_urlkey)
                    user_gig_count[prev_seller] += 1
                    if (len(current_months) >= MIN_MONTHLY_SNAPS and
                            len(current_years) >= 2 and
                            max(current_years) - min(current_years) >= MIN_YEAR_SPAN):
                        qualifying_users.add(prev_seller)
                current_urlkey = urlkey
                current_months = set()
                current_years = set()

            month = timestamp[:6]  # YYYYMM
            year = int(timestamp[:4]) if len(timestamp) >= 4 else 0
            current_months.add(month)
            if year > 0:
                current_years.add(year)

            if records_processed % 5_000_000 == 0:
                print(f"  {records_processed:,} records...")

        # Last gig
        if current_urlkey is not None:
            prev_seller = extract_seller(current_urlkey)
            user_gig_count[prev_seller] += 1
            if (len(current_months) >= MIN_MONTHLY_SNAPS and
                    len(current_years) >= 2 and
                    max(current_years) - min(current_years) >= MIN_YEAR_SPAN):
                qualifying_users.add(prev_seller)

    print(f"  Total users: {len(total_users):,}")
    print(f"  Qualifying users: {len(qualifying_users):,}")
    print()

    # Step 3: Sample 5K from qualifying users
    print("Step 3: Sampling...")
    rng = random.Random(RANDOM_SEED)
    if len(qualifying_users) <= SAMPLE_SIZE:
        sampled = qualifying_users
        print(f"  Only {len(qualifying_users):,} qualifying — taking all")
    else:
        sampled = set(rng.sample(sorted(qualifying_users), SAMPLE_SIZE))
        print(f"  Sampled {len(sampled):,} from {len(qualifying_users):,} qualifying users")

    # Save user list
    with open(PILOT_DIR / "sample-users-v2.txt", "w") as f:
        for u in sorted(sampled):
            f.write(u + "\n")

    # Step 4: Second pass — extract monthly snapshots for sampled users
    print("Step 4: Extracting monthly snapshots for sampled users...")

    total_out = 0
    gig_urls = set()
    year_counts = defaultdict(int)

    current_urlkey = None
    seen_months = set()

    with open(SORTED_TMP, "r") as fin, \
         open(PILOT_DIR / "pilot-manifest-v2.tsv", "w") as fout:
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
                year = timestamp[:4] if len(timestamp) >= 4 else "?"
                year_counts[year] += 1

    # Clean up
    SORTED_TMP.unlink(missing_ok=True)
    try:
        tmp_dir.rmdir()
    except OSError:
        pass

    est_gb = total_out * 590 / 1024 / 1024
    multi_gig = sum(1 for u in sampled if user_gig_count.get(u, 0) >= 2)

    print()
    print("=" * 60)
    print("PILOT v2 STATS")
    print("=" * 60)
    print()
    print(f"Users:              {len(sampled):,}")
    print(f"Gigs:               {len(gig_urls):,}")
    print(f"Snapshots (monthly):{total_out:,}")
    print(f"Avg gigs/user:      {len(gig_urls)/len(sampled):.1f}")
    print(f"Avg snaps/gig:      {total_out/len(gig_urls):.1f}")
    print(f"Users with ≥2 gigs: {multi_gig:,} ({multi_gig/len(sampled)*100:.1f}%)")
    print(f"Est. download:      {est_gb:.1f} GB raw, ~{est_gb/3:.1f} GB compressed")
    print()
    print("BY YEAR:")
    for year in sorted(year_counts.keys()):
        print(f"  {year}: {year_counts[year]:>8,}")
    print()
    print(f"Output: {PILOT_DIR / 'pilot-manifest-v2.tsv'}")


if __name__ == "__main__":
    main()
