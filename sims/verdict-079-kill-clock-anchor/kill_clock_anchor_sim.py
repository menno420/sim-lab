#!/usr/bin/env python3
"""VERDICT 079 — kill-clock anchor vs owner-gated funnel onset (idea-engine PROPOSAL 066).

Three-arm, fully deterministic decision core, stdlib-only, hermetic (reads
ONLY its sibling fixtures.json):

  Arm A — DECISION arm, seedless: exact-Fraction schedule-sum arithmetic over
          the full grid (3 shapes x 3 anchors x 6 tau x 3 q + degeneracies).
  Arm B — twin, seedless, INDEPENDENTLY-WRITTEN: a literal calendar day-walk
          simulator (deposits each day's visits, tests window membership per
          anchor as a date comparison, accumulates N and pre-/post-window
          mass, computes FK by literal repeated multiplication). Must
          reproduce every Arm-A number EXACTLY; powers the second decision
          evaluator.
  Arm R — seeded, REPORTING-ONLY: the literal Bernoulli visit process at the
          decision cell; NO statistical gate rides it.

Decision rule pre-registered in PROPOSAL 066, applied in the registered
order REJECT -> INVALID -> APPROVE -> NULL (INVALID short-circuits on any
gate failure, convention C7). Every decision number is a seedless exact
rational. Determinism: stdout + results.json byte-identical across two full
process runs (verified externally by diff + sha256; no timestamps emitted).
"""

import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# self-check infrastructure
# ---------------------------------------------------------------------------

CHECKS = []


def check(name, cond):
    ok = bool(cond)
    CHECKS.append((name, ok))
    print(("PASS  " if ok else "FAIL  ") + name)
    return ok


# ---------------------------------------------------------------------------
# seed constructor registry (convention C8)
# ---------------------------------------------------------------------------

SEED_REGISTRY = []


def make_rng(seed):
    SEED_REGISTRY.append(seed)
    return random.Random(seed)


# ---------------------------------------------------------------------------
# exact-rational rendering helpers (convention C5 / C9)
# ---------------------------------------------------------------------------

def fr_str(fr):
    fr = Fraction(fr)
    return "%d/%d" % (fr.numerator, fr.denominator)


def fr_round_str(fr, places):
    """Round-half-up an exact nonnegative Fraction to `places` decimals,
    rendered as a plain decimal string (no float pathway)."""
    fr = Fraction(fr)
    scale = 10 ** places
    scaled = (fr.numerator * scale * 2 + fr.denominator) // (2 * fr.denominator)
    s = str(scaled).rjust(places + 1, "0")
    return s[:-places] + "." + s[-places:]


def fk_render(fr):
    return {"exact": fr_str(fr), "float": repr(float(fr)), "round6": fr_round_str(fr, 6)}


# ---------------------------------------------------------------------------
# fixtures (the ONLY input; hermetic)
# ---------------------------------------------------------------------------

with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

WORLD = FX["world"]
T_WINDOW = WORLD["window_T"]          # 14
CAP = WORLD["cap"]                    # 30
TAU_GRID = WORLD["tau_grid"]          # [0, 3, 7, 10, 13, 20]
Q_GRID = [Fraction(s) for s in WORLD["q_grid"]]
Q_DECISION = Fraction(WORLD["decision_q"])
Q_DEGEN = [Fraction(s) for s in WORLD["q_degeneracies"]]
SHAPE_NAMES = ["SPIKE", "BURN", "DRIP"]
ANCHOR_NAMES = ["A-LIST", "A-FUNNEL", "A-CAP30"]

# pinned schedules, funnel-relative (v[d] for funnel-day d >= 1)
def build_schedules():
    spike = {1: 200}
    burn = {d: 60 // d for d in range(1, 61)}
    drip = {d: 2 for d in range(1, 366)}
    return {"SPIKE": spike, "BURN": burn, "DRIP": drip}


SCHEDULES = build_schedules()

check("fixtures: SPIKE total mass matches pin (200)",
      sum(SCHEDULES["SPIKE"].values()) == WORLD["shapes"]["SPIKE"]["total_mass"])
check("fixtures: BURN total mass matches pin (261)",
      sum(SCHEDULES["BURN"].values()) == WORLD["shapes"]["BURN"]["total_mass"])
check("fixtures: BURN first-14 mass matches pin (192)",
      sum(v for d, v in SCHEDULES["BURN"].items() if d <= 14) == WORLD["shapes"]["BURN"]["first_14_mass"])
check("fixtures: DRIP total mass matches pin (730)",
      sum(SCHEDULES["DRIP"].values()) == WORLD["shapes"]["DRIP"]["total_mass"])

check("runtime: CPython minor pinned 3.11", sys.version_info[:2] == (3, 11))

# ---------------------------------------------------------------------------
# Arm A — exact schedule-sum arithmetic (funnel-day predicates)
# ---------------------------------------------------------------------------

def arm_a_N(schedule, anchor, tau, t_window=T_WINDOW, cap=CAP):
    """Evidence mass: sum scheduled visits whose funnel-day d satisfies the
    anchor's registered predicate."""
    total = 0
    for d, v in schedule.items():
        if anchor == "A-LIST":
            inside = (tau + d) <= t_window
        elif anchor == "A-FUNNEL":
            inside = d <= t_window
        elif anchor == "A-CAP30":
            inside = (d <= t_window) and ((tau + d) <= cap)
        else:
            raise ValueError(anchor)
        if inside:
            total += v
    return total


def arm_a_FK(q, n):
    return (Fraction(1) - Fraction(q)) ** n


def occupancy(anchor, tau, t_window=T_WINDOW, cap=CAP):
    if anchor == "A-LIST":
        return t_window
    if anchor == "A-FUNNEL":
        return tau + t_window
    if anchor == "A-CAP30":
        return min(tau + t_window, cap)
    raise ValueError(anchor)


# ---------------------------------------------------------------------------
# Arm B — literal calendar day-walk (INDEPENDENTLY WRITTEN twin)
# ---------------------------------------------------------------------------

def day_walk(schedule, anchor, tau, q, t_window=T_WINDOW, cap=CAP):
    """Walk calendar days 1..(tau + last scheduled funnel day), depositing
    each day's visits and classifying them against the anchor's calendar
    window by date comparison (convention C3: horizon extended past the
    registered 60 so the twin also verifies conservation of DRIP's full
    mass). Returns (N, pre, post, FK) with FK by repeated multiplication."""
    if anchor == "A-LIST":
        win_start, win_end = 1, t_window
    elif anchor == "A-FUNNEL":
        win_start, win_end = tau + 1, tau + t_window
    elif anchor == "A-CAP30":
        win_start, win_end = tau + 1, min(tau + t_window, cap)
    else:
        raise ValueError(anchor)

    last_funnel_day = max(schedule) if schedule else 0
    n_in = n_pre = n_post = 0
    for cal_day in range(1, tau + last_funnel_day + 1):
        funnel_day = cal_day - tau
        visits_today = schedule.get(funnel_day, 0) if funnel_day >= 1 else 0
        if visits_today == 0:
            continue
        if cal_day < win_start:
            n_pre += visits_today
        elif cal_day <= win_end:
            n_in += visits_today
        else:
            n_post += visits_today

    keep = Fraction(1) - Fraction(q)
    fk = Fraction(1)
    for _ in range(n_in):
        fk = fk * keep
    return n_in, n_pre, n_post, fk


# ---------------------------------------------------------------------------
# full-grid tables, both arms
# ---------------------------------------------------------------------------

ALL_Q = Q_GRID + Q_DEGEN  # [1/30, 1/100, 1/300, 0, 1]

N_A = {}    # (shape, anchor, tau) -> int
N_B = {}
PRE_B = {}
POST_B = {}
FK_A = {}   # (shape, anchor, tau, q) -> Fraction
FK_B = {}

for shape in SHAPE_NAMES:
    sched = SCHEDULES[shape]
    for anchor in ANCHOR_NAMES:
        for tau in TAU_GRID:
            na = arm_a_N(sched, anchor, tau)
            N_A[(shape, anchor, tau)] = na
            for q in ALL_Q:
                FK_A[(shape, anchor, tau, q)] = arm_a_FK(q, na)
            for q in ALL_Q:
                nb, pre, post, fkb = day_walk(sched, anchor, tau, q)
                FK_B[(shape, anchor, tau, q)] = fkb
                N_B[(shape, anchor, tau)] = nb
                PRE_B[(shape, anchor, tau)] = pre
                POST_B[(shape, anchor, tau)] = post

# ---------------------------------------------------------------------------
# F1 — model identities
# ---------------------------------------------------------------------------

check("F1: N recomputed identically by both arms (all 54 cells)",
      all(N_A[k] == N_B[k] for k in N_A))

check("F1: FK = (1-q)^N with N recomputed by both arms (all cells, all q)",
      all(FK_B[(s, a, t, q)] == arm_a_FK(q, N_B[(s, a, t)])
          for s in SHAPE_NAMES for a in ANCHOR_NAMES for t in TAU_GRID for q in ALL_Q))

check("F1: conservation in + pre + post = shape total mass (every cell, literal walk)",
      all(N_B[(s, a, t)] + PRE_B[(s, a, t)] + POST_B[(s, a, t)] == sum(SCHEDULES[s].values())
          for s in SHAPE_NAMES for a in ANCHOR_NAMES for t in TAU_GRID))

def _mono_in_q():
    # q ascending => FK nonincreasing (main grid + degeneracies, per cell)
    qs = sorted(ALL_Q)
    for s in SHAPE_NAMES:
        for a in ANCHOR_NAMES:
            for t in TAU_GRID:
                vals = [FK_A[(s, a, t, q)] for q in qs]
                if any(vals[i] < vals[i + 1] for i in range(len(vals) - 1)):
                    return False
    return True

check("F1: monotonicity — FK nonincreasing in q (every cell)", _mono_in_q())

def _mono_in_N():
    for q in ALL_Q:
        by_n = sorted((N_A[k], FK_A[k + (q,)]) for k in N_A)
        if any(by_n[i][1] < by_n[i + 1][1] for i in range(len(by_n) - 1)):
            return False
    return True

check("F1: monotonicity — FK nonincreasing in N (every q, all cells pooled)", _mono_in_N())

check("F1: anchor coincidence at tau = 0 (N and FK identical across anchors, every shape and q)",
      all(N_A[(s, "A-LIST", 0)] == N_A[(s, "A-FUNNEL", 0)] == N_A[(s, "A-CAP30", 0)]
          and all(FK_A[(s, "A-LIST", 0, q)] == FK_A[(s, "A-FUNNEL", 0, q)] == FK_A[(s, "A-CAP30", 0, q)]
                  for q in ALL_Q)
          for s in SHAPE_NAMES))

# ---------------------------------------------------------------------------
# F2 — the three structure theorems + monotone truncation (FULL grid)
# ---------------------------------------------------------------------------

check("F2 theorem 1 (ANCHOR INVARIANCE): A-FUNNEL N and FK exactly tau-invariant (every shape, every q)",
      all(N_A[(s, "A-FUNNEL", t)] == N_A[(s, "A-FUNNEL", TAU_GRID[0])] for s in SHAPE_NAMES for t in TAU_GRID)
      and all(FK_A[(s, "A-FUNNEL", t, q)] == FK_A[(s, "A-FUNNEL", TAU_GRID[0], q)]
              for s in SHAPE_NAMES for t in TAU_GRID for q in ALL_Q))

check("F2 theorem 2 (SPIKE STEP): A-LIST SPIKE N = 200*1[tau <= 13]; FK constant (1-q)^200 through tau = 13, exactly 1 at tau >= 14",
      all(N_A[("SPIKE", "A-LIST", t)] == (200 if t <= 13 else 0) for t in TAU_GRID)
      and all(FK_A[("SPIKE", "A-LIST", t, q)] == arm_a_FK(q, 200)
              for t in TAU_GRID if t <= 13 for q in ALL_Q)
      and all(FK_A[("SPIKE", "A-LIST", t, q)] == Fraction(1)
              for t in TAU_GRID if t >= 14 for q in ALL_Q))

check("F2 theorem 3 (CAP-30 EQUIVALENCE + BOUNDEDNESS): A-CAP30 == A-FUNNEL exactly for every grid tau <= 16 (every shape and q); occupancy <= 30 on the full grid; truncation at tau = 20 with BURN N = 174",
      all(N_A[(s, "A-CAP30", t)] == N_A[(s, "A-FUNNEL", t)]
          and all(FK_A[(s, "A-CAP30", t, q)] == FK_A[(s, "A-FUNNEL", t, q)] for q in ALL_Q)
          for s in SHAPE_NAMES for t in TAU_GRID if t <= 16)
      and all(occupancy("A-CAP30", t) <= 30 for t in TAU_GRID)
      and N_A[("BURN", "A-CAP30", 20)] == 174
      and N_A[("BURN", "A-CAP30", 20)] < N_A[("BURN", "A-FUNNEL", 20)])

def _monotone_truncation():
    for s in SHAPE_NAMES:
        ns = [N_A[(s, "A-LIST", t)] for t in TAU_GRID]
        if any(ns[i] < ns[i + 1] for i in range(len(ns) - 1)):
            return False
        for t in TAU_GRID:
            if t >= T_WINDOW and N_A[(s, "A-LIST", t)] != 0:
                return False
        for q in ALL_Q:
            fks = [FK_A[(s, "A-LIST", t, q)] for t in TAU_GRID]
            if any(fks[i] > fks[i + 1] for i in range(len(fks) - 1)):
                return False
            for t in TAU_GRID:
                if t >= T_WINDOW and FK_A[(s, "A-LIST", t, q)] != Fraction(1):
                    return False
    return True

check("F2 (MONOTONE TRUNCATION): A-LIST N nonincreasing in tau, zero at tau >= 14; FK nondecreasing, exactly 1 at tau >= 14 (every shape and q)",
      _monotone_truncation())

# ---------------------------------------------------------------------------
# F3 — closed-form anchors
# ---------------------------------------------------------------------------

AN = FX["anchors"]

burn_cum = []
run = 0
for d in range(1, 15):
    run += SCHEDULES["BURN"][d]
    burn_cum.append(run)
check("F3: BURN cumulative first-14 schedule (60, 90, ..., 192)",
      burn_cum == AN["burn_cumulative_schedule_first14"])

check("F3: BURN A-LIST N row across the tau grid = (192, 179, 155, 125, 60, 0)",
      [N_A[("BURN", "A-LIST", t)] for t in TAU_GRID] == AN["burn_alist_N_row"])

check("F3: BURN total mass 261", sum(SCHEDULES["BURN"].values()) == AN["burn_total_mass"])

check("F3: DRIP A-LIST N = 2*(14 - tau)^+ (every grid tau)",
      all(N_A[("DRIP", "A-LIST", t)] == 2 * max(0, T_WINDOW - t) for t in TAU_GRID))

check("F3: (99/100)^5 = 9509900499/10000000000 exact",
      Fraction(99, 100) ** 5 == Fraction(9509900499, 10 ** 10)
      and fr_str(Fraction(AN["q_pow_check"]["value"])) == "9509900499/10000000000")

check("F3: A-CAP30 tau = 20 BURN cell N = 174",
      N_A[("BURN", "A-CAP30", 20)] == AN["cap30_tau20_burn_N"])

# ---------------------------------------------------------------------------
# F4 — hand world (both arms)
# ---------------------------------------------------------------------------

HW = AN["hand_world"]
hw_sched = {d + 1: v for d, v in enumerate(HW["shape"])}
hw_q = Fraction(HW["q"])
hw_alist_N = arm_a_N(hw_sched, "A-LIST", HW["tau"], t_window=HW["window"], cap=CAP)
hw_funnel_N = arm_a_N(hw_sched, "A-FUNNEL", HW["tau"], t_window=HW["window"], cap=CAP)
hw_alist_walk = day_walk(hw_sched, "A-LIST", HW["tau"], hw_q, t_window=HW["window"], cap=CAP)
hw_funnel_walk = day_walk(hw_sched, "A-FUNNEL", HW["tau"], hw_q, t_window=HW["window"], cap=CAP)

check("F4: hand world A-LIST — N = 5, FK = 1/32 by pencil (both arms)",
      hw_alist_N == HW["alist_N"]
      and arm_a_FK(hw_q, hw_alist_N) == Fraction(HW["alist_FK"])
      and hw_alist_walk[0] == HW["alist_N"] and hw_alist_walk[3] == Fraction(HW["alist_FK"]))

check("F4: hand world funnel anchor — N = 6, FK = 1/64 by pencil (both arms)",
      hw_funnel_N == HW["funnel_N"]
      and arm_a_FK(hw_q, hw_funnel_N) == Fraction(HW["funnel_FK"])
      and hw_funnel_walk[0] == HW["funnel_N"] and hw_funnel_walk[3] == Fraction(HW["funnel_FK"]))

# ---------------------------------------------------------------------------
# F5 — degeneracies
# ---------------------------------------------------------------------------

check("F5: q = 0 -> FK = 1 everywhere (dead-product row, perfect specificity)",
      all(FK_A[(s, a, t, Fraction(0))] == Fraction(1)
          for s in SHAPE_NAMES for a in ANCHOR_NAMES for t in TAU_GRID))

check("F5: q = 1 -> FK = 1[N = 0] (the anchor certainty edge, every cell)",
      all(FK_A[(s, a, t, Fraction(1))] == (Fraction(1) if N_A[(s, a, t)] == 0 else Fraction(0))
          for s in SHAPE_NAMES for a in ANCHOR_NAMES for t in TAU_GRID))

check("F5: the tau = 20 A-LIST row = 1 exactly at every shape and q (the committed base case as arithmetic)",
      all(FK_A[(s, "A-LIST", 20, q)] == Fraction(1) for s in SHAPE_NAMES for q in ALL_Q))

# ---------------------------------------------------------------------------
# decision quantities (both arms) + doubling / occupancy rows
# ---------------------------------------------------------------------------

DECISION_SHAPE = FX["decision_rule"]["decision_cell"]["shape"]      # BURN
DECISION_ANCHOR = FX["decision_rule"]["decision_cell"]["anchor"]    # A-LIST
DC = FX["decision_rule"]["decision_constants"]
R1_HIGH = Fraction(DC["R1_high_line"])
R1_LOW = Fraction(DC["R1_low_line"])
R2_FACTOR = Fraction(DC["R2_doubling_factor"])
R2_MAX = DC["R2_onset_max"]
APPROVE_RATIO = Fraction(DC["APPROVE_ratio"])
APPROVE_ABS = Fraction(DC["APPROVE_abs_line"])


def doubling_onset(fk_by_tau):
    base = fk_by_tau[TAU_GRID[0]]
    for t in TAU_GRID:
        if fk_by_tau[t] >= R2_FACTOR * base:
            return t
    return None  # off-grid-right


def decision_numbers(fk_table, n_table):
    """Everything a decision evaluator needs, computed from one arm's tables."""
    prof = {t: fk_table[(DECISION_SHAPE, DECISION_ANCHOR, t, Q_DECISION)] for t in TAU_GRID}
    cap_prof = {t: fk_table[(DECISION_SHAPE, "A-CAP30", t, Q_DECISION)] for t in TAU_GRID}
    cap_flat = all(cap_prof[t] == cap_prof[0] for t in TAU_GRID if t <= 16)
    occ_max = max(occupancy("A-CAP30", t) for t in TAU_GRID)
    return {
        "fk0": prof[0],
        "fk13": prof[13],
        "profile": prof,
        "onset": doubling_onset(prof),
        "cap30_flat_thru_16": cap_flat,
        "cap30_occ_max": occ_max,
    }


NUMS_A = decision_numbers(FK_A, N_A)
NUMS_B = decision_numbers(FK_B, N_B)

DOUBLING_ROW = {}
for s in SHAPE_NAMES:
    for q in Q_GRID:
        prof = {t: FK_A[(s, "A-LIST", t, q)] for t in TAU_GRID}
        o = doubling_onset(prof)
        DOUBLING_ROW["%s|%s" % (s, fr_str(q))] = ("off-grid-right" if o is None else o)

OCC_ROW = {a: {str(t): occupancy(a, t) for t in TAU_GRID} for a in ANCHOR_NAMES}

# ---------------------------------------------------------------------------
# twin decision evaluators (independently written; registered order
# REJECT -> INVALID -> APPROVE -> NULL, INVALID short-circuit per C7)
# ---------------------------------------------------------------------------

def evaluator_A(nums, gates_green):
    if not gates_green:
        return "INVALID"
    r1 = (nums["fk13"] >= R1_HIGH) and (nums["fk0"] <= R1_LOW)
    r2 = (nums["onset"] is not None) and (nums["onset"] <= R2_MAX)
    r3 = nums["cap30_flat_thru_16"] and (nums["cap30_occ_max"] <= CAP)
    if r1 and r2 and r3:
        return "REJECT"
    if (nums["fk13"] <= APPROVE_RATIO * nums["fk0"]) and (nums["fk13"] <= APPROVE_ABS):
        return "APPROVE"
    return "NULL"


def evaluator_B(nums, gates_green):
    # independently coded: clause table walked in the registered order
    clauses = {
        "R1": nums["fk13"] * 2 >= 1 and nums["fk0"] * 5 <= 1,
        "R2": nums["onset"] is not None and nums["onset"] <= R2_MAX,
        "R3": nums["cap30_flat_thru_16"] and nums["cap30_occ_max"] <= CAP,
        "A1": nums["fk13"] * 5 <= nums["fk0"] * 6,
        "A2": nums["fk13"] * 4 <= 1,
    }
    for token in ("REJECT", "INVALID", "APPROVE", "NULL"):
        if token == "REJECT" and clauses["R1"] and clauses["R2"] and clauses["R3"]:
            return token
        if token == "INVALID" and not gates_green:
            return token
        if token == "APPROVE" and clauses["A1"] and clauses["A2"]:
            return token
        if token == "NULL":
            return token


# ---------------------------------------------------------------------------
# Arm R — seeded, REPORTING-ONLY (no statistical gate)
# ---------------------------------------------------------------------------

RP = FX["arm_R_params"]
R_CELLS = [(c[0], c[1]) for c in RP["cells"]]
QN, QD = Q_DECISION.numerator, Q_DECISION.denominator


def arm_r_leg(rng, episodes):
    out = {}
    for anchor, tau in R_CELLS:
        n = N_A[(DECISION_SHAPE, anchor, tau)]
        zero = 0
        draws = 0
        rnd = rng.random
        for _ in range(episodes):
            sales = 0
            ep_draws = 0
            for _ in range(n):
                u = rnd()
                ep_draws += 1
                a, b = u.as_integer_ratio()
                if a * QD < QN * b:  # exact-rational u < q (C1)
                    sales += 1
            if ep_draws != n:
                raise AssertionError("draw-count sentinel broke mid-episode")
            draws += ep_draws
            if sales == 0:
                zero += 1
        out["%s|tau=%d" % (anchor, tau)] = {
            "N": n,
            "episodes": episodes,
            "zero_sale_episodes": zero,
            "fk_hat": repr(zero / episodes),
            "fk_exact": fr_str(FK_A[(DECISION_SHAPE, anchor, tau, Q_DECISION)]),
            "fk_exact_float": repr(float(FK_A[(DECISION_SHAPE, anchor, tau, Q_DECISION)])),
            "draws": draws,
        }
    return out


rng_main = make_rng(FX["seeds"]["main"])
ARM_R_MAIN = arm_r_leg(rng_main, RP["episodes_main"])
rng_stab = make_rng(FX["seeds"]["stability"])
ARM_R_STAB = arm_r_leg(rng_stab, RP["episodes_stability"])

check("F6: Arm-R draw-count sentinels exact (main leg: episodes * N per cell)",
      all(v["draws"] == v["episodes"] * v["N"] for v in ARM_R_MAIN.values()))
check("F6: Arm-R draw-count sentinels exact (stability leg)",
      all(v["draws"] == v["episodes"] * v["N"] for v in ARM_R_STAB.values()))

# ---------------------------------------------------------------------------
# drafter-disclosed landing — re-derived and COMPARED, never gated (C9/C11)
# ---------------------------------------------------------------------------

DD = FX["drafter_disclosed_never_gated"]
ANOMALIES = []
COMPARISONS = []


def compare(label, exact_fr, disclosed_float):
    ds = repr(float(disclosed_float))
    places = len(ds.split(".")[1])
    mine = fr_round_str(exact_fr, places)
    ok = (mine == ds)
    COMPARISONS.append({"label": label, "disclosed": ds, "rederived": mine, "match": ok})
    if not ok:
        ANOMALIES.append("%s: disclosed %s vs re-derived %s (exact %s)"
                         % (label, ds, mine, fr_str(exact_fr)))
    return ok


dec_prof = NUMS_A["profile"]
for i, t in enumerate(TAU_GRID):
    compare("decision-cell FK(tau=%d)" % t, dec_prof[t], DD["decision_cell_FK_by_tau"][i])

compare("R1 high-line margin FK(13)/(1/2)", dec_prof[13] / R1_HIGH,
        float(DD["R1_high_margin"].split(" at ")[1].rstrip("x")))
compare("R1 low-line margin (1/5)/FK(0)", R1_LOW / dec_prof[0],
        float(DD["R1_low_margin"].split(" at ")[1].rstrip("x under")))
COMPARISONS.append({"label": "R2 doubling onset", "disclosed": str(DD["R2_onset"]),
                    "rederived": str(NUMS_A["onset"]), "match": NUMS_A["onset"] == DD["R2_onset"]})
if NUMS_A["onset"] != DD["R2_onset"]:
    ANOMALIES.append("R2 doubling onset: disclosed %s vs re-derived %s" % (DD["R2_onset"], NUMS_A["onset"]))
compare("R2 ratio FK(13)/FK(0)", dec_prof[13] / dec_prof[0], DD["R2_ratio_at_13"])
compare("R2 ratio FK(10)/FK(0)", dec_prof[10] / dec_prof[0], DD["R2_ratio_at_10"])
compare("A-CAP30 flat value (decision cell)",
        FK_A[("BURN", "A-CAP30", 0, Q_DECISION)], DD["cap30_flat_value"])
compare("A-CAP30 tau = 20 FK (BURN, q = 1/100)",
        FK_A[("BURN", "A-CAP30", 20, Q_DECISION)], DD["cap30_tau20_FK"])
compare("SPIKE FK constant (A-LIST, q = 1/100, tau <= 13)",
        FK_A[("SPIKE", "A-LIST", 0, Q_DECISION)], DD["spike_FK_constant"])
compare("q = 1/30 FK(13) (BURN, A-LIST)",
        FK_A[("BURN", "A-LIST", 13, Fraction(1, 30))], DD["q_1_30_FK13"])
compare("q = 1/30 ratio FK(13)/FK(0)",
        FK_A[("BURN", "A-LIST", 13, Fraction(1, 30))] / FK_A[("BURN", "A-LIST", 0, Fraction(1, 30))],
        DD["q_1_30_ratio"])
compare("q = 1/300 FK(0) (BURN, A-LIST)",
        FK_A[("BURN", "A-LIST", 0, Fraction(1, 300))], DD["q_1_300_FK0"])
compare("DRIP FK(0) (A-LIST, q = 1/100)",
        FK_A[("DRIP", "A-LIST", 0, Q_DECISION)], DD["drip_FK0"])

# ---------------------------------------------------------------------------
# reporting rows (never gated)
# ---------------------------------------------------------------------------

SPIKE_APPROVE_CLAUSES = (
    FK_A[("SPIKE", "A-LIST", 13, Q_DECISION)] <= APPROVE_RATIO * FK_A[("SPIKE", "A-LIST", 0, Q_DECISION)]
    and FK_A[("SPIKE", "A-LIST", 13, Q_DECISION)] <= APPROVE_ABS)

Q30_R1 = (FK_A[("BURN", "A-LIST", 13, Fraction(1, 30))] >= R1_HIGH
          and FK_A[("BURN", "A-LIST", 0, Fraction(1, 30))] <= R1_LOW)
Q300_R1 = (FK_A[("BURN", "A-LIST", 13, Fraction(1, 300))] >= R1_HIGH
           and FK_A[("BURN", "A-LIST", 0, Fraction(1, 300))] <= R1_LOW)

QUEUE_ROW = {str(t): fr_round_str(10 * dec_prof[t], 6) for t in TAU_GRID}

REPORTING = {
    "spike_lands_approve_clauses_at_decision_q": SPIKE_APPROVE_CLAUSES,
    "q_1_30_R1_fires": Q30_R1,
    "q_1_300_R1_fires": Q300_R1,
    "queue_row_expected_false_kills_10_products_A_LIST": QUEUE_ROW,
    "lived_launch_column": "tau = 0 by the committed timestamps (16:25:16Z listing / 17:18:47Z article, same day) — the committed rule has never yet been exercised at the tau values where it misbehaves",
}

# ---------------------------------------------------------------------------
# F6 battery — twin equality, evaluators, seed registry
# ---------------------------------------------------------------------------

check("F6: Arm B (literal day-walk) exact-equal on every published number (N + FK, all cells, all q incl. degeneracies)",
      all(N_A[k] == N_B[k] for k in N_A) and all(FK_A[k] == FK_B[k] for k in FK_A))

GATES_GREEN_SO_FAR = all(ok for _, ok in CHECKS)
TOKEN_A = evaluator_A(NUMS_A, GATES_GREEN_SO_FAR)
TOKEN_B = evaluator_B(NUMS_B, GATES_GREEN_SO_FAR)

check("F6: twin independently-written decision evaluators agree on the token",
      TOKEN_A == TOKEN_B)

check("F6: seed constructor registry == [main, stability] + presentation pending; aux 20261583 never read",
      SEED_REGISTRY == [FX["seeds"]["main"], FX["seeds"]["stability"]]
      and FX["seeds"]["aux_never_read"] not in SEED_REGISTRY)

# presentation shuffle (read by the presentation-shuffled stdout listing only)
rng_pres = make_rng(FX["seeds"]["presentation"])
grid_lines = []
for s in SHAPE_NAMES:
    for a in ANCHOR_NAMES:
        for t in TAU_GRID:
            for q in Q_GRID:
                grid_lines.append("%s %s tau=%-2d q=%-5s N=%-3d FK=%s"
                                  % (s.ljust(5), a.ljust(8), t, fr_str(q), N_A[(s, a, t)],
                                     fr_round_str(FK_A[(s, a, t, q)], 6)))
rng_pres.shuffle(grid_lines)

check("F6: final seed registry exact ([20261580, 20261581, 20261582]); aux never constructed",
      SEED_REGISTRY == [FX["seeds"]["main"], FX["seeds"]["stability"], FX["seeds"]["presentation"]]
      and FX["seeds"]["aux_never_read"] not in SEED_REGISTRY)

# ---------------------------------------------------------------------------
# ruling + output
# ---------------------------------------------------------------------------

GATES_GREEN = all(ok for _, ok in CHECKS)
TOKEN = TOKEN_A if GATES_GREEN else "INVALID"

R1_FIRES = (NUMS_A["fk13"] >= R1_HIGH) and (NUMS_A["fk0"] <= R1_LOW)
R2_FIRES = (NUMS_A["onset"] is not None) and (NUMS_A["onset"] <= R2_MAX)
R3_FIRES = NUMS_A["cap30_flat_thru_16"] and (NUMS_A["cap30_occ_max"] <= CAP)

print("")
print("=== decision cell (BURN, A-LIST, q = 1/100) — exact ===")
for t in TAU_GRID:
    print("FK(tau=%-2d) = %s  (~ %s)" % (t, fr_str(dec_prof[t]), fr_round_str(dec_prof[t], 6)))
print("R1: FK(13) >= 1/2 -> %s (margin %sx); FK(0) <= 1/5 -> %s (%sx under)"
      % (NUMS_A["fk13"] >= R1_HIGH, fr_round_str(NUMS_A["fk13"] / R1_HIGH, 4),
         NUMS_A["fk0"] <= R1_LOW, fr_round_str(R1_LOW / NUMS_A["fk0"], 4)))
print("R2: doubling onset = %s (<= 13 -> %s); ratio at 13 = %sx, at 10 = %sx"
      % (NUMS_A["onset"], R2_FIRES, fr_round_str(dec_prof[13] / dec_prof[0], 4),
         fr_round_str(dec_prof[10] / dec_prof[0], 4)))
print("R3: A-CAP30 flat through tau <= 16 -> %s; worst occupancy = %d <= 30 -> %s"
      % (NUMS_A["cap30_flat_thru_16"], NUMS_A["cap30_occ_max"], NUMS_A["cap30_occ_max"] <= CAP))
print("REJECT conjuncts: R1=%s R2=%s R3=%s" % (R1_FIRES, R2_FIRES, R3_FIRES))
print("tokens: evaluator_A=%s evaluator_B=%s -> RULING: %s" % (TOKEN_A, TOKEN_B, TOKEN))

print("")
print("=== doubling-onset row (A-LIST, min grid tau with FK >= 2*FK(0)) ===")
for k in sorted(DOUBLING_ROW):
    print("%-14s -> %s" % (k, DOUBLING_ROW[k]))

print("")
print("=== occupancy row (days) ===")
for a in ANCHOR_NAMES:
    print("%-8s : %s" % (a, "  ".join("tau=%d:%d" % (t, OCC_ROW[a][str(t)]) for t in TAU_GRID)))

print("")
print("=== Arm R (seeded, REPORTING-ONLY — no statistical gate) ===")
for leg_name, leg in (("main", ARM_R_MAIN), ("stability", ARM_R_STAB)):
    for cell in sorted(leg):
        v = leg[cell]
        print("%-9s %-16s N=%-3d episodes=%-6d fk_hat=%s  fk_exact~%s"
              % (leg_name, cell, v["N"], v["episodes"], v["fk_hat"],
                 fr_round_str(Fraction(v["fk_exact"]), 6)))

print("")
print("=== drafter-disclosed landing, re-derived (COMPARED, never gated) ===")
for c in COMPARISONS:
    print("%s  %-45s disclosed=%-10s rederived=%s"
          % ("match " if c["match"] else "MISMATCH", c["label"], c["disclosed"], c["rederived"]))
print("anomalies: %d" % len(ANOMALIES))
for a in ANOMALIES:
    print("  ANOMALY: " + a)

print("")
print("=== reporting rows (never gated) ===")
print("SPIKE lands the APPROVE clauses at the decision q: %s" % SPIKE_APPROVE_CLAUSES)
print("q = 1/30 R1 fires: %s   q = 1/300 R1 fires: %s" % (Q30_R1, Q300_R1))
print("10-product queue row (10*FK, A-LIST): %s"
      % "  ".join("tau=%s:%s" % (t, QUEUE_ROW[str(t)]) for t in map(str, TAU_GRID)))

print("")
print("=== full main-grid FK listing (presentation-shuffled, seed 20261582) ===")
for line in grid_lines:
    print(line)

# ---------------------------------------------------------------------------
# results.json (canonical, no timestamps)
# ---------------------------------------------------------------------------

results = {
    "verdict": TOKEN,
    "tokens": {"evaluator_A": TOKEN_A, "evaluator_B": TOKEN_B},
    "reject_conjuncts": {"R1": R1_FIRES, "R2": R2_FIRES, "R3": R3_FIRES},
    "decision_cell": {
        "shape": DECISION_SHAPE, "anchor": DECISION_ANCHOR, "q": fr_str(Q_DECISION),
        "FK_by_tau": {str(t): fk_render(dec_prof[t]) for t in TAU_GRID},
        "R1_high_margin": fr_round_str(NUMS_A["fk13"] / R1_HIGH, 4) + "x",
        "R1_low_margin_under": fr_round_str(R1_LOW / NUMS_A["fk0"], 4) + "x",
        "doubling_onset": NUMS_A["onset"],
        "ratio_at_13": fr_round_str(dec_prof[13] / dec_prof[0], 4),
        "ratio_at_10": fr_round_str(dec_prof[10] / dec_prof[0], 4),
        "cap30_flat_thru_16": NUMS_A["cap30_flat_thru_16"],
        "cap30_occ_max": NUMS_A["cap30_occ_max"],
    },
    "N_table": {"%s|%s|tau=%d" % k: v for k, v in sorted(N_A.items())},
    "FK_table": {"%s|%s|tau=%d|q=%s" % (s, a, t, fr_str(q)): fk_render(FK_A[(s, a, t, q)])
                 for s in SHAPE_NAMES for a in ANCHOR_NAMES for t in TAU_GRID for q in ALL_Q},
    "doubling_onset_row_A_LIST": DOUBLING_ROW,
    "occupancy_row": OCC_ROW,
    "arm_R": {"main": ARM_R_MAIN, "stability": ARM_R_STAB,
              "note": "REPORTING-ONLY; no statistical gate; drift from the exact FK is a named finding, never a ruling"},
    "disclosed_landing_comparison": COMPARISONS,
    "anomalies": ANOMALIES,
    "reporting": REPORTING,
    "checks": [{"name": n, "pass": ok} for n, ok in CHECKS],
    "checks_passed": sum(1 for _, ok in CHECKS if ok),
    "checks_failed": sum(1 for _, ok in CHECKS if not ok),
    "seed_registry": SEED_REGISTRY,
    "python": "cpython-%d.%d" % sys.version_info[:2],
}

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=1, sort_keys=True)
    fh.write("\n")

print("")
n_pass = sum(1 for _, ok in CHECKS if ok)
n_fail = sum(1 for _, ok in CHECKS if not ok)
print("self-checks: %d passed, %d failed" % (n_pass, n_fail))
print("RULING: %s" % TOKEN)
sys.exit(0 if n_fail == 0 else 1)
