## 4. Findings

### 4.1 Descriptive Statistics

Our final panel comprises 1,245 gigs observed in at least two quarters (of 1,908 unique gigs with price data), yielding 21,461 price observations across 500 sellers and 9 service categories. Table 1 summarizes the price distribution by category.

<!-- FIGURE: Table 1 — Summary statistics by category: N gigs, N obs, median price, IQR, min/max year -->

The median basic price across all categories is $25, with substantial variation both across and within categories. Design gigs range from $5 (simple thumbnail designs) to $500+ (comprehensive brand identity packages). Coding gigs show the widest price dispersion, reflecting the heterogeneity of software tasks from basic WordPress customization ($15) to complex API development ($200+).

### 4.2 The Intelligence Price Index: 2017–2025

Figure 1 presents the composite IPI from Q3 2017 to Q2 2025.

<!-- FIGURE: Figure 1 — Composite IPI time series with key AI launch events marked as vertical lines -->

The IPI exhibits three distinct phases:

**Phase 1: Pre-AI Baseline (2017–2019).** The index fluctuates around 70–100, reflecting the normal pricing dynamics of a maturing marketplace. The base period (2019Q1 = 100) captures the market before significant generative AI deployment.

**Phase 2: Sustained Inflation (2020–2024).** The IPI rises steadily from 77 (Q1 2020) to a peak of 312 (Q4 2024)—a 212% increase over the 2019Q1 base (or 305% from the Q1 2020 trough). This trend reflects several concurrent forces:

- **Platform maturation.** Fiverr shifted from a "$5 for everything" marketplace to a professional services platform with premium pricing tiers, especially after its 2019 IPO.
- **Pandemic demand surge.** The COVID-19 pandemic accelerated demand for digital freelance services, particularly in 2020–2021, enabling sellers to raise prices.
- **General inflation.** The 2021–2023 inflationary environment raised the cost of living for freelancers, putting upward pressure on posted prices.
- **Survivor premium.** Our panel, by construction, tracks gigs that persisted over time. Sellers who survived market competition tend to be more established and to raise prices as they accumulate reviews and reputation.

**Phase 3: The 2025 Reversal (Q1–Q2 2025).** The IPI declined from 312 (Q4 2024) to 246 (Q2 2025), a **21% drop in two quarters**. This is the sharpest decline in the entire series and coincides with the availability of the most capable AI systems to date—GPT-4o, Claude 3.5 Sonnet, o1, and their derivatives. While we cannot make a causal claim from this observation alone, the timing is striking: after years of steady inflation, prices reversed precisely when AI capabilities made their most rapid advances.

### 4.3 Category-Level Price Trajectories

Category-level indices reveal substantial heterogeneity beneath the composite trend.

<!-- FIGURE: Figure 2 — Panel of 9 category-level price indices, each with AI capability overlay (right axis) -->

**Design** (weight: 0.464) dominates the composite index. Design prices rose 366% over the period, driven by the shift from "$5 logos" to professional brand identity work. Even Stable Diffusion's August 2022 release and Midjourney's rapid improvement did not reverse this trend within our panel—suggesting that surviving designers adapted by moving upmarket rather than competing on price with AI tools.

**Audio** (weight: 0.076) shows the most distinctive pattern: a price elasticity of intelligence of β = −0.49 (p < 0.001), the only statistically significant *negative* elasticity in our panel. This is consistent with the direct substitutability of AI text-to-speech (ElevenLabs, launched January 2023) and AI music generation (Suno, Udio) for human voiceover and music production services. The audio category is where AI output most closely approximates a drop-in replacement for the human-produced deliverable.

**Writing** (weight: 0.120) shows a positive but modest elasticity (β = 0.21, p < 0.01), with a 95% total price increase. However, the post-ChatGPT structural break analysis reveals a nuanced picture: while prices continued rising in levels, the *rate* of increase slowed markedly after November 2022. Writing may be experiencing what we term *shadow deflation*: a deflationary effect that manifests not as falling prices but as the absence of price increases that would have occurred in the counterfactual without AI, masked by the secular inflationary trend.

**Coding** (weight: 0.083) shows a similar pattern to writing (β = 0.30, p < 0.001), with sustained price increases but a post-ChatGPT effect of +130%—lower than the pre-ChatGPT trajectory would have predicted. The coding category may benefit from strong complementarity effects: AI coding assistants (GitHub Copilot, Cursor) increase developer productivity, potentially allowing freelancers to deliver more value per gig and justify higher prices.

**Marketing** (weight: 0.051) shows a strongly positive elasticity (β = 0.70, p < 0.001), suggesting that AI capabilities in content generation have enhanced rather than displaced marketing services. This is consistent with marketing being a "tool-augmented" category where AI is an input to, rather than a substitute for, the marketing service.

### 4.4 Price Elasticity of Intelligence

Table 2 presents the estimated price elasticities of intelligence across all categories.

| Category | β | SE | p-value | R² | Total Δ% | Post-ChatGPT Δ% | N gigs |
|----------|------|-------|---------|------|---------|----------------|--------|
| Audio | −0.491 | 0.039 | <0.001 | 0.868 | +685% | +240% | 62 |
| Writing | +0.206 | 0.058 | 0.002 | 0.334 | +95% | +107% | 226 |
| Coding | +0.295 | 0.039 | <0.001 | 0.693 | +328% | +130% | 184 |
| Marketing | +0.700 | 0.041 | <0.001 | 0.920 | +4097% | +314% | 71 |
| Design | +1.099 | 0.223 | <0.001 | 0.473 | +366% | +141% | 313 |
| *Video* | — | — | — | — | — | — | *158* |
| *Translation* | — | — | — | — | — | — | *26* |
| *Data Entry* | — | — | — | — | — | — | *46* |
| *Data Analysis* | — | — | — | — | — | — | *38* |

*Italic categories* excluded from elasticity estimation due to insufficient quarterly overlap between the price index and AI capability index (fewer than 6 common quarters). Video, translation, data entry, and data analysis have fewer benchmark data points or too few panel gigs in overlapping periods to produce reliable estimates.

Among the five estimated categories, all elasticities are statistically significant at p < 0.01. The range from −0.49 to +1.10 underscores the heterogeneity of AI's impact across cognitive tasks. The key determinant appears to be **output substitutability**: categories where AI can produce a deliverable that is a near-perfect substitute for the human version (voiceover, simple narration) show deflation, while categories where AI augments a creative or strategic process (brand design, marketing strategy) show complementarity.

### 4.5 Structural Break Analysis

Table 3 shows the change in category price indices around major AI model releases.

<!-- FIGURE: Table 3 — Structural break results for ChatGPT, GPT-4, Stable Diffusion, GPT-4o/Claude 3.5 -->

No single AI launch produced an immediate, sharp price decline in any category. Instead, the pattern is one of **deceleration followed by reversal**: the rate of price increases slowed after each major AI release, with the cumulative effect becoming visible only in 2025. This is consistent with a gradual market adjustment process in which:

1. AI tools are initially adopted by *buyers* as complements (reducing demand for simple gigs but increasing demand for complex ones).
2. *Sellers* respond by moving upmarket, raising prices for premium services.
3. As AI capabilities improve further, the frontier of substitutable tasks expands, eventually catching up with the upmarket repositioning.
4. The 2025 reversal may represent the point where expansion of AI substitution outpaced sellers' ability to differentiate.

The strongest structural break is in the writing category following ChatGPT's November 2022 launch: while prices continued to rise in absolute terms (+33%), this was markedly lower than the pre-ChatGPT trend would have predicted. This is consistent with Hui, Reshef, and Zhou's [CITE-hui-reshef-2023] finding of a 5.2% earnings decline for writing freelancers, noting that our matched-panel approach captures a different margin (within-gig price changes for surviving sellers rather than aggregate platform earnings).
