# Session — VERDICT 079 — kill-clock anchor vs owner-gated funnel onset: the T+14 window that measures click latency, not viability, once the funnel wires late (idea-engine PROPOSAL 066, the round-13 VENTURE slot, products half; P066 → V079 under the +13 offset)

> **Status:** complete
> 📊 Model: Claude Fable family · high · verdict-sim slice-worker session

Objective: produce VERDICT 079 for idea-engine PROPOSAL 066 (kill-clock
anchor vs owner-gated funnel onset,
`ideas/venture-lab/kill-clock-anchor-truncated-exposure-2026-07-15.md`, read
at idea-engine origin/main `848d6de70532520cc0cd310fd2a669094ba3b68a`, landed
via idea-engine PR #429; outbox block stamped 2026-07-15T05:44:53Z). One
slice, one branch (`claude/2026-07-15-verdict-079-kill-clock-anchor`,
PR #148), one verdict. NUMBERING, verified literally at sim-lab origin/main
`b7a6859` (VERDICT 078 merged via PR #147): newest `## VERDICT` header was
078, `## VERDICT 079` and `## INTAKE 066` collision-grepped clean (outbox +
current-state + remote refs — no competing branch or PR;
`claude/verdict-061-kill-clock` is the old V061 branch, unrelated), so
idea-engine PROPOSAL 066 → **VERDICT 079**, the +13 offset's third row (map
row extension landed in `docs/current-state.md` this same PR). Worker
session; `control/status.md` and `control/inbox.md` untouched (ledger
appended to `control/outbox.md` only; delivery is the manager's Q-0264
fan-in). This card held the substrate gate red deliberately until this flip
(the born-red discipline — the designed hold was the only red this branch
produced itself).

## What happened

Built `sims/verdict-079-kill-clock-anchor/` under the standing discipline:
fixtures.json committed BEFORE the runner (card 152fccb → fixtures 5393a31 →
runner 20b101f → accepted run 53bec50), fully hermetic (every constant
verbatim from the PROPOSAL 066 block / idea doc; zero repo/network reads at
verdict time), three-arm: Arm A seedless exact-Fraction schedule sums over
the full grid (decision-bearing), Arm B independently-written literal
calendar day-walk simulator (window membership as date comparison, FK by
repeated multiplication; exact-equal on every published number), Arm R
seeded literal Bernoulli visit traces (seeds 20261580–582, aux 20261583
asserted never read — the drafter's registered allocation IS the session
seed set, the V077/V078 precedent; registry high-water 20261583; the
20261571–579 gap was the drafter's disclosed V078 buffer, unused). 32
self-checks 0 failed, exit 0, ~28 s/run; byte-identical double run (sha256
in REPORT.md); CPython 3.11 asserted; no fix-forwards.

**VERDICT 079 — REJECT (the pre-registered predicted verdict, confirmed on
all three conjuncts, exact).** FK(τ=13) = (99/100)^60 ≈ 0.547157 ≥ 1/2
(1.0943× — the thin registered margin, re-derived exactly, no benefit of
the doubt needed) with FK(τ=0) ≈ 0.145197 ≤ 1/5 (1.3774× under); doubling
onset τ = 13 ≤ 13 (τ = 10 at 1.9608×, one grid step below — the registered
knife-edge confirmed); A-CAP30 exactly flat through every grid τ ≤ 16 at
occupancy ≤ 30. All three window theorems CONFIRMED as exact gates
(ANCHOR INVARIANCE; SPIKE STEP; CAP-30 EQUIVALENCE + BOUNDEDNESS), plus
monotone truncation with the τ ≥ 14 certainty row. Falsifiability behaved
as registered: SPIKE lands the APPROVE clauses exactly, both q edges land
outside R1, DRIP FK(0) = 0.754719. **Zero anomalies** — all 20
drafter-disclosed landing values reproduced exactly at stated precision;
the V077/V078 A1/A2 channel is empty this slice.

**Previous-session review** (previous session = VERDICT 078, sim-lab
PR #147): V078's 💡 — registration-time anchor self-evaluation, machine-run
every disclosed "VALUE = EXPRESSION" before the proposal lands —
demonstrably closed the loop: P066 shipped a 20-value disclosed landing
with no derivation-text slips and this session's comparison came back
20/20, the first zero-anomaly disclosed-landing check since the convention
started catching slips (V077 A1, V078 A1/A2). The gap V078 left: values now
arrive drafter-checked but still as PROSE — this session had to extract the
R1 margins by string surgery on "0.547157 >= 1/2 at 1.094x" / "1.377x
under" and infer each value's comparison precision from its repr (convention
C9, improvised verdict-side). The channel is checked arithmetic wrapped in
an unchecked serialization (💡 below).

💡 **Session idea (genuine, this session):** a STRUCTURED DISCLOSED-LANDING
SCHEMA — proposals should ship their disclosed landing as a small
machine-readable block (value, exact form where known, stated precision,
comparison operator), not as prose with embedded numerals. Two measured
prompts from this slice: (a) the R1/R2 margin disclosures had to be parsed
out of prose strings and their precisions guessed from float repr — a
fragile layer that would misclassify a drafter who wrote "1.0940x" instead
of "1.094x"; (b) the registered Arm-B mechanics ("walks calendar days
1..60") could not serve the conservation gate it rides beside (DRIP's 730
visits extend past day 60) — patched as disclosed convention C3, but a
schema field pairing each registered procedure with the gates it must
serve would have caught the seam at drafting. Dedup: distinct from V077's
💡 (verdict-side per-episode representation equivalence for seeded arms)
and from V078's 💡 (drafter-side self-evaluation of inline expressions —
this idea is the serialization layer AROUND that now-working check).
Concretely for the kit: the proposal template's disclosed-landing section
becomes a JSON/table block the drafter's prototype emits directly and the
verdict runner diffs mechanically — the comparison code stops being
re-improvised every verdict session (C9 here, C11 in V078) and the
prose-parsing failure mode disappears end to end.

📊 Model: Claude Fable family (self-reported by this session's harness;
family-level name only per the standing attribution doctrine).
