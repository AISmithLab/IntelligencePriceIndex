#!/usr/bin/env python3
"""
Step 1.1: Download raw CDX index for fiverr.com gig pages from the Wayback Machine.

Queries CDX API for each letter prefix (a-z), paginating through all results.
Fields retrieved: urlkey, timestamp, original, statuscode, digest, length

THE WINDOW IS AN ARGUMENT, NOT A CONSTANT. The original run (2026-03-22) pulled
all time into `data/cdx-index/raw/` -- 60.0M records, 2011..2026-03. Re-running a
WINDOW is not redundant, for two reasons measured on prefix `q` (2026-09-06):

  * Wayback ingests captures with lag. The March pull saw 212 gig-shaped HTTP-200
    captures in 2025+; the same query today returns 252. **+19%** appeared after
    the fact, and nothing in the March files says so.
  * The March pull's right edge is March 2026. Everything after is simply absent
    (the index holds 13 records for 2026-03 and none later).

So a refresh is how 2025-2026 accrues. It is cheap: 2025+ is ~0.6M of the 60.0M
rows, because the archive was largely walled out of Fiverr after 2024Q3 -- 38% of
2025+ captures are 403 PerimeterX pages and only 19% are 200.

Usage:
    python3 01-download-cdx-index.py                    # 2025-01-01 -> now, into raw-2025/
    python3 01-download-cdx-index.py --from 20110101 --to 20261231 --out raw
    python3 01-download-cdx-index.py --prefixes qxz     # resume a subset
"""

import argparse
import asyncio
import aiohttp
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Set by parse_args() from argv; module-level so both request builders see one window.
RAW_DIR = None
FROM_TS = "20250101000000"
TO_TS = None  # defaults to now, so a refresh always runs to the present edge

CDX_API = "https://web.archive.org/cdx/search/cdx"
FIELDS = "urlkey,timestamp,original,statuscode,digest,length"
MAX_CONCURRENT = 3  # be polite to the Wayback Machine
RETRY_LIMIT = 5
RETRY_BACKOFF = 10  # seconds base backoff


async def get_num_pages(session, prefix):
    """Get the number of CDX pages for a given prefix."""
    params = {
        "url": f"fiverr.com/{prefix}",
        "matchType": "prefix",
        "showNumPages": "true",
        "from": FROM_TS,
        "to": TO_TS,
    }
    for attempt in range(RETRY_LIMIT):
        try:
            async with session.get(CDX_API, params=params, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return int(text.strip())
                elif resp.status in (429, 503):
                    wait = RETRY_BACKOFF * (2 ** attempt)
                    print(f"  [{prefix}] Rate limited (HTTP {resp.status}), waiting {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    print(f"  [{prefix}] Unexpected status {resp.status} getting page count")
                    await asyncio.sleep(RETRY_BACKOFF)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            wait = RETRY_BACKOFF * (2 ** attempt)
            print(f"  [{prefix}] Error getting page count: {e}, retrying in {wait}s...")
            await asyncio.sleep(wait)
    return None


async def download_page(session, prefix, page, num_pages):
    """Download a single CDX page."""
    params = {
        "url": f"fiverr.com/{prefix}",
        "matchType": "prefix",
        "output": "text",
        "fl": FIELDS,
        "page": str(page),
        "from": FROM_TS,
        "to": TO_TS,
    }
    for attempt in range(RETRY_LIMIT):
        try:
            async with session.get(CDX_API, params=params, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                if resp.status == 200:
                    return await resp.text()
                elif resp.status in (429, 503):
                    wait = RETRY_BACKOFF * (2 ** attempt)
                    print(f"  [{prefix}] page {page}/{num_pages}: rate limited, waiting {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    print(f"  [{prefix}] page {page}/{num_pages}: HTTP {resp.status}")
                    await asyncio.sleep(RETRY_BACKOFF)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            wait = RETRY_BACKOFF * (2 ** attempt)
            print(f"  [{prefix}] page {page}/{num_pages}: {e}, retrying in {wait}s...")
            await asyncio.sleep(wait)
    return None


async def download_prefix(session, semaphore, prefix):
    """Download all CDX pages for a single letter prefix."""
    async with semaphore:
        outfile = RAW_DIR / f"{prefix}.tsv"

        # Check for resume: count existing lines
        existing_lines = 0
        start_page = 0
        if outfile.exists():
            with open(outfile, "r") as f:
                existing_lines = sum(1 for _ in f)

        num_pages = await get_num_pages(session, prefix)
        if num_pages is None:
            print(f"[{prefix}] FAILED to get page count, skipping")
            return prefix, 0, False

        if num_pages == 0:
            print(f"[{prefix}] No pages found")
            outfile.touch()
            return prefix, 0, True

        print(f"[{prefix}] {num_pages} pages to download")

        # If we have existing data, estimate where to resume
        # Each page has ~variable lines, so we re-download from scratch if incomplete
        # But if file seems complete (heuristic: > num_pages * 500 lines), skip
        if existing_lines > num_pages * 500:
            print(f"[{prefix}] Already have {existing_lines} lines, appears complete. Skipping.")
            return prefix, existing_lines, True

        total_lines = 0
        mode = "w"  # overwrite to ensure clean data

        with open(outfile, mode) as f:
            for page in range(num_pages):
                data = await download_page(session, prefix, page, num_pages)
                if data is None:
                    print(f"[{prefix}] FAILED on page {page}/{num_pages}")
                    return prefix, total_lines, False

                lines = data.strip()
                if lines:
                    f.write(lines + "\n")
                    f.flush()
                    page_lines = lines.count("\n") + 1
                    total_lines += page_lines

                if (page + 1) % 50 == 0 or page == num_pages - 1:
                    print(f"  [{prefix}] {page+1}/{num_pages} pages done ({total_lines:,} records)")

                # Small delay between pages to be polite
                await asyncio.sleep(0.5)

        print(f"[{prefix}] Complete: {total_lines:,} records")
        return prefix, total_lines, True


def parse_args():
    """--from / --to / --out / --prefixes, all optional."""
    global RAW_DIR, FROM_TS, TO_TS
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="ts_from", default="20250101000000")
    ap.add_argument("--to", dest="ts_to", default=None,
                    help="default: now, so the pull runs to the present edge")
    ap.add_argument("--out", default="raw-2025",
                    help="subdirectory of data/cdx-index/ (default raw-2025; the "
                         "all-time March 2026 pull lives in raw/)")
    ap.add_argument("--prefixes", default="abcdefghijklmnopqrstuvwxyz")
    args = ap.parse_args()

    FROM_TS = args.ts_from.ljust(14, "0")
    TO_TS = (args.ts_to or time.strftime("%Y%m%d%H%M%S", time.gmtime())).ljust(14, "0")
    RAW_DIR = BASE_DIR / "data" / "cdx-index" / args.out
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    return list(args.prefixes)


async def main():
    prefixes = parse_args()
    print(f"Window {FROM_TS} -> {TO_TS}  into data/cdx-index/{RAW_DIR.name}/")
    print(f"Prefixes: {''.join(prefixes)}")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT + 2)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [download_prefix(session, semaphore, p) for p in prefixes]
        results = await asyncio.gather(*tasks)

    # Summary
    print("\n" + "=" * 60)
    print("CDX Index Download Summary")
    print("=" * 60)
    total_records = 0
    failed = []
    for prefix, count, success in results:
        status = "OK" if success else "FAILED"
        print(f"  {prefix}: {count:>10,} records  [{status}]")
        total_records += count
        if not success:
            failed.append(prefix)

    print(f"\nTotal records: {total_records:,}")
    if failed:
        print(f"FAILED prefixes: {', '.join(failed)}")
        print(f"Re-run with: python3 {sys.argv[0]} --prefixes {''.join(failed)}")
    else:
        print("All prefixes downloaded successfully!")

    # Write summary file
    summary_path = RAW_DIR / "download-summary.txt"
    with open(summary_path, "w") as f:
        f.write(f"Download completed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Window: {FROM_TS} -> {TO_TS}\n")
        f.write(f"Total records: {total_records:,}\n")
        f.write(f"Failed prefixes: {', '.join(failed) if failed else 'none'}\n")
        for prefix, count, success in results:
            f.write(f"  {prefix}: {count:,} {'OK' if success else 'FAILED'}\n")


if __name__ == "__main__":
    asyncio.run(main())
