#!/usr/bin/env python3
"""
Pilot: unbalanced-panel price-index methods for the IPI.

Two goals:
  1. DIAGNOSE how unbalanced the panel actually is (span/duration per gig,
     coverage per quarter, entry/exit churn). This tells us whether the
     misaligned-duration concern is material.
  2. PROTOTYPE the time-dummy hedonic regression (two-way fixed effects:
     gig FE + quarter dummies on log price). This uses ALL observations
     simultaneously and is the estimator most robust to differing durations,
     because every gig that appears in >=2 quarters contributes to the time
     effects without needing to be present in every quarter.

     ln p_{it} = alpha_i (gig FE) + beta_t (quarter effect) + e_{it}
     index_t = 100 * exp(beta_t - beta_base)

  Gig fixed effects are absorbed via within-gig demeaning (Frisch-Waugh-Lovell),
  so we only solve a small (n_quarters) least-squares system.

Compares the hedonic time-dummy index to the existing chained-Jevons index
(data/pilot/panel-ipi.csv) on the composite and per category.

Pure numpy/scipy (no pandas/statsmodels in this env).
"""
import csv
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent.parent
PRICES = BASE / "data" / "pilot" / "pilot-prices.csv"
ITEMS = BASE / "data" / "pilot" / "gig-items.csv"
CHAINED = BASE / "data" / "pilot" / "panel-ipi.csv"
CAT_CHAINED = BASE / "data" / "pilot" / "panel-category-indices.csv"
OUT = Path(__file__).resolve().parent

CATEGORY_KEYWORDS = {
    "writing": ["write","article","blog","content","copywriting","story","ebook","book","proofread","edit","ghostwrit","script","resume","cover letter","press release"],
    "coding": ["code","python","javascript","app","mobile app","web","wordpress","shopify","wix","html","css","developer","software","programming","script","api","database","sql","discord bot","game"],
    "design": ["logo","design","graphic","banner","flyer","poster","illustration","draw","cartoon","caricature","infographic","photoshop","ui","ux","brand","tshirt","packaging","mockup","thumbnail","book cover","album cover"],
    "translation": ["translat","spanish","french","german","arabic","chinese","japanese","korean","hindi","portuguese"],
    "video": ["video","animation","motion","whiteboard","explainer","intro","outro","edit video","youtube","after effects","3d","render","model"],
    "audio": ["voice","voiceover","narrat","sing","music","audio","podcast","jingle","sound","mixing","master"],
    "marketing": ["seo","marketing","ads","facebook","google ads","social media","instagram","tiktok","email marketing","ppc","lead","traffic"],
    "data_entry": ["data entry","typing","transcri","convert","pdf","excel","spreadsheet","powerpoint","copy paste"],
    "data_analysis": ["data analy","statistic","research","survey","scraping","machine learning","ai","dashboard","visualization","tableau","power bi"],
}

def classify(desc, label):
    text = (desc + " " + label).lower()
    scores = {c: sum(1 for kw in kws if kw in text) for c, kws in CATEGORY_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "other"

def to_q(y, m):
    try:
        y, m = int(y), int(m)
        return f"{y}Q{(m-1)//3+1}"
    except (ValueError, TypeError):
        return None

def qfloat(q):
    return int(q[:4]) + (int(q[-1]) - 1) * 0.25

# ── Load ────────────────────────────────────────────────────────────────
item_map = {}
with open(ITEMS) as f:
    for r in csv.DictReader(f):
        item_map[(r["seller"], r["slug"])] = (r["item_label"], r["description"])

gig_q = defaultdict(lambda: defaultdict(list))   # gig -> quarter -> [prices]
gig_cat = {}
with open(PRICES) as f:
    for r in csv.DictReader(f):
        key = (r["seller"], r["slug"])
        if key not in item_map:
            continue
        try:
            p = float(r.get("price_basic", 0) or 0)
        except ValueError:
            continue
        if not (0 < p <= 10000):
            continue
        q = to_q(r["year"], r["month"])
        if not q:
            continue
        gig_q[key][q].append(p)
        if key not in gig_cat:
            lbl, desc = item_map[key]
            gig_cat[key] = classify(desc, lbl)

# median price per gig-quarter
gig_qp = {k: {q: float(np.median(v)) for q, v in qs.items()} for k, qs in gig_q.items()}
panel = {k: v for k, v in gig_qp.items() if len(v) >= 2}
all_qs = sorted({q for v in panel.values() for q in v}, key=qfloat)
qidx = {q: i for i, q in enumerate(all_qs)}

# ── 1. DIAGNOSTIC ───────────────────────────────────────────────────────
print("=" * 70)
print("PANEL BALANCE DIAGNOSTIC")
print("=" * 70)
print(f"\nGigs total (>=1 q): {len(gig_qp):,}   panel gigs (>=2 q): {len(panel):,}")
print(f"Quarters spanned: {all_qs[0]} .. {all_qs[-1]}  ({len(all_qs)} quarters)")

# span (last - first quarter, in years) and n_quarters observed per gig
spans, nqs = [], []
for k, v in panel.items():
    qs = sorted(v, key=qfloat)
    spans.append(qfloat(qs[-1]) - qfloat(qs[0]))
    nqs.append(len(v))
spans, nqs = np.array(spans), np.array(nqs)
print("\nPer-gig calendar span (years):  "
      f"min {spans.min():.2f}  p25 {np.percentile(spans,25):.2f}  "
      f"median {np.median(spans):.2f}  p75 {np.percentile(spans,75):.2f}  max {spans.max():.2f}")
print("Per-gig #quarters observed:     "
      f"min {nqs.min()}  median {int(np.median(nqs))}  max {nqs.max()}  "
      f"mean {nqs.mean():.1f}")
fill = nqs.sum() / (len(panel) * len(all_qs))
print(f"Panel fill rate (obs / gig x quarter): {fill:.1%}   "
      f"=> {'BALANCED' if fill>0.8 else 'HIGHLY UNBALANCED'}")

# coverage per quarter + entry/exit churn
print("\nPer-quarter coverage (active gigs) and churn:")
active = {q: {k for k, v in panel.items() if q in v} for q in all_qs}
print(f"  {'quarter':<8} {'active':>7} {'entered':>8} {'exited':>7}")
prev = set()
for q in all_qs:
    a = active[q]
    entered = len(a - prev)
    # exited = in prev but not in a AND never return handled loosely as not-in-a
    exited = len(prev - a)
    print(f"  {q:<8} {len(a):>7} {entered:>8} {exited:>7}")
    prev = a

# per-category duration heterogeneity — the crux of the question
print("\nPer-category span heterogeneity (the misaligned-duration issue):")
print(f"  {'category':<14} {'gigs':>5} {'first..last active q':>22} {'median gig span(y)':>18}")
cat_gigs = defaultdict(list)
for k in panel:
    if gig_cat[k] != "other":
        cat_gigs[gig_cat[k]].append(k)
for cat in sorted(cat_gigs):
    ks = cat_gigs[cat]
    qs_active = sorted({q for k in ks for q in panel[k]}, key=qfloat)
    sp = np.median([qfloat(sorted(panel[k],key=qfloat)[-1]) - qfloat(sorted(panel[k],key=qfloat)[0]) for k in ks])
    print(f"  {cat:<14} {len(ks):>5} {qs_active[0]+'..'+qs_active[-1]:>22} {sp:>18.2f}")

# ── 2. TIME-DUMMY HEDONIC (two-way FE) ──────────────────────────────────
# ln p_it = alpha_i + beta_t + e_it, gig FE absorbed by within-gig demeaning.
# After demeaning, regress demeaned ln p on demeaned quarter-dummy matrix
# (base quarter dropped). Solve via lstsq. index_t = 100*exp(beta_t).
def hedonic_index(gigs, base_q="2019Q1"):
    # build long arrays
    rows = []  # (gig_local_id, q_id, ln_p)
    gmap = {}
    for k in gigs:
        for q, p in panel[k].items():
            gi = gmap.setdefault(k, len(gmap))
            rows.append((gi, qidx[q], math.log(p)))
    if not rows:
        return {}
    gi = np.array([r[0] for r in rows])
    ti = np.array([r[1] for r in rows])
    y = np.array([r[2] for r in rows])
    # within-gig demean y
    n_g = gi.max() + 1
    gsum = np.bincount(gi, weights=y, minlength=n_g)
    gcnt = np.bincount(gi, minlength=n_g)
    gmean = gsum / gcnt
    yd = y - gmean[gi]
    # quarter dummy matrix, drop base quarter to identify
    used_q = sorted(set(ti.tolist()))
    base_id = qidx.get(base_q, used_q[0])
    if base_id not in used_q:
        base_id = used_q[0]
    cols = [q for q in used_q if q != base_id]
    col_pos = {q: j for j, q in enumerate(cols)}
    X = np.zeros((len(rows), len(cols)))
    for r, t in enumerate(ti):
        if t in col_pos:
            X[r, col_pos[t]] = 1.0
    # within-gig demean each dummy column too (FWL)
    for j in range(X.shape[1]):
        col = X[:, j]
        csum = np.bincount(gi, weights=col, minlength=n_g)
        X[:, j] = col - (csum / gcnt)[gi]
    beta, *_ = np.linalg.lstsq(X, yd, rcond=None)
    idx = {all_qs[base_id]: 100.0}
    for q, b in zip(cols, beta):
        idx[all_qs[q]] = 100.0 * math.exp(b)
    return idx

print("\n" + "=" * 70)
print("TIME-DUMMY HEDONIC INDEX (two-way FE) vs CHAINED JEVONS")
print("=" * 70)

# load existing chained composite
chained = {}
if CHAINED.exists():
    with open(CHAINED) as f:
        for r in csv.DictReader(f):
            q = r.get("quarter") or r.get("period")
            val = r.get("ipi") or r.get("index") or r.get("composite")
            if q and val:
                try: chained[q] = float(val)
                except ValueError: pass

# composite hedonic over all non-"other" panel gigs, review-weighted per category
all_panel_gigs = [k for k in panel if gig_cat[k] != "other"]
hed = hedonic_index(all_panel_gigs)

print(f"\n{'quarter':<8} {'hedonic':>9} {'chained':>9} {'diff':>7}")
for q in all_qs:
    h = hed.get(q)
    c = chained.get(q)
    hs = f"{h:8.1f}" if h else "     -- "
    cs = f"{c:8.1f}" if c else "     -- "
    d = f"{h-c:+6.1f}" if (h and c) else "    --"
    print(f"{q:<8} {hs:>9} {cs:>9} {d:>7}")

# correlation where both exist
common = [(hed[q], chained[q]) for q in all_qs if q in hed and q in chained]
if len(common) > 2:
    a = np.array([x[0] for x in common]); b = np.array([x[1] for x in common])
    r = np.corrcoef(a, b)[0, 1]
    print(f"\nCorrelation hedonic vs chained (n={len(common)} quarters): r = {r:.3f}")
    print(f"Mean abs diff: {np.mean(np.abs(a-b)):.1f} index points")

# write composite comparison
with open(OUT / "hedonic-vs-chained.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["quarter", "hedonic_twfe", "chained_jevons"])
    for q in all_qs:
        w.writerow([q, f"{hed[q]:.2f}" if q in hed else "",
                    f"{chained[q]:.2f}" if q in chained else ""])
print(f"\nWrote {OUT/'hedonic-vs-chained.csv'}")

# per-category hedonic (shows where duration heterogeneity bites)
print("\nPer-category hedonic index (endpoints):")
print(f"  {'category':<14} {'base':>6} {'last obs q':>11} {'last idx':>9}")
for cat in sorted(cat_gigs):
    ci = hedonic_index(cat_gigs[cat])
    if not ci: continue
    lastq = max((q for q in ci), key=qfloat)
    print(f"  {cat:<14} {'100':>6} {lastq:>11} {ci[lastq]:>9.1f}")
