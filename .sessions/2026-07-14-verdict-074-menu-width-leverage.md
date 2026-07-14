# Session — VERDICT 074 — superbot-games D&D menu-width leverage inversion: does message-XP widen the menu into FEWER rewards, and can a data-only reorder fix it? (idea-engine PROPOSAL 063, the reserved +11-offset slot, ORDER 008 item (3))

> **Status:** complete
> 📊 Model: Claude Fable family · 2026-07-14 · verdict-074 slice-worker session

Objective: produce VERDICT 074 for idea-engine PROPOSAL 063 (menu-width
leverage inversion, `ideas/superbot-games/menu-width-leverage-inversion-2026-07-14.md`,
read at idea-engine main `6d6735f`, landed via idea-engine PR #419) — the
slot RESERVED by the simreq-010/011 batch per the constant +11 offset map,
dispatched by sim-lab inbox ORDER 008 item (3). One slice, one branch
(`claude/verdict-074-menu-width-leverage`, PR #140), one verdict. Worker
session; `control/status.md`, both inboxes, and superbot-games files
untouched (ledger appended to sim-lab `control/outbox.md` only — INTAKE 063
+ VERDICT 074; delivery is the manager's Q-0264 fan-in). This card held the
substrate gate red deliberately until this flip (the born-red discipline —
the designed hold was the only red this branch produced itself).

## What happened

Subject pins re-verified FIRSTHAND before anything else (Q-0120): the
proposal's pinned superbot-games commit `e3930f13…` fetched into the session
clone; resolver prefix slice, width law, scene tuples, escort mint path,
TIER_CAPS/GLOBAL_MAX, `_FULL_MENU_XP` all traced to their defining lines.
One firsthand finding: the literal shipped `waystation_gate` tuple is
(enter_common_room, circle_to_treeline, rest_at_gate) — (N, M, Z) under the
proposal's role map, not (M, N, Z). Handled as the idea file's own §4(b)
clause anticipates: disclosed in fixtures, asserted as gate F1b
(prefix-SET-identical to MNZ at every width, so the SHIPPED cell is the MNZ
cell for every set-based behaviour) — an assertion, never an assumption.

Built `sims/verdict-074-menu-width-leverage/` under the standing discipline:
fixtures.json committed BEFORE the runner (card 6709901 → fixtures 5ce907d →
runner + accepted run 0c583e3), exact-Fraction forward recursion as the
decision arm + seeded MC twin (20,000 episodes/cell, 4 legs), gates
F1/F1b/F2/F3/F4 all green, byte-identical double run (sha256 pinned in
REPORT.md), CPython 3.11 asserted, seeds 20261559–62 re-registered
contiguously above the V075/V076 high-water 20261558 (the proposal's
drafting seeds were overtaken by that registration — disclosed pre-runner)
— NEW HIGH-WATER 20261562.

**VERDICT 074 — REJECT-REORDER (the pre-registered prediction, confirmed).**
The inversion is real and exact: SHIPPED × B1 long-run mint rate falls
1/2 → 1/3 at the first 500 message-XP (E[mints,T=20] = 9961473/1048576
≈ 9.500 → 21502885715/3486784401 ≈ 6.167, −35.1%). The impossibility is
CERTIFIED, not sampled: across all 6 orderings the width-2 B1 long-run rate
partitions as exactly {0, 1/2} (rate = [M ∈ prefix(2)]/2), so MONOTONE and
POSITIVE-FLOOR are jointly unsatisfiable by ANY data-only reorder. Width
never gates the farmer (19 mints / 190 currency at every width), and the
§4.1 "always ON the menu" clamp promise is FALSE at width 2 for MNZ/NMZ.
Recommendation escalates to the named mechanic change (width must stop
selecting by prefix — per-option `min_width` or width-indexed option sets),
with NZM/ZNM priced as the interim zero-floor menu. Anomaly A1 disclosed,
never smoothed: 59 of 1596 self-checks fail on near-one ONCE cells where
p̂ = 1.0 degenerates the registered sample-σ clause (≤ 1.29σ under the true
binomial σ — agreement); exit 1 carried honestly per the V075 precedent;
decision path exact-arm only, every PER-APP twin check green.

**Previous-session review** (newest prior card,
`.sessions/2026-07-14-verdict-075-076-fishing-roster-cook.md`): its
session idea — a registration-time arithmetic pass that derives each band's
feasible window on paper before any runner exists — was applied here and
paid off twice: the F2 closed forms were re-derived independently before the
fixtures landed, and the {0, 1/2} partition argument meant the REJECT was
expected to be theorem-grade rather than knife-edge; what that idea did NOT
catch (and this session's does) is tolerance-clause degeneracy, the same
class of self-inflicted red their anomaly A1 lived in.

💡 **Session idea (genuine, this session):** pre-registered MC tolerance
clauses should be stress-tested against the EXACT arm's own predicted
distributions before the runner runs — a one-loop "tolerance audit" that
walks every registered check over the exact-arm values and asks "what is
the probability this check fires on a CORRECT implementation?" Here the C7
zero-variance clause fires with probability ≈ 0.98 on every near-one ONCE
cell (P(p̂=1) = (1−ε)^20000 ≈ 1 for ε ≤ 1e-6) — a guaranteed-red instrument
that was knowable from the exact arm alone, before a single episode ran.
Concretely for the kit: add "audit each registered tolerance against the
exact arm: any check with fire-probability > 1e-6 under a correct
implementation is a mis-specified instrument — re-register the clause, not
the result" to the sim README template's registration checklist, beside
V075/076's feasible-window line. It turns the guaranteed-artifact class of
anomaly into a pre-run fixture edit.

📊 Model: Claude Fable family (self-reported by this session's harness;
family-level name only per the standing attribution doctrine).
