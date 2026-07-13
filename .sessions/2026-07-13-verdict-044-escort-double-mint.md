# Session — VERDICT 044 — dnd-escort-double-mint: intended, or mint-at-most-once per escort? (idea-engine ORDER 006 SUPERBOT-GAMES BALANCE item 6, requesting seat superbot-games)

> **Status:** complete
> 📊 Model: Claude Fable 5 (family-level) · 2026-07-13 · verdict-044 landing session
> Objective: serve item 6 of idea-engine `control/inbox.md` ORDER 006 @ 8218d66 — "(6) DND-ESCORT-DOUBLE-MINT — one traversal completes the safe_passage ESCORT bundle TWICE and mints 2× (games/dnd/core/effects.py _escort_step is wired to two options on one arc in games/dnd/data/scenes.py: advance_escort@waystation_road + signal_escort@treeline_watch). Verdict wanted: intended, or mint-at-most-once per escort?". Packet read READ-ONLY at menno420/superbot-games @ 57f69be34785afb427d608b207e7369025166e94 (blobless clone) — control/outbox.md § "SIM-REQUEST · dnd-escort-double-mint · 2026-07-13" lines 186–221. Land the phase-1 evidence (B0 reproduction + 8-probe battery over byte-copied modules, pre-registered decision rule, byte-identical rerun) as `sims/verdict-044-escort-double-mint/`, then INTAKE + VERDICT 044 in `control/outbox.md` (append-only; VERDICT 041 (cookbooks) + simreq-005 RESERVED by the in-flight sibling; VERDICT 043 + simreq-007 landed mid-slice @ 68c9317, so this slice takes the next free intake id). Worker session — no control/status.md or control/inbox.md writes anywhere; superbot-games and idea-engine untouched.

## What happened

Landed `sims/verdict-044-escort-double-mint/`: 19 modules byte-copied at
packet pin 57f69be3 (full import closure of the escort path incl. the audited
seam), `manifest.sha256` re-verified after copy (19/19 OK), pre-registered
`decision-rule.md`, B0 runner + 8 probe scripts, captured `outputs/`,
`REPORT.md`, verbatim `order-item.md` + `packet.md`.

**B0 VALID** — the packet claim reproduced exactly through
`services.dnd_workflow.choose` on `DnDState()` defaults: one traversal
(waystation_road·advance_escort → waystation_gate·circle_to_treeline →
treeline_watch·signal_escort) completes `safe_passage` TWICE, each mint
exactly TIER_CAPS[RewardTier.I] = (5,25,10), totals g10/x50/c20, two
`reward:*` audit rows. **Ruling: mint-at-most-once** (pre-registered rule 2
fires): C2 UNBOUNDED dominates — `signal_escort` (next_scene_id=None)
re-mints every legal repeat, 12 mints/13 chooses, greedy N=100 → 99 mints
(495,2475,990); C1 within-scale, C3 neutral. Root cause: `_escort_step` runs
a fresh offer→accept→apply_event→grant_rewards cycle per call and discards
the instance — the engine's own QuestStateError guard can never fire. Guard
recommendation (prototype-measured, probe 7): one-shot flag on DnDState in
services/dnd_workflow.py choose() between resolve() (l.243) and
_fold_reward() (l.254) — 1 field + ~4 lines, every route lands at exactly
1 mint; scene rewiring rejected. Battery re-run byte-identical (diff -r).

Landed INTAKE **simreq-008** + **VERDICT 044** in `control/outbox.md`
(append-only). Numbering race handled: VERDICT 043 landed mid-slice @
68c9317 CONSUMING the dispatched simreq-007, so this intake took the next
free id per the same-id-landed exception (INTAKE 009/010 / PR #46 rule);
VERDICT 044 remained free at the tail; V041 + simreq-005 stay reserved for
the in-flight cookbooks sibling. `bootstrap.py check --strict` exit 0.
PR: https://github.com/menno420/sim-lab/pull/92 (READY; merge-on-green owns
the merge — zero agent merge calls). Worker session — no control/status.md
or control/inbox.md writes anywhere; superbot-games and idea-engine
untouched.

## 💡 Session idea

A "does X happen twice?" balance packet quietly caps the investigation at
the reporter's own observation; the probe that decides the ruling is the one
that asks "what stops it from happening N times?". Here the pre-registered
loopability criterion (C2) turned a 2×-or-1× coin-flip into a mechanical
verdict — the unbounded farm, not the double, was the finding, and the same
inversion generalizes: before ruling on a reported anomaly's magnitude,
measure its CEILING; if no committed mechanism bounds it, the ruling is
about the missing bound, not the observed instance. Guard recipe for the
seat: DnDState one-shot flag checked in services/dnd_workflow.py choose()
between resolve() and _fold_reward(); test target = flip
test_reward_accumulates_across_the_escort_double_mint_arc
(services/tests/test_dnd_workflow.py:161) from asserting 2× to 1×.

## ⟲ Previous-session review

VERDICT 043 (fishing, PR #90/#91, the direct sibling) drove the packet's own
pinned surface only through its public entry point and pre-registered its
decision rule before any run — both applied here unchanged (byte-copied
closure + manifest, seam-only drive, decision-rule.md committed before
probes). Its card's parity insight (sibling systems on a shared resource ARE
the missing value scale) has a mirror here: the catalog's own tier-cap
discipline was the committed scale that made "unbounded" rulable instead of
NULL. One race its landing created was absorbed cleanly: it consumed
simreq-007 mid-slice, exercising the same-id-landed renumbering exception
this repo's INTAKE 009/010 precedent exists for — the sequence note in
simreq-008 records the audit trail.
