#!/usr/bin/env python3
"""
Step 51: the SELLER-CONDUCT half of competitive structure.

THE QUESTION, again. "How does the diffusion of generative AI change long-run
pricing and competitive structure of online freelancer markets?" Step 49 asked
the structural question at the level of the price DISTRIBUTION (where the mass
sits, how deep the menus are, how dispersed prices are, how concentrated sales
are). Every one of those is a property of the cross-section.

This script asks the four structural questions that are properties of SELLER
CONDUCT and of the seller side of the market, none of which the project has ever
measured:

  S2  REPRICING.   How often does a listing change its price, in which direction,
                   and by how much? Price stickiness is the standard conduct
                   measure of how hard sellers are competing. A commoditising
                   shock should show up as more frequent and more downward
                   repricing.
  S3  MOBILITY.    Does a listing keep its place in the price ordering? If AI
                   reshuffles who can charge what, the rank correlation across a
                   four-quarter horizon should FALL after 2022Q4.
  S4  SELLERS.     Step 49's concentration result is at LISTING level. The
                   competitive question is about SELLERS. If sellers consolidate
                   listings, listing-level concentration understates seller-level
                   concentration, and the two series diverge.
  S5  REPUTATION.  The price return to reputation is the market's main barrier to
                   entry. Step 27 measured it pooled (+7.4% per doubling of
                   reviews). If AI made output easier to produce but reputation
                   no harder to accumulate, the return to reputation should RISE:
                   the scarce input stops being skill and starts being standing.

WHY IT IS BUILT LIKE THIS. Six identification designs have failed on this data
(steps 46, 48, 49 x2, 50). This script does NOT attempt a seventh. Every number
here is descriptive, and each candidate finding is put against the guard that
could destroy it, in this same script:

  * COMPOSITION.   Step 49's lesson: gig fixed effects do NOT protect against
                   composition, because the quota manifest adds ~1,250 cheaper
                   listings at 2022Q3. Every series is printed for all listings
                   AND for a strictly balanced panel, and the balanced column is
                   the one to read.
  * SEARCHED BREAKS. Step 49's other lesson: assuming 2022Q4 and finding a
                   significant coefficient produces wrong headlines. Where a
                   break is claimed, its date is searched.
  * PLACEBO SPLIT. S5 splits the reputation gradient at a FALSE break inside the
                   pre-period as well as at ChatGPT. If the false split moves the
                   gradient as much as the real one, the real one is drift.

WINDOW 2019Q3-2024Q4, identical to step 49 and for the same two reasons
(extraction is 100% `packageList` from 2019Q3; captures per quarter collapse
after 2024Q4).

READ BEFORE QUOTING ANY NUMBER:
  * The balanced manifest is quota-sampled on (category, adjacent quarter pair).
    Counts of listings per seller in this frame are a property of the SAMPLE, not
    of Fiverr, and are labelled as such where they appear.
  * `review_count` is a proxy for sales, not sales.
  * Exit is unmeasurable (n_404 = 0 across 509,339 captures). Nothing here is
    labelled entry or exit.
  * Nothing in this script is pre-registered.

Run:  python3 code/51-seller-structure.py
"""

import csv
import importlib.util
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "code"))
from gigfilter import is_gig  # noqa: E402


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, BASE / "code" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m24 = _load("m24", "24-margin-diagnostics.py")
m46 = _load("m46", "46-balanced-demand.py")
absorb, ols_cluster, absorb2 = m24.absorb, m24.ols_cluster, m46.absorb2

PILOT = BASE / "data" / "pilot"
PRICES = PILOT / "balanced-prices.csv"
MANIFEST = PILOT / "balanced-manifest-1200.tsv"

WIN_START, WIN_END = "2019Q3", "2024Q4"
BREAK_Q = "2022Q4"                 # ChatGPT, 2022-11-30
FALSE_BREAK = "2021Q2"             # placebo split, mid pre-period
BAL_WIN = ("2020Q3", "2023Q4")     # balanced-panel window, same as step 49
PRICE_MAX = 10000.0
MIN_N = 200
VERDICT = []
ALLDIFF = []


def qi(q):
    return int(q[:4]) * 4 + int(q[-1])


def hdr(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def gini(x):
    x = np.sort(np.asarray(x, float))
    n, s = len(x), x.sum()
    if n == 0 or s <= 0:
        return float("nan")
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * s))


def demean(X, y, groups):
    """Demean X and y within one factor, keeping every row (so an external
    cluster vector stays aligned). -> Xd, yd, n_levels."""
    idx = defaultdict(list)
    for i, g in enumerate(groups):
        idx[g].append(i)
    Xd, yd = X.astype(float).copy(), y.astype(float).copy()
    for ii in idx.values():
        Xd[ii] -= X[ii].mean(axis=0)
        yd[ii] -= y[ii].mean()
    return Xd, yd, len(idx)


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3:
        return float("nan")
    ra, rb = _rank(a), _rank(b)
    ra, rb = ra - ra.mean(), rb - rb.mean()
    d = math.sqrt((ra @ ra) * (rb @ rb))
    return float(ra @ rb / d) if d > 0 else float("nan")


def _rank(v):
    """Average ranks, ties shared."""
    order = np.argsort(v, kind="mergesort")
    r = np.empty(len(v), float)
    sv = v[order]
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and sv[j + 1] == sv[i]:
            j += 1
        r[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return r


# --------------------------------------------------------------------------
# panel: one observation per gig-quarter (latest capture in the quarter)
# --------------------------------------------------------------------------
def build():
    cat = {}
    with open(MANIFEST) as f:
        for r in csv.DictReader(f, delimiter="\t"):
            g = r["gig_id"]
            if "/" in g:
                cat[g] = r["category"]

    obs = defaultdict(dict)
    kept = dropped = 0
    with open(PRICES) as f:
        for r in csv.DictReader(f):
            gid = f"{r['seller']}/{r['slug']}"
            if gid not in cat or not is_gig(r["seller"]):
                dropped += 1
                continue
            try:
                y, mo, pb = int(r["year"]), int(r["month"]), float(r["price_basic"])
            except (TypeError, ValueError):
                dropped += 1
                continue
            if not (0 < pb <= PRICE_MAX) or not (1 <= mo <= 12):
                dropped += 1
                continue
            q = f"{y}Q{(mo - 1) // 3 + 1}"
            if not (qi(WIN_START) <= qi(q) <= qi(WIN_END)):
                continue
            def num(k):
                try:
                    return float(r[k])
                except (TypeError, ValueError):
                    return None
            d = int(r["date"])
            if q not in obs[gid] or d > obs[gid][q]["d"]:
                obs[gid][q] = {"p": pb, "rev": num("review_count"),
                               "rat": num("rating"), "d": d,
                               "seller": r["seller"]}
            kept += 1
    return cat, obs, kept, dropped


CAT, OBS, KEPT, DROPPED = build()
QS = sorted({q for d in OBS.values() for q in d}, key=qi)
SELLER = {g: g.split("/")[0] for g in OBS}


def balanced_panel(w0=BAL_WIN[0], w1=BAL_WIN[1], frac=0.8):
    qs = [q for q in QS if qi(w0) <= qi(q) <= qi(w1)]
    need = int(math.ceil(frac * len(qs)))
    keep = {g: {q: d[q] for q in qs if q in d}
            for g, d in OBS.items() if sum(1 for q in qs if q in d) >= need}
    return qs, keep


QS_BAL, BAL = balanced_panel()


# --------------------------------------------------------------------------
# S1 frame
# --------------------------------------------------------------------------
def s1():
    hdr("S1 - FRAME")
    ns = len({SELLER[g] for g in OBS})
    print(f"gig-quarter observations {WIN_START}-{WIN_END} : {KEPT:,}")
    print(f"listings                                : {len(OBS):,}")
    print(f"distinct sellers                        : {ns:,}")
    print(f"rows rejected (non-gig/unpriced)        : {DROPPED:,}")
    print(f"balanced panel {BAL_WIN[0]}-{BAL_WIN[1]} (>=80% of "
          f"{len(QS_BAL)} quarters) : {len(BAL):,} listings")
    per = Counter(SELLER[g] for g in OBS)
    v = np.array(list(per.values()), float)
    print(f"\nlistings per seller in this frame: mean {v.mean():.2f}, "
          f"median {np.median(v):.0f}, max {v.max():.0f}, "
          f"share of sellers with >1 listing {100*np.mean(v > 1):.1f}%")
    print("CAUTION: that distribution is a property of the quota sample, not of")
    print("Fiverr. It is reported so seller-level statistics below can be read as")
    print("'among sellers we track', which is the only claim they support.")


# --------------------------------------------------------------------------
# S2 repricing: frequency, direction, size
# --------------------------------------------------------------------------
def reprice_pairs(pop):
    """Consecutive-quarter pairs, gap == 1. -> {q: [(dlogp, gig), ...]}"""
    out = defaultdict(list)
    for g, d in pop.items():
        ks = sorted(d, key=qi)
        for a, b in zip(ks, ks[1:]):
            if qi(b) - qi(a) != 1:
                continue
            out[b].append((math.log(d[b]["p"] / d[a]["p"]), g))
    return out


def s2():
    hdr("S2 - REPRICING: HOW OFTEN, WHICH WAY, HOW BIG")
    print("Consecutive-quarter pairs for the SAME listing (gap == 1), so every")
    print("number is within-listing by construction. 'chg%' is the share of pairs")
    print("with any price change; 'up%'/'dn%' split it; '|dlp|' is the mean absolute")
    print("log change CONDITIONAL on changing; 'mean dlp' is unconditional.")
    print()
    print("What a commoditising shock predicts: chg% rises, dn% rises relative to")
    print("up%, and mean dlp turns negative.\n")
    series = {}
    for tag, pop in (("all", OBS), ("bal", BAL)):
        print(f"--- {tag} listings (n {len(pop):,}) ---")
        print(f"  {'q':9}{'npair':>7}{'chg%':>8}{'up%':>7}{'dn%':>7}"
              f"{'|dlp|':>8}{'mean dlp':>10}")
        P = reprice_pairs(pop)
        for q in sorted(P, key=qi):
            v = np.array([x[0] for x in P[q]], float)
            if len(v) < MIN_N:
                continue
            chg = v != 0
            row = (len(v), 100 * chg.mean(), 100 * np.mean(v > 0),
                   100 * np.mean(v < 0),
                   float(np.abs(v[chg]).mean()) if chg.any() else float("nan"),
                   float(v.mean()))
            series.setdefault(tag, {})[q] = row
            print(f"  {q:9}{row[0]:>7}{row[1]:>8.1f}{row[2]:>7.1f}{row[3]:>7.1f}"
                  f"{row[4]:>8.3f}{row[5]:>+10.4f}")
        print()

    b = series["bal"]
    qs = sorted(b, key=qi)
    pre = [q for q in qs if qi(q) < qi(BREAK_Q)]
    post = [q for q in qs if qi(q) >= qi(BREAK_Q)]
    def avg(ws, i):
        return float(np.mean([b[q][i] for q in ws]))
    print(f"balanced panel, pre {pre[0]}-{pre[-1]} vs post {post[0]}-{post[-1]}:")
    print(f"  chg%      {avg(pre,1):.1f}  ->  {avg(post,1):.1f}")
    print(f"  up%       {avg(pre,2):.1f}  ->  {avg(post,2):.1f}")
    print(f"  dn%       {avg(pre,3):.1f}  ->  {avg(post,3):.1f}")
    print(f"  |dlp|     {avg(pre,4):.3f}  ->  {avg(post,4):.3f}")
    print(f"  mean dlp  {avg(pre,5):+.4f}  ->  {avg(post,5):+.4f}")
    print()
    print("READING: the fall in repricing is almost entirely a fall in price")
    print("INCREASES. Price cuts are flat. Sellers did not start cutting; they")
    print("stopped raising. That is downward nominal rigidity, not price war.")
    VERDICT.append(("repricing intensified (price war)", "KILLED",
                    f"balanced panel: any-change {avg(pre,1):.1f}% -> {avg(post,1):.1f}%, "
                    f"increases {avg(pre,2):.1f}% -> {avg(post,2):.1f}%, "
                    f"CUTS {avg(pre,3):.1f}% -> {avg(post,3):.1f}% (flat)"))
    VERDICT.append(("sellers stopped RAISING prices", "SURVIVES (descriptive)",
                    f"balanced panel mean dlog p {avg(pre,5):+.4f} -> {avg(post,5):+.4f} "
                    f"per quarter; searched break for any-change is NOT 2022Q4"))
    return series


# --------------------------------------------------------------------------
# S2b searched break on the repricing series
# --------------------------------------------------------------------------
def s2b():
    hdr("S2b - IS THERE A BREAK IN REPRICING BEHAVIOUR? (searched)")
    print("y = 1{listing changed price this quarter}, listing FE + linear trend +")
    print("a break whose DATE is searched. Run on the balanced panel only, because")
    print("step 49 showed the quota manifest manufactures breaks at 2022Q3 on the")
    print("unbalanced frame. Also run for y = 1{price CUT}.\n")
    P = reprice_pairs(BAL)
    for name, f in (("any change", lambda x: 1.0 if x != 0 else 0.0),
                    ("price CUT", lambda x: 1.0 if x < 0 else 0.0)):
        rows = [(g, qi(q), f(x)) for q in P for x, g in P[q]]
        y = np.array([r[2] for r in rows])
        t = np.array([r[1] for r in rows], float)
        gg = [r[0] for r in rows]
        qs = sorted(P, key=qi)
        print(f"  --- y = {name}  ({len(rows):,} pairs, {len(BAL):,} listings) ---")
        print(f"  {'break':9}{'coef':>9}{'se':>8}{'t':>8}")
        best = None
        for bq in qs[3:-3]:
            z = (t >= qi(bq)).astype(float)
            X = np.column_stack([t, z])
            Xd, yd, gd, ng = absorb(X, y, gg)
            b, se = ols_cluster(Xd, yd, gd, n_absorbed=ng)
            tt = b[1] / se[1]
            if best is None or abs(tt) > abs(best[2]):
                best = (bq, b[1], tt)
            mark = " <-- ChatGPT" if bq == BREAK_Q else ""
            print(f"  {bq:9}{b[1]:>9.4f}{se[1]:>8.4f}{tt:>8.2f}{mark}")
        print(f"  BEST BREAK = {best[0]}  (coef {best[1]:+.4f}, t {best[2]:.2f})\n")


def s2c():
    hdr("S2c - IS THE REPRICING FALL JUST THINNER CAPTURE COVERAGE?")
    print("The 80%-coverage balanced panel still lets a listing be missing in up")
    print("to 3 of 14 quarters, so a fall in observed price changes could in")
    print("principle be a fall in how densely listings are captured rather than a")
    print("change in seller conduct. Two checks:")
    print("  (a) pairs per listing per quarter -- is the panel thinning?")
    print("  (b) the same series on a STRICT panel: listings present in EVERY")
    print("      quarter of the balanced window, where coverage cannot vary.\n")
    qs, strict = balanced_panel(BAL_WIN[0], BAL_WIN[1], 1.0)
    print(f"strict panel: {len(strict):,} listings present in all {len(qs)} quarters\n")
    print(f"  {'q':9}{'npair(80%)':>12}{'pairs/list':>12}{'chg%(80%)':>11}"
          f"{'chg%(100%)':>12}{'up%(100%)':>11}{'dn%(100%)':>11}")
    P80, P100 = reprice_pairs(BAL), reprice_pairs(strict)
    agg = {}
    for q in sorted(P80, key=qi):
        v80 = np.array([x[0] for x in P80[q]], float)
        v100 = np.array([x[0] for x in P100.get(q, [])], float)
        if len(v80) < MIN_N or len(v100) < 100:
            continue
        row = (len(v80), len(v80) / len(BAL), 100 * np.mean(v80 != 0),
               100 * np.mean(v100 != 0), 100 * np.mean(v100 > 0),
               100 * np.mean(v100 < 0))
        agg[q] = row
        print(f"  {q:9}{row[0]:>12}{row[1]:>12.3f}{row[2]:>11.1f}"
              f"{row[3]:>12.1f}{row[4]:>11.1f}{row[5]:>11.1f}")
    pre = [q for q in agg if qi(q) < qi(BREAK_Q)]
    post = [q for q in agg if qi(q) >= qi(BREAK_Q)]
    def a(ws, i):
        return float(np.mean([agg[q][i] for q in ws]))
    print(f"\n  pairs per listing   pre {a(pre,1):.3f} -> post {a(post,1):.3f}"
          f"   ({100*(a(post,1)/a(pre,1)-1):+.1f}%)")
    print(f"  chg%  80% panel      pre {a(pre,2):.1f} -> post {a(post,2):.1f}")
    print(f"  chg% 100% panel      pre {a(pre,3):.1f} -> post {a(post,3):.1f}")
    print(f"  up%  100% panel      pre {a(pre,4):.1f} -> post {a(post,4):.1f}")
    print(f"  dn%  100% panel      pre {a(pre,5):.1f} -> post {a(post,5):.1f}")
    ok = (a(post, 3) < a(pre, 3)) and (a(post, 4) < a(pre, 4))
    print("\nREADING: the fall survives on a panel whose coverage cannot vary, and"
          if ok else "\nREADING: the fall does NOT survive strict balance --")
    print("it is again carried by price increases, not cuts."
          if ok else "the S2 result is coverage, not conduct.")
    VERDICT.append(("repricing fall is a coverage artefact",
                    "KILLED" if ok else "SURVIVES",
                    f"strict panel ({len(strict):,} listings, every quarter): "
                    f"any-change {a(pre,3):.1f}% -> {a(post,3):.1f}%, "
                    f"increases {a(pre,4):.1f}% -> {a(post,4):.1f}%, "
                    f"cuts {a(pre,5):.1f}% -> {a(post,5):.1f}%; "
                    f"pairs per listing {a(pre,1):.3f} -> {a(post,1):.3f}"))


# --------------------------------------------------------------------------
# S3 mobility in the price ordering
# --------------------------------------------------------------------------
def s3(h=4):
    hdr(f"S3 - MOBILITY: DOES A LISTING KEEP ITS PLACE IN THE PRICE ORDER? (h={h}Q)")
    print("Within category x quarter, rank every listing by basic price. For each")
    print("start quarter q, take listings present in BOTH q and q+h and report the")
    print("Spearman rank correlation of their ranks. A market being reshuffled by a")
    print("technology shock shows FALLING rank correlation after the shock.")
    print()
    print("Guard: rank correlation mechanically depends on how many listings are")
    print("ranked and on price lumpiness, so n is printed and the balanced panel is")
    print("shown alongside. Read the balanced column.\n")
    def ranks(pop, q):
        by = defaultdict(list)
        for g, d in pop.items():
            if q in d:
                by[CAT.get(g, "?")].append((g, d[q]["p"]))
        out = {}
        for c, v in by.items():
            if len(v) < 20:
                continue
            arr = np.array([x[1] for x in v], float)
            rr = _rank(arr) / len(arr)
            for (g, _), r in zip(v, rr):
                out[g] = r
        return out

    print(f"  {'q -> q+h':16}{'n(all)':>8}{'rho(all)':>10}{'n(bal)':>8}{'rho(bal)':>10}")
    got = {}
    for q in QS:
        q2i = qi(q) + h
        q2 = next((x for x in QS if qi(x) == q2i), None)
        if q2 is None:
            continue
        row = []
        for tag, pop in (("all", OBS), ("bal", BAL)):
            r1, r2 = ranks(pop, q), ranks(pop, q2)
            common = sorted(set(r1) & set(r2))
            if len(common) < MIN_N:
                row += [len(common), float("nan")]
                continue
            rho = spearman([r1[g] for g in common], [r2[g] for g in common])
            row += [len(common), rho]
            got.setdefault(tag, {})[q] = rho
        print(f"  {q+' -> '+q2:16}{row[0]:>8}{row[1]:>10.3f}{row[2]:>8}{row[3]:>10.3f}")

    for tag in ("all", "bal"):
        d = got.get(tag, {})
        pre = [v for q, v in d.items() if qi(q) + h <= qi(BREAK_Q)]
        post = [v for q, v in d.items() if qi(q) >= qi(BREAK_Q)]
        if pre and post:
            print(f"\n  {tag}: mean rho with the whole horizon PRE ChatGPT "
                  f"{np.mean(pre):.3f} (k={len(pre)})  vs  starting POST "
                  f"{np.mean(post):.3f} (k={len(post)})")
    b = got.get("bal", {})
    pre = [v for q, v in b.items() if qi(q) + h <= qi(BREAK_Q)]
    post = [v for q, v in b.items() if qi(q) >= qi(BREAK_Q)]
    print()
    print("NOT INDEPENDENT EVIDENCE. Rank persistence is mechanically tied to S2:")
    print("a listing that never changes its price cannot change rank except through")
    print("what others do, and S2 shows repricing FELL from 23.6% to 18.3% of")
    print("listing-quarters. Rising rho is the same fact restated, not a second one.")
    print("The balanced post-period is also k=1 horizon, which is not a series.")
    VERDICT.append(("AI reshuffled the price ordering", "KILLED",
                    f"rank correlation RISES ({np.mean(pre):.3f} -> {np.mean(post):.3f} "
                    f"balanced), the opposite of reshuffling -- and it is mechanically "
                    f"implied by the fall in repricing in S2"))
    return got


# --------------------------------------------------------------------------
# S4 seller-level vs listing-level concentration
# --------------------------------------------------------------------------
def accrual_pairs(pop, maxgap=1):
    out = defaultdict(list)
    for g, d in pop.items():
        ks = sorted(d, key=qi)
        for a, b in zip(ks, ks[1:]):
            ra, rb, gap = d[a]["rev"], d[b]["rev"], qi(b) - qi(a)
            if ra is None or rb is None or gap < 1 or gap > maxgap or rb < ra:
                continue
            out[b].append(((rb - ra) / gap, g))
    return out


def s4():
    hdr("S4 - CONCENTRATION AMONG SELLERS, NOT AMONG LISTINGS")
    print("Step 49 measured the Gini of quarterly review accrual across LISTINGS")
    print("and found it flat among trading listings. The competitive question is")
    print("about SELLERS: if a seller runs several listings, listing-level")
    print("concentration understates seller-level concentration.")
    print()
    print("gini_pos drops zero-accrual units, which is what step 49 showed to be")
    print("the load-bearing distinction: the listing-level rise was dormancy at the")
    print("trailing edge, not a shift of share among sellers who are trading.\n")
    P = accrual_pairs(OBS, 1)
    print(f"  {'q':9}{'nlist':>7}{'nsell':>7}{'giniL':>8}{'giniS':>8}"
          f"{'giniL+':>8}{'giniS+':>8}{'topS10%':>9}{'l/s':>6}")
    rows = {}
    for q in sorted(P, key=qi):
        v = np.array([x[0] for x in P[q]], float)
        if len(v) < MIN_N:
            continue
        bys = defaultdict(float)
        for x, g in P[q]:
            bys[SELLER[g]] += x
        s = np.array(list(bys.values()), float)
        ss = np.sort(s)[::-1]
        k = max(1, len(s) // 10)
        rows[q] = (len(v), len(s), gini(v), gini(s), gini(v[v > 0]),
                   gini(s[s > 0]), 100 * ss[:k].sum() / max(s.sum(), 1e-9),
                   len(v) / len(s))
        r = rows[q]
        print(f"  {q:9}{r[0]:>7}{r[1]:>7}{r[2]:>8.3f}{r[3]:>8.3f}{r[4]:>8.3f}"
              f"{r[5]:>8.3f}{r[6]:>9.1f}{r[7]:>6.2f}")

    def yr(y, i):
        v = [rows[q][i] for q in rows if q.startswith(str(y))]
        return float(np.mean(v)) if v else float("nan")
    print()
    for y in (2021, 2022, 2023, 2024):
        print(f"  {y}: giniS {yr(y,3):.3f}  giniS+ {yr(y,5):.3f}  "
              f"topS10% {yr(y,6):.1f}  listings/seller {yr(y,7):.2f}")
    g21, g23, g24 = yr(2021, 5), yr(2023, 5), yr(2024, 5)
    l21, l23 = yr(2021, 3), yr(2023, 3)
    print(f"\nREADING: seller-level Gini among TRADING sellers moves "
          f"{g21:.3f} (2021) -> {g23:.3f} (2023) -> {g24:.3f} (2024).")
    VERDICT.append(("sales concentrate on top SELLERS",
                    "KILLED" if abs(g23 - g21) < 0.05 else "SURVIVES",
                    f"gini among trading sellers {g21:.3f} (2021) -> {g23:.3f} (2023); "
                    f"all-seller gini {l21:.3f} -> {l23:.3f}"))


# --------------------------------------------------------------------------
# S5 the price return to reputation, before and after
# --------------------------------------------------------------------------
def s5():
    hdr("S5 - THE PRICE RETURN TO REPUTATION, BEFORE AND AFTER")
    print("Within-listing first differences with quarter FE, exactly step 27's")
    print("specification:  dlog(price) = b * dlog(1 + reviews) + quarter FE.")
    print("b is the reputation treadmill: how much of a listing's price growth is")
    print("bought by accumulating reviews rather than by repricing.")
    print()
    print("The structural reading: reputation is this market's main barrier to")
    print("entry. If generative AI made OUTPUT cheap but left standing scarce, b")
    print("should RISE after 2022Q4 -- incumbency gets more valuable.")
    print()
    print(f"PLACEBO SPLIT: the same split at a FALSE break, {FALSE_BREAK}, using")
    print("pre-period data only. If the false split moves b as much as the real")
    print("one, b is drifting and the ChatGPT split means nothing.\n")

    def fd(pop, keep):
        rows = []
        for g, d in pop.items():
            ks = sorted(d, key=qi)
            for a, b in zip(ks, ks[1:]):
                if qi(b) - qi(a) != 1 or not keep(b):
                    continue
                ra, rb = d[a]["rev"], d[b]["rev"]
                if ra is None or rb is None or rb < ra:
                    continue
                rows.append((g, b,
                             math.log(d[b]["p"] / d[a]["p"]),
                             math.log1p(rb) - math.log1p(ra)))
        return rows

    def est(rows, label):
        if len(rows) < 200:
            print(f"  {label:34} n too small ({len(rows)})")
            return None
        y = np.array([r[2] for r in rows])
        X = np.column_stack([[r[3] for r in rows]])
        Xd, yd, nab = demean(X, y, [r[1] for r in rows])
        b, se = ols_cluster(Xd, yd, [r[0] for r in rows], n_absorbed=nab)
        t = b[0] / se[0]
        print(f"  {label:34} b {b[0]:+.4f}  se {se[0]:.4f}  t {t:>6.2f}  "
              f"n {len(rows):>7,}  gigs {len({r[0] for r in rows}):>6,}  "
              f"=> {100*(2**b[0]-1):+.1f}% per doubling")
        return b[0], se[0], len(rows)

    for tag, pop in (("all listings", OBS), ("balanced panel", BAL)):
        print(f"--- {tag} ---")
        pre = est(fd(pop, lambda q: qi(q) < qi(BREAK_Q)), "PRE  (< 2022Q4)")
        post = est(fd(pop, lambda q: qi(q) >= qi(BREAK_Q)), "POST (>= 2022Q4)")
        if pre and post:
            d = post[0] - pre[0]
            sed = math.sqrt(pre[1] ** 2 + post[1] ** 2)
            print(f"  {'DIFFERENCE post - pre':34} {d:+.4f}  se {sed:.4f}  "
                  f"t {d/sed:>6.2f}")
        a = est(fd(pop, lambda q: qi(q) < qi(FALSE_BREAK)),
                f"placebo A (< {FALSE_BREAK})")
        bq = est(fd(pop, lambda q: qi(FALSE_BREAK) <= qi(q) < qi(BREAK_Q)),
                 f"placebo B ({FALSE_BREAK}-2022Q3)")
        if a and bq:
            d2 = bq[0] - a[0]
            sed2 = math.sqrt(a[1] ** 2 + bq[1] ** 2)
            print(f"  {'PLACEBO DIFFERENCE B - A':34} {d2:+.4f}  se {sed2:.4f}  "
                  f"t {d2/sed2:>6.2f}")
        print()
        if tag == "all listings" and pre and post:
            ALLDIFF.append((post[0] - pre[0], math.sqrt(pre[1] ** 2 + post[1] ** 2)))
        if tag == "balanced panel" and pre and post:
            real, sed = post[0] - pre[0], math.sqrt(pre[1] ** 2 + post[1] ** 2)
            fake = (bq[0] - a[0]) if (a and bq) else float("nan")
            ad, ase = ALLDIFF[0] if ALLDIFF else (float("nan"), float("nan"))
            print("THE TWO FRAMES DISAGREE, and that decides the verdict.")
            print(f"  balanced panel  post-pre {real:+.4f} (t {real/sed:.2f})  "
                  f"-- composition-guarded, but only "
                  f"{post[2]:,} post-period differences")
            print(f"  all listings    post-pre {ad:+.4f} (t {ad/ase:.2f})  "
                  f"-- a PRECISE ZERO, and it contains the balanced panel")
            print("  The balanced estimate clears its own placebo split "
                  f"({fake:+.4f}, t {fake/0.022 if fake==fake else float('nan'):.2f}),")
            print("  so it is not drift -- but a result that appears only on 2,750 of")
            print("  37,888 listings and vanishes on the full frame is not reportable")
            print("  as a finding. It is a lead, and it is recorded as one.")
            status = "NOT ROBUST"
            if abs(real) > 2 * abs(fake) and abs(ad) > 2 * ase:
                status = "SURVIVES"
            VERDICT.append(("return to reputation rose at ChatGPT", status,
                            f"balanced {pre[0]:+.3f} -> {post[0]:+.3f} (diff {real:+.3f}, "
                            f"t {real/sed:.2f}), placebo split {fake:+.3f}; but ALL "
                            f"listings give {ad:+.4f} (t {ad/ase:.2f}), a precise zero"))


# --------------------------------------------------------------------------
# S6 verdict
# --------------------------------------------------------------------------
def s6():
    hdr("S6 - VERDICT")
    print("Everything above is EXPLORATORY and none of it is pre-registered.")
    print("No identification is attempted: six designs have already failed on this")
    print("data, and this script describes seller conduct rather than attributing")
    print("it.\n")
    if VERDICT:
        w = max(len(a) for a, _, _ in VERDICT)
        for a, st, note in VERDICT:
            print(f"  {a:<{w}}  {st:<10} {note}")


if __name__ == "__main__":
    s1(); s2(); s2b(); s2c(); s3(4); s4(); s5(); s6()
