#!/usr/bin/env python3
"""
Step 61: Design 11 — staggered niche-level AI arrival, before vs after.

Implements S4-S6 of `plans/active/niche-event-study-prereg.md`. Consumes the
frozen niche assignment and arrival dates from code/60 and never re-derives
them.

  y_it = sum_k beta_k * 1[t - a_n(i) = k] + listing FE + quarter FE + e
  k in [-8, +8], k = -1 omitted. Controls: NEVER-TREATED niches only.
  SEs clustered on niche. Outcomes: log basic price, log review accrual.

Gates, all pre-registered and pass/fail:
  G1 pre-trend (joint + count)     G4 niche randomisation inference
  G2 fake arrival, 8q earlier      G5 balanced event-time composition
  G3 never-treated placebo         G6 realised MDE

Output: runs/niche-event-study.out
"""

import csv
import importlib.util
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "pilot"
CODE = ROOT / "code"

K_LO, K_HI = -8, 8
REF_K = -1
RI_DRAWS = 999
SEED = 20260820
PRE_COUNT_RULE = 2          # >2 significant pre-coefficients fails G1


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, CODE / fn)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


m46 = _load("m46", "46-balanced-demand.py")
m24 = _load("m24", "24-margin-diagnostics.py")
absorb2, ols_cluster = m46.absorb2, m24.ols_cluster

out = []
def say(s=""):
    print(s)
    out.append(s)


def qi(q):
    return int(q[:4]) * 4 + int(q[5]) - 1


# ------------------------------------------------------------------ inputs
niche_of, label_of = {}, {}
for r in csv.DictReader(open(DATA / "niche-assignment.csv", encoding="utf-8")):
    if r["usable"] == "1":
        niche_of[r["gig_id"]] = int(r["niche"])
        label_of[int(r["niche"])] = r["niche_label"]

arrival = {}
for r in csv.DictReader(open(DATA / "niche-arrival.csv", encoding="utf-8")):
    if r["arrival_quarter"]:
        arrival[int(r["niche"])] = r["arrival_quarter"]

rows = []
for r in csv.DictReader(open(DATA / "ai-title-flags.csv", encoding="utf-8")):
    n = niche_of.get(r["gig_id"])
    if n is None:
        continue
    rows.append((r["gig_id"], r["quarter"], n, float(r["price_basic"] or 0),
                 int(r["review_count"] or 0), int(r["ai_gen"])))

say("=" * 74)
say("STEP 61 - DESIGN 11: STAGGERED NICHE AI ARRIVAL, BEFORE vs AFTER")
say("=" * 74)
say()
say(f"  usable niches        : {len(set(niche_of.values())):,}")
say(f"  treated (AI arrived) : {len(arrival):,}")
say(f"  never-treated        : {len(set(niche_of.values())) - len(arrival):,}")
say(f"  gig-quarter rows in  : {len(rows):,}")

# ---------------------------------------------------- S4: build the sample
adopt_q = {}
for g, q, n, p, rc, ai in rows:
    if ai and (g not in adopt_q or qi(q) < qi(adopt_q[g])):
        adopt_q[g] = q
say(f"  listings that ever adopt AI (truncated at adoption): {len(adopt_q):,}")

by_gig = defaultdict(dict)
for g, q, n, p, rc, ai in rows:
    if g in adopt_q and qi(q) >= qi(adopt_q[g]):
        continue                               # S4: leaves at adoption
    by_gig[g][q] = (n, p, rc)

# treated listings must PRE-DATE their niche's arrival
keep = {}
for g, cells in by_gig.items():
    n = next(iter(cells.values()))[0]
    if n in arrival:
        first = min(cells, key=qi)
        if qi(first) >= qi(arrival[n]):
            continue                           # entrant, not an incumbent
    keep[g] = cells
say(f"  listings after incumbency filter                   : {len(keep):,}")
say()

# ------------------------------------------------------- outcome panels
def event_k(n, q):
    if n not in arrival:
        return None                            # never-treated control
    return qi(q) - qi(arrival[n])

price_rows, accr_rows = [], []
for g, cells in keep.items():
    order = sorted(cells, key=qi)
    for q in order:
        n, p, rc = cells[q]
        if p and p > 0:
            k = event_k(n, q)
            if k is None or K_LO <= k <= K_HI:
                price_rows.append((g, q, n, np.log(p), k))
    for a, b in zip(order, order[1:]):
        dq = qi(b) - qi(a)
        if dq <= 0:
            continue
        drev = cells[b][2] - cells[a][2]
        if drev < 0:
            continue
        n = cells[b][0]
        k = event_k(n, b)
        if k is None or K_LO <= k <= K_HI:
            accr_rows.append((g, b, n, float(np.log1p(drev / dq)), k))


def design(panel):
    """-> y, X(event dummies + quarter dummies), niche clusters, gig ids, ks"""
    ks = [k for k in range(K_LO, K_HI + 1) if k != REF_K]
    quarters = sorted({q for _, q, _, _, _ in panel}, key=qi)
    qcol = {q: i for i, q in enumerate(quarters[1:])}      # drop one for FE
    y = np.array([r[3] for r in panel])
    n_obs = len(panel)
    X = np.zeros((n_obs, len(ks) + len(qcol)))
    for i, (g, q, n, _, k) in enumerate(panel):
        if k is not None and k != REF_K:
            X[i, ks.index(k)] = 1.0
        if q in qcol:
            X[i, len(ks) + qcol[q]] = 1.0
    gigs = [r[0] for r in panel]
    nich = [r[2] for r in panel]
    return y, X, np.array(nich), gigs, ks, [r[1] for r in panel]


def fit(panel, tag):
    y, X, nich, gigs, ks, qs = design(panel)
    Xd, yd, nab = absorb2(X, y, gigs, qs)
    b, se = ols_cluster(Xd, yd, nich, n_absorbed=nab)
    return b[:len(ks)], se[:len(ks)], ks, y, X, nich, gigs, qs, len(y)


def wald(b, se, idx, nich_n):
    """Joint chi2 on a coefficient subset, using the diagonal only (conservative
    when off-diagonal covariance is positive); reported alongside the count rule."""
    z = np.array([b[i] / se[i] for i in idx if se[i] > 0])
    return float((z ** 2).sum()), len(z)


def report(tag, panel):
    b, se, ks, y, X, nich, gigs, qs, n = fit(panel, tag)
    say("-" * 74)
    say(f"{tag}   n = {n:,}   listings = {len(set(gigs)):,}   "
        f"niches = {len(set(nich)):,}")
    say("-" * 74)
    say(f"  {'k':>4}  {'coef':>9}  {'se':>8}  {'t':>7}   {'':<22}")
    for i, k in enumerate(ks):
        t = b[i] / se[i] if se[i] > 0 else 0.0
        star = "  *" if abs(t) > 1.96 else ""
        mark = "PRE " if k < 0 else "POST"
        say(f"  {k:>4}  {b[i]:>9.4f}  {se[i]:>8.4f}  {t:>7.2f}   {mark}{star}")
    pre = [i for i, k in enumerate(ks) if k < REF_K]
    post = [i for i, k in enumerate(ks) if k >= 0]
    npre_sig = sum(1 for i in pre if abs(b[i] / se[i]) > 1.96 if se[i] > 0)
    chi2, df = wald(b, se, pre, len(set(nich)))
    avg_post = float(np.mean([b[i] for i in post]))
    say()
    say(f"  average POST coefficient (k=0..8) : {avg_post:+.4f}")
    say(f"  G1 pre-trend: {npre_sig} of {len(pre)} pre-coefficients significant "
        f"(fails if >{PRE_COUNT_RULE})")
    say(f"  G1 joint chi2({df}) on pre-period  : {chi2:.2f}   "
        f"(5% critical ~ {[0,3.8,6.0,7.8,9.5,11.1,12.6,14.1,15.5][min(df,8)]:.1f})")
    g1 = "PASS" if npre_sig <= PRE_COUNT_RULE else "FAIL"
    say(f"  G1 VERDICT: {g1}")
    say()
    return dict(b=b, se=se, ks=ks, avg_post=avg_post, npre_sig=npre_sig,
                chi2=chi2, df=df, g1=g1, n=n, panel=panel)


say("=" * 74)
say("PRIMARY SPECIFICATION")
say("=" * 74)
say()
res_p = report("PRICE   log basic price", price_rows)
res_a = report("DEMAND  log within-gig review accrual", accr_rows)

# ---------------------------------------------------------------- G2, G3
def shift_arrivals(shift):
    return {n: q for n, q in arrival.items()}


def refit_with(arr2, panel_src, tag, treated_only=None):
    """Rebuild event time under an alternative arrival map and refit."""
    pan = []
    for g, q, n, yv, _k in panel_src:
        if n in arr2:
            k = qi(q) - qi(arr2[n])
            if not (K_LO <= k <= K_HI):
                continue
        else:
            k = None
        pan.append((g, q, n, yv, k))
    return report(tag, pan)


say("=" * 74)
say("GATE BATTERY")
say("=" * 74)
say()

say("G2  FAKE ARRIVAL - every treated niche re-dated 8 quarters EARLIER")
say("    (the tool did not exist then; significant post coefficients = the")
say("     design fires at arbitrary dates, which is how design 10's demand")
say("     margin died at a 75% false-positive rate)")
say()
fake = {}
for n, q in arrival.items():
    i = qi(q) - 8
    fake[n] = f"{i//4}Q{i%4+1}"
g2p = refit_with(fake, price_rows, "G2 PRICE  fake arrival -8q")
g2a = refit_with(fake, accr_rows, "G2 DEMAND fake arrival -8q")

say("G3  NEVER-TREATED PLACEBO - controls given fake arrival dates drawn")
say("    from the treated distribution; true treated niches dropped")
say()
rng = np.random.default_rng(SEED)
never = sorted(set(niche_of.values()) - set(arrival))
draw = list(arrival.values())
fake_never = {n: draw[rng.integers(len(draw))] for n in never[:len(never)//2]}
g3p = refit_with(fake_never,
                 [r for r in price_rows if r[2] not in arrival],
                 "G3 PRICE  never-treated placebo")
g3a = refit_with(fake_never,
                 [r for r in accr_rows if r[2] not in arrival],
                 "G3 DEMAND never-treated placebo")

# ------------------------------------------------- G4 randomisation inference
def ri(panel, observed, tag):
    """Permute arrival dates across niches; Frisch-Waugh on a single POST column."""
    quarters = sorted({q for _, q, _, _, _ in panel}, key=qi)
    gigs = [r[0] for r in panel]
    qs = [r[1] for r in panel]
    y = np.array([r[3] for r in panel])
    niches = sorted({r[2] for r in panel})
    # demean y once — the FE structure does not change across draws
    Y = y.reshape(-1, 1)
    Yd, _, _ = absorb2(Y, y, gigs, qs)[0], None, None
    yd = absorb2(np.zeros((len(y), 1)), y, gigs, qs)[1]
    row_n = np.array([r[2] for r in panel])
    row_q = np.array([qi(r[1]) for r in panel])
    arr_dates = list(arrival.values())
    obs_stat = abs(observed)
    hits = 0
    for d in range(RI_DRAWS):
        perm = rng.permutation(len(niches))[:len(arrival)]
        a2 = {niches[perm[i]]: qi(arr_dates[i]) for i in range(len(arrival))}
        post = np.array([1.0 if (n in a2 and t >= a2[n]) else 0.0
                         for n, t in zip(row_n, row_q)])
        pd_ = absorb2(post.reshape(-1, 1), y, gigs, qs)[0][:, 0]
        den = float(pd_ @ pd_)
        if den <= 1e-12:
            continue
        if abs(float(pd_ @ yd) / den) >= obs_stat:
            hits += 1
    p = (hits + 1) / (RI_DRAWS + 1)
    say(f"G4  {tag}: RI p = {p:.3f} over {RI_DRAWS} permutations "
        f"({'PASS' if p <= 0.05 else 'FAIL'})")
    return p


say()
p4p = ri(price_rows, res_p["avg_post"], "PRICE ")
p4a = ri(accr_rows, res_a["avg_post"], "DEMAND")
say()

# ------------------------------------------------------ G5 composition
def balanced(panel):
    need = set(range(-4, 5))
    have = defaultdict(set)
    for g, q, n, yv, k in panel:
        if k is not None:
            have[g].add(k)
    ok = {g for g, ks in have.items() if need <= ks}
    return [r for r in panel if r[2] not in arrival or r[0] in ok], len(ok)


bp, nbp = balanced(price_rows)
ba, nba = balanced(accr_rows)
say(f"G5  balanced-composition check: {nbp:,} price listings and {nba:,} demand")
say("    listings observed at every k in [-4,+4]")
say()
g5p = report("G5 PRICE  balanced event-time", bp) if nbp >= 30 else None
g5a = report("G5 DEMAND balanced event-time", ba) if nba >= 30 else None
if g5p is None:
    say("G5  PRICE  : too few balanced listings to run — recorded as INCONCLUSIVE")
if g5a is None:
    say("G5  DEMAND : too few balanced listings to run — recorded as INCONCLUSIVE")
say()

# ------------------------------------------------------------- G6 power
def mde(res):
    post_se = [res["se"][i] for i, k in enumerate(res["ks"]) if k >= 0]
    return 2.8 * float(np.mean(post_se))


say("G6  REALISED MDE (80% power, 5%, on the average post coefficient)")
say(f"    PRICE  : MDE {mde(res_p):.4f}   estimate {res_p['avg_post']:+.4f}   "
    f"{'ADEQUATE' if abs(res_p['avg_post']) >= mde(res_p) else 'UNDERPOWERED'}")
say(f"    DEMAND : MDE {mde(res_a):.4f}   estimate {res_a['avg_post']:+.4f}   "
    f"{'ADEQUATE' if abs(res_a['avg_post']) >= mde(res_a) else 'UNDERPOWERED'}")
say()

(ROOT / "runs").mkdir(exist_ok=True)
(ROOT / "runs" / "niche-event-study.out").write_text("\n".join(out) + "\n")
say("written: runs/niche-event-study.out")
