#!/usr/bin/env python3
"""PROPOSAL 147 — Gresham currency hoarding: good money is hoarded out of
circulation, bad money circulates (round-34 GAME slot).

Phenomenon: a game economy issues TWO currencies at nominal parity — a STABLE
"good" currency (holds its value) and a DEPRECIATING "bad" currency (a holding
penalty melts a fraction GAMMA of any unspent bad balance each period; think a
soft currency the designers keep inflating, or a resource that decays if hoarded).
Both faucets mint SYMMETRIC nominal income (each period every player draws the
SAME distribution of good units and bad units), and TODAY both settle a real
expense at par (1 unit of either pays 1 real).

The folk belief: "issue a premium hard currency at par with the soft currency and
it will circulate and drive the economy — two interchangeable currencies at
parity spend equally." Under Gresham's law (bad money drives out good), rational
players do the opposite: they SETTLE with the melting bad currency FIRST (spend it
before it loses value) and HOARD the stable good currency, so the good currency's
circulation velocity COLLAPSES toward zero and the bad currency does almost all
the settlement — even though the two faucets are symmetric. Good money is driven
OUT of circulation, exactly as Gresham's law predicts.

The SIGN of the circulation gap (share of real settlement done in bad currency
minus share done in good currency) depends on spender RATIONALITY:
  * NAIVE world (proportional): players pay each expense in proportion to their
    current unit holdings, with NO currency preference. Because the good currency
    never melts it accumulates in wallets, so a proportional payer actually
    settles MORE in good than in bad — the circulation gap is NEGATIVE (good
    circulates more). NO Gresham effect.
  * RATIONAL world (hoarder): players pay the melting bad currency first and hoard
    the good one. The circulation gap is strongly POSITIVE — good is hoarded out of
    circulation. Gresham's law.

A model-dependence result (the P024 discipline): with no rational hoarding the
folk belief holds (good circulates); with rational hoarding the lever flips sign
and the good currency's velocity collapses.

Anchor: Gresham's law — "bad money drives out good"
(https://en.wikipedia.org/wiki/Gresham%27s_law).

Model note (declared): the two faucets are SYMMETRIC in nominal units (same draw
distribution for good and bad income each period) and both currencies settle
today's expense at par — the ONLY asymmetry is the holding penalty GAMMA on
UNSPENT bad currency (the depreciation that makes bad "bad"). This is the minimal
object that exhibits Gresham hoarding: absent the melt the currencies are
identical and no one prefers either; the melt alone (not any faucet or settlement
asymmetry) drives the good money out of circulation.

Pre-registered gates (APPROVE iff ALL hold, in order G1 -> G2 -> G3):
  G1  AGREEMENT : two independent halves of the R rational-world circulation gaps
                  produce the SAME headline gap within noise — the half-vs-half
                  difference has |z| < SIGMA_GATE (NO significant disagreement).
                  The estimator is stable.
  G2  CONTROL   : in the NAIVE (proportional) world the circulation gap
                  (share_bad - share_good) is NOT significantly positive
                  (z = gap/se < SIGMA_GATE). Without rational hoarding there is no
                  Gresham effect (good circulates at least as much as bad).
  G3  HEAD      : in the RATIONAL (hoarder) world the circulation gap is
                  SIGNIFICANTLY positive — z = gap/se >= SIGMA_GATE. Good money is
                  driven out of circulation; its velocity collapses.
"""

import hashlib
import json
import math
import random

SEED = 20260717
SIGMA_GATE = 3.0

N = 1000                 # players in the economy
T = 100                  # periods
R = 40                   # independent trials (per-trial seed offset from SEED)
INC_MAX = 2.0            # per-currency nominal income ~ Uniform[0, INC_MAX] (SYMMETRIC faucets)
E_MAX = 2.0             # per-period real expense ~ Uniform[0, E_MAX]
GAMMA = 0.90            # holding retention on UNSPENT bad currency (0.90 => 10%/period melt)

TRIAL_STRIDE = 7919      # per-trial seed offset multiplier (prime)


def simulate(policy, seed):
    """One economy run under a spending policy. Returns the settlement shares and
    per-currency velocities aggregated over all players and periods.

    Each period, every player draws SYMMETRIC nominal income (good units and bad
    units from the SAME distribution), then must settle a real expense. Settlement
    is at par (1 unit of either = 1 real). 'rational' pays the melting bad currency
    first and hoards good; 'naive' pays in proportion to current unit holdings.
    After settlement the UNSPENT bad balance melts by factor GAMMA (the depreciation
    that makes bad "bad"); good never melts.
    """
    rng = random.Random(seed)
    uniform = rng.uniform
    g_wallet = [0.0] * N
    b_wallet = [0.0] * N
    settle_good = 0.0
    settle_bad = 0.0
    recv_good = 0.0
    recv_bad = 0.0
    rational = policy == "rational"
    for _ in range(T):
        for i in range(N):
            gi = uniform(0.0, INC_MAX)
            bi = uniform(0.0, INC_MAX)
            g_wallet[i] += gi
            b_wallet[i] += bi
            recv_good += gi
            recv_bad += bi
            gw = g_wallet[i]
            bw = b_wallet[i]
            avail = gw + bw
            e = uniform(0.0, E_MAX)
            pay = e if e <= avail else avail          # cannot settle more than held
            if rational:
                from_bad = pay if pay <= bw else bw   # spend the melting currency first
                from_good = pay - from_bad
            elif avail > 0.0:
                from_good = pay * (gw / avail)         # proportional to unit holdings
                from_bad = pay * (bw / avail)
            else:
                from_good = 0.0
                from_bad = 0.0
            g_wallet[i] = gw - from_good
            b_wallet[i] = (bw - from_bad) * GAMMA      # unspent bad melts
            settle_good += from_good
            settle_bad += from_bad
    total_settle = settle_good + settle_bad
    share_good = settle_good / total_settle if total_settle > 0 else 0.0
    share_bad = settle_bad / total_settle if total_settle > 0 else 0.0
    vel_good = settle_good / recv_good if recv_good > 0 else 0.0
    vel_bad = settle_bad / recv_bad if recv_bad > 0 else 0.0
    return {
        "gap": share_bad - share_good,
        "share_good": share_good,
        "share_bad": share_bad,
        "vel_good": vel_good,
        "vel_bad": vel_bad,
    }


def _mean_se(values):
    """Sample mean and standard error of the mean."""
    n = len(values)
    mean = sum(values) / n
    if n > 1:
        var = sum((x - mean) ** 2 for x in values) / (n - 1)
    else:
        var = 0.0
    return mean, math.sqrt(var / n)


def _z(mean, se, null=0.0):
    return (mean - null) / se if se > 0 else float("inf")


def run_world(policy):
    """R trials under one spending policy; per-trial seed offset from SEED.

    The rational and naive worlds share the per-trial seed (common random numbers:
    identical income and expense draws), so their circulation gaps are a paired
    contrast at fixed randomness.
    """
    gaps = []
    share_good = []
    share_bad = []
    vel_good = []
    vel_bad = []
    for r in range(R):
        out = simulate(policy, SEED + r * TRIAL_STRIDE)
        gaps.append(out["gap"])
        share_good.append(out["share_good"])
        share_bad.append(out["share_bad"])
        vel_good.append(out["vel_good"])
        vel_bad.append(out["vel_bad"])
    return {
        "gaps": gaps,
        "share_good": sum(share_good) / R,
        "share_bad": sum(share_bad) / R,
        "vel_good": sum(vel_good) / R,
        "vel_bad": sum(vel_bad) / R,
    }


def run():
    naive = run_world("naive")
    rational = run_world("rational")

    # --- G1: estimator agreement (halves of the rational circulation gaps)
    gaps = rational["gaps"]
    half = R // 2
    a_mean, a_se = _mean_se(gaps[:half])
    b_mean, b_se = _mean_se(gaps[half:])
    se_ab = math.sqrt(a_se * a_se + b_se * b_se)
    z_g1 = (a_mean - b_mean) / se_ab if se_ab > 0 else 0.0
    g1 = abs(z_g1) < SIGMA_GATE

    # --- G2: control world (naive proportional) — gap NOT significantly positive
    c_mean, c_se = _mean_se(naive["gaps"])
    z_g2 = _z(c_mean, c_se)
    g2 = z_g2 < SIGMA_GATE

    # --- G3: head — rational hoarders, gap significantly positive (Gresham)
    r_mean, r_se = _mean_se(gaps)
    z_g3 = _z(r_mean, r_se)
    g3 = (r_mean > 0.0) and (z_g3 >= SIGMA_GATE)

    first_failing = None
    if not g1:
        first_failing = "G1"
    elif not g2:
        first_failing = "G2"
    elif not g3:
        first_failing = "G3"
    all_pass = g1 and g2 and g3

    def r6(x):
        return round(float(x), 6)

    return {
        "proposal": 147,
        "seed": SEED,
        "sigma_gate": SIGMA_GATE,
        "n": N,
        "t": T,
        "r": R,
        "params": {
            "inc_max": INC_MAX,
            "e_max": E_MAX,
            "gamma": GAMMA,
        },
        "naive_share_good": r6(naive["share_good"]),
        "naive_share_bad": r6(naive["share_bad"]),
        "naive_vel_good": r6(naive["vel_good"]),
        "naive_vel_bad": r6(naive["vel_bad"]),
        "rational_share_good": r6(rational["share_good"]),
        "rational_share_bad": r6(rational["share_bad"]),
        "rational_vel_good": r6(rational["vel_good"]),
        "rational_vel_bad": r6(rational["vel_bad"]),
        "g1_half_a_gap": r6(a_mean),
        "g1_half_b_gap": r6(b_mean),
        "g1_z": r6(z_g1),
        "g1_agreement": g1,
        "g2_naive_gap": r6(c_mean),
        "g2_se": r6(c_se),
        "g2_z": r6(z_g2),
        "g2_control": g2,
        "g3_rational_gap": r6(r_mean),
        "g3_se": r6(r_se),
        "g3_z": r6(z_g3),
        "g3_head": g3,
        "first_failing_gate": first_failing,
        "all_pass": all_pass,
    }


def main():
    results = run()
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    print(json.dumps(results, indent=2, sort_keys=True))
    print(f"Results-JSON sha256: {digest}")
    print(
        "G1 agreement    :",
        "PASS" if results["g1_agreement"] else "FAIL",
        f"(half_a-half_b, z={results['g1_z']:+.2f}, |z|<{SIGMA_GATE})",
    )
    print(
        "G2 control      :",
        "PASS" if results["g2_control"] else "FAIL",
        f"(naive gap={results['g2_naive_gap']:+.4f}, "
        f"z={results['g2_z']:+.2f}, not-sig-positive z<{SIGMA_GATE})",
    )
    print(
        "G3 head         :",
        "PASS" if results["g3_head"] else "FAIL",
        f"(rational gap={results['g3_rational_gap']:+.4f}, "
        f"z={results['g3_z']:+.2f}, z>={SIGMA_GATE})",
    )
    print("all_pass        :", results["all_pass"], "first_failing_gate:", results["first_failing_gate"])
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
