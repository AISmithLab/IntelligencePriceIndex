#!/usr/bin/env python3
"""
Fetch 2025-2026 Wayback Machine snapshots for pilot gigs only.

Instead of downloading the full CDX index, queries the CDX API for each
specific (seller, slug) URL directly. Then downloads the HTML.

Usage:
    python3 fetch-pilot-2025.py

Input:  data/pilot/pilot-prices.csv  (to get seller/slug pairs)
Output: data/pilot-2025/manifest.tsv
        data/pilot-2025/html/<seller>/<YYYYMMDD>_<slug>.html
        data/pilot-2025/prices-2025.csv
"""

import asyncio
import aiohttp
import csv
import json
import re
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_CSV = BASE_DIR / "data" / "pilot" / "pilot-prices.csv"
OUT_DIR = BASE_DIR / "data" / "pilot-2025"
MANIFEST = OUT_DIR / "manifest.tsv"
HTML_DIR = OUT_DIR / "html"
PRICES_CSV = OUT_DIR / "prices-2025.csv"
CDX_CHECKPOINT = OUT_DIR / "cdx-done.txt"
HTML_CHECKPOINT = OUT_DIR / "html-done.txt"
LOG = BASE_DIR / "runs" / "fetch-pilot-2025.log"

OUT_DIR.mkdir(parents=True, exist_ok=True)
HTML_DIR.mkdir(parents=True, exist_ok=True)
LOG.parent.mkdir(exist_ok=True)

CDX_API = "https://web.archive.org/cdx/search/cdx"
WAYBACK = "https://web.archive.org/web/{timestamp}id_/{url}"
FROM_DATE = "20250101000000"
TO_DATE = "20260630235959"

CDX_CONCURRENCY = 5
HTML_CONCURRENCY = 3
DELAY = 1.5
MAX_RETRIES = 4

FIELDS = [
    "seller", "slug", "date", "year", "month",
    "price_basic", "price_standard", "price_premium",
    "title", "rating", "review_count",
    "extraction_method", "file_path",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; research bot; contact: research@example.com)",
}


def load_gigs():
    gigs = set()
    with open(INPUT_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            gigs.add((row["seller"], row["slug"]))
    return sorted(gigs)


def load_set(path):
    done = set()
    if path.exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    done.add(line)
    return done


def append_line(path, line):
    with open(path, "a") as f:
        f.write(line + "\n")


async def fetch_cdx_for_gig(session, semaphore, seller, slug, logfile):
    url = f"fiverr.com/{seller}/{slug}"
    params = {
        "url": url,
        "matchType": "exact",
        "output": "json",
        "fl": "timestamp,original,statuscode",
        "from": FROM_DATE,
        "to": TO_DATE,
        "filter": "statuscode:200",
        "collapse": "timestamp:6",  # one per month
    }
    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                await asyncio.sleep(DELAY)
                async with session.get(CDX_API, params=params,
                                       headers=HEADERS,
                                       timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        rows = json.loads(text) if text.strip() else []
                        # first row is header ["timestamp","original","statuscode"]
                        snapshots = rows[1:] if rows and rows[0][0] == "timestamp" else rows
                        msg = f"CDX {seller}/{slug}: {len(snapshots)} snapshots"
                        print(msg)
                        logfile.write(msg + "\n")
                        logfile.flush()
                        return snapshots
                    elif resp.status in (429, 503):
                        wait = 20 * (attempt + 1)
                        print(f"CDX rate limited {seller}/{slug}, waiting {wait}s")
                        await asyncio.sleep(wait)
                    else:
                        print(f"CDX HTTP {resp.status} {seller}/{slug}")
                        await asyncio.sleep(10)
            except Exception as e:
                wait = 10 * (attempt + 1)
                print(f"CDX error {seller}/{slug}: {e}, retry in {wait}s")
                await asyncio.sleep(wait)
    return []


async def download_html(session, semaphore, timestamp, original_url, seller, slug, logfile):
    wb_url = WAYBACK.format(timestamp=timestamp, url=original_url)
    date = timestamp[:8]
    out_dir = HTML_DIR / seller
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date}_{slug}.html"

    if out_path.exists():
        return str(out_path)

    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                await asyncio.sleep(DELAY)
                async with session.get(wb_url, headers=HEADERS,
                                       timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status == 200:
                        html = await resp.text(errors="replace")
                        out_path.write_text(html, encoding="utf-8")
                        return str(out_path)
                    elif resp.status in (429, 503):
                        wait = 30 * (attempt + 1)
                        print(f"HTML rate limited {seller}/{slug} {date}, waiting {wait}s")
                        await asyncio.sleep(wait)
                    elif resp.status == 404:
                        return None
                    else:
                        print(f"HTML HTTP {resp.status} {seller}/{slug} {date}")
                        await asyncio.sleep(10)
            except Exception as e:
                wait = 10 * (attempt + 1)
                print(f"HTML error {seller}/{slug} {date}: {e}")
                await asyncio.sleep(wait)
    return None


def find_package_list_json(html):
    start_match = re.search(r'packageList"\s*:\s*\[', html)
    if not start_match:
        return None
    start = start_match.end() - 1
    depth = 0
    for i in range(start, len(html)):
        if html[i] == '[':
            depth += 1
        elif html[i] == ']':
            depth -= 1
            if depth == 0:
                return html[start:i + 1]
    return None


def extract_prices(html, seller, slug, timestamp, file_path):
    date = timestamp[:8]
    year = timestamp[:4]
    month = timestamp[4:6]
    result = {
        "seller": seller, "slug": slug,
        "date": date, "year": year, "month": month,
        "price_basic": "", "price_standard": "", "price_premium": "",
        "title": "", "rating": "", "review_count": "",
        "extraction_method": "", "file_path": file_path,
    }

    raw = find_package_list_json(html)
    if raw:
        try:
            packages = json.loads(raw)
            labels = ["price_basic", "price_standard", "price_premium"]
            for i, pkg in enumerate(packages[:3]):
                price = pkg.get("price", 0)
                if isinstance(price, (int, float)) and price > 100:
                    price = price / 100.0
                result[labels[i]] = price
            result["extraction_method"] = "packageList"
        except Exception:
            pass

    if not result["price_basic"]:
        m = re.search(r'\$(\d+(?:\.\d+)?)', html)
        if m:
            result["price_basic"] = float(m.group(1))
            result["extraction_method"] = "dollar_fallback"

    m = re.search(r'<title>([^<]+)</title>', html)
    if m:
        result["title"] = m.group(1).strip()[:200]

    m = re.search(r'"avgSellerRating"\s*:\s*([\d.]+)', html)
    if m:
        result["rating"] = m.group(1)

    m = re.search(r'"sellerRatingCount"\s*:\s*(\d+)', html)
    if m:
        result["review_count"] = m.group(1)

    return result if result["extraction_method"] else None


async def main():
    gigs = load_gigs()
    cdx_done = load_set(CDX_CHECKPOINT)
    html_done = load_set(HTML_CHECKPOINT)

    print(f"Total gigs: {len(gigs)}")
    print(f"CDX already fetched: {len(cdx_done)}")

    cdx_remaining = [(s, g) for s, g in gigs if f"{s}/{g}" not in cdx_done]
    print(f"CDX remaining: {len(cdx_remaining)}")

    # Phase 1: fetch CDX manifest
    manifest_entries = []

    # Load existing manifest entries
    if MANIFEST.exists():
        with open(MANIFEST) as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                manifest_entries.append(row)

    with open(LOG, "a") as logfile:
        logfile.write(f"\n=== Run started {datetime.now()} ===\n")

        if cdx_remaining:
            print(f"\n--- Phase 1: CDX lookup for {len(cdx_remaining)} gigs ---")
            cdx_sem = asyncio.Semaphore(CDX_CONCURRENCY)
            connector = aiohttp.TCPConnector(limit=CDX_CONCURRENCY + 2)

            with open(MANIFEST, "a", newline="") as mf:
                writer = csv.writer(mf, delimiter="\t")
                if not MANIFEST.exists() or MANIFEST.stat().st_size == 0:
                    writer.writerow(["timestamp", "original", "seller", "slug"])

                async with aiohttp.ClientSession(connector=connector) as session:
                    tasks = [fetch_cdx_for_gig(session, cdx_sem, s, g, logfile)
                             for s, g in cdx_remaining]
                    results = await asyncio.gather(*tasks)

                for (seller, slug), snapshots in zip(cdx_remaining, results):
                    for snap in snapshots:
                        timestamp, original, *_ = snap
                        writer.writerow([timestamp, original, seller, slug])
                        manifest_entries.append({
                            "timestamp": timestamp,
                            "original": original,
                            "seller": seller,
                            "slug": slug,
                        })
                    append_line(CDX_CHECKPOINT, f"{seller}/{slug}")

        # Phase 2: download HTML
        to_download = [e for e in manifest_entries
                       if f"{e['seller']}/{e['slug']}/{e['timestamp'][:8]}" not in html_done]

        print(f"\n--- Phase 2: downloading {len(to_download)} HTML snapshots ---")

        html_sem = asyncio.Semaphore(HTML_CONCURRENCY)
        connector2 = aiohttp.TCPConnector(limit=HTML_CONCURRENCY + 2)

        with open(PRICES_CSV, "a", newline="") as pf:
            price_writer = csv.DictWriter(pf, fieldnames=FIELDS)
            if not PRICES_CSV.exists() or PRICES_CSV.stat().st_size == 0:
                price_writer.writeheader()

            async with aiohttp.ClientSession(connector=connector2) as session:
                for entry in to_download:
                    seller = entry["seller"]
                    slug = entry["slug"]
                    timestamp = entry["timestamp"]
                    original = entry["original"]
                    key = f"{seller}/{slug}/{timestamp[:8]}"

                    path = await download_html(session, html_sem, timestamp, original,
                                               seller, slug, logfile)
                    if path:
                        html = Path(path).read_text(encoding="utf-8", errors="replace")
                        row = extract_prices(html, seller, slug, timestamp, path)
                        if row:
                            price_writer.writerow(row)
                            pf.flush()
                            print(f"OK {seller}/{slug} {timestamp[:8]} basic=${row['price_basic']}")
                    append_line(HTML_CHECKPOINT, key)

    print(f"\nDone! Prices saved to {PRICES_CSV}")


if __name__ == "__main__":
    asyncio.run(main())
