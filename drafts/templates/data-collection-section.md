# Template — the data collection section

**What this is.** A fill-in skeleton for the part of the paper that describes where the
data came from: source, window, selection rule, pipeline, attrition, revisions, and
ceilings. In the current draft this is §3.1–3.2 of `drafts/sections/method.md`.

**How it relates to the other two templates.**

| file | answers |
|---|---|
| `plans/templates/data-collection.md` | how to *run* a collection campaign |
| this file | how to *write up* the collection that was run |
| `drafts/paper-template.md` | where this sits in the paper, and what the other sections owe it |

**Where it came from.** The shape below is reverse-engineered from `method.md` §3.1–3.2
after the pilot's collection had been revised five times. Sections 3–6 of this template
(revision history, ceilings, in-flight collections, unit-of-sample-size caution) exist
because each one, when absent, was a thing a reviewer would have found first.

Placeholders are `[LIKE THIS]`. Worked examples from the current draft appear underneath
as `→ current:` — delete them when adapting.

---

## The rule this template encodes

> A collection section is an audit trail, not an advertisement. Its job is to let a
> reader reconstruct what was collected, what was discarded, what was discovered too
> late, and what the source cannot supply at any budget. **Anything the collection got
> wrong is cheaper to publish than to have found.**

Two corollaries used throughout:

1. **Every count carries the count it came from.** A stage that reports "22,632
   downloaded" without "of 26,603 manifest entries" is not reporting attrition.
2. **State the selection rule in terms of what the estimator consumes**, not in terms of
   what was collected. The two diverge by orders of magnitude; only the former binds.

---

## X.1 Source and window

**Purpose.** Establish what the source is, why it is the right one, and why the window
starts where it does — with the floor imposed by the data rather than chosen.

### Contents

**a. What the source is, and the properties that make it suitable.** Enumerate — three
is usually the right number — and tie each to a requirement the estimator has, not to a
generic virtue.

```
1. [PROPERTY]. [WHY THE ESTIMATOR NEEDS IT.]
2. [PROPERTY]. [WHY THE ESTIMATOR NEEDS IT.]
3. [PROPERTY]. [WHY THE ESTIMATOR NEEDS IT.]
```

*→ current: posted (revealed, not surveyed) prices; granular task decomposition matching
the task-level literature; longitudinal coverage back to 2011.*

**b. The immediate qualification.** Whichever property above is weakest, qualify it in
the same breath and with numbers. This paragraph is what separates a source description
from a sales pitch.

> [PROPERTY N] requires immediate qualification, because it is weaker than it appears
> and it constrains everything downstream. [THE MECHANISM — e.g. an opportunistic crawl
> is not a sampling frame.] [THE COUNTS THAT SHOW IT, PER PERIOD.] [WHERE THE CHAIN /
> IDENTIFICATION IS NOT MERELY THIN BUT SEVERED, WITH THE ZERO.] **[PERIOD] is therefore
> a hard floor on [WHAT], and §[X.N] shows even [MARGINAL PERIOD] is too fragile to
> publish.** We report [PUBLISHED WINDOW].

*→ current: 2017Q2/Q4, 2018Q1, 2018Q2 hold no captures at all; 2017Q1→2017Q3 and
2017Q3→2018Q3 share zero matched gigs; 2018Q3 is the hard floor, published window
2020Q1–2026Q1.*

**c. How the source was chosen.** Pre-registered pass/fail criteria, the probe that
tested them, the alternatives probed and rejected, and where the probe artifacts live.

| criterion | threshold set in advance | result |
|---|---|---|
| [COVERAGE] | [≥ N UNITS SPANNING ≥ M YEARS IN ≥ K STRATA] | [MEASURED] |
| [EXTRACTABILITY] | [≥ X% OF PROBED PAGES YIELD THE FIELD] | [MEASURED] |
| [LONGITUDINAL TRACKING] | [≥ N UNITS OBSERVED AT ≥ K DATES] | [MEASURED] |

Rejected alternatives, each with the measured reason: `[SOURCE B] — [WHAT FAILED]`.
Artifacts: `runs/[TAG]/`.

**d. What the gate did *not* establish.** One short paragraph, and do not skip it.

> That gate established that the source is [PARSEABLE AND LONGITUDINAL]. It established
> nothing about whether it is dense enough to [IDENTIFY THE ESTIMAND], which is a
> separate question, is answered in §[X] and §[Y], and is answered largely in the
> [NEGATIVE]. A feasibility criterion cleared at [N] pages is a weak instrument and we
> treat it as one.

**e. How the collection was scoped.** The census of the full source *before* any
collection budget was committed, and the design that census forced.

> A size estimate over [THE SOURCE] found roughly **[N UNITS AND V TB]** — beyond what we
> could [RETRIEVE / STORE / POLITELY REQUEST]. Rather than [COLLECT OPPORTUNISTICALLY AND
> STOP WHEN X RAN OUT], we [SPLIT THE COLLECTION: CHEAP COMPLETE INDEX FIRST, MANIFEST
> BUILT OFFLINE, THEN ONLY THE UNITS THE MANIFEST NAMES]. Every sampling decision below is
> therefore made against a full census rather than against whatever a crawler reached
> first, and **the sampling frame is a file we can publish and others can re-sample from.**

**f. If there is more than one collection, say so here.** Name them, state the rule that
distinguishes them, and forward-reference where they are combined.

*→ current: a 500-seller historical crawl (selected for depth) and a trailing-window
recent crawl (selected for density), estimated separately and spliced in §3.4.*

### Fails when

- The window's start looks chosen to get an answer. Give the floor with the numbers that
  impose it.
- The source's weakness appears only in §Limitations, where a reviewer reads it as a
  concession rather than as part of the design.
- The feasibility gate is described as if it validated the analysis.

---

## X.2 Sample construction — the pipeline, stage by stage

**Purpose.** Let a reader recompute every number in the funnel.

### Contents

**a. A one-line contract for the section.** Scripts cited inline; each stage writes to
disk; every intermediate count recoverable from released artifacts.

**b. One paragraph per stage,** each naming its script and reporting **what entered and
what left**.

```
**Stage N: [NAME]** (`code/[NN]-[script].py`). [WHAT IT DOES, INCLUDING THE PARAMETER
A REPLICATOR WOULD NEED — rate limits, concurrency, seeds, thresholds.] This yields
**[COUNT OUT]** of **[COUNT IN]**.
```

Stages that almost always exist:

| # | Stage | The number that must appear |
|---|---|---|
| 1 | Index / frame retrieval | raw records |
| 2 | Filtering, dedup, classification | records surviving each rule |
| 3 | Sampling | frame size → drawn, **and the sampling unit** |
| 4 | Retrieval | requested → retrieved, with the failure breakdown |
| 5 | Extraction / parsing | success rate **and the share by method** |
| 5b | Exclusions found after the fact | rows dropped, and the artifact that revealed them |
| 6 | Deduplication to analysis units | unique units |
| 7 | Derived groupings | clusters/items, **and what they are not used for** |
| 8 | Panel / analysis-set construction | final n per segment |

**c. The sampling unit, stated as a cost.** Say which unit was drawn and what drawing it
gave up.

> We sample **[UNIT], not [ALTERNATIVE UNIT]**. This is deliberate and it costs coverage:
> drawing [ALTERNATIVE] would spread the same budget over more of [THE SPACE], but it
> would break [THE STRUCTURE THE ANALYSIS REQUIRES].

**d. If the extractor is a cascade, table it** — method, era, mechanism, share. A share
table is what makes a parsing defect visible later.

**e. Exclusions discovered after collection (the "Stage 5b" slot).** Every collection of
any size has one. Report:

- the artifact that revealed it, with the diagnostic signature
  *(→ current: 2,436 rows at exactly \$500 and 330 at \$1,000)*;
- the count dropped, as a share **and where it falls** (which crawl/segment/period);
- the **audit for other instances of the same class**, with at least two independent
  tests that agree;
- why the rule keys on [THE FAMILY] rather than [THE SYMPTOM], with the counter-example
  that would have been destroyed by the broader rule;
- a forward-reference to the results section reporting the effect on the estimate.

**f. The funnel in one line.** `[N raw] → [N deduped] → [N qualifying] → [N sampled] →
[N manifest] → [N retrieved] → [N with valid field] → [N in panel]`, per collection.

### Fails when

- The final *n* is reported without the funnel.
- A stage's parameters are omitted, so the stage cannot be re-run.
- Extraction is reported as a success rate with no breakdown by method, so a defect that
  parses "successfully" stays invisible.

---

## X.3 How the collection changed

**Purpose.** A collection that was revised is normal; one presented as if it were not is
a claim a reviewer will test. Because each revision was forced by something the data
revealed rather than chosen in advance, **the sequence is itself evidence about what
collection in this domain costs**.

### Contents

| # | When | Change | What forced it |
|---|---|---|---|
| 1 | [DATE] | [WHAT CHANGED] | [THE MEASUREMENT THAT FORCED IT] |

Then prose for the ones that carry a transferable lesson — typically:

- **A revision that changed the paper's structure.** *(→ current: the second crawl, and
  why the paper therefore has a splice.)* Say which asymmetries in the results trace back
  to it.
- **A revision that cost nothing but was luck.** *(→ current: 45% transient failure rate
  at 20 req/s versus zero at 10 req/s, same 5.71 pages/s sustained.)* State the correct
  reading — that the setting was past diminishing returns and it was not known until
  measured.
- **A revision that retracted a published finding.** State plainly what was claimed, that
  it was an artifact, that it is retracted, and that the results section reports the full
  before-and-after **rather than quietly restating the corrected numbers**.

### Fails when

- The revision history is omitted, and §Results has to explain a number that has no
  visible cause.
- A retraction is phrased as a refinement.

---

## X.4 What the collection cannot fix

**Purpose.** Separate limits that are properties of the source from limits that are
resource choices. A reader must be able to tell a floor from a budget.

For each: the claim, the measurement that bounds it, and the design that *would* resolve it.

```
**[LIMIT] is unmeasurable/closed/severed**: [THE MEASUREMENT, INCLUDING THE ZERO OR THE
COLLAPSE]. [WHY THE SOURCE BEHAVES THIS WAY — the mechanism, not the symptom.] Only
[THE DESIGN THAT WOULD RESOLVE IT] could separate them.
```

*→ current: exit unmeasurable (`n_404 = 0` across 509,339 in-window captures — the
archive stops re-requesting a delisted URL rather than recording its death); trailing edge
closed (280,779 status-200 captures in 2024-09 → 66 in 2026-03); chain severed before
2018Q3 (1 matched unit at 2017Q3→Q4 against 8,084 at 2018Q3→Q4).*

**State explicitly that no larger collection reaches these**, and if a ceiling is
quantified against a requirement, give both numbers *(→ current: coding needs ≈7,400
matched gigs per pair; the entire index supplies at most 6,142)*.

### Fails when

A ceiling is described qualitatively ("coverage is limited at the early end"), which
reads as a resource complaint rather than a measured property of the source.

---

## X.5 Collections in flight that contribute nothing to this paper

**Purpose.** If enlarged collections exist, a reader who finds them in the repository
must not have to wonder whether any number came from them.

> Censusing the existing [FRAME] showed the binding constraint was never [THE SOURCE] but
> our own selection rule: [SEGMENT] holds **[N]** units where the shipped panel uses
> **[M] ([M/N]%)**. [WHAT IS RUNNING, WITH ITS RULE AND SIZE.] Both write to separate
> files. **Every number in this paper comes from the frozen table of [THE ORIGINAL
> COLLECTIONS]**, and §[LIMITATIONS] states what the enlarged panels are expected to
> resolve — with one ceiling they will not: [THE CEILING].

### Fails when

Omitted, and a reader reconciling the repository against the paper assumes contamination.

---

## X.6 The caution about counts

**Purpose.** Close the section by naming the unit that actually governs precision, so no
count above is misread as sample size.

> [THE COUNT REPORTED PER STAGE] is not the quantity that governs precision. A
> [ESTIMATOR TYPE] is identified by [THE UNIT THE ESTIMATOR CONSUMES — e.g. units shared
> between *pairs* of periods], and the two diverge by orders of magnitude in
> [WHICH SEGMENT]. §[X] reports [THE BINDING UNIT], which is the number that binds, and
> we use it wherever this paper makes a claim about sample size.

---

## Checklist — the numbers this section must contain

- [ ] Window floor, with the counts that impose it (including at least one zero)
- [ ] Pre-registered source criteria with thresholds set **before** the probe
- [ ] Rejected alternative sources, each with a measured reason
- [ ] Full-frame census size, versus what was collected, as a percentage
- [ ] Per-stage in→out counts, and the one-line funnel
- [ ] Sampling unit named, with what it cost
- [ ] Retrieval failure breakdown (hard failures vs transient vs dedup collapse), and a
      statement of whether any evidence of blocking exists
- [ ] Extraction share by method, not only a success rate
- [ ] Post-hoc exclusions: share, location, the audit for siblings, forward-reference
- [ ] Revision table, with what forced each row
- [ ] Every retraction stated in this section, not deferred
- [ ] Source ceilings, each with its bounding measurement and the design that resolves it
- [ ] In-flight collections quarantined explicitly
- [ ] The binding sample-size unit named last

## Reproducibility block to release alongside

| artifact | path |
|---|---|
| sampling frame / manifest | `[PATH]` |
| per-stage scripts | `code/[NN]-*.py` |
| retrieval log + checkpoint | `[PATH]` |
| extraction errors | `[PATH]` |
| probe / census notes | `runs/[TAG]/` |
| frozen numbers the section quotes | `data/[...]/paper-numbers.md` |
