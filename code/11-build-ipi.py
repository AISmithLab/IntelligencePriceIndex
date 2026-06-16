#!/usr/bin/env python3
"""
Build the Intelligence Price Index (IPI) — a CPI-style weighted index
tracking the price of cognitive labor as AI capabilities improve.

Methodology (CPI analogy):
  - CPI basket items  →  gig service categories (writing, coding, design, etc.)
  - CPI prices        →  median gig prices per category per quarter
  - CPI weights       →  transaction volume (review counts as proxy)
  - CPI base period   →  Q1 2019 (pre-GPT era)

Additional analysis:
  - Category-level price indices
  - Correlation with AI benchmark scores
  - Price elasticity of intelligence
  - Structural break detection around AI launches

Output:
  data/pilot/ipi-quarterly.csv       — quarterly IPI values
  data/pilot/category-indices.csv    — per-category price indices
  data/pilot/elasticity-estimates.csv — price elasticity of intelligence
  data/pilot/ipi-analysis-summary.md — human-readable results
"""

import csv
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PRICES_FILE = BASE_DIR / "data" / "pilot" / "pilot-prices.csv"
ITEMS_FILE = BASE_DIR / "data" / "pilot" / "gig-items.csv"
BENCHMARKS_FILE = BASE_DIR / "data" / "ai-benchmarks.csv"

OUTPUT_IPI = BASE_DIR / "data" / "pilot" / "ipi-quarterly.csv"
OUTPUT_CAT = BASE_DIR / "data" / "pilot" / "category-indices.csv"
OUTPUT_ELAST = BASE_DIR / "data" / "pilot" / "elasticity-estimates.csv"
OUTPUT_SUMMARY = BASE_DIR / "data" / "pilot" / "ipi-analysis-summary.md"


# Category mapping: gig cluster keywords → broad categories
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
    """Classify a gig into a broad category based on description + cluster label."""
    text = (description + " " + item_label).lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for kw in keywords if kw in text)
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    return "other"


def to_quarter(year, month):
    """Convert year/month to quarter string like '2019Q1'."""
    try:
        y = int(year)
        m = int(month)
        q = (m - 1) // 3 + 1
        return f"{y}Q{q}"
    except (ValueError, TypeError):
        return None


def quarter_to_float(q):
    """Convert '2019Q1' to 2019.0, '2019Q2' to 2019.25, etc."""
    y = int(q[:4])
    qn = int(q[-1])
    return y + (qn - 1) * 0.25


def main():
    print("=" * 60)
    print("BUILDING INTELLIGENCE PRICE INDEX")
    print("=" * 60)

    # ── Step 1: Load data ──────────────────────────────────────
    print("\n1. Loading data...")

    # Load item mappings
    item_map = {}  # (seller, slug) → (item_id, item_label, description)
    with open(ITEMS_FILE) as f:
        for row in csv.DictReader(f):
            item_map[(row["seller"], row["slug"])] = (
                int(row["item_id"]),
                row["item_label"],
                row["description"],
            )

    # Load prices and classify
    observations = []
    with open(PRICES_FILE) as f:
        for row in csv.DictReader(f):
            key = (row["seller"], row["slug"])
            item_id, item_label, description = item_map.get(key, (-1, "", ""))
            if item_id == -1:
                continue

            price = float(row.get("price_basic", 0) or 0)
            if price <= 0 or price > 10000:
                continue

            quarter = to_quarter(row["year"], row["month"])
            if not quarter:
                continue

            cat = classify_gig(description, item_label)
            reviews = int(row.get("review_count", 0) or 0)

            observations.append({
                "seller": row["seller"],
                "slug": row["slug"],
                "item_id": item_id,
                "category": cat,
                "quarter": quarter,
                "year": int(row["year"]),
                "price": price,
                "reviews": reviews,
            })

    print(f"  {len(observations):,} price observations loaded")

    # ── Step 2: Category classification summary ────────────────
    cat_counts = defaultdict(int)
    for obs in observations:
        cat_counts[obs["category"]] += 1
    print("\n  Category distribution:")
    for cat, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat:<20} {cnt:>6,} obs")

    # ── Step 3: Compute quarterly median prices per category ───
    print("\n2. Computing quarterly category price indices...")

    # Group: (category, quarter) → list of prices
    cat_quarter_prices = defaultdict(list)
    cat_quarter_reviews = defaultdict(int)
    for obs in observations:
        cat_quarter_prices[(obs["category"], obs["quarter"])].append(obs["price"])
        cat_quarter_reviews[(obs["category"], obs["quarter"])] += obs["reviews"]

    # Get all quarters, sorted
    all_quarters = sorted(set(obs["quarter"] for obs in observations))
    print(f"  Time span: {all_quarters[0]} to {all_quarters[-1]}")
    print(f"  {len(all_quarters)} quarters")

    # Categories with enough data
    categories = [c for c, cnt in cat_counts.items()
                  if cnt >= 50 and c != "other"]
    print(f"  Categories with ≥50 obs: {categories}")

    # Base period: Q1 2019 (pre-GPT era), fall back to earliest available
    BASE_QUARTER = "2019Q1"

    # Compute category-level price indices (base = 100)
    cat_indices = {}  # category → {quarter → index_value}
    for cat in categories:
        # Find base price
        base_prices = cat_quarter_prices.get((cat, BASE_QUARTER), [])
        if not base_prices:
            # Use earliest available quarter
            for q in all_quarters:
                base_prices = cat_quarter_prices.get((cat, q), [])
                if base_prices:
                    break
        if not base_prices:
            continue

        base_median = float(np.median(base_prices))
        if base_median <= 0:
            continue

        cat_indices[cat] = {}
        for q in all_quarters:
            prices = cat_quarter_prices.get((cat, q), [])
            if len(prices) >= 3:  # minimum observations
                median_price = float(np.median(prices))
                cat_indices[cat][q] = (median_price / base_median) * 100
            # else: missing quarter

    # ── Step 4: Compute the composite IPI ──────────────────────
    print("\n3. Computing composite IPI (Laspeyres-style)...")

    # Weights: average review count per category in base period year
    # (proxy for transaction volume, like CPI expenditure weights)
    base_year = 2019
    cat_weights = {}
    for cat in categories:
        total_reviews = 0
        n_quarters = 0
        for q in all_quarters:
            if q.startswith(str(base_year)):
                revs = cat_quarter_reviews.get((cat, q), 0)
                if revs > 0:
                    total_reviews += revs
                    n_quarters += 1
        if n_quarters > 0:
            cat_weights[cat] = total_reviews / n_quarters
        else:
            # Fall back to observation count as weight
            cat_weights[cat] = cat_counts.get(cat, 1)

    # Normalize weights to sum to 1
    total_weight = sum(cat_weights.values())
    for cat in cat_weights:
        cat_weights[cat] /= total_weight

    print("  Category weights:")
    for cat, w in sorted(cat_weights.items(), key=lambda x: -x[1]):
        print(f"    {cat:<20} {w:.3f}")

    # Compute Laspeyres composite index
    ipi_values = {}  # quarter → IPI value
    for q in all_quarters:
        weighted_sum = 0
        weight_sum = 0
        for cat in categories:
            if cat in cat_indices and q in cat_indices[cat]:
                w = cat_weights.get(cat, 0)
                weighted_sum += w * cat_indices[cat][q]
                weight_sum += w
        if weight_sum > 0.3:  # need at least 30% of weights represented
            ipi_values[q] = weighted_sum / weight_sum

    print(f"\n  IPI computed for {len(ipi_values)} quarters")

    # ── Step 5: Load AI benchmarks and compute correlations ────
    print("\n4. Loading AI benchmark data and computing correlations...")

    benchmarks = defaultdict(list)  # benchmark_name → [(date, score)]
    bench_category = {}  # benchmark_name → category
    with open(BENCHMARKS_FILE) as f:
        for row in csv.DictReader(f):
            bname = row["benchmark"]
            bdate = datetime.strptime(row["date"], "%Y-%m-%d")
            bscore = float(row["score"])
            benchmarks[bname].append((bdate, bscore))
            bench_category[bname] = row["category_relevance"]

    # Interpolate benchmark scores to quarterly
    def interpolate_to_quarters(series, quarters):
        """Linearly interpolate a time series to quarterly values."""
        series = sorted(series)
        result = {}
        for q in quarters:
            y = int(q[:4])
            qn = int(q[-1])
            m = (qn - 1) * 3 + 2  # middle of quarter
            qdate = datetime(y, m, 15)

            # Find bracketing points
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

    bench_quarterly = {}
    for bname, series in benchmarks.items():
        bench_quarterly[bname] = interpolate_to_quarters(series, all_quarters)

    # Compute composite AI capability index per category
    # Map categories to relevant benchmarks
    cat_to_benchmarks = {
        "coding": ["humaneval", "swe_bench"],
        "writing": ["alpaca_eval", "chatbot_arena"],
        "translation": ["wmt_bleu"],
        "design": ["fid_coco"],
        "data_analysis": ["gsm8k"],
        "data_entry": ["gsm8k"],  # general LLM capability proxy
        "marketing": ["alpaca_eval"],  # writing/content proxy
        "audio": ["whisper_wer"],
    }

    # For each category, compute a composite AI capability index (0-100 normalized)
    cat_ai_index = {}  # category → {quarter → normalized_score}
    for cat, bnames in cat_to_benchmarks.items():
        scores_by_q = defaultdict(list)
        for bname in bnames:
            bq = bench_quarterly.get(bname, {})
            for q, score in bq.items():
                scores_by_q[q].append(score)
        if not scores_by_q:
            continue

        # Average across benchmarks, then normalize to 0-100
        raw = {q: np.mean(vals) for q, vals in scores_by_q.items()}
        if not raw:
            continue
        min_s = min(raw.values())
        max_s = max(raw.values())
        rng = max_s - min_s if max_s > min_s else 1
        # For FID (lower is better), invert
        if "fid_coco" in bnames and len(bnames) == 1:
            cat_ai_index[cat] = {q: (1 - (v - min_s) / rng) * 100
                                  for q, v in raw.items()}
        else:
            cat_ai_index[cat] = {q: ((v - min_s) / rng) * 100
                                  for q, v in raw.items()}

    # ── Step 6: Compute price elasticity of intelligence ───────
    print("\n5. Estimating price elasticity of intelligence...")

    elasticity_results = []
    for cat in categories:
        if cat not in cat_indices or cat not in cat_ai_index:
            continue

        # Align quarters
        common_qs = sorted(set(cat_indices[cat].keys()) &
                           set(cat_ai_index[cat].keys()))
        if len(common_qs) < 4:
            continue

        price_series = [cat_indices[cat][q] for q in common_qs]
        ai_series = [cat_ai_index[cat][q] for q in common_qs]

        # Log-log regression: ln(price_index) = α + β × ln(ai_index + 1)
        # β is the price elasticity of intelligence
        ln_price = [math.log(max(p, 1)) for p in price_series]
        ln_ai = [math.log(max(a, 1) + 1) for a in ai_series]

        n = len(common_qs)
        if n < 4:
            continue

        # OLS
        x_mean = np.mean(ln_ai)
        y_mean = np.mean(ln_price)
        ss_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(ln_ai, ln_price))
        ss_xx = sum((x - x_mean) ** 2 for x in ln_ai)
        if ss_xx == 0:
            continue

        beta = ss_xy / ss_xx
        alpha = y_mean - beta * x_mean

        # R²
        y_pred = [alpha + beta * x for x in ln_ai]
        ss_res = sum((y - yp) ** 2 for y, yp in zip(ln_price, y_pred))
        ss_tot = sum((y - y_mean) ** 2 for y in ln_price)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        # Standard error of beta
        if n > 2:
            se_resid = math.sqrt(ss_res / (n - 2))
            se_beta = se_resid / math.sqrt(ss_xx)
            t_stat = beta / se_beta if se_beta > 0 else 0
        else:
            se_beta = float("inf")
            t_stat = 0

        # Pearson correlation (levels)
        corr = np.corrcoef(price_series, ai_series)[0, 1]

        elasticity_results.append({
            "category": cat,
            "elasticity": beta,
            "se": se_beta,
            "t_stat": t_stat,
            "r_squared": r2,
            "correlation": corr,
            "n_quarters": n,
            "price_start": price_series[0],
            "price_end": price_series[-1],
            "price_change_pct": (price_series[-1] / price_series[0] - 1) * 100,
            "ai_start": ai_series[0],
            "ai_end": ai_series[-1],
        })

    # Sort by elasticity magnitude
    elasticity_results.sort(key=lambda x: x["elasticity"])

    print("\n  Price Elasticity of Intelligence by Category:")
    print(f"  {'Category':<20} {'β':>8} {'SE':>8} {'t':>8} {'R²':>6} {'ρ':>7} {'ΔP%':>8}")
    print(f"  {'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*6} {'-'*7} {'-'*8}")
    for r in elasticity_results:
        sig = "***" if abs(r["t_stat"]) > 2.58 else "**" if abs(r["t_stat"]) > 1.96 else "*" if abs(r["t_stat"]) > 1.64 else ""
        print(f"  {r['category']:<20} {r['elasticity']:>7.3f}{sig} "
              f"{r['se']:>7.3f} {r['t_stat']:>7.2f} {r['r_squared']:>5.2f} "
              f"{r['correlation']:>6.3f} {r['price_change_pct']:>7.1f}%")

    # ── Step 7: Detect structural breaks around AI launches ────
    print("\n6. Detecting structural breaks around key AI launches...")

    ai_events = [
        ("2022Q4", "ChatGPT launch"),
        ("2023Q1", "GPT-4 launch"),
        ("2022Q3", "Stable Diffusion launch"),
        ("2023Q2", "Midjourney v5"),
        ("2024Q2", "GPT-4o / Claude 3.5"),
    ]

    break_results = []
    for event_q, event_name in ai_events:
        for cat in categories:
            if cat not in cat_indices:
                continue
            idx = cat_indices[cat]
            # Pre-event: 4 quarters before
            event_qf = quarter_to_float(event_q)
            pre_qs = [q for q in all_quarters
                      if event_qf - 1.25 <= quarter_to_float(q) < event_qf
                      and q in idx]
            post_qs = [q for q in all_quarters
                       if event_qf <= quarter_to_float(q) <= event_qf + 1.0
                       and q in idx]

            if len(pre_qs) >= 2 and len(post_qs) >= 2:
                pre_mean = np.mean([idx[q] for q in pre_qs])
                post_mean = np.mean([idx[q] for q in post_qs])
                change = post_mean - pre_mean
                change_pct = (post_mean / pre_mean - 1) * 100 if pre_mean > 0 else 0

                break_results.append({
                    "event": event_name,
                    "event_quarter": event_q,
                    "category": cat,
                    "pre_mean": pre_mean,
                    "post_mean": post_mean,
                    "change_pct": change_pct,
                })

    if break_results:
        print(f"\n  {'Event':<25} {'Category':<15} {'Pre':>7} {'Post':>7} {'Δ%':>8}")
        print(f"  {'-'*25} {'-'*15} {'-'*7} {'-'*7} {'-'*8}")
        for r in sorted(break_results, key=lambda x: x["change_pct"]):
            print(f"  {r['event']:<25} {r['category']:<15} "
                  f"{r['pre_mean']:>6.1f} {r['post_mean']:>6.1f} "
                  f"{r['change_pct']:>7.1f}%")

    # ── Step 8: Write outputs ──────────────────────────────────
    print("\n7. Writing outputs...")

    # IPI quarterly
    with open(OUTPUT_IPI, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quarter", "ipi", "year"])
        for q in sorted(ipi_values.keys()):
            w.writerow([q, f"{ipi_values[q]:.2f}", q[:4]])
    print(f"  {OUTPUT_IPI}")

    # Category indices
    with open(OUTPUT_CAT, "w", newline="") as f:
        w = csv.writer(f)
        header = ["quarter"] + sorted(categories)
        w.writerow(header)
        for q in sorted(all_quarters):
            row = [q]
            for cat in sorted(categories):
                val = cat_indices.get(cat, {}).get(q, "")
                row.append(f"{val:.2f}" if val != "" else "")
            w.writerow(row)
    print(f"  {OUTPUT_CAT}")

    # Elasticity estimates
    with open(OUTPUT_ELAST, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "category", "elasticity", "se", "t_stat", "r_squared",
            "correlation", "n_quarters", "price_change_pct",
        ])
        w.writeheader()
        for r in elasticity_results:
            w.writerow({k: f"{v:.4f}" if isinstance(v, float) else v
                        for k, v in r.items()
                        if k in w.fieldnames})
    print(f"  {OUTPUT_ELAST}")

    # ── Step 9: Generate analysis summary ──────────────────────
    print("\n8. Generating analysis summary...")

    # Key findings
    ipi_start = ipi_values.get("2019Q1") or ipi_values.get(min(ipi_values.keys()))
    ipi_end = ipi_values.get(max(ipi_values.keys()))
    ipi_change = (ipi_end / ipi_start - 1) * 100 if ipi_start else 0

    # Find most/least deflated categories
    cat_changes = []
    for r in elasticity_results:
        cat_changes.append((r["category"], r["price_change_pct"], r["elasticity"]))

    summary_lines = [
        "# Intelligence Price Index — Analysis Summary",
        "",
        f"**Generated:** {date.today().isoformat()}",
        f"**Data:** {len(observations):,} price observations, {len(set(o['seller'] for o in observations))} sellers, "
        f"{len(set((o['seller'], o['slug']) for o in observations)):,} gigs",
        f"**Time span:** {all_quarters[0]} to {all_quarters[-1]}",
        f"**Base period:** {BASE_QUARTER} = 100",
        "",
        "## Headline Results",
        "",
        f"**Composite IPI:** {ipi_start:.1f} → {ipi_end:.1f} ({ipi_change:+.1f}% over period)",
        "",
    ]

    if ipi_change < 0:
        summary_lines.append(
            f"The Intelligence Price Index fell by {abs(ipi_change):.1f}% from the base period, "
            f"indicating significant deflationary pressure on cognitive labor prices as AI capabilities improved."
        )
    else:
        summary_lines.append(
            f"The composite IPI rose {ipi_change:.1f}%, though category-level analysis reveals "
            f"heterogeneous patterns with some categories experiencing significant deflation."
        )

    summary_lines += [
        "",
        "## Category Price Changes",
        "",
        "| Category | Price Δ% | Elasticity (β) | R² | Interpretation |",
        "|----------|---------|----------------|-----|----------------|",
    ]

    for r in elasticity_results:
        if r["price_change_pct"] < -15:
            interp = "Strong deflation"
        elif r["price_change_pct"] < -5:
            interp = "Moderate deflation"
        elif r["price_change_pct"] < 5:
            interp = "Stable"
        elif r["price_change_pct"] < 15:
            interp = "Moderate inflation"
        else:
            interp = "Price increase"
        sig = "***" if abs(r["t_stat"]) > 2.58 else "**" if abs(r["t_stat"]) > 1.96 else "*" if abs(r["t_stat"]) > 1.64 else ""
        summary_lines.append(
            f"| {r['category']} | {r['price_change_pct']:+.1f}% | "
            f"{r['elasticity']:.3f}{sig} | {r['r_squared']:.2f} | {interp} |"
        )

    summary_lines += [
        "",
        "## IPI Time Series",
        "",
        "| Quarter | IPI |",
        "|---------|-----|",
    ]
    for q in sorted(ipi_values.keys()):
        summary_lines.append(f"| {q} | {ipi_values[q]:.1f} |")

    summary_lines += [
        "",
        "## AI Breakthrough Impact",
        "",
        "| Event | Quarter | Most Affected Category | Price Δ% |",
        "|-------|---------|----------------------|---------|",
    ]
    # Group breaks by event, pick most affected category
    from itertools import groupby
    event_sorted = sorted(break_results, key=lambda x: x["event"])
    for event, group in groupby(event_sorted, key=lambda x: x["event"]):
        items = list(group)
        most_affected = min(items, key=lambda x: x["change_pct"])
        summary_lines.append(
            f"| {event} | {most_affected['event_quarter']} | "
            f"{most_affected['category']} | {most_affected['change_pct']:+.1f}% |"
        )

    summary_lines += [
        "",
        "## Key Interpretation",
        "",
        "The **price elasticity of intelligence** measures how sensitive gig prices are to AI capability ",
        "improvements. A negative elasticity (β < 0) means prices fall as AI gets better — the market ",
        "is pricing in AI substitution. The magnitude tells us how much: β = -0.5 means a 10% improvement ",
        "in AI capability is associated with a ~5% decline in the price of that service.",
        "",
        "Categories with the most negative elasticity are where AI is most directly substituting for human labor. ",
        "Categories with near-zero or positive elasticity may reflect complementarity — AI makes workers more ",
        "productive, allowing them to command higher prices, or the task requires human judgment that AI cannot yet replicate.",
    ]

    with open(OUTPUT_SUMMARY, "w") as f:
        f.write("\n".join(summary_lines))
    print(f"  {OUTPUT_SUMMARY}")

    # ── Final summary ──────────────────────────────────────────
    print(f"\n{'='*60}")
    print("IPI CONSTRUCTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Composite IPI: {ipi_start:.1f} → {ipi_end:.1f} ({ipi_change:+.1f}%)")
    print(f"  Categories analyzed: {len(elasticity_results)}")
    significant = sum(1 for r in elasticity_results if abs(r["t_stat"]) > 1.96)
    print(f"  Significant elasticities (p<0.05): {significant}/{len(elasticity_results)}")
    most_deflated = min(elasticity_results, key=lambda x: x["price_change_pct"])
    print(f"  Most deflated: {most_deflated['category']} ({most_deflated['price_change_pct']:+.1f}%)")
    if any(r["price_change_pct"] > 0 for r in elasticity_results):
        least_deflated = max(elasticity_results, key=lambda x: x["price_change_pct"])
        print(f"  Least deflated: {least_deflated['category']} ({least_deflated['price_change_pct']:+.1f}%)")


if __name__ == "__main__":
    main()
