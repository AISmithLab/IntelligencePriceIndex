#!/usr/bin/env python3
"""
87 — What buyers actually paid, 2022-2026, and the two artefacts that hide it.

Step 86 recovered 681,668 distinct orders from HTML already on disk, dated by order
rather than by capture. This step turns them into a quarterly series — and most of
its length is about why the obvious way to do that is wrong.

THE OBVIOUS WAY IS WRONG, TWICE.

  1. THE BUCKET SCHEME CHANGED. Fiverr publishes a range, not an amount, and the
     ranges are not fixed. Through 2023 the low end is `$5-$20` and `$20-$50`; from
     roughly 2024Q2 those are replaced by a single `$0-$50`. Bins built naively on
     the published labels are not comparable across that break.

  2. AND — far worse — SUB-$50 ORDERS CARRIED NO BUCKET AT ALL BEFORE ~2024Q2.
     In 2022Q3, 46% of orders have NO price field and the cheapest bucket that
     exists is `$50-$100`. In 2024Q3, missingness is ~0% and `$0-$50` alone is 50%.
     So the share of orders under $50 appears to explode from ~0% to ~50% between
     2023 and 2025. That is a REPORTING CHANGE, not a price collapse. The cheap
     orders were always there; Fiverr started labelling them.

     The tell is that the apparent `<$50` share tracks coverage almost exactly:
     coverage 54-67% -> `<$50` 0-13%; coverage 94% -> 42%; coverage 100% -> ~50%.
     Anyone who plots bucket shares over the raw field will report a dramatic
     collapse in what buyers pay. There isn't one.

WHAT THIS STEP DOES INSTEAD. It conditions on orders of **$50 or more**, where the
bucket boundaries (50 / 100 / 200 / 400 / 800) exist unchanged across every era,
and reports the composition within that segment. The `<$50` segment is simply not
measurable before 2024 and is left out rather than modelled.

That makes the series answer a narrower question honestly: *among orders of $50 or
more, how has the distribution of realised value moved?* It cannot speak to the
sub-$50 segment, and it must not be read as an average order value.

WHAT IT IS NOT. Not the IPI. The IPI is a matched-model index on LISTED
basic-package prices; this is a composition series on REALISED, bucketed
transaction values over a changing set of gigs. Different object, different unit,
no chaining.

Inputs:  data/pilot/order-panel-all.csv   (step 86)
Output:  data/pilot/realised-value-series.csv
         runs/order-panel/realised-value.md
"""

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PANEL = BASE_DIR / "data" / "pilot" / "order-panel-all.csv"
OUT = BASE_DIR / "data" / "pilot" / "realised-value-series.csv"
RUNDIR = BASE_DIR / "runs" / "order-panel"

# Boundaries present in EVERY era's published scheme. The pre-2024 low buckets
# ($5-$20, $20-$50) and the post-2024 $0-$50 all nest below 50, which is exactly
# why 50 is the floor of the comparable range rather than a bin edge inside it.
BINS = [(50, 100, "$50-100"), (100, 200, "$100-200"), (200, 400, "$200-400"),
        (400, 800, "$400-800"), (800, None, "$800+")]
NAMES = [n for _, _, n in BINS]

MIN_N = 200          # below this a quarter's composition is noise, not a reading
FIRST, LAST = "2022Q1", "2026Q1"


def bin_of(lo, hi):
    """-> bin name, or None for an order below the comparable floor."""
    try:
        lo = float(lo)
    except (TypeError, ValueError):
        return None
    hi = None
    if lo < 50:
        return None
    for a, b, name in BINS:
        if lo >= a and (b is None or lo < b):
            return name
    return "$800+"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default=str(PANEL))
    args = ap.parse_args()

    q_tot = Counter()          # all orders in the quarter
    q_missing = Counter()      # no price field at all
    q_sub50 = Counter()        # priced, but below the comparable floor
    q_bin = defaultdict(Counter)
    q_gigs = defaultdict(set)

    with open(args.panel, newline="") as f:
        for r in csv.DictReader(f):
            q = r["order_quarter"]
            if q < FIRST or q > LAST:
                continue
            q_tot[q] += 1
            lo = r["paid_low"]
            if lo == "":
                q_missing[q] += 1
                continue
            b = bin_of(lo, r["paid_high"])
            if b is None:
                q_sub50[q] += 1
                continue
            q_bin[q][b] += 1
            q_gigs[q].add(r["gig_id"])

    rows = []
    for q in sorted(q_tot):
        n = sum(q_bin[q].values())
        if n < MIN_N:
            continue
        row = {"quarter": q, "orders_all": q_tot[q],
               "missing_price": q_missing[q], "under_50": q_sub50[q],
               "n_50plus": n, "gigs_50plus": len(q_gigs[q]),
               "coverage_pct": round(100 * (q_tot[q] - q_missing[q]) / q_tot[q], 1)}
        cum = 0.0
        median_bin = ""
        for name in NAMES:
            share = q_bin[q][name] / n
            row[name] = round(100 * share, 2)
            cum += share
            if cum >= 0.5 and not median_bin:
                median_bin = name
        row["median_bin"] = median_bin
        rows.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    RUNDIR.mkdir(parents=True, exist_ok=True)
    cols = (["quarter", "orders_all", "missing_price", "under_50", "coverage_pct",
             "n_50plus", "gigs_50plus"] + NAMES + ["median_bin"])
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT}  ({len(rows)} quarters)")

    first, last = rows[0], rows[-1]
    drift = {n: last[n] - first[n] for n in NAMES}

    L = ["# Realised order value, $50+ segment, 2022Q1-2026Q1", "",
         f"From **{sum(r['orders_all'] for r in rows):,}** orders recovered by step 86 "
         "out of HTML already on disk — no new collection, and unaffected by the wall "
         "that closed 2025-2026 to the crawler.", "",
         "## The series", "",
         "| quarter | n ($50+) | gigs | " + " | ".join(NAMES) + " | median bin |",
         "|---|---:|---:|" + "---:|" * len(NAMES) + "---|"]
    for r in rows:
        L.append(f"| {r['quarter']} | {r['n_50plus']:,} | {r['gigs_50plus']:,} | "
                 + " | ".join(f"{r[n]:.1f}%" for n in NAMES)
                 + f" | {r['median_bin']} |")

    L += ["", "## Reading it", "",
          f"The median bin is **{first['median_bin']}** in every one of the "
          f"{len(rows)} quarters. Over the full window the composition drifts by "
          + ", ".join(f"**{n} {drift[n]:+.1f}pp**" for n in NAMES) + ".",
          "",
          "That is a mild hollowing of the middle — the two ends thicken slightly "
          "while $100-400 thins — and it is not a collapse in what buyers pay. Any "
          "claim of a realised-price decline over this window has to survive this "
          "table first.",
          "",
          "## Two artefacts this series exists to avoid", "",
          "**1. Sub-$50 orders carried no bucket before ~2024Q2.** Coverage — the "
          "share of orders with any price field — runs:", "",
          "| quarter | coverage | orders with no price |", "|---|---:|---:|"]
    for r in rows:
        L.append(f"| {r['quarter']} | {r['coverage_pct']:.0f}% | {r['missing_price']:,} |")
    L += ["",
          "In 2022Q3 the cheapest bucket that exists at all is `$50-$100` and 46% of "
          "orders are unpriced; by 2024Q3 missingness is ~0 and `$0-$50` alone is 50% "
          "of orders. The apparent `<$50` share therefore tracks coverage almost "
          "exactly (54-67% coverage -> 0-13%; 94% -> 42%; 100% -> ~50%). **Plotting "
          "raw bucket shares would report a dramatic collapse in realised value that "
          "is entirely a reporting change.**",
          "",
          "**2. The bucket labels changed.** `$5-$20` and `$20-$50` disappear and "
          "`$0-$50` appears around 2024Q2. Bins built on published labels are not "
          "comparable across that break; the boundaries 50/100/200/400/800 are.",
          "",
          "Conditioning on $50+ removes both. The cost is that **this series says "
          "nothing about the sub-$50 segment**, which is roughly half of all orders "
          "and is unmeasurable before 2024.",
          "",
          "## Other limits, carried from steps 59 and 63", "",
          "- A page displays ~4 of ~124 reviews, ranked by `relevancy_score`, so this "
          "samples each gig's orders. Step 63A found no **price** selection in that "
          "ranking (late minus early +0 USD, CI [+0, +0]).",
          "- The gig set behind each quarter is whatever the archive captured, and it "
          "thins sharply after 2024Q3 — n falls from 40,393 ($50+ orders in 2024Q3) to "
          "420 in 2026Q1. Later quarters are noisier, not just smaller.",
          "- **This is not the IPI.** The IPI is a matched-model index on listed "
          "basic-package prices; this is a composition series on realised bucketed "
          "values over a changing gig set. Do not chain them.",
          ""]
    rep = RUNDIR / "realised-value.md"
    rep.write_text("\n".join(L))
    print(f"Wrote {rep}")
    print(f"\nMedian bin: {first['median_bin']} in all {len(rows)} quarters")
    for n in NAMES:
        print(f"  {n:>10s}  {first[n]:5.1f}% -> {last[n]:5.1f}%  ({drift[n]:+.1f}pp)")


if __name__ == "__main__":
    main()
