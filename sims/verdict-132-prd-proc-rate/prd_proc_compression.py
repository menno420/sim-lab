#!/usr/bin/env python3
"""
prd_proc_compression.py — reference verifier for PROPOSAL 119
(round-27, game slot).

Pseudo-Random Distribution (PRD) proc-rate compression — the Warcraft III /
Dota 2 anti-streak proc system. Instead of a flat per-attempt chance p, PRD
starts each proc's chance low and RAISES it by a constant increment C on every
consecutive failure, resetting to C on a success:

    P(proc on the n-th attempt since the last proc) = min(1, C * n),  n = 1,2,3,...

This bounds bad-luck streaks (the chance climbs to 1 by attempt ceil(1/C)) and
smooths good-luck streaks, which is exactly why competitive games use it for
crit / bash / evasion.

The counterintuitive trap this proposal isolates: the increment constant C is
NOT the proc rate. A designer who wants "25% crit" and naively sets C = 0.25
does NOT get a 25% effective proc rate — the escalating chance forces frequent
early procs, so the long-run EFFECTIVE rate (procs / attempts) is far higher.
The effective rate is 1 / E[N], where N is the number of attempts between procs:

    P(N=n) = [ prod_{k=1}^{n-1} (1 - min(1, C*k)) ] * min(1, C*n)
    E[N]   = sum_{n>=1} n * P(N=n)
    effective_rate = 1 / E[N].

For C = 0.25 the walk terminates at n=4 (C*4 = 1.0, a guaranteed proc):
    P(N=1)=0.25, P(N=2)=0.375, P(N=3)=0.28125, P(N=4)=0.09375,
    E[N]=2.21875, effective_rate = 1/2.21875 = 0.450704 -- nearly DOUBLE 0.25.
So the correct move is to SOLVE C for the target rate (C ~ 0.0847 yields an
effective 0.25), never to set C = the nominal rate.

The verifier:
  * Simulates PRD as a single seeded stream of ATTEMPTS attempts under the
    naive constant C_NAIVE = 0.25, measuring the effective proc rate
    (procs / attempts) and the MAX consecutive-miss streak.
  * Solves (bisection on the exact E[N] closed form) the constant C_SOLVED that
    yields an effective rate of TARGET = 0.25, then simulates it and measures
    its effective rate.
  * Simulates a true-random Bernoulli(0.25) control stream and measures its
    effective rate and MAX miss streak, to contrast streak behaviour: PRD caps
    the miss run at ceil(1/C)-1 while true-random runs long.
  * z-tests the observed naive-C effective rate against the intended 0.25 using
    the binomial-proportion se z = (p_obs - p_null)/sqrt(p_null*(1-p_null)/N),
    gated at >= SIGMA_GATE sigma.

Gates (APPROVE iff all hold, in order G1 -> G2 -> G3):
  G1 naive-C overshoot (headline): the measured effective proc rate under the
     naive C = 0.25 is >= EFF_MIN = 0.40 by >= 3 sigma (binomial se). Setting the
     increment to the nominal rate nearly DOUBLES the realized proc rate; the
     vs-null z (p_obs vs 0.25) is astronomically significant.
  G2 solve-C-fixes-it (control): the SOLVED constant C_SOLVED yields a measured
     effective rate within 3 sigma of the target 0.25 (|z| < 3) AND C_SOLVED is
     far below the nominal (<= SOLVED_MAX = 0.15). Solving for C recovers the
     intended rate; C != nominal.
  G3 closed-form anchor + anti-streak: the measured naive-C effective rate
     reproduces the exact analytic 1/E[N] = 0.450704 within 3 sigma (|z| < 3)
     AND the PRD max miss-streak is strictly below the true-random max miss
     streak (PRD bounds bad-luck runs; true-random does not).

stdlib only (random, math, json, hashlib); fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717        # proposal-owned pinned seed; SEEDLESS discipline
ATTEMPTS = 2_000_000   # length of each simulated attempt stream
C_NAIVE = 0.25         # the naive increment: designer sets C = nominal "25%"
TARGET = 0.25          # the intended (nominal) effective proc rate
SIGMA_GATE = 3.0       # gate threshold in sigma
EFF_MIN = 0.40         # G1: min naive-C effective rate (overshoot floor)
SOLVED_MAX = 0.15      # G2: max solved constant (must be far below nominal)


def prd_expected_attempts(c):
    """Exact E[N] for PRD with increment c: N = attempts between procs.

    P(N=n) = [prod_{k<n} (1 - min(1,c*k))] * min(1, c*n); the walk terminates
    at n = ceil(1/c) where min(1,c*n) = 1 (a guaranteed proc)."""
    e_n = 0.0
    surviving = 1.0    # P(no proc in the first n-1 attempts) = P(N >= n)
    n = 1
    while True:
        p_n = min(1.0, c * n)          # proc chance on the n-th attempt
        p_eq = surviving * p_n          # P(N = n)
        e_n += n * p_eq
        surviving *= (1.0 - p_n)
        if p_n >= 1.0 or surviving <= 0.0:
            break
        n += 1
    return e_n


def prd_effective_rate(c):
    """Analytic long-run effective proc rate for PRD increment c: 1 / E[N]."""
    return 1.0 / prd_expected_attempts(c)


def solve_c_for_rate(target, lo=1e-9, hi=0.5, iters=200):
    """Bisection: find the PRD increment c whose analytic effective rate equals
    `target`. effective_rate(c) = 1/E[N](c) is strictly increasing in c."""
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if prd_effective_rate(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def simulate_prd(c, attempts, rng):
    """Simulate a PRD stream of `attempts` attempts with increment c.

    Returns (effective_rate, max_miss_streak). The running counter `since` is
    the number of consecutive misses since the last proc; the current attempt
    is the (since+1)-th, so its proc chance is min(1, c*(since+1))."""
    procs = 0
    since = 0            # consecutive misses since the last proc
    max_streak = 0       # longest run of consecutive misses observed
    for _ in range(attempts):
        chance = c * (since + 1)
        if chance >= 1.0 or rng.random() < chance:
            procs += 1
            since = 0
        else:
            since += 1
            if since > max_streak:
                max_streak = since
    return procs / attempts, max_streak


def simulate_random(p, attempts, rng):
    """True-random Bernoulli(p) control stream: effective rate + max miss run."""
    procs = 0
    since = 0
    max_streak = 0
    for _ in range(attempts):
        if rng.random() < p:
            procs += 1
            since = 0
        else:
            since += 1
            if since > max_streak:
                max_streak = since
    return procs / attempts, max_streak


def binom_z(p_obs, p_null, n):
    """Binomial-proportion z of an observed rate vs a null rate over n trials:
    z = (p_obs - p_null) / sqrt(p_null*(1-p_null)/n)."""
    se = math.sqrt(p_null * (1.0 - p_null) / n)
    return (p_obs - p_null) / se if se > 0 else float("inf")


def main():
    rng = random.Random(SEED)

    # --- Analytic anchors (exact, no simulation) --------------------------
    e_n_naive = prd_expected_attempts(C_NAIVE)
    eff_naive_cf = 1.0 / e_n_naive                       # 0.450704...
    c_solved = solve_c_for_rate(TARGET)                  # ~0.0847
    eff_solved_cf = prd_effective_rate(c_solved)         # ~0.25 by construction

    # --- Simulations (single seeded streams, deterministic) ---------------
    eff_naive, streak_naive = simulate_prd(C_NAIVE, ATTEMPTS, rng)
    eff_solved, streak_solved = simulate_prd(c_solved, ATTEMPTS, rng)
    eff_random, streak_random = simulate_random(TARGET, ATTEMPTS, rng)

    # --- Gates ------------------------------------------------------------
    # G1 naive-C overshoot (headline): effective_naive >= EFF_MIN by >= 3 sigma.
    z_g1 = binom_z(eff_naive, EFF_MIN, ATTEMPTS)
    z_naive_vs_null = binom_z(eff_naive, TARGET, ATTEMPTS)   # the vs-0.25 z-test
    g1 = (z_g1 >= SIGMA_GATE) and (eff_naive >= EFF_MIN)

    # G2 solve-C-fixes-it (control): solved effective within 3 sigma of TARGET
    # AND C_SOLVED far below nominal.
    z_g2 = binom_z(eff_solved, TARGET, ATTEMPTS)
    g2 = (abs(z_g2) < SIGMA_GATE) and (c_solved <= SOLVED_MAX)

    # G3 closed-form anchor + anti-streak: measured naive effective reproduces
    # the analytic 1/E[N] within 3 sigma AND PRD bounds the miss streak below
    # true-random.
    z_g3_anchor = binom_z(eff_naive, eff_naive_cf, ATTEMPTS)
    g3 = (abs(z_g3_anchor) < SIGMA_GATE) and (streak_naive < streak_random)

    all_pass = g1 and g2 and g3

    results = {
        "params": {
            "SEED": SEED, "ATTEMPTS": ATTEMPTS, "C_NAIVE": C_NAIVE,
            "TARGET": TARGET, "SIGMA_GATE": SIGMA_GATE,
            "EFF_MIN": EFF_MIN, "SOLVED_MAX": SOLVED_MAX,
        },
        "anchors": {
            "E_N_naive": round(e_n_naive, 6),
            "eff_naive_closed_form": round(eff_naive_cf, 6),
            "c_solved": round(c_solved, 6),
            "eff_solved_closed_form": round(eff_solved_cf, 6),
            "prd_max_streak_bound_naive": math.ceil(1.0 / C_NAIVE) - 1,
        },
        "sim": {
            "eff_naive": round(eff_naive, 6),
            "streak_naive": streak_naive,
            "eff_solved": round(eff_solved, 6),
            "streak_solved": streak_solved,
            "eff_random": round(eff_random, 6),
            "streak_random": streak_random,
        },
        "gates": {
            "G1_naive_overshoot": {"z": round(z_g1, 4),
                                   "z_vs_null_0.25": round(z_naive_vs_null, 4),
                                   "eff_naive": round(eff_naive, 6),
                                   "EFF_MIN": EFF_MIN, "pass": g1},
            "G2_solve_c_fixes_it": {"z": round(z_g2, 4),
                                    "c_solved": round(c_solved, 6),
                                    "eff_solved": round(eff_solved, 6),
                                    "SOLVED_MAX": SOLVED_MAX, "pass": g2},
            "G3_anchor_and_streak": {"z_anchor": round(z_g3_anchor, 4),
                                     "eff_naive": round(eff_naive, 6),
                                     "eff_naive_closed_form": round(eff_naive_cf, 6),
                                     "streak_naive": streak_naive,
                                     "streak_random": streak_random,
                                     "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("prd_proc_compression_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
