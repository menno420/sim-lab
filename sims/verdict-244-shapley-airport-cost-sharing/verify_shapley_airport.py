#!/usr/bin/env python3
"""Airport cost-sharing game -- the Shapley VALUE as average marginal cost.

An airport runway must be long enough for the most demanding plane. Player i
needs a runway of cost c_i; a coalition S needs cost v(S) = max_{i in S} c_i.
The Shapley value splits the grand cost v(N) = max c_i among the planes.

Exact closed form (Littlechild-Owen airport game): sort costs ascending
c_(1) <= ... <= c_(n); the player at rank j pays
    phi_j = sum_{k=1}^{j} (c_(k) - c_(k-1)) / (n - k + 1),  c_(0) = 0,
i.e. each runway segment is shared equally among all planes that need it.

This is the cooperative Shapley VALUE of a COST game -- distinct from the
already-built Shapley-Shubik power index (a simple voting game): different
characteristic function (max-cost vs pivotal-swing), different object (a
cost-allocation vector vs a per-voter power number).

Central identity: phi_i = E over uniformly random join orders of player i's
marginal cost contribution max(0, c_i - max_{j before i} c_j).

stdlib only; deterministic; SEED = 20260717.
Four gates, each in its own direction with real teeth:
  G1  EXACT (Fraction): the segment closed form equals the exact average over
      ALL n! orderings, for n in {4, 5}, every player.
  G2  Monte-Carlo agreement: the sampled random-order mean marginal for the top
      player matches its exact Shapley value, |z| < 3.
  G3  Invariance (exact): efficiency -- the values sum exactly to v(N); and
      symmetry -- two equal-cost players receive exactly equal value.
  G4  Falsifiability: the sampled top-player mean rejects the naive equal-split
      allocation v(N)/n at large |z|.
"""
import hashlib
import json
import math
import random
import sys
from itertools import permutations
from fractions import Fraction

SEED = 20260717
MAIN_COSTS = (1, 2, 4, 8)
MAIN5_COSTS = (1, 2, 4, 8, 16)
SYM_COSTS = (2, 5, 5, 9)
G2_TRIALS = 200000
G4_THRESHOLD = 6.0


def shapley_closed(costs):
    n = len(costs)
    order = sorted(range(n), key=lambda i: costs[i])
    csorted = [costs[i] for i in order]
    phi_rank = [Fraction(0, 1)] * n
    prev = 0
    cum = Fraction(0, 1)
    for k in range(n):
        seg = Fraction(csorted[k] - prev, n - k)
        cum = cum + seg
        phi_rank[k] = cum
        prev = csorted[k]
    phi = [Fraction(0, 1)] * n
    for rank_pos, player in enumerate(order):
        phi[player] = phi_rank[rank_pos]
    return phi


def marginals(costs, perm):
    out = [0] * len(costs)
    curmax = 0
    for p in perm:
        gain = costs[p] - curmax
        out[p] = gain if gain > 0 else 0
        if costs[p] > curmax:
            curmax = costs[p]
    return out


def shapley_enum(costs):
    n = len(costs)
    total = [0] * n
    count = 0
    for perm in permutations(range(n)):
        m = marginals(costs, perm)
        for p in range(n):
            total[p] += m[p]
        count += 1
    return [Fraction(total[p], count) for p in range(n)]


def mc_top(costs, trials, rng):
    n = len(costs)
    top = max(range(n), key=lambda i: costs[i])
    base = list(range(n))
    vals = []
    for _ in range(trials):
        perm = base[:]
        rng.shuffle(perm)
        vals.append(marginals(costs, perm)[top])
    return top, vals


def zstat(vals, target):
    n = len(vals)
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / (n - 1)
    se = math.sqrt(var / n)
    return (mean - target) / se, mean, se


def fr(x):
    return "%d/%d" % (x.numerator, x.denominator)


def compute():
    rng = random.Random(SEED)

    phi_main = shapley_closed(MAIN_COSTS)
    phi_main5 = shapley_closed(MAIN5_COSTS)
    enum_main = shapley_enum(MAIN_COSTS)
    enum_main5 = shapley_enum(MAIN5_COSTS)
    g1_ok = (phi_main == enum_main) and (phi_main5 == enum_main5)

    top, vals = mc_top(MAIN_COSTS, G2_TRIALS, rng)
    z2, mean2, _se2 = zstat(vals, float(phi_main[top]))

    phi_sym = shapley_closed(SYM_COSTS)
    efficiency = sum(phi_main) == max(MAIN_COSTS)
    symmetry = phi_sym[1] == phi_sym[2]
    g3_ok = efficiency and symmetry

    n = len(MAIN_COSTS)
    equal_split = Fraction(max(MAIN_COSTS), n)
    z4, _m4, _s4 = zstat(vals, float(equal_split))

    results = {
        "problem": "airport-shapley-cost-sharing",
        "seed": SEED,
        "main_costs": list(MAIN_COSTS),
        "main5_costs": list(MAIN5_COSTS),
        "sym_costs": list(SYM_COSTS),
        "shapley_main": [fr(x) for x in phi_main],
        "shapley_main_float": ["%.10f" % float(x) for x in phi_main],
        "shapley_main5": [fr(x) for x in phi_main5],
        "shapley_sym": [fr(x) for x in phi_sym],
        "grand_cost": max(MAIN_COSTS),
        "top_player": top,
        "top_shapley": fr(phi_main[top]),
        "g1_enum_main": [fr(x) for x in enum_main],
        "g1_enum_main5": [fr(x) for x in enum_main5],
        "g1_pass": bool(g1_ok),
        "g2_mc": {
            "trials": G2_TRIALS,
            "top_player": top,
            "mean": "%.8f" % mean2,
            "target": "%.10f" % float(phi_main[top]),
            "z": "%.6f" % z2,
        },
        "g2_pass": abs(z2) < 3.0,
        "g3_invariance": {
            "efficiency_sum": fr(sum(phi_main)),
            "grand_cost": max(MAIN_COSTS),
            "efficiency": bool(efficiency),
            "sym_pair": [fr(phi_sym[1]), fr(phi_sym[2])],
            "symmetry": bool(symmetry),
        },
        "g3_pass": bool(g3_ok),
        "g4_falsify": {
            "equal_split": fr(equal_split),
            "equal_split_float": "%.10f" % float(equal_split),
            "z": "%.6f" % z4,
            "threshold": G4_THRESHOLD,
        },
        "g4_pass": abs(z4) > G4_THRESHOLD,
    }
    return results


def serialize(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def main():
    a = compute()
    b = compute()
    sa, sb = serialize(a), serialize(b)
    assert sa == sb, "in-process double-run not byte-identical"
    digest = hashlib.sha256(sa.encode("utf-8")).hexdigest()
    print(sa)
    all_pass = a["g1_pass"] and a["g2_pass"] and a["g3_pass"] and a["g4_pass"]
    print("results_sha256: %s" % digest)
    print("all_gates_pass: %s" % all_pass)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
