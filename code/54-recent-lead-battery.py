#!/usr/bin/env python3
"""
Step 54: the promotion battery for the step-53 lead.

WHY THIS EXISTS. Step 53 found the first AI-consistent pattern in the project:
writing (2nd most exposed of 7) loses review accrual faster than video (6th of 7),
and the gap WIDENS -- -0.8%/quarter over 2019Q3-2024Q4, -4.2%/quarter over
2023Q1-2024Q4, -6.8%/quarter over the recent 2024Q3-2026Q1 frame that Fiverr's
own Q2-2026 release attributes to AI.

Six previous designs produced significant, correctly-signed estimates at exactly
this stage and ALL SIX died on the same battery. Step 53 was recorded as a LEAD,
not a finding, with a promotion rule: it is reported only if it clears the battery
on BOTH frames. This step runs the battery.

THE FIVE GATES, and what each is for.

  A  CATEGORY-LEVEL RANDOMISATION INFERENCE.
     The treatment in step 53 varies across exactly TWO categories, but the SEs
     are clustered on ~525 gigs. That is the Moulton problem in its purest form:
     the effective number of treated clusters is ONE. Every t-statistic step 53
     printed is therefore inflated by an unknown factor. The honest test is to
     compute the same contrast for all 21 category pairs and ask where
     writing-video ranks. p-floor = 1/21 = 0.048.

  B  SEVEN-CATEGORY EXPOSURE GRADIENT.
     A two-category contrast cannot distinguish "exposed work fell faster" from
     "writing fell faster". If AI is the mechanism, the differential trend should
     line up with exposure across ALL seven categories. Spearman rho against the
     pre-registered human_rating_beta; |rho| > 0.786 needed for p < 0.05 at n=7.

  C  PLACEBO WINDOW (pre-AI).
     Same specification on 2019Q3-2021Q4, before any generative-AI tool was in
     commercial use in these categories. Steps 46/50 both died here in effect:
     the diagnosis in the answer document is that the exposure-correlated
     differential trend PREDATES ChatGPT. If it is already there in 2019-2021,
     the recent estimate is a continuation, not an AI effect.

  D  INFERENCE ROBUSTNESS.
     Wild cluster bootstrap (Rademacher, null imposed, 999 reps) over gigs, and a
     collapsed two-step: category-quarter means of gig-demeaned accrual, then the
     writing-video difference series on trend. The collapsed test is immune to
     within-category dependence, which is what inflates the gig-clustered t.

  E  SELECTION AND COMPOSITION AUDIT.
     Gig FE do not protect against composition (the quota manifest already
     manufactured a spurious jump once, see the answer document 3.0). Tests
     differential attrition between writing and video, and re-runs on gigs
     observed in both halves of the window.

PROMOTION RULE, restated from progress.md and NOT negotiable after the fact:
the lead is promoted to a finding only if it clears A-E on both frames. Anything
less is reported as what it is.

Run:  python3 code/54-recent-lead-battery.py
"""

import csv
import importlib.util
import math
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "code"))
PILOT = BASE / "data" / "pilot"

RNG = np.random.default_rng(20260819)


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, BASE / "code" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m24 = _load("m24", "24-margin-diagnostics.py")
s53 = _load("s53", "53-recent-exposure.py")
ols_cluster = m24.ols_cluster
build = s53.build
absorb2 = s53.absorb2
qi = s53.qi

EXPOSED, UNEXPOSED = "writing", "video"

# pre-registered exposure, data/exposure-ranking.csv, human_rating_beta
BETA = {"translation": 0.8400, "writing": 0.6858, "marketing": 0.6243,
        "coding": 0.5884, "design": 0.5084, "video": 0.4019, "audio": 0.2478}
CATS = sorted(BETA, key=lambda c: -BETA[c])


# ---------------------------------------------------------------- estimator
def diff_trend(rows, hi_cat, lo_cat, min_gigs=1):
    """exposed x trend, gig FE + quarter FE, gig-clustered SEs.

    Returns dict or None if the contrast is not estimable.
    """
    sub = [r for r in rows if r["cat"] in (hi_cat, lo_cat)]
    if len(sub) < 20:
        return None
    ghi = {r["gig"] for r in sub if r["cat"] == hi_cat}
    glo = {r["gig"] for r in sub if r["cat"] == lo_cat}
    if len(ghi) < min_gigs or len(glo) < min_gigs:
        return None
    if len({r["q1"] for r in sub}) < 3:
        return None
    t0 = min(r["t"] for r in sub)
    hi = np.array([1.0 if r["cat"] == hi_cat else 0.0 for r in sub])
    tt = np.array([r["t"] - t0 for r in sub], dtype=float)
    y = np.array([r["y"] for r in sub])
    gigs = [r["gig"] for r in sub]
    X = np.column_stack([hi * tt])
    Xd, yd, nab = absorb2(X, y, gigs, [r["q1"] for r in sub])
    if np.std(Xd) < 1e-9:
        return None
    b, se = ols_cluster(Xd, yd, gigs, n_absorbed=nab)
    return {"b": float(b[0]), "se": float(se[0]),
            "t": float(b[0] / se[0]) if se[0] > 0 else np.nan,
            "n": len(sub), "gigs_hi": len(ghi), "gigs_lo": len(glo),
            "Xd": Xd, "yd": yd, "gigs": gigs}


def gradient(rows, base="audio"):
    """Per-category differential trend vs `base`, gig FE + quarter FE."""
    sub = [r for r in rows if r["cat"] in BETA]
    others = [c for c in CATS if c != base]
    present = [c for c in others
               if len({r["gig"] for r in sub if r["cat"] == c}) >= 20]
    if len({r["gig"] for r in sub if r["cat"] == base}) < 20 or not present:
        return None
    t0 = min(r["t"] for r in sub)
    tt = np.array([r["t"] - t0 for r in sub], dtype=float)
    cols = [np.array([1.0 if r["cat"] == c else 0.0 for r in sub]) * tt
            for c in present]
    y = np.array([r["y"] for r in sub])
    gigs = [r["gig"] for r in sub]
    Xd, yd, nab = absorb2(np.column_stack(cols), y, gigs,
                          [r["q1"] for r in sub])
    b, se = ols_cluster(Xd, yd, gigs, n_absorbed=nab)
    out = {base: (0.0, 0.0)}
    for c, bb, ss in zip(present, b, se):
        out[c] = (float(bb), float(ss))
    return out


def spearman(x, y):
    def rank(v):
        order = np.argsort(np.argsort(np.asarray(v, dtype=float)))
        return order.astype(float)
    rx, ry = rank(x), rank(y)
    rx -= rx.mean()
    ry -= ry.mean()
    d = np.sqrt((rx @ rx) * (ry @ ry))
    return float(rx @ ry / d) if d > 0 else np.nan


def wild_bootstrap(fit, reps=999):
    """Rademacher wild cluster bootstrap over gigs, null imposed."""
    Xd, yd, gigs = fit["Xd"], fit["yd"], fit["gigs"]
    idx = defaultdict(list)
    for i, g in enumerate(gigs):
        idx[g].append(i)
    groups = [np.array(v) for v in idx.values()]
    # restricted residuals: under H0 b=0, the FE-absorbed model has fit 0
    u = yd.copy()
    XtX_inv = float(1.0 / (Xd[:, 0] @ Xd[:, 0]))
    ts = []
    for _ in range(reps):
        w = RNG.choice([-1.0, 1.0], size=len(groups))
        ystar = np.empty_like(u)
        for wi, gi in zip(w, groups):
            ystar[gi] = u[gi] * wi
        bstar = XtX_inv * float(Xd[:, 0] @ ystar)
        rstar = ystar - Xd[:, 0] * bstar
        meat = 0.0
        for gi in groups:
            meat += float(Xd[gi, 0] @ rstar[gi]) ** 2
        v = XtX_inv * meat * XtX_inv
        ts.append(bstar / np.sqrt(v) if v > 0 else 0.0)
    ts = np.abs(np.array(ts))
    return float((np.sum(ts >= abs(fit["t"])) + 1) / (reps + 1))


def collapsed(rows, hi_cat, lo_cat):
    """Gig-demean y, take category-quarter means, regress the difference on t."""
    sub = [r for r in rows if r["cat"] in (hi_cat, lo_cat)]
    if not sub:
        return None
    byg = defaultdict(list)
    for r in sub:
        byg[r["gig"]].append(r)
    dem = {}
    for g, rs in byg.items():
        m = np.mean([r["y"] for r in rs])
        for r in rs:
            dem[id(r)] = r["y"] - m
    cell = defaultdict(list)
    for r in sub:
        cell[(r["cat"], r["q1"])].append(dem[id(r)])
    qs = sorted({q for (_, q) in cell}, key=qi)
    xs, ds = [], []
    for q in qs:
        a, b = cell.get((hi_cat, q)), cell.get((lo_cat, q))
        if a and b and len(a) >= 3 and len(b) >= 3:
            xs.append(qi(q))
            ds.append(np.mean(a) - np.mean(b))
    if len(xs) < 4:
        return None
    x = np.array(xs, dtype=float)
    x -= x.mean()
    d = np.array(ds)
    b = float(x @ (d - d.mean()) / (x @ x))
    resid = (d - d.mean()) - b * x
    s2 = float(resid @ resid) / (len(x) - 2)
    se = np.sqrt(s2 / float(x @ x))
    return {"b": b, "se": float(se), "t": b / se, "T": len(x)}


# ------------------------------------------------------------------ report
def hdr(t):
    print("\n" + "=" * 80)
    print(t)
    print("=" * 80)


def main():
    print("=" * 80)
    print("STEP 54 — PROMOTION BATTERY FOR THE STEP-53 LEAD")
    print("=" * 80)

    recent = build(PILOT / "recent-prices.csv", PILOT / "recent-manifest.tsv", None)
    bal = build(PILOT / "balanced-prices.csv",
                PILOT / "balanced-manifest-1200.tsv", None)

    FRAMES = [
        ("RECENT 2024Q3-2026Q1", recent),
        ("BALANCED 2023Q1-2024Q4", [r for r in bal if qi("2023Q1") <= r["t"] <= qi("2024Q4")]),
        ("BALANCED full 2019Q3-2024Q4", [r for r in bal if r["t"] <= qi("2024Q4")]),
    ]
    PLACEBO = ("BALANCED PRE-AI 2019Q3-2021Q4",
               [r for r in bal if r["t"] <= qi("2021Q4")])

    # ------------------------------------------------------------- GATE A
    hdr("GATE A — CATEGORY-LEVEL RANDOMISATION INFERENCE (21 pairs)")
    print("""
  The step-53 treatment varies across TWO categories; its SEs are clustered on
  hundreds of gigs. Effective treated clusters = 1. Every pair below is estimated
  identically, with the MORE-EXPOSED member coded as treated. Under the null that
  exposure is irrelevant, writing-video is exchangeable with the other 20.
  One-sided p-floor = 1/21 = 0.048.""")
    gateA = {}
    for name, rows in FRAMES + [PLACEBO]:
        res = []
        for a, b in combinations(CATS, 2):
            hi, lo = (a, b) if BETA[a] > BETA[b] else (b, a)
            f = diff_trend(rows, hi, lo, min_gigs=20)
            if f:
                res.append((hi, lo, f["b"], f["t"], f["gigs_hi"], f["gigs_lo"],
                            BETA[hi] - BETA[lo]))
        if not res:
            print(f"\n  {name}: no estimable pairs")
            continue
        res.sort(key=lambda r: r[2])
        print(f"\n  {name}   ({len(res)} of 21 pairs estimable, >=20 gigs each side)")
        print("    rank  exposed / unexposed        d.beta      b       t     gigs")
        target = None
        for i, (hi, lo, bb, tt, nh, nl, dbeta) in enumerate(res, 1):
            mark = ""
            if (hi, lo) == (EXPOSED, UNEXPOSED):
                mark = "   <== the step-53 lead"
                target = i
            print(f"    {i:>4}  {hi:<12}/{lo:<12} {dbeta:+.3f} {bb:+8.4f} {tt:+7.2f}"
                  f" {nh:>5}/{nl:<5}{mark}")
        bs = np.array([r[2] for r in res])
        dbs = np.array([r[6] for r in res])
        print(f"\n    pairs with a NEGATIVE differential (exposed falls faster): "
              f"{int(np.sum(bs < 0))} of {len(bs)}")
        print(f"    Spearman(coefficient, exposure gap): {spearman(bs, dbs):+.3f}"
              "    (AI predicts NEGATIVE: bigger gap -> more negative)")
        if target:
            p = target / len(res)
            print(f"    writing-video ranks {target} of {len(res)}  ->  "
                  f"randomisation p = {p:.3f}"
                  f"   {'PASS' if p <= 0.05 else 'FAIL'}")
            gateA[name] = p
        else:
            print("    writing-video not estimable in this frame")

    # ------------------------------------------------------------- GATE B
    hdr("GATE B — SEVEN-CATEGORY EXPOSURE GRADIENT")
    print("""
  Does the differential trend line up with exposure across all seven categories,
  or is this a fact about writing? Trends are relative to audio (least exposed).
  n = 7, so |rho| > 0.786 is needed for p < 0.05. AI predicts NEGATIVE rho.""")
    for name, rows in FRAMES + [PLACEBO]:
        g = gradient(rows)
        if not g:
            print(f"\n  {name}: not estimable")
            continue
        print(f"\n  {name}")
        print("    category      beta    trend vs audio      t")
        cs = [c for c in CATS if c in g]
        for c in cs:
            bb, ss = g[c]
            tt = bb / ss if ss > 0 else np.nan
            base = "  (base)" if c == "audio" else ""
            print(f"    {c:<12} {BETA[c]:.3f}   {bb:+8.4f}   "
                  f"{'' if c=='audio' else f'{tt:+7.2f}'}{base}")
        rho = spearman([BETA[c] for c in cs], [g[c][0] for c in cs])
        print(f"    Spearman(exposure, trend) = {rho:+.3f} over {len(cs)} categories"
              f"   {'PASS' if rho <= -0.786 else 'FAIL'}")

    # ------------------------------------------------------------- GATE C
    hdr("GATE C — PLACEBO WINDOW: was the differential already there before AI?")
    print("""
  2019Q3-2021Q4 predates commercial generative AI in these categories. A
  significant negative writing-video differential HERE means the recent estimate
  is the continuation of a pre-existing trend.""")
    for name, rows in [PLACEBO, ("BALANCED 2019Q3-2020Q4 (tighter)",
                                 [r for r in bal if r["t"] <= qi("2020Q4")])]:
        f = diff_trend(rows, EXPOSED, UNEXPOSED, min_gigs=20)
        if not f:
            print(f"\n  {name}: not estimable")
            continue
        print(f"\n  {name}")
        print(f"    n {f['n']:,}  gigs {f['gigs_hi']:,} writing / {f['gigs_lo']:,} video")
        print(f"    writing x trend  {f['b']:+.4f}  (se {f['se']:.4f}, t {f['t']:+.2f})"
              f"  = {100*(np.exp(f['b'])-1):+.1f}%/quarter")
        verdict = "FAIL (differential predates AI)" if f["t"] < -1.96 else "PASS"
        print(f"    {verdict}")

    # ------------------------------------------------------------- GATE D
    hdr("GATE D — INFERENCE ROBUSTNESS")
    print("""
  Column 1 is what step 53 printed. Column 2 imposes the null and resamples gig
  clusters. Column 3 collapses to category-quarter means, which removes the
  within-category dependence that inflates the gig-clustered t entirely.""")
    for name, rows in FRAMES:
        f = diff_trend(rows, EXPOSED, UNEXPOSED, min_gigs=20)
        if not f:
            print(f"\n  {name}: not estimable")
            continue
        pw = wild_bootstrap(f)
        col = collapsed(rows, EXPOSED, UNEXPOSED)
        print(f"\n  {name}")
        print(f"    gig-clustered      b {f['b']:+.4f}  t {f['t']:+.2f}"
              f"  p {2*(1-_ncdf(abs(f['t']))):.3f}")
        print(f"    wild bootstrap     p {pw:.3f}   (999 reps, Rademacher, H0 imposed)")
        if col:
            print(f"    collapsed 2-step   b {col['b']:+.4f}  t {col['t']:+.2f}"
                  f"  on T = {col['T']} quarter cells")
        else:
            print("    collapsed 2-step   not estimable (too few quarter cells)")

    # ------------------------------------------------------------- GATE E
    hdr("GATE E — SELECTION AND COMPOSITION AUDIT")
    for name, rows in FRAMES:
        sub = [r for r in rows if r["cat"] in (EXPOSED, UNEXPOSED)]
        if not sub:
            continue
        qs = sorted({r["q1"] for r in sub}, key=qi)
        mid = qs[len(qs) // 2]
        print(f"\n  {name}   quarters {qs[0]}..{qs[-1]}, split at {mid}")
        print("    category   gigs  early-only  both halves  late-only   "
              "mean accrual, gigs in BOTH halves: early -> late")
        keep = {}
        for c in (EXPOSED, UNEXPOSED):
            g_e = {r["gig"] for r in sub if r["cat"] == c and qi(r["q1"]) < qi(mid)}
            g_l = {r["gig"] for r in sub if r["cat"] == c and qi(r["q1"]) >= qi(mid)}
            both = g_e & g_l
            keep[c] = both
            e = [r["rate"] for r in sub
                 if r["cat"] == c and r["gig"] in both and qi(r["q1"]) < qi(mid)]
            l = [r["rate"] for r in sub
                 if r["cat"] == c and r["gig"] in both and qi(r["q1"]) >= qi(mid)]
            print(f"    {c:<10} {len(g_e | g_l):>5} {len(g_e - g_l):>11}"
                  f" {len(both):>12} {len(g_l - g_e):>10}      "
                  f"{np.mean(e) if e else float('nan'):8.2f} -> "
                  f"{np.mean(l) if l else float('nan'):.2f}")
        allkeep = keep[EXPOSED] | keep[UNEXPOSED]
        f2 = diff_trend([r for r in sub if r["gig"] in allkeep],
                        EXPOSED, UNEXPOSED, min_gigs=10)
        if f2:
            print(f"    re-estimated on gigs present in BOTH halves: "
                  f"b {f2['b']:+.4f} (t {f2['t']:+.2f}), "
                  f"{f2['gigs_hi']}+{f2['gigs_lo']} gigs")
        else:
            print("    re-estimated on gigs present in BOTH halves: not estimable")

    hdr("VERDICT")
    print("""
  Read gates A-E above. The promotion rule fixed in progress.md before this ran:
  the step-53 lead is reported as a FINDING only if it clears every gate on both
  frames. Gate A is the decisive one -- it is the only test in this file whose
  inference matches the level at which the treatment actually varies.""")


def _ncdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


if __name__ == "__main__":
    main()
