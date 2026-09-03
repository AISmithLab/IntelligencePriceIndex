# How reputation influences price, with task value anchored on a taxonomy node

Panel: **270,965 gig-quarter observations**, **35,826 gigs**, **65 nodes**. Real prices, 2020Q1 dollars. SEs clustered on gig.

Note this panel is **not** step 76's: there is no before/after balance requirement, because nothing here is a difference-in-differences. That is why it carries 35,826 gigs against step 76's 15,676.

## 1. Reference task value, raw and reputation-adjusted

`raw` is the node's mean `ln(real price)`, exactly as specified. `adjusted` is the node's fixed effect from a fit that also carries reputation and quarter, so it is the going rate for the WORK with the sellers' standing taken out. Both are centred on their own mean, so only the GAP between the columns is meaningful.

A positive gap means the node looks dearer than the work warrants because its sellers are well-reviewed; a negative gap means the node is underselling its reputation.

Correlation between the two rankings: **0.9699** (Spearman 0.9647). Mean absolute gap **0.0938** log points, max **0.3749**.

The ten nodes whose price is most inflated by reputation, and the ten least:

| node | gigs | median reviews | raw | adjusted | gap |
|---|---:|---:|---:|---:|---:|
| translation/interpreting | 114 | 10 | -0.4638 | -0.8387 | +0.3749 |
| translation/localization | 128 | 8 | -0.0176 | -0.3924 | +0.3748 |
| translation/language_tutoring | 236 | 21 | -0.8287 | -1.0484 | +0.2196 |
| translation/other | 1,432 | 24 | -0.1424 | -0.3451 | +0.2027 |
| marketing/paid_ads | 781 | 33 | +0.6695 | +0.4911 | +0.1784 |
| marketing/content_strategy | 158 | 25 | +1.0268 | +0.8733 | +0.1535 |
| audio/podcast | 474 | 23 | -0.2900 | -0.4341 | +0.1440 |
| marketing/other | 1,354 | 30 | -0.0387 | -0.1710 | +0.1323 |
| translation/subtitling | 397 | 40 | -1.1609 | -1.2844 | +0.1236 |
| marketing/affiliate | 362 | 28 | -0.1739 | -0.2756 | +0.1017 |
| design/merch_apparel | 63 | 921 | -0.4786 | -0.1809 | -0.2977 |
| design/logo | 822 | 623 | +0.1739 | +0.4125 | -0.2385 |
| design/social_graphics | 71 | 803 | -0.5610 | -0.3377 | -0.2232 |
| design/print_collateral | 669 | 416 | -0.0761 | +0.1296 | -0.2057 |
| design/presentation | 184 | 378 | +0.3135 | +0.5048 | -0.1914 |
| writing/press_pr | 117 | 256 | +0.1882 | +0.3726 | -0.1844 |
| writing/editing_proofreading | 635 | 330 | -0.2931 | -0.1574 | -0.1357 |
| design/brand_identity | 218 | 244 | +0.7279 | +0.8445 | -0.1166 |
| video/spokesperson_ugc | 209 | 198 | +0.0954 | +0.2051 | -0.1097 |
| translation/document_translation | 1,578 | 159 | -1.1547 | -1.0487 | -0.1060 |

## 2. Reputation at three levels

The same two reputation variables, changing only what is held fixed.

**A — between nodes** (65 nodes, one row each; no fixed effects). Does dearer work carry more reviews?

| term | coef | se | t | per doubling |
|---|---:|---:|---:|---:|
| ln(1+reviews) | +0.0968 | 0.0750 | +1.29 | +6.94% |
| rating | -6.5045 | 2.3478 | -2.77 | — |

The rating coefficient here is fit on 65 points and should not be read as a price effect: node mean rating is close to constant (Fiverr ratings sit at 4.8-5.0 almost everywhere), so it is picking up whatever else separates cheap nodes from dear ones.

**B — between gigs, within node** (node absorbed; this is the 'what is reputation worth' reading). Within-R² 0.0497.

| term | coef | se | t | per doubling |
|---|---:|---:|---:|---:|
| ln(1+reviews) | -0.1374 | 0.0049 | -28.30 | -9.08% |
| rating | +0.3235 | 0.0256 | +12.65 | — |

**C — within gig, over time** (gig absorbed; step 76's specification, re-run on this larger panel). Within-R² 0.1228.

| term | coef | se | t | per doubling |
|---|---:|---:|---:|---:|
| ln(1+reviews) | +0.1059 | 0.0034 | +30.92 | +7.62% |
| rating | +0.0218 | 0.0100 | +2.18 | — |

**The three do not agree, and that is the finding.** Between nodes +6.94% per doubling, between gigs within a node -9.08%, within a gig +7.62%. **B and C have OPPOSITE SIGNS.** Among sellers of the SAME task, the better-reviewed ones charge LESS -- and yet any single listing raises its own price as it accumulates reviews. Both are precisely estimated, so this is not noise: it is step 25's Simpson reversal, sharpened from `near zero` to `significantly negative` by holding the task fixed at node rather than domain. The reading is that a high review count identifies two different things at once -- a seller who has been around (which raises price) and a seller running a cheap high-volume operation (which lowers it). Between sellers the second dominates; within one listing only the first can move.

## 3. The rate is not constant

Adding a square term to spec C gives `ln(1+reviews)` **+0.1262** and its square **-0.0028** (t -2.51). The marginal return to a doubling:

| cumulative reviews | per doubling |
|---:|---:|
| 10 | +8.14% |
| 50 | +7.51% |
| 100 | +7.23% |
| 500 | +6.57% |
| 1,000 | +6.29% |
| 5,000 | +5.63% |

A single elasticity is an average over this curve, not a rate that applies at every level.

## 4. Does reputation pay the same for every task?

Spec C re-fit inside each node with at least 100 gigs. This is the question the taxonomy exists to make askable.

58 nodes estimated; **45 significant at 5%**, **58 positive**. Slope range **+1.84%** (translation/localization) to **+27.11%** (translation/interpreting) per doubling.

| node | gigs | per doubling | t |
|---|---:|---:|---:|
| translation/interpreting | 114 | +27.11% | +2.90 |
| coding/site_builder | 230 | +22.00% | +7.60 |
| marketing/funnel_landing | 368 | +14.68% | +3.68 |
| marketing/paid_ads | 781 | +13.86% | +6.65 |
| writing/resume_career | 247 | +13.58% | +6.55 |
| marketing/content_strategy | 158 | +13.47% | +2.06 |
| coding/wordpress | 797 | +12.75% | +5.68 |
| design/presentation | 184 | +12.59% | +3.93 |
| coding/spreadsheet_data | 519 | +11.78% | +5.16 |
| writing/content_writing | 993 | +11.06% | +8.37 |
| audio/voiceover | 1,062 | +10.13% | +6.20 |
| translation/other | 1,432 | +9.82% | +5.25 |
| design/brand_identity | 218 | +9.62% | +3.70 |
| video/intro_outro | 221 | +9.56% | +3.42 |
| video/explainer | 414 | +9.20% | +4.17 |
| writing/book_ebook | 1,026 | +9.05% | +7.78 |
| design/print_collateral | 669 | +8.99% | +7.07 |
| design/three_d | 208 | +8.97% | +4.29 |
| marketing/email_marketing | 196 | +8.95% | +1.88 |
| video/animation | 1,084 | +8.89% | +7.71 |
| writing/other | 382 | +8.70% | +3.75 |
| video/promo_commercial | 631 | +8.61% | +5.18 |
| coding/ecommerce | 823 | +8.32% | +5.48 |
| audio/mixing_mastering | 521 | +8.30% | +4.97 |
| coding/mobile_app | 382 | +8.27% | +3.35 |
| coding/scripting_automation | 784 | +7.98% | +4.50 |
| video/music_video | 379 | +7.72% | +4.09 |
| marketing/analytics_setup | 209 | +7.69% | +2.44 |
| audio/podcast | 474 | +7.68% | +4.09 |
| audio/songwriting | 778 | +7.50% | +4.40 |
| marketing/social_media_mgmt | 1,853 | +7.44% | +6.41 |
| marketing/other | 1,354 | +7.36% | +4.63 |
| video/other | 1,334 | +7.31% | +6.19 |
| audio/music_production | 882 | +7.11% | +3.77 |
| coding/web_dev | 366 | +7.05% | +2.62 |
| writing/copywriting | 153 | +7.05% | +2.15 |
| design/other | 848 | +6.68% | +5.19 |
| writing/editing_proofreading | 635 | +5.96% | +4.12 |
| writing/script_writing | 248 | +5.91% | +2.81 |
| design/ui_ux | 106 | +5.89% | +1.15 |
| audio/other | 1,588 | +5.88% | +4.70 |
| marketing/affiliate | 362 | +5.40% | +1.57 |
| video/video_editing | 159 | +5.28% | +1.82 |
| video/spokesperson_ugc | 209 | +4.92% | +2.04 |
| translation/language_tutoring | 236 | +4.86% | +1.43 |
| video/youtube_content | 231 | +4.69% | +2.32 |
| coding/other | 1,151 | +4.42% | +3.31 |
| design/logo | 822 | +4.27% | +3.57 |
| design/illustration | 622 | +3.98% | +2.90 |
| marketing/youtube_growth | 287 | +3.89% | +1.54 |
| translation/document_translation | 1,578 | +3.54% | +3.29 |
| writing/press_pr | 117 | +3.22% | +1.02 |
| audio/music_promotion | 216 | +3.22% | +1.57 |
| translation/voiceover_leak | 679 | +3.08% | +1.32 |
| translation/subtitling | 397 | +2.97% | +1.48 |
| translation/transcription | 949 | +2.65% | +1.76 |
| marketing/seo | 1,549 | +2.62% | +1.78 |
| translation/localization | 128 | +1.84% | +0.27 |

## 5. What share of price each layer explains

- **domain (7)** alone: 5.7%
- **node (65)** alone: 10.9%
- **gig** alone: 91.4%
- **reputation, on top of node**: a further 2.2% of total variance

So the taxonomy names the task, reputation adds a slice on top of it, and the large remainder is what separates two sellers of the same work with the same review count — quality, presentation, and everything else no column here holds.

