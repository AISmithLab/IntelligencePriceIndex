# Plan: recover the 2026 window from live pages

**Status:** active — tooling built and validated, waiting on one browser session
**Created:** 2026-09-07
**Goal:** get 2026Q2-Q3 price observations after establishing that neither archive has any.

## Why this exists

`plans/completed/fiverr-2025-2026-backfill.md` closed the archive route for 2025 and left
one item open: "re-query CDX for 2026Q2-Q3, which the March pull never covered". That was
done on 2026-09-07 and the answer is that there is nothing there. See
`runs/cdx-refresh-2025/2026-edge.md`:

- **Wayback kept crawling and the wall took it** (corrected after the operator reported
  a 429; the first reading came off half of prefix `z`). On 79,853 records from 12
  prefixes the 403 share runs 1.0% (2025Q4) -> 18.1% (2026Q1) -> **89.3%** (2026Q2) ->
  59.1% (2026Q3), and volume falls ~8x. 2026Q3 holds **50 distinct gig pages** at status
  200 in a 14.5% partial pull — order 350-500 archive-wide — but 2026Q2 holds **one**, so
  adjacent-quarter matched pairs are ~0 on either side. Worth collecting for a count;
  not a route to a 2026 index.
- **Common Crawl was never tried and is also empty.** `fiverr.com/*` returns **one index
  block** in Aug 2026, and the same in Aug 2025 and Aug 2024; its only status-200 records
  are `robots.txt`. CC never crawled Fiverr gigs at all.
- Wayback is **rate-limiting us**, not down: the operator saw a **429**, this host sees
  timeouts then `Connection refused` (207.241.237.3), after yesterday's ~11 GB pull. The
  refresh is paused on its checkpoints and resumes when the throttle clears.

So the only surface that still carries 2026 prices is a live gig page.

## Why a live page is worth anything

Not for its listed price: a 2026Q3 listing pairs with the panel's last listing at a 4-6
quarter gap, which no adjacent-quarter chain can use. The value is the embedded `reviews`
blob step 59 found, whose records are dated by ORDER (`created_at`) and carry what the
buyer paid (`order_price_range_usd`).

Steps 63 and 63b already established the method on stored HTML, before any of this:

- **63A — no price selection.** Late-fetched pages reproduce an old quarter's price
  distribution: median realised value, late minus early, **+0 USD**, gig-clustered
  bootstrap 95% CI **[+0, +0]**.
- **63b — reach.** Displayed orders sit at **median lag 2 months**; 74.7% within 3
  months, 90.2% within 12. A page opened in 2026-09 is therefore mostly a window onto
  **2026Q2-Q3** — precisely the missing quarters.
- **63B — survivorship, the cost.** Only still-listed gigs are reachable: 26-32% of the
  panel, skewed (43.8% of the top listed-price quartile against 22.4% of the bottom;
  55.0% of the top review-count quartile against 20.8% of the bottom).

## Scope

Covers: choosing which gigs to open and in what order, capturing them in the operator's
own browser, and turning the result into panel rows with its selection caveats attached.

Does **not** cover: defeating PerimeterX. No CAPTCHA solving, no proxy rotation, no
fingerprint spoofing — that was refused on 2026-09-04 and stays refused. Nor does it
cover deciding whether 2026 enters the published index; that is a §4 question and needs
the tier-1 numbers first.

## What is on disk

| file | what |
|---|---|
| `code/83-live-target-list.py` | the stratified target list |
| `code/84-make-collector.py` | emits the paste-in browser collector |
| `code/85-ingest-live-capture.py` | JSONL -> `live-prices-*.csv` + `live-orders-*.csv` + report |
| `data/fiverr-live/live-targets-2026-09-04.tsv` | 1,400 targets, tiered 140 / 560 / 1,400 |
| `data/fiverr-live/collector-tier1-2026-09-07.js` | tier-1 collector, 140 gigs, ~15 min |
| `runs/live-collection/targets-2026-09-04.md` | composition of the list |
| `runs/live-collection/ingest-validation-2026-09-07.md` | dry run proving the chain |

**Sampling.** 16,555 of the panel's 63,190 gigs (26.2%) are still listed. Targets are a
stratified sample over category x panel review-count quartile (cuts 16 / 70 / 249),
round-robin under seed 83, so **any prefix of the list is balanced** — stopping at page 40
still yields a probability sample rather than the head of a ranking. Tiers are cumulative
cuts on that one order, so tier 2 extends tier 1 without re-drawing.

**Legal/politeness position.** Fiverr's robots.txt permits gig pages for `User-Agent: *`
(it disallows `/search/`, `/users/`, `/orders/`, pagination and some funnels) and
advertises them in `sitemap_gigs.xml.gz`. The collector runs same-origin in a session the
operator established by visiting the site themselves; it forges nothing, paces one request
at a time 4-9s apart (~9/min, slower than reading), and **halts on three consecutive
403s** rather than retrying.

## Operator steps (tier 1, ~15 minutes)

1. Open <https://www.fiverr.com/> in a normal browser tab; let it load.
2. DevTools -> Console. If it refuses a paste, type `allow pasting` first.
3. Paste the whole of `data/fiverr-live/collector-tier1-2026-09-07.js`, Enter.
4. Leave the tab in the foreground. It logs each gig and downloads a
   `live-capture-tier1-partNN.jsonl` every 25 gigs, plus one at the end.
   `IPI.stop()` halts early and saves; `IPI.status()` reports progress.
5. Move the downloaded `.jsonl` files into `data/fiverr-live/`.
6. `python3 code/85-ingest-live-capture.py`
7. Read `runs/live-collection/live-capture-<date>.md`.

## Steps

- [x] Establish that Wayback has no 2026Q2-Q3 (`runs/cdx-refresh-2025/2026-edge.md`)
- [x] Test Common Crawl as an alternative archive — closed, recorded so it is not re-tried
- [x] `83-live-target-list.py` — stratified, tiered, balanced at every prefix
- [x] `84-make-collector.py` — paced same-origin collector, halts on the wall
- [x] `85-ingest-live-capture.py` — panel rows plus a report that always carries the caveats
- [x] Validate the whole chain on archived HTML before spending a session (found and
      fixed the inner-object `reviews` slice and the package-vs-gig title)
- [ ] **Run tier 1 (140 gigs) in a browser** — the pilot
- [ ] Decide from tier 1: does the wall hold at this pace, and how many 2026Q2-Q3 orders
      does a page actually yield?
- [ ] If tier 1 clears, run tier 2 (560) and re-assess
- [ ] Decide whether 2026 enters the index, only the error bars, or only the text

## Decision Log

- 2026-09-07: **Live browser collection chosen over waiting on Wayback.** The user
  selected it after the archive evidence; the CDX refresh is worth finishing for 2025
  only, and is separately blocked by IA refusing connections.
- 2026-09-07: **Capture the two JSON blobs, not the page.** A gig page is ~1.3 MB and
  1,400 would not fit in a tab; the slices are ~12 KB and are raw, so no extraction
  decision is taken inside the browser where it could not be audited.
- 2026-09-07: **Stratified, not greedy.** Order yield rises with review count, so a
  greedy list would be all head gigs and would compound the survivorship skew that 63B
  measured. Balance at every prefix matters more than yield per page because the session
  can be stopped at any moment.
- 2026-09-07: **Halt on the wall, do not route around it.** Three consecutive 403s ends
  the run. If the wall re-engages that is a finding for the paper, not an obstacle.

## Progress

- 2026-09-07: Archive route closed on both archives and written up. Steps 83/84/85 built
  and validated end-to-end against 60 stored pages. Tier-1 collector generated. Waiting
  on one browser session.
