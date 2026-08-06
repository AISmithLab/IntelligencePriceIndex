#!/usr/bin/env python3
"""
Step 15: Build the tiny data.json the CSRankings-style IPI website consumes.

Reuses step 14's matched-model machinery (imported directly) to get the MONTHLY
per-category index — which step 14 computes but only ever writes as a composite.
The website needs per-category monthly index series + per-category weights so it
can recompute the composite client-side over any checked subset of categories.

Display contract (locked in plans/active/04-ipi-website.md):
  - MONTHLY cadence ("show the IPI per month").
  - TRAILING 12 MONTHS ONLY — 2024 stays on disk as matched-model anchor data but
    is not displayed. We keep the last 13 month-points so the first *change* shown
    is month-over-month into the start of the 12-month window.
  - Each category re-based to the window-start month = 100, so the chart reads as a
    clean "past-year" index and every series starts at 100. Re-basing is just a
    rescale of the matched-model relatives, so the composite formula is preserved.

Output: site/data.json  (a few KB of arrays — none of the raw HTML).
"""

import csv
import importlib.util
import json
import math
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STEP14 = BASE_DIR / "code" / "14-recent-ipi.py"
OUT = BASE_DIR / "docs" / "data.json"

WINDOW = 13  # month-points to display (12-month change + the anchor)


def load_step14():
    spec = importlib.util.spec_from_file_location("recent_ipi", STEP14)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def composite(levels_by_cat, weights, month):
    """Review-weighted geometric-mean composite over categories present this month."""
    log_sum, w_sum = 0.0, 0.0
    for cat, series in levels_by_cat.items():
        v = series.get(month)
        w = weights.get(cat, 0.0)
        if v and v > 0 and w > 0:
            log_sum += w * math.log(v)
            w_sum += w
    return math.exp(log_sum / w_sum) if w_sum > 0 else None


def build_site_data(manifest=None):
    """Assemble the site data dict. If `manifest` is given, step 14 reads its
    category labels from that file instead of the default broad manifest — this is
    how step 17 swaps in narrow subcategories while reusing all the matched-model
    machinery. Returns the data dict (caller writes it)."""
    m14 = load_step14()
    if manifest is not None:
        m14.MANIFEST_FILE = Path(manifest)
    m = m14.build(m14.to_month, m14.month_to_float, "monthly")
    if not m:
        raise SystemExit("No monthly data — is recent-prices.csv populated?")

    # Display only months with a real composite (step 14's monthly coverage gate),
    # so we never show a forward-filled phantom tail.
    real_months = sorted(m["ipi"], key=m14.month_to_float)
    months = real_months[-WINDOW:]
    anchor = months[0]

    cats = sorted(m["cat_index"])
    weights = {c: m["cat_w"].get(c, 0.0) for c in cats}
    panel_gigs = {c: len(m["cat_gigs"][c]) for c in cats}

    # Re-base each category to the anchor month = 100. Forward-fill within the
    # window so display lines stay continuous through sparse monthly transitions
    # (matched-model relatives can skip a month when <3 gig pairs exist).
    rebased = {}
    for c in cats:
        raw = m["cat_index"][c]  # {month: level}, base 2024-07=100
        base_val = raw.get(anchor)
        if not base_val:
            # fall back to first available level in the window
            for mo in months:
                if raw.get(mo):
                    base_val = raw[mo]
                    break
        if not base_val:
            continue
        series, last = {}, None
        for mo in months:
            if raw.get(mo):
                last = 100.0 * raw[mo] / base_val
            series[mo] = last  # forward-filled (None until first obs)
        rebased[c] = series

    cats = [c for c in cats if c in rebased]

    comp = {mo: composite(rebased, weights, mo) for mo in months}

    def delta12(series):
        a, b = series.get(months[0]), series.get(months[-1])
        return (b / a - 1) * 100 if a and b and a > 0 else None

    delta = {c: delta12(rebased[c]) for c in cats}
    delta["composite"] = delta12(comp)

    data = {
        "generated": date.today().isoformat(),
        "base_month": anchor,
        "window_months": WINDOW,
        "categories": cats,
        "weights": {c: round(weights[c], 6) for c in cats},
        "panel_gigs": panel_gigs,
        "months": months,
        "index": {c: [round(rebased[c][mo], 2) if rebased[c][mo] else None
                      for mo in months] for c in cats},
        "composite_all": [round(comp[mo], 2) if comp[mo] else None for mo in months],
        "delta12": {k: (round(v, 1) if v is not None else None) for k, v in delta.items()},
    }
    return data


def write_and_report(data, out=OUT):
    months, cats, delta = data["months"], data["categories"], data["delta12"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Wrote {out}  ({out.stat().st_size/1024:.1f} KB)")
    print(f"Window: {months[0]} -> {months[-1]} ({len(months)} months), anchor {data['base_month']}=100")
    print(f"Categories ({len(cats)}): {', '.join(cats)}")
    comp = data["composite_all"]
    print(f"\nComposite (all categories):")
    for mo, v in zip(months, comp):
        bar = "#" * int(v / 3) if v else ""
        print(f"  {mo}  {v:7.1f}  {bar}" if v else f"  {mo}    n/a")
    print(f"\nComposite trailing-12mo: {delta.get('composite'):+.1f}%")
    print("Per-category trailing-12mo:")
    for c in sorted(cats, key=lambda x: delta[x] if delta[x] is not None else 0):
        d = delta[c]
        print(f"  {c:<22} {d:+6.1f}%" if d is not None else f"  {c:<22}   n/a")


def main():
    write_and_report(build_site_data())


if __name__ == "__main__":
    main()
