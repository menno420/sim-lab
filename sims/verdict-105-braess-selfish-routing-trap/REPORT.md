# VERDICT 105 — Braess's paradox in selfish task routing — REPORT

RULING: APPROVE (first-failing gate: none).

## What was tested
idea-engine PROPOSAL 092 (2026-07-17T06:59:49Z, sim-ready) → VERDICT 105 (+13). Claim: a free A→B shortcut added to a congested 4-node Wardrop/selfish-routing network raises the greedy (logit) equilibrium mean latency ~1.5→~2.0, with a monotone dose-response in shortcut cost s vanishing above an interior threshold s*, and a social-optimum router that refuses the shortcut. Independent stdlib-only reimplementation (agent-level stochastic logit with inertia), not the proposal's dry-sim.

## Pinned world
Nodes {S,A,B,T}; legs S→A=x_SA (congestion), S→B=1, A→T=1, B→T=x_BT (congestion), shortcut A→B=s. N=1000, β=12.0, α=0.10, R=120, statistic=mean realized latency over last 30 rounds; N_SEEDS=30, SEED_BASE=20260719; s-grid {0.0..1.2 step 0.1}; R3 grid N∈{250,500,1000}×β∈{6,12,24}; social-opt grid step 0.001; SIG=3.0σ; MONO_TOL=1e-2; R4_M_TOL=1e-6.

## Dose-response
excess(s) falls monotonically from +0.2612 @ s=0 to ~0 by s=1.2 (max upward violation 0.000000); z falls from 501σ @ s=0 to 5.92σ @ s=1.1 to 1.60σ @ s=1.2. Full table in results.json (dose_response) and run-stdout.txt.

## Gate margins
- R1 paradox-exists: μ_open=1.761316, μ_closed=1.500109, gap=+0.261206, z=501.1σ. PASS.
- R2 dose-response: max upward excess violation 0.000000 (≤1e-2); interior s*=1.167563 (linear-interp of z crossing 3σ between s=1.1 and s=1.2). PASS.
- R3 robustness: 9/9 cells pass, all same sign (positive), min z=122.1σ (N=250,β=6). PASS.
- R4 social-optimum control: p*=0.5, z*(shortcut flow)=0.0, M*=1.500000 ≤ μ_closed. PASS.

## Twins & self-checks
Twin evaluators (ordered if-chain + table scan) agree: APPROVE / first-failing gate None. Self-checks 19/19 pass.

## Cross-check against the proposal dry-sim
Convergent on the core paradox: μ_open 1.76132 vs dry-sim 1.76083; μ_closed 1.50011 vs 1.50010; gap +0.26121 vs +0.26072; R4 zero shortcut flow identical. Divergent, as expected for an independent dynamics implementation: significance magnitudes higher (R1 501σ vs 355σ; R3 min 122σ vs 135σ) and interior threshold s*=1.168 vs 1.095 — both strictly interior, all gate outcomes identical. This is a CONFIRM, not a digit-level reproduction.

## Finding (non-gating)
The selfish equilibrium settles at μ≈1.76, below the pure-Nash Braess collapse of 2.0: at β=12 bounded rationality leaves ~28% of agents on the two direct routes, softening but not removing the paradox. The excess-latency curve is a reusable audit knob for added-capacity changes.

## Digests
- results.json sha256 f54b04f2ffed5c8d10ed368380bfeaccbb7cf396a83a5d6fb810185e3fbd0794
- run-stdout.txt sha256 09c2da9058fc05b386e5b88bf623c321a22d4d26e05182eacae748ffc662b787
- fixtures.json sha256 30b2267111cc2b2bc51b30219be3cf7ac24228de3ed5b73809017b72ffbec8f9
Double run (delete results.json + run-stdout.txt, rerun) → byte-identical.

## Verdict
APPROVE. The Braess paradox reproduces independently on the pinned world; all four pre-registered gates hold; the claim is CONFIRMED.
