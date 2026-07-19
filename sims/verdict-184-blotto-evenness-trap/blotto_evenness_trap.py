#!/usr/bin/env python3
"""PROPOSAL 171 — the Colonel Blotto evenness trap: in a symmetric resource-
allocation contest (B battlefields, equal budgets), spreading your budget EVENLY
across all fields is a losing strategy. A lopsided allocator that CONCEDES a
minority of fields (allocates zero) and OVERLOADS the rest wins strictly MORE
than half the battlefields against an equal-budget uniform splitter — and, more
sharply, keeps winning the majority even while spending LESS: a concede-and-
overload allocator holds >50% battlefield share against a uniform opponent up to
a budget DEFICIT approaching one half. Evenness wastes budget; the lopsided
(even disadvantaged) allocator wins the count. Documented Colonel Blotto result:
uniform division is not a best response; the weaker player can win a majority of
fields (Borel 1921; Roberson, "The Colonel Blotto game", 2006).

Firsthand verifier — stdlib only (math, json, hashlib, random). SEED pinned;
deterministic in-process double-run + cross-invocation identical. Prints the whole
results dict (pretty, indent=2, floats rounded 6 dp) then the sha256 of its
compact-canonical form (WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY posture; no JSON
written to disk).

Gates (APPROVE iff ALL hold, in order G1 -> G2 -> G3; z_gate=3.0):
  G1 evenness-beaten          — with EQUAL budgets, the concede-and-overload
                                allocator wins >0.5 battlefield share vs a uniform
                                splitter, at >=3 sigma across randomized
                                battlefield counts (rejects "equal budget => equal
                                0.5 share").
  G2 concede-arithmetic       — over a deterministic (B,k,deficit) sweep the real
     identity                   concede-and-overload game's share equals the
                                closed-form concede-arithmetic prediction with
                                EXACTLY zero mismatches; the majority-feasibility
                                deficit frontier approaches 1/2 as B grows.
  G3 robustness / hetero-value — under RANDOM field values AND a 40% budget deficit,
     deficit (shifted world)    the value-targeted concede-and-overload (concede the
                                cheapest fields, overload the dearest) still wins
                                >0.5 VALUE share at >=3 sigma AND deepens vs the
                                homogeneous equal-budget baseline.
"""
import hashlib
import json
import math
import random

SEED = 20260717
Z_GATE = 3.0


def value_share(alloc_r, alloc_u, values):
    won = 0.0
    tot = 0.0
    for ar, au, v in zip(alloc_r, alloc_u, values):
        tot += v
        if ar > au:
            won += v
        elif ar == au:
            won += 0.5 * v
    return won / tot


def concede_overload(B, concede_idx, budget):
    cset = set(concede_idx)
    keep = B - len(cset)
    per = budget / keep if keep > 0 else 0.0
    return [0.0 if i in cset else per for i in range(B)]


def summarize(vals):
    n = len(vals)
    m = sum(vals) / n
    var = sum((v - m) ** 2 for v in vals) / (n - 1) if n > 1 else 0.0
    return m, math.sqrt(var), n


def z_vs(vals, null):
    m, sd, n = summarize(vals)
    z = 0.0 if sd == 0.0 else (m - null) / (sd / math.sqrt(n))
    return m, sd, n, z


def r6(x):
    return round(float(x), 6)


def run_g1(R):
    rng = random.Random(SEED + 11)
    shares = []
    for _ in range(R):
        B = rng.randrange(8, 41)
        T = float(B)
        kmax = (B + 1) // 2 - 1
        concede = rng.sample(range(B), kmax)
        alloc_r = concede_overload(B, concede, T)
        alloc_u = [T / B] * B
        values = [1.0] * B
        shares.append(value_share(alloc_r, alloc_u, values))
    return shares


def run_g2_identity():
    mism = 0
    checks = 0
    for B in range(8, 41):
        T = float(B)
        alloc_u = [T / B] * B
        values = [1.0] * B
        for k in range(1, B):
            concede = list(range(k))
            keep = B - k
            for dm in range(0, 91, 5):
                d = dm / 100.0
                budget_r = (1.0 - d) * T
                alloc_r = concede_overload(B, concede, budget_r)
                sim = value_share(alloc_r, alloc_u, values)
                per_r = budget_r / keep
                per_u = T / B
                if per_r > per_u:
                    pred = keep / B
                elif per_r == per_u:
                    pred = 0.5 * keep / B
                else:
                    pred = 0.0
                checks += 1
                if abs(sim - pred) > 1e-12:
                    mism += 1
    return mism, checks


def deficit_frontier():
    fr = {}
    for B in (8, 20, 40):
        best = 0.0
        for dm in range(0, 100):
            d = dm / 100.0
            if any(d * B < k < B / 2.0 for k in range(1, B)):
                best = d
        fr[str(B)] = r6(best)
    return fr


def run_deficit_demo(R):
    rng = random.Random(SEED + 22)
    d = 0.4
    shares = []
    for _ in range(R):
        B = rng.randrange(12, 41)
        T = float(B)
        lo = int(math.floor(d * B)) + 1
        hi = (B + 1) // 2 - 1
        if hi < lo:
            continue
        k = rng.randint(lo, hi)
        concede = rng.sample(range(B), k)
        alloc_r = concede_overload(B, concede, (1.0 - d) * T)
        alloc_u = [T / B] * B
        values = [1.0] * B
        shares.append(value_share(alloc_r, alloc_u, values))
    return shares, d


def run_g3(R):
    rng = random.Random(SEED + 33)
    d = 0.4
    shares = []
    for _ in range(R):
        B = rng.randrange(8, 41)
        values = [rng.uniform(0.2, 5.0) for _ in range(B)]
        T = float(B)
        budget_r = (1.0 - d) * T
        k = int(math.floor(d * B)) + 1
        order = sorted(range(B), key=lambda i: values[i])
        concede = order[:k]
        alloc_r = concede_overload(B, concede, budget_r)
        alloc_u = [T / B] * B
        shares.append(value_share(alloc_r, alloc_u, values))
    return shares, d


def run():
    R1 = 300
    RD = 300
    R3 = 300
    g1_shares = run_g1(R1)
    g1_m, g1_sd, g1_n, g1_z = z_vs(g1_shares, 0.5)
    mism, checks = run_g2_identity()
    frontier = deficit_frontier()
    demo_shares, demo_d = run_deficit_demo(RD)
    demo_m, demo_sd, demo_n, demo_z = z_vs(demo_shares, 0.5)
    g3_shares, g3_d = run_g3(R3)
    g3_m, g3_sd, g3_n, g3_z = z_vs(g3_shares, 0.5)

    g1 = g1_z > Z_GATE and g1_m > 0.5
    g2 = mism == 0
    g3 = (g3_z > Z_GATE) and (g3_m > 0.5) and (g3_m > g1_m)

    gates = [
        {"id": "G1", "name": "evenness_beaten", "pass": g1, "z": r6(g1_z)},
        {"id": "G2", "name": "concede_arithmetic_identity", "pass": g2, "mismatches": mism},
        {"id": "G3", "name": "robustness_hetero_value_deficit", "pass": g3, "z": r6(g3_z)},
    ]
    order_pass = {"G1": g1, "G2": g2, "G3": g3}
    first_fail = next((k for k in ["G1", "G2", "G3"] if not order_pass[k]), None)
    return {
        "proposal": 171,
        "slot": "round-40 GAME",
        "head": "blotto_evenness_trap",
        "seed": SEED,
        "z_gate": Z_GATE,
        "params": {
            "battlefields_range": [8, 40],
            "budget_rule": "T = B (uniform allocation = 1.0 per field)",
            "g1_replications": R1,
            "deficit_demo_replications": RD,
            "g3_replications": R3,
            "deficit": 0.4,
            "value_dist_shifted": [0.2, 5.0],
        },
        "g1_evenness_beaten": {
            "pass": g1,
            "mean_share": r6(g1_m),
            "share_sd": r6(g1_sd),
            "z": r6(g1_z),
            "null": "equal budget => equal 0.5 battlefield share",
        },
        "g2_concede_arithmetic_identity": {
            "pass": g2,
            "mismatches": mism,
            "checks": checks,
            "deficit_frontier_max_d": frontier,
            "note": "analytic majority frontier d -> 1/2 as B grows (deficit*B < k < B/2)",
        },
        "deficit_demo": {
            "deficit": r6(demo_d),
            "mean_share": r6(demo_m),
            "share_sd": r6(demo_sd),
            "z": r6(demo_z),
            "note": "R spends 40% LESS and still wins the field majority",
        },
        "g3_robustness_hetero_value_deficit": {
            "pass": g3,
            "deficit": r6(g3_d),
            "mean_value_share": r6(g3_m),
            "share_sd": r6(g3_sd),
            "z": r6(g3_z),
            "baseline_share": r6(g1_m),
            "deepens": g3_m > g1_m,
        },
        "gates": gates,
        "all_pass": g1 and g2 and g3,
        "first_failing_gate": first_fail,
    }


def main():
    r1 = run()
    r2 = run()
    c1 = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    c2 = json.dumps(r2, sort_keys=True, separators=(",", ":"))
    assert c1 == c2, "in-process nondeterminism"
    digest = hashlib.sha256(c1.encode()).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + digest)


if __name__ == "__main__":
    main()
