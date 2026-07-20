# VERDICT 202 — Ski-rental keep-warm break-even (reproduce PROPOSAL 189)

> **Status:** in-progress

📊 Model: opus-4.8 · effort high · verdict-simulation / reproduction

started: 2026-07-20T00:44:31Z

## 💡 What this verdict does

Reproduces PROPOSAL 189 (idea-engine, `ideas/fleet/ski_rental_keep_warm.py`): the classic ski-rental break-even applied to a keep-warm-vs-cold decision. When idle gaps are long the break-even (rent-then-buy) policy beats always keep-warm; when gaps are short it beats always-cold; and a matched-cost exponential-idle regime recovers the randomized competitive ratio e/(e-1) ≈ 1.58. Deterministic break-even worst case approaches ~2× (ratio-of-means ~1.9× at the tested buy cost). Disclosed results-dict digest `0a0464162b20350c6d07104fed5bf62f1578021be85c0ecba18b4b07a3964c2b`.

## Method

Copy the committed verifier `ideas/fleet/ski_rental_keep_warm.py` from idea-engine byte-identically into `sims/verdict-202-ski-rental-keep-warm/`, run under SEED=20260717 (in-source), confirm the in-process double-run and a separate cross-invocation both byte-match, compute the results-dict sha256 and compare all 64 hex to the disclosed digest, and evaluate the proposal's own G1/G2/G3 gates in order.

## previous-session review

Prior verdict card: VERDICT 201 (Population momentum, reproduce PROPOSAL 188) landed on main, ruled APPROVE — no carryover defects.

## Result

_(pending — flipped to complete at close-out)_

## Ruling

_(pending)_
