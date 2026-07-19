# VERDICT 200 — Glicko RD order-sensitivity (reproduce PROPOSAL 187)

> **Status:** `complete`

📊 **Model:** opus-4.8 · effort high · verdict-simulation / reproduction

started: 2026-07-19T23:11:32Z
flipped: 2026-07-19T23:21:35Z

## 💡 What this verdict does

Reproduces PROPOSAL 187 (idea-engine, round-44 GAME slot): on a Glicko-1 ladder that updates one game per rating period, an identical 6W-6L record against an identical opponent field settles at a DIFFERENT final rating depending only on the ORDER of results, because the rating deviation (RD) shrinks after each game and weights early (high-RD) games more than late ones. Streak order (WWWWWWLLLLLL) lands a mean ~60 Glicko points BELOW alternating order (WLWLWL) for the identical 6W-6L record.

## Method

Copy the committed verifier `ideas/superbot-games/glicko_rd_order_sensitivity.py` from idea-engine byte-identically into `sims/verdict-200-glicko-order-sensitivity/`, run under SEED=20260717 (in-source), confirm in-process double-run and separate cross-invocation both byte-match, compute the results-dict sha256 and compare all 64 hex to the disclosed digest `d4f690a51493a8fc32dd0971548078b059277ba81b6e02c84364415f4d168ba6`, and evaluate the proposal's own G1/G2/G3 gates in order.

## previous-session review

Prior verdict card: VERDICT 199 (follow-on reserve starvation, reproduce PROPOSAL 186) landed on main @289aa0b, ruled APPROVE — no carryover defects.

## Result

Verifier copied byte-identically from idea-engine @678c37c (`diff` exit 0; file sha256 `2267c694d63e3a1de95f88bec885c1e455f916e1bd597cb470c947b4ff9e6f98`, git blob `59d95a4ede7b449cf8a694794ad7dc7cb974c37f`). Ran under the in-source SEED=20260717: two independent invocations produced byte-identical stdout (`diff` exit 0) and the in-process double-run assert held. Results-dict sha256 `d4f690a51493a8fc32dd0971548078b059277ba81b6e02c84364415f4d168ba6` MATCHES the disclosed PROPOSAL 187 digest across all 64 hex (byte-grep count 1, no truncation). Gates in order: G1 order-effect PASS (mean −60.205174, z=−118.692568), G2 sign+magnitude PASS (same-sign 0.9996, |mean| 60.205174), G3 robust +200 shift PASS (mean −54.313763, z=−100.513794); all_pass=true. Grounding `http://www.glicko.net/glicko/glicko.pdf` resolves live and documents RD, the g(RD)·(s−E) per-game update, and RD-shrink-after-each-game. Full run stdout: `run-stdout.txt`; detail: `probe-report.md`.

## Ruling

**APPROVE.** The order-sensitivity head reproduces exactly: an identical 6W-6L record settles ~60 Glicko points lower under streak order (WWWWWWLLLLLL) than alternating order (WLWLWL), driven by RD shrinking after each game so early high-RD games carry a larger g(RD)·(s−E)-weighted update than late ones. All three of the proposal's own gates pass in order and the disclosed results-dict digest matches to the byte.
