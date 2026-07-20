#!/usr/bin/env python3
"""Consistent-hashing max-gap harmonic imbalance - firsthand verifier (PROPOSAL 217).

Counterintuitive-but-exactly-true: uniform random hashing is lopsided. Placing
n independent uniform points on a unit circle cuts it into n arcs, and the
EXPECTED largest arc equals H_n/n (H_n = sum_{j=1}^n 1/j) - a factor H_n ~ ln n
ABOVE the fair share 1/n. That gap is exactly why consistent hashing needs
virtual replicas. The exact combinatorial core is the alternating identity
  sum_{k=1}^n (-1)^(k+1) C(n,k) / k = H_n.

Stdlib-only. SEED=20260717, all randomness from random.Random(20260717).
Deterministic across in-process double-run and separate cross-invocation.
"""
import hashlib
import itertools
import json
import math
import random
from fractions import Fraction

SEED = 20260717
N_LIST = list(range(2, 13))          # G1/G4 exact identity range
G2_N = 4                             # exhaustive enumeration node count
G2_M = (8, 12, 16, 20)              # ring cell counts (C(m,4) each <= ~5000)
MC_N = (32, 64)                     # Monte-Carlo node counts
MC_T = 200000                       # trials per Monte-Carlo cell
SHIFT_L = 7.0                       # G4 alternate circumference


def Hn(n):
    """Exact n-th harmonic number as a Fraction."""
    return sum(Fraction(1, j) for j in range(1, n + 1))


def comb(n, k):
    return math.comb(n, k)


def A_exact(n):
    """A(n) = sum_{k=1}^n (-1)^(k+1) C(n,k) Fraction(1, k*n)."""
    total = Fraction(0)
    for k in range(1, n + 1):
        sign = 1 if (k % 2 == 1) else -1
        total += sign * comb(n, k) * Fraction(1, k * n)
    return total


def A_wrong(n):
    """Corrupted survival: alternating sign dropped (G5 leg b)."""
    total = Fraction(0)
    for k in range(1, n + 1):
        total += comb(n, k) * Fraction(1, k * n)
    return total


def frac_str(f):
    return "{0}/{1}".format(f.numerator, f.denominator)


# ---- G1: exact alternating identity A(n) == H_n/n -------------------------
def gate_g1():
    per_n = {}
    ok = True
    for n in N_LIST:
        A = A_exact(n)
        h = Hn(n)
        B = h / n
        eq = (A == B)
        ok = ok and eq
        per_n[str(n)] = {
            "A": frac_str(A),
            "B": frac_str(B),
            "H_n": frac_str(h),
            "ratio_nA_over_H": frac_str((n * A) / h),
            "equal": eq,
        }
    return ok, per_n


# ---- G2: exhaustive discrete-ring enumeration, monotone convergence -------
def max_circular_gap(occupied, m):
    p = sorted(occupied)
    n = len(p)
    mx = 0
    for i in range(n):
        nxt = p[i + 1] if i + 1 < n else p[0] + m
        g = nxt - p[i]
        if g > mx:
            mx = g
    return mx


def gate_g2():
    target = Hn(G2_N) / G2_N
    means = {}
    diffs = []
    for m in G2_M:
        total = 0
        cnt = 0
        for occ in itertools.combinations(range(m), G2_N):
            total += max_circular_gap(occ, m)
            cnt += 1
        E = Fraction(total, cnt * m)
        d = abs(E - target)
        means[str(m)] = {"E": frac_str(E), "E_float": round(float(E), 9),
                          "abs_err": round(float(d), 9)}
        diffs.append(d)
    monotone = all(diffs[i] > diffs[i + 1] for i in range(len(diffs) - 1))
    within = (float(diffs[-1]) <= 0.03)
    ok = monotone and within
    means["_target"] = frac_str(target)
    means["_target_float"] = round(float(target), 9)
    means["_monotone_strict_decrease"] = monotone
    means["_largest_m_within_0p03"] = within
    return ok, means


# ---- max arc of n uniform points on a circle of circumference L -----------
def max_arc(rng, n, L):
    pts = [rng.random() * L for _ in range(n)]
    pts.sort()
    mx = pts[0] + L - pts[-1]
    for i in range(1, n):
        g = pts[i] - pts[i - 1]
        if g > mx:
            mx = g
    return mx


def mc_stats(rng, n, L, T):
    """Return (mean, se) of the max arc over T trials, circumference L."""
    s = 0.0
    ss = 0.0
    for _ in range(T):
        x = max_arc(rng, n, L)
        s += x
        ss += x * x
    mean = s / T
    var = ss / T - mean * mean
    if var < 0.0:
        var = 0.0
    se = math.sqrt(var) / math.sqrt(T)
    return mean, se


# ---- G3: Monte-Carlo within 3 sigma of H_n/n ------------------------------
def gate_g3(rng):
    per_n = {}
    ok = True
    for n in MC_N:
        target = float(Hn(n) / n)
        mean, se = mc_stats(rng, n, 1.0, MC_T)
        z = (mean - target) / se
        good = (abs(z) <= 3.0)
        ok = ok and good
        per_n[str(n)] = {
            "target": round(target, 9),
            "mean": round(mean, 9),
            "se": round(se, 12),
            "z": round(z, 6),
            "within_3sigma": good,
        }
    return ok, per_n


# ---- G4: invariance - exact ratio == 1 and shift-circumference match ------
def gate_g4(rng):
    ratio_ok = all((N * A_exact(N)) / Hn(N) == 1 for N in N_LIST)
    per_n = {}
    shift_ok = True
    for n in MC_N:
        target = float(Hn(n) / n)
        mean, se = mc_stats(rng, n, SHIFT_L, MC_T)
        norm = mean / SHIFT_L
        se_norm = se / SHIFT_L
        z = (norm - target) / se_norm
        good = (abs(z) <= 3.0)
        shift_ok = shift_ok and good
        per_n[str(n)] = {
            "circumference": SHIFT_L,
            "target": round(target, 9),
            "normalized_mean": round(norm, 9),
            "z": round(z, 6),
            "within_3sigma": good,
        }
    ok = ratio_ok and shift_ok
    return ok, {"exact_ratio_one_all_n": ratio_ok, "shift": per_n}


# ---- G5: falsifiability - both wrong models must be rejected --------------
def gate_g5(rng, g3):
    # (a) naive "busiest owns 1/n": H_n/n != 1/n exactly for n>=2, and the MC
    #     z of the naive value 1/n for n=32 is far beyond 3 sigma.
    naive_neq = all((Hn(n) / n) != Fraction(1, n) for n in N_LIST)
    n = 32
    target_naive = 1.0 / n
    mean, se = mc_stats(rng, n, 1.0, MC_T)
    z_naive = (mean - target_naive) / se
    naive_rejected = naive_neq and (abs(z_naive) > 3.0)
    # (b) corrupted survival with the alternating sign dropped != H_n/n.
    wrong_neq = all(A_wrong(n) != (Hn(n) / n) for n in N_LIST)
    both_rejected = naive_rejected and wrong_neq
    return both_rejected, {
        "naive_1_over_n_neq_Hn_over_n": naive_neq,
        "naive_1_over_n_z_n32": round(z_naive, 6),
        "naive_REJECTED": naive_rejected,
        "dropped_sign_survival_neq": wrong_neq,
        "dropped_sign_REJECTED": wrong_neq,
        "both_wrong_models_rejected": both_rejected,
    }


def run_battery():
    rng = random.Random(SEED)
    g1_ok, g1 = gate_g1()
    g2_ok, g2 = gate_g2()
    g3_ok, g3 = gate_g3(rng)
    g4_ok, g4 = gate_g4(rng)
    g5_ok, g5 = gate_g5(rng, g3)

    gates = {"G1": g1_ok, "G2": g2_ok, "G3": g3_ok, "G4": g4_ok, "G5": g5_ok}
    sim_ready = all(gates.values())
    return {
        "proposal": 217,
        "seed": SEED,
        "n_list": N_LIST,
        "g1_identity": g1,
        "g2_enumeration": g2,
        "g3_montecarlo": g3,
        "g4_invariance": g4,
        "g5_falsifiability": g5,
        "gates": gates,
        "sim_ready": sim_ready,
    }


def digest(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


if __name__ == "__main__":
    import sys

    r1 = run_battery()
    r2 = run_battery()
    d1 = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    d2 = json.dumps(r2, sort_keys=True, separators=(",", ":"))
    determinism = (d1 == d2)
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("results_sha256={0}".format(digest(r1)))
    print("determinism_double_run={0}".format(determinism))
    sys.exit(0 if (r1["sim_ready"] and determinism) else 1)
