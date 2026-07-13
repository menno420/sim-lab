# Session — VERDICT 029 — comp/stipend envelope: the LAST routed lever (idea-engine PROPOSAL 027)

> **Status:** in-progress
> 📊 Model: fable · 2026-07-13 · verdict-029 slice-worker session
> Objective: settle idea-engine PROPOSAL 027 (control/outbox.md · 2026-07-13T06:04:37Z · status: sim-ready; idea `ideas/superbot/casino-comp-stipend-envelope-2026-07-13.md`, the ORDER 004 rule-3 GAME-MECHANICS rotation slot, round 3 — round 1 P020 → V022 rejected the odds lever, round 2 P023 → V025 rejected the entry-fee lever; this head prices the comp/stipend lever, the LAST of VERDICT 022's routed non-odds levers, ON V025's measured surviving substrate). Build the fully hermetic pre-registered four-band measurement: B₀ = 1,000 chips, F = 10, cap c = 5 FIXED, shapes T1/T2 (T3 excluded by citation + one monotonicity spot cell), takes t ∈ {0.05, 0.10} + t=0 control reporting-only; comp designs D1 qualified stipend / D2 handle rebate (cap 2σ·B₀) / D3 loss rebate — D1/D2 over σ ∈ {0.02, 0.05, 0.10, 0.20}, D3 over ρ ∈ {0.2, 0.4, 0.6, 0.8}; 48 decision cells + 4 σ=0 baseline cells that must reproduce V025's committed rows; policies R1/R5/RG/MC and profiles CASUAL/GRINDER/COMPULSIVE verbatim from V025 with comp counted in final wealth; a per-design FARMER family (wash-qualifier / cap-chaser / 12-variant stopper grid) attacking the new MINT band (max over policies ∪ farmers of E[session net incl. comp] ≤ 0). Arm A exact (comp-shifted binomial/DP FUN for all cells, σ=0 Fractions equal to V022/V025's committed values by exact rational equality, D1≡D2 and D3≡baseline FUN identities, the (σ−t)·B₀ pump line, exact banded-Fraction stopper DP on T1, t=0 P_double = 1/3); Arm S seeded MC `random.Random(20260752)` M = 5,000/2,000/500 with the 1.0 pp agreement gate, stability leg seed 20260753 (half M) must reproduce the ruling, reporting legs seed 20260754 (t=0 control, compulsive, house-net table, T3 monotonicity spot cell, aggregated-draw spot check), aux stream seed 20260755. Decision (registered order): REJECT iff no (design, size) rescues C1 = (T1, t=0.10) and none rescues C2 = (T2, t=0.05); APPROVE iff some design rescues C1 at ≥ 2 consecutive sizes all-four-pass, stability-reproduced; NULL otherwise with the per-design signature table as the pin. Hermetic: zero repo/network reads at run time; byte-identical re-run on pinned cpython-3.11.

## What happened

(in progress — fixtures-before-runner, then the dual-arm build, two full
process runs with external diff, then the INTAKE 027 / VERDICT 029 outbox
appends per the V015–V027 slice boundary.)

## Run command

```
python3 sims/verdict-029-comp-stipend/comp_stipend_sim.py
```
