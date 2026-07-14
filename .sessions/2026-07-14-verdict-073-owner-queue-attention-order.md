# Session — VERDICT 073 — Owner-queue attention order: is the derived publish queue's committed presentation (decisions-first with the one-reply "go with defaults" door, then document order) attention-near-optimal against the classical sequencing alternatives on its own committed click counts? (idea-engine PROPOSAL 062, ORDER 003 VENTURE rotation slot, round 12, BOOKS half)

> **Status:** complete
> 📊 Model: Claude Fable family · 2026-07-14 · verdict-073 slice-worker session

Objective: serve idea-engine `control/outbox.md` PROPOSAL 062 (`## PROPOSAL 062 · 2026-07-14T08:19:10Z · status: sim-ready`, landed via idea-engine PR #410 → main be34370, merged 2026-07-14T08:22:59Z; reservation this slice: idea-engine claim file `control/claims/claude-verdict-073-owner-queue-attention-order.md` riding idea-engine PR #412, merged at idea-engine main b8173be; numbering INTAKE = proposal number, PROPOSAL 062 → VERDICT 073 per the established offset map P060→V071 / P061→V072) — compute, in fully deterministic exact arithmetic (integer prefix sums + `fractions.Fraction`), the complete five-policy × two-accounting attention table for venture-lab's derived owner queue `docs/publishing/OWNER-QUEUE.md` @ 68d57bb (44 committed publish sequences totalling 262 unchecked owner clicks, 16 hard-gated, plus the 19-decision layer; policies DOC / SPT / LPT / LAZY-DOC / LAZY-SPT; accountings BATCHED layer = 1 interaction vs PER-ITEM = 19; metrics L_π(t), TTF, T22, MEAN exact Fraction, V_γ = Σ γ^{C_i} exact Fraction at γ ∈ {49/50, 99/100, 199/200}, decision cell γ = 99/100), the two sequencing theorems as gates on the real committed data (EXCHANGE — all 43 adjacent transpositions of SPT weakly worsen MEAN and V_γ at every grid γ; POINTWISE DOMINANCE — L_SPT ≥ L_DOC and ≥ L_LPT at every t, L_LAZY-SPT ≥ L_LAZY-DOC pointwise), the batch-door price (the same-order cost of forgoing the one-reply defaults path), the LPT anchor, the γ = 49/50 crossing check, and the V020-exclusion re-evaluation leg. Arm A (DECISION, seedless): exact integer prefix sums + Fraction V_γ. Arm B (twin, seedless): INDEPENDENTLY-WRITTEN event-walk stepping the owner clock one interaction at a time — must reproduce every Arm-A number EXACTLY. Arm R (seeded, REPORTING-ONLY, no statistical gate): owner-sitting traces, budgets i.i.d. from the pinned pmf {3: 1/2, 8: 3/10, 21: 1/5} — main `random.Random(20261385)` N = 100,000 episodes per policy (one pmf uniform per sitting, draw counts counted and asserted), stability 20261386 at N = 20,000, presentation shuffle 20261387, aux 20261388 reserved and NEVER read. Decision rule pre-registered, applied IN ORDER on the BATCHED best-non-DOC comparisons: REJECT FIRST (ANY of R1 gapMEAN ≥ 10, R2 ratioV(99/100) ≥ 11/10, R3 TTF(DOC) ≥ 3× TTF(best)) → INVALID (F1 data identity · F2 conservation · F3 sequencing theorems · F4 hand world · F5 γ-monotonicity · F6 battery — report, no ruling) → APPROVE (ALL of A1 gapMEAN(BATCHED) ≤ 8, A2 ratioV(99/100) < 11/10, A3 TTF ≤ 2×, A4 gapMEAN(PER-ITEM) ≥ 15, A5 TTF(DOC, PER-ITEM) ≥ 4× TTF(best, PER-ITEM)) → NULL (named axes: order-insensitive, band straddle, γ-conditional, twin-arm disagreement). Drafter's disclosed prototype landing (re-derived from scratch, ZERO trust, compared never gated): APPROVE on all five conjuncts. Fully hermetic: the runner reads only its own fixtures.json (committed BEFORE the runner); zero repo/network reads at verdict time. Build subtree `sims/verdict-073-owner-queue-attention-order/`. Worker session; `control/inbox.md`, both status heartbeats, and idea-engine's outbox untouched (the verdict ledger is canonical HERE — INTAKE 062 + VERDICT 073 appended to sim-lab `control/outbox.md` only). This card held the substrate gate red deliberately until this flip (the born-red discipline — that red was the only red this branch produced itself; mid-session the ORDER 006 rollover landed a newer complete card on main, so commits 4–5 were pushed together to close the gap the mtime-keyed gate opened).

## What happened

Built `sims/verdict-073-owner-queue-attention-order/` — fixtures.json (every
registered constant verbatim from the PROPOSAL 062 block / idea doc @
idea-engine b8173be; fixture-level choices C1–C12 — the document-order
tie-break, completion/live-curve semantics, the Arm-A prefix-sum closed
forms, the Arm-B tick-walk state machine with its own selection-loop order
builders, the twin-evaluator split, the Arm-R chunked sitting-walk draw
grammar, canonical p/q serialization, T22 = the 22nd completion clock, the
presentation-shuffle scope, the exclusion-leg rebuild rule, best-non-DOC
comparison semantics, both-accounting theorem coverage — all disclosed IN
the fixture BEFORE the runner existed). Git trail (PR #135): 21296fa
(born-red card) → 673d133 (fixtures) → 1a72cd0 (runner
owner_queue_attention_order_sim.py + accepted run: results.json,
run-stdout.txt, README.md, REPORT.md) → c16b878 (origin/main merged INTO
this branch — PR #134 the ORDER 006 outbox rollover + PR #136, landed
mid-session; never rebased) → cbdaaf7 (INTAKE 062 + VERDICT 073 ledger) →
this flip. Reservation: idea-engine claim PR #412 (claim-first, merged
08:42:41Z) + born-red card first commit + PR #135 READY; `VERDICT
073`/`INTAKE 062` grepped clean at origin/main 03b81fc at session start and
re-grepped at c16b878 immediately before the ledger append (the rollover
pointer's "next VERDICT 073, INTAKE 062" line is the sole mention — it
confirms the numbering).

**Run:** `SELF-CHECKS: 117 passed, 0 failed`, exit 0, ~18 s/run; stdout +
results.json byte-identical across two full process runs by external diff +
sha256 (run-stdout 72e3df99..., results f79c1fce...); CPython 3.11 pinned,
asserted; seeds 20261385/86/87 the ONLY RNGs constructed (pinned order), aux
20261388 never read (asserted); Arm-R draw sentinels exact (one uniform per
sitting: 16,625,466 + 3,325,706); Arm B (independently-written tick-walk)
exact-equal on every published number (10 main + 10 hand + 10 exclusion
cells); twin decision evaluators agree APPROVE/APPROVE; F1–F6 all green
(incl. the 43-transposition exchange theorem with each swap's MEAN delta
asserted exactly = (n_j − n_i)/44, and pointwise dominance at every t).

**Ruling: APPROVE** — all five pre-registered conjuncts hold on seedless
exact arithmetic. (1) gapMEAN(BATCHED) = 2835/22 − 2691/22 = 72/11 ≈ 6.545
≤ 8 (best: SPT). (2) ratioV(99/100) ≈ 1.068090 < 11/10. (3) TTF 7 ≤ 2 × 4.
(4) gapMEAN(PER-ITEM) = 188/11 ≈ 17.091 ≥ 15 (best flips to LAZY-SPT). (5)
TTF(DOC, PER-ITEM) = 25 ≥ 4 × 5. The committed decisions-first + document
order is attention-near-optimal ONLY through its own batch door, and the
door is load-bearing: +18 mean interactions EXACTLY and 25/7 ≈ 3.57×
time-to-first-title at the same order; the near-optimality is mostly
inherited structure (the residual sort gain is only ≈ 6.5), LPT anchors the
worst sort at 1624/11 ≈ 147.64, the γ = 49/50 leg crosses at ≈ 1.1341
(named, reporting-only — falsifiability behaved as registered), and the
V020-exclusion leg re-lands every clause identically. Anomalies: none —
every drafter-disclosed value reproduced from scratch, 20/20, never gated.

**Previous-session review** (newest prior verdict card,
`.sessions/2026-07-14-verdict-072-plan-depth-jitter.md`): V072's
first-class handling of a drafter-disclosure mismatch (the 0.751 "per dry
cycle" mislabel, resolved to a named quantity fork instead of smoothed
over) set the compare-never-gate bar this session ran under — the full
20-value drafter comparison table was built before the run and landed
20/20 with zero mismatches, so the anomaly section is honestly empty
rather than unexamined; and its 💡 (size safety stock on lag INCREMENTS —
the sufficient-statistic move) is the same shape this session's batch-door
finding takes: the decision-relevant quantity was never the list order,
it was which DOOR the owner walks through.

💡 **Session idea (genuine, this session):** the batch-door decomposition
generalizes to an audit rule for ANY derived checklist with a gate layer:
price every surface twice — once through its cheapest committed reading
(one batched reply) and once through naive item-by-item service — and
report the SPREAD as the document's "door price" alongside the sort gap.
On this queue the door price (+18 mean, 3.57× TTF) dwarfs the sort gap
(6.5 mean) by ~3×, and the LAZY rows show WHY: deferral shields every
ungated item from the layer entirely (their door price is 72/11, not 18).
Practical consequence: a derived to-do surface should emit its own door
price as one generated header line (the deriver already knows n_i and the
gate map), so the owner sees "reply 'go with defaults' first — it is worth
K interactions" as measured fact, not etiquette — and a surface whose door
price is ~0 should NOT front its decision layer at all (LAZY dominates
there by construction).

📊 Model: Claude Fable family (self-reported by this session's harness;
family-level name only per the standing attribution doctrine).
