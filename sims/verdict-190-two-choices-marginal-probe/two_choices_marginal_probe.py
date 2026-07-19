#!/usr/bin/env python3
"""
PROPOSAL 177 — the second probe does all the work: in randomized load
balancing, one extra choice (d=1 -> d=2) collapses the maximum bin load from
Theta(log n / log log n) to Theta(log log n) -- and that single second probe
removes several times more max load than every further probe (3rd, 4th, ...)
COMBINED. The whole dispatch win is the one extra probe; JSQ(3+) adds only a
small aggregate constant.

Anchor: the "power of two choices" / balanced-allocations result
(Azar-Broder-Karlin-Upfal; Mitzenmacher-Richa-Sitaraman survey).

Folk belief: more probes = proportionally better balance.
Counterintuitive truth: probe value is front-loaded onto the SECOND probe. The
individual per-probe gaps past d=2 are small and integer-granular (non-monotone
at finite n), but their whole SUM is dwarfed by the single 1->2 jump, because d
enters only inside a log-log term.

Pre-registered gates (>=3 sigma, each tests the head):
  G1  d=2 strictly beats d=1: z(m1 - m2) >= 3, gap > 0.
  G2  second-probe dominance: second_gain = m1 - m2; further_gain = m2 - m_dmax
      (all probes past the 2nd, combined). dom = second_gain - further_gain;
      require dom > 0, z(dom) >= 3, AND ratio second_gain/further_gain >= 3.
  G3  robustness under shifted load (m = n/2 bins, load factor 2): dom, ratio
      recomputed in that regime; require dom > 0, z(dom) >= 3, ratio >= 3.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. The compact-canonical
results dict's own sha256 IS the digest; the stdout dump is pretty indent=2.
Deterministic: explicit per-(regime,d,trial) seeds; in-process double-run and
cross-invocation identical.
"""

import hashlib
import json
import math
import random

SEED = 20260717
N = 8000              # balls (dispatched requests)
R = 250               # independent trials per (regime, d)
DS = (1, 2, 3, 4)     # number of probes / choices
SIGMA_GATE = 3.0
RATIO_MIN = 3.0
TRIAL_STRIDE = 7919        # prime stride per trial
D_STRIDE = 1_000_003       # prime stride per d
REGIME_STRIDE = 50_000_017 # prime stride per regime


def _max_load(n_balls, m_bins, d, seed):
    rng = random.Random(seed)
    bins = [0] * m_bins
    for _ in range(n_balls):
        best = rng.randrange(m_bins)
        for _ in range(d - 1):
            cand = rng.randrange(m_bins)
            if bins[cand] < bins[best]:
                best = cand
        bins[best] += 1
    return max(bins)


def _mean_se(xs):
    n = len(xs)
    mean = sum(xs) / n
    if n < 2:
        return mean, 0.0
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return mean, math.sqrt(var / n)


def _regime(n_balls, m_bins, regime_seed):
    means = {}
    ses = {}
    for d in DS:
        loads = []
        for t in range(R):
            s = regime_seed + d * D_STRIDE + t * TRIAL_STRIDE
            loads.append(_max_load(n_balls, m_bins, d, s))
        m, se = _mean_se(loads)
        means[d] = m
        ses[d] = se
    return means, ses


def _gap(means, ses, a, b):
    gap = means[a] - means[b]
    se = math.sqrt(ses[a] ** 2 + ses[b] ** 2)
    return gap, se


def _z(val, se):
    return val / se if se > 0 else float("inf")


def r6(x):
    return round(float(x), 6)


def run():
    dmax = DS[-1]
    mA, sA = _regime(N, N, SEED + 0 * REGIME_STRIDE)
    mB, sB = _regime(N, N // 2, SEED + 1 * REGIME_STRIDE)

    g12, s12 = _gap(mA, sA, 1, 2)
    g23, s23 = _gap(mA, sA, 2, 3)
    g34, s34 = _gap(mA, sA, 3, 4)

    second_gain = mA[1] - mA[2]
    further_gain = mA[2] - mA[dmax]
    dom = second_gain - further_gain
    dom_se = math.sqrt(sA[1] ** 2 + 4 * sA[2] ** 2 + sA[dmax] ** 2)
    ratio_g2 = second_gain / further_gain if further_gain > 0 else float("inf")

    second_gainB = mB[1] - mB[2]
    further_gainB = mB[2] - mB[dmax]
    domB = second_gainB - further_gainB
    domB_se = math.sqrt(sB[1] ** 2 + 4 * sB[2] ** 2 + sB[dmax] ** 2)
    ratio_g3 = second_gainB / further_gainB if further_gainB > 0 else float("inf")

    z_g1 = _z(g12, s12)
    z_g2 = _z(dom, dom_se)
    z_g3 = _z(domB, domB_se)

    g1_pass = (g12 > 0) and (z_g1 >= SIGMA_GATE)
    g2_pass = (dom > 0) and (z_g2 >= SIGMA_GATE) and (ratio_g2 >= RATIO_MIN)
    g3_pass = (domB > 0) and (z_g3 >= SIGMA_GATE) and (ratio_g3 >= RATIO_MIN)
    all_pass = g1_pass and g2_pass and g3_pass

    results = {
        "params": {
            "seed": SEED,
            "n_balls": N,
            "trials": R,
            "ds": list(DS),
            "sigma_gate": SIGMA_GATE,
            "ratio_min": RATIO_MIN,
        },
        "regime_a_load1": {
            "maxload_mean": {str(d): r6(mA[d]) for d in DS},
            "maxload_se": {str(d): r6(sA[d]) for d in DS},
            "gap_1_2": r6(g12),
            "gap_2_3": r6(g23),
            "gap_3_4": r6(g34),
            "second_probe_gain": r6(second_gain),
            "all_further_gain_2_to_dmax": r6(further_gain),
        },
        "regime_b_load2": {
            "bins": N // 2,
            "maxload_mean": {str(d): r6(mB[d]) for d in DS},
            "maxload_se": {str(d): r6(sB[d]) for d in DS},
            "second_probe_gain": r6(second_gainB),
            "all_further_gain_2_to_dmax": r6(further_gainB),
        },
        "gates": {
            "g1_second_probe_jump": {
                "z": r6(z_g1), "gap_1_2": r6(g12), "pass": g1_pass,
            },
            "g2_second_probe_dominance": {
                "second_probe_gain": r6(second_gain),
                "all_further_gain": r6(further_gain),
                "dom_stat": r6(dom), "z": r6(z_g2),
                "ratio_second_over_further": r6(ratio_g2), "pass": g2_pass,
            },
            "g3_robust_shifted_load": {
                "second_probe_gain": r6(second_gainB),
                "all_further_gain": r6(further_gainB),
                "dom_stat": r6(domB), "z": r6(z_g3),
                "ratio_second_over_further": r6(ratio_g3), "pass": g3_pass,
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
    print("Results-JSON sha256: " + digest)
    print("G1 second-probe jump:      " +
          ("PASS" if results["gates"]["g1_second_probe_jump"]["pass"] else "FAIL"))
    print("G2 second-probe dominance: " +
          ("PASS" if results["gates"]["g2_second_probe_dominance"]["pass"] else "FAIL"))
    print("G3 robust (shifted load):  " +
          ("PASS" if results["gates"]["g3_robust_shifted_load"]["pass"] else "FAIL"))
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
