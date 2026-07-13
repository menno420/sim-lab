#!/usr/bin/env python3
"""VERDICT 059 — Parrondo's paradox at a conservative discrete pin (idea-engine PROPOSAL 048).

Arm A (DECISION, seedless, exact): fractions.Fraction stationary solve of the
capital-mod-3 reduced Markov chain; long-run drifts D_A, D_B, D_mix as exact
rationals; the ruling is a comparison of D_mix against the pre-registered
bands, evaluated in the registered order (REJECT first / INVALID gate /
APPROVE / NULL) by two independently-written evaluators.

Arm B (VALIDATION, seeded MC): direct capital simulation, N = 200,000 per leg,
the four pre-registered seeds ONLY (20261329 mixed headline / 20261330 pure-A
control / 20261331 pure-B control / 20261332 stability). Reporting/validation
only; never overrides Arm A.

Reporting-only side pins: stationary residue distributions pi_B / pi_mix, the
critical-EPS sweep, the periodic [A,A,B,B] product-chain comparator.

Hermetic: reads only its own fixtures.json. Stdlib only. No wall-clock in any
output. Byte-identical stdout + results.json across process runs.

Run: python3 sims/verdict-059-parrondo-lattice/parrondo_sim.py
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


def F(d):
    return Fraction(d["num"], d["den"])


EPS = F(FX["model"]["EPS"])
M = FX["model"]["M"]
BASE_A = F(FX["model"]["coin_triple_base"]["game_A"])
BASE_B_BAD = F(FX["model"]["coin_triple_base"]["game_B_bad"])
BASE_B_GOOD = F(FX["model"]["coin_triple_base"]["game_B_good"])
A_COIN = BASE_A - EPS
B0_COIN = BASE_B_BAD - EPS
B1_COIN = BASE_B_GOOD - EPS
APPROVE_BAND = F(FX["decision_rule"]["approve_band"])
N_MC = FX["arm_B"]["N"]
SEEDS = {
    "mixed_headline": 20261329,
    "pure_A_control": 20261330,
    "pure_B_control": 20261331,
    "stability": 20261332,
}
check(sorted(str(s) for s in SEEDS.values()) == sorted(FX["seeds"].keys() - {"policy"}),
      "the four registered seeds and no others")
check(M == 3, "M = 3 pinned")

# derived constants re-derived from the pinned base, checked against the
# fixture's own derived block (a transcription gate, not a trust in it)
check(A_COIN == F(FX["model"]["derived"]["a"]) == Fraction(49, 100), "a = 1/2 - EPS = 49/100")
check(B0_COIN == F(FX["model"]["derived"]["b0"]) == Fraction(9, 100), "b0 = 1/10 - EPS = 9/100")
check(B1_COIN == F(FX["model"]["derived"]["b1"]) == Fraction(37, 50), "b1 = 3/4 - EPS = 37/50")

W_MIX = [(A_COIN + b) / 2 for b in (B0_COIN, B1_COIN, B1_COIN)]
check(W_MIX[0] == F(FX["model"]["derived_w"]["w0"]) == Fraction(29, 100), "w0 = 29/100")
check(W_MIX[1] == F(FX["model"]["derived_w"]["w1"]) == Fraction(123, 200), "w1 = 123/200")
check(W_MIX[2] == F(FX["model"]["derived_w"]["w2"]) == Fraction(123, 200), "w2 = 123/200")
for w in W_MIX:
    check(0 < w < 1, "w_s a probability")


# --------------------------------------------------------- exact linear algebra
def stationary(P):
    """Exact stationary law of an irreducible row-stochastic matrix (Fractions)."""
    n = len(P)
    for i in range(n):
        check(sum(P[i]) == 1, "row %d stochastic" % i)
    A = []
    rhs = []
    for j in range(n - 1):  # balance equations, last one replaced by normalization
        A.append([P[i][j] - (Fraction(1) if i == j else Fraction(0)) for i in range(n)])
        rhs.append(Fraction(0))
    A.append([Fraction(1)] * n)
    rhs.append(Fraction(1))
    for col in range(n):  # Gauss-Jordan, exact
        piv = None
        for r in range(col, n):
            if A[r][col] != 0:
                piv = r
                break
        check(piv is not None, "pivot exists at column %d" % col)
        A[col], A[piv] = A[piv], A[col]
        rhs[col], rhs[piv] = rhs[piv], rhs[col]
        inv = Fraction(1) / A[col][col]
        A[col] = [x * inv for x in A[col]]
        rhs[col] = rhs[col] * inv
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [A[r][k] - f * A[col][k] for k in range(n)]
                rhs[r] = rhs[r] - f * rhs[col]
    pi = rhs
    check(sum(pi) == 1, "pi sums to 1 exactly")
    for j in range(n):
        check(sum(pi[i] * P[i][j] for i in range(n)) == pi[j], "pi P = pi at state %d" % j)
        check(0 < pi[j] < 1, "pi_%d in (0,1)" % j)
    return pi


def residue_chain(w):
    """3-residue chain: s -> (s+1) mod 3 w.p. w_s, (s-1) mod 3 w.p. 1 - w_s."""
    P = [[Fraction(0)] * 3 for _ in range(3)]
    for s in range(3):
        P[s][(s + 1) % 3] += w[s]
        P[s][(s - 1) % 3] += 1 - w[s]
    return P


def chain_drift(w):
    pi = stationary(residue_chain(w))
    return sum(pi[s] * (2 * w[s] - 1) for s in range(3)), pi


# ------------------------------------------------------------- Arm A (DECISION)
def arm_A(a_coin, b0_coin, b1_coin):
    w_A = [a_coin, a_coin, a_coin]
    w_B = [b0_coin, b1_coin, b1_coin]
    w_mix = [(a_coin + b) / 2 for b in (b0_coin, b1_coin, b1_coin)]
    D_A, pi_A = chain_drift(w_A)
    D_B, pi_B = chain_drift(w_B)
    D_mix, pi_mix = chain_drift(w_mix)
    return {"D_A": D_A, "D_B": D_B, "D_mix": D_mix,
            "pi_A": pi_A, "pi_B": pi_B, "pi_mix": pi_mix}


ARM_A = arm_A(A_COIN, B0_COIN, B1_COIN)
ARM_A_RERUN = arm_A(A_COIN, B0_COIN, B1_COIN)  # in-process byte-identity twin
check(ARM_A == ARM_A_RERUN, "two Arm-A computations identical rationals")
check(ARM_A["D_A"] == 2 * A_COIN - 1 == Fraction(-1, 50),
      "capital-independent identity: D_A = 2a - 1 = -1/50 exact")
check(ARM_A["pi_A"] == [Fraction(1, 3)] * 3, "pure-A stationary law uniform (doubly stochastic)")

# ---------------------------------------------------- Arm B (seeded VALIDATION)
_RNGS_CONSTRUCTED = []


class CountingRandom(object):
    def __init__(self, seed):
        _RNGS_CONSTRUCTED.append(seed)
        self._r = random.Random(seed)
        self.draws = 0

    def random(self):
        self.draws += 1
        return self._r.random()


def mc_leg(seed, mode, n_steps):
    """Direct capital simulation. Draw order pinned: mixed = (policy coin, win
    coin) per step; pure = (win coin) per step. Returns (final capital, draws)."""
    a_f = float(A_COIN)
    b0_f = float(B0_COIN)
    b1_f = float(B1_COIN)
    rng = CountingRandom(seed)
    capital = 0
    for _ in range(n_steps):
        if mode == "mixed":
            play_a = rng.random() < 0.5
        elif mode == "A":
            play_a = True
        else:
            play_a = False
        if play_a:
            p = a_f
        else:
            p = b0_f if capital % 3 == 0 else b1_f
        capital += 1 if rng.random() < p else -1
    return capital, rng.draws


def leg_report(name, seed, mode, exact_drift):
    capital, draws = mc_leg(seed, mode, N_MC)
    want = FX["arm_B"]["draw_sentinels"]["mixed_leg" if mode == "mixed" else "pure_leg"]
    check(draws == want, "draw sentinel %s: %d" % (name, want))
    d_hat = Fraction(capital, N_MC)
    d_hat_f = capital / N_MC
    se = math.sqrt((1.0 - d_hat_f * d_hat_f) / N_MC)
    dev = abs(d_hat_f - float(exact_drift))
    within = dev <= 4.0 * se
    return {"name": name, "seed": seed, "mode": mode, "N": N_MC,
            "final_capital": capital, "draws": draws,
            "empirical_drift": {"num": d_hat.numerator, "den": d_hat.denominator},
            "empirical_drift_float": d_hat_f,
            "exact_drift_float": float(exact_drift),
            "se": se, "abs_dev": dev, "tol_4se": 4.0 * se,
            "within_4se": bool(within)}


LEGS = [
    leg_report("mixed_headline", SEEDS["mixed_headline"], "mixed", ARM_A["D_mix"]),
    leg_report("pure_A_control", SEEDS["pure_A_control"], "A", ARM_A["D_A"]),
    leg_report("pure_B_control", SEEDS["pure_B_control"], "B", ARM_A["D_B"]),
    leg_report("stability", SEEDS["stability"], "mixed", ARM_A["D_mix"]),
]
check(_RNGS_CONSTRUCTED == [SEEDS["mixed_headline"], SEEDS["pure_A_control"],
                            SEEDS["pure_B_control"], SEEDS["stability"]],
      "exactly four RNGs constructed, registered seeds, pinned order")

STAB_CAP = LEGS[3]["final_capital"]
# stability PASS (registered): sign and the >= 1/1000 margin both reproduce
STAB_SIGN_OK = STAB_CAP > 0
STAB_MARGIN_OK = Fraction(STAB_CAP, N_MC) >= APPROVE_BAND
STAB_OK = STAB_SIGN_OK and STAB_MARGIN_OK
ARM_B_ALL_WITHIN = all(leg["within_4se"] for leg in LEGS)


# ------------------------------------------------- twin decision evaluators
def evaluate_fraction(d_mix, d_a, d_b, band, stab_ok, armb_ok):
    """Evaluator 1: Fraction comparisons, registered order."""
    if d_mix <= 0:
        return "reject"
    if d_a >= 0 or d_b >= 0:
        return "invalid"
    if d_mix >= band and stab_ok and armb_ok:
        return "approve"
    return "null"


def evaluate_integer(d_mix, d_a, d_b, band, stab_ok, armb_ok):
    """Evaluator 2: pure-integer cross-multiplication (Fraction normalizes
    denominators positive, so sign tests are numerator tests); conditions
    tested in the same registered order but via a different arithmetic path."""
    mn, md = d_mix.numerator, d_mix.denominator
    an = d_a.numerator
    bn = d_b.numerator
    if mn <= 0:
        return "reject"
    if an >= 0 or bn >= 0:
        return "invalid"
    # d_mix >= band  <=>  mn * band.den >= band.num * md  (all positive here)
    if mn * band.denominator >= band.numerator * md and stab_ok and armb_ok:
        return "approve"
    return "null"


VERDICT_1 = evaluate_fraction(ARM_A["D_mix"], ARM_A["D_A"], ARM_A["D_B"],
                              APPROVE_BAND, STAB_OK, ARM_B_ALL_WITHIN)
VERDICT_2 = evaluate_integer(ARM_A["D_mix"], ARM_A["D_A"], ARM_A["D_B"],
                             APPROVE_BAND, STAB_OK, ARM_B_ALL_WITHIN)
check(VERDICT_1 == VERDICT_2, "twin decision evaluators agree")
VERDICT = VERDICT_1

# per-rule evaluation record, registered order
RULES = [
    {"rule": "REJECT (checked FIRST): D_mix <= 0",
     "fired": bool(ARM_A["D_mix"] <= 0)},
    {"rule": "INVALID gate: D_A >= 0 or D_B >= 0 (a component game not individually losing)",
     "fired": bool(ARM_A["D_A"] >= 0 or ARM_A["D_B"] >= 0)},
    {"rule": "APPROVE: D_mix >= 1/1000 AND seed-20261332 stability reproduces sign and margin AND all Arm-B legs within 4*se",
     "fired": bool(ARM_A["D_mix"] >= APPROVE_BAND and STAB_OK and ARM_B_ALL_WITHIN)},
    {"rule": "NULL: 0 < D_mix < 1/1000 or a validity conjunct fails",
     "fired": VERDICT == "null"},
]

# ------------------------------------------- reporting-only: critical-EPS sweep
EPS_SWEEP = []
for eps_d in FX["reporting_only"]["critical_EPS_sweep"]:
    eps = F(eps_d)
    a_e = BASE_A - eps
    b0_e = BASE_B_BAD - eps
    b1_e = BASE_B_GOOD - eps
    res = arm_A(a_e, b0_e, b1_e)
    EPS_SWEEP.append({
        "EPS": {"num": eps.numerator, "den": eps.denominator},
        "EPS_float": float(eps),
        "D_mix": {"num": res["D_mix"].numerator, "den": res["D_mix"].denominator},
        "D_mix_float": float(res["D_mix"]),
        "sign_D_mix": "positive" if res["D_mix"] > 0 else ("zero" if res["D_mix"] == 0 else "negative"),
        "D_A_float": float(res["D_A"]),
        "D_B_float": float(res["D_B"]),
    })
check(EPS_SWEEP[0]["D_mix"] == {"num": ARM_A["D_mix"].numerator,
                                "den": ARM_A["D_mix"].denominator},
      "sweep's EPS = 1/100 cell reproduces the headline D_mix")

# ------------------------------- reporting-only: periodic [A,A,B,B] comparator
PATTERN = FX["reporting_only"]["periodic_comparator"]["pattern"]
check(PATTERN == ["A", "A", "B", "B"], "periodic pattern pinned [A,A,B,B]")
NP = len(PATTERN)


def periodic_drift(a_coin, b0_coin, b1_coin, pattern):
    np_, ns = len(pattern), 3
    n = np_ * ns

    def idx(p, s):
        return p * ns + s

    P = [[Fraction(0)] * n for _ in range(n)]
    wvec = [Fraction(0)] * n
    for p in range(np_):
        for s in range(ns):
            if pattern[p] == "A":
                w = a_coin
            else:
                w = b0_coin if s == 0 else b1_coin
            wvec[idx(p, s)] = w
            P[idx(p, s)][idx((p + 1) % np_, (s + 1) % ns)] += w
            P[idx(p, s)][idx((p + 1) % np_, (s - 1) % ns)] += 1 - w
    pi = stationary(P)
    return sum(pi[i] * (2 * wvec[i] - 1) for i in range(n))


D_PERIODIC = periodic_drift(A_COIN, B0_COIN, B1_COIN, PATTERN)

# ------------------------------------- drafter reference comparison (reporting)
REF = FX["drafter_disclosed_reference"]
REF_MATCH = {
    "D_A": ARM_A["D_A"] == F(REF["D_A"]),
    "D_B": ARM_A["D_B"] == F(REF["D_B"]),
    "D_mix": ARM_A["D_mix"] == F(REF["D_mix"]),
    "pi_B": ARM_A["pi_B"] == [F(x) for x in REF["pi_B"]],
    "pi_mix": ARM_A["pi_mix"] == [F(x) for x in REF["pi_mix"]],
}


# --------------------------------------------------------------------- output
def frdict(fr):
    return {"num": fr.numerator, "den": fr.denominator, "float": float(fr)}


RESULTS = {
    "verdict": VERDICT,
    "rules_evaluated_in_registered_order": RULES,
    "arm_A": {
        "D_A": frdict(ARM_A["D_A"]),
        "D_B": frdict(ARM_A["D_B"]),
        "D_mix": frdict(ARM_A["D_mix"]),
        "pi_A": [frdict(x) for x in ARM_A["pi_A"]],
        "pi_B": [frdict(x) for x in ARM_A["pi_B"]],
        "pi_mix": [frdict(x) for x in ARM_A["pi_mix"]],
        "isolated_loss_gates": {"D_A_negative": bool(ARM_A["D_A"] < 0),
                                "D_B_negative": bool(ARM_A["D_B"] < 0)},
        "approve_band": frdict(APPROVE_BAND),
        "margin_over_band": frdict(ARM_A["D_mix"] - APPROVE_BAND),
    },
    "arm_B": {
        "legs": LEGS,
        "stability": {"sign_reproduced": bool(STAB_SIGN_OK),
                      "margin_reproduced": bool(STAB_MARGIN_OK),
                      "pass": bool(STAB_OK)},
        "all_legs_within_4se": bool(ARM_B_ALL_WITHIN),
        "rngs_constructed_in_order": list(_RNGS_CONSTRUCTED),
    },
    "reporting_only": {
        "critical_EPS_sweep": EPS_SWEEP,
        "periodic_AABB_comparator": {
            "pattern": PATTERN,
            "drift": frdict(D_PERIODIC),
            "sign": "positive" if D_PERIODIC > 0 else ("zero" if D_PERIODIC == 0 else "negative"),
        },
        "drafter_reference_match": {k: bool(v) for k, v in REF_MATCH.items()},
    },
    "self_checks": dict(_CHECKS),
    "environment": {"implementation": "CPython", "version_major_minor": "3.11"},
}

out_path = os.path.join(BASE, "results.json")
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(RESULTS, fh, sort_keys=True, indent=2)
    fh.write("\n")

print("VERDICT 059 — Parrondo lattice pin (INTAKE 048)")
print("Arm A (exact, decision):")
print("  D_A   = %s = %.6f" % (ARM_A["D_A"], float(ARM_A["D_A"])))
print("  D_B   = %s = %.6f" % (ARM_A["D_B"], float(ARM_A["D_B"])))
print("  D_mix = %s = %.6f" % (ARM_A["D_mix"], float(ARM_A["D_mix"])))
print("  pi_B   = %s" % (ARM_A["pi_B"],))
print("  pi_mix = %s" % (ARM_A["pi_mix"],))
for leg in LEGS:
    print("Arm B leg %-14s seed %d  D_hat = %+.6f  exact %+.6f  |dev| = %.6f  4se = %.6f  %s"
          % (leg["name"], leg["seed"], leg["empirical_drift_float"],
             leg["exact_drift_float"], leg["abs_dev"], leg["tol_4se"],
             "PASS" if leg["within_4se"] else "FAIL"))
print("Stability (seed 20261332): sign %s, margin >= 1/1000 %s -> %s"
      % (STAB_SIGN_OK, STAB_MARGIN_OK, "PASS" if STAB_OK else "FAIL"))
print("Rules (registered order):")
for r in RULES:
    print("  %-9s %s" % ("FIRED" if r["fired"] else "no-fire", r["rule"]))
print("Critical-EPS sweep (reporting-only):")
for cell in EPS_SWEEP:
    print("  EPS = %d/%d  D_mix = %d/%d = %+.6f  (%s)"
          % (cell["EPS"]["num"], cell["EPS"]["den"], cell["D_mix"]["num"],
             cell["D_mix"]["den"], cell["D_mix_float"], cell["sign_D_mix"]))
print("Periodic [A,A,B,B] comparator (reporting-only): D = %s = %+.6f (%s)"
      % (D_PERIODIC, float(D_PERIODIC),
         RESULTS["reporting_only"]["periodic_AABB_comparator"]["sign"]))
print("Drafter reference match (reporting-only): %s"
      % json.dumps({k: bool(v) for k, v in REF_MATCH.items()}, sort_keys=True))
print("VERDICT: %s" % VERDICT)
print("SELF-CHECKS: %d passed, %d failed" % (_CHECKS["passed"], _CHECKS["failed"]))
