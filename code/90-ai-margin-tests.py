#!/usr/bin/env python3
"""
Step 90: AI-exposure tests on margins the listed-price index cannot see.

EXPLORATORY, not pre-registered. Reads step 89's page and order fields, the
step-45 exposure ranking (unchanged) and the existing gig -> category maps.

  T1  price per word        word-priced gigs (writing/translation), within gig:
                            log real basic price per word, and its two parts
                            (log price, log words); interrupted time series,
                            plus a DiD against low-exposure gigs' log price
  T2  repeat buyers         order-level, Exposure x Post, gig + quarter FE
  T3  review text           share of reviews naming an AI tool / MT, by category;
                            rating gap on those reviews
  T4  seller country        share of gig-quarters from high-income sellers,
                            Exposure x Post, quarter FE (composition, no gig FE)
  T5  AI / anti-AI labels   share of gig descriptions mentioning generative AI,
                            or advertising human/no-AI work, by category
  T6  tier ladder           within-gig log(premium/basic), Exposure x Post
  T7  listed delivery time  within-gig log basic-package delivery hours and
                            revisions, Exposure x Post

Post = 1[quarter >= 2022Q4] (step 76). Page-level window 2019Q4-2024Q4 (the
price model's window; captures are dense, Post has 12 pre quarters). Order-level
window 2021Q4-2024Q4 (step 88). One observation per gig-quarter on page data
(the latest capture in the quarter).

INFERENCE. Exposure varies across 7 categories only. Gig-clustered SEs are
reported and are optimistic; every DiD also gets a wild-cluster bootstrap p on
CATEGORY clusters (Webb 6-point weights, 999 draws), which is the honest one.
With 7 clusters its smallest attainable p is coarse, so read it as a gate.

    python3 code/90-ai-margin-tests.py [--tag all]
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data/pilot"
EXPO = ROOT / "data/exposure-ranking.csv"
OUT = ROOT / "runs/ai-margin-tests.md"

POST = "2022Q4"
PAGE_WIN = ("2019Q4", "2024Q4")
ORD_WIN = ("2021Q4", "2024Q4")
LOW = ["audio", "video"]                  # the two lowest-exposure categories
HIGH_INCOME = {"US", "GB", "CA", "AU", "DE", "FR", "NL", "IT", "ES", "SE", "NO",
               "DK", "FI", "IE", "BE", "AT", "CH", "NZ", "IL", "JP", "KR", "SG",
               "PT", "GR", "LU", "IS", "AE", "SA", "QA", "KW", "HK", "TW", "CZ",
               "SI", "EE", "LV", "LT", "SK", "PL", "HR", "HU", "CY", "MT", "UY",
               "CL", "PA", "BH", "OM"}   # World Bank high-income, FY2024
RNG = np.random.default_rng(90)


# ---------------------------------------------------------------- estimation
def demean2(X, g, t, iters=100, tol=1e-9):
    X = np.asarray(X, float).copy()
    for _ in range(iters):
        old = X.copy()
        X -= pd.DataFrame(X).groupby(g).transform("mean").to_numpy()
        X -= pd.DataFrame(X).groupby(t).transform("mean").to_numpy()
        if np.abs(X - old).max() < tol:
            break
    return X


def demean1(X, t):
    X = np.asarray(X, float)
    return X - pd.DataFrame(X).groupby(t).transform("mean").to_numpy()


def cluster_se(X, e, cl, XtX_inv):
    S = pd.DataFrame(X * e[:, None]).groupby(cl).sum().to_numpy()
    G = len(S)
    return np.sqrt(np.diag(XtX_inv @ (S.T @ S) @ XtX_inv * G / (G - 1)))


WEBB = np.array([-np.sqrt(1.5), -1, -np.sqrt(.5), np.sqrt(.5), 1, np.sqrt(1.5)])


def wild_p(y, X, cl, b_obs, k=0, B=999):
    """Wild-cluster bootstrap-t p for coefficient k, null imposed (WCR)."""
    Xr = np.delete(X, k, axis=1)
    if Xr.shape[1]:
        br = np.linalg.lstsq(Xr, y, rcond=None)[0]
        fit_r = Xr @ br
    else:
        fit_r = np.zeros_like(y)
    er = y - fit_r
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ y
    t_obs = b[k] / cluster_se(X, y - X @ b, cl, XtX_inv)[k]
    codes, uniq = pd.factorize(cl)
    hits = 0
    for _ in range(B):
        w = RNG.choice(WEBB, size=len(uniq))[codes]
        ys = fit_r + er * w
        bs = XtX_inv @ X.T @ ys
        ts = bs[k] / cluster_se(X, ys - X @ bs, cl, XtX_inv)[k]
        hits += abs(ts) >= abs(t_obs)
    return (hits + 1) / (B + 1)


def did(d, y, expo, gig_fe=True, extra=None):
    """y on Exposure x Post (+extra), gig + quarter FE (or quarter FE only)."""
    d = d[d[y].notna() & d[expo].notna()].copy()
    if gig_fe:
        d = d[d.groupby("gig_id").gig_id.transform("size") > 1]
    if len(d) < 50 or d.category.nunique() < 2:
        return dict(b=np.nan, se=np.nan, t=np.nan, p_cat=np.nan, n=len(d),
                    gigs=d.gig_id.nunique(), mean=d[y].mean())
    post = (d.quarter >= POST).to_numpy(float)
    cols = [d[expo].to_numpy() * post]
    if extra:
        cols += [d[c].to_numpy(float) for c in extra]
    M = np.column_stack([d[y].to_numpy(float)] + cols)
    if gig_fe:
        M = demean2(M, d.gig_id.to_numpy(), d.quarter.to_numpy())
    else:
        M = demean1(M, d.quarter.to_numpy())
        # absorb category level too
        M = M - pd.DataFrame(M).groupby(d.category.to_numpy()).transform("mean").to_numpy()
    yv, X = M[:, 0], M[:, 1:]
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ yv
    e = yv - X @ b
    se_g = cluster_se(X, e, d.gig_id.to_numpy(), XtX_inv)
    p_cat = wild_p(yv, X, d.category.to_numpy(), b)
    return dict(b=b[0], se=se_g[0], t=b[0] / se_g[0], p_cat=p_cat, n=len(d),
                gigs=d.gig_id.nunique(), mean=d[y].mean())


def event(d, y, expo, ref="2022Q3"):
    d = d[d[y].notna()].copy()
    d = d[d.groupby("gig_id").gig_id.transform("size") > 1]
    qs = sorted(q for q in d.quarter.unique() if q != ref)
    if len(d) < 50 or not qs:
        return pd.DataFrame(columns=["quarter", "b", "t"])
    X = np.column_stack([d[expo].to_numpy() * (d.quarter == q).to_numpy(float) for q in qs])
    M = demean2(np.column_stack([d[y].to_numpy(float), X]), d.gig_id.to_numpy(),
                d.quarter.to_numpy())
    yv, X = M[:, 0], M[:, 1:]
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ yv
    se = cluster_se(X, yv - X @ b, d.gig_id.to_numpy(), XtX_inv)
    return pd.DataFrame({"quarter": qs, "b": b, "t": b / se})


def its(d, y):
    """Within-gig interrupted time series: gig FE, linear trend, Post, Post x trend."""
    d = d[d[y].notna()].copy()
    d = d[d.groupby("gig_id").gig_id.transform("size") > 1]
    if len(d) < 50:
        nan = (np.nan, np.nan)
        return dict(trend=nan, post=nan, post_trend=nan), len(d), d.gig_id.nunique()
    q0 = qn(POST)
    tr = (d.qn - q0).to_numpy(float)
    post = (d.qn >= q0).to_numpy(float)
    M = np.column_stack([d[y].to_numpy(float), tr, post, post * tr])
    M = M - pd.DataFrame(M).groupby(d.gig_id.to_numpy()).transform("mean").to_numpy()
    yv, X = M[:, 0], M[:, 1:]
    XtX_inv = np.linalg.pinv(X.T @ X)
    b = XtX_inv @ X.T @ yv
    se = cluster_se(X, yv - X @ b, d.gig_id.to_numpy(), XtX_inv)
    return dict(zip(["trend", "post", "post_trend"], zip(b, se))), len(d), d.gig_id.nunique()


def qn(q):
    """'2022Q4' -> integer quarter index; Series in, Series out."""
    if isinstance(q, str):
        return int(q[:4]) * 4 + int(q[-1]) - 1
    return q.str[:4].astype(int) * 4 + q.str[-1].astype(int) - 1


# ---------------------------------------------------------------- data
def cats():
    a = pd.read_csv(P / "balanced-gig-category.csv.gz")
    b = pd.read_csv(P / "ai-title-flags.csv", usecols=["gig_id", "category"])
    return pd.concat([a, b]).drop_duplicates("gig_id")


def load_pages(tag, cat, ex):
    p = pd.read_csv(P / f"page-fields-{tag}.csv.gz", dtype={"seller_country": str})
    p["capture_date"] = p.capture_date.astype(str)
    p["quarter"] = p.capture_date.str[:4] + "Q" + ((p.capture_date.str[4:6].astype(int) - 1) // 3 + 1).astype(str)
    p = p[(p.quarter >= PAGE_WIN[0]) & (p.quarter <= PAGE_WIN[1])]
    p = p.sort_values("capture_date").groupby(["gig_id", "quarter"]).tail(1)
    p = p.merge(cat, on="gig_id")
    p["exp_h"] = p.category.map(ex.exposure_primary)
    p["exp_r"] = p.category.map(ex.exposure_robust)
    p["qn"] = qn(p.quarter)
    cpi = pd.read_csv(P / "cpi-quarterly.csv").set_index("quarter").cpi_sa
    defl = p.quarter.map(cpi / cpi.get("2020Q1"))
    p["lp1"] = np.log(p.p1.where(p.p1 > 0) / defl)
    p["lw1"] = np.log(p.w1.where(p.w1 > 0))
    p["lppw"] = p.lp1 - p.lw1
    p["ladder"] = np.log(p.p3.where(p.p3 > 0) / p.p1.where(p.p1 > 0))
    p["ldur1"] = np.log(p.dur1.where(p.dur1 > 0))
    p["rev1c"] = p.rev1.clip(upper=10)
    p["hi_inc"] = np.where(p.seller_country.notna() & (p.seller_country != ""),
                           p.seller_country.isin(HIGH_INCOME).astype(float), np.nan)
    return p


def load_orders(tag, cat, ex):
    o = pd.read_csv(P / f"order-fields-{tag}.csv.gz")
    o = o.rename(columns={"order_quarter": "quarter"})
    o = o[(o.quarter >= ORD_WIN[0]) & (o.quarter <= ORD_WIN[1])]
    o = o.merge(cat, on="gig_id")
    o["exp_h"] = o.category.map(ex.exposure_primary)
    o["exp_r"] = o.category.map(ex.exposure_robust)
    o["low_rate"] = np.where(o.rating.notna(), (o.rating < 5).astype(float), np.nan)
    return o


# ---------------------------------------------------------------- report
def fmt_did(name, r):
    return (f"| {name} | {r['b']:+.4f} | {r['se']:.4f} | {r['t']:+.2f} | "
            f"{r['p_cat']:.3f} | {r['n']:,} | {r['gigs']:,} | {r['mean']:.3f} |")


DID_HEAD = ["| Outcome · exposure | Coef | SE (gig) | t | wild p (category) | n | gigs | mean |",
            "|---|---:|---:|---:|---:|---:|---:|---:|"]


def by_cat_period(d, cols, ex):
    d = d.assign(period=np.where(d.quarter >= POST, "post", "pre"))
    t = d.groupby(["category", "period"])[cols].mean().unstack("period")
    t.columns = [f"{c} {p}" for c, p in t.columns]
    t.insert(0, "exposure", t.index.map(ex.exposure_primary))
    return t.sort_values("exposure", ascending=False)


def md_table(df, digits=3):
    cols = ["category"] + list(df.columns)
    L = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for idx, r in df.iterrows():
        L.append("| " + " | ".join([str(idx)] + [f"{v:.{digits}f}" if isinstance(v, float) else str(v)
                                                 for v in r]) + " |")
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="all")
    args = ap.parse_args()
    ex = pd.read_csv(EXPO).set_index("category")
    cat = cats()
    p = load_pages(args.tag, cat, ex)
    o = load_orders(args.tag, cat, ex)

    L = ["# Step 90 — AI-exposure tests on margins the price index cannot see (EXPLORATORY)", "",
         f"Pages: {len(p):,} gig-quarters, {p.gig_id.nunique():,} gigs, {PAGE_WIN[0]}–{PAGE_WIN[1]}. "
         f"Orders: {len(o):,}, {ORD_WIN[0]}–{ORD_WIN[1]}. Post = 1[quarter ≥ {POST}]. "
         "Exposure 0–1 (human = step-45 primary, GPT-4 = robustness), so a DiD coefficient is "
         "the post-ChatGPT change for a fully exposed vs an unexposed category. "
         "**Wild p (category)** is the wild-cluster bootstrap on 7 category clusters and is "
         "the inference to read; gig-clustered t is optimistic.", ""]

    # ---- T1 price per word
    L += ["## T1 · Price per word (word-priced gigs)", ""]
    w = p[p.lppw.notna()]
    L.append(f"Gig-quarters with a basic-package word count: {len(w):,} "
             f"({w.gig_id.nunique():,} gigs); by category: "
             + ", ".join(f"{k} {v:,}" for k, v in w.category.value_counts().items()) + ".")
    L += ["", "Within-gig interrupted time series (gig FE, linear trend, Post, Post × trend), "
          "real 2020Q1 dollars, per quarter in log points:", "",
          "| Category | Outcome | trend | Post (level) | t | Post × trend | t | n | gigs |",
          "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for c in ["translation", "writing"]:
        for y, lab in [("lppw", "log price/word"), ("lp1", "log price"), ("lw1", "log words")]:
            r, n, g = its(w[w.category == c], y)
            L.append(f"| {c} | {lab} | {r['trend'][0]:+.4f} | {r['post'][0]:+.4f} | "
                     f"{r['post'][0]/r['post'][1]:+.2f} | {r['post_trend'][0]:+.4f} | "
                     f"{r['post_trend'][0]/r['post_trend'][1]:+.2f} | {n:,} | {g:,} |")
    # DiD: word-priced high-exposure gigs (price per word) vs low-exposure gigs (price)
    s = pd.concat([w[w.category.isin(["translation", "writing"])].assign(y=lambda d: d.lppw, treat=1.0),
                   p[p.category.isin(LOW) & p.lp1.notna()].assign(y=lambda d: d.lp1, treat=0.0)])
    r = did(s, "y", "treat")
    L += ["", "DiD — log real price per word (translation + writing word-priced gigs) vs log real "
          f"basic price ({' + '.join(LOW)}), gig + quarter FE:", ""] + DID_HEAD + [fmt_did("treat × post", r)]

    # ---- T2 repeat buyers
    L += ["", "## T2 · Repeat-buyer share (orders)", ""]
    L += md_table(by_cat_period(o, ["repeat_buyer"], ex)) + [""] + DID_HEAD
    for e_, lab in [("exp_h", "human"), ("exp_r", "GPT-4")]:
        L.append(fmt_did(f"repeat_buyer · {lab}", did(o, "repeat_buyer", e_)))
    es = event(o, "repeat_buyer", "exp_h")
    L += ["", "Event study (human), ref 2022Q3: " + ", ".join(
        f"{q} {b:+.3f} (t {t:+.1f})" for q, b, t in es.itertuples(index=False))]

    # ---- T3 review text
    L += ["", "## T3 · Reviews naming AI tools or machine translation", ""]
    oc = o[o.has_comment == 1].copy()
    oc["yr"] = oc.quarter.str[:4]
    t3 = oc.groupby(["category", "yr"]).cm_ai.mean().unstack() * 100
    L += ["Share of reviews (%) naming a generative-AI tool, by order year:", ""]
    L += md_table(t3, 2)
    L += ["", "Machine-translation mentions (%), translation gigs only, by year: " + ", ".join(
        f"{y} {v*100:.2f}" for y, v in oc[oc.category == "translation"].groupby("yr").cm_mt.mean().items())]
    ai_o = oc[oc.cm_ai == 1]
    L += ["", f"Reviews naming AI: {len(ai_o):,}. Share below 5 stars: "
          f"{ai_o.low_rate.mean():.3f} vs {oc[oc.cm_ai == 0].low_rate.mean():.3f} for all other reviews "
          f"in the same window."]

    # ---- T4 seller country
    L += ["", "## T4 · High-income-country sellers (share of gig-quarters)", ""]
    L += md_table(by_cat_period(p, ["hi_inc"], ex)) + [""] + DID_HEAD
    for e_, lab in [("exp_h", "human"), ("exp_r", "GPT-4")]:
        L.append(fmt_did(f"hi_inc · {lab} (quarter + category FE)", did(p, "hi_inc", e_, gig_fe=False)))

    # ---- T5 labels
    L += ["", "## T5 · Gig descriptions: generative-AI mentions and human/no-AI claims (%)", ""]
    p["yr"] = p.quarter.str[:4]
    for col, lab in [("desc_ai", "mentions generative AI"), ("desc_anti_ai", "claims human / no-AI work")]:
        L += [f"**{lab}**", ""] + md_table(p.groupby(["category", "yr"])[col].mean().unstack() * 100, 2) + [""]
    L += DID_HEAD
    for col in ["desc_ai", "desc_anti_ai"]:
        L.append(fmt_did(f"{col} · human (gig FE)", did(p, col, "exp_h")))

    # ---- T6 ladder, T7 delivery
    L += ["", "## T6 · Tier ladder, T7 · listed delivery time and revisions (within gig)", ""]
    L += md_table(by_cat_period(p, ["ladder", "ldur1", "rev1c"], ex)) + [""] + DID_HEAD
    for y in ["ladder", "ldur1", "rev1c"]:
        for e_, lab in [("exp_h", "human"), ("exp_r", "GPT-4")]:
            L.append(fmt_did(f"{y} · {lab}", did(p, y, e_)))
    for y in ["ladder", "ldur1"]:
        es = event(p, y, "exp_h")
        pre = es[es.quarter < POST]
        L += ["", f"{y} event study (human), ref 2022Q3 — pre-period |t| > 1.96 in "
              f"{(pre.t.abs() > 1.96).sum()} of {len(pre)} quarters; post coefficients: " +
              ", ".join(f"{q} {b:+.3f}" for q, b, t in es[es.quarter >= POST].itertuples(index=False))]

    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
