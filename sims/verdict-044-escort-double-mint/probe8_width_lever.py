"""PROBE 8 — the menu-width lever: is the double-mint gated by XP width anywhere?

Checks at which menu widths (xp floor 0 -> width 2, up to width 4) each leg of the
packet arc and the stay-loop is surfaced, i.e. whether ANY width setting closes the
exploit or whether it is live for a fresh 0-XP player. stdlib only, deterministic.
"""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules"))

from services.dnd_workflow import DnDState, InMemorySink, choose, surfaced_options
from games.dnd.data.scenes import SCENES
from games.exploration.quest.leverage import menu_width, BASE_MENU_WIDTH, MAX_MENU_WIDTH, XP_PER_EXTRA_OPTION

FIXED_NOW = datetime(2026, 7, 13, 12, 0, 0, tzinfo=timezone.utc)


def main():
    print("PROBE 8 — width lever (pin 57f69be3)")
    print(f"BASE_MENU_WIDTH={BASE_MENU_WIDTH} MAX_MENU_WIDTH={MAX_MENU_WIDTH} "
          f"XP_PER_EXTRA_OPTION={XP_PER_EXTRA_OPTION}")
    for xp in (0, 499, 500, 1000, 10**6):
        print(f"  menu_width(xp={xp}) = {menu_width(xp)}")
    print()
    needed = {"waystation_road": "advance_escort", "waystation_gate": "circle_to_treeline",
              "treeline_watch": "signal_escort"}
    for xp in (0, 500, 1000):
        ok = True
        detail = []
        for sid, opt in needed.items():
            ids = [o.id for o in surfaced_options(SCENES[sid], xp=xp)]
            detail.append(f"{sid}:{opt} {'ON' if opt in ids else 'OFF'}-menu")
            ok = ok and opt in ids
        print(f"xp={xp:5d} (width {menu_width(xp)}): packet arc fully legal? {ok} [{'; '.join(detail)}]")
    print()
    # And the arc positions: every escort option sits at index 0 or 1 of its scene tuple,
    # so the FLOOR width already surfaces the whole exploit.
    for sid, scene in SCENES.items():
        idx = {o.id: i for i, o in enumerate(scene.options)}
        esc = [f"{o.id}@{idx[o.id]}" for o in scene.options if o.effect_id == "escort_step"]
        print(f"{sid}: escort options at indices {esc if esc else 'none'} (width floor surfaces indices 0-1)")
    print()
    # Sanity: drive the full loop attack at xp=0 (already probe 2) and xp=1000 — identical mints.
    for xp in (0, 1000):
        state = DnDState(xp=xp)
        sink = InMemorySink()
        c = [0]
        def mid():
            c[0] += 1
            return f"m{c[0]:04d}"
        mints = 0
        for opt in ["advance_escort", "circle_to_treeline"] + ["signal_escort"] * 11:
            r = choose(state, opt, sink=sink, now=FIXED_NOW, mutation_id_factory=mid)
            mints += r.reward is not None
        print(f"xp={xp}: 13-choose loop attack mints {mints} (totals g{state.global_xp}/x{state.game_xp}/c{state.currency})")
    print()
    print("RESULT: the width lever never gates the exploit — every escort option sits inside the")
    print("width-2 FLOOR, so a fresh 0-XP player has the full double-mint arc AND the stay-loop")
    print("from the first session. XP widens options 2->4 but adds no new mint path and closes none.")


if __name__ == "__main__":
    main()
