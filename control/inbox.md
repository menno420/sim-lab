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

## INTAKE 010 · 2026-07-12T00:58:00Z · status: finalized
source: idea-engine `control/outbox.md` → PROPOSAL 010 · 2026-07-11T19:41:38Z · status: sim-ready — internal handoff (merged Ideas Lab seat, Q-0264; pulled directly, not via public-raw poll)
idea: https://github.com/menno420/idea-engine/blob/a9b41f6d51ce8aa34e16c65cb909a8d0ac3c8cf5/control/outbox.md (idea entry `ideas/superbot/rebuild-design-cite-checker-2026-07-10.md` @ a9b41f6d51ce8aa34e16c65cb909a8d0ac3c8cf5; canonical superbot `docs/ideas/rebuild-design-cite-checker-2026-07-04.md` @ b2b7fe0c)
question: Which spec should `tools/check_doc_cites.py` ship with — sweeping the cite-rule ladder (file-exists / +line-range≤EOF / +identifier-near-cited-lines) and cite-grammar/scope variants over the two real doc corpora (superbot-next@2c62a099973a2ee384af51e9a33074d9cd411002, superbot@b2b7fe0ce02a2a68cc18eac5242ab160b7b4330f), measured by true catches vs false positives per variant? (carried from source `question:`)
method: MEASURED PROTOTYPE/SPIKE (rung 2, with a numeric-sweep layer) — built the candidate extract-resolve-judge engine and ran the full 36-variant × 2-corpora grid + a 10-cite planted synthetic layer; handled this session (build subtree `sims/verdict-012-doc-cite-checker-spec/`).
done-when / evidence: per-variant catch and false-positive counts on both corpora with the flagged cite lines listed, an explicit check that the known fabrication class (e.g. the `disbot/core/contracts.py:48-52` `WorkflowResult` case) is caught, and ONE ruling naming cite grammar (regex), doc-tree scope, and warn-vs-red gating — sized so the superbot-next lane build is a single file plus one ci.yml loop word.
finalizes-as: VERDICT 012.
outcome: VERDICT 012 finalized → outbox (approve). Report sims/verdict-012-doc-cite-checker-spec/REPORT.md @ e3be974 (verdict PR #44).

## INTAKE 011 · 2026-07-12T03:25:00Z · status: finalized
source: idea-engine `control/outbox.md` → PROPOSAL 011 · 2026-07-12T02:22:07Z · status: sim-ready — internal handoff (merged Ideas Lab seat, Q-0264; pulled directly, not via public-raw poll)
idea: https://github.com/menno420/idea-engine/blob/6d9e80ec7fbb4f64541b929a6a10f85207400252/control/outbox.md (idea entry `ideas/superbot-next/oracle-copy-punctuation-drift-sweep-2026-07-12.md` @ 6d9e80e; probe pin 2aa1b2fa, probe verdict idea-engine PR #239 head 2ad3408)
question: which (user-copy enumeration grammar × match-normalization tier) cell maximizes true drift catches at near-zero false positives on the real corpora (superbot-next@af985c17def5ff2478103cb363ebb150cb583a97 sb/ literals vs superbot@1ecc21138fe0a1eb672d03b66bd319164c29d55f disbot/ copy), and does the winning cell's true-catch count justify a red-gating checker over a one-line fix? (carried from source `question:`)
method: MEASURED PROTOTYPE/SPIKE (rung 2, with a numeric-sweep layer) — built the candidate `check_copy_drift.py` engine (AST literal extraction → normalization → oracle-pool pairing) and ran the full 60-cell grid (6 enumeration grammars × 5 normalization tiers × 2 gating/pairing rules) over the two real pinned corpora + a seeded planted-drift layer (seed 20260712) with hand-derived per-tier expectations; handled this session (build subtree `sims/verdict-013-oracle-copy-drift-sweep/`).
done-when / evidence: per-cell TC/FP on the real corpora + planted-drift recall, the winning grammar + normalization + gating/waiver spec stated machine-readably, and the tournament.py:153 instance caught by the winning cell — the live drift citation the winning cell must re-find: superbot-next `sb/domain/rps/tournament.py:153` "You're already registered." (period) vs oracle "You're already registered!" @ superbot `1ecc211` `disbot/views/rps/registration.py:49` / `disbot/utils/tournaments.py:44`.
finalizes-as: VERDICT 013 (proposal-aligned numbering per the INTAKE 009/010 / PR #46 rule; V009/V011 were owner-direct interleaves).
outcome: VERDICT 013 finalized → outbox (reject — the one-line fix wins). Report sims/verdict-013-oracle-copy-drift-sweep/REPORT.md @ 4984069 (verdict PR #47).

## ORDER 003 · 2026-07-12T08:30Z · status: new
priority: P2
owner: Ideas Lab coordinator (executor)
provenance: filed by the fleet manager — relocation of startup-prompt v3.1 order 2 (prompts are STATELESS since v3.2, owner correction 2026-07-12; fleet-manager PR #108). Order 1 (handoff verification) is DEAD: sims/verdict-012-doc-cite-checker-spec/ exists at e857b24 and the chain has moved on (PROPOSAL 011 sim-ready, verdict-013 landed).
do: Stand up a GITHUB_TOKEN merge-on-green workflow (or install the kit auto-merge enabler) so sim-lab PRs land without an agent merge call; until it exists, park PRs READY+green.
why: verified at e857b24 2026-07-12: .github/workflows/ contains substrate-gate.yml only — no enabler, no merge-on-green path.
done-when: a PR lands without an agent merge call, evidence cited in status.

## INTAKE 012 · 2026-07-12T15:26:00Z · status: finalized
source: idea-engine `control/outbox.md` → PROPOSAL 012 · 2026-07-12T14:23:57Z · status: sim-ready — internal handoff (merged Ideas Lab seat, Q-0264; pulled directly, not via public-raw poll)
idea: https://github.com/menno420/idea-engine/blob/ff48c2fad809ce7704bb66aafee42335efd5c3fd/control/outbox.md (idea entry `ideas/fleet/routine-cadence-economics-sim-2026-07-12.md` @ 87f0dd2; probe verdict idea-engine PR #259 head fc90d7f)
question: Given trigger-arrival trace T (the real ~14h corpus reconstructed from idea-engine `control/status.md` history `fc0bab6..531b109`, each arrival tagged webhook-visible vs inbox-only, plus seeded Poisson/burst variants) and cost model C (1 worker-turn per pacemaker re-arm, 1 recon-worker-turn per failsafe sweep, ~0 marginal per webhook wake — units stated as worker-turns, not tokens), which policy in grid G = {failsafe-2h, failsafe-1h, failsafe-30m, failsafe-2h + chain-15m-while-work-open, event-driven-only, hybrid(event-driven + failsafe-2h)} minimizes worker-turns per caught trigger subject to p95 catch-latency ≤ 2h, and is any policy strictly dominated across all trace variants? (carried from source `question:`)
method: NUMERIC SIMULATION (rung 1) — seeded, deterministic, parameter-swept discrete-event replay of the real reconstructed corpus + 40-seed Poisson/burst/empty synthetics, full 144-cell grid (6 policies × 12 variant-instances × 2 catch defs) + sensitivities S1–S8; handled this session (build subtree `sims/verdict-014-routine-cadence-economics/`).
done-when / evidence: the per-cell table + dominance verdict + a stated per-variant sensitivity note on the n=1 real trace. (carried from source `done-when:`)
finalizes-as: VERDICT 014 (proposal-aligned numbering per the INTAKE 009/010 / PR #46 rule; VERDICT 013 was PROPOSAL 011, no owner-direct interleave since).
outcome: VERDICT 014 finalized → outbox (approve — keep hybrid(event-driven + failsafe-2h), posture unchanged). Report sims/verdict-014-routine-cadence-economics/REPORT.md @ 477b452 (verdict PR #53, merged by github-actions[bot] via the ORDER 003 enabler).

## INTAKE 013 · 2026-07-12T22:41:51Z · status: finalized
source: idea-engine `control/outbox.md` → PROPOSAL 013 · 2026-07-12T22:04:42Z · status: sim-ready — internal handoff (merged Ideas Lab seat, Q-0264; pulled directly, not via public-raw poll)
idea: https://github.com/menno420/idea-engine/blob/20c5abd7fe0869804d15cb5275c56415f08fe231/control/outbox.md (idea entry `ideas/fleet/heartbeat-contradiction-linter-2026-07-12.md` @ 0a9bfc8de70f83042dee443fe93864942a36d516; landed via idea-engine PR #275)
question: Over the 22 committed revisions of idea-engine control/status.md (fc0bab6 → 0cfe15e, git log --follow), which (fact-key extraction grammar × disposition-vocabulary normalization × comparison scope) cell catches the one known live intra-file contradiction — c77563c line 3 "STILL ENABLED and LEFT ARMED deliberately" vs line 9 "being DISMANTLED with the chat archive", both about trig_01T83UuVthszGBcENYwrTrm7 — plus planted disposition-flip contradictions, at near-zero false positives on the other 21 revisions (in particular NOT flagging e66c78a's quotation-negation carry "the stale Q-0265 … paragraph is DROPPED as superseded"), and does the winning cell's TC/FP profile justify shipping a kit advisory contradiction linter alongside the single-home grammar rule, or the rule alone? (carried from source `question:`; corpus count reconciled at intake — endpoint-inclusive fc0bab6→0cfe15e is 23 revisions, the "22" is the git-exclusive range count, both endpoints touch the file; see the sim's labels.json)
method: MEASURED PROTOTYPE/SPIKE (rung 2, with a numeric-sweep layer) — built the candidate fact-key→normalization→scope detector engine and ran the full 27-cell grid (3 extraction grammars × 3 disposition normalizations × 3 comparison scopes) over the real committed corpus (23 sha256-pinned fixture revisions) + 44 enumerated planted disposition flips (no RNG); handled this session (build subtree `sims/verdict-015-heartbeat-contradiction-linter/`).
done-when / evidence: the per-cell {real-TC, FP, planted-recall} table on the real corpus with the flagged lines listed, the winning cell's grammar/normalization/scope stated machine-readably, the c77563c instance caught and the e66c78a carry un-flagged by the winning cell — ending in ONE ruling: rule + linter (advisory spec named for the kit status-checker family) / single-home rule only (measured FP floor stated) / neither (missing evidence named); real-TC and planted-recall reported separately, keyed-facts-only detection boundary stated. (carried from source `done-when:`)
finalizes-as: VERDICT 015 (proposal-aligned numbering per the INTAKE 009/010 / PR #46 rule; VERDICT 014 was PROPOSAL 012, no owner-direct interleave since).
outcome: VERDICT 015 finalized → outbox (approve — ship BOTH halves: single-home grammar rule + kit advisory contradiction linter, winning-cell spec in the report). Report sims/verdict-015-heartbeat-contradiction-linter/REPORT.md (this verdict PR).

## ORDER 004 · 2026-07-13T09:11:00Z · status: new
priority: P2
owner: Ideas Lab coordinator (executor)
provenance: NIGHT REPORT REQUEST — owner ask 2026-07-13 (relayed via Fleet Manager)
do: post a THOROUGH night report, window 2026-07-12T22:30Z→now, to control/status.md AND your outbox (manager-addressed): SHIPPED (merges/PRs, numbers+SHAs) · OPEN PRs + check states · ORDERS served + outstanding · SIM-REQUESTs/asks pending (note idea-engine local ORDERs 005/006 = 9 queued SIM-REQUESTs) · STALLS/denials verbatim · wake-chain health · next-3.
why: owner morning review.
done-when: report in both files; Fleet Manager compiles the roll-up.

## ORDER 005 · 2026-07-13T22:14Z · status: new
**EAP final-night worklist — owner directive relay (fm ORDER 045, Phase 3 fan-out).**

Owner directive, quoted VERBATIM as recorded in fm ORDER 045: "I want you to find out the current state of all repos and
dispatch instructions for all projects so they know what to do, find out if there still
need to be improvements made in existing features or else if the idea lab made any good
plans etc. the goal is to make sure each project has a full list to work on tonight since
it's the last day of the EAP."

Citations: fm ORDER 045, control/inbox.md @ ca1ce28 · docs/eap-final-night-worklists-2026-07-13.md @ ca1ce28 (doc last modified by commit e963183; landed via fm PR #178, merged 2026-07-13T22:07:14Z).

**Your seat's full night worklist, copied faithfully from the doc:**

## sim-lab — swept @ `32ff5c3`

Healthy and nearly drained: 57 verdicts finalized, 0 open PRs, all ORDERs done.

1. PROPOSAL 047 → VERDICT 058 — creature-rarity vs skill-counter battle sweep, the only sim-ready unverdicted proposal (idea-engine `control/outbox.md` L401 @`66a05b1`, sim-ready 21:28Z, seeds 20261325–328) `[standing]`
2. Heartbeat/ledger refresh through V057 + fleet-seed high-water 20261328 (`control/status.md` 20:08:41Z @`32ff5c3`) `[drift]`
3. `docs/current-state.md` drift — says "verdicts through 045 / V046 pending", stale by 11 verdicts (V046 landed #96) `[drift]` (fix-on-sight class)
4. Kit upgrade v1.7.0 → v1.15.0 — standing watch from the session-2 close; no upgrade PR open at sweep (`control/status.md` kit line @`32ff5c3`) `[improve]`
5. Own outbox rollover prep — 1028 lines and heading for the same 256KB wall as idea-engine ASK 004; adopt whatever convention fm answers (`control/outbox.md@32ff5c3`) `[improve]`

**Blocked (do not schedule):** OA-002 Codex quota · OA-003 review-site deploy · OA-004 harness tag-push 403 (all owner actions, `control/status.md` ⚑ @`32ff5c3`).

Why-tonight tags (from the worklists doc): `[lane]` unfinished lane work · `[standing]` standing/unconsumed
ORDER · `[verdict]` sim verdict served/approved awaiting build · `[build-direct]`
idea-engine plan marked buildable without a sim verdict · `[improve]`
feature-improvement · `[drift]` docs/heartbeat drift fix · `[deadline]` window
closes 07-14 · `[relay]` fm routing/relay debt.

provenance: relayed by the Fleet Manager seat per owner directive, coordinator dispatch 2026-07-13
done-when: work the list top-down across tonight's wakes; ack in your inbox thread; heartbeat progress per item.

ack: 2026-07-13T22:29:14Z — sim-lab seat. ORDER 005 received; worklist being worked top-down. Item 1 done pre-order (PROPOSAL 047 → VERDICT 058, PR #111 @ 8454eb7, finalized 21:56:47Z — before this ORDER's stamp; VERDICT 059 likewise landed 22:11:31Z via PR #112 @ 458f3bd). Items 2–3 this wake (branch claude/order-005-housekeeping). Item 4 (kit v1.7.0 → v1.15.0) dispatched separately, not this wake. Item 5 prep only — rollover/split awaits the fleet-manager's ASK 004 convention answer; sizes verified at HEAD 94cdfba: sim-lab control/outbox.md 834,592 B / 1,068 lines, idea-engine control/outbox.md 408,710 B / 413 lines. Per-item progress on control/status.md. (Ack appended inside this thread per the ORDER's own done-when; lane appender — manager ORDER text untouched.)
