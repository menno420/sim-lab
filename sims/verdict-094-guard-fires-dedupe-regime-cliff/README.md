# verdict-094 · guard-fires-dedupe-regime-cliff

The exact regime map of the substrate-kit guard-fires tail-scan dedupe.
Answers idea-engine PROPOSAL 081
(`## PROPOSAL 081 · 2026-07-16T07:10:30Z · status: sim-ready`, idea
`ideas/substrate-kit/guard-fires-dedupe-regime-cliff-2026-07-16.md` — the
round-17 fleet-backlogs rotation opener, substrate-kit re-tap): the shipped
mechanism (append one JSONL record per guard finding UNLESS the same key
sits in the last **S = 200 lines** with age **≤ W = 600 s**; verdict rows
exempt — always append, never keyed, yet slot-occupying; whole-file read,
parse capped at the tail) is a deterministic dynamical system, and its own
comfort sentence — "a burst larger than this simply dedupes less" — is
priced on all four sides. Six structure theorems, re-derived from scratch:
the NON-MONOTONE renewal law (p(c) = c·(⌊600/c⌋+1) — a 601 s checker
records exactly 1200/601 ≈ 2× more per day than a 600 s one), the CLIFF
with a rotating alibi (steady leak = max(0, F−200); the leaked identity
rotates with period F/gcd(F, F−200)), COMPOUNDING verdict displacement
(min(F, F−200+V) on the saturated region; exact orbits below it — (200,1)
ramps to 19/run and sustains exactly 14/run, 13× the one-for-one
intuition), the BREATHING boundary orbit (201, (1,1,199)×7, 1, 1 at
(201, 300)), the READ BILL ("bounded scan" bounds parses — 13,000 lines
read vs 2,000 parses on the leak scenario), and the TRUE SENTENCE (at the
fix's own design point re-runs append exactly 0), plus the three priced
repairs (S′ = 1000 relocation, keyed index, scan-off).

## Run (one command)

```
python3 sims/verdict-094-guard-fires-dedupe-regime-cliff/guard_fires_dedupe_regime_cliff_sim.py
```

Exit 0 iff all self-checks pass. Deterministic: stdout and `results.json`
are byte-identical across process runs (no wall clock, no paths, no
network, no git at run time). Stdlib only — this is a shipped-algorithm
deterministic-replay head (nearest method kin: P079's replay of a shipped
mechanism; P077's true-sentence-survives move); the model replays three
PINNED source behaviors (strict-`>` age boundary, last-S-LINES slot
accounting, suppressed-first call order) read from ~150 lines of vendored
source at the grounding HEAD — the source-semantics NULL axis prices
exactly that. CPython 3.11 pinned and asserted (Arms A/B are seedless
exact integer arithmetic; only reporting-only Arm R and the presentation
shuffle touch the pinned minor's `random` module).

## Layout

- `fixtures.json` — every registered constant verbatim from the PROPOSAL
  081 block / idea file, committed BEFORE the runner: the pinned source
  behaviors, the world conventions (uniform cadence, stable order, empty
  start, one-batch-per-run with the split control registered as
  load-bearing), the grids and scenario cells, the F3 census anchors, the
  typed contacts C1–C4, the Arm-R draw-order grammar with seeds
  20261718–721 and both registered preview triples, and the
  pre-registered decision rule. Sim-chosen realizations (the Arm-R census
  field definitions, the order-flip probe cells, the rotation-leg
  horizon, the naive-ts probe cell, the presentation-shuffle target) are
  disclosed as vacancy-derived fixtures, never match claims.
- `guard_fires_dedupe_regime_cliff_sim.py` — the three-arm runner.
- `results.json`, `run-stdout.txt` — the accepted run's committed outputs.
- `REPORT.md` — the verdict report (sha256 digests of the double run).

## Arms

- **Arm A** — seedless faithful tail-slice replay of the pinned mechanism
  (append-only `(key, t)` ledger; ONE scan per fire batch at batch start:
  whole-file read counted, parse capped at the last 200 lines, key
  visible iff a same-key line sits in the tail with age ≤ 600 strictly;
  verdict rows first, always, keylessly) + the closed forms on their
  proven domains (the renewal law, the cliff law, the saturated law, the
  rotation period, the quadratic read sum). DECISION-bearing; pure
  integer arithmetic.
- **Arm B** — INDEPENDENTLY-WRITTEN depth-arithmetic twin replay over a
  differently-shaped log: no line list — a global line counter plus
  per-key last-append registers; visibility decided by depth-from-end
  arithmetic (the most recent copy decides: older copies are both deeper
  and older). Tied to Arm A through the typed must-equal contacts:
  **C1** day counts == the closed renewal law ×9, **C2** V = 0 leak ==
  max(0, F−S) ×8 AND rotation first-repeat == 2 + F/gcd(F, F−S) ×4,
  **C3** Arm B == Arm A per-run sequences exactly on all 20
  compounding-region cells × 80 runs and all 13 saturated cells, **C4**
  lines-read == the closed quadratic sum (13,000) AND parse calls ==
  Σ min(len, S) (2,000).
- **Arm R** — seeded random scenario traces, REPORTING-ONLY (no
  statistical gate): per trace EXACTLY 4 `rng.randint` draws in
  registered order (F ∈ [1, 400], V ∈ [0, 8], c ∈ [60, 1200],
  R ∈ [2, 12]), one `random.Random` per seed. Seeds 20261718
  (N = 20,000) and 20261719 (N = 8,000) with registered preview triples;
  presentation shuffle 20261720 (presentation legs only); aux 20261721
  reserved and never read; draw-count sentinel exactly 4N.

Decision rule (registered order, evaluated by two independently-written
evaluators over an ENUMERATED boolean input set): REJECT → INVALID →
APPROVE → NULL, REJECT evaluated FIRST. Full grammar in `fixtures.json`.
