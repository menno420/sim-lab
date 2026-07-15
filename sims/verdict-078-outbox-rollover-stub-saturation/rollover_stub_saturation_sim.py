#!/usr/bin/env python3
"""VERDICT 078 — outbox rollover stub saturation (idea-engine PROPOSAL 065).

Three-arm, fully deterministic decision core:
  Arm A — DECISION arm, seedless: the exact integer recurrence
          (Delta_k = ceil((T - F_k)/b) via -(-x//y), floor update per policy)
          jumped between rolls, over the full {policy x T x s x b x W} grid.
  Arm B — twin, seedless, INDEPENDENTLY-WRITTEN: a literal byte-ledger
          simulator (an actual list of (kind, size) records appended, scanned,
          and rolled; file size recomputed as the sum of record sizes at EVERY
          append). Must reproduce every Arm-A number exactly.
  Arm R — seeded, REPORTING-ONLY: block sizes per proposal from the pinned mix
          {8000: 1/4, 16000: 1/2, 24000: 1/4} (exact-rational thresholds, one
          uniform per appended proposal, draw counts asserted). NO statistical
          gate rides Arm R.

Hermetic: reads ONLY its sibling fixtures.json. Stdlib only. CPython 3.11
pinned and asserted. stdout + results.json byte-identical across process runs
(no timestamps; canonical serialization per fixture convention C5).
"""

import json
import os
import platform
import random
import sys
from datetime import date, timedelta
from fractions import Fraction

# ---------------------------------------------------------------- runtime pin
assert platform.python_implementation() == "CPython", "CPython required"
assert sys.version_info[:2] == (3, 11), "CPython 3.11 pinned (fixtures runtime_pins)"

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

# ------------------------------------------------------------- seed registry
SEED_REGISTRY = []

class LoggedRandom(random.Random):
    def __init__(self, seed):
        SEED_REGISTRY.append(seed)
        super().__init__(seed)

# ---------------------------------------------------------------- self-checks
CHECKS = {"total": 0, "failed": 0, "failures": []}

def check(name, cond):
    CHECKS["total"] += 1
    if not cond:
        CHECKS["failed"] += 1
        CHECKS["failures"].append(name)

def ceil_div(a, b):
    return -(-a // b)

# ------------------------------------------------------------------ constants
W_ = FX["world"]
H0_D = W_["H0"]
HR_D = W_["h_r"]
T_GRID = W_["T_grid"]
S_GRID = W_["s_grid"]
B_GRID = W_["b_grid"]
WG_GRID = W_["W_grid"]
DEC = FX["decision_rule"]["decision_cell"]
POLICIES = ("P-STUB", "P-RANGE", "P-COMPACT")
CAP = W_["unbounded_walk_appends"]  # 100000
PREFIX_CAP = 5000  # C3 — Arm-B prefix walk length on non-special unbounded cells

# =====================================================================
# Arm A — exact integer recurrence (Delta-jump; no per-append iteration)
# =====================================================================

def arm_a(T, s, b, W, h_r, H0, policy, cap):
    """Return the cell record via the registered recurrence."""
    appends = 0
    k = 0
    stub_mass = 0
    receipt_mass = 0
    fulls = 0
    spacings = []
    floors = []
    stub_records = 0
    archived = 0
    while True:
        F = H0 + receipt_mass + stub_mass + fulls * b
        gap = T - F
        # invariant: gap > 0 here (a post-roll F >= T returned below)
        delta = ceil_div(gap, b)
        if appends + delta > cap:
            return {
                "saturated": False,
                "walk_appends": appends,
                "K": k,
                "spacings": spacings,
                "floors": floors,
                "constant_floor": floors[-1] if floors and len(set(floors)) == 1 else None,
            }
        appends += delta
        fulls += delta
        k += 1
        evict = fulls - W if fulls > W else 0
        fulls -= evict
        archived += evict
        if policy == "P-STUB":
            stub_mass += evict * s
            stub_records += evict
        elif policy == "P-RANGE":
            if evict:
                stub_mass += s
                stub_records += 1
        else:  # P-COMPACT — supersede: newest range stub + newest receipt only
            if evict:
                stub_mass = s
                stub_records = 1
        if policy == "P-COMPACT":
            receipt_mass = h_r
        else:
            receipt_mass += h_r
        F = H0 + receipt_mass + stub_mass + fulls * b
        spacings.append(delta)
        floors.append(F)
        if F >= T:
            return {
                "saturated": True,
                "Nstar": appends,
                "K": k,
                "spacings": spacings,
                "floors": floors,
                "composition": {
                    "stub": stub_mass,
                    "receipts": receipt_mass,
                    "window": fulls * b,
                    "header": H0,
                },
                "archived": archived,
                "stub_records": stub_records,
                "live_fulls": fulls,
            }

# =====================================================================
# Arm B — literal byte-ledger simulator (independently written)
# =====================================================================

def arm_b(T, s, b, W, h_r, H0, policy, cap):
    """Event-driven per-append walk over an actual record ledger."""
    kinds = []   # 'full' | 'stub' | 'receipt'
    sizes = []
    appends = 0
    rolls = 0
    since_last_roll = 0
    appended_total = 0
    archived_total = 0
    spacings = []
    floors = []
    sum_ok = True          # F1: size == sum of parts at EVERY append
    conservation_ok = True  # F1/C10: appended == archived + live fulls at every roll
    running = H0
    while appends < cap:
        appends += 1
        appended_total += 1
        since_last_roll += 1
        kinds.append("full")
        sizes.append(b)
        running += b
        if running != H0 + sum(sizes):
            sum_ok = False
        if running >= T:
            rolls += 1
            full_positions = [i for i, kd in enumerate(kinds) if kd == "full"]
            kept = set(full_positions[max(0, len(full_positions) - W):]) if W > 0 else set()
            evicted_positions = [i for i in full_positions if i not in kept]
            e = len(evicted_positions)
            archived_total += e
            drop = set(evicted_positions)
            if policy == "P-COMPACT":
                # supersede: the previous receipt always rolls; the previous
                # range stub rolls only when a new one is written (e >= 1)
                for i, kd in enumerate(kinds):
                    if kd == "receipt":
                        drop.add(i)
                    elif kd == "stub" and e >= 1:
                        drop.add(i)
            new_kinds = []
            new_sizes = []
            for i, (kd, sz) in enumerate(zip(kinds, sizes)):
                if i in drop:
                    continue
                new_kinds.append(kd)
                new_sizes.append(sz)
            # a zero-byte stub is no record at all (true deletion, F5) — the
            # ledger only carries records with mass
            if policy == "P-STUB":
                if s > 0:
                    for _ in range(e):
                        new_kinds.append("stub")
                        new_sizes.append(s)
            elif e >= 1 and s > 0:  # P-RANGE / P-COMPACT: one range stub per (evicting) roll
                new_kinds.append("stub")
                new_sizes.append(s)
            if h_r > 0:  # a zero-byte receipt is likewise no record
                new_kinds.append("receipt")
                new_sizes.append(h_r)
            kinds, sizes = new_kinds, new_sizes
            running = H0 + sum(sizes)
            live_fulls = sum(1 for kd in kinds if kd == "full")
            if appended_total != archived_total + live_fulls:
                conservation_ok = False
            spacings.append(since_last_roll)
            since_last_roll = 0
            floors.append(running)
            if running >= T:
                stub_mass = sum(sz for kd, sz in zip(kinds, sizes) if kd == "stub")
                receipt_mass = sum(sz for kd, sz in zip(kinds, sizes) if kd == "receipt")
                window_mass = sum(sz for kd, sz in zip(kinds, sizes) if kd == "full")
                return {
                    "saturated": True,
                    "Nstar": appends,
                    "K": rolls,
                    "spacings": spacings,
                    "floors": floors,
                    "composition": {
                        "stub": stub_mass,
                        "receipts": receipt_mass,
                        "window": window_mass,
                        "header": H0,
                    },
                    "archived": archived_total,
                    "stub_records": sum(1 for kd in kinds if kd == "stub"),
                    "live_fulls": live_fulls,
                    "sum_ok": sum_ok,
                    "conservation_ok": conservation_ok,
                }
    return {
        "saturated": False,
        "walk_appends": appends,
        "K": rolls,
        "spacings": spacings,
        "floors": floors,
        "constant_floor": floors[-1] if floors and len(set(floors)) == 1 else None,
        "sum_ok": sum_ok,
        "conservation_ok": conservation_ok,
    }


def arm_b_alternate_schedule(T, s, b, W, h_r, H0, policy, every, total_appends):
    """F2a — roll every `every` appends regardless of size; return post-roll sizes."""
    kinds = []
    sizes = []
    out = []
    appended = 0
    rolls = 0
    for _ in range(total_appends):
        appended += 1
        kinds.append("full")
        sizes.append(b)
        if appended % every == 0:
            rolls += 1
            full_positions = [i for i, kd in enumerate(kinds) if kd == "full"]
            kept = set(full_positions[max(0, len(full_positions) - W):]) if W > 0 else set()
            drop = set(i for i in full_positions if i not in kept)
            e = len(drop)
            if policy == "P-COMPACT":
                for i, kd in enumerate(kinds):
                    if kd == "receipt" or (kd == "stub" and e >= 1):
                        drop.add(i)
            nk, ns = [], []
            for i, (kd, sz) in enumerate(zip(kinds, sizes)):
                if i in drop:
                    continue
                nk.append(kd)
                ns.append(sz)
            if policy == "P-STUB":
                nk.extend(["stub"] * e)
                ns.extend([s] * e)
            elif e >= 1:
                nk.append("stub")
                ns.append(s)
            nk.append("receipt")
            ns.append(h_r)
            kinds, sizes = nk, ns
            out.append((rolls, appended, H0 + sum(sizes)))
    return out

# =====================================================================
# Grid sweep + A/B equality
# =====================================================================

def cell_key(policy, T, s, b, W):
    return "%s T=%d s=%d b=%d W=%d" % (policy, T, s, b, W)

SPECIAL_FULL_TWIN = {
    cell_key("P-COMPACT", DEC["T"], DEC["s"], DEC["b"], DEC["W"]),
}

grid_a = {}
grid_b = {}
for policy in POLICIES:
    for T in T_GRID:
        for s in S_GRID:
            for b in B_GRID:
                for Wp in WG_GRID:
                    key = cell_key(policy, T, s, b, Wp)
                    ra = arm_a(T, s, b, Wp, HR_D, H0_D, policy, CAP)
                    cap_b = CAP if (ra["saturated"] or key in SPECIAL_FULL_TWIN) else PREFIX_CAP
                    rb = arm_b(T, s, b, Wp, HR_D, H0_D, policy, cap_b)
                    grid_a[key] = ra
                    grid_b[key] = rb

# F1 aggregate + F6 A/B equality over the whole grid
all_sum_ok = all(rb["sum_ok"] for rb in grid_b.values())
all_conservation_ok = all(rb["conservation_ok"] for rb in grid_b.values())
check("F1 file size == sum of parts at every append (every cell, Arm B)", all_sum_ok)
check("F1 conservation appended == archived + live fulls at every roll (every cell)", all_conservation_ok)

ab_equal = True
for key, ra in grid_a.items():
    rb = grid_b[key]
    if ra["saturated"] != rb["saturated"]:
        ab_equal = False
        break
    if ra["saturated"]:
        for f in ("Nstar", "K", "spacings", "floors", "composition", "archived", "stub_records", "live_fulls"):
            if ra[f] != rb[f]:
                ab_equal = False
    else:
        nb = len(rb["floors"])
        if ra["floors"][:nb] != rb["floors"] or ra["spacings"][:nb] != rb["spacings"]:
            ab_equal = False
check("F6 Arm B reproduces every Arm-A number exactly (243 grid cells: walls, floors, spacings, compositions)", ab_equal)

# ---------------------------------------------------------------- decision cell
DK = cell_key("P-STUB", DEC["T"], DEC["s"], DEC["b"], DEC["W"])
dec_a = grid_a[DK]
dec_b = grid_b[DK]
rng_a = grid_a[cell_key("P-RANGE", DEC["T"], DEC["s"], DEC["b"], DEC["W"])]
rng_b = grid_b[cell_key("P-RANGE", DEC["T"], DEC["s"], DEC["b"], DEC["W"])]
cmp_a = grid_a[cell_key("P-COMPACT", DEC["T"], DEC["s"], DEC["b"], DEC["W"])]
cmp_b = grid_b[cell_key("P-COMPACT", DEC["T"], DEC["s"], DEC["b"], DEC["W"])]

collapse_a = next((i + 1 for i, d in enumerate(dec_a["spacings"]) if d <= 2), None)
collapse_b = next((i + 1 for i, d in enumerate(dec_b["spacings"]) if d <= 2), None)
thrash_a = sum(1 for d in dec_a["spacings"] if d <= 2)
thrash_b = sum(1 for d in dec_b["spacings"] if d <= 2)
collapse_proposal = sum(dec_a["spacings"][:collapse_a]) if collapse_a else None

# F1 spacing identity re-derived at the decision cell (event walk vs recurrence form)
spacing_identity_ok = True
prev_F = H0_D
for j, sp in enumerate(dec_b["spacings"]):
    if sp != ceil_div(DEC["T"] - prev_F, DEC["b"]):
        spacing_identity_ok = False
    prev_F = dec_b["floors"][j]
check("F1 spacing identity Delta_k = ceil((T - F_k)/b) re-derived by the event walk (decision cell)", spacing_identity_ok)

# F1 floor law at every roll (decision cell, all three policies) — closed form in (k, appends)
def floor_law_ok(rec, policy):
    ok = True
    appended = 0
    for j, sp in enumerate(rec["spacings"]):
        appended += sp
        k = j + 1
        Wp = DEC["W"]
        n_window = Wp if appended > Wp else appended
        if policy == "P-STUB":
            expect = H0_D + k * HR_D + DEC["s"] * (appended - n_window) + n_window * DEC["b"]
        elif policy == "P-RANGE":
            expect = H0_D + k * HR_D + DEC["s"] * k + n_window * DEC["b"]
        else:
            expect = H0_D + HR_D + DEC["s"] + n_window * DEC["b"]
        if rec["floors"][j] != expect:
            ok = False
    return ok

check("F1 floor law P-STUB form at every roll (decision cell)", floor_law_ok(dec_b, "P-STUB"))
check("F1 floor law P-RANGE form at every roll (decision cell)", floor_law_ok(rng_b, "P-RANGE"))
check("F1 floor law P-COMPACT form at every roll (decision cell)", floor_law_ok(cmp_b, "P-COMPACT"))

# ---------------------------------------------------------------- F2 theorems
# (a) FLOOR LAW timing invariance — alternate schedule, roll every 25 appends
timing_ok = True
for policy in POLICIES:
    walk = arm_b_alternate_schedule(DEC["T"], DEC["s"], DEC["b"], DEC["W"], HR_D, H0_D, policy, 25, 1000)
    for (k, appended, size) in walk:
        n_window = DEC["W"] if appended > DEC["W"] else appended
        if policy == "P-STUB":
            expect = H0_D + k * HR_D + DEC["s"] * (appended - n_window) + n_window * DEC["b"]
        elif policy == "P-RANGE":
            expect = H0_D + k * HR_D + DEC["s"] * k + n_window * DEC["b"]
        else:
            expect = H0_D + HR_D + DEC["s"] + n_window * DEC["b"]
        if size != expect:
            timing_ok = False
check("F2a FLOOR LAW timing invariance — roll-every-25 schedule matches the closed form at every roll, all three policies", timing_ok)

# (b) RECEIPT-FREE INVARIANCE — h_r = 0, W = 0: wall = ceil((T - H0)/s), b-invariant
rf_expect = ceil_div(DEC["T"] - H0_D, DEC["s"])
rf_walls = []
for b in B_GRID:
    wa = arm_a(DEC["T"], DEC["s"], b, 0, 0, H0_D, "P-STUB", CAP)
    wb = arm_b(DEC["T"], DEC["s"], b, 0, 0, H0_D, "P-STUB", CAP)
    rf_walls.append(wa["Nstar"])
    check("F2b receipt-free A==B at b=%d" % b, wa["saturated"] and wb["saturated"] and wa["Nstar"] == wb["Nstar"])
check("F2b RECEIPT-FREE INVARIANCE wall == ceil((T-H0)/s) == %d, identical across the b grid" % FX["anchors"]["receipt_free_wall"],
      rf_walls == [rf_expect] * 3 and rf_expect == FX["anchors"]["receipt_free_wall"])

# (c) COMPACT BOUNDEDNESS — decision cell, 100,000 appends, both arms full length
compact_const = FX["anchors"]["decision_cell"]["compact_floor"]
compact_ok = (
    not cmp_a["saturated"] and not cmp_b["saturated"]
    and cmp_a["walk_appends"] >= CAP - ceil_div(DEC["T"], DEC["b"]) and set(cmp_a["floors"]) == {compact_const}
    and set(cmp_b["floors"]) == {compact_const}
    and set(cmp_a["spacings"][1:]) == {FX["anchors"]["decision_cell"]["compact_spacing"]}
    and set(cmp_b["spacings"][1:]) == {FX["anchors"]["decision_cell"]["compact_spacing"]}
)
check("F2c COMPACT BOUNDEDNESS — constant floor 34,030 and constant spacing 11 over the 100,000-append walk, both arms", compact_ok)

# MONOTONE THRASH — every P-STUB grid cell: floors strictly increasing, spacings non-increasing
monotone_ok = True
for T in T_GRID:
    for s in S_GRID:
        for b in B_GRID:
            for Wp in WG_GRID:
                rec = grid_a[cell_key("P-STUB", T, s, b, Wp)]
                fl, sp = rec["floors"], rec["spacings"]
                if any(fl[i] >= fl[i + 1] for i in range(len(fl) - 1)):
                    monotone_ok = False
                if any(sp[i] < sp[i + 1] for i in range(len(sp) - 1)):
                    monotone_ok = False
check("F2 MONOTONE THRASH — F_k strictly increasing and Delta_k non-increasing at every P-STUB grid cell", monotone_ok)

# ---------------------------------------------------------------- F3 anchors
AN = FX["anchors"]["decision_cell"]
check("F3 N*_stub == 233", dec_a["Nstar"] == AN["Nstar_stub"])
check("F3 K == 51", dec_a["K"] == AN["K"])
check("F3 first spacing == 13 (value gated; the as-written expression is anomaly A1)", dec_a["spacings"][0] == AN["first_spacing"])
check("F3 first floor == 39,330", dec_a["floors"][0] == AN["first_floor"])
check("F3 collapse index == 34", collapse_a == AN["collapse_index"])
check("F3 thrash roll count == 18", thrash_a == AN["thrash_roll_count"])
check("F3 saturation floor == 205,930", dec_a["floors"][-1] == AN["saturation_floor"])
check("F3 wall composition == 122,430 / 51,000 / 32,000 / 500", dec_a["composition"] == AN["composition"])
check("F3 N*_range == 671", rng_a["Nstar"] == AN["Nstar_range"])
check("F3 P-COMPACT floor == 34,030", cmp_a["floors"] and set(cmp_a["floors"]) == {AN["compact_floor"]})

# anomaly A1 — the disclosed first-spacing derivation expression, asserted
a1_as_written = ceil_div(204800 - 32500, 16000)
a1_correct = ceil_div(204800 - 500, 16000)
check("A1 as-written expression ceil((204800-32500)/16000) == 11 != 13 == ceil((204800-500)/16000) == event walk",
      a1_as_written == 11 and a1_correct == 13 and dec_a["spacings"][0] == 13)

# ---------------------------------------------------------------- F4 hand world
HW = FX["anchors"]["hand_world"]
hw_a = arm_a(HW["T"], HW["s"], HW["b"], HW["W"], HW["h_r"], HW["H0"], "P-STUB", CAP)
hw_b = arm_b(HW["T"], HW["s"], HW["b"], HW["W"], HW["h_r"], HW["H0"], "P-STUB", CAP)
check("F4 hand world N* == 18, K == 8, both arms",
      hw_a["Nstar"] == HW["Nstar"] == hw_b["Nstar"] and hw_a["K"] == HW["K"] == hw_b["K"])
check("F4 hand world spacings (5,3,3,2,2,1,1,1) both arms",
      hw_a["spacings"] == HW["spacings"] == hw_b["spacings"])
check("F4 hand world floors (43,54,65,74,83,90,97,104) both arms",
      hw_a["floors"] == HW["floors"] == hw_b["floors"])

# ---------------------------------------------------------------- F5 degeneracies
DG1 = FX["anchors"]["degeneracy_s_eq_b"]
dg1_a = arm_a(DEC["T"], DG1["s"], DEC["b"], DEC["W"], HR_D, H0_D, "P-STUB", CAP)
dg1_b = arm_b(DEC["T"], DG1["s"], DEC["b"], DEC["W"], HR_D, H0_D, "P-STUB", CAP)
check("F5 degeneracy s == b == 16000: N* == 13, both arms",
      dg1_a["Nstar"] == DG1["Nstar"] == dg1_b["Nstar"])
DG2 = FX["anchors"]["degeneracy_true_deletion"]
dg2_a = arm_a(DEC["T"], DG2["s"], DEC["b"], DEC["W"], DG2["h_r"], H0_D, "P-STUB", CAP)
dg2_b = arm_b(DEC["T"], DG2["s"], DEC["b"], DEC["W"], DG2["h_r"], H0_D, "P-STUB", CAP)
check("F5 degeneracy s == 0 and h_r == 0: no saturation in 100,000 appends, floor constant 32,500, both arms full length",
      (not dg2_a["saturated"]) and (not dg2_b["saturated"])
      and set(dg2_a["floors"]) == {DG2["constant_floor"]} and set(dg2_b["floors"]) == {DG2["constant_floor"]})

# =====================================================================
# Arm R — seeded, REPORTING-ONLY
# =====================================================================
Q14 = Fraction(1, 4)
Q34 = Fraction(3, 4)

def arm_r_episode(rng):
    T, s, Wp, h_r, H0 = DEC["T"], DEC["s"], DEC["W"], HR_D, H0_D
    fulls = []
    stub_mass = 0
    receipts = 0
    total = H0
    appends = 0
    draws = 0
    while True:
        u = rng.random()
        draws += 1
        fu = Fraction(u)
        if fu < Q14:
            bsz = 8000
        elif fu < Q34:
            bsz = 16000
        else:
            bsz = 24000
        appends += 1
        fulls.append(bsz)
        total += bsz
        if total >= T:
            receipts += 1
            evict = len(fulls) - Wp if len(fulls) > Wp else 0
            fulls = fulls[evict:]
            stub_mass += evict * s
            total = H0 + receipts * h_r + stub_mass + sum(fulls)
            if total >= T:
                return appends, draws


def arm_r_leg(seed, episodes):
    rng = LoggedRandom(seed)
    walls = []
    total_draws = 0
    draws_ok = True
    for _ in range(episodes):
        nstar, draws = arm_r_episode(rng)
        if draws != nstar:
            draws_ok = False
        walls.append(nstar)
        total_draws += draws
    walls_sorted = sorted(walls)
    mean = Fraction(sum(walls), len(walls))
    return {
        "episodes": episodes,
        "total_draws": total_draws,
        "draws_ok": draws_ok,
        "min": walls_sorted[0],
        "max": walls_sorted[-1],
        "median": walls_sorted[len(walls_sorted) // 2],
        "mean_fraction": "%d/%d" % (mean.numerator, mean.denominator),
        "mean_float": repr(float(mean)),
        "share_below_233": repr(sum(1 for w in walls if w < 233) / len(walls)),
        "share_at_233": repr(sum(1 for w in walls if w == 233) / len(walls)),
        "share_above_233": repr(sum(1 for w in walls if w > 233) / len(walls)),
    }

leg_main = arm_r_leg(FX["seeds"]["main"], FX["arm_R_params"]["episodes_main"])
leg_stab = arm_r_leg(FX["seeds"]["stability"], FX["arm_R_params"]["episodes_stability"])
check("F6 Arm-R draw sentinels — exactly one uniform per appended proposal, both legs",
      leg_main["draws_ok"] and leg_stab["draws_ok"])

# =====================================================================
# Twin decision evaluators (independently coded; registered order)
# =====================================================================
DR = FX["decision_rule"]

def evaluator_A():
    """Reads Arm-A numbers."""
    gates_green = CHECKS["failed"] == 0
    nstar = dec_a["Nstar"]
    reject = (
        nstar <= DR["REJECT"]["Nstar_stub_max"]
        and thrash_a >= DR["REJECT"]["thrash_rolls_min"]
        and rng_a["Nstar"] <= 4 * nstar
        and (not cmp_a["saturated"]) and set(cmp_a["floors"]) == {compact_const}
    )
    if reject and gates_green:
        return "REJECT"
    if not gates_green:
        return "INVALID"
    first20 = dec_a["spacings"][:20]
    if nstar >= DR["APPROVE"]["Nstar_stub_min"] and len(first20) == 20 and min(first20) >= 4:
        return "APPROVE"
    return "NULL"


def evaluator_B():
    """Reads Arm-B numbers; band logic written separately (subtraction form)."""
    if CHECKS["failed"] > 0:
        # registered order puts REJECT first, but a gate failure means no
        # number is trusted — INVALID short-circuits (C7)
        pass
    n = dec_b["Nstar"]
    clause1 = (DR["REJECT"]["Nstar_stub_max"] - n) >= 0
    clause2 = (thrash_b - DR["REJECT"]["thrash_rolls_min"]) >= 0
    clause3 = (4 * n - rng_b["Nstar"]) >= 0
    clause4 = (cmp_b["saturated"] is False) and all(f == compact_const for f in cmp_b["floors"])
    if clause1 and clause2 and clause3 and clause4 and CHECKS["failed"] == 0:
        return "REJECT"
    if CHECKS["failed"] > 0:
        return "INVALID"
    sp20 = dec_b["spacings"][:20]
    if (n - DR["APPROVE"]["Nstar_stub_min"]) >= 0 and len(sp20) == 20 and all(x >= 4 for x in sp20):
        return "APPROVE"
    return "NULL"

# =====================================================================
# Drafter comparison (NEVER gated) + reporting rows
# =====================================================================
DD = FX["drafter_disclosed_never_gated"]
comparisons = []

def compare(name, disclosed, computed):
    comparisons.append({"name": name, "disclosed": disclosed, "computed": computed, "match": disclosed == computed})

wt = {str(Wp): [grid_a[cell_key("P-STUB", DEC["T"], DEC["s"], b, Wp)]["Nstar"] for b in B_GRID] for Wp in WG_GRID}
compare("wall table N*(W, b) at T=204800 s=530", DD["wall_table_stub_W_by_b"], wt)
sg = {str(s): grid_a[cell_key("P-STUB", DEC["T"], s, DEC["b"], DEC["W"])]["Nstar"] for s in S_GRID}
compare("s-grid walls", DD["s_grid_walls"], sg)
tg = {str(T): grid_a[cell_key("P-STUB", T, DEC["s"], DEC["b"], DEC["W"])]["Nstar"] for T in T_GRID}
compare("T-grid walls", DD["T_grid_walls"], tg)
t4_sp = grid_a[cell_key("P-STUB", 409600, DEC["s"], DEC["b"], DEC["W"])]["spacings"][:20]
compare("T=409600 first-20 spacings all >= 12 (APPROVE cell)", True, len(t4_sp) == 20 and min(t4_sp) >= DD["T_409600_first_20_spacings_min"])
h150 = arm_a(DEC["T"], 150, DEC["b"], DEC["W"], HR_D, H0_D, "P-STUB", CAP)
compare("heading-only 150 B stub wall", DD["heading_only_150B_stub_wall"], h150["Nstar"])
t200k = arm_a(200000, DEC["s"], DEC["b"], DEC["W"], HR_D, H0_D, "P-STUB", CAP)
compare("T = 200,000-decimal reading wall", DD["T_200000_decimal_wall"], t200k["Nstar"])
compare("collapse proposal (drafter approx-tagged '~208')", DD["collapse_proposal_approx"], collapse_proposal)
sat_floor = dec_a["floors"][-1]
shares = {kk: Fraction(vv * 100, sat_floor) for kk, vv in dec_a["composition"].items()}
compare("stub share % (drafter 59.4, truncation of exact)", DD["stub_share_at_wall_pct"], round(float(shares["stub"]), 1))
compare("receipt share %", DD["receipt_share_at_wall_pct"], round(float(shares["receipts"]), 1))
compare("window share %", DD["window_share_at_wall_pct"], round(float(shares["window"]), 1))
mult = Fraction(rng_a["Nstar"], dec_a["Nstar"])
compare("range multiplier ~2.88", DD["multiplier_approx"], round(float(mult), 2))

# reporting rows (C6)
RP = FX["reporting_rows"]
pace = Fraction(RP["pace"]["proposal_intervals"]) / Fraction(RP["pace"]["days"])
days_remaining = Fraction(dec_a["Nstar"] - RP["pace"]["pipeline_at"]) / pace
ref = date.fromisoformat(RP["pace"]["reference_date"])
wall_date = ref + timedelta(days=ceil_div(days_remaining.numerator, days_remaining.denominator))
retro_floor = H0_D + 1 * HR_D + RP["retrodiction"]["n"] * DEC["s"] + RP["retrodiction"]["W"] * DEC["b"]
roll2_delta = ceil_div(DEC["T"] - retro_floor, DEC["b"])
roll2_fulls = RP["retrodiction"]["W"] + roll2_delta
compare("retrodicted post-roll-1 floor", RP["retrodiction"]["predicted_floor"], retro_floor)
compare("roll-2 forecast fulls", RP["roll2_forecast"]["predicted_fulls_at_roll2"], roll2_fulls)
compare("wall date at observed pace", RP["pace"]["disclosed_wall_date_approx"], wall_date.isoformat())

# ---------------------------------------------------------------- F6 battery tail
# presentation seed — constructed here, read by the shuffled stdout listing only
PRESENT_RNG = LoggedRandom(FX["seeds"]["presentation"])
check("F6 aux seed %d never read — constructor registry == [main, stability, presentation] exactly" % FX["seeds"]["aux_never_read"],
      SEED_REGISTRY == [FX["seeds"]["main"], FX["seeds"]["stability"], FX["seeds"]["presentation"]]
      and FX["seeds"]["aux_never_read"] not in SEED_REGISTRY)

ruling_a = evaluator_A()
ruling_b = evaluator_B()
check("F6 twin decision evaluators agree on the ruling token", ruling_a == ruling_b)

# =====================================================================
# Publication
# =====================================================================

def frac_str(fr):
    return "%d/%d" % (fr.numerator, fr.denominator)

results = {
    "verdict": ruling_a,
    "evaluators": {"A": ruling_a, "B": ruling_b},
    "decision_cell": {
        "cell": DEC,
        "Nstar_stub": dec_a["Nstar"],
        "K": dec_a["K"],
        "first_spacing": dec_a["spacings"][0],
        "first_floor": dec_a["floors"][0],
        "collapse_index": collapse_a,
        "collapse_proposal": collapse_proposal,
        "thrash_roll_count": thrash_a,
        "saturation_floor": dec_a["floors"][-1],
        "composition": dec_a["composition"],
        "composition_shares_pct": {kk: {"exact": frac_str(vv), "float": repr(float(vv))} for kk, vv in shares.items()},
        "Nstar_range": rng_a["Nstar"],
        "range_multiplier": {"exact": frac_str(mult), "float": repr(float(mult))},
        "compact_floor_constant": compact_const,
        "compact_spacing_constant": FX["anchors"]["decision_cell"]["compact_spacing"],
        "spacing_series": dec_a["spacings"],
        "floor_series": dec_a["floors"],
    },
    "wall_table": {
        key: (
            {"Nstar": rec["Nstar"], "K": rec["K"], "composition": rec["composition"]}
            if rec["saturated"]
            else {"unbounded": True, "walk_appends": rec["walk_appends"], "constant_floor": rec["constant_floor"], "K": rec["K"]}
        )
        for key, rec in sorted(grid_a.items())
    },
    "theorems": {
        "floor_law_timing_invariance": timing_ok,
        "receipt_free_invariance": {"wall": rf_expect, "b_grid_walls": rf_walls, "identical": len(set(rf_walls)) == 1},
        "compact_boundedness": {"constant_floor": compact_const, "constant_spacing": FX["anchors"]["decision_cell"]["compact_spacing"], "walk_appends": cmp_a["walk_appends"], "held": compact_ok},
        "monotone_thrash": monotone_ok,
    },
    "hand_world": {"Nstar": hw_a["Nstar"], "K": hw_a["K"], "spacings": hw_a["spacings"], "floors": hw_a["floors"]},
    "degeneracies": {
        "s_eq_b_16000": {"Nstar": dg1_a["Nstar"]},
        "true_deletion": {"saturated": dg2_a["saturated"], "constant_floor": DG2["constant_floor"], "walk_appends": dg2_a["walk_appends"]},
    },
    "arm_R": {"main": leg_main, "stability": leg_stab, "deterministic_wall": dec_a["Nstar"], "note": "REPORTING-ONLY; no statistical gate"},
    "drafter_comparison_never_gated": comparisons,
    "anomalies": {
        "A1": "the disclosed first-spacing derivation 'ceil((204800 - 32500)/16000)' evaluates to %d, not the anchored 13; the event-walk-correct expression is ceil((204800 - 500)/16000) = %d; the anchor VALUE 13 is confirmed by the walk and by the rest of the disclosed landing (N* = 233, K = 51); ruling-neutral" % (a1_as_written, a1_correct)
    },
    "reporting": {
        "wall_date_at_observed_pace": wall_date.isoformat(),
        "days_remaining_exact": frac_str(days_remaining),
        "retrodicted_post_roll_1_floor": retro_floor,
        "measured_live_file": RP["retrodiction"]["measured_live_file"],
        "roll2_forecast_fulls": roll2_fulls,
        "live_fulls_at_head": RP["roll2_forecast"]["live_fulls_at_head"],
        "T_200000_decimal_wall": t200k["Nstar"],
        "heading_only_150B_stub_wall": h150["Nstar"],
    },
    "seed_registry": SEED_REGISTRY,
    "self_checks": {"total": CHECKS["total"], "failed": CHECKS["failed"], "failures": CHECKS["failures"]},
    "runtime": {"python": "cpython %d.%d" % sys.version_info[:2], "stdlib_only": True},
}

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=1, sort_keys=True)
    fh.write("\n")

# ------------------------------------------------------------------- stdout
out = []
out.append("VERDICT 078 — outbox rollover stub saturation (idea-engine PROPOSAL 065)")
out.append("runtime: cpython %d.%d.%d, stdlib-only, hermetic" % sys.version_info[:3])
out.append("")
out.append("== decision cell (P-STUB, T=204800, s=530, b=16000, W=2, h_r=1000, H0=500) ==")
out.append("N*_stub     = %d  (REJECT needs <= 300, APPROVE needs >= 500)" % dec_a["Nstar"])
out.append("K           = %d rolls; first spacing %d; first floor %d" % (dec_a["K"], dec_a["spacings"][0], dec_a["floors"][0]))
out.append("collapse    = roll %d (proposal %d); thrash rolls (spacing <= 2) = %d (REJECT needs >= 8)" % (collapse_a, collapse_proposal, thrash_a))
out.append("sat. floor  = %d = stub %d + receipts %d + window %d + header %d" % (dec_a["floors"][-1], dec_a["composition"]["stub"], dec_a["composition"]["receipts"], dec_a["composition"]["window"], dec_a["composition"]["header"]))
out.append("shares      = stub %s%% / receipts %s%% / window %s%% / header %s%%" % tuple(repr(round(float(shares[kk]), 4)) for kk in ("stub", "receipts", "window", "header")))
out.append("N*_range    = %d; multiplier %s = %s (REJECT needs <= 4x)" % (rng_a["Nstar"], frac_str(mult), repr(float(mult))))
out.append("P-COMPACT   = constant floor %d, constant spacing %d, over %d appends (unbounded)" % (compact_const, FX["anchors"]["decision_cell"]["compact_spacing"], cmp_a["walk_appends"]))
out.append("spacings    = %s" % ",".join(str(x) for x in dec_a["spacings"]))
out.append("")
out.append("== P-STUB wall table N*(T, s, b, W) — order presentation-shuffled, seed %d ==" % FX["seeds"]["presentation"])
stub_keys = [k for k in sorted(grid_a) if k.startswith("P-STUB")]
PRESENT_RNG.shuffle(stub_keys)
for kk in stub_keys:
    out.append("  %-38s N* = %d" % (kk, grid_a[kk]["Nstar"]))
out.append("")
out.append("== structure theorems ==")
out.append("FLOOR LAW + timing invariance (roll-every-25 alternate schedule): %s — gated F2a" % timing_ok)
out.append("RECEIPT-FREE INVARIANCE: wall = ceil((T-H0)/s) = %d, identical across b in {8000,16000,24000}: %s — gated F2b" % (rf_expect, rf_walls == [rf_expect] * 3))
out.append("COMPACT BOUNDEDNESS: floor constant %d, spacing constant %d over %d appends — gated F2c" % (compact_const, FX["anchors"]["decision_cell"]["compact_spacing"], cmp_a["walk_appends"]))
out.append("MONOTONE THRASH at every P-STUB cell: %s — gated F2" % monotone_ok)
out.append("")
out.append("== hand world / degeneracies ==")
out.append("hand world: N*=%d K=%d spacings=%s floors=%s" % (hw_a["Nstar"], hw_a["K"], hw_a["spacings"], hw_a["floors"]))
out.append("s=b=16000: N*=%d; true deletion (s=0,h_r=0): unbounded, floor %d over %d appends" % (dg1_a["Nstar"], DG2["constant_floor"], dg2_a["walk_appends"]))
out.append("")
out.append("== Arm R (seeded, REPORTING-ONLY; no statistical gate) ==")
for label, leg in (("main", leg_main), ("stability", leg_stab)):
    out.append("%s leg (n=%d): wall mean %s (exact %s), min %d, median %d, max %d; share below/at/above 233: %s/%s/%s; draws %d (1/proposal, asserted)"
               % (label, leg["episodes"], leg["mean_float"], leg["mean_fraction"], leg["min"], leg["median"], leg["max"],
                  leg["share_below_233"], leg["share_at_233"], leg["share_above_233"], leg["total_draws"]))
out.append("deterministic wall at the decision cell: %d (mix drift is a named finding, never a ruling)" % dec_a["Nstar"])
out.append("")
out.append("== drafter comparison (NEVER gated) ==")
mism = [c["name"] for c in comparisons if not c["match"]]
out.append("%d/%d disclosed rows reproduced; mismatches: %s" % (len(comparisons) - len(mism), len(comparisons), mism))
out.append("anomaly A1: as-written first-spacing expression = %d, anchored value = 13, event walk = 13 (expression slip, ruling-neutral)" % a1_as_written)
out.append("")
out.append("== reporting rows ==")
out.append("wall date at observed pace (63 intervals / 4.43 days, pipeline at 64): %s (days remaining %s ~ %s)" % (wall_date.isoformat(), frac_str(days_remaining), repr(round(float(days_remaining), 4))))
out.append("retrodicted post-roll-1 floor %d vs measured live file %d (gap = un-modeled block families + pending fulls, REJECT-ward, disclosed F1 boundary)" % (retro_floor, RP["retrodiction"]["measured_live_file"]))
out.append("roll-2 forecast: %d full blocks at trigger (live file held %d at the drafting HEAD)" % (roll2_fulls, RP["roll2_forecast"]["live_fulls_at_head"]))
out.append("T-as-200,000-decimal wall: %d (immaterial to every band, disclosed)" % t200k["Nstar"])
out.append("")
out.append("== self-checks: %d total, %d failed ==" % (CHECKS["total"], CHECKS["failed"]))
if CHECKS["failures"]:
    for f in CHECKS["failures"]:
        out.append("  FAILED: %s" % f)
out.append("")
out.append("== RULING (pre-registered order REJECT -> INVALID -> APPROVE -> NULL) ==")
out.append("evaluator A: %s   evaluator B: %s" % (ruling_a, ruling_b))
sys.stdout.write("\n".join(out) + "\n")

sys.exit(0 if CHECKS["failed"] == 0 else 1)
