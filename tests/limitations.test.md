# Tests: Limitations

**Draft file:** drafts/sections/limitations.md
**Last reviewed:** 2026-08-06

Rewritten 2026-08-06. The previous version was seven acknowledgement paragraphs with no quantities; the rewrite attaches a measured bound wherever one exists.

## Reviewer Simulation

| # | Critique | Severity | Status | Response |
|---|----------|----------|--------|----------|
| R1 | "This is a disclaimer list, not a limitations section — nothing is quantified." | major | **PASS** | The opening states the principle ("a limitation with a number attached is a result and one without is a disclaimer") and §6.1 delivers: six of seven categories miss ±5% with each band given, 850–2,500 matched gigs needed to fix it, demand and dormancy MDEs of ±23% to ±66%, DiD interval −14.8% to +87.6%. |
| R2 | "Survivorship is mentioned but not bounded." | **blocking** | **PARTIAL** | §6.2 gives the magnitude of the *gap* (entry prices flat 2019–2025 against +47% to +167% incumbent growth) but explicitly cannot bound the share of the index it explains, because the two crawls disagree on entry medians for the same year (\$50 on n=102 vs \$30 on n=2,389). The draft states this as an open problem rather than claiming a bound it does not have. **This is the most likely blocking objection at review**, and the honest answer is that it needs the crawl-frame reconciliation first. |
| R3 | "You say exit is unmeasurable. Isn't that a reason not to publish?" | major | **PASS** | §6.3 distinguishes the two failure modes — absence means "not archived," and the manifest additionally selects on survival — quantifies both (36.5% of recent-panel gigs last seen in the final quarter against 0.4% historically; 1,747 of 2,930 "first captured" in the manifest's first quarter), and gives two specific, cheap, non-retrofittable collection changes that fix it. The limitation comes with its remedy. |
| R4 | "Your own §3.7 says parts of the index are not identified. Should that not disqualify the results?" | major | **PASS** | §6.4 states the scope precisely: it affects the historical per-category levels for coding, translation and audio, which are withheld; the recent segment is stable under all three perturbations; and the composite is exempt via splice geometry. The draft says the pre-2024 category detail is "weaker than a band alone would suggest" rather than defending it. |
| R5 | "Price versus value — the quality-adjustment problem is fatal for a price index of services." | major | **PASS** | §6.5 states it in both directions (AI-improved output at unchanged price is unmeasured deflation; AI-enabled bundling is unmeasured inflation) and concedes it is unsolved rather than gesturing at a partial fix. |
| R6 | "Fiverr is one platform. Why should anyone care?" | minor | **PASS** | §6.5 restricts the claim explicitly — "a *gig-economy* price index, not a universal price index for cognitive labor" — and §5.3 argues the transferable contribution is methodological rather than the level itself. |
| R7 | "You disclose a data defect (`rating` scale) in a limitations section. Why was it not fixed?" | minor | **PASS** | §6.5 states the defect (217 rows on a 10-point scale written into a 5-point column), states that it does not touch the index because the index uses prices only, states that it does not move the hedonic result (167 surviving rows), and warns against any future row-level use without correcting it. Tracked as an open item. |
| R8 | "§6.6 says you claim nothing. Then what is the paper?" | major | **PASS** | §6.6 is precise rather than nihilistic: it disclaims the causal attribution and names what is claimed instead — the instrument, the bounds, the design requirements. It matches the abstract and §1, so the paper's scope is stated identically in three places. |

## User Requirements

| # | Instruction | Date | Status | Location |
|---|-------------|------|--------|----------|
| U1 | Report the non-price margins as bounds in limitations | 2026-08-05 | **PASS** | §6.1: demand and dormancy null with MDE ±23% to ±66%, and the explicit instruction that the raw dormancy ranking must not be quoted because three of seven categories reverse sign under adjustment. |
| U2 | Specify the full-scale crawl so exit and entry are measurable | 2026-08-05 | **PASS** | §6.3, both requirements stated as numbered items with the reason each is impossible to retrofit. |
| U3 | Report matched gigs per bilateral wherever sample size is cited | 2026-08-05 | **PASS** | §6.1 cites matched-gig medians (208 down to 3) rather than panel-gig counts; the old "Sample size" paragraph that cited panel gigs is gone. |
