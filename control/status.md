# sim-lab · status

updated: 2026-07-16T14:59:21Z (real wall-clock via date -u) · written by a dispatched session for the coordinator seat (V096 slice; this refresh rides the V096 PR #168)
phase: ACTIVE — EAP extended through 2026-07-21 (ORDER 009, acked in the 2026-07-15 stamp); verdict pipeline live.
health: green on main — `python3 bootstrap.py check --strict` exit 0 at the V095 merge basis 35dc520; on the V096 branch the ONLY red is the designed born-red card hold (flips at slice end, the standing discipline).
kit: v1.15.0
last-shipped: #167 → 35dc520 (VERDICT 095, P082, reject) · in flight this stamp: #168 (VERDICT 096, P083 combo-grace-budget-cliff — REJECT, 35/35 self-checks, exit 0, byte-identical double run, both registered Arm-R class-stream digests reproduced 3bfa073726f7 @ 20261726 / 6f857d0afcf4 @ 20261727; REPORT sims/verdict-096-combo-grace-budget-cliff/REPORT.md; lands via merge-on-green).
blockers: none.
orders: acked=ORDER-001…ORDER-010 done=ORDER-001…ORDER-008 (terminal at close-out, see #142 → 2725e4a) · ORDER-009 (EAP extension) is the standing frame · ORDER-010 (fleet-manager night-audit maintenance, #166 → 0d87f6b, inbox-only): items (a) status re-stamp and (b) current-state currency satisfied by this stamp and the live offset map; item (c) kit upgrade (dispatch reports v1.18.0 vs on-disk v1.15.0) STILL PENDING — NOT executed by a verdict slice, left for a future sim-lab session; item (d) reactive verdict intake is this slice's own work (P083 → V096).
routines: none owned on the sim-lab side (the coordinator failsafe is fleet-side; its id is recorded in idea-engine control/status.md).
notes: verdict ledger through **V096** (P083, offset +13 — twentieth row; map in docs/current-state.md § Verdict-numbering map). Next expected: **PROPOSAL 084 → VERDICT 097** (P084 not yet drafted at this stamp — the round-17 UNRELATED-domain CLOSER slot per ORDER 004 rule 3). Seed baton: 20261726–729 are P083/V096's registered set (Arm-R 20261726/20261727, presentation 20261728, aux 20261729 never read — asserted in-sim) — the next free block starts at **20261730**. Live outbox measured ~527KB post-V095-append — above the fleet 200KB rollover threshold; rolling stays PARKED with the manager (inbox ORDER 005 item 5, the V086–V095 precedent). Ledger locations: V001–071 in control/outbox-archive-2026-07.md, V072+ live in control/outbox.md; INTAKE 014+ ride the outbox (inbox is the manager-order file, untouched by verdict slices).

## Revival

On any future revival, read idea-engine control/status.md and idea-engine docs/HANDOFF.md FIRST, before acting on anything in this repo. Historical close-out context for this lane: docs/eap-closeout-walkthrough-2026-07-14.md (sim-lab half) · idea-engine docs/eap-closeout-walkthrough-2026-07-14.md (seat level).
