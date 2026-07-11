# sim-lab · status

updated: 2026-07-11T20:00:00Z
phase: CLOSE-OUT / ARCHIVE-READY — coordinator chat being archived. Sim-ready intake queue EMPTY (idea-engine outbox consumed through PROPOSAL 009 → VERDICT 010). 11 verdicts finalized (V001–011). No open PRs/branches/issues. Durable state brought current: docs/current-state.md living ledger filled (recently-shipped + OA ledger + verdict-numbering map + earn-rate evidence gap); PLATFORM-LIMITS.md lane-local walls recorded (wake-recipe, merge-path, tag-push); ORDER-002 self-review + archive-ready note in docs/retro/. A fresh session resumes from README + CONVENTIONS + control/, re-arms the wake loop per PLATFORM-LIMITS.md § wake-recipe, and polls idea-engine outbox for PROPOSAL 010+.
health: green
kit: v1.7.0 · check: green (bootstrap.py check --strict exit 0) · engaged: yes
last-shipped: this close-out PR — durable-state capture (current-state ledger + PLATFORM-LIMITS walls + docs/retro self-review & archive-ready note + close-out session card); prior: #41 4c74d7a (owner-002 robustness heartbeat)
blockers: none
orders: acked=ORDER-001 ORDER-002 done=ORDER-001 ORDER-002 (ORDER-001 model-attribution: 📊 Model line on the close-out session card + card markers present; ORDER-002 self-review: docs/retro/self-review-2026-07-11.md with the dated section, ⚑ items mirrored below)

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

### ⚑ OWNER-ACTION — OA-005 standing failsafe trigger
WHAT: Disable/delete recurring trigger trig_01SHfnLv6EqZesr4tC3T9kUU ('sim-lab failsafe wake', cron `0 1-23/2 * * *`), or re-arm per PLATFORM-LIMITS.md wake-recipe.
WHERE: Routines screen — it is bound to the to-be-archived coordinator session.
HOW: owner disables it in the Routines UI (cross-session unbind is org-walled from agents).
WHY-IT-MATTERS: it will keep firing at a dead session after archive.
UNBLOCKS: a clean archive.
VERIFIED-NEEDED: trigger armed + confirmed firing 2026-07-10.

notes: CLOSE-OUT session (owner order — wrap the project for archive; anything not in the repo is LOST). No new feature work. All in-flight work classified: 0 open PRs, 0 open issues, only origin/main; verdict PRs #2–#41 all merged. Chat-only knowledge captured to durable homes (wake-recipe + merge-path + tag-push → PLATFORM-LIMITS.md; OA ledger + verdict-numbering map + earn-rate gap → docs/current-state.md; self-review + archive-ready → docs/retro/). Recurring evidence gap (no live fishing/mining earn-rate baseline) flagged in current-state for the manager. This heartbeat is the LAST commit of the close-out PR.
