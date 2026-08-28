#!/usr/bin/env python3
"""
Step 66: Fine-grained (narrow) GEKS-Jevons indices on the balanced panel, in
BOTH nominal and CPI-U-deflated (real) terms.

Motivation
----------
Two gaps in what the notebook's section 7 plotted.

1. It was NOMINAL. The GEKS bilaterals are formed over raw listed USD, so every
   category line carried general US inflation inside it -- over the notebook's
   2020Q1..2024Q4 window CPI-U (SA) itself rose 22.3%. Step 23 already publishes
   the deflated series for the *site* panels; nothing carried the deflator onto
   the balanced panel. This step does, using the identical definition:

       Real_c,t = Nominal_c,t * (CPI_base / CPI_t)

   As step 23 argues, the deflator enters as a per-quarter constant with no
   sampling error attributed to it, so on the log scale the real index is the
   nominal log index shifted by a zero-variance constant: the bootstrap SEs
   computed for the nominal series apply unchanged to the real one. No separate
   real SEs are bootstrapped; that is deliberate.

2. It was at the 7 broad domains. Step 16 already owns a finer taxonomy -- it
   keyword-matches the gig slug *within* its broad parent -- but only the recent
   monthly manifest was ever run through it, where step 16's own coverage
   warning applies (most subcategories are too thin to chain monthly). The
   balanced panel is quarterly and matched-model, which is a much easier gate:
   all 35 narrow buckets clear 20/20 quarters at pair_density 1.00. So the
   subdivision is imported from step 16, not re-invented here, and applied to
   the balanced panel's gig ids.

The residual `<broad>-other` buckets are kept as first-class categories rather
than dropped -- for video and translation they are the largest bucket in the
family, so dropping them would hide most of the gigs. They are labelled as
remainders so nobody reads them as a named niche.

Library use (imported by notebooks/00-explore.ipynb section 7):
    add_narrow, nested_by, geks_table, load_deflator, deflate
CLI:
    python3 code/66-narrow-real-geks.py [--boot N] [--broad]
        writes data/pilot/balanced-narrow-geks.csv and prints the summary table
"""

import argparse
import csv
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PILOT = BASE_DIR / "data" / "pilot"

PRICES_CSV = PILOT / "balanced-prices.csv"
CATEGORY_CSV = PILOT / "balanced-gig-category.csv.gz"
CPI_QUARTERLY = PILOT / "cpi-quarterly.csv"
OUT_CSV = PILOT / "balanced-narrow-geks.csv"

START_Q, END_Q = "2020Q1", "2024Q4"
N_BOOT = 200
SEED = 7
MIN_GIGS = 100          # a narrow bucket below this is folded back into its parent


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, BASE_DIR / "code" / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The estimator, the panel builder and the taxonomy are all imported, never
# re-implemented, so this step can only differ from the papers by the deflator
# and the category split.
esm = _load("es", "64-event-study-twfe.py")     # build_panel, q_to_int
geks = _load("geks", "21-geks-index.py")        # geks_index, MIN_MATCH
narrow = _load("narrow", "16-subclassify-narrow.py")  # subclassify, category_meta
tpd = geks.tpd                                  # CATS

CATS = tpd.CATS
q_to_int = esm.q_to_int


# --------------------------------------------------------------------------
# deflator
# --------------------------------------------------------------------------

def load_deflator(path=CPI_QUARTERLY, variant="cpi_sa"):
    """quarterly CPI-U -> ({quarter: level}, {quarter: contains_imputed_month}).

    Written by step 23 from FRED CPIAUCSL/CPIAUCNS. `imputed` marks quarters
    whose average includes an interpolated month (no October 2025 CPI-U was
    published); the site flags those rather than pretending they are observed.
    """
    cpi, imputed = {}, {}
    with open(path) as f:
        for row in csv.DictReader(f):
            if row.get(variant):
                cpi[row["quarter"]] = float(row[variant])
                imputed[row["quarter"]] = row.get("imputed_month") == "1"
    return cpi, imputed


def deflate(idx, cpi, base_q):
    """Nominal index levels -> real, holding the base quarter at its nominal value.

    idx: {quarter: level}. Quarters with no deflator are dropped, not carried.
    """
    base_cpi = cpi.get(base_q)
    if base_cpi is None:
        raise ValueError(f"no CPI-U for base quarter {base_q}")
    return {q: v * base_cpi / cpi[q] for q, v in idx.items() if q in cpi}


def cpi_rebased(cpi, quarters, base_q):
    """CPI-U itself on the index's own base, so it can be drawn as a reference."""
    base_cpi = cpi[base_q]
    return {q: 100.0 * cpi[q] / base_cpi for q in quarters if q in cpi}


# --------------------------------------------------------------------------
# fine-grained categories
# --------------------------------------------------------------------------

def slug_of(gig_id):
    return gig_id.split("/", 1)[1] if "/" in gig_id else gig_id


def add_narrow(gq, min_gigs=MIN_GIGS):
    """Tidy gig-quarter panel -> same panel with a `narrow` column.

    Step 16's `subclassify` decides the bucket. A bucket holding fewer than
    `min_gigs` distinct gigs is folded into its parent's remainder rather than
    being indexed on a handful of matched pairs.
    """
    d = gq.copy()
    d["narrow"] = [narrow.subclassify(c, slug_of(g))
                   for g, c in zip(d.gig_id, d.category)]
    sizes = d.groupby("narrow").gig_id.nunique()
    thin = {c for c, n in sizes.items() if n < min_gigs}
    if thin:
        d["narrow"] = [f"{c.split('-', 1)[0]}-other" if c in thin else c
                       for c in d.narrow]
    d.attrs["folded"] = sorted(thin)
    return d


def narrow_labels():
    """narrow id -> (display label, parent, colour), from step 16's palette."""
    meta = narrow.category_meta()
    return {cid: (m["label"], m["parent"], m["color"]) for cid, m in meta.items()}


def order_narrow(cats):
    """Family-major ordering: parents in CATS order, remainder bucket last."""
    def key(c):
        parent = c.split("-", 1)[0]
        return (CATS.index(parent) if parent in CATS else 99,
                c.endswith("-other"), c)
    return sorted(cats, key=key)


# --------------------------------------------------------------------------
# indices
# --------------------------------------------------------------------------

def nested_by(gq, col="narrow", price_col="price_basic"):
    """Tidy panel -> {category: {gig: {quarter: price}}}, the shape step 21 takes."""
    out = {}
    for (gid, cat), sub in gq.groupby(["gig_id", col], observed=True):
        out.setdefault(cat, {})[gid] = dict(zip(sub.quarter, sub[price_col]))
    return out


def geks_table(nested, cpi, n_boot=N_BOOT, seed=SEED, window_start=START_Q):
    """{category: panel} -> (nominal df, real df, log-SE df, diagnostics df).

    Every category is indexed on its own base quarter = `window_start` = 100,
    which is also the quarter the deflator is normalised on, so nominal and real
    start together and the gap between them at quarter t IS the CPI-U rise from
    the base to t. Real levels reuse the nominal bootstrap SEs (see module
    docstring).
    """
    rng = np.random.default_rng(seed)
    nom, real, ses, diags = {}, {}, {}, []
    for c in sorted(nested):
        idx, se, diag = geks.geks_index(nested[c], rng=rng, n_boot=n_boot,
                                        window_start=window_start)
        if len(idx) < 2:
            diags.append({"category": c, **diag, "kept": False})
            continue
        nom[c], ses[c] = idx, se
        real[c] = deflate(idx, cpi, window_start)
        diags.append({"category": c, **diag, "kept": True})

    def _df(d):
        return (pd.DataFrame(d).sort_index(key=lambda s: s.map(q_to_int))
                  if d else pd.DataFrame())

    return _df(nom), _df(real), _df(ses), pd.DataFrame(diags)


def build(prices=PRICES_CSV, categories=CATEGORY_CSV, level="narrow",
          start=START_Q, end=END_Q, n_boot=N_BOOT, seed=SEED, min_gigs=MIN_GIGS):
    """End-to-end: prices CSV -> (nominal, real, se, diagnostics, deflator, panel)."""
    gq = esm.build_panel(prices, categories)
    w = gq[(gq.qi >= q_to_int(start)) & (gq.qi <= q_to_int(end))]
    w = add_narrow(w, min_gigs=min_gigs)
    cpi, _ = load_deflator()
    nom, real, se, diag = geks_table(nested_by(w, level), cpi,
                                     n_boot=n_boot, seed=seed, window_start=start)
    return nom, real, se, diag, cpi, w


def write_csv(nom, real, se, path=OUT_CSV):
    """Long format: one row per (category, quarter), nominal + real + log SE."""
    rows = []
    for c in nom.columns:
        for q in nom.index:
            v = nom.at[q, c]
            if pd.isna(v):
                continue
            rows.append({"category": c, "quarter": q,
                         "index_nominal": round(float(v), 3),
                         "index_real": round(float(real.at[q, c]), 3)
                                       if c in real and not pd.isna(real.at[q, c]) else "",
                         "se_log": round(float(se.at[q, c]), 5)
                                   if c in se and not pd.isna(se.at[q, c]) else ""})
    with open(path, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["category", "quarter", "index_nominal",
                                           "index_real", "se_log"])
        wr.writeheader()
        wr.writerows(rows)
    return path, len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--boot", type=int, default=N_BOOT, help="bootstrap draws (0 to skip)")
    ap.add_argument("--broad", action="store_true", help="index the 7 broad domains instead")
    ap.add_argument("--start", default=START_Q)
    ap.add_argument("--end", default=END_Q)
    args = ap.parse_args()

    level = "category" if args.broad else "narrow"
    nom, real, se, diag, cpi, w = build(level=level, start=args.start,
                                        end=args.end, n_boot=args.boot)
    labels = narrow_labels()
    last = nom.index[-1]
    cpi_rise = 100.0 * (cpi[last] / cpi[args.start] - 1)

    print(f"{level} GEKS-Jevons, {args.start}=100 .. {last}, "
          f"{w.gig_id.nunique():,} gigs, {args.boot} bootstrap draws")
    print(f"CPI-U (SA) over the same window: {cpi_rise:+.1f}%\n")
    print(f"{'category':26s} {'gigs':>6s} {'q':>3s} {'dens':>5s} "
          f"{'nominal':>9s} {'real':>9s}")
    print("-" * 64)
    for c in order_narrow(nom.columns):
        d = diag[diag.category == c].iloc[0]
        print(f"{labels.get(c, (c,))[0][:26]:26s} {int(d.gigs):6,d} "
              f"{int(d.quarters_out):3d} {d.pair_density:5.2f} "
              f"{nom.at[last, c] - 100:+8.1f}% {real.at[last, c] - 100:+8.1f}%")

    if w.attrs.get("folded"):
        print("\nfolded into their parent remainder (< %d gigs): %s"
              % (MIN_GIGS, ", ".join(w.attrs["folded"])))
    path, n = write_csv(nom, real, se)
    print(f"\nWrote {path} ({n:,} rows)")


if __name__ == "__main__":
    main()
