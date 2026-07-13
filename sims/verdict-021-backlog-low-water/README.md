# verdict-021 · backlog-low-water

Does the websites backlog bullet's "~3" low-water threshold earn its heartbeat
line? Answers idea-engine PROPOSAL 019 (control/outbox.md
2026-07-13T01:34:28Z, idea
`ideas/fleet/backlog-low-water-signal-tuning-2026-07-13.md`, landed via
idea-engine PR #284, main `f7906e5`) — the ORDER 004 rule-3 FLEET-BACKLOGS
rotation slot (fully hermetic per the PROPOSAL 017/018 precedent: every
fixture is a pinned constant committed with the sim, zero repo/network reads
in the verdict session). Under the pinned never-idle lane model (H=2,000
wakes, b₀=6, R=4; consumption p_c ∈ {0.6, 1.0}, dry wake iff demand meets an
empty backlog; organic arrivals A1 steady-small / A2 bursty-real (anchored to
the observed multiset {2,4,5,11}) / A3 harvest-scarce; signal policy
N ∈ {0(off),1,2,3,4,6}, one outstanding, +R after L ∈ {1,2,4} wakes), what
are D = dry wakes / demand wakes and S = signals per 100 wakes per (cell, N)
across the 18 cells — landing REJECT-a / APPROVE / REJECT-b / NULL per the
decision rule registered in the idea file before any code existed?

## Run (one command)

```
python3 sims/verdict-021-backlog-low-water/backlog_low_water_sim.py
```

Exit 0 iff all 411,339 self-checks pass. Deterministic — the only randomness
is `random.Random(<pinned seed>)` consumed in the pinned loop order (cells
lexicographic, N ascending, replications sequential; per-wake draws:
consumption, arrival-fire, batch-size), no network, no git, no wall clock, no
`hash()`. stdout and `results.json` are byte-identical across process runs
(verified by external `diff` of two complete runs, cpython-3.11). Runtime ~31 s.

## Files

- `backlog_low_water_sim.py` — stdlib-only driver: the pinned four-step wake
  loop, the full 18-cell × 6-N grid at M=300 (primary, seed 20260719), the
  M=50 seed-20260720 decision-stability leg, five reporting-only sensitivity
  legs (R ∈ {2,8}, b₀ ∈ {3,12}, H=500 at M=50), the exact-Fraction decision
  rule evaluated in the pre-registered order, and the self-checks
  (per-replication conservation identities, one-outstanding/spacing/count
  invariants, an independent trace-replay re-implementation on strided
  (cell,N) pairs, hand-derived pins, fixture cross-checks, an independent
  second decision evaluator).
- `fixtures.json` — the pre-registration, committed BEFORE the runner: all
  constants verbatim from the idea file ({H, M, b₀, R, N-grid, L-grid, regime
  constants incl. the observed multisets, p_c grid, band constants, seeds}),
  the pinned wake/draw/loop order, the decision rule + evaluation order +
  consequences, the two hand-derived pin scenarios with full derivations, and
  the ONE intake-time parameter decision (sensitivity legs at M=50 — the idea
  file leaves their M unpinned; disclosed, reporting-only).
- `results.json` — committed run output: the full {D, S, mean backlog} ×
  (cell, N) table for every leg, the N*/ΔD summary, per-axis N*-exists
  shares, decision detail per leg, self-check counts, cpython pin.
- `REPORT.md` — the finalizable verdict report (validity gate + the VERDICT
  021 ruling).

## Verdict (summary — full report in REPORT.md)

**approve (pre-registered)** — the signal earns its line, but at a LOWER
threshold than the bullet's "~3":

- **REJECT-a fails first (checked first):** the no-signal baseline clears
  D(0) ≤ 0.05 in only **3/18 cells** (the three A1 steady-small p_c=0.6
  cells) — organic refill does NOT suffice; A3 harvest-scarce baselines run
  D(0) = 0.75–0.85.
- **APPROVE binds:** N* exists in **18/18 cells** (≥ 80%) and median ΔD =
  508,621/1,200,000 ≈ **0.424** (≥ 0.10) — the signal buys ~42 points of
  dry-wake reduction at the median cell.
- **Recommended threshold = grid-median N\* = 1.** Per-cell N*: 14 cells at
  N*=1, two at N*=2 (A1 p_c=1.0 L=4; A3 p_c=0.6 L=4), two at N*=3 (A2 and A3
  at p_c=1.0, L=4 — burst-poor or scarce arrivals under overnight latency).
- **The bullet's "~3" is NOT within ±1 of the grid-median** (|3 − 1| = 2):
  as a fleet-wide default "~3" over-signals; it is exactly right only in the
  two hardest cells (p_c=1.0, L=4, thin arrivals), where N=3 is also the
  structural-zero threshold (a signal at b=3 always lands before three
  consecutive demands drain it).
- Alarm cost at N* stays inside the band everywhere: S(N*) ranges 0.43–21.3
  per 100 wakes (analytic steady-state: S ≈ 25·deficit/R; A3 p_c=1.0 sits at
  21.2 vs the analytic 21.25).
- Stability leg (M=50, seed 20260720) reproduces APPROVE; sensitivity legs
  R=8 / b₀=3 / b₀=12 / H=500 all land APPROVE with the same or near-same N*
  map — but **R=2 lands NULL under the rule** (reporting-only, cannot flip):
  at half the replenishment batch the alarm budget d/R > 0.25 makes the
  S ≤ 25 band unsatisfiable in the four hardest cells. The approval carries
  the manager-routes-R≥4-worth-of-work caveat.
