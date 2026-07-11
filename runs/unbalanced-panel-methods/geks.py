#!/usr/bin/env python3
"""
GEKS-Jevons index as the drift referee, vs chained Jevons vs two-way FE hedonic.

GEKS makes every pairwise bilateral Jevons comparison transitive by taking, for
each (s,t), the geometric mean over all "link" quarters l of P(s,l)*P(l,t). It is
drift-free (like the FE hedonic) but built from the SAME matched bilateral Jevons
comparisons as the current chained index -- so it isolates chain drift as the only
difference. If GEKS ~ hedonic and both sit well below the chained Jevons, drift is
confirmed as the culprit.

Restricted to the thick-coverage window 2019Q1..2024Q4 so bilateral overlaps are
populated. Uploads a comparison CSV; the chart is built separately as an Artifact.

Pure numpy.
"""
import csv, math
from collections import defaultdict
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parent.parent.parent
PRICES = BASE / "data" / "pilot" / "pilot-prices.csv"
ITEMS  = BASE / "data" / "pilot" / "gig-items.csv"
CHAINED = BASE / "data" / "pilot" / "panel-ipi.csv"
OUT = Path(__file__).resolve().parent

WINDOW = ("2019Q1", "2024Q4")   # thick-coverage window
BASE_Q = "2019Q1"
MIN_MATCH = 3                    # matched gigs required for a bilateral comparison

def to_q(y, m):
    try: y, m = int(y), int(m); return f"{y}Q{(m-1)//3+1}"
    except (ValueError, TypeError): return None
def qfloat(q): return int(q[:4]) + (int(q[-1]) - 1) * 0.25

# ── load panel (median basic price per gig-quarter, >=2 quarters) ──────────
item_ok = set()
with open(ITEMS) as f:
    for r in csv.DictReader(f): item_ok.add((r["seller"], r["slug"]))
gq = defaultdict(lambda: defaultdict(list))
with open(PRICES) as f:
    for r in csv.DictReader(f):
        k = (r["seller"], r["slug"])
        if k not in item_ok: continue
        try: p = float(r.get("price_basic", 0) or 0)
        except ValueError: continue
        if not (0 < p <= 10000): continue
        q = to_q(r["year"], r["month"])
        if q: gq[k][q].append(p)
panel = {k: {q: float(np.median(v)) for q, v in qs.items()} for k, qs in gq.items()}
panel = {k: v for k, v in panel.items() if len(v) >= 2}

lo, hi = qfloat(WINDOW[0]), qfloat(WINDOW[1])
all_qs = sorted({q for v in panel.values() for q in v if lo <= qfloat(q) <= hi}, key=qfloat)
# restrict each gig to window quarters
panelw = {k: {q: p for q, p in v.items() if lo <= qfloat(q) <= hi} for k, v in panel.items()}
panelw = {k: v for k, v in panelw.items() if len(v) >= 2}
print(f"Window {WINDOW[0]}..{WINDOW[1]}: {len(all_qs)} quarters, {len(panelw)} panel gigs")

# ── bilateral log-Jevons P(s,t) over gigs present in both, >=MIN_MATCH ─────
lnP = {}   # (s,t) -> mean(ln p_t - ln p_s)
by_q = {q: {k: math.log(panelw[k][q]) for k in panelw if q in panelw[k]} for q in all_qs}
for i, s in enumerate(all_qs):
    for t in all_qs[i+1:]:
        common = by_q[s].keys() & by_q[t].keys()
        if len(common) >= MIN_MATCH:
            d = np.mean([by_q[t][k] - by_q[s][k] for k in common])
            lnP[(s, t)] = d
            lnP[(t, s)] = -d
for q in all_qs: lnP[(q, q)] = 0.0

def bilat(s, t): return lnP.get((s, t))

# ── GEKS: ln P_GEKS(base,t) = mean over links l of [P(base,l)+P(l,t)] ──────
def geks_from_base(base):
    out = {}
    for t in all_qs:
        vals = []
        for l in all_qs:
            a, b = bilat(base, l), bilat(l, t)
            if a is not None and b is not None:
                vals.append(a + b)
        if vals: out[t] = float(np.mean(vals))
        elif bilat(base, t) is not None: out[t] = bilat(base, t)
    return out

geks_ln = geks_from_base(BASE_Q)
geks = {q: 100.0 * math.exp(v) for q, v in geks_ln.items()}

# ── two-way FE hedonic on the SAME window (gig FE absorbed via demeaning) ──
def hedonic(gigs):
    rows, gmap = [], {}
    for k in gigs:
        for q, p in panelw[k].items():
            gi = gmap.setdefault(k, len(gmap))
            rows.append((gi, q, math.log(p)))
    gi = np.array([r[0] for r in rows]); y = np.array([r[2] for r in rows])
    qs_used = [r[1] for r in rows]
    n_g = gi.max() + 1
    gmean = np.bincount(gi, weights=y, minlength=n_g) / np.bincount(gi, minlength=n_g)
    yd = y - gmean[gi]
    cols = [q for q in all_qs if q != BASE_Q]
    cpos = {q: j for j, q in enumerate(cols)}
    X = np.zeros((len(rows), len(cols)))
    for r, q in enumerate(qs_used):
        if q in cpos: X[r, cpos[q]] = 1.0
    gc = np.bincount(gi, minlength=n_g)
    for j in range(X.shape[1]):
        csum = np.bincount(gi, weights=X[:, j], minlength=n_g)
        X[:, j] -= (csum / gc)[gi]
    beta, *_ = np.linalg.lstsq(X, yd, rcond=None)
    idx = {BASE_Q: 100.0}
    for q, b in zip(cols, beta): idx[q] = 100.0 * math.exp(b)
    return idx
hed = hedonic(list(panelw.keys()))

# ── chained (rebased so 2019Q1=100 to match) ──────────────────────────────
chained_raw = {}
with open(CHAINED) as f:
    for r in csv.DictReader(f):
        try: chained_raw[r["quarter"]] = float(r["ipi"])
        except (ValueError, KeyError): pass
base_val = chained_raw.get(BASE_Q, 100.0)
chained = {q: v / base_val * 100.0 for q, v in chained_raw.items() if q in all_qs}

# ── report + write ────────────────────────────────────────────────────────
print(f"\n{'quarter':<8}{'chained':>9}{'GEKS':>8}{'hedonic':>9}{'GEKS-hed':>9}{'chn-GEKS':>9}")
for q in all_qs:
    c, g, h = chained.get(q), geks.get(q), hed.get(q)
    def s(x): return f"{x:8.1f}" if x is not None else "      --"
    gh = f"{g-h:+8.1f}" if (g and h) else "      --"
    cg = f"{c-g:+8.1f}" if (c and g) else "      --"
    print(f"{q:<8}{s(c):>9}{s(g):>8}{s(h):>9}{gh:>9}{cg:>9}")

def corr(d1, d2):
    ks = [q for q in all_qs if q in d1 and q in d2]
    a = np.array([d1[q] for q in ks]); b = np.array([d2[q] for q in ks])
    return np.corrcoef(a, b)[0, 1], np.mean(np.abs(a - b)), ks
r_gh, mad_gh, _ = corr(geks, hed)
r_cg, mad_cg, _ = corr(chained, geks)
print(f"\nGEKS vs hedonic:  r={r_gh:.3f}  mean|diff|={mad_gh:.1f}")
print(f"chained vs GEKS:  r={r_cg:.3f}  mean|diff|={mad_cg:.1f}")
endq = all_qs[-1]
print(f"\nEndpoint {endq}:  chained={chained.get(endq):.0f}  GEKS={geks.get(endq):.0f}  hedonic={hed.get(endq):.0f}")
if geks.get(endq) and chained.get(endq):
    print(f"Chained overstates vs GEKS by {chained[endq]/geks[endq]:.2f}x at {endq}")

with open(OUT / "three-index-comparison.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["quarter", "chained_jevons", "geks_jevons", "hedonic_twfe"])
    for q in all_qs:
        w.writerow([q, f"{chained.get(q,''):.2f}" if q in chained else "",
                       f"{geks.get(q,''):.2f}" if q in geks else "",
                       f"{hed.get(q,''):.2f}" if q in hed else ""])
print(f"\nWrote {OUT/'three-index-comparison.csv'}")
