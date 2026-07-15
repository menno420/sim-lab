# Session — VERDICT 078 — outbox rollover stub saturation: the 200KB roll that is secretly a countdown (idea-engine PROPOSAL 065, the round-13 FLEET-BACKLOGS opener; P065 → V078 under the +13 offset)

> **Status:** complete
> 📊 Model: Claude Fable family · high · verdict-sim slice-worker session

Objective: produce VERDICT 078 for idea-engine PROPOSAL 065 (outbox rollover
stub saturation, `ideas/fleet/outbox-rollover-stub-saturation-2026-07-15.md`,
read at idea-engine origin/main `85114c5b6168e9ca5012ca35ad78556b4e56bf32`,
landed via idea-engine PR #428, head-ref branch head f9f328d). One slice, one
branch (`claude/2026-07-15-verdict-078-outbox-rollover-stub-saturation`,
PR #147), one verdict. NUMBERING, verified literally at sim-lab origin/main
`71337e2` (VERDICT 077 merged via PR #146): newest `## VERDICT` header was
077, `## VERDICT 078` and `## INTAKE 065` collision-grepped clean (outbox +
current-state + remote refs — no competing branch or PR), so idea-engine
PROPOSAL 065 → **VERDICT 078**, the +13 offset's second row (map row
extension landed in `docs/current-state.md` this same PR). Worker session;
`control/status.md` and `control/inbox.md` untouched (ledger appended to
`control/outbox.md` only; delivery is the manager's Q-0264 fan-in). This
card held the substrate gate red deliberately until this flip (the born-red
discipline — the designed hold was the only red this branch produced
itself).

## What happened

Built `sims/verdict-078-outbox-rollover-stub-saturation/` under the standing
discipline: fixtures.json committed BEFORE the runner (card 087002e →
fixtures cca1a6c → runner 41a3b64 → accepted run d374e59), fully hermetic
(every constant verbatim from the PROPOSAL 065 block / idea doc; zero
repo/network reads at verdict time), three-arm: Arm A seedless exact integer
recurrence over the full 3-policy × 81-cell grid (decision-bearing), Arm B
independently-written literal byte-ledger simulator (file size recomputed as
the sum of record sizes at every append; exact-equal on every published
number across all 243 cells), Arm R seeded size-mix walls (seeds
20261567–569, aux 20261570 asserted never read — the drafter's registered
allocation IS the session seed set, the V077 precedent; registry high-water
20261570). 33 self-checks 0 failed, exit 0, ~8 s/run; byte-identical double
run (sha256 in REPORT.md); CPython 3.11 asserted; no fix-forwards.

**VERDICT 078 — REJECT (the pre-registered predicted verdict, confirmed on
all three conjuncts, exact).** N\*_stub = 233 ≤ 300 (1.29×; the pipeline is
at 64, the wall dates to ≈ 2026-07-27 at the observed pace); 18 thrash rolls
≥ 8 (2.25×; collapse at roll 34 / proposal 209); N\*_range = 671 ≤ 932
(multiplier 2.88, 1.39×) while P-COMPACT held the constant floor 34,030 over
100,000 appends. All three structure theorems CONFIRMED as exact gates
(FLOOR LAW + roll-timing invariance; RECEIPT-FREE INVARIANCE wall = 386,
b-invariant; COMPACT BOUNDEDNESS), monotone thrash at every P-STUB cell.
Anomalies first-class: A1 — the drafter's F3 anchor text "first spacing 13 =
ceil((204800 − 32500)/16000)" contains an expression that evaluates to 11;
the correct expression is ceil((204800 − 500)/16000) = 13, value confirmed,
ruling-neutral. A2 — collapse "≈ 208" vs exact 209 (tilde-tagged), stub
share "59.4%" vs exact 59.4522% (truncation). 12/14 other disclosed rows
reproduced exactly. Arm-R named finding: the size mix pulls the wall
slightly REJECT-ward (mean ≈ 227.5, range 213–245 — far inside the straddle
band).

**Previous-session review** (previous session = VERDICT 077, sim-lab
PR #146): V077's closing recommendation — tag every disclosed-landing number
exact-vs-approximate — demonstrably worked where the P065 drafter adopted
it: the tilde on "≈ 208" let this session classify A2 instantly as a
disclosed approximation rather than a model disagreement. The gap it left is
exactly where this session's A1 landed: the recommendation covered VALUES
but not the inline derivation EXPRESSIONS that ride beside them in the
F-gate anchor lists, and an unchecked expression ("= ceil((204800 −
32500)/16000)") shipped inside an otherwise fully-machine-verified anchor
set. V077's A1 and V078's A1 are the same channel failing twice from two
sides (unlabeled approximation; unevaluated formula) — the fix belongs at
drafting time, not verdict time (💡 below).

💡 **Session idea (genuine, this session):** registration-time ANCHOR
SELF-EVALUATION — every disclosed anchor of the form "VALUE = EXPRESSION" in
a proposal's gate list should be machine-evaluated by the DRAFTER before the
proposal lands: run each inline formula, assert it equals its own stated
value, and tag it `[checked]`. The pattern is now two-for-two across
consecutive verdicts (V077 A1: an unlabeled steady-state approximation;
V078 A1: a derivation expression evaluating to 11 beside its anchored value
13) — both were caught only because the verdict session re-derived
everything from scratch, and both were ruling-neutral only by luck of the
gate design (values gated, prose not). Dedup: distinct from V077's 💡
(per-episode representation-equivalence for seeded arms — a verdict-side
runner convention); this one is a drafter-side proposal-lint. Concretely for
the kit: add "machine-evaluate every inline anchor expression at
registration; a formula that cannot be evaluated verbatim is not an anchor"
to the proposal template's F-gate checklist. Cheap (the drafter's prototype
already computes every value), and it turns the disclosed-landing channel
from prose-with-numbers into checked arithmetic end to end.

📊 Model: Claude Fable family (self-reported by this session's harness;
family-level name only per the standing attribution doctrine).
