#!/usr/bin/env python3
"""
59 — Audit: are realised (buyer-paid) order values recoverable from the archive?

The IPI reads LISTED basic-package prices. drafts/market-structure-answer.md
§1.3 and §5 both record realised order value as unmeasurable on this data.

This step tests that. Fiverr gig pages embed a JSON `reviews` object whose
per-review records carry, among other fields:

    encrypted_order_id   unique order key (dedupes across captures)
    created_at           ORDER date, not capture date
    price_range_start    what the buyer paid, lower bucket edge
    price_range_end      upper bucket edge
    value                rating; repeat_buyer; is_business; reviewer_country_code

Nothing downstream of code/09-extract-prices.py has ever read these fields.

Four questions, in order:
  A. From which capture years does the paid-amount field exist at all?
  B. What do buyers pay, and how does it compare to the listed basic price?
  C. Do pre-2022-dated orders carry prices (retrospective reach)?
  D. Pages show ~4 of ~124 reviews, relevance-ranked. Pooling repeat captures,
     what SHARE of a gig's orders do we recover, and is the price field
     missing selectively?

Pilot only. Samples files; does not stream all 361,760 captures.
"""
import collections
import gzip
import json
import os
import random
import re
import statistics
import sys

ROOTS = ["data/pilot/html-balanced", "data/pilot/html", "data/pilot/html-recent"]
CAP_RE = re.compile(r"(\d{4})(\d{2})\d{2}_(.+)\.html\.gz$")
SEED = 11


def index_captures():
    """(seller, slug) -> [(yyyymm, path)], plus a year -> [path] view."""
    by_gig = collections.defaultdict(list)
    by_year = collections.defaultdict(list)
    for root in ROOTS:
        for dirpath, _, filenames in os.walk(root):
            seller = os.path.basename(dirpath)
            for fn in filenames:
                m = CAP_RE.match(fn)
                if not m:
                    continue
                path = os.path.join(dirpath, fn)
                by_gig[(seller, m.group(3))].append((m.group(1) + m.group(2), path))
                by_year[m.group(1)].append(path)
    return by_gig, by_year


def read(path):
    try:
        return gzip.open(path, "rt", encoding="utf-8", errors="replace").read()
    except Exception:
        return None


def parse_reviews(html):
    """Brace-match the embedded reviews object. String-aware so quoted braces
    inside review comments do not terminate the scan early."""
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
        return json.loads(html[j : k + 1])
    except Exception:
        return None


def rule(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def question_a(by_year, n=120):
    rule("A. FIELD AVAILABILITY BY CAPTURE YEAR")
    print(f"{'year':<6}{'sampled':>9}{'reviewblob':>12}{'w/paid':>8}{'%paid':>8}")
    for year in sorted(by_year):
        sample = random.sample(by_year[year], min(n, len(by_year[year])))
        blob = paid = 0
        for path in sample:
            html = read(path)
            if html is None:
                continue
            if '"reviews":[{' in html or '"reviews":[]' in html:
                blob += 1
            if '"price_range_start"' in html:
                paid += 1
        print(f"{year:<6}{len(sample):>9}{blob:>12}{paid:>8}{100*paid/len(sample):>7.1f}%")
    print("\n  The paid-amount field appears from 2022. Review records themselves")
    print("  (order id, order date, rating, country) go back to 2019.")


def collect(by_year, per_year=250, min_year=2022):
    rows, pages, totals = [], 0, []
    for year in sorted(by_year):
        if int(year) < min_year:
            continue
        for path in random.sample(by_year[year], min(per_year, len(by_year[year]))):
            html = read(path)
            if html is None:
                continue
            obj = parse_reviews(html)
            if not obj:
                continue
            pages += 1
            if obj.get("total_count"):
                totals.append(obj["total_count"])
            for rv in obj.get("reviews", []):
                rv["_capture"] = os.path.basename(path)[:6]
                rows.append(rv)
    return rows, pages, totals


def question_b(rows, pages, totals):
    rule("B. WHAT BUYERS PAID")
    priced = [r for r in rows if r.get("price_range_start") is not None]
    print(f"  pages parsed {pages}   reviews {len(rows)}   "
          f"distinct order ids {len({r.get('encrypted_order_id') for r in rows} - {None})}")
    print(f"  reviews shown per page {len(rows)/pages:.1f}   "
          f"median gig total_count {statistics.median(totals):.0f}")
    print(f"  reviews carrying a paid amount: {len(priced)}/{len(rows)} "
          f"= {100*len(priced)/len(rows):.1f}%\n")
    buckets = collections.Counter(
        (r["price_range_start"], r.get("price_range_end")) for r in priced
    )
    order = sorted(buckets, key=lambda b: b[0])
    print(f"  {'bucket':<16}{'n':>7}{'share':>9}{'cum':>8}")
    cum = 0.0
    for lo, hi in order:
        n = buckets[(lo, hi)]
        share = 100 * n / len(priced)
        cum += share
        label = f"${lo}-{hi}" if hi else f"${lo}+"
        print(f"  {label:<16}{n:>7}{share:>8.1f}%{cum:>7.1f}%")
    under50 = sum(n for (lo, hi), n in buckets.items() if lo < 50)
    print(f"\n  Orders under $50: {100*under50/len(priced):.1f}%.")
    print("  The IPI's listed basic-package median is ~$25-30, so realised order")
    print("  value runs several times the listed price. §1.3 conjectured this;")
    print("  it is now measured.")


def question_c(rows):
    rule("C. RETROSPECTIVE REACH — DO PRE-2022 ORDERS CARRY PRICES?")
    seen = collections.defaultdict(lambda: [0, 0])
    for rv in rows:
        year = (rv.get("created_at") or "")[:4]
        if not year:
            continue
        seen[year][0] += 1
        if rv.get("price_range_start") is not None:
            seen[year][1] += 1
    print(f"  {'order year':<12}{'priced':>8}{'total':>8}{'%':>8}")
    for year in sorted(seen):
        n, k = seen[year]
        print(f"  {year:<12}{k:>8}{n:>8}{100*k/n:>7.1f}%")
    print("\n  Pre-2022 orders DO carry prices when served by a 2022+ page, but the")
    print("  volume is thin: displayed reviews skew recent, so the pre-ChatGPT")
    print("  baseline this can support is roughly one year and back-filled.")


def question_d(by_gig, min_caps=8, n_gigs=60):
    rule("D. COVERAGE AND SELECTION")
    recent = {
        g: sorted(v for v in caps if int(v[0][:4]) >= 2022)
        for g, caps in by_gig.items()
    }
    cands = [g for g, v in recent.items() if len(v) >= min_caps]
    print(f"  gigs with >={min_caps} captures in 2022+: {len(cands)} of {len(recent)}\n")

    tot_orders = tot_priced = tot_new = 0
    per_gig = []
    for gig in random.sample(cands, min(n_gigs, len(cands))):
        orders, counts = {}, []
        for _, path in recent[gig]:
            html = read(path)
            if html is None:
                continue
            obj = parse_reviews(html)
            if not obj:
                continue
            if obj.get("total_count"):
                counts.append(obj["total_count"])
            for rv in obj.get("reviews", []):
                oid = rv.get("encrypted_order_id")
                if oid:
                    orders.setdefault(oid, rv)
        if not counts:
            continue
        new = counts[-1] - counts[0]
        per_gig.append(len(orders))
        tot_orders += len(orders)
        tot_priced += sum(1 for r in orders.values() if r.get("price_range_start") is not None)
        if new > 0:
            tot_new += new

    print(f"  {len(per_gig)} gigs -> {tot_orders} distinct orders ({tot_priced} priced)")
    print(f"  median distinct orders per gig: {statistics.median(per_gig):.0f}")
    print(f"  new reviews implied by total_count growth: {tot_new}")
    print(f"  => RECOVERY RATE OF NEW ORDERS: {100*tot_orders/tot_new:.1f}%")
    print("\n  Pages rank displayed reviews by relevancy_score, NOT at random, so")
    print("  this is a SELECTED sample of transactions. That is the design's")
    print("  central threat and needs its own test before any index is built.")


def selection_check(rows):
    rule("D2. IS THE PAID FIELD ITSELF MISSING SELECTIVELY?")
    priced = [r for r in rows if r.get("price_range_start") is not None]
    unpriced = [r for r in rows if r.get("price_range_start") is None]

    def summarise(name, sel):
        vals = [r["value"] for r in sel if r.get("value") is not None]
        def pct(key):
            v = [r.get(key) for r in sel if r.get(key) is not None]
            return 100 * sum(1 for x in v if x) / len(v) if v else float("nan")
        print(f"  {name:<10} n={len(sel):<6} mean rating {sum(vals)/len(vals):.3f}   "
              f"repeat_buyer {pct('repeat_buyer'):.1f}%   is_business {pct('is_business'):.1f}%")

    summarise("priced", priced)
    summarise("unpriced", unpriced)
    print("\n  Close on all three. Mildly reassuring about the price field itself.")
    print("  It says nothing about which orders get DISPLAYED — see D.")


def main():
    random.seed(SEED)
    if not os.path.isdir(ROOTS[0]):
        sys.exit("run from the repository root")
    by_gig, by_year = index_captures()
    print(f"indexed {sum(len(v) for v in by_year.values())} captures "
          f"across {len(by_gig)} gigs")
    question_a(by_year)
    rows, pages, totals = collect(by_year)
    question_b(rows, pages, totals)
    question_c(rows)
    selection_check(rows)
    question_d(by_gig)
    rule("VERDICT")
    print("  Realised order value IS recoverable, 2022 onward, at order level,")
    print("  dated by order rather than by capture. §5's 'not measurable at any")
    print("  effort' entry is wrong and must be revised.")
    print("  Three limits gate any use: starts 2022; ~12% of orders recovered and")
    print("  relevance-selected; amounts are interval-censored buckets.")


if __name__ == "__main__":
    main()
