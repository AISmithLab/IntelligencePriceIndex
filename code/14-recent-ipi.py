#!/usr/bin/env python3
"""
Step 14: Trailing-12-month Intelligence Price Index (CPI-style "past year").

Builds a matched-model price index over the recent window (2024Q3 onward) from
the recent-window snapshots downloaded in step 08, across all viable Fiverr
categories, and reports the trailing-12-month change per category and composite.

Method mirrors the panel IPI (step 12): within-gig price relatives, Jevons
(geometric-mean) elementary aggregates per category, review-weighted
Törnqvist-style composite. Differences:
  - Input is recent-prices.csv (the recent-window extraction), not pilot-prices.csv.
  - Category is taken authoritatively from recent-manifest.tsv (CDX-classified),
    not re-derived from gig titles.
  - The chain is based at the FIRST period present in the window = 100, so the
    series reads directly as a recent-window index. The headline is the change
    over the trailing 4 quarters (≈ last 12 months).
  - Both a quarterly index (primary, robust) and a monthly index (CPI cadence,
    where monthly coverage supports it) are produced.

Inputs:
  data/pilot/recent-prices.csv     (seller, slug, year, month, price_basic, review_count, ...)
  data/pilot/recent-manifest.tsv   (timestamp, original, category, gig_id, month)
Outputs:
  data/pilot/recent-ipi.csv               (period, ipi)  -- quarterly composite
  data/pilot/recent-category-indices.csv  (quarter, <cat>...)
  data/pilot/recent-ipi-monthly.csv       (month, ipi)   -- if monthly coverage suffices
  data/pilot/recent-ipi-summary.md
"""

import argparse
import csv
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PRICES_FILE = BASE_DIR / "data" / "pilot" / "recent-prices.csv"
MANIFEST_FILE = BASE_DIR / "data" / "pilot" / "recent-manifest.tsv"

OUT_IPI = BASE_DIR / "data" / "pilot" / "recent-ipi.csv"
OUT_CAT = BASE_DIR / "data" / "pilot" / "recent-category-indices.csv"
OUT_WEIGHTS = BASE_DIR / "data" / "pilot" / "recent-category-weights.csv"
OUT_MONTHLY = BASE_DIR / "data" / "pilot" / "recent-ipi-monthly.csv"
OUT_SUMMARY = BASE_DIR / "data" / "pilot" / "recent-ipi-summary.md"

# Matched-model parameters
REL_LO, REL_HI = 0.1, 10.0      # drop within-gig relatives outside this band
MIN_RELATIVES = 3               # min gig relatives to accept a period transition
MIN_WEIGHT_COVER = 0.30         # min summed category weight to publish a composite point
PRICE_MAX = 10000.0             # sanity cap on basic price


def to_quarter(year, month):
    try:
        y, m = int(year), int(month)
        return f"{y}Q{(m - 1) // 3 + 1}"
    except (ValueError, TypeError):
        return None


def quarter_to_float(q):
    return int(q[:4]) + (int(q[-1]) - 1) * 0.25


def to_month(year, month):
    try:
        return f"{int(year):04d}-{int(month):02d}"
    except (ValueError, TypeError):
        return None


def month_to_float(m):
    y, mm = int(m[:4]), int(m[5:7])
    return y + (mm - 1) / 12.0


def load_categories():
    """gig_id (seller/slug) -> category, from the CDX-classified manifest."""
    cat = {}
    with open(MANIFEST_FILE) as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            cat[row["gig_id"]] = row["category"]
    return cat


def build_panel(period_fn):
    """Return gig -> {period -> median basic price}, gig -> category, gig -> max_reviews.

    period_fn(year, month) yields the period key (quarter or month).
    Category comes from the manifest; gigs not in the manifest are skipped.
    """
    gig_cat = load_categories()
    gig_period = defaultdict(lambda: defaultdict(list))
    gig_reviews = defaultdict(int)
    used_cat = {}

    with open(PRICES_FILE) as f:
        for row in csv.DictReader(f):
            gid = f"{row['seller']}/{row['slug']}"
            cat = gig_cat.get(gid)
            if not cat:
                continue
            try:
                price = float(row.get("price_basic") or 0)
            except ValueError:
                continue
            if not (0 < price <= PRICE_MAX):
                continue
            period = period_fn(row["year"], row["month"])
            if not period:
                continue
            gig_period[gid][period].append(price)
            used_cat[gid] = cat
            try:
                rv = int(row.get("review_count") or 0)
            except ValueError:
                rv = 0
            gig_reviews[gid] = max(gig_reviews[gid], rv)

    panel = {}
    for gid, periods in gig_period.items():
        panel[gid] = {p: float(np.median(v)) for p, v in periods.items()}
    return panel, used_cat, gig_reviews


def chain_category(gigs, panel, all_periods, period_order, base_period):
    """Matched-model Jevons chain for one category. Returns {period -> index}."""
    rel = defaultdict(list)  # period -> list of within-gig relatives into that period
    for gid in gigs:
        ps = sorted(panel[gid].keys(), key=period_order)
        for i in range(1, len(ps)):
            p_prev, p_curr = ps[i - 1], ps[i]
            v_prev, v_curr = panel[gid][p_prev], panel[gid][p_curr]
            if v_prev > 0:
                r = v_curr / v_prev
                if REL_LO <= r <= REL_HI:
                    rel[(p_prev, p_curr)].append(r)

    # Aggregate relatives keyed by the destination period, but only for
    # adjacent-in-window transitions so the chain is well defined.
    index = {base_period: 100.0}
    ordered = sorted(all_periods, key=period_order)
    for i in range(1, len(ordered)):
        prev_p, curr_p = ordered[i - 1], ordered[i]
        rels = rel.get((prev_p, curr_p), [])
        if len(rels) >= MIN_RELATIVES and prev_p in index:
            geo = math.exp(float(np.mean(np.log(rels))))
            index[curr_p] = index[prev_p] * geo
    # Backward fill before base if base isn't the earliest
    for i in range(len(ordered) - 2, -1, -1):
        prev_p, curr_p = ordered[i], ordered[i + 1]
        if curr_p in index and prev_p not in index:
            rels = rel.get((prev_p, curr_p), [])
            if len(rels) >= MIN_RELATIVES:
                geo = math.exp(float(np.mean(np.log(rels))))
                index[prev_p] = index[curr_p] / geo
    return index


def composite(cat_index, cat_weights, all_periods, period_order):
    """Review-weighted geometric-mean composite across categories."""
    ipi = {}
    for p in sorted(all_periods, key=period_order):
        log_sum, w_sum = 0.0, 0.0
        for cat, idx in cat_index.items():
            if p in idx and cat in cat_weights:
                w = cat_weights[cat]
                log_sum += w * math.log(idx[p])
                w_sum += w
        if w_sum > MIN_WEIGHT_COVER:
            ipi[p] = math.exp(log_sum / w_sum)
    return ipi


def build(period_fn, period_order, label):
    panel, gig_cat, gig_reviews = build_panel(period_fn)
    # Panel gigs: observed in >= 2 periods
    panel = {g: v for g, v in panel.items() if len(v) >= 2}
    all_periods = sorted({p for v in panel.values() for p in v}, key=period_order)
    if not all_periods:
        return None

    cat_gigs = defaultdict(list)
    for g in panel:
        cat_gigs[gig_cat[g]].append(g)

    base_period = all_periods[0]
    cat_index = {}
    for cat, gigs in cat_gigs.items():
        idx = chain_category(gigs, panel, all_periods, period_order, base_period)
        if len(idx) >= 2:
            cat_index[cat] = idx

    # Weights: total max-reviews per category (volume proxy), normalized
    cat_w = {c: sum(gig_reviews[g] for g in cat_gigs[c]) for c in cat_index}
    tot = sum(cat_w.values()) or 1
    cat_w = {c: w / tot for c, w in cat_w.items()}

    ipi = composite(cat_index, cat_w, all_periods, period_order)
    return {
        "label": label, "periods": all_periods, "base": base_period,
        "panel_n": len(panel), "cat_gigs": cat_gigs, "cat_index": cat_index,
        "cat_w": cat_w, "ipi": ipi,
    }


def trailing_change(series, periods, n_back):
    """% change of series over the last n_back steps within `periods`."""
    pts = [p for p in periods if p in series]
    if len(pts) < 2:
        return None, None, None
    end = pts[-1]
    start_idx = max(0, len(pts) - 1 - n_back)
    start = pts[start_idx]
    if series[start] <= 0:
        return None, start, end
    return (series[end] / series[start] - 1) * 100, start, end


def main():
    global PRICES_FILE, MANIFEST_FILE
    ap = argparse.ArgumentParser()
    ap.add_argument("--prices", type=Path, default=PRICES_FILE)
    ap.add_argument("--manifest", type=Path, default=MANIFEST_FILE)
    args = ap.parse_args()
    PRICES_FILE, MANIFEST_FILE = args.prices, args.manifest

    print("=" * 60)
    print("TRAILING-12-MONTH INTELLIGENCE PRICE INDEX")
    print("=" * 60)

    q = build(to_quarter, quarter_to_float, "quarterly")
    if not q:
        print("No quarterly data — is recent-prices.csv populated?")
        return
    m = build(to_month, month_to_float, "monthly")

    qp = q["periods"]
    print(f"\nQuarterly panel gigs (≥2 quarters): {q['panel_n']:,}")
    print(f"Window: {qp[0]} → {qp[-1]} ({len(qp)} quarters), base {q['base']}=100")
    print("\nCategory panel sizes / weights:")
    for c in sorted(q["cat_index"]):
        print(f"  {c:<14} {len(q['cat_gigs'][c]):>5} gigs   w={q['cat_w'].get(c,0):.3f}")

    print("\nComposite IPI (quarterly, base=100):")
    for p in sorted(q["ipi"], key=quarter_to_float):
        bar = "█" * int(q["ipi"][p] / 5)
        print(f"  {p}  {q['ipi'][p]:>7.1f}  {bar}")

    # ── Trailing-12-month headline ────────────────────────────────
    comp_chg, c_start, c_end = trailing_change(q["ipi"], qp, 4)
    print("\n" + "=" * 60)
    print("TRAILING-12-MONTH CHANGE (last 4 quarters)")
    print("=" * 60)
    if comp_chg is not None:
        print(f"  Composite IPI: {c_start} → {c_end}: {comp_chg:+.1f}%")

    cat_rows = []
    for c in sorted(q["cat_index"]):
        chg, s, e = trailing_change(q["cat_index"][c], qp, 4)
        if chg is not None:
            cat_rows.append((c, chg, s, e, q["cat_w"].get(c, 0)))
    cat_rows.sort(key=lambda r: r[1])
    print(f"\n  {'Category':<14} {'Δ12mo':>8}   window")
    for c, chg, s, e, w in cat_rows:
        print(f"  {c:<14} {chg:>+7.1f}%   {s}→{e}")

    # ── Write outputs ─────────────────────────────────────────────
    with open(OUT_IPI, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quarter", "ipi"])
        for p in sorted(q["ipi"], key=quarter_to_float):
            w.writerow([p, f"{q['ipi'][p]:.2f}"])

    with open(OUT_CAT, "w", newline="") as f:
        w = csv.writer(f)
        cats = sorted(q["cat_index"])
        w.writerow(["quarter"] + cats)
        for p in qp:
            w.writerow([p] + [f"{q['cat_index'][c][p]:.2f}" if p in q["cat_index"][c] else ""
                              for c in cats])

    # Per-category weights (volume proxy) so the website can recompute the
    # review-weighted composite client-side over any checked subset of categories.
    with open(OUT_WEIGHTS, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "weight", "panel_gigs"])
        for c in sorted(q["cat_index"]):
            w.writerow([c, f"{q['cat_w'].get(c, 0):.6f}", len(q["cat_gigs"][c])])

    monthly_published = False
    if m and len(m["ipi"]) >= 6:
        monthly_published = True
        with open(OUT_MONTHLY, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["month", "ipi"])
            for p in sorted(m["ipi"], key=month_to_float):
                w.writerow([p, f"{m['ipi'][p]:.2f}"])

    # ── Summary markdown ──────────────────────────────────────────
    lines = [
        "# Trailing-12-Month Intelligence Price Index — Summary",
        "",
        f"**Generated:** {date.today().isoformat()}",
        "**Method:** Matched-model panel (Jevons elementary, review-weighted Törnqvist composite)",
        f"**Source:** recent-window snapshots ({qp[0]}–{qp[-1]}), categories from CDX classification",
        f"**Quarterly panel gigs:** {q['panel_n']:,} (observed in ≥2 quarters)",
        f"**Base:** {q['base']} = 100",
        "",
        "## Headline — Trailing 12 Months (last 4 quarters)",
        "",
    ]
    if comp_chg is not None:
        lines.append(f"- **Composite IPI {c_start}→{c_end}: {comp_chg:+.1f}%**")
    lines += [
        "",
        "## Trailing-12-Month Change by Category",
        "",
        "| Category | Δ12mo | Window | Weight | Panel gigs |",
        "|----------|-------|--------|--------|-----------|",
    ]
    for c, chg, s, e, w in cat_rows:
        lines.append(f"| {c} | {chg:+.1f}% | {s}→{e} | {w:.3f} | {len(q['cat_gigs'][c])} |")

    lines += ["", "## Quarterly Composite IPI", "", "| Quarter | IPI |", "|---------|-----|"]
    for p in sorted(q["ipi"], key=quarter_to_float):
        lines.append(f"| {p} | {q['ipi'][p]:.1f} |")

    lines += ["", "## Category Indices (quarterly)", "",
              "| Quarter | " + " | ".join(sorted(q["cat_index"])) + " |",
              "|" + "---|" * (len(q["cat_index"]) + 1)]
    for p in qp:
        cells = [f"{q['cat_index'][c][p]:.1f}" if p in q["cat_index"][c] else "·"
                 for c in sorted(q["cat_index"])]
        lines.append(f"| {p} | " + " | ".join(cells) + " |")

    if monthly_published:
        lines += ["", "## Monthly Composite IPI (CPI cadence)", "",
                  "| Month | IPI |", "|-------|-----|"]
        for p in sorted(m["ipi"], key=month_to_float):
            lines.append(f"| {p} | {m['ipi'][p]:.1f} |")

    with open(OUT_SUMMARY, "w") as f:
        f.write("\n".join(lines))

    print("\nWrote:")
    print(f"  {OUT_IPI}")
    print(f"  {OUT_CAT}")
    if monthly_published:
        print(f"  {OUT_MONTHLY}")
    print(f"  {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
