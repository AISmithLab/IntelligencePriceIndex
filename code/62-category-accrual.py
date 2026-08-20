#!/usr/bin/env python3
"""
Step 62: the per-category sales proxy AS A SERIES, quarter by quarter.

WHY THIS EXISTS, AND WHAT IT CANNOT DO. Step 46 estimated a per-category BREAK at
2022Q4 (-13% to -43%) but never wrote the underlying series, and Fiverr Inc.
publishes no category split of GMV or buyers at all, so the platform-level
transaction count of step 47 cannot be decomposed. The only category-level
quantity this project has is within-gig review accrual, and this step reports it
over time rather than as a single break.

THE IDENTIFICATION PROBLEM, STATED UP FRONT. Within a gig, age and calendar
quarter move together one-for-one (age = t - birth, and birth is fixed within the
gig). So gig FE + age FE + quarter FE is EXACTLY collinear in its linear
component: the classic age-period-cohort problem. The consequence for reading
anything below:

  * the RAW series confounds calendar time with panel composition AND aging;
  * the WITHIN-GIG series (gig FE + quarter FE) removes composition but still
    confounds calendar time with aging, because the panel ages as it runs;
  * the AGE-ADJUSTED series removes the SHAPE of the age profile but cannot
    remove its linear part -- only deviations from trend are identified.

This is exactly why step 46 reports a break under a linear-trend assumption
rather than a series, and why nothing here is a causal estimate or a demand
series. It is a descriptive exhibit with its trend explicitly not identified.

Outcome is step 46's pre-registered one, y = ln(1 + reviews per quarter), and the
frame, the panel builder and the accrual transitions are imported from step 46 so
the two steps cannot drift apart.

Run:  python3 code/62-category-accrual.py
Output: runs/category-accrual.out, data/pilot/category-accrual.csv
"""

import csv
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CODE = ROOT / "code"
OUT_RUN = ROOT / "runs" / "category-accrual.out"
OUT_CSV = ROOT / "data" / "pilot" / "category-accrual.csv"
DATAJSON = ROOT / "docs" / "data.json"

# Quarters before this are reported but SHADED on the site: 2018Q4-2019Q3 hold
# 4.1k-5.9k accrual observations against 9k-11k later, and the raw rates swing
# sixfold across them. Drawing them unmarked would show noise as history.
THIN_UNTIL = "2019Q3"

MIN_OBS = 60          # a category-quarter cell below this is reported as absent
# Index base. NOT a single quarter: 2018Q4-2019Q3 hold 4.1k-5.9k accrual
# observations against 9k-11k later, and the raw category rates swing by 6x across
# them (audio 71.4 in 2019Q3 against 11.0 in 2019Q4), so any one early quarter as
# a base sets the level of every later number by its own noise. The four quarters
# of 2020 are the first dense stretch, and 2020 = 100 also matches the base of the
# platform-level transaction series in step 47, so the two can be read together.
BASE_QS = ["2020Q1", "2020Q2", "2020Q3", "2020Q4"]


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, CODE / fn)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


m46 = _load("m46", "46-balanced-demand.py")
CATS, qi, absorb2 = m46.CATS, m46.qi, m46.absorb2

out = []
def say(s=""):
    print(s)
    out.append(s)


def quarter_effects(rows, quarters, age_adjust):
    """Within-gig quarter effects: y = gig FE + quarter FE [+ age FE].

    Returns {quarter: multiplicative effect vs BASE_Q}. Gig and quarter are
    absorbed; age enters as dummies when age_adjust, which identifies the SHAPE
    of the age profile but not its linear part (see module docstring).
    """
    qs = sorted(quarters, key=qi)
    if not all(b in qs for b in BASE_QS):
        return {}
    y = np.array([r["y"] for r in rows])
    gig = [r["gig"] for r in rows]
    qcol = [r["q1"] for r in rows]

    if age_adjust:
        # age dummies, capped so the thin tail does not spawn one-observation levels
        ages = sorted({min(r["age"], 20) for r in rows})
        ages = ages[1:]                       # drop one for the reference level
        X = np.zeros((len(rows), len(ages)))
        for j, a in enumerate(ages):
            for i, r in enumerate(rows):
                if min(r["age"], 20) == a:
                    X[i, j] = 1.0
    else:
        X = np.zeros((len(rows), 0))

    # absorb gig and quarter, then read the quarter effects back as cell means of
    # the residual: with two-way absorption the quarter effect is the mean residual
    # in that quarter once the other factor and the covariates are partialled out.
    if X.shape[1]:
        Xd, yd, _ = absorb2(X, y, gig, qcol)
        beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
        resid = y - X @ beta
    else:
        resid = y

    # now a one-way within-gig demeaning, and the quarter means of what is left
    gsum, gcnt = defaultdict(float), defaultdict(int)
    for r, g in zip(resid, gig):
        gsum[g] += r
        gcnt[g] += 1
    dem = np.array([r - gsum[g] / gcnt[g] for r, g in zip(resid, gig)])
    qsum, qcnt = defaultdict(float), defaultdict(int)
    for v, q in zip(dem, qcol):
        qsum[q] += v
        qcnt[q] += 1
    eff = {q: qsum[q] / qcnt[q] for q in qsum if qcnt[q] >= MIN_OBS}
    have = [b for b in BASE_QS if b in eff]
    if not have:
        return {}
    b = float(np.mean([eff[x] for x in have]))
    return {q: float(np.exp(v - b)) for q, v in eff.items()}



def write_site_block(quarters, raw, within, ageadj, cell_n, spans):
    """Merge the per-category series into `docs/data.json` for the website.

    Same arrangement as step 47's block, and the same warning: step 18 writes
    data.json whole, so **rerunning step 18 drops this**. Rerun step 62 after it.

    The site draws these as SMALL MULTIPLES rather than seven overlaid lines. That
    is not a stylistic preference: the site's seven category colours cannot be told
    apart pairwise under colour-vision deficiency (worst pair dE 6.1 deutan) and one
    pair is below the normal-vision floor as well (dE 13.2). Faceting removes the
    problem at its source -- one series per panel, identity carried by the panel
    title instead of by hue.
    """
    cats = [c for c in CATS if ageadj.get(c)]
    block = {
        "base": "2020 mean = 100",
        "quarters": quarters,
        "thin_until": THIN_UNTIL,
        "index": {c: [round(100 * ageadj[c][q], 1) if q in ageadj[c] else None
                      for q in quarters] for c in cats},
        "raw": {c: [round(raw[c][q], 1) if q in raw[c] else None
                    for q in quarters] for c in cats},
        "n": {c: [cell_n.get((c, q), 0) for q in quarters] for c in cats},
        "peak": {c: max((q for q in quarters if q in ageadj[c]),
                        key=lambda q: ageadj[c][q]) for c in cats},
        "mean_dq": [round(spans[q], 2) if q in spans else None for q in quarters],
        "event": {"label": "ChatGPT", "quarter": "2022Q4"},
        "step": {"label": "common step down", "quarter": "2021Q3"},
        "note": ("Within-gig review accrual, the only category-level quantity in the "
                 "project -- Fiverr Inc. publishes no category split. Age-adjusted "
                 "(gig, quarter and age fixed effects), 2020 four-quarter mean = 100. "
                 "The SHAPE is identified; the TREND is not, because within a gig age "
                 "and calendar quarter move one-for-one. Mean quarters spanned per "
                 "observation widens 1.2 to 1.75 across the window, so part of the "
                 "2024 fall is the archive capturing gigs less often."),
    }
    d = json.loads(DATAJSON.read_text())
    d["category_transactions"] = block
    DATAJSON.write_text(json.dumps(d, indent=2))
    print(f"  wrote category_transactions -> {DATAJSON.relative_to(ROOT)} "
          f"({len(cats)} categories x {len(quarters)} quarters)")


def main():
    say("=" * 92)
    say("STEP 62 - PER-CATEGORY SALES PROXY OVER TIME  (review accrual, within gig)")
    say("=" * 92)
    say()
    say("  Outcome: y = ln(1 + reviews per quarter), step 46's pre-registered one.")
    say("  Frame:   balanced-prices.csv x balanced-manifest-1200.tsv, 2018Q1-2024Q4.")
    say(f"  Index:   mean of {BASE_QS[0]}-{BASE_QS[-1]} = 100 in every series.")
    say()
    say("  READ THE HEADER BEFORE THE NUMBERS. Within a gig, age and calendar quarter")
    say("  move one-for-one, so no column below separates 'the market slowed' from")
    say("  'the panel aged'. Only DIFFERENCES BETWEEN CATEGORIES in the same quarter")
    say("  are clean, because every category ages on roughly the same schedule.")
    say()

    panel = m46.build_panel()
    tr = m46.transitions(panel)
    say(f"  accrual observations {len(tr):,}   gigs {len({r['gig'] for r in tr}):,}")

    by_cat = defaultdict(list)
    for r in tr:
        by_cat[r["cat"]].append(r)
    quarters = sorted({r["q1"] for r in tr}, key=qi)

    # ---------------------------------------------------- capture-span check
    say()
    say("-" * 92)
    say("A0 - CAPTURE SPAN PER QUARTER  (artefact check, read this before section A)")
    say("-" * 92)
    say("  accrual is (reviews gained) / (quarters spanned), assigned to the CLOSING")
    say("  quarter. If the archive captures gigs less often late in the window, the")
    say("  late rates are averages over longer smears and a fall could be the crawl")
    say("  rather than the market. Watch mean dq and the share of dq = 1.")
    say()
    say(f"  {'quarter':<9}{'obs':>9}{'mean dq':>9}{'dq=1':>8}{'gigs':>9}")
    spans = {}
    for q in quarters:
        rows = [r for r in tr if r["q1"] == q]
        if not rows:
            continue
        dq = np.array([r["dq"] for r in rows])
        spans[q] = float(dq.mean())
        say(f"  {q:<9}{len(rows):>9,}{dq.mean():>9.2f}"
            f"{100*float((dq == 1).mean()):>7.0f}%{len({r['gig'] for r in rows}):>9,}")

    # ---------------------------------------------------------------- raw
    raw = {}
    for c in CATS:
        rows = by_cat[c]
        cell = defaultdict(list)
        for r in rows:
            cell[r["q1"]].append(r["rate"])
        raw[c] = {q: float(np.mean(v)) for q, v in cell.items() if len(v) >= MIN_OBS}

    say()
    say("-" * 92)
    say("A - RAW MEAN ACCRUAL, reviews per gig per quarter (DESCRIPTIVE ONLY)")
    say("-" * 92)
    say("  Composition, aging and calendar time are all in here together.")
    say()
    hdr = "  quarter " + "".join(f"{c[:7]:>9}" for c in CATS) + f"{'obs':>9}"
    say(hdr)
    per_q_obs = defaultdict(int)
    for r in tr:
        per_q_obs[r["q1"]] += 1
    for q in quarters:
        line = f"  {q:<8}"
        for c in CATS:
            v = raw[c].get(q)
            line += f"{v:>9.1f}" if v is not None else f"{'-':>9}"
        say(line + f"{per_q_obs[q]:>9,}")

    # ------------------------------------------------- within gig, indexed
    for tag, adj, title in (
        ("within", False, "B - WITHIN-GIG INDEX (gig FE + quarter FE), "
                          f"2020 mean = 100"),
        ("ageadj", True,  "C - AGE-ADJUSTED INDEX (gig FE + quarter FE + age FE), "
                          f"2020 mean = 100"),
    ):
        series = {c: quarter_effects(by_cat[c], quarters, adj) for c in CATS}
        say()
        say("-" * 92)
        say(title)
        say("-" * 92)
        if adj:
            say("  Age dummies capped at 20 quarters. The SHAPE of the age profile is")
            say("  removed; its LINEAR part cannot be (age-period-cohort collinearity),")
            say("  so read the wiggles, not the slope.")
        else:
            say("  Composition is out. Aging is NOT -- the panel ages as the window runs,")
            say("  so part of every downward slope here is gigs getting older.")
        say()
        say("  quarter " + "".join(f"{c[:7]:>9}" for c in CATS))
        for q in quarters:
            line = f"  {q:<8}"
            for c in CATS:
                v = series[c].get(q)
                line += f"{100*v:>9.1f}" if v is not None else f"{'-':>9}"
            say(line)
        globals()[f"_series_{tag}"] = series

    # ----------------------------------------------------------- summary
    within = globals()["_series_within"]
    ageadj = globals()["_series_ageadj"]
    say()
    say("-" * 92)
    say("D - WHERE EACH CATEGORY PEAKED, AND WHAT IT DID AFTER")
    say("-" * 92)
    say("  On the age-adjusted index. The peak quarter is the one number here that is")
    say("  NOT a trend, so it survives the collinearity the level does not.")
    say()
    say(f"  {'cat':<12}{'peak q':>9}{'peak':>8}{'2022Q4':>9}{'2024Q4':>9}"
        f"{'peak->end':>11}{'2020->end':>13}")
    for c in CATS:
        s = ageadj[c]
        if not s:
            continue
        qs = sorted(s, key=qi)
        pk = max(qs, key=lambda q: s[q])
        end = qs[-1]
        b = s.get("2022Q4")
        say(f"  {c:<12}{pk:>9}{100*s[pk]:>8.1f}"
            + (f"{100*b:>9.1f}" if b else f"{'-':>9}")
            + f"{100*s[end]:>9.1f}{100*(s[end]/s[pk]-1):>10.1f}%"
            + f"{100*(s[end]-1):>12.1f}%")

    say()
    say("  Compare with step 46's break at 2022Q4 (ITS, linear trend + post):")
    say("    writing -42.9%  translation -37.2%  audio -35.5%  coding -35.2%")
    say("    video -28.6%  marketing -23.7%  design -13.1%   (all |t| > 6.6)")

    # ------------------------------------------------------------- write
    cell_n = defaultdict(int)
    for r in tr:
        cell_n[(r["cat"], r["q1"])] += 1
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "quarter", "n", "raw_rate",
                    "within_index", "ageadj_index"])
        for c in CATS:
            for q in quarters:
                n = cell_n[(c, q)]
                if n < MIN_OBS:
                    continue
                w.writerow([c, q, n,
                            f"{raw[c].get(q, float('nan')):.4f}",
                            f"{100*within[c][q]:.2f}" if q in within[c] else "",
                            f"{100*ageadj[c][q]:.2f}" if q in ageadj[c] else ""])
    write_site_block(quarters, raw, within, ageadj, cell_n, spans)
    say()
    say(f"  wrote {OUT_CSV.relative_to(ROOT)}")
    OUT_RUN.write_text("\n".join(out) + "\n")
    print(f"  wrote {OUT_RUN.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
