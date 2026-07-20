#!/usr/bin/env python3
"""PROPOSAL 223 / VERDICT 236 (+13 offset) — grim-trigger folk-theorem threshold.

HEAD: In the infinitely-repeated symmetric Prisoner's Dilemma with stage payoffs
T > R > P > S (Temptation, Reward, Punishment, Sucker), the grim-trigger strategy
(cooperate until any defection, then defect forever) sustains mutual cooperation
as a subgame-perfect equilibrium if and only if the discount factor delta meets
the EXACT threshold

    delta* = (T - R) / (T - P).

Derivation (one-shot-deviation principle): cooperating forever is worth
V_C(delta) = R/(1-delta); the best one-shot deviation is worth
V_D(delta) = T + delta*P/(1-delta) (defect once, then grim punishment P forever).
Indifference V_C(delta*) = V_D(delta*) reduces to
    R - T + delta*(T - P) = 0  <=>  delta* = (T - R)/(T - P),
so at delta = delta* the incentive gap V_C - V_D is EXACTLY zero.

Monte-Carlo (continuation-probability) reading: with per-round continuation
probability delta the random horizon H >= 1 is geometric, E[H] = 1/(1-delta).
Define the per-episode statistic
    D_i = (R - P)*H_i - (T - P),
so E[D_i] = (R - P)/(1 - delta) - (T - P), which equals 0 EXACTLY at delta = delta*
because 1 - delta* = (R - P)/(T - P). H is drawn by
    h = 1; while rng.random() < p: h += 1          (p = float(delta))
giving P(H = k) = (1 - p) * p**(k - 1).

Gate battery (each direction stated):
  G1 EXACT indifference (Fraction, equality): headline (5,3,1,0) has
     delta* == Fraction(1,2) AND V_C(delta*) - V_D(delta*) == Fraction(0). No float.
  G2 EXACT grid (Fraction, robustness): for EVERY grid tuple delta* ==
     Fraction(T-R, T-P) with 0 < delta* < 1 AND V_C(delta*) - V_D(delta*) == 0.
  G3 MC agreement (|z| < Z_GATE PASS): N_MC draws of D_i at headline delta*=0.5;
     z = mean*sqrt(N)/std agrees with the E[D]=0 null within Z_GATE sigma.
  G4 MC grid (robustness, |z| < Z_GATE PASS): for each grid tuple, N_MC draws of
     D_i at ITS delta*; PASS iff every tuple's |z| < Z_GATE (record max|z|).
  G5 FALSIFIABILITY — wrong formula REJECTED (|z| > 6 PASS): the naive
     delta_wrong = (T-R)/(T-S) (Sucker S instead of Punishment P) is 2/5 = 0.4 at
     headline, where theory gives E[D] = -2/3 != 0; the sample rejects it at
     large z (opposite direction to G3/G4).
  G6 FALSIFIABILITY — below-threshold REJECTED (z < -6 PASS): at delta_below =
     delta*/2 = 0.25 the deviation is strictly profitable, theory E[D] = -4/3 < 0,
     so "cooperation holds for all delta > 0" is rejected with z_below < -6.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. build_results() is a
pure function of SEED and the fixed parameters; the results dict embeds no digest
of itself. main() runs it twice, asserts the canonical JSON forms are byte-
identical, then prints results_sha256 over the compact-canonical form. A separate
re-invocation must reproduce the identical 64-hex digest. Nothing is written to
disk. All EXACT work (G1/G2 and the theoretical E[D] values) uses
fractions.Fraction; the ONE random.Random(SEED) is drawn sequentially across the
Monte-Carlo gates (G3, then G4 per grid tuple, then G5, then G6) so the stream
order is fixed and deterministic.
"""

import hashlib
import json
import math
import random
import sys
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0
N_MC = 200_000

# grid tuples (T, R, P, S); each chosen so delta* is a clean power-of-two-
# denominator float -> no float bias in the geometric horizon sampler.
HEADLINE = (5, 3, 1, 0)          # delta* = 1/2
GRID = [
    (5, 3, 1, 0),                # delta* = 1/2  (headline)
    (5, 4, 1, 0),                # delta* = 1/4
    (5, 2, 1, 0),                # delta* = 3/4
    (9, 8, 1, 0),                # delta* = 1/8
]


def r6(x):
    return round(float(x), 6)


def frac_str(f):
    return f"{f.numerator}/{f.denominator}"


def delta_star(T, R, P):
    """Exact grim-trigger threshold delta* = (T - R)/(T - P)."""
    return Fraction(T - R, T - P)


def incentive_gap(T, R, P, delta):
    """Exact V_C(delta) - V_D(delta) with V_C = R/(1-delta),
    V_D = T + delta*P/(1-delta). delta is a Fraction => result is a Fraction."""
    v_c = Fraction(R) / (1 - delta)
    v_d = Fraction(T) + delta * Fraction(P) / (1 - delta)
    return v_c - v_d


def theoretical_ED(T, R, P, delta):
    """Exact E[D] = (R - P)/(1 - delta) - (T - P) for a Fraction delta."""
    return Fraction(R - P) / (1 - delta) - Fraction(T - P)


def mc_D_stats(T, R, P, delta_float, n, rng):
    """Draw n episodes of D_i = (R-P)*H_i - (T-P) with H_i geometric at
    continuation probability delta_float, consuming the shared rng in order.
    Return (mean, std, z) with z = mean*sqrt(n)/std (population std)."""
    p = float(delta_float)
    rp = R - P
    tp = T - P
    total = 0.0
    total_sq = 0.0
    for _ in range(n):
        h = 1
        while rng.random() < p:
            h += 1
        d = rp * h - tp
        total += d
        total_sq += d * d
    mean = total / n
    var = total_sq / n - mean * mean
    std = math.sqrt(var) if var > 0.0 else 0.0
    z = mean * math.sqrt(n) / std if std > 0.0 else 0.0
    return mean, std, z


def build_results():
    rng = random.Random(SEED)

    results = {
        "proposal": 223,
        "verdict": 236,
        "slot": "grim-trigger folk-theorem threshold (P223 -> V236, +13 offset)",
        "seed": SEED,
        "z_gate": Z_GATE,
        "n_mc": N_MC,
        "grid": [list(t) for t in GRID],
    }

    # --- G1 EXACT indifference: headline delta* == 1/2 AND gap == 0 -----------
    Th, Rh, Ph, Sh = HEADLINE
    d_head = delta_star(Th, Rh, Ph)
    gap_head = incentive_gap(Th, Rh, Ph, d_head)
    g1_pass = (d_head == Fraction(1, 2)) and (gap_head == Fraction(0))
    results["G1_exact_indifference"] = {
        "payoff": list(HEADLINE),
        "delta_star": frac_str(d_head),
        "delta_star_expected": frac_str(Fraction(1, 2)),
        "incentive_gap": frac_str(gap_head),
        "pass": g1_pass,
    }

    # --- G2 EXACT grid: delta* = Fraction(T-R,T-P), 0<delta*<1, gap == 0 ------
    per_tuple = {}
    g2_pass = True
    for (T, R, P, S) in GRID:
        d = delta_star(T, R, P)
        gap = incentive_gap(T, R, P, d)
        ok = (d == Fraction(T - R, T - P)) and (Fraction(0) < d < Fraction(1)) and (gap == Fraction(0))
        per_tuple[str((T, R, P, S))] = {
            "delta_star": frac_str(d),
            "in_open_unit": bool(Fraction(0) < d < Fraction(1)),
            "incentive_gap": frac_str(gap),
            "ok": ok,
        }
        g2_pass = g2_pass and ok
    results["G2_exact_grid"] = {
        "per_tuple": per_tuple,
        "pass": g2_pass,
    }

    # --- G3 MC agreement at headline delta* = 0.5, |z| < Z_GATE ---------------
    d_head_f = float(d_head)
    mean3, std3, z3 = mc_D_stats(Th, Rh, Ph, d_head_f, N_MC, rng)
    g3_pass = abs(z3) < Z_GATE
    results["G3_mc_agreement"] = {
        "payoff": list(HEADLINE),
        "delta": r6(d_head_f),
        "n": N_MC,
        "mean": r6(mean3),
        "std": r6(std3),
        "z": r6(z3),
        "pass": g3_pass,
    }

    # --- G4 MC grid: each tuple at its delta*, every |z| < Z_GATE -------------
    g4_tuple = {}
    max_abs_z = 0.0
    g4_pass = True
    for (T, R, P, S) in GRID:
        d = delta_star(T, R, P)
        mean_i, std_i, z_i = mc_D_stats(T, R, P, float(d), N_MC, rng)
        g4_tuple[str((T, R, P, S))] = {
            "delta_star": r6(float(d)),
            "z": r6(z_i),
            "pass": abs(z_i) < Z_GATE,
        }
        max_abs_z = max(max_abs_z, abs(z_i))
        g4_pass = g4_pass and (abs(z_i) < Z_GATE)
    results["G4_mc_grid"] = {
        "n": N_MC,
        "per_tuple": g4_tuple,
        "max_abs_z": r6(max_abs_z),
        "pass": g4_pass,
    }

    # --- G5 FALSIFIABILITY: wrong formula (T-R)/(T-S) REJECTED at |z| > 6 -----
    d_wrong = Fraction(Th - Rh, Th - Sh)          # 2/5 for headline
    ED_wrong = theoretical_ED(Th, Rh, Ph, d_wrong)  # -2/3 exactly
    mean5, std5, z5 = mc_D_stats(Th, Rh, Ph, float(d_wrong), N_MC, rng)
    g5_pass = abs(z5) > 6.0
    results["G5_falsify_wrong_formula"] = {
        "wrong_rule": "delta_wrong = (T-R)/(T-S) uses Sucker S instead of Punishment P",
        "delta_wrong": r6(float(d_wrong)),
        "delta_wrong_exact": frac_str(d_wrong),
        "theoretical_ED_exact": frac_str(ED_wrong),
        "z_wrong": r6(z5),
        "rejected": g5_pass,
        "pass": g5_pass,
    }

    # --- G6 FALSIFIABILITY: below threshold (delta*/2) REJECTED at z < -6 -----
    d_below = d_head / 2                            # 1/4
    ED_below = theoretical_ED(Th, Rh, Ph, d_below)   # -4/3 exactly
    mean6, std6, z6 = mc_D_stats(Th, Rh, Ph, float(d_below), N_MC, rng)
    g6_pass = z6 < -6.0
    results["G6_falsify_below_threshold"] = {
        "claim_rejected": "cooperation holds for all delta > 0 (deviation strictly profitable below delta*)",
        "delta_below": r6(float(d_below)),
        "delta_below_exact": frac_str(d_below),
        "theoretical_ED_exact": frac_str(ED_below),
        "z_below": r6(z6),
        "rejected": g6_pass,
        "pass": g6_pass,
    }

    gates = {
        "G1": results["G1_exact_indifference"]["pass"],
        "G2": results["G2_exact_grid"]["pass"],
        "G3": results["G3_mc_agreement"]["pass"],
        "G4": results["G4_mc_grid"]["pass"],
        "G5": results["G5_falsify_wrong_formula"]["pass"],
        "G6": results["G6_falsify_below_threshold"]["pass"],
    }
    order = ["G1", "G2", "G3", "G4", "G5", "G6"]
    first_failing = next((k for k in order if not gates[k]), None)
    results["gates"] = gates
    results["first_failing_gate"] = first_failing
    results["all_pass"] = all(gates[k] for k in order)
    return results


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def main():
    r1 = build_results()
    r2 = build_results()
    c1 = canonical(r1)
    c2 = canonical(r2)
    if c1 != c2:
        sys.stderr.write("NON-DETERMINISTIC: in-process double-run diverged\n")
        sys.exit(3)
    digest = hashlib.sha256(c1.encode("utf-8")).hexdigest()

    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    order = ["G1", "G2", "G3", "G4", "G5", "G6"]
    for k in order:
        print(f"{k}: {'PASS' if r1['gates'][k] else 'FAIL'}")
    print()
    print(f"all_pass: {r1['all_pass']}")
    print(f"results_sha256: {digest}")
    sys.exit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
