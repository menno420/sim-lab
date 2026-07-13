# verdict-023 · renumber-treadmill

Is the shipped Option-1 migration-collision checker ENOUGH, or must the shared
append point go? Answers idea-engine PROPOSAL 021 (control/outbox.md
2026-07-13T02:36:37Z, idea
`ideas/superbot/migration-renumber-treadmill-residual-2026-07-13.md`, landed
via idea-engine PR #287, main `8022a9d`) — the ORDER 004 rule-3 FLEET-BACKLOGS
rotation slot, round 2, harvested from the superbot backlog's captured
migration-number-collision-guard doc (@ `fd638e3`, byte-same at live
`4522522`; the recorded incident: PR #1279, renumbered four times in one
afternoon). Fully hermetic per the PROPOSAL 017/018/019/020 precedent: every
fixture is a pinned constant committed with the sim, zero repo/network reads
in the verdict session. Under the pinned endogenous migration-race model
(PRs arrive Poisson λ ∈ {1, 4, 12}/day, develop W = 8 h, validate
V ∈ {0.25, 2, 24} h, fix latency d = 0.5 h; collision at merge-attempt iff
the held number was merged by another PR since pick; policies by pick time —
P0 at open + each fix start, P1 re-pick at every push (the shipped checker's
semantics), P3 assign-at-merge (must measure exactly zero collisions)), what
are R = renumbers per merged PR and T = share of merged PRs with ≥ 2
renumbers per endogenous (λ, V) cell under P1 — landing APPROVE / REJECT /
NULL per the decision rule registered in the idea file before any code
existed?

## Run (one command)

```
python3 sims/verdict-023-renumber-treadmill/renumber_treadmill_sim.py
```

Exit 0 iff all 16,857 self-checks pass (including the validation gate:
exogenous Arm S within 1.0 pp of the exact Arm A closed forms on every
covered cell, and endogenous P3 exactly zero collisions). Deterministic — the
only randomness is `random.Random(<pinned seed>)` consumed in the pinned loop
order (cells lexicographic λ then V ascending, policy P0/P1/P3, replications
sequential; per rep the only base draws are the Poisson arrival gaps), no
network, no git, no wall clock, no `hash()`. stdout and `results.json` are
byte-identical across process runs (verified by external `diff` + `cmp` of
two complete runs, cpython-3.11). Runtime ~58 s.

## Files

- `renumber_treadmill_sim.py` — stdlib-only driver: the continuous-time event
  engine (event queue ordered by (time, PR id); pick = max(main)+1; collision
  iff held ≤ max(main) at attempt; main stays contiguous by construction —
  checked), the full 9-cell × 3-policy endogenous grid at M=40 (primary, seed
  20260723), Arm A exact closed forms (seedless, each computed twice by
  independent float paths), the exogenous gate leg (M=20,000 focal PRs per
  cell × {P0, P1}, seed 20260726), the M=8 seed-20260724 decision-stability
  leg, four reporting-only sensitivity legs (d ∈ {0.25, 2}, W ∈ {1, 24} at
  M=8), the seed-20260725 jitter leg (W/V/d redrawn exponentially at the
  pinned means), the #1279 anchor leg, the exact-Fraction decision rule
  evaluated in the pre-registered order APPROVE → REJECT → NULL, and the
  self-checks (per-replication contiguity/conservation invariants, P3
  zero-collision control on every endogenous leg, an independent no-heap
  replay re-implementation with SET-membership collision testing and an
  interval-sweep holder recount, hand-derived pins, draw-count accounting,
  fixture cross-checks, twin decision evaluators).
- `fixtures.json` — the pre-registration, committed BEFORE the runner: all
  constants verbatim from the idea file ({λ-grid, V-grid, W, d, H, warm-up,
  M per leg, seeds 20260723–26, band constants, per-policy pick-time
  definitions}), the pinned event/draw/loop order, the decision rule +
  evaluation order + consequences + boundaries, two hand-derived pin
  scenarios with full derivations, and the disclosed intake-time decisions
  (sensitivity/jitter M=8 — the idea file leaves their M unpinned; the
  exogenous two-round truncation; the jitter redraw granularity; the warm-up
  population and p95 conventions). One post-runner amendment, disclosed
  in-place: HAND-1's expected duration sum carried a hand-arithmetic slip
  (10 + 12.5 written as 23.5), corrected to 22.5 after the engine and the
  independent replay both computed 22.5; no decision constant was touched.
- `results.json` — committed run output: the full {R, T, latency inflation,
  amplification ratio, max holders} × (cell, policy) table for every leg,
  Arm A and the exogenous gate tables, the anchor block, decision detail per
  leg, self-check counts, cpython pin.
- `REPORT.md` — the finalizable verdict report (validity gate + the VERDICT
  023 ruling).

## Verdict (summary — full report in REPORT.md)

**reject (pre-registered)** — the shared append point must go; the Option-3
assign-at-merge build gets its evidence row:

- **APPROVE fails first (checked first):** R ≤ 0.10 AND T ≤ 0.01 in only
  **2/9** endogenous P1 cells (the two V=0.25 fast-lane cells at λ ≤ 4/day)
  vs the ≥ 8 bar. The shipped checker's residual is NOT negligible
  fleet-wide.
- **REJECT binds:** T > 0.05 in **5/9 cells** (bar: ≥ 5) — and membership is
  margin-heavy and stable: the five cells run T = 0.133–0.870 (2.7×–17× the
  band), the nearest non-member sits at T = 0.021 (42% of the band), and the
  SAME five-cell set reproduces in all seven legs (stability, jitter, every
  sensitivity leg).
- **The headline deliverable — endogenous amplification:** R_endo/E[N]_ArmA
  ranges 0.96–**25.8** across P1 cells. At (λ=12/day, V=2) the closed form
  prices E[N] = 1.72 renumbers/PR; the coupled system measures R = 44.4 —
  renumber storms feed the collision pressure that causes them. At the
  saturated V=24 high-λ cells the ratio collapses (0.35 → 0.0001): the
  treadmill destabilizes the system, merge throughput falls below λ, and the
  exogenous form (which assumes appends keep arriving at λ) overprices the
  pressure it can no longer sustain.
- **Latency tax (rides to the Option-3 plan):** mean open→merge inflation vs
  P3 up to **15.4×** (493.6 h vs 32 h at λ=4/day, V=24), p95 up to 44×; max
  simultaneous holders of one number up to 967.
- **#1279 anchor (plausibility, never a fit):** Arm A at (λ=12/day, V=2,
  P0) gives E[N] = 3.47, P(N≥3) = 0.51, P(N≥4) = 0.36 — the recorded
  four-renumber afternoon sits comfortably inside the model's mass; the
  endogenous measurement at that cell is far worse (R = 88.5).
- **Validation gate PASS:** exogenous Arm S max |dev| = 0.684 pp vs the 1.0 pp
  gate over all 36 comparisons; endogenous P3 measured exactly zero
  collisions on every leg (per-replication checks).
- Stability leg (M=8, seed 20260724) reproduces REJECT with the identical
  reject set. Boundaries: P1's residual is a FLOOR (uniform compliance) — a
  REJECT is the conservative direction; Poisson arrivals (endogenous bunching
  generated by the mechanism itself; exogenous bursts out of scope).
