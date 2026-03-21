# Project Setup — For AI Agents

This file teaches agents how to bootstrap and orient themselves in the IntelligencePriceIndex project.

## First-time setup

If the project directories don't exist yet, create them:

```
mkdir -p drafts/sections code data runs plans/active plans/completed tests
```

Ensure these files exist:
- `drafts/main.md` — master document assembling sections via `:(sections/file.md)`
- `drafts/render.py` — markdown-to-HTML renderer (zero external dependencies)
- `plans/tech-debt-tracker.md` — technical debt log
- `tests/master.test.md` — cross-section quality tests
- `tests/model-paper.test.md` — model paper benchmark tests
- `progress.md` — reverse-chronological progress log

For each section listed in `drafts/main.md`, ensure a corresponding:
- `drafts/sections/<section>.md` — the draft content
- `tests/<section>.test.md` — the reviewer simulation tests

## Session start checklist

At the start of each session, read these files to orient:

1. `CLAUDE.md` — philosophy and operating instructions.
2. `progress.md` — what has been done (latest entry at top).
3. `plans/active/` — any in-progress execution plans.
4. `plans/tech-debt-tracker.md` — known debt and deferred work.
5. `tests/master.test.md` — cross-cutting quality status.

Then check `git status` and `git log --oneline -5` for recent changes.

## Project structure

```
CLAUDE.md              agent philosophy and instructions
setup.md               this file — agent setup guide
README.md              human-facing project overview
progress.md            reverse-chronological progress log
plans/
  active/              execution plans currently in progress
  completed/           finished plans (moved here when done)
  tech-debt-tracker.md known shortcuts and deferred work
drafts/
  main.md              master document — assembles sections via :(sections/file.md)
  sections/            individual section markdown files
  render.py            script to assemble and render HTML
  draft-YYYY-MM-DD.html  rendered snapshots (dated)
tests/
  master.test.md       cross-section tests (applies to all sections)
  model-paper.test.md  model paper benchmark (separate from section tests)
  *.test.md            per-section reviewer simulation tests
code/                  scripts, pipelines, analysis code
data/                  datasets and derived outputs
runs/                  run-specific logs, checkpoints, temporary artifacts
```

## Paper rendering

Run from project root:

```
python3 drafts/render.py
```

This produces `drafts/draft-YYYY-MM-DD.html`. Re-render after every substantive draft change.

## Adding a new draft section

1. Create `drafts/sections/<section>.md`.
2. Add `:(sections/<section>.md)` to `drafts/main.md` in the correct position.
3. Create `tests/<section>.test.md` with the reviewer simulation template.
4. Re-render the draft.
