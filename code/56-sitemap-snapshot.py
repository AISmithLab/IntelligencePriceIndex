#!/usr/bin/env python3
"""
Step 56: Snapshot Fiverr's published gig sitemap.

Discovered 2026-08-19 while auditing collection routes for 2025-26. Fiverr
publishes `sitemap_gigs.xml.gz` (a sitemap index over 7 sub-sitemaps, ~43.5k
gig URLs each, ~305k total), regenerated daily, and -- unlike the gig pages
themselves -- it is NOT behind the PerimeterX wall. A plain GET returns 200.

What this buys that the archive cannot:
  - the LIVE gig universe on the date of the snapshot
  - ENTRY  = URLs present today, absent in an earlier snapshot
  - EXIT   = URLs present earlier, absent today. `39-status-ledger.py` proved
             exit is unmeasurable from Wayback (n_404 = 0 across 509,339
             in-window captures); this is the only route to it.
  - a target list for any live price crawl, so we crawl listed gigs
  - an attrition check on the archive panel: which 2024 panel gigs still exist

What it does NOT buy: prices. The sitemap carries <loc> only -- no <lastmod>,
no metadata. Prices need the page, and the page 403s.

Snapshots are append-only and dated. A day not snapshotted is lost forever,
which is why this runs before the crawl decision is settled.

Output: data/sitemap/gigs-YYYY-MM-DD.txt.gz   (sorted, deduped seller/slug)
        data/sitemap/manifest.tsv             (date, n_urls, bytes, sha256)
"""

import gzip
import hashlib
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "data" / "sitemap"
MANIFEST = OUT_DIR / "manifest.tsv"
INDEX_URL = "https://www.fiverr.com/sitemap_gigs.xml.gz"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")
POLITE_DELAY = 5.0  # seconds between sub-sitemap fetches


def fetch(url, retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:
            wait = 10 * (2 ** attempt)
            print(f"  fetch failed ({e}); retry in {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"gave up on {url}")


def gig_key(url):
    """https://www.fiverr.com/seller/slug -> seller/slug, else None."""
    u = re.sub(r"^https?://(www\.)?fiverr\.com/", "", url).split("?")[0].strip("/")
    parts = u.split("/")
    if len(parts) == 2 and parts[0] and parts[1]:
        return u
    return None


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out_path = OUT_DIR / f"gigs-{today}.txt.gz"
    if out_path.exists():
        print(f"{out_path} already exists; nothing to do.")
        return

    print(f"Fetching sitemap index: {INDEX_URL}")
    idx = gzip.decompress(fetch(INDEX_URL)).decode("utf-8", "replace")
    subs = re.findall(r"<loc>(.*?)</loc>", idx)
    print(f"  {len(subs)} sub-sitemaps")

    keys = set()
    for i, sub in enumerate(subs, 1):
        raw = fetch(sub)
        xml = gzip.decompress(raw).decode("utf-8", "replace")
        locs = re.findall(r"<loc>(.*?)</loc>", xml)
        got = sum(1 for l in locs if (k := gig_key(l)) and not keys.add(k))
        print(f"  [{i}/{len(subs)}] {sub.rsplit('/', 1)[-1]}: "
              f"{len(locs)} locs, {len(keys)} distinct gigs so far")
        if i < len(subs):
            time.sleep(POLITE_DELAY)

    body = ("\n".join(sorted(keys)) + "\n").encode()
    with gzip.open(out_path, "wb") as f:
        f.write(body)

    digest = hashlib.sha256(body).hexdigest()
    new = not MANIFEST.exists()
    with open(MANIFEST, "a") as f:
        if new:
            f.write("date\tn_gigs\tbytes_gz\tsha256\n")
        f.write(f"{today}\t{len(keys)}\t{out_path.stat().st_size}\t{digest}\n")

    print(f"\nWrote {out_path} -- {len(keys):,} distinct gig URLs "
          f"({out_path.stat().st_size / 1e6:.1f} MB gz)")


if __name__ == "__main__":
    main()
