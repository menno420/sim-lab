# VERDICT 059 — Parrondo's paradox at a conservative discrete pin (idea-engine PROPOSAL 048)

Prices the folk law "two individually-LOSING games combine into a WINNER"
(Parrondo's paradox, the Harmer–Abbott capital-mod-3 structure) at the
registration's deliberately CONSERVATIVE integer-lattice pin — `EPS = 1/100`,
twice the textbook bias, so REJECT is live — per the registration
(PROPOSAL 048, idea-engine
`ideas/fleet/parrondo-losing-games-combine-2026-07-13.md` @ main 1218196).

Run: `python3 sims/verdict-059-parrondo-lattice/parrondo_sim.py`

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 048
  block / idea doc, committed BEFORE the runner.
- `parrondo_sim.py` — Arm A (DECISION: seedless exact `fractions.Fraction`
  3×3 stationary solve; `D_A`, `D_B`, `D_mix` as exact rationals; twin
  decision evaluators) + Arm B (VALIDATION: seeded MC capital stepping,
  seeds 20261329–332, N = 200,000/leg, exact draw sentinels) + the
  reporting-only side pins (residue distributions, critical-EPS sweep,
  periodic [A,A,B,B] comparator).
- `results.json`, `run-stdout.txt` — the accepted run (byte-identical across
  two process runs; sha256s in REPORT.md).
- `REPORT.md` — ruling, the exact drift table, Arm-B legs, boundaries.

Ruling: **approve** (REJECT checked first does not fire — `D_mix =
26673/4429850 ≈ +0.006021 > 0`; both isolated-loss gates hold; `D_mix ≥
1/1000` with the stability leg reproducing sign and margin). The paradox is
real and material at the pin, and the pin is the LAST surviving point of the
registered lattice — `EPS = 3/200` already kills it. Hermetic, stdlib-only,
CPython 3.11 pinned, ~0.2 s/run, 346 self-checks 0 failed.
