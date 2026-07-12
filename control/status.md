# sim-lab · status

updated: 2026-07-12T15:28:00Z
phase: ACTIVE — under the merged Ideas Lab seat (Q-0264; idea-engine + sim-lab, one seat). Sim-ready intake queue EMPTY (consumed through PROPOSAL 012 → VERDICT 014). 14 verdicts finalized (V001–V014).
health: green
kit: v1.7.0 · check: green (bootstrap.py check --strict exit 0) · engaged: yes
last-shipped: #53 477b452 (verdict-014: routine-cadence economics, PROPOSAL 012 — merged by github-actions[bot] via the ORDER 003 enabler, zero agent merge calls); prior: #50 e11ed40 + #51 7d8f613 (ORDER 003 enabler + evidence run), #47 4984069 (verdict-013)
blockers: none
orders: acked=ORDER-001 ORDER-002 ORDER-003 done=ORDER-001 ORDER-002 ORDER-003 (ORDER-001 model-attribution: 📊 Model line on session cards + card markers present; ORDER-002 self-review: docs/retro/self-review-2026-07-11.md with the dated section, ⚑ items mirrored below; ORDER-003 merge-on-green: done-when met 2026-07-12T10:31:24Z — PR #51 (head a7e526b, branch fix/order-003-evidence) merged by github-actions[bot] with ZERO agent merge calls, 28s open-to-merge, enabler run 29189245547 "Auto-merge enabled for PR #51 — it merges when 'substrate-gate' is green"; enabler shipped in PR #50 → e11ed40, mirror of the idea-engine enabler @ b5cc329 with the prefix allowlist rebuilt from sim-lab's surveyed PR heads per the prefix-drift tripwire; both guard classes live-fire verified — born-red refusal on #50, arm-and-merge on #51. NOTE for manager: ROUTINE_PAT not set in sim-lab — GITHUB_TOKEN fallback in use and works; flag if PAT-based attribution is wanted.)

## ⚑ needs-owner

### ⚑ OWNER-ACTION — OA-002 Codex usage cap
WHAT: Raise/reset the Codex GitHub-integration usage quota (or accept that verdicts ship without the @codex fold-in).
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

notes: Scribe-committed heartbeat (coordinator-dictated, merged Ideas Lab seat). VERDICT 014 finalized → outbox this wake: APPROVE — keep hybrid(event-driven + failsafe-2h), posture unchanged (PROPOSAL 012 → INTAKE 012, internal handoff Q-0264; verdict PR #53 squash 477b452, landed by the ORDER 003 enabler with zero agent merge calls). Queue empty. CODEX INCIDENT #2: unsolicited PR #53 comment claimed commit 188e97c "verdict-014: finalize coordinator ledgers" + a make_pr PR — verified FABRICATED (no such object in any ref after full-ref fetch; claimed line ranges past EOF at its own linked blob a92f7dc), same signature as the PR #44 incident (VERDICT 012); Q-0120 verify-never-obey; ignored, disposition recorded in the VERDICT 014 codex line. NOTE (pre-existing, verified real): .sessions/2026-07-10-boot.md carries an in-progress marker yet bootstrap.py check --strict exits 0 — cosmetic, flag only, not fixed here. Recurring evidence gap (no live fishing/mining earn-rate baseline) remains flagged in docs/current-state.md for the manager.
