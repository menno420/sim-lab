# VERDICT 051 — Schelling segregation tipping at τ = 3/10: APPROVE

> **Source:** idea-engine `control/outbox.md` → PROPOSAL 040 ·
> 2026-07-13T17:19:39Z · status: sim-ready (the source of truth; idea doc
> `ideas/fleet/schelling-mild-preference-tipping-2026-07-13.md` @ idea-engine
> main 25b1798). INTAKE 040 → VERDICT 051 per the docs/current-state.md
> offset map (+11 from PROPOSAL 035 onward).
> **Run:** `python3 sims/verdict-051-schelling-tipping/schelling_sim.py` —
> stdlib-only, hermetic (reads only its own `fixtures.json`), exit 0, ~17 s,
> `SELF-CHECKS: 32 passed, 0 failed`; stdout + `results.json` byte-identical
> across two full process runs by external diff; cpython-3.11 pinned and
> asserted. Accepted run = the first complete run of the registered pipeline
> (no fix-forwards).

## The question (registered before any code)

Under the pinned conservative Schelling frame — 40×40 Moore-8 TORUS, exactly
720 type-A / 720 type-B / 160 vacant (45/45/10), satisfaction = like-fraction
among OCCUPIED neighbors ≥ τ tested in exact integers (`like·τ_den ≥
τ_num·occ`, zero occupied neighbors ⇒ SATISFIED), live random-serial sweeps,
an unsatisfied agent relocating to a UNIFORMLY RANDOM vacant cell, fixation
(a zero-relocation sweep, independently re-certified) or cap 500 — what is
the MEDIAN terminal mean like-neighbor share s(τ = 3/10) over M = 32
seed-20261297 runs, and does it land REJECT (< 11/20, checked FIRST) /
APPROVE (≥ 7/10 AND seed-20261298 stability reproduction) / NULL, both bands
carrying the validity conjunct "fewer than 1/4 of the 32 decision-cell runs
cap-censored"?

## Ruling: APPROVE — "mild preference, strong segregation"

Applied in the pre-registered order:

1. **REJECT (checked FIRST): does not fire.** Median s(3/10) =
   **90871/120960 ≈ 0.751248** — not < 11/20 = 0.55. Validity conjunct
   PASS (0/32 runs cap-censored; every decision-cell run fixated, median 12
   sweeps, max 25).
2. **APPROVE: fires.** Median 90871/120960 ≥ 7/10 exactly (0.7512 ≥ 0.70),
   AND the seed-20261298 stability leg (M = 16, fresh generator) reproduces
   the same ruling under the identical rule: its median s = 21511/28800 ≈
   0.746910 ≥ 7/10 with its own validity conjunct passing (0/16
   cap-censored). Twin independently-written evaluators (Fraction vs
   pure-integer cross-multiplication) agree.

**An agent content as a 30% local minority ends up in a ≈ 75%
like-neighborhood — two and a half times its demand — under dynamics
deliberately tilted AGAINST amplification** (uniform-random destinations, a
thin 10% vacancy pool, live serial updating, vacuous satisfaction for
isolated agents). The pre-registered APPROVE consequence applies: the
emergence parable earns a measured, conservative citation pin — fleet prose
invoking emergent segregation cites the measured s(τ) curve below, not the
folklore.

## The measured s(τ) response curve (main leg, seed 20261297, M = 32 per cell)

| τ | median s | mean s | mean interface density | cap-hits | sweeps-to-fixation q1/med/q3 |
|---|----------|--------|------------------------|----------|------------------------------|
| 1/8 | 27497/53760 ≈ 0.5115 | 0.5112 | 0.4909 | 0/32 | 2/2/3 |
| 1/4 | 1381999/2419200 ≈ 0.5713 | 0.5721 | 0.4370 | 0/32 | 5/6/7 |
| **3/10** | **90871/120960 ≈ 0.7512** | 0.7485 | 0.2567 | **0/32** | 11/12/15 — **decision cell** |
| 3/8 | 462089/604800 ≈ 0.7640 | 0.7647 | 0.2413 | 0/32 | 11/12/13 |
| 1/2 | 1049317/1209600 ≈ 0.8675 | 0.8687 | 0.1306 | 0/32 | 14/16/18 |
| 5/8 | 1182991/1209600 ≈ 0.9780 | 0.9773 | 0.0180 | 0/32 | 59/69/83 |
| 3/4 | 4301/4320 ≈ 0.9956 | 0.9955 | 0.0030 | 0/32 | 109/130/163 |

The curve's shape is the finding: a sharp rise between τ = 1/4 (s ≈ 0.57)
and τ = 3/10 (s ≈ 0.75) — the tipping knee sits exactly at the showcase
threshold — then a slower climb to near-total sorting at high τ. Every one
of the 320 runs across all legs FIXATED (zero cap hits anywhere, even at
τ = 3/4); the four pre-registered NULL shapes all stayed empty.
Monotonicity audit (reporting): mean s(τ) non-decreasing across
{1/8 … 1/2} — OK, no anomaly. Decision-cell per-run s range:
0.7143–0.7779 (all 32 runs individually ≥ 7/10). Terminal satisfied
fraction = 1 in every fixated run (fixation certified independently).

## Control, stability, and sensitivity legs

- **τ = 0 control (main seed, M = 32):** EXACTLY zero relocations; every
  run's initial-placement s inside [47/100, 53/100] (measured range
  0.4837–0.5115; mean interface density 0.4998) — the well-mixed baseline
  anchoring the REJECT band's "near baseline" reading is measured, not
  assumed. The τ = 3/10 landing (0.7512) sits ≈ 25 points above it.
- **Stability (seed 20261298, M = 16):** median 0.7469, 0/16 capped —
  reproduces APPROVE.
- **Vacancy pair (seed 20261299, M = 16 each, reporting-only):** vacancy
  1/20 (760/760/80) median s = 50597/67200 ≈ 0.7529; vacancy 1/5
  (640/640/320) median s = 99061/134400 ≈ 0.7371. Both on the SAME side of
  both band edges — **no vacancy-sensitivity flip**; the result is not an
  artifact of the 10% vacancy choice within the swept bracket.
- **Grid N = 25 (281/281/63):** median s = 125/168 ≈ 0.7440 — the finding
  survives the smaller grid.
- **Aux seed 20261300:** reserved, zero draws (the pre-priced NULL probe was
  never needed — no run capped).

## Gates (all green — 32 self-checks, 0 failed)

4×4 hand fixture verified by the engine AND by the independently written
satisfaction scan (16 hand-computed occ/like cells, wrap + neighborhood
arithmetic); τ = 0 zero-move identity + baseline band; per-sweep
conservation 720/720/160 recounted at every one of 9,315 sweep ends (0
violations); every one of 320 fixations independently re-certified (0
unsatisfied found); ascending-vacancy-list invariant (0 violations);
draw-count sentinels exact per leg (control 64 shuffles / 0 randranges;
main 8,684 / 1,100,095 — randranges ≡ relocations, shuffles ≡ runs +
sweeps; stability 205 / 9,243; reporting 682 / 21,430; aux 0); twin
decision evaluators agree; median = mean of the 16th/17th order statistics
recomputed; stdout + results.json byte-identical across two process runs by
external diff.

## Boundaries (registered)

- **Family of dynamics:** results rule on THIS update rule/grid/composition
  only — live random-serial order, uniform-random vacant destinations,
  40×40 Moore-8 torus, 45/45/10. The satisfying-destination flip (movers
  relocate only where satisfied) is the named most-likely-to-flip follow-up
  with the entire engine reusable; graded utilities, unequal groups, von
  Neumann neighborhoods, open boundaries, noise/swap dynamics all out of
  scope.
- **Termination:** s measured at fixation (all 320 runs) or cap; the
  validity conjunct handled cap-censoring — it never bound (0 caps).
- **Measurement:** s is a LOCAL mixing metric; "strong segregation" is
  operationalized as s ≥ 7/10 on this metric. Global cluster structure
  rides reporting-only as interface density (0.4998 well-mixed → 0.2567 at
  the decision cell → 0.0030 at τ = 3/4).

## What a reader does differently

The tipping story may be cited WITH its measured, conservative pin: even
uniform-relocation dynamics with 10% vacancies turn a 0.30 demand into
≈ 0.75 like-neighborhoods (median over 32 registered-seed runs, exact
rational 90871/120960, stability-reproduced). Any fleet prose invoking
"emergent segregation" should cite s(0.30) ≈ 0.75 and the s(τ) curve above
— including its honest complement: at τ = 1/8 the outcome (0.51) is
statistically indistinguishable from the mixed baseline, so the parable's
force lives in the 1/4 → 3/10 knee, not in "any preference segregates".
