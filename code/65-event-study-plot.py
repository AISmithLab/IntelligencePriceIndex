#!/usr/bin/env python3
"""
Step 65: Render §8's event-study figure — "prices rose, but more slowly".

Reproduces notebooks/00-explore.ipynb §8 as a standalone figure so the picture
does not depend on the notebook having been executed. Estimator, sample rule and
SEs are IMPORTED from code/64-event-study-twfe.py, never reimplemented here.

The claim the figure has to carry is a comparison, not a level: prices keep
rising after 2022Q4, but they fall away from the line fitted to the 11 quarters
BEFORE ChatGPT existed. So the pre-trend is drawn extrapolated, and the gap
between it and the realised path is shaded and labelled.

Read the caveat in §8 before quoting the gap: it extrapolates a linear trend
eight quarters past its last data point, and there is no control group.

Output: outputs/figures/event-study-chatgpt.png (+ .pdf)
        runs/event-study-plot.out
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
FIGDIR = ROOT / "outputs" / "figures"
FIGDIR.mkdir(parents=True, exist_ok=True)

PRICES = ROOT / "data" / "pilot" / "balanced-prices.csv"
CATEGORY_CSV = ROOT / "data" / "pilot" / "balanced-gig-category.csv.gz"
START_Q, END_Q = "2020Q1", "2024Q4"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / "code" / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


esm = _load("es64", "64-event-study-twfe.py")
LAUNCH, BASE = esm.CHATGPT_LAUNCH, esm.DEFAULT_BASE

out = []
def say(s=""):
    print(s)
    out.append(s)


gq = esm.build_panel(PRICES, CATEGORY_CSV)
bal = esm.balanced_sample(gq, cut=LAUNCH, window=(START_Q, END_Q))
tab, diag = esm.event_study(bal, base=BASE)
pt = esm.pretrend_test(tab, cut=LAUNCH)
t = pt["table"]

say("=" * 78)
say("STEP 65 — EVENT STUDY FIGURE: ROSE, BUT MORE SLOWLY")
say("=" * 78)
say(f"  window {START_Q}..{END_Q}, base {BASE}, cut {LAUNCH}")
say(f"  gigs pre {bal.attrs['n_pre']:,} / post {bal.attrs['n_post']:,} "
    f"/ BALANCED {bal.attrs['n_balanced']:,}")
say(f"  {diag['obs']:,} obs, {diag['gigs']:,} gigs, {diag['quarters']} quarters")
say()
say(f"  pre-trend on {pt['pre_quarters']} pre-launch quarters: "
    f"{pt['slope']:+.4f} log pts/quarter (t = {pt['t']:.1f})")
say(f"  gap at {t.quarter.iloc[-1]}: {pt['gap_last']:+.4f} log pts "
    f"({100 * np.expm1(pt['gap_last']):+.1f}%) vs the extrapolated pre-trend")
say()
say("  quarter    coef      se    ci_lo    ci_hi   pretrend      gap")
for r in t.itertuples():
    say(f"  {r.quarter}  {r.coef:+.4f}  {r.se:.4f}  {r.ci_lo:+.4f}  "
        f"{r.ci_hi:+.4f}  {r.pretrend:+.4f}  {r.gap:+.4f}")

# ---------------------------------------------------------------- figure
x = np.arange(len(t))
cut_x = float(x[t.quarter == LAUNCH][0]) - 0.5   # boundary, not a quarter centre
post = t.qi >= esm.q_to_int(LAUNCH)

fig, ax = plt.subplots(figsize=(11, 6))

ax.axvspan(cut_x, x[-1] + 0.5, color="0.93", zorder=0)

# the gap the claim is about: realised path vs the counterfactual line
ax.fill_between(x[post.to_numpy()], t.coef[post], t.pretrend[post],
                color="crimson", alpha=.13, zorder=1,
                label="shortfall vs pre-trend")

ax.fill_between(x, t.ci_lo, t.ci_hi, color="C0", alpha=.20, lw=0, zorder=2,
                label="95% CI (gig-clustered)")
ax.plot(x, t.pretrend, "--", lw=1.6, color="0.40", zorder=3,
        label=f"pre-launch trend, extrapolated ({pt['slope']:+.3f} log pts/qtr)")
ax.plot(x, t.coef, "o-", lw=2.2, ms=5, color="C0", zorder=4,
        label=r"$\delta_q$: log price vs " + BASE + " (gig + quarter FE)")

ax.axvline(cut_x, color="crimson", ls=":", lw=2, zorder=5)
ax.axhline(0, color="0.4", lw=.8, zorder=1)

ax.annotate("ChatGPT\n2022-11-30", xy=(cut_x, ax.get_ylim()[1]),
            xytext=(6, -30), textcoords="offset points",
            color="crimson", fontsize=9, ha="left")

# label the endpoint gap, which is the whole point of the chart
gap = pt["gap_last"]
ax.annotate(f"{gap:+.2f} log pts ({100 * np.expm1(gap):+.0f}%)\nbelow the pre-trend",
            xy=(x[-1], (t.coef.iloc[-1] + t.pretrend.iloc[-1]) / 2),
            xytext=(-14, 0), textcoords="offset points",
            ha="right", va="center", fontsize=9, color="crimson",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="crimson", alpha=.9))

ax.set_xticks(x)
ax.set_xticklabels(t.quarter, rotation=90)
ax.set_ylabel(f"log price relative to {BASE}")
ax.set_title(f"Prices kept rising after ChatGPT — but more slowly than the trend that "
             f"preceded it\n{bal.attrs['n_balanced']:,} gigs observed on both sides, "
             f"{diag['obs']:,} gig-quarters, {START_Q}–{END_Q}", fontsize=11)
ax.legend(frameon=False, loc="upper left", fontsize=9)
ax.grid(alpha=.3)
ax.margins(x=.01)

fig.text(.01, .005,
         "No control group: every gig meets the launch on the same date, so "
         "each δ_q is the common time path net of gig level, not an effect. "
         "The dashed line is extrapolated 8 quarters past its last data point.",
         fontsize=7.5, color="0.35")

plt.tight_layout(rect=[0, .03, 1, 1])
for ext in ("png", "pdf"):
    p = FIGDIR / f"event-study-chatgpt.{ext}"
    fig.savefig(p, dpi=170 if ext == "png" else None, bbox_inches="tight")
    say(f"\n  wrote {p.relative_to(ROOT)}")

(ROOT / "runs" / "event-study-plot.out").write_text("\n".join(out) + "\n")
