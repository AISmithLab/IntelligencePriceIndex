# Paper Template — measurement paper

**What this is.** The skeleton of the paper, with each section reduced to its job, its
contents, and the way it usually fails. Written from the structure of `drafts/main.md`,
so it doubles as a map of the current draft and as a reusable template for paper 2.

**How to read the columns.** *Purpose* is the one thing the section must accomplish.
*Contains* is the checklist. *Budget* is the target length. *Fails when* is the failure
mode a reviewer will find first.

Placeholders are written `[LIKE THIS]`. Where the current draft already fills a slot,
it is shown in italics underneath as `→ current:`.

---

## Front matter

```
Title:      [WHAT WAS MEASURED] — [OVER WHAT DOMAIN AND WINDOW]
Authors:    [NAMES, AFFILIATIONS]
Keywords:   [4–6, at least two of them methods terms]
JEL codes:  [IF ECONOMICS VENUE]
Data:       [REPOSITORY LINK, RELEASED WITH THE PAPER]
Code:       [REPOSITORY LINK]
```

*→ current: IPI, seven Fiverr service categories, 2020Q1–2026Q1.*

---

## Abstract — 5 moves, ~300 words

| # | Move | One sentence each |
|---|------|-------------------|
| 1 | **The instrument** | What was built, from what data, over what window, with what estimator. |
| 2 | **The headline number** | The single measured result, with its uncertainty band, against a benchmark. |
| 3 | **The decomposition** | What else explains that number, quantified — not hedged. |
| 4 | **The negative results** | Stated as bounds, not as absences. Include any retraction here, not later. |
| 5 | **The contribution** | Instrument + bounds + the design requirements that would resolve what this cannot. |

**Fails when** it promises identification the body does not deliver. Write it last,
from the frozen numbers, and check every figure against them.

*→ current: 336 words, all five moves present, retraction in move 4.*

---

## 1. Introduction — ~1,000 words

**Purpose.** State the question, the answer, and why a null is worth reading.

**Contains**
- [THE QUESTION], and why existing instruments cannot answer it
- What was built, in three sentences
- **A numbered list of findings, including the negative ones** — reviewers read this list and nothing else on a first pass
- A subsection titled *why this is worth publishing at [SCALE]*, which must state what **would** resolve the question — a null result is only publishable if it specifies the study that wouldn't be null
- Roadmap paragraph

**Fails when** the negative results are deferred to §6, where they read as excuses rather
than as findings.

---

## 2. Related Work — ~4,000 words

**Purpose.** Position the contribution; establish the reference class the paper will be
judged against.

**Contains**
- [LITERATURE 1 — the substantive question]
- [LITERATURE 2 — the methods reference class]. Choose this deliberately: it determines
  the standard of rigor applied to you
- A **positioning table**: rows = prior work, columns = the dimensions that define your
  approach, final row = this paper
- An explicit statement of what this paper does **not** do

**Fails when** it promises a construct the paper later retracts. Re-read §2 against §3
and §4 after every substantive revision — this is the section that silently goes stale.

*→ current: exposure indices + platform outcome studies; methods class is online price
measurement, not the AI literature.*

---

## 3. Data and Method — the longest section

**Purpose.** In a measurement paper, the method *is* the contribution. Budget accordingly.

| Subsection | Purpose | Fails when |
|---|---|---|
| 3.1 **Source and window** | Where the data comes from; why the window starts where it does | The window looks chosen to get an answer. Give the hard floor with numbers |
| 3.2 **Pipeline and attrition** | Every stage, with the count entering and leaving | Reports the final n without the funnel |
| 3.3 **Units and weights** | What a unit is; how the composite aggregates | Buries a dominant weight. If one component carries 70%, say so in the text |
| 3.4 **The estimator** | The formula, why this one, what it rules out | Presents the choice as obvious. Show the alternative and its number |
| 3.5 **Adjustments** | Deflation, normalization, seasonality | Silent about whether uncertainty changes |
| 3.6 **Precision and adequacy** | A stated numeric standard, and which series meet it | States no criterion, so no series can fail |
| 3.7 **Identification failures** | Where the estimator is not identified, and why | Reports standard errors that do not detect the failure |
| 3.8 **Rival explanations, measured** | Each rival quantified, not argued away | Arguing instead of measuring |
| 3.9 **What is not reported, and why** | Specifications tried and rejected, with diagnostics | Dropping them silently |

**The general rule for §3:** state a criterion *before* reporting which series meet it.
A standard invented after the results is not a standard.

**3.1 and 3.2 have their own template** — `drafts/templates/data-collection-section.md`,
which expands the source/window/pipeline rows above into a fill-in skeleton with the
revision history, source ceilings and in-flight-collection quarantine that those two rows
compress away.

*→ current: 6,145 words, all nine subsections.*

---

## 4. Results — ~2,500 words

**Purpose.** The measured findings, each with its uncertainty attached.

**Contains**
- 4.1 **Descriptive facts** before any estimate — the raw picture that motivates the index
- 4.2 **The headline series**, with band and benchmark [FIGURE]
- 4.3 **Disaggregated series**, each with its band [FIGURE] — and an explicit refusal to
  rank if the intervals overlap
- 4.4 **What the result is not** — every rival from §3.8, quantified, with the residual
  named as the thing left to explain
- 4.5 **Other margins**, reported as bounds with minimum detectable effects
- 4.6 **What a correction changed** — if a defect moved the numbers, publish before/after
- 4.7 **What cannot be determined**, and the reason it fails

**Fails when** a null is reported without an MDE. `[NO EFFECT DETECTED]` is not a
finding; `[NO EFFECT LARGER THAN ±X%]` is.

---

## 5. Discussion — ~1,250 words

**Purpose.** What the result means, at the confidence it warrants.

**Contains**
- 5.1 What this instrument adds that existing ones do not — and what it is structurally
  blind to
- 5.2 **The counterintuitive result, with every reading that survives.** List them; say
  which the data cannot distinguish; give the one-line summary a reader should take
- 5.3 **The transferable findings** — what generalizes beyond this dataset. In a
  measurement paper this is usually the most cited section
- 5.4 Reconciliation with prior work, **by margin** rather than by dispute
- 5.5 Implications, separated by audience, each at its own confidence level

**Fails when** it argues for the favored reading instead of listing all of them.

---

## 6. Limitations — ~1,300 words

**Purpose.** Quantify every limitation that has a number.

**Contains**
- 6.1 What the sample cannot resolve — **with the bound**
- 6.2 What the design cannot see — structural blindness, not sampling
- 6.3 **The collection specification that fixes it** — the requirements that cost nothing
  now and cannot be retrofitted
- 6.4 Known data defects, including ones not used in the analysis

**Fails when** limitations are listed without magnitudes. "Sample size is limited" is
not a limitation; "±23% to ±66% minimum detectable effect" is.

---

## 7. Conclusion — ~600 words

**Purpose.** The argument in one page, ending on what it would take to do better.

**Contains**
- What you set out to measure and whether you got it — **first sentence**
- The one positive finding, with its band
- The confounds it survives only with attached
- The retraction, if any
- The findings that outlast the series
- **The specification for the study that would resolve it** — concrete numbers
- A closing line that states the contribution honestly

**Fails when** it recovers ambition the body gave up.

---

## Apparatus checklist

- [ ] **Frozen numbers table.** One file every section quotes from; no section computes
      its own figures. Enforce with a checker that greps the draft for retracted figures
      and requires a retraction cue nearby
- [ ] **Figures**, each with a numbered caption stating what the reader should take from it
- [ ] **Every citation resolves**, and every unverified one is *marked as unverified* —
      an unverified citation is worse than a missing one
- [ ] **Test files**: one per section (reviewer simulation), one cross-cutting, one
      against a model paper
- [ ] **User requirements** recorded as tests, so intent is not lost in conversation
- [ ] Render after every substantive edit

---

## The three rules this template encodes

1. **State the criterion before the result.** Adequacy standards, exclusion rules and
   windows are decided and written down first, or they are not standards.
2. **Every null carries a bound.** A null without an MDE is not reportable.
3. **Retract loudly.** A retraction the authors hand the reviewer costs far less than
   one the reviewer finds.
