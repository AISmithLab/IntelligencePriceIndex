#!/usr/bin/env python3
"""
Step 20 (data validation): programmatic price-extraction spot-check.

The IPI (both the chained and the fixed-effects chart) is only as good as the
prices parsed out of the archived Fiverr pages. This script audits that parsing
on a random sample, using checks that are INDEPENDENT of the pipeline's own
extractor (code/09-extract-prices.py, which reads the `packageList` JSON blob):

  1. Title cross-check  -- Fiverr renders the gig's STARTING price into the page
     <og:title> ("... for $15 on fiverr.com") server-side, separately from the
     packageList JSON. If the parsed price_basic equals the title's dollar
     figure, two independent parts of the page agree -> high confidence.
  2. Presence check     -- the parsed price must literally appear in the raw HTML
     (as cents inside packageList, or as "$X" in text). Catches hallucinated /
     misattributed prices that appear nowhere on the page.
  3. Reproducibility    -- re-run the pipeline extractor on the saved HTML and
     confirm it reproduces the recorded price (catches CSV / pipeline drift).

Outputs an accuracy report + a TSV of every mismatch (with the Wayback URL) for
manual eyeballing. Read-only; touches no site data.

Usage: python code/20-validate-extraction.py [--n 150] [--seed 7]
"""

import argparse
import csv
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "code"))
# reuse the pipeline's own extractor for the reproducibility check
import importlib.util
spec = importlib.util.spec_from_file_location("extract09", BASE_DIR / "code" / "09-extract-prices.py")
extract09 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract09)

PILOT = BASE_DIR / "data" / "pilot"
PRICE_FILES = [PILOT / "recent-prices.csv", PILOT / "pilot-prices.csv"]
OUT_MISMATCH = PILOT / "extraction-validation-mismatches.tsv"

TITLE_RE = re.compile(r'property="og:title"\s+content="([^"]+)"')
TITLE_RE2 = re.compile(r'content="([^"]+)"\s+property="og:title"')
DOLLAR_IN_TITLE = re.compile(r'for\s*\$\s*([\d,]+)')
ANY_DOLLAR = re.compile(r'\$\s*([\d,]+)')


def title_price(html):
    """Independent price signal: the '$X' Fiverr bakes into og:title."""
    m = TITLE_RE.search(html) or TITLE_RE2.search(html)
    if not m:
        return None, None
    title = m.group(1)
    dm = DOLLAR_IN_TITLE.search(title) or ANY_DOLLAR.search(title)
    if not dm:
        return None, title
    try:
        return float(dm.group(1).replace(",", "")), title
    except ValueError:
        return None, title


def present_in_html(html, price):
    """Does the recorded price literally appear on the page?"""
    if price is None:
        return False
    cents = int(round(price * 100))
    dollars = int(price) if price == int(price) else None
    if str(cents) in html:                     # packageList stores cents
        return True
    if re.search(rf'\$\s*{re.escape(str(dollars if dollars is not None else price))}\b', html):
        return True
    if re.search(rf'"price"\s*:\s*"?{re.escape(str(dollars if dollars is not None else price))}(?:\.0+)?"?', html):
        return True
    return False


def load_sample(n, seed):
    import random
    rng = random.Random(seed)
    rows = []
    for pf in PRICE_FILES:
        if not pf.exists():
            continue
        with open(pf) as f:
            for row in csv.DictReader(f):
                row["_src"] = pf.name
                rows.append(row)
    rng.shuffle(rows)
    # keep rows whose HTML we actually have on disk
    kept = []
    for r in rows:
        fp = r.get("file_path", "")
        p = (BASE_DIR / fp) if fp and not Path(fp).is_absolute() else Path(fp)
        if fp and p.exists():
            r["_abspath"] = p
            kept.append(r)
        if len(kept) >= n:
            break
    return kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    sample = load_sample(args.n, args.seed)
    print(f"Validating {len(sample)} randomly-sampled price snapshots "
          f"(seed={args.seed}); HTML re-read from disk.\n")

    n = len(sample)
    title_checked = title_ok = 0
    present_ok = 0
    repro_checked = repro_ok = 0
    mismatches = []
    # breakdowns: (checked, ok) by extraction method and by display era
    from collections import defaultdict
    by_method = defaultdict(lambda: [0, 0])
    by_era = defaultdict(lambda: [0, 0])   # "2020Q1+ (shown)" vs "pre-2020 (not shown)"

    for r in sample:
        try:
            rec = float(r["price_basic"])
        except (ValueError, TypeError, KeyError):
            continue
        html = r["_abspath"].read_text(encoding="utf-8", errors="replace")

        # 1. title cross-check
        tp, title = title_price(html)
        title_agree = None
        if tp is not None:
            title_checked += 1
            title_agree = abs(tp - rec) < 0.01
            if title_agree:
                title_ok += 1
            meth = r.get("extraction_method", "?")
            era = "2020Q1+ (shown on chart)" if (r.get("year", "0") or "0") >= "2020" else "pre-2020 (not shown)"
            by_method[meth][0] += 1; by_method[meth][1] += int(title_agree)
            by_era[era][0] += 1; by_era[era][1] += int(title_agree)

        # 2. presence
        present = present_in_html(html, rec)
        if present:
            present_ok += 1

        # 3. reproducibility (re-run pipeline extractor on the same file)
        repro = None
        res, err = extract09.process_file(r["_abspath"])
        if res is not None:
            repro_checked += 1
            rb = res.get("price_basic")
            repro = (rb is not None and abs(float(rb) - rec) < 0.01)
            if repro:
                repro_ok += 1

        # record anything suspicious
        if (title_agree is False) or (not present) or (repro is False):
            wb = (f"https://web.archive.org/web/{r['date']}/"
                  f"https://www.fiverr.com/{r['seller']}/{r['slug']}")
            mismatches.append({
                "src": r["_src"], "seller": r["seller"], "slug": r["slug"],
                "date": r["date"], "method": r.get("extraction_method", ""),
                "recorded_basic": rec, "title_price": tp,
                "title_agree": title_agree, "present": present, "repro": repro,
                "wayback": wb,
            })

    def pct(a, b):
        return f"{100*a/b:.1f}%" if b else "n/a"

    print("=" * 62)
    print("PRICE-EXTRACTION VALIDATION")
    print("=" * 62)
    print(f"  sampled snapshots ...................... {n}")
    print(f"  [1] title cross-check (independent):")
    print(f"        had a $ price in og:title ....... {title_checked}/{n}")
    print(f"        parsed price == title price ..... {title_ok}/{title_checked}  ({pct(title_ok, title_checked)})")
    print(f"  [2] parsed price present in HTML ........ {present_ok}/{n}  ({pct(present_ok, n)})")
    print(f"  [3] pipeline re-parse reproduces price .. {repro_ok}/{repro_checked}  ({pct(repro_ok, repro_checked)})")

    print(f"\n  title agreement by extraction method:")
    for meth, (c, ok) in sorted(by_method.items(), key=lambda x: -x[1][0]):
        print(f"        {meth:<20} {ok:>3}/{c:<3}  ({pct(ok, c)})")
    print(f"  title agreement by display era (the chart shows 2020Q1+):")
    for era, (c, ok) in sorted(by_era.items()):
        print(f"        {era:<26} {ok:>3}/{c:<3}  ({pct(ok, c)})")

    print(f"\n  suspicious snapshots (any check failed) . {len(mismatches)}")

    if mismatches:
        with open(OUT_MISMATCH, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(mismatches[0].keys()), delimiter="\t")
            w.writeheader()
            w.writerows(mismatches)
        print(f"  -> wrote {OUT_MISMATCH.relative_to(BASE_DIR)} for manual review")
        print("\n  first few flagged (open the wayback URL to eyeball):")
        for m in mismatches[:8]:
            print(f"    {m['method']:<16} rec=${m['recorded_basic']:<7} "
                  f"title={m['title_price']}  present={m['present']} repro={m['repro']}")
            print(f"      {m['wayback']}")


if __name__ == "__main__":
    main()
