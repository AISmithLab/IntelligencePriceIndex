#!/usr/bin/env python3
"""
Step 64: shared panel builder + two-way fixed-effects event study.

Written for `notebooks/00-explore.ipynb`, which needs the same panel the index
builders use but as a dataframe rather than the nested dicts steps 19/21 pass
around. Nothing here is a new estimator for the papers -- the GEKS index the
notebook plots is imported from `21-geks-index.py` unchanged. What IS new is the
two-way FE event study, which no step implements: steps 19/43 fit a pooled TPD
regression whose quarter effects are an index, not an event path around a date.

The two differ only in framing, and the framing matters. `event_study()` fixes
the sample to gigs observed on BOTH sides of a cut quarter, so the quarter
effects cannot move because the composition of gigs changed -- the objection
that kills a naive before/after on this panel, where entry is heavy and entrants
price above incumbents (step 57 S4).

WHAT THIS DESIGN DOES AND DOES NOT IDENTIFY. There is no control group. Every
gig is "treated" by ChatGPT on the same date, so the quarter effects are the
common time path of price on a fixed panel, net of gig level. That is a
descriptive series, and reading a causal effect off it requires assuming price
would have been flat absent the launch -- which the pre-trend printed by
`pretrend_test()` refutes on this data. Designs with a control group are steps
50/53/58 and the niche design of step 61; all of them failed, and the diagnosis
recorded in plans/todo.md is precisely that the trend predates ChatGPT. This
function exists to SHOW that pre-trend, not to work around it.

Estimation is by within-gig demeaning (Frisch-Waugh), so the gig effects are
absorbed rather than estimated -- 16k dummies never enter memory. SEs are
clustered on gig. No statsmodels/linearmodels dependency, deliberately: the
notebook is meant to run on a fresh clone with pandas and numpy only.
"""

import numpy as np
import pandas as pd

CHATGPT_LAUNCH = "2022Q4"      # public release 2022-11-30
DEFAULT_BASE = "2022Q3"        # last fully pre-launch quarter; omitted category


def to_quarter(year, month):
    return f"{int(year)}Q{(int(month) - 1) // 3 + 1}"


def q_to_int(q):
    y, qq = q.split("Q")
    return int(y) * 10 + int(qq)


def build_panel(prices_csv, category_csv, price_col="price_basic", price_max=10000.0):
    """Price CSV -> tidy gig-quarter panel, with steps 19/21's filters applied.

    Filters, in the order the index builders apply them: `is_gig` on the seller
    handle (drops /hire/ and /agencies/ landing pages -- see gigfilter.py), a
    known category, 0 < price <= PRICE_MAX, then the gig-quarter median.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from gigfilter import is_gig

    px = pd.read_csv(prices_csv)
    cat = pd.read_csv(category_csv)

    n0 = len(px)
    px = px[px.seller.map(is_gig)]
    px["gig_id"] = px.seller + "/" + px.slug
    px = px.merge(cat, on="gig_id", how="inner")
    px = px[(px[price_col] > 0) & (px[price_col] <= price_max)]
    px["quarter"] = [to_quarter(y, m) for y, m in zip(px.year, px.month)]

    gq = (px.groupby(["gig_id", "category", "quarter"], observed=True)[price_col]
            .median().reset_index())
    gq["qi"] = gq.quarter.map(q_to_int)
    gq.attrs["rows_in"] = n0
    gq.attrs["rows_kept"] = len(px)
    return gq.sort_values(["gig_id", "qi"]).reset_index(drop=True)


def to_nested(gq, price_col="price_basic"):
    """Tidy panel -> {category: {gig: {quarter: price}}}, the shape steps 19/21 take."""
    out = {}
    for (gid, cat), sub in gq.groupby(["gig_id", "category"], observed=True):
        out.setdefault(cat, {})[gid] = dict(zip(sub.quarter, sub[price_col]))
    return out


def balanced_sample(gq, cut=CHATGPT_LAUNCH, window=None):
    """Gigs observed at least once strictly before `cut` AND at least once at/after.

    This is the "same group of gigs before and after" restriction. It is applied
    AFTER the window trim, so widening the window changes the sample -- report
    both numbers together or the sample is not reproducible.
    """
    d = gq
    if window:
        lo, hi = q_to_int(window[0]), q_to_int(window[1])
        d = d[(d.qi >= lo) & (d.qi <= hi)]
    c = q_to_int(cut)
    pre, post = set(d.gig_id[d.qi < c]), set(d.gig_id[d.qi >= c])
    keep = pre & post
    d = d[d.gig_id.isin(keep)].copy()
    d.attrs["n_pre"], d.attrs["n_post"], d.attrs["n_balanced"] = len(pre), len(post), len(keep)
    return d


def event_study(d, base=DEFAULT_BASE, ycol="price_basic", cluster=True):
    """ln(price) ~ gig FE + quarter dummies. Returns (table, diagnostics).

    Gig FE absorbed by within-gig demeaning; `base` is the omitted quarter, so
    every coefficient reads as a log change relative to it. SEs clustered on gig
    (the unit resampled by step 21's bootstrap, and the level repeat observations
    are correlated at).
    """
    d = d[d[ycol] > 0].copy()
    y_raw = np.log(d[ycol].to_numpy(dtype=float))

    quarters = sorted(d.quarter.unique(), key=q_to_int)
    if base not in quarters:
        raise ValueError(f"base quarter {base} not in panel ({quarters[0]}..{quarters[-1]})")
    cols = [q for q in quarters if q != base]
    pos = {q: j for j, q in enumerate(cols)}
    D = np.zeros((len(d), len(cols)))
    for i, q in enumerate(d.quarter.to_numpy()):
        j = pos.get(q)
        if j is not None:
            D[i, j] = 1.0

    g = pd.factorize(d.gig_id)[0]
    ng = int(g.max()) + 1
    cnt = np.bincount(g, minlength=ng).astype(float)

    def demean(v):
        return v - (np.bincount(g, weights=v, minlength=ng) / cnt)[g]

    y = demean(y_raw)
    X = np.column_stack([demean(D[:, j]) for j in range(D.shape[1])])

    XtXi = np.linalg.pinv(X.T @ X)
    beta = XtXi @ (X.T @ y)
    u = y - X @ beta
    n, k = X.shape

    if cluster:
        order = np.argsort(g, kind="stable")
        gs, Xs, us = g[order], X[order], u[order]
        meat = np.zeros((k, k))
        bounds = np.flatnonzero(np.diff(gs)) + 1
        for a, b in zip(np.r_[0, bounds], np.r_[bounds, len(gs)]):
            s = Xs[a:b].T @ us[a:b]
            meat += np.outer(s, s)
        adj = (ng / (ng - 1)) * ((n - 1) / max(n - k - ng, 1))
        V = XtXi @ meat @ XtXi * adj
    else:
        V = XtXi * float(u @ u) / max(n - k - ng, 1)
    se = np.sqrt(np.clip(np.diag(V), 0, None))

    tab = pd.concat([
        pd.DataFrame({"quarter": cols, "coef": beta, "se": se}),
        pd.DataFrame({"quarter": [base], "coef": [0.0], "se": [0.0]}),
    ])
    tab["qi"] = tab.quarter.map(q_to_int)
    tab = tab.sort_values("qi").reset_index(drop=True)
    tab["ci_lo"] = tab.coef - 1.96 * tab.se
    tab["ci_hi"] = tab.coef + 1.96 * tab.se
    tab["pct"] = 100 * (np.expm1(tab.coef))
    diag = {"obs": n, "gigs": ng, "quarters": len(quarters), "base": base,
            "first": quarters[0], "last": quarters[-1]}
    return tab, diag


def pretrend_test(tab, cut=CHATGPT_LAUNCH):
    """Fit a line to the PRE-cut coefficients, extrapolate it past the cut.

    The event path is only evidence about the launch if it is flat beforehand.
    Returns the fitted slope (log points per quarter), its t-ratio, and the
    post-cut residual -- observed minus the counterfactual the pre-trend implies.
    A residual near zero means the post period is the pre-trend continuing, which
    is the null the papers' failed designs kept landing on.
    """
    c = q_to_int(cut)
    pre = tab[tab.qi < c]
    if len(pre) < 3:
        return None
    t = np.arange(len(pre), dtype=float)
    A = np.column_stack([np.ones_like(t), t])
    b, *_ = np.linalg.lstsq(A, pre.coef.to_numpy(), rcond=None)
    resid = pre.coef.to_numpy() - A @ b
    dof = len(pre) - 2
    s2 = float(resid @ resid) / dof if dof > 0 else np.nan
    se_b = np.sqrt(s2 * np.linalg.pinv(A.T @ A)[1, 1]) if dof > 0 else np.nan

    tt = np.arange(len(tab), dtype=float)
    counterfactual = b[0] + b[1] * tt
    out = tab.copy()
    out["pretrend"] = counterfactual
    out["gap"] = out.coef - out.pretrend
    return {"slope": float(b[1]), "se": float(se_b),
            "t": float(b[1] / se_b) if se_b else np.nan,
            "pre_quarters": len(pre), "table": out,
            "gap_last": float(out.gap.iloc[-1])}
