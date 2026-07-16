# sim-lab · status

updated: 2026-07-16T09:37:36Z (real wall-clock via date -u) · Ideas Lab worker session (V095 slice; this refresh rides the V095 PR #167)
phase: ACTIVE — EAP extended through 2026-07-21 (ORDER 009, acked in the 2026-07-15 stamp); verdict pipeline live.
health: green on main — `python3 bootstrap.py check --strict` exit 0 at the V094 merge basis 5cf86de and re-verified on the V095 branch at the 0d87f6b rebase; on the V095 branch the ONLY red is the designed born-red card hold (flips at slice end, the standing discipline).
kit: v1.15.0
last-shipped: #165 → 5cf86de (VERDICT 094, P081, reject) · in flight this stamp: #167 (VERDICT 095, P082 owner-gate-recognition-cliff — REJECT, 43/43 self-checks, byte-identical double run, both registered Arm-R class-stream digests reproduced; REPORT sims/verdict-095-owner-gate-recognition-cliff/REPORT.md; lands via merge-on-green).
blockers: none.
orders: acked=ORDER-001…ORDER-009 done=ORDER-001…ORDER-008 (terminal at close-out, see #142 → 2725e4a) · ORDER-009 (EAP extension) is the standing frame · ORDER-010 (fleet-manager night-audit maintenance, arrived mid-V095-slice via #166 → 0d87f6b, inbox-only): items (a) status re-stamp and (b) current-state currency are satisfied by this stamp and the live offset map; item (c) kit upgrade (dispatch reports v1.18.0 vs on-disk v1.15.0) NOT executed by the V095 verdict slice — with the next sim-lab session; item (d) reactive verdict intake is this slice's own work (P082 → V095).
routines: none owned on the sim-lab side (the coordinator failsafe is fleet-side; its id is recorded in idea-engine control/status.md).
notes: verdict ledger through **V095** (P082, offset +13 — nineteenth row; map in docs/current-state.md § Verdict-numbering map). Next expected: **PROPOSAL 083 → VERDICT 096** (P083 not yet drafted at this stamp). Seed baton: 20261722–725 are P082/V095's registered set (Arm-R 20261722/20261723, presentation 20261724, aux 20261725 never read — asserted in-sim) — the next free block starts at **20261726**. Live outbox measured 527,014 B post-V095-append — above the fleet 200KB rollover threshold; rolling stays PARKED with the manager (inbox ORDER 005 item 5, the V086–V095 precedent). Ledger locations: V001–071 in control/outbox-archive-2026-07.md, V072+ live in control/outbox.md; INTAKE 014+ ride the outbox (inbox is the manager-order file, untouched by verdict slices).

## Revival

On any future revival, read idea-engine control/status.md and idea-engine docs/HANDOFF.md FIRST, before acting on anything in this repo. Historical close-out context for this lane: docs/eap-closeout-walkthrough-2026-07-14.md (sim-lab half) · idea-engine docs/eap-closeout-walkthrough-2026-07-14.md (seat level).
