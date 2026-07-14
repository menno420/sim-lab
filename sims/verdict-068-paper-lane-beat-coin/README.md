# verdict-068 — the paper lane's BEAT coin (INTAKE 057)

Prices trading-strategy's committed paper-lane grading grammar
(`docs/paper-lane-protocol.md` §7 cycle-window BEAT/MISS comparator, §9 A5/A6,
6 bps/side · $10,000 notional, all @ `d857e50ad7bc32bed5b2999cce16b4bf8a37246e`)
at idea-engine PROPOSAL 057's pinned model. Fully hermetic: the runner reads
ONLY `fixtures.json` (committed before the runner); zero repo/network reads.

## Run

```
python3 sims/verdict-068-paper-lane-beat-coin/paper_lane_beat_coin_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and `results.json` are
byte-identical across process runs (verified by external sha256 — see
REPORT.md). ~22 s/run, stdlib-only.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 057
  block / idea doc, plus the fixture-level choices C1–C9 disclosed BEFORE the
  runner existed.
- `paper_lane_beat_coin_sim.py` — dual-arm runner: Arm A seedless exact
  `fractions.Fraction`/integer lattice + binomial arithmetic (decision-bearing);
  Arm S seeded MC confirmation (seed 20261365, CRN across delta worlds);
  stability seed 20261366 (twin evaluators); reporting seed 20261367; aux
  20261368 never constructed.
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, per-conjunct results in registered order, boundaries.

## Ruling

**REJECT** — all four pre-registered conjuncts fire: (a) BEAT ⟺ R_F < 1 with
zero exceptions over the 1395-point lattice (both accountings, 0 sign flips,
0 ties); (b) B(NULL, COMMITTED) = 0.558905 ≥ 13/25; (c) exact NP power at
n = 8 is 0.040650 (critical count 8-of-8) < 1/2, n*₅₀ = 56 windows (5.00 yr),
n*₈₀ = 124 (11.07 yr); (d) Arm S confirms within the agreement gate on every
decision cell, stability leg reproduces through twin evaluators.
