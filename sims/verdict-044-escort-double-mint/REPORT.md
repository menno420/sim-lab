# VERDICT 044 — DND-ESCORT-DOUBLE-MINT (phase 1: recon + reproduction)

Run window: 2026-07-13T10:53:37Z -> 2026-07-13T11:05:40Z (all `date -u`).
Ruling applied per the PRE-REGISTERED rule in `decision-rule.md` (written BEFORE any probe ran).

## RULING: **mint-at-most-once** (pre-registered rule 2 fires)

One escort should mint the `safe_passage` bundle at most once per session. Concrete guard: a one-shot flag on `services/dnd_workflow.DnDState` (e.g. `bundle_minted: bool = False`), checked and set inside `services/dnd_workflow.choose` between the `resolve(...)` call (line 243 at the pin) and `_fold_reward(state, resolution.reward)` (line 254): if `resolution.reward is not None and state.bundle_minted`, fold nothing (audit the scene transition instead); else fold and set the flag. Surface: 1 dataclass field + ~4 lines; prototype measured in probe 7 — packet arc, loop attack, and honest scout route ALL land at exactly 1 mint. Scene rewiring (the alternative) zeroes the honest scout->signal route and leaves the road mint re-farmable per session — rejected. Engine-level persistence (the "real" fix — the engine's own `QuestStateError` guard already forbids re-completing a persisted instance, probe 4) is the architectural follow-up, not the balance patch.

Why not `intended`: the mint is UNBOUNDED, not 2x — the packet's arc is one point on a 1-mint-per-choose line (rule 2 condition: C2 UNBOUNDED and no committed text blesses repeat minting; the committed SIM-REQUEST itself marks intent as an open question at the pin).
Why not `NULL`: intent IS decidable — the loopability measurement plus the catalog's own cap discipline ("every grant <= GLOBAL_MAX component-wise" as the stated economy invariant, docs/balance.md:13) discriminate cleanly.

## B0 validity gate — PASS (packet claim REPRODUCED exactly)

Driven through the audited seam (`services.dnd_workflow.choose`) on the byte-copied pinned modules, `DnDState()` defaults, fixed `now`, counter mutation ids, zero decision-bearing RNG:
`waystation_road · advance_escort` -> mint #1 (5/25/10) -> `waystation_gate · circle_to_treeline` (narrate) -> `treeline_watch · signal_escort` -> mint #2 (5/25/10), `ended=True`.
Exactly TWO `safe_passage` completions, each exactly `TIER_CAPS[RewardTier.I] = (global_xp=5, game_xp=25, currency=10)`; totals g10/x50/c20 = 2x tier I; two `reward:*` audit rows (`reward:waystation_road`, `reward:treeline_watch`). Full trace: `outputs/b0_traversal.out`. Every step legal at the xp=0 width-2 FLOOR menu (nothing clamped).

## The three pre-registered criteria

- **C1 reward-scale consistency: WITHIN-SCALE.** 2x tier-I = (10, 50, 20) <= TIER_CAPS[II] = (10, 60, 25) component-wise (1.000 / 0.833 / 0.800 of tier II) and <= GLOBAL_MAX = (20, 120, 50). The bounded 2x alone would NOT break the catalog's scale. (probe 1)
- **C2 loopability: UNBOUNDED — the dominant finding.** `signal_escort` at `treeline_watch` has `next_scene_id=None` => the seam leaves `scene_id` unchanged ("the beat concludes / stays") and nothing ends the session: 10/10 repeats re-mint legally (never clamped) -> 12 mints in 13 chooses, totals g60/x300/c120 = 12x tier I (currency already 2.4x the GLOBAL_MAX per-grant ceiling). Greedy N=100: 99 mints, (495, 2475, 990), asymptotic 1 mint/choose (mint #1 at choose 1, #2 at choose 3, then every choose). No cooldown, one-shot flag, or completion memory anywhere on the path (DnDState fields: capability, currency, game_xp, global_xp, player_id, scene_id, seed, xp — no quest state). Root cause: `_escort_step` (games/dnd/core/effects.py) runs a FRESH `offer -> accept -> apply_event -> grant_rewards` cycle per call and discards the instance; both cycles even derive the SAME deterministic `instance_id` (`q-safe_passage-player-9182fb68` at session seed 0) — the engine names one logical quest but no layer stores it, so the engine's own re-completion guard (`QuestStateError: accept requires OFFERED, got completed`) can never fire. (probes 2, 3, 4, 5, 6)
- **C3 design-doc language: NEUTRAL — no once-per-escort ceiling committed anywhere at the pin.** Per-choice framing only ("a valid escort choice mints exactly ``catalog.TIER_CAPS[RewardTier.I]``", effects.py docstring). The committed test `test_reward_accumulates_across_the_escort_double_mint_arc` (services/tests/test_dnd_workflow.py:161) asserts the 2x but its own docstring defers: "The one arc that fires escort_step twice mints the reward 2x (the SIM-REQUEST)." — characterization pending this verdict, not a blessing. docs/balance.md:179: "there is no in-domain cooldown, so the host decides how often a scene/quest can be run" — commits rerun CADENCE to the host but says nothing about per-traversal double minting. The packet itself files intent as open.

## Key numbers

| quantity | value |
|---|---|
| mint per `safe_passage` completion | (global_xp 5, game_xp 25, currency 10) = TIER_CAPS[I] |
| packet-arc total (2x) | (10, 50, 20) — within TIER_CAPS[II] (10, 60, 25) |
| stay-loop, 13 chooses | 12 mints -> (60, 300, 120) = 12x tier I |
| greedy, 100 chooses | 99 mints -> (495, 2475, 990); 0.99 mints/choose |
| farm rate limit | none in-domain; host choose-cadence only (docs/balance.md:179) |
| exploit gating by XP width | none — both escort options sit at index 0, inside the width-2 floor; live for a fresh 0-XP player (probe 8) |
| guard surface (recommended) | 1 field on DnDState + ~4 lines in choose(); measured: 1 mint on every route incl. loop attack (probe 7) |

## Per-probe one-liners

1. `probe1_mint_scale.py` — mint = (5,25,10); 2x = (10,50,20) <= tier II and GLOBAL_MAX -> C1 WITHIN-SCALE.
2. `probe2_stay_loop.py` — after the packet arc, `signal_escort` re-mints 10/10 legal repeats -> C2a UNBOUNDED.
3. `probe3_farm_rate.py` — greedy 100 chooses = 99 mints (0.99/choose); steady-state 1 mint/choose from choose #3.
4. `probe4_instance_persistence.py` — fresh instance per effect call, identical instance_id, engine's QuestStateError guard unreachable — root cause is missing persistence, not the engine.
5. `probe5_guard_scan.py` — no cooldown/one-shot/completion field anywhere on the path; only per-instance QuestState.COMPLETED, never stored.
6. `probe6_path_census.py` — exhaustive census (62 legal paths <= 5 chooses): max mints = path length − (0 or 1); 2x is not a ceiling.
7. `probe7_fix_surface.py` — seam one-shot flag: 1 mint on all routes; scene rewiring: kills honest route + leaves road re-mint; engine store: largest surface. Recommend seam flag.
8. `probe8_width_lever.py` — width lever (2->4 via 500 XP/option) never gates the exploit; whole arc legal at the floor.

## The 8-question battery (sim-lab convention)

1. **What is this really?** Not a double-mint bug but a missing-persistence bug wearing one: the escort effect is a stateless self-completing quest cycle, so EVERY escort choice is a fresh full payout — 2x on the packet arc, Nx on the stay-loop.
2. **Possibility space?** intended / mint-at-most-once (seam flag, scene rewiring, engine store) / NULL — three guard shapes priced in probe 7.
3. **Most advanced capability by simplest implementation?** The seam one-shot flag: 1 field + ~4 lines gives exactly-once semantics per session while keeping every choose audited.
4. **What breaks it?** For the ruling: a committed host-layer cap on chooses per session would bound the farm (none exists in this repo at the pin — balance.md delegates cadence, not count). For the game: any player who notices "Signal the escort onward" never greys out.
5. **What does it unlock?** Closes the last open superbot-games balance item of ORDER 006 batch 2 (items 4-7) and gives the D&D lane its first measured emission ceiling (currently unbounded per session; guarded: 1 bundle/session).
6. **What does it depend on?** The pin 57f69be3; the seam's documented None=>stay semantics; the width floor surfacing both escort options (all verified by mechanical drive, not reading).
7. **Which lane should build it?** superbot-games (its seam, its data catalog); the engine-store follow-up belongs to the quest-engine owner with its own sim.
8. **Smallest shippable slice?** The DnDState flag + guard in choose() with a test flipping test_reward_accumulates_across_the_escort_double_mint_arc's assertion from 2x to 1x.

## Determinism / self-check

Full battery run twice in clean shells; `diff -r outputs outputs2` -> BYTE-IDENTICAL (recorded 2026-07-13T11:05:40Z). Zero decision-bearing RNG (DetRng streams seeded but escort outcomes deterministic; fixed injected `now`; counter mutation ids). No seeds drawn from the fleet ladder (high-water 20260880 untouched).

## Pins, hashes, provenance

- Order item: idea-engine `control/inbox.md` @ **8218d6630f53633461d993d9a3caa4ad54ab251d** line 75 — verbatim in `order-item.md`; matches the dispatch gist exactly.
- Packet: menno420/superbot-games @ **57f69be34785afb427d608b207e7369025166e94**, `control/outbox.md` lines 186-221 — verbatim in `packet.md` (ask: "decide whether one escort completing `safe_passage` twice (and minting 2x) is intended, or whether the arc should mint the escort bundle at most once.").
- sim-lab conventions read @ **48dd6a614169063017ba9f33f0285c1481e05956** — `conventions.md` (next free simreq id: simreq-007; our verdict number: 044; 041/043 reserved by siblings).
- Byte-copied modules (19 files, full import closure of the escort path incl. the audited seam): `modules/` + `manifest.sha256` (sha256 per file + pin sha).
- Captured outputs sha256: b0 30cb9868, p1 12943620, p2 87c457d4, p3 52c45bc0, p4 75ccaff6, p5 9b73df5c, p6 432da1af, p7 a9009cf0, p8 7c9bf209 (full values via `sha256sum outputs/*.out`).

## Capability walls hit

None. Anonymous blobless clone of menno420/superbot-games through the pre-configured proxy succeeded first try (no raw-fetch fallback needed). No writes to any control surface; no commits/pushes anywhere (phase-1 rule).

## Quotes (load-bearing, verbatim)

- ORDER 006 item 6: "(6) DND-ESCORT-DOUBLE-MINT — one traversal completes the safe_passage ESCORT bundle TWICE and mints 2× (games/dnd/core/effects.py _escort_step is wired to two options on one arc in games/dnd/data/scenes.py: advance_escort@waystation_road + signal_escort@treeline_watch). Verdict wanted: intended, or mint-at-most-once per escort?"
- Packet ask: "**Ask:** decide whether one escort completing `safe_passage` twice (and minting 2×) is intended, or whether the arc should mint the escort bundle at most once."
- docs/balance.md:179 @ 57f69be: "Per-hour currency/xp for DND and exploration is host-gated (there is no in-domain cooldown, so the host decides how often a scene/quest can be run)."
- services/tests/test_dnd_workflow.py:162 @ 57f69be: "The one arc that fires escort_step twice mints the reward 2x (the SIM-REQUEST)."

## Scope / limits

Phase 1 only: nothing committed or pushed; all artifacts live in the scratchpad `verdict-044/`. The seam-flag guard is per-SESSION (per DnDState); cross-session re-runs remain host-cadence territory exactly as docs/balance.md already assigns them — the guard closes the in-domain hole (2x per traversal and the unbounded stay-loop), not host scheduling. Fun/narrative value of a repeatable "signal" beat is out of scope; if the seat wants a repeatable narrate-only beat, rewire the SECOND press to `scout_narrate` AFTER the flag lands (data-only, no balance number invented).
