#!/usr/bin/env python3
"""
Step 48: Can the category question be answered at all? The pre-registered fallback.

Step 46 established two things. Every category's review accrual broke sharply at
2022Q4 (-13% to -43%, all |t| > 6.6, MDE now +/-4.2% to +/-7.0%), and the
HIGH-vs-LOW DiD does NOT identify an AI effect: parallel trends failed the gate,
the linear-trend horse race collapsed HIGH x POST from -7.9% to -0.8%, and a CPI-U
placebo reproduced the effect.

Prereg §5 authorises exactly ONE fallback and forbids a third:
  "synthetic control, constructing a weighted combination of the LOW categories to
   match each HIGH category's pre-2022Q4 accrual path."

This script runs it, plus the one specification that directly answers *why* the
original failed:

  C1  Category x quarter accrual series — the raw material, published so the
      reader can see the pre-trends rather than take our word for them.
  C2  DiD WITH CATEGORY-SPECIFIC LINEAR TRENDS. The failure in step 46 was a
      differential TREND, not a differential break. Allowing each category its own
      trend is the textbook fix; if a break survives it, that break is net of trend.
  C3  SYNTHETIC CONTROL, registered form: donors = LOW categories only.
  C4  SYNTHETIC CONTROL, expanded donor pool = LOW + MID. A DECLARED DEVIATION
      (prereg §9) because two donors is a one-parameter weight and cannot match
      much. Reported alongside, never instead of, C3.
  C5  IN-SPACE PLACEBOS for inference. Each donor is treated as if treated; the
      treated gap is ranked against the placebo distribution. With 7 categories
      the smallest attainable one-sided p-value is 1/7 = 0.143, so this CANNOT
      return significance at 5%. That is a property of having seven categories,
      it is known before running, and it is the honest headline of C5.

READ FIRST: none of this can rescue the category question if the pre-trends are
real. Synthetic control relaxes parallel trends; it does not create a control group
where none exists. Every category on this platform is treated.

Run:  python3 code/48-category-impact.py
"""

import csv
import importlib.util
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "code"))


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, BASE / "code" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


s46 = _load("s46", "46-balanced-demand.py")

CATS = s46.CATS
HIGH, LOW, MID = s46.HIGH, s46.LOW, s46.MID
BREAK_Q, WIN_START, WIN_END = s46.BREAK_Q, s46.WIN_START, s46.WIN_END
qi, fit, show = s46.qi, s46.fit, s46.show
RANKING = s46.RANKING


# --------------------------------------------------------------------------
# simplex-constrained least squares (synthetic-control weights)
# --------------------------------------------------------------------------
def proj_simplex(v):
    """Euclidean projection onto {w >= 0, sum w = 1}."""
    u = np.sort(v)[::-1]
    css = np.cumsum(u)
    rho = np.nonzero(u * np.arange(1, len(v) + 1) > (css - 1))[0][-1]
    theta = (css[rho] - 1) / (rho + 1.0)
    return np.maximum(v - theta, 0.0)


def sc_weights(Y_donors, y_target, iters=20000, lr=0.02):
    """min ||y - Yw||^2 s.t. w on the simplex. Projected gradient."""
    n = Y_donors.shape[1]
    w = np.ones(n) / n
    L = np.linalg.norm(Y_donors, 2) ** 2 + 1e-9
    step = lr / L * len(y_target)
    for _ in range(iters):
        g = Y_donors.T @ (Y_donors @ w - y_target)
        w = proj_simplex(w - step * g)
    return w


def synth(series, target, donors, pre_qs, post_qs, demean=True):
    """Doudchenko-Imbens style: match the pre-period path allowing a level shift.

    Returns dict with weights, pre-RMSPE, mean post gap, and the gap path.
    """
    def vec(c, qs):
        return np.array([series[c][q] for q in qs])

    yt_pre = vec(target, pre_qs)
    Yd_pre = np.column_stack([vec(c, pre_qs) for c in donors])
    if demean:
        t_mu = yt_pre.mean()
        d_mu = Yd_pre.mean(axis=0)
        w = sc_weights(Yd_pre - d_mu, yt_pre - t_mu)
        shift = t_mu - float(d_mu @ w)
    else:
        w = sc_weights(Yd_pre, yt_pre)
        shift = 0.0

    def synth_path(qs):
        Yd = np.column_stack([vec(c, qs) for c in donors])
        return Yd @ w + shift

    pre_fit = yt_pre - synth_path(pre_qs)
    post_gap = vec(target, post_qs) - synth_path(post_qs)
    return {
        "w": w, "donors": donors,
        "rmspe": float(np.sqrt(np.mean(pre_fit ** 2))),
        "post_mean": float(post_gap.mean()),
        "post_path": post_gap,
        "pre_path": pre_fit,
    }


# --------------------------------------------------------------------------
def build_series(tr):
    """category -> quarter -> mean log accrual (all quarters populated)."""
    acc = defaultdict(lambda: defaultdict(list))
    for r in tr:
        acc[r["cat"]][r["q1"]].append(r["y"])
    qs = sorted({q for c in acc for q in acc[c]}, key=qi)
    qs = [q for q in qs if all(len(acc[c].get(q, [])) >= 20 for c in CATS)]
    return {c: {q: float(np.mean(acc[c][q])) for q in qs} for c in CATS}, qs


def c1(series, qs):
    print("=" * 96)
    print("C1 — CATEGORY x QUARTER MEAN LOG ACCRUAL  (the raw material)")
    print("=" * 96)
    print(f"\n  {len(qs)} quarters with >=20 observations in all seven categories: "
          f"{qs[0]} to {qs[-1]}")
    print(f"\n  {'quarter':<9}" + "".join(f"{c[:6]:>8}" for c in CATS))
    for q in qs:
        mark = " <<" if q == BREAK_Q else ""
        print(f"  {q:<9}" + "".join(f"{series[c][q]:>8.3f}" for c in CATS) + mark)
    pre = [q for q in qs if qi(q) <= qi(BREAK_Q)]
    post = [q for q in qs if qi(q) > qi(BREAK_Q)]
    print(f"\n  pre {len(pre)} quarters ({pre[0]}-{pre[-1]}), "
          f"post {len(post)} quarters ({post[0]}-{post[-1]})")
    return pre, post


def c2(tr):
    print("\n" + "=" * 96)
    print("C2 — DiD WITH CATEGORY-SPECIFIC LINEAR TRENDS")
    print("=" * 96)
    print("\n  Step 46's failure was a differential TREND. Give every category its own")
    print("  trend and ask whether a differential BREAK survives. gig + quarter FE,")
    print("  gig-clustered SEs, sample = HIGH u LOW.")
    sub = [r for r in tr if r["cat"] in HIGH | LOW]
    for r in sub:
        r["hi"] = 1.0 if r["cat"] in HIGH else 0.0
    cols = []
    for c in sorted(HIGH | LOW)[:-1]:      # one category trend dropped (collinear)
        cols.append((f"trend_{c[:5]}",
                     (lambda c: (lambda r: (r["t"] - 8090) if r["cat"] == c else 0.0))(c)))
    cols.append(("HIGH x POST", lambda r: r["hi"] * r["post"]))
    b, se, n, names = fit(sub, cols, "cat-trend-did")
    print(f"\n    {'term':<18}{'coef':>9} {'se':>8} {'t':>7}     {'effect':>8}"
          f"  {'95% CI on the rate':>22}")
    show(b, se, names, None)
    k = names.index("HIGH x POST")
    print(f"\n  obs {n:,}")
    verdict = "SURVIVES" if abs(b[k] / se[k]) > 1.96 else "DOES NOT SURVIVE"
    print(f"  => HIGH x POST {verdict} category-specific trends.")
    return b[k], se[k]


def c345(series, pre, post):
    exp = {}
    with open(RANKING) as f:
        for row in csv.DictReader(f):
            exp[row["category"]] = float(row["exposure_primary"])

    for tag, donor_pool, note in (
        ("C3", sorted(LOW), "REGISTERED form: donors = LOW only (2 donors)"),
        ("C4", sorted(LOW | MID), "DECLARED DEVIATION: donors = LOW + MID (5 donors)"),
    ):
        print("\n" + "=" * 96)
        print(f"{tag} — SYNTHETIC CONTROL.  {note}")
        print("=" * 96)
        for target in sorted(HIGH):
            donors = [c for c in donor_pool if c != target]
            r = synth(series, target, donors, pre, post)
            print(f"\n  target {target}  (exposure {exp[target]:.3f})")
            print("    weights: " + "  ".join(
                f"{c}={w:.3f}" for c, w in zip(donors, r["w"]) if w > 0.001))
            print(f"    pre-period RMSPE {r['rmspe']:.4f}   "
                  f"mean post gap {r['post_mean']:+.4f} log pts "
                  f"({100*(np.exp(r['post_mean'])-1):+.1f}%)")
            ratio = abs(r["post_mean"]) / r["rmspe"] if r["rmspe"] else float("inf")
            print(f"    |post gap| / pre RMSPE = {ratio:.2f}   "
                  f"({'exceeds pre-period noise' if ratio > 1 else 'WITHIN pre-period noise'})")

        # ---- C5: in-space placebos, on the expanded pool only (needs donors) ----
        if tag != "C4":
            continue
        print("\n" + "=" * 96)
        print("C5 — IN-SPACE PLACEBOS.  Every category treated as if treated.")
        print("=" * 96)
        print("\n  Known before running: with 7 categories the smallest attainable")
        print("  one-sided p-value is 1/7 = 0.143. This CANNOT reach 5%.")
        print(f"\n  {'category':<12}{'arm':>6}{'exposure':>10}{'postGap':>10}"
              f"{'preRMSPE':>10}{'ratio':>8}")
        rows = []
        for target in CATS:
            donors = [c for c in CATS if c != target]
            r = synth(series, target, donors, pre, post)
            arm = "HIGH" if target in HIGH else ("LOW" if target in LOW else "mid")
            ratio = abs(r["post_mean"]) / r["rmspe"] if r["rmspe"] else float("inf")
            rows.append((target, arm, exp[target], r["post_mean"], r["rmspe"], ratio))
        for t, arm, e, g, rm, ra in sorted(rows, key=lambda x: -x[5]):
            star = " <-- HIGH" if arm == "HIGH" else ""
            print(f"  {t:<12}{arm:>6}{e:>10.3f}{g:>+10.4f}{rm:>10.4f}"
                  f"{ra:>8.2f}{star}")
        order = [r[0] for r in sorted(rows, key=lambda x: -x[5])]
        print(f"\n  Rank of the HIGH categories by |gap|/RMSPE, out of {len(rows)}:")
        for h in sorted(HIGH):
            k = order.index(h) + 1
            print(f"    {h:<12} rank {k}  -> one-sided p = {k/len(rows):.3f}")
        print("\n  If AI were driving this, the two HIGH categories should occupy the")
        print("  top ranks. Read the ranks above against that expectation.")
        return rows


def main():
    print("Step 48 — the category question, via the pre-registered fallback\n")
    panel = s46.build_panel()
    tr = s46.transitions(panel)
    series, qs = build_series(tr)
    pre, post = c1(series, qs)
    c2(tr)
    c345(series, pre, post)
    print("\n" + "=" * 96)
    print("Every number is Q1 — accrual per SURVIVING gig. Window ends 2024Q4.")
    print("Fiverr Inc. publishes no category split, so nothing external can")
    print("corroborate a category ranking the way step 47 corroborated the level.")
    print("=" * 96)


if __name__ == "__main__":
    main()
