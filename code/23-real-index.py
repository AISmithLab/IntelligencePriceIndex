#!/usr/bin/env python3
"""
Step 23: Deflate the GEKS-Jevons index to real terms with BLS CPI-U.

Motivation
----------
Every IPI series published so far is in *nominal* USD. That makes the most
obvious reviewer objection -- "the price rise is just inflation" -- unanswerable
by construction (tests/findings.test.md R4). Between 2020Q1 and 2026Q1 the US
price level itself rose substantially, so some fraction of every category's
climb is the dollar, not the service.

This step does the one thing that closes that gap: divide the nominal index by
the general price level and republish, keeping both series side by side.

    Real_c,t = Nominal_c,t * (CPI_base / CPI_t)

Deflator
--------
CPI-U, US city average, all items -- the standard general-purpose deflator for
converting nominal dollars to constant dollars. Two variants are fetched:

  CPIAUCSL  seasonally adjusted    (primary)
  CPIAUCNS  not seasonally adjusted (robustness)

SA is used as the primary deflator because the IPI is compared quarter over
quarter and SA removes the within-year seasonal wave that would otherwise show
up in QoQ real changes. The two are averaged to quarters before use, which
already removes most seasonality, so the choice should barely matter -- the
script prints the max divergence rather than asserting it is small.

A note on what deflation does and does not fix: it removes *general* inflation.
It does not remove Fiverr-specific or gig-economy-specific price drift, and it
is not a control for the reputation treadmill (step 22 Test B) or for
matched-model survivorship (Test C). Those are separate corrections. Real terms
answers R4 and nothing else.

Standard errors
---------------
The deflator enters as a per-quarter constant with no sampling error attributed
to it, so on the log scale the real index is the nominal log index shifted by
-ln(CPI_t/CPI_base). The shift has zero variance, therefore the existing
bootstrap SEs in *-geks-se.csv apply unchanged to the real series. No new SE
files are written; this is deliberate, not an omission.

Caching
-------
The FRED series are cached to data/cpi-u.csv on first fetch and reused
thereafter, so reruns are offline and reproducible. Pass --refresh to re-fetch.

Inputs
------
  data/pilot/panel-category-indices-geks.csv    (nominal, base 2020Q1)
  data/pilot/recent-category-indices-geks.csv   (nominal, base 2024Q3)
  data/pilot/recent-category-weights.csv
  FRED CPIAUCSL / CPIAUCNS  (cached to data/cpi-u.csv)

Outputs
-------
  data/cpi-u.csv                                    monthly deflator cache
  data/pilot/cpi-quarterly.csv                      quarterly deflator, both variants
  data/pilot/panel-category-indices-geks-real.csv   real, base 2020Q1 = 100
  data/pilot/recent-category-indices-geks-real.csv  real, base 2024Q3 = 100
"""

import argparse
import csv
import importlib.util
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA = BASE_DIR / "data"
PILOT = DATA / "pilot"

# Step 19 owns the shared index-CSV format, quarter arithmetic and the splice /
# composite helpers; import it so the real series is written and aggregated by
# exactly the same code as the nominal one (module name starts with a digit,
# hence the explicit loader).
_spec = importlib.util.spec_from_file_location("tpd", Path(__file__).parent / "19-tpd-index.py")
tpd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tpd)

CATS = tpd.CATS
q_to_int = tpd.q_to_int

HIST_NOMINAL = PILOT / "panel-category-indices-geks.csv"
RECENT_NOMINAL = PILOT / "recent-category-indices-geks.csv"
WEIGHTS_CSV = PILOT / "recent-category-weights.csv"

HIST_REAL = PILOT / "panel-category-indices-geks-real.csv"
RECENT_REAL = PILOT / "recent-category-indices-geks-real.csv"

CPI_CACHE = DATA / "cpi-u.csv"
CPI_QUARTERLY = PILOT / "cpi-quarterly.csv"

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd=2016-01-01"
SERIES = {"cpi_sa": "CPIAUCSL", "cpi_nsa": "CPIAUCNS"}
PRIMARY = "cpi_sa"


# --------------------------------------------------------------------------
# deflator
# --------------------------------------------------------------------------

def fetch_cpi_monthly():
    """Fetch both CPI-U variants from FRED. Returns {month: {name: value}}."""
    monthly = defaultdict(dict)
    for name, sid in SERIES.items():
        url = FRED_URL.format(sid=sid)
        with urllib.request.urlopen(url, timeout=60) as resp:
            text = resp.read().decode("utf-8")
        rows = list(csv.reader(text.splitlines()))
        header = rows[0]
        # FRED's date column has been named both DATE and observation_date.
        date_i = 0
        val_i = header.index(sid) if sid in header else 1
        n = 0
        for row in rows[1:]:
            if not row or len(row) <= val_i:
                continue
            raw = row[val_i].strip()
            if raw in ("", "."):
                continue
            monthly[row[date_i][:7]][name] = float(raw)
            n += 1
        print(f"  {sid:10s} {n:4d} monthly observations")
    return monthly


def load_cpi_monthly(refresh=False):
    """Cached fetch. Returns {'YYYY-MM': {'cpi_sa': v, 'cpi_nsa': v}}."""
    if CPI_CACHE.exists() and not refresh:
        monthly = defaultdict(dict)
        with open(CPI_CACHE) as f:
            for row in csv.DictReader(f):
                for name in SERIES:
                    if row.get(name):
                        monthly[row["month"]][name] = float(row[name])
        print(f"CPI-U: {len(monthly)} months from cache {CPI_CACHE.relative_to(BASE_DIR)}")
        return monthly

    print("CPI-U: fetching from FRED ...")
    try:
        monthly = fetch_cpi_monthly()
    except (urllib.error.URLError, OSError) as e:
        if CPI_CACHE.exists():
            print(f"  fetch failed ({e}); falling back to cache", file=sys.stderr)
            return load_cpi_monthly(refresh=False)
        sys.exit(f"CPI fetch failed and no cache at {CPI_CACHE}: {e}")

    with open(CPI_CACHE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month"] + list(SERIES))
        for m in sorted(monthly):
            w.writerow([m] + [f"{monthly[m][n]:.3f}" if n in monthly[m] else "" for n in SERIES])
    print(f"  cached -> {CPI_CACHE.relative_to(BASE_DIR)}")
    return monthly


def _month_index(month):
    return int(month[:4]) * 12 + int(month[5:7]) - 1


def _month_label(idx):
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def fill_missing_months(monthly):
    """Linearly interpolate isolated missing months from their neighbours.

    The CPI-U series has a real hole: FRED carries no October 2025 observation
    (BLS did not publish a CPI-U for that month). Dropping the whole quarter
    would blank 2025Q4 out of the real index even though the underlying gig
    price data for that quarter is fine. CPI-U is smooth and near-monotone at
    monthly frequency, so interpolating a single interior month from the two
    adjacent ones is a far smaller distortion than losing the quarter -- but it
    IS an imputation, so the affected quarters are flagged in the output and
    printed on every run.

    Only isolated interior gaps are filled; runs of two or more consecutive
    missing months are left alone."""
    if not monthly:
        return monthly, []
    idx = {_month_index(m): v for m, v in monthly.items()}
    filled = []
    for i in range(min(idx) + 1, max(idx)):
        if i in idx:
            continue
        if i - 1 not in idx or i + 1 not in idx:
            continue  # not an isolated gap
        lo, hi = idx[i - 1], idx[i + 1]
        idx[i] = {n: (lo[n] + hi[n]) / 2.0 for n in SERIES if n in lo and n in hi}
        filled.append(_month_label(i))

    return {_month_label(i): v for i, v in idx.items()}, filled


def to_quarterly(monthly, imputed_months=()):
    """Average monthly CPI within each quarter. Only complete quarters are kept,
    so a partially-observed trailing quarter never produces a deflator that is
    silently based on one or two months."""
    imputed_q = set()
    for m in imputed_months:
        year, mon = int(m[:4]), int(m[5:7])
        imputed_q.add(f"{year}Q{(mon - 1) // 3 + 1}")

    buckets = defaultdict(lambda: defaultdict(list))
    for month, vals in monthly.items():
        year, mon = int(month[:4]), int(month[5:7])
        q = f"{year}Q{(mon - 1) // 3 + 1}"
        for name, v in vals.items():
            buckets[q][name].append(v)

    quarterly = {}
    for q, series in sorted(buckets.items(), key=lambda kv: q_to_int(kv[0])):
        complete = {n: sum(v) / len(v) for n, v in series.items() if len(v) == 3}
        if PRIMARY in complete:
            complete["imputed"] = 1.0 if q in imputed_q else 0.0
            quarterly[q] = complete
    return quarterly


def write_quarterly(quarterly):
    with open(CPI_QUARTERLY, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quarter"] + list(SERIES) + ["imputed_month"])
        for q in sorted(quarterly, key=q_to_int):
            w.writerow([q] + [f"{quarterly[q][n]:.4f}" if n in quarterly[q] else ""
                              for n in SERIES]
                       + [int(quarterly[q].get("imputed", 0))])


# --------------------------------------------------------------------------
# deflation
# --------------------------------------------------------------------------

def deflate(nominal_csv, quarterly, variant=PRIMARY):
    """Deflate one nominal index CSV. The base quarter is the file's own first
    quarter (where the nominal index is 100 by construction), so the real series
    is 100 at the same base and the two are directly comparable."""
    nominal = tpd.read_index_csv(nominal_csv)
    quarters = sorted({q for s in nominal.values() for q in s}, key=q_to_int)
    if not quarters:
        sys.exit(f"{nominal_csv.name}: no quarters")

    base_q = quarters[0]
    if base_q not in quarterly:
        sys.exit(f"{nominal_csv.name}: no CPI for base quarter {base_q}")
    cpi_base = quarterly[base_q][variant]

    missing = [q for q in quarters if q not in quarterly]
    if missing:
        print(f"  ! no CPI for {len(missing)} quarter(s), dropped from real series: "
              f"{', '.join(missing)}")

    real = {}
    for cat, series in nominal.items():
        out = {}
        for q, level in series.items():
            if q in quarterly:
                out[q] = level * (cpi_base / quarterly[q][variant])
        if out:
            real[cat] = out
    return real, base_q, cpi_base


def cumulative_inflation(quarterly, q0, q1, variant=PRIMARY):
    return (quarterly[q1][variant] / quarterly[q0][variant] - 1.0) * 100.0


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def annualised(level, q0, q1):
    """Annualised % growth implied by moving from 100 at q0 to `level` at q1."""
    years = (q_to_int(q1) - q_to_int(q0)) / 4.0
    if years <= 0 or level <= 0:
        return float("nan")
    return ((level / 100.0) ** (1.0 / years) - 1.0) * 100.0


def report_segment(title, nominal_csv, real, base_q, quarterly, variant=PRIMARY,
                   ref_q=None):
    """Report each category at `ref_q` if it is observed there, otherwise at that
    category's own last observed quarter. Categories drop out of the historical
    panel at different dates, so a single shared end quarter would show one or
    two categories and blank the rest."""
    nominal = tpd.read_index_csv(nominal_csv)
    quarters = sorted({q for s in real.values() for q in s}, key=q_to_int)
    if not quarters:
        return
    print(f"\n{title}  (base {base_q} = 100)")
    print(f"  {'category':<12} {'as of':>7} {'nominal':>9} {'real':>9} {'diff':>8} "
          f"{'CPI-U':>7} {'nom %/yr':>9} {'real %/yr':>10}")
    for cat in CATS:
        series = real.get(cat, {})
        if not series:
            print(f"  {cat:<12} {'-':>7} {'-':>9} {'-':>9} {'-':>8} {'-':>7} "
                  f"{'-':>9} {'-':>10}")
            continue
        end_q = ref_q if (ref_q and ref_q in series) else \
            sorted(series, key=q_to_int)[-1]
        n, r = nominal.get(cat, {}).get(end_q), series[end_q]
        if n is None:
            continue
        infl = cumulative_inflation(quarterly, base_q, end_q, variant)
        print(f"  {cat:<12} {end_q:>7} {n:>9.1f} {r:>9.1f} {r - n:>8.1f} "
              f"{infl:>6.1f}% {annualised(n, base_q, end_q):>8.1f}% "
              f"{annualised(r, base_q, end_q):>9.1f}%")


def report_composite(quarterly, weights, variant=PRIMARY):
    nom_cats, nom_comp = tpd.spliced_composite(HIST_NOMINAL, RECENT_NOMINAL, weights)
    real_cats, real_comp = tpd.spliced_composite(HIST_REAL, RECENT_REAL, weights)

    quarters = sorted(set(nom_comp) & set(real_comp), key=q_to_int)
    if not quarters:
        print("\nComposite: no overlapping quarters")
        return
    q0, q1 = quarters[0], quarters[-1]
    n1, r1 = nom_comp[q1], real_comp[q1]
    infl = cumulative_inflation(quarterly, q0, q1, variant)

    print(f"\nSpliced composite  ({q0} = 100 -> {q1})")
    print(f"  nominal {n1:.1f}  ({n1 - 100:+.1f}%)")
    print(f"  real    {r1:.1f}  ({r1 - 100:+.1f}%)")
    print(f"  CPI-U   +{infl:.1f}% over the same window")
    nom_rise, real_rise = n1 - 100.0, r1 - 100.0
    if nom_rise > 0:
        # Share OF THE RISE that deflation removes -- not the share of the level.
        share = (nom_rise - real_rise) / nom_rise * 100.0
        print(f"  => general inflation accounts for {share:.0f}% of the nominal rise "
              f"({nom_rise:+.1f} pts -> {real_rise:+.1f} pts real);")
        print(f"     the IPI still outpaces CPI-U, but by {real_rise:+.1f}%, not "
              f"{nom_rise:+.1f}%.")
    return nom_comp, real_comp


def report_variant_divergence(quarterly):
    """SA vs NSA: report the largest gap rather than assuming it is negligible."""
    worst_q, worst = None, 0.0
    for q, vals in quarterly.items():
        if "cpi_nsa" not in vals:
            continue
        gap = abs(vals["cpi_sa"] / vals["cpi_nsa"] - 1.0) * 100.0
        if gap > worst:
            worst_q, worst = q, gap
    if worst_q:
        print(f"\nDeflator check: max SA-vs-NSA gap {worst:.2f}% ({worst_q}). "
              f"Primary = {SERIES[PRIMARY]}.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refresh", action="store_true", help="re-fetch CPI from FRED")
    args = ap.parse_args()

    monthly = load_cpi_monthly(refresh=args.refresh)
    monthly, imputed = fill_missing_months(monthly)
    if imputed:
        print(f"  ! CPI-U has no observation for {', '.join(imputed)}; "
              f"interpolated from adjacent months (flagged in {CPI_QUARTERLY.name})")
    quarterly = to_quarterly(monthly, imputed)
    write_quarterly(quarterly)
    qs = sorted(quarterly, key=q_to_int)
    print(f"CPI-U quarterly: {len(qs)} complete quarters, {qs[0]} - {qs[-1]}")
    report_variant_divergence(quarterly)

    print("\n" + "=" * 74)
    print("DEFLATING GEKS-JEVONS TO REAL TERMS")
    print("=" * 74)

    hist_real, hist_base, _ = deflate(HIST_NOMINAL, quarterly)
    recent_real, recent_base, _ = deflate(RECENT_NOMINAL, quarterly)
    tpd.write_index_csv(HIST_REAL, hist_real)
    tpd.write_index_csv(RECENT_REAL, recent_real)

    # 2024Q3 is the recent segment's base and the splice point, so it is the
    # quarter every historical category is most likely to reach and the one the
    # project already quotes elsewhere.
    report_segment("HISTORICAL segment", HIST_NOMINAL, hist_real, hist_base,
                   quarterly, ref_q=recent_base)
    report_segment("RECENT segment", RECENT_NOMINAL, recent_real, recent_base, quarterly)

    weights = {}
    with open(WEIGHTS_CSV) as f:
        for row in csv.DictReader(f):
            weights[row["category"]] = float(row["weight"])
    report_composite(quarterly, weights)

    print(f"\nWrote {HIST_REAL.name}, {RECENT_REAL.name}, {CPI_QUARTERLY.name}")
    print("Bootstrap SEs in *-geks-se.csv apply unchanged (the deflator adds no variance).")


if __name__ == "__main__":
    main()
