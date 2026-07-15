# verdict-084 — the fishing trophy-record quantization ceiling (INTAKE 071)

Prices idea-engine PROPOSAL 071's unpriced committed tension where it
lives: the superbot hub fishing game's trophy-record hook ("a cheap
long-tail retention goal", committed twice @ superbot `f8e2313`) against
the arithmetic it actually runs on. Every catch weight is
`max(0.01, round(nominal x U(0.65, 1.55), 2))` on the pinned 2-decimal
nominals (`round(0.18 x rank^1.65, 2)`), and the PB comparison is
STRICTLY greater (`fishing_workflow.py:267`) — so every species' record
chase is a record process over a FINITE atom grid with a reachable
ceiling, provably terminating instead of long-tailed. The sim computes
the exact atom census, ceiling probabilities, terminating-record law
E[lifetime PBs] = sum p_k / S_k, and cadence P(PB at t) = sum p_k
F_k^(t-1) as exact rationals for all 21 shore ranks, at the decision
cell (bare rod pull 1.00, level 7, shore — exact mix (1/r)/H21), judged
against pre-registered bands REJECT-first (modal ladder <= 20 rungs AND
p_ceiling >= 1/50; E[lifetime PBs] <= 4; P(PB at t) < 1/t for every
t in 2..50), then INVALID, then APPROVE (>= 100 rungs AND >= 1000-cast
horizon), then NULL on named axes. The runner is hermetic — it reads
ONLY `fixtures.json` (committed before the runner); zero repo/network
reads at verdict time; every committed constant was re-verified
firsthand at superbot `f8e2313` before the fixture was written.

## Run

```
python3 sims/verdict-084-trophy-record-quantization-ceiling/trophy_quantization_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and
`results.json` are byte-identical across process runs (verified by
external diff + sha256 — see REPORT.md). Stdlib-only, ~21 s. Every
decision number is an exact rational; the seeded arms (F fidelity, R
career traces) carry no statistical gate.

## Files

- `fixtures.json` — every registered constant verbatim from the
  PROPOSAL 071 block / idea file (the weight law and the 21 pinned
  nominals, the strict-> record rule, the decision-cell mix, the
  F-census anchors including the |A| table 17..2462, the rank-1 atom
  law, E_life(1), the kill-cast identity, the G5 hand world, the
  refinement/degeneracy/L1 battery, the decision bands, Arm F/R
  parameters, seeds 20261630-633, the print discipline), plus
  fixture-level conventions C1-C13 — committed BEFORE the runner,
  including the C12 strict refinement reading and its pre-verified
  first-decade miss.
- `trophy_quantization_sim.py` — four-arm runner: Arm A seedless
  closed-form interval census + suffix-sum record laws (exact
  Fractions; decision-bearing), Arm B INDEPENDENTLY-WRITTEN
  boundary-sweep census + explicit t-DP twin (exact-equal gated; the
  second decision evaluator recomputes from Arm B alone), Arm F the
  committed roll re-implemented verbatim (float round +
  random.uniform, seed 20261630; support equality gated on ranks
  {1, 2, 3, 21}, frequencies reporting), Arm R seeded career traces at
  the decision cell (main 20261631, stability 20261632, aux 20261633
  NEVER read; reporting-only).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, the full atom/ceiling/lifetime census, the
  T1/T2/T3 theorem verifications and the L1 sweep, the band-margin
  ledger and species sweep, the refinement battery with the two named
  anomalies, the career table beside the divergent continuous
  benchmark, the three consequence rows, and the twin-arm /
  byte-identity notes.
