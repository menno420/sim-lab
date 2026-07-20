"""100 prisoners problem — cycle-following strategy survival ~31%, not 2^-100.

Head: 100 prisoners each open 50 of 100 boxes holding a random permutation of
their numbers. Independent guessing gives group survival (1/2)^100 ~ 8e-31. The
cycle-following strategy (open your own number, then follow the chain) makes the
whole group survive iff the permutation has no cycle longer than 50 -- probability
exactly 1 - (H_100 - H_50) ~ 0.31183, bounded below by 1 - ln 2 ~ 0.30685 for
every even N. Sounds impossible; exactly true.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. The compact-canonical
sha256 (sort_keys=True, separators=(",",":")) over the results dict IS the digest;
the dict carries no self-referential field; pretty dump to stdout; floats rounded
6 dp; no on-disk JSON. SEED=20260717; in-process double-run asserts byte-identical;
gates use Z_GATE=3.0.
"""
import hashlib
import json
import math
import random
from fractions import Fraction
from itertools import permutations

SEED = 20260717
Z_GATE = 3.0

# Pinned world
N_MAIN = 100                              # prisoners / boxes
OPEN_MAIN = 50                           # boxes each prisoner may open (N/2)
M_TRIALS = 200000                        # Monte-Carlo permutations for G1
N_ENUM = 8                               # exhaustive-enumeration size (opens 4)
N_SHIFT = (100, 300, 1000, 3000, 10000)  # robustness/shift sweep


def harmonic_exact(n):
    """Exact rational H_n = sum_{k=1..n} 1/k."""
    total = Fraction(0)
    for k in range(1, n + 1):
        total += Fraction(1, k)
    return total


def survival_exact(n):
    """Exact P(group survives) = 1 - (H_n - H_{n//2}) as a Fraction."""
    return Fraction(1) - (harmonic_exact(n) - harmonic_exact(n // 2))


def survival_float(n):
    """Float P(group survives); cheap for large n (no big-int Fraction sums)."""
    half = n // 2
    return 1.0 - sum(1.0 / k for k in range(half + 1, n + 1))


def longest_cycle(perm):
    """Longest cycle length of a permutation perm with perm[i] in 0..n-1."""
    n = len(perm)
    seen = [False] * n
    longest = 0
    for start in range(n):
        if seen[start]:
            continue
        length = 0
        j = start
        while not seen[j]:
            seen[j] = True
            j = perm[j]
            length += 1
        if length > longest:
            longest = length
    return longest


def simulate_survival(n, opens, trials, rng):
    """Fraction of trials where the cycle strategy saves everyone.

    Everyone survives iff the permutation's longest cycle <= opens (following the
    chain from box i visits exactly the cycle containing i).
    """
    base = list(range(n))
    survivors = 0
    for _ in range(trials):
        perm = base[:]
        rng.shuffle(perm)
        if longest_cycle(perm) <= opens:
            survivors += 1
    return survivors / trials


def enumerate_survival(n, opens):
    """Exact survival fraction by exhaustive enumeration over all n! permutations."""
    good = 0
    total = 0
    for perm in permutations(range(n)):
        total += 1
        if longest_cycle(perm) <= opens:
            good += 1
    return Fraction(good, total)


def run():
    rng = random.Random(SEED)

    # G1: Monte-Carlo agreement with the closed form (>= 3 sigma).
    p_star = float(survival_exact(N_MAIN))
    p_hat = simulate_survival(N_MAIN, OPEN_MAIN, M_TRIALS, rng)
    se = math.sqrt(p_star * (1 - p_star) / M_TRIALS)
    z1 = abs(p_hat - p_star) / se
    g1_pass = z1 < Z_GATE

    # G2: exactly-true -- exhaustive enumeration == closed form (exact rational).
    enum_frac = enumerate_survival(N_ENUM, N_ENUM // 2)
    cf_frac = survival_exact(N_ENUM)
    g2_pass = (enum_frac == cf_frac)

    # G3: robustness/shift -- closed form stable, bounded away from 0, crushes naive.
    sweep = {n: survival_float(n) for n in N_SHIFT}
    vals = list(sweep.values())
    ln2_floor = 1.0 - math.log(2)
    spread = max(vals) - min(vals)
    naive_log10 = N_MAIN * math.log10(0.5)
    log10_advantage = math.log10(sweep[N_MAIN]) - naive_log10
    g3_pass = (spread < 0.01) and (min(vals) > ln2_floor) and (max(vals) < 0.32) and (log10_advantage > 25)

    results = {
        "head": "hundred-prisoners-cycle-strategy",
        "seed": SEED,
        "world": {
            "n_main": N_MAIN,
            "open_main": OPEN_MAIN,
            "m_trials": M_TRIALS,
            "n_enum": N_ENUM,
            "n_shift": list(N_SHIFT),
            "z_gate": Z_GATE,
        },
        "g1_montecarlo_vs_closedform": {
            "p_closed_form": round(p_star, 6),
            "p_hat": round(p_hat, 6),
            "std_error": round(se, 6),
            "z": round(z1, 6),
            "pass": g1_pass,
        },
        "g2_exactly_true_enumeration": {
            "n": N_ENUM,
            "opens": N_ENUM // 2,
            "enum_numerator": enum_frac.numerator,
            "enum_denominator": enum_frac.denominator,
            "closed_form_numerator": cf_frac.numerator,
            "closed_form_denominator": cf_frac.denominator,
            "value": round(float(enum_frac), 6),
            "exact_match": g2_pass,
            "pass": g2_pass,
        },
        "g3_robustness_shift": {
            "sweep": {str(n): round(v, 6) for n, v in sweep.items()},
            "spread": round(spread, 6),
            "ln2_floor": round(ln2_floor, 6),
            "naive_survival_log10": round(naive_log10, 6),
            "log10_advantage_over_naive": round(log10_advantage, 6),
            "pass": g3_pass,
        },
    }
    results["all_pass"] = g1_pass and g2_pass and g3_pass
    return results


def main():
    r1 = run()
    r2 = run()
    assert r1 == r2, "non-deterministic results dict"
    blob = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(blob.encode()).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    raise SystemExit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
