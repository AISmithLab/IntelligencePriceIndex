#!/usr/bin/env python3
"""
Step 73: What does a candidate manifest actually cost to crawl, and how much of
it is already on disk?

Every collection decision so far has been argued in gigs, but the thing that is
spent is Wayback requests, wall-clock and disk. This converts a manifest into
those three, using constants MEASURED on the two completed crawls rather than
guessed:

  balanced (36-2, gzipped)   298,009 rows -> 291,997 captured in 10h34m
                             = 98.0% hit rate, 7.83 rows/s, 128 KB/page
  expanded (38-8, plain)     79,191 rows  -> 67,376 captured in 2h34m
                             = 7.28 rows/s, 602 KB/page

The rate is set by 08-download-html.py's `--max-rate 10` politeness cap, not by
bandwidth, so it does not improve with more concurrency. The disk figure is the
reason `--gzip` is not optional at this scale: the same crawl is 4.7x larger
without it, and there is not room.

WHAT IS ALREADY ON DISK. `08-download-html.py` skips a manifest row when the
exact file `<html-dir>/<seller>/<YYYYMMDD>_<slug>.html[.gz]` exists, so the real
cost of a candidate is the rows with no such file -- not the row count, and not
the count of unseen gigs. A backfill into a domain already collected overlaps
heavily at the gig level while still costing a request for every gig-quarter the
old manifest did not select. This resolves it at row granularity by indexing the
three existing html trees and testing each row against all of them.

Usage:
    python 73-collection-cost.py data/pilot/<candidate>-manifest.tsv [...]

Output: runs/uncollected-headroom/collection-cost.md
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTDIR = BASE_DIR / "runs" / "uncollected-headroom"
PILOT = BASE_DIR / "data" / "pilot"

# Every html tree the pipeline has written into.
HTML_DIRS = ["html-balanced", "html-recent", "html"]

HIT_RATE = 0.980            # captured / manifest rows, measured on balanced
ROWS_PER_SEC = 7.83         # measured end-to-end, includes retry passes
KB_PER_PAGE_GZ = 128        # measured: 36 GB / 293,943 gzipped pages


def index_html(html_dir):
    """Set of `<seller>/<YYYYMMDD>_<slug>` keys already on disk under html_dir.

    Mirrors 08-download-html.py's build_output_path, minus the extension, so a
    gzipped and a plain capture of the same page collide as they should.
    """
    keys = set()
    if not html_dir.is_dir():
        return keys
    for seller in html_dir.iterdir():
        if not seller.is_dir():
            continue
        sn = seller.name
        for f in seller.iterdir():
            n = f.name
            for ext in (".html.gz", ".html"):
                if n.endswith(ext):
                    keys.add(f"{sn}/{n[:-len(ext)]}")
                    break
    return keys


def summarise(path, have):
    """Rows, distinct gigs, and per-label (total, still-to-fetch) counts.

    A row is already satisfied if its `<seller>/<date>_<slug>` key exists in any
    html tree; `have` is the union of the three.
    """
    rows = new_rows = 0
    cats, cats_new = Counter(), Counter()
    gigs, gigs_new = set(), set()
    with open(path) as f:
        head = f.readline().rstrip("\n").split("\t")
        gi = head.index("gig_id") if "gig_id" in head else 0
        ti = head.index("timestamp") if "timestamp" in head else 1
        ci = head.index("category") if "category" in head else None
        for line in f:
            p = line.rstrip("\n").split("\t")
            rows += 1
            gid = p[gi]
            gigs.add(gid.lower())
            cat = p[ci] if ci is not None and len(p) > ci else None
            if cat:
                cats[cat] += 1
            seller, _, slug = gid.partition("/")
            if f"{seller}/{p[ti][:8]}_{slug}" not in have:
                new_rows += 1
                gigs_new.add(gid.lower())
                if cat:
                    cats_new[cat] += 1
    return rows, new_rows, gigs, gigs_new, cats, cats_new


def fmt_hours(sec):
    h, m = divmod(round(sec / 60), 60)
    return f"{h}h{m:02d}m"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifests", nargs="+", type=Path)
    ap.add_argument("--free-gb", type=float, default=None,
                    help="disk headroom to check against (default: measure /)")
    args = ap.parse_args()

    if args.free_gb is None:
        import shutil
        args.free_gb = shutil.disk_usage(BASE_DIR).free / 1e9

    print("Indexing pages already on disk...", file=sys.stderr)
    have, per_dir = set(), {}
    for htmldir in HTML_DIRS:
        k = index_html(PILOT / htmldir)
        per_dir[htmldir] = len(k)
        have |= k
        print(f"  {htmldir}: {len(k):,} pages", file=sys.stderr)
    print(f"  union: {len(have):,} pages", file=sys.stderr)

    L = ["# What a candidate collection costs", "",
         "Constants measured on the two completed crawls, not estimated: "
         f"**{HIT_RATE:.1%}** of manifest rows return a page, **{ROWS_PER_SEC} rows/s** "
         "end-to-end (set by `08-download-html.py --max-rate 10`, so it does not "
         f"improve with concurrency), **{KB_PER_PAGE_GZ} KB/page** gzipped.", "",
         f"Disk free: **{args.free_gb:.0f} GB**. Pages already on disk: "
         + ", ".join(f"`{d}` {n:,}" for d, n in per_dir.items())
         + f" ({len(have):,} distinct).", "",
         "`to fetch` counts only rows with no matching `<seller>/<date>_<slug>` file "
         "in any of those trees -- what the crawl would actually request. Disk and "
         "wall-clock are quoted on that, not on the row count.", "",
         "| manifest | rows | to fetch | gigs | new gigs | disk (gz) | wall-clock | fits? |",
         "|---|---:|---:|---:|---:|---:|---:|---|"]

    for path in args.manifests:
        rows, new_rows, gigs, gigs_new, cats, cats_new = summarise(path, have)
        pages = new_rows * HIT_RATE
        gb = pages * KB_PER_PAGE_GZ / 1e6
        sec = new_rows / ROWS_PER_SEC
        fits = "yes" if gb < args.free_gb - 10 else "**no**"
        L.append(f"| `{path.name}` | {rows:,} | **{new_rows:,}** | {len(gigs):,} | "
                 f"{len(gigs_new):,} | {gb:.1f} GB | {fmt_hours(sec)} | {fits} |")
        if cats:
            L += ["", f"**`{path.name}` by label** (rows / of those, still to fetch)", "",
                  "| label | rows | to fetch | disk (gz) | wall-clock |",
                  "|---|---:|---:|---:|---:|"]
            for c, n in cats.most_common():
                nn = cats_new[c]
                L.append(f"| {c} | {n:,} | {nn:,} | "
                         f"{nn * HIT_RATE * KB_PER_PAGE_GZ / 1e6:.1f} GB | "
                         f"{fmt_hours(nn / ROWS_PER_SEC)} |")
            L.append("")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "collection-cost.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
