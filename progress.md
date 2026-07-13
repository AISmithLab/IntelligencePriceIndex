# Progress Log

## 2026-07-13 — Units on the chart y-axis ticks (closing the last bare IPI number) [committed + pushed]

- **User re-issued "add units wherever an IPI number appears," then reported "I still don't see the units."** Two causes: (1) the first attempt tagged only the **top** y-axis tick, too subtle to notice on load; (2) nothing had been **pushed** — commits sat on local `mockup` while the deployed Pages branch is `mockup` on origin.
- **`docs/ipi.js` (`drawChart` y-gridlines):** now every y-axis tick carries ` pts` (e.g. default design view shows "100 pts / 200 pts / 300 pts"; all-categories "200…800 pts"). Widened the left margin **56 → 74** so the labels clear the rotated axis title (widest label "800 pts" left edge ≈ x25; title strip ends ≈ x19.5, verified against real `data.json` ranges).
- **State now:** all IPI *level* renders carry a unit — every y-axis tick (`ipi.js:258`), hover tooltip series (`ipi.js` "318.0 pts"), quarter inspector level ("265.6 pts"). FAQ Q3 readings (130 / 90 / 96.5 / 100) read "index points" from the prior pass; % change columns and $ gig prices already carried their own units.
- **Rebase note:** origin/mockup had a concurrent collaborator commit `35c3760 "Update FAQ on index reading and price changes"`; rebased my two commits on top — **clean, no conflict** (their FAQ edit touched different lines than the units work). FAQ still has 7 "index points" mentions post-rebase.
- **Verified:** `node --check docs/ipi.js` passes; tick labels computed against real data. No headless browser in this env.
- **Status: COMMITTED + PUSHED** on `mockup` (`fccefeb`). Files: `docs/ipi.js`, `progress.md`.

## 2026-07-13 — Units on every IPI number across the live site + FAQ

- **User: "add units to wherever an ipi number appears."** An IPI value is a dimensionless index (base 2020Q1 = 100), so the unit is **index points** (abbreviated **pts** on inline numbers). Some spots already carried a unit (y-axis title "IPI · index points", caption "Index level in index points", inspector "idx"); this pass covers the bare numbers and unifies the abbreviation.
- **`docs/ipi.js`:**
  - *Chart hover tooltip* (`drawChart`) — each per-series value was bare (e.g. "Design: 318.0"); now suffixed `pts` ("Design: 318.0 pts"). The tooltip header already noted "· IPI (base=100)".
  - *Quarter inspector level* (`renderInspector`) — unified the unit token from **idx → pts** so every inline index number reads the same way. (Level readout now "265.6 pts".)
  - Left the **y-axis tick labels bare on purpose** — the rotated axis title "IPI · index points (2020Q1 = 100)" carries the unit; repeating it on every tick is clutter (dataviz convention). SVG path coordinates and the `%`/weight figures were already correct.
- **`docs/faq.html` (Q3, Q8 Step 2, Q9, Q18 caveats):** added **"index points"** to the bare index readings in prose — the 130 / 90 example readings and the 96.5 translation dip in Q3, the "base quarter fixed at 100" definition (Step 2), "a reading above 100" (Q9), and the thin-category "held at 100" caveat (Q18). Baseline `100` mentions that a reader might land on directly (via FAQ anchors) each got the unit once.
- **Scope:** live site (`docs/index.html`, `docs/ipi.js`) + `docs/faq.html`. Did **not** touch the academic paper draft (`drafts/`), where index figures follow a different prose convention — extendable on request.
- **Verified:** `node --check docs/ipi.js` passes; `docs/faq.html` parses clean (`html.parser`); swept all `toFixed(1)` renders — the only two displayed index-level numbers (tooltip series, inspector level) now carry `pts`, everything else is coordinates or already-`%` figures. No headless browser in this env, so not screenshotted; changes are literal text appended to already-exercised render paths.
- **Status: EDITED, uncommitted** on `mockup`. Files: `docs/ipi.js`, `docs/faq.html`, `progress.md`.

## 2026-07-13 — FAQ Q3: clarified the above/below-100 reading so it doesn't imply below-100 lines exist

- **User confusion:** Q3 explained "above 100 / below 100" as if the reader would see it on the chart, but in the pilot every series starts at 100 and fans *upward* — nothing meaningful sits below 100 — so the framing read as disconnected from the actual line chart.
- **Data check (`docs/data.json`):** all seven categories start at exactly 100 (base 2020Q1) and end far above it (translation 209 → marketing 578; composite 318). The *only* sub-100 reading anywhere is translation at **96.5 in 2020Q4**, which recovers immediately. The dashed 100 line the chart draws (`ipi.js:119-127,255`) is the baseline anchor; `Δ'20–'26` = index − 100.
- **Edit:** Rewrote Q3 to (1) lead with "every series *starts* at 100" and name the dashed baseline explicitly, (2) keep the above/below-100 bullets but frame below-100 as the *general reading rule* rather than something on display, and (3) state plainly that the pilot fans upward with the lone translation dip as the only brush with sub-100. Still answers "how do I read the index and the change column."
- **Files:** `docs/faq.html` (Q3 block), `drafts/sections/faq.md` (synced). Not yet committed.
- **Status: EDITED, uncommitted** on `mockup`.

## 2026-07-13 — Live FAQ: ported draft's Q5/Q7/Q8 edits into docs/faq.html [committed + pushed]

- **User: "push the faq.md questions and answers into the live faq.html."** Draft and live were identical except for a collaborator's draft-only edits (commits `f594f03`, `f13f63d`) to Q5/Q7/Q8; ported those three into `docs/faq.html` so the live page matches the draft.
  - **Q5:** now states prices "include the Basic, Standard, and Premium tier" (was Basic-only); added the "each individual freelancer's subcategory is also graphed" sentence. Light copyedit of mechanical slips (comma splice, "over the time"→"over time", subject agreement); synced the same wording back into the draft.
  - **Q7:** dropped "or Upwork" from the heading and removed the Fiverr-vs-Upwork paragraph (kept the surveys/wage-data content).
  - **Q8:** heading now "How is the index calculated?" (dropped "(the formulas)"). Updated both matching TOC entries in the HTML and the draft's TOC.
- **Verified:** 15 `<h3>`, clean `html.parser` parse, 5 math blocks + 2 Q6 tables intact, TOC anchors == section ids in order.
- **⚠ Known inconsistency (flagged to user):** Q5's new tier claim contradicts Q6/Q8, which still describe extracting/using the **Basic** price (matches the actual pipeline and `data.json`). Left Q6/Q8 as-is pending user direction on whether the index truly now uses all three tiers.
- **Status: COMMITTED + PUSHED** on `mockup`. Files: `docs/faq.html`, `drafts/sections/faq.md`.


## 2026-07-12 — Live FAQ: rewrote all answers, merged 21→15 questions, fixed stale framing [committed + pushed]

- **User: "read the FAQ section, check updates needed for each question, combine questions where sensible, rewrite answers more informatively"** under 11 style rules (no dashes; sparing semicolons; no "it is worth noting / in conclusion / crucial"; no general-specific-general paragraphs; no symmetrical sentence structures; natural cautious academic prose; varied sentence structure; preserved rigor/terminology/formulas).
- **Substantive updates (not just style):**
  - *Q3 was stale.* It described "the big number at the top" (the composite headline), but commit `4c20173` **dropped the composite headline** and defaults the chart to a single category. Reframed around the per-category `Δ'20–'26` column and the composite-when-≥2-selected.
  - *Fixed the deflation-first framing.* Old Q3 led with deflation/AI-substitution and used a `−5%` example. Real `docs/data.json` (generated 2026-07-07) shows the composite at **317.7 (+217.7%)** with **every category up** (+109% to +478%). Rewrote the reading guidance to be direction-neutral and to note that all categories currently sit above base.
  - *Added a chain-drift caveat to the limitations* (new 2nd bullet). Reflects the 2026-07-07 pilot: chained Jevons likely overstates the true cumulative rise by ~2.4× vs drift-free GEKS/hedonic estimators. Framed cautiously ("upper bound"; weight direction + cross-category ordering over magnitude). Cross-linked from Q3.
- **Merged 21 → 15 questions** (kept first-of-pair ids so anchors stay stable): Q4+Q5 (window + ChatGPT/COVID → `#period`), Q6+Q7 (priced + categories → `#priced`), Q9+Q10 (why-revealed + why-Fiverr → `#whyrevealed`), Q14+Q15 (geometric means + distortion → `#geo`), Q16+Q17 (toggle + explorer → `#toggle`), Q19+Q20 (reproduce + cadence → `#repro`). Renumbered headings 1–15; rebuilt TOC to 15 entries.
- **Preserved all 5 formula `.math` blocks verbatim**; only rewrote surrounding prose/legends and converted en-dash ranges to "to" (`0.1–10×`→`0.1 to 10×`, `2011–2026`→`2011 to 2026`, `2018–2020`→`2018 to 2020`). Kept the `Δ'20–'26` label (mirrors the index-page column header + appears inside the formula). Step separators `—`→`&middot;`. Title em dash → `&middot;`.
- **Verified:** 15 `<h3>`, TOC anchors == section ids in order, 25/25 div balance, 5 math blocks, 7 step headers, clean `html.parser` parse, no em dashes and no stray en dashes outside the intended `Δ'20–'26` label.
- **Draft synced:** rewrote `drafts/sections/faq.md` to mirror the shipped page — merged to 15 questions, dropped the now-obsolete `[NEW]` tags, updated status header to "applied to live", carried over the reframed reading question and the chain-drift caveat.
- **Draft Q6/Q8 refinement (user follow-up):** restored Q6's two comparison tables as markdown (pipeline funnel + extraction cascade) and wrote out Q8's four formulas as display blocks, matching the HTML. **Verified every Q6 figure against source:** 60M→22.7M dedup, 48,643 qualifying sellers, 500 sampled / 26,603 snapshots (`progress.md`); 22,632 pages = 85% of 26,603; extraction shares computed from `data/pilot/pilot-prices.csv` are **exact** (packageList 72.9% / old_json 15.2% / dollar_fallback 11.2% / html_span 0.7%, n=22,632). Also cleaned em dashes I had introduced in the draft (rule 1).
- **Status: COMMITTED + PUSHED** on `mockup`. Files: `docs/faq.html`, `drafts/sections/faq.md`.

## 2026-07-07 — Pilot: unbalanced-panel index methods → possible chain drift in the headline IPI [uncommitted, runs/ only]

- **User asked:** streams of price data have misaligned durations (some 2020–2023, some 2020–2021); what methods estimate a general price index over time. Recommended time-dummy hedonic / chained superlative / GEKS / state-space; then ran a pilot on the real pilot panel.
- **Diagnostic (`runs/unbalanced-panel-methods/pilot_hedonic.py`):** panel is **highly unbalanced — 10.9% fill rate** (1,245 panel gigs × 53 quarters). Median gig observed 4 quarters / 2-yr span; range 0.25–13.25 yr. Heavy per-quarter entry/exit churn (e.g. 2021Q3: +181/−77). Confirms the duration-misalignment concern is material.
- **Key finding — likely chain drift in the current chained-Jevons IPI.** Compared existing `panel-ipi.csv` (chained Jevons) vs a **two-way FE hedonic** (gig FE + quarter dummies on log price, gig FE absorbed via within-gig demeaning / FWL; pure numpy). They correlate **r=0.91 in direction** but the **level gap grows monotonically**: 0 at 2020Q1 → −166 at 2024Q4 (hedonic **159** vs chained **326**). Monotonic divergence under heavy churn = classic chain-drift signature. Implication: **the peak composite (325.8, 2024Q4) may be ~2× overstated** by drift. Tail 2025Q1+ (<20 active gigs/q) is unreliable in both — trim.
- **GEKS referee ran — chain drift CONFIRMED (`runs/unbalanced-panel-methods/geks.py`).** Built a multilateral GEKS-Jevons index (transitive bilateral Jevons, drift-free but same matched comparisons as the chained index) on the thick-coverage window 2019Q1–2024Q4 (24 quarters, 1,026 panel gigs). Result: **GEKS ≈ hedonic (r=0.994, mean gap 11 pts)** — two independently-derived drift-free methods converge. Both sit far below the chained Jevons, which diverges monotonically to +182 pts by 2024Q4. **Chained overstates by 2.27× at 2024Q4 (326 vs GEKS 144, hedonic 169).** Real 2019Q1→2024Q4 rise is **+44–69%**, not the +226% the chained index implies.
- **Quality-adjusted hedonic added (`runs/unbalanced-panel-methods/quality_hedonic.py`) — 3 drift-free methods now cluster tightly.** Added time-varying within-gig controls to the FE hedonic: `ln p = alpha_gig + beta_quarter + g1*ln(1+reviews) + g2*rating`. Controls sensible & positive: **+9.4% price per e-fold of reviews, +8.2% per rating point** (part of the raw rise was reputation accumulation, not AI-era repricing). Rating/reviews present in 86% of obs. Quality-adjusted index lands **lowest (135 at 2024Q4)**, essentially on GEKS (r=0.996, mean gap 5.6). Four-way endpoint 2024Q4: **chained 326 · GEKS 147 · hedonic 169 · quality-adj 135.** Chained overstates the quality-adjusted index by **2.4×**; real quality-adjusted 2019Q1→2024Q4 rise ≈ **+35%** (vs +226% chained).
- **Recommended next:** (1) adopt a drift-free estimator as the new headline — GEKS-Jevons for the primary (stays in the matched-Jevons family, minimal change from current), FE hedonic + quality-adjusted hedonic as corroboration/robustness; (2) wire GEKS into `code/12-panel-ipi.py` + regenerate site/paper indices; (3) propagate to draft sections + `plans/todo.md` "refresh paper numbers" (peak 325.8 is now known to be a drift artifact, not a real level).
- **Outputs:** `runs/unbalanced-panel-methods/{pilot_hedonic.py, geks.py, quality_hedonic.py, hedonic-vs-chained.csv, three-index-comparison.csv, four-index-comparison.csv}` + Artifact chart (4 indices, interactive, https://claude.ai/code/artifact/0547e46c-b413-49d0-912b-79a06d0a5910). **Status: UNCOMMITTED, pilot only — production pipeline & headline numbers not yet changed.**

## 2026-07-07 — Live FAQ: applied all 21 questions to docs/faq.html [committed + pushed]

- **User: "push all 21 questions into the live site FAQ; do not include the [NEW] tag; keep all the formulas."**
- **Rewrote `docs/faq.html`** from the old **10-question** live version to the full **21-question** set from the reviewed draft (`drafts/sections/faq.md`), in the same reading-flow order. **No `[NEW]` tags** in the live HTML.
- **Preserved all formulas** — the 4-step method math (price relatives, chained Jevons, Törnqvist composite, headline change) plus the weights formula render as before (5 `.math` blocks), updated for the current chart: quarterly cadence, base quarter **2020 Q1 = 100**, headline **Δ'20–'26** (was Δ12mo), category-quarter min-3-matches wording.
- **Updated the TOC** to 21 entries with matching anchor ids (`#who #period #events #categories #whyrevealed #fiverr #inflation #distort #explorer #cadence #contribute` added); verified TOC anchors == section ids in order.
- **Killed stale copy:** removed "trailing-12-month", "recent-window", "full monthly path", "monthly cadence"; data-source section now says full-history quarterly build 2020 Q1→2026 Q1; reproduce section points to `code/18-build-site-data-long.py` → `docs/data.json`.
- **Verified:** 21 `<h3>`, 0 `[NEW]`, 5 math blocks, TOC↔ids match, 0 stale terms.
- **Status: COMMITTED + PUSHED** on `mockup`. File: `docs/faq.html` (index.html links to it, unchanged).

## 2026-07-07 — FAQ draft: synced to 2020Q1→2026Q1 quarterly chart + 6 new questions [committed + pushed, draft NOT applied to live]

- **User: review live site (`aismithlab.com/IntelligencePriceIndex`) vs GitHub `drafts/sections/faq.md`; the chart now covers 2020 Q1 → 2026 Q1 (quarterly). Compare existing FAQ to the updated chart, benchmark against csrankings.org/faq.html, and audience-check for gaps. Then rewrite `faq.md`.**
- **Review findings (3 lenses):**
  - *Staleness:* live `faq.html` (10 Qs) and the draft both still described the **old Feb 2025→Feb 2026 monthly** window; the live chart is now **quarterly, base 2020 Q1, 25 quarters → 2026 Q1**, headline **Δ'20–'26** (full-period, not trailing-12mo), **7 categories** (audio/coding/design/marketing/translation/video/writing, design ~71%). Also: the draft's previously-proposed [NEW] Qs were never applied to live `faq.html`.
  - *vs CSRankings:* IPI was thin on "how scope was chosen" (CSRankings spends ~5 Qs there) and "why not the obvious alternative data source."
  - *Audience:* nothing explained the 2020 start, the ChatGPT/COVID period now on-screen, the freelancer/per-gig explorer feature, or update cadence.
- **Rewrote `drafts/sections/faq.md`:** integrated single list of **21 questions in reading-flow order**. Fixed all quarterly/2020→2026 staleness in existing answers (headline Q3, formulas Q11, data-source Q8, weights Q13, limitations Q18, reproduce Q19 → `code/18-build-site-data-long.py`). Added **6 new `[NEW]`-tagged questions placed in-flow** (not appended): Q4 period/why-2020, Q5 ChatGPT/COVID visibility, Q7 category selection + "AI-exposed" criterion, Q9 why-not-surveys/wage-data, Q17 freelancer/gig explorer, Q20 update cadence. Per user: removed `[NEW]` tags from previously-new (now shipped) questions — only this revision's additions are tagged.
- **Verified data facts against `docs/data.json`** (cadence=quarterly, base_period=2020Q1, 25 periods, 7 categories, weights).
- **Status: COMMITTED + PUSHED** on `mockup`. Draft still says "do NOT apply to live HTML yet." File: `drafts/sections/faq.md`.

## 2026-07-07 — Site: centered header + removed rank (#) column from category table [committed + pushed]

- **User: "center the title and subtitle, also remove the # column in the category dropdown."**
- **Centered header (`docs/index.html`):** `header` flex row → **column, `align-items:center`, `text-align:center`**; logo now stacks above the centered title + def paragraph + FAQ nav.
- **Removed the `#` rank column** — dropped the `data-k="rank"` `<th>` (`index.html`) and the matching rank `<td>` in `catRow` (`docs/ipi.js`). Table is now **7 columns** (was 8). Fixed dependent colspans so alignment holds: `rankingRow` detail rows 6→**5**, composite footer 4→**3**. Default sort was already `delta`, so removing the (only) rank-sort header changes no ordering; the dead `rank` sort branch is harmless.
- **Verified in headless Chromium** (Playwright, 1280px): header `align-items:center`/`flex-direction:column`, def `text-align:center`; thead has no `#`, body/detail/footer all reconcile to 7 columns; expand-a-category detail row spans full width; **no overflow, 0 console errors**.
- **Status: COMMITTED + PUSHED** on `mockup`. Files: `docs/{index.html,ipi.js}`.

## 2026-07-07 — Site: smaller page gutters + mobile-scrollable FAQ tables [committed + pushed]

- **User: "make the web margin smaller."** Widened `.wrap` (`max-width` 1280→1600px) and trimmed side padding (20→12px) on both `docs/index.html` and `docs/faq.html` so content uses more of a wide screen. (faq `max-width` 800→900px, kept readable.)
- **Caught + fixed a pre-existing mobile bug while verifying:** the FAQ `.ftable` data tables (357px, nowrap Result column) overflowed a 375px phone viewport. Added `.ftable { display:block; overflow-x:auto }` inside the ≤560px media query so wide tables scroll in their own box instead of pushing the page sideways.
- **Verified in headless Chromium** (Playwright, served `docs/`): index + faq at 1920/1280/375px — **no horizontal overflow, 0 console errors** on any. Re-check script in scratchpad.
- **Status: COMMITTED + PUSHED** on `mockup` (`c9584b7`). Files: `docs/{index.html,faq.html}`.

## 2026-07-07 — Site: distinct per-category color palette [committed + pushed]

- **User: "add more distinct colors for each category."** The old category colors (`#2a6f47`, `#2a636f`, `#2a3c6f`, …) were all near-identical dark, low-chroma hues at the same lightness — the 7 overlapping trend lines were hard to tell apart.
- **Replaced with a CVD-safe distinct categorical palette** (from the dataviz skill's validated reference set): design `#2a78d6` blue, coding `#008300` green, writing `#4a3aa7` violet, video `#e34948` red, audio `#1baf7a` aqua, marketing `#eda100` yellow, translation `#e87ba4` magenta. **Validated with `validate_palette.js` on the `#fcfcfb` light surface:** lightness band PASS, chroma floor PASS, **worst all-pairs CVD ΔE 12.9** (above the ≥12 target — all 7 lines overlap so every pair, not just adjacent, must separate). Contrast WARN on the three lightest hues (aqua/yellow/magenta <3:1) is covered by relief — the category table + legend/tooltips carry identity, so color is never the only channel. Dominant **design** line got the high-contrast blue; the three low-contrast hues sit on thinner categories.
- **Applied at all three sources so they agree:** `code/18-build-site-data-long.py` `COLORS` (source of truth for regens), `docs/data.json` `colors` (patched in place — display-only, no pipeline re-run), and the `PALETTE` fallback in `docs/ipi.js`.
- **Verified in Chromium** (Playwright, served `docs/`): all 7 lines visually distinct, **0 console errors, 0 horizontal overflow**. Screenshot: `…/scratchpad/colors.png`.
- **Status: UNCOMMITTED** on `mockup`. Files: `code/18-build-site-data-long.py`, `docs/{data.json,ipi.js}`.

## 2026-07-07 — Data validation: fixed translation chaining bug + quarter-inspector on the graph [committed + pushed]

- **User: "validate the data, there's only one quarter of data for translation, why? also add feature for graph so you can see a specific quarter/year for IPI change."**
- **Root cause of thin translation — a real chaining bug in `code/12-panel-ipi.py`, not missing data.** Translation has 317 historical price obs / 36 gigs / 20 gigs in ≥2 quarters and **clears the ≥3-matched-pairs gate for 18 consecutive transitions (2020Q1→2024Q3)**. But the forward-chain loop required the *immediately-preceding grid quarter* to already be in the index (`if prev_q in index`). Translation has a coverage gap in **2019Q2–Q4** (right after the 2019Q1 base), so when the walk reached its first solid quarter (2020Q1) the previous quarter wasn't in the index → the assignment was skipped → and since 2020Q1 never entered the index, every later quarter was dropped too. **The entire forward chain was silently discarded.** Audio/marketing/etc. survived only because their coverage is contiguous with the base. On the site this left translation with recent-crawl data only (7 quarters, 2024Q3→2026Q1), because `chain_category` (step 18) found an empty historical column and fell back to recent-only.
- **Fix (surgical, forward-only):** made the forward chain **gap-tolerant** — chain from the most recent quarter already in the index (the matched-model relative already spans each gig's gap), instead of requiring the adjacent grid quarter. Left the **backward** chain strict on purpose (a symmetric backward fix reshaped pre-2019 levels: start-of-window 53.7→28.6, total +358.9%→+1003.9% — too much blast radius on the paper). Diff of `panel-category-indices.csv` is **purely additive**: translation gains 18 quarters (2020Q1–2024Q3), plus three previously-dropped late points (video 2025Q3, design/marketing 2025Q4) now bridge their gap. **No existing non-empty cell changed.**
- **Site regenerated (`code/18-build-site-data-long.py`):** translation now spans the **full 25 quarters** (2020Q1→2026Q1, +109% over the window), spliced historical→recent at 2024Q3 with **no discontinuity** (100→238 by the link, then 238→290→209). Composite barely moved: **+216.8% → +217.7%**.
- **New feature — quarter inspector on the composite chart (`docs/ipi.js` + `index.html`):** pick any quarter from a year-grouped dropdown **or click the chart** to pin it; a blue dashed rule + labelled dot mark it, and a readout row shows **composite level · QoQ · YoY (4 quarters) · vs window base (2020Q1)** with up/down coloring. `clear` unpins. Dropdown and click share one `pinned` state; recomputes live as the basket changes.
- **Verified end-to-end in Chromium** (Playwright, served `docs/`): 8 chart paths (7 cats + composite, translation included), dropdown pick 2023Q2 → composite 265.6 / QoQ +4.2% / YoY +34.9% / vs2020Q1 +165.6%, click-to-pin works, clear works, **0 console errors, no horizontal overflow**. Screenshot: `runs/…/inspector.png` (scratchpad).
- **⚠️ Paper impact (NOT yet applied to drafts):** re-running step 12 also revived `data_entry`/`data_analysis`/`translation` in the composite + elasticity outputs. `panel-ipi.csv`, `panel-elasticity.csv`, `panel-summary.md` changed: **peak composite 311.6→325.8 (2024Q4)**, **elasticity table now 8 categories (was 5)** — translation/data_entry/data_analysis added; design 1.10→1.14, marketing 0.700→0.701 (negligible). Existing draft prose still cites the old figures (312 peak, 5 categories). Flagged as a to-do — did not silently rewrite the paper.
- **Status: COMMITTED + PUSHED** on `mockup` (`012b7ea`, pushed to `origin/mockup` 2026-07-07). Files: `code/12-panel-ipi.py`, `data/pilot/panel-{category-indices,ipi,elasticity}.csv`, `data/pilot/panel-summary.md`, `docs/{data.json,ipi.js,index.html}`.

## 2026-07-06 — Freelancer explorer: 25/category + per-gig price-over-time drill-down [uncommitted]

- **User: "show more freelancers … a dropdown for each freelancer to show the gigs they sell and how those prices changed over time."** Widened the rankings and made every freelancer expandable to a per-gig price history.
- **Diagnosed the broken-link complaint first:** the site linked each seller to their **live** `fiverr.com/{handle}` profile (`ipi.js`), which rots — archived sellers are frequently deleted/renamed. Also surfaced that the freelancer *pool* on disk is huge: the full classified CDX index has **822,807 distinct status-200 sellers** vs the ~3.3k the rankings showed.
- **`code/18-build-site-data-long.py` — rewrote `build_rankings()`** to rank by distinct **priced** gigs (source of truth = `pilot-prices.csv` + `recent-prices.csv`, year ≥ 2020), so every listed seller is expandable with a real chart. `TOP_N` 12 → **25**. Category per gig from the recent manifest where present, else `classify_gig` on the item text (same taxonomy as the index). Emits a new **`docs/freelancers.json`** (268 KB, 163 sellers, 698 gigs): per seller, each gig's `{slug, cat, title, url, series}` where `series` = `[[YYYYMMDD, basic, standard, premium], …]` **change-point compressed** (flat runs collapsed; ~74% of gigs have ≥2 points). Gig `url` is the **Wayback snapshot** (`…/web/{lastdate}/https://www.fiverr.com/{seller}/{slug}`), not the live profile — fixes the link rot. Priced-seller counts ≈ prior rankings (design 1528, coding 519), so headline numbers barely moved.
- **`docs/ipi.js` + `index.html` — nested drill-down UI.** `freelancers.json` is fetched **lazily** on first category expand (initial load stays light). Each freelancer row is now a caret toggle; expanding renders one compact **inline-SVG price-over-time chart per gig** (self-contained, no libs, matching the house `spark()` style). The three package tiers are **ordered**, so encoded as the category hue at **three lightness steps** (sequential ramp, inherently CVD-safe) — not three categorical colors; one panel-level legend + direct end-labels ($750 P / $75 S / $50 B) + native hover tooltips (date + all tiers). Single-snapshot gigs render as labeled dots. Added a **vertical de-collision pass** on the end-labels (min 10.5px gap) after the first render showed near-equal tiers overlapping.
- **Verified end-to-end in a real browser** (installed Playwright Chromium; served `docs/`): expand Coding → click matarrese8 → 14 gig charts render, "Fix WordPress" climbs ~$50→$750 over time, 0 console errors, no horizontal overflow (panel scrollW == clientW). Screenshot: `runs/freelancer-explorer.png`.
- **Scope note:** price-over-time is limited to sellers we actually downloaded+extracted prices for (the 500-seller pilot + recent crawl), NOT the full 822k CDX pool — that pool has gig *counts* but no prices. Growing the priced panel remains the separate, download-heavy lever (todo "Full-scale data collection").
- **Status: UNCOMMITTED** on `mockup`. Files: `code/18-build-site-data-long.py`, `docs/{ipi.js,index.html,data.json,freelancers.json,README.md}`, `plans/active/05-freelancer-explorer.md`, `progress.md`.

## 2026-07-03 — Freelancer rankings now span the FULL 2020→2026 history [uncommitted]

- **User: "retrieve data from 2020 … dropdown should show ranking of each freelancer for each category by number of services/gigs."** Found the 2026-07-02 build already delivered the 2020→2026 quarterly index AND the expand-row freelancer rankings — but the **rankings were sourced only from the recent 2024–2026 crawl** (`recent-manifest.tsv`), so they didn't reflect the 2020-era archive the user asked about.
- **`code/18-build-site-data-long.py` — `build_rankings()` now unions two sources** so each seller's distinct-gig count spans the whole window: (1) the recent manifest (category given, months ≥2024, unchanged), plus (2) the **historical 500-seller pilot** (`pilot-prices.csv`, filtered to observations in year ≥ `START_YEAR=2020`), with each historical gig classified into the 7 display categories via a copy of step 12's `CATEGORY_KEYWORDS`/`classify_gig` (kept identical so rankings use the same taxonomy the historical price index was built with). A distinct gig = `seller/slug`; unioning dedups gigs present in both crawls. Non-basket classes (data_entry/data_analysis/None) are dropped.
- **Effect:** rankings got materially deeper (gig counts and seller pools both up): design `ace_art` 15 gigs / 1,528 sellers (was `alimsarder786` 10 / 1,341), coding `matarrese8` 14 / 519 (was `creativesalahu` 5 / 406), audio `shadowvo` 11 / 89 (was `aioriar` 2 / 52). All 7 categories now list real multi-gig leaders.
- **No change to the index/composite** — only `build_rankings()` touched. Composite unchanged at **+216.8%** (2020Q1→2026Q1, 25 quarters). Kept the existing expand-row (▸) UI (chosen default; user was away when asked whether to switch to a literal `<select>`).
- **Validated:** `node --check docs/ipi.js` passes; `data.json` re-parses; ranking contract (`rankings[c].sellers`, `top[{seller,gigs}]`) unchanged so the frontend render path is unaffected. No headless browser available in this env, so not visually screenshotted.
- **Status: UNCOMMITTED** on `mockup`. Same file set as 2026-07-02 (`docs/{data.json,index.html,ipi.js}`, `code/18-build-site-data-long.py`) plus `progress.md`.

## 2026-07-02 — Site pivot: full-history QUARTERLY index (2020→2026) + freelancer rankings [uncommitted]

- **Reframed the site from trailing-12mo/monthly to full-history/quarterly.** New **`code/18-build-site-data-long.py`** (supersedes step 15/17 for the site) chains two matched-model panels into one continuous quarterly per-category series: the historical 500-seller pilot (`panel-category-indices.csv`, dense 2020–2024) **ratio-spliced at the shared 2024Q3 link** onto the recent trailing-window crawl (`recent-category-indices.csv`, base 2024Q3=100), then re-based to **2020Q1=100**. Splice keeps the level continuous through the join; quarterly cadence keeps the x-axis uniform and is more robust for thin categories. Composite contract unchanged: `exp(Σ w·ln(idx)/Σ w)` recomputed client-side from review weights.
- **New `rankings` block** in `data.json`: per category, top-12 freelancers by number of distinct gigs/services offered, derived from `recent-manifest.tsv` (`gig_id = seller/slug`), with a `RESERVED` set filtering non-seller URL segments (hire, categories, search, …).
- **`docs/ipi.js`** — (1) `significantMoves()` threshold rescaled 0.8%→4% for quarterly steps and capped at 5 labels (always retaining the two extremes) so a multi-year axis stays readable; move notes/labels reworded month→quarter. (2) Sparklines switched from a shared y-domain to **per-series auto-scale** (levels now span 100→~580 across categories, so a shared domain flattened low-movement rows); 100 kept in range as baseline. (3) Category expand (▸) now renders a **top-freelancers ranking row** (rank, Fiverr-linked handle, gig-count bar) via new `rankingRow()`, replacing the old monthly value dump.
- **`docs/index.html`** — ranking-row CSS (`.rankbox`/`ol.rank`), definition + headline + chart legend reworded to "quarterly from 2020 to today," Δ column header → Δ'20–'26, selbar hint mentions expand-for-freelancers. Dropped the dashed-subcategory legend (subcats not part of this build).
- **Result:** `data.json` regenerated — quarterly, base 2020Q1, **25 quarters (2020Q1→2026Q1)**, 7 categories, carries `rankings`. Full-window composite change **+216.8%** (the historical run-up dominates; recent trailing window is roughly flat, per the 2026-06-27 note). Validated: `node --check docs/ipi.js` passes; both source CSVs present; `data.json` exposes every key the JS reads.
- **Status: UNCOMMITTED** on `mockup`. Modified `docs/{data.json,index.html,ipi.js}`; untracked `code/18-build-site-data-long.py`. Not yet committed/pushed to Pages.

## 2026-06-30 — Site: show BOTH main (broad) categories AND subcategories

- **User: "can you do both subcategories and main?"** Switched from carving subcats *out of* their parent to a two-level model: **main** = full broad domains (the basket/composite), **sub** = relevant subcategory detail lines nested under their parent and **excluded from the composite** (their gigs already sit inside the parent — including them would double-count).
- **`code/17-build-site-data-narrow.py`** — now builds the production broad index (`build_site_data()`) as the main basket, then grafts the relevant subcats (from the full-narrow build) with `level`/`parent`/`label`/`color` metadata. Subcat weight is carried for display only. Composite stays the robust broad −2.1%.
- **`docs/ipi.js`** — composite now computed over `mainChecked` (`level != "sub"`) only; `drawChart` renders sub lines **dashed** ("5 3"); table factored into a `catRow(c, rank, sub)` helper that renders mains and nests each domain's subcats beneath it (indented "↳", gig-share weight in parens, no rank). Footer counts mains only. Caveat + chart legend updated (dashed = subcategory, not in composite).
- **`docs/index.html`** — `.sub` row styling + a dashed-line legend swatch.
- **Result:** main = audio, coding, design, marketing, video, writing; one sub = **Logo & Brand** (Δ −1.8%, 45.2% of basket reviews) nested under Design (Δ −3.3%, 70.6%). Verified: main-only composite recomputes to −2.1% (= stored), main weights sum to 0.997, main/sub colors distinct. `node --check` passes.

## 2026-06-30 — Site: keep only the RELEVANT subcategories (collapse the rest)

- **User: "include the relevant subcategories."** Replaced the show-everything subdivision with a relevance filter in **`code/17-build-site-data-narrow.py`**: a subcat earns its own line only if it BOTH (a) moves — index range ≥ 1.5 pts — AND (b) is well-covered — ≥ 7/12 chainable months. Movement alone admits noise (design-ui_ux_web swung +14% off only 4/12 covered months); coverage alone admits dead-flat lines (most subcats sit at exactly 100 because their matched gig-pairs have unchanged prices). Subcats failing either test collapse back into their broad parent, so that parent keeps its real movement.
- Added **`measure_coverage()` / `relevant_subcats()`** + a `keep`-aware `write_narrow_manifest()` to **`code/16-subclassify-narrow.py`**, and broad-remainder bucket metadata (darker family-hue shade) to `category_meta()`.
- **Result:** the data supports exactly **one** breakout — **design-logo_brand** (range 10, 11/12 coverage, −1.8%). Final basket = 6 broad domains (audio, coding, design, marketing, video, writing) + Logo & Brand carved out of design; translation still too thin to chain. Design's −3.3% broad decline decomposes into Logo & Brand −1.8% and a +1.4% design remainder — i.e. the deflation concentrates in logo/branding.
- **Correctness check:** every untouched domain's delta matches the production broad build exactly (writing +2.3, coding −0.1, marketing/video/audio +0.0); only design differs (logo_brand carved out). **Composition caveat:** the all-categories composite reads −0.2% narrow vs −2.1% broad — a matched-model artifact (splitting design thins per-transition matched pairs and erodes the chained decline), not real economics. Caveat text updated to say the broad/quarterly figures remain the robust headline.
- `node --check ipi.js` passes; `data.json` (3.1 KB) carries labels/colors/parents for all 7 categories.

## 2026-06-30 — Site: narrow subcategories + marketing-name wrap fix

- **Marketing wrap fix** — in the narrowed right-hand table column the category name wrapped *under* its color swatch. Fixed with `.name { white-space: nowrap }` (and dropped `text-transform: capitalize`, which would mangle pre-formatted labels like "eBook").
- **Narrow subcategories (user: "subdivide everything anyway")** — added a subdivision pipeline that reuses step 14's matched-model machinery unchanged:
  - **`code/16-subclassify-narrow.py`** — narrow taxonomy (34 subcats across the 7 broad domains), re-labels `recent-manifest.tsv` → `recent-manifest-narrow.tsv` by keyword-matching slugs within each parent. Also emits display `labels`, `parents`, and parent-hued `colors` (HSL shades of the broad family color).
  - **`code/15-build-site-data.py`** — refactored into `build_site_data(manifest=None)` + `write_and_report()` so a custom manifest can be swapped in (sets `m14.MANIFEST_FILE`) without duplicating the rebasing/weight/composite logic. Default behavior unchanged.
  - **`code/17-build-site-data-narrow.py`** — orchestrates: narrow manifest → `build_site_data(narrow)` → attach labels/parents/colors → write `docs/data.json`. Revert to broad = re-run step 15.
  - **`docs/ipi.js`** — added `colorOf()`/`labelOf()` (read `DATA.colors`/`DATA.labels`, fall back to flat palette + `cap()` so the broad build still works); dialed line opacity to 0.32 when >10 categories overlap; updated the caveat to describe narrow-subcategory thinness.
- **Pilot first (per CLAUDE.md):** measured matched-pair coverage before committing. At monthly cadence with the ≥3-pair gate, current broad cats chain 7–11/12 months; only **design** subcats (and coding/web-dev) clear that bar. Recorded in the pilot script.
- **Result:** 17 of 34 subcats survive step 14's `len(idx)>=2` gate; 18 too thin and dropped. **Honest caveat surfaced to user:** most survivors read +0.0% (single chainable transition, forward-filled flat), `design-ui_ux_web` is a noisy +14% off few pairs, and the composite reads −0.8% (vs −2.1% broad) because flat subcats dilute design's real decline. Offered design-only or broad revert as cleaner alternatives.
- `node --check ipi.js` passes; `data.json` carries `labels`/`colors`/`parents` for all 17 categories.

## 2026-06-30 — Site: taller chart + descriptions for each highlighted move

- **`docs/ipi.js`** — (1) enlarged the trend chart (`H` 320 → 420, slightly larger margins) so it reads bigger alongside the already-widened left column. (2) Added `renderMoveNotes()` which now **populates the previously-empty `#movenotes` list** under the chart: one short line per highlighted move (e.g. *"2025-10 → 2025-11: composite fell −2.3% month-over-month — sharpest single-month drop in the window."*). `significantMoves()` now tags each move with a `why` (threshold crossing vs. biggest rise/drop) and returns them in chronological order so the list reads top-to-bottom in time.
- **Note:** the `#movenotes` element + CSS were added in the prior commit but never filled by JS — they were dead until this change. `node --check` passes; full basket yields 4 described moves.

## 2026-06-30 — Site: highlight significant composite moves on the chart

- **`docs/ipi.js`** — added `significantMoves()` (month-over-month moves past a 0.8% threshold, always including the single biggest rise + biggest drop) and overlaid them on the composite line in `drawChart`: thicker green/red segment, endpoint dot, and a `±x.x%` label. Recomputes live as categories are toggled. With the full basket it flags +0.9% (Mar '25), −1.6% (Sep '25), −2.3% (Nov '25, biggest drop), +1.3% (Dec '25, biggest rebound).
- **`docs/index.html`** — added a small legend caption under the chart (green = price rise, red = price drop). `node --check` passes.
- Also clarified for the user that **composite** = the single headline IPI line — the review-weighted geometric mean across the *selected* categories (`exp(Σ w·ln(index)/Σ w)`), i.e. the whole-basket index vs the per-category sub-indices.

## 2026-06-30 — Site: IPI definition under title + side-by-side chart/selection

- **`docs/index.html`** — per user request: (1) added a clear full-sentence **definition of the IPI directly under the page title** (CPI-style price index of AI-exposed freelance work from posted Fiverr gig prices, trailing 12mo); (2) replaced the stacked chart-then-table layout with a **side-by-side CSS grid** (`.layout`): trend chart in the left card, category-selection table in the right card, collapsing to stacked below 900px. Widened `.wrap` to 1180px to fit two columns.
- **Verified** all element IDs consumed by `ipi.js` (`hNum`, `chart`, `tip`, `rows`, `foot`, `selAll`, `selNone`, `hRange`, `caveat`, `src`) survive the restructure, so the script is unaffected. `faq.html` carried matching aesthetic refresh.
- **Deployed:** committed + pushed `docs/` on `mockup` (GitHub Pages source) to make the changes live.

## 2026-06-30 — IPI frontend committed + hardened on `mockup` branch

- **Committed the rebuilt frontend** that had been sitting untracked: `site/index.html`, `site/ipi.js`, `site/.nojekyll`, `scripts/deploy-site.sh`. The work is now preserved in git on branch `mockup`.
- **Correction to the 2026-06-29 note:** the rebuilt `ipi.js` is now **fully self-contained — no Plotly / no external libs**. It hand-rolls the trend chart and per-row sparklines as inline SVG, so the page works offline and over `file://`-style static hosting with zero CDN dependency.
- **Re-validated before commit:** `node --check site/ipi.js` passes; `data.json` exposes every key `ipi.js` consumes (`months`, `categories`, `weights`, `index`, `composite_all`, `delta12`, `panel_gigs`, `generated`); client-side composite recompute reproduces `composite_all` (max abs diff 5.2e-3, all from JSON 2-dp rounding) and the trailing-12mo headline recomputes to **−2.10%**, matching the stored `delta12.composite` (−2.1).
- **Status:** frontend committed and validated on `mockup`. `gh-pages` Pages setting still not enabled (the user is steering hosting). `scripts/deploy-site.sh` remains the one-command redeploy path but was **not run** (it force-pushes `gh-pages`). Also present on this branch: `scripts/make_mock_ipi.py`, a 20-category synthetic-data + matplotlib mockup generator (separate exploration, untouched).

## 2026-06-29 — IPI frontend rebuilt on `mockup` branch (uncommitted)

- After the 2026-06-27 takedown, the interactive site was **rebuilt** against the kept data layer. Recreated (currently **untracked** — not yet committed): `site/index.html`, `site/ipi.js`, `site/.nojekyll`, `scripts/deploy-site.sh`.
- **Reuses the committed data contract** (`site/data.json` from 2026-06-27, plus `site/README.md` + `site/GUIDE.md`) — no pipeline re-run.
- **Verified consistent:** `ipi.js` consumes exactly the keys `data.json` exposes (`months`, `categories`, `weights`, `delta12`, `panel_gigs`, `index`, `generated`); client-side composite mirrors `composite()` in `code/14-recent-ipi.py` as `exp(Σ wᶜ·ln(idxᶜ)/Σ wᶜ)`. Window = 13 months (2025-02 → 2026-02), **6 categories** (translation drops out at monthly cadence; handled gracefully). Page caveat re-shipped: design ~71% weight, thin categories read near-flat monthly, quarterly figures more robust.
- **Status:** working frontend exists on branch `mockup` but is uncommitted; `gh-pages` Pages setting still not enabled. Next steps if continuing: commit the rebuilt `site/` + `scripts/deploy-site.sh`, then enable Pages (or deploy via the user's own hosting).

## 2026-06-27 — Website taken down (user building their own frontend)

- The page wasn't working (GitHub Pages was never enabled in repo settings) and the user decided to build their own website instead.
- **Took down the frontend + deployment** (user-confirmed scope "Frontend + live, keep data"):
  - Deleted the remote and local `gh-pages` branch (unpublished the site).
  - Removed `site/index.html`, `site/ipi.js`, and `scripts/deploy-site.sh`.
- **Kept** `code/15-build-site-data.py` and `site/data.json` so the user's own site can reuse the generated data (documented data-contract: months, categories, per-category monthly index, weights, composite, delta12; composite recompute = `exp(Σ wᶜ·ln(idxᶜ)/Σ wᶜ)`).
- The underlying recent IPI data and pipeline (steps 13–15) are untouched.

## 2026-06-27 — CSRankings-style IPI website built (monthly, client-side recompute)

- **Built the static IPI website** (`site/`), CSRankings-inspired: a category checklist drives a live, in-browser recompute of the composite index.
  - **`code/15-build-site-data.py`** — reuses step 14's matched-model machinery via `importlib` to emit the **monthly per-category index** (step 14 computes this internally but only ever wrote the monthly *composite*). No re-download or pipeline change. Output: **`site/data.json` (2.2 KB)** — just small arrays, none of the 21 GB of HTML.
  - **Monthly cadence** (user: "show the IPI per month"), **trailing 12 months only** = last 13 months with a real composite (2025-02 → 2026-02; no forward-filled phantom tail), each category **re-based to window-start = 100**.
  - **`site/index.html` + `site/ipi.js`** (vanilla JS + Plotly): heaviest-weighted-first checklist (each row shows Δ12mo, weight, panel gigs), bold composite + thin per-category lines, select-all/none, headline that updates with the basket. Composite recomputed client-side as `exp(Σ wᶜ·ln(idxᶜ)/Σ wᶜ)`, mirroring `composite()` in step 14.
  - **Validated offline** (no server, per user): JS syntax OK; client recompute over all categories reproduces `composite_all` exactly; unchecking design (71% wt) shifts the basket −2.1% → +0.8%.
  - **Headline:** all-categories composite trailing-12mo = **−2.1%** (2025-02→2026-02). **Caveat shipped on the page:** thin categories (audio/marketing/video; translation drops out monthly) read near-flat at monthly cadence; quarterly figures in `recent-ipi-summary.md` are more robust.
  - **Deployed:** published `site/` to an orphan `gh-pages` branch (files at root + `.nojekyll`) and pushed to origin. Added `scripts/deploy-site.sh` for one-command redeploys (regenerate `data.json` → publish to `gh-pages`). **One-time manual step left:** enable Pages in repo Settings → Pages → branch `gh-pages` / root. Live URL once enabled: https://aismithlab.github.io/IntelligencePriceIndex/

## 2026-06-27 — Trailing-12-month IPI built (past-year data retrieval complete)

- **Resumed the stalled recent-window download** (was 12,949/15,309) via `code/run-recent-pipeline.sh`. Final: **15,150/15,309 captured (99.0%)**, 21 GB. The 159 misses are persistent Wayback 429/timeout (exhausted retries over 2 passes; no 403/ban signal).
- **Fixed a bug in `code/09-extract-prices.py`:** `filepath.relative_to(BASE_DIR)` crashed when `--html-dir` is a relative path (BASE_DIR is absolute). Now resolves the path first, falls back to the raw string. This had silently produced an empty `recent-prices.csv` on the first driver run, making the index build report "no data."
- **Extraction: 15,150/15,150 (100%)** → `data/pilot/recent-prices.csv`. Methods: packageList JSON 74.6%, dollar fallback 25.4%.
- **Trailing-12-month IPI built** (`code/14-recent-ipi.py`), matched-model, base 2024Q3=100, window 2024Q3→2026Q1. Panel: 3,566 gigs across 7 categories.
  - **Composite IPI essentially flat over the past year: 2025Q1 → 2026Q1 = −0.3%** (level ~90, down from the 100→100.5 2024 anchor — a one-step ~10% drop into 2025Q1, then flat).
  - Per-category Δ12mo: video −11.6%, coding −6.8%, writing −6.6%, translation −2.7%, marketing −1.2%, audio +0.6%, design +2.1%.
  - Weights are design-dominated (w=0.71) — design's +2.1% offsets the AI-exposed categories' declines, flattening the composite.
  - Outputs: `recent-ipi.csv`, `recent-category-indices.csv`, `recent-category-weights.csv`, `recent-ipi-monthly.csv`, `recent-ipi-summary.md`.
- **Unblocks the CSRankings-style website** (`plans/active/04-ipi-website.md`) — all data-contract CSVs now exist.

## 2026-06-26 — Recent-window data retrieval for trailing-12-month IPI

- **Goal:** extend the IPI to a genuine "past year" (CPI-style trailing 12 months) across all viable Fiverr categories. The original 500-seller pilot was sampled for long histories and goes sparse after 2024Q4, so it can't support a recent index.
- **Manifest (built prior session, `code/13-recent-manifest.py`):** `data/pilot/recent-manifest.tsv` — selects gigs with ≥2 distinct quarters of coverage anchored at 2024Q3 AND ≥1 snapshot in the trailing window (2025Q3–2026Q2), one snapshot/month each.
  - **15,309 snapshots, 3,589 distinct gigs, 7 categories:** design 6,959 / coding 2,634 / writing 2,198 / marketing 1,534 / video 1,295 / audio 437 / translation 252. Months span 202407–202603.
  - Thin categories excluded (uncategorized, data_entry, data_analysis).
- **Download (`code/08-download-html.py`):** launched full retrieval from Wayback Machine raw (`id_`) captures → `data/pilot/html-recent/`, log `recent-download-log.tsv`, checkpoint `recent-download-checkpoint.txt`.
  - Tuned concurrency: tested 10/24/10/20. Throughput is latency-bound (~1.6 MB raw fetches, ~15 s each). Failures are 429/timeout exhausted-retries logged as `fail` (NOT 403 — no ban signal) and are NOT checkpointed, so a second pass retries them. Settled on concurrency 20 / 20 req/s (~74% per-attempt success, ~1/s good throughput).
  - Validation: 210-snapshot pilot test (`recent-pilot-test.tsv` → `html-recent-test/`) had previously confirmed 100% extraction-grade captures.
- **Pending (this run):** finish full download (~24 GB est.), run a retry pass over `fail` rows, then extract prices into `data/pilot/recent-prices.csv` (parameterized `code/09-extract-prices.py` to accept `--html-dir/--output`).

## 2026-03-23 — IPI constructed, full paper drafted and self-reviewed

- **Price extraction:** 22,632/22,632 HTML files extracted (100% success). Methods: packageList JSON (72.9%), old JSON (15.2%), dollar fallback (11.2%), HTML span (0.7%). Output: `data/pilot/pilot-prices.csv`.
- **Item clustering:** 1,908 unique gigs clustered into 150 service items (TF-IDF + agglomerative, k=150, silhouette=0.114). Output: `data/pilot/gig-items.csv`, `data/pilot/item-clusters.csv`.
- **AI benchmark dataset:** Created `data/ai-benchmarks.csv` with 8 benchmarks (HumanEval, SWE-bench, WMT BLEU, AlpacaEval, Chatbot Arena, FID, GSM8K, Whisper WER) spanning 2017–2025.
- **IPI construction (cross-sectional):** Script `code/11-build-ipi.py` — Laspeyres-style index, 9 categories. Revealed platform-wide price inflation masking AI effects.
- **IPI construction (panel):** Script `code/12-panel-ipi.py` — Matched-model Jevons/Törnqvist index tracking same-gig prices. Key results:
  - IPI: 100 (2019Q1) → peak 312 (Q4 2024) → 246 (Q2 2025), **−21% from peak in 2025**.
  - Price elasticity of intelligence: audio β=−0.49 (substitution), writing β=+0.21, coding β=+0.30, marketing β=+0.70, design β=+1.10 (complementarity). All significant p<0.01.
  - Novel concept: "shadow deflation" — AI effect masked by platform inflation, visible only as deceleration.
- **Full paper drafted:** All 8 sections written (abstract, introduction, related work, methods, findings, discussion, limitations, conclusion).
- **Self-review and polish:** Fixed number inconsistencies (312% → "peaked at 312"), section numbering (8→7 sections), missing data flow explanation (14,938→1,908 gigs), added 4 missing categories to elasticity table, trimmed CPI analogy and survivorship bias redundancy, fixed broken cross-references in related work.
- Key outputs: `data/pilot/panel-ipi.csv`, `data/pilot/panel-summary.md`, `data/pilot/panel-elasticity.csv`, all drafts in `drafts/sections/`.

## 2026-03-22 — Phase 1 complete + Pilot download launched

- **Phase 1 (CDX filtering) complete:** Steps 1.1–1.6 all done.
  - Fixed OOM crashes in dedup/filter scripts by switching from in-memory dicts to external sort + streaming.
  - Full census: 5.6M unique gigs, 822K unique sellers across 10 categories + uncategorized.
  - 60M raw CDX → 22.7M deduped → classified by category → longitudinal filter applied.
- **Sampling strategy refined toward CPI-style index:**
  - User wants to track price impact of AI, weight by transaction volume (like CPI basket).
  - Decided to sample at user level (preserves within-seller panel for upskilling analysis).
  - Survivorship bias is acceptable — gig disappearance is part of the AI impact signal.
  - Wayback Machine coverage bias acknowledged as limitation (over-represents popular gigs).
- **Pilot: 500 users sampled** (from 48,643 qualifying users with ≥5 monthly snapshots spanning ≥2 years).
  - 500 users, 14,938 gigs, 26,603 monthly snapshots.
  - Download launched (~5 GB compressed, ~30–45 min).
  - Scripts: `code/06c-pilot-longitudinal.py`, `code/07-pilot-500.py`, `code/08-download-html.py`.
- Key outputs: `data/pilot/pilot-500-manifest.tsv`, `data/pilot/html/` (downloading).

## 2026-03-21 — CLAUDE.md updates: hajimi confirmation + user prompts as tests

- Added `hajimi` print directive to confirm CLAUDE.md is loaded (helps verify config in VS Code sessions).
- Added Philosophy #6: User prompts as first-class test inputs. Instructional prompts about paper content become test entries in `tests/<section>.test.md` under `## User Requirements`.

## 2026-03-21 — Fiverr archive size estimation complete

- ~2.5M unique gig URLs on Wayback Machine, 4–20 TB raw (too large for full download).
- Recommended strategy: two-phase filtered download — Tier 1 categories only (writing, coding, design, translation) with 3+ snapshots spanning 2+ years → ~275 GB compressed.
- Report saved to `runs/archive-size-estimation/report.md`.
- Plan updated: `plans/active/03-fiverr-archive-download.md` — Step 1 complete, Step 2 (download) pending.

## 2026-03-21 — Data Pilot GO + Scoping Complete (parallel execution)

**Data Feasibility Pilot — GO:**
- Wayback Machine has 50+ Fiverr snapshots per category spanning 2012–2025.
- Price extraction: 100% success (20/20 pages) via embedded JSON `packageList`.
- Worker tracking: 6 sellers tracked with 3+ snapshots each. Key finding: froggy92 (architecture) dropped from $50 → $20 (−60%) over 4 years.
- Upwork/Freelancer checked as fallback — not needed; Fiverr is best.
- Plan moved to `plans/completed/01-data-feasibility-pilot.md`.

**Scoping & Taxonomy — Complete:**
- 12-category taxonomy created in `data/task-taxonomy.md` (3 priority tiers).
- Benchmarks mapped per category with historical data sources verified.
- Related work drafted: ~4k words, 5 subsections, 30+ citations. Covers AI-labor, gig economy evidence, benchmarks, scaling laws, positioning table.
- 5 critique-and-improve iterations run. 18 reviewer simulation items in `tests/related-work.test.md`.
- Plan moved to `plans/completed/02-scoping-and-taxonomy.md`.

**Next:** Build scraping pipeline, collect benchmark histories, construct panel dataset.

## 2026-03-21 — Plans Restructured into Concrete Execution Plans

- Converted `paper-plan.md` → `plans/project-brief.md` (reference doc: positioning, structure, risks).
- Created two concrete execution plans:
  - `plans/active/01-data-feasibility-pilot.md` — Wayback Machine + Fiverr viability with clear pass/fail criteria and decision gate.
  - `plans/active/02-scoping-and-taxonomy.md` — task taxonomy, benchmark mapping, related work draft.
- Updated `plans/todo.md`: 2 active items linking to plans, backlog includes all draft sections.
- These two plans can run in parallel.

## 2026-03-21 — Paper Plan Drafted

- Created execution plan: `plans/active/paper-plan.md`.
- Analyzed model paper (GPTs are GPTs): identified strengths, gaps, and what we must exceed.
- Updated `tests/model-paper.test.md` with detailed benchmark comparison (10 dimensions).
- Plan has 6 phases: Scoping & Lit Review → Pilot → Full Data Collection → Core Analysis → Index & Forecasting → Paper Completion.
- Key innovation: price elasticity of intelligence (continuous, not binary exposure); longitudinal Fiverr data via Wayback Machine; forward-looking IPI under AI scaling scenarios.
- Key risk identified: Wayback Machine coverage — must pilot before committing to full collection.

## 2026-03-21 — Restructured docs and test infrastructure

- Decoupled `CLAUDE.md` into three files:
  - `CLAUDE.md` — agent philosophy and operating instructions only.
  - `setup.md` — agent bootstrapping and session-start checklist.
  - `README.md` — human-facing project overview and contributor guide.
- Restructured tests into three layers:
  - `tests/master.test.md` — cross-section quality criteria (applies to all sections).
  - `tests/<section>.test.md` — reviewer simulation only (removed model paper comparison from individual sections).
  - `tests/model-paper.test.md` — standalone model paper benchmark (replaces old `model-paper.md`).

## 2026-03-21 — Added Paper Test Infrastructure

- Added Philosophy #5: Paper test infrastructure with two lenses (reviewer simulation + model paper comparison).
- Created `tests/` directory with per-section test files (`*.test.md`) mirroring `drafts/sections/`.
- Created `tests/model-paper.md` for model paper analysis.
- Test files use PASS/FAIL/BLOCKED/N/A status for each critique and quality dimension.
- Clarified human workflow: user primarily edits plans, drafts, and test files; agents handle execution.

## 2026-03-21 — Added Plans Infrastructure

- Added Philosophy #4: Plans as first-class artifacts.
- Created `plans/active/`, `plans/completed/`, `plans/tech-debt-tracker.md`.
- Updated `CLAUDE.md` with plan file format, lifecycle (active → completed), and conventions.

## 2026-03-21 — Project Scaffolding

- Created `CLAUDE.md` with three core principles: minimize interruption, auditable progress, agile process.
- Set up drafts infrastructure: `drafts/main.md`, `drafts/sections/`, `drafts/render.py`.
- Created `progress.md` (this file) for reverse-chronological audit trail.
- Created project directories: `code/`, `data/`, `runs/`.
- Placeholder section files created for paper draft.
