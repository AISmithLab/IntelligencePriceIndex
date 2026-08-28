#!/usr/bin/env python3
"""
63b — How far back does a page reach?

Step 63 part A found that late pages reproduce an old quarter's PRICE
distribution but recover ~13x fewer of its orders per page. That makes the
reach curve the design-critical number: for a page fetched at month M, what
share of the orders it displays were placed 1, 3, 6, 12, 24 months earlier?

It decides whether a live crawl back-fills 2025 or only observes forward, and
at what cadence it has to run to avoid losing quarters the way 2025 was lost.

Lag is computed per displayed order as (capture month - order month), pooled
over captures from 2024-01 on. Orders are deduped within a capture only, since
the unit here is "what one page shows", not "what a gig ever sold".
"""
import collections, gzip, json, os, random, re, statistics, sys

ROOTS = ["data/pilot/html-balanced", "data/pilot/html", "data/pilot/html-recent"]
CAP_RE = re.compile(r"(\d{4})(\d{2})\d{2}_(.+)\.html\.gz$")
MIN_CAP, N_SAMPLE, SEED = "202401", 3000, 63

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
_m = import_module("63-live-recovery-calibration") if False else None


def read(p):
    try:
        return gzip.open(p, "rt", encoding="utf-8", errors="replace").read()
    except Exception:
        return None


def parse_reviews(html):
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


def months(a, b):
    return (int(a[:4]) - int(b[:4])) * 12 + (int(a[4:6]) - int(b[4:6]))


def main():
    random.seed(SEED)
    print(__doc__)
    caps = []
    for root in ROOTS:
        for dp, _, fns in os.walk(root):
            for fn in fns:
                m = CAP_RE.match(fn)
                if m and m.group(1) + m.group(2) >= MIN_CAP:
                    caps.append((m.group(1) + m.group(2), os.path.join(dp, fn)))
    print(f"captures from {MIN_CAP} on: {len(caps)}")
    sample = random.sample(caps, min(N_SAMPLE, len(caps)))

    lags, pages, shown, priced_by_lag = [], 0, 0, collections.defaultdict(lambda: [0, 0])
    for cap, path in sample:
        html = read(path)
        if html is None:
            continue
        obj = parse_reviews(html)
        if not obj:
            continue
        pages += 1
        seen = set()
        for rv in obj.get("reviews", []):
            ca = (rv.get("created_at") or "")[:7].replace("-", "")
            oid = rv.get("encrypted_order_id")
            if len(ca) != 6 or (oid and oid in seen):
                continue
            if oid:
                seen.add(oid)
            lag = months(cap, ca)
            if lag < 0 or lag > 120:
                continue
            shown += 1
            lags.append(lag)
            b = priced_by_lag[min(lag // 3, 12)]
            b[0] += 1
            b[1] += 1 if rv.get("price_range_start") is not None else 0

    print(f"pages with a review blob: {pages}   displayed orders: {shown}")
    print(f"median lag {statistics.median(lags):.0f} months, "
          f"mean {statistics.mean(lags):.1f}\n")

    print(f"{'lag (months)':<14}{'orders':>9}{'share':>9}{'cumulative':>12}{'% priced':>10}")
    cum = 0
    for q in range(13):
        n, p = priced_by_lag[q]
        if not n:
            continue
        cum += n
        lab = f"{q*3}-{q*3+2}" if q < 12 else "36+"
        print(f"{lab:<14}{n:>9}{100*n/shown:>8.1f}%{100*cum/shown:>11.1f}%"
              f"{100*p/n:>9.1f}%")

    print("\nreach: share of a page's displayed orders placed within N months")
    for n in (3, 6, 12, 18, 24, 36):
        print(f"  <= {n:>2} months   {100*sum(1 for l in lags if l <= n)/shown:>5.1f}%")


if __name__ == "__main__":
    main()
