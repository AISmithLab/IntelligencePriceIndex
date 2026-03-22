# Project Brief: Intelligence Price Index

**Created:** 2026-03-21
**Goal:** Produce a submission-ready empirical paper introducing the Intelligence Price Index (IPI) — a longitudinal index tracking how AI benchmark improvements drive gig-economy task price deflation.

*This is a reference document, not an execution plan. For actionable work, see `plans/todo.md` and `plans/active/`.*

## Positioning

**What this paper is:** An empirical measurement paper that constructs a novel index linking observed market prices to AI capability improvements, estimates price elasticities, and generates forecasts. Think CPI for cognitive labor.

**What this paper is NOT:** An anecdotal exposure assessment (GPTs are GPTs) or a purely theoretical framework. We use revealed prices, not subjective rubrics.

**Key differentiation from GPTs are GPTs (model paper):**

| Dimension | GPTs are GPTs | IPI (ours) |
|-----------|--------------|------------|
| Data | Subjective exposure rubrics (human + GPT-4 labels) | Observed market prices from gig platforms |
| Temporal | Cross-sectional snapshot | Longitudinal panel (multiple years via Wayback Machine) |
| AI measure | Binary exposure (E0/E1/E2) | Continuous benchmark scores over time |
| Forecasting | None | Forward-looking price paths under AI scaling scenarios |
| Granularity | O*NET occupations (formal economy) | Gig-economy tasks (market-priced, rapidly adjusting) |
| Core metric | Exposure percentage | Price elasticity of intelligence |

**Target venue/quality:** Empirical rigor of the Anthropic labor market impacts paper; breadth of GPTs are GPTs. Data-driven, not anecdotal.

## Paper Structure

| # | Section | Content |
|---|---------|---------|
| 1 | Introduction | AI as deflationary force on cognitive labor; the IPI concept; contributions |
| 2 | Related Work | AI & labor (Autor, Acemoglu, Brynjolfsson); gig economy pricing; AI benchmarks as capability measures; prior exposure/automation indices |
| 3 | Data & Methods | Platform selection; Wayback Machine collection; task taxonomy; benchmark mapping; price extraction; panel construction; elasticity estimation |
| 4 | Descriptive Findings | Price trends by category; raw price trajectories; summary statistics |
| 5 | Elasticity Estimates | Price elasticity of intelligence by task category; heterogeneity analysis; routine vs. judgment-intensive tasks |
| 6 | The Intelligence Price Index | Index construction; forward-looking forecasts under AI scaling scenarios; worker adaptation patterns (upskilling, price reduction) |
| 7 | Discussion | Implications for workers, firms, policymakers; comparison to prior indices; what IPI reveals that exposure scores don't |
| 8 | Limitations | Platform coverage bias; Wayback Machine sampling; benchmark-to-task mapping validity; gig economy ≠ full economy |
| 9 | Conclusion | Summary; the IPI as a living instrument |

## Key Risks

| Risk | Mitigation |
|------|-----------|
| Wayback Machine has sparse Fiverr coverage | Pilot first; expand to other platforms if needed |
| Price extraction from archived HTML is unreliable | Build robust parser; validate on sample |
| Benchmark scores don't cleanly map to gig task categories | Use multiple benchmarks per category; sensitivity analysis |
| Gig economy prices reflect many factors beyond AI | Control variables; difference-in-differences; acknowledge in limitations |
| Worker tracking infeasible at scale | Fall back to category-level analysis; use individual cases as illustrations |

## Decision Log

- 2026-03-21: Initial brief created. Targeting empirical paper with longitudinal gig-economy price data linked to AI benchmarks.
- 2026-03-21: Converted from execution plan to reference brief. All actionable items live in `plans/todo.md`.
