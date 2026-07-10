# sim-lab · status

updated: 2026-07-10T21:52:00Z
phase: continuous mode — VERDICT 002 finalized (INTAKE 001 probe panel-vs-single-pass; approve-selectively, evidence=prototype, gate PASS moderate); next slice INTAKE 002
health: green
kit: v1.7.0 · check: green (substrate-gate green on PR #8, merged ca63b87; sim analyze.py self-checks EXIT 0, deterministic) · engaged: yes
last-shipped: #8 ca63b87 — sim: INTAKE 001 panel-vs-single-pass head-to-head + VERDICT 002 report
blockers: none
orders: acked= done=
⚑ needs-owner:

**OA-001 — required check + Allow auto-merge on `main` — CONFIRMED-SATISFIED-BY-OBSERVATION (owner: please verify the settings still exist)**
- WHAT: the CI gate is a required check and auto-merge is allowed, so this lane lands its own PRs per CONVENTIONS.md — confirmed-by-observation again on PR #8 (auto-merged squash on `substrate-gate` green), but neither setting can be read directly, so the owner should still eyeball they exist.
- WHERE: github.com/menno420/sim-lab → Settings → Rules → Rulesets → the ruleset targeting `main` → "Require status checks to pass"; and Settings → General → Pull Requests → "Allow auto-merge".
- HOW: confirm `substrate-gate` is in the status-checks box and "Allow auto-merge" is ticked.
- WHY-IT-MATTERS: without these a green PR sits unmerged and every merge needs a human.
- UNBLOCKS: already unblocked — every verdict PR lands unattended (PRs #2–#8).
- VERIFIED-NEEDED: settings could NOT be read directly (REST branch-protection/repo-object endpoints 403 "GitHub App not connected for this org"; GitHub MCP exposes no branch-protection tool). Resolved by OBSERVED PR behaviour (#2–#8), not by reading the setting.

**OA-002 — enable the Codex GitHub integration for sim-lab — STILL OPEN (now with concrete impact)**
- WHAT: toggle the Codex GitHub integration on for this repo.
- WHERE: chatgpt.com/codex → settings → GitHub integration → add `menno420/sim-lab`.
- HOW: click only.
- WHY-IT-MATTERS: every verdict needs an @codex review before finalization (Q-0264.4). CONCRETE IMPACT NOW: VERDICT 001 & 002's @codex comments (PR #6 #issuecomment-4939558686, PR #8 #issuecomment-4939797948) are posted but draw no reply until this is on — both verdicts are finalized with `codex reply: pending` and were NOT blocked on it (per CONVENTIONS), but the review loop stays open.
- UNBLOCKS: the @codex replies on VERDICT 001 & 002 and every future verdict.
- VERIFIED-NEEDED: owner-account screen — agents have no access (PLATFORM-LIMITS.md).

**OA-003 — failsafe wake routine — RESOLVED (armed + verified by coordinator; owner: informational, and note the browser-UI limitation)**
- WHAT: the dead-man failsafe that re-wakes a stalled continuous seat.
- STATE: failsafe routine 'sim-lab failsafe wake': ARMED-BY-COORDINATOR 2026-07-10T20:54:51Z and VERIFIED via list_triggers — trigger_id trig_01SHfnLv6EqZesr4tC3T9kUU, cron `0 1-23/2 * * *` (odd hours UTC, scheduler adds per-trigger jitter: first next_run_at 21:03:10Z), enabled, bound persistent_session_id session_01JbwY8yeBzLKYcbeR89L88v (coordinator), created_via meta_mcp. VERIFIED LIVE END-TO-END — both wake paths observed delivered into the coordinator session 2026-07-10: cron 'sim-lab failsafe wake' fired 21:03Z and the send_later pacemaker one-shot landed 21:11Z; pacemaker chain re-armed (~15-min link) from a worker seat.
- FLEET RECIPE (reproducible): trigger tools live behind ToolSearch in WORKER seats only (create_trigger/list_triggers/etc.); arm from a worker passing persistent_session_id = the coordinator session id. The browser Routines UI can bind repos/environments but NOT project sessions (owner-verified 2026-07-10), so owner-manual creation of this routine is not possible — it must be armed by proxy from a worker seat. The Q-0265 pacemaker `send_later` is likewise armable by proxy.
- WHY-IT-MATTERS / owner note: this arms an odd-hour self-wake bound to the coordinator session that the owner's browser Routines screen cannot see or manage. It is recorded here (committed, owner-visible) for transparency; flagged so the owner can confirm they want the self-waking failsafe + pacemaker armed via this path.
- UNBLOCKS: unattended recovery of the continuous loop between owner check-ins.

notes:

**VERDICT 002 landed (2026-07-10).** INTAKE 001 probe panel-mode vs single-pass — measured-prototype rung 2. Sim + report: PR #8 (merge ca63b87). Verdict finalized in `control/outbox.md` this session (control fast-lane). approve-selectively (adopt panel ONLY for big-or-contested ideas; reject always-on) · evidence prototype · gate PASS moderate on the covered claims (verdict-change + cost + quality-preference).
- Headline: panel flipped the modal verdict on 2/3 ideas (BUILD→HOLD on the contested discord-oauth + peer-karma; the karma flip beats intra-mode noise — single-pass unanimous BUILD vs panel modal HOLD), NO flip on the well-scoped wild-encounters; cost 4.00× agents / 3.05× tokens / 1.61× wall; blind judges preferred panel 6/6 (slight margin, no position bias).
- Named limit: verdict CORRECTNESS is UNMEASURED (no ground truth) — the recommendation ships the honesty-norm + over-caution guardrails and per-probe agents/tokens/wall telemetry so correctness can be closed over time on live data.
- OA-002 IMPACT NOW: OA-002 (enable Codex GitHub integration for sim-lab — VERDICT 001 & 002 @codex comments draw no reply until on) STILL OPEN; OA-001 (required-check + auto-merge) confirmed-by-observation (PR #8 auto-merged squash on substrate-gate green); OA-003 failsafe wake armed.

**Queue / next slice.** INTAKE queue holds 1 remaining: INTAKE 002 (stats-site OAuth trust-gate — spike + JUDGMENT-ONLY, cost M). Continuous mode; next slice INTAKE 002 (queued). Harness-extraction candidate = the frozen-run deterministic analyzer pattern (`sims/intake-001-probe-panel-vs-single-pass/analyze.py`) + the instrumented probe head-to-head protocol — reusable for any rung-2 LLM-agent measured prototype; extract to `harness/` when a second consumer appears.

seeded 2026-07-10 by the dispatch copilot; continuous mode (Q-0265): send_later pacemaker chain + the odd-hour failsafe 'sim-lab failsafe wake' (trig_01SHfnLv6EqZesr4tC3T9kUU) now armed by proxy (OA-003).
