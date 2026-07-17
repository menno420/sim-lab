# VERDICT 107 — REPORT

**RULING: APPROVE** — first-failing-gate: None. Verifies idea-engine PROPOSAL 094 (2026-07-17T09:48:38Z, sim-ready), offset +13 (P094 → V107).

## What was tested
Net revenue as a non-monotone function of refund-window length W: safety-net conversion lift (conv rises then saturates) traded off against refund cost, which step-jumps once the window arms wardrobe abusers at W_abuse=14. Claim: the net-revenue-maximizing window is INTERIOR (W=13), the day before the extraction threshold.

## Pinned world
- W grid (idx 0..8): `[0, 3, 6, 9, 12, 13, 14, 18, 30]` days
- `P=40.0`, `A=5000` product-views/rep
- `conv(W) = c0 + dC*(1 - e^{-W/tau})`; `c0=0.030`, `dC=0.030`, `tau=6.0`
- Per converted buyer: abuser w.p. `phi=0.08`; else dissatisfied w.p. `d=0.20`; else satisfied
- Honest dissatisfaction realized at `t~Exp(rho=1/9 per day)`; refund iff `t<=W`
- Wardrobe abuse refunds iff `W>=W_abuse=14` (the step discontinuity)
- Refunded sale → $0, kept → `P`. `NR/rep = P*(n_buyers - n_refunds)`
- `N_REPS=400`, `SEED=20260717`, string-keyed sha256-routed `random.Random` streams, stdlib-only

## Fixed points (baseline grid)
mean net revenue per rep ± SE:

```
 idx   W     conv    buyers   refunds       mean_netrev        SE
  0     0  0.03000    149.51      0.00        5980.4000   24.4978
  1     3  0.04180    209.13     11.01        7924.9000   27.5512
  2     6  0.04896    245.28     21.95        8933.4000   27.5687
  3     9  0.05331    266.14     30.75        9415.6000   29.9549
  4    12  0.05594    280.33     38.16        9686.7000   30.7291
  5    13  0.05656    282.85     39.34        9740.3000   30.2013
  6    14  0.05709    285.72     64.22        8859.9000   28.4200
  7    18  0.05851    293.74     70.23        8940.1000   28.3176
  8    30  0.05980    299.27     77.16        8884.4000   28.4294
```

argmax: idx=5 W=13 (interior)

## Gate margins
- **R1 interior optimum:** PASS — argmax W=13 (interior idx5); beats W=0 by 96.7σ, W=30 by 20.6σ (need ≥3σ).
- **R2 abuse cliff:** PASS — W=13 nets \$9740.30 vs W=14 \$8859.90 by 21.2σ despite HIGHER conversion at W=14 (0.05656→0.05709). The conversion gain is real; the +φ=0.08 wardrobe-abuse refund step swamps it.
- **R3 sweep robustness:** PASS — argmax interior at all 7 sweep points (φ∈{0.06,0.07,0.08,0.09,0.10}, ρ×{0.8,1.2}); φ=0.09 tips one grid point left to W=12 (still interior), rest W=13.
- **R4 dC=0 knockout:** PASS — removing conversion lift returns argmax to W=0 by 9.7σ, isolating the lift as the cause of the interior optimum (folk monotone restored).

## Twins & self-checks
Twin evaluators (if-chain + table) agree: APPROVE/None. Self-checks: 15/15 pass. MC-vs-analytic max rel-err 0.4108% (band 1.5%).

## Reconciliation with proposal
Proposal 094 dry-sim disclosed APPROVE (R1 93.3σ vs W=0 / 21.7σ vs W=30, R2 20.7σ, R3 argmax [5,5,4,5,5,5,5] all interior with a <1σ near-tie at φ=0.08, R4 9.2σ). This independent verifier uses aggregated exact-binomial draws (geometric-gap sampling) instead of the proposal's per-buyer Bernoulli loop — same semantics, distinct code path — so gate OUTCOMES match while the results digest deliberately differs from the proposal's c3cfdae… The margins above are this run's independent measurement (note the sweep tip at φ=0.09→W=12 mirrors the proposal's disclosed near-tie).

## Digests
- results.json sha256: 0d7cfe5c0157e22310f44c86ff79db3ca22deb39e9ace36814d3cd749141ac16
- run-stdout.txt sha256: 53ac627969291ecd01fac8405eb726ac82221973c7cf4588bcd71d3b871b84e2
- fixtures.json sha256: 7447b8d4faedc86437bbbb1c28384f54106ae7a9ba5a50404d39ddd8714c5895

(python3 refund_window_sim.py — stdlib only, double run byte-identical, Python 3.11.15)

## Verdict
APPROVE per the pre-registered R1→R2→R3→R4 rule; never softened.
