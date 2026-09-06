#!/usr/bin/env python3
"""
Step 81: what the 2025-2026 CDX refresh adds, and what is still uncollected.

WHY THIS STEP EXISTS. The panel's right edge is starved. `runs/uncollected-
headroom/supply-delta.md` shows matched gigs per adjacent quarter pair falling
off a cliff: design runs 6,420 across 2024Q3->2024Q4 and 301 across
2025Q4->2026Q1; coding 4,670 -> 59; writing 4,760 -> 50. Every 2025-2026 pair
is below every target the balanced manifest has ever used.

That is NOT a collection failure. It is the archive. Of all fiverr.com captures
timestamped 2025 or later in the March 2026 pull, 38% are HTTP 403 and only 19%
are 200 -- the same PerimeterX wall `80-fiverr-sitemap-census.py` measured
against live gig pages in 2026-09 was already turning the Wayback crawler away
in 2025. The supply is thin because the archive is thin.

TWO THINGS THE MARCH PULL STILL MISSED, and both are recoverable:

  1. LATE INGESTION. Wayback keeps absorbing captures long after the fact.
     Re-querying prefix `q` on 2026-09-06 returned 252 gig-shaped 200-status
     captures in 2025+ against the 212 the March pull saw -- **+19%**, invisible
     from inside the March files.
  2. THE RIGHT EDGE. March 2026 is where the old pull stops. The index holds 13
     records for 2026-03 and none after, so 2026Q2 and 2026Q3 are not thin,
     they are absent.

AND ONE THING THE COLLECTIONS MISSED. The balanced and expanded manifests quota
over seven domains and drop `uncategorized`, so 2025+ captures outside that set
were never downloaded even though they were indexed all along.

This step separates those three pools and emits one manifest for 08-download-
html.py. It downloads nothing itself.

Input:  data/cdx-index/raw/*.tsv        (all-time pull, 2026-03-22)
        data/cdx-index/raw-2025/*.tsv   (refresh, 01-download-cdx-index.py --from 20250101)
        data/pilot/*download-log.tsv    (what is already on disk)
Output: data/pilot/refresh-2025-manifest.tsv   (feeds 08-download-html.py)
        runs/cdx-refresh-2025/delta.md
"""

import importlib.util
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

CODE_DIR = Path(__file__).resolve().parent
BASE_DIR = CODE_DIR.parent
sys.path.insert(0, str(CODE_DIR))
from gigfilter import is_gig_id

RAW_OLD = BASE_DIR / "data" / "cdx-index" / "raw"
RAW_NEW = BASE_DIR / "data" / "cdx-index" / "raw-2025"
PILOT = BASE_DIR / "data" / "pilot"
OUTDIR = BASE_DIR / "runs" / "cdx-refresh-2025"
MANIFEST = PILOT / "refresh-2025-manifest.tsv"

# The refresh window. Anything earlier is already fully collected history.
FROM_MONTH = 202501

DOWNLOAD_LOGS = [
    PILOT / "download-log.tsv",
    PILOT / "expanded-download-log.tsv",
    PILOT / "balanced-download-log.tsv",
    PILOT / "balanced-pilot-log.tsv",
    BASE_DIR / "runs" / "expanded-collection" / "pilot-log.tsv",
]


def _load(stem):
    """Import a numbered pipeline step by path -- the names are not identifiers."""
    spec = importlib.util.spec_from_file_location(
        "m" + stem.split("-", 1)[0], CODE_DIR / stem)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Imported, not copied, so the refresh cannot drift from the pull it extends.
is_gig_url = _load("02-filter-gig-pages.py").is_gig_url
label_of = _load("72-reclassify-v2.py").label_of


def gid_of(urlkey):
    """`com,fiverr)/seller/slug` -> `seller/slug`, query and fragment dropped."""
    gid = urlkey.split(")/", 1)[1] if ")/" in urlkey else urlkey
    return gid.split("?", 1)[0].split("#", 1)[0].strip("/")


def scan_raw(directory, want):
    """Gig captures with status 200 at or after FROM_MONTH, keyed (gid, date).

    Value is the earliest timestamp seen for that gig-day, which is the one the
    download step should ask Wayback for.
    """
    out = {}
    stats = Counter()
    files = sorted(p for p in directory.glob("*.tsv"))
    if not files:
        print(f"  WARNING: no *.tsv in {directory}", file=sys.stderr)
    for f in files:
        with open(f, errors="replace") as fh:
            for line in fh:
                parts = line.split()
                if len(parts) < 4:
                    continue
                urlkey, ts, original, status = parts[0], parts[1], parts[2], parts[3]
                if len(ts) < 8 or not ts[:6].isdigit():
                    continue
                if int(ts[:6]) < FROM_MONTH:
                    continue
                stats["in_window"] += 1
                stats[f"status_{status}"] += 1
                if status != "200":
                    continue
                if not is_gig_url(original):
                    continue
                gid = gid_of(urlkey)
                if not is_gig_id(gid):
                    continue
                stats["gig_200"] += 1
                key = (gid, ts[:8])
                prev = out.get(key)
                if prev is None or ts < prev[0]:
                    out[key] = (ts, original)
        print(f"  {f.name}: {stats['in_window']:,} in window, "
              f"{stats['gig_200']:,} gig/200 so far", file=sys.stderr, flush=True)
    print(f"  -> {len(out):,} distinct {want} gig-days", file=sys.stderr)
    return out, stats


def downloaded_set():
    """(gid, YYYYMMDD) already fetched with HTTP 200 by any past collection."""
    got = set()
    for log in DOWNLOAD_LOGS:
        if not log.exists():
            print(f"  (absent) {log.relative_to(BASE_DIR)}", file=sys.stderr)
            continue
        n = 0
        with open(log, errors="replace") as fh:
            header = fh.readline()
            if not header.startswith("timestamp"):
                fh.seek(0)
            for line in fh:
                p = line.rstrip("\n").split("\t")
                if len(p) < 3 or p[2] != "200":
                    continue
                path = urlparse(p[1]).path.strip("/")
                if path.count("/") != 1:
                    continue
                got.add((path, p[0][:8]))
                n += 1
        print(f"  {log.name}: {n:,} successful rows", file=sys.stderr)
    return got


def quarter(month):
    y, m = divmod(int(month), 100)
    return f"{y}Q{(m - 1) // 3 + 1}"


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    print("Scanning the March 2026 all-time pull (2025+ slice)...", file=sys.stderr)
    old, old_stats = scan_raw(RAW_OLD, "March")
    print("Scanning the refresh...", file=sys.stderr)
    new, new_stats = scan_raw(RAW_NEW, "refresh")

    print("Reading download logs...", file=sys.stderr)
    have = downloaded_set()

    union = dict(old)
    union.update(new)                       # refresh wins on ties; same key either way
    added = {k: v for k, v in new.items() if k not in old}

    # Three disjoint pools over the union.
    rows = []
    pool = Counter()
    by_month = defaultdict(Counter)
    by_cat = Counter()
    for key in sorted(union):
        gid, day = key
        ts, original = union[key]
        cat = label_of(gid)[0]
        if key in have:
            pool["collected"] += 1
            continue
        pool["new_from_refresh" if key in added else "indexed_uncollected"] += 1
        by_month[ts[:6]][cat] += 1
        by_cat[cat] += 1
        rows.append((ts, original, cat, gid, ts[:6]))

    # Atomic. A step-08 pass may be reading this file right now: it loads the
    # manifest once at startup, so a rename swaps the file safely under it and
    # the NEXT pass picks up the larger set. A plain "w" would let a live pass
    # read a half-written manifest.
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    tmp = MANIFEST.with_suffix(".tsv.tmp")
    with open(tmp, "w") as fh:
        fh.write("timestamp\toriginal\tcategory\tgig_id\tmonth\n")
        for r in rows:
            fh.write("\t".join(r) + "\n")
    tmp.replace(MANIFEST)

    n_union, n_old, n_new = len(union), len(old), len(new)
    lines = [
        "# The 2025-2026 CDX refresh: what it adds, what is left to collect",
        "",
        f"Window: {FROM_MONTH} onward. Gig URLs with HTTP 200 only, deduplicated to "
        "one capture per gig per day.",
        "",
        "## Where the captures come from",
        "",
        "| pool | gig-days |",
        "|---|---:|",
        f"| in the March 2026 all-time pull | {n_old:,} |",
        f"| in the {len(list(RAW_NEW.glob('*.tsv')))}-prefix refresh | {n_new:,} |",
        f"| **union** | **{n_union:,}** |",
        f"| of which the refresh adds outright | {len(added):,} "
        f"({100 * len(added) / max(n_union, 1):.1f}%) |",
        "",
        "## What is already on disk, and what is not",
        "",
        "| pool | gig-days |",
        "|---|---:|",
        f"| already downloaded by a past collection | {pool['collected']:,} |",
        f"| indexed since March but never collected | {pool['indexed_uncollected']:,} |",
        f"| newly visible in the refresh | {pool['new_from_refresh']:,} |",
        f"| **manifest total** | **{len(rows):,}** |",
        "",
        "The middle row is the cost of quota-ing over seven domains: those captures "
        "sat in the index the whole time and no manifest ever asked for them.",
        "",
        "## Why the archive is thin here, in its own numbers",
        "",
        "| status | March pull, 2025+ | refresh |",
        "|---|---:|---:|",
    ]
    codes = sorted({k for k in list(old_stats) + list(new_stats) if k.startswith("status_")},
                   key=lambda k: -old_stats[k])
    for k in codes[:8]:
        lines.append(f"| {k[7:] or '-'} | {old_stats[k]:,} | {new_stats[k]:,} |")
    lines += [
        "",
        "403 is the PerimeterX wall. A capture exists; its body is a CAPTCHA page and "
        "carries no price. Those rows are dropped here, not counted as supply.",
        "",
        "## Manifest by quarter",
        "",
        "| quarter | gig-days to collect |",
        "|---|---:|",
    ]
    qtot = Counter()
    for m, cats in by_month.items():
        qtot[quarter(m)] += sum(cats.values())
    for q in sorted(qtot):
        lines.append(f"| {q} | {qtot[q]:,} |")
    lines += [
        "",
        "## Manifest by category",
        "",
        "| category | gig-days | collected before? |",
        "|---|---:|---|",
    ]
    collected_domains = {"design", "coding", "writing", "marketing",
                         "video", "audio", "translation"}
    for cat, n in by_cat.most_common():
        lines.append(f"| {cat} | {n:,} | "
                     f"{'yes' if cat in collected_domains else '**no**'} |")
    lines += [
        "",
        f"Manifest written to `{MANIFEST.relative_to(BASE_DIR)}`. Feed it to "
        "`08-download-html.py --manifest ... --gzip`, then `09-extract-prices.py`.",
        "",
    ]
    (OUTDIR / "delta.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
