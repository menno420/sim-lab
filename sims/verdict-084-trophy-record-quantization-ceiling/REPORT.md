# VERDICT 084 — the fishing trophy-record quantization ceiling (idea-engine PROPOSAL 071) — REPORT

## Ruling

**REJECT** (per the pre-registered rule applied in the registered order
REJECT -> INVALID -> APPROVE -> NULL, REJECT evaluated FIRST; both
independently-written decision evaluators agree REJECT/REJECT; every
decision number is an exact rational). All three REJECT clauses fire at
the decision cell (bare rod pull 1.00, level 7, shore; modal species =
rank 1 minnow, L1-gated):

- **Clause (i) — the ladder census**: the minnow's committed weight
  ladder has exactly **17 rungs** (<= 20) with ceiling probability
  **p = 2/81 ~ 0.02469 >= 1/50** — the chase provably completes in
  81/2 = **40.5 catches of the species** in expectation, i.e.
  **1527502293/10346336 ~ 147.64 casts** at the decision-cell mix
  (q1 = 5173168/18858053, H21 = 18858053/5173168) and ~ **74.25 casts**
  at the level-1 onboarding mix (q1 = 6/11).
- **Clause (ii) — the lifetime-celebration law**: the minnow's exact
  E[lifetime PBs] = **11736310749428605/3026966925030048 ~ 3.8773 <= 4**
  — fewer than four "🏅 New personal best!" events EVER, in
  expectation, for the most-caught fish in the game.
- **Clause (iii) — the cadence law**: P(PB at t) < 1/t STRICTLY for
  every t in 2..50, exact (P(PB at 2) = 3083/6561 ~ 0.46990 < 1/2;
  minimum gap 0.011986 at t = 50). The celebration cadence runs below
  the continuous benchmark the hook implicitly sells from every
  species' second catch on.

APPROVE was mutually exclusive by arithmetic and its world was
genuinely live: the one-character `round(., 3)` re-census lands BOTH
APPROVE bands (below), so the run was never theater.

## The three structure theorems — verified as gates

- **T1 — atom census (G2)**: per-rank probabilities sum to exactly 1,
  all 21 ranks; the |A| table verbatim — 17, 52, 99, 160, 232, 312,
  402, 502, 610, 724, 848, 978, 1117, 1262, 1413, 1572, 1737, 1910,
  2088, 2272, 2462; the rank-1 atom law exact (0.12 @ 4/81, fifteen
  atoms 0.13..0.27 @ 5/81, 0.28 @ 2/81); atoms consecutive on the
  0.01 grid; the pinned nominals reproduce
  `round(0.18 x r^1.65, 2)` exactly.
- **T2 — reachable ceiling (G3)**: p_ceiling(1) = 2/81 exactly; the
  kill-cast identity 1/(q1 x 2/81) = 1527502293/10346336 verified with
  H21 = 18858053/5173168; every rank's top atom strictly positive.
- **T3 — terminating-record law (G4)**: E_life(1) exact as disclosed;
  the geometric-series identity holds (partial sums of P(PB at t)
  monotone non-decreasing, E_life − E[PBs in 1000] < 1/1000, exact);
  P(PB at t) < 1/t strict for t in 2..50; E[PBs in n] <= min(H_n,
  E_life) for n in 1..1000 (exact).
- **L1 — modal invariance (G6)**: the committed float mix weights
  `1.0 / (rank ** (1.0 / pull))` are strictly decreasing in rank at
  every committed rod pull x weather cell (pulls 1.00/1.10/1.25/1.45/
  1.70, weather 1.0/1.08/1.12/1.30, weather multiplying the pull) and
  every level band (3 x level, clamped) contains rank 1 — the minnow
  is the modal catch at every committed cell; no committed knob can
  add a rung (`roll_weight`'s only caller passes (species, rng)).

## Census and record laws (Arm A = Arm B exactly, every rational)

- E_life exact printable anchors (print discipline C9): rank 1 =
  11736310749428605/3026966925030048; ranks 2-3 printed in
  results.json; ranks >= 4 gated by in-memory Fraction equality
  between the twin arms and reported as 12-digit floats (3.8773,
  5.0991, 5.1774, 5.7527, 6.6112, ... 8.5613).
- **Lifetime total, all 21 shore species: ~ 153.3824** (exact in
  memory, twin-gated; disclosed ~ 153.38 reproduced).
- **Career table** E[PB events in n casts] (exact thinned-record
  identity, float-evaluated per C6) beside the DIVERGENT continuous
  benchmark sum_t sum_r (1 − (1 − q_r)^t)/t:
  24.88 @ 50, 44.02 @ 150, 67.42 @ 500, 93.00 @ 2,000, 118.84 @
  10,000 -> 153.38 lifetime, vs continuous ~ 99.2 @ 2,000 and
  ~ 181.4 @ 100,000, unbounded beyond. All five disclosed career
  values and both benchmark values reproduced at stated precision.
- **G5 hand world**: nominal 0.10 -> exactly 9 atoms x 1/9, E_life =
  H9 = 7129/2520, E[catches to ceiling] = 9 — both arms.
- **Degeneracy**: spread collapsed to a point -> 1 atom, E_life = 1.

## The band-margin ledger (C5) and the species sweep

The V083 margin-ledger lesson applied to this head's decision geometry:

- Clause margins: rungs **3** (17 vs 20); p_ceiling **19/4050 ~
  0.004691** (2/81 vs 1/50, 1.235x); E_life **~ 0.12275** (3.8773 vs
  4 — the THINNEST margin, 3.1%); min cadence gap **0.011986** at
  t = 50 (1/50 = 0.02 vs P = 0.008014, 2.50x). **No decision clause
  lands margin-0** (gated exact).
- **The species sweep: rank 1 is the ONLY species inside the REJECT
  bands** (rank 2 already has 52 rungs and E_life ~ 5.099 > 4). The
  REJECT is modal-species-specific by construction and rides entirely
  on L1 — which is exactly why L1 is a gate and the n1 axis exists.
  Named for the manager: any committed change that demotes rank 1
  from modal (a rod with effectively infinite pull, a band that drops
  rank 1) re-keys the census, not the method.

## Anomalies — two, both named first-class (drafter hand-slips of one family)

- **A1 — the G6 refinement decade-1 band miss (a registered-band
  defect, not a law defect).** Registered: rank-1 E_life increases by
  ln 10 +/- 1/10 per grid decade. Measured exact: 0.01 -> 0.001 adds
  **2.176943** (misses ln 10 = 2.302585 by 0.125642 > 1/10); 0.001 ->
  0.0001 adds **2.299806** (inside, 0.0028 off). Cause pinned exactly:
  at 3 dp the support edges 0.117 = N·13/20 and 0.279 = N·31/20 land
  ON-GRID, restructuring both edge atoms to exact half-cells (the 2-dp
  edge cells are 0.8 and 0.4 of an interior cell) — a one-time edge
  correction; from 3 dp on the edge structure is self-similar and the
  increment converges to ln 10. The refinement LEMMA's direction and
  cause-attribution stand (the finiteness is the rounding's, not the
  spread's); the registered +/-1/10 band was too tight for the first
  decade. Applied as registered under the C12 strict reading
  (disclosed in fixtures BEFORE the runner, together with the
  pre-verified miss): the leg FAILS and is logged; per the registered
  evaluation order REJECT is evaluated FIRST and fires on exact
  clauses this leg never touches, so the ruling is unaffected (the
  INVALID stage is never reached). The per-two-decade average reading,
  2.238375, would have passed — published as a reporting row.
- **A2 — the disclosed APPROVE-world horizon "~ 1,480 casts" is
  wrong.** The exact 3-dp re-census gives p_ceiling(1) = **1/324**,
  not 2/810: 0.279 lands ON-GRID at 3 dp, halving the top cell, so the
  horizon is 324/q1 = 1527502293/1293292 ~ **1181.10 casts**. The
  disclosed ~1,480 is the naive x10 scaling (2/81 -> 2/810 => 405/q1
  ~ 1476). **The falsifiability claim SURVIVES the correction**: rungs
  163 >= 100 and horizon 1181.10 >= 1000, so the one-character world
  still lands APPROVE outright — the drafter's number was wrong, the
  drafter's conclusion was right.
- Same family, corrected in the consequence row (not a separate
  anomaly number): the option-(a) gain "+~2.3 lifetime PBs per species
  (+~48 total)" is the ln-10 hand estimate; the exact 3-dp re-census
  gives **+2.1836 avg/species, +45.856 total** (rank-1 +2.1769; large
  ranks approach ln 10). Direction and order of magnitude stand.

## Consequence rows (pre-registered menu, exact numbers attached)

- **(a) round(., 3)**: rungs 17 -> 163 (rank 1; full table in
  results.json, 24,615 at rank 21); minnow horizon 147.64 -> 1181.10
  casts; +2.1836 lifetime PBs avg/species (+45.856 total). Lands BOTH
  APPROVE bands — the verdict flips on one committed character.
- **(b) un-quantize the COMPARISON only** (store raw float, round at
  render): the distribution-free continuous law returns exactly —
  P(PB at t) = 1/t, E[records in n] = H_n, divergent (H_2000 ~ 8.178
  per species). The cheapest true fix; display unchanged.
- **(c) lean in — the badge surface**: the per-species ceiling table
  (exact top atom + probability, all 21 shore ranks; 11 deepwater rows
  ride the same rank-atom law) is in results.json — rank 1 ceils at
  0.28 kg @ 2/81, rank 21 at 42.39 kg @ 1/3282.

## Arm F — the committed roll, verbatim (seed 20261630)

400,000 draws per gated rank; support equality with the exact census
GATED and green on ranks {1, 2, 3, 21} (17/17, 52/52, 99/99, 2462/2462
atoms; same min/max). Frequencies (reporting): ceiling freq 0.024903
beside 2/81 ~ 0.024691 (rank 1); 0.006033 vs 0.005952 (rank 2);
0.010253 vs 0.010101 (rank 3); 0.000268 vs 0.000305 (rank 21). The
float-boundary axis (n2) stays disarmed: no committed-float atom
outside the exact support was observed.

## Arm R — seeded career traces (reporting-only)

2,000 main careers (seed 20261631) + 500 stability careers (20261632)
of 2,000 casts each at the decision cell, strict-> PB counting; aux
20261633 asserted never read (constructor registry):

| horizon | main | stability | exact (thinned law) |
|---|---|---|---|
| 50 | 24.97 | 24.91 | 24.88 |
| 150 | 44.08 | 43.98 | 44.02 |
| 500 | 67.50 | 67.25 | 67.42 |
| 2000 | 93.19 | 92.64 | 93.00 |

No statistical gate rides any of this.

## Reproducibility

- One command, no flags, stdlib-only, hermetic (reads only its own
  `fixtures.json`); CPython 3.11 pinned and asserted.
- **323 self-checks: 322 passed, 1 failed** — the single failure is
  the DESIGNED C12 strict-reading refinement leg (A1), pre-disclosed
  in fixtures before the runner existed; the exit contract tolerates
  exactly that named leg and nothing else (exit 0 on the accepted
  run). No fix-forwards after the runner landed — the first complete
  in-repo run of the committed pipeline is the accepted run.
- stdout + results.json **byte-identical across two full in-repo
  process runs** (external diff + sha256):
  - `results.json` `157fba93450876511748108f6687929ba68987059f44de2c6adaaca0b08b0630`
  - `run-stdout.txt` `00c5b6841e963608aba1e96f82cc4d2bfeeb55cee8a30b7a6d69d241ed11af39`
- ~21 s/run (the exact big-rational record laws over 2,462-atom
  ladders dominate).
- Seeds: 20261630 (Arm F) / 20261631 (Arm R main) / 20261632 (Arm R
  stability) are the ONLY RNGs constructed, in pinned order; aux
  20261633 never read. The drafter's registered set IS the session
  seed set (V077-V083 precedent; no new allocation); 20261624-629
  stays the disclosed in-flight buffer, unused. Registry high-water
  after this slice: **20261633** (reserved; highest read 20261632).

## Boundaries (named beside the ruling, per the registration)

- **The engagement boundary**: the priced object is the committed
  celebration PROCESS (event counts, cadence, termination) — never a
  live-retention elasticity claim. "The celebration stops firing
  forever on a computable horizon" is the fact; its retention weight
  is the lane owner's.
- **The float boundary**: exact half-open real intervals vs the
  committed binary rounding — measure-zero ties disclosed; Arm F is
  the honesty row and its support gate is green.
- **The mix boundary**: the decision cell is the committed bare-rod
  law, exact; other committed cells are L1-gated reporting.
- **The intent boundary**: the REJECT indicts the committed retention
  SENTENCE and the unpriced quantization interaction — never the
  weight feature, never the strict comparison, never the game. The
  consequence menu is where intent lives; the ruling conditions on the
  committed constants @ f8e2313 (a later change to spread/base/
  exponent/rounding/comparison means re-run, not reuse).
- **The display axis (n3)**: probed firsthand at harvest —
  `views/fishing/menu.py:106` renders the record as `{best:g}kg`
  (6 significant digits), never coarser than the 2-dp storage grid;
  disarmed, disclosed.
