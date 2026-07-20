#!/usr/bin/env python3
"""
Coprime-density verifier -- PROPOSAL 232 (cross-cutting FLEET slot).

Claim: for two integers drawn independently and uniformly from {1,...,N}, the
probability that they are coprime is the exact Moebius-inversion density

    Q(N) = (1/N^2) * sum_{k=1}^{N} mu(k) * floor(N/k)^2

and Q(N) -> 6/pi^2 = 1/zeta(2) ~= 0.6079271018540267 as N -> infinity -- the
number-theoretic coprime density, NOT the plausible-but-wrong "just avoid a
shared factor of 2 => 3/4" value.

Deterministic, stdlib-only (json, hashlib, math, random, fractions). SEED =
20260717. A single seeded RNG is consumed once, in the Monte-Carlo pass; the
SAME MC sample feeds both G2 (exact-density agreement) and G4 (naive-3/4
rejection). build_results() is a pure function of the seed and fixed constants;
main() runs it twice in-process and asserts byte-identical canonical JSON, and a
separate cross-invocation reproduces the same 64-hex digest.

Gates (each in its own direction, real teeth):
  G1  EXACT identity (integers / fractions.Fraction). For every N in a test set
      (small N in {1,2,3,4,5,6} and larger N in {10,50,100,200}), two INDEPENDENT
      routes must agree exactly:
        Route A (brute force):  A(N) = #{(a,b) in [1,N]^2 : gcd(a,b) == 1}.
        Route B (Moebius):      B(N) = sum_{k=1}^{N} mu(k) * (N//k)^2, mu from a
                                simple sieve.
      PASS iff A(N) == B(N) (int equality) AND Fraction(A,N^2) == Fraction(B,N^2)
      == Q(N) for every N. Reports Q(6) as a reduced Fraction.
  G2  Monte-Carlo agreement at N=10000, M=200000, |z| < Z_ACCEPT=3.0. Q_N =
      Fraction(B(N), N^2) exactly; phat = coprime_count/M; z = (phat -
      float(Q_N)) / sqrt(float(Q_N)*(1-float(Q_N))/M). PASS iff |z| < 3.
  G3  EXACT invariance / robustness: the partition identity
      sum_{d=1}^{N} A(floor(N/d)) == N^2 (every pair has a unique gcd d; pairs of
      gcd exactly d <-> coprime pairs in [1,floor(N/d)]^2), checked as EXACT
      integer equality for every N in {1,2,3,10,20,50,100,200} with A computed via
      the Moebius route; plus 0 < Q(N) < 1 for all tested N. PASS iff the
      partition identity holds exactly for all N and every Q(N) is in the open
      unit interval.
  G4  FALSIFIABILITY: reject the naive "only avoid a shared factor of 2 =>
      P(coprime) = 3/4" hypothesis at |z_naive| >= Z_REJECT=8.0. Using the SAME MC
      sample from G2, z_naive = (phat - 0.75) / sqrt(0.75*0.25/M). PASS iff the
      exact density is accepted (G2) AND the 3/4 fallacy is rejected (|z_naive| >=
      8). The 2-only fallacy predicts 0.75; the true density is 6/pi^2 ~= 0.6079.
"""
import json
import hashlib
import math
import random
from fractions import Fraction

SEED = 20260717

# Monte-Carlo world (fixed constants).
MC_N = 10000
MC_M = 200000
Z_ACCEPT = 3.0     # |z| below this => exact density agrees
Z_REJECT = 8.0     # |z_naive| at/above this => naive 3/4 rejected
NAIVE_P = 0.75     # the plausible-but-wrong "avoid a shared factor of 2" value

# Asymptotic target (reported, not gated -- it is irrational).
INV_ZETA2 = 6.0 / (math.pi ** 2)   # 6/pi^2 = 1/zeta(2) ~= 0.6079271018540267

# Exact-gate test sets.
G1_NS = [1, 2, 3, 4, 5, 6, 10, 50, 100, 200]
G3_NS = [1, 2, 3, 10, 20, 50, 100, 200]


def mobius_sieve(n):
    """mu[0..n] via a simple sieve; mu[0] unused (set to 0)."""
    mu = [1] * (n + 1)
    mu[0] = 0
    is_prime = [True] * (n + 1)
    for i in range(2, n + 1):
        if is_prime[i]:
            for j in range(i, n + 1, i):
                if j > i:
                    is_prime[j] = False
                mu[j] *= -1
            sq = i * i
            for j in range(sq, n + 1, sq):
                mu[j] = 0
    return mu


def brute_coprime_count(N):
    """Route A: A(N) = #{(a,b) in [1,N]^2 : gcd(a,b) == 1}."""
    count = 0
    for a in range(1, N + 1):
        for b in range(1, N + 1):
            if math.gcd(a, b) == 1:
                count += 1
    return count


def mobius_coprime_count(N, mu):
    """Route B: B(N) = sum_{k=1}^{N} mu(k) * (N//k)^2."""
    total = 0
    for k in range(1, N + 1):
        m = mu[k]
        if m:
            total += m * (N // k) ** 2
    return total


def gate1(mu):
    """EXACT identity: brute A(N) == Moebius B(N), and equal densities."""
    rows = {}
    ok = True
    for N in G1_NS:
        a = brute_coprime_count(N)
        b = mobius_coprime_count(N, mu)
        n2 = N * N
        qa = Fraction(a, n2)
        qb = Fraction(b, n2)
        eq_int = (a == b)
        eq_frac = (qa == qb)
        ok = ok and eq_int and eq_frac
        rows[str(N)] = {
            "A_brute": a,
            "B_mobius": b,
            "N_squared": n2,
            "Q_from_brute": str(qa),
            "Q_from_mobius": str(qb),
            "counts_equal": eq_int,
            "densities_equal": eq_frac,
        }
    return ok, {
        "routes": rows,
        "Q6_reduced_fraction": str(Fraction(brute_coprime_count(6), 36)),
        "pass": ok,
    }


def gate2_gate4(rng, mu):
    """One MC pass at N=MC_N; feeds both G2 (exact) and G4 (naive 3/4)."""
    N, M = MC_N, MC_M
    q_frac = Fraction(mobius_coprime_count(N, mu), N * N)
    q = float(q_frac)

    coprime = 0
    for _ in range(M):
        a = rng.randint(1, N)
        b = rng.randint(1, N)
        if math.gcd(a, b) == 1:
            coprime += 1
    phat = coprime / M

    se_exact = math.sqrt(q * (1.0 - q) / M)
    z_exact = (phat - q) / se_exact

    se_naive = math.sqrt(NAIVE_P * (1.0 - NAIVE_P) / M)
    z_naive = (phat - NAIVE_P) / se_naive

    g2_ok = abs(z_exact) < Z_ACCEPT
    g4_ok = g2_ok and (abs(z_naive) >= Z_REJECT)

    g2 = {
        "N": N,
        "M": M,
        "coprime_count": coprime,
        "phat": round(phat, 12),
        "Q_N_exact": str(q_frac),
        "Q_N_float": round(q, 12),
        "asymptotic_6_over_pi2": round(INV_ZETA2, 16),
        "z_agreement": round(z_exact, 6),
        "z_accept": Z_ACCEPT,
        "pass": g2_ok,
    }
    g4 = {
        "N": N,
        "M": M,
        "naive_hypothesis": "avoid a shared factor of 2 => P(coprime)=3/4",
        "naive_p": NAIVE_P,
        "true_density_6_over_pi2": round(INV_ZETA2, 16),
        "phat": round(phat, 12),
        "z_naive": round(z_naive, 6),
        "z_reject": Z_REJECT,
        "exact_accepted": g2_ok,
        "naive_rejected": abs(z_naive) >= Z_REJECT,
        "pass": g4_ok,
    }
    return g2_ok, g2, g4_ok, g4


def gate3(mu):
    """EXACT invariant: partition identity sum_d A(floor(N/d)) == N^2."""
    rows = {}
    partition_ok = True
    bounds_ok = True
    bounds = {}
    for N in G3_NS:
        total = 0
        for d in range(1, N + 1):
            total += mobius_coprime_count(N // d, mu)
        n2 = N * N
        eq = (total == n2)
        partition_ok = partition_ok and eq
        rows[str(N)] = {
            "sum_A_floor_N_over_d": total,
            "N_squared": n2,
            "equal": eq,
        }
        q = Fraction(mobius_coprime_count(N, mu), n2)
        if N == 1:
            # Degenerate single-pair world: the only pair (1,1) is coprime, so
            # Q(1)=1 sits on the boundary; the open-interval teeth apply for N>=2.
            in_unit = (q == Fraction(1))
            bounds[str(N)] = {"Q_N": str(q), "boundary_degenerate_eq_1": in_unit}
        else:
            in_unit = (Fraction(0) < q) and (q < Fraction(1))
            bounds_ok = bounds_ok and in_unit
            bounds[str(N)] = {"Q_N": str(q), "in_open_unit": in_unit}

    ok = partition_ok and bounds_ok
    return ok, {
        "partition_identity_sum_A_eq_N_squared": rows,
        "partition_all_exact": partition_ok,
        "Q_N_in_open_unit_interval": bounds,
        "Q_bounds_all_ok": bounds_ok,
        "pass": ok,
    }


def build_results():
    rng = random.Random(SEED)
    mu = mobius_sieve(MC_N)

    g1_ok, g1 = gate1(mu)
    # G2 and G4 share one MC pass (the only RNG consumer).
    g2_ok, g2, g4_ok, g4 = gate2_gate4(rng, mu)
    g3_ok, g3 = gate3(mu)

    all_pass = g1_ok and g2_ok and g3_ok and g4_ok
    first_failing = None
    for name, ok in (("G1", g1_ok), ("G2", g2_ok), ("G3", g3_ok), ("G4", g4_ok)):
        if not ok:
            first_failing = name
            break

    return {
        "seed": SEED,
        "claim": "P(two uniform integers in [1,N] coprime) = (1/N^2) sum mu(k) floor(N/k)^2 -> 6/pi^2 = 1/zeta(2)",
        "G1_exact_identity_two_routes": g1,
        "G2_monte_carlo_agreement": g2,
        "G3_partition_invariant": g3,
        "G4_falsifiability_naive_three_quarters": g4,
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
