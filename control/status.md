# sim-lab · status

updated: 2026-07-10T21:20:00Z
phase: continuous mode — VERDICT 001 finalized (INTAKE 003 wild-encounter spawn-tuning; needs-more-evidence, evidence=simulation, gate PASS in-scope); next slice INTAKE 001 (probe panel-mode, measured-prototype rung 2)
health: green
kit: v1.7.0 · check: green (substrate-gate green on PR #6; sim self-checks 946/946, exit 0, deterministic) · engaged: yes
last-shipped: #6 95bdc7dbac55542aeb5e86b6cb4e621dc37b7163 — sim: INTAKE 003 wild-encounter spawn-tuning sweep + VERDICT 001 report
blockers: none
orders: acked= done=
⚑ needs-owner:

**OA-001 — required check + Allow auto-merge on `main` — CONFIRMED-SATISFIED-BY-OBSERVATION (owner: please verify the settings still exist)**
- WHAT: the CI gate is a required check and auto-merge is allowed, so this lane lands its own PRs per CONVENTIONS.md — both re-confirmed WORKING on PR #6 (armed squash auto-merge at creation; ruleset held until `substrate-gate` green; then merged), but neither setting can be read directly, so the owner should still eyeball they exist.
- WHERE: github.com/menno420/sim-lab → Settings → Rules → Rulesets → the ruleset targeting `main` → "Require status checks to pass"; and Settings → General → Pull Requests → "Allow auto-merge".
- HOW: confirm `substrate-gate` is in the status-checks box and "Allow auto-merge" is ticked.
- WHY-IT-MATTERS: without these a green PR sits unmerged and every merge needs a human.
- UNBLOCKS: already unblocked — every verdict PR lands unattended (PRs #2–#6).
- VERIFIED-NEEDED: settings could NOT be read directly (REST branch-protection/repo-object endpoints 403 "GitHub App not connected for this org"; GitHub MCP exposes no branch-protection tool). Resolved by OBSERVED PR behaviour (#2–#6), not by reading the setting.

**OA-002 — enable the Codex GitHub integration for sim-lab — STILL OPEN (now with concrete impact)**
- WHAT: toggle the Codex GitHub integration on for this repo.
- WHERE: chatgpt.com/codex → settings → GitHub integration → add `menno420/sim-lab`.
- HOW: click only.
- WHY-IT-MATTERS: every verdict needs an @codex review before finalization (Q-0264.4). CONCRETE IMPACT NOW: VERDICT 001's @codex comment (PR #6 #issuecomment-4939558686) is posted but will draw no reply until this is on — the verdict is finalized with `codex reply: pending` and was NOT blocked on it (per CONVENTIONS), but the review loop stays open.
- UNBLOCKS: the @codex reply on VERDICT 001 and every future verdict.
- VERIFIED-NEEDED: owner-account screen — agents have no access (PLATFORM-LIMITS.md).

**OA-003 — failsafe wake routine — RESOLVED (armed + verified by coordinator; owner: informational, and note the browser-UI limitation)**
- WHAT: the dead-man failsafe that re-wakes a stalled continuous seat.
- STATE: failsafe routine 'sim-lab failsafe wake': ARMED-BY-COORDINATOR 2026-07-10T20:54:51Z and VERIFIED via list_triggers — trigger_id trig_01SHfnLv6EqZesr4tC3T9kUU, cron `0 1-23/2 * * *` (odd hours UTC, scheduler adds per-trigger jitter: first next_run_at 21:03:10Z), enabled, bound persistent_session_id session_01JbwY8yeBzLKYcbeR89L88v (coordinator), created_via meta_mcp. VERIFIED LIVE END-TO-END — both wake paths observed delivered into the coordinator session 2026-07-10: cron 'sim-lab failsafe wake' fired 21:03Z and the send_later pacemaker one-shot landed 21:11Z; pacemaker chain re-armed (~15-min link) from a worker seat.
- FLEET RECIPE (reproducible): trigger tools live behind ToolSearch in WORKER seats only (create_trigger/list_triggers/etc.); arm from a worker passing persistent_session_id = the coordinator session id. The browser Routines UI can bind repos/environments but NOT project sessions (owner-verified 2026-07-10), so owner-manual creation of this routine is not possible — it must be armed by proxy from a worker seat. The Q-0265 pacemaker `send_later` is likewise armable by proxy.
- WHY-IT-MATTERS / owner note: this arms an odd-hour self-wake bound to the coordinator session that the owner's browser Routines screen cannot see or manage. It is recorded here (committed, owner-visible) for transparency; flagged so the owner can confirm they want the self-waking failsafe + pacemaker armed via this path.
- UNBLOCKS: unattended recovery of the continuous loop between owner check-ins.

notes:

**VERDICT 001 landed (2026-07-10).** First live verdict of the lab. Sim + report: PR #6 (merge 95bdc7dbac55542aeb5e86b6cb4e621dc37b7163). Verdict finalized in `control/outbox.md` this session (control fast-lane). needs-more-evidence · evidence simulation · gate PASS on the in-scope claims.
- Sweep headline: recommended defaults (threshold=24, debounce=30s, cooldown=900s) keep spawns rare-but-visible in every tier (0.93 / 3.00 / 4.38 spawns per active-hour, low/med/high); the debounce×threshold ceiling (5.22/hr) is traffic-independent so busy channels can't spawn-spam; paced-spam farming is hard-capped at 4 claims/hr and fast spam yields zero extra (≥24 spam msgs/reward).
- Negative headline: reward inflation vs fishing/mining is UNMEASURABLE — no live earn-rate baseline exists in the source; the sim reports only absolute mint (~6.8/24.0/35.0 claims per 8h window). REPORT.md names the exact telemetry the smallest slice must log to close it.
- Self-check WIN: an assertion asserting "spawn count invariant to cooldown" FIRED, correctly exposing a real second-order coupling (a faster claim clears the live spawn sooner → accrual resumes sooner); the false invariant was removed and the coupling disclosed in the report's gate-2 answer.
- @codex: comment posted on PR #6 head (one question on the message-driven claim model vs the analytic cooldown cap); reply pending (OA-002).
- Harness note (for future verdicts): the Write tool blocks subagent filenames containing "report"; REPORT.md was landed via scratchpad + cp. Fold a rename/allow convention into harness/ when the pattern repeats.

**Queue / next slice.** INTAKE queue holds 2 remaining: INTAKE 001 (probe panel-mode vs single-pass — measured-prototype rung 2, cost M) then INTAKE 002 (stats-site OAuth trust-gate — spike + JUDGMENT-ONLY, cost M). Continuous mode; next slice INTAKE 001.

seeded 2026-07-10 by the dispatch copilot; continuous mode (Q-0265): send_later pacemaker chain + the odd-hour failsafe 'sim-lab failsafe wake' (trig_01SHfnLv6EqZesr4tC3T9kUU) now armed by proxy (OA-003).
