# VERDICT 099 — ACCEPT — a series quality budget's CONCENTRATE→SPREAD optimum flips exactly at the read-through ceiling (P086, series-readthrough-saturation-crossover)

**Ruling: ACCEPT** (no failing gate — all of R1→R2→R3→R4 hold). Source proposal
header cited verbatim: `## PROPOSAL 086 · 2026-07-16T17:48:11Z · status: sim-ready`
(idea-engine `ideas/venture-lab/series-readthrough-saturation-crossover-2026-07-16.md`);
P086 → V099 under the constant **+13** PROPOSAL↔VERDICT offset, confirmed at sim-lab
`docs/current-state.md` § Verdict-numbering map.

On the pinned N=4-book multiplicative read-through funnel (entry cohort C=2000 readers
per seed, seeds S=[1,2,3,4,5], r_base=0.30, ceiling r_max=0.85 the stability bound,
linear map r_k=min(r_max, r_base+slope·b_k) with slope=0.05 so a single step saturates
at b=(0.85−0.30)/0.05=**11** budget units, CONCENTRATE bs=(B,0,0) vs SPREAD
bs=(B/3,B/3,B/3), budget grid B∈{6,11,16,22,33}) two quality-budget allocations are
compared under COMMON RANDOM NUMBERS — per seed each of the C readers' three uniforms
(u1,u2,u3) is drawn ONCE and the identical matrix is reused for BOTH allocations AND
across ALL budgets B (a reader advances transition k iff u_k < r_k; books are
cumulative, stopping at the first failed transition). P086 pre-registered an ACCEPT
rule requiring ALL four gates R1–R4. The measured run ACCEPTS: at B=6 CONCENTRATE beats
SPREAD for all five seeds at **29.81σ** (R1), at B=33 SPREAD beats CONCENTRATE for all
five seeds at **156.67σ** (R2), every realized r_k lands in [0.30, 0.85] and mean
revenue is monotone non-decreasing in B for both allocations (R3), and the crossover
budget **B\*=22** sits strictly in (11, 22] while CONCENTRATE's mean revenue is FLAT
(4336.6 books, 0.0 variation) across B∈{11,16,22,33} — the reversal is mechanistically
caused by the entry step clamping at r_max (R4). The measured table reproduces the
proposal's disclosed dry-sim calibration to the book (R1 per-seed diffs
[454,435,388,381,426] and 29.8σ; R2 diffs [1974,2042,2002,1989,2032] and 156.7σ;
B\*=22; CONCENTRATE flat 4336.6) from an INDEPENDENT re-implementation of the funnel.
Both independently-written decision evaluators agree ACCEPT/None on the measured gate
outcomes.

7 self-checks, 7 passed, 0 failed; exit 0 on the accepted run; < 1 s/run; hermetic —
CPython 3.11.15, stdlib only, zero repo/network reads at verdict time. The two
allocations share one per-seed uniform matrix (CONCENTRATE and SPREAD see identical
reader draws — a per-mode matrix fingerprint is compared and a divergence raises
`SystemExit("NULL: allocations saw different draws")`), and the seed-1 B=6
first-50-reader (u1,u2,u3) draws with books-bought under both allocations are committed
as the fixture and re-verified each run. stdout + results.json byte-identical across two
full in-repo process runs by external diff + sha256:

- `results.json` sha256 `14e7a4d57db265c7f042759e401c4c2521c9036493f961fa3ed1b152cfbbfb3d`
- `run-stdout.txt` sha256 `4d43e3194fdd1c8da0402e8d1e7f348c355c39f665c40160f103648600c7d9d8`
- `fixtures.json` sha256 `69fe5aa13d4ea78519843880cad930f91dc6a6211ddfaceb78f9cd9a87fa74d5`

## The decision clauses (all measured)

- **R1 reach regime @ B=6 — PASS.** At the low anchor B=6 (CONCENTRATE unsaturated:
  r_1=0.60, margin 0.25 below r_max) CONCENTRATE's per-seed revenue exceeds SPREAD's for
  ALL five seeds — per-seed CONC−SPREAD diffs = [454, 435, 388, 381, 426] (all strictly
  positive) — mean margin 416.80 books, paired margin **29.81σ ≥ 3**. The reach argument
  holds: a budget unit at the earliest transition multiplies through every downstream
  book (∂E/∂r_1 = 1+r_2+r_2·r_3 = 1.39 at the base world, the highest shadow value), so
  concentrate genuinely wins while the entry step still has headroom.
- **R2 saturation reversal @ B=33 — PASS.** At the high anchor B=33 (CONCENTRATE's entry
  step saturated at b_1=33 ≫ 11, wasting 22 units at the ceiling; SPREAD's b=11/step just
  reaches r_max) SPREAD's per-seed revenue exceeds CONCENTRATE's for ALL five seeds —
  per-seed SPREAD−CONC diffs = [1974, 2042, 2002, 1989, 2032] (all strictly positive) —
  mean margin 2007.80 books, paired margin **156.67σ ≥ 3**. The optimum has flipped: past
  saturation every extra unit on book 1 buys zero reach while SPREAD's three unsaturated
  transitions keep converting.
- **R3 well-posedness — PASS.** Every realized r_k across all modes/budgets lies in
  [0.30, 0.85] (by construction of the min-clamp), and mean revenue is monotone
  non-decreasing in B for BOTH allocations: CONCENTRATE [3641.8, 4336.6, 4336.6, 4336.6,
  4336.6] (rises then flat), SPREAD [3225.0, 3651.6, 4129.4, 4804.8, 6344.4] (strictly
  rising). No read-through exceeds the ceiling (the V098-family stability check) and
  neither allocation's revenue curve dips.
- **R4 crossover at the entry-step ceiling — PASS.** B\* (smallest grid B with mean
  rev(SPREAD) ≥ mean rev(CONCENTRATE)) = **22**, which lies strictly in (11, 22]; and
  CONCENTRATE's mean revenue is FLAT — 4336.6 books at every B∈{11,16,22,33}, 0.0-book
  variation — because r_1 is clamped at r_max=0.85 for all b_1≥11 and (under common
  random numbers) the identical uniform matrix yields the identical per-reader books at
  every one of those budgets. The reversal is therefore located AT the world's own
  stability bound, not caused by a downstream artifact — the mechanistic core of the
  head.
- **ACCEPT fires.** All four gates hold in the registered order R1→R2→R3→R4, so the
  pre-registered rule (ACCEPT iff R1∧R2∧R3∧R4) returns ACCEPT with no failing gate. The
  REJECT world was genuinely reachable (a mis-set slope/r_max that never saturated
  CONCENTRATE within the grid would fail R2/R4) and did not come live.

## Twin evaluators and agreement

Two independently-written decision evaluators score the SAME measured gate outcomes:

- **Evaluator A (if-chain):** applies R1→R2→R3→R4 as a short-circuit if-chain, returning
  the ruling token and the first gate whose predicate is False → **ACCEPT / None**.
- **Evaluator B (table-driven):** an independently transcribed table of (gate, outcome)
  rows, scanned in the registered order for the first False → **ACCEPT / None**.

Both agree on BOTH the ruling token (ACCEPT) AND the first-failing-gate reason (None),
checked by the self-checks `twin_evaluators_agree_verdict` and
`twin_evaluators_agree_reason`. The seed-1 B=6 first-50-reader draws and books match the
committed fixture (`fixture_matches_committed`), the five per-seed uniform matrices are
distinct and shared across both allocations (`common_random_numbers_shared_per_seed`),
every realized rate is within the stability bound
(`realized_rates_within_stability_bound`), the cohort size is C=2000 (`cohort_size_is_C`),
and the budget grid straddles the saturation budget b=11
(`budget_grid_straddles_saturation`) — 7/7.

## Margin ledger (typed, per-seed revenues over S=[1,2,3,4,5]; mean = total books over the C=2000 cohort)

| B    | CONCENTRATE mean | SPREAD mean | SPREAD − CONC |
|------|------------------|-------------|---------------|
| 6    | 3641.80          | 3225.00     | −416.80       |
| 11   | 4336.60          | 3651.60     | −685.00       |
| 16   | 4336.60          | 4129.40     | −207.20       |
| 22   | 4336.60          | 4804.80     | +468.20       |
| 33   | 4336.60          | 6344.40     | +2007.80      |

- **R1 margin (the passing reach-regime margin):** at B=6, per-seed diffs CONC−SPREAD =
  [454, 435, 388, 381, 426], all > 0; mean 416.80 books, SEM of the paired diff 13.98
  books → **29.81σ ≥ 3** → PASS.
- **R2 margin (the passing reversal margin):** at B=33, per-seed diffs SPREAD−CONC =
  [1974, 2042, 2002, 1989, 2032], all > 0; mean 2007.80 books, SEM 12.82 books →
  **156.67σ ≥ 3** → PASS.
- **R3:** all realized r_k ∈ [0.30, 0.85] (CONCENTRATE r=(0.60/0.85,0.30,0.30);
  SPREAD r=(0.40,0.4833,0.5667,0.6667,0.85) across the grid); mean-rev monotone
  non-decreasing for both → PASS.
- **R4:** B\*=22 ∈ (11, 22]; CONCENTRATE mean revenue flat at 4336.6 books over
  B∈{11,16,22,33} (0.0-book variation) → PASS.

The crossover algebra: CONCENTRATE's entry step saturates at b_1 = (r_max−r_base)/slope =
(0.85−0.30)/0.05 = **11**, past which its revenue is pinned (extra budget on book 1 is
wasted at the r_max ceiling). SPREAD keeps all three transitions unsaturated far longer
(each gets only B/3), so its every budget unit still buys reach; the two mean-revenue
curves cross between B=16 (SPREAD 4129.4 < CONC 4336.6) and B=22 (SPREAD 4804.8 > CONC
4336.6), locating B\*=22 — the reversal sits at the world's own saturation bound.

## Falsifiability gates (were real)

- **Common random numbers (else NULL):** the two allocations are compared on ONE per-seed
  uniform matrix — each mode's evaluation fingerprints the matrix it iterated and the run
  asserts CONCENTRATE's and SPREAD's fingerprints equal the seed's canonical matrix
  fingerprint; a divergence raises `SystemExit("NULL: allocations saw different draws")`.
  Without shared draws the paired comparison would be an allocation-vs-noise confound and
  the run would route NULL.
- **Fixture pin:** the seed-1 B=6 first-50-reader (u1,u2,u3) draws and their books-bought
  under BOTH allocations are committed and re-derived each run — one misread of the
  advance/cumulative-books order moves the fixture and trips the check.
- **Stability bound:** every realized r_k is asserted within [0.30, 0.85]; the min-clamp
  makes the ceiling a hard invariant, not an aspiration.
- **Grid-straddles-saturation:** the budget grid is asserted to contain a B below and a B
  above the saturation budget b=11, so both the reach regime (R1) and the saturation
  regime (R2/R4) are reachable — a grid entirely on one side would make a gate untestable.

Any self-check failure would have blocked exit 0. The REJECT world was reachable (a
mis-set slope/r_max that never saturated CONCENTRATE within the grid would fail R2 and
R4, the proposal's own named honest failure mode) and did not come live — all four gates
pass.

## Scope boundaries (stated, per the registration)

- **Map-constant boundary:** r_base=0.30, r_max=0.85, slope=0.05 are STIPULATED pinned
  constants disclosed as calibration-not-estimate, NOT fit to any real series' measured
  read-through. The ruling prices the phenomenon UNDER the pinned linear map; it is not a
  claim about a real author's production function.
- **Map-shape boundary:** the linear quality→read-through map is a deliberate modeling
  choice that ISOLATES the saturation mechanism. A concave map would saturate more gently
  and move B\*; that is a named follow-up, not a measured result here.
- **Estimator boundary:** revenue is the cohort-total books over C=2000 readers, and the
  gates are PASS/FAIL on the seed-mean revenues and the paired-diff margins over the five
  seeds S=[1,2,3,4,5]; the claim is the gate-by-gate outcome on those means, not a
  distributional/CI statement over an ensemble of cohorts.
- **Allocation-pair boundary:** the ruling binds the CONCENTRATE-vs-SPREAD comparison on
  the pinned map, budget grid, and cohort. Intermediate or adaptive allocations, N-book
  families beyond N=4, and per-step slopes are DIFFERENT objects not tested here.

## Consequence hand-off (pre-registered; routing is the manager's per Q-0260)

This is a venture-lab head (the CONSUMER owns the KDP series quality-budget allocation
guidance). The deliverable is a citable measured verdict plus a transferable
budget-allocation rule, fanned in to the fleet manager (Q-0264). Per the proposal's
pre-registered ACCEPT consequence, paste-ready and recommendation-first (Q-0263.2):
**(1, recommended)** adopt the SWITCH rule — pour the series quality budget into book 1
UNTIL its read-through nears the ceiling (here b_1 ≈ 11 units, where r_1 reaches
r_max=0.85), THEN redirect the surplus downstream; "make book 1 great" is right only until
its read-through saturates, and the crossover B\*=22 is the operational trigger; **(2)**
both folk beliefs are priced, not just retold — folk belief #1 ("make book 1 great,
everything flows from the funnel entry") is CORRECT while the entry step has headroom (R1),
folk belief #2 ("even quality across the series") is CORRECT once the entry step saturates
(R2), and the switch between them sits at the world's own stability bound r_max (R4);
**(3)** the ceiling-location result tells the author WHY, not just THAT — past saturation
the entry step's marginal revenue per budget unit is exactly ZERO, so surplus book-1
budget is wasted while downstream transitions still convert. Transferable audit: any
multiplicative funnel with a per-stage quality→conversion ceiling (a book series, a
multi-step onboarding, a checkout funnel with a saturating top-of-funnel) — "is the
earliest stage saturated at its ceiling, and if so is marginal budget being redirected to
the still-unsaturated downstream stages?"

## Seeds

**V099 consumes NO seed-ledger block.** The seeds are the in-file constants S=[1,2,3,4,5]
(`random.Random(seed)`), a fixed local realization set that drives each seed's
common-random-numbers uniform matrix — NOT a draw from the fleet seed ledger. The next
free ledger block stays **20261730**, untouched (inherited unchanged from the V098 baton).
Both allocations share one uniform matrix per seed so the seeds drive identical reader
draws to CONCENTRATE and SPREAD; no seed touches the decision rule, which is a
deterministic gate-by-gate comparison of the seed-averaged revenues and the paired-diff
margins.
