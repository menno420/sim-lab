#!/usr/bin/env python3
"""
PROPOSAL 113 — the two-choices routing cliff (firsthand verifier).

Phenomenon (balanced allocations / power-of-two-choices load balancing).
A dispatcher routes each of m tasks to the least-loaded of d workers sampled
uniformly at random from n workers (ties -> first sampled). With d=1 (pure
random routing) the maximum queue length grows like ln n / ln ln n. With
d=2 it collapses to ln ln n / ln 2 + O(1) -- a DOUBLE-EXPONENTIAL improvement
in the tail (Azar, Broder, Karlin & Upfal, "Balanced Allocations", SIAM J.
Comput. 29(1):180-200, 1999; Mitzenmacher, "The Power of Two Choices in
Randomized Load Balancing", IEEE TPDS 12(10), 2001). Every extra probe past
the second only divides the already-tiny ln ln n term by ln d: the marginal
gain collapses. The trap is that operators expect balance to improve smoothly
with the probe count and over-provision d=4..8, when the entire benefit is
captured at d=2.

Pre-registered gates (each >= 3 sigma on the /se margin, one pinned SEED):
  G1  two-choices jump is real:   mean(max_1 - max_2) > 0,                z >= 3
  G2  the cliff (front-loaded):   mean((max_1-max_2)-(max_2-max_3)) > 0,  z >= 3
  G3  the plateau beyond two:     mean(max_2 - max_4) < 2.0,              z >= 3

Run:  python3 ideas/fleet/two_choices_routing_cliff.py
Deterministic: same SEED -> identical results dict -> identical sha256.
Exit 0 iff all gates pass.
"""

import random
import math
import json
import hashlib

# ---- pinned world (committed constants) ----
SEED = 20260717
N_WORKERS = 20000          # bins
M_TASKS = 20000            # balls (m = n : the classic balls-into-bins regime)
TRIALS = 120               # independent replicas
D_VALUES = (1, 2, 3, 4)    # probes per task
SIGMA_GATE = 3.0
PLATEAU_MAX = 2.0          # G3 ceiling: total post-2 saving must be < 2 slots


def max_load_for_d(rng, n, m, d):
    """Place m tasks into n workers; each -> least loaded of d sampled. Return max load."""
    load = [0] * n
    for _ in range(m):
        best = rng.randrange(n)
        for _ in range(d - 1):
            c = rng.randrange(n)
            if load[c] < load[best]:
                best = c
        load[best] += 1
    return max(load)


def mean_se(xs):
    n = len(xs)
    mean = sum(xs) / n
    if n < 2:
        return mean, 0.0
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return mean, math.sqrt(var / n)


def z_above_zero(mean, se):
    if se > 0:
        return mean / se
    return 999.0 if mean > 0 else -999.0


def z_below_ceiling(ceiling, mean, se):
    if se > 0:
        return (ceiling - mean) / se
    return 999.0 if mean < ceiling else -999.0


def main():
    rng = random.Random(SEED)

    maxes = {d: [] for d in D_VALUES}
    for _ in range(TRIALS):
        for d in D_VALUES:
            maxes[d].append(max_load_for_d(rng, N_WORKERS, M_TASKS, d))

    d12 = [maxes[1][t] - maxes[2][t] for t in range(TRIALS)]        # first extra probe
    d23 = [maxes[2][t] - maxes[3][t] for t in range(TRIALS)]        # second extra probe
    cliff = [d12[t] - d23[t] for t in range(TRIALS)]               # front-loading
    plateau = [maxes[2][t] - maxes[4][t] for t in range(TRIALS)]   # total post-2 saving

    m12, se12 = mean_se(d12)
    m23, se23 = mean_se(d23)
    mcliff, secliff = mean_se(cliff)
    mplat, seplat = mean_se(plateau)

    g1_z = z_above_zero(m12, se12)
    g2_z = z_above_zero(mcliff, secliff)
    g3_z = z_below_ceiling(PLATEAU_MAX, mplat, seplat)

    gates = {
        "G1_two_choices_jump": {
            "stat": "mean(max_1 - max_2)", "mean": m12, "se": se12,
            "z": g1_z, "pass": g1_z >= SIGMA_GATE,
        },
        "G2_cliff_front_loaded": {
            "stat": "mean((max_1-max_2) - (max_2-max_3))", "mean": mcliff, "se": secliff,
            "z": g2_z, "pass": g2_z >= SIGMA_GATE,
        },
        "G3_plateau_beyond_two": {
            "stat": "mean(max_2 - max_4)", "ceiling": PLATEAU_MAX, "mean": mplat, "se": seplat,
            "z": g3_z, "pass": g3_z >= SIGMA_GATE,
        },
    }
    all_pass = all(g["pass"] for g in gates.values())

    mean_max = {str(d): mean_se(maxes[d])[0] for d in D_VALUES}

    results = {
        "proposal": 113,
        "phenomenon": "two-choices routing cliff (power-of-two-choices balanced allocations)",
        "params": {
            "seed": SEED, "n_workers": N_WORKERS, "m_tasks": M_TASKS,
            "trials": TRIALS, "d_values": list(D_VALUES), "sigma_gate": SIGMA_GATE,
            "plateau_max": PLATEAU_MAX,
        },
        "anchor": {
            "single_choice_ln_n_over_lnln_n": math.log(N_WORKERS) / math.log(math.log(N_WORKERS)),
            "two_choice_lnln_n_over_ln2": math.log(math.log(N_WORKERS)) / math.log(2.0),
            "d23_mean": m23, "d23_se": se23,
        },
        "sim": {"mean_max_load_by_d": mean_max},
        "gates": gates,
        "all_pass": all_pass,
    }

    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    results["results_sha256"] = digest

    with open("two_choices_routing_cliff_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(json.dumps(results, indent=2))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
