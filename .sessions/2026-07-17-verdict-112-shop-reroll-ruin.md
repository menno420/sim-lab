# VERDICT 112 — shop-reroll ruin: in a K=3-item auto-battler/roguelike shop where the roll's best item is kept iff it clears an accept-threshold tau (else pay reroll cost C=0.05 and reroll), the net-utility-maximizing tau*=0.80 is strictly INTERIOR and greedy near-perfect rerolling (tau=0.95) is a value trap — U(tau)=E[M|M≥tau]−C·E[rerolls] is single-peaked below the greedy bar (P099, +13)

> **Status:** `in-progress`
> 📊 Model: opus-4.8 · high · review/verify

Born in-progress as this session's first commit (born-red HOLD); flips to complete as the deliberate last step after the verdict artifacts + heartbeat.

## Objective
Reproduce idea-engine PROPOSAL 099 (2026-07-17T20:18:16Z, sim-ready), offset +13 (P099 → V112), the round-22 GAME slot: on the pinned world, is the net-utility-maximizing accept-threshold tau* strictly interior AND is greedy near-perfect rerolling (tau=0.95) strictly worse net-value? Run the DISCLOSED stdlib-only reference verifier (idea-engine `ideas/superbot-games/shop_reroll_ruin.py`) VERBATIM under the pinned SEED=20260717, confirm all three pre-registered gates hold at their thresholds, and confirm the results-dict sha256 reproduces `7d7d7ad834978e75508c0c645935d6214b97550328d07c19d5b88130c662622b` (or disclose any divergence with its boundary).

## Constraints honored
- stdlib-only (random, math, json, hashlib), hermetic, deterministic — byte-identical double run of the results dict enforced (in-process AND cross-invocation).
- REFERENCE-VERIFIER REPRODUCTION slice (run the proposal's own committed verifier verbatim, SEED-pinned, confirm the disclosed results-dict sha256) — the same posture as V111, distinct from an independent reimplementation: the proposal ships a stdlib verifier and pins the exact sha256, so the tightest verification is a byte-level reproduction of that artifact.
- SEED=20260717 is proposal-owned and SEEDLESS at the ledger (in-file pin, NOT a seed-ledger draw); no seed-ledger block consumed, next free block stays 20261730.

## Gate plan (proposal labels G1/G2/G3, all ≥3σ unless noted)
- G1 value-trap headline: U(tau*) − U(tau=TAU_GREEDY=0.95) ≥ 3σ — greedy near-perfect rerolling is strictly worse than the optimal threshold.
- G2 interior optimum: U(tau*) > U(tau=0) AND U(tau*) > U(tau=TAU_MAX=0.99), each ≥ 3σ — tau* is a genuine interior peak, not an endpoint.
- G3 analytic-anchor MATCH: simulated E[rerolls] at tau* matches the geometric count tau*^K/(1−tau*^K) within 3σ (|z| < 3).
- APPROVE iff G1 ∧ G2 ∧ G3 at their pre-registered thresholds; verdict never softened.

<!-- Outcome + previous-session review + session idea written as the deliberate last step before the Status flip -->
