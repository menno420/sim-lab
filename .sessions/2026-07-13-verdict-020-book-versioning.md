# Session — VERDICT 020 — book breadth vs versioning depth: fixed-budget allocation sweep (idea-engine PROPOSAL 018)

> **Status:** `in-progress`
> 📊 Model: fable · 2026-07-13 · verdict-020 slice-worker session
> Objective: settle idea-engine PROPOSAL 018 (control/outbox.md @ 2026-07-13T01:15:34Z, sim-ready; idea ideas/venture-lab/book-versioning-breadth-depth-allocation-2026-07-13.md @ cb2b6ee, landed via idea-engine PR #283) — under the pinned production-night model (budget B=12, size leg B=6 reporting-only; new title costs 1, extra version costs c ∈ {0.25, 0.5, 0.75}; K ∈ {1,2,3,4,6}, T_eff = B/(1+c·(K−1)) fractional by linearity; θ ~ N(0,1), version quality θ+ε with ε ~ N(0, σ_v²), σ_v ∈ {0.2, 0.5, 1.0}; revenue exp(q+L), L ~ N(−σ_m²/2, σ_m²), σ_m ∈ {0.5, 1.5, 2.5}; Mode P pick-best at fidelity f ∈ {0.2, 0.6, 1.0}; Mode A publish-all at audience separation s ∈ {0, 0.5, 1}), measure K* = argmax_K E[revenue per unit budget] and ΔR = R(K*)/R(1) − 1 per cell (81 cells per mode) in Arm A (analytic, Simpson quadrature, seedless, Mode P f=1 slice) and Arm S (seeded MC, M=20,000, seeds 20260716/20260717, stability leg M=2,000 seed 20260718, Arm A/S agreement ≤ 1.5% on every f=1 cell) — and issue exactly ONE of APPROVE / REJECT / NULL per the pre-registered bands.

## What happened

(in progress — born-red hold; flipped complete in this session's final commit)
