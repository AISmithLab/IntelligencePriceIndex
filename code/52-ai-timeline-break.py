#!/usr/bin/env python3
"""
Step 52: WHEN did the transaction proxy turn, and does that date match generative
AI's actual arrival rather than ChatGPT's launch date?

WHY THIS EXISTS. Every demand design in this project (steps 24, 46, 48, 50) tests
a SINGLE PRE-SPECIFIED break at 2022Q4, on the premise that ChatGPT (2022-11-30)
is "the" generative-AI event. That premise is wrong on the history. Production
tools in exactly the categories this market sells were live well before it:

    2020-06  GPT-3 API beta
    2021-02  Jasper/Jarvis  (copywriting -> writing)
    2021-06  GitHub Copilot preview (-> coding)
    2021-11  GPT-3 API general availability
    2022-04  DALL-E 2      (-> design)
    2022-07  Midjourney open beta (-> design)
    2022-08  Stable Diffusion (-> design)
    2022-11  ChatGPT

So "no break at 2022Q4" is a statement about ONE DATE, not about generative AI.
This step searches the break instead of assuming it, exactly as step 51 did for
repricing, and reports where the transaction proxy actually turns.

IDENTIFICATION — read this before quoting anything.
  Review accrual falls as a gig ages. Within a gig, age and calendar time move
  one-for-one, so with gig fixed effects the LINEAR calendar trend is NOT
  separable from the linear ageing profile. This is the age-period-cohort
  problem and it has no solution here.
  What IS identified is the NON-LINEAR calendar component: gigs of different
  cohorts reach calendar quarter c at different ages, so a level shift or a
  slope change AT c is identified off that cohort spread. Age is absorbed as a
  full set of age fixed effects, not a polynomial, so no functional form is
  imposed on the ageing profile.
  => Only break locations and break sizes are reported. No trend is reported.

Outcome, frame and SEs are step 46's, unchanged: within-gig adjacent-quarter
review accrual, log1p, balanced frame, gig-clustered SEs.

Run:  python3 code/52-ai-timeline-break.py
"""

import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "code"))


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, BASE / "code" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m46 = _load("m46", "46-balanced-demand.py")
m24 = _load("m24", "24-margin-diagnostics.py")
ols_cluster = m24.ols_cluster
qi = m46.qi

# Search window. Starts 2020Q2 so at least three quarters of pre-period remain
# inside the frame (which opens 2019Q3 on extraction homogeneity), ends 2023Q4 so
# at least four quarters of post-period remain before the 2024Q4 hard boundary.
SEARCH_LO, SEARCH_HI = "2020Q2", "2023Q4"
WIN_START, WIN_END = "2019Q3", "2024Q4"

AI_TIMELINE = [
    ("2020Q2", "GPT-3 API beta"),
    ("2021Q1", "Jasper/Jarvis (writing)"),
    ("2021Q2", "GitHub Copilot preview (coding)"),
    ("2021Q4", "GPT-3 API general availability"),
    ("2022Q2", "DALL-E 2 (design)"),
    ("2022Q3", "Midjourney + Stable Diffusion (design)"),
    ("2022Q4", "ChatGPT"),
    ("2023Q1", "GPT-4"),
]


def absorb2(X, y, g1, g2, tol=1e-10, maxit=200):
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


def main():
    print("=" * 84)
    print("STEP 52 — SEARCHED BREAK ON THE TRANSACTION PROXY vs THE AI TIMELINE")
    print("=" * 84)

    panel = m46.build_panel()
    rows = m46.transitions(panel, start=WIN_START, end=WIN_END)
    print(f"\n  frame {WIN_START}-{WIN_END}   accrual observations {len(rows):,}"
          f"   gigs {len({r['gig'] for r in rows}):,}")

    # ---------------- P1: the shape, before any model ----------------
    print("\n" + "=" * 84)
    print("P1 — WITHIN-GIG ACCRUAL BY QUARTER (raw, no controls)")
    print("=" * 84)
    byq = defaultdict(list)
    for r in rows:
        byq[r["q1"]].append(r["rate"])
    print("\n  quarter    n      mean reviews/quarter   index(2020Q1=100)")
    base = None
    for q in sorted(byq, key=qi):
        m = float(np.mean(byq[q]))
        if q == "2020Q1":
            base = m
    for q in sorted(byq, key=qi):
        v = byq[q]
        m = float(np.mean(v))
        idx = 100 * m / base if base else float("nan")
        print(f"  {q}   {len(v):6,}          {m:8.3f}            {idx:7.1f}")

    # ---------------- P2: searched level-shift break ----------------
    print("\n" + "=" * 84)
    print("P2 — SEARCHED BREAK, level-shift form")
    print("     y = gig FE + age FE + delta * 1[t > c],  gig-clustered SEs")
    print("=" * 84)

    y = np.array([r["y"] for r in rows])
    gigs = [r["gig"] for r in rows]
    ages = [r["age"] for r in rows]
    t = np.array([qi(r["q1"]) for r in rows], dtype=float)

    cands = [q for q in sorted(byq, key=qi) if qi(SEARCH_LO) <= qi(q) <= qi(SEARCH_HI)]
    results = []
    for c in cands:
        post = (t > qi(c)).astype(float).reshape(-1, 1)
        Xd, yd, nab = absorb2(post, y, gigs, ages)
        b, se = ols_cluster(Xd, yd, gigs, n_absorbed=nab)
        ssr = float(np.sum((yd - Xd @ b) ** 2))
        results.append((c, float(b[0]), float(se[0]), float(b[0] / se[0]), ssr))

    best = min(results, key=lambda r: r[4])
    print("\n  quarter    delta      se       t        SSR        pct effect")
    for c, b, se, tt, ssr in results:
        star = "  <== BEST FIT" if c == best[0] else ""
        note = next((f"   [{lab}]" for q, lab in AI_TIMELINE if q == c), "")
        print(f"  {c}   {b:+7.4f}  {se:6.4f}  {tt:+6.2f}  {ssr:11.1f}   "
              f"{100*(np.exp(b)-1):+6.1f}%{star}{note}")

    print(f"\n  => BEST BREAK: {best[0]}   delta {best[1]:+.4f} "
          f"(t {best[3]:+.2f}), {100*(np.exp(best[1])-1):+.1f}%")

    # ---------------- P3: how does ChatGPT rank? ----------------
    print("\n" + "=" * 84)
    print("P3 — WHERE THE AI MILESTONES RANK AMONG ALL CANDIDATE BREAKS")
    print("=" * 84)
    order = sorted(results, key=lambda r: r[4])
    rank = {c: i + 1 for i, (c, *_rest) in enumerate(order)}
    print(f"\n  {len(results)} candidate quarters searched\n")
    print("  milestone                                quarter   rank    t")
    for q, lab in AI_TIMELINE:
        if q in rank:
            row = next(r for r in results if r[0] == q)
            print(f"  {lab:38s}  {q}   {rank[q]:3d}/{len(results)}  {row[3]:+6.2f}")
        else:
            print(f"  {lab:38s}  {q}   (outside search window)")

    # ---------------- P4: trend-break form ----------------
    print("\n" + "=" * 84)
    print("P4 — SEARCHED BREAK, trend-break (slope-change) form")
    print("     y = gig FE + age FE + gamma * max(t - c, 0)")
    print("=" * 84)
    tres = []
    for c in cands:
        kink = np.maximum(t - qi(c), 0.0).reshape(-1, 1)
        Xd, yd, nab = absorb2(kink, y, gigs, ages)
        b, se = ols_cluster(Xd, yd, gigs, n_absorbed=nab)
        ssr = float(np.sum((yd - Xd @ b) ** 2))
        tres.append((c, float(b[0]), float(se[0]), float(b[0] / se[0]), ssr))
    tbest = min(tres, key=lambda r: r[4])
    print("\n  quarter    gamma      se       t        SSR")
    for c, b, se, tt, ssr in tres:
        star = "  <== BEST FIT" if c == tbest[0] else ""
        note = next((f"   [{lab}]" for q, lab in AI_TIMELINE if q == c), "")
        print(f"  {c}   {b:+7.4f}  {se:6.4f}  {tt:+6.2f}  {ssr:11.1f}{star}{note}")
    print(f"\n  => BEST TREND BREAK: {tbest[0]}   gamma {tbest[1]:+.4f} "
          f"(t {tbest[3]:+.2f}) per quarter")

    print("\n" + "=" * 84)
    print("HOW TO READ THIS")
    print("=" * 84)
    print("""
  A best-fitting break is NOT evidence of causation. Searching over ~15 candidate
  quarters and reporting the winner inflates significance, and no correction is
  applied here. What the search CAN do is falsify a date: if the proxy turns well
  before a milestone, that milestone did not cause the turn.

  The age-period-cohort limit means the LEVEL of the decline is not attributable
  to calendar time at all — only the location of non-linear changes in it.
""")


if __name__ == "__main__":
    main()
