#!/usr/bin/env python3
"""Polya urn -- reinforcement, yet a coin-toss finish.

Start an urn with 1 black + 1 white ball. Each step: draw one ball uniformly
at random, return it plus one extra ball of the SAME colour (positive
reinforcement -- "rich get richer"). Folk intuition: the process should average
out to its 1/2 starting ratio (law of large numbers), or an early leader should
run away to an extreme. Truth: the number of black draws after n steps is
EXACTLY uniform on {0..n}; the limiting black-share is uniform on [0,1] and its
dispersion never shrinks with n. Reinforcement defeats the LLN.

Deterministic, stdlib-only. SEED = 20260717. All gates pre-registered.
"""
import hashlib
import json
import random
from fractions import Fraction
from math import factorial, sqrt

SEED = 20260717
N_ENUM_MAX = 20          # exact DP verified for n = 1..20
N_MC = 200               # trajectory length for Monte-Carlo gates
M_MC = 20000             # number of Monte-Carlo trajectories
START_SYM = (1, 1)       # symmetric start -> uniform limit
START_SHIFT = (2, 1)     # asymmetric start -> Beta(2,1) limit, mean 2/3


def exact_law(a, b, n):
    """Exact law of #black-added after n draws (Fraction), start (a,b), +1 same."""
    dist = {a: Fraction(1)}          # {black_count: prob}
    for t in range(n):
        nxt = {}
        for black, p in dist.items():
            white = b + (t - (black - a))
            total = black + white     # = a + b + t
            pb = Fraction(black, total)
            nxt[black + 1] = nxt.get(black + 1, Fraction(0)) + p * pb
            nxt[black] = nxt.get(black, Fraction(0)) + p * (1 - pb)
        dist = nxt
    return [dist.get(a + k, Fraction(0)) for k in range(n + 1)]


def betabinom(alpha, beta, n, k):
    """Beta-binomial pmf with integer alpha,beta: P(K=k), k=0..n (Fraction)."""
    def B(x, y):
        return Fraction(factorial(x - 1) * factorial(y - 1), factorial(x + y - 1))
    C = Fraction(factorial(n), factorial(k) * factorial(n - k))
    return C * B(k + alpha, n - k + beta) / B(alpha, beta)


def mc_final_shares(a, b, n_draws, m, rng):
    shares = []
    for _ in range(m):
        black, white = a, b
        for _ in range(n_draws):
            if rng.randrange(black + white) < black:
                black += 1
            else:
                white += 1
        shares.append(black / (black + white))
    return shares


def mc_iid_shares(n_draws, m, rng):
    shares = []
    for _ in range(m):
        s = sum(1 for _ in range(n_draws) if rng.randrange(2) == 0)
        shares.append(s / n_draws)
    return shares


def mean(xs):
    return sum(xs) / len(xs)


def var(xs):
    mu = mean(xs)
    return sum((x - mu) ** 2 for x in xs) / (len(xs) - 1)


def compute():
    # --- exact gates (Fraction) ---
    max_dev_uniform = Fraction(0)
    for n in range(1, N_ENUM_MAX + 1):
        law = exact_law(1, 1, n)
        for k in range(n + 1):
            d1 = abs(law[k] - Fraction(1, n + 1))
            d2 = abs(law[k] - betabinom(1, 1, n, k))
            max_dev_uniform = max(max_dev_uniform, d1, d2)
    max_dev_shift = Fraction(0)
    for n in range(1, N_ENUM_MAX + 1):
        law = exact_law(2, 1, n)
        for k in range(n + 1):
            max_dev_shift = max(max_dev_shift, abs(law[k] - betabinom(2, 1, n, k)))
    sample_law_n3 = [str(x) for x in exact_law(1, 1, 3)]

    # --- Monte-Carlo gates ---
    rng = random.Random(SEED)
    polya = mc_final_shares(1, 1, N_MC, M_MC, rng)
    iid = mc_iid_shares(N_MC, M_MC, rng)
    v_obs = var(polya)
    v_iid = var(iid)
    v_null = 1.0 / (4 * N_MC)                    # LLN concentration null variance
    se_null = v_null * sqrt(2.0 / (M_MC - 1))    # sampling SE of an empirical variance
    z_signal = (v_obs - v_null) / se_null

    band = [k for k in range(N_MC + 1) if 1 / 3 <= (1 + k) / (N_MC + 2) <= 2 / 3]
    p_exact = len(band) / (N_MC + 1)             # exact-law middle-third probability
    rate = sum(1 for s in polya if 1 / 3 <= s <= 2 / 3) / M_MC
    se_a = sqrt(p_exact * (1 - p_exact) / M_MC)
    z_agree = (rate - p_exact) / se_a

    shift = mc_final_shares(2, 1, N_MC, M_MC, rng)
    mean_shift = mean(shift)
    se_mean = sqrt(var(shift) / M_MC)
    z_shift = (mean_shift - 0.5) / se_mean

    return {
        "head": "polya-urn-reinforcement-uniform-finish",
        "seed": SEED,
        "params": {"n_enum_max": N_ENUM_MAX, "n_mc": N_MC, "m_mc": M_MC,
                   "start_symmetric": list(START_SYM), "start_shift": list(START_SHIFT)},
        "G1_exact_uniform": {
            "n_range": [1, N_ENUM_MAX],
            "closed_form": "P(K_n=k)=1/(n+1)",
            "sample_law_n3": sample_law_n3,
            "max_abs_deviation": str(max_dev_uniform),
            "pass": max_dev_uniform == 0,
            "direction": "exact-agreement (Fraction, zero deviation)",
        },
        "G2_signal_dispersion_vs_lln": {
            "observed_var": round(v_obs, 10),
            "uniform_pred_var": round(1.0 / 12.0, 10),
            "lln_null_var": round(v_null, 10),
            "iid_observed_var": round(v_iid, 10),
            "se_null": round(se_null, 12),
            "z": round(z_signal, 4),
            "threshold": 3.0,
            "pass": z_signal >= 3.0,
            "direction": "high z = SIGNAL (dispersion does not vanish; LLN defeated by reinforcement)",
        },
        "G3_agreement_mc_matches_exact": {
            "mc_middle_third_rate": round(rate, 10),
            "exact_middle_third_prob": round(p_exact, 10),
            "se": round(se_a, 10),
            "abs_z": round(abs(z_agree), 4),
            "threshold": 3.0,
            "pass": abs(z_agree) < 3.0,
            "direction": "low |z| = AGREEMENT (Monte-Carlo converges to the exact uniform law)",
        },
        "G4_shift_asymmetric_start": {
            "exact_max_abs_deviation": str(max_dev_shift),
            "mc_mean_share": round(mean_shift, 10),
            "predicted_mean": round(2.0 / 3.0, 10),
            "z_vs_half": round(z_shift, 4),
            "threshold": 3.0,
            "pass": (max_dev_shift == 0) and (abs(z_shift) >= 3.0),
            "direction": "exact-agreement to Beta(2,1) + mean shifts many sigma from 1/2 (robustness/shift)",
        },
    }


def main():
    r1 = compute()
    r2 = compute()
    identical = (r1 == r2)
    r1["G5_determinism"] = {
        "in_process_double_run": "IDENTICAL" if identical else "DIVERGED",
        "pass": identical,
    }
    gates = ["G1_exact_uniform", "G2_signal_dispersion_vs_lln",
             "G3_agreement_mc_matches_exact", "G4_shift_asymmetric_start",
             "G5_determinism"]
    r1["all_gates_pass"] = all(r1[g]["pass"] for g in gates)
    print(json.dumps(r1, indent=2, sort_keys=True))
    canon = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    print("results_sha256: " + hashlib.sha256(canon.encode()).hexdigest())


if __name__ == "__main__":
    main()
