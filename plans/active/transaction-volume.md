# Plan: Is transaction volume on Fiverr falling as AI develops, and where?

**Status:** active
**Created:** 2026-08-14
**Goal:** Answer the quantity question the price index cannot — did Fiverr transactions fall as AI diffused, and does the fall differ by category — using the balanced collection, which is 23.6× better powered for this than anything step 24 ran on.

**User decisions, 2026-08-14:** (1) **causal from the start**, not descriptive-first;
(2) this is a **separate third paper**, not part of paper 2; (3) the live forward crawl is
**deferred** — decide after Phase 0. See §8 for what (1) changes about the ordering.

## Scope

**Covers:** demand-rate measurement from `review_count` accrual, entry, dormancy,
the identification design that separates AI from trend, external validation against
Fiverr Inc.'s reported figures, and the specification of a forward crawl for the part
the archive cannot reach.

**Does not cover:** the price index, the submission draft, or `data/pilot/paper-numbers.md`.
The pilot paper is frozen; this is paper-2 frame work and must not touch a paper section.

---

## 1. What "number of transactions" decomposes into

The platform never publishes a transaction count per gig, and an archived page shows a
price but never a sale. The question therefore splits into three sub-questions with very
different feasibility, and conflating them is the main way this study could go wrong.

| # | Sub-question | Observable? | Instrument |
|---|---|---|---|
| **Q1** | Do *surviving gigs* sell less? | **Yes, well** | `review_count` accrual per gig-quarter |
| **Q2** | Are there *fewer gigs* — more exit, less entry? | **Entry partly; exit no** | first/last capture; dormancy as a proxy |
| **Q3** | Did *platform-wide* volume fall? | **Not from the crawl** | Fiverr Inc. (NYSE: FVRR) reported GMV / active buyers |

Q1 × Q2 ≈ Q3. A finding on Q1 alone is **not** an answer to "are transactions falling" —
it is an answer to "is the average surviving gig selling less". The plan must say which
one every number belongs to, and Q3 exists mainly to check whether Q1 and Q2 together
point the same way as the platform's own books.

## 2. The two hard constraints, both already measured

**(a) Exit is not measurable from the archive. This is settled, not open.**
`code/39-status-ledger.py` streamed all 60.0M raw CDX rows and found **`n_404 = 0` across
509,339 in-window captures** of 25,051 gigs. Wayback stops re-requesting a delisted URL
rather than recording its death. No volume of additional archive collection produces an
exit hazard. Anything labelled "exit" in this study is dormancy — a gig still listed and
accruing nothing — and must be labelled as such every time it is reported.

**(b) The trailing edge is nearly empty, and it is exactly the period of interest.**
Accrual observations per quarter in the balanced frame:

| period | obs/quarter |
|---|---:|
| 2019Q1–2024Q3 | ~9,300–12,000 |
| 2024Q4 | 7,774 |
| **2025Q1** | **1,605** |
| **2025Q2–2026Q1** | **598–847** |

2026Q2 Fiverr gig captures are ~all 403 and our index falls from 280,779 status-200
snapshots in 202409 to 66 in 202603. So **this study answers the question through 2024Q4**
— which does cover ChatGPT (2022Q4), GPT-4 (2023Q1) and the 2023–2024 diffusion, but not
the 2025–2026 agentic period. Say so in the title of every exhibit. Extending past 2024Q4
requires the forward crawl in Phase 4, and nothing else.

## 3. Why this is worth doing now: step 24 was underpowered by a factor of ~5

`code/24-margin-diagnostics.py` already asked this question and found **null demand breaks
in all seven categories** — but with a minimum detectable effect of **±23% (coding) to ±66%
(translation)**. A null that wide excludes almost nothing.

It ran on the shipped panels. The balanced collection is a different order of magnitude:

| frame | gigs w/ review data | gigs ≥2 quarters | **accrual observations** |
|---|---:|---:|---:|
| shipped historical (`pilot-prices`) | 1,373 | 997 | 5,403 |
| shipped recent (`recent-prices`) | 2,596 | 2,537 | 4,872 |
| expanded / rule B | 19,651 | 19,245 | 22,967 |
| **balanced** | **36,700** | **36,336** | **242,468** |

Step 24's total was 10,275. Balanced gives **242,468 — 23.6×**, and on 1/√n that takes the
MDE from ±23% to roughly **±4.7%** for coding and from ±66% to roughly **±14%** for
translation. That converts an uninformative null into an informative one, and it needs
**no new data collection**. This is the highest-value move in the plan and it is Phase 0.

`review_count` also behaves: **only 0.58% of 242,468 consecutive deltas are negative**, so
the series is monotone cumulative and coverage is **95.5%** of rows (92.6–98.1% per year to
2024; 71.8% in 2025, which is another reason the trailing edge is unusable).

## 4. The identification trap this project has already fallen into once

Step 29 retracted the elasticity table because a regression of a trending outcome on a
trending AI score failed three independent tests: **Durbin–Watson 0.22–1.08**, a **linear
time trend fit better in all six categories**, **CPI-U — which has no AI content — fit at
least as well in five of six**, and **in first differences the relationship vanished**
(t = 0.26, −0.02, 0.48, 2.24, −0.34, 0.20).

A demand series is if anything *more* trending than a price series. The same design would
fail the same way. So this study is **not** "regress transactions on an AI index". It is:

- **Descriptive first.** Publish the demand-rate path per category with bands, and stop
  there if the design tests fail.
- **Cross-category difference-in-differences**, where the treatment is *exposure*, not
  time. Categories are ranked by AI substitutability (translation and writing high; video
  and audio production lower), and the estimand is the *differential* break — which
  differences out any platform-wide shock, seasonality, and the ageing profile.
- **Every claim runs the step-29 battery before it is written down**: first differences,
  a linear-trend horse race, a CPI-U (or other AI-free series) placebo, and Newey–West SEs.

The pre-AI placebo window is already an open item in `plans/todo.md`; this study needs it
and should discharge it.

## 5. Known confounds, each with the check that addresses it

| Confound | Why it bites | Check |
|---|---|---|
| **Age ≡ period − cohort** under gig fixed effects | The quarter path contains the panel's ageing profile and cannot be read as demand. Step 24 says the *level break* is identified and the *path* is not. | Report breaks, not levels. Two specs bracketing age/period/cohort, as step 24 already does. |
| **Review propensity drift** | If buyers review less over time, accrual falls with no change in sales. Never tested. | **New.** Compare accrual against an independent volume signal on the same gigs; test for a platform-wide propensity break at UI changes. If untestable, state it as a signed bound. |
| **Survivorship** | The shipped recent panel required a trailing-window capture. | Balanced rule-B frame has no survivor filter — already fixed. |
| **Crawl intensity** | Wayback captures more in some months; entry rates especially are contaminated. | Normalise by capture intensity per category-month, as step 24's M3 does. |
| **Composition** | Category mix shifts. | Within-gig only; report the between/within split. |
| **Top-coding / rounding** | Fiverr displays "1k+" style counts at high volume. | Audit the `review_count` distribution for ceiling artefacts; censor or model. |

## 6. Steps

### Phase −1 — pre-registration (gates Phase 0; see §8) — **DONE 2026-08-17**
Registered at `plans/active/transaction-volume-prereg.md`, built by
`code/45-exposure-ranking.py` from `data/eloundou-2023-occ-level.csv`.
- [x] Externally-sourced AI-exposure ranking of the seven categories, dated and committed.
      Eloundou et al. (2023) β exposure, human annotation primary and GPT-4 annotation as
      declared robustness. **HIGH = {translation, writing}, LOW = {video, audio}** — the four
      categories both annotators agree on. **Coding is quarantined**, because the two
      annotators disagree hard about it: GPT-4 ranks it 1st of 7 (0.917), human labellers
      4th (0.588). Marketing moves the other way (3rd → 5th). Declaring that now costs
      nothing; discovering it after Phase 0 would have looked like arm-picking.
- [x] Pre-registered specification: outcome, break date (2022Q4), gig + quarter FE,
      gig-clustered SEs, placebo window (2018Q3–2019Q4, false break 2019Q2), and the
      pass/fail rule for the step-29 battery (survive all four or it is descriptive).
- [x] Parallel-trends check plan, with the synthetic-control fallback named in advance and
      an explicit "no third fallback" clause.
- [x] Power computed pre-outcome: the primary contrast holds **129,378 accrual
      observations** (HIGH 61,737 + LOW 67,641). The per-category split also reproduces the
      plan's 36,336 gigs / 242,468 observations exactly, so the frame is verified.

### Phase 0 — re-run the existing diagnostics on the balanced frame — **DONE 2026-08-17**
`code/46-balanced-demand.py` → `runs/phase0-demand.out`. 236,535 accrual observations,
35,888 gigs, 2018Q1–2024Q4. Implemented as a new step rather than by editing step 24, so
step 24 stays intact as the underpowered comparison the result is measured against.
- [x] Re-run the demand-rate break on the balanced frame; report the new MDE per category
      next to step 24's. **MDE is 4.7×–9.4× tighter (±4.2% to ±7.0%, was ±23% to ±66%).**
- [x] **Decision gate resolved — and it resolved to neither branch the plan anticipated.**
      The breaks are **not null**: all seven categories fall significantly, −13.1% (design)
      to −42.9% (writing), every |t| > 6.6. But they fall *together*, including the two
      lowest-exposure categories, so the finding is a **platform-wide** decline and Phase 2
      does **not** become the main event — the differential is not identified (see below).
- [x] Parallel trends: **FAILED** the pre-registered gate, 6 of 16 pre-period interactions
      significant. DiD reported as dead per §5; synthetic control is the authorised fallback.
- [x] Step-29 battery: **failed two of four.** The trend horse race collapses HIGH × POST
      from −7.9% (t −4.14) to −0.8% (t −0.30) while HIGH × trend is significant (t −2.98),
      and the **CPI-U placebo is significant** (−3.6%, t −2.93). Placebo window passes
      (t −0.17); Durbin–Watson 2.26, so unlike step 29 the SEs are not the defect — the
      effect is not there. Collapsed Newey–West series: post +0.0041, t 0.13, wrong-signed.
- [x] Descriptive check: Spearman ρ between pre-registered exposure and break size is
      **+0.429** over seven categories, against the ~0.79 needed for p < 0.05. **audio is
      least exposed of the seven and has the third-largest fall; design has the smallest.**

### Phase 1 — establish `review_count` as a transaction proxy, or bound it
**PROMOTED 2026-08-17 to the study's critical path.** Phase 0 found a *platform-wide*
accrual fall of 13–43%, which is exactly the signature of review-propensity drift — buyers
reviewing a smaller share of purchases over time, with no change in sales whatsoever.
The confound now threatens the headline number, not merely the differential. **The −13% to
−43% must not be described as a demand decline until this phase runs.**
- [ ] Monotonicity, coverage and censoring audit (0.58% negative deltas is the starting point).
- [ ] Review-propensity drift test — the one confound with no current answer. Test the
      *global* level first (Phase 0 makes it the binding threat), then the *differential*
      by exposure arm (which is what would revive the DiD).
- [ ] Cross-check accrual against the price panel's own gigs where both exist.
- [ ] Write a short "what one review means" note; every downstream number inherits it.

### Phase 2 — category heterogeneity, done defensibly
- [ ] Build a **pre-registered** AI-exposure ranking of the seven categories from an
      external source, fixed before looking at outcomes. Do not derive it from our data.
- [ ] DiD: high- vs low-exposure differential break, with gig and quarter fixed effects.
- [ ] Run the full step-29 battery on every specification; report all four tests.
- [ ] Pre-AI placebo window (discharges the open todo item).
- [ ] Report bands everywhere; no hard category ranking unless it survives the battery —
      the ±5% adequacy discipline from §3.6 applies here too.

### Phase 3 — entry and dormancy, honestly labelled
- [ ] Entry rate and entry price by category, normalised by crawl intensity
      (`code/44-entry-price-series.py` already builds the entry series within one frame).
- [ ] Dormancy as the *only* available exit proxy, with the step-24 warning attached: the
      **raw dormancy ranking reverses sign for three of seven categories** under the ITS
      spec and must never be quoted raw.
- [ ] State plainly in the write-up that true exit is unmeasurable and why.

### Phase 4 — reach past 2024Q4 and check against the outside world
- [ ] **Specify the forward crawl.** This is already an open todo item ("respecify (a) as a
      live forward crawl on a fixed schedule"). A weekly/monthly re-fetch of a fixed gig
      cohort gives what the archive structurally cannot: a real exit hazard and a live
      2026 trailing edge. Needs a rate-limit and robots decision before any fetching.
- [ ] **External validation.** Fiverr Inc. is public and reports GMV, active buyers and
      spend-per-buyer quarterly. Nothing in this repo uses them. Compare our category-
      aggregated demand path to the reported series — it is the only independent check on
      whether the proxy tracks real transactions at all, and it costs one afternoon.

## 7. Decisions taken (2026-08-14)

1. **Causal from the start.** Not descriptive-first. The paper commits to identifying an AI
   effect on transaction volume, which means the identification apparatus is built before
   any outcome is examined rather than bolted on if the description looks interesting.
2. **A separate third paper.** Paper 2 stays the enlarged price-measurement paper. This gets
   its own frame, its own numbers table and its own test files. Nothing here feeds paper 1
   or paper 2, and the frozen-numbers checker still governs those.
3. **Forward crawl deferred.** Decide after Phase 0. Until then the study is archive-only
   and ends at 2024Q4.

## 8. What "causal from the start" changes — read before running anything

**It reverses the order of Phases 0 and 2's front half.** Phase 0 re-runs step 24, which
produces demand breaks *per category*. Once those are seen, an exposure ranking built
afterwards is not pre-registered in any meaningful sense — the reviewer's objection writes
itself, and it is the same objection that sank the elasticity table. So:

- [ ] **Lock the AI-exposure ranking of the seven categories BEFORE Phase 0 runs.** Sourced
      externally (task-level exposure measures in the existing literature — the O\*NET-style
      and LLM-exposure work already in `drafts/references.json` is the natural base), written
      to a dated, committed file with the rationale per category, and not revised afterwards.
- [ ] **Pre-register the specification in the same file**: outcome definition, break date(s),
      fixed effects, clustering, the placebo window, and the pass/fail rule for the step-29
      battery. Commit it before the first estimation run.
- [ ] Only then run Phase 0.

**It raises the bar on three things that were optional under a descriptive framing:**

- **Parallel trends** must be shown, not assumed — high- and low-exposure categories tracking
  each other pre-2022Q4. If they do not, the DiD is dead and the paper needs a different
  design (synthetic control on the low-exposure categories is the fallback).
- **Review-propensity drift** (§5) stops being a caveat and becomes a threat to identification:
  it only breaks the DiD if propensity drifted *differentially* by category, so that is the
  version of the test to run.
- **The 2024Q4 boundary is now a substantive limit on the claim**, not just a coverage note.
  The treatment period is 2022Q4–2024Q4, eight quarters. State the post-period length wherever
  the estimate appears.

**What does not change:** the step-29 battery still runs on every specification, and a null
is still a real result — a tightly-bounded null differential effect is a publishable causal
finding, not a failure.

## Decision Log

- 2026-08-14: Plan created. Q1/Q2/Q3 decomposition adopted so that "transactions" is never
  reported without saying which margin it refers to.
- 2026-08-14: Exit ruled out as archive-measurable on the existing `n_404 = 0` evidence
  rather than re-litigated; dormancy adopted as the labelled proxy.
- 2026-08-14: Balanced frame chosen over expanded/rule-B for the demand study — 242,468
  accrual observations against 22,967, and it spans 2018Q3–2024Q4 rather than 2024Q3+.
- 2026-08-14: Time-series regression on an AI score ruled out up front, on the step-29
  evidence; DiD on pre-registered exposure adopted instead.
- 2026-08-14 (user): **causal from the start**, **separate third paper**, **forward crawl
  deferred to after Phase 0**. Consequence recorded as §8 — a new Phase −1 now gates Phase 0,
  because Phase 0 reveals per-category outcomes and an exposure ranking built after seeing
  them is not pre-registered. Parallel trends becomes a required exhibit, and
  review-propensity drift must be tested for *differential* drift, not just drift.

- 2026-08-17 (user): **Exposure ranking anchored on Eloundou et al. (2023)**, not Felten
  AIOE and not both — Eloundou is LLM-specific and therefore matches the 2022Q4 break the
  study actually dates, whereas AIOE covers AI broadly and fits the pre-2022 period better.
  Sourced from the authors' public replication repo rather than transcribed, and vendored
  into `data/` so the ranking reproduces offline.
- 2026-08-17: **Human annotation chosen as primary over the GPT-4 annotation**, with the
  GPT-4 one kept as declared robustness. Reason: `dv_rating_*` is GPT-4 scoring its own
  labour-market reach, which is a circularity a reviewer will name, and the study should not
  depend on it. Consequence recorded immediately — the two annotators disagree on coding
  (rank 4 vs rank 1) and marketing (3 vs 5), so the primary contrast uses only the four
  categories they agree on and coding is reported separately.

- 2026-08-17: **Phase 0 result — the AI attribution is not identified, and the
  pre-registration is what established that rather than a reviewer.** Recorded as a decision
  because it redirects the study: the differential question moves to the synthetic-control
  fallback, and **Phase 1 becomes the critical path** ahead of Phase 2. The reason is that
  Phase 0's finding is platform-wide (all seven categories, including the two least exposed),
  and a platform-wide accrual fall is indistinguishable from review-propensity drift on
  present evidence. **Fiverr Inc.'s reported GMV is promoted with it**: an accrual fall the
  company's own books do not show would be close to proof of propensity drift, which makes
  Phase 4's external validation a test of the headline rather than a nice-to-have.
- 2026-08-17: **The −7.9% DiD estimate is recorded here as a near-miss, deliberately.** It
  had t = −4.14, a 95% CI of [−11.4, −4.2], and a realised MDE of ±3.96% that *meets* the
  project's ±5% adequacy standard. Everything about its surface presentation was publishable.
  It died on the trend horse race and the CPI-U placebo. Kept in the log so the next
  specification that looks this clean gets the same battery rather than the benefit of doubt.

## Progress

- 2026-08-17: Phase 0 ran. See the Phase 0 checklist above and the 2026-08-17 entry in
  `progress.md` for the full result. Headline: step 24's seven nulls were an artefact of
  power (MDE 4.7–9.4× tighter), all seven categories broke significantly, they broke
  *together*, and the AI-differential does not survive its own pre-registered tests.
- 2026-08-17: Phase −1 closed. Ranking built and locked, specification pre-registered, power
  computed pre-outcome (129,378 observations in the primary contrast). No outcome was
  estimated. **Phase 0 is now unblocked and needs no new data collection.**
- 2026-08-14: Feasibility measured before drafting — accrual observation counts per frame
  and per category-quarter, `review_count` coverage (95.5%) and monotonicity (0.58%
  negative deltas), and the post-2024Q4 collapse (7,774 → 1,605 → ~700/quarter).
  Confirmed no Fiverr Inc. financial data is used anywhere in the repo.
