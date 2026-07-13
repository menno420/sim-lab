#!/usr/bin/env python3
"""VERDICT 060 — the magnet press-fit band (idea-engine PROPOSAL 049).

Does the shipped `magnet_fit = 0.15` mm diametral interference default
(curious-research projects/effector-mount/magnet_tool.scad @ a9fd5fa) land the
as-printed pocket in the PRESS band across the pinned printer population, and
at what DROPS-OUT / UNSEATABLE error rate?

Arm A (DECISION, seedless, exact): full enumeration of the 41 x 11 x 21 =
9,471-cell equiprobable integer lattice per grid F; every probability an
exact fractions.Fraction; run twice in-process and identity-checked; the
ruling is evaluated in the registered order (REJECT first / INVALID controls
gate / APPROVE / NULL) by two independently-written evaluators.

Arm B (VALIDATION, seeded MC): N = 200,000 common-random-numbers scenario
draws via random.Random(20261333), pinned draw order H -> m -> eta, evaluated
at all six grid F. The four pre-registered seeds ONLY (20261333 headline /
20261334 zero-noise identity control / 20261335 sensitivity confirmations /
20261336 stability). Validation only; never overrides Arm A.

Reporting-only: the full DROP/UNSEAT/FAIL x F table with split, the
glue-fallback view FAIL_glue(F) = UNSEAT(F), the per-H conditional
FAIL(15 | H) curve, the ten sensitivity worlds, the remedy-direction
inversion flag, and the drafter-reference comparison (never gated).

Hermetic: reads only its own fixtures.json. Stdlib only. No wall-clock in
any output. Byte-identical stdout + results.json across process runs.

Run: python3 sims/verdict-060-magnet-press-fit-band/magnet_fit_sim.py
"""

import json
import math
import os
import platform
import random
import sys
from fractions import Fraction

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- self-checks
_CHECKS = {"passed": 0, "failed": 0}


def check(cond, label):
    if cond:
        _CHECKS["passed"] += 1
    else:
        _CHECKS["failed"] += 1
        print("SELF-CHECK FAIL: %s" % label)
        sys.exit(1)


# ------------------------------------------------------------- environment pin
check(platform.python_implementation() == "CPython", "interpreter is CPython")
check(sys.version_info[:2] == (3, 11), "CPython 3.11 pinned")

# ------------------------------------------------------------------- fixtures
with open(os.path.join(BASE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)


def Fr(d):
    return Fraction(d["num"], d["den"])


GRID = list(FX["model"]["fit_grid_cmm"])
F_DEFAULT = FX["model"]["shipped_default_F"]
POP = FX["model"]["population"]
BANDS = FX["model"]["bands"]
I_HOLD = BANDS["I_hold"]
I_SEAT = BANDS["I_seat"]
REJECT_BAND = Fr(FX["decision_rule"]["reject_band"])
APPROVE_BAND = Fr(FX["decision_rule"]["approve_band"])
WC_BAND = Fr(FX["decision_rule"]["wrong_center_band"])
N_MC = FX["arm_B"]["N"]
SEEDS = {
    "headline": 20261333,
    "zero_noise_control": 20261334,
    "sensitivity": 20261335,
    "stability": 20261336,
}

# transcription gates — re-derive every derived constant from the pinned base
# and check it against the fixture's own value (a gate on the copy, not trust)
check(sorted(str(s) for s in SEEDS.values()) == sorted(FX["seeds"].keys() - {"policy"}),
      "the four registered seeds and no others")
check(all(s > 20261332 for s in SEEDS.values()),
      "all seeds strictly above the P048/V059 high-water 20261332")
check(GRID == [5, 10, 15, 20, 25, 30], "fit grid pinned {5,10,15,20,25,30}")
check(F_DEFAULT == 15 and F_DEFAULT in GRID, "shipped default F = 15, a grid cell")
CAL = FX["model"]["exemplar_calibration"]
check(CAL["coin_row_diametral_cmm"] ==
      {k: 2 * v for k, v in CAL["coin_row_per_side_cmm"].items()},
      "coin row diametral = 2 x per-side (the coin's own lines 14-16 rule)")
check(CAL["pair_offset_S"] == CAL["coin_row_diametral_cmm"]["snug"] == 40,
      "pair offset S = 40 (Snug = zero effective as-printed gap)")
RHO = Fr(CAL["hole_share_rho"])
check(RHO == Fraction(1, 2), "hole share rho = 1/2 pinned")
check(Fraction(CAL["population_center_H0"]) == RHO * CAL["pair_offset_S"] == 20,
      "population center H0 = rho * S = 20")
check((POP["H"]["lo"], POP["H"]["hi"]) == (0, 40), "H ~ uniform int {0..40}")
check((POP["H"]["lo"] + POP["H"]["hi"]) // 2 == CAL["population_center_H0"],
      "H span centered on H0 = 20")
check((POP["eta"]["lo"], POP["eta"]["hi"]) == (-10, 10), "eta ~ uniform int {-10..+10}")
check((POP["m"]["lo"], POP["m"]["hi"]) == (-5, 5), "m ~ uniform int {-5..+5}")
check(I_HOLD == 10 and I_SEAT == 50, "band constants I_hold = 10, I_seat = 50")
check(I_HOLD == (0 + 20) // 2, "I_hold = midpoint of the exemplar's no-grip-at-0 / held-at-20 bracket")
LAT = FX["model"]["lattice"]
check(LAT["H_cells"] == 41 and LAT["m_cells"] == 11 and LAT["eta_cells"] == 21,
      "lattice cell counts 41 / 11 / 21")
check(LAT["total"] == 41 * 11 * 21 == 9471, "lattice total 9,471 cells")
check(REJECT_BAND == Fraction(1, 10) and APPROVE_BAND == Fraction(1, 20)
      and WC_BAND == Fraction(1, 100), "decision bands 1/10 / 1/20 / 1/100")
check(FX["decision_rule"]["evaluation_order"] == ["REJECT", "INVALID", "APPROVE", "NULL"],
      "evaluation order pinned: REJECT first")

HEADLINE_CFG = {
    "H": (POP["H"]["lo"], POP["H"]["hi"]),
    "m": (POP["m"]["lo"], POP["m"]["hi"]),
    "eta": (POP["eta"]["lo"], POP["eta"]["hi"]),
    "I_hold": I_HOLD,
    "I_seat": I_SEAT,
}


def classify(I, i_hold, i_seat):
    """The coin bands translated to interference: DROP < hold <= PRESS <= seat < UNSEAT."""
    if I < i_hold:
        return "drop"
    if I > i_seat:
        return "unseat"
    return "press"


# ------------------------------------------------------------- Arm A (DECISION)
def arm_A(cfg, grid):
    """Seedless exact full enumeration; every probability an exact Fraction."""
    h_lo, h_hi = cfg["H"]
    m_lo, m_hi = cfg["m"]
    e_lo, e_hi = cfg["eta"]
    i_hold, i_seat = cfg["I_hold"], cfg["I_seat"]
    total = (h_hi - h_lo + 1) * (m_hi - m_lo + 1) * (e_hi - e_lo + 1)
    out = {}
    for f in grid:
        drop = unseat = 0
        for H in range(h_lo, h_hi + 1):
            for m in range(m_lo, m_hi + 1):
                for eta in range(e_lo, e_hi + 1):
                    band = classify(f + H + m - eta, i_hold, i_seat)
                    if band == "drop":
                        drop += 1
                    elif band == "unseat":
                        unseat += 1
        out[f] = {"DROP": Fraction(drop, total),
                  "UNSEAT": Fraction(unseat, total),
                  "FAIL": Fraction(drop + unseat, total)}
    return out


ARM_A = arm_A(HEADLINE_CFG, GRID)
ARM_A_RERUN = arm_A(HEADLINE_CFG, GRID)  # in-process identity twin
check(ARM_A == ARM_A_RERUN, "two Arm-A computations identical rationals")
for f in GRID:
    check(ARM_A[f]["DROP"] + ARM_A[f]["UNSEAT"] == ARM_A[f]["FAIL"],
          "FAIL(%d) = DROP + UNSEAT exact" % f)
    check(0 <= ARM_A[f]["FAIL"] <= 1, "FAIL(%d) a probability" % f)

FAIL15 = ARM_A[F_DEFAULT]["FAIL"]
MIN_FAIL = min(ARM_A[f]["FAIL"] for f in GRID)
MIN_F_ARG = min(f for f in GRID if ARM_A[f]["FAIL"] == MIN_FAIL)

# monotonicity theorem gates (controls; a violation is an implementation
# defect -> INVALID by the registered rule, recorded, not crashed)
MONO_DROP_A = all(ARM_A[GRID[i]]["DROP"] >= ARM_A[GRID[i + 1]]["DROP"]
                  for i in range(len(GRID) - 1))
MONO_UNSEAT_A = all(ARM_A[GRID[i]]["UNSEAT"] <= ARM_A[GRID[i + 1]]["UNSEAT"]
                    for i in range(len(GRID) - 1))

# per-H conditional FAIL(15 | H) curve (reporting-only)
PER_H = []
_sub_total = (HEADLINE_CFG["m"][1] - HEADLINE_CFG["m"][0] + 1) * \
             (HEADLINE_CFG["eta"][1] - HEADLINE_CFG["eta"][0] + 1)
for H in range(HEADLINE_CFG["H"][0], HEADLINE_CFG["H"][1] + 1):
    fail = 0
    for m in range(HEADLINE_CFG["m"][0], HEADLINE_CFG["m"][1] + 1):
        for eta in range(HEADLINE_CFG["eta"][0], HEADLINE_CFG["eta"][1] + 1):
            if classify(F_DEFAULT + H + m - eta, I_HOLD, I_SEAT) != "press":
                fail += 1
    PER_H.append((H, Fraction(fail, _sub_total)))
check(sum(fr for _, fr in PER_H) / len(PER_H) == FAIL15,
      "per-H conditional curve averages back to FAIL(15) exactly (total probability)")

# zero-noise identity world, Arm A side: eta ≡ 0, m ≡ 0, H ≡ 20
ZERO_CFG = {"H": (20, 20), "m": (0, 0), "eta": (0, 0), "I_hold": I_HOLD, "I_seat": I_SEAT}
ZERO_A = arm_A(ZERO_CFG, GRID)
ZERO_A_OK = all(ZERO_A[f]["FAIL"] == 0 and ZERO_A[f]["DROP"] == 0
                and ZERO_A[f]["UNSEAT"] == 0 for f in GRID)

# ---------------------------------------------------- Arm B (seeded VALIDATION)
_RNGS_CONSTRUCTED = []


class CountingRandom(object):
    """Wrapper: registers construction, counts every draw (one randint call)."""

    def __init__(self, seed):
        _RNGS_CONSTRUCTED.append(seed)
        self._r = random.Random(seed)
        self.draws = 0

    def randint(self, lo, hi):
        self.draws += 1
        return self._r.randint(lo, hi)


def mc_counts(rng, cfg, grid, n):
    """Common random numbers: per scenario draw H -> m -> eta (pinned order),
    evaluate at every grid F. Returns per-F counts {drop, unseat, fail}."""
    counts = {f: {"drop": 0, "unseat": 0} for f in grid}
    i_hold, i_seat = cfg["I_hold"], cfg["I_seat"]
    for _ in range(n):
        H = rng.randint(cfg["H"][0], cfg["H"][1])
        m = rng.randint(cfg["m"][0], cfg["m"][1])
        eta = rng.randint(cfg["eta"][0], cfg["eta"][1])
        base = H + m - eta
        for f in grid:
            band = classify(f + base, i_hold, i_seat)
            if band == "drop":
                counts[f]["drop"] += 1
            elif band == "unseat":
                counts[f]["unseat"] += 1
    return counts


def agreement_row(f, counts, exact, n):
    fail_cnt = counts[f]["drop"] + counts[f]["unseat"]
    fail_hat = Fraction(fail_cnt, n)
    p_a = exact[f]["FAIL"]
    se = math.sqrt(float(p_a) * (1.0 - float(p_a)) / n)
    dev_exact = abs(fail_hat - p_a)                      # exact Fraction
    dev_float = abs(float(fail_hat) - float(p_a))
    within_abs = dev_exact <= Fraction(1, 100)           # exact comparison
    within_4se = dev_float <= 4.0 * se
    return {"F": f, "fail_count": fail_cnt, "N": n,
            "FAIL_hat": {"num": fail_hat.numerator, "den": fail_hat.denominator},
            "FAIL_hat_float": float(fail_hat),
            "FAIL_exact_float": float(p_a),
            "abs_dev": dev_float, "se": se, "tol_4se": 4.0 * se,
            "within_1_100": bool(within_abs), "within_4se": bool(within_4se),
            "pass": bool(within_abs and within_4se)}


# headline leg, seed 20261333
RNG_HEAD = CountingRandom(SEEDS["headline"])
HEAD_COUNTS = mc_counts(RNG_HEAD, HEADLINE_CFG, GRID, N_MC)
check(RNG_HEAD.draws == 3 * N_MC == 600000, "draw sentinel headline: 600,000")
AGREE = [agreement_row(f, HEAD_COUNTS, ARM_A, N_MC) for f in GRID]
AGREE_ALL = all(row["pass"] for row in AGREE)
# Arm-B empirical monotonicity (theorem under common random numbers)
MONO_DROP_B = all(HEAD_COUNTS[GRID[i]]["drop"] >= HEAD_COUNTS[GRID[i + 1]]["drop"]
                  for i in range(len(GRID) - 1))
MONO_UNSEAT_B = all(HEAD_COUNTS[GRID[i]]["unseat"] <= HEAD_COUNTS[GRID[i + 1]]["unseat"]
                    for i in range(len(GRID) - 1))

# zero-noise identity control, seed 20261334 (exact identity, not a tolerance)
N_CTRL = 20000
RNG_ZERO = CountingRandom(SEEDS["zero_noise_control"])
ZERO_COUNTS = mc_counts(RNG_ZERO, ZERO_CFG, GRID, N_CTRL)
check(RNG_ZERO.draws == 3 * N_CTRL == 60000, "draw sentinel zero-noise control: 60,000")
ZERO_B_OK = all(ZERO_COUNTS[f]["drop"] == 0 and ZERO_COUNTS[f]["unseat"] == 0
                for f in GRID)
ZERO_OK = ZERO_A_OK and ZERO_B_OK

# --------------------------------------- sensitivity worlds (seed 20261335,
# N = 20,000 each, REPORTING-ONLY — never flip the decision)
N_SENS = 20000
WORLD_ORDER = FX["sensitivity_worlds"]["order"]
check(WORLD_ORDER == ["H_narrow", "H_wide", "eta_narrow", "eta_wide",
                      "m_degenerate", "m_wide", "I_hold_5", "I_hold_15",
                      "I_seat_40", "I_seat_60"],
      "sensitivity world order pinned (ten worlds)")


def world_cfg(name):
    cfg = dict(HEADLINE_CFG)
    spec = FX["sensitivity_worlds"][name]
    for key, val in spec.items():
        if key in ("H", "m", "eta"):
            cfg[key] = (val["lo"], val["hi"])
        else:
            cfg[key] = val
    return cfg


RNG_SENS = CountingRandom(SEEDS["sensitivity"])
SENS = []
for name in WORLD_ORDER:
    cfg = world_cfg(name)
    exact = arm_A(cfg, GRID)
    counts = mc_counts(RNG_SENS, cfg, GRID, N_SENS)
    rows = [agreement_row(f, counts, exact, N_SENS) for f in GRID]
    w_fail15 = exact[F_DEFAULT]["FAIL"]
    SENS.append({
        "world": name,
        "FAIL15": {"num": w_fail15.numerator, "den": w_fail15.denominator},
        "FAIL15_float": float(w_fail15),
        "DROP15_float": float(exact[F_DEFAULT]["DROP"]),
        "UNSEAT15_float": float(exact[F_DEFAULT]["UNSEAT"]),
        "side_reject_edge": "above" if w_fail15 > REJECT_BAND else "at-or-below",
        "side_approve_edge": "above" if w_fail15 > APPROVE_BAND else "at-or-below",
        "straddle_vs_headline": bool(
            (w_fail15 > REJECT_BAND) != (FAIL15 > REJECT_BAND)
            or (w_fail15 > APPROVE_BAND) != (FAIL15 > APPROVE_BAND)),
        "mc_confirms_all_cells": bool(all(r["pass"] for r in rows)),
        "mc_FAIL15_hat_float": [r for r in rows if r["F"] == F_DEFAULT][0]["FAIL_hat_float"],
    })
check(RNG_SENS.draws == 3 * N_SENS * len(WORLD_ORDER) == 600000,
      "draw sentinel sensitivity: 600,000 across the ten worlds, one RNG, pinned order")
STRADDLE_WORLDS = [w["world"] for w in SENS if w["straddle_vs_headline"]]

# ------------------------------------------- stability leg (seed 20261336)
N_STAB = 20000
RNG_STAB = CountingRandom(SEEDS["stability"])
STAB_COUNTS = mc_counts(RNG_STAB, HEADLINE_CFG, GRID, N_STAB)
check(RNG_STAB.draws == 3 * N_STAB == 60000, "draw sentinel stability: 60,000")
STAB_FAIL15 = Fraction(STAB_COUNTS[F_DEFAULT]["drop"] + STAB_COUNTS[F_DEFAULT]["unseat"], N_STAB)
STAB_MIN_FAIL = min(Fraction(STAB_COUNTS[f]["drop"] + STAB_COUNTS[f]["unseat"], N_STAB)
                    for f in GRID)

check(_RNGS_CONSTRUCTED == [SEEDS["headline"], SEEDS["zero_noise_control"],
                            SEEDS["sensitivity"], SEEDS["stability"]],
      "exactly four RNGs constructed, registered seeds, pinned order")

# ------------------------------------------------- controls gate (INVALID)
GATES = {
    "zero_noise_identity_arm_A": bool(ZERO_A_OK),
    "zero_noise_identity_arm_B": bool(ZERO_B_OK),
    "monotonicity_DROP_nonincreasing_arm_A": bool(MONO_DROP_A),
    "monotonicity_UNSEAT_nondecreasing_arm_A": bool(MONO_UNSEAT_A),
    "monotonicity_DROP_nonincreasing_arm_B": bool(MONO_DROP_B),
    "monotonicity_UNSEAT_nondecreasing_arm_B": bool(MONO_UNSEAT_B),
    "arm_B_agreement_every_cell": bool(AGREE_ALL),
}
GATES_OK = all(GATES.values())


# ------------------------------------------------- twin decision evaluators
def evaluate_fraction(fail15, min_fail, gates_ok, stab_ok):
    """Evaluator 1: Fraction comparisons, registered order (REJECT first)."""
    if fail15 > Fraction(1, 10):
        return "reject"
    if not gates_ok:
        return "invalid"
    if fail15 <= Fraction(1, 20) and fail15 <= min_fail + Fraction(1, 100) and stab_ok:
        return "approve"
    return "null"


def evaluate_integer(fail15, min_fail, gates_ok, stab_ok):
    """Evaluator 2: pure-integer cross-multiplication (Fraction normalizes
    denominators positive, so every band test is an integer inequality);
    same registered order, different arithmetic path."""
    n, d = fail15.numerator, fail15.denominator
    mn, md = min_fail.numerator, min_fail.denominator
    if 10 * n > d:                       # fail15 > 1/10
        return "reject"
    if not gates_ok:
        return "invalid"
    conj_a = 20 * n <= d                 # fail15 <= 1/20
    conj_b = 100 * n * md <= d * (100 * mn + md)   # fail15 <= min_fail + 1/100
    if conj_a and conj_b and stab_ok:
        return "approve"
    return "null"


# provisional Arm-A class (stability placeholder True — non-circular: the
# stability leg must reproduce THIS class; only the APPROVE branch consumes
# the stability conjunct in the final evaluation)
PRE_1 = evaluate_fraction(FAIL15, MIN_FAIL, GATES_OK, True)
PRE_2 = evaluate_integer(FAIL15, MIN_FAIL, GATES_OK, True)
check(PRE_1 == PRE_2, "twin evaluators agree on the provisional Arm-A class")

STAB_1 = evaluate_fraction(STAB_FAIL15, STAB_MIN_FAIL, True, True)
STAB_2 = evaluate_integer(STAB_FAIL15, STAB_MIN_FAIL, True, True)
check(STAB_1 == STAB_2, "twin evaluators agree on the stability-leg class")
STAB_OK = STAB_1 == PRE_1

VERDICT_1 = evaluate_fraction(FAIL15, MIN_FAIL, GATES_OK, STAB_OK)
VERDICT_2 = evaluate_integer(FAIL15, MIN_FAIL, GATES_OK, STAB_OK)
check(VERDICT_1 == VERDICT_2, "twin evaluators agree on the final verdict")
VERDICT = VERDICT_1

# NULL axis naming (registered axes; empty unless the verdict is null)
NULL_AXES = []
if VERDICT == "null":
    if Fraction(1, 20) < FAIL15 <= Fraction(1, 10):
        NULL_AXES.append("band-miss: FAIL(15) in (1/20, 1/10]")
    if FAIL15 <= Fraction(1, 20) and FAIL15 > MIN_FAIL + Fraction(1, 100):
        NULL_AXES.append("wrong-center: a grid F beats FAIL(15) by more than 1/100")
    if FAIL15 <= Fraction(1, 20) and FAIL15 <= MIN_FAIL + Fraction(1, 100) and not STAB_OK:
        NULL_AXES.append("stability non-reproduction")
    if STRADDLE_WORLDS:
        NULL_AXES.append("sensitivity straddle: %s" % ",".join(STRADDLE_WORLDS))

# per-rule evaluation record, registered order
RULES = [
    {"rule": "REJECT (checked FIRST): FAIL(15) > 1/10",
     "fired": bool(FAIL15 > REJECT_BAND)},
    {"rule": "INVALID gate: zero-noise identity fails in either arm, OR a monotonicity theorem fails, OR Arm B breaches the agreement gate on any cell",
     "fired": bool(not GATES_OK)},
    {"rule": "APPROVE: FAIL(15) <= 1/20 AND FAIL(15) <= min_F FAIL(F) + 1/100 AND the seed-20261336 stability leg reproduces the ruling",
     "fired": bool(FAIL15 <= APPROVE_BAND and FAIL15 <= MIN_FAIL + WC_BAND and STAB_OK)},
    {"rule": "NULL: anything else (axes: band-miss / wrong-center / stability non-reproduction / sensitivity straddle)",
     "fired": VERDICT == "null"},
]

# ------------------------------------- drafter reference comparison (reporting)
REF = FX["drafter_disclosed_reference"]
REF_MATCH = {("FAIL(%s)" % f): (ARM_A[int(f)]["FAIL"] == Fr(REF["FAIL"][f]))
             for f in sorted(REF["FAIL"], key=int)}
REF_MATCH["DROP(5)"] = ARM_A[5]["DROP"] == Fr(REF["splits"]["DROP_5"])
REF_MATCH["DROP(10)"] = ARM_A[10]["DROP"] == Fr(REF["splits"]["DROP_10"])
REF_MATCH["UNSEAT(10)"] = ARM_A[10]["UNSEAT"] == Fr(REF["splits"]["UNSEAT_10"])
REF_MATCH["DROP(15)"] = ARM_A[15]["DROP"] == Fr(REF["splits"]["DROP_15"])
REF_MATCH["UNSEAT(15)"] = ARM_A[15]["UNSEAT"] == Fr(REF["splits"]["UNSEAT_15"])


# --------------------------------------------------------------------- output
def frdict(fr):
    return {"num": fr.numerator, "den": fr.denominator, "float": float(fr)}


RESULTS = {
    "verdict": VERDICT,
    "null_axes": NULL_AXES,
    "rules_evaluated_in_registered_order": RULES,
    "arm_A": {
        "table": {str(f): {"DROP": frdict(ARM_A[f]["DROP"]),
                           "UNSEAT": frdict(ARM_A[f]["UNSEAT"]),
                           "FAIL": frdict(ARM_A[f]["FAIL"]),
                           "FAIL_glue": frdict(ARM_A[f]["UNSEAT"])}
                  for f in GRID},
        "FAIL_15": frdict(FAIL15),
        "min_FAIL": frdict(MIN_FAIL),
        "argmin_F": MIN_F_ARG,
        "margin_over_reject_band": frdict(FAIL15 - REJECT_BAND),
        "per_H_conditional_FAIL15": [{"H": H, "FAIL": frdict(fr)} for H, fr in PER_H],
        "zero_noise_identity": {str(f): {"PRESS": frdict(1 - ZERO_A[f]["FAIL"])}
                                for f in GRID},
    },
    "arm_B": {
        "N": N_MC,
        "seed": SEEDS["headline"],
        "agreement": AGREE,
        "all_cells_pass": bool(AGREE_ALL),
        "zero_noise_control": {"seed": SEEDS["zero_noise_control"], "N": N_CTRL,
                               "all_press_exactly": bool(ZERO_B_OK)},
        "rngs_constructed_in_order": list(_RNGS_CONSTRUCTED),
        "draw_sentinels": {"headline": 600000, "zero_noise_control": 60000,
                           "sensitivity": 600000, "stability": 60000},
    },
    "controls_gate": {"gates": GATES, "all_ok": bool(GATES_OK)},
    "stability": {
        "seed": SEEDS["stability"], "N": N_STAB,
        "FAIL15_hat": frdict(STAB_FAIL15),
        "min_FAIL_hat": frdict(STAB_MIN_FAIL),
        "class": STAB_1,
        "reproduces_ruling": bool(STAB_OK),
    },
    "sensitivity_worlds": SENS,
    "straddle_worlds": STRADDLE_WORLDS,
    "reporting_only": {
        "remedy_direction_flag": FX["reporting_only"]["remedy_direction_flag"]["finding"],
        "drafter_reference_match": {k: bool(v) for k, v in REF_MATCH.items()},
    },
    "self_checks": dict(_CHECKS),
    "environment": {"implementation": "CPython", "version_major_minor": "3.11"},
}

out_path = os.path.join(BASE, "results.json")
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(RESULTS, fh, sort_keys=True, indent=2)
    fh.write("\n")

print("VERDICT 060 — magnet press-fit band (INTAKE 049)")
print("Arm A (exact, decision) — DROP/UNSEAT/FAIL x F over the 9,471-cell lattice:")
for f in GRID:
    print("  F = %2d  DROP = %9s = %.6f   UNSEAT = %9s = %.6f   FAIL = %9s = %.6f%s"
          % (f, ARM_A[f]["DROP"], float(ARM_A[f]["DROP"]),
             ARM_A[f]["UNSEAT"], float(ARM_A[f]["UNSEAT"]),
             ARM_A[f]["FAIL"], float(ARM_A[f]["FAIL"]),
             "   <- shipped default" if f == F_DEFAULT else ""))
print("  FAIL(15) = %s = %.6f   min_F FAIL = %s = %.6f at F = %d"
      % (FAIL15, float(FAIL15), MIN_FAIL, float(MIN_FAIL), MIN_F_ARG))
print("  FAIL_glue(F) = UNSEAT(F) (reporting-only): "
      + "  ".join("F=%d %.6f" % (f, float(ARM_A[f]["UNSEAT"])) for f in GRID))
print("Per-H conditional FAIL(15 | H) (reporting-only):")
for H, fr in PER_H:
    print("  H = %2d  FAIL(15 | H) = %9s = %.6f" % (H, fr, float(fr)))
print("Controls gate (INVALID if any fails):")
for k in sorted(GATES):
    print("  %-45s %s" % (k, "PASS" if GATES[k] else "FAIL"))
print("Arm B headline (seed 20261333, N = 200,000, common random numbers):")
for row in AGREE:
    print("  F = %2d  FAIL_hat = %.6f  exact = %.6f  |dev| = %.6f  (1/100 abs %s, 4se = %.6f %s)  %s"
          % (row["F"], row["FAIL_hat_float"], row["FAIL_exact_float"],
             row["abs_dev"], "ok" if row["within_1_100"] else "BREACH",
             row["tol_4se"], "ok" if row["within_4se"] else "BREACH",
             "PASS" if row["pass"] else "FAIL"))
print("Zero-noise identity (seed 20261334): Arm A exact-1 %s, Arm B all-PRESS %s"
      % ("PASS" if ZERO_A_OK else "FAIL", "PASS" if ZERO_B_OK else "FAIL"))
print("Sensitivity worlds (seed 20261335, N = 20,000 each, reporting-only):")
for w in SENS:
    print("  %-13s FAIL(15) = %9s = %.6f  [reject-edge: %-12s approve-edge: %-12s straddle: %-5s]  mc %.6f %s"
          % (w["world"], "%d/%d" % (w["FAIL15"]["num"], w["FAIL15"]["den"]),
             w["FAIL15_float"], w["side_reject_edge"], w["side_approve_edge"],
             w["straddle_vs_headline"], w["mc_FAIL15_hat_float"],
             "confirmed" if w["mc_confirms_all_cells"] else "UNCONFIRMED"))
print("Stability (seed 20261336, N = 20,000): FAIL15_hat = %s = %.6f, class %s -> %s"
      % (STAB_FAIL15, float(STAB_FAIL15), STAB_1,
         "REPRODUCES" if STAB_OK else "DOES-NOT-REPRODUCE"))
print("Rules (registered order):")
for r in RULES:
    print("  %-9s %s" % ("FIRED" if r["fired"] else "no-fire", r["rule"]))
if NULL_AXES:
    print("NULL axes: %s" % "; ".join(NULL_AXES))
print("Remedy-direction flag (reporting-only, routes lane-side): both shipped remedy "
      "texts point the magnet_fit dial the wrong way vs the line-83 geometry "
      "(pocket_d = magnet_d - magnet_fit: RAISING magnet_fit TIGHTENS the pocket).")
print("Drafter reference match (reporting-only): %s"
      % json.dumps({k: bool(v) for k, v in REF_MATCH.items()}, sort_keys=True))
print("VERDICT: %s" % VERDICT)
print("SELF-CHECKS: %d passed, %d failed" % (_CHECKS["passed"], _CHECKS["failed"]))
