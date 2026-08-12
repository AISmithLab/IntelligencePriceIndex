#!/usr/bin/env python3
"""
Extract prices and metadata from downloaded Fiverr HTML snapshots.

Handles three format eras:
  1. 2020+: packageList JSON (price in cents)
  2. 2018-2020: <span class="price">$X</span> + packageList sometimes
  3. Pre-2017: JSON with "price":"X.0" (string dollars) + meta/span tags

Output: data/pilot/pilot-prices.csv

Columns: seller, slug, date, year, month,
         price_basic, price_standard, price_premium,
         title, category_slug, rating, review_count,
         extraction_method
"""

import csv
import gzip
import json
import os
import re
import sys
from pathlib import Path
from html.parser import HTMLParser

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_DIR = BASE_DIR / "data" / "pilot" / "html"
OUTPUT = BASE_DIR / "data" / "pilot" / "pilot-prices.csv"
ERRORS_LOG = BASE_DIR / "data" / "pilot" / "extraction-errors.tsv"

FIELDS = [
    "seller", "slug", "date", "year", "month",
    "price_basic", "price_standard", "price_premium",
    "title", "rating", "review_count",
    "extraction_method", "file_path",
]


def find_package_list_json(html):
    """Find the packageList array in HTML, handling nested brackets."""
    start_match = re.search(r'packageList"\s*:\s*\[', html)
    if not start_match:
        return None
    start = start_match.end() - 1  # position of '['
    depth = 0
    for i in range(start, len(html)):
        if html[i] == '[':
            depth += 1
        elif html[i] == ']':
            depth -= 1
            if depth == 0:
                return html[start:i + 1]
    return None


def extract_package_list(html):
    """Extract prices from packageList JSON (price in cents for modern pages)."""
    raw = find_package_list_json(html)
    if not raw:
        return None

    try:
        packages = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: extract top-level package prices using a targeted pattern
        # Match "id":N followed by "price":N at the same nesting level
        prices = []
        for m in re.finditer(r'"id"\s*:\s*(\d+)\s*,\s*"title"\s*:"[^"]*"\s*,\s*"description"\s*:"[^"]*"\s*,\s*"price"\s*:\s*(\d+)', raw):
            prices.append(int(m.group(2)))
        if not prices:
            # Simpler: find "price":N right after "description"
            for m in re.finditer(r'"description"\s*:\s*"[^"]*"\s*,\s*"price"\s*:\s*(\d+)', raw):
                prices.append(int(m.group(1)))
        if prices:
            result = {"extraction_method": "packageList_partial"}
            labels = ["price_basic", "price_standard", "price_premium"]
            for i, p in enumerate(prices[:3]):
                result[labels[i]] = p / 100.0
            return result
        return None

    if not packages:
        return None

    result = {"extraction_method": "packageList"}
    labels = ["price_basic", "price_standard", "price_premium"]
    for i, pkg in enumerate(packages[:3]):
        price = pkg.get("price", 0)
        if isinstance(price, (int, float)):
            # Fiverr stores prices in cents (e.g., 2500 = $25)
            result[labels[i]] = price / 100.0
        elif isinstance(price, str):
            try:
                result[labels[i]] = float(price)
            except ValueError:
                pass

    return result if any(k.startswith("price_") for k in result) else None


def extract_old_json(html):
    """Extract prices from old-style JSON (pre-2017, price as string dollars)."""
    # Look for array of package objects with "price":"5.0"
    matches = re.findall(r'\{"id"\s*:\s*\d+\s*,\s*"price"\s*:\s*"([\d.]+)"', html)
    if not matches:
        return None

    result = {"extraction_method": "old_json"}
    labels = ["price_basic", "price_standard", "price_premium"]
    for i, price_str in enumerate(matches[:3]):
        try:
            result[labels[i]] = float(price_str)
        except ValueError:
            pass

    return result if any(k.startswith("price_") for k in result) else None


def extract_span_price(html):
    """Extract price from <span class="price">$X</span> or similar HTML."""
    matches = re.findall(r'class="price"[^>]*>\s*\$\s*([\d,]+(?:\.\d+)?)', html)
    if not matches:
        # Try content attribute
        match = re.search(r'"price"\s+content="\$([\d,]+(?:\.\d+)?)"', html)
        if match:
            matches = [match.group(1)]

    if not matches:
        return None

    prices = []
    for m in matches:
        try:
            prices.append(float(m.replace(",", "")))
        except ValueError:
            pass

    if not prices:
        return None

    # Deduplicate and sort
    prices = sorted(set(prices))

    result = {"extraction_method": "html_span"}
    labels = ["price_basic", "price_standard", "price_premium"]
    for i, p in enumerate(prices[:3]):
        result[labels[i]] = p

    return result


def extract_dollar_amounts(html):
    """Last resort: find dollar amounts in og:title or price-related spans."""
    # Try og:title which often has "for $X"
    title_match = re.search(r'(?:og:title|"title")["\s:>]+[^"<]*\$(\d+(?:,\d+)?)', html)
    if title_match:
        try:
            price = float(title_match.group(1).replace(",", ""))
            if price > 0:
                return {"price_basic": price, "extraction_method": "dollar_title"}
        except ValueError:
            pass

    # Find price-related dollar amounts (skip $0)
    matches = re.findall(r'\$(\d+(?:,\d+)*)', html)
    prices = []
    for m in matches:
        try:
            p = float(m.replace(",", ""))
            if p > 0:
                prices.append(p)
        except ValueError:
            pass

    if not prices:
        return None

    # Use the most common price as basic (likely the displayed price)
    from collections import Counter
    price_counts = Counter(prices)
    most_common = [p for p, _ in price_counts.most_common()]
    # Filter out very large/small values that are likely not gig prices
    most_common = [p for p in most_common if 1 <= p <= 50000]

    if not most_common:
        return None

    result = {"extraction_method": "dollar_fallback"}
    labels = ["price_basic", "price_standard", "price_premium"]
    for i, p in enumerate(sorted(set(most_common[:3]))):
        result[labels[i]] = p

    return result


def extract_title(html):
    """Extract gig title from og:title or <h1>."""
    # og:title
    match = re.search(r'property="og:title"\s+content="([^"]+)"', html)
    if not match:
        match = re.search(r'content="([^"]+)"\s+property="og:title"', html)
    if match:
        return match.group(1).strip()

    # <h1> tag
    match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    if match:
        return match.group(1).strip()

    return ""


def extract_rating(html):
    """Extract rating and review count."""
    rating = None
    review_count = None

    # Look for rating in structured data or common patterns
    match = re.search(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html)
    if match:
        try:
            rating = float(match.group(1))
        except ValueError:
            pass

    match = re.search(r'"reviewCount"\s*:\s*"?(\d+)"?', html)
    if match:
        try:
            review_count = int(match.group(1))
        except ValueError:
            pass

    # Fallback: look for "(XXX reviews)" or "(XXX)"
    if review_count is None:
        match = re.search(r'\((\d[\d,]*)\s*reviews?\)', html, re.IGNORECASE)
        if match:
            try:
                review_count = int(match.group(1).replace(",", ""))
            except ValueError:
                pass

    return rating, review_count


def process_file(filepath):
    """Extract all data from a single HTML file."""
    # Parse filename: <YYYYMMDD>_<slug>.html or <YYYYMMDD>_<slug>.html.gz
    # (.stem on a .html.gz leaves the ".html", which would land in the slug)
    fname = filepath.name
    for suffix in (".html.gz", ".html"):
        if fname.endswith(suffix):
            fname = fname[:-len(suffix)]
            break
    seller = filepath.parent.name

    parts = fname.split("_", 1)
    date = parts[0]
    slug = parts[1] if len(parts) > 1 else ""

    year = date[:4] if len(date) >= 4 else ""
    month = date[4:6] if len(date) >= 6 else ""

    opener = gzip.open if filepath.name.endswith(".gz") else open
    try:
        with opener(filepath, "rt", encoding="utf-8", errors="replace") as f:
            html = f.read()
    except Exception:
        return None, "read_error"

    if len(html) < 100:
        return None, "too_short"

    # Try extraction methods in order of reliability
    result = extract_package_list(html)

    # For non-packageList pages, try old_json but validate prices > 0
    if not result:
        result = extract_old_json(html)
        # If old_json returned all zeros, it matched wrong JSON objects — discard
        if result:
            prices = [result.get(f"price_{t}", 0) for t in ("basic", "standard", "premium")]
            if all(p == 0 for p in prices):
                result = None

    if not result:
        result = extract_span_price(html)

    # Last resort for old pages: extract dollar amounts from visible text
    if not result:
        result = extract_dollar_amounts(html)

    if not result:
        return None, "no_price_found"

    # Add metadata
    result["seller"] = seller
    result["slug"] = slug
    result["date"] = date
    result["year"] = year
    result["month"] = month
    result["title"] = extract_title(html)
    try:
        result["file_path"] = str(Path(filepath).resolve().relative_to(BASE_DIR))
    except ValueError:
        result["file_path"] = str(filepath)

    rating, review_count = extract_rating(html)
    result["rating"] = rating if rating is not None else ""
    result["review_count"] = review_count if review_count is not None else ""

    return result, None


def main():
    import argparse
    global HTML_DIR, OUTPUT, ERRORS_LOG
    ap = argparse.ArgumentParser()
    ap.add_argument("--html-dir", type=Path, default=HTML_DIR)
    ap.add_argument("--output", type=Path, default=OUTPUT)
    ap.add_argument("--errors-log", type=Path, default=ERRORS_LOG)
    a = ap.parse_args()
    HTML_DIR, OUTPUT, ERRORS_LOG = a.html_dir, a.output, a.errors_log

    print("Extracting prices from downloaded HTML...")
    print(f"  Input: {HTML_DIR}")

    html_files = sorted(list(HTML_DIR.rglob("*.html")) +
                        list(HTML_DIR.rglob("*.html.gz")))
    print(f"  Found {len(html_files):,} HTML files")

    success = 0
    errors = 0
    error_types = {}
    method_counts = {}

    with open(OUTPUT, "w", newline="") as csvf, \
         open(ERRORS_LOG, "w") as errf:
        writer = csv.DictWriter(csvf, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        errf.write("file\terror\n")

        for i, fpath in enumerate(html_files):
            result, err = process_file(fpath)

            if err:
                errors += 1
                error_types[err] = error_types.get(err, 0) + 1
                errf.write(f"{fpath}\t{err}\n")
            else:
                success += 1
                writer.writerow(result)
                method = result.get("extraction_method", "unknown")
                method_counts[method] = method_counts.get(method, 0) + 1

            if (i + 1) % 5000 == 0:
                print(f"  {i + 1:,}/{len(html_files):,} "
                      f"(ok={success:,} err={errors:,})")

    total = success + errors
    print()
    print("=" * 50)
    print("EXTRACTION RESULTS")
    print("=" * 50)
    print(f"Total files:  {total:,}")
    print(f"Success:      {success:,} ({success/total*100:.1f}%)")
    print(f"Errors:       {errors:,} ({errors/total*100:.1f}%)")
    print()
    print("By method:")
    for method, count in sorted(method_counts.items(), key=lambda x: -x[1]):
        print(f"  {method:<25} {count:>8,} ({count/success*100:.1f}%)")
    print()
    if error_types:
        print("By error type:")
        for err, count in sorted(error_types.items(), key=lambda x: -x[1]):
            print(f"  {err:<25} {count:>8,}")
    print()
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
