#!/usr/bin/env python3
"""PROPOSAL 182 — the pay-to-play cramdown cliff (round-43 VENTURE slot).

Head: In a down round carrying a pay-to-play provision, the marginal pro-rata
dollar is the highest-return dollar on the cap table -- and the driver is the
CONVERSION penalty, not dilution. A non-participating investor is not merely
diluted; their preferred is stripped to common and the liquidation preference
is wiped. Conditional on a non-home-run exit (the modal down-round outcome),
participating preserves several times the value of its own pro-rata check, and
that preserved value comes overwhelmingly from avoiding the preferred->common
conversion rather than from avoiding dilution. The effect sharpens in cold
markets, where exits cluster near the preference stack.

Grounded in the pay-to-play / cramdown provision (non-participating preferred
converts to common on a down round) -- a real, heavily documented term.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (P127+ twist) -- the
compact-canonical results dict's own sha256 IS the digest; stdout is the pretty
(indent=2, sort_keys) dump; nothing is written to disk.

Stdlib only. Deterministic: one local random.Random(SEED); common random
numbers across the base/cold market draws. compute() is run twice in-process
and the two dicts asserted identical.
"""
import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 200_000
Z_GATE = 3.0
RATIO_GATE = 2.0      # G1: participation preserves >= 2x its own check, in-band
CONV_GATE = 1.5       # G2: conversion penalty >= 1.5x the dilution effect, in-band

# ---- pinned world (committed constants, all $M) ---------------------------
PHI_A_PART = 0.25       # A participates pro-rata -> holds 25% (12.5% old + 12.5% new)
PHI_A_DIL = 0.125       # A skips the round -> 25% diluted by the 50% new money
PRO_RATA = 1.25         # A's pro-rata of the $5M new round (0.25 * 5.0)
PREF_A_PART = 5.25      # participate: prior $4M + new $1.25M, each 1x
PREF_A_KEEP = 4.0       # no-pay-to-play counterfactual: keeps prior $4M pref, no pro-rata
PREF_TOTAL = 9.0        # all 1x preferred pari passu (A + others) when A holds preferred
SENIOR_CRAM = 5.0       # cramdown: others' new $5M 1x pref, senior to A-as-common
A_COMMON_SHARE = 0.25   # A's 12.5% is 25% of the 50% common pool after a cramdown
CONVERT_V = 10.0        # exit at which senior preferred convert (SENIOR_CRAM / 0.5 ownership)
DANGER_BAND = 15.0      # a non-home-run exit: V <= 15 (~1.7x the 9.0 pref stack)

BASE_MU, BASE_SIGMA = math.log(18.0), 0.95
COLD_MU, COLD_SIGMA = math.log(11.0), 1.20


def a_participate(v):
    """A does its pro-rata; 1x non-participating preferred, pari passu."""
    as_converted = PHI_A_PART * v
    pref_take = (PREF_A_PART / PREF_TOTAL) * min(v, PREF_TOTAL)
    return max(as_converted, pref_take)


def a_keep_no_p2p(v):
    """No pay-to-play: A skips its pro-rata but keeps the prior preferred; just diluted."""
    as_converted = PHI_A_DIL * v
    pref_take = (PREF_A_KEEP / PREF_TOTAL) * min(v, PREF_TOTAL)
    return max(as_converted, pref_take)


def a_crammed(v):
    """Pay-to-play cramdown: A converted to common, preference wiped, junior to SENIOR_CRAM."""
    if v >= CONVERT_V:            # senior preferred convert; A gets its as-converted common
        return PHI_A_DIL * v
    if v > SENIOR_CRAM:           # seniors take pref off the top; A splits the residual as common
        return A_COMMON_SHARE * (v - SENIOR_CRAM)
    return 0.0                    # exit below the senior stack; common gets nothing


def _mean_sd(xs):
    n = len(xs)
    m = sum(xs) / n
    if n < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var)


def _z_ge(xs, threshold):
    """One-sample z that E[xs] exceeds threshold."""
    m, sd = _mean_sd(xs)
    se = sd / math.sqrt(len(xs)) if sd > 0 else 0.0
    z = (m - threshold) / se if se > 0 else float("inf")
    return m, z


def _market(zdraws, mu, sigma):
    ret_band, conv_band, dil_band = [], [], []
    in_band = 0
    for z in zdraws:
        v = math.exp(mu + sigma * z)
        ap, ak, ac = a_participate(v), a_keep_no_p2p(v), a_crammed(v)
        if v <= DANGER_BAND:
            in_band += 1
            ret_band.append((ap - ac) / PRO_RATA)
            conv_band.append(ak - ac)      # value of avoiding the conversion
            dil_band.append(ap - ak)       # value of avoiding the dilution
    return {
        "band_prob": in_band / len(zdraws),
        "ret_band": ret_band,
        "conv_band": conv_band,
        "dil_band": dil_band,
    }


def compute():
    rng = random.Random(SEED)
    zdraws = [rng.gauss(0.0, 1.0) for _ in range(TRIALS)]  # common random numbers
    base = _market(zdraws, BASE_MU, BASE_SIGMA)
    cold = _market(zdraws, COLD_MU, COLD_SIGMA)

    # G1 -- in-band participation return >= RATIO_GATE at >= Z_GATE sigma
    g1_mean, g1_z = _z_ge(base["ret_band"], RATIO_GATE)
    g1 = (g1_mean >= RATIO_GATE) and (g1_z >= Z_GATE)

    # G2 -- conversion premium >= CONV_GATE x dilution premium, in-band, at >= Z_GATE sigma
    prem = [c - CONV_GATE * d for c, d in zip(base["conv_band"], base["dil_band"])]
    conv_mean, _ = _mean_sd(base["conv_band"])
    dil_mean, _ = _mean_sd(base["dil_band"])
    _, g2_z = _z_ge(prem, 0.0)
    conv_over_dil = conv_mean / dil_mean if dil_mean > 0 else float("inf")
    g2 = (conv_over_dil >= CONV_GATE) and (g2_z >= Z_GATE)

    # G3 -- cold market raises danger-band exposure (two-proportion z); dominance persists
    p_b, p_c = base["band_prob"], cold["band_prob"]
    p_pool = (p_b + p_c) / 2.0
    se_pool = math.sqrt(p_pool * (1.0 - p_pool) * (2.0 / TRIALS)) if 0 < p_pool < 1 else 0.0
    g3_z = (p_c - p_b) / se_pool if se_pool > 0 else float("inf")
    c_conv_mean, _ = _mean_sd(cold["conv_band"])
    c_dil_mean, _ = _mean_sd(cold["dil_band"])
    cold_conv_over_dil = c_conv_mean / c_dil_mean if c_dil_mean > 0 else float("inf")
    g3 = (p_c > p_b) and (g3_z >= Z_GATE) and (cold_conv_over_dil >= CONV_GATE)

    all_pass = g1 and g2 and g3
    return {
        "proposal": 182,
        "head": "pay-to-play cramdown cliff: conditional on a modest exit the marginal pro-rata dollar is the highest-return dollar, driven by the preferred->common conversion (not dilution), and it sharpens in cold markets",
        "seed": SEED,
        "trials": TRIALS,
        "danger_band": DANGER_BAND,
        "pro_rata_check": PRO_RATA,
        "base_median_exit": round(math.exp(BASE_MU), 6),
        "cold_median_exit": round(math.exp(COLD_MU), 6),
        "gate_G1_ret_band_mean": round(g1_mean, 6),
        "gate_G1_ret_band_z": round(g1_z, 6),
        "gate_G1_ratio_gate": RATIO_GATE,
        "gate_G1_pass": g1,
        "gate_G2_conv_mean": round(conv_mean, 6),
        "gate_G2_dil_mean": round(dil_mean, 6),
        "gate_G2_conv_over_dil": round(conv_over_dil, 6),
        "gate_G2_z": round(g2_z, 6),
        "gate_G2_conv_gate": CONV_GATE,
        "gate_G2_pass": g2,
        "gate_G3_base_band_prob": round(p_b, 6),
        "gate_G3_cold_band_prob": round(p_c, 6),
        "gate_G3_band_prob_z": round(g3_z, 6),
        "gate_G3_cold_conv_over_dil": round(cold_conv_over_dil, 6),
        "gate_G3_pass": g3,
        "all_pass": all_pass,
    }


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def main():
    r1 = compute()
    r2 = compute()
    assert r1 == r2, "non-deterministic: in-process double-run diverged"
    digest = hashlib.sha256(canonical(r1).encode("utf-8")).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256 " + digest)
    raise SystemExit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
