#!/usr/bin/env python3
"""PROPOSAL 105 - Delegation loop collapse in liquid democracy.

FLEET-domain mechanism (round-24 fleet slot). Multi-agent governance economics.

Trap / counterintuitive result
------------------------------
N agents each delegate their vote to ONE uniformly-random peer (self allowed =
voting directly). Naive intuition: uniform random delegation spreads influence
evenly, so ~N independent deciders and no concentration. Reality (random-mapping
statistics, Flajolet & Odlyzko 1990): the delegation graph is a random mapping,
and

  * the effective electorate COLLAPSES - only cyclic nodes decide, and their
    count is ~ sqrt(pi*N/2) = O(sqrt(N)), under 10% of agents for N=4096;
  * a SINGLE accidental bloc (largest weakly-connected component) captures a
    Theta(N) share of all voting weight (asymptotic constant ~0.7582);
  * the clique that actually controls that bloc - the cycle at its core - is
    only O(sqrt(N)) agents, under 5% of the population.

So individually-rational one-hop delegation, chosen uniformly at random with no
preferential attachment, silently concentrates >=30% of all voting weight into
a sub-5% clique while shrinking the effective electorate below 10%.

Gates (each an effect >= 3 sigma from its threshold, over T pinned trials):
  G1  effective electorate  mean(C/N)          <= 0.10
  G2  power concentration   mean(bloc_max/N)   >= 0.30
  G3  controlling clique    mean(core_cycle/N) <= 0.05

Determinism: SEED pinned; a canonical results dict is hashed with sha256 and
must reproduce byte-for-byte across runs. Exit 0 iff all gates pass.
"""

import hashlib
import json
import math
import random

SEED = 20260717
N = 4096          # agents
TRIALS = 400      # pinned Monte-Carlo trials
SIGMA = 3.0       # gate strength

G1_MAX = 0.10     # effective-electorate ceiling (C/N)
G2_MIN = 0.30     # largest-bloc weight floor
G3_MAX = 0.05     # controlling-cycle ceiling


def functional_graph_stats(f, n):
    """One O(n) pass over a functional graph f: [n]->[n].

    Returns (num_cyclic, num_components, largest_bloc, controlling_cycle_len).
    """
    UNVISITED, ACTIVE, DONE = 0, 1, 2
    state = [UNVISITED] * n
    pos = [0] * n
    is_cyclic = [False] * n
    root = [-1] * n           # representative cyclic node each node funnels into

    for s in range(n):
        if state[s] != UNVISITED:
            continue
        path = []
        u = s
        while state[u] == UNVISITED:
            state[u] = ACTIVE
            pos[u] = len(path)
            path.append(u)
            u = f[u]
        if state[u] == ACTIVE:
            start = pos[u]
            for c in path[start:]:
                is_cyclic[c] = True
                root[c] = u
            for node in path:
                if root[node] == -1:
                    root[node] = u
                state[node] = DONE
        else:  # DONE -> funnels into an existing cycle
            r = root[u]
            for node in path:
                root[node] = r
                state[node] = DONE

    bloc = {}
    for i in range(n):
        r = root[i]
        bloc[r] = bloc.get(r, 0) + 1
    num_cyclic = sum(is_cyclic)
    num_components = len(bloc)
    top_root = max(bloc, key=lambda k: (bloc[k], -k))
    largest_bloc = bloc[top_root]
    controlling_cycle_len = sum(
        1 for i in range(n) if is_cyclic[i] and root[i] == top_root
    )
    return num_cyclic, num_components, largest_bloc, controlling_cycle_len


def mean_std(xs):
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var)


def run():
    rng = random.Random(SEED)
    c_frac, bloc_frac, core_frac = [], [], []
    for _ in range(TRIALS):
        f = [rng.randrange(N) for _ in range(N)]
        c, _k, bloc_max, core = functional_graph_stats(f, N)
        c_frac.append(c / N)
        bloc_frac.append(bloc_max / N)
        core_frac.append(core / N)

    c_m, c_s = mean_std(c_frac)
    b_m, b_s = mean_std(bloc_frac)
    o_m, o_s = mean_std(core_frac)

    def z_below(mean, sd, thresh):
        se = sd / math.sqrt(TRIALS)
        return (thresh - mean) / se if se > 0 else float("inf")

    def z_above(mean, sd, thresh):
        se = sd / math.sqrt(TRIALS)
        return (mean - thresh) / se if se > 0 else float("inf")

    c_se = c_s / math.sqrt(TRIALS)
    b_se = b_s / math.sqrt(TRIALS)
    o_se = o_s / math.sqrt(TRIALS)

    z1 = z_below(c_m, c_s, G1_MAX)
    z2 = z_above(b_m, b_s, G2_MIN)
    z3 = z_below(o_m, o_s, G3_MAX)

    g1 = c_m <= G1_MAX and z1 >= SIGMA
    g2 = b_m >= G2_MIN and z2 >= SIGMA
    g3 = o_m <= G3_MAX and z3 >= SIGMA

    results = {
        "proposal": 105,
        "domain": "fleet",
        "slot": "round-24-fleet",
        "seed": SEED,
        "N": N,
        "trials": TRIALS,
        "sigma": SIGMA,
        "gates": {
            "G1_electorate_collapse": {
                "stat": "mean_cyclic_frac", "mean": round(c_m, 6),
                "std": round(c_s, 6), "se": round(c_se, 6), "threshold": G1_MAX,
                "z": round(z1, 4), "pass": g1,
            },
            "G2_power_concentration": {
                "stat": "mean_largest_bloc_frac", "mean": round(b_m, 6),
                "std": round(b_s, 6), "se": round(b_se, 6), "threshold": G2_MIN,
                "z": round(z2, 4), "pass": g2,
            },
            "G3_controlling_clique": {
                "stat": "mean_core_cycle_frac", "mean": round(o_m, 6),
                "std": round(o_s, 6), "se": round(o_se, 6), "threshold": G3_MAX,
                "z": round(z3, 4), "pass": g3,
            },
        },
        "theory": {
            "cyclic_expected_frac": round(math.sqrt(math.pi * N / 2) / N, 6),
            "largest_component_frac_asymptotic": 0.7582,
        },
        "all_pass": bool(g1 and g2 and g3),
    }
    return results


def main():
    results = run()
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    out = {"results": results, "sha256": digest}
    with open("delegation_loop_collapse_results.json", "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(canonical)
    print("sha256:", digest)
    for name, g in results["gates"].items():
        print(f"{name}: mean={g['mean']} thr={g['threshold']} z={g['z']} pass={g['pass']}")
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
