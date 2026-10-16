# How reputation influences price, with task value anchored on a taxonomy node

Panel: **265,862 gig-quarter observations**, **34,553 gigs**, **62 nodes**. Real prices, 2020Q1 dollars. SEs clustered on gig.

Note this panel is **not** step 76's: there is no before/after balance requirement, because nothing here is a difference-in-differences. That is why it carries 34,553 gigs against step 76's 15,676.

## 1. Reference task value, raw and reputation-adjusted

`raw` is the node's mean `ln(real price)`, exactly as specified. `adjusted` is the node's fixed effect from a fit that also carries reputation and quarter, so it is the going rate for the WORK with the sellers' standing taken out. Both are centred on their own mean, so only the GAP between the columns is meaningful.

A positive gap means the node looks dearer than the work warrants because its sellers are well-reviewed; a negative gap means the node is underselling its reputation.

Correlation between the two rankings: **0.9731** (Spearman 0.9637). Mean absolute gap **0.0879** log points, max **0.3816**.

The ten nodes whose price is most inflated by reputation, and the ten least:

| node | gigs | median reviews | raw | adjusted | gap |
|---|---:|---:|---:|---:|---:|
| translation/localization | 127 | 9 | -0.0443 | -0.4258 | +0.3816 |
| marketing/paid_ads | 810 | 34 | +0.6763 | +0.4888 | +0.1874 |
| translation/other | 164 | 32 | -0.5505 | -0.7254 | +0.1749 |
| marketing/content_strategy | 159 | 25 | +1.0053 | +0.8401 | +0.1652 |
| audio/podcast | 484 | 23 | -0.3115 | -0.4670 | +0.1555 |
| marketing/other | 1,383 | 30 | -0.0523 | -0.1950 | +0.1427 |
| translation/subtitling | 396 | 41 | -1.1829 | -1.3169 | +0.1340 |
| marketing/affiliate | 363 | 28 | -0.1972 | -0.3081 | +0.1109 |
| marketing/analytics_setup | 209 | 49 | -0.1149 | -0.2180 | +0.1031 |
| video/other | 1,408 | 55 | +0.0841 | -0.0134 | +0.0975 |
| design/merch_apparel | 63 | 921 | -0.5011 | -0.2103 | -0.2907 |
| design/logo | 822 | 623 | +0.1515 | +0.3832 | -0.2318 |
| design/social_graphics | 71 | 803 | -0.5834 | -0.3660 | -0.2174 |
| design/print_collateral | 669 | 416 | -0.0985 | +0.0999 | -0.1984 |
| design/presentation | 184 | 378 | +0.2910 | +0.4749 | -0.1839 |
| writing/press_pr | 117 | 256 | +0.1657 | +0.3418 | -0.1761 |
| writing/editing_proofreading | 635 | 330 | -0.3155 | -0.1873 | -0.1282 |
| design/brand_identity | 218 | 244 | +0.7054 | +0.8135 | -0.1081 |
| translation/document_translation | 1,561 | 160 | -1.1758 | -1.0783 | -0.0976 |
| design/illustration | 622 | 229 | +0.1659 | +0.2582 | -0.0923 |

## 2. Reputation at three levels

The same two reputation variables, changing only what is held fixed.

**A — between nodes** (62 nodes, one row each; no fixed effects). Does dearer work carry more reviews?

| term | coef | se | t | per doubling |
|---|---:|---:|---:|---:|
| ln(1+reviews) | +0.0508 | 0.0820 | +0.62 | +3.58% |
| rating | -6.5183 | 2.6733 | -2.44 | — |

The rating coefficient here is fit on 65 points and should not be read as a price effect: node mean rating is close to constant (Fiverr ratings sit at 4.8-5.0 almost everywhere), so it is picking up whatever else separates cheap nodes from dear ones.

**B — between gigs, within node** (node absorbed; this is the 'what is reputation worth' reading). Within-R² 0.0501.

| term | coef | se | t | per doubling |
|---|---:|---:|---:|---:|
| ln(1+reviews) | -0.1386 | 0.0049 | -28.23 | -9.16% |
| rating | +0.3298 | 0.0264 | +12.48 | — |

**C — within gig, over time** (gig absorbed; step 76's specification, re-run on this larger panel). Within-R² 0.1232.

| term | coef | se | t | per doubling |
|---|---:|---:|---:|---:|
| ln(1+reviews) | +0.1060 | 0.0035 | +30.70 | +7.62% |
| rating | +0.0216 | 0.0101 | +2.13 | — |

**The three do not agree, and that is the finding.** Between nodes +3.58% per doubling, between gigs within a node -9.16%, within a gig +7.62%. **B and C have OPPOSITE SIGNS.** Among sellers of the SAME task, the better-reviewed ones charge LESS -- and yet any single listing raises its own price as it accumulates reviews. Both are precisely estimated, so this is not noise: it is step 25's Simpson reversal, sharpened from `near zero` to `significantly negative` by holding the task fixed at node rather than domain. The reading is that a high review count identifies two different things at once -- a seller who has been around (which raises price) and a seller running a cheap high-volume operation (which lowers it). Between sellers the second dominates; within one listing only the first can move.

## 3. The rate is not constant

Adding a square term to spec C gives `ln(1+reviews)` **+0.1265** and its square **-0.0028** (t -2.50). The marginal return to a doubling:

| cumulative reviews | per doubling |
|---:|---:|
| 10 | +8.15% |
| 50 | +7.52% |
| 100 | +7.23% |
| 500 | +6.57% |
| 1,000 | +6.29% |
| 5,000 | +5.63% |

A single elasticity is an average over this curve, not a rate that applies at every level.

## 4. Does reputation pay the same for every task?

Spec C re-fit inside each node with at least 100 gigs. This is the question the taxonomy exists to make askable.

55 nodes estimated; **43 significant at 5%**, **55 positive**. Slope range **+1.91%** (translation/localization) to **+22.00%** (coding/site_builder) per doubling.

| node | gigs | per doubling | t |
|---|---:|---:|---:|
| coding/site_builder | 230 | +22.00% | +7.60 |
| translation/other | 164 | +18.04% | +3.32 |
| marketing/funnel_landing | 371 | +14.68% | +3.68 |
| marketing/paid_ads | 810 | +13.84% | +6.76 |
| writing/resume_career | 247 | +13.58% | +6.55 |
| marketing/content_strategy | 159 | +13.47% | +2.06 |
| coding/wordpress | 797 | +12.75% | +5.68 |
| design/presentation | 184 | +12.59% | +3.93 |
| coding/spreadsheet_data | 519 | +11.78% | +5.16 |
| writing/content_writing | 993 | +11.06% | +8.37 |
| design/brand_identity | 218 | +9.62% | +3.70 |
| video/intro_outro | 225 | +9.53% | +3.41 |
| video/explainer | 433 | +9.16% | +4.18 |
| marketing/email_marketing | 197 | +9.07% | +1.92 |
| writing/book_ebook | 1,026 | +9.05% | +7.78 |
| design/print_collateral | 669 | +8.99% | +7.07 |
| design/three_d | 208 | +8.97% | +4.29 |
| video/animation | 1,095 | +8.92% | +7.74 |
| writing/other | 382 | +8.70% | +3.75 |
| video/promo_commercial | 638 | +8.62% | +5.18 |
| audio/voiceover | 1,630 | +8.58% | +6.02 |
| audio/mixing_mastering | 523 | +8.40% | +5.05 |
| coding/ecommerce | 823 | +8.32% | +5.48 |
| coding/mobile_app | 382 | +8.27% | +3.35 |
| coding/scripting_automation | 784 | +7.98% | +4.50 |
| audio/songwriting | 835 | +7.84% | +4.69 |
| video/music_video | 380 | +7.80% | +4.14 |
| audio/podcast | 484 | +7.71% | +4.12 |
| marketing/analytics_setup | 209 | +7.69% | +2.44 |
| audio/music_production | 894 | +7.47% | +3.94 |
| marketing/social_media_mgmt | 1,868 | +7.41% | +6.40 |
| marketing/other | 1,383 | +7.37% | +4.68 |
| video/other | 1,408 | +7.35% | +6.26 |
| coding/web_dev | 366 | +7.05% | +2.62 |
| writing/copywriting | 153 | +7.05% | +2.15 |
| design/other | 848 | +6.68% | +5.19 |
| audio/other | 1,628 | +5.98% | +4.80 |
| writing/editing_proofreading | 635 | +5.96% | +4.12 |
| writing/script_writing | 248 | +5.91% | +2.81 |
| design/ui_ux | 106 | +5.89% | +1.15 |
| marketing/affiliate | 363 | +5.39% | +1.57 |
| video/video_editing | 160 | +5.33% | +1.84 |
| video/youtube_content | 237 | +4.62% | +2.30 |
| video/spokesperson_ugc | 261 | +4.46% | +1.95 |
| coding/other | 1,151 | +4.42% | +3.31 |
| design/logo | 822 | +4.27% | +3.57 |
| design/illustration | 622 | +3.98% | +2.90 |
| marketing/youtube_growth | 290 | +3.91% | +1.56 |
| translation/document_translation | 1,561 | +3.49% | +3.22 |
| writing/press_pr | 117 | +3.22% | +1.02 |
| audio/music_promotion | 220 | +3.21% | +1.56 |
| translation/subtitling | 396 | +2.97% | +1.48 |
| translation/transcription | 945 | +2.62% | +1.73 |
| marketing/seo | 1,646 | +2.61% | +1.83 |
| translation/localization | 127 | +1.91% | +0.28 |

## 5. What share of price each layer explains

- **domain (7)** alone: 6.3%
- **node (65)** alone: 10.8%
- **gig** alone: 91.4%
- **reputation, on top of node**: a further 2.2% of total variance

So the taxonomy names the task, reputation adds a slice on top of it, and the large remainder is what separates two sellers of the same work with the same review count — quality, presentation, and everything else no column here holds.

