# IntelligencePriceIndex — Agent Philosophy & Instructions

For project setup and directory structure, see `setup.md`.
For human-facing instructions, see `README.md`.

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

#### Plan file format

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

Every claim in the paper must survive scrutiny before submission. Tests are modular and organized in three layers:

**Layer 1 — Master Tests (`tests/master.test.md`).** Cross-cutting quality criteria that apply to every section: clarity, logical flow, claim-evidence alignment, notation consistency, etc. These are checked against the whole draft.

**Layer 2 — Section Tests (`tests/<section>.test.md`).** Reviewer simulation for each individual section. Anticipate how a critical reviewer would attack the experiments, claims, methodology, and framing specific to that section. Each anticipated critique becomes a test case: PASS, FAIL, or BLOCKED.

**Layer 3 — Model Paper Tests (`tests/model-paper.test.md`).** A separate, standalone comparison against one or more accepted high-quality papers. Benchmarks our draft's rigor, structure, and depth against the standard those papers set — not section-by-section inside each test file, but as a dedicated cross-cutting analysis.

#### Section test file format

```markdown
# Tests: [Section Name]

**Draft file:** drafts/sections/[section].md
**Last reviewed:** YYYY-MM-DD

## Reviewer Simulation

| # | Critique | Severity | Status | Response |
|---|----------|----------|--------|----------|
| R1 | "Sample size too small for claim X" | major | FAIL | Need to add power analysis |
| R2 | "No comparison to baseline Y" | major | PASS | Addressed in §3.2 |
```

#### Status values

- **PASS** — the draft addresses this adequately; no action needed.
- **FAIL** — the draft does not yet handle this; revision or new work required.
- **BLOCKED** — cannot resolve until a dependency is met (e.g., experiment not yet run).
- **N/A** — not applicable.

#### Workflow

1. When a draft section is written or substantially revised, update its test file.
2. When planning new experiments, check test files for FAIL/BLOCKED items — these drive the research agenda.
3. Before any submission milestone, all tests across all layers should be PASS or N/A.

## Conventions

- Save reusable code to `code/`, not inline in notebooks or runs.
- Save collected/derived data to `data/`.
- Save run-specific notes and temporary artifacts to `runs/<tag>/`.
- Use `progress.md` for the audit trail, not git log.
- Citation placeholders: `[CITE-key]`.
- When referencing figures that don't exist yet, use HTML comments: `<!-- FIGURE: description -->`.
- Re-render the draft HTML after every substantive draft change.
