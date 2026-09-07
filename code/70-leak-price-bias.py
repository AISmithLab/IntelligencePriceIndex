#!/usr/bin/env python3
"""
Step 70: Are the gigs step 04 leaks into `uncategorized` priced like the ones it keeps?

Step 68 sized the leak at 88,320 gigs -- listings that belong to a collected domain
but fail step 04's exact-substring keyword test (`develop-or-customize-drupal-websites`
misses coding's `web-develop`/`app-develop`/`developer`). That makes category membership
a function of how a seller worded a slug. The open question is whether the misses are
RANDOM with respect to price and AI exposure. If AI-era listings use newer vocabulary
than the 2023-era keyword lists, the miss correlates with the treatment and the defect
is in the published seven, not only in the uncollected headroom.

WHY THIS COSTS NO CRAWL. Every category-targeted collection (`38`, `41`, `13`) selected
gigs BY step-04 label, so none of them can contain a leaked gig -- they are censored by
construction. The 500-seller pilot (`06c`/`07`) is the exception: it sampled SELLERS and
took their gigs whatever the label, so it is category-blind and already holds 585
uncategorized gigs with 5,639 extracted price rows on disk. That is the test bed.

Comparison, within each domain D, over gigs the pilot already extracted:
  KEPT   -- step 04 assigned D
  LEAKED -- step 04 said uncategorized, step 68's broader stems say D
on (a) price level in logs, (b) within-gig log price trend, (c) AI-vocabulary rate.

Input:  data/pilot/pilot-prices.csv
        code/04-classify-categories.py   (CATEGORIES, classify_slug)
        code/68-uncategorized-families.py (NEW_FAMILIES, LEAKAGE_STEMS, first_match)
Output: runs/uncollected-headroom/leak-price-bias.md
"""

import csv
import importlib.util
import math
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from scipy import stats

BASE_DIR = Path(__file__).resolve().parent.parent
PRICES = BASE_DIR / "data" / "pilot" / "pilot-prices.csv"
OUTDIR = BASE_DIR / "runs" / "uncollected-headroom"

PRICE_MAX = 10000.0
DOMAINS = ["design", "coding", "writing", "marketing", "audio", "video", "translation"]


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, BASE_DIR / "code" / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


c4 = _load("04-classify-categories.py", "c4")
c68 = _load("68-uncategorized-families.py", "c68")

# AI vocabulary, mirroring step 57's AI_GEN stems at slug/title level.
AI_RE = re.compile(
    r"\b(ai|a\.i\.|artificial[-\s]intelligence|chatgpt|gpt|midjourney|dall[-\s]?e|"
    r"stable[-\s]diffusion|generative|llm|prompt[-\s]engineer|copilot|claude|"
    r"leonardo[-\s]ai|runway|elevenlabs|synthesia|firefly)\b", re.I)


def label(slug):
    """(bucket, domain) where bucket is 'kept' | 'leaked' | 'other'."""
    cats = c4.classify_slug(slug)
    if cats != ["uncategorized"]:
        d = cats[0]
        return ("kept", d) if d in DOMAINS else ("other", d)
    s = slug.lower()
    if c68.first_match(s, c68.NEW_FAMILIES):        # a genuinely new family, not a leak
        return ("other", None)
    lk = c68.first_match(s, c68.LEAKAGE_STEMS)
    if lk in DOMAINS:
        return ("leaked", lk)
    return ("other", None)


def quarter(y, m):
    return f"{y}Q{(int(m) - 1) // 3 + 1}"


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # gig -> (bucket, domain); gig -> [(quarter, price, title)]
    meta, obs = {}, defaultdict(list)
    with open(PRICES) as f:
        for r in csv.DictReader(f):
            try:
                p = float(r["price_basic"])
            except (TypeError, ValueError):
                continue
            if not (0 < p <= PRICE_MAX):
                continue
            gid = f"{r['seller']}/{r['slug']}"
            if gid not in meta:
                meta[gid] = label(r["slug"])
            obs[gid].append((quarter(r["year"], r["month"]), p, r["title"] or ""))

    rows = {}   # (domain, bucket) -> dict of stats inputs
    for gid, (bucket, dom) in meta.items():
        if bucket == "other" or dom not in DOMAINS:
            continue
        seq = sorted(obs[gid])
        if not seq:
            continue
        d = rows.setdefault((dom, bucket), {"logp": [], "trend": [], "ai": 0, "n": 0,
                                            "rowcount": 0, "qspan": []})
        d["n"] += 1
        d["rowcount"] += len(seq)
        d["logp"].append(statistics.median([math.log(p) for _, p, _ in seq]))
        if len(seq) >= 2 and seq[0][0] != seq[-1][0]:
            d["trend"].append(math.log(seq[-1][1]) - math.log(seq[0][1]))
        d["qspan"].append(len({q for q, _, _ in seq}))
        text = gid + " " + " ".join(t for _, _, t in seq)
        if AI_RE.search(text):
            d["ai"] += 1

    def fmt(x, nd=3):
        return "n/a" if x is None else f"{x:.{nd}f}"

    L = []
    L.append("# Does step 04's leak bias price? Measured on the category-blind pilot\n")
    L.append("Corpus: `data/pilot/pilot-prices.csv` — the 500-seller pilot, the only "
             "collection sampled by SELLER rather than by step-04 label, so it is the only "
             "one that contains leaked gigs at all. No crawl.\n")
    L.append("`KEPT` = step 04 assigned the domain. `LEAKED` = step 04 said `uncategorized`, "
             "step 68's broader stems say the domain. Gigs matching a genuinely new family "
             "(photography, gaming, legal, …) are excluded, not counted as leaks.\n")

    L.append("## Price level (median of each gig's median log price)\n")
    L.append("| domain | kept n | leaked n | kept median $ | leaked median $ | log gap | Mann-Whitney p |")
    L.append("|---|---:|---:|---:|---:|---:|---:|")
    level_flags = []
    for dom in DOMAINS:
        k = rows.get((dom, "kept"))
        lk = rows.get((dom, "leaked"))
        if not k or not lk or lk["n"] < 5:
            L.append(f"| {dom} | {k['n'] if k else 0} | {lk['n'] if lk else 0} | — | — | — | too thin |")
            continue
        mk, ml = statistics.median(k["logp"]), statistics.median(lk["logp"])
        p = stats.mannwhitneyu(k["logp"], lk["logp"], alternative="two-sided").pvalue
        star = "**" if p < 0.05 else ""
        if p < 0.05:
            level_flags.append(dom)
        L.append(f"| {dom} | {k['n']} | {lk['n']} | {math.exp(mk):.2f} | {math.exp(ml):.2f} "
                 f"| {star}{ml - mk:+.3f}{star} | {p:.3f} |")

    L.append("\n## Price trend (within-gig log change, first to last observed quarter)\n")
    L.append("| domain | kept n | leaked n | kept mean Δlog | leaked mean Δlog | difference | t-test p |")
    L.append("|---|---:|---:|---:|---:|---:|---:|")
    trend_flags = []
    for dom in DOMAINS:
        k = rows.get((dom, "kept"))
        lk = rows.get((dom, "leaked"))
        if not k or not lk or len(lk["trend"]) < 5 or len(k["trend"]) < 5:
            L.append(f"| {dom} | {len(k['trend']) if k else 0} | {len(lk['trend']) if lk else 0} "
                     f"| — | — | — | too thin |")
            continue
        mk, ml = statistics.mean(k["trend"]), statistics.mean(lk["trend"])
        p = stats.ttest_ind(k["trend"], lk["trend"], equal_var=False).pvalue
        star = "**" if p < 0.05 else ""
        if p < 0.05:
            trend_flags.append(dom)
        L.append(f"| {dom} | {len(k['trend'])} | {len(lk['trend'])} | {mk:+.3f} | {ml:+.3f} "
                 f"| {star}{ml - mk:+.3f}{star} | {p:.3f} |")

    L.append("\n## AI vocabulary in slug or title\n")
    L.append("This is the mechanism to rule out: if leaked listings are more AI-era than kept "
             "ones, the miss correlates with the treatment.\n")
    L.append("| domain | kept AI share | leaked AI share | Fisher p |")
    L.append("|---|---:|---:|---:|")
    ai_flags = []
    for dom in DOMAINS:
        k = rows.get((dom, "kept"))
        lk = rows.get((dom, "leaked"))
        if not k or not lk or lk["n"] < 5:
            L.append(f"| {dom} | — | — | too thin |")
            continue
        p = stats.fisher_exact([[k["ai"], k["n"] - k["ai"]],
                                [lk["ai"], lk["n"] - lk["ai"]]]).pvalue
        star = "**" if p < 0.05 else ""
        if p < 0.05:
            ai_flags.append(dom)
        L.append(f"| {dom} | {k['ai']}/{k['n']} ({100*k['ai']/k['n']:.1f}%) "
                 f"| {star}{lk['ai']}/{lk['n']} ({100*lk['ai']/lk['n']:.1f}%){star} | {p:.3f} |")

    L.append("\n## Verdict\n")
    L.append(f"- Domains where LEAKED price **level** differs from KEPT at p<0.05: "
             f"**{', '.join(level_flags) if level_flags else 'none'}**")
    L.append(f"- Domains where LEAKED price **trend** differs at p<0.05: "
             f"**{', '.join(trend_flags) if trend_flags else 'none'}**")
    L.append(f"- Domains where LEAKED **AI-vocabulary rate** differs at p<0.05: "
             f"**{', '.join(ai_flags) if ai_flags else 'none'}**")
    L.append("")
    L.append("Power caveat: the pilot is 500 sellers, so per-domain leaked cells are tens of "
             "gigs, not thousands. A null here bounds the bias loosely — it does not prove the "
             "leak is innocuous at the scale of the 88,320-gig population.")

    out = "\n".join(L) + "\n"
    (OUTDIR / "leak-price-bias.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
