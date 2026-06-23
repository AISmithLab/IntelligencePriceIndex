#!/usr/bin/env python3
"""
Scrape current prices directly from Fiverr for all pilot gigs.

Reads unique (seller, slug) pairs from data/pilot/pilot-prices.csv,
fetches https://www.fiverr.com/{seller}/{slug}, extracts prices,
and appends new rows to data/pilot/pilot-prices.csv.

Usage:
    python3 scrape-current-prices.py
"""

import asyncio
import aiohttp
import csv
import json
import re
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_CSV = BASE_DIR / "data" / "pilot" / "pilot-prices.csv"
OUTPUT_CSV = BASE_DIR / "data" / "pilot" / "pilot-prices-2026.csv"
CHECKPOINT = BASE_DIR / "data" / "pilot" / "scrape-checkpoint.txt"
LOG = BASE_DIR / "runs" / "scrape-current.log"

TODAY = datetime.now().strftime("%Y%m%d")
YEAR = datetime.now().strftime("%Y")
MONTH = datetime.now().strftime("%m")

MAX_CONCURRENT = 3
DELAY = 2.0  # seconds between requests per worker
MAX_RETRIES = 3

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

FIELDS = [
    "seller", "slug", "date", "year", "month",
    "price_basic", "price_standard", "price_premium",
    "title", "rating", "review_count",
    "extraction_method", "file_path",
]


def load_gigs():
    """Load unique (seller, slug) pairs from pilot-prices.csv."""
    gigs = set()
    with open(INPUT_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            gigs.add((row["seller"], row["slug"]))
    return sorted(gigs)


def load_checkpoint():
    done = set()
    if CHECKPOINT.exists():
        with open(CHECKPOINT) as f:
            for line in f:
                line = line.strip()
                if line:
                    done.add(line)
    return done


def save_checkpoint(seller, slug):
    with open(CHECKPOINT, "a") as f:
        f.write(f"{seller}/{slug}\n")


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


def extract_prices(html, seller, slug):
    """Extract prices from Fiverr HTML. Returns dict or None."""
    result = {
        "seller": seller, "slug": slug,
        "date": TODAY, "year": YEAR, "month": MONTH,
        "price_basic": "", "price_standard": "", "price_premium": "",
        "title": "", "rating": "", "review_count": "",
        "extraction_method": "", "file_path": "",
    }

    # Method 1: packageList JSON (modern Fiverr)
    raw = find_package_list_json(html)
    if raw:
        try:
            packages = json.loads(raw)
            labels = ["price_basic", "price_standard", "price_premium"]
            for i, pkg in enumerate(packages[:3]):
                price = pkg.get("price", 0)
                if isinstance(price, (int, float)) and price > 100:
                    price = price / 100.0  # cents to dollars
                result[labels[i]] = price
            result["extraction_method"] = "packageList"
        except Exception:
            pass

    # Method 2: dollar sign fallback
    if not result["price_basic"]:
        m = re.search(r'\$(\d+(?:\.\d+)?)', html)
        if m:
            result["price_basic"] = float(m.group(1))
            result["extraction_method"] = "dollar_fallback"

    # Extract title
    m = re.search(r'<title>([^<]+)</title>', html)
    if m:
        result["title"] = m.group(1).strip()[:200]

    # Extract rating
    m = re.search(r'"avgSellerRating"\s*:\s*([\d.]+)', html)
    if m:
        result["rating"] = m.group(1)

    # Extract review count
    m = re.search(r'"sellerRatingCount"\s*:\s*(\d+)', html)
    if m:
        result["review_count"] = m.group(1)

    if result["extraction_method"]:
        return result
    return None


async def fetch_gig(session, semaphore, seller, slug, writer, logfile):
    url = f"https://www.fiverr.com/{seller}/{slug}"
    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                await asyncio.sleep(DELAY)
                async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        row = extract_prices(html, seller, slug)
                        if row:
                            writer.writerow(row)
                            save_checkpoint(seller, slug)
                            msg = f"OK {seller}/{slug} basic=${row['price_basic']}"
                        else:
                            msg = f"NO_PRICE {seller}/{slug}"
                            save_checkpoint(seller, slug)
                        print(msg)
                        logfile.write(msg + "\n")
                        logfile.flush()
                        return
                    elif resp.status == 404:
                        msg = f"404 {seller}/{slug} (gig removed)"
                        print(msg)
                        logfile.write(msg + "\n")
                        save_checkpoint(seller, slug)
                        return
                    elif resp.status == 429:
                        wait = 30 * (attempt + 1)
                        msg = f"RATE_LIMITED {seller}/{slug}, waiting {wait}s"
                        print(msg)
                        logfile.write(msg + "\n")
                        await asyncio.sleep(wait)
                    else:
                        msg = f"HTTP_{resp.status} {seller}/{slug}"
                        print(msg)
                        logfile.write(msg + "\n")
                        await asyncio.sleep(10)
            except Exception as e:
                msg = f"ERROR {seller}/{slug}: {e}"
                print(msg)
                logfile.write(msg + "\n")
                await asyncio.sleep(10 * (attempt + 1))


async def main():
    LOG.parent.mkdir(exist_ok=True)
    gigs = load_gigs()
    done = load_checkpoint()
    remaining = [(s, g) for s, g in gigs if f"{s}/{g}" not in done]

    print(f"Total gigs: {len(gigs)}")
    print(f"Already done: {len(done)}")
    print(f"Remaining: {len(remaining)}")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    with open(OUTPUT_CSV, "w", newline="") as csvfile, open(LOG, "w") as logfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDS)
        writer.writeheader()

        connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT + 2)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [fetch_gig(session, semaphore, seller, slug, writer, logfile)
                     for seller, slug in remaining]
            await asyncio.gather(*tasks)

    print(f"\nDone! Results saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    asyncio.run(main())
