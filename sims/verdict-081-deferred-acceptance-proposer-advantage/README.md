# verdict-081 — the deferred-acceptance proposer advantage (INTAKE 068)

Prices idea-engine PROPOSAL 068's folk belief where it lives: "once you
require a STABLE two-sided matching the market is pinned — which side runs
the clearing procedure is at most a tie-break," measured against the stable
set's lattice structure on an exact census. n proposers x n receivers with
strict complete rankings; men-proposing deferred acceptance -> mu_M,
women-proposing -> mu_W; the stable set S obtained INDEPENDENTLY by
exhaustive blocking-pair testing of all n! matchings (GS's corner-landing
is a CHECKED claim, F6, never an assumption). Decision cell n = 3 (6^6 =
46,656 profiles, full census, every metric an exact Fraction); control
cells n = 1, 2; growth cells n = 4, 5, 6 (Arm R, seeded, REPORTING-ONLY).
Judged against pre-registered bands, REJECT-first (Delta(3) >= 1/5 AND
f(3) >= 1/5 AND M_prop(3) = 0 with M_recv(3) >= 1/100), then INVALID, then
APPROVE (Delta(3) <= 1/20 AND f(3) <= 1/20), then NULL on named axes.
Fully hermetic: the runner reads ONLY `fixtures.json` (committed before the
runner); zero repo/network reads at verdict time; every fixture constant is
copied verbatim from the PROPOSAL 068 block / idea file at idea-engine pin
`dc155cb`.

## Run

```
python3 sims/verdict-081-deferred-acceptance-proposer-advantage/deferred_acceptance_sim.py
```

CPython 3.11 pinned and asserted. Deterministic: stdout and `results.json`
are byte-identical across process runs (verified by external diff + sha256 —
see REPORT.md). Stdlib-only. Every decision number is an exact rational;
the only seeded arm (R) is reporting-only and its sole gates are the
draw-count sentinel and exact reproducibility.

## Files

- `fixtures.json` — every registered constant verbatim from the PROPOSAL
  068 block / idea doc (n grids, the decision bands {1/5, 1/20, 1/100}, the
  F3 census anchors, the F4 hand world, the F5 degeneracy slice, Arm-R
  parameters {200,000 main / 40,000 stability episodes per size}, seeds
  20261600-603), plus fixture-level conventions C1-C12 — committed BEFORE
  the runner existed.
- `deferred_acceptance_sim.py` — three-arm runner: Arm A seedless exact
  census (GS both ways + exhaustive stable-set enumeration + theorem
  checks + corner-lookup manipulation counts; decision-bearing), Arm B
  INDEPENDENTLY-WRITTEN twin (factorial-decode profile iteration, all-pairs
  stability, extremal matchings as the ENUMERATED set's coordinatewise
  men-rank min/max — never via GS; GS-free manipulation; second decision
  evaluator), Arm R seeded growth legs (n = 4/5/6; main 20261600, stability
  20261601, presentation 20261602, aux 20261603 NEVER read).
- `results.json`, `run-stdout.txt` — the accepted run's outputs.
- `REPORT.md` — ruling, the exact census surfaces, the three theorem
  verifications, the gap-localization decomposition, the manipulation
  asymmetry, Arm R growth, gates, anomalies, boundaries, the pre-registered
  consequence.

## Ruling

**REJECT** (see REPORT.md; the ruling token is issued by the twin
evaluators per the pre-registered order REJECT -> INVALID -> APPROVE ->
NULL). All three REJECT clauses clear at the decision cell exactly as
disclosed: Delta(3) = 7/27 >= 1/5 (1.30x), f(3) = 131/486 >= 1/5 (1.31x),
M_prop(3) = 0 exactly with M_recv(3) = 1/54 >= 1/100 (1.85x). Stability
does NOT pin the outcome: the proposing side captures a systematic,
market-size-born ordinal advantage the receiving side pays, it lives
ENTIRELY on the ~27% of markets with more than one stable outcome
(Delta|unique = 0 exactly, Delta|multi = 126/131), and the receiving side
is additionally the only manipulable side.
