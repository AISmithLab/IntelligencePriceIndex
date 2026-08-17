# Pre-registration: AI exposure and transaction volume on Fiverr

**Status:** LOCKED
**Registered:** 2026-08-17
**Parent plan:** `plans/active/transaction-volume.md` (Phase −1)
**Gates:** Phase 0. Nothing in the study may be estimated until this file is committed.

This file fixes the exposure ranking and the estimating specification **before any
outcome is examined**. It exists because the study is causal from the start (user
decision, 2026-08-14), and because step 29 retracted this project's elasticity table
for precisely the failure this document is designed to prevent: a design chosen after
the researcher had seen which categories moved.

Everything below was written without computing a single demand outcome on the
balanced frame. What *was* computed first is sample sizes (§4), which are not
outcomes. Revisions after Phase 0 runs are permitted only as **declared deviations**,
appended to §9 with a date and a reason, never as silent edits.

---

## 1. Hypothesis

Diffusion of general-purpose LLMs after 2022Q4 reduced transaction volume on Fiverr
**differentially more** in categories whose task content is more exposed to LLMs.

The estimand is the **differential** break, not the level break. A platform-wide fall
in transactions is not evidence for this hypothesis — it is absorbed by the quarter
fixed effects, along with seasonality, Fiverr fee and policy changes, and the panel's
average ageing profile.

**This addresses Q1 only** (do surviving gigs sell less), in the decomposition of the
parent plan §1. It is not an answer to "did platform-wide volume fall," which is Q3
and is not measurable from the crawl.

## 2. Exposure ranking — LOCKED

**Source:** Eloundou, Manning, Mishkin & Rock (2023/2024), *GPTs are GPTs: Labor
market impact potential of LLMs*, Science 384(6702) — `eloundou-2023` in
`drafts/references.json`. Occupation-level exposure taken from the authors' public
replication repository (`openai/GPTs-are-GPTs`, `data/occ_level.csv`), vendored to
`data/eloundou-2023-occ-level.csv` (923 O\*NET-SOC occupations) so the ranking
reproduces offline and cannot drift.

**Measure.** `human_rating_beta` is **primary**; `dv_rating_beta` is the declared
**robustness** measure. β is the paper's headline threshold — direct LLM exposure plus
exposure through LLM-powered software, which is the right notion for a freelance
deliverable. The *human* annotation is primary because the GPT-4 annotation lets a
model score its own labour-market reach; that circularity is an obvious reviewer
target and we decline to depend on it.

**Mapping.** Fiverr category → O\*NET-SOC occupations by task content, equally
weighted. Equal weights because no employment weights exist for Fiverr gigs and
inventing them is a researcher degree of freedom. Built by `code/45-exposure-ranking.py`
→ `data/exposure-ranking.csv`.

| rank | category | `human_rating_beta` | rank (dv) | `dv_rating_beta` | occupations mapped |
|---:|---|---:|---:|---:|---|
| 1 | **translation** | **0.840** | 2 | 0.880 | Interpreters and Translators |
| 2 | **writing** | **0.686** | 3 | 0.815 | Writers and Authors; Poets, Lyricists and Creative Writers; Editors; Technical Writers; Proofreaders and Copy Markers |
| 3 | marketing | 0.624 | **5** | 0.547 | Market Research Analysts; Search Marketing Strategists; PR Specialists |
| 4 | coding | 0.588 | **1** | 0.917 | Computer Programmers; Software Developers; Web Developers |
| 5 | design | 0.508 | 4 | 0.611 | Graphic Designers; Art Directors; Web and Digital Interface Designers |
| 6 | **video** | **0.402** | 7 | 0.486 | Film and Video Editors; Camera Operators; SFX Artists and Animators; Producers and Directors |
| 7 | **audio** | **0.248** | 6 | 0.495 | Musicians and Singers; Music Directors and Composers; Sound Engineering Technicians; Audio and Video Technicians |

**The two annotators disagree, and the disagreement is declared here rather than
discovered later.** GPT-4 ranks **coding** most exposed of the seven (0.917); human
annotators rank it fourth (0.588). Marketing moves the other way (3rd → 5th). Coding
is therefore **quarantined from the primary contrast** — see §3.

**Pre-registered assignment:**

- **HIGH** = {translation, writing} — top-2 on the human measure and top-3 on the GPT-4 measure.
- **LOW** = {video, audio} — bottom-2 on both.
- **DISPUTED / MID** = {marketing, coding, design} — reported separately, never pooled into either arm.

Both annotators agree on the four categories that constitute the contrast. That
agreement is the reason the contrast is defined this way and not by a median split.

**Declared mapping sensitivity.** `15-1255.00` (Web and Digital Interface Designers)
is design by title and coding by task content. It is IN the primary mapping because
Fiverr's design category does carry web/UI gigs. Design's rank is the one most movable
by a single mapping call, so `data/exposure-ranking.csv` carries the drop-it variant
(`exposure_primary_sens`) up front. Design is in the MID bin either way, so this
cannot move the primary contrast — which is why it is a footnote and not a threat.

## 3. Specification — LOCKED

**Frame.** `data/pilot/balanced-prices.csv` joined to `data/pilot/balanced-manifest-1200.tsv`
for category, filtered through `code/gigfilter.py` (`is_gig`). No survivor filter —
rule B selects on ≥2 distinct quarters anywhere in the window.

**Outcome.** Within-gig review accrual per quarter: `Δ review_count` between
consecutive observed gig-quarters, where the within-quarter level is collapsed with
`max()` (the count is cumulative and weakly increasing, so max is the end-of-quarter
level). Modelled in logs as `ln(1 + accrual / quarters_spanned)`. This is step 24's
M1 outcome and is unchanged, so the two studies are comparable by construction.

**Window.** 2018Q1 – **2024Q4**. The trailing edge is excluded on the pre-existing
measurement that accrual observations per quarter collapse 7,774 (2024Q4) → 1,605
(2025Q1) → 598–847 thereafter. This is a hard boundary, not a robustness choice.

**Break date.** **2022Q4** — ChatGPT, 2022-11-30. Single pre-specified break. No
data-driven break search; if one is ever run it is exploratory and labelled as such.

**Treatment period.** 2022Q4 – 2024Q4, **eight quarters**. Stated wherever the
estimate appears.

**Estimating equation.**

```
ln(1 + accrual_igt) = α_i + δ_t + β · (HIGH_i × POST_t) + ε_igt
```

with **gig fixed effects** α_i and **quarter fixed effects** δ_t. β is the estimand.
Sample restricted to HIGH ∪ LOW.

**Clustering.** Standard errors clustered on **gig**. Non-negotiable: step 22's β was
published with an unclustered SE and the gig-clustered version was 1.93× larger
(t 10.19 → 5.26). A second occurrence of that error in this project is not acceptable.
Two-way gig × quarter clustering is reported alongside as a robustness column.

**Secondary specification.** Continuous exposure — β on `exposure_primary` × POST
across all seven categories, which uses the full ranking rather than the four-category
contrast. Declared secondary, not primary, because it depends on cardinal exposure
values and on the two categories the annotators disagree about.

**Age/period/cohort.** Age ≡ period − cohort under gig fixed effects, so the quarter
path contains the panel's ageing profile and **cannot be read as demand**. Only the
break coefficient is reported as a demand result. Two specifications bracketing the
APC problem, as step 24's M1 already does.

## 4. Power — computed pre-outcome

Accrual observations by category on the balanced frame (gigs with ≥2 observed quarters,
2018+):

| category | gigs ≥2q | accrual obs | arm |
|---|---:|---:|---|
| design | 3,814 | 47,251 | MID |
| writing | 3,950 | 40,038 | **HIGH** |
| coding | 5,314 | 37,254 | MID (disputed) |
| video | 4,855 | 36,485 | **LOW** |
| audio | 5,650 | 31,156 | **LOW** |
| marketing | 7,226 | 28,585 | MID |
| translation | 5,527 | 21,699 | **HIGH** |
| **total** | **36,336** | **242,468** | |

**Primary contrast: 61,737 (HIGH) + 67,641 (LOW) = 129,378 accrual observations**,
against step 24's 10,275 across all seven categories. Step 24's per-category MDE ran
±23% (coding) to ±66% (translation); on 1/√n the per-category figures become roughly
±4.7% to ±14%, and the pooled four-category contrast is tighter still.

**Adequacy rule, pre-registered:** the project's existing **±5% at 95%** standard
(§3.6 of the paper) applies. The realised MDE for the primary contrast is computed
and reported in Phase 0 **before** β is interpreted. If the MDE exceeds ±5%, the
result is reported as a bounded null and not as a ranking.

## 5. Parallel trends — required exhibit, not an assumption

- Event-study plot of β by quarter, 2018Q1–2024Q4, with 2022Q3 as the omitted period.
- **Pass rule, fixed in advance:** no pre-period (2018Q1–2022Q3) interaction
  coefficient significant at 5% after clustering, and no monotone pre-trend in the
  point estimates. Both conditions, not either.
- **If it fails, the DiD is dead** and is reported as dead. The declared fallback is
  **synthetic control**, constructing a weighted combination of the LOW categories to
  match each HIGH category's pre-2022Q4 accrual path. No third fallback is authorised
  here; if synthetic control also fails, the study reverts to descriptive reporting
  with bands and says so.

## 6. The step-29 battery — runs on every specification

Every reported estimate carries all four. This is the battery that retracted the
elasticity table, and it is applied here *before* anything is written down, not after.

1. **First differences.** The relationship must survive differencing. Step 29's
   elasticity did not (t = 0.26, −0.02, 0.48, 2.24, −0.34, 0.20).
2. **Linear-trend horse race.** A linear time trend must not fit better than the
   treatment indicator. It beat the AI score in all six categories in step 29.
3. **AI-free placebo series.** CPI-U — which has no AI content — substituted for the
   treatment. It must not reproduce the effect. It fit at least as well in five of six
   categories in step 29.
4. **Newey–West** standard errors reported alongside clustered ones on any
   time-series-shaped specification.

**Pass/fail rule:** a finding is reportable as causal only if it survives **all four**.
Surviving three is a descriptive result and is labelled as one.

## 7. Placebo window

**2018Q3–2019Q4**, pre-AI. The same HIGH × POST specification with a false break at
**2019Q2**. Must return a null. This discharges the long-standing "publish a pre-AI
placebo window" item in `plans/todo.md`.

Known limitation, stated in advance: the pre-period is thin in the *price* panel
(matched gigs per adjacent pair: design 9–24, marketing 3–5, audio 2–4, translation 0).
The accrual panel is far denser, so this placebo is more informative here than the
price-side version — but the 2018 quarters are still the frame's thinnest and the
placebo is reported with its n.

## 8. Threats, with the pre-committed response

| Threat | Response, fixed now |
|---|---|
| **Differential review-propensity drift** | The only confound with no current answer, and under a causal frame it is a threat to identification rather than a caveat. It breaks the DiD only if propensity drifted *differentially* by exposure arm — that is the version tested, in Phase 1, **before** β is interpreted. If untestable, reported as a signed bound. |
| **Exit is unmeasurable** | `n_404 = 0` across 509,339 captures. Dormancy is the labelled proxy and the word "exit" is not used for it. Stated in the write-up, not buried. |
| **Crawl intensity** | Accrual is normalised by capture intensity per category-month, as step 24's M3 does. |
| **Top-coding** | `review_count` is audited for ceiling artefacts ("1k+" display) before estimation; censored or modelled if found. |
| **Composition** | Within-gig only. The between/within split is reported. |

## 9. Declared deviations

- **2026-08-17, clarification, no substantive change.** §3 said "treatment period 2022Q4
  – 2024Q4, **eight quarters**", which is internally loose: 2022Q4–2024Q4 inclusive is
  nine quarters. The implementation (`code/46-balanced-demand.py`) sets
  `POST = 1` for quarters *strictly after* 2022Q4, i.e. **2023Q1–2024Q4 = eight
  quarters**, which matches the stated length and matches step 24's convention so the
  two studies remain comparable. ChatGPT shipped 2022-11-30, so 2022Q4 is
  predominantly a pre-treatment quarter and belongs in the control period. Recorded
  here because the ambiguity was in the registered text, not because the estimate moved.

- **2026-08-17, DECLARED DEVIATION — expanded synthetic-control donor pool.** §5 specified
  synthetic control on "the LOW categories," which is two donors and therefore a
  one-parameter weight. `code/48-category-impact.py` runs that registered form as **C3**
  and additionally reports an expanded pool of LOW + MID (five donors) as **C4**, plus
  in-space placebos over all seven categories as **C5**. Reason: two donors cannot match a
  pre-period path well enough for the pre-RMSPE to mean anything, and inference needs a
  placebo distribution. C4 is reported *alongside* C3, never instead of it, and both are
  shown for both HIGH categories. **The deviation does not rescue the finding — it makes it
  worse**, so it cannot be read as specification-searching toward a result: translation's
  gap moves from −2.2% (C3) to **+1.4%, wrong-signed** (C4).

- **2026-08-17, no deviation — the design failed its own gate and was reported as
  failing.** §5's parallel-trends gate returned FAIL and §6's battery failed two of four
  tests. Per §5 and §6 the DiD is therefore reported as dead rather than published, and
  the fallback is synthetic control. Reporting a pre-committed failure is the
  pre-registration working, not a deviation from it.

## 10. What counts as a result

A **tightly-bounded null differential effect is a publishable causal finding**, not a
failure. If HIGH and LOW categories broke identically at 2022Q4 to within ±5%, that is
a substantive statement about the first two years of LLM diffusion on a large
freelance marketplace, and it is the study's headline. This is recorded before the
estimate is seen so that a null cannot later be reframed as a disappointment.

---

**Commit this file before running `code/24-margin-diagnostics.py` on the balanced frame.**
