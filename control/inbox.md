# sim-lab · inbox

> ORDERS to this Project. **ONE order-writer: the manager** — never edit a manager
> ORDER. Report order progress in `control/status.md` (`orders: acked=… done=…`).
> Protocol: `control/README.md`. **Lane-specific extension (founding package §2 /
> Q-0264):** this lane ALSO appends its own **INTAKE** entries here — `status: sim-ready`
> proposals pulled from `menno420/idea-engine` `control/outbox.md` (public raw, at HEAD),
> each citing the source entry verbatim by number + timestamp. Two appenders, disjoint
> block types (`## ORDER` = manager-only · `## INTAKE` = this lane only), both
> append-only — never edit the other's blocks.

*(no manager orders yet — the manager appends `## ORDER 001 · <ISO8601> · status: new`
blocks here.)*

---

# INTAKE queue (this lane only — `status: sim-ready` pulls from idea-engine outbox)

> Pulled 2026-07-10 from `menno420/idea-engine` `control/outbox.md` (public raw, at HEAD).
> Each entry cites its source outbox proposal verbatim by number + timestamp. Queued only —
> no sim run this wake. **Next slice: PROPOSAL 003** (see recommendation at the foot).

## INTAKE 001 · 2026-07-10T20:35:00Z · status: queued
source: idea-engine `control/outbox.md` → PROPOSAL 001 · 2026-07-10T18:05:00Z · status: sim-ready
idea: https://github.com/menno420/idea-engine/blob/3e3e80d73ea4ad2af1a0f8bee49262db1da09302/ideas/superbot/idea-probe-brainstorm-simulator-2026-07-10.md (canonical: https://github.com/menno420/superbot/blob/main/docs/ideas/idea-probe-brainstorm-simulator-2026-07-10.md)
claim: panel-mode probing (mode 2 — N ideation personas + synthesizer) changes the recommendation or materially improves probe-report quality vs the single-pass battery (mode 1) by enough to justify its multi-agent cost.
method: MEASURED PROTOTYPE/SPIKE (ladder rung 2) — no seedable dynamics to model, so build the smallest real thing: run both probe modes head-to-head on ≥3 real backlog ideas and instrument agents/tokens/wall-time.
done-when / evidence: verdict comparing mode 1 vs mode 2 on ≥3 real backlog ideas — per idea both reports, whether the recommendation flipped, a quality judgment with stated criteria, and measured cost (agents/tokens/wall-time) — ending in ONE ruling: adopt panel always / only for big-or-contested ideas / never.
cost: M (multi-agent runs × ≥3 ideas, token/wall-time instrumentation)

## INTAKE 002 · 2026-07-10T20:35:00Z · status: queued
source: idea-engine `control/outbox.md` → PROPOSAL 002 · 2026-07-10T19:35:00Z · status: sim-ready
idea: https://github.com/menno420/idea-engine/blob/3e0131182acc89d9dcf708797e79cf3a7636c538/ideas/websites/superbot-site-stats-data-story-2026-07-10.md
claim: the §5 OAuth trust-gate for per-server personal stats (Discord OAuth `identify`+`guilds` only, no long-lived token storage, CSRF/state correctness, per-user isolation, rate limiting, abuse cases) plus the §4 superbot read-only API surface holds up under adversarial verification — i.e. the stats phase is buildable-trustworthy as designed.
method: MEASURED PROTOTYPE/SPIKE — item-by-item attack/defense on the OAuth trust-gate + read-only API surface; likely JUDGMENT-ONLY-plus-spike (prototype where a real attack/defense can be demonstrated; JUDGMENT-ONLY, labeled as such, for design items with no runnable dynamics).
done-when / evidence: verdict with a per-§5-item pass/fail checklist (concrete evidence or demonstrated attack), covering both the websites-side OAuth flow and the superbot-side read-only API — ending in ONE ruling: buildable-as-designed / buildable-with-named-changes (listed) / redesign-needed; MUST state explicitly that phases 1–2 (story page, data explorer) carry no auth surface and do not wait on it.
cost: M (adversarial checklist + narrow attack spikes; no long-running sim)

## INTAKE 003 · 2026-07-10T20:35:00Z · status: queued
source: idea-engine `control/outbox.md` → PROPOSAL 003 · 2026-07-10T20:10:06Z · status: sim-ready
idea: https://github.com/menno420/idea-engine/blob/ff75265e737c984bd3b01441c25c4f3f57e217bf/ideas/superbot/wild-encounters-activity-spawning-2026-07-10.md (canonical: https://github.com/menno420/superbot/blob/fd638e3c0693687a62093aa6bd75954e238fa58d/docs/ideas/wild-encounters-activity-spawning-2026-06-20.md)
claim: some (spawn threshold, debounce window, per-claimer cooldown, one-live-spawn-per-channel) set keeps encounter spawns rare-but-visible across low/medium/high traffic tiers while making paced-spam farming unprofitable — and drawing rewards from the existing fishing/mining pool does not materially undercut those games' earn rates.
method: NUMERIC SIMULATION (ladder rung 1) — seeded channel-activity traces (low/med/high + an adversarial paced-spam farmer), parameter sweep of spawn threshold/debounce/cooldown, farmer-vs-honest yield ratio, reward-inflation estimate. Cheapest-adequate rung, closest to the gen3_deployment_sim precedent (see `sims/REFERENCE.md`).
done-when / evidence: verdict with a parameter sweep (spawn frequency per traffic tier per set), a farmer-vs-honest yield ratio for the recommended defaults, and a reward-inflation estimate vs current fishing/mining earn rates — ending in ONE recommended default set (threshold, debounce, cooldown) + guardrail list, OR an explicit "cannot pre-tune without live data" naming the exact telemetry the smallest slice must log.
depends: superbot (hub) seams — `economy_service`, `game_xp`, fishing/mining catalogue, `world_registry` #1156; co-consumers Pokétwo Lanes B/C/D (collection, quests, shiny).
cost: S (one seeded stdlib sim + sweep — the gen3 precedent shape)

**Next slice → run PROPOSAL 003 first.** It is a clean numeric simulation — rung 1, the
cheapest-adequate rung — and the closest analogue to the settled `gen3_deployment_sim`
precedent that `sims/REFERENCE.md` documents, so it reuses that exemplar's shape directly
(seeded traces, parameter sweep, gate answers). Then INTAKE 001 (measured-prototype), then
INTAKE 002 (spike + JUDGMENT-ONLY). No sim was run this wake — queue only.
