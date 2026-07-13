# VERDICT 060 — the magnet press-fit band (idea-engine PROPOSAL 049)

Prices the effector-mount magnet tool's shipped, never-printed press-fit
interference default — `magnet_fit = 0.15` mm DIAMETRAL, its own comment
claiming "0.10-0.20 = a firm press-fit on most printers" (curious-research
`projects/effector-mount/magnet_tool.scad` @ a9fd5fa, never rendered by its
own header) — against the SAME repo's tolerance-test-coin band semantics,
over a pinned integer-lattice printer population, per the registration
(PROPOSAL 049, idea-engine
`ideas/fleet/magnet-press-fit-band-2026-07-13.md` @ main b77beca).

Run: `python3 sims/verdict-060-magnet-press-fit-band/magnet_fit_sim.py`

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 049
  block / idea doc (harvested lines quoted verbatim @ a9fd5fa), committed
  BEFORE the runner.
- `magnet_fit_sim.py` — Arm A (DECISION: seedless exact full enumeration of
  the 41 × 11 × 21 = 9,471-cell lattice per grid F, every probability an
  exact `fractions.Fraction`, run twice in-process and identity-checked;
  twin independently-written decision evaluators) + Arm B (VALIDATION:
  seeded MC, N = 200,000 common random numbers across all six F, seeds
  20261333–336 only, exact draw sentinels) + the controls (zero-noise
  identity at exact 1s, both monotonicity theorems, the per-cell agreement
  gate) + the reporting-only legs (DROP/UNSEAT split, FAIL_glue, the per-H
  conditional curve, ten sensitivity worlds, the remedy-direction flag).
- `results.json`, `run-stdout.txt` — the accepted run (byte-identical across
  two process runs; sha256s in REPORT.md).
- `REPORT.md` — ruling, the exact FAIL × F table, gates, sensitivity table,
  boundaries.

Ruling: **reject** (REJECT checked first FIRES — `FAIL(15) = 145/861 ≈
0.168 > 1/10`; even the grid-best cell F = 10 fails at `40/287 ≈ 0.139`, so
at the pinned population width NO universal default is honest and the fit
line's "on most printers" claim retires in favor of the repo's own
calibrate-first coin doctrine). The default's failure mass sits UNSEAT-side
(`125/861 ≈ 0.145` vs DROP `20/861 ≈ 0.023`) — the expensive, non-glue-fixable
direction. Hermetic, stdlib-only, CPython 3.11 pinned, ~1.2 s/run,
43 self-checks 0 failed.
