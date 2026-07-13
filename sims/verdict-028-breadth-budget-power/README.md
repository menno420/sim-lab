# verdict-028 · breadth-budget power

Does expanding the round-3 config grid past its own q99 shortlist bar buy
true discoveries, or does the bar eat the margin? The POWER complement of
VERDICT 024's null-side burden bar. Answers idea-engine PROPOSAL 026
(control/outbox.md 2026-07-13T05:40:19Z, idea
`ideas/trading-strategy/round3-breadth-budget-q99-power-2026-07-13.md`,
landed via idea-engine PR #293, main `0716140`) — the ORDER 004 rule-3
VENTURE rotation slot, round 3, trading half deliberately (round 1 books
P018 → V020 null, round 2 trading P022 → V024 null; V024's recommendation
flags its burden-bar table as round-3 pre-registration default material,
and that table is HALF a tool — it prices what expansion COSTS, not what
it BUYS). Fully hermetic per the PROPOSAL 017–025 precedent: every fixture
is a pinned constant committed with the sim; zero repo/network reads in
the verdict session; ZERO real market bars; no dev-candidate evaluated on
any data; the owner-gated post-2026 protocol untouched.

Model: V024's committed panel machinery byte-reused at its in-repo pin
(`sims/verdict-024-keep-margins-noise/` @ 5e356ed — generator, strategy
evaluator, independently written twin, k=9 identity gate, quantile
convention, hand pins PIN1/PIN2), extended with ONE planted layer:
per-instrument epoch drifts α_{j,e} = κ·(σ_d/√252)·g_{j,e}, g ~ N(0,1)
i.i.d., redrawn every E bars from bar 0 — persistent cross-sectional drift
dispersion with one-sigma annualized Sharpe κ, gone at κ = 0 so the null
legs are machinery-identical to V024's IID matched cells. 27 decision
cells = κ ∈ {0.5, 1.0, 2.0} × E ∈ {21, 63, 252} × ρ ∈ {0.0, 0.3, 0.6};
IID vol, S_bh = 1.15 (both demotions by V024's measured axis findings).
The lane's R3 rule verbatim (21-bar rebalance, warm-up 252 bars, 111
evaluation periods, trailing-L ranking with ties by index, top-k, 10 bp
per side on replaced names, equal-weight basket benchmark, Δ = Sharpe −
basket Sharpe). Nested design grids G6 ⊂ G10 (targeted short-horizon:
G6 ∪ L ∈ {21,42} × k ∈ {2,3} mom eq) ⊂ G24 ⊂ G96 (V024 definitions
verbatim), N ∈ {6, 10, 24, 96}. Round-3 procedure emulated exactly: per ρ
the bar b_N(ρ) = q99 of Δ_max(G_N) from a κ=0 null leg at M = 1,000
(chained-anchored to V024's committed q99 values within ±0.05); per
planted panel shortlist = {i ∈ G_N : Δ_i ≥ b_N(ρ)}. Oracle margins
θ_i(cell) = no-selection means over M = 400 panels; true edge θ ≥ 0.10;
Y(cell, N) = expected true keeps per sweep; F = expected false keeps
(reporting); N*(cell) = smallest N within 5% of max yield; detectable iff
max_N Y ≥ 0.25. Seeds: 20260748 main / 20260749 stability (M = 200, must
reproduce the ruling) / 20260750 validation + reporting / 20260751 aux.
Decision (registered order): floor (≥ 8/27 detectable, else NULL) →
REJECT iff N* ≤ 10 in ≥ 80% of detectable cells → APPROVE iff N* ≥ 24 in
≥ 80% AND median Y(96) − Y(6) ≥ +0.25 → NULL (flip axis named).
Reporting-only: S_bh = 0 arm, RSV arm, and the marginal-config price list
(bar recomputed at N = 7; ships on every outcome).

Gates (run invalid on any failure): chained anchors (±0.05), k=9 identity
(Δ ≡ 0 to 1e−12), independent-leg familywise (bars from leg A on a fresh
M = 500 leg B, rate within 3 binomial SE of 0.01, pinned leg-C handling),
oracle sign gates (strict at E ∈ {63, 252}; matched 4·SE noise bands at
E = 21 per the fixtures `gate_calibration_disclosure` — the epochs align
exactly with the 21-bar rebalance frame there, making every config's
expected θ identical), cpython-3.11 pinned, stdout + results.json
byte-identical across two process runs (external diff).

## Run (one command)

```
python3 sims/verdict-028-breadth-budget-power/breadth_budget_power_sim.py
```

Exit 0 iff all self-checks pass. Deterministic — pinned seeds, pinned loop
order, one uniform per normal (draw-count stream-rejoin sentinels per
stream). No network, no git, no wall clock, no `hash()`. Progress goes to
stderr only.

## Files

- `fixtures.json` — the pre-registration: every constant verbatim from the
  idea file, V024 anchor constants at full precision, 13 intake-time
  decisions, and the pre-run `gate_calibration_disclosure`.
- `breadth_budget_power_sim.py` — the runner (stdlib-only, single file).
- `results.json` — committed run output (byte-identical on re-run).
- `REPORT.md` — the verdict report (method label, gates, tables, ruling).
