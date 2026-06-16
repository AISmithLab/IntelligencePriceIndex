#!/usr/bin/env python3
"""
Step 1.2: Filter raw CDX records to gig pages only.

Keeps URLs with exactly 2 path segments (/<username>/<gig-slug>), status 200.
Excludes known non-gig prefixes.

Input:  data/cdx-index/raw/*.tsv
Output: data/cdx-index/gig-pages.tsv
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "cdx-index" / "raw"
OUTPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages.tsv"

# Known non-gig path prefixes (first segment)
NON_GIG_PREFIXES = {
    "categories", "search", "support", "pro", "logo-maker", "gigs",
    "business", "stores", "inbox", "manage_orders", "users", "join",
    "not_found", "pages", "help_and_education", "resources", "blog",
    "news", "terms_of_service", "privacy-policy", "intellectual-property",
    "seller_page", "buyer_requests", "settings", "start_selling",
    "content", "cp", "hc", "api", "partnerships", "careers",
    "trust_safety", "legal", "nonprofits", "learn", "guides",
    "community", "events", "podcast", "awards", "about", "press",
    "sitemap", "robots.txt", "favicon.ico", "sw.js",
    "sellerpage", "levels", "referral", "share", "go",
    "_next", "static", "assets", "bundles", "v2",
}

# Regex for valid gig slug: lowercase alphanumeric with hyphens, typically starts with a verb
# Usernames: alphanumeric with underscores, no hyphens typically
VALID_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]+$", re.IGNORECASE)


def is_gig_url(url):
    """Check if a URL is a Fiverr gig page (/<username>/<gig-slug>)."""
    try:
        parsed = urlparse(url if url.startswith("http") else "https://" + url)
        path = parsed.path.strip("/")
        if not path:
            return False

        segments = path.split("/")
        if len(segments) != 2:
            return False

        username, slug = segments

        # Exclude known non-gig first segments
        if username.lower() in NON_GIG_PREFIXES:
            return False

        # Basic validation
        if not username or not slug:
            return False

        # Usernames are typically 3-50 chars
        if len(username) < 2 or len(username) > 60:
            return False

        # Slugs should look like gig titles (contain hyphens for multi-word)
        # but some are short single words
        if len(slug) < 3:
            return False

        return True
    except Exception:
        return False


def main():
    header = "urlkey\ttimestamp\toriginal\tstatuscode\tdigest\tlength"
    total_in = 0
    total_out = 0

    raw_files = sorted(RAW_DIR.glob("*.tsv"))
    if not raw_files:
        print("ERROR: No raw CDX files found in", RAW_DIR)
        return

    print(f"Processing {len(raw_files)} raw CDX files...")

    with open(OUTPUT, "w") as fout:
        fout.write(header + "\n")

        for raw_file in raw_files:
            if raw_file.name == "download-summary.txt":
                continue
            file_in = 0
            file_out = 0
            with open(raw_file, "r") as fin:
                for line in fin:
                    line = line.strip()
                    if not line:
                        continue
                    total_in += 1
                    file_in += 1

                    parts = line.split(" ")
                    if len(parts) < 4:
                        continue

                    # CDX format: urlkey timestamp original statuscode digest length
                    # Fields are space-separated
                    urlkey = parts[0]
                    timestamp = parts[1]
                    original = parts[2]
                    statuscode = parts[3]
                    digest = parts[4] if len(parts) > 4 else ""
                    length = parts[5] if len(parts) > 5 else ""

                    # Filter: status 200 only
                    if statuscode != "200":
                        continue

                    # Filter: must be a gig URL
                    if not is_gig_url(original):
                        continue

                    fout.write(f"{urlkey}\t{timestamp}\t{original}\t{statuscode}\t{digest}\t{length}\n")
                    total_out += 1
                    file_out += 1

            print(f"  {raw_file.name}: {file_in:,} -> {file_out:,} gig records")

    print(f"\nTotal: {total_in:,} raw records -> {total_out:,} gig page records")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
