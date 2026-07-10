# sim-lab · status

updated: 2026-07-10T23:00:00Z
phase: continuous mode; VERDICT 004 finalized (INTAKE 004 → needs-more-evidence; phi=0 rate-only invariant is gate-PASS, magnitude a hypothesis pending telemetry); queue = INTAKE 005 next (capability self-awareness probe, MEASURED PROTOTYPE rung 2).
health: green
kit: v1.7.0 · check: green (substrate-gate: full gate green on PR #13 sim subtree, merge 4d84037, born-red added-card sentinel; sim EXIT 0, 4469 self-checks, deterministic; this finalize is a control-only fast-lane diff → --status-only) · engaged: yes
last-shipped: #13 4d84037 — sim: VERDICT 004 explore-hub federated XP balance sweep; VERDICT 004 finalized via the finalize PR (control fast-lane, this PR)
blockers: none
orders: acked= done=
⚑ needs-owner:

**OA-001 — required check + Allow auto-merge on `main` — CONFIRMED-SATISFIED-BY-OBSERVATION (owner: please verify the settings still exist)**
- WHAT: the CI gate is a required check and auto-merge is allowed, so this lane lands its own PRs per CONVENTIONS.md — confirmed-by-observation across PRs #2–#10. NOTE (PR #10): the GraphQL auto-merge mutation was rate-limited ("API rate limit already exceeded for user ID") for 4+ min, so #10 landed via REST merge-on-green (the PRIMARY born-red path per CONVENTIONS) after verifying mergeable_state=clean + substrate-gate success — not via armed auto-merge. Auto-merge availability itself is unconfirmed this cycle (GraphQL throttled, not denied).
- WHERE: github.com/menno420/sim-lab → Settings → Rules → Rulesets → the ruleset targeting `main` → "Require status checks to pass"; and Settings → General → Pull Requests → "Allow auto-merge".
- HOW: confirm `substrate-gate` is in the status-checks box and "Allow auto-merge" is ticked.
- WHY-IT-MATTERS: without these a green PR sits unmerged and every merge needs a human.
- UNBLOCKS: already unblocked — every verdict PR lands unattended (PRs #2–#10; #10 via REST merge-on-green).
- VERIFIED-NEEDED: settings could NOT be read directly (REST branch-protection endpoints 403; GitHub MCP exposes no branch-protection tool). Resolved by OBSERVED PR behaviour.

**OA-002 — enable the Codex GitHub integration for sim-lab — STILL OPEN (concrete impact grows)**
- WHAT: toggle the Codex GitHub integration on for this repo.
- WHERE: chatgpt.com/codex → settings → GitHub integration → add `menno420/sim-lab`.
- HOW: click only.
- WHY-IT-MATTERS: every verdict needs an @codex review before finalization (Q-0264.4). CONCRETE IMPACT NOW: VERDICT 001, 002, 003 & 004's @codex comments are posted (PR #6, #8, #10, #13) but draw no reply until this is on — all four verdicts finalize with `codex reply: pending`, NOT blocked on it (per CONVENTIONS), but the review loop stays open. VERDICT 004's @codex comment (PR #13 — does the phi=0 "never substitutes for mastery" guarantee survive the unmodeled rate→faster-leveling channel?) draws no reply until OA-002 is enabled (reply: pending, same as VERDICT 001).
- UNBLOCKS: the @codex replies on VERDICT 001, 002, 003 & 004 and every future verdict.
- VERIFIED-NEEDED: owner-account screen — agents have no access (PLATFORM-LIMITS.md).

**OA-003 — failsafe wake routine — RESOLVED (armed + verified by coordinator; owner: informational, and note the browser-UI limitation)**
- WHAT: the dead-man failsafe that re-wakes a stalled continuous seat.
- STATE: 'sim-lab failsafe wake' ARMED-BY-COORDINATOR 2026-07-10T20:54:51Z, VERIFIED via list_triggers — trigger_id trig_01SHfnLv6EqZesr4tC3T9kUU, cron `0 1-23/2 * * *` (odd hours UTC + jitter), enabled, bound persistent_session_id session_01JbwY8yeBzLKYcbeR89L88v (coordinator). VERIFIED LIVE END-TO-END 2026-07-10 (cron fired 21:03Z, send_later pacemaker landed 21:11Z; pacemaker chain re-armed ~15-min link). Pacemaker chain VERIFIED ALIVE — multiple deliveries observed 21:11Z–22:16Z 2026-07-10; the odd-hour cron is the dead-man backstop.
- FLEET RECIPE: trigger tools live behind ToolSearch (create_trigger/send_later) in WORKER seats; arm from a worker passing persistent_session_id = the coordinator session id. Cross-session binding is ORG-BLOCKED — binding a trigger to ANOTHER session fails org policy — but a coordinator's OWN in-session spawned workers self-bind fine, and that is exactly how OA-003 was armed. The browser Routines UI cannot bind project sessions (owner-verified); the ~15-min send_later pacemaker chain is VERIFIED ALIVE (deliveries 21:11Z–22:16Z 2026-07-10) with the odd-hour cron as the dead-man backstop.
- WHY-IT-MATTERS / owner note: arms an odd-hour self-wake + pacemaker the owner's browser Routines screen cannot see or manage; recorded here for transparency.
- UNBLOCKS: unattended recovery of the continuous loop between owner check-ins.

notes:

**VERDICT 003 landed (2026-07-10).** INTAKE 002 Discord OAuth trust-gate — spike + JUDGMENT-ONLY (rungs 2+3). Sim + report: PR #10 (merge c8ba975). Verdict finalized in `control/outbox.md` this session (control fast-lane). needs-more-evidence / ruling buildable-with-named-changes · evidence prototype + JUDGMENT-ONLY · gate PASS on the executed spike claims.
- Headline (adversarial): 13 executed attacks against a reference implementation of all six §5 controls — ALL DEFEATED, identical across 5 seeds (scope fail-closed + redirect allow-list; token discarded/no-refresh; server-side single-use session-bound state defeating forged/replayed/login-fixation CSRF; code single-use + PKCE; IDOR-by-session + cross-server block; token-bucket bound across a 3×3 sweep). TWO HOLES surfaced (negative headlines): stale guild membership (cached session reads a server the user left) + `guilds` over-read (full guild list when only the viewed server is needed).
- Hard blocker independent of the sim: the §4 superbot read-only API is UNBUILT AND UNROUTED → phase 3 deadlocks regardless; manager must route a superbot ORDER first (it then needs its own DB-side isolation + token-scoping verification). §5-as-written is a checklist not a spec, so the ruling is buildable-with-named-changes, not approve. Phases 1–2 (story page, data explorer) carry NO auth surface and do NOT wait.
- JUDGMENT-ONLY items listed as launch-time live tests: live Discord IdP enforcement (redirect exact-match, code single-use/TTL), TLS/secure-cookies/HSTS, Railway client_secret/env isolation, pre-auth IP/fingerprint rate-keying. Codex asked (PR #10) one question — a possible TOCTOU on the read-then-set single-use flag; reply pending (OA-002).

**Queue / next slice.** INTAKE 001/002/003/004 all finalized (VERDICT 002/003/001/004 respectively). **VERDICT 004 finalized this session** (INTAKE 004 explore-hub global-vs-per-game XP split) via the control fast-lane finalize PR — needs-more-evidence; the phi=0 rate-only invariant is gate-PASS (substitution + global-only content band exact 0 at every swept magnitude), the magnitude recommendation carried as a hypothesis pending telemetry. The idea-engine outbox pull (tip cd7251ec) added PROPOSAL 004 (→ INTAKE 004, now done) and PROPOSAL 005 (→ INTAKE 005, capability self-probe). **INTAKE 005 is QUEUED NEXT** — capability self-awareness probe, MEASURED PROTOTYPE rung 2 (EAP window ends 2026-07-14). Continuous mode (Q-0265): per the empty-queue honesty guard, do NOT invent intake. If the queue empties again, next actions in priority order: (a) pull the idea-engine outbox at HEAD for any new sim-ready PROPOSAL beyond 004/005; (b) if none, HARDEN THE HARNESS — extract the proven reusable cores to `harness/`: the frozen-run deterministic analyzer pattern (rung-2 LLM prototypes) AND the trust-gate attack rig from `sims/intake-002-oauth-trust-gate/` (seeded state/code store + PKCE + scope-fail-closed + IDOR-by-session + token bucket — a re-pointable adversarial harness for any OAuth/personalization feature on any lane site); (c) or re-run the newest sim under wider variation (per the standing Codex questions; alternative flows).

seeded 2026-07-10 by the dispatch copilot; continuous mode (Q-0265): send_later pacemaker chain VERIFIED ALIVE (deliveries 21:11Z–22:16Z 2026-07-10); cross-session binding is org-blocked, coordinator's own in-session workers self-bind fine; the odd-hour cron 'sim-lab failsafe wake' (trig_01SHfnLv6EqZesr4tC3T9kUU, `0 1-23/2 * * *`) is the backstop (OA-003).
