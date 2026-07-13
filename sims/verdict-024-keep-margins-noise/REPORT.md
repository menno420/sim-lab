# REPORT — xsec KEEP margins vs selection noise (PROPOSAL 022)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 022** ·
> 2026-07-13T03:02:28Z · status: sim-ready (idea
> `ideas/trading-strategy/xsec-keep-margins-selection-noise-2026-07-13.md`, landed via
> idea-engine PR #288, main `1c6313c`). The ORDER 004 rule-3 VENTURE rotation slot,
> round 2, trading half (ORDER 033: "find more strategies to backtest, as well as more
> stocks, more indicators"). Fully hermetic (the PROPOSAL 017/018/019/020/021
> precedent): every fixture is a pinned constant committed with the sim; zero
> repo/network reads in the verdict session; ZERO real market bars; no dev-candidate
> evaluated on any data; the owner-gated post-2026 protocol untouched.
> Run: `python3 sims/verdict-024-keep-margins-noise/xsec_selection_noise_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — seeded, deterministic, band-scored
against the pre-registration, with analytic validation gates that make the
run invalid on any failure): the null distribution of the trading lane's
promote-on statistic — Δ_max(N) = max over a nested config grid of
(strategy Sharpe − basket Sharpe) — measured on 15,500 momentum-free
synthetic panels matched to the lane's protocol shape, the lane's own R3
KEEP rule applied verbatim, `random.Random(20260727)` in the pinned loop
order, every band decision an exact integer comparison on counts. This label
fills the outbox `evidence: simulation`. The one judgment question — whether
0.01 / 0.10 are the right lines — was pinned by pre-registration in the idea
file; the full per-cell P values and complete quantile tables ship in
`results.json`, so a re-drawn line re-reads, never re-runs.

## PREMISE (verified this session — hermeticity by construction)

The sim reads exactly ONE file (its own committed `fixtures.json`, the
pre-registration) and touches no repo state, no network, no wall clock;
every constant ({J, T, period frame, σ_ann, vol-model constants, ρ-grid,
S_bh-grid, cost, grids G1/G6/G24/G96, M per leg, seeds 20260727–29, tested
margins 0.484/0.130, band constants}) was copied verbatim from the idea file
into `fixtures.json` BEFORE the runner was written, and the runner
cross-checks its literals against that file at start (including asserting
the RSV unconditional unit variance and stationary π EXACTLY, in Fractions).
Ten intake-time decisions are disclosed in `fixtures.json` (normal draws via
`NormalDist().inv_cdf` — one uniform per normal, making draw-count sentinels
exact; RSV initial state from stationary π; period alignment from bar 0 with
the final 12 of 2,595 bars unused; cost-free entry FORCED by pre-registered
gate (a)'s k=9 identity; the left-continuous quantile convention;
reporting-leg M = 250; the vol-ratio gate's equal-weight scope with
rank-linear checked against its own analytic value; ddof = 1; the exact
σ-scaling identity; per-config exchangeability-gate granularity). Three
transcription slips in the committed hand-pin DERIVATIONS were corrected in
a follow-up commit before any runner code existed (git history is the
disclosure); the pinned decision machinery (grids, seeds, bands, rule,
evaluation order) was untouched by every disclosure.

## What the sim MODELS

All constants pre-registered in `fixtures.json`:

- **Panels:** J = 9 instruments × T = 2,595 daily bars;
  r_{j,t} = μ_d + m_{s_t}·σ_d·(√ρ·f_t + √(1−ρ)·z_{j,t}), f and z i.i.d.
  N(0,1), σ_ann = 0.30. Vol models: IID (m ≡ 1) and RSV (2-state Markov
  systemic vol, p_cc = 0.98 / p_ss = 0.94, variance multipliers (0.6, 2.2),
  stationary π = (0.75, 0.25), unconditional unit variance exact, one chain
  per panel shared by all instruments). ρ ∈ {0.0, 0.3, 0.6}; drift
  μ_d = S_bh·σ_d·√(ρ + (1−ρ)/9)/√252 with S_bh ∈ {0, 1.15} (the matched leg
  reproduces the lane's reported basket Sharpe 1.147 in expectation —
  measured mean basket Sharpe 1.152–1.173 across the six matched cells).
  **12 decision cells**, every one momentum-free by construction.
- **Strategy layer (the lane's R3 rule verbatim on the period frame):**
  rebalance every 21 bars (123 periods), warm-up 252 bars, 111 evaluation
  periods; rank by trailing L-bar total log return (ties by instrument
  index), hold top-k to the next rebalance; cost 10 bp per side on replaced
  names (0.001·2·replaced/k); benchmark = zero-cost equal-weight basket;
  Sharpe = mean/std(ddof=1) × √12; Δ(config) = Sharpe_config − Sharpe_basket.
- **Nested burden grids:** G1 = {L=63, k=2, momentum, equal} ⊂ G6 = the
  lane's own L ∈ {63,126,252} × k ∈ {2,3} ⊂ G24 (6 L × 2 k × 2 directions) ⊂
  G96 (8 L × 3 k × 2 directions × 2 weightings) — one panel's 8 sorted
  rankings serve all 96 configs; Δ_max(N) monotone in N by construction and
  asserted per panel.
- **Statistics:** per cell P := P(Δ_max(G6) ≥ 0.484) (the lane's best KEEP
  margin) and P(Δ_max(G6) ≥ 0.130) (the weakest, reporting), plus
  {q50, q90, q99} of Δ_max(N) for N ∈ {1, 6, 24, 96}.
- **Decision rule (registered before any code; evaluated in this order):**
  REJECT iff P ≥ 0.10 in ≥ 6/12 cells (checked FIRST — the
  protect-owner-attention arm); APPROVE iff P ≤ 0.01 in ALL 12; NULL
  otherwise, flip axis named via per-axis APPROVE-pass shares and median P.
- **Legs:** main (M = 1,000/cell, seed 20260727); stability (M = 250, seed
  20260728, must reproduce the ruling — validity gate); reporting-only
  (seed 20260729, M = 250, IID/ρ=0.3/S_bh=1.15 only): J = 18, cost
  c ∈ {0, 25 bp}, σ_ann = 0.15.

## What it SETTLED (the load-bearing numbers)

Full tables in `results.json`.

**(1) The per-cell P table (the decision statistic).** P(Δ_max(G6) ≥ 0.484),
M = 1,000 per cell, post-cost 10 bp:

| vol | ρ | S_bh = 0 | S_bh = 1.15 |
|-----|-----|---------|-------------|
| IID | 0.0 | **0.154** | 0.004 |
| IID | 0.3 | 0.038 | 0.000 |
| IID | 0.6 | 0.002 | 0.000 |
| RSV | 0.0 | **0.169** | 0.004 |
| RSV | 0.3 | 0.030 | 0.003 |
| RSV | 0.6 | 0.000 | 0.000 |

Cells with P ≥ 0.10: **2/12** (REJECT needs ≥ 6 — fails). Cells with
P ≤ 0.01: **8/12** (APPROVE needs 12 — fails). **RULING: NULL**, the
pre-registered expected-plausible outcome, finalized (not a re-run request).

**(2) The flip axis is DRIFT (S_bh), not the expected RSV arm.** Per-axis
APPROVE-pass shares / median P: **S_bh** — 0: share 0.333, median P 0.034;
1.15: share 1.000, median P 0.002 (**spread 0.667, the named axis**). ρ —
0.0: 0.500 / 0.079; 0.3: 0.500 / 0.017; 0.6: 1.000 / 0.000 (spread 0.500,
the second axis). **vol — IID: 0.667 / 0.003; RSV: 0.667 / 0.004 (spread
0.000 — measured INERT):** volatility clustering at the swept persistence
and multipliers does NOT fatten the best-of-N Sharpe-margin tail; the
proposal's expected flip candidate is flat everywhere (largest per-cell
IID-vs-RSV P difference 0.015 at ρ=0/S_bh=0, within 2 MC SE).

**(3) The CONDITIONAL rule (the citable finding).** Under every
DRIFT-MATCHED null swept — basket Sharpe 1.15, the arm matched to the lane's
own reported 1.147 — the best KEEP margin +0.484 is BEYOND best-of-6
selection noise: P ≤ 0.004 in all six matched cells (max q99 of Δ_max(G6)
there is 0.399 < 0.484). Under the zero-drift stress arm at low correlation
it is selection-compatible: P = 0.154 (IID) / 0.169 (RSV) at ρ = 0. The
mechanism is exposed by the q-tables: with a drifting basket, a k-of-9
portfolio carries √(9/k) times the basket's vol, so under H0 its Sharpe is
systematically LOWER and the whole Δ_max distribution shifts left (matched
ρ=0 cells: q50(G6) = −0.31); the zero-drift arm removes that penalty and
leaves pure selection spread (q99(G6) up to 0.918).

**(4) The weakest KEEP margin +0.130 is selection-compatible EVERYWHERE.**
P(Δ_max(G6) ≥ 0.130) runs 0.057–0.616 across all 12 cells — including
0.057–0.156 in the drift-matched arm. The L=252/k=3 dev-candidate's margin
never clears best-of-6 noise in any swept null; only the two ~+0.48 margins
(L=63, k∈{2,3}) carry evidence.

**(5) The burden-bar table (ships on every outcome — ORDER 033's expansion
priced).** Max-over-cells (conservative, zero-drift-dominated) q99 of
Δ_max(N): **N=1: 0.798 · N=6: 0.918 · N=24: 1.054 · N=96: 1.132** (q90 row:
0.417 / 0.589 / 0.737 / 0.814). Drift-MATCHED max q99 (the lane-relevant
row, S_bh=1.15 cells): **N=1: 0.260 · N=6: 0.399 · N=24: 0.516 · N=96:
0.619**. Every ~4× config-count step raises the matched q99 bar by ~0.1–0.2
Sharpe; a 96-config round-3 sweep needs Δ ≥ ~0.62 (matched) / 1.13
(conservative) for a q99-clean shortlist row.

**(6) Stability + validity.** The fresh-seed half-M stability leg (20260728)
reproduces NULL with per-cell counts [40, 1, 8, 0, 0, 0, 47, 2, 14, 1, 0, 0]
/ 250 — same two hot cells, same matched-arm emptiness. All pre-registered
analytic gates PASS: (a) k=9 identity |Δ| ≤ 1e−12 on the first 10 panels of
every cell; (b) exchangeability within 4 MC SE on all 96 configs × 6
S_bh=0 cells; (c) pooled vol ratio within 2% of √(9/k) on all equal-weight
configs (rank-linear within 2% of its own analytic √(9·Σw²), aux); (d) RSV
normalization exact in Fractions; (e) cpython-3.11 asserted, stdout +
results.json byte-identical across two full process runs by external diff.
Draw-count sentinels close exactly (326,970,000 main + 81,742,500 stability
+ 12,326,250 J18 + 6,487,500 cost-leg uniforms, one per normal/transition).
**69,772 self-checks, 0 failed**; runtime ~4.6 min per full run, stdlib-only.

**(7) Reporting legs (cannot flip; did not).** J = 18 ("more stocks"):
q99(G6) shifts −0.041 vs the J=9 matched cell — a wider universe slightly
LOWERS the selection bar at fixed k (more diversified top-k, closer to the
basket's vol). Cost bracket: q99(G6) 0.395 (0 bp) / 0.363 (10 bp) / 0.322
(25 bp) — the pinned 10 bp sits mid-bracket, direction as disclosed.
σ_ann = 0.15: q99(G6) 0.335, matching the exact identity σ0.15@10bp ≡
σ0.30@20bp (asserted to 1e−12 on the first 5 reporting panels).

## What it did NOT settle

- **Which null arm the lane's real data lives in** — this is model-true, not
  market-true: Gaussian one-factor with regime vol; no fat tails beyond
  clustering, no cross-sectional dispersion dynamics, no momentum crashes.
  The measured inertness of the vol axis softens but does not remove this:
  the binding axis (drift) is located by the lane's own committed basket
  Sharpe (1.147 ≈ the matched arm), while the pre-registered live probe
  (lag-1..5 autocorrelation of squared daily basket returns on the lane's
  committed dev bars — one lane-side script, zero holdout spend, zero owner
  clicks) ships as the named locator, now confirmatory rather than decisive.
- **The dev-candidates' true edge** — nothing here evaluates them on any
  data; this is the null side of the inference only. The owner-gated
  post-2026 protocol remains the only legitimate confirmation path and is
  untouched.
- **The frequency boundary (pre-registered, restated):** period-level Sharpe
  (111 obs) emulates the lane's daily stitched-OOS statistic with a WIDER
  null — APPROVE was the conservative direction, and the matched-arm
  emptiness (P ≤ 0.004) survives it; the REJECT band carried 10× head-room
  by construction.
- **Cost/benchmark pins:** 10 bp per side and a zero-cost rebalanced basket
  are model constants (not readable in-repo), both pushing the strategy
  down — conservative toward APPROVE, bracketed by the c ∈ {0, 25 bp} leg.
- **The 0.01/0.10 lines themselves** are pre-registered judgments; full P
  and quantile tables ship so a re-drawn line re-reads, never re-runs.

## The validity gate (all five, quoted verbatim from README §"The validity gate")

**1. "COMPARABLE TO LIVE? what the model abstracts away, and whether any gap could flip the conclusion;"**
The question is about the null distribution of the lane's own dev-stage
statistic under a pinned momentum-free model family — by pre-registration,
not a claim about the lane's real bars. The family brackets the axes that
matter (two vol arms, three correlations, drift matched to the lane's
measured basket Sharpe); the one gap that could move the routing-relevant
number (which arm the real data resembles) is disclosed, and its binding
component — drift — is fixed by the lane's own committed 1.147. The rule's
verbatim application (same interval, same grid, same cost form, same
statistic) removes the protocol-shape gap.

**2. "UNCORRUPTED? no bugs (self-check the sim), no seeded luck (multiple seeds / statistical stability), no parameter cherry-picking (report the sweep, not the best point);"**
Strong. **69,772 self-checks, 0 failed**, exit-coded: four pre-registered
analytic gates (k=9 identity to 1e−12; per-config exchangeability at 4 MC
SE; √(9/k) pooled vol ratio at 2%; exact-Fraction RSV normalization), a
determinism replay of the first panel of every cell, an INDEPENDENTLY
WRITTEN twin evaluator (direct bar sums, explicit weight vectors, its own
sorts and turnover sets, statistics-module moments) agreeing within 1e−9 on
all 96 configs across 62 strided panels, exact draw-count sentinels against
fresh Random(seed) streams, two hand-derived pin panels with committed
derivations (zero-turnover closed-form Δ; alternating-leader exact cost
accounting), RSV chain frequency/transition checks, the exact σ-scaling
identity, and twin decision evaluators (independent code paths, one in
exact Fractions) agreeing on ruling, hot-count, axis shares, and flip axis.
No seeded luck: a DIFFERENT seed reproduces the ruling and both hot cells.
No cherry-picking: all 12 cells × 4 grid sizes × 3 quantiles + both margins
committed, the inert vol axis reported as prominently as the binding one.

**3. "ROBUST? does the conclusion survive variation at the edges;"**
The NULL is margin-heavy on both sides: REJECT fails 2 vs 6 cells (the
third-hottest cell is 0.038, a 2.6× gap to the 0.10 band); APPROVE fails
with 4 cells at 3.0–16.9× the 0.01 line. The stability leg reproduces the
ruling and the cell pattern at half M on a fresh seed. The conditional
finding's decisive side (matched-arm P ≤ 0.004 vs the 0.01 line) holds in
all six matched cells with q99 margins of at least 0.085 Sharpe below the tested
0.484; the reporting legs move q99(G6) by at most ±0.04 without touching
any band side.

**4. "REPRODUCIBLE? committed code, one documented command, same result;"**
Strong. One documented command, no flags, stdlib-only, hermetic; one
`random.Random(<pinned seed>)` stream per leg in the pinned loop order,
exactly one uniform per normal. stdout AND `results.json` byte-identical
across TWO complete process runs by external `diff` on cpython-3.11
(pinned and asserted). ~4.6 min per run.

**5. "LIMITS? what this evidence does NOT show."**
It never touches the lane's real bars, so it cannot say the dev-candidates
HAVE edge — only that their two best margins exceed what selection alone
hands the drift-matched null family, while the +0.130 margin does not
anywhere; the null family is Gaussian-with-regime-vol (no fat tails, no
dispersion dynamics, no crashes); the frequency emulation widens the null
(direction disclosed); the burden bars are model bars, not market
guarantees; and the ruling's conditional structure means NO unconditional
soundbite — neither "the margins are noise" nor "the margins are real" is
supported.

## EVIDENCE STRENGTH: **strong** (for the pre-registered question) — gate PASS

Every constant, band, seed, and the evaluation order were registered in the
idea file before any code; the decision arithmetic is exact integer
comparison; four analytic gates passed; the ruling reproduces on a second
seed at half M; the twin evaluator and twin deciders agree everywhere. The
honest boundary: this strength attaches to the pinned momentum-free panel
family and the pre-registered bands — the sim prices selection noise, it
does not certify edge.

## VERDICT & recommendation (for the fleet manager to route)

- **Verdict: `null` — the pre-registered conditional outcome, finalized.**
  By the rule committed before any code (REJECT checked first): REJECT
  fails (P ≥ 0.10 in only 2/12 cells vs ≥ 6), APPROVE fails (P ≤ 0.01 in
  8/12 vs all 12). **Flip axis: S_bh (drift), spread 0.667**; ρ second
  (0.500); the proposal's expected candidate — the RSV vol arm — measured
  INERT (spread 0.000).
- **The conditional rule (the citable finding, never either soundbite):**
  the lane's TOP KEEP margins (+0.484 / +0.480) clear best-of-6 selection
  noise in EVERY drift-matched cell swept (P ≤ 0.004; matched q99(G6) =
  0.399 < 0.484) — and the matched arm is the one the lane's own committed
  basket Sharpe 1.147 selects; they are selection-compatible only in the
  zero-drift stress arm at ρ ≤ 0.3 (P up to 0.169). The WEAKEST KEEP margin
  (+0.130, L=252/k=3) is selection-compatible EVERYWHERE (P ≥ 0.057 in all
  12 cells) and should carry no promotion weight on its own.
- **Consequence (pre-registered for NULL):** the owner proposal is NOT
  auto-routed and the breadth-flip is NOT auto-invoked; the conditional
  rule ships, and the cheapest LIVE probe is named — the lane computes
  lag-1..5 autocorrelation of squared daily basket returns on its own
  committed dev bars (one lane-side script, zero holdout spend, zero owner
  clicks, zero new data), locating its real null cell; NOTE, measured: the
  vol axis the probe targets is inert in-grid, and the binding drift axis
  is already located by the lane's committed basket Sharpe 1.147 ≈ the
  matched arm — so the probe is confirmatory, and the manager MAY treat the
  matched-arm reading (top margins beyond noise, weakest margin not) as the
  operative conditional when weighing the owner-proposal residual slice.
- **The burden-bar table (round-3 pre-registration default material, on
  every outcome):** conservative max-over-cells q99 of Δ_max(N): N=1 0.798 /
  N=6 0.918 / N=24 1.054 / N=96 1.132; drift-matched row (the lane-relevant
  bar): 0.260 / 0.399 / 0.516 / 0.619. ORDER 033's expansion priced: a
  96-config sweep needs a ~+0.62 margin (matched null, q99) for a
  shortlist row — every added strategy/stock/indicator raises the bar by a
  now-measured amount; "more stocks" alone (J=18 at fixed k) measured
  slightly bar-LOWERING (q99 shift −0.041), so breadth in configs, not
  universe size, is what taxes the shortlist.
- **Boundaries restated (pre-registered):** model-true not market-true
  (Gaussian one-factor + regime vol; the RSV arm was the bracketed
  clustering direction and measured inert); period-level Sharpe widens the
  null — APPROVE-conservative, and the matched-arm P ≤ 0.004 survives it;
  cost/benchmark pins push toward APPROVE and are bracketed by the
  c ∈ {0, 25 bp} leg; reporting-only legs (J=18, cost grid, σ=0.15) touched
  no band side. The owner gate is untouched: no real bars, no candidate
  evaluated, nothing scheduled.
- **Named follow-ups (not ordered):** the lane-side autocorrelation
  one-script probe (the pre-registered NULL unlock); a fat-tailed
  innovation arm (Student-t) only if the lane's probe rejects both swept
  vol arms; the reusable methodology note — this q99(N) curve prices ANY
  fleet pipeline that promotes a best-of-N (idea-engine's own "best probe
  of the batch" included).
- **Codex review:** none this cycle — the @codex step is suspended per the
  outbox codex-line escalation @ `dedc12e`; Q-0120 verify-never-obey stands.

<!-- Outbox verdict-grammar block — appended to control/outbox.md by this
session per the V015–V022 slice boundary, with header timestamps from live
`date -u` at append time. -->
