# VERDICT 111 — the referral-bonus value trap: on a subcritical Galton–Watson referral cascade with saturating conversion q(b)=q_max·(1−e^(−b/b0)), the profit-maximizing bonus b* is strictly INTERIOR and strictly BELOW the virality-maximizing bonus b_viral — "tune for maximum viral coefficient" overspends

> **Status:** `in-progress`
> 📊 Model: [[fill: model line at flip]]

Born in-progress as this session's first commit (born-red HOLD); flips to complete as the deliberate last step after the heartbeat.

## Objective
Reproduce idea-engine PROPOSAL 098 (2026-07-17T15:47:53Z, sim-ready), offset +13 (P098 → V111), the round-22 venture-slot: on the pinned world, is the profit-optimal referral bonus b* strictly interior AND strictly below the viral-coefficient-maximizing bonus b_viral? Run the DISCLOSED stdlib-only reference verifier (idea-engine `ideas/venture-lab/referral_value_trap.py`) verbatim under the pinned SEED=20260717, confirm all three pre-registered gates hold at their thresholds, and confirm the results-dict sha256 reproduces `5438482c51479370e2a80aef0a01d3fe7f5617dcc1d30a622c9e74e1c8436786` (or disclose any divergence with its boundary).

## Constraints honored
- stdlib-only (random, math, json, hashlib, bisect), hermetic, deterministic — byte-identical double run of the results dict enforced (in-process and cross-invocation).
- This is a REFERENCE-VERIFIER REPRODUCTION slice (run the proposal's own committed verifier verbatim, SEED-pinned, and confirm the disclosed results-dict sha256), distinct from V110's independent-reimplementation posture — the proposal ships a stdlib verifier and pins the exact sha256, so the tightest verification is a byte-level reproduction of that artifact.
- SEED=20260717 is proposal-owned and SEEDLESS at the ledger (in-file pin, NOT a seed-ledger draw); no seed-ledger block consumed.

## Gate plan (proposal labels R1/R2/R3; the verifier's internal print-labels are G3/G2/G1 respectively)
- R1 branching-anchor match (verifier G3): |E_sim[T] − S/(1−m(b*))| / SE_T < 3σ — the simulated total-signups mean matches the geometric Galton–Watson anchor at b*.
- R2 interior optimum (verifier G2): Π̄(b*) > Π̄(0) AND Π̄(b*) > Π̄(B_HI=6.0), each ≥ 3σ — profit has a hard interior peak, beating both the no-bonus endpoint and a high bracketing bonus.
- R3 value trap / headline (verifier G1): Π̄(b*) > Π̄(b_viral=8.0) ≥ 3σ — the profit-optimal bonus strictly out-earns the virality-maximizing bonus.
- APPROVE iff R1 ∧ R2 ∧ R3, evaluated at their pre-registered thresholds; verdict never softened.

## ⟲ Previous-session review
[[fill: one-line previous-session review at flip]]

## 💡 Session idea
[[fill: one genuine new idea at flip]]

[[fill: model line footer at flip]]
