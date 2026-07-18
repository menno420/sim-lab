#!/usr/bin/env python3
"""fan-out tail amplification -- round-31 FLEET-slot verifier (PROPOSAL 133).

Phenomenon: a scatter-gather request fans out to N independent leaf servers and
must wait for the LAST of them. If each leaf independently misses its latency
SLO ("is slow") with probability p, the whole request is slow whenever ANY leaf
is slow: P_slow(N) = 1 - (1 - p)**N. A rare per-leaf tail becomes the common
case at fan-out scale, and the MEDIAN request crosses into "slow" at
N* = ln 2 / (-ln(1 - p)) ~= 0.693 / p.

Stdlib only. Deterministic under the pinned SEED; a double run is byte-identical.
"""
import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 120000
P_LEAF = 0.01
N_GRID = (10, 69, 100, 200)
Z_GATE = 3.0


def p_slow_exact(n, p):
    """Closed form: probability at least one of n independent leaves is slow."""
    return 1.0 - (1.0 - p) ** n


def crossover_n_star(p):
    """Smallest integer N with P_slow(N) >= 0.5, plus the real-valued root."""
    root = math.log(2.0) / (-math.log(1.0 - p))
    n_star = math.ceil(root)
    while p_slow_exact(n_star - 1, p) >= 0.5:
        n_star -= 1
    while p_slow_exact(n_star, p) < 0.5:
        n_star += 1
    return n_star, root


def simulate(rng, n, p, trials):
    """Return (frac_requests_slow, mean_slow_leaves) over `trials` fan-outs of width n."""
    slow_requests = 0
    total_slow_leaves = 0
    for _ in range(trials):
        slow_leaves = 0
        for _ in range(n):
            if rng.random() < p:
                slow_leaves += 1
        if slow_leaves > 0:
            slow_requests += 1
        total_slow_leaves += slow_leaves
    return slow_requests / trials, total_slow_leaves / trials


def z_binom(p_hat, p0, trials):
    se = math.sqrt(p0 * (1.0 - p0) / trials)
    return (p_hat - p0) / se if se > 0 else 0.0


def z_mean(mean_hat, mean0, var_per_trial, trials):
    se = math.sqrt(var_per_trial / trials)
    return (mean_hat - mean0) / se if se > 0 else 0.0


def run():
    rng = random.Random(SEED)
    per_n = {}
    for n in N_GRID:
        frac_slow, mean_slow = simulate(rng, n, P_LEAF, TRIALS)
        per_n[str(n)] = {
            "p_slow_hat": frac_slow,
            "p_slow_exact": p_slow_exact(n, P_LEAF),
            "mean_slow_leaves_hat": mean_slow,
            "mean_slow_leaves_exact": n * P_LEAF,
        }

    n_star, root = crossover_n_star(P_LEAF)

    g1_n = 100
    g1_exact = p_slow_exact(g1_n, P_LEAF)
    g1_z = z_binom(per_n[str(g1_n)]["p_slow_hat"], g1_exact, TRIALS)
    g1_pass = abs(g1_z) < Z_GATE

    g2_n = n_star
    g2_exact = p_slow_exact(g2_n, P_LEAF)
    g2_z = z_binom(per_n[str(g2_n)]["p_slow_hat"], g2_exact, TRIALS)
    g2_bracket = (
        p_slow_exact(n_star - 1, P_LEAF) < 0.5 <= p_slow_exact(n_star, P_LEAF)
    )
    g2_pass = abs(g2_z) < Z_GATE and g2_bracket and n_star == 69

    g3_n = 100
    g3_exact = g3_n * P_LEAF
    g3_var = g3_n * P_LEAF * (1.0 - P_LEAF)
    g3_z = z_mean(per_n[str(g3_n)]["mean_slow_leaves_hat"], g3_exact, g3_var, TRIALS)
    g3_pass = abs(g3_z) < Z_GATE

    gates = {
        "G1_union_bound_tail": {
            "n": g1_n, "exact": g1_exact, "z": g1_z, "pass": g1_pass,
        },
        "G2_median_crossover": {
            "n": g2_n, "exact": g2_exact, "z": g2_z,
            "bracket": g2_bracket, "pass": g2_pass,
        },
        "G3_mean_slow_linear": {
            "n": g3_n, "exact": g3_exact, "z": g3_z, "pass": g3_pass,
        },
    }
    all_pass = g1_pass and g2_pass and g3_pass

    return {
        "mechanism": "fan-out-tail-amplification",
        "config": {
            "seed": SEED, "trials": TRIALS, "p_leaf": P_LEAF,
            "n_grid": list(N_GRID), "z_gate": Z_GATE,
        },
        "crossover": {"n_star": n_star, "root": root},
        "per_n": per_n,
        "gates": gates,
        "all_pass": all_pass,
    }


def main():
    results = run()
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + digest)
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
