# Progress Log

## 2026-03-21 — Restructured docs and test infrastructure

- Decoupled `CLAUDE.md` into three files:
  - `CLAUDE.md` — agent philosophy and operating instructions only.
  - `setup.md` — agent bootstrapping and session-start checklist.
  - `README.md` — human-facing project overview and contributor guide.
- Restructured tests into three layers:
  - `tests/master.test.md` — cross-section quality criteria (applies to all sections).
  - `tests/<section>.test.md` — reviewer simulation only (removed model paper comparison from individual sections).
  - `tests/model-paper.test.md` — standalone model paper benchmark (replaces old `model-paper.md`).

## 2026-03-21 — Added Paper Test Infrastructure

- Added Philosophy #5: Paper test infrastructure with two lenses (reviewer simulation + model paper comparison).
- Created `tests/` directory with per-section test files (`*.test.md`) mirroring `drafts/sections/`.
- Created `tests/model-paper.md` for model paper analysis.
- Test files use PASS/FAIL/BLOCKED/N/A status for each critique and quality dimension.
- Clarified human workflow: user primarily edits plans, drafts, and test files; agents handle execution.

## 2026-03-21 — Added Plans Infrastructure

- Added Philosophy #4: Plans as first-class artifacts.
- Created `plans/active/`, `plans/completed/`, `plans/tech-debt-tracker.md`.
- Updated `CLAUDE.md` with plan file format, lifecycle (active → completed), and conventions.

## 2026-03-21 — Project Scaffolding

- Created `CLAUDE.md` with three core principles: minimize interruption, auditable progress, agile process.
- Set up drafts infrastructure: `drafts/main.md`, `drafts/sections/`, `drafts/render.py`.
- Created `progress.md` (this file) for reverse-chronological audit trail.
- Created project directories: `code/`, `data/`, `runs/`.
- Placeholder section files created for paper draft.
