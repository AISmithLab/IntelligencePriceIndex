# FAQ & Methodology — Draft Section

**Target file:** `docs/faq.html`
**Status:** draft for review (do NOT apply to the live HTML yet)
**Audience:** freelancers and buyers active on **Fiverr and Upwork**, plus researchers interested in AI's effect on the price of knowledge work.

This document holds the **full FAQ copy** for review before it goes into `docs/faq.html`.
All questions are given **in final reading order**. Questions added or substantially rewritten
**in this revision** are tagged **`[NEW]`** so the diff is obvious; previously-shipped questions carry no tag
(their answers may still have been edited to match the current chart — see the two facts below).

Two facts that shape several answers below (per current site state):

- **All prices are extracted with the Wayback Machine**, crawling archived Fiverr gig pages back to **~2011**.
- **The chart now plots the full quarterly series from 2020 Q1 → 2026 Q1** — **25 quarters**, with the index
  fixed at `100` in **2020 Q1**. Seven categories are shown (design, writing, marketing, coding, video, audio,
  translation). The pre-2020 archive exists but is too thin to chart; categories may still expand.

---

## Questions (final reading order)

### 1. What is the Intelligence Price Index?
The **Intelligence Price Index (IPI)** tracks the **revealed price of AI-exposed knowledge work** over time.
It is a matched-model price index built from the posted prices of freelance "gigs" on Fiverr — tasks like
logo design, copywriting, coding, voice-over, and video editing — that generative AI can increasingly perform.
The motivating question: as AI gets better at cognitive tasks, what happens to the market price of doing those
tasks? Rather than surveying experts, the IPI reads the answer directly off prices real sellers set and revise.
Built like the CPI, but the "basket" is cognitive labor instead of groceries and rent.

### 2. Who is this for?
The IPI is built for **people who work on or hire through freelance marketplaces — primarily Fiverr and Upwork —**
and for researchers tracking how AI is repricing knowledge work. If you sell logo design, copywriting, coding,
voice-over, translation, or video editing, the index is a read on where the *going rate* for your kind of task has
been heading. If you buy that work, it's a read on what you should expect to pay. The numbers are drawn from one
marketplace (Fiverr, see below), but the tasks priced are the same standardized gigs that dominate both platforms.

### 3. What does the headline number mean?
The big number is the **change in the composite index over the full charted period** — from the **2020 Q1** base
to the latest quarter (labelled **Δ'20–'26** on the page). Each category and the composite are set to `100` at the
base quarter, so a reading of, say, −5% means the selected basket of AI-exposed work is about 5% cheaper than at
the start of 2020. **Negative = deflation** (work getting cheaper — AI substitution pushes this way); **positive =
inflation** (general inflation, or AI complementing rather than replacing the worker). You can also read shorter
movements straight off the chart between any two quarters.

### [NEW] 4. What time period does the chart cover, and why does it start in 2020?
The chart plots the **full quarterly series from 2020 Q1 to 2026 Q1** — 25 quarters, with the index fixed at `100`
in 2020 Q1. The underlying archive reaches back to ~2011, but the chart **opens in 2020** for two reasons: (1)
coverage before 2020 is thin and uneven — too few matched gigs per quarter to draw a stable line; and (2) 2020
gives a clean **pre-generative-AI baseline** (ChatGPT launched November 2022) while keeping the window dense enough
to trust. Earlier history may be added as coverage improves. We show **quarters rather than months** because
quarterly buckets contain more matched gigs each period, so the series is far less jumpy than a monthly one.

### [NEW] 5. Is the effect of ChatGPT (or COVID) visible in the chart?
The window is deliberately drawn so you can look. ChatGPT launched in **November 2022 (2022 Q4)**, so the quarters
on either side of that line are the natural place to look for an AI-substitution signal in exposed categories like
writing and design. The chart also **opens during the COVID shock (2020–2021)**, which moved freelance demand for
its own reasons — so be careful reading the earliest quarters as an AI story. The IPI *shows* the price movement;
it does not, by itself, *prove* what caused any given move. Separating the AI effect from COVID, macro inflation,
and platform growth is exactly what the accompanying paper works on — see the limitations below.

### 6. What exactly is being priced?
The unit is a **gig**: a single, well-defined task offered at a posted price (e.g. "design a minimalist logo,"
"translate 500 words EN→ES"), at the **Basic** price tier. Three properties make these prices index-friendly:
**revealed not surveyed**, **standardized tasks**, and **matched over time** (a gig's price is only compared to
its own earlier price).

### [NEW] 7. How were the categories chosen, and what counts as "AI-exposed"?
The index currently tracks **seven categories** — design, writing, marketing, coding, video, audio, and
translation — chosen on two tests: the task is a **standardized, posted-price gig** that recurs across many
sellers (so it can be matched over time), and it is **plausibly AI-exposed** (something generative AI can
increasingly do or assist). Categories are assigned by classifying each gig from its archived page. Work that is
mostly manual, in-person, or not cleanly priced as a fixed gig — data entry, virtual assistance, admin support,
general "consulting" — is **not** tracked, because it either resists standardized pricing or isn't AI-exposed in
the same way. The category set is meant to grow; it is not a claim that these seven are the only AI-exposed work.

### 8. Where does the data come from?
Every price is a **real, historical Fiverr list price** recovered from the Internet Archive's **Wayback Machine**,
which has snapshotted Fiverr gig pages since ~2011. Nobody is surveyed and nothing is estimated. A multi-stage
pipeline narrows ~60M archived URLs → 22.7M unique snapshots → 48,643 longitudinal sellers → a stratified pilot
sample (500 sellers, 26,603 snapshots) → 22,632 downloaded pages → prices → a matched panel of gigs seen in ≥2
periods. Price extraction uses a four-method cascade (`packageList` JSON 72.9%, old-style JSON 15.2%, dollar
fallback 11.2%, HTML span 0.7%). This site uses the **full-history quarterly build** of that pipeline
(2020 Q1 → 2026 Q1).

### [NEW] 9. Why not just survey freelancers or use official wage data?
Surveys ask people what they *think* prices are doing; the IPI reads what sellers actually **posted**. Revealed
prices can't be colored by recall, sentiment, or who happened to answer. Official wage statistics (e.g. BLS series)
are real too, but they are **aggregated, lagged, and not broken out** by the specific AI-exposed gigs we care about
— you can't see the price of "a minimalist logo" or "500 words EN→ES" in them. Fiverr's posted, packaged prices
give exactly that: a **task-level list price you can match to its own past**, quarter after quarter. The trade-off
is coverage (one marketplace, posted not transacted), which we are upfront about in the limitations.

### 10. Why Fiverr — and what about Upwork?
Two practical reasons. **(1) Posted, packaged prices.** Fiverr gigs carry explicit, fixed price tiers
(Basic / Standard / Premium) that sellers set up front. That makes each gig a clean, comparable price point you can
track quarter to quarter — exactly what a price index needs. Upwork work is mostly negotiated hourly or
per-project, so there is no single posted "list price" to follow over time. **(2) A deep archive.** The **Wayback
Machine** has been snapshotting Fiverr gig pages since ~2011, giving a pre-generative-AI baseline; comparable
historical coverage of posted prices is much thinner elsewhere. We treat Fiverr as the *measuring instrument* for a
price that buyers and sellers on both Fiverr and Upwork care about. Extending coverage to other platforms is
future work.

### 11. How is the index calculated? (the formulas)
A **matched-model index** in three steps, recomputed live in the browser:
1. **Price relatives** — for each gig in two consecutive quarters, `r = p_t / p_{t−1}` (median Basic price per
   quarter; relatives outside `0.1–10×` dropped; ≥3 matched gigs needed per category-quarter).
2. **Category index (Jevons, chained)** — geometric mean of that quarter's relatives, chained onto the prior level;
   the base quarter (2020 Q1) is fixed at `100`.
3. **Composite (Törnqvist-style weighted geometric mean)** — `IPI_t = exp(Σ w_c · ln I^c_t / Σ w_c)`; only
   selected categories enter the sum.
4. **Headline change** — `(IPI_T / IPI_0 − 1) × 100%`, over the charted quarters (2020 Q1 → 2026 Q1).

### 12. Are these prices adjusted for general inflation?
**Not yet — the index is in nominal US dollars.** It tracks the actual posted price of a gig over time, with no
deflation by CPI or any other inflation measure. So a *positive* IPI reading does **not** automatically mean the
work got more expensive in real terms — part of any rise can simply be economy-wide inflation over the same window.
For the AI-substitution story, what's most telling is when gig prices fall (or rise more slowly than general
prices) *despite* a backdrop of broad inflation. A real (inflation-adjusted) version is a planned addition; until
then, read the headline as a **nominal** change and keep the macro backdrop in mind.

### 13. How are the category weights set?
Like CPI expenditure weights, IPI weights reflect each category's share of economic activity. We proxy transaction
volume with **review counts** (a gig accrues reviews roughly in proportion to sales): `w_c = R_c / Σ R_k`, where
`R_c = Σ_{i∈c} max_t reviews_{i,t}`. In the current sample, **design dominates (~71%)**, with writing (~11%) next
and marketing, coding, video, audio, and translation making up the rest.

### 14. Why geometric means instead of plain averages?
**Symmetry** — a price that doubles then halves nets to no change under a geometric (Jevons) mean; an arithmetic
mean would show a spurious increase. And **it is the BLS standard** for elementary CPI aggregates, keeping the IPI
comparable to how real inflation is measured.

### 15. Could a few sellers distort the index?
The design is fairly resistant to a handful of outliers. Three guards do most of the work: we only use **matched
pairs** (a gig's price vs. its own past, so new or vanishing sellers can't swing a level), we take a **geometric
mean** (which damps extreme relatives far more than an arithmetic mean), and we **drop relatives outside `0.1–10×`**
as data errors and require **≥3 matched gigs** before a category-quarter counts. No single seller's price change can
move a category much, and the composite further averages across categories. The bigger risk is *thin coverage*
(too few matches), which we flag in the limitations, not manipulation by any one seller.

### 16. Why can I switch categories on and off?
The composite is recomputed in your browser from the category indices and weights every time you change the basket,
using exactly the Step 3 formula renormalized over selected categories — so you can ask "what does the index look
like for just design and writing?" without trusting a server.

### [NEW] 17. Can I look up individual freelancers or a specific gig?
Yes. Beyond the composite chart, the site lets you drill into the **top freelancers within each category** and open
an **individual gig** to see its own posted price over time. This is the raw material the index is built from — a
matched gig is just one seller's price compared to its own earlier price — so the per-gig view is the most direct
way to sanity-check what the index is summarizing. It is also the quickest way to see why thinly-covered categories
can look flat: with few gigs archived per quarter, there simply aren't many lines to move.

### 18. What are the limitations and caveats?
- **Pilot scale** — a sample of sellers, not the full marketplace; indicative, not definitive.
- **Thin categories read flat** — sparse matched pairs can sit at `100` for stretches (missing matches, not real
  stability); the **earliest quarters** and the **smallest categories** (translation, audio) are most affected.
- **Design dominates** (~71% weight) — composite mostly follows design.
- **Posted, not transacted** — Basic-tier list prices, not final amounts paid.
- **Window starts 2020** — pre-2020 archive is too thin to chart, and the opening quarters overlap the COVID shock.
- **Survivorship and archiving gaps** — Wayback doesn't snapshot every page every quarter; dead gigs leave the panel.
- **Association, not proven causation** — attributing moves to AI specifically needs the paper's further analysis.

### 19. Can I reproduce this?
Yes. The series come from the panel/IPI build scripts in `code/` — the full-history quarterly build is
`code/18-build-site-data-long.py`, which serializes to `docs/data.json`; the page reads that file and recomputes
the composite client-side. Data contract and build steps are in `README.md` and `GUIDE.md`.

### [NEW] 20. How often is the index updated?
The series is **rebuilt from the archive rather than streamed live**, so it updates when we re-run the pipeline
against fresh Wayback Machine snapshots — not continuously. Each build stamps the page with a **generation date**
and the quarters it covers, so you can always see how current the shown series is. Because the newest quarter
depends on pages that have actually been archived and matched, the most recent point can shift slightly as more
snapshots land, and firms up as that quarter fills in.

### 21. Found an error, or want to contribute?
The project is open. Code, data-build scripts, and this page live at
**https://github.com/AISmithLab/IntelligencePriceIndex**. If you spot a misread price, a misclassified gig, or a
bug in the pipeline, please open an issue or a pull request there. Methodology suggestions are welcome too — the
index is meant to be auditable, and corrections from people who actually price this work on Fiverr and Upwork make
it better.

---

## Table-of-contents (final order, for whoever applies this to `faq.html`)

1. What is the Intelligence Price Index?
2. Who is this for?
3. What does the headline number mean?
4. **`[NEW]`** What time period does the chart cover, and why does it start in 2020?
5. **`[NEW]`** Is the effect of ChatGPT (or COVID) visible in the chart?
6. What exactly is being priced?
7. **`[NEW]`** How were the categories chosen, and what counts as "AI-exposed"?
8. Where does the data come from?
9. **`[NEW]`** Why not just survey freelancers or use official wage data?
10. Why Fiverr — and what about Upwork?
11. How is the index calculated? (the formulas)
12. Are these prices adjusted for general inflation?
13. How are the category weights set?
14. Why geometric means instead of plain averages?
15. Could a few sellers distort the index?
16. Why can I switch categories on and off?
17. **`[NEW]`** Can I look up individual freelancers or a specific gig?
18. What are the limitations and caveats?
19. Can I reproduce this?
20. **`[NEW]`** How often is the index updated?
21. Found an error, or want to contribute?

> The six `[NEW]` items are placed in reading-flow position (not appended at the end). Existing answers were also
> edited to match the current chart — **quarterly**, **2020 Q1 → 2026 Q1**, seven categories — so the whole file is
> consistent with the live `index.html` before it goes into `faq.html`.
