#!/usr/bin/env python3
"""
Step 43: results from the two enlarged collections.

Both `plans/active/expanded-collection.md` and `plans/active/balanced-history.md`
stop at the same step: "re-measure matched gigs per bilateral per category
against the +/-5% requirement", and then decide whether the enlarged panel moves
the index enough to warrant rebuilding 19 -> 21 -> 23 -> 18. This script answers
the first question and reports the evidence for the second.

It computes, for four panels:

    shipped-recent      data/pilot/recent-prices.csv       (2,908 panel gigs)
    expanded-recent     data/pilot/expanded-prices.csv     (rule B, no survivor filter)
    shipped-historical  data/pilot/pilot-prices.csv        (1,066 panel gigs)
    balanced-historical data/pilot/balanced-prices.csv     (quota-sampled, 2018Q3+)

  1. panel gigs per category,
  2. matched gigs per bilateral -- the unit that governs precision (S3.6),
     as median / min / share of pairs below MIN_MATCH,
  3. GEKS-Jevons levels with bootstrap bands, against the +/-5% adequacy rule,
  4. the S3.7 window-sensitivity check re-run on the denser historical panel.

Panel construction, the estimator and the bootstrap are IMPORTED from
`21-geks-index.py` (which imports `19-tpd-index.py`), so nothing here is a
reimplementation -- only the input file and the category source differ. That is
deliberate: a difference between these results and the paper's must be the data,
not the code.

NOTE ON PROVENANCE. Nothing this script prints is a paper figure. The paper is
governed by the frozen table `data/pilot/paper-numbers.md` and is built from the
original two crawls only (S3.2). These are paper 2's numbers.

Run:  python3 code/43-enlarged-results.py [--boot N] [--out PATH]
"""

import argparse
import csv
import importlib.util
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PILOT = BASE_DIR / "data" / "pilot"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gigfilter import is_gig  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parent / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


geks = _load("geks", "21-geks-index.py")
tpd = geks.tpd

CATS = geks.CATS
MIN_MATCH = geks.MIN_MATCH
q_to_int = geks.q_to_int
PRICE_MAX = tpd.PRICE_MAX

# ---------------------------------------------------------------------------
# Panel construction: identical rules to 19/21, different input files.
# ---------------------------------------------------------------------------


def category_map(manifest, gig_col="gig_id", cat_col="category"):
    """{(seller, slug): category} from a crawl manifest."""
    out = {}
    with open(manifest) as f:
        for row in csv.DictReader(f, delimiter="\t"):
            gid = row.get(gig_col, "")
            parts = gid.split("/", 1)
            if len(parts) == 2:
                out[(parts[0], parts[1])] = row.get(cat_col, "")
    return out


def build_panel(prices_csv, gig_cat):
    """Same filters as 19-tpd-index.py: gigfilter, price guard, gig-quarter
    median, keep gigs seen in >=2 quarters."""
    gig_quarter = defaultdict(lambda: defaultdict(list))
    rows = kept = 0
    with open(prices_csv) as f:
        for row in csv.DictReader(f):
            rows += 1
            if not is_gig(row["seller"]):
                continue
            key = (row["seller"], row["slug"])
            if key not in gig_cat:
                continue
            try:
                price = float(row.get("price_basic", 0) or 0)
            except ValueError:
                continue
            if price <= 0 or price > PRICE_MAX:
                continue
            q = tpd.to_quarter(row["year"], row["month"])
            if not q:
                continue
            gig_quarter[key][q].append(price)
            kept += 1
    panel = geks.tpd._collapse(gig_quarter, gig_cat)
    return panel, rows, kept


# ---------------------------------------------------------------------------
# Diagnostic: matched gigs per bilateral, the unit that binds (S3.6).
# ---------------------------------------------------------------------------


def matched_per_bilateral(panel_cat, window_start=None):
    """-> (median, min, n_pairs, n_thin, max) over all quarter pairs."""
    by_q, quarters = geks._log_panel(panel_cat, window_start)
    counts = []
    for i, s in enumerate(quarters):
        for t in quarters[i + 1:]:
            counts.append(len(by_q[s].keys() & by_q[t].keys()))
    if not counts:
        return None
    thin = sum(1 for c in counts if c < MIN_MATCH)
    return {
        "median": float(np.median(counts)),
        "min": min(counts),
        "max": max(counts),
        "pairs": len(counts),
        "thin": thin,
        "thin_share": thin / len(counts),
        "quarters": len(quarters),
    }


# +/-5% matched-gig requirement per category, from S3.6 (inverted precision fit).
REQUIREMENT = {"writing": 900, "design": 1100, "video": 1600, "coding": 7400}


def analyse(label, prices_csv, manifest, window_start, n_boot, seed=7):
    print(f"\n{'=' * 78}\n{label}\n{'=' * 78}", flush=True)
    t0 = time.time()
    if prices_csv is None:
        # the paper's historical panel: categories come from the item clustering,
        # not from a crawl manifest, so 19's own builder is used verbatim.
        panel = tpd.build_panel_historical()
        rows = kept = -1
    else:
        gig_cat = category_map(manifest)
        panel, rows, kept = build_panel(prices_csv, gig_cat)
    n_panel = sum(len(v) for v in panel.values())
    src = "pilot-prices.csv (via 19.build_panel_historical)" if prices_csv is None \
        else f"{Path(prices_csv).name}: {rows:,} rows -> {kept:,} usable"
    print(f"  source {src} -> {n_panel:,} panel gigs   ({time.time() - t0:.0f}s)", flush=True)

    rng = np.random.default_rng(seed)
    out = {}
    for cat in CATS:
        pc = panel.get(cat)
        if not pc:
            continue
        mb = matched_per_bilateral(pc, window_start)
        idx, se, diag = geks.geks_index(pc, rng=rng, n_boot=n_boot,
                                        window_start=window_start)
        if not idx:
            out[cat] = {"panel_gigs": len(pc), "matched": mb, "index": None}
            continue
        qs = sorted(idx, key=q_to_int)
        term = qs[-1]
        band = 1.96 * se.get(term, 0.0)
        out[cat] = {
            "panel_gigs": len(pc),
            "matched": mb,
            "base_q": qs[0],
            "terminal_q": term,
            "level": idx[term],
            "delta_pct": idx[term] - 100.0,
            "band_pct": 100.0 * (math.exp(band) - 1.0) if band else 0.0,
            "pair_density": diag["pair_density"],
            "index": {q: idx[q] for q in qs},
        }
        m = out[cat]
        print(f"  {cat:<12} panel {m['panel_gigs']:>6,}  matched/pair med "
              f"{mb['median']:>7.0f} min {mb['min']:>5}  thin {mb['thin_share']:>5.1%}  "
              f"{m['base_q']}->{term} {m['level']:>8.1f}  +/-{m['band_pct']:.1f}%",
              flush=True)
    return out


def composite(res, weights):
    """Weighted geometric mean of category levels at the latest shared quarter."""
    have = {c: r for c, r in res.items() if r.get("index")}
    if not have:
        return None
    shared = set.intersection(*(set(r["index"]) for r in have.values()))
    if not shared:
        return None
    q = max(shared, key=q_to_int)
    wsum = sum(weights.get(c, 0) for c in have)
    if wsum <= 0:
        return None
    ln = sum(weights.get(c, 0) * math.log(have[c]["index"][q]) for c in have) / wsum
    return {"quarter": q, "level": math.exp(ln), "categories": sorted(have)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=200,
                    help="bootstrap replications (0 to skip; the paper uses 200)")
    ap.add_argument("--out", default=str(PILOT / "enlarged-results.json"))
    args = ap.parse_args()

    weights = {}
    with open(PILOT / "recent-category-weights.csv") as f:
        for row in csv.DictReader(f):
            weights[row["category"]] = float(row["weight"])

    panels = [
        ("shipped-recent",
         "SHIPPED RECENT (rule A, survivor-filtered) -- the paper's recent panel",
         PILOT / "recent-prices.csv", PILOT / "recent-manifest.tsv", None),
        ("expanded-recent",
         "EXPANDED RECENT (rule B, no survivor filter)",
         PILOT / "expanded-prices.csv", PILOT / "expanded-manifest.tsv", None),
        ("shipped-historical",
         "SHIPPED HISTORICAL (500-seller pilot) -- the paper's historical panel",
         None, None, "2020Q1"),
        ("balanced-2018Q3",
         "BALANCED HISTORICAL from 2018Q3 (quota-sampled on category x quarter pair)",
         PILOT / "balanced-prices.csv", PILOT / "balanced-manifest-1200.tsv", "2018Q3"),
        ("balanced-2020Q1",
         "BALANCED HISTORICAL from 2020Q1 -- same panel, later window (S3.7 check)",
         PILOT / "balanced-prices.csv", PILOT / "balanced-manifest-1200.tsv", "2020Q1"),
    ]

    results = {}
    for key, label, prices, manifest, wstart in panels:
        results[key] = analyse(label, prices, manifest, wstart, args.boot)
        comp = composite(results[key], weights)
        if comp:
            print(f"  {'COMPOSITE':<12} {comp['quarter']} level {comp['level']:.1f} "
                  f"(over {len(comp['categories'])} categories, shipped weights)")
            results[key]["_composite"] = comp

    Path(args.out).write_text(json.dumps(results, indent=1, default=str))
    print(f"\nwrote {args.out}")

    # ---- the requirement check the two plans are blocked on ----------------
    print(f"\n{'=' * 78}\nMATCHED GIGS PER BILATERAL vs the +/-5% REQUIREMENT (S3.6)\n{'=' * 78}")
    print("Each block compares a shipped panel with its enlarged replacement over the\n"
          "SAME window, so the bands are like for like. The 'need' column is S3.6's\n"
          "inverted precision fit, which was estimated on the recent panel; applying it\n"
          "to the historical window is indicative rather than exact.")
    for tag, base_key, enl_key in [
        ("recent window, 2024Q3 base", "shipped-recent", "expanded-recent"),
        ("historical window, 2020Q1 base", "shipped-historical", "balanced-2020Q1"),
    ]:
        print(f"\n-- {tag} --")
        print(f"{'category':<12} {'need':>7} {'before':>8} {'after':>8} {'gain':>7}  "
              f"{'band':>8}  verdict")
        base, enl = results.get(base_key, {}), results.get(enl_key, {})
        for cat in CATS:
            need = REQUIREMENT.get(cat)
            b = base.get(cat, {}).get("matched")
            e = enl.get(cat, {}).get("matched")
            if not (b and e):
                continue
            gain = e["median"] / b["median"] if b["median"] else float("inf")
            band = enl.get(cat, {}).get("band_pct")
            bandtxt = f"+/-{band:.1f}%" if band else "n/a"
            if need is None:
                verdict = "no stated requirement"
            elif e["median"] >= need:
                verdict = "MEETS requirement"
            else:
                verdict = f"short by {need / e['median']:.1f}x"
            print(f"{cat:<12} {str(need or '-'):>7} {b['median']:>8.0f} {e['median']:>8.0f} "
                  f"{gain:>6.1f}x  {bandtxt:>8}  {verdict}")


if __name__ == "__main__":
    main()
