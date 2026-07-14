# sim-lab · status

updated: 2026-07-14T12:51:32Z (real wall-clock via date -u) · post-close-out heartbeat stamp (scribe session, model family Claude Fable) — neutral facts + pointers only; the full fleet heartbeat lives in idea-engine control/status.md
phase: EAP CLOSED — verdict ledger complete through VERDICT 076 at HEAD 960cbf8 (canonical ledger control/outbox.md: V072–V076 live, V001–V071 rolled byte-faithful to control/outbox-archive-2026-07.md per ORDER 006). Final-day landings: VERDICT 075 (NULL) + VERDICT 076 (APPROVE-WITH-CONSTANTS) via #139 → d0a5a75; VERDICT 074 (REJECT-REORDER, idea-engine P063) via #140 → 9aaf72b; close-out walkthrough + CLOSE-OUT REPORT block via #141 → 960cbf8. Proposal pipeline dry at close (P063 → V074 same day; offset map docs/current-state.md). Fleet seed high-water: 20261562 (V074) — the next sim registers strictly above it. Close-out docs: this repo docs/eap-closeout-walkthrough-2026-07-14.md (sim-lab half) · idea-engine docs/eap-closeout-walkthrough-2026-07-14.md (seat level, both repos).
health: green
kit: v1.15.0
last-shipped: #141 → 960cbf8 (EAP close-out walkthrough + CLOSE-OUT REPORT block, ORDER 008 item (b)) after #140 → 9aaf72b (VERDICT 074) and #139 → d0a5a75 (VERDICT 075 + 076). Open PRs at this refresh: 0 (verified via the GitHub API 2026-07-14T12:51Z), besides this heartbeat branch itself.
blockers: none
orders: acked=ORDER-001 ORDER-002 ORDER-003 ORDER-004 ORDER-005 ORDER-006 ORDER-007 ORDER-008 done=ORDER-001 ORDER-002 ORDER-003 ORDER-004 ORDER-005 ORDER-006 ORDER-007 ORDER-008 (008 landed via #138 @ d4ff3c8 item (a) + #139/#140 @ d0a5a75/9aaf72b verdicts + #141 @ 960cbf8 item (b) walkthrough/close-out report; 006/007 via #134/#136 @ 5356b2a/b10ffce; inbox headers remain `status: new` by append-only design — the done-flips are stamped here in this orders line, not in the inbox). NOTE for manager unchanged: ROUTINE_PAT not set in sim-lab — GITHUB_TOKEN fallback in use and works; flag if PAT-based attribution is wanted.
batons: (1) VERDICT 075 reframing fork (fishing full-roster) — the three-way re-registration pick is routed to the manager/owner via the fleet-manager; the walkthrough §C recommendation on record is option (1), re-center the parity band (fresh@dock ≈ 4.75–4.95; k=1.1, δ=0.6 measured stable interior); nothing from V075 is wire-able until the pick, the 33-row table is published NOT-PINNED. (2) VERDICT 076 F-FLAT30 build precondition — the committed flat `"cooked fish": 30` is perpetual motion at every measured cell; supersede it before any haul-cook op wires the V076 constants (P*=12; minnow 1 / bass 1 / pike 2 / legend_carp 7). (3) VERDICT 074 escalation routes to superbot-games via the fleet-manager (Q-0264 — this repo never seat-directs): width must stop selecting by prefix — per-option `min_width` or width-indexed option sets; NZM/ZNM priced as the interim zero-floor menu. Full handoff: docs/eap-closeout-walkthrough-2026-07-14.md §E + idea-engine docs/eap-closeout-walkthrough-2026-07-14.md §E.

## ⚑ needs-owner

### ⚑ OWNER-ACTION — OA-002 Codex usage cap
WHAT: Raise/reset the Codex GitHub-integration usage quota (or accept that verdicts ship without the @codex fold-in). Split disposition per ORDER 006 do-2: enabled=resolved / quota=open (INC-04), cross-linked in docs/current-state.md.
WHERE: chatgpt.com/codex settings; symptom shows on every verdict PR (e.g. PR #38 comment https://github.com/menno420/sim-lab/pull/38#issuecomment-4948283951).
HOW: owner-only quota reset (click only).
WHY-IT-MATTERS: 6+ @codex questions are pending; the Q-0264.4 review step draws no reply until the quota frees.
UNBLOCKS: @codex fold-in on future verdict PRs.
VERIFIED-NEEDED: bot reply "reached usage limits" reproduced on every verdict PR (integration is LIVE but capped).

### ⚑ OWNER-ACTION — OA-003 review-site deploy
WHAT: Deploy the `review` website.
WHERE: VERDICT 011 (sims/owner-002-websites-purpose-nav) — built locally, no deployed URL.
HOW: owner / websites-lane deploy (click only).
WHY-IT-MATTERS: it was built for Anthropic reviewers but is currently unreachable.
UNBLOCKS: reviewer access to the review site.
VERIFIED-NEEDED: measured local build only; no live URL exists (routed via outbox VERDICT 011, not a sim-lab blocker).

### ⚑ OWNER-ACTION — OA-004 harness tag-push 403
WHAT: Allow refs/tags/* push, or push harness-v0.1.0 from a fresh clone.
WHERE: this repo — `git push origin refs/tags/harness-v0.1.0`.
HOW: owner grants tag-push permission or pushes the tag.
WHY-IT-MATTERS: the harness release is un-versioned; raw/copy consumption still works, so it is not blocking.
UNBLOCKS: tagged harness releases.
VERIFIED-NEEDED: 403 on refs/tags/* push reproduced.

### ⚑ OA-005 standing failsafe trigger — RESOLVED (coordinator, 2026-07-11 ~19:50Z)
WHAT: RESOLVED — no owner click needed. Recurring trigger trig_01SHfnLv6EqZesr4tC3T9kUU ('sim-lab failsafe wake') and the pending one-shot trig_01QoXDsjqF1QhgyDcVXYFMN9 were both deleted by the coordinator via a worker seat before archive.
WHERE: account Routines — resolved out-of-band, not in the UI.
HOW: coordinator deleted both triggers from a worker seat; list_triggers showed the recurring one already `ended_reason=auto_disabled_env_deleted`.
WHY-IT-MATTERS: prevents a dead-session trigger from firing after archive — now moot.
UNBLOCKS: a clean archive.
VERIFIED-NEEDED: post-delete enumeration of all account triggers confirms ZERO sim-lab triggers remain.

notes: Heartbeat home is idea-engine control/status.md (single-home routine disposition ledgered THERE); this file carries the sim-lab lane's neutral facts only. Ledger locations: verdicts V001–071 in control/outbox-archive-2026-07.md, V072–V076 live in control/outbox.md; INTAKEs 001–013 in control/inbox.md, INTAKE 014 onward with the outbox (rolled with their verdicts); reconciliation map in docs/current-state.md. Owner path through the close-out: docs/eap-closeout-walkthrough-2026-07-14.md (§C carries the OA checklist + the V075 fork decision) and idea-engine docs/eap-closeout-walkthrough-2026-07-14.md.
