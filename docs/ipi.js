// Intelligence Price Index — CSRankings-style, self-contained (no external libs).
// Data contract: see site/README.md. Composite math mirrors composite() in code/14-recent-ipi.py.

let DATA, checked, sortK = "delta", sortDir = 1;     // 1 = ascending (most deflationary first)
const open = new Set();

const PALETTE = { design:"#2563eb", coding:"#0891b2", writing:"#7c3aed",
                  marketing:"#db2777", video:"#ea580c", audio:"#16a34a",
                  translation:"#ca8a04" };
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
  checked = new Set(DATA.categories);
  document.getElementById("hRange").textContent =
    `(${DATA.months[0]} → ${DATA.months[DATA.months.length - 1]})`;
  document.getElementById("caveat").textContent =
    "Index, base month = 100. The composite basket is the main (broad) categories, ranked by " +
    "12-month price change (largest decline first). Subcategories (dashed, nested under their parent) " +
    "are shown for detail where they have both solid matched-pair coverage and real movement " +
    "(e.g. Logo & Brand within Design); they are not added to the basket since their gigs already " +
    "sit inside the parent. Thin or flat subcategories stay folded into the broad domain.";
  document.getElementById("src").innerHTML =
    `Source: Fiverr gig prices via the Wayback Machine, matched-model index. ` +
    `Composite = review-weighted geometric mean of the selected categories: ` +
    `<code>exp(Σ w·ln(index) / Σ w)</code>. Data generated ${DATA.generated}.`;
  wireControls();
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
// month-over-month moves worth calling out: anything past a threshold, plus the
// single biggest rise and biggest drop so the chart always labels its extremes.
function significantMoves(series, thresh = 0.8) {
  const moves = [];
  for (let i = 1; i < series.length; i++) {
    if (series[i] == null || series[i - 1] == null) continue;
    moves.push({ i, pct: (series[i] / series[i - 1] - 1) * 100 });
  }
  const ups = moves.filter(m => m.pct > 0), downs = moves.filter(m => m.pct < 0);
  // threshold crossings first; the single biggest rise/drop override with a stronger label
  const pick = new Map(moves.filter(m => Math.abs(m.pct) >= thresh)
    .map(m => [m.i, { ...m, why: `crossed the ±${thresh}% month-over-month threshold` }]));
  if (ups.length) { const m = ups.reduce((a, b) => b.pct > a.pct ? b : a); if (m.pct >= 0.05) pick.set(m.i, { ...m, why: "sharpest single-month rise in the window" }); }
  if (downs.length) { const m = downs.reduce((a, b) => b.pct < a.pct ? b : a); if (m.pct <= -0.05) pick.set(m.i, { ...m, why: "sharpest single-month drop in the window" }); }
  return [...pick.values()].sort((a, b) => a.i - b.i);
}
// shared y-domain across every category + composite, for comparable sparklines
function domain() {
  const all = [...DATA.categories.flatMap(c => DATA.index[c]), ...DATA.composite_all].filter(v => v != null);
  let lo = Math.min(...all), hi = Math.max(...all);
  const pad = Math.max((hi - lo) * 0.12, 0.5);
  return [lo - pad, hi + pad];
}

// ---- sparkline (tiny inline svg) ------------------------------------------
function spark(values, w = 110, h = 20, color = "#888") {
  const [lo, hi] = domain(), n = values.length;
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

// ---- main trend chart ------------------------------------------------------
function drawChart(cats, comp) {
  const box = document.getElementById("chart");
  [...box.querySelectorAll("svg")].forEach(s => s.remove());
  const tip = document.getElementById("tip");
  const W = box.clientWidth || 900, H = 420, m = { t: 16, r: 18, b: 30, l: 42 };
  const months = DATA.months, n = months.length;

  const lineOp = cats.length > 10 ? 0.32 : 0.5;   // dial back when many narrow lines overlap
  const series = cats.map(c => ({ name: labelOf(c), vals: DATA.index[c], color: colorOf(c),
                                  w: 1.3, op: lineOp, dash: isSub(c) ? "5 3" : "" }));
  if (cats.length) series.push({ name: "Composite", vals: comp, color: "#111", w: 3, op: 1 });

  const ys = series.flatMap(s => s.vals).filter(v => v != null);
  let lo = ys.length ? Math.min(...ys) : 95, hi = ys.length ? Math.max(...ys) : 105;
  const pad = Math.max((hi - lo) * 0.15, 0.8); lo -= pad; hi += pad;
  const X = i => m.l + (i / (n - 1)) * (W - m.l - m.r);
  const Y = v => m.t + (1 - (v - lo) / (hi - lo)) * (H - m.t - m.b);

  const svg = el("svg", { _svg: 1, viewBox: `0 0 ${W} ${H}`, width: W, height: H });

  // y gridlines + labels
  const ticks = niceTicks(lo, hi, 5);
  for (const t of ticks) {
    svg.appendChild(el("line", { _svg: 1, x1: m.l, x2: W - m.r, y1: Y(t), y2: Y(t),
      stroke: t === 100 ? "#cfcfcf" : "#eee", "stroke-width": 1, "stroke-dasharray": t === 100 ? "4 3" : "" }));
    svg.appendChild(el("text", { _svg: 1, x: m.l - 6, y: Y(t) + 3, "text-anchor": "end",
      "font-size": 11, fill: "#999" }, [String(t)]));
  }
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
  // composite endpoint markers + label
  if (cats.length) {
    comp.forEach((v, i) => { if (v != null) svg.appendChild(el("circle", { _svg: 1, cx: X(i), cy: Y(v), r: 2.5, fill: "#111" })); });
    const lastV = [...comp].reverse().find(v => v != null), lastI = comp.length - 1;
    if (lastV != null) svg.appendChild(el("text", { _svg: 1, x: X(lastI) - 4, y: Y(lastV) - 8,
      "text-anchor": "end", "font-size": 12, "font-weight": 700, fill: "#111" }, [lastV.toFixed(1)]));

    // highlight the sharpest month-over-month moves in the composite
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

  // hover guide
  const guide = el("line", { _svg: 1, y1: m.t, y2: H - m.b, stroke: "#bbb", "stroke-width": 1, opacity: 0 });
  svg.appendChild(guide);
  const hit = el("rect", { _svg: 1, x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: "transparent" });
  svg.appendChild(hit);
  hit.addEventListener("mousemove", ev => {
    const r = svg.getBoundingClientRect(), sx = (W) / r.width;
    const px = (ev.clientX - r.left) * sx;
    let i = Math.round((px - m.l) / ((W - m.l - m.r) / (n - 1)));
    i = Math.max(0, Math.min(n - 1, i));
    guide.setAttribute("x1", X(i)); guide.setAttribute("x2", X(i)); guide.setAttribute("opacity", 1);
    let rows = series.slice().reverse().map(s => s.vals[i] == null ? "" :
      `<div><span class="k" style="background:${s.color}"></span>${s.name}: <b>${s.vals[i].toFixed(1)}</b></div>`).join("");
    tip.innerHTML = `<b>${months[i]}</b>${rows}`;
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
  if (!cats.length) return;
  const moves = significantMoves(comp), months = DATA.months;
  if (!moves.length) {
    ul.appendChild(el("li", {}, [
      "No single month moved the composite sharply over this window — changes were gradual."]));
    return;
  }
  for (const mv of moves) {
    const up = mv.pct > 0, dir = up ? "up" : "down", verb = up ? "rose +" : "fell −";
    const li = el("li", {});
    li.appendChild(el("span", { class: "mk", style: `background:${up ? "#15803d" : "#dc2626"}` }));
    li.appendChild(el("span", { html:
      `<b>${months[mv.i - 1]} → ${months[mv.i]}</b>: composite ` +
      `<span class="${dir}">${verb}${Math.abs(mv.pct).toFixed(1)}%</span> ` +
      `month-over-month — ${mv.why}.` }));
    ul.appendChild(li);
  }
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
  tr.appendChild(el("td", { class: "num faint" }, [sub ? "" : String(rank)]));
  tr.appendChild(nameCell); tr.appendChild(sparkCell);
  tr.appendChild(el("td", { class: "num d " + cls(d) }, [fmtPct(d)]));
  // subs show their gig-share in parens — informational, not part of the basket
  tr.appendChild(el("td", { class: "num faint" }, [sub ? `(${wt})` : wt]));
  tr.appendChild(el("td", { class: "num faint" }, [DATA.panel_gigs[c] != null ? String(DATA.panel_gigs[c]) : "–"]));
  return tr;
}

function render() {
  const cats = DATA.categories.filter(c => checked.has(c));        // all checked (chart lines)
  const mainChecked = cats.filter(c => !isSub(c));                  // basket members only
  const comp = mainChecked.length ? compositeSeries(mainChecked) : DATA.months.map(() => null);

  const num = document.getElementById("hNum");
  const pc = mainChecked.length ? pctChange(comp) : null;
  num.textContent = mainChecked.length ? fmtPct(pc) : "—";
  num.className = "num " + cls(pc);

  drawChart(cats, comp);                 // every checked line; composite from main only
  renderMoveNotes(comp, mainChecked);

  const tb = document.getElementById("rows"); tb.innerHTML = "";
  const order = sortedCats().filter(c => !isSub(c));
  order.forEach((c, idx) => {
    tb.appendChild(catRow(c, idx + 1, false));

    if (open.has(c)) {
      const vals = DATA.months.map((mo, i) => {
        const v = DATA.index[c][i];
        return `${mo} ${v == null ? "–" : v.toFixed(1)}`;
      }).join("&nbsp;&nbsp;·&nbsp;&nbsp;");
      tb.appendChild(el("tr", { class: "detail" }, [
        el("td", {}), el("td", {}), el("td", {}),
        el("td", { colspan: 5, class: "vals", html: vals })]));
    }
    // nested subcategory detail lines under this domain
    subsOf(c).sort((a, b) => (DATA.delta12[a] ?? 0) - (DATA.delta12[b] ?? 0))
      .forEach(sc => tb.appendChild(catRow(sc, null, true)));
  });

  // composite footer row (main categories only — subs aren't in the basket)
  const ft = document.getElementById("foot"); ft.innerHTML = "";
  const mainCount = DATA.categories.filter(c => !isSub(c)).length;
  if (mainChecked.length) {
    const ftr = el("tr", {});
    ftr.appendChild(el("td", { colspan: 4, html: `Composite &middot; <span style="font-weight:400;color:#777">${mainChecked.length} of ${mainCount} categories</span>` }));
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
