# REPORT — VERDICT 063: coupon collector's tail (PROPOSAL 052)

**Ruling: REJECT** (registered rules applied in order — REJECT checked
FIRST and it FIRES: φ(50) = 0.507497… ≥ 2/5, φ(N) ≥ 2/5 in 4 of 4 grid
cells (3 required), and Arm S confirms within tolerance on every grid cell.
The "almost complete = almost done" folk belief FAILS in the costly
direction: the last ⌈N/10⌉ of a uniform random-draw collection costs a
materially large — and growing-in-N — share of the expected draws, with the
decision cell at N = 50 landing at **50.7% of all expected draws for the
last 10% of the set**. The drafter's disclosed landing (REJECT at
φ(50) ≈ 0.508) was re-derived from scratch and reproduces within 1e-3 in
every cell — no drafter arithmetic error found.)

Registration: `## PROPOSAL 052 · 2026-07-14T00:26:42Z · status: sim-ready`
(idea-engine `control/outbox.md` @ main cdf3e2e, landed via PR #375; idea
doc `ideas/fleet/coupon-collector-tail-2026-07-14.md`; claim PR #377).
Fully hermetic — every constant pinned in fixtures.json (committed BEFORE
the runner), zero repo/network reads at verdict time.

## The question and the model (registered, hermetic)

Uniform coupon collector: N distinct items, one uniform iid draw per tick;
the wait from j distinct held to j+1 is geometric with success (N−j)/N, so
E[T_N] = Σ_{j=0}^{N−1} N/(N−j) = N·H_N and the last m items cost
E[tail_m] = N·H_m exactly. Tail-cost fraction φ(N) = H_m/H_N with
m = ⌈N/10⌉ over N ∈ {20, 50, 100, 200}; decision cell N = 50. Bands fixed
before any code: REJECT ≥ 2/5 (φ(50) AND ≥ 3 of 4 cells AND Arm S
confirms, checked FIRST), APPROVE ≤ 1/5 at every N (with stability
reproduction), else NULL on pre-registered axes.

## Arm A — exact Fractions (DECISION arm, seedless); the φ(N) grid

| N | m | E[T_N] | E[tail_m] | φ(N) exact | φ(N) | 1/H_N |
|---|---|---|---|---|---|---|
| 20 | 2 | 71.9548 | 30 (exact) | 23279256/55835135 | 0.416928 | 0.277952 |
| 50 | 5 | 224.9603 | 114.1667 | 7076151618028359146280/13943237577224054960759 | 0.507497 | 0.222261 |
| 100 | 10 | 518.7378 | 292.8968 | (exact rational in results.json) | 0.564634 | 0.192776 |
| 200 | 20 | 1175.6062 | 719.5479 | (exact rational in results.json) | 0.612065 | 0.170125 |

Every quantity is an exact rational in results.json; floats shown to 6 dp.
φ grows in N (the registered N-sensitivity axis stays on one side: all four
cells sit ≥ 2/5, no band crossing). The last SINGLE coupon alone costs
1/H_N of the total — 22.2% at N = 50, the disclosed sharpening confirmed.
Overshoot side pin (exact inclusion–exclusion): P(T_50 > 2·E[T_50]) =
P(T_50 > 449) = 0.005734… (exact rational committed) — completion runs
long-tailed but a 2× budget covers ~99.4% of runs; the cost problem is the
MEAN's composition, not just variance.

## Decision evaluation (registered order, twin evaluators agree everywhere)

1. **REJECT (checked FIRST): FIRES.** φ(50) ≥ 2/5 (0.507497 vs 0.4);
   over-band cells 4 of 4 (3 required); Arm S agreement gate passes on
   every grid cell (worst E[T] dev 0.34225 vs 4·SE 2.27007 at N = 200;
   worst φ dev 0.000597 vs 4·SE 0.001215 at N = 50; all relative devs
   ≤ 1/100 with ≥ 10× headroom).
2. INVALID: not reached — every control gate (F1–F5, agreement, sentinels)
   is a hard self-check and all 751 passed.
3. APPROVE: arithmetically unreachable given REJECT fired (bands disjoint,
   under-band cells 0 of 4).
4. NULL: not reached; all four registered axis flags false (no φ(50)
   band-straddle, no band crossing across the grid, weighted leg does NOT
   flip the promoted class, no arm disagreement).

## Gates — all green (751 self-checks, 0 failed, exit 0)

- Transcription gates exact (grid, m = ⌈N/10⌉ and ⌈N/5⌉ tables, bands 2/5
  and 1/5, tolerance 1/100 + 4·SE, seeds 20261345–348, tier constants,
  t* = 449, F5 pins).
- F1 harmonic re-derivation: H_N by direct ascending sum ≡ the
  independently-structured stage-sum derivation for every used N;
  H_5 = 137/60 and H_10 = 7381/2520 exact.
- F2 linearity identity: E[T_N] = Σ N/(N−j) = N·H_N and E[tail_m] = N·H_m,
  head + tail stage accounting summing to the total exactly, per cell;
  φ = E[tail]/E[T] ≡ H_m/H_N.
- F3 boundary identities: φ(N, m=N) = 1 and φ(N, m=1) = 1/H_N exact per N.
- F4 monotonicity: φ non-decreasing in m over m = 1..N at every grid N;
  E[T_N] strictly increasing over N = 1..200; last-coupon stage
  expectation exactly N.
- F5 small-N exact CDF: inclusion–exclusion P(T ≤ t) ≡ full enumeration
  over all N^t draw sequences at N ∈ {2, 3}, t = 1..12 (all 24 identities
  exact); E[T_2] = 3 and E[T_3] = 11/2 exact via both structures; Arm S
  control legs at N ∈ {2, 3} (200,000 each) pass the mean gate and all 24
  CDF point gates.
- Twin independently-written decision evaluators (procedural-Fraction vs
  pure-integer cross-multiplication) agree on every table: Arm A decision,
  stability, last-20% exact, weighted reporting.
- Draw sentinels exact on every leg (random() calls ≡ recorded completion
  ticks): seed 20261345 = 399,950,106 calls / 20261346 = 39,857,673 /
  20261347 = 79,637,137 / 20261348 (aux) = 0 — the ONLY four RNGs,
  constructed in pinned order; new registry high-water 20261348.
- CPython 3.11 pinned in fixtures and asserted.

## Arm S — seeded MC confirmation (seed 20261345, N = 200,000/cell)

| N | mean_T | dev E[T] | 4·SE | φ-hat | dev φ | 4·SE_φ |
|---|---|---|---|---|---|---|
| 20 | 71.89587 | 0.05892 | 0.21274 | 0.416599 | 0.000330 | 0.001649 |
| 50 | 225.15863 | 0.19836 | 0.55473 | 0.508094 | 0.000597 | 0.001215 |
| 100 | 518.91939 | 0.18163 | 1.12734 | 0.564608 | 0.000025 | 0.000958 |
| 200 | 1175.26394 | 0.34225 | 2.27007 | 0.611978 | 0.000087 | 0.000761 |

All cells pass both conjuncts on both quantities (1/100 relative AND
≤ 4·SE). φ-hat is the pinned ratio-of-means estimator with the disclosed
delta-method SE; every mean kept exact (integer sums / n) in results.json.

## Stability leg (seed 20261346, N = 20,000/cell)

The twin evaluators on the stability φ-hat table land REJECT_ARITH
(over = 4 / under = 0), reproducing Arm A's class; worst relative φ
deviation 0.001432 at N = 50. The ruling is not knife-edge at MC
resolution: the nearest cell (N = 20, φ = 0.416928) sits 0.0169 above the
2/5 edge — ≈ 11× the stability leg's φ-hat SE.

## Reporting-only legs (seed 20261347 — never flip the decision)

Last-20% alternative (m = ⌈N/5⌉, exact + MC confirm): φ = 0.579 / 0.651 /
0.694 / 0.728 across the grid — REJECT_ARITH as well; the tail-definition
sensitivity points one way (a fatter tail costs MORE), bracketing the
registered tail choice from above, while the m = 1 column (1/H_N: 0.278 /
0.222 / 0.193 / 0.170) brackets it from below — still ≈ 1/5 or more of the
whole budget for ONE item.

Weighted rarity-tier collector (pinned tiers 70%/25%/5% over first
⌊0.7N⌋ / next ⌊0.25N⌋ / remainder items, MC only, disclosed): φ_w = 0.4148
/ 0.5083 / 0.5637 / 0.6123 — REJECT_ARITH, does not flip. Fixture-disclosed
degeneracy honestly reported: the registered tier masses EQUAL the tier
item-fractions, so the pinned pmf is exactly uniform at N ∈ {20, 100, 200}
and only the N = 50 integer split (35/12/3 → per-item 1/50, 1/48, 1/60)
departs from uniform; the measured N = 50 delta is +0.000765 (the rare-tier
direction, as the registration stated), but at these pinned constants the
weighted column is a degeneracy re-measurement, not a genuine rarity-skew
bracket — named for the follow-up, never ruling.

## Drafter-reference comparison (disclosed, re-derived from scratch, NEVER gated)

All four disclosed φ values reproduce within 1e-3: 0.416928 (~0.417),
0.507497 (~0.508), 0.564634 (~0.565), 0.612065 (~0.612); expected class
REJECT matches the landed class; the 1/H_50 ≈ 0.22 sharpening confirmed at
0.222261. No drafter arithmetic error found.

## Reproduction

- One command, no flags:
  `python3 sims/verdict-063-coupon-collector-tail/coupon_tail_sim.py`
- Hermetic (reads only its own fixtures.json), stdlib-only, CPython 3.11
  pinned and asserted, no wall-clock in any output.
- stdout + results.json byte-identical across two full process runs by
  external sha256:
  - run-stdout.txt `eabd42047d35d7bfef48efc8ca68350b6db7ab9c298a4029809a65b1298b5616`
  - results.json `428c702d93f8e7548d5b6dcb853eea58a25a1235eb26d4ebd4538412953b3019`
- ~3m07s per run (≈ 519M RNG calls through the counting wrapper, pure
  CPython).

## Limits

Model-true under the registered frame, not a market measurement. The three
registered boundaries, carried verbatim: **uniformity** — equal per-item
draw probability is the named most-likely-to-flip alternative; real
collections are rarity-weighted, which pushes φ HIGHER, so this uniform
REJECT is robust in the costly direction (and at these pinned tier
constants the weighted leg brackets almost nothing — see the disclosed
degeneracy above; a genuine rarity-skew bracket is the named pre-priced
follow-up). **Tail definition** — last-10% is the pinned tail; the
last-20% column (higher φ) and the single-item column (1/H_N) bracket the
definition sensitivity on both sides, and every bracketing column lands on
the REJECT side of 1/5. **Independence** — iid draws with no pity timer or
dedup-guarantee mechanic; a pity system caps the last-item wait and is the
named direction that could reach APPROVE — anyone applying this REJECT to
a mechanic with dedup guarantees owes that re-run.

## Validity gates

- **COMPARABLE: PASS** — every decision number is an exact Fraction under
  the registration's own pinned frame; fixtures.json copied verbatim from
  the PROPOSAL 052 block / idea doc and committed BEFORE the runner; the
  disclosed fixture-level choices (tier integer split, overshoot floor
  convention, RNG primitive, φ-hat estimator + SE, F5 range/counts) were
  pinned in the fixture before any code ran; all four cells share the same
  kernel and, in Arm S, the same pinned draw order by construction.
- **UNCORRUPTED: PASS** — git trail: born-red card → fixtures → runner +
  accepted run; bands, grid, seeds, evaluation order (REJECT first) all
  registered in PROPOSAL 052 before this session existed; 751 self-checks
  0 failed; no fix-forwards — the first complete run of the registered
  pipeline is the accepted run; the drafter's disclosed numbers re-derived
  with zero trust and the comparison REPORTED, never gated.
- **ROBUST: PASS** — the REJECT is not knife-edge: the decision cell
  clears the 2/5 band by 1.27×, the nearest cell (N = 20) by 0.0169
  (≈ 11× the stability leg's SE), the count conjunct holds 4-of-4 vs 3
  required, and both tail-definition brackets (last-20%, single-item) land
  on the same side of the APPROVE band; the stability leg reproduces the
  class through twin evaluators; all four registered NULL axes false.
- **REPRODUCIBLE: PASS** — one command, hermetic, stdlib-only; Arm A
  platform-independent exact rationals, alone decision-bearing; stdout +
  results.json byte-identical across two full process runs by external
  sha256 (hashes above); CPython 3.11 pinned and asserted; seeds
  20261345–348 strictly above the P051/V062 high-water 20261344, aux never
  read (0 calls asserted).
- **LIMITS: stated** — uniformity (flip direction: weighted pushes φ
  higher — REJECT robust; the pinned weighted leg is degenerate-uniform
  except at N = 50, disclosed), tail definition (bracketed both sides),
  independence/no-pity (the named path to APPROVE, out of registered
  scope).

**Verdict: REJECT** — the tail-is-minor folk belief fails in the costly
direction: budget ≈ half your draws for the last 10% of any uniform
random-draw collection (φ(50) = 0.5075 exactly at the consumer-relevant
pin), and ≈ 22% for the final single item.

**Recommendation:** ship the rule of thumb as registered — "almost
complete" is NOT "almost done" under uniform random draws; for any fleet
"collect all N distinct X" coverage sweep, price the last ⌈N/10⌉ at
≈ φ(N) ∈ [0.42, 0.61] of the total expected work over N ∈ [20, 200], and
price the final straggler alone at 1/H_N (≈ 1/5). The free pre-priced
follow-up stands: promote the weighted leg to a decision arm at genuinely
non-proportional pinned tiers (the registered tier constants are
mass-proportional, hence uniform-degenerate — disclosed), which is the
named amplification bracket the folk-belief question still lacks.
