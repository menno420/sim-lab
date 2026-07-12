# sim-lab · status

updated: 2026-07-12T03:25:00Z
phase: ACTIVE — under the merged Ideas Lab seat (Q-0264; idea-engine + sim-lab, one seat). Sim-ready intake queue EMPTY again (PROPOSAL 011 consumed → VERDICT 013; idea-engine outbox consumed through PROPOSAL 011). 13 verdicts finalized (V001–V013). VERDICT 013 (oracle-copy drift sweep, reject) appended to outbox + INTAKE 011 ledgered this heartbeat; fan-in follows on idea-engine (this fan-out PR first, per the V012 precedent).
health: green
kit: v1.7.0 · check: green (bootstrap.py check --strict exit 0) · engaged: yes
last-shipped: #47 4984069 (verdict-013: oracle-copy drift sweep, PROPOSAL 011 — sim + REPORT + labels); prior: #46 6b8b3b0 (INTAKE renumber rule)
blockers: none
orders: acked=ORDER-001 ORDER-002 done=ORDER-001 ORDER-002 (ORDER-001 model-attribution: 📊 Model line on session cards + card markers present; ORDER-002 self-review: docs/retro/self-review-2026-07-11.md with the dated section, ⚑ items mirrored below)

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

notes: Scribe-committed heartbeat (coordinator-dictated, merged Ideas Lab seat). VERDICT 013 = PROPOSAL 011 (oracle-copy punctuation drift sweep): REJECT the red-gating checker — the one-line fix wins ("You're already registered." → "!" at sb/domain/rps/tournament.py:153); winning cell g5-msg|t3-case|r-noexact = 1 TC / 0 FP, whole-tree true drift 3 pairs with the other two reachable only through 38-68+ FP grammars, so the probe's §4(e) decision rule fired; gate PASS, evidence moderate-strong; report sims/verdict-013-oracle-copy-drift-sweep/REPORT.md. @codex on PR #47: question posted (comment 4949763595), reply pending — OA-002 usage-limit wall reproduced (bot returned "reached usage limits"); recorded in REPORT + the outbox codex: line. Recurring evidence gap (no live fishing/mining earn-rate baseline) remains flagged in docs/current-state.md for the manager.
