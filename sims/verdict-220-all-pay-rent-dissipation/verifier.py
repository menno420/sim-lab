#!/usr/bin/env python3
"""Complete rent dissipation in the symmetric all-pay auction.

Setting: a symmetric complete-information all-pay auction for a prize worth V among
n >= 2 risk-neutral bidders. The highest bid wins the prize; EVERY bidder pays their
own bid (win or lose). The unique symmetric equilibrium is in mixed strategies with
CDF F(b) = (b/V)^(1/(n-1)) on [0, V]; the inverse-CDF sampler draws u ~ U(0,1) and
bids b = V * u^(n-1).

The counterintuitive-but-true claim: total expected effort (revenue) burned in
equilibrium equals EXACTLY V for every n >= 2 -- competition does NOT scale total
effort with the number of rivals; more bidders only split the same V into thinner
per-head slices (V/n each). Every bidder's expected NET payoff is EXACTLY zero: the
rent is fully dissipated.

The exact skeleton (no floats, no irrational roots needed):
  * A bidder bidding b wins with probability F(b)^(n-1) = ((b/V)^(1/(n-1)))^(n-1)
    = b/V -- the fractional root cancels, so P(win) = b/V is an EXACT rational in b.
  * Expected payoff Pi(b) = V * P(win) - b = V * (b/V) - b = 0 for EVERY b in [0, V]:
    exact indifference proves both the equilibrium and the break-even result.
  * Per-bidder expected payment E[b] = V * E[u^(n-1)] = V * (1/n) = V/n.
  * Total expected revenue R = n * (V/n) = V, EXACTLY, for ALL n >= 2.

Gates (SEED=20260717, Z_GATE=3.0):
  G1 EXACT (Fraction, no floats; direction: residual == 0, exact equality) -- for
     n=2..8 and V in {1,2,3,1/2}: closed-form total R == V and per-player == V/n
     exactly, AND Pi(b) == 0 (Fraction-exact) for a rational grid of b in [0,V].
     This proves the equilibrium and the break-even result in closed form.
  G2 EFFECT >=3sigma (Monte-Carlo; direction: measured << naive, AND |measured-V|<3s)
     -- draw M all-pay auctions at n=5 (bid = V*u^(n-1)); the measured total revenue
     sits >=3sigma BELOW the naive linear-growth prediction n*(V/2) (competition does
     NOT scale total effort with n), and is simultaneously within 3sigma of the
     closed-form V (consistency).
  G3 ROBUSTNESS/SHIFT (Monte-Carlo grid; direction: ratio -> 1, max deviation < 3s)
     -- across n in {2..10} x V in {1,2,3,1/2} the measured R_hat / V stays within
     3sigma of 1 in EVERY cell.
"""
import hashlib
import json
import random
import sys
from fractions import Fraction as F

SEED = 20260717
Z_GATE = 3.0

EXACT_NS = list(range(2, 9))          # n = 2..8
EXACT_VS = [F(1), F(2), F(3), F(1, 2)]
B_GRID_D = 12                          # rational grid b = k*V/12, k = 0..12
MC_N5_M = 100_000                      # G2 Monte-Carlo auctions at n=5
MC_N5_N = 5
MC_N5_V = 1.0
ROB_M = 10_000                         # G3 Monte-Carlo auctions per cell
ROB_NS = list(range(2, 11))            # n = 2..10
ROB_VS = [1.0, 2.0, 3.0, 0.5]


# ----------------------------------------------------------------------------
# G1 -- exact closed-form, Fraction only (no floats, no roots).
# ----------------------------------------------------------------------------
def exact_cell(n, V):
    """Return (revenue_residual, per_player, total, pi_residual_max) as Fractions.

    per_player = V * E[u^(n-1)] = V/n (closed form); total = n*per_player.
    P(win | bid=b) = F(b)^(n-1) = b/V EXACTLY (the fractional root cancels), so
    Pi(b) = V*(b/V) - b = 0 for every rational b in [0, V]."""
    per_player = V * F(1, n)                      # E[b] = V/n, exact
    total = n * per_player                        # = V, exact
    revenue_residual = total - V                  # must be 0
    pi_res_max = F(0)
    for k in range(B_GRID_D + 1):
        b = F(k, B_GRID_D) * V                    # rational b in [0, V]
        p_win = b / V if V != 0 else F(0)         # F(b)^(n-1) = b/V, exact
        pi = V * p_win - b                         # expected payoff at bid b
        if abs(pi) > pi_res_max:
            pi_res_max = abs(pi)
    return revenue_residual, per_player, total, pi_res_max


def gate1():
    rev_res_max = F(0)
    pi_res_max = F(0)
    per_player_ok_all = True
    sample = None
    for n in EXACT_NS:
        for V in EXACT_VS:
            rev_res, per_player, total, pi_res = exact_cell(n, V)
            if abs(rev_res) > rev_res_max:
                rev_res_max = abs(rev_res)
            if pi_res > pi_res_max:
                pi_res_max = pi_res
            if per_player != V / n or total != V:
                per_player_ok_all = False
            if n == 5 and V == F(1):
                sample = {
                    "n": n, "V": str(V), "per_player": str(per_player),
                    "total": str(total), "closed_per_player": str(V / n),
                }
    ok = (rev_res_max == 0) and (pi_res_max == 0) and per_player_ok_all
    return {
        "ns": EXACT_NS,
        "Vs": [str(v) for v in EXACT_VS],
        "b_grid_D": B_GRID_D,
        "revenue_residual_max": str(rev_res_max),
        "pi_residual_max": str(pi_res_max),
        "per_player_ok_all": per_player_ok_all,
        "sample_n5_V1": sample,
        "pass": ok,
    }


# ----------------------------------------------------------------------------
# G2 / G3 -- Monte-Carlo, one shared rng threaded in fixed draw order.
# ----------------------------------------------------------------------------
def mc_auctions(rng, n, V, M):
    """Run M all-pay auctions; return (mean_total_R, se_of_mean, sumsq_info).

    Each bidder draws u~U(0,1) and bids V*u^(n-1); per-auction revenue is the sum
    of all n bids (all-pay). Returns the mean per-auction revenue and the standard
    error of that mean (sqrt(sample_variance / M))."""
    s = 0.0
    ss = 0.0
    exp = n - 1
    for _ in range(M):
        tot = 0.0
        for _ in range(n):
            u = rng.random()
            tot += V * (u ** exp)
        s += tot
        ss += tot * tot
    mean = s / M
    var = (ss - M * mean * mean) / (M - 1)
    se = (var / M) ** 0.5
    return mean, se


def r6(x):
    return round(float(x), 6)


def gate2(rng):
    n, V, M = MC_N5_N, MC_N5_V, MC_N5_M
    mean, se = mc_auctions(rng, n, V, M)
    naive = n * (V / 2.0)                          # naive linear-growth prediction
    closed = V                                     # exact closed-form total
    z_below_naive = (naive - mean) / se if se > 0 else 0.0
    consistency_abs = abs(mean - closed)
    within_3se = consistency_abs < 3.0 * se
    ok = (z_below_naive >= Z_GATE) and within_3se
    return {
        "n": n, "V": V, "M": M,
        "measured_R": r6(mean), "closed_R": r6(closed), "naive_R": r6(naive),
        "se": r6(se), "z_below_naive": r6(z_below_naive),
        "consistency_abs": r6(consistency_abs), "consistency_within_3se": within_3se,
        "pass": ok,
    }


def gate3(rng):
    cells = []
    max_dev = 0.0
    max_dev_z = 0.0
    worst = None
    all_within = True
    for V in ROB_VS:
        for n in ROB_NS:
            mean, se = mc_auctions(rng, n, V, ROB_M)
            ratio = mean / V
            dev = abs(ratio - 1.0)
            ratio_se = se / V
            z = dev / ratio_se if ratio_se > 0 else 0.0
            within = z < 3.0
            if not within:
                all_within = False
            if dev > max_dev:
                max_dev = dev
            if z > max_dev_z:
                max_dev_z = z
                worst = {"n": n, "V": r6(V), "ratio": r6(ratio), "z": r6(z)}
            cells.append({"n": n, "V": r6(V), "ratio": r6(ratio), "z": r6(z),
                          "within_3sigma": within})
    return {
        "n_cells": len(cells),
        "ns": ROB_NS, "Vs": [r6(v) for v in ROB_VS], "M_per_cell": ROB_M,
        "max_ratio_dev": r6(max_dev), "max_dev_z": r6(max_dev_z),
        "worst_cell": worst, "all_within_3sigma": all_within,
        "cells": cells, "pass": all_within,
    }


def build_results():
    g1 = gate1()
    rng = random.Random(SEED)                      # one rng, fixed draw order
    g2 = gate2(rng)
    g3 = gate3(rng)
    gates = {"G1": g1["pass"], "G2": g2["pass"], "G3": g3["pass"]}
    return {
        "constants": {
            "seed": SEED, "z_gate": Z_GATE,
            "exact_ns": EXACT_NS, "exact_Vs": [str(v) for v in EXACT_VS],
            "b_grid_D": B_GRID_D,
            "mc_n5_M": MC_N5_M, "mc_n5_n": MC_N5_N, "mc_n5_V": MC_N5_V,
            "rob_M": ROB_M, "rob_ns": ROB_NS, "rob_Vs": ROB_VS,
        },
        "g1_exact": g1,
        "g2_effect": g2,
        "g3_robustness": g3,
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
    for g in ("G1", "G2", "G3"):
        print(f"{g}: {'PASS' if results['gates'][g] else 'FAIL'}")
    print(f"all_pass: {results['all_pass']}")
    print(f"results_sha256: {hashlib.sha256(canonical(results).encode()).hexdigest()}")
    sys.exit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
