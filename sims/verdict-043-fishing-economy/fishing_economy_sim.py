#!/usr/bin/env python3
"""VERDICT 043 — fishing economy tuning (idea-engine ORDER 006 item 5, seat superbot-games).

Drives the packet's own pinned sim (games/fishing/sim/catch_sim.py, byte-copied at
57f69be34785afb427d608b207e7369025166e94 — sha256 MANIFEST in fixtures/) ONLY through its
public entry point ``run(seeds=…, spots=…, casts_per_spot=…)`` per skeleton §5. ZERO edits
to any weight or constant anywhere: the candidate sell/XP curves are a pure fold over the
sim's output distributions (the "new targets" the order names). All decision arithmetic is
exact ``Fraction``; the only inputs are this sim's own fixtures.json + fixtures/ tree.

Run:  python3 sims/verdict-043-fishing-economy/fishing_economy_sim.py
"""

from __future__ import annotations

import dataclasses
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "fixtures"))

with open(os.path.join(HERE, "fixtures.json")) as fh:
    FIX = json.load(fh)["registration"]

from games.fishing.core import catch as catch_mod  # noqa: E402
from games.fishing.core import species as species_mod  # noqa: E402
from games.fishing.core.catch import Catch  # noqa: E402
from games.fishing.inventory import adapter  # noqa: E402
from games.fishing.sim import catch_sim  # noqa: E402
from games.mining.core import energy as energy_mod  # noqa: E402
from games.mining.core import market as market_mod  # noqa: E402
from games.mining.core import rewards as rewards_mod  # noqa: E402
from games.shared.inventory.interface import ProgressionDelta  # noqa: E402

PASSED = 0
FAILED = 0
LINES: list[str] = []


def say(line: str = "") -> None:
    LINES.append(line)


def check(name: str, cond: bool, detail: str = "") -> bool:
    global PASSED, FAILED
    if cond:
        PASSED += 1
    else:
        FAILED += 1
        say(f"SELF-CHECK FAIL: {name} {detail}")
    return cond


def frac(x: float) -> Fraction:
    return Fraction(x)  # every packet constant used here is binary-exact


# ---------------------------------------------------------------- B0 validity gate
def b0_gate() -> dict:
    out: dict = {}
    # B0.1 — catch_to_grant leaves ProgressionDelta empty, for every species.
    empty = ProgressionDelta()
    ok1 = all(
        adapter.catch_to_grant(Catch(sid, 20)).progression == empty
        for sid in species_mod.species_ids()
    )
    ok1 &= empty.global_xp == 0 and empty.game_xp == 0 and empty.currency == 0 and empty.capability is None
    quote = "Progression is left EMPTY: fishing's resolver defines no XP/currency for a catch today"
    ok1 &= quote in (adapter.catch_to_grant.__doc__ or "")
    check("B0.1 empty ProgressionDelta + packet quote", ok1)
    out["B0.1_empty_progression"] = ok1

    # B0.2 — species table exactly as quoted.
    want = {"minnow": (1, 50.0), "bass": (2, 30.0), "pike": (3, 15.0), "legend_carp": (4, 5.0)}
    rows = {s.species_id: (s.size_rank, s.rarity_weight) for s in species_mod.all_species()}
    ok2 = rows == want and species_mod.MAX_SIZE_RANK == 4
    check("B0.2 species size_rank/rarity_weight table", ok2, repr(rows))
    out["B0.2_species_table"] = ok2

    # B0.3 — Catch carries only species_id + size.
    names = tuple(f.name for f in dataclasses.fields(Catch))
    ok3 = names == ("species_id", "size")
    check("B0.3 Catch fields (species_id, size)", ok3, repr(names))
    out["B0.3_catch_shape"] = ok3

    # B0.4 — economy constants as quoted.
    ok4 = (
        catch_mod.CAST_COST == 2
        and energy_mod.DIG_COST == 1
        and energy_mod.REGEN_SECONDS == 10
        and energy_mod.MAX_ENERGY == 60
        and rewards_mod.BASE_ROLL_MAX == 2
        and rewards_mod.ORE_WEIGHTS == {"stone": 3, "bronze": 2.5, "iron": 2, "silver": 1.5, "gold": 1, "diamond": 0.5}
        and [market_mod.sell_price(o) for o in ("stone", "bronze", "iron", "silver", "gold", "diamond")] == [1, 2, 3, 4, 6, 12]
    )
    check("B0.4 economy constants", ok4)
    out["B0.4_economy_constants"] = ok4
    out["pass"] = ok1 and ok2 and ok3 and ok4
    return out


# ------------------------------------------------------- mining faucet derivations
def mining_grounding() -> dict:
    w0 = {k: frac(v) for k, v in rewards_mod.ORE_WEIGHTS.items()}
    vals = {o: market_mod.sell_price(o) for o in w0}
    ev0 = sum(w0[o] * vals[o] for o in w0) / sum(w0.values())
    check("mining E[value/ore] depth0 == 64/21", ev0 == Fraction(64, 21), str(ev0))
    parity = Fraction(3, 2) * ev0  # E[ore/dig fresh]=3/2, DIG_COST=1
    check("mining parity anchor == 32/7", parity == Fraction(32, 7), str(parity))
    w4 = {k: frac(v) for k, v in rewards_mod.ore_weights_for_depth(4).items()}
    ev4 = sum(w4[o] * vals[o] for o in w4) / sum(w4.values())
    check("mining E[value/ore] depth4 == 151/28", ev4 == Fraction(151, 28), str(ev4))
    e_ore_diamond = Fraction(round(1 * 1.5) + round(2 * 1.5), 2)
    ceiling = e_ore_diamond * ev4
    check("mining ceiling proxy == 755/56", ceiling == Fraction(755, 56), str(ceiling))
    return {
        "parity_anchor_coins_per_energy": str(parity),
        "coins_per_hour_sustained": str(parity * 360),
        "ceiling_proxy_coins_per_energy": str(ceiling),
    }


# ------------------------------------------------------------------ leg evaluation
CAST_COST = 2
CASTS_PER_HOUR = Fraction(3600, 10) / CAST_COST  # regen 360 energy/h ÷ 2 energy/cast = 180
CASTS_PER_BURST = 60 // CAST_COST  # a full MAX_ENERGY bar = 30 casts
RANK = {s.species_id: s.size_rank for s in species_mod.all_species()}
WEIGHT = {s.species_id: frac(s.rarity_weight) for s in species_mod.all_species()}
SIDS = tuple(species_mod.species_ids())


def curve_for_c(c: int) -> dict[str, int]:
    return {sid: round(Fraction(c) * Fraction(50) / WEIGHT[sid]) for sid in SIDS}


def coins_per_energy(st, sells: dict[str, int]) -> Fraction:
    # twin evaluators: direct coin total per energy vs bite_rate × E[sell|catch] / cost
    e1 = Fraction(sum(st.species_counts.get(sid, 0) * sells[sid] for sid in SIDS), st.casts * CAST_COST)
    if st.bites:
        esell = sum(Fraction(st.species_counts.get(sid, 0), st.bites) * sells[sid] for sid in SIDS)
        e2 = Fraction(st.bites, st.casts) * esell / CAST_COST
        check("twin coins/energy evaluators agree", e1 == e2)
    return e1


def xp_per_hour(st) -> Fraction:
    return CASTS_PER_HOUR * Fraction(sum(st.species_counts.get(sid, 0) * RANK[sid] for sid in SIDS), st.casts)


def eval_leg(report, sells: dict[str, int], parity: Fraction, ceiling: Fraction) -> dict:
    spots = list(report.spots)
    tiers = list(report.tiers)
    cpe = {(sp, t): coins_per_energy(report.spot_tier(sp, t), sells) for sp in spots for t in tiers}
    xph = {(sp, t): xp_per_hour(report.spot_tier(sp, t)) for sp in spots for t in tiers}
    a1 = Fraction(17, 20) * parity <= cpe[("dock", "fresh")] <= Fraction(21, 20) * parity
    a2 = all(cpe[(sp, "fresh")] < cpe[(sp, "geared")] < cpe[(sp, "master")] for sp in spots)
    a3 = max(cpe.values()) <= ceiling
    a4 = all(cpe[("tide_pool", t)] < cpe[("dock", t)] < cpe[("deep_water", t)] for t in tiers)
    st_df = report.spot_tier("dock", "fresh")
    two_burst_xp = 2 * CASTS_PER_BURST * Fraction(sum(st_df.species_counts.get(s, 0) * RANK[s] for s in SIDS), st_df.casts)
    p1 = two_burst_xp >= 50
    p2 = all(xph[(sp, "fresh")] < xph[(sp, "geared")] < xph[(sp, "master")] for sp in spots)
    hours_l25 = Fraction(25 * 25 * 24) / xph[("deep_water", "master")]
    p3 = 24 <= hours_l25 <= 120
    return {
        "coins_per_energy": {f"{sp}/{t}": [str(v), float(v)] for (sp, t), v in sorted(cpe.items())},
        "xp_per_hour": {f"{sp}/{t}": [str(v), float(v)] for (sp, t), v in sorted(xph.items())},
        "two_burst_xp_fresh_dock": [str(two_burst_xp), float(two_burst_xp)],
        "hours_to_level25_master_deep": [str(hours_l25), float(hours_l25)],
        "bands": {"A1": a1, "A2": a2, "A3": a3, "A4": a4, "P1": p1, "P2": p2, "P3": p3},
        "_cpe": cpe,
    }


# --------------------------------------------------------------- §5 validity anchors
DOC_BITES = {  # skeleton §5 full sim output — bite rate % (2 dp) per (spot, tier)
    ("tide_pool", "fresh"): "65.52", ("tide_pool", "geared"): "73.41", ("tide_pool", "master"): "89.41",
    ("dock", "fresh"): "54.36", ("dock", "geared"): "62.59", ("dock", "master"): "78.82",
    ("deep_water", "fresh"): "47.12", ("deep_water", "geared"): "55.11", ("deep_water", "master"): "71.34",
}
DOC_FRESH_BITES_N = {"tide_pool": 10483, "dock": 8697, "deep_water": 7539}
DOC_DOCK_FRESH_SHARES = {"minnow": "49.66", "bass": "29.90", "pike": "15.01", "legend_carp": "5.44"}
DOC_AGG_BITES = {"fresh": "55.66", "geared": "63.70", "master": "79.86"}


def anchor_checks(report) -> None:
    tol = Fraction(1, 200)  # the doc rounds to 2 dp — exact-rounding tolerance ±0.005
    for (sp, t), pct in DOC_BITES.items():
        st = report.spot_tier(sp, t)
        measured = Fraction(st.bites, st.casts) * 100
        check(f"§5 anchor bite[{sp}/{t}]", abs(measured - Fraction(pct)) <= tol, f"{float(measured):.4f} vs {pct}")
    for sp, n in DOC_FRESH_BITES_N.items():
        check(f"§5 anchor bites-count[{sp}/fresh]", report.spot_tier(sp, "fresh").bites == n)
    st = report.spot_tier("dock", "fresh")
    for sid, pct in DOC_DOCK_FRESH_SHARES.items():
        measured = Fraction(st.species_counts.get(sid, 0), st.bites) * 100
        check(f"§5 anchor dock-fresh share[{sid}]", abs(measured - Fraction(pct)) <= tol, f"{float(measured):.4f} vs {pct}")
    for t, pct in DOC_AGG_BITES.items():
        agg = report.by_tier[t]
        measured = Fraction(agg.bites, agg.casts) * 100
        check(f"§5 anchor aggregate bite[{t}]", abs(measured - Fraction(pct)) <= tol, f"{float(measured):.4f} vs {pct}")
    check("§5 anchor mean energy/cast == 2 exactly", Fraction(report.energy_cost_total, report.energy_cost_n) == CAST_COST)


# --------------------------------------------------------------------------- main
def main() -> int:
    results: dict = {"verdict": "VERDICT 043", "packet_sha": FIX["packet"]["sha"]}

    b0 = b0_gate()
    results["b0"] = {k: v for k, v in b0.items()}
    if not b0["pass"]:
        say("B0 VALIDITY GATE FAILED — verdict rules on the failed premise; no tuning arm evaluated.")
        results["decision"] = "B0-FAIL"
        finish(results)
        return 1

    ground = mining_grounding()
    results["mining_grounding"] = ground
    parity = Fraction(32, 7)
    ceiling = Fraction(755, 56)

    say("== main leg: packet §5 protocol (seeds 0-399, 3 spots, 40 casts/spot) ==")
    main_report = catch_sim.run()  # the pinned protocol, driven only via the public entry point
    check("main leg casts/tier == 48000 (§5)", main_report.casts_per_tier == 48000)
    anchor_checks(main_report)

    # Calibration rule (pre-registered): integer c in [1..20], fresh@dock coins/energy
    # closest to 32/7 without exceeding 1.05x; ties break low.
    cal_rows = []
    best_c, best_gap = None, None
    upper = Fraction(21, 20) * parity
    st_df = main_report.spot_tier("dock", "fresh")
    for c in range(1, 21):
        sells_c = curve_for_c(c)
        v = Fraction(sum(st_df.species_counts.get(s, 0) * sells_c[s] for s in SIDS), st_df.casts * CAST_COST)
        cal_rows.append({"c": c, "sells": sells_c, "fresh_dock_cpe": [str(v), float(v)], "eligible": v <= upper})
        if v <= upper:
            gap = abs(v - parity)
            if best_gap is None or gap < best_gap:
                best_c, best_gap = c, gap
    results["calibration"] = {"rows": cal_rows, "chosen_c": best_c}
    check("calibration rule picks the registered candidate c=8", best_c == FIX["candidate_sell_curve"]["candidate_c"], f"rule chose {best_c}")
    sells = curve_for_c(best_c)
    check("chosen sells == registered candidate values", sells == FIX["candidate_sell_curve"]["candidate_values"], repr(sells))
    say(f"chosen c={best_c} → sell curve {sells}")

    a5 = all(isinstance(v, int) and v >= 1 for v in sells.values()) and all(
        sells[a] < sells[b] for a, b in zip(SIDS, SIDS[1:])
    )
    check("A5 integer sanity + strictly increasing in size_rank", a5)

    main_eval = eval_leg(main_report, sells, parity, ceiling)
    main_eval["bands"]["A5"] = a5
    del main_eval["_cpe"]
    results["main_leg"] = main_eval
    say("main-leg bands: " + json.dumps(main_eval["bands"], sort_keys=True))

    say("== robustness leg: fresh seeds range(20260881, 20261281) — all above fleet high-water 20260880 ==")
    rob_report = catch_sim.run(seeds=range(20260881, 20261281))
    rob_eval = eval_leg(rob_report, sells, parity, ceiling)
    del rob_eval["_cpe"]
    results["robustness_leg"] = rob_eval
    say("robustness-leg bands: " + json.dumps(rob_eval["bands"], sort_keys=True))
    for band in ("A1", "A2", "A3", "A4", "P1", "P2", "P3"):
        check(f"robustness reproduces {band}", rob_eval["bands"][band] == main_eval["bands"][band])

    # progression identity hand-pin: cumulative formula == ladder sum
    check("XP ladder identity 25*L*(L-1) == sum(50k)", all(25 * L * (L - 1) == sum(50 * k for k in range(1, L)) for L in (2, 5, 10, 25)))
    check("cumulative XP to level 25 == 15000", 25 * 25 * 24 == 15000)

    sell_pass = all(main_eval["bands"][b] for b in ("A1", "A2", "A3", "A4", "A5")) and all(
        rob_eval["bands"][b] == main_eval["bands"][b] for b in ("A1", "A2", "A3", "A4")
    )
    prog_pass = all(main_eval["bands"][b] for b in ("P1", "P2", "P3")) and all(
        rob_eval["bands"][b] == main_eval["bands"][b] for b in ("P1", "P2", "P3")
    )
    if sell_pass and prog_pass:
        decision = "APPROVE-WITH-CONSTANTS"
    elif sell_pass or prog_pass:
        decision = "CONDITIONAL"
    else:
        decision = "NULL"
    results["decision"] = decision
    results["sell_arm_pass"] = sell_pass
    results["progression_arm_pass"] = prog_pass
    results["recommended"] = {
        "sell_curve_coins": sells,
        "xp_per_catch_game_xp": {sid: RANK[sid] for sid in SIDS},
        "level_threshold_xp_to_next": "50 * L",
        "milestone_levels": [10, 25],
    }
    results["seeds"] = {
        "main_leg": "packet §5 protocol seeds 0-399 (packet-owned constants, not registry draws)",
        "robustness_leg": "range(20260881, 20261281) — 400 fresh seeds, new fleet high-water 20261280",
    }
    say(f"DECISION: {decision} (sell arm pass={sell_pass}, progression arm pass={prog_pass})")
    finish(results)
    return 0 if FAILED == 0 else 1


def finish(results: dict) -> None:
    results["self_checks"] = {"passed": PASSED, "failed": FAILED}
    say(f"SELF-CHECKS: {PASSED} passed, {FAILED} failed")
    with open(os.path.join(HERE, "results.json"), "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("\n".join(LINES))


if __name__ == "__main__":
    raise SystemExit(main())
