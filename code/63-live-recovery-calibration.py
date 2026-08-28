#!/usr/bin/env python3
"""
63 — Can 2025-26 transactions be recovered from pages fetched LIVE today?

Step 59 established that gig pages embed an order record per displayed review,
dated by ORDER (`created_at`), not by capture. That is the only route to the
2024Q4-2026 window, because the archive is closed there: the crawl stopped in
2024-10 and Fiverr began refusing it in 2025-08 (77.4% 403).

The route only works if a page fetched LONG AFTER a quarter still describes
that quarter the same way a page fetched DURING it did. Two things can break
that, and they are separable:

  A. DISPLAY / RECENCY SELECTION. Pages show ~4 of ~124 reviews ranked by
     `relevancy_score`, and displayed reviews skew recent. A late page may
     recover a non-random - in particular a price-selected - subset of an old
     quarter's orders. Tested WITHIN gigs observed in both windows, so
     survivorship is held fixed by construction.

  B. SURVIVORSHIP. A live fetch can only reach gigs that still exist. Orders
     from 2025 placed at listings that have since died are unreachable, so a
     recovered 2025 will look healthier than 2025 was. Tested by matching the
     archive panel against the 2026-08-21 live sitemap.

A is the internal-validity threat; B is the external one. Neither needs any
new collection - the 86 GB of stored HTML and the sitemap are already on disk.

Design for A: target order year 2023, which is the most recent year with thick
captures on BOTH sides. EARLY captures 202301-202406 (contemporaneous), LATE
captures 202410-202612 (lag 1-3 years). That lag brackets the lag a live 2026
crawl would carry for 2025 orders, so it is the right analogue.

Pilot. Samples gigs and caps captures per gig; does not stream all 361,760.
"""
import collections
import gzip
import json
import os
import random
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOTS = ["data/pilot/html-balanced", "data/pilot/html", "data/pilot/html-recent"]
SITEMAP = "data/sitemap/gigs-2026-08-21.txt.gz"
PRICES = "data/pilot/balanced-prices.csv"
CAP_RE = re.compile(r"(\d{4})(\d{2})\d{2}_(.+)\.html\.gz$")

TARGET_YEAR = "2023"
EARLY = ("202301", "202406")
LATE = ("202410", "202612")
MAX_GIGS = 1500
MAX_CAPS_PER_ARM = 4
SEED = 63


def index_captures():
    by_gig = collections.defaultdict(list)
    for root in ROOTS:
        for dirpath, _, filenames in os.walk(root):
            seller = os.path.basename(dirpath)
            for fn in filenames:
                m = CAP_RE.match(fn)
                if not m:
                    continue
                by_gig[(seller, m.group(3))].append(
                    (m.group(1) + m.group(2), os.path.join(dirpath, fn))
                )
    return by_gig


def read(path):
    try:
        return gzip.open(path, "rt", encoding="utf-8", errors="replace").read()
    except Exception:
        return None


def parse_reviews(html):
    """Brace-match the embedded reviews object (string-aware). From step 59."""
    i = html.find('"reviews":{"has_next"')
    if i < 0:
        return None
    j = html.index("{", i + len('"reviews":') - 1)
    depth, k = 0, j
    while k < len(html):
        c = html[k]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
        elif c == '"':
            k += 1
            while k < len(html) and not (html[k] == '"' and html[k - 1] != "\\"):
                k += 1
        k += 1
    try:
        return json.loads(html[j:k + 1])
    except Exception:
        return None


def rule(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def midpoint(rv):
    lo = rv.get("price_range_start")
    if lo is None:
        return None
    hi = rv.get("price_range_end")
    return (lo + hi) / 2.0 if hi else float(lo)


def harvest(caps, target_year):
    """Dedupe target-year orders across a set of captures -> {order_id: record}."""
    out = {}
    pages = 0
    for _, path in caps:
        html = read(path)
        if html is None:
            continue
        obj = parse_reviews(html)
        if not obj:
            continue
        pages += 1
        for rv in obj.get("reviews", []):
            if (rv.get("created_at") or "")[:4] != target_year:
                continue
            oid = rv.get("encrypted_order_id")
            if oid:
                out.setdefault(oid, rv)
    return out, pages


def describe(name, orders):
    priced = [r for r in orders if r.get("price_range_start") is not None]
    mids = [midpoint(r) for r in priced]
    top = sum(1 for r in priced if r.get("price_range_end") is None)
    ratings = [r.get("value") for r in orders if isinstance(r.get("value"), (int, float))]
    repeat = [r for r in orders if r.get("repeat_buyer")]
    print(f"  {name:<26}{len(orders):>8}{len(priced):>9}"
          f"{100*len(priced)/max(len(orders),1):>8.1f}%"
          f"{(statistics.median(mids) if mids else float('nan')):>10.0f}"
          f"{(100*sum(1 for m in mids if m >= 200)/len(mids) if mids else float('nan')):>9.1f}%"
          f"{(100*top/len(priced) if priced else 0):>8.1f}%"
          f"{(statistics.mean(ratings) if ratings else float('nan')):>9.3f}"
          f"{100*len(repeat)/max(len(orders),1):>9.1f}%")
    return mids


def band_table(mids_early, mids_late):
    edges = [(0, 50), (50, 100), (100, 200), (200, 400), (400, 1000), (1000, 10**9)]
    labels = ["<$50", "$50-100", "$100-200", "$200-400", "$400-1k", "$1k+"]
    print(f"\n  {'band':<12}{'early %':>10}{'late %':>10}{'diff pp':>10}")
    for (lo, hi), lab in zip(edges, labels):
        e = 100 * sum(1 for m in mids_early if lo <= m < hi) / max(len(mids_early), 1)
        l = 100 * sum(1 for m in mids_late if lo <= m < hi) / max(len(mids_late), 1)
        print(f"  {lab:<12}{e:>9.1f}%{l:>9.1f}%{l-e:>+9.1f}")


def bootstrap_gap(pairs, n=2000):
    """Gig-clustered bootstrap of median(late mids) - median(early mids)."""
    if not pairs:
        return None
    rng = random.Random(SEED)
    obs = []
    for _ in range(n):
        samp = [pairs[rng.randrange(len(pairs))] for _ in range(len(pairs))]
        e = [m for p in samp for m in p[0]]
        l = [m for p in samp for m in p[1]]
        if e and l:
            obs.append(statistics.median(l) - statistics.median(e))
    obs.sort()
    return obs[int(0.025 * len(obs))], obs[int(0.975 * len(obs))]


def part_a(by_gig):
    rule(f"A. DISPLAY / RECENCY SELECTION - {TARGET_YEAR} orders, early vs late pages")
    eligible = []
    for gig, caps in by_gig.items():
        early = [c for c in caps if EARLY[0] <= c[0] <= EARLY[1]]
        late = [c for c in caps if LATE[0] <= c[0] <= LATE[1]]
        if early and late:
            eligible.append((gig, early, late))
    print(f"  gigs with captures in BOTH windows: {len(eligible)} "
          f"of {len(by_gig)} in the stored panel")
    if not eligible:
        print("  NOT TESTABLE on stored HTML.")
        return
    rng = random.Random(SEED)
    rng.shuffle(eligible)
    sample = eligible[:MAX_GIGS]
    print(f"  sampling {len(sample)} gigs, <={MAX_CAPS_PER_ARM} captures per arm\n")

    e_all, l_all, pairs = [], [], []
    both_gigs = e_pages = l_pages = 0
    recov_e, recov_l = [], []
    for gig, early, late in sample:
        eo, ep = harvest(sorted(early)[:MAX_CAPS_PER_ARM], TARGET_YEAR)
        lo_, lp = harvest(sorted(late)[:MAX_CAPS_PER_ARM], TARGET_YEAR)
        e_pages += ep
        l_pages += lp
        if not eo and not lo_:
            continue
        recov_e.append(len(eo))
        recov_l.append(len(lo_))
        e_all.extend(eo.values())
        l_all.extend(lo_.values())
        if eo and lo_:
            both_gigs += 1
            me = [m for m in (midpoint(r) for r in eo.values()) if m is not None]
            ml = [m for m in (midpoint(r) for r in lo_.values()) if m is not None]
            if me and ml:
                pairs.append((me, ml))

    print(f"  pages parsed: early {e_pages}   late {l_pages}")
    print(f"  gigs yielding {TARGET_YEAR} orders in BOTH arms: {both_gigs}\n")
    print(f"  {'arm':<26}{'orders':>8}{'priced':>9}{'%priced':>9}"
          f"{'med $':>10}{'>=$200':>10}{'topcens':>8}{'rating':>9}{'repeat':>10}")
    me = describe("EARLY (contemporaneous)", e_all)
    ml = describe("LATE  (lag 1-3 yrs)", l_all)

    if recov_e:
        print(f"\n  {TARGET_YEAR} orders recovered per gig: "
              f"early median {statistics.median(recov_e):.0f}, "
              f"late median {statistics.median(recov_l):.0f}  "
              f"(mean {statistics.mean(recov_e):.1f} vs {statistics.mean(recov_l):.1f})")
    band_table(me, ml)

    if me and ml:
        gap = statistics.median(ml) - statistics.median(me)
        ci = bootstrap_gap(pairs)
        print(f"\n  MEDIAN REALISED VALUE, late minus early: {gap:+.0f} USD")
        if ci:
            print(f"  gig-clustered bootstrap 95% CI ({len(pairs)} gigs): "
                  f"[{ci[0]:+.0f}, {ci[1]:+.0f}]")
            verdict = "NO detectable price selection" if ci[0] <= 0 <= ci[1] else \
                      "PRICE-SELECTED - late pages do not reproduce the quarter"
            print(f"  => {verdict}")


def part_b(by_gig):
    rule("B. SURVIVORSHIP - which panel gigs can a live fetch still reach?")
    if not os.path.exists(SITEMAP):
        print(f"  {SITEMAP} missing.")
        return
    live = set()
    with gzip.open(SITEMAP, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if line:
                live.add(line)
    print(f"  live sitemap 2026-08-21: {len(live)} gigs")

    panel = {}
    for gig, caps in by_gig.items():
        panel[gig] = max(c[0] for c in caps)
    hit = sum(1 for (s, sl) in panel if f"{s}/{sl}" in live)
    print(f"  stored panel: {len(panel)} gigs   still listed: {hit} "
          f"({100*hit/max(len(panel),1):.1f}%)\n")

    print("  by LAST capture year - attrition should rise with age;")
    print("  a flat profile would mean the sitemap is a partial index, not death.")
    print(f"  {'last seen':<12}{'gigs':>8}{'live':>8}{'% live':>9}")
    by_year = collections.defaultdict(lambda: [0, 0])
    for (s, sl), last in panel.items():
        b = by_year[last[:4]]
        b[0] += 1
        b[1] += 1 if f"{s}/{sl}" in live else 0
    for y in sorted(by_year):
        n, k = by_year[y]
        print(f"  {y:<12}{n:>8}{k:>8}{100*k/n:>8.1f}%")

    if not os.path.exists(PRICES):
        return
    latest = {}
    with open(PRICES, encoding="utf-8", errors="replace") as fh:
        hdr = fh.readline().rstrip("\n").split(",")
        ix = {c: i for i, c in enumerate(hdr)}
        for line in fh:
            f = line.rstrip("\n").split(",")
            if len(f) < len(hdr):
                continue
            key = (f[ix["seller"]], f[ix["slug"]])
            d = f[ix["date"]]
            if key not in latest or d > latest[key][0]:
                try:
                    p = float(f[ix["price_basic"]])
                    rc = float(f[ix["review_count"]] or 0)
                except ValueError:
                    continue
                latest[key] = (d, p, rc)

    for label, idx in (("listed basic price", 1), ("review count", 2)):
        vals = sorted(v[idx] for v in latest.values())
        if not vals:
            continue
        qs = [vals[int(q * len(vals))] for q in (0.25, 0.5, 0.75)]
        print(f"\n  by {label} quartile at last observation "
              f"(cuts {qs[0]:.0f} / {qs[1]:.0f} / {qs[2]:.0f})")
        print(f"  {'quartile':<12}{'gigs':>8}{'live':>8}{'% live':>9}")
        buckets = collections.defaultdict(lambda: [0, 0])
        for (s, sl), v in latest.items():
            x = v[idx]
            q = "Q1 low" if x <= qs[0] else "Q2" if x <= qs[1] else \
                "Q3" if x <= qs[2] else "Q4 high"
            buckets[q][0] += 1
            buckets[q][1] += 1 if f"{s}/{sl}" in live else 0
        for q in ("Q1 low", "Q2", "Q3", "Q4 high"):
            n, k = buckets[q]
            if n:
                print(f"  {q:<12}{n:>8}{k:>8}{100*k/n:>8.1f}%")


def main():
    random.seed(SEED)
    print(__doc__)
    by_gig = index_captures()
    print(f"indexed {sum(len(v) for v in by_gig.values())} captures "
          f"across {len(by_gig)} gigs")
    part_a(by_gig)
    part_b(by_gig)
    rule("VERDICT")
    print("  A tells you whether a live 2026 fetch reproduces an old quarter's")
    print("  price distribution. B tells you whose orders it can never see.")
    print("  Both must pass before any live crawl is specified.")


if __name__ == "__main__":
    main()
