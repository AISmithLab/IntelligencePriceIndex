#!/usr/bin/env python3
"""Step 36: build the self-contained reading page for the paper.

Renders `drafts/sections/*.md` (in `drafts/main.md` order) into ONE standalone
HTML fragment suitable for publishing as an artifact: no external requests, all
five figures inlined as SVG, and LaTeX converted to HTML rather than left as
source (the artifact CSP blocks MathJax, so `$\\beta$` would otherwise render as
literal dollar-sign markup).

This is a *reading* surface. `drafts/render.py` remains the working-draft
renderer; neither is generated from the other, and both read the same sections.

Design notes, so a later editor does not undo them by accident:
  - Figures sit on a white plate in BOTH themes. The SVGs carry their own white
    background rect and the site's category palette, so re-theming them would
    mean regenerating them; a plate is honest and keeps them legible.
  - Numbers, captions and labels are monospace with tabular figures, because
    almost every claim in this paper is a number with a band attached.
  - Cells that miss the paper's own +/-5% adequacy criterion are marked amber,
    matching `docs/ipi.js`'s `.imprecise` treatment, so the site and the paper
    flag the same failures the same way.

Run:  python3 code/36-build-paper-page.py
"""
import html
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SECTIONS = BASE / "drafts" / "sections"
FIGURES = BASE / "outputs" / "figures"
OUT = BASE / "drafts" / "paper-page.html"

ORDER = [
    "abstract", "introduction", "related-work", "method",
    "findings", "discussion", "limitations", "conclusion", "references",
    "appendix-a",
]

# --------------------------------------------------------------------------
# LaTeX -> HTML.  The draft's math is a closed set; the five display equations
# are mapped by hand and the inline fragments by substitution.
# --------------------------------------------------------------------------

GREEK = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\varepsilon": "ε", r"\epsilon": "ε", r"\ell": "ℓ", r"\Delta": "Δ",
    r"\rho": "ρ", r"\sigma": "σ", r"\mu": "μ", r"\lambda": "λ",
}
OPS = {
    r"\times": "×", r"\cdot": "·", r"\approx": "≈", r"\in": "∈",
    r"\leq": "≤", r"\geq": "≥", r"\to": "→", r"\pm": "±", r"\sum": "Σ",
    r"\big": "", r"\left": "", r"\right": "", r"\,": " ", r"\;": " ",
}


def _frac(num: str, den: str) -> str:
    return (f'<span class="frac"><span class="num">{num}</span>'
            f'<span class="den">{den}</span></span>')


def tex_inline(s: str) -> str:
    """Convert a LaTeX fragment to inline HTML. Order matters."""
    s = re.sub(r"\\sqrt\{([^{}]*)\}", r"√<span class='rad'>\1</span>", s)
    s = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}",
               lambda m: _frac(tex_inline(m.group(1)), tex_inline(m.group(2))), s)
    s = re.sub(r"\\text\{([^{}]*)\}", r"<span class='rm'>\1</span>", s)
    s = re.sub(r"\\(ln|exp|log|max|min)\b", r"<span class='rm'>\1</span>", s)
    for k, v in {**GREEK, **OPS}.items():
        s = s.replace(k, v)
    # subscripts / superscripts, braced form first
    s = re.sub(r"_\{([^{}]*)\}", r"<sub>\1</sub>", s)
    s = re.sub(r"\^\{([^{}]*)\}", r"<sup>\1</sup>", s)
    s = re.sub(r"_([A-Za-z0-9])", r"<sub>\1</sub>", s)
    s = re.sub(r"\^([A-Za-z0-9])", r"<sup>\1</sup>", s)
    s = s.replace("\\", "")
    return s


DISPLAY = {
    "P_{s,t}": (
        "<span class='v'>P</span><sub>s,t</sub> = <span class='rm'>exp</span> "
        "<span class='paren'>(</span>"
        + _frac("1", "|S<sub>c,s,t</sub>|")
        + " <span class='big'>Σ</span><sub class='lim'>i ∈ S<sub>c,s,t</sub></sub> "
        "<span class='rm'>ln</span> "
        + _frac("p<sub>i,t</sub>", "p<sub>i,s</sub>")
        + "<span class='paren'>)</span>"
    ),
    "\\ln I^c_t = \\frac{1}{|L": (
        "<span class='rm'>ln</span> <span class='v'>I</span><sup>c</sup><sub>t</sub> = "
        + _frac("1", "|L<sub>c,t</sub>|")
        + " <span class='big'>Σ</span><sub class='lim'>ℓ ∈ L<sub>c,t</sub></sub> "
        "<span class='paren'>(</span><span class='rm'>ln</span> "
        "<span class='v'>P</span><sub>0,ℓ</sub> + <span class='rm'>ln</span> "
        "<span class='v'>P</span><sub>ℓ,t</sub><span class='paren'>)</span>"
    ),
    "\\Delta \\ln p_{i,t}": (
        "Δ<span class='rm'>ln</span> <span class='v'>p</span><sub>i,t</sub> = "
        "β Δ<span class='rm'>ln</span> (1 + <span class='v'>R</span><sub>i,t</sub>) "
        "+ ε<sub>i,t</sub>"
    ),
    "\\ln p_i = b_0": (
        "<span class='rm'>ln</span> <span class='v'>p</span><sub>i</sub> = "
        "b<sub>0</sub> + b<sub>1</sub> <span class='rm'>rating</span><sub>i</sub> + "
        "b<sub>2</sub> <span class='rm'>ln</span>(1 + <span class='v'>V</span><sub>i</sub>) + "
        "<span class='big'>Σ</span><sub class='lim'>c</sub> γ<sub>c</sub> "
        "<span class='rm'>taskType</span><sub>ic</sub> + ε<sub>i</sub>"
    ),
    "\\ln I^c_t = \\alpha_c": (
        "<span class='rm'>ln</span> <span class='v'>I</span><sup>c</sup><sub>t</sub> = "
        "α<sub>c</sub> + β<sub>c</sub> <span class='rm'>ln</span> "
        "(<span class='v'>A</span><sup>c</sup><sub>t</sub> + 1) + ε<sub>c,t</sub>"
    ),
}


def display_math(src: str) -> str:
    for key, rendered in DISPLAY.items():
        if key in src:
            return f'<div class="eq">{rendered}</div>'
    return f'<div class="eq">{tex_inline(src)}</div>'


MATHY = re.compile(r"[\\^_]")
# a reported statistic: "t = 5.32", "p &lt; 0.01", "|t| &gt; 1.96", "r = 0.996"
STAT = re.compile(r"^\|?[A-Za-z][A-Za-z0-9^_]*\|?\s*(=|&lt;|&gt;|≈|&le;|&ge;)")
# a parenthesised expression: "(s,t)", "(1 - n/N)"
PAREN = re.compile(r"\([A-Za-z0-9\s,\-+*/.]+\)")


def inline_math(text: str) -> str:
    """Replace $...$ with rendered math, leaving dollar amounts alone."""
    def repl(m):
        inner = m.group(1)
        if "<" in inner or r"\$" in inner:      # spans real markup, or is a price
            return m.group(0)
        looks_math = (bool(MATHY.search(inner))
                      or re.fullmatch(r"[+-]?[\d.]+", inner)
                      or re.fullmatch(r"[A-Za-z]", inner)
                      or bool(STAT.match(inner))
                      or bool(PAREN.fullmatch(inner)))
        if not looks_math:
            return m.group(0)
        return f'<span class="m">{tex_inline(inner)}</span>'
    return re.sub(r"\$([^$\n]{1,70})\$", repl, text)


# --------------------------------------------------------------------------
# Markdown -> HTML
# --------------------------------------------------------------------------

def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-")


DOLLAR = ""      # escaped \$ is hidden from the math scanner, then restored


def inline(t: str) -> str:
    t = html.escape(t, quote=False)
    t = t.replace("&lt;br&gt;", "<br>")
    t = t.replace(r"\$", DOLLAR)
    t = inline_math(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*]+)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((#[^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\[CITE-([^\]]+)\]",
               r'<span class="cite" title="citation key">\1</span>', t)
    t = t.replace(DOLLAR, "$").replace(r"\%", "%")
    return t


def figure(alt: str, src: str) -> str:
    path = BASE / src
    if not path.exists():
        return f"<!-- missing figure: {src} -->"
    svg = path.read_text()
    svg = re.sub(r'\s(width|height)="\d+"', "", svg, count=2)
    return (f'<figure class="fig"><div class="plate">{svg}</div>'
            f'<figcaption data-alt="{html.escape(alt)}">')


def convert(md: str) -> str:
    lines = md.split("\n")
    out, para, i = [], [], 0
    in_list = False
    open_caption = False

    def flush_para():
        nonlocal open_caption
        if not para:
            return
        text = inline(" ".join(para))
        para.clear()
        if open_caption:
            out.append(text + "</figcaption></figure>")
            open_caption = False
            return
        cls = ""
        if text.startswith("<em>(") or text.startswith("<em>("):
            cls = ' class="aside"'
        out.append(f"<p{cls}>{text}</p>")

    def flush_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("$$"):
            flush_para(); flush_list()
            out.append(display_math(line.strip()))
            i += 1
            continue

        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line.strip())
        if m:
            flush_para(); flush_list()
            out.append(figure(m.group(1), m.group(2)))
            open_caption = True
            i += 1
            continue

        m = re.match(r"^(#{2,4})\s+(.+)$", line)
        if m:
            flush_para(); flush_list()
            level, text = len(m.group(1)), m.group(2)
            num = re.match(r"^([\d.]+)\s+(.*)$", text)
            eyebrow = ""
            if num:
                eyebrow = f'<span class="secno">{num.group(1)}</span>'
                text = num.group(2)
            out.append(f'<h{level} id="{slug(text)}">{eyebrow}'
                       f'<span class="htext">{inline(text)}</span></h{level}>')
            i += 1
            continue

        if line.strip().startswith("|"):
            flush_para(); flush_list()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            body = []
            for r, cells in enumerate(rows):
                if r == 1 and all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    continue
                tag = "th" if r == 0 else "td"
                tds = []
                for c in cells:
                    cls = ""
                    if re.match(r"^[±+\-−]?[\d.,]+%?$", c.strip()) or "±" in c:
                        cls = ' class="num"'
                    if c.strip() in {"—", "-"}:
                        cls = ' class="num dash"'
                    tds.append(f"<{tag}{cls}>{inline(c)}</{tag}>")
                body.append("<tr>" + "".join(tds) + "</tr>")
            out.append('<div class="tw"><table>' + "".join(body) + "</table></div>")
            continue

        if re.match(r"^\s*[-*]\s+", line):
            flush_para()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", line)) + "</li>")
            i += 1
            continue

        if not line.strip():
            flush_para(); flush_list()
            i += 1
            continue

        para.append(line.strip())
        i += 1

    flush_para(); flush_list()
    return "\n".join(out)


# --------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------

CSS = """
:root{
  --paper:#FAFAFC; --plate:#FFFFFF; --ink:#1B2130; --mut:#5F6779;
  --rule:#E3E6EE; --rule-2:#EDEFF5; --accent:#3A38A6; --accent-soft:#EEEEF8;
  --flag:#B26A00; --retract:#A32B26; --shadow:0 1px 2px rgba(20,26,40,.05);
}
@media (prefers-color-scheme:dark){
  :root{
    --paper:#13161D; --plate:#1B1F28; --ink:#E8EAF1; --mut:#98A0B2;
    --rule:#2B313E; --rule-2:#232935; --accent:#A6A4F5; --accent-soft:#22243A;
    --flag:#E0A33C; --retract:#EC8B85; --shadow:none;
  }
}
:root[data-theme="dark"]{
  --paper:#13161D; --plate:#1B1F28; --ink:#E8EAF1; --mut:#98A0B2;
  --rule:#2B313E; --rule-2:#232935; --accent:#A6A4F5; --accent-soft:#22243A;
  --flag:#E0A33C; --retract:#EC8B85; --shadow:none;
}
:root[data-theme="light"]{
  --paper:#FAFAFC; --plate:#FFFFFF; --ink:#1B2130; --mut:#5F6779;
  --rule:#E3E6EE; --rule-2:#EDEFF5; --accent:#3A38A6; --accent-soft:#EEEEF8;
  --flag:#B26A00; --retract:#A32B26; --shadow:0 1px 2px rgba(20,26,40,.05);
}

*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:Georgia,"Iowan Old Style",Charter,"Times New Roman",serif;
  font-size:17.5px;line-height:1.62;-webkit-font-smoothing:antialiased}
.sans{font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif}
.mono,code,.num,.m,.eq,figcaption,.stat b,.secno,.cite,th,
.masthead .meta,.railtitle,.notice .lab{
  font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}

/* ---------- shell ---------- */
.wrap{max-width:1180px;margin:0 auto;padding:0 24px 96px;
  display:grid;grid-template-columns:210px minmax(0,1fr);gap:48px}
@media (max-width:900px){.wrap{grid-template-columns:1fr;gap:0}}

/* ---------- masthead ---------- */
.masthead{grid-column:1/-1;padding:56px 0 28px;border-bottom:1px solid var(--rule)}
.kicker{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--accent);margin:0 0 14px}
h1{font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
  font-size:clamp(30px,4.4vw,46px);line-height:1.1;letter-spacing:-.022em;
  font-weight:680;margin:0 0 14px;text-wrap:balance;max-width:20ch}
.dek{font-size:19px;color:var(--mut);margin:0 0 26px;max-width:62ch;line-height:1.5}
.meta{font-size:11.5px;color:var(--mut);letter-spacing:.02em;
  display:flex;flex-wrap:wrap;gap:6px 20px;margin-bottom:26px}
.meta b{color:var(--ink);font-weight:500}

.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));
  gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:3px;
  overflow:hidden}
.stat{background:var(--plate);padding:14px 16px}
.stat span{display:block;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
  font-size:10px;letter-spacing:.11em;text-transform:uppercase;color:var(--mut);
  margin-bottom:6px}
.stat b{display:block;font-size:22px;font-weight:600;letter-spacing:-.02em;
  font-variant-numeric:tabular-nums}
.stat i{font-style:normal;font-size:12px;color:var(--mut);
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace}

.notice{grid-column:1/-1;margin:24px 0 0;padding:13px 16px;border-radius:3px;
  border:1px solid var(--rule);border-left:3px solid var(--retract);
  background:var(--plate);font-size:15px;color:var(--mut);line-height:1.5}
.notice .lab{display:block;font-size:10px;letter-spacing:.13em;text-transform:uppercase;
  color:var(--retract);margin-bottom:5px}
.notice b{color:var(--ink);font-weight:600}

/* ---------- rail ---------- */
nav.rail{position:sticky;top:0;align-self:start;padding:34px 0;max-height:100vh;
  overflow-y:auto}
@media (max-width:900px){nav.rail{position:static;max-height:none;
  border-bottom:1px solid var(--rule);margin-bottom:8px}}
.railtitle{font-size:10px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--mut);margin:0 0 12px}
nav.rail ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:1px}
nav.rail a{display:grid;grid-template-columns:22px 1fr;gap:8px;
  font-family:ui-sans-serif,system-ui,-apple-system,Arial,sans-serif;
  font-size:13px;line-height:1.35;color:var(--mut);text-decoration:none;
  padding:5px 6px;border-radius:3px}
nav.rail a em{font-style:normal;font-family:ui-monospace,Menlo,monospace;
  font-size:11px;color:var(--accent);opacity:.75}
nav.rail a:hover{background:var(--accent-soft);color:var(--ink)}
nav.rail a:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
nav.rail a.sub{grid-template-columns:22px 1fr;font-size:12px;opacity:.82}

/* ---------- article ---------- */
article{padding:34px 0 0;max-width:70ch}
h2{font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
  font-size:26px;font-weight:650;letter-spacing:-.018em;line-height:1.2;
  margin:56px 0 18px;padding-top:22px;border-top:1px solid var(--rule);
  text-wrap:balance;display:flex;gap:12px;align-items:baseline}
h3{font-family:ui-sans-serif,system-ui,-apple-system,"Helvetica Neue",Arial,sans-serif;
  font-size:18px;font-weight:640;letter-spacing:-.01em;margin:38px 0 12px;
  text-wrap:balance;display:flex;gap:10px;align-items:baseline}
h4{font-family:ui-sans-serif,system-ui,Arial,sans-serif;font-size:15px;
  font-weight:640;margin:26px 0 8px}
.secno{font-size:12px;color:var(--accent);font-weight:400;letter-spacing:.04em;
  flex:none;padding-top:2px}
h2 .htext,h3 .htext{display:block}
p{margin:0 0 17px}
p.aside{font-size:15.5px;color:var(--mut);border-left:2px solid var(--rule);
  padding-left:15px;line-height:1.55}
strong{font-weight:700}
ul{margin:0 0 18px;padding-left:20px}
li{margin:0 0 9px}
code{font-size:.86em;background:var(--accent-soft);padding:1px 5px;border-radius:2px}
a{color:var(--accent)}
.cite{font-size:.76em;color:var(--mut);background:var(--rule-2);
  padding:1px 5px;border-radius:2px;letter-spacing:.01em;white-space:nowrap}

/* ---------- tables ---------- */
.tw{overflow-x:auto;margin:0 0 22px;border:1px solid var(--rule);border-radius:3px;
  background:var(--plate)}
table{border-collapse:collapse;width:100%;font-size:13.5px;
  font-family:ui-sans-serif,system-ui,Arial,sans-serif}
th{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:10.5px;
  letter-spacing:.07em;text-transform:uppercase;color:var(--mut);font-weight:500;
  text-align:left;padding:10px 13px;border-bottom:1px solid var(--rule);
  white-space:nowrap;vertical-align:bottom}
td{padding:9px 13px;border-bottom:1px solid var(--rule-2);vertical-align:top}
tr:last-child td{border-bottom:none}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;
  white-space:nowrap}
td.dash{color:var(--mut)}

/* ---------- figures ---------- */
.fig{margin:30px 0 26px;padding:0}
.plate{background:#fff;border:1px solid var(--rule);border-radius:3px;
  padding:14px;box-shadow:var(--shadow);overflow-x:auto}
.plate svg{display:block;width:100%;height:auto;min-width:520px}
figcaption{font-size:12px;line-height:1.5;color:var(--mut);margin-top:10px;
  padding-left:1px}
figcaption strong{color:var(--ink);font-weight:600}

/* ---------- math ---------- */
.eq{margin:22px 0;padding:16px 18px;background:var(--plate);
  border:1px solid var(--rule);border-radius:3px;font-size:15px;
  text-align:center;overflow-x:auto;line-height:2.1}
.m{font-size:.95em;white-space:nowrap}
.rm{font-family:ui-sans-serif,system-ui,Arial,sans-serif;font-size:.92em}
.v{font-style:italic;font-family:Georgia,serif}
.frac{display:inline-flex;flex-direction:column;vertical-align:middle;
  text-align:center;margin:0 4px;font-size:.88em}
.frac .num{border-bottom:1px solid currentColor;padding:0 4px 1px;line-height:1.3}
.frac .den{padding:1px 4px 0;line-height:1.3}
.big{font-size:1.4em;vertical-align:-.12em}
.lim{font-size:.68em}
.paren{font-size:1.25em;vertical-align:-.06em;padding:0 2px}
.rad{border-top:1px solid currentColor;padding:0 1px}

footer{grid-column:1/-1;margin-top:64px;padding-top:22px;
  border-top:1px solid var(--rule);font-size:12px;color:var(--mut);
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace;line-height:1.7}
@media print{nav.rail{display:none}.wrap{grid-template-columns:1fr}}
"""

MASTHEAD = """
<header class="masthead">
  <p class="kicker">Working paper &middot; measurement</p>
  <h1>The Intelligence Price Index</h1>
  <p class="dek">A quarterly matched-model price index for cognitive-labor
  services, built from web archives &mdash; and an account of what pilot-scale
  archival data can and cannot resolve about AI's effect on it.</p>
  <div class="meta">
    <span>Draft <b>2026-08-06</b></span>
    <span>Window <b>2020Q1&ndash;2026Q1</b></span>
    <span>Source <b>37,782 archived Fiverr gig-price snapshots</b></span>
    <span>Estimator <b>GEKS-Jevons</b></span>
    <span>~<b>17,150</b> words</span>
  </div>
  <div class="stats">
    <div class="stat"><span>Composite, real</span><b>+40.7%</b><i>&plusmn;3.7% &middot; nominal +78.4%</i></div>
    <div class="stat"><span>CPI-U, same window</span><b>+26.8%</b><i>~48% of the nominal rise</i></div>
    <div class="stat"><span>Reputation band</span><b>+39.7 / +79.0%</b><i>+7.7% per doubling of reviews</i></div>
    <div class="stat"><span>Meet the &plusmn;5% rule</span><b>1 of 7</b><i>design only; composite passes</i></div>
  </div>
</header>
<div class="notice">
  <span class="lab">Retraction carried in this version</span>
  Earlier drafts reported a <b>price elasticity of intelligence</b> of &minus;0.49
  to +1.10, all significant at <i>p</i> &lt; 0.01. It is a spurious regression and
  is retracted; the diagnostics are reported in its place in
  <a href="#a-regression-we-do-not-report-and-why">&sect;3.9</a>.
</div>
"""


def build_nav(body: str) -> str:
    items = []
    for m in re.finditer(r'<h([23]) id="([^"]+)">(?:<span class="secno">([^<]*)</span>)?'
                         r'<span class="htext">(.*?)</span></h[23]>', body, re.S):
        level, sid, no, text = m.groups()
        text = re.sub(r"<[^>]+>", "", text)
        if level == "3" and not no:
            continue
        cls = "" if level == "2" else "sub"
        items.append(f'<li><a class="{cls}" href="#{sid}"><em>{no or "&mdash;"}</em>'
                     f'<span>{text}</span></a></li>')
    return ('<nav class="rail" aria-label="Contents"><p class="railtitle">Contents</p>'
            "<ol>" + "".join(items) + "</ol></nav>")


def main() -> None:
    parts = []
    for name in ORDER:
        md = (SECTIONS / f"{name}.md").read_text()
        parts.append(f'<section id="sec-{name}">' + convert(md) + "</section>")
    body = "\n".join(parts)

    page = (f"<style>{CSS}</style>\n"
            '<div class="wrap">\n' + MASTHEAD + build_nav(body)
            + "<article>" + body + "</article>"
            '<footer>Rendered from drafts/sections/*.md &middot; figures from '
            'code/34-figures.py &middot; every figure in this page traces to '
            'data/pilot/paper-numbers.md, enforced by code/32-check-draft-numbers.py'
            "</footer></div>")
    OUT.write_text(page)

    figs = page.count("<figure")
    print(f"Wrote {OUT.relative_to(BASE)}")
    print(f"  {len(page):,} bytes   {figs} figures inlined   "
          f"{page.count('<table')} tables   {page.count('class=\"eq\"')} equations")
    leftovers = [f for f in re.findall(r"\$[^$\n<]{1,60}\$", page)
                 if re.search(r"[\\^_=]|&lt;|&gt;", f)]
    print(f"  unconverted math fragments: {len(leftovers)}"
          + (f"  e.g. {leftovers[:3]}" if leftovers else ""))


if __name__ == "__main__":
    main()
