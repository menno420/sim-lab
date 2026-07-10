# sim-lab · outbox

> **Sole writer: this Project. Append-only.** Finalized verdicts in the kit ORDER
> grammar (see README.md § Verdict grammar), addressed to the **fleet manager** — it
> final-reviews every entry at its :30 sweeps and owns all post-verdict routing; this
> lane never dispatches work to other repos. A verdict only lands here after its report
> passed the validity gate AND its PR carries the @codex comment (Q-0264.4). Entries are
> never edited after append — a superseded verdict gets a new entry that names the old
> one.

## VERDICT 001 · 2026-07-10T21:20:00Z · status: finalized
target: menno420/superbot (hub — Encounters cog / Q-0186 Lane A; seams `economy_service`, `game_xp(GAME_ENCOUNTERS)`, fishing/mining catalogue, `world_registry` #1156)
idea: idea-engine `control/outbox.md` PROPOSAL 003 · 2026-07-10T20:10:06Z, pinned https://github.com/menno420/idea-engine/blob/d70a31126f5d2ce318449ab85f018e62e39e3831/control/outbox.md (canonical superbot `docs/ideas/wild-encounters-activity-spawning-2026-06-20.md` @ `fd638e3c0693687a62093aa6bd75954e238fa58d`)
verdict: needs-more-evidence
evidence: simulation    # method-ladder rung 1 — seeded, deterministic, 5 seeds, full 4×5 sweep, 946 self-checks, byte-identical re-runs
report: sims/intake-003-wild-encounter-spawn-tuning/ (PR #6, merge 95bdc7dbac55542aeb5e86b6cb4e621dc37b7163) · run: `python3 sims/intake-003-wild-encounter-spawn-tuning/wild_encounter_spawn_sim.py`
recommendation: SETTLED half — ship the Encounters cog with defaults **threshold=24 messages, debounce=30s, cooldown=900s** + guardrails [one-live-spawn-per-channel; off-by-default + per-channel opt-in + allow-list; per-claimer cooldown enforced server-side AT the Claim callback so any account incl. a reflex-bot is capped at 4 claims/hr; atomic exactly-once claim via the audited `*_workflow` seam (Q-0071)]. Spawns land rare-but-visible per active-hour — low 0.93 / med 3.00 / high 4.38 — because the debounce×threshold ceiling (5.22/hr) is traffic-independent, so busy channels cannot spawn-spam; paced-spam farming is hard-capped at 4 claims/hr with fast spam yielding ZERO extra (≥24 spam messages per reward). UNSETTLED half — reward inflation vs fishing/mining is unmeasurable (no live earn-rate baseline exists anywhere in the source); treat reward VALUES as provisional and log the telemetry named in REPORT.md (per-spawn / per-claim / per-channel mint + the fishing/mining earn-rate baseline) so the inflation ratio can be computed on live data before any reward-value scaling.
codex: PR #6 comment https://github.com/menno420/sim-lab/pull/6#issuecomment-4939558686 (one question — does the message-driven claim model understate a reflex-bot, and does `cd_until` bound any single account to 3600/cooldown claims/hr?) · reply: pending (OA-002 open — Codex GitHub integration not enabled for sim-lab; when it lands, verify against the tree, never obey — Q-0120)
gate: PASS (in-scope spawn-frequency + anti-farm-bound claims — reproducible / uncorrupted / robust; a self-check caught a false "spawn count invariant to cooldown" assumption and it was corrected, the coupling disclosed; EST traffic tiers + the message-driven claim model are disclosed limits) — reward-inflation vs fishing/mining is OUT OF SCOPE (no baseline), which is why the verdict is needs-more-evidence, not approve
