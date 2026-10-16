#!/usr/bin/env python3
"""
Step 94: AI-exposure tests with 35 exposure clusters instead of 7.

EXPLORATORY, not pre-registered. Exposure from step 93 (frozen before this
ran); narrow assignment from step 66's `add_narrow` (step 16 taxonomy, buckets
under 100 gigs folded into the family remainder), so the cells are the 35 of
Appendix A.10.

  A  Cross-section, n = 35: real change 2020Q1 -> 2024Q4 of each narrow GEKS
     index (balanced-narrow-geks.csv) and its post-minus-pre growth rate, against
     exposure.
  B  Gig-level listed real price (data/real-prices/gig-quarter-real-prices),
     2019Q4-2024Q4, `Exposure x Post`:
       B1 gig + quarter FE
       B2 gig + family-by-quarter FE  -- identified ONLY from exposure
          differences inside a family, so any family-wide shock is absorbed
       B3 B1 + one linear trend per narrow cell (the standing rule since step 76)
  C  The two step-90 near-misses on page fields: description mentions
     generative AI / claims human-or-no-AI work, B1 and B2.

Inference: wild-cluster bootstrap on the 35 narrow cells (Webb weights, 999
draws, null imposed); gig-clustered t shown for comparison only.

    python3 code/94-narrow-exposure-tests.py
"""
import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "runs" / "narrow-exposure-tests.md"
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
demean2, cluster_se, wild_p = m90.demean2, m90.cluster_se, m90.wild_p


def qn(q):
    return q.str[:4].astype(int) * 4 + q.str[-1].astype(int) - 1


def attach(d, ex):
    d = m66.add_narrow(d)
    d = d.merge(ex[["narrow", "exposure_human", "exposure_gpt4"]], on="narrow", how="inner")
    d["family"] = d.narrow.str.split("-").str[0]
    d["famq"] = d.family + "_" + d.quarter
    return d


def did(d, y, expo, fe="quarter", trends=False):
    d = d[d[y].notna()].copy()
    d = d[d.groupby("gig_id").gig_id.transform("size") > 1]
    post = (d.quarter >= POST).to_numpy(float)
    cols = [d[expo].to_numpy() * post]
    if trends:
        t = (qn(d.quarter) - qn(pd.Series([POST]))[0]).to_numpy(float)
        for c in sorted(d.narrow.unique())[1:]:
            cols.append((d.narrow == c).to_numpy(float) * t)
    M = np.column_stack([d[y].to_numpy(float)] + cols)
    M = demean2(M, d.gig_id.to_numpy(), d[fe].to_numpy())
    yv, X = M[:, 0], M[:, 1:]
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ X.T @ yv
    se = cluster_se(X, yv - X @ b, d.gig_id.to_numpy(), XtXi)
    p = wild_p(yv, X, d.narrow.to_numpy(), b)
    return b[0], se[0], p, len(d), d.gig_id.nunique(), d.narrow.nunique()


def gap(b, ex, col):
    """Coefficient -> implied % gap between the most and least exposed cell."""
    span = ex[col].max() - ex[col].min()
    return 100 * (np.exp(b * span) - 1), span


def main():
    ex = pd.read_csv(BASE / "data" / "narrow-exposure.csv")
    L = ["# Step 94 — AI exposure with 35 clusters (EXPLORATORY)", "",
         "Exposure from step 93 (frozen before this ran). Post = 1[quarter ≥ 2022Q4]. "
         "**wild p** = wild-cluster bootstrap on the 35 narrow cells, the inference to read. "
         "**Gap** = implied post-ChatGPT price difference between the most- and least-exposed cell "
         "(coefficient × exposure range).", ""]

    # ---------------- A: cross-section
    n = pd.read_csv(BASE / "data" / "pilot" / "balanced-narrow-geks.csv")
    n = n.rename(columns={"category": "narrow"})
    n["lr"] = np.log(n.index_real / 100)
    rows = []
    for c, g in n.groupby("narrow"):
        g = g.set_index("quarter")
        q = qn(pd.Series(g.index)).to_numpy()
        pre, post = g.index < POST, g.index >= POST
        sp = np.polyfit(q[pre], g.lr[pre], 1)[0]
        so = np.polyfit(q[post], g.lr[post], 1)[0]
        rows.append({"narrow": c, "real_change": g.index_real.iloc[-1] / 100 - 1,
                     "se": g.se_log.iloc[-1], "slope_pre": sp, "slope_post": so,
                     "dslope": so - sp})
    A = pd.DataFrame(rows).merge(ex, on="narrow")
    L += ["## A · Cross-section of the 35 narrow indices", "",
          "| Outcome | Exposure | Spearman ρ | p | Pearson r | p | WLS slope (per 0.1 exposure) | t |",
          "|---|---|---:|---:|---:|---:|---:|---:|"]
    for y, lab in [("real_change", "real change 2020Q1→2024Q4"),
                   ("dslope", "growth post − pre (log/qtr)")]:
        for e in ["exposure_human", "exposure_gpt4"]:
            rs, ps = stats.spearmanr(A[e], A[y])
            rp, pp = stats.pearsonr(A[e], A[y])
            yy = np.log1p(A[y]) if y == "real_change" else A[y]
            w = 1 / np.maximum(A.se, 0.01) ** 2 if y == "real_change" else np.ones(len(A))
            X = np.column_stack([np.ones(len(A)), A[e]])
            W = np.diag(w)
            b = np.linalg.solve(X.T @ W @ X, X.T @ W @ yy)
            res = yy - X @ b
            s2 = (w * res ** 2).sum() / (len(A) - 2)
            se = np.sqrt(np.diag(np.linalg.inv(X.T @ W @ X)) * s2)
            L.append(f"| {lab} | {e.split('_')[1]} | {rs:+.3f} | {ps:.3f} | {rp:+.3f} | {pp:.3f} | "
                     f"{b[1]/10:+.4f} | {b[1]/se[1]:+.2f} |")
    A = A.sort_values("exposure_human", ascending=False)
    L += ["", "| Narrow cell | Exposure (human) | GPT-4 | Real change | Growth pre | post |",
          "|---|---:|---:|---:|---:|---:|"]
    L += [f"| {r.narrow} | {r.exposure_human:.2f} | {r.exposure_gpt4:.2f} | {100*r.real_change:+.1f}% | "
          f"{r.slope_pre:+.4f} | {r.slope_post:+.4f} |" for r in A.itertuples()]

    # ---------------- B: gig-level prices
    g = pd.read_csv(BASE / "data" / "real-prices" / "gig-quarter-real-prices.csv.gz")
    g = g[(g.quarter >= WIN[0]) & (g.quarter <= WIN[1])].copy()
    g["lp"] = np.log(g.price_real_2020q1)
    g = attach(g, ex)
    L += ["", "## B · Gig-level listed real price, Exposure × Post", "",
          f"{len(g):,} gig-quarters, {g.gig_id.nunique():,} gigs, {g.narrow.nunique()} cells, "
          f"{WIN[0]}–{WIN[1]}.", "",
          "| Spec | Exposure | Coef | SE (gig) | t (gig) | **wild p (35 cells)** | Gap, most vs least exposed |",
          "|---|---|---:|---:|---:|---:|---:|"]
    specs = [("B1 gig + quarter FE", dict(fe="quarter")),
             ("B2 gig + family×quarter FE (within family)", dict(fe="famq")),
             ("B3 B1 + narrow-cell trends", dict(fe="quarter", trends=True))]
    for lab, kw in specs:
        for e in ["exposure_human", "exposure_gpt4"]:
            b, se, p, nobs, ng, nc = did(g, "lp", e, **kw)
            gp, span = gap(b, ex, e)
            L.append(f"| {lab} | {e.split('_')[1]} | {b:+.4f} | {se:.4f} | {b/se:+.2f} | **{p:.3f}** | "
                     f"{gp:+.1f}% |")

    # ---------------- C: description flags
    p = pd.read_csv(BASE / "data" / "pilot" / "page-fields-all.csv.gz",
                    usecols=["gig_id", "capture_date", "desc_ai", "desc_anti_ai"])
    p["capture_date"] = p.capture_date.astype(str)
    p["quarter"] = p.capture_date.str[:4] + "Q" + ((p.capture_date.str[4:6].astype(int) - 1) // 3 + 1).astype(str)
    p = p[(p.quarter >= WIN[0]) & (p.quarter <= WIN[1])]
    p = p.sort_values("capture_date").groupby(["gig_id", "quarter"]).tail(1)
    cat = m90.cats()
    p = p.merge(cat, on="gig_id")
    p = attach(p, ex)
    L += ["", "## C · Gig descriptions (step-90 near-misses), Exposure × Post", "",
          f"{len(p):,} gig-quarters, {p.gig_id.nunique():,} gigs, {p.narrow.nunique()} cells.", "",
          "| Outcome · spec | Exposure | Coef | SE (gig) | t (gig) | **wild p (35 cells)** | mean |",
          "|---|---|---:|---:|---:|---:|---:|"]
    for y in ["desc_ai", "desc_anti_ai"]:
        for lab, kw in specs[:2]:
            b, se, pv, nobs, ng, nc = did(p, y, "exposure_human", **kw)
            L.append(f"| {y} · {lab.split(' ')[0]} | human | {b:+.4f} | {se:.4f} | {b/se:+.2f} | "
                     f"**{pv:.3f}** | {p[y].mean():.4f} |")

    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
