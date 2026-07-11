# Session — owner-002 robustness hardening — wider-cap re-crawl

> **Status:** `complete`
> 📊 Model: opus-4.8 · 2026-07-11 · hardening slice (continuous mode, sim-ready queue empty)
> Objective: close the VERDICT 011 ROBUST-gate 80-page-cap gap and the open @codex question
> ("could the 80-page cap hide a broken route that flips a sub-verdict?") by re-crawling the two
> LIVE sites that hit the cap (control-plane, botsite) under a WIDER cap (400 pages / depth 8, 2
> passes each), analyzing new-vs-old defects deterministically, appending a REPORT robustness
> addendum, and landing a READY merge-on-green PR (house protocol). READ-ONLY (GET/load only).

## What happened

VERDICT 011 crawled the four websites at an 80-page / depth-2 cap; two LIVE sites (control-plane,
botsite) *hit that cap*, leaving a disclosed ROBUST gap and an open @codex question on PR #38.
This hardening session re-crawled those two sites at **cap = 400 pages / depth = 8, 2 passes each**
(5× the page budget, 4× the depth) using the same `crawl_site.py` — extended with a backward-
compatible `--skip-prefix` so control-plane's 401-gated `/owner` is never fetched (GET-only; no
credentials, no password probe). Wider snapshots: `runs/{control-plane,botsite}-wide.json`.

A sibling analyzer, `analyze_wide.py`, **reuses** `analyze_nav.py`'s measured metric functions and
`SelfCheck` harness (imported, never duplicated), ingests both the narrow and wide snapshots, and
computes the new-vs-old delta. It is byte-deterministic (whole computation twice, byte-identical),
asserts the wider crawled-URL set and control-plane's wider dead-link set are supersets-or-equal of
the narrow ones, statuses in range, `recrawl_agreement == 1.0`, and no gated 401/403 route crawled.

**Measured result (2829 self-checks, 0 failed):**
- **control-plane** 80→400 pages, depth 2→**3** (257 depth-3 journal leaves, all HTTP 200), dead
  links **25→25 (+0 new)**, 0 broken of 6, 0 orphan. The known 25 `.md`/`.sh` 404s reproduced
  exactly (superset, 0 dropped / 0 added). Still truncated at the 400 cap.
- **botsite** 80→400 pages, **breadth-bound at depth 2** (392/400 at depth 2), dead **0→0 (+0)**,
  0 broken of **2,400** assets, 0 orphan. Reached **349 of ~365 `/commands/*`** + all 44
  `/features` — every page HTTP 200. Still truncated at the 400 cap (~16 command pages beyond).

**@codex cap answer: NO** — the 80-page cap does not hide a verdict-flipping route. At 5× the
budget and deeper/wider, **zero** new dead links / broken assets / orphans on either site.
**Neither sub-verdict flips**; VERDICT 011 is confirmed, not changed — so no new @codex comment and
no correction to the finalized outbox/status verdict are warranted (a flip would have been the
headline). The ROBUST gate moves from "disclosed gap" to "measured-and-clean at 5× the budget."

## Verdict

No verdict change. Hardening confirms VERDICT 011. Evidence label MEASURED (wider live crawl +
byte-deterministic delta analyzer); gate PASS.

## Run command

```
python3 sims/owner-002-websites-purpose-nav/analyze_wide.py   # wider-cap robustness (2829 checks)
python3 sims/owner-002-websites-purpose-nav/analyze_nav.py    # original, still green (243 checks)
```
Both stdlib-only, exit 0 iff every self-check passes; `results-wide.json` proven byte-identical on
re-run.

## 💡 Session idea

**Cap-robustness as a first-class close-out move:** when a measured crawl/sweep *hits its cap*, the
honest ROBUST answer is "disclosed gap," but the *cheap* upgrade is a bounded wider re-run whose
analyzer asserts **superset-or-equal** against the narrow baseline (no known defect dropped) and
counts only NEW hard failures. A 0.0% new-defect rate across 5× the surface converts a disclosed
limitation into a measured clearance — and a breadth-bound site (botsite: 400 pages, still depth 2)
is itself a finding worth naming, not a failure.

## ⟲ Previous-session review

VERDICT 011 disclosed the 80-cap as an un-robust-tested gap and posted it as the @codex question
rather than papering over it — which is exactly what made this hardening slice a clean, bounded
follow-up. Reusing the frozen-snapshot + byte-deterministic-analyzer discipline (VERDICT 005 / 011)
meant the wider evidence landed without re-litigating the method: same crawler, same metric
functions, new caps, superset self-checks. The one adjustment vs. an over-eager assumption: botsite
did NOT go deeper (breadth-bound at depth 2), so the "wider envelope" self-check asserts breadth OR
depth, not depth alone.
