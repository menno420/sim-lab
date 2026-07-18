#!/usr/bin/env python3
"""
german_tank_mvue.py -- reference verifier for PROPOSAL 120 (round-27,
UNRELATED slot closer). Domain: statistical estimation theory -- the German-tank
problem (minimum-variance unbiased estimation of the maximum of a discrete
uniform population). Fleet-external pure-mechanism head.

The "the population is the biggest one I've seen" trap. You observe k distinct
serial numbers drawn WITHOUT replacement from an unknown fleet numbered 1..N and
must estimate N. Intuition says the best guess for N is the largest serial you
have seen -- the sample maximum m. That is systematically too LOW: you almost
never sample the very top of the range, so

    E[m] = k*(N+1)/(k+1) < N   (bias N - E[m] = (N-k)/(k+1)).

The frequentist minimum-variance UNBIASED estimator EXTRAPOLATES ABOVE the
largest observed serial:

    N_hat = m*(1 + 1/k) - 1 = m + (m - k)/k

    = "sample maximum + the average gap between the ordered samples"

which is UNBIASED (E[N_hat] = N exactly) with the EXACT variance

    Var(N_hat) = (N - k)*(N + 1) / (k*(k + 2)).

Because m >= k always (the max of k distinct positive serials), N_hat >= m
always: the estimate ALWAYS lies at or above the largest serial observed. A
competing UNBIASED estimator, twice-the-sample-mean-minus-one,

    N_tilde = 2*x_bar - 1,   Var(N_tilde) = (N + 1)*(N - k)/(3*k),

is also unbiased but strictly LESS efficient -- its variance is (k+2)/3 times
the MVUE's, so the MVUE is the better estimator (Rao-Blackwell / Lehmann-Scheffe:
the MVUE conditions on the sufficient statistic m).

Gates (all on the /se margin, the P104..P116 convention -- z on an estimated
statistic via its standard error se = std / sqrt(TRIALS)):
  G1 MVUE-unbiased (headline+control): the measured mean of N_hat is within
     3 sigma of the true N (|z| < 3) -- the estimator that extrapolates ABOVE
     the largest observed serial is spot-on for N.
  G2 max-biased-low + MVUE-above-max: (a) the mean sample maximum m is strictly
     BELOW N by >= 3 sigma (the naive "population = largest seen" underestimates),
     AND (b) the mean N_hat exceeds the mean sample maximum by >= 3 sigma -- the
     MVUE lands ABOVE the largest observed serial, the counterintuitive core.
  G3 closed-form-anchor + efficiency: (a) the empirical Var(N_hat) reproduces
     the exact closed form (N-k)(N+1)/(k(k+2)) within 3 sigma (|z| < 3), AND
     (b) the MVUE is strictly MORE efficient than the unbiased 2*x_bar-1
     estimator: Var(N_tilde) - Var(N_hat) >= 0 by >= 3 sigma.

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717        # proposal-owned pinned seed; SEEDLESS discipline
N_TRUE = 1000          # true (unknown-to-the-estimator) population size / max serial
K = 5                  # sample size: distinct serials drawn WITHOUT replacement
SAMPLES = 4000         # independent size-K samples per replication (the per-trial batch)
TRIALS = 200           # independent replications (the /se convention averages over these)
SIGMA_GATE = 3.0       # pre-registered gate threshold (sigma)


def closed_forms(n, k):
    """Exact closed-form anchors for the discrete-uniform German-tank problem."""
    e_max = k * (n + 1) / (k + 1)                       # E[sample maximum m]
    bias_max = n - e_max                                # = (n-k)/(k+1), how far m sits below N
    var_nhat = (n - k) * (n + 1) / (k * (k + 2))        # Var(N_hat), MVUE
    var_alt = (n + 1) * (n - k) / (3 * k)               # Var(2*x_bar - 1), the unbiased alternative
    return {"e_max": e_max, "bias_max": bias_max,
            "var_nhat": var_nhat, "var_alt": var_alt}


def run_trial(rng, n, k):
    """One replication over SAMPLES independent size-k samples. Returns the batch
    mean of N_hat, the batch mean of the sample maximum m, and the batch sample
    variances of N_hat and of the alternative unbiased estimator 2*x_bar - 1."""
    population = range(1, n + 1)
    nhats = []
    maxes = []
    alts = []
    inv_k = 1.0 / k
    for _ in range(SAMPLES):
        s = rng.sample(population, k)          # k distinct serials, without replacement
        m = max(s)
        nhat = m * (1.0 + inv_k) - 1.0         # MVUE: m + (m-k)/k
        xbar = sum(s) / k
        alt = 2.0 * xbar - 1.0                 # unbiased alternative
        nhats.append(nhat)
        maxes.append(m)
        alts.append(alt)
    mean_nhat = sum(nhats) / SAMPLES
    mean_max = sum(maxes) / SAMPLES
    # sample variance (population form, /SAMPLES) of each estimator over the batch
    var_nhat = sum((x - mean_nhat) ** 2 for x in nhats) / SAMPLES
    mean_alt = sum(alts) / SAMPLES
    var_alt = sum((x - mean_alt) ** 2 for x in alts) / SAMPLES
    return mean_nhat, mean_max, var_nhat, var_alt


def mean_se(xs):
    """Sample mean and standard error of the mean (se = std / sqrt(n))."""
    k = len(xs)
    m = sum(xs) / k
    var = sum((x - m) ** 2 for x in xs) / k
    se = math.sqrt(var / k)
    return m, se


def main():
    rng = random.Random(SEED)
    anch = closed_forms(N_TRUE, K)

    mean_nhats, mean_maxes, var_nhats, var_alts = [], [], [], []
    for _ in range(TRIALS):
        mnh, mmx, vnh, valt = run_trial(rng, N_TRUE, K)
        mean_nhats.append(mnh)
        mean_maxes.append(mmx)
        var_nhats.append(vnh)
        var_alts.append(valt)

    mean_nhat, se_nhat = mean_se(mean_nhats)
    mean_max, se_max = mean_se(mean_maxes)
    mean_var_nhat, se_var_nhat = mean_se(var_nhats)
    mean_var_alt, se_var_alt = mean_se(var_alts)

    # G1 MVUE unbiased: |mean(N_hat) - N| within 3 sigma.
    z_g1 = abs(mean_nhat - N_TRUE) / se_nhat if se_nhat > 0 else float("inf")
    g1 = z_g1 < SIGMA_GATE

    # G2 max biased low (a) + MVUE above the max (b).
    z_g2_bias = (N_TRUE - mean_max) / se_max if se_max > 0 else float("inf")
    gap = mean_nhat - mean_max
    se_gap = math.sqrt(se_nhat ** 2 + se_max ** 2)
    z_g2_above = gap / se_gap if se_gap > 0 else float("inf")
    g2 = (z_g2_bias >= SIGMA_GATE) and (z_g2_above >= SIGMA_GATE)

    # G3 closed-form variance anchor MATCH (a) + efficiency vs 2*x_bar-1 (b).
    z_g3_varmatch = abs(mean_var_nhat - anch["var_nhat"]) / se_var_nhat if se_var_nhat > 0 else float("inf")
    var_diff = mean_var_alt - mean_var_nhat
    se_var_diff = math.sqrt(se_var_alt ** 2 + se_var_nhat ** 2)
    z_g3_eff = var_diff / se_var_diff if se_var_diff > 0 else float("inf")
    g3 = (z_g3_varmatch < SIGMA_GATE) and (z_g3_eff >= SIGMA_GATE)

    all_pass = g1 and g2 and g3

    results = {
        "params": {"SEED": SEED, "N_TRUE": N_TRUE, "K": K,
                   "SAMPLES": SAMPLES, "TRIALS": TRIALS, "SIGMA_GATE": SIGMA_GATE},
        "anchor": {"e_max": round(anch["e_max"], 6),
                   "bias_max": round(anch["bias_max"], 6),
                   "var_nhat_closed_form": round(anch["var_nhat"], 6),
                   "var_alt_closed_form": round(anch["var_alt"], 6),
                   "efficiency_ratio_alt_over_nhat": round(anch["var_alt"] / anch["var_nhat"], 6)},
        "sim": {
            "mean_nhat": round(mean_nhat, 6), "se_nhat": round(se_nhat, 6),
            "mean_sample_max": round(mean_max, 6), "se_sample_max": round(se_max, 6),
            "nhat_above_max_gap": round(gap, 6), "se_gap": round(se_gap, 6),
            "mean_var_nhat": round(mean_var_nhat, 6), "se_var_nhat": round(se_var_nhat, 6),
            "mean_var_alt": round(mean_var_alt, 6), "se_var_alt": round(se_var_alt, 6),
            "var_diff_alt_minus_nhat": round(var_diff, 6), "se_var_diff": round(se_var_diff, 6),
        },
        "gates": {
            "G1_mvue_unbiased": {"z": round(z_g1, 4), "pass": g1},
            "G2_max_biased_low_mvue_above": {
                "z_bias": round(z_g2_bias, 4), "z_above": round(z_g2_above, 4), "pass": g2},
            "G3_anchor_match_efficiency": {
                "z_var_match": round(z_g3_varmatch, 4), "z_efficiency": round(z_g3_eff, 4),
                "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("german_tank_mvue_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
