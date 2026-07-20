#!/usr/bin/env python3
"""PROPOSAL 235 - The value of a 2x2 zero-sum game (von Neumann minimax).

Claim (exact, closed-form): For a 2x2 zero-sum game with row-maximiser payoff
matrix M = [[a, b], [c, d]] that has NO pure-strategy saddle point (pure
maximin < pure minimax, equivalently the optimal mixing weights lie strictly
in (0, 1)), the game value is the exact rational

        v = (a*d - b*c) / (a + d - b - c)

attained by the mixed strategies  row plays row0 with prob (d - c)/(a+d-b-c),
column plays col0 with prob (d - b)/(a+d-b-c). For the reference matrix
M = [[3, -1], [-2, 1]] the value is v = 1/7 with row = (3/7, 4/7),
column = (2/7, 5/7); the pure-strategy security level (maximin) is only -1,
strictly below v, so the naive "value == security level" rule is wrong.

SEED = 20260717. build_results() is a pure function of SEED and the module
constants (per-gate random.Random(SEED); no wall-clock / PID / unordered-set
iteration in the hashed payload), so an in-process double-run and a separate
re-invocation are byte-identical; results_sha256 is the sha256 of the
canonical results dict.

Four gates, each in its own direction:
  G1 EXACT      - closed-form v and optimal strategies match an independent
                  indifference-equation route as exact Fractions over a panel
                  of no-saddle rational games, and each game is confirmed to
                  have no pure saddle point (mix genuine).
  G2 MC AGREE   - both players sampling their optimal mixed strategy, the
                  Monte-Carlo mean payoff agrees with v at |z| < Z_ACCEPT.
  G3 INVARIANCE - (a) minimax guarantee: with row fixed at its optimal mix the
                  expected payoff equals v EXACTLY against every column strategy
                  in a panel; (b) affine invariance: M -> alpha*M + beta shifts
                  the value to alpha*v + beta exactly and leaves the optimal
                  mixes unchanged.
  G4 FALSIFY    - on the SAME MC sample, the plausible naive rule
                  "value == pure-strategy security level (maximin) = -1" is
                  rejected at |z| >= Z_REJECT.

Stdlib only: json, hashlib, math, random, fractions.
"""

import json
import hashlib
import math
import random
from fractions import Fraction

SEED = 20260717

# ---- reference game (all rational) ----------------------------------------
A = Fraction(3)
B = Fraction(-1)
C = Fraction(-2)
D = Fraction(1)

# ---- gate constants -------------------------------------------------------
MC_TRIALS = 400_000
Z_ACCEPT = 3.0
Z_REJECT = 6.0

# panel of no-saddle 2x2 rational games (row maximiser): (a, b, c, d)
PANEL = [
    (Fraction(3), Fraction(-1), Fraction(-2), Fraction(1)),   # v = 1/7 (reference)
    (Fraction(2), Fraction(0), Fraction(-1), Fraction(3)),    # v = 1
    (Fraction(1), Fraction(4), Fraction(3), Fraction(2)),     # v = 5/2
    (Fraction(0), Fraction(-2), Fraction(-3), Fraction(1)),   # v = -1
]

# a game WITH a pure saddle point, for the no-saddle guard cross-check
SADDLE_GAME = (Fraction(4), Fraction(3), Fraction(2), Fraction(1))  # saddle value 3


def denom(a, b, c, d):
    return a + d - b - c


def closed_form(a, b, c, d):
    """Closed-form value and optimal mixes (prob of the FIRST option each)."""
    g = denom(a, b, c, d)
    v = (a * d - b * c) / g
    p_row0 = (d - c) / g
    q_col0 = (d - b) / g
    return v, p_row0, q_col0


def pure_bounds(a, b, c, d):
    """Pure-strategy maximin (row security level) and minimax (column)."""
    maximin = max(min(a, b), min(c, d))   # row picks a row, adversary the min
    minimax = min(max(a, c), max(b, d))   # column picks a col, adversary the max
    return maximin, minimax


def indifference_value(a, b, c, d):
    """Independent route: row mix making column indifferent, then the payoff."""
    g = denom(a, b, c, d)
    x = (d - c) / g                        # prob of row0
    pay_col0 = x * a + (1 - x) * c
    pay_col1 = x * b + (1 - x) * d
    assert pay_col0 == pay_col1, "column not indifferent under x"
    return pay_col0


def gate1_exact():
    ok = True
    rows = []
    for (a, b, c, d) in PANEL:
        maximin, minimax = pure_bounds(a, b, c, d)
        no_saddle = maximin < minimax
        v, p, q = closed_form(a, b, c, d)
        v_ind = indifference_value(a, b, c, d)
        mix_interior = (Fraction(0) < p < Fraction(1)) and (Fraction(0) < q < Fraction(1))
        this = no_saddle and (v == v_ind) and mix_interior
        ok = ok and this
        rows.append({
            "game": f"a={a} b={b} c={c} d={d}",
            "value": str(v), "p_row0": str(p), "q_col0": str(q),
            "value_indifference_route": str(v_ind),
            "pure_maximin": str(maximin), "pure_minimax": str(minimax),
            "no_saddle": no_saddle, "mix_interior": mix_interior,
            "closed_form_eq_indifference": (v == v_ind),
        })
    # cross-check: the saddle game HAS a saddle, pure value = maximin = minimax
    a, b, c, d = SADDLE_GAME
    maximin, minimax = pure_bounds(a, b, c, d)
    saddle_ok = (maximin == minimax)
    ok = ok and saddle_ok
    return ok, {"panel": rows,
                "saddle_crosscheck": {
                    "game": f"a={a} b={b} c={c} d={d}",
                    "pure_maximin": str(maximin), "pure_minimax": str(minimax),
                    "has_saddle": saddle_ok, "pure_value": str(maximin)}}


def _mc_sample():
    """Both players draw their optimal mixed strategy; payoff = M[i][j]."""
    v, p_row0, q_col0 = closed_form(A, B, C, D)
    pr = float(p_row0)
    qc = float(q_col0)
    m = [[float(A), float(B)], [float(C), float(D)]]
    rng = random.Random(SEED)
    xs = []
    for _ in range(MC_TRIALS):
        i = 0 if rng.random() < pr else 1
        j = 0 if rng.random() < qc else 1
        xs.append(m[i][j])
    n = len(xs)
    mean = math.fsum(xs) / n
    var = math.fsum((x - mean) ** 2 for x in xs) / (n - 1)
    se = math.sqrt(var / n)
    return mean, se, n


def gate2_mc_agreement(sample):
    mean, se, n = sample
    v, _, _ = closed_form(A, B, C, D)
    target = float(v)
    z = (mean - target) / se
    return abs(z) < Z_ACCEPT, {
        "trials": n, "mc_mean": round(mean, 6), "target": round(target, 6),
        "z": round(z, 6), "z_accept": Z_ACCEPT, "pass_if": "abs(z) < Z_ACCEPT"}


def gate3_invariance():
    ok = True
    v, p_row0, q_col0 = closed_form(A, B, C, D)

    # (a) minimax guarantee: row fixed at optimal mix, payoff == v vs ANY column
    guar_rows = []
    col_panel = [Fraction(1), Fraction(0), Fraction(1, 2), Fraction(1, 3), q_col0]
    for y in col_panel:  # y = prob column plays col0
        ep = (p_row0 * (y * A + (1 - y) * B)
              + (1 - p_row0) * (y * C + (1 - y) * D))
        exact = (ep == v)
        ok = ok and exact
        guar_rows.append({"q_col0": str(y), "expected_payoff": str(ep),
                          "equals_v": exact})

    # (b) affine invariance: M -> alpha*M + beta
    aff_rows = []
    for (alpha, beta) in [(Fraction(2), Fraction(5)),
                          (Fraction(3), Fraction(-1)),
                          (Fraction(1, 2), Fraction(10))]:
        a2 = alpha * A + beta
        b2 = alpha * B + beta
        c2 = alpha * C + beta
        d2 = alpha * D + beta
        v2, p2, q2 = closed_form(a2, b2, c2, d2)
        exact = (v2 == alpha * v + beta and p2 == p_row0 and q2 == q_col0)
        ok = ok and exact
        aff_rows.append({"alpha": str(alpha), "beta": str(beta),
                         "value": str(v2),
                         "alpha_v_plus_beta": str(alpha * v + beta),
                         "p_row0": str(p2), "q_col0": str(q2), "matches": exact})

    return ok, {"value": str(v), "p_row0": str(p_row0), "q_col0": str(q_col0),
                "minimax_guarantee": guar_rows, "affine_invariance": aff_rows}


def gate4_falsify(sample):
    mean, se, n = sample
    maximin, _ = pure_bounds(A, B, C, D)   # pure security level = -1
    naive_target = float(maximin)
    z = (mean - naive_target) / se
    return abs(z) >= Z_REJECT, {
        "naive_claim": "value == pure-strategy security level (maximin)",
        "naive_target": round(naive_target, 6),
        "mc_mean": round(mean, 6), "z_naive": round(z, 6),
        "z_reject": Z_REJECT,
        "pass_if": "abs(z_naive) >= Z_REJECT (naive rule refuted)"}


def build_results():
    v, p_row0, q_col0 = closed_form(A, B, C, D)
    maximin, minimax = pure_bounds(A, B, C, D)
    sample = _mc_sample()

    g1_ok, g1 = gate1_exact()
    g2_ok, g2 = gate2_mc_agreement(sample)
    g3_ok, g3 = gate3_invariance()
    g4_ok, g4 = gate4_falsify(sample)

    gates = {
        "G1_exact_value_identity": {"pass": g1_ok, **g1},
        "G2_montecarlo_agreement": {"pass": g2_ok, **g2},
        "G3_invariance_robustness": {"pass": g3_ok, **g3},
        "G4_falsifiability_naive": {"pass": g4_ok, **g4},
    }
    order = ["G1_exact_value_identity", "G2_montecarlo_agreement",
             "G3_invariance_robustness", "G4_falsifiability_naive"]
    first_failing = next((g for g in order if not gates[g]["pass"]), None)
    all_pass = first_failing is None

    return {
        "claim": "zerosum_2x2_value: v == (a*d - b*c)/(a + d - b - c)",
        "seed": SEED,
        "reference_game": {
            "matrix": [[str(A), str(B)], [str(C), str(D)]],
            "value": str(v), "p_row0": str(p_row0), "q_col0": str(q_col0),
            "pure_maximin": str(maximin), "pure_minimax": str(minimax),
        },
        "gates": gates,
        "all_gates_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "sim-ready" if all_pass else "needs-more-grooming",
    }


def canonical(r):
    return json.dumps(r, sort_keys=True, separators=(",", ":"))


def main():
    c1 = canonical(build_results())
    c2 = canonical(build_results())
    assert c1 == c2, "NON-DETERMINISTIC: in-process double-run diverged"
    digest = hashlib.sha256(c1.encode()).hexdigest()
    results = build_results()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("in_process_double_run: IDENTICAL")
    print("results_sha256: " + digest)
    print("decision: " + results["decision"])
    raise SystemExit(0 if results["all_gates_pass"] else 1)


if __name__ == "__main__":
    main()
