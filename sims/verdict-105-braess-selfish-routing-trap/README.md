# VERDICT 105 — Braess's paradox in selfish task routing (P092, +13)

## Question
Does adding a free A→B shortcut to a congested 4-node Wardrop network RAISE everyone's selfish-equilibrium latency (the Braess paradox), with a monotone dose-response in the shortcut cost s that vanishes above an interior threshold s*, while a social-optimum router refuses the shortcut?

## Pinned world (one-liner)
Nodes {S,A,B,T}; legs S→A=x_SA, S→B=1, A→T=1, B→T=x_BT, shortcut A→B=s; N=1000 agents, β=12.0, damped-logit revision α=0.10, R=120 rounds; statistic = mean realized latency over last 30 rounds; N_SEEDS=30, SEED_BASE=20260719.

## Model
Agent-level stochastic logit with inertia (simultaneous revision): each round every agent, with prob α=0.10, redraws its route from the logit distribution p_r ∝ exp(-β·c_r) over available routes evaluated at the current (pre-revision) leg loads; else keeps its route. Closed network = routes {P:S→A→T, Q:S→B→T}; open adds Z:S→A→B→T. Realized round latency L = Σ_r f_r·c_r. Two-sample z across 30 seeds. Independent reimplementation from the registered spec — not the proposal dry-sim.

## Pre-registered decision rule
APPROVE iff R1 ∧ R2 ∧ R3 ∧ R4 (fired in order):
- R1: at s=0, μ_open > μ_closed and z ≥ 3σ.
- R2: excess(s)=μ_open(s)−μ_closed monotone non-increasing (≤1e-2 upward slack) and z(s) crosses below 3σ at an interior s* (0<s*<1.2).
- R3: 9 cells N∈{250,500,1000}×β∈{6,12,24} at s=0, all same-sign paradox, each z ≥ 3σ.
- R4: social planner minimizing mean latency (grid step 0.001) with shortcut open returns zero shortcut flow and M* ≤ μ_closed.

## How to run
    python3 braess_selfish_routing_sim.py
Writes results.json + run-stdout.txt; regenerates identically (delete both, rerun → byte-identical). Exits non-zero on any self-check failure, twin disagreement, or fixture drift. stdlib only.

## Outcome
APPROVE (first-failing gate: none). R1 gap +0.2612 @ z=501σ; R2 s*=1.1676, mono-violation 0.0; R3 all 9 same-sign, min z=122σ; R4 p*=0.5, f_Z*=0, M*=1.500. 19/19 self-checks; twins agree APPROVE/None; double-run byte-identical.
