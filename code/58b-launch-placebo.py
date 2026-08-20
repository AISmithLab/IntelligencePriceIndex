#!/usr/bin/env python3
"""
Step 58b: Placebo launches. Does step 58's design fire when nothing happened?

WHY THIS EXISTS
---------------
Step 58's demand margin returned 11 of 20 launches "clearing the pre-window
gate". With 20 tests at 5%, ONE is expected by chance. Eleven is not a discovery
rate, it is a diagnostic: either AI launches move review accrual with wildly
inconsistent signs (DALL-E 2 +5.4%, Stable Diffusion +9.6%, but ChatGPT -6.7%
and GPT-4 -9.0%), or the design fires at arbitrary dates.

This settles it. The IDENTICAL design is run on FAKE launch dates in the pre-AI
era (2019-01 to 2020-06), each assigned the same target categories the real
launches used. No generative-AI tool existed for any of these dates. Any
significant result is a false positive by construction.

Decision rule, fixed before running: if the placebo false-positive rate is
materially above 5%, step 58's demand margin is not interpretable and must be
reported as a failed design rather than as findings.

Output: runs/ai-launch-placebo.out
"""

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np

CODE = Path(__file__).resolve().parent


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, CODE / fn)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


s58 = _load("s58", "58-ai-launch-events.py")
s57 = _load("s57", "57-ai-diffusion-titles.py")

# Fake launches: pre-AI dates, real target-category sets reused verbatim.
PLACEBO = [
    ("p-write-1",  "2019-03", ["writing", "translation"]),
    ("p-code-1",   "2019-04", ["coding"]),
    ("p-design-1", "2019-05", ["design"]),
    ("p-audio-1",  "2019-06", ["audio"]),
    ("p-video-1",  "2019-07", ["video"]),
    ("p-write-2",  "2019-08", ["writing", "translation"]),
    ("p-code-2",   "2019-09", ["coding"]),
    ("p-design-2", "2019-10", ["design"]),
    ("p-audio-2",  "2019-11", ["audio"]),
    ("p-video-2",  "2019-12", ["video"]),
    ("p-write-3",  "2020-01", ["writing", "translation"]),
    ("p-design-3", "2020-02", ["design"]),
]


def main():
    obs = s58.load_monthly()
    print("=" * 84)
    print("STEP 58b — PLACEBO LAUNCHES: does the design fire when nothing happened?")
    print("=" * 84)
    print("\n  12 fake launches, 2019-03 to 2020-02, each given the same target")
    print("  categories a real launch used. No generative-AI tool existed for any")
    print("  of these dates, so every significant result below is a false positive.")

    price_rows = [dict(y=math.log(r["price"]), m=r["m"], cat=r["cat"],
                       mo=r["ym"], g=r["gig"])
                  for r in obs if r["price"] and r["price"] > 0]
    acc = {}
    for r in obs:
        if r["rev"] is not None:
            acc.setdefault(r["gig"], []).append((r["m"], r["rev"], r["cat"]))
    arows = []
    for g, v in acc.items():
        v.sort()
        for (m1, r1, c1), (m2, r2, _) in zip(v, v[1:]):
            if 0 < m2 - m1 <= 3 and r2 >= r1:
                arows.append(dict(y=math.log1p((r2 - r1) / (m2 - m1)), m=m2,
                                  cat=c1, mo=f"{m2//12:04d}-{m2%12+1:02d}", g=g))

    for rows, name in ((price_rows, "PRICE  log(basic price)"),
                       (arows, "DEMAND log(1 + monthly accrual)")):
        print("\n" + "=" * 84)
        print(f"  {name}")
        print("=" * 84)
        print(f"\n  {'fake launch':13} {'date':9} {'n':>8} {'post DiD':>10} "
              f"{'t':>7} {'PRE t':>7}  fires?")
        hits = tot = 0
        for lid, ym, tg in PLACEBO:
            for r in rows:
                r["tr"] = 1.0 if r["cat"] in tg else 0.0
            post = s58.did(rows, "y", "tr", s58.mi(ym), 12, "g", ["g", "mo"], min_n=1000)
            pre = s58.did(rows, "y", "tr", s58.mi(ym) - 12, 12, "g", ["g", "mo"], min_n=1000)
            if post is None:
                print(f"  {lid:13} {ym:9} {'-':>8} {'-':>10} {'-':>7} {'-':>7}  insufficient")
                continue
            tot += 1
            pt = pre["t"] if pre else float("nan")
            fires = abs(post["t"]) >= 1.96 and not (pre and abs(pt) >= 1.96)
            hits += fires
            print(f"  {lid:13} {ym:9} {post['n']:8,} {post['b']:10.4f} "
                  f"{post['t']:7.2f} {pt:7.2f}  "
                  f"{'*** FALSE POSITIVE ***' if fires else 'no'}")
        rate = 100 * hits / tot if tot else 0
        print(f"\n  FALSE-POSITIVE RATE: {hits} of {tot} = {rate:.0f}%   "
              f"(nominal 5%)")
        if rate > 15:
            print("  >>> The design fires at arbitrary dates. Step 58's results on")
            print("      this outcome are NOT interpretable as launch effects.")
        elif rate > 5:
            print("  >>> Elevated but not catastrophic; read step 58 with caution.")
        else:
            print("  >>> At nominal size on this outcome.")


if __name__ == "__main__":
    main()
