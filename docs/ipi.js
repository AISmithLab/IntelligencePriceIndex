// Intelligence Price Index — CSRankings-style, self-contained (no external libs).
// Data contract: see site/README.md. Composite math mirrors composite() in code/14-recent-ipi.py.

let DATA, checked, sortK = "name", sortDir = 1;      // default: categories A→Z
const open = new Set();
let pinned = null;                                    // quarter index the user is inspecting (or null)
// Per-seller gig price histories live in a separate freelancers.json (a few hundred
// KB) that is fetched once, lazily, the first time any category is expanded — so the
// initial page load stays light. openSeller keys are `${cat}/${seller}` because one
// seller can appear in several category lists.
let FDATA = null, fdataPromise = null;
const openSeller = new Set();
function loadFreelancers() {
  if (fdataPromise) return fdataPromise;
  fdataPromise = fetch("freelancers.json").then(r => r.json())
    .then(d => (FDATA = d))
    .catch(() => (FDATA = {}));      // absent detail file → rankings still render
  return fdataPromise;
}

const PALETTE = { design:"#2a78d6", coding:"#008300", writing:"#4a3aa7",
                  video:"#e34948", audio:"#1baf7a", marketing:"#eda100",
                  translation:"#e87ba4" };
const SVGNS = "http://www.w3.org/2000/svg";
// data.json may carry per-category colors/labels (narrow subcategory mode);
// fall back to the flat palette + capitalized id for the broad-category build.
const colorOf = c => (DATA && DATA.colors && DATA.colors[c]) || PALETTE[c] || "#888";
const labelOf = c => (DATA && DATA.labels && DATA.labels[c]) || cap(c);
// "main" categories form the basket/composite; "sub" categories are detail lines
// nested under a parent and excluded from the composite (their gigs sit inside the parent).
const isSub    = c => !!(DATA && DATA.level && DATA.level[c] === "sub");
const parentOf = c => (DATA && DATA.parents && DATA.parents[c]) || c;
const subsOf   = c => DATA.categories.filter(x => isSub(x) && parentOf(x) === c);

const fmtPct = d => d == null ? "n/a" : Math.abs(d) < 0.05 ? "0.0%" : (d > 0 ? "+" : "−") + Math.abs(d).toFixed(1) + "%";
const cls    = d => d == null || Math.abs(d) < 0.05 ? "" : (d > 0 ? "up" : "down");
const cap     = s => s.charAt(0).toUpperCase() + s.slice(1);
const el = (t, a = {}, kids = []) => {
  const n = document.createElementNS(t === "svg" || a._svg ? SVGNS : "http://www.w3.org/1999/xhtml", t);
  for (const k in a) { if (k === "_svg") continue; if (k === "html") n.innerHTML = a[k]; else n.setAttribute(k, a[k]); }
  for (const c of [].concat(kids)) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  return n;
};

fetch("data.json").then(r => r.json()).then(data => {
  DATA = data;
  // Start on a single individual category (not the full composite). Prefer the
  // most data-rich domain (design) when present; otherwise the first category.
  const startCat = DATA.categories.includes("design") ? "design" : DATA.categories[0];
  checked = new Set([startCat]);
  document.getElementById("hRange").textContent =
    `(${DATA.months[0]} → ${DATA.months[DATA.months.length - 1]})`;
  document.getElementById("caveat").textContent =
    "Quarterly index, base " + DATA.base_period + " = 100. Categories are ranked by their price " +
    "change over the whole window. The series chains two matched-model panels — the historical " +
    "pilot (2020–2024) spliced at 2024Q3 onto the recent trailing-window crawl — so the level is " +
    "continuous through the join. Expand any category (▸) to see its top freelancers ranked by the " +
    "number of distinct gigs/services they offer, then click a freelancer to see each gig and how its " +
    "package prices (Basic/Standard/Premium) moved over time. Note the panel is a sample of archived sellers, " +
    "and the composite is design-heavy (design ≈ 71% of review weight), so it tracks design closely.";
  document.getElementById("src").innerHTML =
    `Source: Fiverr gig prices via the Wayback Machine, matched-model index (quarterly, ${DATA.base_period}=100). ` +
    `Composite = review-weighted geometric mean of the selected categories: ` +
    `<code>exp(Σ w·ln(index) / Σ w)</code>. Freelancer rankings from archived gig counts. Data generated ${DATA.generated}.`;
  wireControls();
  initInspector();
  render();
}).catch(e => {
  document.getElementById("chart").innerHTML =
    `<p style="color:#c5221f">Could not load data.json (${e}). Serve over HTTP, not file://.</p>`;
});

// ---- math ------------------------------------------------------------------
function compositeSeries(cats) {
  return DATA.months.map((_, i) => {
    let logSum = 0, wSum = 0;
    for (const c of cats) {
      const v = DATA.index[c][i], w = DATA.weights[c];
      if (v && v > 0 && w > 0) { logSum += w * Math.log(v); wSum += w; }
    }
    return wSum > 0 ? Math.exp(logSum / wSum) : null;
  });
}
const pctChange = s => {
  const a = s.find(v => v != null), b = [...s].reverse().find(v => v != null);
  return a && b ? (b / a - 1) * 100 : null;
};
// period-over-period moves worth calling out: anything past a threshold, plus the
// single biggest rise and biggest drop so the chart always labels its extremes.
// Threshold scales with cadence (quarterly steps are larger than monthly).
function significantMoves(series, thresh = 4) {
  const moves = [];
  for (let i = 1; i < series.length; i++) {
    if (series[i] == null || series[i - 1] == null) continue;
    moves.push({ i, pct: (series[i] / series[i - 1] - 1) * 100 });
  }
  const ups = moves.filter(m => m.pct > 0), downs = moves.filter(m => m.pct < 0);
  // threshold crossings first; the single biggest rise/drop override with a stronger label
  const pick = new Map(moves.filter(m => Math.abs(m.pct) >= thresh)
    .map(m => [m.i, { ...m, why: `crossed the ±${thresh}% quarter-over-quarter threshold` }]));
  const extremes = new Set();
  if (ups.length) { const m = ups.reduce((a, b) => b.pct > a.pct ? b : a); if (m.pct >= 0.05) { pick.set(m.i, { ...m, why: "sharpest single-quarter rise in the window" }); extremes.add(m.i); } }
  if (downs.length) { const m = downs.reduce((a, b) => b.pct < a.pct ? b : a); if (m.pct <= -0.05) { pick.set(m.i, { ...m, why: "sharpest single-quarter drop in the window" }); extremes.add(m.i); } }
  // over a multi-year window many quarters cross the threshold; keep only the most
  // notable so the chart/list stay readable — always retaining the two extremes.
  const MAX = 5;
  let out = [...pick.values()];
  if (out.length > MAX) {
    out = out.sort((a, b) => (extremes.has(b.i) - extremes.has(a.i)) || (Math.abs(b.pct) - Math.abs(a.pct)))
             .slice(0, MAX);
  }
  return out.sort((a, b) => a.i - b.i);
}
// ---- sparkline (tiny inline svg) ------------------------------------------
function spark(values, w = 110, h = 20, color = "#888") {
  // per-series auto-scale (levels span 100→~580 across categories, so a shared
  // domain would flatten low-movement rows); keep 100 inside the range as baseline.
  const present = values.filter(v => v != null);
  let lo = present.length ? Math.min(100, ...present) : 95;
  let hi = present.length ? Math.max(100, ...present) : 105;
  const sp = Math.max((hi - lo) * 0.12, 0.5); lo -= sp; hi += sp;
  const n = values.length;
  const x = i => (i / (n - 1)) * (w - 2) + 1;
  const y = v => h - 1 - ((v - lo) / (hi - lo)) * (h - 2);
  const svg = el("svg", { _svg: 1, width: w, height: h, class: "spark", viewBox: `0 0 ${w} ${h}` });
  // baseline at 100
  const yb = y(100);
  svg.appendChild(el("line", { _svg: 1, x1: 0, x2: w, y1: yb, y2: yb, stroke: "#e3e3e3", "stroke-width": 1 }));
  // path, breaking at nulls
  let d = "", pen = false;
  values.forEach((v, i) => { if (v == null) { pen = false; return; }
    d += `${pen ? "L" : "M"}${x(i).toFixed(1)} ${y(v).toFixed(1)} `; pen = true; });
  svg.appendChild(el("path", { _svg: 1, d, fill: "none", stroke: color, "stroke-width": 1.5 }));
  const last = values[n - 1];
  if (last != null) svg.appendChild(el("circle", { _svg: 1, cx: x(n - 1), cy: y(last), r: 2, fill: color }));
  return svg;
}

// ---- per-gig price-over-time chart (freelancer drill-down) -----------------
// The three package tiers are ORDERED (Basic < Standard < Premium), so they are
// encoded as one hue at three lightness steps — a sequential ramp, not three
// arbitrary categorical colors. Darker = higher tier = higher price.
function mixWhite(hex, amt) {                    // amt 0→base, 1→white
  const m = hex.replace("#", "");
  const r = parseInt(m.slice(0, 2), 16), g = parseInt(m.slice(2, 4), 16), b = parseInt(m.slice(4, 6), 16);
  const mix = (ch) => Math.round(ch + (255 - ch) * amt);
  return `rgb(${mix(r)},${mix(g)},${mix(b)})`;
}
const TIERS = [                                   // index into a series row [date,b,s,p]
  { i: 1, name: "Basic",    light: 0.50 },
  { i: 2, name: "Standard", light: 0.26 },
  { i: 3, name: "Premium",  light: 0.0  },
];
const fmtDate = ymd => `${ymd.slice(0, 4)}-${ymd.slice(4, 6)}`;
const dayNum = ymd => Date.UTC(+ymd.slice(0, 4), +ymd.slice(4, 6) - 1, +ymd.slice(6, 8)) / 864e5;

// Compact inline-SVG line chart for one gig. series = [[YYYYMMDD,b,s,p], ...].
function gigChart(series, baseColor, w = 340, h = 96) {
  const padL = 34, padR = 46, padT = 8, padB = 16;
  const prices = [];
  for (const row of series) for (const t of TIERS) if (row[t.i] != null) prices.push(row[t.i]);
  let lo = Math.min(...prices), hi = Math.max(...prices);
  if (!(lo < hi)) { lo = Math.max(0, lo - 1); hi = hi + 1; }            // flat series → give it height
  const pad = (hi - lo) * 0.12; lo = Math.max(0, lo - pad); hi += pad;
  const days = series.map(r => dayNum(r[0]));
  const d0 = days[0], d1 = days[days.length - 1], span = d1 - d0 || 1;
  const x = dn => padL + ((dn - d0) / span) * (w - padL - padR);
  const y = v => h - padB - ((v - lo) / (hi - lo)) * (h - padT - padB);

  const svg = el("svg", { _svg: 1, width: "100%", height: h, viewBox: `0 0 ${w} ${h}`,
    class: "gigchart", preserveAspectRatio: "xMidYMid meet" });
  // y gridlines at lo / hi with $ labels
  [lo, hi].forEach(v => {
    svg.appendChild(el("line", { _svg: 1, x1: padL, x2: w - padR, y1: y(v), y2: y(v),
      stroke: "#eceef4", "stroke-width": 1 }));
    svg.appendChild(el("text", { _svg: 1, x: padL - 5, y: y(v) + 3, "text-anchor": "end",
      class: "gcax" }, ["$" + Math.round(v)]));
  });
  // one line per tier that has data, lightest→darkest; collect end-labels for a
  // vertical de-collision pass (tiers with near-equal prices would otherwise overlap)
  const labels = [];
  TIERS.forEach(t => {
    const pts = series.filter(r => r[t.i] != null);
    if (!pts.length) return;
    const col = mixWhite(baseColor, t.light);
    if (pts.length > 1) {
      let d = "";
      pts.forEach((r, k) => { d += `${k ? "L" : "M"}${x(dayNum(r[0])).toFixed(1)} ${y(r[t.i]).toFixed(1)} `; });
      svg.appendChild(el("path", { _svg: 1, d, fill: "none", stroke: col,
        "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }));
    }
    // observation markers carry a native hover tooltip (date + all tiers)
    pts.forEach(r => {
      const c = el("circle", { _svg: 1, cx: x(dayNum(r[0])), cy: y(r[t.i]),
        r: pts.length > 1 ? 2.4 : 4, fill: col, stroke: "#fff", "stroke-width": 1 });
      const tip = [`${fmtDate(r[0])}`,
        r[1] != null ? `Basic $${r[1]}` : null,
        r[2] != null ? `Standard $${r[2]}` : null,
        r[3] != null ? `Premium $${r[3]}` : null].filter(Boolean).join("  ·  ");
      c.appendChild(el("title", { _svg: 1 }, [tip]));
      svg.appendChild(c);
    });
    const lastPt = pts[pts.length - 1];
    labels.push({ x: x(dayNum(lastPt[0])) + 5, y: y(lastPt[t.i]), col,
      text: `$${lastPt[t.i]} ${t.name[0]}` });
  });
  // de-collide the direct end-labels: keep a min vertical gap, then shift the stack
  // back inside the plot if it ran past the bottom. (All tiers share the last date,
  // so the labels form one vertical stack at the right edge.)
  const GAP = 10.5;
  labels.sort((a, b) => a.y - b.y);
  for (let k = 1; k < labels.length; k++)
    if (labels[k].y - labels[k - 1].y < GAP) labels[k].y = labels[k - 1].y + GAP;
  const overshoot = labels.length ? labels[labels.length - 1].y - (h - padB) : 0;
  if (overshoot > 0) for (const L of labels) L.y -= overshoot;
  for (const L of labels) L.y = Math.max(padT + 4, L.y);
  labels.forEach(L => svg.appendChild(el("text", { _svg: 1, x: L.x, y: L.y + 3,
    class: "gcend", fill: L.col }, [L.text])));
  // x date range
  svg.appendChild(el("text", { _svg: 1, x: padL, y: h - 3, class: "gcax" }, [fmtDate(series[0][0])]));
  svg.appendChild(el("text", { _svg: 1, x: w - padR, y: h - 3, "text-anchor": "end", class: "gcax" },
    [fmtDate(series[series.length - 1][0])]));
  return svg;
}

// ---- main trend chart ------------------------------------------------------
function drawChart(cats, comp) {
  const box = document.getElementById("chart");
  [...box.querySelectorAll("svg")].forEach(s => s.remove());
  const tip = document.getElementById("tip");
  const W = box.clientWidth || 900, H = 420, m = { t: 16, r: 18, b: 30, l: 74 };
  const months = DATA.months, n = months.length;

  // The composite is only meaningful for a basket of 2+ categories; with a single
  // category selected we show that individual series on its own (its composite would
  // just duplicate it under a heavy black line).
  const showComposite = cats.filter(c => !isSub(c)).length >= 2;
  const lineOp = cats.length > 10 ? 0.32 : (showComposite ? 0.5 : 0.95);
  const series = cats.map(c => ({ name: labelOf(c), vals: DATA.index[c], color: colorOf(c),
                                  w: showComposite ? 1.3 : 2.2, op: lineOp, dash: isSub(c) ? "5 3" : "" }));
  if (showComposite) series.push({ name: "Composite", vals: comp, color: "#111", w: 3, op: 1 });

  const ys = series.flatMap(s => s.vals).filter(v => v != null);
  let lo = ys.length ? Math.min(...ys) : 95, hi = ys.length ? Math.max(...ys) : 105;
  const pad = Math.max((hi - lo) * 0.15, 0.8); lo -= pad; hi += pad;
  const X = i => m.l + (i / (n - 1)) * (W - m.l - m.r);
  const Y = v => m.t + (1 - (v - lo) / (hi - lo)) * (H - m.t - m.b);

  const svg = el("svg", { _svg: 1, viewBox: `0 0 ${W} ${H}`, width: W, height: H });

  // y gridlines + labels — every tick carries the "pts" unit so the numeric scale
  // reads as index points at a glance (the rotated axis title spells it out in full).
  const ticks = niceTicks(lo, hi, 5);
  for (const t of ticks) {
    svg.appendChild(el("line", { _svg: 1, x1: m.l, x2: W - m.r, y1: Y(t), y2: Y(t),
      stroke: t === 100 ? "#cfcfcf" : "#eee", "stroke-width": 1, "stroke-dasharray": t === 100 ? "4 3" : "" }));
    svg.appendChild(el("text", { _svg: 1, x: m.l - 6, y: Y(t) + 3, "text-anchor": "end",
      "font-size": 11, fill: "#999" }, [String(t) + " pts"]));
  }
  // y-axis unit title: IPI is an index (base_period = 100), so label the axis units.
  const yMid = m.t + (H - m.t - m.b) / 2;
  svg.appendChild(el("text", { _svg: 1, x: 14, y: yMid, "text-anchor": "middle",
    "font-size": 11, "font-weight": 600, fill: "#6b7280",
    transform: `rotate(-90 14 ${yMid.toFixed(1)})` },
    [`IPI · index points (${DATA.base_period} = 100)`]));
  // x labels (~6)
  const step = Math.max(1, Math.round(n / 6));
  months.forEach((mo, i) => { if (i % step && i !== n - 1) return;
    svg.appendChild(el("text", { _svg: 1, x: X(i), y: H - 8, "text-anchor": "middle",
      "font-size": 11, fill: "#999" }, [mo])); });

  // series paths
  for (const s of series) {
    let d = "", pen = false;
    s.vals.forEach((v, i) => { if (v == null) { pen = false; return; }
      d += `${pen ? "L" : "M"}${X(i).toFixed(1)} ${Y(v).toFixed(1)} `; pen = true; });
    svg.appendChild(el("path", { _svg: 1, d, fill: "none", stroke: s.color,
      "stroke-width": s.w, opacity: s.op, "stroke-linejoin": "round",
      "stroke-dasharray": s.dash || "" }));
  }
  // composite endpoint markers + highlighted moves (only when a real basket is shown)
  if (showComposite) {
    comp.forEach((v, i) => { if (v != null) svg.appendChild(el("circle", { _svg: 1, cx: X(i), cy: Y(v), r: 2.5, fill: "#111" })); });

    // highlight the sharpest quarter-over-quarter moves in the composite
    for (const mv of significantMoves(comp)) {
      const up = mv.pct > 0, color = up ? "#15803d" : "#dc2626";
      const x1 = X(mv.i - 1), y1 = Y(comp[mv.i - 1]), x2 = X(mv.i), y2 = Y(comp[mv.i]);
      svg.appendChild(el("line", { _svg: 1, x1, y1, x2, y2, stroke: color,
        "stroke-width": 4.5, "stroke-linecap": "round", opacity: 0.92 }));
      svg.appendChild(el("circle", { _svg: 1, cx: x2, cy: y2, r: 3.6, fill: color }));
      svg.appendChild(el("text", { _svg: 1, x: (x1 + x2) / 2, y: (y1 + y2) / 2 + (up ? -9 : 17),
        "text-anchor": "middle", "font-size": 11, "font-weight": 700, fill: color,
        "paint-order": "stroke", stroke: "#fff", "stroke-width": 3, "stroke-linejoin": "round" },
        [(up ? "+" : "−") + Math.abs(mv.pct).toFixed(1) + "%"]));
    }
  }

  // pinned-quarter marker: a solid vertical rule + composite dot at the quarter the
  // user is inspecting, so the readout below always has a visible anchor on the chart.
  if (pinned != null && pinned >= 0 && pinned < n) {
    svg.appendChild(el("line", { _svg: 1, x1: X(pinned), x2: X(pinned), y1: m.t, y2: H - m.b,
      stroke: "#2563eb", "stroke-width": 1.4, opacity: 0.9, "stroke-dasharray": "3 3" }));
    const pv = cats.length ? comp[pinned] : null;
    if (pv != null) svg.appendChild(el("circle", { _svg: 1, cx: X(pinned), cy: Y(pv), r: 4.5,
      fill: "#fff", stroke: "#2563eb", "stroke-width": 2 }));
    svg.appendChild(el("text", { _svg: 1, x: X(pinned), y: m.t - 4, "text-anchor": "middle",
      "font-size": 11, "font-weight": 700, fill: "#2563eb" }, [months[pinned]]));
  }

  // hover guide
  const guide = el("line", { _svg: 1, y1: m.t, y2: H - m.b, stroke: "#bbb", "stroke-width": 1, opacity: 0 });
  svg.appendChild(guide);
  const hit = el("rect", { _svg: 1, x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: "transparent", style: "cursor:pointer" });
  svg.appendChild(hit);
  const idxAt = ev => {
    const r = svg.getBoundingClientRect(), sx = W / r.width;
    const px = (ev.clientX - r.left) * sx;
    let i = Math.round((px - m.l) / ((W - m.l - m.r) / (n - 1)));
    return Math.max(0, Math.min(n - 1, i));
  };
  hit.addEventListener("click", ev => { const i = idxAt(ev); pinQuarter(pinned === i ? null : i); });
  hit.addEventListener("mousemove", ev => {
    const r = svg.getBoundingClientRect(), sx = (W) / r.width;
    const px = (ev.clientX - r.left) * sx;
    let i = Math.round((px - m.l) / ((W - m.l - m.r) / (n - 1)));
    i = Math.max(0, Math.min(n - 1, i));
    guide.setAttribute("x1", X(i)); guide.setAttribute("x2", X(i)); guide.setAttribute("opacity", 1);
    let rows = series.slice().reverse().map(s => s.vals[i] == null ? "" :
      `<div><span class="k" style="background:${s.color}"></span>${s.name}: <b>${s.vals[i].toFixed(1)}</b> pts</div>`).join("");
    tip.innerHTML = `<b>${months[i]}</b> <span style="color:var(--faint);font-weight:400">· IPI (${DATA.base_period}=100)</span>${rows}`;
    tip.style.display = "block";
    const tx = X(i) / sx, left = Math.min(tx + 12, r.width - tip.offsetWidth - 6);
    tip.style.left = Math.max(0, left) + "px";
    tip.style.top = (ev.clientY - r.top + 12) + "px";
  });
  hit.addEventListener("mouseleave", () => { guide.setAttribute("opacity", 0); tip.style.display = "none"; });

  box.appendChild(svg);
}
// ---- highlighted-move descriptions (list under the chart) ------------------
function renderMoveNotes(comp, cats) {
  const ul = document.getElementById("movenotes");
  ul.innerHTML = "";
  if (cats.length < 2) return;   // move notes describe composite basket moves (2+ categories)
  const moves = significantMoves(comp), months = DATA.months;
  if (!moves.length) {
    ul.appendChild(el("li", {}, [
      "No single quarter moved the composite sharply over this window — changes were gradual."]));
    return;
  }
  for (const mv of moves) {
    const up = mv.pct > 0, dir = up ? "up" : "down", verb = up ? "rose +" : "fell −";
    const li = el("li", {});
    li.appendChild(el("span", { class: "mk", style: `background:${up ? "#15803d" : "#dc2626"}` }));
    li.appendChild(el("span", { html:
      `<b>${months[mv.i - 1]} → ${months[mv.i]}</b>: composite ` +
      `<span class="${dir}">${verb}${Math.abs(mv.pct).toFixed(1)}%</span> ` +
      `quarter-over-quarter — ${mv.why}.` }));
    ul.appendChild(li);
  }
}
// ---- quarter inspector: pick a specific quarter/year, read off the IPI change ----
function pinQuarter(i) {
  pinned = i;
  const sel = document.getElementById("qpick");
  if (sel) sel.value = i == null ? "" : String(i);
  render();
}
// Populate the quarter dropdown once (grouped by year) and wire it.
function initInspector() {
  const sel = document.getElementById("qpick");
  if (!sel) return;
  sel.innerHTML = "";
  sel.appendChild(el("option", { value: "" }, ["Inspect a quarter…"]));
  let og = null, yr = null;
  DATA.months.forEach((q, i) => {
    const y = q.slice(0, 4);
    if (y !== yr) { yr = y; og = el("optgroup", { label: y }); sel.appendChild(og); }
    og.appendChild(el("option", { value: String(i) }, [q]));
  });
  sel.onchange = () => pinQuarter(sel.value === "" ? null : +sel.value);
  document.getElementById("qclear").onclick = () => pinQuarter(null);
}
// Fill the readout with the composite level at the pinned quarter and its change
// quarter-over-quarter, year-over-year (4 quarters), and versus the window base.
function renderInspector(comp, cats = [], showComposite = false) {
  const box = document.getElementById("qreadout");
  const clr = document.getElementById("qclear");
  if (!box) return;
  if (pinned == null) { box.innerHTML = '<span class="muted">Click the chart or pick a quarter to read its IPI level per category.</span>';
    clr.style.display = "none"; return; }
  clr.style.display = "";
  const q = DATA.months[pinned];
  const unit = '<span style="font-size:11px;font-weight:400;color:var(--faint)"> pts</span>';
  // one readout chip: swatch + label above, index level (pts) below.
  const chip = (label, val, color, lvl) =>
    `<span class="qm"><span class="ql">` +
      (color ? `<span class="swatch" style="background:${color};margin-right:4px"></span>` : "") +
      `${label}</span><span class="qv ${lvl ? "lvl" : ""}">` +
      (val == null ? "—" : val.toFixed(1) + unit) + `</span></span>`;
  // Composite on top, then the selected categories in alphabetical order — each
  // showing its own index level at the clicked quarter.
  const ordered = [...cats].sort((a, b) => labelOf(a).localeCompare(labelOf(b)));
  if (!showComposite && !ordered.length) {
    box.innerHTML = `<b>${q}</b> &middot; <span class="muted">select a category to read its level at this quarter</span>`;
    return;
  }
  let html = `<span class="qm"><span class="ql">Quarter</span><span class="qv" style="color:var(--ink)">${q}</span></span>`;
  if (showComposite) html += chip("Composite", comp[pinned], "#111", true);
  ordered.forEach(c => {
    const s = DATA.index[c];
    html += chip(labelOf(c), s ? s[pinned] : null, colorOf(c), false);
  });
  box.innerHTML = html;
}
function niceTicks(lo, hi, n) {
  const span = hi - lo, raw = span / n, mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const step = [1, 2, 2.5, 5, 10].map(s => s * mag).find(s => s >= raw) || mag;
  const out = []; for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) out.push(+t.toFixed(2));
  return out;
}

// ---- table -----------------------------------------------------------------
function sortedCats() {
  const key = c => ({ name: c, delta: DATA.delta12[c] ?? 0, weight: DATA.weights[c] ?? 0,
                      gigs: DATA.panel_gigs[c] ?? 0, rank: DATA.delta12[c] ?? 0 }[sortK]);
  return [...DATA.categories].sort((a, b) => {
    const x = key(a), y = key(b);
    return (typeof x === "string" ? x.localeCompare(y) : x - y) * sortDir;
  });
}

// one table row for a category — main, or a nested subcategory detail line
function catRow(c, rank, sub) {
  const d = DATA.delta12[c], col = colorOf(c);
  const tr = el("tr", { class: sub ? "cat sub" : "cat" });
  const caret = el("td", {}, sub ? [] : [el("span", { class: "caret" }, [open.has(c) ? "▾" : "▸"])]);
  if (!sub) caret.onclick = () => { open.has(c) ? open.delete(c) : open.add(c); render(); };
  const cbCell = el("td", {});
  const cb = el("input", { type: "checkbox" }); cb.checked = checked.has(c);
  cb.onchange = () => { cb.checked ? checked.add(c) : checked.delete(c); render(); };
  cbCell.appendChild(cb);
  const nameCell = el("td", { class: "name" },
    (sub ? [el("span", { class: "sublead" }, ["↳ "])] : [])
      .concat([el("span", { class: "swatch", style: `background:${col}` }), labelOf(c)]));
  const sparkCell = el("td", {}); sparkCell.appendChild(spark(DATA.index[c], 110, 20, col));
  const wt = (DATA.weights[c] * 100).toFixed(1) + "%";
  tr.appendChild(caret); tr.appendChild(cbCell);
  tr.appendChild(nameCell); tr.appendChild(sparkCell);
  tr.appendChild(el("td", { class: "num d " + cls(d) }, [fmtPct(d)]));
  // subs show their gig-share in parens — informational, not part of the basket
  tr.appendChild(el("td", { class: "num faint" }, [sub ? `(${wt})` : wt]));
  tr.appendChild(el("td", { class: "num faint" }, [DATA.panel_gigs[c] != null ? String(DATA.panel_gigs[c]) : "–"]));
  return tr;
}

// Clean a stored gig title ("Seller: I will do X for $5 on fiverr.com") down to
// the service phrase; fall back to a prettified slug.
function gigTitle(g) {
  const m = (g.title || "").match(/I will (.+?)(?: for \$[\d,]+.*)?(?: on fiverr\.com)?\s*$/i);
  const s = m ? m[1] : g.slug.replace(/-/g, " ");
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// Drill-down panel for one seller: their gigs in category `c`, each with a
// price-over-time chart. Rendered only when FDATA (freelancers.json) has loaded.
function gigPanel(seller, c) {
  const panel = el("li", { class: "gigpanel" });
  if (!FDATA) { panel.appendChild(el("div", { class: "gigmut" }, ["Loading price histories…"])); return panel; }
  const node = FDATA[seller];
  const gigs = node ? node.gigs.filter(g => g.cat === c) : [];
  if (!gigs.length) {
    panel.appendChild(el("div", { class: "gigmut" },
      ["No archived gig prices for this seller in " + labelOf(c) + "."]));
    return panel;
  }
  // one legend for the whole panel (all charts share the tier ramp)
  const legend = el("div", { class: "giglegend" });
  legend.appendChild(el("span", { class: "glnote" }, ["Package tier:"]));
  TIERS.forEach(t => {
    const it = el("span", { class: "glitem" });
    it.appendChild(el("span", { class: "glsw", style: `background:${mixWhite(colorOf(c), t.light)}` }));
    it.appendChild(document.createTextNode(t.name));
    legend.appendChild(it);
  });
  panel.appendChild(legend);
  // richest series first so the most informative gigs read at the top
  gigs.slice().sort((a, b) => b.series.length - a.series.length).forEach(g => {
    const card = el("div", { class: "gigcard" });
    const head = el("div", { class: "gighead" });
    head.appendChild(el("a", { class: "gigtitle", href: g.url, target: "_blank",
      rel: "noopener", title: "Open the archived gig page (Wayback Machine)" }, [gigTitle(g)]));
    const n = g.series.length;
    head.appendChild(el("span", { class: "gigmeta" }, [n > 1 ? `${n} price points` : "1 snapshot"]));
    card.appendChild(head);
    card.appendChild(gigChart(g.series, colorOf(c)));
    panel.appendChild(card);
  });
  return panel;
}

// expanded detail row: top freelancers in this category, ranked by number of
// distinct priced gigs they offer (DATA.rankings). Each freelancer expands to
// their gigs + price-over-time charts (from the lazily-loaded freelancers.json).
function rankingRow(c) {
  const rk = DATA.rankings && DATA.rankings[c];
  const inner = el("div", { class: "rankbox" });
  if (!rk || !rk.top || !rk.top.length) {
    inner.appendChild(el("div", { class: "rankhead" },
      ["No freelancer ranking available for " + labelOf(c) + "."]));
    return el("tr", { class: "detail" }, [el("td", {}), el("td", {}), el("td", { colspan: 5 }, [inner])]);
  }
  loadFreelancers();      // warm the detail cache so drill-down is instant
  inner.appendChild(el("div", { class: "rankhead", html:
    `Top freelancers in <b>${labelOf(c)}</b>, ranked by distinct gigs offered ` +
    `<span class="rankmut">— ${rk.sellers.toLocaleString()} priced sellers · ` +
    `click a name to see their gigs and how prices moved</span>` }));
  const ol = el("ol", { class: "rank" });
  const max = rk.top[0].gigs;
  rk.top.forEach((s, i) => {
    const key = `${c}/${s.seller}`, isOpen = openSeller.has(key);
    const li = el("li", { class: "rankli" + (isOpen ? " open" : "") });
    li.appendChild(el("span", { class: "caret" }, [isOpen ? "▾" : "▸"]));
    li.appendChild(el("span", { class: "rk" }, [String(i + 1)]));
    li.appendChild(el("span", { class: "rs" }, [s.seller]));
    const bar = el("span", { class: "rbar" });
    bar.appendChild(el("span", { class: "rfill",
      style: `width:${Math.max(6, (s.gigs / max) * 100)}%;background:${colorOf(c)}` }));
    li.appendChild(bar);
    li.appendChild(el("span", { class: "rg" }, [s.gigs + (s.gigs === 1 ? " gig" : " gigs")]));
    li.onclick = () => {
      if (openSeller.has(key)) openSeller.delete(key); else openSeller.add(key);
      loadFreelancers().then(render);
    };
    ol.appendChild(li);
    if (isOpen) ol.appendChild(gigPanel(s.seller, c));
  });
  inner.appendChild(ol);
  return el("tr", { class: "detail" }, [
    el("td", {}), el("td", {}),
    el("td", { colspan: 5 }, [inner])]);
}

function render() {
  const cats = DATA.categories.filter(c => checked.has(c));        // all checked (chart lines)
  const mainChecked = cats.filter(c => !isSub(c));                  // basket members only
  const comp = mainChecked.length ? compositeSeries(mainChecked) : DATA.months.map(() => null);

  const pc = mainChecked.length ? pctChange(comp) : null;
  const showComposite = mainChecked.length >= 2;   // composite is a 2+ category basket

  drawChart(cats, comp);                 // every checked line; composite from main only
  renderMoveNotes(comp, mainChecked);
  renderInspector(comp, mainChecked, showComposite);
  // the highlighted-move legend only applies when composite highlights are drawn
  const note = document.getElementById("chartnote");
  if (note) note.style.display = showComposite ? "" : "none";

  const tb = document.getElementById("rows"); tb.innerHTML = "";
  const order = sortedCats().filter(c => !isSub(c));
  order.forEach((c, idx) => {
    tb.appendChild(catRow(c, idx + 1, false));

    if (open.has(c)) tb.appendChild(rankingRow(c));

    // nested subcategory detail lines under this domain
    subsOf(c).sort((a, b) => labelOf(a).localeCompare(labelOf(b)))
      .forEach(sc => tb.appendChild(catRow(sc, null, true)));
  });

  // composite footer row (main categories only — subs aren't in the basket)
  const ft = document.getElementById("foot"); ft.innerHTML = "";
  const mainCount = DATA.categories.filter(c => !isSub(c)).length;
  if (mainChecked.length) {
    const ftr = el("tr", {});
    ftr.appendChild(el("td", { colspan: 3, html: `Composite &middot; <span style="font-weight:400;color:#777">${mainChecked.length} of ${mainCount} categories</span>` }));
    const sc = el("td", {}); sc.appendChild(spark(comp, 110, 20, "#111")); ftr.appendChild(sc);
    ftr.appendChild(el("td", { class: "num d " + cls(pc) }, [fmtPct(pc)]));
    ftr.appendChild(el("td", { class: "num" }, ["100%"]));
    ftr.appendChild(el("td", { class: "num" }, [String(mainChecked.reduce((s, c) => s + (DATA.panel_gigs[c] || 0), 0))]));
    ft.appendChild(ftr);
  }

  // header sort arrows
  document.querySelectorAll("thead th[data-k]").forEach(th => {
    const k = th.getAttribute("data-k");
    th.querySelector(".arr")?.remove();
    if (k === sortK) th.appendChild(el("span", { class: "arr" }, [" " + (sortDir > 0 ? "▲" : "▼")]));
  });
}

function wireControls() {
  document.getElementById("selAll").onclick  = () => { checked = new Set(DATA.categories); render(); };
  document.getElementById("selNone").onclick = () => { checked = new Set(); render(); };
  document.querySelectorAll("thead th[data-k]").forEach(th => {
    th.onclick = () => {
      const k = th.getAttribute("data-k");
      if (k === sortK) sortDir *= -1;
      else { sortK = k; sortDir = (k === "name") ? 1 : (k === "delta" || k === "rank") ? 1 : -1; }
      render();
    };
  });
  let t; window.addEventListener("resize", () => { clearTimeout(t); t = setTimeout(render, 120); });
}
