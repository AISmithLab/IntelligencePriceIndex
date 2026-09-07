#!/usr/bin/env python3
"""
Step 75: AI branding over time, measured from gig SLUGS across the whole CDX
index rather than from titles on the pages we downloaded.

WHY, GIVEN STEP 57 EXISTS. `57-ai-diffusion-titles.py` already dates in-market
AI diffusion at 2023Q1 from gig titles, and its classifier is audited (a ~0.02%
pre-2022 false-positive floor, guards for the Adobe Illustrator `.ai` extension
and for Synthesia the piano software). But it can only see the 384,983
gig-date observations that were actually downloaded, and that sample has two
problems for a time series:

  * SEAMS. 2024Q2 holds 10,600 observations and 2024Q3 holds 52,087, because
    that is where the expanded harvest lands. The raw share jumps 1.38% -> 3.26%
    across that seam and the two are not comparable.
  * THINNESS. 2025Q1 onward runs ~2,000-5,700 observations per quarter.

The slug is the title. It is in `urlkey` for every capture in the index --
1.77M distinct gigs over 22.7M snapshots, 2010-2026 -- so the same measure can
be taken on the whole archive with no crawl. It is also independent of
`04-classify-categories.py`, so the classifier leak (steps 68/70/71) cannot bias
it: nothing here selects on category.

WHAT A SLUG CAN AND CANNOT SEE. Fiverr mints the URL slug from the title when
the listing is created, so a seller who retitles in place gets a NEW url and
appears here as a new gig. This measure therefore tracks AI-branded *entry*
cleanly and cannot see incumbent retitling under a stable URL. Step 57 part C
found the rise was driven by new listings arriving rather than rebranding, so
the two should agree; where they disagree, step 57's composition-fixed panel is
the one that speaks to retitling.

TWO CURVES, because they answer different questions:

  ENTRY COHORT  of the gigs FIRST captured in quarter Q, what share are
                AI-branded. Each gig counted once, at its first sighting. This
                is the flow -- what is arriving. Caveat: first *capture* is not
                first *listing*; a gig created in 2021 and first crawled in 2023
                is dated 2023, which drags the curve later in quarters where
                Wayback crawled sparsely.

  STOCK         of the distinct gigs OBSERVED in quarter Q, what share are
                AI-branded. This is the market composition on display. It is
                affected by which gigs Wayback happened to crawl that quarter,
                so read it alongside the observation count.

The classifier is IMPORTED from step 57, not reimplemented, so any difference
between the two measures is the data and not the rule.

Input:  data/cdx-index/gig-pages-classified.tsv
Output: runs/ai-slug-diffusion/diffusion.md
"""

import argparse
import importlib.util
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
OUTDIR = BASE_DIR / "runs" / "ai-slug-diffusion"

sys.path.insert(0, str(BASE_DIR / "code"))
from gigfilter import is_gig_id


def _load(fname, name):
    spec = importlib.util.spec_from_file_location(name, BASE_DIR / "code" / fname)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_s57 = _load("57-ai-diffusion-titles.py", "s57")
_s72 = _load("72-reclassify-v2.py", "s72")
classify = _s57.classify
label_of = _s72.label_of

QLO = 2010 * 4          # quarter index floor, keeps the bitmask small
NQ = 68                 # 2010Q1..2026Q4


def qidx(ts):
    return int(ts[:4]) * 4 + (int(ts[4:6]) - 1) // 3 - QLO


def qstr(i):
    n = i + QLO
    return f"{n // 4}Q{n % 4 + 1}"


def slug_text(gid):
    """`seller/do-a-thing-with-ai` -> `do a thing with ai`, so step 57's
    word-boundary rules and its guards apply unchanged."""
    return gid.split("/", 1)[1].replace("-", " ") if "/" in gid else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2018Q3", help="first quarter to report")
    ap.add_argument("--end", default="2026Q1")
    ap.add_argument("--by-category", action="store_true",
                    help="also break the entry cohort down by v2 label (slower)")
    args = ap.parse_args()

    lo = (int(args.start[:4]) * 4 + int(args.start[5]) - 1) - QLO
    hi = (int(args.end[:4]) * 4 + int(args.end[5]) - 1) - QLO

    # gig -> [first_quarter, quarter_bitmask, gen, any_, anti]
    gigs = {}
    n_rows = 0
    print("Streaming the index...", file=sys.stderr)
    with open(INPUT, encoding="utf-8", errors="replace") as f:
        next(f, None)
        for line in f:
            n_rows += 1
            if n_rows % 2_000_000 == 0:
                print(f"  ...{n_rows:,} rows, {len(gigs):,} gigs",
                      file=sys.stderr, flush=True)
            p = line.rstrip("\n").split("\t")
            if len(p) < 7 or p[3] != "200":
                continue
            gid = p[0].split(")/", 1)[1] if ")/" in p[0] else p[0]
            gid = gid.split("?", 1)[0].lower()
            if not is_gig_id(gid):
                continue
            q = qidx(p[1])
            if not 0 <= q < NQ:
                continue
            rec = gigs.get(gid)
            if rec is None:
                any_, gen, anti = classify(slug_text(gid))
                gigs[gid] = [q, 1 << q, gen, any_, anti]
            else:
                if q < rec[0]:
                    rec[0] = q
                rec[1] |= 1 << q

    print(f"  {n_rows:,} rows -> {len(gigs):,} distinct gigs", file=sys.stderr)

    entry = defaultdict(lambda: [0, 0, 0, 0])     # q -> [n, gen, any, anti]
    stock = defaultdict(lambda: [0, 0, 0, 0])
    for _g, (fq, mask, gen, any_, anti) in gigs.items():
        e = entry[fq]
        e[0] += 1; e[1] += gen; e[2] += any_; e[3] += anti
        m = mask
        while m:
            q = (m & -m).bit_length() - 1
            s = stock[q]
            s[0] += 1; s[1] += gen; s[2] += any_; s[3] += anti
            m &= m - 1

    def table(d, title, note):
        L = ["", f"### {title}", "", note, "",
             "| quarter | gigs | AI_GEN | share | AI_ANY | share | anti-AI | share |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for q in range(lo, hi + 1):
            n, g, a, x = d.get(q, [0, 0, 0, 0])
            if not n:
                L.append(f"| {qstr(q)} | 0 | -- | -- | -- | -- | -- | -- |")
                continue
            L.append(f"| {qstr(q)} | {n:,} | {g:,} | {g/n*100:.2f}% | "
                     f"{a:,} | {a/n*100:.2f}% | {x:,} | {x/n*100:.2f}% |")
        return L

    # precision floor, step 57's discipline: what does it flag BEFORE generative
    # AI was purchasable? Those hits are the false-positive rate.
    pre = [g for g, r in gigs.items() if r[2] and r[0] < (2022 * 4 + 3 - QLO)]
    pre_n = sum(1 for r in gigs.values() if r[0] < (2022 * 4 + 3 - QLO))

    L = ["# AI branding over time, from gig slugs across the whole index", "",
         f"Source: `{INPUT.relative_to(BASE_DIR)}` — {n_rows:,} rows, "
         f"**{len(gigs):,} distinct gigs**, status-200 gig URLs only. "
         f"No crawl; no dependence on `04-classify-categories.py`.", "",
         "Classifier imported verbatim from `57-ai-diffusion-titles.py` "
         "(`AI_GEN` generative-specific, `AI_ANY` any AI branding, `ANTI` explicit "
         "human/no-AI claim), with its Adobe-Illustrator `.ai` and Synthesia guards. "
         "Slugs are de-hyphenated first so its word-boundary rules apply.", "",
         "## Precision floor", "",
         f"`AI_GEN` hits among gigs first captured **before 2022Q4**, when "
         f"generative AI was not commercially purchasable: **{len(pre):,}** of "
         f"{pre_n:,} gigs (**{len(pre)/max(pre_n,1)*100:.3f}%**). That is the "
         f"false-positive floor to read the post-2023 levels against.", ""]
    for g in sorted(pre)[:12]:
        L.append(f"- `{g}`")

    L += table(entry, "Entry cohort — gigs FIRST captured in the quarter",
               "Each gig counted once, at first sighting. This is the flow: what "
               "is arriving. First *capture* is not first *listing*, so quarters "
               "Wayback crawled sparsely push their gigs later.")
    L += table(stock, "Stock — distinct gigs OBSERVED in the quarter",
               "Market composition on display. Sensitive to which gigs Wayback "
               "crawled that quarter, so read it against the gig count.")

    if args.by_category:
        L += ["", "### Entry cohort by category (v2 labels)", "",
              "Categories from `72-reclassify-v2.py`, which repairs step 04's "
              "leak — so this is not biased by the miss that steps 70/71 measured.",
              "", "AI_GEN share of gigs first captured in the quarter.", ""]
        cats = ["design", "coding", "writing", "marketing", "video", "audio",
                "translation"]
        bycat = defaultdict(lambda: [0, 0])
        for g, r in gigs.items():
            c = label_of(g)[0]
            if c in set(cats):
                k = bycat[(c, r[0])]
                k[0] += 1; k[1] += r[2]
        L += ["| quarter | " + " | ".join(cats) + " |", "|---|" + "---|" * len(cats)]
        for q in range(lo, hi + 1):
            row = []
            for c in cats:
                n, g = bycat.get((c, q), [0, 0])
                row.append(f"{g/n*100:.2f}%" if n >= 50 else "--")
            L.append(f"| {qstr(q)} | " + " | ".join(row) + " |")
        L.append("")
        L.append("`--` = fewer than 50 gigs entered that quarter, too few to rate.")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "diffusion.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
