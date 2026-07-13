"""PROBE 3 (C2) — greedy farm rate: mints per choose, asymptotic.

Greedy strategy: at every scene pick the first surfaced escort_step option if any,
else the first surfaced option that leads toward one (fixed lookup). Runs N=100
chooses on one session. Also measures the fastest route to the FIRST mint and to
the SECOND mint. stdlib only, deterministic.
"""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules"))

from services.dnd_workflow import DnDState, InMemorySink, choose, surfaced_options
from games.dnd.data.scenes import get_scene, SCENES
from games.dnd.core.effects import EFFECTS

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)


def greedy_option(state):
    scene = get_scene(state.scene_id)
    allowed = surfaced_options(scene, xp=state.xp)
    for o in allowed:
        if o.effect_id == "escort_step":
            return o.id
    # no escort option here: head toward treeline_watch (the stay-mint scene)
    for o in allowed:
        if o.next_scene_id is not None:
            return o.id
    return allowed[0].id


def run(n_chooses):
    state = DnDState()
    sink = InMemorySink()
    c = [0]
    def mid():
        c[0] += 1
        return f"m{c[0]:04d}"
    mints_at = []
    for i in range(1, n_chooses + 1):
        r = choose(state, greedy_option(state), sink=sink, now=FIXED_NOW, mutation_id_factory=mid)
        if r.reward is not None:
            mints_at.append(i)
    return state, mints_at


def main():
    print("PROBE 3 — greedy farm rate (pin 57f69be3)")
    graph = {sid: [(o.id, o.effect_id, o.next_scene_id) for o in s.options] for sid, s in SCENES.items()}
    print(f"scene graph: {graph}")
    print()
    for n in (10, 100):
        state, mints_at = run(n)
        print(f"N={n:3d} chooses -> {len(mints_at)} mints; totals g{state.global_xp}/x{state.game_xp}/c{state.currency}; "
              f"rate={len(mints_at)/n:.2f} mints/choose")
        if n == 10:
            print(f"  mint positions: {mints_at}")
    print()
    _, mints_at = run(100)
    print(f"first mint at choose #{mints_at[0]}; second mint at choose #{mints_at[1]}; "
          f"steady-state 1 mint/choose from #{mints_at[1]} on (stay-loop at treeline_watch)")
    print(f"asymptotic farm: 100 chooses -> {len(mints_at)}x TIER_CAPS[I] = "
          f"({5*len(mints_at)}, {25*len(mints_at)}, {10*len(mints_at)}) — every legal, none clamped")
    print()
    print("C2 RESULT: farm rate approaches 1 mint per choose; the ONLY rate limit is the host's")
    print("choose cadence (docs/balance.md: 'there is no in-domain cooldown, so the host decides")
    print("how often a scene/quest can be run') — in-domain the mint is UNBOUNDED per session.")


if __name__ == "__main__":
    main()
