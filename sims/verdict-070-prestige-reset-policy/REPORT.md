# VERDICT 070 — REPORT

**Serving:** idea-engine `## PROPOSAL 059 · 2026-07-14T05:19:21Z · status: sim-ready`
(control/outbox.md @ main 99ce912, landed via idea-engine PR #402; idea doc
`ideas/superbot-idle/prestige-reset-policy-optimality-2026-07-14.md` @ 94cceaa).
**Source pin:** superbot-idle @ `5ddd5a230d4a6504c06b52805cba5dc8b3276b44`.
**Seeds:** 20261373 (Arm-R main, 12+6) / 20261374 (stability, 4+2) /
20261375 (presentation shuffle only) / 20261376 (aux — NEVER read, asserted).

## Ruling: REJECT

Pre-registered rule, evaluated in the registered order (REJECT → INVALID →
APPROVE → NULL), all comparisons exact big-int:

1. **REJECT — FIRES.** ∃ π ∈ Π \ {fixed-1}: 100·total(π) ≥ 101·total(fixed-1):
   - `hybrid-1000`: 100 · 27,411,200,535 = 2,741,120,053,500 ≥
     101 · 25,386,048,335 = 2,563,990,881,835 — a **7.98% beat vs the 1% line**
     (ratio 27,411,200,535 / 25,386,048,335 ≈ 1.079774).
   - `hybrid-10000`: 26,870,606,289 ≈ 1.058479× — a second cell above the line.
   - Both totals reproduced EXACTLY by the independently written per-second
     Arm B (choice C9; F6 twin equality holds on every total of every leg).
   - **Mechanism attribution holds (NULL axis ii NOT triggered):** with
     milestones OFF the same argmax beater LOSES — hybrid-1000 OFF
     9,405,520,499 vs fixed-1 OFF 9,607,934,390 (0.978933×). The beat is
     exactly the lifetime-3 (+5% forever) rung the greedy loop can never
     earn and `tools/simulate.py` folds zero of.
2. INVALID — not reached; **all gates F1–F6 green** (below).
3. APPROVE — not reached (mutually exclusive with REJECT by arithmetic).
   The grind half of the docstring claim is nonetheless CONFIRMED and
   reported: total(fixed-1) = 1024.972× total(never) (≥ 2× line).
4. NULL — not reached. Horizon-conditional reporting leg: the promoted
   clause HOLDS at H/2 (hybrid-1000 = 1.037531× greedy at 7 days ≥ 101/100),
   so no horizon-conditional finding is triggered.

The REJECT is precise, not global: "reset-and-grow" beats grinding
(1024.97×); the committed SCHEDULE of resetting (reset the instant you are
eligible) is what fails at the fold the engine ships.

## The 15-policy grid @ H = 1,209,600 s (milestones ON, exact integers)

| policy | total | final P | resets | milestones | ratio vs greedy |
|---|---:|---:|---:|---:|---:|
| never | 24,767,541 | 0 | 0 | 3 | 0.000976 |
| **fixed-1 (greedy)** | **25,386,048,335** | 174,619 | 174,619 | 5 | 1.0 |
| fixed-2 | 2,308,530,416 | 11,301 | 11,301 | 5 | 0.090937 |
| fixed-4 | 5,562,567,873 | 27,034 | 13,517 | 5 | 0.219119 |
| fixed-9 | 1,189,091,761 | 3,954 | 1,318 | 5 | 0.046840 |
| fixed-16 | 460,817,123 | 1,148 | 287 | 5 | 0.018152 |
| fixed-25 | 250,843,290 | 500 | 100 | 5 | 0.009881 |
| fixed-100 | 56,754,018 | 50 | 5 | 6 | 0.002236 |
| hybrid-0 | 1,905,424,414 | 17,843 | 17,834 | 6 | 0.075058 |
| hybrid-100 | 24,975,644,645 | 170,715 | 170,706 | 6 | 0.983833 |
| **hybrid-1000** | **27,411,200,535** | 182,276 | 182,267 | 6 | **1.079774** |
| hybrid-10000 | 26,870,606,289 | 179,801 | 179,792 | 6 | 1.058479 |
| cooldown-60 | 15,237,507,974 | 33,844 | 13,357 | 5 | 0.600232 |
| cooldown-300 | 5,758,125,849 | 10,290 | 3,180 | 5 | 0.226822 |
| cooldown-3600 | 1,041,938,127 | 1,416 | 322 | 6 | 0.041044 |

Falsifiability behaved as registered: hybrid-100 lands BELOW parity
(0.983833 — detouring too early starves the compounding base), hybrid-0
collapses (0.075058), every fixed-m ≥ 2 and every cooldown loses outright.
The beater also wins the two other natural metric readings (final P
182,276 > 174,619; milestone set 6 > 5) — the ruling is metric-robust as
disclosed.

## Cooldown price table (the lane's flagged v2 cap, priced)

Fraction of the Π-best's (hybrid-1000) output, pinned + Arm-R probes:
τ=60 → 0.555886 · τ=300 → 0.210065 · τ=527 → 0.144872 · τ=976 → 0.095162 ·
τ=1185 → 0.083259 · τ=1387 → 0.074549 · τ=1768 → 0.062823 ·
τ=3600 → 0.038011 · τ=3965 → 0.035718 · τ=5032 → 0.030013 · τ=6397 → 0.025293.
(Drafting disclosed 0.56 / 0.21 / 0.038 for the pinned τ — reproduced.)

## Gates (any failure → INVALID) — ALL GREEN

- **F1 engine-fold identities:** cost ladder 60/69/79 ✓; rate-by-level at
  P=0 milestones-off [1,1,1,1,2,2] ✓; HEAD fold at neutral theme + zero
  milestones integer-identical to the legacy //10,000 fold (sweep L 0–100 ×
  P samples) ✓; isqrt(1)=1 first-award identity ✓.
- **F2 V038 cross-pins (milestones-OFF greedy):** first prestige at
  t = 12,573 exactly, award 1 ✓; run durations 1–3 = 12,573/11,536/10,475
  exactly ✓; 14-day reset count = **80,795 hard** under the pinned boundary
  order ✓ (twin agrees). The ±1 vs the harness's ~80,796 is now diagnosed
  exactly: a reset lands exactly at t = H = 1,209,600, which the pinned
  convention (choice C1, boundary actions strictly before H) excludes and
  the vendored harness's `t + dt > horizon` convention includes.
- **F3 milestones-OFF contrast:** total_OFF(π) ≤ total_ON(π) for all 15 π ✓
  (exact monotonicity); OFF fixed-1 reproduces F2 ✓. The OFF ratio table is
  the attribution report: hybrid-1000 OFF = 0.978933× (beat inverts),
  hybrid-10000 OFF = 0.998771× (also below parity OFF).
- **F4 conservation:** balance + cumulative spend = run lifetime at every
  boundary; Σ closed-run lifetimes + open run = total at every boundary;
  Σ owned = 1 always, owned rungs never fire ✓ (all policies, all legs).
- **F5 hand world (H = 200 s):** purchases at t = 60 (cost 60) and t = 129
  (cost 69) exactly, horizon balance 71, lifetime = total = 200, L = 2, no
  milestone earned ✓ (both arms).
- **F6 battery:** twin evaluators exact-equal on EVERY total (ON@H, OFF@H,
  ON@H/2, all 24 Arm-R probes) ✓; randrange sentinels 12+6 (seed 20261373)
  and 4+2 (seed 20261374) counted and asserted ✓; presentation seed
  20261375 used for exactly one shuffle ✓; aux 20261376 never read,
  constructed-RNG set = {20261373, 20261374, 20261375} ✓; CPython 3.11
  pinned and asserted ✓; stdout + results.json byte-identical across two
  full process runs (external sha256, below) ✓.

## Reproducibility

- `SELF-CHECKS: 72 passed, 0 failed`, exit 0, ~67 s per full process run,
  stdlib-only, hermetic (reads only its own fixtures.json), CPython 3.11.15.
- Byte-identical double run (external sha256):
  - `run-stdout.txt` `029221996581447ab79c71ed10e35de9d3d24bd144ff16088d431dcf387abe03`
  - `results.json` `732246f0f62f18914fa5ccec7a1782b02099d33dca4e9e34bf910c71c40258ac`
  - `fixtures.json` sha256 `a4f67e02320d9829cdda0ba065338c1f2bb6737a54c7f2e26bfe48d04502ebdd`
- No fix-forwards: fixtures committed before the runner; the first complete
  run of the registered pipeline is the accepted run committed here.
- Drafter-disclosed landing re-derived from scratch and compared, NEVER
  gated: **all 15 disclosed totals reproduced digit-for-digit**, and the
  disclosed ratios (0.9838 / 1.0798 / 1.0585 / 0.6002 / 1024.97× / OFF
  0.9789 / H/2 1.0375 / H/2 hybrid-10000 exactly 1) all reproduce.

## Arm R (reporting-only, never decision-bearing)

Main (20261373): 12 hybrid triggers k ∈ {16256, 36766, 3862, 44627, 58921,
2272, 53885, 19087, 4013, 47285, 12900, 40274}, 6 cooldowns τ ∈ {976, 1387,
3965, 5032, 6397, 527}; stability (20261374): k ∈ {45142, 20780, 24120,
55383}, τ ∈ {1768, 1185}. Every probe total reproduced exactly through Arm B.
**No probe beats the Π-best** (best probe: hybrid-2272 at 27,317,178,883 <
hybrid-1000's 27,411,200,535) — the k-timing curve rises from k=100 toward
k≈1000–2272 and falls thereafter; one planned "ascension" detour pays ~8%
over pure spam, timed neither too early nor too late.

## Named findings / anomalies (first-class)

1. **F2 ±1 diagnosed exactly** (above): a greedy-OFF reset lands exactly at
   t = H; convention C1 vs the harness convention is the whole ±1.
2. **The cooldown price is strongly horizon-dependent:** at H/2 cooldown-60
   sits at 0.994643× greedy (near parity) vs 0.600232× at H — a cadence cap
   looks nearly free at 7 days and costs 40% at 14. Any v2 cap criterion
   should state its horizon.
3. **hybrid-10000 at H/2 = greedy exactly** (ratio exactly 1, identical
   totals): P never reaches 10,000 by day 7, the detour never fires — the
   disclosed degeneracy reproduced to the byte.
4. **Reset-cadence degeneracy quantified** (the heartbeat's "~13 s resets"):
   in the shipped (milestones-ON) fold greedy's late runs bottom out at 2 s
   duration (day-14 bin = 43,200 resets — one per 2 s; OFF world bottoms at
   3 s, the heartbeat's ~13 s figure is an earlier-day average); the Π-best
   keeps the same late cadence — the beater does not fix the spam, it banks
   lifetime-3 first (the cap question is genuinely separate, and now priced).

## Validity-gate answers (repo grammar)

- **COMPARABLE:** every decision number is an exact integer under the
  registration's own pinned frame; fixtures verbatim from the PROPOSAL 059
  block; fixture-level choices C1–C9 disclosed in fixtures.json BEFORE the
  runner existed (commit order enforced in the PR trail).
- **UNCORRUPTED:** fixtures committed before the runner; no fix-forwards;
  first complete registered run accepted; 72 self-checks 0 failed; the
  drafter's disclosed landing re-derived from scratch and compared never
  gated; bands, seeds, policy family, evaluation order all registered in
  PROPOSAL 059 before this session existed.
- **ROBUST:** the REJECT clears its line by ≈ 8× in exact arithmetic (no
  noise exists); a second beater sits above the line independently; the
  beat survives the H/2 leg (1.0375); falsifiability real (hybrid-100 below
  parity at H; three of four pinned hybrids do NOT beat greedy at H/2).
- **REPRODUCIBLE:** one command, no flags, stdlib-only, hermetic;
  byte-identical stdout + results.json across two full process runs by
  external sha256; CPython minor pinned and asserted; seeds 20261373–375
  the only RNGs constructed, aux 20261376 never read.
- **LIMITS:** model-true under the registered frame — within-Π optimality
  scope on APPROVE (moot: REJECT is sound on one beater regardless of Π's
  completeness); the harness's own greedy micro-policy inside every
  macro-policy (a smarter buyer is a different head); SIM-001 reference
  world (count fixed 1, theme neutral — application guard condition 2);
  decision metric = total produced over H (the beater also wins final P and
  milestone count, disclosed); verdict conditions on the SIM-PINNED
  constants + ladders + HEAD fold @ 5ddd5a2 (application guard condition 1).

**Best-implementation recommendation** (per the proposal's pre-registered
REJECT consequence; routing lane-side via the manager per Q-0260): (a,
recommended) fold milestones into `tools/simulate.py` and re-baseline
"optimal play" on the full fold BEFORE registering the v2 cap/cooldown
criterion, using this verdict's policy evaluator + cooldown price table as
the sizing input; (b) re-scope the S3 label as "optimal in the pre-milestone
fold"; (c) amplify the patient detour as a deliberate "ascension run"
mechanic — an owner/lane intent call, never ruled by fiat here.
