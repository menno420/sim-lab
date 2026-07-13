"""PROBE 7 — fix surface: price the mint-at-most-once guard candidates.

Prototypes each candidate ON TOP of the byte-copied modules (in-memory wrappers;
the pinned files are never edited) and re-runs the packet arc + a 10-repeat loop
attack + the honest single-mint route under each. stdlib only, deterministic.

Candidates:
  (a) SEAM ONE-SHOT FLAG — one boolean on DnDState (e.g. `safe_passage_minted`),
      checked/set inside services/dnd_workflow.choose immediately after
      `resolution = resolve(...)` (i.e. between lines 243-254 at the pin, before
      `_fold_reward`): if resolution.reward is not None and the flag is set, drop
      the reward (fold nothing, audit the scene transition instead); else fold and
      set the flag. Surface: 1 dataclass field + ~4 lines in choose().
  (b) SCENE REWIRING — games/dnd/data/scenes.py: change ONE of the two escort
      wirings (treeline_watch.signal_escort effect_id -> "scout_narrate").
      Surface: 1 data-row edit. Closes the packet 2x AND the treeline stay-loop,
      but leaves waystation_road.advance_escort... (measured below).
  (c) ENGINE PERSISTENCE — store QuestInstance per (player, template) and re-drive
      offer/accept through the store so QuestStateError fires. Surface: a new
      store + threading state through pure effects (largest; measured analytically
      via probe 4, not prototyped here).
"""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules"))

import services.dnd_workflow as dw
from services.dnd_workflow import DnDState, InMemorySink
from games.dnd.data import scenes as scenes_mod
from games.dnd.core.models import MenuOption, Scene

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)

PACKET_ARC = ["advance_escort", "circle_to_treeline", "signal_escort"]
LOOP_ATTACK = PACKET_ARC + ["signal_escort"] * 10
HONEST_SINGLE = ["scout_ahead", "signal_escort"]
ROAD_RESTART = ["advance_escort"]  # per-session road mint under candidate (b)


def run(seq, choose_fn):
    state = DnDState()
    sink = InMemorySink()
    c = [0]
    def mid():
        c[0] += 1
        return f"m{c[0]:04d}"
    mints = 0
    for opt in seq:
        r = choose_fn(state, opt, sink=sink, now=FIXED_NOW, mutation_id_factory=mid)
        mints += r.reward is not None
    return mints, (state.global_xp, state.game_xp, state.currency)


# --- candidate (a): seam-level one-shot flag (wrapper prototype) -------------
def make_guarded_choose():
    minted_flags = {}  # id(state) -> bool  (prototype of a DnDState field)

    def guarded_choose(state, option_id, **kw):
        sink = kw["sink"]
        # replicate choose but drop a second bundle mint: prototype by pre-checking
        # via a dry resolve on a COPY, then delegating / suppressing the fold.
        import copy
        probe_state = copy.deepcopy(state)
        r = dw.choose(probe_state, option_id, sink=InMemorySink(),
                      now=kw.get("now"), mutation_id_factory=kw.get("mutation_id_factory"))
        if r.reward is not None and minted_flags.get(id(state), False):
            # guard fires: apply the same transition but fold no reward
            state.scene_id = probe_state.scene_id
            rec_kw = dict(kw)
            res = dw.DnDResult(ok=True, resolution=r.resolution, prev_scene=r.prev_scene,
                               next_scene=r.next_scene, reward=None, ended=r.ended,
                               message=r.message, record=r.record)
            sink.record(r.record)
            return res
        out = dw.choose(state, option_id, **kw)
        if out.reward is not None:
            minted_flags[id(state)] = True
        return out

    return guarded_choose


# --- candidate (b): scene rewiring (in-memory data edit, restored after) -----
def rewired_scenes():
    tw = scenes_mod.TREELINE_WATCH
    new_opts = tuple(
        MenuOption(id=o.id, text_key=o.text_key,
                   effect_id=("scout_narrate" if o.id == "signal_escort" else o.effect_id),
                   next_scene_id=o.next_scene_id)
        for o in tw.options
    )
    return Scene(scene_id=tw.scene_id, context_key=tw.context_key,
                 options=new_opts, default_option_id=tw.default_option_id)


def main():
    print("PROBE 7 — fix-surface pricing (pin 57f69be3; pinned files untouched — in-memory prototypes)")
    print()
    print("BASELINE (unguarded seam):")
    for name, seq in (("packet arc", PACKET_ARC), ("loop attack (arc + 10x signal)", LOOP_ATTACK),
                      ("honest single (scout -> signal)", HONEST_SINGLE)):
        m, tot = run(seq, dw.choose)
        print(f"  {name}: {m} mints, totals {tot}")
    print()

    print("CANDIDATE (a) seam one-shot flag — DnDState field + guard in choose() after resolve(),")
    print("  before _fold_reward (services/dnd_workflow.py: guard belongs between the resolve() call")
    print("  at line 243 and _fold_reward(state, resolution.reward) at line 254):")
    for name, seq in (("packet arc", PACKET_ARC), ("loop attack", LOOP_ATTACK),
                      ("honest single", HONEST_SINGLE)):
        m, tot = run(seq, make_guarded_choose())
        print(f"  {name}: {m} mints, totals {tot}")
    print("  surface: 1 field on DnDState + ~4 lines in choose(); audit still records every choose.")
    print()

    print("CANDIDATE (b) scene rewiring — treeline_watch.signal_escort effect_id -> scout_narrate")
    print("  (games/dnd/data/scenes.py, the signal_escort MenuOption):")
    original = scenes_mod.SCENES["treeline_watch"]
    scenes_mod.SCENES["treeline_watch"] = rewired_scenes()
    try:
        for name, seq in (("packet arc", PACKET_ARC), ("loop attack", LOOP_ATTACK),
                          ("honest single", HONEST_SINGLE), ("road-only restart", ROAD_RESTART)):
            m, tot = run(seq, dw.choose)
            print(f"  {name}: {m} mints, totals {tot}")
    finally:
        scenes_mod.SCENES["treeline_watch"] = original
    print("  surface: 1 data-row edit; NOTE the honest scout route now mints ZERO (it deletes the")
    print("  escort payoff for players who scouted first) and per-session road re-mints survive if")
    print("  sessions are free to recreate — the guard moved the hole, candidate (a) closes it.")
    print()
    print("CANDIDATE (c) engine persistence: guard already exists (QuestStateError, probe 4) but")
    print("needs an instance store threaded through the pure effect layer — largest surface,")
    print("architectural (the effect signature (seed, player_id) has no store handle).")
    print()
    print("RECOMMENDED FIX: candidate (a) — mint-at-most-once per DnDState session via a one-shot")
    print("flag checked in services/dnd_workflow.choose between resolve() and _fold_reward().")


if __name__ == "__main__":
    main()
