# Progress Log

## 2026-08-20 (evening, latest) — A volume card with no price index in it

`code/62-category-accrual.py` (new `pooled` series), `docs/data.json`,
`docs/index.html`, `docs/ipi.js` (`drawVolume`). From a user correction:
**"but I'm trying to look at just the volume of transactions."**

### The confusion was ours, not theirs

Every quantity on the site went through the IPI. That is defensible for the
implied order count — Fiverr reports dollars and never an order count, so
`orders = GMV / price` is the only way to manufacture one — but it meant a
reader asking for *volume* was handed a quotient whose denominator is a price
index, then a five-step explanation of how the index is built. The price index
was never needed for the question that was asked.

**Two of the project's three volume measures never touch a price**, and neither
was on the site as such:

| measure | source | price involved |
|---|---|---|
| review accrual | archived pages, counted | **none** |
| active buyers | Fiverr Inc., reported | **none** |
| implied orders | GMV ÷ IPI | yes — the whole construction |

### The card

Placed **first**, above the implied-order card, because it is the direct answer
and everything below it is derived from something. Pooled review accrual
(quarterly, archive) and active buyers (annual, Fiverr Inc.), both indexed
2020 = 100 so they share **one axis** — the mixed cadence is legitimate only
because of the shared base, and buyers carries open annual markers so its grain
is visible rather than implied. Peak 2020Q3 at 109.3, the 2021Q3 step, the
2023Q4 step, ending at **36.8**.

`pooled` is **equal-weighted across the seven categories, not review-weighted** —
review weight *is* the outcome here, and weighting by it would let the largest
category set its own denominator. It is computed in step 62 rather than in the
browser so the definition lives with the data.

### What the card says it is not

Neither series is an order count, and the card says so in its own text: accrual
is per **surviving** listing and the archive cannot measure exit (`n_404 = 0`
across 509,339 captures), so it will not scale to a platform total; buyers
counts **people**, and spend per buyer nearly doubled over the window. The route
to an actual count is the dated order records still unextracted in the archived
HTML — `encrypted_order_id` + `created_at`, no price required — which remains
PRIORITY 1b.


## 2026-08-20 (evening, later) — The per-category sales proxy, finally as a series

`code/62-category-accrual.py` -> `runs/category-accrual.out`,
`data/pilot/category-accrual.csv`. From a user question: "across the categories,
what do the number of transactions look like over time". Step 46 had estimated a
per-category **break** at 2022Q4 and never written the series it broke; Fiverr Inc.
publishes no category split at all, so per-gig review accrual is the only route.

### What the series shows that the break table could not

| category | peak | 2021Q2 | 2021Q3 | 2022Q4 | 2024Q4 |
|---|---|---:|---:|---:|---:|
| audio | 2020Q3 | 103.9 | 78.9 | 73.6 | 43.9 |
| coding | 2020Q3 | 89.4 | 76.5 | 68.9 | 31.8 |
| design | (2019Q3) | 97.4 | 72.8 | 71.4 | 32.6 |
| marketing | 2020Q3 | 95.7 | 80.3 | 83.7 | **47.3** |
| translation | 2020Q3 | 98.9 | 85.5 | 80.0 | **48.5** |
| video | 2020Q3 | 91.3 | 71.0 | 64.1 | 30.0 |
| writing | 2020Q3 | 97.5 | 76.3 | 67.8 | **23.7** |

Three things the single break estimate hid:

1. **Six of seven peak in the same quarter, 2020Q3**, and the one exception
   (design, 2019Q3) sits in the thin early stretch. The fall is not gradual — it
   is a **step between 2021Q2 and 2021Q3**, simultaneous in all seven, fifteen
   months before ChatGPT.
2. **2022Q1-2023Q3 is a plateau, and ChatGPT lands inside it.** Five of seven
   categories are *higher* in 2023Q3 than in 2022Q3; design rises 67.2 -> 83.8
   across the whole period the AI story would have it falling. The second real
   step down is **2023Q4**.
3. **The end-state ordering contradicts exposure more sharply than step 46 did.**
   The two most AI-exposed categories finish at opposite ends: writing worst at
   **23.7**, translation second-best at **48.5**. An exposure story has to explain
   both with the same mechanism, and it cannot.

### On the website, as small multiples — and why not seven overlaid lines

`docs/data.json` (new `category_transactions`, written by step 62's
`write_site_block` — same arrangement and same warning as step 47's block: **step
18 writes data.json whole, so rerunning it drops this**), `docs/index.html`,
`docs/ipi.js` (`drawCategoryTx`). From a user instruction: "plot the transaction
trends across categories on the website".

The first attempt was seven overlaid lines in the site's existing category
palette. It was abandoned on a measurement, not a preference: those seven colours
fail a colour-vision-deficiency check on all 21 pairs — worst CVD pair
translation/audio at **ΔE 6.1 (deutan)**, and translation/video at **ΔE 13.2 for
normal vision**, below the 15 floor, meaning hard to separate even with full
colour vision. No re-stepping of seven hues cleared it; three attempts all failed
at least one pairwise check, which is the known ceiling for seven categorical
slots under all-pairs CVD.

**Faceting removes the problem at its source** — one series per panel, identity
carried by the panel title, hue reduced to decoration. It also happens to be the
better chart for this finding, because the finding is "they move together, then
separate at the very end": a ghost of the all-category mean sits behind every
panel so both halves of that sentence are readable at a glance. Shared y-scale
across panels, the thin 2018Q4–2019Q3 stretch shaded rather than dropped, 2021Q3
and 2022Q4 marked, per-panel hover carrying the raw rate, the cell count and the
capture span, and a full table underneath.

The palette defect is **not** fixed — it still affects the hero price chart,
where seven lines are overlaid and hue is the only identity cue. Filed as
`plans/tech-debt-tracker.md` **TD2** rather than repainted, because the
category→colour map is used in the sparklines and freelancer panels too and that
is a site-wide change the user did not ask for.

### Identification, stated in the script rather than discovered later

Within a gig, age and calendar quarter move one-for-one, so gig FE + age FE +
quarter FE is exactly collinear in its linear part — the age-period-cohort
problem. **The shape is identified; the trend is not.** Sections B and C are
labelled accordingly, and the peak quarter is singled out in section D as the one
statistic that survives it. A capture-span diagnostic (A0) was added for the same
reason: mean quarters-per-observation widens **1.2 -> 1.75** across the window, so
part of the 2024 fall is the archive capturing gigs less often, not the market.

Base is the **2020 four-quarter mean**, not a single quarter: 2018Q4-2019Q3 hold
4.1k-5.9k observations against 9k-11k later and the raw rates swing sixfold across
them, so any one early quarter would have set every later level by its own noise.
2020 = 100 also matches step 47's platform series, so the two read together.

No paper section, figure or frozen number touched. The series is descriptive and
is not a demand series — review-propensity drift (Phase 1) is still untested.


## 2026-08-20 (evening) — The transaction count got a chart, and the website got the chart

`code/34-figures.py` (new `fig6`, plus a named runner), `code/47-fiverr-inc-external.py`
(new `write_site_block`), `docs/data.json`, `docs/index.html`, `docs/ipi.js`,
`outputs/figures/fig6-transactions.svg`. From a user instruction: "make a chart
that shows the number of transactions over the time range on ipi", then "add it
to the website".

### What the chart plots, and why it plots three lines

The project has exactly one transaction-count series: `orders = real GMV / real
IPI price`, from step 47. It is a **quotient**, and the interesting thing about
it is that the numerator did not fall — real GMV is **+11.3%** against 2020
while the real price is **+35.8%**, which is the whole of the **-18.0%** in
orders. A single line would have hidden that, so the figure draws all three,
indexed to 2020 = 100. Same base, so one axis — never two scales.

| year | real GMV | real price | implied orders |
|---|---:|---:|---:|
| 2020 | 100.0 | 100.0 | 100.0 |
| **2021** | 139.3 | 104.5 | **133.4 (peak)** |
| 2022 | 137.9 | 112.3 | 122.8 |
| 2023 | 138.5 | 125.5 | 110.3 |
| 2024 | 128.3 | 130.0 | 98.7 |
| 2025 | 121.8 | 136.2 | 89.5 |
| 2026 (TTM Q2) | 111.3 | 135.8 | **82.0 (-38.6% from peak)** |

Annual, because Fiverr reports GMV annually; the archive supplies the price.
The ChatGPT marker sits at 2022Q4, **after** the 2021 peak, which is the point.

### Two structural notes worth remembering

- **`write_site_block` lives in step 47, not step 18.** The series is a quotient
  of step 18's index and Fiverr's reported GMV, so it can only be formed once
  `data.json` exists. The consequence: **rerunning step 18 silently drops the
  block** (it writes `data.json` whole), and the site card then hides itself
  rather than erroring. Rerun 47 after 18.
- **Step 34 now takes figure names.** `python3 code/34-figures.py fig6`
  regenerates one figure without paying for figure 4's subsampling curve. No
  argument still builds all six.

### The website card

A second card under the hero chart: legend, line chart with a crosshair
tooltip carrying buyers and spend-per-buyer, a full data table underneath (the
table is the accessibility route, not an extra), and four bullets that state
the upper-bound caveat and the timing. Series colours are a three-hue set run
through a colour-vision-deficiency validator — worst adjacent pair dE 20.0, all
six checks pass — rather than picked by eye.

### What it does not do

No new estimate. Every number is step 47's, unchanged. The card says in its own
text that nothing here identifies a cause, because a chart with a ChatGPT line
on it invites exactly that reading.


## 2026-08-20 (later still) — The plain summary was still assuming finance vocabulary

`drafts/plain-summary.md`, `tests/structure-master.test.md`. From two user
questions in succession: **"what does GMV mean"** and **"when you say buyers
decreased 36 percent, do you mean transactions or revenue? I am confused."**

Both landed on a document published the same day whose entire purpose was to be
readable without jargon. The readability pass had glossed every *econometrics*
term — searched break, placebo, parallel trends, fixed effects — and left the
*finance* terms untouched, because GMV and active buyers did not read as jargon
to the person writing them. They are.

### The specific defect

The document reported three quantities in one table (`buyers`, `spend per
buyer`, `GMV`) and used a fourth word for them collectively (`transactions`),
with no statement that these are different things. A reader who takes "buyers
−36%" as a statement about sales volume has been misled by the document, not by
their own inattention. **Buyers is a headcount of people.** Fiverr does not
publish an order count at all.

### What was added

- **"Six words that get mixed up"**, placed before the "during" correction:
  buyers (people), orders (purchases — *published by nobody*, estimated here),
  GMV (dollars transacted), revenue (Fiverr's cut, roughly a third of GMV),
  review accrual (our sales proxy), listed vs realised price. With the two
  consequences that matter: **GMV = buyers x spend per buyer is arithmetic, not
  an estimate**, which is how a third of the buyers can leave while the dollars
  barely move; and **every transactions-fell claim in the document is derived**,
  from GMV ÷ a price or from review accrual.
- **§2.2 spells GMV out on first use** and states plainly that it is not
  revenue, with the column headers glossed inline.
- **The implied order count now appears in the document** — −18% vs 2020,
  −38.6% from the 2021 peak, with its upper-bound caveat. The glossary promised
  an estimate the document did not contain.
- "Buyers −36%" restated as **1.5 million people who used to buy here and no
  longer do**, because the percentage alone does not read as people.

`tests/structure-master.test.md` **U7**. Re-rendered; the published artifact
carries the same glossary.

### The lesson worth keeping

The readability pass audited for terms *the writer* found technical. The terms
that actually broke were the ones the writer had stopped seeing. Any future
plain-language pass should be checked by asking what a reader would have to
already know, not by scanning for words that look specialised.

## 2026-08-20 (later) — A plain-language summary of the whole project, and the "during" correction

`drafts/plain-summary.md` (19.3k chars), `tests/structure-master.test.md`.
From a user instruction: "make a summary similar to market-structure-answer
summarizing the data you collected and the findings," stated alongside the
user's own reading — **"prices rose during AI launches but transactions
decreased."**

### The document

A standalone non-technical companion to `drafts/market-structure-answer.md`.
Same numbers, no econometrics vocabulary, and structured so the data collection
comes *before* the findings — which the answer doc never does, because it was
written for a reader who already knew where the panel came from.

| part | contents |
|---|---|
| short version | five bullets; prices up, business down, AI present, turns predate it |
| **the "during" correction** | placed before Part 1, not inside the attribution section |
| Part 1 | the archive (60.0M CDX rows → 509,339 captures → ~375,000 pages → 86 GB), the three datasets built from it, the four outside sources, and §1.4 on the order records the extractor was discarding |
| Part 2 | eight findings: price level and what it is made of, Fiverr Inc.'s quantities, the five failed commoditisation predictions, AI diffusion dated to 2023Q1, the six turns in 2020Q3–2021Q4, the twenty-launch before/after test, the positive control, and why nine designs failed |
| Part 3 | five limits, led by "we cannot say AI caused any of this" and "all of this ends at 2024Q4" |
| Part 4 | the four things that would change the answer |
| provenance | every finding mapped to its section in the answer doc and its script |

### The correction, which is the reason the document leads with it

The user's reading is **right in both directions** — prices rose, transactions
fell, and both happened across the launch years. The equivocation is on
**"during"**: the *level* movements span the AI period, but every *turning
point* the project can date lands in **2020Q3–2021Q4**. A decline already
underway that continues through the AI years is not a decline that began with
them, and from a distance the two are indistinguishable — which is the honest
explanation for why the project has needed nine designs and this many steps.

Stating it up front rather than in §4 is a deliberate departure from the answer
doc's ordering. A reader who arrives with the AI hypothesis will otherwise read
Parts 1 and 2 as confirmation of it.

### Three figures corrected in drafting

- pages downloaded stated as **~375,000** (291,997 balanced + 67,377 expanded +
  15,150 recent), not the 384,983 gig-date *observations* — different quantities.
- realised-price bands recomputed from the §1.3 table: **$50–200 = 67.3%**,
  **>$200 = 31.7%** (had written 67.4/31.6).
- design count stated as **nine run, nine failed (1–8 and 10)**. Design 9 is
  pre-registered and has never been estimated, and design 10's *demand* half was
  discarded on its own placebo rather than failing — an easy conflation.

### Tests

`structure-master.test.md` **U5** records the summary instruction, **U6** the
"during" correction. Both PASS. M9's split verdict is unchanged: the plain-language
criterion now passes in two documents and still fails in `drafts/structure/`.

### What this does not do

It is a companion, not a replacement, and it is not in the paper tree. No number
moved; no claim was strengthened. The seven-section tree still carries neither
the plain-language pass nor the realised-price finding.

## 2026-08-20 — The answer document rewritten: what buyers paid folded in, and the jargon glossed

`drafts/market-structure-answer.md` (59,680 → 72,882 chars),
`tests/structure-data.test.md`, `tests/structure-master.test.md`,
`plans/todo.md`. From a user instruction: "revise market-structure-answer.md,
make the wording easy to understand and clearly explain findings." Two jobs in
one pass — fold in step 59's realised-price finding, and make the document
readable by someone who does not already know what a searched break is.

### Job 1 — step 59 written in, and one claim retracted

| section | what changed |
|---|---|
| header | new 2026-08-20 revision note leading the file |
| §0 | new paragraph: buyers were not paying the advertised price; the "orders −18%" row now carries its own caveat inline |
| **§1.3** | retitled *"What 'price' means here — and what buyers actually paid"* and rewritten from a 6-line caveat to a full subsection with the paid-amount distribution, the three limits, and the scale if built |
| §2 | heading was **"the only real transaction data in the project"** — no longer true, so it is now "where the transaction numbers come from" with three sources distinguished; point 2's upper bound is now measured rather than assumed |
| **§5** | the entry **"Realised order value — not measurable at any effort"** struck through and marked *wrong*, with the genuinely unmeasurable part (pre-2022 history) named in its place |
| §6 | re-extraction inserted as item 2, items 2–5 renumbered to 3–6 |
| §7 | three rows added to the reader's guide, including one for what is still **not** measurable |
| §8 | `code/59-review-order-audit.py` added to provenance |

The §5 retraction is the part worth flagging. A section titled *what is not
measurable at any effort* had an entry in it that was measurable from data
already on disk. The strike-through stays rather than a silent delete.

### Job 2 — the readability pass

The document was written for someone who already knew the methods. Three
additions, no numbers touched:

1. **A "How to read this document" glossary** before §0 — thirteen terms in
   plain language (listed vs realised price, real vs nominal, matched-model,
   balanced panel, fixed effects, break, **searched** break, placebo, parallel
   trends, exposure, MDE, Gini, gate), closing with the two conventions that
   carry the argument: break dates are searched not assumed, and every promising
   result is gated on a placebo before it is reported. That second line explains
   in advance why the document contains more failed designs than findings.
2. **"In plain terms:" glosses** at the five densest results — §3's balanced-panel
   rationale, §3.4's Gini-vs-dormancy distinction, §4.3's age-period-cohort
   paragraph (why only *bends* are reported and never slopes), §4.4.1's
   "effective number of treated clusters is one", and §4.5's underpowered window
   (*"not a clean bill of health, a blurry photograph"*).
3. **§4 now opens by explaining what an identification design is** and what it
   means for one to *fail* — four concrete failure modes named — so the
   nine-designs-nine-failures table reads as a result rather than as a list of
   defeats. First-use glosses added for GEKS-Jevons, downward nominal rigidity
   and review-propensity drift.

### Tests

- `structure-data.test.md` **R4** ("listed prices are not transaction prices")
  strengthened from asserted to measured; **R8** added and recorded **FAIL** —
  the display-selection threat, open; **R9** added, PASS — why the index is still
  built on listed prices.
- `structure-master.test.md` **U4** records the readability instruction;
  **M9** added as a standing criterion and deliberately split: **PASS in the
  answer doc, FAIL in `drafts/structure/`.**

### What this does not do

The seven-section paper tree in `drafts/structure/` is untouched. It carries
neither the realised-price finding nor the plain-language pass, and it still
states the scope as six designs. Both are now Active items in `plans/todo.md`.

## 2026-08-20 — What buyers actually paid is in the archive, and the extractor was discarding it

`code/59-review-order-audit.py` -> `runs/review-order-audit.out`. From a user
question: "is there a way to track what buyers paid? Or can we only look at
listing price?" The answer to the second half is **no** — the pages carry
order-level realised amounts and nothing downstream of
`code/09-extract-prices.py` has ever read them.

### What the pages actually hold

Fiverr gig pages embed a JSON `reviews` object. Each review is an **order
record**:

| field | what it gives |
|---|---|
| `encrypted_order_id` | unique order key — dedupes across captures |
| `created_at` | **order date**, not capture date |
| `price_range_start` / `_end` | **what the buyer paid**, bucketed |
| `value` | order rating |
| `repeat_buyer`, `is_business` | buyer type |
| `reviewer_country_code`, `reviewer_industry` | buyer geography and sector |

The extractor keeps `price_basic/standard/premium`, `title`, `rating`,
`review_count` and nothing else. The 86 GB of stored HTML is unchanged, so this
needs **no new collection** — it is a re-extraction.

### Result 1 — realised order value is several times the listed price

| bucket | share | cum |
|---|---:|---:|
| $5–20 | 0.2% | 0.2% |
| $20–50 | 0.9% | 1.0% |
| **$50–100** | **37.5%** | 38.6% |
| **$100–200** | **29.8%** | 68.4% |
| $200–400 | 16.9% | 85.3% |
| $400–600 | 6.2% | 91.5% |
| $600–10000+ | 8.5% | 100.0% |

**Orders under $50 are 1.0% of all orders.** The IPI's listed basic-package
median is ~$25–30. §1.3 of `drafts/market-structure-answer.md` conjectured that
buyers buy up-tier and that realised prices therefore rose faster than the IPI;
that is no longer a conjecture. It also means **every quantity figure derived by
dividing GMV by the IPI is deflating by the wrong price** — the §2 "orders
−18.0%" is built on a denominator that is not what buyers paid.

### Result 2 — §5's "not measurable at any effort" entry is wrong

`drafts/market-structure-answer.md` §5 lists **realised order value** as
unmeasurable on this data. It is measurable, 2022 onward, at order level, dated
by order. That entry must be revised.

### Result 3 — three limits, and they are what gate any use

1. **Starts 2022.** `price_range_start` is absent from every 2018–2021 capture
   (0.0–0.8% of sampled pages) and appears at 64.2% in 2022. Pre-2022 *orders*
   do carry prices when served by a 2022+ page (2020: 58.1%, 2021: 22.9%), but
   displayed reviews skew recent, so the pre-ChatGPT baseline is **roughly one
   year and back-filled** — enough for a level comparison, not for the long-run
   diffusion question the listed-price index answers.
2. **~13% of orders recovered, and selected.** A page shows **4.2 reviews
   against a median gig `total_count` of 168**. Pooling repeat captures of the
   same gig accumulates distinct order ids — on a **59-gig pooling subsample**
   the median is **41 orders per gig** (9,783 gigs have the ≥8 captures in 2022+
   that make pooling worthwhile) — but that is **13.1% of the new orders
   implied by `total_count` growth**. Displayed reviews are ranked by
   `relevancy_score`, **not sampled at random**. This is the central threat and
   needs its own test before any index is built. The weaker check that could be
   run now passes: priced and unpriced reviews are close on rating (4.877 vs
   4.879), repeat-buyer share (39.1% vs 35.9%) and business share (9.3% vs
   7.0%), so the *price field* is not obviously missing selectively — which says
   nothing about which orders are *displayed*.
3. **Interval-censored.** Amounts are buckets with an open top ($10000+), so any
   index needs interval regression or midpoint imputation, not a mean.

### Scale, on the pilot's own numbers

53,855 gigs indexed across 361,760 captures; 9,783 have ≥8 captures in 2022+,
and the 59-gig pooling subsample gives a median 41 distinct orders each at ~55%
priced. Extrapolated, that is an order of **10^5 dated, priced transactions** — the first real transaction-level data in the project.
`review_count` has been a proxy for sales since step 24; this would replace it
with orders.

### Outputs

- `code/59-review-order-audit.py`, `runs/review-order-audit.out`
- No draft changes yet — §1.3, §2 and §5 of
  `drafts/market-structure-answer.md` all need revision and are tracked in
  `plans/todo.md`

## 2026-08-20 — Design 10: twenty named AI launches at monthly resolution, and a placebo that throws half of it away

`code/58-ai-launch-events.py` -> `runs/ai-launch-events.out`;
`code/58b-launch-placebo.py` -> `runs/ai-launch-placebo.out`. From a user
question: "look at specific important dates related to AI launches and compare
before and after -- or did you do that already?" Honest answer was **no, not
properly**. Steps 52/55/57 *searched* for breaks and ranked milestones by fit;
none compared before against after at a named date, and all three ran quarterly.

### Three things this adds

1. **Monthly.** `month` was on every row and no prior test used it. A quarterly
   test smears a launch across up to three months.
2. **Twenty named launches**, dated by **public availability**, not announcement
   -- an announcement cannot change a gig.
3. **Per-tool target category** as treatment (Copilot->coding,
   ElevenLabs->audio, Midjourney->design, ChatGPT->writing+translation,
   Runway/HeyGen/Veo->video, Suno->audio), non-targets as controls. Needs no
   exposure score at all, so it escapes the Eloundou measure entirely.

Every estimate gated on a 12-month pre-window placebo, because steps 52/55
established these series were already bending from 2020Q3.

### Result 1 — the PRICE margin is valid, and it is null

| verdict | n | which |
|---|---:|---|
| confounded, pre-window also significant | 7 | all five image-model dates, Copilot, GPT-4o |
| null | 11 | ElevenLabs, GPT-4, Runway, HeyGen, Suno x2, Sonnet 3.5, FLUX, Veo 2, GPT-3 GA, R1 |
| clears the gate | 2 | GPT-3 API (-3.3%), ChatGPT (-2.0%) |

**Two survivors is FEWER than chance predicts** (~60 tests at 5% gives ~3). And
GPT-3's API date is 2020-06, the pandemic inflection step 52 already flagged as
fitting with the wrong sign.

The image models are the cleanest illustration of the project's recurring
finding: design prices fall -4.5% to -5.1% (t -4.9 to -5.6) at every image date,
and **every one has a LARGER pre-window effect** (t -5.3 to -7.1).

### Result 2 — the DEMAND margin is discarded, on its own placebo

It returned **11 of 20 significant** where chance predicts one, with incoherent
signs: image tools raising design accrual (+5.4% to +9.6%) while text tools cut
writing's (-6.7%, -9.0%). That is not a story, it is a symptom.

Step 58b ran the identical design on **12 fake launches, 2019-03 to 2020-02**,
each given the same target categories a real launch used. No generative-AI tool
existed for any of them.

| outcome | placebo false-positive rate | nominal | verdict |
|---|---:|---:|---|
| price | **1 of 12 = 8%** | 5% | at size; the price null stands |
| demand | **9 of 12 = 75%** | 5% | **fires at arbitrary dates; DISCARDED** |

**The eleven demand results are reported nowhere.** Writing them up and then
running the placebo would have been the wrong order; running the placebo first
is why they never entered the draft.

### Result 3 — the design's own premise failed, and that is the informative part

The first stage asks whether a launch moved AI *adoption* in its target
category. **It rejects the targeting assumption.** ChatGPT produced no
differential adoption in writing or translation; AI branding rose platform-wide
and concentrated in **coding** regardless of which tool launched.

This is what step 57 predicts -- diffusion came through **entry**, not incumbent
conversion in exposed categories -- and it is the deepest diagnosis yet of why
designs 1-8 failed: **they looked for AI's effect inside the categories a
crosswalk called exposed, and that is not where AI arrived.**

Two caveats recorded rather than buried. The first stage clusters on **seven
categories**, the same defect that killed design 7 at step 54's gate A, so only
its direction is read. And launches sit 1-3 months apart, so each pre-window
contains other launches; effects cannot be separated within the 2022-23 cluster.

### Outputs

- `code/58-ai-launch-events.py`, `runs/ai-launch-events.out`
- `code/58b-launch-placebo.py`, `runs/ai-launch-placebo.out`
- `drafts/market-structure-answer.md`: new **4.3.2**, design table extended to 10,
  section 4 retitled to nine designs run, three new reader's-guide rows,
  provenance updated

## 2026-08-19 — Step 57: generative AI is measured inside the market for the first time, and it supplies the positive control the whole identification argument was missing

`code/57-ai-diffusion-titles.py` -> `runs/ai-diffusion-titles.out`,
`data/pilot/ai-title-flags.csv`. No new data collected. The user asked to answer
the standing question on data already held; the answer to "what is held that no
design has used" turned out to be **`title`, present on 384,967 of 384,983
gig-date observations (100.0%)**.

### The gap this closes

Designs 1-8 all proxied AI with something **external** to the market: an
Eloundou occupation score (thin, 36.8% zero-match, varies over 7 categories) or
a release date (a guess about when the technology mattered here). The project
has never had a diffusion measure taken from inside the market. Sellers who use
generative AI advertise it, so the AI-branded share of listings is one.

### The classifier, and the three guards that were needed

Two series: `AI_GEN` (generative-specific) and `AI_ANY` (includes the
pre-generative chatbot/ML-annotation trade). Guards, each added after auditing
flagged titles rather than anticipated:

1. **`.ai` is the Adobe Illustrator file extension.** "convert any file to vector
   ai, eps, svg" is a design gig. Largest source of pre-2022 hits before the guard.
2. **"Synthesia" is both the AI-video platform and piano-tutorial software.**
3. **"real human traffic" is SEO bot-traffic language**, not an anti-AI claim;
   "humanize your brand with animation" (2018) is not one either.

Prefix `<seller>: ` and suffix ` for $X on fiverr.com` are stripped first, or any
seller with "ai" in the handle reads as an AI gig in every quarter since 2019.

**Realised precision floor: 7 distinct `AI_GEN` titles across all of 2019-2021**,
six of them genuine pre-generative AI work. ~0.02% of observations against a
post-2023 level 25-60x higher.

### Result 1 — the diffusion curve is sharp and it breaks at 2023Q1

| quarter | AI share, all listings | share of NEW listings ever AI-branded |
|---|---:|---:|
| 2019Q1-2022Q2 | 0.01-0.03% | 0.00-0.40% |
| 2022Q4 (ChatGPT) | 0.04% | 0.50% |
| **2023Q1** | **0.48%** | **5.98%** |
| 2023Q3 | 1.20% | 3.85% |
| 2026Q1 | 1.86% | - |

Twelvefold in one quarter, on the entry-cohort series, which is the clean one
(the flow, not the stock, so panel composition cannot drive it). The measure is
biased **against** this: "ever AI-branded" gives early cohorts more quarters in
which to be flagged.

### Result 2 — THE POSITIVE CONTROL. The timing machinery is not blind.

The strongest available objection to steps 52/55 was never answerable: *if your
searched-break procedure never finds ChatGPT, maybe it cannot find anything.*
The identical search - same grid, same level-and-slope break, same SSR ranking -
run on the diffusion series:

| series | best break | ChatGPT rank | SSR spread |
|---|---|---|---|
| within-gig transaction proxy (step 52) | 2020Q4 | 11 of 15 | - |
| cheap-end relative performance (step 55) | 2020Q3 | 16 of 17 | 0.06% |
| **AI-branded share of new listings** | **2023Q1** | **1 of 19** | **227%** |
| AI-branded share of standing stock | 2023Q2 | 4 of 19 | 399% |

**The top four candidates of nineteen on the entry series are 2023Q1, 2022Q4,
2023Q2, 2022Q3** - every generative-AI milestone quarter, consecutively, at the
top. Worst is 2019Q4. SSR spread 227% vs step 55's 0.06%, so where that break was
correctly called weakly identified, this one is sharply identified.

**This changes the standing of the project's central negative result.** It is no
longer "we looked and did not find", which is compatible with a blunt
instrument. The same procedure on the same panel over the same quarters resolves
generative AI's arrival to the exact quarter when asked about a variable AI
demonstrably moved, and puts the price/transaction/structure turns in
2020Q3-2021Q4 when asked about those. Written into the answer as **4.3.1**.

Explicitly **not** licensed by this: a positive control shows the procedure
detects a break of the size present in the diffusion series, not an arbitrarily
small one in the price series. Step 55's power caveat stands unchanged.

### Result 3 — diffusion ran through ENTRY, not incumbent conversion

Of **11,425 listings observed in both 2022 and 2024**, only **22 (0.19%)** ever
switched their title to advertise AI, and **none** dropped the label. New
listings carried it instead, at 4-6% of each post-2023 entry cohort.

This is also why designs looking for AI *within* incumbent listings found
nothing: under gig fixed effects an entrant is invisible. It is a
competitive-structure fact the project previously could not see at all.

### Result 4 — AI entered ABOVE the median price

| band | AI listings | non-AI |
|---|---:|---:|
| <=$10 | 25.3% | 28.9% |
| $26-50 | 13.9% | 20.1% |
| $51-100 | **22.1%** | 16.1% |
| >$100 | **16.5%** | 12.4% |

Median AI **$30** vs non-AI **$25**. AI did not arrive as a low-price flood -
consistent with the $5 tier having already emptied, before the technology existed.

Conditional on category x quarter, AI listings none the less price **-12.5%**
below others (t -2.42), ranging audio **-60.8%** (t -5.22) and writing **-26.4%**
(t -2.85) to marketing **+87.4%**. **Recorded as a selection fact, not an
effect** - it compares different listings. The within-gig version is 61 adopters:
**-14.9% (t -0.78)**, same sign, no significance.

### Result 5 — an anti-AI segment that did not exist

Listings explicitly selling human production ("no AI", "100% human", "human
written", "humanize AI content") are **exactly zero in every quarter from 2019Q1
to 2023Q1**, first appear **2023Q2**, and reach 0.15% by 2024Q3. Sellers now pay
title characters to say what their work is *not*. They price -31.5% below others
in the same cell (t -2.37, 107 observations - a description of 107 listings, not
a robust result).

### A bug found and fixed mid-run

The first `_ols` did **one sequential demeaning pass** for two FE sets, which is
wrong - demeaning on the second reintroduces variation in the first. It returned
an exact 0.0000 with a 0.0000 SE, which is what exposed it. Replaced with
alternating projections iterated to convergence.

### Outputs

- `code/57-ai-diffusion-titles.py`, `runs/ai-diffusion-titles.out`
- `data/pilot/ai-title-flags.csv` (384,983 rows: gig, quarter, category, price,
  reviews, ai_gen, ai_any, anti_ai) - reusable by any later design
- `drafts/market-structure-answer.md`: new **3.7** (six subsections), new
  **4.3.1** (the positive control), rewritten header note and 0, six new rows in
  the reader's guide, new 5 bullet on silent adoption, provenance updated

### What this changes about the research agenda

The diffusion measure is a **time-varying, within-category, gig-level** treatment
intensity - which is exactly what designs 1-8 lacked (7 category units, p-floor
0.143). Whether niche-level AI penetration predicts incumbents' price and accrual
paths is now a runnable design, and it is **design 9**. It must be
**pre-registered before any outcome is estimated**, per project practice, and its
endogeneity problem must be declared first: sellers adopt AI where AI works, so
penetration is not exogenous. Plan written to
`plans/active/ai-penetration-prereg.md`.

## 2026-08-19 (later, fourth) — Steps 54-55: the lead dies, the best-designed AI test dies with it, and six series now share one date

Two scripts, both answering the user's standing question ("how does generative AI
diffusion change long-run pricing and competitive structure") on data already
collected. `drafts/market-structure-answer.md` is revised to match and is again
the single current answer.

### Step 54 — the promotion battery. The step-53 lead is NOT promoted.

`code/54-recent-lead-battery.py` -> `runs/recent-lead-battery.out`. Five gates.

**Gate A, category-level randomisation inference — FAIL, and it is decisive.**
Step 53's treatment varies across **two categories** while its SEs cluster on
hundreds of gigs; the effective treated-cluster count is **one**, so every t it
printed is inflated by an unknown factor. Running the identical contrast for all
21 category pairs:

| frame | writing-video rank | p | what beats it |
|---|---|---|---|
| recent 2024Q3-2026Q1 | **4 of 21** | 0.190 | marketing/video, design/video, coding/video |
| balanced 2023Q1-2024Q4 | 5 of 21 | 0.238 | design/audio, writing/audio, design/video, marketing/audio |
| balanced full | 9 of 21 | 0.429 | - |

All three pairs beating it in the recent frame are **X/video**. **The step-53
result is a video result, not a writing result.** Correlation between the 21 pair
coefficients and the exposure gap they span: **-0.068**, i.e. zero.

**Gate B, seven-category exposure gradient — FAIL.** Spearman rho against the
pre-registered beta (needs <= -0.786): **+0.036** recent, -0.250 balanced 2023-24,
-0.143 balanced full. In the recent frame **translation, the most exposed
category, has the most positive trend.**

**Gate C, pre-AI placebo window — PASS**, and this is genuinely new. writing x
trend on 2019Q3-2021Q4 is **+0.0022 (t +0.34)**. Unlike designs I1-I6 this
differential is *not* pre-existing. It does not rescue the design.

**Gate D, inference robustness — PASS on the balanced frame.** Wild cluster
bootstrap (999 reps, Rademacher, H0 imposed) p 0.001 on 2023Q1-2024Q4; collapsed
two-step on category-quarter means b -0.0341 (t -5.98) vs -0.0325. Recent frame
p 0.140 either way.

**Gate E, selection/composition — PASS.** Re-estimated on gigs present in both
halves: recent -0.0719 (t -1.72), balanced 2023-24 -0.0308 (t -4.82).

The auto-verdict printed by step 53 ("NO differential") was flagged in the last
entry as too crude. It reached the right conclusion for the wrong reason: the
recent estimate fails on **power**, but the design fails on **gates A and B**,
which is a different and much more damaging failure.

### Step 55 — Upwork's under-$500 prediction. The best AI test we can run, and it also dies.

`code/55-low-tier-erosion.py` -> `runs/low-tier-erosion.out`. This is the only
public statement by an operator with transaction-level visibility that names a
**specific testable signature**: erosion concentrated in contracts under $500.
Better designed than I1-I7 because it is **within-category** — it needs neither
the seven-unit p-floor nor a two-category treatment. Category x quarter FE;
treatment is the gig's **first observed price**, fixed.

**On 2023Q1-2024Q4 it is the cleanest AI-consistent result in the project.** All
four specifications correctly signed, and the dose response is monotone across
five bands:

| band | trend vs >$100 | t |
|---|---|---|
| <=$10 | **-0.0256** | -2.99 |
| $11-25 | -0.0165 | -1.82 |
| $26-50 | -0.0120 | -1.28 |
| $51-100 | -0.0074 | -0.72 |

**Then the guards fire.**

1. **Pre-AI placebo significant and OPPOSITE-signed.** On 2019Q3-2021Q4 the cheap
   end did *better*: +0.0236 (t +5.95); log price x trend -0.0162 (t **-12.49**);
   <=$10 vs >$100 +0.0721 (t +12.30). So 2023-24 is the **reversal of a large
   pre-existing cheap-end advantage**, not a new decline.
2. **Searched break is 2020Q3. ChatGPT ranks 16 of 17.** The change coefficient
   grows monotonically the *earlier* tau is placed - an early gradual bend, not a
   late-2022 event. Caveats recorded: SSR range across all 17 candidates is 0.06%
   so the location is weakly identified and sits at the window edge, and there is
   no multiple-testing correction.
3. **Recent frame does not continue it** - all four specs null, dose response
   non-monotone and positive.

### The synthesis this creates — six series, one date

| series | turn | dated by |
|---|---|---|
| within-gig transaction proxy | 2020Q4 | searched, 15 quarters (step 52) |
| cheap-end relative performance | **2020Q3** | searched, 17 quarters (step 55) |
| $5 commodity tier | 2021Q2 | searched (step 49) |
| repricing frequency | 2021Q3 | searched (step 51) |
| Fiverr active buyers | 2021 | company reports |
| Ramp marketplace spend share | 2021Q4 | external panel |

Six series, none dated by us in advance, all inside eighteen months, and
generative AI was not in commercial use in these categories in any of them.

### The counterweight that must travel with it — the recent frame is UNDERPOWERED

Realised MDE at 80%/5% (2.80 x se) on the recent frame vs the effects we measure
on the balanced frame:

| design | recent MDE | balanced-frame effect | effect as x MDE |
|---|---|---|---|
| 7, writing x trend | 0.131 | -0.033 | **0.25x** |
| 8, cheap x trend | 0.083 | -0.014 | **0.17x** |

**If the balanced-frame effect were running unchanged through 2025-26 the recent
frame could not see it.** So neither recent-frame null is evidence the operators
are wrong; Upwork's reported GSV -3.6% and clients -4% (annual) sit comfortably
inside our intervals. An uninformative null is not a null.

### Outputs

- `code/54-recent-lead-battery.py`, `runs/recent-lead-battery.out`
- `code/55-low-tier-erosion.py`, `runs/low-tier-erosion.out`
- `drafts/market-structure-answer.md` revised: new 2.5 (operators' account and
  the window problem), rewritten 0 and 4.3, new 4.5.1 / 4.5.2 / 4.6, updated
  5-8. Design count 6 -> 8. Scope of the null now dated to 2024Q4 throughout.

### What this changes about the research agenda

**Thickening the 2024Q3-2026Q1 frame is now priority 1**, ahead of the O*NET task
statements. It is not "extend the window" any more - the window exists and it is
the one that matters; at 525 and 2,537 gigs it just cannot resolve anything. A
~6x increase in recent-frame gigs brings its MDE down to the size of the balanced
frame's estimates, at which point the operators' claims become testable.

## 2026-08-19 (later still) — Step 53: the first AI-consistent pattern in the project, and it is a LEAD, not a finding

`code/53-recent-exposure.py` -> `runs/recent-exposure.out`. Tests Fiverr's own
Q2-2026 claim ("weakness in AI-exposed categories") on gig-level data.

**Declared deviation, made before the outcome was seen.** The registered arms
HIGH={translation,writing} / LOW={video,audio} cannot run on the recent panel:
translation has **27** gigs with usable review counts and audio **47**, reaching
4 and 5 observations in a quarter. Substituted the largest adequately-sized
category on each side of the SAME registered ranking: **writing (exposed, 2nd of
7) vs video (unexposed, 6th of 7)**.

### The result — a monotone escalation

| frame | exposed x trend | t | per quarter |
|---|---|---|---|
| balanced, full 2019Q3-2024Q4 | -0.0077 | **-3.20** | -0.8% |
| balanced, 2023Q1-2024Q4 | -0.0427 | **-6.35** | -4.2% |
| recent, 2024Q3-2026Q1 | **-0.0700** | -1.50 | **-6.8%** |

Writing falls faster than video, **and the gap widens over time** — exactly the
shape an accelerating AI effect predicts. The recent estimate is the largest and
is the only one that misses significance, on **power** (525 gigs against 5,372),
not on sign. Two of three are significant.

**The auto-verdict printed by the script ("NO differential") reads only the recent
t-statistic and is too crude. Do not quote it.**

### Why this is a LEAD and not a finding

It has **not** faced the battery that killed all six previous designs: no trend
horse race, no CPI-U placebo, no placebo window, no Newey-West, no selection
audit. Steps 46 and 50 both produced significant, correctly-signed, tightly-banded
estimates at this stage and **both died on the horse race and the CPI placebo**.
The prior here is that this dies the same way. Promotion rule: it is reported only
if it clears all four, on both frames.

Second reason for caution: the 2023Q1-2024Q4 result sits inside the window six
designs already searched. A differential that only now appears may be a
consequence of narrowing 4 arms to 2 categories, which removes the arm-averaging
that suppressed category-specific noise.

### Frames were not spliced

Balanced (archival) and recent (live) are different gig populations; only slopes
are compared, never levels. The balanced frame's 2025-2026 rows in section A are
its trailing collapse (66-95 gigs) and are not evidence of anything.

## 2026-08-19 (later) — External news check: the descriptive findings hold, the causal null is now at risk from the window

User asked for news corroboration. Searched and verified against company releases
and one independent spend dataset. Three outcomes: **our numbers are confirmed
exactly**, **one claim in this log was wrong**, and **the paper has a window
problem that is more serious than any reviewer critique currently recorded**.

### 1. Confirmed to the digit

Fiverr Q2 2026 release: annual active buyers **2.7M, -21.9% YoY**; annual spend per
buyer **$368, +15.6%**; marketplace take rate 28.0%. `data/fiverr-inc-metrics.csv`
carries 2.70 and 368 for TTM-2026Q2 — both exact. The upmarket repositioning
(fewer, larger buyers) is the platform's own stated strategy, not our inference.

### 2. CORRECTION — Fiverr revenue is falling, and this log said it was rising

An earlier session note used revenue growth (+10.1% to $430.9M in FY2025) to argue
the "revenue is declining" premise was wrong. **It was right, one year later.**

| | Q2 2025 | Q2 2026 | change |
|---|---|---|---|
| total revenue | $108.6M | **$97.8M** | **-10.0%** |
| marketplace revenue | $74.7M | **$63.1M** | **-15.5%** |

Marketplace revenue — the take on gig transactions, the part our price index is
about — is falling **faster** than total. `data/fiverr-inc-metrics.csv` has no
revenue figure for 2026 at all; the column is blank. **It needs a quarterly
revenue series, not an annual one.**

### 3. THE WINDOW PROBLEM — the null may be measuring the wrong years

Both platforms now attribute the decline to AI **explicitly**:

- **Fiverr Q2 2026**: rapid AI adoption is reducing high-volume, low-value
  transactional work; "AI-related demand and traffic headwinds" and weakness in
  AI-exposed categories, cited as the reason for revised 2026 guidance.
- **Upwork Q2 2026**: full-year revenue midpoint cut $35M. Active clients -4%,
  GSV -3.6%. The decline is concentrated in **contracts under $500** as clients use
  AI for simple tasks. Upwork had flagged ~10% of GSV as AI-exposed and says
  erosion inside that group is running ahead of plan — a "pull forward".
- **Ramp** (independent, corporate card spend): labour-marketplace share of total
  corporate spend **0.66% in 2021Q4 -> 0.14% in 2025Q3**; AI-provider share 0 ->
  ~3%. Most-exposed firms substitute **$1 of freelance spend for $0.03 of AI**.

**Ramp's peak is 2021Q4, which corroborates our 2020-21 turn.** But the
AI-attributed collapse those releases describe is **2025-2026**, and:

  * the balanced frame ends **2024Q4**
  * the IPI ends **2026Q1**
  * step 46/48/50 all treat 2022Q4-2024Q4 as "post"

So six identification designs concluded "no AI effect" on a window that mostly
**precedes the period where both operators say the effect arrived.** The paper is
titled *What Generative AI Did Not Do*. On this evidence the defensible title is
narrower: **what it had not yet done by 2024**.

This is not a reason to retract anything descriptive. Prices +40.7% real, the
emptied \$5 tier, flat concentration, no price war, fewer and larger buyers — all
are corroborated by the operators' own accounts. It is a reason to **date the
claim explicitly and stop generalising past the frame**.

### Actions this creates

1. Add a quarterly revenue series to `data/fiverr-inc-metrics.csv` (2025Q1 onward).
2. Restate the second paper's scope as **through 2024Q4** in the title, abstract
   and conclusion; the null does not extend to 2025-2026.
3. New test entry: "the null is a window artefact" against
   `tests/structure-identification.test.md` — currently the strongest live threat
   to the paper and not recorded anywhere.
4. Upwork's under-\$500 concentration is a **testable prediction** our data can
   check on the low tier, and it is the closest thing to an AI signature yet named
   by anyone with transaction-level visibility.

## 2026-08-19 — The transaction turn is dated, and it is not an AI date

`code/52-ai-timeline-break.py` -> `runs/ai-timeline-break.out`. Written to answer a
user question directly: **is the number of transactions on Fiverr decreasing along
with AI development?**

### Why this step exists

Steps 24, 46, 48 and 50 all test a single pre-specified break at **2022Q4**, on the
premise that ChatGPT is "the" generative-AI event. **That premise is wrong on the
history.** GPT-3 API beta is 2020-06, Jasper 2021-02, Copilot preview 2021-06,
GPT-3 GA 2021-11, DALL-E 2 2022-04, Midjourney and Stable Diffusion 2022-07/08.
So "no break at 2022Q4" was only ever a statement about one date, not about
generative AI. This step **searches** the break instead of assuming it.

### The answer

The within-gig transaction proxy **peaks 2020Q3 and turns down from 2020Q4** —
before any of these tools was in commercial use in these categories.

| quarter | index (2020Q1 = 100) |
|---|---|
| 2020Q1 | 100.0 |
| **2020Q3** | **146.4 (peak)** |
| 2021Q2 | 135.0 |
| 2022Q1 | 78.1 |
| 2022Q4 (ChatGPT) | 103.9 |
| 2023Q3 | 124.6 |
| 2024Q4 | 64.9 |

Best **trend break** of 15 candidates: **2020Q4**, gamma -0.0966/quarter (t -48.63).
Best **level-shift** break: 2020Q2, and it is **positive** (+49.7%) — the pandemic
boom beginning, not a decline.

**Where the AI milestones rank among the 15 candidate quarters (level-shift SSR):**

| milestone | quarter | rank | t |
|---|---|---|---|
| GPT-3 API beta | 2020Q2 | 1/15 | +38.73 (wrong-signed) |
| Copilot preview | 2021Q2 | 5/15 | -17.27 |
| GPT-3 GA | 2021Q4 | 8/15 | -10.84 |
| GPT-4 | 2023Q1 | 9/15 | -10.53 |
| **ChatGPT** | **2022Q4** | **11/15** | -6.22 |
| DALL-E 2 | 2022Q2 | 14/15 | -3.52 |
| Midjourney + SD | 2022Q3 | **15/15** | **-0.09** |

**The three image-model and ChatGPT dates are the WORST-fitting breaks in the
window.** The one AI milestone that fits is GPT-3's API beta, and it fits with the
wrong sign, because 2020Q2 is when the pandemic boom started.

### Identification, stated rather than assumed

Review accrual falls as a gig ages, and within a gig age and calendar time move
one-for-one, so under gig FE the **linear** calendar trend is not separable from
the ageing profile — the age-period-cohort problem, which has no solution here.
Age is absorbed as full **age fixed effects** (no functional form imposed), so
**non-linear** calendar changes are identified off cohort spread. Only break
locations and sizes are reported; no trend is.

### What must not be over-claimed

The search covers 15 quarters with **no multiple-testing correction**, so the
winning t is inflated. A searched break also lands at window edges when the series
is humped, and this one is humped. The defensible claim is the weaker one: **the
proxy peaks 2020Q3 and declines thereafter, so no AI milestone can have initiated
the decline.** This is a falsification of dates, not evidence for a cause.

Consistent with the four series that already dated structural change to 2020-21:
commodity tier 2021Q2, repricing 2021Q3, buyer-growth inflection 2022, and the
implied-order peak in 2021 (annual).

## 2026-08-18 (night) — The seller-conduct half of competitive structure, and the whole question assembled into one answer

The user asked, again and directly: **how does the diffusion of generative AI
change long-run pricing and competitive structure of online freelancer markets?**
Two things were produced, both from data already collected.

### 1. `code/51-seller-structure.py` → `runs/seller-structure.out`

Step 49 asked the structural question at the level of the price *distribution* —
all properties of the cross-section. Step 51 asks the four questions that are
properties of **seller conduct and the seller side**, none of which the project
had ever measured. Five candidate findings, **three killed, one demoted to a lead,
one survivor.**

| finding | status | number |
|---|---|---|
| **sellers stopped RAISING prices** | **SURVIVES (descriptive)** | balanced panel: any price change 23.6% → 18.3% of listing-quarters; **increases 18.1% → 12.4%; cuts 5.4% → 5.9%, flat**; mean Δlog p +0.0565 → +0.0239 |
| repricing intensified (price war) | **KILLED** | the fall is *entirely* fewer increases — downward nominal rigidity, not a price war |
| AI reshuffled the price ordering | **KILLED** | 4-quarter rank correlation **rises** 0.898 → 0.940 — and it is mechanically implied by the repricing fall, so not independent evidence |
| sales concentrate on top **sellers** | **KILLED** | Gini among trading sellers 0.637 (2021) → 0.618 (2023) → 0.651 (2024); top-decile seller share 51.5% → 50.5% → 56.4%. Same 2024-only pattern that killed the listing-level version |
| return to reputation rose at ChatGPT | **LEAD, not a finding** | balanced panel +11.3% → **+18.5%** per doubling (diff +0.091, t 2.04), clears a false-break placebo (−0.012, t −0.54) — but **all 37,888 listings give +0.0060, t 0.79, a precise zero** |

**The searched break says this is not a ChatGPT event either.** Best break for
any-change is **2021Q3** (the ChatGPT quarter is t 1.90 and *positively* signed);
for price cuts the best break is 2022Q3, one quarter *before* ChatGPT, and the
ChatGPT-quarter coefficient is −0.0005. That is the third independent series to
date the structural change to 2021 — after the commodity tier (2021Q2) and the
buyer-growth inflection (2022, from +23.5% to +0.0%).

**The lead was demoted on the frame disagreement, not on the placebo.** It clears
its own placebo split cleanly. It appears on 2,750 of 37,888 listings and vanishes
on the frame containing them, so it is recorded as a lead with a written promotion
rule rather than reported.

### 2. `drafts/market-structure-answer.md` — the question, answered

Assembles the IPI (steps 21/23/27/30), the demand break (46), Fiverr Inc.'s
transactions (47), the failed attribution designs (46/48/49/50) and the structure
descriptions (49/51) into one document. The answer, in short:

**Four of the five things a commoditisation story predicts did not happen, and
the fifth happened too early for generative AI to have caused it.**

| prediction | data |
|---|---|
| prices fall | real listed prices **+40.7%** (±3.7%) |
| quantities rise | Fiverr buyers **−36%** from the 2021 peak; implied orders −18% vs 2020 |
| the cheap tier widens | the $5 tier **emptied** 27.3% → 10.3% — steepest decline **2021Q2**, slowing after ChatGPT |
| price competition intensifies | repricing **fell**, entirely through fewer increases; cuts flat |
| sales concentrate | Gini flat among trading listings **and** trading sellers |

What this market looks like across the diffusion window is **repositioning
upmarket** — fewer and larger buyers, higher prices, a hollowed commodity tier,
deeper menus, no price war, unchanged concentration — not commoditisation. The
AI attribution remains unidentified after six designs, and §4.4 of the answer
names the rivals this data cannot separate from AI: post-pandemic normalisation,
the 2022 rate shock, and Fiverr's own upmarket strategy, which predicts every
structural fact **and** predicts the 2021 timing better.

### 3. `plans/active/structure-descriptive-lock.md` — the survivors locked

Discharges the market-structure plan's pre-registration step. Eight descriptive
claims (D1–D8) with the frame each is read off, six locked nulls (N1–N6) that may
not be quietly dropped if a later specification revives one, one lead (L1) with a
written promotion rule, and the five guards that apply to any successor
specification. Locked **before** any further search on this question.

### 4. User chose: **second paper.** Scaffolded with real content, not stubs

`drafts/structure/` — *"What Generative AI Did Not Do to a Freelance Market"*.
Seven sections written from the assembled answer: abstract, introduction, data,
**§3 the five predictions tested** (P1–P5, each rejected in sign or on timing),
**§4 the six identification designs** (relabelled I1–I6 so they cannot be confused
with the lock's descriptive D-claims), discussion, conclusion, references with
`[CITE-]` placeholders. Renders clean, no missing includes:
`drafts/structure-draft-2026-08-18.html`.

`drafts/render.py` gained a `--main` flag so a second paper tree can render; the
HTML still lands in `drafts/` so the `../`-relative image rewriting keeps working.
The IPI draft re-renders byte-identical in structure — nothing about paper 1 moved.

**Nine test files** under `tests/structure-*.test.md`: a master layer carrying the
user requirements (U1 the question, U2 data-we-already-have, U3 second paper) and
eight cross-cutting criteria, plus reviewer simulations for each section — 14
critiques on §3, 12 on §4.

### 5. The tests immediately earned their keep — three FAILs, all now closed

- **R8 "the repricing fall could be thinner capture coverage."** A real threat, and
  it needed data rather than prose. Added S2c to `code/51`: on a **strict panel of
  936 listings present in every quarter**, any-change runs **24.1% → 18.1%**,
  increases **18.5% → 12.0%**, cuts **5.6% → 6.1%**, and observed pairs per listing
  move **−1.9%**. The finding survives a frame where coverage cannot vary. Recorded
  as D7a in the lock.
- **R9 "category × quarter FE absorbs the treatment if AI is platform-wide."**
  Correct, and central enough that §4.4 now states it outright: a *uniform* AI
  shock is absorbed by construction, design I6 identifies only *relative* exposure
  effects, and its null therefore does not mean AI had no effect. This is the
  paper's sharpest self-limitation and it came from a reviewer simulation.
- **M6 terminology** — glossary paragraph added (listing = gig, sales proxy =
  review count). **M5 causal language** — scanned; the only hit is §1's explicit
  disclaimer.

Remaining open FAILs are recorded, not hidden: §2 R3 (what makes this platform
representative), §2 R7 (point at the category classifier), §5 R3 (show the
pre-2020 baseline), §5 R4 (downward nominal rigidity asserted rather than tested).

No IPI paper section, figure, frozen number or site file was touched.

## 2026-08-18 (evening) — The sixth design RAN. First to pass parallel trends; dies on the trend horse race and the CPI-U placebo

`code/50-continuous-exposure.py` → `runs/continuous-exposure.out`, running the
specification locked in `plans/active/exposure-continuous-prereg.md` hours earlier.
**No deviations from §2–§5.** Result recorded as §10 of that file.

### The gate card

| gate | result |
|---|---|
| §2 selection audit | **THREAT** — dropped (zero-match) gigs accrue **+23.7%** more pre-period |
| G1 parallel trends | **PASS** — Wald chi2(11) = 9.99, **p = 0.53**, 0 of 11 significant |
| G2 not-a-price-proxy | **PASS** — −0.1692 (t −2.43) with price rank × quarter controlled |
| G3 placebo window | **PASS** — false break returns t −0.45 |
| G4.2 trend horse race | **FAIL** — `exposure × POST` **flips sign** to +0.021 (t 0.28) once `exposure × trend` (t −2.54) is in |
| G4.3 CPI-U placebo | **FAIL** — t **−2.86** |
| G4.4 Newey-West | PASS — DW 1.73 |
| G5 composition | **FAIL** — balanced frame t −1.85 |

Primary estimate **−0.1680 (se 0.0666, t −2.52)** on 121,414 observations / 20,966
gigs, stable across the entire robustness grid (K = 1/5/10 → −0.140/−0.198/−0.192;
`dv_rating_beta` → −0.114; all significant). Price outcome is a precise zero,
**+0.0021 (t 0.06)**.

### Why this failure is worth more than the previous five

**It is the first design in the project to pass parallel trends on the demand
margin** — and it passes on step 46's stricter count rule as well as the
pre-registered joint test. G2 excludes step 49's mean-reversion disease; G3
excludes step 29's standard-error disease. **Three of the four ways prior designs
died are now ruled out.**

It dies on the fourth, and the diagnosis is now specific rather than a shrug:
**there is an exposure-correlated differential trend that predates ChatGPT, and
there is no break at ChatGPT.** The §6 dose–response says the same thing
independently — decile changes run −13.3% to +3.5% with **no monotone gradient**,
and the *least*-exposed decile falls more (−7.8%) than the most-exposed (−1.9%).

### Three qualifications, so the failure is not overstated

1. **Underpowered against its own standard.** Realised MDE ±0.186 log points
   (±20.5%); |β| is **0.90× the MDE**. Even on a clean sweep this estimate sits
   below the pre-registered power threshold.
2. **G5 failed on power, not sign.** The balanced estimate is **−0.2022** — larger
   and identically signed — and loses significance only because n falls to 1,715
   gigs. Recorded FAIL by the letter of §5; "the sign reversed" would be wrong.
3. **Internal contradiction.** The collapsed Newey-West difference series returns
   `post` = **+0.0701 (t 2.44)**, opposite in sign to the panel estimate. It carries
   no gig FE, so the gap is composition — one more reason not to read −0.168 as an
   effect.

### Where this leaves the project

Six designs, six failures, one consistent surviving pattern. The category design
space was exhausted at step 48; the within-category price route died at step 49;
the continuous-exposure route now dies on trend and placebo. Highest-value
remaining input is the one the prereg declared as a prior weakness **before**
running: **O\*NET task statements**, since the current measure is both thin (36.7%
zero-match) and selected (dropped gigs accrue 23.7% more). Second is reaching past
2024Q4, which needs the live forward crawl.

No paper section, figure, frozen number or site file was touched.

## 2026-08-18 (later) — Pre-registration locked for the sixth design, and a correction to the item-cluster claim

`plans/active/exposure-continuous-prereg.md`. User chose: hold the step-49 framing
decision, sharpen identification first, and pre-register before extending.

**Correction.** The todo entry written earlier today said the 151 item clusters
were ready to carry a continuous-exposure design. They are not.
`data/pilot/item-clusters.csv` was built by `code/10-cluster-items.py` on the
superseded 500-seller pilot: **1,908 gigs, median cluster size 8, only 14 clusters
reaching 30 gigs.** The design scores **gigs directly** instead.

**Feasibility pilot, run before the lock and disclosed in prereg §1:**

| | |
|---|---|
| gigs with usable descriptions | 39,933 |
| TF-IDF match rate against O*NET occupation titles | **63.2%** (36.8% zero-match — a declared selection threat) |
| agreement with the pre-registered category ranking | **Spearman ρ = +0.786 (K=3)**; +0.68 / +0.71 / +0.71 at K = 1 / 5 / 10 |
| within-category sd of exposure | **0.11–0.20**, against a between-category range of **0.13** |

That last row is the reason to run it: **within-category exposure variation is at
least as large as between-category variation**, which is exactly the variation the
seven-category designs never had.

**What is locked:** exposure × POST with gig FE + **category × quarter FE** —
the latter absorbing the platform-wide demand fall that steps 46–48 kept mistaking
for treatment — gig-clustered SEs, and five gates whose failure consequences are
fixed in advance: joint-F parallel trends (not step 46's count rule, which is
infeasible with 11 pre-quarters), a not-a-price-proxy gate carrying step 49's
mean-reversion lesson, a placebo window, the step-29 battery, and a balanced-panel
composition gate carrying step 49's other lesson. Sole authorised fallback:
descriptive dose–response by exposure decile, explicitly not identified.

**The prior is recorded in the file as low.** Five designs have failed on this
data; the lock's purpose is to make a sixth failure interpretable rather than
discardable. The known weakness — O*NET *titles* are thin text, and task
statements would fix coverage — is declared before running and deliberately left
out of scope, so it cannot become a post-hoc excuse.

Nothing has been estimated under this exposure measure. No paper section, figure,
frozen number or site file was touched.

## 2026-08-18 — Competitive structure asked for the first time. Three of six candidate findings died in the same script that produced them

`code/49-market-structure.py` → `runs/market-structure.out`. The user asked how AI
diffusion changes **long-run pricing and competitive structure**. The project
answers the pricing half already (+40.7% real); it had never asked the structure
half. Nine sections on the balanced frame, 2019Q3–2024Q4, 257,208 gig-quarter
observations on 37,888 listings. Plan: `plans/active/market-structure.md`.

### What survives

| finding | status | number |
|---|---|---|
| the $5 commodity tier emptied | **FACT, but PRE-DATES AI** | 32.0% → 11.4% of listings; steepest decline 2021; decline **slows** after 2022Q4 |
| product-line depth rose | **FACT** | 3-tier share 82% → 91%; premium/basic ladder compresses 4.06× → 3.80× |
| dispersion narrowed then recovered | descriptive only | sd log p 1.43 → 1.15 (2023Q3) → 1.23 |
| buyers fewer and larger | FACT (step 47) | buyers −36% from the 2021 peak, spend/buyer $205 → $368, GMV roughly flat |

**The headline is the sign.** A technology that commoditises supply should push
price down, quantity up, and the cheap tier wider. This market shows price **up**,
quantity **down**, and a cheap tier that stopped emptying almost exactly when
ChatGPT launched. Whatever happened here, it does not have the shape of
AI-driven commoditisation of the low end.

### What was killed, and by what

1. **"Sales concentrated on the winners."** Gini of quarterly accrual rises
   0.63 → 0.75 — but Gini **among listings with any sales** is flat (2021 0.64 →
   2023 0.61). The whole rise is the zero-sales share, and that rises only in
   2024, which is the trailing edge step 48 already flagged. Not a concentration
   result; a dormancy-at-the-edge artefact.

2. **"AI eats the cheap end" (new design 1).** Abandons the seven-category
   ranking entirely: rank listings by pre-period price *within* category, let
   category × quarter FE absorb every platform-wide shock, ask whether cheap
   listings lost more demand. 16,526 ranked listings instead of 7 categories.
   **Event study fails: 10 of 11 pre-period coefficients significant**, pre-period
   mean −0.18 against post-period −0.25. No break, just a wandering gradient. The
   DiD point estimate (−0.109, t −3.56) is also **wrong-signed for the hypothesis**.

3. **"Post-ChatGPT price convergence from below" (new design 2).** The same design
   on prices returns the most publishable-looking shape in this project: a clean
   sign reversal at exactly 2022Q3/Q4, monotone after, every coefficient
   significant. **It is mean reversion.** Moving the ranking window moves the
   pattern with it — **3 of 3 windows peak inside their own ranking window** and
   decay away from it in both directions. Dropping the ranking window from the
   estimation sample changes nothing, which confirms the bias is in rank
   measurement error rather than sample overlap. Same failure mode as the
   retracted price-elasticity result: tight, correctly signed, well shaped, and
   about nothing.

### Two methodological traps worth keeping

**Gig fixed effects do not protect against composition.** The quota manifest adds
~1,250 net listings at 2022Q3 and the added ones are cheaper. On all listings the
≤$10 share **jumps +5.7pp at 2022Q3** — one quarter before the break — and a
level-shift search then reports a significant *positive* break at 2022Q4. On a
strictly balanced panel (3,106 listings present in all seven quarters 2021Q4–2023Q2)
the same series falls **monotonically**, 19.8% → 19.1% → 18.6%, with no jump at all.
Every distributional claim here is read off a balanced panel for that reason.

**Break dates must be searched, not assumed.** Assuming 2022Q4 returns a
significant coefficient on the commodity-tier series and would have produced a
wrong headline. Searched, the steepest decline is **2021Q2** and the ChatGPT
quarter carries the opposite sign. And the *form* matters as much as the date: the
series is a decline whose slope changes, so a level-shift search reports curvature
and picks an endpoint (2023Q1), while the trend-break form answers the actual
question. Both are printed.

### What would change the verdict

The category design space is exhausted at seven units (p-floor 0.143) and the two
within-category routes tried here both fail on pre-trends and on mean reversion.
The remaining route is the backlog's **gig-level continuous exposure**, mapping
`data/eloundou-2023-occ-level.csv` onto the **151 item clusters** in
`data/pilot/item-clusters.csv` rather than onto seven categories. That is the only
design in view that raises the p-floor, and both of its inputs are already vendored.

No paper section, figure, frozen number or site file was touched.

## 2026-08-17 — The category question is exhausted at category level: the two HIGH categories land at OPPOSITE ends of the placebo distribution

`code/48-category-impact.py` → `runs/category-impact.out`. Ran the pre-registration's
only authorised fallback (synthetic control) plus the specification that directly
addresses why the DiD failed. **Answer: no, category-level impact cannot be
identified on this data, and the reason is now specific rather than a shrug.**

### C2 — category-specific trends kill it outright

Step 46's failure was a differential *trend*, so the textbook fix is to give every
category its own. Doing that: **HIGH × POST = −0.4% (t −0.17)**, gone. Meanwhile
audio's own trend is +2.7%/quarter (t 7.87) and translation's +2.6% (t 8.57) — the
categories genuinely do trend differently, and once that is allowed there is no
differential break left to attribute.

### C3/C4 — synthetic control, and the internal contradiction

| target | exposure | registered (LOW donors) | expanded (LOW+MID) |
|---|---:|---|---|
| **translation** | **0.840** (most exposed) | −2.2%, ratio 0.14 → **within noise** | **+1.4%, wrong-signed**, ratio 0.10 |
| **writing** | 0.686 | −12.4%, ratio 1.08 | −15.6%, ratio 1.81 |

`ratio` = |mean post gap| / pre-period RMSPE. **The single most AI-exposed category of
the seven shows essentially no deviation from its synthetic control, and it flips sign
when the donor pool widens.** Writing does fall. The two HIGH categories therefore
disagree with each other, which is fatal to an AI reading — the measure that ranks
translation top is the same measure the study pre-registered.

### C5 — in-space placebos: writing 1st of 7, translation LAST of 7

| category | arm | exposure | post gap | pre RMSPE | ratio |
|---|---|---:|---:|---:|---:|
| **writing** | **HIGH** | 0.686 | −0.1695 | 0.0935 | **1.81** |
| audio | **LOW** | 0.248 | +0.0879 | 0.0516 | 1.70 |
| marketing | mid | 0.624 | +0.1840 | 0.1102 | 1.67 |
| video | **LOW** | 0.402 | −0.0969 | 0.0717 | 1.35 |
| coding | mid | 0.588 | +0.1388 | 0.1035 | 1.34 |
| design | mid | 0.508 | −0.1799 | 0.2236 | 0.80 |
| **translation** | **HIGH** | 0.840 | +0.0138 | 0.1394 | **0.10** |

Writing ranks **1 of 7** → one-sided p = **0.143**; translation ranks **7 of 7** →
p = **1.000**. And **audio, the least-exposed category, is second**. Known before
running and stated in the script: with seven categories the smallest attainable
one-sided p-value is 1/7 = 0.143, so **this test cannot reach 5% no matter what the
data say.** That ceiling is a property of having seven categories, not of the result.

### Verdict, and what would actually change it

Four independent designs have now failed to identify a category-level AI effect:
the DiD (parallel trends), the trend horse race, the CPI-U placebo, and now synthetic
control with in-space placebos. **The category-level design space is exhausted.** The
honest statement is that per-category *breaks* are measured precisely (−13% to −43%,
±4.2–7.0%) but their *differences* cannot be attributed to AI exposure.

Three things would change it, in order of value:

1. **Finer exposure variation.** Seven categories caps inference at p = 0.143 by
   construction. Fiverr has hundreds of subcategories; the fix is the **gig-level
   continuous-exposure design already in the backlog**, which needs an external
   task-exposure measure mapped to gigs rather than the hand-built lexicon. The
   Eloundou occupation file vendored today is exactly that measure, so this is now
   materially cheaper than when the backlog item was written.
2. **Reach past 2024Q4.** The treatment window is eight quarters and stops before the
   2025–26 agentic period. Needs the live forward crawl.
3. **Sub-category or gig-population data**, since per-gig accrual and platform orders
   differ by a factor the archive cannot resolve (exit unmeasurable).

One data caution surfaced by C1: **every category drops steeply into 2024Q4**
(design 3.46 at 2023Q3 → 2.08). That is the trailing edge thinning, not a demand
event, and it is a reason the window boundary is 2024Q4 rather than later.

Declared as a prereg deviation (§9): C4's expanded donor pool. It is declared because
it deviates, and noted as *worsening* the finding — translation goes from −2.2% to
+1.4% wrong-signed — so it cannot be read as searching toward a result.

## 2026-08-17 — Fiverr Inc.'s reported transactions: buyers −36%, orders −18% to −39%. Phase 0's decline is REAL, not a review artefact

`code/47-fiverr-inc-external.py` → `runs/fvrr-external.out`, off a new
`data/fiverr-inc-metrics.csv`. **The first actual transaction data in this project.**
The archive has none — `review_count` is a proxy — so the only route to real
quantities is Fiverr Inc. (NYSE: FVRR), which nothing in this repo had used.

### 1. What the company reports

Fiverr defines spend per buyer as TTM GMV / active buyers, so **GMV = buyers ×
spend per buyer is an identity, not an estimate**. It reproduces every independently
reported GMV to within rounding (2022: 4.2M × $262 = $1,100M vs $1,090M reported).
Revenue is *not* a substitute — 2024 revenue / GMV = 36% against a 27.6% take rate,
because revenue also carries Pro, subscriptions, ads and acquired services.

| period | buyers (M) | $/buyer | GMV ($M) | buyers YoY |
|---|---:|---:|---:|---:|
| 2020 | 3.40 | 205 | 699 | +44.7% |
| 2021 | **4.20** | 242 | 1,020 | +23.5% |
| 2022 | 4.20 | 262 | 1,090 | **+0.0%** |
| 2023 | 4.10 | 278 | **1,140** | −2.4% |
| 2024 | 3.60 | 302 | 1,087 | −12.2% |
| 2025 | 3.10 | 342 | 1,060 | −13.9% |
| 2026 TTM-Q2 | **2.70** | 368 | 994 | −12.9% |

**Buyers peaked at 4.20M in 2021 and are 2.70M — −35.7%.** GMV peaked in 2023 and is
only −12.8%. The whole gap is spend per buyer, which rose *every single year* from
$119 (2017) to $368. **Fewer, larger buyers.** Any "transactions are falling" claim
has to handle that composition shift first, and the buyer series is the cleanest
quantity the company publishes.

**The inflection is 2022.** Buyer growth ran +44.7% and +23.5% in 2020–21, hit
**exactly +0.0% in 2022**, and has fallen 12–14% a year since. That is the right era
for ChatGPT — and also for post-pandemic normalisation, the rate shock and the tech
downturn, none of which this series can separate. Timing is suggestive, not evidence.

### 2. The transaction count, derived

`orders = GMV / price per order`. Deflating GMV by CPI-U and dividing by the IPI real
composite (both indexed 2020 = 100, so only the ratio is used):

- real GMV **+11.3%** vs 2020
- real IPI price **+35.8%**
- **implied orders −18.0% vs 2020, and −38.6% from the 2021 peak**

### 3. This kills the leading rival explanation for Phase 0

Phase 0's platform-wide 13–43% accrual fall was equally consistent with (a) real
transaction decline and (b) review-propensity drift, and nothing internal to the crawl
could separate them. **Fiverr's buyer and GMV series have nothing to do with reviewing
behaviour, and they fall too.** So the *direction* of Phase 0 is externally
corroborated: **fewer transactions is real, not a reviewing artefact.** That was the
threat flagged this morning as urgent enough to block calling Phase 0 a demand
decline; it is now substantially discharged, though Phase 1 should still bound the
magnitude.

Magnitudes don't match (−18% platform vs −13% to −43% per surviving gig) and that gap
is informative rather than fatal: per-gig accrual falls faster than platform orders if
the listing population grew, slower if it shrank. Sign agreement is the result; the
level gap is a gig-population question the archive cannot answer, since exit is
unmeasurable (`n_404 = 0` across 509,339 captures).

### 4. Caveats that bound the number

1. **The IPI measures listed basic-package prices, not realised order value.** If
   buyers shifted to higher tiers or Pro — which the spend-per-buyer path and Fiverr's
   stated upmarket push both suggest — realised price rose faster than the IPI and the
   implied order decline is **overstated**. Treat −18% / −38.6% as an **upper bound**
   on the fall.
2. Active buyers is trailing-twelve-month, so it smooths any break and **cannot date
   an event to a quarter**.
3. GMV from 2024 is derived (Fiverr stopped reporting it directly).
4. Orders per buyer is unobserved; buyers −36% says most of the fall is fewer buyers.
5. **Platform-wide only (Q3).** Fiverr publishes no category split, so this says
   nothing about which categories. **The category question stays where step 46 left
   it: not identified.**

Discharges the Phase 4 external-validation item. No paper section, figure or frozen
number was touched.

## 2026-08-17 — Phase 0 RAN. Step 24's null was underpowering; the AI attribution is not identified

`code/46-balanced-demand.py` → `runs/phase0-demand.out`. Ran the specification locked
in the pre-registration hours earlier, against 236,535 accrual observations on 35,888
gigs, 2018Q1–2024Q4. **The pre-registration earned its keep on the first run: it caught
a −7.9% "AI effect" with a tight CI and t = −4.14 that is not real.**

### 1. Step 24's seven nulls were an artefact of power. All seven categories broke hard.

MDE is now **4.7× to 9.4× tighter**, and every category shows a large, highly
significant fall in review accrual at 2022Q4 (gig FE + linear trend, gig-clustered SEs):

| category | arm | obs | break | t | MDE now | MDE step 24 |
|---|---|---:|---:|---:|---:|---:|
| writing | **HIGH** | 39,129 | **−42.9%** | −23.00 | ±4.9% | ±31% |
| translation | **HIGH** | 19,766 | **−37.2%** | −13.48 | ±7.0% | ±66% |
| audio | **LOW** | 29,977 | **−35.5%** | −15.28 | ±5.8% | ±52% |
| coding | mid | 35,755 | −35.2% | −17.63 | ±4.9% | ±23% |
| video | **LOW** | 35,513 | −28.6% | −14.49 | ±4.7% | ±38% |
| marketing | mid | 25,947 | −23.7% | −8.49 | ±6.5% | ±44% |
| design | mid | 44,699 | −13.1% | −6.65 | ±4.2% | ±27% |

So the 2026-08-14 premise was right — the shipped-panel nulls excluded almost nothing —
but the result it revealed is **not** the one the study was designed to find.

### 2. Every category fell, including the least AI-exposed ones. That is the problem.

**audio is 7th of 7 on pre-registered exposure (β 0.248) and has the 3rd largest fall.**
**design is mid-exposure and has the smallest (−13.1%).** Spearman ρ between exposure
rank and break size is **+0.429** over seven categories — |ρ| must exceed ~0.79 for
p < 0.05, so it neither supports nor refutes the ranking. A fall that hits low-exposure
categories as hard as high-exposure ones is what a **platform-wide** shock looks like.

### 3. Parallel trends FAILED, so the DiD is dead — as pre-committed, not as an excuse.

Event study, HIGH vs LOW, 2022Q3 omitted: **6 of 16 pre-period interactions significant
at 5%** (2019Q1 +2.48, 2019Q4 +2.14, 2020Q2 −2.08, 2020Q3 −5.13, 2021Q1 −2.62,
2021Q2 −2.61). The gate's pre-registered rule is *no* significant pre-period coefficient,
so it fails. Per §5 the consequence was fixed in advance: **the DiD is reported as dead
and the only authorised fallback is synthetic control on the LOW categories.**

### 4. The DiD estimate is exactly the trap the battery exists to catch.

Had the gate not been pre-committed, the headline would have been
**HIGH × POST = −7.9% [−11.4, −4.2], t = −4.14**, on a realised MDE of **±3.96%** —
which *meets* the project's ±5% adequacy standard. It is tight, significant, correctly
signed, and wrong. **Two of the four step-29 tests kill it:**

- **Linear-trend horse race.** Adding HIGH × trend collapses HIGH × POST from −0.0822
  (t −4.14) to **−0.0078 (t −0.30)**, while HIGH × trend is itself significant
  (−0.0083, t −2.98). The "break at ChatGPT" is a **differential trend that predates it**.
- **CPI-U placebo.** HIGH × CPI-U — a series with no AI content — is **significant
  (−3.6%, t −2.93)**. The design is not isolating AI.
- Newey–West on the collapsed HIGH-minus-LOW quarterly series: post = **+0.0041
  (t 0.13)**, null and wrong-signed. **Durbin–Watson 2.26**, so unlike step 29
  (0.22–1.08) the SEs here are not the problem — the effect simply isn't there.
- First differences passes by construction: the outcome *is* a difference, not a level.
- **Placebo window passes** (2018Q3–2019Q4, false break 2019Q2): −1.5%, t −0.17.

Three independent routes — failed pre-trends, the trend horse race, and the CPI-U
placebo — say the same thing, and the collapsed series shows no break at all.

### 5. What is and is not established

- **Established:** review accrual per surviving gig fell sharply and platform-wide after
  2022, by 13% to 43% depending on category, now bounded to ±4.2–7.0% rather than
  ±23–66%. This is **Q1** — do surviving gigs sell less — not platform volume.
- **Not established:** that AI caused it, or that it hit AI-exposed categories harder.
  The differential is a pre-existing trend and is reproduced by an AI-free series.
- **Leading rival explanation, and it is now urgent rather than a caveat.** A
  *platform-wide* accrual decline of this size is precisely what **review-propensity
  drift** looks like — buyers reviewing a smaller share of purchases over time, with no
  change in sales at all. That confound has never been tested (Phase 1) and it now
  threatens the headline number, not just the differential. **The −13% to −43% must not
  be described as a demand decline until Phase 1 runs.**

### 6. Next

Phase 1 (review-propensity drift) is promoted ahead of everything else, because it
governs whether Phase 0's platform-wide finding is about sales or about reviewing.
Synthetic control is the authorised fallback for the differential question. Fiverr Inc.'s
reported GMV becomes materially more valuable: a platform-wide accrual fall that the
company's own books do *not* show would be close to proof of propensity drift.

No paper section, figure or frozen number was touched.

## 2026-08-17 — Pre-registered the transaction-volume study (Phase −1); Phase 0 unblocked

- **The plan from 2026-08-14 existed but was unstarted** — no `code/45+`, no pre-registration
  file. Phase −1 was the only thing standing between it and a run, because the study is
  causal from the start: Phase 0 reveals per-category demand breaks, and an exposure ranking
  built after seeing those is not pre-registered in any meaningful sense. That is the same
  objection that sank the elasticity table in step 29.
- **Exposure ranking sourced, not recalled.** User chose Eloundou et al. (2023) over Felten
  AIOE — Eloundou is LLM-specific and matches the 2022Q4 break the study actually dates.
  Pulled the authors' occupation-level file from their public replication repository
  (`openai/GPTs-are-GPTs`, `data/occ_level.csv`) and vendored it to
  `data/eloundou-2023-occ-level.csv` (923 O\*NET-SOC occupations) so the ranking reproduces
  offline. `code/45-exposure-ranking.py` maps the seven Fiverr categories onto SOC codes by
  task content, equally weighted, and emits `data/exposure-ranking.csv`.

  | rank | category | human β | rank (dv) | dv β |
  |---:|---|---:|---:|---:|
  | 1 | **translation** | 0.840 | 2 | 0.880 |
  | 2 | **writing** | 0.686 | 3 | 0.815 |
  | 3 | marketing | 0.624 | **5** | 0.547 |
  | 4 | coding | 0.588 | **1** | 0.917 |
  | 5 | design | 0.508 | 4 | 0.611 |
  | 6 | **video** | 0.402 | 7 | 0.486 |
  | 7 | **audio** | 0.248 | 6 | 0.495 |

- **The two annotators disagree about coding, and finding that now rather than later is the
  main value of doing Phase −1 at all.** GPT-4 ranks coding the most exposed of the seven
  (β 0.917); human labellers rank it fourth (0.588). Marketing moves the other way (3rd →
  5th). So the primary contrast is built only from the four categories both annotators agree
  on — **HIGH = {translation, writing}, LOW = {video, audio}** — and **coding is quarantined**
  and reported separately. Had this surfaced after Phase 0, any assignment of coding to an
  arm would have read as arm-picking.
- **Human annotation is primary, GPT-4 is declared robustness.** `dv_rating_*` is a model
  scoring its own labour-market reach; that circularity is an obvious reviewer target and the
  study should not depend on it.
- **Specification locked** in `plans/active/transaction-volume-prereg.md`: outcome =
  within-gig `ln(1 + review accrual per quarter)`, window 2018Q1–2024Q4, single pre-specified
  break at **2022Q4**, gig + quarter fixed effects, **SEs clustered on gig** (step 22's
  published SE was unclustered and 1.93× too small — a second occurrence would be
  indefensible), placebo window 2018Q3–2019Q4 with a false break at 2019Q2, parallel trends
  as a **pass/fail gate** with synthetic control named as the *only* authorised fallback, and
  the step-29 battery (first differences, linear-trend horse race, CPI-U placebo,
  Newey–West) required to pass **all four** or the result is labelled descriptive rather than
  causal. §10 records in advance that a tightly-bounded null is the headline, not a
  disappointment, so it cannot later be reframed as one.
- **Power computed pre-outcome** (sample sizes are not outcomes). Primary contrast:
  **129,378 accrual observations** — HIGH 61,737 (writing 40,038 + translation 21,699) and
  LOW 67,641 (video 36,485 + audio 31,156) — against step 24's 10,275 across all seven
  categories. The per-category split also reproduces the 2026-08-14 totals of **36,336 gigs /
  242,468 observations** exactly, which verifies the frame independently.
- **Nothing was estimated.** No demand outcome was computed on the balanced frame, and no
  paper section, figure or frozen number was touched. Phase 0 — generalise
  `code/24-margin-diagnostics.py` to take a frame argument and re-run M1/M2/M3 — is now
  unblocked and needs no new data collection.

## 2026-08-14 — Planned the transaction-volume study; measured its feasibility first

- **User question: "is the number of transactions on Fiverr decreasing along with AI
  development? what are the impacts across different categories?"** → new plan at
  `plans/active/transaction-volume.md`. Nothing was run beyond feasibility probes; no
  paper section, figure or frozen number was touched.
- **The plan's central finding is that we already ran this study and it was underpowered.**
  `code/24-margin-diagnostics.py` reported null demand breaks in all seven categories, but
  on the *shipped* panels: **5,403 (historical) + 4,872 (recent) = 10,275** review-accrual
  observations, MDE **±23% (coding) to ±66% (translation)**. Measured today,
  `balanced-prices.csv` supplies **242,468 accrual observations across 36,336 gigs — 23.6×**,
  which on 1/√n is roughly **±4.7%** and **±14%**. Re-running step 24 against the balanced
  frame needs **no new collection** and is the plan's Phase 0, with an explicit decision gate:
  a null that tight is itself the publishable result.

  | frame | gigs w/ reviews | gigs ≥2 quarters | accrual obs |
  |---|---:|---:|---:|
  | shipped historical | 1,373 | 997 | 5,403 |
  | shipped recent | 2,596 | 2,537 | 4,872 |
  | expanded (rule B) | 19,651 | 19,245 | 22,967 |
  | **balanced** | **36,700** | **36,336** | **242,468** |

- **`review_count` checks out as a cumulative-sales proxy on the balanced frame**: **95.5%**
  row coverage (92.6–98.1% per year through 2024, 71.8% in 2025) and only **1,395 of 242,468
  consecutive deltas negative — 0.58%**.
- **The window closes at 2024Q4, and this is now quantified.** Accrual observations per
  quarter run ~9,300–12,000 from 2019Q1 to 2024Q3, then **7,774 (2024Q4) → 1,605 (2025Q1) →
  598–847** thereafter. Per category it is worse: at 2026Q1, audio has 13 observations and
  translation 10. So the study covers ChatGPT (2022Q4), GPT-4 and the 2023–24 diffusion, but
  **not the 2025–26 agentic period** — consistent with the earlier finding that 2026Q2 Fiverr
  gig captures are ~all 403. Only a live forward crawl extends it.
- **Two design decisions taken up front rather than discovered later.** (1) "Transactions" is
  decomposed into per-gig demand (measurable), gig population (entry partly; **exit not at
  all** — `n_404 = 0` across 509,339 captures, so dormancy is the labelled proxy), and
  platform total (not measurable from the crawl), so no number is ever reported without its
  margin. (2) **Regressing a trending demand series on an AI score is ruled out before it is
  written** — step 29 retracted exactly that design for the price series on four tests, and a
  demand series is if anything more trending. The estimand is a cross-category DiD on a
  **pre-registered** exposure ranking, with the first-differences / linear-trend /
  CPI-U-placebo / Newey–West battery run on every specification.
- **Two gaps found that nothing in the repo currently addresses.** **Review-propensity drift**
  has never been tested — if buyers review less over time, accrual falls with no change in
  sales, and this contaminates the outcome directly. And **no Fiverr Inc. (NYSE: FVRR)
  reported GMV / active-buyer / spend-per-buyer data appears anywhere in the project**
  (grepped `drafts/`, `code/`, `plans/`, `data/`, `tests/`), despite being the only
  independent check on whether the proxy tracks real transactions at all.
- **User answered all three framing decisions the same day: causal from the start, a
  separate third paper, and the forward crawl deferred until after Phase 0.** The causal
  choice has one non-obvious consequence, now written into the plan as §8 and a new
  **Phase −1 that gates Phase 0**: Phase 0 re-runs step 24 and therefore *reveals the
  per-category demand breaks*, so an exposure ranking constructed afterwards is not
  pre-registered in any sense a reviewer would accept — it is the same objection that sank
  the elasticity table. The ranking and the full specification (outcome, break date, fixed
  effects, clustering, placebo window, battery pass/fail rule) must be sourced externally,
  dated and committed **before** the re-run. Causal framing also promotes **parallel trends**
  from an assumption to a required exhibit, with synthetic control on the low-exposure
  categories named in advance as the fallback, and converts **review-propensity drift** from
  a caveat into a threat to identification — the test that matters is *differential* drift by
  category, not drift as such. The 2024Q4 boundary becomes substantive rather than
  administrative: the treatment period is eight quarters, 2022Q4–2024Q4.

## 2026-08-13 — A combined plain-language walkthrough: methods + results in one file

- **User, after five rounds of edits: "I am still not clear what the data collection process
  looked like, nor the results"** → then asked for a combined methods-and-results document
  that is "super extra clear" on collection and on what changed to address limitations.
- **Diagnosis of why the earlier edits failed.** Every previous attempt rewrote the *paper's*
  prose, which is compressed, cross-referenced and hedged by design. The register was the
  problem, not the wording. What finally landed in conversation was a **worked example on
  real rows**, so that is what the new document is built around.
- **New `drafts/methods-and-results.md`** (2,879 words), at the drafts root rather than in
  `sections/`, so it is explicitly not a paper section and is outside the frozen-numbers
  checker. Seven parts: what we measure and why it is hard → the six collection steps with
  the funnel → **one real gig traced end to end** → how gigs become an index number → every
  problem and what we changed → the results → what we still cannot do.
- **Two things in it are computed live from the data rather than quoted from prose**, and
  both are new to the project's documentation: the gig
  `nickkonstan/transcribe-your-favorite-track-to-midi-data` with its actual quarterly
  medians ($10 in 2020Q1 → $80 in 2024Q4, from 66 captures in 2018Q3 alone), and a real
  bilateral — 2024Q3→2024Q4 on the recent panel, **1,132 matched gigs, 95 raised, 61 cut,
  976 unchanged, +0.83%**. The last of those makes a point no prose had: **most gigs do not
  change price in a quarter**; the index moves because a minority re-price.
- **The eight-row problem/change table is written with a "did it work?" column**, including
  the honest **no** on the 2017–2018 gap, which is a permanent loss rather than a repair.
- **Verified**: all 15 headline figures cross-checked against `data/pilot/paper-numbers.md`;
  the two computed figures verified against the CSVs; paper checker still PASS.

## 2026-08-13 — results.md states the final model

- **User: "in the results, talk about the final model we used."** `results.md` named
  GEKS-Jevons once, in a provenance note about which script it imports, and never said what
  the model actually does or why it beat the alternatives.
- **New "The final model, and why it is the one we use"** opens the analysis, in the same
  plain register as §0: what a matched-model index does (a gig against its own earlier
  price, so seller, quality and task difficulty cancel — none of which *can* be measured
  from an archived page); what the Jevons and GEKS halves each contribute, with GEKS
  explained as averaging over routes rather than multiplying a chain; the exact
  specification (full window, ≥3 gigs per quarter, ≥2 quarters per gig, `MIN_MATCH = 3`,
  gig-quarter medians, price guard, 200 bootstrap replications at seed 7, 1.96 × log-level
  SE, weighted geometric mean); and an explicit note that **all levels in this file are
  nominal**, the CPI-U deflation being a paper step not applied here.
- **The three rejected models are now stated as a table** with the reason for each — chained
  Jevons (irregular captures, +283.0% against +78.4%), time-product-dummy (agrees at
  $r = 0.996$ but imputes ~85% of cells on a 14.9%-filled panel), and the direct
  base-to-terminal comparison (kept as an independent check, too thin historically to be an
  index). Weighted multilaterals noted as never available, since an archived page shows a
  price but never a sale.
- Reading guide updated to point at the new block. No figure changed; `results.md` is
  outside the frozen table, and the paper checker still passes.

## 2026-08-13 — Section 3 cut to 3,996 words; Appendix A created

- **User: "can you make method.md under 4,000 words."** From 9,050 — a 56% cut.
- **Nothing was deleted.** Detail went to two homes: a **new `drafts/sections/appendix-a.md`**
  (2,277 words) for the estimation diagnostics, and `drafts/data-collection.md` — which
  already held the collection detail — for the pipeline narrative and operational figures.
- **Appendix A** carries: the chained-index decomposition; the extraction-method share table;
  the `MIN_MATCH` sweep; the precision-vs-*n* table with its finite-population correction and
  the independent validation of the bootstrap SEs; the window/base/threshold decomposition
  and the 7,400-vs-6,142 coding ceiling; the full hedonic table with its caveats and the
  per-category reputation elasticities; the five retracted-elasticity diagnostics; and the
  six-row corrections table. Wired into `drafts/main.md` and `code/36`'s `ORDER`.
- **§3 keeps** every claim, both figures, the weights table, the adequacy table, the two GEKS
  equations, and all 23 checker-required figures.
- **Verified**: checker PASS; every numeric token from the previous version accounted for
  across method + appendix. The first pass silently dropped ~15 figures — the extraction
  shares, the coding ceiling, the reputation SE and *n*, the base-quarter log SEs — caught by
  the token diff and restored into Appendix A. HTML re-rendered (11 tables); inline math
  confirmed converting, no raw LaTeX leaking.
- **Two prominence changes flagged, both reversible:** the U7 hedonic table now sits in
  Appendix A rather than §3.8 — still in the paper, which is what U7 required, but out of the
  body — and §3.9/§3.10 keep their claims and retraction language in the body while their
  tables move back. Restoring either to §3 costs the word budget something of equal size.
- Recorded as U16.

## 2026-08-13 — §3.1–3.2 rewritten to follow the collection as it actually happened

- **User: "Rewrite the entire method.md to follow the true data collection process."** Fifth
  request in a row about this section, after four incremental patches failed to make it land.
- **Root cause identified: the collection was being described four times** — the U13 phase
  roadmap, the eight-stage table, the U14 change table, and prose — none of them the story of
  what actually happened. That quadruple-telling, not the wording, is why it kept not landing.
- **§3.2 rebuilt around "The collection as it happened"**: seven dated steps, each forced by
  what the previous one revealed. The pipeline table is retitled "The pipeline as it now
  stands" and demoted from spine to replication reference.
- **§3.1 reordered for truth.** The archive's sparsity was stated *before* how the source was
  chosen, implying we knew and picked Fiverr anyway. It now follows the scoping decision as
  "What the census then revealed" — those figures are measured over the capture index and
  could not have existed before it. A 20-page probe cannot detect them; the text now says so.
- **The U13 roadmap table was deleted** as the redundant telling. Its intent survives in the
  narrative and a short "How this section is organised" paragraph; the phase mapping survives
  in the stage table's Phase column. Three prose paragraphs absorbed into the narrative.
- **Section numbering preserved deliberately** — 91 cross-references to `§3.x` across 13
  files, with §3.6 and §3.7 referenced 16 times each. Nothing was renumbered.
- Net **+650 words** on §3: this trades length for a structure that matches reality. No
  numeric token lost, checker PASS, HTML re-rendered. Recorded as U15.
- **Not done, and stated rather than quietly skipped:** §3.3–3.10 were not rewritten. They
  are estimator, precision, identification, rival explanations and corrections — not data
  collection — and §3's macro order is already collect → estimate → assess → test → correct.
  The open question from the earlier structural diagnosis (split §3 into method vs. how-well-
  it-worked, ~8,400 words across two sections) remains unanswered and unactioned.

## 2026-08-13 — §3.2: one limitation-and-response record instead of four scattered ones

- **User: "In method, describe the entire data collection process and what changes we made
  to address limitations."** The process was already there (roadmap + stage table, U13); the
  *responses to limitations* were scattered across four places — a five-row revision table,
  a two-sentence orphan paragraph on what the crawl's shape caused, §3.1's two-phase
  scoping argument, and a standalone subsection on the enlarged collections.
- **Consolidated into one eight-row table**: limitation the data revealed → change made →
  effect. Three responses that were never in the change log are now rows in it — the
  catalogue-first two-phase design (response to the archive's size), the 2018Q3 window floor
  (response to the severed chain), and the enlarged collections (response to matched gigs
  per pair being the binding unit). Rows are marked so a reader can tell the five pipeline
  revisions from the three design responses.
- **Prose kept only for the three with consequences**: the second crawl and why the paper
  has a splice, the rate lesson, and the Stage 5b retraction. The retraction paragraph now
  makes the *detection* the point — the defect survived every check until the extraction
  *share* table exposed it, which is the argument for reporting shares over a success rate.
- **"What the collection cannot fix" → "What no change could fix"**, so it reads as the
  boundary of the change log rather than an unrelated topic.
- Net −5 words on §3.2's back half while adding three responses and an effect column. No
  numeric token lost (diffed against previous version), checker PASS, HTML re-rendered.
  Recorded as U14.
- **Boundary held:** none of `results.md`'s measured figures for the enlarged collections
  entered the paper — they are outside the frozen table and belong to paper 2.

## 2026-08-13 — results.md rewritten in plain language

- **User: "I do not get what results.md means, can you make the language super clear."**
  The file was written for someone already fluent in the project's vocabulary — *bilateral*,
  *rule B*, *frame*, *not identified*, *shipped* — none of which it defined.
- **New §0 "What this file is, in plain terms"** opens it: the one question the file answers,
  a **table defining the eight terms** the rest of it uses (gig, panel gigs, quarter pair,
  matched gigs per pair, band, the ±5% requirement, index points, not identified), a table
  naming the **three data sets being compared** (shipped / expanded / balanced) and what
  distinguishes them, the four findings in four sentences, and a note on how to read the rest.
- **Every section's prose de-jargoned.** "Bilateral" → "quarter pair" with the reason it is
  the binding unit stated in words; "band" → "margin of error" at first use in each section;
  "the survivor filter" → an explicit sentence on what the paper's recent sample excludes and
  why that matters; §4's window-sensitivity result restated as "growth over a fixed span
  changes depending on where you start estimating, which ought to be impossible"; §5 opens
  with a plain statement of what the survivorship threat actually is before measuring it.
- **No figure changed.** Verified by diffing every numeric token against the previous
  version: all present, three references restored after the first pass dropped them (the
  `19 → 21 → 23 → 18` rebuild chain, the 403 wall cross-reference to §5.2, and the
  500-seller pilot as the contrast frame in §3).
- File remains outside the paper — not included by `drafts/main.md`, not scanned by
  `code/32-check-draft-numbers.py`, no HTML re-render needed. Pushed to `origin/mockup`.

## 2026-08-13 — Section 3 gains a collection roadmap

- **User: "I'm still confused by the data collection process in method.md"** → walked the
  pipeline step by step in conversation, then **"make this timeline extra clear in method.md
  so I know what to write in my paper."**
- **New "The collection in order" roadmap opens Section 3**, before §3.1: six phases —
  0 choose the source, 1 census the archive, 2 build the manifest offline, 3 download,
  4 read the prices, 5 build the panel — each pointing to the subsection that details it.
- **Three things the old text left implicit are now stated.** That phases 1–2 finish before
  any page is downloaded (the design decision the whole two-phase argument rests on); that
  the two crawls and the five revisions cut *across* the phase order rather than extending
  it; and the two terminology collisions (*index* = capture index vs price index, *pilot* =
  the 500-seller crawl vs the 20-page probe), hoisted into one fixed place at the head of
  the section.
- **§3.2's stage table gains a Phase column** so the eight stages map onto the roadmap, plus
  a sentence noting Stages 1–3 touch the capture index only, Stage 4 is the first request
  for a page, and both crawls share Stages 4–8.
- Net +383 words on a section U12 had compressed 22%; the now-redundant inline terminology
  sentence in §3.1 was removed in exchange. No figure added, moved or restated —
  `code/32-check-draft-numbers.py` PASS, HTML re-rendered. Recorded as U13 in
  `tests/method.test.md`.

## 2026-08-13 — The enlarged collections analysed: one worked, one largely did not

- **User: "can you make a results.md showing the results of the new data."** New
  `drafts/sections/results.md` (placed there on request; it is **not** included by
  `drafts/main.md` and is not scanned by the frozen-numbers checker, so it sits alongside
  the paper sections without entering the paper), from two new scripts — `code/43-enlarged-results.py` (panels, matched
  gigs per bilateral, GEKS with 200-replication bootstrap) and `code/44-entry-price-series.py`.
  Both import panel construction and the estimator from `21`/`19` rather than reimplementing
  them, so any difference from the paper is the data and not the code. Validated: run on the
  shipped historical panel the harness returns coding **312.8 ±61.1%** and translation
  **227.8**, the figures §3.7 and §3.4 already report.
- **The finding: sampling on gigs bought nothing; sampling on bilaterals bought a lot.** The
  expanded recent collection (rule B) raised the panel 8.6× (2,908 → 25,014) and matched
  gigs per bilateral only **1.2–2.0×**, leaving the bands unmoved. The balanced historical
  collection, quota-sampled on (category × adjacent quarter pair), raised the panel 37× and
  matched gigs per bilateral **32–112×**, cutting bands 3–7× — coding ±61.1% → ±13.1%. This
  is the strongest confirmation the project has of §3.6's claim that panel gigs are the
  wrong unit, and it is the design rule for any full-frame collection.
- **Both blocked plans are now decided.** `expanded-collection.md`: **do not rebuild** — the
  recent composite moves +0.8 points on a ±4.5% band. `balanced-history.md`: **rebuild** —
  three not-identified series become reportable and four category levels move by more than
  a third. Checkboxes closed and decision-log entries written in both.
- **A comparison error caught before it was written down.** The shipped historical
  categories terminate at seven *different* quarters (translation 2024Q3 … design 2025Q4),
  so comparing each panel at its own terminal quarter compares 2025Q1 with 2026Q1 and reads
  the gap as a panel effect. Struck at a common 2024Q3 instead, the pattern reverses for
  coding — 206.0 → 234.5, not 312.8 → 229.1 — and the real signature emerges: the thinnest
  categories fall hardest, the densest rise.
- **§3.7's window defect is reduced but not eliminated by density.** Audio's 76-point spread
  between a 2018Q3 and a 2020Q1 start collapses to **2.8** on the balanced panel, but
  coding, translation, marketing and video still move 45–57 points. §3.7's central claim
  survives the enlarged collection and should not be softened.
- **Entry prices, and a contamination check that changed the answer.** §6.2 asks for the
  entry series to be built inside one crawl; the balanced collection is that frame. But
  `review_count` is only reliable where `packageList` supplies it — the 2018 "new gig"
  cohort is **16% packageList** and returns a median entry price of \$395 against \$10 for
  established gigs, which is a parse artifact, not a price. Restricted to 2020+, where
  packageList supplies ≥95%: entry prices **double, \$10 → \$20 (2020–2024)**, against an
  incumbent composite of 184.5 — so entry is *not* flat, which would weaken the survivorship
  threat. But it splits where it matters: coding entry rises 8× while **design entry is flat
  at \$10**, and design carries 70.6% of the weight. Reported as preliminary with four
  stated reasons it must not enter the paper yet; the right next step is a matched
  entry-cohort index rather than a median.
- **Nothing here touches the paper.** Every figure comes from the enlarged panels, which are
  paper 2's frame; the frozen table and all draft sections are untouched.

## 2026-08-13 — Section 3 compressed to paper form; the plain account moves to the appendix

- **User: "update method.md and make it more concise in research paper form, there is a lot of content making it hard to digest."** Section 3 goes from **10,116 to 7,987 words (−22%)** and 463 to 322 lines. No figure was cut: a token-level diff of every number in the old and new versions confirms the only absences are four operational figures relocated to the appendix and superseded prose. `code/32-check-draft-numbers.py` PASS before and after.
- **§3.0 was the largest single cut, and it was yesterday's deliverable.** The plain-language account added on 2026-08-12 (U11) retold §3.1–3.2 in ordinary language — 1,300 words that duplicated the section they preceded. It moves **verbatim** to `drafts/data-collection.md` §0, which already declares itself the appendix method.md compresses. U11 stays satisfied because the plain account still exists; it is no longer inside the paper. This was the user's call, asked because deleting a recorded requirement is not a judgment to make silently.
- **Stages 1–8 become one in→out table** rather than eight prose blocks, with four short paragraphs kept for the steps that carry a decision rather than mechanics: the URL-shape rule as the pipeline's load-bearing assumption, sellers-not-gigs as a stated trade-off, un-checkpointed failures as the reproduction-relevant property, and clustering explicitly not used for the index. The one-line funnel was dropped as redundant — the table *is* the funnel now.
- **Six in-text self-corrections consolidated into a new §3.10.** The 404-attrition explanation, the "stratified" mislabel, the 10.9%→14.9% panel fill, the β=+0.103 unclustered SE, the 2.5M projection and the retracted 2025 fall were parentheticals interrupting the argument in five different subsections. They are now one table — earlier claim / what is correct / effect on results — which reads as an audit trail rather than as a series of interruptions, and makes visible that only one of the six changed a published result. The rating-scale defect follows as a closing note.
- **One inconsistency fixed in passing.** The old §3.8 parenthetical reported the gig-clustered reputation *t* as 5.26 while §3.8's own text reported 5.32. §3.10 states 5.32, matching the frozen table.
- **Also found, not yet fixed:** `abstract.md` and `conclusion.md` say the index is "built from 37,782 archived Fiverr gig-price snapshots." That figure is 22,632 + 15,150, the count *before* Stage 5b removes 3,846 non-gig rows — so the abstract quotes a denominator that includes the rows behind the paper's own retraction. The index is built from **33,936**. Stage 5b uses 37,782 correctly as a denominator; the abstract and conclusion use it wrongly as a sample size. Left alone because it is outside the requested edit and touches two other sections.

## 2026-08-12 — A plain-language §3.0, so the collection can be understood without the apparatus

- **User: "write the data collection process and changes made in simple clear terms for the ordinary person to understand."** New **§3.0 The Collection in Plain Terms**, opening Section 3: the whole story in ordinary language — what a gig and a snapshot are, why the archive is the only way to see past prices, the compare-a-gig-to-itself idea, the size problem and the catalogue-first solution, how the 500 sellers were chosen, why 1.8M archived gigs collapse to ~1,000 usable ones, the five changes with what forced each, and the three limits no further collecting fixes. It ends by telling a reader they may stop there.
- **Delivered as an addition rather than a rewrite, and this is the substantive call.** Plainifying §3.1–3.2 in place would have stripped the rate limits, seeds, script citations and in→out counts that make the section replicable — the audit-trail function the write-up template exists to enforce. The plain account and the auditable one want different things from the same prose, so they are now two passes over the same material rather than one compromised one.
- **The retraction is stated in the plain version too, not just the technical one.** The Stage 5b defect is told as a story an ordinary reader can follow — a budget slider's default read as if it were a price, Fiverr changing it from \$1,000 to \$500, every category appearing to halve — and it says plainly that we had published that as a real 2025 fall, that it was not real, and that §4.6 shows before and after.
- **Fixed `drafts/render.py`'s escaped-dollar leak** while it was in front of me — noted but not fixed on 2026-08-10, and newly conspicuous because §3.0 quotes dollar figures in prose. `_inline` now unescapes `\$`; the draft was showing `\$10,000`. Equations verified intact (the draft's LaTeX never uses `\$`), and `36-build-paper-page.py` already handled it.
- Checker PASS, both surfaces re-rendered, `tests/method.test.md` U11 added.

## 2026-08-12 — §3.1–3.2 restructured into named sub-sections, and the index census measured rather than estimated

- **User: "explain in clear words what the pilot data collection/crawl looked like" → "put this in method.md in sections".** §3.1 and §3.2 rewritten as labelled `####` sub-sections in the order a reader actually needs them, **without renumbering** — §3.2–3.9 are cross-referenced from four other sections, so the `### 3.x` headings are fixed and the new structure sits one level below. §3.2 now runs one sub-section per pipeline stage (build the index not the corpus → narrow 60M records to eligible sellers → draw the sample, sellers not gigs → download → read the prices → Stage 5b → stages 6–8), then the funnel, the crawl's structural consequences, the revision history, the ceilings, the enlarged collections, and the closing caution.
- **The one genuinely new argumentative block: "What the shape of this crawl caused."** The splice and the 2020Q1 window were already justified separately, several hundred words apart. Stated together and up front, they are consequences of a single design choice — sellers selected for long histories thin out at the trailing edge, and the archive is severed at the early end — which is a weaker claim to defend than two independent ones and is how a reviewer will read them anyway.
- **A terminology note, because three separate exercises here are called "pilot"** and the draft used the word for all of them: the 20-page feasibility probe (§3.1), the 500-seller pilot crawl (every historical figure in the paper), and the 1,946-page extraction pilot run ahead of the balanced collection. Unqualified, it now means the second.
- **The scoping estimate is now reported against its own measurement.** §3.1 quoted "roughly 2.5 million distinct gig URLs and 4–20 TB" — the 2026-03-21 projection, made before the harvest, and never checked against it. Measured off `gig-pages-deduped.tsv` (`runs/index-census/`): **1,778,505 distinct gig base URLs**, 22,739,659 deduplicated status-200 captures, **2.474 TB** of archived compressed bytes ≈ 12 TB raw at this corpus's measured 5.0× ratio. **The estimate was 1.4× high on URLs and right on volume**, and the paper now gives both — the estimate because it is what forced the two-phase design, the measurement because it is what the archive turned out to hold.
  - **The trap in that count, recorded because it is a factor of 3.1.** CDX urlkeys retain query strings, so the file's 5,587,932 distinct urlkeys collapse to 1,778,505 distinct gigs; 4.2M of 22.7M rows carry a tracking parameter. And stripping `?…` breaks the file's sort order (`/a/b-c` sorts between `/a/b` and `/a/b?x`), so `uniq` over-counts and the distinct count needs a hash set.
- **Two staleness fixes carried in the same edit.** The enlarged collections were still described as "in flight" and "running" — both completed 2026-08-10 — and the balanced crawl was quoted at **41,235 gigs**, which is its *manifest target*; delivered is **39,933 gigs / 292,447 priced rows**. Both now read as complete, at delivered sizes.
- **No frozen figure moved.** `code/32-check-draft-numbers.py` PASS before and after. Both surfaces re-rendered: `drafts/draft-2026-08-12.html`, `drafts/paper-page.html`. `tests/method.test.md` U10 added.

## 2026-08-10 — The collection written up in full, and both enlarged crawls found to have finished

- **User: "add this more fleshed out in the drafts folder."** New `drafts/data-collection.md` — the complete account of the collection, filled against `drafts/templates/data-collection-section.md`: source selection with the pre-registered gate and the rejected alternatives, scoping, all eight pipeline stages with the parameters needed to re-run them, the cost/settings table, the five revisions, the archive's ceilings, the enlarged collections, and the artifact index. §3.1–3.2 of `method.md` remains the publishable compression; this is the appendix. Stated explicitly in the header that **`method.md` wins on any number**, since the frozen-table checker governs `drafts/sections/` only and does not see this file.
- **Both in-flight collections had completed and their plans did not record it.** Checked rather than assumed, and both are now checked off with their real outcomes. **Expanded (rule B):** 67,377 newly captured of 79,191 manifest rows → extraction over the combined corpus, 82,967 files → **82,966 rows, 1 `no_price_found`**. **Balanced (historical):** 298,009 → **291,997 captured**, 293,943 files → **292,447 rows, 1,496 `no_price_found` (0.51%)**, disk **36 GB against the 35.1 GB year-weighted estimate**. Both wrote to separate files; `recent-prices.csv` and `pilot-prices.csv` are untouched, so no paper figure moves. Next step on both is the same: re-measure matched gigs per bilateral against the ±5% requirement.
- **One distinction the document had to nail down because the two numbers look contradictory.** The status ledger reports `n_404 = 0` across 509,339 in-window captures, but the download logs record **178 (expanded) and 11,501 (balanced) 404s**. These are different quantities: the ledger's is the **origin** status recorded in the CDX index at capture time, the log's is a **replay** failure from `web.archive.org/web/<ts>id_/<url>`. Only the first bears on whether gig exit is observable, and it is still zero — the exit-unmeasurable finding stands.
- File count reconciles exactly in both crawls (files = priced rows + extraction errors), which is what validates that extraction ran over the whole combined corpus rather than a subset.

## 2026-08-10 — The write-up half of the collection template: a fill-in skeleton for §3.1–3.2

- **User: "can you give me a template for the data collection process for my paper."** The existing `plans/templates/data-collection.md` covers how to *run* a campaign; `drafts/paper-template.md` compresses the write-up into two table rows. New `drafts/templates/data-collection-section.md` fills the gap — a fill-in skeleton for the collection section itself, reverse-engineered from `method.md` §3.1–3.2 as it stands after five revisions. Cross-linked from `paper-template.md` §3.
- **Six slots, of which four exist because their absence was the failure mode:** source and window (with the floor imposed by data, not chosen); pipeline stage-by-stage with in→out counts; **how the collection changed**; **what the collection cannot fix**; **collections in flight that contribute nothing to this paper**; and a closing caution naming the unit that actually governs precision.
- **The rule it encodes:** a collection section is an audit trail, not an advertisement — anything the collection got wrong is cheaper to publish than to have found. Two corollaries carried through every slot: every count carries the count it came from, and the selection rule is stated in terms of what the *estimator* consumes rather than what was collected.
- Includes the pre-registered source-gate table (thresholds set before the probe, rejected alternatives with measured reasons), the "what the gate did *not* establish" paragraph, the Stage 5b post-hoc-exclusion pattern with its sibling audit, a 14-item numeric checklist, and a reproducibility artifact table. Worked examples from the current draft are marked `→ current:` for deletion when adapting.

## 2026-08-10 — A reusable template for collection campaigns, cut from the three that have already run

- **User: "can you give me a template for the data collection process."** New `plans/templates/data-collection.md` — a fill-in execution plan for any campaign that fetches a new corpus or re-selects a manifest, plus a driver-script skeleton, an artifact-paths table, and the nine checks that have each caught a real failure.
- **Cut from what the recent, rule-B expanded and link-balanced historical campaigns converged on independently**, so it is a record of practice rather than a proposal: census headroom → choose the rule → cost by year → pilot the unfamiliar stratum → download → extract to a new file → adequacy check → explicit rebuild gate.
- **The ordering is the substantive part.** Three of the four design changes those campaigns made came out of steps 1, 3 and 4 (census, per-year cost, pilot), and each would have been discovered *after* the crawl had those steps come later — census found the binding constraint was the selection rule not the archive (the shipped panel used 3.2% of what was on disk), per-year sizing corrected a disk estimate by 2.2× and reversed the target decision, and the pilot surfaced an `old_json` extraction path no modern page uses.
- Carries forward as defaults the settings that were learned the hard way: 10/10 rate (45% transient failures at 20/20, zero at 10/10, same 5.71 pages/s), `--gzip`, a new prices file every time, matched-gigs-per-bilateral as the only sample-size unit that binds, and watching `extraction_method` shares rather than the success rate — the `hire/*` Pro pages parsed "successfully" at 25.1% of rows and inverted the recent trend in 6 of 7 categories.

## 2026-08-10 — The collection's *revision history* is now in the paper, and checking it against the logs falsified two claims the draft was making

- **User: "write how we first collected data then the changes we made over time."** §3.2 gains a closing block, **"How the collection changed"** — a five-row table (sampling rule → second crawl → 20 req/s → 10 req/s → gzip → Stage 5b) giving the trigger for each revision, then prose on the three that have consequences a reader needs.
- **The framing that makes this worth including rather than an appendix:** every revision was *forced by something the data revealed*, none was chosen in advance, so the sequence is itself evidence about what archival price collection costs. Stated that way in the lead-in.
- **The three expanded:** (1) *why the paper has a splice at all* — the original design was one crawl, and sellers selected for long histories are exactly the ones who thin out at the trailing edge, so the recent crawl exists because the first design structurally cannot measure the recent period; nearly every asymmetry in the results, including which categories are identified, traces to depth-selected vs density-selected sampling. (2) *the rate lesson* — 20/20 logged **12,336 transient failures against 15,150 successes (45%)**, absorbed only because failures are un-checkpointed; 10/10 logs **zero** at the same 5.71 pages/s. Written as "we were well past diminishing returns and did not know until it was measured," not as a success. (3) *Stage 5b as the only revision that retracted a published finding*.
- **Added: what no collection change can fix** — `n_404 = 0` across 509,339 captures (exit needs a live forward crawl); status-200 captures 280,779 in 202409 → **66** in 202603 (trailing edge closed, re-harvesting recovers nothing); **1** matched gig at 2017Q3→Q4 against 8,084 at 2018Q3→Q4 (the 2018Q3 floor is archive-imposed). And the two in-flight collections, marked as contributing **no number** to this paper, with coding's unreachable ceiling (needs ≈7,400 matched gigs/pair; index supplies at most 6,142).

**Two claims in the draft did not survive checking against the logs.** Both are corrections to *explanations*, not to numbers — 22,632, 85.1%, 15,150 and everything downstream are unchanged.

- **The historical crawl's 15% shortfall is not 404 attrition.** The draft said the missing 3,971 entries "returned 404s (archived in the index, content no longer served), consistent with normal Wayback attrition." `data/pilot/download-log.tsv` records **23,798 successes, 102 hard failures and zero 404s**. Reconciled: those 23,798 success lines resolve to **22,632 distinct output paths** — verified equal to the file count on disk — so the bulk of the gap is manifest rows collapsing onto a gig-day file already retrieved. That is deduplication, not loss, and the draft was crediting the archive with a failure mode it did not exhibit.
- **"No 403 in either crawl" was too strong**, and I had written it into §3.2 earlier the same day off a June progress note. The logs show **3** 403s (recent crawl), which is still no evidence of blocking — but the 45% failure rate at 20 req/s is the real signal about request-rate discipline, and it is now reported instead of the reassuring one.
- Both surfaces re-rendered; `tests/method.test.md` U9 added and last-reviewed moved to 2026-08-10.

## 2026-08-10 — The data collection §§ now describe how the collection was *decided*, not just what it produced — and the word "stratified" was wrong

- **User: "can you summarize the initial data collection process" → "can you put this in the draft".** The method section reported the pipeline's *outputs* (60M → 22.7M → 48,643 → 500 → 26,603 → 22,632) but almost none of its *decisions*, so a reader could not tell why Fiverr, why an index-first two-phase design, or why sellers rather than gigs. Added to `drafts/sections/method.md`, **without renumbering** — §3.2–3.9 are cross-referenced from four other sections, so the new material sits inside §3.1 and §3.2 as bolded blocks.
- **§3.1 gains two gates.** *How the source was chosen*: the three pre-registered pass/fail criteria from the 2026-03-21 feasibility pilot (coverage ≥10 snapshots/≥3 years/≥3 categories; extraction ≥80%, got 20/20; tracking ≥5 sellers at ≥3 dates, got 6), plus the Upwork/Freelancer fallback probe and why neither was needed. Followed by an explicit statement that the gate tested *parseability and longitudinality*, not adequacy — that question is §3.6/§3.7 and is answered negatively, so a 20-page gate must not be read as validating the sample. *How the collection was scoped*: the 2.5M-gig / 4–20 TB size estimate forcing the index-first two-phase design, whose real payoff is that sampling runs against a **census** rather than against whatever a crawler reached first.
- **§3.2 Stages 1–5 and 7 gain mechanics + script citations** (`code/01`…`code/10`): letter-prefix CDX pagination and the six retained fields; digest-based deduplication; external-sort streaming (the in-memory version OOM'd at 22M records, which is why it is written that way); keyword classification against `data/task-taxonomy.md`; the `id_` raw-capture URL form; checkpointed resume; and the failure taxonomy that matters operationally — **404 permanent, 429/timeout transient and deliberately un-checkpointed so a re-run retries exactly those, no 403 in either crawl**.
- **Two things stated as trade-offs rather than facts.** Seller-level sampling now carries its cost (it spreads the download budget over less of the category space; it buys the within-seller panel §3.8 needs). And the **two-segment URL rule is flagged as the pipeline's load-bearing assumption about what a gig is**, with a forward link to Stage 5b — the rule's failure is already in the paper as a −10.2% observation exclusion, and it should be introduced as fallible where it is first applied, not only where it broke.
- **A factual correction: the 500-seller draw is not stratified.** The draft said "stratified random sample." The production route (`06c-pilot-longitudinal.py` → `07-pilot-500.py`) is two **uniform** random draws with a fixed seed, 48,643 → 5,000 → 500. The stratification-by-snapshot-count lives in `06-pilot-sample.py`, an earlier sampling design that never reached the production manifest. §3.2 now says uniform and carries a parenthetical recording the correction, matching how the paper handles its other superseded figures.
- Rendered both surfaces: `drafts/draft-2026-08-10.html` (`render.py`) and `drafts/paper-page.html` (`code/36-build-paper-page.py`). Test file updated: `tests/method.test.md` U8. **No numbers changed** — every count, share and rate in the section is as it was; only the surrounding explanation is new.
- *(Noted, not fixed: `render.py` leaks the backslash in `\$` escapes — the working draft shows `\$10,000`. `36-build-paper-page.py` handles it correctly, so it affects only the internal draft surface.)*

## 2026-08-09 — The balanced historical crawl is committed at the *larger* target, because the estimate that made it look unaffordable measured page size on the wrong decade

- **User: "can you collect more data if possible".** Yes — the balanced-history full download is launched at **target 1200 matched gigs per (category, adjacent quarter pair)**: `data/pilot/balanced-manifest.tsv`, **298,009 pages / 41,235 gigs / 2018Q3–2026Q1**, via `code/run-balanced-pipeline.sh`. Steady-state **10.84 pages/s** measured over 90 s, **ETA ~7.5 h**. Extraction is chained on completion into a **new** file, `data/pilot/balanced-prices.csv`; `pilot-prices.csv` feeds the frozen paper numbers and is not touched.
- **THE 600-VS-1200 DECISION TURNED ON A MEASUREMENT ERROR IN MY OWN COST TABLE, AND 1200 WAS NEVER ACTUALLY MARGINAL.** The plan costed target 1200 at **~78 GB against 95 GB free**, which is exactly the band where the cautious call is 600. That figure applied a flat **~275 KB/page** taken from the 2024Q3+ gzipped corpus. **Fiverr gig pages have grown ~7× over the window**, and the pilot measures it directly: **37 KB (2018), 39, 61, 94, 131, 172, 244, 248, 268 KB (2026)**. Weighting by the manifest's own year distribution — which is 33% pre-2021 — gives **35.1 GB, not 78**. The larger option was affordable the whole time and the smaller one would have been chosen on an artifact.
  - Worth keeping as a general caution: a per-unit constant calibrated on the newest data will misprice any historical collection, and the error compounds with how far back the collection reaches.
- **Chose 1200 on what it buys, not on what it costs.** The thin pairs are precisely where §6.4 marks the historical panel **not identified**, and 600 leaves most of them thin. **But this does not double coverage everywhere and the plan says so:** 2018Q3–2019Q2, translation, and audio are **archive-exhausted at either target** (`runs/history-headroom/balanced-coverage.md` marks 100 of 210 cells with `*`). 1200 buys density in the middle years and nothing at the ends.
- **The pilot cleared extraction against pre-2020 layouts, which was the gate.** 1,946 pages stratified **equally per quarter** — deliberately over-weighting the oldest, least-validated layouts — returned **1,936 rows, 10 `no_price_found`, 99.5%**. Method mix: `packageList` 1,759, **`old_json` 96**, `dollar_fallback` 80, `html_span` 1. The `old_json` path carries rows that **no page in the modern corpus uses**, which is the specific risk the pilot existed to find.
- **Disk watchdog on an 11-hour unattended run.** The driver polls every 5 min and stops the download if free space falls under 10 GB — a full root filesystem takes the box down, not just the crawl. Projected headroom is comfortable (35 of 95 GB); this is insurance, not a forecast.
- **The 1,946 pilot pages are reused rather than re-fetched** — step 08's `existing_path()` matches either storage form, the same mechanism that skipped 11,744 pages on the expanded run.
- **Status: download in flight, ~5,400/298,009 at time of writing.** Uncommitted. No index rebuild, no `docs/data.json` change, no draft change — 19 → 21 → 23 → 18 on the enlarged panel remains a separate, deliberate decision.

## 2026-08-09 — Collection was never archive-limited: the recent panel used 3.2% of the gigs already in the index, and the survivor filter is why

- **User: "help me collect more gig data".** Measured the headroom before crawling anything. **The binding constraint is `13-recent-manifest.py`, not the Wayback Machine.** Plan: `plans/active/expanded-collection.md`. **Nothing in `drafts/`, `docs/` or the frozen paper numbers was touched** — this is paper 2's frame, per the 2026-08-05 decision, and the pilot's numbers stay frozen.
- **`code/37-collection-headroom.py` censuses the existing index over the 2024Q3+ window: 22.7M rows scanned, 1,053,705 status-200 snapshots, and 91,849 distinct gigs. The shipped recent panel uses 2,930 of them — 3.2%.** Four selection rules costed per category:
  - **A shipped** (≥2 quarters **and** ≥1 snapshot in 2025Q3–2026Q2): **2,930 gigs / 11,424 downloads**
  - **B no-survivor** (≥2 quarters anywhere): **25,051 gigs / 79,191 downloads** — **8.5×**
  - **C any-pair** (≥2 months): 34,458 / 100,596; **D all**: 91,849 / 157,987
  - **Rule A reproduces the production panel exactly (2,930 post-`gigfilter`)**, which is what validates the census against something known.
- **CHOSE RULE B, which is also the rule `plans/todo.md` demands on independent grounds.** Step 13's trailing-window requirement is what makes the recent panel a survivor panel (36.5% of gigs last seen in the final quarter vs 0.4% historically; 1,747 of 2,930 "first captured" at `WINDOW_START` by construction). Dropping it removes the selection *and* is the largest honest gain — C's extra 9,407 gigs span ≥2 months but only one quarter, so they contribute nothing to a **quarterly** matched-model index, and D's are singletons that cannot yield a price relative at all. `code/38-expanded-manifest.py` → `data/pilot/expanded-manifest.tsv`, **79,191 rows / 25,051 gigs**, a strict superset of `recent-manifest.tsv`.
- **A FRESH CDX HARVEST WOULD BUY ALMOST NOTHING, AND THAT IS NOW MEASURED RATHER THAN ASSUMED.** The index was harvested 2026-03-22, so the obvious move was to re-crawl for the missing five months. Direct probes of the live CDX API for 2026Q2–Q3 return **almost exclusively 403** on Fiverr gig URLs — prefix `ba`, 2026Q2: **21 captures, zero status-200**. Our own index shows the same collapse from the other side: **280,779 status-200 snapshots in 202409 against 66 in 202603**. Archiving of these pages has effectively stopped; the trailing edge is not recoverable by re-harvesting, and the data that exists is already on disk.
- **EXIT IS UNMEASURABLE FROM WAYBACK, FULL STOP — the todo item asking the crawl to "record the 404s" cannot be satisfied by any archive-based collection.** `code/39-status-ledger.py` was built to settle it: it streams all **60.0M raw CDX rows** (the raw files are the *only* place non-200 statuses survive — `02-filter-gig-pages.py` dropped them, so `gig-pages-classified.tsv` is status-200 by construction and cannot answer this) and tallies every status class for the 25,051 selected gigs. Result over **509,339 in-window captures: `n_404 = 0`**, with 1,155 403s, 1,588 3xx, 1,662 5xx. **The archive stops re-requesting a delisted URL rather than recording its death.** Requirement (a) of that todo item must be respecified as a **live forward crawl on a fixed schedule**; requirement (b), not selecting on survival, is what rule B delivers. Ledger: `data/pilot/gig-status-ledger.tsv`, 80,039 gig-month rows.
  - I first wrote this ledger against the classified file and it came back with **zero** non-200 rows — not because there are none upstream, but because that file had already been filtered. Caught it by noticing the ledger row count equalled the census's status-200 gig-month count exactly. The vacuous version was removed from step 38, which now says in its docstring why it cannot answer the question.
- **Storage: gzip, measured at 5.0× on this corpus.** Rule B stored plain would be **~93 GB against 115 GB free**; gzipped it is **~17.6 GB**. `08-download-html.py` gains `--gzip`, `--chunk` (one coroutine per row is fine at 15k rows and not at 79k on a 5 GB box) and `--limit` for pilots, and **reuses plain files already on disk so the 15,150 existing pages are not re-fetched**. `09-extract-prices.py` reads both forms.
  - **One defect caught in the smoke test:** `.stem` on `<date>_<slug>.html.gz` leaves the `.html`, which would have landed inside every gzipped row's `slug` and silently split each gig into two identities. Handled explicitly; verified 0 malformed rows.
- **PILOT BEFORE SCALE, and it changed the crawl settings.** 500 rows at concurrency 10 / 10 req/s: **440 ok, 0 failures, 0 retries, 5.71 pages/s**. The June–July run at 20/20 logged **12,336 failures against 15,150 successes — 45%**. Throughput is the same or better at the gentler setting, so it is strictly preferable. Extraction re-run over the combined corpus: **15,590 files, 100% success, 0 errors.**
- **Full download launched** (~64,000 new pages, sustaining **8.27 pages/s**, ETA ~2.5 h). Resumable from `data/pilot/expanded-download-checkpoint.txt`.
- **Expected payoff, and it is partial — stated now rather than discovered later.** Extrapolating each category's current matched-gigs-per-bilateral against the ±5% requirement from `code/34-figures.py`: **design ~1,120 vs 1,100 needed (clears)**, writing ~680 vs 900 (close), video ~370 vs 1,600, **coding ~670 vs 7,400 (nowhere near)**. Rule B likely brings one category over the adequacy line and one near it. **Coding cannot be fixed at archive density** — that is a property of what Wayback captured, not of the selection rule, and it should inform whether paper 2 is archive-based at all.
- **Status: apparatus built (uncommitted), download in flight.** Steps 37/38/39 added; `08` and `09` extended backward-compatibly. Extraction is chained to run on completion into a **new** file, `data/pilot/expanded-prices.csv` — `recent-prices.csv` is left alone because it feeds `docs/data.json` and the frozen paper numbers. No index rebuild, no site refresh, no draft change.

## 2026-08-06 — The hedonic regression published in full: §3.8 gets the coefficient table it was summarising

- **User: "so what is the linear regression model you made" → "ok publish these".** Asked where, because the paper and the live site are materially different audiences; **user chose the paper**. §3.8 previously carried the hedonic as prose only — the headline numbers were there but **no reader could check a coefficient**, which is not a defensible way to publish a regression the paper leans on for its design argument.
- **Added the estimating equation and a three-column table** to `drafts/sections/method.md` §3.8: (1) cross-section, (2) + quarter FE, (3) the volume slope re-estimated within-gig. Every coefficient with its *t*, plus $R^2$, *n* and cluster counts per column. Bold marks $|t| > 1.96$; the caption states that task-type coefficients are price levels relative to design and carry no AI-exposure content, which is the most likely misreading.
  - Rating **+0.310 (2.76)** → **+0.338 (3.10)** under quarter FE; coding **+0.808 (9.92)**, marketing +0.625, video +0.337, writing +0.153, translation **−0.506 (−2.61)**, audio n.s.; $R^2$ **0.065** → 0.096.
  - The reversal is now legible as a table row rather than a claim: `ln(1+reviews)` reads **+0.022 (1.64)** in column (1), **−0.001** in (2), and **+0.133 (7.87)** in (3).
- **Two things the prose had left out and the table forced in.** The **second reading of "prior gigs"** is now reported rather than only mentioned — substituting seller gig counts gives **−0.051 (t = −0.59)** and leaves every other coefficient unchanged, which is the check a reviewer would ask for given the two readings are *negatively* correlated (−0.333). And the **rating-scale sensitivity is given as three numbers** (rescale +0.310 / drop +0.311 / raw +0.302) instead of the assertion that the bug does not matter.
- **Removed a duplication I created.** The degeneracy caveat (sd 0.26, 41% at exactly 5.0) now sits once, in the paragraph that bounds how the rating slope should be read; the closing parenthetical was trimmed to the scale defect alone, which is the part that concerns *future* row-level use of the field rather than this estimate.
- **Verified:** `code/32-check-draft-numbers.py` still **PASSES**; `code/35-bibliography.py` still resolves all 63 keys with none unresolved; `drafts/render.py` re-renders with the table as real `<table>` markup. No new numbers were introduced — every figure comes from `scratchpad/hedonic.out`, which re-ran byte-identical on 2026-08-05.
- **Logged as `method.test.md` U7**, with an explicit note that the user chose the paper over the site when offered both, so the result should not be moved to the live site without asking.
- **Status: committed.** Paper and tests only; no code, data or site changes.

## 2026-08-06 — Phase 4 apparatus: five figures, a resolved bibliography, and the assumption-free check — and recomputing the precision curve moved the paper's own design requirement

- **Phase 4 of `plans/active/publication.md`.** Three new scripts (33, 34, 35), five figures, a 63-entry bibliography, and the last method FAIL closed. **Every `<!-- FIGURE -->` placeholder is gone and every `[CITE-]` placeholder now resolves.** Nothing in `data/` or the index pipeline was touched.
- **`code/33-direct-matched-check.py` closes `method.test.md` R10, the last FAIL in that file.** The critique is that both estimators §3.4 compares GEKS against share its panel construction, so their agreement is partly internal consistency. The direct base-to-terminal bilateral Jevons shares **none** of GEKS's machinery — no chain, no transitivity correction, no link quarters, no regression, no imputation.
  - **Recent panel: GEKS agrees closely.** writing **+1.4%** (n=65 matched gigs), coding **+1.9%** (58), design **+2.7%** (275), marketing **−4.7%** (47), video **−5.0%** (63), audio **+1.7%** (6). **Median absolute gap 2.7%**, 6 of 7 inside GEKS's own band.
  - **Historical panel: the check is uninformative, and the paper says so rather than omitting it.** Only **1–4 gigs** survive both endpoints per category and the direct figure disagrees by up to **63.6%** (writing, on a single gig). That is a statement about the direct estimator, not about GEKS — and it is another view of §3.7's sparsity. Publishing only the recent half would have been the flattering half.
  - The earlier version of this check could not be quoted because **its figures predated the Stage 5b non-gig exclusion**, which moved the composite by 26 real points. This is re-measured on the production panel.
- **`code/34-figures.py` emits five standalone SVGs** — composite real+nominal with CPI-U and band; seven category panels with bands; raw-vs-reputation-adjusted band with a β sensitivity strip; the precision curve; link-path support per quarter. SVG rather than matplotlib, which is not installed here and would add a dependency the site's hand-built inline SVG convention does not need. All five parse as XML and are embedded in the draft with numbered captions.
- **THE FIGURE CHANGED THE RESULT IT WAS DRAWING. Figure 4's curve was recomputed rather than transcribed, and it was wrong before.** Subsampling **without** replacement has variance $(1-n/N)$ times the with-replacement variance, so the raw subsample spread understates the precision loss as *n* approaches the panel size — and is **zero by construction at n=N**. The published SEs come from a bootstrap that resamples *with* replacement, so the two were not on the same footing. Applying the finite-population correction:
  - **The requirement is now per-category and far worse in one case.** ±5% needs **≈900 matched gigs (writing), 1,100 (design), 1,600 (video) — and ≈7,400 (coding)**, whose per-gig information content is much lower. The previously published **"850–2,500 per category" is superseded**; the honest statement is that a full-frame collection must be sized on the **worst** category, not the average.
  - **The corrected curve independently validates the published bootstrap SEs.** Extrapolated to each category's own full *N*: design **±4.4%** vs published ±4.8%, writing **±7.8%** vs ±8.3%, video **±12.9%** vs ±11.9%, coding **±20.0%** vs ±17.1%. Two procedures sharing no machinery agree to within 3 points in every case — so the curve is now a result, not only an exhibit.
  - The old range was quoted in **§1, §3.6, §6.1, §7 and on the live site**. All five are restated, and the FAQ mirror regenerated.
- **`code/35-bibliography.py` + `drafts/references.json`: 63 entries, every placeholder resolves, and 7 are flagged as submission blockers.** The script fails the run on an unresolved key, reports defined-but-uncited entries, and generates `drafts/sections/references.md` with unverified entries **visibly marked so the flag survives into the rendered draft**.
  - **7 UNVERIFIED, all of them in §2.** `ainsworth-nelson-2004` (neither authors nor year confirmable; the nearest known work is Ainsworth et al., JCDL **2011**), `piazzesi-schneider-2016` (published **2020**), `guha-2024` (the benchmark is NeurIPS **2023**), `whalley-2024` (unidentifiable), plus three platform statistics that could not be traced to a citable publication — `fiverr-2025`'s 641%, `upwork-2024`'s 60%/40%, and `upwork-freelance-forward`. **An unverified citation is worse than a missing one**, because a reader cannot tell it apart from a checked one. Each must be verified, replaced, or the sentence cut. Logged as `related-work.test.md` R16, which stays **FAIL**.
  - **One misattribution fixed:** the Massenkoff & McCrory paper was cited under an `anthropic-2025` key — naming the data provider rather than the authors — in both the prose and the positioning table.
- **Found and fixed a defect in the renderer while embedding the figures: `drafts/render.py` had no image support**, so all five `![...](...)` embeds would have rendered as literal markdown text in the HTML. Added image handling (rewriting repo-root-relative paths to be relative to `drafts/`, where the HTML lives) plus a CSS rule, and added the generated references to `drafts/main.md`.
- **Test files updated:** `method.test.md` **1 FAIL → 0** (R10 closed with the new figures; R12's matched-gig requirement restated to the corrected values); `related-work.test.md` **0 FAIL → 1** (new R16 for the unverified citations, new R17 for the citation-key fix) — that is a real regression in the count and it is deliberate, because the citations were previously untested rather than passing; `conclusion.test.md` R3 restated off the corrected requirement.
- **Verified:** all three new scripts `py_compile` clean and run to exit 0; `code/33` and `code/34` reproduce the figures quoted in §3.4 and §3.6 exactly; `code/32-check-draft-numbers.py` still **PASSES** (22 frozen figures present, 6 retracted figures properly cued); `code/35` exits 0 with **no unresolved keys**; all five SVGs parse; `drafts/render.py` renders `draft-2026-08-06.html` with **0 missing includes, 5 `<img>` tags and 0 literal `![` left**.
- **Known remaining gaps:** the 7 unverified citations; `model-paper.test.md` still 10 BLOCKED; `master.test.md` never reviewed; the pre-AI placebo exhibit measured but unwritten (`findings.test.md` R2); the unclustered SE still live inside `code/22-confounder-diagnostics.py`; the `rating` 10-point scale bug in the extractor.
- **Status: Phase 4 figures and citations done and committed.** Nothing in `data/`, `docs/data.json` or the pipeline changed; the one site edit is the FAQ's restated matched-gig requirement.

## 2026-08-06 — Phases 2 and 3 done: numbers frozen, and every prose section rewritten off them. The paper is no longer four and a half months behind the analysis

- **User: "ok do it" (execute Phase 3).** Did Phase 2 first, because §4 cannot be written until the numbers are frozen. **All eight prose sections now current; the draft renders clean.**
- **PHASE 2 — `code/30-freeze-numbers.py` writes `data/pilot/paper-numbers.{md,json}`** from `docs/data.json`. Every section quotes this one table; no section computes its own figures. That is the mechanism that let the draft drift into carrying the retired chained series' 312 peak alongside §3's post-exclusion GEKS numbers.
  - **Caught a convention mismatch that would have put the paper and the site at odds.** My first pass computed bands as `(exp(1.96·se)−1)`, giving design ±5.0% — which flips design across the ±5% adequacy line. `docs/ipi.js` publishes `halfWidth = se => 196·se`, the linear form, giving **±4.8%**. Matched the site exactly (design ±4.8%, writing ±8.3%, marketing ±7.7%, video ±11.9%, audio ±13.9%, coding ±17.1%, translation ±29.2%, composite ±3.7%) and the exact asymmetric CI on the level is carried in its own column.
  - **No pipeline re-run was needed**, as D1–D4 predicted: `docs/data.json` (generated 2026-07-31) stands.
- **PHASE 3 — all eight sections.** §3 Methods and §4 Findings rewritten; **abstract, §1, §5 and §7 written from scratch**; §6 Limitations rewritten; §2 corrected at the claim level; the FAQ mirror regenerated.
  - **§3 Methods (2,345 → 5,367 words)** now carries every Phase 1 decision: the D1 `MIN_MATCH` sweep, the 2020Q1 window with the 2018Q3 hard floor evidenced, CPI-U deflation (new §3.5), the ±5% criterion with the precision-vs-n curve and matched-gigs-per-bilateral (new §3.6), **the link-path identification failure (new §3.7)**, the rival explanations including the hedonic reversal (new §3.8), and **§3.9, which retracts the elasticity regression and prints the diagnostics**. R8's 2019Q1/2020Q1 base inconsistency fixed; the unreproducible "10.9% filled" restated as 14.9% with the definition and an explicit note.
  - **§4 Findings** rewritten on real-as-headline. Retracts the 2025 reversal in the text rather than deleting it, refuses the category ranking with the overlapping intervals shown, and adds **§4.6 reporting the non-gig exclusion as a finding in its own right** — the before/after is the most useful thing in the paper for anyone else building prices from web archives.
  - **§2 Related Work was self-contradictory and is fixed at six points.** It still promised the elasticity construct, framed benchmarks as the regressor, justified a forecasting component the paper does not have, and had a positioning-table row reading "Forecasting: **Yes**". Left the 68 `[CITE-]` placeholders for Phase 4 — those are citations, not claims.
  - **The FAQ mirror is now GENERATED, not copied** (`code/31-mirror-faq.py`, HTML → markdown, 15 sections / 5,113 words). It had drifted three weeks and carried retracted figures while the live page was correct. A hand-maintained mirror will drift again; this one cannot.
- **Built a guard so the freeze is enforced, not just declared.** `code/32-check-draft-numbers.py` scans the governed sections for every frozen figure and greps for retracted ones, requiring a retraction cue nearby. **Passes: 22 frozen figures present, 6 retracted figures all properly cued.** Two false positives fixed in the checker itself — `\b312\b` was matching coding's unrelated **312.8**, and sentence-splitting on decimals truncated context so it could not see the retraction cue preceding a hit.
- **Test infrastructure brought current — seven files, five of which had never been reviewed.** `method.test.md` goes **5 FAIL + 1 BLOCKED → 1 FAIL** (R10, the direct matched-pair check, is genuinely still not in the draft *and* its figures predate the Stage 5b exclusion, so it stays FAIL rather than being quietly closed); R5, R6, R8, R9, R11, R12 all closed, five new tests added (R13–R17). `findings.test.md` goes **5 FAIL → 0 FAIL** with two PARTIALs kept honest (R2's placebo exhibit is still unwritten; R3's survivorship threat is acknowledged but unbounded). `abstract`, `introduction`, `discussion`, `limitations`, `conclusion` written from empty stubs.
- **Verified:** all four new scripts `py_compile` clean and run to exit 0. `drafts/render.py` renders `draft-2026-08-06.html` with **0 missing includes**. The frozen table reproduces the site's published bands exactly. Descriptive statistics in §4.1 were **computed** from the panels rather than carried over — the previous draft's "median \$25" was right for the recent panel and wrong for the historical one (\$20).
- **Known remaining gaps, stated rather than glossed:** 86 `[CITE-]` placeholders and 5 `<!-- FIGURE -->` placeholders (Phase 4); `method.test.md` R10 still FAIL; the pre-AI placebo exhibit measured but not written into §4; `model-paper.test.md` still 10 BLOCKED; `master.test.md` never reviewed.
- **Status: draft rewritten and committed.** Nothing in `data/` (beyond the new frozen table), `docs/` or the pipeline was modified.

## 2026-08-06 — D4 closed, and Phase 1 with it: the elasticity table is a spurious regression and must be cut; the chain-drift comparison survives only if rebuilt on the production panel

- **Phase 1 decision D4 of `plans/active/publication.md`** — the last one. Built `code/29-chained-elasticity-audit.py`. Two separate questions with different answers: does the chained-vs-GEKS drift comparison survive, and does the elasticity table survive. **Measurement only; nothing in `data/`, `docs/` or `drafts/` was modified.** Output: `scratchpad/chained-elasticity-audit.out`.
- **DECISION: cut the elasticity table outright. Keep the chain-drift comparison only in a rebuilt form, computed on the production panel at the production base — which means it should not come from `code/12-panel-ipi.py` at all.**
- **THE ELASTICITY TABLE IS A SPURIOUS REGRESSION, and three independent tests say so.** It regresses log price index on log AI-benchmark score over ~20 quarterly observations, two trending series, no control group.
  - **Serial correlation is total. Durbin–Watson runs 0.22 to 1.08 in all six categories** (audio 0.22, design 0.26, marketing 0.33, coding 0.50, writing 0.60, translation 1.08). Every `p_value` in `panel-elasticity.csv` — eight of eight at 0.0000–0.0016 — is computed from a standard error that assumption invalidates. Newey–West at lag 4 shrinks the t by 1.3–1.8× but cannot rescue it, because the problem is the trend, not the SE.
  - **PLACEBO 1 — a plain linear time trend fits BETTER than the AI score in all six categories.** R²(time) vs R²(AI): **design 0.979 vs 0.412, marketing 0.981 vs 0.934, coding 0.974 vs 0.909, writing 0.941 vs 0.864, audio 0.925 vs 0.805, translation 0.913 vs 0.882.** A variable with zero AI content explains more. The AI score is proxying for time.
  - **PLACEBO 2 — swapping in CPI-U fits at least as well in five of six** (design 0.976, writing 0.970, audio 0.953, translation 0.951, coding 0.939; marketing 0.926 vs 0.934 is the one exception) **and returns "CPI elasticities" of +4.56 to +8.73.** Nobody would publish a claim that gig prices rise 5–9% per 1% of CPI, and it is the same regression on the same data.
  - **In first differences the relationship disappears.** Δln P on Δln(AI): **t = 0.26 (audio), −0.02 (coding), 0.48 (design), 2.24 (marketing), −0.34 (translation), 0.20 (writing)** — one marginal result out of six tests, which is what chance produces. Whatever the levels regression is fitting, it is not a relationship between the changes.
- **The ranking — the only thing the table is actually used for — is not stable to anything.** Against the shipped table, the same estimator differing only in panel construction and base quarter gives **Spearman ρ = +0.314 (p = 0.544)**: **design falls from +1.139, the most elastic of eight, to +0.295, fourth of six**, and writing rises from seventh to second. Across price series, as-built vs adjacent is ρ = +1.000 (so the TD1 defect is *not* what drives the ordering) but **as-built vs GEKS is ρ = +0.657 (p = 0.156)**, with translation moving from fifth to second. This is a fourth independent route to the conclusion already reached from price precision, the margin bounds and the DiD probe: **the pilot cannot rank categories by AI impact.**
- **THE CHAIN-DRIFT COMPARISON IS ALSO NOT PUBLISHABLE AS IT STANDS, and the reason is new.** §3.4 attributes the whole chained-vs-GEKS gap (+217.7% vs +44.6%) to chain drift. Decomposing it on the production panel — as-built → adjacent-only isolates the TD1 defect, adjacent-only → GEKS isolates genuine drift:
  - **defect × / drift ×: audio 1.05 / 1.93, coding 1.80 / 0.88, design 1.47 / 1.81, marketing 1.89 / 1.41, translation 1.89 / 0.57, video 1.32 / 1.36, writing 1.28 / 1.37.**
  - **The defect's share of the total log gap runs from 7% (audio) to 802% (translation)** — it exceeds 100% wherever drift runs the other way, **and in coding and translation it does: the adjacent-only chain lands BELOW GEKS** (coding 273.7 vs 312.8, translation 130.4 vs 227.8). So §3.4 is wrong in both directions at once — part of the gap is a coding defect, and the residual "drift" has no consistent sign.
  - **The defect fires often and can fire hugely.** 24–35% of within-gig links span more than one quarter (translation 34.5%, marketing 27.7%, coding 26.1%, audio 25.5%, design 24.8%, writing 24.1%, video 23.9%), and **the longest span is 35 quarters in coding** — an 8.75-year price change booked as a single-quarter change and then chained on top of the gigs that *were* observed in between.
- **RECOMMENDATION, and it retires TD1 by decision rather than by fixing it.** Do not repair `code/12-panel-ipi.py` for the paper. Its own panel and 2019Q1 base are themselves a source of divergence — D3 settled the base at 2020Q1 — and the reconstruction here already computes the comparison on the production panel at the production base. §3.4 should quote **that** three-way decomposition and state the honest conclusion: the chained index diverges from GEKS by **−43% to +93%** across categories **with no consistent sign**, which is an argument for GEKS and not a measurement of drift. `code/12-panel-ipi.py` stays in the repo for the audit trail. **Closes `tests/method.test.md` R9.**
- **The reconstruction is validated, which is what lets it replace step 12.** Re-based to 2020Q1=100 it reproduces the shipped per-category chained level **exactly in four of seven categories** — audio 731.0, marketing 782.2, translation 238.5, video 601.9 — and to within 3–6% in coding (492.4 vs 464.9), design (381.0 vs 359.7) and writing (359.2 vs 348.8), the residual being step 12's different panel. So it is step 12's estimator, isolated.
- **Verified:** `py_compile` clean; runs end to end (exit 0). Both chained variants and GEKS are built on the same `19-tpd-index.py` panel so the comparison is not contaminated by panel differences; the AI-score construction (benchmark map, quarterly interpolation, min-max normalisation, `fid_coco` sign flip) reproduces step 12's exactly. OLS, Newey–West and Durbin–Watson are implemented directly — `statsmodels` is not installed in this environment — with Newey–West checked to collapse to the OLS SE at lag 0.
- **Corrected one thing mid-build:** the "for the record" block first read `panel-ipi.csv`, which is composite-only (`quarter,ipi`) and has no category columns, so it silently printed nothing; the per-category shipped chain lives in `panel-category-indices.csv`. That is also what made the reconstruction check possible.
- **PHASE 1 IS NOW COMPLETE (D1, D1b/D1c pending write-up, D2, D3, D4). Phase 2 needs no pipeline re-run:** D1 keeps `MIN_MATCH = 3`, D3 keeps the window at 2020Q1, D2 is an additional published band rather than a change to the index, and D4 removes outputs rather than changing them. The frozen numbers table can be cut from the existing `docs/data.json`.
- **Status: exploratory finding. `code/29-chained-elasticity-audit.py` added; `progress.md`, `plans/todo.md` and `plans/active/publication.md` updated. Nothing else touched.**

## 2026-08-06 — D3 closed: the window stays 2020Q1 — and the per-category growth turns out not to be window-invariant, which is the same defect as D1c wearing a different hat

- **Phase 1 decision D3 of `plans/active/publication.md`.** Built `code/28-window-choice.py` — 5 window starts (2018Q1 … 2020Q1) × 7 categories, plus the spliced composite, the pre-period pair density, the placebo, a `MIN_MATCH=4` stress test and a mechanism decomposition. Imports `19-tpd-index.py` and `21-geks-index.py` **unmodified** and varies only `window_start`; `build_geks`'s rng sequence is replicated exactly so every window's bootstrap SEs are comparable to production. **Measurement only; nothing in `data/`, `docs/` or `drafts/` was modified.** Output: `scratchpad/window-choice.out`.
- **DECISION: keep the published window at 2020Q1. Publish 2018Q3–2020Q1 as a separate pre-AI exhibit, not as part of the headline series.** Four measured reasons, none of which is the one the plan anticipated:
  - **Nothing is gained on the headline.** Composite 2020Q1→2026Q1 reads **+76.8% (2018Q1 and 2018Q3), +74.3% (2019Q1), +76.8% (2019Q3), +78.4% (production)** nominal; real **+39.5 / +37.5 / +39.4 / +40.7%**. The spread is inside the composite's own ±3.7% band.
  - **Precision gets worse in four of seven categories, by up to 4×.** ±95% at terminal, production → 2018Q3: **design ±23.3% → ±93.7%, writing ±38.1% → ±103.2%, marketing ±86.5% → ±182.6%, translation ±83.8% → ±129.5%.** Only audio (±118.6% → ±92.1%) and video (±75.8% → ±71.0%) improve; coding is flat.
  - **Translation gains nothing at all** — it bases at **2019Q4 under every window from 2018Q1 through 2019Q3**, because no earlier quarter carries three distinct gigs. And **audio's pre-period chain is broken**: the adjacent pairs 2018Q3→2018Q4, 2018Q4→2019Q1 and 2019Q2→2019Q3 carry **2 matched gigs each**, below `MIN_MATCH=3`, so GEKS has to route around three of the six pre-2020 links.
  - **The extended series is *more* fragile to `MIN_MATCH`, not less.** At k=4, **five of seven categories change their terminal quarter on the 2018Q3 window against three on 2020Q1** — and audio collapses to its own base quarter (100.0 by construction) while translation falls back to 2019Q4. Extending the window buys length by spending robustness.
- **THE BY-PRODUCT IS BIGGER THAN THE DECISION: the published per-category growth is not window-invariant.** Over the **identical span** 2020Q1→terminal, audio reads **+103.9% on the 2018Q3 window and +258.7% on the 2020Q1 window**. Spreads across the five windows: **audio 76.0%, marketing 42.1%, design 27.6%, writing 26.3%, coding 21.3%, video 16.4%, translation 1.7%.** Levels are deterministic — no rng — so this is the estimator, not sampling noise.
- **Mechanism proven, not asserted, and it decomposes cleanly into two channels of which only one fires.** GEKS sets ln P(base,t) as a mean over link quarters l of [lnP(base,l) + lnP(l,t)], so the base terms cancel out of a growth rate **only if the link sets for t and for the pivot coincide**. Widening the window adds link quarters and breaks that.
  - **Channel (a), the gig set: nil.** `_log_panel` keeps a gig only with ≥2 observations inside the window, so widening changes the gig count (audio 54 vs 50, design 313 vs 272) — but **max |Δ lnP| over every shared bilateral is 0.0000 in all seven categories.** The extra gigs cannot enter a post-2020 bilateral, because a gig with one observation in the window contributes to none.
  - **Channel (b), the link set: everything.** Recomputing the same growth on the link quarters both windows share, with the base cancelled algebraically, gives **exactly identical answers** — audio **142.0% under both**, design 56.6%, marketing 172.7%, coding 218.2%, translation 137.8%, video 144.2%. Note that **neither published audio figure equals 142.0%**: both are artifacts of which links happened to be available.
  - **The shared link sets are tiny** — |L\*| = **2 (coding), 3 (audio, design, translation), 4 (video), 5 (marketing), 0 (writing)**. That is the same sparsity D1c found, reached from a different direction.
- **This unifies three separately-recorded findings into one defect.** `MIN_MATCH` (D1c, coding +129% on a one-step change), the base quarter (2026-08-03, pooled 2020Q1 level 75.7 / 96.0 / 75.5) and now the window all move the historical per-category answer far more than its stated band, and all three do it **through the same channel — how many link paths support a quarter**. The paper should name the mechanism once and mark the historical per-category series accordingly, rather than treating these as three unrelated robustness footnotes.
- **The 2019Q1 window's anomalies are a spike quarter, and the mechanism predicts the sign.** On the 2018Q3 base, 2019Q1 sits well above both neighbours in five of six resolvable categories — **video 226.7 (vs 101.8 and 124.3), design 154.0 (vs 103.9, 116.3), writing 119.7 (vs 103.2, 93.2), audio 126.0, coding 120.1**. Basing there makes a high denominator, so the 2019Q1 window reports the *smallest* growth for design, video and writing. **Marketing dips instead (76.8), and its growth correspondingly reads high — +173.5% vs the 2018Q3 window's +98.5%.** The sign flips exactly where the mechanism says it should, which is the check that this is the base and not noise.
- **Why the composite survives when its components do not — verified, and worth stating in §3.** The splice links the two panels at **2024Q3**, so only the **2020Q1→2024Q3** leg of the historical series ever reaches the headline, and that leg is far steadier than the full span: spreads **design 4.0%, video 4.5%, translation 1.7%, writing 10.7%, audio 18.2%, marketing 24.4%, coding 33.0%** — against 27.6% / 16.4% / 1.7% / 26.3% / 76.0% / 42.1% / 21.3% over 2020Q1→terminal. The fragile late-historical quarters are truncated by the splice, and design — the steadiest at 4.0% — carries ~71% of the review weight.
- **The placebo, on a single unspliced 2018Q3-based series.** Annualised growth pre- vs post-2022Q4 is **higher after ChatGPT in all seven categories**: audio 0.4% → 5.8%, coding 9.6% → 68.2%, design 10.3% → 12.1%, marketing 11.3% → 19.2%, translation 22.6% → 23.6%, video 16.9% → 21.1%, writing 7.0% → 20.6%. Two cautions before this is quoted: **coding's post leg runs to its not-identified 2025Q1 terminal**, and this pre/post split is cut at **2022Q4**, so it is *not* the same statistic as `plans/todo.md`'s 2018Q3–2019Q4 pre-AI figures (audio −38%, writing −20%, …) and must not be presented as agreeing or disagreeing with them. Composite pre-AI leg **2018Q3→2020Q1: +10.0% nominal, +7.0% real.**
- **Verified:** `py_compile` clean; runs end to end (exit 0, 42s). Piloted on two categories before the full sweep per the agile-research rule. Two run-time self-checks are built into the script: the production window reproduces the shipped `panel-category-indices-geks.csv` to **0.005 index points**, and the local re-basing helper reproduces `tpd.chain_category` to **0.0000 points** at `START_Q`, so the alternative-base composite is the production splice with one argument changed. The invariance mechanism was confirmed by direct decomposition (shared-bilateral gap and fixed-link-set recompute), not inferred from the level movement.
- **Status: exploratory finding. `code/28-window-choice.py` added; `progress.md`, `plans/todo.md` and `plans/active/publication.md` updated. Nothing else touched.**

## 2026-08-06 — D2 closed: the reputation band is +39.7% to +79.0%, β must be pooled, and step 22's t-statistic was inflated by unclustered SEs

- **Phase 1 decision D2 of `plans/active/publication.md`.** Built `code/27-reputation-band.py`. Adjusts the **production** panels cell-by-cell — `adjusted = p · exp(−β·ln(1+reviews))` — rather than rebuilding a separate panel, so raw and adjusted differ only by the adjustment. **Measurement only; nothing in `data/`, `docs/` or `drafts/` was modified.** Output: `scratchpad/reputation-band.out`.
- **THE DELIVERABLE — the band. Composite 2020Q1→2026Q1: raw +79.0%, reputation-adjusted +39.7%, width 39.3 points.** The adjusted series is a **lower bound, not a correction**: reviews are cumulative *sales*, so β absorbs demand as well as reputation, and if AI suppressed demand the adjustment eats part of the effect the paper is trying to measure. Raw stays the headline; the pair is published as a range.
- **Per category, historical 2024Q3 (raw → adjusted): writing 189.2 → 138.9 (−27%), translation 227.8 → 168.7 (−26%), marketing 267.7 → 210.2 (−21%), design 146.8 → 120.1 (−18%), audio 310.1 → 257.2 (−17%), video 276.8 → 229.4 (−17%), coding 205.0 → 171.7 (−16%).** The recent segment barely moves (−3% to −4%) because its window is only seven quarters, so little review accumulation occurs inside it.
- **β IS POOLED, and the reason is decisive rather than a preference.** Estimated per category, **audio (−0.089) and translation (−0.080) come back wrong-signed** (both insignificant, n=443/148). Adjusting those categories with their own β would *raise* their index — "stripping out reputation" would add price, which is not interpretable. Pooled **β = +0.1068 (se 0.0201, t 5.32)** on 9,762 transitions / 3,419 gigs; a doubling of a gig's reviews moves its price **+7.7%**. This closes the open sub-question in `plans/todo.md` ("whether β is estimated pooled or per category").
- **Per-category β for the record:** marketing +0.206 (t 3.27), writing +0.192 (t 4.87), coding +0.161 (t 3.47), video +0.108 (t 2.97), design +0.075 (t 4.20), then the two wrong-signed ones. The spread is wide enough that pooling is a real assumption, not a formality, and should be stated as one.
- **A REAL DEFECT IN STEP 22: its β standard error is unclustered.** It runs plain OLS on 9,543 within-gig first differences drawn from 3,298 gigs, so errors are correlated within gig. Gig-clustered SEs are **1.93× larger — se 0.0101 → 0.0195, t 10.19 → 5.26**. β survives comfortably; **the published t = 10.19 does not** and is quoted in `progress.md` (2026-07-29), `plans/todo.md` and `tests/findings.test.md` R1. All three need restating to t ≈ 5.3.
- **Sensitivity — the band's width is driven by β, and β is not pinned tightly.** Composite full-window: **β=0 → +79.0%, 0.05 → +59.4%, 0.10 → +41.9%, 0.15 → +26.4%, 0.20 → +12.5%.** Roughly −3.3 points of composite growth per 0.01 of β. With a clustered 95% CI on β of about [0.067, 0.146], the adjusted lower bound itself ranges from roughly +50% to +28% — so the band's floor is soft and should be presented with that caveat rather than as a single number.
- **Implication worth flagging for §4, not yet computed properly:** deflating the adjusted composite by the same CPI-U factor used elsewhere (+26.8%) gives roughly **139.7 / 1.268 ≈ 110 (+10%) real and reputation-adjusted**, against the published **+40.7% real**. That is arithmetic on two separately-produced numbers, not a run of `23-real-index.py` on the adjusted series — it needs producing properly before it appears anywhere.
- **Corrected myself mid-build.** I first recorded that Test B2's magnitudes were unquotable because it runs on a merged panel (design 1,637 gigs vs production's 330). The panel construction does differ, but the levels do not: B2's 2024Q3 figures agree with the published index (design 146.8 vs 146.7, translation 227.8 vs 227.8, audio 310.1 vs 307.4, writing 189.5 vs 186.0). The 146.8-vs-156.6 gap I flagged was a **quarter mismatch** — 156.6 is design's *terminal* quarter (2025Q4), not its 2024Q3 level. The script now verifies the raw column against the unrestricted production index **at run time** so this cannot drift again; the restriction to review-carrying cells (90.2% historical, 89.6% recent) moves no category by more than **1.7%**.
- **Verified:** `py_compile` clean; runs end to end (exit 0). Piloted before scaling. Panels come from `19-tpd-index.py` unmodified and the index from `21-geks-index.py` unmodified; `ols_cluster` is imported from step 25 rather than reimplemented. The unclustered-vs-clustered comparison reproduces step 22's exact spec before re-running it with clustering, so the 1.93× is measured on identical data.
- **Status: exploratory finding. `code/27-reputation-band.py` added; `progress.md` and `plans/active/publication.md` updated. Nothing else touched, NOT committed.**

## 2026-08-06 — `MIN_MATCH` swept: the coverage-for-precision trade-off does not exist, and the historical coding level is not identified

- **Phase 1 decision D1 of `plans/active/publication.md`.** Built `code/26-minmatch-sensitivity.py` — 8 values of `MIN_MATCH` × 7 categories × 2 segments, plus the spliced composite. Imports `19-tpd-index.py` and `21-geks-index.py` **unmodified** and varies only `geks.MIN_MATCH`; `build_geks`'s rng sequence is replicated exactly (one `default_rng(SEED)` consumed over `CATS` in order) so every sweep value is comparable to production at k=3. **Measurement only; nothing in `data/`, `docs/` or `drafts/` was modified.** Output: `scratchpad/minmatch-sensitivity.out`.
- **THE PREMISE OF THE DECISION WAS WRONG. Raising `MIN_MATCH` buys no precision anywhere, and in the thin categories it destroys it.** Recent segment, ±95% on the terminal level: **audio ±11.3% (k=1) → ±16.0% (k=3) → ±30.3% (k=5) → ±34.1% (k=6)** — strictly monotone in the wrong direction. design (±4.8%), marketing (±9.0%), writing (±8.0%), coding (±20.7%) and video (±13.0%) are **flat to within 0.2pp across k=1…10** — the knob does nothing at all where the panel is dense.
- **The mechanism, and it is the part worth carrying into the paper: `MIN_MATCH` does not add matched gigs to a comparison, it deletes comparisons.** GEKS sets a quarter's level as the mean over every populated link path base→l→t. Raising the bar shrinks that mean's support; in the limit it collapses to a single bilateral and the "index" is one comparison wearing an index's clothes.
- **Demonstrated on coding's historical series, which turns out not to be identified.** Terminal level **312.8 at k=3 → 717.7 at k=4 → 220.0 at k=5** (the last on a different terminal quarter, 2024Q4 not 2025Q1). Diagnosed rather than asserted: at k=3 the terminal quarter is supported by **8 link paths**; at k=4 exactly **one** survives, and it is the most extreme of the eight (+1.97 in logs). The direct 2020Q1→2025Q1 bilateral carries **1 matched gig** and is never used at any k. **A +129% swing from a one-step change in a robustness knob sits far outside coding's own ±61% band** — so the band understates the uncertainty, and the right description is *not identified*, not *imprecise*.
- **Levels move on the historical segment generally, not just for coding:** design 156.6 → 127.1 (−18.8% at k≥5), video 244.2 → 167.1 (k=4) → 300.9 (k=5), translation 227.8 → 168.2 (k=4) → 95.3 (k=6), audio 358.7 → 219.4 (k=6). Marketing is stable to k=6 then collapses to 170.7 at k=8. The recent segment is far better behaved — five of seven categories do not move at all.
- **The headline composite is robust, which is the reassuring half.** Spliced composite 2020Q1→2026Q1: **+76.4% (k=1), +76.6%, +78.4% (prod), +77.6%, +78.2%, +77.8% (k=6)**, falling to +65.7% / +64.8% only at k=8/10 where several categories have stopped resolving. **The published +78.4% does not depend on this choice.**
- **Two reading traps found in my own first-pass table and now marked in the output.** (1) The **terminal quarter changes with k** as quarters drop out, so a naive "vs k=3" column silently compares different quarters — those rows now carry `!`. (2) Cells reporting **±0.0% are degenerate, not precise**: only the base quarter survived, so the index is 100.0 by construction (translation k=8/10, audio k=10 historical). Same failure mode as the n=full row of the 2026-08-05 precision curve, and it would have read as perfect precision.
- **Recommendation for D1: keep `MIN_MATCH = 3`, and stop treating it as the precision lever.** Lowering to 1 genuinely helps audio (±16.0% → ±11.3%) but lets a bilateral rest on a single gig, which is an obvious reviewer target for a gain confined to the two thinnest categories. Raising it is strictly worse on every measured axis. The thin-category problem is real but belongs to the **adequacy criterion** (bands and no ranking claims, already shipped on the site), not to `MIN_MATCH`. This **decouples D1 from the precision problem it was assumed to solve** and unblocks Phase 2 without a pipeline re-run.
- **Closes `tests/method.test.md` R5**, which has been asking for exactly this table ("the sensitivity check is not yet in the draft"), and supplies §3 with a methods exhibit. Note R5's stated magnitude — "relaxing 3→1 moves audio's final level +17 pts and marketing's −13 pts" — is **historical-segment** behaviour; on the recent segment audio moves +1.3% and marketing 0.0%. Both belong in the restatement.
- **Verified:** `py_compile` clean; runs end to end (exit 0). Piloted on two categories before the full sweep per the agile-research rule. Levels are deterministic (no rng), so the coding swing is a property of the estimator and was confirmed by counting link paths directly, not inferred from the level.
- **Status: exploratory finding. `code/26-minmatch-sensitivity.py` added; `progress.md` and `plans/active/publication.md` updated. Nothing else touched, NOT committed.**

## 2026-08-05 — Publication readiness audited: the analysis is four and a half months ahead of the prose, and the abstract is retracted rather than stale

- **User: "I want to get this to research publication soon, what steps should I take. also I want to build a linear regression model using average gig rating, a worker's number of prior gigs, and task type."** The regression **already existed** — it was built earlier the same day as `code/25-hedonic-regression.py` in response to the identical instruction. Re-ran it: exit 0, **byte-identical** to the stored `scratchpad/hedonic.out`, so the result is reproducible. Reported the results rather than rebuilding. No new analysis code written.
- **The binding constraint on publication is the writing, not the analysis — and that was not visible from `plans/todo.md`.** Every prose section except `method.md` and `faq.md` (both 2026-07-31) is dated **2026-03-23**. Ten separate findings have landed since and none are in the paper.
- **The abstract is RETRACTED, not merely out of date. Every substantive claim in it is superseded:**
  - "composite IPI peaked at **312** (base 2019Q1=100) … declining 21% in early 2025" — that is the **naive chained series, removed from the site 2026-07-27**. The published GEKS composite is **+78.4% nominal / +40.7% real** over 2020Q1→2026Q1, and the post-2024Q3 decline it describes was the `hire/*` artifact fixed 2026-07-31.
  - "price elasticities range from **−0.49 audio to +1.10 design**" — `panel-elasticity.csv` is already on the to-do list **to be retired**; it returns design as the most AI-elastic category when design is the flattest in real terms.
  - "**9 service categories** … **2017 to 2025**" — 7 categories; **2018Q3 is a hard floor** (2026-08-03: the matched chain is severed in 2017); data runs to 2026Q1.
  - AI framed as the driver — against the **descriptive-first decision of 2026-07-30**.
  - Consequence: the abstract must be **written from scratch**, not edited. Same for intro, discussion and conclusion.
- **Apparatus gap measured, not estimated:** **85 `[CITE-]` placeholders** (68 in `related-work.md`, 9 in `method.md`, 5 in `discussion.md`), **4 unfilled `<!-- FIGURE -->`** placeholders (all in `findings.md`). Test layers: `method.test.md` **5 FAIL + 1 BLOCKED**, `model-paper.test.md` **10 BLOCKED**, and **seven of ten test files have never been reviewed** (`Last reviewed: —`).
- **USER DECISION: publish the pilot as a measurement paper; the full-scale collection becomes paper 2.** Presented the fork explicitly because every margin measured over the past week converges on the same bound — price precision fails in six of seven categories, demand and dormancy are null at ±23–66%, the DiD CI spans −15% to +88%, and exit/entry are unmeasurable by crawl construction. **The pilot cannot rank categories by AI impact on any margin**, and claiming otherwise is the single thing most likely to sink the paper. It *can* deliver the instrument, the bounds, and the forward design requirements — with the negative results as part of the contribution rather than an embarrassment.
- **New `plans/active/publication.md`** sequences it in four phases, with **Phase 1 gating Phase 3**: settle the four number-moving decisions (`MIN_MATCH` + the ±5% criterion jointly, the reputation-adjusted band, the 2020Q1-vs-2018Q3 window, and whether the chained/elasticity path survives at all) → re-run 12 → 14 → 19 → 21 → 23 → 18 once and freeze a single numbers table every section quotes from → rewrite the prose → figures, citations, tests. Drafting §4 before the decisions are made guarantees a second rewrite.
- **Found a defect in the test infrastructure itself.** `tests/method.test.md` **R12 still carries the two-category version** of the adequacy failure — it names only audio (±13.9%) and translation (±29.2%), while the corrected second pass on 2026-08-05 found **six of seven fail at 2026Q1** and that **coding (±17.1%) is worse than audio**. The site and `progress.md` carry the corrected scope; the test file does not. A test that understates its own finding will not catch it. Logged as its own Active item.
- **Status: audit + planning only. `plans/active/publication.md` created; `plans/todo.md` and `progress.md` updated. No code, data, docs or draft files were modified.**

## 2026-08-05 — Hedonic regression built: rating is priced, task type dominates, and the volume slope reverses sign between the cross-section and within-gig

- **User: "I want to build a linear regression model using average gig rating of a worker, a worker's number of prior gigs, and task type."** Built as `code/25-hedonic-regression.py`; output `scratchpad/hedonic.out`. **Measurement only; nothing in `data/`, `docs/` or `drafts/` was modified.** Estimated on 3,753 gigs (one row per gig at its latest capture, so heavily-archived gigs do not dominate), seller-clustered SEs.
- **Two data problems found before fitting anything, both now handled in code.**
  - **`rating` has a scale bug:** 217 historical rows carry ratings in (5, 10] — pre-2019 Fiverr displayed a **10-point scale** and the extractor wrote it into the same column as the 5-point one, so an untreated fit reads 10.0 as twice as good as 5.0. `RATING_FIX` runs all three treatments (`rescale`/`drop`/`raw`); **the choice turns out not to matter here** (b(rating) = +0.3097 / +0.3110 / +0.3023), because only 167 of the affected rows survive to a gig's latest capture. The bug is real and should still be fixed upstream in the extractor.
  - **`rating` is nearly degenerate:** at gig level sd = **0.26**, IQR **4.80–5.00**, 90% at ≥4.8, **41% exactly 5.0**. A "per rating point" coefficient is an extrapolation far outside the data, so the script reports the slope **per 0.1 point** as the primary reading.
- **"Number of prior gigs" is ambiguous and the two readings are NEGATIVELY correlated (−0.333).** `seller_gigs` (distinct gigs a seller offers) is near-constant — median 1 in the recent crawl, only 8.9% of sellers offer more than one, and the historical distribution is an artefact of the 500-seller sample. `reviews` (cumulative orders) is the reading that varies (sd 2.09 in logs) and is the "prior work done" notion the question is about. Both are estimated; results below use reviews.
- **Result 1 — rating is priced, and it is the one seller-level variable that is.** b(rating) = **+0.310 (se 0.112, t = 2.76)**, i.e. **+3.15% per 0.1 rating point**. Survives quarter fixed effects (**+0.338, t = 3.10**). Given the compression, this is a large association across a narrow range.
- **Result 2 — task type dominates the fit, and the spread is wide.** Relative to design: **coding +124%** (t 9.9), **marketing +87%** (t 6.5), **video +40%** (t 3.7), **writing +17%** (t 2.1), audio +20% (n.s.), **translation −40%** (t −2.6). Task type contributes most of the model's explanatory power — and total R² is only **0.065** (0.096 with quarter FE), so posted price is overwhelmingly *not* explained by these three variables.
- **Result 3 — THE FINDING: the volume slope reverses between the cross-section and within-gig.** Cross-sectional b(ln reviews) = **+0.022 (t 1.64), indistinguishable from zero**, and it goes to **−0.001** with quarter FE. But the **same slope estimated within a gig over time is +0.133 (se 0.017, t 7.87)** — a **6.1×** difference — closely reproducing step 22 Test B's +0.103 on a different sample cut.
  - **Interpretation: the cross-section does not inflate a real effect, it cancels one.** A gig that accumulates orders raises its own price ~**+10% per doubling**; but across sellers, high volume is also what *cheap high-throughput* sellers have. The two forces offset — a **Simpson-style reversal**, not noise.
  - **Consequence for the paper: the near-zero cross-sectional coefficient must not be reported as "experience is unpriced."** It is priced; the cross-section cannot see it. This is a concrete argument for the paper's within-gig/matched-model design over a hedonic one, and it is now demonstrated rather than asserted.
- **Corrected myself mid-build.** The script's original narrative asserted the cross-sectional slope would *exceed* the within-gig one (the usual selection story) and printed a nonsensical "−513% of the association is selection" when the data went the other way. Both the code and the docstring now state the reversal that was actually found. A label bug (`ln(1+ln_reviews)`), a mislabelled cluster unit in spec 3, and a hard-coded 58% share carried over from a row-level probe (41% at gig level) were also fixed.
- **Verified:** `py_compile` clean; runs end to end (exit 0). Category assignment mirrors `19-tpd-index.py` exactly and the panel is read through the same `gigfilter`/price-guard path as the published index, so the sample matches. The within-gig slope reproduces an independent earlier estimate (+0.133 here vs +0.103 in step 22) on a differently-constructed sample.
- **Status: exploratory finding; `code/25-hedonic-regression.py` added, `progress.md` and `plans/todo.md` updated. Nothing else touched.**

## 2026-08-05 — Precision published on the site: six of seven categories miss the ±5% standard, and the category ranking is retracted

- **User: "what is #1" → "yes".** Applied the 2026-08-05 sample-adequacy criterion to what the site actually publishes. **Site edits made, NOT committed.** Files: `docs/ipi.js`, `docs/index.html`, `docs/faq.html`, `plans/todo.md`, `progress.md`, plus a rebuilt `scratchpad/render_check.js`.
- **The scope of the problem was wrong on the record, and the correction is the finding. SIX of seven categories fail, not two.** On 1.96×se_ln at 2026Q1: **translation ±29.2%, coding ±17.1%, audio ±13.9%, video ±11.9%, writing ±8.3%, marketing ±7.7%**; only **design (±4.8%)** clears ±5%. The 2026-08-05 entry named only audio and translation — **coding, at ±17.1%, is worse than audio** and was not flagged. Read directly off `docs/data.json` and confirmed against `data/pilot/recent-category-indices-geks-se.csv`.
- **That killed the planned remedy.** "Suppress or grey the failing cells" was written when it meant two categories; at six of seven it would leave a one-category site. Chose instead **bands everywhere + no hard ranking claims**, with ±5% restated as the standard the pilot does not meet.
- **The live exposure was the ranking, not any single level.** The site sorts by Δ and the FAQ asserted an order ("design, writing, and coding sit at the bottom; marketing, translation, and audio sit at the top"). The top three — **audio 254.2 ±13.9%, translation 236.3 ±29.2%, marketing 232.2 ±7.7%** — have intervals that **overlap one another completely**, so which is highest is not determined by the data. Verified pairwise in the harness. **Design is the one genuine separation** (117–129 vs audio's 221–292).
- **New `±95%` column on the category table**, computed from `index_geks_se` at each category's terminal quarter, sortable, with the exact asymmetric CI on the change in the cell tooltip and an amber `.imprecise` marking for cells that miss the standard.
- **Confidence bands now drawn for every plotted line, not just the emphasised one.** Previously only the composite (or the lone selected category) carried a band; the other six were bare lines, which showed them as more certain than they are. Composite band opacity 0.13, category bands 0.07 when a composite is drawn and 0.11 otherwise.
- **The composite passes at ±3.7% — surfaced by the harness and now published.** Not a contradiction: it is review-weighted and design carries ~71% of the weight, so the basket inherits design's precision. The **+40.7%** headline is on firmer ground than any category line except design's. This was not previously stated anywhere.
- **FAQ Q3 rewritten.** The ordering paragraph now states plainly that the pilot cannot support the ordering and does not claim it, carries the full precision table (seven categories + composite), explains the overlap consequence, and adds the margin result — no detectable break in sales rate or dormancy, with ±23–66% bounds — as a second reason not to read the ordering as an AI signal. Also states the ~850–2,500 matched-gigs-per-category requirement to reach ±5%.
- **Verified:** rebuilt `scratchpad/render_check.js` (the earlier harness was gone) as a DOM shim that runs the real `render()`/`catRow()` against the real `data.json` — **49 checks, all pass**: header/row/footer column counts agree at 8, every site-computed half-width matches an independent recompute off the raw arrays, exactly six cells carry `.imprecise` and design does not, every ±figure and level quoted in `index.html`/`faq.html` matches the data, the three-way overlap claim holds and design's non-overlap holds, and `render()` succeeds with one category, all seven, and on both bases. Separately: `node --check` clean on both JS files; all three HTML files nesting-checked; all 23 FAQ in-page anchors resolve; every `getElementById` in `ipi.js` resolves to an id in `index.html`; composite level 140.7 confirmed against `composite_geks_real`.
- **Caught mid-task:** the new FAQ table was first written without the `ftable` class the page's other tables use, so it would have rendered unstyled.
- **Status: edits made, NOT committed.** `docs/data.json` was not modified — `index_geks_se` was already present and sufficient, so no pipeline re-run was needed.

## 2026-08-05 — Non-price margins opened up: reviews give a real demand series, but exit and entry are unmeasurable in this crawl and every margin test returns a null with a bound

- **User: "how can i address which categories are most impacted by ai" → "yes" (build the margin diagnostic).** Answered that price is the wrong margin to look at first, then built `code/24-margin-diagnostics.py` to measure the quantity margins. **Measurement only; nothing in `data/`, `docs/` or `drafts/` was modified.** Output: `scratchpad/margin-diagnostics.out`.
- **First: the existing elasticity table should stop being treated as the impact ranking.** `data/pilot/panel-elasticity.csv` runs off step 12's chained series (TD1) — its `total_change_pct` reads marketing **4260%**, design 408% — has no control group, and returns **design as the most AI-elastic category (+1.14)** when design is the flattest category in real terms, and **audio negative (−0.49)** when audio is the top real riser. Three independent reasons not to quote it.
- **`review_count` is a usable sales proxy, and this is the enabling finding.** Post-`gigfilter` coverage is **88.7% historical / 90.7% recent** (the earlier ~11%/32% blank rates were almost entirely the `hire/*` and `agencies/*` rows), and the series is effectively monotone — only **0.4% / 0.1%** of within-gig transitions decrease. Reviews are cumulative sales, so the **accrual rate is a demand series**. Note the asymmetry with step 22: reviews are a *bad control* for price precisely because they respond to demand, which is exactly what makes them a *good outcome* here.
- **TRUE EXIT IS NOT MEASURABLE, and this is the hardest constraint.** Both crawls are Wayback CDX-derived, so a gig's absence in quarter t means "not archived", not "taken down". Worse, `code/13-recent-manifest.py:36-37` requires ≥1 snapshot in 2025Q3–2026Q2, so the **recent panel conditions on survival by construction** — 36.5% of its gigs are last seen in the final quarter, against 0.4% in the historical panel. No exit hazard can be estimated from either crawl.
- **ENTRY IS ALSO NOT MEASURABLE — the profile is crawl-window geometry.** Normalising new-gig counts by observed gigs does not fix it, because the numerator is truncated at both window edges. **1,747 of 2,930 recent-panel gigs are "first captured" in 2024Q3 — exactly `WINDOW_START` — and 5 in 2026Q1.** Entry runs ~100% → ~0% by construction, and the apparent historical decline (31% in 2019 → 8% in 2024) is the same artefact. Reported as a closed question, not a finding.
- **M1 demand rate — null in every category, and the bound is the deliverable.** Within-gig interrupted time series on reviews accrued per quarter, gig FE + linear trend + post-2022Q4, gig-clustered SEs, 4,874 transitions / 887 gigs. **Nothing significant:** translation −18%, design −11%, writing −3%, coding −2%, marketing +12%, audio +13%, video +24% of pre-period rate, all |t| < 1.1. **Minimum detectable break: ±23% (coding), ±27% (audio, writing), ±28% (design), ±42% (marketing), ±47% (video), ±66% (translation).** So: no category's sales rate broke by more than roughly a quarter to two-thirds — a real bound, not evidence of no effect.
- **The age/period/cohort trap is why there are two specs, and the second one is contaminated.** Given gig FE, age = period − cohort is perfectly collinear with calendar time, so the *level path* cannot be read as demand; only the **level break relative to the fitted trend** is identified. The age-bucket-FE alternative (spec B) returns large positives (audio +20.9 t=3.34, design +19.8 t=2.54, marketing +19.4 t=2.25) and **disagrees in sign with spec A in four of seven categories** — it drops the gig effect, so it compares different gigs pre and post, and in a Wayback panel the later gigs are the ones the archive kept re-sampling. Spec B is survivor composition, not demand.
- **M2 dormancy — the raw ranking looked like the AI story and did not survive adjustment.** Share of gig-quarters with zero review accrual. **Raw** pre→post: writing **+6.1pp**, marketing +5.6, audio +5.0, translation +5.0, coding −0.8, video −1.7, design −2.3 — an ordering that lines up suspiciously well with text-deliverable exposure. **Trend- and composition-adjusted** (same ITS spec): marketing +7.9 (t 1.35), audio +7.8 (t 1.68), writing +4.5 (t 1.27), coding +1.9, video +1.7, design +0.8, **translation flips to −0.6** (t −0.83, 16 gigs). Marketing/audio/writing stay on top, but **nothing reaches significance and the raw ranking is not stable** — dormancy rises with gig age, and the post window is simply later.
- **M4 pooled exposure contrast — pooling does not buy back the power either.** High-exposure (writing, translation, marketing — text deliverable, hypothesis stated before looking) vs low (audio, coding, design, video), gig FE + quarter FE + high×post. **Demand rate +28.7% [−2.9%, +60.4%], t = 1.78 — and WRONG-SIGNED**: high-exposure categories accrued *more* reviews after ChatGPT. **Dormancy +32.6% [−17.2%, +82.4%], t = 1.28.** Both groups are treated, so this is a contrast, not identification.
- **The two M4 signs are jointly consistent with polarisation** — the mean sells more while the bottom tail goes dormant — but at t = 1.78 and 1.28 that is a hypothesis to test at scale, not a result.
- **Verdict: the pilot sample cannot rank categories by AI impact on ANY margin.** Price is confounded and imprecise (audio ±13.9%, translation ±29.2% at 2026Q1); demand and dormancy are null with bounds of ±23–66%; entry and exit are unmeasurable by crawl design. This converges with the 2026-08-03 DiD probe (95% CI −15% to +88%) and the 2026-08-05 precision curve from the same direction: **the binding constraint is sample size and crawl design, not estimator choice.**
- **Two design requirements for the full-scale collection fall out of this**, and both are cheap to specify now and impossible to retrofit later: (1) **sample gig URLs on a fixed schedule regardless of whether they still resolve**, recording 404s — that alone makes exit measurable; (2) **do not select the manifest on survival into a trailing window**, which is what makes entry and exit uninterpretable today.
- **Verified:** script compiles (`py_compile`) and runs end to end (exit 0, 224 lines). Category assignment mirrors `19-tpd-index.py` exactly (item map + `classify_gig` historical, manifest recent) so categories match the published index; panel built through the same `gigfilter`/price-guard path. Review coverage and monotonicity measured directly off both price files. The entry-truncation diagnosis was confirmed against first-capture counts, not asserted. Reported regression `n` is the post-absorption estimation count (singleton gigs contribute nothing after demeaning and are dropped), and SEs are CR1 clustered on gig.
- **Corrected two things mid-build.** The first M3 pass presented the entry decline as a result before the truncation check showed it was window geometry; and the first M2 pass ranked categories on the raw pre/post difference, which reverses sign for three of seven once trend and composition are held fixed.
- **Status: exploratory finding. `code/24-margin-diagnostics.py` added; `progress.md` and `plans/todo.md` updated. Nothing else touched.**

## 2026-08-05 — Sample adequacy has a benchmark now: ±5% at 95%. The recent panel clears it in 5 of 7; the historical panel fails at the pair level everywhere

- **User: "how do i know that my sampling size is enough? what benchmark do i use?"** Answered with a measured criterion rather than a rule of thumb. **Measurement only; nothing in `code/`, `data/`, `docs/` or `drafts/` was modified.** Script: `scratchpad/precision-curve.py` (kept in the session scratchpad), panel densities from a direct sweep of `19-tpd-index.py`'s two builders, imported unmodified.
- **The criterion: MDE, not n.** For a matched-model index "enough" is precision relative to the effect being claimed. Proposed published rule — **±5% at 95% on the category index at the terminal quarter**; suppress or band any category-quarter that misses it.
- **Precision-vs-n curve (recent panel, terminal 2026Q1, sd of ln(index) over 60 independent subsamples).** design ±29.1% at n=25 → ±18.5% at 100 → ±10.4% at 200 → ±7.0% at 400 → ±4.6% at 800. coding ±56.5% / ±33.5% / ±18.2% / ±6.9%. writing ±26.3% / ±11.4% / ±7.4%. video ±29.6% / ±14.2% / ±5.4%. Clean 1/√n, log-scale constant **0.75–1.3**, so **±5% needs ~850–2,500 matched gigs per category**, ±10% needs ~215–650. Extrapolated full-n values land in the same range as the published bootstrap SEs — an independent check on both. (The n=full row of the curve is degenerate at 0.0% — sampling all gigs without replacement has no variation.)
- **The counting unit was wrong, and this is the finding.** Adequacy is set by **matched gigs per bilateral**, not by panel gigs, and the two diverge hard. Historical: design **330 gigs but median 1 matched per pair, 721/1081 pairs (67%) below `MIN_MATCH=3`**; writing 229 gigs, median **0**, 1090/1378 (79%) unusable; translation 26 gigs, median 0, 85% unusable. Recent: design 1466 gigs, median **208**, **0/21** pairs thin; coding 58; video 32; writing 48; marketing 35 — but **audio median 5 (5/21 thin)** and **translation median 3 (7/21 thin)**.
- **This is the mechanism behind the 2026-08-03 base-quarter instability.** A segment whose median quarter pair shares one gig or zero cannot pin a level; the 75.5 / 96.0 / 75.7 swing across base choices is that sparsity, not a base-choice pathology.
- **Live exposure identified: audio and translation are being reported as if they pass, and they do not.** Published bootstrap SEs at 2026Q1 give **audio ±13.9%** and **translation ±29.2%** against the ±5% rule — and audio is currently the site's headline "top real riser." Fixable by reporting a band, not by collecting more data.
- **External benchmark deliberately not CPI.** BLS runs ~94k quotes/month at ~0.1pp median SE on 12-month change; we are two orders off and the comparison only damages the paper. Borrow the *rules* instead — the ILO CPI Manual minimum-relatives rule and BLS cell suppression. **`MIN_MATCH = 3` is far below either** (3 matched gigs ≈ ±50% on a Jevons link). Reviewer's real reference class is online-price work (Cavallo & Rigobon BPP; Cavallo 2017), which reports coverage and matched-item counts.
- **Verified:** curve computed by importing `21-geks-index.py`'s `geks_index` unmodified with `n_boot=0` and varying only the gig set; densities counted directly off both builders' panels; 1/√n fit checked per category; degenerate full-n row diagnosed rather than reported as precision.
- **Status: exploratory finding. `progress.md` and `plans/todo.md` updated, nothing else touched.**

## 2026-08-03 — Gig-level exposure DiD: identification works, power does not. Feasible design, not a feasible conclusion at pilot scale

- **User: "what is DiD" → "would I be able to use it for this project?" → probe feasibility first.** Answered that the *category-level* DiD in `plans/todo.md` Backlog is dead (quantified below), proposed a gig-level continuous-exposure variant instead, and ran a feasibility probe rather than writing a plan for it. **Measurement only; nothing in `code/`, `data/`, `docs/` or `drafts/` was modified.** Scripts: `scratchpad/did-feasibility.py` (Q1–Q4), `scratchpad/did-feasibility2.py` (Q5–Q9), output `scratchpad/did-feasibility.out`.
- **The category-level design is dead, with numbers.** The only low-exposure candidate, `data_entry`, carries **46 gigs / 23 quarters** in `panel-elasticity.csv` and is **explicitly excluded from the recent crawl** as too thin (`code/13-recent-manifest.py:38`, `SKIP_CATEGORIES`), so the post-2022Q4 window — where the effect would be — has almost no control observations. On the merits it is a bad control anyway: its keywords are transcription, PDF conversion, typing (`code/12-panel-ipi.py:68`), squarely inside what LLMs and ASR automated first. Treated-vs-treated.
- **The gig-level variant: exposure varies within category, so cat×quarter FE can absorb everything platform- and category-wide.** Gigs scored on one question — as of 2023, can a general-purpose model produce the *deliverable* end to end (text/code/image/synthetic speech = high) versus work needing platform credentials, a physical object, a real counterparty, a live human, or accountability for a running system (low). Spec: within-gig first differences, per-quarter normalised, `Δlnp = γ_{c,q} + β₀·score + β₁·score×post + ε`, gig-clustered SEs, panel read through `19-tpd-index.py`'s builders imported unmodified.
- **Q1 — scoreable, but two categories carry no contrast.** 55% of historical transitions score (68% of design gigs, 35% of video). **Marketing is 46 of 50 scored gigs low** (SEO/backlinks/lead-gen) and **translation 18 of 26 high** — sd(score) 0.387 and 0.885 respectively, but one-sided. Those two categories contribute nothing to β.
- **Q2 — the identifying cells are sparse.** Only **55 of 258** historical cat-quarter cells (21%) hold ≥3 high *and* ≥3 low transitions. Marketing and translation have **zero**; audio and video have 3 each. Identification is coding (18), design (22), writing (9). The **recent** panel is far denser — 25 of 40 cells usable (62%) — but it is post-only and cannot host a DiD.
- **Q3/Q6 — PARALLEL TRENDS PASS. This is the finding.** Pre-period placebo (2018Q3–2022Q4, 1,865 transitions, 469 gigs): **β(score) = −0.0082, se 0.0093, t = −0.88**. Event study by year (base 2021) has every pre-year insignificant: **2019 +0.017 (t 0.53), 2020 −0.042 (t −1.54), 2022 +0.003 (t 0.28)**. Exposure did *not* predict differential price trends before ChatGPT — a genuine contrast with the category-level design, where pre-trends ran from audio −38%/yr to video +13%/yr and parallel trends failed outright.
- **Q4/Q7/Q8 — the DiD estimate is null and wrong-signed, and robust to being so.** Main: **β₁ = +0.0147, se 0.0126, t = 1.17** (more exposed → prices rose *faster*, insignificantly). Binary high-vs-low on the five categories holding both: **+0.0310, se 0.0264, t = 1.17**. Lean lexicon with nine generic operational verbs (`manage`, `optimiz`, `maintain`, `setup`, …) dropped: **+0.0115, se 0.0129**. Leave-one-category-out is stable (+0.006 to +0.020); **no single category drives it** — dropping design, which supplies 1,147 of 2,785 transitions, leaves +0.0198.
  - Only translation alone is significant (**−0.1414, se 0.0681, t = −2.08**), on **100 transitions / 21 gigs**, and its sign contradicts translation being the site's top real riser. Noise.
- **Q9 — the null is a precision problem, not evidence of no effect.** 95% CI on β₁ is **[−0.0100, +0.0393]** per quarter per unit of score. Over the eight quarters 2023Q1–2024Q4 for the high-vs-low contrast that is **−14.8% to +87.6%**, point +26.5%. The band is wider than every effect the paper already reports (reputation treadmill +7.4%, composite real +40.7%). **It cannot distinguish "AI did nothing" from "AI did a lot."**
- **Verdict: build it at full scale, not at pilot scale.** The design is sound where the category-level one was not — the assumption it rests on is testable and it passes. What it lacks is n: 594 scored gigs in the historical panel. The **full-scale collection** item (48,643 qualifying sellers vs the 500-seller pilot) would raise density toward the recent crawl's 62% usable cells and shrink the SE roughly an order of magnitude, putting the MDE near ±5% — a genuinely powered test.
- **Two threats to record before anyone builds it.** (1) **The lexicon is hand-built and is the weakest link** — a reviewer will attack keywords we invented; the real version needs an external measure (GPTs-are-GPTs task exposure, O\*NET) mapped to gigs. (2) **Within-gig first differences condition on survival**, the same problem as Test C — if highly exposed gigs *exit* rather than cut price, the DiD sees nothing by construction, and the observed null is exactly what that would produce. The entry-price companion series is the check.
- **Verified:** both scripts run end to end (exit 0). Panel built by importing `19-tpd-index.py` unmodified, so the gig set is the published one. Absorbed-FE OLS checked against the singleton-cell drop (cells of size 1 contribute nothing after demeaning and are removed so cluster counts and dof are honest); the part-1 event study returned NOT ESTIMABLE and the cause was diagnosed rather than worked around — the historical crawl trickles four captures into 2026 with zero within-cell variance, so `x2026` is a zero column; part 2 restricts to 2019–2024.
- **Status: exploratory finding. `progress.md` and `plans/todo.md` updated, nothing else touched.**

## 2026-08-03 — 2016–2020 probed and ruled out: the matched chain is severed in 2017, and the answer is whatever base you pick

- **User: "what does the historical trend look like between 2016 and 2020"** — probed it rather than answered from the published series, which starts at 2020Q1. **The window cannot be measured with usable precision**, and the fragment of signal that exists points **flat-to-down**, not up. Measurement only; nothing in `code/`, `data/`, `docs/` or `drafts/` was modified.
- **The crawl is nearly empty before 2018 and has a 15-month hole.** Distinct gigs per quarter: 2016Q1–Q4 **9 / 12 / 23 / 43**, 2017Q1 **18**, 2017Q3 **2** — against 408 in 2020Q1. **2017Q2, 2017Q4, 2018Q1 and 2018Q2 have zero captures.** This is a Wayback sampling artifact of the pilot manifest, not a gap in Fiverr.
- **The matched-model chain is severed, not merely thin.** `2017Q1 → 2017Q3` has **0** matched gigs and `2017Q3 → 2018Q3` has **0**. Only **65 of 1,066** panel gigs are observed both ≤2017Q3 and ≥2018Q3, so GEKS crosses the hole only on long-range direct bilaterals carrying 1–16 gigs each.
- **Consequence: the base quarter picks the answer.** Pooled GEKS (all categories, `21-geks-index.py` imported unmodified, only `window_start` varied), 2020Q1 level: base **2016Q4 → 75.7**, base **2018Q3 → 96.0**, base **2019Q1 → 75.5**, on se_ln **0.12–0.24** (±13–27% at one sd). Base **2016Q1 fails outright** — 1 of 36 quarters reachable from it. Same estimator, same panel, three incompatible answers.
- **Per category a 2016 base mostly does not exist.** With `window_start="2016Q1"`: **audio** resolves 1 of 29 quarters and **video** 1 of 29 (both unreachable); **marketing**'s base slips to 2018Q3 and **translation**'s to 2019Q4; **coding** returns 7 of 30 with holes. Only **design** (2016Q4=100 → 2020Q1 **88.2**, se_ln 0.245) and **writing** (2016Q4=100 → 2020Q1 **50.7**, se_ln 0.112) yield a series spanning the window at all.
- **Raw medians rise and the matched index falls — and the medians are the artifact.** Median posted basic price runs \$5 (2016Q1–Q3) → \$10 (2016Q4–2017Q1) → \$20 (2018Q3–2019Q2) → \$25 (2019Q3–Q4). That is mostly **the death of Fiverr's \$5-for-everything floor** (already established 2026-07-29), an entry-mix and platform-policy change. The matched-model index, which holds the gig fixed, moves the *other way* — exactly the divergence a composition story predicts.
- **Corroborates the existing pre-AI finding rather than adding to it.** Pooled base 2018Q3 → 2019Q4 = **94.1**, consistent with the 2026-07-29 diagnostics (no common upward pre-2020 trend; audio and writing falling). The takeaway is unchanged and now bounded: **2018Q3 is the earliest defensible base**, and `plans/todo.md`'s placebo item has been annotated to that effect so no one retries 2016.
- **Verified:** quarter counts and matched-pair counts read directly from `data/pilot/pilot-prices.csv` under the standard `0 < price <= 10000` guard; indices produced by importing `19-tpd-index.py` and `21-geks-index.py` unmodified and passing `window_start`, so only the window differs; real levels deflated with `data/pilot/cpi-quarterly.csv` (`cpi_sa`). Probe script: `scratchpad/hist-2016.py`.
- **Status: exploratory finding; `plans/todo.md` and `progress.md` updated, nothing else touched.**

## 2026-07-31 — Non-gig landing pages excluded; audited every category for the same class of defect; index re-run

- **User: "okay fix these errors and make sure there aren't other errors like these for the rest of the categories."** Both done. The fix is a single shared rule; the audit found **one additional family** beyond `hire/*` and confirmed nothing else of the kind exists.
- **Audit first, before touching anything.** Swept both price files with **two independent tests**: (a) leading URL path segment is a known Fiverr site section, (b) page title is not gig-shaped (no "I will", no "for $N"). The two agree **exactly** — `recent-prices.csv` has **3,846 junk rows = `hire` 3,806 + `agencies` 40** (the latter new: titles like *"Best Digital Marketing Agencies | Fiverr"*), and **no third family**. `pilot-prices.csv` (historical) has **zero**. Junk is not concentrated in audio: `hire` spans all seven categories (design 1,128, coding 815, writing 753, marketing 428, video 321, audio 248, translation 152), which is why the trend inverted everywhere and not just where the user spotted it.
- **Rejected the broader `dollar_fallback` rule, with evidence.** That was the open question from yesterday. `pilot-prices.csv` holds **2,531 `dollar_fallback` rows and 2,527 are genuine gigs** — real seller handles, *"<seller> : I will … for $5 on www.fiverr.com"* titles, clustered at \$5 because that was Fiverr's original floor. Dropping the method would have deleted valid pre-2017 history. **The defect is the URL family, not the parser branch**, so the filter keys on the path segment.
- **Two other candidate defects checked and cleared.** 1,103 historical rows carry `price_basic=0` (all `old_json`, 66 gigs) and one recent row reads \$20,000 — both already excluded by the pre-existing `price <= 0 or price > 10000` guard in every panel builder, so neither ever reached the index. Also verified the historical title-vs-extracted price mismatch (15.1%) is dominated by those zero-price rows, not by systematic misparsing.
- **New `code/gigfilter.py` is the single source of truth** (`is_gig`, `is_gig_id`, 27-entry `RESERVED`), applied on **all seven** price-reading paths: `12`, `13`, `14`, `16`, `18`, `19` (both builders), `22`. `18` had its **own duplicate copy** of the reserved set applied only to the gallery and not to the index — that copy is now an import, so the gallery and the index can no longer disagree about what a gig is. `13` (the crawl manifest builder) filters upstream and prints the excluded count, so these URLs are **never fetched again**.
- **Re-ran 12 → 14 → 19 → 21 → 23 → 18, all exit 0.** Recent panel **3,566 → 2,908 gigs**; historical unchanged at 1,066, and `panel-ipi.csv` / `panel-elasticity.csv` / `panel-category-indices*.csv` are **byte-identical** — independent confirmation that the historical segment was clean.
- **The user's original symptom is resolved:** audio 2024Q4→2025Q1 moves from **−42.6% to +3.2%**, consistent with the individual gig charts they were reading.
- **Headline impact.** Spliced composite 2020Q1→2026Q1: **nominal +44.7% → +78.4%**, **real +14.1% → +40.7%** against CPI-U +26.8%. General inflation is now **~48%** of the nominal rise, not ~68%. Recent segment (2024Q3=100 → 2026Q1) flips from falling to flat-or-rising in six of seven: audio 60.6→**104.9**, coding 78.5→**121.4**, writing 75.6→**108.5**, marketing 77.6→**109.9**, design 91.4→**106.4**, translation 120.8→**131.5**; video 83.3→**96.9** is the one still below 100.
- **Precision improved, which corroborates the fix.** Bootstrap SEs at 2026Q1 **narrowed in five of seven** categories — audio 0.155→0.071 (−54%), writing −51%, marketing −49%, design −35% — so the removed rows were injecting variance, not carrying signal. The chart's long-standing 0.1pp headline rounding gap also closed (chart and `data.json` now both read +78.4%).
- **Downstream updated:** `docs/data.json`; site copy in `index.html` (deflation bullet, "how to read it" example) and `faq.html` (Q3 magnitudes **and category ordering** — audio, not translation, is now the top real riser; Q9 deflation share; Q13 chain-drift comparison **+283.0%** chained vs **+78.4%** GEKS); a new FAQ subsection *"Pages that look like gigs but are not"* documenting the exclusion; draft **§3.2 Stage 5b** (new) and **§3.4** (gap-spanning shares 26/39% → 25/44%, bootstrap bands, TPD comparison 66.1%→89.6% with r 0.983→0.996, terminal-price test); `tests/findings.test.md` (R4 restated, **new R7**, **new U2/U3** recording the user's two instructions) and `tests/method.test.md` (R1–R3 restated).
- **Corrected myself mid-task:** I first rewrote the FAQ's extraction-method share table to combined-crawl figures, then found that table sits under the 22,632-page pilot pipeline and was **historical-only and already correct**. Reverted it and added a scope note instead.
- **Found but deliberately not fixed** (logged as new Active items): `drafts/sections/findings.md` still carries the pre-fix §4 narrative; `drafts/sections/faq.md` has drifted from the live FAQ since 2026-07-12 and is now marked OUT OF SYNC in its header; and §3.4's **"10.9% filled"** panel figure **cannot be reproduced** under any obvious definition — it is 14.9% now and was 15.0% *before* this change, so it is stale for an unrelated reason and needs its own restatement rather than a silent edit.
- **Verified:** `py_compile` clean on all eight touched scripts; unit checks on `gigfilter`; zero reserved-path gigs remain in either rebuilt panel; `node --check` clean on both JS files; all three HTML files nesting-checked; every FAQ in-page anchor resolves; the DOM-shim render harness passes **all 16 checks** (real view +40.7% matching `delta_geks_real.composite`, nominal +78.4%, design +23.2%, 7 table rows, 25-quarter picker).
- **Status: edits made, NOT committed.**

## 2026-07-30 — `hire/*` landing pages are not gigs: 25% of the recent crawl is corrupt, and it inverts the recent trend

- **User: "in 2024Q4 to 2025Q1 I see a drop in audio, but the individual gigs don't show a drop during that period, why?"** They were right, and the reason is a data-quality defect, not an index property. `data/pilot/recent-prices.csv` contains **3,806 of 15,150 rows (25.1%) with `seller='hire'`** — these are **Fiverr Pro category directory pages**, not gigs (title of one: *"12 Best freelance nft experts for hire in July 2024"*, body: *"Hire the best nft experts"*). Every one of them was parsed by `extraction_method=dollar_fallback`: the package-list parser found nothing and fell back to scraping a dollar figure off the page, which is a **budget-filter value**, not a price.
- **The tell is the price distribution.** Of the 3,806 `hire` rows, **2,436 carry `price_basic=500.0` and 330 carry `1000.0`** — the filter defaults. The audio drop the user spotted is exactly this: of the **12 matched gigs** in the 2024Q4→2025Q1 bilateral, **10 are `hire/*` pages** and they move `1000 → 500` (two worse: `female-voice-over` 1000→68, `music-composition` 1000→48). **The 2 genuine gigs in the matched set (`aioriar` ×2) both moved exactly 0.0%.** So the −55.4% direct matched comparison is Fiverr redesigning a budget widget between quarters, and the user's reading of the individual gig charts was correct — real gigs did not drop.
- **Scope: recent segment only.** `build_panel_recent()` carries **652 of 3,566 panel gigs (18%)** as `hire/*`; `build_panel_historical()` carries **zero**. The historical segment (2020Q1–2024Q3) is clean. But the site splices recent onto historical, so the published full-window numbers are affected.
- **Removing them inverts the recent trend in every category.** Recent GEKS 2024Q3=100 → 2026Q1, as-built vs `hire`-stripped: audio **60.6 → 104.9**, coding **78.5 → 121.0**, design **91.4 → 106.2**, marketing **77.6 → 109.8**, video **83.3 → 96.9**, writing **75.6 → 108.5**, translation **120.8 → 131.5**. The as-built series says prices have been falling since 2024Q3 in six of seven categories; stripped, **six of seven are flat or rising**.
- **Headline impact — the composite nearly doubles its move.** Spliced composite 2020Q1→2026Q1 nominal: **+44.7% as-built → +78.0% stripped**. Per category at 2026Q1: audio 186.3→**322.3**, coding 161.7→**249.2**, design 134.1→**155.8**, marketing 207.7→**293.9**, video 228.5→**265.6**, writing 140.6→**201.8**, translation 275.1→**299.5**.
- **This retracts a claim made earlier in the same session.** In arguing against a causal AI reading I cited "prices falling in real terms since 2024Q3 across nearly every category" (audio −11.4%/yr etc., from the 2026-07-30 real-terms run) as evidence against the AI story. **That decline is an artifact of the `hire/*` rows.** The no-control-group objection, the reputation treadmill, and the survivorship gap are untouched and still stand on their own; the post-2024 decline does not.
- **Not fixed, deliberately.** The correct filter is a one-line exclusion in the panel builders, but it changes the project's headline number and every downstream artifact (site, `data.json`, elasticity tables, draft §3/§4), so it is a methods change to be made deliberately rather than silently. Logged as the top Active item in `plans/todo.md`. Open sub-questions: whether to drop `seller='hire'` specifically or all `dollar_fallback` rows (the latter may catch other landing-page families), and whether the crawl manifest should have excluded these URLs upstream.
- **Verified:** counts from `data/pilot/recent-prices.csv` directly; the two index variants recomputed by importing `19-tpd-index.py` / `21-geks-index.py` unmodified and filtering the panel dict, so only the gig set differs. One landing-page HTML read end to end to confirm it is a directory, not a gig. **Nothing in `code/`, `data/`, `docs/`, or `drafts/` was modified.**

## 2026-07-30 — FAQ audit + everything since 2026-07-27 committed and pushed live

- **User: "publish these changes, also update the faq."** Committed and pushed the real-terms work to `mockup`, which is what deploys https://aismithlab.com/IntelligencePriceIndex/. Before publishing, audited the **whole** FAQ rather than only the Q9 rewrite already in the tree — and found four claims that had gone stale when the chained series was retired on 2026-07-27 and the real series became the default today.
- **Q3 was quoting the retired chained series.** It read "every category has risen, several to **three or four times** their 2020 level" — those are `delta12` magnitudes (marketing +478%, audio +370%), not anything the site plots. The displayed real range is **+5.8% (design) to +117% (translation)**, composite +14.1%. Worse, the ordering claim was **inverted**: it said "translation, writing, and coding occupy the bottom … audio, video, and marketing the top", but on the real GEKS series translation is the **highest** category of the seven. Rewrote with the true ordering (bottom: design, writing, coding; top: video, marketing, translation) and added a paragraph stating plainly that translation topping the table is *not* what an exposure story predicts, alongside the reason to discount it — thinnest series, widest band, quarters missing.
- **Q8 still described the chained index as the published one.** Steps 1–4 built the chain and Step 5 was framed as a correction shown on "**the second chart on the home page**" — there has been one chart since 2026-07-27. Reframed the intro so GEKS-Jevons + CPI-U deflation is stated up front as what's plotted, with steps 1–4 kept as the clearest way to explain a matched-model index and explicitly labelled **not plotted anywhere on this site**.
- **Added Step 6, deflation — a real documentation gap.** Real is the *default view* and the calculation section did not document it at all. New step gives `I_real = I × CPI₀/CPI_t`, names `CPIAUCSL`, explains why the seasonally adjusted series is primary (QoQ reading; NSA checked, max divergence 0.36%), and why the **bootstrap bands are identical on both bases** — the deflator carries no sampling error.
- **Q13 limitations rewritten around what has actually been measured.** The old "possible upward drift" bullet described the chained series as though it were on screen; replaced with the corrected-but-still-an-estimate framing (+44.7% GEKS vs +217.7% chained). Added two bullets from the 2026-07-29 diagnostics: the **reputation treadmill** (doubling reviews ≈ +7% price, ~40% of within-gig growth, and why reviews are a bad control since they are cumulative sales) and **survivorship** (entrants post flat prices 2019–2025 while the matched index climbs). Strengthened the causation bullet to the descriptive-first position: AI is one candidate among measured rivals, and no comparison group exists within the sample because every category is exposed.
- **Q14** now names the real three-script build (21 → 23 → 18) instead of only step 18, and adds the `PriceIndexCalc` exact-reproduction check.
- **Found but did not fix:** `docs/GUIDE.md` and `docs/README.md` still document the **pre-quarterly** contract (`DATA.index`, `delta12`, "−2.1% headline"). Q14 links to them, so rather than leave readers pointed at wrong docs I added a one-line warning there naming `data.json` as authoritative, and logged the refresh in `plans/todo.md`. Deliberately out of scope for this commit.
- **Verified:** all three HTML files parse (nesting-checked, not just well-formed); every in-page `href="#…"` in the FAQ resolves to a real `id`; `node --check` clean on both JS files; the DOM-shim render harness passes **all 16 checks** — real view 9 paths / headline +14.1% matching `delta_geks_real.composite`, nominal view 10 paths with the CPI-U line / +44.6%, single-category design +5.8%, 7 table rows, 25-option quarter picker. Every figure newly written into the FAQ was checked against `docs/data.json` or the 2026-07-29 diagnostics run.
- **Status: COMMITTED + PUSHED** on `mockup` (live). Two commits: the real-terms site work, then the FAQ audit.

## 2026-07-30 — Site published in real terms: CPI-U-deflated by default, nominal on a toggle

- **User: "update the website now."** The real series computed earlier today existed only as CSVs; nothing under `docs/` read them. The site now **defaults to the real (CPI-U-deflated) index**, with a **Real / Nominal** segmented toggle on the hero chart. Defaulting to real is a deliberate editorial call: the index is quoted in dollars, the dollar lost ~27% of its value over the window, and the nominal series answers "how many dollars" while the real one answers "how much intelligence work actually costs" — the question the project exists to ask.
- **Data layer (`code/18-build-site-data-long.py`).** Reads the two `*-geks-real.csv` files through the **same** `chain_category` → `aligned` → `composite_series` path as the nominal series, so on the chart the two differ *only* by the deflator — no separate splice logic to drift out of sync. New `data.json` keys: `index_geks_real`, `composite_geks_real`, `delta_geks_real`, plus `cpi` (CPI-U rebased to 2020Q1=100) and `cpi_imputed` (per-quarter flag). **No `*_real_se` block** — the deflator carries no sampling error, so `index_geks_se` applies to both bases; this is documented in the emitting code so it doesn't read as an omission.
- **Cross-check against the independent path:** the site build reports composite **nominal +44.7% / real +14.1% / CPI-U +26.8%**, and `code/23-real-index.py` computed **114.1** by a different composite route (step 19's `spliced_composite`). Agreement to 0.1pp.
- **The real view changes the story per category.** Full-window Δ, nominal → real: design **+34.1% → +5.8%**, writing **+40.6% → +10.9%**, coding **+61.7% → +27.6%**, audio **+86.3% → +47.0%**, marketing **+107.7% → +63.9%**, video **+128.5% → +80.3%**, translation **+175.1% → +117.0%**. **Design — the heaviest category at ~71% of review weight — is essentially flat in real terms over six years.**
- **Chart behaviour.** All reads routed through `idxSrc()`/`deltaSrc()` accessors (chart lines, confidence band, Δ column, row sparklines, quarter inspector, headline delta) rather than scattered `DATA.index_geks` references, so the two bases can never partially mix. In the **nominal** view CPI-U is drawn as a dashed grey reference line so the inflation gap is visible directly; in the real view it is omitted, since it is flat at 100 by construction. The y-axis title and tooltip both name the active basis, and the tooltip flags quarters whose deflator contains an interpolated month. The toggle **hides itself** if `data.json` predates the real block.
- **Copy updated so nothing contradicts the new default:** new hero bullet explaining deflation with the two-thirds figure; intro boxes ("How to read it" example changed from 142 pts to 114 pts, since the old number was the nominal composite); source line naming `CPIAUCSL` and the October 2025 gap; **FAQ Q9 rewritten** from "carries no inflation adjustment at present / a real version is planned" to the real-by-default explanation with the caveat that deflation removes *general* inflation and is **not** a control for the reputation treadmill, seller mix, or survivorship; Q3 and Q4 de-stale'd. Gallery page switched to the real series to match, with its footer noting that **featured gig package prices remain nominal posted dollars** (they are actual amounts, not index levels).
- **Verified:** `node --check` clean on both JS files; every `getElementById` in `ipi.js` resolves to an id in `index.html`; all three HTML files parse. Full build path rendered under a DOM shim against the real `data.json` — **real view: 9 paths** (7 categories + composite + band), headline **+14.1%** matching `delta_geks_real.composite`; **nominal view: 10 paths** (the CPI-U line appears), headline +44.6%; single-category design view renders and reads **+5.8%** = `delta_geks_real.design`; 7 table rows + composite footer; quarter picker 25 options across 7 year groups. Build re-run is idempotent. Harness: `scratchpad/render_check.js`.
  - Three initial harness failures were **wrong expectations, not site defects** (verified individually): the picker nests options inside year optgroups; the source line is set in the fetch bootstrap the shim strips; and the chart's +44.6% vs `data.json`'s +44.7% is **pre-existing** rounding — the chart recomputes the composite client-side from the 2dp-rounded index arrays while `full_delta` uses unrounded values. Same 0.1pp gap existed before this change (see 2026-07-27 entry). Not introduced here, not fixed here.
- **Status: edits made, NOT yet committed.** Files: `code/18-build-site-data-long.py`, `docs/ipi.js`, `docs/gallery.js`, `docs/index.html`, `docs/gallery.html`, `docs/faq.html`, `docs/data.json`, `docs/freelancers.json`, `plans/todo.md`, `progress.md`. The paper (`drafts/`) is still entirely nominal — that is the next item.

## 2026-07-30 — Real terms: the IPI deflated by CPI-U, and a framing decision

- **User decision: the paper is framed descriptive-first.** The 2026-07-29 diagnostics showed AI is not identified in the current design (no control group — every category is treated). Rather than build a DiD to chase identification, the paper now leads with the **price index itself** as the contribution and reports AI as one candidate explanation among several *measured* rivals (reputation treadmill, general inflation, platform composition, survivorship). The DiD moves to Backlog with the reason recorded, not silently dropped. This converts R1/R3/R5 from blocking identification failures into the paper's rival-explanations section.
- **New `code/23-real-index.py` — deflates GEKS-Jevons to real terms.** `Real_c,t = Nominal_c,t · (CPI_base / CPI_t)`. Deflator is CPI-U, US city average, all items, fetched from FRED and cached to `data/cpi-u.csv` so reruns are offline and reproducible. Both **CPIAUCSL (SA, primary)** and **CPIAUCNS (NSA, robustness)** are pulled; SA is primary because the index is read quarter over quarter and SA removes the seasonal wave from QoQ real changes. **Max SA-vs-NSA divergence is 0.36% (2021Q4)** — printed on every run rather than assumed negligible.
- **Headline result — general inflation is about two-thirds of the composite rise.** Spliced composite 2020Q1→2026Q1: **nominal 144.6 (+44.6%) → real 114.1 (+14.1%)**, against CPI-U **+26.8%** over the same window. So **~68% of the nominal rise is the dollar, not the service** — but the IPI still outpaces CPI-U, by **+14.1%** rather than +44.6%. The direction of the finding survives deflation; the magnitude does not.
- **Per category, historical segment at 2024Q3 (nominal → real, annualised real):** audio 307.4→**253.2** (9.3%/yr), video 274.2→**225.9** (8.1%), marketing 267.7→**220.6** (7.8%), translation 227.8→**187.7** (6.2%), coding 206.0→**169.7** (5.2%), writing 186.0→**153.2** (4.1%), design 146.7→**120.9** (1.8%). CPI-U over that window: +21.4%. **Design in real terms is essentially flat** — +1.8%/yr over four and a half years.
- **Recent segment 2024Q3→2026Q1 was already falling and falls harder in real terms:** audio −11.4%/yr, writing −6.9%, marketing −6.4%, coding −6.1%, video −4.9%, design −2.9%; only translation is positive (+3.3%/yr).
- **Found and handled a real hole in the deflator: there is no October 2025 CPI-U** (BLS published none; FRED carries no observation). Dropping the quarter would have blanked 2025Q4 out of the real index even though the gig price data for that quarter is fine. CPI-U is smooth at monthly frequency, so the script **linearly interpolates isolated interior missing months** from their neighbours, flags the affected quarter (`imputed_month=1` in `cpi-quarterly.csv`) and prints the warning on every run. Runs of 2+ consecutive missing months are left as genuine gaps. This is an imputation and is labelled as one.
- **Standard errors deliberately not recomputed.** The deflator is a per-quarter constant carrying no sampling error, so on the log scale the real index is the nominal log index shifted by a zero-variance constant — the existing bootstrap SEs in `*-geks-se.csv` apply unchanged to the real series.
- **Scope note:** deflation answers R4 ("it's just inflation") and *nothing else*. It does not touch the reputation treadmill (Test B), matched-model survivorship (Test C), or platform composition. Those remain separate open corrections.
- **Verified:** script runs end to end from a cold fetch and from cache (exit 0); real CSVs carry 100.00 at their base quarters; `144.6 / 1.268 = 114.0` reproduces the composite by hand; 2025Q4 present and flagged. Corrected one mislabel mid-build — the inflation share is computed against the *rise* (68%), not the level (21%).
- **Status: computed and written; NOT yet in the site or the paper.** Files: `code/23-real-index.py`, `data/cpi-u.csv`, `data/pilot/cpi-quarterly.csv`, `data/pilot/panel-category-indices-geks-real.csv`, `data/pilot/recent-category-indices-geks-real.csv`, `plans/todo.md`, `tests/findings.test.md`, `progress.md`. Nothing under `docs/` or `drafts/` was modified.

## 2026-07-29 — Confounder diagnostics: AI is not currently identified, and the reputation treadmill is first-order

- **User: "gig workers' labor becomes expensive over time, which is why they increase price — not only because of inflation. Is there any way to capture this? Look at data earlier than 2020? The data doesn't show AI is the only cause."** Correct on both counts. Built `code/22-confounder-diagnostics.py` (4 tests) to measure the rival explanations rather than argue about them. Full output: `scratchpad/confounder-diagnostics.out`.
- **Test B — the reputation treadmill is real and large.** `review_count` is populated **88–99% of rows from 2018 on** (it was already in `pilot-prices.csv`/`recent-prices.csv`, unused). Within-gig first differences, 9,543 transitions across 3,957 gigs, pooled with **quarter fixed effects** (so any common shock — CPI, platform-wide repricing, Fiverr fee changes — is absorbed): **β(Δln reviews) = +0.1026, se 0.0101, t = 10.19.** A doubling of a gig's review count raises its price **+7.4%**. Review counts grow **+0.20 log pts per transition** against mean Δln price of **+0.050** ⇒ reputation accounts for roughly **41% of within-gig price growth**. Per category: marketing β=0.270 (t=7.2), writing 0.165 (t=7.0), coding 0.126 (t=4.5), video 0.108 (t=3.2), design 0.081 (t=5.8); audio −0.076 and translation −0.081 both n.s. (n=469/119).
- **Test B2 — adjusting for it moves the headline a lot.** GEKS rebuilt on `ln p − β·ln(1+reviews)`, same 2020Q1 window (2024Q3 raw → adjusted): design **146.8 → 121.0**, writing **189.5 → 140.9**, coding **203.2 → 171.5**, marketing **267.4 → 212.0**, video **266.1 → 223.7**, translation **227.8 → 170.7**, audio **310.1 → 259.1**. Writing's six-year move drops from +90% to +41%. **This is a first-order correction, not a footnote.**
  - **But β is a bad control.** Reviews are cumulative *sales*. If AI suppresses demand, review growth slows, and adjusting for reviews absorbs part of the effect we want to measure. The adjusted series is a **lower bound**, the raw series an upper bound; report the pair as a range, do not swap the headline.
- **Test A/A2 — a pre-AI placebo is feasible but only from ~2019Q1, and it does NOT show a common upward trend.** Panel construction already runs back to 2011; only the GEKS *window* was pinned at 2020Q1. Pushing it to 2018Q1 identifies **26–28 quarters at pair density 0.70–0.88** for six categories (translation 0.42, base slips to 2019Q4). Base quarter resolves to **2018Q3** (2018Q1/Q2 fail the ≥3-gig bar). Pre-AI path to 2019Q4, annualised: **audio −38.4%, writing −19.8%, coding +3.1%, marketing +6.5%, design +10.2%, video +13.0%** — versus 2020Q1–2022Q3 of +8.5% to +31.5% *in every category*. So the post-2020 climb is not the continuation of a pre-existing secular trend, and two categories were falling before AI.
  - **The pre-period is thin, though.** Matched gigs per adjacent quarter pair in 2018Q3–2019Q2: design 9–24, coding 6–12, writing 5–10, video 6–9, marketing 3–5, audio 2–4, translation **0**. Only design is comfortably usable before 2019Q3; the quarter-to-quarter bounce (video 226.7 → 124.3 → 106.1 across 2019Q1–Q3) is sampling noise, not price. **Usable as a qualitative placebo, not as a precise counterfactual.**
- **Test C — new-gig entry prices are flat while the incumbent index climbs.** First capture of every gig, restricted to genuine entrants (**≤10 reviews at first sight**), median entry price by year: design 10 / 10 / 25 / 30 / · / 10 / 15 (2019→2025), writing 12 / 10 / 10 / 12 / 18 / 20 / 10, video 30 / 20 / 25 / 38 / · / 15 / 20, marketing · / 30 / 15 / · / · / 30 / 25. **Essentially flat 2019–2025** while the matched-model index says design +47%, writing +86%, video +166%, marketing +167% over the same span. Coding is the exception (15 → 20 → 85 in 2024). The index conditions on survival and follows ageing incumbents; entrants price where they always did. This is the **matched-model survivorship problem**, and it is the same phenomenon Test B measures, seen from outside.
  - **Crawl-frame caveat, do not compare across sources:** HIST 2024 entry median **$50 (n=102)** vs RECENT 2024 **$30 (n=2389)** — different sampling frames. Within HIST alone, all-entrant medians run **$5 (2011–2014) → $10 (2019) → $15 (2020–21) → $20 (2022) → $40–50 (2023–24)**, which mostly records **the death of Fiverr's original $5-for-everything model** — an institutional confound with nothing to do with AI, and a reason the pre-2018 window should never be used for levels.
- **The real gap this exposes: there is no control group.** The elasticity regressions correlate category price with category AI benchmarks, but every category is treated, so any platform-wide shock is absorbed into the "AI" coefficient. Nothing currently in the design separates AI from CPI, platform fee/policy changes, the tenure treadmill, or Fiverr's mix shift upmarket. Four fixes queued in `plans/todo.md`, in priority order: (1) report the reputation-adjusted band alongside the raw index, (2) deflate to real terms with BLS CPI, (3) build a DiD on high- vs low-exposure categories so common shocks difference out, (4) an entry-price index as a survivorship-free companion series.
- **Verified:** `code/22-confounder-diagnostics.py` parses and runs end to end (exit 0, 120 lines of output). All figures above are from that run; nothing in `data/pilot/`, `docs/`, or the draft was modified — this session is measurement only.
- **Status: diagnostics built and run, NO paper or site changes yet.** Files: `code/22-confounder-diagnostics.py`, `scratchpad/confounder-diagnostics.out`, `plans/todo.md`, `progress.md`.

## 2026-07-27 — The site's headline chart was still the naive chained index; removed it

- **User: "some of the data seems suspicious, for instance design ipi tripled over 6 years."** They were reading the **top** chart on `docs/index.html`, which was still `DATA.index` — the naive chained-Jevons series (design 2020Q1→2026Q1: **100 → 304**). The GEKS-Jevons chart directly beneath it, the one the 2026-07-15 decision made the method, read **134**. The 2026-07-23 rewire renamed and rewrote everything *around* the second chart but never retired the first, so the page led with the series the project had already rejected.
- **Independent check that GEKS is the right number — direct matched-pair Jevons, no chaining and no multilateral correction at all.** Take the gigs present in both 2020Q1 and 2024Q3 and compare their prices:

  | cat | chained (site) | GEKS | direct 20Q1→24Q3 | n |
  |---|---|---|---|---|
  | design | 317.7 | 146.7 | **154.2** | 17 |
  | coding | 380.2 | 206.0 | **196.8** | 7 |
  | writing | 336.6 | 186.0 | **185.6** | 7 |
  | marketing | 723.0 | 267.7 | **245.0** | 5 |
  | video | 502.0 | 274.2 | **283.2** | 9 |
  | audio | 702.9 | 307.4 | **391.5** | 3 |
  | translation | 238.5 | 227.8 | **282.8** | 2 |

  GEKS tracks the direct comparison in every category; chained runs **1.6–2.7×** high. Only 2–17 gigs survive both endpoints, so this corroborates GEKS rather than pinning it down. Second check, on thick coverage: 2024Q3→2026Q1 direct on **299–570 matched design gigs** gives **94–100** — flat to slightly down, so nothing in the last six quarters supports the continued climb the chained series shows. Design's honest six-year move is roughly **+35–50%**, not +204%.
- **Site fix — one chart, GEKS only.** Deleted the `.fxwrap` card and promoted the GEKS series into the hero card, merging the confidence band into `drawChart` (so the single chart now carries the band, the sharpest-QoQ-move highlights, and the quarter inspector). Removed `drawChartGEKS`, `pinnedFx`, `pinQuarterFx`, `renderInspectorFx`, `#chart2`/`#tip2`/`#qpick2`/`#qreadout2`/`#qclear2` and their CSS. `compositeSeries` now defaults to `DATA.index_geks`; the **Δ'20–'26 column and its sort key moved from `delta12` to `delta_geks`**, and the row sparklines from `DATA.index` to `DATA.index_geks` — these were the last places the inflated series was still visible. Tooltip and axis copy say GEKS-Jevons. In `gallery.js`, removed the silent `DATA.index`/`delta12` fallbacks so the bad series can never reappear by accident. **Zero references to `DATA.index[...]` or `delta12` remain under `docs/`.**
- **New hero bullet explains why a chained index is not used** — gigs are not archived every quarter, so chaining credits a gig's whole multi-quarter change to the one quarter it reappears, on top of the rise already chained in from gigs that were observed in between; 317.7 pts against 144.7. Links to FAQ Step 5.
- **Found a real defect in `code/12-panel-ipi.py` (TD1) — characterised, attempted, reverted.** Line 184 keys within-gig relatives by destination quarter alone, so multi-quarter changes are double-counted. **22–31% of links span >1 quarter in every category.** Minimal repro (true path = one +50% step then flat): as-built gives 100/150/**183.7**, adjacent-only gives 100/150/**150**. Design 2020Q1→2024Q3: as-built 326, adjacent-only 229, direct 154, GEKS 147. `code/14-recent-ipi.py` is **not** affected (adjacent pairs only, lines 149–151), so only the historical segment is wrong — but that is 19 of the site's 25 quarters.
  - **Rewrote it to key by the ordered pair `(q_prev, q_curr)` and reverted.** Anchoring at 2019Q1 with the pair rule drops audio, translation and both `data_*` categories entirely (no link out of the base); anchoring at each category's first linkable quarter instead punches holes in the composite at 2022Q4/2023Q1 and crashes `panel-summary.md`. Choosing among adjacent-only, pair-keyed-with-anchor, and windowing to 2020Q1+ is a **methods decision that moves the paper's peak-composite and chain-drift figures**, not a mechanical fix. Reverted; `data/pilot/panel-category-indices.csv` verified byte-identical to its pre-session state.
  - **Paper consequence:** §3.4 attributes the whole chained-vs-GEKS gap (+217.7% vs +44.6%) to chain drift, but part of it is this defect. Logged as `tests/method.test.md` **R9 FAIL**; the direct-comparison corroboration above logged as **R10 PASS (evidence not yet in the draft)**.
- **Verified:** `node --check` clean on `ipi.js` and `gallery.js`; every `getElementById` in `ipi.js` resolves to an id present in `index.html`, and no stale chart-2 ids remain; ran the full `ipi.js` build path under a DOM shim against the real `data.json` — default view (design) renders 2 paths (band + line) with `geksDelta` **+34.1%** = `delta_geks.design`, all-categories view renders **9 paths** (7 categories + composite + 1 band run), 30 markers, 5 move notes, `geksDelta` **+44.6%** = `composite_geks`; 7 table rows + composite footer. No headless browser in-env, so the visual render is verified structurally/numerically only.
- **Status: edits made, NOT yet committed.** Files: `docs/index.html`, `docs/ipi.js`, `docs/gallery.js`, `plans/todo.md`, `plans/tech-debt-tracker.md`, `tests/method.test.md`, `progress.md`. Unchanged: `docs/data.json` (still carries `index`/`delta12`/`composite_all` for the paper's method comparison — retained deliberately, just not plotted), `code/12-panel-ipi.py`, all of `data/pilot/`.

## 2026-07-23 — Rewire site + paper from fixed effects to GEKS-Jevons (the 2026-07-15 decision, finished)

- **Context:** the 2026-07-15 entry chose GEKS-Jevons and dropped fixed effects, but only the *data* side had been done — `code/18-build-site-data-long.py` was already emitting `index_geks`/`composite_geks`/`*_geks_se` and the rebuilt `docs/data.json` had **dropped the `index_tpd` block entirely**, while `docs/ipi.js` and `docs/gallery.js` still read `DATA.index_tpd`. **The second home-page chart was silently dead** (`if (!DATA.index_geks) return` — key absent → early return) and the gallery had fallen back to the drifting chained series. This session finishes the rewire.
- **JS/data contract.** Renamed throughout `docs/ipi.js`, `docs/gallery.js`, `docs/index.html`, `docs/gallery.html`: `index_tpd`→`index_geks`, `index_tpd_se`→`index_geks_se`, `composite_tpd*`→`composite_geks*`, `delta_tpd`→`delta_geks`, `drawChartTPD`→`drawChartGEKS`, element id `tpdDelta`→`geksDelta`, local `useTpd`→`useGeks`. Zero `tpd`/`TPD` references remain under `docs/`.
- **User-facing copy — every "fixed effects" mention replaced with the GEKS explanation** (the old text described the *wrong* method to readers): chart title "Intelligence Price Index (GEKS-Jevons)"; the three bullets under it now say every quarter is compared with every other directly rather than through a chain, the band is a **bootstrap** 95% CI, and the validation bullet cites the `PriceIndexCalc` exact reproduction instead of "two-way fixed-effects (Time–Product–Dummy)"; tooltip label; gallery badge/caption/footer.
- **FAQ Step 5 rewritten** (`docs/faq.html`) — was "Correcting for irregular sampling (the fixed-effects index)" with the `ln p = α + δ + ε` regression and the plain-language α/δ walkthrough committed two days ago. Now "Correcting for chain drift (the GEKS-Jevons index)": explains that link-level errors compound multiplicatively (chained reads ~2× the drift-free level by 2026), the "compare every pair, average all routes" intuition, then the bilateral Jevons formula and the GEKS transitivity product, and closes on the point that GEKS **never imputes** an unobserved gig-quarter.
- **Method §3.4 rewritten** (`drafts/sections/method.md`) — the TPD/FE paragraph is replaced by four: (1) chain drift quantified (chained +217.7% vs GEKS +44.6%, 2.2×) and the GEKS-Jevons estimator with both equations; (2) sample construction, `MIN_MATCH=3`, the 2020Q1 estimation-window rationale, bootstrap SEs and the ±7.6%→±26% band spread; (3) the TPD comparison framed as **imputation** (de Haan 2004; 10.9%-filled panel ⇒ ~89% of cells imputed) plus the Chessa et al. dump-price bias *tested* (+0.090 vs +0.070 log pts, t=1.34 n.s.) and the full-vs-rolling-window choice; (4) the `PriceIndexCalc` validation including why the reference crashes on our sparser categories. New placeholders: `[CITE-ivancic-diewert-fox-2011]`, `[CITE-ilo-cpi-manual-2004]`, `[CITE-de-haan-2004]`, `[CITE-chessa-verburg-willenborg-2017]`, `[CITE-krsinich-2016]`.
- **Verified:** `node --check` clean on both JS files; every `DATA.*` key referenced by the two scripts exists in `docs/data.json` except the pre-existing guarded `level`/`parents` (absent by design in the long build); all 7 categories carry 25-quarter `index_geks` + `index_geks_se`, translation 22/25 (the known gap — charts pen-up at nulls, which is correct). Draft re-rendered → `drafts/draft-2026-07-23.html`.
- **Tests updated** (`tests/method.test.md`): R1 rewritten for GEKS; added R2 (why GEKS over TPD/weighted multilaterals), R3 (dump-price bias, tested), R4 (window choice), R7 (implementation validation) as PASS; **R5 FAIL** — `MIN_MATCH=3` sensitivity documented but the table isn't in the draft (3→1 moves audio +17 pts, marketing −13); **R6 BLOCKED** — translation publication decision still open; **R8 FAIL** — pre-existing base-period inconsistency, §3.4 composite paragraph says 2019Q1 while the site and GEKS window use 2020Q1. U2/U3 recorded.
- **Still open (unchanged by this session):** the translation coverage decision (report with a ±26% band vs suppress) and the `MIN_MATCH` sensitivity check. Files: `docs/ipi.js`, `docs/gallery.js`, `docs/index.html`, `docs/gallery.html`, `docs/faq.html`, `drafts/sections/method.md`, `drafts/draft-2026-07-23.html`, `tests/method.test.md`, `progress.md`.

## 2026-07-22 — Gig price charts: break the line across coverage gaps (stop bridging missing data)

- **User: "show gaps for missing data — it's misleading to fill in data when really no data exists."** Audited every chart. The **index / category / composite** charts were already honest — they break at `null` quarters (pen-up in `ipi.js`) and the build never carries values forward (`aligned()` leaves `None`; translation genuinely breaks at 2021Q4). The culprit was the **freelancer gig price charts** (`gigChart`, duplicated in `docs/ipi.js` and `docs/gallery.js`): they drew one continuous line through every capture with no gap-breaking, so a gig captured in 2020 and again in 2025 got a straight line **bridging 5.8 years of no data** (worst real case: `dilini9496/flat-minimalist-...-logo`).
- **Why it needed a build-side fix too.** `_compress_series` drops repeated identical prices, so from the compressed series alone you can't tell "flat but observed monthly" from "no coverage at all" — both look like two far-apart points. Fixed at the source: raw captures run ~monthly (median 30d, p90 190d), so wherever two consecutive **raw** captures are >`GAP_DAYS=180` apart (2+ quarters), `_compress_series` now emits an all-`None` sentinel row `[null,null,null,null]`. Testing the raw gap (not the kept-point gap) means flat-but-observed stretches stay connected; only genuine coverage lapses break.
- **Render side.** Both `gigChart` copies now walk the full series and lift the pen at sentinel rows (`isGap = all three tiers null`), so the line breaks and isolated captures show as bare dots. Tier-only-missing at a real capture still connects (unchanged). Y-domain calcs already filter `!= null`, so sentinels don't corrupt scaling; `ser[-1]` stays a real row (sentinels never land first/last), so the archive-URL logic is safe.
- **Impact:** rebuilt `docs/data.json` + `docs/freelancers.json` — **655 of 1440 gigs (815 sentinels)** contained at least one misleading bridge now shown as a gap. Verified: 0 gigs with a sentinel as first/last row; `node --check` clean on both JS files. Files: `code/18-build-site-data-long.py`, `docs/ipi.js`, `docs/gallery.js`, `docs/data.json`, `docs/freelancers.json`.

## 2026-07-15 — GEKS-Jevons: a drift-free index with no regression and no fixed effects

- **User: "use another method besides fixed effects."** The project's drift correction was the time-product-dummy / two-way FE regression (`code/19-tpd-index.py`, site chart 2, method §3.4). Built **GEKS-Jevons** as an independent alternative: for every quarter pair it takes the direct matched Jevons comparison over gigs present in both, then makes those transitive by averaging the direct route against every indirect route through a link quarter. **No chain to drift along, no gig fixed effect** — the gig's price level cancels inside each bilateral difference. Stays in the same matched-model family as the headline index, so it shares *no estimation machinery* with the TPD regression; agreement between the two is therefore informative rather than circular.
- **New `code/21-geks-index.py`** — imports 19's panel construction (identical category assignment, gig→quarter median, ≥2-quarter filter, ≥3-gigs-per-quarter), so only the index formula differs. Writes `panel-/recent-category-indices-geks.csv` + `*-geks-se.csv`. **Bootstrap SEs** (200 reps, gigs resampled with replacement, seed 7) since the bilateral means have no closed-form joint variance — gives the site's bands the same meaning as the TPD regression SEs.
- **Result — the two drift-free methods converge, chained Jevons is the outlier.** Composite 2020Q1→2026Q1: **Jevons +217.7% · TPD +66.1% · GEKS +44.6%.** TPD vs GEKS **r=0.983, mean |diff| 9.4 pts, max 23.3**. Chained sits at **2.2× the GEKS level** at 2026Q1 — independently reproduces the ~2.3× drift the 2026-07-07 pilot measured at a 2019Q1 base. GEKS is also *marginally less* jumpy than TPD (3.30 vs 3.40 mean |QoQ log change|), so drift-freeness costs no volatility.
- **Per-category the two agree on** audio (186 vs 180), marketing (208 vs 199), translation (275 vs 282), video (229 vs 220); **separate on** coding (162 vs 211), design (134 vs 158), writing (141 vs 161), GEKS consistently the more conservative. That spread is the honest uncertainty on the correction — an argument for reporting both.
- **Caught a real failure mode before it shipped (coverage diagnostic).** GEKS reaches quarter *t* from the base only if both `base→l` and `l→t` bilaterals are populated. The panels run back to 2011, where a category's earliest quarter holds 2–4 gigs, so a naive full-history base left most quarters unreachable — **design got an index for 2 of 39 quarters, audio 1 of 32**, and the composite read a meaningless −8.6%. **Fix:** estimate over the reported window (`WINDOW_START = 2020Q1`, which is already the published base period, and standard practice for GEKS). Coverage → **design 23/23, audio 20/20, coding 21/21, video 22/22, writing 21/21**. The TPD regression never had this problem because it identifies all quarters jointly on the largest connected component.
- **Known weak spot: translation.** Only **43%** of its quarter pairs clear the 3-matched-gig bar → 16 of 19 quarters identified. Bootstrap SEs: design ±7.6%, writing ±10.3%, coding ±13.6% vs **audio ±24%, marketing ±24%, translation ±26%**. Thin categories are where the pooled regression borrows strength GEKS cannot.
- **Literature check — why GEKS-Jevons is the defensible primary (user asked "which method do you recommend based on existing research"):**
  1. **GEKS is the canonical fix for our exact problem.** Ivancic, Diewert & Fox (2011), *J. Econometrics* 161(1):24–35, introduced GEKS-in-time specifically to eliminate chain drift in scanner data.
  2. **No quantity data ⇒ only two candidates, and we built both.** The ILO CPI Manual (2004) recommends Jevons at the elementary level exactly when expenditure/quantity info is unavailable — our case (posted prices only; review counts proxy volume at *category* level for weights, not per gig-quarter). This rules out GEKS-Törnqvist and Geary-Khamis at the elementary level, leaving unweighted GEKS-Jevons vs unweighted TPD.
  3. **The two differ only through imputation.** De Haan (2004): the time-dummy regression implicitly generates an *imputation* index, collapsing to the plain matched-model index when there is no entry/exit. Our panel is ~10.9% filled → **TPD imputes ~89% of gig-quarter cells** under the constant-α assumption; GEKS declines to impute and uses matched pairs only. **The +66.1% vs +44.6% gap IS the price of that assumption**, not an arithmetic disagreement.
  4. **The main documented strike against GEKS does not apply here — tested, not assumed.** Chessa, Verburg & Willenborg (2017, Statistics Netherlands / Ottawa Group): GEKS has "a downward bias in cases with dump prices for disappearing products; GK and TPD indices are insensitive." Our GEKS sits *below* TPD = the direction that bias pushes, so ran the test: a gig's **final** observed price change averages **+0.090 log pts vs +0.070 for its other transitions (t=1.34, ns)**; no category shows a significant final-period drop. **No dumping.** Structural reason: **99% of gigs stop being observed mid-panel** → "disappearance" is Wayback *crawl attrition*, not seller delisting — plausibly unrelated to price, unlike scanner-data clearance.
  5. **Full-window, not rolling-window.** RGEKS / Krsinich's FEWS exist because agencies cannot revise published history; ours is a retrospective research index over a fixed window, so full-window GEKS uses all data and avoids an arbitrary splice. Chessa et al. also note rolling-window+splice "has shown signs of drift."
  - **Where TPD still earns its place:** thin categories. Translation clears the 3-matched-gig bar on only 43% of quarter pairs; TPD's imputation is exactly how it covers such gaps (the two agree there anyway: 275 vs 282). ⇒ **Recommendation: GEKS-Jevons primary, TPD retained as robustness.**
- **User decision (2026-07-15): drop fixed effects entirely; GEKS-Jevons is the approach.** That removes the two-methods-agree corroboration, so GEKS now carries the whole drift correction alone → validated the implementation against an external reference before going further.
- **VALIDATION vs external reference — my GEKS math is exactly right.** Ran `code/21-geks-index.py` against **`PriceIndexCalc` 0.7** (`pandas_modules.multilateral.geks`, `bilateral_method="jevons"`) on the *identical* filtered panel, MIN_MATCH=1 to isolate implementation from filter choice. **max|diff| = 0.0000 pts, corr = 1.0000** on audio, marketing, video, writing (script: `scratchpad/validate_geks.py`; venv, since system python is externally-managed).
  - **The reference CRASHED (`ZeroDivisionError`) on coding, design, translation** — our panel has quarter pairs sharing **zero** matched gigs (coding 1 pair, design 5, **translation 25 = 15% of pairs**). The reference assumes a panel dense enough that any two periods share products; ours is not. My averaging over *available* link routes only is therefore a necessary design choice, not a stylistic one.
  - **`MIN_MATCH=3` is a real lever, not a neutral default.** Relaxing 3→1 moves audio's final level **+17 pts** and marketing's **−13 pts**. Set to 3 to mirror `MIN_RELATIVES=3` already used by steps 12/14 (consistent with project convention) — but it must be documented in the paper and carry a sensitivity check.
- **⚠ TRANSLATION IS NOW UNCOVERED — direct consequence of dropping FE.** Only **43%** of translation's quarter pairs clear the 3-matched-gig bar, **15% have zero overlap**, bootstrap band **±26%**, 16/19 quarters identified. FE covered this by imputing (de Haan 2004) — that was its remaining virtue. With FE gone there is no fallback. Options: report translation with an explicit wide band, or flag/suppress it. **Needs a decision before publication.**
- **Verified:** script runs clean; coverage diagnostic printed per category; windowed-vs-full-history base isolated as the sole cause of the first run's collapse (separate diagnostic confirmed design 2→23, audio 1→20 quarters). Dump-price test run on the real historical panel (1,066 final vs 4,318 non-final transitions). External-reference validation as above.
- **Status: method validated + chosen (GEKS-Jevons); NOT yet wired into the site or paper.** GEKS CSVs are new files; Jevons and TPD outputs untouched. Awaiting scope decision (recommendation: GEKS as the primary drift-free index, FE retained as a second robustness check). Files: `code/21-geks-index.py`, `data/pilot/*-geks*.csv`, `progress.md`.

## 2026-07-15 — Common x axis: every gig chart shares one time window

- **User: "for the website implement a common x axis so its the same for all users."** Both gig-price charts (`gigChart` in `docs/ipi.js`, per-seller drill-down; and in `docs/gallery.js`, featured gig) previously **self-scaled** their x axis to that gig's own first/last snapshot (`d0 = days[0]`, `d1 = days[n-1]`). Every chart therefore stretched edge-to-edge regardless of the period it covered — a seller priced only in 2024 looked identical in width to one spanning 2020–2026, and **no two sellers' charts could be read against each other**.
- **Fix:** both files now derive one shared domain from the index window, `xDomain() = [periodStart(DATA.months[0]), periodEnd(DATA.months.at(-1))]` → **2020-01-01 → 2026-03-31**. Points are clamped into the domain. The gig chart now spans the **same window as the index trend chart** above it, so the micro example and the macro index line up.
- **Positional reference marks:** with a fixed window a short gig occupies a small slice, so added faint **year gridlines + ’20…’26 tick labels** (7 ticks). These replace the old per-gig start/end date captions, which were misleading now that they'd always read the same. Exact dates remain in the hover tooltips.
- **Reader-facing notes** (a line covering part of the width is now meaningful, not a bug): gallery footer + featured-gig caption state the shared axis; the seller panel legend in `ipi.js` carries "· shared time axis 2020Q1–2026Q1".
- **Verified** (no headless browser in-env → structural/numerical): `node --check` clean on both files; rendered `gallery.js`'s full build path under a DOM shim → **7 cards, all points inside the plot area, 7/7 distinct x spans** (was: all identical); rendered **all 1,440 gigs** through `ipi.js`'s `gigChart` → **0 points outside the domain, 1,255 distinct x spans**. Sample confirms placement is by real date (translation gig 2024-09→2025-08 sits at x 304–353 of 388; video gig 2020-01→2023-02 at x 40–215).
- **Status: edits made, NOT yet committed.** Files: `docs/ipi.js`, `docs/gallery.js`, `docs/gallery.html`, `progress.md`.

## 2026-07-14 — Gallery page: per-category highlight reel (index trend + featured gig)

- **User: "add a gallery feature/page highlighting some of the graphs of each category, 1–2 for each."** New standalone `docs/gallery.html` + `docs/gallery.js` (self-contained, same vanilla-JS + inline-SVG approach as `ipi.js`; no shared state so it can't break the index page).
- **Each of the 7 categories gets a card with two graphs:** (1) its **price-index trend** — the drift-free fixed-effects series (`DATA.index_tpd`) with a shaded **95% CI band** from `index_tpd_se`, base 2020Q1=100; (2) a **featured real gig's package-price history** (Basic/Standard/Premium ramp) pulled from `freelancers.json`, with a Wayback link to the archived gig. Cards ordered by size of the category's '20–'26 move; each header carries a Δ badge.
- **Featured-gig picker (`featuredGig`)**: the raw gig category tags are noisy (richest gig for a domain is sometimes cross-tagged — e.g. a music-*law* service tagged `audio`). Added a soft **relevance signal** (`CAT_KW` per-category keyword list): on-topic gig wins, then richest price history (most snapshots) with a small bonus for gigs whose price actually moved; falls back to pure richness if nothing matches. Fixed audio→voice/DJ gig, coding→shopify-speed, writing→book-layout, etc.
- **Discoverability:** added a **Gallery** link to the header nav on `docs/index.html` and `docs/faq.html`.
- **Verified:** both files parse; `node --check` clean; ran `gallery.js`'s build path under a DOM shim → **7 cards / 14 SVG charts** with no runtime errors; featured-gig selection validated against real `data.json` + `freelancers.json` (all 7 categories resolve a TPD index + SE and an on-topic multi-point gig). No headless browser in-env, so the visual render is verified structurally/numerically only.
- **Status: edits made, NOT yet committed.** Files: `docs/gallery.html`, `docs/gallery.js`, `docs/index.html`, `docs/faq.html`, `progress.md`.

## 2026-07-14 — Document the fixed-effects (time-dummy) index: how irregular sampling is handled

- **Prompted by the professor's concern** about aggregating freelancers sampled at different rates / covering different time ranges. The time-product-dummy (TPD / two-way fixed-effects) method was already implemented (`code/19-tpd-index.py`) and shown as the site's second chart, but was undocumented in the paper and FAQ.
- **Paper (`drafts/sections/method.md` §3.4):** added a "Robustness to irregular sampling: a time-product-dummy index" paragraph — `ln p_{i,t} = α_i + δ_t + ε_{i,t}`, gig FE absorbs level, quarter FE estimated jointly, `I=100·exp(δ_t)`, largest-connected-component identification, ≥3 gigs/quarter + ≥2 obs/gig, within-quarter medians, per-δ SEs; notes ~26% hist / ~39% recent changes are gap-spanning.
- **FAQ (`docs/faq.html` §8 "How is the index calculated?"):** added plain-language **Step 5** with the A/B logo-gig example (frequently-captured gigs reveal the path shape; each rarely-captured gig's change is spread across the correct quarters instead of piled into the reappearance quarter).
- **Re-rendered** the draft → `drafts/draft-2026-07-14.html`. Both `method.md` and `faq.html` parse/render cleanly.
- **Tests:** `tests/method.test.md` R1 (irregular-sampling critique) → PASS; U1 (user requirement to explain the aggregation) → PASS.
- **Status: edits made, NOT yet committed** (paper drafts + FAQ). Files: `drafts/sections/method.md`, `docs/faq.html`, `drafts/draft-2026-07-14.html`, `tests/method.test.md`, `progress.md`.

## 2026-07-14 — Programmatic data validation: extraction spot-check + fixed-effects confidence bands

Two data-validation deliverables for the fixed-effects chart (professor's "improve data quality programmatically").

- **(A) Price-extraction spot-check — `code/20-validate-extraction.py`:** audits parsed prices with checks *independent* of the pipeline's own `packageList` parser. (1) **Title cross-check** — Fiverr renders the starting price into `og:title` ("…for $15…") separately from the JSON → agreement = independent confirmation. (2) **Presence** — parsed price must appear literally in the HTML. (3) **Reproducibility** — re-run `09-extract-prices.py` on the saved HTML.
  - **Result (n=300, seed=7):** presence **100%**, reproducibility **100%**, title-agreement **88%** overall — but **`packageList` 99.5%** and **the displayed window (2020Q1+) is 100% (202/202)**. All failures are the pre-2017 `old_json` era (9%), which the chart doesn't show → **data behind both charts is clean; noise is confined to a pre-2020 era we don't display.** Flagged rows → `data/pilot/extraction-validation-mismatches.tsv` with Wayback URLs.
- **(B) Fixed-effects confidence bands:** `19-tpd-index.py` computes per-quarter regression **SE** (`Var(β)=σ²(XᵀX)⁻¹` via sparse `splu`) → `*-tpd-se.csv`. `18-build` aligns/splices them → `index_tpd_se` + `composite_tpd_se` in `data.json`. `ipi.js` `drawChartTPD` draws a **shaded 95% band** (`level·exp(±1.96·se)`) around the emphasised line (composite SE recomputed client-side from weighted category SEs). Makes the thin-category caveat visible: composite **±3.2%**, design **±4.1%** vs translation **±34%**, audio **±26%**.
- **Verified:** `node --check` + HTML parse clean; `data.json` has SE fields. **Bands are a visible chart change not renderable in-env (no browser) — verified numerically only.**
- **Status: COMMITTED + PUSHED** on `mockup` (live). Files: `code/20-validate-extraction.py`, `code/19-tpd-index.py`, `code/18-build-site-data-long.py`, `docs/ipi.js`, `docs/index.html`, `docs/data.json`, `data/pilot/*-tpd-se.csv`, `data/pilot/extraction-validation-mismatches.tsv`, `progress.md`.

## 2026-07-14 — Condense header: three paragraphs → two side-by-side boxes

- **User: "too much text at the top."** Replaced the three stacked header paragraphs (`.mission` / `.def` / `.units`) with a two-column `.introgrid` of `.ibox` cards: **"What this is"** (Wayback Machine → track intelligence-work prices since 2020 → separate inflation from AI productivity gains; folds in the IPI definition) and **"How to read it"** (index points, 2020Q1=100, worked examples, levels-in-points/changes-in-percent). Text trimmed for concision; boxes stack to one column under 640px.
- Removed the now-dead `p.mission`/`p.def`/`p.units` CSS; added `.introgrid`/`.ibox`/`.ibox-h` rules.
- **Verified:** `index.html` parses; zero leftover references to the old classes.
- **Status: COMMITTED + PUSHED** on `mockup`. Files: `docs/index.html`, `progress.md`.

## 2026-07-14 — Quarter readout = composite + 7 categories; push pending changes live

- **Quarter-click readout redesign (`docs/ipi.js`):** after the user clarified, `renderInspector` now lists **Composite first, then all 7 categories in alphabetical order**, each with its index level (pts) at the clicked quarter; the repeated quarter block is gone (the dropdown already shows it). Composite = full 7-category composite (selection-independent snapshot). (Note: earlier this session I reverted the readout to the original QoQ/YoY/vs-base percentages at the user's request, then they clarified they wanted the composite+categories layout — this is the reconciled final form.)
- **"Push to the actual website":** confirmed the live site is **https://aismithlab.com/IntelligencePriceIndex/** (custom domain) and **deploys from `mockup`** — it already served the Fixed-Effects chart / `leftcol` / `chart2`, so all earlier pushes were already live. Committed + pushed the remaining pending work.
- **Mission statement at top of site (`docs/index.html`):** added a `.mission` paragraph directly under the `<h1>` — states we use the Internet Archive's **Wayback Machine** to recover historical snapshots of freelance "intelligence" jobs and reconstruct how their prices moved, with the explicit goal of **separating inflation (upward pull) from AI productivity gains (downward push)**. Sits above the existing `.def` and `.units` paragraphs. (Answers the professor's "explain what we're trying to do at the top" item.)
- **Pending work shipped:** (1) `docs/index.html` — a "How to read the units" explainer paragraph in the header (index points vs dollars, base 2020Q1=100, levels-in-points/changes-in-percent) + its `.units` CSS. (2) `code/18-build-site-data-long.py` — `TOP_N` 25 → 100 (more freelancers per category ranking; addresses the professor's "cover more freelancer" item). (3) Rebuilt `docs/data.json` + `docs/freelancers.json` (now 592 sellers; rankings up to 100/category — audio 89, translation 50 are capped by their smaller pools; `index_tpd` intact).
- **Verified:** `data.json`/`freelancers.json` valid JSON; `index.html` parses; readout output simulated against real data (Composite 317.7 pts + 7 categories A→Z at 2026Q1). No headless browser here.
- **Status: COMMITTED + PUSHED** on `mockup` (live). Files: `docs/ipi.js`, `docs/index.html`, `code/18-build-site-data-long.py`, `docs/data.json`, `docs/freelancers.json`, `progress.md`.

## 2026-07-13 — Revert over-deletion: restore main-chart content; fixed-effects chart same size as main

- **Correction:** the prior "clean the charts" pass over-deleted — I removed the on-chart quarter-move highlights AND the `#movenotes` narrative list under the main IPI chart, but the user only meant to remove the *legend*, not the lines. Restored `docs/index.html` + `docs/ipi.js` from commit `705c3ae` (brings back `chartnote`, `movenotes`, `significantMoves`, `renderMoveNotes`, and the on-chart highlight markers), then re-applied only the wanted changes on top.
- **Fixed-effects chart = separate card, same size as main:** wrapped the main-chart card and the fixed-effects card in a `.leftcol` flex column (both 1.45fr → equal width); the category table is the right column. Retitled the bottom chart **"Intelligence Price Index (Fixed Effects)"** (badge dropped). Set `drawChartTPD` height `300 → 420` to match the main chart. Removed the now-unused `.tpddivider`/`.tpdbadge` CSS.
- **Left the main chart fully intact** — quarter-move highlights, the rise/drop legend, and the move-notes list are all back. Did NOT re-remove the "quarter legend" this round; need the user to point at exactly which element they meant.
- **Verified:** `node --check` clean; `index.html` parses; no dangling `tpdBadge`/`tpddivider` refs; `chartnote`/`movenotes` present; `#chart2`/`#tpdDelta`/`leftcol` present.
- **Status: COMMITTED + PUSHED** on `mockup`. Files: `docs/index.html`, `docs/ipi.js`, `progress.md`.

## 2026-07-13 — Clean the charts: separate the fixed-effects chart, drop the quarter-move legend

- **User (chart cleanup):** (1) fully separate the fixed-effects chart from the main IPI chart; (2) title it "Intelligence Price Index (Fixed Effects)"; (3) delete the quarter legend under the main chart, keep only category legends. Maps to the professor's "clean the chart" item.
- **Separated the fixed-effects chart:** moved `#chart2` out of the hero card into its **own full-width `.card` (`.fxwrap`)** below the whole `layout` grid (was nested under the main chart inside one card). Retitled **"Intelligence Price Index (Fixed Effects)"** (dropped the `fixed-effects` badge — redundant with the title). Now full-width so it renders wider/cleaner. `#chart2`/`#tip2`/`#tpdDelta` IDs preserved so JS is unchanged in behavior.
- **Removed the quarter-move highlighting feature from the main chart** (that was the "quarter legend"): deleted the `#chartnote` green/red rise/drop legend, the on-chart green/red QoQ move segments+labels in `drawChart`, and the `#movenotes` narrative list. The **category identification (per-quarter readout with swatches + the selection table) stays** — that's the category legend the user wanted kept. Removed now-dead JS (`significantMoves`, `renderMoveNotes`) and orphaned CSS (`.chartnote`, `.movenotes`, `.tpdbadge`, `.tpddivider`).
- **Verified:** `node --check` clean; `index.html` parses; no dangling refs to any removed id/class/function; required IDs present.
- **Status: COMMITTED + PUSHED** on `mockup`. Files: `docs/index.html`, `docs/ipi.js`, `progress.md`.

## 2026-07-13 — Corrected (time-dummy) index shipped as a second chart under the main IPI chart

- **User decision:** "right under the ipi chart create a new chart with the corrected index." Done — the live site now shows the drift-free time-dummy index directly beneath the main chained index, reacting to the same category selection.
- **Build (`code/18-build-site-data-long.py`):** reads the TPD CSVs (`panel-/recent-category-indices-tpd.csv` from step 19), splices + re-bases them with the *same* `chain_category` logic as the Jevons pair (refactored the forward-fill/composite into reusable `aligned()` / `fill_composite()` helpers), and emits parallel `index_tpd`, `composite_tpd`, `delta_tpd` into `docs/data.json`.
- **Site (`docs/index.html` + `docs/ipi.js`):** new `#chart2` inside the hero card under the main chart, titled "Corrected index" with a live per-basket Δ badge. New `drawChartTPD(cats)` mirrors `drawChart` visuals (pts gridlines, axis title, category lines + black composite, endpoint dots) but reads `DATA.index_tpd`, shares the global `pinned` quarter (click either chart to mark both), and has its own hover tooltip (`#tip2`). `compositeSeries(cats, src)` generalized to take a data source. Wired into `render()` so it redraws on selection/pin/resize.
- **Verified:** `node --check` clean; `index.html` parses; client-side TPD composite recompute == build (`166.1`, `+66.1%`); resize handler (`ipi.js:696`) redraws both. No headless browser in this env, so not screenshotted — rendering code mirrors the proven `drawChart` path.
- **Status: COMMITTED + PUSHED** on `mockup`. Files: `docs/index.html`, `docs/ipi.js`, `docs/data.json`, `code/18-build-site-data-long.py`, `progress.md`.

## 2026-07-13 — Time-dummy (TPD) index to fix misaligned-stream timing + per-quarter inspector redesign

- **User goal:** the price streams per freelancer have different windows and sampling rates; they want the index to "correctly show when prices moved," and want the chart's per-quarter readout to list composite-on-top then categories A→Z.
- **Diagnostic first (`scratchpad/panel_loss.py`):** the current chained-Jevons panel (12/14) is already gap-tolerant (matches a gig to its *previous observed* quarter, not the calendar-adjacent one), so gappy gigs aren't dropped — but a multi-quarter change is attributed to the single quarter a gig reappears. Measured on real data: **26% of historical and 39% of recent price changes are such gap-spanning jumps**; 34% of historical gigs have only 1 quarter (unavoidably unusable for a *change*). So the real symptom is a **jumpy, mis-timed** index, not missing freelancers.
- **Built the fix — `code/19-tpd-index.py` (Time-Product-Dummy regression):** per category, `ln price ~ gig fixed effect + quarter effect`, estimated by sparse least squares (scipy `lsqr`) on the **largest connected gig–quarter component** (so every quarter effect is identified vs the base). Reuses 12/14's exact panel construction (same category assignment, gig→quarter median price, ≥2-quarter filter, ≥3-gigs-per-quarter). Writes **new** CSVs (`panel-category-indices-tpd.csv`, `recent-category-indices-tpd.csv`) — the live Jevons CSVs are untouched. Splices + re-bases with 18-build's logic to compare.
- **Result (spliced composite, 2020Q1=100):** cumulative rise **+217.7% (Jevons) → +66.1% (TPD)** — a **~3.3× overstatement**, consistent with the paper's own limitation note (chained overstates the true rise). Composite jumpiness (mean |QoQ log change|) **5.75 → 3.40 (−41%)** — the timing fix works. Caveat surfaced: thin cats (translation/audio/video) swing *more* under TPD (each quarter estimated freely, no chaining smoothness); translation even reads higher (282 vs 209) on ~26–61 gigs.
- **Decision aid published (artifact):** overlay of the two composite lines with the drift band shaded, stat tiles, plain-language explainer, per-category landing table. https://claude.ai/code/artifact/2d4ba133-d43c-4e33-bf01-9f034efefb8e
- **UI — per-quarter inspector (`docs/ipi.js` `renderInspector`):** rewrote so clicking a quarter now lists **Composite on top, then each selected category alphabetically**, each with its own index level (pts) at that quarter and a color swatch (was: single series with QoQ/YoY/vs-base chips). Call site passes `mainChecked`.
- **NOT yet wired into the live site** — swapping the headline from +218% to +66% is a paper-level methodology decision; awaiting user direction on integration (replace / show both / robustness-check-only).
- **Verified:** `node --check docs/ipi.js` passes; `19-tpd-index.py` runs clean, indices identified on connected components. `scratchpad/` added to `.gitignore`.
- **Status:** inspector + TPD script **COMMITTED**; live index unchanged. Files: `docs/ipi.js`, `code/19-tpd-index.py`, `data/pilot/*-tpd.csv`, `.gitignore`, `progress.md`.

## 2026-07-13 — Sync new FAQ Q3 into live site + default category list to alphabetical

- **Two-task request.** (1) Push the updated draft FAQ Q3 into the live `docs/faq.html`; (2) make the right-hand category selection list render in alphabetical order.
- **Q3 sync (`docs/faq.html`):** commit `35c3760 "Update FAQ on index reading and price changes"` had rewritten `drafts/sections/faq.md` Q3 into a tighter two-paragraph version (drops the above/below-100 bullet list; leads with "a level records the cumulative percentage change… rather than a dollar amount," then a second paragraph on reading the *ordering* not the height). The live page still carried the older bullet version. Replaced the live Q3 with the draft text, keeping the site's conventions: `index points` unit on the 130 reading, and the `#inflation` / `#caveats` anchor links (draft's "inflation" and "limitations" mentions).
- **Alphabetical categories (`docs/ipi.js`):** default sort was `sortK = "delta"` (largest movers first). Changed the default to `sortK = "name"` so the list opens A→Z (audio, coding, design, marketing, translation, video, writing); the clickable column headers still let a user re-sort by Δ / weight / gigs. Also switched the nested subcategory detail lines from delta-order to `labelOf().localeCompare()` so drill-downs are alphabetical too (no subs in the current broad-category `data.json`, but correct for narrow builds).
- **Verified:** `node --check docs/ipi.js` passes; `data.json` categories are all main-level and already stored alphabetically, so the A→Z render is confirmed by inspection. No headless browser in this env.
- **Status: COMMITTED + PUSHED** on `mockup`. Files: `docs/faq.html`, `docs/ipi.js`, `progress.md`.

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
