#!/usr/bin/env python3
"""
Step 72: Re-label the index so the collectable headroom is addressable, and
project it into the form 41-balanced-manifest.py consumes.

WHY. Steps 67/68 measured that `uncategorized` is the densest label in the CDX
index and that part of it belongs to domains already collected. But
40-history-headroom.py drops `uncategorized` from the projection before
41-balanced-manifest.py ever sees it (SKIP_CATEGORIES), so none of that headroom
is reachable by any existing manifest. The labels have to be fixed first. This
step does that and nothing else -- it selects no gigs and downloads nothing.

TWO SEPARATE DEFECTS, FIXED IN ORDER. Sizing them apart matters, because they
have different implications for the shipped series.

  1. URL-PARSE DEFECT (found here, 2026-09-01). `04-classify-categories.py`
     reads the slug off the `original` column with
     `url.split("fiverr.com/")[-1] if "fiverr.com/" in url else url`. The CDX
     index also carries the pre-HTTPS capture form `http://fiverr.com:80/...`,
     which contains no `fiverr.com/` substring, so the fallback splits the whole
     URL on "/" and returns `parts[1]` -- the empty string between the scheme's
     two slashes. Every such snapshot is classified on an EMPTY slug and lands
     in `uncategorized` regardless of content. The label is therefore not a
     function of the gig: the same listing is labelled correctly in its https
     captures and `uncategorized` in its :80 captures.

     The fix needs no new keywords -- it is step 04's own rule applied to the
     slug taken from `urlkey`, which is the canonicalised form and always has
     the shape `com,fiverr)/<seller>/<slug>`.

  2. KEYWORD LEAK (measured in step 68, bias-tested in steps 70/71). Step 04
     matches exact substrings, so `develop-or-customize-drupal-websites` misses
     coding's `web-develop`/`app-develop`/`developer`. Step 68's broader stems
     recover those.

Order is parse fix, then new families, then leakage stems -- new families before
leakage because the leakage stems are deliberately broad (`art`, `lead`,
`sound`) and would otherwise swallow photography and social-engagement listings.
That is step 68's own ordering, so the leak figures stay comparable to
`families.md`.

Running the stages in this order also makes the v2 label a pure function of the
gig id, which the v1 labels are not. That matters downstream: 41's gig summary
takes the category off whichever row sorts first, and the sort key does not
include the category column, so a gig step 04 labelled inconsistently gets an
arbitrary one of its labels.

`data_entry` and `data_analysis` are carried through rather than skipped: step
67 sizes them at median 346 and 180 matched gigs per pair, thin but
translation-grade, and the sizing step should be able to cost them.

Input:  data/cdx-index/gig-pages-classified.tsv
Output: data/cdx-index/gig-month-index-v2.tsv   (sorted projection, for step 41)
        runs/uncollected-headroom/reclassify-v2.md
"""

import importlib.util
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gigfilter import is_gig_id

BASE_DIR = Path(__file__).resolve().parent.parent
CLASSIFIED = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
PROJECTION = BASE_DIR / "data" / "cdx-index" / "gig-month-index-v2.tsv"
SORT_TMP = BASE_DIR / "data" / "cdx-index" / "sort-tmp"
OUTDIR = BASE_DIR / "runs" / "uncollected-headroom"

COLLECTED = ("design", "coding", "writing", "marketing", "video", "audio", "translation")


def _load(stem):
    """Import a numbered pipeline step by path -- the names are not identifiers."""
    spec = importlib.util.spec_from_file_location(
        stem.split("-", 1)[0].join(("m", "")), Path(__file__).resolve().parent / stem)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Both rule sets are imported rather than copied, so the three steps cannot drift.
_s04 = _load("04-classify-categories.py")
_s68 = _load("68-uncategorized-families.py")
classify_slug = _s04.classify_slug
NEW_FAMILIES = _s68.NEW_FAMILIES
LEAKAGE_STEMS = _s68.LEAKAGE_STEMS

_RULES = [(lab, kw) for lab, kws in NEW_FAMILIES.items() for kw in kws]
_RULES += [(lab, kw) for lab, kws in LEAKAGE_STEMS.items() for kw in kws]
_LEAK_LABELS = set(LEAKAGE_STEMS)

PARSE_FIX, NEW_FAMILY, LEAK_FIX, RESIDUAL = "parse", "family", "leak", "residual"


def label_of(gid):
    """v2 label for a gig id, plus which stage produced it.

    `gid` is `<seller>/<slug>` taken from the urlkey, so the slug is always the
    real one -- this is what makes stage 1 a fix rather than a re-run.
    """
    slug = gid.split("/", 1)[1] if "/" in gid else ""
    cat = classify_slug(slug)[0]          # step 04's own rule, correct input
    if cat != "uncategorized":
        return cat, PARSE_FIX
    s = gid.lower()
    for lab, kw in _RULES:
        if kw in s:
            return lab, (LEAK_FIX if lab in _LEAK_LABELS else NEW_FAMILY)
    return "uncategorized", RESIDUAL


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    SORT_TMP.mkdir(parents=True, exist_ok=True)

    raw = PROJECTION.with_suffix(".raw.tmp")

    snap_before, snap_after = Counter(), Counter()
    v1_label = {}                # gid -> first v1 label seen
    mixed = set()                # gids step 04 labelled inconsistently
    v2 = {}                      # gid -> (label, stage)
    n_rows = n_kept = n_status = n_reserved = 0

    print("Pass 1: re-labelling and projecting...", file=sys.stderr)
    with open(CLASSIFIED) as fin, open(raw, "w") as fout:
        next(fin, None)
        for line in fin:
            n_rows += 1
            if n_rows % 2_000_000 == 0:
                print(f"  ...{n_rows:,} rows, {n_kept:,} kept", file=sys.stderr, flush=True)
            p = line.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            urlkey, ts, status, cat = p[0], p[1], p[3], p[6]
            if status != "200":
                n_status += 1
                continue
            gid = urlkey.split(")/", 1)[1] if ")/" in urlkey else urlkey
            gid = gid.split("?", 1)[0]
            if not is_gig_id(gid):
                n_reserved += 1
                continue

            snap_before[cat] += 1
            prev = v1_label.setdefault(gid, cat)
            if prev != cat:
                mixed.add(gid)

            ent = v2.get(gid)
            if ent is None:
                ent = v2[gid] = label_of(gid)
            cat_v2 = ent[0]

            snap_after[cat_v2] += 1
            if cat_v2 == "uncategorized":
                continue          # residual long tail: not addressable, not projected
            fout.write(f"{gid}\t{ts[:6]}\t{ts}\t{cat_v2}\n")
            n_kept += 1

    print(f"  scanned {n_rows:,}; kept {n_kept:,}; dropped {n_status:,} non-200 / "
          f"{n_reserved:,} reserved", file=sys.stderr)

    print("Pass 2: external sort by gig, month, timestamp...", file=sys.stderr)
    cmd = (f"sort -t'\t' -k1,1 -k2,2 -k3,3 -T '{SORT_TMP}' -S 512M "
           f"'{raw}' > '{PROJECTION}'")
    subprocess.run(["bash", "-c", cmd], check=True)
    raw.unlink()

    # ---- report -----------------------------------------------------------
    gig_before = Counter(v1_label.values())
    gig_after = Counter(lab for lab, _st in v2.values())
    stages = Counter(st for lab, st in v2.values())
    # a gig only *gains* from stage 1 if step 04 left it uncategorized outright
    parse_recovered = sum(1 for g, (lab, st) in v2.items()
                          if st == PARSE_FIX and v1_label[g] == "uncategorized")

    L = ["# v2 labels: what the re-classification moves", "",
         f"Source: `{CLASSIFIED.relative_to(BASE_DIR)}` ({n_rows:,} rows scanned, "
         f"status-200 gig URLs only). Distinct gigs: **{len(v1_label):,}**.", "",
         "## The defect this found", "",
         "`04-classify-categories.py` takes the slug from the `original` column with a "
         "`\"fiverr.com/\" in url` test. The index also carries the pre-HTTPS capture form "
         "`http://fiverr.com:80/<seller>/<slug>`, which does not contain that substring, so "
         "the fallback path splits the whole URL on `/` and returns the empty string between "
         "the scheme's two slashes. **Every `:80` snapshot is classified on an empty slug and "
         "labelled `uncategorized` regardless of content.**", "",
         f"- Gigs step 04 labelled **inconsistently across their own snapshots** (correct in "
         f"the https captures, `uncategorized` in the `:80` ones): **{len(mixed):,}**",
         f"- Gigs step 04 left `uncategorized` that its own keyword rule labels once the slug "
         f"is read from `urlkey` instead: **{parse_recovered:,}**", "",
         "This is a labelling defect, not a keyword one -- no new stems are involved in "
         "recovering these.", "",
         "## What each stage contributes (distinct gigs)", "",
         "| stage | gigs | what it is |", "|---|---:|---|",
         f"| 1. parse fix | {stages[PARSE_FIX]:,} | step 04's own rule, slug read from `urlkey` |",
         f"| 2. new families | {stages[NEW_FAMILY]:,} | taxonomy rows T9/T10/T12 + families never listed |",
         f"| 3. leakage stems | {stages[LEAK_FIX]:,} | step 68's broader stems for the seven collected domains |",
         f"| residual | {stages[RESIDUAL]:,} | genuine long tail, not projected |", "",
         "## Distinct gigs per label", "",
         "| label | v1 (step 04) | v2 | change |", "|---|---:|---:|---:|"]
    for lab in sorted(set(gig_before) | set(gig_after),
                      key=lambda c: -gig_after.get(c, 0)):
        b, a = gig_before.get(lab, 0), gig_after.get(lab, 0)
        tag = "**new**" if b == 0 else (f"{(a-b)/b*100:+.0f}%" if a != b else "0%")
        L.append(f"| {'**' + lab + '**' if lab in COLLECTED else lab} | "
                 f"{b:,} | {a:,} | {tag} |")
    L += ["", "## Snapshots per label", "", "| label | v1 | v2 |", "|---|---:|---:|"]
    for lab in sorted(set(snap_before) | set(snap_after),
                      key=lambda c: -snap_after.get(c, 0)):
        L.append(f"| {lab} | {snap_before.get(lab, 0):,} | {snap_after.get(lab, 0):,} |")
    L += ["", f"Projection written: `{PROJECTION.relative_to(BASE_DIR)}` "
              f"({n_kept:,} rows). Feed it to `41-balanced-manifest.py --projection` "
              f"to cost a collection.", ""]

    (OUTDIR / "reclassify-v2.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
