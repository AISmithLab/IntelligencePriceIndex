# IntelligencePriceIndex

## Overview

Research project investigating intelligence pricing trends and dynamics.

**Current status is in `progress.md` (latest entry at the top). Open work is in `plans/todo.md`.**
This file describes how to work in the repo, not where the project stands.

## The two papers

The repo carries two paper trees. They are separate documents with separate section
files and separate test files.

| Tree | Paper | Assembled by |
|---|---|---|
| `drafts/sections/` | **Intelligence Price Index** — the measurement paper | `drafts/main.md` |
| `drafts/structure/sections/` | **What Generative AI Did Not Do** — market structure | `drafts/structure/main.md` |

Test files follow the same split: `tests/<section>.test.md` covers the IPI paper,
`tests/structure-<section>.test.md` covers the second one.

## For Human Contributors

You primarily work in three places:

### 1. Plans (`plans/`)
- **`plans/todo.md`** — the master to-do list. Add items, reprioritize, check things off. This is where you steer the project.
- **`plans/active/`** — execution plans for complex tasks that need their own scope and tracking. Most to-do items don't need one.

### 2. Drafts (`drafts/sections/`, `drafts/structure/sections/`)
Write and revise paper sections. Each section is a standalone markdown file. The master
document assembles them in order — `drafts/main.md` for the IPI paper, `drafts/structure/main.md`
for the market-structure paper. See **The two papers** above for which is which.

To preview the current draft as HTML:
```
python3 drafts/render.py
open drafts/draft-$(date +%Y-%m-%d).html
```

### 3. Tests (`tests/`)
Define what must be true for the paper to hold up under review.

- **`tests/master.test.md`** — quality criteria that apply to every section (clarity, flow, claim-evidence alignment).
- **`tests/<section>.test.md`** — reviewer simulation for each section. Enumerate the critiques a reviewer would raise and track whether the draft addresses them.
- **`tests/model-paper.test.md`** — benchmark against an accepted high-quality paper. What standard does it set, and does our draft meet it?

### Checking progress

Open `progress.md` — latest entry is at the top. This is the audit trail of everything that has been done.

## Project Structure

```
CLAUDE.md              agent instructions (philosophy, conventions)
setup.md               agent setup guide (bootstrapping, session start)
README.md              this file — human instructions
progress.md            reverse-chronological progress log

plans/
  todo.md              master to-do list
  active/              execution plans for complex tasks
  completed/           finished plans
  tech-debt-tracker.md known shortcuts and deferred work

drafts/
  main.md              assembles the IPI paper via :(sections/file.md)
  sections/            IPI paper section files
  structure/           the second paper — its own main.md and sections/
  render.py            markdown → HTML renderer
  draft-YYYY-MM-DD.html  dated HTML snapshots

tests/
  master.test.md       cross-section quality tests
  model-paper.test.md  model paper benchmark
  *.test.md            per-section reviewer simulation

code/                  scripts, pipelines, analysis code
data/                  datasets and derived outputs
runs/                  run-specific logs, checkpoints, artifacts
```
