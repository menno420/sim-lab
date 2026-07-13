# Session — VERDICT 026 — Braess's paradox added-edge frequency (idea-engine PROPOSAL 024)

> **Status:** `in-progress`
> 📊 Model: fable · 2026-07-13 · verdict-026 slice-worker session
> Objective: settle idea-engine PROPOSAL 024 (control/outbox.md · 2026-07-13T04:21:12Z · status: sim-ready; idea `ideas/fleet/braess-paradox-added-edge-2026-07-13.md`, the ORDER 004 rule-3 COMPLETELY-UNRELATED-domain rotation slot, round 2 — transportation / congestion routing games, Wardrop selfish-user equilibrium, rotated to a fresh fleet-external domain after round 1's social choice (PROPOSAL 017 → VERDICT 019)). Build the fully hermetic pre-registered measurement of Braess's paradox frequency and magnitude on the pinned diamond (nodes s,a,b,t; base edges e1=s→a, e2=a→t, e3=s→b, e4=b→t; optional bridge e5=a→b; unit demand D=1 routed to the UNIQUE Wardrop user equilibrium under affine non-decreasing latencies l_e(x)=a_e·x+b_e, a_e≥0; equilibrium and total cost C=Σ_e x_e·(a_e·x_e+b_e) computed exactly). Arm A: exhaustive integer census (a_e,b_e)∈{0,1,2}² on e1..e4 × (a5,b5)∈{0,1}² on the bridge = 9⁴·4 = 26,244 raw fixtures, 0-cost-without fixtures excluded and effective N reported, all arithmetic exact `fractions.Fraction`, no PRNG — f_A (paradox frequency: cost_with > cost_without), median-r and max-r among paradox fixtures (r = cost_with/cost_without). Arm S: seeded continuous robustness — a_e,b_e ~ U[0,2], `random.Random` seeds 20260740/20260741/20260742/20260743, documented float tolerance on the paradox comparison, pooled f_S. Arm-agreement gate: |f_S − f_A| ≤ 1.0 pp AND both arms yield the SAME call, else NULL-by-arm-disagreement. Bands registered in the idea file BEFORE any code: APPROVE iff f_A ≥ 0.15 OR median-r ≥ 1.15; REJECT iff f_A ≤ 0.03 AND max-r ≤ 1.05; NULL otherwise. Byte-identical re-run (Arm A platform-independent exact rationals; Arm S pinned to a stated CPython minor version); model-basis caveat stated (selfish Wardrop routing under uniform coefficients; the single most-likely-to-flip alternative is system-optimal routing, under which Braess cannot occur and f → 0). Hermetic: zero repo/network reads at run time — both arms construct their entire world in-sim.

## What happened

(in progress — filled at close-out)

## Run command

```
python3 sims/verdict-026-braess-added-edge/braess_added_edge_sim.py
```

## 💡 Session idea

(filled at close-out)

## ⟲ Previous-session review

(filled at close-out)
