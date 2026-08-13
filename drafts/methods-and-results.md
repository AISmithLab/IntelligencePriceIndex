# How We Collected the Data, and What We Found

**A plain walkthrough.** This document explains the whole project in ordinary language: what we
were trying to measure, exactly how the data was gathered, every problem we ran into and what
we changed in response, and what the results say.

**This is not the paper.** The paper is `drafts/sections/method.md` (the formal methods) and
`drafts/sections/findings.md` (the formal results). This file explains the same work without
the compression a journal demands. Where a number differs, the paper wins — it is governed by
a frozen table (`data/pilot/paper-numbers.md`) and this file is not.

---

## Part 1 — What we are measuring, and why it is hard

We want to know what it costs to buy a piece of thinking work — a written article, a logo, a
translation, a few hundred lines of code — and whether that cost changed as AI got better at
doing it.

To answer that you need **real posted prices, for specific tasks, over many years**.

We get them from **Fiverr**, where freelancers advertise fixed jobs called *gigs* at a listed
price: "I will write a 1000-word blog post — $25." The price is printed on the page. Nobody
had to be surveyed.

Fiverr only shows *today's* prices, so to see the past we use the **Wayback Machine**, the
Internet Archive's project that periodically saves copies of web pages. It has been saving
Fiverr since 2011. Each saved copy is a **snapshot**: what one gig's page looked like on one
day, including its price.

**The core idea is simple.** Find the same gig at two different dates. Compare its price to
*its own* earlier price. Repeat over thousands of gigs.

Why compare a gig only to itself? Because everything else about it then cancels out — how
skilled the seller is, how hard the task is, how much is bundled into the price. None of that
has to be measured, which matters enormously, because **none of it can be measured from an
archived web page.**

### Three words used throughout

| Word | Meaning |
|---|---|
| **Gig** | One freelancer's fixed-price offer. |
| **Snapshot** | One archived copy of that gig's page, on one day, showing its price. |
| **Matched gig** | A gig we can see in *both* of the two quarters being compared. This is the unit that determines how good our numbers are — not the total number of gigs. |

---

## Part 2 — How the data was collected, in six steps

### Step 0: Pick the source (before writing any collection code)

We set three pass/fail tests in advance and tried them on 20 pages:

| Test | Threshold | Result |
|---|---|---|
| Enough history? | ≥10 snapshots over ≥3 years, in ≥3 categories | Writing and programming each returned 50+ snapshots spanning 2012–2025 |
| Can we read a price? | ≥80% of pages | **20 of 20** |
| Can we follow a seller over time? | ≥5 sellers at ≥3 dates | 6 found |

We also checked two rivals and rejected both: **Upwork** negotiates prices privately, so the
archived page often has no price at all; **Freelancer.com** is barely archived.

### Step 1: Download the catalogue, not the pages

Then we hit the size problem. The archive holds **1,778,505 distinct gig pages** and about
**22.7 million snapshots** of them — roughly **12 TB** if downloaded. Too much to store, and
too much to politely ask the Internet Archive for.

So we split the job in two. The Internet Archive publishes a **catalogue**: a plain list of
every page it has saved and when, *without* the pages themselves. We downloaded the entire
catalogue first — **60 million rows** — and only then decided what to fetch.

**This ordering is the single most important design decision in the project.** It means our
sample was chosen against a complete inventory of what exists, rather than against whatever a
crawler happened to grab before we ran out of disk.

### Step 2: Choose the sample offline

From the catalogue, working entirely on our own machine:

- Keep things that look like gig pages (a two-part web address, page saved successfully).
- Collapse repeat saves of the same page on the same day.
- Find sellers with at least one gig saved **≥5 times over ≥2 years** → **48,643 sellers qualify**.
- Draw **500 of them at random**.

**Why sellers and not gigs?** Picking gigs directly would have covered more of the marketplace
for the same download budget. Picking sellers lets us follow one person's whole shop over
years, which some later analysis needs. We chose sellers deliberately, and it cost us breadth.

### Step 3: Download only those pages

That gave a shopping list of **26,603 pages**. We downloaded them politely, a few per second,
and got **22,632**.

### Step 4: Read the price off each page

Fiverr's page design changed twice over fifteen years, so the price reader tries four methods
in order of reliability, falling through only when one finds nothing:

| Method | Era | Share of pages |
|---|---|---:|
| Embedded `packageList` JSON | 2020+ | 72.9% |
| Old-style JSON | pre-2017 | 15.2% |
| HTML price tag | 2018–2020 | 0.7% |
| Any `$X` in the page text | all | 11.2% |

We read a price off **100%** of downloaded pages.

### Step 5: Build the panel

Collapse to unique gigs (**1,908**), take one median price per gig per quarter, then keep only
gigs seen in **≥2 different quarters** — because a single sighting tells you nothing about a
price *change*.

**Result: 1,066 usable gigs.**

### Step 6: A second crawl, because the first could not see recent years

Sellers chosen for having *long* histories turn out to be exactly the sellers whose pages stop
being saved near the end — an old shop still listed is not a busy one. So the first crawl
cannot measure 2025–2026 at all.

We ran a second crawl with a different rule, aimed at **2024Q3–2026Q1**: **2,908 usable gigs**,
far denser than the first crawl achieves anywhere.

The two are kept separate, estimated separately, and joined at **2024Q3**, the first quarter
they share.

### The funnel, in one line

> 60M catalogue rows → 22.7M unique page-months → 48,643 qualifying sellers → **500 sellers** →
> 26,603 pages requested → 22,632 downloaded → 1,908 gigs → **1,066 usable gigs** (+2,908 from
> the second crawl)

That drop — from 1.8 million gigs in the archive to about a thousand we can actually use — is
the honest shape of this kind of research. The Wayback Machine saves pages when it happens to,
not on a schedule designed for us. **Most gigs were photographed once and never again.**

---

## Part 3 — One real gig, start to finish

Here is an actual gig from the data:

**`nickkonstan/transcribe-your-favorite-track-to-midi-data`** — *"I will transcribe your
favorite track to MIDI."*

The Wayback Machine saved this page many times — in the third quarter of 2018 alone there are
**66 separate captures**, all showing $20. We collapse each quarter to a single median price,
which gives this gig's own price history:

| Quarter | 2020Q1 | 2020Q3 | 2021Q3 | 2021Q4 | 2022Q1 | 2023Q2 | 2024Q1 | 2024Q4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Price | $10 | $5 | $10 | $20 | $40 | $80 | $60 | $80 |

**This is the raw material of the index.** Not "audio work costs $X" — but *this specific gig
went from $10 to $80*. We never compare it to any other gig, so we never need to know whether
this seller is good or whether MIDI transcription is hard.

---

## Part 4 — How gigs become an index number

Take one pair of quarters. Find every gig priced in **both**. Compute each gig's own ratio.
Take the geometric mean.

Run on the real recent panel, 2024Q3 → 2024Q4:

- **1,132 gigs** appear in both quarters
- **95 raised** their price, **61 cut** it, **976 left it unchanged**
- The index for that quarter = **+0.83%**

Two things worth noticing. First, **most gigs do not change price in a given quarter** — the
index moves because a minority re-price. Second, that is *one* comparison; the full estimator
(**GEKS-Jevons**) does this for every pair of quarters and averages across routes, so all the
quarters are mutually consistent.

**Why not just chain the quarters together?** Because archived captures are irregular. A gig
often vanishes for several quarters and reappears. Chaining would book a three-year price
change as if it happened in one quarter, and those errors compound. Chained, this data reads
**+283%**; done properly it reads **+78.4%**.

---

## Part 5 — Every problem we hit, and what we changed

**None of these changes were planned.** Each was forced by something the data revealed, which
is why we report the sequence rather than presenting the final pipeline as if we designed it
that way from the start.

| # | The problem | What we changed | Did it work? |
|---|---|---|---|
| 1 | Archive far too big to download (1.78M gigs, ~12 TB) | Download the catalogue first; fetch only what an offline shortlist names | **Yes.** Sample drawn against a full census, and the shortlist is a file others can re-use |
| 2 | Our first rule picked sellers whose pages the archive saved *most often* | Switched to: qualify on having a long history, then draw at random | **Yes.** The old rule measured how interesting a page was to a crawler, not how useful it is to us |
| 3 | The first crawl goes quiet after 2024 and cannot measure recent years | Added a second crawl aimed at 2024Q3–2026Q1 | **Yes** — and it is why the project has two datasets joined at 2024Q3 |
| 4 | Four quarters in 2017–2018 contain **no saved pages at all** | Nothing. The window simply starts later | **No — this is a permanent loss.** Nothing can bridge the gap, so everything before 2018Q3 is unusable |
| 5 | Downloading at 20 pages/sec failed **45%** of requests | Slowed to 10/sec | **Yes.** Zero failures, at the same actual speed. The fast setting bought nothing |
| 6 | 93 GB of saved pages on disk | Compressed them | **Yes.** 5× smaller — 93 GB → 17.6 GB |
| 7 | Some Fiverr *directory* pages look like gig pages | Exclude them by web address | **Yes, and this one mattered most — see below** |
| 8 | We were counting the wrong thing (total gigs, not matched gigs) | Ran two much larger collections to test it | **Partly — see Part 7** |

### The one that changed a published result

Fiverr has its own directory pages (`/hire/design`, `/agencies/somename`) whose web addresses
look exactly like a gig's. Our price reader found no real price on them, so it fell back to
grabbing the first dollar amount on the page — which happened to be **the default setting of a
budget slider**.

When Fiverr changed that default from $1,000 to $500 in early 2025, it looked to us like every
category had suddenly halved in price.

**We had published that as a real finding: a −21% fall in the price of cognitive labor in
2025. It was not real. We retracted it.** Removing those pages cost 10.2% of our observations.

The part worth carrying forward is *how it was caught*: it survived every check we had until we
looked at the table showing **which price-reading method fired how often**. A "100% success
rate" showed nothing wrong. That is why we now report method shares, not just success rates.

### The rate lesson, which cost nothing but was luck

Running at 20 requests/second, we logged **12,336 failures against 15,150 successes**. We
survived it only because failed requests are simply retried rather than recorded as lost. Only
**3** of ~38,000 responses were blocks, so we were never banned — we were just running well
past the point of diminishing returns, and did not know until we measured it.

### Three problems no change can fix

- **We cannot tell when a gig dies.** When a page is delisted, the archive just stops saving
  it; it does not record a death. A takedown and a lapse in crawling look identical. Across
  509,339 captures we found **zero** "page gone" records.
- **The recent edge is closed.** Saved pages fall from 280,779 in September 2024 to **66** in
  March 2026. Re-harvesting recovers nothing new.
- **Nothing before 2018Q3 is reachable**, per problem 4 above.

---

## Part 6 — What we found

All figures cover **2020Q1 to 2026Q1**. "Real" means after subtracting general inflation.

### The headline

| | Change |
|---|---:|
| Composite index, nominal | **+78.4%** |
| US consumer inflation (CPI-U) over the same period | +26.8% |
| **Composite index, real** | **+40.7%** (±3.7%) |

**The posted price of cognitive labor on Fiverr rose substantially in real terms.** It did not
fall — which is what a simple "AI is destroying these prices" story would predict.

About **48%** of the nominal rise is just general inflation, which is why we report real terms
as the headline.

### By category

| Category | Real change | Margin of error | Meets our ±5% standard? |
|---|---:|---:|:--:|
| **Composite** | **+40.7%** | ±3.7% | **yes** |
| Design | +23.2% | ±4.8% | **yes** |
| Marketing | +132.1% | ±7.7% | no |
| Writing | +59.2% | ±8.3% | no |
| Video | +109.5% | ±11.9% | no |
| Audio | +154.2% | ±13.9% | no |
| Coding | +97.3% | ±17.1% | no |
| Translation | +136.3% | ±29.2% | no |

### Three things you must know to read that table

**1. Design is 70.6% of the composite.** The composite is, to a first approximation, a design
index with six minority components. It passes the precision standard *because design passes* —
not because seven categories averaged out into something well measured.

**2. Only design meets the standard.** The other six carry a direction and a rough magnitude,
never a precise rate and never a ranking. A wide margin of error does not mean the number is
*wrong* — it means we cannot pin it down tightly.

**3. Part of the rise is reputation, not price.** A gig's price rises partly because it
accumulates reviews and can charge more — the seller's career progressing, not the service
getting dearer. Adjusting for that takes the composite from **+79.0% down to +39.7%**. The
truth is somewhere in that band, and we publish both ends rather than picking one.

### The honest one-sentence version

> The posted price of cognitive labor on Fiverr rose substantially in real terms from 2020 to
> 2026 — but a large share of that rise is general inflation and seller reputation rather than
> the price of the service itself, and only one of seven categories is measured precisely
> enough to quote a firm rate.

---

## Part 7 — What we still cannot do

**Some historical numbers are not just imprecise — they are not pinned down at all.** For
coding, translation and audio in the earlier period, the estimate swings wildly depending on
settings that should not matter: coding's level moves from 312.8 to 717.7 on a single
one-step change to a robustness threshold. Where that happens, **we refuse to quote the
number**. It is marked "not identified" and never appears as a point estimate.

**We cannot yet separate incumbent price growth from service price growth.** The index follows
gigs that already exist and are ageing. If brand-new gigs keep entering at the same price while
established ones climb, we are partly measuring careers rather than the market. This is the
biggest open problem in the project.

**Bigger samples helped less than expected — and taught us the real lesson.** We ran two much
larger collections to test this:

| Collection | How it sampled | Size gain | Accuracy gain |
|---|---|---|---|
| Expanded recent | more **gigs** | 8.6× bigger | **1.2–2.0×** — almost nothing |
| Balanced historical | filled a quota for **each pair of neighbouring quarters** | 37× bigger | **32–112×** — margins of error cut 3–7× |

**Collecting more gigs did almost nothing; collecting gigs that bridge specific quarter
comparisons did a great deal.** That is the design rule for any future collection: target the
comparisons, not the gigs.

One ceiling is confirmed permanent: coding would need roughly **7,400** matched gigs per
comparison to hit our standard, and the entire archive can supply at most **6,142**. No
collection from this source will ever measure coding precisely enough.

---

## Where everything lives

| What you want | File |
|---|---|
| The formal methods section | `drafts/sections/method.md` |
| The formal results | `drafts/sections/findings.md` |
| Estimation diagnostics and full tables | `drafts/sections/appendix-a.md` |
| Every collection parameter, for replication | `drafts/data-collection.md` |
| The enlarged-collection analysis | `drafts/sections/results.md` |
| The frozen figures every section must match | `data/pilot/paper-numbers.md` |
