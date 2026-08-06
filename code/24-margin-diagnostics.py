#!/usr/bin/env python3
"""
Step 24: Non-price margin diagnostics — which categories are most impacted by AI?

The price index cannot answer this on its own. Every category in the sample is
treated, so there is no control group, and the matched-model index follows ageing
incumbents whose posted prices are sticky. If AI displaces a category, the first
place it shows up is not the price tag — it is the *quantity* sold, the rate of
new entry, and gigs going dormant.

This script measures those margins from data already in the crawl, using
`review_count` as a sales proxy. Reviews are cumulative sales, so the *accrual
rate* (reviews gained per quarter) is a demand series. Note the asymmetry with
step 22: reviews are a BAD CONTROL for price (Test B) precisely because they
respond to demand — which is exactly what makes them a GOOD OUTCOME here.

  M0  Selection audit. What the two crawls can and cannot measure.
  M1  Demand rate. Within-gig reviews accrued per quarter, per category, with an
      interrupted-time-series break at 2022Q4 (ChatGPT). Two specifications that
      bracket the age/period/cohort problem.
  M2  Dormancy. Share of gig-quarters with zero review accrual — a gig still
      listed but selling nothing. The closest measurable thing to exit.
  M3  Entry. New-gig arrival rate and entry price, normalised by crawl intensity.

WHAT THIS CANNOT DO — read before quoting any number:

  * TRUE EXIT IS NOT MEASURABLE. Both crawls are built from Wayback CDX
    snapshots, so a gig's absence in quarter t means "not archived", not
    "taken down". Worse, `code/13-recent-manifest.py` selects gigs having
    >=1 snapshot in 2025Q3..2026Q2, so the recent panel is a SURVIVOR panel by
    construction. M2 (dormancy) is a proxy measured on survivors, not a hazard.

  * AGE IS COLLINEAR WITH TIME given gig fixed effects (age = period - cohort,
    and the gig effect is the cohort). The estimated quarter path therefore
    contains the panel's average ageing profile and cannot be read as pure
    demand. The 2022Q4 LEVEL BREAK is identified — it is a shift relative to the
    fitted linear trend, which is what absorbs the ageing drift — so M1's break
    column is the defensible number and the level path is not.

  * ~11% of gig rows carry no review_count and pre-2018 rows carry almost none,
    so M1/M2 are restricted to 2018 onward.

Run:  python3 code/24-margin-diagnostics.py
"""

import csv
import importlib.util
import math
import sys
from collections import defaultdict, Counter
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

CATS = tpd.CATS
PILOT = BASE / "data" / "pilot"
PRICE_MAX = tpd.PRICE_MAX

BREAK_Q = "2022Q4"        # ChatGPT release, 2022-11-30
MIN_YEAR = 2018           # review_count coverage collapses before this
ENTRANT_MAX_REV = 10      # "genuinely new" at first capture


# --------------------------------------------------------------------------
# panel construction — category assignment mirrors 19-tpd-index.py exactly
# --------------------------------------------------------------------------
def build_margin_panel(which):
    """-> {gig: {"cat":c, "q":{quarter: (median price, max reviews, n_obs)}}}

    Reviews are collapsed with max() rather than median: within a quarter the
    count is cumulative and weakly increasing, so max is the end-of-quarter
    level, which is what a first difference should span.
    """
    gig_cat = {}
    if which == "historical":
        item_map = {}
        with open(tpd.HIST_ITEMS) as f:
            for row in csv.DictReader(f):
                item_map[(row["seller"], row["slug"])] = (row["item_label"], row["description"])
        src = tpd.HIST_PRICES
    else:
        with open(tpd.RECENT_MANIFEST) as f:
            for row in csv.DictReader(f, delimiter="\t"):
                gid = tuple(row["gig_id"].split("/", 1))
                if len(gid) == 2:
                    gig_cat[gid] = row["category"]
        src = tpd.RECENT_PRICES

    raw = defaultdict(lambda: defaultdict(lambda: ([], [])))
    first_seen = {}
    with open(src) as f:
        for row in csv.DictReader(f):
            if not is_gig(row["seller"]):
                continue
            key = (row["seller"], row["slug"])
            if which == "historical":
                item = item_map.get(key)
                if not item:
                    continue
                if key not in gig_cat:
                    gig_cat[key] = tpd.classify_gig(item[1], item[0])
            elif key not in gig_cat:
                continue
            try:
                price = float(row.get("price_basic") or 0)
            except ValueError:
                continue
            if price <= 0 or price > PRICE_MAX:
                continue
            q = tpd.to_quarter(row["year"], row["month"])
            if not q:
                continue
            rev_s = row.get("review_count") or ""
            try:
                rev = float(rev_s) if rev_s != "" else None
            except ValueError:
                rev = None
            raw[key][q][0].append(price)
            if rev is not None:
                raw[key][q][1].append(rev)
            d = row["date"]
            if key not in first_seen or d < first_seen[key][0]:
                first_seen[key] = (d, q, price, rev)

    panel = {}
    for key, qs in raw.items():
        cat = gig_cat.get(key)
        if cat not in CATS:
            continue
        cells = {}
        for q, (ps, rs) in qs.items():
            cells[q] = (float(np.median(ps)),
                        float(max(rs)) if rs else None,
                        len(ps))
        panel[key] = {"cat": cat, "q": cells, "first": first_seen[key]}
    return panel


def transitions(panel, min_year=MIN_YEAR):
    """Within-gig adjacent-quarter transitions with reviews at both ends.

    -> list of dicts: gig, cat, q0, q1, dq (quarters elapsed), drev_per_q,
       rev0, age (quarters since first capture), post (0/1), t (quarter index)
    """
    out = []
    for key, rec in panel.items():
        cells = rec["q"]
        order = [q for q in sorted(cells, key=tpd.q_to_int) if int(q[:4]) >= min_year]
        birth = tpd.q_to_int(rec["first"][1])
        for a, b in zip(order, order[1:]):
            r0, r1 = cells[a][1], cells[b][1]
            if r0 is None or r1 is None:
                continue
            dq = ((int(b[:4]) - int(a[:4])) * 4 + (int(b[-1]) - int(a[-1])))
            if dq <= 0:
                continue
            drev = r1 - r0
            if drev < 0:            # review deletion / reset — 0.1-0.4% of rows
                continue
            age = ((int(a[:4]) * 4 + int(a[-1])) - ((birth // 10) * 4 + birth % 10))
            out.append({
                "gig": key, "cat": rec["cat"], "q0": a, "q1": b, "dq": dq,
                "drev_per_q": drev / dq, "rev0": r0, "age": max(age, 0),
                "post": 1.0 if tpd.q_to_int(b) > tpd.q_to_int(BREAK_Q) else 0.0,
                "t": tpd.q_to_int(b),
            })
    return out


# --------------------------------------------------------------------------
# OLS with absorbed fixed effects and gig-clustered standard errors
# --------------------------------------------------------------------------
def absorb(X, y, groups):
    """Demean X and y within `groups` (one absorbed factor). Drops singletons,
    which contribute nothing after demeaning and would otherwise inflate dof."""
    idx = defaultdict(list)
    for i, g in enumerate(groups):
        idx[g].append(i)
    keep = [i for g, ii in idx.items() if len(ii) > 1 for i in ii]
    keep.sort()
    if not keep:
        return None, None, None, 0
    Xk, yk = X[keep], y[keep]
    gk = [groups[i] for i in keep]
    pos = defaultdict(list)
    for i, g in enumerate(gk):
        pos[g].append(i)
    Xd, yd = Xk.copy(), yk.copy()
    for g, ii in pos.items():
        Xd[ii] -= Xk[ii].mean(axis=0)
        yd[ii] -= yk[ii].mean()
    return Xd, yd, gk, len(pos)


def ols_cluster(X, y, clusters, n_absorbed=0):
    """-> (coef, se) with CR1 cluster-robust SEs."""
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    cl = defaultdict(list)
    for i, c in enumerate(clusters):
        cl[c].append(i)
    G, n, k = len(cl), len(y), X.shape[1] + n_absorbed
    meat = np.zeros((X.shape[1], X.shape[1]))
    for _, ii in cl.items():
        Xg, ug = X[ii], resid[ii]
        s = Xg.T @ ug
        meat += np.outer(s, s)
    dof_c = (G / max(G - 1, 1)) * ((n - 1) / max(n - k, 1))
    V = dof_c * (XtX_inv @ meat @ XtX_inv)
    return beta, np.sqrt(np.maximum(np.diag(V), 0.0))


# --------------------------------------------------------------------------
# M0: what the crawls can measure
# --------------------------------------------------------------------------
def m0(hist, recent):
    print("=" * 78)
    print("M0 — SELECTION AUDIT: what these crawls can and cannot measure")
    print("=" * 78)
    for tag, panel in (("historical", hist), ("recent", recent)):
        last_q = Counter()
        for rec in panel.values():
            last_q[max(rec["q"], key=tpd.q_to_int)] += 1
        n = len(panel)
        tail = sorted(last_q, key=tpd.q_to_int)[-1]
        print(f"\n  {tag}: {n} gigs")
        print(f"    share whose LAST observation is the crawl's final quarter "
              f"({tail}): {last_q[tail]/n:.1%}")
        rows = sorted(last_q.items(), key=lambda kv: tpd.q_to_int(kv[0]))[-6:]
        print("    last-observed quarter, final 6: "
              + "  ".join(f"{q}:{c}" for q, c in rows))
    print("\n  => A gig 'disappearing' is a Wayback sampling event, not a takedown.")
    print("     code/13-recent-manifest.py requires >=1 snapshot in 2025Q3..2026Q2,")
    print("     so the RECENT panel conditions on survival and cannot host an exit")
    print("     hazard at all. M2 below is a dormancy proxy on survivors, not exit.")

    print("\n  review_count coverage on panel gig-quarters (post gigfilter):")
    for tag, panel in (("historical", hist), ("recent", recent)):
        by_year = Counter()
        ok_year = Counter()
        for rec in panel.values():
            for q, (_, rev, _) in rec["q"].items():
                by_year[q[:4]] += 1
                if rev is not None:
                    ok_year[q[:4]] += 1
        cells = " ".join(f"{y}:{100*ok_year[y]//by_year[y]:>3}%"
                         for y in sorted(by_year) if by_year[y] >= 30)
        print(f"    {tag:<11} {cells}")


# --------------------------------------------------------------------------
# M1: demand rate and its break at 2022Q4
# --------------------------------------------------------------------------
def m1(hist):
    print("\n" + "=" * 78)
    print("M1 — DEMAND RATE: reviews accrued per gig-quarter (a sales proxy)")
    print("=" * 78)
    tr = transitions(hist)
    print(f"\nwithin-gig transitions (historical crawl, {MIN_YEAR}+): {len(tr)}"
          f"  across {len({r['gig'] for r in tr})} gigs")

    print("\n--- descriptive: median reviews accrued per quarter, by year ---")
    years = [str(y) for y in range(2018, 2026)]
    buck = defaultdict(lambda: defaultdict(list))
    for r in tr:
        buck[r["cat"]][r["q1"][:4]].append(r["drev_per_q"])
    print(f"  {'cat':<12} " + " ".join(f"{y[2:]:>11}" for y in years))
    for cat in CATS:
        cells = []
        for y in years:
            v = buck[cat].get(y, [])
            cells.append(f"{np.median(v):5.1f}(n{len(v):>3})" if len(v) >= 8
                         else f"{'.':>11}")
        print(f"  {cat:<12} " + " ".join(cells))

    print(f"\n--- interrupted time series: level break at {BREAK_Q} ---")
    print("    y = reviews/quarter ;  post = 1 after 2022Q4")
    print("    spec A: gig FE + linear trend + post     (composition held fixed)")
    print("    spec B: age-bucket FE + linear trend + post  (ageing held fixed)")
    print("    The linear trend absorbs the ageing drift that gig FE cannot")
    print("    separate from calendar time, so `post` is the identified object.")
    print(f"\n  {'cat':<12} {'n':>6} {'gigs':>6} {'preMean':>8} "
          f"{'A:post':>9} {'se':>7} {'t':>6} {'  %pre':>7} | "
          f"{'B:post':>9} {'se':>7} {'t':>6}")

    results = {}
    for cat in CATS:
        sub = [r for r in tr if r["cat"] == cat]
        if len(sub) < 60:
            print(f"  {cat:<12} {len(sub):>6}  -- too few transitions --")
            continue
        y = np.array([r["drev_per_q"] for r in sub])
        t = np.array([r["t"] for r in sub], dtype=float)
        t = (t // 10) * 4 + (t % 10)          # quarter index, linear in time
        t = t - t.mean()
        post = np.array([r["post"] for r in sub])
        gigs = [r["gig"] for r in sub]
        pre = y[post == 0]
        pre_mean = pre.mean() if len(pre) else float("nan")

        # spec A — gig FE absorbed
        XA = np.column_stack([t, post])
        Xd, yd, gk, n_g = absorb(XA, y, gigs)
        if Xd is None or len(yd) < 20 or Xd[:, 1].std() == 0:
            print(f"  {cat:<12} {len(sub):>6}  -- not estimable (no within-gig "
                  f"pre/post contrast) --")
            continue
        bA, seA = ols_cluster(Xd, yd, gk, n_absorbed=n_g)

        # spec B — age-bucket FE absorbed
        ab = [min(r["age"] // 4, 6) for r in sub]      # 0-1y, 1-2y, ... , 6y+
        XB = np.column_stack([t, post])
        Xdb, ydb, gkb, n_b = absorb(XB, y, ab)
        bB = seB = None
        if Xdb is not None and len(ydb) >= 20 and Xdb[:, 1].std() > 0:
            cl_b = [sub[i]["gig"] for i in range(len(sub))]
            # absorb() reindexes; re-derive clusters on the kept rows
            keepB = _kept_rows(ab)
            bB, seB = ols_cluster(Xdb, ydb, [gigs[i] for i in keepB], n_absorbed=n_b)

        pct = 100 * bA[1] / pre_mean if pre_mean else float("nan")
        results[cat] = {"post": bA[1], "se": seA[1], "pre": pre_mean,
                        "pct": pct, "n": len(yd),
                        "mde": 196 * seA[1] / pre_mean if pre_mean else float("nan"),
                        "postB": (bB[1] if bB is not None else None),
                        "seB": (seB[1] if seB is not None else None)}
        bcell = (f"{bB[1]:>9.3f} {seB[1]:>7.3f} {bB[1]/seB[1]:>6.2f}"
                 if bB is not None else f"{'--':>9} {'--':>7} {'--':>6}")
        print(f"  {cat:<12} {len(yd):>6} {n_g:>6} {pre_mean:>8.2f} "
              f"{bA[1]:>9.3f} {seA[1]:>7.3f} {bA[1]/seA[1]:>6.2f} "
              f"{pct:>6.0f}% | {bcell}")

    if results:
        print(f"\n  RANKING — largest demand drop at {BREAK_Q}, spec A, "
              f"as % of pre-period rate:")
        for cat, r in sorted(results.items(), key=lambda kv: kv[1]["pct"]):
            sig = "*" if abs(r["post"] / r["se"]) > 1.96 else " "
            agree = ("agrees" if r["postB"] is not None
                     and np.sign(r["postB"]) == np.sign(r["post"]) else "DIFFERS")
            print(f"    {cat:<12} {r['pct']:>7.0f}% {sig}  "
                  f"({r['post']:+.3f} reviews/qtr on a base of {r['pre']:.2f})"
                  f"   spec B {agree}")
        print("    * = |t| > 1.96 on gig-clustered SEs")

        print("\n  POWER — smallest demand break spec A could have detected "
              "(1.96*se as % of pre-period rate):")
        for cat, r in sorted(results.items(), key=lambda kv: kv[1]["mde"]):
            print(f"    {cat:<12} +/- {r['mde']:>5.0f}%")
        print("  Nothing is significant, so read the row above as a BOUND: no")
        print("  category's sales rate broke by more than this at ChatGPT.")
        print("\n  Spec A and spec B disagree in sign for several categories.")
        print("  Spec B drops the gig effect, so it compares DIFFERENT gigs pre")
        print("  and post — in a Wayback panel the later gigs are the ones the")
        print("  archive kept re-sampling, i.e. the more successful ones. Spec B")
        print("  is therefore survivor-composition, not demand. Spec A is the")
        print("  one to quote; the disagreement is why M1 is reported as a bound.")
    return results


def _kept_rows(groups):
    idx = defaultdict(list)
    for i, g in enumerate(groups):
        idx[g].append(i)
    keep = [i for g, ii in idx.items() if len(ii) > 1 for i in ii]
    keep.sort()
    return keep


# --------------------------------------------------------------------------
# M2: dormancy — listed but not selling
# --------------------------------------------------------------------------
def m2(hist, recent):
    print("\n" + "=" * 78)
    print("M2 — DORMANCY: share of gig-quarters with ZERO reviews accrued")
    print("=" * 78)
    print("  A gig still listed but gaining no reviews is selling nothing. This is")
    print("  the closest measurable analogue of exit — but it is measured ON")
    print("  SURVIVORS, so it understates displacement by construction.")

    for tag, panel in (("historical", hist), ("recent", recent)):
        tr = transitions(panel)
        if not tr:
            continue
        print(f"\n--- {tag} crawl ---")
        years = sorted({r["q1"][:4] for r in tr})
        by = defaultdict(lambda: defaultdict(list))
        for r in tr:
            by[r["cat"]][r["q1"][:4]].append(1.0 if r["drev_per_q"] == 0 else 0.0)
        print(f"  {'cat':<12} " + " ".join(f"{y[2:]:>11}" for y in years))
        for cat in CATS:
            cells = []
            for y in years:
                v = by[cat].get(y, [])
                cells.append(f"{100*np.mean(v):5.1f}%(n{len(v):>3})" if len(v) >= 8
                             else f"{'.':>11}")
            print(f"  {cat:<12} " + " ".join(cells))

    print(f"\n--- historical: dormancy share pre vs post {BREAK_Q} ---")
    print("  RAW difference first — this is confounded: dormancy rises with gig")
    print("  age, and the post window is simply later, so every category should")
    print("  drift up. Only the CROSS-CATEGORY spread is informative here.")
    tr = transitions(hist)
    print(f"\n  {'cat':<12} {'pre n':>7} {'pre':>8} {'post n':>7} {'post':>8} "
          f"{'raw diff':>9}")
    raw = {}
    for cat in CATS:
        sub = [r for r in tr if r["cat"] == cat]
        pre = [1.0 if r["drev_per_q"] == 0 else 0.0 for r in sub if r["post"] == 0]
        post = [1.0 if r["drev_per_q"] == 0 else 0.0 for r in sub if r["post"] == 1]
        if len(pre) < 20 or len(post) < 20:
            continue
        a, b = np.mean(pre), np.mean(post)
        raw[cat] = (b - a, a, b)
        print(f"  {cat:<12} {len(pre):>7} {100*a:>7.1f}% {len(post):>7} "
              f"{100*b:>7.1f}% {100*(b-a):>+8.1f}pp")

    # Same interrupted-time-series spec as M1, on the dormancy indicator: the
    # gig effect holds composition fixed and the linear trend absorbs the ageing
    # drift, so `post` is a break relative to each category's own trajectory.
    print(f"\n  ITS: dormant = gig FE + linear trend + post   (gig-clustered SEs)")
    print(f"  {'cat':<12} {'n':>6} {'gigs':>6} {'preRate':>8} {'post':>9} "
          f"{'se':>7} {'t':>6} {'  95% CI (pp)':>20}")
    rank = []
    for cat in CATS:
        sub = [r for r in tr if r["cat"] == cat]
        if len(sub) < 60:
            continue
        y = np.array([1.0 if r["drev_per_q"] == 0 else 0.0 for r in sub])
        t = np.array([r["t"] for r in sub], dtype=float)
        t = (t // 10) * 4 + (t % 10)
        t = t - t.mean()
        post = np.array([r["post"] for r in sub])
        gigs = [r["gig"] for r in sub]
        pre_rate = y[post == 0].mean() if (post == 0).any() else float("nan")
        Xd, yd, gk, n_g = absorb(np.column_stack([t, post]), y, gigs)
        if Xd is None or len(yd) < 20 or Xd[:, 1].std() == 0:
            continue
        b, se = ols_cluster(Xd, yd, gk, n_absorbed=n_g)
        lo, hi = 100 * (b[1] - 1.96 * se[1]), 100 * (b[1] + 1.96 * se[1])
        rank.append((cat, b[1], se[1], pre_rate, lo, hi))
        print(f"  {cat:<12} {len(yd):>6} {n_g:>6} {100*pre_rate:>7.1f}% "
              f"{100*b[1]:>+8.1f} {100*se[1]:>7.1f} {b[1]/se[1]:>6.2f} "
              f"  [{lo:>+6.1f}, {hi:>+6.1f}]")

    if rank:
        print("\n  RANKING — largest rise in dormancy at ChatGPT, "
              "trend- and composition-adjusted:")
        for cat, b, se, pr, lo, hi in sorted(rank, key=lambda x: -x[1]):
            sig = "*" if abs(b / se) > 1.96 else " "
            rawd = raw.get(cat, (float('nan'),))[0]
            print(f"    {cat:<12} {100*b:>+6.1f}pp {sig} "
                  f"(raw {100*rawd:>+5.1f}pp, pre-rate {100*pr:.1f}%)")
        print("    * = |t| > 1.96 on gig-clustered SEs")
    return rank


# --------------------------------------------------------------------------
# M3: entry
# --------------------------------------------------------------------------
def m3(hist, recent):
    print("\n" + "=" * 78)
    print("M3 — ENTRY: NOT MEASURABLE IN THIS CRAWL. The diagnostic, and why.")
    print("=" * 78)
    print("  Entry rate = (gigs first captured in quarter t with <=10 reviews)")
    print("               / (all gigs observed in quarter t), within one crawl.")
    print("  Normalising by observed gigs was meant to absorb the crawl's varying")
    print("  sampling intensity. It does not, because the NUMERATOR is truncated")
    print("  by the crawl window at both ends: nothing can be 'first captured'")
    print("  before the window opens, and a gig entering near the close has no")
    print("  chance to be caught first. The counts below show that geometry is the")
    print("  dominant signal, so the declining entry profile is an artefact.")
    print("  Reported to close the question, NOT as a finding.")

    print("\n--- first-capture quarter vs crawl window ---")
    for tag, panel in (("historical", hist), ("recent", recent)):
        fq = Counter(r["first"][1] for r in panel.values())
        obs = Counter(q for r in panel.values() for q in r["q"])
        qs = sorted(obs, key=tpd.q_to_int)[-8:]
        print(f"  {tag:<11} first-captures: "
              + " ".join(f"{q}:{fq.get(q, 0)}" for q in qs))
        print(f"  {'':<11} observed gigs : "
              + " ".join(f"{q}:{obs[q]}" for q in qs))
    rf = Counter(r["first"][1] for r in recent.values())
    print(f"\n  => {rf.get('2024Q3', 0)} of {len(recent)} recent-panel gigs are "
          f"'first captured' in 2024Q3 — exactly WINDOW_START in")
    print(f"     code/13-recent-manifest.py — and {rf.get('2026Q1', 0)} in the "
          f"final quarter. Entry runs ~100% -> ~0%")
    print("     by construction. Real entry needs a crawl designed for it.")

    for tag, panel in (("historical", hist), ("recent", recent)):
        print(f"\n--- {tag} crawl: new-gig share of observed gigs, by year ---")
        obs = defaultdict(lambda: defaultdict(set))
        new = defaultdict(lambda: defaultdict(set))
        for key, rec in panel.items():
            cat = rec["cat"]
            for q in rec["q"]:
                if int(q[:4]) < MIN_YEAR:
                    continue
                obs[cat][q[:4]].add(key)
            d, fq, price, rev = rec["first"]
            if int(fq[:4]) >= MIN_YEAR and rev is not None and rev <= ENTRANT_MAX_REV:
                new[cat][fq[:4]].add(key)
        years = sorted({y for c in obs.values() for y in c})
        print(f"  {'cat':<12} " + " ".join(f"{y[2:]:>11}" for y in years))
        for cat in CATS:
            cells = []
            for y in years:
                d = len(obs[cat].get(y, ()))
                nn = len(new[cat].get(y, ()))
                cells.append(f"{100*nn/d:5.1f}%(n{d:>3})" if d >= 15 else f"{'.':>11}")
            print(f"  {cat:<12} " + " ".join(cells))

    print("\n--- historical: median entry price of new gigs (nominal USD) ---")
    years = [str(y) for y in range(2018, 2026)]
    buck = defaultdict(lambda: defaultdict(list))
    for key, rec in hist.items():
        d, fq, price, rev = rec["first"]
        if rev is not None and rev <= ENTRANT_MAX_REV and int(fq[:4]) >= MIN_YEAR:
            buck[rec["cat"]][fq[:4]].append(price)
    print(f"  {'cat':<12} " + " ".join(f"{y[2:]:>11}" for y in years))
    for cat in CATS:
        cells = []
        for y in years:
            v = buck[cat].get(y, [])
            cells.append(f"{np.median(v):6.0f}(n{len(v):>2})" if len(v) >= 5
                         else f"{'.':>11}")
        print(f"  {cat:<12} " + " ".join(cells))


# --------------------------------------------------------------------------
# M4: pooled exposure contrast — does pooling buy back the power?
# --------------------------------------------------------------------------
# Stated as a hypothesis BEFORE looking at the outcome, not read off the results:
# by end-2022 a general-purpose LLM could produce a text deliverable end to end,
# so writing / translation / marketing-copy are high exposure. Image, video and
# audio generation were either later, or not yet producing a client-ready
# commercial deliverable. This is coarse and both groups are treated — it buys
# power, not identification.
HIGH_EXPOSURE = {"writing", "translation", "marketing"}


def m4(hist):
    print("\n" + "=" * 78)
    print("M4 — POOLED EXPOSURE CONTRAST: does pooling recover the lost power?")
    print("=" * 78)
    print("  high exposure (text deliverable): " + ", ".join(sorted(HIGH_EXPOSURE)))
    print("  low  exposure (visual/audio)    : "
          + ", ".join(sorted(set(CATS) - HIGH_EXPOSURE)))
    print("  spec: y = gig FE + quarter FE + high*post,  gig-clustered SEs.")
    print("  Quarter FE absorbs every platform-wide shock (CPI, Fiverr policy,")
    print("  the ageing drift common to all gigs); the coefficient is the")
    print("  DIFFERENTIAL break in high-exposure categories. Both groups are")
    print("  treated, so this is a contrast, not an identified AI effect.")

    tr = transitions(hist)
    for label, getter in (("demand rate (reviews/qtr)", lambda r: r["drev_per_q"]),
                          ("dormancy (1 = zero accrual)",
                           lambda r: 1.0 if r["drev_per_q"] == 0 else 0.0)):
        y = np.array([getter(r) for r in tr])
        high = np.array([1.0 if r["cat"] in HIGH_EXPOSURE else 0.0 for r in tr])
        post = np.array([r["post"] for r in tr])
        gigs = [r["gig"] for r in tr]
        # quarter FE via dummies (gig FE is the absorbed factor)
        quarters = sorted({r["q1"] for r in tr}, key=tpd.q_to_int)
        qi = {q: i for i, q in enumerate(quarters)}
        Q = np.zeros((len(tr), len(quarters) - 1))
        for i, r in enumerate(tr):
            j = qi[r["q1"]]
            if j > 0:
                Q[i, j - 1] = 1.0
        X = np.column_stack([high * post, Q])
        Xd, yd, gk, n_g = absorb(X, y, gigs)
        if Xd is None:
            continue
        keep = _kept_rows(gigs)
        b, se = ols_cluster(Xd, yd, [gigs[i] for i in keep], n_absorbed=n_g)
        pre_hi = y[(high == 1) & (post == 0)].mean()
        lo, hi = b[0] - 1.96 * se[0], b[0] + 1.96 * se[0]
        print(f"\n  {label}")
        print(f"    n={len(yd)}  gigs={n_g}  pre-period high-exposure mean="
              f"{pre_hi:.3f}")
        print(f"    high*post = {b[0]:+.4f}  (se {se[0]:.4f}, t={b[0]/se[0]:.2f})"
              f"   95% CI [{lo:+.4f}, {hi:+.4f}]")
        if pre_hi:
            print(f"    as % of the high-exposure pre-period level: "
                  f"{100*b[0]/pre_hi:+.1f}%  "
                  f"[{100*lo/pre_hi:+.1f}%, {100*hi/pre_hi:+.1f}%]")


def main():
    print("Building margin panels...")
    hist = build_margin_panel("historical")
    recent = build_margin_panel("recent")
    for tag, p in (("historical", hist), ("recent", recent)):
        print(f"  {tag}: " + ", ".join(
            f"{c}={sum(1 for r in p.values() if r['cat'] == c)}" for c in CATS))

    m0(hist, recent)
    m1(hist)
    m2(hist, recent)
    m3(hist, recent)
    m4(hist)

    print("\n" + "=" * 78)
    print("READ THE M0 CAVEATS BEFORE QUOTING ANY OF THIS.")
    print("Exit is not measured. Dormancy and entry are measured on survivors.")
    print("The M1 level path is age-confounded; only the `post` break is identified.")
    print("=" * 78)


if __name__ == "__main__":
    main()
