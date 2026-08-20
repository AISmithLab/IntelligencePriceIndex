# Tests: Structure paper §2 — data

**Draft file:** `drafts/structure/sections/data.md`
**Last reviewed:** 2026-08-18

## Reviewer Simulation

| # | Critique | Severity | Status | Response |
|---|---|---|---|---|
| R1 | "Internet Archive coverage is not random — you observe survivors" | major | PASS | stated as the binding limit: `n_404 = 0` across 509,339 captures means exit is unmeasurable, and the manifest is not a survival-free sample |
| R2 | "Why start at 2019Q3? Convenient for your result" | major | PASS | extraction-method mix table given; three-tier detection differs by 19pp across the seam |
| R3 | "One platform is not a market" | major | FAIL | conceded in §5.5 but the draft should say in §2 what makes this platform representative, and of what |
| R4 | "Listed prices are not transaction prices" | major | PASS | §2.6, and every derived quantity is labelled an upper bound. **Strengthened 2026-08-20**: step 59 recovered order-level realised amounts from the same archived pages, so the gap is now measured rather than asserted — orders under $50 are 1.0% of all orders against a listed median of $25–30 (`drafts/market-structure-answer.md` §1.3) |
| R8 | "The realised prices you recovered are the ones Fiverr chose to display, ranked by relevance — so your distribution is selected" | major | FAIL | **Open, and conceded in §1.3 as the central threat.** ~13.1% of orders are recovered (a 59-gig subsample estimate) and pages rank displayed reviews by `relevancy_score`. The available check (priced vs unpriced reviews near-identical on rating, repeat-buyer and business shares) tests the *field*, not the *display*. A display-selection test must run before any realised-price number is published as more than a pilot description |
| R9 | "Realised order value is available from 2022 — so why is the index still built on listed prices?" | minor | PASS | answered in §1.3 limit 1: the paid field is absent from 0.0–0.8% of 2018–2021 captures and appears at 64.2% in 2022, so it cannot reach the pre-ChatGPT baseline the long-run index needs |
| R5 | "The operator's metrics are unaudited marketing numbers" | minor | PASS | GMV = buyers × spend/buyer is an identity that reproduces reported GMV to rounding; revenue explicitly rejected as a substitute |
| R6 | "TF-IDF over job titles is not an exposure measure" | major | PASS | §2.5 gives coverage (63.2%) and the selection threat (+23.7%), both declared before estimation |
| R7 | "Category assignment method is not described" | minor | FAIL | §2 should point at the classifier and its validation rather than assuming the IPI paper's §Method |
