#!/usr/bin/env python3
"""Step 35: resolve and validate the bibliography — Phase 4.

The draft carries `[CITE-key]` placeholders. This script:

  1. checks every placeholder resolves to an entry in `drafts/references.json`;
  2. reports entries that are defined but never cited (dead weight);
  3. reports every entry whose status is UNVERIFIED, which is a SUBMISSION BLOCKER
     -- an unverified citation is worse than a missing one, because a reader
     cannot tell it apart from a checked one;
  4. writes `drafts/sections/references.md`, alphabetical, with unverified
     entries visibly marked so the flag survives into the rendered draft.

Exit code is non-zero if any placeholder fails to resolve. UNVERIFIED entries are
reported loudly but do not fail the run, because the draft is expected to carry
them until the final citation pass.

Run:  python3 code/35-bibliography.py
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SECT = BASE / "drafts" / "sections"
REFS = json.loads((BASE / "drafts" / "references.json").read_text())["refs"]
OUT = SECT / "references.md"

# faq.md is generated from the live site and carries no citations
SOURCES = sorted(p for p in SECT.glob("*.md")
                 if p.name not in ("faq.md", "references.md"))

cited = {}
for p in SOURCES:
    for m in re.finditer(r"\[CITE-([a-z0-9-]+)(?:,\s*CITE-([a-z0-9-]+))*\]", p.read_text()):
        pass
# a bracket may hold several keys: [CITE-a, CITE-b]. Collect them all.
for p in SOURCES:
    txt = p.read_text()
    for m in re.finditer(r"\[((?:CITE-[a-z0-9-]+)(?:\s*,\s*CITE-[a-z0-9-]+)*)\]", txt):
        for k in re.findall(r"CITE-([a-z0-9-]+)", m.group(1)):
            cited.setdefault(k, set()).add(p.name)

print("=" * 88)
print("BIBLIOGRAPHY")
print("=" * 88)
total = sum(len(v) for v in cited.values())
print(f"{len(cited)} distinct keys cited across {len(SOURCES)} sections; "
      f"{len(REFS)} entries defined")

unresolved = sorted(k for k in cited if k not in REFS)
unused = sorted(k for k in REFS if k not in cited)
unverified = sorted(k for k in cited if k in REFS and REFS[k].get("status") == "UNVERIFIED")

if unresolved:
    print(f"\nUNRESOLVED ({len(unresolved)}) — cited but not defined:")
    for k in unresolved:
        print(f"  - {k}   (in {', '.join(sorted(cited[k]))})")
else:
    print("\nUNRESOLVED: none — every placeholder resolves.")

if unused:
    print(f"\nDEFINED BUT NEVER CITED ({len(unused)}):")
    for k in unused:
        print(f"  - {k}")

if unverified:
    print(f"\n*** UNVERIFIED ({len(unverified)}) — SUBMISSION BLOCKERS ***")
    print("    An unverified citation is worse than a missing one: the reader")
    print("    cannot tell it apart from a checked one. Verify, replace, or cut")
    print("    the claim each supports before submitting.")
    for k in unverified:
        r = REFS[k]
        print(f"  - {k}  (cited in {', '.join(sorted(cited[k]))})")
        print(f"      {r.get('note', 'no note')}")

# ------------------------------------------------------------------ emit
by_status = {}
for k in cited:
    if k in REFS:
        by_status[REFS[k].get("status", "confident")] = \
            by_status.get(REFS[k].get("status", "confident"), 0) + 1

L = ["## References", ""]
L.append(f"*{len(cited)} works cited. Entries marked* **[UNVERIFIED]** *could not be "
         f"confirmed and must be verified, replaced, or the supported claim cut "
         f"before submission — see `drafts/references.json`.*")
L.append("")
for k in sorted(cited, key=lambda k: (REFS.get(k, {}).get("authors", "zzz").lower(), k)):
    if k not in REFS:
        L.append(f"- **[MISSING ENTRY: {k}]**")
        continue
    r = REFS[k]
    mark = " **[UNVERIFIED]**" if r.get("status") == "UNVERIFIED" else ""
    L.append(f"- {r['authors']} ({r['year']}). *{r['title']}*. {r['venue']}.{mark}")
L.append("")
OUT.write_text("\n".join(L) + "\n")
print(f"\nWrote {OUT.relative_to(BASE)} — {len(cited)} entries "
      f"({', '.join(f'{v} {k}' for k, v in sorted(by_status.items()))})")
print("=" * 88)
sys.exit(1 if unresolved else 0)
