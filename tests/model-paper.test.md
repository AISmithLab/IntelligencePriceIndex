# Model Paper Benchmark

Learn from accepted, high-quality papers. Use them as structural and rigor benchmarks — not text sources.

## Model Paper(s)

| Paper | Venue | Year | Why selected |
|-------|-------|------|-------------|
| GPTs are GPTs: An Early Look at the Labor Market Impact Potential of LLMs | Science (working paper) | 2023 | Same domain (AI + labor); task-level analysis; exposure rubric methodology; sets the bar we must exceed empirically |
| The Macroeconomic Impact of Artificial Intelligence (Anthropic) | Anthropic Research | 2025 | Empirical rigor target; combines theoretical capability with observed deployment data; labor market outcome analysis |

## What Makes GPTs are GPTs Strong

- **Dual annotation**: Both human experts and GPT-4 label tasks → cross-validation of measurements
- **Granular task-level analysis**: Uses O*NET's 19,265 tasks and 2,087 DWAs, not just occupations
- **Exposure rubric**: Clear, reproducible rubric with E0/E1/E2 levels and explicit thresholds (50% time reduction)
- **Validation section**: Compares their measure against 6+ prior automation/exposure indices (Webb, Frey & Osborne, Brynjolfsson SML, etc.)
- **Honest limitations**: Section 3.4 explicitly lists weaknesses (subjective judgments, task-based framework validity, forward-looking uncertainty)
- **Rich descriptive analysis**: Exposure by wage, employment, skill importance, job zone, education level
- **Economically meaningful framing**: Connects to GPT (general-purpose technology) theory

## What GPTs are GPTs Lacks (Our Opportunity)

- **No observed market data**: Relies entirely on subjective rubrics, not actual prices or adoption
- **Cross-sectional**: Single snapshot in time; cannot track how exposure translates to price/wage changes
- **No continuous AI measure**: AI capability is binary (exposed or not), not linked to benchmark improvements
- **No forecasting**: Cannot project where things are headed
- **Formal economy only**: O*NET occupations miss the gig economy where price adjustment is fastest and most visible

## Benchmark Comparison

| # | Quality dimension | Model paper standard | Our draft | Status | Action needed |
|---|-------------------|---------------------|-----------|--------|---------------|
| B1 | Related work breadth | 50+ refs spanning AI, labor econ, GPT theory, prior exposure measures | — | BLOCKED | Lit review in Phase 0 |
| B2 | Related work synthesis | Groups into clear themes (LLM advancement, economic impacts, GPT theory) | — | BLOCKED | — |
| B3 | Data transparency | Full rubric in appendix; sample data in Table 1; agreement scores in Table 2 | — | BLOCKED | Must publish task taxonomy and benchmark mapping |
| B4 | Method reproducibility | Rubric is explicit enough to replicate; prompts described | — | BLOCKED | Parsing pipeline and elasticity estimation must be fully specified |
| B5 | Statistical rigor | OLS regressions with controls; summary statistics; correlation analysis | — | BLOCKED | Need elasticity regressions with proper controls |
| B6 | Validation against prior work | Dedicated Section 5 comparing to 6 prior measures; R² = 60–73% | — | BLOCKED | Compare IPI to GPTs-are-GPTs exposure, Anthropic index, etc. |
| B7 | Limitation honesty | 3 explicit subsections on methodology weaknesses | — | BLOCKED | Must address Wayback sampling bias, gig ≠ full economy, etc. |
| B8 | Writing quality / pacing | Clean academic prose; well-structured sections with clear transitions | — | BLOCKED | — |
| B9 | Figure / table design | 5 figures + 9 tables; binscatter plots; exposure distributions | — | BLOCKED | IPI time series, elasticity charts, forecast scenario plots |
| B10 | Contribution framing | "GPTs are GPTs" — memorable, conceptually clear | — | BLOCKED | "CPI for the mind" — strong framing, needs to be delivered |

## Lessons Learned

1. **Dual measurement validates**: Using both human and model annotations strengthens credibility. We should consider having AI benchmark scores validated by expert assessment.
2. **Granularity wins**: Task-level (not occupation-level) analysis is what made the paper compelling. Our task-level pricing is even more granular.
3. **Validation section is essential**: Must compare IPI to existing measures (GPTs-are-GPTs exposure scores, Anthropic index, BLS wage data) to show our index adds value.
4. **Honest limitations build trust**: Section 3.4 listing weaknesses before reviewers find them. We need the same.
5. **Memorable framing matters**: "GPTs are GPTs" is a meme-worthy title. "Intelligence Price Index" and "CPI for the mind" have similar potential.
