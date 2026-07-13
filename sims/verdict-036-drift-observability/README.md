# verdict-036 · Drift-regime observability

Is the arm of VERDICT 024's drift-conditional trust rule readable from the
basket stream in time to act? An operating-characteristic sweep of 18
pre-registered cheap threshold detectors — statistic ∈ {trailing pinned-vol
annualized Sharpe SR_w, trailing up-share UP_w} × window w ∈ {63, 126, 252}
× threshold position λ ∈ {0.3, 0.5, 0.7} — on a pinned two-arm
regime-switching stream whose two states ARE V024's two committed arms
(state D basket-Sharpe 1.15, i.e. per-bar mean δ = 1.15/√252; state Z zero
drift; unit Gaussian noise; ρ-invariant by construction, asserted), scored
as trust-misallocation removed vs the EXACT best-static-prior baseline
min(π_D, π_Z) per cell: ΔE_oracle = min(π_D, π_Z) − E, win iff ≥ +0.10.
Answers idea-engine PROPOSAL 034 (control/outbox.md 2026-07-13T09:12:01Z,
idea `ideas/trading-strategy/xsec-drift-regime-observability-2026-07-13.md`,
main `eea4e5b`) — the standing ORDER 003 VENTURE rotation slot, round 5,
trading half. Fully hermetic: every fixture a pinned constant committed in
`fixtures.json` (the only file read, cross-checked at start); ZERO real
market bars; no dev-candidate evaluated on any data; the owner-gated
post-2026 protocol untouched.

World: 2-state Markov chain, geometric sojourns, 9 decision cells
(S_D, S_Z) ∈ {126, 252, 1008}² bars, stationary start, T = 2,595 bars,
scoring t ∈ [252, T), M = 1,000 paths per cell (main leg). Arm A is exact
and seedless (pure-window Gaussian/Binomial operating characteristics via
math.erf/math.comb, exact occupancies, static baselines, flip-count
expectations, the full ceiling table); Arm S is the seeded MC of the full
switching stream (seeds 20260772 main / 20260773 stability, M = 250, must
reproduce the ruling / 20260774 reporting / 20260775 aux — allocated
strictly above the P033 registry high-water 20260771). Gates, run invalid
on any failure: familywise-calibrated frozen-state control legs (36
points), exact occupancy/flip-count bands (closed-form variances), the swap
identity (exact in Arm A; SR-family statistical transpose in Arm S), the
ρ-invariance byte-identity, per-leg draw-count sentinels, twin
independently-written decision evaluators, two-process byte-identity,
CPython 3.11 pinned. Reporting-only legs (cannot flip): post-flip lag
tables, ΔE_always, the realized-sd SR variant, and the occupancy-graded bar
leg — V024's committed G6 panel machinery at its IID/ρ = 0.3 cell (M = 400
per point, φ_D ∈ {0, 0.25, 0.5, 0.75, 1} as one leading D-block), chained
to V024's committed anchors q99(G6) = 0.604101 (φ = 0) / 0.366902 (φ = 1),
machine-read @ `cd47c06`, via pre-pinned tail-count tolerances.

Decision (registered order): REJECT iff NO variant wins ≥ 3 of 9 cells
(checked FIRST) → APPROVE iff ONE variant (same statistic, w, λ) wins
≥ 7 of 9, stability-reproduced → NULL (the per-cell frontier is the pin,
flip axes named via per-axis pass shares).

## Run (one command)

```
python3 sims/verdict-036-drift-observability/drift_observability_sim.py
```

Exit 0 iff all self-checks pass. Deterministic: pinned seeds, pinned loop
order, one uniform per normal, no network, no git, no wall clock. Progress
goes to stderr only. ~3 min.

## Files

- `fixtures.json` — the pre-registration: every constant verbatim from the
  idea file, the decision rule with its evaluation order, gate tolerances
  with their SE arithmetic, and 15 intake-time decisions (committed BEFORE
  the runner — git history is the trail).
- `drift_observability_sim.py` — the runner (stdlib-only, single file).
- `results.json` — committed run output (byte-identical on re-run).
- `REPORT.md` — the verdict report (method label, gates, tables, ruling).
