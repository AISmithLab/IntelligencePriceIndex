# How does generative AI diffusion change long-run pricing and competitive structure in online freelancer markets?

**Answer assembled 2026-08-18, last revised 2026-08-20 from data already
collected.**
Sources: the IPI panel (`data/pilot/paper-numbers.md`, frozen 2026-07-31), the
balanced archival frame (`data/pilot/balanced-prices.csv`, 257,208 gig-quarter
observations on 37,888 listings, 2019Q3–2024Q4), the recent live frame
(`data/pilot/recent-prices.csv`, 2024Q3–2026Q1), Fiverr Inc.'s reported metrics
(`data/fiverr-inc-metrics.csv`), and steps 46–59.

**What the 2026-08-20 revision changed.** We now know **what buyers actually
paid**, and it is not what the price index measures. Every archived gig page
carries a hidden block of order records — one per displayed review, each with an
order date, an order id, and the amount the buyer paid in a price band. The
extractor had been discarding it since 2019. Reading it back (§1.3) shows that
**orders under $50 are 1.0% of all orders**, against a listed entry-package
median of $25–30: buyers almost never buy the package the index prices. Three
consequences. (i) §1.3 stops being a caveat about something unmeasurable and
becomes a measurement. (ii) The implied "orders −18%" in §2 divides revenue by a
price nobody pays, and is flagged as such. (iii) §5's entry saying realised order
value is "not measurable at any effort" was **wrong** and has been removed. The
field only starts in 2022 and roughly an eighth of orders are recovered, so this
is a new resource with real limits, not a finished index — see §1.3 and §6.

**What the 2026-08-19 revision changed.** One thing, and it is the largest
single addition since the answer was assembled. **Generative AI is now measured
inside the market rather than assumed from a calendar** (§3.7): gig titles, held
on 100.0% of observations and never used by any design, give a quarterly
diffusion series. It breaks at **2023Q1**, diffusion runs through **entry rather
than incumbent conversion**, AI listings sit **above** the median price, and an
**anti-AI segment appears from exactly zero in 2023Q2**. Critically, this
supplies the **positive control the identification argument was missing**
(§4.3.1): the same searched-break procedure that ranks ChatGPT 11th of 15 on the
transaction proxy ranks it **1st of 19** here. The instrument is not blind — so
the absence of AI from the pricing and structure results is a fact about the
market, not about the method.

**What the earlier 2026-08-19 revision changed.** Three things, none of them descriptive.
(i) The scope of the null is now **dated to 2024Q4** and the 2025–26 window is
reported separately, because both platform operators have since attributed their
declines to AI and both are describing a period our structure frame does not
cover (§2.5). (ii) The AI *timing* claim is now falsified rather than merely
unsupported: the break in the transaction proxy was searched over 15 quarters and
the ChatGPT and image-model dates are the **worst-fitting** candidates (§4.3).
(iii) Two new designs were run directly on the 2025–26 window and both failed
(§4.4), bringing the count to **eight designs, eight failures**.

---

## How to read this document

The findings below are stated in the vocabulary of applied econometrics. Here is
what the recurring terms mean in plain language, so the results can be read
without it.

| term | what it means here |
|---|---|
| **listed price** | the price a seller advertises on the gig page. This is what the index measures. |
| **realised price** | what a buyer actually paid on a completed order. Newly recovered — see §1.3. |
| **nominal vs real** | *nominal* is the dollar figure as observed; *real* subtracts general inflation (CPI-U). A +78% nominal rise is +41% real. |
| **matched-model index** | prices are compared **within the same listing over time**, never across different listings, so a change in *which* listings exist cannot masquerade as a change in price. |
| **balanced panel / frame** | a fixed set of listings observed in every period. Used wherever a change over time is claimed, because a changing sample manufactures trends on its own. |
| **fixed effects** | a control that strips out everything permanently distinctive about a listing (or a quarter), leaving only *changes* to be compared. |
| **a break** | a date at which a series changes its level or its slope. |
| **a searched break** | instead of assuming a date and testing it, the break is fitted at *every* candidate quarter and the best-fitting one reported. This is what allows the claim that the market turned *before* ChatGPT, rather than merely that it did not turn *at* ChatGPT. |
| **a placebo test** | the identical test run where the answer must be "nothing" — a fake date, an unrelated series, a period before the technology existed. If it still finds an effect, the test is broken, not the world. |
| **parallel trends** | the assumption behind any before/after comparison of two groups: they must have been moving in step *beforehand*. If they were not, a post-event gap may just be the old divergence continuing. |
| **exposure** | an external score of how much of a category's work is the kind generative AI can do, built from O\*NET occupation text. It is the "treatment" in most designs here, and a known weak point. |
| **MDE** (minimum detectable effect) | the smallest effect a test could have detected. A null on a large MDE means *we could not have seen it*, not *it is not there*. |
| **Gini** | a 0–1 concentration measure. 0 = every listing sells equally; 1 = one listing takes everything. |
| **a gate** | a pass/fail check fixed **before** the result is seen. A finding that fails a gate is not reported as a finding, however good it looks. |

Two conventions carry most of the argument's weight. **Break dates are searched,
not assumed**, so a claim that this market turned in 2020 is a claim about which
date fits best — not about which date we happened to test. And **every promising
result is gated on a placebo before it is reported**, which is why this document
contains more failed designs than findings.

---

## 0. The answer in one page

**On pricing, the data are decisive and the direction is the opposite of the
standard prediction.** Listed prices for cognitive-labour services rose
**+40.7% in real terms** over 2020Q1–2026Q1 (+78.4% nominal, ±3.7%), against
CPI-U of +26.8%. Roughly half the nominal rise is general inflation and a large
further share is reputation accumulation; a reputation-adjusted composite floors
the real rise at about **+39.7%** on a raw ceiling of **+79.0%**. Prices did not
fall in any category, in any specification, at any point in the diffusion window.

**Buyers were not paying the advertised price, and we can now show it.** The
index reads listed entry-package prices, typically $25–30. Order records
recovered from the same archived pages (§1.3) show **1.0% of orders were under
$50** and roughly two-thirds were $50–200. The listed price is a real and
well-measured quantity, but it is the *advertised* one; what buyers actually
spent per order runs several times higher. This is measurable from 2022 onward,
which is late enough that it cannot yet extend the long-run index.

**On competitive structure, four of the five things a commoditisation story
predicts did not happen, and the fifth happened too early to be caused by
generative AI.**

| what a commoditisation story predicts | what the data show |
|---|---|
| prices fall | real prices **+40.7%** |
| quantities rise | Fiverr buyers **−36%** from the 2021 peak; implied orders **−18%** vs 2020 (an upper bound — the divisor is the *listed* price, §1.3) |
| the cheap tier widens | the **$5 tier emptied**, 27.3% → 10.3% of listings — but its steepest decline is **2021Q2**, and the decline **slows** after ChatGPT |
| price competition intensifies | repricing **fell** (23.6% → 18.3% of listing-quarters), and the fall is **entirely fewer price increases**; price cuts are flat at ~5–6% |
| sales concentrate on winners | Gini among trading listings **flat** (0.64 → 0.61); among trading **sellers** flat too (0.637 → 0.618) |

**On attribution, the honest answer is that this project cannot assign any of it
to generative AI, and it now knows precisely why.** Nine identification designs
have now been run and all nine have failed (§4), the latest at monthly resolution
against twenty named product launches. Their joint diagnosis is not a shrug but a dated fact:
**six series in this project turned in the same eighteen months, 2020Q3–2021Q4,
and none of them was dated by us in advance.**

| series | turn | how dated |
|---|---|---|
| within-gig transaction proxy | **2020Q4** | searched over 15 quarters (§4.3) |
| cheap-end relative performance | **2020Q3** | searched over 17 quarters (§4.4.2) |
| $5 commodity tier | **2021Q2** | searched (§3.1) |
| repricing frequency | **2021Q3** | searched (§3.5) |
| Fiverr active buyers | **2021** | company reports (§2) |
| Ramp marketplace spend share | **2021Q4** | external panel (§2.5.1) |

Against that, the ChatGPT quarter ranks **11th of 15** as a break in the
transaction proxy and **16th of 17** in the cheap-end series, and the image-model
dates rank last. **Generative AI was not in commercial use in these categories in
any of those six windows.** Whatever bent this market, it started bending before
the technology arrived.

**Generative AI is in this market, and we can now date its arrival to the
quarter.** The share of *new* listings advertising AI runs at 0.0–0.5% from 2019
through 2022Q4 and jumps to **5.98% in 2023Q1**, the first full quarter after
ChatGPT — a twelvefold move in one quarter, ranking **1st of 19** candidate break
quarters, with the next three ranks also taken by AI milestone quarters (§3.7).
It diffused through **entry**: of 11,425 listings observed in both 2022 and 2024,
**22** ever relabelled themselves as AI. It entered **above** the median price,
not below it. And it created a segment that did not previously exist — listings
selling explicitly *human* production are **exactly zero in every quarter to
2023Q1** and appear from 2023Q2.

**That measure is also the positive control the argument was missing.** The same
searched-break procedure that ranks ChatGPT 11th of 15 on the transaction proxy
and 16th of 17 on the cheap-end series ranks it **1st of 19** on the diffusion
series, with an SSR spread of 227% against 0.06%. The instrument resolves the AI
date to within one quarter when the variable is one AI moved. **So the failure to
find AI in prices and structure is a fact about this market, not a fact about the
method** (§4.3.1).

**So the defensible answer is a joint description, not a causal claim.** Across
the generative-AI diffusion window this market moved *upmarket*: fewer and larger
buyers, higher listed prices, a hollowed-out commodity tier, deeper product
menus, no price war, and no change in who captures the sales. That is the shape
of a market being **repositioned** — by sellers, by the platform, and by a
composition shift in demand — not the shape of a market being **commoditised**.
Whether generative AI caused the repositioning is not identified on this data,
and the timing evidence (§4.3) is actively unhelpful to an AI account.

**And the whole of the above is a statement about the period up to 2024Q4.** It
is not a statement about 2025–26. Both operators now attribute their declines to
AI explicitly, and the period they describe is one the structure frame barely
reaches (§2.5). Two designs were run on the recent frame anyway; both failed, and
one of them failed on **power** rather than on sign, which means the recent
window is currently **uninformative** rather than null (§4.5). The title *What
Generative AI Did Not Do* is defensible only in its dated form: **what it had not
yet done by 2024Q4.**

---

## 1. The pricing half

### 1.1 Level

Matched-model GEKS-Jevons index over seven categories, 2020Q1 = 100. (The index
compares each listing only with itself over time, then chains the categories
together with equal weight on every pair of periods — the standard construction
for goods that appear and disappear from the market.)

| series | terminal 2026Q1 nominal | real | real Δ | ±95% |
|---|---:|---:|---:|---:|
| **composite** | 178.4 | 140.7 | **+40.7%** | ±3.7% |
| design | 156.1 | 123.2 | +23.2% | ±4.8% |
| writing | 201.8 | 159.2 | +59.2% | ±8.3% |
| marketing | 294.3 | 232.2 | +132.1% | ±7.7% |
| coding | 250.1 | 197.3 | +97.3% | ±17.1% |
| video | 265.6 | 209.5 | +109.5% | ±11.9% |
| audio | 322.3 | 254.2 | +154.2% | ±13.9% |
| translation | 299.5 | 236.3 | +136.3% | ±29.2% |

**Do not rank the categories.** Six of seven miss the ±5% precision standard the
project sets; the top three intervals overlap completely. In particular
translation — the most AI-exposed category on the pre-registered exposure
measure (β 0.840) — carries a ±29.2% band on 28 panel gigs.

### 1.2 What the rise is made of

- **General inflation** accounts for roughly half the nominal increase
  (CPI-U +26.8% against nominal +78.4%).
- **Reputation accumulation** accounts for a large further share. Within a gig,
  price rises **+7.7% per doubling of cumulative reviews**; rebuilding the index
  on reputation-adjusted prices gives a composite band of **+39.7% to +79.0%**.
  The floor is soft — β's own 95% CI moves it between roughly +50% and +28% —
  and it is a lower bound rather than a correction, because review counts are
  cumulative sales and so β absorbs demand as well as standing.
- **What remains** is not attributable. See §4.

### 1.3 What "price" means here — and what buyers actually paid

The index reads **listed basic-package prices**: the entry-tier figure a seller
advertises. That is a clean, comparable, well-measured quantity, and it is not
what changes hands.

Until 2026-08-20 this was recorded here as a caveat about something we could not
measure. That was wrong. Every archived gig page carries an embedded block of
**order records** — one per displayed review — and each record holds an order id,
the **date of the order** (not of the capture), and the amount the buyer paid,
reported as a price band. The extractor kept the listed prices and dropped the
rest, so this has been sitting in the stored pages the whole time. Recovering it
needs **no new collection** (`code/59-review-order-audit.py`).

**What buyers paid**, across 2,883 priced orders on a 1,226-page pilot sample:

| band | share of orders | cumulative |
|---|---:|---:|
| $5–20 | 0.2% | 0.2% |
| $20–50 | 0.9% | 1.0% |
| **$50–100** | **37.5%** | 38.6% |
| **$100–200** | **29.8%** | 68.4% |
| $200–400 | 16.9% | 85.3% |
| $400–600 | 6.2% | 91.5% |
| $600–1,000 | 3.5% | 94.9% |
| $1,000–10,000+ | 5.1% | 100.0% |

**Orders under $50 are 1.0% of all orders**, against a listed basic-package
median of about $25–30. Buyers essentially never buy the advertised entry
package: two-thirds of orders land in $50–200. Fiverr's rising spend per buyer
(§2) is therefore visible in individual transactions and not only in company
aggregates, and this section's former *conjecture* — that realised prices rose
faster than listed ones — now has a level measurement underneath it.

**Three limits decide what this can and cannot be used for.**

1. **It starts in 2022.** The paid-amount field is absent from essentially every
   2018–2021 capture (0.0–0.8% of sampled pages) and appears on 64.2% of 2022
   pages. Orders placed *before* 2022 do carry amounts when a 2022-or-later page
   displays them (2020: 58.1%, 2021: 22.9%), but pages show recent reviews, so
   the pre-ChatGPT baseline this can support is roughly one year and
   back-filled. That is enough to compare levels. It is **not** enough for the
   long-run diffusion question the listed-price index answers.
2. **About an eighth of orders are recovered, and not at random.** A page
   displays a median of 4.2 reviews against a median gig lifetime total of 168.
   Pooling repeated captures of the same gig accumulates distinct order ids: on a
   59-gig pooling subsample the median is **41 distinct orders per gig**, but
   that is only **13.1%** of the new orders implied by those gigs' own
   review-count growth. (**9,783** gigs have the ≥8 captures since 2022 that make
   pooling worthwhile; the 41 and the 13.1% are measured on the 59-gig
   subsample, and both need re-measuring at full scale.) And pages choose which reviews to display by a
   `relevancy_score`, **not at random**. Until it is shown that displayed orders
   are not selected on price, the table above describes *displayed* orders, not
   all orders. This is the central threat to any index built on it.

   The weaker check that can be run today passes. Orders that carry a price and
   orders that do not are near-identical on rating (4.877 vs 4.879), repeat-buyer
   share (39.1% vs 35.9%) and business-buyer share (9.3% vs 7.0%). That says the
   *price field* is not missing selectively. It says nothing about which orders
   get shown.
3. **Amounts are bands, not numbers**, with an open top ($10,000+). Any index
   built on them needs interval regression or midpoint imputation — not a mean.

**What this changes elsewhere.** Every quantity figure obtained by dividing
revenue by the index is deflating by a price buyers do not pay, so the implied
order decline in §2 stays an **upper bound on the quantity decline** — but the
reasoning behind that bound is now measured rather than assumed. And §5's entry
declaring realised order value unmeasurable was wrong; it has been removed, and
the re-extraction is now the second-highest-value item in §6.

**Scale, if it is built.** 9,783 poolable gigs at the subsample's median of 41
distinct orders each, roughly 55% of them priced — an extrapolation, and one on
the order of **10⁵ dated, priced transactions**. That
would be the first transaction-level data in the project, and a direct
replacement for `review_count` as the sales proxy.

---

## 2. The quantity half — where the transaction numbers come from

Three sources, answering different questions.

- **Fiverr Inc.'s reported metrics** (NYSE: FVRR) are the only *market-wide*
  quantities. GMV = active buyers × spend per buyer is an accounting identity
  rather than an estimate, and it reproduces every independently reported GMV to
  within rounding.
- **Order records inside the archived pages** (§1.3) are the only
  *transaction-level* quantities. They begin in 2022 and recover about an eighth
  of orders, so they can currently anchor a level, not a time series.
- **`review_count`** carries everything in between — the per-gig demand results
  below. It is a **proxy** for sales, not a count of them.

**Fiverr Inc.'s reported quantities:**

| period | buyers (M) | $/buyer | GMV ($M) | buyers YoY |
|---|---:|---:|---:|---:|
| 2020 | 3.40 | 205 | 699 | +44.7% |
| 2021 | **4.20** | 242 | 1,020 | +23.5% |
| 2022 | 4.20 | 262 | 1,090 | **+0.0%** |
| 2023 | 4.10 | 278 | **1,140** | −2.4% |
| 2024 | 3.60 | 302 | 1,087 | −12.2% |
| 2025 | 3.10 | 342 | 1,060 | −13.9% |
| 2026 TTM-Q2 | **2.70** | 368 | 994 | −12.9% |

Three facts matter for the structure question.

1. **Buyers peaked in 2021 and are −36%.** GMV is only −12.8% from its peak. The
   entire gap is spend per buyer, which rose *every single year* from $119 (2017)
   to $368. **Fewer, larger buyers.**
2. **Implied order count.** Deflating GMV by CPI-U and dividing by the IPI real
   composite gives real GMV +11.3%, real price +35.8%, and therefore
   **orders −18.0% vs 2020, −38.6% from the 2021 peak.** Read this as an **upper
   bound on the decline — and the bound is now measured, not assumed.** The
   divisor is the *listed* entry price, and §1.3 shows buyers hardly ever pay it:
   99% of orders are above $50 against a listed median of $25–30. If what buyers
   actually paid rose faster than the listed index, then real prices rose more
   than +35.8% and the order count fell by less than 18.0%.
3. **This kills the leading rival explanation for the archive's demand result.**
   The 13–43% fall in per-gig review accrual at 2022Q4 was equally consistent
   with two very different stories: sales really fell, or buyers simply began
   leaving reviews less often (**review-propensity drift**), which would make
   sales look like they fell when they had not. Fiverr's buyer and GMV series
   have nothing to do with reviewing behaviour, and they fall too. **The
   direction is externally corroborated.**

The archive's own demand result, for completeness (step 46, gig FE + linear
trend, gig-clustered SEs, break at 2022Q4):

| category | exposure arm | break in review accrual | t |
|---|---|---:|---:|
| writing | HIGH | −42.9% | −23.00 |
| translation | HIGH | −37.2% | −13.48 |
| audio | **LOW** | −35.5% | −15.28 |
| coding | mid | −35.2% | −17.63 |
| video | **LOW** | −28.6% | −14.49 |
| marketing | mid | −23.7% | −8.49 |
| design | mid | −13.1% | −6.65 |

**Every category fell, including the least exposed ones**, and the least-exposed
category of the seven (audio, β 0.248) has the third-largest fall. Spearman ρ
between exposure rank and break size is +0.429 over seven categories, where
|ρ| > 0.79 is needed for p < 0.05. That is what a **platform-wide** shock looks
like.

---

## 2.5 The operators' own account — what it corroborates, and the window problem it creates

Checked against company releases and one independent spend dataset on 2026-08-19.
This section exists because the external evidence does two opposite things at
once: it **confirms the descriptive findings to the digit** and it **dates the
AI-attributed decline to a period this project's structure frame does not cover.**

### 2.5.1 Confirmed

Fiverr's Q2-2026 release reports annual active buyers **2.7M (−21.9% YoY)**,
annual spend per buyer **$368 (+15.6%)**, take rate 28.0%.
`data/fiverr-inc-metrics.csv` carries 2.70 and 368 for TTM-2026Q2 — both exact.
The upmarket repositioning in §2 is the platform's **own stated strategy**, not
our inference. Ramp's corporate-card panel, which has nothing to do with our data
or with Fiverr, puts labour-marketplace share of corporate spend at **0.66% in
2021Q4 → 0.14% in 2025Q3**; its peak is 2021Q4, corroborating the 2020–21 turn
that four of our own series independently date (§4.3).

### 2.5.2 The revenue direction, corrected

An earlier note in this project used FY2025 revenue growth (+10.1% to $430.9M) to
argue that the "revenue is declining" premise was wrong. It was right, one year
early.

| | Q2 2025 | Q2 2026 | change |
|---|---:|---:|---:|
| total revenue | $108.6M | **$97.8M** | **−10.0%** |
| marketplace revenue | $74.7M | **$63.1M** | **−15.5%** |

Marketplace revenue — the take on gig transactions, which is the part a price
index is about — is falling *faster* than total revenue.

### 2.5.3 The window problem

Both operators attribute the decline to AI **explicitly**, and both are
describing 2025–26:

- **Fiverr, Q2 2026.** Rapid AI adoption is reducing high-volume, low-value
  transactional work; "AI-related demand and traffic headwinds" and weakness in
  AI-exposed categories are cited as the reason for revised 2026 guidance.
- **Upwork, Q2 2026.** Full-year revenue midpoint cut $35M; active clients −4%,
  GSV −3.6%. The decline is concentrated in **contracts under $500**. Upwork had
  flagged ~10% of GSV as AI-exposed and says erosion inside that group is running
  ahead of plan.
- **Ramp.** Most-exposed firms substitute **$1 of freelance spend for $0.03 of
  AI provider spend.**

Against that: the balanced structure frame ends **2024Q4**, and designs I1–I6 all
treat 2022Q4–2024Q4 as "post". **Six designs concluded "no AI effect" on a window
that mostly precedes the period the operators are describing.** That is a real
limitation and it is the strongest live threat to the paper — stronger than any
reviewer critique currently recorded in the test files.

It is **not** a reason to retract anything in §1–§3. Prices, the emptied $5 tier,
flat concentration, the absent price war, and fewer-and-larger buyers are all
corroborated by the operators' own accounts. It is a reason to **date the claim
and stop generalising past the frame** — which §0 now does — and to test the
recent window directly, which §4.4 does.

**Two of the operators' statements are specific enough to be testable on our
data, and both were tested.** Fiverr's "weakness in AI-exposed categories" is
tested in §4.4.1; Upwork's under-$500 concentration in §4.4.2.

---

## 3. The structure half — five facts, each with the guard that could have killed it

All figures are read off a **balanced panel** wherever a change over time is
claimed. This is not a formality: the quota manifest adds ~1,250 net listings at
2022Q3 and the added ones are cheaper, which manufactures a +5.7pp jump in the
≤$10 share one quarter before the break of interest. **Gig fixed effects do not
protect against composition.**

**In plain terms:** if the set of listings you are looking at changes, the market
can appear to move when no individual listing has moved at all. Holding the set
fixed is the only defence, and holding listings fixed *statistically* is not the
same defence — new listings arriving still shift the average.

### 3.1 The commodity tier emptied — but before ChatGPT

Share of listings priced at $5, fixed panel: **27.3% (2019Q3) → 10.3% (2024Q4)**.
On all listings, 32.0% → 11.4%. The $100+ tier moved the other way, 15.6% → 22.4%.
Median listed price $15 → $30.

The break date was **searched, not assumed**, and this decides the interpretation:

- best trend break on the balanced panel is **2021Q2**;
- the ChatGPT quarter carries the **opposite sign**;
- the decline **slows** after 2022Q4.

Assuming 2022Q4 returns a significant coefficient and would have produced a wrong
headline. The commodity tier emptied on a schedule that generative AI cannot
explain — the steepest decline is eighteen months before ChatGPT's release.

### 3.2 Product lines got deeper and the ladder compressed

Fixed panel, 2019Q3 → 2024Q4: share of listings offering three tiers
**82.1% → 90.6%**; the premium/basic ratio among three-tier listings
**4.06× → 3.80×**. Sellers version more and spread their own menu less widely —
consistent with menu design converging on a platform template, and with sellers
raising the floor faster than the ceiling.

### 3.3 Dispersion fell, then partly recovered

sd of log price, fixed panel: **1.428 (2019Q3) → 1.150 (2023Q3) → 1.233 (2024Q4)**.
The trough is mid-2023. **Descriptive only** — an attempt to convert this into a
convergence result died in §4.

### 3.4 Sales did not concentrate — at listing level or at seller level

Listing-level Gini of quarterly review accrual rises 0.63 → 0.75, which looks
like a winner-take-all result and is not one. Gini **among listings with any
sales** is flat (2021 0.64 → 2023 0.61). The whole rise is the zero-sales share,
and that rises only in 2024 — the trailing edge where captures per quarter
collapse from ~9,300 to ~700. It is dormancy at the edge of the crawl, not a
shift of share.

**In plain terms:** concentration appears to rise only because more listings
record zero sales, and they record zero because the crawl stopped seeing them —
not because their sales went to somebody else. Among listings that actually sold
anything, the split is unchanged.

Step 51 closed the obvious objection: that is *listing*-level, and the
competitive question is about *sellers*. Aggregating accrual to the seller
(29,835 distinct sellers) changes nothing — Gini among trading sellers
**0.637 (2021) → 0.618 (2023) → 0.651 (2024)**, top-decile share of seller
accrual 51.5% → 50.5% → 56.4%, on the same 2024-only pattern. Listings per seller
in frame is flat at 1.09–1.15, though that number is a property of the quota
sample rather than of Fiverr.

### 3.5 Sellers stopped raising prices — they did not start cutting them

This is the one new fact in this assembly (step 51), and it is the seller-conduct
counterpart to the price level in §1. Consecutive-quarter pairs for the same
listing, balanced panel, pre (2020Q4–2022Q3) vs post (2022Q4–2023Q4):

| | pre | post |
|---|---:|---:|
| share of listing-quarters with any price change | **23.6%** | **18.3%** |
| …an increase | **18.1%** | **12.4%** |
| …a cut | 5.4% | 5.9% |
| mean Δlog price per quarter | **+0.0565** | **+0.0239** |

**The fall in repricing is almost entirely a fall in price increases. Cuts are
flat.** The engine that produced the +78% nominal index throttled back after 2022
without reversing: sellers stopped pushing prices up but would not push them
down — **downward nominal rigidity** in a market with falling demand, which is
the opposite of a price war. A searched break confirms it is not a ChatGPT event —
the best break for any-change is **2021Q3** and the ChatGPT quarter is
insignificant and *positively* signed; for price cuts the best break is 2022Q3,
one quarter *before* ChatGPT, and the ChatGPT-quarter coefficient is −0.0005.

**Not a coverage artefact.** On a strict panel of **936 listings present in every
quarter** of the balanced window, the same pattern holds — any change 24.1% →
18.1%, increases 18.5% → 12.0%, cuts 5.6% → 6.1% — while observed pairs per
listing move only −1.9% across the break.

A companion measure — the Spearman correlation of a listing's within-category
price rank across four quarters — **rises** (0.898 → 0.940 balanced), i.e. the
price ordering became *more* rigid, the opposite of a technology reshuffling who
can charge what. It is recorded as **not independent evidence**: a listing that
never reprices cannot change rank except through what others do, so rising rank
persistence is the §3.5 fact restated.

### 3.6 One lead, explicitly not a finding

The within-listing price return to reputation is **+11.3% per doubling of reviews
pre-ChatGPT and +18.5% post** on the balanced panel (difference +0.091, t 2.04),
and it clears a placebo split at a false 2021Q2 break (−0.012, t −0.54). If real,
it would say incumbency became more valuable exactly when output became cheap to
produce — the most economically interesting structural claim available here.

**On all 37,888 listings the same difference is +0.0060 (t 0.79), a precise
zero.** A result that appears on 2,750 listings and vanishes on the frame that
contains them is a lead, not a finding, and is recorded as one.

---

## 3.7 The diffusion half — AI measured inside the market, not assumed from a calendar

Everything above shares one weakness, and step 57 is the first thing in the
project to remove it. **Designs 1–8 all proxied "AI" with something external to
the market** — an occupation-exposure score, or a release date. The score is thin
(36.8% of gigs zero-match) and varies over seven categories; the date is a guess
about when a technology mattered here.

The panel has carried a direct measure the whole time and no design has used it.
`title` is present on **384,967 of 384,983 gig-date observations (100.0%)**.
Sellers who use generative AI advertise it in the title, so the share of listings
marketing AI *is* a diffusion measure, taken from inside the market and dated
quarterly.

### 3.7.1 The measure and what it costs to build

Two series are built: `AI_GEN`, generative-specific (ChatGPT, GPT, Midjourney,
Stable Diffusion, DALL·E, LLM, prompt engineering, "AI-generated/voice/avatar",
Synthesia, ElevenLabs, HeyGen, Sora), and `AI_ANY`, which also catches the
pre-generative AI trade (chatbots, ML annotation). `AI_GEN` is the usable one
because its pre-2022 baseline is near zero.

Three false-positive guards were added by auditing flagged titles, not by
anticipation, and each matters:

1. **`.ai` is the Adobe Illustrator file extension.** "convert any file to vector
   ai, eps, svg" is a design gig. Before the guard this was the single largest
   source of pre-2022 hits and would have manufactured a flat AI baseline in the
   design category since 2019.
2. **"Synthesia" is both the AI-video platform and piano-tutorial software**,
   disambiguated on video/spokesperson versus piano/MIDI.
3. **"real human traffic" is bot-traffic language in the SEO trade**, not an
   anti-AI claim; and "humanize your brand with animation" (2018) is not one
   either.

The `<seller>:` prefix and the ` for $X on fiverr.com` suffix are stripped first,
or any seller with "ai" in the handle reads as an AI gig in every quarter since
2019.

**Realised precision floor:** across 2019–2021, before generative AI was
commercially available, `AI_GEN` flags **7 distinct titles in three years**, six
of which are genuine pre-generative AI work (Dialogflow chatbots, GPT-3, ML
annotation). The false-positive rate is ~0.02% of observations against a
post-2023 level 25–60× higher.

### 3.7.2 The diffusion curve, and it is sharp

| quarter | AI-branded share, all listings | share of *new* listings ever AI-branded |
|---|---:|---:|
| 2019Q1–2022Q2 | 0.01–0.03% | 0.00–0.40% |
| 2022Q3 | 0.04% | 0.34% |
| **2022Q4** (ChatGPT, 30 Nov) | **0.04%** | **0.50%** |
| **2023Q1** | **0.48%** | **5.98%** |
| 2023Q2 | 0.95% | 5.75% |
| 2023Q3 | 1.20% | 3.85% |
| 2024Q2 | 1.38% | 1.29% |
| 2026Q1 | 1.86% | — |

**The entry-cohort column is the cleaner series** — it is the AI intensity of the
*flow* of new listings, so it is not contaminated by the changing composition of
the stock. It moves **twelvefold in one quarter**, and that quarter is the first
full one after ChatGPT's release. Note the measure is biased *against* this
result: "ever AI-branded" gives early cohorts more quarters in which to be
flagged, so the pre-2023 baseline is if anything overstated.

### 3.7.3 Diffusion happened through entry, not conversion

Of the **11,425 listings observed in both 2022 and 2024** — the same gigs
throughout — only **22 (0.19%)** ever switched their title to advertise AI, and
**none dropped the label** once adopted. Incumbent sellers essentially did not
rebrand. The AI share of the market rose because **new AI listings arrived**, at
roughly 4–6% of each post-2023 entry cohort.

This is a competitive-structure fact in its own right, and it is the one the
project could not previously see: **generative AI entered this market on the
entry margin.** It also explains why every design that looked for AI effects
*within* incumbent listings found nothing — under gig fixed effects, an entrant
is invisible.

### 3.7.4 AI listings are not cheap, and they are not at the bottom

The commoditisation story says AI floods the cheap end. It did not.

| entry-price band | share of AI listings | share of non-AI listings |
|---|---:|---:|
| ≤$10 | 25.3% | 28.9% |
| $11–25 | 22.3% | 22.4% |
| $26–50 | 13.9% | 20.1% |
| $51–100 | **22.1%** | 16.1% |
| >$100 | **16.5%** | 12.4% |

Median AI listing **$30** against **$25** non-AI (2023Q1–2024Q4). AI listings are
*over*-represented in the top two price bands and under-represented in the middle.
Whatever generative AI did here, it did not arrive as a low-price flood — which
is consistent with §3.1's finding that the $5 tier had already emptied, and had
emptied before the technology existed.

Conditional on category and quarter, AI-branded listings none the less price
**−12.5% below** non-AI listings in the same cell (t −2.42; −11.1% on 2023Q1–2024Q4,
**−37.8%** on the thin 2025Q1–2026Q1 window, t −2.80), and the spread by category
is enormous:

| category | AI vs non-AI price | t |
|---|---:|---:|
| audio | **−60.8%** | −5.22 |
| writing | **−26.4%** | −2.85 |
| translation | −14.9% | −0.63 |
| coding | −12.4% | −1.80 |
| video | +9.5% | +0.47 |
| design | +10.3% | +0.68 |
| marketing | +87.4% | +1.70 |

**This is a selection fact, not a treatment effect, and it must not be read as
one.** It compares different listings, not the same listing before and after. The
within-gig version — the 61 adopters with usable price series — gives **−14.9%
(t −0.78)**: same sign, no significance, and far too few adopters to resolve
anything. The cross-sectional gap says *who* advertises AI (cheap voice cloning
and cheap copy, expensive marketing consulting), not what AI does to a price.

### 3.7.5 A product attribute that did not exist before 2023

Listings that explicitly sell **human** production — "no AI", "100% human",
"human written", "humanize AI content" — are **exactly zero in every quarter from
2019Q1 to 2023Q1**. The first appears in **2023Q2**, and the share reaches 0.15%
by 2024Q3.

This is the clearest single piece of evidence in the whole project that
generative AI changed this market: **it created a differentiation margin that had
no reason to exist before.** Sellers now find it worth paying title characters to
say what their work is *not*. Those listings price **−31.5%** below others in the
same category-quarter (t −2.37, 107 observations) — human-positioning is at
present a low-end defensive claim, not a premium, though on this sample size that
ordering is a description of 107 listings and not a robust result.

### 3.7.6 What this section does and does not establish

**Does:** generative AI diffused into this market on a well-dated schedule, and
the date is 2023Q1. It entered through new listings, not incumbent conversion. It
entered above the median price, not below it. It created an anti-AI segment from
nothing.

**Does not:** attribute any price or quantity movement to it. Nothing here is an
identified effect. The diffusion measure is also a measure of *marketing*, not of
production — a seller quietly using ChatGPT to write copy is invisible to it, and
that is very likely the larger group. The measure is therefore a **lower bound on
adoption and an upper bound on nothing.**

---

## 4. Attribution: nine designs run (1–8 and 10), nine failures, and what they establish

Nothing above is causally attributed to generative AI, because nothing can be.

**What "a design" means here.** Describing what happened is easy. Showing that
generative AI *caused* it requires a comparison — some group the technology
should have hit harder than another, or some date at which it should have
arrived. Each design below builds one such comparison and then tries to break it.
A design **fails** when a check fixed in advance shows the comparison would have
produced the same answer in a world with no AI in it: because the two groups were
already drifting apart beforehand, because a plain time trend explains the data
better, because an unrelated series (US consumer prices) fits just as well, or
because the test also fires on dates when nothing happened.

The nine failures are listed with what killed each, because the *pattern* of the
failures is itself the finding.

| # | design | step | killed by |
|---|---|---|---|
| 1 | category DiD, HIGH vs LOW exposure | 46 | parallel trends (6/16 pre-period coefficients significant) |
| 2 | trend horse race | 46 | HIGH × POST collapses −7.9% → −0.8% once HIGH × trend enters |
| 3 | CPI-U placebo | 46 | significant (−3.6%, t −2.93) — the design tracks any smooth series |
| 4 | synthetic control + in-space placebos | 48 | translation ranks **last of 7**; p-floor 1/7 = 0.143 by construction |
| 5 | within-category price-tier DiD | 49 | parallel trends (10/11 pre-period coefficients significant); wrong-signed anyway |
| 6 | gig-level continuous exposure (pre-registered) | 50 | trend horse race (sign flip) and CPI-U placebo (t −2.86) |
| 7 | recent-window category contrast, writing vs video | 53, 54 | category-level randomisation (ranks 4th of 21 pairs, p = 0.190) and no exposure gradient (ρ = +0.04 over 7 categories) |
| 8 | within-category cheap-tier erosion (Upwork's prediction) | 55 | searched break is 2020Q3, ChatGPT ranks 16th of 17; pre-AI placebo significant and opposite-signed (t +5.95) |
| 9 | *(reserved — niche-level AI penetration, pre-registered, not yet run)* | — | — |
| 10 | twenty named launches, monthly, per-tool target category | 58, 58b | price margin **valid and null** (2 of 20 clear, below the ~3 chance predicts; 7 confounded by pre-trends); demand margin **discarded** on a 75% placebo false-positive rate |

### 4.1 Why designs 1–4 could never have worked

They share one defect: **seven units.** With seven categories the smallest
attainable one-sided p-value is 1/7 = 0.143, so the test cannot reach 5% no
matter what the data say. That is a property of the design space, not of the
result.

### 4.2 Design 6 is the informative one

It was **pre-registered before any outcome was estimated**
(`plans/active/exposure-continuous-prereg.md`), with five gates whose failure
consequences were fixed in advance. Continuous text-derived exposure at the gig
level, external to our data, with category × quarter fixed effects absorbing
every platform-wide shock.

It is the **first design in the project to pass parallel trends** (Wald χ²(11) =
9.99, p = 0.53; 0 of 11 pre-period coefficients significant). It also passes the
not-a-price-proxy gate and the placebo window. **Three of the four ways the
previous designs died are ruled out.** The primary estimate is −0.168 (t −2.52)
on 121,414 observations, stable across the entire pre-registered robustness grid.

It dies on the fourth: `exposure × trend` is significant (t −2.54) and
`exposure × POST` **flips sign** once it enters, and the CPI-U placebo is
significant at t −2.86. The pre-registered descriptive fallback says the same
thing independently — decile changes run −13.3% to +3.5% with **no monotone
gradient**, and the *least*-exposed decile falls more than the most-exposed.

Three qualifications, so the failure is not overstated: the estimate was
underpowered against its own standard (|β| = 0.90× the realised MDE); the
composition gate failed on power, not sign (balanced-frame β = −0.202, *larger*,
losing significance only because n falls to 1,715 gigs); and the collapsed
difference series returns the opposite sign, which is itself a reason not to read
−0.168 as an effect.

### 4.3 What the failures jointly establish — and the timing falsification

**There is an exposure-correlated differential trend that predates ChatGPT, and
there is no break at ChatGPT.** Two independent pieces of §3 agree: the commodity
tier's steepest decline is 2021Q2 (§3.1), and the repricing break is 2021Q3
(§3.5). The structural transformation in this market was already underway before
generative AI was publicly available.

**Step 52 converts this from an absence of evidence into a falsification of
dates.** Every design before it tested a single *assumed* break at 2022Q4, on the
premise that ChatGPT is "the" generative-AI event. That premise is wrong on the
history: GPT-3's API beta is 2020-06, Jasper 2021-02, Copilot preview 2021-06,
GPT-3 GA 2021-11, DALL-E 2 2022-04, Midjourney and Stable Diffusion 2022-07/08.
So "no break at 2022Q4" was only ever a statement about one date. Step 52
**searches** the break across 15 candidate quarters instead.

The within-gig transaction proxy **peaks 2020Q3** and turns down from 2020Q4 —
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

Best trend break of 15: **2020Q4** (γ −0.0966/quarter, t −48.63). Best
level-shift break: 2020Q2, and it is **positive** (+49.7%) — the pandemic boom
beginning, not a decline. Where the AI milestones rank among the 15 candidates on
level-shift SSR:

| milestone | quarter | rank | t |
|---|---|---|---|
| GPT-3 API beta | 2020Q2 | 1/15 | +38.73 (wrong-signed) |
| Copilot preview | 2021Q2 | 5/15 | −17.27 |
| GPT-3 GA | 2021Q4 | 8/15 | −10.84 |
| GPT-4 | 2023Q1 | 9/15 | −10.53 |
| **ChatGPT** | **2022Q4** | **11/15** | −6.22 |
| DALL-E 2 | 2022Q2 | 14/15 | −3.52 |
| Midjourney + SD | 2022Q3 | **15/15** | **−0.09** |

**The three image-model dates and ChatGPT are the worst-fitting breaks in the
window.** The one AI milestone that fits is GPT-3's API beta, and it fits with
the wrong sign, because 2020Q2 is when the pandemic boom started.

Two things must not be over-claimed. The search covers 15 quarters with **no
multiple-testing correction**, so the winning t is inflated; and a searched break
lands at window edges when the series is humped, and this one is humped. The
defensible claim is the weaker one: **the proxy peaks 2020Q3 and declines
thereafter, so no AI milestone can have initiated the decline.** That is a
falsification of dates, not evidence for a cause.

Identification is stated rather than assumed. Review accrual falls as a gig ages,
and within a gig, age and calendar time move one-for-one, so under gig FE the
**linear** calendar trend is not separable from the ageing profile — the
age-period-cohort problem, which has no solution here. Age is absorbed as full
**age fixed effects** with no functional form imposed, so **non-linear** calendar
changes are identified off cohort spread. Only break locations and sizes are
reported; no trend is.

**In plain terms:** a gig collects fewer reviews as it gets older, and for any
one gig, getting older and the calendar advancing are the same thing. So a slow
market-wide decline cannot be told apart from ordinary ageing — and we do not
try. Only *bends* in the series are reported, never its slope. Bends survive
because gigs of many different ages coexist in every quarter.

### 4.3.1 The positive control — the timing machinery is not blind

The single strongest objection to §4.3 has always been available and has never
been answerable: **if your searched-break procedure never finds ChatGPT, maybe
your procedure cannot find anything.** A method that returns "no break at the AI
date" on every series it is pointed at is not evidence about AI; it is evidence
about the method.

Step 57 supplies the missing control. The **identical** search — same grid, same
level-and-slope break, same ranking on SSR — is run on the AI-diffusion series of
§3.7, a series that *must* break at the AI date if the machinery works at all.

| series | best break of the grid | where ChatGPT ranks | SSR spread |
|---|---|---|---|
| within-gig transaction proxy (§4.3) | 2020Q4 | **11 of 15** | — |
| cheap-end relative performance (§4.4.2) | 2020Q3 | **16 of 17** | 0.06% |
| **AI-branded share of new listings (§3.7)** | **2023Q1** | **1 of 19** | **227%** |
| AI-branded share of the standing stock | 2023Q2 | 4 of 19 | 399% |

On the entry series the **top four candidates of nineteen are 2023Q1, 2022Q4,
2023Q2 and 2022Q3** — every generative-AI milestone quarter, in a row, at the top.
The worst-fitting break is 2019Q4. And the SSR spread is **227% of the best fit**,
against **0.06%** for the cheap-end search in §4.4.2 — so where that break
location was correctly called weakly identified, this one is sharply identified.

**This changes the standing of the project's central negative result.** The claim
is no longer "we looked for AI and did not find it", which is compatible with a
blunt instrument. It is:

> The same procedure, on the same panel, over the same quarters, locates
> generative AI's arrival to the exact quarter when it is asked about a variable
> AI demonstrably moved — and locates the price, transaction and market-structure
> turns two and a half years earlier, in 2020Q3–2021Q4, when it is asked about
> those.

The instrument resolves the AI date to within one quarter. It is therefore not
the instrument's bluntness that keeps AI out of the pricing and structure
results. **AI is in this market, on a well-dated schedule, and the market's
pricing and competitive structure turned before it arrived.**

One thing this does *not* license. A positive control shows the procedure can
detect a break of the size and shape present in the diffusion series; it does not
show the procedure could detect an arbitrarily small break in the price series.
The power caveat of §4.5 stands unchanged, and the two statements are compatible:
the machinery is sharp, and the 2025–26 window is still too thin.

---

### 4.3.2 Design 10 — twenty named launches, monthly, and a placebo that splits the result in two

Steps 52, 55 and 57 *searched* for breaks and ranked the AI milestones by fit.
None of them compared before against after at a named launch date, and all three
ran quarterly. Design 10 (step 58) does both missing things, and adds a third:

- **Monthly.** `month` is on every row and no prior test used it. A quarterly
  test smears a launch across up to three months.
- **Twenty named launches**, dated by **public availability** rather than
  announcement — an announcement cannot change a gig.
- **Per-tool targeting.** Each launch is matched to the category it should hit
  (Copilot→coding, ElevenLabs→audio, Midjourney→design, ChatGPT→writing +
  translation, Runway/HeyGen/Veo→video, Suno→audio), with non-target categories
  as controls. This needs no exposure score at all.

Every estimate is gated on a pre-window placebo: the same contrast run on the
twelve months *before* the launch. Steps 52 and 55 established these series were
already bending from 2020Q3, so an unguarded post-launch difference is worthless.

#### The price result: the null survives its sharpest test

| verdict | n | launches |
|---|---:|---|
| **confounded** — pre-window also significant | 7 | all five image-model dates (DALL·E 2, Midjourney, Stable Diffusion, DALL·E 2 open, MJ v5), Copilot, GPT-4o |
| **null** | 11 | ElevenLabs, GPT-4, Runway Gen-2, HeyGen, Suno ×2, Claude 3.5 Sonnet, FLUX.1, Veo 2, GPT-3 GA, DeepSeek R1 |
| **clears the gate** | 2 | GPT-3 API (−3.3%), ChatGPT (−2.0%) |

**Two survivors is fewer than chance predicts.** Roughly 60 tests at 5% yield
about three by luck. And GPT-3's API date is 2020-06 — precisely the pandemic
inflection §4.3 already flagged as fitting with the wrong sign.

The image models are the cleanest illustration of the project's recurring
finding. Design prices fall **−4.5% to −5.1%** (t −4.9 to −5.6) at every image
date — and **every one has a larger pre-window effect** (t −5.3 to −7.1). Design
was already diverging downward before any image model shipped.

#### The demand result is discarded, and the placebo is why

The same design on review accrual returned **11 of 20 "significant"** where
chance predicts one, with incoherent signs: image tools raising design's accrual
(+5.4% to +9.6%) while text tools cut writing's (−6.7%, −9.0%). No account of AI
produces that pattern.

Step 58b runs the identical design on **twelve fake launches dated 2019-03 to
2020-02**, each given the same target categories a real launch used. No
generative-AI tool existed for any of them, so every hit is a false positive.

| outcome | placebo false-positive rate | nominal | verdict |
|---|---:|---:|---|
| **price** | **1 of 12 = 8%** | 5% | at size; the price result stands |
| **demand** | **9 of 12 = 75%** | 5% | **the design fires at arbitrary dates; discarded** |

The accrual margin is dominated by seasonality and by the platform-wide decline
already documented in §2, and the launch dates are incidental to both. **The
eleven demand results are not reported as findings anywhere in this document.**
The price margin, by contrast, is validated by the same test — which is what
makes its null worth something.

#### The premise failed, and that is the informative part

The first stage — does a launch move AI *adoption* in its own target category? —
**rejects the design's own targeting assumption.** ChatGPT produced no
differential adoption in writing or translation. AI branding rose platform-wide
and concentrated in **coding**, regardless of which tool had just launched.

This is exactly what §3.7.3 predicts: diffusion came through **entry**, not
through incumbent conversion in exposed categories. It is also the deepest
diagnosis yet of why designs 1–8 failed — they searched for AI's effect inside
the categories a crosswalk called exposed, and that is not where AI arrived.

One caveat on the first stage itself: it clusters on **seven categories**, the
same too-few-clusters defect that killed design 7 at step 54's gate A, so its
t-statistics are not trustworthy and only the direction is read. And because the
launches sit one to three months apart, each launch's pre-window contains other
launches — effects cannot be separated within the 2022–23 cluster, and no attempt
is made to.

---

### 4.4 The two designs that tested the 2025–26 window directly

§2.5.3 established that designs I1–I6 tested a window that mostly precedes the
period the operators describe. Designs 7 and 8 test the operators' own two
specific claims, on the recent frame, with the promotion rule fixed in advance:
**a result is reported as a finding only if it clears the full battery.**

#### 4.4.1 Fiverr's claim — "weakness in AI-exposed categories" (steps 53, 54)

The registered exposure arms cannot run on the recent frame: translation has 27
gigs with usable review counts and audio 47. Step 53 therefore substituted the
largest adequately-sized category on each side of the **same registered
ranking** — **writing** (exposed, 2nd of 7) vs **video** (unexposed, 6th of 7) —
a deviation declared before the outcome was seen.

The first pass looked like the first AI-consistent pattern in the project, a
monotone escalation in exactly the shape an accelerating effect predicts:

| frame | exposed × trend | t | per quarter |
|---|---|---|---|
| balanced, full 2019Q3–2024Q4 | −0.0077 | −3.20 | −0.8% |
| balanced, 2023Q1–2024Q4 | −0.0427 | −6.35 | −4.2% |
| recent, 2024Q3–2026Q1 | **−0.0700** | −1.50 | **−6.8%** |

It was recorded as a **lead, not a finding**, because designs I1–I6 all looked
like this at the same stage. Step 54 ran the battery. It survives two gates and
dies on the two that matter.

**Gate A — category-level randomisation inference. FAIL, and this is decisive.**
The treatment varies across exactly **two categories** while the SEs are
clustered on hundreds of gigs; the effective number of treated clusters is
**one**. In plain terms, the statistics behave as though there were hundreds of
independent observations when the comparison actually rests on one category being
set against one other category — so the confidence interval comes out far
narrower than the evidence supports. The honest test computes the identical contrast for all 21 category
pairs, more-exposed member coded as treated, and asks where writing–video ranks.
It does not rank first anywhere:

| frame | writing–video rank | randomisation p | pairs beating it |
|---|---|---|---|
| recent 2024Q3–2026Q1 | **4 of 21** | 0.190 | marketing/video, design/video, coding/video |
| balanced 2023Q1–2024Q4 | 5 of 21 | 0.238 | design/audio, writing/audio, design/video, marketing/audio |
| balanced full | 9 of 21 | 0.429 | — |

The three pairs that beat it in the recent frame are **all X/video**. The result
is a *video* result, not a *writing* result: video is the category everything
else falls faster than, and writing–video picks that up. Correlation between the
21 pair coefficients and the exposure gap they span is **−0.068** — zero.

**Gate B — seven-category exposure gradient. FAIL.** If AI is the mechanism the
differential should line up with exposure across all seven categories. Spearman ρ
against the pre-registered β, where ρ ≤ −0.786 is needed for p < 0.05 at n = 7:

| frame | ρ | note |
|---|---|---|
| recent 2024Q3–2026Q1 | **+0.036** | translation, the *most* exposed, has the most positive trend |
| balanced 2023Q1–2024Q4 | −0.250 | the two biggest fallers are writing (2nd) and design (5th) |
| balanced full | −0.143 | |
| balanced pre-AI 2019Q3–2021Q4 | +0.000 | |

**Gate C — pre-AI placebo window. PASS**, and this is genuinely new: writing ×
trend over 2019Q3–2021Q4 is **+0.0022 (t +0.34)**. Unlike designs I1–I6, this
particular differential is *not* pre-existing. It does not rescue the design,
because gates A and B say the differential is not ordered by exposure.

**Gate D — inference robustness. PASS on the balanced frame.** Wild cluster
bootstrap (999 reps, Rademacher, null imposed) gives p = 0.001 on 2023Q1–2024Q4
against the gig-clustered p < 0.001, and the collapsed two-step on
category-quarter means returns b −0.0341 (t −5.98) against −0.0325. The recent
frame is p = 0.140 either way.

**Gate E — selection and composition. PASS.** Re-estimated on gigs present in
both halves of each window: recent −0.0719 (t −1.72) against −0.0700; balanced
2023–24 −0.0308 (t −4.82) against −0.0325. Composition is not producing it.

**Verdict: not promoted.** The differential is real and it is not a pre-trend,
but it is not ordered by AI exposure, and it is not the largest such differential
even among these seven categories. Design 7 fails.

#### 4.4.2 Upwork's claim — erosion concentrated under $500 (step 55)

This is the best-designed AI test available on this data and it produced the
strongest AI-consistent result in the project. It still cannot be promoted, and
the reason it fails is the same reason everything else here fails.

**Why the design is better than I1–I7.** It is a *within-category* contrast, so
it needs neither the seven-category unit count (p-floor 0.143) nor a treatment
that varies across two categories (the Moulton problem that killed design 7).
Category × quarter FE absorb every category-wide shock, so it asks only whether
the **cheap end of a category** eroded faster than the **expensive end of the
same category in the same quarter**. Treatment is the gig's **first observed
basic price in the frame**, fixed and never updated, so within-window repricing
cannot move a gig between arms.

**The result on 2023Q1–2024Q4 is exactly what Upwork describes**, in all four
specifications and with a monotone dose response:

| specification | b | t | AI-consistent? |
|---|---:|---:|---|
| cheap (≤$10) × trend | −0.0137 | −3.15 | yes (negative) |
| cheap (≤$25) × trend | −0.0141 | −3.11 | yes |
| log entry price × trend | +0.0069 | +3.73 | yes (dearer does better) |
| ≤$10 vs >$100 only | −0.0258 | −2.98 | yes |

| entry-price band | trend vs >$100 | t |
|---|---:|---:|
| ≤$10 | **−0.0256** | −2.99 |
| $11–25 | −0.0165 | −1.82 |
| $26–50 | −0.0120 | −1.28 |
| $51–100 | −0.0074 | −0.72 |
| >$100 | 0 | (base) |

Monotone, correctly ordered, on 20,173 gigs. Nothing else in this project has
looked this clean.

**And then the guards fire.**

**The pre-AI placebo is significant and points the other way.** On 2019Q3–2021Q4
the cheap end did **better**, emphatically: cheap × trend **+0.0236 (t +5.95)**,
log entry price × trend **−0.0162 (t −12.49)**, ≤$10 vs >$100 **+0.0721
(t +12.30)**. So the 2023–24 result is not a cheap-end decline appearing out of
nowhere; it is the **reversal** of a large pre-existing cheap-end advantage. A
reversal is only AI evidence if it happens when AI arrived.

**The break was searched, and it is 2020Q3.** Fitting
`cheap × trend + cheap × max(t − τ, 0)` over 17 candidate quarters:

| τ | change at τ | t | SSR rank |
|---|---:|---:|---:|
| 2020Q3 | −0.0453 | −6.39 | **1 (best)** |
| 2020Q2 | −0.0510 | −6.21 | 2 |
| 2020Q4 | −0.0378 | −6.08 | 3 |
| 2021Q2 | −0.0270 | −5.33 | 5 |
| 2021Q3 | −0.0225 | −4.81 | 6 |
| **2022Q4 (ChatGPT)** | **−0.0106** | **−2.38** | **16 of 17** |
| 2024Q2 | −0.0406 | −2.64 | 17 |

**ChatGPT ranks 16th of 17.** The change coefficient gets monotonically larger
and more significant the *earlier* the break is placed — the signature of an
early, gradual bend, not a discrete event in late 2022.

**Two honesty notes on that search.** The SSR range across all 17 candidates is
0.06% (173,359 to 173,461), so the *location* is weakly identified and the
best-fitting τ sits at the window edge; and there is no multiple-testing
correction, so the winning t is inflated. What survives both caveats is the
ranking, and the ranking puts the AI date second-to-last.

**The recent frame does not continue the pattern.** On 2024Q3–2026Q1 all four
specifications are null (cheap × trend −0.0080, t −0.27; log price × trend
−0.0024, t −0.25) and the dose response is **non-monotone and positive**
(≤$10 +0.027, $26–50 +0.077). Per §4.5 this frame could not have detected an
effect of the 2023–24 size, so this is not evidence against Upwork — but it is
not the acceleration an AI story needs either.

**Verdict: not promoted.** The cheap end really did stop outperforming and start
underperforming, with a clean monotone gradient. It happened around **2020Q3**,
it is a reversal of a pre-existing advantage rather than a new decline, and the
ChatGPT date is nearly the worst explanation of it available. Design 8 fails on
timing — the same way §3.1 and §3.5 failed.

**This is the fourth series in this project whose break was searched rather than
assumed, and all four land in the same eighteen months:** transaction proxy
2020Q4, cheap-tier reversal 2020Q3, commodity tier 2021Q2, repricing 2021Q3. Two
external series that we did not date at all agree — Fiverr's buyer peak in 2021
and Ramp's marketplace-spend peak in 2021Q4. **Six series, none dated by us in
advance, all pointing at 2020Q3–2021Q4** — and generative AI was not in
commercial use in these categories in any of them.

### 4.5 The recent window is underpowered, so its nulls are not evidence of absence

This is the single most important qualification on §4.4 and it is stated before
any reader can mistake a thin frame for a clean null. The recent frame carries
**525 gigs** for design 7 and **2,537** for design 8, against 5,372 and 20,173 on
the balanced frame. Realised minimum detectable effects at 80% power and 5% size
(2.80 × se):

| design | recent se | recent MDE | observed | balanced-frame effect | balanced effect as × MDE |
|---|---:|---:|---:|---:|---:|
| 7, writing × trend | 0.0466 | 0.131 | −0.070 | −0.033 | **0.25×** |
| 8, cheap × trend | 0.0296 | 0.083 | −0.008 | −0.014 | **0.17×** |

**Read the last column.** If the effect measured on the balanced frame were
running unchanged through 2025–26, the recent frame could not detect it — it is
four to six times too small. **In plain terms: this window is not a clean bill of
health, it is a blurry photograph.** So the recent-frame results are **uninformative**
about effects of the magnitude this project has been measuring, and neither of
them should be quoted as showing that the operators are wrong.

What the recent frame *can* rule out is a **very large** differential — anything
above roughly 8–13% per quarter. Fiverr's and Upwork's own numbers are nowhere
near that: Upwork reports GSV −3.6% and clients −4% *annually*. **Their claims are
comfortably inside our confidence intervals.** We can neither confirm nor
contradict them, and saying so is the whole of the honest answer for 2025–26.

An uninformative null is not a null. This is the same standard step 46 applied to
itself and it is applied here for the same reason.

### 4.6 Rival explanations that this data cannot separate from AI

Post-pandemic normalisation (2020–21 was a freelance boom, and the buyer series
peaks exactly at its end); the 2022 rate shock and tech downturn; and Fiverr's own
strategy — Pro, subscriptions, ads, an explicit upmarket push — which predicts
*every* structural fact in §3 as well as an AI account does, and predicts the
2021 timing better.

---

## 5. What is not measurable on this data, at any effort

- **Entry and exit.** `n_404 = 0` across 509,339 captures: the crawl records no
  removals, so nothing here can be labelled entry or exit. This is the single
  largest gap for a competitive-structure question, because entry is how a
  commoditising shock usually shows up first.
- ~~**Realised order value.**~~ **Entry removed 2026-08-20 — it was wrong.**
  What buyers paid *is* recoverable, at order level and dated by order, from 2022
  onward, out of pages already on disk (§1.3). What genuinely is not measurable
  is the **pre-2022** realised-price history: the field does not exist in those
  captures, which is a limit of the source rather than of effort.
- **The 2025–26 period, at usable precision.** The balanced structure frame stops
  at 2024Q4, before the agentic period. A recent frame does reach 2026Q1, and two
  designs were run on it (§4.4), but it is four to six times too thin to detect
  effects of the size this project measures elsewhere (§4.5). This is now the
  **binding constraint on the whole question**, because it is the exact window
  both operators attribute to AI.
- **Which categories.** Fiverr publishes no category split, and the archive's
  category comparison is not identified (§4).
- **Sales.** `review_count` is a proxy.
- **Silent AI adoption.** §3.7 measures AI *marketing*, not AI *production*. A
  seller who quietly drafts copy with ChatGPT and does not say so is invisible,
  and is very likely the larger group. The diffusion series is a **lower bound on
  adoption**.

---

## 6. What would change the answer, in order of value

1. **Thicken the 2024Q3–2026Q1 frame with a live forward crawl.** Promoted to
   first place on 2026-08-19. This is no longer "extend the window" — the window
   exists and it is the one that matters (§2.5.3), but at 525 and 2,537 gigs it
   cannot detect the effects we measure elsewhere (§4.5). Roughly a **6× increase
   in recent-frame gigs** would bring its MDE down to the size of the balanced
   frame's estimates, at which point Fiverr's and Upwork's claims become testable
   rather than merely inside our intervals. Nothing else on this list changes the
   answer as much.
2. **Re-extract the order records, and test the display selection first**
   (new 2026-08-20). §1.3 shows that what buyers paid is sitting inside pages
   already on disk and has never been read. This costs compute and no crawling.
   The first task is **not** the index but the **selection test**: pages choose
   which reviews to show by relevance, so before any number is published it must
   be established that displayed orders are not selected on price. If they are
   not, this yields on the order of **10⁵ dated, priced transactions** from 2022
   — the first transaction-level data in the project, and a direct replacement
   for `review_count` as the sales proxy.
3. **O*NET task statements** in place of occupation titles. The current exposure
   measure is both thin (36.8% of gigs get a zero match) and selected (dropped
   gigs accrue 23.7% more pre-period than kept ones). This weakness was declared
   in the pre-registration *before* design 6 ran, precisely so it could not
   become a post-hoc excuse. It is the one input change that alters the treatment
   measure itself. Gate B of step 54 sharpens the case: the seven-category
   gradient is flat, and a measure this coarse is one reason why.
4. **A quarterly Fiverr revenue series** in `data/fiverr-inc-metrics.csv`, which
   currently has no revenue figure for 2026 at all. Marketplace revenue is
   −15.5% YoY (§2.5.2) and the file cannot show it.
5. **A collection design that records 404s** on a fixed schedule, with manifests
   not selected on survival. That is the only route to entry and exit, and hence
   to the part of competitive structure this data cannot see at all.
6. **Sub-category or gig-population data.** Seven categories caps inference at
   p = 0.143 by construction.

---

## 7. Reader's guide to which claims carry what weight

| claim | status |
|---|---|
| real listed prices +40.7% (±3.7%) over 2020Q1–2026Q1 | measured, published, frozen |
| buyers −36%, spend/buyer +79%, implied orders −18% | external company data + an identity; orders is an upper bound |
| what buyers paid is recoverable from the archive, 2022 onward | **measured** — dated order records with ids and paid bands sit in pages already collected (§1.3) |
| orders under $50 are 1.0% of all orders, against a listed median of $25–30 | **measured on a pilot sample** of 2,883 priced orders — a description of *displayed* orders until the relevance-selection test runs |
| a realised-price series over time, or before 2022 | **not measurable yet** — the field begins in 2022, ~13% of orders are recovered, and display is relevance-ranked |
| per-gig review accrual broke −13% to −43% at 2022Q4 in all seven categories | measured; direction externally corroborated |
| $5 tier 27.3% → 10.3%, steepest decline 2021Q2 | measured on a balanced panel, break searched |
| three-tier share 82% → 91%, ladder 4.06× → 3.80× | measured on a balanced panel |
| repricing 23.6% → 18.3%, entirely fewer increases; cuts flat | measured on a balanced panel, break searched |
| sales concentration flat among trading listings and trading sellers | measured; the apparent rise is 2024 dormancy at the trailing edge |
| dispersion U-shaped, trough mid-2023 | descriptive only |
| return to reputation rose post-2022 | **lead only** — balanced panel t 2.04, full frame t 0.79 |
| any of this was caused by generative AI | **not identified**; nine designs run, nine failures |
| no AI milestone initiated the transaction decline | **falsified in timing** — proxy peaks 2020Q3; ChatGPT and the image models are the worst-fitting of 15 candidate breaks |
| the 2025–26 decline concentrated in AI-exposed categories | **not reproduced** — writing–video ranks 4th of 21 category pairs, exposure gradient ρ = +0.04; and the frame is too thin to detect it either way (§4.5) |
| the cheap end stopped outperforming and began underperforming | **measured**, monotone dose response across five price bands — but the searched break is **2020Q3** and it is a reversal of a pre-existing advantage, not a new decline |
| the operators' AI attribution is wrong | **not claimed, and not supported** — their reported magnitudes sit comfortably inside our recent-frame confidence intervals |
| the price ordering was reshuffled | **rejected** — rank persistence rose |
| the market commoditised | **rejected in sign** on four of five margins |
| generative AI diffused into this market, dated 2023Q1 | **measured**, from gig titles; entry-cohort share 0.5% → 5.98% in one quarter, break ranks 1 of 19 |
| diffusion ran through entry, not incumbent conversion | **measured** — 22 of 11,425 continuously-observed listings ever relabelled |
| AI listings undercut the cheap end | **rejected** — AI median $30 vs $25, over-represented in the top two price bands |
| an explicitly anti-AI segment exists and is new | **measured** — exactly zero to 2023Q1, first appears 2023Q2 |
| AI-branded listings price −12.5% below others | **descriptive selection fact, not an effect** — cross-sectional; the within-gig version is 61 adopters, −14.9% (t −0.78) |
| the searched-break machinery is capable of finding AI | **demonstrated** — ChatGPT ranks 1 of 19 on the diffusion series, 11 of 15 and 16 of 17 on the outcome series |
| no named AI launch moves prices in the category it targets | **measured at monthly resolution** over 20 launches — 2 of 20 clear the pre-window gate, below the ~3 chance predicts; validated by a placebo at 8% against a nominal 5% |
| AI launches moved sales in their target categories | **discarded, not reported** — the same design has a **75%** false-positive rate on fake 2019 launch dates |
| each AI tool shows up in the category it targets | **rejected** — ChatGPT produced no differential adoption in writing; AI branding concentrated in coding regardless of tool |

---

## 8. Provenance

| element | script | output |
|---|---|---|
| price index, categories, bands | `code/21`, `code/23`, `code/30` | `data/pilot/paper-numbers.md` |
| reputation band | `code/27-reputation-band.py` | frozen numbers §2 |
| demand break by category | `code/46-balanced-demand.py` | `runs/phase0-demand.out` |
| Fiverr Inc. transactions | `code/47-fiverr-inc-external.py` | `runs/fvrr-external.out` |
| category attribution (synthetic control) | `code/48-category-impact.py` | `runs/category-impact.out` |
| price distribution, versioning, dispersion, concentration | `code/49-market-structure.py` | `runs/market-structure.out` |
| continuous-exposure design (pre-registered) | `code/50-continuous-exposure.py` | `runs/continuous-exposure.out` |
| repricing, mobility, seller concentration, reputation split | `code/51-seller-structure.py` | `runs/seller-structure.out` |
| searched break vs the AI timeline | `code/52-ai-timeline-break.py` | `runs/ai-timeline-break.out` |
| recent-window exposure contrast (the lead) | `code/53-recent-exposure.py` | `runs/recent-exposure.out` |
| promotion battery for the lead (gates A–E) | `code/54-recent-lead-battery.py` | `runs/recent-lead-battery.out` |
| cheap-tier erosion, Upwork's prediction | `code/55-low-tier-erosion.py` | `runs/low-tier-erosion.out` |
| AI diffusion measured from gig titles | `code/57-ai-diffusion-titles.py` | `runs/ai-diffusion-titles.out`, `data/pilot/ai-title-flags.csv` |
| named-launch event studies, monthly | `code/58-ai-launch-events.py` | `runs/ai-launch-events.out` |
| placebo launches (the design's own size check) | `code/58b-launch-placebo.py` | `runs/ai-launch-placebo.out` |
| order records recovered from stored pages | `code/59-review-order-audit.py` | `runs/review-order-audit.out` |
