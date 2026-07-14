# VERDICT 066 — badge saturation: Coin Magnate vs the committed daily faucet (idea-engine PROPOSAL 055)

Prices the World flagship's showcase wealth badge — `server/views.py`
@ superbot-mineverse `b983291`, `COIN_MAGNATE_THRESHOLD = 10_000`, with
its own calibration comment ("Sample: DeepDelver 18450 and MagmaMaven
25990 hit; SilverSeeker 7320 and below don't") — against the hub's
committed daily faucet `_DAILY_TIERS` @ superbot `3477594`
(E[`!daily`] = 169201/100 exact, one claim per `_DAILY_COOLDOWN = 86400` s)
on the shared wallet the read contract wires the badge to (`coins`
"mutated only by `economy_service`"), under the pinned player model, per
the registration (PROPOSAL 055, idea-engine
`ideas/superbot-mineverse/badge-saturation-coin-magnate-2026-07-14.md`
@ main 18f3171).

Run: `python3 sims/verdict-066-badge-saturation/badge_saturation_sim.py`

- `fixtures.json` — every registered constant verbatim from the PROPOSAL
  055 block / idea doc, committed BEFORE the runner; both calibration
  comments and the shared-wallet contract line quoted verbatim at the
  pins; the 7-miner sample table; the disclosed fixture-level choices
  (Bernoulli/value draw conventions, full-horizon trajectory shape and
  draw sentinels, the exact-variance SE convention, reporting N = 10,000,
  the C* binomial-mixture machinery with its exact cross-check against
  the absorbing arm, the median convention, the twin evaluators, the
  cpython-3.11 pin) all pinned here first.
- `badge_saturation_sim.py` — Arm A (DECISION: seedless exact absorbing
  DP over integer wallet states 0..9999, run-decomposed prefix-sum
  transitions, every P(T ≤ n) an exact Fraction over (2·10^6)^n; alone
  decision-bearing) + Arm S (robustness: seed 20261357, N = 20,000/cell,
  claim-Bernoulli then tier-then-uniform value exactly as
  `economy_helpers._pick_daily`; agreement 1/100 absolute on every
  decision cell AND ≥ 4·SE headroom on every firing cell) + stability
  leg (seed 20261358, N = 10,000, twin independently-written decision
  evaluators) + reporting leg (seed 20261359: σ ∈ {0, 9/10} worlds,
  H ∈ {30, 180}, badge-share curves S(d), the CV-of-T concentration mark,
  the C* threshold menu via the exact day-90 wallet law, the six static
  badge rows + deep_diver saturation note) + gates F1–F5. Aux seed
  20261360 never constructed, never read.
- `results.json`, `run-stdout.txt` — the accepted run (byte-identical
  across two process runs by external sha256; hashes in REPORT.md; every
  decision number an exact rational; no wall-clock in any output).
- `REPORT.md` — ruling, the exact decision grid, the C* menu, gates,
  drafter-reference comparison (every disclosed value reproduces), the
  three first-class anomalies, boundaries, and the five validity-gate
  answers.

Ruling: see REPORT.md (the decision rides Arm A alone, rules applied in
the registered order — REJECT checked first, bands 19/20 · 3-of-4 ·
≤ 14-day median · 1/100 + 4·SE exact).
Hermetic, stdlib-only, CPython 3.11 pinned, no wall-clock in any output.
