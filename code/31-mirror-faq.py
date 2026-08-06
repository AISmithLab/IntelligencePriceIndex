#!/usr/bin/env python3
"""Step 31: mirror the live FAQ into the draft — Phase 3 of `plans/active/publication.md`.

`drafts/sections/faq.md` is a markdown copy of `docs/faq.html`. It was maintained
by hand, and it drifted: the mirror sat at 2026-07-12 while the live page went
through the real-terms rollout (07-30), a full FAQ audit (07-30) and the non-gig
exclusion (07-31), so for three weeks the draft carried retracted numbers. A
hand-copied mirror will drift again, so this script generates it instead.

The live HTML is authoritative. Re-run after any FAQ edit.

Run:  python3 code/31-mirror-faq.py
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "docs" / "faq.html"
OUT = BASE / "drafts" / "sections" / "faq.md"

INLINE_OPEN = {"b": "**", "strong": "**", "i": "*", "em": "*", "code": "`"}
BLOCK = {"p", "h1", "h2", "h3", "h4", "li", "tr", "div"}


class FaqParser(HTMLParser):
    """Walks the page and emits markdown for the question cards and the contents list."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []            # finished markdown blocks
        self.buf = []            # inline text of the block being built
        self.stack = []          # open tag names
        self.in_paper = False    # inside the card that holds the questions
        self.in_toc = False
        self.cur_block = None    # tag name of the open block element
        self.cur_class = ""
        self.table = None        # {"head": [...], "rows": [[...]]}
        self.row = None
        self.cell = None
        self.list_kind = []      # stack of "ul" / "ol"
        self.li_index = []
        self.href = None
        self.section_ids = []

    # -- helpers ------------------------------------------------------------
    def _text(self):
        t = "".join(self.buf)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def _flush(self):
        text = self._text()
        self.buf = []
        return text

    def _emit(self, md):
        if md:
            self.out.append(md)

    # -- tags ---------------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "")
        self.stack.append(tag)

        if tag == "div":
            if "paper" in cls:
                self.in_paper = True
            if "toc" in cls:
                self.in_toc = True
            if "q" in cls.split() and a.get("id"):
                self.section_ids.append(a["id"])
            return

        if not (self.in_paper or self.in_toc):
            return

        if tag in INLINE_OPEN:
            self.buf.append(INLINE_OPEN[tag])
        elif tag == "a":
            self.href = a.get("href", "")
            self.buf.append("[")
        elif tag == "br":
            self.buf.append(" ")
        elif tag in ("ul", "ol"):
            self.list_kind.append(tag)
            self.li_index.append(0)
        elif tag == "li":
            self.buf = []
            self.cur_block = "li"
        elif tag == "table":
            self.table = {"head": [], "rows": []}
        elif tag == "tr":
            self.row = []
        elif tag in ("th", "td"):
            self.buf = []
            self.cell = tag
        elif tag in ("p", "h2", "h3", "h4"):
            self.buf = []
            self.cur_block = tag
            self.cur_class = cls

    def handle_endtag(self, tag):
        if self.stack and tag in self.stack:
            # pop back to the matching tag
            while self.stack:
                t = self.stack.pop()
                if t == tag:
                    break

        if tag == "div":
            # the questions card ends before the footer
            return

        if not (self.in_paper or self.in_toc):
            return

        if tag in INLINE_OPEN:
            self.buf.append(INLINE_OPEN[tag])
        elif tag == "a":
            txt = "".join(self.buf)
            i = txt.rfind("[")
            label = txt[i + 1:]
            self.buf = [txt[:i], f"[{label}]({self.href})" if self.href else label]
            self.href = None
        elif tag in ("ul", "ol"):
            if self.list_kind:
                self.list_kind.pop()
                self.li_index.pop()
            self.cur_block = None
        elif tag == "li":
            text = self._flush()
            if text:
                if self.list_kind and self.list_kind[-1] == "ol":
                    self.li_index[-1] += 1
                    self._emit(f"{self.li_index[-1]}. {text}")
                else:
                    self._emit(f"- {text}")
            self.cur_block = None
        elif tag in ("th", "td"):
            if self.row is not None:
                self.row.append(self._flush())
            self.cell = None
        elif tag == "tr":
            if self.table is not None and self.row:
                if not self.table["head"]:
                    self.table["head"] = self.row
                else:
                    self.table["rows"].append(self.row)
            self.row = None
        elif tag == "table":
            self._emit(self._render_table())
            self.table = None
        elif tag in ("p", "h2", "h3", "h4"):
            text = self._flush()
            if text:
                if tag == "h3":
                    self._emit(f"### {text}")
                elif tag == "h2":
                    self._emit(f"## {text}")
                elif tag == "h4":
                    self._emit(f"#### {text}")
                elif "step" in self.cur_class:
                    self._emit(f"**{text}**")
                else:
                    self._emit(text)
            self.cur_block = None
            self.cur_class = ""

    def handle_data(self, data):
        if self.in_paper or self.in_toc:
            if self.cur_block or self.cell is not None:
                self.buf.append(data)

    def _render_table(self):
        t = self.table
        if not t or not t["head"]:
            return ""
        width = max(len(t["head"]), *(len(r) for r in t["rows"])) if t["rows"] else len(t["head"])
        def pad(r):
            return r + [""] * (width - len(r))
        lines = ["| " + " | ".join(pad(t["head"])) + " |",
                 "|" + "---|" * width]
        for r in t["rows"]:
            lines.append("| " + " | ".join(pad(r)) + " |")
        return "\n".join(lines)


def main():
    if not SRC.exists():
        sys.exit(f"missing {SRC}")
    p = FaqParser()
    p.feed(SRC.read_text())

    body = "\n\n".join(p.out)
    # the contents list duplicates the question headings; keep it, it is the
    # page's own reading order and the draft is easier to navigate with it
    n_q = sum(1 for line in body.splitlines() if line.startswith("### "))

    header = f"""# FAQ & Methodology · Draft Section

**Target file:** `docs/faq.html`
**Status:** GENERATED — do not edit by hand.
**Generated by:** `code/31-mirror-faq.py` from `docs/faq.html`, which is authoritative.
**Audience:** freelancers and buyers active on Fiverr and Upwork, plus researchers
interested in AI's effect on the price of knowledge work.

This mirror was previously maintained by hand and drifted three weeks out of date,
carrying retracted figures while the live page had been corrected. It is now
generated; re-run the script after any FAQ edit rather than editing this file.

Questions appear in the live page's reading order ({n_q} sections).

---

"""
    OUT.write_text(header + body + "\n")
    print(f"Wrote {OUT.relative_to(BASE)}")
    print(f"  {n_q} question sections, {len(body.split())} words")
    print(f"  anchors: {', '.join(p.section_ids)}")


if __name__ == "__main__":
    main()
