# VERDICT 106 — Retry-amplified metastable overload collapse: a lane pool at ~60% utilization goes bistable above a critical retry-aggressiveness, and the fix is a retry budget, not more lanes

> **Status:** `complete`
> 📊 Model: opus-4.8 · high · verdict-sim

Born in-progress as this session's first commit (born-red HOLD); flips to complete as the deliberate last step after the heartbeat.

## Objective
Verify idea-engine PROPOSAL 093 (+13 → VERDICT 106): a lane pool held at ~60% utilization becomes BISTABLE above a critical retry-aggressiveness r_c≈0.57 — a transient load blip tips it into a self-sustaining retry storm that persists after load returns to baseline (hysteresis, width ≈56) — and the fix is a retry BUDGET, not more lanes (a retry-budget cap eliminates the HOT fixed point, restoring monostability).

## Constraints honored
- Independent stdlib-only reimplementation from the registered spec (mean-field root-solve + stochastic map, twin root-finders) — NOT the proposal's dry-sim.
- Deterministic: seeded RNG, byte-identical double run; stdout digest intentionally differs from the proposal's disclosed value (independent implementation).
- Twin evaluators + twin root-finders; gates fired R1→R2→R3→R4 in order; verdict per the pre-registered rule, never softened.
- SEEDLESS: pins own SEED_BASE=20260721; shared seed-ledger block 20261730 untouched.

## What happened
APPROVE — all four gates hold (first-failing gate: none). Independent stdlib-only sim (`sims/verdict-106-metastable-retry-storm-collapse/metastable_retry_storm_sim.py`) reimplemented the pinned world from the registered spec. Twins agree APPROVE/None, 25/25 self-checks, byte-identical double run.

- R1 bistability: three roots — COLD x=61.31 (u=0.613, stable), MIDDLE x=104.75 (unstable), HOT x=400.00 (u=4.0, stable) = λ/(1−r); seeded stochastic run COLD u=0.6146±0.0035 vs HOT u=3.9922±0.0535, separation 308.8σ ≥ 3σ. PASS.
- R2 hysteresis: adiabatic folds λ_up=78.07, λ_down=22.68, width=55.39 (≈56); coexistence at λ=60 confirmed (3 roots, λ_down<60<λ_up). PASS.
- R3 retry-lever: fold width monotone non-decreasing in r; r_c=0.5642 (≈0.566) where λ_down crosses the operating point λ=60; onset clean. PASS.
- R4 knockout: retry-budget cap b=0.20 → HOT root eliminated, monostable (1 root at x=61.31); uncapped had 3 roots. PASS.

Digests: results.json sha256 `3a1cb3c6…`, run-stdout.txt sha256 `d87e1dc8…`, fixtures.json sha256 `c475f3ec…`. `bootstrap.py check --strict` exit 0.

## ⟲ Previous-session review
V105 (P092 Braess selfish-routing trap, APPROVE, #178) landed clean via merge-on-green — the born-red + heartbeat-before-flip choreography held. This session reuses that shape; no regressions observed in the sim-lab lane at boot (origin/main tip 025e419).

## 💡 Session idea
The op-margin 60−λ_down(r) is a reusable owner-facing knob: it quantifies exactly how deep a load trough must go before a stormed pool self-recovers, and shows the HOT branch (x=λ/(1−r)) is retry-driven, not capacity-driven — adding lanes rescales u but leaves the λ/(1−r) collapse intact, so only a retry budget removes the second attractor. A natural template for auditing any retry/backoff policy for metastable-collapse risk before shipping.

📊 Model: opus-4.8 · high · verdict-sim
