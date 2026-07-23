// Intelligence Price Index — Gallery. Self-contained (no external libs), reuses
// the same data contract as ipi.js. For each category it renders two graphs:
//   1. the category's GEKS-Jevons price-index trend, with a 95% confidence band
//   2. a featured real gig's package-price history (from freelancers.json)
// so the reader sees both the macro index and a concrete micro example per domain.

let DATA, FDATA = null;

const PALETTE = { design:"#2a78d6", coding:"#008300", writing:"#4a3aa7",
                  video:"#e34948", audio:"#1baf7a", marketing:"#eda100",
                  translation:"#e87ba4" };
const SVGNS = "http://www.w3.org/2000/svg";
const cap = s => s.charAt(0).toUpperCase() + s.slice(1);
const colorOf = c => (DATA && DATA.colors && DATA.colors[c]) || PALETTE[c] || "#888";
const labelOf = c => (DATA && DATA.labels && DATA.labels[c]) || cap(c);
const el = (t, a = {}, kids = []) => {
  const n = document.createElementNS(t === "svg" || a._svg ? SVGNS : "http://www.w3.org/1999/xhtml", t);
  for (const k in a) { if (k === "_svg") continue; if (k === "html") n.innerHTML = a[k]; else n.setAttribute(k, a[k]); }
  for (const c of [].concat(kids)) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  return n;
};
const fmtPct = d => d == null ? "n/a" : (d > 0 ? "+" : d < 0 ? "−" : "") + Math.abs(d).toFixed(1) + "%";
const pctChange = s => {
  const a = s.find(v => v != null), b = [...s].reverse().find(v => v != null);
  return a && b ? (b / a - 1) * 100 : null;
};
function niceTicks(lo, hi, n) {
  const span = hi - lo, raw = span / n, mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const step = [1, 2, 2.5, 5, 10].map(s => s * mag).find(s => s >= raw) || mag;
  const out = []; for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) out.push(+t.toFixed(2));
  return out;
}

// ---- category index trend, with 95% confidence band -----------------------
// Prefers the drift-free GEKS-Jevons series (DATA.index_geks); band from its
// bootstrap log-scale standard error: level·exp(±1.96·se).
function drawIndexMini(cat) {
  const useGeks = DATA.index_geks && DATA.index_geks[cat];
  const vals = (useGeks ? DATA.index_geks[cat] : DATA.index[cat]) || [];
  const se   = useGeks && DATA.index_geks_se ? (DATA.index_geks_se[cat] || []) : [];
  const months = DATA.months, n = months.length, color = colorOf(cat);
  const W = 440, H = 232, m = { t: 14, r: 16, b: 26, l: 46 };

  const band = vals.map((v, i) => { const s = se[i];
    return (v == null || s == null) ? null : [v * Math.exp(-1.96 * s), v * Math.exp(1.96 * s)]; });
  const ys = vals.filter(v => v != null).concat(band.filter(Boolean).flatMap(b => b));
  let lo = ys.length ? Math.min(100, ...ys) : 95, hi = ys.length ? Math.max(100, ...ys) : 105;
  const pad = Math.max((hi - lo) * 0.14, 0.8); lo -= pad; hi += pad;
  const X = i => m.l + (i / (n - 1)) * (W - m.l - m.r);
  const Y = v => m.t + (1 - (v - lo) / (hi - lo)) * (H - m.t - m.b);

  const svg = el("svg", { _svg: 1, viewBox: `0 0 ${W} ${H}`, width: "100%", height: "auto",
    class: "gsvg", preserveAspectRatio: "xMidYMid meet" });

  for (const t of niceTicks(lo, hi, 4)) {
    svg.appendChild(el("line", { _svg: 1, x1: m.l, x2: W - m.r, y1: Y(t), y2: Y(t),
      stroke: t === 100 ? "#cfcfcf" : "#eef0f4", "stroke-width": 1,
      "stroke-dasharray": t === 100 ? "4 3" : "" }));
    svg.appendChild(el("text", { _svg: 1, x: m.l - 6, y: Y(t) + 3, "text-anchor": "end",
      "font-size": 10, fill: "#9aa1ad" }, [String(Math.round(t))]));
  }
  const step = Math.max(1, Math.round(n / 4));
  months.forEach((mo, i) => { if (i % step && i !== n - 1) return;
    svg.appendChild(el("text", { _svg: 1, x: X(i), y: H - 8, "text-anchor": "middle",
      "font-size": 10, fill: "#9aa1ad" }, [mo])); });

  // shaded 95% band (drawn under the line) — one polygon per CONTIGUOUS run of
  // estimated quarters, so the band breaks at gaps instead of bridging quarters
  // that were never measured.
  const bandRuns = [];
  band.forEach((b, i) => {
    if (!b) return;
    const cur = bandRuns[bandRuns.length - 1];
    if (cur && cur[cur.length - 1].i === i - 1) cur.push({ i, lo: b[0], hi: b[1] });
    else bandRuns.push([{ i, lo: b[0], hi: b[1] }]);
  });
  for (const run of bandRuns) {
    if (run.length < 2) continue;
    let d = run.map((p, k) => `${k ? "L" : "M"}${X(p.i).toFixed(1)} ${Y(p.hi).toFixed(1)}`).join(" ");
    for (let k = run.length - 1; k >= 0; k--) d += ` L${X(run[k].i).toFixed(1)} ${Y(run[k].lo).toFixed(1)}`;
    svg.appendChild(el("path", { _svg: 1, d: d + " Z", fill: color, opacity: 0.12, stroke: "none" }));
  }
  // the index line
  let d = "", pen = false;
  vals.forEach((v, i) => { if (v == null) { pen = false; return; }
    d += `${pen ? "L" : "M"}${X(i).toFixed(1)} ${Y(v).toFixed(1)} `; pen = true; });
  svg.appendChild(el("path", { _svg: 1, d, fill: "none", stroke: color, "stroke-width": 2.4,
    "stroke-linejoin": "round", "stroke-linecap": "round" }));
  const last = vals[n - 1];
  if (last != null) svg.appendChild(el("circle", { _svg: 1, cx: X(n - 1), cy: Y(last), r: 3, fill: color }));
  return svg;
}

// ---- featured gig: package-price history ----------------------------------
// The three package tiers are ORDERED (Basic < Standard < Premium): one hue at
// three lightness steps, darker = higher tier. Mirrors gigChart() in ipi.js.
function mixWhite(hex, amt) {
  const mm = hex.replace("#", "");
  const r = parseInt(mm.slice(0, 2), 16), g = parseInt(mm.slice(2, 4), 16), b = parseInt(mm.slice(4, 6), 16);
  const mix = ch => Math.round(ch + (255 - ch) * amt);
  return `rgb(${mix(r)},${mix(g)},${mix(b)})`;
}
const TIERS = [ { i: 1, name: "Basic", light: 0.50 }, { i: 2, name: "Standard", light: 0.26 },
                { i: 3, name: "Premium", light: 0.0 } ];
const fmtDate = ymd => `${ymd.slice(0, 4)}-${ymd.slice(4, 6)}`;
const dayNum = ymd => Date.UTC(+ymd.slice(0, 4), +ymd.slice(4, 6) - 1, +ymd.slice(6, 8)) / 864e5;

// Every gig chart shares one x scale — the index window (DATA.months), the same
// window the trend chart above it spans — instead of self-scaling to its own
// first/last snapshot. Otherwise a gig priced only in 2024 fills the panel exactly
// like one spanning 2020–2026, and no two cards can be read against each other.
// Handles quarterly ("2020Q1") and monthly ("2020-01") period labels.
const periodStart = p => {
  const q = p.match(/^(\d{4})Q([1-4])$/);
  return (q ? Date.UTC(+q[1], (+q[2] - 1) * 3, 1) : Date.UTC(+p.slice(0, 4), +p.slice(5, 7) - 1, 1)) / 864e5;
};
const periodEnd = p => {                                   // last day of the period
  const q = p.match(/^(\d{4})Q([1-4])$/);
  return (q ? Date.UTC(+q[1], +q[2] * 3, 1) : Date.UTC(+p.slice(0, 4), +p.slice(5, 7), 1)) / 864e5 - 1;
};
const xDomain = () => [periodStart(DATA.months[0]), periodEnd(DATA.months[DATA.months.length - 1])];
// Year boundaries inside the domain: with a fixed window a short gig sits in a
// small slice of the chart, so it needs reference marks to be locatable.
function yearTicks(d0, d1) {
  const out = [];
  for (let y = new Date(d0 * 864e5).getUTCFullYear(); y <= new Date(d1 * 864e5).getUTCFullYear(); y++) {
    const dn = Date.UTC(y, 0, 1) / 864e5;
    if (dn >= d0 && dn <= d1) out.push({ dn, label: "’" + String(y).slice(2) });
  }
  return out;
}

function gigChart(series, baseColor, W = 440, H = 210) {
  const padL = 40, padR = 52, padT = 10, padB = 20;
  const prices = [];
  for (const row of series) for (const t of TIERS) if (row[t.i] != null) prices.push(row[t.i]);
  let lo = Math.min(...prices), hi = Math.max(...prices);
  if (!(lo < hi)) { lo = Math.max(0, lo - 1); hi = hi + 1; }
  const pad = (hi - lo) * 0.14; lo = Math.max(0, lo - pad); hi += pad;
  const [d0, d1] = xDomain(), span = d1 - d0 || 1;
  const x = dn => padL + ((Math.min(Math.max(dn, d0), d1) - d0) / span) * (W - padL - padR);
  const y = v => H - padB - ((v - lo) / (hi - lo)) * (H - padT - padB);

  const svg = el("svg", { _svg: 1, viewBox: `0 0 ${W} ${H}`, width: "100%", height: "auto",
    class: "gsvg", preserveAspectRatio: "xMidYMid meet" });
  [lo, hi].forEach(v => {
    svg.appendChild(el("line", { _svg: 1, x1: padL, x2: W - padR, y1: y(v), y2: y(v),
      stroke: "#eef0f4", "stroke-width": 1 }));
    svg.appendChild(el("text", { _svg: 1, x: padL - 6, y: y(v) + 3, "text-anchor": "end",
      "font-size": 10, fill: "#9aa1ad" }, ["$" + Math.round(v)]));
  });
  // x gridlines + labels at year boundaries of the shared window
  for (const t of yearTicks(d0, d1)) {
    svg.appendChild(el("line", { _svg: 1, x1: x(t.dn), x2: x(t.dn), y1: padT, y2: H - padB,
      stroke: "#f1f2f6", "stroke-width": 1 }));
    svg.appendChild(el("text", { _svg: 1, x: x(t.dn), y: H - 6, "text-anchor": "middle",
      "font-size": 10, fill: "#9aa1ad" }, [t.label]));
  }
  const isGap = r => r[1] == null && r[2] == null && r[3] == null;   // coverage-gap sentinel
  const labels = [];
  TIERS.forEach(t => {
    const pts = series.filter(r => !isGap(r) && r[t.i] != null);      // real observations only
    if (!pts.length) return;
    const col = mixWhite(baseColor, t.light);
    // lift the pen across coverage gaps — never draw a line through a stretch with
    // no captures, since a straight bridge there would invent prices.
    let d = "", pen = false, drawn = 0;
    series.forEach(r => {
      if (isGap(r)) { pen = false; return; }         // no captures here -> break the line
      if (r[t.i] == null) return;                    // this tier missing at a real capture -> skip
      d += `${pen ? "L" : "M"}${x(dayNum(r[0])).toFixed(1)} ${y(r[t.i]).toFixed(1)} `;
      pen = true; drawn++;
    });
    if (drawn > 1) {
      svg.appendChild(el("path", { _svg: 1, d, fill: "none", stroke: col, "stroke-width": 2.2,
        "stroke-linejoin": "round", "stroke-linecap": "round" }));
    }
    pts.forEach(r => {
      const c = el("circle", { _svg: 1, cx: x(dayNum(r[0])), cy: y(r[t.i]),
        r: pts.length > 1 ? 2.6 : 4, fill: col, stroke: "#fff", "stroke-width": 1 });
      const tip = [fmtDate(r[0]),
        r[1] != null ? `Basic $${r[1]}` : null,
        r[2] != null ? `Standard $${r[2]}` : null,
        r[3] != null ? `Premium $${r[3]}` : null].filter(Boolean).join("  ·  ");
      c.appendChild(el("title", { _svg: 1 }, [tip]));
      svg.appendChild(c);
    });
    const lastPt = pts[pts.length - 1];
    labels.push({ x: x(dayNum(lastPt[0])) + 5, y: y(lastPt[t.i]), col, text: `$${lastPt[t.i]} ${t.name[0]}` });
  });
  const GAP = 11;
  labels.sort((a, b) => a.y - b.y);
  for (let k = 1; k < labels.length; k++)
    if (labels[k].y - labels[k - 1].y < GAP) labels[k].y = labels[k - 1].y + GAP;
  const overshoot = labels.length ? labels[labels.length - 1].y - (H - padB) : 0;
  if (overshoot > 0) for (const L of labels) L.y -= overshoot;
  for (const L of labels) L.y = Math.max(padT + 4, L.y);
  labels.forEach(L => svg.appendChild(el("text", { _svg: 1, x: L.x, y: L.y + 3,
    "font-size": 10.5, "font-weight": 600, fill: L.col }, [L.text])));
  return svg;
}

function gigTitle(g) {
  const m = (g.title || "").match(/I will (.+?)(?: for \$[\d,]+.*)?(?: on fiverr\.com)?\s*$/i);
  const s = m ? m[1] : (g.slug || "").replace(/-/g, " ");
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// Category tags in the archived gig data are noisy (the richest gig for a domain
// is sometimes cross-tagged — e.g. a music-law service under "audio"). For a
// curated highlight reel we add a soft relevance signal: a gig whose title reads
// as on-topic for its category wins over a longer but off-topic one; when nothing
// matches we fall back to pure richness. Keywords are intentionally conservative.
const CAT_KW = {
  audio:       ["voice", "voiceover", "voice over", "podcast", "audio", "sound",
                "jingle", "narrat", "dj ", "drop", "sfx", "mixing", "mastering"],
  coding:      ["code", "coding", "develop", "website", "web ", "webflow", "shopify",
                "wordpress", "python", "javascript", "bug", "api", "plugin", "software",
                "landing page", "app "],
  design:      ["logo", "design", "illustrat", "brand", "banner", "flyer", "graphic",
                "anime", "art ", " ui", " ux", "poster", "thumbnail"],
  marketing:   ["marketing", "ads", "dropship", "facebook", "social media", "campaign",
                "backlink", "promote", "seo", "tiktok", "instagram"],
  translation: ["translat", "subtitle", "localiz", "transcri", "caption", "proofread",
                "language"],
  video:       ["video", "animation", "animate", " edit", "motion", "3d", "render",
                "twitch", "overlay", "intro", "vfx"],
  writing:     ["writ", "article", "blog", "content", "copy", "ebook", " book", "resume",
                "essay", "ghostwrit", "layout", "format", "script"],
};
const relevant = (cat, title) => {
  const kw = CAT_KW[cat]; if (!kw) return 0;
  const t = (title || "").toLowerCase();
  return kw.some(k => t.includes(k)) ? 1 : 0;
};
// Pick the most illustrative gig for a category: on-topic first, then the richest
// price history (most snapshots), preferring ones whose price actually moved so
// the chart tells a story.
function featuredGig(cat) {
  if (!FDATA) return null;
  const rk = DATA.rankings && DATA.rankings[cat];
  const sellers = rk && rk.top ? rk.top.map(s => s.seller) : Object.keys(FDATA);
  let best = null, bestScore = -1;
  for (const seller of sellers) {
    const node = FDATA[seller];
    if (!node) continue;
    for (const g of node.gigs) {
      if (g.cat !== cat || !g.series || g.series.length < 2) continue;
      const prices = g.series.flatMap(r => TIERS.map(t => r[t.i]).filter(v => v != null));
      if (prices.length < 2) continue;
      const moved = Math.max(...prices) - Math.min(...prices) > 0 ? 1 : 0;
      const score = relevant(cat, g.title) * 1000 + g.series.length * 10 + moved * 5 + prices.length;
      if (score > bestScore) { bestScore = score; best = { seller, g }; }
    }
  }
  return best;
}

// ---- build the gallery -----------------------------------------------------
function buildGallery() {
  const grid = document.getElementById("grid");
  grid.innerHTML = "";
  // order categories by the size of their move over the window (most dramatic first).
  // Use the drift-free GEKS-Jevons delta (delta_geks) to match the charts below —
  // the naive chained delta (delta12) overstates thin/volatile panels via chain drift.
  const moveOf = c => Math.abs((DATA.delta_geks && DATA.delta_geks[c] != null ? DATA.delta_geks[c] : DATA.delta12[c]) ?? 0);
  const cats = [...DATA.categories].filter(c => !(DATA.level && DATA.level[c] === "sub"))
    .sort((a, b) => moveOf(b) - moveOf(a));

  for (const cat of cats) {
    const color = colorOf(cat);
    const card = el("section", { class: "gcard" });

    // header: swatch + name + Δ badge. The badge reports the drift-free
    // GEKS-Jevons change (delta_geks) so it agrees with the trend chart below;
    // the naive chained delta12 overstates thin/volatile panels (e.g. marketing).
    const d = DATA.delta_geks && DATA.delta_geks[cat] != null ? DATA.delta_geks[cat] : DATA.delta12[cat];
    const head = el("div", { class: "ghead" });
    head.appendChild(el("span", { class: "gsw", style: `background:${color}` }));
    head.appendChild(el("span", { class: "gname" }, [labelOf(cat)]));
    const badge = el("span", { class: "gbadge " + (d > 0 ? "up" : d < 0 ? "down" : "") },
      [fmtPct(d) + " ’20–’26"]);
    badge.setAttribute("title", "Change over 2020Q1→present, GEKS-Jevons (drift-free) estimate");
    head.appendChild(badge);
    card.appendChild(head);

    // graph 1: price-index trend
    const g1 = el("figure", { class: "gfig" });
    g1.appendChild(el("figcaption", { class: "gcap" },
      ["Price index · GEKS-Jevons, base " + DATA.base_period + " = 100 · shaded = 95% CI"]));
    g1.appendChild(drawIndexMini(cat));
    card.appendChild(g1);

    // graph 2: a featured real gig's package-price history
    const feat = featuredGig(cat);
    if (feat) {
      const g2 = el("figure", { class: "gfig" });
      const cap2 = el("figcaption", { class: "gcap" });
      cap2.appendChild(document.createTextNode("Featured gig · "));
      cap2.appendChild(el("a", { href: feat.g.url, target: "_blank", rel: "noopener",
        title: "Open the archived gig page (Wayback Machine)" },
        [gigTitle(feat.g)]));
      cap2.appendChild(el("span", { class: "gseller" }, [" — " + feat.seller]));
      cap2.appendChild(el("span", { class: "gseller" },
        [" · same time axis as above, " + DATA.months[0] + "–" + DATA.months[DATA.months.length - 1]]));
      g2.appendChild(cap2);
      g2.appendChild(gigChart(feat.g.series, color));
      // tier legend
      const leg = el("div", { class: "gleg" });
      TIERS.forEach(t => {
        const it = el("span", { class: "glitem" });
        it.appendChild(el("span", { class: "glsw", style: `background:${mixWhite(color, t.light)}` }));
        it.appendChild(document.createTextNode(t.name));
        leg.appendChild(it);
      });
      g2.appendChild(leg);
      card.appendChild(g2);
    }
    grid.appendChild(card);
  }
}

Promise.all([
  fetch("data.json").then(r => r.json()),
  fetch("freelancers.json").then(r => r.json()).catch(() => null),
]).then(([data, fdata]) => {
  DATA = data; FDATA = fdata;
  const gen = document.getElementById("gen");
  if (gen) gen.textContent = DATA.generated;
  buildGallery();
}).catch(e => {
  document.getElementById("grid").innerHTML =
    `<p style="color:#c5221f">Could not load data.json (${e}). Serve over HTTP, not file://.</p>`;
});
