# REPORT — VERDICT 061: kill-clock horizon (PROPOSAL 050)

**Ruling: NULL** (registered rules applied in order, margin m = 1/20 exact —
REJECT checked FIRST does NOT fire: 1 over-margin cell vs the 7 required;
APPROVE arithmetic FIRES on Arm A's exact numbers (8 of 9 cells under
margin, 3 of 3 SKEPTIC) BUT its registered stability conjunct fails — the
seed-20261338 twin-evaluator re-evaluation on the 20,000-trajectory table
lands over = 3 / under = 6, so the ruling falls to NULL per "anything
else". **Named axis: (iii) margin-thin**, the registered candidate — the
ruling flips inside the registered sweep (m = 1/50 → NULL_ARITH) and the
exact arithmetic flip boundary is m\* = D(SKEPTIC/B=2) = 0.043963…
(212-digit exact rational committed in results.json): APPROVE's arithmetic
holds for every margin m > m\* and fails at or below it. The two disclosed
near-edge cells (SKEPTIC/B=2 at D = 0.043963, HOPEFUL/B=10 at D = 0.048155)
sit 0.0060 and 0.0018 under the 1/20 edge — inside MC noise at N = 20,000
(4·SE up to 0.041) — which is exactly why the stability leg cannot
reproduce the arithmetic class. This is the registration's own disclosed
falsifiability landing: the drafter's numbers reproduce EXACTLY, and the
pre-registered confirmation machinery, applied as registered, declines to
certify the thin APPROVE.)

Registration: `## PROPOSAL 050 · 2026-07-13T23:26:05Z · status: sim-ready`
(idea-engine `control/outbox.md` @ main 3b9b26c, idea doc
`ideas/venture-lab/kill-clock-horizon-2026-07-13.md`). Fully hermetic; the
harvested kill-clock family rides the double pin venture-lab `be6c75d` via
idea-engine outbox `763b19e`, secondhand status carried in fixtures.json.

## The question and the model (registered, hermetic)

One experimental product slot, H = 90 whole slot-days. Each launched
product draws a true per-day organic-sale probability p i.i.d. from the
cell prior over P = {0, 1/60, 1/30, 1/14, 1/7}; priors SKEPTIC
(3/4, 1/10, 3/40, 1/20, 1/40) / NEUTRAL (1/2, 1/8, 1/8, 1/8, 1/8) /
HOPEFUL (1/4, 1/4, 1/4, 3/20, 1/10); build downtime B ∈ {2, 5, 10}; 9
cells = prior × B. Policy KILL@T for the lane's own three committed clocks
T ∈ {7, 14, 30}: first sale on day x ≤ T → graduation (slot freed, B build
days, fresh draw); zero sales through day T → kill (B build days, fresh
draw); live-at-horizon contributes nothing. G(cell, T) = expected
graduations in H slot-days, exact. D(cell) = (max_T G − G(14)) / G(14).

## Arm A — exact Fractions (DECISION arm, seedless); the 9 × 3 G table

| cell | G(7) | G(14) | G(30) | D | dir |
|---|---|---|---|---|---|
| SKEPTIC/B=2 | 0.656410 | 0.628768 | 0.507449 | 0.043963 | SHORTER |
| SKEPTIC/B=5 | 0.506206 | 0.536226 | 0.474449 | 0 | HELD |
| SKEPTIC/B=10 | 0.370672 | 0.426550 | 0.418959 | 0 | HELD |
| NEUTRAL/B=2 | 1.877411 | 1.754739 | 1.397232 | 0.069909 | SHORTER |
| NEUTRAL/B=5 | 1.411738 | 1.467175 | 1.270487 | 0 | HELD |
| NEUTRAL/B=10 | 1.024887 | 1.154395 | 1.097574 | 0 | HELD |
| HOPEFUL/B=2 | 2.270117 | 2.261934 | 2.012794 | 0.003618 | SHORTER |
| HOPEFUL/B=5 | 1.699114 | 1.879887 | 1.803883 | 0 | HELD |
| HOPEFUL/B=10 | 1.228336 | 1.471887 | 1.542765 | 0.048155 | LONGER |

(Floats shown to 6 dp; every G and D is committed as an exact rational in
results.json. T = 30 is the argmax in exactly ONE corner — HOPEFUL/B=10 —
and beaten in the other 8 cells: the "give it the full signal window"
instinct loses almost everywhere at these widths, as the registration's
disclosed sharpening predicted.)

## Decision evaluation (registered order, twin evaluators agree everywhere)

1. **REJECT (checked FIRST): does not fire.** Over-margin cells at
   m = 1/20: 1 (NEUTRAL/B=2, D = 0.069909, SHORTER) — 7 required.
2. **APPROVE: arithmetic fires, stability conjunct FAILS.** Under-margin: 8
   of 9 (7 required) including 3 of 3 SKEPTIC (2 required). Stability leg
   (seed 20261338, N = 20,000/leg, widened agreement gate ≤ 3/50 — every
   leg passes the gate with worst |dev| 0.025335 at HOPEFUL/B=10 T=30):
   the twin evaluators on the stability G-hat table land over = 3 / under
   = 6 / skeptic_under = 2 → NULL_ARITH ≠ APPROVE_ARITH. The three
   over-margin cells on the stability table: SKEPTIC/B=2 D-hat = 0.070807,
   NEUTRAL/B=2 D-hat = 0.069896, HOPEFUL/B=10 D-hat = 0.068152.
3. **NULL fires** — named axis margin-thin (see ruling block above); the
   over-margin set across the sweep straddles directions (SHORTER at B=2,
   LONGER at HOPEFUL/B=10) and concentrates in the extreme-B columns, so
   the build-cost-conditional reading rides along: the right clock hinges
   on the build-downtime and dead-share numbers.

## Gates — all green (959 self-checks, 0 failed, exit 0)

- F1 pmf normalization exact (all three priors, both grids non-negative).
- F2 point-mass identities: p = 0 ⇒ G = 0 for every (T, B, H ∈ {90, 60,
  180}); p = 1 ⇒ G = ⌈H/(1+B)⌉, asserted equal to (30, 15, 9) at H = 90.
- F3 truncated-geometric identity exact per grid p (P and P′) and clock;
  per-launch graduation probability non-decreasing in T (per p and per
  prior).
- F4 hand world H = 6, B = 1, T = 2, p = 1/2: G = 31/16 exactly via the
  pinned chain G(1) = 1/2, G(2) = 3/4, G(3) = 1, G(4) = 11/8, G(5) = 13/8.
- F5 (a) G non-increasing in B for every (prior, T), in the main world AND
  every sensitivity world; (b) all-dead world exact zeros, kills ≡ renewals,
  kill count matching the closed form ⌊(H−T)/(T+B)⌋+1; (c) slot-day
  accounting identity graduation-days + kill-days + build-days +
  live-at-horizon-days = H exact for all 27 (cell, clock) legs.
- Twin in-process Arm-A computations (scalar DP vs independently-structured
  bookkeeping DP) identical rationals on all 27 legs.
- Twin independently-written decision evaluators (procedural-Fraction vs
  pure-integer cross-multiplication) agree on every table: Arm A
  provisional, stability, every reporting world, every margin sweep.
- Arm agreement gate: every main leg within 3/200 absolute AND 4·SE ≤
  3/200 (max 4·SE 0.013138); worst |dev| 0.005503 at HOPEFUL/B=2 T=7.
- Draw sentinels exact on every leg: daily-trial draws ≡ recorded live
  days, p-draws ≡ recorded launches; per-seed totals via the counting RNG
  wrapper — 20261337: 380,890,538 calls / 20261338: 38,085,547 / 20261339:
  162,191,295 / 20261340 (aux): 0 (constructed fourth in pinned order,
  RESERVED, never read by any decision number).
- CPython 3.11 pinned in fixtures and asserted.

## Arm S — seeded MC confirmation (seed 20261337, N = 200,000/leg, 27 legs)

All 27 legs pass |ArmS − ArmA| ≤ 3/200 with ≥ 4·SE headroom. Worst cell:
HOPEFUL/B=2 T=7, |dev| = 0.005503 (gate 0.015, 4·SE 0.013138). Full per-leg
table (sum_grads, G-hat, dev, 4·SE, draw counts) in results.json.

## Reporting-only legs (seed 20261339, N = 20,000/leg — never flip the decision)

Sensitivity worlds (Arm A exact re-evaluations, MC-confirmed on all 27 legs
each, worst devs 0.010794 / 0.021590 / 0.011271 / 0.006117):

| world | arith class | over-margin cells |
|---|---|---|
| H = 60 | APPROVE_ARITH (7 under, 2/3 SKEPTIC) | NEUTRAL/B=2 0.068583 SHORTER; SKEPTIC/B=2 0.052875 SHORTER |
| H = 180 | APPROVE_ARITH (7 under, 2/3 SKEPTIC) | NEUTRAL/B=2 0.077436 SHORTER; SKEPTIC/B=2 0.057236 SHORTER |
| grid P′ | APPROVE_ARITH (8 under, 3/3 SKEPTIC) | HOPEFUL/B=10 0.087435 LONGER |
| blocks-slot | APPROVE_ARITH (9 under, 3/3 SKEPTIC) | none |

No world flips the arithmetic class, but the near-edge cell SKEPTIC/B=2
crosses the 1/20 edge in BOTH H worlds (0.0529, 0.0572) and HOPEFUL/B=10
crosses in P′ (0.0874) — the band conjuncts genuinely live at the edge,
consistent with the margin-thin axis.

Margin sweep (Arm A exact): m = 1/50 → NULL_ARITH (over = 3: SKEPTIC/B=2
SHORTER, NEUTRAL/B=2 SHORTER, HOPEFUL/B=10 LONGER — directions straddle);
m = 1/10 → APPROVE_ARITH (9 under). Exact flip boundary m\* =
D(SKEPTIC/B=2) = 0.043963… (exact rational in results.json).

Per-cell bookkeeping (Arm A exact; kills / idle build days (post-grad +
post-kill) / live-at-horizon days / wasted graduations vs the 30-day
window), shipped clock T = 14 row shown; all 27 rows in run-stdout.txt and
exact rationals in results.json:

| cell | kills | idle days | live-at-horizon | wasted grads |
|---|---|---|---|---|
| SKEPTIC/B=2 | 4.8327 | 10.8287 | 7.5942 | 0.286399 |
| SKEPTIC/B=5 | 4.5091 | 21.9840 | 1.4824 | 0.267223 |
| SKEPTIC/B=10 | 3.5992 | 35.8836 | 1.0168 | 0.213299 |
| NEUTRAL/B=2 | 4.4130 | 12.1535 | 5.7696 | 0.599134 |
| NEUTRAL/B=5 | 3.8314 | 24.7194 | 2.9764 | 0.520181 |
| NEUTRAL/B=10 | 3.0243 | 38.6506 | 2.1976 | 0.410602 |
| HOPEFUL/B=2 | 4.1457 | 12.6099 | 5.4193 | 0.988203 |
| HOPEFUL/B=5 | 3.5366 | 25.6040 | 3.2551 | 0.843015 |
| HOPEFUL/B=10 | 2.7770 | 39.5909 | 2.4331 | 0.661963 |

(wasted graduations = graduations the kill forfeits relative to the lane's
own 30-day signal window — the fixture-pinned disambiguation of the idea
doc's "graduations the shorter clock forfeits"; exactly 0 at T = 30.)

Per-p conditional graduation split: committed exact per (cell, clock) in
results.json (grads_by_p / kills_by_p over rows 0, 1/60, 1/30, 1/14, 1/7)
and printed in run-stdout.txt — e.g. SKEPTIC/B=2 moving T 7→14 saves
mostly 1/60- and 1/30-burners (grads 0.114→0.126, 0.163→0.171) while the
1/7-burners LOSE throughput (0.170→0.136): the fast burners are better
served by faster recycling, the slow burners by patience — the two-sided
tradeoff in one row.

## Stability result (seed 20261338, N = 20,000/leg)

Widened agreement gate ≤ 3/50 passes on every leg (worst |dev| 0.025335,
max 4·SE 0.041227). The twin evaluators on the stability table land
NULL_ARITH (over = 3 / under = 6 / skeptic_under = 2) vs Arm A's
APPROVE_ARITH — the APPROVE conjunct fails, the mechanism being the two
disclosed near-edge cells plus noise (their D-hats: 0.070807 / 0.068152 vs
true 0.043963 / 0.048155).

## Drafter-reference comparison (disclosed, re-derived from scratch, NEVER gated)

All disclosed quantities reproduce exactly: D = 0 in 5 of 9 cells (match);
SKEPTIC/B=2 0.043963 SHORTER (~0.0440 disclosed); NEUTRAL/B=2 0.069909
SHORTER (~0.0699); HOPEFUL/B=2 0.003618 SHORTER (~0.0036); HOPEFUL/B=10
0.048155 LONGER (~0.0482) — 4/4 cells match to 4 dp with directions. The
drafter's EXPECTED CLASS (APPROVE thinly) does not survive its own
registered stability conjunct — no drafter arithmetic error found; the
registration's confirmation machinery is what declines the thin APPROVE.

## Reproduction

- One command, no flags: `python3 sims/verdict-061-kill-clock-horizon/kill_clock_sim.py`
- Hermetic (reads only its own fixtures.json), stdlib-only, CPython 3.11
  pinned and asserted, no wall-clock in any output.
- stdout + results.json byte-identical across two full process runs by
  external sha256:
  - run-stdout.txt `239bdb66fe79f34664a536ea5e1755ab1bcab553285da2abd896fd9ab79c4876`
  - results.json `97e9aaace6f94783943cb4c23704c73480894a8b13114fd520de97c9d2105018`
- ~3m46s per run (≈ 581M RNG calls, pure CPython).

## Limits

Model-true under the registered frame, not a market measurement. The four
registered boundaries: **stationarity** — per-day Bernoulli with no launch
spike or decay is the named most-likely-to-flip alternative; a launch-spike
world concentrates evidence early and shortens the optimal clock, so the
stationary model is GENEROUS TO LONG CLOCKS (direction stated — any future
APPROVE of T+14 against T+7 reads net of it; here the margin-thin NULL's
SHORTER-leaning cells would only strengthen). **Invented widths** — the p
grid, the three pmfs, the token→slot-day conversion behind B, and H carry
NO live datapoint anywhere in the fleet (the lane's launched products have
zero sales — the harvested evidence itself); the widths bracket scale, not
measured shape; the prior and B axes are promoted INTO the grid, and the
lane's own launch/first-sale timestamps are the named free live
measurement. **Secondhand pin** — the kill-rule text was not read directly
(the drafting-time denial is quoted verbatim in fixtures.json); the
application guard voids application on a mismatched real shape (different
clock values, non-kill T+14 semantics, a dominant reads/inbound leg) and on
any live organic sale before application (the V053 guard, inherited).
**Binary graduation** — first sale only; multi-sale value and the
reads/inbound leg are out of registered scope.
