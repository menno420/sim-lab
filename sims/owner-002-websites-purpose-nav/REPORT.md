# REPORT — owner-002: the four websites — purpose-fit, navigation health, and cross-site consistency

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md` and owner-001's REPORT.
> Source idea: OWNER-DIRECT request 2026-07-11 (mennovanhattum@gmail.com) — audit the fleet's websites: do they serve their stated purpose, is the navigation healthy (dead links / orphans / dead-ends / broken assets), and are they consistent with each other.
> Run: `python3 sims/owner-002-websites-purpose-nav/analyze_nav.py`
> Inputs: four committed crawl snapshots `runs/{control-plane,botsite,dashboard,review}.json`.
> Pinned source — `menno420/websites` @ `31cfd9f` (each snapshot carries the per-site `head_sha`).

## METHOD LABEL: (1) NUMERIC/MEASURED CRAWL SIMULATION (rung 1–2) for the 3 live sites + (2) MEASURED PROTOTYPE (local build) for review

This is the cheapest ADEQUATE evidence for the purpose-and-navigation question:
every structural claim (page count, depth, dead links, broken assets, orphan
pages, dead-end pages, re-crawl agreement, task-battery pass rate, cross-site
consistency) is **measured** by a deterministic analyzer that RE-DERIVES the
numbers from the committed crawl snapshots — the snapshots are the source of
truth, not this narrative. Three sites were crawled **LIVE** on their production
Railway URLs (strong: real deployed behavior). The fourth, `review`, is **not
deployed**; it was built and served **LOCALLY** from `menno420/websites` and
crawled at `127.0.0.1` — a MEASURED PROTOTYPE (rung 2), so its live behavior is
unverified. The "does it serve its purpose / is it polished enough" judgment
sits on top of the measured conformance core, labeled where it is judgment.

## 1. Purpose & scope — the four sites, with evidence

The audit target is `menno420/websites` @ `31cfd9f`. That repo's own
`docs/current-state.md` + `review/app.py:3-15` enumerate **four services**, each
its own subtree with a stated purpose:

| site | live URL (crawl_mode) | purpose_quote (source `purpose_path`) | purpose-fit |
|---|---|---|---|
| **control-plane** | https://control-plane-production-abb0.up.railway.app · **LIVE** | "readiness board + journal browser… check every repo's working quality and progress" (`app/main.py:1`) | **YES** |
| **botsite** | https://botsite-production-cfd7.up.railway.app · **LIVE** | "Public bot site (server-rendered marketing + reference)" (`botsite/Dockerfile:1`) | **YES** |
| **dashboard** | https://dashboard-production-a91b.up.railway.app · **LIVE** | "Developer dashboard service (private… read-only oversight site)" (`dashboard/Dockerfile:1`) | **YES** |
| **review** | *(not deployed)* built + served locally · **LOCAL** | "Program review site — how an owner + Claude-agent fleet ships, told honestly. Built for Anthropic reviewers… Every claim links to committed evidence; nothing is marketing prose." (`review/app.py:1-15`) | **YES (on the local build)** |

**Why these four and not others.** `review/app.py` and `docs/current-state.md`
name exactly these four services. Two sites that surfaced during discovery are
**NOT** among the four and were excluded with cause:
- **games-web** — a `product-forge` concept (the comic browser-RPG presentation
  layer), already settled by **VERDICT 007** (redirect); not a `websites`-lane
  service.
- **superbot-stats** — a **phase-3 feature of botsite** (the OAuth personal-stats
  surface), already settled by **VERDICT 003**; a future botsite phase, not a
  separate deployed site.

## 2. Method

Method ladder: **(1) NUMERIC/MEASURED crawl simulation** for control-plane /
botsite / dashboard (crawled LIVE, 2 passes each, stdlib HTTP BFS, 80-page /
depth-2 cap) + **(2) MEASURED PROTOTYPE** for review (built locally from source,
served with `uvicorn review.app:app`, crawled at `127.0.0.1`, Playwright run
locally). The analyzer loads the four committed snapshots and re-derives all
metrics; it runs the whole computation **twice** and asserts the two results are
byte-identical, and self-checks every number.

```
python3 sims/owner-002-websites-purpose-nav/analyze_nav.py
```

Re-crawl (documented, agreement-reproducible — live sites are not
seed-deterministic):
`python3 sims/owner-002-websites-purpose-nav/crawl_site.py <base_url> <site_name>`

### Verbatim analyzer output

```
owner-002 websites-purpose-nav -- per-site summary (re-derived from snapshots)
============================================================================================
site            mode  pgs  maxd  avgd   dead deadend  forms   task  recrawl
--------------------------------------------------------------------------------------------
botsite         live   80     2  1.89      0       0      1   5/5     100%
control-plane   live   80     2  1.81     25      26     54   5/5     100%
dashboard       live   25     2  1.40      0       0      0   5/5     100%
review          loca    6     1  0.83      0       1      0   7/7     100%
--------------------------------------------------------------------------------------------
broken assets:  botsite 0/480  control-plane 0/6  dashboard 0/150  review 0/25
ds/ design sys: botsite=True  control-plane=False  dashboard=True  review=True  (shared by all: False)
console errors: botsite=not-captured (live/proxy)  control-plane=not-captured (live/proxy)  dashboard=not-captured (live/proxy)  review=6
============================================================================================
wrote results.json (canonical, sort_keys)
SELF-CHECKS: 243 passed, 0 failed
```

## 3. Per-site findings

Conformance FIRST (features present/absent, data REAL vs placeholder — the
VERDICT 007 lesson), then judged polish. Every finding ties to a measurement.

### 3a. control-plane — readiness board + journal browser (LIVE)

**Purpose-fit: serves-purpose — YES.** Real live data: the readiness board and
the journal browser are both present and populated from real GitHub-API data
(no fallback banner). Task battery **5/5** (view board, open a repo's
quality/progress detail, browse the journal, find a named repo's progress,
return home from the deepest page).

| metric | value |
|---|---|
| pages crawled | 80 (hit the 80-page / depth-2 cap) |
| max depth / avg depth | 2 / 1.81 |
| **dead links (HTTP ≥400)** | **25** (all 404) |
| dead-end pages | 26 (journal `file?path=` leaves — still nav-bearing) |
| orphan pages | 0 |
| broken assets | 0 / 6 |
| forms | 54 (journal filter forms) |
| re-crawl agreement (pass1≡pass2) | 100% |
| task battery | 5/5 |

**Ranked findings:**
1. **[TOP DEFECT] 25 dead in-content links (all 404), measured.** In-content
   markdown `.md` / `.sh` paths (e.g. `/README.md`, `/docs/mod-concepts.md`,
   `/planning/gen2-launch-record-2026-07-10.md`, `/environments/archetypes.md`)
   are rendered as **site-relative URLs** and 404 when clicked. They concentrate
   on the `/environments`, `/queue`, `/reviews`, and `/fleet` detail pages. These
   are documentation cross-references that were meant to point at GitHub, not at
   the control-plane host.
2. `/owner` returns **401** and is correctly gated — **unauditable from here**
   (no credentials; no Playwright auth attempted). Recorded as a limit, not a
   defect.
3. 26 dead-end pages are the journal `file?path=` leaves — expected terminal
   content, each still carrying the nav chrome (not orphans).

**Suggestion:** rewrite the in-content `.md`/`.sh` paths to absolute GitHub blob
URLs (or strip them) so the 25 links stop 404-ing.
**Sub-verdict: serves-purpose (real data, 5/5 tasks) — one fixable content-link defect.**

### 3b. botsite — public marketing + reference site (LIVE)

**Purpose-fit: serves-purpose — YES.** Feed is LIVE/real (no fallback banner;
`/status` reports "All systems operational", build `e0fd8ef7` 2026-07-11). Task
battery **5/5** including the explicit "confirm marketing data is REAL vs
placeholder" task.

| metric | value |
|---|---|
| pages crawled | 80 (cap hit — site is much larger) |
| dead links | 0 · orphan pages 0 · dead-end pages 0 |
| broken assets | 0 / 480 |
| forms | 1 (`/submit`) |
| re-crawl agreement | 100% · task battery 5/5 |

**Ranked findings:**
1. **Clean nav graph, zero defects in the crawled surface** (0 dead / 0 orphan /
   0 dead-end / 0 broken of 480 assets).
2. **[LIMIT — not a defect] the 80-page cap truncated a large reference site.**
   The `/commands/*` reference (~365 pages) and `/features` (~43 pages) far
   exceed the cap; only a slice was crawled (29 `/commands/*` + 44 `/features`
   in-cap). A broken route could hide beyond the cap — see ROBUST/LIMITS.

**Suggestion:** run a scoped `/commands/*` deep crawl (raise `--max-pages`) to
confirm all ~365 command pages are healthy.
**Sub-verdict: serves-purpose (real feed, clean graph) — deep-crawl to confirm the reference at scale.**

### 3c. dashboard — read-only developer oversight site (LIVE)

**Purpose-fit: serves-purpose — YES.** Real live data (build `448584e4`
2026-07-11). Read-only is **enforced and measured**: 0 forms sitewide. Task
battery **5/5**, including confirming `/admin` writes are stubbed.

| metric | value |
|---|---|
| pages crawled | 25 (13 routes + their `?refresh=1` duplicates) |
| max depth / avg depth | 2 / 1.40 |
| dead links | 0 · orphan pages 0 · dead-end pages 0 |
| broken assets | 0 / 150 |
| **forms (sitewide)** | **0** (read-only enforced) |
| re-crawl agreement | 100% · task battery 5/5 |

**Ranked findings:**
1. **Read-only is real, not just claimed: 0 forms across all 25 pages.**
2. `/admin` is present but **STUBBED and honestly labeled** "Control panel (stub)"
   — no hidden write surface.
3. **[MINOR] `?refresh=1` doubles the crawl surface** — every route appears twice
   (13 routes → 25 pages). Cosmetic; a canonical-URL hint would halve the graph.

**Suggestion:** canonicalize `?refresh=1` (rel=canonical or drop the query for
nav links) so the route set isn't double-counted.
**Sub-verdict: serves-purpose (real data, read-only proven) — one cosmetic canonicalization.**

### 3d. review — program review site for Anthropic reviewers (LOCAL build)

**Purpose-fit: serves-purpose — YES on the local build.** Content is **REAL**
from `data/snapshot.json` (126 PRs / 149 commits / 72 cards / 250 tests / 4
services), **no placeholders**. `/growth` renders **3 inline SVG charts, all
non-empty** (confirmed via local Playwright: `svg_count=3, svg_nonempty=3`). Task
battery **7/7** (overview, /process, /growth charts, /successes, /problems,
content-real check, all pages reachable from home nav).

| metric | value |
|---|---|
| pages crawled | 6 (5 HTML + `/story.json`) |
| max depth / avg depth | 1 / 0.83 (flat hub-spoke) |
| dead links | 0 · orphan pages 0 · broken assets 0 |
| dead-end pages | 1 (`/story.json` leaf — expected) |
| console errors (local Playwright) | 6 (5 × `ERR_CONNECTION_RESET` on the external font + 1 × `/favicon.ico` 404) |
| re-crawl agreement | 100% · task battery 7/7 |

**Ranked findings:**
1. **[TOP STRUCTURAL FINDING] the site is NOT deployed.** It is "Built for
   Anthropic reviewers," but reviewers **have no URL** — deploy is a pending
   OWNER-ACTION. Everything below is measured on a local build, so live behavior
   (TLS, Railway env, real host) is unverified.
2. **[MINOR] `/favicon.ico` 404 on every visit** (captured in the local console).
3. **[MINOR] one external runtime call** — Google Fonts in `base.html`
   (`fonts.googleapis.com`) is the only external asset in an otherwise
   network-free site (the `ERR_CONNECTION_RESET` console errors are that font
   failing through the proxy).

**Suggestions:** deploy the service (owner-action) so reviewers get a URL; add a
`/favicon.ico` route; vendor the Google font locally to make the site fully
network-free.
**Sub-verdict: serves-purpose on the local build (real content, 7/7 tasks) — NOT DEPLOYED (owner-action) + 2 minors.**

## 4. Cross-site consistency (measured + judged)

| site | shares `ds/` design system | nav-home rate (200-pages) | crawl_mode |
|---|---|---|---|
| botsite | **yes** | 100% | live |
| control-plane | **no** | 98.2% (54/55) | live |
| dashboard | **yes** | 100% | live |
| review | **yes** | 83.3% (5/6; the 6th is `/story.json`) | local |

**Measured finding: the `ds/` design system is shared by 3 of the 4 sites;
control-plane diverges** (it ships its own minimal styling — only 2 unique
assets, no `/static/ds/*`). botsite, dashboard, and review all load
`/static/ds/tokens.css` + `/static/ds/components.css` + `/static/ds/ds.js`.
Nav-home (a persistent home link) is near-universal (100% on the two full live
sites; the control-plane misses are the 404 leaves, and review's single miss is
the non-HTML `/story.json`).

**Judged:** the three `ds/`-sharing sites read as one system; **control-plane is
the styling outlier** — worth aligning to `ds/` for a consistent fleet look, but
not a functional defect.

## 5. The five validity-gate answers (verbatim, honest)

**1. COMPARABLE TO LIVE?** *"what the model abstracts away, and whether any gap could flip the conclusion"*

Three sites (control-plane, botsite, dashboard) were crawled **LIVE on their
production Railway URLs** — strong: this is real deployed behavior, not a model.
The pages are **no-JS server-rendered** (FastAPI/Jinja2), so a stdlib HTTP crawl
captures the **full navigation graph** — there is no client-rendered surface the
crawler misses. The **review** site was **NOT crawled live**: it is not deployed,
so it was built and served locally — a measured PROTOTYPE. Its live behavior
(real host, TLS, Railway env) is **unverified**; a Railway deploy could differ.
The one abstraction that could hide a defect: **real-browser console errors were
NOT captured on the 3 live sites** — Playwright was **SKIPPED** on all three
(Chromium build mismatch: installed pw 1.61 wants build 1228, only 1194 present;
`playwright install` disallowed; AND every `page.goto` returned
`net::ERR_CONNECTION_RESET` through the agent proxy). Console errors were
captured **only for review, locally** (6, all benign: external-font resets + a
favicon 404). The stdlib HTTP passes are authoritative for the nav graph;
JS-runtime errors on the live sites are a disclosed blind spot. None of this
flips the measured headlines (dead links, broken assets, task pass rates, forms).

**2. UNCORRUPTED?** *"no bugs (self-check the sim), no seeded luck, no parameter cherry-picking"*

**243 self-checks, 0 failed.** The analyzer runs the whole computation **twice**
and asserts byte-identical results (`analyze-determinism`). Every site's
**re-crawl agreement is 100%** (pass1 ≡ pass2 over the sorted url→status maps —
the live-site equivalent of "no seeded luck": the crawl was repeated in-run and
agreed exactly). No cherry-picking: the **full page set to the cap** is reported,
the **cap is disclosed**, and every dead-link / broken-asset / orphan / dead-end
URL is listed in `results.json` (counts self-checked to equal the listed URL
lengths). Headline numbers are guarded by explicit self-checks (control-plane
dead_links==25, dashboard forms_total==0, review crawl_mode=="local").

**3. ROBUST?** *"does the conclusion survive variation at the edges"*

The "serves-purpose" ruling survives on the crawled surface for all four sites
(clean graphs except control-plane's 25 content-link 404s, which are **off the
core task paths** — all task batteries pass 5/5 or 7/7). **What is NOT robust-
tested:** the **80-page cap** on botsite and control-plane means a broken route
could exist **beyond the cap** (botsite's ~365 `/commands/*` + ~43 `/features`,
and control-plane's deeper journal leaves were not exhausted). A deep crawl past
the cap was **not done** — disclosed. The 25-dead-link finding is robust (it
recurs identically across both passes and is off the core paths).

**4. REPRODUCIBLE?** *"committed code, one documented command, same result"*

Committed: the four crawl snapshots (`runs/*.json`) + `analyze_nav.py` +
`crawl_site.py` + `results.json`. **One command**
(`python3 sims/owner-002-websites-purpose-nav/analyze_nav.py`) re-derives every
number and is **byte-deterministic** (run-twice assert + canonical `sort_keys`
`results.json`), exit 0. The **live re-crawl** is reproducible via `crawl_site.py`
but is **agreement-reproducible, not seed-deterministic** — a live site can
change between runs, so reproducibility for the crawl layer is defined as
re-crawl agreement (measured 100%), exactly as VERDICT 005 redefined it for a
non-seedable live layer.

**5. LIMITS?** *"what this evidence does NOT show"*

- The **80-page cap** truncates the two large sites (botsite, control-plane) —
  routes beyond the cap are unaudited.
- **Real-browser console errors are uncaptured on the 3 live sites** (Chromium /
  proxy wall) — JS-runtime health on live is a blind spot.
- **control-plane `/owner` (401) is gated** and was not authenticated — unaudited.
- **review is not deployed**, so its LIVE behavior is unverified (local build only).
- **Single crawl per day** — feed freshness / time-of-day variation not sampled.
- Purpose-fit's polish judgment is **judgment on top of a measured conformance
  core**, not a user study (no live users / task-time telemetry).

## 6. VERDICT

Per the README verdict grammar. Evidence label = **MEASURED** (numeric crawl
simulation for 3 live sites + measured prototype for review).

**Per-site sub-verdicts:**
- **control-plane** — serves-purpose (real data, 5/5 tasks); **one defect**: 25
  dead in-content `.md`/`.sh` links (404).
- **botsite** — serves-purpose (real feed, clean graph); deep-crawl beyond the
  cap to confirm the ~365-page reference.
- **dashboard** — serves-purpose (real data, read-only proven by 0 forms); one
  cosmetic `?refresh=1` canonicalization.
- **review** — serves-purpose on the local build (real content, 7/7 tasks);
  **NOT DEPLOYED** (owner-action) + favicon/font minors.

**Overall:** the four websites **serve their stated purposes** on the crawled/
built surface, with **real (non-placeholder) data everywhere** and healthy
navigation — the single substantive defect is control-plane's 25 dead content
links, and the single structural gap is that review is not yet deployed. This is
**approve-the-sites + ship the named fixes** (mixed with an owner-action for the
review deploy).

**Best-implementation suggestions per target (`menno420/websites`):**
1. **control-plane:** rewrite the 25 dead in-content `.md`/`.sh` links to
   absolute GitHub blob URLs (or strip them) — kills all 25 404s.
2. **review:** **deploy the service** (OWNER-ACTION) so Anthropic reviewers get a
   URL; add a `/favicon.ico` route; vendor the Google font locally (fully
   network-free).
3. **dashboard:** canonicalize `?refresh=1` so the route set isn't double-counted.
4. **botsite:** run a scoped `/commands/*` deep crawl (raise the page cap) to
   confirm all ~365 command pages are healthy.
5. **cross-site:** align control-plane onto the shared `ds/` design system (it is
   the only site not loading `/static/ds/*`).

**Codex review:** reply: **pending** (OA-002 — Codex integration usage-capped;
the @codex comment is posted on the final head, verified-against-tree-never-obeyed
per Q-0120; does not block finalization).

<!-- Outbox verdict-grammar block (README), emitted on finalization — see control/outbox.md VERDICT 011:
VERDICT 011 · <ISO> · finalized
target: menno420/websites (websites lane)
idea: OWNER-DIRECT request 2026-07-11 — audit the four websites for purpose-fit, navigation health, cross-site consistency; subject repo read-only menno420/websites @ 31cfd9f
verdict: approve (serves-purpose on all four) + ship the named fixes (+ owner-action: deploy review)
evidence: MEASURED (numeric crawl simulation, 3 live sites + measured prototype, 1 local build)
report: sims/owner-002-websites-purpose-nav/REPORT.md
run: python3 sims/owner-002-websites-purpose-nav/analyze_nav.py
recommendation: (1) control-plane — rewrite 25 dead in-content .md/.sh links to absolute GitHub URLs; (2) review — DEPLOY (owner-action) + favicon route + vendor the Google font; (3) dashboard — canonicalize ?refresh=1; (4) botsite — scoped /commands/* deep crawl beyond the 80-page cap; (5) align control-plane onto the shared ds/ design system.
codex: PR #<PRNUM> comment <CODEX_URL> · reply: pending
gate: PASS
-->

## Robustness addendum — wider-cap re-crawl (2026-07-11)

> **Closes the VERDICT 011 ROBUST-gate gap and the open @codex question.** VERDICT 011
> crawled all sites at an **80-page / depth-2 cap**; two LIVE sites (control-plane,
> botsite) *hit that cap*, so a broken route could in principle have hidden beyond it.
> The @codex comment on PR #38 asked exactly this: *"could the 80-page cap hide a broken
> route that flips a sub-verdict?"* This addendum answers it with a measured **wider** re-crawl.
> Run: `python3 sims/owner-002-websites-purpose-nav/analyze_wide.py` (the original
> `analyze_nav.py` stays green and unchanged in its numbers).
> Wider snapshots: `runs/{control-plane,botsite}-wide.json` — crawled LIVE at **cap = 400
> pages / depth = 8**, **2 passes each** (5× the page budget, 4× the depth). control-plane's
> 401-gated `/owner` was **skipped** (GET-only crawler; no credentials, no password probe).

### Method (wider re-crawl)

Same stdlib BFS crawler (`crawl_site.py`), now invoked with `--max-pages 400 --max-depth 8`
(control-plane additionally `--skip-prefix …/owner`). The wider snapshots carry a
`"cap":{"pages":400,"depth":8}` field and the same schema as the original runs. A sibling
analyzer, `analyze_wide.py`, **reuses** `analyze_nav.py`'s measured metric functions and
`SelfCheck` harness (imported, never duplicated), ingests BOTH the narrow and wide snapshots,
and computes the new-vs-old delta. It is byte-deterministic (whole computation run twice,
asserted byte-identical) and self-checks: statuses in 100–599, `recrawl_agreement == 1.0`,
the wider **crawled-URL set is a superset-or-equal** of the narrow one (BFS-order guarantee,
home-slash-normalized), the wider **dead-link set is a superset-or-equal** of the narrow one
for control-plane (no known 404 dropped), and that no gated 401/403 route was crawled.
**`SELF-CHECKS: 2829 passed, 0 failed`**, exit 0; emits `results-wide.json`.

### Wider metrics (narrow 80/2 → wide 400/8)

| site | pages (n→w) | max depth (n→w) | dead links (n→w) | **new dead** | broken assets (wide) | orphans (wide) | dead-ends (n→w) | re-crawl | still truncated? |
|---|---|---|---|---|---|---|---|---|---|
| **control-plane** | 80 → **400** | 2 → **3** | 25 → **25** | **+0** | **0 / 6** | **0** | 26 → 5 | **100%** | **YES (400-cap)** |
| **botsite** | 80 → **400** | 2 → **2** | 0 → **0** | **+0** | **0 / 2400** | **0** | 0 → 0 | **100%** | **YES (400-cap)** |

Supporting coverage (measured from the wide snapshots):
- **control-plane** reached **depth 3** (257 depth-3 journal-leaf pages, **all HTTP 200**).
  Full status split at 400 pages: **375 × 200 + 25 × 404**. The **25 404s are byte-for-byte
  the SAME set** the 80-cap saw (superset holds, **0 dropped, 0 added**). Forms rose 54 → 370
  (more journal filter forms — expected, not a defect). **Still truncated** at the 400 cap.
- **botsite** is **breadth-bound**: 400 pages exhausted at **depth 2** (392 of 400 pages sit
  at depth 2) because the `/commands/*` + `/features` reference fans out there. The wider crawl
  reached **349 `/commands/*` pages** (of the ~365 that exist) + **44 `/features`** — **all
  HTTP 200**, **0 dead of 400 pages, 0 broken of 2,400 assets probed**. **Still truncated** at
  the 400 cap (~16 command pages beyond the budget), but 349/~365 spot-checked healthy is
  decisive at this coverage.

> Note on dead-ends (control-plane 26 → 5): this is **live-site variation, not a regression** —
> journal `file?path=` leaves that were bare terminals in the earlier narrow crawl now render
> with nav chrome (out-links), so fewer count as dead-ends. Dead-ends were never a defect class
> (they are expected terminal content); a lower count is neutral.

### New-vs-old delta — does the cap hide anything?

**Zero new defects surfaced beyond the 80-cap, on either site.**

| delta (wide − narrow) | control-plane | botsite |
|---|---|---|
| new dead links | **0** | **0** |
| new broken assets | **0** | **0** |
| new orphan pages | **0** | **0** |
| dropped (known) dead links | **0** | **0** |
| new **hard failures** of any class | **none** | **none** |

### The explicit @codex cap answer

**Does the 80-page cap hide a verdict-flipping route? — NO.** At **5× the page budget** (80 →
400) and, on control-plane, **one depth level deeper** (depth 2 → 3, 257 additional
all-200 journal leaves), and on botsite **320 additional pages** (349/~365 of the `/commands/*`
reference plus all `/features`, every one HTTP 200), the wider crawl surfaced **zero** new
dead links, **zero** new broken assets, and **zero** new orphans. control-plane's known 25
dead `.md`/`.sh` content links are reproduced **exactly** (superset, nothing dropped, nothing
added); botsite stays **0 dead / 0 broken**. **Neither sub-verdict flips:**

- **control-plane** — still *serves-purpose*; the single defect is still exactly the **25 dead
  in-content `.md`/`.sh` links**. The deeper crawl found **no additional broken route**. **Sub-verdict HOLDS.**
- **botsite** — still *serves-purpose* with a **clean nav graph**; 349/~365 command pages + all
  features now measured healthy (was ~29 command pages in-cap before). **Sub-verdict HOLDS.**

### Updated gate answers (superseding the 80-cap disclosures)

- **ROBUST (updated).** The 80-cap ROBUST gap is now **closed by measurement**: the
  "serves-purpose" ruling survives a 5×-wider, deeper re-crawl on both large sites with **no
  new defect of any class**. What remains **NOT** exhaustively crawled is the tail past **400**
  pages (botsite is breadth-bound and still truncated — ~16 command pages beyond the budget;
  control-plane still truncated at 400 with a depth-4+ journal tail unvisited), but at
  400-page/349-of-365 coverage with a **0.0% defect rate** in the newly-revealed surface, a
  hidden verdict-flipping route is not credible.
- **LIMITS (updated).** The cap is now **400**, not 80. **botsite is still truncated at 400** —
  349 of ~365 `/commands/*` pages were crawled and **all spot-checked HTTP 200** (0 dead / 0
  broken of 2,400 assets); the ~16 uncrawled command pages are the only unaudited botsite
  routes. **control-plane is still truncated at 400** (depth-3 tail reached, all 200; deeper
  journal leaves beyond the budget unvisited). Live-console-error capture, `/owner` (401,
  now explicitly skipped), and review-not-deployed limits are unchanged from §5.

**Bottom line:** the wider crawl **confirms** VERDICT 011 — it does not change the ruling. No
new @codex comment and no correction to the finalized outbox VERDICT 011 are warranted (no
sub-verdict flipped). The addendum only *strengthens* the ROBUST gate from "disclosed gap" to
"measured-and-clean at 5× the budget."
