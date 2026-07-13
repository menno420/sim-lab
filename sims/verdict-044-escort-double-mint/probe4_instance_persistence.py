"""PROBE 4 — root cause: each _escort_step runs a FRESH offer->accept->apply->grant cycle.

Shows (a) two escort_step applications at the same scene derive the SAME deterministic
quest instance_id yet both complete and both mint (nothing persists the COMPLETED
state); (b) the engine ITSELF forbids re-completion when an instance IS persisted
(accept from COMPLETED raises QuestStateError) — the guard exists one layer down but
no layer stores the instance. stdlib only, deterministic.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules"))

from games.exploration.quest import engine
from games.exploration.quest.models import QuestState, QuestStateError, RewardTier
from games.exploration.quest.predicates import GameEvent
from games.dnd.core.effects import EFFECTS
from games.dnd.core.resolver import _STORY_SALT
from games.exploration.quest.rng import derive_seed


def main():
    print("PROBE 4 — quest-instance persistence (pin 57f69be3)")
    # The exact seed the resolver hands the effect at treeline_watch (seed=0 session):
    scene_seed = derive_seed(_STORY_SALT, 0, "treeline_watch")
    print(f"resolver-derived scene seed for treeline_watch (session seed 0): {scene_seed}")

    o1 = EFFECTS["escort_step"].apply(seed=scene_seed, player_id="player")
    o2 = EFFECTS["escort_step"].apply(seed=scene_seed, player_id="player")
    print(f"escort_step call #1: reward={(o1.reward.global_xp, o1.reward.game_xp, o1.reward.currency)}")
    print(f"escort_step call #2: reward={(o2.reward.global_xp, o2.reward.game_xp, o2.reward.currency)}")
    print("-> the SAME (seed, player) mints TWICE: the effect is stateless by construction.")
    print()

    # The deterministic instance identity — both cycles build the SAME instance id:
    inst_a = engine.offer("safe_passage", "player", RewardTier.I, scene_seed)
    inst_b = engine.offer("safe_passage", "player", RewardTier.I, scene_seed)
    print(f"offer #1 instance_id: {inst_a.instance_id} (state={inst_a.state.value})")
    print(f"offer #2 instance_id: {inst_b.instance_id} (state={inst_b.state.value})")
    print(f"identical ids? {inst_a.instance_id == inst_b.instance_id} — the engine names ONE logical"
          " quest, but no store remembers it was completed.")
    print()

    # The engine's own state machine DOES forbid re-running a persisted instance:
    inst = engine.accept(inst_a)
    inst = engine.apply_event(inst, GameEvent(type="npc_reached", payload={"npc": "traveler", "dest": "waystation"}))
    print(f"completed persisted instance: state={inst.state.value}")
    try:
        engine.accept(inst)
        print("accept(COMPLETED) -> did NOT raise (unexpected)")
    except QuestStateError as e:
        print(f"accept(COMPLETED) raises QuestStateError: {e!r}")
    r2 = engine.apply_event(inst, GameEvent(type="npc_reached", payload={"npc": "traveler", "dest": "waystation"}))
    print(f"apply_event on COMPLETED instance: state stays {r2.state.value}, step unchanged? {r2.step == inst.step} "
          f"(returned unchanged: {r2 == inst})")
    try:
        engine.grant_rewards(inst)
        print("grant_rewards on COMPLETED works (idempotent read) — the mint guard must live where"
              " the instance is (not) stored.")
    except QuestStateError as e:
        print(f"grant_rewards raised: {e!r}")
    print()
    print("ROOT CAUSE: games/dnd/core/effects.py _escort_step lines ~86-97 construct a fresh")
    print("instance per call (offer->accept->apply_event->grant_rewards) and discard it; no layer")
    print("(effect, resolver, seam DnDState) persists QuestInstance, so the engine's own")
    print("re-completion guard (QuestStateError) can never fire.")


if __name__ == "__main__":
    main()
