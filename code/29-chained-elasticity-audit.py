#!/usr/bin/env python3
"""Step 29: does the chained series and its elasticity table survive in the paper?
Phase 1 decision D4 of `plans/active/publication.md`.

TWO SEPARATE QUESTIONS, and they have different answers.

Q1. THE CHAINED-VS-GEKS COMPARISON. Section 3.4 quantifies chain drift as chained
    +217.7% against GEKS +44.6% and attributes the whole gap to drift. But TD1
    (`plans/tech-debt-tracker.md`) says part of it is a coding defect: step 12
    keys within-gig relatives by DESTINATION QUARTER ALONE, so a gig unobserved
    for k quarters files its entire k-quarter change as a one-quarter change,
    which the chain then stacks on top of the growth already contributed by gigs
    that were observed in between. This script splits the gap in two:

        as-built  ->  adjacent-only     = the TD1 defect
        adjacent-only  ->  GEKS         = genuine chain drift

    All three are rebuilt on the SAME production panel from 19-tpd-index.py, so
    the comparison is not contaminated by panel differences. That makes it a
    reconstruction of step 12's ESTIMATOR, not a reproduction of its published
    numbers (step 12 builds its own panel and bases at 2019Q1); the shipped
    figures are printed alongside for the record.

Q2. THE ELASTICITY TABLE. `data/pilot/panel-elasticity.csv` regresses the log of
    a trending price index on the log of a trending AI-benchmark score over ~20
    quarterly observations, with no control group. That is the textbook setup for
    a spurious regression, so the question is not "is the coefficient big" but
    "does this regression have any content at all". Four tests, none of which the
    original ran:

      1. DURBIN-WATSON on the residuals. Serially correlated residuals mean the
         reported SEs — and therefore every p < 0.01 in the table — are fiction.
      2. NEWEY-WEST SEs at lag 4, the honest version of the same standard error.
      3. TWO PLACEBOS: refit with a LINEAR TIME TREND, and with LN CPI-U, in
         place of the AI score. Neither has any AI content. If they fit as well,
         the AI score is proxying for time and nothing else.
      4. FIRST DIFFERENCES: d ln P on d ln(AI). Common trends drop out, so a
         relationship that survives differencing is real and one that vanishes
         was the trend.

Q3 falls out of Q1+Q2: does the category RANKING — the thing the table is
   actually used for — survive being computed on a different price series?

Measurement only -- writes nothing outside scratchpad/.

Run:  python3 code/29-chained-elasticity-audit.py
"""
import csv
import importlib.util
import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "code"))


def load(name, fn):
    spec = importlib.util.spec_from_file_location(name, BASE / "code" / fn)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


tpd = load("tpd", "19-tpd-index.py")
geks = load("geks", "21-geks-index.py")
CATS = tpd.CATS
PILOT = BASE / "data" / "pilot"
BASE_Q = tpd.START_Q          # 2020Q1 — the published base (D3, 2026-08-06)
MIN_REL = 3                   # step 12 requires >=3 relatives at a quarter
NW_LAG = 4


def q_int(q):
    return tpd.q_to_int(q)


def q_pos(q):
    """quarter -> integer position on the grid, so gap length is measurable."""
    y, n = q.split("Q")
    return int(y) * 4 + int(n) - 1


# ---------------------------------------------------------------- estimators
def chained_jevons(panel_cat, adjacent_only):
    """Step 12's chain, rebuilt. adjacent_only=False reproduces the TD1 defect.

    Relatives are keyed by destination quarter, exactly as step 12 does. With
    adjacent_only=True a within-gig link is admitted only when it spans exactly
    one quarter, so a k-quarter change can no longer be booked as a one-quarter
    change."""
    rel = defaultdict(list)
    for qs in panel_cat.values():
        obs = sorted(qs, key=q_int)
        for a, b in zip(obs, obs[1:]):
            if qs[a] <= 0:
                continue
            if adjacent_only and q_pos(b) - q_pos(a) != 1:
                continue
            r = qs[b] / qs[a]
            if 0.1 <= r <= 10:            # step 12's outlier guard
                rel[b].append(r)
    if not rel:
        return {}
    quarters = sorted({q for qs in panel_cat.values() for q in qs}, key=q_int)
    quarters = [q for q in quarters if q_int(q) >= q_int(BASE_Q)]
    if not quarters or quarters[0] != BASE_Q:
        return {}
    index, last = {BASE_Q: 100.0}, BASE_Q
    for q in quarters[1:]:
        if len(rel.get(q, [])) >= MIN_REL:
            index[q] = index[last] * math.exp(float(np.mean(np.log(rel[q]))))
            last = q
    return index


def geks_levels(panel_cat):
    idx, _, _ = geks.geks_index(panel_cat, rng=None, n_boot=0, window_start=BASE_Q)
    return idx


# ---------------------------------------------------------------- regressions
def ols(y, X):
    """X already includes a constant column. Returns b, se, resid, r2."""
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ b
    n, k = X.shape
    XtXi = np.linalg.pinv(X.T @ X)
    s2 = float(e @ e) / max(n - k, 1)
    se = np.sqrt(np.diag(s2 * XtXi))
    ybar = float(np.mean(y))
    ss_tot = float(((y - ybar) ** 2).sum())
    r2 = 1 - float(e @ e) / ss_tot if ss_tot > 0 else float("nan")
    return b, se, e, r2


def newey_west_se(X, e, lag):
    """HAC standard errors — the honest SE for a trending time series."""
    n, k = X.shape
    XtXi = np.linalg.pinv(X.T @ X)
    S = (X * e[:, None]).T @ (X * e[:, None])
    for L in range(1, min(lag, n - 1) + 1):
        w = 1.0 - L / (lag + 1.0)
        A = (X[L:] * e[L:, None]).T @ (X[:-L] * e[:-L, None])
        S += w * (A + A.T)
    V = XtXi @ S @ XtXi
    return np.sqrt(np.maximum(np.diag(V), 0.0))


def durbin_watson(e):
    return float(((np.diff(e)) ** 2).sum() / (e @ e)) if float(e @ e) > 0 else float("nan")


def bivariate(y, x):
    """y on [1, x]; returns slope, ols se, nw se, t_nw, r2, dw."""
    X = np.column_stack([np.ones(len(x)), x])
    b, se, e, r2 = ols(y, X)
    nw = newey_west_se(X, e, NW_LAG)
    t_nw = b[1] / nw[1] if nw[1] > 0 else float("nan")
    return dict(slope=float(b[1]), se=float(se[1]), nw=float(nw[1]),
                t_ols=float(b[1] / se[1]) if se[1] > 0 else float("nan"),
                t_nw=float(t_nw), r2=r2, dw=durbin_watson(e), n=len(y))


# ---------------------------------------------------------------- AI scores
def ai_scores(quarters):
    """Reproduce step 12's cat_ai construction exactly (same mapping, same
    interpolation, same min-max normalisation, same fid_coco sign flip)."""
    benchmarks = defaultdict(list)
    with open(BASE / "data" / "ai-benchmarks.csv") as f:
        for row in csv.DictReader(f):
            benchmarks[row["benchmark"]].append(
                (datetime.strptime(row["date"], "%Y-%m-%d"), float(row["score"])))

    def interp(series):
        series = sorted(series)
        out = {}
        for q in quarters:
            y, qn = int(q[:4]), int(q[-1])
            qdate = datetime(y, (qn - 1) * 3 + 2, 15)
            before = [(d, s) for d, s in series if d <= qdate]
            after = [(d, s) for d, s in series if d > qdate]
            if before and after:
                d0, s0 = before[-1]
                d1, s1 = after[0]
                frac = (qdate - d0).days / max((d1 - d0).days, 1)
                out[q] = s0 + frac * (s1 - s0)
            elif before:
                out[q] = before[-1][1]
            elif after:
                out[q] = after[0][1]
        return out

    cat_to_bench = {
        "coding": ["humaneval", "swe_bench"], "writing": ["alpaca_eval", "chatbot_arena"],
        "translation": ["wmt_bleu"], "design": ["fid_coco"], "marketing": ["alpaca_eval"],
        "audio": ["whisper_wer"],
    }
    out = {}
    for cat, bnames in cat_to_bench.items():
        sq = defaultdict(list)
        for bn in bnames:
            for q, s in interp(benchmarks.get(bn, [])).items():
                sq[q].append(s)
        if not sq:
            continue
        raw = {q: float(np.mean(v)) for q, v in sq.items()}
        mn, mx = min(raw.values()), max(raw.values())
        rng = mx - mn if mx > mn else 1
        if bnames == ["fid_coco"]:          # lower FID = better, so flip
            out[cat] = {q: (1 - (v - mn) / rng) * 100 for q, v in raw.items()}
        else:
            out[cat] = {q: ((v - mn) / rng) * 100 for q, v in raw.items()}
    return out


# =============================================================== run
hist_panel = tpd.build_panel_historical()

print("=" * 104)
print("CHAINED SERIES + ELASTICITY TABLE — do they survive in the paper? (D4)")
print("=" * 104)
print(f"\nall three series rebuilt on the SAME production panel, base {BASE_Q}=100")
print("panel gigs: " + ", ".join(f"{c}={len(hist_panel.get(c,{}))}" for c in CATS))

series = {}
for c in CATS:
    if not hist_panel.get(c):
        continue
    series[c] = {
        "as-built": chained_jevons(hist_panel[c], adjacent_only=False),
        "adjacent": chained_jevons(hist_panel[c], adjacent_only=True),
        "geks": geks_levels(hist_panel[c]),
    }

# ---------------------------------------------------------------- gap length
print("\n" + "=" * 104)
print("0. HOW OFTEN DOES THE DEFECT FIRE? — within-gig link span")
print("=" * 104)
print("a link spanning >1 quarter is one the as-built chain mis-books as a")
print("single-quarter change. TD1 measured 22-31%; re-measured here.\n")
print(f"{'cat':<12}{'links':>8}{'span=1':>9}{'span>1':>9}{'share >1':>10}{'max span':>10}")
for c in CATS:
    if not hist_panel.get(c):
        continue
    spans = []
    for qs in hist_panel[c].values():
        obs = sorted(qs, key=q_int)
        spans += [q_pos(b) - q_pos(a) for a, b in zip(obs, obs[1:])]
    if not spans:
        continue
    long = sum(1 for s in spans if s > 1)
    print(f"{c:<12}{len(spans):>8}{len(spans)-long:>9}{long:>9}"
          f"{100*long/len(spans):>9.1f}%{max(spans):>10}")

# ------------------------------------------------------- 1. decompose the gap
print("\n" + "=" * 104)
print("1. DECOMPOSING THE CHAINED-vs-GEKS GAP — how much is drift, how much is TD1?")
print("=" * 104)
print(f"levels at each category's terminal quarter, {BASE_Q}=100. 'defect' is the")
print("as-built/adjacent ratio; 'drift' is the adjacent/GEKS ratio.\n")
print(f"{'cat':<12}{'terminal':>9}{'as-built':>10}{'adjacent':>10}{'GEKS':>9}"
      f"{'defect x':>10}{'drift x':>9}{'defect share':>14}")
for c in CATS:
    S = series.get(c)
    if not S or not S["geks"]:
        continue
    common = set(S["as-built"]) & set(S["adjacent"]) & set(S["geks"])
    if not common:
        print(f"{c:<12}{'no common quarter':>40}")
        continue
    t = max(common, key=q_int)
    a, j, g = S["as-built"][t], S["adjacent"][t], S["geks"][t]
    defect, drift = a / j, j / g
    # share of the total log gap attributable to the defect
    tot = math.log(a / g)
    share = math.log(defect) / tot * 100 if abs(tot) > 1e-9 else float("nan")
    print(f"{c:<12}{t:>9}{a:>10.1f}{j:>10.1f}{g:>9.1f}"
          f"{defect:>10.2f}{drift:>9.2f}{share:>13.0f}%")
print("\n  'defect x' > 1 means the as-built chain overstates relative to the same")
print("  estimator with long links removed. 'drift x' > 1 is genuine chain drift.")
print("  'defect share' is the fraction of the total log gap the defect explains.")

print("\n  For the record — what step 12 actually ships (its own panel, base 2019Q1).")
print("  `panel-ipi.csv` is composite-only, so the per-category shipped chain is")
print("  read from `panel-category-indices.csv` and re-based here for comparison:")
shipped = tpd.read_index_csv(PILOT / "panel-category-indices.csv")
for c in CATS:
    s = shipped.get(c)
    if not s:
        print(f"    {c:<12} not in the shipped file")
        continue
    qs = sorted(s, key=q_int)
    b = s.get(BASE_Q)
    reb = f"{s[qs[-1]]/b*100:8.1f}" if b else f"{'-':>8}"
    mine = series.get(c, {}).get("as-built", {})
    mt = max(mine, key=q_int) if mine else None
    print(f"    {c:<12} {qs[0]}>{qs[-1]}  shipped level {s[qs[-1]]:>8.1f}   "
          f"re-based {BASE_Q}=100: {reb}   "
          f"reconstruction here: {(f'{mine[mt]:8.1f} @{mt}' if mt else '-')}")
print("  the two differ because step 12 builds its own panel and bases at 2019Q1;")
print("  the reconstruction isolates the ESTIMATOR on the production panel.")

# --------------------------------------------------- 2. spurious-regression tests
print("\n" + "=" * 104)
print("2. IS THE ELASTICITY REGRESSION SPURIOUS?")
print("=" * 104)
quarters_all = sorted({q for S in series.values() for q in S["geks"]}, key=q_int)
AI = ai_scores(quarters_all)

cpi = {}
with open(PILOT / "cpi-quarterly.csv") as f:
    for row in csv.DictReader(f):
        cpi[row["quarter"]] = float(row["cpi_sa"])

print("\nfitted on the AS-BUILT chained series, which is what the shipped table uses.")
print("DW near 2 = no serial correlation; DW below ~1 = the OLS SE is not usable.\n")
print(f"{'cat':<12}{'n':>4}{'beta(AI)':>10}{'t OLS':>8}{'t NW':>8}{'DW':>7}{'R2 AI':>8}"
      f"{'R2 time':>9}{'R2 CPI':>8}{'beta(CPI)':>11}{'d-diff t':>10}")
diag_rows = []
for c in CATS:
    S = series.get(c)
    if not S or c not in AI:
        continue
    idx = S["as-built"]
    common = sorted(set(idx) & set(AI[c]) & set(cpi), key=q_int)
    if len(common) < 6:
        continue
    lnP = np.log(np.array([idx[q] for q in common]))
    lnA = np.log(np.array([max(AI[c][q], 0.1) for q in common]) + 1)
    trend = np.arange(len(common), dtype=float)
    lnC = np.log(np.array([cpi[q] for q in common]))

    r_ai = bivariate(lnP, lnA)
    r_tr = bivariate(lnP, trend)
    r_cp = bivariate(lnP, lnC)
    d_ai = bivariate(np.diff(lnP), np.diff(lnA)) if len(common) > 3 else None

    diag_rows.append((c, r_ai, r_tr, r_cp, d_ai))
    dt = f"{d_ai['t_ols']:>9.2f}" if d_ai else f"{'-':>10}"
    print(f"{c:<12}{r_ai['n']:>4}{r_ai['slope']:>10.3f}{r_ai['t_ols']:>8.2f}"
          f"{r_ai['t_nw']:>8.2f}{r_ai['dw']:>7.2f}{r_ai['r2']:>8.3f}"
          f"{r_tr['r2']:>9.3f}{r_cp['r2']:>8.3f}{r_cp['slope']:>11.2f}{dt:>10}")

print("\n  READING:")
print("   * 'R2 time' is a placebo — a linear trend has no AI content whatever.")
print("     Where it matches or beats 'R2 AI', the AI score is proxying for time.")
print("   * 'R2 CPI' / 'beta(CPI)' is a second placebo. CPI-U does not measure AI.")
print("   * 't NW' is the OLS t corrected for serial correlation. The published")
print("     table's p-values use the uncorrected one.")
print("   * 'd-diff t' differences both sides. A common trend drops out; whatever")
print("     survives is a relationship between the CHANGES.")

# ------------------------------------------------------- 3. ranking stability
print("\n" + "=" * 104)
print("3. DOES THE RANKING SURVIVE A CHANGE OF PRICE SERIES?")
print("=" * 104)
print("the table is used to rank categories by AI exposure. Re-estimate the same")
print("regression on each of the three series and compare the orderings.\n")
print(f"{'cat':<12}{'as-built':>12}{'adjacent':>12}{'GEKS':>12}")
ranks = {}
for name in ("as-built", "adjacent", "geks"):
    vals = {}
    for c in CATS:
        S = series.get(c)
        if not S or c not in AI or not S[name]:
            continue
        common = sorted(set(S[name]) & set(AI[c]), key=q_int)
        if len(common) < 6:
            continue
        lnP = np.log(np.array([S[name][q] for q in common]))
        lnA = np.log(np.array([max(AI[c][q], 0.1) for q in common]) + 1)
        vals[c] = bivariate(lnP, lnA)["slope"]
    ranks[name] = vals
for c in CATS:
    cells = "".join(f"{ranks[n][c]:>12.3f}" if c in ranks[n] else f"{'-':>12}"
                    for n in ("as-built", "adjacent", "geks"))
    print(f"{c:<12}{cells}")

print()
for a, b in (("as-built", "adjacent"), ("as-built", "geks"), ("adjacent", "geks")):
    shared = sorted(set(ranks[a]) & set(ranks[b]))
    if len(shared) >= 3:
        rho, p = sp_stats.spearmanr([ranks[a][c] for c in shared],
                                    [ranks[b][c] for c in shared])
        print(f"  Spearman rank correlation  {a:<9} vs {b:<9} "
              f"rho = {rho:+.3f}  (p = {p:.3f}, n = {len(shared)})")

print("\n  ordering, most to least 'AI-elastic', under each series:")
for name in ("as-built", "adjacent", "geks"):
    order = sorted(ranks[name], key=lambda c: -ranks[name][c])
    print(f"    {name:<9} " + " > ".join(order))

# the shipped table is the thing the paper would actually print — compare to it
ship_el = {}
with open(PILOT / "panel-elasticity.csv") as f:
    for row in csv.DictReader(f):
        ship_el[row["category"]] = float(row["elasticity"])
print("\n  vs the SHIPPED table (`panel-elasticity.csv`, step 12's own panel, base")
print("  2019Q1, 8 categories) — the coefficients the paper currently quotes:")
print(f"    {'cat':<14}{'shipped':>10}{'here (as-built)':>18}{'change':>10}")
for c in sorted(ship_el, key=lambda k: -ship_el[k]):
    mine = ranks["as-built"].get(c)
    d = f"{mine-ship_el[c]:+9.3f}" if mine is not None else f"{'n/a':>10}"
    print(f"    {c:<14}{ship_el[c]:>10.3f}"
          f"{(f'{mine:18.3f}' if mine is not None else f'{chr(45):>18}')}{d}")
sh_order = [c for c in sorted(ship_el, key=lambda k: -ship_el[k])]
print(f"    shipped ordering: " + " > ".join(sh_order))
shared = sorted(set(ship_el) & set(ranks["as-built"]))
if len(shared) >= 3:
    rho, p = sp_stats.spearmanr([ship_el[c] for c in shared],
                                [ranks["as-built"][c] for c in shared])
    print(f"    Spearman shipped vs reconstruction: rho = {rho:+.3f} "
          f"(p = {p:.3f}, n = {len(shared)})")
    print("    -- the SAME estimator on the SAME platform, differing only in panel")
    print("       construction and base quarter.")

print("\n" + "=" * 104)
print("done")
print("=" * 104)
