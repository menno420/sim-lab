# VERDICT 200 — Glicko RD order-sensitivity (reproduce PROPOSAL 187)

> **Status:** `in-progress`

📊 **Model:** opus-4.8 · effort high · verdict-simulation / reproduction

started: 2026-07-19T23:11:32Z

## 💡 What this verdict does

Reproduces PROPOSAL 187 (idea-engine, round-44 GAME slot): on a Glicko-1 ladder that updates one game per rating period, an identical 6W-6L record against an identical opponent field settles at a DIFFERENT final rating depending only on the ORDER of results, because the rating deviation (RD) shrinks after each game and weights early (high-RD) games more than late ones. Streak order (WWWWWWLLLLLL) lands a mean ~60 Glicko points BELOW alternating order (WLWLWL) for the identical 6W-6L record.

## Method

Copy the committed verifier `ideas/superbot-games/glicko_rd_order_sensitivity.py` from idea-engine byte-identically into `sims/verdict-200-glicko-order-sensitivity/`, run under SEED=20260717 (in-source), confirm in-process double-run and separate cross-invocation both byte-match, compute the results-dict sha256 and compare all 64 hex to the disclosed digest `d4f690a51493a8fc32dd0971548078b059277ba81b6e02c84364415f4d168ba6`, and evaluate the proposal's own G1/G2/G3 gates in order.

## previous-session review

Prior verdict card: VERDICT 199 (follow-on reserve starvation, reproduce PROPOSAL 186) landed on main @289aa0b, ruled APPROVE — no carryover defects.

## Result

_pending — filled at flip to complete._

## Ruling

_pending — filled at flip to complete._
