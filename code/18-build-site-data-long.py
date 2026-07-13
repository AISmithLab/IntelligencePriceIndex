#!/usr/bin/env python3
"""
Step 18: Build the FULL-HISTORY data.json the IPI website consumes (2020 -> 2026).

Supersedes the trailing-12-month build (step 15/17) for the site display. Two
datasets are chained into a single continuous QUARTERLY per-category index:

  - Historical panel (the March 500-seller pilot) -> data/pilot/panel-category-indices.csv
    Matched-model quarterly index, dense 2018-2024, base 2019Q1=100. We use it for
    2020Q1 .. the splice quarter.
  - Recent panel (the trailing-window crawl) -> data/pilot/recent-category-indices.csv
    Matched-model quarterly index, base 2024Q3=100, covering 2024Q3 .. 2026Q1. We
    splice it onto the historical level at the shared 2024Q3 link (ratio splice), so
    the recent segment continues the historical level rather than restarting at 100.

The whole chained series is then re-based to 2020Q1 = 100. Quarterly (not mixed
monthly/quarterly) keeps the x-axis uniform and comparable, and quarterly is the
more robust cadence for the thin categories (see recent-ipi-summary.md).

Composite is recomputed client-side from the per-category index + review weights
(recent-category-weights.csv) as exp(Sum w*ln(idx) / Sum w) -- unchanged contract.

Also emits a `rankings` block: per category, the top freelancers by number of
distinct gigs/services they offer, derived from the recent manifest.

Output: docs/data.json
"""

import csv
import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PILOT = BASE_DIR / "data" / "pilot"
HIST_CSV = PILOT / "panel-category-indices.csv"
RECENT_CSV = PILOT / "recent-category-indices.csv"
# Corrected (time-dummy / TPD) category indices from code/19-tpd-index.py.
# Spliced + re-based identically to the Jevons pair; emitted as a parallel
# `index_tpd` block so the site can draw the drift-free index under the main one.
HIST_TPD_CSV = PILOT / "panel-category-indices-tpd.csv"
RECENT_TPD_CSV = PILOT / "recent-category-indices-tpd.csv"
WEIGHTS_CSV = PILOT / "recent-category-weights.csv"
MANIFEST = PILOT / "recent-manifest.tsv"
HIST_PRICES = PILOT / "pilot-prices.csv"     # historical extracted prices (2011->2026)
RECENT_PRICES = PILOT / "recent-prices.csv"  # recent-window extracted prices (2024->2026)
HIST_ITEMS = PILOT / "gig-items.csv"         # (seller, slug) -> item_label/description
OUT = BASE_DIR / "docs" / "data.json"
FREELANCERS_OUT = BASE_DIR / "docs" / "freelancers.json"  # per-seller gig price series

START_Q = "2020Q1"          # first displayed quarter
START_YEAR = 2020           # rankings count gigs observed in this year or later
LINK_Q = "2024Q3"           # shared quarter used to splice recent onto historical
TOP_N = 25                  # freelancers listed per category ranking

# Fiverr URL path segments that are NOT seller handles (landing/section pages).
# gig_id is "seller/slug"; when the first segment is one of these it's not a gig.
RESERVED = {"hire", "agencies", "categories", "category", "search", "gig", "gigs",
            "s", "users", "user", "profile", "inbox", "support", "help", "business",
            "pro", "resource", "resources", "cp", "community", "blog", "invite",
            "logo-maker", "start_selling", "seller_onboarding", "login", "join"}

# broad categories that make up the basket (order/labels/colors for display)
CATS = ["audio", "coding", "design", "marketing", "translation", "video", "writing"]
LABELS = {"audio": "Audio", "coding": "Coding", "design": "Design",
          "marketing": "Marketing", "translation": "Translation",
          "video": "Video", "writing": "Writing"}
# Distinct categorical palette (CVD-safe as a set: worst all-pairs ΔE 12.9;
# validated via dataviz validate_palette.js on the #fcfcfb light surface).
# Dominant design line gets the high-contrast blue; low-contrast hues
# (aqua/yellow/magenta) sit on thinner categories.
COLORS = {"design": "#2a78d6", "coding": "#008300", "writing": "#4a3aa7",
          "video": "#e34948", "audio": "#1baf7a", "marketing": "#eda100",
          "translation": "#e87ba4"}

# Keyword classifier for HISTORICAL gigs (recent gigs already carry a category).
# Kept identical to code/12-panel-ipi.py so historical rankings use the same
# taxonomy the historical price index was built with.
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
    return best   # None if nothing matched (gig dropped from rankings)


# ---- quarter helpers -------------------------------------------------------
def q_to_int(q):
    """'2020Q3' -> 20203 (sortable/orderable integer)."""
    y, qtr = q.split("Q")
    return int(y) * 10 + int(qtr)


def quarters(start, end):
    out, cur = [], q_to_int(start)
    end_i = q_to_int(end)
    while cur <= end_i:
        y, qq = divmod(cur, 10)
        out.append(f"{y}Q{qq}")
        qq += 1
        cur = (y + 1) * 10 + 1 if qq > 4 else y * 10 + qq
    return out


def read_index_csv(path):
    """Read a quarter-indexed per-category CSV -> {category: {quarter: value}}."""
    out = defaultdict(dict)
    with open(path) as f:
        r = csv.DictReader(f)
        for row in r:
            q = row["quarter"]
            for cat, val in row.items():
                if cat == "quarter" or val in (None, ""):
                    continue
                out[cat][q] = float(val)
    return out


# ---- chained index ---------------------------------------------------------
def chain_category(cat, hist, recent):
    """Splice recent onto historical at LINK_Q, then re-base so START_Q = 100.
    Returns {quarter: level} (only quarters with data)."""
    h, r = hist.get(cat, {}), recent.get(cat, {})
    chained = {}

    # link at the EARLIEST quarter present in both panels, so we switch to the
    # denser recent crawl as soon as it starts (historical goes sparse post-2024).
    common = sorted((set(h) & set(r)), key=q_to_int)
    common = [q for q in common if r.get(q)]
    if common:
        link = common[0]
        link_level = h[link]
        for q, v in h.items():
            if q_to_int(q) < q_to_int(link):
                chained[q] = v
        for q, v in r.items():                       # includes the link quarter itself
            chained[q] = link_level * v / r[link]
    elif r:                                            # recent only (e.g. thin cats)
        chained = dict(r)
    elif h:                                            # historical only
        chained = dict(h)
    else:
        return {}

    # re-base to START_Q = 100 (or the first available quarter if START_Q missing)
    base = chained.get(START_Q)
    if base is None:
        for q in sorted(chained, key=q_to_int):
            base = chained[q]
            break
    if not base:
        return {}
    return {q: 100.0 * v / base for q, v in chained.items()}


def composite(levels_by_cat, weights, q):
    log_sum, w_sum = 0.0, 0.0
    for cat, series in levels_by_cat.items():
        v, w = series.get(q), weights.get(cat, 0.0)
        if v and v > 0 and w > 0:
            log_sum += w * math.log(v)
            w_sum += w
    return math.exp(log_sum / w_sum) if w_sum > 0 else None


# ---- freelancer rankings + per-gig price series ----------------------------
def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _compress_series(points):
    """points: list of (date, basic, standard, premium). Sort, dedupe consecutive
    rows with identical (b, s, p) — most gigs are flat for long stretches — while
    always keeping the first and last observation so the line spans the full range."""
    pts = sorted(set(points))
    out, prev = [], object()
    for d, b, s, p in pts:
        key = (b, s, p)
        if key != prev:
            out.append([d, b, s, p])
            prev = key
    if pts and out[-1][0] != pts[-1][0]:
        d, b, s, p = pts[-1]
        out.append([d, b, s, p])
    return out


def build_rankings():
    """Per category: sellers ranked by number of distinct PRICED gigs across the
    2020->2026 span, plus the per-gig price-over-time series for the top sellers.

    Prices are the source of truth here (not the CDX manifest counts), so every
    listed freelancer is expandable with a real chart. Category per gig comes from
    the recent manifest (gig_id -> category) where available, else from classifying
    the gig's item text (historical gigs), matching the price-index taxonomy.

    Returns (summary, detail):
      summary  {cat: {"sellers": total, "top": [{seller, gigs}]}}       -> data.json
      detail   {seller: {"gigs": [{slug, cat, title, url, series}]}}    -> freelancers.json
               (series = [[date, basic, standard, premium], ...], change-points only)
    """
    # gig_id ('seller/slug') -> category, from the recent manifest (authoritative
    # for recent gigs; carries Fiverr's own category label).
    manifest_cat = {}
    with open(MANIFEST) as f:
        for row in csv.DictReader(f, delimiter="\t"):
            manifest_cat[row["gig_id"]] = row["category"]

    # (seller, slug) -> item text, for classifying historical gigs.
    item_map = {}
    with open(HIST_ITEMS) as f:
        for row in csv.DictReader(f):
            item_map[(row["seller"], row["slug"])] = (row["item_label"],
                                                      row["description"])
    cat_cache = {}

    def cat_of(seller, slug):
        gid = f"{seller}/{slug}"
        if gid in manifest_cat:
            return manifest_cat[gid]
        key = (seller, slug)
        if key not in cat_cache:
            item = item_map.get(key)
            cat_cache[key] = classify_gig(item[1], item[0]) if item else None
        return cat_cache[key]

    # cat -> seller -> slug -> {"title", "pts"}
    series = defaultdict(lambda: defaultdict(lambda: defaultdict(
        lambda: {"title": "", "pts": []})))
    for price_file in (HIST_PRICES, RECENT_PRICES):
        if not price_file.exists():
            continue
        with open(price_file) as f:
            for row in csv.DictReader(f):
                try:
                    if int(row["year"]) < START_YEAR:
                        continue
                except (ValueError, TypeError):
                    continue
                seller, slug = row["seller"], row["slug"]
                if seller in RESERVED:
                    continue
                cat = cat_of(seller, slug)
                if cat not in CATS:
                    continue
                g = series[cat][seller][slug]
                if row.get("title"):
                    g["title"] = row["title"]
                g["pts"].append((row["date"], _num(row["price_basic"]),
                                 _num(row["price_standard"]),
                                 _num(row["price_premium"])))

    summary, detail = {}, {}
    for cat in CATS:
        sellers = series.get(cat, {})
        ranked = sorted(((s, g) for s, g in sellers.items()),
                        key=lambda x: (-len(x[1]), x[0]))
        summary[cat] = {
            "sellers": len(sellers),
            "top": [{"seller": s, "gigs": len(g)} for s, g in ranked[:TOP_N]],
        }
        for seller, gigs in ranked[:TOP_N]:
            node = detail.setdefault(seller, {"gigs": []})
            for slug, v in gigs.items():
                ser = _compress_series(v["pts"])
                if not ser:
                    continue
                last_date = ser[-1][0]
                node["gigs"].append({
                    "slug": slug,
                    "cat": cat,
                    "title": v["title"][:140],
                    "url": (f"https://web.archive.org/web/{last_date}/"
                            f"https://www.fiverr.com/{seller}/{slug}"),
                    "series": ser,
                })
    return summary, detail


# ---- assemble --------------------------------------------------------------
def main():
    hist = read_index_csv(HIST_CSV)
    recent = read_index_csv(RECENT_CSV)

    weights = {}
    panel_gigs = {}
    with open(WEIGHTS_CSV) as f:
        for row in csv.DictReader(f):
            weights[row["category"]] = float(row["weight"])
            panel_gigs[row["category"]] = int(row["panel_gigs"])

    # last quarter present anywhere in the recent panel = end of the axis
    last_q = max((q for c in recent.values() for q in c), key=q_to_int)
    qs = quarters(START_Q, last_q)

    chained = {}
    for cat in CATS:
        s = chain_category(cat, hist, recent)
        if s:
            chained[cat] = s
    cats = [c for c in CATS if c in chained]

    def aligned(chained_by_cat):
        """Forward-fill each category's chained level onto the display quarters qs
        (None until first observed, then carried across gaps so lines stay whole)."""
        out = {}
        for c in cats:
            ch = chained_by_cat.get(c, {})
            series, last = [], None
            for q in qs:
                if q in ch:
                    last = round(ch[q], 2)
                first_seen = any(qq in ch for qq in qs[:qs.index(q) + 1])
                series.append(last if first_seen else None)
            out[c] = series
        return out

    def fill_composite(chained_by_cat):
        comp = [composite({c: chained_by_cat[c] for c in chained_by_cat}, weights, q) for q in qs]
        filled, last = [], None
        for v in comp:
            if v is not None:
                last = v
            filled.append(round(last, 2) if last is not None else None)
        return filled

    index = aligned(chained)
    comp = fill_composite(chained)

    # corrected (time-dummy / TPD) index — spliced + re-based the same way,
    # aligned to the same quarters and category set for the second chart.
    hist_tpd = read_index_csv(HIST_TPD_CSV)
    recent_tpd = read_index_csv(RECENT_TPD_CSV)
    chained_tpd = {}
    for cat in cats:
        s = chain_category(cat, hist_tpd, recent_tpd)
        if s:
            chained_tpd[cat] = s
    index_tpd = aligned(chained_tpd)
    comp_tpd = fill_composite(chained_tpd)

    def full_delta(series):
        a = next((v for v in series if v is not None), None)
        b = next((v for v in reversed(series) if v is not None), None)
        return round((b / a - 1) * 100, 1) if a and b and a > 0 else None

    delta = {c: full_delta(index[c]) for c in cats}
    delta["composite"] = full_delta(comp)
    delta_tpd = {c: full_delta(index_tpd[c]) for c in cats}
    delta_tpd["composite"] = full_delta(comp_tpd)

    rankings, freelancers = build_rankings()

    data = {
        "generated": date.today().isoformat(),
        "cadence": "quarterly",
        "base_period": START_Q,
        "categories": cats,
        "weights": {c: round(weights.get(c, 0.0), 6) for c in cats},
        "panel_gigs": {c: panel_gigs.get(c) for c in cats},
        "months": qs,                       # quarter labels (key kept for JS compat)
        "index": index,
        "composite_all": comp,
        "delta12": {k: v for k, v in delta.items()},   # now full-period change
        "index_tpd": index_tpd,                        # corrected (time-dummy) index
        "composite_tpd": comp_tpd,
        "delta_tpd": delta_tpd,
        "labels": {c: LABELS[c] for c in cats},
        "colors": {c: COLORS[c] for c in cats},
        "rankings": rankings,
        "has_freelancer_detail": True,   # tells the site freelancers.json exists
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
    with open(FREELANCERS_OUT, "w") as f:
        json.dump(freelancers, f, separators=(",", ":"))

    # ---- report ----
    print(f"Wrote {OUT}  ({OUT.stat().st_size/1024:.1f} KB)")
    print(f"Axis: {qs[0]} -> {qs[-1]} ({len(qs)} quarters), base {START_Q}=100, splice {LINK_Q}")
    print(f"Categories ({len(cats)}): {', '.join(cats)}")
    print("\nComposite (all categories):")
    for q, v in zip(qs, comp):
        bar = "#" * int((v or 0) / 8)
        print(f"  {q:<7} {('%7.1f' % v) if v else '    n/a'}  {bar}")
    print(f"\nFull-period change {qs[0]}->{qs[-1]}:  composite {delta['composite']:+.1f}%")
    print("Per-category full-period change:")
    for c in sorted(cats, key=lambda x: delta[x] if delta[x] is not None else 0):
        d = delta[c]
        print(f"  {c:<12} {d:+7.1f}%" if d is not None else f"  {c:<12}     n/a")
    print("\nTop freelancer per category (by distinct priced gigs):")
    for c in cats:
        top = data["rankings"][c]["top"]
        if top:
            print(f"  {c:<12} {top[0]['seller']} ({top[0]['gigs']} gigs)  "
                  f"[{data['rankings'][c]['sellers']} priced sellers]")
    n_gigs = sum(len(v["gigs"]) for v in freelancers.values())
    print(f"\nWrote {FREELANCERS_OUT}  ({FREELANCERS_OUT.stat().st_size/1024:.0f} KB)"
          f"  {len(freelancers)} sellers, {n_gigs} gigs with price series")


if __name__ == "__main__":
    main()
