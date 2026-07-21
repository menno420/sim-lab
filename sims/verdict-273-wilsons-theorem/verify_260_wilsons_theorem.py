#!/usr/bin/env python3
"""
PROPOSAL 260 -- Wilson's theorem verifier (stdlib only).

Claim: for every integer n >= 2,
    (n-1)! is congruent to -1 (mod n)   if and only if   n is prime.

Four gates, each in its own direction:
  G1 EXACT        the Wilson predicate agrees with independent trial-division
                  primality on every n in [2, N] (0 mismatches), and the
                  iterated-mod residue equals the exact full-bignum factorial
                  residue on [2, bignum_N] (0 mismatches).
  G2 MC AGREEMENT iid uniform draws of n in [2, N]; the empirical density of
                  the Wilson predicate matches the exact prime density
                  pi(N)/(N-1) at |z| < 3 (binomial).
  G3 INVARIANCE   composite-side robustness: every composite n > 4 has
                  (n-1)! congruent to 0 (mod n); the sole composite exception
                  is n = 4 (residue 2).
  G4 FALSIFIABLE  the sign-flip foil "(n-1)! congruent to +1 (mod n) iff prime"
                  is rejected at |z| > 3 (it holds for almost no prime).

Determinism: SEED fixed; build_results is a pure function of SEED and the
fixed parameters (no wall clock / hostname / unseeded randomness); every float
enters via a fixed 6-dp format string, every count as an int, every fraction
as "num/den". In-process double-run and a separate re-invocation are
byte-identical; results_sha256 is the full 64-hex sha256 of the results dict.
"""

import argparse
import hashlib
import json
import math
import random
import sys
from fractions import Fraction

SEED = 20260721
N = 1500          # population upper bound (inclusive) for {2..N}
BIGNUM_N = 400    # upper bound for the exact full-factorial cross-check
M = 200000        # iid Monte-Carlo draws
Z_ACCEPT = 3.0
Z_REJECT = 3.0


def is_prime_trial(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def wilson_residue(n):
    """(n-1)! mod n by exact iterated modular reduction."""
    r = 1
    for k in range(2, n):
        r = (r * k) % n
    return r


def wilson_residue_bignum(n):
    """(n-1)! mod n via the exact full bignum factorial."""
    return math.factorial(n - 1) % n


def fmt_z(x):
    return "%.6f" % x


def build_results(seed=SEED):
    residue = [0] * (N + 1)
    for n in range(2, N + 1):
        residue[n] = wilson_residue(n)

    prime = [False] * (N + 1)
    for n in range(2, N + 1):
        prime[n] = is_prime_trial(n)

    # G1: exact agreement + full-bignum cross-check
    g1_mismatches = 0
    for n in range(2, N + 1):
        wilson = (residue[n] == (n - 1) % n)
        if wilson != prime[n]:
            g1_mismatches += 1
    g1_bignum_mismatches = 0
    for n in range(2, BIGNUM_N + 1):
        if residue[n] != wilson_residue_bignum(n):
            g1_bignum_mismatches += 1
    g1_pass = (g1_mismatches == 0 and g1_bignum_mismatches == 0)

    # exact prime density over {2..N}
    pop = N - 1
    pi_N = sum(1 for n in range(2, N + 1) if prime[n])
    density = Fraction(pi_N, pop)
    d = pi_N / pop
    se = math.sqrt(d * (1.0 - d) / M)

    # G2 + G4 iid sampling
    rng = random.Random(seed)
    g2_hits = 0
    g4_foil_hits = 0
    for _ in range(M):
        n = rng.randint(2, N)
        if residue[n] == (n - 1) % n:
            g2_hits += 1
        if residue[n] == 1 % n:
            g4_foil_hits += 1
    g2_z = (g2_hits / M - d) / se
    g2_pass = abs(g2_z) < Z_ACCEPT
    g4_z = (g4_foil_hits / M - d) / se
    g4_reject = abs(g4_z) > Z_REJECT

    # G3: composite-side invariance
    g3_exceptions = [n for n in range(5, N + 1)
                     if (not prime[n]) and residue[n] != 0]
    g3_n4_residue = residue[4]
    g3_pass = (len(g3_exceptions) == 0 and g3_n4_residue == 2)

    # anchors (incl. Carmichael numbers 561, 1105 that fool Fermat but not Wilson)
    anchor_ns = [2, 3, 4, 5, 6, 7, 9, 11, 13, 15, 561, 1105]
    anchors = {}
    for n in anchor_ns:
        r = residue[n] if n <= N else wilson_residue(n)
        p = prime[n] if n <= N else is_prime_trial(n)
        anchors[str(n)] = {
            "residue": r,
            "wilson_holds": (r == (n - 1) % n),
            "is_prime": p,
        }

    gates = {
        "G1": {
            "direction": "exact: Wilson predicate == independent trial-division primality on [2,N]; iterated-mod == full-bignum residue on [2,bignum_N]",
            "range_hi": N,
            "checked": pop,
            "mismatches": g1_mismatches,
            "bignum_range_hi": BIGNUM_N,
            "bignum_mismatches": g1_bignum_mismatches,
            "z": "exact",
            "pass": g1_pass,
        },
        "G2": {
            "direction": "iid MC: empirical Wilson-predicate density matches exact prime density pi(N)/(N-1) at |z|<3",
            "N_samples": M,
            "exact_prime_count": pi_N,
            "exact_density": "%d/%d" % (density.numerator, density.denominator),
            "hits": g2_hits,
            "phat": "%.6f" % (g2_hits / M),
            "z": fmt_z(g2_z),
            "z_accept": "%.6f" % Z_ACCEPT,
            "pass": g2_pass,
        },
        "G3": {
            "direction": "invariance: composite n>4 => (n-1)! congruent to 0 (mod n); sole composite exception n=4 (residue 2)",
            "range_hi": N,
            "composite_nonzero_exceptions": g3_exceptions,
            "n4_residue": g3_n4_residue,
            "violations": len(g3_exceptions),
            "pass": g3_pass,
        },
        "G4": {
            "direction": "falsifiability: reject the sign-flip foil (n-1)! congruent to +1 (mod n) iff prime at |z|>3",
            "N_samples": M,
            "foil_hits": g4_foil_hits,
            "foil_phat": "%.6f" % (g4_foil_hits / M),
            "z_foil": fmt_z(g4_z),
            "z_reject": "%.6f" % Z_REJECT,
            "reject": g4_reject,
            "pass": g4_reject,
        },
    }

    all_pass = all(gates[g]["pass"] for g in ("G1", "G2", "G3", "G4"))
    first_failing = next((g for g in ("G1", "G2", "G3", "G4") if not gates[g]["pass"]), None)

    results = {
        "proposal": 260,
        "claim": "for n>=2: (n-1)! == -1 (mod n) iff n is prime",
        "SEED": seed,
        "params": {"N": N, "M": M, "bignum_N": BIGNUM_N},
        "anchors": anchors,
        "G1": gates["G1"],
        "G2": gates["G2"],
        "G3": gates["G3"],
        "G4": gates["G4"],
        "all_gates_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "PASS" if all_pass else "FAIL",
    }
    return results


def results_sha256(results):
    blob = json.dumps(results, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true",
                    help="in-process double-run determinism check")
    ap.parse_args(argv)

    r1 = build_results()
    r2 = build_results()
    digest = results_sha256(r1)
    identical = (r1 == r2) and (results_sha256(r2) == digest)

    print(json.dumps(r1, sort_keys=True, indent=2))
    for g in ("G1", "G2", "G3", "G4"):
        print("%s: %s" % (g, "PASS" if r1[g]["pass"] else "FAIL"))
    print()
    print("results_sha256 = %s" % digest)
    print()
    print("determinism: in-process double-run identical = %s" % identical)

    if not r1["all_gates_pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
