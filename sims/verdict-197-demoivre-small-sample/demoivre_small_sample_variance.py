#!/usr/bin/env python3
"""PROPOSAL 184 - de Moivre's small-sample variance artifact ("the most
dangerous equation", Wainer 2007): when units share ONE true rate p but
differ in sample size n, the OBSERVED rate has SD = sqrt(p(1-p)/n), so
small-n units land at BOTH extremes of any ranking by observed rate. The
top and bottom of the leaderboard are a sample-size illusion, not a
quality signal. Firsthand stdlib-only verifier. Deterministic under SEED.
No disk writes. Prints the whole results dict (pretty) then its
canonical-JSON sha256. WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY."""

import sys
import math
import json
import hashlib
import random

SEED = 20260717
Z_GATE = 3.0


def r6(x):
    return round(float(x), 6)


def mean_std(vals):
    n = len(vals)
    m = sum(vals) / n
    if n < 2:
        return m, 0.0
    v = sum((x - m) ** 2 for x in vals) / (n - 1)
    return m, math.sqrt(v)


def z_pos(vals, null):
    """One-sided z that mean(vals) exceeds `null`, using the SEM."""
    m, s = mean_std(vals)
    n = len(vals)
    if s == 0.0:
        return 0.0
    return (m - null) / (s / math.sqrt(n))


def pearson(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = syy = sxy = 0.0
    for x, y in zip(xs, ys):
        dx = x - mx
        dy = y - my
        sxx += dx * dx
        syy += dy * dy
        sxy += dx * dy
    den = math.sqrt(sxx * syy)
    if den == 0.0:
        return 0.0
    return sxy / den


def log_uniform_int(rng, lo, hi):
    u = rng.uniform(math.log(lo), math.log(hi))
    return max(lo, min(hi, int(round(math.exp(u)))))


def obs_rate(rng, n, p):
    hits = 0
    for _ in range(n):
        if rng.random() < p:
            hits += 1
    return hits / n


def scaling_corr(rng, m, lo, hi, p):
    """Pearson corr across m units between |r - p| and 1/sqrt(n)."""
    devs = []
    inv_root = []
    for _ in range(m):
        n = log_uniform_int(rng, lo, hi)
        r = obs_rate(rng, n, p)
        devs.append(abs(r - p))
        inv_root.append(1.0 / math.sqrt(n))
    return pearson(devs, inv_root)


def extreme_small_delta(rng, m, lo, hi, p, ext):
    """pop_mean_n - mean_n(top+bottom ext by observed rate). Positive when
    the ranking extremes are dominated by small-n units."""
    units = []
    for _ in range(m):
        n = log_uniform_int(rng, lo, hi)
        r = obs_rate(rng, n, p)
        units.append((r, n))
    pop_mean_n = sum(n for _, n in units) / m
    k = max(1, int(round(m * ext)))
    srt = sorted(units, key=lambda u: u[0])
    extremes = srt[:k] + srt[-k:]
    ext_mean_n = sum(n for _, n in extremes) / len(extremes)
    return pop_mean_n - ext_mean_n


def run():
    rng = random.Random(SEED)
    TRIALS = 100
    M = 800
    LO = 10
    HI = 800
    P = 0.5
    P_SHIFT = 0.1
    EXT = 0.10
    LO2 = 25
    HI2 = 250

    # G1 - de Moivre scaling law: |r-p| tracks 1/sqrt(n), corr > 0.
    g1 = [scaling_corr(rng, M, LO, HI, P) for _ in range(TRIALS)]
    g1_mean, g1_std = mean_std(g1)
    g1_z = z_pos(g1, 0.0)
    g1_pass = (g1_mean > 0.0) and (g1_z >= Z_GATE)

    # G2 - leaderboard extremes are small-n dominated: delta > 0.
    g2 = [extreme_small_delta(rng, M, LO, HI, P, EXT) for _ in range(TRIALS)]
    g2_mean, g2_std = mean_std(g2)
    g2_z = z_pos(g2, 0.0)
    g2_pass = (g2_mean > 0.0) and (g2_z >= Z_GATE)

    # G3 - robust under a shifted rate (p=0.1) and a shifted size range.
    g3a = [scaling_corr(rng, M, LO, HI, P_SHIFT) for _ in range(TRIALS)]
    g3a_mean, _ = mean_std(g3a)
    g3a_z = z_pos(g3a, 0.0)
    g3b = [extreme_small_delta(rng, M, LO2, HI2, P, EXT) for _ in range(TRIALS)]
    g3b_mean, _ = mean_std(g3b)
    g3b_z = z_pos(g3b, 0.0)
    g3_pass = (g3a_mean > 0.0 and g3a_z >= Z_GATE and
               g3b_mean > 0.0 and g3b_z >= Z_GATE)

    gates = {
        "G1_deMoivre_scaling_law": g1_pass,
        "G2_extremes_small_n_dominated": g2_pass,
        "G3_robust_shifted_p_and_range": g3_pass,
    }
    order = ("G1_deMoivre_scaling_law",
             "G2_extremes_small_n_dominated",
             "G3_robust_shifted_p_and_range")
    all_pass = all(gates.values())
    first_failing = next((k for k in order if not gates[k]), None)

    return {
        "seed": SEED,
        "z_gate": Z_GATE,
        "trials": TRIALS,
        "units": M,
        "n_lo": LO,
        "n_hi": HI,
        "n_lo_shift": LO2,
        "n_hi_shift": HI2,
        "p_base": P,
        "p_shift": P_SHIFT,
        "ext_frac": EXT,
        "g1_scaling_corr_mean": r6(g1_mean),
        "g1_scaling_corr_std": r6(g1_std),
        "g1_z": r6(g1_z),
        "g2_extreme_delta_n_mean": r6(g2_mean),
        "g2_extreme_delta_n_std": r6(g2_std),
        "g2_z": r6(g2_z),
        "g3a_shifted_p_corr_mean": r6(g3a_mean),
        "g3a_shifted_p_z": r6(g3a_z),
        "g3b_shifted_range_delta_mean": r6(g3b_mean),
        "g3b_shifted_range_z": r6(g3b_z),
        "gates": gates,
        "all_pass": all_pass,
        "first_failing_gate": first_failing,
    }


def _canon(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r1 = run()
    r2 = run()
    assert _canon(r1) == _canon(r2), "non-deterministic double-run"
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + hashlib.sha256(_canon(r1).encode("utf-8")).hexdigest())
    return 0 if r1["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
