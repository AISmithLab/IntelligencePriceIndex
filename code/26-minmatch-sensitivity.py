#!/usr/bin/env python3
"""Step 26: MIN_MATCH sensitivity sweep — the measurement behind Phase 1 decision
D1 (`plans/active/publication.md`) and the table `tests/method.test.md` R5 asks for.

MIN_MATCH is the number of matched gigs a quarter pair must share before its
bilateral log-Jevons comparison is admitted to the GEKS matrix. It is currently 3.
Raising it is usually argued as "buy precision with coverage". This script tests
that trade-off instead of assuming it.

HEADLINE: THE TRADE-OFF DOES NOT EXIST IN THAT FORM. Raising MIN_MATCH buys no
precision in any category, and in the thin ones it destroys precision:

  recent segment, +/-95% on the terminal level
  audio        k=1 +/-11.3%  ->  k=3 +/-16.0%  ->  k=6 +/-34.1%   (strictly WORSE)
  design/marketing/writing/coding/video   flat to within 0.2pp across k=1..10

The reason is mechanical and is the point worth carrying into the paper: MIN_MATCH
does not add matched gigs to a comparison, it DELETES comparisons. GEKS averages
a quarter's level over every populated link path; dropping links shrinks the
average's support. In the limit it collapses to one link and the "index" is a
single bilateral. That is what produces the coding spike below.

CODING HISTORICAL, DIAGNOSED (levels are deterministic — no rng — so this is the
estimator, not the bootstrap):
  k=3  2025Q1 = 312.8, supported by 8 link paths
  k=4  2025Q1 = 717.7, supported by 1 link path (2022Q1, the most extreme, +1.97)
  k=5  terminal quarter falls back to 2024Q4 = 220.0, 17 link paths
The direct 2020Q1->2025Q1 bilateral carries ONE matched gig, so it is never used
at any k. A +129% swing from a one-step change in a robustness knob is far outside
coding's own stated band (+/-61%), and it means the historical coding level is not
identified rather than merely imprecise.

TWO READING CAVEATS, both live in the output below:
  1. The terminal quarter CHANGES with k as quarters drop out (coding 2025Q1 at
     k=3-4 but 2024Q4 at k>=5; audio 7/7 quarters at k<=6 but 4/7 at k>=8). The
     "vs k=3 level" column is only an apples-to-apples comparison where qout/qin
     is unchanged; where it is not, the column compares different quarters and is
     marked with '!'.
  2. Cells reporting +/-0.0% are DEGENERATE, not precise: only the base quarter
     survived, so the index is 100.0 by construction with nothing to vary
     (translation k=8,10; audio k=10 historical). Same failure mode as the n=full
     row of the 2026-08-05 precision curve.

Method: import 19-tpd-index.py and 21-geks-index.py UNMODIFIED, build both panels
once, then vary ONLY geks.MIN_MATCH. build_geks's rng sequence is replicated
exactly (one default_rng(SEED) consumed over CATS in order) so each sweep value is
comparable to production, which runs at k=3.

Run:  python3 code/26-minmatch-sensitivity.py
"""
import importlib.util, math, sys
from pathlib import Path
import numpy as np

BASE = Path("/home/exouser/IntelligencePriceIndex")
sys.path.insert(0, str(BASE / "code"))


def load(name, fn):
    spec = importlib.util.spec_from_file_location(name, BASE / "code" / fn)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


tpd = load("tpd", "19-tpd-index.py")
geks = load("geks", "21-geks-index.py")
CATS = tpd.CATS
KS = [1, 2, 3, 4, 5, 6, 8, 10]
PROD_K = 3

import csv
weights = {}
with open(tpd.WEIGHTS_CSV) as f:
    for row in csv.DictReader(f):
        weights[row["category"]] = float(row["weight"])

hist_panel = tpd.build_panel_historical()
recent_panel = tpd.build_panel_recent()

print("=" * 100)
print("MIN_MATCH SENSITIVITY SWEEP — GEKS-Jevons")
print("=" * 100)
print(f"\npanel gigs   historical: " + ", ".join(f"{c}={len(hist_panel.get(c,{}))}" for c in CATS))
print(f"panel gigs   recent:     " + ", ".join(f"{c}={len(recent_panel.get(c,{}))}" for c in CATS))
print(f"\nproduction value is MIN_MATCH={PROD_K}; N_BOOT={geks.N_BOOT}, SEED={geks.SEED}")


def run_segment(panel, k):
    """Replicate build_geks exactly: one rng, CATS in order."""
    geks.MIN_MATCH = k
    rng = np.random.default_rng(geks.SEED)
    idx, se, diag = {}, {}, {}
    for cat in CATS:
        if panel.get(cat):
            i, s, d = geks.geks_index(panel[cat], rng=rng)
            if i:
                idx[cat], se[cat], diag[cat] = i, s, d
    return idx, se, diag


results = {}
for k in KS:
    h_idx, h_se, h_diag = run_segment(hist_panel, k)
    r_idx, r_se, r_diag = run_segment(recent_panel, k)
    chained = {c: tpd.chain_category(c, h_idx, r_idx) for c in CATS}
    chained = {c: s for c, s in chained.items() if s}
    qs = sorted({q for s in chained.values() for q in s}, key=tpd.q_to_int)
    qs = [q for q in qs if tpd.q_to_int(q) >= tpd.q_to_int(tpd.START_Q)]
    comp = {q: tpd.composite_at(chained, weights, q) for q in qs}
    comp = {q: v for q, v in comp.items() if v is not None}
    results[k] = dict(h_idx=h_idx, h_se=h_se, h_diag=h_diag,
                      r_idx=r_idx, r_se=r_se, r_diag=r_diag,
                      chained=chained, comp=comp)
geks.MIN_MATCH = PROD_K


def hw(se_val):
    """1.96 sd on ln level -> symmetric-ish % half width."""
    return (math.exp(1.96 * se_val) - 1) * 100


# ---------------------------------------------------------------- per segment
for tag, ikey, sekey, dkey in (("RECENT (2024Q3=100, terminal 2026Q1)", "r_idx", "r_se", "r_diag"),
                               ("HISTORICAL (2020Q1=100, terminal 2024Q3)", "h_idx", "h_se", "h_diag")):
    print("\n" + "=" * 100)
    print(tag)
    print("=" * 100)
    print(f"{'cat':<12}{'k':>3} {'gigs':>6} {'qout/qin':>10} {'pairfill':>9} "
          f"{'terminal':>10} {'+/-95%':>9}   {'vs k=3 level':>13}")
    for cat in CATS:
        base_idx = results[PROD_K][ikey].get(cat, {})
        base_term_q = base_term = None
        if base_idx:
            base_term_q = sorted(base_idx, key=tpd.q_to_int)[-1]
            base_term = base_idx[base_term_q]
        for k in KS:
            R = results[k]
            idx, se, diag = R[ikey].get(cat), R[sekey].get(cat), R[dkey].get(cat)
            if not idx:
                print(f"{cat:<12}{k:>3} {'-':>6} {'NO INDEX':>10}")
                continue
            term_q = sorted(idx, key=tpd.q_to_int)[-1]
            lvl, h = idx[term_q], hw(se[term_q])
            # '!' = the terminal quarter moved, so this is not the same comparison
            mark = "!" if (base_term_q and term_q != base_term_q) else " "
            delta = f"{(lvl/base_term-1)*100:+.1f}%{mark}" if base_term else "-"
            # +/-0.0% with a single surviving quarter is degeneracy, not precision
            hs = f"{h:>8.1f}%" if diag["quarters_out"] > 1 else f"{'DEGEN':>9}"
            star = " <-- prod" if k == PROD_K else ""
            print(f"{cat:<12}{k:>3} {diag['gigs']:>6} "
                  f"{diag['quarters_out']:>4}/{diag['quarters_in']:<5} "
                  f"{diag['pair_density']*100:>8.0f}% {lvl:>10.1f} {hs} {delta:>13}{star}")
        print()
    print("  '!' = terminal quarter differs from the k=3 one, so the level column")
    print("        compares different quarters and is not an apples-to-apples delta.")
    print("  'DEGEN' = only the base quarter survived; the index is 100.0 by")
    print("        construction and its zero SE is degeneracy, not precision.")

# ---------------------------------------------------------------- composite
print("=" * 100)
print("SPLICED COMPOSITE (2020Q1=100, review-weighted) — the headline")
print("=" * 100)
print(f"{'k':>3} {'quarters':>9} {'cats in':>8} {'2026Q1':>9} {'full-window delta':>19}")
for k in KS:
    comp = results[k]["comp"]
    if not comp:
        print(f"{k:>3}  NO COMPOSITE")
        continue
    last = sorted(comp, key=tpd.q_to_int)[-1]
    star = "  <-- prod" if k == PROD_K else ""
    print(f"{k:>3} {len(comp):>9} {len(results[k]['chained']):>8} "
          f"{comp[last]:>9.1f} {(comp[last]/100-1)*100:>18.1f}%{star}   (terminal {last})")

# ---------------------------------------------------------------- the question
print("\n" + "=" * 100)
print("DOES RAISING MIN_MATCH BUY PRECISION? (recent segment, terminal quarter)")
print("=" * 100)
print(f"{'cat':<12}" + "".join(f"{'k='+str(k):>9}" for k in KS))
print(f"{'':<12}" + "".join(f"{'':>9}" for k in KS))
for cat in CATS:
    cells = []
    for k in KS:
        idx, se = results[k]["r_idx"].get(cat), results[k]["r_se"].get(cat)
        if not idx:
            cells.append(f"{'--':>9}")
            continue
        tq = sorted(idx, key=tpd.q_to_int)[-1]
        cells.append(f"{hw(se[tq]):>8.1f}%")
    print(f"{cat:<12}" + "".join(cells))
print("\n(cells are the +/-95% half-width on the terminal level; '--' = no index at that k)")
print("\nIf the trade-off were as usually argued, every row would fall left to right.")
print("It does not. Five dense categories are flat; audio gets strictly worse.")

# ------------------------------------------------- why: link-path support
print("\n" + "=" * 100)
print("WHY — LINK-PATH SUPPORT (coding, historical: the 312.8 -> 717.7 -> 220.0 swing)")
print("=" * 100)
print("GEKS sets a quarter's level as the mean over every populated path base->l->t.")
print("MIN_MATCH deletes links, so it shrinks that mean's support. Collapse to one")
print("link and the 'index' is a single bilateral.\n")
panel = hist_panel["coding"]
by_q, quarters = geks._log_panel(panel, geks.WINDOW_START)
cbase = quarters[0]
counts = {}
for i, s in enumerate(quarters):
    for t in quarters[i + 1:]:
        counts[(s, t)] = len(by_q[s].keys() & by_q[t].keys())
thin = sum(1 for v in counts.values() if v < 3)
print(f"  coding historical: {len(panel)} gigs, {len(quarters)} quarters, base={cbase}")
print(f"  quarter pairs with <3 matched gigs: {thin}/{len(counts)} "
      f"({thin/len(counts)*100:.0f}%)")
for k in (3, 4, 5):
    geks.MIN_MATCH = k
    lnP = geks._bilaterals(by_q, quarters)
    lvl = geks._geks_levels(lnP, quarters, cbase)
    if cbase not in lvl:
        continue
    idx = {q: 100 * math.exp(v - lvl[cbase]) for q, v in lvl.items()}
    term = sorted(idx, key=tpd.q_to_int)[-1]
    links = [l for l in quarters if (cbase, l) in lnP and (l, term) in lnP]
    print(f"\n  MIN_MATCH={k}: {term} = {idx[term]:.1f}, supported by {len(links)} link path(s)"
          f"; direct {cbase}->{term} bilateral: "
          f"{'yes' if (cbase, term) in lnP else 'NO'} "
          f"({counts.get((cbase, term), 0)} matched gigs)")
    contribs = sorted(((lnP[(cbase, l)] + lnP[(l, term)], l) for l in links), reverse=True)
    print("    link contributions (ln, high to low): " +
          ", ".join(f"{l}={v:+.2f}" for v, l in contribs[:4]) +
          (" ..." if len(contribs) > 4 else ""))
geks.MIN_MATCH = PROD_K
print("\n  => at k=4 the terminal level rests on ONE link, and it is the most extreme")
print("     of the eight available at k=3. The +129% jump is the estimator behaving")
print("     as defined on a chain this thin, not a defect. Read it as: the historical")
print("     coding level is NOT IDENTIFIED, which its +/-61% band does not convey.")
