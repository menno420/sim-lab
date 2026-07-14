# sim-lab · status

updated: 2026-07-14T09:31:32Z (real wall-clock via date -u) · minimal heartbeat refresh (scribe session, model family Claude Fable) — neutral facts + pointers only; the full fleet heartbeat lives in idea-engine control/status.md
phase: EAP close-out — verdict ledger runs through VERDICT 073 @ 2ceeb59 (canonical ledger control/outbox.md; VERDICT 001–071 rolled byte-faithful to control/outbox-archive-2026-07.md per ORDER 006, V072 + V073 live post-roll). Prior full session prose stands in this file's git history (last full ledger @ b155cd1) and idea-engine docs/retro/.
health: green
kit: v1.15.0 · check: green · engaged: yes
last-shipped: #135 → 2ceeb59 (VERDICT 073: P062 owner-queue attention-order simulation) after #136 → b10ffce (ORDER 006 do-2 + ORDER 007 closeout) and #134 → 5356b2a (ORDER 006 do-1 outbox rollover). Open PRs at this refresh: 0 (verified via the GitHub API 2026-07-14T09:31Z), besides this heartbeat branch itself.
blockers: none
orders: acked=ORDER-001 ORDER-002 ORDER-003 ORDER-004 ORDER-005 ORDER-006 ORDER-007 done=ORDER-001 ORDER-002 ORDER-003 ORDER-004 ORDER-005 ORDER-006 ORDER-007 (006/007 landed via PR #134/#136 @ 5356b2a/b10ffce; inbox headers remain `status: new` by append-only design — the done-flips are stamped here in this orders line, not in the inbox). ORDER 006 do-1 outbox rollover: control/outbox.md rolled 1,091,133 B → 41,974 B (128 terminal blocks to control/outbox-archive-2026-07.md, one-line pointer stubs, content-stable numbering); measured 62,963 B at HEAD 2ceeb59 after the subsequent V072/V073 appends. NOTE for manager unchanged: ROUTINE_PAT not set in sim-lab — GITHUB_TOKEN fallback in use and works; flag if PAT-based attribution is wanted.

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

notes: Heartbeat home is idea-engine control/status.md (single-home routine disposition ledgered THERE); this file carries the sim-lab lane's neutral facts only. Ledger locations: verdicts V001–071 in control/outbox-archive-2026-07.md, V072+ live in control/outbox.md; INTAKEs 001–013 in control/inbox.md, INTAKE 014 onward with the outbox (rolled with their verdicts); reconciliation map in docs/current-state.md.
