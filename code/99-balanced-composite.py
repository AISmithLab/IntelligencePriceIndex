#!/usr/bin/env python3
"""
Step 99: a composite index built on the balanced panel alone, 2020Q1-2024Q4.

Nothing from the headline index is used -- not its weights (recent-panel gig
shares, design 0.706), not its panels, not its splice. Inputs:

  data/pilot/balanced-broad-trajectories.csv   step 98: per-category GEKS-Jevons
                                               levels + bootstrap se_log
  data/real-prices/gig-quarter-real-prices.csv.gz
                                               the same gig-quarter panel (231,757
                                               rows / 34,967 gigs in the window),
                                               used only for weights

Aggregation is the same formula the paper uses, a fixed-weight geometric mean
    ln C_t = sum_c w_c ln I^c_t,   sum_c w_c = 1.

Weights. The balanced panel is quota-sampled, so its gig counts per category
reflect the sampling design, not the market. Three fixed weightings:

  sales   (primary)  sum over gigs of median nominal price x reviews gained in
                     the window -- a revenue proxy (one review ~ one completed order)
  equal              1/7 each
  gigs               share of distinct gigs in the window (sampling quotas)

Band. Step 98 bootstraps each category on its own gigs, and the seven categories
are disjoint gig sets, so the draws are independent and
    se(ln C_t) = sqrt(sum_c w_c^2 se_c,t^2).
Half-width 1.96 * se, as everywhere else; meets 5% when it is <= 0.05. Real =
nominal deflated by CPI-U, which shifts the log level by a constant and leaves
the band unchanged (step 66).

Run:  python3 code/99-balanced-composite.py
Writes data/pilot/balanced-composite.csv (published copy: data/real-prices/balanced-composite.csv)
and runs/balanced-composite/report.md
"""

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
TRAJ = BASE_DIR / "data" / "pilot" / "balanced-broad-trajectories.csv"
GIGS = BASE_DIR / "data" / "real-prices" / "gig-quarter-real-prices.csv.gz"
OUT_CSV = BASE_DIR / "data" / "pilot" / "balanced-composite.csv"
PUBLISHED = BASE_DIR / "data" / "real-prices" / "balanced-composite.csv"
REPORT = BASE_DIR / "runs" / "balanced-composite" / "report.md"
START_Q, END_Q = "2020Q1", "2024Q4"
Z, TARGET = 1.96, 0.05


def weights(gq):
    gq = gq.sort_values(["gig_id", "quarter"])
    per_gig = gq.groupby(["category", "gig_id"]).agg(
        price=("price_nominal", "median"),
        r0=("reviews", "first"), r1=("reviews", "last"))
    per_gig["gained"] = (per_gig.r1 - per_gig.r0).clip(lower=0).fillna(0)
    sales = (per_gig.price * per_gig.gained).groupby("category").sum()
    gigs = per_gig.groupby("category").size()
    cats = sorted(gigs.index)
    w = pd.DataFrame({"sales": sales / sales.sum(),
                      "equal": pd.Series(1 / len(cats), index=cats),
                      "gigs": gigs / gigs.sum()})
    return w, per_gig


def composite(traj, w):
    out = []
    for q, d in traj.groupby("quarter"):
        d = d.set_index("category").loc[w.index]
        ln_nom = (w * np.log(d.index_nominal)).sum()
        ln_real = (w * np.log(d.index_real)).sum()
        se = float(np.sqrt((w ** 2 * d.se_log ** 2).sum()))
        hw = Z * se
        out.append({"quarter": q, "index_nominal": np.exp(ln_nom), "index_real": np.exp(ln_real),
                    "se_log": se, "half_width_pct": 100 * hw,
                    "real_lo": np.exp(ln_real - hw), "real_hi": np.exp(ln_real + hw),
                    "meets_5pct": bool(hw <= TARGET) if q != START_Q else ""})
    return pd.DataFrame(out)


def main():
    traj = pd.read_csv(TRAJ)
    gq = pd.read_csv(GIGS)
    gq = gq[(gq.quarter >= START_Q) & (gq.quarter <= END_Q)]
    w, per_gig = weights(gq)

    tables = {}
    for scheme in w.columns:
        t = composite(traj, w[scheme])
        t.insert(0, "weights", scheme)
        tables[scheme] = t
    allt = pd.concat(tables.values())
    allt.round(4).to_csv(OUT_CSV, index=False)
    allt.round(4).to_csv(PUBLISHED, index=False)

    s = tables["sales"].set_index("quarter")
    last = s.loc[END_Q]
    L = [
        "# Balanced-panel composite, 2020Q1-2024Q4",
        "",
        f"Built by `code/99-balanced-composite.py` from step 98's category indices. "
        f"{gq.gig_id.nunique():,} gigs, {len(gq):,} gig-quarters. No headline-index input. "
        "Fixed-weight geometric mean of the 7 category GEKS-Jevons indices, 2020Q1 = 100; "
        "band = 1.96 x sqrt(sum w^2 se^2) (categories are independent bootstraps).",
        "",
        "## Weights",
        "",
        "| category | sales (primary) | equal | gigs |",
        "|---|---:|---:|---:|",
    ]
    for c in w.sort_values("sales", ascending=False).index:
        L.append(f"| {c} | {w.at[c, 'sales']:.3f} | {w.at[c, 'equal']:.3f} | {w.at[c, 'gigs']:.3f} |")
    L += ["", f"Sales = median nominal price x reviews gained {START_Q}-{END_Q}, per gig, summed; "
          f"{int((per_gig.gained > 0).sum()):,} of {len(per_gig):,} gigs gained reviews.", "",
          "## 2024Q4 under each weighting", "",
          "| weights | nominal | real | real 95% band | half-width | meets ±5% | quarters meeting (of 19) |",
          "|---|---:|---:|---|---:|---|---:|"]
    for k, t in tables.items():
        r = t.set_index("quarter").loc[END_Q]
        n = int((t.meets_5pct == True).sum())  # noqa: E712
        L.append(f"| {k} | {r.index_nominal - 100:+.1f}% | {r.index_real - 100:+.1f}% | "
                 f"[{r.real_lo - 100:+.1f}%, {r.real_hi - 100:+.1f}%] | ±{r.half_width_pct:.1f}% | "
                 f"{'**yes**' if r.meets_5pct else 'no'} | {n} |")
    L += ["", "## Sales-weighted composite by quarter", "",
          "| quarter | nominal | real | real 95% band | half-width |", "|---|---:|---:|---|---:|"]
    for q, r in s.iterrows():
        L.append(f"| {q} | {r.index_nominal:.1f} | {r.index_real:.1f} | "
                 f"[{r.real_lo:.1f}, {r.real_hi:.1f}] | ±{r.half_width_pct:.1f}%"
                 f"{'*' if r.meets_5pct is True else ''} |")
    L.append("\n\\* = meets ±5%.")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(L) + "\n")
    print(REPORT.read_text())
    print(f"Wrote {OUT_CSV} and {PUBLISHED} ({len(allt)} rows) and {REPORT}")


if __name__ == "__main__":
    main()
