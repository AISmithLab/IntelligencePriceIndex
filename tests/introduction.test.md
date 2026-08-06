# Tests: Introduction

**Draft file:** drafts/sections/introduction.md
**Last reviewed:** 2026-08-06

Rewritten from scratch 2026-08-06. The previous version opened by asserting AI as "the most powerful deflationary force… since the word processor" and organised its contribution around the price elasticity of intelligence, which §3.9 now retracts.

## Reviewer Simulation

| # | Critique | Severity | Status | Response |
|---|----------|----------|--------|----------|
| R1 | "The introduction asserts AI's deflationary power in its first line and then reports a price *rise*." | **blocking** | **PASS (rewritten)** | The opening assertion is gone. The introduction now opens on the measurement gap — exposure indices are judgments, platform studies are aggregates, a price index is missing — and states the finding (a real rise) without a deflation frame. |
| R2 | "You changed your research question mid-project. Say so." | major | **PASS** | Stated directly: "Our contribution is the instrument and its bounds, not a causal claim about AI… this is a change of ambition from where this project began, and the reason for the change is itself a result." The retraction is signposted to §3.9 in the introduction rather than left as a surprise. |
| R3 | "Why is a pilot-scale paper with mostly negative results worth publishing?" | **blocking** | **PASS** | Answered in its own subsection ("Why this is worth publishing at pilot scale") with three concrete deliverables: a measured $1/\sqrt{n}$ requirement of 850–2,500 matched gigs per category, two crawl-design changes that are impossible to retrofit, and an identified DiD design that fails on power alone at a density the recent crawl already achieves. A reviewer can disagree with the judgment but not with its being made explicitly. |
| R4 | "The CPI analogy is decorative." | minor | **PASS** | The introduction states the analogy is "methodological rather than rhetorical" and names the shared problems (matching items across periods, quality adjustment, item churn, thin cells), each of which the paper actually confronts in §3.4, §3.6 and §6.5. |
| R5 | "Four numbered findings, three of which are about your own method rather than the market." | minor | **PASS (deliberate)** | This is a measurement paper, and the introduction says so before the list. The methodological findings (the hedonic reversal, the link-path identification failure, the parsing defect) are the transferable content; §5.3 argues that case at length. |
| R6 | "Does the introduction overstate the precision of its one positive result?" | major | **PASS** | The +40.7% real figure appears with its band (±3.7%) and with CPI-U alongside, and the next paragraph immediately subtracts inflation and reputation and states the residual "is not separately identified." |
| R7 | "You claim the DiD 'passes its parallel-trends test' — that is a headline claim for a null result." | major | **PASS** | The claim is stated with its numbers (pre-period β = −0.0082, se 0.0093, insignificant event-study pre-years) and immediately paired with the interval that makes it useless in practice (−14.8% to +87.6%). The introduction presents it as a *design* result, not an effect estimate, and §4.7 repeats the framing. |

## User Requirements

| # | Instruction | Date | Status | Location |
|---|-------------|------|--------|----------|
| U1 | Reframe descriptive-first; AI as one candidate among measured rivals | 2026-07-30 | **PASS** | "What we find" subsection names inflation and reputation as measured rivals and states the residual is not identified. No causal language survives. |
| U2 | Publish the pilot as a measurement paper | 2026-08-05 | **PASS** | Stated as the contribution in the third paragraph and defended in "Why this is worth publishing at pilot scale." |
| U3 | Use the cross-section/within-gig reversal as the argument for the matched-model design | 2026-08-05 | **PASS** | Numbered finding 2, with both coefficients and the Simpson-style interpretation. |
