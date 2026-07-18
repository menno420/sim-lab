#!/usr/bin/env python3
"""PROPOSAL 139 — raid team-size coordination overhead: the Ringelmann DPS cliff
(round-32 GAME slot).

Phenomenon: in a co-op raid each ADDED member contributes nominal single-target
DPS, but also imposes COORDINATION OVERHEAD — per-member uptime decays as the
roster grows (mechanic-dodges, movement, target-swaps) and burst-window
collisions waste overlapping damage. Model the total raid DPS at roster size N as

    DPS(N) = ( sum_{i=1..N} base_i ) * uptime(N) * (1 - collision_loss(N)),

with
    uptime(N)         = max(FLOOR, 1 - C_UPTIME*(N-1))         # linear decay, floored
    1 - collision_loss(N) = (1 - Q_COLLISION)^(N-1)            # multiplicative burst waste

The nominal sum grows LINEARLY in N, but uptime and the collision factor decay,
so their product PEAKS at a roster size N* strictly SMALLER than the max allowed
roster NMAX. Against an enrage-timer boss (a raw-DPS race) a smaller premade at
N* out-clears a full NMAX stack — "stack more bodies" is negative-EV past N*.

Folk belief (inverted here): "more raiders = more DPS; always bring a full roster."

This is the game-lane instance of the RINGELMANN EFFECT — individual
productivity falls as group size grows through coordination and motivation loss
(https://en.wikipedia.org/wiki/Ringelmann_effect; Ingham, Levinger, Graves &
Peckham 1974, "The Ringelmann effect: Studies of group size and group
performance", J. Exp. Soc. Psychol. 10(4):371-384).

Pinned world:
  NMAX          = 8      max allowed roster (an 8-person raid)
  base_i        ~ Gamma(K_SHAPE=4, THETA=25)  -> mean 100, CoV 0.5 (DPS heterogeneity)
  uptime decay  C_UPTIME = 0.06, FLOOR = 0.35
  collision     Q_COLLISION = 0.07 per added member (multiplicative)
The deterministic mean-DPS model MU*N*uptime(N)*eff(N) (MU=100) peaks at N*=6:
its expected total raid DPS at 6 bodies STRICTLY exceeds that at the full 8.

Pre-registered gates (APPROVE iff ALL hold, in order G1 -> G2 -> G3):
  G1  CLIFF     : with N* the pre-registered mean-model peak, the paired
                  per-trial difference DPS(N*) - DPS(NMAX) has Monte-Carlo
                  mean > 0 with z = mean/se >= 3 sigma — the smaller premade
                  strictly out-DPSes the full roster.
  G2  INTERIOR  : the per-trial argmax roster size N*_t is STRICTLY INTERIOR
                  (1 < N*_t < NMAX). The fraction of trials that are interior,
                  tested as a one-proportion z against the null p0 = 0.5,
                  is >= 3 sigma AND the mean-model peak N* is itself interior.
  G3  PLACEBO   : remove the overhead (C_UPTIME = 0, Q_COLLISION = 0). Then
                  DPS(N) = sum base_i is MONOTONE increasing, so the interior
                  fraction is 0.0 EXACTLY and the paired mean DPS(NMAX)-DPS(N*)
                  > 0 with z >= 3 sigma — the full roster reliably wins. The
                  interior peak is CAUSED by coordination overhead, not the sim.
"""

import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 20_000
SIGMA_GATE = 3.0

NMAX = 8                      # max allowed raid roster
K_SHAPE = 4.0                # Gamma shape  -> CoV = 1/sqrt(K) = 0.5
THETA = 25.0                 # Gamma scale  -> mean base DPS = K*THETA = 100
MU = K_SHAPE * THETA         # nominal mean single-target DPS = 100.0

C_UPTIME = 0.06              # per-member uptime decay
FLOOR = 0.35                 # uptime floor
Q_COLLISION = 0.07           # per-member multiplicative burst-collision waste

P0_INTERIOR = 0.5            # null proportion for the interior one-proportion z


def uptime(n, c=C_UPTIME, floor=FLOOR):
    """Per-member uptime at roster size n: linear decay, floored."""
    return max(floor, 1.0 - c * (n - 1))


def eff(n, q=Q_COLLISION):
    """Collision-survival factor 1 - collision_loss(n): multiplicative burst waste."""
    return (1.0 - q) ** (n - 1)


def mean_dps(n, c=C_UPTIME, q=Q_COLLISION):
    """Deterministic mean-model total raid DPS at roster size n."""
    return MU * n * uptime(n, c) * eff(n, q)


def peak_roster(c=C_UPTIME, q=Q_COLLISION):
    """argmax over n=1..NMAX of the deterministic mean-model DPS."""
    best_n, best_v = 1, mean_dps(1, c, q)
    for n in range(2, NMAX + 1):
        v = mean_dps(n, c, q)
        if v > best_v:
            best_n, best_v = n, v
    return best_n


def _z(mean, se, null=0.0):
    return (mean - null) / se if se > 0 else float("inf")


def run():
    rng = random.Random(SEED)

    n_star = peak_roster()                       # pre-registered interior peak (=6)
    mean_model = {n: mean_dps(n) for n in range(1, NMAX + 1)}

    # accumulators
    s_diff = ss_diff = 0.0                        # G1: DPS(N*) - DPS(NMAX), overhead world
    interior_count = 0                           # G2: per-trial argmax strictly interior
    s_plac = ss_plac = 0.0                        # G3: DPS(NMAX) - DPS(N*), placebo world
    interior_plac_count = 0                      # G3: placebo interior fraction (== 0)

    up = [0.0] + [uptime(n) for n in range(1, NMAX + 1)]   # 1-indexed
    ef = [0.0] + [eff(n) for n in range(1, NMAX + 1)]

    for _ in range(TRIALS):
        base = [rng.gammavariate(K_SHAPE, THETA) for _ in range(NMAX)]
        # prefix sums: prefix[n] = sum of the first n members
        prefix = [0.0] * (NMAX + 1)
        acc = 0.0
        for i in range(NMAX):
            acc += base[i]
            prefix[i + 1] = acc

        # overhead world: DPS(n) = prefix[n]*uptime(n)*eff(n)
        dps = [0.0] + [prefix[n] * up[n] * ef[n] for n in range(1, NMAX + 1)]
        # per-trial argmax roster size
        arg = 1
        best = dps[1]
        for n in range(2, NMAX + 1):
            if dps[n] > best:
                best, arg = dps[n], n
        if 1 < arg < NMAX:
            interior_count += 1

        d = dps[n_star] - dps[NMAX]              # paired cliff difference
        s_diff += d
        ss_diff += d * d

        # placebo world: no overhead -> DPS(n) = prefix[n], monotone increasing
        dplac_star = prefix[n_star]
        dplac_max = prefix[NMAX]
        # placebo argmax is always NMAX (strictly monotone since base_i > 0)
        # interior_plac_count stays 0 by construction; assert via the sum below
        dp = dplac_max - dplac_star              # full roster minus smaller premade
        s_plac += dp
        ss_plac += dp * dp

    # --- G1: cliff (smaller premade out-DPSes the full roster)
    mean_d = s_diff / TRIALS
    var_d = max(ss_diff / TRIALS - mean_d * mean_d, 0.0)
    se_d = math.sqrt(var_d / TRIALS)
    z_g1 = _z(mean_d, se_d)
    g1 = (mean_d > 0.0) and (z_g1 >= SIGMA_GATE)

    # --- G2: interior peak (one-proportion z vs null p0 = 0.5)
    phat = interior_count / TRIALS
    se_p = math.sqrt(P0_INTERIOR * (1.0 - P0_INTERIOR) / TRIALS)
    z_g2 = (phat - P0_INTERIOR) / se_p
    g2 = (1 < n_star < NMAX) and (phat > P0_INTERIOR) and (z_g2 >= SIGMA_GATE)

    # --- G3: placebo (no overhead -> full roster reliably wins, no interior peak)
    interior_plac_fraction = interior_plac_count / TRIALS
    mean_p = s_plac / TRIALS
    var_p = max(ss_plac / TRIALS - mean_p * mean_p, 0.0)
    se_pl = math.sqrt(var_p / TRIALS)
    z_g3 = _z(mean_p, se_pl)
    g3 = (interior_plac_fraction == 0.0) and (mean_p > 0.0) and (z_g3 >= SIGMA_GATE)

    all_pass = g1 and g2 and g3

    return {
        "proposal": 139,
        "seed": SEED,
        "trials": TRIALS,
        "sigma_gate": SIGMA_GATE,
        "nmax": NMAX,
        "params": {
            "k_shape": K_SHAPE,
            "theta": THETA,
            "mu_base": MU,
            "c_uptime": C_UPTIME,
            "floor": FLOOR,
            "q_collision": Q_COLLISION,
        },
        "mean_model_dps": {str(n): mean_model[n] for n in range(1, NMAX + 1)},
        "n_star": n_star,
        "mean_dps_at_n_star": mean_model[n_star],
        "mean_dps_at_nmax": mean_model[NMAX],
        "g1_mean_cliff_diff": mean_d,
        "g1_se": se_d,
        "g1_z": z_g1,
        "g1_cliff": g1,
        "g2_interior_fraction": phat,
        "g2_p0": P0_INTERIOR,
        "g2_z": z_g2,
        "g2_n_star_interior": bool(1 < n_star < NMAX),
        "g2_interior": g2,
        "g3_interior_fraction_placebo": interior_plac_fraction,
        "g3_mean_fullbeats_diff": mean_p,
        "g3_se": se_pl,
        "g3_z": z_g3,
        "g3_placebo": g3,
        "all_pass": all_pass,
    }


def main():
    results = run()
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    print(
        "G1 cliff        :",
        "PASS" if results["g1_cliff"] else "FAIL",
        f"(DPS(N*)-DPS(Nmax)={results['g1_mean_cliff_diff']:+.4f}, z={results['g1_z']:+.2f})",
    )
    print(
        "G2 interior     :",
        "PASS" if results["g2_interior"] else "FAIL",
        f"(N*={results['n_star']}, interior_frac={results['g2_interior_fraction']:.5f}, "
        f"z={results['g2_z']:+.2f})",
    )
    print(
        "G3 placebo      :",
        "PASS" if results["g3_placebo"] else "FAIL",
        f"(interior_frac={results['g3_interior_fraction_placebo']:.1f}, "
        f"full-beats={results['g3_mean_fullbeats_diff']:+.4f}, z={results['g3_z']:+.2f})",
    )
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
