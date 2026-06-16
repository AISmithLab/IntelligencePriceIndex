#!/usr/bin/env python3
"""
Panel-based Intelligence Price Index — tracks same-gig price changes over time.

Unlike the naive cross-sectional approach (script 11), this uses a matched panel:
  - Only gigs observed in 2+ quarters contribute
  - Price changes are computed WITHIN gig (controls for composition)
  - Category indices are geometric means of within-gig price relatives
  - Composite IPI uses Törnqvist-style weights

This is analogous to the "matched model" method the BLS uses for CPI items
where quality adjustment is difficult.

Output:
  data/pilot/panel-ipi.csv
  data/pilot/panel-category-indices.csv
  data/pilot/panel-elasticity.csv
  data/pilot/panel-summary.md
"""

import csv
import math
import os
import sys
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats

BASE_DIR = Path(__file__).resolve().parent.parent
PRICES_FILE = BASE_DIR / "data" / "pilot" / "pilot-prices.csv"
ITEMS_FILE = BASE_DIR / "data" / "pilot" / "gig-items.csv"
BENCHMARKS_FILE = BASE_DIR / "data" / "ai-benchmarks.csv"

OUTPUT_IPI = BASE_DIR / "data" / "pilot" / "panel-ipi.csv"
OUTPUT_CAT = BASE_DIR / "data" / "pilot" / "panel-category-indices.csv"
OUTPUT_ELAST = BASE_DIR / "data" / "pilot" / "panel-elasticity.csv"
OUTPUT_SUMMARY = BASE_DIR / "data" / "pilot" / "panel-summary.md"

# Same category keywords as script 11
CATEGORY_KEYWORDS = {
    "writing": ["write", "article", "blog", "content", "copywriting", "story",
                 "ebook", "book", "proofread", "edit", "ghostwrit", "script",
                 "resume", "cover letter", "press release"],
    "coding": ["code", "python", "javascript", "app", "mobile app", "web",
               "wordpress", "shopify", "wix", "html", "css", "developer",
               "software", "programming", "script", "api", "database",
               "sql", "discord bot", "game"],
    "design": ["logo", "design", "graphic", "banner", "flyer", "poster",
               "illustration", "draw", "cartoon", "caricature", "infographic",
               "photoshop", "ui", "ux", "brand", "tshirt", "packaging",
               "mockup", "thumbnail", "book cover", "album cover"],
    "translation": ["translat", "spanish", "french", "german", "arabic",
                     "chinese", "japanese", "korean", "hindi", "portuguese"],
    "video": ["video", "animation", "motion", "whiteboard", "explainer",
              "intro", "outro", "edit video", "youtube", "after effects",
              "3d", "render", "model"],
    "audio": ["voice", "voiceover", "narrat", "sing", "music", "audio",
              "podcast", "jingle", "sound", "mixing", "master"],
    "marketing": ["seo", "marketing", "ads", "facebook", "google ads",
                   "social media", "instagram", "tiktok", "email marketing",
                   "ppc", "lead", "traffic"],
    "data_entry": ["data entry", "typing", "transcri", "convert", "pdf",
                    "excel", "spreadsheet", "powerpoint", "copy paste"],
    "data_analysis": ["data analy", "statistic", "research", "survey",
                       "scraping", "machine learning", "ai", "dashboard",
                       "visualization", "tableau", "power bi"],
}


def classify_gig(description, item_label):
    text = (description + " " + item_label).lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for kw in keywords if kw in text)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "other"


def to_quarter(year, month):
    try:
        y, m = int(year), int(month)
        return f"{y}Q{(m - 1) // 3 + 1}"
    except (ValueError, TypeError):
        return None


def quarter_to_float(q):
    return int(q[:4]) + (int(q[-1]) - 1) * 0.25


def main():
    print("=" * 60)
    print("PANEL-BASED INTELLIGENCE PRICE INDEX")
    print("=" * 60)

    # ── Load data ──────────────────────────────────────────────
    print("\n1. Loading and building panel...")

    item_map = {}
    with open(ITEMS_FILE) as f:
        for row in csv.DictReader(f):
            item_map[(row["seller"], row["slug"])] = (
                int(row["item_id"]), row["item_label"], row["description"])

    # Build gig-quarter panel: for each gig, median price per quarter
    gig_quarter = defaultdict(lambda: defaultdict(list))
    gig_meta = {}  # (seller, slug) → {category, reviews_max}

    with open(PRICES_FILE) as f:
        for row in csv.DictReader(f):
            key = (row["seller"], row["slug"])
            item = item_map.get(key)
            if not item:
                continue
            price = float(row.get("price_basic", 0) or 0)
            if price <= 0 or price > 10000:
                continue
            quarter = to_quarter(row["year"], row["month"])
            if not quarter:
                continue

            gig_quarter[key][quarter].append(price)

            if key not in gig_meta:
                cat = classify_gig(item[2], item[1])
                gig_meta[key] = {"category": cat, "max_reviews": 0}
            reviews = int(row.get("review_count", 0) or 0)
            gig_meta[key]["max_reviews"] = max(gig_meta[key]["max_reviews"], reviews)

    # Collapse to median price per gig per quarter
    gig_quarterly_price = {}
    for key, quarters in gig_quarter.items():
        gig_quarterly_price[key] = {}
        for q, prices in quarters.items():
            gig_quarterly_price[key][q] = float(np.median(prices))

    # Filter: only gigs with 2+ quarters
    panel_gigs = {k: v for k, v in gig_quarterly_price.items() if len(v) >= 2}
    print(f"  Total gigs: {len(gig_quarterly_price):,}")
    print(f"  Panel gigs (≥2 quarters): {len(panel_gigs):,}")

    all_quarters = sorted(set(q for qs in panel_gigs.values() for q in qs))
    print(f"  Quarters: {all_quarters[0]} to {all_quarters[-1]} ({len(all_quarters)})")

    # ── Compute within-gig price relatives ─────────────────────
    print("\n2. Computing within-gig price relatives...")

    # For each consecutive pair of quarters a gig is observed in,
    # compute the price relative: p_t / p_{t-1}
    # Then the category index chains these relatives together

    # Group gigs by category
    cat_gigs = defaultdict(list)
    for key in panel_gigs:
        cat = gig_meta[key]["category"]
        if cat != "other":
            cat_gigs[cat].append(key)

    print(f"  Categories: {sorted(cat_gigs.keys())}")
    for cat, gigs in sorted(cat_gigs.items()):
        print(f"    {cat:<20} {len(gigs):>5} panel gigs")

    # For each quarter transition, compute geometric mean of price relatives
    # within each category (Jevons index — used by CPI for elementary aggregates)
    cat_chain = {}  # category → {quarter → chained_index}

    for cat, gigs in cat_gigs.items():
        # Collect price relatives for each quarter pair
        quarter_relatives = defaultdict(list)  # quarter → list of (p_t / p_{t-1})

        for key in gigs:
            qs = sorted(panel_gigs[key].keys())
            for i in range(1, len(qs)):
                q_prev, q_curr = qs[i-1], qs[i]
                p_prev = panel_gigs[key][q_prev]
                p_curr = panel_gigs[key][q_curr]
                if p_prev > 0:
                    relative = p_curr / p_prev
                    # Filter extreme outliers (price changed >10x in one step)
                    if 0.1 <= relative <= 10:
                        quarter_relatives[q_curr].append(relative)

        if not quarter_relatives:
            continue

        # Chain: start at 100 in base quarter, multiply by geometric mean relative
        base_q = "2019Q1"
        # Find starting quarter
        available = sorted(quarter_relatives.keys())
        if not available:
            continue

        # Initialize at base quarter = 100
        index = {base_q: 100.0}

        # Chain forward from base
        forward_qs = [q for q in all_quarters if q >= base_q]
        for i in range(1, len(forward_qs)):
            q = forward_qs[i]
            if q in quarter_relatives and len(quarter_relatives[q]) >= 3:
                geo_mean = np.exp(np.mean(np.log(quarter_relatives[q])))
                prev_q = forward_qs[i-1]
                if prev_q in index:
                    index[q] = index[prev_q] * geo_mean

        # Chain backward from base
        backward_qs = [q for q in reversed(all_quarters) if q <= base_q]
        for i in range(1, len(backward_qs)):
            q = backward_qs[i]
            q_next = backward_qs[i-1]
            if q_next in quarter_relatives and len(quarter_relatives[q_next]) >= 3:
                geo_mean = np.exp(np.mean(np.log(quarter_relatives[q_next])))
                if q_next in index:
                    index[q] = index[q_next] / geo_mean

        cat_chain[cat] = index

    # ── Compute composite IPI ──────────────────────────────────
    print("\n3. Computing composite panel IPI...")

    # Weights: max review count as volume proxy (Törnqvist-style)
    cat_weights = {}
    for cat, gigs in cat_gigs.items():
        if cat in cat_chain:
            cat_weights[cat] = sum(gig_meta[k]["max_reviews"] for k in gigs)
    total_w = sum(cat_weights.values()) or 1
    for cat in cat_weights:
        cat_weights[cat] /= total_w

    print("  Weights:")
    for cat, w in sorted(cat_weights.items(), key=lambda x: -x[1]):
        print(f"    {cat:<20} {w:.3f}")

    # Composite: weighted geometric mean of category indices
    ipi = {}
    for q in all_quarters:
        log_sum = 0
        w_sum = 0
        for cat, idx in cat_chain.items():
            if q in idx and cat in cat_weights:
                w = cat_weights[cat]
                log_sum += w * math.log(idx[q])
                w_sum += w
        if w_sum > 0.3:
            ipi[q] = math.exp(log_sum / w_sum)

    # Print IPI time series
    print("\n  IPI Time Series (base 2019Q1 = 100):")
    for q in sorted(ipi.keys()):
        bar = "█" * int(ipi[q] / 5)
        print(f"    {q}  {ipi[q]:>6.1f}  {bar}")

    # ── AI Benchmarks ──────────────────────────────────────────
    print("\n4. Loading AI benchmarks...")

    benchmarks = defaultdict(list)
    bench_cat = {}
    with open(BENCHMARKS_FILE) as f:
        for row in csv.DictReader(f):
            benchmarks[row["benchmark"]].append(
                (datetime.strptime(row["date"], "%Y-%m-%d"), float(row["score"])))
            bench_cat[row["benchmark"]] = row["category_relevance"]

    def interp_quarterly(series, quarters):
        series = sorted(series)
        result = {}
        for q in quarters:
            y, qn = int(q[:4]), int(q[-1])
            qdate = datetime(y, (qn-1)*3+2, 15)
            before = [(d, s) for d, s in series if d <= qdate]
            after = [(d, s) for d, s in series if d > qdate]
            if before and after:
                d0, s0 = before[-1]
                d1, s1 = after[0]
                frac = (qdate - d0).days / max((d1 - d0).days, 1)
                result[q] = s0 + frac * (s1 - s0)
            elif before:
                result[q] = before[-1][1]
            elif after:
                result[q] = after[0][1]
        return result

    cat_to_bench = {
        "coding": ["humaneval", "swe_bench"],
        "writing": ["alpaca_eval", "chatbot_arena"],
        "translation": ["wmt_bleu"],
        "design": ["fid_coco"],
        "data_analysis": ["gsm8k"],
        "data_entry": ["gsm8k"],
        "marketing": ["alpaca_eval"],
        "audio": ["whisper_wer"],
    }

    cat_ai = {}
    for cat, bnames in cat_to_bench.items():
        scores_q = defaultdict(list)
        for bn in bnames:
            for q, s in interp_quarterly(benchmarks.get(bn, []), all_quarters).items():
                scores_q[q].append(s)
        if not scores_q:
            continue
        raw = {q: np.mean(v) for q, v in scores_q.items()}
        mn, mx = min(raw.values()), max(raw.values())
        rng = mx - mn if mx > mn else 1
        if "fid_coco" in bnames and len(bnames) == 1:
            cat_ai[cat] = {q: (1 - (v - mn) / rng) * 100 for q, v in raw.items()}
        else:
            cat_ai[cat] = {q: ((v - mn) / rng) * 100 for q, v in raw.items()}

    # ── Elasticity estimation ──────────────────────────────────
    print("\n5. Estimating price elasticity of intelligence (panel)...")

    elasticity_results = []
    for cat in sorted(cat_chain.keys()):
        if cat not in cat_ai:
            continue
        idx = cat_chain[cat]
        ai = cat_ai[cat]
        common = sorted(set(idx.keys()) & set(ai.keys()))
        if len(common) < 6:
            continue

        prices = np.array([idx[q] for q in common])
        ai_scores = np.array([ai[q] for q in common])

        # Log-log regression
        ln_p = np.log(np.maximum(prices, 1))
        ln_a = np.log(np.maximum(ai_scores, 0.1) + 1)

        slope, intercept, r_value, p_value, std_err = sp_stats.linregress(ln_a, ln_p)

        # Also compute Pearson correlation in levels
        corr, corr_p = sp_stats.pearsonr(prices, ai_scores)

        # Pre/post ChatGPT comparison
        pre_chatgpt = [idx[q] for q in common if quarter_to_float(q) < 2022.75]
        post_chatgpt = [idx[q] for q in common if quarter_to_float(q) >= 2023.0]

        pre_mean = np.mean(pre_chatgpt) if pre_chatgpt else np.nan
        post_mean = np.mean(post_chatgpt) if post_chatgpt else np.nan
        chatgpt_effect = ((post_mean / pre_mean) - 1) * 100 if pre_mean > 0 else np.nan

        price_start = prices[0]
        price_end = prices[-1]
        total_change = (price_end / price_start - 1) * 100

        elasticity_results.append({
            "category": cat,
            "elasticity": slope,
            "se": std_err,
            "t_stat": slope / std_err if std_err > 0 else 0,
            "p_value": p_value,
            "r_squared": r_value ** 2,
            "correlation": corr,
            "corr_p": corr_p,
            "n_quarters": len(common),
            "n_gigs": len(cat_gigs.get(cat, [])),
            "price_start": price_start,
            "price_end": price_end,
            "total_change_pct": total_change,
            "pre_chatgpt_mean": pre_mean,
            "post_chatgpt_mean": post_mean,
            "chatgpt_effect_pct": chatgpt_effect,
        })

    elasticity_results.sort(key=lambda x: x["elasticity"])

    print(f"\n  {'Category':<18} {'β':>7} {'SE':>7} {'p':>8} {'R²':>6} {'ΔP%':>8} {'ChatGPT%':>9}")
    print(f"  {'-'*18} {'-'*7} {'-'*7} {'-'*8} {'-'*6} {'-'*8} {'-'*9}")
    for r in elasticity_results:
        sig = "***" if r["p_value"] < 0.01 else "**" if r["p_value"] < 0.05 else "*" if r["p_value"] < 0.1 else ""
        print(f"  {r['category']:<18} {r['elasticity']:>6.3f}{sig:1} "
              f"{r['se']:>6.3f} {r['p_value']:>7.4f} {r['r_squared']:>5.3f} "
              f"{r['total_change_pct']:>7.1f}% {r['chatgpt_effect_pct']:>8.1f}%")

    # ── Structural breaks ──────────────────────────────────────
    print("\n6. Structural break analysis (panel)...")

    ai_events = [
        ("2022Q4", "ChatGPT (Nov 2022)"),
        ("2023Q1", "GPT-4 (Mar 2023)"),
        ("2022Q3", "Stable Diffusion (Aug 2022)"),
        ("2024Q2", "GPT-4o / Claude 3.5"),
    ]

    break_table = []
    for event_q, event_name in ai_events:
        eqf = quarter_to_float(event_q)
        for cat, idx in cat_chain.items():
            pre = [idx[q] for q in sorted(idx) if eqf - 1.25 <= quarter_to_float(q) < eqf]
            post = [idx[q] for q in sorted(idx) if eqf <= quarter_to_float(q) <= eqf + 1.0]
            if len(pre) >= 2 and len(post) >= 2:
                pm, pom = np.mean(pre), np.mean(post)
                chg = (pom / pm - 1) * 100
                break_table.append({
                    "event": event_name, "category": cat,
                    "pre": pm, "post": pom, "change_pct": chg,
                })

    print(f"\n  {'Event':<25} {'Category':<15} {'Pre':>7} {'Post':>7} {'Δ%':>8}")
    print(f"  {'-'*25} {'-'*15} {'-'*7} {'-'*7} {'-'*8}")
    for r in sorted(break_table, key=lambda x: x["change_pct"]):
        print(f"  {r['event']:<25} {r['category']:<15} "
              f"{r['pre']:>6.1f} {r['post']:>6.1f} {r['change_pct']:>7.1f}%")

    # ── Write outputs ──────────────────────────────────────────
    print("\n7. Writing outputs...")

    with open(OUTPUT_IPI, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quarter", "ipi"])
        for q in sorted(ipi.keys()):
            w.writerow([q, f"{ipi[q]:.2f}"])

    with open(OUTPUT_CAT, "w", newline="") as f:
        w = csv.writer(f)
        cats = sorted(cat_chain.keys())
        w.writerow(["quarter"] + cats)
        for q in sorted(all_quarters):
            row = [q] + [f"{cat_chain[c].get(q, ''):.2f}"
                         if q in cat_chain.get(c, {}) else ""
                         for c in cats]
            w.writerow(row)

    with open(OUTPUT_ELAST, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "category", "elasticity", "se", "p_value", "r_squared",
            "correlation", "n_quarters", "n_gigs",
            "total_change_pct", "chatgpt_effect_pct",
        ])
        w.writeheader()
        for r in elasticity_results:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v)
                        for k, v in r.items() if k in w.fieldnames})

    # ── Generate summary ───────────────────────────────────────
    ipi_sorted = sorted(ipi.items())
    ipi_start = ipi_sorted[0][1] if ipi_sorted else 100
    ipi_end = ipi_sorted[-1][1] if ipi_sorted else 100
    ipi_change = (ipi_end / ipi_start - 1) * 100

    # Find the IPI at ChatGPT launch
    chatgpt_ipi = ipi.get("2022Q4") or ipi.get("2023Q1")
    post_ai_change = ((ipi_end / chatgpt_ipi) - 1) * 100 if chatgpt_ipi else 0

    lines = [
        "# Panel-Based Intelligence Price Index — Summary",
        "",
        f"**Generated:** {date.today().isoformat()}",
        f"**Method:** Matched-model panel (Jevons elementary, Törnqvist composite)",
        f"**Panel gigs:** {len(panel_gigs):,} (observed in ≥2 quarters)",
        f"**Time span:** {all_quarters[0]}–{all_quarters[-1]}",
        f"**Base period:** 2019Q1 = 100",
        "",
        "## Headline",
        "",
        f"- **Overall IPI:** {ipi_start:.1f} → {ipi_end:.1f} ({ipi_change:+.1f}% total)",
        f"- **Post-ChatGPT IPI change:** {post_ai_change:+.1f}% (from {chatgpt_ipi:.1f} to {ipi_end:.1f})",
        "",
        "## Category Elasticities (Price Elasticity of Intelligence)",
        "",
        "| Category | β | SE | p | R² | Total Δ% | Post-ChatGPT Δ% | Gigs |",
        "|----------|---|----|----|---|---------|----------------|------|",
    ]
    for r in elasticity_results:
        sig = "***" if r["p_value"] < 0.01 else "**" if r["p_value"] < 0.05 else "*" if r["p_value"] < 0.1 else ""
        lines.append(
            f"| {r['category']} | {r['elasticity']:.3f}{sig} | {r['se']:.3f} | "
            f"{r['p_value']:.3f} | {r['r_squared']:.2f} | {r['total_change_pct']:+.1f}% | "
            f"{r['chatgpt_effect_pct']:+.1f}% | {r['n_gigs']} |"
        )

    lines += [
        "",
        "## IPI Time Series",
        "",
        "| Quarter | IPI | Δ from base |",
        "|---------|-----|------------|",
    ]
    for q, v in sorted(ipi.items()):
        lines.append(f"| {q} | {v:.1f} | {v - 100:+.1f} |")

    lines += [
        "",
        "## Structural Breaks",
        "",
        "| Event | Category | Pre | Post | Δ% |",
        "|-------|---------|-----|------|----|",
    ]
    for r in sorted(break_table, key=lambda x: x["change_pct"])[:15]:
        lines.append(f"| {r['event']} | {r['category']} | {r['pre']:.1f} | "
                     f"{r['post']:.1f} | {r['change_pct']:+.1f}% |")

    with open(OUTPUT_SUMMARY, "w") as f:
        f.write("\n".join(lines))
    print(f"  {OUTPUT_SUMMARY}")

    # ── Final ──────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("PANEL IPI COMPLETE")
    print(f"{'='*60}")
    print(f"  IPI: {ipi_start:.1f} → {ipi_end:.1f} ({ipi_change:+.1f}%)")
    print(f"  Post-ChatGPT: {post_ai_change:+.1f}%")
    neg_elast = sum(1 for r in elasticity_results if r["elasticity"] < 0)
    print(f"  Negative elasticities: {neg_elast}/{len(elasticity_results)}")
    sig = sum(1 for r in elasticity_results if r["p_value"] < 0.05)
    print(f"  Significant (p<0.05): {sig}/{len(elasticity_results)}")


if __name__ == "__main__":
    main()
