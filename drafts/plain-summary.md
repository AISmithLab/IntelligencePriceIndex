# What we collected, and what we found — the plain-language summary

**Written 2026-08-20.** This is a non-technical companion to
`drafts/market-structure-answer.md`. Same data, same findings, no econometrics
vocabulary. Where a number appears here it is the same number as in the full
document; nothing is rounded differently or restated more strongly.

**The question the project is trying to answer:** when generative AI arrived,
what happened to prices and to business in an online freelance market?

---

## The short version

Between 2020 and 2026, on Fiverr:

- **Prices went up.** Not down. About **+41% after inflation**, and up in every
  one of the seven categories we measure.
- **Business went down.** Fiverr's own buyer count is **−36%** from its 2021
  peak, and per-gig sales activity fell in every category.
- **The market went upmarket.** Fewer buyers, each spending more, on
  higher-priced work. The $5 tier emptied out.
- **Generative AI is definitely here.** We can see it inside the market and date
  its arrival to **early 2023**, sharply.
- **But the price and business turns happened in late 2020 and 2021** — one to
  two years *before* the AI tools existed commercially. And when we test the
  twenty actual product launch dates one by one, nothing happens at them.

So: prices up, transactions down, both true — and neither one is timed to AI.

---

## Six words that get mixed up

Most of the confusion about this market comes from four different quantities
being called "sales." They are not the same number and they do not move
together — the whole "fewer, larger buyers" finding is a gap *between* two of
them.

| word | what it counts | is it published? |
|---|---|---|
| **buyers** | *people* — accounts that bought at least once in the past year | yes, by Fiverr |
| **orders** (= transactions) | *purchases* — how many times somebody bought something | **no. Nobody publishes this. We estimate it** |
| **GMV** | *dollars transacted* — every order added up at what the buyer paid | yes, by Fiverr |
| **revenue** | *Fiverr's cut* of those dollars, roughly a third of GMV | yes, by Fiverr |
| **review accrual** | how many new reviews a gig collects in a quarter — our stand-in for its sales | no; we measure it from the archive |
| **listed vs realised price** | what a seller *advertises* vs what a buyer *actually paid* | neither; we measure the first, and recovered the second last week |

Two consequences worth holding on to:

- **GMV = buyers x spend per buyer.** That is arithmetic, not an estimate. It is
  why a third of the buyers can leave while the dollars barely move.
- **Nobody reports an order count**, so every statement in this document about
  transactions falling comes from one of two *derived* things: GMV divided by a
  price, or review accrual. Both are proxies, and §1.4 and §2.2 say what each
  one gets wrong.

---

## About the way you summarised it

You said: *prices rose during AI launches but transactions decreased.*

**Both directions are right.** Prices rose, transactions fell, and both happened
across the years when the AI tools were launching. If you had only those two
facts, "AI did this" is the natural conclusion — and it is the conclusion most
press coverage draws.

**The word doing the work is "during," and that is the one part the data
contradict.** Two things are true at once:

1. Over the whole AI period, prices are up and transactions are down.
2. The *turning points* in both series are dated to **2020Q3–2021Q4** — before
   ChatGPT, before Midjourney, before Copilot shipped.

A decline that was already underway continued through the AI years. That is not
the same as a decline that began with them. Everything below is essentially the
project's attempt to tell those two stories apart, and the reason it has taken
so many steps is that from a distance they look identical.

---

## Part 1 — What data we collected

### 1.1 The main source: the Internet Archive

Fiverr does not publish price history. The Wayback Machine has been
photographing Fiverr gig pages since 2017, so the history exists as saved web
pages, and we reconstructed it from those.

| stage | scale |
|---|---|
| raw archive index rows scanned | **60.0 million** |
| page captures identified in our window | **509,339** |
| distinct gigs available in the recent window | **91,849** |
| gig pages downloaded and parsed | **~375,000** |
| stored HTML on disk | **86 GB** |
| gig-date observations in the working dataset | **384,983** |

From each saved page we read the seller's advertised prices (basic, standard and
premium package), the gig title, the star rating, and the number of reviews.

### 1.2 The three datasets we built out of it

| dataset | what it is | period |
|---|---|---|
| **the price index panel** | 2,908 gigs tracked continuously enough to compare a price against its own earlier price | 2020Q1–2026Q1 |
| **the balanced frame** | 37,888 listings, 257,208 listing-quarter observations, a fixed set present throughout | 2019Q3–2024Q4 |
| **the recent frame** | the live trailing edge, much thinner | 2024Q3–2026Q1 |

The reason for the fussiness: if you just average all prices each quarter, you
are partly measuring **which gigs happen to exist**, not what prices did. So
every price comparison in this project compares a listing **against itself at an
earlier date**, and every claim about change over time uses a fixed set of
listings.

### 1.3 Outside data we brought in

- **Fiverr Inc.'s own reported numbers** (it is a public company, NYSE: FVRR) —
  buyer counts, spend per buyer, revenue, 2017 through mid-2026.
- **CPI-U**, US consumer inflation, so we can say what happened to prices in real
  terms rather than just in dollars.
- **An academic AI-exposure score** (Eloundou et al. 2023) rating how much of an
  occupation's work generative AI can do.
- **A third-party corporate spend panel** (Ramp) as an independent check on
  Fiverr's direction.
- **Twenty AI product launch dates**, each dated by when the tool actually became
  available to the public — not when it was announced. An announcement cannot
  change a gig.

### 1.4 The thing we found last week that we had been throwing away

Every archived gig page contains a hidden block of data behind the reviews. Each
displayed review is really an **order record**: an order ID, the **date of the
order**, and **the amount the buyer paid**, in a band.

Our extractor kept the advertised prices and discarded all of it, every time,
since 2019. It is still sitting in the 86 GB we already have, so recovering it
needs no new collection. From a 1,226-page pilot covering 2,883 priced orders:

| what the buyer paid | share of orders |
|---|---:|
| under $50 | **1.0%** |
| $50–200 | **67.3%** |
| over $200 | 31.7% |

The advertised entry price is typically **$25–30**. So buyers essentially never
buy the package our index prices — they buy up. This does not make the index
wrong (it measures what it says it measures: advertised entry prices), but it
does mean **"what things cost" and "what people spent" are two different series,
and we have only really measured the first one.**

This data starts in 2022, and we recover only about an eighth of orders, so it
cannot yet extend the long history.

---

## Part 2 — What we found

### 2.1 Prices rose. Substantially. In every category.

| | rise, 2020Q1 → 2026Q1 |
|---|---:|
| in dollars | **+78.4%** |
| after inflation | **+40.7%** |
| US consumer inflation over the same period, for comparison | +26.8% |

Every category rose. Design rose least (+23% real), audio most (+154%).

**Do not read the category ranking.** Six of the seven categories have error
bars wider than our own ±5% standard — translation's is ±29% on 28 gigs — and
the top three overlap completely. The *composite* is solid; the league table is
not.

What the rise is made of, as far as we can decompose it:

- **About half** is general inflation.
- **A large further part is reputation.** Within a single gig, price rises about
  **+7.7% each time its review count doubles.** A seller with more sales charges
  more. Strip that out and the real rise floors at about **+39.7%** on a raw
  ceiling of +79%.
- **The rest is unexplained**, and Part 3 is about why we cannot attribute it.

### 2.2 Business fell — and this is corroborated from outside the archive

Fiverr Inc.'s reported numbers. **GMV** is *gross merchandise value* — every
order added up at what the buyer paid. It is not Fiverr's revenue; Fiverr keeps
roughly a third of it. And note that the three columns are an identity rather
than three separate estimates: **buyers x spend per buyer = GMV**.

| year | buyers (M)<br>*people* | spend per buyer<br>*dollars each* | GMV ($M)<br>*total dollars transacted* |
|---|---:|---:|---:|
| 2020 | 3.40 | $205 | 699 |
| **2021** | **4.20 (peak)** | $242 | 1,020 |
| 2022 | 4.20 | $262 | 1,090 |
| 2023 | 4.10 | $278 | **1,140 (peak)** |
| 2024 | 3.60 | $302 | 1,087 |
| 2025 | 3.10 | $342 | 1,060 |
| 2026 (trailing 12m) | **2.70** | **$368** | 994 |

**Buyers are down 36% from the peak — that is 1.5 million people who used to
buy here and no longer do. Total money through the platform is down only
12.8%.** The entire difference is spend per buyer, which has risen *every
single year* since 2017, from $119 to $368.

That is the central fact about this market: **fewer buyers, each much larger.**

Divide those dollars by a price and you get an order count. It comes out at
**−18% against 2020, and −38.6% from the 2021 peak.** Treat that as an *upper
bound* on the decline rather than an estimate of it: the price we are dividing
by is the advertised entry package, and §1.4 shows buyers hardly ever pay it.
If what they really paid rose faster than the advertised price, the order count
fell by less than 18%.

Inside the archive, per-gig sales activity fell in every category at once:

| category | fall in review accrual |
|---|---:|
| writing | −42.9% |
| translation | −37.2% |
| **audio** | **−35.5%** |
| coding | −35.2% |
| **video** | **−28.6%** |
| marketing | −23.7% |
| design | −13.1% |

The two categories in bold are the two the AI-exposure score rates *least*
exposed. Audio is the least exposed of all seven and has the third-largest fall.
**Everything fell together, exposed or not** — which is what a platform-wide
shock looks like, not what a technology hitting specific kinds of work looks
like.

One important check: an alternative explanation for that table was that buyers
simply started leaving reviews less often, which would make sales *look* like
they fell when they hadn't. Fiverr's buyer and revenue numbers have nothing to
do with reviewing behaviour, and they fall too. So the direction is real.

### 2.3 The market restructured — but not the way anyone predicted

The standard prediction, if AI commoditises freelance work, has five parts. Four
are wrong in direction and the fifth is wrong in timing:

| prediction | what actually happened |
|---|---|
| prices fall | prices **rose 41%** |
| volumes rise as work gets cheap | buyers **−36%** |
| the cheap tier grows | the **$5 tier emptied**, 27.3% → 10.3% — *but its steepest drop is 2021Q2, and it slows down after ChatGPT* |
| sellers undercut each other | **price changes became rarer**, 23.6% → 18.3% of quarters, and the drop is **entirely fewer price increases** — actual price cuts are flat at 5–6% |
| the winners take everything | concentration **flat** (Gini 0.64 → 0.61), whether measured across listings or across sellers |

The last row is worth pausing on. "AI will let a few super-productive sellers
eat the market" is a common prediction. Sales are distributed almost exactly as
unequally in 2024 as in 2019.

### 2.4 Generative AI *is* in this market, and we can date it precisely

The earlier designs all guessed at AI's presence from outside — an occupation
score, or a release date. Then we noticed that gig **titles** were on 100% of our
observations and no analysis had ever used them. Sellers who use AI advertise it.
So the share of listings advertising AI is a measurement of AI's arrival taken
from *inside* the market.

| quarter | share of new listings advertising AI |
|---|---:|
| 2019Q1 – 2022Q2 | 0.0 – 0.4% |
| 2022Q4 (ChatGPT launches) | 0.5% |
| **2023Q1** | **5.98%** |
| 2023Q3 | 3.85% |

**Twelvefold in a single quarter**, in the first full quarter after ChatGPT.
There is no ambiguity about whether AI reached this market.

Three further things about *how* it arrived, none of which were expected:

1. **It came through new sellers, not existing ones.** Of 11,425 listings we
   watch continuously from 2022 to 2024, **22** ever changed their title to
   advertise AI. Twenty-two. AI entered as new listings by new entrants.
2. **It entered above the median price, not below it.** Median AI gig **$30** vs
   non-AI **$25**, and AI is over-represented in the top price bands. It did not
   arrive as a flood of cheap work.
3. **A new product category appeared: explicitly human work.** Listings selling
   "no AI" / "100% human" are **exactly zero** in every quarter through 2023Q1
   and appear from 2023Q2 onward.

### 2.5 The timing does not line up, and this is the crux

We took the six series in this project that turned at some point and asked, for
each, *which date fits the turn best?* — testing every candidate quarter rather
than assuming one.

| what turned | when it turned |
|---|---|
| per-gig transaction proxy | **2020Q4** |
| cheap-end performance | **2020Q3** |
| the $5 tier | **2021Q2** |
| how often sellers repriced | **2021Q3** |
| Fiverr's active buyers | **2021** |
| corporate spend share on the platform (external data) | **2021Q4** |

**All six fall in the same eighteen months, 2020Q3 – 2021Q4.** None of them was
dated by us in advance; each came out of a search. And generative AI was not in
commercial use in these categories in any of those quarters.

Ranked against the actual AI milestones, ChatGPT's quarter comes **11th out of
15** candidate dates for the transaction turn, and the image-model dates come
last. The only AI date that fits well is GPT-3's API beta in June 2020 — and it
fits with the *wrong sign*, because June 2020 is when the pandemic boom started.

### 2.6 The direct before-and-after test on twenty named launches

The above searches for turning points. The obvious complementary test is the
simple one: **take each real launch date and compare the months before with the
months after.**

We did that for 20 launches, month by month, matching each tool to the category
it should have hit (Copilot → coding, Midjourney → design, ChatGPT → writing and
translation, ElevenLabs and Suno → audio, and so on), using the other categories
as a comparison group.

Every result was checked against the **12 months before** the launch, when the
tool did not exist. If prices were already moving that way beforehand, the
post-launch movement is not the launch.

| result | how many of the 20 |
|---|---:|
| no effect at all | 11 |
| an effect — but the same or bigger effect was already there beforehand | 7 |
| survives the check | **2** |

**Two survivors is fewer than luck predicts.** About 60 statistical tests at the
usual threshold produce roughly three false positives by chance. And one of the
two is that same June 2020 pandemic date.

The image models are the clearest illustration. Design prices fall 4.5–5.1% at
*every* image-model launch date — which looks like a smoking gun until you see
that design prices were falling *faster* in the twelve months before each one.
Design was already sliding before image AI existed.

**One half of this test we ran and then threw away.** The same design applied to
sales volume lit up at 11 of 20 launches, with a nonsensical pattern — image
tools appearing to *increase* design orders while text tools cut writing's. So
we invented **12 fake launch dates in 2019**, before any of these tools existed,
and ran the identical test. It found "effects" at **9 of the 12 fake dates.**

| test | false-positive rate on fake dates | should be |
|---|---:|---:|
| prices | **8%** (1 of 12) | 5% |
| sales volume | **75%** (9 of 12) | 5% |

The sales-volume version fires at any date you hand it, so it measures nothing.
Those eleven results are not reported as findings anywhere. The price version
passes the same check, which is exactly why its null result is worth something.

### 2.7 Why this is not just "our method can't see anything"

This is the strongest objection to everything above, and for most of the
project's life we had no answer to it. If your test never finds AI, maybe your
test is broken.

So we pointed the identical procedure — same data, same quarters, same
machinery — at something AI demonstrably *did* change: the share of new listings
advertising AI.

| what we asked it about | where ChatGPT's quarter ranks |
|---|---|
| the transaction turn | 11th of 15 |
| the cheap-end turn | 16th of 17 |
| **AI's own diffusion** | **1st of 19** |

And the next three best-fitting dates after 2023Q1 are 2022Q4, 2023Q2 and
2022Q3 — the AI milestone quarters, consecutively, at the top.

**The instrument finds AI immediately when AI is actually there.** So its failure
to find AI in prices and market structure is a fact about this market, not a
defect in the method.

### 2.8 Why nine attempts at proving causation all failed — and what that taught us

Nine identification designs have been run — designs 1 through 8, and design 10
— and all nine failed. That sounds like incompetence until you see the
diagnosis, which only emerged at the end:

**Designs 1–8 all looked for AI's effect inside the categories that an external
"which jobs are exposed to AI" list said would be hit — and that is not where AI
arrived.** AI branding rose platform-wide and concentrated in **coding**,
regardless of which tool had just launched. ChatGPT produced no differential AI
adoption in writing or translation at all.

And because AI came in through *new listings* rather than existing ones, any
design that follows the same gigs over time is structurally blind to it: a new
entrant is invisible to a method built on within-gig comparison.

---

## Part 3 — What we cannot say

1. **We cannot say AI caused any of this.** Not "we found it isn't AI" — we
   found the timing is wrong for an AI story and we cannot identify a causal
   effect either way. Other things happened in these years: the pandemic hiring
   boom and its unwind, Fiverr's own push upmarket into business services, the
   2022 tech-sector contraction, changes in platform search ranking. Nothing in
   this data separates them from each other.
2. **All of the above ends at 2024Q4.** Both Fiverr and Upwork now blame AI for
   their declines explicitly, and they are describing **2025–26** — a period our
   data barely reaches. We ran two designs on that recent window and both failed,
   one of them because there simply isn't enough data yet. The recent window is
   **uninformative**, not null. This is a genuine open question, not a settled
   one.
3. **We measured advertised prices, not what people paid.** See 1.4. The order
   data exists, is 2022-onward, and hasn't been extracted yet.
4. **A null is not a zero.** We can rule out AI effects above a certain size. A
   small effect could hide underneath.
5. **We cannot see sellers leaving.** The archive stops re-requesting a deleted
   page rather than recording its death — zero 404s across 509,339 captures. Exit
   would need a live ongoing crawl.

---

## Part 4 — What would change the answer, in order of value

1. **Extend the data through 2025–26 with a live crawl.** This is the window
   where both platforms say AI is biting, and we're currently 4–6× too thin to
   test it. Nothing else on the agenda matters as much.
2. **Extract the order records.** First deliverable is not an index — it is a
   test of whether the reviews a page displays are selected on price. If they
   are, every "what buyers paid" number is biased and unusable. Only if that
   passes do we get real transaction prices.
3. **Rebuild the AI-exposure measure from richer occupation text.** The current
   one fails to match 36.7% of gigs and the misses are not random.
4. **Build AI penetration at the niche level** rather than across seven broad
   categories — which is what every failed design actually lacked.

---

## Where the numbers come from

Every figure above appears in `drafts/market-structure-answer.md` with its
source. Analysis scripts are in `code/`, numbered by step; outputs in `runs/`.
The price index numbers are frozen in `data/pilot/paper-numbers.md`, and a check
script enforces that no draft quotes anything else.

| finding here | full document | script |
|---|---|---|
| price level and decomposition | §1.1, §1.2 | `code/21`, `23`, `27`, `30` |
| what buyers actually paid | §1.3 | `code/59-review-order-audit.py` |
| Fiverr Inc. quantities | §2 | `code/47-fiverr-inc-external.py` |
| per-category demand falls | §2 | `code/46-balanced-demand.py` |
| market structure, five predictions | §3 | `code/49`, `code/51` |
| AI diffusion measured from titles | §3.7 | `code/57-ai-diffusion-titles.py` |
| the timing falsification | §4.3 | `code/52-ai-timeline-break.py` |
| the positive control | §4.3.1 | `code/57-ai-diffusion-titles.py` |
| twenty named launches | §4.3.2 | `code/58-ai-launch-events.py` |
| the fake-launch placebo | §4.3.2 | `code/58b-launch-placebo.py` |
