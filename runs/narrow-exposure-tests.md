# Step 94 — AI exposure with 35 clusters (EXPLORATORY)

Exposure from step 93 (frozen before this ran). Post = 1[quarter ≥ 2022Q4]. **wild p** = wild-cluster bootstrap on the 35 narrow cells, the inference to read. **Gap** = implied post-ChatGPT price difference between the most- and least-exposed cell (coefficient × exposure range).

## A · Cross-section of the 35 narrow indices

| Outcome | Exposure | Spearman ρ | p | Pearson r | p | WLS slope (per 0.1 exposure) | t |
|---|---|---:|---:|---:|---:|---:|---:|
| real change 2020Q1→2024Q4 | human | +0.246 | 0.161 | +0.120 | 0.498 | -0.0052 | -0.27 |
| real change 2020Q1→2024Q4 | gpt4 | +0.269 | 0.125 | +0.211 | 0.231 | +0.0169 | +0.97 |
| growth post − pre (log/qtr) | human | +0.082 | 0.646 | +0.137 | 0.441 | +0.0015 | +0.78 |
| growth post − pre (log/qtr) | gpt4 | +0.225 | 0.201 | +0.304 | 0.081 | +0.0029 | +1.80 |

| Narrow cell | Exposure (human) | GPT-4 | Real change | Growth pre | post |
|---|---:|---:|---:|---:|---:|
| translation-translation | 0.84 | 0.88 | +5.3% | +0.0080 | +0.0022 |
| writing-copywriting | 0.77 | 0.88 | +73.1% | +0.0451 | +0.0070 |
| writing-ebook_book | 0.77 | 0.88 | +67.8% | +0.0368 | +0.0212 |
| writing-other | 0.69 | 0.82 | +68.2% | +0.0407 | +0.0107 |
| coding-automation_bot | 0.68 | 0.95 | +142.1% | +0.0418 | +0.0726 |
| design-ui_ux_web | 0.68 | 0.83 | +143.9% | +0.0518 | +0.0315 |
| marketing-social_media | 0.68 | 0.55 | +53.9% | +0.0218 | +0.0170 |
| translation-subtitle | 0.68 | 0.92 | +3.1% | +0.0042 | +0.0088 |
| writing-content_seo | 0.66 | 0.71 | +65.4% | +0.0324 | +0.0223 |
| coding-web_dev | 0.65 | 0.92 | +100.0% | +0.0467 | +0.0272 |
| marketing-other | 0.62 | 0.55 | +89.9% | +0.0419 | +0.0225 |
| writing-editing | 0.62 | 0.81 | +71.5% | +0.0392 | +0.0199 |
| coding-other | 0.59 | 0.92 | +77.8% | +0.0474 | +0.0274 |
| marketing-email_funnel | 0.58 | 0.50 | +148.3% | +0.0640 | +0.0371 |
| writing-resume_bio | 0.57 | 0.58 | +81.7% | +0.0450 | +0.0107 |
| coding-data_ml_ai | 0.56 | 0.69 | +72.8% | +0.0172 | +0.0542 |
| coding-backend_api | 0.54 | 0.85 | +120.9% | +0.0442 | +0.0560 |
| marketing-ads_ppc | 0.53 | 0.51 | +134.4% | +0.0697 | +0.0292 |
| design-other | 0.51 | 0.61 | +56.1% | +0.0326 | +0.0199 |
| marketing-seo | 0.51 | 0.55 | +39.3% | +0.0244 | +0.0150 |
| video-motion_intro | 0.47 | 0.53 | +46.2% | +0.0382 | +0.0047 |
| video-animation | 0.47 | 0.53 | +55.5% | +0.0333 | +0.0197 |
| video-video_editing | 0.47 | 0.53 | +52.1% | +0.0364 | +0.0285 |
| coding-mobile_app | 0.45 | 0.87 | +110.9% | +0.0495 | +0.0355 |
| design-print_merch | 0.45 | 0.57 | +50.7% | +0.0302 | +0.0154 |
| design-threed_product | 0.43 | 0.50 | +41.6% | +0.0304 | +0.0108 |
| design-logo_brand | 0.42 | 0.50 | +30.2% | +0.0198 | +0.0093 |
| design-social_graphics | 0.41 | 0.50 | +97.4% | +0.0470 | +0.0182 |
| video-other | 0.40 | 0.49 | +64.0% | +0.0326 | +0.0250 |
| design-illustration | 0.36 | 0.46 | +19.9% | +0.0157 | +0.0065 |
| audio-voiceover | 0.35 | 0.42 | +62.6% | +0.0405 | +0.0158 |
| audio-podcast | 0.29 | 0.43 | +45.9% | +0.0369 | +0.0009 |
| audio-other | 0.25 | 0.50 | +56.0% | +0.0228 | +0.0141 |
| audio-music_prod | 0.23 | 0.51 | +83.1% | +0.0439 | +0.0228 |

## B · Gig-level listed real price, Exposure × Post

249,213 gig-quarters, 37,658 gigs, 35 cells, 2019Q4–2024Q4.

| Spec | Exposure | Coef | SE (gig) | t (gig) | **wild p (35 cells)** | Gap, most vs least exposed |
|---|---|---:|---:|---:|---:|---:|
| B1 gig + quarter FE | human | +0.0434 | 0.0233 | +1.86 | **0.725** | +2.7% |
| B1 gig + quarter FE | gpt4 | +0.1576 | 0.0237 | +6.66 | **0.318** | +8.7% |
| B2 gig + family×quarter FE (within family) | human | +0.1905 | 0.0734 | +2.59 | **0.332** | +12.3% |
| B2 gig + family×quarter FE (within family) | gpt4 | +0.2588 | 0.0813 | +3.18 | **0.241** | +14.7% |
| B3 B1 + narrow-cell trends | human | +0.0648 | 0.0240 | +2.70 | **0.148** | +4.0% |
| B3 B1 + narrow-cell trends | gpt4 | +0.0509 | 0.0238 | +2.14 | **0.385** | +2.7% |

## C · Gig descriptions (step-90 near-misses), Exposure × Post

277,653 gig-quarters, 51,541 gigs, 35 cells.

| Outcome · spec | Exposure | Coef | SE (gig) | t (gig) | **wild p (35 cells)** | mean |
|---|---|---:|---:|---:|---:|---:|
| desc_ai · B1 | human | +0.0146 | 0.0035 | +4.20 | **0.011** | 0.0123 |
| desc_ai · B2 | human | -0.0032 | 0.0096 | -0.33 | **0.811** | 0.0123 |
| desc_anti_ai · B1 | human | +0.0123 | 0.0045 | +2.75 | **0.068** | 0.0093 |
| desc_anti_ai · B2 | human | -0.0054 | 0.0085 | -0.63 | **0.744** | 0.0093 |
