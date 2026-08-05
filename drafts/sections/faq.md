# FAQ & Methodology · Draft Section

**Target file:** `docs/faq.html`
**Status:** ⚠️ **OUT OF SYNC** — last mirrored 2026-07-12. The live `docs/faq.html` has since been revised
by the real-terms rollout (2026-07-30), the full FAQ audit (2026-07-30), and the non-gig-page exclusion
(2026-07-31). Treat `docs/faq.html` as authoritative until this mirror is rebuilt.
**Audience:** freelancers and buyers active on **Fiverr and Upwork**, plus researchers interested in AI's effect on the price of knowledge work.

This document holds the **full FAQ copy** as it appears on the live page. All questions are given
**in final reading order**. This revision **merged the earlier 21 questions into 15** (six overlapping
pairs were combined), rewrote every answer for informativeness under the project's style rules, and
corrected two stale points against current site state. `[NEW]` tags were dropped now that the whole
set is shipped.

Two facts that shape several answers below (per current site state):

- **All prices are extracted with the Wayback Machine**, crawling archived Fiverr gig pages back to **~2011**.
- **The chart plots the full quarterly series from 2020 Q1 to 2026 Q1**, **25 quarters**, with the index
  fixed at `100` in **2020 Q1**. Seven categories are shown (design, writing, marketing, coding, video, audio,
  translation). The pre-2020 archive exists but is too thin to chart, and categories may still expand.

Two corrections applied in this revision:

- The **composite headline number was dropped** from `index.html` and the chart defaults to a single
  category, so the old "what does the headline number mean?" answer was reframed around the per-category
  `Δ'20–'26` column and the composite shown when two or more categories are selected.
- At the time of that revision `docs/data.json` showed the composite at **317.7 (+217.7%)** on the chained
  series with **every category up** (+109% to +478%), so the earlier deflation-first framing was corrected
  to be direction-neutral. A **chain-drift** caveat was added to the limitations. *(Superseded: the chained
  series was retired on 2026-07-27 and the published index is now GEKS-Jevons, real by default — composite
  **+78.4% nominal / +40.7% real** as of 2026-07-31.)*

---

## Questions (final reading order)

### 1. What is the Intelligence Price Index?
The **Intelligence Price Index (IPI)** measures the **revealed price of knowledge work that generative AI
is increasingly able to perform**. It is a matched-model price index assembled from the posted prices of
freelance "gigs" on Fiverr, covering tasks such as logo design, copywriting, software work, voiceover,
translation, and video editing. The question behind it is what happens to the market price of a cognitive
task as machines become better at doing it. Instead of asking experts to score exposure or forecast
disruption, the IPI reads prices that sellers themselves set and adjust inside a competitive marketplace.
Its construction follows the logic of the Consumer Price Index (CPI), with the basket redefined from
household goods to units of cognitive labor.

### 2. Who is this for?
Two audiences make use of the index. Freelancers who sell standardized services, together with the buyers
who commission them, can see where the going rate for a given kind of task has moved. Researchers studying
how AI reshapes the labor market gain a task-level price series that conventional statistics rarely
provide. Someone who sells logo design, copywriting, coding, voiceover, translation, or video editing can
treat the relevant category as a gauge of where prices for that work have trended. For a buyer
commissioning the same tasks, the series indicates what a reasonable posted rate looks like at a given
time. All prices come from a single marketplace (Fiverr, described below), though the offerings themselves
are standard across both Fiverr and Upwork.

### 3. How do I read the index and the change column?
Every series is set to 100 in the base quarter, **2020 Q1**, so a level records the cumulative percentage change in a category's posted prices since then rather than a dollar amount. A reading of 130 places current list prices 30% above their 2020 level, and the **Δ'20–'26** column reports that figure for the latest quarter, largest movers first. The chart opens on a single category, since a composite of one line is uninformative; selecting further categories rebuilds the weighted composite and draws it alongside them.
What the levels track is the price of work that generative AI performs with increasing competence. In this pilot every category has risen, several to three or four times their 2020 level, so an AI effect is to be sought in the ordering rather than in the height of any one line. Translation, writing, and coding, the tasks language models address most directly, occupy the bottom of the change column, while audio, video, and marketing occupy the top. A category rising more slowly than its neighbours, or more slowly than prices in general, is where substitution is most plausible; a steep rise is more consistent with AI complementing the seller. The figures are nominal and the levels are chained, so consult inflation and limitations before drawing a conclusion from a single number.

### 4. What window does the chart cover, and can I see ChatGPT or COVID in it?
The series runs quarterly from **2020 Q1 to 2026 Q1**, twenty-five quarters in all, indexed to `100` at the
start. Archived prices reach back to roughly 2011, yet the chart begins in 2020 for two reasons. Coverage
before that year is sparse and irregular, with too few matched gigs per quarter to trace a stable line.
Opening in 2020 also fixes the baseline before generative AI came into wide use, since ChatGPT launched in
**November 2022**, while keeping the sample dense enough to trust. Quarterly buckets replace months because
each quarter pools more matched gigs, which steadies the series against the noise a monthly frequency would
introduce. Earlier history may be added as coverage improves.

Because the window straddles November 2022, the quarters on either side of that date are the natural place
to look for a substitution signal in exposed categories such as writing and design. Two confounders
complicate that reading. The opening quarters coincide with the COVID shock of 2020 and 2021, which moved
freelance demand for reasons unrelated to AI, so the earliest movements should not be taken as an AI story.
General inflation and the platform's own growth also press on posted prices across the whole window. The
index records how prices moved. It does not, on its own, establish why. Disentangling an AI effect from
these other forces is the task of the accompanying paper, and the relevant limitations appear below.

### 5. What is priced, and how are the categories chosen?
The unit of observation is a **gig**, meaning a single well-defined task offered at a posted price, for
instance "design a minimalist logo" or "translate 500 words from English to Spanish." Prices include the
**Basic** tier, the **Standard** tier, and the **Premium** tier. Because a gig denotes a standardized task,
its price can be followed across periods much as a CPI item is. Each observation, finally, counts only
against the same gig's own earlier price, which isolates genuine price movement from shifts in the mix of
sellers.

Seven categories are tracked at present: design, writing, marketing, coding, video, audio, and translation.
Each individual freelancer's subcategory is also graphed so its own price change can be observed over time.
A category qualifies on two grounds. Its work must recur as a standardized posted-price gig across many
sellers, so that individual gigs can be matched to their own histories. It must also be plausibly exposed
to generative AI, meaning something these models can increasingly do or assist with. Each gig is assigned to
a category from its archived page. Work that is largely manual, performed in person, or not cleanly packaged
as a fixed-price gig, such as data entry, virtual assistance, or general consulting, falls outside the
index, either because it resists standardized pricing or because its exposure to AI differs in kind. The set
is expected to expand and makes no claim that these seven exhaust the AI-exposed portion of knowledge work.

### 6. Where does the data come from?
Every price shown is an actual historical Fiverr list price, recovered from the Internet Archive's **Wayback
Machine**, the public web archive that has snapshotted Fiverr gig pages since roughly 2011. Nothing is
surveyed and nothing is imputed. The figures are simply those sellers posted, as preserved in archived
copies of their pages, aligned over time.

**From 60 million archived URLs to a clean price panel.** Reaching a usable series from the raw archive takes
several stages, each narrowing a large pile of entries toward gigs whose prices can be followed reliably:

| Stage | What happens | Result |
|---|---|---|
| CDX retrieval | Query the Wayback Machine's index for every archived `fiverr.com` gig URL. | 60M entries |
| Dedup & classify | Collapse to unique (URL, month) snapshots; tag each gig with a service category. | 22.7M unique |
| Longitudinal filter | Keep sellers with enough history (≥5 monthly snapshots spanning ≥2 years). | 48,643 sellers |
| Stratified sample | Draw a representative pilot sample of sellers and list their snapshots to download. | 500 sellers · 26,603 snapshots |
| Download | Fetch the archived HTML from the Wayback Machine (rate-limited, with retries). | 22,632 pages (85%) |
| Price extraction | Parse the Basic price out of each page (see below). | prices 2011 to 2026 |
| Matched panel | Keep only gigs seen in two or more periods, so each price change is measured against the same gig's own past. | matched gigs |

**How a price is read off each page.** Fiverr redesigned its pages repeatedly over the years, so extraction
proceeds through a cascade of four methods, attempting the most reliable first and falling back as needed:

| Method | Era | How the price is found | Share |
|---|---|---|---|
| `packageList` JSON | 2020+ | Embedded JSON array, price in cents | 72.9% |
| Old-style JSON | pre-2017 | JSON with price as a dollar string | 15.2% |
| Dollar fallback | all eras | `$X` pattern in the page text | 11.2% |
| HTML `<span>` | 2018 to 2020 | `class="price"` DOM element | 0.7% |

**What this site shows specifically.** The full study spans 2011 to 2026. The figures on this page draw on the
**full-history quarterly build** of that pipeline, aggregated into quarters and charted from 2020 Q1 to 2026
Q1 (twenty-five quarters). The `Gigs` column on the index page reports how many matched gigs sit behind each
category. Because the sample is pilot-scale, the limitations below should temper any strong reading of an
individual category.

### 7. Why revealed Fiverr prices rather than surveys or wage data?
Three alternatives suggest themselves, and each falls short for this purpose. Surveys record what
respondents *believe* prices are doing, a signal that recall, sentiment, and the composition of those who
answer can all colour. Posted prices carry none of that mediation. Official wage statistics, such as the BLS
series, are genuine measurements, but they arrive aggregated and lagged and do not resolve to the specific
AI-exposed gigs of interest. One cannot locate the price of "a minimalist logo" or "500 words from English
to Spanish" within them. Fiverr's packaged, posted prices supply exactly that: a **task-level list price
that can be matched to its own past**, quarter after quarter.

### 8. How is the index calculated?
A **matched-model index** assembled in three steps, following the approach the BLS applies to CPI items that
are difficult to quality-adjust. A fourth step turns the resulting level into the reported change. The
composite is recomputed live in the browser whenever the basket changes.

**Step 1 · Price relatives (same gig, period to period).** For every gig *i* seen in two consecutive
quarters, take the ratio of its later price to its earlier one:

```
r_{i,t} = p_{i,t} / p_{i,t−1}
```

Here p_{i,t} is the price of gig *i* in quarter *t*, taken as the median Basic price when a gig has several
snapshots that quarter. Ratios falling outside the band 0.1 to 10× are treated as data errors and discarded,
and a category-quarter enters only once at least 3 gigs are matched.

**Step 2 · Category index (Jevons, chained).** Within a category, that quarter's price relatives are combined
through a Jevons index, the geometric mean of the relatives, and chained onto the previous quarter's level:

```
I^c_t = I^c_{t−1} × ( ∏_{i ∈ S_{c,t}} r_{i,t} ) ^ ( 1 / |S_{c,t}| )
```

S_{c,t} denotes the set of gigs in category *c* matched between *t*−1 and *t*, and |S_{c,t}| its size.
Multiplying the relatives and raising the product to the power 1/n returns their geometric mean. The base
quarter (2020 Q1) is fixed at 100.

**Step 3 · Composite IPI (weighted geometric mean).** The category indices are combined into a single figure
by a Törnqvist-style weighted geometric mean:

```
IPI_t = exp( Σ_c w_c · ln I^c_t / Σ_c w_c )
```

Only the categories currently selected enter the sum, which is why the composite responds as the basket is
toggled.

**Step 4 · The reported change.** The change shown for a category is the percentage difference in its index
from the base quarter (2020 Q1, period 0) to the latest quarter *T*:

```
Δ'20–'26 = ( IPI_T / IPI_0 − 1 ) × 100%
```

The same expression yields the composite's Δ'20–'26 figure when the composite index is substituted for a
category's index.

### 9. Are these prices adjusted for inflation?
The index is stated in **nominal US dollars** and carries no inflation adjustment at present. It follows the
actual posted price of a gig over time, without deflating by CPI or any other measure. A reading above `100`
therefore does not by itself mean the work grew more expensive in real terms, since part of any increase
reflects economy-wide inflation over the same span. What speaks more directly to substitution by AI is a
fall in gig prices, or a rise slower than general prices, against an inflationary backdrop. A real,
inflation-adjusted version is planned. Until it exists, the reported change is best read as a **nominal**
figure, with the wider macroeconomic context kept in view.

### 10. How are the category weights set?
Weights are intended, in the manner of CPI expenditure weights, to reflect how much economic activity each
category carries. Transaction volume is proxied by **review counts**, on the premise that a gig accumulates
reviews roughly in proportion to its sales: `w_c = R_c / Σ R_k`, where `R_c = Σ_{i∈c} max_t reviews_{i,t}`.
In the present sample **design carries most of the basket**, near 71%, with writing next at about 11% and
marketing, coding, video, audio, and translation dividing the remainder.

### 11. Why geometric means, and can a few sellers distort the index?
The geometric mean is symmetric under reversal: a price that doubles and then halves returns to its starting
point, where an arithmetic mean of the relatives would record a spurious net rise. The Bureau of Labor
Statistics likewise uses it for elementary CPI aggregates, which keeps the IPI comparable with how headline
inflation is actually measured. That same construction limits how far a handful of sellers can move the
index. Since each gig is compared only with its own past, sellers entering or leaving the sample cannot by
themselves shift a level. The geometric mean then damps extreme ratios far more heavily than an arithmetic
mean would, and two guardrails discard relatives outside `0.1 to 10×` and require at least 3 matched gigs
before a category-quarter counts. No individual seller's price change moves a category by much, and
averaging across categories dilutes it further. The more serious threat is *thin coverage*, too few matched
pairs in a given cell, rather than manipulation by any one participant, and it is flagged in the limitations
below.

### 12. Can I toggle categories and inspect individual freelancers or gigs?
The composite is rebuilt in the browser from the category indices and their weights each time the basket
changes, applying the Step 3 formula above and renormalizing over whatever categories are selected. This
makes it possible to ask what the index looks like for, say, design and writing alone, without relying on a
server to recompute it. The checkboxes toggle categories, and the All / None links select or clear the set
at once. The interface also opens up the material underneath the composite. Each category can be expanded to
its **leading freelancers**, and an **individual gig** can be opened to show its own posted price across
time. Because a matched gig is nothing more than one seller's price set against its earlier self, this
per-gig view is the most direct check on what the index summarizes. It also shows plainly why thinly covered
categories look flat: when few gigs are archived in a quarter, there are simply not many lines that can move.

### 13. What are the limitations and caveats?
- **Pilot scale.** The figures rest on a sample of sellers rather than the whole marketplace, and are best
  read as indicative rather than settled.
- **Possible upward drift in the level.** The composite is chained from quarter-to-quarter geometric means.
  When the panel of matched gigs turns over heavily between quarters, indices built this way can accumulate
  drift, and diagnostic runs using drift-free multilateral (GEKS) and hedonic estimators place the true
  cumulative rise well below the chained figure. The level is therefore better read as an upper bound, with
  the *direction* of movement and the *ordering* across categories carrying more weight than the absolute
  magnitude.
- **Thin categories read flat.** Sparse matched-pair coverage can hold a series at `100` for long
  stretches, which reflects missing matches rather than genuine price stability. The earliest quarters and
  the smallest categories (translation, audio) are most exposed to this.
- **Design dominates** (~71% weight). The composite largely tracks design, and toggling it off reveals the
  rest of the basket on its own.
- **Posted, not transacted.** The prices observed are Basic-tier list prices, not the final amounts paid
  after add-ons, discounts, or negotiation.
- **Window opens in 2020.** The pre-2020 archive is too thin to chart, and the opening quarters overlap the
  COVID shock.
- **Survivorship and archiving gaps.** The Wayback Machine does not capture every page in every quarter,
  and gigs that disappear drop out of the panel.
- **Association, not established causation.** The index documents how prices moved. Assigning those
  movements to AI specifically requires the further analysis in the paper.

### 14. Can I reproduce this, and how often is it updated?
The series can be regenerated from the project's analysis pipeline under `code/`. The full-history quarterly
build is `code/18-build-site-data-long.py`, which writes `docs/data.json`; the page loads that file and
recomputes the composite on the client. `README.md` and `GUIDE.md` alongside this page document the data
contract and the build steps. Updates come from rebuilding against fresh Wayback Machine snapshots rather
than from a live feed, so the index moves when the pipeline is re-run, not continuously. Each build stamps
the page with a **generation date** and the quarters it covers, so the currency of the displayed series
stays visible. The most recent quarter depends on pages that have actually been archived and matched, which
means it can shift a little as further snapshots arrive and settles as that quarter fills in.

### 15. Found an error, or want to contribute?
The project is open. Code, data-build scripts, and this page live at
**https://github.com/AISmithLab/IntelligencePriceIndex**. A misread price, a misclassified gig, or a bug in
the pipeline can be reported as an issue or a pull request there. Suggestions on methodology are equally
welcome, since the index is meant to be auditable, and corrections from people who price this kind of work
on Fiverr and Upwork improve it.

---

## Table-of-contents (final order, mirrors `faq.html`)

1. What is the Intelligence Price Index?
2. Who is this for?
3. How do I read the index and the change column?
4. What window does the chart cover, and can I see ChatGPT or COVID in it?
5. What is priced, and how are the categories chosen?
6. Where does the data come from?
7. Why revealed Fiverr prices rather than surveys or wage data?
8. How is the index calculated?
9. Are these prices adjusted for inflation?
10. How are the category weights set?
11. Why geometric means, and can a few sellers distort the index?
12. Can I toggle categories and inspect individual freelancers or gigs?
13. What are the limitations and caveats?
14. Can I reproduce this, and how often is it updated?
15. Found an error, or want to contribute?

> The earlier 21 questions were merged into these 15: window + ChatGPT/COVID (4), priced + categories (5),
> why-revealed + why-Fiverr (7), geometric means + distortion (11), toggle + explorer (12), and reproduce +
> cadence (14). This draft is consistent with the shipped `faq.html` and with the live `index.html`
> (quarterly, 2020 Q1 → 2026 Q1, seven categories).
