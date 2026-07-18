#!/usr/bin/env python3
"""
PROPOSAL 138 — usage-based billing variance shock (round-32 VENTURE slot).

Claim (counterintuitive): under usage-based (consumption) pricing a firm's
monthly revenue R = sum_i U_i is the sum of many independent accounts, so the
folk model says "with N accounts the law of large numbers smooths revenue and
the coefficient of variation falls like CV_account / sqrt(N)". FALSE when
account SIZES are heterogeneous. Because independent-but-unequal accounts add
in variance weighted by the square of their size,

    CV(R) = CV_account * sqrt(HHI),   HHI = sum_i w_i^2,   w_i = m_i / sum m_i,

so the effective number of accounts diversifying the book is N_eff = 1 / HHI,
NOT N. With Zipf-law account sizes (m_i = 1/i, i = 1..N) a book of N = 400
accounts has N_eff ~ 25 -- revenue is ~4x MORE volatile than the naive
CV_account/sqrt(N) predicts, a shock the law of large numbers hides because
size concentration (Cauchy-Schwarz forces HHI >= 1/N), not customer count,
sets the variance floor. The trap: a CFO who "has thousands of usage-based
accounts" models revenue as smooth and is blind-sided by single-account swings.

Distinct from a correlation-driven variance floor (independent accounts here;
the driver is size HETEROGENEITY / Herfindahl concentration, not covariance)
and from a Jensen convexity bias in a POINT estimate (this is a second-moment
RISK result: the point mean is fine, the dispersion is not).

Pinned world (per-account monthly usage U_i ~ Gamma(shape k, scale m_i / k),
so E[U_i] = m_i and CV(U_i) = CV_account = 1/sqrt(k), independent across i):
  CONCENTRATED book: sizes m_i = 1 / i for i = 1..N  (Zipf / power law, alpha=1)
  UNIFORM      book: every m_i = mean(concentrated sizes) -> HHI = 1/N exactly,
                     SAME N, SAME total mean revenue, SAME per-account CV.
Closed forms (computed exactly from the deterministic size vector, not hard-coded):
  HHI            = sum m_i^2 / (sum m_i)^2
  N_eff          = 1 / HHI
  CV(R)_exact    = CV_account * sqrt(HHI)
  CV_naive (LLN) = CV_account / sqrt(N)   [ = CV_account*sqrt(HHI) iff HHI=1/N ]

SE via BATCH MEANS (method of independent replications) -- the sampling SE of a
ratio estimator CV_hat = s / xbar has no clean normal-theory form when R is
size-dominated and mildly skewed, so we split the T months into B independent
batches, take one CV estimate per batch, and use the between-batch spread:
mean_CV +/- sd(batch CVs)/sqrt(B). Batches are independent (months are drawn
from one stream in order), so this SE is distribution-free and valid.

Gates (evaluation order G1 -> G2 -> G3; APPROVE iff all hold):
  G1 diversification shortfall EXISTS -- the CONCENTRATED-book revenue CV
     strictly exceeds the naive CV_account/sqrt(N) at >= SIGMA. one-sided /se.
  G2 sim reproduces the EXACT closed form CV_account*sqrt(HHI) for the
     concentrated book -- |z| < SIGMA (a no-significant-deviation bracket).
  G3 the shock is CONCENTRATION-driven, not N or per-account CV -- with SAME N,
     SAME total mean revenue, SAME per-account CV, the CONCENTRATED CV exceeds
     the UNIFORM CV at >= SIGMA, and the uniform CV matches the naive 1/sqrt(N)
     (uniform |CV_unif - CV_naive| negligible < 0.01). one-sided /se.

Determinism: random.seed(SEED) once; single stream; concentrated then uniform,
batch by batch, month by month, account by account, in fixed order; no
wall-clock, no re-seed. Stdlib only (random, math, json, hashlib). Digest
posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY -- the results dict carries
NO results_sha256 field; the sha256 is over the COMPACT canonical serialization
(sort_keys, separators=(",",":")), while stdout prints the PRETTY indent=2
form (the twist -- pretty stdout != hashed preimage). No on-disk artifact.
"""

import hashlib
import json
import math
import random

SEED = 20260717
N = 400                 # accounts in the book
K_SHAPE = 4.0           # Gamma shape -> CV_account = 1/sqrt(K) = 0.5
CV_ACCOUNT = 1.0 / math.sqrt(K_SHAPE)
N_BATCH = 60            # independent batches (replications) for the SE
BATCH_MONTHS = 250      # months per batch
SIGMA = 3.0


def mean_std(xs):
    """Return (mean, sample standard deviation) with the (n-1) denominator."""
    n = len(xs)
    mu = sum(xs) / n
    var = sum((x - mu) ** 2 for x in xs) / (n - 1)
    return mu, math.sqrt(var)


def batch_cv(sizes):
    """One CV estimate of monthly revenue over BATCH_MONTHS independent months.

    Each month draws N independent per-account usages U_i ~ Gamma(K_SHAPE,
    m_i / K_SHAPE) and sums them; CV = sample_sd / sample_mean across the months.
    """
    revenues = []
    for _ in range(BATCH_MONTHS):
        total = 0.0
        for m in sizes:
            total += random.gammavariate(K_SHAPE, m / K_SHAPE)
        revenues.append(total)
    mu, sd = mean_std(revenues)
    return sd / mu


def run():
    random.seed(SEED)

    # Deterministic size vectors -----------------------------------------------
    conc_sizes = [1.0 / i for i in range(1, N + 1)]        # Zipf alpha = 1
    mean_size = sum(conc_sizes) / N
    unif_sizes = [mean_size] * N                            # same total, flat

    # Exact closed forms from the size vectors (not hard-coded) ----------------
    s1_c = sum(conc_sizes)
    s2_c = sum(m * m for m in conc_sizes)
    hhi_conc = s2_c / (s1_c * s1_c)
    n_eff_conc = 1.0 / hhi_conc
    cv_exact_conc = CV_ACCOUNT * math.sqrt(hhi_conc)

    s1_u = sum(unif_sizes)
    s2_u = sum(m * m for m in unif_sizes)
    hhi_unif = s2_u / (s1_u * s1_u)
    cv_exact_unif = CV_ACCOUNT * math.sqrt(hhi_unif)

    cv_naive = CV_ACCOUNT / math.sqrt(N)                    # LLN folk model

    # Batch-means estimates (concentrated then uniform, fixed order) -----------
    conc_batch_cvs = []
    unif_batch_cvs = []
    for _ in range(N_BATCH):
        conc_batch_cvs.append(batch_cv(conc_sizes))
        unif_batch_cvs.append(batch_cv(unif_sizes))

    conc_cv_mean, conc_cv_sd = mean_std(conc_batch_cvs)
    unif_cv_mean, unif_cv_sd = mean_std(unif_batch_cvs)
    conc_se = conc_cv_sd / math.sqrt(N_BATCH)
    unif_se = unif_cv_sd / math.sqrt(N_BATCH)

    # G1: diversification shortfall exists (conc CV > naive at >= SIGMA) --------
    g1_diff = conc_cv_mean - cv_naive
    g1_z = g1_diff / conc_se
    g1_pass = bool(g1_diff > 0.0 and g1_z >= SIGMA)

    # G2: sim reproduces the exact closed form (|z| < SIGMA bracket) ------------
    g2_z = (conc_cv_mean - cv_exact_conc) / conc_se
    g2_pass = bool(abs(g2_z) < SIGMA)

    # G3: concentration-driven (conc CV > unif CV at >= SIGMA; unif ~ naive) ----
    g3_diff = conc_cv_mean - unif_cv_mean
    g3_se = math.sqrt(conc_se ** 2 + unif_se ** 2)
    g3_z = g3_diff / g3_se
    unif_naive_gap = abs(unif_cv_mean - cv_naive)
    g3_pass = bool(g3_diff > 0.0 and g3_z >= SIGMA and unif_naive_gap < 0.01)

    all_pass = bool(g1_pass and g2_pass and g3_pass)

    results = {
        "proposal": 138,
        "domain": "venture-lab",
        "slot": "round-32 VENTURE",
        "seed": SEED,
        "n_accounts": N,
        "sigma": SIGMA,
        "params": {
            "gamma_shape_k": K_SHAPE,
            "cv_account": round(CV_ACCOUNT, 6),
            "n_batches": N_BATCH,
            "batch_months": BATCH_MONTHS,
            "size_law": "zipf_alpha_1_reciprocal_rank",
        },
        "closed_form": {
            "hhi_concentrated": round(hhi_conc, 6),
            "n_eff_concentrated": round(n_eff_conc, 6),
            "cv_exact_concentrated": round(cv_exact_conc, 6),
            "hhi_uniform": round(hhi_unif, 6),
            "cv_exact_uniform": round(cv_exact_unif, 6),
            "cv_naive_lln": round(cv_naive, 6),
            "volatility_multiplier": round(cv_exact_conc / cv_naive, 6),
        },
        "observed": {
            "conc_cv_mean": round(conc_cv_mean, 6),
            "unif_cv_mean": round(unif_cv_mean, 6),
            "conc_minus_naive": round(g1_diff, 6),
            "conc_minus_unif": round(g3_diff, 6),
            "unif_naive_gap": round(unif_naive_gap, 6),
        },
        "gates": {
            "G1_shortfall_exists": {
                "z": round(g1_z, 6),
                "threshold_sigma": SIGMA,
                "pass": g1_pass,
            },
            "G2_matches_closed_form": {
                "z": round(g2_z, 6),
                "threshold_sigma": SIGMA,
                "pass": g2_pass,
            },
            "G3_concentration_driven": {
                "z": round(g3_z, 6),
                "threshold_sigma": SIGMA,
                "unif_naive_gap": round(unif_naive_gap, 6),
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
        "G1 shortfall_exists z=%.3f pass=%s | "
        "G2 matches_closed_form z=%.3f pass=%s | "
        "G3 concentration_driven z=%.3f pass=%s"
        % (
            g["G1_shortfall_exists"]["z"], g["G1_shortfall_exists"]["pass"],
            g["G2_matches_closed_form"]["z"], g["G2_matches_closed_form"]["pass"],
            g["G3_concentration_driven"]["z"], g["G3_concentration_driven"]["pass"],
        )
    )
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
