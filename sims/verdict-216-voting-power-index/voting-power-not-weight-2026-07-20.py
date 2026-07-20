#!/usr/bin/env python3
"""Voting power is not voting weight -- the Banzhaf / Shapley-Shubik paradox.

A weighted voting game [q; w_1..w_n]: coalition S wins iff sum of its weights
>= q. Voter i is a swing (critical) in S (i not in S) iff S loses but S+{i} wins.
Banzhaf power ~ swing count; Shapley-Shubik power ~ pivotal share over orderings.
Both are computed EXACTLY (fractions.Fraction) by coalition enumeration; Banzhaf
is cross-checked by an exact weight generating-function DP.

Gates (SEED=20260717, Z_GATE=3.0):
  G1 EXACT headline instance (direction: exact fraction equality) -- for
     [51; 50,49,1] the normalized Banzhaf index is EXACTLY (3/5, 1/5, 1/5) and
     Shapley-Shubik is EXACTLY (2/3, 1/6, 1/6): the 49-weight bloc has identical
     power to the 1-weight bloc under both indices, while the 50-weight bloc holds
     3x (Banzhaf). Banzhaf swing counts agree brute-vs-DP (closed-form vs enum).
  G2 EXACT exhaustive n=4, weights 1..6 (direction: counts > 0, methods agree) --
     positive-weight DUMMIES occur (a voter with weight yet zero power), the
     max power-share / weight-share ratio strictly exceeds 1 (power is not
     proportional to weight), and brute-vs-DP Banzhaf agree for ALL 1296 games.
  G3 EXACT exhaustive n=4 (direction: count > 0) -- the Banzhaf and Shapley-Shubik
     normalized vectors DIFFER in a nonzero number of games: the two 'canonical'
     power measures give materially different answers; the max L1 gap is pinned.
  G4 ROBUSTNESS + >=3sigma (direction: mean > 0) -- over a seeded sample of larger
     games (n in {5,6,7}, weights 1..20), the top voter's Banzhaf power-share minus
     its weight-share has strictly positive mean with z >= 3.0 (a large-voter
     premium: the biggest bloc's power systematically exceeds its weight).
"""
import hashlib
import json
import random
import sys
from fractions import Fraction as F
from itertools import combinations, product
from math import factorial

SEED = 20260717
Z_GATE = 3.0


def majority_quota(weights):
    return sum(weights) // 2 + 1


def swings_brute(weights, quota):
    n = len(weights)
    sw = [0] * n
    for i in range(n):
        others = [j for j in range(n) if j != i]
        wi = weights[i]
        for r in range(len(others) + 1):
            for combo in combinations(others, r):
                s = sum(weights[j] for j in combo)
                if s < quota and s + wi >= quota:
                    sw[i] += 1
    return sw


def swings_dp(weights, quota):
    n = len(weights)
    sw = [0] * n
    for i in range(n):
        wi = weights[i]
        counts = {0: 1}
        for j in range(n):
            if j == i:
                continue
            w = weights[j]
            nc = dict(counts)
            for s, c in counts.items():
                nc[s + w] = nc.get(s + w, 0) + c
            counts = nc
        lo, hi = quota - wi, quota - 1
        sw[i] = sum(c for s, c in counts.items() if lo <= s <= hi)
    return sw


def banzhaf_norm(weights, quota):
    sw = swings_brute(weights, quota)
    tot = sum(sw)
    if tot == 0:
        return [F(0)] * len(weights), sw
    return [F(s, tot) for s in sw], sw


def shapley_shubik(weights, quota):
    n = len(weights)
    fact = [factorial(k) for k in range(n + 1)]
    ss = [F(0)] * n
    for i in range(n):
        others = [j for j in range(n) if j != i]
        wi = weights[i]
        for r in range(len(others) + 1):
            coeff = F(fact[r] * fact[n - 1 - r], fact[n])
            for combo in combinations(others, r):
                s = sum(weights[j] for j in combo)
                if s < quota and s + wi >= quota:
                    ss[i] += coeff
    return ss


def r6(x):
    return round(float(x), 6)


def gate1():
    weights = (50, 49, 1)
    q = majority_quota(weights)
    bz, sw = banzhaf_norm(weights, q)
    ss = shapley_shubik(weights, q)
    dp = swings_dp(weights, q)
    methods_agree = (sw == dp)
    exp_bz = [F(3, 5), F(1, 5), F(1, 5)]
    exp_ss = [F(2, 3), F(1, 6), F(1, 6)]
    ok = (bz == exp_bz) and (ss == exp_ss) and methods_agree
    return ok, weights, q, bz, ss, methods_agree


def gate23(n=4, wmax=6):
    dummy_count = 0
    dummy_first = None
    unequal_count = 0
    total = 0
    methods_agree_all = True
    max_ratio = F(0)
    max_ratio_game = None
    max_l1 = F(0)
    max_l1_game = None
    for weights in product(range(1, wmax + 1), repeat=n):
        total += 1
        q = majority_quota(weights)
        bz, sw = banzhaf_norm(weights, q)
        if sw != swings_dp(weights, q):
            methods_agree_all = False
        ss = shapley_shubik(weights, q)
        if any(weights[i] > 0 and sw[i] == 0 for i in range(n)):
            dummy_count += 1
            if dummy_first is None:
                dummy_first = (list(weights), q)
        W = sum(weights)
        tot = sum(sw)
        if tot > 0:
            for i in range(n):
                ratio = F(sw[i], tot) / F(weights[i], W)
                if ratio > max_ratio:
                    max_ratio = ratio
                    max_ratio_game = (list(weights), q)
        if bz != ss:
            unequal_count += 1
            l1 = sum(abs(bz[i] - ss[i]) for i in range(n))
            if l1 > max_l1:
                max_l1 = l1
                max_l1_game = (list(weights), q)
    return {
        "total": total, "dummy_count": dummy_count, "dummy_first": dummy_first,
        "methods_agree_all": methods_agree_all, "max_ratio": max_ratio,
        "max_ratio_game": max_ratio_game, "unequal_count": unequal_count,
        "max_l1": max_l1, "max_l1_game": max_l1_game,
    }


def gate4():
    rng = random.Random(SEED)
    ns = [5, 6, 7]
    per_n = 1000
    diffs = []
    for n in ns:
        for _ in range(per_n):
            weights = tuple(rng.randint(1, 20) for _ in range(n))
            q = majority_quota(weights)
            _, sw = banzhaf_norm(weights, q)
            tot = sum(sw)
            if tot == 0:
                continue
            W = sum(weights)
            top = max(range(n), key=lambda i: weights[i])
            diffs.append(sw[top] / tot - weights[top] / W)
    mean = sum(diffs) / len(diffs)
    var = sum((d - mean) ** 2 for d in diffs) / (len(diffs) - 1)
    sem = (var / len(diffs)) ** 0.5
    z = mean / sem if sem > 0 else 0.0
    return len(diffs), mean, sem, z


def build_results():
    g1_ok, g1w, g1q, g1bz, g1ss, g1agree = gate1()
    e = gate23(4, 6)
    n_sample, mean, sem, z = gate4()

    g1 = g1_ok
    g2 = (e["dummy_count"] > 0) and e["methods_agree_all"] and (e["max_ratio"] > 1)
    g3 = e["unequal_count"] > 0
    g4 = (mean > 0) and (z >= Z_GATE)
    gates = {"G1": g1, "G2": g2, "G3": g3, "G4": g4}

    return {
        "constants": {"seed": SEED, "z_gate": Z_GATE, "enum_n": 4, "enum_wmax": 6,
                      "sample_ns": [5, 6, 7], "per_n": 1000},
        "g1_instance": {"weights": list(g1w), "quota": g1q,
                        "banzhaf": [str(x) for x in g1bz],
                        "shapley_shubik": [str(x) for x in g1ss],
                        "methods_agree": g1agree},
        "g2": {"games_total": e["total"], "dummy_count": e["dummy_count"],
               "dummy_first": e["dummy_first"], "methods_agree_all": e["methods_agree_all"],
               "max_power_weight_ratio": str(e["max_ratio"]),
               "max_ratio_game": e["max_ratio_game"]},
        "g3": {"games_total": e["total"], "index_unequal_count": e["unequal_count"],
               "max_index_l1": str(e["max_l1"]), "max_l1_game": e["max_l1_game"]},
        "g4": {"sample": n_sample, "mean_power_minus_weight_share": r6(mean),
               "sem": r6(sem), "z": r6(z)},
        "gates": gates,
        "all_pass": all(gates.values()),
    }


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def main():
    r1 = build_results()
    r2 = build_results()
    if canonical(r1) != canonical(r2):
        sys.stderr.write("NON-DETERMINISTIC: in-process double-run diverged\n")
        sys.exit(3)
    results = r1
    print(json.dumps(results, indent=2, sort_keys=True))
    for g in ("G1", "G2", "G3", "G4"):
        print(f"{g}: {'PASS' if results['gates'][g] else 'FAIL'}")
    print(f"all_pass: {results['all_pass']}")
    print(f"results_sha256: {hashlib.sha256(canonical(results).encode()).hexdigest()}")
    sys.exit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
