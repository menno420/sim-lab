# VERDICT 105 — Braess's paradox in selfish task routing: a free shortcut raises everyone's greedy-equilibrium latency

> **Status:** `in-progress`
> 📊 Model: opus-4.8 · high · verdict-sim

Born in-progress as this session's first commit (born-red HOLD); flips to complete as the deliberate last step after the heartbeat.

## Objective
Verify idea-engine PROPOSAL 092 (+13 → VERDICT 105): adding a free A→B shortcut to a congested 4-node Wardrop network raises the selfish (greedy-logit) equilibrium mean latency from ~1.5 toward ~2.0, with a monotone dose-response in shortcut cost s that vanishes above an interior threshold s*, while a social-optimum router refuses the shortcut.

## Constraints honored
- Independent stdlib-only reimplementation from the registered spec (agent-level stochastic logit with inertia) — NOT the proposal's dry-sim.
- Deterministic: seeded RNG, 9dp rounding, byte-identical double run.
- Twin evaluators; gates fired R1→R2→R3→R4 in order; verdict per the pre-registered rule, never softened.
- SEEDLESS: pins own SEED_BASE=20260719; shared block 20261730 untouched.

## What happened
APPROVE — all four gates hold. R1 gap +0.2612 @ z=501σ; R2 s*=1.1676 (mono-violation 0.0); R3 all 9 cells same-sign, min z=122σ; R4 p*=0.5, zero shortcut flow, M*=1.500. 19/19 self-checks, twins agree APPROVE/None, double-run byte-identical (results.json f54b04f2…).

## ⟲ Previous-session review
V104 (P091 pity-timer anticipation collapse) landed APPROVE via PR #177, 16/16 self-checks, byte-identical — the born-red + heartbeat-before-flip choreography held. This session reuses that shape; no regressions observed in the sim-lab lane.

## 💡 Session idea
The excess-latency dose-response curve is a clean owner-facing knob: it quantifies exactly how "free" a shortcut must be (s < s*) before selfish routing degrades throughput — a reusable template for auditing any added-capacity change (CDN edge, cache tier, task-router fast-path) for Braess regressions before shipping.

📊 Model: opus-4.8 · high · verdict-sim
