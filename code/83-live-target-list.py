#!/usr/bin/env python3
"""
83 — Which gigs to open in a live browser session, in what order.

WHY THIS EXISTS. `runs/cdx-refresh-2025/2026-edge.md` closes both archives on the
2026 window: Wayback's fiverr crawl stops after 2026Q1 (prefix `z` has 173 captures
in 2026Q1 and 21 across 2026Q2+Q3, one of them a 200), and Common Crawl returns a
single index block for fiverr.com in Aug 2026, Aug 2025 and Aug 2024 alike, whose
only 200s are robots.txt. The sole remaining route to 2026Q2-Q3 is a live page.

Live pages are 403 to scripted requests (step 80: 15/15, PerimeterX), so collection
runs in the operator's own browser at human pace. That makes the page budget SMALL —
hundreds, not the 291k that exist — and the ordering of the list is therefore the
whole design.

WHAT A LIVE PAGE IS WORTH. Not the listed price: one 2026Q3 listing pairs with a
2025 listing at a 4-6 quarter gap, which no adjacent-quarter chain can use. The value
is the embedded `reviews` blob step 59 found, whose records carry `created_at` (ORDER
date) and `price_range_start/end` (what the buyer PAID). Step 63b measured the reach:
median lag 2 months, 74.7% of displayed orders within 3 months, 90.2% within 12. So a
page opened in 2026-09 is mostly a window onto 2026Q2-Q3 — exactly the missing
quarters — and step 63A found no price selection in late-fetched pages (median
realised value late minus early +0 USD, bootstrap CI [+0, +0]).

SELECTION, STATED PLAINLY. Two selections are already unavoidable and one is ours:

  * Survivorship (step 63B). A live fetch reaches only gigs still listed — 32.1% of
    the panel, and skewed: 43.8% of the top listed-price quartile against 22.4% of
    the bottom, 55.0% of the top review-count quartile against 20.8% of the bottom.
    Nothing in the ordering can undo this; it is a property of what still exists.
  * Display (step 59). A page shows ~4 of ~124 reviews, ranked by relevancy_score.
  * OURS: order-yield rises with review count, so a greedy list would be all
    head gigs and would compound the survivorship skew. It is therefore NOT greedy.
    Targets are drawn as a stratified sample — equal quota per category, and within
    a category equal quota across review-count quartiles measured on the PANEL, not
    on survivors. Rank within a stratum is random under a fixed seed, so a truncated
    session (the operator stops at page 200) is still a probability sample of the
    stratum and not its head.

Tiers are cumulative and cut on that shuffled order, so tier 1 is a valid small
sample on its own — the pilot-before-scale unit — and tier 2 extends it without
re-drawing.

Inputs:  data/pilot/balanced-prices.csv, data/pilot/refresh2025-prices.csv
         data/pilot/balanced-gig-category.csv.gz
         data/fiverr-live/gig-urls-YYYY-MM-DD.txt.gz   (newest, step 80)
Output:  data/fiverr-live/live-targets-<date>.tsv
         runs/live-collection/targets-<date>.md
"""

import argparse
import csv
import gzip
import random
import sys
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PRICE_FILES = [
    BASE_DIR / "data" / "pilot" / "balanced-prices.csv",
    BASE_DIR / "data" / "pilot" / "refresh2025-prices.csv",
]
CATEGORIES = BASE_DIR / "data" / "pilot" / "balanced-gig-category.csv.gz"
LIVE_DIR = BASE_DIR / "data" / "fiverr-live"
RUNDIR = BASE_DIR / "runs" / "live-collection"
SEED = 83

# Tier 1 is the pilot: small enough to sit through in one session, big enough that
# "zero orders recovered" would be a real answer rather than bad luck.
TIER_SIZES = [(1, 140), (2, 560), (3, 1400)]


def newest_sitemap():
    caps = sorted(LIVE_DIR.glob("gig-urls-*.txt.gz"))
    if not caps:
        sys.exit("no sitemap capture in data/fiverr-live/ — run code/80-fiverr-sitemap-census.py")
    return caps[-1]


def load_live(path):
    with gzip.open(path, "rt") as f:
        return {line.strip() for line in f if line.strip()}


def load_categories():
    cats = {}
    with gzip.open(CATEGORIES, "rt") as f:
        for row in csv.DictReader(f):
            cats[row["gig_id"]] = row["category"]
    return cats


def load_panel():
    """gig_id -> last observation on the panel.

    Last, not first: the pair a live page forms is against the most recent listed
    price we hold, and the review-count quartile has to be measured at the same
    moment as the price it is stratifying.
    """
    last = {}
    for path in PRICE_FILES:
        if not path.exists():
            print(f"  (skipping absent {path.name})")
            continue
        n = 0
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                seller, slug, date = row["seller"], row["slug"], row["date"]
                if not seller or not slug or not date:
                    continue
                gig = f"{seller}/{slug}"
                prev = last.get(gig)
                if prev is None or date > prev["date"]:
                    last[gig] = {
                        "date": date,
                        "year": row.get("year", ""),
                        "month": row.get("month", ""),
                        "price_basic": row.get("price_basic", ""),
                        "review_count": row.get("review_count", ""),
                        "rating": row.get("rating", ""),
                        "title": row.get("title", ""),
                    }
                n += 1
        print(f"  {path.name}: {n:,} rows")
    return last


def as_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def quartile_cuts(values):
    """Cuts on the PANEL distribution, so the strata are properties of the market
    rather than of who survived — otherwise the quartiles drift with attrition."""
    vs = sorted(values)
    if not vs:
        return (0, 0, 0)
    return tuple(vs[int(len(vs) * q)] for q in (0.25, 0.50, 0.75))


def quartile_of(v, cuts):
    if v is None:
        return "Qna"
    return "Q1" if v <= cuts[0] else "Q2" if v <= cuts[1] else "Q3" if v <= cuts[2] else "Q4"


def quarter(v):
    """The panel writes `date` as YYYYMMDD and carries `year`/`month` alongside it;
    take the explicit fields rather than slicing, which is what produced the
    nonsense '2019Q11' labels on the first run of this step."""
    y, m = v.get("year", ""), as_int(v.get("month"))
    if not y or m is None or not 1 <= m <= 12:
        return ""
    return f"{y}Q{(m - 1) // 3 + 1}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-date", default=None, help="stamp for the output filename")
    args = ap.parse_args()

    sitemap = newest_sitemap()
    stamp = args.out_date or sitemap.stem.replace("gig-urls-", "").replace(".txt", "")

    print("Loading inputs")
    live = load_live(sitemap)
    print(f"  {sitemap.name}: {len(live):,} live gigs")
    cats = load_categories()
    print(f"  categories: {len(cats):,} gigs")
    panel = load_panel()
    print(f"  panel: {len(panel):,} distinct gigs")

    # Quartile cuts on the whole panel, before any survivorship filter.
    rc_cuts = quartile_cuts([r for r in (as_int(v["review_count"]) for v in panel.values())
                             if r is not None])
    print(f"  review-count quartile cuts (panel): {rc_cuts}")

    reachable = {g: v for g, v in panel.items() if g in live}
    print(f"  still listed 2026: {len(reachable):,} of {len(panel):,} "
          f"({100 * len(reachable) / max(len(panel), 1):.1f}%)")

    # Stratify: category x review-count quartile.
    strata = defaultdict(list)
    for gig, v in reachable.items():
        cat = cats.get(gig)
        if not cat:
            continue  # uncategorised gigs are outside every published domain
        strata[(cat, quartile_of(as_int(v["review_count"]), rc_cuts))].append(gig)

    rng = random.Random(SEED)
    for key in strata:
        strata[key].sort()          # deterministic before shuffling
        rng.shuffle(strata[key])

    # Round-robin across strata: equal quota per category and per quartile, and the
    # list stays balanced at EVERY prefix length, so stopping early costs balance
    # rather than breaking it.
    keys = sorted(strata)
    order, cursors, exhausted = [], {k: 0 for k in keys}, set()
    while len(exhausted) < len(keys):
        for k in keys:
            if k in exhausted:
                continue
            i = cursors[k]
            if i >= len(strata[k]):
                exhausted.add(k)
                continue
            order.append((k, strata[k][i]))
            cursors[k] = i + 1

    total_cap = TIER_SIZES[-1][1]
    order = order[:total_cap]

    def tier_of(rank):
        for tier, size in TIER_SIZES:
            if rank <= size:
                return tier
        return len(TIER_SIZES)

    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    RUNDIR.mkdir(parents=True, exist_ok=True)
    out = LIVE_DIR / f"live-targets-{stamp}.tsv"
    cols = ["tier", "rank", "url", "gig_id", "seller", "slug", "category",
            "rc_quartile", "last_seen", "last_quarter", "last_price_basic",
            "last_review_count", "last_rating"]
    with open(out, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(cols)
        for rank, ((cat, q), gig) in enumerate(order, 1):
            v = reachable[gig]
            seller, slug = gig.split("/", 1)
            w.writerow([tier_of(rank), rank, f"https://www.fiverr.com/{gig}", gig,
                        seller, slug, cat, q, v["date"], quarter(v),
                        v["price_basic"], v["review_count"], v["rating"]])
    print(f"\nWrote {out}  ({len(order):,} targets)")

    # Report
    by_cat = defaultdict(int)
    by_q = defaultdict(int)
    by_lastq = defaultdict(int)
    t1_cat = defaultdict(int)
    for rank, ((cat, q), gig) in enumerate(order, 1):
        by_cat[cat] += 1
        by_q[q] += 1
        by_lastq[quarter(reachable[gig])] += 1
        if rank <= TIER_SIZES[0][1]:
            t1_cat[cat] += 1

    lines = [
        f"# Live collection targets — {stamp}",
        "",
        f"Sitemap: `{sitemap.name}` ({len(live):,} live gigs). Panel: {len(panel):,} "
        f"distinct gigs, of which **{len(reachable):,} ({100*len(reachable)/max(len(panel),1):.1f}%) "
        "are still listed** and therefore reachable at all.",
        "",
        f"Stratified sample, seed {SEED}: equal quota per category x review-count "
        "quartile, round-robin, so any prefix of the list is balanced. Quartile cuts "
        f"are taken on the **panel** ({rc_cuts[0]}, {rc_cuts[1]}, {rc_cuts[2]} reviews), "
        "not on survivors.",
        "",
        "## Tiers (cumulative, cut on the same shuffled order)",
        "",
        "| tier | through rank | what it buys |",
        "|---|---:|---|",
        f"| 1 | {TIER_SIZES[0][1]} | pilot: enough that 'no orders recovered' is an answer |",
        f"| 2 | {TIER_SIZES[1][1]} | extends the pilot without re-drawing |",
        f"| 3 | {TIER_SIZES[2][1]} | full list as written |",
        "",
        "## Composition of the full list",
        "",
        "| category | targets | of which tier 1 |",
        "|---|---:|---:|",
    ]
    for c in sorted(by_cat):
        lines.append(f"| {c} | {by_cat[c]} | {t1_cat[c]} |")
    lines += ["", "| review-count quartile | targets |", "|---|---:|"]
    for q in sorted(by_q):
        lines.append(f"| {q} | {by_q[q]} |")
    lines += ["", "| last panel observation | targets |", "|---|---:|"]
    for q in sorted(by_lastq):
        lines.append(f"| {q} | {by_lastq[q]} |")
    lines += [
        "",
        "## What this list cannot fix",
        "",
        "Survivorship (step 63B) is upstream of every choice here: the 32.1% that "
        "remain listed over-represent expensive, heavily-reviewed gigs, and no "
        "ordering of the survivors recovers the dead. Any 2026 estimate built from "
        "this collection carries that caveat and should be reported with it.",
        "",
    ]
    report = RUNDIR / f"targets-{stamp}.md"
    report.write_text("\n".join(lines))
    print(f"Wrote {report}")


if __name__ == "__main__":
    main()
