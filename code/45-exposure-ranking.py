#!/usr/bin/env python3
"""
Step 45: Pre-registered AI-exposure ranking of the seven Fiverr categories.

This script exists to make the ranking REPRODUCIBLE and AUDITABLE, not to
discover it. It is Phase -1 of `plans/active/transaction-volume.md`, and it must
be run and committed BEFORE any outcome is estimated on the balanced frame. The
whole point of the transaction-volume study is a difference-in-differences whose
treatment is *exposure*, not time; an exposure ranking built after seeing the
per-category demand breaks is not pre-registered in any meaningful sense, and it
is exactly the objection that sank the elasticity table in step 29.

SOURCE — external, published, and not derived from our data:

  Eloundou, Manning, Mishkin & Rock (2023/2024), "GPTs are GPTs: Labor market
  impact potential of LLMs", Science 384(6702). Occupation-level exposure from
  the authors' public replication repository:

      https://github.com/openai/GPTs-are-GPTs  ->  data/occ_level.csv

  Vendored to `data/eloundou-2023-occ-level.csv` (923 O*NET-SOC occupations) so
  the ranking reproduces offline and cannot drift under us.

EXPOSURE MEASURE. The file carries three cumulative thresholds (alpha < beta <
gamma) under two annotators (`human_rating_*` by human labellers, `dv_rating_*`
by GPT-4). We pre-register:

  * PRIMARY   `human_rating_beta` — beta is the paper's headline measure (direct
    LLM exposure PLUS exposure via LLM-powered software, which is the right
    notion for a freelance deliverable), and the HUMAN annotation avoids the
    circularity of letting a model score its own labour-market reach. A reviewer
    will raise that circularity; we pre-empt it by not depending on it.
  * ROBUSTNESS `dv_rating_beta` — the GPT-4 annotation, same threshold. Any
    finding must be reported under both. They do NOT agree on coding (see below),
    and that disagreement is declared here rather than discovered later.

MAPPING. Each Fiverr category is mapped to O*NET-SOC occupations by task
content, equally weighted (we have no employment weights for Fiverr gigs, and
inventing them would be a researcher degree of freedom). The mapping is fixed
here and is not revised after outcomes are seen.

Run:  python3 code/45-exposure-ranking.py
Out:  data/exposure-ranking.csv
"""

import csv
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "data" / "eloundou-2023-occ-level.csv"
OUT = BASE / "data" / "exposure-ranking.csv"

PRIMARY = "human_rating_beta"
ROBUST = "dv_rating_beta"

# Fiverr category -> O*NET-SOC codes. Fixed 2026-08-17, pre-outcome.
MAPPING = {
    "translation": ["27-3091.00"],                                   # Interpreters and Translators
    "writing":     ["27-3043.00", "27-3043.05", "27-3041.00",        # Writers/Authors; Poets, Lyricists
                    "27-3042.00", "43-9081.00"],                     # and Creative Writers; Editors;
                                                                     # Technical Writers; Proofreaders
    "coding":      ["15-1251.00", "15-1252.00", "15-1254.00"],       # Programmers; Software Devs; Web Devs
    "marketing":   ["13-1161.00", "13-1161.01", "27-3031.00"],       # Market Research Analysts; Search
                                                                     # Marketing Strategists; PR Specialists
    "design":      ["27-1024.00", "27-1011.00", "15-1255.00"],       # Graphic Designers; Art Directors;
                                                                     # Web and Digital Interface Designers
    "video":       ["27-4032.00", "27-4031.00", "27-1014.00",        # Film/Video Editors; Camera Operators;
                    "27-2012.00"],                                   # SFX Artists/Animators; Producers/Dirs
    "audio":       ["27-2042.00", "27-2041.00", "27-4014.00",        # Musicians/Singers; Music Directors
                    "27-4011.00"],                                   # and Composers; Sound Engineering
                                                                     # Techs; Audio and Video Techs
}

# Pre-declared sensitivity: 15-1255.00 (Web and Digital Interface Designers) is
# design by title and coding by task content. Fiverr's design category does carry
# web/UI gigs, so it is IN the primary mapping — but design's rank is the one
# most movable by a single mapping call, so we report it both ways up front
# rather than being asked for it later.
SENSITIVITY_DROP = {"design": ["15-1255.00"]}


def load():
    rows = {}
    with open(SRC) as f:
        for r in csv.DictReader(f):
            rows[r["O*NET-SOC Code"]] = r
    return rows


def score(rows, codes, field):
    vals = []
    for c in codes:
        if c not in rows:
            sys.exit(f"FATAL: SOC code {c} not found in {SRC.name}")
        vals.append(float(rows[c][field]))
    return sum(vals) / len(vals)


def main():
    rows = load()
    recs = []
    for cat, codes in MAPPING.items():
        rec = {
            "category": cat,
            "n_occupations": len(codes),
            "exposure_primary": round(score(rows, codes, PRIMARY), 4),
            "exposure_robust": round(score(rows, codes, ROBUST), 4),
            "soc_codes": ";".join(codes),
            "occupations": "; ".join(rows[c]["Title"] for c in codes),
        }
        if cat in SENSITIVITY_DROP:
            kept = [c for c in codes if c not in SENSITIVITY_DROP[cat]]
            rec["exposure_primary_sens"] = round(score(rows, kept, PRIMARY), 4)
            rec["exposure_robust_sens"] = round(score(rows, kept, ROBUST), 4)
        else:
            rec["exposure_primary_sens"] = rec["exposure_primary"]
            rec["exposure_robust_sens"] = rec["exposure_robust"]
        recs.append(rec)

    recs.sort(key=lambda r: -r["exposure_primary"])
    for i, r in enumerate(recs, 1):
        r["rank_primary"] = i
    by_rob = sorted(recs, key=lambda r: -r["exposure_robust"])
    for i, r in enumerate(by_rob, 1):
        r["rank_robust"] = i

    cols = ["rank_primary", "category", "exposure_primary", "rank_robust",
            "exposure_robust", "exposure_primary_sens", "exposure_robust_sens",
            "n_occupations", "soc_codes", "occupations"]
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in recs:
            w.writerow({c: r[c] for c in cols})

    print(f"source: {SRC.name} ({len(rows)} occupations)")
    print(f"primary: {PRIMARY}   robustness: {ROBUST}\n")
    print(f"{'cat':<12}{'primary':>9}{'rk':>4}{'robust':>9}{'rk':>4}   agree?")
    for r in recs:
        agree = "" if abs(r["rank_primary"] - r["rank_robust"]) <= 1 else "  <-- DISAGREE"
        print(f"{r['category']:<12}{r['exposure_primary']:>9.3f}{r['rank_primary']:>4}"
              f"{r['exposure_robust']:>9.3f}{r['rank_robust']:>4}{agree}")

    # The pre-registered treatment/control split: categories on which BOTH
    # annotators agree. Anything they disagree on is quarantined, not forced.
    hi = [r["category"] for r in recs if r["rank_primary"] <= 2 and r["rank_robust"] <= 3]
    lo = [r["category"] for r in recs if r["rank_primary"] >= 6 and r["rank_robust"] >= 6]
    mid = [r["category"] for r in recs if r["category"] not in hi + lo]
    print(f"\nHIGH (both annotators): {hi}")
    print(f"LOW  (both annotators): {lo}")
    print(f"MID / disputed:         {mid}")
    print(f"\nwrote {OUT.relative_to(BASE)}")


if __name__ == "__main__":
    main()
