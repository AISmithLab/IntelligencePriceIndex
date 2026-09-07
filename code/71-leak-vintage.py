#!/usr/bin/env python3
"""
Step 71: Are the gigs step 04 leaks NEWER than the ones it keeps?

Step 70 tested the leak for price bias on the 500-seller pilot and found a level gap
(design leaked +0.85 log, coding -0.51) but no trend gap and no AI-vocabulary gap.
The AI test there is uninformative: the pilot's own AI rate is 2/524 in design, so it
could not have detected a difference.

This runs the high-power version. Slug text and capture timestamps are in the CDX index
already, so the whole population is testable with no crawl -- 88,320 leaked gigs against
the kept populations rather than tens.

The concern, stated in plans/todo.md: step 04's keyword lists were written in 2023, and
AI-era listings use newer vocabulary, so the miss could correlate with the treatment.
Two observable implications:
  (a) leaked gigs carry AI vocabulary in the slug more often than kept gigs;
  (b) leaked gigs are of LATER vintage (first captured in a later quarter).
Either would make the leak non-random with respect to the treatment.

Input:  data/cdx-index/gig-pages-classified.tsv
Output: runs/uncollected-headroom/leak-vintage.md
"""

import importlib.util
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
OUTDIR = BASE_DIR / "runs" / "uncollected-headroom"

sys.path.insert(0, str(BASE_DIR / "code"))
from gigfilter import is_gig

DOMAINS = ["design", "coding", "writing", "marketing", "audio", "video", "translation"]


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, BASE_DIR / "code" / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


c68 = _load("68-uncategorized-families.py", "c68")

AI_RE = re.compile(
    r"(^|[-/])(ai|gpt|chatgpt|midjourney|dalle|dall-e|generative|llm|openai|"
    r"stable-diffusion|prompt-engineer|copilot|elevenlabs|synthesia|runway|firefly|"
    r"ai-generated|ai-art|ai-voice|ai-image|ai-video|ai-content|ai-chatbot)([-/]|$)")


def quarter(ts):
    return f"{ts[:4]}Q{(int(ts[4:6]) - 1) // 3 + 1}"


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # gig -> (bucket, domain); gig -> earliest timestamp
    bucket = {}
    first = {}
    scanned = 0
    with open(INPUT, encoding="utf-8", errors="replace") as f:
        next(f)
        for line in f:
            scanned += 1
            p = line.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            cat, ts = p[6], p[1]
            g = c68.gig_id(p[2])
            if not g:
                continue
            g = g.lower()
            if g not in bucket:
                if cat in DOMAINS:
                    bucket[g] = ("kept", cat)
                elif cat == "uncategorized":
                    if c68.first_match(g, c68.NEW_FAMILIES):
                        bucket[g] = ("other", None)
                    else:
                        lk = c68.first_match(g, c68.LEAKAGE_STEMS)
                        bucket[g] = ("leaked", lk) if lk in DOMAINS else ("other", None)
                else:
                    bucket[g] = ("other", None)
            if g not in first or ts < first[g]:
                first[g] = ts

    n = Counter()
    ai = Counter()
    vint = defaultdict(Counter)
    for g, (b, d) in bucket.items():
        if b == "other" or d not in DOMAINS:
            continue
        n[(d, b)] += 1
        slug = g.split("/", 1)[1] if "/" in g else g
        if AI_RE.search(slug):
            ai[(d, b)] += 1
        vint[(d, b)][quarter(first[g])] += 1

    def median_q(counter):
        items = sorted(counter.items())
        tot = sum(c for _, c in items)
        acc = 0
        for q, c in items:
            acc += c
            if acc >= tot / 2:
                return q
        return "n/a"

    def share_since(counter, cut):
        tot = sum(counter.values())
        return sum(c for q, c in counter.items() if q >= cut) / tot if tot else 0.0

    try:
        from scipy import stats
        have_scipy = True
    except ImportError:
        have_scipy = False

    L = []
    L.append("# Is step 04's leak correlated with listing vintage or AI vocabulary?\n")
    L.append(f"Full population from `data/cdx-index/gig-pages-classified.tsv` "
             f"({scanned:,} index rows). No crawl. `KEPT` = step 04 assigned the domain; "
             f"`LEAKED` = step 04 said `uncategorized` and step 68's broader stems say the "
             f"domain; gigs matching a genuinely new family are excluded.\n")
    L.append("Vintage = quarter of the gig's EARLIEST capture. `2023Q1+` is the share first "
             "seen in 2023Q1 or later — the window step 04's keyword lists predate.\n")

    L.append("## AI vocabulary in the slug\n")
    L.append("| domain | kept n | kept AI | leaked n | leaked AI | Fisher p |")
    L.append("|---|---:|---:|---:|---:|---:|")
    ai_flags = []
    for d in DOMAINS:
        nk, nl = n[(d, "kept")], n[(d, "leaked")]
        if not nk or not nl:
            L.append(f"| {d} | {nk} | — | {nl} | — | too thin |")
            continue
        ak, al = ai[(d, "kept")], ai[(d, "leaked")]
        p = (stats.fisher_exact([[ak, nk - ak], [al, nl - al]]).pvalue
             if have_scipy else float("nan"))
        star = "**" if p < 0.05 else ""
        if p < 0.05:
            ai_flags.append(d)
        L.append(f"| {d} | {nk:,} | {ak:,} ({100*ak/nk:.2f}%) | {nl:,} "
                 f"| {star}{al:,} ({100*al/nl:.2f}%){star} | {p:.2e} |")

    L.append("\n## Vintage\n")
    L.append("| domain | kept median 1st qtr | leaked median 1st qtr | kept 2023Q1+ | leaked 2023Q1+ | Fisher p |")
    L.append("|---|---|---|---:|---:|---:|")
    v_flags = []
    for d in DOMAINS:
        nk, nl = n[(d, "kept")], n[(d, "leaked")]
        if not nk or not nl:
            L.append(f"| {d} | — | — | — | — | too thin |")
            continue
        ck, cl = vint[(d, "kept")], vint[(d, "leaked")]
        sk, sl = share_since(ck, "2023Q1"), share_since(cl, "2023Q1")
        hk, hl = round(sk * nk), round(sl * nl)
        p = (stats.fisher_exact([[hk, nk - hk], [hl, nl - hl]]).pvalue
             if have_scipy else float("nan"))
        star = "**" if p < 0.05 else ""
        if p < 0.05:
            v_flags.append(d)
        L.append(f"| {d} | {median_q(ck)} | {median_q(cl)} | {100*sk:.1f}% "
                 f"| {star}{100*sl:.1f}%{star} | {p:.2e} |")

    L.append("\n## Verdict\n")
    L.append(f"- Domains where LEAKED slugs carry AI vocabulary at a different rate (p<0.05): "
             f"**{', '.join(ai_flags) if ai_flags else 'none'}**")
    L.append(f"- Domains where LEAKED gigs are of different vintage (p<0.05): "
             f"**{', '.join(v_flags) if v_flags else 'none'}**")
    L.append("")
    L.append("Read with step 70, which tested the same leak for price bias on the "
             "category-blind 500-seller pilot: level differs in design and coding, trend "
             "differs nowhere.")

    out = "\n".join(L) + "\n"
    (OUTDIR / "leak-vintage.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
