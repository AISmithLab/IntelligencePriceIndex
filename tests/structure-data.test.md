# Tests: Structure paper §2 — data

**Draft file:** `drafts/structure/sections/data.md`
**Last reviewed:** 2026-08-18

## Reviewer Simulation

| # | Critique | Severity | Status | Response |
|---|---|---|---|---|
| R1 | "Internet Archive coverage is not random — you observe survivors" | major | PASS | stated as the binding limit: `n_404 = 0` across 509,339 captures means exit is unmeasurable, and the manifest is not a survival-free sample |
| R2 | "Why start at 2019Q3? Convenient for your result" | major | PASS | extraction-method mix table given; three-tier detection differs by 19pp across the seam |
| R3 | "One platform is not a market" | major | FAIL | conceded in §5.5 but the draft should say in §2 what makes this platform representative, and of what |
| R4 | "Listed prices are not transaction prices" | major | PASS | §2.6, and every derived quantity is labelled an upper bound |
| R5 | "The operator's metrics are unaudited marketing numbers" | minor | PASS | GMV = buyers × spend/buyer is an identity that reproduces reported GMV to rounding; revenue explicitly rejected as a substitute |
| R6 | "TF-IDF over job titles is not an exposure measure" | major | PASS | §2.5 gives coverage (63.2%) and the selection threat (+23.7%), both declared before estimation |
| R7 | "Category assignment method is not described" | minor | FAIL | §2 should point at the classifier and its validation rather than assuming the IPI paper's §Method |
