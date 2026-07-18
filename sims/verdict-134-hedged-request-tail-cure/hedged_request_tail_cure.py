#!/usr/bin/env python3
"""
hedged_request_tail_cure.py -- reference verifier for PROPOSAL 121 (round-28,
FLEET slot opener). Domain: distributed-systems tail-latency theory -- the "tail
at scale" hedged-request cure (Dean & Barroso, CACM 2013). Fleet-domain pure-
mechanism head.

The "to kill the tail you must duplicate everything" trap. A request served by
ONE replica has a heavy-tailed latency: its 99th percentile is dominated by the
occasional straggler. The folk fix is to send the request to TWO replicas and
take the first to answer -- which halves the tail but DOUBLES the load (+100%).
The folk belief also holds that any delay before the second request "leaves
latency on the table."

Both halves are wrong. The HEDGED request defers the second copy to a small
delay d: send the primary at t=0; only if it has not answered by d do you send a
secondary to an independent replica; the response is

    latency = min(primary, d + secondary).

Set d to the 95th percentile of the service-time distribution. Then the hedge
FIRES only on the ~5% of requests whose primary already exceeds p95 -- the
extra load is P(S > p95) ~= 0.05, not 100%. Yet because a straggler primary is
almost always rescued by a fast independent secondary, the 99th-percentile
latency COLLAPSES: it recovers the large majority of full duplication's tail
reduction at a twentieth of the cost. The last sliver of tail benefit that full
duplication buys BEYOND the p95 hedge costs ~20x the load -- the knee. So the
tail cure is almost free, and fleet dispatch should tie-hedge after ~p95 rather
than duplicate.

Service-time model (a two-component straggler mixture, the canonical heavy tail):
  with probability (1 - P_STRAGGLER): S ~ Exp(mean = MEAN_FAST)   (the common case)
  with probability P_STRAGGLER:       S ~ Exp(mean = MEAN_SLOW)   (a straggler)
Every request/replica draws an INDEPENDENT S (independent replicas), so a slow
primary and its secondary are independent draws -- the reason hedging works.

Arms (per request, on independent draws S1 for the primary, S2 for the secondary):
  baseline  : latency = S1                          load per request = 1   (no extra)
  hedge@p95 : latency = min(S1, d + S2) if S1 > d   load = 1 + [S1 > d]     (fires ~5%)
              else S1                                (d = empirical p95 of the S1 batch)
  full-dup  : latency = min(S1, S2)                 load = 2   (+100%, always duplicated)

Gates (all on the /se margin, the P104..P120 convention -- z on an estimated
statistic via its standard error se = std / sqrt(TRIALS)):
  G1 hedge collapses the tail (headline): mean(p99_base - p99_hedge) > 0 by
     >= 3 sigma -- deferring the hedge to the p95 delay strictly and largely
     lowers the 99th-percentile latency.
  G2 the knee (near-full benefit at tiny load): (a) the capture ratio
     mean[(p99_base - p99_hedge) / (p99_base - p99_dup)] >= CAPTURE_MIN by
     >= 3 sigma -- the p95 hedge recovers >= 80% of full duplication's tail
     reduction; AND (b) the hedge's extra load is small: mean hedge-fire fraction
     <= LOAD_MAX (fires on ~p95 = 5% of requests), while full duplication costs
     +100% load.
  G3 almost free (efficiency): mean[ reduction_hedge / load_hedge
     - reduction_dup / load_dup ] > 0 by >= 3 sigma -- the tail-reduction PER
     UNIT of extra load from the p95 hedge strictly exceeds full duplication's.
     The tail cure is nearly free exactly where duplication is expensive.

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717        # proposal-owned pinned seed; SEEDLESS discipline
MEAN_FAST = 10.0       # mean service time of the common (fast) component
MEAN_SLOW = 200.0      # mean service time of the straggler component (heavy tail)
P_STRAGGLER = 0.05     # fraction of draws that are stragglers
N_REQUESTS = 20000     # independent requests per replication (the per-trial batch)
TRIALS = 200           # independent replications (the /se convention averages over these)
HEDGE_PCTL = 0.95      # hedge delay d = the 95th percentile of the service-time batch
DUP_LOAD = 2.0         # full duplication issues 2 requests each (+100% load)
BASE_LOAD = 1.0        # one request per call
CAPTURE_MIN = 0.80     # G2(a) threshold: p95 hedge recovers >= 80% of full-dup's tail cut
LOAD_MAX = 0.08        # G2(b) threshold: hedge extra load stays small (~p95 = 5%)
SIGMA_GATE = 3.0       # pre-registered gate threshold (sigma)


def service_time(rng):
    """One independent service-time draw from the two-component straggler mixture."""
    if rng.random() < P_STRAGGLER:
        return rng.expovariate(1.0 / MEAN_SLOW)
    return rng.expovariate(1.0 / MEAN_FAST)


def mixture_cdf(x):
    """Exact CDF of the straggler mixture -- closed-form anchor for the percentiles."""
    if x <= 0:
        return 0.0
    return ((1.0 - P_STRAGGLER) * (1.0 - math.exp(-x / MEAN_FAST))
            + P_STRAGGLER * (1.0 - math.exp(-x / MEAN_SLOW)))


def mixture_quantile(q):
    """Exact q-quantile of the mixture by bisection on the closed-form CDF."""
    lo, hi = 0.0, 1.0
    while mixture_cdf(hi) < q:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mixture_cdf(mid) < q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def percentile(sorted_xs, q):
    """The q-quantile of an already-sorted list (nearest-rank, lower index)."""
    n = len(sorted_xs)
    idx = int(q * n)
    if idx >= n:
        idx = n - 1
    return sorted_xs[idx]


def run_trial(rng):
    """One replication over N_REQUESTS independent requests. Returns the batch
    p99 of each arm (baseline / hedge@p95 / full-dup) and the hedge-fire fraction."""
    s1 = [service_time(rng) for _ in range(N_REQUESTS)]   # primary draws
    s2 = [service_time(rng) for _ in range(N_REQUESTS)]   # independent secondary draws
    # hedge delay d = the empirical 95th percentile of THIS batch's primary times
    d = percentile(sorted(s1), HEDGE_PCTL)

    base_lat = []
    hedge_lat = []
    dup_lat = []
    fires = 0
    for a, b in zip(s1, s2):
        base_lat.append(a)
        if a > d:                       # primary is running long -> fire the hedge
            hedge_lat.append(min(a, d + b))
            fires += 1
        else:
            hedge_lat.append(a)
        dup_lat.append(min(a, b))       # full duplication: always take the faster of two

    p99_base = percentile(sorted(base_lat), 0.99)
    p99_hedge = percentile(sorted(hedge_lat), 0.99)
    p99_dup = percentile(sorted(dup_lat), 0.99)
    hedge_fire_frac = fires / N_REQUESTS
    return p99_base, p99_hedge, p99_dup, hedge_fire_frac


def mean_se(xs):
    """Sample mean and standard error of the mean (se = std / sqrt(n))."""
    k = len(xs)
    m = sum(xs) / k
    var = sum((x - m) ** 2 for x in xs) / k
    se = math.sqrt(var / k)
    return m, se


def main():
    rng = random.Random(SEED)

    p99_bases, p99_hedges, p99_dups, fires = [], [], [], []
    captures, eff_diffs = [], []
    load_hedge_per_trial = []
    for _ in range(TRIALS):
        pb, ph, pd, ff = run_trial(rng)
        p99_bases.append(pb)
        p99_hedges.append(ph)
        p99_dups.append(pd)
        fires.append(ff)
        red_hedge = pb - ph                       # tail reduction from the p95 hedge
        red_dup = pb - pd                         # tail reduction from full duplication
        captures.append(red_hedge / red_dup if red_dup > 0 else 0.0)
        load_hedge = ff                           # extra load = hedge-fire fraction
        load_dup = DUP_LOAD - BASE_LOAD           # extra load of full-dup = +1.0 (+100%)
        load_hedge_per_trial.append(load_hedge)
        eff_hedge = red_hedge / load_hedge if load_hedge > 0 else 0.0
        eff_dup = red_dup / load_dup if load_dup > 0 else 0.0
        eff_diffs.append(eff_hedge - eff_dup)     # efficiency edge of the hedge

    mean_p99_base, se_p99_base = mean_se(p99_bases)
    mean_p99_hedge, se_p99_hedge = mean_se(p99_hedges)
    mean_p99_dup, se_p99_dup = mean_se(p99_dups)
    mean_fire, se_fire = mean_se(fires)
    mean_capture, se_capture = mean_se(captures)
    mean_eff_diff, se_eff_diff = mean_se(eff_diffs)

    # paired tail-collapse: mean of (p99_base - p99_hedge) per trial, with its se
    tail_cut = [b - h for b, h in zip(p99_bases, p99_hedges)]
    mean_tail_cut, se_tail_cut = mean_se(tail_cut)

    # closed-form anchors (exact mixture quantiles)
    anch_p95 = mixture_quantile(0.95)
    anch_p99 = mixture_quantile(0.99)

    # G1 hedge collapses the tail: mean(p99_base - p99_hedge) > 0 by >= 3 sigma.
    z_g1 = mean_tail_cut / se_tail_cut if se_tail_cut > 0 else float("inf")
    g1 = z_g1 >= SIGMA_GATE

    # G2 the knee: (a) capture ratio >= CAPTURE_MIN by >= 3 sigma; (b) hedge load small.
    z_g2_capture = (mean_capture - CAPTURE_MIN) / se_capture if se_capture > 0 else float("inf")
    g2a = z_g2_capture >= SIGMA_GATE
    g2b = mean_fire <= LOAD_MAX
    g2 = g2a and g2b

    # G3 almost free: efficiency edge (reduction/load) of the p95 hedge > 0 by >= 3 sigma.
    z_g3_eff = mean_eff_diff / se_eff_diff if se_eff_diff > 0 else float("inf")
    g3 = z_g3_eff >= SIGMA_GATE

    all_pass = g1 and g2 and g3

    # descriptive efficiency ratio (hedge tail-cut per unit load vs full-dup's)
    eff_hedge_mean = (mean_p99_base - mean_p99_hedge) / mean_fire if mean_fire > 0 else 0.0
    eff_dup_mean = (mean_p99_base - mean_p99_dup) / (DUP_LOAD - BASE_LOAD)

    results = {
        "params": {"SEED": SEED, "MEAN_FAST": MEAN_FAST, "MEAN_SLOW": MEAN_SLOW,
                   "P_STRAGGLER": P_STRAGGLER, "N_REQUESTS": N_REQUESTS, "TRIALS": TRIALS,
                   "HEDGE_PCTL": HEDGE_PCTL, "CAPTURE_MIN": CAPTURE_MIN,
                   "LOAD_MAX": LOAD_MAX, "SIGMA_GATE": SIGMA_GATE},
        "anchor": {"mixture_p95": round(anch_p95, 6),
                   "mixture_p99": round(anch_p99, 6),
                   "dup_extra_load": round(DUP_LOAD - BASE_LOAD, 6)},
        "sim": {
            "mean_p99_base": round(mean_p99_base, 6), "se_p99_base": round(se_p99_base, 6),
            "mean_p99_hedge": round(mean_p99_hedge, 6), "se_p99_hedge": round(se_p99_hedge, 6),
            "mean_p99_dup": round(mean_p99_dup, 6), "se_p99_dup": round(se_p99_dup, 6),
            "mean_tail_cut_hedge": round(mean_tail_cut, 6), "se_tail_cut_hedge": round(se_tail_cut, 6),
            "mean_hedge_fire_frac": round(mean_fire, 6), "se_hedge_fire_frac": round(se_fire, 6),
            "mean_capture_ratio": round(mean_capture, 6), "se_capture_ratio": round(se_capture, 6),
            "mean_efficiency_edge": round(mean_eff_diff, 6), "se_efficiency_edge": round(se_eff_diff, 6),
            "eff_hedge_per_unit_load": round(eff_hedge_mean, 6),
            "eff_dup_per_unit_load": round(eff_dup_mean, 6),
            "efficiency_ratio_hedge_over_dup": round(eff_hedge_mean / eff_dup_mean, 6) if eff_dup_mean > 0 else 0.0,
        },
        "gates": {
            "G1_hedge_collapses_tail": {"z": round(z_g1, 4), "pass": g1},
            "G2_knee_capture_and_load": {
                "z_capture": round(z_g2_capture, 4), "mean_capture": round(mean_capture, 6),
                "mean_hedge_load": round(mean_fire, 6), "load_max": LOAD_MAX, "pass": g2},
            "G3_almost_free_efficiency": {"z": round(z_g3_eff, 4), "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("hedged_request_tail_cure_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
