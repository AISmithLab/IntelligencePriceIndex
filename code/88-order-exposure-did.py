#!/usr/bin/env python3
"""
Step 88: exposure difference-in-differences on ORDER-level outcomes.

EXPLORATORY, not pre-registered. Uses the step-86 order panel (dated by order,
not capture) and the step-45 exposure ranking, unchanged.

WHY NOT ORDER COUNTS. A page displays at most 5 of a gig's reviews, ranked by
relevancy (65% of captures show exactly 5). Orders per gig-quarter is therefore
captures x 5, an archive-density series, not demand. And `duration_days` is 0%
populated before 2023Q2 (100% from 2024Q3) -- a reporting artefact, no pre
period. What an order still carries is its composition:

  * hi_value  1[paid_low >= 200] among orders banded $50+ (the stable bands, step 87)
  * low_rate  1[rating < 5]  -- buyer satisfaction
  * us_buyer  1[country == US]

SPEC. Order-level LPM, gig FE + quarter FE, `Exposure x Post` with
Post = 1[order_quarter >= 2022Q4] (step 76 convention), window 2021Q4-2024Q4
(the quarters with dense orders). Plus an event study, Exposure x quarter,
reference 2022Q3. SEs clustered on gig. Exposure varies at CATEGORY level and
there are 7 categories, so gig clustering is optimistic; a category-level
wild-cluster bootstrap would be the honest inference, and the event study's
pre-period is only 4 quarters.

    python3 code/88-order-exposure-did.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ORDERS = ROOT / "data/pilot/order-panel-all.csv"
CATS = ROOT / "data/pilot/balanced-gig-category.csv.gz"
EXPO = ROOT / "data/exposure-ranking.csv"
OUT = ROOT / "runs/order-exposure-did.md"

WINDOW = ("2021Q4", "2024Q4")
POST = "2022Q4"
REF = "2022Q3"


def qi(q):
    return q.str[:4].astype(int) * 4 + q.str[-1].astype(int) - 1


def demean2(X, g, t, iters=50, tol=1e-10):
    """Two-way within transform by alternating projections."""
    X = X.copy()
    for _ in range(iters):
        X_old = X.copy()
        X -= pd.DataFrame(X).groupby(g).transform("mean").to_numpy()
        X -= pd.DataFrame(X).groupby(t).transform("mean").to_numpy()
        if np.abs(X - X_old).max() < tol:
            break
    return X


def ols_cluster(y, X, cl):
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    S = pd.DataFrame(X * e[:, None]).groupby(cl).sum().to_numpy()
    G = len(S)
    V = XtX_inv @ (S.T @ S) @ XtX_inv * G / (G - 1)
    return b, np.sqrt(np.diag(V))


def load():
    o = pd.read_csv(ORDERS, usecols=["gig_id", "order_quarter", "paid_low",
                                     "rating", "country"])
    o = o.merge(pd.read_csv(CATS), on="gig_id")
    ex = pd.read_csv(EXPO).set_index("category")
    o["exp_h"] = o.category.map(ex.exposure_primary)
    o["exp_r"] = o.category.map(ex.exposure_robust)
    o = o[(o.order_quarter >= WINDOW[0]) & (o.order_quarter <= WINDOW[1])].copy()
    o["hi_value"] = np.where(o.paid_low >= 50, (o.paid_low >= 200).astype(float), np.nan)
    o["low_rate"] = np.where(o.rating.notna(), (o.rating < 5).astype(float), np.nan)
    o["us_buyer"] = np.where(o.country.notna(), (o.country == "US").astype(float), np.nan)
    return o


def did(o, y, expo):
    d = o[o[y].notna()].copy()
    # singleton gigs carry no within variation
    d = d[d.groupby("gig_id").gig_id.transform("size") > 1]
    post = (d.order_quarter >= POST).to_numpy(float)
    X = (d[expo].to_numpy() * post)[:, None]
    Z = demean2(np.column_stack([d[y].to_numpy(), X]),
                d.gig_id.to_numpy(), d.order_quarter.to_numpy())
    b, se = ols_cluster(Z[:, 0], Z[:, 1:], d.gig_id.to_numpy())
    return b[0], se[0], len(d), d.gig_id.nunique(), d[y].mean()


def event(o, y, expo):
    d = o[o[y].notna()].copy()
    d = d[d.groupby("gig_id").gig_id.transform("size") > 1]
    qs = sorted(q for q in d.order_quarter.unique() if q != REF)
    X = np.column_stack([d[expo].to_numpy() * (d.order_quarter == q).to_numpy(float)
                         for q in qs])
    Z = demean2(np.column_stack([d[y].to_numpy(), X]),
                d.gig_id.to_numpy(), d.order_quarter.to_numpy())
    b, se = ols_cluster(Z[:, 0], Z[:, 1:], d.gig_id.to_numpy())
    return pd.DataFrame({"quarter": qs, "coef": b, "se": se, "t": b / se})


def main():
    o = load()
    L = ["# Step 88 — exposure DiD on order-level outcomes (EXPLORATORY)", "",
         f"Window {WINDOW[0]}–{WINDOW[1]}, Post = 1[quarter ≥ {POST}], gig + quarter FE, "
         "gig-clustered SE. Exposure on a 0–1 scale, so the coefficient is the "
         "post-ChatGPT change for a fully exposed vs unexposed category.", ""]

    L += ["## Raw means by category, pre (2021Q4–2022Q3) vs post (2022Q4–2024Q4)", "",
          "| Category | Exposure | hi_value pre | post | low_rate pre | post | us_buyer pre | post | orders |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    o["period"] = np.where(o.order_quarter >= POST, "post", "pre")
    for cat, g in o.groupby("category"):
        m = g.groupby("period")[["hi_value", "low_rate", "us_buyer"]].mean()
        L.append(f"| {cat} | {g.exp_h.iloc[0]:.2f} | "
                 + " | ".join(f"{m.loc['pre', c]:.3f} | {m.loc['post', c]:.3f}"
                              for c in ["hi_value", "low_rate", "us_buyer"])
                 + f" | {len(g):,} |")
    o = o.drop(columns="period")

    L += ["", "## Exposure × Post", "",
          "| Outcome | Exposure | Coef | SE | t | n orders | gigs | mean |",
          "|---|---|---:|---:|---:|---:|---:|---:|"]
    for y in ["hi_value", "low_rate", "us_buyer"]:
        for expo, lab in [("exp_h", "human"), ("exp_r", "GPT-4")]:
            b, se, n, g, mu = did(o, y, expo)
            L.append(f"| {y} | {lab} | {b:+.4f} | {se:.4f} | {b/se:+.2f} | {n:,} | {g:,} | {mu:.3f} |")

    L += ["", "## Event study (human exposure), ref 2022Q3", ""]
    for y in ["hi_value", "low_rate", "us_buyer"]:
        es = event(o, y, "exp_h")
        L += [f"### {y}", "", "| Quarter | Coef | SE | t |", "|---|---:|---:|---:|"]
        L += [f"| {r.quarter} | {r.coef:+.4f} | {r.se:.4f} | {r.t:+.2f} |"
              for r in es.itertuples()]
        L.append("")
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
