# sim-lab · status

updated: 2026-07-16T06:17:38Z (real wall-clock via date -u) · Ideas Lab worker session session_01VddygwKfjhUsh9pNs3HNHy (V093 slice; this refresh rides the V093 PR #164)
phase: ACTIVE — EAP extended through 2026-07-21 (ORDER 009, acked in the 2026-07-15 stamp); verdict pipeline live.
health: green on main — `python3 bootstrap.py check --strict` exit 0 at the V092 merge basis 418de3e; on the V093 branch the ONLY red is the designed born-red card hold (flips at slice end, the standing discipline).
kit: v1.15.0
last-shipped: #163 → 418de3e (VERDICT 092, P079, reject) · in flight this stamp: #164 (VERDICT 093, P080 cycle-following-coupling-lever — REJECT, 61/61 self-checks, byte-identical double run; lands via merge-on-green).
blockers: none.
orders: acked=ORDER-001…ORDER-009 done=ORDER-001…ORDER-008 (terminal at close-out, see #142 → 2725e4a) · ORDER-009 (EAP extension) is the standing frame — no open sim-lab ORDERs at this stamp.
routines: none owned on the sim-lab side (the coordinator failsafe is fleet-side; its id is recorded in idea-engine control/status.md).
notes: verdict ledger through **V093** (P080, offset +13 — seventeenth row; map in docs/current-state.md § Verdict-numbering map). Next expected: **PROPOSAL 081 → VERDICT 094** (P081 not yet drafted at this stamp). Live outbox measured 481,859 B post-V093-append — above the fleet 200KB rollover threshold; rolling stays PARKED with the manager (inbox ORDER 005 item 5, the V086–V093 precedent). Ledger locations: V001–071 in control/outbox-archive-2026-07.md, V072+ live in control/outbox.md; INTAKE 014+ ride the outbox (inbox is the manager-order file, untouched by verdict slices).

## Revival

On any future revival, read idea-engine control/status.md and idea-engine docs/HANDOFF.md FIRST, before acting on anything in this repo. Historical close-out context for this lane: docs/eap-closeout-walkthrough-2026-07-14.md (sim-lab half) · idea-engine docs/eap-closeout-walkthrough-2026-07-14.md (seat level).
