#!/usr/bin/env python3
"""
Hat-check invariance verifier -- PROPOSAL 204 (round-48 UNRELATED slot).

Claim: for a uniform random permutation of n items, the number of fixed points
(patrons who get their own coat back) has mean EXACTLY 1 for every n>=1 and
variance EXACTLY 1 for every n>=2; the probability of zero fixed points (a
derangement) is D_n/n! = sum_{k=0}^n (-1)^k / k!  ->  1/e; and the whole
fixed-point count converges to Poisson(1).

Deterministic, stdlib-only. SEED = 20260717. One seeded RNG is consumed in
gate order G2 -> G3 -> G4. An in-process double-run reproduces the identical
results-dict sha256, and a separate cross-invocation reproduces it too.

Gates:
  G1  EXACT (Fraction, exhaustive enumeration, n=1..8): E==1, Var==1 (n>=2),
      brute D_n == inclusion-exclusion == recurrence. Direction: every
      identity exact; any mismatch => FAIL.
  G2  >=3 sigma derangement floor (n=200): empirical P(no fixed point) clears
      the folk "essentially never" floor 0.30 by z_floor>=3 and sits within
      3 sigma of 1/e. Direction: one-sided up past the floor + |z|<3 vs 1/e.
  G3  n-invariance / robustness-shift (n in {10,100,1000,2000}): cross-scale
      range of mean fixed points < 0.05 and every mean within 0.05 of 1.
      Direction: the mean does NOT move with crowd size.
  G4  Poisson(1) shape (n=100): Pearson chi-square (df=4, buckets k=0,1,2,3,>=4)
      below the alpha=0.001 critical value 18.467 => fit not rejected.
      Direction: chi2 < crit => the limiting shape holds.
"""
import json
import hashlib
import math
import random
from fractions import Fraction
from itertools import permutations

SEED = 20260717


def factorial(n):
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r


def derangements_recurrence(n):
    if n == 0:
        return 1
    if n == 1:
        return 0
    dm2, dm1 = 1, 0
    for k in range(2, n + 1):
        dm2, dm1 = dm1, (k - 1) * (dm1 + dm2)
    return dm1


def derangements_incexc(n):
    total = Fraction(0)
    for k in range(0, n + 1):
        total += Fraction((-1) ** k, factorial(k))
    val = total * factorial(n)
    assert val.denominator == 1
    return val.numerator


def enumerate_exact(n):
    total_fixed = 0
    total_fixed_sq = 0
    derange = 0
    for p in permutations(range(n)):
        f = 0
        for i in range(n):
            if p[i] == i:
                f += 1
        total_fixed += f
        total_fixed_sq += f * f
        if f == 0:
            derange += 1
    nf = factorial(n)
    E = Fraction(total_fixed, nf)
    E2 = Fraction(total_fixed_sq, nf)
    Var = E2 - E * E
    return E, Var, derange, nf


def count_fixed(rng, n):
    perm = list(range(n))
    rng.shuffle(perm)
    c = 0
    for i in range(n):
        if perm[i] == i:
            c += 1
    return c


def gate1():
    rows = {}
    ok = True
    for n in range(1, 9):
        E, Var, derange, nf = enumerate_exact(n)
        d_ie = derangements_incexc(n)
        d_rec = derangements_recurrence(n)
        e_ok = (E == 1)
        var_ok = (Var == 1) if n >= 2 else (Var == 0)
        d_ok = (derange == d_ie == d_rec)
        ok = ok and e_ok and var_ok and d_ok
        rows[str(n)] = {
            "E": str(E),
            "Var": str(Var),
            "D_n_brute": derange,
            "D_n_incexc": d_ie,
            "D_n_recur": d_rec,
            "p_derange": str(Fraction(derange, nf)),
            "E_eq_1": e_ok,
            "Var_ok": var_ok,
            "D_all_agree": d_ok,
        }
    return ok, rows


def gate2(rng):
    n, M = 200, 80000
    d = 0
    for _ in range(M):
        if count_fixed(rng, n) == 0:
            d += 1
    phat = d / M
    floor = 0.30
    se = math.sqrt(phat * (1.0 - phat) / M)
    z_floor = (phat - floor) / se
    inv_e = math.exp(-1.0)
    z_inv_e = (phat - inv_e) / se
    ok = (z_floor >= 3.0) and (abs(z_inv_e) < 3.0)
    return ok, {
        "n": n, "M": M,
        "p_derange": round(phat, 10),
        "folk_floor": floor,
        "z_floor": round(z_floor, 6),
        "inv_e": round(inv_e, 10),
        "z_inv_e": round(z_inv_e, 6),
        "pass": ok,
    }


def gate3(rng):
    plan = [(10, 80000), (100, 80000), (1000, 40000), (2000, 25000)]
    means = {}
    zs = {}
    for n, M in plan:
        s = 0
        for _ in range(M):
            s += count_fixed(rng, n)
        m = s / M
        means[str(n)] = round(m, 10)
        se = math.sqrt(1.0 / M)
        zs[str(n)] = round((m - 1.0) / se, 6)
    vals = [means[str(n)] for n, _ in plan]
    rng_range = max(vals) - min(vals)
    ok = (rng_range < 0.05) and all(abs(v - 1.0) < 0.05 for v in vals)
    return ok, {
        "plan": [[n, M] for n, M in plan],
        "means": means,
        "z_vs_1": zs,
        "range": round(rng_range, 10),
        "pass": ok,
    }


def gate4(rng):
    n, M = 100, 80000
    counts = [0, 0, 0, 0, 0]
    for _ in range(M):
        f = count_fixed(rng, n)
        counts[f if f < 4 else 4] += 1
    probs = [math.exp(-1.0) / factorial(k) for k in range(4)]
    probs.append(1.0 - sum(probs))
    expected = [M * p for p in probs]
    chi2 = sum((counts[i] - expected[i]) ** 2 / expected[i] for i in range(5))
    crit = 18.467
    ok = chi2 < crit
    return ok, {
        "n": n, "M": M,
        "buckets": "k=0,1,2,3,>=4",
        "counts": counts,
        "expected": [round(e, 4) for e in expected],
        "chi2": round(chi2, 6),
        "df": 4,
        "crit_0p001": crit,
        "pass": ok,
    }


def compute():
    rng = random.Random(SEED)
    g1_ok, g1 = gate1()
    g2_ok, g2 = gate2(rng)
    g3_ok, g3 = gate3(rng)
    g4_ok, g4 = gate4(rng)
    return {
        "seed": SEED,
        "G1_exact_enumeration": g1,
        "G2_derangement_floor": g2,
        "G3_n_invariance": g3,
        "G4_poisson1_shape": g4,
        "gates": {"G1": g1_ok, "G2": g2_ok, "G3": g3_ok, "G4": g4_ok},
        "decision": "sim-ready" if (g1_ok and g2_ok and g3_ok and g4_ok) else "needs-more-grooming",
    }


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def main():
    r1 = compute()
    r2 = compute()
    c1 = canonical(r1)
    c2 = canonical(r2)
    assert c1 == c2, "NON-DETERMINISTIC: in-process double-run diverged"
    digest = hashlib.sha256(c1.encode("utf-8")).hexdigest()
    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    print("in_process_double_run: IDENTICAL")
    print("results_sha256: " + digest)
    print("decision: " + r1["decision"])


if __name__ == "__main__":
    main()
