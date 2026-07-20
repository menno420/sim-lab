#!/usr/bin/env python3
"""
Firsthand verifier - PROPOSAL 212: dimension-dependent recurrence of the simple
random walk (Polya's recurrence theorem).

Claim (counterintuitive-but-true): a symmetric nearest-neighbour random walk on
the integer lattice returns to its start with probability 1 in dimensions 1 and 2
(RECURRENT), but with probability only ~0.3405 in dimension 3 (TRANSIENT).
"A drunk man will find his way home; a drunk bird may be lost forever."

stdlib-only, deterministic (SEED=20260717). Two independent lines of evidence:

  EXACT (closed form vs exhaustive enumeration, integer/Fraction-exact):
    * number of length-2n closed walks:
        2D: a2(n) = C(2n,n)**2                          (Vandermonde)
        3D: a3(n) = sum_{i+j+k=n} (2n)! / (i!^2 j!^2 k!^2)
      G1/G2 verify these against brute-force enumeration of every step sequence.
    * single-step return prob p_d(2n) = a_d(n)/(2d)**(2n) obeys the local CLT
        2D:  n * p2(n)      -> 1/pi         (~0.3183)  => sum diverges  => RECURRENT
        3D:  n**1.5 * p3(n) -> 2(3/4pi)**1.5 (~0.2333) => sum converges => TRANSIENT
      G3/G4 check the finite-n scaled values land in predicted bands.

  MONTE CARLO (seeded, deterministic corroboration):
    G5  3D within-horizon return fraction sits >=3 sigma below the recurrence line 0.5.
    G6  2D return fraction dominates 3D AND rises with horizon (the divergent
        return-count signature) while 3D stays flat.

Decision: sim-ready iff all gates hold AND the battery is byte-identical across an
in-process double run.
"""

import hashlib
import json
import math
import random
from fractions import Fraction

SEED = 20260717


def a2_closed(n):
    """# length-2n closed 2D walks = C(2n,n)^2."""
    return math.comb(2 * n, n) ** 2


def a3_closed(n):
    """# length-2n closed 3D walks = sum_{i+j+k=n} (2n)!/(i!^2 j!^2 k!^2)."""
    f = math.factorial
    top = f(2 * n)
    total = 0
    for i in range(n + 1):
        for j in range(n - i + 1):
            k = n - i - j
            total += top // (f(i) ** 2 * f(j) ** 2 * f(k) ** 2)
    return total


def enumerate_returns(dim, length):
    """Brute force: count length-`length` walks on Z^dim ending at the origin."""
    moves = []
    for axis in range(dim):
        for sign in (1, -1):
            v = [0] * dim
            v[axis] = sign
            moves.append(tuple(v))
    count = 0

    def rec(step, pos):
        nonlocal count
        if step == length:
            if all(c == 0 for c in pos):
                count += 1
            return
        for m in moves:
            rec(step + 1, tuple(p + d for p, d in zip(pos, m)))

    rec(0, tuple([0] * dim))
    return count


def p_single(dim, n):
    """Exact single-step return prob p_dim(2n) = a_dim(n)/(2*dim)^(2n)."""
    if dim == 2:
        a = a2_closed(n)
    elif dim == 3:
        a = a3_closed(n)
    else:
        raise ValueError(dim)
    return Fraction(a, (2 * dim) ** (2 * n))


def first_return_steps(rng, dim, walks, horizon):
    """First step (<=horizon) at which each walk revisits the origin, else None.
    Committed RNG protocol: walks 0..walks-1 in order; within a walk, step t draws
    rng.randrange(2*dim) as the move index (axis = idx>>1, sign = idx&1); a walk
    stops early on first return."""
    two_d = 2 * dim
    out = []
    for _ in range(walks):
        pos = [0] * dim
        ret = None
        for t in range(1, horizon + 1):
            idx = rng.randrange(two_d)
            axis = idx >> 1
            pos[axis] += 1 if (idx & 1) == 0 else -1
            if pos[axis] == 0 and all(c == 0 for c in pos):
                ret = t
                break
        out.append(ret)
    return out


def frac_within(first_returns, T):
    n = len(first_returns)
    c = sum(1 for r in first_returns if r is not None and r <= T)
    return c / n


def run_battery():
    exact_2d = []
    for two_n in (2, 4, 6):
        n = two_n // 2
        enum = enumerate_returns(2, two_n)
        closed = a2_closed(n)
        exact_2d.append({"2n": two_n, "enum": enum, "closed": closed, "eq": enum == closed})
    exact_3d = []
    for two_n in (2, 4):
        n = two_n // 2
        enum = enumerate_returns(3, two_n)
        closed = a3_closed(n)
        exact_3d.append({"2n": two_n, "enum": enum, "closed": closed, "eq": enum == closed})
    G1 = all(d["eq"] for d in exact_2d)
    G2 = all(d["eq"] for d in exact_3d)

    n2 = 2000
    scaled_2d = n2 * float(p_single(2, n2))            # -> 1/pi ~ 0.3183
    G3 = 0.30 <= scaled_2d <= 0.335

    n3 = 60
    scaled_3d = (n3 ** 1.5) * float(p_single(3, n3))   # -> 2(3/4pi)^1.5 ~ 0.2333
    G4 = 0.19 <= scaled_3d <= 0.29

    K = 15000
    T_hi = 1200
    T_lo = 100
    rng = random.Random(SEED)
    fr2 = first_return_steps(rng, 2, K, T_hi)          # 2D first ...
    fr3 = first_return_steps(rng, 3, K, T_hi)          # ... then 3D, same stream

    f2_hi = frac_within(fr2, T_hi)
    f2_lo = frac_within(fr2, T_lo)
    f3_hi = frac_within(fr3, T_hi)
    f3_lo = frac_within(fr3, T_lo)

    def se(p, n):
        return math.sqrt(max(p * (1 - p), 1e-12) / n)

    se3 = se(f3_hi, K)
    z_transient = (0.5 - f3_hi) / se3
    G5 = (z_transient >= 3.0) and (0.28 <= f3_hi <= 0.38)

    se_diff = math.sqrt(se(f2_hi, K) ** 2 + se(f3_hi, K) ** 2)
    z_dominate = (f2_hi - f3_hi) / se_diff
    se_shift2 = math.sqrt(se(f2_hi, K) ** 2 + se(f2_lo, K) ** 2)
    z_shift_2d = (f2_hi - f2_lo) / se_shift2
    se_shift3 = math.sqrt(se(f3_hi, K) ** 2 + se(f3_lo, K) ** 2)
    z_shift_3d = (f3_hi - f3_lo) / se_shift3
    G6 = (z_dominate >= 3.0) and (z_shift_2d >= 3.0) and (z_shift_2d >= z_shift_3d + 3.0)

    results = {
        "seed": SEED,
        "exact_2d": exact_2d,
        "exact_3d": exact_3d,
        "scaled_2d_n2000": round(scaled_2d, 6),
        "scaled_2d_target_1_over_pi": round(1.0 / math.pi, 6),
        "scaled_3d_n60": round(scaled_3d, 6),
        "scaled_3d_target": round(2.0 * (3.0 / (4.0 * math.pi)) ** 1.5, 6),
        "mc_K": K,
        "mc_T_hi": T_hi,
        "mc_T_lo": T_lo,
        "f2_hi": round(f2_hi, 6),
        "f2_lo": round(f2_lo, 6),
        "f3_hi": round(f3_hi, 6),
        "f3_lo": round(f3_lo, 6),
        "z_transient_3d": round(z_transient, 4),
        "z_dominate_2d_over_3d": round(z_dominate, 4),
        "z_shift_2d": round(z_shift_2d, 4),
        "z_shift_3d": round(z_shift_3d, 4),
        "gates": {"G1": G1, "G2": G2, "G3": G3, "G4": G4, "G5": G5, "G6": G6},
    }
    results["sim_ready"] = all(results["gates"].values())
    return results


def main():
    r1 = run_battery()
    r2 = run_battery()
    determinism_ok = (r1 == r2)
    r1["determinism_double_run_ok"] = determinism_ok
    payload = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("results_sha256=" + digest)
    return 0 if (r1["sim_ready"] and determinism_ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
