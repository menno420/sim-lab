#!/usr/bin/env python3
"""VERDICT 070 — prestige reset-policy optimality (INTAKE 059 / idea-engine PROPOSAL 059).

Does superbot-idle's committed "optimal-play" greedy reset loop (fixed-1)
survive the milestone fold the engine ships at HEAD 5ddd5a2? A pre-registered,
fully deterministic, exact-integer 15-policy grid over H = 1,209,600 s.

Arms:
  Arm A — seedless exact event scheduling (DECISION-bearing).
  Arm B — independently written per-second twin evaluator; must reproduce
          every Arm-A total EXACTLY (F6).
  Arm R — seeded REPORTING-ONLY random-policy probes; no statistical gate
          rides Arm R; a probe beating the Pi-best is a named finding,
          never a ruling.

Seeds: 20261373 Arm-R main (12 hybrid triggers randrange(1,60001) then
6 cooldowns randrange(30,7201)); 20261374 stability (4+2, same grammar);
20261375 presentation shuffle ONLY; 20261376 aux, NEVER read (asserted).

Pre-registered rule evaluated IN ORDER: REJECT -> INVALID -> APPROVE -> NULL.
REJECT: exists pi in Pi \\ {fixed-1}: 100*total(pi) >= 101*total(fixed-1),
exact big-int, Arm A reproduced exactly by Arm B (fixture choice C9), with
the mechanism-miss NULL axis evaluated on the argmax beater (choice C4).

Hermetic: this runner reads ONLY its own fixtures.json. No network, no repo
reads. stdout and results.json must be byte-identical across two process
runs (verified externally by sha256). CPython minor pinned: 3.11.

Drafter-disclosed landing (PROPOSAL 059) is re-derived from scratch and
compared for the record — NEVER gated.
"""

import hashlib
import json
import os
import random
import sys
from fractions import Fraction
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- self-checks
CHECKS = {"passed": 0, "failed": 0, "failures": []}


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        CHECKS["failures"].append(name)
        print(f"SELF-CHECK FAIL: {name}")
    return bool(cond)


# ---------------------------------------------------------------- fixtures
with open(os.path.join(HERE, "fixtures.json"), "rb") as fh:
    _FIX_BYTES = fh.read()
FIX = json.loads(_FIX_BYTES)
FIX_SHA = hashlib.sha256(_FIX_BYTES).hexdigest()

W = FIX["world"]
BASE_RATE = W["generator"]["base_rate"]
COUNT = W["generator"]["count_fixed"]
THEME = W["theme_pct_neutral"]
UP_BASE = W["upgrade"]["base_cost"]
UP_NUM = W["upgrade"]["cost_growth_num"]
UP_DEN = W["upgrade"]["cost_growth_den"]
UP_EFF = W["upgrade"]["effect_percent_additive"]
P_THRESH = W["prestige"]["threshold"]
P_DIV = W["prestige"]["award_divisor"]
P_BONUS = W["prestige"]["bonus_percent_per_unit"]
MS_LT = tuple(W["milestones"]["lifetime_thresholds"])
MS_PT = tuple(W["milestones"]["prestige_thresholds"])
MS_OWN = tuple(W["milestones"]["owned_thresholds"])
MS_BONUS = W["milestones"]["bonus_percent_each"]
FOLD_DIV = W["fold"]["fold_divisor"]
H = W["horizon_s"]
H2 = W["half_horizon_s"]
POLICIES = [(p["name"], p["kind"], p["param"]) for p in FIX["policies"]]
NAMES = [p[0] for p in POLICIES]
SEEDS = FIX["seeds"]
REJ_N, REJ_D = FIX["decision"]["reject_line_num_den"]
APP_N, APP_D = FIX["decision"]["approve_line_num_den"]
GRIND = FIX["decision"]["grind_multiple"]

check("cpython-minor-pinned-3.11", list(sys.version_info[:2]) == FIX["meta"]["cpython_minor_pinned"])
check("fixtures-horizon-is-14-days", H == 14 * 86_400)
check("fixtures-half-horizon", H2 * 2 == H)
check("fixtures-threshold-equals-divisor", P_THRESH == P_DIV)
check("fixtures-15-policies", len(POLICIES) == 15 and NAMES[1] == "fixed-1")
check("fixtures-seeds-distinct-ascending",
      SEEDS["arm_r_main"] < SEEDS["arm_r_stability"] < SEEDS["presentation"] < SEEDS["aux_reserved_never_read"]
      and SEEDS["arm_r_main"] > SEEDS["high_water_below"])
check("fixtures-decision-constants", (REJ_N, REJ_D, APP_N, APP_D, GRIND) == (101, 100, 99, 100, 2))

# ---------------------------------------------------------------- Arm A engine
_COSTS_A = [UP_BASE * UP_NUM ** L // UP_DEN ** L for L in range(128)]


def _cost_a(L):
    while L >= len(_COSTS_A):
        n = len(_COSTS_A)
        _COSTS_A.append(UP_BASE * UP_NUM ** n // UP_DEN ** n)
    return _COSTS_A[L]


def _fold_a(L, P, ms):
    return (BASE_RATE * COUNT * (100 + UP_EFF * L) * (100 + P_BONUS * P)
            * (100 + MS_BONUS * ms) * THEME) // FOLD_DIV


MAX_EVENTS = 6_000_000


def arm_a(kind, param, horizon, ms_on, record_purchases=False):
    """Exact event-scheduled evaluator (decision arm). Seedless.

    Events (fixture choice C2): purchase affordability, next unearned
    lifetime-milestone crossing (ms_on only), policy reset event. The full
    pinned boundary sequence (award/buy/award/reset/award) runs at every
    boundary strictly before the horizon (choice C1).
    """
    t = 0
    bal = 0
    life = 0
    L = 0
    P = 0
    ms = 0
    lt_i = 0
    pt_i = 0
    run_start = 0
    total = 0
    spend = 0
    closed = 0
    conserve = True
    n_resets = 0
    first3 = []
    last3 = []
    dur_min = None
    dur_max = None
    dur_final = None
    days = (horizon + 86_399) // 86_400
    day_bins = [0] * days
    series_h = hashlib.sha256()
    ms_tl = []
    purchases = [] if record_purchases else None
    detour_active = False
    detour_used = False
    detour = None
    events = 0
    big = horizon + 1  # sentinel event time beyond horizon

    while t < horizon:
        events += 1
        if events > MAX_EVENTS:
            raise RuntimeError(f"event budget exceeded ({kind},{param})")
        rate = _fold_a(L, P, ms)
        if rate <= 0:
            raise RuntimeError(f"production stalled at rate 0 (t={t})")
        # next event (all strictly > t at loop top)
        nxt = t + (_cost_a(L) - bal + rate - 1) // rate
        if ms_on and lt_i < 3:
            e = t + (MS_LT[lt_i] - life + rate - 1) // rate
            if e < nxt:
                nxt = e
        if kind == "fixed":
            e = t + (param * P_THRESH - life + rate - 1) // rate
            if e < nxt:
                nxt = e
        elif kind == "hybrid":
            target = 10_000_000 if detour_active else P_THRESH
            e = t + (target - life + rate - 1) // rate
            if e < nxt:
                nxt = e
        elif kind == "cooldown":
            if life >= P_THRESH:
                e = run_start + param
            else:
                e = t + (P_THRESH - life + rate - 1) // rate
                cd = run_start + param
                if cd > e:
                    e = cd
            if e < nxt:
                nxt = e
        if nxt > horizon:
            dt = horizon - t
            at_boundary = False
        else:
            dt = nxt - t
            at_boundary = True
        gain = dt * rate
        bal += gain
        life += gain
        total += gain
        t += dt
        # C1: boundary sequence only strictly before the horizon
        if at_boundary and t < horizon:
            # award milestones (1)
            if ms_on:
                while lt_i < 3 and life >= MS_LT[lt_i]:
                    ms += 1
                    ms_tl.append([f"lifetime-{lt_i + 1}", t])
                    lt_i += 1
                while pt_i < 3 and P >= MS_PT[pt_i]:
                    ms += 1
                    ms_tl.append([f"prestige-{pt_i + 1}", t])
                    pt_i += 1
            # buy while affordable
            c = _cost_a(L)
            while bal >= c:
                bal -= c
                spend += c
                L += 1
                if purchases is not None:
                    purchases.append([t, L, c, bal])
                c = _cost_a(L)
            # award milestones (2)
            if ms_on:
                while lt_i < 3 and life >= MS_LT[lt_i]:
                    ms += 1
                    ms_tl.append([f"lifetime-{lt_i + 1}", t])
                    lt_i += 1
                while pt_i < 3 and P >= MS_PT[pt_i]:
                    ms += 1
                    ms_tl.append([f"prestige-{pt_i + 1}", t])
                    pt_i += 1
            # reset check
            do_reset = False
            if kind == "fixed":
                if life >= param * P_THRESH:
                    do_reset = True
            elif kind == "hybrid":
                if detour_active:
                    if life >= 10_000_000:
                        do_reset = True
                        detour_active = False
                        detour_used = True
                elif life >= P_THRESH:
                    if (not detour_used) and P >= param:
                        detour_active = True
                        detour = {"trigger_t": t, "trigger_P": P}
                    else:
                        do_reset = True
            elif kind == "cooldown":
                if life >= P_THRESH and (t - run_start) >= param:
                    do_reset = True
            if do_reset:
                award = isqrt(life // P_DIV)
                P += award
                n_resets += 1
                dur = t - run_start
                rec = [t, dur, award, life, L]
                if len(first3) < 3:
                    first3.append(rec)
                last3.append(rec)
                if len(last3) > 3:
                    last3.pop(0)
                dur_final = dur
                dur_min = dur if dur_min is None or dur < dur_min else dur_min
                dur_max = dur if dur_max is None or dur > dur_max else dur_max
                day_bins[t // 86_400 if t < horizon else days - 1] += 1
                series_h.update(f"{t},".encode())
                if detour is not None and "reset_t" not in detour:
                    if detour_used and detour.get("trigger_t") is not None:
                        detour.update({"reset_t": t, "duration": dur,
                                       "award": award, "lifetime": life})
                closed += life
                bal = 0
                life = 0
                L = 0
                spend = 0
                run_start = t
            # award milestones (3)
            if ms_on:
                while lt_i < 3 and life >= MS_LT[lt_i]:
                    ms += 1
                    ms_tl.append([f"lifetime-{lt_i + 1}", t])
                    lt_i += 1
                while pt_i < 3 and P >= MS_PT[pt_i]:
                    ms += 1
                    ms_tl.append([f"prestige-{pt_i + 1}", t])
                    pt_i += 1
        # F4 conservation at every boundary (choice C8)
        if bal + spend != life or closed + life != total:
            conserve = False

    ms_names = sorted(m[0] for m in ms_tl)
    return {
        "total": total, "final_P": P, "resets": n_resets,
        "milestones": ms_names, "ms_timeline": ms_tl,
        "first3": first3, "last3": last3,
        "dur_min": dur_min, "dur_max": dur_max, "dur_final": dur_final,
        "per_day_resets": day_bins,
        "series_sha256": series_h.hexdigest(),
        "conservation_ok": conserve,
        "final_level": L, "final_balance": bal, "final_life": life,
        "detour": detour, "purchases": purchases,
    }


# ---------------------------------------------------------------- Arm B twin
# Independently written per-second evaluator. Different cost path (incremental
# exact numerator/denominator), different fold form (the engine's documented
# exact identity: (x*100)//100_000_000 == x//1_000_000), literal 1-second
# ticking with the pinned boundary sequence guarded by exact non-noop
# conditions. Same C1 horizon convention: no actions once t == horizon.

def arm_b(kind, param, horizon, ms_on):
    t = 0
    bal = 0
    life = 0
    level = 0
    pres = 0
    earned = 0
    lt_next_idx = 0
    pt_next_idx = 0
    run_start = 0
    total = 0
    resets = 0
    armed = False
    used = False
    ms_ids = []
    # own cost ladder: exact incremental numerator/denominator
    cost_num = [UP_BASE]
    cost_den = [1]
    costs = [UP_BASE]

    def cost_at(lv):
        while lv >= len(costs):
            cost_num.append(cost_num[-1] * UP_NUM)
            cost_den.append(cost_den[-1] * UP_DEN)
            costs.append(cost_num[-1] // cost_den[-1])
        return costs[lv]

    def rate_now():
        x = (100 + UP_EFF * level) * (100 + P_BONUS * pres) * (100 + MS_BONUS * earned)
        return x // 1_000_000  # exact identity of the HEAD fold at theme 100

    rate = rate_now()
    cost_cur = cost_at(0)
    LT3 = 10_000_000
    nlt = MS_LT[0] if ms_on else horizon * rate + LT3 * 100  # unreachable sentinel
    while t < horizon:
        bal += rate
        life += rate
        total += rate
        t += 1
        if t >= horizon:
            break  # C1: no boundary actions at t == horizon
        # non-noop guard (exact union of sequence-changing conditions)
        trig = bal >= cost_cur
        if not trig and ms_on and lt_next_idx < 3 and life >= nlt:
            trig = True
        if not trig:
            if kind == "fixed":
                trig = life >= param * P_THRESH
            elif kind == "hybrid":
                trig = life >= (LT3 if armed else P_THRESH)
            elif kind == "cooldown":
                trig = life >= P_THRESH and t - run_start >= param
        if trig:
            # award (1)
            if ms_on:
                while lt_next_idx < 3 and life >= MS_LT[lt_next_idx]:
                    earned += 1
                    ms_ids.append(f"lifetime-{lt_next_idx + 1}")
                    lt_next_idx += 1
                while pt_next_idx < 3 and pres >= MS_PT[pt_next_idx]:
                    earned += 1
                    ms_ids.append(f"prestige-{pt_next_idx + 1}")
                    pt_next_idx += 1
            # buy while affordable
            while bal >= cost_at(level):
                bal -= cost_at(level)
                level += 1
            # award (2)
            if ms_on:
                while lt_next_idx < 3 and life >= MS_LT[lt_next_idx]:
                    earned += 1
                    ms_ids.append(f"lifetime-{lt_next_idx + 1}")
                    lt_next_idx += 1
                while pt_next_idx < 3 and pres >= MS_PT[pt_next_idx]:
                    earned += 1
                    ms_ids.append(f"prestige-{pt_next_idx + 1}")
                    pt_next_idx += 1
            # reset check
            fire = False
            if kind == "fixed":
                fire = life >= param * P_THRESH
            elif kind == "hybrid":
                if armed:
                    if life >= LT3:
                        fire = True
                        armed = False
                        used = True
                elif life >= P_THRESH:
                    if (not used) and pres >= param:
                        armed = True
                    else:
                        fire = True
            elif kind == "cooldown":
                fire = life >= P_THRESH and t - run_start >= param
            if fire:
                pres += isqrt(life // P_DIV)
                resets += 1
                bal = 0
                life = 0
                level = 0
                run_start = t
            # award (3)
            if ms_on:
                while lt_next_idx < 3 and life >= MS_LT[lt_next_idx]:
                    earned += 1
                    ms_ids.append(f"lifetime-{lt_next_idx + 1}")
                    lt_next_idx += 1
                while pt_next_idx < 3 and pres >= MS_PT[pt_next_idx]:
                    earned += 1
                    ms_ids.append(f"prestige-{pt_next_idx + 1}")
                    pt_next_idx += 1
            rate = rate_now()
            cost_cur = cost_at(level)
            nlt = MS_LT[lt_next_idx] if (ms_on and lt_next_idx < 3) else horizon * rate + LT3 * 100
    return {"total": total, "final_P": pres, "resets": resets,
            "milestones": sorted(ms_ids)}


# ---------------------------------------------------------------- RNG plumbing
RNG_CONSTRUCTED = []


class CountingRandom(random.Random):
    def __init__(self, seed):
        if seed == SEEDS["aux_reserved_never_read"]:
            raise RuntimeError("attempt to read the aux reserved seed")
        RNG_CONSTRUCTED.append(seed)
        super().__init__(seed)
        self.randrange_calls = 0
        self.shuffle_calls = 0

    def randrange(self, *a, **kw):
        self.randrange_calls += 1
        return super().randrange(*a, **kw)

    def shuffle(self, x):
        self.shuffle_calls += 1
        return super().shuffle(x)


# ---------------------------------------------------------------- gate F1
check("F1-cost-ladder-armA", [_cost_a(0), _cost_a(1), _cost_a(2)] == FIX["gates"]["F1"]["cost_ladder"])
check("F1-rate-by-level-P0-msoff", [_fold_a(L, 0, 0) for L in range(6)] == FIX["gates"]["F1"]["rate_by_level_P0_msoff"])
_legacy_ok = True
for _L in range(FIX["gates"]["F1"]["legacy_fold_identity_sweep"]["L_range"][0],
                FIX["gates"]["F1"]["legacy_fold_identity_sweep"]["L_range"][1] + 1):
    for _P in FIX["gates"]["F1"]["legacy_fold_identity_sweep"]["P_samples"]:
        if _fold_a(_L, _P, 0) != (100 + UP_EFF * _L) * (100 + P_BONUS * _P) // 10_000:
            _legacy_ok = False
check("F1-legacy-fold-identity", _legacy_ok)
check("F1-isqrt-first-award", isqrt(P_THRESH // P_DIV) == FIX["gates"]["F1"]["isqrt_first_award"])

# ---------------------------------------------------------------- F5 hand world
F5 = FIX["gates"]["F5"]
hand_a = arm_a("fixed", 1, F5["horizon"], ms_on=F5["milestones_on"], record_purchases=True)
hand_b = arm_b("fixed", 1, F5["horizon"], ms_on=F5["milestones_on"])
check("F5-hand-purchase-times", [p[0] for p in hand_a["purchases"]] == F5["purchase_times"])
check("F5-hand-purchase-costs", [p[2] for p in hand_a["purchases"]] == F5["purchase_costs"])
check("F5-hand-balance", hand_a["final_balance"] == F5["balance_at_horizon"])
check("F5-hand-lifetime", hand_a["final_life"] == F5["lifetime"])
check("F5-hand-total", hand_a["total"] == F5["total"])
check("F5-hand-level", hand_a["final_level"] == F5["level"])
check("F5-hand-no-milestone", len(hand_a["milestones"]) == F5["milestones_earned"])
check("F5-hand-twin-agrees", (hand_b["total"], hand_b["final_P"], hand_b["resets"])
      == (hand_a["total"], hand_a["final_P"], hand_a["resets"]))

# ---------------------------------------------------------------- grids
grid_on = {}
grid_off = {}
grid_h2 = {}
b_on = {}
b_off = {}
b_h2 = {}
for name, kind, param in POLICIES:
    grid_on[name] = arm_a(kind, param, H, ms_on=True)
    grid_off[name] = arm_a(kind, param, H, ms_on=False)
    grid_h2[name] = arm_a(kind, param, H2, ms_on=True)
    b_on[name] = arm_b(kind, param, H, ms_on=True)
    b_off[name] = arm_b(kind, param, H, ms_on=False)
    b_h2[name] = arm_b(kind, param, H2, ms_on=True)

# ---------------------------------------------------------------- gate F2
F2 = FIX["gates"]["F2"]
g_off = grid_off["fixed-1"]
check("F2-first-prestige-t", g_off["first3"][0][0] == F2["first_prestige_t"])
check("F2-first-award", g_off["first3"][0][2] == F2["first_award"])
check("F2-run-durations-1-3", [r[1] for r in g_off["first3"]] == F2["run_durations_1_3"])
check("F2-reset-count-14d", g_off["resets"] == F2["reset_count_14d"])
check("F2-twin-reset-count", b_off["fixed-1"]["resets"] == F2["reset_count_14d"])

# ---------------------------------------------------------------- gate F3
for name in NAMES:
    check(f"F3-off-le-on-{name}", grid_off[name]["total"] <= grid_on[name]["total"])

# ---------------------------------------------------------------- gate F4
for name in NAMES:
    check(f"F4-conservation-{name}",
          grid_on[name]["conservation_ok"] and grid_off[name]["conservation_ok"]
          and grid_h2[name]["conservation_ok"])
_no_owned = all(not m.startswith("owned")
                for g in (grid_on, grid_off, grid_h2)
                for r in g.values() for m in r["milestones"])
check("F4-owned-rungs-never-fire", _no_owned)
check("F4-owned-thresholds-unreachable-at-count-1", COUNT < min(MS_OWN))

# ---------------------------------------------------------------- Arm R
AR = FIX["arm_r"]
rng_main = CountingRandom(SEEDS["arm_r_main"])
r_main_ks = [rng_main.randrange(1, 60001) for _ in range(AR["main_draws"]["hybrid_triggers"])]
_after_hybrid = rng_main.randrange_calls
r_main_taus = [rng_main.randrange(30, 7201) for _ in range(AR["main_draws"]["cooldowns"])]
check("F6-sentinel-main-hybrid-draws-12", _after_hybrid == AR["main_draws"]["hybrid_triggers"] == 12)
check("F6-sentinel-main-total-draws-18", rng_main.randrange_calls == 18)

rng_stab = CountingRandom(SEEDS["arm_r_stability"])
r_stab_ks = [rng_stab.randrange(1, 60001) for _ in range(AR["stability_draws"]["hybrid_triggers"])]
_after_hybrid_s = rng_stab.randrange_calls
r_stab_taus = [rng_stab.randrange(30, 7201) for _ in range(AR["stability_draws"]["cooldowns"])]
check("F6-sentinel-stability-hybrid-draws-4", _after_hybrid_s == AR["stability_draws"]["hybrid_triggers"] == 4)
check("F6-sentinel-stability-total-draws-6", rng_stab.randrange_calls == 6)


def probe(kind, param):
    a = arm_a(kind, param, H, ms_on=True)
    b = arm_b(kind, param, H, ms_on=True)
    return {"kind": kind, "param": param, "total": a["total"],
            "final_P": a["final_P"], "resets": a["resets"],
            "milestones": a["milestones"],
            "twin_total": b["total"], "twin_exact": a["total"] == b["total"]}


arm_r_main = [probe("hybrid", k) for k in r_main_ks] + [probe("cooldown", x) for x in r_main_taus]
arm_r_stab = [probe("hybrid", k) for k in r_stab_ks] + [probe("cooldown", x) for x in r_stab_taus]
check("F6-armR-main-twin-exact", all(p["twin_exact"] for p in arm_r_main))
check("F6-armR-stability-twin-exact", all(p["twin_exact"] for p in arm_r_stab))

# presentation shuffle (reporting only)
rng_pres = CountingRandom(SEEDS["presentation"])
presentation_order = list(NAMES)
rng_pres.shuffle(presentation_order)
check("F6-presentation-single-shuffle", rng_pres.shuffle_calls == 1 and rng_pres.randrange_calls == 0)
check("F6-aux-seed-never-read", SEEDS["aux_reserved_never_read"] not in RNG_CONSTRUCTED)
check("F6-rng-constructed-set",
      RNG_CONSTRUCTED == [SEEDS["arm_r_main"], SEEDS["arm_r_stability"], SEEDS["presentation"]])

# ---------------------------------------------------------------- gate F6 twins
for leg, ga, gb in (("on-H", grid_on, b_on), ("off-H", grid_off, b_off), ("on-H2", grid_h2, b_h2)):
    check(f"F6-twin-total-{leg}", all(ga[n]["total"] == gb[n]["total"] for n in NAMES))
    check(f"F6-twin-state-{leg}", all(
        (ga[n]["final_P"], ga[n]["resets"], ga[n]["milestones"])
        == (gb[n]["final_P"], gb[n]["resets"], gb[n]["milestones"]) for n in NAMES))

# hybrid detour sanity: lifetime-3 earned iff the detour fired (ON grid)
_det_ok = True
for name, kind, param in POLICIES:
    if kind == "hybrid":
        fired = grid_on[name]["detour"] is not None and "reset_t" in (grid_on[name]["detour"] or {})
        has_lt3 = "lifetime-3" in grid_on[name]["milestones"]
        if fired != has_lt3:
            _det_ok = False
check("hybrid-detour-iff-lifetime-3", _det_ok)

GATES = {
    "F1": all(n not in CHECKS["failures"] for n in
              ("F1-cost-ladder-armA", "F1-rate-by-level-P0-msoff", "F1-legacy-fold-identity", "F1-isqrt-first-award")),
    "F2": all(not f.startswith("F2-") for f in CHECKS["failures"]),
    "F3": all(not f.startswith("F3-") for f in CHECKS["failures"]),
    "F4": all(not f.startswith("F4-") for f in CHECKS["failures"]),
    "F5": all(not f.startswith("F5-") for f in CHECKS["failures"]),
    "F6": all(not f.startswith("F6-") for f in CHECKS["failures"]),
}

# ---------------------------------------------------------------- decision
T1 = grid_on["fixed-1"]["total"]
T_NEVER = grid_on["never"]["total"]
alt_names = [n for n in NAMES if n != "fixed-1"]
beaters = [n for n in alt_names if 100 * grid_on[n]["total"] >= 101 * T1]
twin_on_exact = all(grid_on[n]["total"] == b_on[n]["total"] for n in NAMES)
reject_fires = bool(beaters) and twin_on_exact

best_alt = max(alt_names, key=lambda n: grid_on[n]["total"])
best_alt_ratio = Fraction(grid_on[best_alt]["total"], T1)

mechanism_miss = False
argmax_beater = None
if beaters:
    argmax_beater = max(beaters, key=lambda n: grid_on[n]["total"])
    mechanism_miss = (100 * grid_off[argmax_beater]["total"]
                      >= 101 * grid_off["fixed-1"]["total"])

approve_fires = (all(100 * grid_on[n]["total"] <= 99 * T1 for n in alt_names)
                 and T1 >= GRIND * T_NEVER)

null_axis = None
if reject_fires and mechanism_miss:
    verdict_class = "NULL"
    null_axis = "mechanism-miss"
elif reject_fires:
    verdict_class = "REJECT"
elif not all(GATES.values()):
    verdict_class = "INVALID"
elif approve_fires:
    verdict_class = "APPROVE"
else:
    verdict_class = "NULL"
    if Fraction(99, 100) < best_alt_ratio < Fraction(101, 100):
        null_axis = "parity-straddle"
    elif not twin_on_exact:
        null_axis = "twin-arm-disagreement"
    else:
        null_axis = "other"
# INVALID trumps nothing per the registered literal order (REJECT first);
# any gate failure alongside a fired REJECT is reported as a first-class
# anomaly in the gates block, and the fired REJECT already required exact
# twin agreement on the decision leg (choice C9).
if verdict_class == "REJECT" and not all(GATES.values()):
    print("ANOMALY: REJECT fired with a gate failure present — see gates block")

# horizon-conditional reporting leg (named, never ruling)
h2_beaters = [n for n in alt_names if 100 * grid_h2[n]["total"] >= 101 * grid_h2["fixed-1"]["total"]]
h2_clause_same_side = None
if verdict_class in ("REJECT", "NULL") and argmax_beater is not None:
    h2_clause_same_side = (100 * grid_h2[argmax_beater]["total"]
                           >= 101 * grid_h2["fixed-1"]["total"])
elif verdict_class == "APPROVE":
    h2_clause_same_side = (all(100 * grid_h2[n]["total"] <= 99 * grid_h2["fixed-1"]["total"] for n in alt_names)
                           and grid_h2["fixed-1"]["total"] >= GRIND * grid_h2["never"]["total"])

grind_holds = T1 >= GRIND * T_NEVER
grind_ratio = Fraction(T1, T_NEVER)

pi_best = max(NAMES, key=lambda n: grid_on[n]["total"])
PI_BEST_T = grid_on[pi_best]["total"]
probe_beats_pi_best = [p for p in arm_r_main + arm_r_stab if p["total"] > PI_BEST_T]

# ---------------------------------------------------------------- reporting
def fr(n, d):
    f = Fraction(n, d)
    return {"exact": f"{f.numerator}/{f.denominator}", "float": repr(n / d)}


ratios_on = {n: fr(grid_on[n]["total"], T1) for n in NAMES}
ratios_off = {n: fr(grid_off[n]["total"], grid_off["fixed-1"]["total"]) for n in NAMES}
ratios_h2 = {n: fr(grid_h2[n]["total"], grid_h2["fixed-1"]["total"]) for n in NAMES}

k_curve = sorted(
    [{"k": p[2], "source": "pinned", "total": grid_on[p[0]]["total"],
      "ratio_vs_greedy": fr(grid_on[p[0]]["total"], T1)} for p in POLICIES if p[1] == "hybrid"]
    + [{"k": p["param"], "source": "arm-r-main", "total": p["total"],
        "ratio_vs_greedy": fr(p["total"], T1)} for p in arm_r_main if p["kind"] == "hybrid"]
    + [{"k": p["param"], "source": "arm-r-stability", "total": p["total"],
        "ratio_vs_greedy": fr(p["total"], T1)} for p in arm_r_stab if p["kind"] == "hybrid"],
    key=lambda r: (r["k"], r["source"]))

cooldown_price = sorted(
    [{"tau": p[2], "source": "pinned", "total": grid_on[p[0]]["total"],
      "fraction_of_pi_best": fr(grid_on[p[0]]["total"], PI_BEST_T)} for p in POLICIES if p[1] == "cooldown"]
    + [{"tau": p["param"], "source": "arm-r-main", "total": p["total"],
        "fraction_of_pi_best": fr(p["total"], PI_BEST_T)} for p in arm_r_main if p["kind"] == "cooldown"]
    + [{"tau": p["param"], "source": "arm-r-stability", "total": p["total"],
        "fraction_of_pi_best": fr(p["total"], PI_BEST_T)} for p in arm_r_stab if p["kind"] == "cooldown"],
    key=lambda r: (r["tau"], r["source"]))

# drafter-disclosed landing — re-derived comparison, NEVER gated
DISCLOSED = {
    "never": 24_767_541, "fixed-1": 25_386_048_335, "fixed-2": 2_308_530_416,
    "fixed-4": 5_562_567_873, "fixed-9": 1_189_091_761, "fixed-16": 460_817_123,
    "fixed-25": 250_843_290, "fixed-100": 56_754_018, "hybrid-0": 1_905_424_414,
    "hybrid-100": 24_975_644_645, "hybrid-1000": 27_411_200_535,
    "hybrid-10000": 26_870_606_289, "cooldown-60": 15_237_507_974,
    "cooldown-300": 5_758_125_849, "cooldown-3600": 1_041_938_127,
}
disclosed_cmp = {n: {"disclosed": DISCLOSED[n], "measured": grid_on[n]["total"],
                     "match": DISCLOSED[n] == grid_on[n]["total"]} for n in NAMES}


def strip(rec):
    out = dict(rec)
    out.pop("purchases", None)
    return out


results = {
    "meta": {
        "verdict": "VERDICT 070", "intake": "INTAKE 059",
        "proposal": FIX["meta"]["proposal_header_verbatim"],
        "source_pin": FIX["meta"]["source_pin"],
        "fixtures_sha256": FIX_SHA,
        "cpython": f"{sys.version_info[0]}.{sys.version_info[1]}",
    },
    "grid_on_h": {n: strip(grid_on[n]) for n in NAMES},
    "grid_off_h": {n: strip(grid_off[n]) for n in NAMES},
    "grid_on_h2": {n: strip(grid_h2[n]) for n in NAMES},
    "arm_b": {"on_h": b_on, "off_h": b_off, "on_h2": b_h2},
    "arm_r": {
        "main": {"seed": SEEDS["arm_r_main"], "hybrid_triggers": r_main_ks,
                 "cooldowns": r_main_taus, "probes": arm_r_main,
                 "randrange_calls": rng_main.randrange_calls},
        "stability": {"seed": SEEDS["arm_r_stability"], "hybrid_triggers": r_stab_ks,
                      "cooldowns": r_stab_taus, "probes": arm_r_stab,
                      "randrange_calls": rng_stab.randrange_calls},
        "probes_beating_pi_best": probe_beats_pi_best,
    },
    "presentation_order": presentation_order,
    "ratios_on_h": ratios_on, "ratios_off_h": ratios_off, "ratios_on_h2": ratios_h2,
    "k_timing_curve": k_curve,
    "cooldown_price_table": cooldown_price,
    "gates": {**GATES, "all_green": all(GATES.values())},
    "decision": {
        "class": verdict_class,
        "null_axis": null_axis,
        "rule_order": ["REJECT", "INVALID", "APPROVE", "NULL"],
        "reject": {
            "fires": reject_fires, "beaters": beaters,
            "argmax_beater": argmax_beater,
            "beater_totals": {n: grid_on[n]["total"] for n in beaters},
            "fixed_1_total": T1,
            "twin_on_exact": twin_on_exact,
            "mechanism_attribution": None if argmax_beater is None else {
                "beater_off_total": grid_off[argmax_beater]["total"],
                "fixed_1_off_total": grid_off["fixed-1"]["total"],
                "beater_beats_off": mechanism_miss,
                "attribution_to_milestone_fold_holds": not mechanism_miss,
            },
        },
        "approve": {"fires": approve_fires,
                    "grind_clause": {"holds": grind_holds,
                                     "greedy_over_never": fr(T1, T_NEVER)["exact"],
                                     "greedy_over_never_float": fr(T1, T_NEVER)["float"]}},
        "best_alternative": {"name": best_alt, "total": grid_on[best_alt]["total"],
                             "ratio_vs_greedy": fr(grid_on[best_alt]["total"], T1)},
        "pi_best": {"name": pi_best, "total": PI_BEST_T},
        "horizon_conditional": {
            "h2_beaters": h2_beaters,
            "promoted_clause_holds_at_h2": h2_clause_same_side,
            "note": "named finding, never ruling",
        },
    },
    "disclosed_comparison_never_gated": disclosed_cmp,
    "self_checks": {"passed": CHECKS["passed"], "failed": CHECKS["failed"],
                    "failures": CHECKS["failures"]},
}

# ---------------------------------------------------------------- stdout report
print("VERDICT 070 — prestige reset-policy optimality (INTAKE 059 / PROPOSAL 059)")
print(f"fixtures sha256: {FIX_SHA}")
print(f"cpython: {sys.version_info[0]}.{sys.version_info[1]} (pinned 3.11)")
print()
print("15-policy grid @ H = 1,209,600 s (milestones ON, Arm A exact; Arm B twin equal):")
hdr = f"{'policy':>14} {'total':>16} {'final_P':>8} {'resets':>8} {'ms':>3} {'ratio-vs-greedy':>18}"
print(hdr)
for n in NAMES:
    g = grid_on[n]
    print(f"{n:>14} {g['total']:>16} {g['final_P']:>8} {g['resets']:>8} "
          f"{len(g['milestones']):>3} {ratios_on[n]['float']:>18}")
print()
print("milestones-OFF contrast grid @ H (attribution control, F3):")
for n in NAMES:
    g = grid_off[n]
    print(f"{n:>14} {g['total']:>16} ratio-vs-greedy-OFF {ratios_off[n]['float']}")
print()
print("H/2 = 604,800 s reporting grid:")
for n in NAMES:
    g = grid_h2[n]
    print(f"{n:>14} {g['total']:>16} ratio {ratios_h2[n]['float']}")
print()
print(f"Arm R main (seed {SEEDS['arm_r_main']}): hybrid triggers {r_main_ks} cooldowns {r_main_taus}")
for p in arm_r_main:
    print(f"  probe {p['kind']}-{p['param']:>5}: total {p['total']} twin-exact {p['twin_exact']}")
print(f"Arm R stability (seed {SEEDS['arm_r_stability']}): hybrid {r_stab_ks} cooldowns {r_stab_taus}")
for p in arm_r_stab:
    print(f"  probe {p['kind']}-{p['param']:>5}: total {p['total']} twin-exact {p['twin_exact']}")
print(f"probes beating the Pi-best ({pi_best}): {len(probe_beats_pi_best)}"
      + (" — named finding, never a ruling" if probe_beats_pi_best else ""))
print(f"presentation order (seed {SEEDS['presentation']}, reporting only): {presentation_order}")
print()
print("cooldown price table (fraction of Pi-best output):")
for row in cooldown_price:
    print(f"  tau={row['tau']:>5} ({row['source']}): total {row['total']} "
          f"fraction {row['fraction_of_pi_best']['float']}")
print()
print(f"gates: F1={GATES['F1']} F2={GATES['F2']} F3={GATES['F3']} "
      f"F4={GATES['F4']} F5={GATES['F5']} F6={GATES['F6']}")
print()
print("decision (pre-registered order REJECT -> INVALID -> APPROVE -> NULL):")
print(f"  REJECT clause: fires={reject_fires} beaters={beaters} "
      f"(line: 100*total(pi) >= 101*{T1})")
if argmax_beater is not None:
    print(f"  argmax beater {argmax_beater}: total {grid_on[argmax_beater]['total']} "
          f"= {ratios_on[argmax_beater]['float']} x greedy")
    print(f"  attribution: {argmax_beater} OFF total {grid_off[argmax_beater]['total']} vs "
          f"fixed-1 OFF {grid_off['fixed-1']['total']} -> beats OFF: {mechanism_miss} "
          f"(attribution to the milestone fold holds: {not mechanism_miss})")
print(f"  grind clause: greedy = {fr(T1, T_NEVER)['float']} x never (>= 2x: {grind_holds})")
print(f"  horizon-conditional (H/2, named never ruling): promoted clause holds at H/2: "
      f"{h2_clause_same_side}; H/2 beaters: {h2_beaters}")
print(f"  CLASS: {verdict_class}" + (f" (axis: {null_axis})" if null_axis else ""))
print()
print("drafter-disclosed comparison (NEVER gated):")
all_match = all(v["match"] for v in disclosed_cmp.values())
print(f"  all 15 disclosed totals reproduced from scratch: {all_match}")
for n in NAMES:
    if not disclosed_cmp[n]["match"]:
        print(f"  MISMATCH {n}: disclosed {disclosed_cmp[n]['disclosed']} measured {disclosed_cmp[n]['measured']}")
print()
print(f"SELF-CHECKS: {CHECKS['passed']} passed, {CHECKS['failed']} failed")

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=1, sort_keys=True, ensure_ascii=True)
    fh.write("\n")

sys.exit(0 if CHECKS["failed"] == 0 else 1)
