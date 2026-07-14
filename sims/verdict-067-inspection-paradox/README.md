# VERDICT 067 — the inspection paradox at equal means (idea-engine PROPOSAL 056)

Prices the folk rule "a service averaging one arrival every μ minutes means a
random arriver waits μ/2" against the exact random-incidence law
ρ = E[W]/(μ/2) = E[X²]/E[X]² = 1 + CV², on the committed equal-mean schedule
grid (CLOCKWORK / JITTER / SPREAD / MEMORYLESS / BUNCHED, all mean exactly
μ = 10 min), per the registration (PROPOSAL 056, idea-engine
`ideas/fleet/inspection-paradox-wait-inflation-2026-07-14.md` @ ae0e038).

Run: `python3 sims/verdict-067-inspection-paradox/inspection_paradox_sim.py`

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 056
  block / idea doc, committed BEFORE the runner; the disclosed fixture-level
  choices (single RNG stream per leg with the per-cell
  intervals-before-landings reading, the uniform-only draw maps, the
  exact-variance SE convention with Var(W) = E[X³]/(3E[X]) − E[W]², the
  literal both-halves-on-both-metrics agreement-gate parse, the reporting-leg
  size, the twin evaluators, the CPython 3.11 pin) all pinned here first.
- `inspection_paradox_sim.py` — Arm A (DECISION: seedless exact
  `fractions.Fraction` moment arithmetic per cell; geometric via closed forms
  cross-checked against exact rational partial sums to K = 500 plus exact
  shift-identity tails; alone decision-bearing) + Arm S (confirmation: seed
  20261361, per stochastic cell K = 100,000 intervals then N = 200,000
  uniform landings with bisect waits, pinned cell order JITTER → SPREAD →
  MEMORYLESS → BUNCHED, geometric as count-of-Bernoulli(q)-trials) + F1–F5
  control gates + the registered agreement gate (1/100 relative AND 4·SE, on
  E[W] and on P(W > 10), per cell) + stability leg (seed 20261362,
  K = 20,000 / N = 50,000, twin independently-written evaluators) + reporting
  leg (seed 20261363, median/P90 rows) + draw-count sentinels + the RNG
  registry (aux 20261364 asserted never read).
- `results.json`, `run-stdout.txt` — the accepted run (byte-identical across
  two full process runs; sha256s in REPORT.md; every Arm-A number an exact
  rational; per-cell gate detail with all four sub-booleans committed).
- `REPORT.md` — ruling, the ρ × cell table, the exceedance grid, the
  rider-vs-operator table at BUNCHED, gates, the three first-class findings
  (under-powered registered gate; parse-dependent class; the disclosed
  stream-interpretation pin), drafter-reference comparison, boundaries, and
  the five validity-gate answers.

Ruling: see REPORT.md (rules applied in the registered order — REJECT checked
first; the class this run lands is INVALID, the registration's own
"controls misbehaving — report, no ruling" branch, fired by the Arm-S
agreement gate breaching on one cell by ordinary sampling noise; every
drafter-disclosed exact value reproduces from scratch in Arm A).
Hermetic, stdlib-only, CPython 3.11 pinned, no wall-clock in any output.
