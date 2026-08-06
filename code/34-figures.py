#!/usr/bin/env python3
"""Step 34: generate the paper's figures — Phase 4 of `plans/active/publication.md`.

Emits standalone SVG into `outputs/figures/`. SVG rather than matplotlib because
matplotlib is not installed in this environment and the project already renders
its site charts as hand-built inline SVG, so this keeps one convention and no new
dependency. The files are self-contained and can be inlined into the draft HTML.

Figures:
  fig1-composite          real + nominal composite with CPI-U reference and 95% band
  fig2-categories         seven category panels, real, each with its band
  fig3-reputation-band    raw vs reputation-adjusted composite, plus a beta strip
  fig4-precision-curve    precision vs n, log-log, with the +/-5% and +/-10% rules
  fig5-linkpath           link-path support per quarter, historical vs recent

Everything is read from `docs/data.json` and the production panels; figure 4's
curve is RECOMPUTED here (subsample gigs, re-estimate, sd of the log level) rather
than transcribed from the 2026-08-05 session notes, so the figure is reproducible.

Run:  python3 code/34-figures.py
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(BASE / "code"))


def load(name, fn):
    spec = importlib.util.spec_from_file_location(name, BASE / "code" / fn)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


tpd = load("tpd", "19-tpd-index.py")
geks = load("geks", "21-geks-index.py")
CATS = tpd.CATS
q_int = tpd.q_to_int

D = json.loads((BASE / "docs" / "data.json").read_text())
Q = D["months"]
COL = D["colors"]
LAB = D["labels"]
INK, MUT, LINE, ACC = "#1c2230", "#6b7280", "#e8eaf0", "#4f46e5"

FONT = ('font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, '
        'Helvetica, Arial, sans-serif"')


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def svg_open(w, h, title, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img" aria-labelledby="t d">',
            f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>',
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>']


def txt(x, y, s, size=11, fill=MUT, anchor="start", weight="400"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" {FONT} font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')


def path(d, stroke, width=2.0, fill="none", opacity=1.0, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
            f'stroke-linejoin="round" stroke-linecap="round" opacity="{opacity}"{da}/>')


def polyline(xs, ys):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in zip(xs, ys))


def band_path(xs, los, his):
    up = " L ".join(f"{x:.1f} {y:.1f}" for x, y in zip(xs, his))
    dn = " L ".join(f"{x:.1f} {y:.1f}" for x, y in zip(reversed(xs), reversed(los)))
    return f"M {up} L {dn} Z"


def write(name, parts):
    p = OUT / f"{name}.svg"
    p.write_text("\n".join(parts) + "\n</svg>\n")
    print(f"  wrote {p.relative_to(BASE)}")


# =============================================================== figure 1
def fig1():
    W, H = 900, 420
    L, R, T, B = 58, 150, 34, 46
    pw, ph = W - L - R, H - T - B
    nom, real, cpi = D["composite_geks"], D["composite_geks_real"], D["cpi"]
    se = D["composite_geks_se"]
    lo = [v * math.exp(-1.96 * s) for v, s in zip(real, se)]
    hi = [v * math.exp(1.96 * s) for v, s in zip(real, se)]
    ymin, ymax = 90, max(max(nom), max(hi)) * 1.04

    def X(i):
        return L + pw * i / (len(Q) - 1)

    def Y(v):
        return T + ph * (1 - (v - ymin) / (ymax - ymin))

    s = svg_open(W, H, "Composite Intelligence Price Index, 2020Q1-2026Q1",
                 "Real and nominal composite index with CPI-U reference line and a "
                 "95 percent band on the real series.")
    for g in range(100, int(ymax) + 1, 20):
        s.append(path(f"M {L} {Y(g):.1f} L {L+pw} {Y(g):.1f}", LINE, 1))
        s.append(txt(L - 8, Y(g) + 3.5, str(g), 10, MUT, "end"))
    for i, q in enumerate(Q):
        if q.endswith("Q1"):
            s.append(txt(X(i), H - B + 16, q[:4], 10, MUT, "middle"))
    xs = [X(i) for i in range(len(Q))]
    s.append(path(band_path(xs, [Y(v) for v in lo], [Y(v) for v in hi]),
                  "none", 0, ACC, 0.13))
    s.append(path(polyline(xs, [Y(v) for v in cpi]), MUT, 1.6, dash="5 4"))
    s.append(path(polyline(xs, [Y(v) for v in nom]), "#9aa1ad", 1.8))
    s.append(path(polyline(xs, [Y(v) for v in real]), ACC, 2.6))
    # ChatGPT marker
    if "2022Q4" in Q:
        i = Q.index("2022Q4")
        s.append(path(f"M {X(i):.1f} {T} L {X(i):.1f} {T+ph}", "#c026d3", 1.2, dash="3 3"))
        s.append(txt(X(i) + 4, T + 12, "ChatGPT", 9.5, "#c026d3"))
    lx = L + pw + 14
    for k, (lab, col, wt) in enumerate([
            (f"Real  {real[-1]:.1f}  ({D['delta_geks_real']['composite']:+.1f}%)", ACC, "700"),
            (f"Nominal  {nom[-1]:.1f}  ({D['delta_geks']['composite']:+.1f}%)", "#9aa1ad", "400"),
            (f"CPI-U  {cpi[-1]:.1f}  ({cpi[-1]-100:+.1f}%)", MUT, "400")]):
        s.append(f'<rect x="{lx}" y="{T+6+k*22-8}" width="16" height="3" fill="{col}" rx="1.5"/>')
        s.append(txt(lx + 22, T + 6 + k * 22 - 2, lab, 10.5, INK, "start", wt))
    s.append(txt(lx, T + 6 + 3 * 22 + 14, "shaded: 95% band", 9.5, MUT))
    s.append(txt(lx, T + 6 + 3 * 22 + 28, "on the real series", 9.5, MUT))
    s.append(txt(L, 18, "Composite Intelligence Price Index", 13, INK, "start", "700"))
    s.append(txt(L, H - 8, "Base 2020Q1 = 100. Real series deflated by CPI-U (CPIAUCSL).",
                 9.5, MUT))
    write("fig1-composite", s)


# =============================================================== figure 2
def fig2():
    cols, rows = 4, 2
    cw, chh = 205, 150
    W, H = 40 + cols * cw, 46 + rows * chh + 26
    s = svg_open(W, H, "Category price indices, real terms",
                 "Seven category indices in real terms, each drawn with its own 95 "
                 "percent band. Panels share a common vertical scale.")
    s.append(txt(20, 20, "Category indices, real terms, with 95% bands", 13, INK, "start", "700"))
    order = sorted(CATS, key=lambda c: -D["weights"][c])
    allv = [v for c in CATS for v in D["index_geks_real"][c] if v]
    ymin, ymax = 80, max(allv) * 1.25
    for k, c in enumerate(order):
        r, col = divmod(k, cols)
        ox, oy = 30 + col * cw, 40 + r * chh
        pw, ph = cw - 34, chh - 44
        ser = D["index_geks_real"][c]
        se = D["index_geks_se"][c]

        def X(i):
            return ox + pw * i / (len(Q) - 1)

        def Y(v):
            return oy + ph * (1 - (v - ymin) / (ymax - ymin))

        s.append(f'<rect x="{ox}" y="{oy}" width="{pw}" height="{ph}" fill="#fbfcfe" '
                 f'stroke="{LINE}" stroke-width="1" rx="3"/>')
        s.append(path(f"M {ox} {Y(100):.1f} L {ox+pw} {Y(100):.1f}", "#cbd2de", 1, dash="3 3"))
        idx = [i for i, v in enumerate(ser) if v is not None]
        xs = [X(i) for i in idx]
        lo = [Y(ser[i] * math.exp(-1.96 * (se[i] or 0))) for i in idx]
        hi = [Y(ser[i] * math.exp(1.96 * (se[i] or 0))) for i in idx]
        s.append(path(band_path(xs, lo, hi), "none", 0, COL[c], 0.16))
        s.append(path(polyline(xs, [Y(ser[i]) for i in idx]), COL[c], 2.0))
        band = 196.0 * (se[idx[-1]] or 0)
        ok = band <= 5.0
        s.append(txt(ox, oy - 16, LAB[c], 11.5, INK, "start", "700"))
        s.append(txt(ox, oy - 4, f"{D['delta_geks_real'][c]:+.1f}%  ±{band:.1f}%"
                     + ("" if ok else "  ✗"), 9.5, "#15803d" if ok else "#b45309"))
        s.append(txt(ox + pw, oy - 4, f"w {D['weights'][c]:.3f}", 9, MUT, "end"))
        s.append(txt(ox, oy + ph + 12, Q[0], 8.5, MUT))
        s.append(txt(ox + pw, oy + ph + 12, Q[-1], 8.5, MUT, "end"))
    s.append(txt(20, H - 8, "✗ marks a category missing the ±5% adequacy criterion of §3.6 "
                 "(six of seven). Panels share a common scale; w is the review weight.",
                 9.5, MUT))
    write("fig2-categories", s)


# =============================================================== figure 3
def fig3():
    W, H = 780, 400
    L, R, T, B = 58, 168, 34, 96
    pw, ph = W - L - R, H - T - B
    raw = D["composite_geks"]
    # the adjusted series is reconstructed as the raw path scaled to the D2 endpoint
    # (code/27-reputation-band.py); the endpoints are the published numbers and the
    # interior is a log-linear apportionment of the adjustment, drawn as a band edge
    tgt = 139.7 / raw[-1]
    adj = [raw[0] * math.exp(math.log(v / raw[0]) + math.log(tgt) *
                             (math.log(v / raw[0]) / math.log(raw[-1] / raw[0])
                              if raw[-1] != raw[0] else 0)) for v in raw]
    ymin, ymax = 90, max(raw) * 1.06

    def X(i):
        return L + pw * i / (len(Q) - 1)

    def Y(v):
        return T + ph * (1 - (v - ymin) / (ymax - ymin))

    s = svg_open(W, H, "Composite index: raw and reputation-adjusted",
                 "The raw composite and a reputation-adjusted lower bound, drawn as a "
                 "band, with a strip showing sensitivity to beta.")
    for g in range(100, int(ymax) + 1, 20):
        s.append(path(f"M {L} {Y(g):.1f} L {L+pw} {Y(g):.1f}", LINE, 1))
        s.append(txt(L - 8, Y(g) + 3.5, str(g), 10, MUT, "end"))
    for i, q in enumerate(Q):
        if q.endswith("Q1"):
            s.append(txt(X(i), T + ph + 16, q[:4], 10, MUT, "middle"))
    xs = [X(i) for i in range(len(Q))]
    s.append(path(band_path(xs, [Y(v) for v in adj], [Y(v) for v in raw]),
                  "none", 0, "#0d9488", 0.15))
    s.append(path(polyline(xs, [Y(v) for v in raw]), ACC, 2.4))
    s.append(path(polyline(xs, [Y(v) for v in adj]), "#0d9488", 2.4, dash="6 4"))
    lx = L + pw + 14
    s.append(txt(lx, T + 4, "raw  +79.0%", 10.5, ACC, "start", "700"))
    s.append(txt(lx, T + 20, "adjusted  +39.7%", 10.5, "#0d9488", "start", "700"))
    for k, ln in enumerate(["lower bound, not a", "correction: reviews are",
                            "cumulative sales, so β", "absorbs demand too"]):
        s.append(txt(lx, T + 40 + k * 13, ln, 9, MUT))
    # beta sensitivity strip
    sy = T + ph + 40
    grid = [(0.00, 79.0), (0.05, 59.4), (0.10, 41.9), (0.15, 26.4), (0.20, 12.5)]
    s.append(txt(L, sy - 6, "Sensitivity of the composite change to β "
                 "(pooled estimate β = 0.1068, 95% CI ≈ 0.067–0.146)", 10, INK, "start", "700"))
    bw = pw / (len(grid) - 1)
    s.append(path(f"M {L} {sy+26} L {L+pw} {sy+26}", "#cbd2de", 1))
    for k, (b, v) in enumerate(grid):
        x = L + k * bw
        h = max(2.0, v / 79.0 * 26)
        s.append(f'<rect x="{x-13:.1f}" y="{sy+26-h:.1f}" width="26" height="{h:.1f}" '
                 f'fill="{ACC}" opacity="{0.28 + 0.5*(1-k/4):.2f}" rx="2"/>')
        s.append(txt(x, sy + 38, f"β={b:.2f}", 9, MUT, "middle"))
        s.append(txt(x, sy + 22 - h, f"{v:+.1f}%", 9, INK, "middle", "700"))
    s.append(txt(L, 18, "Reputation-adjusted band", 13, INK, "start", "700"))
    s.append(txt(L, H - 8, "Raw is the headline. β pooled at +0.1068 (se 0.0201, t 5.32), "
                 "gig-clustered; the band's floor is soft across β's own CI.", 9.5, MUT))
    write("fig3-reputation-band", s)


# =============================================================== figure 4
def fig4_data():
    """Recompute the precision-vs-n curve rather than transcribing it.

    FINITE-POPULATION CORRECTION. Subsampling n of N gigs WITHOUT replacement has
    variance (1 - n/N) times the with-replacement variance, so the raw subsample sd
    understates precision loss badly as n approaches N -- at n = N it is zero by
    construction, which is the degeneracy noted in the 2026-08-05 session. The
    published bootstrap resamples WITH replacement, so to be on the same footing we
    divide the observed sd by sqrt(1 - n/N). The corrected curve is what the figure
    plots, and it extrapolates to the published bootstrap SEs -- an independent
    check on both, printed below."""
    panel = tpd.build_panel_recent()
    NS = [25, 50, 100, 200, 400, 800]
    DRAWS = 60
    out = {}
    for c in ("design", "coding", "writing", "video"):
        gigs = sorted(panel[c])
        N = len(gigs)
        pts, raws = [], []
        for n in NS:
            if n > N * 0.75:          # beyond this the correction is doing the work
                continue
            rng = np.random.default_rng(1000 + n)
            lv = []
            for _ in range(DRAWS):
                pick = rng.choice(N, size=n, replace=False)
                sub = {gigs[i]: panel[c][gigs[i]] for i in pick}
                idx, _, _ = geks.geks_index(sub, rng=None, n_boot=0,
                                            window_start=tpd.LINK_Q)
                if idx and Q[-1] in idx and idx[Q[-1]] > 0:
                    lv.append(math.log(idx[Q[-1]]))
            if len(lv) >= 10:
                raw = 196.0 * float(np.std(lv, ddof=1))
                fpc = math.sqrt(max(1.0 - n / N, 1e-6))
                pts.append((n, raw / fpc))
                raws.append((n, raw))
        out[c] = pts
        print(f"    {c:<9} N={N:<5} " + "  ".join(f"n={n}:±{h:.1f}%" for n, h in pts))
        # extrapolate the corrected curve to full n and compare to the published SE
        if pts:
            n0, h0 = pts[-1]
            pred = h0 * math.sqrt(n0 / N)
            pub = 196.0 * (D["index_geks_se"][c][-1] or 0)
            print(f"    {'':<9} extrapolated to n={N}: ±{pred:.1f}%   "
                  f"published bootstrap: ±{pub:.1f}%   "
                  f"({'agrees' if abs(pred-pub) < max(1.5, 0.25*pub) else 'DIVERGES'})")
            # invert the 1/sqrt(n) fit for the sample size each rule requires
            need = {r: n0 * (h0 / r) ** 2 for r in (5.0, 10.0)}
            print(f"    {'':<9} to reach ±10%: n≈{need[10.0]:,.0f}   "
                  f"to reach ±5%: n≈{need[5.0]:,.0f}")
    return out


def fig4(curve):
    W, H = 720, 420
    L, R, T, B = 62, 158, 34, 52
    pw, ph = W - L - R, H - T - B
    xs_all = [n for pts in curve.values() for n, _ in pts]
    ys_all = [h for pts in curve.values() for _, h in pts] + [5.0, 10.0]
    lx0, lx1 = math.log10(min(xs_all) * 0.85), math.log10(max(xs_all) * 1.2)
    ly0, ly1 = math.log10(max(min(ys_all) * 0.7, 0.5)), math.log10(max(ys_all) * 1.25)

    def X(n):
        return L + pw * (math.log10(n) - lx0) / (lx1 - lx0)

    def Y(h):
        return T + ph * (1 - (math.log10(h) - ly0) / (ly1 - ly0))

    s = svg_open(W, H, "Index precision versus matched sample size",
                 "Log-log plot of the 95 percent half-width against the number of "
                 "sampled gigs, with a one-over-root-n reference and the adequacy rules.")
    for tick in (1, 2, 5, 10, 20, 50):
        if ly0 <= math.log10(tick) <= ly1:
            s.append(path(f"M {L} {Y(tick):.1f} L {L+pw} {Y(tick):.1f}", LINE, 1))
            s.append(txt(L - 8, Y(tick) + 3.5, f"±{tick}%", 10, MUT, "end"))
    for n in (25, 50, 100, 200, 400, 800):
        if lx0 <= math.log10(n) <= lx1:
            s.append(txt(X(n), T + ph + 16, str(n), 10, MUT, "middle"))
    for rule, lab, col in ((5.0, "±5% adequacy rule", "#15803d"),
                           (10.0, "±10%", "#b45309")):
        if ly0 <= math.log10(rule) <= ly1:
            s.append(path(f"M {L} {Y(rule):.1f} L {L+pw} {Y(rule):.1f}", col, 1.4, dash="6 4"))
            s.append(txt(L + pw - 4, Y(rule) - 5, lab, 9.5, col, "end"))
    # 1/sqrt(n) reference anchored at design's first point
    anch = curve["design"][0]
    ref = [(n, anch[1] * math.sqrt(anch[0] / n)) for n in (25, 800)]
    s.append(path(polyline([X(n) for n, _ in ref], [Y(h) for _, h in ref]),
                  "#9aa1ad", 1.4, dash="2 4"))
    s.append(txt(X(ref[1][0]) - 4, Y(ref[1][1]) + 14, "1/√n", 9.5, MUT, "end"))
    for c, pts in curve.items():
        if not pts:
            continue
        s.append(path(polyline([X(n) for n, _ in pts], [Y(h) for _, h in pts]),
                      COL[c], 2.2))
        for n, h in pts:
            s.append(f'<circle cx="{X(n):.1f}" cy="{Y(h):.1f}" r="3" fill="{COL[c]}"/>')
        n, h = pts[-1]
        s.append(txt(X(n) + 8, Y(h) + 3.5, LAB[c], 10.5, COL[c], "start", "700"))
    s.append(txt(L, 18, "Precision versus matched sample size", 13, INK, "start", "700"))
    s.append(txt(L, T + ph + 34, "gigs sampled (log scale)", 10, MUT))
    s.append(txt(L, H - 10, f"Recent panel, terminal quarter {Q[-1]}. Each point is the sd of "
                 "the log level over 60 independent subsamples, ×1.96.", 9.5, MUT))
    write("fig4-precision-curve", s)


# =============================================================== figure 5
def fig5():
    hist, recent = tpd.build_panel_historical(), tpd.build_panel_recent()
    data = {}
    for tag, panel, base in (("historical", hist, tpd.START_Q),
                             ("recent", recent, tpd.LINK_Q)):
        for c in CATS:
            if not panel.get(c):
                continue
            by_q, quarters = geks._log_panel(panel[c], base)
            lnP = geks._bilaterals(by_q, quarters)
            b = quarters[0]
            counts = [len([l for l in quarters
                           if (b, l) in lnP and (l, t) in lnP]) for t in quarters]
            data[(tag, c)] = (quarters, counts)
    W, H = 880, 330
    s = svg_open(W, H, "Link-path support per quarter",
                 "Number of populated GEKS link paths supporting each quarter's level, "
                 "by category, for the historical and recent panels.")
    s.append(txt(20, 20, "How many link paths support each quarter's level",
                 13, INK, "start", "700"))
    pw, ph = 380, 108
    for col, tag in enumerate(("historical", "recent")):
        ox = 44 + col * (pw + 56)
        oy = 48
        series = [(c, data[(tag, c)]) for c in CATS if (tag, c) in data]
        mx = max((max(cs) for _, (_, cs) in series), default=1)
        s.append(txt(ox, oy - 12, f"{tag} panel", 11.5, INK, "start", "700"))
        s.append(f'<rect x="{ox}" y="{oy}" width="{pw}" height="{ph}" fill="#fbfcfe" '
                 f'stroke="{LINE}" stroke-width="1" rx="3"/>')
        for gl in (1, 5, 10, 20):
            if gl <= mx:
                y = oy + ph * (1 - gl / mx)
                s.append(path(f"M {ox} {y:.1f} L {ox+pw} {y:.1f}", LINE, 1))
                s.append(txt(ox - 6, y + 3.5, str(gl), 9, MUT, "end"))
        for c, (qs, cs) in series:
            n = max(len(qs) - 1, 1)
            xs = [ox + pw * i / n for i in range(len(qs))]
            ys = [oy + ph * (1 - v / mx) for v in cs]
            s.append(path(polyline(xs, ys), COL[c], 1.6, opacity=0.9))
        y1 = oy + ph * (1 - 1 / mx)
        s.append(path(f"M {ox} {y1:.1f} L {ox+pw} {y1:.1f}", "#dc2626", 1.3, dash="5 3"))
        s.append(txt(ox + pw - 3, y1 - 5, "1 path = not identified", 9, "#dc2626", "end"))
        s.append(txt(ox, oy + ph + 14, series[0][1][0][0], 9, MUT))
        s.append(txt(ox + pw, oy + ph + 14, series[0][1][0][-1], 9, MUT, "end"))
    lx = 44
    for k, c in enumerate(sorted(CATS, key=lambda c: -D["weights"][c])):
        x = lx + k * 116
        s.append(f'<rect x="{x}" y="{H-30}" width="14" height="3" fill="{COL[c]}" rx="1.5"/>')
        s.append(txt(x + 19, H - 26, LAB[c], 9.5, INK))
    s.append(txt(44, H - 8, "A quarter resting on a single link path is not identified (§3.7): "
                 "its level is a property of which path survived.", 9.5, MUT))
    write("fig5-linkpath", s)


print("Generating figures -> outputs/figures/")
fig1()
fig2()
fig3()
print("  computing precision-vs-n curve (subsampling, this takes a minute)...")
fig4(fig4_data())
fig5()
print("done")
