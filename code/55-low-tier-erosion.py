#!/usr/bin/env python3
"""
Step 55: Upwork's under-$500 prediction, tested on our data.

WHY THIS EXISTS. Upwork's Q2-2026 release is the only public statement by an
operator with transaction-level visibility that names a SPECIFIC, TESTABLE
signature of AI substitution: the GSV decline is concentrated in contracts under
$500, because clients now do simple, small tasks with AI instead. Fiverr says the
same thing in different words -- "high-volume, low-value transactional work".

This is a WITHIN-CATEGORY, WITHIN-PLATFORM prediction, so it escapes the two
defects that killed designs I1-I4 and the step-53 lead: it does not need the
seven-category unit count (p-floor 0.143), and its treatment varies across
thousands of gigs rather than across two categories (the Moulton problem that
gate A of step 54 used to kill the lead).

THE PREDICTION. Cheap gigs should lose accrual faster than expensive gigs, and
increasingly so through 2025-2026.

THE KNOWN TRAP, declared before running. Step 49 already ran a within-category
price-tier DiD on the balanced frame and it died TWICE: parallel trends failed
(10/11 pre-period coefficients significant) and the estimate was wrong-signed.
The diagnosed cause was mean reversion -- a gig observed at a low price is partly
low by transitory noise, and reverts. Three guards are therefore built in here and
not added afterwards:

  1. Tier is assigned on the gig's FIRST observed price in the frame and never
     updated, so within-window repricing cannot move a gig between arms.
  2. A PRE-AI PLACEBO WINDOW (2019Q3-2021Q4) runs the identical specification.
     If cheap gigs already eroded faster before generative AI, the recent result
     is mean reversion or a secular trend, not AI.
  3. A CONTINUOUS specification (log price x trend) runs alongside the tier
     split, because a tier cut at an arbitrary threshold can manufacture a
     gradient that a continuous measure will not reproduce.

Category x quarter FE absorb every category-wide shock, so this asks only whether
the CHEAP END of a category eroded faster than the expensive end of the SAME
category in the SAME quarter.

Run:  python3 code/55-low-tier-erosion.py
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
PILOT = BASE / "data" / "pilot"


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, BASE / "code" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m24 = _load("m24", "24-margin-diagnostics.py")
s53 = _load("s53", "53-recent-exposure.py")
ols_cluster = m24.ols_cluster
qi = s53.qi

CATS = {"translation", "writing", "marketing", "coding", "design", "video", "audio"}


def build(prices, manifest):
    """Accrual pairs + the gig's FIRST observed basic price in the frame."""
    cat = {}
    with open(manifest) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            cat[r["gig_id"]] = r["category"]
    raw = defaultdict(lambda: defaultdict(list))
    first_price, first_date, first_q = {}, {}, {}
    with open(prices) as f:
        for r in csv.DictReader(f):
            gid = r["seller"] + "/" + r["slug"]
            c = cat.get(gid)
            if c not in CATS:
                continue
            q = r["year"] + "Q" + str((int(r["month"]) - 1) // 3 + 1)
            try:
                p = float(r.get("price_basic") or "")
            except ValueError:
                p = None
            if p is not None and p > 0:
                if gid not in first_date or r["date"] < first_date[gid]:
                    first_date[gid] = r["date"]
                    first_price[gid] = p
            if gid not in first_q or r["date"] < first_q[gid][0]:
                first_q[gid] = (r["date"], q)
            rv = r.get("review_count") or ""
            if rv == "":
                continue
            try:
                rev = float(rv)
            except ValueError:
                continue
            raw[gid][q].append(rev)
    out = []
    for gid, qs in raw.items():
        if gid not in first_price:
            continue
        cells = {q: max(v) for q, v in qs.items()}
        order = sorted(cells, key=qi)
        birth = qi(first_q[gid][1])
        for a, b in zip(order, order[1:]):
            dq = qi(b) - qi(a)
            drev = cells[b] - cells[a]
            if dq <= 0 or drev < 0:
                continue
            out.append({"gig": gid, "cat": cat[gid], "q1": b, "t": qi(b),
                        "rate": drev / dq, "y": np.log1p(drev / dq),
                        "p0": first_price[gid], "lp0": math.log(first_price[gid]),
                        "age": max(qi(a) - birth, 0)})
    return out


def absorb2(X, y, g1, g2, tol=1e-10, maxit=300):
    i1, i2 = defaultdict(list), defaultdict(list)
    for i, g in enumerate(g1):
        i1[g].append(i)
    for i, g in enumerate(g2):
        i2[g].append(i)
    Z = np.column_stack([X, y]).astype(float)
    for _ in range(maxit):
        prev = Z.copy()
        for ii in i1.values():
            Z[ii] -= Z[ii].mean(axis=0)
        for ii in i2.values():
            Z[ii] -= Z[ii].mean(axis=0)
        if np.max(np.abs(Z - prev)) < tol:
            break
    return Z[:, :-1], Z[:, -1], len(i1) + len(i2) - 1


def est(rows, xfun, label, note=""):
    """y = (x_i x trend) + gig FE + (category x quarter) FE, gig-clustered."""
    if len(rows) < 50:
        print(f"    {label:<34} not estimable (n {len(rows)})")
        return None
    t0 = min(r["t"] for r in rows)
    x = np.array([xfun(r) for r in rows], dtype=float)
    tt = np.array([r["t"] - t0 for r in rows], dtype=float)
    y = np.array([r["y"] for r in rows])
    gigs = [r["gig"] for r in rows]
    cq = [r["cat"] + "|" + r["q1"] for r in rows]
    Xd, yd, nab = absorb2(np.column_stack([x * tt]), y, gigs, cq)
    if np.std(Xd) < 1e-9:
        print(f"    {label:<34} not estimable (no variation)")
        return None
    b, se = ols_cluster(Xd, yd, gigs, n_absorbed=nab)
    t = b[0] / se[0] if se[0] > 0 else np.nan
    print(f"    {label:<34} {b[0]:+8.4f}  (se {se[0]:.4f}, t {t:+6.2f})"
          f"  n {len(rows):>7,}  gigs {len({g for g in gigs}):>6,}  {note}")
    return float(b[0]), float(se[0]), float(t)


def tiers(rows, cuts=(10.0, 25.0, 50.0, 100.0)):
    lab = []
    for r in rows:
        p = r["p0"]
        if p <= cuts[0]:
            lab.append(0)
        elif p <= cuts[1]:
            lab.append(1)
        elif p <= cuts[2]:
            lab.append(2)
        elif p <= cuts[3]:
            lab.append(3)
        else:
            lab.append(4)
    return lab


def hdr(t):
    print("\n" + "=" * 84)
    print(t)
    print("=" * 84)


def main():
    print("=" * 84)
    print("STEP 55 — DID THE CHEAP END ERODE FASTER? (Upwork's under-$500 claim)")
    print("=" * 84)

    recent = build(PILOT / "recent-prices.csv", PILOT / "recent-manifest.tsv")
    bal = build(PILOT / "balanced-prices.csv", PILOT / "balanced-manifest-1200.tsv")

    FRAMES = [
        ("RECENT 2024Q3-2026Q1  <== the AI-attributed period", recent),
        ("BALANCED 2023Q1-2024Q4", [r for r in bal if qi("2023Q1") <= r["t"] <= qi("2024Q4")]),
        ("BALANCED full 2019Q3-2024Q4", [r for r in bal if r["t"] <= qi("2024Q4")]),
        ("BALANCED PRE-AI 2019Q3-2021Q4  <== PLACEBO", [r for r in bal if r["t"] <= qi("2021Q4")]),
    ]

    hdr("A — WHO IS IN THE CHEAP ARM (entry price, fixed at first observation)")
    for name, rows in FRAMES:
        g = {}
        for r in rows:
            g[r["gig"]] = r["p0"]
        if not g:
            continue
        p = np.array(list(g.values()))
        band = [("<=$10", (p <= 10).sum()), ("$11-25", ((p > 10) & (p <= 25)).sum()),
                ("$26-50", ((p > 25) & (p <= 50)).sum()),
                ("$51-100", ((p > 50) & (p <= 100)).sum()), (">$100", (p > 100).sum())]
        print(f"\n  {name}   {len(g):,} gigs, median entry price ${np.median(p):.0f}")
        print("    " + "  ".join(f"{k} {v:,} ({100*v/len(g):.1f}%)" for k, v in band))

    hdr("B — RAW PATHS: mean quarterly accrual by entry-price band")
    for name, rows in FRAMES[:2]:
        lab = tiers(rows)
        byq = defaultdict(lambda: defaultdict(list))
        for r, l in zip(rows, lab):
            byq[r["q1"]][l].append(r["rate"])
        names = ["<=$10", "$11-25", "$26-50", "$51-100", ">$100"]
        print(f"\n  {name}")
        print("    quarter   " + "".join(f"{n:>12}" for n in names))
        for q in sorted(byq, key=qi):
            cells = byq[q]
            row = "".join(
                f"{np.mean(cells[i]):>12.1f}" if len(cells.get(i, [])) >= 5 else f"{'.':>12}"
                for i in range(5))
            print(f"    {q}  {row}")

    hdr("C — THE TEST: does the cheap end lose accrual faster?")
    print("""
  y = (x x trend) + gig FE + (category x quarter) FE, gig-clustered SEs.
  Category x quarter FE means this is a WITHIN-CATEGORY, WITHIN-QUARTER contrast.

  Upwork's prediction: CHEAP falls faster, i.e.
      "cheap (<=$10) x trend"  NEGATIVE
      "log entry price x trend" POSITIVE (dearer gigs do better)""")
    for name, rows in FRAMES:
        print(f"\n  {name}")
        lab = tiers(rows)
        cheap = {id(r): (1.0 if l == 0 else 0.0) for r, l in zip(rows, lab)}
        cheap25 = {id(r): (1.0 if l <= 1 else 0.0) for r, l in zip(rows, lab)}
        est(rows, lambda r: cheap[id(r)], "cheap (<=$10) x trend",
            "NEG = AI-consistent")
        est(rows, lambda r: cheap25[id(r)], "cheap (<=$25) x trend",
            "NEG = AI-consistent")
        est(rows, lambda r: r["lp0"], "log entry price x trend",
            "POS = AI-consistent")
        # top vs bottom only, discarding the middle
        ends = [r for r, l in zip(rows, lab) if l in (0, 4)]
        if ends:
            ce = {id(r): (1.0 if r["p0"] <= 10 else 0.0) for r in ends}
            est(ends, lambda r: ce[id(r)], "cheap x trend, <=$10 vs >$100",
                "NEG = AI-consistent")

    hdr("D — DOSE RESPONSE: trend by entry-price band, band 5 (>$100) as base")
    for name, rows in FRAMES[:3]:
        lab = tiers(rows)
        t0 = min(r["t"] for r in rows)
        tt = np.array([r["t"] - t0 for r in rows], dtype=float)
        cols = []
        used = []
        for k in range(4):
            v = np.array([1.0 if l == k else 0.0 for l in lab])
            if v.sum() >= 50:
                cols.append(v * tt)
                used.append(k)
        if not cols:
            continue
        y = np.array([r["y"] for r in rows])
        gigs = [r["gig"] for r in rows]
        cq = [r["cat"] + "|" + r["q1"] for r in rows]
        Xd, yd, nab = absorb2(np.column_stack(cols), y, gigs, cq)
        b, se = ols_cluster(Xd, yd, gigs, n_absorbed=nab)
        names = ["<=$10", "$11-25", "$26-50", "$51-100"]
        print(f"\n  {name}")
        print("    band        trend vs >$100        t")
        for k, bb, ss in zip(used, b, se):
            print(f"    {names[k]:<10}   {bb:+8.4f}     {bb/ss if ss>0 else float('nan'):+7.2f}")
        print(f"    {'>$100':<10}   {0.0:+8.4f}      (base)")
        print("    AI-consistent pattern = monotone, most negative at <=$10")


    hdr("E — WHERE IS THE BREAK? (searched, not assumed)")
    print("""
  Section C shows the cheap-end differential is POSITIVE pre-2022 and NEGATIVE in
  2023-24: a sign reversal. A reversal is only AI evidence if it happens when AI
  arrived. Every previous break in this project that was SEARCHED rather than
  assumed landed in 2021 (commodity tier 2021Q2, repricing 2021Q3, transaction
  proxy 2020Q4). This searches it.

      y = gig FE + (category x quarter) FE
          + cheap x trend                 (the pre-break differential slope)
          + cheap x max(t - tau, 0)        (the CHANGE in that slope at tau)

  The AI hypothesis names tau = 2022Q4. It is one of 17 candidates here and gets
  no special treatment.""")
    rows = [r for r in bal if r["t"] <= qi("2024Q4")]
    lab = tiers(rows)
    cheapv = np.array([1.0 if l == 0 else 0.0 for l in lab])
    t0 = min(r["t"] for r in rows)
    tt = np.array([r["t"] - t0 for r in rows], dtype=float)
    y = np.array([r["y"] for r in rows])
    gigs = [r["gig"] for r in rows]
    cq = [r["cat"] + "|" + r["q1"] for r in rows]
    cands = [f"{yr}Q{q}" for yr in range(2020, 2025) for q in range(1, 5)]
    cands = [c for c in cands if qi("2020Q2") <= qi(c) <= qi("2024Q2")]
    res = []
    for tau in cands:
        kink = np.maximum(tt - (qi(tau) - t0), 0.0)
        Xd, yd, nab = absorb2(np.column_stack([cheapv * tt, cheapv * kink]),
                              y, gigs, cq)
        b, se = ols_cluster(Xd, yd, gigs, n_absorbed=nab)
        resid = yd - Xd @ b
        res.append((tau, float(b[0]), float(b[1]), float(b[1] / se[1]) if se[1] > 0 else float("nan"),
                    float(resid @ resid)))
    best = min(res, key=lambda r: r[4])
    print("\n    tau       cheap x trend   change at tau        t        SSR   rank")
    order = sorted(res, key=lambda r: r[4])
    rank = {r[0]: i + 1 for i, r in enumerate(order)}
    for tau, b0, b1, t1, ssr in res:
        mark = ""
        if tau == best[0]:
            mark = "  <== BEST"
        if tau == "2022Q4":
            mark += "  <== ChatGPT"
        print(f"    {tau}    {b0:+10.4f}   {b1:+10.4f}  {t1:+7.2f}  {ssr:10.1f}"
              f"  {rank[tau]:>4}{mark}")
    print(f"\n    Best break: {best[0]}.  ChatGPT (2022Q4) ranks "
          f"{rank['2022Q4']} of {len(res)} on SSR.")
    print("    NOTE: 17 candidates, no multiple-testing correction, so the")
    print("    winning t is inflated. Only the LOCATION is read off this.")

    hdr("VERDICT")
    print("""
  Promotion rule, same as step 54: this is reported as a finding only if the sign
  is AI-consistent in the RECENT frame, the dose response in D is monotone, AND
  the PRE-AI PLACEBO frame is clean. A significant placebo means mean reversion,
  which is exactly how step 49's version of this test died.""")


if __name__ == "__main__":
    main()
