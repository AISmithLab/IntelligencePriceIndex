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
- [ ] **D2. Reputation-adjusted band: publish the pair or not.** β(Δln reviews) = +0.103 (t 10.2) with quarter FE, ~41% of within-gig price growth. Reviews are cumulative *sales*, so adjusting is a bad control — raw is the upper bound, adjusted the lower. Decide pooled vs per-category β. Do **not** swap the headline.
- [ ] **D3. Published window: stays 2020Q1, or moves to 2018Q3.** GEKS runs back to 2018Q1; the pre-AI placebo is favourable but thin (matched gigs per adjacent pair: design 9–24, marketing 3–5, audio 2–4, translation 0). 2018Q3 is a hard floor — do not retry 2016.
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

- 2026-08-06: **D1 closed — keep `MIN_MATCH = 3`.** Swept 8 values × 7 categories × 2 segments before deciding, and the trade-off the decision was framed around turned out not to exist: raising k buys no precision anywhere and destroys it in the thin categories. D1 is therefore **decoupled** from the precision problem and split into D1b (adequacy criterion, the actual remedy) and D1c (the historical series that are not identified, a problem no band expresses). Phase 2 does not need a re-run on D1's account — the composite is robust across k=1…6.

- 2026-08-05: **Pilot published as a measurement paper; full-scale collection becomes paper 2** (user). Rationale: every margin measured converges on the same bound — price precision fails 6/7, demand and dormancy null at ±23–66%, DiD CI −15% to +88%, exit/entry unmeasurable by construction. The pilot cannot rank categories by AI impact on any margin, and claiming otherwise is the one thing that would sink the paper. It *can* deliver the instrument, the bounds, and the design requirements.
- 2026-08-05: **Phase 1 gates Phase 3.** Four open methods decisions each move every published figure; drafting §4 before they are settled guarantees a second rewrite.
- 2026-08-05: Plan created after a readiness audit found the prose four and a half months stale and the abstract's every substantive claim retracted or superseded.

## Progress

- 2026-08-06: **Phase 1 D1 done.** `code/26-minmatch-sensitivity.py` built and run (py_compile clean, exit 0). Decision: keep k=3. Two by-products: the R5 sensitivity table §3 needs, and the discovery that the historical coding/translation/audio levels are not identified (new D1c). Also caught two reading traps in the sweep's own output — a shifting terminal quarter that makes the level column compare different quarters, and ±0.0% cells that are degeneracy rather than precision — both now marked in the script's output.

- 2026-08-05: Plan created. Readiness audit done: draft section dates, 85 `[CITE-]` / 4 `<!-- FIGURE -->` placeholders, test-layer status (method 5 FAIL + 1 BLOCKED, model-paper 10 BLOCKED, 7 files never reviewed), and the abstract-vs-current-results table above. `code/25-hedonic-regression.py` re-run and confirmed byte-identical to `scratchpad/hedonic.out`.
