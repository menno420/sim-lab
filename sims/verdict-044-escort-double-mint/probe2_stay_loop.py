"""PROBE 2 (C2a) — the stay-loop: after the packet arc, is signal_escort re-choosable?

treeline_watch's signal_escort has next_scene_id=None; the seam documents None as
"the beat concludes / stays, so scene_id is left unchanged". Nothing resets or ends
the session object. This probe repeats signal_escort 10 more times on the SAME
DnDState and counts mints. stdlib only, deterministic (fixed now, counter ids).
"""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules"))

from services.dnd_workflow import DnDState, InMemorySink, choose, surfaced_options
from games.dnd.data.scenes import get_scene

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)


def main():
    state = DnDState()
    sink = InMemorySink()
    n = [0]
    def mid():
        n[0] += 1
        return f"m{n[0]:04d}"

    print("PROBE 2 — stay-loop farm after the packet arc (pin 57f69be3)")
    # The packet arc first (mint #1, #2):
    for opt in ("advance_escort", "circle_to_treeline", "signal_escort"):
        r = choose(state, opt, sink=sink, now=FIXED_NOW, mutation_id_factory=mid)
    print(f"after packet arc: scene_id={state.scene_id!r} totals=g{state.global_xp}/x{state.game_xp}/c{state.currency} "
          f"(ended flag on last result: {r.ended})")
    print()

    extra_mints = 0
    for i in range(1, 11):
        scene = get_scene(state.scene_id)
        allowed = [o.id for o in surfaced_options(scene, xp=state.xp)]
        legal = "signal_escort" in allowed
        r = choose(state, "signal_escort", sink=sink, now=FIXED_NOW, mutation_id_factory=mid)
        minted = r.reward is not None
        extra_mints += bool(minted)
        print(f"repeat {i:2d}: scene={r.prev_scene!r} on-menu={legal} clamped={r.resolution.clamped} "
              f"minted={minted} totals=g{state.global_xp}/x{state.game_xp}/c{state.currency}")

    reward_rows = [rec for rec in sink.records if rec.target.startswith("reward:")]
    print()
    print(f"extra mints in 10 repeats: {extra_mints} (all legal, none clamped)"
          if extra_mints == 10 else f"extra mints in 10 repeats: {extra_mints}")
    print(f"total reward:* audit rows: {len(reward_rows)}; final totals g{state.global_xp}/x{state.game_xp}/c{state.currency}")
    expected = (5 * 12, 25 * 12, 10 * 12)
    actual = (state.global_xp, state.game_xp, state.currency)
    print(f"totals == 12x TIER_CAPS[I] {expected}? {actual == expected}")
    print()
    print(f"C2a RESULT: {'UNBOUNDED — signal_escort re-mints every repeat; no cooldown, no one-shot flag, no session end' if extra_mints == 10 else 'BOUNDED'}")


if __name__ == "__main__":
    main()
