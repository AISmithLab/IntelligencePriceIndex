#!/usr/bin/env python3
"""Step 33: the assumption-free corroboration of GEKS — closes `method.test.md` R10.

THE CRITIQUE. Both estimators the paper compares GEKS against (the chained Jevons
of §3.4 and the time-product-dummy of the same section) are built on the same
panel and share its construction. A reviewer can reasonably ask whether the
agreement between them is informative or circular.

THE ANSWER. A DIRECT bilateral Jevons comparison between the base quarter and the
terminal quarter uses only gigs observed at BOTH endpoints. It involves no chain,
no transitivity correction, no regression, no imputation, and no link quarters --
so it shares no estimation machinery with GEKS at all. If GEKS is inventing the
level, this will not reproduce it.

    ln P(0,T) = mean over gigs i observed in both 0 and T of [ln p_iT - ln p_i0]

An earlier version of this check existed but its figures PREDATE the Stage 5b
non-gig exclusion (2026-07-31), which moved the composite by 26 real points, so
they could not be quoted. This re-measures on the current production panel.

THE CAVEAT THAT MUST TRAVEL WITH IT. Very few gigs survive both endpoints -- that
is exactly why GEKS routes through link quarters in the first place. This is
CORROBORATION, not a precise estimate, and the script reports the matched count
for every cell so the reader can see how thin it is.

Measurement only -- writes nothing outside scratchpad/.

Run:  python3 code/33-direct-matched-check.py
"""
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
q_int = tpd.q_to_int


def direct_bilateral(panel_cat, q0, qT):
    """Jevons over gigs observed at both endpoints. Returns (level, n_matched)."""
    both = [(qs[q0], qs[qT]) for qs in panel_cat.values()
            if q0 in qs and qT in qs and qs[q0] > 0 and qs[qT] > 0]
    if not both:
        return None, 0
    d = float(np.mean([math.log(b / a) for a, b in both]))
    return 100.0 * math.exp(d), len(both)


def chained_adjacent(panel_cat, q0, qT):
    """Chained Jevons over adjacent quarter pairs only — a second independent
    construction, and the one §3.4 uses for the D4 decomposition."""
    by_q, quarters = geks._log_panel(panel_cat, q0)
    quarters = [q for q in quarters if q_int(q0) <= q_int(q) <= q_int(qT)]
    if len(quarters) < 2:
        return None
    lvl = 1.0
    for a, b in zip(quarters, quarters[1:]):
        common = by_q[a].keys() & by_q[b].keys()
        if len(common) < geks.MIN_MATCH:
            continue
        lvl *= math.exp(float(np.mean([by_q[b][g] - by_q[a][g] for g in common])))
    return 100.0 * lvl


print("=" * 96)
print("DIRECT MATCHED-PAIR CHECK — does GEKS survive an estimator that shares none of its machinery?")
print("=" * 96)

hist = tpd.build_panel_historical()
recent = tpd.build_panel_recent()
rng = np.random.default_rng(geks.SEED)

for tag, panel, base_q in (("HISTORICAL", hist, tpd.START_Q),
                           ("RECENT", recent, tpd.LINK_Q)):
    print(f"\n{tag} panel, base {base_q} = 100")
    print(f"{'cat':<12}{'terminal':>9}{'GEKS':>9}{'direct':>9}{'adj-chain':>11}"
          f"{'n matched':>11}{'GEKS vs direct':>16}")
    rows = []
    for c in CATS:
        if not panel.get(c):
            continue
        idx, se, _ = geks.geks_index(panel[c], rng=rng, window_start=base_q)
        if not idx:
            print(f"{c:<12}{'NO INDEX':>9}")
            continue
        qs = sorted(idx, key=q_int)
        term = qs[-1]
        g = idx[term]
        d, n = direct_bilateral(panel[c], base_q, term)
        ch = chained_adjacent(panel[c], base_q, term)
        if d is None:
            print(f"{c:<12}{term:>9}{g:>9.1f}{'none':>9}"
                  f"{(f'{ch:11.1f}' if ch else '          -')}{n:>11}{'no overlap':>16}")
            continue
        gap = (g / d - 1) * 100
        band = 196.0 * se.get(term, 0.0)
        inside = abs(gap) <= band
        rows.append((c, g, d, n, gap, band, inside))
        print(f"{c:<12}{term:>9}{g:>9.1f}{d:>9.1f}"
              f"{(f'{ch:11.1f}' if ch else '          -')}{n:>11}"
              f"{gap:>+14.1f}% {'in' if inside else 'OUT'}")
    if rows:
        ok = sum(1 for r in rows if r[6])
        med = float(np.median([abs(r[4]) for r in rows]))
        print(f"\n  {ok} of {len(rows)} categories: GEKS is within its own 95% band of the")
        print(f"  direct comparison. Median absolute gap {med:.1f}%.")
        print(f"  Matched gigs at both endpoints: "
              f"{', '.join(f'{r[0]} {r[3]}' for r in rows)}")

print("\n" + "=" * 96)
print("READING: the direct column shares no machinery with GEKS — no chain, no")
print("transitivity correction, no link quarters, no regression, no imputation.")
print("Agreement is therefore corroboration rather than internal consistency. The")
print("n column is the caveat: where it is small the direct figure is itself very")
print("imprecise, which is the reason GEKS routes through link quarters at all.")
print("=" * 96)
