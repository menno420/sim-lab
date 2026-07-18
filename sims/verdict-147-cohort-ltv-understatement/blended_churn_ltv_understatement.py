#!/usr/bin/env python3
"""
PROPOSAL 134 — cohort-blended LTV understatement (round-31 VENTURE slot).

Claim (counterintuitive): collapsing a heterogeneous book of customers to a
SINGLE blended churn rate and computing LTV = m / churn does NOT give the
portfolio's true average LTV -- it systematically UNDERSTATES it. Because
LTV = m/c is convex in the churn rate c, Jensen's inequality forces
    E[m/c]  >=  m / E[c],
so the average of per-customer LTVs strictly exceeds the LTV you get from the
blended (average) churn. The gap is driven by churn DISPERSION, not its
level: hold the mean churn fixed and widen the spread and the understatement
grows. A portfolio that looks marginal at the blended number can clear the
LTV/CAC bar once the long-lived low-churn tail is counted.

Pinned world (churn per period c ~ Uniform[LO, HI], margin m = 1):
  WIDE  band  c ~ U[0.05, 0.35]   (retention 65%-95%), mean churn 0.20
  NARROW band c ~ U[0.19, 0.21]   (same mean churn 0.20, tiny spread)
For c ~ U[a,b] the exact figures are closed-form:
  true mean LTV  E[m/c] = m*(ln b - ln a)/(b - a)
  naive LTV      m / E[c] = 2m/(a+b)
  WIDE:   true = ln(7)/0.30 = 6.486367,  naive = 5.0,  gap = 1.486367
  NARROW: true = (ln.21-ln.19)/0.02 = 5.004173, naive = 5.0, gap = 0.004173

Gates (evaluation order G1 -> G2 -> G3; APPROVE iff all hold):
  G1 understatement bias exists -- simulated (true mean LTV - naive) gap is
     POSITIVE at >= SIGMA (WIDE band). one-sided separation gate.
  G2 sim reproduces the EXACT closed form E[m/c] = (ln b - ln a)/(b - a) for
     the WIDE band -- |z| < SIGMA (a no-significant-deviation bracket gate).
  G3 the gap is DISPERSION-driven, not a fixed offset -- with mean churn held
     fixed, the WIDE-band gap exceeds the NARROW-band gap at >= SIGMA, and the
     narrow-band gap is negligible (< 0.05). one-sided separation gate.

Determinism: random.seed(SEED) once; single stream; no wall-clock, no PRNG
re-seed. Stdlib only (random, math, json, hashlib). Digest posture:
WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY -- the results dict carries NO
results_sha256 field; the sha256 is over the COMPACT canonical serialization
(sort_keys, separators=(",",":")), while stdout prints the PRETTY indent=2
form. No on-disk artifact is written.
"""

import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 200000
SIGMA = 3.0

M = 1.0                    # per-period gross margin (normalized; LTV scales linearly in M)
W_LO, W_HI = 0.05, 0.35    # WIDE churn band: retention 65%-95%, mean churn 0.20
N_LO, N_HI = 0.19, 0.21    # NARROW churn band: SAME mean churn 0.20, tiny spread


def mean_std(xs):
    """Return (mean, sample standard deviation) with the (n-1) denominator."""
    n = len(xs)
    mu = sum(xs) / n
    var = sum((x - mu) ** 2 for x in xs) / (n - 1)
    return mu, math.sqrt(var)


def se(sd):
    """Standard error of the mean over TRIALS draws."""
    return sd / math.sqrt(TRIALS)


def exact_true_ltv(a, b):
    """Closed form E[M/c] for c ~ Uniform[a, b]."""
    return M * (math.log(b) - math.log(a)) / (b - a)


def naive_ltv(a, b):
    """LTV from the blended (mean) churn: M / E[c] = 2M/(a+b)."""
    return M / ((a + b) / 2.0)


def run():
    random.seed(SEED)

    naive_w = naive_ltv(W_LO, W_HI)
    wide_ltv = []
    wide_gap = []
    for _ in range(TRIALS):
        c = random.uniform(W_LO, W_HI)
        ltv = M / c
        wide_ltv.append(ltv)
        wide_gap.append(ltv - naive_w)

    naive_n = naive_ltv(N_LO, N_HI)
    narrow_gap = []
    for _ in range(TRIALS):
        c = random.uniform(N_LO, N_HI)
        narrow_gap.append((M / c) - naive_n)

    wide_ltv_mean, wide_ltv_sd = mean_std(wide_ltv)
    wide_gap_mean, wide_gap_sd = mean_std(wide_gap)
    narrow_gap_mean, narrow_gap_sd = mean_std(narrow_gap)

    exact_wide = exact_true_ltv(W_LO, W_HI)
    exact_narrow = exact_true_ltv(N_LO, N_HI)
    gap_exact_wide = exact_wide - naive_w
    gap_exact_narrow = exact_narrow - naive_n
    second_order_wide = 2.0 * (W_HI - W_LO) ** 2 / (3.0 * (W_LO + W_HI) ** 3)

    # G1: understatement bias exists (WIDE gap > 0 at >= SIGMA)
    g1_z = wide_gap_mean / se(wide_gap_sd)
    g1_pass = bool(wide_gap_mean > 0.0 and g1_z >= SIGMA)

    # G2: sim reproduces the EXACT closed form (|z| < SIGMA)
    g2_z = (wide_ltv_mean - exact_wide) / se(wide_ltv_sd)
    g2_pass = bool(abs(g2_z) < SIGMA)

    # G3: dispersion-driven (WIDE gap - NARROW gap > 0 at >= SIGMA)
    diff = wide_gap_mean - narrow_gap_mean
    diff_sd = math.sqrt(wide_gap_sd ** 2 + narrow_gap_sd ** 2)
    g3_z = diff / se(diff_sd)
    g3_pass = bool(diff > 0.0 and g3_z >= SIGMA and narrow_gap_mean < 0.05)

    all_pass = bool(g1_pass and g2_pass and g3_pass)

    results = {
        "proposal": 134,
        "domain": "venture-lab",
        "slot": "round-31 VENTURE",
        "seed": SEED,
        "trials": TRIALS,
        "sigma": SIGMA,
        "params": {
            "margin_m": M,
            "wide_band": [W_LO, W_HI],
            "narrow_band": [N_LO, N_HI],
            "mean_churn": round((W_LO + W_HI) / 2.0, 6),
        },
        "closed_form": {
            "exact_true_ltv_wide": round(exact_wide, 6),
            "naive_ltv_wide": round(naive_w, 6),
            "gap_exact_wide": round(gap_exact_wide, 6),
            "second_order_gap_wide": round(second_order_wide, 6),
            "exact_true_ltv_narrow": round(exact_narrow, 6),
            "naive_ltv_narrow": round(naive_n, 6),
            "gap_exact_narrow": round(gap_exact_narrow, 6),
        },
        "observed": {
            "wide_ltv_mean": round(wide_ltv_mean, 6),
            "wide_gap_mean": round(wide_gap_mean, 6),
            "narrow_gap_mean": round(narrow_gap_mean, 6),
            "gap_diff_wide_minus_narrow": round(diff, 6),
        },
        "gates": {
            "G1_understatement_bias": {
                "z": round(g1_z, 6),
                "threshold_sigma": SIGMA,
                "pass": g1_pass,
            },
            "G2_matches_closed_form": {
                "z": round(g2_z, 6),
                "threshold_sigma": SIGMA,
                "pass": g2_pass,
            },
            "G3_dispersion_driven": {
                "z": round(g3_z, 6),
                "threshold_sigma": SIGMA,
                "narrow_gap_mean": round(narrow_gap_mean, 6),
                "pass": g3_pass,
            },
        },
        "all_pass": all_pass,
    }
    return results


def main():
    results = run()
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    g = results["gates"]
    print(
        "G1 understatement_bias z=%.3f pass=%s | "
        "G2 matches_closed_form z=%.3f pass=%s | "
        "G3 dispersion_driven z=%.3f pass=%s"
        % (
            g["G1_understatement_bias"]["z"], g["G1_understatement_bias"]["pass"],
            g["G2_matches_closed_form"]["z"], g["G2_matches_closed_form"]["pass"],
            g["G3_dispersion_driven"]["z"], g["G3_dispersion_driven"]["pass"],
        )
    )
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
