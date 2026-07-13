# VERDICT 054 — Brineward band-2 necessity (idea-engine PROPOSAL 043)

**Ruling: APPROVE** — per the pre-registered rules applied in order, REJECT
checked FIRST. "Band-2 runs are necessary AND greed has a shape": NEC(cell) ≥
3/2 in **7 of 9** cells (band ≥ 7; REJECT's NEC < 5/4 fires in **0 of 9**),
the central cell's argmax is **GRIND-H(2,1)** (a GRIND-H variant — the
registered interior answer), and the seed-20261310 stability leg reproduces
the ruling class through both twin evaluators.

Serves `## PROPOSAL 043 · 2026-07-13T19:11:37Z · status: sim-ready`
(idea-engine control/outbox.md @ ea3744d, PR #337; claim PR #338). Committed
game tables quoted verbatim @ gba-homebrew
`8bac80a70c82096828663d501af5f2790acbccc4`.

## The decision table (Arm A, exact rationals — alone decision-bearing)

NEC = G*(all 18) / G*(b ≤ 1); NEC0 = G*(all 18) / G*(b = 0).

| cell | NEC (exact) | NEC ≈ | NEC0 ≈ | argmax | G* ≈ | T180 ≈ |
|---|---|---|---|---|---|---|
| D0=20/Td=1/2 | 63713/28400 | 2.2434 | 4.0111 | GRIND(2,1) | 31.6875 | 5.68 |
| D0=20/Td=1 | 74529/35500 | 2.0994 | 3.8506 | GRIND(2,1) | 25.3500 | 7.10 |
| D0=20/Td=2 | 206346143/97021500 | 2.1268 | 4.0292 | GRIND-H(2,2) | 19.9038 | 9.04 |
| D0=35/Td=1/2 | 164385/95764 | 1.7166 | 3.1739 | GRIND-H(2,1) | 16.4526 | 10.94 |
| D0=35/Td=1 (central) | 204849/114632 | 1.7870 | 3.1115 | GRIND-H(2,1) | 13.7446 | 13.10 |
| D0=35/Td=2 | 370305/196294 | 1.8865 | 3.1516 | GRIND(2,1) | 10.7449 | 16.75 |
| D0=50/Td=1/2 | 801325/605988 | 1.3223 | 2.7005 | GRIND-H(2,1) | 9.3204 | 19.31 |
| D0=50/Td=1 | 990269/719820 | 1.3757 | 2.5250 | GRIND-H(2,1) | 7.8465 | 22.94 |
| D0=50/Td=2 | 943193/581436 | 1.6222 | 2.5843 | GRIND(2,1) | 6.6967 | 26.88 |

7 cells ≥ 3/2; the two D0=50 low-T_dock cells sit **between the bands**
(1.3223 / 1.3757 — above 5/4, below 3/2); zero cells below 5/4 anywhere. The
argmax band is **2 in every cell** and every argmax is m = 1 or a hull-aware
variant — the measured greed dial: at honest duel risk you bank after (nearly)
every deep fight. The central-cell m-curve (band 2, GRIND-H): 13.74 / 11.11 /
9.83 for m = 1/2/3 — "one more fight" is measurably worse than "turn for
home", which is doc line 2's number. Doc line 1's number is the measured NEC
floor: the best shallow-restricted route to ANY banked-gold target (including
the committed 180g ladder) is ≥ 1.32× slower everywhere on the grid, ≥ 1.5×
slower in 7 of 9 cells (vs band-0-only: 2.5–4.0× slower). Hold-cap waste at
the argmax: 0 everywhere (the cap never binds at the optimum — m* is too
small); per-segment sink probabilities at the argmax run 0 → 5/8 across the
risk axis, the honest price the deeps still pay for their rate.

## Mechanism (read off the exact table)

A band-2 crate is worth 5× a band-0 crate and the committed damage ratio is
only 9/4, so the deep rate survives even sink-heavy play: at the central cell
the best band-2 policy banks 75g-per-won-water against a 3/8 per-water sink
risk plus descent losses, and still runs 1.79× the best band-1 rate
(GRIND(1,1) = 7.69). The greed dial's interior answer is carried by the
hull-aware trigger (GRIND-H's mid-descent bank), not by longer loops — larger
m only stacks forfeit risk on an already-full pier detour.

## Gates — all green (1484 self-checks, 0 failed, exit 0)

- **F1** ladder identity (15 + 45) × 3 = 180 from the committed `BW_UP_COST`.
- **F2** hold arithmetic exact: descent bank 51g; band-2 m=1 bank 75g; m=3
  bank 200g + exactly one 25g crate wasted (cap 8).
- **F3** zero-damage fixture cell (D0=0, T_dock=1, not in the grid):
  G(GRIND(2,2)) = 75/2, G(GRIND(1,2)) = 18, NEC = 25/12 — exact hand values.
- **F4** damage-pmf mean identity: mean = D_b exactly, every band, every axis
  point, both supports (5-point and 7-point).
- **F5** exact monotonicity: G non-increasing in D0 (all 18 policies × 3
  T_dock, exact); NEC ≥ 1 (class nesting); per-segment sink probability
  non-decreasing in m and in band (all cells, both GRIND and GRIND-H).
- **F6** repair identities: h=1 → 1g, h=48 → 12g, zero-damage segment pays 0.
- Zero-sink branch reachability asserted: D0=20 band 2 m=1 has q = 0 exactly
  (2·45 = 90 < 100) and rides the pure-loop-rate closed form.
- Twin decision evaluators (A: Fraction comprehension; B: pure-integer
  cross-multiplication with independently re-derived argmax) agree on Arm A
  and on the stability leg.
- Draw-count sentinels exact: main 16,200,000 / stability 3,240,000 /
  sensitivity 17,280,000; aux seed 20261312 ZERO draws.

## Arms

- **Arm A** (decision): seedless exact `fractions.Fraction` renewal-reward
  over the sink-to-sink cycle (descent enumeration ≤ 25 paths, loop segments
  ≤ 125/343 paths, geometric composition in closed form).
- **Arm S main** (seed 20261309, 100,000 waters per (cell, policy) leg, one
  damage draw per water): **all 162 legs pass the registered 1/50 gate**,
  worst |G_S − G_A|/G_A = 0.019096.
- **Stability** (seed 20261310, 20,000 waters, widened gate 1/20): class
  APPROVE-CELLS through both twin evaluators — per-cell NEC 2.25 / 2.10 /
  2.12 / 1.72 / 1.79 / 1.88 / 1.34 / 1.38 / 1.61 (same 7-high/2-mid split,
  argmax band 2 everywhere). One widened-gate breach on a decision-irrelevant
  leg: GRIND(1,3) @ D0=50/Td=2, rel 0.050620 vs 1/20 (1.9 SE at that leg's
  exact predicted SE — see the headroom defect below). **Dual-reading
  disclosure:** the registered APPROVE conjunct is class reproduction
  (proposal verbatim: "the seed-20261310 stability leg reproduces the
  ruling"), which holds → APPROVE; under a stricter breach-denies reading the
  class would be NULL(margin-thin). Both readings are committed in
  results.json; the ruling rides the registered text.
- **Sensitivity** (seed 20261311, 20,000 waters, reporting-only — never
  flips): rulings t_hull_proportional APPROVE-CELLS / support_7pt NULL-CELLS
  / m_4 APPROVE-CELLS / theta_30 APPROVE-CELLS / theta_70 APPROVE-CELLS /
  restart_T_dock NULL-CELLS. **Sensitivity straddle named (registered
  reporting axis): support_7pt and restart_T_dock** — both drop D0=50 cells
  below 3/2 without ever approaching the REJECT band; the APPROVE is
  risk-axis-edged at D0=50, exactly where the NULL probe's bench measurement
  of D0 would bite. Five sensitivity-leg gate breaches (worst rel 0.0621),
  all on low-G legs predicted by the headroom defect, all reported anomalies.

## Registration defect, disclosed (first-class anomaly)

The registration claims the 1/50 main gate was "pre-checked ≥ 4 SE headroom
at the pinned leg length". The exact renewal-reward variance from the Arm-A
enumeration shows this is FALSE: 68 of 162 main legs sit below 4 SE (worst
1.66 SE, D0=50/Td=2 GRIND(1,3)) — the relative gate is narrow in absolute
terms exactly where G is small. Direction: a headroom shortfall risks a FALSE
breach of the confirmation gate, never a wrong decision number (Arm A exact
rationals alone are decision-bearing). The main leg nonetheless passed all
162 gates; the observed stability/sensitivity breaches are this defect
surfacing at the shorter widened legs, as the arithmetic predicts.

## Robustness

Nothing sits on the REJECT side of any band: 0 of 9 cells below 5/4 (nearest
cell 1.3223, 5.8% above the REJECT band). The APPROVE count conjunct has zero
slack (exactly 7 of 9) — but the 7th-lowest high cell (D0=50/Td=2, 1.6222)
clears 3/2 by 8.1%, the central argmax condition is not knife-edge (GRIND-H
carries 5 of 9 argmaxes), and the stability leg reproduces the same
7-high/2-mid split cell-for-cell. The named honest limit: the two mid cells
and both sensitivity straddles live on the D0=50 edge of the invented risk
axis — the pre-registered probe (bands-*-keys.txt recorded routes +
bw_telemetry headless replays) converts D0 and t_b to bench numbers.

## Reproducibility

One command, no flags, stdlib-only, hermetic (reads only its own
fixtures.json), no wall-clock in any output. CPython 3.11 pinned and
asserted. Run TWICE as full processes, compared by external diff —
byte-identical both times:

- results.json sha256 (run 1) `049adec71d0a500f85f3e80c4af521d0d29519af14f74ab034af1cfe87b1f939`
- results.json sha256 (run 2) `049adec71d0a500f85f3e80c4af521d0d29519af14f74ab034af1cfe87b1f939` (identical)
- run-stdout.txt sha256 (run 1) `32d077e970d11f46704adff5ee206968d3f49db9499d021a5e492ca5cad82311`
- run-stdout.txt sha256 (run 2) `32d077e970d11f46704adff5ee206968d3f49db9499d021a5e492ca5cad82311` (identical)

~8 s/run. Seeds 20261309–312 strictly above the V053 registry high-water
20261308 — new registry high-water **20261312**.

## Boundaries (each with its direction, per the registration)

- **Invented constants**: D0 and T_dock carry no bench measurement anywhere
  in the fleet — the sweeps bracket scale; the band SCALING of D_b is
  committed-derived ({1, 15/8, 9/4} from rakes-to-kill × enemy reload). The
  named probe converts both to measurements.
- **Hazard omission**: Maw bites/crates, reefs {0, 3, 5}, per-band weather
  are out of the model — omissions flatter band 2, GENEROUS TO APPROVE, so
  this APPROVE must be read net of that direction (a REJECT would have been
  robust to it; the APPROVE is not automatically).
- **Bounded play**: mid-duel flight is approximated only by GRIND-H's
  segment-level trigger — direction: deep-band viability is a lower bound in
  that one respect (strengthens APPROVE).
- **Tier-0**: upgrades are the TARGET, never a lever — the doc's claim is
  about reaching the ladder.
