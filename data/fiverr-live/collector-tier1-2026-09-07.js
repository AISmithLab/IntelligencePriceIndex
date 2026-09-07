
// =====================================================================
// IPI live collector — tier 1, 140 gigs, generated 2026-09-07
//
// HOW TO RUN
//   1. Open https://www.fiverr.com/ in a normal tab and let it load.
//   2. DevTools -> Console. If it warns about pasting, type: allow pasting
//   3. Paste this entire file, press Enter.
//   4. Leave the tab open and in the foreground. ~15 minutes.
//
// It downloads a .jsonl part-file every 25 gigs and at the end.
// Move those files into data/fiverr-live/ and run code/85-ingest-live-capture.py
//
// Controls:  IPI.stop()   finish the current page, save, halt
//            IPI.save()   download what is held right now
//            IPI.status() how far along
// =====================================================================
(() => {
  const TARGETS = ["heykeram/review-your-song-and-provide-feedback","iq_nimrah/do-mixing-and-mastering-to-your-songs-and-podcasts-in-audacity","mrswarmvoice/produce-a-female-voice-over-in-a-charming-voice","sethdmeyers/provide-a-professional-and-engaging-voiceover","saasta6/write-filthy-original-lyrics-for-your-metal-song","studio_moxie/build-a-custom-ai-voice-assistant-ai-caller-for-you-using-vapi","rezaulfv07/create-responsive-clickable-html-email-signature-design","shkhamza3/fix-bugs-in-your-react-native-app","wix_pr0/design-wix-website-design-and-redesign-wix-website","xk1dreaperx/assess-your-cloud-environment-against-security-best-practice","raphicx2125/design-tech-and-saas-logo-with-corporate-brand-identity","eveeelin/create-a-high-end-brand-identity","complexxfx/rig-light-and-render-your-3d-models-for-movies-and-games","graphic_alert/make-5-logo-animation-intros","masumbillah54/design-attractive-social-media-posts","shofeulislam/fix-google-search-console-analytics-index-coverage-errors","muhammaddani70/do-guest-post-on-marketbusinessnews-and-priceofbusiness","rebeccapagec/give-your-marketing-strategy-more-focus-8c49","sampabiswas/create-a-responsive-landing-page-for-your-startup-business","singurc/provide-award-winning-ppc-and-google-ads-services","saschacs/be-your-german-customer-service-and-technical-support-agent","anna1590/teach-you-conversational-russian","amandastudio/record-a-unique-brazilian-portuguese-voiceover","elanjapowers/transcribe-english-audio-to-text-any-accent","nativechina/typewrite-enter-1000-english-or-chinese-words","vfxbook/create-high-quality-book-promo-video","raj2016/make-this-isometric-explainer-video-for-you","yusriil/create-lottie-json-svg-animated-gif-video-for-website-app","dmitrighi/create-truck-logistics-warehouse-promo-video","graphicsqueens/create-cinematic-3d-book-trailer-video","sivanlm/shoot-editorial-fashion-spreads-in-new-york","tarafoss/proofread-and-copy-edit-your-work","seb_jenkins/freelance-journalist-experience-writing-across-all-subjects-news-and-sport","katiehowe/write-engaging-sales-copy","daniel51233/create-book-author-website","brunonavarrov/produce-your-audio-ad-for-radio-podcasts-spotify","syedzeeshan7860/remake-any-beat-for-you","acasillas987/mix-and-master-your-rap-hip-hop-song","reggieduncan1/play-pedal-steel-guitar-on-your-song","varoproductions/help-you-find-pleasure-in-pursuing-your-music-career","jimavidbrio/migrate-your-store-to-shopify-with-a-professional-design","mohinkhan007/do-fabulous-and-eye-catching-ms-word-excel-invoice-for-you","aiobjective/code-for-computer-vision-with-deep-learning-in-python","arslannone/create-shopify-store-dropshipping-store-or-shopify-website","webdivine/squarespace-website-designer-and-developer","w3bdesignuk/design-and-build-a-custom-woocommerce-website","alimsarder786/create-amazing-animated-logo-animation-youtube-intro-video","sarahgraphics/a-brand-style-guide-and-logo-design","graphic_company/create-a-superior-powerpoint-presentation","perfectdesigns7/design-creative-social-media-design-and-professional-banner-ads","setjo1980/do-an-advanced-monthly-seo-and-will-fix-all-site-errors","tomneale521/do-advanced-seo-competitor-keyword-research-for-google-using-semrush-or-ahrefs","wajidlatif/setup-sales-and-membership-funnels-in-clickfunnels","amz_services63/catchy-amazon-product-listing-description-with-seo-amazon-listing-optimization","social_atik/perfectly-all-social-media-accounts-create-set-up-and-optimize-professionally","stephaniejmnz/spanish-voiceover-for-your-inclusive-project","fabiorevo/record-a-professional-italian-voice-over","juanvoiceart/deep-male-voice-over-in-spanish","nsabrina/translate-english-to-italian","christiangutirr/write-narration-scripts-for-your-podcast-in-spanish","fruktorum/develop-high-quality-video-game-for-any-platform","trippiesteff/do-an-awesome-looped-animation-in-my-unique-style","rapid_pro/create-premium-2d-animated-explainer-video-in-24h","sandrotsk/create-lofi-hip-hop-animations","vfxbook/make-custom-children-book-trailer-and-kids-promo-videos-8645","belalmiya/retouch-and-enhancement-product-photo-editing-and-clipping-path","maryjmurphy22/write-your-cover-letter-resume-or-cv","bkille/write-a-tv-commercial-or-video-script","antur2020/promote-and-kindle-ebook-to-usa-users-at-website","shihab_ga4/fix-or-setup-facebook-pixel-conversion-api-with-server-side-tracking-via-gtm","thir13eenbeatz/create-love-song-for-marriage-anniversary-birthday","israelprince/create-afrobeats-in-48-hours","aclekahney/master-your-rock-metal-djent-punk-music","radiostreamlive/play-your-song-on-radio-new-york-live","gma7913/provide-straightforward-advice-on-how-to-improve-your-music-675c","mikewhaites/provide-1-hour-of-wix-website-design-assistance","techconsolution/design-an-html5-responsive-website-for-you","mehran120/do-material-takeoff-estimation-bluebeam-plan-swift-quantity-surveyor-boq","iammrsq/create-an-excel-formula","mhmdwldnprhst/do-web-scraping-data-mining-and-extraction-of-any-website","burntredhen/custom-illustrated-wedding-invitation","thedevsigner/design-interactive-pdf-ex-fillable-form-user-manual-guide","arif_saputra/make-your-manga-page","milkyway1315/design-responsive-mailchimp-email-template-034a6103-5c2c-4cde-86bc-1d8753a8a3cc","iamfahim_k/ecwid-and-big-cartel-online-store-design-ecwid-and-big-cartel-website","sayyamkashmiri/do-text-message-and-bulk-sms-marketing-one-time-blast-sms","rockgardenlosan/boost-your-google-rankings-with-30-pr9-high-pr-seo-social-backlinks","arosh_it/create-run-and-manage-tiktok-ads-campaign-tik-tok-ads-tiktok-advertising","yas17sheikh/setup-google-ads-conversion-tracking","jimmy1256/create-an-ecommerce-amazon-affiliate-store","jackbezerra77/localize-your-video-game-from-english-to-portuguese","yevhenhumeniuk/do-sweden-seo-with-high-quality-swedish-forum-backlinks","compumusic/transcribe-a-monophonic-instrument-of-any-song","mosesistheone/transcribe-20-minutes-of-audio-for-you","umargohar/provide-guest-post-on-netherland-and-russian-with-do-follow-link","arminbeciragic/create-an-appealing-intro-animation","makarov_video/be-your-videographer-in-new-york-city","shoaibkalyar912/create-custom-2d-explainer-video","mridul4567/video-editting-experiece-for-over-4-years","wizard_of_oz/make-360-video-in-virtual-reality-as-a-company-tour","carleywithasea/teach-creative-writing-techniques","homeestates/write-a-professional-blog-or-article","chamika_cd/design-your-professional-cv-or-resume","asad_rehman_se/create-wordpress-website-or-blog-or-fix-any-issues","daniel98226/write-your-book-from-scratch","aquincygoodman/mix-your-metal-or-pop-song-to-a-professional-standard","raymondmusic/write-or-produce-your-rock-or-metal-song","cascreativearts/write-horror-creepy-intense-background-music","tgmusic/sing-and-compose-vocals-or-song-for-you","djkodered/review-your-music-and-give-you-feedback","rickhardypro/do-your-data-science-finance-quant-machine-learning-project","aiobjective/machine-learning-tasks-with-python","yaeliroz/design-your-shopify-store","jewelahmmed/fix-smtp-email-dns-mx-mysql-cpanel-whm-webmin-virtualmin-plesk-issues","jobair_security/wordpress-website-website-design-wordpress-website-redesign-elementor-pro","paulvirlan/draw-professional-childrens-book-illustration","vfxmix/do-professional-3d-animated-logo-intro-video-4k","apollo_studio/do-professional-minimalist-business-card-c17a","salehgardezi/do-any-adobe-illustrator-work","simonameleca/figma-design-figma-website-design-ui-ux","qamarzaman60/do-seo-backlinks-on-high-dr-50-to-70-sites","backlinknation/create-5500-mega-seo-contextual-backlinks-tiered","julietsalve/make-custom-emoji-for-twitch-and-youtube","virtualsuperman/help-you-rank-with-high-authority-contextual-seo-backlinks-tf-cf-da-pa-google-pr","labtech_pro2/perfectly-create-and-set-up-all-social-media-accounts-and-optimize-business-page","davidahn00/be-the-english-to-korean-interpreter-you-are-looking-for","elenaperrin/be-all-ears-for-your-transcription","veronicasummer/record-a-high-quality-german-voice-over-hochdeutsch","juliasolomakha/translateenglish-to-russian-manually","pisethz/translate-and-localize-your-website-app-into-khmer","serson/create-a-lyric-or-music-video-for-your-christmas-song","alexandr02/create-a-romantic-music-video-for-your-song","librada26/create-a-tiktok-dance-video-on-your-song","hamzazaman469/produce-cinematic-game-trailer-for-your-twitch-or-youtube-channel","intro_tamim/create-a-3d-cinematic-intro-for-you","athar_aly/write-articles-and-blog-posts-on-crypto-blockchain-bitcoin-and-metaverse","emmaki/create-engaging-blog-posts-that-build-your-brand-visibility","creative_worksx/design-ebooks-workbooks-and-pdf-lead-magnets","missheather/write-you-a-500-word-article-on-the-topic-of-your-choice","janetteartea/write-a-newsworthy-press-release"];
  const TIER = 1;
  const MIN_DELAY = 4000, MAX_DELAY = 9000;   // one page at a time
  const CHUNK = 25;                    // download a part-file this often
  const DONE_KEY = 'ipi_done_tier' + TIER;    // survives a reload; small (paths only)

  if (window.IPI && window.IPI.running) {
    console.warn('IPI: a run is already in progress. IPI.stop() first.');
    return;
  }

  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const jitter = () => MIN_DELAY + Math.random() * (MAX_DELAY - MIN_DELAY);

  // String-aware brace/bracket matcher: quoted braces inside a review comment
  // would break a naive depth count, and comments routinely contain them.
  function matchFrom(s, start, open, close) {
    let depth = 0, inStr = false, esc = false;
    for (let i = start; i < s.length; i++) {
      const c = s[i];
      if (inStr) {
        if (esc) esc = false;
        else if (c === '\\') esc = true;
        else if (c === '"') inStr = false;
      } else if (c === '"') inStr = true;
      else if (c === open) depth++;
      else if (c === close) { depth--; if (depth === 0) return s.slice(start, i + 1); }
    }
    return null;
  }

  function slice(html, key, open, close) {
    const i = html.indexOf(key);
    if (i < 0) return null;
    // Search from i, NOT from the end of the key: the key '"reviews":{"has_next"'
    // contains the opening brace itself, so starting past it matched the first
    // INNER object instead (star_summary:{}), which is how the first version of
    // this step returned a 2-byte 'reviews' blob for a gig with 368 reviews.
    const j = html.indexOf(open, i);
    if (j < 0) return null;
    return matchFrom(html, j, open, close);
  }

  function parseMaybe(raw) { try { return raw ? JSON.parse(raw) : null; } catch (e) { return null; } }

  // Same sources code/09-extract-prices.py reads, so a live row and an archive
  // row carry the same title and rating and are directly comparable. The
  // packageList's own `title` is the PACKAGE name ("Basic"), not the gig's.
  function first(html, res) {
    for (const re of res) { const m = html.match(re); if (m) return m[1].trim(); }
    return null;
  }
  const ogTitle = html => first(html, [
    /property="og:title"\s+content="([^"]+)"/,
    /content="([^"]+)"\s+property="og:title"/,
    /"gigTitle":"((?:[^"\\]|\\.)*)"/,
  ]);
  const ratingOf = html => first(html, [/"ratingValue"\s*:\s*"?([\d.]+)"?/]);

  function download(rows, part) {
    const name = `live-capture-tier${TIER}-part${String(part).padStart(2, '0')}.jsonl`;
    const blob = new Blob([rows.map(r => JSON.stringify(r)).join('\n') + '\n'],
                          { type: 'application/x-ndjson' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 30000);
    console.log(`IPI: wrote ${name} (${rows.length} gigs)`);
  }

  let done;
  try { done = new Set(JSON.parse(localStorage.getItem(DONE_KEY) || '[]')); }
  catch (e) { done = new Set(); }

  const IPI = window.IPI = {
    running: true, stopped: false, part: 0, buffer: [], ok: 0, fail: 0,
    stop() { this.stopped = true; console.log('IPI: stopping after this page.'); },
    save() { if (this.buffer.length) { download(this.buffer, ++this.part); this.buffer = []; } },
    status() {
      console.log(`IPI: ${this.ok} captured, ${this.fail} failed, `
                + `${done.size}/${TARGETS.length} attempted, ${this.buffer.length} buffered`);
    },
  };

  (async () => {
    const started = Date.now();
    let consecutive403 = 0;

    for (let n = 0; n < TARGETS.length; n++) {
      if (IPI.stopped) break;
      const path = TARGETS[n];
      if (done.has(path)) continue;

      let rec = { path, fetched_at: new Date().toISOString(), tier: TIER };
      try {
        // Relative URL: same-origin, so the session the operator established by
        // loading this page applies. No headers are forged.
        const res = await fetch('/' + path, { credentials: 'same-origin' });
        rec.status = res.status;
        if (res.status === 403) {
          consecutive403++;
          console.warn(`IPI: 403 on ${path} (${consecutive403}). `
                     + 'The wall is up; not retrying.');
          if (consecutive403 >= 3) {
            console.error('IPI: three consecutive 403s. Halting — this is a result, '
                        + 'not an obstacle. Saving what we have.');
            IPI.buffer.push(rec); done.add(path);
            break;
          }
        } else if (res.status === 200) {
          consecutive403 = 0;
          const html = await res.text();
          rec.html_len = html.length;
          rec.og_title = ogTitle(html);
          rec.rating = ratingOf(html);
          rec.package_list = slice(html, '"packageList"', '[', ']');
          rec.reviews = slice(html, '"reviews":{"has_next"', '{', '}');
          const rv = parseMaybe(rec.reviews);
          rec.review_total = rv ? rv.total_count : null;
          rec.reviews_shown = rv && rv.reviews ? rv.reviews.length : 0;
          if (rec.package_list) IPI.ok++; else IPI.fail++;
        } else {
          consecutive403 = 0;
          IPI.fail++;
        }
      } catch (e) {
        rec.error = String(e);
        IPI.fail++;
      }

      IPI.buffer.push(rec);
      done.add(path);
      try { localStorage.setItem(DONE_KEY, JSON.stringify([...done])); } catch (e) {}

      if (IPI.buffer.length >= CHUNK) IPI.save();

      const pct = ((n + 1) / TARGETS.length * 100).toFixed(0);
      const eta = ((TARGETS.length - n - 1) * (MIN_DELAY + MAX_DELAY) / 2 / 60000).toFixed(0);
      console.log(`IPI [${n + 1}/${TARGETS.length}, ${pct}%] ${rec.status || 'ERR'} `
                + `${rec.reviews_shown || 0} reviews  ${path}  (~${eta} min left)`);

      if (n < TARGETS.length - 1 && !IPI.stopped) await sleep(jitter());
    }

    IPI.save();
    IPI.running = false;
    const mins = ((Date.now() - started) / 60000).toFixed(1);
    console.log(`IPI: finished. ${IPI.ok} captured, ${IPI.fail} failed, ${mins} min.`);
    console.log('IPI: move the downloaded .jsonl files into data/fiverr-live/ '
              + 'and run  python3 code/85-ingest-live-capture.py');
    console.log(`IPI: to re-run this tier from scratch: localStorage.removeItem('${DONE_KEY}')`);
  })();
})();
