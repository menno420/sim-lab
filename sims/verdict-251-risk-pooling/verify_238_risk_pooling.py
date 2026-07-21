#!/usr/bin/env python3
"""PROPOSAL 238 verifier - the insurance risk-pooling variance law.

Setup: a mutual pool of n members, each member's annual loss is an independent
Bernoulli(p) unit claim (loss 1 with probability p, else 0). The pooled
per-member cost is L_bar = S / n where S = sum of the n losses ~ Binomial(n, p).

Exact claim (the diversification / insurance principle):
    E[L_bar]   = p                 -> the fair premium is scale-free in n
    Var[L_bar] = p*(1-p) / n       -> per-member risk falls as 1/sqrt(n)

Headline (p = 1/10): a single member's cost sd is sqrt(0.09) = 0.3; pooling
n = 100 independent members cuts it to 0.3 / 10 = 0.03, an exact sqrt(n) = 10x
reduction, with the mean premium unchanged at p = 0.1.

Naive foil (falsified): the comonotonic belief that pooling gives no benefit,
Var[L_bar] = p*(1-p) for every n (the perfectly correlated rho = 1 limit).

Four gates, each in its own direction:
  G1 EXACT          - Var[L_bar] computed two independent ways (closed form vs
                      full-pmf reconstruction), fractions.Fraction, must be EQUAL.
  G2 MC agreement   - empirical mean cost and empirical Var[L_bar] agree with
                      the closed form at |z| < 3 (Z_ACCEPT = 3.0).
  G3 invariance     - (i) Var[L_bar]*n == p(1-p) across n in {1,10,100,1000};
                      (ii) coefficient of variation independent of severity.
  G4 falsifiability - the naive comonotonic variance p(1-p) is REJECTED by the
                      independent pool's empirical Var[L_bar] at |z| >= 8
                      (Z_REJECT = 8.0).

Stdlib only (json, hashlib, math, random, fractions). SEED fixed. Deterministic:
in-process double run and separate re-invocation are byte-identical; the sha256
of the results dict is disclosed in full.
"""

import json
import math
import random
import hashlib
from fractions import Fraction
from math import comb

SEED = 20260717
Z_ACCEPT = 3.0
Z_REJECT = 8.0

P = Fraction(1, 10)     # claim probability
N_POOL = 100            # headline pool size
M_POOLS = 100_000       # number of independent Monte-Carlo pools
SEVERITY = 5            # claim severity for the G3(ii) scale-invariance check
INV_NS = (1, 10, 100, 1000)


def exact_var_direct(p, n):
    """Route A - closed form: Var(S/n) = Var(S)/n^2, Var(S) = n p (1-p)."""
    return (n * p * (1 - p)) / (n * n)


def exact_var_pmf(p, n):
    """Route B - reconstruct Var(S/n) = E[(S/n)^2] - (E[S/n])^2 from the full
    binomial pmf, summing k = 0..n as exact Fractions."""
    q = 1 - p
    e_x = Fraction(0)
    e_x2 = Fraction(0)
    total = Fraction(0)
    for k in range(n + 1):
        pk = comb(n, k) * (p ** k) * (q ** (n - k))
        total += pk
        x = Fraction(k, n)
        e_x += x * pk
        e_x2 += x * x * pk
    assert total == 1, "pmf must sum to exactly 1"
    return e_x2 - e_x * e_x


def coeff_var_sq(p, n, severity):
    """Exact CV^2 of the per-member pooled cost at a given claim severity:
    Var(c*L_bar)/E[c*L_bar]^2 = c^2 Var(L_bar)/(c^2 p^2) = (1-p)/(p n)."""
    mean = severity * p
    var = (severity ** 2) * exact_var_direct(p, n)
    return var / (mean * mean)


def simulate(p_float, n, m, rng):
    """m independent pools; return (mean L_bar, mean (L_bar-p)^2,
    sd of L_bar samples, sd of (L_bar-p)^2 samples)."""
    lbars = []
    us = []
    for _ in range(m):
        s = 0
        for _ in range(n):
            if rng.random() < p_float:
                s += 1
        lbar = s / n
        lbars.append(lbar)
        us.append((lbar - p_float) ** 2)
    mean_lbar = sum(lbars) / m
    mean_u = sum(us) / m
    var_lbar = sum((x - mean_lbar) ** 2 for x in lbars) / (m - 1)
    var_u = sum((x - mean_u) ** 2 for x in us) / (m - 1)
    return mean_lbar, mean_u, math.sqrt(var_lbar), math.sqrt(var_u)


def zscore(estimate, hypothesis, sample_sd, m):
    se = sample_sd / math.sqrt(m)
    return (estimate - hypothesis) / se


def compute():
    rng = random.Random(SEED)
    p_float = float(P)

    var_direct = exact_var_direct(P, N_POOL)
    var_pmf = exact_var_pmf(P, N_POOL)
    var_theory = var_direct
    var_naive = P * (1 - P)
    sd_single = math.sqrt(float(var_naive))
    sd_pooled = math.sqrt(float(var_theory))

    # G1 - two independent exact routes must be EQUAL
    g1_pass = (var_direct == var_pmf == Fraction(9, 10000))

    # G2 - Monte-Carlo agreement, |z| < 3
    mean_lbar, mean_u, sd_lbar, sd_u = simulate(p_float, N_POOL, M_POOLS, rng)
    z_mean = zscore(mean_lbar, p_float, sd_lbar, M_POOLS)
    z_var = zscore(mean_u, float(var_theory), sd_u, M_POOLS)
    g2_metric = max(abs(z_mean), abs(z_var))
    g2_pass = g2_metric < Z_ACCEPT

    # G3 - invariance
    g3i_pass = all(exact_var_direct(P, n) * n == var_naive for n in INV_NS)
    cv_sq_c1 = coeff_var_sq(P, N_POOL, 1)
    cv_sq_c5 = coeff_var_sq(P, N_POOL, SEVERITY)
    g3ii_pass = (cv_sq_c1 == cv_sq_c5 == (1 - P) / (P * N_POOL))
    g3_pass = g3i_pass and g3ii_pass

    # G4 - falsifiability: reject naive comonotonic variance at |z| >= 8
    z_naive = zscore(mean_u, float(var_naive), sd_u, M_POOLS)
    g4_pass = abs(z_naive) >= Z_REJECT

    gates = {"G1": g1_pass, "G2": g2_pass, "G3": g3_pass, "G4": g4_pass}
    all_pass = all(gates.values())
    first_fail = next((g for g in ("G1", "G2", "G3", "G4") if not gates[g]), None)

    return {
        "proposal": 238,
        "claim": "pooled per-member cost Var = p(1-p)/n, mean = p (insurance risk-pooling law)",
        "seed": SEED,
        "params": {"p": "1/10", "n_pool": N_POOL, "m_pools": M_POOLS,
                   "severity": SEVERITY, "inv_ns": list(INV_NS)},
        "exact": {
            "var_theory": str(var_theory),
            "var_route_A_direct": str(var_direct),
            "var_route_B_pmf": str(var_pmf),
            "var_naive_comonotonic": str(var_naive),
            "sd_single_member": round(sd_single, 6),
            "sd_pooled_n100": round(sd_pooled, 6),
            "sqrt_n_reduction": round(sd_single / sd_pooled, 6),
            "cv_sq": str(cv_sq_c1),
        },
        "monte_carlo": {
            "mean_lbar": round(mean_lbar, 6),
            "mean_u_est_var": round(mean_u, 8),
            "z_mean_vs_p": round(z_mean, 4),
            "z_var_vs_theory": round(z_var, 4),
            "g2_metric_maxabs_z": round(g2_metric, 4),
        },
        "gates": {
            "G1_exact_two_routes_equal": g1_pass,
            "G2_mc_agreement_absz_lt_3": g2_pass,
            "G3_invariance_sigma2_over_n_and_cv_scale": g3_pass,
            "G4_falsify_comonotonic_absz_ge_8": g4_pass,
            "z_naive_reject": round(z_naive, 2),
        },
        "all_gates_pass": all_pass,
        "first_failing_gate": first_fail,
    }


def digest(results):
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main():
    r1 = compute()
    r2 = compute()
    d1 = digest(r1)
    d2 = digest(r2)
    assert d1 == d2, "in-process double run not byte-identical"
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("results_sha256=" + d1)
    print("all_gates_pass=" + str(r1["all_gates_pass"]))
    print("first_failing_gate=" + str(r1["first_failing_gate"]))


if __name__ == "__main__":
    main()
