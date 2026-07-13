#!/usr/bin/env python3
"""VERDICT 054 — Brineward band-2 necessity: does the committed loot/price
ladder actually force the deeps, or is shallow grinding a viable route to the
full upgrade ladder?

Serves idea-engine PROPOSAL 043 (## PROPOSAL 043 · 2026-07-13T19:11:37Z ·
status: sim-ready; idea doc ideas/gba-homebrew/
brineward-band-necessity-2026-07-13.md @ ea3744d, landed via idea-engine PR
#337; claim idea-engine PR #338). Committed game tables quoted verbatim from
menno420/gba-homebrew @ 8bac80a70c82096828663d501af5f2790acbccc4.

Arm A (DECISION arm): seedless exact fractions.Fraction enumeration —
renewal-reward over the sink-to-sink cycle, closed form; the zero-sink branch
is the pure loop rate exactly (proposal: "the zero-sink branch handled exactly
as the pure loop rate — reachable by construction at D0=20, band 2, m=1, max
cumulative damage 90 < 100").

Arm S (confirmation arm): seeded Monte Carlo, seeds 20261309 (main) /
20261310 (stability) / 20261311 (sensitivity) / 20261312 (aux, NEVER read).
"one damage draw per water in pinned order"; every MC number is an exact
Fraction (integer gold over integer twentieths of a water-unit) — zero float
thresholds anywhere.

Hermetic: reads only its own fixtures.json. Stdlib only. Deterministic:
stdout + results.json byte-identical across process runs (no wall-clock
anywhere). Decision rule pre-registered, evaluated in order, REJECT FIRST
(proposal: 'REJECT ... NEC(cell) < 5/4 in >= 5 of 9 cells — checked FIRST').
"""
import json
import os
import platform
import random
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = json.load(open(os.path.join(HERE, "fixtures.json")))

# ---------------------------------------------------------------- self-checks
_PASS = [0]


def gate(cond, label):
    if not cond:
        print("GATE FAIL: %s" % label)
        print("SELF-CHECKS: %d passed, 1 failed" % _PASS[0])
        sys.exit(1)
    _PASS[0] += 1


ANOMALIES = []


def anomaly(line):
    ANOMALIES.append(line)
    print("!! FIRST-CLASS ANOMALY: %s" % line)


# ---------------------------------------------------------------- constants
gate(".".join(platform.python_version_tuple()[:2]) == FIX["cpython_minor"],
     "CPython minor pinned %s" % FIX["cpython_minor"])

CT = FIX["committed_tables"]
LOOT = CT["BW_BAND_LOOT_VALUE_OF"]          # {5, 12, 25} @ 8bac80a
UPCOST = CT["BW_UP_COST"]                   # {0, 15, 45} @ 8bac80a
TRACKS = CT["upgrade_tracks"]               # 3
LADDER = CT["ladder_total_gold"]            # 180
DROPS = CT["BW_LOOT_DROPS"]                 # 3
HOLD_CAP = CT["BW_HOLD_CAP"]                # 8
REPAIR_PER_GOLD = CT["BW_REPAIR_PER_GOLD"]  # 4
HULL_MAX = CT["BW_HULL_MAX"]                # 100 (tier 0; sink threshold)

# F1 — ladder-total identity, asserted from the committed table.
gate((UPCOST[1] + UPCOST[2]) * TRACKS == LADDER,
     "F1 ladder identity (15 + 45) * 3 = 180 from BW_UP_COST")

T_BASE = [F(x) for x in FIX["model"]["duel_time_per_band"]]        # {1,3/2,3/2}
T_HP = [F(x) for x in FIX["sensitivity_values"]
        ["duel_time_hull_proportional"]]                            # {1,13/10,8/5}
D0_AXIS = FIX["model"]["D0_axis"]                                  # {20,35,50}
TDOCK_AXIS = [F(x) for x in FIX["model"]["T_dock_axis"]]           # {1/2,1,2}
DTAB = {int(k): v for k, v in
        FIX["model"]["damage_tables_round_half_up"].items()}
CENTRAL = (F(FIX["model"]["central_cell"][0]),
           F(FIX["model"]["central_cell"][1]))                     # (35, 1)
THETA = FIX["model"]["theta_hull_bank_trigger"]                    # 50
THETAS = FIX["sensitivity_values"]["theta_variants"]               # {30, 70}
SINK_AT = FIX["model"]["sink_threshold_cum_damage"]                # 100
gate(SINK_AT == HULL_MAX, "sink threshold = BW_HULL_MAX at tier 0")

# committed-derived damage-ratio spot check: D_b = round-half-up(D0 * r_b)
RATIO = [F(x) for x in FIX["model"]["damage_ratio_committed_derived"]]
for d0 in D0_AXIS:
    for b in range(3):
        want = int(F(d0) * RATIO[b] + F(1, 2))  # round half up
        gate(DTAB[d0][b] == want,
             "damage table D0=%d band %d = %d (round half up on r_b)"
             % (d0, b, want))

W5 = [F(1, 8), F(1, 4), F(1, 4), F(1, 4), F(1, 8)]
W7 = [F(1, 16), F(1, 8), F(1, 8), F(3, 8), F(1, 8), F(1, 8), F(1, 16)]
gate(sum(W5) == 1, "5-point pmf sums to 1")
gate(sum(W7) == 1, "7-point pmf sums to 1")


def support5(D):
    """Proposal (verbatim): '{0, |_D_b/2_|, D_b, D_b + |~D_b/2~|, 2*D_b}'."""
    return [0, D // 2, D, D + (D + 1) // 2, 2 * D]


def support7(D):
    """Sensitivity support. Proposal: '{0, D/2, 3D/4, D, 5D/4, 3D/2, 2D} pmf
    {1/16, 1/8, 1/8, 3/8, 1/8, 1/8, 1/16}, mean exactly D, quarter terms
    floored and disclosed'. Sub-D terms floored, above-D mirrors carry the
    compensating ceil (the committed 5-point convention) so the F4 exact-mean
    identity holds for every integer D — disclosed in fixtures.json."""
    return [0, D // 2, (3 * D) // 4, D,
            D + (D + 3) // 4, D + (D + 1) // 2, 2 * D]


# F4 — damage-pmf mean identity, every band, axis point, both supports.
for d0 in [0] + D0_AXIS:
    for b in range(3):
        D = DTAB[d0][b] if d0 in DTAB else 0
        gate(sum(w * v for w, v in zip(W5, support5(D))) == D,
             "F4 mean identity 5pt D0=%d band %d (D=%d)" % (d0, b, D))
        gate(sum(w * v for w, v in zip(W7, support7(D))) == D,
             "F4 mean identity 7pt D0=%d band %d (D=%d)" % (d0, b, D))

# F6 — repair identities: cum damage h pays ceil(h/4).
def repair(cum):
    return (cum + REPAIR_PER_GOLD - 1) // REPAIR_PER_GOLD


for h, cost in sorted((int(k), v)
                      for k, v in FIX["hand_fixture"]["F6_repair_spots"].items()):
    gate(repair(h) == cost, "F6 repair spot h=%d -> %dg" % (h, cost))

SEEDS = FIX["seeds"]
gate(min(SEEDS[k] for k in ("main", "stability", "sensitivity",
                            "aux_never_read")) > 20261308,
     "seeds strictly above the V053 registry high-water 20261308")
W_MAIN = FIX["waters_per_leg"]["main"]
W_STAB = FIX["waters_per_leg"]["stability"]
W_SENS = FIX["waters_per_leg"]["sensitivity"]
GATE_MAIN = F(FIX["agreement_gates"]["main_rel"])
GATE_WIDE = F(FIX["agreement_gates"]["stability_rel"])
SE_HEADROOM = FIX["agreement_gates"]["se_headroom_min"]
REJECT_BAND = F(FIX["decision_rule"]["reject_band"])       # 5/4
APPROVE_BAND = F(FIX["decision_rule"]["approve_band"])     # 3/2
REJECT_CELLS = FIX["decision_rule"]["reject_cells_of_9"]   # 5
APPROVE_CELLS = FIX["decision_rule"]["approve_cells_of_9"] # 7

CELLS = [(d0, td) for d0 in D0_AXIS for td in TDOCK_AXIS]  # pinned order


def cell_id(d0, td):
    return "D0=%d/Td=%s" % (d0, td)


CENTRAL_ID = cell_id(int(CENTRAL[0]), CENTRAL[1])

# pinned policy order: GRIND(b,m) b outer, m inner; then GRIND-H likewise
POLICIES = ([("GRIND", b, m) for b in range(3) for m in (1, 2, 3)]
            + [("GRIND-H", b, m) for b in range(3) for m in (1, 2, 3)])
POLICIES_M4 = ([("GRIND", b, m) for b in range(3) for m in (1, 2, 3, 4)]
               + [("GRIND-H", b, m) for b in range(3) for m in (1, 2, 3, 4)])
M4_NEW = [("GRIND", b, 4) for b in range(3)] + [("GRIND-H", b, 4)
                                                for b in range(3)]


def pol_name(p):
    return "%s(%d,%d)" % (p[0], p[1], p[2])


gate([pol_name(p) for p in POLICIES] == FIX["policies"]["pinned_order"],
     "policy pinned order matches fixtures")


# ---------------------------------------------------------------- Arm A core
class Cfg(object):
    """One model configuration: a cell plus variant knobs."""

    def __init__(self, dmg, tdock, t=None, sup="5", theta=THETA, rho=F(0)):
        self.dmg = dmg          # per-band damage [D_0, D_1, D_2]
        self.tdock = tdock      # F
        self.t = t or T_BASE    # per-band duel time, F
        self.sup = sup          # "5" | "7"
        self.theta = theta      # GRIND-H hull trigger
        self.rho = rho          # post-sink restart overhead, F

    def draws(self, band):
        D = self.dmg[band]
        if self.sup == "5":
            return list(zip(support5(D), W5))
        return list(zip(support7(D), W7))


def loop_seg_enum(cfg, b, m, hbank):
    """Exact enumeration of one loop segment (starts full hull, empty hold).
    Proposal: 'loop {fight m waters in band b, pier-bank + repair}';
    GRIND-H 'banks + repairs early whenever hull <= 50 after a won water'.
    Returns outcomes (prob, banked_gold, time, waters, wasted, sink, hold_gold).
    banked_gold is net of repair; hold_gold is the pre-repair hold at bank
    (0 on sink — 'sink forfeits the unbanked hold')."""
    out = []
    tb = cfg.t[b]
    draws = cfg.draws(b)

    def walk(i, cum, crates, gold, time, wasted, prob):
        for d, w in draws:
            p = prob * w
            c = cum + d
            if c >= SINK_AT:
                # 'the sinking draw resolving before the win';
                # 'sinking water costs t_b/2'
                out.append((p, 0, time + tb / 2, i, wasted, True, 0))
                continue
            t2 = time + tb
            take = min(DROPS, HOLD_CAP - crates)
            crates2, gold2 = crates + take, gold + take * LOOT[b]
            waste2 = wasted + (DROPS - take)
            if i == m or (hbank and HULL_MAX - c <= cfg.theta):
                out.append((p, gold2 - repair(c), t2 + cfg.tdock, i, waste2,
                            False, gold2))
            else:
                walk(i + 1, c, crates2, gold2, t2, waste2, p)

    walk(1, 0, 0, 0, F(0), 0, F(1))
    return out


def descent_enum(cfg, b, hbank):
    """Exact enumeration of the descent: 'descend by winning one water per
    band 0..b-1 (scooping en route), pier-bank + repair at descent end';
    'sinking restarts the descent'. Returns outcomes
    (prob, banked_gold, time, waters, wasted, sink, last_hold_gold)."""
    if b == 0:
        return [(F(1), 0, F(0), 0, 0, False, 0)]
    out = []

    def walk(k, cum, crates, gold, time, banked, wasted, prob):
        tb = cfg.t[k]
        for d, w in cfg.draws(k):
            p = prob * w
            c = cum + d
            if c >= SINK_AT:
                out.append((p, banked, time + tb / 2, k + 1, wasted, True, 0))
                continue
            t2 = time + tb
            take = min(DROPS, HOLD_CAP - crates)
            crates2, gold2 = crates + take, gold + take * LOOT[k]
            waste2 = wasted + (DROPS - take)
            if k == b - 1:
                # descent-end bank (regardless of the GRIND-H trigger:
                # one bank, never two)
                out.append((p, banked + gold2 - repair(c), t2 + cfg.tdock,
                            b, waste2, False, gold2))
            elif hbank and HULL_MAX - c <= cfg.theta:
                # GRIND-H mid-descent bank+repair, then keep descending
                walk(k + 1, 0, 0, 0, t2 + cfg.tdock,
                     banked + gold2 - repair(c), waste2, p)
            else:
                walk(k + 1, c, crates2, gold2, t2, banked, waste2, p)

    walk(0, 0, 0, 0, F(0), 0, 0, F(1))
    return out


def policy_stats(cfg, pol):
    """Exact long-run banked-gold rate G by renewal-reward over the
    sink-to-sink cycle, plus reporting + SE quantities."""
    kind, b, m = pol
    hbank = kind == "GRIND-H"
    loop = loop_seg_enum(cfg, b, m, hbank)
    desc = descent_enum(cfg, b, hbank)
    # post-sink restart overhead rides every sink (base 0; sensitivity T_dock)
    loop = [(p, g, t + (cfg.rho if s else 0), w, x, s, hg)
            for p, g, t, w, x, s, hg in loop]
    desc = [(p, g, t + (cfg.rho if s else 0), w, x, s, hg)
            for p, g, t, w, x, s, hg in desc]

    q = sum(p for p, g, t, w, x, s, hg in loop if s)
    A = sum(p * g for p, g, t, w, x, s, hg in loop)
    B = sum(p * t for p, g, t, w, x, s, hg in loop)
    Wseg = sum(p * w for p, g, t, w, x, s, hg in loop)
    waste_seg = sum(p * x for p, g, t, w, x, s, hg in loop)
    PD = sum(p for p, g, t, w, x, s, hg in desc if not s)
    Gd = sum(p * g for p, g, t, w, x, s, hg in desc)
    Td = sum(p * t for p, g, t, w, x, s, hg in desc)
    Wd = sum(p * w for p, g, t, w, x, s, hg in desc)
    waste_desc = sum(p * x for p, g, t, w, x, s, hg in desc)

    if q == 0:
        # zero-sink branch: the pure loop rate exactly (proposal, verbatim:
        # 'the zero-sink branch ... handled exactly as the pure loop rate')
        G = A / B
        var_x = sum(p * (g - G * t) ** 2 for p, g, t, w, x, s, hg in loop)
        e_t_unit, e_w_unit = B, Wseg
    else:
        ER = Gd + PD * A / q
        ET = Td + PD * B / q
        G = ER / ET
        mu_c = sum(p * (g - G * t) for p, g, t, w, x, s, hg in loop if not s)
        mu_x = sum(p * (g - G * t) for p, g, t, w, x, s, hg in loop if s)
        m2_c = sum(p * (g - G * t) ** 2 for p, g, t, w, x, s, hg in loop
                   if not s)
        m2_x = sum(p * (g - G * t) ** 2 for p, g, t, w, x, s, hg in loop if s)
        e_s = (mu_c + mu_x) / q
        e_s2 = (m2_c + m2_x + 2 * mu_c * e_s) / q
        var_x = F(0)
        for p, g, t, w, x, s, hg in desc:
            xd = g - G * t
            if s:
                var_x += p * xd ** 2
            else:
                var_x += p * (xd ** 2 + 2 * xd * e_s + e_s2)
        e_t_unit = ET
        e_w_unit = Wd + PD * Wseg / q
    # SE^2 of the MC ratio estimator at W waters = se2w / W (asymptotic
    # renewal-reward CLT: Var(R - G*T per renewal unit) / (N * E[T]^2),
    # N = W / E[waters per renewal unit])
    se2w = var_x * e_w_unit / (e_t_unit ** 2)
    return {"G": G, "q_loop": q, "p_sink_descent": 1 - PD,
            "waste_seg": waste_seg, "waste_desc": waste_desc,
            "e_waters_unit": e_w_unit, "se2w": se2w}


def arm_a_tables(mk_cfg, policies):
    """Full policy x 9-cell exact tables for one variant."""
    out = {}
    for d0, td in CELLS:
        cfg = mk_cfg(d0, td)
        out[cell_id(d0, td)] = {pol_name(p): policy_stats(cfg, p)
                                for p in policies}
    return out


def cfg_base(d0, td):
    return Cfg(DTAB[d0], td)


VARIANT_CFGS = {
    "base": cfg_base,
    "t_hull_proportional": lambda d0, td: Cfg(DTAB[d0], td, t=T_HP),
    "support_7pt": lambda d0, td: Cfg(DTAB[d0], td, sup="7"),
    "m_4": cfg_base,  # base config, extended family
    "theta_30": lambda d0, td: Cfg(DTAB[d0], td, theta=THETAS[0]),
    "theta_70": lambda d0, td: Cfg(DTAB[d0], td, theta=THETAS[1]),
    "restart_T_dock": lambda d0, td: Cfg(DTAB[d0], td, rho=td),
}
VARIANT_ORDER = FIX["sensitivity_variants_pinned_order"]
gate(VARIANT_ORDER == ["t_hull_proportional", "support_7pt", "m_4",
                       "theta_30", "theta_70", "restart_T_dock"],
     "sensitivity variant pinned order matches fixtures")
VARIANT_POLICIES = {v: (POLICIES_M4 if v == "m_4" else POLICIES)
                    for v in ["base"] + VARIANT_ORDER}


def decision_numbers(table, policies):
    """Per-cell G*(all), G*(<=1), G*(b0), NEC, NEC0, argmax, T180."""
    out = {}
    for d0, td in CELLS:
        cid = cell_id(d0, td)
        row = table[cid]
        best_all, best_all_p = None, None
        best_le1, best_b0 = None, None
        for p in policies:  # pinned order; strict > keeps the first on ties
            gv = row[pol_name(p)]["G"]
            if best_all is None or gv > best_all:
                best_all, best_all_p = gv, p
            if p[1] <= 1 and (best_le1 is None or gv > best_le1):
                best_le1 = gv
            if p[1] == 0 and (best_b0 is None or gv > best_b0):
                best_b0 = gv
        gate(best_all > 0 and best_le1 > 0 and best_b0 > 0,
             "positive decision rates in %s" % cid)
        out[cid] = {"G_all": best_all, "G_le1": best_le1, "G_b0": best_b0,
                    "NEC": best_all / best_le1, "NEC0": best_all / best_b0,
                    "argmax": pol_name(best_all_p), "argmax_pol": best_all_p,
                    "T180": F(LADDER) / best_all}
    return out


# ---------------------------------------------------------------- hand fixture
# F2 + F3 — the zero-damage fixture cell (D0 = 0, T_dock = 1, NOT in the grid)
F3 = Cfg(DTAB[0] if 0 in DTAB else [0, 0, 0], F(1))
_desc0 = descent_enum(F3, 2, False)
gate(len(_desc0) == 25 and all(hg == FIX["hand_fixture"]
     ["F2_descent_bank_gold_b2"] for p, g, t, w, x, s, hg in _desc0),
     "F2 descent hold 51g (3*5 + 3*12), every zero-damage path")
_l21 = loop_seg_enum(F3, 2, 1, False)
gate(all(hg == FIX["hand_fixture"]["F2_band2_m1_loop_hold_gold"]
         for p, g, t, w, x, s, hg in _l21),
     "F2 band-2 m=1 loop hold 75g")
_l23 = loop_seg_enum(F3, 2, 3, False)
gate(all(hg == FIX["hand_fixture"]["F2_band2_m3_loop_hold_gold"]
         and x == FIX["hand_fixture"]["F2_band2_m3_wasted_crates"]
         for p, g, t, w, x, s, hg in _l23),
     "F2 band-2 m=3 loop hold 200g + one 25g crate wasted (cap 8)")
_f3_tab = {cell_id(0, F(1)): {pol_name(p): policy_stats(F3, p)
                              for p in POLICIES}}
_f3_row = _f3_tab[cell_id(0, F(1))]
gate(_f3_row["GRIND(2,2)"]["G"] == F(FIX["hand_fixture"]["F3_G_GRIND_2_2"]),
     "F3 G(GRIND(2,2)) = 75/2 at the zero-damage fixture cell")
gate(_f3_row["GRIND(1,2)"]["G"] == F(FIX["hand_fixture"]["F3_G_GRIND_1_2"]),
     "F3 G(GRIND(1,2)) = 18 at the zero-damage fixture cell")
_f3_all = max(_f3_row[pol_name(p)]["G"] for p in POLICIES)
_f3_le1 = max(_f3_row[pol_name(p)]["G"] for p in POLICIES if p[1] <= 1)
gate(_f3_all / _f3_le1 == F(FIX["hand_fixture"]["F3_NEC"]),
     "F3 NEC = 25/12 at the zero-damage fixture cell")
gate(all(g == hg for p, g, t, w, x, s, hg in _l21),
     "F6 zero-damage segment pays 0 repair (banked == hold)")

# ---------------------------------------------------------------- Arm A runs
DTAB[0] = [0, 0, 0]
ARM_A = {}
ARM_A["base"] = arm_a_tables(VARIANT_CFGS["base"], POLICIES)
for v in VARIANT_ORDER:
    ARM_A[v] = arm_a_tables(VARIANT_CFGS[v], VARIANT_POLICIES[v])

DEC = {v: decision_numbers(ARM_A[v], VARIANT_POLICIES[v])
       for v in ["base"] + VARIANT_ORDER}

# zero-sink branch reachability, asserted (proposal: 'reachable by
# construction at D0=20, band 2, m=1, max cumulative damage 90 < 100')
gate(policy_stats(cfg_base(20, F(1)), ("GRIND", 2, 1))["q_loop"] == 0,
     "zero-sink branch reachable: D0=20 band 2 m=1 loop q = 0 (2*45 = 90 < 100)")

# F5 — exact monotonicity theorems (base variant, Arm A exact).
for td in TDOCK_AXIS:
    for p in POLICIES:
        g20 = ARM_A["base"][cell_id(20, td)][pol_name(p)]["G"]
        g35 = ARM_A["base"][cell_id(35, td)][pol_name(p)]["G"]
        g50 = ARM_A["base"][cell_id(50, td)][pol_name(p)]["G"]
        gate(g20 >= g35 >= g50,
             "F5 G non-increasing in D0 (%s, Td=%s)" % (pol_name(p), td))
for d0, td in CELLS:
    cid = cell_id(d0, td)
    gate(DEC["base"][cid]["NEC"] >= 1, "F5 NEC >= 1 (class nesting) %s" % cid)
for d0, td in CELLS:
    cid = cell_id(d0, td)
    for kind in ("GRIND", "GRIND-H"):
        for b in range(3):
            q1 = ARM_A["base"][cid]["%s(%d,1)" % (kind, b)]["q_loop"]
            q2 = ARM_A["base"][cid]["%s(%d,2)" % (kind, b)]["q_loop"]
            q3 = ARM_A["base"][cid]["%s(%d,3)" % (kind, b)]["q_loop"]
            gate(q1 <= q2 <= q3,
                 "F5 sink prob non-decreasing in m (%s b=%d %s)"
                 % (kind, b, cid))
        for m in (1, 2, 3):
            q0 = ARM_A["base"][cid]["%s(0,%d)" % (kind, m)]["q_loop"]
            q1b = ARM_A["base"][cid]["%s(1,%d)" % (kind, m)]["q_loop"]
            q2b = ARM_A["base"][cid]["%s(2,%d)" % (kind, m)]["q_loop"]
            gate(q0 <= q1b <= q2b,
                 "F5 sink prob non-decreasing in band (%s m=%d %s)"
                 % (kind, m, cid))


# ---------------------------------------------------------------- evaluators
def eval_A(dec):
    """Twin evaluator A — Fraction comparisons, comprehension-style.
    Cells-level ruling: REJECT-CELLS if NEC < 5/4 in >= 5 of 9 (checked
    FIRST); APPROVE-CELLS if NEC >= 3/2 in >= 7 of 9 AND the central cell's
    argmax is neither GRIND(b*,1) nor GRIND(b*,3); NULL-CELLS otherwise."""
    low = sum(1 for cid in dec if dec[cid]["NEC"] < REJECT_BAND)
    high = sum(1 for cid in dec if dec[cid]["NEC"] >= APPROVE_BAND)
    kind, b, m = dec[CENTRAL_ID]["argmax_pol"]
    interior = kind == "GRIND-H" or (kind == "GRIND" and m not in (1, 3))
    if low >= REJECT_CELLS:
        return "REJECT-CELLS"
    if high >= APPROVE_CELLS and interior:
        return "APPROVE-CELLS"
    return "NULL-CELLS"


def eval_B(g_rows, policies):
    """Twin evaluator B — independently written: pure-integer
    cross-multiplication on Fraction numerators/denominators, explicit
    loops; re-derives per-cell maxima and the central argmax itself.
    g_rows: {cell_id: {pol_name: G Fraction}}."""
    n_low = 0
    n_high = 0
    central_arg = None
    for cid in [cell_id(d0, td) for d0, td in CELLS]:  # pinned cell order
        best_num, best_den = None, None
        le1_num, le1_den = None, None
        arg = None
        for p in policies:
            gv = g_rows[cid][pol_name(p)]
            a, bden = gv.numerator, gv.denominator  # den > 0 normalized
            if best_num is None or a * best_den > best_num * bden:
                best_num, best_den, arg = a, bden, p
            if p[1] <= 1:
                if le1_num is None or a * le1_den > le1_num * bden:
                    le1_num, le1_den = a, bden
        if cid == CENTRAL_ID:
            central_arg = arg
        # NEC = (best_num/best_den) / (le1_num/le1_den)
        #     = (best_num * le1_den) / (best_den * le1_num); le1 > 0 gated
        nec_n = best_num * le1_den
        nec_d = best_den * le1_num
        # NEC < 5/4  <=>  4 * nec_n < 5 * nec_d   (nec_d > 0)
        if 4 * nec_n < 5 * nec_d:
            n_low += 1
        # NEC >= 3/2  <=>  2 * nec_n >= 3 * nec_d
        if 2 * nec_n >= 3 * nec_d:
            n_high += 1
    k, bb, mm = central_arg
    interior = 1 if (k == "GRIND-H" or mm == 2 or mm == 4) else 0
    if n_low >= 5:
        return "REJECT-CELLS"
    if n_high >= 7 and interior:
        return "APPROVE-CELLS"
    return "NULL-CELLS"


def g_only(table, policies):
    return {cid: {pol_name(p): table[cid][pol_name(p)]["G"]
                  for p in policies}
            for cid in table}


# ---------------------------------------------------------------- Arm S
MAP5 = (0, 1, 1, 2, 2, 3, 3, 4)          # eighths {1,2,2,2,1}
MAP7 = (0, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5, 6)  # sixteenths


def mc_leg(rng, cfg, pol, w_leg):
    """One MC leg: simulate the policy from respawn for exactly w_leg waters
    ('one damage draw per water in pinned order'); G_S = total banked / total
    time, exact (integer gold / integer twentieths). Returns (G_S, draws)."""
    kind, b, m = pol
    hbank = kind == "GRIND-H"
    if cfg.sup == "5":
        bits, dmap = 3, MAP5
    else:
        bits, dmap = 4, MAP7
    sup = [[v for v, w in cfg.draws(k)] for k in range(3)]
    t20 = [int(t * 20) for t in cfg.t]
    ts20 = [x // 2 for x in t20]
    dock20 = int(cfg.tdock * 20)
    rho20 = int(cfg.rho * 20)
    theta = cfg.theta
    getbits = rng.getrandbits
    banked = 0
    time20 = 0
    waters = 0
    descending = b > 0
    stage = 0
    cum = 0
    crates = 0
    gold = 0
    segw = 0
    while waters < w_leg:
        band = stage if descending else b
        d = sup[band][dmap[getbits(bits)]]
        waters += 1
        cum += d
        if cum >= SINK_AT:
            # sink: t_b/2, forfeit hold, restart descent (+ rho overhead)
            time20 += ts20[band] + rho20
            cum = crates = gold = segw = 0
            descending = b > 0
            stage = 0
            continue
        time20 += t20[band]
        take = DROPS if crates + DROPS <= HOLD_CAP else HOLD_CAP - crates
        crates += take
        gold += take * LOOT[band]
        if descending:
            if stage == b - 1:
                time20 += dock20
                banked += gold - (cum + 3) // 4
                cum = crates = gold = 0
                descending = False
                segw = 0
            elif hbank and HULL_MAX - cum <= theta:
                time20 += dock20
                banked += gold - (cum + 3) // 4
                cum = crates = gold = 0
                stage += 1
            else:
                stage += 1
        else:
            segw += 1
            if segw == m or (hbank and HULL_MAX - cum <= theta):
                time20 += dock20
                banked += gold - (cum + 3) // 4
                cum = crates = gold = 0
                segw = 0
    return F(banked * 20, time20), waters


def mc_sweep(seed, w_leg, variants):
    """One seeded sweep: a single random.Random(seed) stream, variants ->
    cells -> policies in pinned order. Returns per-variant G_S tables and
    the total draw count."""
    rng = random.Random(seed)
    draws = 0
    out = {}
    for vname, pols in variants:
        mk = VARIANT_CFGS[vname]
        vt = {}
        for d0, td in CELLS:
            cfg = mk(d0, td)
            row = {}
            for p in pols:
                gs, dr = mc_leg(rng, cfg, p, w_leg)
                draws += dr
                row[pol_name(p)] = gs
            vt[cell_id(d0, td)] = row
        out[vname] = vt
    return out, draws


def agree_gate(mc_tab, a_tab, pols, bound, label, w_leg):
    """Arm agreement check + the registered SE-headroom pre-check, both in
    exact rationals. Breaches are recorded findings (never silent): the
    registration text says 'any breach invalidating the run' AND registers
    'arm disagreement' as NULL axis (vi) — resolved (frozen BEFORE any
    decision number was read, disclosed in fixtures.json): a main-leg breach
    lands the verdict as NULL(arm-disagreement), a citable finding per the
    honest-null-explicit clause, never a silent invalid. The headroom claim
    ('pre-checked >= 4 SE headroom at the pinned leg length') is COMPUTED and
    reported — where it fails, that is a registration defect disclosed as a
    first-class anomaly (direction: a shortfall risks a FALSE breach of the
    confirmation gate, never a wrong decision number — Arm A alone decides).
    Returns (worst_rel, breaches, headroom_fail_count, worst_headroom_sq)."""
    worst = F(0)
    breaches = []
    hr_fail = 0
    worst_hr_sq = None  # (headroom_ratio^2 as Fraction, leg label)
    for d0, td in CELLS:
        cid = cell_id(d0, td)
        for p in pols:
            pn = pol_name(p)
            ga = a_tab[cid][pn]["G"]
            rel = abs(mc_tab[cid][pn] - ga) / ga
            if rel > worst:
                worst = rel
            if rel <= bound:
                _PASS[0] += 1
            else:
                breaches.append("%s %s %s rel=%s" % (label, cid, pn,
                                                     float(rel)))
                anomaly("AGREEMENT BREACH %s %s %s rel=%s > %s"
                        % (label, cid, pn, float(rel), bound))
            # SE headroom pre-check (exact rationals, squared comparison)
            se2 = a_tab[cid][pn]["se2w"] / w_leg
            if se2 == 0:
                continue
            hr_sq = (bound * ga) ** 2 / se2
            if worst_hr_sq is None or hr_sq < worst_hr_sq[0]:
                worst_hr_sq = (hr_sq, "%s %s" % (cid, pn))
            if hr_sq < SE_HEADROOM ** 2:
                hr_fail += 1
    if hr_fail:
        anomaly("%s: SE headroom < %d SE on %d legs (worst %s at %s) — the "
                "registration's 'pre-checked >= 4 SE headroom' claim fails "
                "at the pinned leg length; disclosed, reporting-only"
                % (label, SE_HEADROOM, hr_fail,
                   "%.3f" % (float(worst_hr_sq[0]) ** 0.5), worst_hr_sq[1]))
    return worst, breaches, hr_fail, worst_hr_sq


# main leg — seed 20261309, 100k waters per (cell, policy), base variant
S_MAIN, draws_main = mc_sweep(SEEDS["main"], W_MAIN, [("base", POLICIES)])
gate(draws_main == W_MAIN * len(CELLS) * len(POLICIES),
     "draw-count sentinel main leg (%d)" % draws_main)
worst_main, breach_main, hrfail_main, hrworst_main = agree_gate(
    S_MAIN["base"], ARM_A["base"], POLICIES, GATE_MAIN, "main(1/50)", W_MAIN)

# stability leg — seed 20261310, 20k waters, widened gate 1/20
S_STAB, draws_stab = mc_sweep(SEEDS["stability"], W_STAB,
                              [("base", POLICIES)])
gate(draws_stab == W_STAB * len(CELLS) * len(POLICIES),
     "draw-count sentinel stability leg (%d)" % draws_stab)
worst_stab, breach_stab, hrfail_stab, hrworst_stab = agree_gate(
    S_STAB["base"], ARM_A["base"], POLICIES, GATE_WIDE, "stability(1/20)",
    W_STAB)

# sensitivity confirmations — seed 20261311, 20k waters, gate 1/20;
# m_4 confirms the six NEW (b, 4) policies (the 18 base legs already
# confirmed by the main leg), other variants confirm all 18.
SENS_PLAN = [(v, (M4_NEW if v == "m_4" else POLICIES)) for v in VARIANT_ORDER]
S_SENS, draws_sens = mc_sweep(SEEDS["sensitivity"], W_SENS, SENS_PLAN)
_exp = sum(W_SENS * len(CELLS) * len(pols) for v, pols in SENS_PLAN)
gate(draws_sens == _exp, "draw-count sentinel sensitivity legs (%d)"
     % draws_sens)
worst_sens = F(0)
breach_sens = []
for v, pols in SENS_PLAN:
    w, br, hf, hw = agree_gate(S_SENS[v], ARM_A[v], pols, GATE_WIDE,
                               "sens-%s(1/20)" % v, W_SENS)
    breach_sens += br
    if w > worst_sens:
        worst_sens = w

# aux seed 20261312 — registered, NEVER read by any decision number
AUX_DRAWS = 0
gate(AUX_DRAWS == 0, "aux seed 20261312 never read (0 draws)")

# ---------------------------------------------------------------- decision
# stability-leg decision numbers (from MC G_S values, exact Fractions)
def mc_decision_numbers(mc_tab, policies):
    out = {}
    for d0, td in CELLS:
        cid = cell_id(d0, td)
        row = mc_tab[cid]
        best_all, best_p = None, None
        best_le1, best_b0 = None, None
        for p in policies:
            gv = row[pol_name(p)]
            if best_all is None or gv > best_all:
                best_all, best_p = gv, p
            if p[1] <= 1 and (best_le1 is None or gv > best_le1):
                best_le1 = gv
            if p[1] == 0 and (best_b0 is None or gv > best_b0):
                best_b0 = gv
        gate(best_all > 0 and best_le1 > 0, "positive MC rates %s" % cid)
        out[cid] = {"NEC": best_all / best_le1,
                    "NEC0": best_all / best_b0,
                    "argmax": pol_name(best_p), "argmax_pol": best_p}
    return out


DEC_STAB = mc_decision_numbers(S_STAB["base"], POLICIES)

ruling_A_1 = eval_A(DEC["base"])
ruling_A_2 = eval_B(g_only(ARM_A["base"], POLICIES), POLICIES)
gate(ruling_A_1 == ruling_A_2, "twin evaluators agree on Arm A (%s)"
     % ruling_A_1)
ruling_S_1 = eval_A(DEC_STAB)
ruling_S_2 = eval_B({cid: dict(S_STAB["base"][cid]) for cid in
                     S_STAB["base"]}, POLICIES)
gate(ruling_S_1 == ruling_S_2, "twin evaluators agree on stability leg (%s)"
     % ruling_S_1)

# sensitivity rulings (reporting-only — CANNOT flip the decision)
SENS_RULINGS = {v: eval_A(DEC[v]) for v in VARIANT_ORDER}
sens_straddle = [v for v in VARIANT_ORDER if SENS_RULINGS[v] != ruling_A_1]


def null_axis(dec, dec_stab, ruling_a, ruling_s):
    """Named NULL axis, pre-registered candidates, registration order
    (operationalizations disclosed in fixtures.json)."""
    cids = [cell_id(d0, td) for d0, td in CELLS]
    # (i) band-1-carries
    n_b1 = sum(1 for cid in cids
               if dec[cid]["argmax_pol"][1] == 1
               and dec[cid]["NEC0"] >= APPROVE_BAND)
    if n_b1 >= 5:
        return "band-1-carries (argmax band 1 with NEC0 >= 3/2 in %d of 9)" \
            % n_b1
    # (ii) hold-cap bind — the wasted-crate column at the argmax
    n_waste = sum(1 for cid in cids
                  if ARM_A["base"][cid][dec[cid]["argmax"]]["waste_seg"] > 0)
    if n_waste >= 5:
        return "hold-cap-bind (argmax wastes crates in %d of 9 cells)" \
            % n_waste
    lean = {}
    for cid in cids:
        nec = dec[cid]["NEC"]
        lean[cid] = "R" if nec < REJECT_BAND else (
            "A" if nec >= APPROVE_BAND else "M")
    # (iii) risk-straddle — flips across D0 at fixed T_dock (boundary D0+)
    for td in TDOCK_AXIS:
        col = [lean[cell_id(d0, td)] for d0 in D0_AXIS]
        if "R" in col and "A" in col:
            return "risk-straddle (Td=%s column %s; D0-dagger between the " \
                "adjacent flipped cells)" % (td, "".join(col))
    # (iv) dock-straddle — flips across T_dock at fixed D0
    for d0 in D0_AXIS:
        row = [lean[cell_id(d0, td)] for td in TDOCK_AXIS]
        if "R" in row and "A" in row:
            return "dock-straddle (D0=%d row %s)" % (d0, "".join(row))
    # (v) margin-thin — deciding cells live between 5/4 and 3/2
    n_mid = sum(1 for cid in cids if lean[cid] == "M")
    if n_mid >= 1:
        return "margin-thin (%d of 9 cells between 5/4 and 3/2)" % n_mid
    # (vi) arm disagreement — stability class differs from Arm A class
    if ruling_s != ruling_a:
        return "arm-disagreement (stability %s vs Arm A %s)" \
            % (ruling_s, ruling_a)
    # (vii) sensitivity straddle
    if sens_straddle:
        return "sensitivity-straddle (%s)" % ", ".join(sens_straddle)
    return "margin-thin (fallback: no registered axis fired)"


# THE RULING — pre-registered order, REJECT FIRST (proposal, verbatim:
# 'does the result land REJECT (... checked FIRST ...), APPROVE (...), or
# NULL (anything else ...)')
verdict = None
verdict_axis = ""
if breach_main:
    verdict = "null"
    verdict_axis = ("arm-disagreement (main-leg agreement breach: %s; the "
                    "registered NULL axis (vi) — resolution frozen before "
                    "any decision number was read)" % "; ".join(breach_main))
elif ruling_A_1 == "REJECT-CELLS":
    verdict = "reject"
elif ruling_A_1 == "APPROVE-CELLS":
    # Proposal, verbatim: 'AND the seed-20261310 stability leg reproduces
    # the ruling'; done-when: 'reproduces the ruling class through both twin
    # evaluators'. The registered conjunct is CLASS REPRODUCTION — a widened
    # -gate breach on a stability leg is a first-class anomaly (recorded
    # above) but not a registered APPROVE conjunct; the stricter
    # breach-denies reading is also computed and recorded in results.json
    # (dual-reading disclosure, fixtures.json implementation pins).
    if ruling_S_1 == "APPROVE-CELLS":
        verdict = "approve"
    else:
        verdict = "null"
        verdict_axis = ("margin-thin (stability leg class %s failed to "
                        "reproduce APPROVE through the twin evaluators)"
                        % ruling_S_1)
else:
    verdict = "null"
    verdict_axis = null_axis(DEC["base"], DEC_STAB, ruling_A_1, ruling_S_1)

# dual-reading disclosure: what the stricter (breach-denies) reading lands
strict_verdict = verdict
if (not breach_main) and ruling_A_1 == "APPROVE-CELLS" and (
        ruling_S_1 != "APPROVE-CELLS" or breach_stab):
    strict_verdict = "null"

# ---------------------------------------------------------------- output


def s(x):
    return str(x)


def fapprox(x):
    return "%.6f" % float(x)


def serialize_dec(dec):
    out = {}
    for cid, d in dec.items():
        out[cid] = {"NEC": s(d["NEC"]), "NEC_approx": fapprox(d["NEC"]),
                    "NEC0": s(d["NEC0"]), "NEC0_approx": fapprox(d["NEC0"]),
                    "argmax": d["argmax"]}
        if "G_all" in d:
            out[cid].update({
                "G_all": s(d["G_all"]), "G_all_approx": fapprox(d["G_all"]),
                "G_le1": s(d["G_le1"]), "G_le1_approx": fapprox(d["G_le1"]),
                "G_b0": s(d["G_b0"]),
                "T180": s(d["T180"]), "T180_approx": fapprox(d["T180"])})
    return out


def serialize_arm_a(table, policies):
    out = {}
    for cid, row in table.items():
        out[cid] = {}
        for p in policies:
            e = row[pol_name(p)]
            out[cid][pol_name(p)] = {
                "G": s(e["G"]), "G_approx": fapprox(e["G"]),
                "q_loop": s(e["q_loop"]),
                "p_sink_descent": s(e["p_sink_descent"]),
                "wasted_crates_loop_seg": s(e["waste_seg"]),
                "wasted_crates_descent": s(e["waste_desc"])}
    return out


def serialize_mc(mc_tab):
    return {cid: {pn: s(gv) for pn, gv in row.items()}
            for cid, row in mc_tab.items()}


results = {
    "verdict_054": {
        "class": verdict,
        "null_axis": verdict_axis,
        "rule_trace": {
            "REJECT_checked_first": True,
            "arm_a_cells_ruling": ruling_A_1,
            "stability_cells_ruling": ruling_S_1,
            "twin_evaluators": ("agree (A: Fraction comprehension, "
                                "B: integer cross-multiplication with "
                                "independent argmax)"),
            "central_cell": CENTRAL_ID,
            "central_argmax": DEC["base"][CENTRAL_ID]["argmax"],
        },
        "cells": serialize_dec(DEC["base"]),
        "cells_low_of_9": sum(1 for cid in DEC["base"]
                              if DEC["base"][cid]["NEC"] < REJECT_BAND),
        "cells_high_of_9": sum(1 for cid in DEC["base"]
                               if DEC["base"][cid]["NEC"] >= APPROVE_BAND),
        "sensitivity_rulings_reporting_only": SENS_RULINGS,
        "sensitivity_straddle": sens_straddle,
        "stability_cells": serialize_dec(DEC_STAB),
        "stability_gate_breaches": breach_stab,
        "dual_reading_disclosure": {
            "registered_reading": ("APPROVE conjunct = stability leg "
                                   "reproduces the ruling CLASS through both "
                                   "twin evaluators (proposal text verbatim)"),
            "registered_reading_class": verdict,
            "stricter_breach_denies_reading_class": strict_verdict,
        },
    },
    "arm_a": {v: serialize_arm_a(ARM_A[v], VARIANT_POLICIES[v])
              for v in ["base"] + VARIANT_ORDER},
    "arm_a_decision_numbers": {v: serialize_dec(DEC[v])
                               for v in ["base"] + VARIANT_ORDER},
    "arm_s": {
        "main_seed_20261309": serialize_mc(S_MAIN["base"]),
        "stability_seed_20261310": serialize_mc(S_STAB["base"]),
        "sensitivity_seed_20261311": {v: serialize_mc(S_SENS[v])
                                      for v in VARIANT_ORDER},
        "draw_counts": {"main": draws_main, "stability": draws_stab,
                        "sensitivity": draws_sens,
                        "aux_20261312": AUX_DRAWS},
        "worst_rel_dev": {"main": s(worst_main) + " (~%s)" % fapprox(worst_main),
                          "stability": s(worst_stab) + " (~%s)" % fapprox(worst_stab),
                          "sensitivity": s(worst_sens) + " (~%s)" % fapprox(worst_sens)},
        "agreement_breaches": {"main": breach_main, "stability": breach_stab,
                               "sensitivity": breach_sens},
        "se_headroom_precheck": {
            "claimed": ">= 4 SE at the pinned leg length (registration)",
            "main_legs_below_4se": hrfail_main,
            "main_worst_headroom_se": "%.4f" % (float(hrworst_main[0]) ** 0.5),
            "main_worst_leg": hrworst_main[1],
            "stability_legs_below_4se": hrfail_stab,
            "note": ("headroom shortfall risks a false confirmation-gate "
                     "breach only; Arm A exact rationals alone are "
                     "decision-bearing")},
    },
    "anomalies": ANOMALIES,
    "self_checks_passed": None,
}

print("=" * 72)
print("VERDICT 054 — Brineward band-2 necessity (PROPOSAL 043)")
print("=" * 72)
print("Committed tables @ %s" % FIX["source_pin"])
print("Arm A decision table (exact; NEC = G*(all 18) / G*(b <= 1)):")
for d0, td in CELLS:
    cid = cell_id(d0, td)
    d = DEC["base"][cid]
    band = ("<5/4" if d["NEC"] < REJECT_BAND else
            (">=3/2" if d["NEC"] >= APPROVE_BAND else "mid"))
    print("  %-12s NEC=%s (%s) NEC0=%s argmax=%-13s G*=%s T180=%s %s"
          % (cid, fapprox(d["NEC"]), s(d["NEC"]), fapprox(d["NEC0"]),
             d["argmax"], fapprox(d["G_all"]), fapprox(d["T180"]), band))
print("Per-band m-curve at the central cell %s (G approx, m=1/2/3):"
      % CENTRAL_ID)
for kind in ("GRIND", "GRIND-H"):
    for b in range(3):
        gs = [fapprox(ARM_A["base"][CENTRAL_ID]["%s(%d,%d)" % (kind, b, m)]
                      ["G"]) for m in (1, 2, 3)]
        print("  %-8s b=%d: %s" % (kind, b, " / ".join(gs)))
print("Wasted-crate column (argmax policy, expected per loop segment):")
for d0, td in CELLS:
    cid = cell_id(d0, td)
    d = DEC["base"][cid]
    e = ARM_A["base"][cid][d["argmax"]]
    print("  %-12s %-13s waste=%s sink(q)=%s desc-sink=%s"
          % (cid, d["argmax"], fapprox(e["waste_seg"]),
             fapprox(e["q_loop"]), fapprox(e["p_sink_descent"])))
print("Arm S worst |G_S - G_A|/G_A: main=%s stability=%s sensitivity=%s"
      % (fapprox(worst_main), fapprox(worst_stab), fapprox(worst_sens)))
print("Sensitivity rulings (reporting-only, cannot flip): %s"
      % SENS_RULINGS)
if sens_straddle:
    print("Sensitivity straddle (named, reporting-only): %s" % sens_straddle)
print("Stability leg (seed 20261310) cells ruling: %s" % ruling_S_1)
print("Dual-reading disclosure: registered class=%s | stricter "
      "breach-denies class=%s" % (verdict, strict_verdict))
print("Anomalies: %s" % (ANOMALIES if ANOMALIES else "none"))
print("RULING (pre-registered order, REJECT first): %s%s"
      % (verdict.upper(), (" — axis: " + verdict_axis) if verdict_axis
         else ""))
results["self_checks_passed"] = _PASS[0]
print("SELF-CHECKS: %d passed, 0 failed" % _PASS[0])

with open(os.path.join(HERE, "results.json"), "w") as f:
    json.dump(results, f, indent=1, sort_keys=False)
    f.write("\n")
