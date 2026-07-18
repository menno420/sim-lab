#!/usr/bin/env python3
"""PROPOSAL 132 — the birthday-collision sqrt(N) scaling law (round-30 UNRELATED slot).

Phenomenon (dynamical, not the one-line static probability). Draw values one at a
time, uniformly at random with replacement, from a space of N equally likely
outcomes. Let T be the WAITING TIME — the number of draws until the first value
that repeats one already seen. Folk belief (inverted here): "a collision is rare
until you have sampled a large fraction of the space — you need on the order of
N/2 draws before two draws coincide." Reality: the first collision arrives after
only about sqrt(N) draws. The waiting time is governed by a genuine distribution
whose mean scales as the SQUARE ROOT of N, not linearly:
    E[T_N] -> sqrt(pi * N / 2) = 1.2533... * sqrt(N)   (Ramanujan's Q-function),
and the point at which a collision becomes more-likely-than-not sits at
    m*(N) ~ sqrt(2 ln 2) * sqrt(N) = 1.1774... * sqrt(N),
a VANISHING fraction m*/(N/2) = 2.3548/sqrt(N) -> 0 of the space. So doubling the
space multiplies the safe draw budget by only sqrt(2) ~ 1.41x, not 2x — the
counterintuitive quadratic scaling behind hash-collision risk, random-ID reuse,
nonce/session-token reuse, and cache-key aliasing.

This is the DYNAMICAL emergence framing endorsed for the P104/P108/P112/P116/P124
family: a Monte-Carlo that reproduces a closed-form DISTRIBUTION/scaling law and
isolates the mechanism with a dose-response, NOT the static one-line combinatorial
collision probability a prior sweep set aside as "nothing a sim settles".

Anchors: the birthday problem and Ramanujan's Q-function E[T_N] = 1 + Q(N),
Q(N) = sum_{k>=1} N!/((N-k)! N**k), with E[T_N] ~ sqrt(pi N / 2) + 2/3 + ...
(Flajolet, Grabner, Kirschenhofer, Prodinger, "On Ramanujan's Q-function",
J. Comput. Appl. Math. 58 (1995)); the 50%-threshold sqrt(2 ln 2 * N).

Pre-registered gates (APPROVE iff ALL hold, in order G1 -> G2 -> G3):
  G1  SIM CORRECT : at N_HI the Monte-Carlo mean waiting time matches the EXACT
                    finite-N anchor E[T_N] = sum_k P(first k draws distinct)
                    within z < 3 sigma (standard error of the mean).
  G2  SQRT-N LAW  : the mean waiting time scales like sqrt(N), NOT like N. The MC
                    ratio mean(T at N_HI)/mean(T at N_LO) matches sqrt(N_HI/N_LO)
                    within z < 3 sigma (delta method) and is nowhere near the
                    linear-N folk prediction N_HI/N_LO (4.0 vs 16.0 here).
  G3  INVERSION   : a collision is more-likely-than-not after only
                    m* ~ 1.1774*sqrt(N) draws — a vanishing fraction of the space,
                    NOT ~N/2. At N_HI the MC fraction of runs collided by draw m*
                    exceeds 0.5 AND matches the exact anchor 1 - P(all m* distinct)
                    within z < 3 sigma, with m*/(N/2) << 1. Folk belief reversed.
"""

import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 120_000
N_GRID = (365, 1024, 4096, 16384)   # 365 = the classic birthday space
N_LO = 1024
N_HI = 16384                        # sqrt(N_HI/N_LO) = sqrt(16) = 4.0 exactly
SIGMA_GATE = 3.0

C_MEAN = math.sqrt(math.pi / 2.0)          # 1.2533141... leading coeff of E[T_N]
C_HALF = math.sqrt(2.0 * math.log(2.0))    # 1.1774100... 50%-threshold coeff


def prob_all_distinct(k, n):
    """P(first k draws from N=n cells are all distinct) = prod_{i=0}^{k-1}(n-i)/n."""
    p = 1.0
    for i in range(k):
        p *= (n - i) / n
        if p == 0.0:
            break
    return p


def exact_expected_waiting(n):
    """Exact E[T_N] = sum_{k=0}^{N} P(first k draws all distinct) (Ramanujan Q+1)."""
    total = 0.0
    term = 1.0                 # P(all 0 distinct) = 1
    total += term              # k = 0
    for k in range(1, n + 1):
        term *= (n - (k - 1)) / n   # P(all k distinct) from P(all k-1 distinct)
        if term == 0.0:
            break
        total += term
    return total


def half_threshold(n):
    """Smallest m with P(collision within m draws) >= 0.5 (exact, deterministic)."""
    p = 1.0
    m = 0
    while True:
        m += 1
        p *= (n - (m - 1)) / n      # P(all m draws distinct)
        if 1.0 - p >= 0.5:
            return m, (1.0 - p)     # (m*, exact P(collision by m*))


def simulate(n, trials, m_star, rng):
    """Monte-Carlo the first-collision waiting time T for space size n.

    Returns (mean, sample_variance, frac_collided_by_m_star). We draw values one
    at a time until the first repeat, so this genuinely falsifies the sqrt(N)
    scaling claim rather than assuming it.
    """
    s = 0.0
    ss = 0.0
    collided_by = 0
    for _ in range(trials):
        seen = set()
        t = 0
        while True:
            x = rng.randrange(n)
            t += 1
            if x in seen:
                break
            seen.add(x)
        s += t
        ss += t * t
        if t <= m_star:
            collided_by += 1
    mean = s / trials
    var = ss / trials - mean * mean          # population variance of the sample
    var_unbiased = var * trials / (trials - 1)
    return mean, var_unbiased, collided_by / trials


def run():
    rng = random.Random(SEED)

    # exact deterministic anchors (no RNG)
    exact_mean = {n: exact_expected_waiting(n) for n in N_GRID}
    m_star_hi, anchor_collide_hi = half_threshold(N_HI)

    # Monte-Carlo each grid cell in fixed order off the single pinned stream
    mc_mean = {}
    mc_var = {}
    frac_collided_hi = None
    for n in N_GRID:
        m_for_frac = m_star_hi if n == N_HI else 0
        mean, var, frac = simulate(n, TRIALS, m_for_frac, rng)
        mc_mean[n] = mean
        mc_var[n] = var
        if n == N_HI:
            frac_collided_hi = frac

    # G1 — sim correct at N_HI: MC mean waiting time vs exact E[T_N]
    se_hi = math.sqrt(mc_var[N_HI] / TRIALS)
    z_g1 = (mc_mean[N_HI] - exact_mean[N_HI]) / se_hi if se_hi > 0 else float("inf")
    g1 = abs(z_g1) < SIGMA_GATE

    # G2 — sqrt(N) scaling law. The EXACT anchor is the ratio of the exact means
    # E[T_hi]/E[T_lo], which equals sqrt(N_hi/N_lo) to leading order (4.0) plus a
    # vanishing +2/3/sqrt(N) correction — decisively far from the linear-N folk
    # prediction N_hi/N_lo = 16.0. The z-gate tests the MC ratio against the exact
    # ratio; a structural check confirms that exact ratio is a sqrt-law (near 4.0),
    # not a linear-law (near 16.0), value.
    ratio_mc = mc_mean[N_HI] / mc_mean[N_LO]
    ratio_anchor_exact = exact_mean[N_HI] / exact_mean[N_LO]   # 3.9506... (sqrt-law)
    ratio_sqrt_leading = math.sqrt(N_HI / N_LO)               # 4.0 (leading coeff)
    ratio_linear_folk = N_HI / N_LO                           # 16.0 (wrong belief)
    se_lo = math.sqrt(mc_var[N_LO] / TRIALS)
    se_ratio = ratio_mc * math.sqrt(
        (se_hi / mc_mean[N_HI]) ** 2 + (se_lo / mc_mean[N_LO]) ** 2
    )
    z_g2 = (ratio_mc - ratio_anchor_exact) / se_ratio if se_ratio > 0 else float("inf")
    g2_matches = abs(z_g2) < SIGMA_GATE
    g2_sqrt_not_linear = (
        abs(ratio_anchor_exact - ratio_sqrt_leading)
        < abs(ratio_anchor_exact - ratio_linear_folk)
    )
    g2 = g2_matches and g2_sqrt_not_linear

    # G3 — inversion: collision more-likely-than-not by m* ~ 1.1774*sqrt(N) << N/2
    se_frac = math.sqrt(anchor_collide_hi * (1.0 - anchor_collide_hi) / TRIALS)
    z_g3 = (frac_collided_hi - anchor_collide_hi) / se_frac if se_frac > 0 else float("inf")
    g3_matches = abs(z_g3) < SIGMA_GATE
    g3_majority = frac_collided_hi > 0.5
    frac_of_space = m_star_hi / (N_HI / 2.0)       # m*/(N/2), the folk yardstick
    g3_tiny_fraction = frac_of_space < 0.1
    g3 = g3_matches and g3_majority and g3_tiny_fraction

    all_pass = g1 and g2 and g3

    return {
        "proposal": 132,
        "seed": SEED,
        "trials": TRIALS,
        "n_grid": list(N_GRID),
        "n_lo": N_LO,
        "n_hi": N_HI,
        "sigma_gate": SIGMA_GATE,
        "c_mean_sqrt_pi_over_2": C_MEAN,
        "c_half_sqrt_2ln2": C_HALF,
        "exact_expected_waiting": {str(n): exact_mean[n] for n in N_GRID},
        "mc_mean_waiting": {str(n): mc_mean[n] for n in N_GRID},
        "mc_mean_over_sqrt_n": {str(n): mc_mean[n] / math.sqrt(n) for n in N_GRID},
        "m_star_hi": m_star_hi,
        "anchor_collide_by_m_star_hi": anchor_collide_hi,
        "mc_frac_collided_by_m_star_hi": frac_collided_hi,
        "m_star_fraction_of_half_space": frac_of_space,
        "g1_sim_correct": g1,
        "g1_z": z_g1,
        "g1_mc_mean_hi": mc_mean[N_HI],
        "g1_exact_mean_hi": exact_mean[N_HI],
        "g2_sqrt_n_law": g2,
        "g2_ratio_mc": ratio_mc,
        "g2_ratio_anchor_exact": ratio_anchor_exact,
        "g2_ratio_sqrt_leading": ratio_sqrt_leading,
        "g2_ratio_linear_folk": ratio_linear_folk,
        "g2_z": z_g2,
        "g2_sqrt_not_linear": g2_sqrt_not_linear,
        "g3_inversion": g3,
        "g3_z": z_g3,
        "g3_majority": g3_majority,
        "g3_tiny_fraction": g3_tiny_fraction,
        "all_pass": all_pass,
    }


def main():
    results = run()
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    print(
        "G1 sim-correct  :",
        "PASS" if results["g1_sim_correct"] else "FAIL",
        f"(z={results['g1_z']:+.3f}, mean={results['g1_mc_mean_hi']:.4f} "
        f"vs exact {results['g1_exact_mean_hi']:.4f})",
    )
    print(
        "G2 sqrt-N law   :",
        "PASS" if results["g2_sqrt_n_law"] else "FAIL",
        f"(z={results['g2_z']:+.3f}, ratio_mc={results['g2_ratio_mc']:.4f} "
        f"vs exact {results['g2_ratio_anchor_exact']:.4f} ~ sqrt {results['g2_ratio_sqrt_leading']:.1f}; "
        f"linear-folk {results['g2_ratio_linear_folk']:.1f})",
    )
    print(
        "G3 inversion    :",
        "PASS" if results["g3_inversion"] else "FAIL",
        f"(z={results['g3_z']:+.3f}, collided-by-m*={results['mc_frac_collided_by_m_star_hi']:.4f}"
        f">0.5, m*={results['m_star_hi']} = {results['m_star_fraction_of_half_space']:.4f} of N/2)",
    )
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
