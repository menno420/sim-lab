"""B0 VALIDITY — one traversal, packet-claimed double mint (VERDICT 044).

Drives the byte-copied pinned modules (menno420/superbot-games @ 57f69be34785af...)
through the audited seam services.dnd_workflow.choose, exactly the packet arc:
  waystation_road · advance_escort  ->  waystation_gate · circle_to_treeline
  ->  treeline_watch · signal_escort
Determinism: DnDState() defaults (seed=0, xp=0, player_id="player"); injected
fixed now + counter mutation-id factory. Zero decision-bearing RNG in the path
(DetRng is seeded by the resolver but the escort outcome is deterministic).
stdlib only.
"""
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "modules"))

from services.dnd_workflow import DnDState, InMemorySink, choose, surfaced_options
from games.dnd.data.scenes import get_scene
from games.exploration.quest.catalog import TIER_CAPS, GLOBAL_MAX
from games.exploration.quest.models import RewardTier

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)


def mid_factory():
    n = [0]
    def f():
        n[0] += 1
        return f"m{n[0]:04d}"
    return f


def fmt_bundle(b):
    if b is None:
        return "None"
    return f"(global_xp={b.global_xp}, game_xp={b.game_xp}, currency={b.currency}, capability={b.capability!r})"


def main():
    print("B0 — packet traversal on pinned modules @ 57f69be34785afb427d608b207e7369025166e94")
    print(f"TIER_CAPS[I]   = {fmt_bundle(TIER_CAPS[RewardTier.I])}")
    print(f"TIER_CAPS[II]  = {fmt_bundle(TIER_CAPS[RewardTier.II])}")
    print(f"TIER_CAPS[III] = {fmt_bundle(TIER_CAPS[RewardTier.III])}")
    print(f"GLOBAL_MAX     = {fmt_bundle(GLOBAL_MAX)}")
    print()

    state = DnDState()
    sink = InMemorySink()
    mid = mid_factory()
    steps = ["advance_escort", "circle_to_treeline", "signal_escort"]
    mints = []

    for i, option_id in enumerate(steps, 1):
        scene = get_scene(state.scene_id)
        allowed = [o.id for o in surfaced_options(scene, xp=state.xp)]
        print(f"STEP {i}: scene={state.scene_id!r} surfaced(width-capped)={allowed} choose={option_id!r}")
        assert option_id in allowed, f"option {option_id!r} not surfaced at width cap — traversal illegal"
        res = choose(state, option_id, sink=sink, now=FIXED_NOW, mutation_id_factory=mid)
        print(f"  clamped={res.resolution.clamped} effect={res.resolution.effect_id!r} "
              f"prev={res.prev_scene!r} next={res.next_scene!r} ended={res.ended}")
        print(f"  reward={fmt_bundle(res.reward)}")
        print(f"  audit: mutation_id={res.record.mutation_id} target={res.record.target!r} "
              f"prev_value={res.record.prev_value!r} new_value={res.record.new_value!r}")
        print(f"  running totals: g{state.global_xp}/x{state.game_xp}/c{state.currency}")
        if res.reward is not None:
            mints.append((i, res.prev_scene, res.reward))
        print()

    reward_rows = [r for r in sink.records if r.target.startswith("reward:")]
    print(f"BUNDLE COMPLETION EVENTS (mints): {len(mints)}")
    for i, scene_id, b in mints:
        print(f"  mint at step {i} (scene {scene_id!r}): {fmt_bundle(b)}")
    print(f"reward:* audit rows: {len(reward_rows)} -> {[r.target for r in reward_rows]}")
    print(f"final totals: g{state.global_xp}/x{state.game_xp}/c{state.currency}")

    tier1 = TIER_CAPS[RewardTier.I]
    expected = (2 * tier1.global_xp, 2 * tier1.game_xp, 2 * tier1.currency)
    actual = (state.global_xp, state.game_xp, state.currency)
    both_tier1 = all(
        b.global_xp == tier1.global_xp and b.game_xp == tier1.game_xp and b.currency == tier1.currency
        for _, _, b in mints
    )
    verdict = (len(mints) == 2 and both_tier1 and actual == expected and len(reward_rows) == 2)
    print()
    print(f"B0 CHECK: two mints? {len(mints) == 2} · each == TIER_CAPS[I]? {both_tier1} · "
          f"totals == 2x TIER_CAPS[I] {expected}? {actual == expected} · two reward:* rows? {len(reward_rows) == 2}")
    print(f"B0 RESULT: {'REPRODUCED — one traversal completes safe_passage TWICE and mints 2x' if verdict else 'NOT REPRODUCED'}")
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
