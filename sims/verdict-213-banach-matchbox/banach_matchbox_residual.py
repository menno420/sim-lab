#!/usr/bin/env python3
"""banach_matchbox_residual.py — Banach's matchbox problem verifier (stdlib only).

Two matchboxes, each initially N matches (one per pocket). Each pick chooses
left/right with probability 1/2 and removes a match. Eventually a chosen box is
found EMPTY. Let K = matches remaining in the OTHER box at that moment.

Closed form:
  P(K=k) = C(2N-k, N) * 2^(-(2N-k)),  k = 0..N.
  E[K]   = (2N+1) * C(2N,N) * 2^(-2N) - 1.
Asymptotically E[K] ~ 2*sqrt(N/pi) - 1.

The folk belief "symmetry => both boxes empty => K ~ 0" is WRONG: at N=50 the
other box still holds ~7 matches on average.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. The results dict
carries no self hash; sha256 over its compact-canonical JSON is the digest,
printed to stdout, never written to disk. An in-process double-run asserts the
two results dicts are byte-identical. SEED fixed. Exit 0 iff all gates hold.
"""

from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction
import random

SEED = 20260717
N_HEAD = 50
GRID = (10, 50, 200)
TRIALS = 2_000_000
Z_GATE = 3.0
RATIO_LO = Fraction(110, 100)  # 1.10
RATIO_HI = Fraction(120, 100)  # 1.20
TWO_OVER_SQRT_PI = 2.0 / math.sqrt(math.pi)  # ~1.1283791671


# ----------------------------------------------------------------------------
# Closed form (exact Fractions)
# ----------------------------------------------------------------------------
def closed_form_pmf(N: int) -> list[Fraction]:
    """P(K=k) = C(2N-k, N) * 2^(-(2N-k)) for k = 0..N, exact."""
    return [
        Fraction(math.comb(2 * N - k, N), 1) / Fraction(2) ** (2 * N - k)
        for k in range(N + 1)
    ]


def closed_form_EK(N: int) -> Fraction:
    """E[K] = (2N+1) * C(2N,N) * 2^(-2N) - 1, exact."""
    return (
        Fraction((2 * N + 1) * math.comb(2 * N, N), 1) / Fraction(2) ** (2 * N)
        - 1
    )


# ----------------------------------------------------------------------------
# Exact forward DP (no sampling) — enumerate states (a,b) = matches drawn from
# L, R; process in increasing (a+b) order with exact Fraction probability mass.
# ----------------------------------------------------------------------------
def exact_dp_pmf(N: int) -> list[Fraction]:
    """Exact enumeration of P(K=k) via forward DP over drawn-count states."""
    mass: dict[tuple[int, int], Fraction] = {(0, 0): Fraction(1)}
    kbin = [Fraction(0) for _ in range(N + 1)]
    half = Fraction(1, 2)
    # Process states in increasing (a+b) order so each state's mass is complete
    # before it is spent. Drive the sweep by the total-drawn layer s = a + b,
    # from 0 to 2N (a dict cannot be extended while iterating a fixed sort).
    for s in range(0, 2 * N + 1):
        for (a, b) in [ab for ab in mass if ab[0] + ab[1] == s]:
            p = mass[(a, b)]
            if p == 0:
                continue
            if a < N and b < N:
                mass[(a + 1, b)] = mass.get((a + 1, b), Fraction(0)) + p * half
                mass[(a, b + 1)] = mass.get((a, b + 1), Fraction(0)) + p * half
            elif a == N and b < N:
                # continue on the right; left pick finds L empty -> K = N - b
                mass[(a, b + 1)] = mass.get((a, b + 1), Fraction(0)) + p * half
                kbin[N - b] += p * half
            elif b == N and a < N:
                # continue on the left; right pick finds R empty -> K = N - a
                mass[(a + 1, b)] = mass.get((a + 1, b), Fraction(0)) + p * half
                kbin[N - a] += p * half
            else:  # a == N and b == N: both moves terminal -> K = 0
                kbin[0] += p
    return kbin


# ----------------------------------------------------------------------------
# Monte Carlo
# ----------------------------------------------------------------------------
def monte_carlo(N: int, trials: int) -> tuple[float, float, float]:
    """Seeded simulation; returns (sim_mean, sim_var, se)."""
    rng = random.Random(SEED)
    total = 0
    total_sq = 0
    for _ in range(trials):
        a = 0
        b = 0
        while True:
            if rng.random() < 0.5:  # pick left
                if a == N:
                    k = N - b
                    break
                a += 1
            else:  # pick right
                if b == N:
                    k = N - a
                    break
                b += 1
        total += k
        total_sq += k * k
    sim_mean = total / trials
    sim_var = total_sq / trials - sim_mean * sim_mean
    se = math.sqrt(sim_var / trials)
    return sim_mean, sim_var, se


# ----------------------------------------------------------------------------
# Deterministic full computation -> canonical results dict
# ----------------------------------------------------------------------------
def compute() -> dict:
    # G1 EXACTLY-TRUE: closed form == exact DP, elementwise, for N in {10,50}.
    g1_pass = True
    g1_detail = {}
    for N in (10, 50):
        cf = closed_form_pmf(N)
        dp = exact_dp_pmf(N)
        pmf_equal = cf == dp
        ek_closed = closed_form_EK(N)
        ek_from_dp = sum(k * dp[k] for k in range(N + 1))
        ek_equal = ek_closed == ek_from_dp
        sum_one = sum(dp) == 1
        g1_detail[str(N)] = {
            "pmf_equal": pmf_equal,
            "ek_equal": ek_equal,
            "sum_is_one": sum_one,
        }
        g1_pass = g1_pass and pmf_equal and ek_equal and sum_one

    # Monte Carlo at the head N.
    ek_closed_head = closed_form_EK(N_HEAD)
    sim_mean, sim_var, se = monte_carlo(N_HEAD, TRIALS)

    # G2 ≥3σ SIGNAL (folk refutation): null E[K]=0.
    z2 = sim_mean / se
    g2_pass = z2 >= Z_GATE

    # G3 AGREEMENT (|z|<3) with the closed form.
    z3 = (sim_mean - float(ek_closed_head)) / se
    g3_pass = abs(z3) < Z_GATE

    # G4 ROBUSTNESS/SHIFT: ratio_N = (E[K]+1)/sqrt(N), band + monotone decrease
    # toward 2/sqrt(pi).
    ratios_exact = {}
    ratios_float = {}
    for N in GRID:
        r = (closed_form_EK(N) + 1) / Fraction(1)  # exact numerator part
        # ratio = (E[K]+1)/sqrt(N); sqrt(N) irrational -> compare as float.
        ratio_val = (float(closed_form_EK(N)) + 1.0) / math.sqrt(N)
        ratios_exact[str(N)] = r  # (E[K]+1) exact, for reference
        ratios_float[str(N)] = ratio_val
    in_band = all(
        RATIO_LO <= Fraction(str(round(ratios_float[str(N)], 6))) <= RATIO_HI
        for N in GRID
    )
    decreasing = (
        ratios_float["10"] > ratios_float["50"] > ratios_float["200"]
    )
    converge = all(ratios_float[str(N)] > TWO_OVER_SQRT_PI for N in GRID)
    g4_pass = in_band and decreasing and converge

    all_pass = g1_pass and g2_pass and g3_pass and g4_pass

    pmf_head = closed_form_pmf(N_HEAD)
    pmf10 = closed_form_pmf(10)

    results = {
        "N_head": N_HEAD,
        "grid": list(GRID),
        "seed": SEED,
        "trials": TRIALS,
        "z_gate": round(Z_GATE, 6),
        "two_over_sqrt_pi": round(TWO_OVER_SQRT_PI, 6),
        # PMF head values at N=50 (P(K=0..4)) and P(K=0) at N=10.
        "pmf50_head": [round(float(pmf_head[k]), 6) for k in range(5)],
        "pmf50_K0": round(float(pmf_head[0]), 6),
        "pmf50_KN": round(float(pmf_head[N_HEAD]), 6),
        "pmf10_K0": round(float(pmf10[0]), 6),
        "pmf_sum50_is_one": bool(sum(pmf_head) == 1),
        "pmf_sum10_is_one": bool(sum(pmf10) == 1),
        # E[K] at head, both float(6dp) and exact.
        "EK50_float": round(float(ek_closed_head), 6),
        "EK50_exact": f"{ek_closed_head.numerator}/{ek_closed_head.denominator}",
        "EK10_float": round(float(closed_form_EK(10)), 6),
        "EK200_float": round(float(closed_form_EK(200)), 6),
        # Monte Carlo.
        "sim_mean": round(sim_mean, 6),
        "sim_var": round(sim_var, 6),
        "se": round(se, 6),
        "z2": round(z2, 6),
        "z3": round(z3, 6),
        # Ratios.
        "ratios": {N: round(ratios_float[N], 6) for N in ratios_float},
        # Gates.
        "g1_detail": g1_detail,
        "G1_exactly_true": bool(g1_pass),
        "G2_signal_3sigma": bool(g2_pass),
        "G3_agreement": bool(g3_pass),
        "G4_robustness": bool(g4_pass),
        "all_pass": bool(all_pass),
    }
    return results


def canonical(d: dict) -> str:
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main() -> int:
    r1 = compute()
    r2 = compute()
    c1 = canonical(r1)
    c2 = canonical(r2)
    assert c1 == c2, "DETERMINISM FAILED: in-process double-run not byte-identical"
    digest = hashlib.sha256(c1.encode()).hexdigest()

    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    print(f"results_sha256={digest}")
    return 0 if r1["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
