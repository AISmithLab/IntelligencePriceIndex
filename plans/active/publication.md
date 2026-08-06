# Plan: Take the pilot to submission as a measurement paper

**Status:** active
**Created:** 2026-08-05
**Goal:** Rewrite the paper around the corrected index and the measured bounds, and submit the pilot as a measurement contribution — not as a causal AI-impact claim.

## Scope

**In scope.** Settling the four number-moving methods decisions, re-running the pipeline once to freeze the numbers, rewriting every prose section from the current results, filling figures and citations, and driving all three test layers to PASS/N/A.

**Out of scope.** The full-scale collection (48,643 sellers) and the gig-level exposure DiD. Both stay in Backlog and become paper 2. This plan deliberately does **not** attempt an identified AI effect — see the framing decision below.

**Framing decision (user, 2026-08-05): pilot as measurement paper, full-scale as a follow-on.**
The contribution is the *instrument and its bounds*: a matched-model GEKS-Jevons price index for cognitive-labour services built from web archives, plus honest measurement of what a pilot-scale archive crawl can and cannot resolve. The negative results are part of the contribution, not an embarrassment to be hidden:
- the cross-section/within-gig reversal on volume (a hedonic design reaches the opposite conclusion from a matched-model one);
- price precision failing in six of seven categories against a stated criterion;
- demand and dormancy null with ±23–66% bounds;
- exit and entry unmeasurable by crawl construction — with the design requirements that would fix it.

## The core problem this plan solves

The analysis is four and a half months ahead of the writing. Every prose section except `method.md` and `faq.md` is dated **2026-03-23**, and the abstract is not stale — it is **retracted**:

| Abstract currently claims | Current state |
|---|---|
| composite peaked at 312 (base 2019Q1=100), declined 21% in early 2025 | that is the naive chained series, removed from the site 2026-07-27; published GEKS composite is **+78.4% nominal / +40.7% real** over 2020Q1→2026Q1, and the post-2024Q3 decline was the `hire/*` artifact |
| elasticities −0.49 audio to +1.10 design | `panel-elasticity.csv` is slated for retirement — it returns design as most AI-elastic when design is flattest in real terms |
| "9 service categories … 2017 to 2025" | 7 categories; **2018Q3 is a hard floor**; data runs to 2026Q1 |
| AI as the driver | **descriptive-first**, decided 2026-07-30 |

The abstract must be **written from scratch**, not edited.

## Steps

### Phase 1 — settle the number-moving decisions (do this first; writing before it means writing twice)

- [x] **D1. `MIN_MATCH`** — **MEASURED AND DECIDED 2026-08-06** (`code/26-minmatch-sensitivity.py`, output `scratchpad/minmatch-sensitivity.out`). **Keep `MIN_MATCH = 3`; it is not the precision lever it was assumed to be.** The coverage-for-precision trade-off does not exist: raising k buys nothing in the five dense categories (flat to within 0.2pp across k=1…10) and **destroys** precision in the thin ones (audio ±11.3% at k=1 → ±34.1% at k=6). Mechanism: `MIN_MATCH` deletes *comparisons*, not gigs, and GEKS averages over link paths — coding's historical terminal quarter has 8 supporting paths at k=3 and **one** at k=4, which is why its level jumps 312.8 → 717.7. Lowering to 1 helps only audio and translation and lets a bilateral rest on a single gig — an easy reviewer target for a narrow gain. **The headline composite is robust across k=1…6 (+76.4% to +78.4%), so Phase 2 needs no re-run on this account.** Closes `method.test.md` R5. **The thin-category problem is real but belongs to the adequacy criterion (bands, no ranking claims), not here** — split out as D1b below.

- [ ] **D1b. State the ±5% adequacy criterion in §3** (split from D1, 2026-08-06 — the two were bundled on the false premise that `MIN_MATCH` could fix precision). Needs the rule, the six-of-seven failure at 2026Q1, the composite passing at ±3.7%, and the precision-vs-n curve. Closes `method.test.md` R12. Site half already shipped 2026-08-05.

- [ ] **D1c. Decide how to publish the historical coding, translation and audio levels** (new, 2026-08-06 — surfaced by the D1 sweep). These are **not identified**, which is a stronger statement than imprecise: coding's historical level swings +129% on a one-step `MIN_MATCH` change, far outside its ±61% band, because the terminal quarter rests on a single link path. A confidence band does not convey this. Options: suppress the historical segment for these categories, publish with an explicit not-identified marking, or report the `MIN_MATCH` range as the honest interval. The recent segment is unaffected (five of seven categories do not move at all).
- [x] **D2. Reputation-adjusted band** — **MEASURED AND DECIDED 2026-08-06** (`code/27-reputation-band.py`, output `scratchpad/reputation-band.out`). **Publish the pair as a band; β is POOLED; raw stays the headline.** Composite 2020Q1→2026Q1: **raw +79.0%, adjusted +39.7%**, width 39.3 points. Pooled β = **+0.1068 (se 0.0201, t 5.32)**, gig-clustered, on the production cells. Pooling is forced, not preferred: per category, **audio (−0.089) and translation (−0.080) are wrong-signed**, so adjusting them with their own β would *raise* their index. Two things to carry into §3: step 22's **t = 10.19 was unclustered and should be ≈5.3** (restate in `progress.md` 2026-07-29, `plans/todo.md`, `tests/findings.test.md` R1), and the band's **floor is soft** — on β's 95% CI the lower bound ranges ~+50% to +28%, so it must not be quoted as a single number. Per-category β spread (marketing +0.206 to design +0.075) means pooling is a stated assumption, not a formality.
- [x] **D3. Published window** — **MEASURED AND DECIDED 2026-08-06** (`code/28-window-choice.py`, output `scratchpad/window-choice.out`). **Keep 2020Q1; publish 2018Q3–2020Q1 as a separate pre-AI exhibit, not as part of the headline series.** Nothing is gained (composite 2020Q1→2026Q1 reads +74.3% to +78.4% nominal across five window starts, inside its own ±3.7% band) and precision is lost in **four of seven** categories, by up to 4× (design ±23.3% → ±93.7%, writing ±38.1% → ±103.2%, marketing ±86.5% → ±182.6%). Translation gains nothing — it bases at 2019Q4 under every window ≤2019Q3 — and audio's pre-period chain is broken at three adjacent pairs (2 matched gigs each, below `MIN_MATCH`). The extended series is also **more** fragile to `MIN_MATCH`: at k=4 five of seven categories change terminal quarter against three on 2020Q1. **2018Q3 remains a hard floor; do not retry 2016.** Feeds D1c below — see D3b.

- [ ] **D3b. The per-category historical growth is not window-invariant, and it is the same defect as D1c** (new, 2026-08-06). Over the **identical span** 2020Q1→terminal, audio reads **+103.9%** on the 2018Q3 window and **+258.7%** on the 2020Q1 window; spreads across five windows run audio 76.0%, marketing 42.1%, design 27.6%, writing 26.3%, coding 21.3%, video 16.4%, translation 1.7%. **Mechanism decomposed and proven:** the gig-set channel contributes nothing (max |Δ lnP| over shared bilaterals = **0.0000** in all seven categories), and the link-set channel contributes all of it (growth recomputed on the shared link set is **exactly identical** across windows — audio 142.0% under both, a figure neither published number matches). Shared link sets are tiny: |L\*| = 2–5. **So `MIN_MATCH` (D1c), the base quarter (2026-08-03) and the window (D3) are one defect, not three** — each perturbs how many link paths support a quarter. §3 should name the mechanism once and mark the historical per-category series on it; D1c's marking decision should be taken to cover this too. **The composite is exempt and the reason is verifiable:** the splice truncates the historical leg at 2024Q3, and that leg's spread is only design 4.0% / video 4.5% / writing 10.7%, with design carrying ~71% of the review weight.
- [ ] **D4. Does the chained series / elasticity table survive in the paper at all?** TD1 means the +217.7% vs +44.6% gap mixes genuine chain drift with a coding defect. Options: fix the estimator and requote, state it as an upper bound, or cut the comparison. Closes `method.test.md` R9. Interacts with retiring `panel-elasticity.csv`.

### Phase 2 — rebuild once, freeze the numbers

- [ ] Re-run 12 → 14 → 19 → 21 → 23 → 18 under the D1–D4 choices; refresh `docs/data.json` and the site.
- [ ] Produce a single frozen numbers table (composite + 7 categories, nominal and real, with ±95%) that every draft section quotes from. No section computes its own figures.

### Phase 3 — rewrite the prose (the bulk of the work)

- [ ] **§3 Methods** — add the deflation method (CPI-U `CPIAUCSL`, the interpolated October 2025 month, why the bootstrap SEs are unchanged); state the ±5% criterion and add the precision-vs-n curve as a methods exhibit; report **matched gigs per bilateral** everywhere sample size is claimed, not panel gigs; fix the 2019Q1/2020Q1 base inconsistency (R8); recompute or restate the unreproducible "10.9% filled" figure.
- [ ] **§3 or §5 — the cross-section/within-gig reversal as the design justification.** b(ln reviews) = +0.022 (t 1.64) across sellers vs **+0.133 (t 7.87)** within a gig, 6.1×, reproducing step 22's +0.103 on a different cut. A hedonic cross-section concludes experience is unpriced; it is priced at ~+10% per doubling. This is a *demonstrated* argument for the matched-model design where the draft currently asserts one. Source: `code/25-hedonic-regression.py`.
- [ ] **§4 Findings** — rewrite on the corrected index. Real as headline, nominal alongside. Kill the "prices falling since 2024Q3" narrative (it was the `hire/*` artifact) and the 2026-07-07 elasticity table.
- [ ] **§ Limitations** — the margin bounds (demand and dormancy null, MDE ±23–66%; the raw dormancy ranking reverses sign for three of seven under trend/composition adjustment, so it must not be quoted raw); survivorship and the flat entry-price gap; exit/entry unmeasurable by crawl design, with the two forward design requirements.
- [ ] **Abstract, §1 Introduction, §6 Discussion, Conclusion** — write from scratch, descriptive-first. AI as one candidate among *measured* rivals (reputation treadmill, general inflation, platform composition, survivorship). Closes `findings.test.md` U1.
- [ ] **Re-mirror `drafts/sections/faq.md`** from the live `docs/faq.html` (stamped 2026-07-12, marked OUT OF SYNC 2026-07-31).

### Phase 4 — apparatus

- [ ] **4 figures** — IPI time series with bands, category panels, precision-vs-n curve, cross-section-vs-within-gig contrast. Replace the `<!-- FIGURE -->` placeholders in `findings.md`.
- [ ] **85 `[CITE-]` placeholders**, 68 of them in `related-work.md`. Reference class is online-price measurement — Cavallo & Rigobon (BPP), Cavallo (2017), the ILO CPI Manual, BLS cell-suppression practice.
- [ ] **Test files to PASS/N/A.** `method.test.md` 5 FAIL + 1 BLOCKED; `model-paper.test.md` 10 BLOCKED; seven section test files never reviewed (`Last reviewed: —`). Note B6 (validation against GPTs-are-GPTs / Anthropic index) is achievable at pilot scale as a *correlation* exhibit and should not be deferred to paper 2.
- [ ] Render `drafts/render.py` → dated HTML.

## Known defects to fix while passing through

- [ ] **`tests/method.test.md` R12 carries the superseded scope.** It names only audio (±13.9%) and translation (±29.2%) as failing the ±5% rule. The corrected second pass the same day found **six of seven fail at 2026Q1** — translation ±29.2%, coding ±17.1%, audio ±13.9%, video ±11.9%, writing ±8.3%, marketing ±7.7%; only design (±4.8%) passes, and the composite passes at ±3.7% because design carries ~71% of the review weight. Coding is worse than audio and is not mentioned. Restate R12.
- [ ] **`rating` 10-point scale bug** — 217 historical rows in (5, 10]. Does not move the hedonic result, but any future row-level use of `rating` is wrong. Fix in extraction or normalise in `gigfilter.py`.

## Decision Log

- 2026-08-06: **D3 closed — the published window stays 2020Q1**, and the pre-AI period becomes a separate exhibit rather than part of the headline series. Extending to 2018Q3 moves the composite by less than its own band while degrading per-category precision in four of seven categories and increasing fragility to `MIN_MATCH`. The decision was easy; the by-product was not. Prepending quarters moves the **published per-category growth over an unchanged span** by up to 76% (audio), and decomposing it showed the cause is entirely the GEKS link set, not the gig set. That makes D1c, the 2026-08-03 base-quarter swing and D3 one mechanism rather than three findings, and it is the single most important thing §3 has to explain about the historical segment.

- 2026-08-06: **D2 closed — publish raw and reputation-adjusted as a band (+79.0% / +39.7%), with a pooled β.** Per-category β is wrong-signed in two of seven categories, which rules out the per-category variant on interpretability rather than on precision. Also found that step 22's β t-statistic was inflated ~1.9× by unclustered SEs, and that the band's floor is soft across β's own confidence interval — both must be stated in §3 rather than presented as a single adjusted series.

- 2026-08-06: **D1 closed — keep `MIN_MATCH = 3`.** Swept 8 values × 7 categories × 2 segments before deciding, and the trade-off the decision was framed around turned out not to exist: raising k buys no precision anywhere and destroys it in the thin categories. D1 is therefore **decoupled** from the precision problem and split into D1b (adequacy criterion, the actual remedy) and D1c (the historical series that are not identified, a problem no band expresses). Phase 2 does not need a re-run on D1's account — the composite is robust across k=1…6.

- 2026-08-05: **Pilot published as a measurement paper; full-scale collection becomes paper 2** (user). Rationale: every margin measured converges on the same bound — price precision fails 6/7, demand and dormancy null at ±23–66%, DiD CI −15% to +88%, exit/entry unmeasurable by construction. The pilot cannot rank categories by AI impact on any margin, and claiming otherwise is the one thing that would sink the paper. It *can* deliver the instrument, the bounds, and the design requirements.
- 2026-08-05: **Phase 1 gates Phase 3.** Four open methods decisions each move every published figure; drafting §4 before they are settled guarantees a second rewrite.
- 2026-08-05: Plan created after a readiness audit found the prose four and a half months stale and the abstract's every substantive claim retracted or superseded.

## Progress

- 2026-08-06: **Phase 1 D3 done.** `code/28-window-choice.py` built and run (py_compile clean, exit 0, 42s; piloted on two categories first). Decision: keep 2020Q1. Two run-time self-checks are built in — the production window reproduces the shipped GEKS CSV to 0.005 index points, and the local re-basing helper reproduces `tpd.chain_category` exactly — so the alternative-window numbers are the production pipeline with one argument changed. By-products: the window-invariance failure and its decomposition (new D3b), a demonstration that the 2019Q1 window's anomalies are a spike quarter with the sign flipping exactly as the mechanism predicts, a verified explanation for why the composite is exempt (the splice truncates at 2024Q3), and a single-series pre/post-2022Q4 placebo in which post-period annualised growth exceeds pre in all seven categories — with the caveat that its pre-leg is cut at 2022Q4 and so is **not** the same statistic as the 2018Q3–2019Q4 figures in `plans/todo.md`.

- 2026-08-06: **Phase 1 D2 done.** `code/27-reputation-band.py` built and run (py_compile clean, exit 0). Band decided; pooled β forced by two wrong-signed category betas. By-products: step 22's unclustered-SE defect (t 10.19 → 5.26, needs restating in three places), a β-sensitivity curve for §3, and an in-script run-time check that restricting to review-carrying cells does not itself move the index (≤1.7% in every category). Corrected an error of my own mid-build — I had flagged Test B2's magnitudes as unquotable on a quarter mismatch; they agree with the published index.

- 2026-08-06: **Phase 1 D1 done.** `code/26-minmatch-sensitivity.py` built and run (py_compile clean, exit 0). Decision: keep k=3. Two by-products: the R5 sensitivity table §3 needs, and the discovery that the historical coding/translation/audio levels are not identified (new D1c). Also caught two reading traps in the sweep's own output — a shifting terminal quarter that makes the level column compare different quarters, and ±0.0% cells that are degeneracy rather than precision — both now marked in the script's output.

- 2026-08-05: Plan created. Readiness audit done: draft section dates, 85 `[CITE-]` / 4 `<!-- FIGURE -->` placeholders, test-layer status (method 5 FAIL + 1 BLOCKED, model-paper 10 BLOCKED, 7 files never reviewed), and the abstract-vs-current-results table above. `code/25-hedonic-regression.py` re-run and confirmed byte-identical to `scratchpad/hedonic.out`.
