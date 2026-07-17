#!/usr/bin/env python3
"""
shop_reroll_ruin.py — reference verifier for PROPOSAL 099 (round-22, game slot).

The "reroll ruin" value trap in auto-battler / roguelike shops: a shop shows K
items per roll (each item's power ~ Uniform(0,1)); the player keeps the roll's
best item M iff M >= tau, else pays reroll cost C and rolls again. Net utility
U(tau) = M_kept - C * (rerolls performed).

Gates (all >= 3 sigma unless noted):
  G1 value-trap headline: greedy near-perfect rerolling (tau=TAU_GREEDY) is
     strictly worse than the optimal threshold tau*  (U(tau*)-U(greedy) >= 3s).
  G2 interior optimum: U(tau*) beats accept-first (tau=0) AND near-always-reroll
     (tau=TAU_MAX), each >= 3 sigma.
  G3 analytic-anchor MATCH: simulated E[rerolls] at tau* matches the geometric
     count tau*^K / (1 - tau*^K) within 3 sigma (|z| < 3).

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717      # proposal-owned pinned seed; SEEDLESS discipline
K = 3                # items shown per shop roll
C = 0.05             # reroll cost, in item-power units
N = 100_000          # Monte-Carlo episodes per evaluated policy
R_MAX = 500          # hard reroll cap (termination guard; tau<1 => P(accept)>0)
GRID_STEP = 0.01     # tau grid resolution for analytic argmax
TAU_GREEDY = 0.95    # "reroll for near-perfect" trap policy
TAU_MAX = 0.99       # near-always-reroll comparison policy


def analytic_U(tau):
    """Infinite-horizon expected net utility for threshold tau (iid U(0,1), best-of-K)."""
    if tau <= 0.0:
        return K / (K + 1.0)
    p = 1.0 - tau ** K
    e_rerolls = (tau ** K) / p
    e_M_given = (K / (K + 1.0)) * (1.0 - tau ** (K + 1)) / p
    return e_M_given - C * e_rerolls


def analytic_rerolls(tau):
    p = 1.0 - tau ** K
    return (tau ** K) / p


def argmax_tau():
    best_tau, best_u = 0.0, analytic_U(0.0)
    steps = int(round(0.99 / GRID_STEP))
    for i in range(1, steps + 1):
        tau = i * GRID_STEP
        u = analytic_U(tau)
        if u > best_u:
            best_u, best_tau = u, tau
    return best_tau, best_u


def simulate(tau, n, rng):
    """Monte-Carlo one policy. Returns (mean_U, se_U, mean_rerolls, se_rerolls)."""
    su = su2 = sr = sr2 = 0.0
    for _ in range(n):
        rerolls = 0
        m = max(rng.random() for _ in range(K))
        while m < tau and rerolls < R_MAX:
            rerolls += 1
            m = max(rng.random() for _ in range(K))
        u = m - C * rerolls
        su += u
        su2 += u * u
        sr += rerolls
        sr2 += rerolls * rerolls
    mu = su / n
    varu = max(su2 / n - mu * mu, 0.0)
    seu = math.sqrt(varu / n)
    mr = sr / n
    varr = max(sr2 / n - mr * mr, 0.0)
    ser = math.sqrt(varr / n)
    return mu, seu, mr, ser


def z_diff(a, sea, b, seb):
    se = math.sqrt(sea * sea + seb * seb)
    return (a - b) / se if se > 0 else float("inf")


def main():
    rng = random.Random(SEED)
    tau_star, u_star_analytic = argmax_tau()

    u_star, se_star, rr_star, se_rr_star = simulate(tau_star, N, rng)
    u_zero, se_zero, _, _ = simulate(0.0, N, rng)
    u_greedy, se_greedy, _, _ = simulate(TAU_GREEDY, N, rng)
    u_max, se_max, _, _ = simulate(TAU_MAX, N, rng)

    z_g1 = z_diff(u_star, se_star, u_greedy, se_greedy)
    g1 = z_g1 >= 3.0
    z_g2a = z_diff(u_star, se_star, u_zero, se_zero)
    z_g2b = z_diff(u_star, se_star, u_max, se_max)
    g2 = (z_g2a >= 3.0) and (z_g2b >= 3.0)
    rr_analytic = analytic_rerolls(tau_star)
    z_g3 = abs(rr_star - rr_analytic) / se_rr_star if se_rr_star > 0 else float("inf")
    g3 = z_g3 < 3.0

    all_pass = g1 and g2 and g3

    results = {
        "params": {"SEED": SEED, "K": K, "C": C, "N": N, "R_MAX": R_MAX,
                   "GRID_STEP": GRID_STEP, "TAU_GREEDY": TAU_GREEDY, "TAU_MAX": TAU_MAX},
        "policy": {"tau_star": round(tau_star, 4),
                   "U_star_analytic": round(u_star_analytic, 6)},
        "sim": {
            "U_star": round(u_star, 6), "se_star": round(se_star, 6),
            "U_zero": round(u_zero, 6), "se_zero": round(se_zero, 6),
            "U_greedy": round(u_greedy, 6), "se_greedy": round(se_greedy, 6),
            "U_max": round(u_max, 6), "se_max": round(se_max, 6),
            "rerolls_star": round(rr_star, 6), "se_rerolls_star": round(se_rr_star, 6),
            "rerolls_analytic": round(rr_analytic, 6),
        },
        "gates": {
            "G1_value_trap": {"z": round(z_g1, 2), "pass": g1},
            "G2_interior": {"z_vs_zero": round(z_g2a, 2), "z_vs_max": round(z_g2b, 2), "pass": g2},
            "G3_anchor_match": {"z": round(z_g3, 2), "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("shop_reroll_ruin_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
