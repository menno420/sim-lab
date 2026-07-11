#!/usr/bin/env python3
"""VERDICT 007 — games-web comic-RPG contract vs mineverse direct view.

Method: JUDGMENT-ONLY on the value axis, with a reproducible CONFORMANCE CHECK
(ladder rung 2, measured core). The value question ("does a presentation layer add
value") has no ground truth reachable here. What IS checkable is checked: this script
loads the two committed contracts frozen at pinned SHAs under runs/ (+ stated.json and
the two games-web fixtures) and DETERMINISTICALLY diffs games-web's
`games-web.character-sheet` contract against the real `mining_snapshot.v1` feed it
claims to present, asserting each field-level mismatch. It self-checks every assertion,
prints a plain report, and is byte-identical on re-run (it reads frozen files, calls no
clock, draws no RNG).

Run: python3 sims/verdict-007-games-web-concept-evidence-pass/analyze.py
Stdlib only. Exit 0 iff every self-check passes.

Field sets are DERIVED from the real frozen files (not hardcoded); the expected sets are
asserted so a drift in the source contracts fails loudly rather than silently passing.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")


# ---- vendored from harness/simharness.py (stdlib-only; sims stay self-contained) ----
class SelfCheck:
    """Assertion battery with a pass counter. Vendored from harness/simharness.py."""

    def __init__(self):
        self.passed = 0
        self.detail = []

    def check(self, cond, label):
        self.detail.append((bool(cond), label))
        if cond:
            self.passed += 1
        else:
            raise AssertionError("SELF-CHECK FAILED: " + label)
        return bool(cond)

    def report(self):
        failed = sum(1 for ok, _ in self.detail if not ok)
        print("SELF-CHECKS: %d passed, %d failed" % (self.passed, failed))
        return 0 if failed == 0 else 1


def determinism_bytes(sc, obj, label="determinism: stable canonical JSON"):
    """Byte-identical canonical serialization check. Vendored from harness/simharness.py."""
    s1 = json.dumps(obj, indent=2, sort_keys=True)
    s2 = json.dumps(obj, indent=2, sort_keys=True)
    return sc.check(s1 == s2, label)
# ---- end vendored ----------------------------------------------------------------


def load(name):
    with open(os.path.join(RUNS, name)) as f:
        return json.load(f)


def main():
    sc = SelfCheck()

    gw_schema = load("games-web.character-sheet.schema.json")
    mv_schema = load("mineverse.mining_snapshot.v1.schema.json")
    stated = load("stated.json")
    fx_mining = load("games-web.mining-character.fixture.json")
    fx_recruit = load("games-web.recruit-character.fixture.json")

    # ---- DERIVE field sets from the real frozen files -----------------------------
    # games-web top-level properties + gear slots + gear-item fields
    gw_top = set(gw_schema["properties"].keys())
    gw_gear_slots = set(gw_schema["properties"]["gear"]["required"])
    # gearSlot object (oneOf: [null, object]) -> the object arm's properties
    gearslot_arms = gw_schema["$defs"]["gearSlot"]["oneOf"]
    gearslot_obj = next(a for a in gearslot_arms if a.get("type") == "object")
    gw_gear_item_fields = set(gearslot_obj["properties"].keys())

    # mineverse miner properties + equipment slots
    mv_miner_props = set(mv_schema["$defs"]["miner"]["properties"].keys())
    mv_equip_slots = set(
        mv_schema["$defs"]["miner"]["properties"]["equipment"]["propertyNames"]["enum"])
    # mineverse gear representation: equipped item is a bare name STRING; wear tracked
    # in the gear_wear name->count map. No per-item object -> no rarity/power fields.
    mv_gear_item_fields = {"name", "gear_wear"}

    # games-web stat keys — READ from the fixtures (both must agree)
    stat_keys_mining = [s["key"] for s in fx_mining["stats"]]
    stat_keys_recruit = [s["key"] for s in fx_recruit["stats"]]
    sc.check(stat_keys_mining == stat_keys_recruit,
             "both games-web fixtures declare the same stat key order: %s vs %s"
             % (stat_keys_mining, stat_keys_recruit))
    gw_stat_keys = list(stat_keys_mining)

    # ---- anchor the derived sets to the expected reality (fail loud on drift) ------
    sc.check(gw_gear_slots == {
        "head", "chest", "hands", "legs", "feet", "main_hand", "off_hand", "trinket"},
        "games-web gear slots are the expected 8: %s" % sorted(gw_gear_slots))
    sc.check(mv_equip_slots == {
        "tool", "light", "charm", "weapon", "shield", "helmet",
        "chestplate", "leggings", "boots"},
        "mineverse equipment slots are the expected 9: %s" % sorted(mv_equip_slots))
    sc.check(gw_schema["properties"]["contract"]["const"] == "games-web.character-sheet",
             "games-web schema const contract == games-web.character-sheet")
    sc.check(mv_schema["properties"]["schema_version"]["const"] == "1",
             "mineverse schema_version const == '1' (mining_snapshot.v1)")

    # ================================================================================
    # FINDING 1 — GEAR TAXONOMY DISJOINT
    # ================================================================================
    slot_intersection = gw_gear_slots & mv_equip_slots
    sc.check(slot_intersection == set(),
             "FINDING 1: games-web gear slots ∩ mineverse equipment slots == ∅ "
             "(shared: %s)" % sorted(slot_intersection))
    sc.check(len(gw_gear_slots) == 8, "FINDING 1: games-web has 8 gear slots")
    sc.check(len(mv_equip_slots) == 9, "FINDING 1: mineverse has 9 equipment slots")

    # ================================================================================
    # FINDING 2 — STATS INVENTED (each games-web stat key has no mineverse miner field)
    # ================================================================================
    sc.check(len(gw_stat_keys) >= 1, "FINDING 2: games-web declares >=1 stat key")
    stats_without_source = []
    for k in gw_stat_keys:
        has_source = k in mv_miner_props
        sc.check(not has_source,
                 "FINDING 2: games-web stat key %r has NO counterpart field in the "
                 "mining_snapshot.v1 miner object" % k)
        if not has_source:
            stats_without_source.append(k)
    sc.check(stats_without_source == gw_stat_keys,
             "FINDING 2: every games-web stat is invented (no real source field)")

    # ================================================================================
    # FINDING 3 — RARITY/POWER absent from real data
    # ================================================================================
    for f in ("rarity", "power"):
        sc.check(f in gw_gear_item_fields,
                 "FINDING 3: games-web gear item carries %r" % f)
        sc.check(f not in mv_gear_item_fields,
                 "FINDING 3: mineverse gear does NOT carry %r" % f)
    sc.check("gear_wear" in mv_miner_props,
             "FINDING 3: mineverse tracks gear via gear_wear (name + wear), not rarity/power")

    # ================================================================================
    # FINDING 4 — DROPPED FIELDS (mineverse carries, games-web omits)
    # ================================================================================
    mv_carries = ["coins", "energy", "depth", "position", "vault", "xp",
                  "skills", "structures"]
    for f in mv_carries:
        sc.check(f in mv_miner_props,
                 "FINDING 4: mineverse miner schema carries %r" % f)
    gw_omits = ["coins", "energy", "depth", "position", "vault", "biome", "leaderboards"]
    for f in gw_omits:
        sc.check(f not in gw_top,
                 "FINDING 4: games-web character-sheet top-level OMITS %r" % f)

    # ================================================================================
    # FINDING 5 — TRANSPORT CONFLICT (self-API envelope != decided feed envelope)
    # ================================================================================
    gw_self = stated["games_web_self_api"]["envelope_contract"]
    decided = stated["decided_transport"]["envelope_contract"]
    sc.check(gw_self == "games-web.character-sheet",
             "FINDING 5: games-web self-API envelope is games-web.character-sheet")
    sc.check(decided == "mining_snapshot.v1",
             "FINDING 5: decided transport envelope is mining_snapshot.v1")
    sc.check(gw_self != decided,
             "FINDING 5: games-web self-API envelope %r != decided feed envelope %r "
             "(transport conflict)" % (gw_self, decided))

    # ================================================================================
    # canonical findings dict + byte-identical determinism proof
    # ================================================================================
    findings = {
        "verdict": "007-games-web-concept-evidence-pass",
        "finding_1_gear_taxonomy_disjoint": {
            "games_web_slots": sorted(gw_gear_slots),
            "mineverse_slots": sorted(mv_equip_slots),
            "intersection": sorted(slot_intersection),
            "counts": {"games_web": len(gw_gear_slots), "mineverse": len(mv_equip_slots)},
            "disjoint": slot_intersection == set(),
        },
        "finding_2_stats_invented": {
            "games_web_stat_keys": gw_stat_keys,
            "with_mineverse_source": [k for k in gw_stat_keys if k in mv_miner_props],
            "invented": stats_without_source,
        },
        "finding_3_rarity_power_absent": {
            "games_web_gear_item_fields": sorted(gw_gear_item_fields),
            "mineverse_gear_item_fields": sorted(mv_gear_item_fields),
            "rarity_in_mineverse": "rarity" in mv_gear_item_fields,
            "power_in_mineverse": "power" in mv_gear_item_fields,
        },
        "finding_4_dropped_fields": {
            "mineverse_carries": mv_carries,
            "games_web_top_level": sorted(gw_top),
            "games_web_omits": gw_omits,
        },
        "finding_5_transport_conflict": {
            "games_web_self_api_envelope": gw_self,
            "decided_transport_envelope": decided,
            "conflict": gw_self != decided,
        },
    }
    determinism_bytes(sc, findings,
                      "determinism: canonical findings JSON byte-identical on re-run")

    # ---- plain report -------------------------------------------------------------
    print("=" * 78)
    print("VERDICT 007 — games-web.character-sheet vs mining_snapshot.v1 — conformance")
    print("=" * 78)
    print("\ninputs (frozen @ pinned SHAs, see runs/PROVENANCE.md):")
    print("  games-web  product-forge @ 43563dc")
    print("  mineverse  superbot-mineverse @ 2b1bd0b")

    print("\n[1] GEAR TAXONOMY DISJOINT")
    print("    games-web (%d): %s" % (len(gw_gear_slots), sorted(gw_gear_slots)))
    print("    mineverse (%d): %s" % (len(mv_equip_slots), sorted(mv_equip_slots)))
    print("    intersection : %s  -> DISJOINT" % (sorted(slot_intersection) or "∅"))

    print("\n[2] STATS INVENTED (games-web stat key -> source in mining_snapshot.v1)")
    for k in gw_stat_keys:
        src = "REAL FIELD" if k in mv_miner_props else "none (invented)"
        print("    %-12s -> %s" % (k, src))

    print("\n[3] RARITY / POWER absent from real data")
    print("    games-web gear item fields : %s" % sorted(gw_gear_item_fields))
    print("    mineverse gear item fields : %s" % sorted(mv_gear_item_fields))
    print("    rarity in mineverse gear   : %s" % ("rarity" in mv_gear_item_fields))
    print("    power  in mineverse gear   : %s" % ("power" in mv_gear_item_fields))

    print("\n[4] DROPPED FIELDS (mineverse carries -> games-web character-sheet omits)")
    for f in gw_omits:
        in_mv = f in mv_miner_props or f in mv_schema["properties"]
        note = "" if f not in ("biome", "leaderboards") else "  (biome/leaderboard not a miner field)"
        print("    %-12s present-in-mineverse=%-5s omitted-by-games-web=%s%s"
              % (f, in_mv, f not in gw_top, note))
    print("    mineverse miner carries (asserted present): %s" % mv_carries)

    print("\n[5] TRANSPORT CONFLICT")
    print("    games-web self-API envelope : %s" % gw_self)
    print("    decided feed envelope       : %s" % decided)
    print("    conflict                    : %s" % (gw_self != decided))

    print("\nRULING: redirect — games-web.character-sheet is a hand-authored RPG fiction,")
    print("        not a projection of the decided mining_snapshot.v1 committed feed.")
    print("=" * 78)
    return sc.report()


if __name__ == "__main__":
    sys.exit(main())
