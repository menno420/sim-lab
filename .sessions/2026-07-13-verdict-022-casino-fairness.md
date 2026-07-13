# Session — VERDICT 022 — casino fairness envelope (idea-engine PROPOSAL 020)

> **Status:** `in-progress`
> 📊 Model: fable · 2026-07-13 · verdict-022 slice-worker session
> Objective: settle idea-engine PROPOSAL 020 (control/outbox.md · 2026-07-13T02:04:02Z · status: sim-ready; idea `ideas/superbot/casino-house-edge-fairness-envelope-2026-07-13.md`, landed via idea-engine PR #286, main `da20713`) — the ORDER 004 rule-3 GAME-MECHANICS rotation slot, taken early because its consumer window (tonight's superbot minigame/casino consolidation, inbox ORDER 004 "World's balance pins") closes tonight. Build the fully hermetic pre-registered fairness-envelope sweep for house-banked wager minigames: integer-chip bankroll walks, B₀=1,000, min stake 1; archetypes G1/G2/G3 with payout k ∈ {1,5,19} and win probability p = (1−e)/(k+1) (EV per unit staked = −e exactly); house-edge grid e ∈ {0.01, 0.02, 0.05, 0.10} + e=0 control (reporting-only); max-bet caps MAXBET = m·B₀, m ∈ {0.05, 0.25, 1.0}, clipping every policy; 5 swept policies F-0.01/F-0.05/F-0.10 fixed-fraction, C constant-50, M capped-martingale base-10, plus the analytic-only constant-10 FUN reference leg; profiles CASUAL (100 bets; P_ahead, P_wipe), GRINDER (double-or-half, cap 4,000 bets, >1% cap-hits marks the cell indeterminate — a NULL path, never silently absorbed), COMPULSIVE (reporting-only, C policy, median bets-to-ruin); 36 envelope cells = 3 archetypes × 4 edges × 3 caps. Arm A (analytic, seedless, exact Fractions): exact binomial FUN tails via math.comb (ahead iff wins·(k+1) > 100), exact two-boundary gambler's-ruin closed forms for GRINDER on G1×C (unit steps of 50, start 10 above the lower boundary, span 30), e=0 control P_double = 1/3 exactly. Arm S (seeded MC): `random.Random(20260721)`, pinned loop order, M = 5,000 casual / 2,000 grinder / 500 compulsive per cell-policy, 1.0 pp Arm-A agreement gate, half-M stability leg seed 20260722. Then issue exactly ONE of REJECT (E* = ∅ at every cap in ≥ 2 of 3 archetypes, both arms where covered — checked FIRST) / APPROVE (∃ m* with ∩_g E*(g, m*) ⊇ 2 consecutive grid edges, stability-reproduced) / NULL (anything else — flip axis named via per-axis envelope shares) per the decision rule registered in the idea file BEFORE any code existed, with the bankroll-relative boundary and the V001/V008 earn-rate-baseline caveat restated verbatim.

## What happened

(in progress — fixtures-before-runner discipline: the pre-registration
`sims/verdict-022-casino-fairness/fixtures.json` lands before the runner is
written, per the V019/V020/V021 precedent)

## Run command

```
python3 sims/verdict-022-casino-fairness/casino_fairness_sim.py
```
