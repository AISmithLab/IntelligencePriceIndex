#!/usr/bin/env python3
"""
Step 21: GEKS-Jevons category price indices — a drift-free index that uses NO
regression and NO fixed effects.

Motivation
----------
The chained-Jevons builders (12/14) compare each gig only to its *previous
observed* quarter, so a multi-quarter change lands entirely in the quarter a
sparsely-sampled gig reappears, and the errors compound along the chain (chain
drift). Step 19 fixes this with a time-product-dummy regression (gig fixed
effect + quarter effect).

GEKS fixes the same problem from the opposite direction. For every pair of
quarters (s,t) it forms the *direct* bilateral Jevons comparison over the gigs
observed in BOTH quarters, then makes those comparisons transitive by averaging
the direct route against every indirect route through a link quarter l:

    ln P_GEKS(s,t) = mean over links l of [ ln P(s,l) + ln P(l,t) ]

There is no chain to drift along and no gig fixed effect to estimate — the gig
level differences out inside each bilateral comparison. GEKS therefore corrects
drift while staying inside the same matched-model Jevons family as the headline
index, which makes it an independent check on step 19 rather than a variant of
it: the two share no estimation machinery, so agreement between them is
informative.

Panel construction is imported from 19-tpd-index.py, so the panel, category
assignment, gig->quarter median price and >=2-quarter filter are IDENTICAL to
both the TPD and (via 19's mirroring) the Jevons builders. Only the index
formula differs.

Standard errors are bootstrapped by resampling gigs within a category (the
bilateral means have no closed-form joint variance), giving the site's
confidence bands the same meaning as the TPD regression SEs.

Outputs (new files — the Jevons and TPD CSVs are left untouched):
  data/pilot/panel-category-indices-geks.csv      (historical, quarterly)
  data/pilot/recent-category-indices-geks.csv     (recent, quarterly)
  data/pilot/*-geks-se.csv                        (bootstrap SEs, log scale)
and prints a three-way comparison (Jevons vs TPD vs GEKS) plus a coverage
diagnostic for the bilateral comparison matrix.
"""

import csv
import importlib.util
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PILOT = BASE_DIR / "data" / "pilot"

# Import step 19 for its panel construction + splice/composite helpers, so this
# index is computed on exactly the same panel (module name starts with a digit,
# hence the explicit loader).
_spec = importlib.util.spec_from_file_location("tpd", Path(__file__).parent / "19-tpd-index.py")
tpd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tpd)

CATS = tpd.CATS
q_to_int = tpd.q_to_int

HIST_JEVONS = PILOT / "panel-category-indices.csv"
RECENT_JEVONS = PILOT / "recent-category-indices.csv"
HIST_TPD = PILOT / "panel-category-indices-tpd.csv"
RECENT_TPD = PILOT / "recent-category-indices-tpd.csv"
WEIGHTS_CSV = PILOT / "recent-category-weights.csv"

HIST_OUT = PILOT / "panel-category-indices-geks.csv"
RECENT_OUT = PILOT / "recent-category-indices-geks.csv"

MIN_MATCH = 3        # matched gigs required for a bilateral comparison to count
MIN_GIGS_PER_Q = tpd.MIN_GIGS_PER_Q   # a quarter needs >=3 distinct gigs (mirrors 19)
N_BOOT = 200
SEED = 7

# GEKS reaches quarter t from the base only when both base->l and l->t bilaterals
# are populated, so it needs a base quarter that is densely linked. The panels run
# back to 2011, where a category may have 2-4 gigs in its earliest quarter; using
# that as the base leaves most quarters unreachable (design produced an index for
# 2 of 39 quarters, audio 1 of 32). Estimating over the reported window instead --
# which is also the base period of the published index -- restores full coverage
# (design 23/23, audio 20/20). The pooled TPD regression does not need this because
# it identifies every quarter jointly on the largest connected component.
WINDOW_START = tpd.START_Q          # "2020Q1"


# ---- GEKS estimator ---------------------------------------------------------
def _log_panel(panel_cat, window_start=None):
    """{gig: {quarter: price}} -> ({quarter: {gig: ln price}}, [quarters]).

    Applies the same quarter-thickness filter as step 19 (>=3 distinct gigs),
    then drops gigs left with <2 observations (they inform no comparison)."""
    lo = q_to_int(window_start) if window_start else None
    qcount = Counter(q for qs in panel_cat.values() for q in qs
                     if lo is None or q_to_int(q) >= lo)
    good_q = {q for q, c in qcount.items() if c >= MIN_GIGS_PER_Q}

    kept = {}
    for g, qs in panel_cat.items():
        obs = {q: p for q, p in qs.items() if q in good_q and p > 0}
        if len(obs) >= 2:
            kept[g] = obs
    quarters = sorted({q for qs in kept.values() for q in qs}, key=q_to_int)
    by_q = {q: {g: math.log(p) for g, p in ((g, qs[q]) for g, qs in kept.items() if q in qs)}
            for q in quarters}
    return by_q, quarters


def _bilaterals(by_q, quarters):
    """Direct bilateral log-Jevons for every quarter pair with >=MIN_MATCH matched gigs.

    ln P(s,t) = mean over gigs in both s and t of (ln p_t - ln p_s). The gig's
    price *level* cancels inside the difference, which is what removes the need
    for a fixed effect."""
    lnP = {}
    for i, s in enumerate(quarters):
        for t in quarters[i + 1:]:
            common = by_q[s].keys() & by_q[t].keys()
            if len(common) >= MIN_MATCH:
                d = float(np.mean([by_q[t][g] - by_q[s][g] for g in common]))
                lnP[(s, t)] = d
                lnP[(t, s)] = -d
    for q in quarters:
        lnP[(q, q)] = 0.0
    return lnP


def _geks_levels(lnP, quarters, base):
    """ln P_GEKS(base,t) = mean over links l of [ln P(base,l) + ln P(l,t)].

    A quarter with no populated link path to the base is dropped rather than
    given a wrong level."""
    out = {}
    for t in quarters:
        vals = [lnP[(base, l)] + lnP[(l, t)]
                for l in quarters
                if (base, l) in lnP and (l, t) in lnP]
        if vals:
            out[t] = float(np.mean(vals))
        elif (base, t) in lnP:
            out[t] = lnP[(base, t)]      # fall back to the direct comparison
    return out


def geks_index(panel_cat, rng=None, n_boot=N_BOOT, window_start=WINDOW_START):
    """{gig: {quarter: price}} -> ({quarter: level}, {quarter: se}, diagnostics).

    Base quarter = earliest surviving quarter in the window, pinned to 100."""
    by_q, quarters = _log_panel(panel_cat, window_start)
    if len(quarters) < 2:
        return {}, {}, {}
    base = quarters[0]
    lnP = _bilaterals(by_q, quarters)
    ln_levels = _geks_levels(lnP, quarters, base)
    if base not in ln_levels:
        return {}, {}, {}
    idx = {q: 100.0 * math.exp(v - ln_levels[base]) for q, v in ln_levels.items()}

    # bilateral matrix density: the share of quarter pairs that have >=MIN_MATCH
    # matched gigs. Thin categories can leave this sparse, which is the main way
    # GEKS degrades relative to the pooled TPD regression.
    n_pairs = len(quarters) * (len(quarters) - 1) // 2
    filled = sum(1 for i, s in enumerate(quarters) for t in quarters[i + 1:] if (s, t) in lnP)
    diag = {
        "quarters_in": len(quarters),
        "quarters_out": len(idx),
        "gigs": len(panel_cat),
        "pair_density": filled / n_pairs if n_pairs else 0.0,
    }

    # bootstrap SEs: resample gigs with replacement, recompute, sd of ln level.
    se = {}
    if n_boot and rng is not None:
        gigs = sorted(panel_cat)
        draws = defaultdict(list)
        for _ in range(n_boot):
            pick = [gigs[i] for i in rng.integers(0, len(gigs), len(gigs))]
            # resampled gigs need distinct keys so duplicates count as separate gigs
            resampled = {(g, j): panel_cat[g] for j, g in enumerate(pick)}
            b_q, b_quarters = _log_panel(resampled, window_start)
            if len(b_quarters) < 2 or base not in b_quarters:
                continue
            b_ln = _geks_levels(_bilaterals(b_q, b_quarters), b_quarters, base)
            if base not in b_ln:
                continue
            for q, v in b_ln.items():
                draws[q].append(v - b_ln[base])
        for q in idx:
            vals = draws.get(q, [])
            se[q] = float(np.std(vals, ddof=1)) if len(vals) >= 2 else 0.0

    order = sorted(idx, key=q_to_int)
    return {q: idx[q] for q in order}, {q: se.get(q, 0.0) for q in order}, diag


def build_geks(panel_by_cat, rng):
    idx, se, diags = {}, {}, {}
    for cat in CATS:
        if panel_by_cat.get(cat):
            i, s, d = geks_index(panel_by_cat[cat], rng=rng)
            if i:
                idx[cat] = i
                se[cat] = s
                diags[cat] = d
    return idx, se, diags


def main():
    rng = np.random.default_rng(SEED)

    print("Building GEKS-Jevons indices (historical + recent panels)...")
    hist_panel = tpd.build_panel_historical()
    recent_panel = tpd.build_panel_recent()
    for tag, panel in (("historical", hist_panel), ("recent", recent_panel)):
        print(f"  {tag}: " + ", ".join(f"{c}={len(panel.get(c, {}))}" for c in CATS) + " panel gigs")

    hist_geks, hist_se, hist_diag = build_geks(hist_panel, rng)
    recent_geks, recent_se, recent_diag = build_geks(recent_panel, rng)

    tpd.write_index_csv(HIST_OUT, hist_geks)
    tpd.write_index_csv(RECENT_OUT, recent_geks)
    tpd.write_index_csv(HIST_OUT.with_name("panel-category-indices-geks-se.csv"), hist_se, fmt="{:.5f}")
    tpd.write_index_csv(RECENT_OUT.with_name("recent-category-indices-geks-se.csv"), recent_se, fmt="{:.5f}")
    print(f"\nWrote {HIST_OUT.name} and {RECENT_OUT.name} (+ *-se.csv bootstrap SEs)")

    print("\n=== BILATERAL COVERAGE (can GEKS identify each category?) ===")
    print(f"  {'cat':<12}{'panel':>7}{'q in':>6}{'q out':>7}{'pair fill':>11}   {'panel':>7}{'q in':>6}{'q out':>7}{'pair fill':>11}")
    print(f"  {'':<12}{'--- historical ---':^31}   {'--- recent ---':^31}")
    for c in CATS:
        h, r = hist_diag.get(c, {}), recent_diag.get(c, {})
        def fmt(d):
            if not d:
                return f"{'-':>7}{'-':>6}{'-':>7}{'-':>11}"
            return (f"{d['gigs']:7d}{d['quarters_in']:6d}{d['quarters_out']:7d}"
                    f"{d['pair_density']*100:10.0f}%")
        print(f"  {c:<12}{fmt(h)}   {fmt(r)}")

    weights = {}
    with open(WEIGHTS_CSV) as f:
        for row in csv.DictReader(f):
            weights[row["category"]] = float(row["weight"])

    j_cats, j_comp = tpd.spliced_composite(HIST_JEVONS, RECENT_JEVONS, weights)
    t_cats, t_comp = tpd.spliced_composite(HIST_TPD, RECENT_TPD, weights)
    g_cats, g_comp = tpd.spliced_composite(HIST_OUT, RECENT_OUT, weights)

    print("\n=== COMPOSITE (spliced, re-based 2020Q1=100) ===")
    print(f"  {'quarter':<9}{'Jevons':>9}{'TPD':>9}{'GEKS':>9}{'G vs T %':>10}")
    allq = sorted(set(j_comp) | set(t_comp) | set(g_comp), key=q_to_int)
    for q in allq:
        jv, tv, gv = j_comp.get(q), t_comp.get(q), g_comp.get(q)
        gt = f"{(gv/tv-1)*100:+8.1f}" if tv and gv else "       -"
        def s(x):
            return f"{x:8.1f}" if x else "       -"
        print(f"  {q:<9}{s(jv):>9}{s(tv):>9}{s(gv):>9}{gt:>10}")

    def full_change(c):
        return (c[allq[-1]] / c[allq[0]] - 1) * 100 if len(allq) > 1 and c.get(allq[0]) and c.get(allq[-1]) else float("nan")
    print(f"\n  Full-period composite change:  Jevons {full_change(j_comp):+.1f}%   "
          f"TPD {full_change(t_comp):+.1f}%   GEKS {full_change(g_comp):+.1f}%")
    print(f"  Composite jumpiness (mean |QoQ log change|, x100):  "
          f"Jevons {tpd.volatility(j_comp):.2f}   TPD {tpd.volatility(t_comp):.2f}   GEKS {tpd.volatility(g_comp):.2f}")

    # do the two drift-free methods agree? (the point of building GEKS at all)
    common = [q for q in allq if q in t_comp and q in g_comp]
    if len(common) > 2:
        a = np.array([t_comp[q] for q in common]); b = np.array([g_comp[q] for q in common])
        print(f"\n  TPD vs GEKS composite:  r={np.corrcoef(a, b)[0,1]:.3f}  "
              f"mean|diff|={np.mean(np.abs(a-b)):.1f} pts  max|diff|={np.max(np.abs(a-b)):.1f} pts")

    print("\n=== PER-CATEGORY final level (2020Q1=100) and jumpiness ===")
    print(f"  {'cat':<12}{'Jevons':>9}{'TPD':>8}{'GEKS':>8}   {'Jev jmp':>8}{'TPD jmp':>8}{'GEKS jmp':>9}")
    for c in CATS:
        js, ts, gs = j_cats.get(c, {}), t_cats.get(c, {}), g_cats.get(c, {})
        def last(s):
            return f"{s[max(s, key=q_to_int)]:8.1f}" if s else "       -"
        print(f"  {c:<12}{last(js):>9}{last(ts):>8}{last(gs):>8}   "
              f"{tpd.volatility(js):8.2f}{tpd.volatility(ts):8.2f}{tpd.volatility(gs):9.2f}")

    # mean bootstrap SE per category (log scale -> approximate +/-% band)
    print("\n=== GEKS bootstrap SE (mean over quarters, as +/-% band) ===")
    for c in CATS:
        vals = [v for v in list(hist_se.get(c, {}).values()) + list(recent_se.get(c, {}).values()) if v > 0]
        print(f"  {c:<12}{(f'{np.mean(vals)*100:6.1f}%' if vals else '     -')}")

    cmp = {
        "quarters": allq,
        "jevons_composite": [round(j_comp[q], 1) if j_comp.get(q) else None for q in allq],
        "tpd_composite": [round(t_comp[q], 1) if t_comp.get(q) else None for q in allq],
        "geks_composite": [round(g_comp[q], 1) if g_comp.get(q) else None for q in allq],
        "final": {c: {"jevons": (round(j_cats[c][max(j_cats[c], key=q_to_int)], 1) if j_cats.get(c) else None),
                      "tpd": (round(t_cats[c][max(t_cats[c], key=q_to_int)], 1) if t_cats.get(c) else None),
                      "geks": (round(g_cats[c][max(g_cats[c], key=q_to_int)], 1) if g_cats.get(c) else None)}
                  for c in CATS},
        "coverage": {c: {"historical": hist_diag.get(c, {}), "recent": recent_diag.get(c, {})} for c in CATS},
        "summary": {"jevons_change_pct": round(full_change(j_comp), 1),
                    "tpd_change_pct": round(full_change(t_comp), 1),
                    "geks_change_pct": round(full_change(g_comp), 1)},
    }
    out = BASE_DIR / "scratchpad" / "geks-vs-tpd-vs-jevons.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump(cmp, f)
    print(f"\nWrote comparison JSON -> {out}")


if __name__ == "__main__":
    main()
