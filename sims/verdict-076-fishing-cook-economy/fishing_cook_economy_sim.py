"""VERDICT 076 — fishing cook-leg constants (SIM-REQUEST · fishing-cook-economy · 2026-07-13).

Hermetic: reads only ./fixtures.json and the byte-copied packet closure in ./fixtures/
(menno420/superbot-games @ ed2fabbef58f3b97a03e6586a4e03ad0ab89c451, sha256 MANIFEST
re-verified before import). Drives the packet's OWN resolver; species tables injected
as DATA only. Catch streams are P-independent, so each world is measured once and the
P grid is folded arithmetically from the recorded species counts (convention K1).

Run:  python3 sims/verdict-076-fishing-cook-economy/fishing_cook_economy_sim.py
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")

_CHECKS: list[tuple[str, bool]] = []


def check(name: str, cond: bool) -> None:
    _CHECKS.append((name, bool(cond)))
    if not cond:
        print(f"SELF-CHECK FAIL: {name}")


def verify_manifest() -> None:
    n = 0
    with open(os.path.join(FIX, "MANIFEST.sha256"), encoding="utf-8") as fh:
        for line in fh:
            digest, rel = line.split()
            with open(os.path.join(FIX, rel), "rb") as f:
                h = hashlib.sha256(f.read()).hexdigest()
            check(f"manifest:{rel}", h == digest)
            n += 1
    check("manifest:count==16", n == 16)


verify_manifest()
check("cpython-3.11", platform.python_implementation() == "CPython" and sys.version_info[:2] == (3, 11))

with open(os.path.join(HERE, "fixtures.json"), encoding="utf-8") as fh:
    REG = json.load(fh)

sys.path.insert(0, FIX)
import games.fishing.core.catch as catch  # noqa: E402
import games.fishing.core.economy as economy_mod  # noqa: E402
import games.fishing.core.rng as rng_mod  # noqa: E402
import games.fishing.core.species as species_mod  # noqa: E402
import games.fishing.core.spots as spots_mod  # noqa: E402
import games.fishing.sim.catch_sim as catch_sim  # noqa: E402
import games.mining.core.energy as energy_mod  # noqa: E402
import games.mining.core.items as items_mod  # noqa: E402
import games.mining.core.market as market_mod  # noqa: E402

RESULTS: dict = {"verdict": "VERDICT 076", "registered_utc": REG["registered_utc"]}

# --------------------------------------------------------------------------- B0
B0 = REG["committed_constants_B0"]
check("B0:RESTORE_VALUES", energy_mod.RESTORE_VALUES == B0["RESTORE_VALUES"])
check("B0:flat-cooked-fish-30", energy_mod.RESTORE_VALUES["cooked fish"] == 30)
check("B0:buy(ration)", market_mod.buy_price("ration") == 20)
check("B0:buy(drink)", market_mod.buy_price("energy drink") == 40)
check("B0:shop-price-0.8", 20 / 25 == 0.8 and 40 / 50 == 0.8)
_cf = items_mod.lookup("cooked fish")
check("B0:cooked-item", _cf is not None and _cf.value == 5 and _cf.kind is items_mod.ItemKind.CONSUMABLE)
check("B0:cooked-not-sellable", market_mod.sell_price("cooked fish") is None)
check("B0:SELL_VALUES", economy_mod.SELL_VALUES == B0["SELL_VALUES"])
check("B0:CAST_COST", catch.CAST_COST == B0["CAST_COST"])
check("B0:REGEN_SECONDS", energy_mod.REGEN_SECONDS == B0["REGEN_SECONDS"])
# The request's claim: "no cooked-value or energy-restore constants anywhere in the repo".
# Measured: FALSE for the flat mining-side constant (RESTORE_VALUES['cooked fish']=30 exists
# at the pin), TRUE for per-species fishing constants (none exist).
RESULTS["B0_request_claim"] = {
    "claim": REG["source_request"]["request_claim_to_test"],
    "finding": "PARTIALLY FALSE at the pin: games/mining/core/energy.py RESTORE_VALUES carries a FLAT 'cooked fish': 30 (the legacy-inherited campfire meal); NO per-species constants exist — the ask stands, but the flat constant is committed reality the cook wiring must supersede or reconcile (audited as F-FLAT30)",
}

# --------------------------------------------------------------------------- worlds
PINNED = {"minnow": (1, 50.0, 8), "bass": (2, 30.0, 13), "pike": (3, 15.0, 27), "legend_carp": (4, 5.0, 80)}
_ORIG = (species_mod._SPECIES, dict(species_mod._BY_ID), species_mod.MAX_SIZE_RANK)


def disp(sid: str) -> str:
    return sid.replace("_", " ").title()


def inject(rows) -> None:
    species_mod._SPECIES = tuple(rows)
    species_mod._BY_ID = {s.species_id: s for s in rows}
    species_mod.MAX_SIZE_RANK = max(s.size_rank for s in rows)


def restore() -> None:
    species_mod._SPECIES, by_id, species_mod.MAX_SIZE_RANK = _ORIG[0], _ORIG[1], _ORIG[2]
    species_mod._BY_ID = dict(by_id)


def wr_world():
    rows, sells = [], {}
    for sid, venue, rank, weight, sell in REG["worlds"]["WR_rows"]:
        rows.append(species_mod.Species(sid, disp(sid), "🐟", f"a {disp(sid).lower()}", rank, weight))
        sells[sid] = sell
    return rows, sells


def w4_world():
    rows = list(_ORIG[0])
    sells = dict(economy_mod.SELL_VALUES)
    return rows, sells


def measure_counts(rows, seeds, casts: int = 40):
    """K1 loop: per (spot,tier) cast/bite/species counts via the packet resolver."""
    inject(rows)
    tiers = catch_sim.tier_stats()
    cells = {(sp, t): {"casts": 0, "bites": 0, "species": Counter()}
             for sp in spots_mod.spot_ids() for t in tiers}
    for seed in seeds:
        for sp in spots_mod.spot_ids():
            for i in range(casts):
                base = rng_mod.fishing_seed(seed, f"{sp}:{i}")
                for tname, stats in tiers.items():
                    out = catch.resolve_cast(seed, sp, stats, rng=random.Random(base))
                    c = cells[(sp, tname)]
                    c["casts"] += 1
                    if out.bit and out.catch is not None:
                        c["bites"] += 1
                        c["species"][out.catch.species_id] += 1
    restore()
    return cells


def fold_rho(cells, energy_of) -> dict:
    """rho(cell) = bite_rate * E[E_s|catch] / CAST_COST from recorded counts."""
    out = {}
    for (sp, t), c in cells.items():
        if c["bites"]:
            mean_e = sum(energy_of[sid] * n for sid, n in c["species"].items()) / c["bites"]
        else:
            mean_e = 0.0
        bite = c["bites"] / c["casts"]
        out[f"{sp}/{t}"] = {"bite_rate": round(bite, 6), "mean_cook_energy": round(mean_e, 6),
                            "rho": round(bite * mean_e / catch.CAST_COST, 6)}
    return out


EVAL_SEEDS = list(range(20261509, 20261549))
STAB_SEEDS = list(range(20261549, 20261559))
check("seeds:eval-count", len(EVAL_SEEDS) == 40)
check("seeds:above-V075", min(EVAL_SEEDS) > 20261508)
check("seeds:high-water==20261558", max(STAB_SEEDS) == 20261558)

print("measuring W4 (committed 4-species, decision world) and WR (V075 candidate, reporting) ...")
rows4, sells4 = w4_world()
rowsR, sellsR = wr_world()
check("WR:33-rows", len(rowsR) == 33)
cells4 = measure_counts(rows4, EVAL_SEEDS)
cellsR = measure_counts(rowsR, EVAL_SEEDS)

# --------------------------------------------------------------------------- F-FLAT30 audit
flat30 = {"W4": {}, "WR": {}}
for wname, cells in (("W4", cells4), ("WR", cellsR)):
    for (sp, t), c in cells.items():
        bite = c["bites"] / c["casts"]
        flat30[wname][f"{sp}/{t}"] = round(15.0 * bite, 6)  # rho_flat = bite*30/2
_flat_min = min(min(v.values()) for v in flat30.values())
check("F-FLAT30:perpetual-motion-everywhere", _flat_min >= 4.5 * 0.3 / 0.3 and _flat_min > 1.0)
RESULTS["F_FLAT30"] = {"rho_flat_by_cell": flat30, "min_rho_flat": _flat_min,
                       "floor_bound": "rho_flat = 15 x bite_rate >= 15 x MIN_BITE_CHANCE(0.30) = 4.5 at ANY cell of ANY world — the committed flat 30 is a self-sustaining energy loop (perpetual motion) the moment a fishing-haul cook op wires it; it must be superseded by the per-species table"}
check("F-FLAT30:bound-4.5", _flat_min >= 4.5)

# --------------------------------------------------------------------------- P sweep (folded)
P_GRID = REG["cook_family"]["P_grid"]
MAXF = 755 / 56  # mining ceiling proxy; V043 fishing band top 10.20 also quoted
sweep = []
for P in P_GRID:
    e4 = {sid: max(1, round(s / P)) for sid, s in sells4.items()}
    eR = {sid: max(1, round(s / P)) for sid, s in sellsR.items()}
    rho4 = fold_rho(cells4, e4)
    rhoR = fold_rho(cellsR, eR)
    worst4 = max(v["rho"] for v in rho4.values())
    worstR = max(v["rho"] for v in rhoR.values())
    c1 = worst4 <= 0.9
    min_price4 = min(sells4[sid] / e4[sid] for sid in e4)
    c2 = min_price4 >= 0.8
    sweep.append({"P": P, "worst_rho_W4": worst4, "worst_rho_WR": worstR,
                  "min_implied_price_W4": round(min_price4, 6), "C1_PM": c1, "C2_BYPASS": c2,
                  "E_committed": e4, "pass": c1 and c2})
RESULTS["P_sweep"] = [{k: v for k, v in row.items() if k != "E_committed"} for row in sweep]
check("sweep:9-cells", len(sweep) == 9)

passing = [row for row in sweep if row["pass"]]
ruling: dict = {}
if not passing:
    ruling["outcome"] = "REJECT"
    ruling["reason"] = "no P in the registered grid satisfies C1_PM and C2_BYPASS on the committed world"
else:
    win = min(passing, key=lambda r: r["P"])
    P_STAR = win["P"]
    E_STAR = win["E_committed"]
    ruling["outcome"] = "APPROVE-WITH-CONSTANTS"
    ruling["P_star"] = P_STAR
    ruling["cook_energy_committed_species"] = E_STAR
    ruling["extension_rule"] = f"E_s = max(1, round(S_s / {P_STAR})) for any later-pinned roster species (roster per-species values inherit VERDICT 075's NULL; the roster wave re-derives P via this same registered selector at its own pin)"

    # C3 choice axes at P*
    rho4_star = fold_rho(cells4, E_STAR)
    rhoR_star = fold_rho(cellsR, {sid: max(1, round(s / P_STAR)) for sid, s in sellsR.items()})
    coin_axis = {sid: {"E_s": E_STAR[sid], "sell": sells4[sid],
                       "cook_then_earn_at_max_faucet": round(E_STAR[sid] * MAXF, 6),
                       "coin_dominated": E_STAR[sid] * MAXF <= sells4[sid]}
                 for sid in E_STAR}
    time_axis = {sid: {"regen_seconds_skipped": E_STAR[sid] * energy_mod.REGEN_SECONDS} for sid in E_STAR}
    RESULTS["C3_choice"] = {
        "coin_axis_arithmetic": coin_axis,
        "time_axis_measured": time_axis,
        "judgment_label": "the VALUE of the time axis (energy-now vs coins-later) and of campfire shop-independence is JUDGMENT-ONLY; the domination arithmetic above is measured",
        "shop_context": "under the committed (V042-flagged, intent-open) shop at 0.8 coins/energy, sell-then-buy-rations yields 1.25 energy per forgone coin — cooking at P* is coin-dominated BY DESIGN (the anti-bypass direction); its niche is immediacy + campfire access",
    }
    RESULTS["rho_at_P_star"] = {"W4": rho4_star, "WR": rhoR_star}

    # K6 stability
    cells4s = measure_counts(rows4, STAB_SEEDS)
    rho4s = fold_rho(cells4s, E_STAR)
    worst_s = max(v["rho"] for v in rho4s.values())
    RESULTS["stability"] = {"worst_rho_W4": worst_s, "cells": rho4s}
    check("stability:rho<=0.9", worst_s <= 0.9)
    check("stability:rho<1.0", worst_s < 1.0)
    if worst_s > 0.9:
        ruling["outcome"] = "NULL"
        ruling["null_axis"] = "stability band break on rho at P* (K5/K6)"

RESULTS["ruling"] = ruling
RESULTS["seeds"] = {"eval": [EVAL_SEEDS[0], EVAL_SEEDS[-1]], "stability": [STAB_SEEDS[0], STAB_SEEDS[-1]],
                    "fleet_high_water_after": 20261558}

failed = [n for n, ok in _CHECKS if not ok]
RESULTS["self_checks"] = {"passed": len(_CHECKS) - len(failed), "failed": len(failed), "failed_names": failed}
out = json.dumps(RESULTS, sort_keys=True, indent=1)
with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    fh.write(out + "\n")

print(f"F-FLAT30 min rho_flat: {_flat_min} (perpetual motion everywhere)")
print(f"passing P cells: {[r['P'] for r in passing]}")
print(f"RULING: {ruling['outcome']}" + (f" P*={ruling.get('P_star')}" if "P_star" in ruling else ""))
if "cook_energy_committed_species" in ruling:
    print(f"cook energy (committed 4): {ruling['cook_energy_committed_species']}")
print(f"SELF-CHECKS: {len(_CHECKS) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
