#!/usr/bin/env python3
"""PROPOSAL 236 - Counting necklaces: the Burnside / cyclic-group orbit count.

Claim (exact, closed-form): the number of distinct necklaces of n beads in k
colours, counting two colourings equivalent when one is a rotation of the other
(the cyclic group C_n acting on bead positions), is the exact integer

        N_k(n) = (1/n) * sum_{d | n} phi(d) * k^(n/d)

where phi is Euler's totient. This is Burnside's lemma specialised to C_n
(each rotation by s fixes k^gcd(s,n) colourings, and grouping the n rotations
by the order d = n/gcd of the subgroup they generate gives phi(d) rotations
each fixing k^(n/d) colourings). For the headline instance n = 6, k = 3:

        N_3(6) = (1/6)[phi(1)*3^6 + phi(2)*3^3 + phi(3)*3^2 + phi(6)*3^1]
               = (1/6)[729 + 27 + 18 + 6] = 780/6 = 130.

SEED = 20260717. build_results() is a pure function of SEED and the module
constants (one seeded random.Random(SEED) consumed in fixed order; no
wall-clock / PID / unordered-set iteration in the hashed payload), so an
in-process double-run and a separate re-invocation are byte-identical;
results_sha256 is the sha256 of the canonical results dict.

Four gates, each in its own direction:
  G1 EXACT      - the Fraction (1/n) sum_{d|n} phi(d) k^(n/d) reduces to an
                  integer (denominator 1) and equals BOTH the brute-force
                  orbit count (enumerate every k^n colouring, bucket by the
                  minimum over its n rotations) AND the expected value, on a
                  panel of (n, k) instances.
  G2 MC AGREE   - drawing uniform random colourings of the headline (6, 3),
                  the unbiased estimator N_hat = k^n * mean(1/orbit_size)
                  agrees with the exact N = 130 at |z| < Z_ACCEPT.
  G3 INVARIANCE - the orbit count is a function of orbit structure only, so it
                  is invariant to a colour relabelling; permuting every colour
                  by the cyclic +1 (mod k) map and re-counting reproduces the
                  brute count for (6, 3) and (5, 2).
  G4 FALSIFY    - on the SAME MC sample, the plausible naive rule
                  "N == k^n / n" (divide by the group order, ignoring the
                  non-free orbits) with value 729/6 = 121.5 is rejected at
                  |z| >= Z_REJECT.

Stdlib only: json, hashlib, math, random, fractions.
"""

import json
import hashlib
import math
import random
from fractions import Fraction

SEED = 20260717

# ---- gate constants -------------------------------------------------------
MC_TRIALS = 400_000
Z_ACCEPT = 3.0
Z_REJECT = 6.0

# panel of (n, k, expected necklace count) -- recomputed, not trusted
PANEL = [
    (6, 3, 130),
    (4, 2, 6),
    (5, 2, 8),
    (6, 2, 14),
    (4, 3, 24),
]

# headline instance
HEADLINE_N = 6
HEADLINE_K = 3
HEADLINE_N_EXACT = 130
HEADLINE_KPOWN = 729  # 3 ** 6


# ---- number theory --------------------------------------------------------
def euler_phi(n):
    """Euler's totient via trial-division factorisation."""
    assert n >= 1
    result = n
    m = n
    p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            result -= result // p
        p += 1
    if m > 1:
        result -= result // m
    return result


def divisors(n):
    """Sorted list of positive divisors of n."""
    ds = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            ds.append(i)
            if i != n // i:
                ds.append(n // i)
        i += 1
    return sorted(ds)


def burnside_count(n, k):
    """Exact necklace count as a fractions.Fraction (must reduce to integer)."""
    total = Fraction(0)
    for d in divisors(n):
        total += Fraction(euler_phi(d)) * Fraction(k) ** (n // d)
    return total / n


# ---- cyclic-group action on colourings ------------------------------------
def rotate(c, s):
    """Rotate colouring tuple c by s positions."""
    s %= len(c)
    return c[s:] + c[:s]


def canonical_form(c):
    """Lexicographically minimal rotation -- the orbit representative."""
    n = len(c)
    return min(rotate(c, s) for s in range(n))


def stabilizer_size(c):
    """Number of rotations fixing c (order of its cyclic stabiliser)."""
    n = len(c)
    return sum(1 for s in range(n) if rotate(c, s) == c)


def orbit_size(c):
    """Orbit-stabiliser: |orbit| = n / |stabiliser|."""
    n = len(c)
    return n // stabilizer_size(c)


def all_colorings(n, k):
    """Yield every k^n colouring as an n-tuple over range(k) (base-k odometer)."""
    total = k ** n
    for idx in range(total):
        c = []
        x = idx
        for _ in range(n):
            c.append(x % k)
            x //= k
        yield tuple(c)


def brute_orbit_count(n, k):
    """Enumerate all colourings, count distinct minimal-rotation reps."""
    reps = set()
    for c in all_colorings(n, k):
        reps.add(canonical_form(c))
    return len(reps)


def relabel(c, k):
    """Nontrivial colour permutation: cyclic +1 (mod k) on every bead."""
    return tuple((x + 1) % k for x in c)


def brute_orbit_count_relabeled(n, k):
    """Orbit count over the colour-relabelled space (must match the original)."""
    reps = set()
    for c in all_colorings(n, k):
        reps.add(canonical_form(relabel(c, k)))
    return len(reps)


# ---- gates ----------------------------------------------------------------
def gate1_exact():
    ok = True
    rows = []
    for (n, k, exp) in PANEL:
        v = burnside_count(n, k)
        brute = brute_orbit_count(n, k)
        is_int = (v.denominator == 1)
        matches = is_int and (v == Fraction(exp)) and (brute == exp)
        ok = ok and matches
        rows.append({
            "n": n, "k": k, "expected": exp,
            "burnside_fraction": str(v),
            "burnside_int": int(v) if is_int else None,
            "denominator_is_1": is_int,
            "brute_orbit_count": brute,
            "all_agree": matches,
        })
    headline = burnside_count(HEADLINE_N, HEADLINE_K)
    return ok, {
        "panel": rows,
        "headline_fraction_repr": repr(headline),
        "headline_reduces_to": int(headline) if headline.denominator == 1 else None,
    }


def _mc_sample():
    """Draw uniform random colourings of the headline; x = 1/orbit_size."""
    n, k = HEADLINE_N, HEADLINE_K
    rng = random.Random(SEED)
    xs = []
    for _ in range(MC_TRIALS):
        c = tuple(rng.randrange(k) for _ in range(n))
        xs.append(1.0 / orbit_size(c))
    m = len(xs)
    mean = math.fsum(xs) / m
    var_pop = math.fsum((x - mean) ** 2 for x in xs) / m
    return mean, var_pop, m


def gate2_mc_agreement(sample):
    mean, var_pop, m = sample
    kpown = HEADLINE_KPOWN
    n_hat = kpown * mean
    se = kpown * math.sqrt(var_pop) / math.sqrt(m)
    z = (n_hat - HEADLINE_N_EXACT) / se
    return abs(z) < Z_ACCEPT, {
        "trials": m,
        "n_hat": round(n_hat, 6),
        "target": HEADLINE_N_EXACT,
        "se": round(se, 8),
        "z": round(z, 6),
        "z_accept": Z_ACCEPT,
        "pass_if": "abs(z) < Z_ACCEPT",
    }


def gate3_invariance():
    ok = True
    rows = []
    for (n, k) in [(HEADLINE_N, HEADLINE_K), (5, 2)]:
        base = brute_orbit_count(n, k)
        relabeled = brute_orbit_count_relabeled(n, k)
        invariant = (base == relabeled)
        ok = ok and invariant
        rows.append({
            "n": n, "k": k,
            "brute_orbit_count": base,
            "relabeled_orbit_count": relabeled,
            "invariant": invariant,
        })
    return ok, {
        "relabel": "cyclic +1 (mod k) on every bead",
        "checks": rows,
    }


def gate4_falsify(sample):
    mean, var_pop, m = sample
    kpown = HEADLINE_KPOWN
    n_hat = kpown * mean
    se = kpown * math.sqrt(var_pop) / math.sqrt(m)
    n_naive = kpown / HEADLINE_N   # 729 / 6 = 121.5 -- "divide by group order"
    z = (n_hat - n_naive) / se
    return abs(z) >= Z_REJECT, {
        "naive_claim": "N == k^n / n (divide by group order, ignores non-free orbits)",
        "n_naive": round(n_naive, 6),
        "n_hat": round(n_hat, 6),
        "z_reject_stat": round(z, 6),
        "z_reject": Z_REJECT,
        "pass_if": "abs(z_reject_stat) >= Z_REJECT (naive rule refuted)",
    }


def build_results():
    sample = _mc_sample()

    g1_ok, g1 = gate1_exact()
    g2_ok, g2 = gate2_mc_agreement(sample)
    g3_ok, g3 = gate3_invariance()
    g4_ok, g4 = gate4_falsify(sample)

    gates = {
        "G1_exact_orbit_count": {"name": "exact closed form == brute == expected",
                                 "ok": g1_ok, **g1},
        "G2_montecarlo_agreement": {"name": "MC estimator agrees with N",
                                    "ok": g2_ok, **g2},
        "G3_invariance_relabel": {"name": "orbit count invariant to colour relabel",
                                  "ok": g3_ok, **g3},
        "G4_falsifiability_naive": {"name": "naive N == k^n/n rejected",
                                    "ok": g4_ok, **g4},
    }
    order = ["G1_exact_orbit_count", "G2_montecarlo_agreement",
             "G3_invariance_relabel", "G4_falsifiability_naive"]
    first_failing = next((g for g in order if not gates[g]["ok"]), None)
    all_pass = first_failing is None

    return {
        "claim": "necklace_burnside: N_k(n) == (1/n) sum_{d|n} phi(d) k^(n/d)",
        "seed": SEED,
        "headline": {
            "n": HEADLINE_N, "k": HEADLINE_K,
            "N_exact": HEADLINE_N_EXACT, "k_pow_n": HEADLINE_KPOWN,
        },
        "gates": gates,
        "all_gates_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "PASS" if all_pass else "FAIL",
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
