# Session — VERDICT 024 — xsec KEEP margins vs selection noise (idea-engine PROPOSAL 022)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-13 · verdict-024 slice-worker session
> Objective: settle idea-engine PROPOSAL 022 (control/outbox.md · 2026-07-13T03:02:28Z · status: sim-ready; idea `ideas/trading-strategy/xsec-keep-margins-selection-noise-2026-07-13.md`, the ORDER 004 rule-3 VENTURE rotation slot, round 2 — trading half per ORDER 033's "more strategies, more stocks, more indicators"). Build the fully hermetic pre-registered selection-noise calibration for the trading lane's promote-on statistic: J = 9 instruments × T = 2,595 daily bars, one-factor Gaussian panels r_{j,t} = μ_d + m_{s_t}·σ_d·(√ρ·f_t + √(1−ρ)·z_{j,t}), σ_ann = 0.30; 12 decision cells = vol model {IID, RSV 2-state Markov systemic vol (p_cc = 0.98, p_ss = 0.94, variance multipliers (0.6, 2.2), unconditional unit variance exact and asserted)} × ρ ∈ {0.0, 0.3, 0.6} × basket-Sharpe drift S_bh ∈ {0, 1.15}; M = 1,000 seeded panels per cell, `random.Random(20260727)`, pinned loop order; the lane's R3 momentum KEEP rule verbatim on the period frame (rebalance every 21 bars → 123 periods, warm-up 252 bars, 111 evaluation periods, rank by trailing L-bar total log return with ties by instrument index, hold top-k, 10 bp per-side cost on replaced names, zero-cost equal-weight basket benchmark, Δ = annualized period Sharpe ×√12 minus basket Sharpe); nested burden grids G1 = {L=63, k=2, momentum, equal} ⊂ G6 = the lane's own L ∈ {63,126,252} × k ∈ {2,3} ⊂ G24 ⊂ G96 (96 configs, one panel's 8 sorted rankings serving every config); per cell P := P(Δ_max(G6) ≥ 0.484) (best KEEP margin; P(≥ 0.130) reported alongside) and burden-bar quantiles {q50, q90, q99} of Δ_max(N) for N ∈ {1, 6, 24, 96}; analytic gates run-invalid-on-failure (k=9 identity Δ ≡ 0 to 1e−12, exchangeability pre-cost mean gate within 4 MC SE at S_bh = 0, √(9/k) vol-ratio gate within 2% on the IID/ρ=0.0/S_bh=0 cell, RSV normalization exact, CPython minor pinned, byte-identical stdout + results.json across two process runs); decision-stability leg seed 20260728 M = 250 must reproduce the ruling; reporting-only legs seed 20260729 (J = 18, cost c ∈ {0, 25 bp}, σ_ann = 0.15, all on the IID/ρ=0.3/S_bh=1.15 cell). Then issue exactly ONE of REJECT (P ≥ 0.10 in ≥ 6 of 12 cells — checked FIRST, the protect-owner-attention arm) / APPROVE (P ≤ 0.01 in ALL 12 cells) / NULL (anything else — flip axis named via per-axis APPROVE-pass shares and median P) per the decision rule registered in the idea file BEFORE any code existed, with the model-true boundary, the wider-null frequency bias, and the cost/benchmark pins stated as disclosed conservative directions, and the burden-bar table shipped on EVERY outcome. Hermetic: zero repo/network reads at run time, ZERO real market bars, no dev-candidate evaluated on any data, the owner gate untouched (the routing-hazard clause honored as a contract term).

## What happened

Built `sims/verdict-024-keep-margins-noise/` — a stdlib-only NUMERIC
SIMULATION (rung 1), fully hermetic: the sim reads exactly one file (its own
committed `fixtures.json` pre-registration, cross-checked at start) and
touches no repo state, network, or wall clock. The pre-registration (all
constants verbatim from the idea file, the pinned loop/draw order, the
decision rule with evaluation order, two hand-derived pin scenarios with
derivations, and TEN disclosed intake-time decisions) was committed BEFORE
the runner was written. Three transcription slips in the committed hand-pin
DERIVATIONS were caught by recomputing the closed forms and corrected in a
follow-up commit BEFORE any runner code existed (the git history is the
disclosure); the decision machinery was untouched. Profiled one panel first
(~16 ms), logged the projected runtime (~5 min/run vs the ~3 h wall), and
smoke-tested the full self-check battery on a throwaway seed before any
pinned-seed run.

**Run output summary:** `SELF-CHECKS: 69772 passed, 0 failed`, exit 0,
stdout + results.json byte-identical across two full process runs (external
diff), cpython-3.11 pinned, ~4.6 min per run, 15,500 panels. **Ruling: NULL
— the pre-registered expected-plausible conditional outcome, finalized.**
REJECT (checked first) fails at 2/12 hot cells vs the ≥6 bar (only the two
zero-drift ρ=0 cells: P = 0.154 IID / 0.169 RSV); APPROVE fails at 8/12 vs
the all-12 bar. **Flip axis: S_bh (drift), spread 0.667** — NOT the
proposal's expected RSV arm, which measured INERT (spread 0.000: volatility
clustering does not fatten the best-of-N Sharpe-margin tail at the swept
persistence/multipliers). The conditional rule: the lane's top KEEP margins
(+0.484/+0.480) clear best-of-6 selection noise in EVERY drift-matched cell
(P ≤ 0.004; matched q99(G6) = 0.399 < 0.484) — and the matched arm is the
one the lane's own committed basket Sharpe 1.147 selects; they are
selection-compatible only in the zero-drift stress arm at ρ ≤ 0.3. The
weakest KEEP margin (+0.130) is selection-compatible EVERYWHERE (P ≥ 0.057
in all 12 cells). Burden bar (ships on every outcome): max-over-cells q99
of Δ_max(N) = 0.798/0.918/1.054/1.132 for N = 1/6/24/96; drift-matched row
0.260/0.399/0.516/0.619. All four pre-registered analytic gates PASS;
stability leg (fresh seed, M=250) reproduces NULL with the same two hot
cells; J=18 "more stocks" measured slightly bar-LOWERING (q99 shift −0.041).

Slice boundary this cycle (the V015–V023 precedent): this session carries
the INTAKE 022 and VERDICT 024 control/ appends itself; control/status.md
stays coordinator-only and is untouched; control/inbox.md untouched
(manager-order file). The tail at append was VERDICT 023 (PROPOSAL 021,
landed @ fda94d0 by the sibling session while this sim was building) — the
branch was rebased onto it before the append, numbering unaffected, +2
offset preserved (P022 → V024), origin/main re-checked immediately before
the append. No @codex step — suspended per the outbox codex-line escalation
@ dedc12e. Born-red card and complete flip land in one push (the V018–V023
choreography). The owner gate honored end-to-end: zero real market bars, no
dev-candidate evaluated on any data, nothing scheduled.

## Run command

```
python3 sims/verdict-024-keep-margins-noise/xsec_selection_noise_sim.py
```

## 💡 Session idea

Recompute every hand-derived pin's closed form MECHANICALLY before
committing it: all three defects this session were transcription slips in
the pre-registration's own derivation constants (two Delta floats, one
multiset value), caught only because the float targets were re-derived from
the committed formula pieces inside the check itself (`assert
|formula - committed_float| <= 1e-12` runs BEFORE the evaluator
comparison). The portable rule: a hand pin should commit BOTH the formula
and its float, and the runner should assert their agreement as its own
self-check — then a slip in either is caught at smoke time instead of
poisoning the pinned run. Also exportable: when a spec pins a single RNG
stream across a whole leg (not per-panel seeds), draw normals via
`NormalDist().inv_cdf(rng.random())` rather than `rng.gauss()` — the
cached second value in gauss makes exact draw-count sentinels impossible,
and the one-uniform-per-normal discipline turns stream-position accounting
into exact integer arithmetic (verified here with fresh-Random advance
sentinels closing at 427,526,250 total uniforms across four legs).

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
