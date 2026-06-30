# FAQ & Methodology — Draft Section

**Target file:** `docs/faq.html`
**Status:** draft for review (do NOT apply to the live HTML yet)
**Audience:** freelancers and buyers active on **Fiverr and Upwork**, plus researchers interested in AI's effect on the price of knowledge work.

This document holds the **full FAQ copy** for review before it goes into `docs/faq.html`.
It contains the **10 existing questions** (unchanged, kept for continuity) followed by a
block of **proposed NEW questions**. New items are tagged **`[NEW]`** so the diff is obvious.

Two facts that shape several answers below (per current project scope):

- **All prices are extracted with the Wayback Machine**, crawling archived Fiverr gig pages across **2011–2026**.
- **The chart on the site is not finalized.** This first version plots only the **Feb 2025 → Feb 2026** window
  (a recent-window slice of the full 2011–2026 study). Categories shown are also provisional and will expand.

---

## Existing questions (unchanged)

### 1. What is the Intelligence Price Index?
The **Intelligence Price Index (IPI)** tracks the **revealed price of AI-exposed knowledge work** over time.
It is a matched-model price index built from the posted prices of freelance "gigs" on Fiverr — tasks like
logo design, copywriting, coding, voice-over, and video editing — that generative AI can increasingly perform.
The motivating question: as AI gets better at cognitive tasks, what happens to the market price of doing those
tasks? Rather than surveying experts, the IPI reads the answer directly off prices real sellers set and revise.
Built like the CPI, but the "basket" is cognitive labor instead of groceries and rent.

### 2. What does the headline number mean?
The big number is the **trailing-12-month change in the composite index**. Each category and the composite are
set to `100` at the start of the window, so a reading of −2.1% means the selected basket of AI-exposed work is
about 2.1% cheaper than twelve months earlier. **Negative = deflation** (work getting cheaper — AI substitution
pushes this way); **positive = inflation** (general inflation, or AI complementing rather than replacing the worker).

### 3. What exactly is being priced?
The unit is a **gig**: a single, well-defined task offered at a posted price (e.g. "design a minimalist logo,"
"translate 500 words EN→ES"), at the **Basic** price tier. Three properties make these prices index-friendly:
**revealed not surveyed**, **standardized tasks**, and **matched over time** (a gig's price is only compared to
its own earlier price).

### 4. Where does the data come from?
Every price is a **real, historical Fiverr list price** recovered from the Internet Archive's **Wayback Machine**,
which has snapshotted Fiverr gig pages since ~2011. Nobody is surveyed and nothing is estimated. A multi-stage
pipeline narrows ~60M archived URLs → 22.7M unique snapshots → 48,643 longitudinal sellers → a stratified pilot
sample (500 sellers, 26,603 snapshots) → 22,632 downloaded pages → prices 2011–2026 → a matched panel of gigs
seen in ≥2 periods. Price extraction uses a four-method cascade (`packageList` JSON 72.9%, old-style JSON 15.2%,
dollar fallback 11.2%, HTML span 0.7%). This site uses the **recent-window** slice of that pipeline.

### 5. How is the index calculated? (the formulas)
A **matched-model index** in three steps, recomputed live in the browser:
1. **Price relatives** — for each gig in two consecutive periods, `r = p_t / p_{t−1}` (median Basic price per
   month; relatives outside `0.1–10×` dropped; ≥3 matched gigs needed per category-period).
2. **Category index (Jevons, chained)** — geometric mean of that period's relatives, chained onto the prior level;
   first period fixed at `100`.
3. **Composite (Törnqvist-style weighted geometric mean)** — `IPI_t = exp(Σ w_c · ln I^c_t / Σ w_c)`; only
   selected categories enter the sum.
4. **Headline change** — `(IPI_T / IPI_0 − 1) × 100%`.

### 6. How are the category weights set?
Like CPI expenditure weights, IPI weights reflect each category's share of economic activity. We proxy transaction
volume with **review counts** (a gig accrues reviews roughly in proportion to sales): `w_c = R_c / Σ R_k`, where
`R_c = Σ_{i∈c} max_t reviews_{i,t}`. In the current sample, design dominates (~71%).

### 7. Why geometric means instead of plain averages?
**Symmetry** — a price that doubles then halves nets to no change under a geometric (Jevons) mean; an arithmetic
mean would show a spurious increase. And **it is the BLS standard** for elementary CPI aggregates, keeping the IPI
comparable to how real inflation is measured.

### 8. Why can I switch categories on and off?
The composite is recomputed in your browser from the category indices and weights every time you change the basket,
using exactly the Step 3 formula renormalized over selected categories — so you can ask "what does the index look
like for just design and writing?" without trusting a server.

### 9. What are the limitations and caveats?
- **Pilot scale** — a sample of sellers, not the full marketplace; indicative, not definitive.
- **Thin categories read flat** — sparse matched pairs can sit at `100` for stretches (missing matches, not real
  stability); quarterly figures are more robust.
- **Design dominates** (~71% weight) — composite mostly follows design.
- **Posted, not transacted** — Basic-tier list prices, not final amounts paid.
- **Survivorship and archiving gaps** — Wayback doesn't snapshot every page every month; dead gigs leave the panel.
- **Association, not proven causation** — attributing moves to AI specifically needs the paper's further analysis.

### 10. Can I reproduce this?
Yes. Series come from `code/14-recent-ipi.py`, serialized to `data.json` by `code/15-build-site-data.py`; the page
reads that file and recomputes the composite client-side. Data contract and build steps are in `README.md` and `GUIDE.md`.

---

## Proposed new questions `[NEW]`

> Placement note: insert these into `docs/faq.html` and the table-of-contents in the order shown below.
> Suggested positions are noted on each item. None of these touch category definitions (deferred to a later version).

### `[NEW]` A. Who is this for? — *(suggested: new #2, right after "What is the IPI?")*
The IPI is built for **people who work on or hire through freelance marketplaces — primarily Fiverr and Upwork —**
and for researchers tracking how AI is repricing knowledge work. If you sell logo design, copywriting, coding,
voice-over, translation, or video editing, the index is a read on where the *going rate* for your kind of task has
been heading. If you buy that work, it's a read on what you should expect to pay. The numbers are drawn from one
marketplace (Fiverr, see below), but the tasks priced are the same standardized gigs that dominate both platforms.

### `[NEW]` B. Why Fiverr — and what about Upwork? — *(suggested: after "Where does the data come from?")*
Two practical reasons. **(1) Posted, packaged prices.** Fiverr gigs carry explicit, fixed price tiers
(Basic / Standard / Premium) that sellers set up front. That makes each gig a clean, comparable price point you can
track month to month — exactly what a price index needs. Upwork work is mostly negotiated hourly or per-project,
so there is no single posted "list price" to follow over time. **(2) A deep archive.** The **Wayback Machine** has
been snapshotting Fiverr gig pages since ~2011, giving a pre-generative-AI baseline; comparable historical coverage
of posted prices is much thinner elsewhere. We treat Fiverr as the *measuring instrument* for a price that buyers
and sellers on both Fiverr and Upwork care about. Extending coverage to other platforms is future work.

### `[NEW]` C. Are these prices adjusted for general inflation? — *(suggested: after the formulas, before "weights")*
**Not yet — the index is in nominal US dollars.** It tracks the actual posted price of a gig over time, with no
deflation by CPI or any other inflation measure. So a *positive* IPI reading does **not** automatically mean the
work got more expensive in real terms — part of any rise can simply be economy-wide inflation over the same window.
For the AI-substitution story, what's most telling is when gig prices fall (or rise more slowly than general
prices) *despite* a backdrop of broad inflation. A real (inflation-adjusted) version is a planned addition; until
then, read the headline as a **nominal** change and keep the macro backdrop in mind.

### `[NEW]` D. What time period does the chart cover right now? — *(suggested: near "What does the headline number mean?")*
The full study spans **2011–2026**, but **this first version of the chart plots only Feb 2025 → Feb 2026** — a
recent 12-month window — so the headline reads like a "past year" figure. The chart, its categories, and its window
are **not finalized**: expect more history, more categories, and refinements in later versions. Treat the current
view as a working preview, not the final series.

### `[NEW]` E. Could a few sellers distort the index? — *(suggested: after "Why geometric means")*
The design is fairly resistant to a handful of outliers. Three guards do most of the work: we only use **matched
pairs** (a gig's price vs. its own past, so new or vanishing sellers can't swing a level), we take a **geometric
mean** (which damps extreme relatives far more than an arithmetic mean), and we **drop relatives outside `0.1–10×`**
as data errors and require **≥3 matched gigs** before a category-period counts. No single seller's price change can
move a category much, and the composite further averages across categories. The bigger risk is *thin coverage*
(too few matches), which we flag in the limitations, not manipulation by any one seller.

### `[NEW]` F. Found an error, or want to contribute? — *(suggested: last, after "Can I reproduce this?")*
The project is open. Code, data-build scripts, and this page live at
**https://github.com/AISmithLab/IntelligencePriceIndex**. If you spot a misread price, a misclassified gig, or a
bug in the pipeline, please open an issue or a pull request there. Methodology suggestions are welcome too — the
index is meant to be auditable, and corrections from people who actually price this work on Fiverr and Upwork make
it better.

---

## Table-of-contents changes (for whoever applies this to `faq.html`)

Existing TOC has 10 entries. With the new questions inserted in the suggested positions, the renumbered list is:

1. What is the Intelligence Price Index?
2. **`[NEW]`** Who is this for?
3. What does the headline number mean?
4. **`[NEW]`** What time period does the chart cover right now?
5. What exactly is being priced?
6. Where does the data come from?
7. **`[NEW]`** Why Fiverr — and what about Upwork?
8. How is the index calculated? (the formulas)
9. **`[NEW]`** Are these prices adjusted for general inflation?
10. How are the category weights set?
11. Why geometric means instead of plain averages?
12. **`[NEW]`** Could a few sellers distort the index?
13. Why can I switch categories on and off?
14. What are the limitations and caveats?
15. Can I reproduce this?
16. **`[NEW]`** Found an error, or want to contribute?

> Ordering is a suggestion; the new copy is self-contained and can be reordered without rewrites.
> Per current scope, **no category-definition question is included** — deferred until the chart's categories are finalized.
