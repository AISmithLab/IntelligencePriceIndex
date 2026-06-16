#!/usr/bin/env python3
"""
Step 1.6: Generate download manifest statistics.

Reports: total gigs, total snapshots, by category, by year, estimated download size.

Input:  data/cdx-index/download-manifest.tsv
Output: runs/archive-download/manifest-stats.md
"""

from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "download-manifest.tsv"
OUTPUT = BASE_DIR / "runs" / "archive-download" / "manifest-stats.md"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

AVG_PAGE_SIZE_KB = 590  # from pilot


def normalize_url(url):
    url = url.split("?")[0].split("#")[0]
    url = url.replace("://www.", "://")
    if url.startswith("http://"):
        url = "https://" + url[7:]
    return url.rstrip("/")


def main():
    print("Generating manifest statistics...")

    total_records = 0
    gig_urls = set()
    category_records = defaultdict(int)
    category_gigs = defaultdict(set)
    year_records = defaultdict(int)
    year_gigs = defaultdict(set)

    with open(INPUT, "r") as f:
        header = f.readline()
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_records += 1
            parts = line.split("\t")

            timestamp = parts[1] if len(parts) > 1 else ""
            original = parts[2] if len(parts) > 2 else ""
            category = parts[6] if len(parts) > 6 else "unknown"

            base_url = normalize_url(original)
            gig_urls.add(base_url)

            category_records[category] += 1
            category_gigs[category].add(base_url)

            year = timestamp[:4] if len(timestamp) >= 4 else "unknown"
            year_records[year] += 1
            year_gigs[year].add(base_url)

    total_gigs = len(gig_urls)
    est_size_gb = total_records * AVG_PAGE_SIZE_KB / 1024 / 1024

    # Determine action per decision gate
    if total_records < 500_000:
        action = "Download all categories"
        gate = "< 500K snapshots"
    elif total_records < 2_000_000:
        action = "Download Tier 1 categories (writing, coding, design, translation)"
        gate = "500K – 2M snapshots"
    else:
        action = "Further filter: top-50K gigs by snapshot count, or sample within categories"
        gate = "> 2M snapshots"

    # Build report
    lines = []
    lines.append("# Download Manifest Statistics")
    lines.append(f"\n**Generated:** 2026-03-22")
    lines.append(f"**Input:** `{INPUT.relative_to(BASE_DIR)}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total gig URLs | {total_gigs:,} |")
    lines.append(f"| Total snapshots | {total_records:,} |")
    lines.append(f"| Avg snapshots/gig | {total_records/total_gigs:.1f} |")
    lines.append(f"| Estimated download size | {est_size_gb:.0f} GB (raw HTML) |")
    lines.append(f"| Estimated compressed | {est_size_gb/3:.0f} GB (gzip ~3:1) |")
    lines.append("")
    lines.append("## Decision Gate")
    lines.append("")
    lines.append(f"| Gate | Action |")
    lines.append(f"|------|--------|")
    lines.append(f"| {gate} | **{action}** |")
    lines.append("")
    lines.append("## By Category")
    lines.append("")
    lines.append("| Category | Gigs | Snapshots | % of total | Est. size (GB) |")
    lines.append("|----------|------|-----------|-----------|----------------|")
    for cat in sorted(category_records.keys(), key=lambda x: -category_records[x]):
        recs = category_records[cat]
        gigs = len(category_gigs[cat])
        pct = recs / total_records * 100
        size = recs * AVG_PAGE_SIZE_KB / 1024 / 1024
        lines.append(f"| {cat} | {gigs:,} | {recs:,} | {pct:.1f}% | {size:.0f} |")
    lines.append("")

    # Tier 1 subtotal
    tier1_cats = {"writing", "coding", "design", "translation"}
    tier1_recs = sum(category_records.get(c, 0) for c in tier1_cats)
    tier1_gigs = len(set().union(*(category_gigs.get(c, set()) for c in tier1_cats)))
    tier1_size = tier1_recs * AVG_PAGE_SIZE_KB / 1024 / 1024
    lines.append(f"**Tier 1 subtotal:** {tier1_gigs:,} gigs, {tier1_recs:,} snapshots, ~{tier1_size:.0f} GB")
    lines.append("")

    lines.append("## By Year")
    lines.append("")
    lines.append("| Year | Gigs active | Snapshots | % of total |")
    lines.append("|------|------------|-----------|-----------|")
    for year in sorted(year_records.keys()):
        recs = year_records[year]
        gigs = len(year_gigs[year])
        pct = recs / total_records * 100
        lines.append(f"| {year} | {gigs:,} | {recs:,} | {pct:.1f}% |")
    lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    lines.append(f"Based on the decision gate ({gate}):")
    lines.append(f"- **Recommended action:** {action}")
    if tier1_recs > 0:
        lines.append(f"- Tier 1 categories alone: {tier1_recs:,} snapshots (~{tier1_size:.0f} GB)")
    lines.append("")

    report = "\n".join(lines)

    with open(OUTPUT, "w") as f:
        f.write(report)

    print(report)
    print(f"\nReport saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
