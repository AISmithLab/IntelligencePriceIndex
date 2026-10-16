#!/usr/bin/env python3
"""
Step 93: AI-exposure scores for the 35 narrow categories.

EXPLORATORY, and written down BEFORE any outcome is estimated on it (same rule as
step 45). Step 45 scored the 7 broad categories; with exposure varying across 7
clusters, every exposure DiD in steps 76/88/90 has at most 7 effective
observations. This step scores step 16's narrow taxonomy so the tests can use 35.

SOURCE: Eloundou et al. (2024) occupation-level beta, vendored at
data/eloundou-2023-occ-level.csv -- human_rating_beta (primary) and
dv_rating_beta (GPT-4, robustness), exactly as step 45.

MAPPING RULES, fixed here:
  * each narrow category -> the O*NET occupations whose core task the gig sells,
    equally weighted (no Fiverr employment weights exist);
  * every `<family>-other` remainder inherits its family's step-45 mapping
    unchanged, so the narrow scores nest the broad ones;
  * no mapping is revised after outcomes are seen.

KNOWN BLIND SPOT, declared now: beta measures exposure to LANGUAGE models and
LLM-powered software. Image and voice generation (Midjourney, Stable Diffusion,
ElevenLabs) are under-scored -- Fine Artists/Illustrators 0.31, Actors 0.16 --
so illustration, logo and voiceover cells are likely under-exposed relative to
their true 2023-24 exposure. Results are reported with that caveat, not adjusted.

    python3 code/93-narrow-exposure.py   ->  data/narrow-exposure.csv
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
ELOUNDOU = BASE / "data" / "eloundou-2023-occ-level.csv"
OUT = BASE / "data" / "narrow-exposure.csv"

# step 45's broad mapping, inherited by every <family>-other
BROAD = {
    "translation": ["27-3091.00"],
    "writing": ["27-3043.00", "27-3043.05", "27-3041.00", "27-3042.00", "43-9081.00"],
    "marketing": ["13-1161.00", "13-1161.01", "27-3031.00"],
    "coding": ["15-1251.00", "15-1252.00", "15-1254.00"],
    "design": ["27-1024.00", "27-1011.00", "15-1255.00"],
    "video": ["27-4032.00", "27-4031.00", "27-1014.00", "27-2012.00"],
    "audio": ["27-2042.00", "27-2041.00", "27-4014.00", "27-4011.00"],
}

NARROW = {
    # design
    "design-logo_brand": ["27-1024.00", "27-1011.00"],          # graphic designers, art directors
    "design-illustration": ["27-1013.00", "27-1024.00"],        # fine artists/illustrators, graphic designers
    "design-ui_ux_web": ["15-1255.00"],                         # web & digital interface designers
    "design-print_merch": ["27-1024.00", "43-9031.00"],         # graphic designers, desktop publishers
    "design-social_graphics": ["27-1024.00"],                   # graphic designers
    "design-threed_product": ["27-1021.00", "17-3011.00", "27-1025.00"],  # industrial designers, drafters, interior
    # coding
    "coding-web_dev": ["15-1254.00", "15-1299.01"],             # web developers, web administrators
    "coding-backend_api": ["15-1252.00", "15-1242.00", "15-1243.00", "15-1244.00"],  # software dev, DB admin/arch, sysadmin
    "coding-automation_bot": ["15-1251.00"],                    # computer programmers
    "coding-data_ml_ai": ["15-2051.00", "15-2051.01", "15-1221.00"],  # data scientists, BI analysts, CS research
    "coding-mobile_app": ["15-1252.00"],                        # software developers
    # writing
    "writing-content_seo": ["27-3043.00", "13-1161.01"],        # writers, search marketing strategists
    "writing-copywriting": ["27-3043.00", "27-3043.05"],        # writers, creative writers
    "writing-editing": ["27-3041.00", "43-9081.00"],            # editors, proofreaders
    "writing-ebook_book": ["27-3043.00", "27-3043.05"],         # writers, creative writers
    "writing-resume_bio": ["27-3043.00", "21-1012.00"],         # writers, career counselors
    # marketing
    "marketing-seo": ["13-1161.01"],                            # search marketing strategists
    "marketing-social_media": ["13-1161.00", "27-3031.00"],     # marketing specialists, PR specialists
    "marketing-ads_ppc": ["13-1161.01", "11-2011.00"],          # search marketing, advertising managers
    "marketing-email_funnel": ["13-1161.00"],                   # marketing specialists
    # video
    "video-video_editing": ["27-4032.00"],                      # film & video editors
    "video-animation": ["27-1014.00"],                          # special effects artists & animators
    "video-motion_intro": ["27-1014.00"],                       # special effects artists & animators
    # audio
    "audio-voiceover": ["27-3011.00", "27-2011.00"],            # broadcast announcers, actors
    "audio-music_prod": ["27-2041.00", "27-2042.00", "27-4014.00"],  # composers, musicians, sound engineers
    "audio-podcast": ["27-4014.00", "27-4011.00"],              # sound engineers, A/V technicians
    # translation
    "translation-translation": ["27-3091.00"],                  # interpreters & translators
    "translation-subtitle": ["27-3092.00", "27-3091.00"],       # captioners, translators
}
NARROW.update({f"{fam}-other": socs for fam, socs in BROAD.items()})


def main():
    e = pd.read_csv(ELOUNDOU).set_index("O*NET-SOC Code")
    rows = []
    for cell, socs in sorted(NARROW.items()):
        missing = [s for s in socs if s not in e.index]
        if missing:
            raise SystemExit(f"{cell}: SOC codes not in Eloundou file: {missing}")
        sub = e.loc[socs]
        rows.append({"narrow": cell, "family": cell.split("-", 1)[0],
                     "exposure_human": round(sub.human_rating_beta.mean(), 4),
                     "exposure_gpt4": round(sub.dv_rating_beta.mean(), 4),
                     "n_occupations": len(socs), "soc_codes": ";".join(socs),
                     "occupations": "; ".join(sub.Title)})
    df = pd.DataFrame(rows).sort_values("exposure_human", ascending=False)
    df.to_csv(OUT, index=False)
    print(df[["narrow", "exposure_human", "exposure_gpt4", "occupations"]].to_string(index=False))
    print(f"\n{len(df)} cells -> {OUT}")


if __name__ == "__main__":
    main()
