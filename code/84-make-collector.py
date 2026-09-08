#!/usr/bin/env python3
"""
84 — Emit a self-contained browser-console collector for one tier of step 83's list.

WHY A CONSOLE SCRIPT. Fiverr gig pages are permitted by the site's own robots.txt
(only /search/, /users/, /orders/, pagination and a handful of funnels are
disallowed) and are advertised in `sitemap_gigs.xml.gz`. They are nonetheless 403
to a scripted request from this host — step 80 measured 15/15 with browser headers,
and the homepage 403s on the FIRST request, so it is a bot-detection layer, not a
rate limit. This project refuses to defeat that layer: no CAPTCHA solving, no proxy
rotation, no fingerprint spoofing.

What remains is the operator's own browser. This step writes a script they paste
into the DevTools console on an open fiverr.com tab. Requests are same-origin, so
they carry the session the operator already established by visiting the site
themselves; nothing here forges or bypasses anything.

PACING IS DELIBERATELY SLOWER THAN A HUMAN READS. One request at a time, randomised
4-9s apart (~9 pages/minute), and the run ABORTS on the first 403 rather than
retrying — if the wall re-engages, that is an answer, not an obstacle. A tier-1 run
of 140 pages takes ~15 minutes.

WHAT IT KEEPS. Not the page: a gig page is ~1.3 MB and 1,400 of them would not fit
in a tab. It slices out the two JSON blobs the pipeline actually reads, verbatim,
so step 85 can parse them with the same logic as steps 09 and 59:

    packageList   listed prices in cents  ->  the IPI's price object
    reviews       per-order records: created_at (ORDER date), order_price_range,
                  encrypted_order_id, value, reviewer_country_code

That is a few KB per gig instead of 1.3 MB, and it is raw — no extraction decision
is taken inside the browser, where it could not be audited.

Output: data/fiverr-live/collector-tier<N>-<date>.js   (paste this whole file)
        results land as data/fiverr-live/live-capture-tier<N>-part<K>.jsonl
        in the operator's Downloads folder, to be moved back here for step 85.

Usage:
    python3 84-make-collector.py --tier 1
    python3 84-make-collector.py --tier 2 --skip 140     # continue past tier 1
"""

import argparse
import csv
import json
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LIVE_DIR = BASE_DIR / "data" / "fiverr-live"

TEMPLATE = r"""
// =====================================================================
// IPI live collector — tier __TIER__, __COUNT__ gigs, generated __STAMP__
//
// HOW TO RUN
//   1. Open https://www.fiverr.com/ in a normal tab and let it load.
//   2. DevTools -> Console. If it warns about pasting, type: allow pasting
//   3. Paste this entire file, press Enter.
//   4. Leave the tab open and in the foreground. ~__MINUTES__ minutes.
//
// It downloads a .jsonl part-file every __CHUNK__ gigs and at the end.
// Move those files into data/fiverr-live/ and run code/85-ingest-live-capture.py
//
// Controls:  IPI.stop()   finish the current page, save, halt
//            IPI.save()   download what is held right now
//            IPI.status() how far along
// =====================================================================
(() => {
  const TARGETS = __TARGETS__;
  const TIER = __TIER__;
  const MIN_DELAY = 4000, MAX_DELAY = 9000;   // one page at a time
  const CHUNK = __CHUNK__;                    // download a part-file this often
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
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", type=int, default=1)
    ap.add_argument("--skip", type=int, default=0,
                    help="drop the first N ranks (to continue past an earlier tier)")
    ap.add_argument("--chunk", type=int, default=25)
    ap.add_argument("--limit", type=int, default=0,
                    help="take only the first N targets. The list is round-robin "
                         "across strata, so a prefix is still balanced -- this is a "
                         "smaller sample, not a biased one.")
    ap.add_argument("--compact", action="store_true",
                    help="strip the banner and long comments, for pasting into a "
                         "chat window rather than transferring a file")
    ap.add_argument("--targets", default=None, help="path to a step-83 targets TSV")
    args = ap.parse_args()

    if args.targets:
        tpath = Path(args.targets)
    else:
        found = sorted(LIVE_DIR.glob("live-targets-*.tsv"))
        if not found:
            raise SystemExit("no targets file — run code/83-live-target-list.py first")
        tpath = found[-1]

    with open(tpath, newline="") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t")
                if int(r["tier"]) <= args.tier]
    rows.sort(key=lambda r: int(r["rank"]))
    rows = rows[args.skip:]
    if args.limit:
        rows = rows[:args.limit]
    paths = [r["gig_id"] for r in rows]

    stamp = date.today().isoformat()
    minutes = round(len(paths) * 6.5 / 60)
    js = (TEMPLATE
          .replace("__TARGETS__", json.dumps(paths, indent=0).replace("\n", ""))
          .replace("__TIER__", str(args.tier))
          .replace("__COUNT__", str(len(paths)))
          .replace("__STAMP__", stamp)
          .replace("__CHUNK__", str(args.chunk))
          .replace("__MINUTES__", str(minutes)))

    if args.compact:
        import re as _re
        # Drop the banner block and any whole-line // comment; keep the code.
        js = js[js.index("(() => {"):]
        js = "\n".join(l for l in js.split("\n")
                       if not l.strip().startswith("//"))
        js = _re.sub(r"\n{3,}", "\n\n", js)

    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    name = f"collector-tier{args.tier}{'-compact' if args.compact else ''}-{stamp}.js"
    out = LIVE_DIR / name
    out.write_text(js)
    print(f"Targets file : {tpath.name}")
    print(f"Gigs         : {len(paths):,} (tier <= {args.tier}, skipping {args.skip})")
    print(f"Estimated run: ~{minutes} min at 4-9s spacing")
    print(f"Wrote        : {out}")


if __name__ == "__main__":
    main()
