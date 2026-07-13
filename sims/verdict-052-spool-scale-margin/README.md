# verdict-052-spool-scale-margin

> **Status:** `finalized` — VERDICT 052 (INTAKE 041), idea-engine PROPOSAL 041
> ("spool-scale go/no-go margin error budget", the standing ORDER 003
> FLEET-BACKLOGS rotation slot, round 7 — the first harvest from
> curious-research, the fleet's maker/3D-print seat).

Pre-registered hermetic error-budget sim of the one decision the
curious-research spool-weight-scale build exists to serve: START a print iff
F̂ ≥ Ĵ + M at the cited ±5 g scale resolution, margin grid
M ∈ {0, 5, 10, 15, 25, 40, 60, 100} g × three tare-knowledge regimes (R-OWN
measured tare / R-TABLE seeded brand table / R-GUESS control). RUNOUT =
P(run-out | started) and FORGONE = P(declined | feasible) as exact Fractions
in Arm A (seedless enumeration — the decision arm; net-error collapse gated
by an exact-equality spot-check against the direct product enumeration),
confirmed by Arm S (seeded MC, 200,000 scenarios/regime, seed 20261301,
common random numbers across the margin grid). Every constant verbatim from
the PROPOSAL 041 block (the source of truth). Details and the full ruling in
[REPORT.md](REPORT.md).

- **Run:** `python3 sims/verdict-052-spool-scale-margin/spool_margin_sim.py`
  (stdlib-only, hermetic — reads only its own `fixtures.json` — one command,
  no flags; exit 0; ~14 s; stdout + `results.json` byte-identical across two
  full process runs by external diff — no wall-clock in any output;
  cpython-3.11 pinned and asserted)
- **Pre-registration:** `fixtures.json` committed BEFORE the runner (git
  trail, PR #104 commits) — all error lattices with their sensitivity pairs,
  the four brand seeds, the job mix, the M grid, band constants
  (1/100 · 1/5 · 25 g · 15 g), the six-scenario hand fixture, seeds
  20261301–304 (new registry high-water 20261304), the two harvested doc
  lines verbatim @ curious-research `a9fd5fa`
- **Legs:** Arm A exact (decision — the ruling rides Arm A alone) · Arm S
  main seed 20261301 (200k/regime) · stability seed 20261302 (20k/regime,
  must reproduce the ruling) · reporting seed 20261303 (drift + sensitivity
  confirmations, 20k per cell — cannot flip) · aux 20261304 reserved, never
  read
- **Gates (all green, 15 self-checks 0 failed):** six-scenario hand fixture ·
  zero-error identity (exact zeros) · convolution spot-check (48 cells,
  exact equality) · monotonicity in M, both arms, 25 tables · arm agreement
  (max |ΔRUNOUT| 0.00095 ≤ 3/1000, max |ΔFORGONE| 0.00128 ≤ 1/100) ·
  draw-count sentinels · twin independently-written decision evaluators ·
  two-process byte-identity
- **Ruling:** **NULL — table-parity** (pre-registered axis ii). REJECT
  (checked first) does not fire: Feas(R-OWN) = the whole grid, M*(R-OWN) = 0.
  The APPROVE habit conjunct fails: M*(R-TABLE) = 0 < M*(R-OWN) + 15 — at
  the pinned spreads the seeded brand table clears the same bands at the
  same zero margin, so "beats the seeded table, every time" is overstated
  for go/no-go purposes. The habit's measured payoff lives in the R-GUESS
  control (M* = 60) and the drift row (R-TABLE M* moves 0 → 5), not in
  own-vs-table. The pre-priced bench probe (ten weighings + three empties)
  is the named next step.
