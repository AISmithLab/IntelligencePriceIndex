#!/usr/bin/env python3
"""
Step 16: Subdivide the broad CDX categories into NARROW subcategories.

The recent manifest (data/pilot/recent-manifest.tsv) labels each gig with one of 7
broad domains (design, coding, writing, marketing, video, audio, translation).
This step re-labels each gig with a finer subcategory by keyword-matching its slug
again *within* its broad parent, and writes a parallel manifest the site-data
builder can point step 14 at unchanged.

Coverage warning (measured in runs/, 2026-06-30 pilot): at MONTHLY cadence with the
>=3 matched-pair gate, only design subcategories (and coding/web-dev) chain a full
series; most other subcategories are thin and read near-flat. The user opted in to
the full subdivision anyway — thin subcats that can't chain even one transition are
dropped automatically by step 14's `len(idx) >= 2` gate.

Library use (imported by step 17):
    from <this module> import subclassify, write_narrow_manifest, category_meta
CLI:
    python3 code/16-subclassify-narrow.py        # writes the narrow manifest + prints dist
"""

import csv
import colorsys
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gigfilter import is_gig

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_MANIFEST = BASE_DIR / "data" / "pilot" / "recent-manifest.tsv"
DST_MANIFEST = BASE_DIR / "data" / "pilot" / "recent-manifest-narrow.tsv"
PRICES_FILE = BASE_DIR / "data" / "pilot" / "recent-prices.csv"

# matched-pair gate, mirroring step 14 — used to decide which subcats are "relevant"
REL_LO, REL_HI, MIN_REL, PRICE_MAX, WINDOW = 0.1, 10.0, 3, 10000.0, 13

# broad -> ordered list of (sub_id, display label, [slug keywords]).
# First keyword match within the broad parent wins; the remainder falls into
# "<broad>-other". Order also sets the colour shade (first = lightest).
NARROW = {
    "design": [
        ("logo_brand",      "Logo & Brand",      ["logo", "brand", "identity", "business-card", "letterhead", "stationery"]),
        ("illustration",    "Illustration",      ["illustrat", "cartoon", "caricature", "portrait", "character", "comic", "manga", "avatar", "drawing", "sketch"]),
        ("ui_ux_web",       "UI/UX & Web",       ["ui-", "ux-", "ui-ux", "web-design", "app-design", "figma", "landing", "website-design", "wireframe"]),
        ("print_merch",     "Print & Merch",     ["flyer", "poster", "brochure", "banner", "packaging", "label", "t-shirt", "merch", "print", "menu", "invitation", "card-design", "sticker"]),
        ("social_graphics", "Social Graphics",   ["thumbnail", "social-media", "instagram", "youtube-thumbnail", "cover", "banner-ad"]),
        ("threed_product",  "3D & Product",      ["3d-", "3d", "cad", "render", "product-design", "mockup", "architect", "interior"]),
    ],
    "coding": [
        ("web_dev",         "Web Dev",           ["web-develop", "website", "wordpress", "shopify", "wix", "squarespace", "html", "css", "react", "angular", "vue", "php", "laravel", "webflow", "webpage", "landing-page"]),
        ("backend_api",     "Backend & API",     ["api", "database", "sql", "backend", "node", "python", "java", "django", "devops", "server"]),
        ("automation_bot",  "Automation & Bots", ["bot", "automation", "scraping", "scrape", "discord-bot", "telegram", "zapier", "macro", "script"]),
        ("data_ml_ai",      "Data/ML & AI",      ["machine-learning", "deep-learning", "data-scien", "ai-", "chatbot", "tensorflow", "pytorch", "data-analy"]),
        ("mobile_app",      "Mobile App",        ["mobile-app", "app-develop", "flutter", "swift", "kotlin", "android", "ios", "react-native"]),
    ],
    "writing": [
        ("content_seo",     "Content & SEO",     ["article", "blog", "seo-writ", "content-writ", "website-content", "product-description"]),
        ("copywriting",     "Copywriting",       ["copywrit", "copywriter", "sales-copy", "ad-copy", "email-copy", "slogan", "tagline", "script-writ", "creative-writ"]),
        ("editing",         "Editing & Proofing",["proofread", "edit-your", "editing", "editor", "rewrite", "rewriting"]),
        ("ebook_book",      "eBook & Ghostwrite",["ebook", "e-book", "book-writ", "ghostwrit", "story", "novel"]),
        ("resume_bio",      "Resume & Bio",      ["resume", "cover-letter", "linkedin-profile", "bio-writ", "cv-"]),
    ],
    "marketing": [
        ("seo",             "SEO",               ["seo", "backlink", "keyword", "on-page", "off-page", "link-building"]),
        ("social_media",    "Social Media",      ["social-media", "instagram", "facebook", "tiktok", "pinterest", "twitter", "social"]),
        ("ads_ppc",         "Ads & PPC",         ["google-ads", "ppc", "facebook-ads", "ad-campaign", "ads", "adwords"]),
        ("email_funnel",    "Email & Funnels",   ["email-market", "funnel", "klaviyo", "mailchimp", "newsletter", "drip"]),
    ],
    "video": [
        ("video_editing",   "Video Editing",     ["video-edit", "edit-your-video", "premiere", "after-effects", "reels", "short-video", "youtube-video"]),
        ("animation",       "Animation",         ["animat", "2d-animat", "3d-animat", "whiteboard", "cartoon", "explainer", "lottie"]),
        ("motion_intro",    "Motion & Intros",   ["motion-graphic", "intro", "outro", "logo-animat", "lower-third"]),
    ],
    "audio": [
        ("voiceover",       "Voiceover",         ["voiceover", "voice-over", "voice-act", "narrat", "voice"]),
        ("music_prod",      "Music Production",   ["music", "song", "jingle", "beat", "instrumental", "mixing", "mastering", "compose", "producer"]),
        ("podcast",         "Podcast & Sound",   ["podcast", "audio-edit", "sound-design"]),
    ],
    "translation": [
        ("translation",     "Translation",        ["translat", "locali", "interpret"]),
        ("subtitle",        "Subtitles & Transcribe", ["subtitle", "caption", "transcri"]),
    ],
}

# Broad-family hues (deg) mirroring the original flat palette, so subcategories
# read as shades of their parent's colour.
BROAD_HUE = {"design": 224, "coding": 190, "writing": 265, "marketing": 330,
             "video": 24, "audio": 145, "translation": 45}


def slug_of(gid):
    return gid.split("/", 1)[1] if "/" in gid else gid


def subclassify(broad, slug):
    """broad domain + gig slug -> narrow category id '<broad>-<sub>'."""
    if broad not in NARROW:
        return broad
    s = slug.lower()
    for sub_id, _label, kws in NARROW[broad]:
        if any(kw in s for kw in kws):
            return f"{broad}-{sub_id}"
    return f"{broad}-other"


def measure_coverage(src=SRC_MANIFEST, prices=PRICES_FILE, window=WINDOW):
    """For every candidate narrow subcat, count how many of the trailing-`window`
    monthly transitions clear step 14's >=MIN_REL matched-pair gate. Returns
    {subcat_id: chainable_months}. This is the relevance signal: thin subcats that
    can't chain a real series get collapsed back into their broad parent."""
    gig_broad = {}
    with open(src) as f:
        for row in csv.DictReader(f, delimiter="\t"):
            gig_broad[row["gig_id"]] = row["category"]
    gig_sub = {g: subclassify(b, slug_of(g)) for g, b in gig_broad.items()}

    panel = defaultdict(lambda: defaultdict(list))
    with open(prices) as f:
        for row in csv.DictReader(f):
            if not is_gig(row["seller"]):      # /hire/, /agencies/ landing pages
                continue
            gid = f"{row['seller']}/{row['slug']}"
            if gid not in gig_sub:
                continue
            try:
                price = float(row.get("price_basic") or 0)
            except ValueError:
                continue
            if not (0 < price <= PRICE_MAX):
                continue
            try:
                mo = f"{int(row['year']):04d}-{int(row['month']):02d}"
            except (ValueError, TypeError):
                continue
            panel[gid][mo].append(price)
    panel = {g: {m: statistics.median(v) for m, v in d.items()} for g, d in panel.items()}

    months = sorted({m for d in panel.values() for m in d})[-window:]
    trans = list(zip(months, months[1:]))
    by_sub = defaultdict(list)
    for g in panel:
        by_sub[gig_sub[g]].append(g)

    cov = {}
    for sub, gigs in by_sub.items():
        rel = defaultdict(list)
        for g in gigs:
            ps = sorted(p for p in panel[g] if p in months)
            for a, b in zip(ps, ps[1:]):
                va, vb = panel[g][a], panel[g][b]
                if va > 0 and REL_LO <= vb / va <= REL_HI:
                    rel[(a, b)].append(vb / va)
        cov[sub] = sum(1 for t in trans if len(rel.get(t, [])) >= MIN_REL)
    return cov


def relevant_subcats(bar=7, src=SRC_MANIFEST, prices=PRICES_FILE):
    """Subcat ids whose coverage meets `bar` (default 7/12 — the floor of the
    current broad categories). The '<broad>-other' remainder buckets are never
    promoted to a standalone split; they collapse into the broad parent."""
    cov = measure_coverage(src, prices)
    keep = {s for s, c in cov.items() if c >= bar and not s.endswith("-other")}
    return keep, cov


def _hsl_hex(h_deg, s, l):
    r, g, b = colorsys.hls_to_rgb(h_deg / 360.0, l, s)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def category_meta():
    """Every category id that can appear -> {'label', 'parent', 'color'}.
    Subcats are lightness-stepped shades of their parent hue; the broad
    'remainder' bucket (id == the broad name) is a darker, muted shade of the
    same hue so each family reads together."""
    meta = {}
    for broad, subs in NARROW.items():
        hue = BROAD_HUE.get(broad, 0)
        ids = [(f"{broad}-{sid}", lbl) for sid, lbl, _ in subs]
        ids.append((f"{broad}-other", f"{broad.capitalize()} · other"))
        n = len(ids)
        for i, (cid, lbl) in enumerate(ids):
            light = 0.60 - (0.24 * (i / (n - 1) if n > 1 else 0))  # 0.60 -> 0.36
            meta[cid] = {"label": lbl, "parent": broad,
                         "color": _hsl_hex(hue, 0.66, light)}
        # broad remainder bucket (gigs not carved into a kept subcat)
        meta[broad] = {"label": broad.capitalize(), "parent": broad,
                       "color": _hsl_hex(hue, 0.45, 0.30)}
    return meta


def write_narrow_manifest(src=SRC_MANIFEST, dst=DST_MANIFEST, keep=None):
    """Copy the manifest, replacing the broad 'category' with the narrow id.
    If `keep` (a set of subcat ids) is given, only those subcats are split out;
    every other gig keeps its broad parent label so the parent stays well-covered."""
    counts = Counter()
    with open(src) as fin, open(dst, "w", newline="") as fout:
        r = csv.DictReader(fin, delimiter="\t")
        w = csv.DictWriter(fout, fieldnames=r.fieldnames, delimiter="\t")
        w.writeheader()
        for row in r:
            broad = row["category"]
            sub = subclassify(broad, slug_of(row["gig_id"]))
            row["category"] = sub if (keep is None or sub in keep) else broad
            w.writerow(row)
            counts[row["category"]] += 1
    return dst, counts


def main():
    dst, counts = write_narrow_manifest()
    by_parent = defaultdict(list)
    for cid, n in counts.items():
        by_parent[cid.split("-", 1)[0]].append((cid, n))
    print(f"Wrote {dst}\n")
    print(f"{'narrow category':28s} {'rows':>7s}")
    print("-" * 38)
    for parent in NARROW:
        for cid, n in sorted(by_parent.get(parent, []), key=lambda x: -x[1]):
            print(f"  {cid:26s} {n:7d}")


if __name__ == "__main__":
    main()
