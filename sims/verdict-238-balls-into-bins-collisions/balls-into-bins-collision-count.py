#!/usr/bin/env python3
"""Balls-into-bins expected collision count - firsthand verifier (PROPOSAL 225).

Counterintuitive-but-exactly-true: throw m balls independently and uniformly
into n bins (equivalently: hash m keys into a table of n buckets, or draw m
values from a discrete-uniform space of size n). Count a COLLISION for every
UNORDERED PAIR of balls that share a bin - i.e. X = sum_bins C(B_k, 2), where
B_k is the load of bin k. The expected number of colliding pairs is EXACTLY

    E[X] = C(m, 2) / n = m(m-1) / (2n)          (fraction-exact)

by linearity of expectation over the C(m,2) pairs: each fixed pair lands in the
same bin with probability exactly 1/n (sum over the n bins of (1/n)*(1/n)), so
E[X] = C(m,2) * (1/n). NO independence between pairs is needed - linearity does
not care. The count is quadratic in m: it is the m(m-1)/2 PAIRS that grow, not
the m balls, which is why hash-table / shard / nonce collisions arrive far
sooner than a per-ball 1/n intuition predicts (the birthday-attack mechanism).

The plausible-but-WRONG engineering shortcut drops the -1 and writes
E ~= m^2/(2n) (as if a ball could collide with itself, counting m^2/2 ordered
self-inclusive pairs). It overstates the exact answer by exactly m/(2n) and is
REJECTED here at large |z|. A second wrong model, the ORDERED-pair count
m(m-1)/n (double-counting each pair), is rejected even harder.

Stdlib-only. SEED=20260717, all randomness from a single random.Random(20260717)
consumed in a fixed, documented order: G2 draws MC_TRIALS balls-into-bins trials
per config (in CONFIGS order), then G3 draws the robustness sweep (SWEEP order),
then G4 draws the falsifiability sample on FALSIFY_CFG - back-to-back, no
interleaving. Deterministic across in-process double-run and separate
cross-invocation.

Gate battery (each read in ITS OWN direction):
  G1 EXACT identity (Fraction, equality). Direction: any of the three exact
     routes != the closed form => FAIL. For each config the expected colliding-
     pair count is built THREE independent exact ways and asserted equal:
       (a) LITERAL sum of Fraction(1, n) over all C(m,2) unordered pairs
           (multiplied/added out in a loop, NOT hardcoded to the closed form);
       (b) the per-bin linearity route n * Fraction(C(m,2), n*n);
       (c) the closed form Fraction(m*(m-1), 2*n).
     PASS = (a) == (b) == (c) exactly for every config.
  G2 MONTE-CARLO agreement (|z| < 3 PASS). Direction: |z| >= 3 => FAIL. For
     each config the sample mean of X over MC_TRIALS trials agrees with the
     exact E[X] within 3 sigma, z = (mean - E)/(sample_sd/sqrt(T)).
  G3 ROBUSTNESS (sweep, all agree). Direction: any swept config disagrees
     (|z| >= 3), OR the exact-scaling identity fails => FAIL. (a) a strictly-
     larger set of (n, m) configs each agree within |z| < 3; (b) an exact
     algebraic leg: doubling m from m to 2m at fixed n multiplies E by exactly
     (2m-1)/(m-1)*... - checked as the exact Fraction ratio E(2m)/E(m).
  G4 FALSIFIABILITY (wrong model REJECTED at |z| >= 6). Direction: PASS iff the
     naive m^2/(2n) shortcut is REJECTED at |z| >= 6 on the SAME sample whose
     mean AGREES with the exact m(m-1)/(2n) at |z| < 3. The ordered-pair count
     m(m-1)/n is recorded as a second, harder rejection.
"""
import hashlib
import json
import math
import random
from fractions import Fraction

SEED = 20260717
# (n bins, m balls) - hash-collision / shard-cover flavored configs.
CONFIGS = [(365, 23), (256, 64), (1000, 100)]   # G1 exact + G2 MC
SWEEP = [(365, 30), (128, 40), (500, 50), (64, 16)]  # G3 robustness sweep
FALSIFY_CFG = (256, 64)                          # G4 falsifiability sample
MC_TRIALS = 200000                               # trials per config (G2, G4)
SWEEP_TRIALS = 120000                            # trials per swept config (G3)
Z_AGREE = 3.0                                    # G2/G3 two-sided agreement band
Z_REJECT = 6.0                                   # G4 falsifiability rejection floor


def frac_str(f):
    return "{0}/{1}".format(f.numerator, f.denominator)


# ---- exact expected colliding-pair count, THREE independent routes ----------
def exact_pairsum(n, m):
    """Route (a): LITERAL sum of Fraction(1, n) over all C(m,2) unordered pairs,
    added out in a double loop - NOT hardcoded to the closed form."""
    total = Fraction(0)
    per_pair = Fraction(1, n)
    for a in range(m):
        for b in range(a + 1, m):
            total += per_pair
    return total


def exact_perbin(n, m):
    """Route (b): per-bin linearity - each of the n bins contributes
    E[C(B_k,2)] = C(m,2)/n^2, summed over n bins."""
    cm2 = Fraction(m * (m - 1), 2)
    return n * (cm2 / Fraction(n * n))


def exact_closed(n, m):
    """Route (c): the closed form m(m-1)/(2n)."""
    return Fraction(m * (m - 1), 2 * n)


# ---- one balls-into-bins trial: X = sum_bins C(load, 2) ---------------------
def collision_count(rng, n, m):
    """Throw m balls uniformly into n bins; return the number of colliding
    unordered pairs = sum over bins of C(load, 2). Counted incrementally in
    O(m): each arriving ball forms exactly `current load` new colliding pairs
    with the balls already in its bin, and summing (load-before-insert) over all
    balls equals sum_bins C(load,2). Consumes exactly m rng.randrange(n) draws
    per trial, in order - identical to the per-bin scan, so the result and the
    RNG stream are unchanged."""
    loads = {}
    x = 0
    for _ in range(m):
        b = rng.randrange(n)
        c = loads.get(b, 0)
        x += c
        loads[b] = c + 1
    return x


def mc_stats(rng, n, m, T):
    """Sample mean and sample standard deviation of X over T trials."""
    s = 0
    s2 = 0
    for _ in range(T):
        x = collision_count(rng, n, m)
        s += x
        s2 += x * x
    mean = s / T
    var = (s2 - s * s / T) / (T - 1)      # unbiased sample variance
    sd = math.sqrt(var) if var > 0 else 0.0
    return mean, sd


def z_of(mean, target, sd, T):
    """Two-sided z of the sample mean vs `target` using the sample SE."""
    se = sd / math.sqrt(T) if sd > 0 else float("inf")
    return (mean - target) / se if se > 0 else 0.0, se


# ---- G1: EXACT identity - three routes agree exactly ------------------------
def gate_g1():
    per_config = {}
    ok = True
    for (n, m) in CONFIGS:
        a = exact_pairsum(n, m)
        b = exact_perbin(n, m)
        c = exact_closed(n, m)
        agree = (a == b == c)
        ok = ok and agree
        per_config["{0},{1}".format(n, m)] = {
            "n": n,
            "m": m,
            "pairs_C_m_2": m * (m - 1) // 2,
            "route_a_pairsum": frac_str(a),
            "route_b_perbin": frac_str(b),
            "route_c_closed": frac_str(c),
            "three_routes_equal": agree,
            "E_float": round(float(c), 9),
        }
    return ok, per_config


# ---- G2: Monte-Carlo agreement, |z| < 3 -------------------------------------
def gate_g2(rng):
    per_config = {}
    ok = True
    for (n, m) in CONFIGS:
        E = float(exact_closed(n, m))
        mean, sd = mc_stats(rng, n, m, MC_TRIALS)
        z, se = z_of(mean, E, sd, MC_TRIALS)
        good = abs(z) < Z_AGREE
        ok = ok and good
        per_config["{0},{1}".format(n, m)] = {
            "n": n,
            "m": m,
            "trials": MC_TRIALS,
            "E_exact": round(E, 9),
            "sample_mean": round(mean, 9),
            "sample_sd": round(sd, 9),
            "z": round(z, 6),
            "within_3sigma": good,
        }
    return ok, per_config


# ---- G3: robustness sweep + exact-scaling algebra ---------------------------
def gate_g3(rng):
    sweep = {}
    sweep_ok = True
    for (n, m) in SWEEP:
        E = float(exact_closed(n, m))
        mean, sd = mc_stats(rng, n, m, SWEEP_TRIALS)
        z, se = z_of(mean, E, sd, SWEEP_TRIALS)
        good = abs(z) < Z_AGREE
        sweep_ok = sweep_ok and good
        sweep["{0},{1}".format(n, m)] = {
            "n": n,
            "m": m,
            "trials": SWEEP_TRIALS,
            "E_exact": round(E, 9),
            "sample_mean": round(mean, 9),
            "z": round(z, 6),
            "within_3sigma": good,
        }
    # (b) exact-scaling algebra: E(n, 2m)/E(n, m) == (2m)(2m-1) / (m)(m-1),
    # independent of n - a pure Fraction identity, no randomness.
    scale = {}
    scale_ok = True
    for (n, m) in [(365, 23), (256, 64)]:
        r_sim = exact_closed(n, 2 * m) / exact_closed(n, m)
        r_pred = Fraction((2 * m) * (2 * m - 1), m * (m - 1))
        eq = (r_sim == r_pred)
        scale_ok = scale_ok and eq
        scale["{0},{1}".format(n, m)] = {
            "ratio_E2m_over_Em": frac_str(r_sim),
            "predicted_ratio": frac_str(r_pred),
            "n_independent_equal": eq,
        }
    ok = sweep_ok and scale_ok
    return ok, {
        "sweep": sweep,
        "sweep_all_within_3sigma": sweep_ok,
        "exact_scaling": scale,
        "scaling_holds": scale_ok,
        "both_hold": ok,
    }


# ---- G4: falsifiability - the m^2/(2n) shortcut REJECTED at |z| >= 6 ---------
def gate_g4(rng):
    n, m = FALSIFY_CFG
    E_true = float(exact_closed(n, m))          # m(m-1)/(2n)
    E_naive = (m * m) / (2.0 * n)               # WRONG: m^2/(2n) (self-pair)
    E_ordered = (m * (m - 1)) / (1.0 * n)       # WRONG: ordered pairs m(m-1)/n
    mean, sd = mc_stats(rng, n, m, MC_TRIALS)
    z_true, se = z_of(mean, E_true, sd, MC_TRIALS)
    z_naive, _ = z_of(mean, E_naive, sd, MC_TRIALS)
    z_ordered, _ = z_of(mean, E_ordered, sd, MC_TRIALS)
    true_agrees = abs(z_true) < Z_AGREE
    naive_rejected = abs(z_naive) >= Z_REJECT
    ordered_rejected = abs(z_ordered) >= Z_REJECT
    # the exact overstatement of the naive shortcut is m/(2n), as a Fraction
    overstate = Fraction(m * m, 2 * n) - exact_closed(n, m)       # = m/(2n)
    ok = true_agrees and naive_rejected and ordered_rejected
    return ok, {
        "config": [n, m],
        "trials": MC_TRIALS,
        "E_true_m_m_minus_1_over_2n": round(E_true, 9),
        "E_naive_m_squared_over_2n": round(E_naive, 9),
        "E_ordered_m_m_minus_1_over_n": round(E_ordered, 9),
        "sample_mean": round(mean, 9),
        "z_true_agree": round(z_true, 6),
        "z_naive_reject": round(z_naive, 6),
        "z_ordered_reject": round(z_ordered, 6),
        "naive_overstatement_exact": frac_str(overstate),   # m/(2n)
        "true_agrees_within_3sigma": true_agrees,
        "naive_rejected_at_z_ge_6": naive_rejected,
        "ordered_rejected_at_z_ge_6": ordered_rejected,
        "both_wrong_models_rejected": naive_rejected and ordered_rejected,
    }


def run_battery():
    rng = random.Random(SEED)
    g1_ok, g1 = gate_g1()
    g2_ok, g2 = gate_g2(rng)
    g3_ok, g3 = gate_g3(rng)
    g4_ok, g4 = gate_g4(rng)

    gates = {"G1": g1_ok, "G2": g2_ok, "G3": g3_ok, "G4": g4_ok}
    sim_ready = all(gates.values())
    return {
        "proposal": "PROPOSAL 225",
        "verdict": 238,
        "theorem": "Balls-into-bins expected collision count = m(m-1)/(2n)",
        "identity": "E[colliding pairs] = C(m,2)/n = m(m-1)/(2n) exactly",
        "seed": SEED,
        "configs": [list(c) for c in CONFIGS],
        "g1_exact_identity": g1,
        "g2_montecarlo": g2,
        "g3_robustness": g3,
        "g4_falsifiability": g4,
        "gates": gates,
        "sim_ready": sim_ready,
    }


def digest(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


if __name__ == "__main__":
    import sys

    r1 = run_battery()
    r2 = run_battery()
    d1 = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    d2 = json.dumps(r2, sort_keys=True, separators=(",", ":"))
    determinism = (d1 == d2)
    sim_ready = r1["sim_ready"]
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("results_sha256={0}".format(digest(r1)))
    print("determinism_double_run={0}".format(determinism))
    print("sim_ready={0}".format(sim_ready))
    sys.exit(0 if (sim_ready and determinism) else 1)
