#!/usr/bin/env python3
"""Term-sheet winner's curse: the investor who wins a competitive VC round
systematically overpays, and the overpayment (a) is negative in expectation,
(b) deepens with the number of competing term sheets, and (c) survives a
heavier-tailed, higher-dispersion estimation-error distribution.

Stdlib only. Deterministic: SEED pinned; in-process double-run byte-identical.
Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (P127+ twist) — the
compact-canonical results dict's own sha256 IS the digest; it is not a field.
"""
import json
import hashlib
import math
import random

SEED = 20260717
V0 = 1.0            # normalised intrinsic value of the company
SIGMA = 0.25        # std-dev of each investor's unbiased valuation error
SIGMA_HEAVY = 0.35  # inflated dispersion for the shifted robustness world
TRIALS = 200_000
N_LOW = 2
N_HIGH = 8
Z_GATE = 3.0


def gaussian_noise(rng):
    return rng.normalvariate(0.0, SIGMA)


def laplace_noise(rng):
    # Heavier-tailed, higher-dispersion shifted world (mean 0, var SIGMA_HEAVY**2).
    # Laplace scale b: var = 2*b**2  ->  b = SIGMA_HEAVY / sqrt(2).
    b = SIGMA_HEAVY / math.sqrt(2.0)
    u = rng.random() - 0.5
    return -b * math.copysign(1.0, u) * math.log(1.0 - 2.0 * abs(u))


def winner_excess(rng, n, noise_fn):
    """One competitive round: n naive bidders each bid their own estimate
    V0 + eps; the winner is the highest bid. Returns the winner's realised
    excess value V0 - winning_bid = -max(eps)."""
    biggest = None
    for _ in range(n):
        eps = noise_fn(rng)
        if biggest is None or eps > biggest:
            biggest = eps
    return -biggest


def mean_se(vals):
    n = len(vals)
    m = math.fsum(vals) / n
    var = math.fsum((v - m) ** 2 for v in vals) / (n - 1)
    se = math.sqrt(var / n)
    return m, se


def z_of(m, se):
    return abs(m) / se if se > 0 else float("inf")


def compute():
    rng = random.Random(SEED)

    # G1: winner overpays, magnitude deepens with N (gaussian errors)
    ex_low = [winner_excess(rng, N_LOW, gaussian_noise) for _ in range(TRIALS)]
    ex_high = [winner_excess(rng, N_HIGH, gaussian_noise) for _ in range(TRIALS)]
    m_low, se_low = mean_se(ex_low)
    m_high, se_high = mean_se(ex_high)
    z_high_neg = z_of(m_high, se_high)
    diff = m_high - m_low
    se_diff = math.sqrt(se_low ** 2 + se_high ** 2)
    z_deepens = abs(diff) / se_diff
    g1 = (m_high < 0.0) and (z_high_neg >= Z_GATE) and (m_high < m_low) and (z_deepens >= Z_GATE)

    # G2: conditional-on-winning reversal (N_HIGH, gaussian)
    single = [-gaussian_noise(rng) for _ in range(TRIALS)]
    m_single, se_single = mean_se(single)
    gap = m_high - m_single
    se_gap = math.sqrt(se_high ** 2 + se_single ** 2)
    z_reversal = abs(gap) / se_gap
    g2 = (m_single > m_high) and (gap < 0.0) and (z_reversal >= Z_GATE)

    # G3: robustness under heavier-tailed, higher-dispersion Laplace errors
    hx_low = [winner_excess(rng, N_LOW, laplace_noise) for _ in range(TRIALS)]
    hx_high = [winner_excess(rng, N_HIGH, laplace_noise) for _ in range(TRIALS)]
    hm_low, hse_low = mean_se(hx_low)
    hm_high, hse_high = mean_se(hx_high)
    hz_high_neg = z_of(hm_high, hse_high)
    hdiff = hm_high - hm_low
    hse_diff = math.sqrt(hse_low ** 2 + hse_high ** 2)
    hz_deepens = abs(hdiff) / hse_diff
    g3 = (hm_high < 0.0) and (hz_high_neg >= Z_GATE) and (hm_high < hm_low) and (hz_deepens >= Z_GATE)

    all_pass = g1 and g2 and g3

    return {
        "head": "term-sheet-winners-curse",
        "seed": SEED,
        "constants": {
            "V0": V0, "sigma": SIGMA, "sigma_heavy": SIGMA_HEAVY,
            "trials": TRIALS, "n_low": N_LOW, "n_high": N_HIGH, "z_gate": Z_GATE,
        },
        "gaussian": {
            "mean_excess_n_low": round(m_low, 6),
            "mean_excess_n_high": round(m_high, 6),
            "z_winner_overpays": round(z_high_neg, 6),
            "z_deepens_with_n": round(z_deepens, 6),
        },
        "conditional_reversal": {
            "mean_excess_unconditional": round(m_single, 6),
            "mean_excess_winner": round(m_high, 6),
            "z_reversal": round(z_reversal, 6),
        },
        "robustness_laplace": {
            "mean_excess_n_low": round(hm_low, 6),
            "mean_excess_n_high": round(hm_high, 6),
            "z_winner_overpays": round(hz_high_neg, 6),
            "z_deepens_with_n": round(hz_deepens, 6),
        },
        "gates": {
            "G1_winner_overpays_deepens": g1,
            "G2_conditional_reversal": g2,
            "G3_robust_heavy_tail": g3,
        },
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
    print("Results-JSON sha256 %s" % digest)
    return 0 if r1["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
