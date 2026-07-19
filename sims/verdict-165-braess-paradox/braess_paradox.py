#!/usr/bin/env python3
"""Braess's paradox: adding a zero-cost shortcut to a congested network
RAISES the selfish-equilibrium travel time for everyone.

Head claim (G1): in the canonical 4-node Braess network under stochastic
demand, the user (Wardrop) equilibrium travel time WITH a zero-cost A->B
shortcut is strictly greater than WITHOUT it -- adding capacity makes the
network slower.

Mechanism. Two symmetric routes S->A->T and S->B->T each combine one
congestion-priced edge (cost = flow / CAP) with one fixed 45-minute edge.
Without the shortcut the equilibrium splits demand 50/50:
    t_without(D) = FIXED + D / (2 * CAP).
Add a zero-cost link A->B and a third route S->A->B->T appears that uses
BOTH congestion edges and NEITHER fixed edge. Selfish drivers pile onto it
until it is no better than the alternatives, driving both congestion edges
to carry the full flow. The exact augmented-network Wardrop equilibrium is
piecewise:
    t_with(D) = 2 * D / CAP                for D <= FIXED * CAP
    t_with(D) = 2 * FIXED                  for FIXED * CAP < D <= 2 * FIXED * CAP
The paradox gap t_with - t_without is positive for 30*CAP < D < 90*CAP and
peaks at D = FIXED*CAP. Below 30*CAP the shortcut actually helps -- a caveat
disclosed honestly and probed by the shifted-distribution robustness gate.

Grounded in Braess (1968) and documented road removals that IMPROVED flow:
Seoul's Cheonggyecheon expressway (2003), Stuttgart, New York 42nd Street.

Gates (evaluation order; APPROVE iff ALL hold):
  G1  mean(t_with - t_without) > 0                    at >= 3 sigma
  G2  mean(t_with / t_without - 1) > 0.10             at >= 3 sigma   (degradation is large, not marginal)
  G3  under a SHIFTED demand distribution, mean gap>0 at >= 3 sigma   (robustness inside the window)

Posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. SEED pinned; two
in-process runs asserted identical; results dict plus its sha256 printed.
Stdlib only.
"""

import hashlib
import json
import math
import random

SEED = 20260717

CAP = 100.0          # congestion slope denominator (cost = flow / CAP)
FIXED = 45.0         # fixed-edge travel time (minutes)
N_TRIALS = 20000

# base demand distribution
D_MEAN = 4000.0
D_SD = 250.0

# shifted (robustness) demand distribution -- lower mean, wider spread,
# still inside the (30*CAP, 90*CAP) = (3000, 9000) validity window
D_MEAN_SHIFT = 3500.0
D_SD_SHIFT = 300.0

# gate thresholds
G2_MIN_REL = 0.10
SIGMA = 3.0


def t_without(D):
    """Symmetric 50/50 user equilibrium on the base (no-shortcut) network."""
    return FIXED + D / (2.0 * CAP)


def t_with(D):
    """Exact Wardrop equilibrium travel time on the augmented network."""
    if D <= FIXED * CAP:                 # everyone on the shortcut route
        return 2.0 * D / CAP
    if D <= 2.0 * FIXED * CAP:           # congestion edges saturate at FIXED*CAP
        return 2.0 * FIXED
    return t_without(D)                  # shortcut abandoned (out of tested range)


def zstat(vals, h0):
    """One-sample z of the mean of vals against null h0."""
    n = len(vals)
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / (n - 1)
    sd = math.sqrt(var)
    if sd == 0.0:
        return mean, sd, float("inf")
    return mean, sd, (mean - h0) / (sd / math.sqrt(n))


def run_distribution(rng, d_mean, d_sd):
    gaps = []
    rels = []
    for _ in range(N_TRIALS):
        D = rng.gauss(d_mean, d_sd)
        if D < 1.0:
            D = 1.0
        tw = t_without(D)
        ts = t_with(D)
        gaps.append(ts - tw)
        rels.append(ts / tw - 1.0)
    gm, gsd, gz = zstat(gaps, 0.0)
    rm, rsd, rz = zstat(rels, G2_MIN_REL)
    frac_worse = sum(1 for g in gaps if g > 0.0) / len(gaps)
    return {
        "gap_mean": gm, "gap_sd": gsd, "gap_z": gz,
        "rel_mean": rm, "rel_sd": rsd, "rel_z": rz,
        "frac_worse": frac_worse,
    }


def rnd(x):
    return round(x, 6)


def run():
    rng = random.Random(SEED)
    base = run_distribution(rng, D_MEAN, D_SD)
    shift = run_distribution(rng, D_MEAN_SHIFT, D_SD_SHIFT)

    g1 = base["gap_z"] >= SIGMA and base["gap_mean"] > 0.0
    g2 = base["rel_z"] >= SIGMA and base["rel_mean"] > G2_MIN_REL
    g3 = shift["gap_z"] >= SIGMA and shift["gap_mean"] > 0.0
    all_pass = g1 and g2 and g3
    order = [("G1", g1), ("G2", g2), ("G3", g3)]
    first_fail = next((name for name, ok in order if not ok), None)

    results = {
        "seed": SEED,
        "n_trials": N_TRIALS,
        "cap": CAP, "fixed": FIXED,
        "d_mean": D_MEAN, "d_sd": D_SD,
        "d_mean_shift": D_MEAN_SHIFT, "d_sd_shift": D_SD_SHIFT,
        "valid_window": [rnd(30 * CAP), rnd(90 * CAP)],
        "base_gap_mean": rnd(base["gap_mean"]),
        "base_gap_z": rnd(base["gap_z"]),
        "base_rel_mean": rnd(base["rel_mean"]),
        "base_rel_z": rnd(base["rel_z"]),
        "base_frac_worse": rnd(base["frac_worse"]),
        "shift_gap_mean": rnd(shift["gap_mean"]),
        "shift_gap_z": rnd(shift["gap_z"]),
        "shift_frac_worse": rnd(shift["frac_worse"]),
        "g1_sign": g1, "g2_magnitude": g2, "g3_robust": g3,
        "all_pass": all_pass,
        "first_failing_gate": first_fail,
    }
    return results


def main():
    results = run()
    again = run()
    assert results == again, "non-deterministic: in-process double run diverged"

    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    print("Braess paradox verifier -- canonical 4-node network, stochastic demand")
    print(f"  base  : gap_mean={results['base_gap_mean']:+.6f}  z={results['base_gap_z']:+.6f}  frac_worse={results['base_frac_worse']:.6f}")
    print(f"  G2 rel: rel_mean={results['base_rel_mean']:+.6f}  z={results['base_rel_z']:+.6f}  (null=0.10)")
    print(f"  shift : gap_mean={results['shift_gap_mean']:+.6f}  z={results['shift_gap_z']:+.6f}  frac_worse={results['shift_frac_worse']:.6f}")
    print(f"  gates : G1={results['g1_sign']}  G2={results['g2_magnitude']}  G3={results['g3_robust']}  all_pass={results['all_pass']}")
    print()
    print(json.dumps(results, indent=2, sort_keys=True))
    print(f"Results-JSON sha256: {digest}")
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
