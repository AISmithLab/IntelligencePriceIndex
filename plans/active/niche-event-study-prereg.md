# Plan: design 11 — staggered niche-level AI arrival, before vs after (PRE-REGISTRATION)

**Status:** active — pre-registration, no outcome estimated
**Created:** 2026-08-20
**Goal:** answer the user's question in its own form — *when AI listings arrive
in a niche, what happens to the incumbent human sellers already there, after
versus before?* — with each niche dated by its own AI arrival rather than by a
platform-wide calendar date.

## The question this answers

> In the first three years of generative-AI diffusion, how did AI entry into a
> niche change prices and competitive structure among the incumbent human
> sellers already in that niche?

This is the project's headline question narrowed on five axes: diffusion becomes
a measured variable rather than a date; the unit becomes the niche rather than
the category; the sample becomes incumbents rather than the whole market; the
window becomes the three years AI has actually existed; and the platform is
named rather than generalised to "online freelancer markets".

## Why this is not design 9, and not design 10

| | design 9 (registered, unrun) | design 10 (run, failed) | **design 11 (this)** |
|---|---|---|---|
| treatment | continuous penetration `pen_{n,t}` | 20 named launch dates | **first AI arrival in the niche** |
| timing | none — level regression | one global date per launch | **staggered, one date per niche** |
| unit | niche × quarter | category × month | niche × event-time |
| what it shows | association with penetration level | effect of a product launch | **the before/after shape at arrival** |

Design 10 died partly because a single platform-wide date puts every niche's
"after" in the same calendar quarters as the pandemic unwind, the 2022 tech
contraction and Fiverr's own move upmarket. **Staggered arrival is the fix**: a
niche whose AI competitors appear in 2024Q2 has its "before" running through
2023, when other niches are already treated. Calendar-common shocks are absorbed
by quarter fixed effects; only the event-time profile is read.

## Scope

**Covers:** niche construction, arrival dating, the event-study specification,
the gate battery, the promotion rule.
**Does not cover:** causal language; the seller-exit margin (unmeasurable, zero
404s across 509,339 captures); realised transaction prices (2022+ only, not yet
extracted).

## Steps

- [ ] **S1. Build niches, and freeze them.** TF-IDF over cleaned gig titles →
      KMeans, target 300–600 niches over the balanced panel. **The same frozen
      assignment serves design 9**, so the two designs cannot be accused of
      picking different niche definitions to suit their results. Committed before
      any outcome is estimated.

- [ ] **S2. Adequacy gate, pre-outcome.** A niche is usable with **≥30 listings**
      and **≥8 quarters** of coverage. **If fewer than 100 usable niches survive,
      the design is abandoned here**, before any outcome is seen — the p-floor
      problem that killed designs 1–8 would not have been solved.

- [ ] **S3. Date AI arrival, per niche.** Arrival quarter `a_n` = the **first
      quarter in which the niche's AI-branded share reaches ≥5% and stays ≥5%
      for at least two consecutive quarters** (`ai_gen`,
      `data/pilot/ai-title-flags.csv`). The sustain requirement exists so a
      single mislabelled title cannot date a niche. Niches that never reach the
      threshold are **never-treated controls**.
      - Report the distribution of `a_n`. **If arrivals are not staggered — if
        more than 70% of treated niches share one quarter — the design collapses
        back to a single global date and is abandoned at S3**, because that is
        design 10 with extra steps.

- [ ] **S4. Sample.** Listings present in the niche **before** its arrival
      quarter and **never AI-branded in any quarter**. A listing that adopts AI
      leaves the sample from its adoption quarter. Never-treated niches
      contribute their listings over the whole window.

- [ ] **S5. Primary specification.** Event study in event time `k = t − a_n`,
      k ∈ [−8, +8], `k = −1` omitted as the reference:

      `y_{i,t} = Σ_k β_k · 1[t − a_{n(i)} = k] + listing FE + quarter FE + ε`

      **Controls are never-treated niches only.** Already-treated niches are
      excluded from the control group, so no comparison uses a treated unit as a
      counterfactual — the negative-weighting failure of two-way fixed effects
      under staggered adoption. SEs **clustered on niche**.

      Two outcomes, both pre-registered, reported together, neither privileged:
      (i) **log basic price**; (ii) **log within-gig review accrual**.

- [ ] **S6. Gates — all fixed now, all pass/fail.**
      - **G1 pre-trend (the decisive one).** Joint test that β_{−8..−2} = 0.
        Fails if the joint test rejects at 5%, or if >2 of the 7 pre-period
        coefficients are individually significant. *This is what killed the
        image-model result in design 10 and it is the gate the user's question
        turns on: if the niche was already sliding, the after-number means
        nothing.*
      - **G2 fake arrival placebo.** Re-date every treated niche **8 quarters
        earlier** and re-run. Fails if the post-period coefficients are
        significant — the design would be firing at arbitrary dates, which is
        exactly how design 10's demand margin died (75% false-positive rate).
      - **G3 never-treated placebo.** Assign never-treated niches random arrival
        quarters drawn from the treated distribution. Fails if significant.
      - **G4 niche randomisation inference.** Permute arrival dates across
        niches, 999 draws. Fails if p > 0.05.
      - **G5 composition.** The estimate must survive on a balanced event-time
        panel — listings observed at every k in [−4, +4]. Fails if the sign flips.
      - **G6 power.** Realised MDE at 80%/5%, reported whether or not the design
        passes. An estimate below its own MDE is labelled underpowered
        regardless of its t.

- [ ] **S7. Promotion rule, fixed now.**
      - All six gates pass → reported as a **finding**, in association language.
      - G1–G5 pass, G6 fails → **lead, underpowered**.
      - Any of G1–G5 fails → **failed design 11**, written into the same table
        as designs 1–10 with what killed it.
      - **In no case is causal language used.** AI entrants choose their niches;
        entry is not random and no gate here makes it so.

## The declared threat, stated before the design runs

**Arrival is endogenous.** AI sellers enter niches where AI works — where the
task is automatable, where demand is growing, where incumbents are weak or slow.
A post-arrival fall in incumbent sales is therefore consistent with (a) AI
competitors taking the work, (b) AI entrants selecting into niches that were
already turning, and (c) both. G1 tests (b) in its *observable* form — a
pre-existing trend — and cannot rule out selection on a level or on an
unobserved shock timed to arrival.

This is declared now so it cannot become a post-hoc excuse.

## Decision Log
- 2026-08-20: Registered before any outcome estimated, on the user's request for
  a before/after design.
- 2026-08-20: Never-treated-only controls chosen over standard two-way FE.
  Under staggered adoption, TWFE uses already-treated units as controls and can
  return a sign opposite to every underlying effect. Not a robustness check — the
  primary specification.
- 2026-08-20: Arrival threshold set at 5% sustained two quarters, fixed before
  the distribution of niche AI shares was inspected at niche level. The
  platform-wide new-listing share reached 5.98% in 2023Q1 (step 57), so 5% is
  "AI is visibly present here", not "one AI gig exists".
- 2026-08-20: S3 given its own abandonment condition. If arrival is not
  genuinely staggered the design is design 10 rebuilt, and its failure would
  carry no new information.

## Progress
- 2026-08-20: Created. Nothing estimated.
