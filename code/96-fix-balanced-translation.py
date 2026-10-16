#!/usr/bin/env python3
"""
Step 96: TD6 -- rebuild the balanced panel's categories without language names.

Step 04 classifies a slug into the first matching category in the order
writing, coding, design, translation, data_entry, data_analysis, video,
marketing, audio. Its translation list includes bare language names
("german", "spanish", ...), and translation comes before audio and marketing,
so `record-a-german-voice-over` and `make-german-seo-backlinks` were filed as
translation. In the balanced panel that put ~40% non-translation gigs into
translation (TD6; the same leak TD5 fixed in the pilot's step 19).

This step re-runs step 04's own `classify_slug` with ONE change: the
translation keywords become

    translat, locali, subtitle, caption, transcri, interpreter, interpreting,
    interprete

i.e. the language names are dropped and the bare "interpret" is narrowed
(it matched dream and data interpretation). caption and transcri stay: the
balanced panel carries a subtitles/transcription narrow cell (step 16), and
"caption" is already caught by writing first. A dropped gig falls through to
whatever step 04 would otherwise have assigned -- audio for voice-overs,
marketing for German SEO -- or out of the seven categories altogether
(language tutoring, fortune telling, typing), where build_panel's
known-category filter excludes it.

Step 04 itself is left untouched: steps 70 and 72 measure ITS behaviour.

Before writing, it checks that the unmodified classifier reproduces the
current file exactly, so the only difference is the keyword change.

Input:  data/pilot/balanced-gig-category.csv.gz   (gig_id, category)
Output: data/pilot/balanced-gig-category.csv.gz   rewritten in place
        runs/td6-rebuild/reclassify.md             transition table + examples

    python3 code/96-fix-balanced-translation.py
"""
import importlib.util
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
CATEGORY = BASE / "data" / "pilot" / "balanced-gig-category.csv.gz"
REPORT = BASE / "runs" / "td6-rebuild" / "reclassify.md"
SEVEN = ["audio", "coding", "design", "marketing", "translation", "video", "writing"]
TRANSLATION = ["translat", "locali", "subtitle", "caption", "transcri",
               "interpreter", "interpreting", "interprete"]


def load_step04():
    spec = importlib.util.spec_from_file_location("m04", BASE / "code" / "04-classify-categories.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    m = load_step04()
    c = pd.read_csv(CATEGORY)
    slug = c.gig_id.str.split("/", n=1).str[1].fillna("")

    redo = [m.classify_slug(s)[0] for s in slug]
    if not (pd.Series(redo, index=c.index) == c.category).all():
        raise SystemExit("step 04 no longer reproduces the current file -- it has already "
                         "been rewritten, or step 04 changed. Restore it from git first.")

    m.CATEGORIES["translation"] = TRANSLATION
    c["new"] = [m.classify_slug(s)[0] for s in slug]

    moved = c[c.category != c.new]
    if not (moved.category == "translation").all():
        raise SystemExit("the keyword change moved a non-translation gig; check step 04")

    out = c.loc[c.new.isin(SEVEN), ["gig_id", "new"]].rename(columns={"new": "category"})
    out.to_csv(CATEGORY, index=False, compression="gzip")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    L = ["# Step 96 -- TD6: balanced-panel translation reclassified", "",
         f"Translation keywords now: `{', '.join(TRANSLATION)}` (language names dropped). "
         "Every other step-04 rule unchanged; the unmodified classifier was verified to "
         "reproduce the old file exactly before rewriting.", "",
         "| Category | Before | After | Change |", "|---|---:|---:|---:|"]
    before, after = c.category.value_counts(), out.category.value_counts()
    for k in SEVEN:
        L.append(f"| {k} | {before.get(k, 0):,} | {after.get(k, 0):,} | {after.get(k, 0) - before.get(k, 0):+,} |")
    L.append(f"| **all seven** | {len(c):,} | {len(out):,} | {len(out) - len(c):+,} |")
    L += ["", "## Where the old translation gigs went", "", "| New label | Gigs | Examples |", "|---|---:|---|"]
    t = c[c.category == "translation"]
    for k, n in t.new.value_counts().items():
        ex = t[t.new == k].gig_id.str.split("/", n=1).str[1].sample(min(3, n), random_state=0)
        L.append(f"| {k}{'' if k in SEVEN else ' (dropped)'} | {n:,} | " + ", ".join(f"`{e}`" for e in ex) + " |")
    REPORT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
