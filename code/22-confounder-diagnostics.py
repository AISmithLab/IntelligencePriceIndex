"""Confounder diagnostics: is the IPI's rise really about AI?

Four tests that separate the AI signal from three rival explanations.

  A/A2  Pre-AI placebo. Re-estimate GEKS-Jevons with the window pushed back to
        2018Q1 (pre-ChatGPT, pre-Stable-Diffusion). If prices already climbed at
        the post-2022 rate, the post-2022 climb says nothing about AI.
  B     The reputation treadmill. Within a gig, price and cumulative review count
        both rise. A matched-model index holds the *gig* constant but not the
        seller's accumulated reputation, so reputation growth enters the index as
        pure price inflation. Estimates the within-gig elasticity of price w.r.t.
        reviews, with quarter fixed effects absorbing common shocks.
  B2    Rebuilds the index on reputation-adjusted prices, ln p - beta*ln(1+reviews).
  C     New-gig entry prices. The matched-model index follows *incumbent* gigs,
        which are ageing. New gigs enter with no tenure and no reviews. If the
        market price of the service is genuinely rising, entrants must post higher
        prices too. Flat entry prices alongside a climbing index means the climb is
        a tenure/survivorship premium, not a price level.

CAVEAT on B: review count is not exogenous. Reviews are cumulative sales, so if AI
suppresses demand, review growth slows and adjusting for it absorbs part of the very
effect we want to measure (a "bad control" in the Angrist-Pischke sense). Treat the
adjusted index as a lower bound on measured price growth, not as the headline.

CAVEAT on C: the historical (500-seller pilot) and recent crawls have different
sampling frames -- HIST 2024 entry median $50 (n=102) vs RECENT 2024 $30 (n=2389).
Compare within a crawl, not across.

Run:  python3 code/22-confounder-diagnostics.py
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

CATS = tpd.CATS
PILOT = BASE / "data" / "pilot"


# --------------------------------------------------------------------------
# Test A: push the GEKS window back to 2018Q1
# --------------------------------------------------------------------------
def test_a():
    print("=" * 78)
    print("TEST A — pre-AI placebo: GEKS with the window pushed back to 2018Q1")
    print("=" * 78)
    panel = tpd.build_panel_historical()
    rng = np.random.default_rng(7)

    for start in ("2018Q1", "2020Q1"):
        print(f"\n--- window_start = {start} (base quarter = 100) ---")
        print(f"{'cat':<12} {'qtrs':>5} {'dens':>6} "
              f"{'2019Q4':>8} {'2020Q1':>8} {'2022Q4':>8} {'2024Q3':>8}")
        for cat in CATS:
            pc = panel.get(cat, {})
            if not pc:
                continue
            idx, se, diag = geks.geks_index(pc, rng=rng, n_boot=0, window_start=start)
            if not idx:
                print(f"{cat:<12} {'--- no identified quarters ---'}")
                continue
            cells = " ".join(
                f"{idx[q]:8.1f}" if q in idx else f"{'.':>8}"
                for q in ("2019Q4", "2020Q1", "2022Q4", "2024Q3")
            )
            print(f"{cat:<12} {diag['quarters_out']:>5} "
                  f"{diag['pair_density']:>6.2f} {cells}")

        # annualised growth pre vs post, per category, on the 2018Q1-based series
        if start == "2018Q1":
            print("\n  annualised %/yr on the 2018-based series:")
            print(f"  {'cat':<12} {'18Q1-19Q4':>10} {'20Q1-22Q3':>10} {'22Q4-24Q3':>10}")
            for cat in CATS:
                pc = panel.get(cat, {})
                if not pc:
                    continue
                idx, _, _ = geks.geks_index(pc, rng=rng, n_boot=0, window_start=start)
                if not idx:
                    continue

                def cagr(q0, q1, years):
                    if q0 not in idx or q1 not in idx:
                        return None
                    return 100 * ((idx[q1] / idx[q0]) ** (1 / years) - 1)

                segs = [cagr("2018Q1", "2019Q4", 1.75),
                        cagr("2020Q1", "2022Q3", 2.5),
                        cagr("2022Q4", "2024Q3", 1.75)]
                cells = " ".join(f"{s:>10.1f}" if s is not None else f"{'.':>10}"
                                 for s in segs)
                print(f"  {cat:<12}{cells}")


# --------------------------------------------------------------------------
# Test B: within-gig price ~ reviews
# --------------------------------------------------------------------------
def build_reputation_panel():
    """{(seller,slug): {quarter: (median price, median review_count)}} + category."""
    item_map = {}
    with open(PILOT / "gig-items.csv") as f:
        for row in csv.DictReader(f):
            item_map[(row["seller"], row["slug"])] = (row["item_label"], row["description"])

    raw = defaultdict(lambda: defaultdict(lambda: ([], [])))
    gig_cat = {}
    for path, has_items in ((PILOT / "pilot-prices.csv", True),
                            (PILOT / "recent-prices.csv", False)):
        with open(path) as f:
            for row in csv.DictReader(f):
                if not is_gig(row["seller"]):   # /hire/, /agencies/ landing pages
                    continue
                key = (row["seller"], row["slug"])
                try:
                    price = float(row.get("price_basic") or 0)
                except ValueError:
                    continue
                if price <= 0 or price > tpd.PRICE_MAX:
                    continue
                try:
                    rev = float(row.get("review_count") or "")
                except ValueError:
                    continue
                q = tpd.to_quarter(row["year"], row["month"])
                if not q:
                    continue
                raw[key][q][0].append(price)
                raw[key][q][1].append(rev)
                if key not in gig_cat:
                    item = item_map.get(key)
                    if item:
                        gig_cat[key] = tpd.classify_gig(item[1], item[0])
                    else:
                        gig_cat[key] = tpd.classify_gig(row.get("title", ""), "")

    panel = {}
    for key, qs in raw.items():
        panel[key] = {q: (float(np.median(p)), float(np.median(r)))
                      for q, (p, r) in qs.items()}
    return panel, gig_cat


def test_b():
    print("\n" + "=" * 78)
    print("TEST B — the reputation treadmill: within-gig price vs cumulative reviews")
    print("=" * 78)
    panel, gig_cat = build_reputation_panel()
    print(f"gigs with price+reviews: {len(panel)}")

    # adjacent-quarter within-gig first differences
    rows = []   # (cat, q_prev, q_curr, dlnp, dlnrev, years)
    for key, qs in panel.items():
        cat = gig_cat.get(key)
        if cat not in CATS:
            continue
        order = sorted(qs, key=tpd.q_to_int)
        for a, b in zip(order, order[1:]):
            pa, ra = qs[a]
            pb, rb = qs[b]
            if pa <= 0 or pb <= 0:
                continue
            dt = (tpd.q_to_int(b) - tpd.q_to_int(a))
            years = ((int(b[:4]) - int(a[:4])) * 4 + (int(b[-1]) - int(a[-1]))) / 4
            if years <= 0:
                continue
            rows.append((cat, a, b,
                         math.log(pb) - math.log(pa),
                         math.log1p(rb) - math.log1p(ra),
                         years))

    print(f"within-gig transitions: {len(rows)}")
    dlnp = np.array([r[3] for r in rows])
    dlnr = np.array([r[4] for r in rows])
    print(f"mean dln(price) per transition : {dlnp.mean():+.4f}")
    print(f"mean dln(1+reviews)            : {dlnr.mean():+.4f}")
    print(f"share of transitions with reviews growing: "
          f"{(dlnr > 0).mean():.1%}")

    # pooled first-difference regression with quarter-pair (time) fixed effects:
    # dlnp = beta * dlnr + tau_{q_curr} + e   -- tau absorbs any common shock
    # (inflation, platform-wide repricing, macro) in that quarter.
    quarters = sorted({r[2] for r in rows}, key=tpd.q_to_int)
    qidx = {q: i for i, q in enumerate(quarters)}
    X = np.zeros((len(rows), 1 + len(quarters)))
    X[:, 0] = dlnr
    for i, r in enumerate(rows):
        X[i, 1 + qidx[r[2]]] = 1.0
    coef, *_ = np.linalg.lstsq(X, dlnp, rcond=None)
    beta = coef[0]
    resid = dlnp - X @ coef
    dof = len(rows) - np.linalg.matrix_rank(X)
    sigma2 = resid @ resid / dof
    XtX_inv = np.linalg.pinv(X.T @ X)
    se_beta = math.sqrt(sigma2 * XtX_inv[0, 0])
    print(f"\npooled FD + quarter-FE:  beta(dln reviews) = {beta:+.4f} "
          f"(se {se_beta:.4f}, t={beta/se_beta:.2f})")
    print(f"  => a doubling of a gig's review count moves its price "
          f"{100*(math.exp(beta*math.log(2))-1):+.1f}%")

    # per-category
    print(f"\n  {'cat':<12} {'n':>6} {'beta':>8} {'se':>7} {'t':>6} "
          f"{'mean dlnR':>10} {'repu part of dlnP':>19}")
    for cat in CATS:
        sub = [r for r in rows if r[0] == cat]
        if len(sub) < 50:
            continue
        y = np.array([r[3] for r in sub])
        x = np.array([r[4] for r in sub])
        qs = sorted({r[2] for r in sub}, key=tpd.q_to_int)
        qi = {q: i for i, q in enumerate(qs)}
        Xc = np.zeros((len(sub), 1 + len(qs)))
        Xc[:, 0] = x
        for i, r in enumerate(sub):
            Xc[i, 1 + qi[r[2]]] = 1.0
        c, *_ = np.linalg.lstsq(Xc, y, rcond=None)
        res = y - Xc @ c
        d = len(sub) - np.linalg.matrix_rank(Xc)
        s2 = res @ res / d
        se = math.sqrt(s2 * np.linalg.pinv(Xc.T @ Xc)[0, 0])
        share = (c[0] * x.mean() / y.mean() * 100) if y.mean() != 0 else float("nan")
        print(f"  {cat:<12} {len(sub):>6} {c[0]:>8.4f} {se:>7.4f} "
              f"{c[0]/se:>6.2f} {x.mean():>10.4f} {share:>18.1f}%")

    return rows, beta


# --------------------------------------------------------------------------
# Test B2: hedonic-adjusted GEKS — strip the reputation component out
# --------------------------------------------------------------------------
def test_b2(beta):
    print("\n" + "=" * 78)
    print(f"TEST B2 — GEKS on reputation-adjusted prices  ln p - {beta:.4f}*ln(1+reviews)")
    print("=" * 78)
    panel, gig_cat = build_reputation_panel()

    adj = defaultdict(dict)
    raw_p = defaultdict(dict)
    for key, qs in panel.items():
        cat = gig_cat.get(key)
        if cat not in CATS:
            continue
        for q, (p, r) in qs.items():
            adj[cat].setdefault(key, {})[q] = math.exp(math.log(p) - beta * math.log1p(r))
            raw_p[cat].setdefault(key, {})[q] = p

    rng = np.random.default_rng(7)
    print(f"\n{'cat':<12} {'raw 24Q3':>10} {'adj 24Q3':>10} "
          f"{'raw 26Q1':>10} {'adj 26Q1':>10}")
    for cat in CATS:
        if cat not in adj:
            continue
        i_raw, _, _ = geks.geks_index(raw_p[cat], rng=rng, n_boot=0,
                                      window_start="2020Q1")
        i_adj, _, _ = geks.geks_index(adj[cat], rng=rng, n_boot=0,
                                      window_start="2020Q1")
        if not i_raw or not i_adj:
            continue
        cells = []
        for q in ("2024Q3", "2026Q1"):
            cells.append(f"{i_raw.get(q, float('nan')):10.1f}")
            cells.append(f"{i_adj.get(q, float('nan')):10.1f}")
        print(f"{cat:<12} {cells[0]} {cells[1]} {cells[2]} {cells[3]}")


def test_a2():
    print("=" * 78)
    print("TEST A2 — the pre-AI path in full (window 2018Q1, base = first identified qtr)")
    print("=" * 78)
    panel = tpd.build_panel_historical()
    rng = np.random.default_rng(7)
    qs_show = ["2018Q1", "2018Q2", "2018Q3", "2018Q4",
               "2019Q1", "2019Q2", "2019Q3", "2019Q4",
               "2020Q1", "2020Q2"]
    print(f"{'cat':<12} {'base':>7} " + " ".join(f"{q[2:]:>7}" for q in qs_show))
    pre = {}
    for cat in CATS:
        pc = panel.get(cat, {})
        if not pc:
            continue
        idx, _, _ = geks.geks_index(pc, rng=rng, n_boot=0, window_start="2018Q1")
        if not idx:
            print(f"{cat:<12} {'-- none --'}")
            continue
        base = min(idx, key=tpd.q_to_int)
        cells = " ".join(f"{idx[q]:7.1f}" if q in idx else f"{'.':>7}" for q in qs_show)
        print(f"{cat:<12} {base:>7} {cells}")
        pre[cat] = (base, idx)

    print("\n  pre-AI growth, base quarter -> 2019Q4, annualised:")
    for cat, (base, idx) in pre.items():
        if "2019Q4" not in idx:
            continue
        yrs = ((2019 - int(base[:4])) * 4 + (4 - int(base[-1]))) / 4
        if yrs <= 0:
            continue
        g = 100 * ((idx["2019Q4"] / 100.0) ** (1 / yrs) - 1)
        print(f"    {cat:<12} {base} -> 2019Q4 ({yrs:.2f}y): {g:+6.1f}%/yr")


def test_c():
    print("\n" + "=" * 78)
    print("TEST C — entry prices of NEW gigs vs the matched-model index")
    print("=" * 78)
    item_map = {}
    with open(PILOT / "gig-items.csv") as f:
        for row in csv.DictReader(f):
            item_map[(row["seller"], row["slug"])] = (row["item_label"], row["description"])

    # first observation of every gig, with its review count at first sight
    first = {}
    gig_cat = {}
    for path in (PILOT / "pilot-prices.csv", PILOT / "recent-prices.csv"):
        with open(path) as f:
            for row in csv.DictReader(f):
                if not is_gig(row["seller"]):   # /hire/, /agencies/ landing pages
                    continue
                key = (row["seller"], row["slug"])
                try:
                    price = float(row.get("price_basic") or 0)
                except ValueError:
                    continue
                if price <= 0 or price > tpd.PRICE_MAX:
                    continue
                d = row["date"]
                q = tpd.to_quarter(row["year"], row["month"])
                if not q:
                    continue
                try:
                    rev = float(row.get("review_count") or "")
                except ValueError:
                    rev = float("nan")
                if key not in first or d < first[key][0]:
                    first[key] = (d, q, price, rev)
                if key not in gig_cat:
                    item = item_map.get(key)
                    gig_cat[key] = (tpd.classify_gig(item[1], item[0]) if item
                                    else tpd.classify_gig(row.get("title", ""), ""))

    # "young" entrants only: first seen with few reviews => genuinely new, not a
    # veteran gig that the crawler simply happened to catch late.
    for max_rev in (10, 25):
        print(f"\n--- entrants with <= {max_rev} reviews at first capture "
              f"(median entry price, USD) ---")
        buckets = defaultdict(lambda: defaultdict(list))
        for key, (d, q, price, rev) in first.items():
            cat = gig_cat.get(key)
            if cat not in CATS:
                continue
            if not (rev == rev) or rev > max_rev:
                continue
            buckets[cat][q[:4]].append(price)
        years = [str(y) for y in range(2018, 2027)]
        print(f"{'cat':<12} " + " ".join(f"{y[2:]:>12}" for y in years))
        for cat in CATS:
            cells = []
            for y in years:
                v = buckets[cat].get(y, [])
                cells.append(f"{np.median(v):6.0f}(n{len(v):>3})" if len(v) >= 5
                             else f"{'.':>12}")
            print(f"{cat:<12} " + " ".join(cells))

    # all entrants regardless of review count, for coverage comparison
    print("\n--- ALL first-captures (median entry price) ---")
    buckets = defaultdict(lambda: defaultdict(list))
    for key, (d, q, price, rev) in first.items():
        cat = gig_cat.get(key)
        if cat in CATS:
            buckets[cat][q[:4]].append(price)
    years = [str(y) for y in range(2018, 2027)]
    print(f"{'cat':<12} " + " ".join(f"{y[2:]:>12}" for y in years))
    for cat in CATS:
        cells = []
        for y in years:
            v = buckets[cat].get(y, [])
            cells.append(f"{np.median(v):6.0f}(n{len(v):>3})" if len(v) >= 5
                         else f"{'.':>12}")
        print(f"{cat:<12} " + " ".join(cells))



if __name__ == "__main__":
    test_a()
    test_a2()
    rows, beta = test_b()
    test_b2(beta)
    test_c()
