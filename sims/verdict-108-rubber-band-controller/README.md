# VERDICT 108 - catch-up rubber-band as a proportional feedback controller

> **Status:** VERDICT complete - APPROVE

Independent stdlib-only reverification of idea-engine PROPOSAL 095 (2026-07-17T12:06:59Z, sim-ready), offset +13 (P095 -> V108).

## Question

Is the engagement-maximizing catch-up-rubber-band gain **interior**? P095 models the catch-up boost as a discrete-time proportional feedback controller on the signed skill gap and claims engagement is **non-monotone** in boost gain k: a weak band lets the faster racer run away (decided-early boredom) while past the exact stability boundary k=2 the loop goes unstable and the winner **decouples from skill** (no-agency churn). The claim is that the engagement-maximizing gain is INTERIOR, that sensor delay d=1 **halves** the Jury stability boundary to k=1, and that a derivative stabilizer relocates the boundary to k_crit=2-2β exactly as discrete-control theory predicts.

## Pinned world

- Signed-gap iterator: `g(t+1) = g(t) + F - k·g(t-d) - β·(g(t)-g(t-1)) + ε(t)`, `ε ~ Normal(0, σ²)`
- `F = 2s` (skill gap s=0.5 → F=1.0), `σ=1.0`, `g0=0`, history 0 for negative indices; base world `d=0`, `β=0`
- K grid: `[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 1.9, 1.95, 2.05, 2.2]`
- `T=4000`, burn-in `B=1000`, `G_CAP=1e6` (divergence guard)
- Engagement metric `E = (lead-change rate)·(2·skill-fidelity − 1)`; `E := 0` on divergence
- `N_REPS=400` (main base sweep), `SEED=20260717`, sha256-keyed per-(d, k_index, rep) gauss streams, stdlib-only

## Model

- **📊 Model:** claude-opus-4-8 · high · verdict-sim

## Pre-registered rule

APPROVE iff ALL hold, evaluated in order R1 → R2 → R3 → R4:

- **R1** argmax mean-E is INTERIOR and beats BOTH the weak endpoint k=0.2 and the past-instability endpoint k=2.2 by ≥ 3σ
- **R2** every k>2 diverges; last-stable k=1.95 outsells first-above-2 k=2.05 by ≥ 3σ; measured Var(g) vs σ²/(k(2−k)) max rel-err < 5% on the stable arm; cliff bracket straddles the analytic boundary k=2
- **R3** with delay d=1 the divergence boundary HALVES to ≈1 and the engagement argmax stays INTERIOR across s ∈ {0.3, 0.5, 0.7}
- **R4** (a) skill-off s=0 (F=0) collapses engagement to ≈0; (b) β-sweep divergence onset matches k_crit=2−2β

## How to run

```
python3 rubber_band_controller_sim.py
```

Stdlib only. Regenerates `results.json` + `run-stdout.txt` + `fixtures.json` byte-identically on a double run; exits non-zero on twin disagreement / self-check failure / fixture drift.

## Outcome

`RULING: APPROVE - first-failing-gate=None`

- **R1 interior optimum:** PASS — argmax mean-E at k=1.2 (interior), E=0.22478±0.00035; beats weak k=0.2 (E=0.00204) by 632σ and past-instability k=2.2 (E=0) by 650σ (need ≥3σ).
- **R2 instability cliff + Var anchor:** PASS — diverged_frac=1.000 at k=2.05 and k=2.2; last-stable k=1.95 (E=0.15747) outsells first-above-2 k=2.05 (E=0) by 1231σ; Var(g) vs σ²/(k(2−k)) max rel-err 0.494% (<5%); cliff bracket last-stable k=2.0 / first-divergent k=2.05 straddles the analytic boundary k=2.
- **R3 delay d=1:** PASS — Jury boundary halves to ≈1 (bracket last-stable k=1.0 / first-divergent k=1.05, vs undelayed 2); engagement argmax interior at k=0.8; s-sweep argmax interior at all three s∈{0.3,0.5,0.7} (F∈{0.6,1.0,1.4} → argmax [0.6,0.8,0.8]).
- **R4 dual control:** PASS — (a) skill-off s=0 (F=0) collapses engagement: max|E|=0.016 (~0), skill-fidelity≈0.5 flat; (b) β-sweep divergence onset matches k_crit=2−2β (β=0→bracket(2.0,2.05), β=+0.5→(1.0,1.05), β=−0.5→(3.0,3.05)).

Twin evaluators agree (CONFIRMED / None). Self-checks 15/15 pass. Fixture anchor reproduced exactly. Byte-identical double run.

Non-gating finding: the independent engagement argmax lands at k=1.2, one grid-step below the proposal's disclosed k*=1.4 — both interior, both dominate the two endpoints by >600σ, so the R1 ranking gate is identical; the E(k) ridge is flat-topped across k∈[1.2,1.4].
