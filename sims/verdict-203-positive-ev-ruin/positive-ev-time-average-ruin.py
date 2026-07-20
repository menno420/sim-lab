#!/usr/bin/env python3
"""Positive-expected-value ruin (ergodicity economics): a repeated multiplicative
bet with STRICTLY POSITIVE expected value (ensemble/arithmetic average per-round
multiplier > 1) drives the TYPICAL investor almost surely toward ruin, because
the TIME-AVERAGE (geometric) growth rate is NEGATIVE. The folk belief
"positive EV => take it and repeat" is exactly wrong under compounding.

Stdlib only (random, math, json, hashlib). Deterministic: SEED pinned; a fresh
random.Random(SEED) is created at the start of EACH full run, so both an
in-process double-run and separate cross-invocation reproduce byte-identical
output.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY — the compact-canonical
results dict's own sha256 IS the digest; it is not a field inside the dict.
"""
import json
import hashlib
import math
import random

SEED = 20260717
W0 = 1.0            # starting wealth
T = 100             # rounds per path
P = 20_000          # number of paths
Z_GATE = 3.0
ROUND_DP = 10       # fixed serialization precision for byte-stable floats

# Pinned world (base): up-multiplier U with prob 0.5, else down-multiplier D.
U_BASE = 1.5
D_BASE = 0.6
# Shifted robustness world: still positive EV, still negative geometric growth.
U_SHIFT = 1.6
D_SHIFT = 0.55


def mean_se(vals):
    """Sample mean and standard error of the mean (ddof=1)."""
    n = len(vals)
    m = math.fsum(vals) / n
    var = math.fsum((v - m) ** 2 for v in vals) / (n - 1)
    se = math.sqrt(var / n)
    return m, se


def simulate(rng, u, d):
    """Simulate P paths of T multiplicative rounds under a two-outcome world.

    Returns a dict of the pinned summary statistics for this world."""
    final_wealth = []
    time_avg_growth = []          # per-path (1/T)*ln(W_T/W0)
    simple_returns_sum = 0.0      # sum over all path-rounds of (multiplier-1)
    simple_returns_sq_sum = 0.0   # sum of squares, for SE across all path-rounds
    n_rounds = 0

    for _ in range(P):
        w = W0
        for _ in range(T):
            m = u if rng.random() < 0.5 else d
            w *= m
            r = m - 1.0
            simple_returns_sum += r
            simple_returns_sq_sum += r * r
            n_rounds += 1
        final_wealth.append(w)
        time_avg_growth.append((1.0 / T) * math.log(w / W0))

    mean_final = math.fsum(final_wealth) / P
    sorted_fw = sorted(final_wealth)
    # median of an even-length list = average of the two central order statistics
    mid = P // 2
    if P % 2 == 0:
        median_final = 0.5 * (sorted_fw[mid - 1] + sorted_fw[mid])
    else:
        median_final = sorted_fw[mid]

    mean_tag, se_tag = mean_se(time_avg_growth)

    # per-round simple return: mean and SE across ALL path-rounds
    mean_pr = simple_returns_sum / n_rounds
    var_pr = (simple_returns_sq_sum - n_rounds * mean_pr * mean_pr) / (n_rounds - 1)
    se_pr = math.sqrt(var_pr / n_rounds)

    frac_below_start = sum(1 for w in final_wealth if w < W0) / P
    frac_ruined_10pct = sum(1 for w in final_wealth if w < 0.1 * W0) / P

    # z-scores
    z_time_avg_neg = (-mean_tag) / se_tag if se_tag > 0 else float("inf")
    z_ev_pos = mean_pr / se_pr if se_pr > 0 else float("inf")
    z_below = (frac_below_start - 0.5) / math.sqrt(0.25 / P)

    return {
        "u": u,
        "d": d,
        "ensemble_expected_multiplier": round(0.5 * u + 0.5 * d, ROUND_DP),
        "geometric_per_round_multiplier": round(math.sqrt(u * d), ROUND_DP),
        "mean_final_wealth": round(mean_final, ROUND_DP),
        "median_final_wealth": round(median_final, ROUND_DP),
        "mean_time_avg_growth": round(mean_tag, ROUND_DP),
        "se_time_avg_growth": round(se_tag, ROUND_DP),
        "mean_per_round_simple_return": round(mean_pr, ROUND_DP),
        "se_per_round_simple_return": round(se_pr, ROUND_DP),
        "frac_below_start": round(frac_below_start, ROUND_DP),
        "frac_ruined_10pct": round(frac_ruined_10pct, ROUND_DP),
        "z_time_avg_negative": round(z_time_avg_neg, ROUND_DP),
        "z_ev_positive": round(z_ev_pos, ROUND_DP),
        "z_frac_below_start": round(z_below, ROUND_DP),
    }


def compute():
    # Fresh RNG per full run: reproducible in-process AND cross-invocation.
    rng = random.Random(SEED)

    base = simulate(rng, U_BASE, D_BASE)
    shift = simulate(rng, U_SHIFT, D_SHIFT)

    # G1: time-average growth NEGATIVE (base world)
    g1 = (base["mean_time_avg_growth"] < 0.0) and (base["z_time_avg_negative"] >= Z_GATE)
    # G2: arithmetic per-round EV POSITIVE (base world)
    g2 = (base["mean_per_round_simple_return"] > 0.0) and (base["z_ev_positive"] >= Z_GATE)
    # G3: typical investor RUINED — majority below start (base world)
    g3 = (base["frac_below_start"] > 0.5) and (base["z_frac_below_start"] >= Z_GATE)
    # G4: robustness/shift — the sign structure persists in the shifted world
    g4 = (
        (shift["mean_time_avg_growth"] < 0.0) and (shift["z_time_avg_negative"] >= Z_GATE)
        and (shift["mean_per_round_simple_return"] > 0.0) and (shift["z_ev_positive"] >= Z_GATE)
        and (shift["frac_below_start"] > 0.5) and (shift["z_frac_below_start"] >= Z_GATE)
    )

    all_pass = g1 and g2 and g3 and g4

    first_failing = None
    for name, ok in (("G1", g1), ("G2", g2), ("G3", g3), ("G4", g4)):
        if not ok:
            first_failing = name
            break

    return {
        "head": "positive-ev-time-average-ruin",
        "seed": SEED,
        "constants": {
            "W0": W0, "T": T, "P": P, "z_gate": Z_GATE,
            "u_base": U_BASE, "d_base": D_BASE,
            "u_shift": U_SHIFT, "d_shift": D_SHIFT,
        },
        "base_world": base,
        "shifted_world": shift,
        "gates": {
            "G1_time_average_negative": g1,
            "G2_arithmetic_ev_positive": g2,
            "G3_typical_investor_ruined": g3,
            "G4_robustness_shift": g4,
        },
        "first_failing_gate": first_failing,
        "all_pass": all_pass,
    }


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r1 = compute()
    r2 = compute()
    assert canonical(r1) == canonical(r2), "non-deterministic: double-run diverged"
    digest = hashlib.sha256(canonical(r1).encode("utf-8")).hexdigest()
    print(json.dumps(r1, indent=2))
    print("double_run_identical=true")
    print("all_pass=%s" % ("true" if r1["all_pass"] else "false"))
    b = r1["base_world"]
    s = r1["shifted_world"]
    print("G1_z(time_avg_negative,base)=%s" % b["z_time_avg_negative"])
    print("G2_z(ev_positive,base)=%s" % b["z_ev_positive"])
    print("G3_z(frac_below_start,base)=%s" % b["z_frac_below_start"])
    print("G4_z(time_avg_negative,shift)=%s" % s["z_time_avg_negative"])
    print("G4_z(ev_positive,shift)=%s" % s["z_ev_positive"])
    print("G4_z(frac_below_start,shift)=%s" % s["z_frac_below_start"])
    print("RESULTS_SHA256=%s" % digest)
    return 0 if r1["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
