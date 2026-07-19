#!/usr/bin/env python3
"""
PROPOSAL 176 — Giant-component phase transition in random graphs (UNRELATED slot, round 42).

HEAD: In a random graph on n nodes with average degree c (Erdos-Renyi G(n, m),
m = round(c*n/2) edges), the fraction of nodes in the LARGEST connected component
undergoes a sharp phase transition at c = 1. Below c = 1 the largest component is a
vanishing fraction of n (order log n); above c = 1 a "giant" component containing a
constant fraction rho(c) > 0 of all nodes appears abruptly. Folk belief: connectivity
grows smoothly and proportionally with edge count. Reality: nothing macroscopic exists
until average degree crosses exactly 1 edge per node, then a giant snaps into being.
Fixed point: rho = 1 - exp(-c*rho)  (rho(1.4) ~= 0.51).

Gates (z_gate = 3.0, SEED = 20260717, deterministic in-process double-run):
  G1 existence  : supercritical (c=1.4) giant fraction >= 0.30 and subcritical (c=0.7)
                  fraction <= 0.08; z of the difference >= 3.
  G2 robustness : under a 4x scale shift (n: 4000 -> 16000) the supercritical giant
                  fraction stays >= 0.30 (z vs 0.30 floor >= 3) and is size-invariant
                  (|rho(16000)-rho(4000)| <= 0.05), while the subcritical fraction
                  SHRINKS with n (order log n / n -> 0).
  G3 sharpness  : the near-threshold jump frac(1.1)-frac(0.9) exceeds the far-subcritical
                  jump frac(0.7)-frac(0.5) by >= 3 sigma, with all sub-threshold
                  fractions <= 0.15 — growth is concentrated at c~1, not linear in c.
"""

import hashlib
import json
import math
import random

SEED = 20260717
Z_GATE = 3.0
TRIALS = 40


class DSU:
    __slots__ = ("parent", "size", "largest")

    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.largest = 1

    def find(self, x):
        p = self.parent
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        if self.size[ra] > self.largest:
            self.largest = self.size[ra]


def largest_fraction(n, c, rng):
    m = int(round(c * n / 2.0))
    dsu = DSU(n)
    for _ in range(m):
        a = rng.randrange(n)
        b = rng.randrange(n)
        if a != b:
            dsu.union(a, b)
    return dsu.largest / n


def stats(samples):
    k = len(samples)
    mean = sum(samples) / k
    var = sum((x - mean) ** 2 for x in samples) / (k - 1) if k > 1 else 0.0
    se = math.sqrt(var / k)
    return mean, se


def diff_z(mean_a, se_a, mean_b, se_b):
    denom = math.sqrt(se_a * se_a + se_b * se_b)
    return (mean_a - mean_b) / denom if denom > 0 else 0.0


def sample(n, c, rng):
    return [largest_fraction(n, c, rng) for _ in range(TRIALS)]


def r6(x):
    return round(float(x), 6)


def compute():
    rng = random.Random(SEED)
    n1, n2 = 4000, 16000

    s_sub_n1 = sample(n1, 0.7, rng)
    s_sup_n1 = sample(n1, 1.4, rng)
    s_sub_n2 = sample(n2, 0.7, rng)
    s_sup_n2 = sample(n2, 1.4, rng)
    s_c05 = sample(n2, 0.5, rng)
    s_c09 = sample(n2, 0.9, rng)
    s_c11 = sample(n2, 1.1, rng)

    m_sub1, se_sub1 = stats(s_sub_n1)
    m_sup1, se_sup1 = stats(s_sup_n1)
    m_sub2, se_sub2 = stats(s_sub_n2)
    m_sup2, se_sup2 = stats(s_sup_n2)
    m_c05, se_c05 = stats(s_c05)
    m_c09, se_c09 = stats(s_c09)
    m_c11, se_c11 = stats(s_c11)

    z1 = diff_z(m_sup1, se_sup1, m_sub1, se_sub1)
    g1 = (m_sup1 >= 0.30) and (m_sub1 <= 0.08) and (z1 >= Z_GATE)

    z2 = (m_sup2 - 0.30) / se_sup2 if se_sup2 > 0 else 0.0
    size_invariant = abs(m_sup2 - m_sup1) <= 0.05
    sub_shrinks = m_sub2 < m_sub1
    g2 = (m_sup2 >= 0.30) and (z2 >= Z_GATE) and size_invariant and sub_shrinks

    jump_near = m_c11 - m_c09
    jump_far = m_sub2 - m_c05
    se_jn = math.sqrt(se_c11 ** 2 + se_c09 ** 2)
    se_jf = math.sqrt(se_sub2 ** 2 + se_c05 ** 2)
    z3 = diff_z(jump_near, se_jn, jump_far, se_jf)
    subthresh_bounded = (m_c05 <= 0.15) and (m_c09 <= 0.15) and (m_sub2 <= 0.15)
    g3 = ((jump_near - jump_far) >= 0.05) and (z3 >= Z_GATE) and subthresh_bounded

    gates = {
        "G1_existence": {"sup_mean": r6(m_sup1), "sub_mean": r6(m_sub1), "z": r6(z1), "pass": g1},
        "G2_robustness": {"sup_mean_n16000": r6(m_sup2), "z_vs_floor": r6(z2),
                          "size_gap": r6(abs(m_sup2 - m_sup1)), "sub_shrinks": sub_shrinks, "pass": g2},
        "G3_sharpness": {"jump_near": r6(jump_near), "jump_far": r6(jump_far), "z": r6(z3), "pass": g3},
    }
    order = ["G1_existence", "G2_robustness", "G3_sharpness"]
    first_fail = next((g for g in order if not gates[g]["pass"]), None)

    return {
        "head": "giant-component-threshold",
        "seed": SEED,
        "trials": TRIALS,
        "z_gate": Z_GATE,
        "conditions": {
            "sub_n4000_c0.7": {"mean": r6(m_sub1), "se": r6(se_sub1)},
            "sup_n4000_c1.4": {"mean": r6(m_sup1), "se": r6(se_sup1)},
            "sub_n16000_c0.7": {"mean": r6(m_sub2), "se": r6(se_sub2)},
            "sup_n16000_c1.4": {"mean": r6(m_sup2), "se": r6(se_sup2)},
            "n16000_c0.5": {"mean": r6(m_c05), "se": r6(se_c05)},
            "n16000_c0.9": {"mean": r6(m_c09), "se": r6(se_c09)},
            "n16000_c1.1": {"mean": r6(m_c11), "se": r6(se_c11)},
        },
        "gates": gates,
        "all_pass": all(gates[g]["pass"] for g in order),
        "first_failing_gate": first_fail,
    }


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r_a = compute()
    r_b = compute()
    assert canonical(r_a) == canonical(r_b), "non-deterministic double-run"
    print(json.dumps(r_a, sort_keys=True, indent=2))
    print("Results-JSON sha256: " + hashlib.sha256(canonical(r_a).encode()).hexdigest())


if __name__ == "__main__":
    main()
