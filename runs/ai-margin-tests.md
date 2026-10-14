# Step 90 — AI-exposure tests on margins the price index cannot see (EXPLORATORY)

Pages: 277,663 gig-quarters, 51,544 gigs, 2019Q4–2024Q4. Orders: 612,013, 2021Q4–2024Q4. Post = 1[quarter ≥ 2022Q4]. Exposure 0–1 (human = step-45 primary, GPT-4 = robustness), so a DiD coefficient is the post-ChatGPT change for a fully exposed vs an unexposed category. **Wild p (category)** is the wild-cluster bootstrap on 7 category clusters and is the inference to read; gig-clustered t is optimistic.

## T1 · Price per word (word-priced gigs)

Gig-quarters with a basic-package word count: 21,965 (4,612 gigs); by category: translation 8,745, writing 5,307, audio 5,228, video 1,844, marketing 442, coding 265, design 134.

Within-gig interrupted time series (gig FE, linear trend, Post, Post × trend), real 2020Q1 dollars, per quarter in log points:

| Category | Outcome | trend | Post (level) | t | Post × trend | t | n | gigs |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| translation | log price/word | +0.0274 | -0.0919 | -4.93 | -0.0096 | -2.08 | 8,616 | 1,838 |
| translation | log price | +0.0168 | -0.0718 | -3.59 | -0.0033 | -0.73 | 8,616 | 1,838 |
| translation | log words | -0.0106 | +0.0201 | +1.14 | +0.0064 | +1.57 | 8,616 | 1,838 |
| writing | log price/word | +0.0338 | -0.0585 | -2.23 | -0.0270 | -3.57 | 5,226 | 1,062 |
| writing | log price | +0.0382 | -0.0893 | -3.01 | -0.0126 | -1.64 | 5,226 | 1,062 |
| writing | log words | +0.0044 | -0.0308 | -1.25 | +0.0144 | +2.17 | 5,226 | 1,062 |

DiD — log real price per word (translation + writing word-priced gigs) vs log real basic price (audio + video), gig + quarter FE:

| Outcome · exposure | Coef | SE (gig) | t | wild p (category) | n | gigs | mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| treat × post | -0.0914 | 0.0183 | -4.99 | 0.133 | 86,740 | 13,832 | 2.136 |

## T2 · Repeat-buyer share (orders)

| category | exposure | repeat_buyer post | repeat_buyer pre |
|---|---|---|---|
| translation | 0.840 | 0.454 | 0.414 |
| writing | 0.686 | 0.399 | 0.344 |
| marketing | 0.624 | 0.334 | 0.278 |
| coding | 0.588 | 0.386 | 0.332 |
| design | 0.508 | 0.374 | 0.358 |
| video | 0.402 | 0.370 | 0.331 |
| audio | 0.248 | 0.440 | 0.398 |

| Outcome · exposure | Coef | SE (gig) | t | wild p (category) | n | gigs | mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| repeat_buyer · human | -0.0156 | 0.0139 | -1.12 | 0.242 | 610,226 | 33,051 | 0.377 |
| repeat_buyer · GPT-4 | +0.0131 | 0.0132 | +0.99 | 0.819 | 610,226 | 33,051 | 0.377 |

Event study (human), ref 2022Q3: 2021Q4 -0.011 (t -0.4), 2022Q1 -0.004 (t -0.2), 2022Q2 +0.004 (t +0.2), 2022Q4 -0.054 (t -2.5), 2023Q1 -0.056 (t -2.3), 2023Q2 +0.005 (t +0.2), 2023Q3 -0.016 (t -0.7), 2023Q4 +0.037 (t +1.5), 2024Q1 -0.014 (t -0.5), 2024Q2 +0.009 (t +0.3), 2024Q3 +0.000 (t +0.0), 2024Q4 +0.003 (t +0.1)

## T3 · Reviews naming AI tools or machine translation

Share of reviews (%) naming a generative-AI tool, by order year:

| category | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| audio | 0.00 | 0.01 | 0.07 | 0.13 |
| coding | 0.00 | 0.02 | 0.43 | 0.58 |
| design | 0.00 | 0.01 | 0.07 | 0.19 |
| marketing | 0.04 | 0.02 | 0.06 | 0.09 |
| translation | 0.00 | 0.02 | 0.05 | 0.17 |
| video | 0.00 | 0.01 | 0.12 | 0.16 |
| writing | 0.01 | 0.02 | 0.21 | 0.39 |

Machine-translation mentions (%), translation gigs only, by year: 2021 0.05, 2022 0.25, 2023 0.21, 2024 0.12

Reviews naming AI: 836. Share below 5 stars: 0.313 vs 0.085 for all other reviews in the same window.

## T4 · High-income-country sellers (share of gig-quarters)

| category | exposure | hi_inc post | hi_inc pre |
|---|---|---|---|
| translation | 0.840 | 0.520 | 0.507 |
| writing | 0.686 | 0.406 | 0.500 |
| marketing | 0.624 | 0.295 | 0.340 |
| coding | 0.588 | 0.168 | 0.178 |
| design | 0.508 | 0.157 | 0.181 |
| video | 0.402 | 0.258 | 0.294 |
| audio | 0.248 | 0.562 | 0.604 |

| Outcome · exposure | Coef | SE (gig) | t | wild p (category) | n | gigs | mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| hi_inc · human (quarter + category FE) | +0.0039 | 0.0188 | +0.21 | 0.970 | 252,797 | 48,107 | 0.332 |
| hi_inc · GPT-4 (quarter + category FE) | +0.0164 | 0.0169 | +0.97 | 0.887 | 252,797 | 48,107 | 0.332 |

## T5 · Gig descriptions: generative-AI mentions and human/no-AI claims (%)

**mentions generative AI**

| category | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| audio | 0.06 | 0.09 | 0.09 | 0.13 | 0.60 | 1.08 |
| coding | 0.06 | 0.07 | 0.11 | 0.22 | 4.44 | 10.15 |
| design | 0.00 | 0.04 | 0.05 | 0.10 | 0.39 | 1.00 |
| marketing | 0.00 | 0.03 | 0.02 | 0.13 | 0.54 | 0.97 |
| translation | 0.00 | 0.00 | 0.17 | 0.16 | 0.78 | 1.69 |
| video | 0.00 | 0.13 | 0.32 | 0.59 | 1.68 | 2.72 |
| writing | 0.00 | 0.00 | 0.03 | 0.01 | 1.16 | 4.25 |

**claims human / no-AI work**

| category | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| audio | 0.45 | 0.33 | 0.25 | 0.16 | 0.37 | 0.68 |
| coding | 0.57 | 0.79 | 0.79 | 0.66 | 0.54 | 0.62 |
| design | 0.41 | 0.56 | 0.55 | 0.64 | 0.64 | 0.94 |
| marketing | 0.19 | 0.09 | 0.17 | 0.10 | 0.24 | 0.43 |
| translation | 4.06 | 3.53 | 3.43 | 3.74 | 4.36 | 4.08 |
| video | 0.11 | 0.34 | 0.47 | 0.44 | 0.53 | 0.44 |
| writing | 0.41 | 0.52 | 0.52 | 0.41 | 0.93 | 2.67 |

| Outcome · exposure | Coef | SE (gig) | t | wild p (category) | n | gigs | mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| desc_ai · human (gig FE) | +0.0120 | 0.0038 | +3.16 | 0.147 | 272,918 | 48,163 | 0.012 |
| desc_anti_ai · human (gig FE) | +0.0119 | 0.0045 | +2.63 | 0.140 | 272,918 | 48,163 | 0.009 |

## T6 · Tier ladder, T7 · listed delivery time and revisions (within gig)

| category | exposure | ladder post | ladder pre | ldur1 post | ldur1 pre | rev1c post | rev1c pre |
|---|---|---|---|---|---|---|---|
| translation | 0.840 | 1.608 | 1.642 | 3.893 | 3.885 | nan | nan |
| writing | 0.686 | 1.337 | 1.315 | 4.089 | 4.228 | nan | nan |
| marketing | 0.624 | 1.538 | 1.465 | 4.343 | 4.387 | nan | nan |
| coding | 0.588 | 1.570 | 1.653 | 4.061 | 4.069 | nan | nan |
| design | 0.508 | 1.362 | 1.314 | 4.035 | 4.208 | nan | nan |
| video | 0.402 | 1.326 | 1.316 | 4.275 | 4.394 | nan | nan |
| audio | 0.248 | 1.273 | 1.312 | 4.220 | 4.194 | nan | nan |

| Outcome · exposure | Coef | SE (gig) | t | wild p (category) | n | gigs | mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| ladder · human | -0.0147 | 0.0212 | -0.69 | 0.830 | 236,107 | 41,968 | 1.417 |
| ladder · GPT-4 | -0.0796 | 0.0213 | -3.73 | 0.414 | 236,107 | 41,968 | 1.417 |
| ldur1 · human | -0.0125 | 0.0178 | -0.70 | 0.921 | 272,919 | 48,163 | 4.171 |
| ldur1 · GPT-4 | +0.0341 | 0.0172 | +1.98 | 0.603 | 272,919 | 48,163 | 4.171 |
| rev1c · human | +nan | nan | +nan | nan | 0 | 0 | nan |
| rev1c · GPT-4 | +nan | nan | +nan | nan | 0 | 0 | nan |

ladder event study (human), ref 2022Q3 — pre-period |t| > 1.96 in 3 of 11 quarters; post coefficients: 2022Q4 +0.038, 2023Q1 +0.010, 2023Q2 +0.026, 2023Q3 -0.000, 2023Q4 -0.033, 2024Q1 -0.021, 2024Q2 +0.011, 2024Q3 -0.007, 2024Q4 -0.003

ldur1 event study (human), ref 2022Q3 — pre-period |t| > 1.96 in 0 of 11 quarters; post coefficients: 2022Q4 -0.012, 2023Q1 -0.018, 2023Q2 -0.025, 2023Q3 -0.022, 2023Q4 -0.003, 2024Q1 -0.007, 2024Q2 -0.007, 2024Q3 +0.006, 2024Q4 +0.033
