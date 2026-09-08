# Tests: Abstract

**Draft file:** drafts/sections/abstract.md
**Last reviewed:** 2026-09-08

The abstract was **rewritten from scratch** on 2026-08-06. Every substantive claim in the previous version was retracted or superseded (see R1), so it was rewritten rather than edited.

## Reviewer Simulation

| # | Critique | Severity | Status | Response |
|---|----------|----------|--------|----------|
| R1 | "The abstract's claims do not match the paper's results." | **blocking** | **PASS (rewritten)** | True of the previous version, which quoted a composite peak of 312 and a 21% 2025 decline (the retired chained series plus the `hire/*` artifact), elasticities of −0.49 to +1.10 (retracted, §3.9), "9 service categories … 2017 to 2025" (7 categories, 2020Q1–2026Q1), and AI as the driver (against the descriptive-first decision). The rewrite quotes only figures from `data/pilot/paper-numbers.md`. |
| R2 | "The abstract claims a price index but leads with a number that is mostly inflation and reputation." | major | **PASS** | The abstract gives real (+40.7%) and nominal (+78.4%) with CPI-U (+26.8%) in the same sentence, then devotes its second paragraph to the two rivals it can measure — inflation at ~half the nominal rise, reputation at +7.7% per doubling of reviews yielding a +39.7% to +79.0% band — and states that the band's floor is itself imprecise. A reader cannot come away with the headline unqualified. |
| R3 | "Abstracts that lead with negative results do not get read." | minor | **PASS (deliberate)** | The negative results are placed third, after the instrument and the measured result, and are framed as the paper's contribution ("part of its contribution") rather than as failures. The final paragraph states the forward design requirements so the abstract ends on what the work enables. |
| R4 | "You say you retract a previously reported result. Is an abstract the place for that?" | minor | **PASS** | Yes, given the finding is methodological and transferable: the specification is intuitive and easy to run, and the abstract states the three diagnostics that kill it (time-trend placebo, CPI-U placebo, first differences). Burying a retraction in §3.9 while the abstract stayed silent would be the worse choice. |
| R5 | "37,782 snapshots — is that the number the index is built on?" | minor | **PASS** | It is the total observation count across both crawls before the Stage 5b exclusion, and the abstract says "gig-price snapshots" rather than implying it is the panel. §3.2 gives the full attrition chain and §4.1 gives the panel counts (1,066 historical and 2,908 recent gigs). Reviewer could reasonably ask for the panel figure instead; the larger number is defensible but is the more flattering of the two. |
| R6 | "Does the abstract state the window and the base?" | minor | **PASS** | 2020Q1–2026Q1, seven categories, with the base implied by the index convention and stated in §3.4. |
| R9 | "The abstract now carries five results and two artifacts. Is it still an abstract?" | minor | **PASS** | It runs 541 words in five paragraphs, each doing one job: the instrument, the measured confounds, the two nulls, the negative results, and the closing window. Every number in it is frozen and checked by `code/32-check-draft-numbers.py`. A reviewer may reasonably ask for it to be cut to 250 for a venue with a hard limit; the material to cut first is the 35-category sentence in paragraph four. |

## User Requirements

| # | Instruction | Date | Status | Location |
|---|-------------|------|--------|----------|
| U1 | Paper must not claim AI as the sole or identified driver | 2026-07-29 | **PASS** | The abstract never attributes the rise to AI; it names inflation and reputation as measured rivals and states the residual is not separately identified. |
| U2 | Publish the pilot as a measurement paper; negative results are part of the contribution | 2026-08-05 | **PASS** | Third paragraph, explicitly framed as contribution; fourth paragraph gives the forward design requirements. |
| U-window | "But don't we look at 2018 to 2026, not 2020-2026?" — the abstract must not attach the index window to the data, which reaches back further | 2026-09-08 | **PASS** | The abstract previously read "37,782 snapshots ... covering seven categories over 2020Q1-2026Q1", which reads as if collection began in 2020. It now separates the three spans: captures reach back to 2018, the estimation panel opens 2019Q4, and the index is **published** 2020Q1-2026Q1 — with the reason stated (four quarters of 2017-2018 hold no captures; §3.7 shows the 2018Q3-2020Q1 leg is not identified, its level moving by a third under a change of base quarter). Checked across all sections: every other use of "2020Q1-2026Q1" already attaches it to the index, not the data. |
