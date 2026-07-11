#!/usr/bin/env python3
"""
Quality-adjusted two-way FE hedonic, vs the other three estimators.

Adds time-varying WITHIN-gig controls to the FE hedonic:
    ln p_it = alpha_i (gig FE) + beta_t (quarter) + g1*ln(1+reviews_it)
              + g2*rating_it + e_it
Gig FE absorb time-invariant quality; the two controls absorb reputation that
ACCUMULATES within a gig over time (a gig gaining reviews / rating drift), so the
quarter effects beta_t are net of that -- a genuinely quality-adjusted index.

All four indices on the common window 2019Q1..2024Q4, rebased to 2019Q1=100.
Reuses the GEKS + plain-hedonic construction so the four are directly comparable.
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

WINDOW = ("2019Q1", "2024Q4"); BASE_Q = "2019Q1"; MIN_MATCH = 3

def to_q(y, m):
    try: y, m = int(y), int(m); return f"{y}Q{(m-1)//3+1}"
    except (ValueError, TypeError): return None
def qfloat(q): return int(q[:4]) + (int(q[-1]) - 1) * 0.25

# ── load: per gig-quarter median price, plus median rating & reviews ───────
item_ok = set()
with open(ITEMS) as f:
    for r in csv.DictReader(f): item_ok.add((r["seller"], r["slug"]))

gp = defaultdict(lambda: defaultdict(list))   # gig->q->[price]
gr = defaultdict(lambda: defaultdict(list))   # gig->q->[rating]
gv = defaultdict(lambda: defaultdict(list))   # gig->q->[reviews]
with open(PRICES) as f:
    for r in csv.DictReader(f):
        k = (r["seller"], r["slug"])
        if k not in item_ok: continue
        try: p = float(r.get("price_basic", 0) or 0)
        except ValueError: continue
        if not (0 < p <= 10000): continue
        q = to_q(r["year"], r["month"])
        if not q: continue
        gp[k][q].append(p)
        rr = (r.get("rating") or "").strip()
        vv = (r.get("review_count") or "").strip()
        try:
            f_r = float(rr)
            if 0 < f_r <= 5: gr[k][q].append(f_r)      # clip out the /10 artifacts
        except ValueError: pass
        try:
            i_v = int(float(vv))
            if i_v >= 0: gv[k][q].append(i_v)
        except ValueError: pass

lo, hi = qfloat(WINDOW[0]), qfloat(WINDOW[1])
def inwin(q): return lo <= qfloat(q) <= hi

price = {k: {q: float(np.median(v)) for q, v in qs.items() if inwin(q)} for k, qs in gp.items()}
price = {k: v for k, v in price.items() if len(v) >= 2}
rating = {k: {q: float(np.median(v)) for q, v in qs.items()} for k, qs in gr.items()}
reviews = {k: {q: float(np.median(v)) for q, v in qs.items()} for k, qs in gv.items()}
all_qs = sorted({q for v in price.values() for q in v}, key=qfloat)
print(f"Window {WINDOW[0]}..{WINDOW[1]}: {len(all_qs)} quarters, {len(price)} panel gigs")

# ── shared helpers ────────────────────────────────────────────────────────
def within_demean(gi, col, gc, n_g):
    csum = np.bincount(gi, weights=col, minlength=n_g)
    return col - (csum / gc)[gi]

def hedonic(with_quality):
    """Two-way FE hedonic; if with_quality, add ln(1+reviews) & rating controls.
       Returns (index_dict, gammas or None, n_obs)."""
    rows = []   # (gig, quarter, ln_p, ln_rev, rating)
    gmap = {}
    for k in price:
        for q, p in price[k].items():
            if with_quality:
                rv = reviews.get(k, {}).get(q); rt = rating.get(k, {}).get(q)
                if rv is None or rt is None:      # need both controls present
                    continue
                rows.append((gmap.setdefault(k, len(gmap)), q, math.log(p), math.log(1+rv), rt))
            else:
                rows.append((gmap.setdefault(k, len(gmap)), q, math.log(p), 0.0, 0.0))
    gi = np.array([r[0] for r in rows]); y = np.array([r[2] for r in rows])
    qs_used = [r[1] for r in rows]
    n_g = gi.max() + 1; gc = np.bincount(gi, minlength=n_g)
    yd = within_demean(gi, y, gc, n_g)
    cols = [q for q in all_qs if q != BASE_Q]; cpos = {q: j for j, q in enumerate(cols)}
    ncq = len(cols)
    extra = 2 if with_quality else 0
    X = np.zeros((len(rows), ncq + extra))
    for r, q in enumerate(qs_used):
        if q in cpos: X[r, cpos[q]] = 1.0
    if with_quality:
        X[:, ncq]   = np.array([r[3] for r in rows])   # ln(1+reviews)
        X[:, ncq+1] = np.array([r[4] for r in rows])   # rating
    for j in range(X.shape[1]):
        X[:, j] = within_demean(gi, X[:, j], gc, n_g)
    beta, *_ = np.linalg.lstsq(X, yd, rcond=None)
    idx = {BASE_Q: 100.0}
    for q, b in zip(cols, beta[:ncq]): idx[q] = 100.0 * math.exp(b)
    gammas = (beta[ncq], beta[ncq+1]) if with_quality else None
    return idx, gammas, len(rows)

hed, _, n_plain = hedonic(False)
hedq, gammas, n_q = hedonic(True)
print(f"Plain hedonic obs: {n_plain}   quality-adj obs: {n_q}")
print(f"Quality controls (within-gig):  ln(1+reviews) beta = {gammas[0]:+.4f}   rating beta = {gammas[1]:+.4f}")

# ── GEKS-Jevons (drift referee) ───────────────────────────────────────────
by_q = {q: {k: math.log(price[k][q]) for k in price if q in price[k]} for q in all_qs}
lnP = {}
for i, s in enumerate(all_qs):
    for t in all_qs[i+1:]:
        common = by_q[s].keys() & by_q[t].keys()
        if len(common) >= MIN_MATCH:
            d = float(np.mean([by_q[t][k] - by_q[s][k] for k in common]))
            lnP[(s, t)] = d; lnP[(t, s)] = -d
geks = {}
for t in all_qs:
    vals = [lnP[(BASE_Q, l)] + lnP[(l, t)] for l in all_qs if (BASE_Q, l) in lnP and (l, t) in lnP]
    if vals: geks[t] = 100.0 * math.exp(float(np.mean(vals)))
    elif (BASE_Q, t) in lnP: geks[t] = 100.0 * math.exp(lnP[(BASE_Q, t)])
geks[BASE_Q] = 100.0

# ── chained (from production csv, rebased) ────────────────────────────────
chained_raw = {}
with open(CHAINED) as f:
    for r in csv.DictReader(f):
        try: chained_raw[r["quarter"]] = float(r["ipi"])
        except (ValueError, KeyError): pass
bv = chained_raw.get(BASE_Q, 100.0)
chained = {q: v / bv * 100.0 for q, v in chained_raw.items() if q in all_qs}

# ── report + write ────────────────────────────────────────────────────────
print(f"\n{'quarter':<8}{'chained':>9}{'GEKS':>8}{'hedonic':>9}{'hed+QA':>8}")
for q in all_qs:
    def s(d): x=d.get(q); return f"{x:8.1f}" if x is not None else "      --"
    print(f"{q:<8}{s(chained):>9}{s(geks):>8}{s(hed):>9}{s(hedq):>8}")

def corr(d1, d2):
    ks=[q for q in all_qs if q in d1 and q in d2]
    a=np.array([d1[q] for q in ks]); b=np.array([d2[q] for q in ks])
    return np.corrcoef(a,b)[0,1], float(np.mean(np.abs(a-b)))
e=all_qs[-1]
print(f"\nEndpoint {e}:  chained={chained[e]:.0f}  GEKS={geks[e]:.0f}  hedonic={hed[e]:.0f}  hed+QA={hedq[e]:.0f}")
r_hq,m_hq=corr(hed,hedq); print(f"plain vs quality-adj hedonic:  r={r_hq:.3f}  mean|diff|={m_hq:.1f}")
r_gq,m_gq=corr(geks,hedq); print(f"GEKS  vs quality-adj hedonic:  r={r_gq:.3f}  mean|diff|={m_gq:.1f}")

with open(OUT/"four-index-comparison.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["quarter","chained_jevons","geks_jevons","hedonic_twfe","hedonic_quality_adj"])
    for q in all_qs:
        w.writerow([q,
            f"{chained.get(q,''):.2f}" if q in chained else "",
            f"{geks.get(q,''):.2f}" if q in geks else "",
            f"{hed.get(q,''):.2f}" if q in hed else "",
            f"{hedq.get(q,''):.2f}" if q in hedq else ""])
print(f"\nWrote {OUT/'four-index-comparison.csv'}")
