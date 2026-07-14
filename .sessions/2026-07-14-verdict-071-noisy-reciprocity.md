# Session — VERDICT 071 — Noisy reciprocity: does the Axelrod folk claim "Tit-for-Tat is the best strategy" survive the complete 16-rule deterministic memory-one field under trembling-hand execution noise? (idea-engine PROPOSAL 060, ORDER 003 COMPLETELY-UNRELATED rotation slot, round-11 closer)

> **Status:** complete
> 📊 Model: Claude Fable family · 2026-07-14 · verdict-071 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 060 (`## PROPOSAL 060 · 2026-07-14T05:55:31Z · status: sim-ready`, landed via idea-engine PR #404 → main 0d307cc; reservation this slice: idea-engine claim file `control/claims/claude-verdict-071-noisy-reciprocity.md` riding idea-engine PR #405; numbering INTAKE = proposal number, PROPOSAL 060 → VERDICT 071 per the established offset map P058→V069 / P059→V070) — compute the full exact 16 × 16 long-run value table, score table, and rank table of ALL 16 deterministic memory-one rules (c_CC, c_CD, c_DC, c_DD) ∈ {0,1}⁴ under trembling-hand execution noise ε ∈ {1/1000, 1/100, 1/20, 1/10} (decision cell ε = 1/100; controls ε = 1/2 degeneracy and ε = 0 orbit leg, both open C), stage game u(C,C)=3, u(C,D)=0, u(D,C)=5, u(D,D)=1. Arm A (DECISION, seedless): exact fractions.Fraction Gaussian elimination per ordered pair per ε (4 × 256 stationary solves) + ε = 0 orbit-cycle evaluator + ε = 1/2 check. Arm B (twin, seedless): independently-written Cramer/adjugate evaluator, must reproduce every v(i,j) EXACTLY. Arm R (seeded, REPORTING-ONLY, no statistical gate): finite-horizon tournament at ε = 1/100, 136 unordered pairs, T = 4,000, random.Random(20261377), 2 uniform draws per round; stability 20261378 at T = 1,000; presentation shuffle 20261379; aux 20261380 NEVER read. Decision rule pre-registered, applied IN ORDER: REJECT FIRST (score(WSLS) − score(TFT) ≥ 2/5 exact at ε = 1/100 AND v(TFT,TFT) = 9/4 exactly at EVERY grid ε AND rank(TFT) strictly worse than rank(WSLS) at EVERY grid ε AND v(WSLS,WSLS) ≥ 14/5 at ε = 1/100) → INVALID (F1 field & solve identities · F2 echo theorem · F3 closed-form anchors · F4 transpose conservation · F5 ε = 1/2 degeneracy · F6 battery — report, no ruling) → APPROVE (rank(TFT) = 1 at ε = 1/100 AND rank(TFT) ≤ rank(WSLS) at EVERY grid ε) → NULL (named axes: margin-straddle, noise-floor-conditional, echo-identity failure with gates passing, surviving twin-arm disagreement). Drafter's disclosed prototype landing (re-derived from scratch, ZERO trust, compared never gated): REJECT on all four conjuncts. Fully hermetic: the runner reads only its own fixtures.json (committed BEFORE the runner); zero repo/network reads at verdict time. Build subtree `sims/verdict-071-noisy-reciprocity/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 060 + VERDICT 071 appended to sim-lab `control/outbox.md` only; the parallel VERDICT 070 session's files/branch/PR #131 untouched). This card held the substrate gate red deliberately until this flip (the born-red discipline — that red was the ONLY red on this branch).

## What happened

Built `sims/verdict-071-noisy-reciprocity/` — fixtures.json (every registered
constant verbatim from the PROPOSAL 060 block / idea doc @ idea-engine
0d307cc; fixture-level choices C1–C9 — state/rule encoding, DENSE rank with
printed-table-only lexicographic ties, the Arm-A Gaussian system, the
differently-assembled Arm-B Cramer system, the ε = 0 limit-cycle-only orbit
convention, the Arm-R 2-draws-per-round grammar, canonical p/q serialization,
the nice-subfield restriction, the presentation-shuffle scope — all disclosed
IN the fixture BEFORE the runner existed). Git trail (PR #132): a0941e2
(born-red card) → ebff9a6 (fixtures) → a2219a1 (runner
noisy_reciprocity_sim.py + accepted run: results.json, run-stdout.txt,
README.md, REPORT.md) → 3440b1f (INTAKE 060 + VERDICT 071 ledger) → this
flip. Reservation: idea-engine claim PR #405 (claim-first) + born-red card
first commit + PR #132 READY; `VERDICT 071`/`INTAKE 060` grepped clean at
session start (49833d0) and re-grepped clean at fbb7046 immediately before
the ledger append (main moved mid-session: PR #131, the parallel VERDICT 070
slice landing exactly as pre-announced; origin/main merged INTO this branch,
never rebased).

**Run:** `SELF-CHECKS: 54 passed, 0 failed`, exit 0, ~4 s/run; stdout +
results.json byte-identical across two full process runs by external diff +
sha256 (run-stdout 105edaf4..., results 00b718d6...); CPython 3.11 pinned,
asserted; seeds 20261377/78/79 the ONLY RNGs constructed (pinned order), aux
20261380 never read (asserted); Arm-R draw sentinels exact (2T per game:
1,088,000 + 272,000); Arm B exact-equal on all 1,024 grid values; twin
decision evaluators agree REJECT/REJECT; F1–F6 all green.

**Ruling: REJECT** — all four pre-registered conjuncts fire on seedless exact
rationals. (1) gap = score(WSLS) − score(TFT) =
9345083308624553/19013690936000000 ≈ 0.4915 ≥ 2/5 at ε = 1/100. (2)
v(TFT,TFT) = 9/4 EXACTLY at every grid ε — the ε-independent echo identity,
F2-proved (uniform stationary), with the ε = 0 orbit value 3 as the
singular-perturbation exhibit. (3) rank(TFT) strictly worse than rank(WSLS)
at every grid ε (dense 9 vs 5, all four ε). (4) v(WSLS,WSLS) =
737773/250000 = 2.951092 ≥ 14/5. ALLD tops every noisy table (597/200 at
1/100) — uniform-field statement, no equilibrium claim. Falsifiability
behaved as registered: gap already below 2/5 at ε = 1/20 and 1/10; orbit gap
1/12 — the WSLS margin is noise-born. Anomalies, first-class: (A1) the
drafter's disclosed rank(TFT) = 10 is the COMPETITION-rank rendering — the
REGISTERED dense convention gives 9, because rules 3 = (0,0,1,1) and
12 = (1,1,0,0) tie at exactly 9/4 above TFT at every grid ε; ruling-neutral
(every rank clause is relational), reported not smoothed; every other
disclosed exact value reproduced digit-for-digit. (A2) Arm-R mixing-time
finding: max |finite-horizon − stationary| = 37359/37250 ≈ 1.0029 at pair
(4,12) — rule 12 repeats its own executed move, regime switches only via own
trembles, relaxation ~1/ε = 100 rounds; stability leg worse (1.218) —
exactly why Arm R was registered reporting-only.

**Previous-session review** (newest prior card,
`.sessions/2026-07-14-verdict-070-prestige-reset-policy.md`): V070's real
contribution to the discipline was diagnosing its disclosed F2 ±1 discrepancy
to the exact CONVENTION (boundary-action-at-t=H included vs excluded) instead
of waving it through as "close enough" — this session inherited that bar and
it paid immediately: the rank 10-vs-9 disclosure mismatch resolved to a named
convention fork (dense vs competition on a genuine tie) rather than a mystery.
Its card-template observation has now held a fourth consecutive session
unchanged; the promotion to a committed template is overdue and still
un-landed — that gap, not prose length, is now the template's real cost.

💡 **Session idea (genuine, this session):** the A1 anomaly generalizes to an
instrument rule for any pre-registered ranking claim: NEVER register a
decision clause on a rank INTEGER when ties are possible — rank conventions
(dense/competition/ordinal) fork exactly and only on ties, so a disclosed
landing and a registered instrument can silently disagree while both are
"right". Register order relations on the underlying exact scores instead
(rank(TFT) > rank(WSLS) is safe because it reduces to score(TFT) <
score(WSLS); rank(X) = 7 is not). This session's registration survived only
because all four clauses happened to be relational — P060's disclosed
"ranks 10/5" would have INVALIDated a hypothetical "rank(TFT) = 10" conjunct
on a correct implementation. Zero extra cost: the exact scores already exist
wherever a rank does.

📊 Model: Claude Fable family (self-reported by this session's harness;
family-level name only per the standing attribution doctrine).
