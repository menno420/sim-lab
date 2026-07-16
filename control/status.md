# sim-lab · status

updated: 2026-07-16T02:15:58Z (real wall-clock via date -u) · Ideas Lab worker session session_01NJn3xbf3JSM3mh82p6YEBe (V092 slice; this refresh rides the V092 PR #163 — the prior stamp had gone stale at 5ea6a43/offset-+11/P064-expected)
phase: ACTIVE — EAP extended through 2026-07-21 (ORDER 009, acked in the 2026-07-15 stamp); verdict pipeline live.
health: green on main — `python3 bootstrap.py check --strict` exit 0 at the V091 merge basis 7ec0d64; on the V092 branch the ONLY red is the designed born-red card hold (flips at slice end, the standing discipline).
kit: v1.15.0
last-shipped: #162 → 7ec0d64 (VERDICT 091, P078, reject) · in flight this stamp: #163 (VERDICT 092, P079 owned-track-launch-flag-dial — REJECT, 61/61 self-checks, byte-identical double run; lands via merge-on-green).
blockers: none.
orders: acked=ORDER-001…ORDER-009 done=ORDER-001…ORDER-008 (terminal at close-out, see #142 → 2725e4a) · ORDER-009 (EAP extension) is the standing frame — no open sim-lab ORDERs at this stamp.
routines: none owned on the sim-lab side (the coordinator failsafe is fleet-side; its id is recorded in idea-engine control/status.md).
notes: verdict ledger through **V092** (P079, offset +13 — sixteenth row; map in docs/current-state.md § Verdict-numbering map). Next expected: **PROPOSAL 080 → VERDICT 093** (P080 not yet drafted at this stamp). Live outbox measured 461,840 B post-V092-append — above the fleet 200KB rollover threshold; rolling stays PARKED with the manager (inbox ORDER 005 item 5, the V086–V092 precedent). Ledger locations: V001–071 in control/outbox-archive-2026-07.md, V072+ live in control/outbox.md; INTAKE 014+ ride the outbox (inbox is the manager-order file, untouched by verdict slices).

## Revival

On any future revival, read idea-engine control/status.md and idea-engine docs/HANDOFF.md FIRST, before acting on anything in this repo. Historical close-out context for this lane: docs/eap-closeout-walkthrough-2026-07-14.md (sim-lab half) · idea-engine docs/eap-closeout-walkthrough-2026-07-14.md (seat level).
