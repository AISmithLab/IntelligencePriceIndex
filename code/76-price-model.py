#!/usr/bin/env python3
"""
Step 76: does real price move with AI exposure after ChatGPT, once task value,
inflation and reputation are taken out?

THE SPECIFICATION, in the order the user posed it:

  1. DEFLATE. Posted prices are nominal. Divide by CPI-U so the outcome is a
     real price in 2020Q1 dollars, exactly as `23-real-index.py` does it
     (SA series, quarterly average, Real = Nominal * CPI_base / CPI_t).
  2. TASK VALUE (x) and REPUTATION (z). Reputation is time-varying and estimated:
     `ln(1 + review_count)` is the reputation treadmill step 22/27 measured, and
     `rating` is the quality signal beside it. Task value is time-INVARIANT --
     what this particular piece of work is intrinsically worth -- so it is the
     gig fixed effect, absorbed during estimation and recovered afterwards as
     the per-gig intercept. That is the right home for it: no observable in this
     data measures task value directly, and pretending otherwise would put a
     proxy where a fixed effect belongs.
  3. THE AI TEST. With x and z out, is the residual price variation associated
     with AI exposure after the launch?

         ln(real price)_it = a_i + d_t + b1*ln(1+rev)_it + b2*rating_it
                             + g*(Exposure_c x Post_t) + e_it

     `a_i` gig FE, `d_t` quarter FE, SEs clustered on gig. Exposure_c alone is
     absorbed by the gig FE and Post_t by the quarter FE; the interaction is
     what identifies g, and it is a difference-in-differences in everything but
     name -- so it inherits every objection that killed the earlier ones.

WHICH EXPOSURE MEASURE, AND WHY THE ORDER MATTERS. Two are available and they
disagree, so the choice cannot be made after seeing the result:

  PRIMARY    `data/exposure-ranking.csv` -- Eloundou et al. human-annotated
             occupation exposure, PRE-REGISTERED in
             `plans/active/transaction-volume-prereg.md`. It is the weaker
             measure (constant per category, 36.8% zero-match) but it is the one
             locked before any outcome was seen.
  SECONDARY  `runs/ai-slug-diffusion/diffusion.md` -- step 75's share of newly
             archived gigs whose title advertises AI, per category per quarter.
             Better in every technical respect: measured inside this market,
             time-varying, so it is identified against BOTH fixed effects
             without needing a Post interaction. But it ranks the categories
             almost opposite to the pre-registration (translation least exposed,
             coding most; the prereg has translation HIGH and coding
             quarantined), so swapping it in as primary is exactly the
             specification search the prereg exists to stop. It is reported as a
             declared robustness and labelled exploratory.

THE BATTERY IS NOT OPTIONAL. `29-chained-elasticity-audit.py` found the
project's headline elasticity was a spurious regression: a linear time trend fit
better than the AI score, CPI-U returned comparable coefficients, and the
relationship vanished in first differences. Every specification here is run
through that battery and the result is reported as descriptive unless it passes
all of it:

  A  PRE-TRENDS   Exposure x each pre-launch quarter. Any significant pre-period
                  interaction and parallel trends fails -- the prereg makes this
                  a gate, not a diagnostic.
  B  TREND RACE   add Exposure_c x linear trend. If g collapses, the "effect"
                  was a trend that happens to correlate with exposure.
  C  PLACEBO      the same spec with a false break at 2019Q2, pre-period only.
  D  DIFFERENCES  re-fit on within-gig first differences.
  E  INFERENCE    gig-clustered SEs throughout, printed beside unclustered ones,
                  because step 22 shipped an unclustered SE that was 1.93x too
                  small.
  F  POWER        MDE at 80% power, so a null is interpretable as a null rather
                  than as silence.

Input:  data/pilot/balanced-prices.csv
        data/pilot/balanced-gig-category.csv.gz
        data/cpi-u.csv
        data/exposure-ranking.csv
        runs/ai-slug-diffusion/diffusion.md   (secondary exposure, optional)
Output: runs/price-model/model.md  (+ per-gig task value to task-value.csv)
"""

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "code"))
from gigfilter import is_gig

def _first_present(*paths):
    """First path that exists. The 88 MB CSVs are gitignored and the 8 MB gzips
    are committed, so a fresh clone resolves to the same panel, not a fallback."""
    for q in paths:
        if q.exists():
            return q
    return paths[0]


PRICES = _first_present(BASE_DIR / "data" / "pilot" / "balanced-prices.csv",
                        BASE_DIR / "data" / "pilot" / "balanced-prices.csv.gz")
CATEGORY = BASE_DIR / "data" / "pilot" / "balanced-gig-category.csv.gz"
CPI = BASE_DIR / "data" / "cpi-u.csv"
EXPOSURE = BASE_DIR / "data" / "exposure-ranking.csv"
SLUG_AI = BASE_DIR / "runs" / "ai-slug-diffusion" / "diffusion.md"
OUTDIR = BASE_DIR / "runs" / "price-model"

CHATGPT_LAUNCH = "2022Q4"      # project convention, and the prereg's break
PLACEBO_BREAK = "2019Q2"       # prereg's placebo break, used when in window
CPI_BASE = "2020Q1"            # published index base
PRICE_MAX = 10000.0
RATING_MAX = 5.0               # 1,303 rows carry a 10-point rating; not our scale


def q_to_int(q):
    return int(q[:4]) * 4 + int(q[5]) - 1


def to_quarter(y, m):
    return f"{int(y)}Q{(int(m) - 1) // 3 + 1}"


# ---------------------------------------------------------------- panel
def build_panel(prices=None, category=None):
    """Gig-quarter panel carrying real price, reviews and rating.

    Mirrors `64-event-study-twfe.py:build_panel` filter for filter -- is_gig,
    known category, 0 < price <= PRICE_MAX, gig-quarter median -- and adds the
    two reputation columns it does not carry. Reviews are cumulative, so the
    quarter's MAX is the level at quarter end; price and rating take the median.
    """
    px = pd.read_csv(prices or PRICES)
    n0 = len(px)
    px = px[px.seller.map(is_gig)].copy()
    px["gig_id"] = px.seller + "/" + px.slug
    px = px.merge(pd.read_csv(category or CATEGORY), on="gig_id", how="inner")
    px = px[(px.price_basic > 0) & (px.price_basic <= PRICE_MAX)]
    px.loc[px.rating > RATING_MAX, "rating"] = np.nan
    px["quarter"] = [to_quarter(y, m) for y, m in zip(px.year, px.month)]

    gq = (px.groupby(["gig_id", "category", "quarter"], observed=True)
            .agg(price=("price_basic", "median"),
                 rating=("rating", "median"),
                 reviews=("review_count", "max"))
            .reset_index())
    gq["qi"] = gq.quarter.map(q_to_int)

    # deflate: real = nominal * CPI_base / CPI_t, SA, quarterly average (step 23)
    cpi = pd.read_csv(CPI)
    cpi["quarter"] = [f"{m[:4]}Q{(int(m[5:7]) - 1) // 3 + 1}" for m in cpi.month]
    cq = cpi.groupby("quarter").cpi_sa.mean()
    base = cq[CPI_BASE]
    gq["cpi"] = gq.quarter.map(cq)
    gq = gq[gq.cpi.notna()]
    gq["real"] = gq.price * base / gq.cpi

    gq.attrs["rows_in"], gq.attrs["rows_kept"] = n0, len(px)
    return gq.sort_values(["gig_id", "qi"]).reset_index(drop=True)


# ---------------------------------------------------------------- estimator
def fe_ols(y, X, g, names, cluster=True):
    """Within-gig demeaned OLS. Returns (coef, se, extras).

    Gig FE absorbed by demeaning (Frisch-Waugh) so 30k dummies never allocate.
    Cluster-robust variance on `g`, the same unit step 21's bootstrap resamples.
    """
    ng = int(g.max()) + 1
    cnt = np.bincount(g, minlength=ng).astype(float)
    dm = lambda v: v - (np.bincount(g, weights=v, minlength=ng) / cnt)[g]

    yd = dm(y)
    Xd = np.column_stack([dm(X[:, j]) for j in range(X.shape[1])])
    XtXi = np.linalg.pinv(Xd.T @ Xd)
    b = XtXi @ (Xd.T @ yd)
    u = yd - Xd @ b
    n, k = Xd.shape
    dof = max(n - k - ng, 1)

    if cluster:
        o = np.argsort(g, kind="stable")
        gs, Xs, us = g[o], Xd[o], u[o]
        meat = np.zeros((k, k))
        bnd = np.flatnonzero(np.diff(gs)) + 1
        for a, bq in zip(np.r_[0, bnd], np.r_[bnd, len(gs)]):
            s = Xs[a:bq].T @ us[a:bq]
            meat += np.outer(s, s)
        V = XtXi @ meat @ XtXi * (ng / (ng - 1)) * ((n - 1) / dof)
    else:
        V = XtXi * float(u @ u) / dof
    se = np.sqrt(np.clip(np.diag(V), 0, None))

    # gig intercepts: the part of ln(real price) no regressor and no quarter explains
    alpha = (np.bincount(g, weights=y - X @ b, minlength=ng) / cnt)
    r2w = 1 - float(u @ u) / max(float(yd @ yd), 1e-12)
    return (pd.DataFrame({"term": names, "coef": b, "se": se,
                          "t": b / np.where(se > 0, se, np.nan)}),
            {"obs": n, "gigs": ng, "dof": dof, "within_r2": r2w, "alpha": alpha,
             "resid_sd": float(np.std(u))})


def qdummies(quarters, base):
    cols = [q for q in sorted(set(quarters), key=q_to_int) if q != base]
    pos = {q: j for j, q in enumerate(cols)}
    D = np.zeros((len(quarters), len(cols)))
    for i, q in enumerate(quarters):
        j = pos.get(q)
        if j is not None:
            D[i, j] = 1.0
    return D, [f"Q:{c}" for c in cols]


def mde(se, power=0.80, alpha=0.05):
    """Two-sided MDE at the given power -- (1.96 + 0.84) * se."""
    from math import sqrt
    return (1.959964 + 0.841621) * se


# ---------------------------------------------------------------- exposure
def load_slug_exposure():
    """Step 75's per-(category, quarter) AI-branded share, from its report."""
    if not SLUG_AI.exists():
        return None
    md = SLUG_AI.read_text()
    if "AI_GEN share of gigs first captured" not in md:
        return None
    sec = md.split("AI_GEN share of gigs first captured", 1)[1]
    cats, rows = None, []
    for line in sec.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells[0] == "quarter":
            cats = cells[1:]
        elif re.match(r"^\d{4}Q[1-4]$", cells[0]) and cats:
            for c, v in zip(cats, cells[1:]):
                if v not in ("--", ""):
                    rows.append((c, cells[0], float(v.rstrip("%")) / 100.0))
    return pd.DataFrame(rows, columns=["category", "quarter", "ai_share"]) if rows else None


# ---------------------------------------------------------------- the runs
def design(d, exposure, post_cut=CHATGPT_LAUNCH, base=None, extra=None):
    """Build (y, X, names, g) for the main specification.

    `exposure` is a per-gig scalar (Eloundou, constant within category) or, when
    `d` already carries `ai_share`, the time-varying column is used directly and
    no Post interaction is needed.
    """
    base = base or sorted(d.quarter.unique(), key=q_to_int)[0]
    y = np.log(d.real.to_numpy(float))
    D, dn = qdummies(d.quarter.to_numpy(), base)
    cols, names = [D], list(dn)
    cols.append(np.log1p(d.reviews.to_numpy(float))[:, None]); names.append("ln(1+reviews)")
    cols.append(d.rating.to_numpy(float)[:, None]); names.append("rating")
    if exposure is not None:
        post = (d.qi >= q_to_int(post_cut)).to_numpy(float)
        cols.append((exposure * post)[:, None]); names.append("Exposure x Post")
    if extra:
        for nm, v in extra:
            cols.append(v[:, None]); names.append(nm)
    g = pd.factorize(d.gig_id)[0]
    return y, np.column_stack(cols), names, g


def fmt(tab, terms):
    out = []
    for t in terms:
        r = tab[tab.term == t]
        if r.empty:
            continue
        c, s, tv = float(r.coef.iloc[0]), float(r.se.iloc[0]), float(r.t.iloc[0])
        star = "***" if abs(tv) > 2.576 else "**" if abs(tv) > 1.96 else ""
        out.append(f"| {t} | {c:+.4f} | {s:.4f} | {tv:+.2f}{star} | "
                   f"[{c-1.96*s:+.4f}, {c+1.96*s:+.4f}] | {100*np.expm1(c):+.2f}% |")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2019Q4", help="panel window start")
    ap.add_argument("--end", default="2024Q4", help="panel window end (archive ceiling)")
    ap.add_argument("--balanced", action="store_true", default=True,
                    help="keep only gigs observed both before and after the cut")
    args = ap.parse_args()

    OUTDIR.mkdir(parents=True, exist_ok=True)
    L = ["# Real price, task value, reputation, and AI exposure", ""]

    gq = build_panel()
    lo, hi = q_to_int(args.start), q_to_int(args.end)
    d = gq[(gq.qi >= lo) & (gq.qi <= hi)].copy()
    d = d[d.reviews.notna() & d.rating.notna() & (d.real > 0)]
    cut = q_to_int(CHATGPT_LAUNCH)
    pre, post = set(d.gig_id[d.qi < cut]), set(d.gig_id[d.qi >= cut])
    d = d[d.gig_id.isin(pre & post)].copy()
    d = d.sort_values(["gig_id", "qi"]).reset_index(drop=True)

    L += [f"Panel: **{len(d):,} gig-quarter observations**, "
          f"**{d.gig_id.nunique():,} gigs**, {args.start}–{args.end}, "
          f"restricted to gigs seen both before and after {CHATGPT_LAUNCH}.",
          f"Prices deflated to {CPI_BASE} dollars with CPI-U (SA, quarterly mean), "
          f"as `23-real-index.py`. Rows without a rating or review count are dropped "
          f"({len(gq[(gq.qi >= lo) & (gq.qi <= hi)]) - len(d):,} of "
          f"{len(gq[(gq.qi >= lo) & (gq.qi <= hi)]):,} in-window rows).", "",
          "| category | gigs | obs | median real price | median reviews |",
          "|---|---:|---:|---:|---:|"]
    for c, s in d.groupby("category"):
        L.append(f"| {c} | {s.gig_id.nunique():,} | {len(s):,} | "
                 f"${s.real.median():,.2f} | {s.reviews.median():,.0f} |")

    # ---------------- 1. inflation ------------------------------------------
    nom, real = np.log(d.price).mean(), np.log(d.real).mean()
    L += ["", "## 1. Deflation", "",
          f"Mean ln price falls from **{nom:.4f}** nominal to **{real:.4f}** real "
          f"({100*np.expm1(real-nom):+.1f}%): that is the general price level over the "
          f"window, removed before anything else is estimated.", ""]

    # ---------------- 2. reputation + task value ----------------------------
    expo = pd.read_csv(EXPOSURE).set_index("category").exposure_primary
    e_vec = d.category.map(expo).to_numpy(float)

    y, X, names, g = design(d, None)
    t0, x0 = fe_ols(y, X, g, names)
    L += ["## 2. Reputation (z) and task value (x)", "",
          "Baseline, no AI term: `ln(real price) ~ gig FE + quarter FE + ln(1+reviews) + rating`. "
          "SEs clustered on gig.", "",
          "| term | coef | se | t | 95% CI | effect |", "|---|---:|---:|---:|---|---:|"]
    L += fmt(t0, ["ln(1+reviews)", "rating"])
    b_rev = float(t0[t0.term == "ln(1+reviews)"].coef.iloc[0])
    L += ["", f"**Reputation.** A doubling of cumulative reviews carries "
              f"**{100*np.expm1(b_rev*np.log(2)):+.2f}%** in real price. "
              f"Step 22/27 measured +7.7% on the shipped panels; this is the same "
              f"treadmill re-estimated on the balanced panel in real terms.",
          "", f"Within-gig R² = {x0['within_r2']:.4f}. Residual SD = {x0['resid_sd']:.4f} log points.", ""]

    # task value = the recovered gig intercept
    gid = pd.factorize(d.gig_id)[0]
    tv = (pd.DataFrame({"gig_id": d.gig_id.to_numpy()[np.unique(gid, return_index=True)[1]],
                        "x": x0["alpha"]})
          .merge(d[["gig_id", "category"]].drop_duplicates(), on="gig_id"))
    tv.to_csv(OUTDIR / "task-value.csv", index=False)
    L += ["**Task value.** Time-invariant by construction, so it is the gig fixed effect, "
          "recovered after fitting as the per-gig intercept — the log real price this "
          "particular piece of work commands net of inflation, the common quarter path and "
          "reputation. Written to `runs/price-model/task-value.csv`.", "",
          "| category | n | median x | implied real price | IQR of x |", "|---|---:|---:|---:|---:|"]
    for c, s in tv.groupby("category"):
        L.append(f"| {c} | {len(s):,} | {s.x.median():+.3f} | ${np.exp(s.x.median()):,.2f} | "
                 f"{s.x.quantile(.25):+.3f} … {s.x.quantile(.75):+.3f} |")
    L += ["", f"Task value spans **{tv.x.std():.3f}** log points SD across "
              f"{len(tv):,} gigs — far more variation than anything time-varying in this "
              f"model, which is why it belongs in the fixed effect rather than a proxy.", ""]

    # ---------------- 3. the AI test ----------------------------------------
    y, X, names, g = design(d, e_vec)
    t1, x1 = fe_ols(y, X, g, names)
    t1u, _ = fe_ols(y, X, g, names, cluster=False)
    row = t1[t1.term == "Exposure x Post"]
    gam, gse = float(row.coef.iloc[0]), float(row.se.iloc[0])
    gse_u = float(t1u[t1u.term == "Exposure x Post"].se.iloc[0])

    L += ["## 3. AI exposure after ChatGPT", "",
          "**PRIMARY — pre-registered exposure.** Eloundou human-annotated occupation "
          "exposure (`exposure_primary`), constant per category, interacted with "
          f"`Post = 1[quarter >= {CHATGPT_LAUNCH}]`.", "",
          "| term | coef | se | t | 95% CI | effect |", "|---|---:|---:|---:|---|---:|"]
    L += fmt(t1, ["Exposure x Post", "ln(1+reviews)", "rating"])
    lo_e, hi_e = expo.min(), expo.max()
    L += ["", f"Exposure runs {lo_e:.2f} (audio) to {hi_e:.2f} (translation), a spread of "
              f"{hi_e-lo_e:.2f}, so the coefficient scales to a "
              f"**{100*np.expm1(gam*(hi_e-lo_e)):+.2f}%** real-price gap between the least "
              f"and most exposed category after the launch.", ""]

    # ---------------- 4. the battery ----------------------------------------
    L += ["## 4. The battery", "",
          "`29-chained-elasticity-audit.py` found the project's earlier AI result was a "
          "spurious regression. Nothing here is reported as a finding until it survives "
          "all of this.", ""]

    # A. pre-trends
    preq = [q for q in sorted(d.quarter.unique(), key=q_to_int) if q_to_int(q) < cut]
    ex_pre = []
    for q in preq[1:]:
        ex_pre.append((f"Exp x {q}", e_vec * (d.quarter == q).to_numpy(float)))
    y2, X2, n2, g2 = design(d, e_vec, extra=ex_pre)
    t2, _ = fe_ols(y2, X2, g2, n2)
    sig = t2[t2.term.str.startswith("Exp x ") & (t2.t.abs() > 1.96)]
    gateA = "**PASS**" if len(sig) == 0 else f"**FAIL** — {len(sig)} of {len(ex_pre)} significant"
    L += [f"**A · Parallel trends (gate).** Exposure interacted with each pre-launch "
          f"quarter: {gateA}. The pre-registration makes this pass/fail, with synthetic "
          f"control the only authorised fallback.", ""]
    if len(sig):
        L += ["| pre-period interaction | coef | t |", "|---|---:|---:|"]
        for _, r in sig.iterrows():
            L.append(f"| {r.term} | {r.coef:+.4f} | {r.t:+.2f} |")
        L.append("")

    # B. trend horse race
    trend = (d.qi - d.qi.min()).to_numpy(float)
    y3, X3, n3, g3 = design(d, e_vec, extra=[("Exposure x trend", e_vec * trend)])
    t3, _ = fe_ols(y3, X3, g3, n3)
    g3v = float(t3[t3.term == "Exposure x Post"].coef.iloc[0])
    t3v = float(t3[t3.term == "Exposure x Post"].t.iloc[0])
    tr_c = float(t3[t3.term == "Exposure x trend"].coef.iloc[0])
    tr_t = float(t3[t3.term == "Exposure x trend"].t.iloc[0])
    if gam * g3v < 0:
        verdict = ("**FAIL** — the coefficient changes SIGN. Whatever `Exposure x Post` "
                   "was picking up, a trend explains it better.")
    elif abs(g3v) < 0.5 * abs(gam):
        verdict = "**FAIL** — the coefficient collapses by more than half."
    else:
        verdict = "**PASS** — the coefficient survives the trend."
    L += [f"**B · Linear-trend horse race.** Adding `Exposure x trend` moves "
          f"`Exposure x Post` from **{gam:+.4f}** (t {float(row.t.iloc[0]):+.2f}) to "
          f"**{g3v:+.4f}** (t {t3v:+.2f}). `Exposure x trend` itself is "
          f"{tr_c:+.5f} (t {tr_t:+.2f}"
          f"{', significant' if abs(tr_t) > 1.96 else ''}). {verdict}", ""]

    # C. placebo -- a false break strictly inside the pre-period, so the test is
    # not vacuous. The prereg's 2019Q2 lies before this panel starts, which would
    # make Post all-ones and the interaction collinear with the gig effects; the
    # midpoint of the observed pre-period is used instead and named in the output.
    dp = d[d.qi < cut].copy()
    preqs = sorted(dp.quarter.unique(), key=q_to_int)
    pb = PLACEBO_BREAK if PLACEBO_BREAK in preqs[1:-1] else preqs[len(preqs) // 2]
    if dp.gig_id.nunique() > 100 and len(preqs) >= 4:
        ep = dp.category.map(expo).to_numpy(float)
        y4, X4, n4, g4 = design(dp, ep, post_cut=pb)
        t4, _ = fe_ols(y4, X4, g4, n4)
        r4 = t4[t4.term == "Exposure x Post"]
        t4v = float(r4.t.iloc[0])
        L += [f"**C · Placebo break at {pb}** — a false break inside the pre-period "
              f"({len(dp):,} obs / {dp.gig_id.nunique():,} gigs, {preqs[0]}–{preqs[-1]}). "
              f"The prereg's {PLACEBO_BREAK} sits before this panel opens, which would "
              f"make `Post` all-ones and the interaction collinear; the pre-period "
              f"midpoint is used instead. "
              f"Estimate {float(r4.coef.iloc[0]):+.4f} (t {t4v:+.2f}) — "
              f"{'**FAIL**, a break appears where none exists' if abs(t4v) > 1.96 else '**PASS**'}.", ""]

    # D. first differences
    dd = d.copy()
    dd["dln"] = dd.groupby("gig_id").apply(
        lambda s: np.log(s.real).diff(), include_groups=False).reset_index(level=0, drop=True)
    dd["drev"] = dd.groupby("gig_id").apply(
        lambda s: np.log1p(s.reviews).diff(), include_groups=False).reset_index(level=0, drop=True)
    dd["dpost"] = dd.groupby("gig_id").apply(
        lambda s: (s.qi >= cut).astype(float).diff(), include_groups=False).reset_index(level=0, drop=True)
    fd = dd.dropna(subset=["dln", "drev", "dpost"])
    if len(fd) > 1000:
        efd = fd.category.map(expo).to_numpy(float)
        Dq, dn = qdummies(fd.quarter.to_numpy(), sorted(fd.quarter.unique(), key=q_to_int)[0])
        Xf = np.column_stack([Dq, fd.drev.to_numpy(float)[:, None],
                              (efd * fd.dpost.to_numpy(float))[:, None]])
        nf = list(dn) + ["d ln(1+reviews)", "Exposure x dPost"]
        gf = pd.factorize(fd.gig_id)[0]
        t5, _ = fe_ols(fd.dln.to_numpy(float), Xf, gf, nf)
        r5 = t5[t5.term == "Exposure x dPost"]
        L += [f"**D · First differences** ({len(fd):,} within-gig changes): "
              f"{float(r5.coef.iloc[0]):+.4f} (t {float(r5.t.iloc[0]):+.2f}) — "
              f"{'survives' if abs(float(r5.t.iloc[0])) > 1.96 else '**does not survive**'} "
              f"differencing.", ""]

    # E/F inference + power
    L += [f"**E · Inference.** Gig-clustered SE **{gse:.4f}** against unclustered "
          f"{gse_u:.4f} — clustering inflates it {gse/gse_u:.2f}x. Step 22 shipped the "
          f"unclustered one; this reports the clustered one.", "",
          f"**F · Power.** MDE at 80% power is **{mde(gse):.4f}** log points on the "
          f"interaction, i.e. **{100*np.expm1(mde(gse)*(hi_e-lo_e)):.2f}%** across the "
          f"exposure spread. The point estimate is {abs(gam):.4f}, "
          f"**{'BELOW' if abs(gam) < mde(gse) else 'ABOVE'}** that. "
          + ("So this null does not rule out an effect up to the MDE — it is a "
             "silence, not a zero, and must be reported as one."
             if abs(gam) < mde(gse) else
             "So the design could have seen an effect of this size.") , ""]

    # ---------------- 5. secondary exposure ---------------------------------
    slug = load_slug_exposure()
    if slug is not None:
        ds = d.merge(slug, on=["category", "quarter"], how="inner")
        if len(ds) > 1000:
            ai = ds.ai_share.to_numpy(float)
            ys, Xs_, ns, gs_ = design(ds, None, extra=[("AI share (cat x quarter)", ai)])
            t6, x6 = fe_ols(ys, Xs_, gs_, ns)
            r6 = t6[t6.term == "AI share (cat x quarter)"]
            c6, s6 = float(r6.coef.iloc[0]), float(r6.se.iloc[0])
            L += ["## 5. Secondary, exploratory — step 75's market-measured exposure", "",
                  "**Not pre-registered.** Step 75's AI-branded share varies by category AND "
                  "quarter, so it enters directly and is identified against both fixed "
                  "effects with no Post interaction. It also ranks the categories nearly "
                  "opposite to the pre-registration, which is why it cannot be promoted "
                  "to primary after the fact.", "",
                  f"Sample {len(ds):,} obs / {ds.gig_id.nunique():,} gigs.", "",
                  "| term | coef | se | t | 95% CI | effect |", "|---|---:|---:|---:|---|---:|"]
            L += fmt(t6, ["AI share (cat x quarter)", "ln(1+reviews)", "rating"])
            L += ["", f"Scaled: a 10pp rise in a category's AI-branded share is associated "
                      f"with **{100*np.expm1(c6*0.10):+.2f}%** in real price "
                      f"(95% CI {100*np.expm1((c6-1.96*s6)*0.10):+.2f}% to "
                      f"{100*np.expm1((c6+1.96*s6)*0.10):+.2f}%).", "",
                  "That is a large, tightly-estimated coefficient — which is precisely "
                  "when step 29's lesson applies hardest. `AI share` varies at the "
                  "category-by-quarter level, so it will absorb ANY category-specific "
                  "time path, AI-driven or not. Two tests decide whether it is measuring "
                  "AI or measuring trend.", ""]

            # B' -- category-specific linear trends. The sharpest test available:
            # if AI share only proxies "coding rose and translation did not", it dies here.
            cats_s = sorted(ds.category.unique())[1:]      # one absorbed
            trs = (ds.qi - ds.qi.min()).to_numpy(float)
            extra_tr = [(f"trend x {c}", trs * (ds.category == c).to_numpy(float))
                        for c in cats_s]
            y7, X7, n7, g7 = design(ds, None,
                                    extra=[("AI share (cat x quarter)", ai)] + extra_tr)
            t7, _ = fe_ols(y7, X7, g7, n7)
            r7 = t7[t7.term == "AI share (cat x quarter)"]
            c7, t7v = float(r7.coef.iloc[0]), float(r7.t.iloc[0])
            surv = (c6 * c7 > 0) and abs(c7) > 0.5 * abs(c6) and abs(t7v) > 1.96
            L += [f"**Category-specific linear trends.** Adding one trend per category "
                  f"moves the coefficient from **{c6:+.4f}** (t {float(r6.t.iloc[0]):+.2f}) "
                  f"to **{c7:+.4f}** (t {t7v:+.2f}); the 10pp effect goes from "
                  f"{100*np.expm1(c6*0.10):+.2f}% to {100*np.expm1(c7*0.10):+.2f}%. "
                  + ("**PASS** — it is not a category trend in disguise." if surv else
                     "**FAIL** — most of it was a category-specific trend, not AI."), ""]

            # D' -- first differences on the same sample
            ds2 = ds.sort_values(["gig_id", "qi"]).copy()
            gb = ds2.groupby("gig_id")
            ds2["dln"] = gb.apply(lambda x: np.log(x.real).diff(),
                                  include_groups=False).reset_index(level=0, drop=True)
            ds2["drev"] = gb.apply(lambda x: np.log1p(x.reviews).diff(),
                                   include_groups=False).reset_index(level=0, drop=True)
            ds2["dai"] = gb.apply(lambda x: x.ai_share.diff(),
                                  include_groups=False).reset_index(level=0, drop=True)
            fd2 = ds2.dropna(subset=["dln", "drev", "dai"])
            if len(fd2) > 1000:
                Dq2, dn2 = qdummies(fd2.quarter.to_numpy(),
                                    sorted(fd2.quarter.unique(), key=q_to_int)[0])
                X8 = np.column_stack([Dq2, fd2.drev.to_numpy(float)[:, None],
                                      fd2.dai.to_numpy(float)[:, None]])
                t8, _ = fe_ols(fd2.dln.to_numpy(float), X8,
                               pd.factorize(fd2.gig_id)[0],
                               list(dn2) + ["d ln(1+reviews)", "d AI share"])
                r8 = t8[t8.term == "d AI share"]
                t8v = float(r8.t.iloc[0])
                L += [f"**First differences** ({len(fd2):,} within-gig changes): "
                      f"{float(r8.coef.iloc[0]):+.4f} (t {t8v:+.2f}) — "
                      + ("survives differencing." if abs(t8v) > 1.96 else
                         "**does not survive** differencing."), ""]

    (OUTDIR / "model.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
