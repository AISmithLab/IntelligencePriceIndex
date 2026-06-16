## 5. Discussion

### 5.1 The IPI as a Measurement Framework

The Intelligence Price Index provides something the AI-labor literature has lacked: a continuous, market-based measure of how AI capability improvements translate into economic outcomes for cognitive workers. Unlike exposure indices that classify occupations into discrete risk categories [CITE-eloundou-2023, CITE-felten-2021], the IPI produces a time series that can be tracked, decomposed, and forecasted. Unlike wage studies that rely on aggregate labor statistics with long reporting lags, the IPI can be updated as frequently as new platform data and benchmark scores become available. Both the IPI and the CPI face the same fundamental challenge—quality change over time—and both address it through matched-model tracking of the same items across periods.

### 5.2 Reconciling Inflation and AI Deflation

Our most important finding is the coexistence of sustained price inflation (2019–2024) with mounting AI deflationary pressure that became visible as price deflation only in 2025. This is not a contradiction. It reflects the interaction of multiple forces:

**Platform lifecycle effects** dominated the early period. Fiverr's transformation from a novelty marketplace to a professional services platform drove natural price inflation as the seller base professionalized and the platform's pricing norms matured. These effects are independent of AI and would have occurred regardless.

**Survivorship selection** amplifies the inflation signal, since sellers displaced by AI or competition exit the panel rather than appearing as price declines (see Section 6 for a full discussion of this limitation).

**AI as deflationary headwind.** Our structural break analysis and the 2025 reversal suggest that AI has been exerting deflationary pressure throughout the period, but this pressure was initially overwhelmed by the inflationary forces above. The observed pattern—rising prices that decelerate after AI launches, then finally reverse—is consistent with a model in which AI substitution gradually erodes the pricing power of human cognitive workers.

The 2025 reversal (IPI peak of 312 in Q4 2024 to 246 in Q2 2025) is particularly noteworthy because it occurs *across categories simultaneously*. Previous AI releases (ChatGPT, Stable Diffusion) affected specific categories; the 2025 decline suggests a broader, cross-category deflationary event consistent with the latest generation of AI models achieving multimodal, general-purpose competence.

### 5.3 The Price Elasticity of Intelligence: A Taxonomy

Our elasticity estimates suggest a three-tier taxonomy of AI's economic impact on cognitive tasks:

**Tier 1: Direct substitution (β < 0).** Audio services (voiceover, narration) are the clearest case, with β = −0.49. In these categories, AI produces output that is functionally equivalent to the human deliverable: a synthetic voice reading a script is, for many commercial applications, indistinguishable from a human recording. The "product" is the output itself, and AI can produce it at near-zero marginal cost.

**Tier 2: Shadow deflation (0 < β < 0.5).** Writing and coding show positive elasticities but with decelerating price growth after AI launches. In these categories, AI augments human productivity (writers use ChatGPT for drafts; developers use Copilot for boilerplate) while buyers increasingly substitute AI-generated output for simple tasks. The net effect on *surviving* sellers' prices may be positive (they handle more complex work), but the aggregate market shrinks as routine tasks are automated. The positive β captures the selection effect; the shadow deflation captures the missing counterfactual.

**Tier 3: Complementarity (β > 0.5).** Design and marketing show strongly positive elasticities. In these categories, AI tools function as productivity multipliers—designers use Midjourney for rapid ideation, marketers use LLMs for content drafts—but the *service* remains fundamentally about human judgment, strategic thinking, and client interaction. AI makes the worker more productive, enabling higher-value outputs and higher prices. This is the "complementarity" channel theorized by Autor [CITE-autor-2015] and Brynjolfsson, Li, and Raymond [CITE-brynjolfsson-2023], operating through task-level complementarity rather than occupation-level exposure.

### 5.4 Implications

**For workers:** The heterogeneity of elasticities implies different optimal responses by task type. Workers in direct-substitution categories face genuine displacement risk and should consider transitioning to adjacent categories with complementarity dynamics. Workers in shadow-deflation categories should actively leverage AI tools to maintain productivity advantages. Workers in complementarity categories benefit from AI improvements and should deepen their integration of AI tools into their workflows.

**For platforms:** Gig platforms can use IPI-style monitoring to anticipate category-level demand shifts. Categories approaching the substitution threshold (declining IPI trajectory) may require platform intervention—upskilling programs, new task categories, quality certification—to manage the transition.

**For policymakers:** The IPI provides a leading indicator of labor market disruption that is more timely and granular than aggregate wage statistics. A sustained decline in the IPI for a category signals active displacement; a rising IPI signals complementarity. Monitoring these trajectories can inform retraining investments and social safety net design.

### 5.5 Comparison to Prior Work

Our findings are broadly consistent with, but more nuanced than, prior studies. Hui, Reshef, and Zhou [CITE-hui-reshef-2023] found a 5.2% earnings decline for writing freelancers post-ChatGPT; our within-gig panel shows continued price increases but at a slower rate, suggesting that the aggregate earnings decline documented by Hui et al. was driven more by *reduced demand volume* than by per-gig price cuts for surviving sellers. Demirci, Hannane, and Zhu [CITE-demirci-2024] documented a 21% decrease in job postings for automation-prone tasks; our IPI framework captures the complementary price channel, showing how surviving sellers adjust pricing in response to the same forces that reduce posting volume.

The key insight that our panel approach adds to this literature is the **decomposition of the aggregate effect into intensive and extensive margins**: the intensive margin (within-gig price changes) and the extensive margin (gig entry and exit). Our IPI captures the intensive margin; the aggregate platform-level results of Hui et al. and Demirci et al. capture the combination of both margins.
