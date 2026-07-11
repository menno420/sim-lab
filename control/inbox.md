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

## INTAKE 004 · 2026-07-10T22:35:00Z · status: in-progress
source: idea-engine `control/outbox.md` → PROPOSAL 004 · 2026-07-10T21:25:30Z · status: sim-ready
idea: https://github.com/menno420/idea-engine/blob/cd7251ec30950d12d29e65c57d843864387d0aec/control/outbox.md (canonical superbot `docs/ideas/explore-hub-federated-world-2026-06-19.md` @ fd638e3c0693687a62093aa6bd75954e238fa58d; idea-engine idea entry `ideas/superbot/explore-hub-federated-world-2026-07-10.md` @ e953aaaad335c6a2352b0bea2054ab5f5bbd7fab)
claim: under the explore-hub contract "loops are accelerators, never gates," which global-vs-per-game XP split parameter sets (trickle ratio from per-game XP into the global pool + global-skill effect sizes: stamina/carry/luck/xp-gain) keep the global pool a measurable cold-start accelerator in a new game while never substituting for per-game mastery or gating any content — swept against the shipped mining/fishing earn shapes plus PROPOSAL 003's GAME_ENCOUNTERS source.
method: NUMERIC SIMULATION (ladder rung 1) — seeded, deterministic, multi-seed, full parameter sweep (trickle ratio × effect size × mechanism × veteran depth), self-checked; this session.
done-when / evidence: reproduced-evidence verdict with a parameter sweep (per set: cold-start advantage = time-to-baseline vs a no-global-pool player + a mastery-substitution check + a gate check where content unreachable without global level = fail), ending in ONE recommended default set (trickle + effect sizes + guardrails) for superbot plan PR 2's owner gate, OR an explicit finding that balance cannot be pre-tuned without live data naming the exact telemetry PR 2's plumbing slice must log. The four owner-reserved design questions (hub shape, survival overlay, docking topology, cross-game identity) are OUT OF SCOPE and remain with the owner.
cost: M (one numeric sim + report; verdict this session)

## INTAKE 005 · 2026-07-10T22:35:00Z · status: queued
source: idea-engine `control/outbox.md` → PROPOSAL 005 · 2026-07-10T22:19:04Z · status: sim-ready
idea: https://github.com/menno420/idea-engine/blob/cd7251ec30950d12d29e65c57d843864387d0aec/control/outbox.md (canonical superbot `docs/ideas/project-capability-self-awareness-2026-07-10.md` @ 9624c5399f5b1a3da293c07ce930e8b0410d79e4; idea-engine idea entry @ 6690d2c460725056ba9a0d5d320d0f4e35e90dbb; batched agent-plane half `ideas/superbot/session-start-capability-self-probe-2026-07-10.md` folded in)
claim: can an automated capability probe produce an HONEST docs/CAPABILITIES.md — when the two-plane battery (agent plane: session-start toolset checklist — scheduler tools, GitHub MCP, Bash, subagent spawn; subprocess plane: seed-wall battery — push walls, api.github.com, raw reachability, env tokens) runs from ≥2 documented seat types (coordinator + spawned worker, the OA-003 create_trigger/send_later split), do outputs agree with each other and with the hand-maintained ledgers' verified walls, or does per-seat variance make single-file regeneration a laundering of one seat's world into "the repo's abilities."
method: MEASURED PROTOTYPE/SPIKE (ladder rung 2) — run the battery from ≥2 seat types, per-item present/absent/wall with verbatim errors, three-way diff vs hand-maintained baselines, false-wall/false-capability count; queued next after VERDICT 004.
done-when / evidence: reproduced-evidence verdict with the battery run from ≥2 seat types (per-item results, dated), a three-way diff (seat A vs seat B vs baseline: this repo's planted docs/CAPABILITIES.md seed walls + fleet-manager docs/capabilities.md), and a false-wall/false-capability count — ending in ONE ruling: regenerate-whole-file is honest / probe must annotate per-seat-type sections (schema named) / file-granularity probing cannot be honest — naming the exact output schema a substrate-kit `capabilities --probe` build ORDER should implement.
cost: M-L (multi-seat prototype; EAP platform-ask window ends 2026-07-14)

## ORDER 001 · 2026-07-11T03:29:16Z · status: new
priority: P3
from: fleet-manager manager — ORDER 010 per-lane relay (provenance: fm control/inbox.md ORDER 010 + fm docs/findings/model-matrix-2026-07.md; relayed via fm PR #63)
executor: sim-lab lane coordinator — next fired session
do: Model-attribution ground truth (fleet standing rule, family-level names only per Q-0262): (1) confirm the session-card template carries a `📊 Model:` line — add it if missing; (2) every fired session records the model family its own harness/environment reports (e.g. fable-5, opus-4.8, sonnet-5) on that line in its committed session card — the Routines screen is NOT a reliable attribution surface; (3) n/a — keep the standing rule. sim-lab is idle-by-design (odd-hours failsafe); this order simply waits for the next fired session.
why: the fleet model matrix (fm docs/findings/model-matrix-2026-07.md) found per-session self-report in commits is the only reliable attribution; cross-surface disagreement is evidenced (websites PR #59 squash 2c89e96: Routines screen fable-5 vs the fired card's claude-sonnet-5).
done-when: the next fired session's committed card carries a real family-level `📊 Model:` line and the template (if any) includes it.

## INTAKE 006 · 2026-07-11T04:31:54Z · status: in-progress
source: idea-engine `control/outbox.md` → PROPOSAL 006 · 2026-07-11T04:02:00Z · status: sim-ready
idea: https://github.com/menno420/idea-engine/blob/7df1d6cd09d52ad8574b6f37adf00abb99179f5e/control/outbox.md (idea entry `ideas/superbot-idle/idle-economy-sim-kernel-2026-07-11.md` @ b13aa36d59c75abd639fafe4b4db38be912b1873; relays superbot-idle SIM-001 — `docs/design/economy-v1.md` § "Simulation request — SIM-001 (Q-0264)" @ f11c71a52d4d2adf88b2bf11f5d1134bad495be2)
claim: SIM-001's own pre-registered ask, relayed not reinvented — the provisional economy-v1 parameters (UPGRADE_BASE_COST_SECONDS=60 · COST_GROWTH 115/100 · EFFECT_PERCENT=25 · PRESTIGE_THRESHOLD=100000 · AWARD_DIVISOR=100000 · BONUS_PERCENT=10) hit the pre-registered pacing targets T1–T10 per acceptance criteria A1–A10, under scenarios S1 (idle-only) / S2 (check-in N ∈ {0.25, 2, 8, 24} h, greedy-buy then prestige-iff-eligible) / S3 (optimal 1-s speedrun; S3b threshold policy optional, additive), over a 14-day horizon with ≥3 resets where reachable, driving the REAL `idle_engine/` functions at the pinned commit (deterministic, integer-exact, stdlib-only — re-implementation explicitly unwanted; T10 out of scope by the request's own text, no criterion).
method: NUMERIC SIMULATION (ladder rung 1) — drive the REAL `idle_engine/` @ `f11c71a` across S1/S2/S3, deterministic integer-exact stdlib, 14-day horizon with ≥3 resets where reachable, per-criterion A1–A10 evaluation; handled this session (build subtree `sims/verdict-006-idle-economy-sim-kernel/`).
done-when / evidence: the report format SIM-001 itself pins — one results doc covering outputs O1–O6 (time-to-first-upgrade; purchase timelines through reset 3; currency trajectories; time-to-prestige distribution + per-reset durations; payback curve; 20-reset prestige-stacking with a super-geometric-shrinkage flag) plus a verdict row per criterion A1–A10 — ending in ONE ruling: ALL-PASS graduates the parameter table PROVISIONAL → SIM-PINNED (the lane's follow-up PR updates economy-v1.md + upgrades-prestige-v0.md together, per its own verdict semantics), ANY-FAIL names which criterion broke and by how much so the lane re-registers new values before any engine tuning lands.
depends: superbot-idle (providing lane) — engine `idle_engine/` + the seven-parameter provisional table @ `f11c71a` (parity test-enforced by `tests/test_economy_design_doc.py`; the lane's STEADY-STATE HOLD freezes engine surface pending exactly this verdict, so the pin is policy-stable); SIM-001 is the lane's own committed request, ⚑'d "awaiting manager relay" since its PR #12 — **manager relay verified un-fired at sim-lab HEAD `f70fbea`** (intake = INTAKE 001–005 only, all finalized; a late relay landing after this append is a duplicate, reconcile by source citation at sim-lab intake). Themes carry ZERO economy numbers (schema-bounded, none used by the 12 shipped packs) so the verdict is theme-independent by construction. Known co-consumers: the lane's blocked roadmap item 3 (economy tuning / parameter graduation) + the future generator-purchase-path slice (T10's target pre-registered, awaiting the mechanic).
cost: S (one deterministic stdlib sim driving the real engine + criteria/sweep table — the gen3 / PROPOSAL 003 precedent shape)
