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
    "Quarterly GEKS-Jevons index, base " + DATA.base_period + " = 100. Categories can be sorted by their " +
    "price change over the whole window, but that ordering is provisional: six of the seven categories miss " +
    "the ±5% precision standard at the latest quarter (see the ±95% column), and the intervals of the top " +
    "three overlap one another entirely, so which is highest is not determined by these data. " +
    "The series joins two matched-model panels — the historical " +
    "pilot (2020–2024) spliced at 2024Q3 onto the recent trailing-window crawl — so the level is " +
    "continuous through the join. Expand any category (▸) to see its top freelancers ranked by the " +
    "number of distinct gigs/services they offer, then click a freelancer to see each gig and how its " +
    "package prices (Basic/Standard/Premium) moved over time. Note the panel is a sample of archived sellers, " +
    "and the composite is design-heavy (design ≈ 71% of review weight), so it tracks design closely.";
  document.getElementById("src").innerHTML =
    `Source: Fiverr gig prices via the Wayback Machine, matched-model GEKS-Jevons index (quarterly, ${DATA.base_period}=100). ` +
    `Composite = review-weighted geometric mean of the selected categories: ` +
    `<code>exp(Σ w·ln(index) / Σ w)</code>. Real series deflated by CPI-U, US city average, all items, ` +
    `seasonally adjusted (BLS, via FRED <code>CPIAUCSL</code>); no CPI-U was published for October 2025, ` +
    `so the 2025Q4 deflator interpolates that month from its neighbours. ` +
    `Freelancer rankings from archived gig counts. Data generated ${DATA.generated}.`;
  wireControls();
  initInspector();
  setBasis(hasReal() ? basis : "nominal");   // sets the toggle state + note, then renders
}).catch(e => {
  document.getElementById("chart").innerHTML =
    `<p style="color:#c5221f">Could not load data.json (${e}). Serve over HTTP, not file://.</p>`;
});

// ---- math ------------------------------------------------------------------
// Everything on this page reads the drift-free GEKS-Jevons series — DATA.index_geks
// (nominal) or DATA.index_geks_real (CPI-U-deflated), routed through idxSrc() below.
// DATA.index — the naive chained-Jevons series — is retained in data.json for the
// paper's method comparison but is NOT plotted: chaining credits a sparsely-sampled
// gig's multi-quarter price change to the single quarter it reappears, on top of the
// growth already chained in from densely-sampled gigs, so the same increase is counted
// more than once. Over 2020Q1–2026Q1 that inflates the composite to 317.7 pts against
// 144.7 for GEKS. See faq.html Step 5.
// ---- price basis: real (CPI-U-deflated) vs nominal --------------------------
// Real is the DEFAULT view. The index is quoted in dollars and the dollar lost
// ~27% of its value over 2020Q1-2026Q1, so the nominal series answers "how many
// dollars does this gig cost" while the real series answers "how much of a
// basket of goods does this gig cost" -- the latter is the one that speaks to
// whether intelligence work actually got more expensive. Both are published;
// nominal additionally draws CPI-U alongside so the gap is visible directly.
// Falls back to nominal if data.json predates the real block (2026-07-30).
let basis = "real";
const hasReal   = () => !!(DATA && DATA.index_geks_real);
const idxSrc    = () => (basis === "real" && hasReal()) ? DATA.index_geks_real : DATA.index_geks;
const deltaSrc  = () => (basis === "real" && DATA.delta_geks_real) ? DATA.delta_geks_real : DATA.delta_geks;
const isReal    = () => basis === "real" && hasReal();
const basisWord = () => isReal() ? "real" : "nominal";

// ---- precision --------------------------------------------------------------
// Sample-adequacy standard (plans/todo.md, adopted 2026-08-05): a category index
// should be within ±5% at 95% confidence at the terminal quarter. At 2026Q1 SIX of
// the seven categories miss it — translation ±29.2%, coding ±17.1%, audio ±13.9%,
// video ±11.9%, writing ±8.3%, marketing ±7.7% — and only design (±4.8%) clears it.
// Suppressing the failures would leave one category, so the site instead publishes
// the half-width beside every level and marks the ones that miss the standard.
// Half-width is reported as 1.96·se on the log scale (the convention the project
// records precision in); the exact asymmetric interval is in the cell's tooltip.
const PRECISION_RULE = 5;                        // ±% at 95% on the terminal quarter
const seriesOf   = c => (idxSrc()[c] || []);
const lastPresent = arr => { for (let i = arr.length - 1; i >= 0; i--) if (arr[i] != null) return i; return -1; };
const seAtOf = (c, i) => (DATA.index_geks_se && (DATA.index_geks_se[c] || [])[i]) ?? null;
// terminal-quarter log-scale SE for one category
function seTerminal(c) {
  const i = lastPresent(seriesOf(c));
  return i < 0 ? null : seAtOf(c, i);
}
// ...and for the composite of a basket, weighted exactly as the composite itself is
function seTerminalComposite(cats) {
  if (!DATA.index_geks_se || !cats.length) return null;
  const comp = compositeSeries(cats);
  const i = lastPresent(comp);
  if (i < 0) return null;
  let num = 0, wsum = 0;
  for (const c of cats) {
    const v = seriesOf(c)[i], w = DATA.weights[c], se = seAtOf(c, i);
    if (v > 0 && w > 0 && se != null) { num += (w * se) ** 2; wsum += w; }
  }
  return wsum > 0 ? Math.sqrt(num) / wsum : null;
}
const halfWidth  = se => se == null ? null : 196 * se;          // ±% at 95%, log scale
const meetsRule  = se => se != null && halfWidth(se) <= PRECISION_RULE;
const fmtHalf    = se => se == null ? "–" : "±" + halfWidth(se).toFixed(1) + "%";
// exact (asymmetric) interval on the full-window change, for the tooltip
function deltaCiText(se, level) {
  if (se == null || level == null) return "";
  const lo = (level * Math.exp(-1.96 * se) / 100 - 1) * 100;
  const hi = (level * Math.exp(1.96 * se) / 100 - 1) * 100;
  return `95% CI on the change: ${lo >= 0 ? "+" : "−"}${Math.abs(lo).toFixed(1)}% to ` +
         `${hi >= 0 ? "+" : "−"}${Math.abs(hi).toFixed(1)}%`;
}

function compositeSeries(cats, src = idxSrc()) {
  return DATA.months.map((_, i) => {
    let logSum = 0, wSum = 0;
    for (const c of cats) {
      const v = src[c] ? src[c][i] : null, w = DATA.weights[c];
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

// Every gig chart shares one x scale — the index window (DATA.months) — instead of
// self-scaling to its own first/last snapshot. Otherwise a seller priced only in
// 2024 fills the panel exactly like one spanning 2020–2026, and no two sellers'
// charts can be read against each other. Handles quarterly ("2020Q1") and monthly
// ("2020-01") period labels.
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

// Compact inline-SVG line chart for one gig. series = [[YYYYMMDD,b,s,p], ...].
function gigChart(series, baseColor, w = 340, h = 96) {
  const padL = 34, padR = 46, padT = 8, padB = 16;
  const prices = [];
  for (const row of series) for (const t of TIERS) if (row[t.i] != null) prices.push(row[t.i]);
  let lo = Math.min(...prices), hi = Math.max(...prices);
  if (!(lo < hi)) { lo = Math.max(0, lo - 1); hi = hi + 1; }            // flat series → give it height
  const pad = (hi - lo) * 0.12; lo = Math.max(0, lo - pad); hi += pad;
  const [d0, d1] = xDomain(), span = d1 - d0 || 1;
  const x = dn => padL + ((Math.min(Math.max(dn, d0), d1) - d0) / span) * (w - padL - padR);
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
  // x gridlines + labels at year boundaries of the shared window
  for (const t of yearTicks(d0, d1)) {
    svg.appendChild(el("line", { _svg: 1, x1: x(t.dn), x2: x(t.dn), y1: padT, y2: h - padB,
      stroke: "#f1f2f6", "stroke-width": 1 }));
    svg.appendChild(el("text", { _svg: 1, x: x(t.dn), y: h - 3, "text-anchor": "middle",
      class: "gcax" }, [t.label]));
  }
  // one line per tier that has data, lightest→darkest; collect end-labels for a
  // vertical de-collision pass (tiers with near-equal prices would otherwise overlap)
  const isGap = r => r[1] == null && r[2] == null && r[3] == null;   // coverage-gap sentinel
  const labels = [];
  TIERS.forEach(t => {
    const pts = series.filter(r => !isGap(r) && r[t.i] != null);      // real observations only
    if (!pts.length) return;
    const col = mixWhite(baseColor, t.light);
    // one path, lifting the pen across coverage gaps so we never draw a line through
    // a stretch with no captures — a straight bridge there would invent prices.
    let d = "", pen = false, drawn = 0;
    series.forEach(r => {
      if (isGap(r)) { pen = false; return; }         // no captures here -> break the line
      if (r[t.i] == null) return;                    // this tier missing at a real capture -> skip
      d += `${pen ? "L" : "M"}${x(dayNum(r[0])).toFixed(1)} ${y(r[t.i]).toFixed(1)} `;
      pen = true; drawn++;
    });
    if (drawn > 1) {
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
  return svg;
}

// ---- main trend chart (GEKS-Jevons) ----------------------------------------
function drawChart(cats, comp) {
  const box = document.getElementById("chart");
  [...box.querySelectorAll("svg")].forEach(s => s.remove());
  const tip = document.getElementById("tip");
  const W = box.clientWidth || 900, H = 420, m = { t: 16, r: 18, b: 30, l: 74 };
  const months = DATA.months, n = months.length;

  // The composite is only meaningful for a basket of 2+ categories; with a single
  // category selected we show that individual series on its own (its composite would
  // just duplicate it under a heavy black line).
  const mains = cats.filter(c => !isSub(c));
  const showComposite = mains.length >= 2;
  const lineOp = cats.length > 10 ? 0.32 : (showComposite ? 0.5 : 0.95);
  const SRC = idxSrc();
  const series = cats.map(c => ({ name: labelOf(c), vals: SRC[c] || [], color: colorOf(c),
                                  w: showComposite ? 1.3 : 2.2, op: lineOp, dash: isSub(c) ? "5 3" : "" }));
  if (showComposite) series.push({ name: "Composite", vals: comp, color: "#111", w: 3, op: 1 });
  // In the nominal view, draw CPI-U alongside so the reader can see directly how
  // much of the climb is the general price level. In the real view CPI-U is flat
  // at 100 by construction, so plotting it would be noise.
  const showCpi = !isReal() && Array.isArray(DATA.cpi);
  if (showCpi) series.push({ name: "CPI-U (US consumer prices)", vals: DATA.cpi,
                             color: "#8a90a0", w: 2, op: 0.95, dash: "6 4" });

  // 95% confidence bands. EVERY published level carries one — the composite (when a
  // 2+ category basket is selected) and each selected category — because six of the
  // seven categories miss the ±5% terminal-quarter precision standard, so drawing a
  // bare line for any of them would show it as more certain than it is. se is the
  // bootstrap standard error on the log scale; band = level·exp(±1.96·se).
  // The deflator is a per-quarter constant with no sampling error, so the bootstrap
  // SEs are the same on the real and nominal series -- only the level they scale
  // changes (see code/23-real-index.py).
  const emph = showComposite ? comp : (mains.length ? (SRC[mains[0]] || []) : []);
  const compositeSeAt = i => {                  // composite SE from weighted category SEs
    if (!DATA.index_geks_se) return null;
    let num = 0, wsum = 0;
    for (const c of mains) {
      const v = (SRC[c] || [])[i], w = DATA.weights[c], se = (DATA.index_geks_se[c] || [])[i];
      if (v > 0 && w > 0 && se != null) { num += (w * se) ** 2; wsum += w; }
    }
    return wsum > 0 ? Math.sqrt(num) / wsum : null;
  };
  const bandOf = (vals, seAt) => vals.map((v, i) => { const se = seAt(i);
    return (v == null || se == null) ? null : [v * Math.exp(-1.96 * se), v * Math.exp(1.96 * se)]; });

  const bandSpecs = [];
  if (showComposite) bandSpecs.push({ band: bandOf(comp, compositeSeAt), color: "#111", op: 0.13 });
  for (const c of mains) {
    bandSpecs.push({ band: bandOf(SRC[c] || [], i => seAtOf(c, i)),
                     color: colorOf(c), op: showComposite ? 0.07 : 0.11 });
  }

  const ys = series.flatMap(s => s.vals).filter(v => v != null)
    .concat(bandSpecs.flatMap(b => b.band.filter(Boolean).flatMap(p => p)));   // bands inside the frame
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
    [`IPI · index points (${DATA.base_period} = 100, ${basisWord()})`]));
  // x labels (~6)
  const step = Math.max(1, Math.round(n / 6));
  months.forEach((mo, i) => { if (i % step && i !== n - 1) return;
    svg.appendChild(el("text", { _svg: 1, x: X(i), y: H - 8, "text-anchor": "middle",
      "font-size": 11, fill: "#999" }, [mo])); });

  // shaded 95% confidence bands (drawn first, lines on top). One polygon per
  // CONTIGUOUS run of estimated quarters, so a band breaks at gaps exactly where its
  // line does rather than bridging quarters we never estimated.
  for (const spec of bandSpecs) {
    const runs = [];
    spec.band.forEach((b, i) => {
      if (!b) return;
      const cur = runs[runs.length - 1];
      if (cur && cur[cur.length - 1].i === i - 1) cur.push({ i, lo: b[0], hi: b[1] });
      else runs.push([{ i, lo: b[0], hi: b[1] }]);
    });
    for (const run of runs) {
      if (run.length < 2) continue;             // a lone point has no area to shade
      let d = run.map((p, k) => `${k ? "L" : "M"}${X(p.i).toFixed(1)} ${Y(p.hi).toFixed(1)}`).join(" ");
      for (let k = run.length - 1; k >= 0; k--) d += ` L${X(run[k].i).toFixed(1)} ${Y(run[k].lo).toFixed(1)}`;
      svg.appendChild(el("path", { _svg: 1, d: d + " Z", fill: spec.color, opacity: spec.op, stroke: "none" }));
    }
  }

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
    const flag = (DATA.cpi_imputed && DATA.cpi_imputed[i])
      ? ` <span style="color:var(--faint);font-weight:400">· deflator interpolated</span>` : "";
    tip.innerHTML = `<b>${months[i]}</b> <span style="color:var(--faint);font-weight:400">· GEKS-Jevons, ${basisWord()} (${DATA.base_period}=100)</span>${flag}${rows}`;
    tip.style.display = "block";
    const tx = X(i) / sx, left = Math.min(tx + 12, r.width - tip.offsetWidth - 6);
    tip.style.left = Math.max(0, left) + "px";
    tip.style.top = (ev.clientY - r.top + 12) + "px";
  });
  hit.addEventListener("mouseleave", () => { guide.setAttribute("opacity", 0); tip.style.display = "none"; });

  box.appendChild(svg);

  // headline delta for whatever basket is selected (composite, or the lone category)
  const dl = document.getElementById("geksDelta");
  if (dl) {
    const d = pctChange(emph);
    dl.textContent = d == null ? "—" : (d > 0 ? "+" : "") + d.toFixed(1) + "%";
    dl.className = d == null ? "" : (d < 0 ? "down" : "up");
  }
}

// ---- volume, with no price index in it -------------------------------------
// The point of this chart is what is ABSENT from it. Every other quantity on the
// page is a quotient of dollars and a price; these two are counted directly.
// Different cadences (accrual quarterly, buyers annual) on ONE axis, which is
// legitimate only because both are indexed to the same 2020 base -- never two
// y-scales. The buyers series is drawn with open markers so its annual grain is
// visible rather than implied.
const VOL_ACCRUAL = "#4f46e5", VOL_BUYERS = "#b45309";   // validated pair, dE 31.7 protan

function drawVolume() {
  const box = document.getElementById("volchart");
  const CT = DATA && DATA.category_transactions, TX = DATA && DATA.transactions;
  if (!box) return;
  if (!CT || !CT.pooled || !TX) { const c = box.closest("section"); if (c) c.style.display = "none"; return; }
  [...box.querySelectorAll("svg")].forEach(s => s.remove());
  const tip = document.getElementById("voltip");

  // shared x domain in quarter-index space, so an annual point lands in the right
  // place among the quarters rather than at an arbitrary tick
  const qn = q => parseInt(q.slice(0, 4), 10) * 4 + (parseInt(q.slice(5), 10) - 1);
  const qs = CT.quarters, acc = CT.pooled;
  const yrNum = y => parseInt(y, 10);
  const byrs = TX.years, bidx = TX.buyers_index;
  // an annual figure describes the whole year: place it at the year's midpoint
  const bx = byrs.map(y => yrNum(y) * 4 + 1.5);
  const x0 = Math.min(qn(qs[0]), bx[0]), x1 = Math.max(qn(qs[qs.length - 1]), bx[bx.length - 1]);

  const W = box.clientWidth || 900, narrow = W < 620;
  const H = narrow ? 300 : 360, m = { t: 16, r: narrow ? 16 : 132, b: 34, l: 48 };
  const vals = acc.filter(v => v != null).concat(bidx);
  let lo = Math.min(...vals), hi = Math.max(...vals);
  const pad = Math.max((hi - lo) * .14, 2); lo -= pad; hi += pad;
  const X = v => m.l + ((v - x0) / (x1 - x0)) * (W - m.l - m.r);
  const Y = v => m.t + (1 - (v - lo) / (hi - lo)) * (H - m.t - m.b);

  const svg = el("svg", { _svg: 1, viewBox: `0 0 ${W} ${H}`, width: W, height: H });
  for (const tk of niceTicks(lo, hi, 5)) {
    svg.appendChild(el("line", { _svg: 1, x1: m.l, x2: W - m.r, y1: Y(tk), y2: Y(tk),
      stroke: tk === 100 ? "#cfcfcf" : "#eee", "stroke-width": 1,
      "stroke-dasharray": tk === 100 ? "4 3" : "" }));
    svg.appendChild(el("text", { _svg: 1, x: m.l - 6, y: Y(tk) + 3.5, "text-anchor": "end",
      "font-size": 11, fill: "#999" }, [String(tk)]));
  }
  const yMid = m.t + (H - m.t - m.b) / 2;
  svg.appendChild(el("text", { _svg: 1, x: 13, y: yMid, "text-anchor": "middle",
    "font-size": 11, "font-weight": 600, fill: "#6b7280",
    transform: `rotate(-90 13 ${yMid.toFixed(1)})` }, ["index (2020 = 100)"]));
  for (let y = Math.ceil(x0 / 4); y <= Math.floor(x1 / 4); y++)
    svg.appendChild(el("text", { _svg: 1, x: X(y * 4), y: H - 8, "text-anchor": "middle",
      "font-size": 11, fill: "#999" }, [String(y)]));

  // the thin early panel, shaded not dropped
  const thinTo = qs.indexOf(CT.thin_until);
  if (thinTo > 0) svg.appendChild(el("rect", { _svg: 1, x: X(qn(qs[0])), y: m.t,
    width: Math.max(0, X(qn(qs[thinTo])) - X(qn(qs[0]))), height: H - m.t - m.b,
    fill: "#1c2230", opacity: .05 }));
  [["2021Q3", "#6b7280", "step down"], ["2022Q4", "#c026d3", "ChatGPT"]].forEach(([q, c, lab]) => {
    const x = X(qn(q));
    svg.appendChild(el("line", { _svg: 1, x1: x, x2: x, y1: m.t, y2: H - m.b,
      stroke: c, "stroke-width": 1.1, "stroke-dasharray": "3 3" }));
    svg.appendChild(el("text", { _svg: 1, x: x + 5, y: m.t + 12, "font-size": 10, fill: c }, [lab]));
  });

  const keep = acc.map((v, i) => [i, v]).filter(p => p[1] != null);
  svg.appendChild(el("path", { _svg: 1, fill: "none", stroke: VOL_ACCRUAL, "stroke-width": 2.6,
    "stroke-linejoin": "round", "stroke-linecap": "round",
    d: keep.map((p, k) => `${k ? "L" : "M"}${X(qn(qs[p[0]])).toFixed(1)} ${Y(p[1]).toFixed(1)}`).join(" ") }));
  svg.appendChild(el("path", { _svg: 1, fill: "none", stroke: VOL_BUYERS, "stroke-width": 2.2,
    "stroke-linejoin": "round", "stroke-linecap": "round",
    d: bidx.map((v, i) => `${i ? "L" : "M"}${X(bx[i]).toFixed(1)} ${Y(v).toFixed(1)}`).join(" ") }));
  bidx.forEach((v, i) => svg.appendChild(el("circle", { _svg: 1, cx: X(bx[i]), cy: Y(v),
    r: 4.2, fill: "#fff", stroke: VOL_BUYERS, "stroke-width": 2.2 })));

  // peak searched only outside the thin stretch, and by index rather than by
  // value, so a repeated level cannot resolve to the wrong quarter
  let pk = -1;
  for (let i = thinTo + 1; i < acc.length; i++)
    if (acc[i] != null && (pk < 0 || acc[i] > acc[pk])) pk = i;
  if (pk > thinTo) {
    svg.appendChild(el("circle", { _svg: 1, cx: X(qn(qs[pk])), cy: Y(acc[pk]), r: 7.5,
      fill: "none", stroke: VOL_ACCRUAL, "stroke-width": 1.3, opacity: .55 }));
    svg.appendChild(el("text", { _svg: 1, x: X(qn(qs[pk])), y: Y(acc[pk]) - 14,
      "text-anchor": "middle", "font-size": 10, "font-weight": 700, fill: VOL_ACCRUAL },
      [`accrual peak ${qs[pk]} · ${acc[pk].toFixed(0)}`]));
  }
  // The 2022Q1-2023Q3 plateau ends in a RALLY, not a slide, and leaving it
  // unmarked made the stretch look flatter than it is -- 2023Q3 is the busiest
  // quarter since 2021Q4. It is a local high inside a decline, labelled as one.
  let lh = -1;
  for (let i = 0; i < qs.length; i++)
    if (qs[i] >= "2022Q1" && qs[i] <= "2023Q3" && acc[i] != null &&
        (lh < 0 || acc[i] > acc[lh])) lh = i;
  if (lh >= 0) {
    svg.appendChild(el("circle", { _svg: 1, cx: X(qn(qs[lh])), cy: Y(acc[lh]), r: 6,
      fill: "none", stroke: VOL_ACCRUAL, "stroke-width": 1.2, opacity: .45,
      "stroke-dasharray": "2 2" }));
    svg.appendChild(el("text", { _svg: 1, x: X(qn(qs[lh])), y: Y(acc[lh]) - 12,
      "text-anchor": "middle", "font-size": 9.5, fill: VOL_ACCRUAL, opacity: .85 },
      [`local high ${qs[lh]} · ${acc[lh].toFixed(0)}`]));
  }
  // active buyers peaks in a DIFFERENT year from accrual, which is the whole
  // reason an unqualified "peak" label was wrong here
  let bp = 0;
  bidx.forEach((v, i) => { if (v > bidx[bp]) bp = i; });
  svg.appendChild(el("text", { _svg: 1, x: X(bx[bp]), y: Y(bidx[bp]) - 12,
    "text-anchor": "middle", "font-size": 9.5, "font-weight": 700, fill: VOL_BUYERS },
    [`buyers peak ${byrs[bp]}`]));
  if (!narrow) {
    const lastA = keep[keep.length - 1];
    [[Y(lastA[1]), X(qn(qs[lastA[0]])), VOL_ACCRUAL, "Review accrual", lastA[1], qs[lastA[0]]],
     [Y(bidx[bidx.length - 1]), X(bx[bx.length - 1]), VOL_BUYERS, "Active buyers",
      bidx[bidx.length - 1], byrs[byrs.length - 1]]].forEach(([y, , c, lab, v, when]) => {
      svg.appendChild(el("text", { _svg: 1, x: W - m.r + 10, y: y - 2, "font-size": 12.5,
        "font-weight": 700, fill: c }, [v.toFixed(0)]));
      svg.appendChild(el("text", { _svg: 1, x: W - m.r + 10, y: y + 12, "font-size": 10,
        fill: "#6b7280" }, [`${lab} · ${when}`]));
    });
  }

  const guide = el("line", { _svg: 1, x1: 0, x2: 0, y1: m.t, y2: H - m.b,
    stroke: "#bbb", "stroke-width": 1, opacity: 0 });
  svg.appendChild(guide);
  const hit = el("rect", { _svg: 1, x: m.l, y: m.t, width: Math.max(1, W - m.l - m.r),
    height: H - m.t - m.b, fill: "transparent" });
  hit.addEventListener("mousemove", ev => {
    const r = svg.getBoundingClientRect(), sx = W / r.width;
    const xv = x0 + (((ev.clientX - r.left) * sx) - m.l) / (W - m.l - m.r) * (x1 - x0);
    let i = 0, best = Infinity;
    qs.forEach((q, k) => { const dd = Math.abs(qn(q) - xv); if (dd < best) { best = dd; i = k; } });
    let bi = 0, bb = Infinity;
    bx.forEach((v, k) => { const dd = Math.abs(v - xv); if (dd < bb) { bb = dd; bi = k; } });
    guide.setAttribute("x1", X(qn(qs[i]))); guide.setAttribute("x2", X(qn(qs[i])));
    guide.setAttribute("opacity", 1);
    tip.innerHTML = `<b>${qs[i]}</b>`
      + `<div><span class="k" style="background:${VOL_ACCRUAL}"></span>Review accrual: `
      + `<b>${acc[i] == null ? "–" : acc[i].toFixed(1)}</b></div>`
      + `<div><span class="k" style="background:${VOL_BUYERS}"></span>Active buyers `
      + `<span style="color:var(--faint)">(${byrs[bi]})</span>: <b>${TX.buyers_m[bi].toFixed(2)}M</b>`
      + ` · index ${bidx[bi].toFixed(1)}</div>`
      + (i <= thinTo ? `<div style="color:var(--down)">thin panel — read as noise</div>` : "");
    tip.style.display = "block";
    const left = Math.min(X(qn(qs[i])) / sx + 12, r.width - tip.offsetWidth - 6);
    tip.style.left = Math.max(0, left) + "px";
    tip.style.top = (ev.clientY - r.top + 12) + "px";
  });
  hit.addEventListener("mouseleave", () => { guide.setAttribute("opacity", 0); tip.style.display = "none"; });
  svg.appendChild(hit);
  box.appendChild(svg);

  const lg = document.getElementById("vollegend");
  if (lg) lg.innerHTML =
    `<span class="lead"><span class="sw" style="background:${VOL_ACCRUAL}"></span>Review accrual · quarterly · archive</span>`
    + `<span><span class="sw" style="background:${VOL_BUYERS}"></span>Active buyers · annual · Fiverr Inc.</span>`;
  const tb = document.getElementById("volrows");
  if (tb) {
    tb.innerHTML = "";
    const rows = Math.max(qs.length, byrs.length);
    for (let i = 0; i < rows; i++) {
      const tr = el("tr", i <= thinTo ? { style: "opacity:.55" } : {});
      tr.appendChild(el("td", {}, [qs[i] ? qs[i] + (i <= thinTo ? " ·thin" : "") : ""]));
      tr.appendChild(el("td", { class: "hl" }, [acc[i] == null ? "" : acc[i].toFixed(1)]));
      tr.appendChild(el("td", {}, [byrs[i] || ""]));
      tr.appendChild(el("td", {}, [byrs[i] ? TX.buyers_m[i].toFixed(2) : ""]));
      tr.appendChild(el("td", {}, [byrs[i] ? bidx[i].toFixed(1) : ""]));
      tb.appendChild(tr);
    }
  }
  const nt = document.getElementById("volnote");
  if (nt) nt.innerHTML =
    `<span>No price index is used anywhere on this card. Review accrual is the equal-weighted `
    + `mean of the seven category indices (age-adjusted, within-gig); active buyers is as reported. `
    + `Accrual ends 2024Q4; buyers runs to the twelve months ending 2026Q2.</span>`;
}

// ---- transactions: the implied order count ---------------------------------
// The only transaction-count series the project has. Fiverr Inc. reports GMV
// (dollars) and never an order count; orders = GMV / price, and the IPI is the
// price. Orders, real GMV and real price are all indexed to the same base year,
// so they share ONE axis -- and they have to be drawn together, because the
// finding is that the quotient falls while the numerator does not.
//
// Series colours are the three-hue set validated for colour-vision deficiency
// (worst adjacent pair dE 20.0, all six checks pass on this surface); identity is
// carried by a legend and end-of-line labels as well as by hue, never hue alone.
const TX_COLORS = { orders: "#4f46e5", gmv_real: "#0891b2", price_real: "#b45309" };
const TX_SERIES = [
  { key: "gmv_real",   name: "Real GMV",       w: 2,   lead: false },
  { key: "price_real", name: "Real IPI price", w: 2,   lead: false },
  { key: "orders",     name: "Implied orders", w: 3.2, lead: true  },
];

function drawTransactions() {
  const box = document.getElementById("txchart");
  const TX = DATA && DATA.transactions;
  if (!box) return;
  if (!TX) {                                  // older data.json: hide the whole card
    const card = box.closest("section");
    if (card) card.style.display = "none";
    return;
  }
  [...box.querySelectorAll("svg")].forEach(s => s.remove());
  const tip = document.getElementById("txtip");
  const W = box.clientWidth || 900, H = 340, m = { t: 16, r: 118, b: 30, l: 62 };
  const yrs = TX.years, n = yrs.length;
  const series = TX_SERIES.map(s => ({ ...s, vals: TX[s.key], color: TX_COLORS[s.key] }));

  const all = series.flatMap(s => s.vals).filter(v => v != null);
  let lo = Math.min(...all), hi = Math.max(...all);
  const pad = Math.max((hi - lo) * 0.16, 1); lo -= pad; hi += pad;
  const X = i => m.l + (i / (n - 1)) * (W - m.l - m.r);
  const Y = v => m.t + (1 - (v - lo) / (hi - lo)) * (H - m.t - m.b);

  const svg = el("svg", { _svg: 1, viewBox: `0 0 ${W} ${H}`, width: W, height: H });

  for (const tk of niceTicks(lo, hi, 5)) {
    svg.appendChild(el("line", { _svg: 1, x1: m.l, x2: W - m.r, y1: Y(tk), y2: Y(tk),
      stroke: tk === 100 ? "#cfcfcf" : "#eee", "stroke-width": 1,
      "stroke-dasharray": tk === 100 ? "4 3" : "" }));
    svg.appendChild(el("text", { _svg: 1, x: m.l - 6, y: Y(tk) + 3, "text-anchor": "end",
      "font-size": 11, fill: "#999" }, [String(tk)]));
  }
  const yMid = m.t + (H - m.t - m.b) / 2;
  svg.appendChild(el("text", { _svg: 1, x: 13, y: yMid, "text-anchor": "middle",
    "font-size": 11, "font-weight": 600, fill: "#6b7280",
    transform: `rotate(-90 13 ${yMid.toFixed(1)})` },
    [`index (${TX.base_year} = 100)`]));
  yrs.forEach((y, i) => svg.appendChild(el("text", { _svg: 1, x: X(i), y: H - 8,
    "text-anchor": "middle", "font-size": 11, fill: "#999" }, [y])));

  // the event marker: a date, not a result. Placed where it falls inside its year.
  if (TX.event) {
    const ei = yrs.findIndex(y => parseInt(y, 10) === TX.event.year);
    if (ei >= 0 && ei < n - 1) {
      const ex = X(ei) + TX.event.frac * (X(ei + 1) - X(ei));
      svg.appendChild(el("line", { _svg: 1, x1: ex, x2: ex, y1: m.t, y2: H - m.b,
        stroke: "#c026d3", "stroke-width": 1.2, "stroke-dasharray": "3 3" }));
      svg.appendChild(el("text", { _svg: 1, x: ex + 5, y: m.t + 12, "font-size": 10,
        fill: "#c026d3" }, [TX.event.label]));
    }
  }

  for (const s of series) {
    const d = s.vals.map((v, i) => `${i ? "L" : "M"}${X(i).toFixed(1)} ${Y(v).toFixed(1)}`).join(" ");
    svg.appendChild(el("path", { _svg: 1, d, fill: "none", stroke: s.color,
      "stroke-width": s.w, "stroke-linejoin": "round", "stroke-linecap": "round" }));
    s.vals.forEach((v, i) => svg.appendChild(el("circle", { _svg: 1, cx: X(i), cy: Y(v),
      r: s.lead ? 4.2 : 3.4, fill: s.color, stroke: "#fff", "stroke-width": 2 })));
    // end-of-line label, so no series depends on colour alone to be identified
    svg.appendChild(el("text", { _svg: 1, x: W - m.r + 9, y: Y(s.vals[n - 1]) - 2,
      "font-size": 12, "font-weight": 700, fill: s.color }, [s.vals[n - 1].toFixed(0)]));
    svg.appendChild(el("text", { _svg: 1, x: W - m.r + 9, y: Y(s.vals[n - 1]) + 12,
      "font-size": 10, fill: "#6b7280" },
      [`${s.name} ${(s.vals[n - 1] - 100 >= 0 ? "+" : "−")}${Math.abs(s.vals[n - 1] - 100).toFixed(0)}%`]));
  }

  // the peak matters more than the base-year comparison: the decline is measured
  // from 2021, not from 2020, and quoting only "vs 2020" understates it.
  const ord = TX.orders;
  const pk = ord.indexOf(Math.max(...ord));
  if (pk > 0) {
    svg.appendChild(el("circle", { _svg: 1, cx: X(pk), cy: Y(ord[pk]), r: 7.5,
      fill: "none", stroke: TX_COLORS.orders, "stroke-width": 1.3, opacity: 0.55 }));
    svg.appendChild(el("text", { _svg: 1, x: X(pk), y: Y(ord[pk]) - 14, "text-anchor": "middle",
      "font-size": 10, "font-weight": 700, fill: TX_COLORS.orders },
      [`orders peak ${yrs[pk]} · ${ord[pk].toFixed(0)}`]));
    // real GMV peaks in a different year from orders. Marking only the orders peak
  // invited "but GMV peaked in 2023" -- which is true of the NOMINAL series and
  // is exactly the confusion this label removes.
  const gm = TX.gmv_real, gp = gm.indexOf(Math.max(...gm));
  svg.appendChild(el("text", { _svg: 1, x: X(gp), y: Y(gm[gp]) - 12,
    "text-anchor": "middle", "font-size": 9.5, "font-weight": 700, fill: TX_COLORS.gmv_real },
    [`real GMV peak ${yrs[gp]}`]));
  svg.appendChild(el("text", { _svg: 1, x: X(n - 1) - 6, y: Y(ord[n - 1]) + 24,
      "text-anchor": "end", "font-size": 10, "font-weight": 700, fill: TX_COLORS.orders },
      [`−${(100 * (1 - ord[n - 1] / ord[pk])).toFixed(0)}% from peak`]));
  }

  const guide = el("line", { _svg: 1, x1: 0, x2: 0, y1: m.t, y2: H - m.b,
    stroke: "#bbb", "stroke-width": 1, opacity: 0 });
  svg.appendChild(guide);
  const hit = el("rect", { _svg: 1, x: m.l, y: m.t, width: Math.max(1, W - m.l - m.r),
    height: H - m.t - m.b, fill: "transparent" });
  svg.appendChild(hit);
  hit.addEventListener("mousemove", ev => {
    const r = svg.getBoundingClientRect(), sx = W / r.width;
    const px = (ev.clientX - r.left) * sx;
    let i = Math.round((px - m.l) / ((W - m.l - m.r) / (n - 1)));
    i = Math.max(0, Math.min(n - 1, i));
    guide.setAttribute("x1", X(i)); guide.setAttribute("x2", X(i)); guide.setAttribute("opacity", 1);
    const rows = series.slice().reverse().map(s =>
      `<div><span class="k" style="background:${s.color}"></span>${s.name}: <b>${s.vals[i].toFixed(1)}</b></div>`).join("");
    tip.innerHTML = `<b>${yrs[i]}</b> <span style="color:var(--faint);font-weight:400">· ${TX.base_year}=100 · ${TX.buyers_m[i].toFixed(2)}M buyers · $${TX.spend_per_buyer[i]}/buyer</span>${rows}`;
    tip.style.display = "block";
    const tx = X(i) / sx, left = Math.min(tx + 12, r.width - tip.offsetWidth - 6);
    tip.style.left = Math.max(0, left) + "px";
    tip.style.top = (ev.clientY - r.top + 12) + "px";
  });
  hit.addEventListener("mouseleave", () => { guide.setAttribute("opacity", 0); tip.style.display = "none"; });
  box.appendChild(svg);

  // legend (always present for 2+ series) and the table view of the same numbers
  const lg = document.getElementById("txlegend");
  if (lg) {
    lg.innerHTML = "";
    series.slice().reverse().forEach(s => lg.appendChild(el("span", { class: s.lead ? "lead" : "",
      html: `<span class="sw" style="background:${s.color}"></span>${s.name}` })));
  }
  const tb = document.getElementById("txrows");
  if (tb) {
    tb.innerHTML = "";
    yrs.forEach((y, i) => {
      const tr = el("tr", pk === i ? { class: "peak" } : {});
      tr.appendChild(el("td", {}, [y]));
      tr.appendChild(el("td", {}, [TX.buyers_m[i].toFixed(2)]));
      tr.appendChild(el("td", {}, ["$" + TX.spend_per_buyer[i]]));
      tr.appendChild(el("td", {}, [TX.gmv_usd_m[i].toFixed(0)]));
      tr.appendChild(el("td", {}, [TX.gmv_real[i].toFixed(1)]));
      tr.appendChild(el("td", {}, [TX.price_real[i].toFixed(1)]));
      tr.appendChild(el("td", { class: "hl" }, [TX.orders[i].toFixed(1)]));
      tb.appendChild(tr);
    });
  }
  const nt = document.getElementById("txnote");
  if (nt) nt.textContent = TX.note;
}

// ---- transactions by category: small multiples -----------------------------
// SEVEN OVERLAID LINES WOULD BE THE WRONG CHART HERE, and not for taste. The
// site's seven category colours cannot be told apart pairwise under colour-vision
// deficiency (worst pair dE 6.1 deutan) and one pair is below the normal-vision
// floor too (dE 13.2), so identity carried by hue alone would fail for some
// readers on some pairs. Faceting removes the problem at its source: one series
// per panel, named by its own title, with hue reduced to decoration. It also
// suits the finding, which is that the seven move TOGETHER and separate only at
// the very end -- a ghost of the all-category mean sits behind every panel so
// that "together" and "apart" are both readable at a glance.
function drawCategoryTx() {
  const box = document.getElementById("ctxchart");
  const CT = DATA && DATA.category_transactions;
  if (!box) return;
  if (!CT) { const card = box.closest("section"); if (card) card.style.display = "none"; return; }
  [...box.querySelectorAll("svg")].forEach(s => s.remove());
  const tip = document.getElementById("ctxtip");

  const cats = Object.keys(CT.index).sort((a, b) => labelOf(a).localeCompare(labelOf(b)));
  const qs = CT.quarters, n = qs.length;
  const W = box.clientWidth || 900;
  const cols = W < 560 ? 1 : (W < 820 ? 2 : 3);
  const rows = Math.ceil(cats.length / cols);
  const gapX = 16, gapY = 34, padL = 34, padT = 20, padB = 26;
  const pw = (W - padL - gapX * (cols - 1)) / cols, ph = 104;
  const H = padT + rows * (ph + gapY) + padB;

  // one shared scale across every panel, or the panels cannot be compared
  const all = cats.flatMap(c => CT.index[c]).filter(v => v != null);
  let lo = Math.min(...all), hi = Math.max(...all);
  const pad = Math.max((hi - lo) * 0.12, 2); lo -= pad; hi += pad;

  // the all-category mean, drawn behind each panel as a reference ghost
  const ghost = qs.map((_, i) => {
    const v = cats.map(c => CT.index[c][i]).filter(x => x != null);
    return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null;
  });
  const qIdx = q => qs.indexOf(q);
  const thinTo = qIdx(CT.thin_until);
  const evI = CT.event ? qIdx(CT.event.quarter) : -1;
  const stI = CT.step ? qIdx(CT.step.quarter) : -1;

  const svg = el("svg", { _svg: 1, viewBox: `0 0 ${W} ${H}`, width: W, height: H });
  const line = (xs, ys, color, w, op, dash) => el("path", { _svg: 1,
    d: xs.map((x, k) => `${k ? "L" : "M"}${x.toFixed(1)} ${ys[k].toFixed(1)}`).join(" "),
    fill: "none", stroke: color, "stroke-width": w, opacity: op,
    "stroke-linejoin": "round", "stroke-linecap": "round",
    ...(dash ? { "stroke-dasharray": dash } : {}) });

  cats.forEach((c, k) => {
    const ox = padL + (k % cols) * (pw + gapX);
    const oy = padT + Math.floor(k / cols) * (ph + gapY);
    const X = i => ox + (i / (n - 1)) * pw;
    const Y = v => oy + (1 - (v - lo) / (hi - lo)) * ph;
    const col = colorOf(c);

    svg.appendChild(el("rect", { _svg: 1, x: ox, y: oy, width: pw, height: ph,
      fill: "#fbfcfe", stroke: "#eef0f5", "stroke-width": 1, rx: 3 }));
    // the thin early panel, marked rather than dropped
    if (thinTo > 0) svg.appendChild(el("rect", { _svg: 1, x: ox, y: oy,
      width: Math.max(0, X(thinTo) - ox), height: ph, fill: "#1c2230", opacity: 0.045 }));
    // 100 = the 2020 base
    svg.appendChild(el("line", { _svg: 1, x1: ox, x2: ox + pw, y1: Y(100), y2: Y(100),
      stroke: "#cfcfcf", "stroke-width": 1, "stroke-dasharray": "4 3" }));
    if (stI >= 0) svg.appendChild(el("line", { _svg: 1, x1: X(stI), x2: X(stI),
      y1: oy, y2: oy + ph, stroke: "#6b7280", "stroke-width": 1, "stroke-dasharray": "2 3", opacity: .55 }));
    if (evI >= 0) svg.appendChild(el("line", { _svg: 1, x1: X(evI), x2: X(evI),
      y1: oy, y2: oy + ph, stroke: "#c026d3", "stroke-width": 1.1, "stroke-dasharray": "3 3" }));

    const idx = CT.index[c];
    const keep = idx.map((v, i) => [i, v]).filter(([, v]) => v != null);
    svg.appendChild(line(keep.map(([i]) => X(i)), keep.map(([i]) => Y(ghost[i])),
      "#9aa1ad", 1.6, 0.42, "4 3"));
    svg.appendChild(line(keep.map(([i]) => X(i)), keep.map(([, v]) => Y(v)), col, 2, 1));

    const pk = qIdx(CT.peak[c]);
    if (pk >= 0 && idx[pk] != null) svg.appendChild(el("circle", { _svg: 1,
      cx: X(pk), cy: Y(idx[pk]), r: 3.6, fill: col, stroke: "#fff", "stroke-width": 1.6 }));

    svg.appendChild(el("text", { _svg: 1, x: ox, y: oy - 6, "font-size": 11.5,
      "font-weight": 700, fill: "#1c2230" }, [labelOf(c)]));
    const last = keep.length ? keep[keep.length - 1][1] : null;
    if (last != null) svg.appendChild(el("text", { _svg: 1, x: ox + pw, y: oy - 6,
      "text-anchor": "end", "font-size": 11, "font-weight": 700, fill: col },
      [`${last.toFixed(0)} · peak ${CT.peak[c]}`]));

    // y labels only on the leftmost column, to keep the grid uncluttered
    if (k % cols === 0) [40, 80, 120].forEach(tk => {
      if (tk < lo || tk > hi) return;
      svg.appendChild(el("text", { _svg: 1, x: ox - 6, y: Y(tk) + 3.5,
        "text-anchor": "end", "font-size": 9.5, fill: "#9aa1ad" }, [String(tk)]));
    });
    // x labels only on the bottom row
    if (Math.floor(k / cols) === rows - 1 || k >= cats.length - cols) {
      [0, Math.floor((n - 1) / 2), n - 1].forEach(i =>
        svg.appendChild(el("text", { _svg: 1, x: X(i), y: oy + ph + 14,
          "text-anchor": i === 0 ? "start" : (i === n - 1 ? "end" : "middle"),
          "font-size": 9.5, fill: "#9aa1ad" }, [qs[i]])));
    }

    const hit = el("rect", { _svg: 1, x: ox, y: oy, width: pw, height: ph, fill: "transparent" });
    hit.addEventListener("mousemove", ev => {
      const r = svg.getBoundingClientRect(), sx = W / r.width;
      let i = Math.round((((ev.clientX - r.left) * sx) - ox) / (pw / (n - 1)));
      i = Math.max(0, Math.min(n - 1, i));
      const v = idx[i], rw = CT.raw[c][i];
      tip.innerHTML = `<b>${labelOf(c)} · ${qs[i]}</b>`
        + `<div><span class="k" style="background:${col}"></span>index: <b>${v == null ? "–" : v.toFixed(1)}</b>`
        + `<span style="color:var(--faint)"> (2020=100)</span></div>`
        + `<div style="color:var(--mut)">${rw == null ? "" : rw.toFixed(1) + " reviews/gig/qtr raw · "}`
        + `${(CT.n[c][i] || 0).toLocaleString()} obs`
        + `${CT.mean_dq[i] ? " · span " + CT.mean_dq[i].toFixed(2) + "q" : ""}</div>`
        + (i <= thinTo ? `<div style="color:var(--down)">thin panel — read as noise</div>` : "");
      tip.style.display = "block";
      const left = Math.min(X(i) / sx + 12, r.width - tip.offsetWidth - 6);
      tip.style.left = Math.max(0, left) + "px";
      tip.style.top = (ev.clientY - r.top + 12) + "px";
    });
    hit.addEventListener("mouseleave", () => { tip.style.display = "none"; });
    svg.appendChild(hit);
  });
  box.appendChild(svg);

  // table view: the relief the contrast WARN obligates, and the only place the
  // full series is legible number by number
  const th = document.getElementById("ctxhead"), tb = document.getElementById("ctxrows");
  if (th && tb) {
    th.innerHTML = ""; tb.innerHTML = "";
    th.appendChild(el("th", { scope: "col" }, ["Quarter"]));
    cats.forEach(c => th.appendChild(el("th", { scope: "col" }, [labelOf(c)])));
    qs.forEach((q, i) => {
      const tr = el("tr", i <= thinTo ? { style: "opacity:.55" } : {});
      tr.appendChild(el("td", {}, [q + (i <= thinTo ? " ·thin" : "")]));
      cats.forEach(c => {
        const v = CT.index[c][i];
        tr.appendChild(el("td", { class: CT.peak[c] === q ? "hl" : "" },
                            [v == null ? "–" : v.toFixed(1)]));
      });
      tb.appendChild(tr);
    });
  }
  const nt = document.getElementById("ctxnote");
  if (nt) nt.innerHTML = `<span>${CT.note}</span>`
    + `<span><span class="dash" style="border-top-color:#9aa1ad"></span>all-category mean</span>`
    + `<span><span class="dot" style="background:#c026d3"></span>ChatGPT 2022Q4</span>`
    + `<span><span class="dot" style="background:#6b7280"></span>common step down 2021Q3</span>`;
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
// Populate a quarter dropdown (grouped by year) and wire its onchange.
function fillQuarterPicker(id, onpick) {
  const sel = document.getElementById(id);
  if (!sel) return;
  sel.innerHTML = "";
  sel.appendChild(el("option", { value: "" }, ["Inspect a quarter…"]));
  let og = null, yr = null;
  DATA.months.forEach((q, i) => {
    const y = q.slice(0, 4);
    if (y !== yr) { yr = y; og = el("optgroup", { label: y }); sel.appendChild(og); }
    og.appendChild(el("option", { value: String(i) }, [q]));
  });
  sel.onchange = () => onpick(sel.value === "" ? null : +sel.value);
}
function initInspector() {
  fillQuarterPicker("qpick", pinQuarter);
  const c1 = document.getElementById("qclear"); if (c1) c1.onclick = () => pinQuarter(null);
}
// Fill a readout with the composite level first, then all 7 categories in
// alphabetical order, each at the pinned quarter, on the GEKS-Jevons series.
function renderInspectorInto(boxId, clrId, pinnedVal, indexSrc) {
  const box = document.getElementById(boxId);
  const clr = document.getElementById(clrId);
  if (!box) return;
  if (pinnedVal == null) { box.innerHTML = '<span class="muted">Click the chart or pick a quarter to read the composite and category levels.</span>';
    if (clr) clr.style.display = "none"; return; }
  if (clr) clr.style.display = "";
  const unit = '<span style="font-size:11px;font-weight:400;color:var(--faint)"> pts</span>';
  // one readout chip: swatch + label above, index level (pts) below.
  const chip = (label, val, color, lvl) =>
    `<span class="qm"><span class="ql">` +
      (color ? `<span class="swatch" style="background:${color};margin-right:4px"></span>` : "") +
      `${label}</span><span class="qv ${lvl ? "lvl" : ""}">` +
      (val == null ? "—" : val.toFixed(1) + unit) + `</span></span>`;
  const mains = DATA.categories.filter(c => !isSub(c)).sort((a, b) => labelOf(a).localeCompare(labelOf(b)));
  const comp = compositeSeries(mains, indexSrc);   // composite of all categories
  let html = chip("Composite", comp[pinnedVal], "#111", true);
  mains.forEach(c => {
    const s = indexSrc[c];
    html += chip(labelOf(c), s ? s[pinnedVal] : null, colorOf(c), false);
  });
  box.innerHTML = html;
}
function renderInspector()   { renderInspectorInto("qreadout",  "qclear",  pinned,   idxSrc()); }
function niceTicks(lo, hi, n) {
  const span = hi - lo, raw = span / n, mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const step = [1, 2, 2.5, 5, 10].map(s => s * mag).find(s => s >= raw) || mag;
  const out = []; for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) out.push(+t.toFixed(2));
  return out;
}

// ---- table -----------------------------------------------------------------
// Δ column reads delta_geks (or delta_geks_real in the real view), matching the
// chart. delta12 (naive chained) is not shown anywhere on the site — see the note
// on compositeSeries.
const deltaOf = c => { const d = deltaSrc(); return (d && d[c] != null) ? d[c] : null; };

function sortedCats() {
  const key = c => ({ name: c, delta: deltaOf(c) ?? 0, weight: DATA.weights[c] ?? 0,
                      gigs: DATA.panel_gigs[c] ?? 0, rank: deltaOf(c) ?? 0,
                      prec: seTerminal(c) ?? 0 }[sortK]);
  return [...DATA.categories].sort((a, b) => {
    const x = key(a), y = key(b);
    return (typeof x === "string" ? x.localeCompare(y) : x - y) * sortDir;
  });
}

// one table row for a category — main, or a nested subcategory detail line
function catRow(c, rank, sub) {
  const d = deltaOf(c), col = colorOf(c);
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
  const sparkCell = el("td", {}); sparkCell.appendChild(spark(idxSrc()[c] || [], 110, 20, col));
  const wt = (DATA.weights[c] * 100).toFixed(1) + "%";
  tr.appendChild(caret); tr.appendChild(cbCell);
  tr.appendChild(nameCell); tr.appendChild(sparkCell);
  tr.appendChild(el("td", { class: "num d " + cls(d) }, [fmtPct(d)]));
  // precision on the terminal-quarter level: published beside every change figure so
  // the Δ column can't be read as a clean ranking when the intervals overlap.
  const se = seTerminal(c), lvl = seriesOf(c)[lastPresent(seriesOf(c))];
  const pcell = el("td", { class: "num prec" + (se != null && !meetsRule(se) ? " imprecise" : "") },
                   [fmtHalf(se)]);
  if (se != null) {
    pcell.setAttribute("title",
      `${labelOf(c)}: ${deltaCiText(se, lvl)}. ` +
      (meetsRule(se) ? `Meets the ±${PRECISION_RULE}% precision standard.`
                     : `MISSES the ±${PRECISION_RULE}% precision standard — treat the level as a range, not a point.`));
  }
  tr.appendChild(pcell);
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
  // all charts in the panel — and in every other seller's panel — share one time
  // axis, so a line covering part of the width means the gig was priced only then
  legend.appendChild(el("span", { class: "glnote" },
    [`· shared time axis ${DATA.months[0]}–${DATA.months[DATA.months.length - 1]}`]));
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
    return el("tr", { class: "detail" }, [el("td", {}), el("td", {}), el("td", { colspan: 6 }, [inner])]);
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
    el("td", { colspan: 6 }, [inner])]);
}

function render() {
  const cats = DATA.categories.filter(c => checked.has(c));        // all checked (chart lines)
  const mainChecked = cats.filter(c => !isSub(c));                  // basket members only
  const comp = mainChecked.length ? compositeSeries(mainChecked) : DATA.months.map(() => null);

  const pc = mainChecked.length ? pctChange(comp) : null;
  const showComposite = mainChecked.length >= 2;   // composite is a 2+ category basket

  drawChart(cats, comp);                 // every checked line; composite from main only
  drawVolume();                          // the price-free view, drawn first
  drawTransactions();                    // independent of the category selection
  drawCategoryTx();                      // small multiples, also selection-independent
  renderMoveNotes(comp, mainChecked);
  renderInspector();
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
    const cse = seTerminalComposite(mainChecked);
    const cft = el("td", { class: "num prec" + (cse != null && !meetsRule(cse) ? " imprecise" : "") },
                   [fmtHalf(cse)]);
    if (cse != null) cft.setAttribute("title",
      `Composite: ${deltaCiText(cse, [...comp].reverse().find(v => v != null))}.`);
    ftr.appendChild(cft);
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

function setBasis(b) {
  basis = b;
  const rb = document.getElementById("basisReal"), nb = document.getElementById("basisNominal");
  if (rb) rb.classList.toggle("on", b === "real");
  if (nb) nb.classList.toggle("on", b !== "real");
  const note = document.getElementById("basisNote");
  if (note) {
    const cpiPct = Array.isArray(DATA.cpi)
      ? [...DATA.cpi].reverse().find(v => v != null) : null;
    const cpiTxt = cpiPct != null ? `${(cpiPct - 100) >= 0 ? "+" : "−"}${Math.abs(cpiPct - 100).toFixed(1)}%` : "n/a";
    note.innerHTML = b === "real"
      ? `Deflated by <b>CPI-U</b> &mdash; constant ${DATA.base_period} dollars. US consumer prices rose <b>${cpiTxt}</b> over this window.`
      : `Undeflated <b>dollar prices</b>. The dashed grey line is <b>CPI-U</b> (${cpiTxt} over the window) &mdash; the gap between it and the index is the real change.`;
  }
  render();
}

function wireControls() {
  const rb = document.getElementById("basisReal"), nb = document.getElementById("basisNominal");
  if (rb && nb) {
    if (!hasReal()) {                     // older data.json: hide the toggle entirely
      rb.parentElement.style.display = "none";
    } else {
      rb.onclick = () => setBasis("real");
      nb.onclick = () => setBasis("nominal");
    }
  }
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
