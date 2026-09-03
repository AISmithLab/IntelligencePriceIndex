# A two-level task taxonomy, and a reference task value per node

Built from gig titles (39,593 gigs, one title each). Domains are step 04's; subcategories are this step's, matched on the deliverable phrase with ORDERED first-match-wins rules. Nodes under 30 gigs are folded into `<domain>/other`.

Panel: **270,965 gig-quarter observations**, **35,826 gigs**, **65 nodes** across **7 domains**. Prices are real, 2020Q1 dollars (CPI-U, SA quarterly mean).

Reference values below are computed on the **estimation sample** — the rows `78-reputation-price.py` can fit, i.e. those carrying both a rating and a review count. That drops 16,653 of 287,618 gig-quarter rows (5.8%) and is deliberate: it keeps ONE reference task value in the project rather than one here and a different one in the model.

## Coverage

- gigs landing in a named subcategory: **77.5%** (30,685 of 39,593)
- gigs in `<domain>/other`: **8,908**

| domain | gigs | nodes | in `other` | share named |
|---|---:|---:|---:|---:|
| audio | 5,934 | 8 | 1,674 | 71.8% |
| coding | 5,653 | 9 | 1,236 | 78.1% |
| design | 4,188 | 10 | 936 | 77.7% |
| marketing | 8,368 | 11 | 1,550 | 81.5% |
| translation | 6,250 | 8 | 1,666 | 73.3% |
| video | 5,057 | 10 | 1,438 | 71.6% |
| writing | 4,143 | 9 | 408 | 90.2% |

## Reference task value by node

**Reference task value** is the mean of `ln(real price)` over the node's gig-quarters, reported in dollars as `exp(mean ln p)` -- a geometric mean, which is the right centre for a log-normal price and is not dragged by the few $10,000 listings. `sd` is the within-node spread in log points: a large one means the node is still mixing different jobs.

| node | gigs | obs | reference task value | mean ln p | sd ln p | median reviews |
|---|---:|---:|---:|---:|---:|---:|
| marketing/content_strategy | 158 | 885 | $59.38 | +4.0840 | 1.3590 | 25 |
| coding/site_builder | 230 | 2,207 | $58.18 | +4.0636 | 1.2196 | 115 |
| video/explainer | 414 | 3,535 | $44.28 | +3.7906 | 1.5581 | 136 |
| design/brand_identity | 218 | 2,896 | $44.04 | +3.7851 | 1.5721 | 244 |
| coding/mobile_app | 382 | 3,284 | $43.03 | +3.7620 | 1.4971 | 75 |
| design/ui_ux | 106 | 1,300 | $42.08 | +3.7395 | 1.2406 | 177 |
| marketing/paid_ads | 781 | 4,181 | $41.54 | +3.7268 | 1.2429 | 33 |
| coding/ecommerce | 823 | 6,651 | $40.95 | +3.7124 | 1.4416 | 156 |
| writing/resume_career | 247 | 2,940 | $36.91 | +3.6085 | 1.1255 | 181 |
| marketing/funnel_landing | 368 | 1,962 | $35.80 | +3.5779 | 1.1249 | 46 |
| writing/copywriting | 153 | 1,551 | $32.21 | +3.4722 | 1.1955 | 134 |
| coding/wordpress | 797 | 6,023 | $29.77 | +3.3934 | 1.2862 | 219 |
| video/music_video | 379 | 3,262 | $29.54 | +3.3858 | 1.3200 | 142 |
| design/presentation | 184 | 2,734 | $29.10 | +3.3707 | 1.1869 | 378 |
| video/animation | 1,084 | 9,624 | $28.96 | +3.3660 | 1.2601 | 81 |
| coding/web_dev | 366 | 3,162 | $28.58 | +3.3528 | 1.4731 | 96 |
| design/three_d | 208 | 2,702 | $28.23 | +3.3404 | 0.9924 | 200 |
| writing/content_writing | 993 | 10,268 | $27.67 | +3.3204 | 1.2086 | 136 |
| design/other | 848 | 11,243 | $25.89 | +3.2537 | 1.3328 | 229 |
| marketing/social_media_mgmt | 1,853 | 8,970 | $25.73 | +3.2476 | 1.3254 | 46 |
| design/illustration | 622 | 7,308 | $25.68 | +3.2455 | 1.3063 | 229 |
| writing/press_pr | 117 | 1,268 | $25.67 | +3.2454 | 1.1493 | 256 |
| audio/songwriting | 778 | 5,097 | $25.50 | +3.2387 | 0.9797 | 84 |
| marketing/email_marketing | 196 | 879 | $25.38 | +3.2339 | 1.1367 | 32 |
| video/promo_commercial | 631 | 5,402 | $25.36 | +3.2330 | 1.3318 | 86 |
| design/logo | 822 | 10,033 | $25.31 | +3.2311 | 1.3991 | 623 |
| coding/other | 1,151 | 9,090 | $24.78 | +3.2100 | 1.3248 | 66 |
| writing/book_ebook | 1,026 | 11,644 | $24.57 | +3.2014 | 1.2437 | 183 |
| writing/academic | 84 | 766 | $24.09 | +3.1819 | 1.1242 | 100 |
| audio/mixing_mastering | 521 | 3,960 | $23.93 | +3.1751 | 0.9484 | 136 |
| video/other | 1,334 | 11,132 | $23.89 | +3.1736 | 1.3663 | 56 |
| video/spokesperson_ugc | 209 | 1,593 | $23.40 | +3.1527 | 1.0507 | 198 |
| coding/scripting_automation | 784 | 6,293 | $21.98 | +3.0904 | 1.1571 | 83 |
| writing/other | 382 | 4,036 | $21.71 | +3.0780 | 1.1564 | 178 |
| marketing/seo | 1,549 | 7,610 | $21.66 | +3.0753 | 1.4602 | 59 |
| writing/script_writing | 248 | 2,927 | $21.27 | +3.0574 | 1.1280 | 172 |
| translation/localization | 128 | 561 | $20.90 | +3.0397 | 0.7739 | 8 |
| marketing/other | 1,354 | 6,307 | $20.46 | +3.0185 | 1.2193 | 30 |
| audio/music_production | 882 | 5,540 | $20.45 | +3.0178 | 1.0489 | 64 |
| marketing/youtube_growth | 287 | 1,307 | $20.05 | +2.9984 | 1.0751 | 68 |
| design/print_collateral | 669 | 9,610 | $19.71 | +2.9812 | 0.9732 | 416 |
| marketing/analytics_setup | 209 | 1,242 | $19.39 | +2.9648 | 1.1388 | 49 |
| video/intro_outro | 221 | 1,888 | $18.85 | +2.9365 | 1.0472 | 120 |
| translation/other | 1,432 | 5,896 | $18.45 | +2.9148 | 1.1456 | 24 |
| marketing/affiliate | 362 | 1,305 | $17.87 | +2.8834 | 1.0565 | 28 |
| audio/other | 1,588 | 9,976 | $17.44 | +2.8585 | 0.9592 | 59 |
| audio/voiceover | 1,062 | 7,340 | $17.38 | +2.8553 | 1.0840 | 234 |
| video/video_editing | 159 | 1,376 | $16.94 | +2.8295 | 1.0019 | 102 |
| audio/music_promotion | 216 | 1,026 | $16.41 | +2.7976 | 0.9394 | 80 |
| marketing/marketplace | 59 | 274 | $16.16 | +2.7825 | 0.9667 | 56 |
| audio/podcast | 474 | 2,698 | $15.91 | +2.7672 | 1.0071 | 23 |
| writing/editing_proofreading | 635 | 7,103 | $15.87 | +2.7641 | 1.0932 | 330 |
| coding/spreadsheet_data | 519 | 4,018 | $13.97 | +2.6368 | 0.9641 | 93 |
| translation/interpreting | 114 | 365 | $13.38 | +2.5935 | 0.9069 | 10 |
| design/merch_apparel | 63 | 641 | $13.18 | +2.5786 | 0.9950 | 921 |
| design/social_graphics | 71 | 787 | $12.14 | +2.4963 | 1.1257 | 803 |
| translation/voiceover_leak | 679 | 3,496 | $12.10 | +2.4929 | 0.9253 | 138 |
| video/youtube_content | 231 | 1,716 | $11.55 | +2.4463 | 0.8502 | 102 |
| coding/bugfix_support | 64 | 528 | $11.37 | +2.4308 | 0.7700 | 88 |
| audio/audio_editing | 82 | 537 | $11.16 | +2.4120 | 0.6979 | 52 |
| translation/language_tutoring | 236 | 913 | $9.29 | +2.2285 | 0.6839 | 21 |
| video/slideshow | 60 | 586 | $8.08 | +2.0894 | 0.5467 | 113 |
| translation/transcription | 949 | 5,192 | $6.89 | +1.9298 | 0.6006 | 73 |
| translation/document_translation | 1,578 | 8,392 | $6.70 | +1.9025 | 0.6730 | 159 |
| translation/subtitling | 397 | 1,927 | $6.66 | +1.8964 | 0.5873 | 40 |

Reference task value runs **$6.66** (translation/subtitling) to **$59.38** (marketing/content_strategy), a spread of **2.188 log points**.

## How much task variation the taxonomy actually captures

- **domain only (7 units)**: explains 5.7% of the variance in `ln(real price)`
- **node (this taxonomy)**: explains 10.9% of the variance in `ln(real price)`
- **gig (step 76's fixed effect)**: explains 91.4% of the variance in `ln(real price)`

The gap between the node row and the gig row is what a taxonomy cannot reach: differences between two listings of *the same kind of work*. Step 78 asks how much of that gap is reputation.

