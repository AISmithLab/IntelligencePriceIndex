#!/usr/bin/env python3
"""
Download HTML snapshots from the Wayback Machine.

Reads a manifest TSV, constructs Wayback URLs, downloads raw HTML.
Handles: rate limiting, retries, resume from interruption, progress logging.

Usage:
    python 08-download-html.py [--manifest PATH] [--concurrency N] [--max-rate N]

Input:  data/pilot/pilot-500-manifest.tsv (default)
Output: data/pilot/html/<username>/<YYYYMMDD>_<slug>.html
        data/pilot/download-log.tsv
"""

import argparse
import asyncio
import aiohttp
import gzip
import time
import csv
import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = BASE_DIR / "data" / "pilot" / "pilot-500-manifest.tsv"
DEFAULT_HTML_DIR = BASE_DIR / "data" / "pilot" / "html"
DEFAULT_LOG = BASE_DIR / "data" / "pilot" / "download-log.tsv"
DEFAULT_CHECKPOINT = BASE_DIR / "data" / "pilot" / "download-checkpoint.txt"

WAYBACK_TPL = "https://web.archive.org/web/{timestamp}id_/{url}"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument("--html-dir", type=Path, default=DEFAULT_HTML_DIR)
    p.add_argument("--log", type=Path, default=DEFAULT_LOG)
    p.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    p.add_argument("--concurrency", type=int, default=10)
    p.add_argument("--max-rate", type=float, default=12.0,
                   help="Max requests per second")
    p.add_argument("--max-retries", type=int, default=3)
    p.add_argument("--gzip", action="store_true",
                   help="Store pages gzipped as <name>.html.gz. Measured 5.0x on "
                        "this corpus (22 GB -> ~4.4 GB per 15k pages); "
                        "09-extract-prices.py reads both forms transparently.")
    p.add_argument("--chunk", type=int, default=5000,
                   help="Schedule this many downloads at a time instead of "
                        "creating one coroutine per manifest row up front.")
    p.add_argument("--limit", type=int, default=0,
                   help="Stop after N new downloads (0 = no limit). For pilots.")
    return p.parse_args()


def extract_seller_slug(url):
    """Extract (seller, slug) from a Fiverr URL."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    elif len(parts) == 1:
        return parts[0], "unknown"
    return "unknown", "unknown"


def build_output_path(html_dir, seller, slug, timestamp, use_gzip=False):
    """Build output path: html/<seller>/<YYYYMMDD>_<slug>.html[.gz]

    Does NOT create the directory — with ~90k gigs this is called once per
    manifest row during the existence check, and mkdir on every row is a
    measurable cost. The writer creates the parent when it actually writes.
    """
    date = timestamp[:8]
    return html_dir / seller / f"{date}_{slug}.html{'.gz' if use_gzip else ''}"


def existing_path(html_dir, seller, slug, timestamp):
    """Return an already-downloaded page for this snapshot in either storage
    form, or None. Lets a gzipped run reuse the plain files from earlier runs
    instead of re-fetching 15,150 pages that are already on disk."""
    for gz in (False, True):
        p = build_output_path(html_dir, seller, slug, timestamp, gz)
        if p.exists() and p.stat().st_size > 0:
            return p
    return None


def load_manifest(manifest_path):
    """Load manifest, return list of (timestamp, original_url) tuples."""
    entries = []
    with open(manifest_path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            entries.append((row["timestamp"], row["original"]))
    return entries


def load_checkpoint(checkpoint_path):
    """Load set of already-downloaded (timestamp, url) pairs."""
    done = set()
    if checkpoint_path.exists():
        with open(checkpoint_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    done.add(line)
    return done


class RateLimiter:
    """Token bucket rate limiter."""
    def __init__(self, rate):
        self.rate = rate
        self.tokens = rate
        self.last = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last
            self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
            self.last = now
            if self.tokens < 1:
                wait = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait)
                self.tokens = 0
            else:
                self.tokens -= 1


async def download_one(session, timestamp, url, html_dir, rate_limiter,
                       max_retries, log_file, checkpoint_file, stats,
                       use_gzip=False):
    """Download a single Wayback snapshot."""
    seller, slug = extract_seller_slug(url)

    # Skip if already on disk in either storage form
    if existing_path(html_dir, seller, slug, timestamp) is not None:
        stats["skipped"] += 1
        return

    out_path = build_output_path(html_dir, seller, slug, timestamp, use_gzip)

    wayback_url = WAYBACK_TPL.format(timestamp=timestamp, url=url)

    for attempt in range(max_retries):
        await rate_limiter.acquire()
        try:
            async with session.get(wayback_url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    if use_gzip:
                        with gzip.open(out_path, "wb", compresslevel=6) as f:
                            f.write(content)
                    else:
                        with open(out_path, "wb") as f:
                            f.write(content)

                    stats["ok"] += 1
                    size = len(content)

                    # Log
                    log_file.write(f"{timestamp}\t{url}\t200\t{out_path}\t{size}\n")
                    log_file.flush()

                    # Checkpoint
                    checkpoint_file.write(f"{timestamp}\t{url}\n")
                    checkpoint_file.flush()
                    return

                elif resp.status == 429 or resp.status >= 500:
                    wait = 2 ** (attempt + 1)
                    stats["retries"] += 1
                    await asyncio.sleep(wait)
                else:
                    # 404, 403, etc. — don't retry
                    stats["failed"] += 1
                    log_file.write(f"{timestamp}\t{url}\t{resp.status}\t\t0\n")
                    log_file.flush()
                    return

        except (aiohttp.ClientError, asyncio.TimeoutError):
            wait = 2 ** (attempt + 1)
            stats["retries"] += 1
            await asyncio.sleep(wait)

    # Exhausted retries
    stats["failed"] += 1
    log_file.write(f"{timestamp}\t{url}\tfail\t\t0\n")
    log_file.flush()


async def main_async(args):
    entries = load_manifest(args.manifest)
    done = load_checkpoint(args.checkpoint)

    # Filter out already done
    todo = [(ts, url) for ts, url in entries if f"{ts}\t{url}" not in done]
    n_pending = len(todo)
    if args.limit:
        todo = todo[:args.limit]

    print(f"Manifest:    {len(entries):,} snapshots")
    print(f"Already done:{len(entries) - n_pending:,}")
    print(f"To download: {len(todo):,}" +
          (f" (--limit of {n_pending:,} pending)" if args.limit else ""))
    print(f"Storage:     {'gzip' if args.gzip else 'plain'}")
    print(f"Concurrency: {args.concurrency}")
    print(f"Rate limit:  {args.max_rate} req/s")
    print()

    if not todo:
        print("Nothing to download!")
        return

    args.html_dir.mkdir(parents=True, exist_ok=True)

    stats = {"ok": 0, "failed": 0, "skipped": 0, "retries": 0}
    rate_limiter = RateLimiter(args.max_rate)
    start_time = time.time()

    connector = aiohttp.TCPConnector(limit=args.concurrency, force_close=True)

    with open(args.log, "a") as log_file, \
         open(args.checkpoint, "a") as checkpoint_file:

        # Write log header if new file
        if args.log.stat().st_size == 0 if args.log.exists() else True:
            log_file.write("timestamp\turl\tstatus\tfile_path\tsize\n")

        async with aiohttp.ClientSession(connector=connector) as session:
            sem = asyncio.Semaphore(args.concurrency)

            async def bounded_download(ts, url):
                async with sem:
                    await download_one(session, ts, url, args.html_dir,
                                       rate_limiter, args.max_retries,
                                       log_file, checkpoint_file, stats,
                                       use_gzip=args.gzip)

                # Progress update
                total_done = stats["ok"] + stats["failed"] + stats["skipped"]
                if total_done % 500 == 0:
                    elapsed = time.time() - start_time
                    rate = total_done / elapsed if elapsed > 0 else 0
                    pct = total_done / len(todo) * 100
                    print(f"  [{pct:5.1f}%] {total_done:,}/{len(todo):,} "
                          f"| ok={stats['ok']:,} fail={stats['failed']:,} "
                          f"skip={stats['skipped']:,} "
                          f"| {rate:.1f}/s | {elapsed:.0f}s")

            # Schedule in chunks. One coroutine per manifest row up front is
            # fine at 15k rows and not at 100k on a 5 GB box.
            for i in range(0, len(todo), args.chunk):
                batch = todo[i:i + args.chunk]
                await asyncio.gather(*(bounded_download(ts, url)
                                       for ts, url in batch))

    elapsed = time.time() - start_time
    print()
    print("=" * 50)
    print(f"DONE in {elapsed:.0f}s ({elapsed/60:.1f}min)")
    print(f"  OK:      {stats['ok']:,}")
    print(f"  Failed:  {stats['failed']:,}")
    print(f"  Skipped: {stats['skipped']:,}")
    print(f"  Retries: {stats['retries']:,}")

    # Check disk usage (both storage forms)
    total_size = sum(f.stat().st_size for f in args.html_dir.rglob("*.html*"))
    print(f"  Disk:    {total_size / 1024 / 1024 / 1024:.2f} GB")
    if stats["ok"]:
        print(f"  Rate:    {stats['ok'] / elapsed:.2f} pages/s sustained")


def main():
    args = parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
