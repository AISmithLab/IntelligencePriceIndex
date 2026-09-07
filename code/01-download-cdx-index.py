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

THE 2026-09-06 REFRESH FAILED AND THIS IS THE FIX. That run marked all 26
prefixes FAILED: 14 never got a page count at all and the 12 that started
managed 927 of 6,384 pages (14.5%) before dying, after 499 rate-limit hits. Two
defects, both now repaired:

  * A 429 is per-IP, not per-prefix, but the backoff was per-prefix -- one worker
    slept while the other two kept hammering, so the limiter never let go.
    `Throttle` is now global: any 429 pauses every worker, and all requests pace
    through one token bucket.
  * There was no resume. The loop opened each prefix with mode="w" and restarted
    from page 0, so a run that died at 15% lost all 15%. Progress is now
    checkpointed per page in `<prefix>.progress.json` (pages and BYTES written),
    and a resume truncates to the last complete page before appending.

Resume has one subtlety worth stating: CDX page boundaries are only stable for a
fixed query, and --to defaults to *now*, which moves between runs. So a resume
adopts the checkpointed --to rather than today's clock, and says so. Passing an
explicit --to overrides that and restarts any prefix whose window disagrees.

Usage:
    python3 01-download-cdx-index.py                    # 2025-01-01 -> now, into raw-2025/
    python3 01-download-cdx-index.py --from 20110101 --to 20261231 --out raw
    python3 01-download-cdx-index.py --prefixes qxz     # a subset
    python3 01-download-cdx-index.py                    # again: resumes where it died
"""

import argparse
import asyncio
import aiohttp
import json
import random
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
# The 2026-09-06 run used 3 workers, a 0.5s per-page sleep and per-prefix backoff,
# and took 499 rate-limit hits. Two workers paced through one global token bucket
# is slower per request and far faster to completion, because it does not spend
# the run in backoff.
MAX_CONCURRENT = 2
MIN_INTERVAL = 0.75   # seconds between ANY two requests, globally
RETRY_LIMIT = 8       # a long pull will legitimately meet 429s; do not give up early
RETRY_BACKOFF = 10    # seconds base backoff, doubled per attempt, jittered
MAX_BACKOFF = 300


class Throttle:
    """One global pacer shared by every worker.

    A 429 from the CDX API is a statement about our IP, not about the prefix that
    happened to receive it, so `penalise` stops the whole run rather than one
    task. Without this the other workers keep the limiter angry and no amount of
    per-task sleeping recovers.
    """

    def __init__(self, min_interval):
        self.min_interval = min_interval
        self._lock = asyncio.Lock()
        self._next = 0.0
        self._cooldown_until = 0.0
        self.hits = 0

    async def acquire(self):
        loop = asyncio.get_running_loop()
        async with self._lock:
            start = max(loop.time(), self._next, self._cooldown_until)
            self._next = start + self.min_interval
        delay = start - loop.time()
        if delay > 0:
            await asyncio.sleep(delay)

    async def penalise(self, seconds):
        loop = asyncio.get_running_loop()
        async with self._lock:
            self.hits += 1
            self._cooldown_until = max(self._cooldown_until, loop.time() + seconds)


THROTTLE = None  # built inside main(), where a loop exists


def describe(exc):
    """`asyncio.TimeoutError` stringifies to the empty string, which made the
    2026-09-07 log read `page count: ; retrying`. Always name the class."""
    return f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__


def backoff(attempt):
    """Exponential with jitter, so parallel retries do not resynchronise."""
    return min(MAX_BACKOFF, RETRY_BACKOFF * (2 ** attempt)) * (0.5 + random.random())


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
        await THROTTLE.acquire()
        try:
            async with session.get(CDX_API, params=params, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return int(text.strip())
                elif resp.status in (429, 503):
                    wait = backoff(attempt)
                    print(f"  [{prefix}] page count: rate limited (HTTP {resp.status}); "
                          f"pausing every worker {wait:.0f}s", flush=True)
                    await THROTTLE.penalise(wait)
                else:
                    print(f"  [{prefix}] page count: unexpected status {resp.status}", flush=True)
                    await THROTTLE.penalise(RETRY_BACKOFF)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            wait = backoff(attempt)
            print(f"  [{prefix}] page count: {describe(e)}; retrying in {wait:.0f}s", flush=True)
            await THROTTLE.penalise(wait)
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
        await THROTTLE.acquire()
        try:
            async with session.get(CDX_API, params=params, timeout=aiohttp.ClientTimeout(total=300)) as resp:
                if resp.status == 200:
                    return await resp.text()
                elif resp.status in (429, 503):
                    wait = backoff(attempt)
                    print(f"  [{prefix}] page {page}/{num_pages}: rate limited; "
                          f"pausing every worker {wait:.0f}s", flush=True)
                    await THROTTLE.penalise(wait)
                else:
                    print(f"  [{prefix}] page {page}/{num_pages}: HTTP {resp.status}", flush=True)
                    await THROTTLE.penalise(RETRY_BACKOFF)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            wait = backoff(attempt)
            print(f"  [{prefix}] page {page}/{num_pages}: {describe(e)}; "
                  f"retrying in {wait:.0f}s", flush=True)
            await THROTTLE.penalise(wait)
    return None


def progress_path(prefix):
    return RAW_DIR / f"{prefix}.progress.json"


def read_progress(prefix):
    path = progress_path(prefix)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def write_progress(prefix, num_pages, pages_done, bytes_done, records):
    """Checkpoint after every page.

    `bytes_done` is what makes the resume exact: on restart the file is truncated
    to that offset, so a page that was half-written when the process died is
    discarded rather than duplicated or left torn.
    """
    progress_path(prefix).write_text(json.dumps({
        "window": [FROM_TS, TO_TS],
        "num_pages": num_pages,
        "pages_done": pages_done,
        "bytes_done": bytes_done,
        "records": records,
    }))


async def download_prefix(session, semaphore, prefix):
    """Download all CDX pages for one letter prefix, resuming where a prior run died."""
    async with semaphore:
        outfile = RAW_DIR / f"{prefix}.tsv"

        prog = read_progress(prefix)
        checkpointed = prog if prog and prog.get("window") == [FROM_TS, TO_TS] else None

        num_pages = await get_num_pages(session, prefix)
        if num_pages is None:
            # Do not let one flaky request throw away a checkpoint. The page count
            # is fixed for a fixed query, so a checkpoint from this same window
            # already carries it.
            if checkpointed:
                num_pages = checkpointed["num_pages"]
                print(f"[{prefix}] page count unavailable; taking {num_pages} "
                      f"from the checkpoint", flush=True)
            else:
                print(f"[{prefix}] FAILED to get page count", flush=True)
                return prefix, 0, False

        if num_pages == 0:
            print(f"[{prefix}] No pages found", flush=True)
            outfile.touch()
            write_progress(prefix, 0, 0, 0, 0)
            return prefix, 0, True

        # Resume only against a checkpoint from the SAME query. CDX page
        # boundaries shift when the window moves, so a stale checkpoint would
        # splice two different paginations together.
        start_page = total_lines = bytes_done = 0
        if checkpointed and checkpointed.get("num_pages") == num_pages:
            start_page = min(checkpointed.get("pages_done", 0), num_pages)
            total_lines = checkpointed.get("records", 0)
            bytes_done = checkpointed.get("bytes_done", 0)
        elif prog:
            print(f"[{prefix}] checkpoint is for a different query, restarting", flush=True)

        if start_page >= num_pages:
            print(f"[{prefix}] already complete: {total_lines:,} records", flush=True)
            return prefix, total_lines, True

        if start_page:
            print(f"[{prefix}] resuming at page {start_page}/{num_pages} "
                  f"({total_lines:,} records already)", flush=True)
        else:
            print(f"[{prefix}] {num_pages} pages to download", flush=True)

        # Truncate to the last complete page, then append.
        with open(outfile, "a+b") as f:
            f.truncate(bytes_done)
            f.seek(bytes_done)

            for page in range(start_page, num_pages):
                data = await download_page(session, prefix, page, num_pages)
                if data is None:
                    # The checkpoint is already on disk for every page before this
                    # one, so re-running the step picks up here rather than at 0.
                    print(f"[{prefix}] FAILED on page {page}/{num_pages} "
                          f"-- {page - start_page} pages kept this run", flush=True)
                    return prefix, total_lines, False

                lines = data.strip()
                if lines:
                    payload = (lines + "\n").encode()
                    f.write(payload)
                    f.flush()
                    bytes_done += len(payload)
                    total_lines += lines.count("\n") + 1

                write_progress(prefix, num_pages, page + 1, bytes_done, total_lines)

                if (page + 1) % 50 == 0 or page == num_pages - 1:
                    print(f"  [{prefix}] {page+1}/{num_pages} pages "
                          f"({total_lines:,} records)", flush=True)

        print(f"[{prefix}] Complete: {total_lines:,} records", flush=True)
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
    RAW_DIR = BASE_DIR / "data" / "cdx-index" / args.out
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if args.ts_to:
        TO_TS = args.ts_to.ljust(14, "0")
    else:
        # A resume must reuse the window it checkpointed against, not today's
        # clock -- otherwise CDX repaginates and every prefix restarts at 0,
        # which is exactly the failure this rewrite exists to prevent. Adopt the
        # window of the newest unfinished checkpoint, if there is one.
        TO_TS = time.strftime("%Y%m%d%H%M%S", time.gmtime())
        best = None
        for path in RAW_DIR.glob("*.progress.json"):
            try:
                d = json.loads(path.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            if d.get("pages_done", 0) < d.get("num_pages", 0) and d.get("window", [None, None])[0] == FROM_TS:
                cand = d["window"][1]
                if best is None or cand > best:
                    best = cand
        if best:
            TO_TS = best
            print(f"Resuming an unfinished pull: adopting --to {TO_TS} from its checkpoint.\n"
                  f"Pass --to explicitly to start a fresh window instead.")
    return list(args.prefixes)


async def main():
    prefixes = parse_args()
    print(f"Window {FROM_TS} -> {TO_TS}  into data/cdx-index/{RAW_DIR.name}/")
    print(f"Prefixes: {''.join(prefixes)}")

    global THROTTLE
    THROTTLE = Throttle(MIN_INTERVAL)
    print(f"Pacing: {MAX_CONCURRENT} workers through one bucket at "
          f"{MIN_INTERVAL}s/request")

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
    print(f"Rate-limit pauses: {THROTTLE.hits}")
    if failed:
        print(f"FAILED prefixes: {', '.join(failed)}")
        print(f"Re-run to RESUME (checkpoints are on disk, no work is repeated):")
        print(f"  python3 {sys.argv[0]} --from {FROM_TS} --to {TO_TS} "
              f"--out {RAW_DIR.name} --prefixes {''.join(failed)}")
    else:
        print("All prefixes downloaded successfully!")

    # Write summary file
    summary_path = RAW_DIR / "download-summary.txt"
    with open(summary_path, "w") as f:
        f.write(f"Download completed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Window: {FROM_TS} -> {TO_TS}\n")
        f.write(f"Total records: {total_records:,}\n")
        f.write(f"Failed prefixes: {', '.join(failed) if failed else 'none'}\n")
        f.write(f"Rate-limit pauses: {THROTTLE.hits}\n")
        for prefix, count, success in results:
            f.write(f"  {prefix}: {count:,} {'OK' if success else 'FAILED'}\n")


if __name__ == "__main__":
    asyncio.run(main())
