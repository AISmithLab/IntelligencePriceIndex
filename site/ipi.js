// Intelligence Price Index — CSRankings-style, self-contained (no external libs).
// Data contract: see site/README.md. Composite math mirrors composite() in code/14-recent-ipi.py.

let DATA, checked, sortK = "delta", sortDir = 1;     // 1 = ascending (most deflationary first)
const open = new Set();

const PALETTE = { design:"#2563eb", coding:"#0891b2", writing:"#7c3aed",
                  marketing:"#db2777", video:"#ea580c", audio:"#16a34a",
                  translation:"#ca8a04" };
const SVGNS = "http://www.w3.org/2000/svg";

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
    "Index, base month = 100. Categories ranked by 12-month price change (largest decline first). " +
    "Design carries ~71% of basket weight; thin categories (audio, marketing, video) have sparse " +
    "matched-pair coverage at monthly cadence and read near-flat — quarterly figures are more robust.";
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
  const W = box.clientWidth || 900, H = 320, m = { t: 14, r: 16, b: 28, l: 38 };
  const months = DATA.months, n = months.length;

  const series = cats.map(c => ({ name: cap(c), vals: DATA.index[c], color: PALETTE[c] || "#888", w: 1.3, op: 0.5 }));
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
      "stroke-width": s.w, opacity: s.op, "stroke-linejoin": "round" }));
  }
  // composite endpoint markers + label
  if (cats.length) {
    comp.forEach((v, i) => { if (v != null) svg.appendChild(el("circle", { _svg: 1, cx: X(i), cy: Y(v), r: 2.5, fill: "#111" })); });
    const lastV = [...comp].reverse().find(v => v != null), lastI = comp.length - 1;
    if (lastV != null) svg.appendChild(el("text", { _svg: 1, x: X(lastI) - 4, y: Y(lastV) - 8,
      "text-anchor": "end", "font-size": 12, "font-weight": 700, fill: "#111" }, [lastV.toFixed(1)]));
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

function render() {
  const cats = DATA.categories.filter(c => checked.has(c));
  const comp = cats.length ? compositeSeries(cats) : DATA.months.map(() => null);

  const num = document.getElementById("hNum");
  const pc = cats.length ? pctChange(comp) : null;
  num.textContent = cats.length ? fmtPct(pc) : "—";
  num.className = "num " + cls(pc);

  drawChart(cats, comp);

  const tb = document.getElementById("rows"); tb.innerHTML = "";
  const order = sortedCats();
  order.forEach((c, idx) => {
    const d = DATA.delta12[c], col = PALETTE[c] || "#888";
    const tr = el("tr", { class: "cat" });
    const caret = el("td", {}, [el("span", { class: "caret" }, [open.has(c) ? "▾" : "▸"])]);
    caret.onclick = () => { open.has(c) ? open.delete(c) : open.add(c); render(); };
    const cbCell = el("td", {});
    const cb = el("input", { type: "checkbox" }); cb.checked = checked.has(c);
    cb.onchange = () => { cb.checked ? checked.add(c) : checked.delete(c); render(); };
    cbCell.appendChild(cb);
    const nameCell = el("td", { class: "name" }, [
      el("span", { class: "swatch", style: `background:${col}` }), cap(c)]);
    const sparkCell = el("td", {}); sparkCell.appendChild(spark(DATA.index[c], 110, 20, col));
    tr.appendChild(caret); tr.appendChild(cbCell);
    tr.appendChild(el("td", { class: "num faint" }, [String(idx + 1)]));
    tr.appendChild(nameCell); tr.appendChild(sparkCell);
    tr.appendChild(el("td", { class: "num d " + cls(d) }, [fmtPct(d)]));
    tr.appendChild(el("td", { class: "num faint" }, [(DATA.weights[c] * 100).toFixed(1) + "%"]));
    tr.appendChild(el("td", { class: "num faint" }, [DATA.panel_gigs[c] != null ? String(DATA.panel_gigs[c]) : "–"]));
    tb.appendChild(tr);

    if (open.has(c)) {
      const vals = DATA.months.map((mo, i) => {
        const v = DATA.index[c][i];
        return `${mo} ${v == null ? "–" : v.toFixed(1)}`;
      }).join("&nbsp;&nbsp;·&nbsp;&nbsp;");
      tb.appendChild(el("tr", { class: "detail" }, [
        el("td", {}), el("td", {}), el("td", {}),
        el("td", { colspan: 5, class: "vals", html: vals })]));
    }
  });

  // composite footer row
  const ft = document.getElementById("foot"); ft.innerHTML = "";
  if (cats.length) {
    const ftr = el("tr", {});
    ftr.appendChild(el("td", { colspan: 4, html: `Composite &middot; <span style="font-weight:400;color:#777">${cats.length} of ${DATA.categories.length} categories</span>` }));
    const sc = el("td", {}); sc.appendChild(spark(comp, 110, 20, "#111")); ftr.appendChild(sc);
    ftr.appendChild(el("td", { class: "num d " + cls(pc) }, [fmtPct(pc)]));
    ftr.appendChild(el("td", { class: "num" }, ["100%"]));
    ftr.appendChild(el("td", { class: "num" }, [String(DATA.categories.filter(c => checked.has(c)).reduce((s, c) => s + (DATA.panel_gigs[c] || 0), 0))]));
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
