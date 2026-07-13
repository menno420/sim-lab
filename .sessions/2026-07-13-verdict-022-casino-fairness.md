# Session — VERDICT 022 — casino fairness envelope (idea-engine PROPOSAL 020)

> **Status:** `complete`
> 📊 Model: fable · 2026-07-13 · verdict-022 slice-worker session
> Objective: settle idea-engine PROPOSAL 020 (control/outbox.md · 2026-07-13T02:04:02Z · status: sim-ready; idea `ideas/superbot/casino-house-edge-fairness-envelope-2026-07-13.md`, landed via idea-engine PR #286, main `da20713`) — the ORDER 004 rule-3 GAME-MECHANICS rotation slot, taken early because its consumer window (tonight's superbot minigame/casino consolidation, inbox ORDER 004 "World's balance pins") closes tonight. Build the fully hermetic pre-registered fairness-envelope sweep for house-banked wager minigames: integer-chip bankroll walks, B₀=1,000, min stake 1; archetypes G1/G2/G3 with payout k ∈ {1,5,19} and win probability p = (1−e)/(k+1) (EV per unit staked = −e exactly); house-edge grid e ∈ {0.01, 0.02, 0.05, 0.10} + e=0 control (reporting-only); max-bet caps MAXBET = m·B₀, m ∈ {0.05, 0.25, 1.0}, clipping every policy; 5 swept policies F-0.01/F-0.05/F-0.10 fixed-fraction, C constant-50, M capped-martingale base-10, plus the analytic-only constant-10 FUN reference leg; profiles CASUAL (100 bets; P_ahead, P_wipe), GRINDER (double-or-half, cap 4,000 bets, >1% cap-hits marks the cell indeterminate — a NULL path, never silently absorbed), COMPULSIVE (reporting-only, C policy, median bets-to-ruin); 36 envelope cells = 3 archetypes × 4 edges × 3 caps. Arm A (analytic, seedless, exact Fractions): exact binomial FUN tails via math.comb (ahead iff wins·(k+1) > 100), exact two-boundary gambler's-ruin closed forms for GRINDER on G1×C (unit steps of 50, start 10 above the lower boundary, span 30), e=0 control P_double = 1/3 exactly. Arm S (seeded MC): `random.Random(20260721)`, pinned loop order, M = 5,000 casual / 2,000 grinder / 500 compulsive per cell-policy, 1.0 pp Arm-A agreement gate, half-M stability leg seed 20260722. Then issue exactly ONE of REJECT (E* = ∅ at every cap in ≥ 2 of 3 archetypes, both arms where covered — checked FIRST) / APPROVE (∃ m* with ∩_g E*(g, m*) ⊇ 2 consecutive grid edges, stability-reproduced) / NULL (anything else — flip axis named via per-axis envelope shares) per the decision rule registered in the idea file BEFORE any code existed, with the bankroll-relative boundary and the V001/V008 earn-rate-baseline caveat restated verbatim.

## What happened

Built `sims/verdict-022-casino-fairness/` — a stdlib-only NUMERIC SIMULATION
(rung 1), fully hermetic: the sim reads exactly one file (its own committed
`fixtures.json` pre-registration, cross-checked at start) and touches no repo
state, network, or wall clock. The pre-registration (all constants verbatim
from the idea file, the pinned loop/draw order, the decision rule with
evaluation order, two hand-derived pin scenarios with derivations, and eight
disclosed intake-time decisions) was committed BEFORE the runner was written.
One honest amendment inside that discipline: a throwaway-seed M=200 smoke run
exposed that the drafted e=0 fairness self-check (mean-final t-check) is
statistically invalid on the heavy-tailed k=19 fixed-fraction legs (sample SD
under-estimates the true SD; false alarms on a fair game) — replaced with the
win-indicator Wald martingale check and disclosed in fixtures.json BEFORE any
pinned-seed run; the decision machinery was untouched.

**Run output summary:** `SELF-CHECKS: 13392272 passed, 0 failed`, exit 0,
stdout + results.json byte-identical across two full process runs (external
diff), cpython-3.11 pinned, ~72 s. **Ruling: REJECT — odds cannot do the
job.** Evaluated first per the registered order and decisive: E*(g, m) = ∅ in
all 36 cells, at every cap, in 3/3 archetypes (bar: 2/3), reproduced by the
half-M fresh-seed stability leg. The anatomy is sharper than the proposal
guessed: the expected NULL candidate (even-money empties while jackpot holds
a band) is INVERTED — G2/G3 (k=5/19) are the unfixable ones (SINK worst-policy
P_double 0.195–0.323 vs 0.10 at EVERY edge and cap; the edge barely moves
p = (1−e)/(k+1) at high k, so grinder doubling is variance-dominated), while
even-money G1 is the only edge-controllable shape and its near-miss cell
(e=0.05, m=0.05: FUN 0.2738 exact, SINK 0.0895) dies on SAFE (flat-50 wipe
0.1358, 2.7× the band — variance again, wipe 5.7% even at e=0). Agreement
gate PASS (pooled per-edge deviations 0.051–0.720 pp vs 1.0 pp; e=0 control
= 1/3 exactly in both analytic derivations). Consequence routed: the
consolidation does not tune per-game odds; rake-only PvP framing (priced free
by the G1-at-e=r identity), session comp/stipend, and entry-fee-with-prize
ride to the World seat with the quantified per-archetype gap.

Slice boundary this cycle (the V015–V021 precedent): this session carries the
INTAKE 020 and VERDICT 022 control/ appends itself; control/status.md stays
coordinator-only and is untouched; control/inbox.md untouched (manager-order
file). The tail at append was the INTAKE 018 / VERDICT 020 relocation echo
(@ a7edcad) — numbering unaffected, +2 offset preserved (P020 → V022),
origin/main re-checked immediately before the append (no race). No @codex
step — suspended per the outbox codex-line escalation @ dedc12e. Born-red
card and complete flip land in one push (the V018–V021 choreography).

## Run command

```
python3 sims/verdict-022-casino-fairness/casino_fairness_sim.py
```

## 💡 Session idea

Smoke-test the SELF-CHECKS on a throwaway seed before the pinned run, and
treat a self-check that CAN false-alarm as a bug in the check, not noise to
absorb: the mean-final t-check looked airtight (4 SE!) but is invalid
exactly where the model is most interesting (heavy-tailed legs), and it
would have poisoned the pinned run with 0-failed-expected noise. The
portable rule: for martingale-fairness controls on stopped walks, test the
BOUNDED-increment martingale (the win indicator, Wald variance p(1−p)·E[bets])
rather than the value process — the value process's variance is what the
sim exists to measure, so assuming it for a control is circular. Also
exportable: when a pre-registered MC-vs-analytic gate is written without a
noise budget (1.0 pp at M=2,000 ≈ 1 SE per cap-leg here), the honest move is
to commit the granularity reading BEFORE the runner (pooling the
cap-independent legs that measure the identical quantity) and report the
raw per-leg deviations anyway — interpreting a gate is intake work, not
post-hoc work.

## ⟲ Previous-session review

Prior card `2026-07-13-verdict-021-backlog-low-water.md`: complete, honest,
and its exports are adopted here directly. (1) The one-push born-red
choreography is followed verbatim. (2) Fixtures-before-runner, including
hand-derived pins WITH derivations committed before code — reused (two pins:
the seven-loss martingale wipe, the two-win jackpot double under the tight
cap). (3) Its trace-replay twin + twin decision evaluators pattern — reused
and extended with per-bet stake-bound assertions inside the twin. (4) Its
draw-count accounting identity — strengthened here to an exact stream
sentinel (fresh Random(seed), skip exactly total-bets draws, next draw must
equal the recorded sentinel; closes at 247,448,560 + 123,439,648 draws). One
improvement carried forward rather than copied: V021's analytic
corroboration of a surprising row becomes a full analytic ARM here (the
proposal pre-registered it), which is what let the gate catch — or here,
clear — the MC before any cell was believed.
