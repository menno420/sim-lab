# sim-lab · status

updated: 2026-07-12T23:32:28Z
phase: ACTIVE — under the merged Ideas Lab seat (Q-0264; idea-engine + sim-lab, one seat), coordinator session 2 (booted 2026-07-12 ~20:45Z; owner ORDER 003 standing in the idea-engine inbox: continuous idea pipeline). Sim-ready intake consumed through the PROPOSAL 015 assignment; PROPOSAL 015 (superbot-idle T10 cost curve, 2026-07-12T23:08:19Z) verdict session dispatched — VERDICT 017 expected. 16 verdicts finalized (V001–V016).
health: green
kit: v1.7.0 · check: green (bootstrap.py check --strict exit 0) · engaged: yes
last-shipped: #58 0d64f36 (verdict-016: external-review authenticity gate, PROPOSAL 014 — approve a MANDATORY pre-trust gate in the Q-0120 ceremony over suspending @codex; recorded catch 3/3, 0/24 false alarms on the genuine set; headline: all 3 fabrications fail line-range≤EOF alone); prior: #57 aa1a3ce (verdict-015: heartbeat contradiction linter, PROPOSAL 013 — approve both halves; winning cell g3-id+alias × n3-attrib+quote-excl × s3-cross-block, 30/30 real + 44/44 planted, 0 FP flags)
blockers: none
orders: acked=ORDER-001 ORDER-002 ORDER-003 done=ORDER-001 ORDER-002 ORDER-003 (ORDER-001 model-attribution: 📊 Model line on session cards + card markers present; ORDER-002 self-review: docs/retro/self-review-2026-07-11.md with the dated section, ⚑ items mirrored below; ORDER-003 merge-on-green: done-when met 2026-07-12T10:31:24Z — PR #51 (head a7e526b, branch fix/order-003-evidence) merged by github-actions[bot] with ZERO agent merge calls, 28s open-to-merge, enabler run 29189245547 "Auto-merge enabled for PR #51 — it merges when 'substrate-gate' is green"; enabler shipped in PR #50 → e11ed40, mirror of the idea-engine enabler @ b5cc329 with the prefix allowlist rebuilt from sim-lab's surveyed PR heads per the prefix-drift tripwire; both guard classes live-fire verified — born-red refusal on #50, arm-and-merge on #51; live-verified again by PRs #57/#58 zero-agent-merge landings. NOTE for manager: ROUTINE_PAT not set in sim-lab — GITHUB_TOKEN fallback in use and works; flag if PAT-based attribution is wanted.)

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

notes: Scribe-committed heartbeat (coordinator-dictated, merged Ideas Lab seat). CODEX POSTURE: the @codex question step remains suspended @ dedc12e (three replies verified fabricated); VERDICT 016 now supplies the evidence-based ruling — gate, don't suspend (mandatory pre-trust authenticity gate; the step can be reinstated behind it) — the adoption decision sits with manager/owner (OA-002 still open). LEDGER NOTE (neutral fact): INTAKE 013 rode PR #57 in control/inbox.md; INTAKE 014 onward ride control/outbox.md with a source-line note (worker inbox-write restriction) — the intake ledger location is split; the reconciliation pointer lives with the numbering map in docs/current-state.md. Pre-existing flags unchanged: .sessions/2026-07-10-boot.md carries an in-progress marker while check --strict exits 0 (cosmetic, flag only); the recurring evidence gap (no live fishing/mining earn-rate baseline) remains flagged in docs/current-state.md for the manager.
