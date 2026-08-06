# Tests: Conclusion

**Draft file:** drafts/sections/conclusion.md
**Last reviewed:** 2026-08-06

Rewritten from scratch 2026-08-06. The previous version's three headline findings were the 312 peak, the 21% 2025 reversal, and the −0.49-to-+1.10 elasticity range — all three retracted.

## Reviewer Simulation

| # | Critique | Severity | Status | Response |
|---|----------|----------|--------|----------|
| R1 | "The conclusion's three findings are all retracted." | **blocking** | **PASS (rewritten)** | The 312 peak (retired chained series), the 2025 reversal (`hire/*` artifact) and the elasticity range (spurious regression) are all gone. The rewrite opens by stating the original goal was not achieved, which is the honest frame. |
| R2 | "Opening with 'we did not obtain it' is a strange way to conclude a paper." | minor | **PASS (deliberate)** | It is followed immediately by what *was* obtained — instrument, series, and an account of why the original question is out of reach. The structure mirrors the abstract and §1 so the paper's scope is consistent across all three. |
| R3 | "Does the conclusion quote anything the body does not support?" | major | **PASS** | Every figure traces to `data/pilot/paper-numbers.md` or to a numbered result in §3–§4: +40.7% real / +78.4% nominal / ±3.7% / CPI-U +26.8%; +7.7% per doubling; +39.7% to +79.0% band; ±23% to ±66% MDEs; −14.8% to +87.6% DiD interval; ρ = +0.314. The matched-gig requirement was restated 2026-08-06 to the finite-population-corrected values of §3.6 (≈900 writing, 1,100 design, 1,600 video, 7,400 coding) in place of the old 850–2,500 range. No new numbers are introduced. |
| R4 | "Retracting a prior result in the conclusion reads as self-flagellation." | minor | **PASS** | One paragraph, stating the diagnostics rather than the apology, and justified by the transferability argument ("the specification is an obvious one to try and produces a memorable number"). §5.3 carries the longer version. |
| R5 | "The 'three findings that will outlast the series' — are they really findings, or lessons?" | minor | **PASS** | All three are measured: the parsing defect with its 26-point real effect, the non-identification with its +129% swing against a ±61% band and the decomposition proving the single mechanism, and the hedonic reversal with both coefficients. They are results about method, not reflections. |
| R6 | "The final line still gestures at the price of intelligence." | minor | **PASS** | It does so by explicit disclaimer — "This paper does not report it" — and then states what is reported instead. The rhetorical callback survives without a claim attached. |
| R7 | "Does the conclusion state what would resolve the question?" | major | **PASS** | Its penultimate paragraph gives all three: the 850–2,500 matched-gig target from the measured $1/\sqrt{n}$ curve, the two collection-design changes, and the observation that the DiD design passing its identifying test here would approach ±5% MDE at the density the recent crawl already achieves. |

## User Requirements

| # | Instruction | Date | Status | Location |
|---|-------------|------|--------|----------|
| U1 | AI must not be presented as the sole or identified driver | 2026-07-30 | **PASS** | The conclusion states the residual is not attributable and lists the four margins that failed to attribute it. |
| U2 | Publish the pilot as a measurement paper; defer the causal claim | 2026-08-05 | **PASS** | Opening paragraph and closing paragraph both frame the contribution as instrument, bounds and design requirements. |
