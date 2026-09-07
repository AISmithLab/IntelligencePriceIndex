# What is inside step 04's `uncategorized` bucket?

Distinct gig URLs labelled `uncategorized`: **289,613** (`data/cdx-index/gig-pages-classified.tsv`, all years, `gigfilter.is_gig` applied).
First-match assignment, so each gig counts once.

## 1. Candidate new families

| family | distinct gigs | share of bucket |
|---|---:|---:|
| photography | 22,719 | 7.8% |
| gaming | 17,060 | 5.9% |
| education_tutoring | 15,205 | 5.3% |
| social_engagement | 13,217 | 4.6% |
| ecommerce_ops | 7,371 | 2.5% |
| legal | 6,843 | 2.4% |
| lifestyle_control | 6,593 | 2.3% |
| accounting_consulting | 5,110 | 1.8% |
| engineering_cad | 2,275 | 0.8% |
| customer_service_va | 1,502 | 0.5% |
| **subtotal** | **97,895** | **33.8%** |

## 2. Leakage — gigs that belong to a domain already collected

Step 04 assigns a category only on an exact keyword substring, so a listing worded `develop-or-customize-drupal-websites` matches none of coding's keywords (`web-develop`, `app-develop`, `developer`) and falls through. Sizing that:

| collected domain | leaked gigs | vs. gigs the step-04 label already holds |
|---|---:|---|
| design | 31,668 | +13% |
| coding | 24,087 | +16% |
| writing | 11,960 | +8% |
| marketing | 10,478 | +14% |
| audio | 8,465 | +29% |
| video | 1,662 | +3% |
| **subtotal** | **88,320** | |

## 3. Residual long tail

**103,398 gigs (35.7%)** match neither table — finance/trading, coaching, sourcing, wellness, one-off novelty listings. Sample:

- `a002348/find-manufacturers-and-suppliers-in-india-for-you`
- `alejandrobrufal/traducir-del-espanol-al-ingles`
- `apple6835/royality-stock-image-free`
- `bear7890/review-or-test-anything-for-you`
- `cash123/lose-you-weight-in-the-next-week`
- `daisys2/be-your-personal-trainer-no-equipment-needed`
- `doreamon08/make-origami-decorations-and-cards`
- `expertguru43/publish-a-guest-post-on-theodysseyonline-da83`
- `genevievemusic/make-you-a-progressive-house-melody-and-chord`
- `heidifitz1231/be-your-mindset-coach-guiding-you-to-find-your-inner-peace`
- `italianstar/tell-you-who-is-your-soulmate-or-twin-flame`
- `joe_brighth/be-your-systeme-io-expert`
- `khubaibkhan_4/reskin-android-apps-into-professional-clean-ui`
- `lorepugi/help-you-setting-up-your-google-tag-manager-like-a-pro`
- `mathematicss664/help-you-in-mathematics-problems-24-hours-77fa`
- `mohaiman01/your-online-detective-for-harassment-cyberbullying-and-gather-information`
- `nataliexu5067/help-you-use-oriental-divination-to-avoid-harm`
- `owen_1zhang/purchase-or-ship-items-from-china-for-you`
- `qusaymoe/do-anything-we-agree-on-before-placing-an-order`
- `ronaldjoya/be-the-best-appointment-setter-for-your-business`
- `seangluz/add-jewelry-on-model`
- `skipease/best-skip-tracer-for-real-estate-skip-tracing`
- `syntrix/replace-these-faces-with-faces-of-your-choice-for-a-great-xmas-card`
- `translations2u/answer-4-british-english-learning-questions`
- `wassibhai/create-mobile-screenshots-for-google-play-and-play-store`
- `zxcvbnmzxcvbnm/be-your-paid-active-referral`
