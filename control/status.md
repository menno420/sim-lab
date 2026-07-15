# sim-lab · status

updated: 2026-07-15T04:06:11Z (real wall-clock via date -u) · Ideas Lab coordinator session_015yw6rJdcbH2txW9r8z9TAX
phase: ACTIVE — EAP extended through 2026-07-21 (ORDER 009 acked 2026-07-15T04:06:11Z); SEAT DORMANT (2026-07-14 dormancy stamp) superseded.
health: green — `python3 bootstrap.py check --strict` exit 0 at boot, HEAD 5ea6a43
kit: v1.15.0
last-shipped: #144 → 5ea6a43 (EAP-extension note, ORDER 009 on the bus); this stamp is the extension-reactivation ack.
blockers: none.
orders: acked=ORDER-001 ORDER-002 ORDER-003 ORDER-004 ORDER-005 ORDER-006 ORDER-007 ORDER-008 ORDER-009 done=ORDER-001 ORDER-002 ORDER-003 ORDER-004 ORDER-005 ORDER-006 ORDER-007 ORDER-008 (001–008 terminal at close-out, see #142 → 2725e4a) · ORDER-009 acked 2026-07-15T04:06:11Z.
routines: none owned on the sim-lab side (the coordinator failsafe is fleet-side; its id is recorded in idea-engine control/status.md).
notes: verdict work resumes on the next PROPOSAL from idea-engine (P064 expected, offset +11).

## Revival

Superseded by ORDER 009 (EAP extension through 2026-07-21) — the seat is active again; kept for the ledger pointers. On any future revival, read idea-engine control/status.md and idea-engine docs/HANDOFF.md FIRST, before acting on anything in this repo. Historical close-out context for this lane: docs/eap-closeout-walkthrough-2026-07-14.md (sim-lab half) · idea-engine docs/eap-closeout-walkthrough-2026-07-14.md (seat level). Ledger locations unchanged: verdicts V001–071 in control/outbox-archive-2026-07.md, V072–V076 live in control/outbox.md; reconciliation map in docs/current-state.md.
