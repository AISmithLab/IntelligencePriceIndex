#!/usr/bin/env python3
"""
Step 98: broad-category price trajectories on the balanced panel, 2020Q1-2024Q4,
with 95% bands and the +/-5% adequacy check, on the post-TD6 data.

Nothing is re-implemented: the panel, the 7-category split, GEKS-Jevons, the
bootstrap and the CPI-U deflator all come from step 66 (`build(level="category")`).
Step 66's own `--broad` flag would overwrite `balanced-narrow-geks.csv`, so this
step calls `build` directly and writes its own file.

Band convention matches the site (`docs/ipi.js`, halfWidth = 1.96 * se_log, read
as +/- percent); the exact asymmetric band on the level, 100 * exp(ln I +/- 1.96 se),
is carried alongside. A category-quarter "meets 5%" when 1.96 * se_log <= 0.05.

Run:  python3 code/98-broad-trajectories.py [--boot N]
Writes data/pilot/balanced-broad-trajectories.csv and runs/broad-trajectories/report.md
"""

import argparse
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_CSV = BASE_DIR / "data" / "pilot" / "balanced-broad-trajectories.csv"
REPORT = BASE_DIR / "runs" / "broad-trajectories" / "report.md"
Z = 1.96
TARGET = 0.05


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, BASE_DIR / "code" / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


s66 = _load("s66", "66-narrow-real-geks.py")


def long_table(nom, real, se):
    rows = []
    for c in nom.columns:
        for q in nom.index:
            if pd.isna(nom.at[q, c]):
                continue
            s = float(se.at[q, c]) if not pd.isna(se.at[q, c]) else np.nan
            hw = Z * s
            rows.append({
                "category": c, "quarter": q,
                "index_nominal": nom.at[q, c], "index_real": real.at[q, c],
                "se_log": s, "half_width_pct": 100 * hw,
                "real_lo": real.at[q, c] * np.exp(-hw), "real_hi": real.at[q, c] * np.exp(hw),
                "nominal_lo": nom.at[q, c] * np.exp(-hw), "nominal_hi": nom.at[q, c] * np.exp(hw),
                "meets_5pct": bool(hw <= TARGET) if q != nom.index[0] else "",
            })
    return pd.DataFrame(rows)


def report(df, diag, n_gigs, n_boot, cpi_rise):
    last = df.quarter.max()
    t = df[df.quarter == last].set_index("category")
    body = df[df.quarter != df.quarter.min()]
    lines = [
        "# Broad-category trajectories, balanced panel, 2020Q1-2024Q4 (post-TD6)",
        "",
        f"Built by `code/98-broad-trajectories.py` (estimator from step 66). {n_gigs:,} gigs, "
        f"{n_boot} bootstrap draws, 2020Q1 = 100. CPI-U (SA) over the window: {cpi_rise:+.1f}%.",
        "Band = 95% (1.96 x bootstrap SE of the log index); meets 5% when the half-width <= 5%.",
        "",
        "## 2024Q4 endpoint",
        "",
        "| category | gigs | density | nominal | real | real 95% band | half-width | meets ±5% at 2024Q4 | quarters meeting ±5% (of 19) |",
        "|---|---:|---:|---:|---:|---|---:|---|---:|",
    ]
    for c in t.index:
        r, d = t.loc[c], diag.set_index("category").loc[c]
        k = int((body[body.category == c].meets_5pct == True).sum())  # noqa: E712
        lines.append(
            f"| {c} | {int(d.gigs):,} | {d.pair_density:.2f} | {r.index_nominal - 100:+.1f}% | "
            f"{r.index_real - 100:+.1f}% | [{r.real_lo - 100:+.1f}%, {r.real_hi - 100:+.1f}%] | "
            f"±{r.half_width_pct:.1f}% | {'**yes**' if r.meets_5pct else 'no'} | {k} |")
    lines += ["", "## Real index by quarter (half-width in brackets; * = meets ±5%)", ""]
    piv = df.pivot(index="quarter", columns="category", values="index_real")
    hw = df.pivot(index="quarter", columns="category", values="half_width_pct")
    lines.append("| quarter | " + " | ".join(piv.columns) + " |")
    lines.append("|---|" + "---:|" * len(piv.columns))
    for q in piv.index:
        cells = []
        for c in piv.columns:
            h = hw.at[q, c]
            star = "*" if h <= 100 * TARGET and q != piv.index[0] else ""
            cells.append(f"{piv.at[q, c]:.1f} (±{h:.1f}){star}")
        lines.append(f"| {q} | " + " | ".join(cells) + " |")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--boot", type=int, default=s66.N_BOOT)
    args = ap.parse_args()
    nom, real, se, diag, cpi, w = s66.build(level="category", n_boot=args.boot)
    df = long_table(nom, real, se)
    df.round(4).to_csv(OUT_CSV, index=False)
    cpi_rise = 100 * (cpi[nom.index[-1]] / cpi[s66.START_Q] - 1)
    report(df, diag, w.gig_id.nunique(), args.boot, cpi_rise)
    print(REPORT.read_text())
    print(f"Wrote {OUT_CSV} ({len(df)} rows) and {REPORT}")


if __name__ == "__main__":
    main()
