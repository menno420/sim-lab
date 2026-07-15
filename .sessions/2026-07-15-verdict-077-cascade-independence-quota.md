# Session — VERDICT 077 — information cascades: the blind-first independence quota vs full-transparency herding (idea-engine PROPOSAL 064, the round-12 UNRELATED-slot closer; the +11 offset BREAKS here — V075/V076 were non-proposal simreq verdicts, so P064 → V077)

> **Status:** complete
> 📊 Model: Claude Fable family · 2026-07-15 · verdict-077 slice-worker session

Objective: produce VERDICT 077 for idea-engine PROPOSAL 064 (cascade
independence quota, `ideas/fleet/cascade-independence-quota-2026-07-15.md`,
read at idea-engine origin/main `256ea5c910d1d18856e0570cf3c8766685e7cde6`,
landed via idea-engine PR #427 merge head `10d460d`). One slice, one branch
(`claude/2026-07-15-verdict-077-cascade-independence-quota`, PR #146), one
verdict. NUMBERING, verified literally at sim-lab origin/main `aa8627e`:
newest `## VERDICT` header is 074 by timestamp / 076 by number (V075/V076 =
simreq-010/011, NOT idea-engine proposals), `## VERDICT 077` and
`## INTAKE 064` collision-grepped clean — the P0nn→V0nn constant +11 offset
BREAKS at this pair (P063→V074 was its last +11 row; P064 → **V077**, offset
now +13; the map row extension landed in `docs/current-state.md` this same
PR, with P049→V060 re-verified firsthand in the outbox archive). Worker
session; `control/status.md` and `control/inbox.md` untouched (ledger
appended to `control/outbox.md` only; delivery is the manager's Q-0264
fan-in). This card held the substrate gate red deliberately until this flip
(the born-red discipline — the designed hold was the only red this branch
produced itself).

## What happened

Built `sims/verdict-077-cascade-independence-quota/` under the standing
discipline: fixtures.json committed BEFORE the runner (card 72862aa →
fixtures 8d8781c → runner cb46ada → accepted run c712701), fully hermetic
(every constant verbatim from the PROPOSAL 064 block / idea doc; zero
repo/network reads at verdict time), three-arm + census: Arm A seedless
exact-Fraction forward absorbing-walk DP (decision-bearing), Arm B
independently-written backward recursion + Gaussian ruin solve + Pascal pmf
(exact-equal on every published number), the algorithm-free 2^12 path
census at N = 12, Arm R seeded reporting-only literal traces (seeds
20261563–565, aux 20261566 asserted never read; strictly above the V074
fleet high-water 20261562 — new high-water 20261566 reserved). 139
self-checks 0 failed, exit 0; byte-identical double run (sha256 in
REPORT.md); CPython 3.11 asserted.

**VERDICT 077 — REJECT (the pre-registered predicted verdict, confirmed on
all three conjuncts, exact).** G(100, 7/10) ≈ 8.651255 ≥ 6 (1.44×);
k* = 15 ≥ 5 (3×; runner-up 17 by ≈ 0.004925, disclosed, read by no
clause); e(15) ≈ 0.033227 ≤ e(0)/2 (2.34×). All three structure theorems
CONFIRMED as exact gates at every grid cell (QUOTA-NULL, PARITY +
finite-horizon strictness, KNIFE-EDGE with the 441/14500 reference hit
exactly); k* ODD at every one of the 12 cells. The transparency tax is
N-independent (crowd cap 49/58 ≈ 0.8448 at p = 7/10 vs majority-of-100
≈ 0.9999845) and individually rational (late free-rider 0.8448 > solo 0.7)
— the fix needs a mandate. Falsifiability behaved as registered: N = 25
lands G ≈ 0.7402, p = 9/10 lands ≈ 0.7859, p = 4/5 straddles at ≈ 3.7539.
Anomaly A1, first-class: the drafter's disclosed IR-wedge pair
"≈ 2.2 / ≈ 10.8" is a steady-state approximation (cap-valued free-rides);
the exact counterfactual sums are 1.6738 / 10.3251 — cancels in G exactly,
ruling-neutral; 16/18 other disclosed values reproduced digit-for-digit.

**Previous-session review** (previous session = the PROPOSAL 064 drafter,
idea-engine PR #427): the drafter applied the V075/V074 card lineage
(registration-time arithmetic pass + tolerance audit) to full effect — a
fully deterministic gate set with joint pass probability 1 as computed at
registration, and that is exactly what this session experienced: the first
complete run of the registered pipeline exited 0 with the ruling stable at
disclosed margins. The one seam: the disclosed-landing channel mixed EXACT
prototype values (reproduced digit-for-digit) with unlabeled steady-state
APPROXIMATIONS (the IR-wedge pair, caught here as anomaly A1) — disclosed
landings should tag each number exact-vs-approximate so the verdict session
knows which mismatches are findings and which are the drafter rounding on
purpose.

💡 **Session idea (genuine, this session):** in a fully-deterministic sim,
the seeded reporting arm should be promoted from "statistically close,
never gated" to an EXACT per-episode representation-equivalence check: run
the literal rule-derived process AND the abstracted shortcut process (here:
LR-table agent vs absorbing-walk) on the SAME draws and assert
action-sequence identity on every episode — a structural gate with pass
probability 1 for a correct implementation that costs zero extra draws.
Implemented here as convention C3 (green on all 240,000 episodes × 2 quota
cells): it turns the MC arm's real value — checking that the ABSTRACTION,
not just its moments, matches the model narrative — into arithmetic,
closing the gap the V074 tolerance audit named from the other side
(tolerance clauses exist only because trace and law are compared
statistically; comparing REPRESENTATIONS episode-wise needs no tolerance
at all). Concretely for the kit: add "if the decision arm is exact, pair
every seeded reporting leg with a per-episode twin-representation identity
assertion" to the sim README template's registration checklist.

📊 Model: Claude Fable family (self-reported by this session's harness;
family-level name only per the standing attribution doctrine).
