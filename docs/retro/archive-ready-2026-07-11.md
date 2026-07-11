# Archive-ready — 2026-07-11

> **Status:** `reference` — the single-paragraph true state at archive time,
> every open owner-action, and what a fresh session needs to resume.

## Current true state (one paragraph)
sim-lab is green and idle-clean at origin/main HEAD (close-out PR merged
2026-07-11). Eleven verdicts are finalized in control/outbox.md (V001–V011),
scoreboard: 3 approve (006, 010, 011), 1 approve-selectively (002), 5
needs-more-evidence (001, 003, 004, 005, 008), 1 redirect (007). Every verdict
passed the validity gate. Harness v0.1 (harness/simharness.py + REPORT_TEMPLATE
+ selftest) is live as the standing second product (consumed via raw/copy; tag
un-pushed — OA-004). The idea-engine sim-ready queue is fully consumed (through
PROPOSAL 009 → VERDICT 010); no open PRs, no branches beyond main, no open
issues. kit v1.7.0, `bootstrap.py check --strict` exits 0.

## Open owner-actions (⚑)
- **OA-002 — Codex usage cap.** The @codex integration is LIVE but usage-capped:
  the bot replies "reached usage limits" on every verdict PR; 6+ @codex
  questions pending (e.g. PR #38 comment
  https://github.com/menno420/sim-lab/pull/38#issuecomment-4948283951). Verdicts
  finalized without fold-in (merge not gated). Owner: raise/reset the Codex
  quota, or accept verdicts ship without the Codex fold-in.
- **OA-003 — review-site deploy.** VERDICT 011 built the `review` site for
  Anthropic reviewers but there is no deployed URL. Owner: deploy it (routed via
  outbox VERDICT 011; not a sim-lab blocker).
- **OA-004 — harness tag-push 403.** Pushing refs/tags/* is 403-walled;
  harness-v0.1.0 is un-pushed (a local tag → 6db7cee existed only in a dead
  session). Owner: allow tag pushes or push the tag from a fresh clone.
- **OA-005 — standing failsafe trigger.** Recurring cron trigger
  `trig_01SHfnLv6EqZesr4tC3T9kUU` ('sim-lab failsafe wake', cron `0 1-23/2 * * *`)
  is still bound to the to-be-archived coordinator session. Owner: disable/delete
  it in the Routines screen, OR a future coordinator re-arms per
  PLATFORM-LIMITS.md § wake-recipe. (Pacemaker one-shot
  trig_01QoXDsjqF1QhgyDcVXYFMN9 was being disarmed at hand-off.)
- **control-plane dead links (manager/lane, not owner).** VERDICT 011 headline:
  control-plane ships 25 dead in-content links — routed to the websites lane via
  outbox.

## Blocked-on-another-project
- **idea-engine** — no new sim-ready intake until PROPOSAL 010+ posts to
  menno420/idea-engine control/outbox.md. sim-lab is idle-waiting on supply.
- **earn-rate telemetry** — no live fishing/mining earn-rate baseline exists; it
  blocked VALUE-terms conclusions in VERDICTs 001 and 008. The named telemetry
  slice is the unlock; owned upstream, not in sim-lab.
- **Codex quota** (OA-002) — external, blocks the @codex fold-in step.

## Resume recipe for a fresh session
1. Land on origin/main HEAD; read README.md + CONVENTIONS.md + control/ (inbox,
   outbox, status).
2. Re-arm the wake loop per PLATFORM-LIMITS.md § "Routine / wake arming": from a
   WORKER seat, ToolSearch → create_trigger with persistent_session_id = own
   coordinator session (cross-session binding is org-walled).
3. Poll menno420/idea-engine control/outbox.md (public raw) for PROPOSAL 010+
   with status: sim-ready; INTAKE into control/inbox.md citing the source entry.
4. If queue empty: harden the newest verdict under wider variation or harden the
   harness; flag "queue empty" in status. Never invent intake.

## Verdict-numbering map (chat-only, now durable)
- VERDICT 009 = OWNER-DIRECT settings/UX audit (superbot-next vs superbot) — NOT
  an idea-engine proposal.
- idea-engine PROPOSAL 009 (settle-once-architecture-guard) became VERDICT 010
  (the owner-direct 009 + owner-002 verdicts interleaved, offsetting the
  numbers).

## Chat-only knowledge — confirmed captured
Wake/routine recipe, merge-path facts, OA ledger, verdict-numbering map, and the
earn-rate evidence gap are all now in the repo (PLATFORM-LIMITS.md,
docs/current-state.md, docs/retro/). Nothing load-bearing remains chat-only.
