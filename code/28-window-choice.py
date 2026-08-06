#!/usr/bin/env python3
"""Step 28: published-window choice — Phase 1 decision D3 of
`plans/active/publication.md`.

THE QUESTION. The published index starts at 2020Q1 because that is where
`19-tpd-index.py` pins START_Q, not because anything was measured. GEKS runs back
to 2018Q1, and the pre-AI placebo (2018Q3-2019Q4) is favourable: growth before
ChatGPT is nothing like growth after. Should the published window MOVE to 2018Q3,
or should the pre-period stay a robustness exhibit outside the headline series?

2018Q3 is a hard floor either way (checked 2026-08-03): the crawl has no captures
at all in 2017Q2, 2017Q4, 2018Q1 or 2018Q2, and the matched chain is severed there
-- 2017Q1->2017Q3 and 2017Q3->2018Q3 both have ZERO matched gigs.

WHAT THIS SCRIPT MEASURES. Four things, in the order that should decide it:

  1. INVARIANCE (the crux). GEKS levels come from averaging over every populated
     link path, so ADDING EARLIER QUARTERS CHANGES THE PATHS AVAILABLE TO LATER
     ONES. The published claim is a 2020Q1->2026Q1 change. If that number moves
     when quarters are prepended, then it was never a property of the data alone
     and the window is not a presentational choice. Measured directly as
     idx[terminal]/idx[2020Q1] under each window.
  2. COVERAGE. How many categories resolve a series at all from each start, and
     which base quarter the estimator actually lands on (it takes the earliest
     SURVIVING quarter in the window, which need not be the requested one).
  3. DENSITY. Matched gigs per adjacent quarter pair through the pre-period --
     the thinness that makes the placebo qualitative rather than precise.
  4. IDENTIFICATION. The D1c stress test applied to the extended window: re-run at
     MIN_MATCH=4 and see whether the added quarters rest on single link paths the
     way coding's historical terminal quarter does.

A fifth diagnostic falls out of the composite and is easy to miss: the basket
CHANGES SIZE across the pre-period as categories fail to resolve, so a composite
extended to 2018Q3 is not the same basket quarter to quarter. Category count per
quarter is printed alongside the level for exactly that reason.

Method: import 19-tpd-index.py and 21-geks-index.py UNMODIFIED, build both panels
once, and vary ONLY the `window_start` argument. build_geks's rng sequence is
replicated exactly (one default_rng(SEED) consumed over CATS in order) so every
window's bootstrap SEs are comparable to production, which runs from 2020Q1. The
recent panel has no observations before 2024Q3, so it is built once and reused.

Measurement only -- writes nothing outside scratchpad/.

Run:  python3 code/28-window-choice.py
"""
import csv
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np

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

WINDOWS = ["2018Q1", "2018Q3", "2019Q1", "2019Q3", "2020Q1"]
PROD_W = "2020Q1"
PIVOT = "2020Q1"          # the quarter every window has in common
CHATGPT_Q = "2022Q4"


def q_int(q):
    return tpd.q_to_int(q)


def hw(se_val):
    """1.96 sd on the log level -> +/-% half width."""
    return (math.exp(1.96 * se_val) - 1) * 100


# ---------------------------------------------------------------- inputs
weights = {}
with open(tpd.WEIGHTS_CSV) as f:
    for row in csv.DictReader(f):
        weights[row["category"]] = float(row["weight"])

cpi = {}
with open(PILOT / "cpi-quarterly.csv") as f:
    for row in csv.DictReader(f):
        cpi[row["quarter"]] = float(row["cpi_sa"])

hist_panel = tpd.build_panel_historical()
recent_panel = tpd.build_panel_recent()

print("=" * 104)
print("PUBLISHED-WINDOW CHOICE — GEKS-Jevons, historical segment (D3)")
print("=" * 104)
print("\npanel gigs   historical: " + ", ".join(f"{c}={len(hist_panel.get(c,{}))}" for c in CATS))
print("panel gigs   recent:     " + ", ".join(f"{c}={len(recent_panel.get(c,{}))}" for c in CATS))
print(f"\nproduction window starts {PROD_W}; MIN_MATCH={geks.MIN_MATCH}, "
      f"N_BOOT={geks.N_BOOT}, SEED={geks.SEED}")


def run_segment(panel, window_start, min_match=None):
    """Replicate build_geks exactly: one rng, CATS in order, only the window varies."""
    old_k = geks.MIN_MATCH
    if min_match is not None:
        geks.MIN_MATCH = min_match
    rng = np.random.default_rng(geks.SEED)
    idx, se, diag = {}, {}, {}
    for cat in CATS:
        if panel.get(cat):
            i, s, d = geks.geks_index(panel[cat], rng=rng, window_start=window_start)
            if i:
                idx[cat], se[cat], diag[cat] = i, s, d
    geks.MIN_MATCH = old_k
    return idx, se, diag


# the recent panel starts at 2024Q3, so its index cannot depend on the window
recent_idx, recent_se, recent_diag = run_segment(recent_panel, PROD_W)

results = {}
for w in WINDOWS:
    h_idx, h_se, h_diag = run_segment(hist_panel, w)
    results[w] = dict(idx=h_idx, se=h_se, diag=h_diag)


# ---- run-time check: the production window reproduces the shipped CSV ---------
shipped = tpd.read_index_csv(PILOT / "panel-category-indices-geks.csv")
worst = 0.0
for c in CATS:
    a, b = results[PROD_W]["idx"].get(c, {}), shipped.get(c, {})
    for q in set(a) & set(b):
        worst = max(worst, abs(a[q] - b[q]))
print(f"\ncheck: window={PROD_W} reproduces panel-category-indices-geks.csv to "
      f"{worst:.3f} index points (max over all cells) -- "
      f"{'OK' if worst < 0.01 else 'MISMATCH'}")


# ---------------------------------------------------------------- 1. coverage
print("\n" + "=" * 104)
print("1. COVERAGE — which categories resolve, and from which base quarter")
print("=" * 104)
print("the estimator bases on the earliest SURVIVING quarter in the window, which")
print("is not always the one requested (a quarter needs >=3 distinct gigs to exist)\n")
print(f"{'cat':<12}{'window':>9} {'base':>8} {'qout/qin':>10} {'pairfill':>9} "
      f"{'terminal':>10} {'level':>9} {'+/-95%':>9}")
for cat in CATS:
    for w in WINDOWS:
        R = results[w]
        idx, se, diag = R["idx"].get(cat), R["se"].get(cat), R["diag"].get(cat)
        if not idx:
            print(f"{cat:<12}{w:>9} {'NO INDEX':>8}")
            continue
        qs = sorted(idx, key=q_int)
        base_q, term_q = qs[0], qs[-1]
        star = " <-- prod" if w == PROD_W else ""
        # a single surviving quarter is 100.0 by construction: zero SE is
        # degeneracy, not precision (same trap as the step 26 sweep)
        band = f"{hw(se[term_q]):8.1f}%" if diag["quarters_out"] > 1 else f"{'DEGEN':>9}"
        print(f"{cat:<12}{w:>9} {base_q:>8} "
              f"{diag['quarters_out']:>4}/{diag['quarters_in']:<5} "
              f"{diag['pair_density']*100:>8.0f}% {term_q:>10} {idx[term_q]:>9.1f} "
              f"{band:>9}{star}")
    print()


# ------------------------------------------------------- 2. THE INVARIANCE TEST
print("=" * 104)
print(f"2. INVARIANCE — does prepending quarters move the PUBLISHED {PIVOT}->terminal change?")
print("=" * 104)
print("levels are deterministic (no rng), so any movement here is the estimator,")
print("not sampling noise. A window-invariant index would show a flat 'growth' column.\n")
print(f"{'cat':<12}{'window':>9} {'terminal':>10} {'growth %':>11} {'vs prod':>10} "
      f"{'+/-95% at term':>16}")
invariance = {}
for cat in CATS:
    prod = results[PROD_W]["idx"].get(cat, {})
    prod_g = None
    if prod and PIVOT in prod:
        pt = sorted(prod, key=q_int)[-1]
        prod_g = prod[pt] / prod[PIVOT]
    rows = []
    for w in WINDOWS:
        idx = results[w]["idx"].get(cat, {})
        if not idx or PIVOT not in idx:
            print(f"{cat:<12}{w:>9} {'-':>10} {'PIVOT ABSENT':>11}")
            continue
        qs = sorted(idx, key=q_int)
        term_q = qs[-1]
        g = idx[term_q] / idx[PIVOT]
        se_t = results[w]["se"][cat].get(term_q, 0.0)
        vs = f"{(g/prod_g-1)*100:+9.1f}%" if prod_g else "        -"
        mark = "!" if (prod and term_q != sorted(prod, key=q_int)[-1]) else " "
        star = " <-- prod" if w == PROD_W else ""
        print(f"{cat:<12}{w:>9} {term_q:>9}{mark} {(g-1)*100:>10.1f}% {vs:>10} "
              f"{hw(se_t):>15.1f}%{star}")
        rows.append((w, g))
    invariance[cat] = rows
    print()
print("  '!' = terminal quarter differs from production's, so the growth column")
print("        spans a different span and the 'vs prod' delta is not clean.")

print("\n  SPREAD of the growth figure across windows (max/min - 1), per category:")
for cat in CATS:
    rows = invariance.get(cat, [])
    if len(rows) < 2:
        print(f"    {cat:<12} -")
        continue
    gs = [g for _, g in rows]
    print(f"    {cat:<12}{(max(gs)/min(gs)-1)*100:>8.1f}%   "
          f"({min(gs)-1:+.1%} to {max(gs)-1:+.1%})")


# ---------------------------------------------------------------- 3. density
print("\n" + "=" * 104)
print("3. DENSITY — matched gigs per ADJACENT quarter pair, through the pre-period")
print("=" * 104)
print(f"a pair below MIN_MATCH={geks.MIN_MATCH} contributes no bilateral at all.")
print("counted on the 2018Q1-window panel so every quarter that can exist is shown.\n")
pre_quarters = []
by_cat_pairs = {}
for cat in CATS:
    if not hist_panel.get(cat):
        continue
    by_q, quarters = geks._log_panel(hist_panel[cat], "2018Q1")
    pairs = {}
    for a, b in zip(quarters, quarters[1:]):
        pairs[(a, b)] = len(by_q[a].keys() & by_q[b].keys())
    by_cat_pairs[cat] = pairs
    for q in quarters:
        if q not in pre_quarters and q_int(q) <= q_int("2020Q4"):
            pre_quarters.append(q)
pre_quarters.sort(key=q_int)
adj = list(zip(pre_quarters, pre_quarters[1:]))
print(f"{'cat':<12}" + "".join("{:>9}".format(a[2:] + ">" + b[2:]) for a, b in adj))
for cat in CATS:
    pairs = by_cat_pairs.get(cat, {})
    cells = []
    for pr in adj:
        n = pairs.get(pr)
        cells.append("     -" + "   " if n is None else f"{n:>6}" + ("*  " if n < geks.MIN_MATCH else "   "))
    print(f"{cat:<12}" + "".join(cells))
print("\n  '-' = the pair does not exist in this category's filtered panel")
print(f"  '*' = below MIN_MATCH={geks.MIN_MATCH}: no bilateral, so GEKS must route around it")


# ---------------------------------------------------------------- 4. placebo
print("\n" + "=" * 104)
print("4. PLACEBO — pre-ChatGPT vs post-ChatGPT annualised growth, on the 2018Q3 window")
print("=" * 104)
print(f"pre  = base -> {CHATGPT_Q};  post = {CHATGPT_Q} -> terminal.")
print("both legs come from the SAME series, so the comparison does not splice.\n")
print(f"{'cat':<12}{'base':>8} {'pre span':>10} {'pre %/yr':>10} "
      f"{'post span':>11} {'post %/yr':>11}")


def annualised(idx, a, b):
    if a not in idx or b not in idx or idx[a] <= 0:
        return None
    yrs = (q_int(b) - q_int(a)) // 10 + ((q_int(b) % 10) - (q_int(a) % 10)) / 4.0
    if yrs <= 0:
        return None
    return ((idx[b] / idx[a]) ** (1 / yrs) - 1) * 100


for cat in CATS:
    idx = results["2018Q3"]["idx"].get(cat, {})
    if not idx:
        print(f"{cat:<12}{'NO INDEX':>8}")
        continue
    qs = sorted(idx, key=q_int)
    base_q, term_q = qs[0], qs[-1]
    cut = min((q for q in qs if q_int(q) >= q_int(CHATGPT_Q)), key=q_int, default=None)
    if cut is None or cut == base_q:
        print(f"{cat:<12}{base_q:>8} {'no post-period split':>32}")
        continue
    pre = annualised(idx, base_q, cut)
    post = annualised(idx, cut, term_q)
    pre_s = "{:9.1f}%".format(pre) if pre is not None else "{:>10}".format("-")
    post_s = "{:10.1f}%".format(post) if post is not None else "{:>11}".format("-")
    print("{:<12}{:>8} {:>10} {} {:>11} {}".format(
        cat, base_q, base_q + ">" + cut, pre_s, cut + ">" + term_q, post_s))


# ---------------------------------------------------------------- 5. composite
print("\n" + "=" * 104)
print("5. COMPOSITE — the headline under each window")
print("=" * 104)


def chain_rebase(cat, hist, recent, base_q):
    """tpd.chain_category with the re-base quarter parameterised.

    Verified against tpd.chain_category at base_q=START_Q at run time below."""
    h, r = hist.get(cat, {}), recent.get(cat, {})
    chained = {}
    common = sorted((set(h) & set(r)), key=q_int)
    if common:
        link = common[0]
        link_level = h[link]
        for q, v in h.items():
            if q_int(q) < q_int(link):
                chained[q] = v
        for q, v in r.items():
            chained[q] = link_level * v / r[link]
    elif r:
        chained = dict(r)
    elif h:
        chained = dict(h)
    else:
        return {}
    base = chained.get(base_q)
    if not base:
        return {}
    return {q: 100.0 * v / base for q, v in chained.items()}


# run-time check that the local re-baser is the production one at START_Q
mism = 0.0
for c in CATS:
    a = chain_rebase(c, results[PROD_W]["idx"], recent_idx, tpd.START_Q)
    b = tpd.chain_category(c, results[PROD_W]["idx"], recent_idx)
    for q in set(a) & set(b):
        mism = max(mism, abs(a[q] - b[q]))
    if set(a) ^ set(b):
        mism = float("inf")
print(f"\ncheck: chain_rebase(base={tpd.START_Q}) == tpd.chain_category to "
      f"{mism:.4f} pts -- {'OK' if mism < 1e-6 else 'MISMATCH'}")


def composite_series(hist_idx, base_q, floor_q):
    chained = {c: chain_rebase(c, hist_idx, recent_idx, base_q) for c in CATS}
    chained = {c: s for c, s in chained.items() if s}
    qs = sorted({q for s in chained.values() for q in s}, key=q_int)
    qs = [q for q in qs if q_int(q) >= q_int(floor_q)]
    out, ncat = {}, {}
    for q in qs:
        v = tpd.composite_at(chained, weights, q)
        if v is not None:
            out[q] = v
            ncat[q] = sum(1 for s in chained.values() if s.get(q))
    return out, ncat, chained


print(f"\n5a. re-based at {PIVOT} (production convention) — does the headline move?\n")
print(f"{'window':>9} {'cats':>6} {'quarters':>10} {'2026Q1':>9} "
      f"{'nominal delta':>15} {'real delta':>12}")
for w in WINDOWS:
    comp, ncat, chained = composite_series(results[w]["idx"], PIVOT, PIVOT)
    if not comp:
        print(f"{w:>9}  NO COMPOSITE")
        continue
    qs = sorted(comp, key=q_int)
    a, b = qs[0], qs[-1]
    nom = (comp[b] / comp[a] - 1) * 100
    real = ((comp[b] / cpi[b]) / (comp[a] / cpi[a]) - 1) * 100 if a in cpi and b in cpi else float("nan")
    star = " <-- prod" if w == PROD_W else ""
    print(f"{w:>9} {len(chained):>6} {len(qs):>4} {a}>{b} {comp[b]:>9.1f} "
          f"{nom:>14.1f}% {real:>11.1f}%{star}")

print(f"\n5b. the 2018Q3-based series — what MOVING the window would publish\n")
comp18, ncat18, chained18 = composite_series(results["2018Q3"]["idx"], "2018Q3", "2018Q3")
if comp18:
    print(f"{'quarter':<9}{'composite':>11}{'real':>10}{'cats in basket':>16}")
    base_cpi = cpi.get("2018Q3")
    for q in sorted(comp18, key=q_int):
        r = 100.0 * (comp18[q] / cpi[q]) / (comp18["2018Q3"] / base_cpi) if q in cpi else float("nan")
        flag = "  <-- basket changes" if ncat18[q] != ncat18.get(sorted(comp18, key=q_int)[0]) else ""
        print(f"{q:<9}{comp18[q]:>11.1f}{r:>10.1f}{ncat18[q]:>10} of {len(chained18)}{flag}")
    qs = sorted(comp18, key=q_int)
    print(f"\n  2018Q3->{qs[-1]}: nominal {(comp18[qs[-1]]/comp18[qs[0]]-1)*100:+.1f}%")
    if PIVOT in comp18:
        print(f"  2018Q3->{PIVOT} (the pre-AI leg alone): "
              f"nominal {(comp18[PIVOT]/comp18['2018Q3']-1)*100:+.1f}%, "
              f"real {((comp18[PIVOT]/cpi[PIVOT])/(comp18['2018Q3']/cpi['2018Q3'])-1)*100:+.1f}%")
else:
    print("  NO COMPOSITE resolves from 2018Q3")


# ------------------------------------------------- 6. identification stress test
print("\n" + "=" * 104)
print("6. IDENTIFICATION STRESS (the D1c test applied to the extended window)")
print("=" * 104)
print("re-run each window at MIN_MATCH=4. A level that swings far outside its own")
print("stated band on a one-step change in a robustness knob is NOT IDENTIFIED --")
print("a confidence band does not express that, so it must not be published as one.\n")
print(f"{'cat':<12}{'window':>9} {'k=3 term':>12} {'k=4 term':>12} {'swing':>10} "
      f"{'k=3 +/-95%':>12} {'verdict':>18}")
# hoisted: one k=4 run per window, not one per (category, window) cell
k4_by_w = {w: run_segment(hist_panel, w, min_match=4)[0] for w in ("2018Q3", PROD_W)}
for cat in CATS:
    for w in ("2018Q3", PROD_W):
        i3 = results[w]["idx"].get(cat, {})
        i4 = k4_by_w[w].get(cat, {})
        if not i3:
            print(f"{cat:<12}{w:>9} {'NO INDEX':>12}")
            continue
        t3 = sorted(i3, key=q_int)[-1]
        band = hw(results[w]["se"][cat].get(t3, 0.0))
        if not i4:
            print(f"{cat:<12}{w:>9} {i3[t3]:>7.1f}@{t3[2:]:<4} {'NO INDEX':>12} "
                  f"{'-':>10} {band:>11.1f}% {'NOT IDENTIFIED':>18}")
            continue
        t4 = sorted(i4, key=q_int)[-1]
        if t4 != t3:
            note = f"terminal moved {t3}>{t4}"
            print(f"{cat:<12}{w:>9} {i3[t3]:>7.1f}@{t3[2:]:<4} {i4[t4]:>7.1f}@{t4[2:]:<4} "
                  f"{'n/a':>10} {band:>11.1f}% {note:>18}")
            continue
        swing = (i4[t4] / i3[t3] - 1) * 100
        verdict = "NOT IDENTIFIED" if abs(swing) > band else "within band"
        print(f"{cat:<12}{w:>9} {i3[t3]:>7.1f}@{t3[2:]:<4} {i4[t4]:>7.1f}@{t4[2:]:<4} "
              f"{swing:>9.1f}% {band:>11.1f}% {verdict:>18}")
    print()

# --------------------------------------------- 7. WHY invariance fails (mechanism)
print("=" * 104)
print("7. MECHANISM — why the 2020Q1->terminal growth moves at all")
print("=" * 104)
print("""GEKS sets ln P(base,t) = mean over link quarters l of [lnP(base,l) + lnP(l,t)],
where l ranges over quarters for which BOTH legs are populated. Growth from the
pivot to t is therefore

    mean_{l in L_t}[lnP(base,l) + lnP(l,t)] - mean_{l in L_p}[lnP(base,l) + lnP(l,p)]

and the lnP(base,l) terms cancel only if L_t == L_p. Prepending quarters changes
the available l's, so growth is window-dependent BY CONSTRUCTION. There is a
second, separate channel: _log_panel keeps a gig only if it has >=2 observations
INSIDE the window, so widening the window also changes the GIG SET, which moves
the bilaterals themselves. This section separates the two.

  channel (a) gig set  -> the bilaterals lnP(l,t) differ between windows
  channel (b) link set -> the same bilaterals are averaged over different l's

g* below re-computes growth on the link quarters BOTH windows share, with the
base term cancelled algebraically. If g* agrees across windows, the movement is
channel (b) alone; if g* also moves, channel (a) is contributing.\n""")

WA, WB = "2018Q3", PROD_W
print(f"{'cat':<12}{'terminal':>9} {'gigs A/B':>11} {'shared bilat':>13} "
      f"{'max|dlnP|':>10} {'|L*|':>6} {'g(A)':>9} {'g(B)':>9} {'g*(A)':>9} {'g*(B)':>9}")
for cat in CATS:
    if not hist_panel.get(cat):
        continue
    prod_idx = results[PROD_W]["idx"].get(cat, {})
    if not prod_idx or PIVOT not in prod_idx:
        print(f"{cat:<12}{'-':>9}  pivot absent")
        continue
    term = sorted(prod_idx, key=q_int)[-1]

    built = {}
    for w in (WA, WB):
        by_q, quarters = geks._log_panel(hist_panel[cat], w)
        lnP = geks._bilaterals(by_q, quarters)
        base = quarters[0]
        L_t = [l for l in quarters if (base, l) in lnP and (l, term) in lnP]
        L_p = [l for l in quarters if (base, l) in lnP and (l, PIVOT) in lnP]
        built[w] = dict(by_q=by_q, quarters=quarters, lnP=lnP, base=base,
                        L_t=set(L_t), L_p=set(L_p),
                        ngig=len({g for d in by_q.values() for g in d}))

    A, B = built[WA], built[WB]
    # channel (a): do the shared bilaterals themselves differ?
    shared = set(A["lnP"]) & set(B["lnP"])
    dmax = max((abs(A["lnP"][k] - B["lnP"][k]) for k in shared), default=0.0)
    # channel (b): fix the link set to what both windows can average over
    Lstar = A["L_t"] & A["L_p"] & B["L_t"] & B["L_p"]
    def gstar(D):
        if not Lstar:
            return None
        return (float(np.mean([D["lnP"][(l, term)] for l in Lstar]))
                - float(np.mean([D["lnP"][(l, PIVOT)] for l in Lstar])))
    gA = math.log(results[WA]["idx"][cat][term] / results[WA]["idx"][cat][PIVOT]) \
        if term in results[WA]["idx"].get(cat, {}) and PIVOT in results[WA]["idx"].get(cat, {}) else None
    gB = math.log(prod_idx[term] / prod_idx[PIVOT])
    sA, sB = gstar(A), gstar(B)
    def pc(x):
        return "{:8.1f}%".format((math.exp(x) - 1) * 100) if x is not None else "{:>9}".format("-")
    print(f"{cat:<12}{term:>9} {A['ngig']:>5}/{B['ngig']:<5} "
          f"{len(shared)//2:>13} {dmax:>10.4f} {len(Lstar):>6} "
          f"{pc(gA):>9} {pc(gB):>9} {pc(sA):>9} {pc(sB):>9}")
print(f"\n  A = window {WA},  B = window {WB} (production)")
print("  g  = the published growth, pivot -> terminal, as the index reports it")
print("  g* = the same growth recomputed on the shared link set L*, base cancelled")
print("  max|dlnP| = largest gap between the two windows' shared bilaterals (channel a)")

# the 2019Q1 window looked pathological in tables 1-2; check whether the cause is
# a spike in the quarter it bases on
print("\n  2019Q1 as a BASE — levels around it on the 2018Q3 window (index, base 2018Q3=100):")
print(f"    {'cat':<12}" + "".join(f"{q:>10}" for q in ("2018Q4", "2019Q1", "2019Q2")))
for cat in CATS:
    idx = results["2018Q3"]["idx"].get(cat, {})
    if not idx:
        continue
    cells = "".join(f"{idx[q]:>10.1f}" if q in idx else f"{'-':>10}"
                    for q in ("2018Q4", "2019Q1", "2019Q2"))
    print(f"    {cat:<12}{cells}")
print("    a quarter that sits above its neighbours makes a LOW base: every later")
print("    level is divided by it, which is why the 2019Q1 window reports the")
print("    smallest growth for design, video and writing in table 2.")

print("=" * 104)
print("done")
print("=" * 104)
