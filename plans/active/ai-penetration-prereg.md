# Plan: design 9 — niche-level AI penetration as a treatment (PRE-REGISTRATION)

**Status:** active — pre-registration, no outcome yet estimated
**Created:** 2026-08-19
**Goal:** test whether the arrival of AI-branded competitors in a seller's own
niche moves that seller's price and sales, using the step-57 diffusion measure
as a time-varying continuous treatment.

## Why this design exists and why it is not design 7 again

Designs 1–8 died in four distinct ways, and step 54's gates A and B named the
structural one: **treatment varied across seven categories**, so the smallest
attainable p-value is 1/7 = 0.143 and the effective treated-cluster count in the
recent frame was one. Every category-level design in this project is capped by
that, no matter how it is estimated.

Step 57's measure is different in three ways that matter:

1. **It varies within category and within quarter**, at the listing level.
2. **It is measured inside the market**, not imported from an occupation
   crosswalk that zero-matches 36.8% of gigs.
3. **It is dated, sharply.** The break ranks 1 of 19 with an SSR spread of 227%
   (step 57 Part D), against 0.06% for step 55's weakly-identified break.

## The declared threat, stated BEFORE the design runs

**AI penetration is endogenous.** Sellers enter with AI where AI works — where
the task is automatable, where demand is growing, where incumbents are weak. A
negative correlation between niche AI penetration and incumbent prices is
therefore consistent with (a) AI competition depressing prices, (b) AI entrants
selecting into niches already in decline, and (c) both. **This design cannot
separate them and will not claim to.** It is registered as a *conditional
correlation with a declared confound*, and the promotion rule below reflects
that: it can produce a documented association, never an identified effect.

This is declared now, before estimation, precisely so it cannot become a post-hoc
excuse — the same discipline `exposure-continuous-prereg.md` §8 applied to the
O*NET weakness.

## Scope

**Covers:** construction of niches; the penetration variable; the primary
specification; the gate battery; the promotion rule.
**Does not cover:** any causal language, the 2025–26 window as a standalone test
(it is too thin — realised MDE 0.131/0.083, step 54/55), or O*NET.

## Steps

- [ ] **S1. Build niches.** TF-IDF over cleaned gig titles → KMeans on the
      balanced panel's 37,888 listings. Target ~300–600 niches (vs 7 categories).
      `code/10-cluster-items.py` is the precedent but ran on 1,908 gigs only.
      Freeze the niche assignment and commit it BEFORE any outcome is estimated.
- [ ] **S2. Adequacy gate on the niches, pre-outcome.** A niche is usable only
      with ≥30 listings and ≥8 quarters. Report how many survive. If fewer than
      100 usable niches survive, the p-floor problem is not solved and the design
      is **abandoned here**, before any outcome is seen.
- [ ] **S3. Treatment.** `pen_{n,t}` = share of listings in niche n, quarter t
      that are AI-branded (`ai_gen`, `data/pilot/ai-title-flags.csv`).
      **Leave-one-out**: a listing's own flag is excluded from its own niche's
      penetration, or the regressor contains the outcome's own label.
- [ ] **S4. Sample.** Incumbent, never-AI-branded listings only. A listing that
      adopts AI leaves the sample from its adoption quarter (its own behaviour is
      §3.7.4's territory, not this design's).
- [ ] **S5. Primary specification.**
      `y = β·pen_{n,t} + listing FE + (category × quarter) FE`,
      SEs **two-way clustered on niche and on listing**. Outcomes, both
      pre-registered, reported together, neither privileged:
      (i) log basic price; (ii) log within-gig review accrual.
- [ ] **S6. Gates, all pre-registered, all pass/fail:**
      - **G1 parallel trends** — 2019Q3–2022Q3 interactions of *future*
        penetration with quarter. Fails if >2 of 12 are significant, matching
        step 46's count rule.
      - **G2 trend horse race** — add `pen × trend`. Fails if β flips sign or
        loses significance. This killed designs 2 and 6 and is the gate this
        design is most likely to die on.
      - **G3 CPI-U placebo** — regress CPI-U on penetration. Fails if
        significant. This killed designs 3 and 6.
      - **G4 pre-AI placebo** — assign each niche its 2024 penetration and run on
        2019Q3–2021Q4. Fails if significant. This killed design 8.
      - **G5 niche-level randomisation inference** — permute penetration across
        niches within category, 999 draws. Fails if p > 0.05. This is gate A of
        step 54 applied at the unit the design actually varies over, and it is
        the reason the design exists.
      - **G6 power** — realised MDE at 80%/5%. Reported whether or not the design
        passes; an estimate below its own MDE is labelled underpowered
        regardless of its t.
- [ ] **S7. Promotion rule, fixed now.** Reported as a **finding** only if all
      six gates pass. If G1–G5 pass but G6 fails → **lead, underpowered**. If any
      of G1–G5 fails → **failed design 9**, written up with what killed it, in
      the same table as designs 1–8. **In no case is causal language used**, per
      the declared endogeneity threat above.

## Decision Log
- 2026-08-19: Design specified and registered before any outcome estimated.
  Endogeneity declared in advance as a limit on the claim, not as a gate — a
  gate would be dishonest, since no available test resolves it.
- 2026-08-19: Adopters excluded from the sample rather than controlled for.
  Controlling for own-adoption inside a penetration regression conditions on a
  post-treatment variable.
- 2026-08-19: S2 written as an abandonment point rather than a warning, so the
  design can die before any outcome is seen rather than after.

## Progress
- 2026-08-19: Created. Nothing estimated. `data/pilot/ai-title-flags.csv` is the
  input and already exists (step 57).
