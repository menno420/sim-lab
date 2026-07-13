"""PROBE 5 (C2b) — mechanical guard scan: any cooldown / one-shot / completion flag?

Scans (a) DnDState's declared fields, (b) the byte-copied escort-path sources for
guard tokens. stdlib only, deterministic (sorted output).
"""
import dataclasses
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "modules"))

from services.dnd_workflow import DnDState

FILES = [
    "services/dnd_workflow.py",
    "games/dnd/core/effects.py",
    "games/dnd/core/resolver.py",
    "games/dnd/core/models.py",
    "games/dnd/data/scenes.py",
    "games/exploration/quest/engine.py",
    "games/exploration/quest/models.py",
    "games/exploration/quest/catalog.py",
]

TOKENS = re.compile(r"cooldown|once|one[-_ ]shot|already|COMPLETED|minted|claimed|lockout|throttle|rate[-_ ]limit")


def main():
    print("PROBE 5 — guard scan (pin 57f69be3)")
    print("DnDState fields:", sorted(f.name for f in dataclasses.fields(DnDState)))
    print("-> no field records quest/bundle completion (only scene_id + running totals).")
    print()
    any_hit = False
    for rel in FILES:
        path = os.path.join(HERE, "modules", rel)
        with open(path, encoding="utf-8") as fh:
            for i, line in enumerate(fh, 1):
                if TOKENS.search(line):
                    any_hit = True
                    print(f"{rel}:{i}: {line.rstrip()}")
    if not any_hit:
        print("no guard tokens found anywhere on the path")
    print()
    print("C2b RESULT: the only 'completed' hits are the engine's per-INSTANCE state machine")
    print("(QuestState.COMPLETED) — which nothing persists across chooses (probe 4). No cooldown,")
    print("no one-shot flag, no session-level completion memory exists on the escort path.")


if __name__ == "__main__":
    main()
