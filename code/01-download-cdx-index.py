#!/usr/bin/env python3
"""
Step 1.1: Download raw CDX index for fiverr.com gig pages from the Wayback Machine.

Queries CDX API for each letter prefix (a-z), paginating through all results.
Stores raw CDX records as TSV files in data/cdx-index/raw/.

Fields retrieved: urlkey, timestamp, original, statuscode, digest, length
"""

import asyncio
import aiohttp
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "cdx-index" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

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


async def main():
    prefixes = list("abcdefghijklmnopqrstuvwxyz")

    # Allow resuming specific prefixes
    if len(sys.argv) > 1:
        prefixes = list(sys.argv[1])
        print(f"Downloading only prefixes: {prefixes}")

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
        print(f"Re-run with: python3 {sys.argv[0]} {''.join(failed)}")
    else:
        print("All prefixes downloaded successfully!")

    # Write summary file
    summary_path = RAW_DIR / "download-summary.txt"
    with open(summary_path, "w") as f:
        f.write(f"Download completed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total records: {total_records:,}\n")
        f.write(f"Failed prefixes: {', '.join(failed) if failed else 'none'}\n")
        for prefix, count, success in results:
            f.write(f"  {prefix}: {count:,} {'OK' if success else 'FAILED'}\n")


if __name__ == "__main__":
    asyncio.run(main())
