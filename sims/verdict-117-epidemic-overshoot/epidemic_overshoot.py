#!/usr/bin/env python3
"""
epidemic_overshoot.py — reference verifier for PROPOSAL 104 (round-23, UNRELATED
slot closer). Domain: epidemiology — Kermack-McKendrick (1927) SIR final-size
theory. Fleet-external pure-mechanism head.

The "overshoot past herd immunity" trap. The herd-immunity threshold is
h* = 1 - 1/R0: the susceptible fraction at which transmission stops GROWING
(the effective reproduction number falls to 1). The folk belief is that the
epidemic therefore STOPS near h*, so the final fraction infected is about h*.
It does not. Infections already in flight when the threshold is crossed keep
transmitting, so the epidemic OVERSHOOTS: the final attack rate z* solves the
final-size equation z = 1 - exp(-R0*z) and satisfies z* > h* strictly for every
R0 > 1. The overshoot z* - h* is the fraction of the population infected
UNNECESSARILY, past the point where growth already turned negative.

Model: stochastic Reed-Frost chain-binomial SIR on a homogeneously-mixing
population of N. Each generation, every susceptible independently escapes
infection from each of the I_t current infectives with per-pair transmission
probability q = R0/N, so it is infected with probability 1 - (1-q)^{I_t};
infectives recover after one generation. Seeded with I0 infectives. Epidemics
are classified major (a real outbreak) vs minor (early stochastic fade-out) by
a final-size cutoff; the closed-form final-size limit conditions on a major
outbreak, so the gates compare against major outbreaks only.

Gates (all >= 3 sigma):
  G1 overshoot headline: the measured final attack rate z_sim exceeds the
     herd-immunity threshold h* = 1 - 1/R0 by >= 3 sigma, and z_sim > h* --
     the epidemic does NOT stop at herd immunity.
  G2 final-size anchor MATCH: z_sim matches the closed-form final-size solution
     z* of z = 1 - exp(-R0*z) within 3 sigma (|z| < 3) -- the stochastic sim
     reproduces the Kermack-McKendrick anchor.
  G3 post-threshold burn: the mean fraction infected AFTER the susceptible pool
     first drops below 1/R0 (the herd threshold is crossed) is >= 3 sigma above
     zero -- in-flight transmission past the threshold produces the overshoot.

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717        # proposal-owned pinned seed; SEEDLESS discipline
R0 = 2.5               # basic reproduction number (favorable-epidemic regime R0>1)
N_POP = 5000           # homogeneously-mixing population per epidemic
I0 = 1                 # initial infectives (index cases)
N_EPIDEMICS = 4000     # independent stochastic epidemics simulated
MAJOR_CUTOFF = 0.10    # final-size fraction separating major from minor outbreaks
SIGMA_GATE = 3.0       # pre-registered gate threshold (sigma)


def rbinom(n, p, rng):
    """Exact Binomial(n, p) draw via the geometric-gap method (stdlib only).

    Sample the positions of successes among n Bernoulli(p) trials by drawing
    geometric gaps; cost is O(number of successes). Deterministic given rng."""
    if n <= 0 or p <= 0.0:
        return 0
    if p >= 1.0:
        return n
    log_q = math.log(1.0 - p)
    count = 0
    idx = -1
    while True:
        u = rng.random()
        gap = int(math.floor(math.log(u) / log_q))  # failures before next success
        idx += 1 + gap
        if idx >= n:
            break
        count += 1
    return count


def final_size_star(r0):
    """Closed-form final attack rate: nonzero root z* of z = 1 - exp(-r0*z).

    Bisection on (eps, 1) isolates the nonzero root (the trivial z=0 is excluded
    by starting strictly above 0). f(z)=1-exp(-r0 z)-z is >0 just above 0 (since
    f'(0)=r0-1>0 for r0>1) and <0 at z=1, so a single crossing = z*."""
    def f(z):
        return (1.0 - math.exp(-r0 * z)) - z
    lo, hi = 1e-9, 1.0 - 1e-12
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def run_epidemic(rng):
    """One Reed-Frost chain-binomial SIR epidemic.

    Returns (final_frac, pre_threshold_frac) where final_frac is the total ever
    infected as a fraction of N, and pre_threshold_frac is the cumulative
    infected fraction at the FIRST generation whose end-of-generation
    susceptible count has dropped below N/R0 (the herd threshold crossing).
    A minor outbreak returns pre_threshold_frac == final_frac (threshold never
    crossed) and is filtered out downstream by the major cutoff."""
    q = R0 / N_POP
    log_esc = math.log(1.0 - q)          # per-infective log escape probability
    herd_S = N_POP / R0                  # susceptibles at the herd threshold
    s = N_POP - I0
    inf = I0
    infected_total = I0
    pre_threshold = None                 # cumulative infected at threshold crossing
    while inf > 0 and s > 0:
        # per-susceptible infection probability against inf infectives this gen
        p_inf = 1.0 - math.exp(inf * log_esc)
        new_inf = rbinom(s, p_inf, rng)
        s -= new_inf
        infected_total += new_inf
        inf = new_inf
        if pre_threshold is None and s < herd_S:
            # herd threshold just crossed at the END of this generation
            pre_threshold = infected_total / N_POP
    final_frac = infected_total / N_POP
    if pre_threshold is None:            # threshold never crossed (minor outbreak)
        pre_threshold = final_frac
    return final_frac, pre_threshold


def main():
    rng = random.Random(SEED)

    h_star = 1.0 - 1.0 / R0              # herd-immunity threshold
    z_star = final_size_star(R0)        # closed-form final attack rate
    overshoot_star = z_star - h_star    # closed-form overshoot (final - threshold)

    finals = []
    burns = []                          # post-threshold burn per major outbreak
    n_major = 0
    n_minor = 0
    for _ in range(N_EPIDEMICS):
        final_frac, pre_threshold = run_epidemic(rng)
        if final_frac >= MAJOR_CUTOFF:
            n_major += 1
            finals.append(final_frac)
            burns.append(final_frac - pre_threshold)
        else:
            n_minor += 1

    def mean_se(xs):
        k = len(xs)
        m = sum(xs) / k
        var = sum((x - m) ** 2 for x in xs) / k
        se = math.sqrt(var / k)
        return m, se

    z_sim, se_z = mean_se(finals)
    burn_mean, se_burn = mean_se(burns)

    # G1 overshoot headline: z_sim exceeds herd threshold h* by >= 3 sigma.
    z_g1 = (z_sim - h_star) / se_z if se_z > 0 else float("inf")
    g1 = (z_g1 >= SIGMA_GATE) and (z_sim > h_star)

    # G2 final-size anchor MATCH: z_sim == closed-form z* within 3 sigma.
    z_g2 = abs(z_sim - z_star) / se_z if se_z > 0 else float("inf")
    g2 = z_g2 < SIGMA_GATE

    # G3 post-threshold burn: mean post-threshold infected fraction > 0 at >=3 sigma.
    z_g3 = burn_mean / se_burn if se_burn > 0 else float("inf")
    g3 = (z_g3 >= SIGMA_GATE) and (burn_mean > 0.0)

    all_pass = g1 and g2 and g3

    results = {
        "params": {"SEED": SEED, "R0": R0, "N_POP": N_POP, "I0": I0,
                   "N_EPIDEMICS": N_EPIDEMICS, "MAJOR_CUTOFF": MAJOR_CUTOFF,
                   "SIGMA_GATE": SIGMA_GATE},
        "anchor": {"h_star_herd_threshold": round(h_star, 6),
                   "z_star_final_size": round(z_star, 6),
                   "overshoot_star": round(overshoot_star, 6)},
        "counts": {"n_major": n_major, "n_minor": n_minor,
                   "major_frac": round(n_major / N_EPIDEMICS, 6)},
        "sim": {
            "z_sim_final_attack": round(z_sim, 6), "se_z": round(se_z, 6),
            "burn_post_threshold": round(burn_mean, 6), "se_burn": round(se_burn, 6),
            "overshoot_sim": round(z_sim - h_star, 6),
        },
        "gates": {
            "G1_overshoot": {"z": round(z_g1, 2), "pass": g1},
            "G2_anchor_match": {"z": round(z_g2, 2), "pass": g2},
            "G3_post_threshold_burn": {"z": round(z_g3, 2), "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("epidemic_overshoot_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
