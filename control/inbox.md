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

## INTAKE 007 · 2026-07-11T09:42:30Z · status: finalized
source: idea-engine `control/outbox.md` → PROPOSAL 007 · 2026-07-11T09:19:48Z · status: sim-ready
idea: https://github.com/menno420/idea-engine/blob/d213efa01ac2a7badb4bdb338c1623067dd770f7/control/outbox.md (idea entry `ideas/product-forge/games-web-concept-evidence-pass-2026-07-11.md` @ e73f225d0c23f218afdefd1d301b010c7797e8dd; relays product-forge ORDER 001 owner deferral "the full concept heads to sim-lab for an evidence pass later" @ 43563dccc874c58946576444fbba38600bb45f86)
question: Does the games-web comic browser-RPG presentation layer add incremental player/owner value over superbot-mineverse's existing direct utility view of the same miner state (`mining_snapshot.v1`), and should phase 2 proceed-as-scoped / redirect / stop-at-phase-1? (carried from source `question:`)
method: rung-3 JUDGMENT-ONLY on the value axis (no live users / no ground truth reachable here) WITH a rung-2 reproducible CONFORMANCE CHECK core — diff games-web's `games-web.character-sheet` v1.0.1 contract against the real `mining_snapshot.v1` it claims to present, and against the decided committed-JSON transport (fm ORDER 012/013). Precedent: verdict-005 mixed-evidence labeling.
done-when / evidence: reproduced-evidence verdict with STATED criteria + NAMED sources ("not measured" beats invention): (1) concept-value assessment vs the mineverse direct view; (2) conformance check against the committed feed (re-litigate NO transport); (3) ONE ruling proceed-as-scoped / redirect / stop-at-phase-1, WHO-builds (seam A/B/C, idea-engine #87) explicitly out of scope.
depends: product-forge (requesting lane) — phase-1 artifacts as evidence inputs @ 43563dc. Duplicate-guard: the deferral is product-forge's own ORDER 001 prose, so a later manager relay of the same deferral is a duplicate — reconciled by this source citation at intake (PROPOSAL 006 precedent clause). Sequencing: verdict is worth most BEFORE the superbot-lane providing ORDER (fm ORDER 012/013, verified UNROUTED @ 58040c6) unblocks phase-2 spend.
cost: S (conformance diff + structured JUDGMENT-ONLY scoring; no build, no sim)

## ORDER 002 · 2026-07-11T10:00Z · status: new
priority: P1
from: fleet-manager coordinator — owner-requested fleet-wide self-review relay (provenance: filed by fleet-manager on coordinator direction, cse_012o8pySy5K3AV6JWoPKryZL; owner-directed)
executor: sim-lab seat (next wake)
do: quick self-review of this lane covering roughly the last 24h (2026-07-10 ~20:00Z → now): (1) anything that WENT WRONG — red CI runs, guard/classifier denials, walls hit, drift found, mistakes made or corrected — each with a citation (PR/run/commit); (2) anything REQUIRING OWNER ATTENTION — owner-only asks, pending vetoes, risky decisions taken decide-and-flag, spend/publish items — click-level and plain language; (3) one-line current health (what shipped, what's next). Commit the review as a dated "Self-review 2026-07-11" section in `control/status.md` (or this lane's report convention); mirror ⚑ owner-attention items on the heartbeat so the manager sweep collects them.
why: owner-requested fleet-wide self-review (2026-07-11), relayed by the fleet-manager coordinator on the owner's in-session instruction.
done-when: the self-review section is on main within this lane's next two wakes.

## INTAKE 008 · 2026-07-11T12:45:17Z · status: in-progress
source: idea-engine `control/outbox.md` → PROPOSAL 008 · 2026-07-11T12:16:30Z · status: sim-ready
idea: https://github.com/menno420/idea-engine/blob/68f45743d4cab7eab5f863f2918e4fb7d9c1c196/control/outbox.md (idea entry `ideas/superbot/mining-grid-encounters-2026-07-10.md` @ 977662f2d84d1b29d51fbc4121f2e467afcc6a94; canonical superbot `docs/ideas/mining-grid-encounters-2026-06-22.md` @ e1090dbcfdf63ffd955399dc2325b9ad1a2f8c8d)
claim: which (depth threshold, per-action encounter chance, per-player cooldown) sets produce the owner's ruled shape — zero encounters above the threshold, rare-but-present at depth, interruption rate bounded across casual roamer / deep-runner / `!fastmine` grinder playstyles (Q-0087 never-mandatory) — while keeping the loot faucet within a stated fraction of the same trace's `mine_here` earn rate, and does per-action rolling stay farm-unprofitable for the fastmine grinder vs honest play?
method: numeric simulation (rung 1, this session) — seeded grid-traversal traces × full (threshold, chance, cooldown) sweep; encounters/hr per playstyle per set, grinder-vs-honest yield ratio, loot-faucet estimate vs simulated `mine_here` earn rate. Mirrors VERDICT 001 (sims/intake-003-wild-encounter-spawn-tuning).
done-when / evidence: gated report — sweep table (encounters/hr per playstyle per set) + grinder-vs-honest yield ratio for recommended defaults + loot-faucet estimate relative to `mine_here` earn rate; ONE recommended (threshold, chance, cooldown) set + guardrails (per-player not per-cell cooldown; one live encounter per player; audited-seam resolution), OR explicit "defaults cannot be pre-tuned without live data" naming the exact telemetry the smallest slice must log. VERDICT 001's no-earn-rate-baseline caveat restated verbatim.
depends: superbot (hub) seams — grid navigator `views/mining/grid_mine_view.py`, audited `mining_workflow` (RS02/Q-0071), `economy_service`/`update_mining_item`/`game_xp`; co-consumers: the Q-0186 wild-encounters/Encounters-cog build (shared encounter-resolution engine, VERDICT 001 sim-pinned defaults) and the fishing/mining earn-rate baseline telemetry both verdicts name. duplicate-guard: same resolution engine as VERDICT 001 — whichever build lands first fixes it.
cost: M — one sim session, this session.

## INTAKE owner-001 · 2026-07-11T15:16:50Z · status: finalized · source: OWNER-DIRECT (not idea-engine queue)
source: owner-direct request 2026-07-11 (mennovanhattum@gmail.com) via coordinator routing — "run a simulation against all superbot-next functions/settings, compare with old superbot especially the settings, find redundant/combinable settings, reachability of each, AI-panel improvables, and measure the UX delta."
idea: subject repos read-only — superbot-next @ 168ef8080347905766893fd92ae3be1ec2ebbc4c (main), superbot @ 9f46cb7840cb2216a012002fe27feb342d45f480 (main)
method: NUMERIC/STRUCTURAL SIMULATION (rung 1–2, measured-from-code): full settings/command/panel inventory + diff, redundancy (dead/display-only/duplicate/subordinate), combinability (co-read collapse + seeded config-space sampling), reachability graph (steps-to-reach per setting, discoverability, task battery), AI-panel independent structured audit, UX-delta proxies. Overall-UX-improved magnitude = JUDGMENT-ONLY.
outcome: VERDICT 009 finalized → outbox (needs-more-evidence / approve-the-direction + named changes). Report sims/owner-001-superbot-next-settings-ux/REPORT.md.

## INTAKE 009 · 2026-07-11T16:36:50Z · status: in-progress
source: menno420/idea-engine control/outbox.md @ 05601ba3ef751e794b610b2dbc84fe8a30398dd0 (PROPOSAL 009, status: sim-ready)
idea: superbot docs/ideas/settle-once-architecture-guard-2026-06-24.md @ 8214200aa0c00dda4156748617c9482dadc4277a (canonical); idea-engine ideas/superbot/settle-once-architecture-guard-2026-07-10.md @ b2b855b8a11c8bcf47a48b859a04d16fa2b264ba
method: NUMERIC SIMULATION / reconstruction (rung 1–2) — reconstruct each of the six documented double-settlement instances as a minimal replayable case, then run every candidate settle-once guard contract through a catch matrix (instance × contract: prevented-statically / caught-at-runtime / missed) + a false-positive column (legit settlement must still pass) + a variant/interleaving generalization sweep.
target (build, if approved): superbot-next (owns the tools/check_* CI seam, the K7 op grammar D-0010, the D-0042 wager-lane discipline); lane-side one-liner for superbot (Rule 6 registry-roots drift).
corpus: (1) superbot BUG-0013 deathmatch challenge-view timeout; (2) RPS PvP #1444; (3) deathmatch bot-duel #1444; (4) blackjack PvP #1445; (5) Gate-V Arm-D deathmatch W/L double-write #1781; (6) superbot-next #133 blackjack-tournament consolation double-payout.
done-when: reproduced-evidence verdict — catch matrix + false-positive count + one recommended guard contract stated as the invariant every money-moving leg must satisfy + the static rule that enforces it; states whether superbot's Rule 6 registry-roots drift (check_consistency.py:1151 roots=("views/","services/") vs docstring cogs/) changes the catch row.
finalizes-as: VERDICT 010 (009 already used by owner-direct settings/UX audit).
this session.

## INTAKE owner-002 · 2026-07-11T18:20:00Z · status: finalized · source: OWNER-DIRECT (not idea-engine queue)
source: owner-direct request 2026-07-11 (mennovanhattum@gmail.com) via coordinator routing — audit the fleet's websites: do the four sites (control-plane, botsite, dashboard, review) serve their stated purpose, is the navigation healthy (dead links / orphans / dead-ends / broken assets), and are they consistent with each other.
idea: subject repo read-only — menno420/websites @ 31cfd9f (four services enumerated by review/app.py:3-15 + docs/current-state.md). games-web (product-forge concept, VERDICT 007) + superbot-stats (botsite phase-3 feature, VERDICT 003) investigated and excluded — not among the four.
method: (1) NUMERIC/MEASURED CRAWL SIMULATION (rung 1–2) for the 3 LIVE-crawled production Railway sites (control-plane/botsite/dashboard, 2 passes each, stdlib HTTP BFS, 80-page/depth-2 cap) + (2) MEASURED PROTOTYPE for the not-deployed review site (built + served locally, crawled at 127.0.0.1, Playwright local). Deterministic analyzer re-derives every number from the committed snapshots; byte-identical re-run; 243 self-checks.
outcome: VERDICT 011 finalized → outbox (approve — serves-purpose on all four + ship named fixes; owner-action: deploy review). Report sims/owner-002-websites-purpose-nav/REPORT.md.

## INTAKE 012 · 2026-07-12T00:58:00Z · status: finalized
source: idea-engine `control/outbox.md` → PROPOSAL 010 · 2026-07-11T19:41:38Z · status: sim-ready — internal handoff (merged Ideas Lab seat, Q-0264; pulled directly, not via public-raw poll)
idea: https://github.com/menno420/idea-engine/blob/a9b41f6d51ce8aa34e16c65cb909a8d0ac3c8cf5/control/outbox.md (idea entry `ideas/superbot/rebuild-design-cite-checker-2026-07-10.md` @ a9b41f6d51ce8aa34e16c65cb909a8d0ac3c8cf5; canonical superbot `docs/ideas/rebuild-design-cite-checker-2026-07-04.md` @ b2b7fe0c)
question: Which spec should `tools/check_doc_cites.py` ship with — sweeping the cite-rule ladder (file-exists / +line-range≤EOF / +identifier-near-cited-lines) and cite-grammar/scope variants over the two real doc corpora (superbot-next@2c62a099973a2ee384af51e9a33074d9cd411002, superbot@b2b7fe0ce02a2a68cc18eac5242ab160b7b4330f), measured by true catches vs false positives per variant? (carried from source `question:`)
method: MEASURED PROTOTYPE/SPIKE (rung 2, with a numeric-sweep layer) — built the candidate extract-resolve-judge engine and ran the full 36-variant × 2-corpora grid + a 10-cite planted synthetic layer; handled this session (build subtree `sims/verdict-012-doc-cite-checker-spec/`).
done-when / evidence: per-variant catch and false-positive counts on both corpora with the flagged cite lines listed, an explicit check that the known fabrication class (e.g. the `disbot/core/contracts.py:48-52` `WorkflowResult` case) is caught, and ONE ruling naming cite grammar (regex), doc-tree scope, and warn-vs-red gating — sized so the superbot-next lane build is a single file plus one ci.yml loop word.
finalizes-as: VERDICT 012 (numbering by intake order — V009/V011 were owner-direct intakes; INTAKE number aligned to the verdict per the REPORT numbering note).
outcome: VERDICT 012 finalized → outbox (approve). Report sims/verdict-012-doc-cite-checker-spec/REPORT.md @ e3be974 (verdict PR #44).
