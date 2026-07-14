#!/usr/bin/env python3
"""
Step 19: Time-Product-Dummy (TPD) category price indices — the "correctly-timed"
alternative to the chained-Jevons builders (steps 12 + 14).

Motivation
----------
The chained-Jevons panel (12/14) compares each gig to its *previous observed*
quarter. When a gig is sampled sparsely (yearly, or with gaps), a multi-quarter
price change is attributed entirely to the single quarter the gig reappears —
so the quarter-to-quarter index is jumpy and mis-locates *when* prices moved.
(Diagnostic: ~26% of historical and ~39% of recent price changes are such
gap-spanning jumps.)

TPD fixes the timing by estimating, per category, one pooled regression:

    ln p_{i,t} = alpha_i (gig fixed effect) + delta_t (quarter effect) + e_{i,t}

Every observation of every gig contributes to the quarter effects jointly, so a
gig seen only in 2024Q1 and 2025Q1 has its change spread correctly across the
intervening quarters instead of dumped into one. The index for quarter t is
100 * exp(delta_t), with the base quarter's delta pinned to 0.

This mirrors the panel construction of 12/14 EXACTLY (same category assignment,
same gig->quarter median price, same >=2-quarter panel filter) and only swaps
the index computation, so the comparison below is apples-to-apples.

Outputs (new files — the live Jevons CSVs are left untouched):
  data/pilot/panel-category-indices-tpd.csv     (historical, quarterly)
  data/pilot/recent-category-indices-tpd.csv     (recent, quarterly)
and prints a side-by-side comparison of the spliced/re-based composite.
"""

import csv
import math
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import lsqr, splu

BASE_DIR = Path(__file__).resolve().parent.parent
PILOT = BASE_DIR / "data" / "pilot"

HIST_PRICES = PILOT / "pilot-prices.csv"
HIST_ITEMS = PILOT / "gig-items.csv"
RECENT_PRICES = PILOT / "recent-prices.csv"
RECENT_MANIFEST = PILOT / "recent-manifest.tsv"

HIST_JEVONS = PILOT / "panel-category-indices.csv"
RECENT_JEVONS = PILOT / "recent-category-indices.csv"
WEIGHTS_CSV = PILOT / "recent-category-weights.csv"

HIST_OUT = PILOT / "panel-category-indices-tpd.csv"
RECENT_OUT = PILOT / "recent-category-indices-tpd.csv"

CATS = ["audio", "coding", "design", "marketing", "translation", "video", "writing"]
START_Q = "2020Q1"
LINK_Q = "2024Q3"
MIN_GIGS_PER_Q = 3          # a quarter needs >=3 distinct gigs to get an effect
PRICE_MAX = 10000.0

# Historical keyword classifier — identical to 12-panel-ipi.py / 18-build.
CATEGORY_KEYWORDS = {
    "writing": ["write", "article", "blog", "content", "copywriting", "story",
                "ebook", "book", "proofread", "edit", "ghostwrit", "script",
                "resume", "cover letter", "press release"],
    "coding": ["code", "python", "javascript", "app", "mobile app", "web",
               "wordpress", "shopify", "wix", "html", "css", "developer",
               "software", "programming", "script", "api", "database",
               "sql", "discord bot", "game"],
    "design": ["logo", "design", "graphic", "banner", "flyer", "poster",
               "illustration", "draw", "cartoon", "caricature", "infographic",
               "photoshop", "ui", "ux", "brand", "tshirt", "packaging",
               "mockup", "thumbnail", "book cover", "album cover"],
    "translation": ["translat", "spanish", "french", "german", "arabic",
                    "chinese", "japanese", "korean", "hindi", "portuguese"],
    "video": ["video", "animation", "motion", "whiteboard", "explainer",
              "intro", "outro", "edit video", "youtube", "after effects",
              "3d", "render", "model"],
    "audio": ["voice", "voiceover", "narrat", "sing", "music", "audio",
              "podcast", "jingle", "sound", "mixing", "master"],
    "marketing": ["seo", "marketing", "ads", "facebook", "google ads",
                  "social media", "instagram", "tiktok", "email marketing",
                  "ppc", "lead", "traffic"],
}


def classify_gig(description, item_label):
    text = (description + " " + item_label).lower()
    best, best_score = None, 0
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best, best_score = cat, score
    return best


def to_quarter(year, month):
    try:
        y, m = int(year), int(month)
        return f"{y}Q{(m - 1) // 3 + 1}"
    except (ValueError, TypeError):
        return None


def q_to_int(q):
    y, qtr = q.split("Q")
    return int(y) * 10 + int(qtr)


# ---- panel construction (mirrors 12 / 14) ----------------------------------
def build_panel_historical():
    item_map = {}
    with open(HIST_ITEMS) as f:
        for row in csv.DictReader(f):
            item_map[(row["seller"], row["slug"])] = (row["item_label"], row["description"])

    gig_quarter = defaultdict(lambda: defaultdict(list))
    gig_cat = {}
    with open(HIST_PRICES) as f:
        for row in csv.DictReader(f):
            key = (row["seller"], row["slug"])
            item = item_map.get(key)
            if not item:
                continue
            try:
                price = float(row.get("price_basic", 0) or 0)
            except ValueError:
                continue
            if price <= 0 or price > PRICE_MAX:
                continue
            q = to_quarter(row["year"], row["month"])
            if not q:
                continue
            gig_quarter[key][q].append(price)
            if key not in gig_cat:
                gig_cat[key] = classify_gig(item[1], item[0])
    return _collapse(gig_quarter, gig_cat)


def build_panel_recent():
    gig_cat = {}
    with open(RECENT_MANIFEST) as f:
        for row in csv.DictReader(f, delimiter="\t"):
            gid = tuple(row["gig_id"].split("/", 1))
            if len(gid) == 2:
                gig_cat[gid] = row["category"]

    gig_quarter = defaultdict(lambda: defaultdict(list))
    with open(RECENT_PRICES) as f:
        for row in csv.DictReader(f):
            key = (row["seller"], row["slug"])
            if key not in gig_cat:
                continue
            try:
                price = float(row.get("price_basic", 0) or 0)
            except ValueError:
                continue
            if price <= 0 or price > PRICE_MAX:
                continue
            q = to_quarter(row["year"], row["month"])
            if not q:
                continue
            gig_quarter[key][q].append(price)
    return _collapse(gig_quarter, gig_cat)


def _collapse(gig_quarter, gig_cat):
    """-> {category: {gig: {quarter: median_price}}}, panel = gigs with >=2 quarters."""
    by_cat = defaultdict(dict)
    for key, quarters in gig_quarter.items():
        cat = gig_cat.get(key)
        if cat not in CATS:
            continue
        med = {q: float(np.median(ps)) for q, ps in quarters.items()}
        if len(med) >= 2:                      # same >=2-quarter panel filter as 12/14
            by_cat[cat][key] = med
    return by_cat


# ---- Time-Product-Dummy estimator ------------------------------------------
def _largest_component(obs):
    """obs: list of (gig, quarter, logprice). Keep only the largest connected
    component of the bipartite gig<->quarter graph, so every quarter effect is
    identified relative to the base (unconnected quarters can't be compared)."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for g, q, _ in obs:
        union(("g", g), ("q", q))
    comp_size = Counter(find(("g", g)) for g, _, _ in obs)
    if not comp_size:
        return obs
    keep_root = comp_size.most_common(1)[0][0]
    return [o for o in obs if find(("g", o[0])) == keep_root]


def tpd_index(panel_cat):
    """panel_cat: {gig: {quarter: median_price}} -> {quarter: index_level} (base=100)."""
    # quarters need >=3 distinct gigs to earn an effect (parallels 12/14's MIN_RELATIVES=3)
    qcount = Counter(q for qs in panel_cat.values() for q in qs)
    good_q = {q for q, c in qcount.items() if c >= MIN_GIGS_PER_Q}

    obs = [(g, q, math.log(p))
           for g, qs in panel_cat.items()
           for q, p in qs.items() if q in good_q and p > 0]
    # gigs must retain >=2 observations to inform time effects
    gcount = Counter(o[0] for o in obs)
    obs = [o for o in obs if gcount[o[0]] >= 2]
    if not obs:
        return {}
    obs = _largest_component(obs)
    if not obs:
        return {}

    gigs = sorted({o[0] for o in obs})
    quarters = sorted({o[1] for o in obs}, key=q_to_int)
    base = quarters[0]
    gidx = {g: i for i, g in enumerate(gigs)}
    qcol = {q: len(gigs) + j for j, q in enumerate(q for q in quarters if q != base)}

    rows, cols, vals, y = [], [], [], []
    for r, (g, q, lp) in enumerate(obs):
        rows.append(r); cols.append(gidx[g]); vals.append(1.0)
        if q != base:
            rows.append(r); cols.append(qcol[q]); vals.append(1.0)
        y.append(lp)
    yv = np.asarray(y)
    A = csr_matrix((vals, (rows, cols)), shape=(len(obs), len(gigs) + len(qcol)))
    sol = lsqr(A, yv, atol=1e-10, btol=1e-10)[0]

    idx = {base: 100.0}
    for q, c in qcol.items():
        idx[q] = 100.0 * math.exp(sol[c])

    # standard error of each quarter effect (log scale), for confidence bands.
    # Var(beta) = sigma^2 * (X'X)^-1 ; sigma^2 = RSS / (n_obs - n_params).
    # Factorize X'X once, then read the diagonal for each quarter-dummy column.
    se = {base: 0.0}
    resid = A.dot(sol) - yv
    dof = max(1, len(yv) - A.shape[1])
    sigma2 = float(resid.dot(resid)) / dof
    try:
        lu = splu((A.T @ A).tocsc())
        for q, c in qcol.items():
            e = np.zeros(A.shape[1]); e[c] = 1.0
            var = sigma2 * float(lu.solve(e)[c])
            se[q] = math.sqrt(var) if var > 0 else 0.0
    except Exception:
        se = {}   # singular design -> no bands rather than wrong bands
    order = sorted(idx, key=q_to_int)
    return ({q: idx[q] for q in order},
            {q: se.get(q, 0.0) for q in order} if se else {})


def build_tpd(panel_by_cat):
    idx, se = {}, {}
    for cat in CATS:
        if panel_by_cat.get(cat):
            i, s = tpd_index(panel_by_cat[cat])
            if i:
                idx[cat] = i
                if s:
                    se[cat] = s
    return idx, se


# ---- CSV I/O + splice/composite (splice logic mirrors 18-build) ------------
def write_index_csv(path, cat_index, fmt="{:.2f}"):
    quarters = sorted({q for s in cat_index.values() for q in s}, key=q_to_int)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quarter"] + CATS)
        for q in quarters:
            w.writerow([q] + [fmt.format(cat_index[c][q]) if c in cat_index and q in cat_index[c]
                              else "" for c in CATS])


def read_index_csv(path):
    out = defaultdict(dict)
    with open(path) as f:
        for row in csv.DictReader(f):
            q = row["quarter"]
            for cat, val in row.items():
                if cat != "quarter" and val not in (None, ""):
                    out[cat][q] = float(val)
    return out


def chain_category(cat, hist, recent):
    """Splice recent onto historical at the earliest shared quarter, re-base START_Q=100."""
    h, r = hist.get(cat, {}), recent.get(cat, {})
    chained = {}
    common = sorted((set(h) & set(r)), key=q_to_int)
    if common:
        link = common[0]
        link_level = h[link]
        for q, v in h.items():
            if q_to_int(q) < q_to_int(link):
                chained[q] = v
        for q, v in r.items():
            chained[q] = link_level * v / r[link]
    elif r:
        chained = dict(r)
    elif h:
        chained = dict(h)
    else:
        return {}
    base = chained.get(START_Q) or (chained[min(chained, key=q_to_int)] if chained else None)
    if not base:
        return {}
    return {q: 100.0 * v / base for q, v in chained.items()}


def composite_at(levels_by_cat, weights, q):
    ls, ws = 0.0, 0.0
    for cat, s in levels_by_cat.items():
        v, w = s.get(q), weights.get(cat, 0.0)
        if v and v > 0 and w > 0:
            ls += w * math.log(v); ws += w
    return math.exp(ls / ws) if ws > 0 else None


def volatility(series):
    """Mean absolute quarter-to-quarter log change (a jumpiness measure)."""
    vals = [(q, v) for q, v in sorted(series.items(), key=lambda kv: q_to_int(kv[0]))]
    d = [abs(math.log(vals[i][1] / vals[i - 1][1]))
         for i in range(1, len(vals)) if vals[i][1] > 0 and vals[i - 1][1] > 0]
    return 100 * sum(d) / len(d) if d else 0.0


def spliced_composite(hist_csv, recent_csv, weights):
    hist, recent = read_index_csv(hist_csv), read_index_csv(recent_csv)
    chained = {c: chain_category(c, hist, recent) for c in CATS}
    chained = {c: s for c, s in chained.items() if s}
    quarters = sorted({q for s in chained.values() for q in s}, key=q_to_int)
    quarters = [q for q in quarters if q_to_int(q) >= q_to_int(START_Q)]
    comp = {q: composite_at(chained, weights, q) for q in quarters}
    comp = {q: v for q, v in comp.items() if v is not None}
    return chained, comp


def main():
    print("Building TPD indices (historical + recent panels)...")
    hist_panel = build_panel_historical()
    recent_panel = build_panel_recent()
    for tag, panel in (("historical", hist_panel), ("recent", recent_panel)):
        print(f"  {tag}: " + ", ".join(f"{c}={len(panel.get(c, {}))}" for c in CATS) + " panel gigs")

    hist_tpd, hist_se = build_tpd(hist_panel)
    recent_tpd, recent_se = build_tpd(recent_panel)
    write_index_csv(HIST_OUT, hist_tpd)
    write_index_csv(RECENT_OUT, recent_tpd)
    write_index_csv(HIST_OUT.with_name("panel-category-indices-tpd-se.csv"), hist_se, fmt="{:.5f}")
    write_index_csv(RECENT_OUT.with_name("recent-category-indices-tpd-se.csv"), recent_se, fmt="{:.5f}")
    print(f"\nWrote {HIST_OUT.name} and {RECENT_OUT.name} (+ *-se.csv standard errors)")

    weights = {}
    with open(WEIGHTS_CSV) as f:
        for row in csv.DictReader(f):
            weights[row["category"]] = float(row["weight"])

    j_cats, j_comp = spliced_composite(HIST_JEVONS, RECENT_JEVONS, weights)
    t_cats, t_comp = spliced_composite(HIST_OUT, RECENT_OUT, weights)

    print("\n=== COMPOSITE (spliced, re-based 2020Q1=100) — Jevons vs TPD ===")
    print(f"  {'quarter':<9}{'Jevons':>9}{'TPD':>9}{'diff%':>8}")
    allq = sorted(set(j_comp) | set(t_comp), key=q_to_int)
    for q in allq:
        jv, tv = j_comp.get(q), t_comp.get(q)
        diff = f"{(tv/jv-1)*100:+6.1f}" if jv and tv else "     -"
        print(f"  {q:<9}{(f'{jv:8.1f}' if jv else '       -')}"
              f"{(f'{tv:8.1f}' if tv else '       -')}{diff:>8}")

    jf = j_comp[allq[-1]] / j_comp[allq[0]] - 1 if len(allq) > 1 else 0
    tf = t_comp[allq[-1]] / t_comp[allq[0]] - 1 if len(allq) > 1 else 0
    print(f"\n  Full-period composite change:  Jevons {jf*100:+.1f}%   TPD {tf*100:+.1f}%")
    print(f"  Composite jumpiness (mean |QoQ log change|, ×100):"
          f"  Jevons {volatility(j_comp):.2f}   TPD {volatility(t_comp):.2f}")

    print("\n=== PER-CATEGORY final level (2020Q1=100) and jumpiness ===")
    print(f"  {'cat':<12}{'Jevons lvl':>11}{'TPD lvl':>10}{'  Jev jump':>11}{'TPD jump':>10}")
    for c in CATS:
        js, ts = j_cats.get(c, {}), t_cats.get(c, {})
        jl = js[max(js, key=q_to_int)] if js else None
        tl = ts[max(ts, key=q_to_int)] if ts else None
        print(f"  {c:<12}{(f'{jl:11.1f}' if jl else '          -')}"
              f"{(f'{tl:10.1f}' if tl else '         -')}"
              f"{volatility(js):11.2f}{volatility(ts):10.2f}")

    # dump a compact comparison JSON for the overlay chart
    import json
    cmp = {
        "quarters": allq,
        "jevons_composite": [round(j_comp.get(q), 1) if j_comp.get(q) else None for q in allq],
        "tpd_composite": [round(t_comp.get(q), 1) if t_comp.get(q) else None for q in allq],
        "categories": {c: {
            "quarters": sorted(set(j_cats.get(c, {})) | set(t_cats.get(c, {})), key=q_to_int),
        } for c in CATS},
        "final": {c: {"jevons": (round(j_cats[c][max(j_cats[c], key=q_to_int)], 1) if j_cats.get(c) else None),
                      "tpd": (round(t_cats[c][max(t_cats[c], key=q_to_int)], 1) if t_cats.get(c) else None)}
                  for c in CATS},
        "summary": {"jevons_change_pct": round(jf * 100, 1), "tpd_change_pct": round(tf * 100, 1),
                    "jevons_jump": round(volatility(j_comp), 2), "tpd_jump": round(volatility(t_comp), 2)},
    }
    for c in CATS:
        qs = cmp["categories"][c]["quarters"]
        cmp["categories"][c]["jevons"] = [round(j_cats[c][q], 1) if j_cats.get(c, {}).get(q) else None for q in qs]
        cmp["categories"][c]["tpd"] = [round(t_cats[c][q], 1) if t_cats.get(c, {}).get(q) else None for q in qs]
    out = BASE_DIR / "scratchpad" / "tpd-vs-jevons.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump(cmp, f)
    print(f"\nWrote comparison JSON -> {out}")


if __name__ == "__main__":
    main()
