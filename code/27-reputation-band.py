#!/usr/bin/env python3
"""Step 27: the reputation-adjusted band — Phase 1 decision D2 of
`plans/active/publication.md`.

THE QUESTION. A gig's price rises partly because the gig accumulates reviews
(cumulative completed orders), not because the service got dearer. Step 22 Test B
measured that treadmill; this script decides how to PUBLISH it.

    adjusted price = p * exp(-beta * ln(1+reviews))

and the index is rebuilt on the adjusted series. Raw is then the upper bound and
adjusted the lower bound of a band. Reviews are cumulative SALES, so beta is a
BAD CONTROL: if AI suppressed demand, review growth slows and the adjustment
absorbs part of the very effect the paper is trying to measure. That is the whole
reason for publishing a band rather than swapping the headline.

ONE REAL DEFECT IN STEP 22, AND ONE FALSE ALARM — both checked 2026-08-06:

  1. REAL — STEP 22's BETA SE IS UNCLUSTERED. It runs plain OLS on 9,543 within-gig
     first differences drawn from 3,298 gigs, so the errors are correlated within
     gig. Gig-clustered SEs are 1.93x larger: se 0.0101 -> 0.0195, t 10.19 -> 5.26.
     Beta survives comfortably; the published t does not.

  2. FALSE ALARM — Test B2's panel construction does differ from production
     (build_reputation_panel merges both price files into one panel; design carries
     1,637 gigs against production historical's 330), and I first read that as
     making its magnitudes unquotable. It does not. The resulting 2024Q3 levels
     agree closely with the published index -- design 146.8 vs 146.7 unrestricted,
     translation 227.8 vs 227.8, audio 310.1 vs 307.4, writing 189.5 vs 186.0. The
     apparent 146.8-vs-156.6 gap that prompted the concern was a quarter mismatch
     on my part: 156.6 is design's TERMINAL quarter (2025Q4), not its 2024Q3 level.
     The RAW column below is verified against the unrestricted production index at
     run time so this cannot drift again.

METHOD HERE. Take the production panels from 19-tpd-index.py unmodified, attach
median review counts on the same (gig, quarter) cells, and restrict BOTH the raw
and the adjusted index to cells carrying reviews -- so the only difference between
the two series is the adjustment, not the sample. Beta is re-estimated on those
same cells for internal consistency, and reported alongside step 22's.

Run:  python3 code/27-reputation-band.py
"""
import csv
import importlib.util
import math
import sys
from collections import defaultdict
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
geks = _load("geks", "21-geks-index.py")
hed = _load("hed", "25-hedonic-regression.py")      # ols_cluster
CATS = tpd.CATS
PILOT = BASE / "data" / "pilot"
BETA_GRID = [0.00, 0.05, 0.10, 0.15, 0.20]


def review_lookup():
    """{(seller, slug): {quarter: median review_count}} over both price files."""
    raw = defaultdict(lambda: defaultdict(list))
    for path in (PILOT / "pilot-prices.csv", PILOT / "recent-prices.csv"):
        with open(path) as f:
            for row in csv.DictReader(f):
                if not is_gig(row["seller"]):
                    continue
                try:
                    rev = float(row.get("review_count") or "")
                except ValueError:
                    continue
                q = tpd.to_quarter(row["year"], row["month"])
                if not q:
                    continue
                raw[(row["seller"], row["slug"])][q].append(rev)
    return {k: {q: float(np.median(v)) for q, v in qs.items()} for k, qs in raw.items()}


def restrict_and_adjust(panel_by_cat, revs, beta):
    """Keep only cells that carry reviews; return (raw, adjusted) on that SAME set."""
    raw_out, adj_out = {}, {}
    kept = total = 0
    for cat, gigs in panel_by_cat.items():
        r_c, a_c = {}, {}
        for gig, qs in gigs.items():
            gr = revs.get(gig, {})
            r_cells, a_cells = {}, {}
            for q, p in qs.items():
                total += 1
                if q not in gr:
                    continue
                kept += 1
                r_cells[q] = p
                a_cells[q] = p * math.exp(-beta * math.log1p(gr[q]))
            if len(r_cells) >= 2:
                r_c[gig], a_c[gig] = r_cells, a_cells
        if r_c:
            raw_out[cat], adj_out[cat] = r_c, a_c
    return raw_out, adj_out, kept, total


def estimate_beta(panel_by_cat, revs, per_category=False):
    """Within-gig FD with quarter FE, gig-clustered SEs, on the production cells."""
    rows = []
    for cat, gigs in panel_by_cat.items():
        for gig, qs in gigs.items():
            gr = revs.get(gig, {})
            order = [q for q in sorted(qs, key=tpd.q_to_int) if q in gr]
            for a, b in zip(order, order[1:]):
                if qs[a] <= 0 or qs[b] <= 0:
                    continue
                rows.append((gig, cat, b,
                             math.log(qs[b]) - math.log(qs[a]),
                             math.log1p(gr[b]) - math.log1p(gr[a])))
    if not rows:
        return None, None, 0, 0, {}

    def fit(sub):
        y = np.array([r[3] for r in sub])
        qs_ = sorted({r[2] for r in sub}, key=tpd.q_to_int)
        qi = {q: i for i, q in enumerate(qs_)}
        X = np.zeros((len(sub), 1 + len(qs_)))
        X[:, 0] = np.array([r[4] for r in sub])
        for i, r in enumerate(sub):
            X[i, 1 + qi[r[2]]] = 1.0
        names = ["dlnr"] + [f"q:{q}" for q in qs_]
        res = hed.ols_cluster(X, y, [r[0] for r in sub], names)
        return res["beta"][0], res["se"][0], len(sub), res["G"]

    b, se, n, g = fit(rows)
    per = {}
    if per_category:
        for cat in CATS:
            sub = [r for r in rows if r[1] == cat]
            if len(sub) >= 50:
                per[cat] = fit(sub)
    return b, se, n, g, per


def build_series(panel_by_cat, window_start=None):
    rng = np.random.default_rng(geks.SEED)
    idx, se = {}, {}
    for cat in CATS:
        if panel_by_cat.get(cat):
            kw = {} if window_start is None else {"window_start": window_start}
            i, s, _ = geks.geks_index(panel_by_cat[cat], rng=rng, **kw)
            if i:
                idx[cat], se[cat] = i, s
    return idx, se


def composite_of(h_idx, r_idx, weights):
    chained = {c: tpd.chain_category(c, h_idx, r_idx) for c in CATS}
    chained = {c: s for c, s in chained.items() if s}
    qs = sorted({q for s in chained.values() for q in s}, key=tpd.q_to_int)
    qs = [q for q in qs if tpd.q_to_int(q) >= tpd.q_to_int(tpd.START_Q)]
    comp = {q: tpd.composite_at(chained, weights, q) for q in qs}
    return chained, {q: v for q, v in comp.items() if v is not None}


def main():
    weights = {}
    with open(tpd.WEIGHTS_CSV) as f:
        for row in csv.DictReader(f):
            weights[row["category"]] = float(row["weight"])

    revs = review_lookup()
    hist = tpd.build_panel_historical()
    recent = tpd.build_panel_recent()

    print("=" * 92)
    print("STEP 27 — REPUTATION-ADJUSTED BAND (decision D2)")
    print("=" * 92)

    # ---------------------------------------------------------------- beta
    print("\n" + "-" * 92)
    print("BETA — within-gig first differences + quarter FE, GIG-CLUSTERED SEs")
    print("-" * 92)
    allcells = {c: dict(hist.get(c, {}), **{}) for c in CATS}
    for c in CATS:                       # pool both panels for estimation only
        for g, qs in recent.get(c, {}).items():
            allcells.setdefault(c, {}).setdefault(g, {}).update(qs)
    b, se, n, g, per = estimate_beta(allcells, revs, per_category=True)
    print(f"  pooled beta = {b:+.4f}  (se {se:.4f}, t {b/se:.2f})   "
          f"n = {n} transitions, {g} gigs")
    print(f"  => a doubling of a gig's reviews moves its price "
          f"{100*(math.exp(b*math.log(2))-1):+.1f}%")
    print(f"\n  step 22 reported beta +0.1026 with se 0.0101 (t 10.19) on its own")
    print(f"  combined panel and WITHOUT clustering; clustering alone is a 1.93x")
    print(f"  widening. Beta survives; the published t does not.")
    print(f"\n  {'cat':<12} {'beta':>9} {'se':>8} {'t':>7} {'n':>7} {'gigs':>7}")
    for cat in CATS:
        if cat in per:
            pb, pse, pn, pg = per[cat]
            flag = "  <-- WRONG SIGN" if pb < 0 else ""
            print(f"  {cat:<12} {pb:>+9.4f} {pse:>8.4f} {pb/pse:>7.2f} "
                  f"{pn:>7} {pg:>7}{flag}")
    neg = [c for c in per if per[c][0] < 0]
    if neg:
        print(f"\n  {len(neg)} categories carry a NEGATIVE beta ({', '.join(neg)}).")
        print("  Adjusting those with their own beta would RAISE their index -- i.e.")
        print("  'strip out reputation' would add price. That is not interpretable,")
        print("  and it is the decisive argument for a POOLED beta.")

    # ---------------------------------------------------- raw vs adjusted
    print("\n" + "-" * 92)
    print(f"RAW vs ADJUSTED on the PRODUCTION panels (pooled beta = {b:.4f})")
    print("-" * 92)
    h_raw, h_adj, hk, ht = restrict_and_adjust(hist, revs, b)
    r_raw, r_adj, rk, rt = restrict_and_adjust(recent, revs, b)
    print(f"  cells carrying reviews: historical {hk}/{ht} ({hk/ht:.1%}), "
          f"recent {rk}/{rt} ({rk/rt:.1%})")
    print("  raw and adjusted are computed on this SAME restricted cell set, so the")
    print("  only difference between the two series is the adjustment.")

    # the restriction must not itself move the index -- check, do not assume
    unres_h, _ = build_series(hist)
    print(f"\n  CHECK — does restricting to review-carrying cells move the index?")
    print(f"  {'cat':<12} {'unrestricted 2024Q3':>20} {'restricted raw':>16} {'gap':>8}")
    for cat in CATS:
        u = unres_h.get(cat, {}).get("2024Q3")
        r_ = build_series({cat: h_raw[cat]})[0].get(cat, {}).get("2024Q3") if cat in h_raw else None
        if u is None or r_ is None:
            continue
        print(f"  {cat:<12} {u:>20.1f} {r_:>16.1f} {(r_/u-1)*100:>+7.1f}%")

    hi_raw, _ = build_series(h_raw)
    hi_adj, _ = build_series(h_adj)
    ri_raw, _ = build_series(r_raw)
    ri_adj, _ = build_series(r_adj)

    print(f"\n  {'cat':<12} {'hist 2024Q3':>22} {'recent 2026Q1':>22}")
    print(f"  {'':<12} {'raw':>10}{'adj':>10}{'d%':>6}  {'raw':>10}{'adj':>10}{'d%':>6}")
    for cat in CATS:
        hr, ha = hi_raw.get(cat, {}).get("2024Q3"), hi_adj.get(cat, {}).get("2024Q3")
        rr, ra = ri_raw.get(cat, {}).get("2026Q1"), ri_adj.get(cat, {}).get("2026Q1")
        def cell(x, y):
            if x is None or y is None:
                return f"{'-':>10}{'-':>10}{'-':>6}"
            return f"{x:>10.1f}{y:>10.1f}{(y/x-1)*100:>+6.0f}"
        print(f"  {cat:<12} {cell(hr, ha)}  {cell(rr, ra)}")

    _, comp_raw = composite_of(hi_raw, ri_raw, weights)
    _, comp_adj = composite_of(hi_adj, ri_adj, weights)
    lq = sorted(comp_raw, key=tpd.q_to_int)[-1]
    print(f"\n  COMPOSITE {tpd.START_Q}->{lq}:  raw {comp_raw[lq]:.1f} "
          f"({comp_raw[lq]-100:+.1f}%)   adjusted {comp_adj[lq]:.1f} "
          f"({comp_adj[lq]-100:+.1f}%)")
    print(f"  => THE BAND: +{comp_adj[lq]-100:.1f}% to +{comp_raw[lq]-100:.1f}% "
          f"(width {comp_raw[lq]-comp_adj[lq]:.1f} pts)")

    # ------------------------------------------------------- beta grid
    print("\n" + "-" * 92)
    print("SENSITIVITY — composite as beta varies (0 = no adjustment)")
    print("-" * 92)
    print(f"  {'beta':>6} {'composite':>11} {'full-window':>13}")
    for bg in BETA_GRID:
        _, a_h, _, _ = restrict_and_adjust(hist, revs, bg)
        _, a_r, _, _ = restrict_and_adjust(recent, revs, bg)
        ih, _ = build_series(a_h)
        ir, _ = build_series(a_r)
        _, cg = composite_of(ih, ir, weights)
        if not cg:
            continue
        q = sorted(cg, key=tpd.q_to_int)[-1]
        mark = "  <-- estimated" if abs(bg - b) < 0.026 else ""
        print(f"  {bg:>6.2f} {cg[q]:>11.1f} {cg[q]-100:>+12.1f}%{mark}")

    print("\n" + "=" * 92)
    print("HOW TO READ THIS: the adjusted series is a LOWER bound, not a correction.")
    print("Reviews are cumulative sales, so beta absorbs demand as well as reputation.")
    print("Publish the pair as a band; do not swap the headline.")
    print("=" * 92)


if __name__ == "__main__":
    main()
