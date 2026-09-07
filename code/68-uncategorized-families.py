#!/usr/bin/env python3
"""
Step 68: What is inside step 04's `uncategorized` bucket?

Step 67 measures that the skipped label holds more matched-pair headroom than any
collected category. This asks what it is made of, over DISTINCT gigs (not
snapshots, which over-weight long-lived listings).

Two passes over the slug text:

  1. Candidate NEW families the taxonomy names but step 04 never gave keywords —
     T9 customer service, T10 legal, T12 accounting — plus families the taxonomy
     never listed at all (photography, gaming, education, engineering/CAD,
     e-commerce ops, social engagement) and a deliberately AI-*un*exposed
     lifestyle family that would serve as a control group.
  2. LEAKAGE — of what neither step 04 nor pass 1 catches, how much is really a
     member of one of the seven collected domains under a broader stem. This is a
     property of the shipped index, not only of the headroom.

Input:  data/cdx-index/gig-pages-classified.tsv
Output: runs/uncollected-headroom/families.md
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gigfilter import is_gig

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
OUTDIR = BASE_DIR / "runs" / "uncollected-headroom"

NEW_FAMILIES = {
    "photography": ["photo", "retouch", "photoshoot", "lightroom", "headshot", "product-photo",
                    "background-remov", "remove-background", "color-grad", "image-edit",
                    "picture", "restore-old", "colorize"],
    "gaming": ["game", "gaming", "minecraft", "roblox", "unity", "unreal", "fortnite",
               "twitch-", "esports", "dnd", "dungeons", "rpg", "mod-", "gta", "fivem"],
    "education_tutoring": ["tutor", "teach", "lesson", "course", "curriculum", "homework",
                           "exam", "study-guide", "quiz", "flashcard", "thesis",
                           "dissertation", "essay", "citation", "bibliograph", "apa", "mla",
                           "academic"],
    "social_engagement": ["followers", "likes", "subscribers", "views", "backlink", "traffic",
                          "bookmark", "upvote", "retweet", "promote-your"],
    "legal": ["legal", "lawyer", "attorney", "contract", "nda", "trademark", "patent",
              "copyright", "compliance", "gdpr", "terms-and-conditions", "privacy-policy",
              "llc", "incorporat", "immigration", "paralegal", "litigation"],
    "ecommerce_ops": ["amazon", "ebay", "etsy", "dropship", "product-listing", "shopify-store",
                      "fba", "aliexpress", "walmart", "inventory", "order-fulfil",
                      "virtual-staging"],
    "lifestyle_control": ["psychic", "tarot", "astrolog", "horoscope", "numerolog", "reiki",
                          "healing", "spiritual", "manifest", "affirmation", "fitness",
                          "workout", "nutrition", "meal-plan", "diet", "yoga", "meditat",
                          "postcard", "prank", "relationship-advice", "life-coach", "dating"],
    "accounting_consulting": ["accounting", "accountant", "quickbooks", "xero", "payroll",
                              "tax-", "taxes", "bookkeep", "invoice", "financial-statement",
                              "balance-sheet", "business-plan", "pitch-consult", "valuation",
                              "due-diligence", "budget", "audit", "cfo", "profit-loss"],
    "engineering_cad": ["cad", "autocad", "solidworks", "revit", "blueprint", "floor-plan",
                        "structural", "mechanical-design", "electrical-design", "pcb",
                        "arduino", "matlab", "simulation", "takeoff", "estimation", "hvac",
                        "mep", "survey-engineer"],
    "customer_service_va": ["customer-service", "customer-support", "chat-support",
                            "email-support", "help-desk", "helpdesk", "live-chat",
                            "personal-assistant", "executive-assistant", "manage-your-inbox",
                            "appointment-setting", "cold-call", "telemarket", "receptionist"],
}

# broader stems for the seven domains the collections already cover; used only to
# size how much of the residual is step 04 missing its own categories
LEAKAGE_STEMS = {
    "design": ["draw", "sketch", "art", "paint", "vector", "mockup", "layout", "template",
               "visual", "creative-design", "render", "model-3d", "aesthetic"],
    "coding": ["develop", "websit", "web-", "softw", "script", "plugin", "theme", "drupal",
               "magento", "woocommerce", "ecommerce-site", "server", "hosting", "integrat",
               "migrat", "landing"],
    "writing": ["write", "writ", "content", "article", "report", "proposal", "summar",
                "transcri", "document", "letter", "note"],
    "marketing": ["promot", "advertis", "campaign", "brand-awareness", "outreach", "lead",
                  "sales", "audience", "reach", "viral", "classified-ad"],
    "audio": ["guitar", "piano", "vocal", "drum", "sing", "sound", "voice", "radio", "dj-"],
    "video": ["footage", "reel", "clip", "stream", "record-video", "montage"],
    "translation": ["proofread-in", "native-speaker"],
}


def gig_id(url):
    url = url.split("?")[0].split("#")[0]
    path = url.split("fiverr.com/", 1)[-1] if "fiverr.com/" in url else url
    parts = path.strip("/").split("/")
    if len(parts) < 2 or not parts[0] or not is_gig(parts[0]):
        return None
    return f"{parts[0]}/{parts[1]}"


def first_match(slug, table):
    for name, kws in table.items():
        if any(k in slug for k in kws):
            return name
    return None


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    gigs = set()
    with open(INPUT) as f:
        f.readline()
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 7 or p[6] != "uncategorized":
                continue
            g = gig_id(p[2])
            if g:
                gigs.add(g.lower())

    total = len(gigs)
    new_hits, leak_hits, residual = Counter(), Counter(), []
    for g in gigs:
        n = first_match(g, NEW_FAMILIES)
        if n:
            new_hits[n] += 1
            continue
        lk = first_match(g, LEAKAGE_STEMS)
        if lk:
            leak_hits[lk] += 1
        else:
            residual.append(g)

    new_tot, leak_tot = sum(new_hits.values()), sum(leak_hits.values())
    L = [f"# What is inside step 04's `uncategorized` bucket?", "",
         f"Distinct gig URLs labelled `uncategorized`: **{total:,}** "
         f"(`{INPUT.relative_to(BASE_DIR)}`, all years, `gigfilter.is_gig` applied).",
         "First-match assignment, so each gig counts once.", "",
         "## 1. Candidate new families", "",
         "| family | distinct gigs | share of bucket |", "|---|---:|---:|"]
    for c, n in new_hits.most_common():
        L.append(f"| {c} | {n:,} | {n/total*100:.1f}% |")
    L += [f"| **subtotal** | **{new_tot:,}** | **{new_tot/total*100:.1f}%** |", "",
          "## 2. Leakage — gigs that belong to a domain already collected", "",
          "Step 04 assigns a category only on an exact keyword substring, so a listing "
          "worded `develop-or-customize-drupal-websites` matches none of coding's keywords "
          "(`web-develop`, `app-develop`, `developer`) and falls through. Sizing that:", "",
          "| collected domain | leaked gigs | vs. gigs the step-04 label already holds |",
          "|---|---:|---|"]
    incat = {"design": 249623, "coding": 148212, "writing": 150875, "marketing": 76132,
             "video": 54959, "audio": 29195, "translation": 19869}  # step 67, in-window
    for c, n in leak_hits.most_common():
        L.append(f"| {c} | {n:,} | +{n/incat[c]*100:.0f}% |")
    L += [f"| **subtotal** | **{leak_tot:,}** | |", "",
          f"## 3. Residual long tail", "",
          f"**{len(residual):,} gigs ({len(residual)/total*100:.1f}%)** match neither table — "
          "finance/trading, coaching, sourcing, wellness, one-off novelty listings. Sample:", ""]
    for i, g in enumerate(sorted(residual)):
        if i % max(1, len(residual) // 25) == 0:
            L.append(f"- `{g}`")

    (OUTDIR / "families.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:40]))
    print(f"\nWrote {OUTDIR/'families.md'}")


if __name__ == "__main__":
    main()
