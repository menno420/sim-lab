#!/usr/bin/env python3
"""PROPOSAL 183 — the kingmaker skill-inversion: adding a player who can no
longer win, but who still decides the outcome, flips the sign of skill. In a
3-player game the lowest qualifier is eliminated into a "kingmaker" role and the
top two become contenders; without the kingmaker the final is decided by skill,
so the stronger contender wins more than half the time. A SPITEFUL kingmaker
instead eliminates the standings LEADER -- and because standings track skill, the
leader is usually the stronger contender, so raw skill turns from an asset into a
liability: the stronger contender now wins LESS than half the time. Raw skill and
win rate become negatively correlated, and the inversion survives even when the
kingmaker acts spitefully only part of the time.

Firsthand verifier -- stdlib only (math, json, hashlib, random). SEED pinned;
deterministic in-process double-run + cross-invocation identical. Prints the whole
results dict (pretty, indent=2, floats rounded 6 dp) then the sha256 of its
compact-canonical form (WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY posture; no JSON
written to disk).

Gates (APPROVE iff ALL hold, in order G1 -> G2 -> G3; z_gate=3.0):
  G1 skill-is-real (no kingmaker) -- with a skill-decided final the stronger
                                    contender wins > 0.5 at >=3 sigma.
  G2 the inversion (spiteful kingmaker) -- with a fully spiteful kingmaker the
                                    stronger contender wins < 0.5 at >=3 sigma;
                                    skill's sign is flipped.
  G3 robustness (shifted skills, partial spite) -- under a wider skill spread and
                                    a kingmaker who acts only 60% of the time the
                                    inversion persists at >=3 sigma AND deepens
                                    below the baseline rate.
"""
import hashlib
import json
import math
import random

SEED = 20260717
Z_GATE = 3.0
N_GAMES = 200000


def run_condition(seed, n_games, mu, sigma, qnoise, scale, spite):
    rng = random.Random(seed)
    stronger_wins = 0
    for _ in range(n_games):
        s0 = rng.gauss(mu, sigma)
        s1 = rng.gauss(mu, sigma)
        s2 = rng.gauss(mu, sigma)
        s = (s0, s1, s2)
        q0 = s0 + rng.gauss(0.0, qnoise)
        q1 = s1 + rng.gauss(0.0, qnoise)
        q2 = s2 + rng.gauss(0.0, qnoise)
        q = (q0, q1, q2)
        km = min(range(3), key=lambda i: q[i])
        rest = [i for i in range(3) if i != km]
        a, b = rest[0], rest[1]
        leader = a if q[a] >= q[b] else b
        trailer = b if leader == a else a
        stronger = a if s[a] >= s[b] else b
        if rng.random() < spite:
            winner = trailer
        else:
            pa = 1.0 / (1.0 + math.exp(-(s[a] - s[b]) / scale))
            winner = a if rng.random() < pa else b
        if winner == stronger:
            stronger_wins += 1
    return stronger_wins / n_games


def zstat(p, n):
    se = math.sqrt(0.25 / n)
    return (p - 0.5) / se


def r6(x):
    return round(float(x), 6)


def run():
    n = N_GAMES
    p1 = run_condition(SEED + 11, n, 0.0, 1.0, 0.5, 1.0, 0.0)
    p2 = run_condition(SEED + 22, n, 0.0, 1.0, 0.5, 1.0, 1.0)
    p3 = run_condition(SEED + 33, n, 0.0, 1.5, 0.7, 1.0, 0.6)
    z1 = zstat(p1, n)
    z2 = zstat(p2, n)
    z3 = zstat(p3, n)
    g1 = (p1 > 0.5) and (z1 >= Z_GATE)
    g2 = (p2 < 0.5) and (z2 <= -Z_GATE)
    g3 = (p3 < 0.5) and (z3 <= -Z_GATE) and (p3 < p1)
    gates = [
        {"id": "G1", "name": "skill_is_real_no_kingmaker", "pass": g1, "z": r6(z1)},
        {"id": "G2", "name": "inversion_spiteful_kingmaker", "pass": g2, "z": r6(z2)},
        {"id": "G3", "name": "robustness_shifted_partial_spite", "pass": g3, "z": r6(z3)},
    ]
    order_pass = {"G1": g1, "G2": g2, "G3": g3}
    first_fail = next((k for k in ["G1", "G2", "G3"] if not order_pass[k]), None)
    return {
        "proposal": 183,
        "slot": "round-43 GAME",
        "head": "kingmaker_skill_inversion",
        "seed": SEED,
        "z_gate": Z_GATE,
        "n_games": n,
        "params": {
            "baseline": {"mu": 0.0, "sigma": 1.0, "qnoise": 0.5, "scale": 1.0, "spite": 0.0},
            "spiteful": {"mu": 0.0, "sigma": 1.0, "qnoise": 0.5, "scale": 1.0, "spite": 1.0},
            "shifted": {"mu": 0.0, "sigma": 1.5, "qnoise": 0.7, "scale": 1.0, "spite": 0.6},
        },
        "g1_skill_is_real": {"pass": g1, "stronger_win_rate": r6(p1), "z_vs_half": r6(z1), "null": "no kingmaker => stronger contender wins > 0.5"},
        "g2_inversion": {"pass": g2, "stronger_win_rate": r6(p2), "z_vs_half": r6(z2), "null": "spiteful kingmaker => stronger contender wins < 0.5"},
        "g3_robustness": {"pass": g3, "stronger_win_rate": r6(p3), "z_vs_half": r6(z3), "baseline_win_rate": r6(p1), "deepens": p3 < p1},
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
