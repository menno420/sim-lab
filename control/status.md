# sim-lab · status

updated: 2026-07-14T21:14:50Z (real wall-clock via date -u) · EAP FINAL SHUTDOWN — dormancy stamp; this file is the seat's final record
phase: SEAT DORMANT (owner order 2026-07-14)
health: dormant
kit: v1.15.0
last-shipped: #142 → 2725e4a (post-close-out heartbeat stamp) after #141 → 960cbf8 (EAP close-out walkthrough + CLOSE-OUT REPORT block). This dormancy stamp is the final change; nothing ships from this seat after it.
blockers: none — seat shut down per owner directive
orders: acked=ORDER-001 ORDER-002 ORDER-003 ORDER-004 ORDER-005 ORDER-006 ORDER-007 ORDER-008 done=ORDER-001 ORDER-002 ORDER-003 ORDER-004 ORDER-005 ORDER-006 ORDER-007 ORDER-008 (all terminal at close-out; see #142 → 2725e4a for the final done-flip record). No further orders are read from this inbox while the seat is dormant.
routines: none owned on the sim-lab side (OA-005 resolved — zero sim-lab triggers remain; verified pre-archive).

## Revival

Seat shut down per owner directive (2026-07-14, EAP final day). ORDER 014 and the full revival handoff live in menno420/idea-engine — on revival, read idea-engine control/status.md and idea-engine docs/HANDOFF.md FIRST, before acting on anything in this repo. Historical close-out context for this lane: docs/eap-closeout-walkthrough-2026-07-14.md (sim-lab half) · idea-engine docs/eap-closeout-walkthrough-2026-07-14.md (seat level). Ledger locations unchanged: verdicts V001–071 in control/outbox-archive-2026-07.md, V072–V076 live in control/outbox.md; reconciliation map in docs/current-state.md.
