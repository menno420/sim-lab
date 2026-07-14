# verdict-072 — plan-depth refill jitter (INTAKE 061)

Prices superbot's committed plan-queue inventory rule where it lives: the
Q-0164 bar "DEPTH >= the cadence — leave enough genuine buildable work to
reach the NEXT pass (~30 PRs of capacity)" against the committed cadence
(`STEP = 30`, trigger verbatim `latest // 30 > marker // 30`) and the
marker-reset-to-latest convention, under refill-lag jitter — at idea-engine
PROPOSAL 061's pinned model (window law W = 30 − ℓ_prev + ℓ_cur; consumption
Bernoulli(q); S ∈ {9, 20, 30, 33, 36, 39, 45} × q ∈ {3/5, 3/4, 9/10, 1} ×
lag mixes {L0, PROMPT, HEAVY}; decision cell S = 30, q = 9/10, L0). Fully
hermetic: the runner reads ONLY `fixtures.json` (committed before the
runner); zero repo/network reads.

## Run

```
python3 sims/verdict-072-plan-depth-jitter/plan_depth_jitter_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and `results.json`
are byte-identical across process runs (verified by external diff + sha256 —
see REPORT.md). ~18 s/run, stdlib-only.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 061
  block / idea doc, plus the fixture-level choices C1–C9 disclosed BEFORE the
  runner existed.
- `plan_depth_jitter_sim.py` — three-arm runner: Arm A seedless exact
  `fractions.Fraction` binomial tails + negative-binomial span sums over the
  lag-pair lattice (decision-bearing); Arm B independently-written
  queue-level DP event-walk twin (exact-equal on every published cell,
  powers the second decision evaluator); Arm R seeded REPORTING-ONLY
  mechanism trace of the literal counter/marker/trigger system (main
  20261381 at N = 100,000, stability 20261382 at N = 20,000, presentation
  shuffle 20261383; aux 20261384 NEVER read, asserted).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, per-conjunct results in registered order, theorems,
  anomalies, boundaries.

## Ruling

**REJECT** — all three pre-registered conjuncts fire at exact rationals: the
committed depth 30 dries in p_dry = 1101510756549069125820660830403305561487141/
6250000000000000000000000000000000000000000 ≈ 0.176242 ≥ 1/20 of cycles at
the pinned jitter; the honest 1%-safe depth is S* = 39 = cadence + 9 ≥ 33
(bracket p_dry(38) ≈ 0.018095 > 1/100 > p_dry(39) ≈ 0.008070); the expected
dry-PR span fraction ≈ 0.027816 ≥ 1/50. "Depth = cadence" is a
never-dry-IF-LATENESS-IS-STEADY rule, not a never-dry rule: the forgiveness
theorem holds EXACTLY (every constant lag gives p_dry(30) = 0 at every grid
q — the marker convention cancels steady lateness perfectly, E[W] = 30 on
every mix), the PROMPT mix holds the committed bar (p_dry ≈ 0.009538,
S* = 30), and at q = 1 the failure probability IS P(lateness grew): 19/50 /
1/4 / 25/64 on L0/PROMPT/HEAVY, distribution-free. The model retrodicts the
committed Q-0164 incident from first principles: at the old S = 9 horizon
the queue dries in ≈ 99.99993% of cycles with expected drained span
≈ 20.0000000003 PRs — dead on the harvested "drained the queue ~20 PRs
before each refill".

Headline anomaly (first-class, reported, ruling-neutral): the proposal
block's "dry consuming-arrivals ≈ 0.751 per dry cycle" mislabels the
quantity — 0.751 is the UNCONDITIONAL per-cycle expectation (the idea doc's
own "per-cycle" wording); conditional on a dry cycle the expected stranded
arrivals are 8202042300415/1924773766366 ≈ 4.261 — the average dry cycle
strands over four plan slices' worth of dispatch fires, not "most of one".
