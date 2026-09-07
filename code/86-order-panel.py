#!/usr/bin/env python3
"""
86 — How far forward does the HTML we already hold actually reach?

THE QUESTION. The listed-price panel ends where the archive's *captures* end, and
after the PerimeterX wall that is 2024Q3 for practical purposes. But step 59
established that a gig page embeds a `reviews` object whose records are dated by
ORDER (`created_at`) and carry what the buyer paid (`order_price_range_usd`). A
capture taken in 2025-09 therefore describes orders placed in 2025, and nothing
downstream of `09-extract-prices.py` has ever read those fields at scale.

So before collecting anything new, the cheap question is: how far forward do the
order records inside the 11 GB of HTML we ALREADY downloaded reach, and how thick
are they per quarter? If the answer is "into 2025Q4 and 2026Q1 at usable density",
the panel's right edge can be extended with zero new collection — on realised
prices rather than listed ones, which is a different and in some ways better price
object.

WHAT THIS IS NOT. It is not the IPI. The IPI is a matched-model index on LISTED
basic-package prices; this is a transaction series on bucketed realised values.
They are different objects and must not be chained together. This step measures
supply, so that the decision about what to do with it is taken on numbers.

THE THREE LIMITS, carried from steps 59 and 63 and re-stated by the report:
  * the paid-amount field appears from 2022 only;
  * a page displays ~4 of ~124 reviews, ranked by relevancy_score, so this is a
    sample of a gig's orders, not a census (step 63A found no PRICE selection in
    that ranking: late minus early +0 USD, CI [+0, +0]);
  * Fiverr publishes a RANGE ("$50-$100"), so a realised value is an interval and
    the midpoint is an assumption.

Dedupe is by `encrypted_order_id` across every capture of every gig, which is what
makes pooling repeat captures legitimate: the same order shown on ten captures is
one order.

Usage:
    python3 86-order-panel.py --limit 1000          # pilot
    python3 86-order-panel.py --workers 7           # full corpus
"""

import argparse
import csv
import gzip
import json
import os
import re
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ROOTS = ["data/pilot/html-refresh2025", "data/pilot/html-recent",
         "data/pilot/html-balanced", "data/pilot/html"]
OUTDIR = BASE_DIR / "data" / "pilot"
RUNDIR = BASE_DIR / "runs" / "order-panel"

CAP_RE = re.compile(r"(\d{8})_(.+)\.html\.gz$")
RANGE_RE = re.compile(r"\$([\d,]+)\s*-\s*\$([\d,]+)")
UPTO_RE = re.compile(r"[Uu]p to \$([\d,]+)")
PLUS_RE = re.compile(r"\$([\d,]+)\s*\+")

FIELDS = ["gig_id", "seller", "slug", "order_id", "order_date", "order_quarter",
          "paid_low", "paid_high", "paid_mid", "rating", "country",
          "duration_days", "capture_date"]


def parse_range(txt):
    if not txt:
        return (None, None)
    m = RANGE_RE.search(txt)
    if m:
        return (float(m.group(1).replace(",", "")), float(m.group(2).replace(",", "")))
    m = UPTO_RE.search(txt)
    if m:
        return (0.0, float(m.group(1).replace(",", "")))
    m = PLUS_RE.search(txt)
    if m:
        return (float(m.group(1).replace(",", "")), None)
    return (None, None)


def parse_reviews(html):
    """Brace-match the embedded reviews object, string-aware — review comments
    routinely contain braces, which a naive depth count would trip on."""
    i = html.find('"reviews":{"has_next"')
    if i < 0:
        return None
    j = html.find("{", i)
    if j < 0:
        return None
    depth = 0
    in_str = esc = False
    for k in range(j, len(html)):
        c = html[k]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(html[j:k + 1])
                except json.JSONDecodeError:
                    return None
    return None


def scan(path):
    """-> (gig_id, capture_date, [order rows]). Runs in a worker process."""
    p = Path(path)
    m = CAP_RE.search(p.name)
    if not m:
        return None
    cap_date, slug = m.group(1), m.group(2)
    seller = p.parent.name
    gig = f"{seller}/{slug}"
    try:
        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as f:
            html = f.read()
    except (OSError, EOFError):
        return None

    obj = parse_reviews(html)
    if not obj:
        return (gig, cap_date, [])

    rows = []
    for rv in obj.get("reviews") or []:
        created = rv.get("created_at") or ""
        if len(created) < 7:
            continue
        try:
            om = int(created[5:7])
        except ValueError:
            continue
        if not 1 <= om <= 12:
            continue
        lo, hi = parse_range(rv.get("order_price_range_usd")
                             or rv.get("order_price_range") or "")
        if lo is None and rv.get("price_range_start") is not None:
            lo, hi = rv.get("price_range_start"), rv.get("price_range_end")
        rows.append({
            "gig_id": gig, "seller": seller, "slug": slug,
            "order_id": rv.get("encrypted_order_id") or rv.get("id") or "",
            "order_date": created[:10],
            "order_quarter": f"{created[:4]}Q{(om - 1) // 3 + 1}",
            "paid_low": "" if lo is None else lo,
            "paid_high": "" if hi is None else hi,
            "paid_mid": (lo + hi) / 2 if (lo is not None and hi is not None) else "",
            "rating": rv.get("value", ""),
            "country": rv.get("reviewer_country_code", ""),
            "duration_days": rv.get("order_duration_in_days", ""),
            "capture_date": cap_date,
        })
    return (gig, cap_date, rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roots", default=None,
                    help="comma-separated HTML roots (default: all four)")
    ap.add_argument("--limit", type=int, default=0, help="pilot on N files")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--tag", default="all")
    args = ap.parse_args()

    roots = (args.roots.split(",") if args.roots else ROOTS)
    files = []
    for r in roots:
        d = BASE_DIR / r
        if d.exists():
            found = sorted(str(p) for p in d.rglob("*.html.gz"))
            print(f"  {r}: {len(found):,} captures")
            files.extend(found)
    if not files:
        sys.exit("no HTML found")
    if args.limit:
        # Stride rather than head: the head of a sorted list is one alphabetical
        # corner of the seller space, which is not a pilot of the corpus.
        step = max(1, len(files) // args.limit)
        files = files[::step][:args.limit]
    print(f"Scanning {len(files):,} captures on {args.workers} workers\n")

    orders = {}                       # order_id -> row  (dedupe across captures)
    pages_with_blob = pages = 0
    caps_per_gig = Counter()
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for res in ex.map(scan, files, chunksize=32):
            done += 1
            if done % 5000 == 0:
                print(f"  {done:,}/{len(files):,}  orders so far {len(orders):,}",
                      flush=True)
            if not res:
                continue
            gig, cap, rows = res
            pages += 1
            caps_per_gig[gig] += 1
            if rows:
                pages_with_blob += 1
            for r in rows:
                oid = r["order_id"]
                if not oid:
                    continue
                prev = orders.get(oid)
                # Keep the EARLIEST capture that showed the order: it is the one
                # closest to the transaction, and it makes the row deterministic
                # regardless of file iteration order.
                if prev is None or r["capture_date"] < prev["capture_date"]:
                    orders[oid] = r

    rows = sorted(orders.values(), key=lambda r: (r["order_date"], r["order_id"]))
    OUTDIR.mkdir(parents=True, exist_ok=True)
    RUNDIR.mkdir(parents=True, exist_ok=True)
    out = OUTDIR / f"order-panel-{args.tag}.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {out}  ({len(rows):,} distinct orders)")

    # ---------------- report ----------------
    import statistics
    by_q = Counter(r["order_quarter"] for r in rows)
    gigs_q = defaultdict(set)
    for r in rows:
        gigs_q[r["order_quarter"]].add(r["gig_id"])

    L = [f"# Order panel — reach of the HTML already on disk ({args.tag})",
         "",
         f"Captures scanned: **{len(files):,}** over {', '.join(roots)}. "
         f"Pages parsed: {pages:,}, of which **{pages_with_blob:,}** carried at least "
         f"one displayed order. Distinct gigs: {len(caps_per_gig):,}.",
         "",
         f"Distinct orders after dedupe on `encrypted_order_id`: **{len(rows):,}**.",
         "",
         "## Orders by ORDER quarter (not capture quarter)",
         "",
         "| quarter | orders | distinct gigs | priced | median paid (mid) |",
         "|---|---:|---:|---:|---:|"]
    for q in sorted(by_q):
        qp = [float(r["paid_mid"]) for r in rows
              if r["order_quarter"] == q and r["paid_mid"] != ""]
        med = f"${statistics.median(qp):,.0f}" if qp else "-"
        L.append(f"| {q} | {by_q[q]:,} | {len(gigs_q[q]):,} | {len(qp):,} | {med} |")

    L += ["", "## What this is not", "",
          "This is a transaction series on **bucketed realised values**, not the IPI, "
          "which is a matched-model index on **listed** basic-package prices. They are "
          "different price objects and must not be chained together.",
          "",
          "## Three limits, from steps 59 and 63", "",
          "1. The paid-amount field appears **from 2022** only.",
          "2. A page displays ~4 of ~124 reviews, ranked by `relevancy_score`, so this "
          "is a sample of each gig's orders. Step 63A found no **price** selection in "
          "that ranking (late minus early +0 USD, CI [+0, +0]).",
          "3. Fiverr publishes a **range**, so `paid_mid` is the midpoint of a closed "
          "bucket and is an assumption; open-topped buckets are excluded from medians.",
          ""]
    rep = RUNDIR / f"reach-{args.tag}.md"
    rep.write_text("\n".join(L))
    print(f"Wrote {rep}")

    late = {q: by_q[q] for q in by_q if q >= "2025Q1"}
    print(f"\nOrders dated 2025Q1 or later: {sum(late.values()):,}")
    for q in sorted(late):
        print(f"  {q}: {late[q]:,} orders, {len(gigs_q[q]):,} gigs")


if __name__ == "__main__":
    main()
