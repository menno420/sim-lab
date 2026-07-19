#!/usr/bin/env python3
"""PROPOSAL 162 — the option-pool shuffle: a pre-money option pool dilutes founders alone.

PHENOMENON
    In a priced venture round (investment I at pre-money valuation P, so post-money
    P+I), the term sheet also carves out an employee option pool of size q (a fraction
    of the fully-diluted post-money cap table). Standard VC practice creates that pool
    PRE-money. Under that convention the incoming investor's post-money ownership is
    exactly t := I/(P+I) and is INVARIANT to the pool size q: every share of the pool
    comes out of the founders' pre-money stake. Founders bear 100% of the pool's
    dilution. Relative to a "fair" pro-rata pool (created post-round, diluting existing
    holders and the new investor alike to t*(1-q)), the pre-money pool transfers exactly
    q*t = q*I/(P+I) of the company from founders to the investor.

FOLK BELIEF (inverted here)
    "An option pool dilutes everyone in proportion to their holdings, so a bigger pool
    just means a bit less for each shareholder -- the investor and the founders share the
    hit." False under the pre-money convention: the investor's stake does not move with
    q at all; the founders eat the whole pool, plus a q*t transfer to the investor
    versus a pro-rata pool.

PRE-REGISTERED GATES (order G1 -> G2 -> G3; APPROVE iff ALL hold, z_gate=3.0)
    G1  investor-fraction invariance to pool size (rejects the pro-rata null):
        over N paired draws at fixed (P, I), the change in the investor's realized
        integer cap-table fraction between a low pool q_lo and a high pool q_hi is ~0
        under the shuffle, while the pro-rata null predicts -t*(q_hi-q_lo); the
        divergence (pro-rata change minus shuffle change) is decisively non-zero at z>=3.
    G2  founders->investor wealth transfer = q*t:
        at matched (P, I, q) the investor-fraction gap between the shuffle and a pro-rata
        pool equals the closed form q*t within a tight relerr ceiling, and is robustly
        positive at z>=3.
    G3  robustness under a shifted distribution (mega-rounds, pools up to 30%):
        G1 re-run under a shifted regime holds the invariance and keeps the divergence
        decisively above the null at z>=3.

DIGEST POSTURE
    WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. The ordered results dict does NOT contain
    its own hash; floats are rounded to 6 dp; the compact canonical JSON (sort_keys,
    tight separators) is hashed with sha256; the pretty indent=2 dump and the sha256 are
    printed to stdout. An in-process double run is asserted byte-identical.
"""

import hashlib
import json
import math
import random
import statistics

SEED = 20260717
N = 4000              # paired draws per regime
F0 = 10_000_000       # founders' pre-round fully-diluted shares (fixed)
Z_GATE = 3.0


def shuffle_investor_fraction(t, q, f0):
    """Pre-money pool (the shuffle): founders keep f0 shares; the investor targets
    post-money fraction t; the pool is q of post-money, carved from the founders'
    pre-money stake, so the investor's fraction is t, independent of q. Integer share
    counts introduce quantization noise."""
    denom = 1.0 - t - q
    s = round(f0 / denom)
    inv = round(t * s)
    return inv / s


def prorata_investor_fraction(t, q, f0):
    """Pro-rata pool (the 'fair' null): the pool dilutes existing holders AND the new
    investor proportionally, so the investor lands at t*(1-q)."""
    denom = (1.0 - t) * (1.0 - q)
    s = round(f0 / denom)
    inv = round(t * (1.0 - q) * s)
    return inv / s


def zscore(mean, se):
    if se == 0.0:
        return float("inf")
    return mean / se


def mean_se(xs):
    m = statistics.fmean(xs)
    if len(xs) < 2:
        return m, 0.0
    sd = statistics.pstdev(xs)
    se = sd / math.sqrt(len(xs))
    return m, se


def run_regime(rng, n, t_lo, t_hi, qlo_lo, qlo_hi, qhi_lo, qhi_hi, f0):
    d_shuffle = []
    divergence = []
    transfer = []
    predicted_qt = []
    transfer_relerr = []
    for _ in range(n):
        t = rng.uniform(t_lo, t_hi)
        q_lo = rng.uniform(qlo_lo, qlo_hi)
        q_hi = rng.uniform(qhi_lo, qhi_hi)
        sh_lo = shuffle_investor_fraction(t, q_lo, f0)
        sh_hi = shuffle_investor_fraction(t, q_hi, f0)
        pr_lo = prorata_investor_fraction(t, q_lo, f0)
        pr_hi = prorata_investor_fraction(t, q_hi, f0)
        ds = sh_hi - sh_lo
        dp = pr_hi - pr_lo
        d_shuffle.append(ds)
        divergence.append(dp - ds)
        tr = sh_hi - pr_hi
        transfer.append(tr)
        pred = q_hi * t
        predicted_qt.append(pred)
        transfer_relerr.append(abs(tr - pred) / pred)
    return {
        "d_shuffle": d_shuffle,
        "divergence": divergence,
        "transfer": transfer,
        "predicted_qt": predicted_qt,
        "transfer_relerr": transfer_relerr,
    }


def r6(x):
    return round(float(x), 6)


def run():
    rng = random.Random(SEED)

    base = run_regime(
        rng, N,
        t_lo=0.15, t_hi=0.30,
        qlo_lo=0.05, qlo_hi=0.10,
        qhi_lo=0.15, qhi_hi=0.25,
        f0=F0,
    )
    div_mean, div_se = mean_se(base["divergence"])
    ds_absmean = statistics.fmean([abs(x) for x in base["d_shuffle"]])
    g1_z = abs(zscore(div_mean, div_se))
    g1_pass = g1_z >= Z_GATE and abs(div_mean) > 0.0

    tr_mean, tr_se = mean_se(base["transfer"])
    relerr_mean = statistics.fmean(base["transfer_relerr"])
    g2_z = abs(zscore(tr_mean, tr_se))
    g2_pass = g2_z >= Z_GATE and relerr_mean < 1e-3

    shifted = run_regime(
        rng, N,
        t_lo=0.10, t_hi=0.20,
        qlo_lo=0.08, qlo_hi=0.12,
        qhi_lo=0.22, qhi_hi=0.30,
        f0=100_000_000,
    )
    sdiv_mean, sdiv_se = mean_se(shifted["divergence"])
    sds_absmean = statistics.fmean([abs(x) for x in shifted["d_shuffle"]])
    g3_z = abs(zscore(sdiv_mean, sdiv_se))
    g3_pass = g3_z >= Z_GATE and abs(sdiv_mean) > 0.0

    all_pass = g1_pass and g2_pass and g3_pass
    first_failing = None
    for name, ok in (("G1", g1_pass), ("G2", g2_pass), ("G3", g3_pass)):
        if not ok:
            first_failing = name
            break

    results = {
        "mechanism": "option-pool-shuffle-investor-invariance",
        "seed": SEED,
        "n_draws": N,
        "founder_shares": F0,
        "z_gate": Z_GATE,
        "G1_investor_invariance": {
            "shuffle_change_absmean": r6(ds_absmean),
            "prorata_minus_shuffle_change_mean": r6(div_mean),
            "se": r6(div_se),
            "z": r6(g1_z),
            "pass": g1_pass,
        },
        "G2_wealth_transfer": {
            "transfer_mean": r6(tr_mean),
            "predicted_qt_mean": r6(statistics.fmean(base["predicted_qt"])),
            "relerr_mean": r6(relerr_mean),
            "z": r6(g2_z),
            "pass": g2_pass,
        },
        "G3_robust_shift": {
            "shuffle_change_absmean": r6(sds_absmean),
            "prorata_minus_shuffle_change_mean": r6(sdiv_mean),
            "se": r6(sdiv_se),
            "z": r6(g3_z),
            "pass": g3_pass,
        },
        "all_pass": all_pass,
        "first_failing_gate": first_failing,
    }
    return results


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def digest(results):
    return hashlib.sha256(canonical(results).encode("utf-8")).hexdigest()


def main():
    a = run()
    b = run()
    assert canonical(a) == canonical(b), "in-process double run diverged"
    print(json.dumps(a, indent=2, sort_keys=True))
    print("sha256:", digest(a))
    return 0 if a["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
