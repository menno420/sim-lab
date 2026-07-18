#!/usr/bin/env python3
"""PROPOSAL 135 — balance-triangle pick-rate inversion (round-31 GAME slot).

Phenomenon: a "balance triangle" — a weighted rock-paper-scissors metagame of
three units R, P, S in a beat-cycle R>S>P>R — is a skew-symmetric zero-sum game.
Its unique mixed-strategy Nash equilibrium plays each unit in proportion to the
winning margin of the matchup it is NOT part of, so a buff to one unit's margin
can LOWER that unit's own equilibrium pick rate and RAISE its counter's, while
the game value stays 0. Folk belief (inverted here): "balance means equal pick
rates; buff a weak unit and it gets played more."

Model (skew-symmetric zero-sum, row payoff in expected match score on [-1,1]):
cycle R>S>P>R with winning margins
    a = margin(R beats S),  b = margin(S beats P),  c = margin(P beats R).
Payoff matrix M (row's expected score vs column), order (R, P, S):
    M[R] = [ 0, -c,  a]      # R loses to P by c, beats S by a
    M[P] = [ c,  0, -b]      # P beats R by c, loses to S by b
    M[S] = [-a,  b,  0]      # S loses to R by a, beats P by b
M is skew-symmetric (M = -M^T), so the value is 0 and the symmetric equilibrium
x* solves M x* = 0. Solving gives
    x*_R : x*_P : x*_S = b : a : c,
i.e. each unit's equilibrium pick rate is proportional to the margin of the
matchup it is NOT in. Buffing a (R crushes S harder) therefore raises x*_P
(P's share ∝ a) and can DROP x*_R (∝ b, unchanged) below its old level — the
pick-rate response flows AROUND the cycle, not to the buffed unit.

Pinned worlds:
  SKEWED (a=0.4, b=0.2, c=0.2):  x* = (0.25, 0.50, 0.25) — buffing R (a: 0.2->0.4)
     from the symmetric 1/3-each meta DROPS R to 0.25 and DOUBLES P to 0.50.
     Uniform play (1/3 each) is exploitable: best response R earns (a-c)/3.
  SYMMETRIC (a=b=c=0.2): x* = (1/3, 1/3, 1/3); uniform is the equilibrium and is
     exactly non-exploitable — the placebo.

Literature anchors: von Neumann (1928) minimax theorem; the value of a
skew-symmetric matrix game is 0 with a symmetric optimal strategy (Gale, Kuhn &
Tucker 1950); generalized / weighted rock-paper-scissors mixed equilibria
(https://en.wikipedia.org/wiki/Rock_paper_scissors). Nash (1951) existence.

Pre-registered gates (APPROVE iff ALL hold, in order G1 -> G2 -> G3):
  G1  EQUILIBRIUM : with the opponent fixed at the closed-form mix x*, each of
                    the row's three pure actions has Monte-Carlo mean payoff
                    within z < 3 sigma of 0 — x* makes the field indifferent,
                    confirming it solves the skew-symmetric game (value 0).
  G2  INVERSION   : in the SKEWED triangle, against the intuitive UNIFORM meta
                    the best pure response (R) has MC mean payoff > 0 with
                    z = mean/se >= 3 sigma AND matches the exact anchor (a-c)/3.
                    "Equal pick rates" is exploitable; balance needs pick rates
                    proportional to the inverse margins (b, a, c), so buffing a
                    raises x*_P, not x*_R — the folk reading is reversed.
  G3  PLACEBO     : in the SYMMETRIC triangle the exact exploitability of the
                    uniform meta is 0.0 for every action (max |(row vs uniform)|
                    == 0.0 exactly) AND the MC best-action payoff vs uniform is
                    within z < 3 sigma of 0 — the effect vanishes when the
                    margins are equal (caused by asymmetry, not by the sim).
"""

import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 200_000
SIGMA_GATE = 3.0

# order is (R, P, S) throughout
ACTIONS = ("R", "P", "S")

# SKEWED triangle: R buffed (a) above the symmetric baseline.
A_SKEW, B_SKEW, C_SKEW = 0.4, 0.2, 0.2
# SYMMETRIC triangle: the placebo (equal margins).
A_SYM, B_SYM, C_SYM = 0.2, 0.2, 0.2


def payoff_matrix(a, b, c):
    """Row's expected score vs column, order (R, P, S). Skew-symmetric."""
    return [
        [0.0, -c, a],   # R vs (R, P, S)
        [c, 0.0, -b],   # P vs (R, P, S)
        [-a, b, 0.0],   # S vs (R, P, S)
    ]


def equilibrium_mix(a, b, c):
    """Symmetric Nash mix of the skew-symmetric triangle: x_R:x_P:x_S = b:a:c."""
    total = a + b + c
    return [b / total, a / total, c / total]   # (R, P, S)


def _mc_payoff(row_action_idx, opp_mix, matrix, trials, rng):
    """MC mean/se of the row playing a fixed pure action vs a mixed opponent."""
    row = matrix[row_action_idx]
    # opponent's action-sampling thresholds (cumulative)
    c0 = opp_mix[0]
    c1 = opp_mix[0] + opp_mix[1]
    s = 0.0
    ss = 0.0
    for _ in range(trials):
        u = rng.random()
        j = 0 if u < c0 else (1 if u < c1 else 2)
        v = row[j]
        s += v
        ss += v * v
    mean = s / trials
    var = max(ss / trials - mean * mean, 0.0)
    se = math.sqrt(var / trials)
    return mean, se


def _z(mean, se, null=0.0):
    return (mean - null) / se if se > 0 else float("inf")


def _exact_vs_uniform(matrix):
    """Exact expected payoff of each pure row action vs the uniform (1/3) meta."""
    return [sum(matrix[i]) / 3.0 for i in range(3)]


def run():
    rng = random.Random(SEED)

    m_skew = payoff_matrix(A_SKEW, B_SKEW, C_SKEW)
    m_sym = payoff_matrix(A_SYM, B_SYM, C_SYM)
    x_star = equilibrium_mix(A_SKEW, B_SKEW, C_SKEW)      # (0.25, 0.5, 0.25)
    x_star_sym = equilibrium_mix(A_SYM, B_SYM, C_SYM)     # (1/3, 1/3, 1/3)
    uniform = [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]

    # --- G1: opponent fixed at x*, each pure action indifferent (mean payoff 0)
    g1_means = {}
    g1_z = {}
    for i, name in enumerate(ACTIONS):
        mean, se = _mc_payoff(i, x_star, m_skew, TRIALS, rng)
        g1_means[name] = mean
        g1_z[name] = _z(mean, se)
    g1_max_abs_z = max(abs(z) for z in g1_z.values())
    g1 = g1_max_abs_z < SIGMA_GATE

    # --- G2: SKEWED triangle, opponent uniform; best action R exploits it
    exact_vs_uniform_skew = _exact_vs_uniform(m_skew)     # [(a-c)/3, (c-b)/3, (b-a)/3]
    g2_anchor = (A_SKEW - C_SKEW) / 3.0                   # R's exact edge vs uniform
    mean_R, se_R = _mc_payoff(0, uniform, m_skew, TRIALS, rng)
    z_g2_exist = _z(mean_R, se_R)                         # vs 0
    z_g2_anchor = _z(mean_R, se_R, g2_anchor)             # match closed form
    g2 = (mean_R > 0.0) and (z_g2_exist >= SIGMA_GATE) and (abs(z_g2_anchor) < SIGMA_GATE)

    # --- G3: SYMMETRIC triangle placebo — uniform exactly non-exploitable
    exact_vs_uniform_sym = _exact_vs_uniform(m_sym)       # all exactly 0.0
    g3_max_abs_exact = max(abs(v) for v in exact_vs_uniform_sym)
    mean_R_sym, se_R_sym = _mc_payoff(0, uniform, m_sym, TRIALS, rng)
    z_g3 = _z(mean_R_sym, se_R_sym)
    g3 = (g3_max_abs_exact == 0.0) and (abs(z_g3) < SIGMA_GATE)

    all_pass = g1 and g2 and g3

    return {
        "proposal": 135,
        "seed": SEED,
        "trials": TRIALS,
        "sigma_gate": SIGMA_GATE,
        "skewed_margins": {"a_R_beats_S": A_SKEW, "b_S_beats_P": B_SKEW, "c_P_beats_R": C_SKEW},
        "symmetric_margins": {"a": A_SYM, "b": B_SYM, "c": C_SYM},
        "x_star_skewed": {"R": x_star[0], "P": x_star[1], "S": x_star[2]},
        "x_star_symmetric": {"R": x_star_sym[0], "P": x_star_sym[1], "S": x_star_sym[2]},
        "g1_indifference_mean_payoff": g1_means,
        "g1_z": g1_z,
        "g1_max_abs_z": g1_max_abs_z,
        "g1_equilibrium": g1,
        "g2_exact_vs_uniform_skewed": {ACTIONS[i]: exact_vs_uniform_skew[i] for i in range(3)},
        "g2_best_action": "R",
        "g2_anchor": g2_anchor,
        "g2_mc_payoff_R_vs_uniform": mean_R,
        "g2_z_exist": z_g2_exist,
        "g2_z_anchor": z_g2_anchor,
        "g2_inversion": g2,
        "g3_exact_vs_uniform_symmetric": {ACTIONS[i]: exact_vs_uniform_sym[i] for i in range(3)},
        "g3_max_abs_exact_exploit": g3_max_abs_exact,
        "g3_mc_payoff_R_vs_uniform_sym": mean_R_sym,
        "g3_z": z_g3,
        "g3_placebo": g3,
        "all_pass": all_pass,
    }


def main():
    results = run()
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    print(
        "G1 equilibrium  :",
        "PASS" if results["g1_equilibrium"] else "FAIL",
        f"(max|z|={results['g1_max_abs_z']:.3f})",
    )
    print(
        "G2 inversion    :",
        "PASS" if results["g2_inversion"] else "FAIL",
        f"(R vs uniform={results['g2_mc_payoff_R_vs_uniform']:+.5f}, "
        f"z_exist={results['g2_z_exist']:+.2f}, z_anchor={results['g2_z_anchor']:+.3f})",
    )
    print(
        "G3 placebo      :",
        "PASS" if results["g3_placebo"] else "FAIL",
        f"(max|exact|={results['g3_max_abs_exact_exploit']:.1e}, z={results['g3_z']:+.3f})",
    )
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
