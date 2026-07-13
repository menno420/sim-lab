# VERDICT 055 — checkout pooling folk law at ρ = 9/10

**Ruling: APPROVE** (pre-registered rules applied in order, REJECT checked FIRST).

Serves idea-engine PROPOSAL 044 (`## PROPOSAL 044 · 2026-07-13T19:47:09Z ·
status: sim-ready`, `control/outbox.md` @ main 1bc22e8, landed via idea-engine
PR #339; idea doc
`ideas/fleet/checkout-pooling-single-line-2026-07-13.md` @ 3f38420; claim
idea-engine PR #340). Fully hermetic — the runner reads only its own
`fixtures.json`, every constant copied verbatim from the idea doc.

Run: `python3 sims/verdict-055-checkout-pooling/pooling_sim.py` (stdlib-only;
CPython 3.11 pinned and asserted; ~4 s; stdout + results.json byte-identical
across two full process runs by external diff; stdout sha256
`82585fdf62aa867ea64487abec91f0dfde9ac7c0c2745d246b7e80b64d0a7f2e`,
results.json sha256
`1634b098432f4c338ec6db080ce0a5c4a0b30102593a0999578da6052d261274`).

## The question

On a deliberately CONSERVATIVE discrete frame (c = 3 registers; Bernoulli
arrivals `randrange(35) < A`, at most one arrival per tick — burst-free;
low-SCV integer service pmf {2:3, 3:3, 4:2, 6:2}/10, mean 7/2, SCV = 41/245;
tick semantics completions → arrival → index-order starts; T = 20,000 with
warm-up 2,000 and drain-to-empty, cap 80,000), does ONE shared FIFO line
(POOLED) beat a line per register joined by a random label (SPLIT-RANDOM) by
≥ 2× on cohort mean wait at the showcase load A = 27 → ρ = 9/10 exactly? The
decision number is the median over M = 32 seed-20261313 runs of the per-run
common-random-numbers ratio R = Ŵ(SPLIT-RANDOM)/Ŵ(POOLED), exact Fractions.

## Decision

- Validity conjunct (both bands): 0 invalid of 32 main-leg runs (< 1/4) — PASS.
- **Median R (main) = 9017678143/967484332 ≈ 9.320749** (per-run R range
  ≈ 7.456 – 11.369; all 32 runs individually above 2).
- REJECT (checked FIRST) iff median R < 3/2: does NOT fire.
- APPROVE iff median R ≥ 2 AND the seed-20261314 stability leg reproduces:
  FIRES — stability (M = 16, 0 invalid) median R = 7786058125/841026576
  ≈ 9.257803 ≥ 2, same ruling through both twin evaluators.

Pooling doesn't just halve the identical customers' waits at ρ = 9/10 on this
conservative frame — it cuts them ≈ 9.3×. The mechanism, read off the table:
at SCV = 41/245 the POOLED 3-server system runs almost lean (mean cohort wait
≈ 1.54 ticks, p95 ≈ 6), while each split line is a single-server ρ = 9/10
queue whose waits stay large (mean ≈ 14.13, p95 ≈ 45); the conservative
choices cut the POOLED side's queueing even harder than the split side's, so
the measured ratio lands ABOVE the continuous-time anchor (≈ 3.3), not below.

## Cell table (per-cell medians; full per-run tables in results.json)

| leg | A | ρ | M (inv) | median R | Ŵ POOLED | Ŵ SPLIT-RANDOM | median R_JSQ |
|---|---|---|---|---|---|---|---|
| main | 27 | 9/10 | 32 (0) | **9.320749** | 1.543 | 14.132 | 1.156 |
| stability | 27 | 9/10 | 16 (0) | 9.257803 | 1.528 | 13.978 | 1.159 |
| reporting | 21 | 7/10 | 16 (0) | 11.576455 | 0.313 | 3.622 | 1.322 |
| reporting | 24 | 4/5 | 16 (0) | 9.700997 | 0.635 | 6.127 | 1.241 |
| reporting | 30 | 1 | 16 (0) | 3.990714 | 36.618 | 126.798 | 1.008 |

Reporting-only reads (cannot flip; did not): the JSQ informed-shopper column
nearly recovers pooling (median R_JSQ ≈ 1.16 at the decision cell — the folk
corollary "it's picking the short line" is mostly right on this frame); the
R(ρ) curve falls toward saturation (11.6 → 9.7 → 9.3 → 3.99 at ρ = 1, where
both systems drown — max drain end 20,623 < cap, all 16 saturation runs still
valid); no load-sensitivity flip (every non-saturation cell's median sits
above 2).

## Gates (all green; SELF-CHECKS: 1111 passed, 0 failed)

- 8-tick hand fixture exactly: POOLED (0,0,0,1,0,0) mean 1/6, SPLIT-RANDOM
  (0,3,0,4,0,0) mean 7/6, SPLIT-JSQ (0,0,0,1,0,0) mean 1/6 with routes
  (0,1,2,0,1,1), fixture ratio R = 7.
- Tick-engine cross-check: a literal tick-stepping reference implementation of
  the registered semantics reproduces the fast decision engines per customer
  (waits, routes, max queue, drain end, busy ticks) on the hand fixture AND
  run 0 of every (leg, cell), all three configurations.
- A = 0 control leg (M = 4): zero arrivals/starts/busy ticks, per-run draw
  sentinel exactly T.
- Work conservation, stream identity across configurations, cohort
  conservation, per-run + per-leg draw sentinels (T + 2·arrivals; main leg
  1,628,134 draws over 494,067 arrivals).
- Twin independently-written decision evaluators (Fraction comparisons vs
  pure-integer cross-multiplication) agree: (APPROVE, —) both.
- Pooled-dominance audit: Ŵ(POOLED) ≤ Ŵ(SPLIT-RANDOM) on every valid run —
  no anomaly line fired. Load-monotonicity audit: mean cohort wait
  non-decreasing in A across {21, 24, 27} for all three configurations —
  no anomaly line fired.
- Byte-identity: stdout + results.json identical across two full process
  runs (external diff); CPython 3.11 asserted; aux seed 20261316 never
  constructed (asserted).

## Boundaries (ride every citation)

- **Frame:** THIS discrete burst-free low-SCV FIFO no-jockeying frame only.
  The service-SCV sweep (same mean 7/2, fat tail, e.g. {2:8, 14:2}/10) is the
  named most-likely-to-flip follow-up.
- **Measurement:** "dramatically better" is operationalized as R ≥ 2 on cohort
  MEAN wait; p95 and the JSQ column ride reporting-only.
- **Load:** the decision is the ρ = 9/10 cell; the R(ρ) curve and the ρ = 1
  saturation cell are reporting-only.
