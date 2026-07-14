# VERDICT 061 — kill-clock horizon (idea-engine PROPOSAL 050)

Prices the venture products lane's shipped **T+14 zero-sale kill clock**
against the lane's own two OTHER committed clock values — the T+7 checkpoint
and the 30-day signal window (harvested SECONDHAND with the double pin:
venture-lab `be6c75d` via idea-engine outbox `763b19e`; the lane's evidence
line "0 organic sales across 7 click-queued products") — as a
censored-observation renewal problem: expected proven-product graduations
per 90 slot-days, over the pre-registered 3-prior (SKEPTIC/NEUTRAL/HOPEFUL
dead-share pmfs) x 3-build-downtime (B ∈ {2, 5, 10}) grid, per the
registration (PROPOSAL 050, idea-engine
`ideas/venture-lab/kill-clock-horizon-2026-07-13.md` @ main 3b9b26c).

Run: `python3 sims/verdict-061-kill-clock-horizon/kill_clock_sim.py`

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 050
  block / idea doc (the harvested kill-clock family and evidence line quoted
  with their double pin and the quoted access denial), committed BEFORE the
  runner.
- `kill_clock_sim.py` — Arm A (DECISION: the registered seedless exact
  `fractions.Fraction` renewal DP, alone decision-bearing, reproduced by an
  independently-structured bookkeeping DP as identical rationals; twin
  independently-written decision evaluators) + Arm S (confirmation: seeded
  MC, N = 200,000 per (cell, clock), pinned p-then-daily-trials draw order,
  seeds 20261337–340 only, exact draw sentinels) + gates F1–F5 (pmf
  normalization; p = 0 / p = 1 point-mass identities; truncated-geometric
  identity; the 31/16 hand world; B-monotonicity, all-dead zeros with
  kills ≡ renewals, exact slot-day accounting) + the reporting-only legs
  (kills / idle days / wasted graduations, per-p split, H ∈ {60, 180},
  grid P′, graduation-blocks-slot world, margin sweep m ∈ {1/50, 1/10}).
- `results.json`, `run-stdout.txt` — the accepted run (byte-identical across
  two process runs; sha256s in REPORT.md; every decision number committed
  as an exact rational in results.json).
- `REPORT.md` — ruling, the 9 x 3 G table with the D column and directions,
  gates, sensitivity worlds, drafter-reference comparison, boundaries.

Ruling: see REPORT.md (the decision rides Arm A alone, rules applied in the
registered order — REJECT checked first, margin m = 1/20 exact). Hermetic,
stdlib-only, CPython 3.11 pinned, no wall-clock in any output.
