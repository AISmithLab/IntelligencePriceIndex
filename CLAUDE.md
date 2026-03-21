# IntelligencePriceIndex — Agent Instructions

## Core Philosophy

### 1. Minimize Interruption

Do not ask the user for confirmation unless:
- You are about to propose or change a **major plan** (scope, architecture, research direction).
- You need to **delete local files** that contain non-trivial work.
- You need to **crawl a website** where the IP might get banned.
- A task is **genuinely ambiguous** and guessing wrong would waste significant time.

For everything else — file creation, code execution, exploratory analysis, draft writing — just do it. Prefer action over asking. If a decision is reversible, make the best call and move on.

### 2. Auditable Progress Record

Maintain `progress.md` at the project root. This is the single source of truth for what has been done.

Format:
- **Latest entry at the top** (reverse chronological).
- Each entry: date, title, bullet summary of what was done, key decisions, outputs produced.
- The user should be able to open `progress.md` at any time and immediately see current status.

Update `progress.md` after every meaningful milestone (experiment completed, section drafted, data collected, tool built, etc.).

### 3. Agile Research Process

**Pilot before scale.** Before any large computational task (big data collection, full-corpus analysis, expensive API calls), run a small pilot first. Validate the approach works, check the output quality, then scale up.

**Maintain a living paper draft.** The paper is the primary deliverable. Keep it current with the latest results.

### 4. Plans as First-Class Artifacts

Plans are versioned, co-located, and checked into the repository — not ephemeral conversation context.

- **Lightweight plans** (small changes, single-session work): write directly in `progress.md` or as inline notes. No ceremony needed.
- **Execution plans** (multi-step, multi-session, or architecturally significant work): create a dedicated plan file in `plans/active/` with scope, steps, progress log, and decision rationale. Update the plan as work proceeds.

When a plan is complete, move it from `plans/active/` to `plans/completed/`. This creates a durable record of what was planned, what actually happened, and why decisions were made.

Track known technical debt in `plans/tech-debt-tracker.md` — a living document of shortcuts taken, things deferred, and cleanup needed. Each entry should note what, why it was deferred, and rough priority.

### Structure

```
plans/
    active/              execution plans currently in progress
    completed/           finished plans (moved here when done)
    tech-debt-tracker.md known shortcuts, deferred work, cleanup needed
```

### Plan file format

```markdown
# Plan: [title]

**Status:** active | blocked | completed
**Created:** YYYY-MM-DD
**Goal:** one-line summary

## Scope
What this plan covers and what it does not.

## Steps
- [ ] Step 1
- [ ] Step 2
...

## Decision Log
- YYYY-MM-DD: [decision and rationale]

## Progress
- YYYY-MM-DD: [what was done]
```

Agents should read `plans/active/` at session start to understand ongoing work without relying on external context.

### 5. Paper Test Infrastructure

Every claim in the paper must survive scrutiny before submission. Tests are modular, mapped 1:1 to draft sections, and driven by two complementary lenses:

**Lens A — Reviewer Simulation.** For each section, anticipate how a critical reviewer would attack the experiments, claims, methodology, and framing. Each anticipated critique becomes a test case: either the draft already addresses it (PASS), needs revision (FAIL), or requires additional experiments (BLOCKED). This is the primary defense against desk-reject and major-revision feedback.

**Lens B — Model Paper Comparison.** Identify a model paper (an accepted, high-quality paper in the same domain or venue). Use it as a structural and rigor benchmark — not a text source. For each section, test whether our draft meets the standard the model paper sets: depth of related work, methodological transparency, statistical rigor, limitation honesty, etc.

### Test structure

Each draft section in `drafts/sections/` has a corresponding test file in `tests/`:

```
tests/
    model-paper.md           notes on the model paper: what makes it strong, section-by-section
    abstract.test.md
    introduction.test.md
    related-work.test.md
    method.test.md
    findings.test.md
    discussion.test.md
    limitations.test.md
    conclusion.test.md
```

### Test file format

```markdown
# Tests: [Section Name]

**Draft file:** drafts/sections/[section].md
**Last reviewed:** YYYY-MM-DD

## Reviewer Simulation

| # | Critique | Severity | Status | Response |
|---|----------|----------|--------|----------|
| R1 | "Sample size too small for claim X" | major | FAIL | Need to add power analysis |
| R2 | "No comparison to baseline Y" | major | PASS | Addressed in §3.2 |
| R3 | "Unclear how Z was operationalized" | minor | FAIL | Revise definition |

## Model Paper Comparison

| # | Quality dimension | Model paper | Our draft | Status | Gap |
|---|-------------------|-------------|-----------|--------|-----|
| M1 | Related work breadth | 80+ refs across 4 subfields | 12 refs | FAIL | Need lit review pass |
| M2 | Method reproducibility | Full pseudocode + params | Prose only | FAIL | Add algorithm box |
| M3 | Limitation depth | 6 concrete limitations | Placeholder | FAIL | Draft after findings |
```

### Status values

- **PASS** — the draft addresses this adequately; no action needed.
- **FAIL** — the draft does not yet handle this; revision or new work required.
- **BLOCKED** — cannot resolve until a dependency is met (e.g., experiment not yet run).
- **N/A** — not applicable to this section.

### Workflow

1. When a draft section is written or substantially revised, update its test file.
2. When planning new experiments, check test files for FAIL/BLOCKED items — these drive the research agenda.
3. Before any submission milestone, all tests across all sections should be PASS or N/A.

### Human workflow

The user primarily edits three things:
- **Plan documents** (`plans/active/`) — what to do and why.
- **Draft sections** (`drafts/sections/`) — the paper content.
- **Test files** (`tests/`) — what must be true for the paper to hold up.

Agents handle execution: running experiments, collecting data, updating progress, and re-rendering drafts. Tests are the contract between human judgment and agent execution.

## Paper Drafting Infrastructure

### Structure

```
drafts/
    main.md              master document — assembles sections via :(sections/file.md)
    sections/            individual section markdown files
    render.py            script to assemble and render HTML
    draft-YYYY-MM-DD.html   rendered snapshots (dated)
```

### Section Files

Each section is a standalone markdown file in `drafts/sections/`. Example sections:

```
sections/abstract.md
sections/introduction.md
sections/related-work.md
sections/method.md
sections/findings.md
sections/discussion.md
sections/limitations.md
sections/conclusion.md
```

Add or rename sections as the paper evolves.

### Assembly

`drafts/main.md` defines section order using include directives:

```
# Paper Title

:(sections/abstract.md)

:(sections/introduction.md)

...
```

### Rendering

Run `python3 drafts/render.py` to produce `drafts/draft-YYYY-MM-DD.html`.

The render script:
1. Reads `main.md` and resolves `:(sections/file.md)` includes.
2. Converts the assembled markdown to HTML.
3. Wraps it in a print-friendly template with a dated "WORKING DRAFT" banner.
4. Writes to `drafts/draft-YYYY-MM-DD.html`.

**Re-render after every substantive draft change.**

## Project Structure

```
CLAUDE.md              this file
progress.md            reverse-chronological progress log
plans/                 execution plans, completed plans, tech debt
  active/              plans currently in progress
  completed/           finished plans
  tech-debt-tracker.md known shortcuts and deferred work
drafts/                paper drafts and rendering
tests/                 paper unit tests (1:1 with draft sections)
  model-paper.md       model paper analysis
  *.test.md            per-section test files
code/                  scripts, pipelines, analysis code
data/                  datasets and derived outputs
runs/                  run-specific logs, checkpoints, temporary artifacts
```

## Conventions

- Save reusable code to `code/`, not inline in notebooks or runs.
- Save collected/derived data to `data/`.
- Save run-specific notes and temporary artifacts to `runs/<tag>/`.
- Use `progress.md` for the audit trail, not git log.
- Citation placeholders: `[CITE-key]`.
- When referencing figures that don't exist yet, use HTML comments: `<!-- FIGURE: description -->`.
