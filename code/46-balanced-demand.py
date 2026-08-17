#!/usr/bin/env python3
"""
Step 46: Phase 0 of the transaction-volume study — demand breaks on the balanced frame.

Runs the specification LOCKED in `plans/active/transaction-volume-prereg.md`
(registered 2026-08-17) against `data/pilot/balanced-prices.csv`. Nothing here is
chosen after seeing an outcome; every knob below is quoted from that file.

WHY THIS EXISTS. `code/24-margin-diagnostics.py` already asked whether demand broke
at ChatGPT and found null in all seven categories — but on the shipped panels'
10,275 review-accrual observations, with a minimum detectable effect of +/-23%
(coding) to +/-66% (translation). A null that wide excludes almost nothing. The
balanced frame carries 242,468 observations, 23.6x more, which is the difference
between an uninformative null and a publishable one.

WHAT IT REPORTS, in the pre-registered order:

  P0  Frame audit + per-category ITS break at 2022Q4 with the REALISED MDE next to
      step 24's. This is Phase 0's decision gate.
  P1  Parallel trends. Event study, HIGH vs LOW, 2022Q3 omitted. A PASS/FAIL GATE:
      if it fails, the DiD is dead and is reported as dead (fallback: synthetic
      control on the LOW categories).
  P2  The pre-registered DiD: HIGH x POST, gig + quarter FE, gig-clustered SEs.
  P3  Placebo window 2018Q3-2019Q4 with a FALSE break at 2019Q2. Must return null.
  P4  The step-29 battery: first differences, linear-trend horse race, CPI-U
      placebo, Newey-West. All four must pass before anything is called causal.

Pre-registered arms (`data/exposure-ranking.csv`, from Eloundou et al. 2023):
  HIGH = translation, writing      (top-2 human beta, top-3 GPT-4 beta)
  LOW  = video, audio              (bottom-2 on both)
  MID  = marketing, coding, design (quarantined; coding because the two annotators
                                    disagree hard — GPT-4 ranks it 1st, humans 4th)

READ BEFORE QUOTING ANY NUMBER:
  * This is Q1 of the parent plan's decomposition — do SURVIVING GIGS SELL LESS.
    It is NOT "did platform-wide transactions fall" (Q3), which the crawl cannot see.
  * Window ends 2024Q4. Accrual observations per quarter collapse 7,774 -> 1,605 ->
    ~700 after that. The treatment period is eight quarters, 2022Q4-2024Q4.
  * Age = period - cohort under gig FE, so the quarter PATH contains the panel's
    ageing profile and is not demand. Only the BREAK is reported as a demand result.
  * True exit is not measurable (n_404 = 0 across 509,339 captures). Nothing here
    is labelled exit.

Run:  python3 code/46-balanced-demand.py
"""

import csv
import importlib.util
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
m24 = _load("m24", "24-margin-diagnostics.py")

absorb, ols_cluster = m24.absorb, m24.ols_cluster
CATS = tpd.CATS
PILOT = BASE / "data" / "pilot"

PRICES = PILOT / "balanced-prices.csv"
MANIFEST = PILOT / "balanced-manifest-1200.tsv"
RANKING = BASE / "data" / "exposure-ranking.csv"
CPI = PILOT / "cpi-quarterly.csv"

# ---- everything below is quoted from the pre-registration, not chosen here ----
BREAK_Q = "2022Q4"          # ChatGPT, 2022-11-30. Single pre-specified break.
WIN_START, WIN_END = "2018Q1", "2024Q4"
PLACEBO_START, PLACEBO_END, PLACEBO_BREAK = "2018Q3", "2019Q4", "2019Q2"
HIGH = {"translation", "writing"}
LOW = {"video", "audio"}
MID = {"marketing", "coding", "design"}
# step 24's per-category MDE, for the side-by-side that is Phase 0's whole point
MDE_24 = {"coding": 23, "design": 27, "writing": 31, "video": 38,
          "marketing": 44, "audio": 52, "translation": 66}


def qi(q):
    """2022Q4 -> 8091, monotone quarter index (linear in time)."""
    return int(q[:4]) * 4 + int(q[-1])


# --------------------------------------------------------------------------
# panel
# --------------------------------------------------------------------------
def build_panel():
    gig_cat = {}
    with open(MANIFEST) as f:
        for row in csv.DictReader(f, delimiter="\t"):
            gid = row["gig_id"]
            if "/" in gid:
                gig_cat[tuple(gid.split("/", 1))] = row["category"]

    raw = defaultdict(lambda: defaultdict(list))
    first = {}
    with open(PRICES) as f:
        for row in csv.DictReader(f):
            key = (row["seller"], row["slug"])
            if key not in gig_cat or not is_gig(row["seller"]):
                continue
            q = tpd.to_quarter(row["year"], row["month"])
            if not q:
                continue
            rev_s = row.get("review_count") or ""
            try:
                rev = float(rev_s) if rev_s != "" else None
            except ValueError:
                rev = None
            if rev is not None:
                raw[key][q].append(rev)
            d = row["date"]
            if key not in first or d < first[key][0]:
                first[key] = (d, q)

    panel = {}
    for key, qs in raw.items():
        cat = gig_cat.get(key)
        if cat not in CATS:
            continue
        # within-quarter: max(), because review_count is cumulative and weakly
        # increasing, so max is the end-of-quarter level a difference should span
        panel[key] = {"cat": cat,
                      "q": {q: max(v) for q, v in qs.items()},
                      "first": first[key][1]}
    return panel


def transitions(panel, start=WIN_START, end=WIN_END):
    """Within-gig adjacent-quarter review accrual inside [start, end]."""
    lo, hi = qi(start), qi(end)
    out = []
    for key, rec in panel.items():
        cells = rec["q"]
        order = [q for q in sorted(cells, key=qi) if lo <= qi(q) <= hi]
        birth = qi(rec["first"])
        for a, b in zip(order, order[1:]):
            dq = qi(b) - qi(a)
            if dq <= 0:
                continue
            drev = cells[b] - cells[a]
            if drev < 0:                 # review deletion / reset — 0.58% of rows
                continue
            rate = drev / dq
            out.append({
                "gig": key, "cat": rec["cat"], "q1": b, "dq": dq,
                "rate": rate,
                "y": np.log1p(rate),     # PRE-REGISTERED outcome
                "age": max(qi(a) - birth, 0),
                "post": 1.0 if qi(b) > qi(BREAK_Q) else 0.0,
                "t": qi(b),
            })
    return out


# --------------------------------------------------------------------------
# two-way fixed effects by alternating projections
# --------------------------------------------------------------------------
def absorb2(X, y, g1, g2, tol=1e-10, maxit=200):
    """Demean X, y within two factors simultaneously. -> Xd, yd, n_absorbed."""
    i1, i2 = defaultdict(list), defaultdict(list)
    for i, g in enumerate(g1):
        i1[g].append(i)
    for i, g in enumerate(g2):
        i2[g].append(i)
    Z = np.column_stack([X, y]).astype(float)
    for _ in range(maxit):
        prev = Z.copy()
        for ii in i1.values():
            Z[ii] -= Z[ii].mean(axis=0)
        for ii in i2.values():
            Z[ii] -= Z[ii].mean(axis=0)
        if np.max(np.abs(Z - prev)) < tol:
            break
    return Z[:, :-1], Z[:, -1], len(i1) + len(i2) - 1


def fit(rows, cols, label, extra_absorb_quarter=True):
    """Two-way-FE OLS with gig-clustered SEs. cols: list of (name, fn)."""
    X = np.column_stack([[fn(r) for r in rows] for _, fn in cols])
    y = np.array([r["y"] for r in rows])
    gigs = [r["gig"] for r in rows]
    if extra_absorb_quarter:
        Xd, yd, nab = absorb2(X, y, gigs, [r["q1"] for r in rows])
    else:
        Xd, yd, gigs, ng = absorb(X, y, gigs)
        nab = ng
    b, se = ols_cluster(Xd, yd, gigs, n_absorbed=nab)
    return b, se, len(yd), [n for n, _ in cols]


def show(b, se, names, base_rate, indent="    "):
    for i, n in enumerate(names):
        t = b[i] / se[i] if se[i] else float("nan")
        lo, hi = b[i] - 1.96 * se[i], b[i] + 1.96 * se[i]
        # log-point -> % of the pre-period rate
        pct = 100 * (np.exp(b[i]) - 1)
        plo, phi = 100 * (np.exp(lo) - 1), 100 * (np.exp(hi) - 1)
        star = "*" if abs(t) > 1.96 else " "
        print(f"{indent}{n:<18}{b[i]:>9.4f} {se[i]:>8.4f} {t:>7.2f} {star}  "
              f"{pct:>+7.1f}%  [{plo:>+7.1f}, {phi:>+7.1f}]")


# --------------------------------------------------------------------------
# P0 — frame audit + per-category ITS, with the realised MDE
# --------------------------------------------------------------------------
def p0(tr):
    print("=" * 92)
    print("P0 — FRAME AUDIT AND PER-CATEGORY BREAK AT 2022Q4  (Phase 0 decision gate)")
    print("=" * 92)
    n_g = len({r["gig"] for r in tr})
    print(f"\n  accrual observations {len(tr):,}   gigs {n_g:,}   "
          f"window {WIN_START}-{WIN_END}")
    per = Counter(r["cat"] for r in tr)
    print(f"\n  {'cat':<12}{'arm':>6}{'obs':>10}{'gigs':>8}")
    for c in sorted(CATS, key=lambda c: -per[c]):
        arm = "HIGH" if c in HIGH else ("LOW" if c in LOW else "mid")
        g = len({r["gig"] for r in tr if r["cat"] == c})
        print(f"  {c:<12}{arm:>6}{per[c]:>10,}{g:>8,}")

    print(f"\n  --- ITS: y = ln(1+reviews/qtr), gig FE + linear trend + post ---")
    print(f"  gig-clustered SEs.  'MDE' = 1.96*se as % of the pre-period rate.")
    print(f"\n  {'cat':<12}{'obs':>9}{'preRate':>9}{'post':>9}{'se':>8}{'t':>7}"
          f"{'   effect %':>12}{'  MDE now':>10}{'  MDE s24':>10}")
    out = {}
    for c in CATS:
        sub = [r for r in tr if r["cat"] == c]
        pre = [r["rate"] for r in sub if r["post"] == 0]
        pre_rate = float(np.mean(pre)) if pre else float("nan")
        b, se, n, names = fit(
            sub, [("trend", lambda r: r["t"]), ("post", lambda r: r["post"])],
            c, extra_absorb_quarter=False)
        eff = 100 * (np.exp(b[1]) - 1)
        mde = 100 * (np.exp(1.96 * se[1]) - 1)
        out[c] = (b[1], se[1], eff, mde, n)
        print(f"  {c:<12}{n:>9,}{pre_rate:>9.2f}{b[1]:>9.4f}{se[1]:>8.4f}"
              f"{b[1]/se[1]:>7.2f}{eff:>+11.1f}%{mde:>+9.1f}%{MDE_24[c]:>+9.0f}%")

    print(f"\n  => POWER GAIN, the reason Phase 0 exists: MDE now vs step 24.")
    for c in sorted(out, key=lambda c: out[c][3]):
        print(f"     {c:<12} +/-{out[c][3]:>5.1f}%   (step 24: +/-{MDE_24[c]:>3.0f}%)"
              f"   {MDE_24[c]/out[c][3]:>5.1f}x tighter")

    # Does the SIZE of the break line up with pre-registered exposure at all?
    # This is the descriptive form of the question and it needs no identification
    # assumption — but with n=7 it has almost no power, so it is a sanity check on
    # the DiD, not a substitute for it.
    exp = {}
    with open(RANKING) as f:
        for row in csv.DictReader(f):
            exp[row["category"]] = float(row["exposure_primary"])
    cats = [c for c in CATS if c in out and c in exp]
    ex = np.array([exp[c] for c in cats])
    ef = np.array([out[c][2] for c in cats])          # % effect, negative = fall
    rx = np.argsort(np.argsort(-ex))                  # rank by exposure, desc
    rf = np.argsort(np.argsort(ef))                   # rank by fall size, desc
    n = len(cats)
    rho = 1 - 6 * float(np.sum((rx - rf) ** 2)) / (n * (n * n - 1))
    print(f"\n  => DOES THE BREAK TRACK EXPOSURE? Spearman rho over {n} categories.")
    print(f"     {'cat':<12}{'exposure':>10}{'rank':>6}{'break %':>10}{'rank':>6}")
    for i, c in enumerate(sorted(cats, key=lambda c: -exp[c])):
        j = cats.index(c)
        print(f"     {c:<12}{exp[c]:>10.3f}{rx[j]+1:>6}{ef[j]:>+9.1f}%{rf[j]+1:>6}")
    print(f"\n     rho = {rho:+.3f}   (n=7; |rho| must exceed ~0.79 for p<0.05,")
    print(f"     so this is NOT significant either way and cannot rank categories.)")
    return out


# --------------------------------------------------------------------------
# P1 — parallel trends: a PASS/FAIL gate, not a diagnostic
# --------------------------------------------------------------------------
def p1(tr):
    print("\n" + "=" * 92)
    print("P1 — PARALLEL TRENDS  (pre-registered PASS/FAIL gate)")
    print("=" * 92)
    sub = [r for r in tr if r["cat"] in HIGH | LOW]
    for r in sub:
        r["hi"] = 1.0 if r["cat"] in HIGH else 0.0
    qs = sorted({r["q1"] for r in sub}, key=qi)
    omit = "2022Q3"
    inter = [q for q in qs if q != omit]
    cols = [(f"hi_{q}", (lambda q: (lambda r: r["hi"] if r["q1"] == q else 0.0))(q))
            for q in inter]
    b, se, n, names = fit(sub, cols, "event-study")

    print(f"\n  HIGH x quarter interactions, {omit} omitted. gig + quarter FE, "
          f"gig-clustered SEs.\n  obs {n:,}")
    print(f"\n  {'quarter':<10}{'coef':>9}{'se':>8}{'t':>7}   sig")
    pre_sig, pre_pts = [], []
    for i, q in enumerate(inter):
        t = b[i] / se[i] if se[i] else 0.0
        tag = "post" if qi(q) > qi(BREAK_Q) else "pre "
        star = "*" if abs(t) > 1.96 else " "
        if tag == "pre ":
            pre_pts.append(b[i])
            if abs(t) > 1.96:
                pre_sig.append((q, b[i], t))
        print(f"  {q:<10}{b[i]:>9.4f}{se[i]:>8.4f}{t:>7.2f} {star}  {tag}")

    # pre-registered rule: NO pre-period coefficient significant at 5% AND no
    # monotone pre-trend in the point estimates. Both, not either.
    mono = len(pre_pts) >= 3 and (all(x <= y for x, y in zip(pre_pts, pre_pts[1:]))
                                  or all(x >= y for x, y in zip(pre_pts, pre_pts[1:])))
    print(f"\n  pre-period coefficients significant at 5%: {len(pre_sig)} "
          f"of {len(pre_pts)}")
    if pre_sig:
        for q, c, t in pre_sig:
            print(f"     {q}  coef {c:+.4f}  t {t:+.2f}")
    print(f"  monotone pre-trend in point estimates: {'YES' if mono else 'no'}")
    ok = (not pre_sig) and (not mono)
    print(f"\n  GATE: {'PASS — the DiD may be estimated.' if ok else 'FAIL'}")
    if not ok:
        print("  Pre-registered consequence: the DiD is reported as DEAD and the")
        print("  fallback is synthetic control on the LOW categories. No third")
        print("  fallback is authorised.")
    return ok, sub


# --------------------------------------------------------------------------
# P2 — the pre-registered DiD
# --------------------------------------------------------------------------
def p2(sub):
    print("\n" + "=" * 92)
    print("P2 — PRE-REGISTERED DiD:  HIGH x POST, gig + quarter FE")
    print("=" * 92)
    hi_n = len({r["gig"] for r in sub if r["hi"] == 1})
    lo_n = len({r["gig"] for r in sub if r["hi"] == 0})
    print(f"\n  HIGH = {sorted(HIGH)}  ({hi_n:,} gigs)")
    print(f"  LOW  = {sorted(LOW)}  ({lo_n:,} gigs)")
    print(f"  treatment period {BREAK_Q}-{WIN_END} = eight quarters\n")
    print(f"    {'term':<18}{'coef':>9} {'se':>8} {'t':>7}     {'effect':>8}"
          f"  {'95% CI on the rate':>22}")
    b, se, n, names = fit(
        sub, [("HIGH x POST", lambda r: r["hi"] * r["post"])], "did")
    show(b, se, names, None)
    print(f"\n  obs {n:,}   SEs clustered on gig")
    mde = 100 * (np.exp(1.96 * se[0]) - 1)
    print(f"  realised MDE on the primary contrast: +/-{mde:.2f}%")
    print(f"  pre-registered adequacy standard: +/-5%  -> "
          f"{'MET' if mde <= 5 else 'NOT MET'}")
    return b[0], se[0], mde


# --------------------------------------------------------------------------
# P3 — placebo window
# --------------------------------------------------------------------------
def p3(panel):
    print("\n" + "=" * 92)
    print(f"P3 — PLACEBO: window {PLACEBO_START}-{PLACEBO_END}, "
          f"FALSE break at {PLACEBO_BREAK}")
    print("=" * 92)
    tr = transitions(panel, PLACEBO_START, PLACEBO_END)
    sub = [r for r in tr if r["cat"] in HIGH | LOW]
    for r in sub:
        r["hi"] = 1.0 if r["cat"] in HIGH else 0.0
        r["post"] = 1.0 if qi(r["q1"]) > qi(PLACEBO_BREAK) else 0.0
    if len(sub) < 100 or len({r["post"] for r in sub}) < 2:
        print(f"\n  not estimable: {len(sub)} observations")
        return None
    print(f"\n  obs {len(sub):,}   gigs {len({r['gig'] for r in sub}):,}   "
          f"(the pre-period is the frame's thinnest — n stated per the prereg)")
    print(f"\n    {'term':<18}{'coef':>9} {'se':>8} {'t':>7}     {'effect':>8}"
          f"  {'95% CI on the rate':>22}")
    b, se, n, names = fit(
        sub, [("HIGH x FALSEPOST", lambda r: r["hi"] * r["post"])], "placebo")
    show(b, se, names, None)
    ok = abs(b[0] / se[0]) < 1.96
    print(f"\n  must return null: {'PASS' if ok else 'FAIL — the design is picking'
                                  ' up something that predates AI'}")
    return ok


# --------------------------------------------------------------------------
# P4 — the step-29 battery
# --------------------------------------------------------------------------
def p4(sub):
    print("\n" + "=" * 92)
    print("P4 — THE STEP-29 BATTERY  (all four must pass to call anything causal)")
    print("=" * 92)

    print("\n  [1] FIRST DIFFERENCES — passes by construction, and this is not a")
    print("      dodge. The outcome IS a first difference: review accrual between")
    print("      consecutive quarters, not a level. The spurious-regression failure")
    print("      that killed the elasticity table was a LEVEL-on-LEVEL regression of")
    print("      two trending series; there is no level here to trend.")

    print("\n  [2] LINEAR-TREND HORSE RACE — does HIGH x POST survive HIGH x trend?")
    b, se, n, names = fit(sub, [
        ("HIGH x trend", lambda r: r["hi"] * (r["t"] - 8090)),
        ("HIGH x POST", lambda r: r["hi"] * r["post"]),
    ], "horserace")
    print(f"\n    {'term':<18}{'coef':>9} {'se':>8} {'t':>7}     {'effect':>8}"
          f"  {'95% CI on the rate':>22}")
    show(b, se, names, None)
    print(f"\n      A differential linear trend is the rival explanation. If")
    print(f"      HIGH x POST collapses once it is included, the 'break' was a trend.")

    print("\n  [3] CPI-U PLACEBO — substitute an AI-free time series for POST.")
    cpi = {}
    with open(CPI) as f:
        for row in csv.DictReader(f):
            cpi[row["quarter"]] = float(row["cpi_sa"])
    vals = [cpi[r["q1"]] for r in sub if r["q1"] in cpi]
    if not vals:
        print("      CPI-U unavailable for this window — cannot run.")
    else:
        mu, sd = float(np.mean(vals)), float(np.std(vals))
        ok = [r for r in sub if r["q1"] in cpi]
        b2, se2, n2, nm2 = fit(ok, [
            ("HIGH x CPI-U", lambda r: r["hi"] * (cpi[r["q1"]] - mu) / sd),
        ], "cpi")
        print(f"\n    {'term':<18}{'coef':>9} {'se':>8} {'t':>7}     {'effect':>8}"
              f"  {'95% CI on the rate':>22}")
        show(b2, se2, nm2, None)
        print(f"\n      CPI-U has no AI content. Quarter FE absorb its level, so this")
        print(f"      identifies whether HIGH categories simply move differentially")
        print(f"      with ANY smooth time series. Significant here => the design is")
        print(f"      not isolating AI. (obs {n2:,}, CPI-U standardised)")

    print("\n  [4] NEWEY-WEST on the collapsed HIGH-minus-LOW difference series.")
    byq = defaultdict(lambda: {1.0: [], 0.0: []})
    for r in sub:
        byq[r["q1"]][r["hi"]].append(r["y"])
    qs = [q for q in sorted(byq, key=qi)
          if byq[q][1.0] and byq[q][0.0]]
    d = np.array([np.mean(byq[q][1.0]) - np.mean(byq[q][0.0]) for q in qs])
    post = np.array([1.0 if qi(q) > qi(BREAK_Q) else 0.0 for q in qs])
    tt = np.array([qi(q) for q in qs], dtype=float)
    tt -= tt.mean()
    X = np.column_stack([np.ones(len(d)), tt, post])
    beta = np.linalg.pinv(X.T @ X) @ (X.T @ d)
    u = d - X @ beta
    L = 4
    XtX_inv = np.linalg.pinv(X.T @ X)
    S = (X * u[:, None]).T @ (X * u[:, None])
    for l in range(1, L + 1):
        w = 1 - l / (L + 1)
        G = (X[l:] * u[l:, None]).T @ (X[:-l] * u[:-l, None])
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    nw = np.sqrt(np.maximum(np.diag(V), 0))
    dw = float(np.sum(np.diff(u) ** 2) / np.sum(u ** 2))
    print(f"\n      {len(qs)} quarterly difference observations, "
          f"Bartlett lag {L}, Durbin-Watson {dw:.2f}")
    print(f"      {'term':<14}{'coef':>10}{'NW se':>9}{'t':>7}")
    for nm, i in (("trend", 1), ("post", 2)):
        print(f"      {nm:<14}{beta[i]:>10.4f}{nw[i]:>9.4f}"
              f"{beta[i]/nw[i] if nw[i] else 0:>7.2f}")
    print(f"      DW near 2 => no residual autocorrelation to invalidate the SE.")
    print(f"      (Step 29's fatal readings were 0.22-1.08.)")


def main():
    print("Phase 0 — transaction-volume study, pre-registered 2026-08-17")
    print(f"frame: {PRICES.name} x {MANIFEST.name}\n")
    panel = build_panel()
    tr = transitions(panel)
    p0(tr)
    ok, sub = p1(tr)
    p2(sub)
    p3(panel)
    p4(sub)
    print("\n" + "=" * 92)
    print("Every number above is Q1 — do surviving gigs sell less. Not platform")
    print("volume (Q3, unmeasurable here). Window ends 2024Q4. Exit is never claimed.")
    print("=" * 92)


if __name__ == "__main__":
    main()
