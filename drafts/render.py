#!/usr/bin/env python3
"""Assemble section markdown files into a dated HTML draft.

Usage:
    python3 drafts/render.py              # renders drafts/draft-YYYY-MM-DD.html
    python3 drafts/render.py --out foo.html  # renders to a custom path
    python3 drafts/render.py --main drafts/structure/main.md
                                          # renders drafts/structure-draft-YYYY-MM-DD.html
"""

import re
import datetime
import argparse
from pathlib import Path

DRAFTS_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Markdown include resolution
# ---------------------------------------------------------------------------

INCLUDE_RE = re.compile(r"^:\((.+?)\)\s*$", re.MULTILINE)


def resolve_includes(text: str, base: Path) -> str:
    """Replace :(path) directives with file contents."""

    def _replace(m: re.Match) -> str:
        target = base / m.group(1)
        if target.exists():
            return target.read_text()
        return f"<!-- MISSING: {m.group(1)} -->"

    return INCLUDE_RE.sub(_replace, text)


# ---------------------------------------------------------------------------
# Lightweight markdown -> HTML (no external deps)
# ---------------------------------------------------------------------------

def md_to_html(md: str) -> str:
    """Convert markdown to HTML. Handles headings, paragraphs, bold, italic,
    inline code, tables, and lists.  Good enough for a working-draft render."""
    lines = md.split("\n")
    html_parts: list[str] = []
    in_table = False
    in_list = False
    list_type = ""
    para_buf: list[str] = []

    def flush_para():
        if para_buf:
            text = " ".join(para_buf)
            text = _inline(text)
            html_parts.append(f"<p>{text}</p>")
            para_buf.clear()

    def flush_list():
        nonlocal in_list, list_type
        if in_list:
            html_parts.append(f"</{list_type}>")
            in_list = False
            list_type = ""

    def _inline(t: str) -> str:
        # images: ![alt](src) — repo-root-relative sources are rewritten to be
        # relative to drafts/, where the rendered HTML lives.
        def _img(m: re.Match) -> str:
            alt, src = m.group(1), m.group(2)
            if not re.match(r"^(https?:|/|\.)", src):
                src = f"../{src}"
            return f'<img src="{src}" alt="{alt}">'

        t = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _img, t)
        # inline code
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        # bold
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        # italic
        t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
        # markdown escape for a literal dollar sign — the sections write `\$10,000`
        # so the figure is not read as math. Unescape it, or the draft shows the
        # backslash. LaTeX in this draft never uses `\$`, so this is safe to do
        # globally. (`code/36-build-paper-page.py` already handled it.)
        t = t.replace(r"\$", "$")
        return t

    i = 0
    while i < len(lines):
        line = lines[i]

        # headings
        hm = re.match(r"^(#{1,6})\s+(.+)$", line)
        if hm:
            flush_para()
            flush_list()
            level = len(hm.group(1))
            text = _inline(hm.group(2))
            slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            html_parts.append(f'<h{level} id="{slug}">{text}</h{level}>')
            i += 1
            continue

        # table
        if "|" in line and line.strip().startswith("|"):
            flush_para()
            flush_list()
            if not in_table:
                in_table = True
                html_parts.append("<table>")
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # skip separator rows like |---|---|
            if all(re.match(r"^[-:]+$", c) for c in cells):
                i += 1
                continue
            tag = "th" if not any("<td>" in p for p in html_parts[-5:] if "<t" in p) and html_parts[-1] == "<table>" else "td"
            row = "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells)
            html_parts.append(f"<tr>{row}</tr>")
            i += 1
            continue
        else:
            if in_table:
                html_parts.append("</table>")
                in_table = False

        # unordered list
        ulm = re.match(r"^(\s*)[-*]\s+(.+)$", line)
        if ulm:
            flush_para()
            if not in_list or list_type != "ul":
                flush_list()
                html_parts.append("<ul>")
                in_list = True
                list_type = "ul"
            html_parts.append(f"<li>{_inline(ulm.group(2))}</li>")
            i += 1
            continue

        # ordered list
        olm = re.match(r"^(\s*)\d+[.)]\s+(.+)$", line)
        if olm:
            flush_para()
            if not in_list or list_type != "ol":
                flush_list()
                html_parts.append("<ol>")
                in_list = True
                list_type = "ol"
            html_parts.append(f"<li>{_inline(olm.group(2))}</li>")
            i += 1
            continue

        # blank line
        if not line.strip():
            flush_para()
            flush_list()
            i += 1
            continue

        # regular text -> paragraph buffer
        para_buf.append(line.strip())
        i += 1

    flush_para()
    flush_list()
    if in_table:
        html_parts.append("</table>")

    return "\n".join(html_parts)


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  @media print {{
    body {{ font-size: 10pt; }}
    h2 {{ page-break-before: always; }}
    h2:first-of-type {{ page-break-before: avoid; }}
    table {{ page-break-inside: avoid; }}
  }}
  body {{
    font-family: "Times New Roman", Times, Georgia, serif;
    max-width: 750px;
    margin: 40px auto;
    padding: 0 20px;
    line-height: 1.5;
    color: #1a1a1a;
    font-size: 12pt;
  }}
  h1 {{
    font-size: 18pt;
    text-align: center;
    margin-bottom: 30px;
    line-height: 1.3;
  }}
  h2 {{ font-size: 14pt; margin-top: 28px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }}
  h3 {{ font-size: 12pt; margin-top: 20px; }}
  h4 {{ font-size: 11pt; margin-top: 16px; }}
  p {{ margin: 8px 0; text-align: justify; }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 10pt;
  }}
  th, td {{
    border: 1px solid #999;
    padding: 4px 8px;
    text-align: left;
  }}
  th {{ background-color: #f0f0f0; font-weight: bold; }}
  ul, ol {{ margin: 8px 0; padding-left: 24px; }}
  li {{ margin: 4px 0; }}
  code {{ font-size: 10pt; background: #f5f5f5; padding: 1px 4px; }}
  img {{ display: block; width: 100%; max-width: 100%; height: auto; margin: 16px auto 4px; }}
  em {{ font-style: italic; }}
  strong {{ font-weight: bold; }}
  .draft-notice {{
    text-align: center;
    color: #c00;
    font-size: 10pt;
    margin-bottom: 20px;
    padding: 8px;
    border: 1px solid #c00;
  }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def render(out_path: Path | None = None, main_path: Path | None = None) -> Path:
    """Assemble `main_path` (default drafts/main.md) into dated HTML.

    A second paper lives in its own subtree (e.g. drafts/structure/main.md) with
    its own sections/. Includes resolve relative to the main file's directory,
    but the rendered HTML is always written into drafts/ so the `../`-relative
    image rewriting in _inline() keeps working."""
    today = datetime.date.today().isoformat()
    if main_path is None:
        main_path = DRAFTS_DIR / "main.md"
    main_path = Path(main_path).resolve()
    base = main_path.parent
    main_md = main_path.read_text()
    assembled = resolve_includes(main_md, base)
    body_html = md_to_html(assembled)

    # Extract title from first H1
    title_match = re.search(r"<h1[^>]*>(.+?)</h1>", body_html)
    title = title_match.group(1) if title_match else "Working Draft"

    # Insert draft notice after first H1
    notice = f'<div class="draft-notice">WORKING DRAFT \u2014 {today} \u2014 Not for distribution</div>'
    if title_match:
        insert_pos = title_match.end()
        body_html = body_html[:insert_pos] + "\n" + notice + "\n" + body_html[insert_pos:]
    else:
        body_html = notice + "\n" + body_html

    html = HTML_TEMPLATE.format(title=title, body=body_html)

    if out_path is None:
        prefix = "" if base == DRAFTS_DIR else f"{base.name}-"
        out_path = DRAFTS_DIR / f"{prefix}draft-{today}.html"
    out_path.write_text(html)
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render paper draft to HTML")
    parser.add_argument("--out", type=Path, default=None, help="Output path")
    parser.add_argument("--main", type=Path, default=None,
                        help="Master document (default: drafts/main.md)")
    args = parser.parse_args()
    result = render(args.out, args.main)
    print(f"Rendered: {result}")
