#!/usr/bin/env python3
"""
kelly_overbet_ruin.py — reference verifier for PROPOSAL 100 (round-22, UNRELATED
slot closer). Domain: information theory / mathematical finance — growth-optimal
capital allocation (Kelly 1956). Fleet-external pure-mechanism head.

The "overbet ruin" trap in repeated multiplicative betting: on a favorable
even-money bet (win prob p>1/2), staking a fraction f of current wealth each
round grows the ENSEMBLE (arithmetic-mean) wealth monotonically in f — so a
naive expected-value maximizer bets as much as possible — yet the TIME-AVERAGE
(a.s. per-round) growth rate g(f)=p*ln(1+f)+q*ln(1-f) peaks at a strictly
INTERIOR Kelly fraction f*=2p-1 and turns NEGATIVE past a ruin boundary f_c>f*.
Betting "bigger for bigger EV" (double-Kelly f=2f*) is a value trap: the typical
gambler's wealth decays to zero while the ensemble average balloons.

Gates (all >= 3 sigma unless noted):
  G1 overbet-trap headline: the growth-optimal fraction f* strictly beats the
     naive double-Kelly fraction F_OVER=2f* (g(f*)-g(F_OVER) >= 3s), and the
     trap fraction has NEGATIVE time-average growth while f* is positive.
  G2 interior optimum: g(f*) beats a timid fraction F_UNDER AND a near-all-in
     fraction F_MAX, each >= 3 sigma (f* is a genuine interior peak).
  G3 analytic-anchor MATCH: the simulated mean per-round growth at f* matches
     the closed form g(f*)=p*ln(1+f*)+q*ln(1-f*) within 3 sigma (|z| < 3).

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717      # proposal-owned pinned seed; SEEDLESS discipline
P_WIN = 0.6          # win probability of the favorable even-money bet (p>1/2)
N_PATHS = 100_000    # independent wealth trajectories (Monte-Carlo paths)
T_ROUNDS = 400       # bets per trajectory (time horizon)
GRID_STEP = 0.01     # bet-fraction grid resolution for analytic argmax
F_UNDER = 0.02       # timid under-bet comparison fraction
F_OVER = 0.40        # naive "double-Kelly" over-bet (= 2*f*): the trap policy
F_MAX = 0.90         # near-all-in catastrophic comparison fraction


def g_analytic(f):
    """Time-average (a.s.) per-round log-growth rate for stake fraction f."""
    q = 1.0 - P_WIN
    if f <= 0.0:
        return 0.0
    if f >= 1.0:
        return float("-inf")
    return P_WIN * math.log(1.0 + f) + q * math.log(1.0 - f)


def argmax_f():
    """Grid argmax of the analytic growth rate over f in (0,1)."""
    best_f, best_g = 0.0, g_analytic(0.0)
    steps = int(round(0.99 / GRID_STEP))
    for i in range(1, steps + 1):
        f = i * GRID_STEP
        gg = g_analytic(f)
        if gg > best_g:
            best_g, best_f = gg, f
    return best_f, best_g


def ruin_boundary():
    """Larger root f_c in (f*,1) of g(f)=0 by bisection (time-average ruin edge)."""
    lo, hi = 2.0 * P_WIN - 1.0, 0.999999
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if g_analytic(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def simulate(fractions, n, t, rng):
    """One coherent pass: the SAME coin sequence per path drives every fraction.

    Per path we count wins w ~ Binomial(t, P_WIN); realized per-round growth for
    a fraction f is G = (w*ln(1+f) + (t-w)*ln(1-f)) / t. Returns, per fraction,
    (mean_G, se_G, frac_paths_negative)."""
    logs = {f: (math.log(1.0 + f), math.log(1.0 - f)) for f in fractions}
    s = {f: 0.0 for f in fractions}
    s2 = {f: 0.0 for f in fractions}
    neg = {f: 0 for f in fractions}
    for _ in range(n):
        w = 0
        for _r in range(t):
            if rng.random() < P_WIN:
                w += 1
        loss = t - w
        for f in fractions:
            la, lb = logs[f]
            gi = (w * la + loss * lb) / t
            s[f] += gi
            s2[f] += gi * gi
            if gi < 0.0:
                neg[f] += 1
    out = {}
    for f in fractions:
        mean = s[f] / n
        var = max(s2[f] / n - mean * mean, 0.0)
        se = math.sqrt(var / n)
        out[f] = (mean, se, neg[f] / n)
    return out


def z_diff(a, sea, b, seb):
    se = math.sqrt(sea * sea + seb * seb)
    return (a - b) / se if se > 0 else float("inf")


def main():
    rng = random.Random(SEED)
    q = 1.0 - P_WIN

    f_star_analytic = 2.0 * P_WIN - 1.0        # Kelly fraction f* = p - q
    f_star_grid, g_star_grid = argmax_f()
    f_c = ruin_boundary()

    fractions = [F_UNDER, f_star_grid, F_OVER, F_MAX]
    sim = simulate(fractions, N_PATHS, T_ROUNDS, rng)

    g_star, se_star, neg_star = sim[f_star_grid]
    g_under, se_under, neg_under = sim[F_UNDER]
    g_over, se_over, neg_over = sim[F_OVER]
    g_max, se_max, neg_max = sim[F_MAX]

    # G1 overbet-trap headline: f* beats double-Kelly F_OVER, which itself ruins.
    z_g1 = z_diff(g_star, se_star, g_over, se_over)
    g1 = (z_g1 >= 3.0) and (g_over < 0.0) and (g_star > 0.0)

    # G2 interior optimum: f* beats timid F_UNDER AND near-all-in F_MAX.
    z_g2a = z_diff(g_star, se_star, g_under, se_under)
    z_g2b = z_diff(g_star, se_star, g_max, se_max)
    g2 = (z_g2a >= 3.0) and (z_g2b >= 3.0)

    # G3 analytic-anchor MATCH: sim mean growth at f* == closed-form g(f*).
    g_star_closed = g_analytic(f_star_grid)
    z_g3 = abs(g_star - g_star_closed) / se_star if se_star > 0 else float("inf")
    g3 = z_g3 < 3.0

    all_pass = g1 and g2 and g3

    # Descriptive ergodicity gap at the trap fraction (computed analytically to
    # avoid float overflow): ensemble arithmetic-mean wealth grows while the
    # typical (median) path decays.
    arith_mult_over = 1.0 + F_OVER * (2.0 * P_WIN - 1.0)   # E[W_{t+1}/W_t]
    log10_ensemble_over = T_ROUNDS * math.log10(arith_mult_over)
    median_wealth_over = math.exp(T_ROUNDS * g_over)

    results = {
        "params": {"SEED": SEED, "P_WIN": P_WIN, "N_PATHS": N_PATHS,
                   "T_ROUNDS": T_ROUNDS, "GRID_STEP": GRID_STEP,
                   "F_UNDER": F_UNDER, "F_OVER": F_OVER, "F_MAX": F_MAX},
        "policy": {"f_star_analytic": round(f_star_analytic, 6),
                   "f_star_grid": round(f_star_grid, 4),
                   "g_star_grid_analytic": round(g_star_grid, 6),
                   "f_ruin_boundary": round(f_c, 6)},
        "sim": {
            "g_star": round(g_star, 6), "se_star": round(se_star, 6),
            "g_under": round(g_under, 6), "se_under": round(se_under, 6),
            "g_over": round(g_over, 6), "se_over": round(se_over, 6),
            "g_max": round(g_max, 6), "se_max": round(se_max, 6),
            "g_star_closed": round(g_star_closed, 6),
            "neg_frac_star": round(neg_star, 6),
            "neg_frac_over": round(neg_over, 6),
        },
        "ergodicity_gap_at_F_OVER": {
            "arith_per_round_mult": round(arith_mult_over, 6),
            "log10_ensemble_mean_wealth": round(log10_ensemble_over, 4),
            "median_path_wealth": round(median_wealth_over, 6),
        },
        "gates": {
            "G1_overbet_trap": {"z": round(z_g1, 2), "pass": g1},
            "G2_interior": {"z_vs_under": round(z_g2a, 2),
                            "z_vs_max": round(z_g2b, 2), "pass": g2},
            "G3_anchor_match": {"z": round(z_g3, 2), "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("kelly_overbet_ruin_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
