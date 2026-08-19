#!/usr/bin/env python3
"""
Step 53: Did the 2025-2026 acceleration concentrate in AI-exposed work?

THE QUESTION. Fiverr's Q2 2026 release blames "AI-related demand headwinds" and
"weakness in AI-exposed categories". Every design in this project so far tested a
window ending 2024Q4, which mostly PRECEDES the period the operator is describing.
This step tests the operator's own claim on the recent (live-collected) panel,
2024Q3-2026Q1.

THE TEST. If AI is doing this, exposed work should fall faster than unexposed work.
If everything falls together, it is a demand slump and AI is not identified.

DECLARED DEVIATION FROM PRE-REGISTRATION. The registered arms are
HIGH = {translation, writing}, LOW = {video, audio} (`data/exposure-ranking.csv`).
They cannot be run here: on the recent panel translation has 27 gigs with usable
review counts and audio has 47, reaching 4 and 5 observations in a quarter. Both
registered arms are anchored on a category that would return a null whatever the
truth. This step therefore uses the largest adequately-sized category on each side
of the SAME registered ranking:

    EXPOSED   = writing   (323 gigs)   -- 2nd of 7 on human beta
    UNEXPOSED = video     (217 gigs)   -- 6th of 7 on human beta

This is a deviation, declared before the outcome is seen, not a re-ranking. It
narrows the contrast from 4 categories to 2 and loses the arm-averaging that the
registered design used to reduce category-specific noise.

FRAMES ARE NOT SPLICED. The balanced (archival) and recent (live) panels are
different gig populations. Each is measured within itself; only SLOPES are
compared across them, never levels.

Outcome, construction and SEs follow step 46: within-gig adjacent-quarter review
accrual, log1p, gig-clustered SEs.

Run:  python3 code/53-recent-exposure.py
"""

import csv
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


m24 = _load("m24", "24-margin-diagnostics.py")
ols_cluster = m24.ols_cluster

PILOT = BASE / "data" / "pilot"
EXPOSED, UNEXPOSED = "writing", "video"


def qi(q):
    return int(q[:4]) * 4 + int(q[-1])


def build(prices, manifest, gid_cols, delim="\t"):
    cat = {}
    with open(manifest) as f:
        for r in csv.DictReader(f, delimiter=delim):
            cat[r["gig_id"]] = r["category"]
    raw = defaultdict(lambda: defaultdict(list))
    first = {}
    with open(prices) as f:
        for r in csv.DictReader(f):
            gid = r["seller"] + "/" + r["slug"]
            if gid not in cat:
                continue
            rv = r.get("review_count") or ""
            if rv == "":
                continue
            try:
                rev = float(rv)
            except ValueError:
                continue
            q = r["year"] + "Q" + str((int(r["month"]) - 1) // 3 + 1)
            raw[gid][q].append(rev)
            if gid not in first or r["date"] < first[gid][0]:
                first[gid] = (r["date"], q)
    out = []
    for gid, qs in raw.items():
        cells = {q: max(v) for q, v in qs.items()}
        order = sorted(cells, key=qi)
        birth = qi(first[gid][1])
        for a, b in zip(order, order[1:]):
            dq = qi(b) - qi(a)
            drev = cells[b] - cells[a]
            if dq <= 0 or drev < 0:
                continue
            out.append({"gig": gid, "cat": cat[gid], "q1": b, "t": qi(b),
                        "rate": drev / dq, "y": np.log1p(drev / dq),
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


def path(rows, label):
    print(f"\n  {label}")
    print("    quarter     n gigs   mean reviews/quarter")
    byq = defaultdict(list)
    for r in rows:
        byq[r["q1"]].append(r["rate"])
    for q in sorted(byq, key=qi):
        print(f"    {q}    {len(byq[q]):6,}          {np.mean(byq[q]):8.2f}")


def slope_test(rows, tag):
    """Differential trend: exposed vs unexposed, gig FE + quarter FE."""
    sub = [r for r in rows if r["cat"] in (EXPOSED, UNEXPOSED)]
    if not sub:
        print(f"\n  {tag}: no rows")
        return
    t0 = min(r["t"] for r in sub)
    hi = np.array([1.0 if r["cat"] == EXPOSED else 0.0 for r in sub])
    tt = np.array([r["t"] - t0 for r in sub], dtype=float)
    y = np.array([r["y"] for r in sub])
    gigs = [r["gig"] for r in sub]
    X = np.column_stack([hi * tt])
    Xd, yd, nab = absorb2(X, y, gigs, [r["q1"] for r in sub])
    b, se = ols_cluster(Xd, yd, gigs, n_absorbed=nab)
    ng = len({g for g in gigs})
    print(f"\n  {tag}")
    print(f"    n {len(sub):,}   gigs {ng:,}   "
          f"exposed gigs {len({r['gig'] for r in sub if r['cat']==EXPOSED}):,}")
    print(f"    exposed x trend  {b[0]:+.4f}  (se {se[0]:.4f}, t {b[0]/se[0]:+.2f})"
          f"   = {100*(np.exp(b[0])-1):+.1f}% per quarter differential")
    return float(b[0]), float(se[0]), float(b[0] / se[0])


def main():
    print("=" * 80)
    print("STEP 53 — DID THE DECLINE CONCENTRATE IN AI-EXPOSED WORK, 2024Q3-2026Q1?")
    print("=" * 80)
    print(f"\n  EXPOSED = {EXPOSED}   UNEXPOSED = {UNEXPOSED}")
    print("  (declared deviation: registered arms unusable, translation n=27, audio n=47)")

    recent = build(PILOT / "recent-prices.csv", PILOT / "recent-manifest.tsv",
                   None)
    bal = build(PILOT / "balanced-prices.csv", PILOT / "balanced-manifest-1200.tsv",
                None)

    print("\n" + "=" * 80)
    print("A — THE RAW PATHS, each frame within itself")
    print("=" * 80)
    for c in (EXPOSED, UNEXPOSED):
        path([r for r in recent if r["cat"] == c], f"RECENT frame — {c}")
    for c in (EXPOSED, UNEXPOSED):
        path([r for r in bal if r["cat"] == c and r["t"] >= qi("2023Q1")],
             f"BALANCED frame — {c} (2023Q1-2024Q4)")

    print("\n" + "=" * 80)
    print("B — DIFFERENTIAL TREND: does exposed work fall FASTER?")
    print("     y = gig FE + quarter FE + (exposed x trend)")
    print("     a NEGATIVE coefficient means exposed work fell faster = AI signature")
    print("=" * 80)
    r_new = slope_test(recent, "RECENT frame, 2024Q3-2026Q1  <== the period Fiverr blames AI for")
    r_old = slope_test([r for r in bal if r["t"] >= qi("2023Q1")],
                       "BALANCED frame, 2023Q1-2024Q4  (comparison baseline)")
    r_all = slope_test(bal, "BALANCED frame, full 2019Q3-2024Q4")

    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)
    if r_new:
        b, se, t = r_new
        if t < -1.96:
            print("\n  Exposed work fell significantly FASTER in 2024Q3-2026Q1.")
            print("  This is the first AI-consistent signature in the project.")
        elif t > 1.96:
            print("\n  Exposed work fell SLOWER — opposite of the AI prediction.")
        else:
            print(f"\n  NO differential (t {t:+.2f}). Writing and video fell together.")
            print("  Consistent with a general demand slump, NOT with an AI-specific")
            print("  effect on exposed categories. Fiverr's stated attribution is not")
            print("  reproduced on the gig-level data for the period it describes.")
    print("""
  LIMITS. Two categories, not four arms. 2025Q1-Q2 are thin (66 and 73 writing
  observations). A null here does not exclude a UNIFORM AI effect across all
  categories -- that is absorbed by quarter FE by construction, the same
  self-limitation recorded as R9 for design I6.
""")


if __name__ == "__main__":
    main()
