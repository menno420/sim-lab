# Session — VERDICT 021 — backlog low-water signal threshold (idea-engine PROPOSAL 019)

> **Status:** `in-progress`
> 📊 Model: fable · 2026-07-13 · verdict-021 slice-worker session
> Objective: settle idea-engine PROPOSAL 019 (control/outbox.md · 2026-07-13T01:34:28Z · status: sim-ready; idea `ideas/fleet/backlog-low-water-signal-tuning-2026-07-13.md`, landed via idea-engine PR #284, main `f7906e5`) — the ORDER 004 rule-3 FLEET-BACKLOGS rotation slot, restarting the cycle after 017 unrelated / 018 venture. Build the fully hermetic pre-registered reorder-point sim for never-idle lane backlogs: discrete wakes H=2,000, b₀=6, R=4; per wake in pinned order (replenishment lands → consumption p_c ∈ {0.6, 1.0}, dry wake iff demand meets b=0 → organic arrival A1/A2/A3, A2 anchored to the websites backlog's observed multiset {2,4,5,11} → signal policy N ∈ {0(off),1,2,3,4,6}, one outstanding, +R at t+L, L ∈ {1,2,4}); 18 cells = 3 regimes × 2 p_c × 3 L, M=300 seeded reps per (cell,N), `random.Random(20260719)`, pinned loop order; metrics D = dry wakes / demand wakes, S = signals per 100 wakes, mean backlog (reporting); sensitivity legs R ∈ {2,8}, b₀ ∈ {3,12}, H=500 and a decision-stability leg M=50 seed 20260720, all reporting-only. Then issue exactly ONE of REJECT-a (D(0) ≤ 0.05 in ≥ 80% of cells, checked FIRST) / APPROVE (N* = smallest N with D ≤ 0.05 AND S ≤ 25 exists in ≥ 80% of cells AND median ΔD = D(0) − D(N*) ≥ 0.10 → threshold = grid-median N*, stating whether the bullet's "~3" lies within ±1) / REJECT-b (N* exists in < 50% of cells) / NULL (flip axis named via per-axis N*-exists shares and median ΔD) per the decision rule registered in the idea file BEFORE any code existed, with the n=4 anchor caveat and the latency-in-wakes mapping stated.

## What happened

(in progress — born-red card; the strict gate fails on an in-progress newest
card by design, so the flip to `complete` rides the same push as the work —
the V018/V019 one-push choreography.)

## Run command

```
python3 sims/verdict-021-backlog-low-water/backlog_low_water_sim.py
```
