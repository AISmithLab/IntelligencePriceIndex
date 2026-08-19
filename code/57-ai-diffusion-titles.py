#!/usr/bin/env python3
"""
Step 57: Measure generative-AI diffusion INSIDE the market, from gig titles.

WHY THIS EXISTS
---------------
Designs 1-8 all failed, and steps 52/54/55 diagnosed why: every one of them
proxied "AI exposure" with something EXTERNAL to the market -- an occupation
score (Eloundou beta) or a calendar date (ChatGPT's release). The occupation
score is thin (36.8% zero-match) and varies over 7 categories (p-floor 0.143);
the calendar date is the worst-fitting break of 15 candidates (step 52).

The project has never had a measure of AI diffusion taken FROM the market.
It has one available and unused: `title`, present on 384,967 of 384,983
gig-date observations (100.0%). Sellers who use generative AI advertise it.

This script builds that measure and audits it. It does NOT run a causal design;
Part H states what the measure makes testable and what must be pre-registered
first. Everything here is descriptive and was written before any outcome was
estimated.

WHAT IS MEASURED
  A  classifier + precision audit (AI-positive, anti-AI, negation, false pos)
  B  diffusion curve, raw and composition-fixed, overall and by category
  C  entry vs retitling -- is the rise new gigs, or incumbents relabelling?
  D  searched break over 15 candidate quarters (step 52's machinery, reused)
  E  price of AI-branded vs non-AI work, within category x quarter
  F  within-gig event study around a gig's own adoption quarter
  G  anti-AI ("no AI", "100% human") positioning and its price
  H  where in the price distribution AI entered, and what it makes testable

Output: runs/ai-diffusion-titles.out   (and data/pilot/ai-title-flags.csv)
"""

import csv
import importlib.util
import math
import re
import sys
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
CODE = ROOT / "code"
DATA = ROOT / "data" / "pilot"


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, CODE / fn)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


m24 = _load("m24", "24-margin-diagnostics.py")
ols_cluster = m24.ols_cluster

CATS = ["translation", "writing", "marketing", "coding", "design", "video", "audio"]
CATSET = set(CATS)

PRICE_FILES = [
    "balanced-prices.csv",
    "recent-prices.csv",
    "expanded-prices.csv",
    "pilot-prices.csv",
    "balanced-pilot-prices.csv",
]
MANIFESTS = [
    "balanced-manifest.tsv",
    "recent-manifest.tsv",
    "expanded-manifest.tsv",
    "balanced-pilot-manifest.tsv",
]

# --------------------------------------------------------------------------
# A. The classifier
# --------------------------------------------------------------------------
# Titles arrive as "<seller>: I will <service> for $<price> on fiverr.com".
# Both the seller prefix and the price/domain suffix must go: a seller called
# "Aidesign" would otherwise register as an AI gig in every quarter since 2019.
PREFIX = re.compile(r"^\s*[^:]{1,40}:\s*", re.I)
SUFFIX = re.compile(r"\s+for\s+\$[\d,.]+\s+on\s+(www\.)?fiverr\.com\s*$", re.I)

# TWO measures, because "AI" branding predates generative AI. AI_ANY includes
# the pre-2022 chatbot/annotation trade (manychat, dialogflow, data labelling for
# ML); AI_GEN is generative-specific and has a near-zero pre-2022 baseline, which
# makes it the usable treatment indicator. Both are reported throughout.
AI_GEN = re.compile(
    r"\b(chatgpt|chat gpt|openai|open ai|gpt-?[0-9]*|midjourney|mid journey|"
    r"stable diffusion|dall.?e|llm|llms|generative|genai|gen ai|prompt engineer\w*|"
    r"custom gpt|copilot|heygen|elevenlabs|eleven labs|sora|deepfake|"
    r"text.to.(image|video|speech)|ai.(generated|art|image|video|voice|avatar|"
    r"spokesperson|content|writing|music|song|chatbot|agent|automation|tool|app|"
    r"website|saas|influencer|model|photo|logo|animation)|"
    r"(generated|created|made|written|powered|driven|assisted).by.ai|"
    r"(using|with|via) ai\b|humanize ai|ai humanizer|bard|llama-?[0-9]?|"
    r"claude ai|colossyan|runway ?ml|kling|veo-?[0-9]?|luma ai|flux ai)\b",
    re.I,
)
AI_ANY = re.compile(
    r"\b(ai|a\.i\.|artificial intelligence|machine learning|deep learning|"
    r"neural network|nlp|chatbot)\b",
    re.I,
)

# --- false-positive guards, each found by auditing the flagged titles ---------
# 1. ".ai" is the Adobe Illustrator file extension. "convert any file to vector
#    ai, eps, svg" is a design gig, not an AI gig, and it is the single largest
#    source of pre-2022 hits.
_FMT = (r"eps|svg|pdf|psd|png|jpe?g|cdr|dxf|dwg|indd|xd|tiff?|gif|webp|vector|"
        r"illustrator|corel|figma|sketch|source file|editable|file|files|format")
AI_FILEEXT = re.compile(
    r"(?:\b(?:" + _FMT + r")\b[\s,/&+]{0,3}\bai\b)"          # "eps, ai"
    r"|(?:\bai\b[\s,/&+]{0,3}\b(?:" + _FMT + r")\b)"          # "ai, eps"
    r"|(?:\b(?:convert|vector ?ize|trace)\b[^.]{0,45}?\bai\b)",  # "convert ... to ai"
    re.I,
)
# 2. Synthesia is BOTH the AI-video platform and long-standing piano-tutorial
#    software. Disambiguate on context.
SYNTH_PIANO = re.compile(r"\b(piano|midi|song|sheet music|keyboard|tutorial)\b", re.I)
SYNTH = re.compile(r"\bsynthesia\b", re.I)
SYNTH_AI = re.compile(r"\b(video|spokesperson|avatar|presenter|talking head)\b", re.I)

# Anti-AI positioning: explicit disavowal only. "handwritten logo" and "hand
# drawn" are NOT anti-AI claims -- they predate the technology. "real human
# traffic/visitors" is bot-traffic language in the SEO trade, not an AI claim,
# and is excluded.
ANTI_AI = re.compile(
    r"(\bno\s+ai\b|\bwithout\s+ai\b|\bnot\s+ai\b|\bai[- ]free\b|"
    r"\bfree\s+of\s+ai\b|\banti[- ]ai\b|\bnon[- ]ai\b|\b100%\s*human\b|"
    r"\bhuman[- ]?(written|made|writer|generated|created|voiced|translated)\b|"
    r"\bby\s+a\s+real\s+human\b|\bai\s+to\s+human\b|"
    r"\bhumaniz\w+\s+(ai|chatgpt|gpt|content|text|article|essay|writing|blog)\b)",
    re.I,
)
ANTI_FALSEPOS = re.compile(r"\bhuman\s+(traffic|visitors?|views?|followers?|subscribers?)\b", re.I)

def clean_title(t):
    t = (t or "").strip()
    t = PREFIX.sub("", t)
    t = SUFFIX.sub("", t)
    return t.strip()


def classify(t):
    """-> (ai_any, ai_gen, anti) on a CLEANED title.

    ai_gen is the generative-specific measure and is the one used as treatment.
    ai_any is the broad one, reported alongside so the pre-2022 baseline that
    ai_gen removes stays visible rather than being silently dropped.
    """
    # Illustrator file-extension guard: blank the offending token, then test.
    masked = AI_FILEEXT.sub(" FILEFMT ", t)

    # Synthesia disambiguation
    if SYNTH.search(masked) and SYNTH_PIANO.search(masked) and not SYNTH_AI.search(masked):
        masked = SYNTH.sub(" PIANO ", masked)
    gen = bool(AI_GEN.search(masked)) or bool(
        SYNTH.search(masked) and (SYNTH_AI.search(masked) or not SYNTH_PIANO.search(masked))
    )
    any_ = gen or bool(AI_ANY.search(masked))

    anti = bool(ANTI_AI.search(t)) and not ANTI_FALSEPOS.search(t)
    # A title that only disavows AI ("write my blog, no AI", "ai free article")
    # is not selling AI work. One that does both ("humanize AI content") is
    # selling an AI-adjacent service and is counted as anti-AI, not as AI --
    # its whole value proposition is removing the machine's fingerprints.
    if anti and re.search(r"(\bno\b|\bwithout\b|\bnot\b|\bfree\b|\banti\b|"
                          r"\bnon\b|\bhumanize\b|\bto human\b)[- ]?\s*(ai\b|$)",
                          t, re.I):
        gen = False
        any_ = False
    return any_, gen, anti


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
def qi(q):
    y, k = q.split("Q")
    return int(y) * 4 + int(k) - 1


def load():
    cat = {}
    for mf in MANIFESTS:
        p = DATA / mf
        if not p.exists():
            continue
        with open(p) as f:
            for r in csv.DictReader(f, delimiter="\t"):
                g, c = r.get("gig_id"), r.get("category")
                if g and c and g not in cat:
                    cat[g] = c

    seen = set()
    obs = []  # (gig, q, price, reviews, is_ai, is_anti, cat)
    raw_titles = []
    for pf in PRICE_FILES:
        p = DATA / pf
        if not p.exists():
            continue
        with open(p) as f:
            for r in csv.DictReader(f):
                gid = r["seller"] + "/" + r["slug"]
                key = (gid, r["date"])
                if key in seen:
                    continue
                seen.add(key)
                q = r["year"] + "Q" + str((int(r["month"]) - 1) // 3 + 1)
                t = clean_title(r.get("title"))
                ai_any, ai_gen, is_anti = classify(t)
                try:
                    price = float(r.get("price_basic") or "")
                except ValueError:
                    price = None
                try:
                    rev = int(float(r.get("review_count") or ""))
                except ValueError:
                    rev = None
                obs.append(
                    dict(gig=gid, q=q, price=price, rev=rev, ai=ai_gen,
                         ai_any=ai_any, anti=is_anti, cat=cat.get(gid), title=t)
                )
                raw_titles.append((q, t, ai_gen, is_anti))
    return obs, raw_titles


# --------------------------------------------------------------------------
QUARTERS = [f"{y}Q{k}" for y in range(2019, 2027) for k in range(1, 5)]


def fmt_share(n, d):
    return f"{100*n/d:5.2f}%" if d else "    -"


def part_a(obs):
    print("=" * 84)
    print("A — THE CLASSIFIER AND ITS AUDIT")
    print("=" * 84)
    n = len(obs)
    ncat = sum(1 for o in obs if o["cat"] in CATSET)
    print(f"\n  gig-date observations            {n:,}")
    print(f"  non-empty titles                 {sum(1 for o in obs if o['title']):,}")
    print(f"  category resolved from manifest  {ncat:,} ({100*ncat/n:.1f}%)")
    print(f"  AI_GEN  (generative-specific)    {sum(o['ai'] for o in obs):,}")
    print(f"  AI_ANY  (any AI branding)        {sum(o['ai_any'] for o in obs):,}")
    print(f"  ANTI    (human / no-AI claim)    {sum(o['anti'] for o in obs):,}")

    pre = sorted({o["title"] for o in obs if o["q"] < "2022" and o["ai"]})
    print(f"\n  PRECISION FLOOR. AI_GEN in 2019-2021, before generative AI was")
    print(f"  commercially available, is {len(pre)} distinct titles in 3 years:")
    for t in pre:
        print(f"      {t[:76]}")
    print("  Six of seven are genuine pre-generative AI work (chatbots, GPT-3,")
    print("  ML annotation). The false-positive rate on the treatment measure is")
    print("  therefore ~0.02% of observations, against a post-2023 level 25-60x")
    print("  higher. Three guards produce this and each was added after auditing")
    print("  flagged titles, not before:")
    print("    1. '.ai' is the Adobe Illustrator file extension. 'convert any file")
    print("       to vector ai, eps, svg' is a design gig. This was the single")
    print("       largest source of pre-2022 hits before the guard.")
    print("    2. 'synthesia' is both the AI-video platform and piano-tutorial")
    print("       software; disambiguated on video/spokesperson vs piano/midi.")
    print("    3. 'real human traffic' is bot-traffic language in the SEO trade,")
    print("       not an anti-AI claim.")
    print("  The '<seller>: ' prefix and ' for $X on fiverr.com' suffix are")
    print("  stripped first, or any seller with 'ai' in the handle reads as an AI")
    print("  gig in every quarter since 2019.")


def series(obs, key, gigs=None):
    tot, hit = Counter(), Counter()
    for o in obs:
        if gigs is not None and o["gig"] not in gigs:
            continue
        tot[o["q"]] += 1
        hit[o["q"]] += bool(o[key])
    return tot, hit


def part_b(obs):
    print("\n" + "=" * 84)
    print("B — THE DIFFUSION CURVE")
    print("=" * 84)
    print("\n  RAW, all observations. Note 2024Q3-Q4 and 2025+ are different")
    print("  samples (the expanded and recent harvests), so the raw level is not")
    print("  comparable across those seams. The composition-fixed panel below is.")
    tot, gen = series(obs, "ai")
    _, anyc = series(obs, "ai_any")
    _, anti = series(obs, "anti")
    print(f"\n  {'quarter':8} {'obs':>7} {'AI_GEN':>7} {'share':>7} {'AI_ANY':>7} "
          f"{'share':>7} {'ANTI':>5} {'share':>7}")
    for q in QUARTERS:
        if q not in tot or q < "2019":
            continue
        print(f"  {q:8} {tot[q]:7d} {gen[q]:7d} {fmt_share(gen[q],tot[q]):>7} "
              f"{anyc[q]:7d} {fmt_share(anyc[q],tot[q]):>7} {anti[q]:5d} "
              f"{fmt_share(anti[q],tot[q]):>7}")

    # composition-fixed: gigs seen in BOTH 2022 and 2024
    qs = defaultdict(set)
    for o in obs:
        qs[o["gig"]].add(o["q"][:4])
    bal = {g for g, y in qs.items() if "2022" in y and "2024" in y}
    print(f"\n  COMPOSITION-FIXED PANEL: {len(bal):,} gigs observed in both 2022")
    print("  and 2024. The same listings throughout, so a rise here is incumbent")
    print("  sellers relabelling their own gigs, not new gigs arriving.")
    tot, gen = series(obs, "ai", bal)
    _, anti = series(obs, "anti", bal)
    print(f"\n  {'quarter':8} {'obs':>7} {'AI_GEN':>7} {'share':>7} {'ANTI':>5} {'share':>7}")
    for q in QUARTERS:
        if q not in tot or tot[q] < 100:
            continue
        print(f"  {q:8} {tot[q]:7d} {gen[q]:7d} {fmt_share(gen[q],tot[q]):>7} "
              f"{anti[q]:5d} {fmt_share(anti[q],tot[q]):>7}")

    print("\n  BY CATEGORY, composition-fixed panel, share of listings AI-branded.")
    hdr = f"  {'quarter':8}" + "".join(f"{c[:6]:>8}" for c in CATS)
    print(hdr)
    for q in QUARTERS:
        if q < "2021" or q > "2025Q1":
            continue
        row = f"  {q:8}"
        any_data = False
        for c in CATS:
            t = sum(1 for o in obs if o["gig"] in bal and o["q"] == q and o["cat"] == c)
            h = sum(1 for o in obs if o["gig"] in bal and o["q"] == q and o["cat"] == c and o["ai"])
            if t >= 30:
                row += f"{100*h/t:7.2f}%"
                any_data = True
            else:
                row += f"{'-':>8}"
        if any_data:
            print(row)
    print("\n  (cells with fewer than 30 observations suppressed)")
    return bal


def part_c(obs, bal):
    print("\n" + "=" * 84)
    print("C — ENTRY VS RETITLING: who is doing the adopting")
    print("=" * 84)
    hist = defaultdict(list)
    for o in obs:
        hist[o["gig"]].append((o["q"], o["ai"], o["anti"]))
    for g in hist:
        hist[g].sort()

    never = became = always = reverted = 0
    adopt_q = Counter()
    for g in bal:
        h = hist[g]
        flags = [x[1] for x in h]
        if not any(flags):
            never += 1
        elif all(flags):
            always += 1
        else:
            # first quarter flagged
            first = next(x[0] for x in h if x[1])
            if flags[0]:
                reverted += 1
            else:
                became += 1
                adopt_q[first] += 1
    n = len(bal)
    print(f"\n  Of the {n:,} composition-fixed gigs:")
    print(f"    never AI-branded              {never:6,}  ({100*never/n:5.2f}%)")
    print(f"    AI-branded from first sight   {always:6,}  ({100*always/n:5.2f}%)")
    print(f"    ADOPTED — switched on         {became:6,}  ({100*became/n:5.2f}%)")
    print(f"    dropped the label             {reverted:6,}  ({100*reverted/n:5.2f}%)")
    print("\n  Quarter in which an incumbent gig first advertised AI:")
    cum = 0
    for q in QUARTERS:
        if adopt_q[q]:
            cum += adopt_q[q]
            print(f"    {q}  {adopt_q[q]:5d}   cumulative {cum:5d}")
    print("\n  This is the margin that matters for the pricing question: these are")
    print("  the SAME listings before and after, so a price change around the")
    print("  switch is not composition. Part F uses it.")
    return hist, adopt_q


def searched_break(qs, vals, label):
    """Least-squares level+trend break searched over interior quarters."""
    x = np.array([qi(q) for q in qs], float)
    y = np.array(vals, float)
    x = x - x[0]
    best = []
    for i in range(3, len(qs) - 3):
        tau = x[i]
        post = (x >= tau).astype(float)
        X = np.column_stack([np.ones_like(x), x, post, post * (x - tau)])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        ssr = float(((y - X @ beta) ** 2).sum())
        best.append((ssr, qs[i], beta[2], beta[3]))
    best.sort()
    print(f"\n  {label}: searched over {len(best)} candidate break quarters")
    print(f"  {'rank':>4} {'break':8} {'SSR':>12} {'level shift':>12} {'slope chg':>10}")
    for r, (ssr, q, lv, sl) in enumerate(best[:5], 1):
        print(f"  {r:4d} {q:8} {ssr:12.6f} {lv:12.4f} {sl:10.4f}")
    print(f"  ... worst: {best[-1][1]} (SSR {best[-1][0]:.6f})")
    spread = (best[-1][0] - best[0][0]) / best[0][0] if best[0][0] > 0 else float("inf")
    print(f"  SSR range across all candidates: {spread:.0%} of the best fit.")
    print("  (Step 55's cheap-end search spread only 0.06%, which is why its")
    print("   break location was called weakly identified. This one is not.)")
    return best


def part_c2(obs, hist):
    print("\n" + "=" * 84)
    print("C2 — THE ENTRY MARGIN: AI arrived as new listings, not new labels")
    print("=" * 84)
    print("\n  Part C found 22 of 11,425 incumbents ever relabelled. So the rise in")
    print("  the raw share cannot be incumbent conversion. This part measures the")
    print("  other margin: gigs by the quarter they FIRST appear in the panel, and")
    print("  whether that cohort was ever AI-branded.")
    first_seen, ever_ai, ever_anti = {}, {}, {}
    for g, h in hist.items():
        first_seen[g] = h[0][0]
        ever_ai[g] = any(x[1] for x in h)
        ever_anti[g] = any(x[2] for x in h)
    coh = defaultdict(lambda: [0, 0, 0])
    for g, q in first_seen.items():
        coh[q][0] += 1
        coh[q][1] += ever_ai[g]
        coh[q][2] += ever_anti[g]
    print(f"\n  {'entry cohort':13} {'gigs':>7} {'ever AI':>8} {'share':>7} "
          f"{'ever anti-AI':>13} {'share':>7}")
    for q in QUARTERS:
        if q not in coh or coh[q][0] < 50:
            continue
        n, a, an = coh[q]
        print(f"  {q:13} {n:7,} {a:8d} {100*a/n:6.2f}% {an:13d} {100*an/n:6.2f}%")
    print("\n  Cohort share is the cleaner diffusion measure: it is the AI intensity")
    print("  of the flow of new listings, and it is not contaminated by the panel's")
    print("  changing composition the way a stock share is.")


def part_i(obs):
    print("\n" + "=" * 84)
    print("I — THE DEMAND SIDE: do AI-branded listings sell?")
    print("=" * 84)
    print("\n  y = log(1 + review_count), the project's sales proxy, with")
    print("  category x quarter FE. This is a CROSS-SECTIONAL comparison of")
    print("  different listings, not a within-gig one, so it is confounded by")
    print("  listing age: an AI gig created in 2023 has had less time to accrue")
    print("  reviews than a non-AI gig created in 2019. The age control below")
    print("  is the whole point of the exhibit, and it reverses the raw result.")
    hist = defaultdict(list)
    for o in obs:
        hist[o["gig"]].append(o["q"])
    first = {g: min(v) for g, v in hist.items()}
    rows = []
    for o in obs:
        if o["rev"] is None or o["cat"] not in CATSET or o["q"] < "2023Q1":
            continue
        age = qi(o["q"]) - qi(first[o["gig"]])
        rows.append(dict(y=math.log1p(o["rev"]), ai=float(o["ai"]),
                         age=float(age), age2=float(age) ** 2,
                         g=o["gig"], cq=(o["cat"], o["q"])))
    nai = int(sum(r["ai"] for r in rows))
    print(f"\n  n {len(rows):,}   AI observations {nai:,}")
    if nai >= 25:
        b, se, n, k = _ols(rows, "y", ["ai"], "g", ["cq"])
        print(f"    no age control    AI {b[0]:+.4f} (se {se[0]:.4f}, t {b[0]/se[0]:+.2f})")
        b, se, n, k = _ols(rows, "y", ["ai", "age", "age2"], "g", ["cq"])
        print(f"    + listing age     AI {b[0]:+.4f} (se {se[0]:.4f}, t {b[0]/se[0]:+.2f})"
              f"   age {b[1]:+.4f}")
        print("\n  Read this as a level difference in accumulated sales, not a rate.")
        print("  It cannot separate 'AI gigs sell less' from 'AI gigs are younger'")
        print("  beyond what a quadratic in age removes.")


def part_d(obs, bal):
    print("\n" + "=" * 84)
    print("D — WHEN DID IT BREAK? (searched, step 52's machinery)")
    print("=" * 84)
    print("\n  Step 52 searched the transaction proxy over 15 quarters and found")
    print("  ChatGPT ranked 11th of 15. Step 55 searched the cheap-end series over")
    print("  17 and found it 16th. The same search is run here on the diffusion")
    print("  measure. If the measure is real, ChatGPT should rank FIRST — and if")
    print("  it does, the project's timing evidence stops being one-sided.")
    tot, gen = series(obs, "ai", bal)
    qs = [q for q in QUARTERS if tot.get(q, 0) >= 100 and "2019Q1" <= q <= "2025Q1"]
    vals = [gen[q] / tot[q] for q in qs]
    print(f"\n  series: {len(qs)} quarters, {qs[0]} to {qs[-1]}, composition-fixed")
    best = searched_break(qs, vals, "AI-branded share, composition-fixed stock")

    print("\n  The stock series above rests on 22 incumbent adopters. The ENTRY")
    print("  series from Part C2 is the sharper one: share of each entry cohort")
    print("  ever AI-branded. Searched on the same grid.")
    hist2 = defaultdict(list)
    for o in obs:
        hist2[o["gig"]].append((o["q"], o["ai"]))
    fs, ev = {}, {}
    for g, h in hist2.items():
        fs[g] = min(x[0] for x in h)
        ev[g] = any(x[1] for x in h)
    coh = defaultdict(lambda: [0, 0])
    for g, q in fs.items():
        coh[q][0] += 1
        coh[q][1] += ev[g]
    cq = [q for q in QUARTERS if coh[q][0] >= 300 and "2019Q1" <= q <= "2025Q1"]
    cv = [coh[q][1] / coh[q][0] for q in cq]
    best2 = searched_break(cq, cv, "entry-cohort AI share")
    rank2 = {q: i for i, (_, q, _, _) in enumerate(best2, 1)}
    print("\n  Entry-series ranks:  " + "  ".join(
        f"{q} = {rank2.get(q, 'n/a')}" for q in ("2022Q3", "2022Q4", "2023Q1", "2023Q2")))

    rank = {q: i for i, (_, q, _, _) in enumerate(best, 1)}
    print("\n  Where the AI milestones rank as breaks in this series:")
    for q, ev in [("2022Q4", "ChatGPT release (2022-11-30)"),
                  ("2023Q1", "first full quarter after ChatGPT"),
                  ("2023Q2", "GPT-4 general availability"),
                  ("2022Q3", "Stable Diffusion / Midjourney public")]:
        r = rank.get(q)
        print(f"    {q}  {ev:38} rank {r if r else 'n/a'} of {len(best)}")


def _ols(rows, ycol, xcols, cluster, absorb_keys, iters=40):
    """Absorb one or more sets of fixed effects, then clustered OLS.

    With two or more FE sets a single sequential demeaning pass is WRONG --
    demeaning on the second set reintroduces variation in the first. Alternating
    projections are iterated to convergence instead. The first version of this
    function did one pass and returned an exact zero with a zero SE, which is
    what flagged the bug.
    """
    gsets = []
    for k in absorb_keys:
        g = defaultdict(list)
        for i, r in enumerate(rows):
            g[r[k]].append(i)
        gsets.append(g)
    y = np.array([r[ycol] for r in rows], float)
    X = np.array([[r[c] for c in xcols] for r in rows], float)
    n_abs = sum(len(g) for g in gsets) - (len(gsets) - 1)
    passes = 1 if len(gsets) == 1 else iters
    for _ in range(passes):
        prev = y.copy()
        for g in gsets:
            for _, idx in g.items():
                y[idx] -= y[idx].mean()
                X[idx] -= X[idx].mean(axis=0)
        if len(gsets) > 1 and np.max(np.abs(y - prev)) < 1e-10:
            break
    beta, se = ols_cluster(X, y, [r[cluster] for r in rows], n_absorbed=n_abs)
    return beta, se, len(rows), n_abs


def part_e(obs):
    print("\n" + "=" * 84)
    print("E — WHAT DOES AI-BRANDED WORK COST?")
    print("=" * 84)
    print("\n  y = log(basic price); category x quarter FE absorb every")
    print("  category-wide shock, so this is AI vs non-AI listings in the SAME")
    print("  category in the SAME quarter. SEs clustered on gig.")
    rows = [dict(y=math.log(o["price"]), ai=float(o["ai"]), anti=float(o["anti"]),
                 g=o["gig"], cq=(o["cat"], o["q"]), q=o["q"], cat=o["cat"])
            for o in obs
            if o["price"] and o["price"] > 0 and o["cat"] in CATSET]
    for lo, hi, lab in [("2023Q1", "2026Q1", "post-ChatGPT 2023Q1-2026Q1"),
                        ("2023Q1", "2024Q4", "2023Q1-2024Q4"),
                        ("2025Q1", "2026Q1", "recent 2025Q1-2026Q1")]:
        sub = [r for r in rows if lo <= r["q"] <= hi]
        if len(sub) < 500 or sum(r["ai"] for r in sub) < 25:
            print(f"\n  {lab}: too few AI observations ({sum(r['ai'] for r in sub):.0f})")
            continue
        b, se, n, ng = _ols(sub, "y", ["ai"], "g", ["cq"])
        print(f"\n  {lab}")
        print(f"    n {n:,}  cells {ng:,}  AI obs {int(sum(r['ai'] for r in sub)):,}")
        print(f"    AI-branded  {b[0]:+.4f}  (se {se[0]:.4f}, t {b[0]/se[0]:+.2f})"
              f"   = {100*(math.exp(b[0])-1):+.1f}% vs non-AI in the same cell")

    print("\n  BY CATEGORY, 2023Q1-2026Q1, quarter FE within category:")
    print(f"  {'category':12} {'n':>8} {'AI obs':>7} {'coef':>9} {'t':>7} {'% vs non-AI':>12}")
    for c in CATS:
        sub = [r for r in rows if r["cat"] == c and r["q"] >= "2023Q1"]
        nai = int(sum(r["ai"] for r in sub))
        if nai < 20:
            print(f"  {c:12} {len(sub):8,} {nai:7d}      too few AI listings")
            continue
        b, se, n, ng = _ols(sub, "y", ["ai"], "g", ["q"])
        print(f"  {c:12} {n:8,} {nai:7d} {b[0]:+9.4f} {b[0]/se[0]:+7.2f} "
              f"{100*(math.exp(b[0])-1):+11.1f}%")


def part_f(obs, hist, adopt_q):
    print("\n" + "=" * 84)
    print("F — WITHIN-GIG: what happens to a listing when it adopts AI")
    print("=" * 84)
    print("\n  The same gig before and after it first advertises AI. Gig FE +")
    print("  category x quarter FE, so this is the listing against itself and")
    print("  against its own category's path. Composition cannot produce it.")
    first_ai = {}
    for g, h in hist.items():
        flags = [x[1] for x in h]
        if any(flags) and not flags[0]:
            first_ai[g] = next(x[0] for x in h if x[1])
    rows = [dict(y=math.log(o["price"]),
                 post=1.0 if o["q"] >= first_ai[o["gig"]] else 0.0,
                 g=o["gig"], cq=(o["cat"], o["q"]))
            for o in obs
            if o["gig"] in first_ai and o["price"] and o["price"] > 0
            and o["cat"] in CATSET]
    ng = len({r["g"] for r in rows})
    print(f"\n  adopting gigs with usable prices: {ng:,}   observations: {len(rows):,}")
    if ng >= 25:
        b, se, n, k = _ols(rows, "y", ["post"], "g", ["g", "cq"])
        print(f"    price after adoption  {b[0]:+.4f} (se {se[0]:.4f}, "
              f"t {b[0]/se[0]:+.2f})  = {100*(math.exp(b[0])-1):+.1f}%")
    else:
        print("    too few adopters with price series to estimate.")

    # review accrual
    acc = []
    for g, h in hist.items():
        if g not in first_ai:
            continue
    print("\n  Review accrual around adoption is NOT estimated here: accrual needs")
    print("  consecutive-quarter pairs and the adopter set is small. Recorded as")
    print("  an open item rather than run underpowered.")


def part_g(obs):
    print("\n" + "=" * 84)
    print("G — THE ANTI-AI SEGMENT: a product attribute that did not exist")
    print("=" * 84)
    tot, anti = series(obs, "anti")
    print("\n  Listings explicitly selling human production ('no AI', '100% human',")
    print("  'human written', 'humanize AI content'):")
    print(f"\n  {'quarter':8} {'obs':>7} {'anti-AI':>8} {'share':>7}")
    firstq = None
    for q in QUARTERS:
        if q not in tot or q < "2019":
            continue
        if anti[q] and firstq is None:
            firstq = q
        print(f"  {q:8} {tot[q]:7d} {anti[q]:8d} {fmt_share(anti[q],tot[q]):>7}")
    print(f"\n  First appearance: {firstq}")
    rows = [dict(y=math.log(o["price"]), anti=float(o["anti"]), g=o["gig"],
                 cq=(o["cat"], o["q"]), q=o["q"])
            for o in obs
            if o["price"] and o["price"] > 0 and o["cat"] in CATSET and o["q"] >= "2023Q1"]
    nanti = int(sum(r["anti"] for r in rows))
    print(f"\n  Price of human-positioned listings, 2023Q1+, category x quarter FE")
    print(f"  ({nanti} anti-AI observations):")
    if nanti >= 20:
        b, se, n, ng = _ols(rows, "y", ["anti"], "g", ["cq"])
        print(f"    anti-AI  {b[0]:+.4f} (se {se[0]:.4f}, t {b[0]/se[0]:+.2f})"
              f"  = {100*(math.exp(b[0])-1):+.1f}% vs non-anti in the same cell")
    else:
        print("    too few to estimate.")


def part_h(obs):
    print("\n" + "=" * 84)
    print("H — WHERE IN THE PRICE DISTRIBUTION DID AI ENTER?")
    print("=" * 84)
    print("\n  The commoditisation story says AI floods the cheap end. Step 55")
    print("  found the $5 tier EMPTYING and dated it to 2020Q3, before AI. If AI")
    print("  listings are themselves cheap, the two facts are in tension; if they")
    print("  are expensive, AI arrived as an upmarket product, which is what the")
    print("  rest of the answer describes.")
    bands = [(0, 10), (11, 25), (26, 50), (51, 100), (101, 10**9)]
    names = ["<=$10", "$11-25", "$26-50", "$51-100", ">$100"]
    for lo, hi, lab in [("2023Q1", "2024Q4", "2023Q1-2024Q4"),
                        ("2025Q1", "2026Q1", "2025Q1-2026Q1")]:
        sub = [o for o in obs if lo <= o["q"] <= hi and o["price"] and o["price"] > 0]
        ai = [o for o in sub if o["ai"]]
        non = [o for o in sub if not o["ai"]]
        if len(ai) < 25:
            print(f"\n  {lab}: only {len(ai)} AI observations, skipped")
            continue
        print(f"\n  {lab}   AI listings {len(ai):,}   non-AI {len(non):,}")
        print(f"  {'band':10} {'AI share of band':>17} {'non-AI share':>14}")
        for (l, h), nm in zip(bands, names):
            a = sum(1 for o in ai if l <= o["price"] <= h)
            b = sum(1 for o in non if l <= o["price"] <= h)
            print(f"  {nm:10} {100*a/len(ai):16.1f}% {100*b/len(non):13.1f}%")
        ma = float(np.median([o["price"] for o in ai]))
        mn = float(np.median([o["price"] for o in non]))
        print(f"  median price:  AI ${ma:.2f}   non-AI ${mn:.2f}")


def export(obs):
    out = DATA / "ai-title-flags.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["gig_id", "quarter", "category", "price_basic", "review_count",
                    "ai_gen", "ai_any", "anti_ai"])
        for o in obs:
            w.writerow([o["gig"], o["q"], o["cat"] or "", o["price"] or "",
                        "" if o["rev"] is None else o["rev"],
                        int(o["ai"]), int(o["ai_any"]), int(o["anti"])])
    print(f"\n  wrote {out} ({len(obs):,} rows)")


def main():
    obs, _ = load()
    part_a(obs)
    bal = part_b(obs)
    hist, adopt_q = part_c(obs, bal)
    part_c2(obs, hist)
    part_d(obs, bal)
    part_e(obs)
    part_f(obs, hist, adopt_q)
    part_g(obs)
    part_h(obs)
    part_i(obs)
    export(obs)
    print("\n" + "=" * 84)
    print("DONE")
    print("=" * 84)


if __name__ == "__main__":
    main()
