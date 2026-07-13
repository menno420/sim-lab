# verdict-020 · book-versioning

Book breadth vs versioning depth — fixed-budget allocation sweep for the
venture-lab book pipeline. Answers idea-engine PROPOSAL 018 (control/outbox.md
2026-07-13T01:15:34Z, idea
`ideas/venture-lab/book-versioning-breadth-depth-allocation-2026-07-13.md` @
`cb2b6ee`, landed via idea-engine PR #283): at a production-night budget B=12,
does the K-th VERSION of a book beat the next NEW title — swept over version
cost c ∈ {0.25, 0.5, 0.75}, version spread σ_v ∈ {0.2, 0.5, 1.0}, discovery
lottery σ_m ∈ {0.5, 1.5, 2.5}, and per publication mode: Mode P pick-best
(selection fidelity f ∈ {0.2, 0.6, 1.0}) and Mode A publish-all (audience
separation s ∈ {0, 0.5, 1}), K ∈ {1, 2, 3, 4, 6}. Fully hermetic (the
PROPOSAL 017 precedent): every fixture is a pinned constant in `grid.json`,
copied verbatim from the idea file; pre-registered bands and decision rule.

## Run (one command)

```
python3 sims/verdict-020-book-versioning/book_versioning_sim.py
```

Exit 0 iff all 4,144 self-checks pass AND the pre-registered validity gates
hold (Arm A/S agreement ≤ 1.5% on every f=1 cell; stability leg reproduces the
ruling). Deterministic — fixed seeds only (20260716 Mode P / 20260717 Mode A /
20260718 stability), no unseeded RNG, no network, no git, no wall clock, no
`hash()`. stdout and `results.json` are byte-identical across process runs
(verified by external `diff` of two complete runs). Arm A is seedless
quadrature; Arm S is pinned to CPython 3.11 (asserted at startup).
Runtime ~2 min.

## Files

- `book_versioning_sim.py` — stdlib-only driver: Arm A (Simpson quadrature of
  the order-statistic integral, `math.erf`), Arm S (seeded MC, M=20,000 per
  (mode, cell, K), pinned per-title draw order, disclosed unbiased
  control-variate estimators), the analytic diagnostic layer, hit-probability
  legs, the pre-registered decision rule, 4,144 self-checks.
- `grid.json` — the committed fixture: all constants verbatim from the idea
  file ({B, c, K, σ_v, σ_m, f, s, M, seeds, band constants}), the pinned loop
  order, the disclosed estimator formulas, the decision rule — committed with
  the sim, values registered in the proposal BEFORE any code existed.
- `results.json` — committed run output: both 81-cell grids (per-cell K\*, ΔR,
  per-K values, hit legs), Arm A slice, agreement gate, per-axis K\*≥2 shares,
  stability leg, ruling.
- `REPORT.md` — the finalizable verdict report (validity gate + the VERDICT
  020 recommendation).

## Verdict (summary — full report in REPORT.md)

**null** — the pre-registered honest straddle: the two publication modes give
OPPOSITE allocation defaults, so neither "always version" nor "always breadth"
is settled; the mode split itself is the citable finding.

- **Mode P (pick-best): breadth dominates.** K\*=1 in 69/81 = 85.19% of cells,
  median ΔR +0.0000; versioning pays only where cheap versions, wide spread,
  and perfect selection align (c=0.25, σ_v=1.0, f=1.0: K\*=3, ΔR ≈ +0.27) and
  never at f=0.2. σ_m is measured inert in Mode P (E[exp(L)]=1 by
  construction).
- **Mode A (publish-all): versioning dominates.** K\*≥2 in 72/81 = 88.89% of
  cells, median ΔR +0.4062, grid-median K\* = 6 (the swept top); at s=1 pure
  ticket arithmetic gives K\*=6 everywhere (ΔR +166.7%/+71.4%/+26.3% by c).
- **Ruling: NULL** per the pre-registered rule (APPROVE fails on Mode P,
  REJECT fails on Mode A — both margin-free). Named flip axes (tie-aware):
  Mode P {c, σ_v, f} (spread 0.3333 each); Mode A {c, σ_m, s} (spread 0.2593
  each); version cost c is the only axis on both frontiers.
- Arm S vs Arm A: max rel dev 0.240% (gate 1.5%, 135 checks), analytic K\*
  reproduced 27/27 on the f=1 slice; stability leg (M=2,000, seed 20260718)
  reproduces NULL with identical headline shares.
- Named next step (pre-registered NULL consequence): the two-version live
  probe — publish two versions of ONE existing-research book with disjoint
  audience keywords and measure whether draws separate (measures s in the
  wild).
