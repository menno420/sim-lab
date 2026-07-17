#!/usr/bin/env python3
"""
referral_value_trap.py  --  sim-lab verifier for "The referral-bonus value trap".

Counterintuitive claim: the referral bonus that maximizes the viral coefficient
R0 is strictly LARGER than the bonus that maximizes profit. Because total signups
grow as S/(1-R0) (subcritical Galton-Watson geometric anchor), pushing R0 toward 1
is ruinously expensive, so profit has a hard INTERIOR optimum b* strictly below the
virality-maximizing bonus. "Tune for maximum virality" therefore overspends.

Model (Galton-Watson, subcritical):
  - Seed cohort of S users (generation 0).
  - Each user makes K independent referral attempts; each attempt converts a new
    signup with prob q(b).  Offspring ~ Binomial(K, q(b)); mean offspring
    m(b) = K*q(b) = R0(b).  Params keep m(b) < 1 across the whole grid.
  - Saturating bonus response:  q(b) = q_max * (1 - exp(-b/b0)),  b >= 0.
  - Bonus b paid to the referrer per SUCCESSFUL referral (per realized offspring).
  - Margin M = net value per signup (LTV net of other CAC).

Analytic anchors (reproduced by the simulation):
  - E[T] = S / (1 - m(b))                      # total signups, incl. seed
  - E[R] = E[T] - S = S*m(b) / (1 - m(b))      # referred signups (offspring)
  - Pi(b) = M*E[T] - b*E[R] = S*(M - b*m(b)) / (1 - m(b))
  - b_viral = largest tested bonus (m monotone increasing -> R0 max at grid top)
  - b*      = argmax over the fine bonus grid of the analytic Pi(b) (strictly interior)

Per-replication profit is  Pi_rep = M*T - b*(T - S) = (M-b)*T + b*S  (T = simulated
total signups for that cohort replication).

stdlib only: random, math, json, hashlib, bisect.
"""

import random
import math
import json
import hashlib
from bisect import bisect_left

# ----------------------------------------------------------------------------
# Pinned parameters (all chosen so m(b) < 1 on the grid, b* strictly interior,
# and every gate clears with a comfortable >=3-sigma margin).
# ----------------------------------------------------------------------------
SEED  = 20260717          # fixed integer seed -> fully deterministic run
S     = 1000              # seed cohort size (generation 0)
K     = 3                 # referral attempts per user (fixed integer)
Q_MAX = 0.25              # saturation prob per attempt; K*Q_MAX = 0.75 < 1 (subcritical cap)
B0    = 2.0               # bonus half-saturation scale
M     = 10.0              # net margin (value) per signup
N     = 2000              # Monte-Carlo replications (cohorts) per bonus level

# Pinned fine bonus grid: 0.0, 0.1, ..., 8.0
GRID  = [round(0.1 * i, 1) for i in range(0, 81)]

# Bracketing high bonus for the interior-peak gate G2 (b* < B_HI < b_viral).
B_HI  = 6.0


# ----------------------------------------------------------------------------
# Analytic model functions
# ----------------------------------------------------------------------------
def q_of_b(b):
    return Q_MAX * (1.0 - math.exp(-b / B0))

def m_of_b(b):            # mean offspring == R0
    return K * q_of_b(b)

def ET_analytic(b):       # expected total signups incl. seed
    return S / (1.0 - m_of_b(b))

def ER_analytic(b):       # expected referred signups (offspring)
    return ET_analytic(b) - S

def Pi_analytic(b):       # expected profit
    m = m_of_b(b)
    return S * (M - b * m) / (1.0 - m)


# ----------------------------------------------------------------------------
# Simulation:  Binomial(K, q) offspring per individual via a categorical draw
# (one random() per individual) built from the exact pmf; generation-by-
# generation until extinction.  Returns total signups T (incl. seed).
# ----------------------------------------------------------------------------
def build_cdf(q):
    """Cumulative distribution of Binomial(K, q) as an increasing list, last == 1.0."""
    cdf = []
    acc = 0.0
    for j in range(K + 1):
        pmf = math.comb(K, j) * (q ** j) * ((1.0 - q) ** (K - j))
        acc += pmf
        cdf.append(acc)
    cdf[-1] = 1.0  # guard against fp drift so bisect always resolves
    return cdf

def simulate_T(cdf):
    """One cohort replication -> total signups (all generations incl. seed)."""
    total = S
    current = S
    while current > 0:
        nxt = 0
        for _ in range(current):
            u = random.random()
            nxt += bisect_left(cdf, u)   # number of offspring for this individual
        total += nxt
        current = nxt
    return total

def run_level(b):
    """N replications at bonus b. Returns dict with profit & T summary stats."""
    q = q_of_b(b)
    cdf = build_cdf(q)
    sum_p = 0.0; sumsq_p = 0.0
    sum_t = 0.0; sumsq_t = 0.0
    for _ in range(N):
        T = simulate_T(cdf)
        p = (M - b) * T + b * S          # == M*T - b*(T - S)
        sum_p += p;  sumsq_p += p * p
        sum_t += T;  sumsq_t += T * T
    mean_p = sum_p / N
    # sample variance (unbiased); guard N==1
    var_p = (sumsq_p - N * mean_p * mean_p) / (N - 1) if N > 1 else 0.0
    var_p = max(var_p, 0.0)
    se_p = math.sqrt(var_p / N)
    mean_t = sum_t / N
    var_t = (sumsq_t - N * mean_t * mean_t) / (N - 1) if N > 1 else 0.0
    var_t = max(var_t, 0.0)
    se_t = math.sqrt(var_t / N)
    return {
        "b": b,
        "q": q,
        "m_R0": m_of_b(b),
        "mean_profit": mean_p,
        "se_profit": se_p,
        "mean_T": mean_t,
        "se_T": se_t,
        "analytic_profit": Pi_analytic(b),
        "analytic_ET": ET_analytic(b),
    }


def z_diff(a, sea, b, seb):
    """z for (a - b) with independent standard errors."""
    sd = math.sqrt(sea * sea + seb * seb)
    if sd == 0.0:
        return float("inf") if a != b else 0.0
    return (a - b) / sd


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    random.seed(SEED)

    # ---- analytic profit over the full grid -> b* and single-peak check ----
    profits = [Pi_analytic(b) for b in GRID]
    star_idx = max(range(len(GRID)), key=lambda i: profits[i])
    b_star   = GRID[star_idx]
    b_viral  = GRID[-1]          # largest tested bonus -> R0 max
    b_zero   = GRID[0]           # 0.0

    # single-peak (unimodal) verification on the grid
    inc_ok = all(profits[i] <= profits[i + 1] + 1e-9 for i in range(0, star_idx))
    dec_ok = all(profits[i] >= profits[i + 1] - 1e-9 for i in range(star_idx, len(GRID) - 1))
    single_peaked = inc_ok and dec_ok
    interior = (0 < star_idx < len(GRID) - 1)

    # subcritical check across whole grid
    max_m = max(m_of_b(b) for b in GRID)
    subcritical = max_m < 1.0

    print("=" * 78)
    print("REFERRAL-BONUS VALUE TRAP  --  sim-lab verifier")
    print("=" * 78)
    print("Parameters (pinned):")
    print(f"  SEED      = {SEED}")
    print(f"  S (seed cohort)      = {S}")
    print(f"  K (attempts/user)    = {K}")
    print(f"  q_max                = {Q_MAX}   (K*q_max = {K*Q_MAX} < 1 : subcritical cap)")
    print(f"  b0 (sat scale)       = {B0}")
    print(f"  M (margin/signup)    = {M}")
    print(f"  N (replications)     = {N}")
    print(f"  bonus grid           = [{GRID[0]} .. {GRID[-1]}] step 0.1  ({len(GRID)} pts)")
    print(f"  B_HI (bracket high)  = {B_HI}")
    print()
    print("Analytic anchors:")
    print("  q(b)   = q_max*(1 - exp(-b/b0))")
    print("  m(b)   = K*q(b) = R0(b)")
    print("  E[T]   = S/(1 - m(b))")
    print("  E[R]   = S*m(b)/(1 - m(b))")
    print("  Pi(b)  = M*E[T] - b*E[R] = S*(M - b*m(b))/(1 - m(b))")
    print()
    print(f"  max m(b) over grid   = {max_m:.6f}   subcritical(all m<1): {subcritical}")
    print(f"  Pi single-peaked on grid: {single_peaked}   b* strictly interior: {interior}")
    print()

    def line(tag, b):
        print(f"  {tag:<10} b={b:>5}  R0=m(b)={m_of_b(b):.6f}  "
              f"E[T]={ET_analytic(b):10.3f}  Pi(b)={Pi_analytic(b):12.3f}")

    print("Key bonus levels (analytic):")
    line("b=0",     b_zero)
    line("b*",      b_star)
    line("b_hi",    B_HI)
    line("b_viral", b_viral)
    print()
    print(f"  => b* = {b_star}  (R0*={m_of_b(b_star):.6f})   "
          f"b_viral = {b_viral}  (R0_viral={m_of_b(b_viral):.6f})   "
          f"b* != b_viral : {b_star != b_viral}")
    print()

    # ---- simulate the relevant levels ----
    print("Running Monte-Carlo simulation (this may take ~20-40s) ...")
    levels = {}
    for tag, b in [("b0", b_zero), ("bstar", b_star), ("bhi", B_HI), ("bviral", b_viral)]:
        levels[tag] = run_level(b)
        r = levels[tag]
        print(f"  simulated {tag:<7} b={b:>5}: "
              f"mean_profit={r['mean_profit']:12.3f} (se {r['se_profit']:8.4f})  "
              f"mean_T={r['mean_T']:10.3f} (se {r['se_T']:7.4f})  "
              f"[analytic Pi={r['analytic_profit']:.3f}, E[T]={r['analytic_ET']:.3f}]")
    print()

    L0, Ls, Lh, Lv = levels["b0"], levels["bstar"], levels["bhi"], levels["bviral"]

    # ---- GATES ----
    # G1 : value trap headline -- Pi(b*) exceeds Pi(b_viral) by >= 3 sigma
    z_g1 = z_diff(Ls["mean_profit"], Ls["se_profit"], Lv["mean_profit"], Lv["se_profit"])
    g1 = z_g1 >= 3.0

    # G2 : interior optimum -- Pi(b*) beats both Pi(0) and Pi(b_hi) by >= 3 sigma
    z_g2a = z_diff(Ls["mean_profit"], Ls["se_profit"], L0["mean_profit"], L0["se_profit"])
    z_g2b = z_diff(Ls["mean_profit"], Ls["se_profit"], Lh["mean_profit"], Lh["se_profit"])
    g2 = (z_g2a >= 3.0) and (z_g2b >= 3.0)

    # G3 : branching anchor consistency -- sim mean T matches S/(1-m(b*)) within 3 sigma
    z_g3 = abs(Ls["mean_T"] - ET_analytic(b_star)) / Ls["se_T"] if Ls["se_T"] > 0 else 0.0
    g3 = z_g3 < 3.0

    print("=" * 78)
    print("PRE-REGISTERED GATES")
    print("=" * 78)
    print(f"  G1  value trap (headline): Pi(b*) > Pi(b_viral) by >=3 sigma")
    print(f"      Pi*={Ls['mean_profit']:.3f}  Pi_viral={Lv['mean_profit']:.3f}  "
          f"diff={Ls['mean_profit']-Lv['mean_profit']:.3f}   z = {z_g1:.2f} sigma   "
          f"-> {'PASS' if g1 else 'FAIL'}")
    print(f"  G2  interior optimum: Pi(b*) > Pi(0) AND Pi(b*) > Pi(b_hi), each >=3 sigma")
    print(f"      vs b=0 : diff={Ls['mean_profit']-L0['mean_profit']:.3f}  z = {z_g2a:.2f} sigma")
    print(f"      vs b_hi: diff={Ls['mean_profit']-Lh['mean_profit']:.3f}  z = {z_g2b:.2f} sigma")
    print(f"      -> {'PASS' if g2 else 'FAIL'}")
    print(f"  G3  branching anchor consistency (MATCH): |E_sim[T] - S/(1-m(b*))| < 3 sigma")
    print(f"      E_sim[T]={Ls['mean_T']:.3f}  analytic={ET_analytic(b_star):.3f}  "
          f"|z| = {z_g3:.2f} sigma   -> {'PASS' if g3 else 'FAIL'}")
    print()
    all_pass = g1 and g2 and g3
    print(f"  ALL GATES PASS: {all_pass}")
    print("=" * 78)

    # ---- results JSON + sha256 ----
    results = {
        "params": {
            "SEED": SEED, "S": S, "K": K, "Q_MAX": Q_MAX, "B0": B0, "M": M,
            "N": N, "grid_min": GRID[0], "grid_max": GRID[-1], "grid_step": 0.1,
            "grid_n": len(GRID), "B_HI": B_HI,
        },
        "analytic": {
            "b_star": b_star, "R0_star": m_of_b(b_star),
            "Pi_star_analytic": Pi_analytic(b_star), "ET_star_analytic": ET_analytic(b_star),
            "b_viral": b_viral, "R0_viral": m_of_b(b_viral),
            "Pi_viral_analytic": Pi_analytic(b_viral),
            "b_zero": b_zero, "Pi_zero_analytic": Pi_analytic(b_zero),
            "b_hi": B_HI, "Pi_hi_analytic": Pi_analytic(B_HI),
            "max_m_over_grid": max_m, "subcritical": subcritical,
            "single_peaked": single_peaked, "interior": interior,
        },
        "sim": {
            k: {
                "b": v["b"], "mean_profit": v["mean_profit"], "se_profit": v["se_profit"],
                "mean_T": v["mean_T"], "se_T": v["se_T"],
            } for k, v in levels.items()
        },
        "gates": {
            "G1_value_trap": {"z_sigma": z_g1, "pass": g1},
            "G2_interior": {"z_vs_zero": z_g2a, "z_vs_bhi": z_g2b, "pass": g2},
            "G3_anchor_match": {"abs_z_sigma": z_g3, "pass": g3},
            "all_pass": all_pass,
        },
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    out_path = "referral_value_trap_results.json"
    with open(out_path, "w") as fh:
        fh.write(canonical)

    print(f"\nResults JSON written to: {out_path}")
    print(f"Results-JSON sha256: {digest}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
