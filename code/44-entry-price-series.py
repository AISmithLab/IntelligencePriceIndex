#!/usr/bin/env python3
"""
Step 44: the entry-price series, built inside a single crawl.

WHY THIS EXISTS. S6.2 calls the entry-price gap "the paper's most serious
unresolved threat": new gigs (<=10 reviews at first capture) enter at flat
prices while the matched index of incumbents climbs, which would mean the index
measures the life-cycle of surviving gigs rather than the price of the service.
The paper cannot settle it because the two original crawls return different
entry medians for the same year ($50 on n=102 versus $30 on n=2,389), so S6.2
states the requirement: "the series must be built within a crawl or the frames
reconciled first."

The balanced historical collection is a single frame spanning 2018Q3-2026Q1
(39,933 gigs, 292,447 priced rows), so the series can now be built within one
crawl. That is what this script does.

WHAT IT DOES NOT SETTLE. The manifest is quota-sampled on (category, adjacent
quarter pair), not on gigs, so "first capture" is still bounded by the window at
both edges: a gig alive before 2018Q3 is recorded as entering in the first
quarter it happens to be sampled. The script therefore prints the first-capture
distribution alongside the price series, and the cohorts within a few quarters of
either edge must be read as truncated rather than as entry. This is a measurement
of what the new frame supports, not a decomposition of the index.

Run:  python3 code/44-entry-price-series.py [--max-reviews 10]
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PILOT = BASE_DIR / "data" / "pilot"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gigfilter import is_gig  # noqa: E402

PRICES = PILOT / "balanced-prices.csv"
MANIFEST = PILOT / "balanced-manifest-1200.tsv"
CATS = ["audio", "coding", "design", "marketing", "translation", "video", "writing"]
PRICE_MAX = 10000.0


def quarter(y, m):
    try:
        y, m = int(y), int(m)
    except (TypeError, ValueError):
        return None
    if not (1 <= m <= 12) or not (2010 <= y <= 2030):
        return None
    return f"{y}Q{(m - 1) // 3 + 1}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-reviews", type=int, default=10,
                    help="a gig is 'new' at first capture if reviews <= this (S6.2 uses 10)")
    args = ap.parse_args()

    gig_cat = {}
    with open(MANIFEST) as f:
        for row in csv.DictReader(f, delimiter="\t"):
            parts = row.get("gig_id", "").split("/", 1)
            if len(parts) == 2:
                gig_cat[(parts[0], parts[1])] = row.get("category", "")

    # first capture per gig: earliest (year, month) carrying a usable price
    first = {}
    with open(PRICES) as f:
        for row in csv.DictReader(f):
            if not is_gig(row["seller"]):
                continue
            key = (row["seller"], row["slug"])
            if gig_cat.get(key) not in CATS:
                continue
            try:
                price = float(row.get("price_basic", 0) or 0)
            except ValueError:
                continue
            if price <= 0 or price > PRICE_MAX:
                continue
            q = quarter(row["year"], row["month"])
            if not q:
                continue
            stamp = (int(row["year"]), int(row["month"]))
            prev = first.get(key)
            if prev is None or stamp < prev[0]:
                rc = row.get("review_count", "")
                try:
                    rc = int(float(rc)) if rc not in ("", None) else None
                except ValueError:
                    rc = None
                first[key] = (stamp, q, price, rc, row.get("extraction_method", "?"))

    print(f"gigs with a first capture: {len(first):,}")
    known = [v for v in first.values() if v[3] is not None]
    print(f"  of which review_count is readable: {len(known):,} ({100*len(known)/len(first):.1f}%)")

    new = {k: v for k, v in first.items() if v[3] is not None and v[3] <= args.max_reviews}
    print(f"  of which 'new' at first capture (<= {args.max_reviews} reviews): {len(new):,}")

    # --- the extraction-path check that invalidates the pre-2020 cohorts ----
    # `review_count` is only reliable where the packageList blob supplies it. On
    # pre-2020 layouts the extractor falls through to dollar_fallback/old_json,
    # which report review counts erratically, so a "<=10 reviews" filter there
    # selects on parse failure rather than on newness. Measured below.
    print("\nEXTRACTION PATH OF THE 'NEW' COHORT, by first-capture year")
    print(f"  {'year':<6} {'n':>6}  {'packageList':>12}  {'median $':>9}  "
          f"{'median $ (packageList only)':>28}")
    by_year_meth = defaultdict(lambda: defaultdict(list))
    for (_, q, price, _, meth) in new.values():
        by_year_meth[q[:4]][meth].append(price)
    clean_years = set()
    for y in sorted(by_year_meth):
        meths = by_year_meth[y]
        allp = [p for ps in meths.values() for p in ps]
        pl = meths.get("packageList", [])
        share = len(pl) / len(allp) if allp else 0
        if share >= 0.95:
            clean_years.add(y)
        pltxt = f"{np.median(pl):.0f} (n={len(pl)})" if len(pl) >= 10 else "-"
        flag = "" if share >= 0.95 else "   <-- CONTAMINATED"
        print(f"  {y:<6} {len(allp):>6}  {share:>11.1%}  {np.median(allp):>9.0f}  "
              f"{pltxt:>28}{flag}")
    print(f"  Years where packageList supplies >=95% of the cohort: "
          f"{', '.join(sorted(clean_years)) or 'none'}")
    print("  Only those years are interpretable as entry prices.")

    # --- truncation profile: where do first captures land? -----------------
    print("\nFIRST-CAPTURE DISTRIBUTION (the truncation check S6.3 demands)")
    per_q = defaultdict(int)
    for _, q, _, _, _ in first.values():
        per_q[q] += 1
    qs = sorted(per_q, key=lambda s: (int(s[:4]), int(s[-1])))
    tot = sum(per_q.values())
    for q in qs:
        bar = "#" * int(60 * per_q[q] / max(per_q.values()))
        print(f"  {q}  {per_q[q]:>6,} ({100*per_q[q]/tot:>5.1f}%)  {bar}")

    # --- entry price by cohort year and category ---------------------------
    print(f"\nMEDIAN ENTRY PRICE, gigs with <= {args.max_reviews} reviews at first capture")
    print("  (packageList first captures only; contaminated years above are excluded)")
    by = defaultdict(list)
    cat_year = defaultdict(list)
    for k, (_, q, price, _, meth) in new.items():
        if meth != "packageList" or q[:4] not in clean_years:
            continue
        by[q].append(price)
        cat_year[(gig_cat[k], q[:4])].append(price)

    years = sorted({q[:4] for q in by})
    print(f"\n{'category':<12} " + " ".join(f"{y:>10}" for y in years))
    out = {}
    for cat in CATS:
        cells = []
        for y in years:
            v = cat_year.get((cat, y), [])
            cells.append(f"{np.median(v):>6.0f} ({len(v):>3})" if len(v) >= 10 else f"{'-':>10}")
            if len(v) >= 10:
                out.setdefault(cat, {})[y] = {"median": float(np.median(v)), "n": len(v)}
        print(f"{cat:<12} " + " ".join(cells))

    allq = {y: [p for (c, yy), ps in cat_year.items() if yy == y for p in ps] for y in years}
    print(f"\n{'ALL':<12} " + " ".join(
        f"{np.median(allq[y]):>6.0f} ({len(allq[y]):>3})" if allq[y] else f"{'-':>10}"
        for y in years))

    dest = PILOT / "entry-price-series.json"
    dest.write_text(json.dumps(
        {"max_reviews": args.max_reviews,
         "n_first_capture": len(first), "n_new": len(new),
         "first_capture_by_quarter": dict(per_q),
         "entry_median_by_cat_year": out,
         "entry_median_all": {y: {"median": float(np.median(allq[y])), "n": len(allq[y])}
                              for y in years if allq[y]}}, indent=1))
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
