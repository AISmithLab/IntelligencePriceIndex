#!/usr/bin/env python3
"""
85 — Turn a live browser capture into panel rows, and say what it bought.

Reads the .jsonl part-files step 84's collector downloads, and emits two tables:

  live-prices-<date>.csv   LISTED prices, in the exact schema of
                           data/pilot/balanced-prices.csv, so every downstream
                           step reads it without modification.
  live-orders-<date>.csv   REALISED orders recovered from the embedded `reviews`
                           blob: one row per displayed review, dated by
                           `created_at` (the ORDER date, not the capture date).

The second table is the point. A live listing observed in 2026Q3 pairs with the
panel's last listing at a 4-6 quarter gap, which no adjacent-quarter chain can
use. The order records are dated independently of the fetch, and step 63b measured
their reach — median lag 2 months, 74.7% within 3 — so a capture taken in 2026-09
is mostly a window onto 2026Q2-Q3, the quarters both archives lost.

WHAT THE REPORT MUST SAY, EVERY TIME. Three selections stack on this data and none
of them is fixed by collecting more of it:

  * survivorship — only still-listed gigs are reachable (step 63B: 26-32% of the
    panel, skewed rich and heavily-reviewed);
  * display — a page shows ~4 of ~124 reviews, ranked by relevancy_score (step 59);
  * price bucketing — Fiverr publishes a RANGE ("$50-$100"), not an amount, so a
    realised value is an interval, and the midpoint used here is an assumption.

The report prints all three alongside the counts, so no number leaves this step
without them.

Usage:
    python3 85-ingest-live-capture.py
    python3 85-ingest-live-capture.py --glob 'live-capture-tier1-*.jsonl'
"""

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LIVE_DIR = BASE_DIR / "data" / "fiverr-live"
RUNDIR = BASE_DIR / "runs" / "live-collection"
CATEGORIES = BASE_DIR / "data" / "pilot" / "balanced-gig-category.csv.gz"

PRICE_FIELDS = [
    "seller", "slug", "date", "year", "month",
    "price_basic", "price_standard", "price_premium",
    "title", "rating", "review_count", "extraction_method", "file_path",
]
ORDER_FIELDS = [
    "gig_id", "seller", "slug", "category", "order_id", "order_date",
    "order_year", "order_month", "order_quarter", "paid_low", "paid_high",
    "paid_mid", "rating", "country", "duration_days", "listed_basic", "fetched_at",
]

# "$50-$100" | "Up to $50" | "$1,000+" | "$100-$200"
RANGE_RE = re.compile(r"\$([\d,]+)\s*-\s*\$([\d,]+)")
UPTO_RE = re.compile(r"[Uu]p to \$([\d,]+)")
PLUS_RE = re.compile(r"\$([\d,]+)\s*\+")


def money(s):
    return float(s.replace(",", ""))


def parse_range(txt):
    """-> (low, high). `high` is None for an open-topped bucket, which is why the
    midpoint below is only defined for closed ones."""
    if not txt:
        return (None, None)
    m = RANGE_RE.search(txt)
    if m:
        return (money(m.group(1)), money(m.group(2)))
    m = UPTO_RE.search(txt)
    if m:
        return (0.0, money(m.group(1)))
    m = PLUS_RE.search(txt)
    if m:
        return (money(m.group(1)), None)
    return (None, None)


def load_categories():
    import gzip
    cats = {}
    if CATEGORIES.exists():
        with gzip.open(CATEGORIES, "rt") as f:
            for row in csv.DictReader(f):
                cats[row["gig_id"]] = row["category"]
    return cats


def quarter(y, m):
    return f"{y}Q{(m - 1) // 3 + 1}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="live-capture-*.jsonl")
    ap.add_argument("--out-date", default=None)
    args = ap.parse_args()

    files = sorted(LIVE_DIR.glob(args.glob))
    if not files:
        raise SystemExit(
            f"no capture files matching {args.glob} in {LIVE_DIR}.\n"
            "Run the step-84 collector in a browser, then move the downloaded "
            ".jsonl files into data/fiverr-live/.")

    stamp = args.out_date or date.today().isoformat()
    cats = load_categories()

    records, seen = [], set()
    for path in files:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                # Part-files can overlap if a run was resumed; the gig is the key.
                if r.get("path") in seen:
                    continue
                seen.add(r.get("path"))
                records.append(r)
    print(f"Read {len(files)} part-file(s): {len(records):,} distinct gigs")

    status = Counter(r.get("status", "error") for r in records)
    price_rows, order_rows = [], []
    no_pkg = no_rev = 0

    for r in records:
        gig = r.get("path", "")
        if "/" not in gig:
            continue
        seller, slug = gig.split("/", 1)
        fetched = r.get("fetched_at", "")
        fdate = fetched[:10].replace("-", "")
        fy, fm = (fetched[:4], fetched[5:7]) if len(fetched) >= 7 else ("", "")

        pkgs = None
        if r.get("package_list"):
            try:
                pkgs = json.loads(r["package_list"])
            except json.JSONDecodeError:
                pkgs = None
        if not pkgs:
            no_pkg += 1

        rv = None
        if r.get("reviews"):
            try:
                rv = json.loads(r["reviews"])
            except json.JSONDecodeError:
                rv = None
        if not rv:
            no_rev += 1

        # packageList carries cents; the panel stores dollars.
        def price_at(i):
            if not pkgs or i >= len(pkgs):
                return ""
            p = pkgs[i].get("price")
            return f"{p / 100:.1f}" if isinstance(p, (int, float)) else ""

        listed_basic = price_at(0)
        if pkgs:
            price_rows.append({
                "seller": seller, "slug": slug, "date": fdate, "year": fy, "month": fm,
                "price_basic": listed_basic,
                "price_standard": price_at(1),
                "price_premium": price_at(2),
                # og:title, not pkgs[0]["title"] — the latter is the PACKAGE name
                # ("Basic"), which would put a constant in a column the panel
                # uses for the gig's own title.
                "title": (r.get("og_title") or "").strip(),
                "rating": r.get("rating") or "",
                "review_count": rv.get("total_count", "") if rv else "",
                "extraction_method": "live_console_packageList",
                "file_path": f"live:{gig}",
            })

        for rev in (rv or {}).get("reviews", []) or []:
            created = rev.get("created_at") or ""
            if len(created) < 7:
                continue
            oy, om = created[:4], int(created[5:7])
            lo, hi = parse_range(rev.get("order_price_range_usd")
                                 or rev.get("order_price_range") or "")
            if lo is None and rev.get("price_range_start") is not None:
                # Older era carried numeric bounds instead of a formatted string.
                lo = rev.get("price_range_start")
                hi = rev.get("price_range_end")
            mid = (lo + hi) / 2 if (lo is not None and hi is not None) else ""
            order_rows.append({
                "gig_id": gig, "seller": seller, "slug": slug,
                "category": cats.get(gig, ""),
                "order_id": rev.get("encrypted_order_id") or rev.get("id") or "",
                "order_date": created[:10],
                "order_year": oy, "order_month": f"{om:02d}",
                "order_quarter": quarter(oy, om),
                "paid_low": "" if lo is None else lo,
                "paid_high": "" if hi is None else hi,
                "paid_mid": mid,
                "rating": rev.get("value", ""),
                "country": rev.get("reviewer_country_code", ""),
                "duration_days": rev.get("order_duration_in_days", ""),
                "listed_basic": listed_basic,
                "fetched_at": fetched,
            })

    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    RUNDIR.mkdir(parents=True, exist_ok=True)
    pout = LIVE_DIR / f"live-prices-{stamp}.csv"
    oout = LIVE_DIR / f"live-orders-{stamp}.csv"
    with open(pout, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PRICE_FIELDS)
        w.writeheader()
        w.writerows(price_rows)
    with open(oout, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ORDER_FIELDS)
        w.writeheader()
        w.writerows(order_rows)
    print(f"Wrote {pout.name}: {len(price_rows):,} listed-price rows")
    print(f"Wrote {oout.name}: {len(order_rows):,} order rows")

    # ---------------- report ----------------
    by_q = Counter(o["order_quarter"] for o in order_rows)
    priced = [o for o in order_rows if o["paid_mid"] != ""]
    gigs_with_orders = len({o["gig_id"] for o in order_rows})
    by_cat_q = defaultdict(Counter)
    for o in order_rows:
        if o["category"]:
            by_cat_q[o["category"]][o["order_quarter"]] += 1

    target_q = {"2026Q2", "2026Q3"}
    in_target = sum(v for k, v in by_q.items() if k in target_q)

    L = [
        f"# Live capture — {stamp}",
        "",
        f"Part-files read: {len(files)}. Gigs attempted: **{len(records):,}**. "
        f"HTTP status: " + ", ".join(f"{k} {v}" for k, v in sorted(
            status.items(), key=lambda kv: str(kv[0]))) + ".",
        "",
        f"Pages with no `packageList`: {no_pkg}. With no `reviews` blob: {no_rev}.",
        "",
        "## What came back",
        "",
        f"- **{len(price_rows):,}** listed-price rows (one per gig, dated by fetch).",
        f"- **{len(order_rows):,}** order records from **{gigs_with_orders:,}** gigs "
        f"({len(order_rows) / max(gigs_with_orders, 1):.1f} per gig with any).",
        f"- **{len(priced):,}** carry a closed price bucket "
        f"({100 * len(priced) / max(len(order_rows), 1):.1f}%).",
        f"- **{in_target:,}** orders fall in **2026Q2-Q3** — the quarters neither "
        f"archive holds ({100 * in_target / max(len(order_rows), 1):.1f}% of the haul).",
        "",
        "## Orders by quarter",
        "",
        "| quarter | orders | priced | median paid (mid) |",
        "|---|---:|---:|---:|",
    ]
    import statistics
    for q in sorted(by_q):
        qp = [float(o["paid_mid"]) for o in priced if o["order_quarter"] == q]
        med = f"{statistics.median(qp):.0f}" if qp else "-"
        L.append(f"| {q} | {by_q[q]} | {len(qp)} | {med} |")

    if by_cat_q:
        L += ["", "## 2026Q2-Q3 orders by category", "",
              "| category | 2026Q2 | 2026Q3 |", "|---|---:|---:|"]
        for c in sorted(by_cat_q):
            L.append(f"| {c} | {by_cat_q[c].get('2026Q2', 0)} | "
                     f"{by_cat_q[c].get('2026Q3', 0)} |")

    L += [
        "",
        "## Three selections that travel with every number above",
        "",
        "1. **Survivorship.** Only still-listed gigs are reachable. Step 63B: 26-32% "
        "of the panel, and skewed — 43.8% of the top listed-price quartile against "
        "22.4% of the bottom, 55.0% of the top review-count quartile against 20.8% "
        "of the bottom. Orders placed at listings that have since died are "
        "unreachable, so a recovered quarter looks healthier than the quarter was.",
        "2. **Display.** A page shows ~4 of ~124 reviews, ranked by `relevancy_score`, "
        "not at random (step 59). Step 63A found no detectable PRICE selection in "
        "that ranking (late minus early median realised value +0 USD, CI [+0, +0]), "
        "which is why the price levels are usable; it does not make the sample of "
        "orders complete.",
        "3. **Bucketing.** Fiverr publishes a range, not an amount. `paid_mid` is the "
        "midpoint of a closed bucket and is an assumption; open-topped buckets "
        "(`$X+`) have no midpoint and are excluded from every median above.",
        "",
        "These are properties of the source. Collecting more pages narrows the "
        "confidence interval and does not touch any of the three.",
        "",
    ]
    rep = RUNDIR / f"live-capture-{stamp}.md"
    rep.write_text("\n".join(L))
    print(f"Wrote {rep}")
    print(f"\n2026Q2-Q3 orders recovered: {in_target:,}")


if __name__ == "__main__":
    main()
