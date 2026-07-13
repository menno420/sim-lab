#!/usr/bin/env python3
"""VERDICT 042 — mining-economy-tuning (idea-engine ORDER 006 SIM-REQUEST 4).

Drives the byte-copied superbot-games mining core (engine/games/mining/core/*,
pinned @ 57f69be34785afb427d608b207e7369025166e94, sha256 MANIFEST re-verified
before import) to answer:

  (a) descend-gate shape — time/actions for a fresh player (iron pickaxe only)
      to first descend under the current light gate vs alternative gate arms;
  (b) faucet/sink gap — exact coins/dig (and materials/dig) per registered
      profile vs the sink ladder iron sword 60 / Forge I 3,000 / Forge II 8,000.

Method: rung 1 NUMERIC SIMULATION. Every decision-bearing number is EXACT
Fraction arithmetic over engine constants read live from the copied modules
(zero decision-bearing RNG). Seeded engine-driven Monte Carlo legs (seeds
20260792-20260797, strictly above the fleet high-water 20260791) validate the
exact numbers and the GRID-1 abstraction; they are self-checks, not rulings.

Pre-registration: fixtures.json (committed before this runner existed).
One command:  python3 sims/verdict-042-mining-economy/mining_economy_sim.py
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------- #
# 0. Manifest re-verification BEFORE import (the V038 discipline).
# --------------------------------------------------------------------------- #
CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))


with open(os.path.join(HERE, "engine", "MANIFEST.json"), encoding="utf-8") as fh:
    MANIFEST = json.load(fh)

for rel, want in sorted(MANIFEST["files"].items()):
    p = os.path.join(HERE, "engine", rel)
    got = hashlib.sha256(open(p, "rb").read()).hexdigest()
    check(f"manifest:{rel}", got == want, f"{got} vs {want}")

sys.path.insert(0, os.path.join(HERE, "engine"))

from games.mining.core import (  # noqa: E402
    energy,
    equipment,
    grid,
    items,
    market,
    recipes,
    rewards,
    structures,
    world,
)

with open(os.path.join(HERE, "fixtures.json"), encoding="utf-8") as fh:
    FIX = json.load(fh)

R: dict = {"pin": MANIFEST["pinned_sha"], "intake": "simreq-006", "verdict": 42}

# --------------------------------------------------------------------------- #
# 1. B0 VALIDITY GATE — reproduce every packet-pinned constant exactly.
# --------------------------------------------------------------------------- #
fresh = equipment.compute_stats({"tool": "iron pickaxe"})
check("B0:fresh depth_access==0", fresh.depth_access == 0)
check("B0:fresh max_accessible_depth==0", world.max_accessible_depth(fresh) == 0)
check("B0:fresh can_descend(0)==False", world.can_descend(0, fresh) is False)

check("B0:torch item depth_access==1", equipment.item_stats("torch").depth_access == 1)
with_torch = equipment.compute_stats({"tool": "iron pickaxe", "light": "torch"})
check("B0:torch max_accessible_depth==1", world.max_accessible_depth(with_torch) == 1)

check("B0:lantern item depth_access==2", equipment.item_stats("lantern").depth_access == 2)
with_lantern = equipment.compute_stats({"tool": "iron pickaxe", "light": "lantern"})
check("B0:lantern max_accessible_depth==2", world.max_accessible_depth(with_lantern) == 2)

check("B0:BASE_ROLL_MAX==2", rewards.BASE_ROLL_MAX == 2)
_amts = set()
_rng = random.Random(20260792)
for _ in range(1000):
    _, a = rewards.roll_mine_loot(has_pickaxe=False, depth=0, multiplier=1.0, rng=_rng)
    _amts.add(a)
check("B0:base roll support {1,2} @ mult 1.0", _amts == {1, 2}, str(sorted(_amts)))

for ore, want_v in FIX["b0_validity_anchors"]["faucet"]["sell_values"].items():
    check(f"B0:sell_price({ore})=={want_v}", market.sell_price(ore) == want_v,
          str(market.sell_price(ore)))

check("B0:GEAR_SHOP['iron sword']==60", market.GEAR_SHOP["iron sword"] == 60)

ladder = structures._FORGE_BUILD_LADDER
check("B0:Forge I == 3000 + {iron:25, stone:15}",
      ladder[0].coins == 3000 and ladder[0].materials == {"iron": 25, "stone": 15},
      repr(ladder[0]))
check("B0:Forge II == 8000 + {gold:20, iron:10}",
      ladder[1].coins == 8000 and ladder[1].materials == {"gold": 20, "iron": 10},
      repr(ladder[1]))

# Auxiliary engine pins the probes read (drift made visible).
check("aux:torch shop 10", market.GEAR_SHOP["torch"] == 10)
check("aux:lantern shop 40", market.GEAR_SHOP["lantern"] == 40)
check("aux:ration shop 20 / +25 energy",
      market.GEAR_SHOP["ration"] == 20 and energy.RESTORE_VALUES["ration"] == 25)
check("aux:energy drink shop 40 / +50 energy",
      market.GEAR_SHOP["energy drink"] == 40 and energy.RESTORE_VALUES["energy drink"] == 50)
check("aux:torch recipe {wood:2}", recipes.DEFAULT_RECIPES["torch"] == {"wood": 2})
check("aux:energy 60/1/10", (energy.MAX_ENERGY, energy.DIG_COST, energy.REGEN_SECONDS) == (60, 1, 10))
check("aux:TOOL_POWER_GAIN 0.0625", rewards.TOOL_POWER_GAIN == 0.0625)
check("aux:iron pickaxe power 4", equipment.item_stats("iron pickaxe").mining_power == 4)
_fw = dict((f.name, w) for f, w in grid._FEATURE_WEIGHTS)
check("aux:feature weights 70/10/18/2",
      _fw == {"NORMAL": 70.0, "RICH": 10.0, "BARREN": 18.0, "TREASURE": 2.0}, str(_fw))
_rich = {f.name: v for f, v in grid._RICHNESS.items()}
check("aux:richness 1/2/0.5/2",
      _rich == {"NORMAL": 1.0, "RICH": 2.0, "BARREN": 0.5, "TREASURE": 2.0}, str(_rich))

B0_OK = all(ok for name, ok, _ in CHECKS)
R["b0"] = {"pass": B0_OK, "anchors": len(CHECKS)}

# --------------------------------------------------------------------------- #
# 2. Exact per-dig model (Fractions; engine arithmetic reproduced by
#    ENUMERATING the engine's own float ops on the finite support).
# --------------------------------------------------------------------------- #
ORE_VALUES = {o: market.sell_price(o) for o in rewards.ORE_WEIGHTS}
FEATS = [(f, Fraction(w).limit_denominator() / 100) for f, w in
         [(f, Fraction(w)) for f, w in grid._FEATURE_WEIGHTS]]
# grid._FEATURE_WEIGHTS floats (70.0 etc.) are exact; normalize over 100.
FEATS = [(f, Fraction(w) / 100) for f, w in grid._FEATURE_WEIGHTS]


def depth_weights(d: int) -> dict[str, Fraction]:
    w = rewards.ore_weights_for_depth(d)
    tot = Fraction(0)
    out = {}
    for k, v in w.items():
        fv = Fraction(v)  # 0.5-step floats are exact binary fractions
        out[k] = fv
        tot += fv
    return {k: v / tot for k, v in out.items()}


def base_amount_pmf(mult: float) -> dict[int, Fraction]:
    """pmf of max(1, round(r * mult)) for r ~ U{1..BASE_ROLL_MAX} — the engine's
    own float round(), enumerated."""
    pmf: dict[int, Fraction] = {}
    n = rewards.BASE_ROLL_MAX
    for r in range(1, n + 1):
        a = max(1, round(r * mult))
        pmf[a] = pmf.get(a, Fraction(0)) + Fraction(1, n)
    return pmf


def cell_scaled(a: int, feature) -> int:
    """The engine's apply_cell_to_loot amount scaling, via grid._RICHNESS."""
    return max(1, round(a * grid._RICHNESS[feature]))


def per_dig_pmf(mult: float, depth: int, cells: str) -> dict[tuple[str, int], Fraction]:
    """Exact pmf over (ore, amount) per dig. cells: 'normal' or 'grid'."""
    wd = depth_weights(depth)
    base = base_amount_pmf(mult)
    pmf: dict[tuple[str, int], Fraction] = {}
    feat_dist = FEATS if cells == "grid" else [(grid.CellFeature.NORMAL, Fraction(1))]
    for feat, pf in feat_dist:
        if pf == 0:
            continue
        for a, pa in base.items():
            amt = cell_scaled(a, feat)
            # RICH/TREASURE swap the found ore for the cell's featured ore —
            # itself drawn from the same depth weights (grid.cell_at), so the
            # ore marginal is wd either way.
            for ore, po in wd.items():
                key = (ore, amt)
                pmf[key] = pmf.get(key, Fraction(0)) + pf * pa * po
    return pmf


def E_coins(pmf) -> Fraction:
    return sum(p * a * ORE_VALUES[o] for (o, a), p in pmf.items())


def E_ore(pmf, ore: str) -> Fraction:
    return sum(p * a for (o, a), p in pmf.items() if o == ore)


IRON_MULT = rewards.mine_multiplier({"tool": "iron pickaxe"}, {})
check("aux:iron pickaxe mult 1.25", IRON_MULT == 1.25, str(IRON_MULT))

PROFILES = {
    "P0_fresh_floor": dict(mult=IRON_MULT, depth=0, cells="normal"),
    "P1_surface_roamer": dict(mult=IRON_MULT, depth=0, cells="grid"),
    "P2_cavern_roamer": dict(mult=IRON_MULT, depth=1, cells="grid"),
    "P3_deep_roamer": dict(mult=IRON_MULT, depth=2, cells="grid"),
}

prof_res = {}
for name, cfg in PROFILES.items():
    pmf = per_dig_pmf(cfg["mult"], cfg["depth"], cfg["cells"])
    ec = E_coins(pmf)
    prof_res[name] = {
        "E_coins_per_dig": ec,
        "coins_per_hour_sustained": ec * 360,
        "E_stone_per_dig": E_ore(pmf, "stone"),
        "E_iron_per_dig": E_ore(pmf, "iron"),
        "E_gold_per_dig": E_ore(pmf, "gold"),
        "pmf": pmf,
    }

# Registered closed-form prediction confirmations.
check("pred:E[v] d0 == 64/21", depth_weights(0) and
      sum(depth_weights(0)[o] * ORE_VALUES[o] for o in ORE_VALUES) == Fraction(64, 21))
check("pred:E[v] d1 == 85/22",
      sum(depth_weights(1)[o] * ORE_VALUES[o] for o in ORE_VALUES) == Fraction(85, 22))
check("pred:E[v] d2 == 106/23",
      sum(depth_weights(2)[o] * ORE_VALUES[o] for o in ORE_VALUES) == Fraction(106, 23))
check("pred:P0 E[coins/dig] == 32/7",
      prof_res["P0_fresh_floor"]["E_coins_per_dig"] == Fraction(32, 7),
      str(prof_res["P0_fresh_floor"]["E_coins_per_dig"]))
_amt_grid = sum(p * a for (o, a), p in
                per_dig_pmf(IRON_MULT, 0, "grid").items()) / Fraction(64, 21) * Fraction(3, 2)
check("pred:grid E[amount] == 1.59",
      sum(pf * sum(pa * cell_scaled(a, f) for a, pa in base_amount_pmf(IRON_MULT).items())
          for f, pf in FEATS) == Fraction(159, 100))

# --------------------------------------------------------------------------- #
# 3. PROBE A — descend gate. Exact DP + deterministic action counts.
# --------------------------------------------------------------------------- #
def coin_pmf(pmf) -> dict[int, Fraction]:
    out: dict[int, Fraction] = {}
    for (o, a), p in pmf.items():
        c = a * ORE_VALUES[o]
        out[c] = out.get(c, Fraction(0)) + p
    return out


def digs_to_threshold(cp: dict[int, Fraction], T: int):
    """Exact distribution of digs until cumulative coins >= T (min coin >= 1
    so at most T digs). Returns (E, quantiles, full distribution)."""
    states = {0: Fraction(1)}
    done: dict[int, Fraction] = {}
    step = 0
    while states:
        step += 1
        nxt: dict[int, Fraction] = {}
        absorbed = Fraction(0)
        for s, ps in states.items():
            for c, pc in cp.items():
                s2 = s + c
                if s2 >= T:
                    absorbed += ps * pc
                else:
                    nxt[s2] = nxt.get(s2, Fraction(0)) + ps * pc
        if absorbed:
            done[step] = absorbed
        states = nxt
        if step > T:
            break
    E = sum(Fraction(k) * v for k, v in done.items())
    cum = Fraction(0)
    quant = {}
    for q in (Fraction(1, 2), Fraction(9, 10), Fraction(99, 100)):
        cum2 = Fraction(0)
        for k in sorted(done):
            cum2 += done[k]
            if cum2 >= q:
                quant[str(q)] = k
                break
    worst = max(done)
    check(f"dp:mass sums to 1 (T={T})", sum(done.values()) == 1)
    return E, quant, worst, done


cp0 = coin_pmf(prof_res["P0_fresh_floor"]["pmf"])
E_digs10, q10, worst10, _ = digs_to_threshold(cp0, 10)

gate = {}
# G0 current — CHOP-CRAFT path: chop yields U{1,2,3} wood (no axe); torch = 2 wood.
# P(1 chop suffices) = 2/3; worst-case DETERMINISTIC 2 chops. Then craft+equip+descend.
gate["G0_chop_craft"] = {
    "E_chops": Fraction(4, 3),
    "E_actions": Fraction(4, 3) + 3,
    "worst_actions": 2 + 3,
    "worst_seconds_INT1": (2 + 3) * 2,
}
# G0 — DIG-SELL-BUY path: digs to 10 coins (exact DP) + sell + buy + equip + descend.
gate["G0_dig_sell_buy"] = {
    "E_digs": E_digs10,
    "digs_quantiles": q10,
    "worst_digs": worst10,
    "E_actions": E_digs10 + 4,
    "worst_actions": worst10 + 4,
}
# G1 — pickaxe grants depth 1: descend immediately.
gate["G1_pickaxe_grants_depth1"] = {"worst_actions": 1, "worst_seconds_INT1": 2,
                                    "cost": "deletes the light-slot Cavern gate (torch teaching beat); lantern still gates Deep"}
# G2 — torch cheaper/earlier: 5 coins or 1 wood.
E_digs5, q5, worst5, _ = digs_to_threshold(cp0, 5)
gate["G2_torch_cheaper"] = {
    "chop_worst_actions": 1 + 3,
    "dig_E_digs": E_digs5,
    "dig_worst_digs": worst5,
}
g0_worst_actions = min(gate["G0_chop_craft"]["worst_actions"],
                       gate["G0_dig_sell_buy"]["worst_actions"])
g0_worst_seconds = g0_worst_actions * 2  # all inside the full-bar burst @ INT-1
gate["G0_best_worst_case"] = {"actions": g0_worst_actions, "seconds_INT1": g0_worst_seconds}
BAND_GATE_RATIFY = g0_worst_actions <= 20 and g0_worst_seconds <= 120
check("band:GATE evaluated", True, f"worst {g0_worst_actions} actions / {g0_worst_seconds}s")
R["probe_a"] = gate

# --------------------------------------------------------------------------- #
# 4. PROBE B — faucet/sink. Exact rates, NP-1 composite, sink times.
# --------------------------------------------------------------------------- #
def digs_time(d: Fraction) -> Fraction:
    """Wall-clock seconds for d digs: first 60 in the full-bar burst @ INT-1
    (2 s/action), the rest energy-bound @ 10 s/dig."""
    burst = min(d, Fraction(60))
    rest = max(d - 60, Fraction(0))
    return burst * 2 + rest * 10


# BAND-SWORD: digs to iron sword at P1 (fluid + exact DP).
ec1 = prof_res["P1_surface_roamer"]["E_coins_per_dig"]
sword_fluid = Fraction(60) / ec1
E_sw, q_sw, worst_sw, _ = digs_to_threshold(coin_pmf(prof_res["P1_surface_roamer"]["pmf"]), 60)
BAND_SWORD_LOW, BAND_SWORD_HIGH = 10, 200
BAND_SWORD_RATIFY = BAND_SWORD_LOW <= float(E_sw) <= BAND_SWORD_HIGH

# NP-1 composite (fluid expectation accounting per fixtures).
np1 = {}
ec0 = prof_res["P0_fresh_floor"]["E_coins_per_dig"]
ec2 = prof_res["P2_cavern_roamer"]["E_coins_per_dig"]
ec3 = prof_res["P3_deep_roamer"]["E_coins_per_dig"]
d_torch = Fraction(10) / ec0
d_lantern = Fraction(40) / ec2
d_sword = Fraction(60) / ec3
# Withheld-material value adjustment: forge materials come out of ore that would
# otherwise be sold, so the coin need rises by the withheld sell value.
withheld_f1 = 25 * ORE_VALUES["iron"] + 15 * ORE_VALUES["stone"]   # 90
withheld_f2 = 20 * ORE_VALUES["gold"] + 10 * ORE_VALUES["iron"]    # 150
d_forge1 = (Fraction(3000) + withheld_f1) / ec3
d_forge2 = (Fraction(8000) + withheld_f2) / ec3
cum_torch = d_torch
cum_lantern = cum_torch + d_lantern
cum_sword = cum_lantern + d_sword
cum_f1 = cum_sword + d_forge1
cum_f2 = cum_f1 + d_forge2
np1["digs"] = {"torch": cum_torch, "lantern": cum_lantern, "iron_sword": cum_sword,
               "forge_I": cum_f1, "forge_II": cum_f2}
np1["seconds_sustained"] = {k: digs_time(v) for k, v in np1["digs"].items()}
np1["withheld_material_value"] = {"forge_I": withheld_f1, "forge_II": withheld_f2}

# Binding-resource check: expected materials on hand at each forge milestone
# (accumulated at the stage rates) vs the requirement.
mats_at_f1 = {
    "iron": d_torch * prof_res["P0_fresh_floor"]["E_iron_per_dig"]
    + d_lantern * prof_res["P2_cavern_roamer"]["E_iron_per_dig"]
    + (d_sword + d_forge1) * prof_res["P3_deep_roamer"]["E_iron_per_dig"],
    "stone": d_torch * prof_res["P0_fresh_floor"]["E_stone_per_dig"]
    + d_lantern * prof_res["P2_cavern_roamer"]["E_stone_per_dig"]
    + (d_sword + d_forge1) * prof_res["P3_deep_roamer"]["E_stone_per_dig"],
}
gold_at_f2 = (cum_f2 - cum_lantern) * prof_res["P3_deep_roamer"]["E_gold_per_dig"]
np1["materials_check"] = {
    "iron_at_forge_I_vs_25": mats_at_f1["iron"],
    "stone_at_forge_I_vs_15": mats_at_f1["stone"],
    "gold_at_forge_II_vs_20": gold_at_f2,
    "coins_bind": mats_at_f1["iron"] >= 25 and mats_at_f1["stone"] >= 15 and gold_at_f2 >= 20,
}
check("np1:coins bind (materials non-binding)", np1["materials_check"]["coins_bind"])

BAND_F1_RATIFY = 200 <= float(cum_f1) <= 2200
BAND_F2_RATIFY = 500 <= float(cum_f2) <= 4400
R["probe_b"] = {
    "profiles": {k: {kk: vv for kk, vv in v.items() if kk != "pmf"} for k, v in prof_res.items()},
    "sword": {"P1_fluid_digs": sword_fluid, "P1_E_digs": E_sw, "P1_quantiles": q_sw,
              "P1_worst_digs": worst_sw},
    "np1": np1,
}

# --------------------------------------------------------------------------- #
# 5. REPORTING LEGS (cannot flip the ruling).
# --------------------------------------------------------------------------- #
# TOOL-LADDER: E[amount] per tool at a NORMAL cell under BASE_ROLL_MAX=2.
tools = {"bare hands": {}, "pickaxe": {"tool": "pickaxe"}, "iron pickaxe": {"tool": "iron pickaxe"},
         "gold pickaxe": {"tool": "gold pickaxe"}, "diamond pickaxe": {"tool": "diamond pickaxe"}}
ladder_leg = {}
for tname, eq in tools.items():
    m = rewards.mine_multiplier(eq, {})
    pmfa = base_amount_pmf(m)
    ladder_leg[tname] = {"multiplier": m, "E_amount": sum(a * p for a, p in pmfa.items()),
                         "support": sorted(pmfa)}
check("ladder:pickaxe amount-identical to bare hands",
      ladder_leg["pickaxe"]["E_amount"] == ladder_leg["bare hands"]["E_amount"] == Fraction(3, 2))
check("ladder:iron pickaxe amount-identical to bare hands",
      ladder_leg["iron pickaxe"]["E_amount"] == Fraction(3, 2))
check("ladder:gold pickaxe pays (E 2)", ladder_leg["gold pickaxe"]["E_amount"] == Fraction(2))
check("ladder:diamond pickaxe pays (E 5/2)",
      ladder_leg["diamond pickaxe"]["E_amount"] == Fraction(5, 2))
R["tool_ladder_leg"] = ladder_leg

# FAUCET-BYPASS: boosters convert coins->energy at 20/25 and 40/50 = 0.8 coins/dig.
booster_cost = Fraction(market.GEAR_SHOP["ration"], energy.RESTORE_VALUES["ration"])
booster_cost2 = Fraction(market.GEAR_SHOP["energy drink"], energy.RESTORE_VALUES["energy drink"])
check("bypass:booster cost 0.8 coins/dig (both items)",
      booster_cost == booster_cost2 == Fraction(4, 5))
net3 = ec3 - booster_cost
bypass = {
    "coins_per_dig_cost": booster_cost,
    "net_coins_per_dig_P3": net3,
    "digs_per_hour_INT1": 1800,
    "net_coins_per_hour_boosted_P3": net3 * 1800,
    "boosted_seconds_to_forge_I_from_P3": (Fraction(3000) + withheld_f1) / net3 * 2,
    "boosted_seconds_to_forge_II_after_I": (Fraction(8000) + withheld_f2) / net3 * 2,
    "note": "boosted active play is x5 the sustained throttle and PROFITABLE (0.8 < E[coins/dig] at every depth) — the 360/hr energy throttle is bypassable at scale for coins; flagged, reporting-only",
}
check("bypass:boosting profitable at P0 (0.8 < 32/7)", booster_cost < ec0)
R["faucet_bypass_leg"] = bypass

# PACKET-ARITHMETIC: the packet's '~22 coins per 8 digs'.
w0 = {o: Fraction(w) for o, w in rewards.ORE_WEIGHTS.items()}
low3 = ["stone", "bronze", "iron"]
E_v_low3 = sum(w0[o] * ORE_VALUES[o] for o in low3) / sum(w0[o] for o in low3)
packet_per8 = E_v_low3 * Fraction(3, 2) * 8
R["packet_arithmetic_leg"] = {
    "E_value_stone_bronze_iron_only": E_v_low3,
    "x1.5_amount_x8_digs": packet_per8,
    "exact_faucet_per8_P0": ec0 * 8,
    "exact_faucet_per8_P1": ec1 * 8,
    "reading": "the packet's ~22/8digs is the stone/bronze/iron-only average (28/15 x 1.5 x 8 = 22.4); the true faucet includes silver/gold/diamond and is ~1.6-1.7x higher",
}
check("packet:~22 per 8 digs reconstructed (22.4)", packet_per8 == Fraction(112, 5))

# --------------------------------------------------------------------------- #
# 6. MC VALIDATION LEGS (seeded, engine-driven; self-checks only).
# --------------------------------------------------------------------------- #
MC_N = 200_000
MC = {}
seeds = {"P0_fresh_floor": 20260792, "P1_surface_roamer": 20260793,
         "P2_cavern_roamer": 20260794, "P3_deep_roamer": 20260795}
feat_names = [f for f, _ in grid._FEATURE_WEIGHTS]
feat_ws = [w for _, w in grid._FEATURE_WEIGHTS]
for pname, cfg in PROFILES.items():
    rng = random.Random(seeds[pname])
    wd = rewards.ore_weights_for_depth(cfg["depth"])
    ores, ws = list(wd.keys()), list(wd.values())
    total = 0
    for _ in range(MC_N):
        found, amt = rewards.roll_mine_loot(
            has_pickaxe=False, depth=cfg["depth"], multiplier=cfg["mult"], rng=rng)
        if cfg["cells"] == "grid":
            feat = rng.choices(feat_names, weights=feat_ws, k=1)[0]
            featured = rng.choices(ores, weights=ws, k=1)[0]
            cell = grid.Cell(0, 0, cfg["depth"], feat, featured, grid._RICHNESS[feat])
            found, amt, _n = grid.apply_cell_to_loot(cell, found, amt)
        total += amt * ORE_VALUES[found]
    mean = Fraction(total, MC_N)
    exact = prof_res[pname]["E_coins_per_dig"]
    rel = abs(mean - exact) / exact
    MC[pname] = {"seed": seeds[pname], "N": MC_N, "mc_mean": mean, "exact": exact,
                 "rel_err": rel}
    check(f"mc:{pname} within 1% of exact", rel <= Fraction(1, 100), f"rel {float(rel):.5f}")

# GRID-1 leg: engine-exact cell_at frequencies vs _FEATURE_WEIGHTS.
world_seed = 20260796
crng = random.Random(20260797)
counts = {f: 0 for f in feat_names}
G_N = 200_000
for _ in range(G_N):
    x, y = crng.randint(-500, 500), crng.randint(-500, 500)
    z = crng.randint(0, 2)
    counts[grid.cell_at(world_seed, x, y, z).feature] += 1
grid1 = {}
for f, w in grid._FEATURE_WEIGHTS:
    obs = Fraction(counts[f], G_N)
    exp = Fraction(w) / 100
    grid1[f.name] = {"observed": obs, "expected": exp, "abs_err": abs(obs - exp)}
    check(f"grid1:{f.name} freq within 1% abs", abs(obs - exp) <= Fraction(1, 100),
          f"{float(obs):.4f} vs {float(exp):.4f}")
R["mc"] = MC
R["grid1"] = grid1
R["grid1_seeds"] = {"world_seed": world_seed, "coord_seed": 20260797,
                    "disclosure": "the two GRID-1 seeds were not enumerated in fixtures.json (which pinned only the four profile-MC seeds); chosen per the registered policy (strictly above high-water 20260791), disclosed here — intake-time decision, self-check leg only"}

# --------------------------------------------------------------------------- #
# 7. DECISION (the pre-registered mechanical rule; NULL-first).
# --------------------------------------------------------------------------- #
bands = {
    "BAND-GATE": {"ratify": BAND_GATE_RATIFY,
                  "measured": f"worst-case deterministic {g0_worst_actions} actions / {g0_worst_seconds}s @ INT-1 (chop-craft path)"},
    "BAND-SWORD": {"ratify": BAND_SWORD_RATIFY,
                   "measured": f"E[digs]={float(E_sw):.3f} (band [10,200])"},
    "BAND-FORGE1": {"ratify": BAND_F1_RATIFY,
                    "measured": f"NP-1 cumulative {float(cum_f1):.1f} digs (band [200,2200])"},
    "BAND-FORGE2": {"ratify": BAND_F2_RATIFY,
                    "measured": f"NP-1 cumulative {float(cum_f2):.1f} digs (band [500,4400])"},
}
if not B0_OK:
    ruling = "NULL"
else:
    a_ok = BAND_GATE_RATIFY
    b_ok = BAND_SWORD_RATIFY and BAND_F1_RATIFY and BAND_F2_RATIFY
    ruling = "approve" if (a_ok and b_ok) else ("conditional" if (a_ok or b_ok) else "reject")
R["bands"] = bands
R["ruling"] = ruling

# --------------------------------------------------------------------------- #
# 8. Emit.
# --------------------------------------------------------------------------- #
def enc(o):
    if isinstance(o, Fraction):
        return {"frac": f"{o.numerator}/{o.denominator}", "float": float(o)}
    if isinstance(o, dict):
        return {str(k): enc(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [enc(v) for v in o]
    if hasattr(o, "name"):  # Enum
        return o.name
    return o


failed = [(n, d) for n, ok, d in CHECKS if not ok]
R["self_checks"] = {"passed": len(CHECKS) - len(failed), "failed": len(failed),
                    "failures": [{"name": n, "detail": d} for n, d in failed]}

out = json.dumps(enc(R), indent=2, sort_keys=True)
with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    fh.write(out + "\n")

print(f"VERDICT 042 mining-economy-tuning @ {MANIFEST['pinned_sha'][:8]}")
print(f"B0 validity gate: {'PASS' if B0_OK else 'FAIL'}")
for name, cfg in PROFILES.items():
    v = prof_res[name]
    print(f"  {name}: E[coins/dig] = {v['E_coins_per_dig']} = {float(v['E_coins_per_dig']):.4f}"
          f" -> {float(v['coins_per_hour_sustained']):.1f}/h sustained")
print(f"gate G0 worst-case: {g0_worst_actions} actions / {g0_worst_seconds}s (chop-craft);"
      f" dig-sell-buy E[digs]={float(E_digs10):.3f} worst {worst10}")
print(f"sword@P1 E[digs]={float(E_sw):.3f}; NP-1 forge I {float(cum_f1):.1f} digs"
      f" ({float(np1['seconds_sustained']['forge_I'])/3600:.2f}h),"
      f" forge II {float(cum_f2):.1f} digs ({float(np1['seconds_sustained']['forge_II'])/3600:.2f}h)")
print(f"bands: " + ", ".join(f"{k}={'RATIFY' if v['ratify'] else 'FAIL'}" for k, v in bands.items()))
print(f"tool ladder E[amount]: " + ", ".join(
    f"{t}={v['E_amount']}" for t, v in ladder_leg.items()))
print(f"booster bypass: net {float(net3):.4f} coins/dig boosted, "
      f"forge I in {float(bypass['boosted_seconds_to_forge_I_from_P3'])/60:.1f} min boosted")
print(f"packet arithmetic: {float(packet_per8):.1f} per 8 digs reconstructed vs exact "
      f"{float(ec0*8):.1f} (P0) / {float(ec1*8):.1f} (P1)")
print(f"RULING: {ruling}")
print(f"SELF-CHECKS: {len(CHECKS) - len(failed)} passed, {len(failed)} failed")
for n, d in failed:
    print(f"  FAILED: {n} ({d})")
sys.exit(1 if failed else 0)
