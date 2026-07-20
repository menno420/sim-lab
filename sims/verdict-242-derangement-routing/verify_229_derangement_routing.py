#!/usr/bin/env python3
"""
Derangement-routing verifier -- PROPOSAL 229 (round-54 FLEET slot).

Claim: for a fleet of N agents assigned tasks by a uniformly-random permutation
routing (a random bijection giving each agent a distinct task), the probability
that NO agent is routed to its own "home" task equals the derangement ratio

    p_N = D_N / N! = sum_{k=0}^{N} (-1)^k / k!  ->  1/e   as N -> infinity.

Deterministic, stdlib-only (json, hashlib, math, random, fractions). SEED =
20260717. A single seeded RNG is consumed once, in the Monte-Carlo pass; the
same MC sample feeds both G2 (exact-model agreement) and G4 (naive-model
rejection). build_results() is a pure function of the seed and fixed constants;
main() runs it twice in-process and asserts byte-identical canonical JSON, and a
separate cross-invocation reproduces the same 64-hex digest.

Gates (each in its own direction, real teeth):
  G1  EXACT identity (fractions.Fraction), n=1..12. p_n computed TWO independent
      ways -- (a) subfactorial recurrence D_n=(n-1)(D_{n-1}+D_{n-2}) then
      p_n=Fraction(D_n,n!); (b) the alternating sum sum_{k=0}^n (-1)^k/k!. PASS
      iff the two Fractions are EXACTLY equal for every n.
  G2  Monte-Carlo agreement (N=7, T large): T seeded Fisher-Yates permutations,
      count derangements; z=(phat-p_7)/sqrt(p_7(1-p_7)/T). PASS iff |z|<3.
  G3  Invariant / robustness: exact (Fraction/int) D_n = n*D_{n-1}+(-1)^n over a
      range, 0<p_n<1 for n>=2, and p_n straddles 1/e with the correct
      alternating sign (p_even>1/e>p_odd). PASS iff all identities hold exactly.
  G4  Falsifiability: the naive independence model predicts q_N=(1-1/N)^N. Using
      the SAME MC sample at N=7, z_naive=(phat-q_7)/sqrt(q_7(1-q_7)/T). PASS iff
      the exact model is accepted (|z|<3 from G2) AND the naive model is
      rejected at large |z_naive| (>8).
"""
import json
import hashlib
import math
import random
from fractions import Fraction

SEED = 20260717

# Monte-Carlo world (fixed constants).
MC_N = 7
MC_T = 2_000_000
Z_ACCEPT = 3.0   # |z| below this => exact model agrees
Z_REJECT = 8.0   # |z_naive| above this => naive model rejected

# Gate ranges.
G1_NMAX = 12
G3_NMAX = 15
STRADDLE_NMAX = 12


def factorial(n):
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r


def subfactorial_recurrence(nmax):
    """D_0..D_nmax via D_n=(n-1)(D_{n-1}+D_{n-2}), D_0=1, D_1=0."""
    D = [1, 0]
    for n in range(2, nmax + 1):
        D.append((n - 1) * (D[n - 1] + D[n - 2]))
    return D


def alternating_sum(n):
    """sum_{k=0}^n (-1)^k / k! as an exact Fraction."""
    total = Fraction(0)
    for k in range(0, n + 1):
        total += Fraction((-1) ** k, factorial(k))
    return total


def inv_e_bounds(order):
    """Tight rational lower/upper bounds on 1/e from the alternating series.

    Partial sums of sum (-1)^k/k! bracket the limit: an odd cutoff sits below
    1/e, an even cutoff above it. Taking a large odd/even pair gives bounds far
    tighter than 1/n! for any n we test, so the straddle comparison is exact.
    """
    lo = alternating_sum(order | 1)          # odd cutoff -> below 1/e
    hi = alternating_sum((order | 1) + 1)    # even cutoff -> above 1/e
    return lo, hi


def gate1(D):
    """EXACT identity: Fraction(D_n, n!) == alternating sum, n=1..G1_NMAX."""
    rows = {}
    ok = True
    for n in range(1, G1_NMAX + 1):
        nf = factorial(n)
        p_from_D = Fraction(D[n], nf)
        p_from_sum = alternating_sum(n)
        eq = (p_from_D == p_from_sum)
        ok = ok and eq
        rows[str(n)] = {
            "D_n": D[n],
            "n_factorial": nf,
            "p_from_recurrence": str(p_from_D),
            "p_from_alt_sum": str(p_from_sum),
            "exactly_equal": eq,
        }
    return ok, rows


def gate2_gate4(rng):
    """One MC pass at N=MC_N; feeds both G2 (exact) and G4 (naive)."""
    n, T = MC_N, MC_T
    # Exact reference probabilities as Fractions, then floats for the z-tests.
    D = subfactorial_recurrence(n)
    p_exact_frac = Fraction(D[n], factorial(n))
    p_exact = float(p_exact_frac)
    q_naive = (1.0 - 1.0 / n) ** n          # naive independence model (6/7)^7

    # T seeded Fisher-Yates shuffles; count fixed-point-free permutations.
    base = list(range(n))
    derange = 0
    for _ in range(T):
        perm = base[:]
        for i in range(n - 1, 0, -1):
            j = rng.randint(0, i)
            perm[i], perm[j] = perm[j], perm[i]
        fixed = False
        for i in range(n):
            if perm[i] == i:
                fixed = True
                break
        if not fixed:
            derange += 1

    phat = derange / T

    se_exact = math.sqrt(p_exact * (1.0 - p_exact) / T)
    z_exact = (phat - p_exact) / se_exact

    se_naive = math.sqrt(q_naive * (1.0 - q_naive) / T)
    z_naive = (phat - q_naive) / se_naive

    g2_ok = abs(z_exact) < Z_ACCEPT
    g4_ok = g2_ok and (abs(z_naive) > Z_REJECT)

    g2 = {
        "N": n,
        "T": T,
        "derangements": derange,
        "phat": round(phat, 12),
        "p_exact": str(p_exact_frac),
        "p_exact_float": round(p_exact, 12),
        "z_exact": round(z_exact, 6),
        "z_accept": Z_ACCEPT,
        "pass": g2_ok,
    }
    g4 = {
        "N": n,
        "T": T,
        "q_naive_indep": round(q_naive, 12),
        "q_naive_formula": "(1-1/N)^N",
        "phat": round(phat, 12),
        "z_naive": round(z_naive, 6),
        "z_reject": Z_REJECT,
        "exact_accepted": g2_ok,
        "naive_rejected": abs(z_naive) > Z_REJECT,
        "pass": g4_ok,
    }
    return g2_ok, g2, g4_ok, g4


def gate3(D):
    """Exact invariants: second recurrence, 0<p_n<1, alternating straddle."""
    # (a) D_n = n*D_{n-1} + (-1)^n  (exact integers), n=1..G3_NMAX.
    rec2 = {}
    rec2_ok = True
    for n in range(1, G3_NMAX + 1):
        rhs = n * D[n - 1] + (-1) ** n
        eq = (D[n] == rhs)
        rec2_ok = rec2_ok and eq
        rec2[str(n)] = {"D_n": D[n], "n_Dnm1_plus_sign": rhs, "equal": eq}

    # (b) 0 < p_n < 1 exactly (Fraction), n=2..G3_NMAX  (p_1 = 0 is excluded).
    bounds_ok = True
    bounds = {}
    for n in range(2, G3_NMAX + 1):
        p = Fraction(D[n], factorial(n))
        ok = (Fraction(0) < p) and (p < Fraction(1))
        bounds_ok = bounds_ok and ok
        bounds[str(n)] = {"p_n": str(p), "in_open_unit": ok}

    # (c) straddle: sign(p_n - 1/e) = +1 (n even) / -1 (n odd), via tight
    #     rational bounds lo < 1/e < hi. Checked exactly with Fractions.
    lo, hi = inv_e_bounds(40)
    straddle = {}
    straddle_ok = True
    for n in range(2, STRADDLE_NMAX + 1):
        p = Fraction(D[n], factorial(n))
        if n % 2 == 0:
            ok = p > hi           # even partial sum strictly above 1/e
            side = "above"
        else:
            ok = p < lo           # odd partial sum strictly below 1/e
            side = "below"
        straddle_ok = straddle_ok and ok
        straddle[str(n)] = {"p_n": str(p), "expected_side": side, "ok": ok}

    ok = rec2_ok and bounds_ok and straddle_ok
    return ok, {
        "second_recurrence_Dn_eq_n_Dnm1_plus_sign": rec2,
        "second_recurrence_all_exact": rec2_ok,
        "p_n_in_open_unit_interval": bounds,
        "p_n_bounds_all_ok": bounds_ok,
        "inv_e_lower_bound": str(lo),
        "inv_e_upper_bound": str(hi),
        "straddle_alternating_sign": straddle,
        "straddle_all_ok": straddle_ok,
        "pass": ok,
    }


def build_results():
    rng = random.Random(SEED)
    D = subfactorial_recurrence(max(G1_NMAX, G3_NMAX))

    g1_ok, g1 = gate1(D)
    # G2 and G4 share one MC pass (the only RNG consumer).
    g2_ok, g2, g4_ok, g4 = gate2_gate4(rng)
    g3_ok, g3 = gate3(D)

    all_pass = g1_ok and g2_ok and g3_ok and g4_ok
    first_failing = None
    for name, ok in (("G1", g1_ok), ("G2", g2_ok), ("G3", g3_ok), ("G4", g4_ok)):
        if not ok:
            first_failing = name
            break

    return {
        "seed": SEED,
        "claim": "P(no agent routed to its home task) = D_N/N! = sum (-1)^k/k! -> 1/e",
        "G1_exact_identity_two_routes": g1,
        "G2_monte_carlo_agreement": g2,
        "G3_invariants_and_straddle": g3,
        "G4_falsifiability_naive_independence": g4,
        "gates": {"G1": g1_ok, "G2": g2_ok, "G3": g3_ok, "G4": g4_ok},
        "all_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "sim-ready" if all_pass else "needs-more-grooming",
    }


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def main():
    r1 = build_results()
    r2 = build_results()
    c1 = canonical(r1)
    c2 = canonical(r2)
    assert c1 == c2, "NON-DETERMINISTIC: in-process double-run diverged"
    digest = hashlib.sha256(c1.encode("utf-8")).hexdigest()
    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    print("in_process_double_run: IDENTICAL")
    print("results_sha256: " + digest)
    print("decision: " + r1["decision"])
    if not r1["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
