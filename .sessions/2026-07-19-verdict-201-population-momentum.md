# VERDICT 201 — Population momentum (reproduce PROPOSAL 188)

> **Status:** `in-progress`

📊 Model: opus-4.8 · effort high · verdict-simulation / reproduction

started: 2026-07-19T23:41:12Z
flipped: (pending — flipped complete at close-out)

## 💡 What this verdict does

Reproduces PROPOSAL 188 (idea-engine, round-44 UNRELATED slot): a growing population (NRR 1.5) whose fertility drops instantly to exact replacement (NRR 1.0) keeps growing for roughly a generation, ending ~29% larger, purely because the young age structure inherited from the prior growth regime still carries a reproductive surplus. Leslie-matrix renewal; the deterministic momentum M_det = 1.291976.

## Method

Copy the committed verifier `ideas/fleet/population_momentum.py` from idea-engine byte-identically into `sims/verdict-201-population-momentum/`, run under SEED=20260717 (in-source), confirm the in-process double-run and a separate cross-invocation both byte-match, compute the results-dict sha256 and compare all 64 hex to the disclosed digest `fb74854ebd92a08fe48770136cf4e5645b47176394d1b04a70c2a0cc6ef36f33`, and evaluate the proposal's own G1/G2/G3 gates in order.

## previous-session review

Prior verdict card: VERDICT 200 (Glicko RD order-sensitivity, reproduce PROPOSAL 187) landed on main, ruled APPROVE — no carryover defects.

## Result

(pending — filled at flip to complete)

## Ruling

(pending — filled at flip to complete)
