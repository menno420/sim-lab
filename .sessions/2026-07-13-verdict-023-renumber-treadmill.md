# Session — VERDICT 023 — migration renumber-treadmill residual (idea-engine PROPOSAL 021)

> **Status:** `in-progress`
> 📊 Model: fable · 2026-07-13 · verdict-023 slice-worker session
> Objective: settle idea-engine PROPOSAL 021 (control/outbox.md · 2026-07-13T02:36:37Z · status: sim-ready; idea `ideas/superbot/migration-renumber-treadmill-residual-2026-07-13.md`, landed via idea-engine PR #287, main `8022a9d`) — the ORDER 004 rule-3 FLEET-BACKLOGS rotation slot, round 2, harvested from the superbot section's 237-doc backlog (canonical doc `migration-number-collision-guard-2026-06-22.md` @ fd638e3, byte-same at live 4522522; the recorded incident is #1279's four-renumber afternoon). Build the fully hermetic pre-registered continuous-time event sim of migration-number races: PRs arrive Poisson λ ∈ {1, 4, 12}/day, develop W = 8 h, validate V ∈ {0.25, 2, 24} h; collision at merge-attempt iff the held number was merged by another PR since pick → renumber (fix latency d = 0.5 h) → re-validate; policies by pick time — P0 at open + each fix start (windows W+V then d+V), P1 re-pick at every push (every window = V, the shipped Option-1 checker's semantics), P3 assign-at-merge (exposure 0, MUST measure exactly zero collisions — built-in control); H = 2,000 h, first 200 h warm-up discarded, M = 40 reps per (cell, policy), `random.Random(20260723)`, pinned loop order; metrics on the post-warm-up merged population R = renumbers per merged PR and T = share with ≥ 2 renumbers, plus reporting-only latency inflation vs P3, max simultaneous holders, and the endogenous/exogenous amplification ratio vs the exact Arm-A closed forms P(N≥1) = p(w₁), P(N≥2) = p(w₁)·p(w₂), E[N] = p(w₁)·e^(λw₂), p(w) = 1 − e^(−λw). Validation gate: Arm S in exogenous mode (external Poisson appends, one focal PR, M = 20,000, seed 20260726) within 1.0 pp absolute of Arm A on P(N≥1) and P(N≥2) in every covered cell AND endogenous P3 exactly zero collisions, else the run is INVALID. Reporting-only legs: sensitivity d ∈ {0.25, 2}, W ∈ {1, 24}; jitter seed 20260725; stability M = 8 seed 20260724 (must reproduce the ruling); the #1279 anchor (λ=12/day, V=2, d=0.5, P0 — E[N] and P(N≥3), plausibility vs an n=1 anecdote, never a fit). Then issue exactly ONE of APPROVE (R ≤ 0.10 AND T ≤ 0.01 in ≥ 8 of 9 endogenous P1 cells, gate passed; checked FIRST) / REJECT (T > 0.05 in ≥ 5 of 9 cells → the per-cell residual-tax table rides to the Option-3 plan) / NULL (flip axis named via per-axis APPROVE-pass shares and median T; the conditional per-PR-class rule is the citable finding) per the decision rule registered in the idea file BEFORE any code existed, with the Poisson-arrivals and uniform-compliance boundaries stated (P1's residual is a FLOOR — APPROVE is the fragile direction).

## What happened

[[fill: run summary — self-check counts, byte-identical evidence, ruling + headline numbers, slice-boundary and choreography notes]]

## Run command

```
python3 sims/verdict-023-renumber-treadmill/renumber_treadmill_sim.py
```

## 💡 Session idea

[[fill: one exportable idea from this session]]

## ⟲ Previous-session review

[[fill: review of .sessions/2026-07-13-verdict-021-backlog-low-water.md]]
