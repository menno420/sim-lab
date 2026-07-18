#!/usr/bin/env python3
"""PROPOSAL 142 — venture slot (round-33) — sim-lab verifier.

Claim: the sales "pipeline coverage ratio" (expected pipeline value / quota)
is NOT a sufficient statistic for quota attainment. At a FIXED 3x coverage
ratio and a FIXED per-deal win probability, the probability of MISSING quota
rises sharply with deal-size concentration. Two pipelines with identical
coverage and identical win-rate -- one granular (many small deals), one
concentrated (a few whales) -- have identical expected bookings yet the
concentrated pipeline misses quota far more often, because bookings variance
is exactly proportional to the Herfindahl-Hirschman concentration index of
deal values: Var(B) = p*(1-p) * V^2 * HHI.

stdlib only. Deterministic: one random.seed(SEED), single stream, batch means.
Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (compact-canonical
sha256 is the digest; stdout dumps the pretty indent=2 form).
"""

import hashlib
import json
import math
import random

SEED = 20260717            # fleet-pinned
P_WIN = 0.40               # per-deal win probability (iid Bernoulli), held equal
QUOTA = 1_000_000.0        # period quota (dollars)
COVERAGE = 3.0             # pipeline coverage ratio E[B]/QUOTA, held equal
SIGMA = 3.0                # gate threshold (sigma)

# 3x-coverage rule implies total pipeline value V: E[B] = P_WIN*V = COVERAGE*QUOTA
PIPELINE_VALUE = COVERAGE * QUOTA / P_WIN     # = 7_500_000

N_G = 75                   # granular pipeline: N_G equal deals summing to V
CONC_WEIGHTS = [0.40, 0.20, 0.1333333333, 0.0933333333,
                0.0666666667, 0.0533333333, 0.0333333333, 0.02]  # "few whales"

N_BATCH = 40
BATCH_TRIALS = 2000        # 80_000 trials per pipeline


def build_deals():
    granular = [PIPELINE_VALUE / N_G] * N_G
    conc = [w * PIPELINE_VALUE for w in CONC_WEIGHTS]
    scale = PIPELINE_VALUE / sum(conc)          # guard float drift -> exact V
    conc = [v * scale for v in conc]
    return granular, conc


def hhi(deals):
    v = sum(deals)
    return sum((d / v) ** 2 for d in deals)


def theory(deals):
    v = sum(deals)
    sum_sq = sum(d * d for d in deals)
    return {
        "value": v,
        "sum_sq": sum_sq,
        "hhi": hhi(deals),
        "mean": P_WIN * v,
        "var": P_WIN * (1.0 - P_WIN) * sum_sq,
    }


def simulate(deals):
    """Per-batch (mean_bookings, miss_rate, var_bookings) on the shared stream."""
    book_means, miss_means, book_vars = [], [], []
    for _ in range(N_BATCH):
        s = 0.0
        ss = 0.0
        miss = 0
        for _ in range(BATCH_TRIALS):
            b = 0.0
            for v in deals:
                if random.random() < P_WIN:
                    b += v
            s += b
            ss += b * b
            if b < QUOTA:
                miss += 1
        n = BATCH_TRIALS
        mean = s / n
        var = (ss - n * mean * mean) / (n - 1)
        book_means.append(mean)
        book_vars.append(var)
        miss_means.append(miss / n)
    return book_means, miss_means, book_vars


def mean_sd(xs):
    n = len(xs)
    m = sum(xs) / n
    if n < 2:
        return m, 0.0
    v = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(v)


def batch_stat(xs):
    m, sd = mean_sd(xs)
    return m, sd / math.sqrt(len(xs))


def run():
    random.seed(SEED)
    granular, conc = build_deals()
    th_g = theory(granular)
    th_c = theory(conc)

    # single shared stream: granular first, then concentrated
    g_book_means, g_miss_means, g_book_vars = simulate(granular)
    c_book_means, c_miss_means, c_book_vars = simulate(conc)

    # G1 anchor: empirical Bernoulli variance matches closed form for BOTH tiers
    var_emp_g, var_sd_g = mean_sd(g_book_vars)
    var_emp_c, var_sd_c = mean_sd(c_book_vars)
    se_var_g = var_sd_g / math.sqrt(N_BATCH)
    se_var_c = var_sd_c / math.sqrt(N_BATCH)
    z_var_g = (var_emp_g - th_g["var"]) / se_var_g if se_var_g > 0 else 0.0
    z_var_c = (var_emp_c - th_c["var"]) / se_var_c if se_var_c > 0 else 0.0
    z1 = max(abs(z_var_g), abs(z_var_c))
    g1_pass = z1 <= SIGMA

    # G2 coverage control: both empirical coverages equal COVERAGE (confound held)
    g_book_mean, g_book_se = batch_stat(g_book_means)
    c_book_mean, c_book_se = batch_stat(c_book_means)
    cov_g = g_book_mean / QUOTA
    cov_c = c_book_mean / QUOTA
    z_cov_g = (cov_g - COVERAGE) / (g_book_se / QUOTA) if g_book_se > 0 else 0.0
    z_cov_c = (cov_c - COVERAGE) / (c_book_se / QUOTA) if c_book_se > 0 else 0.0
    z2 = max(abs(z_cov_g), abs(z_cov_c))
    g2_pass = z2 <= SIGMA

    # G3 head: concentrated misses quota more than granular (one-sided)
    g_miss, g_miss_se = batch_stat(g_miss_means)
    c_miss, c_miss_se = batch_stat(c_miss_means)
    diff = c_miss - g_miss
    se_diff = math.sqrt(g_miss_se ** 2 + c_miss_se ** 2)
    z3 = diff / se_diff if se_diff > 0 else 0.0
    g3_pass = z3 >= SIGMA

    var_ratio_theory = th_c["var"] / th_g["var"]
    var_ratio_emp = var_emp_c / var_emp_g

    results = {
        "proposal": 142,
        "domain": "venture",
        "slot": "round-33 venture",
        "seed": SEED,
        "claim": "coverage ratio is not sufficient; quota-miss risk scales with deal HHI",
        "params": {
            "p_win": P_WIN,
            "quota": QUOTA,
            "coverage_target": COVERAGE,
            "pipeline_value": PIPELINE_VALUE,
            "n_granular_deals": N_G,
            "n_conc_deals": len(conc),
            "n_batch": N_BATCH,
            "batch_trials": BATCH_TRIALS,
            "sigma": SIGMA,
        },
        "closed_form": {
            "granular_hhi": round(th_g["hhi"], 12),
            "conc_hhi": round(th_c["hhi"], 12),
            "hhi_ratio": round(th_c["hhi"] / th_g["hhi"], 6),
            "granular_var": round(th_g["var"], 6),
            "conc_var": round(th_c["var"], 6),
            "var_ratio_theory": round(var_ratio_theory, 6),
            "granular_mean": round(th_g["mean"], 6),
            "conc_mean": round(th_c["mean"], 6),
        },
        "observed": {
            "granular_book_mean": round(g_book_mean, 6),
            "conc_book_mean": round(c_book_mean, 6),
            "coverage_granular": round(cov_g, 6),
            "coverage_conc": round(cov_c, 6),
            "granular_var_emp": round(var_emp_g, 6),
            "conc_var_emp": round(var_emp_c, 6),
            "var_ratio_emp": round(var_ratio_emp, 6),
            "miss_granular": round(g_miss, 6),
            "miss_conc": round(c_miss, 6),
            "miss_diff": round(diff, 6),
        },
        "gates": {
            "G1_anchor_variance_law": {"z": round(z1, 6), "threshold_sigma": SIGMA,
                                       "two_sided": True, "pass": bool(g1_pass)},
            "G2_coverage_control": {"z": round(z2, 6), "threshold_sigma": SIGMA,
                                    "two_sided": True, "pass": bool(g2_pass)},
            "G3_head_miss_gap": {"z": round(z3, 6), "threshold_sigma": SIGMA,
                                 "one_sided": True, "pass": bool(g3_pass)},
        },
        "all_pass": bool(g1_pass and g2_pass and g3_pass),
    }
    return results


def main():
    results = run()
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    g = results["gates"]
    print("GATES: G1 z=%.3f pass=%s | G2 z=%.3f pass=%s | G3 z=%.3f pass=%s" % (
        g["G1_anchor_variance_law"]["z"], g["G1_anchor_variance_law"]["pass"],
        g["G2_coverage_control"]["z"], g["G2_coverage_control"]["pass"],
        g["G3_head_miss_gap"]["z"], g["G3_head_miss_gap"]["pass"]))
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
