#!/usr/bin/env python3
"""PROPOSAL 167 — MMR/Elo rating deflation: a competitive ladder's mean rating
is NOT conserved. Every game is a zero-sum transaction (the winner gains exactly
what the loser drops), so rating points can only enter or leave the pool WITH
players. Newcomers enter underrated at a provisional floor and, after climbing to
their true skill, retire carrying those accumulated points OUT — so a strictly
zero-sum ladder deflates in the long run (Elo, "Combating deflation"), with no
change in anyone's true skill, at a rate set by churn x the enter-low/retire-high
gap.

Firsthand verifier — stdlib only (math, json, hashlib, random). SEED pinned;
deterministic in-process double-run + cross-invocation identical. Prints the whole
results dict (pretty, indent=2, floats rounded 6 dp) then the sha256 of its
compact-canonical form (WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY posture; no JSON
written to disk).

Gates (APPROVE iff ALL hold, in order G1 -> G2 -> G3; z_gate=3.0):
  G1 deflation-real          — across R ladders the pool mean displayed-rating
                               drift is negative at >=3 sigma (z < -3), rejecting
                               the zero-sum => mean-stable folk null.
  G2 churn-ledger identity   — total displayed-rating change == points-in minus
                               points-out to float precision (|residual| < 1e-6);
                               play moves zero net points.
  G3 robustness deeper-floor — under a lower floor + shifted K/churn, deflation
                               persists at >=3 sigma AND deepens.
"""
import hashlib
import json
import math
import random

SEED = 20260717
Z_GATE = 3.0


def expected(ra, rb):
    return 1.0 / (1.0 + 10.0 ** ((rb - ra) / 400.0))


def run_ladder(seed, P, floor, mu, sigma, K, steps, conv_games, churn_every):
    rng = random.Random(seed)
    true = [rng.gauss(mu, sigma) for _ in range(P)]
    disp = list(true)
    games = [0] * P
    start_total = sum(disp)
    ledger_in = 0.0
    ledger_out = 0.0
    for t in range(1, steps + 1):
        a = rng.randrange(P)
        b = rng.randrange(P)
        while b == a:
            b = rng.randrange(P)
        pa = expected(disp[a], disp[b])
        p_true = expected(true[a], true[b])
        sa = 1.0 if rng.random() < p_true else 0.0
        d = K * (sa - pa)
        disp[a] += d
        disp[b] -= d
        games[a] += 1
        games[b] += 1
        if t % churn_every == 0:
            eligible = [i for i in range(P) if games[i] >= conv_games]
            if eligible:
                r = eligible[rng.randrange(len(eligible))]
                ledger_out += disp[r]
                true[r] = rng.gauss(mu, sigma)
                disp[r] = floor
                games[r] = 0
                ledger_in += floor
    end_total = sum(disp)
    drift_mean = (end_total - start_total) / P
    residual = (end_total - start_total) - (ledger_in - ledger_out)
    return drift_mean, residual


def summarize(vals):
    n = len(vals)
    m = sum(vals) / n
    var = sum((v - m) ** 2 for v in vals) / (n - 1)
    return m, math.sqrt(var), n


def zstat(mean, sd, n):
    if sd == 0.0:
        return 0.0
    return mean / (sd / math.sqrt(n))


def r6(x):
    return round(float(x), 6)


def run():
    R = 40
    P = 60
    steps = 15000
    conv_games = 40
    base = [run_ladder(SEED + i, P, 1000.0, 1500.0, 300.0, 32.0, steps, conv_games, 50) for i in range(R)]
    shift = [run_ladder(SEED + 777 + i, P, 700.0, 1500.0, 300.0, 24.0, steps, conv_games, 40) for i in range(R)]
    bd = [d for d, _ in base]
    br = [abs(res) for _, res in base]
    sd_ = [d for d, _ in shift]
    sr = [abs(res) for _, res in shift]
    bm, bsd, bn = summarize(bd)
    sm, ssd, sn = summarize(sd_)
    z_g1 = zstat(bm, bsd, bn)
    z_g3 = zstat(sm, ssd, sn)
    max_resid = max(max(br), max(sr))
    g1 = z_g1 < -Z_GATE
    g2 = max_resid < 1e-6
    g3 = (z_g3 < -Z_GATE) and (sm < bm)
    gates = [
        {"id": "G1", "name": "deflation_real", "pass": g1, "z": r6(z_g1)},
        {"id": "G2", "name": "churn_ledger_identity", "pass": g2, "residual": r6(max_resid)},
        {"id": "G3", "name": "robustness_deeper_floor", "pass": g3, "z": r6(z_g3)},
    ]
    order_pass = {"G1": g1, "G2": g2, "G3": g3}
    first_fail = next((k for k in ["G1", "G2", "G3"] if not order_pass[k]), None)
    return {
        "proposal": 167,
        "slot": "round-39 GAME",
        "head": "mmr_rating_deflation",
        "seed": SEED,
        "z_gate": Z_GATE,
        "params": {
            "replications": R,
            "pool_size": P,
            "steps": steps,
            "conv_games": conv_games,
            "skill_mu": 1500.0,
            "skill_sigma": 300.0,
            "baseline": {"floor": 1000.0, "K": 32.0, "churn_every": 50},
            "shifted": {"floor": 700.0, "K": 24.0, "churn_every": 40},
        },
        "baseline": {
            "mean_drift": r6(bm),
            "drift_sd": r6(bsd),
            "z_deflation": r6(z_g1),
            "max_identity_residual": r6(max(br)),
        },
        "shifted": {
            "mean_drift": r6(sm),
            "drift_sd": r6(ssd),
            "z_deflation": r6(z_g3),
            "max_identity_residual": r6(max(sr)),
        },
        "g1_deflation_real": {"pass": g1, "z_deflation": r6(z_g1), "null": "zero-sum => mean drift == 0"},
        "g2_churn_ledger_identity": {"pass": g2, "max_residual": r6(max_resid)},
        "g3_robustness_deeper_floor": {"pass": g3, "z_deflation": r6(z_g3), "baseline_drift": r6(bm), "shifted_drift": r6(sm), "deepens": sm < bm},
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
