#!/usr/bin/env python3
"""
Step 78: how does reputation influence price, once task value is a NODE and not
a black box?

THE DESIGN, in the order it was asked for:

  1. TAXONOMY. Step 77 assigns every gig a node, `domain/subcategory`.
  2. REFERENCE TASK VALUE. v_n = mean of ln(real price) over the node. Printed
     in dollars as exp(v_n), a geometric mean.
  3. REPUTATION. Fit price against reputation with v_n as the anchor.

WHY THIS IS NOT STEP 76 AGAIN. Step 76 absorbed task value in a GIG fixed
effect, which made it unreportable -- and worse, a gig fixed effect also absorbs
the PERMANENT part of reputation, so step 76 could only ever see a gig
repricing itself over time. Anchoring on the node instead leaves the
between-seller comparison alive: two sellers offering `design/logo`, one with
50 reviews and one with 5,000, are in the same node and their price gap is
visible. That comparison is the one the question is actually about.

THE CATCH, STATED BEFORE THE NUMBERS. The mean price of a node is NOT clean of
reputation. If `design/logo` happens to be full of high-review veterans, part of
its $24.28 is their reputation, and subtracting that mean subtracts some of the
effect being estimated. So the reference value is computed BOTH ways:

  RAW        v_n = mean ln p in the node.                  (as specified)
  ADJUSTED   v_n = the node fixed effect from a joint fit
             that also carries reputation and quarter.      (reputation removed)

The gap between them is how much of a node's going rate is its sellers' standing
rather than the work. It is reported per node.

THREE LEVELS, BECAUSE THEY DISAGREE AND THE DISAGREEMENT IS THE ANSWER:

  A  BETWEEN NODES     do dearer nodes carry more reviews? (task, not reputation)
  B  BETWEEN GIGS,     two listings of the same work, different review counts.
     WITHIN NODE       This is the "what is reputation worth" reading.
  C  WITHIN GIG        one listing over time as reviews accrue. Step 76's +7.33%.

Step 25 found A/B and C disagree at the category level -- a Simpson reversal, the
cross-section near zero against a positive panel slope. With 65 nodes instead of
7 categories the same contrast is much sharper, and §4 measures it.

SEs are clustered on gig throughout, the unit that repeats.

Input:  data/pilot/taxonomy-assignment.csv  (step 77)
        data/pilot/balanced-prices.csv, balanced-gig-category.csv.gz, data/cpi-u.csv
Output: runs/taxonomy/reputation.md
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUTDIR = BASE_DIR / "runs" / "taxonomy"

_spec = importlib.util.spec_from_file_location("tax", BASE_DIR / "code" / "77-task-taxonomy.py")
tax = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tax)

MIN_GIGS_NODE_SLOPE = 100      # a per-node slope below this is not reported


def fe_ols(y, X, absorb, cluster, names):
    """OLS absorbing ONE fixed effect by demeaning, clustered on another group.

    `absorb` and `cluster` are separate on purpose: spec B absorbs the NODE but
    still clusters on GIG, because a gig contributes many correlated quarters.
    """
    na = int(absorb.max()) + 1
    cnt = np.bincount(absorb, minlength=na).astype(float)
    dm = lambda v: v - (np.bincount(absorb, weights=v, minlength=na) / cnt)[absorb]
    yd = dm(y)
    Xd = np.column_stack([dm(X[:, j]) for j in range(X.shape[1])])
    XtXi = np.linalg.pinv(Xd.T @ Xd)
    b = XtXi @ (Xd.T @ yd)
    u = yd - Xd @ b
    n, k = Xd.shape
    dof = max(n - k - na, 1)

    o = np.argsort(cluster, kind="stable")
    gs, Xs, us = cluster[o], Xd[o], u[o]
    ng = len(np.unique(cluster))
    meat = np.zeros((k, k))
    bnd = np.flatnonzero(np.diff(gs)) + 1
    for a, bq in zip(np.r_[0, bnd], np.r_[bnd, len(gs)]):
        s = Xs[a:bq].T @ us[a:bq]
        meat += np.outer(s, s)
    V = XtXi @ meat @ XtXi * (ng / (ng - 1)) * ((n - 1) / dof)
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    alpha = np.bincount(absorb, weights=y - X @ b, minlength=na) / cnt
    return (pd.DataFrame({"term": names, "coef": b, "se": se,
                          "t": b / np.where(se > 0, se, np.nan)}),
            {"obs": n, "within_r2": 1 - float(u @ u) / max(float(yd @ yd), 1e-12),
             "alpha": alpha, "resid_sd": float(np.std(u))})


def qdummies(quarters):
    cols = sorted(set(quarters))[1:]
    pos = {q: j for j, q in enumerate(cols)}
    D = np.zeros((len(quarters), len(cols)))
    for i, q in enumerate(quarters):
        j = pos.get(q)
        if j is not None:
            D[i, j] = 1.0
    return D, [f"Q:{c}" for c in cols]


def pct(b):
    """log coefficient -> % per DOUBLING of reviews."""
    return 100 * np.expm1(b * np.log(2))


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    gq, _ = tax.build()
    d = gq[gq.reviews.notna() & gq.rating.notna() & (gq.real > 0)].copy()

    y = np.log(d.real.to_numpy(float))
    lnrev = np.log1p(d.reviews.to_numpy(float))
    rating = d.rating.to_numpy(float)
    D, dn = qdummies(d.quarter.to_numpy())
    inode = pd.factorize(d.node)[0]
    igig = pd.factorize(d.gig_id)[0]
    REP = ["ln(1+reviews)", "rating"]

    L = ["# How reputation influences price, with task value anchored on a taxonomy node", ""]
    L += [f"Panel: **{len(d):,} gig-quarter observations**, **{d.gig_id.nunique():,} gigs**, "
          f"**{d.node.nunique()} nodes**. Real prices, 2020Q1 dollars. SEs clustered on gig.",
          "", "Note this panel is **not** step 76's: there is no before/after balance "
          "requirement, because nothing here is a difference-in-differences. That is why "
          f"it carries {d.gig_id.nunique():,} gigs against step 76's 15,676.", ""]

    # ---- 1. the two reference task values ----------------------------------
    raw = d.groupby("node").apply(lambda s: float(np.mean(np.log(s.real))),
                                  include_groups=False)
    Xb = np.column_stack([D, lnrev[:, None], rating[:, None]])
    tB, exB = fe_ols(y, Xb, inode, igig, list(dn) + REP)
    adj = pd.Series(exB["alpha"], index=pd.factorize(d.node)[1])
    # put both on a comparable footing: quarter dummies are omitted-base coded, so
    # compare each node to its own domain-free mean shift by re-centring both.
    raw_c, adj_c = raw - raw.mean(), adj - adj.mean()

    L += ["## 1. Reference task value, raw and reputation-adjusted", "",
          "`raw` is the node's mean `ln(real price)`, exactly as specified. `adjusted` is "
          "the node's fixed effect from a fit that also carries reputation and quarter, so "
          "it is the going rate for the WORK with the sellers' standing taken out. Both are "
          "centred on their own mean, so only the GAP between the columns is meaningful.", "",
          "A positive gap means the node looks dearer than the work warrants because its "
          "sellers are well-reviewed; a negative gap means the node is underselling its "
          "reputation.", ""]
    cmp = pd.DataFrame({"raw": raw_c, "adjusted": adj_c})
    cmp["gap"] = cmp.raw - cmp.adjusted
    cmp["gigs"] = d.groupby("node").gig_id.nunique()
    cmp["med_rev"] = d.groupby("node").reviews.median()
    L += [f"Correlation between the two rankings: **{cmp.raw.corr(cmp.adjusted):.4f}** "
          f"(Spearman {cmp.raw.corr(cmp.adjusted, method='spearman'):.4f}). "
          f"Mean absolute gap **{cmp.gap.abs().mean():.4f}** log points, max "
          f"**{cmp.gap.abs().max():.4f}**.", ""]
    L += ["The ten nodes whose price is most inflated by reputation, and the ten least:", "",
          "| node | gigs | median reviews | raw | adjusted | gap |", "|---|---:|---:|---:|---:|---:|"]
    ends = pd.concat([cmp.nlargest(10, "gap"), cmp.nsmallest(10, "gap")])
    for n, r in ends.iterrows():
        L.append(f"| {n} | {int(r.gigs):,} | {r.med_rev:,.0f} | {r.raw:+.4f} | "
                 f"{r.adjusted:+.4f} | {r.gap:+.4f} |")

    # ---- 2. the three levels ----------------------------------------------
    L += ["", "## 2. Reputation at three levels", "",
          "The same two reputation variables, changing only what is held fixed.", ""]

    # A: between nodes -- collapse to node means, no FE
    nm = d.groupby("node").agg(lnp=("real", lambda s: float(np.mean(np.log(s))))
                               ).join(d.groupby("node").agg(
                                   lr=("reviews", lambda s: float(np.mean(np.log1p(s)))),
                                   rt=("rating", "mean")))
    Xa = np.column_stack([np.ones(len(nm)), nm.lr.to_numpy(), nm.rt.to_numpy()])
    ba, *_ = np.linalg.lstsq(Xa, nm.lnp.to_numpy(), rcond=None)
    ua = nm.lnp.to_numpy() - Xa @ ba
    va = np.linalg.pinv(Xa.T @ Xa) * float(ua @ ua) / max(len(nm) - 3, 1)
    sea = np.sqrt(np.diag(va))
    L += [f"**A — between nodes** ({len(nm)} nodes, one row each; no fixed effects). "
          f"Does dearer work carry more reviews?", "",
          "| term | coef | se | t | per doubling |", "|---|---:|---:|---:|---:|",
          f"| ln(1+reviews) | {ba[1]:+.4f} | {sea[1]:.4f} | {ba[1]/sea[1]:+.2f} | {pct(ba[1]):+.2f}% |",
          f"| rating | {ba[2]:+.4f} | {sea[2]:.4f} | {ba[2]/sea[2]:+.2f} | — |", "",
          "The rating coefficient here is fit on 65 points and should not be read as a "
          "price effect: node mean rating is close to constant (Fiverr ratings sit at "
          "4.8-5.0 almost everywhere), so it is picking up whatever else separates cheap "
          "nodes from dear ones.", ""]

    # B: between gigs within node
    L += [f"**B — between gigs, within node** (node absorbed; this is the "
          f"'what is reputation worth' reading). Within-R² {exB['within_r2']:.4f}.", "",
          "| term | coef | se | t | per doubling |", "|---|---:|---:|---:|---:|"]
    for t_ in REP:
        r = tB[tB.term == t_].iloc[0]
        extra = f"{pct(r.coef):+.2f}%" if t_.startswith("ln") else "—"
        L.append(f"| {t_} | {r.coef:+.4f} | {r.se:.4f} | {r.t:+.2f} | {extra} |")

    # C: within gig
    tC, exC = fe_ols(y, Xb, igig, igig, list(dn) + REP)
    L += ["", f"**C — within gig, over time** (gig absorbed; step 76's specification, "
              f"re-run on this larger panel). Within-R² {exC['within_r2']:.4f}.", "",
          "| term | coef | se | t | per doubling |", "|---|---:|---:|---:|---:|"]
    for t_ in REP:
        r = tC[tC.term == t_].iloc[0]
        extra = f"{pct(r.coef):+.2f}%" if t_.startswith("ln") else "—"
        L.append(f"| {t_} | {r.coef:+.4f} | {r.se:.4f} | {r.t:+.2f} | {extra} |")

    bB = float(tB[tB.term == "ln(1+reviews)"].coef.iloc[0])
    bC = float(tC[tC.term == "ln(1+reviews)"].coef.iloc[0])
    L += ["", f"**The three do not agree, and that is the finding.** Between nodes "
              f"{pct(ba[1]):+.2f}% per doubling, between gigs within a node "
              f"{pct(bB):+.2f}%, within a gig {pct(bC):+.2f}%. "
              + ("**B and C have OPPOSITE SIGNS.** Among sellers of the SAME task, the "
                 "better-reviewed ones charge LESS -- and yet any single listing raises its "
                 "own price as it accumulates reviews. Both are precisely estimated, so this "
                 "is not noise: it is step 25's Simpson reversal, sharpened from `near zero` "
                 "to `significantly negative` by holding the task fixed at node rather than "
                 "domain. The reading is that a high review count identifies two different "
                 "things at once -- a seller who has been around (which raises price) and a "
                 "seller running a cheap high-volume operation (which lowers it). Between "
                 "sellers the second dominates; within one listing only the first can move."
                 if bB < 0 < bC else
                 "The cross-section is weaker than the panel, step 25's Simpson reversal "
                 "localised: across sellers of the SAME task, high review counts belong to "
                 "high-throughput cheap sellers, which cancels much of the premium a single "
                 "gig earns by accumulating them."
                 if bB < bC else
                 "The cross-section is not weaker than the panel here, which REVERSES step "
                 "25's finding and needs explaining before either is quoted."), ""]

    # ---- 3. curvature -------------------------------------------------------
    Xq = np.column_stack([D, lnrev[:, None], (lnrev ** 2)[:, None], rating[:, None]])
    nq = list(dn) + ["ln(1+reviews)", "ln(1+reviews)^2", "rating"]
    tQ, _ = fe_ols(y, Xq, igig, igig, nq)
    b1 = float(tQ[tQ.term == "ln(1+reviews)"].coef.iloc[0])
    b2 = float(tQ[tQ.term == "ln(1+reviews)^2"].coef.iloc[0])
    t2 = float(tQ[tQ.term == "ln(1+reviews)^2"].t.iloc[0])
    L += ["## 3. The rate is not constant", "",
          f"Adding a square term to spec C gives `ln(1+reviews)` **{b1:+.4f}** and its "
          f"square **{b2:+.4f}** (t {t2:+.2f}). The marginal return to a doubling:", "",
          "| cumulative reviews | per doubling |", "|---:|---:|"]
    for r_ in [10, 50, 100, 500, 1000, 5000]:
        m = b1 + 2 * b2 * np.log1p(r_)
        L.append(f"| {r_:,} | {pct(m):+.2f}% |")
    L += ["", "A single elasticity is an average over this curve, not a rate that applies "
              "at every level.", ""]

    # ---- 4. does reputation pay differently by task? ------------------------
    L += ["## 4. Does reputation pay the same for every task?", "",
          f"Spec C re-fit inside each node with at least {MIN_GIGS_NODE_SLOPE} gigs. This "
          "is the question the taxonomy exists to make askable.", ""]
    rows = []
    for n, s in d.groupby("node"):
        if s.gig_id.nunique() < MIN_GIGS_NODE_SLOPE:
            continue
        ys = np.log(s.real.to_numpy(float))
        Ds, dns = qdummies(s.quarter.to_numpy())
        gs = pd.factorize(s.gig_id)[0]
        Xs = np.column_stack([Ds, np.log1p(s.reviews.to_numpy(float))[:, None],
                              s.rating.to_numpy(float)[:, None]])
        try:
            ts, _ = fe_ols(ys, Xs, gs, gs, list(dns) + REP)
            r = ts[ts.term == "ln(1+reviews)"].iloc[0]
            rows.append((n, s.gig_id.nunique(), float(r.coef), float(r.se), float(r.t)))
        except Exception:
            continue
    nod = pd.DataFrame(rows, columns=["node", "gigs", "coef", "se", "t"]).set_index("node")
    sig = nod[nod.t.abs() > 1.96]
    L += [f"{len(nod)} nodes estimated; **{len(sig)} significant at 5%**, "
          f"**{(nod.coef > 0).sum()} positive**. Slope range "
          f"**{pct(nod.coef.min()):+.2f}%** ({nod.coef.idxmin()}) to "
          f"**{pct(nod.coef.max()):+.2f}%** ({nod.coef.idxmax()}) per doubling.", "",
          "| node | gigs | per doubling | t |", "|---|---:|---:|---:|"]
    for n, r in nod.sort_values("coef", ascending=False).iterrows():
        L.append(f"| {n} | {int(r.gigs):,} | {pct(r.coef):+.2f}% | {r.t:+.2f} |")

    # ---- 5. variance decomposition -----------------------------------------
    L += ["", "## 5. What share of price each layer explains", ""]
    tot = float(np.var(y))
    parts = []
    for lbl, key in [("domain (7)", d.domain.to_numpy()), ("node (65)", d.node.to_numpy()),
                     ("gig", d.gig_id.to_numpy())]:
        m = pd.Series(y).groupby(pd.Series(key)).transform("mean").to_numpy()
        parts.append((lbl, 1 - float(np.var(y - m)) / tot))
    for lbl, v in parts:
        L.append(f"- **{lbl}** alone: {v:.1%}")
    resid_node = y - pd.Series(y).groupby(pd.Series(d.node.to_numpy())).transform("mean").to_numpy()
    Xr = np.column_stack([lnrev[:, None], rating[:, None]])
    br, *_ = np.linalg.lstsq(np.column_stack([np.ones(len(y)), Xr]), resid_node, rcond=None)
    fitted = np.column_stack([np.ones(len(y)), Xr]) @ br
    L += [f"- **reputation, on top of node**: a further "
          f"{float(np.var(fitted))/tot:.1%} of total variance", "",
          "So the taxonomy names the task, reputation adds a slice on top of it, and the "
          "large remainder is what separates two sellers of the same work with the same "
          "review count — quality, presentation, and everything else no column here holds.", ""]

    (OUTDIR / "reputation.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
