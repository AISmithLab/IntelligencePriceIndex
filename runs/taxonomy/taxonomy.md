# A two-level task taxonomy, and a reference task value per node

Built from gig titles (38,085 gigs, one title each). Domains are step 04's; subcategories are this step's, matched on the deliverable phrase with ORDERED first-match-wins rules. Nodes under 30 gigs are folded into `<domain>/other`.

Panel: **265,862 gig-quarter observations**, **34,553 gigs**, **62 nodes** across **7 domains**. Prices are real, 2020Q1 dollars (CPI-U, SA quarterly mean).

Reference values below are computed on the **estimation sample** — the rows `78-reputation-price.py` can fit, i.e. those carrying both a rating and a review count. That drops 15,982 of 281,844 gig-quarter rows (5.7%) and is deliberate: it keeps ONE reference task value in the project rather than one here and a different one in the model.

## Coverage

- gigs landing in a named subcategory: **80.0%** (30,485 of 38,085)
- gigs in `<domain>/other`: **7,600**

| domain | gigs | nodes | in `other` | share named |
|---|---:|---:|---:|---:|
| audio | 6,671 | 8 | 1,720 | 74.2% |
| coding | 5,653 | 9 | 1,236 | 78.1% |
| design | 4,188 | 10 | 936 | 77.7% |
| marketing | 8,567 | 11 | 1,582 | 81.5% |
| translation | 3,608 | 5 | 198 | 94.5% |
| video | 5,255 | 10 | 1,520 | 71.1% |
| writing | 4,143 | 9 | 408 | 90.2% |

## Reference task value by node

**Reference task value** is the mean of `ln(real price)` over the node's gig-quarters, reported in dollars as `exp(mean ln p)` -- a geometric mean, which is the right centre for a log-normal price and is not dragged by the few $10,000 listings. `sd` is the within-node spread in log points: a large one means the node is still mixing different jobs.

| node | gigs | obs | reference task value | mean ln p | sd ln p | median reviews |
|---|---:|---:|---:|---:|---:|---:|
| marketing/content_strategy | 159 | 887 | $59.44 | +4.0850 | 1.3576 | 25 |
| coding/site_builder | 230 | 2,207 | $58.18 | +4.0636 | 1.2196 | 115 |
| video/explainer | 433 | 3,622 | $44.34 | +3.7920 | 1.5517 | 133 |
| design/brand_identity | 218 | 2,896 | $44.04 | +3.7851 | 1.5721 | 244 |
| coding/mobile_app | 382 | 3,284 | $43.03 | +3.7620 | 1.4971 | 75 |
| marketing/paid_ads | 810 | 4,365 | $42.77 | +3.7560 | 1.2345 | 34 |
| design/ui_ux | 106 | 1,300 | $42.08 | +3.7395 | 1.2406 | 177 |
| coding/ecommerce | 823 | 6,651 | $40.95 | +3.7124 | 1.4416 | 156 |
| writing/resume_career | 247 | 2,940 | $36.91 | +3.6085 | 1.1255 | 181 |
| marketing/funnel_landing | 371 | 1,968 | $35.73 | +3.5761 | 1.1238 | 46 |
| writing/copywriting | 153 | 1,551 | $32.21 | +3.4722 | 1.1955 | 134 |
| coding/wordpress | 797 | 6,023 | $29.77 | +3.3934 | 1.2862 | 219 |
| video/music_video | 380 | 3,265 | $29.55 | +3.3860 | 1.3195 | 142 |
| design/presentation | 184 | 2,734 | $29.10 | +3.3707 | 1.1869 | 378 |
| video/animation | 1,095 | 9,669 | $28.96 | +3.3660 | 1.2608 | 81 |
| coding/web_dev | 366 | 3,162 | $28.58 | +3.3528 | 1.4731 | 96 |
| design/three_d | 208 | 2,702 | $28.23 | +3.3404 | 0.9924 | 200 |
| writing/content_writing | 993 | 10,268 | $27.67 | +3.3204 | 1.2086 | 136 |
| design/other | 848 | 11,243 | $25.89 | +3.2537 | 1.3328 | 229 |
| marketing/email_marketing | 197 | 891 | $25.75 | +3.2486 | 1.1364 | 33 |
| design/illustration | 622 | 7,308 | $25.68 | +3.2455 | 1.3063 | 229 |
| writing/press_pr | 117 | 1,268 | $25.67 | +3.2454 | 1.1493 | 256 |
| marketing/social_media_mgmt | 1,868 | 9,024 | $25.67 | +3.2454 | 1.3251 | 46 |
| video/promo_commercial | 638 | 5,425 | $25.48 | +3.2379 | 1.3346 | 86 |
| audio/songwriting | 835 | 5,379 | $25.35 | +3.2326 | 0.9747 | 80 |
| design/logo | 822 | 10,033 | $25.31 | +3.2311 | 1.3991 | 623 |
| coding/other | 1,151 | 9,090 | $24.78 | +3.2100 | 1.3248 | 66 |
| writing/book_ebook | 1,026 | 11,644 | $24.57 | +3.2014 | 1.2437 | 183 |
| writing/academic | 84 | 766 | $24.09 | +3.1819 | 1.1242 | 100 |
| audio/mixing_mastering | 523 | 3,993 | $23.99 | +3.1778 | 0.9481 | 136 |
| video/other | 1,408 | 11,422 | $23.66 | +3.1638 | 1.3599 | 55 |
| video/spokesperson_ugc | 261 | 1,824 | $22.96 | +3.1340 | 1.0490 | 166 |
| coding/scripting_automation | 784 | 6,293 | $21.98 | +3.0904 | 1.1571 | 83 |
| writing/other | 382 | 4,036 | $21.71 | +3.0780 | 1.1564 | 178 |
| marketing/seo | 1,646 | 7,992 | $21.50 | +3.0679 | 1.4444 | 59 |
| writing/script_writing | 248 | 2,927 | $21.27 | +3.0574 | 1.1280 | 172 |
| translation/localization | 127 | 557 | $20.81 | +3.0354 | 0.7750 | 9 |
| marketing/other | 1,383 | 6,416 | $20.64 | +3.0273 | 1.2271 | 30 |
| audio/music_production | 894 | 5,601 | $20.47 | +3.0192 | 1.0494 | 63 |
| marketing/youtube_growth | 290 | 1,320 | $20.24 | +3.0074 | 1.0786 | 68 |
| design/print_collateral | 669 | 9,610 | $19.71 | +2.9812 | 0.9732 | 416 |
| marketing/analytics_setup | 209 | 1,242 | $19.39 | +2.9648 | 1.1388 | 49 |
| video/intro_outro | 225 | 1,904 | $18.95 | +2.9418 | 1.0463 | 119 |
| marketing/affiliate | 363 | 1,307 | $17.86 | +2.8825 | 1.0560 | 28 |
| audio/other | 1,628 | 10,120 | $17.42 | +2.8576 | 0.9567 | 59 |
| video/video_editing | 160 | 1,384 | $16.94 | +2.8299 | 0.9997 | 100 |
| audio/music_promotion | 220 | 1,033 | $16.38 | +2.7963 | 0.9368 | 79 |
| marketing/marketplace | 59 | 274 | $16.16 | +2.7825 | 0.9667 | 56 |
| audio/podcast | 484 | 2,752 | $15.93 | +2.7682 | 1.0043 | 23 |
| writing/editing_proofreading | 635 | 7,103 | $15.87 | +2.7641 | 1.0932 | 330 |
| audio/voiceover | 1,630 | 10,307 | $15.65 | +2.7506 | 1.0624 | 195 |
| coding/spreadsheet_data | 519 | 4,018 | $13.97 | +2.6368 | 0.9641 | 93 |
| design/merch_apparel | 63 | 641 | $13.18 | +2.5786 | 0.9950 | 921 |
| translation/other | 164 | 649 | $12.54 | +2.5291 | 0.9918 | 32 |
| design/social_graphics | 71 | 787 | $12.14 | +2.4963 | 1.1257 | 803 |
| video/youtube_content | 237 | 1,733 | $11.51 | +2.4431 | 0.8478 | 100 |
| coding/bugfix_support | 64 | 528 | $11.37 | +2.4308 | 0.7700 | 88 |
| audio/audio_editing | 82 | 537 | $11.16 | +2.4120 | 0.6979 | 52 |
| video/slideshow | 60 | 586 | $8.08 | +2.0894 | 0.5467 | 113 |
| translation/transcription | 945 | 5,171 | $6.89 | +1.9296 | 0.6015 | 73 |
| translation/document_translation | 1,561 | 8,305 | $6.71 | +1.9039 | 0.6750 | 160 |
| translation/subtitling | 396 | 1,925 | $6.66 | +1.8968 | 0.5875 | 41 |

Reference task value runs **$6.66** (translation/subtitling) to **$59.44** (marketing/content_strategy), a spread of **2.188 log points**.

## How much task variation the taxonomy actually captures

- **domain only (7 units)**: explains 6.3% of the variance in `ln(real price)`
- **node (this taxonomy)**: explains 10.8% of the variance in `ln(real price)`
- **gig (step 76's fixed effect)**: explains 91.4% of the variance in `ln(real price)`

The gap between the node row and the gig row is what a taxonomy cannot reach: differences between two listings of *the same kind of work*. Step 78 asks how much of that gap is reputation.

