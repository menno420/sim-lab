# Session — VERDICT 024 — xsec KEEP margins vs selection noise (idea-engine PROPOSAL 022)

> **Status:** `in-progress`
> 📊 Model: fable · 2026-07-13 · verdict-024 slice-worker session
> Objective: settle idea-engine PROPOSAL 022 (control/outbox.md · 2026-07-13T03:02:28Z · status: sim-ready; idea `ideas/trading-strategy/xsec-keep-margins-selection-noise-2026-07-13.md`, the ORDER 004 rule-3 VENTURE rotation slot, round 2 — trading half per ORDER 033's "more strategies, more stocks, more indicators"). Build the fully hermetic pre-registered selection-noise calibration for the trading lane's promote-on statistic: J = 9 instruments × T = 2,595 daily bars, one-factor Gaussian panels r_{j,t} = μ_d + m_{s_t}·σ_d·(√ρ·f_t + √(1−ρ)·z_{j,t}), σ_ann = 0.30; 12 decision cells = vol model {IID, RSV 2-state Markov systemic vol (p_cc = 0.98, p_ss = 0.94, variance multipliers (0.6, 2.2), unconditional unit variance exact and asserted)} × ρ ∈ {0.0, 0.3, 0.6} × basket-Sharpe drift S_bh ∈ {0, 1.15}; M = 1,000 seeded panels per cell, `random.Random(20260727)`, pinned loop order; the lane's R3 momentum KEEP rule verbatim on the period frame (rebalance every 21 bars → 123 periods, warm-up 252 bars, 111 evaluation periods, rank by trailing L-bar total log return with ties by instrument index, hold top-k, 10 bp per-side cost on replaced names, zero-cost equal-weight basket benchmark, Δ = annualized period Sharpe ×√12 minus basket Sharpe); nested burden grids G1 = {L=63, k=2, momentum, equal} ⊂ G6 = the lane's own L ∈ {63,126,252} × k ∈ {2,3} ⊂ G24 ⊂ G96 (96 configs, one panel's 8 sorted rankings serving every config); per cell P := P(Δ_max(G6) ≥ 0.484) (best KEEP margin; P(≥ 0.130) reported alongside) and burden-bar quantiles {q50, q90, q99} of Δ_max(N) for N ∈ {1, 6, 24, 96}; analytic gates run-invalid-on-failure (k=9 identity Δ ≡ 0 to 1e−12, exchangeability pre-cost mean gate within 4 MC SE at S_bh = 0, √(9/k) vol-ratio gate within 2% on the IID/ρ=0.0/S_bh=0 cell, RSV normalization exact, CPython minor pinned, byte-identical stdout + results.json across two process runs); decision-stability leg seed 20260728 M = 250 must reproduce the ruling; reporting-only legs seed 20260729 (J = 18, cost c ∈ {0, 25 bp}, σ_ann = 0.15, all on the IID/ρ=0.3/S_bh=1.15 cell). Then issue exactly ONE of REJECT (P ≥ 0.10 in ≥ 6 of 12 cells — checked FIRST, the protect-owner-attention arm) / APPROVE (P ≤ 0.01 in ALL 12 cells) / NULL (anything else — flip axis named via per-axis APPROVE-pass shares and median P) per the decision rule registered in the idea file BEFORE any code existed, with the model-true boundary, the wider-null frequency bias, and the cost/benchmark pins stated as disclosed conservative directions, and the burden-bar table shipped on EVERY outcome. Hermetic: zero repo/network reads at run time, ZERO real market bars, no dev-candidate evaluated on any data, the owner gate untouched (the routing-hazard clause honored as a contract term).

## What happened

(in progress — this line flips with the Status marker when the slice completes)

## Run command

```
python3 sims/verdict-024-keep-margins-noise/xsec_selection_noise_sim.py
```

## 💡 Session idea

(to be filled at completion)

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-022-casino-fairness.md`: complete and honest;
its exports are adopted here directly. (1) The one-push born-red choreography
is followed verbatim. (2) Fixtures-before-runner, including hand-derived pins
WITH derivations committed before code — reused (two pins: the
constant-plus-alternating zero-turnover panel; the alternating-leader
turnover/cost panel). (3) Its trace-replay twin + twin decision evaluators
pattern — reused (an independently written direct-summation strategy
evaluator replays strided panels; two decision evaluators must agree on
ruling, per-axis shares, and the flip axis). (4) Its draw-count accounting —
reused as an exact analytic count + fresh-Random(seed) advance sentinel; to
make it exact, normals are drawn as `NormalDist().inv_cdf(rng.random())`
(exactly one uniform per normal) instead of `rng.gauss()` (whose cached
second value makes the stream uncountable) — an intake-time decision
disclosed in fixtures.json. (5) Its smoke-test-the-self-checks-on-a-
throwaway-seed practice — followed before any pinned-seed run.
