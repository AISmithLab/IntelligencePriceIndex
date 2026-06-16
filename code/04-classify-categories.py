#!/usr/bin/env python3
"""
Step 1.4: Classify gig pages by category using keyword matching on gig slugs.

Matches against the taxonomy from data/task-taxonomy.md.

Input:  data/cdx-index/gig-pages-deduped.tsv
Output: data/cdx-index/gig-pages-classified.tsv (adds 'category' column)
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-deduped.tsv"
OUTPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"

# Category keyword mappings derived from task-taxonomy.md
# Tier 1 categories (strongest data for IPI)
CATEGORIES = {
    "writing": [
        "article", "blog", "copywriting", "copywriter", "seo-writing", "content-writ",
        "ghostwrit", "ghostwrite", "ebook", "e-book", "book-writ", "write-your",
        "write-a", "write-an", "writing", "rewrite", "proofread", "edit-your",
        "editing", "editor", "resume", "cover-letter", "press-release",
        "product-description", "creative-writ", "story", "script-writ",
        "speech", "grant-writ", "technical-writ", "white-paper", "case-study",
        "newsletter", "email-copy", "sales-copy", "ad-copy", "slogan", "tagline",
        "caption", "linkedin-profile", "bio-writ",
    ],
    "coding": [
        "python", "javascript", "java", "code", "coding", "program", "developer",
        "software", "web-develop", "website-develop", "app-develop", "mobile-app",
        "wordpress", "shopify", "wix", "squarespace", "html", "css", "react",
        "angular", "vue", "node", "php", "ruby", "golang", "rust", "swift",
        "kotlin", "flutter", "api", "database", "sql", "mongodb", "firebase",
        "aws", "cloud", "devops", "docker", "bug-fix", "debug",
        "full-stack", "frontend", "backend", "web-scraping", "scraping",
        "automation", "bot", "discord-bot", "telegram-bot", "chatbot",
        "blockchain", "smart-contract", "solidity", "nft", "crypto",
        "machine-learning", "deep-learning", "ai-", "artificial-intelligence",
        "data-scien", "excel", "spreadsheet", "google-sheets",
    ],
    "design": [
        "logo", "graphic", "design", "illustration", "illustrat", "banner",
        "flyer", "poster", "brochure", "business-card", "brand", "identity",
        "infographic", "icon", "ui-", "ux-", "ui-ux", "web-design",
        "app-design", "photoshop", "figma", "canva", "packaging",
        "label", "book-cover", "album-cover", "thumbnail", "social-media-design",
        "t-shirt", "merch", "print", "3d-model", "3d-design", "cad",
        "architect", "interior-design", "fashion-design", "cartoon",
        "caricature", "portrait", "avatar", "character-design", "comic",
        "manga", "tattoo", "invitation", "card-design", "menu-design",
        "presentation", "powerpoint", "pitch-deck", "resume-design",
    ],
    "translation": [
        "translat", "interpret", "locali", "subtitle", "caption",
        "transcri", "spanish", "french", "german", "chinese", "japanese",
        "korean", "arabic", "portuguese", "italian", "russian", "hindi",
        "turkish", "dutch", "polish", "swedish", "danish", "norwegian",
        "finnish", "greek", "hebrew", "thai", "vietnamese", "indonesian",
        "malay", "tagalog", "urdu", "bengali", "tamil",
    ],
    # Tier 2
    "data_entry": [
        "data-entry", "data-input", "typing", "copy-paste", "form-filling",
        "data-processing", "data-clean", "data-mining", "lead-generat",
        "web-research", "virtual-assist", "admin", "bookkeeping",
    ],
    "data_analysis": [
        "data-analy", "statistic", "visualiz", "dashboard", "tableau",
        "power-bi", "r-program", "spss", "stata", "survey",
        "market-research", "financial-model", "forecast",
    ],
    "video": [
        "video", "animation", "animat", "motion-graphic", "explainer",
        "whiteboard", "2d-animat", "3d-animat", "video-edit",
        "after-effects", "premiere", "film", "cinemat", "drone",
        "lyric-video", "music-video", "promo-video", "intro",
        "outro", "lottie", "gif",
    ],
    "marketing": [
        "seo", "social-media", "facebook", "instagram", "twitter",
        "tiktok", "youtube", "pinterest", "linkedin-market",
        "google-ads", "ppc", "email-market", "market",
        "influencer", "affiliate", "growth", "funnel",
        "landing-page", "conversion", "analytics",
    ],
    "audio": [
        "voiceover", "voice-over", "voice-act", "narrat", "podcast",
        "audio", "music", "song", "jingle", "sound-design",
        "mixing", "mastering", "beat", "instrumental", "singing",
        "composer", "composition",
    ],
}


def classify_slug(slug):
    """Classify a gig slug into categories. Returns list of matching categories."""
    slug_lower = slug.lower()
    matches = []
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in slug_lower:
                matches.append(category)
                break
    return matches if matches else ["uncategorized"]


def extract_slug(url):
    """Extract the gig slug from a Fiverr URL."""
    url = url.split("?")[0].split("#")[0]
    path = url.split("fiverr.com/")[-1] if "fiverr.com/" in url else url
    parts = path.strip("/").split("/")
    if len(parts) >= 2:
        return parts[1]
    return ""


def main():
    print("Classifying gig pages by category...")

    total = 0
    category_counts = {}

    with open(INPUT, "r") as fin, open(OUTPUT, "w") as fout:
        header = fin.readline().strip()
        fout.write(header + "\tcategory\n")

        for line in fin:
            line = line.strip()
            if not line:
                continue
            total += 1

            parts = line.split("\t")
            original = parts[2] if len(parts) > 2 else ""
            slug = extract_slug(original)
            categories = classify_slug(slug)

            # Use primary category (first match) for the TSV
            primary = categories[0]
            fout.write(f"{line}\t{primary}\n")

            for cat in categories:
                category_counts[cat] = category_counts.get(cat, 0) + 1

    print(f"\nClassification results ({total:,} records):")
    print(f"{'Category':<20} {'Count':>10} {'%':>8}")
    print("-" * 40)
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"{cat:<20} {count:>10,} {count/total*100:>7.1f}%")

    print(f"\nOutput: {OUTPUT}")


if __name__ == "__main__":
    main()
