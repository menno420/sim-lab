# VERDICT 106 — Retry-amplified metastable overload collapse — REPORT

RULING: APPROVE (first-failing gate: none).

## What was tested
idea-engine PROPOSAL 093 → VERDICT 106. Claim: a lane pool at ~60% utilization becomes BISTABLE above a critical retry-aggressiveness r_c≈0.57 — a transient load blip tips it into a self-sustaining retry storm that persists after load returns to baseline (hysteresis) — and the fix is a retry BUDGET, not more lanes. Independent stdlib-only mean-field reimplementation (root-solve + stochastic map), not the proposal's dry-sim; gate outcomes match, digits are expected to differ.

## Pinned world
c=100 lanes; p(x)=p0+(1−p0)·σ(k·(u−θ)), u=x/c, p0=0.02, k=12.0, θ=1.05; balance F(x)=λ+r·p(x)·x−x. Pinned r=0.85, λ=60 (disclosed correction 70→60); retry-budget cap b=0.20; SEED_BASE=20260721; SIG=3.0; stochastic run N_REP=24 × T_STEPS=400, window 120, Poisson-style noise scale 0.5. Tolerances (pre-registered): COLD∈[55,70], HOT∈[380,420], WIDTH_TARGET=56 ±2.0, RC_TARGET=0.566 ±0.02, |HOT−x*|≤0.5, width-monotone slack 1e-6.

## Fixed points (pinned world)
Three roots of F: COLD x=61.311 (u=0.613, F′=−0.947, stable), MIDDLE x=104.748 (u=1.047, F′=+2.044, unstable), HOT x=400.000 (u=4.000, F′=−0.150, stable). HOT coincides with the collapsed mean-field x*=λ/(1−r)=400 to within 4e-7. Twin root-finders (bisection vs secant) agree to ≤1e-4.

## Gate margins
- R1 bistability: (a) exactly 3 roots, COLD & HOT stable, middle unstable — PASS. (b) seeded stochastic run: started COLD mean u=0.6146 ± 0.0035, started HOT mean u=3.9922 ± 0.0535, separation 308.8σ ≥ 3σ — PASS. R1 PASS.
- R2 hysteresis: adiabatic folds λ_up=78.070 (COLD fold), λ_down=22.679 (HOT fold), width=55.391 (|55.391−56|=0.609 ≤ 2.0); root-count twin λ_up=78.00, λ_down=22.75 (agree ≤0.5); coexistence at λ=60 confirmed (λ_down<60<λ_up and 3 roots). R2 PASS.
- R3 retry-lever: fold width monotone non-decreasing across r∈{0.30..0.95} (max downward drop 0.000000); operating-point margin (60−λ_down, clamped) monotone from 0; r_c=0.564155 where λ_down crosses λ=60 (|0.5642−0.566|=0.0018 ≤ 0.02); onset clean — every grid r below r_c monostable at the operating point, every r above bistable. R3 PASS.
- R4 knockout: retry-budget cap b=0.20 binds when r·p·x>b·λ=12. Uncapped: 3 roots, HOT present. Capped: 1 root at x=61.311 (u=0.613), HOT eliminated — monostable. R4 PASS.

## Twins & self-checks
Twin decision procedures (ordered if-chain + table scan) agree: APPROVE / first-failing gate None. Twin root-finders and twin fold-finders cross-check within tolerance. Self-checks 25/25 pass, including analytic-vs-numeric F′ at all three roots and in-process determinism.

## Reconciliation with the proposal
Convergent on every structural claim: bistability with COLD≈61 / HOT≈400 split by an unstable middle; hysteresis width ≈56 (measured 55.39 vs claimed ≈56; λ_up 78.07 vs ≈78.5, λ_down 22.68 vs ≈22.5); r_c≈0.564 vs claimed ≈0.566; retry-budget cap eliminates the HOT fixed point. r_c is the retry aggressiveness at which the pinned operating point λ=60 enters the coexistence window (λ_down(r)=60), matching the proposal's "~60% utilization becomes bistable above r_c" framing — the abstract saddle-node onset (any λ) sits far lower (~0.27) and is not the gated quantity. This is a CONFIRM of gate outcomes, not a digit-level reproduction; the stdout digest differs from the disclosed value by construction (independent implementation).

## Finding (non-gating)
The HOT branch is the retry-storm attractor: at u=4 essentially every attempt fails (p≈1) so inflow r·p·x≈r·x self-sustains at x=λ/(1−r)=400 regardless of the p0 floor. Adding lanes (raising c) rescales u but leaves the λ/(1−r) collapse intact — only a retry budget (cap on r·p·x) removes the second attractor. The op-margin 60−λ_down(r) is a reusable knob quantifying how deep a load trough must go before a stormed pool self-recovers.

## Digests
- results.json sha256 3a1cb3c6e69990f5c6d873e0e23883fac0d4c0e3b3842224277680e05220a6eb
- run-stdout.txt sha256 d87e1dc83b4e7a29ac2623e361ca3943d5739444f55a6090441e2f55414e5d96
- fixtures.json sha256 c475f3ec6bb5fa890b6344504bde4b57986447be219361efa0d1a3090e685336
Double run (delete results.json + run-stdout.txt, rerun) → byte-identical.

## Verdict
APPROVE. Retry-amplified metastable bistability, hysteresis (width ≈56), the monotone retry lever with onset r_c≈0.566, and the retry-budget knockout all reproduce independently on the pinned world; all four pre-registered gates hold; the claim is CONFIRMED.
