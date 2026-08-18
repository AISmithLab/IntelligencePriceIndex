# Lock: the surviving descriptive structure claims

**Status:** LOCKED 2026-08-18, after steps 49 and 51 ran and before any further
specification search on the structure question
**Parent:** `plans/active/market-structure.md`
**Assembled answer:** `drafts/market-structure-answer.md`

## Why this exists

Step 46 set the precedent: on this data, a specification searched after seeing
outcomes produces tight, correctly signed, well-shaped results about nothing —
the retracted price elasticity, step 49's convergence result, step 50's primary
estimate. Steps 49 and 51 are **exploratory by construction**: eleven candidate
findings were generated and seven were killed by guards run in the same scripts.

The survivors are descriptive, not identified. This file locks them **as they
stand today**, so that anything estimated on the structure question from here on
is visibly either (a) a robustness check on a locked claim or (b) a new search
that must declare itself as one.

**This lock does not authorise a causal claim.** Six identification designs have
failed (steps 46, 48, 49 ×2, 50). Nothing below is attributed to generative AI.

## 1. LOCKED claims — the descriptive survivors

Each is stated with the frame it is read off, because the frame is the claim.
All are on `data/pilot/balanced-prices.csv`, window 2019Q3–2024Q4.

| # | claim | frame | number |
|---|---|---|---|
| D1 | the $5 commodity tier emptied | fixed panel (pre+post) | 27.3% → 10.3%; all listings 32.0% → 11.4% |
| D2 | …and it emptied **before** ChatGPT | balanced panel, break **searched** | steepest trend break **2021Q2**; ChatGPT quarter opposite-signed; decline slows after 2022Q4 |
| D3 | the top of the distribution filled | fixed panel | $100+ 15.6% → 22.4%; median $15 → $30 |
| D4 | product lines got deeper | fixed panel | 3-tier share 82.1% → 90.6% |
| D5 | the own-menu ladder compressed | fixed panel, 3-tier listings | premium/basic 4.06× → 3.80× |
| D6 | dispersion fell then partly recovered | fixed panel | sd log p 1.428 → 1.150 (2023Q3) → 1.233 |
| D7 | repricing slowed, and only on the upside | balanced panel, gap-1 pairs | any change 23.6% → 18.3%; **increases 18.1% → 12.4%; cuts 5.4% → 5.9%**; mean Δlog p +0.0565 → +0.0239 |
| D7a | …and D7 is not a coverage artefact | **strict** panel, every quarter | 936 listings: any change 24.1% → 18.1%, increases 18.5% → 12.0%, cuts 5.6% → 6.1%; pairs per listing −1.9% |
| D8 | …and that is not a ChatGPT event | balanced panel, break **searched** | best break for any-change **2021Q3**; ChatGPT quarter t 1.90, positively signed; for cuts, best break 2022Q3 and ChatGPT-quarter coef −0.0005 |

**D6 is labelled descriptive only in every use.** The attempt to convert it into a
convergence result died on a ranking-window placebo (step 49 S8).

## 2. LOCKED nulls — claims that are reported as rejected

These are results, not absences, and they may not be quietly dropped if a later
specification happens to revive one.

| # | rejected claim | killed by |
|---|---|---|
| N1 | sales concentrated on winning **listings** | Gini among trading listings flat, 0.64 (2021) → 0.61 (2023); the rise is zero-sales listings in 2024 only — trailing-edge dormancy |
| N2 | sales concentrated on winning **sellers** | Gini among trading sellers 0.637 → 0.618 → 0.651; top-decile seller share 51.5% → 50.5% → 56.4%; same 2024-only pattern |
| N3 | AI ate the cheap end (within-category price-tier DiD) | parallel trends: 10 of 11 pre-period coefficients significant; point estimate wrong-signed anyway |
| N4 | post-ChatGPT price convergence from below | ranking-window placebo: 3 of 3 windows peak inside their own ranking window |
| N5 | AI reshuffled the price ordering | rank correlation **rises** 0.898 → 0.940; and it is mechanically implied by D7 |
| N6 | price competition intensified | D7 — the fall in repricing is entirely fewer increases; cuts flat |

## 3. LEAD — not a finding, and may not be reported as one

**L1 — the within-listing price return to reputation.** Balanced panel: +0.1547
pre → +0.2455 post (difference +0.091, t 2.04), clearing a placebo split at a
false 2021Q2 break (−0.012, t −0.54). **On all 37,888 listings the same
difference is +0.0060 (t 0.79), a precise zero.**

Promotion rule, fixed now: L1 becomes reportable only if the difference is
significant **on a frame that is not selected on panel balance** — either the
full frame, or a balance requirement chosen before estimating, not after.
Otherwise it stays a lead, including in any write-up.

## 4. Guards that apply to every claim above, and to any successor

- **Balanced panel or nothing.** Gig fixed effects do not protect against
  composition: the quota manifest adds ~1,250 net cheaper listings at 2022Q3 and
  manufactures a +5.7pp jump in the ≤$10 share one quarter before the break of
  interest. Any distributional or conduct claim is read off a balanced panel.
- **Searched breaks.** No claim may assume 2022Q4. Where a break is claimed, the
  date is searched and the full search path is printed.
- **Form matters as much as date.** The commodity-tier series is a decline whose
  slope changes, so a level-shift search reports curvature and picks an endpoint.
  Both forms are printed.
- **The trailing edge is 2024Q4.** Captures per quarter collapse ~9,300 → ~700
  after it. Any claim resting on 2024 alone is a trailing-edge artefact until
  shown otherwise — this is what killed N1 and N2.
- **Sampling caveat travels with the number.** The balanced manifest is
  quota-sampled on (category, adjacent quarter pair); a within-quarter
  cross-section is not a random sample of live listings, and seller-level counts
  are properties of the sample.

## 5. What this lock forbids

1. No further specification search on the structure question may be reported
   without declaring itself a search and stating what was tried.
2. No claim in §1 may be restated on a different frame without printing both.
3. No null in §2 may be dropped from a write-up because a later specification
   revived it; the revival is reported next to the null.
4. L1 may not be promoted except by §3's rule.

## 6. Deviations

Any departure from §1–§5 is recorded here with its date, its reason, and whether
it improves or worsens the headline — per the step 48 precedent.

## Decision Log

- 2026-08-18: D7a added the same evening, after a reviewer-simulation test (`tests/structure-description.test.md` R8) asked whether the repricing fall was thinner capture coverage. It is not. Adding a robustness check that could have killed a locked claim is a permitted addition; weakening one is not.
- 2026-08-18: Locked after step 51 added the repricing result (D7/D8) and the
  seller-concentration null (N2), and before any further work on this question.
- 2026-08-18: L1 kept out of §1 despite clearing its own placebo, because it
  disagrees with the full frame. The disagreement, not the placebo, is decisive.
