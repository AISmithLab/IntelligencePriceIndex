#!/usr/bin/env python3
"""
Step 58: Named AI launches, monthly, with the category each one should hit.

WHAT THIS ADDS OVER STEPS 52/55/57
----------------------------------
Those SEARCHED for a break and ranked the AI milestones by fit. None of them
compared before against after at a named launch date, and all three ran
QUARTERLY. Two things were being left on the table:

  1. The panel is MONTHLY (`year`, `month` are on every row). A quarterly test
     smears a launch across up to three months and cannot see a 4-8 week
     response, which is the timescale on which a marketplace listing changes.

  2. Every launch has a NATURAL TARGET CATEGORY. Copilot is a coding tool.
     ElevenLabs is a voice tool. Midjourney is an image tool. Designs 1-8 used
     one exposure score for all of AI; this uses each tool's own target as its
     treatment, with the non-target categories as controls. That is a
     different and much sharper contrast, and it does not need the Eloundou
     score at all.

THE FIRST STAGE IS THE POINT
----------------------------
Step 57 gives something no previous design had: a measure of whether a launch
ACTUALLY DIFFUSED here. So each launch gets a first stage -- did the AI-branded
share of its target category move? -- before any price outcome is looked at. A
launch with no first stage cannot be expected to move prices, and reading its
price null as evidence about AI would be a mistake. Ordering the launches by
first-stage strength is therefore the exhibit that matters.

DECLARED IN ADVANCE, BEFORE ANY OUTCOME WAS ESTIMATED
-----------------------------------------------------
  - MULTIPLE TESTING. ~20 launches x 3 outcomes is ~60 tests; at 5% about three
    will be significant by chance. No result here is promoted on its own
    p-value. Reported: how many clear 5%, against how many are expected to.
  - OVERLAPPING WINDOWS. The launches cluster in 2022-2023; a +/-6 month window
    around ChatGPT contains GPT-4, Claude and ElevenLabs. Effects cannot be
    separated between launches inside a cluster, and no attempt is made to.
  - PRE-EXISTING TRENDS. Steps 52/55 established that the outcome series were
    already bending from 2020Q3. A significant post-launch difference is
    therefore NOT evidence of an effect unless the pre-window is flat, which is
    reported alongside every estimate as the honest gate.

Output: runs/ai-launch-events.out
"""

import csv
import importlib.util
import math
import sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CODE = ROOT / "code"
DATA = ROOT / "data" / "pilot"


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, CODE / fn)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


s57 = _load("s57", "57-ai-diffusion-titles.py")
m24 = _load("m24", "24-margin-diagnostics.py")
ols_cluster = m24.ols_cluster
CATS = s57.CATS
CATSET = s57.CATSET

# --------------------------------------------------------------------------
# The launch table. Dates are the PUBLIC AVAILABILITY date -- the date a Fiverr
# seller could actually start using the tool -- not the announcement or the
# paper. Where the two differ the availability date is used and the announcement
# noted, because an announcement cannot change a gig.
# --------------------------------------------------------------------------
LAUNCHES = [
    # (id, YYYY-MM, label, target categories)
    ("gpt3-api",   "2020-06", "GPT-3 API private beta",        ["writing", "translation"]),
    ("copilot",    "2021-06", "GitHub Copilot tech preview",   ["coding"]),
    ("gpt3-ga",    "2021-11", "GPT-3 general availability",    ["writing", "translation"]),
    ("dalle2",     "2022-04", "DALL-E 2 limited beta",         ["design"]),
    ("midjourney", "2022-07", "Midjourney open beta",          ["design"]),
    ("sd",         "2022-08", "Stable Diffusion public",       ["design"]),
    ("dalle2-open","2022-09", "DALL-E 2 open to all",          ["design"]),
    ("chatgpt",    "2022-11", "ChatGPT",                       ["writing", "translation"]),
    ("elevenlabs", "2023-01", "ElevenLabs beta",               ["audio"]),
    ("gpt4",       "2023-03", "GPT-4",                         ["writing", "translation", "coding"]),
    ("mj-v5",      "2023-03", "Midjourney v5",                 ["design"]),
    ("runway-g2",  "2023-06", "Runway Gen-2",                  ["video"]),
    ("heygen",     "2023-08", "HeyGen public",                 ["video"]),
    ("suno",       "2023-12", "Suno v1",                       ["audio"]),
    ("suno-v3",    "2024-03", "Suno v3",                       ["audio"]),
    ("gpt4o",      "2024-05", "GPT-4o",                        ["writing", "translation"]),
    ("sonnet35",   "2024-06", "Claude 3.5 Sonnet",             ["coding"]),
    ("flux",       "2024-08", "FLUX.1",                        ["design"]),
    ("veo2",       "2024-12", "Veo 2",                         ["video"]),
    ("r1",         "2025-01", "DeepSeek R1",                   ["coding"]),
]

PRICE_FILES = s57.PRICE_FILES
MANIFESTS = s57.MANIFESTS


def mi(ym):
    y, m = ym.split("-")
    return int(y) * 12 + int(m) - 1


def load_monthly():
    cat = {}
    for mf in MANIFESTS:
        p = DATA / mf
        if not p.exists():
            continue
        with open(p) as f:
            for r in csv.DictReader(f, delimiter="\t"):
                g, c = r.get("gig_id"), r.get("category")
                if g and c and g not in cat:
                    cat[g] = c
    seen, obs = set(), []
    for pf in PRICE_FILES:
        p = DATA / pf
        if not p.exists():
            continue
        with open(p) as f:
            for r in csv.DictReader(f):
                gid = r["seller"] + "/" + r["slug"]
                key = (gid, r["date"])
                if key in seen:
                    continue
                seen.add(key)
                ym = f"{int(r['year']):04d}-{int(r['month']):02d}"
                t = s57.clean_title(r.get("title"))
                _, ai_gen, anti = s57.classify(t)
                try:
                    price = float(r.get("price_basic") or "")
                except ValueError:
                    price = None
                try:
                    rev = int(float(r.get("review_count") or ""))
                except ValueError:
                    rev = None
                c = cat.get(gid)
                if c not in CATSET:
                    continue
                obs.append(dict(gig=gid, ym=ym, m=mi(ym), cat=c, price=price,
                                rev=rev, ai=ai_gen, anti=anti))
    return obs


def did(rows, ycol, treat_key, m0, half, cluster, absorb, min_n=200):
    """Before/after x target/non-target, with FE absorbed. -> dict or None."""
    win = [r for r in rows if m0 - half <= r["m"] < m0 + half]
    if len(win) < min_n:
        return None
    ntreat = sum(r[treat_key] for r in win)
    if ntreat < 30 or ntreat == len(win):
        return None
    for r in win:
        r["post"] = 1.0 if r["m"] >= m0 else 0.0
        r["tp"] = r[treat_key] * r["post"]
    npost = sum(r["post"] for r in win)
    if npost < 50 or npost == len(win):
        return None
    b, se, n, k = s57._ols(win, ycol, ["tp", "post"], cluster, absorb)
    if se[0] == 0 or not np.isfinite(se[0]):
        return None
    return dict(b=float(b[0]), se=float(se[0]), t=float(b[0] / se[0]), n=n,
                ntreat=int(ntreat))


def main():
    obs = load_monthly()
    print("=" * 88)
    print("STEP 58 — NAMED AI LAUNCHES, MONTHLY, AGAINST THE CATEGORY EACH ONE TARGETS")
    print("=" * 88)
    mm = Counter(r["ym"] for r in obs)
    print(f"\n  observations {len(obs):,}   months {len(mm)}   "
          f"{min(mm)} to {max(mm)}")
    print(f"  median observations per month: {int(np.median(list(mm.values()))):,}")
    print("\n  Monthly density is what makes this test possible at all; every")
    print("  earlier test in the project ran quarterly and smeared each launch")
    print("  across up to three months.")

    print("\n" + "=" * 88)
    print("A — THE LAUNCH TABLE")
    print("=" * 88)
    print("\n  Dates are PUBLIC AVAILABILITY -- when a seller could actually use the")
    print("  tool -- not the announcement. An announcement cannot change a gig.\n")
    print(f"  {'launch':13} {'date':9} {'tool':30} target categories")
    for lid, ym, lab, tg in LAUNCHES:
        print(f"  {lid:13} {ym:9} {lab:30} {', '.join(tg)}")

    for half, tag in ((6, "+/- 6 months"), (12, "+/- 12 months")):
        print("\n" + "=" * 88)
        print(f"B — FIRST STAGE: did the launch move AI ADOPTION in its target?  [{tag}]")
        print("=" * 88)
        print("\n  y = AI-branded (0/1).  DiD: target categories vs the other")
        print("  categories, after vs before. Month FE + category FE absorbed;")
        print("  SEs clustered on category. This asks whether the launch actually")
        print("  diffused HERE -- the question no design before step 57 could ask.")
        print(f"\n  {'launch':13} {'date':9} {'n':>8} {'DiD (pp)':>10} {'t':>7}  first stage")
        fs = {}
        for lid, ym, lab, tg in LAUNCHES:
            rows = [dict(y=float(r["ai"]), tr=1.0 if r["cat"] in tg else 0.0,
                         m=r["m"], cat=r["cat"], mo=r["ym"], g=r["gig"])
                    for r in obs]
            res = did(rows, "y", "tr", mi(ym), half, "cat", ["mo", "cat"])
            if res is None:
                print(f"  {lid:13} {ym:9} {'-':>8} {'-':>10} {'-':>7}  insufficient data")
                continue
            fs[lid] = res
            mark = "STRONG" if res["t"] > 2 else ("weak" if res["t"] > 1 else "none")
            print(f"  {lid:13} {ym:9} {res['n']:8,} {100*res['b']:10.3f} "
                  f"{res['t']:7.2f}  {mark}")
        if half == 6:
            first_stage = fs

    print("\n" + "=" * 88)
    print("C — PRICE: within-gig log price, target vs non-target, around each launch")
    print("=" * 88)
    print("\n  y = log(basic price). Gig FE + month FE absorbed, so this is the")
    print("  SAME listings before and after, against listings in other categories")
    print("  over the same months. SEs clustered on gig.")
    print("\n  The PRE column is the same DiD run on the 12 months BEFORE the")
    print("  window, with a false launch date. It is the gate: a post estimate")
    print("  with a significant pre estimate is a pre-existing trend, not an")
    print("  effect, and steps 52/55 showed these series were already bending.")
    print(f"\n  {'launch':13} {'date':9} {'n':>8} {'post DiD':>10} {'t':>7} "
          f"{'PRE t':>7}  verdict")
    price_rows = [dict(y=math.log(r["price"]), m=r["m"], cat=r["cat"],
                       mo=r["ym"], g=r["gig"])
                  for r in obs if r["price"] and r["price"] > 0]
    results = []
    for lid, ym, lab, tg in LAUNCHES:
        for r in price_rows:
            r["tr"] = 1.0 if r["cat"] in tg else 0.0
        post = did(price_rows, "y", "tr", mi(ym), 12, "g", ["g", "mo"], min_n=1000)
        pre = did(price_rows, "y", "tr", mi(ym) - 12, 12, "g", ["g", "mo"], min_n=1000)
        if post is None:
            print(f"  {lid:13} {ym:9} {'-':>8} {'-':>10} {'-':>7} {'-':>7}  insufficient")
            continue
        pt = pre["t"] if pre else float("nan")
        if abs(post["t"]) < 1.96:
            v = "null"
        elif pre and abs(pt) >= 1.96:
            v = "CONFOUNDED (pre also significant)"
        else:
            v = "*** clears the pre-window gate ***"
        results.append((lid, post, pre, v))
        print(f"  {lid:13} {ym:9} {post['n']:8,} {post['b']:10.4f} "
              f"{post['t']:7.2f} {pt:7.2f}  {v}")

    print("\n" + "=" * 88)
    print("D — DEMAND: within-gig review accrual around each launch")
    print("=" * 88)
    print("\n  y = log(1 + monthly review accrual), the project's sales proxy.")
    acc = defaultdict(list)
    for r in obs:
        if r["rev"] is not None:
            acc[r["gig"]].append((r["m"], r["rev"], r["cat"]))
    arows = []
    for g, v in acc.items():
        v.sort()
        for (m1, r1, c1), (m2, r2, _) in zip(v, v[1:]):
            if 0 < m2 - m1 <= 3 and r2 >= r1:
                arows.append(dict(y=math.log1p((r2 - r1) / (m2 - m1)), m=m2,
                                  cat=c1, mo=f"{m2//12:04d}-{m2%12+1:02d}", g=g))
    print(f"  accrual observations: {len(arows):,}")
    print(f"\n  {'launch':13} {'date':9} {'n':>8} {'post DiD':>10} {'t':>7} "
          f"{'PRE t':>7}  verdict")
    for lid, ym, lab, tg in LAUNCHES:
        for r in arows:
            r["tr"] = 1.0 if r["cat"] in tg else 0.0
        post = did(arows, "y", "tr", mi(ym), 12, "g", ["g", "mo"], min_n=1000)
        pre = did(arows, "y", "tr", mi(ym) - 12, 12, "g", ["g", "mo"], min_n=1000)
        if post is None:
            print(f"  {lid:13} {ym:9} {'-':>8} {'-':>10} {'-':>7} {'-':>7}  insufficient")
            continue
        pt = pre["t"] if pre else float("nan")
        if abs(post["t"]) < 1.96:
            v = "null"
        elif pre and abs(pt) >= 1.96:
            v = "CONFOUNDED (pre also significant)"
        else:
            v = "*** clears the pre-window gate ***"
        print(f"  {lid:13} {ym:9} {post['n']:8,} {post['b']:10.4f} "
              f"{post['t']:7.2f} {pt:7.2f}  {v}")

    print("\n" + "=" * 88)
    print("E — THE EXHIBIT THAT MATTERS: price effect ORDERED BY first-stage strength")
    print("=" * 88)
    print("\n  A launch that never diffused here cannot be expected to move prices,")
    print("  and its null says nothing about AI. So the test is whether the")
    print("  launches that DID diffuse are the ones with price effects.")
    print(f"\n  {'launch':13} {'first-stage t':>14} {'price DiD':>11} {'price t':>9}  gate")
    rmap = {lid: (p, pre, v) for lid, p, pre, v in results}
    order = sorted(first_stage.items(), key=lambda kv: -kv[1]["t"])
    for lid, f in order:
        if lid not in rmap:
            continue
        p, pre, v = rmap[lid]
        print(f"  {lid:13} {f['t']:14.2f} {p['b']:11.4f} {p['t']:9.2f}  {v}")
    print("\n  Multiple testing: ~20 launches x 3 outcomes is ~60 tests, so about")
    print("  three significant results at 5% are expected by chance alone. Count")
    print("  the '***' rows against three before reading anything into them.")


if __name__ == "__main__":
    main()
