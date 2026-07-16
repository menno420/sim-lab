# VERDICT 097 — REJECT — the pooled rate that hides one confounded allocation (P084, simpsons-paradox-aggregation-reversal)

**Ruling: REJECT** (the folk rule "a treatment better in EVERY subgroup is better
overall" is wrong as doctrine the moment the subgroup allocation is confounded
with the subgroup baseline. On the pinned Charig et al. (1986) kidney-stone table
treatment A beats B in BOTH strata yet LOSES the pool by exactly 16/350 = 8/175 —
the reversal — because the pooled rate is a SIZE-WEIGHTED mean whose weights
belong to the ALLOCATION, and A over-loads the hard large stratum (263/350) that
B barely touches (80/350). The reversal is a single-cliff size-weighting effect
(pooled_A(x) strictly decreasing, one crossing of 289/350 at x*=184, real table
x=263 past it), and a common-weight STANDARDIZATION restores the true per-stratum
ordering, weight-invariant over four mixes) — per the pre-registered rule applied
in the registered order REJECT → INVALID → APPROVE → NULL (REJECT evaluated FIRST;
both independently-written decision evaluators agree REJECT/REJECT over an
ENUMERATED 16-row boolean predicate space; every decision number a seedless exact
`Fraction`/integer identity).

33 self-checks, 33 passed, 0 failed; exit 0 on the accepted run; < 1 s/run;
hermetic — seedless exact rational arithmetic in every decision leg, stdlib only,
zero repo/network reads at verdict time. stdout + results.json byte-identical
across two full in-repo process runs by external diff + sha256:

- `results.json` sha256 `7abe38549d01bc2abb30f535c351eabd40d02ad2200b58cdecfb187698c7eeee`
- `run-stdout.txt` sha256 `62686fc03de7b6a212979db8a2a0cf324328344b5651759ac320ada37ec2926a`

## The decision clauses (all exact)

- **The reversal is real (fires, checked not assumed).** A dominates B in EACH
  stratum by cross-multiplication — small 81·270=21,870 > 234·87=20,358, large
  192·80=15,360 > 55·263=14,465 — while pooled B beats pooled A (289/350 vs
  273/350). The naive "pooling preserves stratum ordering" claim is therefore
  refuted by a single exhibited counterexample.
- **The pivot is the allocation.** The reversal lives entirely in the weights,
  not the treatment ranking: standardizing both arms to A's own marginal
  (`a_marginal`) leaves A at 273/350≈0.7800 but drops B to ≈0.7320 — A wins the
  moment B is judged on A's exposure mix — and under B's marginal A rises to
  ≈0.8851. A wins every common-weight comparison.
- **The repair restores the truth (fires).** A common-weight standardization
  restores A > B on ALL four registered mixes {pooled_marginal, uniform,
  a_marginal, b_marginal}. Under the pooled marginal (357 small / 343 large)
  std_A=634983/762700≈0.83255 > std_B=6231/8000≈0.77887. Weight-invariance holds
  because A wins every stratum (collapsibility under a uniform effect sign).
- **APPROVE does not fire and is arithmetically excluded.** APPROVE would require
  a uniform stratum ordering to always survive pooled aggregation; the single
  exhibited reversal excludes it. Mutually exclusive with REJECT, as registered.

## Twin arms and typed contacts

Arm A (the pinned `Fraction` automaton — DECISION-bearing, seedless) and Arm B
(an INDEPENDENTLY-shaped twin: an integer roll-up of raw counts for the pooled
winner and an OPPOSITE-DIRECTION crossing walk descending from x=n_A for the
cliff) are tied through the typed must-equal contacts, all True on the measured
run:

- **C1 (pooled winner):** Arm-B raw-count pooled rates == Arm-A `Fraction`
  pooled rates (A=273/350, B=289/350).
- **C2 (cliff x*):** Arm-B descending-walk crossing == Arm-A ascending-sweep
  crossing == **184**.
- **C3 (standardization):** Arm-B common-denominator (std_A, std_B, A>B) ==
  Arm-A `Fraction` triple under the pooled-marginal mix.
- **C_margin / C_reversal:** the reversal margin (8/175) and the reversal flag
  agree across the two arms.

The twin decision evaluators (an if-chain scorer and an independently transcribed
table-driven scorer) agree on the ruling token over the FULL enumerated 16-row
boolean predicate space AND on the measured inputs — REJECT/REJECT.

## Margin ledger (typed, exact)

- **Per-stratum rates (A vs B), each an exact fraction:** small 27/29≈0.9310 vs
  13/15≈0.8667 (A>B); large 192/263≈0.7300 vs 11/16≈0.6875 (A>B). (81/87 reduces
  to 27/29; 234/270 to 13/15; 55/80 to 11/16 — A dominates each stratum.)
- **Pooled:** A=273/350=39/50≈0.7800, B=289/350≈0.8257 — B wins the pool.
- **Reversal margin (B−A):** 16/350 = **8/175** ≈ 0.04571, a strict positive gap.
- **The cliff:** pooled_A(x) strictly decreasing in x = #A-in-large-stratum,
  crossing 289/350 exactly ONCE at **x*=184** (boundary x=183 above / x=184 at-or-
  below); the real table sits at **x=263**, well past the crossing.
- **Standardization (pooled marginal):** std_A=634983/762700≈0.83255 >
  std_B=6231/8000≈0.77887, and A>B holds weight-invariantly over all four mixes.
  No tolerance anywhere — every comparison is exact rational.

## Falsifiability gates (were real)

- **F1 — integer cells:** every cell has 0 ≤ successes ≤ total. PASS.
- **F2 — per-stratum A dominance:** A > B in each stratum (the premise of the
  paradox). PASS.
- **F3 — pooled reversal:** pooled A < pooled B. PASS.
- **F4 — differential weighting:** A's large-stratum share ≠ B's large-stratum
  share (the allocation is confounded — without this there is no reversal to
  exhibit). PASS.
- **F5 — standardization well-defined:** every weight set has a positive weight
  sum. PASS.

Any F-gate failure would have routed the verdict to INVALID under the registered
precedence; none fired. The named NULL axes — estimand-weight (a same-signed
table where a positive weight flips the adjusted sign, which the same-sign
standardization does NOT claim to cover), model-arithmetic (a misread stratum
count moving the pooled gap and x* together), and witness-scope (existence of ONE
pinned reversal, not prevalence over an ensemble) — were all reachable and none
fired.

## Scope boundaries (stated, per the registration)

- **Estimand-weight boundary:** the standardization invariance is claimed ONLY
  for the same-effect-sign case (A wins every stratum). A same-signed table where
  a positive weight flips the adjusted sign would refute a general collapsibility
  claim; the head prices only the exhibited same-sign case.
- **Model-arithmetic boundary:** the arithmetic is exact and seedless; the ruling
  binds the pinned table as registered, not an executed external surface. One
  misread stratum count moves the pooled gap and the cliff x* together — the
  independently-shaped twin exists precisely to catch such a misread.
- **Witness-scope boundary:** the decision claim is existential and exact on the
  ONE pinned reversal — the head prices the EXISTENCE and exact structure of a
  single reversal, not a PREVALENCE over random tables. Prevalence rides only the
  reporting-only Arm R and carries no gate.

## Consequence hand-off (pre-registered; routing is the manager's per Q-0260)

This is a fleet-external pure-math head with NO lane consumer: the deliverable is
the rotation's seventeenth fleet-external domain-coverage row (a citable measured
verdict) plus a transferable aggregation-bias correction, fanned in to the fleet
manager (Q-0264). Per the proposal's pre-registered REJECT consequence,
paste-ready and recommendation-first (Q-0263.2): **(1)** never rank two POOLED
rates without checking whether the grouping variable is balanced across the arms
— a pooled rate is a size-weighted mean whose weights belong to the ALLOCATION, so
a confounded rollout / skewed sampling frame / uneven cohort mix can flip the sign
while every cohort agrees; **(2)** the reversal is a CLIFF (single allocation
threshold x*=184 of 350), so "the numbers are close, it won't matter" is exactly
wrong near it; **(3)** the repair is STANDARDIZATION and it is NOT free — it
requires RECORDING the confounder and reweighting to a common distribution, a
decision to instrument for the covariate before you need it. Transferable audit:
every fleet metric surface that pools a rate over a possibly-confounded grouping
(review-queue / backlog dashboards, any pass-rate roll-up over lanes / repos /
time-windows / container images) — "is this rate pooled over a confounded
grouping, and if so what is the standardized comparison?"

## Seeds

**V097 is SEEDLESS.** Every decision leg is exact seedless integer/`Fraction`
arithmetic. Arm R exists ONLY as a seeded, REPORTING-ONLY 2×2×2 census with no
statistical gate; its seeds **970 / 971 / 972** are LOCAL reporting-only constants
carried in `fixtures.json`, NOT a draw from the fleet seed ledger. This slice
consumes NO seed-ledger block — the next free block stays **20261730**, untouched
(inherited from the V096 baton). No seed touches any decision arm.
