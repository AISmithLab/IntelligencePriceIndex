# Tests: Structure paper §4 — the six designs

**Draft file:** `drafts/structure/sections/identification.md`
**Last reviewed:** 2026-08-18

## Reviewer Simulation

| # | Critique | Severity | Status | Response |
|---|---|---|---|---|
| R1 | "Six failed designs is a fishing expedition dressed as rigour" | major | PASS | §4.6 and the pre-registration: I6's gates and consequences were fixed before estimation; the lock file records the prior as low |
| R2 | "You are reporting a null with no power calculation" | major | PASS | realised MDE reported next to the estimate; I6's \|β\| = 0.90× MDE is stated as a qualification, not hidden |
| R3 | "G5 failed — so composition kills your estimate" | major | PASS | reported as failing on power not sign (−0.2022, larger, n falls to 1,715 listings); recorded FAIL by the letter of the lock |
| R4 | "The p-floor argument is a smokescreen for a weak measure" | major | PASS | 1/7 = 0.143 is arithmetic, and I6 escapes it entirely by moving to gig level — and still fails |
| R5 | "TF-IDF on job titles is a thin exposure measure" | major | PASS | conceded, declared in the pre-registration *before* running (§8 of the lock), and named as the top fix in §5.4 |
| R6 | "36.8% zero-match with differential selection invalidates I6" | major | PASS | declared as a threat in the gate card; the selection audit is reported, not suppressed |
| R7 | "A CPI-U placebo is a strange test" | minor | PASS | its role is stated: it detects a design tracking any smooth series |
| R8 | "You never show the specification that would have 'worked'" | minor | PASS | §4.1 and §4.3 both report the publishable-looking artefacts in full |
| R9 | "Category × quarter FE absorbs the treatment if AI is platform-wide" | major | PASS | §4.4 now states it directly: a uniform AI shock is absorbed by construction, I6 identifies only relative exposure effects, and a null there does not mean AI had no effect |
| R10 | "The dose–response fallback is not identified, so why report it?" | minor | PASS | reported as the pre-registered fallback, explicitly not identified |
| R11 | "Synthetic control with 7 donors is underpowered by construction" | major | PASS | that is the reported conclusion, with the in-space placebo ranks given |
| R12 | "Newey-West series contradicts the panel estimate" | major | PASS | reported as an internal contradiction and attributed to composition |
| R13 | "Your searched-break procedure never finds ChatGPT — how do we know it can find anything?" | **critical** | PASS | **Positive control added 2026-08-19** (`drafts/market-structure-answer.md` §4.3.1, step 57). The identical search on the AI-diffusion series ranks ChatGPT **1 of 19**, top four candidates all AI milestone quarters, SSR spread 227% vs step 55's 0.06%. The instrument resolves the AI date to within one quarter, so the null in the outcome series is a fact about the market, not the method |
| R14 | "You measure AI exposure but never measure AI itself — is generative AI even in this market?" | major | PASS | §3.7: it is, dated to **2023Q1** on the entry-cohort series (0.5% → 5.98% in one quarter), measured from gig titles held on 100.0% of observations |
| R15 | "The title classifier is doing the work; show me its false positives" | major | PASS | §3.7.1: realised precision floor is **7 distinct titles across 2019–2021**, six of them genuine pre-generative AI work. Three guards reported with the audit that produced each — `.ai` as the Illustrator extension being the largest |
| R16 | "AI-branded listings price −12.5% below others — that is your AI effect" | **critical** | PASS | §3.7.4 refuses the reading explicitly: cross-sectional, different listings, a selection fact about *who* advertises AI. The within-gig version is 61 adopters at −14.9% (t −0.78) and is reported as such |
| R17 | "The diffusion measure only catches sellers who advertise AI" | major | PASS | conceded in §3.7.6 and §5: it measures AI *marketing*, not AI *production*; silent adopters are invisible and are likely the larger group; stated as a **lower bound on adoption** |
| R18 | "Diffusion via entry is convenient — it excuses every within-gig null you report" | major | PASS | it is measured, not asserted: 22 of 11,425 continuously-observed listings ever relabelled (§3.7.3). The implication for gig-FE designs is stated as a consequence, and design 9 (`plans/active/ai-penetration-prereg.md`) is pre-registered to test the entry margin directly |
| R19 | "You never tested actual product launch dates — only a vague 'AI period'" | **critical** | PASS | Design 10 (§4.3.2): 20 named launches at **monthly** resolution, dated by public availability, each matched to the category it targets. 2 of 20 clear the pre-window gate, below the ~3 that 60 tests give by chance |
| R20 | "Design 10's demand results are the strongest AI evidence in the paper" | **critical** | PASS | They are reported nowhere. Step 58b's 12 placebo launches in 2019 give a **75% false-positive rate** on that outcome; the margin is discarded, and the discard is documented rather than the results quietly dropped |
| R21 | "How do we know design 10's price null isn't the same broken test?" | major | PASS | The same placebo gives **8%** on the price margin against a nominal 5%. The size check is reported for both outcomes, and it is what separates them |
| R22 | "Image models obviously hit design — your own table shows −5%" | major | PASS | §4.3.2: every image-model date shows it, and every one has a **larger pre-window effect** (t −5.3 to −7.1 against −4.9 to −5.6). Design was diverging downward before any image model shipped |
| R23 | "Your per-tool targeting is asserted, not verified" | major | PASS | It is verified, and it **fails** — the first stage shows ChatGPT produced no differential adoption in writing, with AI branding concentrating in coding regardless of tool. Reported as the design's most informative result, and its 7-category clustering flagged as untrustworthy for inference |

## User Requirements

| # | Instruction | Date | Status | Location |
|---|---|---|---|---|
| U1 | "Answer: how does generative AI diffusion change long-run pricing and competitive structure in online freelancer markets" — on data already collected, no new collection | 2026-08-19 | PASS | `drafts/market-structure-answer.md`, whole document; §3.7 and §4.3.1 are the 2026-08-19 additions and used only data already on disk |
| U2 | The answer must remain answerable from held data — a route that requires new collection is a research-agenda item, not part of the answer | 2026-08-19 | PASS | §6 lists collection-dependent items separately; `plans/active/recent-frame-collection.md` holds the open crawl decision |
| U3 | "Look at specific important dates related to AI launches and compare before and after" | 2026-08-20 | PASS | §4.3.2; `code/58-ai-launch-events.py` (20 named launches, monthly) and `code/58b-launch-placebo.py` (the size check that split the result) |
