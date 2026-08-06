#!/usr/bin/env python3
"""
Step 25: Hedonic price regression — price on seller rating, prior-gig count, and
task type.

    ln(price) = b0 + b1*rating + b2*ln(1+prior_gigs) + sum_c g_c*taskType_c + e

WHAT THIS IS. A descriptive hedonic: how much of the cross-gig spread in posted
price is associated with a seller's rating, their accumulated volume, and what
kind of work it is. It is NOT causal and must not be read as one — see the
confound section below, which the script quantifies rather than asserts.

TWO DATA PROBLEMS, handled explicitly:

  1. RATING IS NEARLY DEGENERATE. At gig level ~90% sit at >= 4.8 and ~41% are
     exactly 5.0 (IQR 4.80 to 5.00, sd 0.26). Fiverr ratings are compressed at
     the top, so b1 is estimated off a thin slice of the distribution and a
     "per rating point" reading is an extrapolation far outside the data. The
     script prints the spread and reports the slope per 0.1 point instead.

  2. RATING HAS A SCALE BUG. 217 historical rows carry ratings in (5, 10] --
     pre-2019 Fiverr displayed a 10-point scale, and the extractor wrote it into
     the same column as the 5-point one. Untreated, a 10.0 reads as twice as
     good as a 5.0. Handled by RATING_FIX: "rescale" (halve them, the default),
     "drop", or "raw" (reproduce the bug, for comparison). All three are run.

"PRIOR GIGS" IS AMBIGUOUS, so both readings are estimated:

  seller_gigs  distinct gigs the seller offers in the crawl. Weak: median 1 in
               the recent crawl (8.9% of sellers offer more than one), and the
               historical crawl is a 500-seller sample chosen for long histories,
               so its distribution is a sampling artefact.
  reviews      cumulative review count ~ completed orders. This is the reading
               that actually varies, and it is the "prior work done" notion the
               question is really about.

CROSS-SECTION vs WITHIN-GIG. Specs 1-2 compare different sellers; spec 3
re-estimates the volume slope WITHIN a gig over time, holding the seller fixed.
They disagree, and not in the expected direction: the cross-sectional slope on
ln(1+reviews) is +0.022 and indistinguishable from zero, while the within-gig
slope is +0.133 (t=7.9), consistent with step 22 Test B's +0.103. So the
cross-section does not inflate a real effect -- it CANCELS one. A gig that
accumulates orders raises its own price ~+10% per doubling, but across sellers
high volume is also what cheap high-throughput sellers have, and the two forces
offset. This is a Simpson-style reversal. Do NOT read the near-zero
cross-sectional coefficient as "experience is unpriced": it is priced, and the
cross-section cannot see it.

Run:  python3 code/25-hedonic-regression.py
"""

import csv
import importlib.util
import math
import sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "code"))
from gigfilter import is_gig


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, BASE / "code" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tpd = _load("tpd", "19-tpd-index.py")
CATS = tpd.CATS
PILOT = BASE / "data" / "pilot"
PRICE_MAX = tpd.PRICE_MAX
REF_CAT = "design"          # omitted dummy — the largest category
RATING_MAX = 5.0


# --------------------------------------------------------------------------
# OLS with cluster-robust (CR1) standard errors
# --------------------------------------------------------------------------
def ols_cluster(X, y, clusters, names, absorbed=0):
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    cl = defaultdict(list)
    for i, c in enumerate(clusters):
        cl[c].append(i)
    G, n, k = len(cl), len(y), X.shape[1] + absorbed
    meat = np.zeros((X.shape[1], X.shape[1]))
    for _, ii in cl.items():
        s = X[ii].T @ resid[ii]
        meat += np.outer(s, s)
    adj = (G / max(G - 1, 1)) * ((n - 1) / max(n - k, 1))
    V = adj * (XtX_inv @ meat @ XtX_inv)
    se = np.sqrt(np.maximum(np.diag(V), 0.0))
    tss = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (resid @ resid) / tss if tss > 0 else float("nan")
    return {"beta": beta, "se": se, "names": names, "r2": r2,
            "n": n, "G": G, "resid": resid}


def report(res, title, note="", unit="sellers"):
    print(f"\n  {title}")
    if note:
        print(f"    {note}")
    print(f"    n = {res['n']}   clusters ({unit}) = {res['G']}   R^2 = {res['r2']:.4f}")
    print(f"    {'term':<24} {'coef':>10} {'se':>9} {'t':>7}   {'effect on price':>18}")
    for nm, b, s in zip(res["names"], res["beta"], res["se"]):
        t = b / s if s > 0 else float("nan")
        # a coefficient on ln(price) is a semi-elasticity
        eff = (math.exp(b) - 1) * 100
        star = "*" if abs(t) > 1.96 else " "
        print(f"    {nm:<24} {b:>10.4f} {s:>9.4f} {t:>7.2f} {star}  {eff:>+16.1f}%")


# --------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------
def clean_rating(v, mode):
    """Fiverr showed a 10-point scale before ~2019; the extractor wrote it into the
    same column as the 5-point one. Return None to drop the observation."""
    if v is None:
        return None
    if v <= 0:
        return None
    if v <= RATING_MAX:
        return v
    if mode == "rescale":
        return v / 2.0
    if mode == "drop":
        return None
    return v                       # "raw" — reproduce the bug on purpose


def build(rating_fix="rescale"):
    """One row per gig (its LATEST capture), so frequently-archived gigs do not
    dominate. -> list of dicts + the gig-quarter panel for the within-gig spec."""
    item_map = {}
    with open(tpd.HIST_ITEMS) as f:
        for row in csv.DictReader(f):
            item_map[(row["seller"], row["slug"])] = (row["item_label"], row["description"])
    manifest_cat = {}
    with open(tpd.RECENT_MANIFEST) as f:
        for row in csv.DictReader(f, delimiter="\t"):
            gid = tuple(row["gig_id"].split("/", 1))
            if len(gid) == 2:
                manifest_cat[gid] = row["category"]

    obs = defaultdict(list)        # gig -> [(date, quarter, price, rating, reviews)]
    gig_cat = {}
    scale_hits = 0
    for src, hist in ((tpd.HIST_PRICES, True), (tpd.RECENT_PRICES, False)):
        with open(src) as f:
            for row in csv.DictReader(f):
                if not is_gig(row["seller"]):
                    continue
                key = (row["seller"], row["slug"])
                if hist:
                    item = item_map.get(key)
                    if not item:
                        continue
                    cat = tpd.classify_gig(item[1], item[0])
                elif key in manifest_cat:
                    cat = manifest_cat[key]
                else:
                    continue
                if cat not in CATS:
                    continue
                try:
                    price = float(row.get("price_basic") or 0)
                except ValueError:
                    continue
                if price <= 0 or price > PRICE_MAX:
                    continue
                q = tpd.to_quarter(row["year"], row["month"])
                if not q:
                    continue

                def num(field):
                    v = row.get(field) or ""
                    try:
                        return float(v) if v != "" else None
                    except ValueError:
                        return None

                raw_rating = num("rating")
                if raw_rating is not None and raw_rating > RATING_MAX:
                    scale_hits += 1
                rating = clean_rating(raw_rating, rating_fix)
                obs[key].append((row["date"], q, price, rating, num("review_count")))
                gig_cat[key] = cat

    seller_gigs = Counter()
    for (seller, slug) in obs:
        seller_gigs[seller] += 1

    rows = []
    for key, recs in obs.items():
        recs.sort()
        date, q, price, rating, reviews = recs[-1]      # latest capture
        if rating is None or reviews is None:
            continue
        rows.append({
            "gig": key, "seller": key[0], "cat": gig_cat[key], "q": q,
            "lnp": math.log(price), "rating": rating,
            "ln_seller_gigs": math.log1p(seller_gigs[key[0]]),
            "ln_reviews": math.log1p(reviews),
        })
    return rows, obs, gig_cat, scale_hits


def design_matrix(rows, volume_key, with_quarter_fe=False):
    cats = [c for c in CATS if c != REF_CAT]
    names = ["rating", volume_key.replace("ln_", "ln(1+") + ")"] + [f"cat:{c}" for c in cats]
    cols = [np.array([r["rating"] for r in rows]),
            np.array([r[volume_key] for r in rows])]
    for c in cats:
        cols.append(np.array([1.0 if r["cat"] == c else 0.0 for r in rows]))
    if with_quarter_fe:
        qs = sorted({r["q"] for r in rows}, key=tpd.q_to_int)[1:]     # omit the first
        for q in qs:
            cols.append(np.array([1.0 if r["q"] == q else 0.0 for r in rows]))
            names.append(f"q:{q}")
    cols.append(np.ones(len(rows)))
    names.append("const")
    return np.column_stack(cols), names


def main():
    rows, obs, gig_cat, scale_hits = build("rescale")
    print("=" * 78)
    print("STEP 25 — HEDONIC REGRESSION: ln(price) ~ rating + prior gigs + task type")
    print("=" * 78)
    print(f"\ngigs with price, rating and review count at their latest capture: {len(rows)}")
    print(f"ratings found on the pre-2019 10-point scale: {scale_hits} "
          f"(halved; see RATING_FIX)")

    rat = np.array([r["rating"] for r in rows])
    print(f"\nRATING VARIANCE — the binding constraint on b1:")
    print(f"  mean {rat.mean():.3f}   sd {rat.std():.3f}   "
          f"share >= 4.8: {(rat >= 4.8).mean():.1%}   share == 5.0: {(rat == 5.0).mean():.1%}")
    print(f"  interquartile range: {np.percentile(rat, 25):.2f} to {np.percentile(rat, 75):.2f}")
    print("  => a '1-point' rating coefficient is an extrapolation far outside the data;")
    print("     read b1 per 0.1 rating point instead (printed below each spec).")

    sg = np.array([r["ln_seller_gigs"] for r in rows])
    rv = np.array([r["ln_reviews"] for r in rows])
    print(f"\nVOLUME MEASURES — correlation between the two readings: "
          f"{np.corrcoef(sg, rv)[0,1]:+.3f}")
    print(f"  ln(1+seller_gigs): mean {sg.mean():.2f} sd {sg.std():.2f}")
    print(f"  ln(1+reviews)    : mean {rv.mean():.2f} sd {rv.std():.2f}")

    print("\n" + "-" * 78)
    print("SPEC 1 — cross-section, as asked (one row per gig, seller-clustered SEs)")
    print("-" * 78)
    for vol in ("ln_reviews", "ln_seller_gigs"):
        X, names = design_matrix(rows, vol)
        res = ols_cluster(X, np.array([r["lnp"] for r in rows]),
                          [r["seller"] for r in rows], names)
        report(res, f"volume = {vol}")
        b1 = res["beta"][0]
        print(f"    rating per +0.1 point: {(math.exp(0.1*b1)-1)*100:+.2f}% on price")
        b2 = res["beta"][1]
        print(f"    doubling {vol.replace('ln_','')}: "
              f"{(math.exp(b2*math.log(2))-1)*100:+.1f}% on price")

    print("\n" + "-" * 78)
    print("SPEC 2 — same, plus quarter fixed effects (absorbs inflation + platform")
    print("         -wide repricing, so the slopes are within-quarter comparisons)")
    print("-" * 78)
    X, names = design_matrix(rows, "ln_reviews", with_quarter_fe=True)
    res2 = ols_cluster(X, np.array([r["lnp"] for r in rows]),
                       [r["seller"] for r in rows], names)
    keep = [i for i, n in enumerate(names) if not n.startswith("q:")]
    report({"beta": res2["beta"][keep], "se": res2["se"][keep],
            "names": [names[i] for i in keep], "r2": res2["r2"],
            "n": res2["n"], "G": res2["G"]},
           "volume = ln_reviews (quarter dummies estimated, not shown)")

    print("\n" + "-" * 78)
    print("SPEC 3 — the same volume slope estimated WITHIN a gig over time")
    print("         (first differences + quarter FE; the seller is held fixed)")
    print("-" * 78)
    diffs = []
    for key, recs in obs.items():
        byq = {}
        for date, q, price, rating, reviews in sorted(recs):
            if reviews is None:
                continue
            byq[q] = (price, reviews)          # last capture in the quarter
        order = sorted(byq, key=tpd.q_to_int)
        for a, b in zip(order, order[1:]):
            p0, r0 = byq[a]
            p1, r1 = byq[b]
            if p0 <= 0 or p1 <= 0 or r1 < r0:
                continue
            diffs.append({"gig": key, "seller": key[0], "q": b,
                          "dlnp": math.log(p1) - math.log(p0),
                          "dlnr": math.log1p(r1) - math.log1p(r0)})
    if diffs:
        qs = sorted({d["q"] for d in diffs}, key=tpd.q_to_int)[1:]
        cols = [np.array([d["dlnr"] for d in diffs])]
        nm = ["ln(1+reviews)"]
        for q in qs:
            cols.append(np.array([1.0 if d["q"] == q else 0.0 for d in diffs]))
            nm.append(f"q:{q}")
        cols.append(np.ones(len(diffs))); nm.append("const")
        Xd = np.column_stack(cols)
        r3 = ols_cluster(Xd, np.array([d["dlnp"] for d in diffs]),
                         [d["gig"] for d in diffs], nm)
        keep = [i for i, n in enumerate(nm) if not n.startswith("q:")]
        report({"beta": r3["beta"][keep], "se": r3["se"][keep],
                "names": [nm[i] for i in keep], "r2": r3["r2"],
                "n": r3["n"], "G": r3["G"]},
               "within-gig first differences, gig-clustered SEs", unit="gigs")

        X1, n1 = design_matrix(rows, "ln_reviews")
        cs = ols_cluster(X1, np.array([r["lnp"] for r in rows]),
                         [r["seller"] for r in rows], n1)["beta"][1]
        wi = r3["beta"][0]
        print(f"\n  CROSS-SECTION vs WITHIN-GIG — the two disagree, and that is the finding:")
        print(f"    cross-section slope on ln(1+reviews) : {cs:+.4f}")
        print(f"    within-gig slope on the same variable: {wi:+.4f}")
        print(f"    (step 22 Test B, a different sample cut, put the within-gig slope at +0.103)")
        if abs(wi) > abs(cs):
            print(f"    The within-gig slope is {abs(wi/cs):.1f}x the cross-sectional one, and the")
            print(f"    cross-sectional one is not distinguishable from zero. So the cross-section")
            print(f"    does NOT merely inflate a real effect -- it CANCELS it. A gig that")
            print(f"    accumulates orders raises its own price (+{(math.exp(wi*math.log(2))-1)*100:.0f}% per doubling),")
            print(f"    but across sellers, high-volume sellers are not the expensive ones:")
            print(f"    volume on this platform is also what cheap high-throughput sellers have.")
            print(f"    The two forces offset, which is a Simpson-style reversal, not noise.")
            print(f"    CONSEQUENCE: do not use the cross-sectional coefficient to argue that")
            print(f"    experience is unpriced. It is priced; the cross-section cannot see it.")
        else:
            print(f"    => roughly {100*(1 - wi/cs):.0f}% of the cross-sectional association is")
            print(f"       between-seller selection, not a return to accumulated volume.")

    print("\n" + "-" * 78)
    print("SENSITIVITY — does the rating scale bug matter?")
    print("-" * 78)
    for fix in ("rescale", "drop", "raw"):
        rws, _, _, _ = build(fix)
        X, names = design_matrix(rws, "ln_reviews")
        r = ols_cluster(X, np.array([x["lnp"] for x in rws]),
                        [x["seller"] for x in rws], names)
        print(f"  RATING_FIX={fix:<8} n={r['n']:<6} b(rating) = {r['beta'][0]:+.4f} "
              f"(se {r['se'][0]:.4f})   b(ln reviews) = {r['beta'][1]:+.4f}")
    print("  'raw' leaves the 10-point rows in and is the wrong answer; it is run only")
    print("  to show the size of the error the bug would have introduced.")

    print("\n" + "=" * 78)
    print("HOW TO READ THIS: specs 1-2 are descriptive associations across different")
    print("sellers, not causal effects. Task-type coefficients are price *levels*")
    print("relative to " + REF_CAT + " and say nothing about AI exposure. The rating")
    print(f"slope is estimated off a distribution where {(rat == 5.0).mean():.0%} of gigs "
          f"share one value.")
    print("=" * 78)


if __name__ == "__main__":
    main()
