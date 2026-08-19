#!/usr/bin/env python3
"""
Step 50: the gig-level continuous-exposure design, exactly as pre-registered.

Runs the specification LOCKED in `plans/active/exposure-continuous-prereg.md`
(registered 2026-08-18, before any outcome was estimated under this exposure
measure). Nothing below is chosen after seeing an outcome; every knob is quoted
from that file, and §1 of it discloses the mapping diagnostics that WERE seen.

WHY THIS EXISTS. Five designs have failed to identify an AI effect on this data
(steps 46, 48, 49). Four of them shared one defect -- seven units, so the in-space
placebo p-floor is 1/7 = 0.143 by construction. The fifth fixed the unit count but
used pre-period PRICE as the treatment proxy, and price rank turned out to be
contaminated by mean reversion.

This design fixes both. Exposure is continuous, gig-level, and external (Eloundou
et al. 2023 O*NET occupation ratings), and CATEGORY x QUARTER fixed effects absorb
the platform-wide and category-wide shocks that killed designs 1-4. The prior
recorded in the pre-registration is LOW: five failures on the same underlying data
is evidence about the data, not only about the designs. The lock exists so that a
sixth failure is interpretable rather than discardable.

SECTIONS, in the pre-registered order:
  E0  exposure construction + the §2 selection audit on zero-match gigs
  E1  primary specification, with the realised MDE beside the estimate
  G1  parallel trends -- JOINT F-TEST gate. FAIL => the DiD is dead (§6 fallback)
  G2  not-a-price-proxy gate (step 49's mean-reversion lesson)
  G3  placebo window 2019Q3-2021Q4, false break 2020Q3. Must be null
  G4  the step-29 battery: first differences, trend horse race, CPI-U, Newey-West
  G5  composition gate on the balanced panel (step 49's other lesson)
  F   §6 fallback -- descriptive dose-response by exposure decile, NOT identified

READ BEFORE QUOTING ANY NUMBER:
  * Exit is unmeasurable (n_404 = 0 across 509,339 captures). Nothing is exit.
  * review_count is a sales proxy, not sales.
  * The IPI reads listed basic-package prices, not realised order value.
  * The window stops at 2024Q4 and says nothing about the 2025-26 agentic period.

Run:  python3 code/50-continuous-exposure.py
"""

import csv
import importlib.util
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "code"))
from gigfilter import is_gig  # noqa: E402


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, BASE / "code" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m24 = _load("m24", "24-margin-diagnostics.py")
m46 = _load("m46", "46-balanced-demand.py")
absorb, ols_cluster, absorb2 = m24.absorb, m24.ols_cluster, m46.absorb2

PILOT = BASE / "data" / "pilot"
PRICES = PILOT / "balanced-prices.csv"
MANIFEST = PILOT / "balanced-manifest-1200.tsv"
CPI = PILOT / "cpi-quarterly.csv"
ELO = BASE / "data" / "eloundou-2023-occ-level.csv"

# ---- everything below is quoted from the pre-registration, not chosen here ----
PRIMARY, ROBUST = "human_rating_beta", "dv_rating_beta"
K_PRIMARY, K_GRID = 3, [1, 5, 10]
WIN_START, WIN_END = "2019Q3", "2024Q4"
BREAK_Q = "2022Q4"
PLB_START, PLB_END, PLB_BREAK = "2019Q3", "2021Q4", "2020Q3"
MIN_DESC = 10
BAL_WIN, BAL_FRAC = ("2020Q3", "2023Q4"), 0.8
GATES = {}


def qi(q):
    return int(q[:4]) * 4 + int(q[-1])


def hdr(t):
    print("\n" + "=" * 88)
    print(t)
    print("=" * 88)


def clean(t):
    if not t:
        return ""
    t = re.sub(r"^[^:]+:\s*", "", t, count=1)
    t = re.sub(r"\s+for\s+\$[\d,]+\s+on\s+(?:www\.)?fiverr\.com\s*$", "", t, flags=re.I)
    t = re.sub(r"^I will\s+", "", t, flags=re.I)
    return " ".join(t.split()).lower()


# --------------------------------------------------------------------------
# panel
# --------------------------------------------------------------------------
def build():
    cat = {}
    with open(MANIFEST) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if "/" in r["gig_id"]:
                cat[r["gig_id"]] = r["category"]
    obs, desc = defaultdict(dict), {}
    with open(PRICES) as f:
        for r in csv.DictReader(f):
            gid = f"{r['seller']}/{r['slug']}"
            if gid not in cat or not is_gig(r["seller"]):
                continue
            try:
                y, mo, pb = int(r["year"]), int(r["month"]), float(r["price_basic"])
            except (TypeError, ValueError):
                continue
            if not (0 < pb <= 10000) or not (1 <= mo <= 12):
                continue
            q = f"{y}Q{(mo - 1) // 3 + 1}"
            if not (qi(WIN_START) <= qi(q) <= qi(WIN_END)):
                continue
            if gid not in desc:
                d = clean(r["title"])
                if len(d) >= MIN_DESC:
                    desc[gid] = d
            try:
                rev = float(r["review_count"])
            except (TypeError, ValueError):
                rev = None
            dt = int(r["date"])
            if q not in obs[gid] or dt > obs[gid][q]["d"]:
                obs[gid][q] = {"p": pb, "rev": rev, "d": dt}
    return cat, obs, desc


CAT, OBS, DESC = build()
QS = sorted({q for d in OBS.values() for q in d}, key=qi)


# --------------------------------------------------------------------------
# E0 exposure
# --------------------------------------------------------------------------
def e0():
    hdr("E0 - EXPOSURE CONSTRUCTION (prereg §2)")
    from sklearn.feature_extraction.text import TfidfVectorizer

    occ = []
    with open(ELO) as f:
        for r in csv.DictReader(f):
            try:
                occ.append((r["Title"], float(r[PRIMARY]), float(r[ROBUST])))
            except (TypeError, ValueError):
                continue
    gids = [g for g in OBS if g in DESC]
    V = TfidfVectorizer(stop_words="english", ngram_range=(1, 2),
                        min_df=1, sublinear_tf=True)
    A = V.fit_transform([DESC[g] for g in gids] + [t for t, _, _ in occ])
    S = (A[:len(gids)] @ A[len(gids):].T).toarray()
    rat = {"primary": np.array([b for _, b, _ in occ]),
           "robust": np.array([d for _, _, d in occ])}

    def score(K, which):
        idx = np.argsort(-S, axis=1)[:, :K]
        w = np.take_along_axis(S, idx, axis=1)
        ok = w.sum(axis=1) > 0
        e = np.full(len(gids), np.nan)
        e[ok] = (w[ok] * rat[which][idx][ok]).sum(axis=1) / w[ok].sum(axis=1)
        return e, ok

    e, ok = score(K_PRIMARY, "primary")
    EXP = {g: v for g, v, o in zip(gids, e, ok) if o}
    ALT = {}
    for K in K_GRID:
        ee, oo = score(K, "primary")
        ALT[f"K={K}"] = {g: v for g, v, o in zip(gids, ee, oo) if o}
    ee, oo = score(K_PRIMARY, "robust")
    ALT["dv_rating_beta"] = {g: v for g, v, o in zip(gids, ee, oo) if o}

    print(f"occupations {len(occ)}   gigs with usable description {len(gids):,}")
    print(f"matched (nonzero TF-IDF) {len(EXP):,} = {100*len(EXP)/len(gids):.1f}%"
          f"   zero-match {100*(1-len(EXP)/len(gids)):.1f}%")
    print(f"exposure: mean {np.mean(list(EXP.values())):.3f}  "
          f"sd {np.std(list(EXP.values())):.3f}  "
          f"IQR {np.percentile(list(EXP.values()),25):.3f}-"
          f"{np.percentile(list(EXP.values()),75):.3f}")

    print("\nper-category mean exposure, and within-category sd (the design's premise):")
    bycat = defaultdict(list)
    for g, v in EXP.items():
        bycat[CAT[g]].append(v)
    order = sorted(bycat, key=lambda c: -np.mean(bycat[c]))
    for c in order:
        print(f"  {c:12} mean {np.mean(bycat[c]):.3f}  sd {np.std(bycat[c]):.3f}  n={len(bycat[c]):,}")
    rng = np.mean(bycat[order[0]]) - np.mean(bycat[order[-1]])
    wsd = np.mean([np.std(bycat[c]) for c in bycat])
    print(f"  between-category range {rng:.3f}   mean within-category sd {wsd:.3f}"
          f"   ratio {wsd/rng:.2f}x")

    print("\n§2 SELECTION AUDIT - dropped (zero-match) vs kept gigs:")
    acc = defaultdict(list)
    for g, d in OBS.items():
        ks = sorted(d, key=qi)
        for a, b in zip(ks, ks[1:]):
            ra, rb, gap = d[a]["rev"], d[b]["rev"], qi(b) - qi(a)
            if ra is None or rb is None or gap < 1 or gap > 2 or rb < ra:
                continue
            if qi(b) <= qi(BREAK_Q):
                acc[g].append((rb - ra) / gap)
    kept = [np.mean(acc[g]) for g in gids if g in EXP and acc.get(g)]
    drop = [np.mean(acc[g]) for g in gids if g not in EXP and acc.get(g)]
    pk = [np.median([OBS[g][q]["p"] for q in OBS[g]]) for g in gids if g in EXP]
    pd_ = [np.median([OBS[g][q]["p"] for q in OBS[g]]) for g in gids if g not in EXP]
    gap = 100 * (np.mean(drop) / np.mean(kept) - 1) if kept else float("nan")
    print(f"  pre-period mean accrual  kept {np.mean(kept):.2f} (n={len(kept):,})"
          f"   dropped {np.mean(drop):.2f} (n={len(drop):,})   gap {gap:+.1f}%")
    print(f"  median price             kept ${np.median(pk):.0f}   dropped ${np.median(pd_):.0f}")
    flag = abs(gap) > 10
    print(f"  §2 rule: |gap| > 10% => declare an external-validity threat."
          f"  {'THREAT DECLARED' if flag else 'within tolerance'}")
    GATES["§2 selection"] = "THREAT" if flag else "OK"
    return EXP, ALT


EXP, ALT = e0()


# --------------------------------------------------------------------------
# panels + fitter
# --------------------------------------------------------------------------
def accrual_rows(win0=WIN_START, win1=WIN_END):
    out = []
    for g, d in OBS.items():
        ks = [q for q in sorted(d, key=qi) if qi(win0) <= qi(q) <= qi(win1)]
        for a, b in zip(ks, ks[1:]):
            ra, rb, gap = d[a]["rev"], d[b]["rev"], qi(b) - qi(a)
            if ra is None or rb is None or gap < 1 or gap > 2 or rb < ra:
                continue
            out.append({"gig": g, "q": b, "t": qi(b),
                        "y": math.log1p((rb - ra) / gap)})
    return out


def price_rows():
    return [{"gig": g, "q": q, "t": qi(q), "y": math.log(d[q]["p"])}
            for g, d in OBS.items() for q in d]


ACC, PRC = accrual_rows(), price_rows()


def prerank():
    raw = {}
    for g, d in OBS.items():
        v = [math.log(d[q]["p"]) for q in d if qi("2021Q1") <= qi(q) <= qi("2022Q1")]
        if len(v) >= 2:
            raw[g] = float(np.mean(v))
    bycat = defaultdict(list)
    for g, v in raw.items():
        bycat[CAT[g]].append((v, g))
    rk = {}
    for c, l in bycat.items():
        l.sort()
        for i, (_, g) in enumerate(l):
            rk[g] = i / (len(l) - 1)
    return rk


PRK = prerank()


def fit(rows, cols, exp, brk=BREAK_Q):
    """Two-way FE (gig, category x quarter) with gig-clustered SEs."""
    P = [r for r in rows if r["gig"] in exp]
    if not P:
        return None
    X = np.column_stack([[fn(r, exp, brk) for r in P] for _, fn in cols])
    y = np.array([r["y"] for r in P])
    gg = [r["gig"] for r in P]
    Xd, yd, nab = absorb2(X, y, gg, [f"{CAT[r['gig']]}|{r['q']}" for r in P])
    b, se = ols_cluster(Xd, yd, gg, n_absorbed=nab)
    return b, se, len(yd), len(set(gg)), [n for n, _ in cols]


def show(res, indent="  "):
    b, se, n, ng, names = res
    for i, nm in enumerate(names):
        t = b[i] / se[i] if se[i] else float("nan")
        lo, hi = b[i] - 1.96 * se[i], b[i] + 1.96 * se[i]
        print(f"{indent}{nm:<26}{b[i]:>9.4f}{se[i]:>8.4f}{t:>8.2f} "
              f"{'*' if abs(t) > 1.96 else ' '}  [{lo:>+7.4f}, {hi:>+7.4f}]")
    print(f"{indent}obs {n:,}   gigs {ng:,}")


POSTX = ("exposure x POST", lambda r, e, brk: e[r["gig"]] * (1.0 if r["t"] > qi(brk) else 0.0))


# --------------------------------------------------------------------------
# E1 primary
# --------------------------------------------------------------------------
def e1():
    hdr("E1 - PRIMARY SPECIFICATION (prereg §4)")
    print("y = log1p(quarterly review accrual);  exposure x POST")
    print("gig FE + CATEGORY x QUARTER FE; gig-clustered SEs.")
    print("The category x quarter FE is the point: it absorbs the platform-wide")
    print("demand fall that steps 46-48 kept mistaking for a treatment effect.\n")
    res = fit(ACC, [POSTX], EXP)
    show(res)
    b, se = res[0][0], res[1][0]
    mde = 2.8 * se
    print(f"\n  realised MDE (80% power, 5%, two-sided) = +/-{mde:.4f} log points"
          f"  = +/-{100*(math.exp(mde)-1):.1f}% of the accrual rate")
    print(f"  estimate is {abs(b)/mde:.2f}x the MDE"
          f" -- {'informative' if abs(b) > mde else 'UNDERPOWERED, a null here excludes little'}")
    print("\n  robustness grid (prereg §2), all must be reported:")
    for k, alt in ALT.items():
        r2 = fit(ACC, [POSTX], alt)
        print(f"    {k:<16}{r2[0][0]:>9.4f}{r2[1][0]:>8.4f}"
              f"{r2[0][0]/r2[1][0]:>8.2f} {'*' if abs(r2[0][0]/r2[1][0])>1.96 else ' '}"
              f"   gigs {r2[3]:,}")
    print("\n  secondary outcome, log(basic price):")
    show(fit(PRC, [POSTX], EXP), indent="    ")
    return res


# --------------------------------------------------------------------------
# G1 parallel trends -- the gate
# --------------------------------------------------------------------------
def g1():
    hdr("G1 - PARALLEL TRENDS (prereg §5). JOINT F-TEST GATE.")
    print("Event study: exposure x quarter, 2022Q3 omitted. The pre-registered rule")
    print("is a JOINT test of the pre-period interactions, not a count -- with 11")
    print("pre-quarters ~0.55 significant coefficients are expected under the null,")
    print("so step 46's count rule fails by construction here.\n")
    P = [r for r in ACC if r["gig"] in EXP]
    use = [q for q in QS if q != "2022Q3" and any(r["q"] == q for r in P)]
    X = np.column_stack([[EXP[r["gig"]] * (r["q"] == q) for r in P] for q in use])
    y = np.array([r["y"] for r in P])
    gg = [r["gig"] for r in P]
    Xd, yd, nab = absorb2(X, y, gg, [f"{CAT[r['gig']]}|{r['q']}" for r in P])
    b, se = ols_cluster(Xd, yd, gg, n_absorbed=nab)
    # full cluster VCV for the joint test
    XtX = np.linalg.pinv(Xd.T @ Xd)
    u = yd - Xd @ b
    cl = defaultdict(list)
    for i, c in enumerate(gg):
        cl[c].append(i)
    meat = np.zeros((Xd.shape[1], Xd.shape[1]))
    for ii in cl.values():
        s = Xd[ii].T @ u[ii]
        meat += np.outer(s, s)
    G = len(cl)
    Vc = XtX @ meat @ XtX * (G / max(G - 1, 1))
    pre = [i for i, q in enumerate(use) if qi(q) < qi(BREAK_Q)]
    post = [i for i, q in enumerate(use) if qi(q) >= qi(BREAK_Q)]
    for i, q in enumerate(use):
        t = b[i] / se[i] if se[i] else float("nan")
        tag = "PRE " if i in pre else "POST"
        print(f"  {tag} {q:9}{b[i]:>9.4f}{se[i]:>8.4f}{t:>8.2f} {'*' if abs(t)>1.96 else ' '}")
    bp = b[pre]
    Vp = Vc[np.ix_(pre, pre)]
    W = float(bp @ np.linalg.pinv(Vp) @ bp)
    k = len(pre)
    # chi2(k) survival, via a Wilson-Hilferty normal approximation
    z = ((W / k) ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k))
    p = 0.5 * math.erfc(z / math.sqrt(2))
    nsig = sum(1 for i in pre if abs(b[i] / se[i]) > 1.96)
    print(f"\n  JOINT test of the {k} pre-period interactions: "
          f"Wald chi2({k}) = {W:.2f}, p = {p:.4f}")
    print(f"  (count rule, for comparison with step 46: {nsig} of {k} significant at 5%)")
    print(f"  pre-period mean {np.mean(b[pre]):+.4f}   post-period mean {np.mean(b[post]):+.4f}")
    ok = p >= 0.05
    GATES["G1 parallel trends"] = "PASS" if ok else "FAIL"
    print(f"\n  GATE: {'PASS' if ok else 'FAIL'}."
          + ("" if ok else " Per prereg §5 the DiD is DEAD and is reported as dead."
                          " Only authorised fallback is §6."))
    return ok


# --------------------------------------------------------------------------
# G2..G5
# --------------------------------------------------------------------------
def g2(base):
    hdr("G2 - NOT-A-PRICE-PROXY (prereg §5)")
    print("Step 49 killed a design because pre-period price rank is contaminated by")
    print("mean reversion. If exposure is really a price proxy, controlling for")
    print("price rank x quarter should kill it.\n")
    rows = [r for r in ACC if r["gig"] in PRK]
    qs = [q for q in QS if q != "2022Q3"]
    cols = [POSTX] + [(f"prk x {q}", (lambda qq: (lambda r, e, brk: PRK[r["gig"]] * (r["q"] == qq)))(q))
                      for q in qs]
    res = fit(rows, cols, EXP)
    b, se = res[0][0], res[1][0]
    t = b / se
    print(f"  exposure x POST, controlling for price rank x quarter:")
    print(f"    {b:>9.4f}{se:>8.4f}{t:>8.2f} {'*' if abs(t)>1.96 else ' '}"
          f"   (uncontrolled: {base[0][0]:+.4f}, t {base[0][0]/base[1][0]:.2f})")
    keep = abs(t) > 1.96 and np.sign(b) == np.sign(base[0][0])
    GATES["G2 not-a-price-proxy"] = "PASS" if keep else "FAIL"
    print(f"  GATE: {'PASS' if keep else 'FAIL'}"
          + ("" if keep else " -- the estimate is a repriced-listing effect, not exposure."))


def g3():
    hdr("G3 - PLACEBO WINDOW (prereg §5)")
    print(f"Window {PLB_START}-{PLB_END}, FALSE break at {PLB_BREAK}. Must be null.\n")
    res = fit(accrual_rows(PLB_START, PLB_END), [("exposure x FALSE POST", POSTX[1])],
              EXP, brk=PLB_BREAK)
    show(res)
    t = res[0][0] / res[1][0]
    ok = abs(t) <= 1.96
    GATES["G3 placebo window"] = "PASS" if ok else "FAIL"
    print(f"  GATE: {'PASS (null, as required)' if ok else 'FAIL -- a false break is significant; the SEs are wrong'}")


def g4():
    hdr("G4 - THE STEP-29 BATTERY (prereg §5). All four must pass.")
    print("\n [1] FIRST DIFFERENCES - passes by construction. The outcome IS a first")
    print("     difference (accrual between consecutive quarters), not a level, so")
    print("     there is no level-on-level spurious regression available.")
    GATES["G4.1 first differences"] = "PASS"

    print("\n [2] LINEAR-TREND HORSE RACE - does exposure x POST survive exposure x trend?")
    res = fit(ACC, [("exposure x trend", lambda r, e, brk: e[r["gig"]] * (r["t"] - qi(BREAK_Q))),
                    POSTX], EXP)
    show(res, indent="   ")
    t = res[0][1] / res[1][1]
    ok2 = abs(t) > 1.96
    GATES["G4.2 trend horse race"] = "PASS" if ok2 else "FAIL"
    print(f"   GATE: {'PASS' if ok2 else 'FAIL -- the break was a differential trend'}")

    print("\n [3] CPI-U PLACEBO - substitute an AI-free series for POST.")
    cpi = {}
    with open(CPI) as f:
        for r in csv.DictReader(f):
            cpi[r["quarter"]] = float(r["cpi_sa"])
    rows = [r for r in ACC if r["q"] in cpi]
    if not rows:
        print("   CPI-U unavailable for this window.")
        GATES["G4.3 CPI-U placebo"] = "N/A"
    else:
        v = [cpi[r["q"]] for r in rows]
        mu, sd = float(np.mean(v)), float(np.std(v))
        res = fit(rows, [("exposure x CPI-U", lambda r, e, brk: e[r["gig"]] * (cpi[r["q"]] - mu) / sd)], EXP)
        show(res, indent="   ")
        t = res[0][0] / res[1][0]
        ok3 = abs(t) <= 1.96
        GATES["G4.3 CPI-U placebo"] = "PASS" if ok3 else "FAIL"
        print(f"   CPI-U has no AI content. Significant here => the design is not"
              f" isolating AI.\n   GATE: {'PASS (null)' if ok3 else 'FAIL (significant)'}")

    print("\n [4] NEWEY-WEST on the collapsed high-minus-low exposure difference series.")
    med = float(np.median(list(EXP.values())))
    byq = defaultdict(lambda: {1: [], 0: []})
    for r in ACC:
        if r["gig"] in EXP:
            byq[r["q"]][1 if EXP[r["gig"]] > med else 0].append(r["y"])
    qs = [q for q in sorted(byq, key=qi) if byq[q][1] and byq[q][0]]
    d = np.array([np.mean(byq[q][1]) - np.mean(byq[q][0]) for q in qs])
    tt = np.array([qi(q) for q in qs], float)
    tt -= tt.mean()
    X = np.column_stack([np.ones(len(d)), tt, (np.array([qi(q) for q in qs]) > qi(BREAK_Q)).astype(float)])
    beta = np.linalg.pinv(X.T @ X) @ (X.T @ d)
    u = d - X @ beta
    XtX = np.linalg.pinv(X.T @ X)
    S = (X * u[:, None]).T @ (X * u[:, None])
    for l in range(1, 5):
        Gm = (X[l:] * u[l:, None]).T @ (X[:-l] * u[:-l, None])
        S += (1 - l / 5) * (Gm + Gm.T)
    nw = np.sqrt(np.maximum(np.diag(XtX @ S @ XtX), 0))
    dw = float(np.sum(np.diff(u) ** 2) / np.sum(u ** 2))
    print(f"   {len(qs)} quarterly differences, Bartlett lag 4, Durbin-Watson {dw:.2f}")
    for nm, i in (("trend", 1), ("post", 2)):
        print(f"   {nm:<8}{beta[i]:>10.4f}{nw[i]:>9.4f}{beta[i]/nw[i] if nw[i] else 0:>8.2f}")
    ok4 = 1.5 <= dw <= 2.5
    GATES["G4.4 Newey-West"] = "PASS" if ok4 else "FAIL"
    print(f"   GATE: DW {'in [1.5,2.5], no residual autocorrelation' if ok4 else 'OUTSIDE [1.5,2.5] -- SEs suspect'}"
          f" (step 29's fatal readings were 0.22-1.08)")


def g5(base):
    hdr("G5 - COMPOSITION (prereg §5)")
    print("Step 49: gig FE do NOT protect against composition -- the quota manifest")
    print(f"adds cheaper listings at 2022Q3. Re-run on listings present in >={BAL_FRAC:.0%}")
    print(f"of quarters in {BAL_WIN[0]}-{BAL_WIN[1]}.\n")
    qs = [q for q in QS if qi(BAL_WIN[0]) <= qi(q) <= qi(BAL_WIN[1])]
    need = int(math.ceil(BAL_FRAC * len(qs)))
    bal = {g for g, d in OBS.items() if sum(1 for q in qs if q in d) >= need}
    rows = [r for r in ACC if r["gig"] in bal]
    res = fit(rows, [POSTX], EXP)
    show(res)
    t = res[0][0] / res[1][0]
    keep = abs(t) > 1.96 and np.sign(res[0][0]) == np.sign(base[0][0])
    GATES["G5 composition"] = "PASS" if keep else "FAIL"
    print(f"  balanced listings {len(bal):,}   (unbalanced estimate {base[0][0]:+.4f},"
          f" t {base[0][0]/base[1][0]:.2f})")
    print(f"  GATE: {'PASS' if keep else 'FAIL -- sign or significance does not survive a balanced frame'}")


# --------------------------------------------------------------------------
# F  the §6 fallback
# --------------------------------------------------------------------------
def fallback():
    hdr("F - PREREG §6 FALLBACK: descriptive dose-response. NOT IDENTIFIED.")
    print("Mean log1p accrual before and after 2022Q4, by exposure decile.")
    print("This is a DESCRIPTION. No causal reading is authorised by the")
    print("pre-registration, and none is offered.\n")
    e = np.array([EXP[g] for g in EXP])
    cuts = np.percentile(e, np.arange(0, 101, 10))
    dec = {}
    for g, v in EXP.items():
        dec[g] = min(int(np.searchsorted(cuts, v, side="right")) - 1, 9)
    agg = defaultdict(lambda: {"pre": [], "post": []})
    for r in ACC:
        if r["gig"] in dec:
            agg[dec[r["gig"]]]["pre" if r["t"] <= qi(BREAK_Q) else "post"].append(r["y"])
    print(f"  {'decile':8}{'exposure':>10}{'n gigs':>9}{'pre':>9}{'post':>9}{'change':>10}")
    for d in range(10):
        a, b = agg[d]["pre"], agg[d]["post"]
        if not a or not b:
            continue
        ng = sum(1 for g in dec.values() if g == d)
        ch = 100 * (math.exp(np.mean(b) - np.mean(a)) - 1)
        print(f"  {d+1:<8}{(cuts[d]+cuts[d+1])/2:>10.3f}{ng:>9,}"
              f"{np.mean(a):>9.3f}{np.mean(b):>9.3f}{ch:>9.1f}%")
    print("\n  If the decile changes are flat in exposure, the platform-wide reading")
    print("  from steps 46-48 stands and nothing category- or task-specific is added.")


def verdict(base):
    hdr("VERDICT")
    w = max(len(k) for k in GATES)
    for k, v in GATES.items():
        print(f"  {k:<{w}}  {v}")
    fails = [k for k, v in GATES.items() if v == "FAIL"]
    b, se = base[0][0], base[1][0]
    print(f"\n  primary estimate  exposure x POST = {b:+.4f} (se {se:.4f}, t {b/se:.2f})")
    if GATES.get("G1 parallel trends") == "FAIL":
        print("\n  G1 FAILED. Per prereg §5 the DiD is DEAD and reported as dead. The")
        print("  primary estimate above is NOT identified and must not be quoted as an")
        print("  effect. This is the SIXTH design to fail on this data; per prereg §0")
        print("  that is evidence about the data, not only about the designs.")
    elif fails:
        print(f"\n  {len(fails)} gate(s) failed: {', '.join(fails)}. Not causal.")
    else:
        print("\n  ALL GATES PASS. This is the first identified AI effect in the project;")
        print("  treat with the suspicion prereg §0 records, and replicate before drafting.")


if __name__ == "__main__":
    base = e1()
    ok = g1()
    g2(base); g3(); g4(); g5(base)
    fallback()
    verdict(base)
