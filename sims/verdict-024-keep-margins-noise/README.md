# verdict-024 · keep-margins-noise

Are the trading lane's R3 momentum KEEP margins (+0.484 / +0.480 / +0.130
stitched-OOS Sharpe over the equal-weight basket's 1.147) bigger than what
best-of-grid SELECTION alone hands a momentum-FREE market of the lane's
shape — and how fast must the shortlist bar rise as ORDER 033's "more
strategies, more stocks, more indicators" multiplies the config count N?
Answers idea-engine PROPOSAL 022 (control/outbox.md 2026-07-13T03:02:28Z,
idea `ideas/trading-strategy/xsec-keep-margins-selection-noise-2026-07-13.md`,
landed via idea-engine PR #288, main `1c6313c`) — the ORDER 004 rule-3
VENTURE rotation slot, round 2, trading half. Fully hermetic per the
PROPOSAL 017/018/019/020/021 precedent: every fixture is a pinned constant
committed with the sim, zero repo/network reads in the verdict session,
ZERO real market bars, no dev-candidate evaluated on any data, the
owner-gated post-2026 protocol untouched (the routing-hazard clause honored
as a contract term).

Model: J = 9 instruments × T = 2,595 daily bars, one-factor Gaussian panels
r_{j,t} = μ_d + m_{s_t}·σ_d·(√ρ·f_t + √(1−ρ)·z_{j,t}), σ_ann = 0.30;
12 decision cells = vol model {IID, RSV 2-state Markov systemic vol
(p_cc = 0.98, p_ss = 0.94, variance multipliers (0.6, 2.2), unconditional
unit variance exact and asserted)} × ρ ∈ {0.0, 0.3, 0.6} × basket-Sharpe
drift S_bh ∈ {0, 1.15}; every cell momentum-free by construction. Strategy
layer = the lane's R3 rule verbatim on the period frame: rebalance every 21
bars (123 periods), warm-up 252 bars, 111 evaluation periods; rank by
trailing L-bar total log return (ties by instrument index), hold top-k,
10 bp per-side cost on replaced names, zero-cost equal-weight basket
benchmark, Δ = annualized period Sharpe (×√12) minus basket Sharpe. Nested
burden grids G1 ⊂ G6 (the lane's own L ∈ {63,126,252} × k ∈ {2,3}) ⊂ G24 ⊂
G96 — one panel's 8 sorted rankings serve all 96 configs. Per cell:
P := P(Δ_max(G6) ≥ 0.484) (the best KEEP margin; P(≥ 0.130) alongside) and
{q50, q90, q99} of Δ_max(N) for N ∈ {1, 6, 24, 96}. Ruling REJECT (P ≥ 0.10
in ≥ 6/12 cells, checked FIRST) / APPROVE (P ≤ 0.01 in ALL 12) / NULL per
the decision rule registered in the idea file before any code existed.

## Run (one command)

```
python3 sims/verdict-024-keep-margins-noise/xsec_selection_noise_sim.py
```

Exit 0 iff all self-checks pass. Deterministic — the only randomness is
`random.Random(20260727)` (main) / `random.Random(20260728)` (stability) /
`random.Random(20260729)` (reporting legs), each consumed in the pinned
loop order (cells lexicographic vol IID→RSV then ρ then S_bh ascending,
panels sequential; per panel regime chain, then f, then z by instrument
then bar; every normal = `NormalDist().inv_cdf(rng.random())`, exactly one
uniform per normal). No network, no git, no wall clock, no `hash()`.
stdout and `results.json` are byte-identical across process runs (verified
by external `diff` of two complete runs, cpython-3.11). Progress /
partial-results checkpoints go to stderr only.

## Files

- `xsec_selection_noise_sim.py` — stdlib-only driver: panel generator with
  the 2-state systemic-vol chain, prefix-sum period frame, 8 sorted
  rankings per rebalance serving all 96 nested configs via incremental
  top-k cumsums, exact draw-count accounting with fresh-Random sentinels,
  analytic gates (a) k=9 identity ≤ 1e−12, (b) exchangeability within 4 MC
  SE, (c) √(9/k) vol ratio within 2%, (d) RSV normalization exact in
  Fractions, (e) CPython pin + byte-identity; determinism replay of the
  first panel of every cell; an independently written twin evaluator
  (direct bar sums, explicit weights, statistics-module moments) replayed
  on strided panels; twin decision evaluators; two hand-derived pins;
  stability + reporting legs.
- `fixtures.json` — the pre-registration, committed BEFORE the runner: all
  constants verbatim from the idea file, the pinned loop/draw order, the
  decision rule + evaluation order + consequences, ten disclosed
  intake-time decisions, and two hand-derived pin scenarios with full
  derivations (three transcription slips in the committed derivations were
  corrected in a follow-up commit before any runner code existed — see the
  git history).
- `results.json` — committed run output: the full {P(≥0.484), P(≥0.130),
  q50/q90/q99 of Δ_max(N)} × (12 cells × N ∈ {1,6,24,96}) table for the
  main and stability legs, the burden-bar max-over-cells summary, per-axis
  APPROVE-pass shares and median P, the reporting legs, draw counts, and
  the ruling.
- `REPORT.md` — the finalizable verdict report (validity gate + the
  VERDICT 024 ruling).

## Verdict (summary — full report in REPORT.md)

**null (pre-registered conditional outcome, finalized)** — REJECT fails
first (P ≥ 0.10 in only **2/12** cells vs the ≥ 6 bar: the two zero-drift
ρ=0 cells, 0.154 IID / 0.169 RSV), APPROVE fails (P ≤ 0.01 in **8/12** vs
all 12). **Flip axis: S_bh (drift), spread 0.667**; ρ second (0.500); the
proposal's expected candidate — the RSV vol arm — measured **INERT**
(spread 0.000: volatility clustering does not fatten the best-of-N
Sharpe-margin tail at the swept persistence/multipliers).

- **The conditional rule (the citable finding):** the lane's TOP KEEP
  margins (+0.484 / +0.480) clear best-of-6 selection noise in EVERY
  drift-matched cell (P ≤ 0.004; matched q99(G6) = 0.399 < 0.484) — and
  the matched arm is the one the lane's own committed basket Sharpe 1.147
  selects; they are selection-compatible only in the zero-drift stress arm
  at ρ ≤ 0.3 (P up to 0.169). The WEAKEST KEEP margin (+0.130, L=252/k=3)
  is selection-compatible EVERYWHERE (P ≥ 0.057 in all 12 cells).
- **Burden bar (ships on every outcome):** max-over-cells q99 of Δ_max(N):
  N=1 0.798 / N=6 0.918 / N=24 1.054 / N=96 1.132; drift-matched row:
  0.260 / 0.399 / 0.516 / 0.619 — ORDER 033's expansion priced.
- **Stability:** fresh-seed half-M leg reproduces NULL with the same two
  hot cells. All four pre-registered analytic gates PASS.
- **Reporting legs:** J=18 shifts q99(G6) −0.041 (more stocks slightly
  LOWERS the bar); cost bracket 0.395/0.363/0.322 (0/10/25 bp);
  σ_ann = 0.15 ≡ 20 bp by the exact scaling identity.

69,772 self-checks, 0 failed; stdout + results.json byte-identical across
two full process runs by external diff on cpython-3.11; ~4.6 min per run.
