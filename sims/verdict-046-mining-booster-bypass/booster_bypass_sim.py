#!/usr/bin/env python3
"""VERDICT 046 — mining booster bypass / throttle seal (idea-engine PROPOSAL 035).

Drives the byte-copied superbot-games mining core (engine/games/mining/core/*,
pinned @ 57f69be34785afb427d608b207e7369025166e94 — the SAME subtree the parent
VERDICT 042 committed; sha256 MANIFEST re-verified before import) to answer:

  Which cells of the committed-shape lever sweep — booster-admission cap
  C in {60, 75, 100, 125} effective energy per player per window x window
  semantics in {sliding-3600 s, fixed-hour} — pass ALL THREE pre-registered
  bands (SEAL 5/4 / REFILL / PACE 0.8x), with REPRICE and HYBRID cells riding
  reporting-only, and does the result land REJECT / APPROVE / NULL per the
  pre-registered rule (REJECT checked first)?

Method: rung 1 NUMERIC SIMULATION. The engine's energy/admission dynamics are
DETERMINISTIC (energy.py carries zero RNG; verified at B0), so every (cell,
policy, row) timeline is a deterministic event-driven run and every DECISION
number is exact Fraction arithmetic on its integer dig/purchase counts (the
parent's zero-decision-bearing-RNG discipline). Seeded MC legs (seeds
20261281-20261284, strictly above the fleet high-water 20261280) validate the
per-dig coin means through the engine's own roll path — self-checks, never
rulings.

Pre-registration: fixtures.json (committed before this runner existed; two
gate tolerances amended pre-run, before any execution — see git history).
One command:  python3 sims/verdict-046-mining-booster-bypass/booster_bypass_sim.py
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
F = Fraction

# --------------------------------------------------------------------------- #
# 0. Manifest re-verification BEFORE import + CPython pin.
# --------------------------------------------------------------------------- #
CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))


check("env:cpython-3.11 pinned",
      platform.python_implementation() == "CPython"
      and sys.version_info[:2] == (3, 11),
      platform.python_version())

with open(os.path.join(HERE, "engine", "MANIFEST.json"), encoding="utf-8") as fh:
    MANIFEST = json.load(fh)

for rel, want in sorted(MANIFEST["files"].items()):
    p = os.path.join(HERE, "engine", rel)
    got = hashlib.sha256(open(p, "rb").read()).hexdigest()
    check(f"manifest:{rel}", got == want, f"{got} vs {want}")

sys.path.insert(0, os.path.join(HERE, "engine"))

from games.mining.core import energy, grid, market, rewards  # noqa: E402

with open(os.path.join(HERE, "fixtures.json"), encoding="utf-8") as fh:
    FIX = json.load(fh)

R: dict = {"pin": MANIFEST["pinned_sha"], "intake": "035", "verdict": 46}

HORIZON = FIX["horizon_seconds"]
INT1 = FIX["b0_parent_anchors"]["INT_1_seconds"]
MAXE = energy.MAX_ENERGY
SHOP = FIX["b0_parent_anchors"]["shop_energy"]

# --------------------------------------------------------------------------- #
# 1. B0 VALIDITY GATE — re-derive every parent anchor exactly.
# --------------------------------------------------------------------------- #
check("B0:shop ration 20 -> 25",
      market.GEAR_SHOP["ration"] == SHOP["GEAR_SHOP_ration"] == 20
      and energy.RESTORE_VALUES["ration"] == SHOP["restore_ration"] == 25)
check("B0:shop energy drink 40 -> 50",
      market.GEAR_SHOP["energy drink"] == SHOP["GEAR_SHOP_energy_drink"] == 40
      and energy.RESTORE_VALUES["energy drink"] == SHOP["restore_energy_drink"] == 50)
check("B0:energy 60/1/10",
      (energy.MAX_ENERGY, energy.DIG_COST, energy.REGEN_SECONDS)
      == (SHOP["MAX_ENERGY"], SHOP["DIG_COST"], SHOP["REGEN_SECONDS"]) == (60, 1, 10))
check("B0:sustained 360 digs/h",
      3600 // energy.REGEN_SECONDS == 360 == SHOP["sustained_digs_per_hour"])
check("B0:energy.py has zero RNG (source scan)",
      "random" not in open(os.path.join(
          HERE, "engine", "games", "mining", "core", "energy.py")).read())

ORE_VALUES = {o: market.sell_price(o) for o in rewards.ORE_WEIGHTS}
FEATS = [(f, F(w) / 100) for f, w in grid._FEATURE_WEIGHTS]


def depth_weights(d: int) -> dict[str, Fraction]:
    out = {k: F(v) for k, v in rewards.ore_weights_for_depth(d).items()}
    tot = sum(out.values())
    return {k: v / tot for k, v in out.items()}


def base_amount_pmf(mult: float) -> dict[int, Fraction]:
    pmf: dict[int, Fraction] = {}
    n = rewards.BASE_ROLL_MAX
    for r_ in range(1, n + 1):
        a = max(1, round(r_ * mult))
        pmf[a] = pmf.get(a, F(0)) + F(1, n)
    return pmf


def per_dig_pmf(mult: float, depth: int, cells: str) -> dict[tuple[str, int], Fraction]:
    wd = depth_weights(depth)
    base = base_amount_pmf(mult)
    pmf: dict[tuple[str, int], Fraction] = {}
    feat_dist = FEATS if cells == "grid" else [(grid.CellFeature.NORMAL, F(1))]
    for feat, pf in feat_dist:
        for a, pa in base.items():
            amt = max(1, round(a * grid._RICHNESS[feat]))
            for ore, po in wd.items():
                key = (ore, amt)
                pmf[key] = pmf.get(key, F(0)) + pf * pa * po
    return pmf


def E_coins(pmf) -> Fraction:
    return sum(p * a * ORE_VALUES[o] for (o, a), p in pmf.items())


IRON_MULT = rewards.mine_multiplier({"tool": "iron pickaxe"}, {})
DIAMOND_MULT = rewards.mine_multiplier({"tool": "diamond pickaxe"}, {})
check("B0:iron mult 1.25 / diamond mult 1.5", IRON_MULT == 1.25 and DIAMOND_MULT == 1.5)

ROW_CFG = {
    "P0": dict(mult=IRON_MULT, depth=0, cells="normal"),
    "P1": dict(mult=IRON_MULT, depth=0, cells="grid"),
    "P2": dict(mult=IRON_MULT, depth=1, cells="grid"),
    "P3": dict(mult=IRON_MULT, depth=2, cells="grid"),
    "ceiling_755_56": dict(mult=DIAMOND_MULT, depth=4, cells="normal"),
}
ROW_E: dict[str, Fraction] = {
    rname: E_coins(per_dig_pmf(cfg["mult"], cfg["depth"], cfg["cells"]))
    for rname, cfg in ROW_CFG.items()
}

_pins = FIX["b0_parent_anchors"]["depth_row_E_coins_per_dig"]
for rname in ("P0", "P1", "P2", "P3"):
    check(f"B0:row {rname} == {_pins[rname]}", ROW_E[rname] == F(_pins[rname]),
          str(ROW_E[rname]))
check("B0:ceiling row == 755/56", ROW_E["ceiling_755_56"] == F(755, 56),
      str(ROW_E["ceiling_755_56"]))

E_COST = F(FIX["b0_parent_anchors"]["bypass_leg"]["coins_per_energy_committed"])
check("B0:committed coins/energy == 4/5 (both items)",
      F(market.GEAR_SHOP["ration"], energy.RESTORE_VALUES["ration"]) == E_COST
      == F(market.GEAR_SHOP["energy drink"], energy.RESTORE_VALUES["energy drink"])
      == F(4, 5))
check("B0:net/dig P3 == 7507/1150",
      ROW_E["P3"] - E_COST
      == F(FIX["b0_parent_anchors"]["bypass_leg"]["net_coins_per_dig_P3"]))
check("B0:boosted net/h P3 == 270252/23",
      (ROW_E["P3"] - E_COST) * 1800
      == F(FIX["b0_parent_anchors"]["bypass_leg"]["net_coins_per_hour_boosted_P3"]))
check("B0:bypass ratio (V042 accounting) == 37535/8427",
      (ROW_E["P3"] - E_COST) * 1800 / (ROW_E["P3"] * 360) == F(37535, 8427))
check("B0:bypass ratio (regen-credited) == 38455/8427",
      (1800 * ROW_E["P3"] - 1440 * E_COST) / (360 * ROW_E["P3"]) == F(38455, 8427))

# NP-1 composite anchors, reproduced with the parent's own accounting.
withheld_f1 = 25 * ORE_VALUES["iron"] + 15 * ORE_VALUES["stone"]
withheld_f2 = 20 * ORE_VALUES["gold"] + 10 * ORE_VALUES["iron"]
D_F1 = (F(market.GEAR_SHOP["torch"]) / ROW_E["P0"]
        + F(market.GEAR_SHOP["lantern"]) / ROW_E["P2"]
        + F(market.GEAR_SHOP["iron sword"]) / ROW_E["P3"]
        + (F(3000) + withheld_f1) / ROW_E["P3"])
D_F2 = D_F1 + (F(8000) + withheld_f2) / ROW_E["P3"]
NP1 = FIX["b0_parent_anchors"]["np1_anchors"]
check("B0:Forge I digs == 1005258865/2292144", D_F1 == F(NP1["forge_I_digs"]), str(D_F1))
check("B0:Forge II digs == 3554578865/2292144", D_F2 == F(NP1["forge_II_digs"]), str(D_F2))
T_F1 = 10 * D_F1 - 480
T_F2 = 10 * D_F2 - 480
check("B0:Forge I seconds == 4476179765/1146072 (10D-480)",
      T_F1 == F(NP1["forge_I_seconds"]), str(T_F1))
check("B0:Forge II seconds == 17222779765/1146072 (10D-480)",
      T_F2 == F(NP1["forge_II_seconds"]), str(T_F2))

check("B0:REPRICE exclusion pair 11325/896 > 48/7",
      F(15, 16) * ROW_E["ceiling_755_56"] == F(11325, 896)
      and F(2880, 7) / 60 == F(48, 7) and F(11325, 896) > F(48, 7))
check("B0:committed full-bar refill == 60 coins (drink+ration, 0 -> 60 effective)",
      market.GEAR_SHOP["energy drink"] + market.GEAR_SHOP["ration"] == 60
      and min(50, MAXE - 0) + min(25, MAXE - 50) == 60)
check("B0:fishing max 40797/4000 < 755/56 (reporting-only by arithmetic)",
      F(FIX["b0_parent_anchors"]["fishing_reporting_max_coins_per_energy"]["value"])
      < F(755, 56))

B0_OK = all(ok for _, ok, _ in CHECKS)
R["b0"] = {"pass": B0_OK, "anchors": len(CHECKS)}

# --------------------------------------------------------------------------- #
# 2. The deterministic timeline engine (energy.py drives all dynamics).
# --------------------------------------------------------------------------- #
DRINK = ("energy drink", energy.RESTORE_VALUES["energy drink"])
RATION = ("ration", energy.RESTORE_VALUES["ration"])
COMMITTED_PRICES = {"energy drink": F(market.GEAR_SHOP["energy drink"]),
                    "ration": F(market.GEAR_SHOP["ration"])}


class Admission:
    """The injected booster-admission layer (effective-energy accounting)."""

    def __init__(self, cap: int | None, semantics: str | None):
        self.cap = cap  # None = no cap (C = inf); 0 = admits nothing
        self.semantics = semantics
        self.log: list[tuple[int, int]] = []  # (t, effective energy admitted)

    def _window_sum(self, t: int) -> int:
        if self.semantics == "fixed-hour":
            start = (t // 3600) * 3600
            return sum(a for (tt, a) in self.log if start <= tt <= t)
        return sum(a for (tt, a) in self.log if t - 3600 < tt <= t)

    def remaining(self, t: int) -> int:
        if self.cap is None:
            return 10 ** 9
        if self.cap == 0:
            return 0
        return max(0, self.cap - self._window_sum(t))

    def admit(self, t: int, gain: int) -> None:
        self.log.append((t, gain))

    def next_free(self, t: int) -> int:
        if self.semantics == "fixed-hour":
            return (t // 3600 + 1) * 3600
        old = [tt for (tt, _) in self.log if tt > t - 3600]
        return (min(old) + 3601) if old else t + 1


def run_timeline(cap, semantics, prices: dict[str, Fraction], row_E: Fraction,
                 policy: str, horizon: int = HORIZON, stop_digs: int | None = None,
                 mix: str = "drink-first"):
    """One deterministic event-driven run of the byte-copied engine."""
    es = energy.EnergyState(MAXE, 0)
    adm = Admission(cap, semantics)
    t = 0
    digs = 0
    spend = F(0)
    purchases = 0
    admitted = 0
    limit = horizon if stop_digs is None else 10 ** 9

    def profitable(price: Fraction, gain: int) -> bool:
        return price < gain * row_E  # strict, registered

    def order_for(cur: int, rem: int) -> list[tuple[str, int, int]]:
        """[(item, restore, gain)] candidates per the registered greedy rules:
        (a) drink at full gain without touching the cap (cur <= 9);
        (b) ration at full gain without touching the cap (cur <= 34);
        (c) the exact residual top-up (cur == MAXE - rem, rem < 25) — the one
            deliberate cap-touch, needed to exhaust C = 60's residual 10.
        Mix variants permute (a)/(b) for the invariance gate."""
        cands = []
        a = (DRINK[0], DRINK[1], min(DRINK[1], MAXE - cur))
        b = (RATION[0], RATION[1], min(RATION[1], MAXE - cur))
        if mix == "ration-only":
            if rem >= b[2] == 25 and cur <= 34:
                cands.append(b)
            if rem >= 50 and cur <= 9 and not cands:
                cands.append(b)  # rations still; drink never
        else:
            first, second = (a, b) if (mix == "drink-first" or purchases % 2 == 0) \
                else (b, a)
            if rem >= first[2] and ((first is a and cur <= 9) or (first is b and cur <= 34)):
                cands.append(first)
            elif rem >= second[2] and ((second is a and cur <= 9) or (second is b and cur <= 34)):
                cands.append(second)
        if 0 < rem < 25 and cur == MAXE - rem:
            cands.append((RATION[0], RATION[1], rem))  # (c) residual top-up
        return cands

    def try_buy(now: int) -> bool:
        nonlocal es, spend, purchases, admitted
        cur = energy.settle(es, now).current
        rem = adm.remaining(now)
        if rem <= 0:
            return False
        rem_digs = (limit - now) // INT1 if stop_digs is None else 10 ** 9
        for name, restore, gain in order_for(cur, rem):
            if gain <= 0 or gain > rem or cur + gain > max(0, rem_digs):
                continue
            price = prices[name]
            if not profitable(price, gain):
                continue
            es = energy.restore(es, now, restore)
            adm.admit(now, gain)
            spend += price
            purchases += 1
            admitted += gain
            return True
        return False

    def gamer_buy_allowed(now: int) -> bool:
        # BOUNDARY-GAMER: even fixed windows defer purchases to the last 10 s;
        # odd windows buy normally (front-loaded) -> back-to-back bursts.
        win = now // 3600
        if win % 2 == 0:
            return (now % 3600) >= 3590
        return True

    while True:
        if stop_digs is not None and digs >= stop_digs:
            break
        if stop_digs is None and t >= horizon:
            break
        if policy == "HONEST-CASUAL" and (t % 3600) >= 1800:
            t = (t // 3600 + 1) * 3600
            continue
        if policy == "BOOST-FARMER" or (policy == "BOUNDARY-GAMER" and gamer_buy_allowed(t)):
            while try_buy(t):
                pass
        elif policy == "HONEST-CASUAL":
            cur0 = energy.settle(es, t).current
            hour_start = (t // 3600) * 3600
            if cur0 == 0 and not any(tt >= hour_start for (tt, _) in adm.log):
                # the registered full-bar bundle: drink at 0, ration on top
                for name, restore in (DRINK, RATION):
                    cur = energy.settle(es, t).current
                    gain = min(restore, MAXE - cur)
                    if gain > 0 and gain <= adm.remaining(t) \
                            and profitable(prices[name], gain):
                        es = energy.restore(es, t, restore)
                        adm.admit(t, gain)
                        spend += prices[name]
                        purchases += 1
                        admitted += gain
        cur = energy.settle(es, t).current
        if policy == "BOOST-FARMER" and isinstance(cap, int) and cap > 0:
            # HOLD-TO-TOP-UP (the registered greedy adversary's exhaust move):
            # a residual 0 < rem < 25 is only admissible at cur == MAXE - rem
            # (partial ration gain); holding digs (they are regen-bound, not
            # lost) until regen lifts cur there strictly gains rem extra digs.
            rem = adm.remaining(t)
            if 0 < rem < 25 and 1 <= cur < MAXE - rem \
                    and prices["ration"] < rem * row_E:
                t += max(1, energy.seconds_until(es, t, MAXE - rem))
                continue
        if cur >= 1:
            es = energy.spend(es, t)
            digs += 1
            t += INT1
            continue
        wait_regen = energy.seconds_until(es, t, 1)
        nxt = t + max(1, wait_regen)
        if policy in ("BOOST-FARMER", "BOUNDARY-GAMER") and cap not in (None, 0):
            nxt = min(nxt, max(t + 1, adm.next_free(t)))
        if policy == "BOUNDARY-GAMER":
            win_gate = (t // 3600) * 3600 + 3590
            if (t // 3600) % 2 == 0 and win_gate > t:
                nxt = min(nxt, win_gate)
        t = nxt

    end_t = t if stop_digs is not None else horizon
    return {"digs": digs, "admitted": admitted, "purchases": purchases,
            "spend": spend, "seconds": end_t, "log": adm.log}


def peak_window_admitted(log: list[tuple[int, int]]) -> int:
    """Independent re-audit (written separately from Admission): max admitted
    effective energy over ALL trailing closed 3600 s windows [t0, t0+3599]."""
    best = 0
    for (t0, _) in log:
        s = sum(a for (tt, a) in log if t0 <= tt <= t0 + 3599)
        best = max(best, s)
    return best


def prices_at(e: Fraction) -> dict[str, Fraction]:
    """REPRICE: items repriced to e coins per NOMINAL energy unit."""
    return {"energy drink": e * 50, "ration": e * 25}


def _cascade(C: int) -> list[tuple[Fraction, int]]:
    """Arm-A fluid model of the window-0 purchase cascade: the bar descends at
    2/5 energy/s net; rations land at cur 34 every 62.5 s from t = 65, the
    residual top-up (C mod 25) lands 22.5 s after the last full item."""
    n_full, partial = divmod(C, 25)
    ev = [(F(65) + F(125, 2) * j, 25) for j in range(n_full)]
    if partial:
        ev.append(((ev[-1][0] + F(45, 2)) if ev else F(65), partial))
    return ev


def fluid_ladder_seconds(D: Fraction, C: int, semantics: str) -> Fraction:
    """Arm-A fluid predictor. Window 0 supplies C via the purchase cascade;
    later windows: fixed-hour re-arms in full at 3600k, sliding re-arms each
    window-0 purchase 3600 s after it aged in. Dig at 1/2 digs/s on backlog,
    1/10 regen-paced otherwise. Pre-registered engine agreement +-180 s."""
    cas = _cascade(C)
    events: list[tuple[Fraction, int]] = list(cas)
    for k in range(1, 12):
        if semantics == "fixed-hour":
            events.append((F(3600 * k), C))
        else:
            events.extend((tt + 3600 * k, g) for tt, g in cas)
    events.sort()
    t, dug = F(0), F(0)
    while dug < D:
        supply = 60 + t / 10 + sum(g for (te, g) in events if te <= t)
        nxt_evt = min((te for (te, _) in events if te > t), default=None)
        if dug < supply:
            gap_close = t + (supply - dug) / F(2, 5)
            t_reach = t + (D - dug) * 2
            tn = min(x for x in (gap_close, t_reach, nxt_evt) if x is not None)
            dug += (tn - t) / 2
        else:
            t_reach = t + (D - dug) * 10
            tn = min(x for x in (t_reach, nxt_evt) if x is not None)
            dug += (tn - t) / 10
        t = tn
    return t


# --------------------------------------------------------------------------- #
# 3. Control + identity cells.
# --------------------------------------------------------------------------- #
control = run_timeline(0, None, COMMITTED_PRICES, ROW_E["P3"], "THROTTLED")
CTRL_DIGS = control["digs"]
lo, hi = FIX["closed_form_predictions_pre_run"]["control_digs_8h_band"]
check(f"gate:control digs in [{lo},{hi}]", lo <= CTRL_DIGS <= hi, str(CTRL_DIGS))
check("gate:control admits nothing", control["admitted"] == 0 and control["spend"] == 0)

SEMS = ["sliding-3600s", "fixed-hour"]
identity_cells = {}
for sem in SEMS:
    z = run_timeline(0, sem, COMMITTED_PRICES, ROW_E["ceiling_755_56"], "BOOST-FARMER")
    check(f"gate:C=0 {sem} == throttled control",
          z["digs"] == CTRL_DIGS and z["admitted"] == 0 and z["spend"] == 0, str(z["digs"]))
    inf = run_timeline(None, sem, COMMITTED_PRICES, ROW_E["ceiling_755_56"], "BOOST-FARMER")
    # The registered adversary buys only what the remaining horizon can dig
    # (fixtures policies.BOOST-FARMER), so the final <60 s of INT-1 slots go
    # unboosted: the 1800/h identity holds up to that terminal absorption.
    check(f"gate:C=inf {sem} digs == 14400 - terminal absorption (in [14380,14400])",
          14380 <= inf["digs"] <= HORIZON // INT1 == 14400, str(inf["digs"]))
    check(f"gate:C=inf {sem} purchased == digs - control (regen preserved)",
          inf["admitted"] == inf["digs"] - CTRL_DIGS,
          f"{inf['admitted']} vs {inf['digs'] - CTRL_DIGS}")
    identity_cells[f"C0_{sem}"] = {"digs": z["digs"], "admitted": 0}
    identity_cells[f"Cinf_{sem}"] = {"digs": inf["digs"], "admitted": inf["admitted"],
                                     "spend_coins": str(inf["spend"])}
R["identity_cells"] = identity_cells

# --------------------------------------------------------------------------- #
# 4. DECISION CELLS — 8 (C x semantics) + bands.
# --------------------------------------------------------------------------- #
ROWS = list(ROW_CFG.keys())
C_GRID = FIX["cells"]["decision_C_grid"]
SEAL_T = F(5, 4)
PACE_T = F(4, 5)
REFILL_BAR = F(FIX["bands"]["REFILL"]["coin_threshold"])
ctrl_net = {rname: CTRL_DIGS * ROW_E[rname] for rname in ROWS}


def build_decision_cells() -> dict:
    cells = {}
    for sem in SEMS:
        for C in C_GRID:
            run = run_timeline(C, sem, COMMITTED_PRICES, ROW_E["ceiling_755_56"],
                               "BOOST-FARMER")
            delta = CTRL_DIGS + run["admitted"] - run["digs"]
            band = 8 if C % 25 != 0 else 0  # (c) residual top-up cap-touches
            check(f"gate:farmer identity digs==control+admitted-delta ({sem},C={C})",
                  0 <= delta <= band, f"delta {delta} (band [0,{band}])")
            check(f"gate:admitted == 8*C ({sem},C={C})", run["admitted"] == 8 * C,
                  str(run["admitted"]))
            peak = peak_window_admitted(run["log"])
            if sem == "sliding-3600s":
                check(f"gate:sliding re-audit peak <= C ({sem},C={C})", peak <= C,
                      str(peak))
            rows_tab = {}
            seal_all = True
            for rname in ROWS:
                # committed prices are profitable at full AND top-up gains on
                # every row, so the ceiling-row timeline is row-invariant at
                # these cells (asserted for the top-up: 20 < 10*E for all rows)
                net = run["digs"] * ROW_E[rname] - run["spend"]
                rho = net / ctrl_net[rname]
                cf = 1 + C * (ROW_E[rname] - E_COST) / (360 * ROW_E[rname])
                rows_tab[rname] = {
                    "net_coins_per_h": str(net / 8),
                    "net_coins_per_h_float": round(float(net / 8), 2),
                    "rho_vs_control": str(rho), "rho_float": round(float(rho), 4),
                    "rho_closed_form": str(cf),
                    "premium": round(float(rho - cf), 4),
                    "SEAL_pass": bool(rho <= SEAL_T),
                }
                seal_all = seal_all and rho <= SEAL_T
            refill_ok = C >= 60
            refill_cost = COMMITTED_PRICES["energy drink"] + COMMITTED_PRICES["ration"]
            refill_pass = bool(refill_ok and refill_cost <= REFILL_BAR)
            ladder = {}
            pace_all = True
            for fname, Dfrac, Tanchor in (("forge_I", D_F1, T_F1),
                                          ("forge_II", D_F2, T_F2)):
                lrun = run_timeline(C, sem, COMMITTED_PRICES, ROW_E["ceiling_755_56"],
                                    "BOOST-FARMER", stop_digs=math.ceil(Dfrac))
                secs = lrun["seconds"]
                fluid = fluid_ladder_seconds(Dfrac, C, sem)
                check(f"gate:ladder fluid agreement ({sem},C={C},{fname}) +-180s",
                      abs(secs - fluid) <= 180,
                      f"engine {secs} vs fluid {float(fluid):.1f}")
                ratio = F(secs) / Tanchor
                ladder[fname] = {"engine_seconds": secs,
                                 "fluid_seconds_float": round(float(fluid), 1),
                                 "throttled_anchor_seconds": str(Tanchor),
                                 "sustained_rate_prediction": round(
                                     float((120 + (Dfrac - 60) * F(3600, 360 + C))
                                           / Tanchor), 4),
                                 "ratio": round(float(ratio), 4),
                                 "ratio_frac": str(ratio),
                                 "PACE_pass": bool(ratio >= PACE_T)}
                pace_all = pace_all and ratio >= PACE_T
            cells[f"{sem}|C={C}"] = {
                "C": C, "semantics": sem, "digs": run["digs"],
                "admitted": run["admitted"], "purchases": run["purchases"],
                "spend_coins": str(run["spend"]),
                "peak_trailing_3600s_admitted": peak,
                "rows": rows_tab, "ladder": ladder,
                "SEAL": bool(seal_all),
                "REFILL": {"full_bar_within_window": bool(refill_ok),
                           "cost_coins": str(refill_cost), "pass": refill_pass},
                "PACE": bool(pace_all),
                "passes_all_three": bool(seal_all and refill_pass and pace_all),
            }
    return cells


# assert the row-invariance premise used above (top-up profitable everywhere)
check("gate:top-up profitable at every row (20 < 10*E)",
      all(F(20) < 10 * ROW_E[r] for r in ROWS))

decision = build_decision_cells()
R["decision_cells"] = decision

# Drink-mix invariance gate at (sliding, C=75).
mixes = {}
for mix in ("drink-first", "ration-only", "alternating"):
    m = run_timeline(75, "sliding-3600s", COMMITTED_PRICES, ROW_E["ceiling_755_56"],
                     "BOOST-FARMER", mix=mix)
    mixes[mix] = (m["digs"], m["admitted"], str(m["spend"]), m["purchases"])
check("gate:drink-mix invariance (digs/admitted/spend equal; action counts may differ)",
      len({(v[0], v[1], v[2]) for v in mixes.values()}) == 1, str(mixes))
R["drink_mix_invariance"] = {k: {"digs": v[0], "admitted": v[1], "spend": v[2],
                                 "purchase_actions": v[3]} for k, v in mixes.items()}

# Affordability gate (exact, post-hoc): worst case = P0 row.
for key, cell in decision.items():
    check(f"gate:affordability ({key})",
          F(cell["spend_coins"]) <= cell["digs"] * ROW_E["P0"],
          f"{cell['spend_coins']} vs {float(cell['digs'] * ROW_E['P0']):.0f}")

# --------------------------------------------------------------------------- #
# 5. BOUNDARY-GAMER reporting leg (fixed-hour worst-window premium).
# --------------------------------------------------------------------------- #
bg = {}
E_CEIL = ROW_E["ceiling_755_56"]
for C in C_GRID:
    g = run_timeline(C, "fixed-hour", COMMITTED_PRICES, E_CEIL, "BOUNDARY-GAMER")
    peak = peak_window_admitted(g["log"])
    peak_rho = 1 + peak * (E_CEIL - E_COST) / (360 * E_CEIL)
    farmer_peak = decision[f"fixed-hour|C={C}"]["peak_trailing_3600s_admitted"]
    bg[f"C={C}"] = {"digs": g["digs"], "admitted": g["admitted"],
                    "peak_trailing_3600s_admitted": peak,
                    "asap_farmer_peak": farmer_peak,
                    "sliding_audited_ceiling": C,
                    "peak_window_rho_ceiling": round(float(peak_rho), 4),
                    "note": "2C is the naive bound; the 60-energy bar caps an instantaneous burst, so the measured peak lands near C + 60"}
R["boundary_gamer_fixed_hour"] = bg

# --------------------------------------------------------------------------- #
# 6. HONEST-CASUAL reporting leg (convenience preservation).
# --------------------------------------------------------------------------- #
cas = {}
cas_uncapped = run_timeline(None, "sliding-3600s", COMMITTED_PRICES, ROW_E["P1"],
                            "HONEST-CASUAL")
for sem in SEMS:
    for C in C_GRID:
        c = run_timeline(C, sem, COMMITTED_PRICES, ROW_E["P1"], "HONEST-CASUAL")
        cas[f"{sem}|C={C}"] = (c["digs"], c["admitted"], str(c["spend"]))
allsame = len(set(cas.values())) == 1
check("casual:immune at EVERY decision cell (== uncapped)",
      allsame and list(cas.values())[0][0] == cas_uncapped["digs"],
      f"{sorted(set(cas.values()))} vs uncapped {cas_uncapped['digs']}")
R["honest_casual"] = {"per_cell_identical": bool(allsame),
                      "digs_8h": cas_uncapped["digs"],
                      "admitted_8h": cas_uncapped["admitted"],
                      "spend_8h_coins": str(cas_uncapped["spend"]),
                      "refills": cas_uncapped["purchases"]}

# --------------------------------------------------------------------------- #
# 7. REPRICE + HYBRID reporting cells.
# --------------------------------------------------------------------------- #
reprice = {}
for e_str in FIX["cells"]["reprice_e_grid"]:
    e = F(e_str)
    pr = prices_at(e)
    rows_tab = {}
    for rname in ROWS:
        run = run_timeline(None, "sliding-3600s", pr, ROW_E[rname], "BOOST-FARMER")
        net = run["digs"] * ROW_E[rname] - run["spend"]
        rho = net / ctrl_net[rname]
        rows_tab[rname] = {"digs": run["digs"],
                           "rho_vs_control": round(float(rho), 4),
                           "buys": bool(run["admitted"] > 0),
                           "SEAL_pass": bool(rho <= SEAL_T)}
    refill_60e = 60 * e
    reprice[e_str] = {
        "rows": rows_tab,
        "SEAL_all_rows": bool(all(v["SEAL_pass"] for v in rows_tab.values())),
        "refill_cost_60e": str(refill_60e),
        "refill_cost_75e_committed_granularity": str(75 * e),
        "REFILL_pass_60e": bool(refill_60e <= REFILL_BAR),
    }
check("reprice:registered exclusion realized (no e passes SEAL-at-every-row AND REFILL)",
      not any(v["SEAL_all_rows"] and v["REFILL_pass_60e"] for v in reprice.values()),
      str({k: (v["SEAL_all_rows"], v["REFILL_pass_60e"]) for k, v in reprice.items()}))
R["reprice_reporting"] = reprice

hy = FIX["cells"]["hybrid"]
hrun = run_timeline(hy["C"], hy["semantics"], prices_at(F(hy["e"])), E_CEIL,
                    "BOOST-FARMER")
hnet = hrun["digs"] * E_CEIL - hrun["spend"]
R["hybrid_reporting"] = {"cell": hy, "digs": hrun["digs"], "admitted": hrun["admitted"],
                         "rho_ceiling": round(float(hnet / ctrl_net["ceiling_755_56"]), 4)}

# --------------------------------------------------------------------------- #
# 8. TWIN DECISION EVALUATORS + ruling.
# --------------------------------------------------------------------------- #
def evaluator_fraction(cells: dict) -> tuple[str, list[str]]:
    """Evaluator A — exact Fractions, reads the band flags' raw fractions."""
    passing = []
    for k, c in cells.items():
        seal = all(F(v["rho_vs_control"]) <= F(5, 4) for v in c["rows"].values())
        refl = c["REFILL"]["full_bar_within_window"] \
            and F(c["REFILL"]["cost_coins"]) <= F(2880, 7)
        pace = all(F(v["ratio_frac"]) >= F(4, 5) for v in c["ladder"].values())
        if seal and refl and pace:
            passing.append(k)
    by_sem: dict[str, int] = {}
    for k in passing:
        by_sem[k.split("|")[0]] = by_sem.get(k.split("|")[0], 0) + 1
    if not passing:
        return "reject", sorted(passing)
    if any(n >= 2 for n in by_sem.values()):
        return "approve", sorted(passing)
    return "null", sorted(passing)


def evaluator_float(cells: dict) -> tuple[str, list[str]]:
    """Evaluator B — independently written, float arithmetic on raw counts."""
    passing = []
    for k, c in cells.items():
        ctrl_coins = {r: CTRL_DIGS * float(ROW_E[r]) for r in ROWS}
        seal = True
        for r in ROWS:
            net = c["digs"] * float(ROW_E[r]) - float(F(c["spend_coins"]))
            seal = seal and (net / ctrl_coins[r] <= 1.25 + 1e-12)
        refl = c["C"] >= 60 and float(F(c["REFILL"]["cost_coins"])) <= 2880.0 / 7 + 1e-9
        pace = all(v["engine_seconds"] / float(F(v["throttled_anchor_seconds"]))
                   >= 0.8 - 1e-12 for v in c["ladder"].values())
        if seal and refl and pace:
            passing.append(k)
    sems = [k.split("|")[0] for k in passing]
    if not passing:
        return "reject", sorted(passing)
    if any(sems.count(s) >= 2 for s in set(sems)):
        return "approve", sorted(passing)
    return "null", sorted(passing)


rule_a, pass_a = evaluator_fraction(decision)
rule_b, pass_b = evaluator_float(decision)
check("gate:twin evaluators agree (main)", rule_a == rule_b and pass_a == pass_b,
      f"{rule_a}/{pass_a} vs {rule_b}/{pass_b}")
RULING = rule_a
R["passing_cells"] = pass_a

# --------------------------------------------------------------------------- #
# 9. MC VALIDATION LEGS (seeded; self-checks, never rulings).
# --------------------------------------------------------------------------- #
def mc_row_mean(rng: random.Random, cfg: dict, n: int) -> Fraction:
    wd = rewards.ore_weights_for_depth(cfg["depth"])
    ores, ws = list(wd.keys()), list(wd.values())
    feat_names = [f for f, _ in grid._FEATURE_WEIGHTS]
    feat_ws = [w for _, w in grid._FEATURE_WEIGHTS]
    total = 0
    for _ in range(n):
        found, amt = rewards.roll_mine_loot(
            has_pickaxe=False, depth=cfg["depth"], multiplier=cfg["mult"], rng=rng)
        if cfg["cells"] == "grid":
            feat = rng.choices(feat_names, weights=feat_ws, k=1)[0]
            featured = rng.choices(ores, weights=ws, k=1)[0]
            cell = grid.Cell(0, 0, cfg["depth"], feat, featured, grid._RICHNESS[feat])
            found, amt, _n = grid.apply_cell_to_loot(cell, found, amt)
        total += amt * ORE_VALUES[found]
    return F(total, n)


SEEDS = FIX["seeds"]
mc = {"rows": {}, "cells": {}}
rng_aux = random.Random(SEEDS["aux"])
N_ROW = FIX["M_replications"]["row_validation_N"]
for rname, cfg in ROW_CFG.items():
    mean = mc_row_mean(rng_aux, cfg, N_ROW)
    rel = abs(mean - ROW_E[rname]) / ROW_E[rname]
    check(f"mc:row {rname} within 0.01", rel <= F(1, 100), f"rel {float(rel):.5f}")
    mc["rows"][rname] = {"N": N_ROW, "mc_mean": str(mean), "exact": str(ROW_E[rname]),
                         "rel_err": round(float(rel), 6)}

rng_main = random.Random(SEEDS["main"])
M_MAIN = FIX["M_replications"]["main"]
ccfg = ROW_CFG["ceiling_755_56"]
for sem in SEMS:
    for C in C_GRID:
        d = decision[f"{sem}|C={C}"]["digs"]
        # per-dig rewards are i.i.d. and independent of the deterministic
        # timeline, so M replicates x d digs collapse to one M*d-draw stream
        mean = mc_row_mean(rng_main, ccfg, M_MAIN * d)
        rel = abs(mean - ROW_E["ceiling_755_56"]) / ROW_E["ceiling_755_56"]
        check(f"mc:cell ({sem},C={C}) M=400 ceiling within 0.01", rel <= F(1, 100),
              f"rel {float(rel):.6f}")
        mc["cells"][f"{sem}|C={C}"] = {"M": M_MAIN, "draws": M_MAIN * d,
                                       "mc_mean": str(mean),
                                       "rel_err": round(float(rel), 6)}
R["mc_validation"] = mc

# STABILITY leg — fresh seed at half M + a full from-scratch rebuild of the
# decision table; must reproduce the ruling through BOTH evaluators.
rng_stab = random.Random(SEEDS["stability"])
M_STAB = FIX["M_replications"]["stability"]
stab_ok = True
for sem in SEMS:
    for C in C_GRID:
        d = decision[f"{sem}|C={C}"]["digs"]
        mean = mc_row_mean(rng_stab, ccfg, M_STAB * d)
        rel = abs(mean - ROW_E["ceiling_755_56"]) / ROW_E["ceiling_755_56"]
        stab_ok = stab_ok and rel <= F(1, 100)
_n_checks_before = len(CHECKS)
decision_stab = build_decision_cells()
CHECKS[:] = CHECKS[:_n_checks_before]  # rebuild re-ran per-cell gates; dedup
check("gate:stability rebuild == main decision table",
      json.dumps(decision_stab, sort_keys=True, default=str)
      == json.dumps(decision, sort_keys=True, default=str))
s_a, sp_a = evaluator_fraction(decision_stab)
s_b, sp_b = evaluator_float(decision_stab)
check("gate:stability leg reproduces the ruling (fresh-seed MC + twin evaluators)",
      stab_ok and s_a == RULING and s_b == RULING and sp_a == pass_a,
      f"{s_a}/{s_b} mc_ok={stab_ok}")
R["stability"] = {"seed": SEEDS["stability"], "M": M_STAB,
                  "reproduces_ruling": bool(stab_ok and s_a == RULING),
                  "ruling": s_a}

rng_rep = random.Random(SEEDS["reporting"])
mean_rep = mc_row_mean(rng_rep, ROW_CFG["P3"], 20000)
rel_rep = abs(mean_rep - ROW_E["P3"]) / ROW_E["P3"]
check("mc:reporting seed P3 within 0.01", rel_rep <= F(1, 100), f"{float(rel_rep):.5f}")

# --------------------------------------------------------------------------- #
# 10. Ruling + emit.
# --------------------------------------------------------------------------- #
failed = [(n, d) for n, ok, d in CHECKS if not ok]
if failed:
    RULING = "null (VALIDITY FAILURE)"
R["ruling"] = RULING
R["control"] = {"digs_8h": CTRL_DIGS,
                "net_coins_per_h": {r: str(v / 8) for r, v in ctrl_net.items()}}
R["self_checks"] = {"passed": len(CHECKS) - len(failed), "failed": len(failed),
                    "failures": [{"name": n, "detail": d} for n, d in failed]}
R["seeds"] = dict(main=SEEDS["main"], stability=SEEDS["stability"],
                  reporting=SEEDS["reporting"], aux=SEEDS["aux"],
                  new_high_water=20261284)

out = json.dumps(R, indent=2, sort_keys=True)
with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    fh.write(out + "\n")

print(f"VERDICT 046 mining-booster-bypass @ {MANIFEST['pinned_sha'][:8]}")
print(f"B0 validity gate: {'PASS' if B0_OK else 'FAIL'} ({R['b0']['anchors']} anchors)")
print(f"control (throttled, 8h): {CTRL_DIGS} digs")
for key, c in decision.items():
    rc = c["rows"]["ceiling_755_56"]
    print(f"  {key}: rho(ceiling) {rc['rho_float']}"
          f" (cf {float(F(rc['rho_closed_form'])):.4f})"
          f" SEAL={'P' if c['SEAL'] else 'F'}"
          f" REFILL={'P' if c['REFILL']['pass'] else 'F'}"
          f" PACE={'P' if c['PACE'] else 'F'}"
          f" (FI {c['ladder']['forge_I']['ratio']}"
          f" / FII {c['ladder']['forge_II']['ratio']})"
          f" -> {'PASS' if c['passes_all_three'] else 'fail'}")
print(f"passing cells: {pass_a}")
print("boundary-gamer peak-window admitted (fixed-hour): "
      + ", ".join(f"C={C}:{bg[f'C={C}']['peak_trailing_3600s_admitted']}"
                  for C in C_GRID))
print(f"casual: {'immune (identical at every cell)' if allsame else 'AFFECTED'} — "
      f"{cas_uncapped['digs']} digs/8h of 30-min sessions,"
      f" {cas_uncapped['purchases']} refill purchases")
print("reprice (reporting): " + ", ".join(
    f"e={k}: SEAL_all={v['SEAL_all_rows']} REFILL_60e={v['REFILL_pass_60e']}"
    for k, v in reprice.items()))
print(f"RULING: {RULING}")
print(f"SELF-CHECKS: {len(CHECKS) - len(failed)} passed, {len(failed)} failed")
for n, d in failed:
    print(f"  FAILED: {n} ({d})")
sys.exit(1 if failed else 0)
