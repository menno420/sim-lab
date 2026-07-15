# VERDICT 085 — the pooled-screening prevalence wall (idea-engine PROPOSAL 072) — REPORT

## Ruling

**REJECT** (per the pre-registered rule applied in the registered order
REJECT → INVALID → APPROVE → NULL, REJECT evaluated FIRST; both
independently-written decision evaluators agree REJECT/REJECT; every
decision number is an exact rational). All three REJECT clauses fire at
the pre-registered cells:

- **R1 — the wall + practical damage (p = 2/5)**: T(n, 2/5) > 1 for
  EVERY n ∈ {2..64} (the strict wall clause — q = 3/5 < 3^(−1/3),
  certified by 3q³ = 81/125 < 1), AND the minimum over the practical
  grid n ∈ {2..8} is ≥ 21/20. The true practical min is
  **T(8, 2/5) = 3463137/3125000 ≈ 1.10820** (margin ×1.0554); the
  grid-tail min over {2..64} is 1 + 1/64 − (3/5)⁶⁴ ≈ 1.015625 at n = 64
  (the honest infimum-1 disclosure — the damage quantifier is
  grid-bounded by design).
- **R2 — the pair is never optimal**: the identity
  **T(2, q) − T(3, q) = (q − 2/3)²(q + 1/3) + 1/54** holds by exact
  coefficient match AND on the 102-point identity grid, floor **1/54**
  attained exactly and only at q = 2/3. Every gap ≥ 1/54.
- **R3 — the savings are real (p = 1/100)**:
  **T\*(1/100) = 21512792031541191037911/110000000000000000000000
  ≈ 0.195571 ≤ 1/4** at n\* = 11 (margin ×1.2783) — pooling saves ~80%
  where the folk belief lives.

APPROVE was mutually exclusive by arithmetic and its world was genuinely
live: deleting the pool test's 1/n cost (the falsifiability world) makes
T̃(n, 2/5) < 1 for every n and flips the verdict to APPROVE outright — so
the run was never theater.

## The three structure theorems — verified as gates

- **T1 — the WALL (F2a)**: pooling helps at p for some n ∈ {2..64} iff
  3q³ > 1 iff p < p\* = 1 − 3^(−1/3), certified by the integer-power
  chain 3² = 9 > 8 = 2³, 3⁴ = 81 > 64 = 4³, 3⁵ = 243 > 125 = 5³, and
  (n+1)ⁿ < nⁿ⁺¹ for every n ∈ {3..64} — so argmin over the grid of
  n^(−1/n) is n = 3. The certificate matches the grid scan at every
  prevalence: helps at {1/100, 1/50, 1/20, 1/10, 1/5, 1/4, 3/10}, fails
  at {1/3, 2/5, 1/2, 2/3, 9/10}. Boundary law T(3, q) = 1 ⟺ 3q³ = 1
  (no rational grid p lands on it).
- **T2 — PAIR-DOMINANCE (F2b)**: the difference polynomial in q,
  1/6 − q² + q³, equals (q − 2/3)²(q + 1/3) + 1/54 by exact
  coefficient match; grid floor 1/54 at q = 2/3 only.
- **T3 — the 2–4 DEGENERACY (F2c)**: 1/4 − q² + q⁴ = (q² − 1/2)² by
  exact coefficient match; pool 4 weakly dominates pool 2 at every grid
  q; the margin-0 knife-edge sits at q² = 1/2 (irrational — off every
  rational grid point), where 2⁴ = 4² makes q₂\* = q₄\* = 2^(−1/2) the
  common break-even. The family's one true zero, certified symbolically.

## Census and cost laws (Arm A = Arm B exactly, every rational)

Helping cells below the wall (n\*, T\*), Arm A closed form = Arm B
outcome tree exactly:

| p | n\* | T\* | ≈ |
|---|---|---|---|
| 1/100 | 11 | 21512792031541191037911/110000000000000000000000 | 0.195571 |
| 1/50 | 8 | 10712381930399/39062500000000 | 0.274237 |
| 1/20 | 5 | 1363901/3200000 | 0.426219 |
| 1/10 | 4 | 5939/10000 | 0.593900 (Dorfman's classic cell) |
| 1/5 | 3 | 308/375 | 0.821333 |
| 1/4 | 3 | 175/192 | 0.911458 |
| 3/10 | 3 | 2971/3000 | 0.990333 (last helping cell, wall's shadow) |

- **F4 hand world**: T(2, 1/2) = 5/4 exactly — both clean prob 1/4 → 1
  test, else → 3 tests; E = (1/4)·1 + (3/4)·3 = 5/2 per pool = 5/4 per
  item (both arms).
- **F5 degeneracies**: p = 0 → T(n) = 1/n; p = 1 → T(n) = 1 + 1/n;
  T(n, p) strictly increasing in p at fixed n on the identity grid.
- **Small-p sharpenings (reporting)**: T\* ≈ 2√p with n\* ≈ 1/√p —
  n\*(1/400) = 21, n\*(1/2500) = 51 (both reproduced).

## The above-wall anomalies — three, one family (drafter argmin slips)

The proposal's DECISION landing reproduced exactly on every value. But
three DISCLOSED above-wall SUMMARIES misidentify the argmin of T over a
pool grid at an above-wall prevalence — one conceptual family, none
touching a decision clause's truth:

- **A1 — the practical-grid min at p = 2/5.** Registration (R1 margin
  ledger / F3): "min over {2..8} of T(n, 2/5) = 419/375 at n = 3."
  Exact: the TRUE min over {2..8} is **T(8, 2/5) = 3463137/3125000 ≈
  1.10820 at n = 8**. 419/375 ≈ 1.11733 is T(3, 2/5), a LOCAL min, not
  the grid min. **Cause pinned**: above the wall T(n, 2/5) = 1/n + 1 −
  (3/5)ⁿ descends toward 1⁺ as n grows (the 1/n term dominates the
  vanishing (3/5)ⁿ), so the pool-grid minimum sits at the LARGEST n —
  not at n = 3, which is the argmin of n^(−1/n) (the wall-optimal pool
  that survives to the highest prevalence), a DIFFERENT optimization.
  The R1 damage clause STILL FIRES on the true min (1.10820 ≥ 21/20,
  margin ×1.0554 vs the disclosed ×1.0641) — the ruling is untouched.
- **A2 — the grid min at p = 1/3.** Registration (F3): "min over {2..64}
  of T(n, 1/3) = 28/27 at n = 3." Exact: the TRUE min over {2..64} is at
  **n = 64, ≈ 1.015625** (28/27 ≈ 1.03704 is T(3, 1/3), the small-n
  local min; the tail dips below it from n = 27 on). Same mechanism.
  This anchor is pure reporting (the "double knife-edge" note); no
  decision clause reads it. The n = 3 VALUE 28/27 and its status as a
  local min are both correct.
- **A3 — "the best batch above the wall wastes 11.7%."** Inherits the
  A1 slip: the best PRACTICAL batch at p = 2/5 is n = 8 wasting
  **10.82%** (T = 3463137/3125000), not 11.7% (which is n = 3's waste).
  Direction and order of magnitude stand.

The proposal's Q8 anticipated exactly this ("the more interesting
outcome — DISAGREES and pins the drafter's error, which the
pre-registered rule then rules on honestly"). The wall theorem itself
(n = 3 minimizes n^(−1/n)) is CORRECT and gated green; the census
anchors misapplied it to a fixed-prevalence pool-grid minimization.

## Falsifiability and the straddle edge

- **The free-pool-test world (C4)**: delete the 1/n term →
  T̃(n, p) = 1 − qⁿ < 1 for every n ≥ 2 and p < 1; at p = 2/5 the min
  over {2..64} is 0.64, the APPROVE clause fires, the verdict flips to
  **APPROVE** outright. The entire wall lives in one term — computed as
  a named reporting world, never a decision code path (F1 keeps 1/n in
  every decision T).
- **The p = 3/10 straddle**: T(3, 3/10) = 2971/3000 < 1 — pooling helps
  again one grid step below the wall cell (a 0.97% saving in the wall's
  shadow), the genuine NULL-straddle edge.

## The band-margin ledger (C5)

- R1 practical clause: **×1.0554** (true min 3463137/3125000 at n = 8 vs
  21/20 — corrected from the disclosed ×1.0641, which used the A1 slip).
- R1 strict clause: a theorem (T(n, 2/5) > 1 for every n ∈ {2..64}) with
  the honest disclosure that the infimum over unbounded n is 1 (grid-tail
  1.015625 at n = 64) — grid-bounded by design.
- R2 floor: **×1.00 at q = 2/3** — a registered knife-edge equality (the
  identity makes the floor exact); the R2 clause uses the ≥ 1/54 floor
  over the whole grid, which holds strictly off q = 2/3.
- R3: **×1.2783** (T\*(1/100) vs 1/4).
- T3's margin-0 cell q² = 1/2 is the family's one true zero, irrational,
  off every rational grid point (symbolic).
- **No decision clause rests on a margin-0 cell** (gated exact).

## Arm R — seeded screening careers (reporting-only)

Two-stage screening simulated over N items per cell; mean tests per item
beside the exact expectation (main seed 20261640 @ N = 100,000,
stability 20261641 @ N = 40,000; draw sentinel: exactly n Bernoulli
draws per pool, counted and asserted):

| cell (p, n) | main | stability | exact T |
|---|---|---|---|
| (1/100, 11) | 0.1953 | 0.1951 | 0.195571 |
| (1/10, 4) | 0.5964 | 0.5872 | 0.593900 |
| (2/5, 3) | 1.1175 | 1.1190 | 1.117333 |

The preview cell (1/10, 4) measured 0.59636 beside the exact 0.5939 (the
drafter's disclosed preview 0.591920 is a different implementation's
draw — Arm R is reporting-only and impl-dependent, no gate). Presentation
seed 20261642 read only by the row-shuffle leg; aux seed 20261643
asserted never read. No statistical gate rides any of this.

## Reproducibility

- One command, no flags, stdlib-only, hermetic (reads only its own
  `fixtures.json`); CPython 3.11 pinned and asserted.
- **1607 self-checks: 1607 passed, 0 failed** — no sim self-check is
  designed to fail; the three above-wall slips are ANOMALIES via C3
  (disclosed-anchor comparison), not gate failures. Exit 0. No
  fix-forwards after the runner landed — the first complete in-repo run
  of the committed pipeline is the accepted run.
- stdout + results.json **byte-identical across two full in-repo process
  runs** (external diff + sha256):
  - `results.json` `66e6e1f3532e0107c2a85d1f05f3e2605219d395b19a7352ecb58137e962c8fd`
  - `run-stdout.txt` `d261168e8b734be7821fc4966d25da0c3714e5d11bb8901ff27738cc026f3446`
- ~1.2 s/run.
- Seeds: 20261640 (Arm R main) / 20261641 (stability) / 20261642
  (presentation) are the ONLY RNGs constructed, in pinned order; aux
  20261643 never read. The drafter's registered set IS the session seed
  set (V077–V084 precedent; no new allocation); 20261634–639 stays the
  disclosed in-flight gap, unused. Registry high-water after this slice:
  **20261643** (reserved; highest read 20261642).

## Boundaries (named beside the ruling, per the registration)

- **Model basis (declared)**: PERFECT tests (no false neg/pos, no
  dilution) — the wall p\* is perfect-test-conditional; i.i.d. defects —
  clustering only moves the wall UP (the boundary is directional);
  TWO-STAGE Dorfman retest-all — adaptive protocols have a different T
  and a different wall; TEST COUNT the only cost — latency /
  sample-splitting named reporting.
- **The wall location is the model-dependent quantity, and its entire
  sensitivity is the 1/n term** (the falsifiability world). The T2/T3
  dominance identities are exact facts about the committed T functional
  and survive any cost rescaling.
- **The intent boundary**: the REJECT indicts the "batching always saves
  / small pools are safe" doctrine, never any specific repo edit; the
  consequence menu is where intent lives (routing is the manager's per
  Q-0260). Named follow-ups, none in scope: imperfect tests; adaptive
  halving/Sterling protocols; correlated defects; pool-size mixtures;
  the information-theoretic H(p) floor as reporting benchmark.
