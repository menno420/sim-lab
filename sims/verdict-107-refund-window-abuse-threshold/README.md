# VERDICT 107 - refund window as a conversion instrument

> **Status:** VERDICT complete - APPROVE

Independent stdlib-only reverification of idea-engine PROPOSAL 094 (2026-07-17T09:48:38Z, sim-ready), offset +13 (P094 -> V107).

## Question

Does the net-revenue-maximizing refund-window length W sit at an **interior** optimum? P094 claims net revenue is **non-monotone** in W: the safety-net conversion lift (`conv` rises then saturates) trades off against refund cost, which **step-jumps** once the window arms wardrobe abusers at `W_abuse=14`. The claim is that the optimum is INTERIOR at **W=13**, the day before the wardrobe-extraction threshold - conversion keeps rising past 13, but net revenue falls because the abuse cliff dominates the marginal conversion gain.

## Pinned world

- W grid (idx 0..8): `[0, 3, 6, 9, 12, 13, 14, 18, 30]` days
- `P=40.0`, `A=5000` product-views/rep
- `conv(W) = c0 + dC*(1 - e^{-W/tau})`; `c0=0.030`, `dC=0.030`, `tau=6.0`
- Per converted buyer: abuser w.p. `phi=0.08`; else dissatisfied w.p. `d=0.20`; else satisfied
- Honest dissatisfaction realized at `t~Exp(rho=1/9 per day)`; refund iff `t<=W` => `P=1-e^{-rho*W}`
- Wardrobe abuse refunds iff `W>=W_abuse=14` (the step discontinuity)
- Refunded sale -> $0, kept -> `P`. `NR/rep = P*(n_buyers - n_refunds)`
- `N_REPS=400`, `SEED=20260717`, string-keyed sha256-routed `random.Random` streams, stdlib-only

## Model

- **📊 Model:** claude-opus-4-8 · high · verdict-sim

## Pre-registered rule

APPROVE iff ALL hold, evaluated in order R1 -> R2 -> R3 -> R4:

- **R1** argmax mean-netrev is INTERIOR (idx != 0, != 8) and beats BOTH W=0 and W=30 by >= 3 sigma
- **R2** last-safe W=13 (idx5) outsells first-armed W=14 (idx6) by >= 3 sigma DESPITE higher conversion at W=14
- **R3** argmax stays INTERIOR across phi in {0.06,0.07,0.08,0.09,0.10} and rho x {0.8,1.2} (7 sweep points)
- **R4** with dC=0 (no conversion lift) argmax returns to W=0 by >= 3 sigma (folk monotone restored)

## How to run

```
python3 refund_window_sim.py
```

Stdlib only. Regenerates `results.json` + `run-stdout.txt` + `fixtures.json` byte-identically on a double run; exits non-zero on twin disagreement / self-check failure / fixture drift.

## Outcome

`RULING: APPROVE - first-failing-gate=None`

- **R1 interior-optimum:** PASS - argmax W=13 (interior), beats W=0 by 96.7σ and W=30 by 20.6σ (need ≥3σ)
- **R2 abuse-cliff:** PASS - W=13 nets $9740.30 vs W=14 $8859.90 by 21.2σ; conv 0.05656→0.05709 (higher at W=14)
- **R3 sweep-robust:** PASS - argmax interior at all 7 sweep points (φ→W13,W13,W13,W12,W13; ρ×0.8→W13, ρ×1.2→W13)
- **R4 dC=0 knockout:** PASS - argmax returns to W=0 by 9.7σ (folk monotone restored)

Twin evaluators agree (APPROVE/None). Self-checks 15/15 pass. MC-vs-analytic max rel-err 0.4108% (band 1.5%).
