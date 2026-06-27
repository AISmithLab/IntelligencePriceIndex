// Intelligence Price Index — CSRankings-style live recompute.
// The composite over a checked subset of categories is the review-weighted
// geometric mean of the per-category index, recomputed in-browser:
//     composite(t) = exp( Σ_c w_c · ln(index_c(t)) / Σ_c w_c )
// which mirrors composite() in code/14-recent-ipi.py exactly.

const PALETTE = {
  design: "#2563eb", coding: "#0891b2", writing: "#7c3aed", marketing: "#db2777",
  video: "#ea580c", audio: "#16a34a", translation: "#ca8a04",
};
const fmtMonth = (m) => {
  const [y, mo] = m.split("-");
  return new Date(y, mo - 1).toLocaleString("en", { month: "short", year: "2-digit" });
};

let DATA, checked;

function compositeSeries(cats) {
  // Per-month review-weighted geometric mean over the selected categories.
  return DATA.months.map((_, i) => {
    let logSum = 0, wSum = 0;
    for (const c of cats) {
      const v = DATA.index[c][i], w = DATA.weights[c];
      if (v && v > 0 && w > 0) { logSum += w * Math.log(v); wSum += w; }
    }
    return wSum > 0 ? Math.exp(logSum / wSum) : null;
  });
}

function pct(series) {
  const a = series.find((v) => v != null);
  const b = [...series].reverse().find((v) => v != null);
  return a && b ? (b / a - 1) * 100 : null;
}

function deltaClass(d) { return d == null ? "flat" : d > 0.05 ? "up" : d < -0.05 ? "down" : "flat"; }
function deltaText(d) { return d == null ? "n/a" : (d >= 0 ? "+" : "") + d.toFixed(1) + "%"; }

function render() {
  const cats = DATA.categories.filter((c) => checked.has(c));

  // Headline: composite change for the current basket.
  const comp = cats.length ? compositeSeries(cats) : DATA.months.map(() => null);
  const d = pct(comp);
  const hn = document.getElementById("headlineNum");
  hn.textContent = cats.length ? deltaText(d) : "—";
  hn.style.color = `var(--${deltaClass(d) === "up" ? "up" : deltaClass(d) === "down" ? "down" : "ink"})`;
  document.getElementById("headlineLbl").textContent =
    `trailing 12 months · ${cats.length} of ${DATA.categories.length} categories · base ${fmtMonth(DATA.base_month)} = 100`;

  // Traces: thin per-category lines for checked cats + bold composite.
  const traces = cats.map((c) => ({
    x: DATA.months.map(fmtMonth), y: DATA.index[c], name: c, mode: "lines",
    line: { color: PALETTE[c] || "#999", width: 1.5 }, opacity: 0.55,
    hovertemplate: `${c}: %{y:.1f}<extra></extra>`,
  }));
  if (cats.length) {
    traces.push({
      x: DATA.months.map(fmtMonth), y: comp, name: "Composite IPI", mode: "lines+markers",
      line: { color: "#111827", width: 3.5 }, marker: { size: 5 },
      hovertemplate: "Composite: %{y:.1f}<extra></extra>",
    });
  }

  Plotly.react("chart", traces, {
    margin: { l: 48, r: 16, t: 16, b: 40 },
    xaxis: { showgrid: false, tickfont: { size: 12 } },
    yaxis: { title: { text: "Index (base = 100)", font: { size: 12 } }, zeroline: false,
             gridcolor: "#f0f0f0", tickfont: { size: 12 } },
    legend: { orientation: "h", y: -0.18, font: { size: 12 } },
    hovermode: "x unified", paper_bgcolor: "#fff", plot_bgcolor: "#fff",
  }, { displayModeBar: false, responsive: true });
}

function buildList() {
  const list = document.getElementById("catList");
  list.innerHTML = "";
  // Heaviest-weighted first, like CSRankings ordering by relevance.
  const ordered = [...DATA.categories].sort((a, b) => DATA.weights[b] - DATA.weights[a]);
  for (const c of ordered) {
    const d = DATA.delta12[c];
    const row = document.createElement("label");
    row.className = "row";
    row.innerHTML =
      `<input type="checkbox" ${checked.has(c) ? "checked" : ""} data-cat="${c}">
       <span class="name"><span class="swatch" style="background:${PALETTE[c] || "#999"}"></span>${c}</span>
       <span class="meta"><span class="delta ${deltaClass(d)}">${deltaText(d)}</span>
         <span class="wt">${(DATA.weights[c] * 100).toFixed(1)}% wt · ${DATA.panel_gigs[c]} gigs</span></span>`;
    row.querySelector("input").addEventListener("change", (e) => {
      e.target.checked ? checked.add(c) : checked.delete(c);
      render();
    });
    list.appendChild(row);
  }
}

fetch("data.json").then((r) => r.json()).then((data) => {
  DATA = data;
  checked = new Set(DATA.categories);
  buildList();
  render();
  document.getElementById("selAll").onclick = () => {
    checked = new Set(DATA.categories); buildList(); render();
  };
  document.getElementById("selNone").onclick = () => {
    checked = new Set(); buildList(); render();
  };
  document.getElementById("foot").innerHTML =
    `<strong>Method.</strong> Matched-model price index over the same Fiverr gigs tracked month to month
     (Jevons geometric-mean elementary aggregates; review-weighted geometric-mean composite). Each category
     is re-based to ${fmtMonth(DATA.base_month)} = 100. The composite shown updates live from the checked
     categories using their volume (review-count) weights. <br><br>
     <strong>Caveat.</strong> Thin categories (audio, marketing, video, translation) have sparse month-to-month
     matched pairs and can read near-flat at monthly cadence; design dominates the basket weight (${(DATA.weights.design*100).toFixed(0)}%).
     Quarterly figures are more robust — see <code>data/pilot/recent-ipi-summary.md</code>.
     Source: Wayback Machine snapshots, ${DATA.months[0]}–${DATA.months[DATA.months.length-1]}. Generated ${DATA.generated}.`;
});
