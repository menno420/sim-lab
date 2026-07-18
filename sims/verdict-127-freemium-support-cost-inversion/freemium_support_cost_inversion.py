#!/usr/bin/env python3
"""PROPOSAL 114 - The freemium support-cost inversion.

VENTURE-domain mechanism (round-26 venture slot). Freemium / product-led-growth
unit economics.

Trap / counterintuitive result
------------------------------
A freemium business carries every free user at a support/infra cost c and earns
only on the fraction that converts to paid. The per-free-user contribution is

    marginal(i) = V * p(i) - c

where p(i) is the conversion probability of the i-th acquired free user and V is
the paid lifetime value. The catch: conversion probability DECLINES with
acquisition volume - the first free users are the highest-intent (they sought the
product out), and each marginal cohort is lower-intent than the last. Model the
decline as p(i) = P0 * exp(-K*i). Then the marginal contribution is DECREASING in
i and crosses zero at

    n_star = ln(V * P0 / c) / K,

so TOTAL contribution C(n) = sum_{i=1}^{n} (V * 1{convert_i} - c) is CONCAVE: it
rises to a peak at n_star and then FALLS, eventually going NEGATIVE once the
accumulated support cost of low-intent users outweighs their thin conversion
value. The signup-maximizing volume (acquire as many free users as you can,
N_MAX) sits FAR past the contribution-maximizing volume n_star - so a growth team
that optimizes signups drives a program that was worth +C(n_star) down through
zero into value destruction, even though every headline metric (signups, total
conversions, gross new logos) is still going up. Scaling free acquisition
destroys value abruptly once contribution crosses zero.

Design fix: cap paid free-tier acquisition at the contribution optimum
n_star = ln(V*P0/c)/K (equivalently, admit a marginal free cohort only while its
expected conversion clears the support-cost breakeven p >= c/V); spend the rest
of the budget on intent quality (targeting, qualification, activation), not raw
signup volume.

Gates (each an effect >= 3 sigma from its threshold, over TRIALS pinned trials;
z is computed on the ESTIMATED MEAN via its standard error se = std/sqrt(TRIALS),
the P104/P105/P106/P107/P108/P109/P110/P111/P112/P113 /se convention):
  G1  contribution inversion (headline)  mean(C(n_star) - C(N_MAX)) at declining intent  >= DROP_MIN
  G2  declining-intent necessity control mean(C(N_MAX) - C(n_star)) at FLAT top-intent   >  0 (scaling HELPS)
  G3  closed-form anchor MATCH           sim C(n_star), C(N_MAX) match V*S(n) - c*n       (|z| < 3)

Determinism: SEED pinned; a canonical results dict is hashed with sha256 and must
reproduce byte-for-byte across runs. Exit 0 iff all gates pass.

stdlib only: random, math, json, hashlib.
"""

import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 400        # pinned Monte-Carlo trials
SIGMA = 3.0         # gate strength

P0 = 0.10           # top-intent conversion probability (first free user)
K = 0.001           # intent-decay rate per acquired free user
V = 100.0           # paid lifetime value per conversion
C_SUPPORT = 2.0     # support / infra cost carried per free user
N_MAX = 6000        # signup-maximizing volume ("acquire as many free users as we can")

DROP_MIN = 1000.0   # honest floor: over-scaling from n_star to N_MAX must destroy at least this much contribution

# Contribution optimum: marginal V*p(i) - c crosses zero where p(i) = c/V.
# n_star_cf = ln(V*P0/c)/K ; the integer argmax of C(n) is floor(n_star_cf).
N_STAR_CF = math.log(V * P0 / C_SUPPORT) / K
N_OPT = int(math.floor(N_STAR_CF))   # last free user with positive marginal contribution


def s_expected(n):
    """Closed-form expected cumulative conversions over users 1..n: sum P0*e^{-K*i}."""
    if n <= 0:
        return 0.0
    return P0 * (1.0 - math.exp(-K * n)) / (math.exp(K) - 1.0)


def cf_contribution(n):
    """Closed-form expected total contribution C(n) = V*S(n) - c*n under declining intent."""
    return V * s_expected(n) - C_SUPPORT * n


def trial(flat):
    """One trial. Returns (C_at_n_opt, C_at_n_max).

    flat=False: conversion probability declines with volume, p(i)=P0*e^{-K*i}.
    flat=True : conversion probability held at the TOP-intent level P0 for every
                user (the necessity control) - marginal V*P0-c > 0 for all i, so
                contribution is strictly increasing and the inversion vanishes.
    """
    total = 0.0
    c_opt = 0.0
    for i in range(1, N_MAX + 1):
        p = P0 if flat else P0 * math.exp(-K * i)
        if random.random() < p:
            total += V
        total -= C_SUPPORT
        if i == N_OPT:
            c_opt = total
    return c_opt, total


def mean_std(xs):
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var)


def run():
    random.seed(SEED)

    # Declining-intent condition (the mechanism).
    dec_opt, dec_max = [], []
    for _ in range(TRIALS):
        co, cm = trial(flat=False)
        dec_opt.append(co)
        dec_max.append(cm)

    # Flat top-intent control (necessity): scaling should HELP here.
    flat_opt, flat_max = [], []
    for _ in range(TRIALS):
        co, cm = trial(flat=True)
        flat_opt.append(co)
        flat_max.append(cm)

    def se(sd):
        return sd / math.sqrt(TRIALS)

    # G1: over-scaling destroys value under declining intent.
    drop = [o - m for o, m in zip(dec_opt, dec_max)]
    drop_m, drop_s = mean_std(drop)
    drop_se = se(drop_s)
    z1 = (drop_m - DROP_MIN) / drop_se if drop_se > 0 else float("inf")
    g1 = drop_m >= DROP_MIN and z1 >= SIGMA

    # G2: under FLAT top-intent the SAME over-scaling RAISES contribution (>0).
    gain = [m - o for o, m in zip(flat_opt, flat_max)]
    gain_m, gain_s = mean_std(gain)
    gain_se = se(gain_s)
    z2 = (gain_m - 0.0) / gain_se if gain_se > 0 else float("inf")
    g2 = gain_m > 0.0 and z2 >= SIGMA

    # G3: closed-form anchor match at both volumes (declining intent).
    do_m, do_s = mean_std(dec_opt)
    dm_m, dm_s = mean_std(dec_max)
    do_se = se(do_s)
    dm_se = se(dm_s)
    cf_opt = cf_contribution(N_OPT)
    cf_max = cf_contribution(N_MAX)
    z3a = abs(do_m - cf_opt) / do_se if do_se > 0 else 0.0
    z3b = abs(dm_m - cf_max) / dm_se if dm_se > 0 else 0.0
    g3 = z3a < SIGMA and z3b < SIGMA

    results = {
        "proposal": 114,
        "domain": "venture",
        "slot": "round-26-venture",
        "seed": SEED,
        "trials": TRIALS,
        "sigma": SIGMA,
        "params": {
            "P0": P0, "K": K, "V": V, "c_support": C_SUPPORT,
            "N_MAX": N_MAX, "N_OPT": N_OPT, "DROP_MIN": DROP_MIN,
        },
        "observed": {
            "C_opt_dec_mean": round(do_m, 6), "C_opt_dec_se": round(do_se, 6),
            "C_max_dec_mean": round(dm_m, 6), "C_max_dec_se": round(dm_se, 6),
            "drop_mean": round(drop_m, 6), "drop_se": round(drop_se, 6),
            "flat_gain_mean": round(gain_m, 6), "flat_gain_se": round(gain_se, 6),
        },
        "closed_form": {
            "n_star": round(N_STAR_CF, 6),
            "C_opt": round(cf_opt, 6),
            "C_max": round(cf_max, 6),
            "breakeven_conv_prob": round(C_SUPPORT / V, 6),
            "S_max": round(s_expected(N_MAX), 6),
        },
        "gates": {
            "G1_contribution_inversion": {
                "stat": "mean_contribution_drop_opt_to_max", "mean": round(drop_m, 6),
                "se": round(drop_se, 6), "threshold": DROP_MIN,
                "z": round(z1, 4), "pass": g1,
            },
            "G2_declining_intent_necessity": {
                "stat": "mean_flat_gain_opt_to_max", "mean": round(gain_m, 6),
                "se": round(gain_se, 6), "threshold": 0.0,
                "z": round(z2, 4), "pass": g2,
            },
            "G3_anchor_match": {
                "stat": "sim_vs_closed_form",
                "z_C_opt": round(z3a, 4), "z_C_max": round(z3b, 4), "pass": g3,
            },
        },
        "all_pass": bool(g1 and g2 and g3),
    }
    return results


def main():
    results = run()
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    print(canonical)
    print("sha256:", digest)
    obs = results["observed"]
    cf = results["closed_form"]
    print(
        f"declining intent: C(n_star={results['params']['N_OPT']})={obs['C_opt_dec_mean']} "
        f"-> C(N_MAX={results['params']['N_MAX']})={obs['C_max_dec_mean']}  "
        f"(over-scaling destroys {obs['drop_mean']}; C(N_MAX) < 0 = value destroyed)  |  "
        f"flat top-intent control: over-scaling ADDS {obs['flat_gain_mean']} (scaling helps)"
    )
    for name, g in results["gates"].items():
        print(f"{name}: pass={g['pass']}  {g}")
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
