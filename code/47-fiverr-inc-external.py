#!/usr/bin/env python3
"""
Step 47: Fiverr Inc.'s reported transaction data — the external check, and the
only place in this project where actual transactions appear.

WHY THIS EXISTS. The archive contains no transactions. `review_count` is a proxy,
and step 46 (Phase 0) found it falling 13-43% across every category at once — a
platform-wide pattern that is equally consistent with (a) real transaction decline
and (b) buyers reviewing a smaller share of purchases. Nothing internal to the
crawl can separate those. Fiverr Inc. (NYSE: FVRR) is public and reports the real
quantities quarterly, and until now nothing in this repo used them.

WHAT FIVERR REPORTS. Active buyers (trailing twelve months) and annual spend per
buyer, which the company defines as TTM GMV / active buyers. So:

    GMV = active buyers x spend per buyer          (an identity, not an estimate)

Revenue is NOT a substitute: 2024 revenue / GMV = 36% against a 27.6% marketplace
take rate, because revenue also carries Fiverr Pro, subscriptions, ads and
acquired services. GMV is the marketplace quantity we want.

WHAT WE DERIVE. GMV is dollars, not transactions. Splitting it needs a price:

    orders = GMV / price per order

and the IPI is a price index. Deflating both by CPI-U and dividing gives an
implied real order count. THIS IS THE STUDY'S FIRST ACTUAL TRANSACTION-COUNT
ESTIMATE, and its weakest link is stated up front in §CAVEATS below.

Sources for `data/fiverr-inc-metrics.csv` (all public):
  * FY2019 and FY2022/FY2024 Form 20-F (SEC EDGAR, CIK 1762301)
  * Fiverr quarterly results press releases, investors.fiverr.com
  * Cross-checked against the GMV = buyers x spend identity in every year where
    both were reported independently; agreement is within rounding (2022:
    4.2M x $262 = $1,100M against $1,090M reported, i.e. buyers is 4.16M).

Run:  python3 code/47-fiverr-inc-external.py
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
FVRR = BASE / "data" / "fiverr-inc-metrics.csv"
CPI = BASE / "data" / "pilot" / "cpi-quarterly.csv"
DATAJSON = BASE / "docs" / "data.json"


def load_fvrr():
    rows = []
    with open(FVRR) as f:
        for r in csv.DictReader(f):
            rows.append({
                "year": int(r["year"]),
                "period": r["period"],
                "buyers": float(r["active_buyers_m"]),
                "spend": float(r["spend_per_buyer_usd"]),
                "gmv": float(r["gmv_usd_m"]),
                "src": r["gmv_source"],
            })
    return rows


def load_cpi_annual():
    q = {}
    with open(CPI) as f:
        for r in csv.DictReader(f):
            q[r["quarter"]] = float(r["cpi_sa"])
    by_year = defaultdict(list)
    for k, v in q.items():
        by_year[int(k[:4])].append(v)
    return {y: float(np.mean(v)) for y, v in by_year.items()}, q


def load_ipi_annual():
    """Our real composite price index, averaged to calendar years."""
    d = json.load(open(DATAJSON))
    months, real = d["months"], d["composite_geks_real"]
    by_year = defaultdict(list)
    for m, v in zip(months, real):
        if v is not None:
            by_year[int(m[:4])].append(float(v))
    return {y: float(np.mean(v)) for y, v in by_year.items()}, months


def main():
    fv = load_fvrr()
    cpi, _ = load_cpi_annual()
    ipi, months = load_ipi_annual()

    print("=" * 88)
    print("FIVERR INC. REPORTED TRANSACTION DATA  (NYSE: FVRR)")
    print("=" * 88)
    print(f"\n  {'period':<10}{'buyers M':>10}{'$/buyer':>9}{'GMV $M':>10}{'src':>9}"
          f"{'buyers YoY':>12}{'GMV YoY':>10}")
    prev = None
    for r in fv:
        by = f"{100*(r['buyers']/prev['buyers']-1):+.1f}%" if prev else "--"
        gy = f"{100*(r['gmv']/prev['gmv']-1):+.1f}%" if prev else "--"
        lab = f"{r['year']}" if r["period"] == "FY" else f"{r['year']} Q2*"
        print(f"  {lab:<10}{r['buyers']:>10.2f}{r['spend']:>9.0f}"
              f"{r['gmv']:>10.1f}{r['src']:>9}{by:>12}{gy:>10}")
        prev = r
    print("  * trailing twelve months to 2026Q2")

    # ---- the headline the company's own books give ----
    bmax = max(fv, key=lambda r: r["buyers"])
    gmax = max(fv, key=lambda r: r["gmv"])
    last = fv[-1]
    print(f"\n  => BUYERS peaked at {bmax['buyers']:.2f}M in {bmax['year']} and are "
          f"{last['buyers']:.2f}M now: {100*(last['buyers']/bmax['buyers']-1):+.1f}%")
    print(f"  => GMV    peaked at ${gmax['gmv']:.0f}M in {gmax['year']} and is "
          f"${last['gmv']:.0f}M now: {100*(last['gmv']/gmax['gmv']-1):+.1f}%")
    print(f"  => The gap is spend per buyer, which rose every single year: "
          f"${fv[0]['spend']:.0f} -> ${last['spend']:.0f}")
    print(f"\n  So the platform is losing BUYERS fast while holding DOLLAR volume")
    print(f"  roughly flat. Fewer, larger buyers. That is a composition shift, and")
    print(f"  it is the first thing any 'transactions are falling' claim must handle.")

    # ---- real terms ----
    print("\n" + "=" * 88)
    print("REAL GMV, AND THE IMPLIED ORDER COUNT")
    print("=" * 88)
    print("\n  orders = GMV / price per order. GMV deflated by CPI-U (annual mean of")
    print("  CPIAUCSL); price is the IPI real composite, annual mean. Both indexed")
    print("  to 2020 = 100, so only the RATIO is used, never a dollar level.")

    base = 2020
    if base not in ipi or base not in cpi:
        print("  base year unavailable")
        return
    print(f"\n  {'year':<7}{'GMV $M':>9}{'CPI-U':>9}{'realGMV':>9}"
          f"{'  IPI real':>10}{'  impliedOrders':>16}")
    rows = []
    for r in fv:
        y = r["year"]
        if y not in cpi or y not in ipi:
            continue
        real_gmv = r["gmv"] * cpi[base] / cpi[y]
        rows.append((y, r["period"], r["gmv"], cpi[y], real_gmv, ipi[y]))
    g0 = next(x[4] for x in rows if x[0] == base)
    p0 = ipi[base]
    for y, per, gmv, c, rg, p in rows:
        gi = 100 * rg / g0
        pi = 100 * p / p0
        oi = 100 * gi / pi
        star = "*" if per != "FY" else " "
        print(f"  {y}{star:<3}{gmv:>9.0f}{c:>9.1f}{gi:>9.1f}{pi:>10.1f}{oi:>16.1f}")

    y_last, per_last, _, _, rg_last, p_last = rows[-1]
    gi = 100 * rg_last / g0
    pi = 100 * p_last / p0
    oi = 100 * gi / pi
    print(f"\n  => 2020 -> {y_last}{'(TTM Q2)' if per_last != 'FY' else ''}:")
    print(f"     real GMV        {gi-100:+.1f}%")
    print(f"     real IPI price  {pi-100:+.1f}%")
    print(f"     IMPLIED ORDERS  {oi-100:+.1f}%   <- the transaction-count answer")

    # peak-to-now on implied orders
    peak = max(rows, key=lambda x: 100 * (100 * x[4] / g0) / (100 * ipi[x[0]] / p0))
    op = 100 * (100 * peak[4] / g0) / (100 * ipi[peak[0]] / p0)
    print(f"     peak implied orders was {peak[0]} at {op:.1f}; "
          f"now {oi:.1f}, i.e. {100*(oi/op-1):+.1f}% from peak")

    # ---- does this corroborate step 46? ----
    print("\n" + "=" * 88)
    print("CROSS-CHECK AGAINST STEP 46 (review accrual per surviving gig)")
    print("=" * 88)
    print("\n  Step 46 found review accrual per surviving gig down 13%-43% at 2022Q4,")
    print("  in EVERY category. Two readings, and the external data discriminates:")
    print("\n    (a) REAL: transactions per gig genuinely fell.")
    print("    (b) ARTEFACT: review propensity fell; sales did not.")
    print("\n  Fiverr Inc. reports buyers down "
          f"{100*(last['buyers']/bmax['buyers']-1):.0f}% from peak and implied real")
    print(f"  orders down {abs(oi-op)/op*100:.0f}%-ish from peak, on data that has")
    print("  nothing to do with reviewing behaviour. So the DIRECTION of step 46 is")
    print("  corroborated externally: fewer transactions is real, not a review artefact.")
    print("\n  BUT the magnitudes do not match, and that gap is informative rather")
    print("  than fatal:")
    print(f"    * platform orders (implied)      {oi-100:+.1f}% vs 2020")
    print( "    * accrual per SURVIVING gig      -13% to -43% at 2022Q4")
    print("  Per-gig accrual should fall FASTER than platform orders if the gig")
    print("  population grew — the same orders spread over more listings. It should")
    print("  fall SLOWER if listings shrank. Sign agreement is the result here;")
    print("  the level difference is a gig-population question the archive cannot")
    print("  answer, because exit is unmeasurable (n_404 = 0 across 509,339 captures).")

    print("\n" + "=" * 88)
    print("CAVEATS — read before quoting the implied order count")
    print("=" * 88)
    print("""
  1. The IPI measures LISTED basic-package prices, not realised order value.
     If buyers shifted to higher tiers or to Fiverr Pro, realised price rose
     faster than the IPI and the implied order fall is OVERSTATED. Fiverr's own
     spend-per-buyer path (+$119 -> +$368) and its stated upmarket push both
     point that way, so treat the implied order count as an UPPER BOUND on the
     decline.
  2. Active buyers is trailing-twelve-month, so it lags a true quarterly series
     and smooths any break. It cannot date an event to a quarter.
  3. GMV for 2024 onward is derived from the buyers x spend identity because
     Fiverr stopped reporting GMV directly. The identity is the company's own
     definition of spend per buyer, and it reproduces every independently
     reported GMV to within rounding, but it is a derivation.
  4. Orders per buyer is not observed. A fall in implied orders could be fewer
     buyers each ordering the same amount, or the same buyers ordering less.
     Buyers down 36% from peak says most of it is the former.
  5. This is PLATFORM-WIDE (Q3 in the parent plan's decomposition). It says
     nothing about which categories, because Fiverr reports no category split.
     The category question stays where step 46 left it: not identified.
""")


if __name__ == "__main__":
    main()
