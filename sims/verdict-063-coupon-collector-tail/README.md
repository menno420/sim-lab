# VERDICT 063 — coupon collector's tail (idea-engine PROPOSAL 052)

Prices the folk belief "once you've collected most of a random-draw set
you're basically done" — the uniform coupon collector's tail-cost fraction
φ(N) = H_m/H_N (the share of the expected total draws E[T_N] = N·H_N that
the LAST m = ⌈N/10⌉ items cost), over the pre-registered grid
N ∈ {20, 50, 100, 200} with decision cell N = 50, per the registration
(PROPOSAL 052, idea-engine `ideas/fleet/coupon-collector-tail-2026-07-14.md`
@ main cdf3e2e).

Run: `python3 sims/verdict-063-coupon-collector-tail/coupon_tail_sim.py`

- `fixtures.json` — every registered constant verbatim from the PROPOSAL 052
  block / idea doc, committed BEFORE the runner; the disclosed fixture-level
  choices (weighted-tier integer split, overshoot t* = ⌊2·E[T_50]⌋ = 449,
  the per-draw RNG primitive, the φ-hat ratio-of-means estimator +
  delta-method SE, the F5 enumeration range and control-leg count) all
  pinned here first.
- `coupon_tail_sim.py` — Arm A (DECISION: seedless exact
  `fractions.Fraction` harmonic sums, twin independently-structured
  derivations, alone decision-bearing; the inclusion–exclusion CDF for the
  F5 identity and the overshoot report; twin independently-written decision
  evaluators) + Arm S (confirmation: seed 20261345, 200,000
  draw-until-complete trajectories per cell, agreement gate 1/100 relative
  AND 4·SE on E[T_N] and φ) + gates F1–F5 (harmonic re-derivation incl.
  H_5 = 137/60 and H_10 = 7381/2520; linearity/stage accounting; the
  φ(m=N) = 1 and φ(m=1) = 1/H_N boundaries; monotonicity theorems; the
  small-N exact-CDF-vs-full-enumeration identity at N ∈ {2, 3} with
  E[T_2] = 3, E[T_3] = 11/2) + the stability leg (seed 20261346) and the
  reporting-only legs (seed 20261347: last-20% alternative, weighted
  rarity-tier collector; aux 20261348 reserved, never read).
- `results.json`, `run-stdout.txt` — the accepted run (byte-identical
  across two process runs; sha256s in REPORT.md; every decision number
  committed as an exact rational in results.json).
- `REPORT.md` — ruling, the φ(N) grid table, gates, sensitivity legs,
  drafter-reference comparison, boundaries, the five validity-gate answers.

Ruling: see REPORT.md (the decision rides Arm A alone, rules applied in the
registered order — REJECT checked first, bands 2/5 and 1/5 exact).
Hermetic, stdlib-only, CPython 3.11 pinned, no wall-clock in any output.
