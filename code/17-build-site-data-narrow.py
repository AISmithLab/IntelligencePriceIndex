#!/usr/bin/env python3
"""
Step 17: Build docs/data.json showing BOTH the main (broad) categories AND the
relevant subcategories underneath them.

  - MAIN categories are the full broad domains (every gig in the domain), computed
    exactly like the production broad build — these form the basket/composite, so
    the headline stays robust.
  - SUBCATEGORIES are detail lines nested under their parent. A subcat earns a line
    only if it BOTH moves (index range >= MOVE_MIN) AND is well-covered
    (>= COV_BAR/12 chainable months). They are NOT added to the composite weight
    (their gigs are already counted inside the parent) — the front-end excludes
    `level == "sub"` from the composite to avoid double-counting.

Each category carries `level` (main|sub), `parent`, `label`, `color`. Subcats are a
shade of the parent's hue; main domains are the darker base shade.

To revert the site to a pure broad build: re-run `python3 code/15-build-site-data.py`.
"""

import importlib.util
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
NARROW_MANIFEST = BASE_DIR / "data" / "pilot" / "recent-manifest-narrow.tsv"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOVE_MIN = 1.5   # min index range (max-min, in points): the line must visibly move
COV_BAR = 7      # min chainable months (of 12): so the movement is real, not a few-pair fluke


def _series_range(arr):
    vals = [v for v in arr if v is not None]
    return (max(vals) - min(vals)) if vals else 0.0


def main():
    sub = _load("subclassify_narrow", BASE_DIR / "code" / "16-subclassify-narrow.py")
    site = _load("build_site_data", BASE_DIR / "code" / "15-build-site-data.py")

    # 1. build the FULL narrow index once, then keep only subcats that BOTH move
    #    (range >= MOVE_MIN) AND are well-covered (>= COV_BAR/12 chainable months).
    #    Movement alone admits noise (e.g. a +14% swing off ~4 covered months);
    #    coverage alone admits dead-flat lines (matched pairs with unchanged prices).
    #    A subcat must clear both to earn its own line; everything else collapses
    #    back into its broad parent, which keeps that bucket's real movement.
    sub.write_narrow_manifest(keep=None)
    full = site.build_site_data(manifest=NARROW_MANIFEST)
    cov = sub.measure_coverage()
    ranges = {c: _series_range(full["index"][c]) for c in full["categories"]}
    keep = {c for c in full["categories"]
            if "-" in c and not c.endswith("-other")
            and ranges[c] >= MOVE_MIN and cov.get(c, 0) >= COV_BAR}

    print(f"Relevant subcats (move >= {MOVE_MIN} pts AND coverage >= {COV_BAR}/12): {len(keep)}")
    for c in sorted(full["categories"], key=lambda x: -ranges[x]):
        if "-" not in c or c.endswith("-other"):
            continue
        ok_m, ok_c = ranges[c] >= MOVE_MIN, cov.get(c, 0) >= COV_BAR
        tag = "keep " if (c in keep) else "drop "
        why = "" if c in keep else ("(flat)" if not ok_m else "(noisy/thin coverage)")
        print(f"  {tag} {c:26s} range={ranges[c]:5.1f}  cov={cov.get(c,0):2d}/12  {why}")
    print("  (collapsed gigs + every other domain stay under their broad parent)\n")

    # 2. MAIN basket: the production broad build (full domains, robust composite)
    data = site.build_site_data()           # default broad manifest
    meta = sub.category_meta()
    main_cats = list(data["categories"])

    level = {c: "main" for c in main_cats}
    parent = {c: c for c in main_cats}
    labels = {c: meta.get(c, {}).get("label", c.capitalize()) for c in main_cats}
    colors = {c: meta.get(c, {}).get("color", "#888") for c in main_cats}

    # 3. graft the relevant subcats (from the full-narrow build) as detail rows,
    #    only when their parent domain is present in the main basket.
    sub_cats = [c for c in keep if meta.get(c, {}).get("parent") in main_cats]
    for c in sorted(sub_cats, key=lambda x: (meta[x]["parent"], -ranges[x])):
        data["index"][c] = full["index"][c]
        data["weights"][c] = full["weights"].get(c, 0.0)   # display only; not in composite
        data["panel_gigs"][c] = full["panel_gigs"].get(c, 0)
        data["delta12"][c] = full["delta12"].get(c)
        level[c] = "sub"
        parent[c] = meta[c]["parent"]
        labels[c] = meta[c]["label"]
        colors[c] = meta[c]["color"]

    data["categories"] = main_cats + sub_cats   # composite_all already = broad (main) composite
    data["level"] = level
    data["parents"] = parent
    data["labels"] = labels
    data["colors"] = colors

    site.write_and_report(data)
    print(f"\nMain categories ({len(main_cats)}): {', '.join(main_cats)}")
    print(f"Subcategory detail lines ({len(sub_cats)}): " +
          (', '.join(f'{c} (parent {parent[c]})' for c in sub_cats) or 'none'))


if __name__ == "__main__":
    main()
