#!/usr/bin/env python3
"""
97 — "Orders in Queue": a current-demand field on stored gig pages.

EXPLORATORY. No step has extracted it. Fiverr shows "N Orders in Queue" under
the rating on a gig page; the page data carries the same number as
`overview.gig.ordersInQueue`, next to the gig's own `ratingsCount`. Measured on
300 balanced captures per year before this was written: present on 70% of
2018 captures (visible text only), 90% in 2019, ~100% 2020-2026; on 324 pages
showing both, JSON and visible text agreed every time; when the value is 0 the
page hides the line, so a missing line is NOT a missing value once the JSON
exists. One value per page (rare duplicates always agree).

WHAT IT IS. A snapshot of the active-order backlog on the capture day -- not a
quarter's sales. It is demand net of the seller's throughput, and sellers can
cap their queue or pause the gig, so it is partly a capacity choice.

THE PILOT asks whether it measures demand at all, against the one flow we
already hold: growth in a gig's cumulative review count between consecutive
quarters (reviews are left on completed orders, so dReviews ~ orders x review
rate). It reports coverage, the cross-sectional and within-gig association of
queue with dReviews (lagged and lead), and the raw quarterly path.

Input:  data/pilot/balanced-prices.csv  (file_path to stored HTML)
        data/pilot/balanced-gig-category.csv.gz
Output: data/pilot/queue-<tag>.csv      one row per capture
        runs/orders-in-queue/<tag>.md   the validation report

    python3 code/97-orders-in-queue.py --categories translation design --tag pilot
    python3 code/97-orders-in-queue.py --tag all
"""

import argparse
import gzip
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PRICES = BASE_DIR / "data" / "pilot" / "balanced-prices.csv"
CATEGORY = BASE_DIR / "data" / "pilot" / "balanced-gig-category.csv.gz"
OUTDIR = BASE_DIR / "data" / "pilot"
RUNDIR = BASE_DIR / "runs" / "orders-in-queue"

JSON_RE = re.compile(rb'"ordersInQueue"\s*:\s*(\d+)')
TEXT_RE = re.compile(rb">\s*(\d[\d,]*)\s+orders?\s+in\s+queue\s*<", re.I)
POST_Q = "2022Q4"


def scan(path):
    """Stored capture -> (queue, source). source: json | text | none | error."""
    try:
        b = gzip.open(BASE_DIR / path).read()
    except Exception:
        return None, "error"
    m = JSON_RE.search(b)
    if m:
        return int(m.group(1)), "json"
    m = TEXT_RE.search(b)
    if m:
        return int(m.group(1).replace(b",", b"")), "text"
    return None, "none"


def extract(categories, workers, limit):
    px = pd.read_csv(PRICES, usecols=["seller", "slug", "date", "year", "month",
                                      "review_count", "file_path"])
    px["gig_id"] = px.seller + "/" + px.slug
    px = px.merge(pd.read_csv(CATEGORY), on="gig_id", how="inner")
    if categories:
        px = px[px.category.isin(categories)]
    px = px.drop_duplicates("file_path")
    if limit:
        px = px.iloc[::max(1, len(px) // limit)][:limit]
    print(f"scanning {len(px):,} captures, {px.gig_id.nunique():,} gigs", file=sys.stderr)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(scan, px.file_path, chunksize=200))
    px["queue"] = [r[0] for r in res]
    px["source"] = [r[1] for r in res]
    return px[["gig_id", "category", "date", "year", "month", "review_count",
               "queue", "source"]]


def quarter(y, m):
    return f"{int(y)}Q{(int(m) - 1) // 3 + 1}"


def qi(q):
    return int(q[:4]) * 4 + int(q[-1]) - 1


def report(cap, tag):
    L = [f"# Orders in Queue — {tag}", ""]
    cats = sorted(cap.category.unique())
    L += [f"Captures: **{len(cap):,}** across **{cap.gig_id.nunique():,} gigs** "
          f"({', '.join(cats)}), balanced panel. Source: `data/pilot/queue-{tag}.csv`.", ""]

    # 1. coverage
    L += ["## 1. Coverage by year", "",
          "| year | captures | json | text only | none | coverage | share 0 | median | p90 | max |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for y, g in cap.groupby("year"):
        v = g.queue.dropna()
        n = len(g)
        L.append(f"| {y} | {n:,} | {(g.source == 'json').sum():,} | {(g.source == 'text').sum():,} | "
                 f"{(g.source == 'none').sum():,} | {len(v) / n:.0%} | "
                 f"{(v == 0).mean():.0%} | {v.median():.0f} | {v.quantile(.9):.0f} | {v.max():.0f} |")
    L += ["", "*Text-only rows (2018) cannot record a 0 — the page hides the line — so 2018 "
          "values are conditional on a positive queue and are excluded below.*", ""]

    # 2. gig-quarter panel
    c = cap[(cap.source == "json")].copy()
    c["quarter"] = [quarter(y, m) for y, m in zip(c.year, c.month)]
    gq = (c.groupby(["gig_id", "category", "quarter"])
            .agg(queue=("queue", "mean"), n_cap=("queue", "size"),
                 reviews=("review_count", "max"))
            .reset_index())
    gq["qi"] = gq.quarter.map(qi)
    gq = gq.sort_values(["gig_id", "qi"])
    g = gq.groupby("gig_id")
    for k, s in (("lag", 1), ("lead", -1)):
        prev_r, prev_q = g.reviews.shift(s), g.qi.shift(s)
        adj = (gq.qi - prev_q).abs() == 1
        d = (gq.reviews - prev_r) if s == 1 else (prev_r - gq.reviews)
        gq[f"d_rev_{k}"] = d.where(adj & (d >= 0))
    L += ["## 2. Does the queue track demand?", "",
          f"Gig-quarter panel (JSON captures only): **{len(gq):,}** gig-quarters, "
          f"**{gq.gig_id.nunique():,}** gigs, {gq.quarter.min()}–{gq.quarter.max()}; "
          f"{(gq.n_cap > 1).mean():.0%} of gig-quarters average more than one capture.", "",
          "`dReviews (into q)` = reviews gained from q-1 to q; `dReviews (out of q)` = reviews gained "
          "from q to q+1 — orders in the queue at q are completed, and reviewed, after it. "
          "Consecutive quarters only.", "",
          "| association | n | Spearman ρ (pooled) | within-quarter ρ (median over quarters) | within-gig ρ |",
          "|---|---:|---:|---:|---:|"]
    for k, lab in (("lag", "queue vs dReviews (into q)"), ("lead", "queue vs dReviews (out of q)")):
        sub = gq.dropna(subset=[f"d_rev_{k}"])
        rho = sub.queue.rank().corr(sub[f"d_rev_{k}"].rank())
        wq = np.nanmedian([x.queue.rank().corr(x[f"d_rev_{k}"].rank())
                           for _, x in sub.groupby("quarter") if len(x) > 30] or [np.nan])
        multi = sub[sub.groupby("gig_id").gig_id.transform("size") >= 3]
        dq = multi.queue - multi.groupby("gig_id").queue.transform("mean")
        dr = multi[f"d_rev_{k}"] - multi.groupby("gig_id")[f"d_rev_{k}"].transform("mean")
        wg = dq.rank().corr(dr.rank())
        L.append(f"| {lab} | {len(sub):,} | {rho:+.3f} | {wq:+.3f} | {wg:+.3f} |")
    sub = gq.dropna(subset=["d_rev_lead"])
    L += ["", "Mean reviews gained in the next quarter, by queue level:", "",
          "| queue at q | gig-quarters | mean dReviews (out of q) | median |", "|---|---:|---:|---:|"]
    bins = [-0.1, 0, 1, 3, 10, np.inf]
    labs = ["0", "(0, 1]", "(1, 3]", "(3, 10]", "> 10"]
    sub = sub.assign(b=pd.cut(sub.queue, bins, labels=labs))
    for b_, x in sub.groupby("b", observed=True):
        L.append(f"| {b_} | {len(x):,} | {x.d_rev_lead.mean():.1f} | {x.d_rev_lead.median():.0f} |")

    # 3. raw path
    L += ["", "## 3. Raw quarterly path (JSON captures, gig-quarter means)", "",
          "Composition is not held fixed here; the gig-FE contrast below is.", "",
          "| quarter | " + " | ".join(f"{c_} n | {c_} mean | {c_} % > 0" for c_ in cats) + " |",
          "|---|" + "---:|---:|---:|" * len(cats)]
    for q, x in gq.groupby("quarter"):
        if q < "2019Q1":
            continue
        cells = []
        for c_ in cats:
            y_ = x[x.category == c_].queue
            cells += [f"{len(y_):,}", f"{y_.mean():.2f}" if len(y_) else "–",
                      f"{(y_ > 0).mean():.0%}" if len(y_) else "–"]
        L.append(f"| {q} | " + " | ".join(cells) + " |")

    # 4. within-gig pre/post, per category
    L += ["", f"## 4. Within-gig change across {POST_Q} (descriptive, no exposure contrast)", "",
          "Gigs with JSON captures both in 2021Q1–2022Q3 and 2023Q1–2024Q3 (the post window skips "
          "the launch quarter; both end before the 2024Q4 capture thinning). Change in each gig's "
          "mean queue and in its share of quarters with a queue.", "",
          "| category | gigs | pre mean | post mean | Δ mean (gig-paired) | 95% CI | pre % > 0 | post % > 0 |",
          "|---|---:|---:|---:|---:|---|---:|---:|"]
    pre = gq[(gq.quarter >= "2021Q1") & (gq.quarter <= "2022Q3")]
    post = gq[(gq.quarter >= "2023Q1") & (gq.quarter <= "2024Q3")]
    a = pre.groupby(["category", "gig_id"]).queue.agg(["mean", lambda s: (s > 0).mean()])
    b_ = post.groupby(["category", "gig_id"]).queue.agg(["mean", lambda s: (s > 0).mean()])
    a.columns = b_.columns = ["m", "p"]
    j = a.join(b_, lsuffix="_pre", rsuffix="_post", how="inner").reset_index()
    rng = np.random.default_rng(0)
    for c_, x in j.groupby("category"):
        d = (x.m_post - x.m_pre).to_numpy()
        boot = [rng.choice(d, len(d)).mean() for _ in range(999)]
        L.append(f"| {c_} | {len(x):,} | {x.m_pre.mean():.2f} | {x.m_post.mean():.2f} | "
                 f"{d.mean():+.2f} | [{np.percentile(boot, 2.5):+.2f}, {np.percentile(boot, 97.5):+.2f}] | "
                 f"{x.p_pre.mean():.0%} | {x.p_post.mean():.0%} |")
    L += ["", "*Survivor panel: gigs seen on both sides. A demand loss that shows up as exit is "
          "invisible here, as in every within-gig test in this project.*", ""]
    if len(cats) == 2:
        L += event_study(gq, cats)
    return "\n".join(L) + "\n", gq


def contrast(df, col, treat, ref, base="2022Q3"):
    """Gig-demeaned (category, quarter) means, treat minus ref, normalised at `base`.

    With one observation per gig-quarter this is the two-way FE event study up
    to the panel's small imbalance."""
    x = df.assign(dm=df[col] - df.groupby("gig_id")[col].transform("mean"))
    m = x.groupby(["quarter", "category"]).dm.mean().unstack()
    d = m[treat] - m[ref]
    return d - d[base]


def event_study(gq, cats, n_boot=200, seed=0):
    """Two-category event study on log(1+queue) and on P(queue > 0), gig bootstrap."""
    ref, treat = sorted(cats, key=lambda c: c != "design")  # design is the reference if present
    w = gq[(gq.quarter >= "2019Q4") & (gq.quarter <= "2024Q4")].copy()
    w["lq"] = np.log1p(w.queue)
    w["pos"] = (w.queue > 0).astype(float)
    w = w.reset_index(drop=True)
    idx = w.groupby("gig_id").indices
    gigs = np.array(list(idx))
    rng = np.random.default_rng(seed)
    L = [f"## 5. Event study: {treat} minus {ref}, gig-demeaned, 2022Q3 = 0", "",
         f"Gig bootstrap, {n_boot} draws; * = 95% interval excludes 0. Window 2019Q4–2024Q4. "
         "Two categories only — this is a contrast, not the exposure DiD.", "",
         "| quarter | log(1+queue) | 95% CI | P(queue > 0) | 95% CI |", "|---|---:|---|---:|---|"]
    res = {}
    for col in ("lq", "pos"):
        pt = contrast(w, col, treat, ref)
        boots = []
        for _ in range(n_boot):
            s = rng.choice(gigs, len(gigs))
            rows = np.concatenate([idx[k] for k in s])
            b = w.loc[rows].assign(gig_id=np.repeat(np.arange(len(s)), [len(idx[k]) for k in s]))
            boots.append(contrast(b, col, treat, ref))
        B = pd.concat(boots, axis=1)
        res[col] = (pt, B.quantile(.025, axis=1), B.quantile(.975, axis=1))
    for q in res["lq"][0].index:
        cells = []
        for col in ("lq", "pos"):
            pt, lo, hi = res[col]
            star = "*" if (lo[q] > 0 or hi[q] < 0) else ""
            cells += [f"{pt[q]:+.3f}{star}", f"[{lo[q]:+.3f}, {hi[q]:+.3f}]"]
        L.append(f"| {q} | " + " | ".join(cells) + " |")
    pt = res["lq"][0]
    pre = pt[pt.index < POST_Q]
    n_sig = sum(1 for q in pre.index if q != "2022Q3"
                and (res["lq"][1][q] > 0 or res["lq"][2][q] < 0))
    L += ["", f"Pre-period (2019Q4–2022Q2): **{n_sig} of {len(pre) - 1}** quarters significant on "
          f"log(1+queue); mean {pre.mean():+.3f}. Post 2023Q1–2024Q3 mean "
          f"{pt[(pt.index >= '2023Q1') & (pt.index <= '2024Q3')].mean():+.3f}.", ""]
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--categories", nargs="*", default=None)
    ap.add_argument("--tag", default="pilot")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=7)
    args = ap.parse_args()

    out = OUTDIR / f"queue-{args.tag}.csv"
    cap = extract(args.categories, args.workers, args.limit)
    cap.to_csv(out, index=False)
    print(f"wrote {out} ({len(cap):,} rows)", file=sys.stderr)

    RUNDIR.mkdir(parents=True, exist_ok=True)
    md, _ = report(cap, args.tag)
    (RUNDIR / f"{args.tag}.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
