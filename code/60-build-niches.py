#!/usr/bin/env python3
"""
Step 60: Build niches from gig titles, gate them, and date AI arrival per niche.

Implements S1-S3 of `plans/active/niche-event-study-prereg.md` (design 11).
This script is PRE-OUTCOME by construction: it never touches price or review
accrual. It emits a frozen niche assignment and a per-niche AI arrival date,
both of which the estimation step (code/61) consumes without re-deriving.

The same frozen assignment also serves design 9, so the two designs cannot be
accused of choosing different niche definitions to suit their results.

S1  TF-IDF over cleaned titles -> KMeans, target 300-600 niches
S2  adequacy gate: >=30 listings and >=8 quarters. <100 survivors -> ABANDON
S3  arrival: first quarter with AI share >=5% sustained >=2 quarters
    >70% of arrivals in one quarter -> ABANDON (it is design 10 again)

Outputs: data/pilot/niche-assignment.csv, data/pilot/niche-arrival.csv
         runs/niches.out
"""

import csv
import importlib.util
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import Normalizer

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "pilot"
CODE = ROOT / "code"

# --- pre-registered constants (prereg S1-S3) ---
N_NICHES = 450          # midpoint of the registered 300-600 target
LSA_DIMS = 100          # see prereg decision log, 2026-08-20 (deviation 1)
MIN_LISTINGS = 30
MIN_QUARTERS = 8
ARRIVAL_SHARE = 0.05
ARRIVAL_SUSTAIN = 2
# Guards added pre-outcome (prereg decision log, deviation 2). Without them the
# share is computed on any denominator: four niches were dated by a single
# listing and one by 1/1 = 100%. A quarter counts toward arrival only if the
# niche has >=15 observed listings in it AND >=2 of them are AI-branded, so no
# single gig can date a niche.
ARRIVAL_MIN_OBS = 15
ARRIVAL_MIN_AI = 2
MAX_ONE_QUARTER = 0.70
SEED = 20260820


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, CODE / fn)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


m57 = _load("m57", "57-ai-diffusion-titles.py")
clean_title = m57.clean_title

out = []
def say(s=""):
    print(s)
    out.append(s)


# ---------------------------------------------------------------- S1: titles
say("=" * 72)
say("STEP 60 - NICHES, ADEQUACY, AND AI ARRIVAL DATES  (design 11, S1-S3)")
say("=" * 72)
say()

titles = {}          # gig_id -> Counter of cleaned titles
with open(DATA / "balanced-prices.csv", newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        gid = f"{row['seller']}/{row['slug']}"
        t = clean_title(row.get("title"))
        if t:
            titles.setdefault(gid, Counter())[t] += 1

say(f"S1  gigs with at least one usable title : {len(titles):,}")

# panel: gig x quarter, with AI flag and category
panel = []           # (gig_id, quarter, category, ai_gen)
gig_cat = {}
with open(DATA / "ai-title-flags.csv", newline="", encoding="utf-8") as fh:
    for row in csv.DictReader(fh):
        gid = row["gig_id"]
        panel.append((gid, row["quarter"], row["category"], int(row["ai_gen"])))
        gig_cat[gid] = row["category"]

say(f"S1  gig-quarter observations            : {len(panel):,}")

gigs = sorted(set(g for g, _, _, _ in panel) & set(titles))
say(f"S1  gigs with BOTH title and panel row  : {len(gigs):,}")
say()

# Every Fiverr title begins "I will ..." — 39,920 of 39,933 (100.0%). Left in,
# it is a constant that no vectorizer setting removes cleanly, so it is stripped.
BOILERPLATE = re.compile(r"^\s*(i\s+will\s+|will\s+)", re.I)
docs = [BOILERPLATE.sub("", titles[g].most_common(1)[0][0]) for g in gigs]

vec = TfidfVectorizer(
    lowercase=True, stop_words="english",
    ngram_range=(1, 2), min_df=5, max_df=0.35, sublinear_tf=True,
)
X = vec.fit_transform(docs)
say(f"S1  TF-IDF matrix                       : {X.shape[0]:,} x {X.shape[1]:,}")

# Deviation recorded in the prereg decision log: KMeans on the raw sparse
# TF-IDF matrix is degenerate here — MiniBatchKMeans put 33,971 of 39,933 gigs
# (85.1%) into one cluster and only 41 clusters cleared 30 members. Reducing to
# an LSA space first and running full KMeans fixes it. Pre-outcome fix; no
# price or accrual variable has been read at this point.
svd = TruncatedSVD(n_components=LSA_DIMS, random_state=SEED)
Xr = Normalizer().fit_transform(svd.fit_transform(X))
say(f"S1  LSA dims / explained variance       : {LSA_DIMS} / "
    f"{svd.explained_variance_ratio_.sum():.3f}")

km = KMeans(n_clusters=N_NICHES, random_state=SEED, n_init=3, max_iter=300)
lab = km.fit_predict(Xr)
sizes = Counter(lab)
say(f"S1  KMeans niches requested             : {N_NICHES}")
say(f"S1  niches actually populated           : {len(sizes):,}")
say(f"S1  largest niche                       : {max(sizes.values()):,} "
    f"({100*max(sizes.values())/len(gigs):.1f}% of gigs)")
say()

niche_of = dict(zip(gigs, lab))

# human-readable niche labels: top TF-IDF terms per centroid
terms = np.array(vec.get_feature_names_out())
centroids = svd.inverse_transform(km.cluster_centers_)   # back to term space
order = centroids.argsort()[:, ::-1]
niche_label = {n: " / ".join(terms[order[n, :3]]) for n in range(N_NICHES)}

# ------------------------------------------------------- S2: adequacy gate
listings_per = Counter(niche_of[g] for g in gigs)
qtrs_per = defaultdict(set)
for gid, q, _, _ in panel:
    if gid in niche_of:
        qtrs_per[niche_of[gid]].add(q)

usable = {n for n in listings_per
          if listings_per[n] >= MIN_LISTINGS and len(qtrs_per[n]) >= MIN_QUARTERS}

say("-" * 72)
say(f"S2  ADEQUACY GATE  (>={MIN_LISTINGS} listings and >={MIN_QUARTERS} quarters)")
say("-" * 72)
say(f"    niches populated                    : {len(listings_per):,}")
say(f"    fail on listings                    : {sum(1 for n in listings_per if listings_per[n] < MIN_LISTINGS):,}")
say(f"    fail on quarters                    : {sum(1 for n in listings_per if len(qtrs_per[n]) < MIN_QUARTERS):,}")
say(f"    USABLE NICHES                       : {len(usable):,}")
sz = sorted(listings_per[n] for n in usable)
if sz:
    say(f"    listings per usable niche           : median {sz[len(sz)//2]}, "
        f"p10 {sz[len(sz)//10]}, p90 {sz[9*len(sz)//10]}, max {sz[-1]}")
    say(f"    listings covered by usable niches   : {sum(sz):,} of {len(gigs):,} "
        f"({100*sum(sz)/len(gigs):.1f}%)")
say()
if len(usable) < 100:
    say("    *** GATE S2 FAILED - fewer than 100 usable niches. DESIGN ABANDONED. ***")
    (ROOT / "runs").mkdir(exist_ok=True)
    (ROOT / "runs" / "niches.out").write_text("\n".join(out) + "\n")
    sys.exit(0)
say(f"    GATE S2 PASSED ({len(usable)} >= 100)")
say()

# --------------------------------------------------- S3: date AI arrival
nq_tot = Counter()
nq_ai = Counter()
for gid, q, _, ai in panel:
    n = niche_of.get(gid)
    if n is None or n not in usable:
        continue
    nq_tot[(n, q)] += 1
    nq_ai[(n, q)] += ai

quarters = sorted({q for _, q in nq_tot})
qidx = {q: i for i, q in enumerate(quarters)}

arrival = {}
peak_share = {}
for n in sorted(usable):
    ok, shares = [], []
    for q in quarters:
        tot = nq_tot.get((n, q), 0)
        a = nq_ai.get((n, q), 0)
        shares.append(a / tot if tot else None)
        ok.append(tot >= ARRIVAL_MIN_OBS and a >= ARRIVAL_MIN_AI
                  and tot and a / tot >= ARRIVAL_SHARE)
    # peak share reported only on quarters thick enough to mean anything
    thick = [s for s, q in zip(shares, quarters)
             if s is not None and nq_tot.get((n, q), 0) >= ARRIVAL_MIN_OBS]
    peak_share[n] = max(thick, default=0.0)
    for i in range(len(quarters) - ARRIVAL_SUSTAIN + 1):
        if all(ok[i:i + ARRIVAL_SUSTAIN]):
            arrival[n] = quarters[i]
            break

treated = sorted(arrival)
never = sorted(usable - set(arrival))

say("-" * 72)
say(f"S3  AI ARRIVAL  (share >={ARRIVAL_SHARE:.0%}, >={ARRIVAL_MIN_AI} AI listings, "
    f">={ARRIVAL_MIN_OBS} observed, sustained {ARRIVAL_SUSTAIN} quarters)")
say("-" * 72)
say(f"    TREATED niches (AI arrived)         : {len(treated):,}")
say(f"    NEVER-TREATED controls              : {len(never):,}")
say()
say("    arrival quarter distribution")
dist = Counter(arrival.values())
for q in sorted(dist):
    bar = "#" * min(60, dist[q])
    say(f"      {q}  {dist[q]:4d}  {bar}")
say()
if treated:
    top = dist.most_common(1)[0]
    frac = top[1] / len(treated)
    say(f"    largest single arrival quarter      : {top[0]} at {frac:.1%} of treated")
    if frac > MAX_ONE_QUARTER:
        say(f"    *** GATE S3 FAILED - arrivals not staggered ({frac:.1%} > {MAX_ONE_QUARTER:.0%}). ***")
        say("    *** This is design 10 with extra steps. DESIGN ABANDONED. ***")
    else:
        say(f"    GATE S3 PASSED - arrivals are staggered ({frac:.1%} <= {MAX_ONE_QUARTER:.0%})")
    say(f"    distinct arrival quarters           : {len(dist)}")
say()

say("    twenty largest treated niches, by listing count")
say(f"      {'n':>4}  {'gigs':>5}  {'arrive':>7}  {'peak AI':>7}  label")
for n in sorted(treated, key=lambda n: -listings_per[n])[:20]:
    say(f"      {n:>4}  {listings_per[n]:>5}  {arrival[n]:>7}  "
        f"{peak_share[n]:>6.1%}  {niche_label[n][:44]}")
say()
say("    ten largest never-treated niches (the control pool)")
for n in sorted(never, key=lambda n: -listings_per[n])[:10]:
    say(f"      {n:>4}  {listings_per[n]:>5}  {'never':>7}  "
        f"{peak_share[n]:>6.1%}  {niche_label[n][:44]}")
say()

# category composition of treated vs never
say("    where AI arrived, by category")
say(f"      {'category':<12} {'treated':>8} {'never':>7} {'% treated':>10}")
cat_t, cat_n = Counter(), Counter()
for n in usable:
    members = [g for g in gigs if niche_of[g] == n]
    modal = Counter(gig_cat[g] for g in members).most_common(1)[0][0]
    (cat_t if n in arrival else cat_n)[modal] += 1
for c in sorted(set(cat_t) | set(cat_n), key=lambda c: -(cat_t[c] + cat_n[c])):
    tot = cat_t[c] + cat_n[c]
    say(f"      {c:<12} {cat_t[c]:>8} {cat_n[c]:>7} {cat_t[c]/tot:>9.1%}")
say()

# ------------------------------------------------------------- outputs
with open(DATA / "niche-assignment.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["gig_id", "niche", "niche_label", "usable"])
    for g in gigs:
        n = niche_of[g]
        w.writerow([g, n, niche_label[n], int(n in usable)])

with open(DATA / "niche-arrival.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["niche", "niche_label", "n_listings", "arrival_quarter", "peak_ai_share"])
    for n in sorted(usable):
        w.writerow([n, niche_label[n], listings_per[n],
                    arrival.get(n, ""), f"{peak_share[n]:.4f}"])

say("outputs")
say("  data/pilot/niche-assignment.csv")
say("  data/pilot/niche-arrival.csv")
say("  runs/niches.out")

(ROOT / "runs").mkdir(exist_ok=True)
(ROOT / "runs" / "niches.out").write_text("\n".join(out) + "\n")
