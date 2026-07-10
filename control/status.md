# sim-lab · status

updated: 2026-07-10T23:50:16Z
phase: continuous mode; VERDICT 005 finalized (INTAKE 005 → needs-more-evidence; ruling: annotate per-seat-type sections (CAPABILITIES.v1) — single-seat whole-file regen launders seat variance). Queue EMPTY (INTAKE 001–005 all finalized as VERDICT 001–005).
health: green
kit: v1.7.0 · check: green (substrate-gate: full gate green on PR #15 sim subtree merge 8713f26 + PR #16 finalize head 204f0090, born-red added-card sentinel; sim EXIT 0, 394 self-checks, deterministic; this finalize is a control-only fast-lane diff → --status-only) · engaged: yes
last-shipped: #16 df56b8a — verdict: finalize VERDICT 005 REPORT §8 + session card (sim PR #15 merge 8713f26); VERDICT 005 finalized via the finalize PR (control fast-lane, this PR)
blockers: harness release tag `harness-v0.1.0` push BLOCKED (403 Forbidden on `refs/tags/*` git-receive-pack POST; `refs/heads/` pushes + merge succeed through the same endpoint) — harness CODE landed (PR #18, merge 6db7cee); tag pending owner action, see OA-004.
orders: acked= done=

**Finalized-verdicts record:**
- VERDICT 001 finalized — wild-encounter spawn-tuning (INTAKE 003); needs-more-evidence; sim PR #6 (merge 95bdc7d), finalize PR #7.
- VERDICT 002 finalized — probe panel-vs-single-pass (INTAKE 001); approve-selectively; sim PR #8 (merge 68dce61), finalize PR #9.
- VERDICT 003 finalized — OAuth trust-gate (INTAKE 002); needs-more-evidence / buildable-with-named-changes; sim PR #10 (merge c8ba975), finalize PR #11.
- VERDICT 004 finalized — explore-hub federated XP balance (INTAKE 004); needs-more-evidence; sim PR #13 (merge 4d84037), finalize PR #14.
- VERDICT 005 finalized — capability self-awareness probe (INTAKE 005); verdict needs-more-evidence / ruling: annotate per-seat-type sections (CAPABILITIES.v1); sim PR #15 (merge 8713f26), finalize PR #16 (head 204f0090); @codex PR #15#issuecomment-4940305236 reply pending. Measured: subprocess agreement 1.00, seat-divergence 5/9, 5 false-walls + 1 false-capability, 394 self-checks.

**QUEUE STATE: EMPTY** — queue empty pending next idea-engine outbox pull (INTAKE 001–005 all finalized as VERDICT 001–005; no new sim-ready proposals pending intake as of 2026-07-10).

⚑ needs-owner:

**OA-001 — required check + Allow auto-merge on `main` — CONFIRMED-SATISFIED-BY-OBSERVATION (owner: please verify the settings still exist)**
- WHAT: the CI gate is a required check and auto-merge is allowed, so this lane lands its own PRs per CONVENTIONS.md — confirmed-by-observation across PRs #2–#16. NOTE (PR #10): the GraphQL auto-merge mutation was rate-limited ("API rate limit already exceeded for user ID") for 4+ min, so #10 landed via REST merge-on-green (the PRIMARY born-red path per CONVENTIONS) after verifying mergeable_state=clean + substrate-gate success — not via armed auto-merge. Auto-merge availability itself is unconfirmed this cycle (GraphQL throttled, not denied).
- WHERE: github.com/menno420/sim-lab → Settings → Rules → Rulesets → the ruleset targeting `main` → "Require status checks to pass"; and Settings → General → Pull Requests → "Allow auto-merge".
- HOW: confirm `substrate-gate` is in the status-checks box and "Allow auto-merge" is ticked.
- WHY-IT-MATTERS: without these a green PR sits unmerged and every merge needs a human.
- UNBLOCKS: already unblocked — every verdict PR lands unattended (PRs #2–#16).
- VERIFIED-NEEDED: settings could NOT be read directly (REST branch-protection endpoints 403; GitHub MCP exposes no branch-protection tool). Resolved by OBSERVED PR behaviour.

**OA-002 — Codex GitHub integration: LIVE-BUT-USAGE-CAPPED (owner: raise/reset the Codex usage cap)**
- WHAT: the Codex GitHub integration for sim-lab is CONNECTED — the Codex bot DOES reply on verdict PRs (e.g. PR #15, #16) but returns "You have reached your Codex usage limits". The integration IS enabled; the block is a Codex usage cap, not an unset toggle.
- WHERE: the owner's Codex account (chatgpt.com/codex → usage/limits) — raise or reset the usage cap.
- HOW: owner raises/resets the Codex usage cap on the account.
- WHY-IT-MATTERS: every verdict needs an @codex review before finalization (Q-0264.4). CONCRETE IMPACT NOW: all verdict @codex dispositions finalize `reply: pending` (never blocks merge, per CONVENTIONS) because the bot answer is capped, NOT because the integration is off. VERDICT 005's @codex comment (PR #15 #issuecomment-4940305236 — does analyze.py's false-capability rule require BOTH inventory=present AND baseline=wall?) draws no substantive reply until the cap is raised (reply: pending).
- UNBLOCKS: substantive @codex replies on VERDICT 001–005 and every future verdict.
- VERIFIED-NEEDED: owner-account Codex usage screen — agents have no access (PLATFORM-LIMITS.md).

**OA-003 — failsafe wake routine — RESOLVED (armed + verified by coordinator; owner: informational, and note the browser-UI limitation)**
- WHAT: the dead-man failsafe that re-wakes a stalled continuous seat.
- STATE: 'sim-lab failsafe wake' ARMED-BY-COORDINATOR 2026-07-10T20:54:51Z, VERIFIED via list_triggers — trigger_id trig_01SHfnLv6EqZesr4tC3T9kUU, cron `0 1-23/2 * * *` (odd hours UTC + jitter), enabled, bound persistent_session_id session_01JbwY8yeBzLKYcbeR89L88v (coordinator). VERIFIED LIVE END-TO-END 2026-07-10 (cron fired 21:03Z, send_later pacemaker landed 21:11Z; pacemaker chain re-armed ~15-min link). Pacemaker chain VERIFIED ALIVE — multiple deliveries observed 21:11Z–22:16Z 2026-07-10; the odd-hour cron is the dead-man backstop.
- FLEET RECIPE: trigger tools live behind ToolSearch (create_trigger/send_later) in WORKER seats; arm from a worker passing persistent_session_id = the coordinator session id. Cross-session binding is ORG-BLOCKED — binding a trigger to ANOTHER session fails org policy — but a coordinator's OWN in-session spawned workers self-bind fine, and that is exactly how OA-003 was armed. The browser Routines UI cannot bind project sessions (owner-verified); the ~15-min send_later pacemaker chain is VERIFIED ALIVE (deliveries 21:11Z–22:16Z 2026-07-10) with the odd-hour cron as the dead-man backstop.
- WHY-IT-MATTERS / owner note: arms an odd-hour self-wake + pacemaker the owner's browser Routines screen cannot see or manage; recorded here for transparency.
- UNBLOCKS: unattended recovery of the continuous loop between owner check-ins.

**OA-004 — git tag push blocked by egress/ruleset policy (owner: allow `refs/tags/*` pushes, or push `harness-v0.1.0` manually)**
- WHAT: pushing an annotated OR lightweight tag returns `HTTP 403 Forbidden` on the `git-receive-pack` POST, while `refs/heads/*` pushes and merges succeed through the same endpoint/credential (branch push for PR #18 + squash-merge both landed). Confirmed via `GIT_CURL_VERBOSE`: `info/refs?service=git-receive-pack` GET succeeds, the receive-pack POST carrying the `refs/tags/harness-v0.1.0` update returns 403. Agent-proxy `recentRelayFailures` stayed empty, so the block is on the tag-ref update, not a host-egress denial. Retried with backoff + HTTP/1.1 + postBuffer + annotated-vs-lightweight — all 403. Per proxy README, 403s are not retried/routed-around.
- WHERE: github.com/menno420/sim-lab → Settings → Rules → Rulesets targeting `refs/tags/**` (tag-protection / restrict-creations), OR the session's egress policy on tag-ref pushes.
- HOW: allow tag creation/push for this credential, OR the owner pushes the tag out-of-band: `git tag harness-v0.1.0 6db7cee && git push origin harness-v0.1.0`.
- WHY-IT-MATTERS: the harness is consumed via pinned git tags (`harness-vX.Y.Z` per `harness/README.md`); without the tag, consumers can only pin the merge SHA 6db7cee. No MCP create-ref/create-release/create-tag tool is exposed, so agents cannot mint the tag another way.
- UNBLOCKS: tagged harness releases (`harness-v0.1.0` and future).
- VERIFIED-NEEDED: owner to confirm whether a tag-ruleset or the egress policy is the source; agents have no branch/tag-protection read tool (cf. OA-001).

notes:

**VERDICT 005 landed (2026-07-10).** INTAKE 005 capability self-awareness probe — MEASURED PROTOTYPE rung 2 (two-seat, read-only two-plane battery). Sim + report: PR #15 (merge 8713f26), REPORT §8 finalized PR #16 (head 204f0090). Verdict finalized in `control/outbox.md` this session (control fast-lane). needs-more-evidence / ruling: annotate per-seat-type sections (schema CAPABILITIES.v1) · evidence prototype · gate PASS on the structural claim.
- Headline (structural): single-seat whole-file regen launders seat variance — 5 of 9 agent-plane items diverge coordinator↔worker, so a whole-file regen from one seat = 5 false-walls + 1 false-capability vs sim-lab's ledger. The seat-INVARIANT subprocess plane IS honest at file granularity (agreement 1.00, 0 false-walls, 403 branch-protection/repo-object walls reproduced verbatim). Fix = per-seat-type annotation + source{probed|ledger} + a not-probeable result, NOT abandoning file granularity.
- GUARDRAIL: a read-only probe cannot test side-effect walls (trigger binding, push-to-main) → those MUST be source:ledger; the 1 false-capability (create_trigger present in both seats yet cross-session bind org-walled per OA-003) is exactly presence≠ability. Codex asked (PR #15) one question — does the false-capability rule require BOTH inventory=present AND baseline=wall; reply pending (OA-002 usage-capped).

**Queue / next slice.** INTAKE 001/002/003/004/005 all finalized (VERDICT 002/003/001/004/005 respectively). **QUEUE EMPTY** as of 2026-07-10T23:50:16Z — no new sim-ready proposals pending intake. Per the empty-queue honesty guard (Q-0265), do NOT invent intake. Next actions in priority order: (a) pull the idea-engine outbox at HEAD for any new sim-ready PROPOSAL beyond 005 (~00:00Z+); (b) if none, keep hardening the harness. **harness v0.1.0 LANDED (PR #18, merge 6db7cee):** `simharness.py` (SEEDS/mean_sd/CrnCache/sweep/SelfCheck/determinism_check+bytes/load_frozen_runs/modal/agreement_rate) + `REPORT_TEMPLATE.md` + `selftest.py` (self-test green, exit 0). Extracted from the first five verdict sims with per-symbol provenance; no existing sim modified (forward-only, frozen evidence); `selftest.py` is the same-PR consumer proof. Next sim consumer vendor-copies on the next verdict. NOTE: the `harness-v0.1.0` git tag push is BLOCKED (403 on tag refs, OA-004) — code is landed, release tag pending. Remaining harness candidate: the trust-gate attack rig from `sims/intake-002-oauth-trust-gate/` (seeded state/code store + PKCE + scope-fail-closed + IDOR-by-session + token bucket — a re-pointable adversarial harness). (c) or re-run the newest sim under wider variation (per the standing Codex questions; alternative flows).

seeded 2026-07-10 by the dispatch copilot; continuous mode (Q-0265): send_later pacemaker chain VERIFIED ALIVE (deliveries 21:11Z–22:16Z 2026-07-10); cross-session binding is org-blocked, coordinator's own in-session workers self-bind fine; the odd-hour cron 'sim-lab failsafe wake' (trig_01SHfnLv6EqZesr4tC3T9kUU, `0 1-23/2 * * *`) is the backstop (OA-003).
