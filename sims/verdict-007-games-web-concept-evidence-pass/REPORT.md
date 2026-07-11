# VERDICT 007 — games-web comic-RPG presentation layer vs mineverse direct view

- Live verdict for: PROPOSAL 007 (games-web-concept-evidence-pass), idea-engine `control/outbox.md` @ d213efa (idea `ideas/product-forge/games-web-concept-evidence-pass-2026-07-11.md` @ e73f225d)
- Evidence inputs (frozen, pinned in runs/): product-forge `products/games-web/` @ 43563dc; superbot-mineverse @ 2b1bd0b
- run: `python3 sims/verdict-007-games-web-concept-evidence-pass/analyze.py`

## METHOD LABEL: JUDGMENT-ONLY (value axis) + reproducible CONFORMANCE CHECK (rung-2 measured core)
"Does a presentation layer add value" has no ground truth reachable from this environment — no live users, no engagement telemetry — so the value question is rung-3 JUDGMENT-ONLY (hypothesis, not evidence). What IS checkable is checked (rung 2): a deterministic diff of the games-web `games-web.character-sheet` v1.0.1 contract against the real `mining_snapshot.v1` it claims to present, and against the decided committed-JSON transport (fm ORDER 012/013). The ruling is DRIVEN by the conformance check (measured fact); the value axis is scored transparently on stated criteria and carried as hypothesis.

## What it MEASURES / MODELS
- CONFORMANCE (measured, reproducible): field-level diff of two committed contracts at pinned SHAs — gear-slot taxonomy, stat provenance, rarity/power provenance, dropped fields, transport-envelope identity. `analyze.py` loads the frozen contracts + `stated.json` and asserts each mismatch (harness SelfCheck), byte-identical output, exit 0.
- VALUE (JUDGMENT-ONLY): 5 stated criteria scored against named evidence inputs (phase-1 artifacts + mineverse artifacts). No agent-judge panel was run: agreement would measure inter-judge consensus, not value-correctness (no ground truth), and would not move a ruling the conformance check already forces — omitted as agreement-theater ("not measured beats invention").

## What it SETTLED (load-bearing, measured)
1. NON-CONFORMANT AS-SCOPED (headline). games-web's contract is a hand-authored RPG fiction, not a projection of `mining_snapshot.v1`:
   - Gear taxonomies are DISJOINT: games-web 8 slots {head,chest,hands,legs,feet,main_hand,off_hand,trinket} ∩ mineverse 9 slots {tool,light,charm,weapon,shield,helmet,chestplate,leggings,boots} = ∅.
   - Stats are INVENTED: games-web {strength,endurance,haste,luck,ore_yield,armor} have no source field in `mining_snapshot.v1`.
   - rarity + power per gear item exist in games-web, absent from real data (mineverse tracks name + `gear_wear`).
   - games-web drops coins/energy/depth/position/vault/biome/leaderboards that the real feed carries.
2. TRANSPORT CONFLICT. games-web's own phase-2 proposal (`docs/phase2-data-api-proposal.md`) asks for a separate `GET /v1/games-web/character-sheet/{id}` emitting `games-web.character-sheet` — conflicting with the decided superbot-lane committed-JSON `mining_snapshot.v1` feed (fm ORDER 012/013). "Phase 2 = presentation layer on the committed feed" (proceed-as-scoped) is therefore NOT buildable without re-contracting games-web or re-litigating transport (which the proposal forbids).

## What it did NOT settle (negatives as headlines)
- Whether the comic-RPG layer actually adds player/owner value is UNMEASURED — no live users, no A/B, no engagement telemetry here. The value hypothesis is neither confirmed nor refuted; carried as JUDGMENT-ONLY.
- WHO builds phase 2 (the games-web↔mineverse seam ruling A/B/C, idea-engine #87) is OUT OF SCOPE — the manager's call. This pass settles WHETHER/WHAT the layer is worth, not ownership.
- Genre-comparable engagement lift (Shakes & Fidget-style retention) is NAMED as precedent but NOT measured — no numbers.

## The validity gate (all five, answered honestly)
1. COMPARABLE TO LIVE? The conformance check compares the ACTUAL committed contracts at pinned SHAs — exactly comparable for the conformance claim (no abstraction). The value axis has NO live comparison available (no users) — that gap is why value is JUDGMENT-ONLY, and it cannot flip the conformance-driven ruling (redirect), only the strength of the value hypothesis.
2. UNCORRUPTED? No sim, no seeds. The conformance analyzer is deterministic, self-checked over every asserted mismatch, and re-diffs frozen inputs — no cherry-picking (it reports the full field set, not a chosen subset). Value criteria are stated up front, scored once, not tuned to a conclusion.
3. ROBUST? The disjoint-gear-taxonomy and invented-stats findings survive any field-mapping attempt (the sets are disjoint — there is no lossy mapping, there is no mapping). The transport conflict is a contract-name identity check — binary. The redirect ruling is robust; only the value hypothesis's strength varies with taste.
4. REPRODUCIBLE? Committed frozen inputs (both contracts + stated-transport facts under runs/) + one command `python3 sims/verdict-007-games-web-concept-evidence-pass/analyze.py`, byte-identical output, exit 0.
5. LIMITS? This evidence shows the concept is non-conformant as-scoped and a redirect is required before phase-2 spend. It does NOT show the comic-RPG layer lacks value (unmeasured), does NOT pick a seam owner (#87), and does NOT measure engagement lift.

## EVIDENCE STRENGTH: moderate — gate PASS
The decision-driving conformance core is measured/reproducible (strong); the ultimate value question is JUDGMENT-ONLY (weak, hypothesis). The mix nets to moderate, and the label travels with the verdict.

## VERDICT & recommendation
- Verdict: needs-more-evidence (proposal ruling: redirect).
- Ruling: redirect — do NOT proceed-as-scoped; do NOT stop-at-phase-1.
- Target: menno420/product-forge (re-scope games-web phase-2). WHO builds the seam (A/B/C, idea-engine #87) = manager's call, OUT OF SCOPE.
- Named changes required before phase-2 spend:
  1. Re-contract `games-web.character-sheet` as a PROJECTION of `mining_snapshot.v1`: map the 9 real gear slots; derive stat lines from real fields (xp/level/depth/gear_wear/coins) or CUT the invented ones; derive rarity/power from real `gear_wear`/tier or DROP them (no fabricated numbers shipped as if real).
  2. Consume the committed-JSON `mining_snapshot.v1` feed (fm ORDER 012/013); RETIRE the competing `GET /v1/games-web/character-sheet` self-API proposal.
  3. Treat presentation-value as a phase-2 HYPOTHESIS to MEASURE (A/B or engagement telemetry vs the mineverse direct view) — that is the "more evidence" this verdict names; unreachable now.
- Why not stop-at-phase-1: the value hypothesis is plausible (distinct user intent: ops/utility vs engagement/retention; named genre precedent), and phase-1 artifacts are cheap-to-redirect (mock-first, ~170-line app.js, dependency-free inline SVG) — no evidence to kill it.
- Why not proceed-as-scoped: blocked by the measured conformance failure (disjoint taxonomy + invented stats + transport conflict).
- Best implementation found: keep phase-1's dependency-free inline-SVG paper-doll + rarity chips + a11y scaffolding as a reusable presentation SHELL; replace the FICTION contract with a real `mining_snapshot.v1` projection.
- Guardrails/telemetry: phase-2 must ship the A/B hook (comic layer vs direct view) so the value hypothesis is finally measured, not assumed.
- Codex review: one question posted on this PR's final head; reply: pending (OA-002 usage-capped).

## Analyzer output

The full stdout of `python3 sims/verdict-007-games-web-concept-evidence-pass/analyze.py`
(exit 0; every conformance assertion held against the real frozen files). Note: the two
games-web fixtures declare the Ore-Yield stat under the KEY `yield` (display label
"Ore Yield") — the finding above names it `ore_yield` for readability; the conformance
result is identical (`yield` has no source field in `mining_snapshot.v1` either).

```
==============================================================================
VERDICT 007 — games-web.character-sheet vs mining_snapshot.v1 — conformance
==============================================================================

inputs (frozen @ pinned SHAs, see runs/PROVENANCE.md):
  games-web  product-forge @ 43563dc
  mineverse  superbot-mineverse @ 2b1bd0b

[1] GEAR TAXONOMY DISJOINT
    games-web (8): ['chest', 'feet', 'hands', 'head', 'legs', 'main_hand', 'off_hand', 'trinket']
    mineverse (9): ['boots', 'charm', 'chestplate', 'helmet', 'leggings', 'light', 'shield', 'tool', 'weapon']
    intersection : ∅  -> DISJOINT

[2] STATS INVENTED (games-web stat key -> source in mining_snapshot.v1)
    strength     -> none (invented)
    endurance    -> none (invented)
    haste        -> none (invented)
    luck         -> none (invented)
    yield        -> none (invented)
    armor        -> none (invented)

[3] RARITY / POWER absent from real data
    games-web gear item fields : ['icon', 'name', 'power', 'rarity']
    mineverse gear item fields : ['gear_wear', 'name']
    rarity in mineverse gear   : False
    power  in mineverse gear   : False

[4] DROPPED FIELDS (mineverse carries -> games-web character-sheet omits)
    coins        present-in-mineverse=True  omitted-by-games-web=True
    energy       present-in-mineverse=True  omitted-by-games-web=True
    depth        present-in-mineverse=True  omitted-by-games-web=True
    position     present-in-mineverse=True  omitted-by-games-web=True
    vault        present-in-mineverse=True  omitted-by-games-web=True
    biome        present-in-mineverse=False omitted-by-games-web=True  (biome/leaderboard not a miner field)
    leaderboards present-in-mineverse=False omitted-by-games-web=True  (biome/leaderboard not a miner field)
    mineverse miner carries (asserted present): ['coins', 'energy', 'depth', 'position', 'vault', 'xp', 'skills', 'structures']

[5] TRANSPORT CONFLICT
    games-web self-API envelope : games-web.character-sheet
    decided feed envelope       : mining_snapshot.v1
    conflict                    : True

RULING: redirect — games-web.character-sheet is a hand-authored RPG fiction,
        not a projection of the decided mining_snapshot.v1 committed feed.
==============================================================================
SELF-CHECKS: 40 passed, 0 failed
```