# verdict-069 — rubric weight-robustness (INTAKE 058)

Prices the weight-robustness of the band partition induced by venture-lab's
shipped ideation rubric (weights Distribution 35 / Buildability 20 /
Launch-effort 15 / Speed 15 / WTP 15; bands "below ~3.0 = do not build;
3.0–3.5 = borderline, tight budget only; above 3.5 = best available") over the
published 7 × 5 per-criterion score table of the fresh 7-concept batch
(`docs/products/ideas-2026-07-13-night.md` blob `aa09f12` @ `a9e202d`) at
idea-engine PROPOSAL 058's pinned model. Fully hermetic: the runner reads
ONLY `fixtures.json` (committed before the runner); zero repo/network reads.

## Run

```
python3 sims/verdict-069-rubric-weight-robustness/rubric_weight_robustness_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and `results.json` are
byte-identical across process runs (verified by external sha256 — see
REPORT.md). ~2.5 s/run, stdlib-only.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 058
  block / idea doc, plus the fixture-level choices C1–C7 disclosed BEFORE the
  runner existed.
- `rubric_weight_robustness_sim.py` — dual-arm runner: Arm A seedless exact
  `fractions.Fraction` linear-fractional 32-vertex arithmetic (decision-bearing
  for the x\* clauses; powers gates F2/F3/F4); Arm S seeded uniform-jitter MC
  (main seed 20261369, N = 100,000/radius; stability seed 20261370,
  N = 20,000/radius; cross-seed agreement gate 1/50 absolute); reporting seed
  20261371 (Dirichlet worlds κ ∈ {100, 400}, never decision-bearing); aux
  20261372 NEVER read (asserted).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, per-conjunct results in registered order, boundaries.

## Ruling

**REJECT** — all three pre-registered conjuncts fire: p̂(1/10) on the main leg
= 0.224550 ≥ 1/10; Arm A's exact x\*₁ = 1/27 ≈ ±3.70% ≤ 1/20 (the sole
above-band concept leaves "best" through the 3.5 edge inside ±3.7% of weight
jitter); x\*₆ = 1/47 ≈ ±2.13% ≤ 1/20 (the knife-edge borderline floor). The
band partition is knife-edge fragile at the batch's own published numbers —
the honest unit of report is distance-to-edge (the x\* column), not band.
Five of seven concepts tolerate ≥ ±9% jitter: the fragility is a property of
the two knife-edge rows, not of rubric arithmetic as such.
