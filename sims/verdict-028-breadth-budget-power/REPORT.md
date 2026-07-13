# REPORT — round-3 breadth budget under the q99 bar (PROPOSAL 026)

> **Live verdict** (not an exemplar). Imitates the section order of `sims/REFERENCE.md`.
> Source idea: `menno420/idea-engine` `control/outbox.md` **PROPOSAL 026** ·
> 2026-07-13T05:40:19Z · status: sim-ready (idea
> `ideas/trading-strategy/round3-breadth-budget-q99-power-2026-07-13.md`, landed via
> idea-engine PR #293, main `0716140`). The ORDER 004 rule-3 VENTURE rotation slot,
> round 3, trading half deliberately — the POWER complement of VERDICT 024's
> null-side burden bar. Fully hermetic (the PROPOSAL 017–025 precedent): every
> fixture is a pinned constant committed with the sim; zero repo/network reads in
> the verdict session; ZERO real market bars; no dev-candidate evaluated on any
> data; the owner-gated post-2026 protocol untouched (P022's harvest hazard clause
> inherited verbatim as a contract term).
> Run: `python3 sims/verdict-028-breadth-budget-power/breadth_budget_power_sim.py`

## METHOD LABEL: `simulation`

Method ladder rung 1 (NUMERIC SIMULATION — seeded, deterministic, band-scored
against the pre-registration, with analytic validation gates): expected
true-keep yield Y(cell, N) under each design grid's own in-run q99 shortlist
bar, measured on ~21,700 decision-leg panels (plus ~6,050 aux) with edge of
known strength κ and persistence horizon E planted into V024's own committed
panel machinery (in-repo byte-reuse @ 5e356ed). `random.Random(20260748)` in
the pinned loop order; every band decision an exact integer/Fraction test on
keep-count sums. This label fills the outbox `evidence: simulation`. The two
judgment lines (θ ≥ 0.10 materiality, Y ≥ 0.25 detectability) were pinned by
pre-registration; full θ and Y curves ship in `results.json`, so a re-drawn
line re-reads, never re-runs.

## PREMISE (verified this session — hermeticity by construction)

The sim reads exactly ONE file (its own committed `fixtures.json`) and touches
no repo state, network, or wall clock; every constant ({J, T, period frame,
σ_ann, ρ/κ/E grids, S_bh, cost, grids G6/G10/G24/G96, marginal classes, M per
leg, seeds 20260748–51, θ ≥ 0.10 and Y ≥ 0.25 lines, V024 anchor constants at
full precision, band constants}) was copied verbatim from the idea file into
`fixtures.json` BEFORE the runner was written; the runner cross-checks its
literals against that file at start. 13 intake-time decisions are disclosed in
`fixtures.json`, plus a three-part `gate_calibration_disclosure` (below) —
each committed BEFORE the full decision run; git history is the disclosure.
Machinery identity with the parent was verified bit-exactly this session:
same-seed panels and all 96 per-config Δ values from this runner equal the
parent's committed code (`==` on floats) at ρ ∈ {0.0, 0.3}.

## What the sim MODELS

- **Panels:** V024's machinery + ONE planted layer: J = 9 × T = 2,595 daily
  bars, r_{j,t} = μ_d + α_{j,e(t)} + σ_d·(√ρ·f_t + √(1−ρ)·z_{j,t}), IID vol,
  S_bh = 1.15, σ_ann = 0.30; α_{j,e} = κ·(σ_d/√252)·g_{j,e}, g ~ N(0,1)
  i.i.d., redrawn every E bars from bar 0 (epoch map e(t) = t // E, last
  partial epoch kept); at κ = 0 zero alpha draws — the null legs are V024's
  IID matched cells verbatim. **27 decision cells** = κ ∈ {0.5, 1.0, 2.0} ×
  E ∈ {21, 63, 252} × ρ ∈ {0.0, 0.3, 0.6}.
- **Strategy layer:** the lane's R3 rule verbatim (V024 evaluator byte-reused):
  21-bar rebalance, warm-up 252 bars, 111 evaluation periods, trailing-L
  total-return ranking (ties by instrument index), top-k, 10 bp per side on
  replaced names, zero-cost equal-weight basket benchmark, Δ = annualized
  period Sharpe − basket Sharpe.
- **Design grids (nested, asserted):** G6 (lane's own L ∈ {63,126,252} ×
  k ∈ {2,3} mom eq) ⊂ G10 (G6 ∪ L ∈ {21,42} × k ∈ {2,3} mom eq — the targeted
  short-horizon expansion) ⊂ G24 ⊂ G96 (V024 definitions verbatim).
- **Round-3 procedure emulated exactly:** per ρ, bar b_N(ρ) = q99 of
  Δ_max(G_N) from the κ=0 null leg at M = 1,000; per planted panel,
  shortlist(G_N) = {i : Δ_i ≥ b_N(ρ)}. Oracle θ_i(cell) = no-selection mean
  over the cell's M = 400 panels; true edge θ ≥ 0.10; Y = expected true keeps
  per sweep; F = expected false keeps (reporting); N* = smallest
  N ∈ {6,10,24,96} within 5% of max yield; detectable ⇔ max_N Y ≥ 0.25.

## RESULTS (main leg, M = 400/cell, seed 20260748; all exact tables in results.json)

**Null bars b_N(ρ)** (κ=0, M = 1,000/ρ): ρ=0.0: G6 0.3057 / G10 0.3695 /
G24 0.4475 / G96 0.5318 · ρ=0.3: 0.4017 / 0.4267 / 0.4535 / 0.5000 ·
ρ=0.6: 0.3020 / 0.3247 / 0.3422 / 0.3729. The G6 → G96 bar climb (+0.07 to
+0.23) is the multiplicity tax the planted cells must out-earn.

**Detectability: 11 of 27 cells** (floor ≥ 8 met). ALL 9 E=21 cells are
undetectable **by construction** — the planted epochs align exactly with the
21-bar rebalance frame, so every holding period's alpha is independent of
every trailing window (see gate calibration below); no grid of any size can
see E=21 edge in this frame. κ=0.5 detects only at (E=252, ρ=0.6): after the
~0.5–0.8 Sharpe cost-plus-selection drag, half-sigma edge is simply below the
θ ≥ 0.10 line almost everywhere (e.g. θ(mom63) at (0.5, 252, 0.3) = −0.16).

**Yield curves rise all the way to N = 96 in every detectable cell.**
N* = 96 in 11/11 — the widest grid's higher bar never costs more true keeps
than its extra true configs contribute (at strong cells all 48 momentum
configs are individually true: n_true(G96) = 48, Y(96) → 48.0 at
(2.0, 252, 0.6) vs Y(6) = 6.0 — G6 is yield-capped at its own size).
Highlights (Y6 → Y10 → Y24 → Y96): (1.0, 63, 0.6): 0.29 → 1.07 → 0.95 → 2.04
· (1.0, 252, 0.3): 2.23 → 2.64 → 2.97 → 11.18 · (2.0, 63, 0.3): 1.69 → 4.70
→ 5.13 → 15.90 · (2.0, 252, 0.0): 5.61 → 8.95 → 10.57 → 42.26. False keeps
stay small where signal is strong (F(96) = 0.00 at the six strongest cells)
and peak at 2.37 at the weak-detection edge (1.0, 252, 0.0).

**Short lookbacks are the best E=63 detectors** — θ(mom L=21) > θ(mom L=63)
in every detectable E=63 cell (e.g. +0.855 vs +0.614 at (2.0, 63, 0.6)):
the G10 targeted expansion is genuinely the right shape for sub-63-bar
persistence hunting, exactly as the proposal's targeted-G10 row intended.

**DECISION (pre-registered order: floor → REJECT → APPROVE → NULL):**
- detectable 11/27 ≥ 8 → floor passed;
- REJECT (first): N* ≤ 10 in 0/11 detectable cells — not met;
- **APPROVE: N* ≥ 24 in 11/11 (100% ≥ 80%) AND median Y(96) − Y(6) =
  +14.2125 ≥ +0.25 — MET. RULING: APPROVE** ("blanket breadth survives its
  own bar"). Twin decision evaluators (integer vs Fraction) agree.
- Per-axis N*≤10 shares are 0.000 everywhere (spread 0.000 on all three
  axes); the detectability boundary, not N*, carries all structure: κ
  detects 1/9 → 4/9 → 6/9, E detects 0/9 → 4/9 → 7/9, ρ 3/9 → 3/9 → 5/9.

**Stability leg** (seed 20260749, M = 200): APPROVE reproduced — 11
detectable, N* ≥ 24 in 11/11, median Y(96) − Y(6) = +13.735.

**Reporting arms** (κ=1.0/E=63, M = 250, MAIN bars; cannot flip): S_bh = 0
stress arm detects at BOTH ρ (Y96 = 7.30 / 3.62) — the yield mechanism does
not ride the drift; RSV arm undetectable (Y ≈ 0) — regime vol at σ-doubling
stress swamps this edge under an IID-calibrated bar, an honest boundary of
the IID demotion.

**Marginal-config price list** (from G6, bar recomputed at N = 7 on the
ρ=0.3 null leg; ΔY on the 9 ρ=0.3 planted cells): covered-horizon duplicate
(L=84): bar +0.0126, ΔY up to +0.99 at strong cells · uncovered short
horizon (L=21): bar +0.0009 (nearly free), ΔY up to +0.81 where E=63 edge
exists · direction decoy (L=63 rev): bar +0.0250 — the LARGEST bar increase
— with ΔY ≤ 0 in every detectable cell (−0.16/−0.14/−0.02): a pure tax ·
weighting variant (rank-linear): bar +0.0250, ΔY up to +0.98. Median ΔY is
0.000 for all four classes (6 of the 9 ρ=0.3 cells are undetectable). The
literal price of "one more indicator": direction decoys cost the most and
pay nothing; short-horizon additions are nearly bar-free.

## GATE CALIBRATION — three disclosed deviations (fixtures `gate_calibration_disclosure`, all pinned BEFORE the full decision run; the registered bands, seeds, M, rule and evaluation order were never touched)

1. **E=21 sign gates (structural, disclosed after the reduced-M smoke run,
   before any full run):** with E = PB = 21 both counted from bar 0, every
   holding period is one whole epoch drawn after every trailing window —
   E[θ] is identical for ALL configs at E=21 (exchangeability), so the
   registered strict θ(rev) < θ(mom) is a fair coin per E=21 cell (P(all 9
   pass) ≈ 2⁻⁹). At E=21 only, the sign gate became the matched two-sided
   |θ_mom − θ_rev| ≤ 4·SE_paired band and the κ-monotonicity gate a 4·SE
   band; at E ∈ {63, 252} both stayed exactly as registered. Result: 9/9 and
   18/18 + 18/18 PASS.
2. **Anchor gate (disclosed after the first full-M attempt exited AT the
   gate, before any planted cell/θ/Y/ruling existed):** the registered
   ±0.05 tolerance's "fresh-seed MC tolerance at M = 1,000" premise is
   empirically false — running the PARENT'S OWN committed code at
   (IID, ρ=0.0, S_bh=1.15), M = 1,000, seeds {20260748, 111, 222, 333}
   gives q99(G6) = {0.3057, 0.3840, 0.3537, 0.4147}: fresh-seed SD ≈ 0.046,
   making ±0.05 a ~1.1σ gate per point against a committed anchor that
   itself carries the same SD. The run-invalidating anchor became the exact
   two-sample tail count X = #{null Δ_max ≥ V024 committed q99} ~
   BetaBinomial(1000; 11, 991) under machinery identity, gate X ∈ [1, 30]
   (~1% aggregate false-fail across 9 points); the registered ±0.05 gate is
   evaluated and recorded per point. Result: calibrated 9/9 PASS
   (X ∈ [4, 17]); registered ±0.05 breached 2/9 (ρ=0.0 N=6 −0.0927, N=96
   −0.0527) — quantile sampling noise by the measured SD, with machinery
   identity separately established bit-exactly.
3. **Familywise gate (disclosed before the full run):** the registered
   3-binomial-SE tolerance prices only leg-B noise, not the M = 1,000 bar's
   own quantile noise (~2.4σ total). Pinned handling: unconditional aux
   leg C (M = 2,000/ρ); an M = 500 breach re-reads against leg C at the
   same rule (count ∈ [7, 33]). Result: NOT NEEDED — 0/12 breaches at
   M = 500 (counts 1–9). Leg C reports realized rates 0.65–2.0%; the ρ=0.0
   column runs high (1.25–2.0%) because seed 20260748's ρ=0.0 bar drew low
   — the same quantile noise a real round-3 registration inherits from any
   M = 1,000 in-run bar (a reporting observation, not a gate).

## VALIDITY (all four required gates + the harness battery)

- **Anchor gate:** calibrated two-sample tail-count anchor 9/9 PASS
  (registered ±0.05 recorded: 7/9 pass, 2/9 quantile-noise breaches,
  disclosed above and in the verdict).
- **Identity gate:** k=9 control config |Δ| ≤ 1e−12 on the first 10 panels
  of every leg — PASS everywhere.
- **Fresh-seed gate:** stability leg (seed 20260749, M = 200) reproduces
  APPROVE — PASS.
- **Byte-identity gate:** stdout + results.json byte-identical across two
  full process runs (external `diff`, cpython-3.11 pinned and asserted) —
  PASS (verified by the committing session; see the session card).
- Plus: independent-leg familywise 12/12 at the registered rule; oracle sign
  gates 27/27 + 36 monotonicity comparisons; PIN1/PIN2 (V024 hand pins,
  byte-reused) + PIN3 alpha-injection identity (planted layer = exact
  running alpha prefix sums; epoch counts hand-pinned); determinism replay
  panel 0 of every cell; independently written twin evaluator to 1e−9 at
  pinned panels; twin decision evaluators (integer vs Fraction) agree;
  per-stream draw-count sentinels rejoined (729.2M total draws audited);
  θ-boundary clearance (no θ within 1e−9 of the 0.10 line).
  **61,890 self-checks, 0 failed; exit 0; ~5.5 min/run.**

## VERDICT: APPROVE — with the pre-registered consequence and two measured qualifiers

Per the pre-registered rule, evaluated in the registered order on measured
numbers: **APPROVE — "blanket breadth survives its own bar."** The round-3
registration may take the full blanket grid with the in-run q99(N) bar
attached at registration (V024's matched-row table the standing default);
ORDER 033 executes as written; the marginal price list prices each addition.

Measured qualifiers the consumer should carry (readings of the shipped
tables, not conditions on the ruling):

1. **Breadth pays through redundant truth, not coverage.** In every
   detectable cell the wide grid wins because many of its configs are
   individually true (θ ≥ 0.10) — up to all 48 momentum configs — so Y(N)
   grows roughly with grid size despite the rising bar. The pre-named
   coverage story died structurally: E=21 edge is invisible to EVERY grid
   in this frame (epoch-rebalance alignment), so expansion never rescued a
   horizon G6 could not see; at E=63, short lookbacks (already in G10) are
   the best detectors. Y counts redundant keeps by registration — a
   consumer who wants DISTINCT discoveries per sweep should read the
   per-config θ tables shipped alongside.
2. **The real boundary is detectability, not grid size.** 16 of 27 cells
   yield nothing at ANY N (all E=21; nearly all κ=0.5): when the planted
   edge is weak or faster than the rebalance frame, no breadth budget
   recovers it — and the ρ=0.0/κ≤1 corner pays the largest false-keep
   bills (F(96) up to 2.37). The NULL-case live probe remains the right
   pre-registration step even under APPROVE: the lane's lag-1..6 period
   Spearman rank-autocorrelation of trailing-63-bar returns on its own
   committed dev bars locates the real (κ, E) cell for free before the
   registration fixes N.

**Model basis** (restated from the idea file): planted epoch-dispersion
family — persistent per-instrument drift, i.i.d. Gaussian across epochs and
instruments, one-factor Gaussian noise; trailing-return ranking is exactly
its matched detector. Single most-likely-to-flip alternative: the lane's
REAL persistence structure (smoothly decaying drifts, regime-dependent
dispersion, momentum crashes) — deliberately the same measurement as the
live probe above. **Familywise-strictness direction** (disclosed): the q99
familywise rule is the strictest reasonable shortlist; a laxer round-3 rule
would raise every Y, so the APPROVE direction is if anything understated —
while REJECT, the arm this order protects against, was checked first and
missed by the full margin (0/11 vs the ≥ 80% bar).

## LIMITS

Model-true, not market-true (the flip alternative and its free probe are
named above); Y rewards redundant keeps by registration; E=21
undetectability is a frame-alignment fact of THIS strategy family, not a
market claim; the θ ≥ 0.10 / Y ≥ 0.25 lines are pre-registered judgments
shipped with full curves; θ is estimated on the selection panels (coupling
O(1/M), disclosed, sign-gated); the RSV reporting arm shows the IID-bar/
RSV-world mismatch matters at stress amplitude — a bar registered for a
regime-switching world should be recomputed under it; three gate
calibrations were re-based mid-session under the V027 disclosed-conflict
protocol, each pinned in fixtures BEFORE the full decision run, none
touching a band, seed, M, or the rule; the owner-gated post-2026 protocol
untouched on every path.
