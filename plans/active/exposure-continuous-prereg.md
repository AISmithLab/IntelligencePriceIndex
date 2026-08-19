# Pre-registration: gig-level continuous AI-exposure design

**Status:** LOCKED 2026-08-18, before any outcome is estimated under this exposure measure
**Supersedes:** nothing. Complements `plans/active/transaction-volume-prereg.md`
**Parent:** `plans/active/market-structure.md`

## 0. Why this exists, and why it is the last design in view

Five designs have now failed to identify an AI effect on this data:

| # | design | killed by | step |
|---|---|---|---|
| 1 | category DiD, HIGH vs LOW exposure | parallel trends (6/16 pre-period coefs sig.) | 46 |
| 2 | trend horse race | HIGH x POST collapses −7.9% → −0.8% | 46 |
| 3 | CPI-U placebo | significant (−3.6%, t −2.93) | 46 |
| 4 | synthetic control + in-space placebos | translation ranks LAST of 7; p-floor 1/7 = 0.143 | 48 |
| 5 | within-category price-tier DiD | parallel trends (10/11 pre-period coefs sig.) | 49 |

Designs 1–4 share one defect: **seven units.** The p-floor is 0.143 by
construction, so the test cannot reach 5% no matter what the data say. Design 5
fixed the unit count but used *price* as the treatment proxy, and step 49 showed
price rank is contaminated by mean reversion.

This design fixes both: **continuous, text-derived exposure at the gig level,**
external to our data, with **category x quarter fixed effects** absorbing every
platform-wide and category-wide shock — including the ones that killed 1–4.

**Prior belief, recorded before running:** low. Five failures on the same
underlying data is evidence about the data, not only about the designs. The value
of this pre-registration is that it makes a sixth failure *interpretable* rather
than another discarded specification.

## 1. FULL DISCLOSURE — what was already seen before this lock

Honesty about this is the whole point, so it is stated first and completely.
A feasibility pilot was run on 2026-08-18 and the following were observed:

- 39,933 gigs carry a usable description; **36.8% get a zero TF-IDF match** to
  any O*NET occupation title, so effective coverage is **63.2%**.
- Automated per-category mean exposure vs the pre-registered ranking in
  `data/exposure-ranking.csv`: **Spearman rho = +0.679 (K=1), +0.786 (K=3),
  +0.714 (K=5), +0.714 (K=10)**. The automated ranking puts marketing above
  translation; otherwise the ordering agrees.
- **Within-category sd of exposure is 0.11–0.20**, against a between-category
  range of 0.13 (0.342 design → 0.472 marketing). Within-category variation is
  at least as large as between-category variation.

**Nothing else was seen.** No outcome — price, accrual, dispersion, anything —
has been regressed on this exposure measure. K=3 is selected below because it
maximises agreement with the pre-registered ranking, which is a decision made on
a *validation* statistic, not on an outcome, and it is declared here so a reader
can discount it.

## 2. Exposure measure — LOCKED

**Source.** `data/eloundou-2023-occ-level.csv` (Eloundou et al. 2023, 923 O*NET-SOC
occupations), already vendored, already used for the pre-registered category
ranking in step 45. External to our data by construction.

**Primary rating** `human_rating_beta`. **Robustness** `dv_rating_beta`. Same
choice and same rationale as step 45; not revisited here.

**Gig text.** The first observed `title` per gig on the balanced frame, cleaned by
the existing `code/10-cluster-items.py` rules (strip seller prefix, strip
`for $X on fiverr.com`, strip leading `I will`, lowercase, collapse whitespace).
Gigs whose cleaned description is under 10 characters are dropped.

**Scoring.** TF-IDF over the union of gig descriptions and O*NET occupation
titles, `stop_words="english"`, `ngram_range=(1,2)`, `sublinear_tf=True`,
`min_df=1`. Cosine similarity gig x occupation. Exposure is the
**similarity-weighted mean of the top K=3 occupations**.

**Robustness grid, fixed now:** K in {1, 5, 10} and `dv_rating_beta`. Any reported
finding must be shown under all of them.

**Zero-match gigs (36.8%) are DROPPED**, and this is a selection threat, not a
technicality. Required alongside any result: the category composition, price
distribution and pre-period accrual of dropped vs kept gigs. If dropped gigs
differ on pre-period accrual by more than 10%, the drop is declared a threat to
external validity in the write-up.

## 3. Sample, window, break — LOCKED

- Frame: `data/pilot/balanced-prices.csv` + `balanced-manifest-1200.tsv`, `is_gig` applied.
- Window **2019Q3–2024Q4**. Start: extraction is 100% `packageList` from 2019Q3.
  End: step 48's trailing-edge collapse.
- Break **2022Q4** (ChatGPT, 2022-11-30). Single, pre-specified, not searched.
- One observation per gig-quarter (latest capture in the quarter).
- Accrual pairs: consecutive observed quarters, gap 1–2, rate per quarter,
  non-negative. Identical to step 46 so the two are comparable.

## 4. Outcomes and specification — LOCKED

**Primary outcome** `log1p(quarterly review accrual)` — same as step 46.
**Secondary outcome** `log(basic price)`.

**Primary specification**

    y_igt = beta * (exposure_i x POST_t) + gig FE + (category x quarter) FE + e_igt

gig-clustered SEs. `exposure_i` is time-invariant and absorbed by gig FE; `POST_t`
is absorbed by category x quarter FE. **Only the interaction is identified, and
the category x quarter FE is the whole point** — it absorbs the platform-wide
demand fall that steps 46–48 kept mistaking for a treatment effect.

**Report the realised MDE next to the estimate**, per the step 46 precedent. An
uninformative null is not a null.

## 5. GATES — pre-committed, with consequences fixed in advance

Each gate is PASS/FAIL. **The consequence of failure is stated now so it cannot be
negotiated later.**

- **G1 Parallel trends.** Event study, `exposure x quarter`, 2022Q3 omitted.
  Rule: **joint F-test of all pre-period interactions = 0 must not reject at 5%.**
  (A joint test, not step 46's count rule: with 11 pre-quarters, ~0.55 significant
  coefficients are expected under the null, so a count rule fails by construction.)
  The count is reported too, for comparability with step 46.
  **FAIL ⇒ the DiD is dead and is reported as dead.** Only authorised fallback:
  §6 below.

- **G2 Not-a-price-proxy.** Step 49 killed a design because pre-period price rank
  is contaminated by mean reversion. Re-run the primary spec adding
  `pre-period price rank x quarter` as a control. **beta must retain its sign and
  remain significant.** FAIL ⇒ the estimate is a repriced-listing effect, not an
  exposure effect, and is reported as such.

- **G3 Placebo window.** Window 2019Q3–2021Q4, false break 2020Q3.
  **Must return null.** FAIL ⇒ the SEs are wrong (the step 29 disease) and nothing
  is causal.

- **G4 Step-29 battery.** First differences; linear-trend horse race
  (`exposure x trend` included — beta on `exposure x POST` must survive);
  CPI-U placebo; Newey-West. **All four must pass.**

- **G5 Composition.** Step 49's lesson: gig FE do NOT protect against composition,
  because the quota manifest adds ~1,250 cheaper listings at 2022Q3. The primary
  spec is therefore re-run on the balanced panel (listings present in >=80% of
  quarters). **Sign and significance must survive.**

## 6. The ONLY authorised fallback

If G1 fails: report **descriptive dose–response by exposure decile** — mean
accrual change 2022Q3→post by decile, with bands — and state explicitly that it
is not identified. No new specification may be searched on this data under this
plan. A sixth failure is written up as a failure.

## 7. What is NOT identified even on a full pass

- **Exit.** `n_404 = 0` across 509,339 captures. Nothing here is labelled exit.
- **Realised order value.** The IPI reads listed basic-package prices; step 47
  shows the buyer mix moved upmarket, so listed price understates realised price.
- **Anything after 2024Q4.** The treatment window is eight quarters and stops
  before the 2025–26 agentic period.
- **`review_count` is a sales proxy, not sales.**

## 8. Known weakness, and the one thing that would fix it

The binding constraint is **mapping quality**: O*NET occupation *titles* are a few
words long, which is why 36.8% of gigs match nothing and why marketing outranks
translation. The fix is O*NET **task statements** (or Eloundou's task-level file),
which give far richer text per occupation and would plausibly push coverage well
above 63%. That is a small additional vendored download and is **out of scope for
this lock** — recorded here so that if the design fails, "the mapping was thin" is
a stated prior weakness rather than a post-hoc excuse.

## 9. Deviations

Any departure from §2–§5 must be recorded here with its date, its reason, and
**whether it improves or worsens the headline finding**, per the step 48 precedent.

## Decision Log

- 2026-08-18: Locked before any outcome regression. K=3 chosen on ranking
  agreement, a validation statistic, and the choice is disclosed in §1.
- 2026-08-18: G1 uses a joint F-test rather than step 46's zero-significant-
  coefficient count rule, which is infeasible with 11 pre-period quarters.
- 2026-08-18: Task-level O*NET text deliberately excluded from this lock, so that
  mapping thinness is a declared prior weakness rather than a later excuse.

## 10. RESULT — recorded 2026-08-18, after running `code/50-continuous-exposure.py`

**No deviations from §2–§5.** The locked specification ran as written. Output:
`runs/continuous-exposure.out`.

### Gate card

| gate | result |
|---|---|
| §2 selection audit | **THREAT DECLARED** — dropped (zero-match) gigs accrue **+23.7%** more pre-period than kept gigs, past the 10% tolerance |
| G1 parallel trends | **PASS** — Wald chi2(11) = 9.99, **p = 0.53**; 0 of 11 pre-period coefficients significant |
| G2 not-a-price-proxy | **PASS** — −0.1692 (t −2.43) controlling for price rank × quarter, vs −0.1680 uncontrolled |
| G3 placebo window | **PASS** — false break at 2020Q3 returns −0.036 (t −0.45), null as required |
| G4.1 first differences | PASS by construction |
| G4.2 trend horse race | **FAIL** — `exposure × trend` −0.0226 (t −2.54) and `exposure × POST` **collapses to +0.0214 (t 0.28)**, a sign flip |
| G4.3 CPI-U placebo | **FAIL** — −0.1133 (**t −2.86**) |
| G4.4 Newey-West | PASS — Durbin–Watson 1.73 |
| G5 composition | **FAIL** — balanced frame −0.2022 (t −1.85) |

**Primary estimate:** `exposure × POST` = **−0.1680** (se 0.0666, t −2.52), 121,414
observations on 20,966 gigs. Significant, correctly signed, and stable across the
whole robustness grid (K = 1/5/10: −0.140/−0.198/−0.192; `dv_rating_beta`: −0.114;
all significant). Secondary outcome log(price): **+0.0021 (t 0.06)**, a precise zero.

### Verdict: FAIL. Sixth design, and the most informative failure so far.

**This is the first design in the project to pass parallel trends on the demand
margin.** G1 passes comfortably (p = 0.53, and on step 46's stricter count rule
too), G2 rules out the step-49 mean-reversion disease, and G3 rules out the step-29
standard-error disease. Three of the four ways the previous designs died are now
excluded.

It dies on the fourth. `exposure × trend` is significant and `exposure × POST`
**changes sign** once it is included — exposure-correlated gigs were already on a
divergent trend before ChatGPT — and the CPI-U placebo is significant at t −2.86,
which means the interaction tracks *any* smooth time series, not an AI event.
The §6 dose–response confirms it: decile changes run −13.3% to +3.5% with **no
monotone gradient**, and the *least*-exposed decile (−7.8%) falls more than the
most-exposed (−1.9%).

**Three honest qualifications, so the failure is not overstated:**

1. **The estimate was underpowered against its own pre-registered standard.** The
   realised MDE is ±0.186 log points (±20.5%) and |β| is **0.90× the MDE**. Even
   had every gate passed, this estimate sits below the power threshold.
2. **G5's failure is power, not sign.** The balanced-frame estimate is −0.2022,
   *larger* in magnitude and identically signed; it loses significance because n
   falls to 1,715 gigs. The §5 rule required significance, so it is recorded FAIL
   by the letter of the lock — but "the sign reversed" would be a misreading.
3. **An internal contradiction worth keeping.** The collapsed Newey-West difference
   series returns `post` = **+0.0701 (t 2.44)** — the opposite sign to the panel
   estimate. The series carries no gig fixed effects, so the gap is composition,
   and it is one more reason not to read −0.168 as an effect.

### What this closes

Six designs have now failed. Across all six the surviving pattern is the same and
is now specific: **there is an exposure-correlated differential trend that predates
ChatGPT, and there is no break at ChatGPT.** That is a finding about the data, and
per §0 it was the recorded prior.

### What is left, in order of value

1. **O*NET task statements** (§8's declared prior weakness). 36.7% zero-match, and
   the dropped gigs accrue 23.7% more — the measure is thin *and* selected. Fixing
   the text is the one input change that could alter the exposure measure itself.
2. **Reach past 2024Q4.** The treatment window is eight quarters and stops before
   the 2025–26 agentic period. Needs the live forward crawl.
3. **Accept the platform-wide reading** and write up the structure results from
   step 49 as description, which is what they already are.
