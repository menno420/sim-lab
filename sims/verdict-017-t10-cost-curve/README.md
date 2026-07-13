# verdict-017 · t10-cost-curve

Generator-purchase cost-curve sweep for superbot-idle's pre-registered T10
target. Answers idea-engine PROPOSAL 015 (control/outbox.md
2026-07-12T23:08:19Z, idea
`ideas/superbot-idle/generator-purchase-path-t10-2026-07-12.md` @ `18778ff`,
landed via idea-engine PR #277): driving the real `idle_engine/` byte-copied
at superbot-idle `c753bc8` (reference world extended to two generator specs,
neutral theme pct, the seven VERDICT 006-graduated parameters held pinned),
which (tier-2 base cost C2 ∈ {300, 600, 900, 1800} seconds-of-tier-1-output ×
tier-2 base_rate R2 ∈ {5, 10, 25} × per-count cost growth g ∈ {110/100,
115/100, 120/100}) cells hit the pre-registered T10 band
(time-to-second-generator-tier 15–45 min active, target 30) under the SIM-001
S2/S3 policies extended with a committed greedy buy rule — while keeping all
ten SIM-001 criteria A1–A10 in PASS state with the purchase path present
(baseline leg first, isolating the milestone/theme-fold engine drift since
the `f11c71a` verdicted pin), measurably lowering VERDICT 006's flagged
3-in-4 early-inert-purchase floor, and reporting `owned` milestone rung
arrivals (10/100/1,000) per player profile?

## Run (one command)

```
python3 sims/verdict-017-t10-cost-curve/t10_cost_curve_sim.py
```

Exit 0 iff all 201 self-checks pass. Deterministic — NO RNG anywhere, no
network, no git, no wall clock at run time; the engine is a sha256-manifest-
pinned byte copy and every grid/policy input is committed (`grid.json`).
stdout and `results.json` are byte-identical across process runs (verified
by external `diff` of two complete runs, plus an in-process re-evaluation of
a committed 6-cell subset and both baselines). Runtime ~4 minutes (the grid
is 36 cells × 3 mechanic shapes × 7 scenario legs, all driven through the
real engine).

## Files

- `t10_cost_curve_sim.py` — stdlib-only driver: baseline legs B0/B1, the
  36-cell committed grid, two disclosed diagnostic shape legs (D1/D2), the
  committed greedy buy rule, SIM-001's A1–A10 re-scored dual-read
  (LITERAL/INTENT), T10 under S3/S3g/S2(N), early-inert fractions,
  owned-rung arrivals, mechanical winner rule, 201 self-checks.
- `fixtures/idle_engine/` — the VENDORED pinned engine: byte-for-byte and
  COMPLETE (all 11 modules, `__init__.py` included, unmodified) from
  `menno420/superbot-idle` @ `c753bc8f5ace96e4632510f43b53f0ee45e2def5`.
  The driver loads only the six economy-surface modules through a synthetic
  package anchor so the byte-identical `__init__.py` (which imports
  `theme` → non-stdlib `yaml`, outside the SIM-001 economy surface) is never
  executed — the VERDICT 006 accommodation, strengthened (006 reconstructed
  the init; here no vendored byte differs).
- `fixtures/MANIFEST.json` — pin commit + per-file sha256 of every copied
  file; re-verified by self-checks before the engine is imported.
- `grid.json` — the committed inputs: the 36-cell grid, the held-pinned
  graduated parameters, the candidate mechanic's cost-curve family and
  driver-level purchase semantics, the committed greedy buy rule (myopic
  primary + S3g saving variant), the diagnostic shape definitions, scoring
  and the mechanical winner rule.
- `results.json` — committed run output: both baselines, all 36 cells ×
  3 shapes with full dual scorecards, summary, winner/reshape-winner.
- `REPORT.md` — the finalizable verdict report (validity gate + paste-ready
  VERDICT 017 outbox entry).

## Verdict (summary — full report in REPORT.md)

**conditional** — the committed count-stacking shape is REJECTED at every
cell, and the unlock-only reshape passes at exactly one (C2, R2):

- **Committed shape (greedy buy set {upgrade, tier-1 copy, tier-2 copy},
  tier-1 copies at the 60 s cost anchor): 0/36.** Every cell breaks A3 AND
  A6 catastrophically (S3 first-prestige collapses from the verdicted
  3.49 h to 8.4–16.2 **minutes**; A6 = 103–200× vs its 4–12× band) and
  every cell's T10 (5.8–10.9 min) undershoots the 15-min band floor. The
  count-purchase feedback loop — cost `60·g^n` growing slower than
  count-multiplied income — is the runaway; the swept tier-2 knobs never
  bind. Diagnostic D1 (tier-1 copy path removed) still fails 36/36 on
  A3/A6: tier-2 copy-stacking runs away the same way the moment any
  count-purchase loop exists at g ≤ 1.2.
- **Diagnostic D2 (unlock-only: buying the second generator TIER is a
  one-off unlock — T10's registered wording — no count-stacking): the
  (C2=900, R2=5) column passes 10/10 on BOTH scorecard readings with T10
  = 1948 s ≈ 32.5 min** (target 30; S3g and S2(0.25 h) land on the 900-s
  band floor — policy-robust). A6 = 11.74 sits near its 12× edge —
  disclosed. The g axis is INERT in this shape (no repeat generator
  purchase exists), so **g must not be registered from this sweep**.
- Band-edge cells marked: C2=300 (T10 940 s, 40 s above the floor),
  C2=600|R2=5 (A6 = 12.04, misses by 0.04×), C2=1800|R2=5 (10/10 but T10
  3081 s, 381 s past the ceiling).
- Baseline legs: B0 (milestones off) reproduces VERDICT 006's published
  numbers EXACTLY (self-checked: 60 s / 12573 s / 21600 s / 1215-s gap /
  awards all 1); B1 (milestone+theme fold, the real HEAD engine) scores
  10/10 — the engine drift since `f11c71a` does NOT break any registered
  band (A3 12134 s, −3.5%), and the achievements doc's lifetime-2 ↔
  first-prestige double-hit lands as designed.
- Findings routed to the lane: the `owned` milestone ladder (10/100/1,000)
  and pacing-compatible generator purchases are mutually exclusive as
  registered — in the passing shape total owned maxes at 2 (all owned
  rungs unreachable); in the rejected stacking shapes rung 1 arrives in
  ~5–7 min but T3/T6 die. The early-inert floor (9/12) is NOT relieved by
  the passing shape (VERDICT 006's base_rate follow-up stays open); the
  stacking shapes relieved it (2–7%) but broke pacing.
