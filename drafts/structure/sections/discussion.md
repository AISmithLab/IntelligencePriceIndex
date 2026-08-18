## 5. Discussion

### 5.1 What the market actually looks like

Put §3's five verdicts together and the composite is coherent, and it is not a
commoditised market. Over the generative-AI diffusion window this platform shows:

- **fewer, larger buyers** — active buyers −36% from peak while spend per buyer
  rose every year, from \$205 (2020) to \$368;
- **higher listed prices** — +40.7% real, with no category falling;
- **a hollowed-out commodity tier** — the \$5 tier down from 27.3% to 10.3% of
  listings, the \$100+ tier up from 15.6% to 22.4%, the median listing \$15 → \$30;
- **deeper product menus** — three-tier share 82% → 91%, with the seller's own
  premium/basic ladder compressing 4.06× → 3.80×;
- **no price war** — repricing down, and down entirely through fewer increases;
- **unchanged concentration** — flat among trading listings and trading sellers.

That is the signature of a market **repositioning upmarket**: shedding its
micro-task base, retaining and up-selling larger buyers, and differentiating
through packaging rather than competing through price. Whether one reads that as
sellers responding to AI by abandoning work AI does well, or as a platform
strategy pursued for its own reasons, the data are the same — which is the point
of §5.2.

### 5.2 Rival explanations we cannot separate from AI

The timing evidence in §4.5 does not merely fail to support an AI account; it
actively favours several rivals, and this paper cannot adjudicate between them.

- **Post-pandemic normalisation.** 2020–21 was a freelance boom. The buyer series
  peaks exactly at its end, and the commodity-tier decline is steepest in 2021Q2.
  A normalisation account predicts the observed dates better than an AI account
  does.
- **The 2022 rate shock and the tech downturn.** Marketing and design budgets are
  procyclical, and these are two of the platform's largest categories.
- **The platform's own strategy.** Pro, subscriptions, advertising, acquired
  services, and an explicit upmarket push. **This rival predicts every structural
  fact in §3 — hollowed cheap tier, deeper menus, upmarket buyer mix, higher
  listed prices — and predicts the 2021 timing better than AI does.** It is the
  hardest rival, and the archive cannot separate it from AI because both act on
  the whole platform at once, which is exactly what a category × quarter fixed
  effect absorbs.

A pattern that appears in every category, including the least AI-exposed, is what
a platform-wide shock looks like. The identification problem is not a technical
shortfall; it is that the treatment we care about and the rivals we must exclude
have the same footprint.

### 5.3 Why the negative result is worth reporting

Three specific reasons.

**The false positives were available and would have looked good.** Design I1
yields −7.9% with t = −4.14 on a realised MDE meeting a stated precision
standard. Design I5's price variant yields a textbook event study — sign reversal
at exactly the treatment quarter, monotone afterwards, every coefficient
significant — and is mean reversion. On this class of data, an analyst who stops
at the first well-shaped result will find one.

**The failure is diagnostic rather than uninformative.** Design I6 passes
parallel trends, the not-a-price-proxy gate and the placebo window, and fails on
a trend horse race and a price-index placebo. That combination localises the
problem: an exposure-correlated differential trend that predates the event. That
is a claim about the world, not about our estimator.

**The p-floor is a design fact worth publishing.** Seven categories cap the
attainable one-sided p-value at 0.143. Any category-level study of AI exposure on
a platform with a handful of categories inherits that ceiling regardless of
sample size within categories, and no amount of additional listings fixes it.

### 5.4 What would change the answer

In order of value.

1. **Task-level exposure text.** Occupation *titles* are a few words long, which
   is why 36.8% of listings match nothing and why the automated ranking puts
   marketing above translation. Task statements would plausibly push coverage
   well above 63% and would change the treatment measure itself. This weakness
   was declared in the pre-registration *before* design I6 ran, so that if the
   design failed, "the mapping was thin" would be a stated prior weakness rather
   than a post-hoc excuse [CITE-prereg].
2. **Coverage past 2024Q4.** The structural window ends eight quarters after the
   break and before the 2025–26 agentic period, which is where the largest
   capability change has occurred.
3. **A collection design that records 404s** on a fixed schedule, with manifests
   not selected on survival. This is the only route to entry and exit — the
   margin where a commoditising shock would appear first, and the one this data
   cannot see at all.
4. **Sub-category or population-level data**, to escape the seven-unit p-floor.

### 5.5 Limitations

Beyond the measurement limits in §2.6: this is one platform, and platform
strategy is a confound rather than a nuisance (§5.2); listed prices are not
realised prices, so quantity declines derived from them are upper bounds; review
counts proxy sales; the descriptive claims in §3 are read off quota-sampled
cross-sections, which is why every one of them is stated on a fixed or balanced
panel with both columns printed; and the structural claims are pre-registered
only in the weak sense that they were locked after being generated and before any
further specification search [CITE-lock] — they are descriptions, not tests.
