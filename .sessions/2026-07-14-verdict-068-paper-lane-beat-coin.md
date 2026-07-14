# Session — VERDICT 068 — The paper lane's BEAT coin: does trade P&L cancel exactly out of trading-strategy's committed cycle-window verdict grammar, where does the zero-skill BEAT coin sit under drift, and can the committed "verdicts are counted" grammar see honest skill at first-year n? (idea-engine PROPOSAL 057, ORDER 003 FLEET-BACKLOGS rotation slot, round 11 opener)

> **Status:** complete
> 📊 Model: fable-family · 2026-07-14 · verdict-068 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 057 (`## PROPOSAL 057 · 2026-07-14T03:30:10Z · status: sim-ready`, landed via idea-engine PR #391 → main 665dca9c458ba4e90f63c138b9c638189d403183; reservation this slice: idea-engine claim file `control/claims/claude-verdict-068-paper-lane-beat-coin.md` riding idea-engine PR #393; numbering INTAKE = proposal number, PROPOSAL 057 → VERDICT 068 per the established +11 offset map P050→V061 … P056→V067) — price trading-strategy's pre-registered paper-lane grading grammar (docs/paper-lane-protocol.md §7 cycle-window BEAT/MISS comparator, §9 A5/A6, 6 bps/side · $10,000 notional, all @ d857e50ad7bc32bed5b2999cce16b4bf8a37246e) at the proposal's pinned model: (i) the exact-cancellation identity gate (BEAT ⟺ R_F < 1, zero exceptions over the full enumerated lattice, both cost accountings), (ii) the exact null coin B(δ, drift) per drift cell, (iii) the exact one-sided Neyman–Pearson count-test power at n = 8, size ≤ 1/20, NULL vs SKILL at the committed drift, plus the n*₅₀/n*₈₀ rows in windows and calendar years. Pinned model verbatim from the idea file: X = 101/100 w.p. p_up else 99/100 (s = 1/100), drift grid p_up ∈ {1/2 ZERO, 13/25 COMMITTED, 27/50 DOUBLE}; F ~ {6: 1/4, 12: 1/2, 24: 1/4}, T ~ {4: 1/4, 8: 1/2, 16: 1/4}, F ⊥ T, mean cycle 45/2 days ⇒ 16.8 windows/18 months; skill = flat-day up-prob p_up − δ, δ ∈ {0 NULL, 1/25 SKILL decision, 2/25 and −1/25 reporting}; n ∈ {8 decision, 16, 34 reporting}. Arm A = DECISION (seedless exact `fractions.Fraction`/integer lattice + binomial arithmetic, per-F thresholds k*(F), the 101-prime no-tie theorem, exact NP tests, exact EV rows E[Δ$] ∝ E[R_T]·(1 − E[R_F])); Arm S = confirmation (seed 20261365: N = 200,000 cycles per decision world, pinned draw order F draw → F daily coins (+ the disclosed T-block extension for protocol-arithmetic evaluation), CRN across δ worlds, 50,000 8-window seasons for the power row; agreement gate |EST − EXACT| ≤ 1/100 absolute AND ≤ 4·SE on every decision cell); stability seed 20261366 (N = 20,000, twin independently-written decision evaluators); reporting seed 20261367 (s pairs {1/200, 1/50}, F-mix pairs, δ = 2/25/−1/25, n ∈ {16, 34}, EV rows, dollar-accounting bound — reporting legs only); aux seed 20261368 reserved, NEVER constructed. Decision rule pre-registered, applied IN ORDER: REJECT FIRST ((a) identity zero exceptions AND (b) B(NULL, COMMITTED) ≥ 13/25 AND (c) NP power at n = 8 < 1/2 AND (d) Arm S confirms within the agreement gate on every decision cell) → INVALID (F1–F5 controls, draw sentinels, twin-evaluator disagreement, any agreement breach — report, no ruling) → APPROVE (power ≥ 4/5 at n = 8 AND B(NULL, COMMITTED) ≤ 1/2 AND stability reproduces through twin evaluators) → NULL (power-straddle / coin-straddle / sensitivity-conditional / surviving arm disagreement — named axes, never a re-run request). Drafter's disclosed landing (re-derived from scratch, zero trust, compared never gated): REJECT on all four conjuncts — B(NULL, COMMITTED) = 1985628207794352919031012090343552/3552713678800500929355621337890625 ≈ 0.5589, power(n = 8) ≈ 0.0406 (critical count 8-of-8), B(SKILL) ≈ 0.6701, B(NULL, ZERO) = 20656327/33554432 ≈ 0.6156, DOUBLE-drift B ≈ 0.5012 below the 13/25 edge, n*₅₀ ≈ 56 windows (~5 years), n*₈₀ ≈ 124 (~11 years). Fully hermetic: the runner reads only its own fixtures.json (committed BEFORE the runner); zero repo/network reads at verdict time. Build subtree `sims/verdict-068-paper-lane-beat-coin/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 057 + VERDICT 068 appended to sim-lab `control/outbox.md` only). This card holds the substrate gate red deliberately until the final flip (the born-red discipline — that red is the ONLY acceptable red on this branch).

## What happened

Built `sims/verdict-068-paper-lane-beat-coin/` — fixtures.json (every
registered constant verbatim from the PROPOSAL 057 block / idea doc @
idea-engine 665dca9; fixture-level choices C1–C9 — the T-block draw-order
extension asserted decision-irrelevant per cycle, the CRN threshold reading,
exact-lattice-table MC evaluation with no float comparison on any decision
path, the stability-reproduces-or-INVALID parse, the ungated size row, the
EV convention, the sensitivity tie rule — all disclosed IN the fixture BEFORE
the runner existed). Git trail (PR #126): fa5d4d1 (born-red card) →
f17a164 (fixtures) → e9e4d76 (runner paper_lane_beat_coin_sim.py + accepted
run: results.json, run-stdout.txt, README.md, REPORT.md) → 15bcd99
(INTAKE 057 + VERDICT 068 ledger) → this flip. Reservation: idea-engine claim
PR #393 (claim-first) + born-red card first commit + PR #126 READY;
`VERDICT 068`/`INTAKE 057` grepped clean at session start (311c461) and
re-grepped clean at 311c461 immediately before the ledger append (main never
moved this session). The drafting pin trading-strategy @ d857e50 was
independently re-verified at intake via a fresh shallow clone landing exactly
at d857e50 (§7 quotes, config.py:60–61, the :217 trade-rate line, the single
paper-0001 WATCH row — all verbatim); the verdict sim itself read none of it.

**Run:** `SELF-CHECKS: 68 passed, 0 failed`, exit 0, ~22 s/run; stdout +
results.json byte-identical across two full process runs by external sha256
(run-stdout 9cfe2b08..., results 910e562c...); CPython 3.11 pinned, asserted;
seeds 20261365/66/67 the ONLY RNGs constructed (never-construct aux hygiene,
the V066/V067 pattern), aux 20261368 never read; draw sentinels exact
(2N + sum-F + sum-T per drift block); twin evaluators 0 mismatches over all
1395 lattice points and every MC cycle; F1–F5 control gates all green.

**Ruling: REJECT** — all four pre-registered conjuncts fire. (a) BEAT ⟺
R_F < 1 with zero exceptions over the full lattice, both accountings, 0 sign
flips, 0 ties (101 prime — A5 never fires in-world): the trade's own P&L
cancels exactly out of the committed verdict. (b) B(NULL, COMMITTED) =
1985628207794352919031012090343552/3552713678800500929355621337890625 ≈
0.558905 ≥ 13/25 — the null coin is not conservative; the zero-skill trader
BEATs 55.9% of windows while losing $54.33/cycle expected to B&H (EV rows
side by side as registered; DOUBLE-drift control 0.501206 lands below the
edge, ZERO-drift closed form 20656327/33554432 exact). (c) exact NP power at
n = 8 is 0.040650, critical count 8-of-8; n*₅₀ = 56 windows = 5.00 yr,
n*₈₀ = 124 = 11.07 yr; strong skill still 0.121. (d) Arm S confirms on every
decision cell (worst dev 0.001170); stability leg reproduces REJECT through
both twin evaluators. Every drafter-disclosed exact value reproduced from
scratch, never gated — digit-for-digit including the 34-digit numerator.
First-class reporting finding: the registered s-pair {1/200, 1/50} leaves the
coin EXACTLY invariant (k*(F) = F/2 at every registered s) — vol scale moves
R_F's magnitude, never the median-threshold count rule; the F-mix pairs move
the coin exactly as vol drag predicts (0.580933 / 0.537470, both ≥ 13/25).

**Previous-session review** (newest prior card,
`.sessions/2026-07-14-verdict-067-inspection-paradox.md`): V067's headline
lesson — a registered agreement gate whose relative-1/100 half is
under-powered at the registered N makes INVALID the modal outcome of a
perfect sim — was applied here at registration time, not discovered at run
time: PROPOSAL 057 registered its gate as 1/100 ABSOLUTE (not relative) AND
4·SE, which at N = 200,000 gives ~9σ headroom on the coin cells, and the
stability-leg parse (C4) was pinned in fixtures before the runner. The V067
card's guard recipe held: no gate artifact fired this session, and the class
landed on the science, not the harness.

💡 **Session idea (genuine, this session):** the identity proof suggests a
zero-cost protocol hardening for ANY comparator-graded lane: publish the
verdict statistic in its REDUCED form (here: "BEAT ⟺ flat-segment market
return < 0") alongside the operational definition. If the reduced form
surprises the lane owner, the grammar is measuring something other than what
the prose implies — a one-line disclosure that would have surfaced the
P&L-cancellation years before any sim. Candidate kit lint: flag any
pre-registered comparator whose two sides share a common multiplicative
factor (the cancellation is then structural, not empirical).

📊 Model: fable-family (self-reported by this session's harness; family-level
name only per the standing attribution doctrine).
