#!/usr/bin/env python3
"""
Step 95: did AI exposure hit inexperienced and experienced freelancers differently?

EXPLORATORY, not pre-registered. Experience = the gig's cumulative review count
at its last observation before ChatGPT (<= 2022Q3), fixed per gig, so it cannot
respond to treatment. Terciles of that count define novice / mid / veteran.
Exposure = step 93's 35-cell scores (human primary, GPT-4 robustness).

Panel: data/real-prices/gig-quarter-real-prices.csv.gz (step 92 = step 76's
build_panel), 2019Q4-2024Q4, gigs observed both before and after 2022Q4.

  E1  descriptive: real price change pre -> post by experience tercile x
      exposure half (above / below the median cell)
  E2  log real price on gig + quarter FE with
        Exposure x Post, Exposure x Post x Novice, Exposure x Post x Veteran,
        Post x Novice, Post x Veteran
      so `Exposure x Post` is the mid tercile's exposure effect and the triple
      terms are how novices / veterans differ from it
  E3  E2 + gig-specific reputation control ln(1+reviews), since reviews grow
      faster in proportional terms for novices (the step-76 treadmill)
  E4  E2 + one linear trend per experience tercile x narrow cell

Inference: wild-cluster bootstrap on the 35 narrow cells, for each triple term.

    python3 code/95-experience-exposure.py
"""
import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "runs" / "experience-exposure.md"
POST, WIN = "2022Q4", ("2019Q4", "2024Q4")


def _load(name, rel):
    sys.path.insert(0, str(BASE / "code"))
    spec = importlib.util.spec_from_file_location(name, BASE / "code" / rel)
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m


m66 = _load("m66", "66-narrow-real-geks.py")
m90 = _load("m90", "90-ai-margin-tests.py")
demean2, cluster_se = m90.demean2, m90.cluster_se
WEBB = m90.WEBB
RNG = np.random.default_rng(95)


def wild_p(y, X, cl, b_obs, k=0, B=999):
    """Same test as step 90's wild_p (WCR, Webb weights, cluster-robust t), but
    every draw works on per-cluster sums: with G = 35 clusters the n-row
    products are computed once, and all B draws run as one matrix product."""
    Xr = np.delete(X, k, axis=1)
    fit_r = Xr @ np.linalg.lstsq(Xr, y, rcond=None)[0] if Xr.shape[1] else np.zeros_like(y)
    er = y - fit_r
    codes, uniq = pd.factorize(cl)
    G, K = len(uniq), X.shape[1]
    XtXi = np.linalg.pinv(X.T @ X)
    c = XtXi[k]                                   # row giving coefficient k
    P = np.zeros((G, K)); Q = np.zeros((G, K)); H = np.zeros((G, K, K))
    np.add.at(P, codes, X * fit_r[:, None])
    np.add.at(Q, codes, X * er[:, None])
    for gi in range(G):
        Xg = X[codes == gi]
        H[gi] = Xg.T @ Xg
    Hc = H @ c                                    # (G, K): H_g c, so c'H_g b = Hc_g . b
    adj = G / (G - 1)

    def tstat(W):                                  # W: (B, G) cluster weights
        XtY = P.sum(0) + W @ Q                     # (B, K)
        bs = XtY @ XtXi.T                          # (B, K)
        # score of cluster g projected on c: c'(P_g + w Q_g - H_g b)
        z = (P @ c)[None, :] + W * (Q @ c)[None, :] - bs @ Hc.T   # (B, G)
        return bs[:, k] / np.sqrt(adj * (z ** 2).sum(1))

    t_obs = tstat(np.ones((1, G)))[0]
    W = RNG.choice(WEBB, size=(B, G))
    hits = (np.abs(tstat(W)) >= abs(t_obs)).sum()
    return (hits + 1) / (B + 1)


def qn(q):
    return q.str[:4].astype(int) * 4 + q.str[-1].astype(int) - 1


def panel():
    g = pd.read_csv(BASE / "data" / "real-prices" / "gig-quarter-real-prices.csv.gz")
    g = g[(g.quarter >= WIN[0]) & (g.quarter <= WIN[1]) & g.reviews.notna()].copy()
    g["lp"] = np.log(g.price_real_2020q1)
    g["post"] = (g.quarter >= POST).astype(float)
    both = g.groupby("gig_id").post.agg(["min", "max"])
    g = g[g.gig_id.isin(both[(both["min"] == 0) & (both["max"] == 1)].index)]
    base = (g[g.post == 0].sort_values("quarter").groupby("gig_id").reviews.last()
            .rename("rev0"))
    g = g.merge(base, on="gig_id")
    cuts = base.quantile([1 / 3, 2 / 3]).to_numpy()
    g["tercile"] = np.where(g.rev0 <= cuts[0], "novice",
                            np.where(g.rev0 <= cuts[1], "mid", "veteran"))
    g = m66.add_narrow(g)
    ex = pd.read_csv(BASE / "data" / "narrow-exposure.csv")
    g = g.merge(ex[["narrow", "exposure_human", "exposure_gpt4"]], on="narrow")
    g["lrev"] = np.log1p(g.reviews)
    return g, cuts


def fit(g, expo, extra=None, trends=False):
    post = g.post.to_numpy()
    e = g[expo].to_numpy()
    nov = (g.tercile == "novice").to_numpy(float)
    vet = (g.tercile == "veteran").to_numpy(float)
    cols = [e * post, e * post * nov, e * post * vet, post * nov, post * vet]
    names = ["Exp×Post (mid tercile)", "Exp×Post×Novice", "Exp×Post×Veteran",
             "Post×Novice", "Post×Veteran"]
    if extra:
        cols.append(g[extra].to_numpy(float)); names.append(extra)
    if trends:
        t = (qn(g.quarter) - qn(pd.Series([POST]))[0]).to_numpy(float)
        cell = g.tercile + "|" + g.narrow
        for c in sorted(cell.unique())[1:]:
            cols.append((cell == c).to_numpy(float) * t)
    M = demean2(np.column_stack([g.lp.to_numpy()] + cols), g.gig_id.to_numpy(),
                g.quarter.to_numpy())
    y, X = M[:, 0], M[:, 1:]
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ X.T @ y
    se = cluster_se(X, y - X @ b, g.gig_id.to_numpy(), XtXi)
    cl = g.narrow.to_numpy()
    ps = {k: wild_p(y, X, cl, b, k=k) for k in (0, 1, 2)}
    return [(names[k], b[k], se[k], ps.get(k)) for k in range(5)]


def main():
    g, cuts = panel()
    med = g.drop_duplicates("narrow")[["narrow", "exposure_human"]].exposure_human.median()
    g["exp_half"] = np.where(g.exposure_human > med, "high exposure", "low exposure")
    L = ["# Step 95 — AI exposure × freelancer experience (EXPLORATORY)", "",
         f"{len(g):,} gig-quarters, {g.gig_id.nunique():,} gigs observed both before and after "
         f"{POST}, {g.narrow.nunique()} cells, {WIN[0]}–{WIN[1]}. Experience = reviews at the gig's "
         f"last pre-ChatGPT quarter; terciles: **novice ≤ {cuts[0]:.0f}**, mid ≤ {cuts[1]:.0f}, "
         f"**veteran > {cuts[1]:.0f}** reviews. High/low exposure split at the median cell "
         f"({med:.2f}).", ""]

    # E1 descriptive: mean within-gig change in log real price, post mean minus pre mean
    gm = g.groupby(["gig_id", "post"]).lp.mean().unstack()
    d = (gm[1.0] - gm[0.0]).rename("dlp").reset_index().merge(
        g.drop_duplicates("gig_id")[["gig_id", "tercile", "exp_half"]], on="gig_id")
    t = d.groupby(["tercile", "exp_half"]).dlp.agg(["mean", "count", "sem"])
    L += ["## E1 · Within-gig real price change, post-ChatGPT mean vs pre mean", "",
          "| Experience | Low exposure | High exposure | High − low |", "|---|---:|---:|---:|"]
    for ter in ["novice", "mid", "veteran"]:
        lo, hi = t.loc[(ter, "low exposure")], t.loc[(ter, "high exposure")]
        pct = lambda v: 100 * (np.exp(v) - 1)
        L.append(f"| {ter} | {pct(lo['mean']):+.1f}% (n {int(lo['count']):,}) | "
                 f"{pct(hi['mean']):+.1f}% (n {int(hi['count']):,}) | "
                 f"{100*(hi['mean']-lo['mean']):+.1f} log pts |")

    for lab, kw in [("E2 · gig + quarter FE", {}),
                    ("E3 · + reputation control ln(1+reviews)", {"extra": "lrev"}),
                    ("E4 · + linear trend per experience tercile × cell", {"trends": True})]:
        L += ["", f"## {lab}", "",
              "| Term | Exposure | Coef | SE (gig) | t (gig) | wild p (cells) |",
              "|---|---|---:|---:|---:|---:|"]
        for e in ["exposure_human", "exposure_gpt4"]:
            for name, b, se, p in fit(g, e, **kw):
                ps = f"**{p:.3f}**" if p is not None else "—"
                L.append(f"| {name} | {e.split('_')[1]} | {b:+.4f} | {se:.4f} | {b/se:+.2f} | {ps} |")

    L += ["", "Reading: `Exp×Post×Novice` < 0 would mean AI exposure lowered novices' prices "
          "relative to mid-experience sellers in the same cell; > 0 the reverse. Coefficients are "
          "per unit of exposure; the 35 cells span 0.23–0.84 (human)."]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
