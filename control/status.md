# sim-lab · status

updated: 2026-07-16T07:56:41Z (real wall-clock via date -u) · Ideas Lab worker session session_014ZbpdUe74qrvzJ1LL9FkT6 (V094 slice; this refresh rides the V094 PR #165)
phase: ACTIVE — EAP extended through 2026-07-21 (ORDER 009, acked in the 2026-07-15 stamp); verdict pipeline live.
health: green on main — `python3 bootstrap.py check --strict` exit 0 at the V093 merge basis ce5d1a6; on the V094 branch the ONLY red is the designed born-red card hold (flips at slice end, the standing discipline).
kit: v1.15.0
last-shipped: #164 → ce5d1a6 (VERDICT 093, P080, reject) · in flight this stamp: #165 (VERDICT 094, P081 guard-fires-dedupe-regime-cliff — REJECT, 52/52 self-checks, byte-identical double run; lands via merge-on-green).
blockers: none.
orders: acked=ORDER-001…ORDER-009 done=ORDER-001…ORDER-008 (terminal at close-out, see #142 → 2725e4a) · ORDER-009 (EAP extension) is the standing frame — no open sim-lab ORDERs at this stamp.
routines: none owned on the sim-lab side (the coordinator failsafe is fleet-side; its id is recorded in idea-engine control/status.md).
notes: verdict ledger through **V094** (P081, offset +13 — eighteenth row; map in docs/current-state.md § Verdict-numbering map). Next expected: **PROPOSAL 082 → VERDICT 095** (P082 not yet drafted at this stamp). Seed baton: 20261718–721 are P081/V094's registered set (aux 20261721 never read) — the next free block starts at **20261722**. Live outbox measured 505,807 B post-V094-append — above the fleet 200KB rollover threshold; rolling stays PARKED with the manager (inbox ORDER 005 item 5, the V086–V094 precedent). Ledger locations: V001–071 in control/outbox-archive-2026-07.md, V072+ live in control/outbox.md; INTAKE 014+ ride the outbox (inbox is the manager-order file, untouched by verdict slices).

## Revival

On any future revival, read idea-engine control/status.md and idea-engine docs/HANDOFF.md FIRST, before acting on anything in this repo. Historical close-out context for this lane: docs/eap-closeout-walkthrough-2026-07-14.md (sim-lab half) · idea-engine docs/eap-closeout-walkthrough-2026-07-14.md (seat level).
