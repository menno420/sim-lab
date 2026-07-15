# VERDICT 077 — cascade independence quota (idea-engine PROPOSAL 064) — REPORT

## Ruling

**REJECT** (per the pre-registered rule applied in the registered order
REJECT → INVALID → APPROVE → NULL; both independently-written decision
evaluators agree REJECT/REJECT; every decision number a seedless exact
`fractions.Fraction`):

- **G(100, 7/10) ≈ 8.651255 ≥ 6** exact (1.44× over the line) — exact value
  in results.json (`decision.G`).
- **k\*(100, 7/10) = 15 ≥ 5** (3× over the line; unique argmax, ties = 1;
  runner-up k = 17 by ≈ 0.004925 — thin, disclosed, read by no decision
  clause).
- **e(k\*) = 481791730791717/14500000000000000 ≈ 0.033227 ≤ (1/2)·e(0) =
  9/116 ≈ 0.077586** exact (2.34×).

"Full observational transparency is not free": the shipped k = 0 regime pays
a permanent, N-independent herding tax — crowd accuracy caps at
1 − e(0) = 49/58 ≈ 0.8448 at p = 7/10 whether N = 25 or N = 400, locking in
after 100/29 ≈ 3.45 actions in expectation, while majority vote over the
same 100 independent signals would score ≈ 0.9999845 — and a mandated
blind-first quota materially beats it (V(100, 0) ≈ 83.9834 →
V(100, 15) ≈ 92.6346; expected wrong agents per 100 fall 16.017 → 7.365).

## Gates — ALL GREEN (139 self-checks, 0 failed, exit 0)

- **F1** — action table re-derived from likelihood ratios (p/q)^(lead+s) at
  every grid p + the hand p = 2/3 (own-signal at |lead| ≤ 1, herd-copy at
  |lead| ≥ 2, cascades never break); state-mass conservation exact at every
  DP step; every acc_i ∈ [0, 1]; V(N, N) = N·p at all grid p × N; the
  θ-relabeling SYMMETRY gate (a full mirrored DP with its own ruin solve
  reproduces every published V surface and e curve exactly).
- **F2** — (a) QUOTA-NULL: e and V identical for k ∈ {0, 1, 2} at every
  grid cell; (b) PARITY: e(2m+1) = e(2m+2) for every m ≥ 1 (k ≤ 120) at
  every grid p, and the finite-horizon strictness V(N, 2m+2) < V(N, 2m+1)
  at every grid cell for every m ≥ 1; (c) the harmonic identities and the
  KNIFE-EDGE decomposition exact for every m ≥ 1 at every grid p, reference
  e(2) − e(3) = 441/14500 at (7/10, m = 1) hit exactly.
- **F3** — e(0) = q²/(1 − 2pq) = 81/202, 9/58, 1/17, 1/82 across the grid;
  h at 7/10 = (237/580, 9/58, 27/580); lock-in 100/29; the p = 1 anchor
  (e = 0, V = N at every k, both arms).
- **F4** — hand world p = 2/3: h = (7/15, 1/5, 1/15), e(3) = 23/135,
  V(6, 3) = 350/81 (both arms).
- **F5** — p = 1/2 degeneracy: e(k) = 1/2 for every k ≤ 120,
  V(N, k) = N/2 at every (N, k), both arms.
- **F6** — Arm B (independently-written backward recursion + Gaussian ruin
  solve + Pascal pmf) exact-equal on every published number (all e curves,
  all 12 V surfaces, lock-ins, decision numbers, k\* argmaxes, decision-cell
  acc trajectories); the 2^12 census at N = 12 (every grid p, every k ≤ 12)
  equals BOTH arms exactly on V and the per-agent trajectories; k\* interior
  (max 109 ≤ 118); twin decision evaluators agree REJECT/REJECT; Arm-R draw
  sentinels exact (10,100,000 main + 2,020,000 stability = 1 + N per
  episode); aux seed 20261566 never read (constructor registry:
  [20261563, 20261564, 20261565]); stdout + results.json byte-identical
  across two full process runs; CPython 3.11 asserted.

## Reproducibility

One command, no flags: `python3
sims/verdict-077-cascade-independence-quota/cascade_independence_quota_sim.py`.
Two full process runs externally diffed — byte-identical. sha256:
`run-stdout.txt`
`3b627de2e07af8c8df2a6eee0dddb84bafef21674cda25d59420f7e08fd32f27`,
`results.json`
`3e0745aeccd1318e0e0347a341a1d4770e1d3daa409db35acd46f36415c35202`.
~2 m 24 s/run on CPython 3.11.15, stdlib-only, hermetic (reads only its own
`fixtures.json`). Seeds constructed: 20261563 (main), 20261564 (stability),
20261565 (presentation shuffle — read by the shuffled stdout cell listing
only); 20261566 reserved, asserted never read.

## Headline tables (floats; exact Fractions in results.json)

k\*(N, p) — ODD at every cell (the parity + strictness corollary):

| p \ N | 25 | 100 | 400 |
|-------|----|-----|-----|
| 11/20 | 9  | 33  | 109 |
| 7/10  | 7  | 15  | 29  |
| 4/5   | 5  | 9   | 15  |
| 9/10  | 3  | 5   | 7   |

G(N, p) = V(N, k\*) − V(N, 0):

| p \ N | 25 | 100 | 400 |
|-------|----|-----|-----|
| 11/20 | 0.4139 | 7.3513 | 69.9867 |
| 7/10  | 0.7402 | 8.6513 | 50.8877 |
| 4/5   | 0.3801 | 3.7539 | 20.2465 |
| 9/10  | 0.0905 | 0.7859 | 4.1973 |

Falsifiability behaved exactly as registered: the N = 25 cell lands
G ≈ 0.7402 ≤ 2 (one horizon step left of the decision cell is
straddle/mixed territory — the quota's value is horizon-born), the p = 9/10
column lands G ≈ 0.7859 at N = 100 (one signal-quality step up and the gain
clause fails), the p = 4/5 cell sits inside the straddle band at
G ≈ 3.7539.

Bounded-learning exhibit (reporting): crowd cap 1 − e(0) vs the
majority-of-N benchmark (C6) — 0.5990 vs 0.8413 (11/20, N = 100), 0.8448 vs
0.9999845 (7/10), 0.9412 vs ≈ 1 (4/5), 0.9878 vs ≈ 1 (9/10); expected
lock-in 3.96 / 3.45 / 2.94 / 2.44 actions. The herd wastes almost all of
the crowd's information, and it is individually rational:
acc_100(k = 0) ≈ 0.8448 > solo p = 0.7 — the fix needs a MANDATE.

IR wedge, exact (C10): sacrifice = Σ_{i≤15}(acc_i(0) − p) ≈ **1.6738**,
recovery = Σ_{i>15}(acc_i(15) − acc_i(0)) ≈ **10.3251**, identity
G = recovery − sacrifice asserted exact.

Knife-edge decomposition at 7/10 (first values): e(2m) − e(2m+1) =
441/14500 (m = 1), then per results.json
(`knife_edge_decomposition_decision_p`).

## Anomalies — first-class, never smoothed

**A1 (drafter-disclosure approximation, ruling-neutral):** the proposal's
disclosed IR-wedge numbers "sacrifice ≈ 2.2, recovery ≈ 10.8" are the
STEADY-STATE approximation (each quota member's forgone free-ride valued at
the N-independent cap 49/58: 15 × (49/58 − 7/10) ≈ 2.172) — the exact
counterfactual sums are 1.6738 / 10.3251, because transparent-world agents
1–15 have not yet reached the cap (agents 1–2 sit at p exactly; the cascade
locks in ≈ 3.45 actions in expectation, so the early free-ride is worth
less than the cap). The difference cancels in G exactly (both pairs satisfy
G = recovery − sacrifice ≈ 8.651); no decision clause reads either number.
Drafter comparison: 16/18 disclosed values reproduced from scratch
digit-for-digit (incl. the 43/86-digit exact decision rationals, the full
k\*/gain tables, e(15) exact, majority benchmark, V(100, 16)); the 2
mismatches are this A1 pair.

**Arm R drift: none found** — the reporting traces sit on the exact law
well within MC noise (main leg |wrong-casc err| ≈ 0.00036 at k = 0,
≈ 0.00037 at k = 15; mean-correct errs ≤ 0.0012 across legs; unabsorbed
frequency 0 at N = 100 in all 240,000 episodes, consistent with the exact
walk's ~10⁻¹⁹ tail); the C3 per-episode exactness cross-check (literal
LR-rule process ≡ walk-shortcut process on the same draws) passed on every
one of 240,000 episodes × 2 quota cells.

## Boundaries (pre-registered, ride the verdict)

- **Tie-break** — theorems are convention-conditional on FOLLOW-OWN-SIGNAL;
  the classic random tie-break is the named follow-up (same bounded-learning
  shape, different constants).
- **Action space** — binary actions ARE the cascade engine; continuous
  reports dissolve it; this verdict prices fixed binary-choice surfaces.
- **Information** — homogeneous known p, public quota indices; the quota is
  equivalent to publishing the first k signals; heterogeneity/hidden
  mechanisms are named follow-ups.
- **Objective** — unweighted known-horizon welfare; reweightings are
  reporting flavors, never the decision.

## Consequence (pre-registered REJECT branch, verbatim-faithful)

The folk rule "more visible history never hurts" retires with numbers; the
correction ships in two transferable lines: (1) wherever the fleet shows
CONCLUSIONS without EVIDENCE (recommendation-first asks, visible-approval
review chains, verdict-token-first summaries), publish the SIGNAL alongside
the conclusion — evidence-forward summaries restore full learning at zero
accuracy cost, because the cascade exists only while actions are coarser
than signals; (2) where only conclusions can be shown, blind the first
speakers — an independence quota sized ≈ k\*(N, p) and always ODD (the
parity theorem prices the even member at exactly zero long-run and strictly
below zero finite-horizon). The knife-edge theorem is the design lens: an
intervention on a stopping process has leverage only at the stopping
boundary — audit where a mechanism binds before pricing it. Routing is the
manager's per Q-0260; this repo edits no other repo.
