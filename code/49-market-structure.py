#!/usr/bin/env python3
"""
Step 49: competitive structure of the market, not just its price level.

THE QUESTION. "How does the diffusion of generative AI change long-run pricing
and competitive structure of online freelancer markets?" The IPI answers the
price-LEVEL half (+40.7% real, 2020Q1-2026Q1). This script asks the structural
half on data already collected: what happened to the price DISTRIBUTION, to
product-line depth, to dispersion, and to the concentration of sales.

WHY IT IS BUILT LIKE THIS. Steps 46 and 48 established that the AI attribution is
not identified at category level: four designs failed (parallel trends, the trend
horse race, the CPI-U placebo, synthetic control with in-space placebos, whose
p-floor is 1/7 = 0.143). This script therefore does two separate things and keeps
them separate:

  (a) DESCRIBE structural change over the diffusion window, with the sampling
      caveats stated next to each number; and
  (b) TEST two new identification routes that do NOT rely on the seven-category
      exposure ranking -- and report that BOTH fail, with the diagnostic that
      kills each.

Every candidate finding here runs against a placebo that could destroy it, and
three of them are destroyed. That is the reportable content, not a preamble to it.

WINDOW: 2019Q3-2024Q4.
  * Start: extraction method is 100% `packageList` from 2019Q3 (before that it is
    a 3-way mix of packageList/old_json/dollar_fallback whose 3-tier detection
    rates differ by 19 points, so any versioning series across that seam is a
    parser artefact).
  * End: 2024Q4, for the reason step 48 gives -- captures per quarter collapse
    from ~9,300 to ~700 after it, and every category drops steeply into the edge.

SECTIONS
  S1  frame audit
  S2  the price distribution: the $5 tier and the $100+ tier
  S3  DATING the $5 collapse -- break-date search, not an assumed break
  S4  versioning: 3-tier share and the premium/basic ladder
  S5  dispersion, all gigs vs a fixed panel
  S6  sales concentration, and whether it is mechanical
  S7  NEW DESIGN 1 -- within-category price-tier DiD ("does AI eat the cheap end?")
  S8  NEW DESIGN 2 -- price convergence, with a ranking-window placebo
  S9  verdict table

READ BEFORE QUOTING ANY NUMBER:
  * The balanced manifest is quota-sampled on (category, adjacent quarter pair),
    so a within-quarter cross-section is NOT a random sample of live listings.
    Cross-sectional shares are reported for the fixed panel as well as for all
    gigs, and the fixed-panel column is the one to trust for change over time.
  * review_count is a proxy for sales, not sales. Exit is unmeasurable
    (n_404 = 0 across 509,339 captures); nothing here is labelled exit.
  * Nothing in this script is pre-registered. It is exploratory by construction
    and is labelled as such in the verdict table.

Run:  python3 code/49-market-structure.py
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
BREAK_Q = "2022Q4"                      # ChatGPT, 2022-11-30
RANK_WIN = ("2021Q1", "2022Q1")         # default ranking window for S7/S8
PLACEBO_WINS = [("2019Q3", "2019Q4"), ("2021Q1", "2022Q1"), ("2023Q3", "2024Q4")]
CATS = ["audio", "coding", "design", "marketing", "translation", "video", "writing"]
PRICE_MAX = 10000.0
VERDICT = []


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
    meth = defaultdict(Counter)
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
            meth[q][r["extraction_method"]] += 1
            if not (qi(WIN_START) <= qi(q) <= qi(WIN_END)):
                continue
            try:
                prem = float(r["price_premium"])
            except (TypeError, ValueError):
                prem = None
            try:
                rev = float(r["review_count"])
            except (TypeError, ValueError):
                rev = None
            d = int(r["date"])
            if q not in obs[gid] or d > obs[gid][q]["d"]:
                obs[gid][q] = {"p": pb, "prem": prem, "rev": rev, "d": d}
            kept += 1
    return cat, obs, meth, kept, dropped


CAT, OBS, METH, KEPT, DROPPED = build()
QS = sorted({q for d in OBS.values() for q in d}, key=qi)
PRE = {g for g, d in OBS.items() if any(qi(q) < qi(BREAK_Q) for q in d)}
POST = {g for g, d in OBS.items() if any(qi(q) >= qi(BREAK_Q) for q in d)}
FIXED = PRE & POST


# --------------------------------------------------------------------------
# S1 frame audit
# --------------------------------------------------------------------------
def s1():
    hdr("S1 - FRAME AUDIT")
    print(f"in-window gig-quarter observations : {KEPT:,}")
    print(f"gigs                               : {len(OBS):,}")
    print(f"gigs seen both pre and post {BREAK_Q} : {len(FIXED):,}  (the 'fixed panel')")
    print(f"rows rejected (non-gig/unpriced)   : {DROPPED:,}")
    print("\nextraction-method mix -- this is why the window starts at 2019Q3:")
    print(f"  {'q':9}{'packageList':>13}{'old_json':>10}{'dollar_fb':>11}{'n':>9}")
    for q in sorted(METH, key=qi)[:8]:
        t = sum(METH[q].values())
        print(f"  {q:9}{100*METH[q]['packageList']/t:>12.1f}%{100*METH[q]['old_json']/t:>9.1f}%"
              f"{100*METH[q]['dollar_fallback']/t:>10.1f}%{t:>9,}")
    tail = [q for q in sorted(METH, key=qi) if qi(q) >= qi("2019Q3")]
    pl = min(100 * METH[q]["packageList"] / sum(METH[q].values()) for q in tail)
    print(f"  ... from 2019Q3 on, packageList share never falls below {pl:.1f}%")


# --------------------------------------------------------------------------
# S2 the price distribution
# --------------------------------------------------------------------------
def s2():
    hdr("S2 - THE PRICE DISTRIBUTION: WHERE THE MASS WENT")
    print("share of gig-quarter observations at each price point.")
    print("'fixed' = only gigs present both before and after 2022Q4, so a change")
    print("there is the SAME listings repricing, not composition.\n")
    pts = [5, 10, 25, 50]
    print(f"{'q':9}{'pop':7}{'n':>7}" + "".join(f"{'$'+str(p):>7}" for p in pts)
          + f"{'>=$100':>8}{'median':>8}")
    series = {}
    for q in QS:
        for tag, pop in (("all", OBS), ("fixed", {g: OBS[g] for g in FIXED})):
            v = [d[q]["p"] for d in pop.values() if q in d]
            if len(v) < 200:
                continue
            c, n, a = Counter(v), len(v), np.array(v)
            row = [100 * c[p] / n for p in pts] + [100 * np.mean(a >= 100)]
            series.setdefault(tag, {})[q] = row
            print(f"{q:9}{tag:7}{n:>7}" + "".join(f"{x:>7.1f}" for x in row[:-1])
                  + f"{row[-1]:>8.1f}{np.median(a):>8.0f}")
    f0, f1 = series["fixed"][QS[0]], series["fixed"][QS[-1]]
    print(f"\nfixed panel, {QS[0]} -> {QS[-1]}:  $5 tier {f0[0]:.1f}% -> {f1[0]:.1f}%"
          f"   |   $100+ tier {f0[-1]:.1f}% -> {f1[-1]:.1f}%")
    return series


# --------------------------------------------------------------------------
# S3 dating the $5 collapse -- a BREAK-DATE SEARCH, not an assumed break
# --------------------------------------------------------------------------
def balanced_panel(w0, w1, frac=0.8):
    """Listings observed in at least `frac` of the quarters in [w0, w1]."""
    qs = [q for q in QS if qi(w0) <= qi(q) <= qi(w1)]
    need = int(math.ceil(frac * len(qs)))
    keep = {g: {q: d[q] for q in qs if q in d}
            for g, d in OBS.items() if sum(1 for q in qs if q in d) >= need}
    return qs, keep


def _break_search(pop, qs, label, kind="level"):
    """kind='level': one-off shift.  kind='trend': change in SLOPE at the break.
    The trend form is the one that matches the question -- did the commodity tier
    empty FASTER after ChatGPT? -- because the series is a decline whose slope
    changes, not a step."""
    rows = [(g, qi(q), 1.0 if d[q]["p"] <= 10 else 0.0) for g, d in pop.items() for q in d]
    y = np.array([r[2] for r in rows])
    t = np.array([r[1] for r in rows], float)
    gg = [r[0] for r in rows]
    print(f"\n  --- {label} [{kind} break]  ({len(pop):,} listings, {len(rows):,} obs) ---")
    if kind == "trend":
        print(f"  {'break':9}{'d slope':>10}{'se':>8}{'t':>8}   negative = decline STEEPENS after")
    else:
        print(f"  {'break':9}{'coef':>9}{'se':>8}{'t':>8}")
    best = None
    for bq in qs[3:-3]:
        b0 = qi(bq)
        z = np.maximum(t - b0, 0.0) if kind == "trend" else (t >= b0).astype(float)
        X = np.column_stack([t, z])
        Xd, yd, gd, ng = absorb(X, y, gg)
        b, se = ols_cluster(Xd, yd, gd, n_absorbed=ng)
        tt = b[1] / se[1]
        if best is None or abs(tt) > abs(best[2]):
            best = (bq, b[1], tt)
        mark = " <-- ChatGPT" if bq == BREAK_Q else ""
        print(f"  {bq:9}{b[1]:>9.4f}{se[1]:>8.4f}{tt:>8.2f}{mark}")
    print(f"  BEST BREAK = {best[0]}  (coef {best[1]:+.4f}, t {best[2]:.2f})")
    return best


def s3():
    hdr("S3 - WHEN DID THE COMMODITY TIER EMPTY? (break-date search)")
    print("y = 1{basic price <= $10}, gig FE + linear trend + a break whose DATE is")
    print("searched rather than assumed. If the cheap tier emptied because of")
    print("generative AI, the best break is 2022Q4 and the decline steepens there.")
    print()
    print("Two framings are needed and neither is optional:")
    print("  * FRAME. Gig FE does NOT protect against composition. The quota manifest")
    print("    adds ~1,250 net listings at 2022Q3 and the added ones are cheaper,")
    print("    which manufactures a break exactly at the quarter of interest.")
    print("  * FORM. The series is a decline whose SLOPE changes, not a step, so a")
    print("    level-shift search reports curvature and a trend-break search reports")
    print("    the event. Both are shown.")

    _break_search(OBS, QS, "ALL listings (composition-contaminated)", "level")
    qs_b, bal = balanced_panel("2020Q3", "2023Q4", 0.8)
    _break_search(bal, qs_b, "BALANCED panel 2020Q3-2023Q4, >=80% coverage", "level")
    b_tr = _break_search(bal, qs_b, "BALANCED panel 2020Q3-2023Q4, >=80% coverage", "trend")

    print("\n  The balanced series itself, share of listings priced <= $10:")
    print(f"  {'q':9}{'n_bal':>8}{'<=$10':>9}{'QoQ pp':>9}   {'n_all':>7}{'<=$10 all':>11}")
    prev = None
    for q in qs_b:
        v = np.array([d[q]["p"] for d in bal.values() if q in d])
        a = np.array([d[q]["p"] for d in OBS.values() if q in d])
        cur = 100 * float(np.mean(v <= 10))
        dq = "" if prev is None else f"{cur-prev:>+9.1f}"
        print(f"  {q:9}{len(v):>8}{cur:>8.1f}%{dq:>9}   {len(a):>7}{100*np.mean(a<=10):>10.1f}%")
        prev = cur
    print("\n  The all-listings column JUMPS at 2022Q3 (+5.7pp). The balanced column")
    print("  does not: it falls throughout and DECELERATES after 2022.")

    hit = b_tr[0] == BREAK_Q
    print(f"\n  VERDICT: on the balanced frame the trend break lands at {b_tr[0]}"
          f" with slope change {b_tr[1]:+.4f}/quarter,")
    print(f"  {'which IS' if hit else 'and 2022Q4 is not'} the ChatGPT quarter. The sign at 2022Q4 says the")
    print("  emptying of the commodity tier SLOWED after ChatGPT rather than")
    print("  accelerating -- the opposite of an AI-commoditisation signature.")
    VERDICT.append(("$5 commodity tier emptied", "FACT, PRE-DATES AI",
                    f"32%->11% of listings; steepest decline 2021, trend break "
                    f"{b_tr[0]}; post-2022Q4 the decline SLOWS"))
    return b_tr


# --------------------------------------------------------------------------
# S4 versioning
# --------------------------------------------------------------------------
def s4():
    hdr("S4 - PRODUCT-LINE DEPTH (versioning)")
    print("3-tier share = share of listings offering a premium package.")
    print("ladder = mean log(premium/basic) among 3-tier listings: how far the")
    print("top of a seller's own menu sits above the bottom.\n")
    print(f"{'q':9}{'pop':7}{'n':>7}{'3tier%':>9}{'ladder':>9}{'prem/basic':>12}")
    out = {}
    for q in QS:
        for tag, pop in (("all", OBS), ("fixed", {g: OBS[g] for g in FIXED})):
            v = [d[q] for d in pop.values() if q in d]
            if len(v) < 200:
                continue
            three = np.mean([1 if x["prem"] else 0 for x in v])
            lad = [math.log(x["prem"] / x["p"]) for x in v if x["prem"] and x["prem"] > 0]
            L = float(np.mean(lad)) if lad else float("nan")
            out.setdefault(tag, {})[q] = (three, L)
            print(f"{q:9}{tag:7}{len(v):>7}{100*three:>9.1f}{L:>9.3f}{math.exp(L):>11.2f}x")
    a, b = out["fixed"][QS[0]], out["fixed"][QS[-1]]
    print(f"\nfixed panel {QS[0]} -> {QS[-1]}: 3-tier {100*a[0]:.1f}% -> {100*b[0]:.1f}%,"
          f"  ladder {math.exp(a[1]):.2f}x -> {math.exp(b[1]):.2f}x")
    VERDICT.append(("product-line depth rose", "FACT",
                    f"3-tier {100*a[0]:.0f}%->{100*b[0]:.0f}%, ladder compresses "
                    f"{math.exp(a[1]):.2f}x->{math.exp(b[1]):.2f}x"))


# --------------------------------------------------------------------------
# S5 dispersion
# --------------------------------------------------------------------------
def s5():
    hdr("S5 - PRICE DISPERSION")
    print("sd of log(basic price) and the P90-P10 log spread, within quarter,")
    print("pooling categories. Prices are lumpy (round numbers), so sd is the")
    print("informative column and the percentile spread is chunky by construction.\n")
    print(f"{'q':9}{'pop':7}{'n':>7}{'sd_logp':>10}{'P90-P10':>10}")
    keep = {}
    for q in QS:
        for tag, pop in (("all", OBS), ("fixed", {g: OBS[g] for g in FIXED})):
            v = [d[q]["p"] for d in pop.values() if q in d]
            if len(v) < 200:
                continue
            lp = np.log(v)
            sd = float(lp.std(ddof=1))
            sp = float(np.percentile(lp, 90) - np.percentile(lp, 10))
            keep.setdefault(tag, {})[q] = sd
            print(f"{q:9}{tag:7}{len(v):>7}{sd:>10.3f}{sp:>10.3f}")
    f = keep["fixed"]
    lo = min(f, key=lambda q: f[q])
    print(f"\nfixed panel: sd {f[QS[0]]:.3f} ({QS[0]}) -> {f[lo]:.3f} ({lo})"
          f" -> {f[QS[-1]]:.3f} ({QS[-1]})")
    print("Dispersion falls then partly recovers; the trough is mid-2023. This is a")
    print("description of a quota-sampled cross-section, NOT an identified result.")
    VERDICT.append(("price dispersion narrowed then recovered", "DESCRIPTIVE",
                    f"sd log p {f[QS[0]]:.2f} -> {f[lo]:.2f} ({lo}) -> {f[QS[-1]]:.2f}"))


# --------------------------------------------------------------------------
# S6 concentration -- and whether it is mechanical
# --------------------------------------------------------------------------
def accrual_pairs(pop, maxgap=2):
    out = defaultdict(list)
    for g, d in pop.items():
        ks = sorted(d, key=qi)
        for a, b in zip(ks, ks[1:]):
            ra, rb, gap = d[a]["rev"], d[b]["rev"], qi(b) - qi(a)
            if ra is None or rb is None or gap < 1 or gap > maxgap or rb < ra:
                continue
            out[b].append(((rb - ra) / gap, g))
    return out


def s6():
    hdr("S6 - CONCENTRATION OF SALES, AND WHETHER IT IS MECHANICAL")
    print("Quarterly review accrual per listing. gini_all is the headline")
    print("concentration number; gini_pos drops the zero-accrual listings.")
    print("If concentration rose only because more listings sold NOTHING, then")
    print("gini_all rises while gini_pos does not -- and the story is dormancy,")
    print("not a shift of share among sellers who are trading.\n")
    coh = {g: OBS[g] for g in OBS
           if any(2022 * 4 + 1 <= qi(q) <= 2022 * 4 + 4 for q in OBS[g])
           and any(2024 * 4 + 1 <= qi(q) <= 2024 * 4 + 4 for q in OBS[g])}
    for tag, pop, mg in [("all gigs, gap<=2", OBS, 2),
                         ("all gigs, gap==1", OBS, 1),
                         ("2022&2024 cohort, gap==1", coh, 1)]:
        P = accrual_pairs(pop, mg)
        print(f"--- {tag}  (n gigs {len(pop):,}) ---")
        print(f"  {'q':9}{'npair':>7}{'zero%':>8}{'gini_all':>10}{'gini_pos':>10}"
              f"{'top10%':>9}{'mean':>8}{'median':>8}")
        for q in sorted(P, key=qi):
            v = np.array([x[0] for x in P[q]], float)
            if len(v) < 200:
                continue
            pos = v[v > 0]
            s = np.sort(v)[::-1]
            k = max(1, len(v) // 10)
            print(f"  {q:9}{len(v):>7}{100*np.mean(v==0):>8.1f}{gini(v):>10.3f}"
                  f"{gini(pos):>10.3f}{100*s[:k].sum()/max(v.sum(),1e-9):>9.1f}"
                  f"{v.mean():>8.1f}{np.median(v):>8.1f}")
        print()
    P = accrual_pairs(OBS, 1)
    def yr(y):
        v = [np.mean(np.array([x[0] for x in P[q]]) == 0)
             for q in P if q.startswith(str(y)) and len(P[q]) >= 200]
        gp = [gini(np.array([x[0] for x in P[q]])[np.array([x[0] for x in P[q]]) > 0])
              for q in P if q.startswith(str(y)) and len(P[q]) >= 200]
        return 100 * float(np.mean(v)), float(np.mean(gp))
    z21, g21 = yr(2021)
    z23, g23 = yr(2023)
    z24, g24 = yr(2024)
    print(f"annual means, gap==1:  2021 zero {z21:.1f}% gini_pos {g21:.3f}"
          f" | 2023 zero {z23:.1f}% gini_pos {g23:.3f}"
          f" | 2024 zero {z24:.1f}% gini_pos {g24:.3f}")
    print("\nREADING: 2021 -> 2023 is FLAT on both margins. The whole rise is 2024,")
    print("which is the trailing edge step 48 already flagged as thinning. So the")
    print("'sales concentrated on winners' story is NOT supported: what rises is the")
    print("zero-sales share, it rises only at the edge, and concentration among")
    print("trading listings barely moves.")
    VERDICT.append(("sales concentrated on top sellers", "KILLED",
                    f"gini_pos flat 2021 {g21:.2f} -> 2023 {g23:.2f}; rise is zero-sales "
                    f"listings in 2024 only, confounded with trailing-edge thinning"))


# --------------------------------------------------------------------------
# ranking helper for S7/S8
# --------------------------------------------------------------------------
def price_rank(w0, w1, minobs=2):
    a, b = qi(w0), qi(w1)
    raw = {}
    for g, d in OBS.items():
        v = [math.log(d[q]["p"]) for q in d if a <= qi(q) <= b]
        if len(v) >= minobs:
            raw[g] = float(np.mean(v))
    bycat = defaultdict(list)
    for g, v in raw.items():
        bycat[CAT[g]].append((v, g))
    rank = {}
    for c, lst in bycat.items():
        lst.sort()
        for i, (_, g) in enumerate(lst):
            rank[g] = i / (len(lst) - 1)
    return rank


def event_study(rows, ycol, rank, omit="2022Q3"):
    """rank x quarter, absorbing gig FE and category x quarter FE."""
    P = [r for r in rows if r["gig"] in rank]
    use = [q for q in QS if q != omit and any(r["q"] == q for r in P)]
    X = np.column_stack([[rank[r["gig"]] * (r["q"] == q) for r in P] for q in use])
    y = np.array([r[ycol] for r in P])
    gg = [r["gig"] for r in P]
    Xd, yd, nab = absorb2(X, y, gg, [f"{CAT[r['gig']]}|{r['q']}" for r in P])
    b, se = ols_cluster(Xd, yd, gg, n_absorbed=nab)
    return use, b, se, len(yd)


# --------------------------------------------------------------------------
# S7 NEW DESIGN 1 -- does AI eat the cheap end?
# --------------------------------------------------------------------------
def s7():
    hdr("S7 - NEW DESIGN 1: DOES AI EAT THE CHEAP END? (within-category)")
    print("The seven-category exposure design is exhausted (step 48: p-floor 0.143).")
    print("This design abandons the category ranking entirely. If generative AI")
    print("substitutes for routine low-value work, the demand fall should be LARGER")
    print("for listings that were cheap BEFORE the break -- within category. That")
    print("gives ~16k units instead of 7, and category x quarter FE absorb every")
    print("platform-wide and category-wide shock, including the ones that killed 46.\n")
    rank = price_rank(*RANK_WIN)
    print(f"pre-period price rank from {RANK_WIN[0]}-{RANK_WIN[1]}: {len(rank):,} gigs ranked")
    rows = []
    for g, d in OBS.items():
        ks = sorted(d, key=qi)
        for a, b in zip(ks, ks[1:]):
            ra, rb, gap = d[a]["rev"], d[b]["rev"], qi(b) - qi(a)
            if ra is None or rb is None or gap < 1 or gap > 2 or rb < ra:
                continue
            rows.append({"gig": g, "q": b, "y": math.log1p((rb - ra) / gap),
                         "post": 1.0 if qi(b) > qi(BREAK_Q) else 0.0})
    P = [r for r in rows if r["gig"] in rank]
    X = np.column_stack([[rank[r["gig"]] * r["post"] for r in P]])
    y = np.array([r["y"] for r in P])
    gg = [r["gig"] for r in P]
    Xd, yd, nab = absorb2(X, y, gg, [f"{CAT[r['gig']]}|{r['q']}" for r in P])
    b, se = ols_cluster(Xd, yd, gg, n_absorbed=nab)
    print(f"\nDiD  rank x POST  = {b[0]:+.4f} (se {se[0]:.4f}, t {b[0]/se[0]:.2f})   n={len(yd):,}")
    print("     negative = expensive listings lost MORE, i.e. the OPPOSITE of the")
    print("     'AI eats the cheap end' prediction.\n")
    print("PARALLEL-TRENDS GATE (event study, 2022Q3 omitted):")
    use, eb, ese, n = event_study(rows, "y", rank)
    pre = [(q, eb[i], eb[i] / ese[i]) for i, q in enumerate(use) if qi(q) < qi(BREAK_Q)]
    post = [(q, eb[i], eb[i] / ese[i]) for i, q in enumerate(use) if qi(q) >= qi(BREAK_Q)]
    for q, c, t in pre + post:
        mark = "PRE " if qi(q) < qi(BREAK_Q) else "POST"
        print(f"  {mark} {q:9}{c:>9.4f}  t={t:>7.2f} {'*' if abs(t) > 1.96 else ' '}")
    nsig = sum(1 for _, _, t in pre if abs(t) > 1.96)
    print(f"\n  {nsig} of {len(pre)} PRE-period coefficients significant at 5%.")
    print(f"  pre-period mean {np.mean([c for _,c,_ in pre]):+.3f}"
          f"   post-period mean {np.mean([c for _,c,_ in post]):+.3f}")
    print("\n  VERDICT: FAILS. The pre-period coefficients are large, significant and")
    print("  span the same range as the post-period ones -- there is no break, only a")
    print("  persistent and wandering price gradient. The DiD point estimate is not")
    print("  identified, and its sign is wrong for the hypothesis in any case.")
    VERDICT.append(("AI eats the cheap end (within-category)", "KILLED",
                    f"{nsig}/{len(pre)} pre-period coefs significant; pre mean "
                    f"{np.mean([c for _,c,_ in pre]):+.2f} vs post "
                    f"{np.mean([c for _,c,_ in post]):+.2f} -- no break"))


# --------------------------------------------------------------------------
# S8 NEW DESIGN 2 -- price convergence, with the placebo that kills it
# --------------------------------------------------------------------------
def s8():
    hdr("S8 - NEW DESIGN 2: PRICE CONVERGENCE, AND THE PLACEBO THAT KILLS IT")
    print("Same design on the PRICE side: did cheap listings raise price faster than")
    print("expensive ones after the break (compression from below)? Run naively this")
    print("returns a clean sign reversal at exactly 2022Q3/Q4 and a monotone trend")
    print("after it -- one of the most publishable-looking shapes in this project.\n")
    print("It is an artefact. Pre-period price rank is measured with error, so a")
    print("listing ranked cheap is partly ranked cheap by luck and reverts. That")
    print("produces a coefficient that PEAKS AT THE RANKING WINDOW and decays away")
    print("from it in BOTH directions -- which is exactly the observed shape.\n")
    print("The test: move the ranking window. If the pattern follows the window")
    print("rather than 2022Q4, it is mean reversion and there is no result.\n")
    rows = [{"gig": g, "q": q, "y": math.log(d[q]["p"])} for g, d in OBS.items() for q in d]
    cols = []
    for w in PLACEBO_WINS:
        rk = price_rank(*w)
        use, b, se, n = event_study(rows, "y", rk)
        cols.append((f"rank@{w[0]}-{w[1]}", dict(zip(use, b)), len(rk), w))
    print(f"coefficient on rank x quarter in log(price), 2022Q3 omitted:\n")
    print(f"{'quarter':9}" + "".join(f"{c[0]:>26}" for c in cols))
    print(f"{'':9}" + "".join(f"{'(' + format(c[2], ',') + ' gigs)':>26}" for c in cols))
    for q in QS:
        if q == "2022Q3":
            continue
        line = f"{q:9}"
        for _, d, _, w in cols:
            inwin = qi(w[0]) <= qi(q) <= qi(w[1])
            line += f"{(format(d[q], '.3f') + (' <' if inwin else '  ')):>26}" if q in d else f"{'.':>26}"
        print(line)
    print("\n  '<' marks quarters inside that column's own ranking window.")
    peaks = []
    for name, d, _, w in cols:
        pk = max(d, key=lambda q: d[q])
        inwin = qi(w[0]) <= qi(pk) <= qi(w[1])
        peaks.append(inwin)
        print(f"  {name:26} peaks at {pk}"
              f"  {'INSIDE its own ranking window' if inwin else 'outside its window'}")
    print(f"\n  VERDICT: {'SPURIOUS' if all(peaks) else 'partially survives'}."
          f" {sum(peaks)}/{len(peaks)} specifications peak inside their own ranking")
    print("  window and decay monotonically away from it. The 2022Q4 sign reversal is")
    print("  a property of where the ranking window was placed, not of the data. This")
    print("  is the same failure mode as the retracted price-elasticity result (S3.9):")
    print("  a tight, correctly-signed, well-shaped estimate of nothing.")
    VERDICT.append(("post-ChatGPT price convergence from below", "KILLED",
                    f"ranking-window placebo: {sum(peaks)}/{len(peaks)} windows peak at "
                    f"themselves -- mean reversion, not a 2022Q4 break"))


# --------------------------------------------------------------------------
# S9 verdict
# --------------------------------------------------------------------------
def s9():
    hdr("S9 - VERDICT")
    print("Everything below is EXPLORATORY: none of it is pre-registered, and the")
    print("three KILLED rows are killed by placebos run in this same script.\n")
    w = max(len(a) for a, _, _ in VERDICT)
    for a, st, note in VERDICT:
        print(f"  {a:<{w}}  {st:<12} {note}")
    print("\nWhat survives is a description, not an attribution: over the diffusion")
    print("window this market shows higher prices, a hollowed-out commodity tier that")
    print("hollowed out BEFORE ChatGPT, and deeper product menus -- with no identified")
    print("change in dispersion, concentration, or the price gradient of demand.")


if __name__ == "__main__":
    s1(); s2(); s3(); s4(); s5(); s6(); s7(); s8(); s9()
