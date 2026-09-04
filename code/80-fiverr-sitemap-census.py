#!/usr/bin/env python3
"""
Step 80: which panel gigs are STILL LISTED on Fiverr today.

WHY THIS EXISTS. `code/39-status-ledger.py` streamed all 60.0M raw CDX rows and found
`n_404 = 0` across 509,339 in-window captures: the Wayback archive stops re-requesting
a delisted URL rather than recording its death, so EXIT IS UNMEASURABLE FROM THE
ARCHIVE. That was logged as impossible. It is not -- it just cannot come from Wayback.

Fiverr publishes its live gig inventory as sitemaps, listed in its own robots.txt and
served without the PerimeterX wall that 403s every gig PAGE. Eight requests give the
set of gigs that exist right now, and joining that to the panel gives survival.

WHAT THIS DOES NOT GIVE. Prices. No sitemap carries one, and gig pages are hard-blocked
(measured 2026-09-04: 15/15 403 at 3s spacing with browser headers; the homepage 403s on
the first request, so it is not a rate limit). This CANNOT extend the price index. It
measures existence, nothing else.

A gig absent from the sitemap is not proven dead -- it may be delisted, paused, unindexed
or simply rotated out of a sitemap that is capped. Read it as "still publicly listed",
and as a LOWER bound on survival.

Output: data/fiverr-live/gig-urls-YYYY-MM-DD.txt.gz   (the raw live set)
        runs/live-collection/survival-YYYY-MM-DD.md   (the join to the panel)
"""

import gzip
import re
import time
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUTDIR = BASE_DIR / "data" / "fiverr-live"
RUNDIR = BASE_DIR / "runs" / "live-collection"
INDEX = "https://www.fiverr.com/sitemap_gigs.xml.gz"
PRICES = BASE_DIR / "data" / "pilot" / "balanced-prices.csv"
UA = "Mozilla/5.0 (X11; Linux x86_64) research contact datasmithlab@gmail.com"
PAUSE = 2.0          # eight requests total; politeness costs nothing here


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        raw = r.read()
    return gzip.decompress(raw).decode("utf-8", "replace") if raw[:2] == b"\x1f\x8b" \
        else raw.decode("utf-8", "replace")


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    RUNDIR.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()

    subs = re.findall(r"<loc>([^<]+)</loc>", get(INDEX))
    print(f"{len(subs)} sub-sitemaps")
    live = set()
    for i, s in enumerate(subs, 1):
        time.sleep(PAUSE)
        n0 = len(live)
        live |= set(re.findall(r"<loc>https://www\.fiverr\.com/([^<]+)</loc>", get(s)))
        print(f"  {i}/{len(subs)} {s.rsplit('/', 1)[-1]:24s} +{len(live)-n0:,}")

    urls = OUTDIR / f"gig-urls-{stamp}.txt.gz"
    with gzip.open(urls, "wt") as f:
        f.write("\n".join(sorted(live)))
    print(f"\n{len(live):,} live gig URLs -> {urls.relative_to(BASE_DIR)}")

    d = pd.read_csv(PRICES, usecols=["seller", "slug", "year"])
    d["gid"] = d.seller + "/" + d.slug
    p = d.groupby("gid").year.max().to_frame("last_year")
    p["alive"] = p.index.isin(live)

    t = p.groupby("last_year").alive.agg(gigs="size", alive="sum", survival="mean")
    lines = [f"# Panel gigs still listed on Fiverr, {stamp}", "",
             f"Live set: **{len(live):,}** gig URLs from {len(subs)} sitemaps "
             f"(robots.txt-listed, served; gig PAGES are 403 behind PerimeterX).", "",
             f"Panel: **{len(p):,}** gigs. Still listed: **{p.alive.sum():,}** "
             f"({p.alive.mean():.1%}).", "",
             "Absence is *not listed*, which is a lower bound on survival -- a gig may be "
             "paused, unindexed or rotated out rather than dead.", "",
             "| last seen in panel | gigs | still listed | survival |",
             "|---|---:|---:|---:|"]
    for y, r in t.iterrows():
        lines.append(f"| {y} | {r.gigs:,.0f} | {r.alive:,.0f} | {r.survival:.1%} |")
    md = RUNDIR / f"survival-{stamp}.md"
    md.write_text("\n".join(lines) + "\n")
    print(f"panel {len(p):,} gigs, {p.alive.sum():,} still listed ({p.alive.mean():.1%})")
    print(f"-> {md.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
