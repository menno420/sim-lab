#!/usr/bin/env python3
"""PROPOSAL 172 - Berkson's collider paradox: selection on an additive
composite of two INDEPENDENT traits manufactures a negative correlation
between them. Firsthand stdlib-only verifier. Deterministic under SEED.
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


def select_top(pairs, frac):
    k = max(2, int(round(len(pairs) * frac)))
    top = sorted(pairs, key=lambda p: p[0] + p[1], reverse=True)[:k]
    return [p[0] for p in top], [p[1] for p in top]


def draw_normal(rng, n):
    return [(rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0)) for _ in range(n)]


def draw_uniform(rng, n):
    return [(rng.random(), rng.random()) for _ in range(n)]


def draw_exponential(rng, n):
    return [(rng.expovariate(1.0), rng.expovariate(1.0)) for _ in range(n)]


def mean_std(vals):
    n = len(vals)
    m = sum(vals) / n
    if n < 2:
        return m, 0.0
    v = sum((x - m) ** 2 for x in vals) / (n - 1)
    return m, math.sqrt(v)


def z_neg(vals):
    m, s = mean_std(vals)
    n = len(vals)
    if s == 0.0:
        return 0.0
    return -(m / (s / math.sqrt(n)))


def run():
    rng = random.Random(SEED)
    TRIALS = 200
    N = 8000
    TOP = 0.10
    TIGHT = 0.02
    LOOSE = 0.40

    sel_top_r = []
    pop_r = []
    tight_r = []
    loose_r = []
    for _ in range(TRIALS):
        pairs = draw_normal(rng, N)
        pop_r.append(pearson([p[0] for p in pairs], [p[1] for p in pairs]))
        xs, ys = select_top(pairs, TOP)
        sel_top_r.append(pearson(xs, ys))
        xt, yt = select_top(pairs, TIGHT)
        tight_r.append(pearson(xt, yt))
        xl, yl = select_top(pairs, LOOSE)
        loose_r.append(pearson(xl, yl))

    g1_mean, g1_std = mean_std(sel_top_r)
    g1_z = z_neg(sel_top_r)
    g1_pass = (g1_mean < 0.0) and (g1_z >= Z_GATE)

    pop_mean, pop_std = mean_std(pop_r)
    diff = [s - p for s, p in zip(sel_top_r, pop_r)]
    g2_mean, _ = mean_std(diff)
    g2_z = z_neg(diff)
    g2_pass = (g2_mean < 0.0) and (g2_z >= Z_GATE) and (abs(pop_mean) < 0.01)

    deep_diff = [t - l for t, l in zip(tight_r, loose_r)]
    deep_mean, _ = mean_std(deep_diff)
    deep_z = z_neg(deep_diff)
    tight_mean, _ = mean_std(tight_r)
    loose_mean, _ = mean_std(loose_r)

    uni_r = []
    exp_r = []
    for _ in range(TRIALS):
        up = draw_uniform(rng, N)
        xu, yu = select_top(up, TOP)
        uni_r.append(pearson(xu, yu))
        ep = draw_exponential(rng, N)
        xe, ye = select_top(ep, TOP)
        exp_r.append(pearson(xe, ye))

    uni_mean, _ = mean_std(uni_r)
    uni_z = z_neg(uni_r)
    exp_mean, _ = mean_std(exp_r)
    exp_z = z_neg(exp_r)
    g3_pass = (uni_mean < 0.0 and uni_z >= Z_GATE and
               exp_mean < 0.0 and exp_z >= Z_GATE)

    gates = {
        "G1_selected_negative": g1_pass,
        "G2_selection_induced_reversal": g2_pass,
        "G3_robust_nonnormal": g3_pass,
    }
    order = ("G1_selected_negative", "G2_selection_induced_reversal",
             "G3_robust_nonnormal")
    all_pass = all(gates.values())
    first_failing = next((k for k in order if not gates[k]), None)

    return {
        "seed": SEED,
        "z_gate": Z_GATE,
        "trials": TRIALS,
        "n_per_trial": N,
        "top_frac": TOP,
        "tight_frac": TIGHT,
        "loose_frac": LOOSE,
        "g1_selected_mean_r": r6(g1_mean),
        "g1_selected_std_r": r6(g1_std),
        "g1_z": r6(g1_z),
        "population_mean_r": r6(pop_mean),
        "population_std_r": r6(pop_std),
        "g2_selected_minus_pop_mean": r6(g2_mean),
        "g2_z": r6(g2_z),
        "deepening_tight_mean_r": r6(tight_mean),
        "deepening_loose_mean_r": r6(loose_mean),
        "deepening_diff_mean": r6(deep_mean),
        "deepening_z": r6(deep_z),
        "g3_uniform_mean_r": r6(uni_mean),
        "g3_uniform_z": r6(uni_z),
        "g3_exponential_mean_r": r6(exp_mean),
        "g3_exponential_z": r6(exp_z),
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
