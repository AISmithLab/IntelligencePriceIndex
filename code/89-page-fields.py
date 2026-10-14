#!/usr/bin/env python3
"""
89 — Fields on stored gig pages that no step has extracted yet.

EXPLORATORY. Feeds step 90's AI-exposure tests. Scans the same four HTML roots
as step 86 and writes two files:

  data/pilot/page-fields-<tag>.csv   one row per capture
      package prices (cents -> USD), word_count calculator value, revisions and
      delivery hours for each of the up-to-3 packages; seller country (from
      `sellerCard.countryCode`); gig-description AI flags.
  data/pilot/order-fields-<tag>.csv  one row per displayed order (deduped on
      encrypted_order_id, earliest capture kept, as in step 86)
      repeat_buyer, rating, order quarter, review-text AI flags.

COVERAGE, measured on 300 captures per year before this was written:
packageList / sellerCard / description 98-100% of captures 2020-2024 (12% in
2018, 78% in 2019); the word_count calculator 10-19% every year (it exists only
for word-priced services, so its share is a category mix, not a reporting
change); repeat_buyer 0% before 2021, 41% in 2021, 96-99% 2022-2023. So the
repeat-buyer test has the same short pre-period as step 88.

    python3 code/89-page-fields.py --limit 2000 --tag pilot
    python3 code/89-page-fields.py --tag all
"""

import argparse
import csv
import gzip
import json
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ROOTS = ["data/pilot/html-refresh2025", "data/pilot/html-recent",
         "data/pilot/html-balanced", "data/pilot/html"]
OUTDIR = BASE_DIR / "data" / "pilot"
CAP_RE = re.compile(r"(\d{8})_(.+)\.html\.gz$")
DESC_RE = re.compile(r'"description":\{"content":"((?:[^"\\]|\\.)*)"')
COUNTRY_RE = re.compile(r'"sellerCard":\{.{0,400}?"countryCode":"([A-Z]{2})"', re.S)

# Generative-AI terms only. Bare "AI" is NOT matched: on design pages it is the
# Adobe Illustrator file format ("Source file AI, EPS, PSD"), which the pilot
# found in ~5% of 2020 descriptions. "Artificial intelligence" / "machine
# learning" are long-standing coding services, also excluded.
AI_USE = re.compile(r"(?i)\b(chat\s?gpt|gpt-?[34]\w*|openai|midjourney|stable diffusion|"
                    r"dall-?e|elevenlabs|claude ai|gemini ai|copilot|"
                    r"ai[- ](generated|powered|assisted|art|artwork|images?|voices?|"
                    r"writ\w*|content|tools?|music|avatar|video|model)|"
                    r"(using|with|by|via|leverag\w+)\s+ai\b|generative ai)\b")
ANTI_AI = re.compile(r"(?i)\b(no|not|without|zero|never|free of|free from)\s+"
                     r"(the\s+)?(use\s+of\s+)?(ai|a\.i\.|chat\s?gpt|gpt|machine translation|"
                     r"google translate|automated tools?)\b|100\s?%\s*human|"
                     r"\bhuman[- ](written|made|translat\w*|created|generated)|"
                     r"\bhand[- ]?written\b|\bnot\s+ai[- ]generated|\bai[- ]free\b")
MT = re.compile(r"(?i)\b(machine translat\w*|google translat\w*|deepl)\b")

PAGE_FIELDS = ["gig_id", "capture_date", "n_pkg",
               "p1", "p2", "p3", "w1", "w2", "w3", "rev1", "rev2", "rev3",
               "dur1", "dur2", "dur3", "seller_country",
               "desc_len", "desc_ai", "desc_anti_ai"]
ORDER_FIELDS = ["gig_id", "order_id", "order_quarter", "capture_date",
                "repeat_buyer", "rating", "has_comment", "cm_ai", "cm_mt"]


def match_bracket(s, j):
    """String-aware bracket match from s[j] in '[{'; returns end index or -1."""
    open_c = s[j]
    close_c = "]" if open_c == "[" else "}"
    depth = 0
    in_str = esc = False
    for k in range(j, len(s)):
        c = s[k]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == open_c:
            depth += 1
        elif c == close_c:
            depth -= 1
            if depth == 0:
                return k
    return -1


def load_json_at(html, key):
    i = html.find(key)
    if i < 0:
        return None
    j = i + len(key)
    while j < len(html) and html[j] not in "[{":
        j += 1
    if j >= len(html):
        return None
    k = match_bracket(html, j)
    if k < 0:
        return None
    try:
        return json.loads(html[j:k + 1])
    except json.JSONDecodeError:
        return None


def word_count(pkg):
    for c in pkg.get("calculators") or []:
        if c.get("name") == "word_count" and c.get("included", True):
            return c.get("value")
    return None


def scan(path):
    p = Path(path)
    m = CAP_RE.search(p.name)
    if not m:
        return None
    cap, slug = m.group(1), m.group(2)
    gig = f"{p.parent.name}/{slug}"
    try:
        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as f:
            html = f.read()
    except (OSError, EOFError):
        return None

    row = {"gig_id": gig, "capture_date": cap}
    pkgs = load_json_at(html, '"packageList":') or []
    row["n_pkg"] = len(pkgs)
    for n in (1, 2, 3):
        pk = pkgs[n - 1] if len(pkgs) >= n and isinstance(pkgs[n - 1], dict) else {}
        pr = pk.get("price")
        row[f"p{n}"] = pr / 100 if isinstance(pr, (int, float)) else ""
        wc = word_count(pk) if pk else None
        row[f"w{n}"] = wc if isinstance(wc, (int, float)) else ""
        rv = pk.get("revisions")
        row[f"rev{n}"] = rv if isinstance(rv, (int, float)) else ""
        du = pk.get("duration")
        row[f"dur{n}"] = du if isinstance(du, (int, float)) else ""
    cm = COUNTRY_RE.search(html)
    row["seller_country"] = cm.group(1) if cm else ""
    dm = DESC_RE.search(html)
    desc = ""
    if dm:
        try:
            desc = json.loads(f'"{dm.group(1)}"')
        except json.JSONDecodeError:
            desc = dm.group(1)
        desc = re.sub(r"<[^>]+>", " ", desc)
    row["desc_len"] = len(desc) if dm else ""
    row["desc_ai"] = int(bool(AI_USE.search(desc))) if dm else ""
    row["desc_anti_ai"] = int(bool(ANTI_AI.search(desc))) if dm else ""

    orders = []
    # step 86's anchor: the first bare '"reviews":' on a page can be another object
    obj = None
    i = html.find('"reviews":{"has_next"')
    if i >= 0:
        j = html.find("{", i)
        k = match_bracket(html, j)
        if k > 0:
            try:
                obj = json.loads(html[j:k + 1])
            except json.JSONDecodeError:
                obj = None
    for rv in (obj or {}).get("reviews") or []:
        created = rv.get("created_at") or ""
        oid = rv.get("encrypted_order_id") or rv.get("id") or ""
        if len(created) < 7 or not oid:
            continue
        try:
            om = int(created[5:7])
        except ValueError:
            continue
        if not 1 <= om <= 12:
            continue
        txt = rv.get("comment") or ""
        rb = rv.get("repeat_buyer")
        orders.append({
            "gig_id": gig, "order_id": oid,
            "order_quarter": f"{created[:4]}Q{(om - 1) // 3 + 1}",
            "capture_date": cap,
            "repeat_buyer": "" if rb is None else int(bool(rb)),
            "rating": rv.get("value", ""),
            "has_comment": int(bool(txt.strip())),
            "cm_ai": int(bool(AI_USE.search(txt))),
            "cm_mt": int(bool(MT.search(txt))),
        })
    return row, orders


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--tag", default="all")
    args = ap.parse_args()

    files = []
    for r in ROOTS:
        d = BASE_DIR / r
        if d.exists():
            files.extend(sorted(str(p) for p in d.rglob("*.html.gz")))
    if not files:
        sys.exit("no HTML found")
    if args.limit:
        step = max(1, len(files) // args.limit)
        files = files[::step][:args.limit]
    print(f"Scanning {len(files):,} captures on {args.workers} workers", flush=True)

    pages, orders = [], {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for n, res in enumerate(ex.map(scan, files, chunksize=32), 1):
            if n % 20000 == 0:
                print(f"  {n:,}/{len(files):,}", flush=True)
            if not res:
                continue
            row, ords = res
            pages.append(row)
            for o in ords:
                prev = orders.get(o["order_id"])
                if prev is None or o["capture_date"] < prev["capture_date"]:
                    orders[o["order_id"]] = o

    for name, fields, rows in [(f"page-fields-{args.tag}.csv", PAGE_FIELDS, pages),
                               (f"order-fields-{args.tag}.csv", ORDER_FIELDS,
                                list(orders.values()))]:
        with gzip.open(OUTDIR / (name + ".gz"), "wt", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(f"Wrote {OUTDIR / (name + '.gz')}  ({len(rows):,} rows)")


if __name__ == "__main__":
    main()
