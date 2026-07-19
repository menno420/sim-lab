#!/usr/bin/env python3
"""
Population-momentum verifier (idea-engine PROPOSAL 188, round-44 UNRELATED slot).

Head: a population whose fertility drops instantly to exact replacement
(net reproduction rate NRR = 1.000, intrinsic per-cohort growth zero) keeps
growing for roughly a generation, because the young age structure inherited
from the prior growth regime still carries a reproductive surplus. This is
Keyfitz's population momentum (1971).

stdlib-only, deterministic. SEED pinned; in-process double-run asserts
byte-identical results. Digest posture: WHOLE-DICT / NO-SELF-FIELD /
STDOUT-ONLY -- the compact-canonical results dict's own sha256 IS the digest;
the dict carries no self field; pretty dump to stdout; no on-disk JSON.
"""

import hashlib
import json
import math
import random

SEED = 20260717

# ---- pinned world ---------------------------------------------------------
N_CLASSES = 17            # 5-year age bins, ages 0..84
SURV = 0.96              # per-step (5-year) survival, classes 0..15
FERT_SHAPE = [0.0, 0.0, 0.0, 0.30, 0.90, 1.00, 0.70, 0.35, 0.10]  # classes 0..8
NRR_GROWTH = 1.50
NRR_REPL = 1.00
N0 = 300000
K_REPS = 1500
T_STEPS = 50
SHIFT_CLASSES = 1        # delayed-childbearing shift for the robustness gate
NULL_BAND = 0.02
Z_GATE = 3.0


def survival_vector():
    return [SURV] * (N_CLASSES - 1) + [0.0]


def survivorship(s):
    l = [1.0] * N_CLASSES
    for x in range(1, N_CLASSES):
        l[x] = l[x - 1] * s[x - 1]
    return l


def fert_shape(shift):
    shape = [0.0] * N_CLASSES
    for i, v in enumerate(FERT_SHAPE):
        j = i + shift
        if 0 <= j < N_CLASSES:
            shape[j] = v
    return shape


def scale_to_nrr(shape, s, target_nrr):
    l = survivorship(s)
    raw = sum(l[x] * shape[x] for x in range(N_CLASSES))
    alpha = target_nrr / raw
    return [alpha * shape[x] for x in range(N_CLASSES)]


def leslie(fert, s):
    m = [[0.0] * N_CLASSES for _ in range(N_CLASSES)]
    for x in range(N_CLASSES):
        m[0][x] = fert[x]
    for x in range(N_CLASSES - 1):
        m[x + 1][x] = s[x]
    return m


def matvec(m, v):
    return [sum(m[i][j] * v[j] for j in range(len(v))) for i in range(len(m))]


def stable_structure(m):
    v = [1.0 / N_CLASSES] * N_CLASSES
    for _ in range(2000):
        w = matvec(m, v)
        tot = sum(w)
        v = [x / tot for x in w]
    return v


def binom(n, p, rng):
    if n <= 0 or p <= 0.0:
        return 0
    if p >= 1.0:
        return n
    mean = n * p
    var = n * p * (1.0 - p)
    if mean > 15.0 and n * (1.0 - p) > 15.0:
        val = int(round(rng.gauss(mean, math.sqrt(var))))
        if val < 0:
            return 0
        if val > n:
            return n
        return val
    c = 0
    for _ in range(n):
        if rng.random() < p:
            c += 1
    return c


def poisson_like(mean, rng):
    if mean <= 0.0:
        return 0
    if mean > 15.0:
        val = int(round(rng.gauss(mean, math.sqrt(mean))))
        return val if val > 0 else 0
    ell = math.exp(-mean)
    k = 0
    prod = 1.0
    while True:
        k += 1
        prod *= rng.random()
        if prod <= ell:
            return k - 1


def integer_counts(structure, total):
    return [int(round(structure[x] * total)) for x in range(N_CLASSES)]


def project_stochastic(start_counts, fert, s, rng):
    counts = list(start_counts)
    for _ in range(T_STEPS):
        births_mean = sum(counts[x] * fert[x] for x in range(N_CLASSES))
        births = poisson_like(births_mean, rng)
        new = [0] * N_CLASSES
        for x in range(N_CLASSES - 1):
            new[x + 1] = binom(counts[x], s[x], rng)
        new[0] = births
        counts = new
    return sum(counts)


def replicate_momentum(structure, fert, s, rng):
    start = integer_counts(structure, N0)
    init_total = sum(start)
    final_total = project_stochastic(start, fert, s, rng)
    return final_total / init_total


def mean_se(xs):
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var / n)


def deterministic_momentum(structure, fert, s):
    counts = [structure[x] * N0 for x in range(N_CLASSES)]
    init = sum(counts)
    for _ in range(400):
        births = sum(counts[x] * fert[x] for x in range(N_CLASSES))
        new = [0.0] * N_CLASSES
        for x in range(N_CLASSES - 1):
            new[x + 1] = counts[x] * s[x]
        new[0] = births
        counts = new
    return sum(counts) / init


def run():
    rng = random.Random(SEED)
    s = survival_vector()

    shape0 = fert_shape(0)
    fert_growth = scale_to_nrr(shape0, s, NRR_GROWTH)
    fert_repl = scale_to_nrr(shape0, s, NRR_REPL)
    struct_growth = stable_structure(leslie(fert_growth, s))
    struct_repl = stable_structure(leslie(fert_repl, s))

    l = survivorship(s)
    nrr_repl_check = sum(l[x] * fert_repl[x] for x in range(N_CLASSES))
    m_det = deterministic_momentum(struct_growth, fert_repl, s)

    m_young = [replicate_momentum(struct_growth, fert_repl, s, rng) for _ in range(K_REPS)]
    mean1, se1 = mean_se(m_young)
    z1 = (mean1 - 1.0) / se1

    m_null = [replicate_momentum(struct_repl, fert_repl, s, rng) for _ in range(K_REPS)]
    mean_n, se_n = mean_se(m_null)
    z_null = (mean_n - 1.0) / se_n
    z_contrast = (mean1 - mean_n) / math.sqrt(se1 ** 2 + se_n ** 2)

    shape_s = fert_shape(SHIFT_CLASSES)
    fert_growth_s = scale_to_nrr(shape_s, s, NRR_GROWTH)
    fert_repl_s = scale_to_nrr(shape_s, s, NRR_REPL)
    struct_growth_s = stable_structure(leslie(fert_growth_s, s))
    m_shift = [replicate_momentum(struct_growth_s, fert_repl_s, s, rng) for _ in range(K_REPS)]
    mean3, se3 = mean_se(m_shift)
    z3 = (mean3 - 1.0) / se3

    g1 = bool(z1 >= Z_GATE and mean1 > 1.0)
    g2 = bool(abs(mean_n - 1.0) < NULL_BAND and z_contrast >= Z_GATE)
    g3 = bool(z3 >= Z_GATE)
    all_pass = bool(g1 and g2 and g3)

    return {
        "seed": SEED,
        "world": {
            "n_classes": N_CLASSES,
            "survival": round(SURV, 6),
            "nrr_growth": round(NRR_GROWTH, 6),
            "nrr_repl_check": round(nrr_repl_check, 6),
            "n0": N0,
            "k_reps": K_REPS,
            "t_steps": T_STEPS,
            "shift_classes": SHIFT_CLASSES,
            "null_band": round(NULL_BAND, 6),
            "z_gate": round(Z_GATE, 6),
        },
        "deterministic_momentum": round(m_det, 6),
        "g1_momentum": {
            "mean_m": round(mean1, 6),
            "se": round(se1, 6),
            "z": round(z1, 6),
            "pass": g1,
        },
        "g2_null_contrast": {
            "mean_m_null": round(mean_n, 6),
            "se_null": round(se_n, 6),
            "z_null": round(z_null, 6),
            "z_contrast": round(z_contrast, 6),
            "pass": g2,
        },
        "g3_robustness_shift": {
            "mean_m_shift": round(mean3, 6),
            "se": round(se3, 6),
            "z": round(z3, 6),
            "pass": g3,
        },
        "all_pass": all_pass,
    }


def main():
    r1 = run()
    r2 = run()
    assert r1 == r2, "in-process double-run mismatch: non-deterministic"
    payload = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print(f"Results-JSON sha256: {digest}")
    raise SystemExit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
