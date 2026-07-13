# verdict-022 · casino-fairness

Can ONE house rule — a shared house-edge band plus a shared max-bet cap — keep
house-banked wager minigames simultaneously FUN (casual sessions winnable often
enough), SAFE (no player-invented policy, capped martingale included, vaporizes
a session bankroll), and SINK (the casino is never a viable earn path under a
grinder's best policy) across three payout shapes? Answers idea-engine
PROPOSAL 020 (control/outbox.md 2026-07-13T02:04:02Z, idea
`ideas/superbot/casino-house-edge-fairness-envelope-2026-07-13.md`, landed via
idea-engine PR #286, main `da20713`) — the ORDER 004 rule-3 GAME-MECHANICS
rotation slot, taken early because the consumer window (tonight's superbot
minigame/casino consolidation, inbox ORDER 004 "World's balance pins") closes
tonight. Fully hermetic per the PROPOSAL 017/018/019 precedent: every fixture
is a pinned constant committed with the sim, zero repo/network reads in the
verdict session.

Model: integer-chip bankroll walks, B₀ = 1,000, min stake 1; archetypes
G1/G2/G3 with payout k ∈ {1, 5, 19} and win probability p = (1−e)/(k+1) (EV
per unit staked = −e exactly); house-edge grid e ∈ {0.01, 0.02, 0.05, 0.10} +
e=0 control (reporting-only); caps MAXBET = m·B₀, m ∈ {0.05, 0.25, 1.0};
policies F-0.01/F-0.05/F-0.10 fixed-fraction, C constant-50, M
capped-martingale base-10, plus the analytic-only constant-10 FUN reference
leg; profiles CASUAL (100 bets; P_ahead, P_wipe), GRINDER (double-or-half,
cap 4,000 bets, >1% cap-hits marks the cell indeterminate), COMPULSIVE
(reporting-only; median bets-to-ruin). 36 envelope cells = 3 archetypes × 4
edges × 3 caps; bands FUN ≥ 0.25 / SAFE ≤ 0.05 / SINK ≤ 0.10; ruling
REJECT / APPROVE / NULL per the decision rule registered in the idea file
before any code existed, evaluated in that order.

## Run (one command)

```
python3 sims/verdict-022-casino-fairness/casino_fairness_sim.py
```

Exit 0 iff all self-checks pass. Deterministic — the only randomness is
`random.Random(20260721)` (primary) / `random.Random(20260722)` (stability) /
`random.Random(20260723)` (aux self-check stream only), each consumed in the
pinned loop order (archetype, e ascending with the e=0 control first, m
ascending, policy F/C/M with β ascending, profile casual → grinder →
compulsive, replications sequential; exactly ONE `rng.random()` draw per bet).
No network, no git, no wall clock, no `hash()`. stdout and `results.json` are
byte-identical across process runs (verified by external `diff` of two
complete runs, cpython-3.11).

## Files

- `casino_fairness_sim.py` — stdlib-only driver: Arm A (exact Fractions —
  binomial FUN tails via `math.comb`, two-boundary gambler's-ruin closed form
  for G1×C independently re-derived by tridiagonal elimination, e=0 control
  = 1/3 exactly), Arm S (the pinned MC sweep, M = 5,000/2,000/500 per
  cell-policy), the half-M seed-20260722 stability leg, the 1.0 pp Arm-A
  agreement gate, the aux reference-leg MC corroboration, and the
  self-checks (per-replication conservation + stop-validity + outcome
  classification, G1×C exact-boundary hits, trace-replay through an
  independently written twin kernel with per-bet stake-bound assertions,
  hand-derived pins, draw-count accounting against a fresh
  `Random(seed)`, e=0 win-martingale fairness, twin decision evaluators).
- `fixtures.json` — the pre-registration, committed BEFORE the runner: all
  constants verbatim from the idea file, the pinned loop/draw order, the
  decision rule + evaluation order + consequences, two hand-derived pin
  scenarios with full derivations, and eight disclosed intake-time decisions
  (incl. the agreement-gate granularity reading and the amended e=0 fairness
  statistic — see the disclosures themselves).
- `results.json` — committed run output: the full
  {P_ahead, P_wipe, P_double, P_half, cap-hit fraction, median bets-to-ruin}
  × (archetype, e, m, policy) table for both legs, Arm-A exact values
  (fractions + floats), the agreement gate, envelope sets E*(g, m),
  indeterminate cells, per-axis envelope shares, the REJECT gap
  quantification, and the ruling.
- `REPORT.md` — the finalizable verdict report (validity gate + the VERDICT
  022 ruling).

## Verdict (summary — full report in REPORT.md)

**reject (pre-registered)** — odds cannot do the job: **E\*(g, m) = ∅ in all
36 cells, at every cap, in 3/3 archetypes** (the rule needs 2/3), both arms
where covered, reproduced by the half-M seed-20260722 stability leg.

- **SINK fails 33/36:** for G2 (k=5) and G3 (k=19) NO edge at NO cap passes —
  worst-policy P_double runs 0.195–0.323 vs the 0.10 band, because
  p = (1−e)/(k+1) barely moves with e at high k: the grinder's doubling odds
  are variance-dominated, not edge-controlled (e=0 control: 0.30–0.41). Only
  even-money G1 is edge-controllable (closed-form leg): SINK passes at
  (e=0.05, m=0.05), (e=0.10, m=0.05), (e=0.10, m=0.25) only.
- **SAFE fails 36/36:** flat C-50 wipes 0.063–0.725 at the tight cap;
  capped martingale wipes 0.182–0.983 at m ≥ 0.25. Even at e=0, C-50 wipes
  5.7% — wipe-within-100-bets is gambler's-ruin variance, not edge.
- **FUN fails only 3/36** (G1 e=0.10, exact 0.1346 < 0.25) — high-variance
  shapes stay winnable at every edge, which is exactly why they cannot be
  sink-proofed.
- **Nearest miss:** (G1, e=0.05, m=0.05) passes FUN (0.2738 exact) and SINK
  (0.0895; Arm A exact 0.0899) but fails SAFE at 2.7× the band (0.1358).
- **Gate PASS:** pooled G1×C MC-vs-exact deviations 0.05–0.72 pp (≤ 1.0 pp
  pre-registered); e=0 control reproduces P_double = 1/3.
- **Consequence (pre-registered):** the consolidation does NOT tune per-game
  odds; the non-odds levers (rake-only PvP framing — priced free by the
  G1-at-e=r identity — session comp/stipend, entry-fee-with-prize) ride to
  the World seat with the quantified gap.

13,392,272 self-checks, 0 failed; stdout + results.json byte-identical
across two full process runs by external diff on cpython-3.11; ~72 s.
