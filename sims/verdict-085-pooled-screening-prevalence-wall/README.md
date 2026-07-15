# verdict-085 — the pooled-screening prevalence wall (INTAKE 072)

Prices idea-engine PROPOSAL 072's batching folk belief ("pooling always
saves; small pools are the safe hedge") where it lives: the Dorfman
two-stage cost law **T(n, p) = 1/n + 1 − (1 − p)^n** (T(1) = 1), against
the three exact structure facts the belief denies — an integer-power-
certified prevalence WALL (p\* = 1 − 3^(−1/3) ≈ 0.3066, above which every
pool size strictly loses), an exact dominance identity making the pair-
pool never optimal (floor 1/54 at q = 2/3 exactly), and a margin-0
degeneracy tying pools 2 and 4 at their common break-even (2⁴ = 4²). All
decision arithmetic is seedless exact `fractions.Fraction` judged against
bands fixed before any code (REJECT first): the strict wall + practical
damage ≥ 21/20 at p = 2/5, the 1/54 dominance floor, savings ≤ 1/4 at
p = 1/100. The runner is hermetic — it reads ONLY `fixtures.json`
(committed before the runner); zero repo/network reads at verdict time.
Every model constant is invented-but-pinned in the PROPOSAL 072 block, so
the arms re-derive the whole surface from the pinned cost law with no
external grounding pin to re-verify.

## Run

```
python3 sims/verdict-085-pooled-screening-prevalence-wall/pooled_screening_wall_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and
`results.json` are byte-identical across process runs (verified by
external diff + sha256 — see REPORT.md). Stdlib-only, ~1.2 s. Every
decision number is an exact rational; the seeded Arm R carries no
statistical gate.

## Files

- `fixtures.json` — every registered constant verbatim from the
  PROPOSAL 072 block / idea file (the cost law, the pool/prevalence/
  identity grids, the decision cells p = 2/5 and p = 1/100, the REJECT
  R1/R2/R3 bands, the F1–F6 gates, the census anchors, the T2/T3
  identities and their knife-edges, the margin ledger, the Arm-R cells
  and seeds 20261640–643, the disclosed above-wall summaries), plus
  fixture-level conventions C1–C9 — committed BEFORE the runner,
  including C3 (disclosed-anchor mismatches raise first-class anomalies,
  never silent gates) and C4 (the falsifiability world is a named
  reporting demonstration, never a decision code path).
- `pooled_screening_wall_sim.py` — three-arm runner: Arm A seedless
  closed-form T(n, p) census + integer-power wall certificate +
  polynomial-identity gates + n\* search (exact Fractions;
  decision-bearing), Arm B INDEPENDENTLY-WRITTEN binomial outcome-tree
  recomputation of T with its own n\* search and its own wall check
  (q^n vs 1/n; exact-equal gated; the second decision evaluator
  recomputes from Arm B alone), Arm R seeded Monte-Carlo screening
  careers at (p, n) ∈ {(1/100, 11), (1/10, 4), (2/5, 3)} (main 20261640
  at N = 100,000, stability 20261641 at N = 40,000, presentation shuffle
  20261642, aux 20261643 NEVER read; reporting-only).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, the wall/identity/census surface, the three
  structure theorems verified as gates, the margin ledger, the three
  named above-wall anomalies (one family), the falsifiability world and
  the p = 3/10 straddle edge, the Arm-R traces beside the exact
  expectations, and the twin-arm / byte-identity notes.
