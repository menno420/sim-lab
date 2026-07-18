#!/usr/bin/env python3
"""
series_reliability_collapse.py — reference verifier for PROPOSAL 112 (round-25,
UNRELATED slot closer). Domain: reliability engineering / systems-reliability
theory — the series-system MTBF collapse. Fleet-external pure-mechanism head.

The "a chain of excellent parts is a fragile system" trap. A SERIES system works
only while ALL of its N components work, so it fails at the FIRST component
failure: its lifetime is the MINIMUM of the N per-component lifetimes. With
independent exponential component lifetimes (rate LAMBDA, per-component
MTBF T = 1/LAMBDA), the minimum of N of them is itself exponential with rate
N*LAMBDA (hazard rates ADD: lambda_sys = sum lambda_i = N*LAMBDA), so the system
MTBF collapses to exactly T/N -- N individually-"excellent" parts give a system
N times more failure-prone than one part, and reliability R_sys(t) = r(t)^N
decays GEOMETRICALLY in N. The counterintuitive core: "99%-reliable" parts feel
like practically-perfect building blocks, yet stringing enough of them in series
makes a coin-flip system, and the SYMMETRIC parallel redundancy (system fails
only when the LAST component fails: lifetime = MAXIMUM of N) buys only
LOGARITHMIC MTBF, T*H_N (the N-th harmonic number) -- 20-fold redundancy
multiplies MTBF by only ~3.6x. A single component in isolation keeps the full
MTBF T, so the collapse is 100% the seriesing of many parts, not a bad part.

min of N iid Exp(LAMBDA) ~ Exp(N*LAMBDA)  =>  E[min] = T/N (the series anchor).
max of N iid Exp(LAMBDA): E[max] = T*H_N, H_N = sum_{k=1..N} 1/k (parallel, descriptive).
Both anchors are closed-form and exact; computed in stdlib from LAMBDA and N.

Gates (all on the /se margin, the P104/P105/P106/P107/P108 convention -- z on the
estimated MEAN via its standard error se = std / sqrt(TRIALS)):
  G1 series-collapse headline: the measured series-system MTBF is at or below
     COLLAPSE_MAX (a small fraction of the per-component MTBF T) by >= 3 sigma AND
     is below the single-component MTBF -- a chain of identical "good" parts has a
     system MTBF far under a single part's, purely from seriesing them.
  G2 single-component control: the measured single-component MTBF matches T within
     3 sigma (|z| < 3) -- each component in isolation keeps the FULL MTBF, so G1's
     collapse is 100% the seriesing of N parts, not a bad/degraded component.
  G3 closed-form anchor MATCH: the measured series MTBF matches the exact series
     anchor T/N_SERIES within 3 sigma (|z| < 3) -- reproduces the min-of-
     exponentials / hazard-addition law (lambda_sys = N*lambda), so the effect IS
     the series-reliability mechanism itself.

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717        # proposal-owned pinned seed; SEEDLESS discipline
LAMBDA = 1.0           # per-component failure rate -> per-component MTBF T = 1/LAMBDA = 1.0
N_SERIES = 20          # components in series (system fails at the FIRST failure)
N_SYSTEMS = 20000      # simulated systems per trial (the batch the per-trial mean is taken over)
TRIALS = 400           # independent experiments (the /se convention averages over these)
SIGMA_GATE = 3.0       # pre-registered gate threshold (sigma)
COLLAPSE_MAX = 0.10    # G1 ceiling on the series-system MTBF (fraction of T; anchor T/N = 0.05)


def harmonic(n):
    """H_n = sum_{k=1..n} 1/k -- the N-th harmonic number (parallel/max MTBF factor)."""
    return sum(1.0 / k for k in range(1, n + 1))


def run_trial(rng):
    """One experiment over N_SYSTEMS series systems. Returns (mtbf_series, mtbf_single,
    mtbf_parallel):
      mtbf_series   = mean over systems of min(N_SERIES component lifetimes) -- the series
                      system fails at the FIRST component failure,
      mtbf_single   = mean over systems of a single component's lifetime (comps[0]) -- the
                      no-seriesing control (one component in isolation),
      mtbf_parallel = mean over systems of max(N_SERIES component lifetimes) -- a fully
                      parallel/redundant system fails at the LAST failure (descriptive).
    Each system draws N_SERIES iid Exp(LAMBDA) component lifetimes from one stream.
    """
    sum_series = sum_single = sum_parallel = 0.0
    for _ in range(N_SYSTEMS):
        comps = [rng.expovariate(LAMBDA) for _ in range(N_SERIES)]
        sum_series += min(comps)
        sum_single += comps[0]
        sum_parallel += max(comps)
    return (sum_series / N_SYSTEMS,
            sum_single / N_SYSTEMS,
            sum_parallel / N_SYSTEMS)


def mean_se(xs):
    """Sample mean and standard error of the mean (se = std / sqrt(n))."""
    k = len(xs)
    m = sum(xs) / k
    var = sum((x - m) ** 2 for x in xs) / k
    se = math.sqrt(var / k)
    return m, se


def main():
    rng = random.Random(SEED)

    T = 1.0 / LAMBDA                          # per-component MTBF
    anchor_series = T / N_SERIES              # E[min of N Exp] = T/N (series anchor)
    anchor_parallel = T * harmonic(N_SERIES)  # E[max of N Exp] = T*H_N (parallel, descriptive)
    r_at_T = math.exp(-float(N_SERIES))       # R_sys(T) = e^{-N} (descriptive geometric decay)

    series, singles, parallels = [], [], []
    for _ in range(TRIALS):
        s, o, p = run_trial(rng)
        series.append(s)
        singles.append(o)
        parallels.append(p)

    mtbf_series, se_series = mean_se(series)
    mtbf_single, se_single = mean_se(singles)
    mtbf_parallel, se_parallel = mean_se(parallels)

    # G1 series-collapse headline: series MTBF at/below COLLAPSE_MAX by >= 3 sigma.
    z_g1 = (COLLAPSE_MAX - mtbf_series) / se_series if se_series > 0 else float("inf")
    g1 = (z_g1 >= SIGMA_GATE) and (mtbf_series < mtbf_single)

    # G2 single-component control: single-component MTBF consistent with T.
    z_g2 = abs(mtbf_single - T) / se_single if se_single > 0 else float("inf")
    g2 = z_g2 < SIGMA_GATE

    # G3 closed-form anchor MATCH: series MTBF == T/N within 3 sigma.
    z_g3 = abs(mtbf_series - anchor_series) / se_series if se_series > 0 else float("inf")
    g3 = z_g3 < SIGMA_GATE

    all_pass = g1 and g2 and g3

    results = {
        "params": {"SEED": SEED, "LAMBDA": LAMBDA, "N_SERIES": N_SERIES,
                   "N_SYSTEMS": N_SYSTEMS, "TRIALS": TRIALS, "SIGMA_GATE": SIGMA_GATE,
                   "COLLAPSE_MAX": COLLAPSE_MAX},
        "anchor": {"T_component_mtbf": round(T, 6),
                   "anchor_series_mtbf_T_over_N": round(anchor_series, 6),
                   "anchor_parallel_mtbf_T_HN": round(anchor_parallel, 6),
                   "R_sys_at_T_e_neg_N": r_at_T},
        "sim": {
            "mtbf_series": round(mtbf_series, 6), "se_series": round(se_series, 6),
            "mtbf_single": round(mtbf_single, 6), "se_single": round(se_single, 6),
            "mtbf_parallel": round(mtbf_parallel, 6), "se_parallel": round(se_parallel, 6),
        },
        "gates": {
            "G1_series_collapse": {"z": round(z_g1, 4), "pass": g1},
            "G2_single_component_control": {"z": round(z_g2, 4), "pass": g2},
            "G3_anchor_match": {"z": round(z_g3, 4), "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("series_reliability_collapse_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
