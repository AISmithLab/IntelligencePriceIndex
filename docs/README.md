# IPI website data contract — `data.json`

`data.json` is the single, self-contained input a frontend needs to render the
Intelligence Price Index (IPI): a matched-model price index for AI-exposed
knowledge work on Fiverr. It is small (~2 KB) and contains no raw scrape data.

Regenerate it from the pipeline with:

```bash
python3 code/15-build-site-data.py   # writes site/data.json
```

## Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `generated` | string | ISO date the file was built, e.g. `"2026-06-27"`. |
| `base_month` | string | The window-start month (`YYYY-MM`); every category is re-based to this month = 100. |
| `window_months` | number | How many month-points are included (currently 13 = a 12-month change plus the anchor). |
| `categories` | string[] | Category keys present, e.g. `["audio","coding","design","marketing","video","writing"]`. Use these to index `weights`, `panel_gigs`, and `index`. |
| `months` | string[] | The x-axis: month labels `YYYY-MM`, ascending. Length = `window_months`. Currently `2025-02` … `2026-02`. |
| `weights` | object | `category → weight` (0–1, a review-volume proxy). Used to weight the composite. Weights of the *displayed* categories do not necessarily sum to 1 (some categories are dropped at monthly cadence). |
| `panel_gigs` | object | `category → integer` count of distinct gigs underlying that category (display/credibility only). |
| `index` | object | `category → number[]`. Each array is parallel to `months`: the per-category matched-model price index, re-based so `base_month` = 100. Entries may be `null` where a category has no data that month. |
| `composite_all` | number[] | Parallel to `months`. The composite over **all** categories — the default series. Recomputing the composite over every category (see formula) reproduces this exactly. |
| `delta12` | object | `category → number` and `composite → number`: the trailing-12-month % change (first vs last month of the window). Convenience values for headline labels. |

## The one piece of logic: client-side composite recompute

The interactive feature (toggle categories → the composite updates) needs **no
backend**. For any selected subset of categories `S`, the composite at a given
month is the review-weighted geometric mean of the per-category index:

```
composite(month) = exp( Σ_{c∈S} w_c · ln(index_c[month]) / Σ_{c∈S} w_c )
```

…skipping any `(c, month)` where `index_c[month]` is `null` or `w_c` is 0. This
mirrors `composite()` in `code/14-recent-ipi.py`. Reference implementation:

```js
function composite(data, month_i, selectedCats) {
  let logSum = 0, wSum = 0;
  for (const c of selectedCats) {
    const v = data.index[c][month_i], w = data.weights[c];
    if (v && v > 0 && w > 0) { logSum += w * Math.log(v); wSum += w; }
  }
  return wSum > 0 ? Math.exp(logSum / wSum) : null;
}

// trailing-12mo % change of any series (array parallel to data.months):
function delta12(series) {
  const a = series.find(v => v != null);
  const b = [...series].reverse().find(v => v != null);
  return a && b ? (b / a - 1) * 100 : null;
}
```

With `selectedCats = data.categories` this returns `data.composite_all` to the
penny — a good correctness check for your renderer.

## Rendering notes & gotchas

- **Serve over HTTP.** `fetch('data.json')` fails from a `file://` page. Use any
  static host or `python3 -m http.server` during development.
- **Index, not dollars.** Values are an index (base month = 100), not prices. A
  category at 97 means ~3% below its `base_month` level.
- **Thin categories read flat.** At monthly cadence, low-volume categories
  (audio, marketing, video; translation drops out entirely) have sparse
  matched-pair coverage and can appear near-flat or carry `null` months. Design
  dominates the basket weight (~71%). Quarterly figures are more robust — see
  `data/pilot/recent-ipi-summary.md`.
- **Window is display-only.** 2024 snapshots still exist on disk as matched-model
  anchor data; `data.json` intentionally exposes only the trailing window.

## Changing what gets exported

Edit `code/15-build-site-data.py`:
- `WINDOW` — number of month-points to display.
- Swap `m14.to_month`/`month_to_float` for `m14.to_quarter`/`quarter_to_float`
  to emit a quarterly series instead of monthly.
- The re-basing step (each category ÷ its `base_month` value × 100) is where the
  "everything starts at 100" behavior comes from; remove it to ship raw index
  levels (base = mid-2024).
