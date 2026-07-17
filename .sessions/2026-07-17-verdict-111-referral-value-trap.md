# VERDICT 111 — the referral-bonus value trap: on a subcritical Galton–Watson referral cascade with saturating conversion q(b)=q_max·(1−e^(−b/b0)), the profit-maximizing bonus b* is strictly INTERIOR and strictly BELOW the virality-maximizing bonus b_viral — "tune for maximum viral coefficient" overspends

> **Status:** `complete`
> 📊 Model: opus-4.8 · high · verdict-sim

Born in-progress as this session's first commit (born-red HOLD); flips to complete as the deliberate last step after the heartbeat.

## Objective
Reproduce idea-engine PROPOSAL 098 (2026-07-17T15:47:53Z, sim-ready), offset +13 (P098 → V111), the round-22 venture-slot: on the pinned world, is the profit-optimal referral bonus b* strictly interior AND strictly below the viral-coefficient-maximizing bonus b_viral? Run the DISCLOSED stdlib-only reference verifier (idea-engine `ideas/venture-lab/referral_value_trap.py`) verbatim under the pinned SEED=20260717, confirm all three pre-registered gates hold at their thresholds, and confirm the results-dict sha256 reproduces `5438482c51479370e2a80aef0a01d3fe7f5617dcc1d30a622c9e74e1c8436786` (or disclose any divergence with its boundary).

## Constraints honored
- stdlib-only (random, math, json, hashlib, bisect), hermetic, deterministic — byte-identical double run of the results dict enforced (in-process and cross-invocation).
- This is a REFERENCE-VERIFIER REPRODUCTION slice (run the proposal's own committed verifier verbatim, SEED-pinned, and confirm the disclosed results-dict sha256), distinct from V110's independent-reimplementation posture — the proposal ships a stdlib verifier and pins the exact sha256, so the tightest verification is a byte-level reproduction of that artifact.
- SEED=20260717 is proposal-owned and SEEDLESS at the ledger (in-file pin, NOT a seed-ledger draw); no seed-ledger block consumed, next free block stays 20261730.

## Gate plan (proposal labels R1/R2/R3; the verifier's internal print-labels are G3/G2/G1 respectively)
- R1 branching-anchor match (verifier G3): |E_sim[T] − S/(1−m(b*))| / SE_T < 3σ — the simulated total-signups mean matches the geometric Galton–Watson anchor at b*.
- R2 interior optimum (verifier G2): Π̄(b*) > Π̄(0) AND Π̄(b*) > Π̄(B_HI=6.0), each ≥ 3σ — profit has a hard interior peak, beating both the no-bonus endpoint and a high bracketing bonus.
- R3 value trap / headline (verifier G1): Π̄(b*) > Π̄(b_viral=8.0) ≥ 3σ — the profit-optimal bonus strictly out-earns the virality-maximizing bonus.
- APPROVE iff R1 ∧ R2 ∧ R3, evaluated at their pre-registered thresholds; verdict never softened.

## Outcome — APPROVE (first-failing-gate None)
All three gates PASS, reproducing the proposal's disclosed dry-sim EXACTLY:
- R1 PASS — E_sim[T]=3035.927 (se 2.6884) vs analytic 3039.057, |z|=1.16σ < 3σ.
- R2 PASS — Π̄(b*)=21197.596 > Π̄(0)=10000.000 at +757.29σ AND > Π̄(B_HI=6.0)=19932.238 at +62.75σ.
- R3 PASS — Π̄(b*)=21197.596 > Π̄(b_viral=8.0)=15575.369 by 5622.227 at +335.89σ.
results.json sha256 `5438482c51479370e2a80aef0a01d3fe7f5617dcc1d30a622c9e74e1c8436786` = the proposal's disclosed expected digest, byte-identical across a double run (in-process and cross-invocation). b*=4.5 (R0=0.670951) strictly interior, b_viral=8.0 (R0=0.736263); the profit optimum sits below the virality optimum by 3.5 bonus units.

## ⟲ Previous-session review
Prior loop P097 → V110 (long-chain process-flexibility max-flow) landed APPROVE — sim-lab PR #183 (merged to main, head 5eb983f), sims/verdict-110-long-chain/. V110's independent-reimplementation + twin-evaluator (Edmonds-Karp vs Ford-Fulkerson) discipline is the sibling posture to this slice's reference-verifier reproduction: both answer "does the pinned claim survive an outside run," V110 by rebuilding the model from spec and V111 by byte-reproducing the shipped verifier's pinned digest — the proposal here shipped a stdlib verifier and pinned the exact sha256, so reproduction is the tighter of the two checks and it landed to the digit.

## 💡 Session idea
The value trap is MARGIN-DEPENDENT, and the proposal pins a single M=10.0 that hides the dependence. b* is the argmax of Π(b)=S·(M−b·m(b))/(1−m(b)); the bonus-cost term −b·m(b) is what pulls the optimum interior and below b_viral, and its weight relative to the M·E[T] reach term scales like 1/M. So there should be a critical margin M_crit above which chasing virality STOPS overspending — as M grows the profit-optimal bonus rides UP toward the grid ceiling and b* → b_viral (the trap collapses for high-LTV products), while below some low margin the interior peak instead retreats toward b=0 (thin-margin products should barely pay a bonus at all). The natural next venture-lab slice holds K/q_max/b0 fixed and sweeps M over a grid, locating M_crit as the margin where b*(M) first reaches B_HI, with a single new gate: b*(M_low) strictly interior AND b*(M_high) pinned at the ceiling, with ≥3σ separation in the argmax location across the sweep. That turns the one-point "tune for profit, not virality" rule into a margin-conditioned policy — the actionable version of the finding for a real product deciding a referral budget.

📊 Model: opus-4.8 · high · verdict-sim
