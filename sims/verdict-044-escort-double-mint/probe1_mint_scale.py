"""PROBE 1 (C1) — mint size per completion; 2x total vs the catalog's reward scale.

Pure reads of the pinned catalog (games/exploration/quest/catalog.py @ 57f69be3).
stdlib only, deterministic.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules"))

from games.exploration.quest.catalog import TIER_CAPS, GLOBAL_MAX, TEMPLATES
from games.exploration.quest.models import RewardTier


def tup(b):
    return (b.global_xp, b.game_xp, b.currency)


def main():
    t1, t2, t3 = tup(TIER_CAPS[RewardTier.I]), tup(TIER_CAPS[RewardTier.II]), tup(TIER_CAPS[RewardTier.III])
    gm = tup(GLOBAL_MAX)
    double = tuple(2 * x for x in t1)
    print("PROBE 1 — mint scale (all values read live from the pinned catalog)")
    print(f"mint per safe_passage completion (TIER_CAPS[I]): {t1}  (global_xp, game_xp, currency)")
    print(f"packet-arc total (2x TIER_CAPS[I]):              {double}")
    print(f"TIER_CAPS[II]:                                   {t2}")
    print(f"TIER_CAPS[III]:                                  {t3}")
    print(f"GLOBAL_MAX:                                      {gm}")
    print()
    le_t2 = all(d <= c for d, c in zip(double, t2))
    gt_t2 = [name for name, d, c in zip(("global_xp", "game_xp", "currency"), double, t2) if d > c]
    le_gm = all(d <= c for d, c in zip(double, gm))
    print(f"2x tier-I <= TIER_CAPS[II] component-wise? {le_t2}"
          + (f" (exceeds on: {gt_t2})" if gt_t2 else ""))
    print(f"2x tier-I <= GLOBAL_MAX component-wise?   {le_gm}")
    for name, d, c in zip(("global_xp", "game_xp", "currency"), double, t2):
        print(f"  {name}: 2x tier-I = {d} vs tier-II cap {c} ({d/c:.3f} of tier II)")
    print()
    print(f"safe_passage template: kind={TEMPLATES['safe_passage'].kind.value!r}, "
          f"objectives={len(TEMPLATES['safe_passage'].objectives)} "
          f"(single objective, required={TEMPLATES['safe_passage'].objectives[0].required})")
    print()
    print(f"C1 RESULT: {'WITHIN-SCALE' if le_t2 and le_gm else 'SCALE-BREAKING'} "
          f"per the pre-registered threshold (2x tier-I {'<=' if le_t2 else '>'} tier-II component-wise)")


if __name__ == "__main__":
    main()
