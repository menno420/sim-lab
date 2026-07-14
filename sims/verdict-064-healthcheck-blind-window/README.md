# VERDICT 064 — the healthcheck blind window (idea-engine PROPOSAL 053)

Prices the websites repo's shipped 6-hourly point-probe liveness net —
`.github/workflows/healthcheck.yml` @ websites `3076e9d`, cron
`17 */6 * * *` (the T = 360 min cell) — against its own committed framing
("standing liveness verification") and the backlog's committed hard window
("up to 6 hours until the cron probe fires"), under the pinned
probe-and-outage model, per the registration (PROPOSAL 053, idea-engine
`ideas/websites/healthcheck-blind-window-2026-07-14.md` @ main 39e35ec).

Run: `python3 sims/verdict-064-healthcheck-blind-window/healthcheck_blind_window_sim.py`

- `fixtures.json` — every registered constant verbatim from the PROPOSAL
  053 block / idea doc, committed BEFORE the runner; the disclosed
  fixture-level choices (K = 9 fire variates + coverage assertion, the
  19-draw scenario shape and CRN maps, the exact-variance SE convention,
  control N = 20,000, the sensitivity world order with the q-sweep under
  common random numbers, the E[L] closed-form method, the shipped-cell
  brute-force cross-structure, the twin evaluators, the draw sentinels,
  the cpython-3.11 pin) all pinned here first.
- `healthcheck_blind_window_sim.py` — Arm A (DECISION: seedless exact
  `fractions.Fraction` full-lattice enumeration over onset phase × fires,
  alone decision-bearing; independent second structure at the shipped
  cell: full 1024-outcome per-fire enumeration with exact integer weights
  must equal the product form on every DET(360, D) cell and WINDOW(360))
  + Arm B (validation: seed 20261349, N = 200,000 common-random-numbers
  scenarios evaluated at all five T cells, agreement gate 1/100 absolute
  AND 4·SE on all 315 reported cells) + the zero-noise identity control
  (seed 20261350, per-draw exactness: MISS(T,D) = (T−D)/T for D ≤ T,
  MISS(360,180) = 1/2, WINDOW(360) = 0, WINDOW(720) = 359/720) + the
  monotonicity theorem gates (DET in D; DET_mix in T; WINDOW in q, exact
  AND per-scenario CRN) + sensitivity reporting worlds (seed 20261351:
  q ∈ {0, 1/10}, delay {0}/{0..60}, short-/long-heavy mixes) + the
  stability leg (seed 20261352, N = 20,000, twin independently-written
  decision evaluators).
- `results.json`, `run-stdout.txt` — the accepted run (byte-identical
  across two process runs; sha256s in REPORT.md; every decision number an
  exact rational; includes the full per-φ conditional DET(360, D | φ)
  table and the E[L] × q table).
- `REPORT.md` — ruling, the DET × (T, D) cadence menu with runs/day cost
  column, WINDOW(T) tail, gates, sensitivity legs, drafter-reference
  comparison (exact agreement on every disclosed Fraction) and the three
  first-class anomalies, boundaries, and the five validity-gate answers.

Ruling: see REPORT.md (the decision rides Arm A alone, rules applied in
the registered order — REJECT checked first, bands 1/2 · 1/20 · 3/4 ·
1/100 exact).
Hermetic, stdlib-only, CPython 3.11 pinned, no wall-clock in any output.
