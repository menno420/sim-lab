# verdict-032 · adaptive-versioning (early signal)

Adaptive versioning on early signal — does a two-stage produce → observe →
version policy beat VERDICT 020's mode-conditional static fork? Answers
idea-engine PROPOSAL 030 (control/outbox.md 2026-07-13T07:25:14Z, idea
`ideas/venture-lab/adaptive-versioning-early-signal-2026-07-13.md`, landed via
idea-engine PR #298) — the ORDER 003 VENTURE rotation slot, round 4 (the books
half): the parent verdict's own "What it did NOT settle" names this head
verbatim ("**Adaptive K.** Static quota only; per-title adaptation on early
signal is a named follow-up, not scope creep").

Model: V020's production night inherited VERBATIM (B = 12, quarter-unit
integer budget B4 = 48; version cost c ∈ {0.25, 0.5, 0.75}; θ ~ N(0,1);
version quality θ + ε, ε ~ N(0, σ_v²), σ_v ∈ {0.2, 0.5, 1.0}; revenue
exp(q + L), L ~ N(−σ_m²/2, σ_m²) so E[exp(L)] = 1 exactly, σ_m ∈ {0.5, 1.5,
2.5}; Mode P pick-best f ∈ {0.2, 0.6, 1.0}; Mode A publish-all s ∈ {0, 0.5,
1}) + ONE new axis: early-signal noise σ_e ∈ {0.25, 1.0} on y = θ + ε_1 + η
read on a title's first version — 324 decision cells. Policies: AD(ω),
ω ∈ {0.5, 0.75} (stage 1 round(ω·B) one-version titles, stage 2 remaining
budget as extra versions by y-descending round-robin passes, K_cap = 4) vs
static S(K), K ∈ {1, 2, 3, 4, 6} (integer-night realization of V020's
fractional T_eff). Metric: mean night revenue per unit budget, M = 8,000
nights per (cell, policy), CE/CV estimators per the V020 disclosure (formulas
committed in `fixtures.json`), per-leg MC SE shipped. Comparisons per
(cell, ω): Δ_cond vs the V020-conditional default (Mode P K=1 / Mode A K=6)
and Δ_or vs the in-cell static oracle max_K R_S(K).

Decision (registered order, REJECT first): REJECT iff ∀ω, both σ_e:
median-over-cells Δ_cond ≤ +0.02 in BOTH modes → APPROVE iff ∃ ONE ω with
median Δ_cond ≥ +0.10 in both modes at both σ_e AND Δ_or ≥ −0.02 in ≥ 80% of
cells in all four mode×σ_e quadrants, stability-reproduced → NULL (flip axis
named). Gates, run invalid on any failure: the K=1 analytic identity
exp((1+σ_v²)/2) exact in both modes, Mode A s=1 additivity exact, the Mode P
f=1 static slice equal to V020's 45 committed Arm A quadrature values, the
CHAINED ANCHOR (fresh-seed per-title-expectation leg reproducing V020's
committed ruling row within tolerances pre-checked ≥ 2.5σ in the fixtures
BEFORE any run), and the aux signal-degeneracy self-check (pure-noise y ≡
uniform-order allocation). Reporting-only (cannot flip): B = 6, K_cap = 6,
the perfect-signal σ_e = 0 upper bound, discarded-budget fractions.

## Run (one command)

```
python3 sims/verdict-032-adaptive-versioning/adaptive_versioning_sim.py
```

Exit 0 iff all self-checks pass AND every pre-registered gate holds.
Deterministic — fixed seeds only (20260760 main / 20260761 stability M=2,000 /
20260762 reporting / 20260763 aux — strictly above the P029 registry
high-water 20260759), one uniform per normal (`NormalDist().inv_cdf`),
draw-count sentinels at the RNG API, no network, no git, no wall clock, no
`hash()`. stdout and `results.json` byte-identical across process runs
(verified by external `diff` of two complete runs). CPython minor pinned to
3.11 (asserted at startup). Runtime ~7 min.

## Files

- `fixtures.json` — the pre-registration: every constant verbatim from the
  idea file, the V020 anchor row + 45 Arm A values quoted verbatim, estimator
  formulas, pre-checked ≥ 2.5σ tolerances with derivations, 18 disclosed
  intake-time decisions — committed BEFORE the runner.
- `adaptive_versioning_sim.py` — the runner (stdlib-only, single file):
  night engines for both modes, the analytic quadrature layer (parent's
  I(K,σ) inherited verbatim), all gates, twin decision evaluators.
- `results.json` — committed run output (byte-identical on re-run).
- `REPORT.md` — the verdict report (method label, gates, tables, ruling).
