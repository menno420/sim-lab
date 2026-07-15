# verdict-079 — kill-clock anchor vs owner-gated funnel onset (INTAKE 066)

Prices idea-engine PROPOSAL 066's harvested incoherence where it lives: the
venture products lane's committed T+14 kill window is anchored at
LISTING-live while its sales evidence flows only through a funnel that goes
live on a SEPARATE, un-synchronized owner click τ days later. In the pinned
world (whole calendar days; kill window = calendar days 1..14 with the
committed ≥1-organic-sale threshold; funnel onset τ ∈ {0, 3, 7, 10, 13, 20};
pinned integer visit schedules SPIKE/BURN/DRIP quantifying the channel
table's committed adjectives; per-visit i.i.d. conversion q ∈ {1/30, 1/100,
1/300}), the evidence mass N(shape, anchor, τ) and false-kill probability
FK = (1 − q)^N are exact rationals, and three anchors are priced: A-LIST
(committed, calendar days 1..14), A-FUNNEL (funnel-days 1..14, unbounded
occupancy), A-CAP30 (funnel-anchored, hard-capped at the lane's own
committed 30-day signal window). Judged against pre-registered bands at the
decision cell (BURN, A-LIST, q = 1/100): REJECT-first (R1 FK(13) ≥ 1/2 AND
FK(0) ≤ 1/5; R2 doubling onset ≤ 13; R3 A-CAP30 exactly flat through every
grid τ ≤ 16 at occupancy ≤ 30), APPROVE (FK(13) ≤ (6/5)·FK(0) AND
FK(13) ≤ 1/4), NULL otherwise on named axes, INVALID on any F1–F6 gate
failure. Three hand-proved window theorems ride as gates: ANCHOR INVARIANCE
(funnel-anchored FK is exactly τ-invariant), SPIKE STEP (one-shot mass makes
FK a step function — all-or-nothing under the calendar anchor), CAP-30
EQUIVALENCE + BOUNDEDNESS (A-CAP30 ≡ A-FUNNEL exactly for τ ≤ 16, occupancy
bounded by the constant the lane already ships), plus MONOTONE TRUNCATION
(τ ≥ 14 is a CERTAIN false kill — the committed base case as arithmetic).
Fully hermetic: the runner reads ONLY `fixtures.json` (committed before the
runner); zero repo/network reads at verdict time.

## Run

```
python3 sims/verdict-079-kill-clock-anchor/kill_clock_anchor_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and `results.json`
are byte-identical across process runs (verified by external diff + sha256 —
see REPORT.md). Stdlib-only. Every decision number is a seedless exact
rational; the only seeded arm (R) is reporting-only with NO statistical
gate.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 066
  block / idea doc (window T = 14; cap 30; τ grid {0, 3, 7, 10, 13, 20}; the
  three shape schedules SPIKE 200·1[d=1] / BURN floor(60/d) d = 1..60 / DRIP
  2/day d = 1..365; q grid {1/30, 1/100, 1/300} with decision cell 1/100 and
  degeneracies {0, 1}; the three anchors with window predicates and
  occupancy formulas; the decision constants {1/2, 1/5, 2×-doubling ≤ 13,
  6/5, 1/4}; the F3–F5 anchors; Arm-R episodes and cells; seeds
  20261580–583; the four harvested sentences with the FIRSTHAND pin 520bdfc
  and the lived launch's two timestamps), plus fixture-level conventions
  C1–C11 and the drafter's disclosed landing (compared, never gated) —
  committed BEFORE the runner existed.
- `kill_clock_anchor_sim.py` — three-arm runner: Arm A seedless
  exact-Fraction schedule sums over the full grid (decision-bearing), Arm B
  independently-written literal calendar day-walk simulator (exact-equal on
  every published number; second decision evaluator), Arm R seeded Bernoulli
  visit traces (reporting-only).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, FK tables, theorem verifications, gates, anomalies,
  reporting legs, boundaries, the pre-registered consequence.

## Ruling

See REPORT.md (written from the accepted run; the ruling token is issued by
the twin evaluators per the pre-registered order REJECT → INVALID → APPROVE
→ NULL).
