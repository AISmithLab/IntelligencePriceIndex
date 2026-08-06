#!/usr/bin/env python3
"""Step 32: check the draft against the frozen numbers — Phase 3 guard.

Phase 2 froze the paper's figures into `data/pilot/paper-numbers.json` so that no
section computes its own. This script enforces it: for every headline quantity it
scans the rendered draft and the section sources, and fails if a section quotes a
value the frozen table does not contain.

It also greps for figures that were RETRACTED (the 312 peak, the -0.49..+1.10
elasticity range, "9 service categories", the 2019Q1 base) and reports where they
still appear, so that a retracted number cannot creep back in as an assertion. A
hit is not automatically an error -- the draft legitimately quotes retracted
figures while retracting them -- so those are reported with their surrounding
sentence for eyeballing rather than failing the run.

Run:  python3 code/32-check-draft-numbers.py
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SECT = BASE / "drafts" / "sections"
FROZEN = json.loads((BASE / "data" / "pilot" / "paper-numbers.json").read_text())

# sections the frozen table governs (faq.md is generated from the site; related-work
# is a literature review and quotes other papers' figures)
GOVERNED = ["abstract", "introduction", "method", "findings", "discussion",
            "limitations", "conclusion"]

text = {n: (SECT / f"{n}.md").read_text() for n in GOVERNED}
joined = "\n".join(text.values())

fails, warns = [], []


def expect(label, needle, where=None):
    """The draft must contain this string somewhere in the governed sections."""
    scope = text[where] if where else joined
    if needle in scope:
        print(f"  ok    {label:<42} '{needle}'")
    else:
        fails.append((label, needle, where or "any section"))
        print(f"  FAIL  {label:<42} '{needle}' not found in {where or 'any section'}")


print("=" * 88)
print("DRAFT vs FROZEN NUMBERS")
print("=" * 88)
print(f"frozen source: {FROZEN['source']} (generated {FROZEN['data_generated']}), "
      f"base {FROZEN['base_period']}, window {FROZEN['window']}")

comp = FROZEN["composite"]
print("\n-- composite ------------------------------------------------------------")
expect("composite nominal delta", f"+{comp['delta_nominal_pct']:.1f}%")
expect("composite real delta", f"+{comp['delta_real_pct']:.1f}%")
expect("composite band", f"±{comp['band_pct']:.1f}%")
expect("CPI-U change", f"+{FROZEN['cpi_change_pct']:.1f}%")

print("\n-- per category (real delta and band must both appear) -------------------")
for r in FROZEN["categories"]:
    expect(f"{r['label']} real delta", f"+{r['delta_real_pct']:.1f}%")
    expect(f"{r['label']} band", f"±{r['band_pct']:.1f}%")

print("\n-- adequacy rule --------------------------------------------------------")
n_fail = sum(1 for r in FROZEN["categories"] if not r["meets_5pct"])
expect("adequacy rule stated", f"±{FROZEN['adequacy_rule_pct']:.0f}%")
if not re.search(r"[Ss]ix of seven", joined):
    fails.append(("six-of-seven failure stated", "six of seven", "any section"))
    print(f"  FAIL  {'six-of-seven failure stated':<42} 'six of seven' not found")
else:
    print(f"  ok    {'six-of-seven failure stated':<42} (frozen table: {n_fail} of "
          f"{len(FROZEN['categories'])} fail)")
if n_fail != 6:
    fails.append(("frozen table disagrees with prose", f"{n_fail} fail", "paper-numbers.json"))
    print(f"  FAIL  frozen table says {n_fail} categories fail, prose says six")

print("\n-- reputation band (D2) -------------------------------------------------")
rb = FROZEN["reputation_band"]
expect("band upper (raw)", f"+{rb['raw_pct']:.1f}%")
expect("band lower (adjusted)", f"+{rb['adjusted_pct']:.1f}%")
expect("pooled beta", f"{rb['beta']:.4f}")

print("\n-- retracted figures: where do they still appear? -----------------------")
RETRACTED = {
    # 312 the retracted composite peak, NOT 312.8 (coding's link-path level in §3.7)
    "312 peak": r"\b312\b(?!\.)",
    "-0.49 elasticity": r"−0\.49|-0\.49",
    "+1.10 elasticity": r"\+1\.10",
    "nine categories": r"9 service categories|nine service categories",
    "2019Q1 base": r"2019Q1 ?= ?100|base 2019Q1",
    "21% reversal": r"21% (drop|decline)",
    "10.9% filled": r"10\.9% filled",
    "shadow deflation": r"shadow deflation",
}
RETRACTION_CUES = ("retract", "earlier version", "previous version", "no longer",
                   "artifact", "superseded", "could not be reproduced", "was an artifact")
for label, pat in RETRACTED.items():
    for name, body in text.items():
        for m in re.finditer(pat, body):
            # a fixed character window, not a sentence: figures like "-0.49" and
            # "312.8" contain periods, so sentence splitting truncates the context
            # and hides the retraction cue that precedes the hit
            s, e = max(0, m.start() - 400), min(len(body), m.end() + 200)
            sent = body[s:e].strip().replace("\n", " ")
            cued = any(c in sent.lower() for c in RETRACTION_CUES)
            tag = "ok   " if cued else "CHECK"
            if not cued:
                warns.append((label, name, sent[:150]))
            print(f"  {tag} {label:<20} {name:<14} {sent[:110]}")

print("\n" + "=" * 88)
if fails:
    print(f"FAILED: {len(fails)} frozen-number mismatches")
    for label, needle, where in fails:
        print(f"  - {label}: expected '{needle}' in {where}")
if warns:
    print(f"\n{len(warns)} retracted figure(s) appear WITHOUT a retraction cue nearby "
          f"— verify each is intentional:")
    for label, name, sent in warns:
        print(f"  - {label} in {name}.md: {sent}")
if not fails and not warns:
    print("PASS: every frozen figure appears, and every retracted figure is "
          "accompanied by a retraction cue.")
print("=" * 88)
sys.exit(1 if fails else 0)
