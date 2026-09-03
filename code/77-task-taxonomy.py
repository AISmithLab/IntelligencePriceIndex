#!/usr/bin/env python3
"""
Step 77: a two-level task taxonomy, and a reference task value for every node.

WHY THIS EXISTS. Step 76 put task value in a GIG fixed effect. That is the
honest home for it when nothing observable measures the task -- but it is also a
dead end for the question actually being asked, because a fixed effect that
ABSORBS task value can never REPORT it. `a_i` came back with an SD of 1.249 log
points and no way to say what any part of it was.

This step moves task value out of the fixed effect and into an observable. The
unit is a taxonomy NODE: a `domain / subcategory` pair such as `coding /
wordpress` or `audio / voiceover`. A node's reference task value is the mean log
real price of the work in it. That is a number you can print, rank, and argue
with, which `a_i` was not.

THE TAXONOMY IS BUILT FROM TITLES, NOT SLUGS. `04-classify-categories.py`
matches keywords against the URL slug and assigns the seven domains this panel
carries. Titles are richer (99.99% coverage here) and regular: Fiverr renders
them as `<seller>: I will <deliverable> for $<n> on fiverr.com`, so stripping
the frame leaves the deliverable phrase. Subcategory rules match on that phrase.

RULES ARE ORDERED AND FIRST-MATCH-WINS, most specific first. `shopify dropshipping
store` must reach `ecommerce` before `web_dev` sees the word `store`. The order
is part of the definition, so it is written out in the report and must not be
sorted.

WHAT THIS DOES NOT FIX. The seven domains come from step 04 and inherit its
classifier leak (todo, 2026-09-01): `translation` contains 493 `voice over`
gigs, `writing` contains 151 `video editing` ones. The subcategory layer makes
the leak VISIBLE -- a `voiceover` node inside `translation` is a leak you can
count -- but it does not repair the domain assignment. Read node counts, not
just domain counts.

Input:  data/pilot/balanced-prices.csv (or .csv.gz)
        data/pilot/balanced-gig-category.csv.gz
        data/cpi-u.csv
Output: data/pilot/taxonomy-assignment.csv.gz  gig_id, domain, subcategory, node, phrase
        (gzipped: 5.9 MB -> 1.5 MB, and nothing reads it -- step 78 and the
        notebook both call `build()` rather than the file. Inspection artifact.)
        runs/taxonomy/taxonomy.md            coverage, node table, reference values
"""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "code"))
from gigfilter import is_gig


def _first_present(*paths):
    for q in paths:
        if q.exists():
            return q
    return paths[0]


PRICES = _first_present(BASE_DIR / "data" / "pilot" / "balanced-prices.csv",
                        BASE_DIR / "data" / "pilot" / "balanced-prices.csv.gz")
CATEGORY = BASE_DIR / "data" / "pilot" / "balanced-gig-category.csv.gz"
CPI = BASE_DIR / "data" / "cpi-u.csv"
OUTDIR = BASE_DIR / "runs" / "taxonomy"
ASSIGN = BASE_DIR / "data" / "pilot" / "taxonomy-assignment.csv.gz"

CPI_BASE = "2020Q1"
PRICE_MAX = 10000.0
RATING_MAX = 5.0
MIN_NODE = 30          # a node below this is folded into <domain>/other

# ---------------------------------------------------------------- title parsing
_TAIL = re.compile(r"\s+for\s+\$[\d,.]+\s+on\s+(?:www\.)?fiverr\.com\s*$", re.I)
_HEAD = re.compile(r"^\s*\S+\s*:\s*")
_IWILL = re.compile(r"^\s*i\s+will\s+", re.I)


def phrase_of(title):
    """`seller: I will <deliverable> for $N on fiverr.com` -> `<deliverable>`."""
    if not isinstance(title, str):
        return ""
    s = _TAIL.sub("", title)
    s = _HEAD.sub("", s)
    s = _IWILL.sub("", s)
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()


# ---------------------------------------------------------------- the taxonomy
# (subcategory, [patterns]) per domain, ORDERED -- first match wins.
TAXONOMY = {
    "audio": [
        ("voiceover",        ["voice over", "voiceover", "voice acting", "narrat",
                              "spokesperson", "audiobook", "text to speech"]),
        ("songwriting",      ["songwrit", "write a song", "lyric", "compose", "jingle",
                              "singer", "sing ", "vocalist", "topline"]),
        ("mixing_mastering", ["mix and master", "mixing", "mastering", "master your",
                              "mix your", "vocal tuning", "autotune"]),
        ("music_production", ["produce", "beat", "instrumental", "backing track",
                              "music for", "original music", "score"]),
        ("podcast",          ["podcast"]),
        ("sound_design",     ["sound design", "sound effect", "foley", "sfx"]),
        ("audio_editing",    ["audio edit", "edit your audio", "noise", "clean up",
                              "restore", "transcribe audio"]),
        ("music_promotion",  ["spotify", "playlist", "music promotion", "promote your music"]),
    ],
    "coding": [
        ("ecommerce",        ["shopify", "dropship", "woocommerce", "bigcommerce",
                              "etsy store", "ecommerce", "e commerce", "online store"]),
        ("wordpress",        ["wordpress", "elementor", "divi", "wp "]),
        ("site_builder",     ["wix", "squarespace", "webflow", "godaddy", "weebly"]),
        ("mobile_app",       ["mobile app", "android", "ios app", "flutter",
                              "react native", "app develop"]),
        ("scripting_automation", ["python", "script", "scraping", "scrape", "automat",
                              "bot", "api ", " api", "selenium"]),
        ("spreadsheet_data", ["excel", "google sheet", "spreadsheet", "data entry",
                              "vba", "macro", "database", "sql"]),
        ("bugfix_support",   ["fix ", "debug", "error", "troubleshoot", "bug"]),
        ("web_dev",          ["website", "web develop", "landing page", "html",
                              "css", "responsive", "redesign", "web design"]),
    ],
    "design": [
        ("logo",             ["logo"]),
        ("brand_identity",   ["brand", "identity", "business card", "stationery",
                              "letterhead", "style guide"]),
        ("ui_ux",            ["ui ", " ux", "ui ux", "figma", "mockup", "app design",
                              "website design", "wireframe", "landing page design"]),
        ("illustration",     ["illustrat", "draw", "cartoon", "caricature", "portrait",
                              "character", "comic", "manga", "anime", "sketch"]),
        ("print_collateral", ["flyer", "poster", "brochure", "banner", "menu",
                              "invitation", "label", "packaging", "book cover",
                              "album cover", "sticker"]),
        ("presentation",     ["powerpoint", "presentation", "pitch deck", "slide",
                              "keynote", "infographic"]),
        ("social_graphics",  ["thumbnail", "social media", "instagram post",
                              "youtube banner", "facebook cover"]),
        ("merch_apparel",    ["t shirt", "tshirt", "merch", "apparel", "hoodie"]),
        ("three_d",          ["3d", "render", "blender", "cad", "floor plan"]),
    ],
    "marketing": [
        ("seo",              ["seo", "backlink", "keyword", "rank your", "on page",
                              "off page", "link building", "guest post"]),
        ("paid_ads",         ["google ads", "facebook ads", "ppc", "adwords",
                              "ad campaign", "tiktok ads", "run ads", "advertis"]),
        ("social_media_mgmt", ["social media", "instagram", "facebook page", "tiktok",
                              "pinterest", "twitter", "community manager"]),
        ("email_marketing",  ["email marketing", "newsletter", "mailchimp", "klaviyo",
                              "email campaign", "cold email"]),
        ("affiliate",        ["affiliate", "clickbank", "cpa "]),
        ("funnel_landing",   ["funnel", "clickfunnel", "landing page", "lead magnet"]),
        ("youtube_growth",   ["youtube channel", "subscriber", "youtube views",
                              "youtube promotion", "monetiz"]),
        ("marketplace",      ["amazon", "ebay", "etsy", "walmart", "listing optimiz"]),
        ("analytics_setup",  ["analytics", "tag manager", "pixel", "conversion tracking",
                              "search console"]),
        ("content_strategy", ["content strategy", "marketing plan", "marketing strategy",
                              "brand strategy", "market research"]),
    ],
    "translation": [
        ("subtitling",       ["subtitle", "caption", "srt", "closed caption"]),
        ("transcription",    ["transcri"]),
        ("interpreting",     ["interpret"]),
        ("localization",     ["locali"]),
        ("proofreading_lang", ["proofread", "correct your", "grammar"]),
        ("language_tutoring", ["teach", "lesson", "tutor"]),
        ("voiceover_leak",   ["voice over", "voiceover", "record"]),
        ("document_translation", ["translat"]),
    ],
    "video": [
        ("music_video",      ["music video", "lyric video", "visualizer"]),
        ("explainer",        ["explainer", "whiteboard", "doodle"]),
        ("animation",        ["animat", "2d", "3d", "motion graphic", "cartoon"]),
        ("intro_outro",      ["intro", "outro", "logo reveal", "logo sting"]),
        ("spokesperson_ugc", ["spokesperson", "testimonial", "ugc", "on camera"]),
        ("promo_commercial", ["promo", "commercial", "trailer", "advertis",
                              "product video"]),
        ("slideshow",        ["slideshow", "photo video", "photo slideshow"]),
        ("video_editing",    ["edit", "editing"]),
        ("youtube_content",  ["youtube", "shorts", "tiktok video", "reel"]),
    ],
    "writing": [
        ("resume_career",    ["resume", "cv ", " cv", "cover letter", "linkedin"]),
        ("book_ebook",       ["ebook", "e book", "book", "ghostwrit", "novel",
                              "story", "children"]),
        ("press_pr",         ["press release", "public relation", " pr "]),
        ("script_writing",   ["script", "screenplay", "video script"]),
        ("academic",         ["research", "essay", "thesis", "dissertation",
                              "literature review", "report"]),
        ("copywriting",      ["copywrit", "copy for", "sales copy", "ad copy",
                              "product description", "slogan", "tagline", "sales page"]),
        ("editing_proofreading", ["proofread", "edit", "rewrite", "rephrase",
                              "paraphras"]),
        ("content_writing",  ["blog", "article", "content", "seo writ", "write",
                              "post", "website content"]),
    ],
}


def classify(domain, phrase):
    """-> subcategory. First matching rule in the domain's ORDERED list wins."""
    rules = TAXONOMY.get(domain)
    if not rules:
        return "other"
    p = f" {phrase} "
    for sub, pats in rules:
        for pat in pats:
            if pat in p:
                return sub
    return "other"


# ---------------------------------------------------------------- panel
def build(prices=None, category=None):
    """Gig-quarter panel with real price, reputation columns, and taxonomy node."""
    px = pd.read_csv(prices or PRICES)
    px = px[px.seller.map(is_gig)].copy()
    px["gig_id"] = px.seller + "/" + px.slug
    px = px.merge(pd.read_csv(category or CATEGORY), on="gig_id", how="inner")
    px = px[(px.price_basic > 0) & (px.price_basic <= PRICE_MAX)]
    px.loc[px.rating > RATING_MAX, "rating"] = np.nan
    px["quarter"] = [f"{int(y)}Q{(int(m) - 1) // 3 + 1}" for y, m in zip(px.year, px.month)]

    # taxonomy is a GIG attribute: assign from the gig's first non-empty title
    t = (px[["gig_id", "category", "title"]].dropna(subset=["title"])
           .drop_duplicates("gig_id").copy())
    t["phrase"] = t.title.map(phrase_of)
    t["subcategory"] = [classify(c, p) for c, p in zip(t.category, t.phrase)]
    t = t.rename(columns={"category": "domain"})

    # fold thin nodes into <domain>/other so no reference value rests on <30 gigs
    t["node"] = t.domain + "/" + t.subcategory
    small = t.node.value_counts()
    thin = set(small[small < MIN_NODE].index)
    t.loc[t.node.isin(thin), "subcategory"] = "other"
    t["node"] = t.domain + "/" + t.subcategory

    px = px.merge(t[["gig_id", "domain", "subcategory", "node", "phrase"]],
                  on="gig_id", how="inner")

    gq = (px.groupby(["gig_id", "domain", "subcategory", "node", "quarter"],
                     observed=True)
            .agg(price=("price_basic", "median"),
                 rating=("rating", "median"),
                 reviews=("review_count", "max"))
            .reset_index())
    gq["qi"] = [int(q[:4]) * 4 + int(q[5]) - 1 for q in gq.quarter]

    cpi = pd.read_csv(CPI)
    cpi["quarter"] = [f"{m[:4]}Q{(int(m[5:7]) - 1) // 3 + 1}" for m in cpi.month]
    cq = cpi.groupby("quarter").cpi_sa.mean()
    gq["cpi"] = gq.quarter.map(cq)
    gq = gq[gq.cpi.notna()]
    gq["real"] = gq.price * cq[CPI_BASE] / gq.cpi
    return gq.sort_values(["gig_id", "qi"]).reset_index(drop=True), t


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    gq_all, t = build()
    t[["gig_id", "domain", "subcategory", "node", "phrase"]].to_csv(ASSIGN, index=False)

    # Reference values are computed on the ESTIMATION sample -- the rows step 78 can
    # actually fit, i.e. those carrying both reputation columns. Reporting them on the
    # full panel instead would put a second, slightly different "reference task value"
    # into the project, and `marketing/content_strategy` alone moves $59.38 -> $67.11
    # between the two. One number, defined where it is used.
    gq = gq_all[gq_all.reviews.notna() & gq_all.rating.notna() & (gq_all.real > 0)].copy()
    dropped = len(gq_all) - len(gq)

    L = ["# A two-level task taxonomy, and a reference task value per node", ""]
    L += [f"Built from gig titles ({len(t):,} gigs, one title each). Domains are step 04's; "
          f"subcategories are this step's, matched on the deliverable phrase with "
          f"ORDERED first-match-wins rules. Nodes under {MIN_NODE} gigs are folded into "
          f"`<domain>/other`.", ""]
    L += [f"Panel: **{len(gq):,} gig-quarter observations**, **{gq.gig_id.nunique():,} gigs**, "
          f"**{gq.node.nunique()} nodes** across **{gq.domain.nunique()} domains**. "
          f"Prices are real, 2020Q1 dollars (CPI-U, SA quarterly mean).", "",
          f"Reference values below are computed on the **estimation sample** — the rows "
          f"`78-reputation-price.py` can fit, i.e. those carrying both a rating and a "
          f"review count. That drops {dropped:,} of {len(gq_all):,} gig-quarter rows "
          f"({dropped/len(gq_all):.1%}) and is deliberate: it keeps ONE reference task "
          f"value in the project rather than one here and a different one in the model.", ""]

    oth = t[t.subcategory == "other"]
    L += ["## Coverage", "",
          f"- gigs landing in a named subcategory: **{1 - len(oth)/len(t):.1%}** "
          f"({len(t)-len(oth):,} of {len(t):,})",
          f"- gigs in `<domain>/other`: **{len(oth):,}**", ""]
    L += ["| domain | gigs | nodes | in `other` | share named |", "|---|---:|---:|---:|---:|"]
    for d in sorted(t.domain.unique()):
        s = t[t.domain == d]
        no = (s.subcategory == "other").sum()
        L.append(f"| {d} | {len(s):,} | {s.subcategory.nunique()} | {no:,} | "
                 f"{1-no/len(s):.1%} |")

    L += ["", "## Reference task value by node", "",
          "**Reference task value** is the mean of `ln(real price)` over the node's "
          "gig-quarters, reported in dollars as `exp(mean ln p)` -- a geometric mean, "
          "which is the right centre for a log-normal price and is not dragged by the "
          "few $10,000 listings. `sd` is the within-node spread in log points: a large "
          "one means the node is still mixing different jobs.", ""]
    L += ["| node | gigs | obs | reference task value | mean ln p | sd ln p | median reviews |",
          "|---|---:|---:|---:|---:|---:|---:|"]
    ref = (gq.groupby("node")
             .agg(gigs=("gig_id", "nunique"), obs=("real", "size"),
                  mean_lnp=("real", lambda s: float(np.mean(np.log(s)))),
                  sd_lnp=("real", lambda s: float(np.std(np.log(s)))),
                  med_rev=("reviews", "median"))
             .sort_values("mean_lnp", ascending=False))
    for n, r in ref.iterrows():
        L.append(f"| {n} | {int(r.gigs):,} | {int(r.obs):,} | ${np.exp(r.mean_lnp):,.2f} | "
                 f"{r.mean_lnp:+.4f} | {r.sd_lnp:.4f} | {r.med_rev:,.0f} |")

    L += ["", f"Reference task value runs **${np.exp(ref.mean_lnp.min()):,.2f}** "
              f"({ref.mean_lnp.idxmin()}) to **${np.exp(ref.mean_lnp.max()):,.2f}** "
              f"({ref.mean_lnp.idxmax()}), a spread of "
              f"**{ref.mean_lnp.max()-ref.mean_lnp.min():.3f} log points**.", ""]

    L += ["## How much task variation the taxonomy actually captures", ""]
    lnp = np.log(gq.real.to_numpy(float))
    tot = float(np.var(lnp))
    for lbl, key in [("domain only (7 units)", "domain"), ("node (this taxonomy)", "node"),
                     ("gig (step 76's fixed effect)", "gig_id")]:
        grp = gq.groupby(key).real.transform(lambda s: np.mean(np.log(s)))
        L.append(f"- **{lbl}**: explains {1 - float(np.var(lnp - grp))/tot:.1%} of the "
                 f"variance in `ln(real price)`")
    L += ["", "The gap between the node row and the gig row is what a taxonomy cannot reach: "
              "differences between two listings of *the same kind of work*. Step 78 asks how "
              "much of that gap is reputation.", ""]

    (OUTDIR / "taxonomy.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:40]))
    print(f"\n... wrote {OUTDIR/'taxonomy.md'} and {ASSIGN}")


if __name__ == "__main__":
    main()
