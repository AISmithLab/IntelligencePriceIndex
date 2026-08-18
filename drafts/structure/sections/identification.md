## 4. Six identification designs, and why each fails

Nothing in §3 is attributed to generative AI, because on these data nothing can
be. This section reports the six designs that tried, in the order they were run,
with the diagnostic that kills each. We report them in full for two reasons.
First, five of the six produce a **significant, correctly signed, plausibly sized
AI effect** before their guards are applied — so the guards, not the estimates,
are the content. Second, their failures are structured, and the structure is
itself the finding (§4.7).

| # | design | killed by |
|---|---|---|
| I1 | category DiD, HIGH vs LOW exposure | parallel trends: 6 of 16 pre-period coefficients significant |
| I2 | trend horse race | HIGH × POST collapses −7.9% → −0.8% once HIGH × trend enters |
| I3 | CPI-U placebo | significant (−3.6%, t −2.93): the design tracks any smooth series |
| I4 | synthetic control with in-space placebos | the most-exposed category ranks **last of 7**; p-floor 1/7 = 0.143 |
| I5 | within-category price-tier DiD | parallel trends: 10 of 11 pre-period coefficients significant |
| I6 | gig-level continuous exposure (**pre-registered**) | trend horse race (sign flip) and CPI-U placebo (t −2.86) |

### 4.1 I1–I3 — the category difference-in-differences

Seven categories split into HIGH and LOW exposure arms on a ranking
pre-registered from [CITE-eloundou2023], outcome log1p quarterly review accrual,
listing FE, break at 2022Q4.

Had the gate not been committed in advance, the headline would have been
**HIGH × POST = −7.9% [−11.4, −4.2], t = −4.14** on a realised MDE of ±3.96% —
tight, significant, correctly signed, and meeting the project's stated precision
standard. It is wrong, and three checks say so:

- **Parallel trends fails.** Event study with 2022Q3 omitted: 6 of 16 pre-period
  interactions significant at 5%. The pre-registered rule was zero, so the DiD is
  reported dead.
- **Trend horse race.** Adding HIGH × trend collapses HIGH × POST to −0.0078
  (t −0.30) while HIGH × trend is itself significant (−0.0083, t −2.98). The
  "break at ChatGPT" is a differential trend that predates it.
- **CPI-U placebo.** HIGH × CPI-U — a series with no AI content — is significant
  (−3.6%, t −2.93).

Two further checks pass and are reported for completeness: a placebo window
(false break 2019Q2) returns −1.5% (t −0.17), and Newey–West on the collapsed
HIGH-minus-LOW series returns +0.0041 (t 0.13) with Durbin–Watson 2.26 — so
unlike an earlier retracted result in this project, the standard errors are not
the problem here. The effect simply is not there.

The deeper problem is visible without any regression: **every category fell,
including the least exposed.** Spearman ρ between exposure rank and break size is
+0.429 across seven categories, where |ρ| > 0.79 is needed for p < 0.05.

### 4.2 I4 — synthetic control, and an internal contradiction

The pre-registration's only authorised fallback. Each HIGH category is matched to
a synthetic control built from LOW-exposure donors.

| target | exposure | registered donors | expanded donors |
|---|---:|---|---|
| **translation** | **0.840** (most exposed) | −2.2%, ratio 0.14 → within noise | **+1.4%, wrong-signed** |
| writing | 0.686 | −12.4%, ratio 1.08 | −15.6%, ratio 1.81 |

(`ratio` = mean absolute post gap over pre-period RMSPE.) **The single most
AI-exposed category shows essentially no deviation from its synthetic control,
and flips sign when the donor pool widens.** The two HIGH categories disagree
with each other, which is fatal on its own: the measure that ranks translation
top is the measure the study pre-registered.

In-space placebos make the ceiling explicit. Writing ranks 1 of 7 (one-sided
p = 0.143); translation ranks **7 of 7** (p = 1.000); and audio, the *least*
exposed category, ranks second. **With seven units the smallest attainable
one-sided p-value is 1/7 = 0.143, so this test cannot reach 5% no matter what
the data say.** That is a property of the design space, not of the result — and
it applies to I1–I4 alike.

### 4.3 I5 — abandoning categories for within-category price rank

Rank listings by pre-period price *within* category, let category × quarter fixed
effects absorb every platform-wide shock, and ask whether cheap listings lost more
demand. This replaces 7 units with 16,526 ranked listings.

The event study fails: **10 of 11 pre-period coefficients significant**,
pre-period mean −0.18 against post-period −0.25 — no break, a wandering gradient.
The point estimate (−0.109, t −3.56) is in any case wrong-signed for the
hypothesis.

**The companion specification is the cautionary tale of this paper.** The same
design run on *prices* returns the most publishable-looking shape we produced: a
clean sign reversal at exactly 2022Q3/Q4, monotone afterwards, every coefficient
significant. It is **mean reversion**. Moving the ranking window moves the whole
pattern with it — 3 of 3 windows peak inside their own ranking window and decay
away from it in both directions — and dropping the ranking window from the
estimation sample changes nothing, which locates the bias in rank measurement
error rather than in sample overlap.

### 4.4 I6 — the pre-registered continuous-exposure design

The final design was **locked before any outcome was estimated** [CITE-prereg],
with the exposure measure, sample, window, break, specification, robustness grid
and five gates fixed in advance, each gate's failure consequence stated so it
could not be renegotiated. Full disclosure of what had been seen beforehand (a
feasibility pilot on coverage and ranking agreement only) is recorded in the
lock, as is a **prior belief of low**: five designs had already failed, and the
lock's stated purpose was to make a sixth failure interpretable rather than
discardable.

Specification: `y = β·(exposure × POST) + listing FE + (category × quarter) FE`,
listing-clustered SEs, on 121,414 observations across 20,966 listings. The
category × quarter term is the whole point — it absorbs the platform-wide demand
fall that I1–I4 kept mistaking for treatment.

**Gate card, as recorded:**

| gate | result |
|---|---|
| selection audit | **threat declared** — dropped (zero-match) listings accrue **+23.7%** more pre-period, past the 10% tolerance |
| G1 parallel trends | **PASS** — Wald χ²(11) = 9.99, **p = 0.53**; 0 of 11 pre-period coefficients significant |
| G2 not-a-price-proxy | **PASS** — −0.1692 (t −2.43) controlling for price rank × quarter |
| G3 placebo window | **PASS** — false break at 2020Q3 returns −0.036 (t −0.45) |
| G4.1 first differences | pass by construction |
| G4.2 trend horse race | **FAIL** — `exposure × trend` −0.0226 (t −2.54); `exposure × POST` **flips to +0.0214 (t 0.28)** |
| G4.3 CPI-U placebo | **FAIL** — −0.1133 (**t −2.86**) |
| G4.4 Newey–West | pass — Durbin–Watson 1.73 |
| G5 composition | **FAIL** — balanced frame −0.2022 (t −1.85) |

Primary estimate **−0.1680 (se 0.0666, t −2.52)**, stable across the entire
pre-registered robustness grid (K = 1/5/10 → −0.140/−0.198/−0.192; the alternative
exposure rating → −0.114; all significant). The secondary price outcome is a
precise zero, **+0.0021 (t 0.06)**.

**This is the first design in the project to pass parallel trends on the demand
margin** — on both the pre-registered joint test and I1's stricter count rule —
and G2 and G3 rule out the two failure modes that killed I5 and an earlier
retracted result. Three of the four ways prior designs died are excluded. It dies
on the fourth: the exposure interaction changes sign once a differential trend is
allowed, and the CPI-U placebo shows the interaction tracks any smooth series.

The pre-registered fallback — descriptive dose–response by exposure decile,
explicitly not identified — agrees: decile changes run −13.3% to +3.5% with **no
monotone gradient**, and the *least*-exposed decile falls more (−7.8%) than the
most-exposed (−1.9%).

**Three qualifications, so the failure is not overstated.** (i) The estimate was
underpowered against its own pre-registered standard: realised MDE ±0.186 log
points and |β| is 0.90× the MDE. (ii) G5 failed on power, not sign — the balanced
estimate is −0.2022, *larger* and identically signed, losing significance only
because n falls to 1,715 listings; recorded FAIL by the letter of the lock, but
"the sign reversed" would be a misreading. (iii) The collapsed Newey–West
difference series returns +0.0701 (t 2.44), opposite in sign to the panel
estimate; it carries no listing fixed effects, so the gap is composition — one
more reason not to read −0.168 as an effect.

### 4.5 What the six failures jointly establish

They are not six independent nulls. Across all six the surviving pattern is the
same, and after I6 it is specific:

> **There is an exposure-correlated differential trend that predates ChatGPT, and
> there is no break at ChatGPT.**

Two descriptive series in §3, built without any exposure measure, date the
structural change the same way: the commodity tier's steepest decline is 2021Q2
(§3.3) and the repricing break is 2021Q3 (§3.4). A third — the platform's buyer
growth — inflects in 2022, from +23.5% to exactly +0.0%. The transformation was
under way before generative AI was publicly available.

### 4.6 A note on method

Every design in this section was run against a placebo capable of destroying it,
in the same script that produced it, and the gate rules for I6 were fixed before
estimation. We stress this because the alternative was available and would have
been publishable: I1 alone yields a −7.9% AI effect with t = −4.14 meeting a
stated precision standard, and I5's price variant yields a textbook event-study
figure. Both are artefacts. On observational marketplace data of this shape,
**the guard is the result**.
