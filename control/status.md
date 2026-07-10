# sim-lab · status

updated: 2026-07-10T19:30:00Z
phase: SEEDED born-right (dispatch copilot) — awaiting Project boot (founding package §1/§2 pastes)
health: green
kit: v1.7.0 · check: green · engaged: yes (gate wired at seed; the seed push itself is the first live CI run — verify on the Actions tab)
last-shipped: seed commit on main (empty-repo direct push — the one push a ruleset can't cover)
blockers: none
orders: acked= done=
⚑ needs-owner:

**OA-001 — required check + Allow auto-merge on `main`**
- WHAT: make the CI gate a required check and allow auto-merge, so this lane can land its own PRs per CONVENTIONS.md.
- WHERE: github.com/menno420/sim-lab → Settings → Rules → Rulesets → the ruleset targeting `main` → "Require status checks to pass" → Add checks; and Settings → General → Pull Requests → "Allow auto-merge".
- HOW: paste `substrate-gate` in the status-checks search box, select it, Save; tick "Allow auto-merge".
- WHY-IT-MATTERS: without it a green PR can sit unmerged and every merge needs a human.
- UNBLOCKS: the coordinator's ORDER 000 walking skeleton (branch → PR → gate → merge) and every verdict PR after it.
- VERIFIED-NEEDED: fleet-wide inherited wall (PLATFORM-LIMITS.md) — branch-protection/settings edits are owner-click-only; check name `substrate-gate` read from the wired workflow (same name product-forge verified live on its PR #1).

**OA-002 — enable the Codex GitHub integration for sim-lab**
- WHAT: toggle the Codex GitHub integration on for this repo.
- WHERE: chatgpt.com/codex → settings → GitHub integration → add `menno420/sim-lab`.
- HOW: click only.
- WHY-IT-MATTERS: every verdict needs an @codex review before finalization (Q-0264.4) — without the toggle the comment draws no reply and verdicts stall at `pending`.
- UNBLOCKS: the full verdict loop (gate → @codex → finalized outbox entry).
- VERIFIED-NEEDED: owner-account screen — agents have no access (PLATFORM-LIMITS.md); same wall class as the fleet-manager Codex gap already in the owner queue.

notes: seeded 2026-07-10 by the dispatch copilot (superbot round-3 part-4; recipe: part-4 brief §3, third consumer). Coordinator NOT booted — this heartbeat is the seed record, not a wake. First wake must pull idea-engine PROPOSAL 001 (verified waiting, sim-ready, 18:05Z) — the Q-0264 pipeline's end-to-end proof. This seat is born CONTINUOUS (owner directive Q-0265): the send_later continuation chain is the pacemaker; at boot the coordinator arms only the dead-man failsafe — "sim-lab failsafe wake", cron 0 1-23/2 * * * (ODD hours — reads the Idea Engine's even-hour output one hour later; manager reads at :30).
