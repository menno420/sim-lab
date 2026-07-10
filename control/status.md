# sim-lab · status

updated: 2026-07-10T21:00:00Z
phase: BOOT COMPLETE — continuous mode; ORDER 000 walking skeleton landed, verdict-grammar exemplar shipped, intake queue holds 3 (next slice PROPOSAL 003 / INTAKE 003)
health: green
kit: v1.7.0 · check: green (`check --strict` green at seed) · engaged: yes (substrate-gate CI wired at seed and observed live on PRs #2/#3/#4)
last-shipped: PR #4 a2da483 — intake: PROPOSAL 001-003 queued into control/inbox.md (control fast-lane)
blockers: none
orders: acked= done=
⚑ needs-owner:

**OA-001 — required check + Allow auto-merge on `main` — CONFIRMED-SATISFIED-BY-OBSERVATION (owner: please verify the settings still exist)**
- WHAT: the CI gate is a required check and auto-merge is allowed, so this lane can land its own PRs per CONVENTIONS.md — both are now confirmed WORKING by live PR behaviour, but neither could be read directly, so the owner should still eyeball that the settings exist.
- WHERE: github.com/menno420/sim-lab → Settings → Rules → Rulesets → the ruleset targeting `main` → "Require status checks to pass"; and Settings → General → Pull Requests → "Allow auto-merge".
- HOW: confirm `substrate-gate` is listed in the status-checks box and "Allow auto-merge" is ticked. Two facts, resolved SEPARATELY by observation:
  - (a) required-check `substrate-gate` on `main` = ENFORCED — observed live: main's ruleset held PR #2's armed auto-merge RED until `substrate-gate` went green, then merged.
  - (b) "Allow auto-merge" = ENABLED — observed live: auto-merge armed successfully (squash) at PR creation on #2, #3, and #4.
- WHY-IT-MATTERS: without these a green PR sits unmerged and every merge needs a human; the landing lane depends on both.
- UNBLOCKS: already unblocked — the coordinator's ORDER 000 walking skeleton and every verdict PR after it now land unattended.
- VERIFIED-NEEDED: settings could NOT be read directly — REST branch-protection + repo-object endpoints return 403 "GitHub App not connected for this org", and the GitHub MCP exposes no branch-protection/repo-object tool. Both facts were therefore resolved by OBSERVED PR behaviour (#2/#3/#4), not by reading the setting. OA-001 is effectively satisfied for this lane's operation; kept visible so the owner can confirm the underlying settings.

**OA-002 — enable the Codex GitHub integration for sim-lab — STILL OPEN**
- WHAT: toggle the Codex GitHub integration on for this repo.
- WHERE: chatgpt.com/codex → settings → GitHub integration → add `menno420/sim-lab`.
- HOW: click only.
- WHY-IT-MATTERS: every verdict needs an @codex review before finalization (Q-0264.4) — without the toggle the comment draws no reply and verdicts stall at `pending`.
- UNBLOCKS: the full verdict loop (gate → @codex → finalized outbox entry).
- VERIFIED-NEEDED: owner-account screen — agents have no access (PLATFORM-LIMITS.md); same wall class as the fleet-manager Codex gap already in the owner queue.

**OA-003 — arm the failsafe wake Routine — owner-manual-pending**
- WHAT: arm the dead-man failsafe so a stalled continuous seat gets re-woken.
- WHERE: claude.ai → Routines screen.
- HOW: create the Routine with the exact prompt text given in the coordinator's first reply. VERBATIM state: failsafe routine 'sim-lab failsafe wake' (cron 0 1-23/2 * * *): owner-manual-pending — coordinator session has no create_trigger tool (verbatim: tool not present in session toolset) and no send_later tool (continuation chain unavailable); owner must arm it in the claude.ai Routines screen; exact prompt text is in the coordinator's first reply.
- WHY-IT-MATTERS: this seat is CONTINUOUS (owner directive Q-0265); the send_later chain is the pacemaker and the failsafe is the only recovery if the chain breaks — without it a dead seat stays dead.
- UNBLOCKS: unattended recovery of the continuous loop between owner check-ins.
- VERIFIED-NEEDED: the coordinator session toolset contains neither create_trigger nor send_later (verbatim: tool not present in session toolset) — the Routine cannot be armed by an agent; owner-click-only.

notes:

**Boot sequence COMPLETE (2026-07-10).** This heartbeat records the walking-skeleton run end to end; the seat is now in continuous mode with 3 sim-ready entries queued.

**Seed verification** — synced to origin/main HEAD 7f149f0; all 8 seed artifacts PRESENT: kit v1.7.0 engaged; substrate-gate CI wired; all 5 validity-gate questions verbatim in README; control bus + outbox; sims/ + harness/ skeletons; seed card; heartbeat. `check --strict` green at seed.

**ORDER 000 — walking-skeleton verdict.** PR #2 (merge SHA bbcff61) — a READY (not draft) PR adding the born-red boot session card `.sessions/2026-07-10-boot.md`; auto-merge armed at creation (squash); the ruleset held the merge until the `substrate-gate` check #86456422943 succeeded via the born-red advisory-sentinel lane; then auto-merged. No friction, no manual merge call needed. GOTCHA (documented, not a gate failure): a bare local `check --strict` REDS (EXIT 1) on the in-progress born-red card via the newest-by-mtime fallback — this is a main-state artifact of the in-progress card, NOT a gate failure; CI uses the added-card advisory-sentinel path (`--session-log .sessions/__born-red-card-added__.md`, EXIT 0). The control fast-lane uses `check --strict --status-only`.

**REFERENCE.md landed.** PR #3 (merge SHA f958e57) — `sims/REFERENCE.md`, the verdict-grammar exemplar applied to superbot `tools/sim/gen3_deployment_sim.py`; method label `simulation`, evidence-strength `moderate`, validity-gate verdict PASS. Gate green via the advisory-sentinel lane. Note: the external sim re-run was denied by auto-mode, so the exemplar is grounded in the fetched code + its docstring, with minute figures marked illustrative.

**Intake result.** idea-engine `control/outbox.md` fetched at HEAD (HTTP 200); 3 sim-ready entries queued into `control/inbox.md` via PR #4 (merge SHA a2da483, control fast-lane):
- INTAKE 001 — probe panel-mode vs single-pass (measured-prototype/spike, cost M).
- INTAKE 002 — stats-site OAuth trust-gate adversarial verification (spike + JUDGMENT-ONLY, cost M).
- INTAKE 003 — wild-encounter spawn-tuning parameter sweep (numeric simulation, cost S).
NEXT SLICE recommended: **PROPOSAL 003 / INTAKE 003** — numeric simulation, the cheapest-adequate rung and the closest analogue to the REFERENCE gen3 sim.

**Session status.** Boot sequence complete; continuous-mode — queue holds 3 entries, next slice PROPOSAL 003. The boot session card `.sessions/2026-07-10-boot.md` remains born-red/in-progress; it will be flipped to `complete` only as the deliberate final step, which takes the full locked-door gate lane.

seeded 2026-07-10 by the dispatch copilot; booted 2026-07-10 in continuous mode (owner directive Q-0265): the send_later continuation chain is the pacemaker; the dead-man failsafe 'sim-lab failsafe wake' (cron 0 1-23/2 * * *, ODD hours — reads the Idea Engine's even-hour output one hour later) is owner-manual-pending per OA-003.
