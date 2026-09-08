(() => {
  const TARGETS = ["heykeram/review-your-song-and-provide-feedback","iq_nimrah/do-mixing-and-mastering-to-your-songs-and-podcasts-in-audacity","mrswarmvoice/produce-a-female-voice-over-in-a-charming-voice","sethdmeyers/provide-a-professional-and-engaging-voiceover","saasta6/write-filthy-original-lyrics-for-your-metal-song","studio_moxie/build-a-custom-ai-voice-assistant-ai-caller-for-you-using-vapi","rezaulfv07/create-responsive-clickable-html-email-signature-design","shkhamza3/fix-bugs-in-your-react-native-app","wix_pr0/design-wix-website-design-and-redesign-wix-website","xk1dreaperx/assess-your-cloud-environment-against-security-best-practice","raphicx2125/design-tech-and-saas-logo-with-corporate-brand-identity","eveeelin/create-a-high-end-brand-identity","complexxfx/rig-light-and-render-your-3d-models-for-movies-and-games","graphic_alert/make-5-logo-animation-intros","masumbillah54/design-attractive-social-media-posts","shofeulislam/fix-google-search-console-analytics-index-coverage-errors","muhammaddani70/do-guest-post-on-marketbusinessnews-and-priceofbusiness","rebeccapagec/give-your-marketing-strategy-more-focus-8c49","sampabiswas/create-a-responsive-landing-page-for-your-startup-business","singurc/provide-award-winning-ppc-and-google-ads-services","saschacs/be-your-german-customer-service-and-technical-support-agent","anna1590/teach-you-conversational-russian","amandastudio/record-a-unique-brazilian-portuguese-voiceover","elanjapowers/transcribe-english-audio-to-text-any-accent","nativechina/typewrite-enter-1000-english-or-chinese-words","vfxbook/create-high-quality-book-promo-video","raj2016/make-this-isometric-explainer-video-for-you","yusriil/create-lottie-json-svg-animated-gif-video-for-website-app","dmitrighi/create-truck-logistics-warehouse-promo-video","graphicsqueens/create-cinematic-3d-book-trailer-video","sivanlm/shoot-editorial-fashion-spreads-in-new-york","tarafoss/proofread-and-copy-edit-your-work","seb_jenkins/freelance-journalist-experience-writing-across-all-subjects-news-and-sport","katiehowe/write-engaging-sales-copy","daniel51233/create-book-author-website","brunonavarrov/produce-your-audio-ad-for-radio-podcasts-spotify","syedzeeshan7860/remake-any-beat-for-you","acasillas987/mix-and-master-your-rap-hip-hop-song","reggieduncan1/play-pedal-steel-guitar-on-your-song","varoproductions/help-you-find-pleasure-in-pursuing-your-music-career"];
  const TIER = 1;
  const MIN_DELAY = 4000, MAX_DELAY = 9000;   // one page at a time
  const CHUNK = 20;                    // download a part-file this often
  const DONE_KEY = 'ipi_done_tier' + TIER;    // survives a reload; small (paths only)

  if (window.IPI && window.IPI.running) {
    console.warn('IPI: a run is already in progress. IPI.stop() first.');
    return;
  }

  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const jitter = () => MIN_DELAY + Math.random() * (MAX_DELAY - MIN_DELAY);

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
    const j = html.indexOf(open, i);
    if (j < 0) return null;
    return matchFrom(html, j, open, close);
  }

  function parseMaybe(raw) { try { return raw ? JSON.parse(raw) : null; } catch (e) { return null; } }

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
