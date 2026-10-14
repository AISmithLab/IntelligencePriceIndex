#!/usr/bin/env python3
"""
Step 92: one place for the deflated (real) price data.

Real prices previously lived in four places with different layouts: the
category CSVs from step 23, the composite only inside docs/data.json, the 35
narrow cells in balanced-narrow-geks.csv, and gig-level real prices only in
memory inside step 76. This step writes them to data/real-prices/ without
re-estimating anything:

  real-indices.csv          composite + 7 categories, 2020Q1-2026Q1, nominal,
                            real, SE (log) and CPI -- copied from docs/data.json,
                            the site's and the paper's source of truth
  narrow-real-indices.csv   the 35 narrow categories (copied from
                            data/pilot/balanced-narrow-geks.csv)
  gig-quarter-real-prices.csv.gz
                            gig-quarter panel built by step 76's build_panel
                            (is_gig, known category, 0 < price <= $10,000,
                            gig-quarter median), real = nominal * CPI_2020Q1 / CPI_t
  cpi-quarterly.csv         the deflator (copied from data/pilot/)

    python3 code/92-export-real-prices.py
"""
import importlib.util
import io
import json
import shutil
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "data" / "real-prices"
SERIES = ["composite", "audio", "coding", "design", "marketing", "translation",
          "video", "writing"]


def load_step76():
    sys.path.insert(0, str(BASE / "code"))
    spec = importlib.util.spec_from_file_location("m76", BASE / "code" / "76-price-model.py")
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m


def indices():
    d = json.loads((BASE / "docs" / "data.json").read_text())
    rows = []
    for i, q in enumerate(d["months"]):
        for s in SERIES:
            if s == "composite":
                nom, real, se = (d["composite_geks"][i], d["composite_geks_real"][i],
                                 d["composite_geks_se"][i])
            else:
                nom, real, se = (d["index_geks"][s][i], d["index_geks_real"][s][i],
                                 d["index_geks_se"][s][i])
            rows.append({"quarter": q, "series": s, "index_nominal": nom,
                         "index_real": real, "se_log": se, "cpi_index": d["cpi"][i],
                         "cpi_imputed": int(bool(d["cpi_imputed"][i]))})
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ix = indices()
    ix.to_csv(OUT / "real-indices.csv", index=False)
    shutil.copy(BASE / "data/pilot/balanced-narrow-geks.csv", OUT / "narrow-real-indices.csv")
    shutil.copy(BASE / "data/pilot/cpi-quarterly.csv", OUT / "cpi-quarterly.csv")

    m = load_step76()
    gq = m.build_panel()
    gq = gq.rename(columns={"price": "price_nominal", "real": "price_real_2020q1"})
    cols = ["gig_id", "category", "quarter", "price_nominal", "price_real_2020q1",
            "cpi", "reviews", "rating"]
    gq[cols].round({"price_real_2020q1": 4, "cpi": 4}).to_csv(
        OUT / "gig-quarter-real-prices.csv.gz", index=False, compression="gzip")

    last = ix[ix.quarter == ix.quarter.max()].set_index("series")
    print(f"real-indices.csv: {len(ix)} rows; {ix.quarter.min()}-{ix.quarter.max()}")
    print("  latest real:", ", ".join(f"{s} {last.index_real[s]}" for s in SERIES))
    print(f"gig-quarter-real-prices.csv.gz: {len(gq):,} rows, {gq.gig_id.nunique():,} gigs, "
          f"{gq.quarter.min()}-{gq.quarter.max()}")


if __name__ == "__main__":
    main()
