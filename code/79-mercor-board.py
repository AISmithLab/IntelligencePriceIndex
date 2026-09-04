#!/usr/bin/env python3
"""
Step 79: a dated snapshot of Mercor's open job board.

WHY THIS IS ONE REQUEST AND NOT A CRAWL. `work.mercor.com/jobs` is a Next.js page
that server-renders EVERY open listing into `__NEXT_DATA__`. One GET returns the
whole cross-section -- rates, capacity, timestamps -- so there is nothing to crawl
and no per-listing fetching to rate-limit. `work.mercor.com/robots.txt` allows
`/jobs/`; `/apply/`, `/api/`, `/interview/` are disallowed and are never touched.

WHAT THIS IS NOT. Mercor listings are EMPLOYER-POSTED HOURLY RATE BANDS for contract
roles, not seller-posted fixed prices for deliverables. They are not comparable to
the Fiverr gig prices the IPI is built on and must not be spliced into that index.
This is a separate, demand-side series on AI-adjacent expert labour.

A snapshot is a cross-section. The PANEL comes from running this repeatedly: the
`version` field increments on a genuine edit, so re-running daily separates a
reprice from a re-crawl, and a listing leaving the board is an exit.

Output: data/mercor/board-YYYY-MM-DD.csv   (one row per open listing)
        data/mercor/board-latest.csv       (a copy, for scripts that want one path)
"""

import gzip
import json
import re
import sys
import urllib.request
from datetime import date, timezone, datetime
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUTDIR = BASE_DIR / "data" / "mercor"
BOARD = "https://work.mercor.com/jobs"
UA = "Mozilla/5.0 (X11; Linux x86_64) research contact datasmithlab@gmail.com"

# the fields worth keeping; the payload carries ~51 and most are UI state
KEEP = ["listingId", "uid", "version", "title", "listingDomain", "companyName",
        "rateMin", "rateMax", "payRateFrequency", "commitment", "hoursPerWeek",
        "status", "createdAt", "postedAt", "location", "workArrangement",
        "remainingSlots", "suppliedSlots", "recentCandidatesCount",
        "isPrivate", "listingType", "offersEquity"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "replace")


def listings(html):
    """Every dict in the dehydrated react-query cache that looks like a listing."""
    m = re.search(r'__NEXT_DATA__[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise RuntimeError("no __NEXT_DATA__ — the page shape changed, stop and look")
    state = json.loads(m.group(1))["props"]["pageProps"]["dehydratedState"]

    def walk(o):
        if isinstance(o, dict):
            if "listingId" in o and "rateMin" in o:
                yield o
            for v in o.values():
                yield from walk(v)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v)

    seen, out = set(), []
    for d in walk(state):
        if d["listingId"] not in seen:
            seen.add(d["listingId"])
            out.append(d)
    return out


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    rows = listings(fetch(BOARD))
    if not rows:
        sys.exit("no listings parsed — refusing to write an empty snapshot")

    df = pd.DataFrame([{k: d.get(k) for k in KEEP} for d in rows])
    df.insert(0, "collected_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))

    # one derived column, because the board mixes hourly / yearly / per-task and a
    # naive mean over rateMin would be meaningless
    df["rate_mid"] = (df.rateMin + df.rateMax) / 2
    df.loc[df.payRateFrequency != "hourly", "rate_mid"] = pd.NA

    out = OUTDIR / f"board-{stamp}.csv"
    df.to_csv(out, index=False)
    df.to_csv(OUTDIR / "board-latest.csv", index=False)

    hourly = df[df.payRateFrequency == "hourly"]
    print(f"{len(df)} open listings -> {out.relative_to(BASE_DIR)}")
    print(f"  by pay frequency: {df.payRateFrequency.value_counts().to_dict()}")
    print(f"  hourly: {len(hourly)}, median band "
          f"${hourly.rateMin.median():,.0f}-${hourly.rateMax.median():,.0f}, "
          f"median midpoint ${hourly.rate_mid.median():,.0f}")
    print(f"  domains: {df.listingDomain.notna().sum()}/{len(df)} labelled, "
          f"top {df.listingDomain.value_counts().head(3).to_dict()}")
    print(f"  capacity: remainingSlots on {df.remainingSlots.notna().sum()}/{len(df)}, "
          f"total open slots {df.remainingSlots.sum():,.0f}")


if __name__ == "__main__":
    main()
