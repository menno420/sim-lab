#!/usr/bin/env python3
"""PROPOSAL 125 - The coordination-overhead retrograde-throughput cliff.

FLEET-domain mechanism (round-29 fleet slot). Multi-agent fleet-sizing /
parallel-scalability economics -- the Universal Scalability Law (USL).

Trap / counterintuitive result
------------------------------
Naive linear scaling says a fleet of N agents on one coordinated job does N
times the work: double the agents, double the throughput. Amdahl's law already
kills that -- a serial/contention fraction `alpha` caps speedup at 1/alpha no
matter how many agents you add. The USL is worse: with ANY pairwise
coordination (coherency) cost `beta > 0`, throughput does not merely saturate,
it PEAKS and then DECLINES. The relative throughput (speedup) of an N-agent
fleet is

    C(N) = N / (1 + alpha*(N-1) + beta*N*(N-1))            (Universal Scalability Law)

whose completion-TIME form (C(N) = T(1)/T(N), T(1)=1) is, after algebra,

    T(N) = (1 - alpha)/N  +  (alpha - beta)  +  beta*N.

Three competing pieces: a parallel term (1-alpha)/N that shrinks with N, a
constant (alpha - beta), and a COHERENCY term beta*N that GROWS linearly with
N. Minimising T(N) over N gives the optimum fleet size

    N* = sqrt((1 - alpha) / beta),

past which the beta*N coordination cost dominates and every extra agent makes
the fleet SLOWER -- "retrograde scaling". On the pinned world (alpha=0.03,
beta=0.001) N* = sqrt(0.97/0.001) = 31.14 -> 31 agents, where throughput peaks
at C(31) ~ 10.95x; a 200-agent fleet delivers only C(200) ~ 4.28x -- LESS THAN
HALF the peak. Adding 169 agents past the optimum roughly halves the fleet's
output.

Amdahl (beta = 0) is the isolating control: T0(N) = (1-alpha)/N + alpha is
monotone DECREASING in N (speedup saturates at 1/alpha but never falls), so the
retrograde peak is 100% the coherency term beta, not fleet size or a sim
artifact.

How the sim EMERGES the curve (not asserted)
--------------------------------------------
Each fleet realisation at concurrency N draws its completion time as a sum of
stochastic components with unit-mean parts:

    T(N) = (1 - alpha)/N * Abar  +  (alpha - beta) * S  +  beta * B

  * Abar = (1/N) * sum_{j=1..N} u_j  with u_j ~ Exp(1)  -- the parallel term;
    the 1/N speed-up EMERGES by averaging N per-agent work draws. Since a sum
    of N iid Exp(1) is exactly Gamma(N,1), we sample sum(u_j) as
    gammavariate(N,1) for O(1) cost -- the 1/N averaging is intact, not faked.
  * S ~ Exp(1)                              -- the serial/contention constant.
  * B = sum_{j=1..N} p_j  with p_j ~ Exp(1) -- the coherency term; the LINEAR-in-N
    coordination cost EMERGES by summing N pairwise-coordination draws (sampled
    as Gamma(N,1)).

E[T(N)] = (1-alpha)/N + (alpha-beta) + beta*N is exactly the USL time, so the
retrograde peak arises from the competing 1/N-vs-beta*N draws, and the anchor
gate (G3) checks the measured curve against the closed form. Passing beta=0
gives the Amdahl control (serial coefficient alpha, no coherency term).

Gates (each an effect >= 3 sigma on the /se margin, over TRIALS pinned trials):
  G1  retrograde existence   mean(T(N_hi) - T(N*)) > 0            z >= 3
                             (more agents -> MORE time -> less throughput)
  G2  coherency-necessity    mean(T0(N_hi) - T0(N*)) < 0          z <= -3
                             (beta=0 Amdahl: the SAME fleet is monotone faster)
  G3  closed-form USL anchor  |mean T(N*) - cf|/se < 3 AND
                              |mean T(N_hi) - cf|/se < 3 AND
                              argmin_N mean T(N) == N*  (the throughput peak)

Gate z-scores are computed on the ESTIMATED MEAN via its standard error
(se = std/sqrt(TRIALS)) -- the P104..P124 /se convention.

Determinism: SEED pinned; a canonical results dict is hashed with sha256 and
must reproduce byte-for-byte across runs. Exit 0 iff all gates pass.
"""

import hashlib
import json
import math
import random

SEED = 20260717
ALPHA = 0.03        # contention / serial fraction (Amdahl term)
BETA = 0.001        # coherency / pairwise-coordination coefficient (USL term)
TRIALS = 400        # pinned outer Monte-Carlo trials
BATCH = 200         # fleet realisations averaged per trial
SIGMA = 3.0         # gate strength

# fleet sizes measured; includes N* and a large post-peak fleet N_hi
N_GRID = (1, 2, 4, 8, 16, 24, 31, 48, 64, 96, 128, 200)
N_STAR = round(math.sqrt((1.0 - ALPHA) / BETA))   # 31
N_HI = 200                                         # well past the peak


def usl_time_cf(n, alpha, beta):
    """Closed-form USL completion time T(N) (T(1)=1)."""
    return (1.0 - alpha) / n + (alpha - beta) + beta * n


def usl_speedup_cf(n, alpha, beta):
    """Closed-form USL speedup C(N) = N / (1 + a(N-1) + b N(N-1))."""
    return n / (1.0 + alpha * (n - 1) + beta * n * (n - 1))


def fleet_time(rng, n, alpha, beta):
    """One stochastic realisation of the N-agent fleet completion time.

    T(N) = (1-alpha)/N * Abar + (alpha-beta)*S + beta*B, with
    Abar = Gamma(N,1)/N (== mean of N iid Exp(1)), S = Exp(1),
    B = Gamma(N,1) (== sum of N iid Exp(1)). E[T]=usl_time_cf(n,alpha,beta).
    beta=0 drops the coherency term (Amdahl control).
    """
    abar = rng.gammavariate(n, 1.0) / n            # mean 1 (avg of N Exp(1))
    s = rng.expovariate(1.0)                       # mean 1
    t = (1.0 - alpha) / n * abar + (alpha - beta) * s
    if beta > 0.0:
        b = rng.gammavariate(n, 1.0)               # mean N (sum of N Exp(1))
        t += beta * b
    return t


def mean_std(xs):
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var)


def batch_mean_time(rng, n, alpha, beta):
    acc = 0.0
    for _ in range(BATCH):
        acc += fleet_time(rng, n, alpha, beta)
    return acc / BATCH


def run():
    rng = random.Random(SEED)

    # per-trial batch-mean completion time for every fleet size (USL: beta>0)
    grid_trials = {n: [] for n in N_GRID}
    # paired retrograde differences at (N*, N_hi): USL and Amdahl (beta=0) control
    diff_usl = []      # T(N_hi) - T(N*), beta>0  -> should be > 0 (retrograde)
    diff_amdahl = []   # T0(N_hi) - T0(N*), beta=0 -> should be < 0 (monotone)

    for _ in range(TRIALS):
        for n in N_GRID:
            grid_trials[n].append(batch_mean_time(rng, n, ALPHA, BETA))
        t_star = batch_mean_time(rng, N_STAR, ALPHA, BETA)
        t_hi = batch_mean_time(rng, N_HI, ALPHA, BETA)
        diff_usl.append(t_hi - t_star)
        t0_star = batch_mean_time(rng, N_STAR, ALPHA, 0.0)
        t0_hi = batch_mean_time(rng, N_HI, ALPHA, 0.0)
        diff_amdahl.append(t0_hi - t0_star)

    # grid means / closed-form anchor
    grid_mean = {n: mean_std(grid_trials[n])[0] for n in N_GRID}
    grid_cf = {n: usl_time_cf(n, ALPHA, BETA) for n in N_GRID}
    grid_se = {n: mean_std(grid_trials[n])[1] / math.sqrt(TRIALS) for n in N_GRID}
    argmin_sim = min(N_GRID, key=lambda n: grid_mean[n])
    anchor_max_abs_z = max(
        abs((grid_mean[n] - grid_cf[n]) / grid_se[n]) if grid_se[n] > 0 else 0.0
        for n in N_GRID
    )

    # measured speedup curve (throughput relative to N=1)
    t1 = grid_mean[1]
    speedup_sim = {n: t1 / grid_mean[n] for n in N_GRID}
    speedup_cf = {n: usl_speedup_cf(n, ALPHA, BETA) for n in N_GRID}

    # ---- G1: retrograde exists (T(N_hi) > T(N*), beta>0) ----
    d1_m, d1_s = mean_std(diff_usl)
    d1_se = d1_s / math.sqrt(TRIALS)
    z1 = d1_m / d1_se if d1_se > 0 else float("inf")
    g1 = d1_m > 0 and z1 >= SIGMA

    # ---- G2: control -- beta=0 Amdahl is monotone faster (drop reverses) ----
    d2_m, d2_s = mean_std(diff_amdahl)
    d2_se = d2_s / math.sqrt(TRIALS)
    z2 = d2_m / d2_se if d2_se > 0 else float("inf")
    g2 = d2_m < 0 and z2 <= -SIGMA

    # ---- G3: closed-form USL anchor + peak location ----
    z3_star = (grid_mean[N_STAR] - grid_cf[N_STAR]) / grid_se[N_STAR]
    z3_hi = (grid_mean[N_HI] - grid_cf[N_HI]) / grid_se[N_HI]
    g3 = (abs(z3_star) < SIGMA) and (abs(z3_hi) < SIGMA) and (argmin_sim == N_STAR)

    # headline throughput facts (closed form, reported)
    c_star_cf = usl_speedup_cf(N_STAR, ALPHA, BETA)
    c_hi_cf = usl_speedup_cf(N_HI, ALPHA, BETA)

    all_pass = bool(g1 and g2 and g3)

    results = {
        "proposal": 125,
        "domain": "fleet",
        "slot": "round-29-fleet",
        "seed": SEED,
        "params": {
            "ALPHA": ALPHA, "BETA": BETA, "TRIALS": TRIALS, "BATCH": BATCH,
            "SIGMA": SIGMA, "N_GRID": list(N_GRID), "N_STAR": N_STAR, "N_HI": N_HI,
        },
        "theory": {
            "n_star_closed_form": round(math.sqrt((1.0 - ALPHA) / BETA), 6),
            "n_star_int": N_STAR,
            "speedup_peak_cf": round(c_star_cf, 6),
            "speedup_hi_cf": round(c_hi_cf, 6),
            "peak_over_hi_ratio": round(c_star_cf / c_hi_cf, 6),
            "amdahl_ceiling_1_over_alpha": round(1.0 / ALPHA, 6),
        },
        "curve": {
            "time_sim": {str(n): round(grid_mean[n], 6) for n in N_GRID},
            "time_cf": {str(n): round(grid_cf[n], 6) for n in N_GRID},
            "speedup_sim": {str(n): round(speedup_sim[n], 6) for n in N_GRID},
            "speedup_cf": {str(n): round(speedup_cf[n], 6) for n in N_GRID},
            "argmin_time_sim": argmin_sim,
            "anchor_max_abs_z": round(anchor_max_abs_z, 4),
        },
        "gates": {
            "G1_retrograde_exists": {
                "stat": "mean_time_hi_minus_star", "mean": round(d1_m, 6),
                "std": round(d1_s, 6), "se": round(d1_se, 6),
                "z": round(z1, 4), "pass": g1,
            },
            "G2_coherency_necessity": {
                "stat": "mean_amdahl_hi_minus_star", "mean": round(d2_m, 6),
                "std": round(d2_s, 6), "se": round(d2_se, 6),
                "z": round(z2, 4), "pass": g2,
            },
            "G3_usl_anchor_and_peak": {
                "z_star": round(z3_star, 4), "z_hi": round(z3_hi, 4),
                "argmin_time_sim": argmin_sim, "n_star": N_STAR, "pass": g3,
            },
        },
        "all_pass": all_pass,
    }
    return results


def main():
    results = run()
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("usl_coherency_retrograde_cliff_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    g = results["gates"]
    print("G1_retrograde_exists:", g["G1_retrograde_exists"]["z"],
          g["G1_retrograde_exists"]["pass"])
    print("G2_coherency_necessity:", g["G2_coherency_necessity"]["z"],
          g["G2_coherency_necessity"]["pass"])
    print("G3_usl_anchor_and_peak: z_star", g["G3_usl_anchor_and_peak"]["z_star"],
          "z_hi", g["G3_usl_anchor_and_peak"]["z_hi"],
          "argmin", g["G3_usl_anchor_and_peak"]["argmin_time_sim"],
          g["G3_usl_anchor_and_peak"]["pass"])
    print("peak C(%d)=%.4f vs C(%d)=%.4f (ratio %.4f); N*_cf=%.4f" % (
        N_STAR, results["theory"]["speedup_peak_cf"], N_HI,
        results["theory"]["speedup_hi_cf"], results["theory"]["peak_over_hi_ratio"],
        results["theory"]["n_star_closed_form"]))
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
