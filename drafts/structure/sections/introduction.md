## 1. Introduction

The standard prediction for what generative AI does to a market for routine
cognitive labour is a commoditisation story, and it is specific enough to test.
If a technology sharply lowers the cost of producing writing, translation,
graphic design or code, then in the market where that output is sold: prices
should fall, transacted quantities should rise, the low-price tier should widen
as marginal work becomes profitable, price competition should intensify as
sellers pass through their own cost reductions, and sales should concentrate on
whichever sellers adopt first.

This paper takes those five predictions to an online freelancer market across the
diffusion window, using the largest archival panel of listed service prices we
are aware of: **257,208 listing-quarter observations on 37,888 Fiverr listings
from 29,835 sellers, 2019Q3–2024Q4**, reconstructed from the Internet Archive,
joined to a matched-model price index that runs to 2026Q1 [CITE-ipi] and to the
platform operator's reported buyer and GMV series.

**Four of the five predictions are rejected in sign; the fifth is rejected on
timing.** §3 gives the descriptive record. What the data show instead is a market
moving upmarket: prices up, buyers fewer and larger, the commodity tier hollowed
out on a schedule that starts before generative AI was publicly available,
product menus deeper, no price war, and no change in who captures the sales.

The second half of the paper is a negative result reported as a result. §4
documents **six identification designs that all fail** to attribute the observed
change to AI exposure. They are not a catalogue of our mistakes; they are a map
of what archival marketplace data of this shape can and cannot support, and their
failures are structured. Four die on having only seven categories, which caps the
attainable one-sided p-value at 1/7 = 0.143 by construction. One dies on mean
reversion in a price-rank treatment proxy. The sixth — **pre-registered before
any outcome was estimated**, with five gates whose failure consequences were
fixed in advance — is the first to pass parallel trends, and dies on a trend
horse race in which the treatment interaction changes sign, and on a CPI-U
placebo significant at t = −2.86.

Their joint diagnosis is the paper's second contribution and is more useful than
another point estimate: **there is an exposure-correlated differential trend that
predates ChatGPT, and there is no break at ChatGPT.** Two independent descriptive
series agree — the commodity tier's steepest decline is 2021Q2 and the repricing
break is 2021Q3.

We make three contributions.

1. **A structural record.** Eight descriptive claims about the price
   distribution, product-line depth and seller repricing conduct across the
   diffusion window, each read off a balanced panel with searched rather than
   assumed break dates, and each pre-registered before further specification
   search [CITE-lock].
2. **Six rejected predictions, and six failed designs, reported in full** —
   including the pre-registration, the gate card, and the specifications that
   *would* have produced a publishable-looking AI effect had the gates not been
   committed in advance. One of them — a clean sign reversal at exactly
   2022Q3/Q4, monotone afterwards, every coefficient significant — is mean
   reversion.
3. **Design requirements.** The specific properties archival data must have for
   this question to be answerable: 404s recorded on a fixed schedule, manifests
   not selected on survival, and exposure measures built from task-level rather
   than title-level text.

**Scope.** This is one platform, listed prices rather than realised order value,
and a sales proxy rather than sales. §2 states each limit and §5 states which
rival explanations we cannot separate from AI. We claim a description of what
happened and a demonstration of what cannot be identified from it — not a causal
estimate of AI's effect, which we explicitly fail to produce.
