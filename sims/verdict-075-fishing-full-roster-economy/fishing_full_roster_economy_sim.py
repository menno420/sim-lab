"""VERDICT 075 — fishing full-roster sell/XP curve (SIM-REQUEST · fishing-full-roster-economy · 2026-07-13).

Hermetic: reads only ./fixtures.json and the byte-copied packet closure in ./fixtures/
(menno420/superbot-games @ ed2fabbef58f3b97a03e6586a4e03ad0ab89c451, sha256 MANIFEST
re-verified before import). Drives the packet's OWN resolver (games.fishing.core.catch
.resolve_cast) and harness (games.fishing.sim.catch_sim.run); the species table is
swapped as DATA only (the packet's documented growth surface). Zero logic edits.

Run:  python3 sims/verdict-075-fishing-full-roster-economy/fishing_full_roster_economy_sim.py
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")

# --------------------------------------------------------------------------- self-checks
_CHECKS: list[tuple[str, bool]] = []


def check(name: str, cond: bool) -> None:
    _CHECKS.append((name, bool(cond)))
    if not cond:
        print(f"SELF-CHECK FAIL: {name}")


# --------------------------------------------------------------------------- manifest
def verify_manifest() -> None:
    path = os.path.join(FIX, "MANIFEST.sha256")
    n = 0
    with open(path, encoding="utf-8") as fh:
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

RESULTS: dict = {"verdict": "VERDICT 075", "registered_utc": REG["registered_utc"]}

# --------------------------------------------------------------------------- B0 validity
B0 = REG["committed_constants_B0"]
check("B0:SELL_VALUES", economy_mod.SELL_VALUES == B0["SELL_VALUES"])
check("B0:XP_PER_LEVEL", economy_mod.XP_PER_LEVEL == B0["XP_PER_LEVEL"])
check("B0:MILESTONES", list(economy_mod.MILESTONE_LEVELS) == B0["MILESTONE_LEVELS"])
check("B0:BASE_LEVEL", economy_mod.BASE_LEVEL == B0["BASE_LEVEL"])
_committed_rows = [(s.species_id, s.size_rank, s.rarity_weight) for s in species_mod.all_species()]
check("B0:species_rows", _committed_rows == [tuple(r) for r in B0["species_rows_local"]])
check("B0:MAX_SIZE_RANK==4", species_mod.MAX_SIZE_RANK == 4)
for _name in ("CAST_COST", "BASE_BITE_CHANCE", "BITE_LUCK_PER_POINT", "MAX_BITE_CHANCE",
              "MIN_BITE_CHANCE", "POWER_BIAS_PER_POINT", "SIZE_PER_RANK", "SIZE_JITTER",
              "MAX_FISHING_POWER", "MAX_BITE_LUCK"):
    check(f"B0:catch.{_name}", getattr(catch, _name) == B0[_name])
check("B0:MAX_ENERGY", energy_mod.MAX_ENERGY == B0["MAX_ENERGY"])
check("B0:DIG_COST", energy_mod.DIG_COST == B0["DIG_COST"])
check("B0:REGEN_SECONDS", energy_mod.REGEN_SECONDS == B0["REGEN_SECONDS"])
check("B0:RESTORE_VALUES", energy_mod.RESTORE_VALUES == B0["RESTORE_VALUES"])
check("B0:buy(ration)==20", market_mod.buy_price("ration") == B0["market_buy"]["ration"])
check("B0:buy(drink)==40", market_mod.buy_price("energy drink") == B0["market_buy"]["energy drink"])
check("B0:cooked-fish-not-sellable", market_mod.sell_price("cooked fish") is None)
_cf = items_mod.lookup("cooked fish")
check("B0:cooked-fish-item", _cf is not None and _cf.value == 5 and _cf.kind is items_mod.ItemKind.CONSUMABLE)
check("B0:_fish_value", items_mod._fish_value(0) == 1 and items_mod._fish_value(1) == 1 and items_mod._fish_value(21) == 21)
for _sid, _prof in B0["spots"].items():
    _sp = spots_mod.profile_for(_sid)
    check(f"B0:spot.{_sid}.bias", abs(_sp.bite_bias - _prof["bite_bias"]) < 1e-12)
    for _fid, _m in _prof["weight_mult"].items():
        check(f"B0:spot.{_sid}.mult.{_fid}", abs(_sp.multiplier_for(_fid) - _m) < 1e-12)
# V043 family identity: sell == round(8*50/w) for all four committed rows.
for _sid, _rank, _w in _committed_rows:
    check(f"B0:family:{_sid}", round(8 * 50 / _w) == economy_mod.SELL_VALUES[_sid])

# §5 reproduction — the packet's own harness at its own defaults (protocol seeds range(400)).
print("B0: running the packet harness catch_sim.run() at its own defaults ...")
_rep = catch_sim.run()
_a = B0["v043_s5_published_anchors"]
check("B0:s5:dock-fresh-bite", round(_rep.spot_tier("dock", "fresh").bite_rate * 100, 2) == _a["dock_fresh_bite_rate_pct"])
for _spot, _n in _a["fresh_bite_counts_by_spot"].items():
    check(f"B0:s5:fresh-bites:{_spot}", _rep.spot_tier(_spot, "fresh").bites == _n)
for _fid, _pct in _a["dock_fresh_shares_pct"].items():
    check(f"B0:s5:dock-fresh-share:{_fid}", round(_rep.spot_tier("dock", "fresh").species_share(_fid) * 100, 2) == _pct)
for _tier, _pct in _a["aggregate_tier_bite_pct"].items():
    check(f"B0:s5:agg-bite:{_tier}", round(_rep.by_tier[_tier].bite_rate * 100, 2) == _pct)
check("B0:s5:mean-energy==2", _rep.mean_energy_cost == _a["mean_energy_cost"])
RESULTS["B0"] = {"dock_fresh_bite_pct": round(_rep.spot_tier("dock", "fresh").bite_rate * 100, 6),
                 "mean_energy_cost": _rep.mean_energy_cost}

# --------------------------------------------------------------------------- naming leg (C10)
# Supersede reading: legend_carp VERBATIM 80 at legacy carp's rank 10 vs pinned pike 27 at rank 11
# breaks even WEAK monotonicity (80 > 27 going up-rank). Mechanical => DISTINCT.
_supersede_ok = 80 <= 27  # sell(rank10)=80 must be <= sell(rank11)=27 for weak monotonicity
check("naming:supersede-breaks-A5weak", _supersede_ok is False)
RESULTS["naming_leg"] = {"reading": "DISTINCT", "mechanics": "legend_carp@rank10=80 > pike@rank11=27 breaks weak monotonicity; distinct reading keeps carp; all 29 rows stand; legend_carp placed at shore rank 22 (strict apex)"}

# --------------------------------------------------------------------------- roster + weight law
ANCHORS = [(1, 50.0), (9, 30.0), (11, 15.0), (22, 5.0)]


def what(r: float) -> float:
    for (r0, w0), (r1, w1) in zip(ANCHORS, ANCHORS[1:]):
        if r0 <= r <= r1:
            t = (r - r0) / (r1 - r0)
            return math.exp(math.log(w0) * (1 - t) + math.log(w1) * t)
    raise ValueError(r)


for _r, _w in ANCHORS:
    check(f"interp:anchor@{_r}", abs(what(_r) - _w) < 1e-9)

PINNED = {"minnow": (1, 50.0, 8), "bass": (9, 30.0, 13), "pike": (11, 15.0, 27), "legend_carp": (22, 5.0, 80)}
SHORE_NEW = [tuple(r) for r in REG["roster"]["shore_new"]]
DEEP_NEW = [tuple(r) for r in REG["roster"]["deepwater_new"]]
check("roster:counts", len(SHORE_NEW) == 18 and len(DEEP_NEW) == 11)


def disp(sid: str) -> str:
    return sid.replace("_", " ").title()


def build_world(k: float, delta: float, world: str):
    """Candidate table rows + sell map + venue map. Worlds per C2 (W1 shore-only, W2 full)."""
    rows, sells, venue = [], {}, {}
    for sid, (rank, w, sell) in PINNED.items():
        rows.append(species_mod.Species(sid, disp(sid), "🐟", f"a {disp(sid).lower()}", rank, w))
        sells[sid] = sell
        venue[sid] = "shore"
    for sid, rank in SHORE_NEW:
        w = round(k * what(rank), 4)
        rows.append(species_mod.Species(sid, disp(sid), "🐟", f"a {disp(sid).lower()}", rank, w))
        sells[sid] = int(round(400.0 / w))
        venue[sid] = "shore"
    if world == "W2":
        for sid, rank in DEEP_NEW:
            w = round(k * delta * what(rank), 4)
            rows.append(species_mod.Species(sid, disp(sid), "🐟", f"a {disp(sid).lower()}", rank, w))
            sells[sid] = int(round(400.0 / w))
            venue[sid] = "deepwater"
    return rows, sells, venue


_ORIG = (species_mod._SPECIES, dict(species_mod._BY_ID), species_mod.MAX_SIZE_RANK)


def inject(rows) -> None:
    species_mod._SPECIES = tuple(rows)
    species_mod._BY_ID = {s.species_id: s for s in rows}
    species_mod.MAX_SIZE_RANK = max(s.size_rank for s in rows)


def restore() -> None:
    species_mod._SPECIES, by_id, species_mod.MAX_SIZE_RANK = _ORIG[0], _ORIG[1], _ORIG[2]
    species_mod._BY_ID = dict(by_id)


def a5_weak(rows, sells, venue_name: str, venue) -> tuple[bool, int, bool]:
    """(weakly increasing?, adjacent tie count, apex strict?) for one venue."""
    seq = sorted(((r.size_rank, sells[r.species_id]) for r in rows if venue[r.species_id] == venue_name))
    ok, ties = True, 0
    for (r0, s0), (r1, s1) in zip(seq, seq[1:]):
        if s1 < s0:
            ok = False
        if s1 == s0:
            ties += 1
    apex = True
    if venue_name == "shore":
        below = [s for r, s in seq if r < 22]
        apex = max(below) < 80 if below else True
    return ok, ties, apex


def measure(rows, sells, seeds, casts: int = 40):
    """C5 loop: per (spot,tier) coins/energy + bite rate + xp rate, via the packet resolver."""
    inject(rows)
    rank_of = {r.species_id: r.size_rank for r in rows}
    tiers = catch_sim.tier_stats()
    cells: dict[tuple[str, str], dict] = {(sp, t): {"casts": 0, "bites": 0, "coins": 0, "energy": 0, "xp": 0}
                                          for sp in spots_mod.spot_ids() for t in tiers}
    for seed in seeds:
        for sp in spots_mod.spot_ids():
            for i in range(casts):
                base = rng_mod.fishing_seed(seed, f"{sp}:{i}")
                for tname, stats in tiers.items():
                    out = catch.resolve_cast(seed, sp, stats, rng=random.Random(base))
                    c = cells[(sp, tname)]
                    c["casts"] += 1
                    c["energy"] += out.energy_cost
                    if out.bit and out.catch is not None:
                        c["bites"] += 1
                        c["coins"] += sells[out.catch.species_id]
                        c["xp"] += rank_of[out.catch.species_id]
    restore()
    table = {}
    for (sp, t), c in cells.items():
        table[f"{sp}/{t}"] = {
            "bite_rate": round(c["bites"] / c["casts"], 6),
            "coins_per_energy": round(c["coins"] / c["energy"], 6),
            "xp_per_hour": round(180.0 * c["xp"] / c["casts"], 6),
            "mean_sell_per_catch": round(c["coins"] / c["bites"], 6) if c["bites"] else 0.0,
        }
    return table


def two_burst_xp(rows, seeds) -> float:
    """C7: mean XP over 60 consecutive fresh casts at the dock (two full 60-energy bursts)."""
    inject(rows)
    rank_of = {r.species_id: r.size_rank for r in rows}
    fresh = catch_sim.tier_stats()["fresh"]
    total = 0
    for seed in seeds:
        for i in range(60):
            base = rng_mod.fishing_seed(seed, f"dock:{i}")
            out = catch.resolve_cast(seed, "dock", fresh, rng=random.Random(base))
            if out.bit and out.catch is not None:
                total += rank_of[out.catch.species_id]
    restore()
    return total / len(seeds)


# --------------------------------------------------------------------------- sweep
SW = REG["sweep"]
K_GRID, D_GRID = SW["k_grid"], SW["delta_grid"]
A1_LO, A1_HI = 0.85 * 32 / 7, 1.05 * 32 / 7
CEIL = 755 / 56
EVAL_SEEDS = list(range(20261389, 20261489))
STAB_SEEDS = list(range(20261489, 20261509))
check("seeds:eval-count", len(EVAL_SEEDS) == 100)
check("seeds:above-high-water", min(EVAL_SEEDS) > 20261388)

print("sweep: evaluating W1 per k and W2 per (k, delta) on the packet resolver ...")
w1_cache: dict[float, dict] = {}
cell_rows = []
for k in K_GRID:
    rows1, sells1, venue1 = build_world(k, 1.0, "W1")
    ok1, ties1, apex1 = a5_weak(rows1, sells1, "shore", venue1)
    m1 = measure(rows1, sells1, EVAL_SEEDS)
    w1_cache[k] = {"a5": (ok1, ties1, apex1), "m": m1, "sells": sells1, "rows": rows1, "venue": venue1}
for k in K_GRID:
    for d in D_GRID:
        rows2, sells2, venue2 = build_world(k, d, "W2")
        okS, tiesS, apexS = a5_weak(rows2, sells2, "shore", venue2)
        okD, tiesD, _ = a5_weak(rows2, sells2, "deepwater", venue2)
        m2 = measure(rows2, sells2, EVAL_SEEDS)
        w1 = w1_cache[k]
        parity = w1["m"]["dock/fresh"]["coins_per_energy"]
        max_ce = max([v["coins_per_energy"] for v in w1["m"].values()] + [v["coins_per_energy"] for v in m2.values()])
        a5_ok = w1["a5"][0] and w1["a5"][2] and okS and okD and apexS
        a1_ok = A1_LO <= parity <= A1_HI
        a3_ok = max_ce <= CEIL
        # measured deepwater premium: same-rank deep/shore sell ratio, median over shared ranks
        shore_by_rank = {r: sells2[sid] for sid, (rk, w, s) in PINNED.items() for r in [rk]}
        for sid, rk in SHORE_NEW:
            shore_by_rank[rk] = sells2[sid]
        prem = sorted(sells2[sid] / shore_by_rank[rk] for sid, rk in DEEP_NEW if rk in shore_by_rank)
        premium = prem[len(prem) // 2]
        cell_rows.append({"k": k, "delta": d, "parity_dock_fresh_W1": parity, "max_coins_per_energy": round(max_ce, 6),
                          "shore_ties": w1["a5"][1], "deep_ties": tiesD, "A5weak": a5_ok, "A1": a1_ok, "A3": a3_ok,
                          "eligible": a5_ok and a1_ok and a3_ok, "deep_premium_median": round(premium, 6)})
RESULTS["sweep_cells"] = cell_rows
check("sweep:32-cells", len(cell_rows) == 32)

eligible = [c for c in cell_rows if c["eligible"]]
RESULTS["eligible_count"] = len(eligible)

ruling = {}
if not eligible:
    ruling["outcome"] = "REJECT"
    ruling["reason"] = "zero (k, delta) cells satisfy A5'weak AND A1' AND A3' (registered C9)"
else:
    eligible.sort(key=lambda c: (c["delta"], abs(c["parity_dock_fresh_W1"] - 32 / 7), c["k"]))
    winner = eligible[0]
    ruling["outcome"] = "APPROVE-WITH-CONSTANTS"
    ruling["winner"] = {"k": winner["k"], "delta": winner["delta"]}
    kw, dw = winner["k"], winner["delta"]

    rows_final, sells_final, venue_final = build_world(kw, dw, "W2")
    published = [{"species_id": r.species_id, "venue": venue_final[r.species_id], "size_rank": r.size_rank,
                  "rarity_weight": r.rarity_weight, "sell": sells_final[r.species_id], "game_xp": r.size_rank}
                 for r in rows_final]
    published.sort(key=lambda x: (x["venue"], x["size_rank"]))
    RESULTS["published_table"] = published
    check("publish:33-rows", len(published) == 33)
    check("publish:pinned-verbatim", all(sells_final[s] == PINNED[s][2] for s in PINNED))

    # ---------------- XP arm (S2) on the winning cell ----------------
    m1w = w1_cache[kw]["m"]
    m2w = measure(rows_final, sells_final, EVAL_SEEDS)
    tb = two_burst_xp(w1_cache[kw]["rows"], EVAL_SEEDS)
    xph_deep_master = m2w["deep_water/master"]["xp_per_hour"]
    p2 = all(m1w[f"{sp}/fresh"]["xp_per_hour"] < m1w[f"{sp}/geared"]["xp_per_hour"] < m1w[f"{sp}/master"]["xp_per_hour"]
             for sp in spots_mod.spot_ids())
    xp_arm = {"two_burst_xp_fresh_dock_W1": round(tb, 6), "xp_per_hour_master_deep_W2": xph_deep_master,
              "P2_gear_gradient_W1": p2, "per_s": []}
    chosen_s = None
    for s in SW["xp_arm"]["ladder_scale_grid_s"]:
        p1 = tb >= 50 * s
        hours_l25 = 15000 * s / xph_deep_master
        p3 = 24 <= hours_l25 <= 120
        xp_arm["per_s"].append({"s": s, "P1": p1, "P3": p3, "hours_to_L25": round(hours_l25, 6)})
        if chosen_s is None and p1 and p2 and p3:
            chosen_s = s
    xp_arm["chosen_s"] = chosen_s
    xp_arm["outcome"] = "APPROVE" if chosen_s is not None else "NULL-XP"
    RESULTS["xp_arm"] = xp_arm
    RESULTS["winning_cells_measured"] = {"W1": m1w, "W2": m2w}

    # ---------------- stability leg ----------------
    m1s = measure(w1_cache[kw]["rows"], w1_cache[kw]["sells"], STAB_SEEDS)
    m2s = measure(rows_final, sells_final, STAB_SEEDS)
    par_s = m1s["dock/fresh"]["coins_per_energy"]
    max_s = max([v["coins_per_energy"] for v in m1s.values()] + [v["coins_per_energy"] for v in m2s.values()])
    tb_s = two_burst_xp(w1_cache[kw]["rows"], STAB_SEEDS)
    stab = {"parity_dock_fresh_W1": par_s, "max_coins_per_energy": round(max_s, 6), "two_burst_xp": round(tb_s, 6)}
    check("stability:A1", A1_LO <= par_s <= A1_HI)
    check("stability:A3", max_s <= CEIL)
    if chosen_s is not None:
        check("stability:P1", tb_s >= 50 * chosen_s)
        h_s = 15000 * chosen_s / m2s["deep_water/master"]["xp_per_hour"]
        stab["hours_to_L25"] = round(h_s, 6)
        check("stability:P3", 24 <= h_s <= 120)
    RESULTS["stability"] = stab

RESULTS["ruling"] = ruling
RESULTS["theorem_F_STRICT"] = REG["amendment_A5"]["why_theorem_F_STRICT"]
RESULTS["seeds"] = {"eval": [EVAL_SEEDS[0], EVAL_SEEDS[-1]], "stability": [STAB_SEEDS[0], STAB_SEEDS[-1]],
                    "fleet_high_water_before": 20261388, "reserved_through_this_pr": 20261558}

# --------------------------------------------------------------------------- finish
failed = [n for n, ok in _CHECKS if not ok]
RESULTS["self_checks"] = {"passed": len(_CHECKS) - len(failed), "failed": len(failed), "failed_names": failed}
out = json.dumps(RESULTS, sort_keys=True, indent=1)
with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    fh.write(out + "\n")

print(f"naming: {RESULTS['naming_leg']['reading']}")
print(f"eligible cells: {RESULTS['eligible_count']}/32")
if "winner" in ruling:
    print(f"winner: k={ruling['winner']['k']} delta={ruling['winner']['delta']}")
    print(f"xp arm: {RESULTS['xp_arm']['outcome']} chosen_s={RESULTS['xp_arm']['chosen_s']}")
print(f"RULING: {ruling['outcome']}")
print(f"SELF-CHECKS: {len(_CHECKS) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
