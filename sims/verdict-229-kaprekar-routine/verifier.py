#!/usr/bin/env python3
"""Kaprekar's-constant universal funnel - firsthand verifier (PROPOSAL 216).

Counterintuitive-but-exactly-true: under Kaprekar's routine every 4-digit
number with at least two distinct digits funnels to the single constant
6174 within at most 7 iterations. Proven here by EXHAUSTION over all 8991
valid inputs (not sampling), plus a seeded Monte-Carlo confirmation and a
3-digit dimension-shift control (constant 495, max 6 steps).

Stdlib-only. SEED=20260717. Deterministic across in-process double-run and
separate cross-invocation.
"""
import hashlib
import json
from fractions import Fraction

SEED = 20260717
N_MC = 200000
NULL_P0 = Fraction(99, 100)  # null hypothesis: fewer than 100% of numbers converge


def kaprekar_step(n, width):
    s = str(n).zfill(width)
    hi = int("".join(sorted(s, reverse=True)))
    lo = int("".join(sorted(s)))
    return hi - lo


def is_repdigit_str(s):
    return len(set(s)) == 1


def steps_to(n, width, fixed, cap=100):
    c = 0
    while n != fixed:
        n = kaprekar_step(n, width)
        c += 1
        if c > cap:
            return None
    return c


def valid_inputs(width):
    lo = 10 ** (width - 1)
    hi = 10 ** width - 1
    out = []
    for n in range(lo, hi + 1):
        if not is_repdigit_str(str(n)):
            out.append(n)
    return out


def exhaustive(width, fixed):
    inputs = valid_inputs(width)
    total = 0
    mx = 0
    nonconv = 0
    for n in inputs:
        c = steps_to(n, width, fixed)
        if c is None:
            nonconv += 1
            continue
        total += c
        if c > mx:
            mx = c
    mean = Fraction(total, len(inputs)) if inputs else Fraction(0)
    return {
        "domain_size": len(inputs),
        "nonconverge": nonconv,
        "max_steps": mx,
        "total_steps": total,
        "mean_steps": "{0}/{1}".format(mean.numerator, mean.denominator),
    }


def fixed_points(width):
    fps = []
    for n in valid_inputs(width):
        if kaprekar_step(n, width) == n:
            fps.append(n)
    return sorted(fps)


class LCG:
    """Deterministic 64-bit LCG (Numerical Recipes constants)."""

    def __init__(self, seed):
        self.s = seed & ((1 << 64) - 1)

    def _next(self):
        self.s = (self.s * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        return self.s

    def below(self, k):
        return self._next() % k


def mc_confirm(width, fixed, bound, n_draws, seed):
    inputs = valid_inputs(width)
    m = len(inputs)
    rng = LCG(seed)
    successes = 0
    for _ in range(n_draws):
        x = inputs[rng.below(m)]
        c = steps_to(x, width, fixed)
        if c is not None and c <= bound:
            successes += 1
    p_hat = Fraction(successes, n_draws)
    p0 = float(NULL_P0)
    se = (p0 * (1 - p0) / n_draws) ** 0.5
    z = (float(p_hat) - p0) / se
    return {
        "n_draws": n_draws,
        "successes": successes,
        "p_hat": "{0}/{1}".format(p_hat.numerator, p_hat.denominator),
        "null_p0": "{0}/{1}".format(NULL_P0.numerator, NULL_P0.denominator),
        "z": round(z, 6),
    }


def run_battery():
    four = exhaustive(4, 6174)
    fps4 = fixed_points(4)
    mc = mc_confirm(4, 6174, 7, N_MC, SEED)
    three = exhaustive(3, 495)
    fps3 = fixed_points(3)

    g1 = (four["nonconverge"] == 0 and four["max_steps"] == 7)
    wrong_bound_rejected = (four["max_steps"] > 6)
    g2 = (fps4 == [6174])
    g3 = (mc["z"] >= 3.0 and mc["successes"] == mc["n_draws"])
    g4 = (three["nonconverge"] == 0 and fps3 == [495] and three["max_steps"] == 6)

    gates = {"G1": g1, "G2": g2, "G3": g3, "G4": g4}
    sim_ready = all(gates.values()) and wrong_bound_rejected
    return {
        "proposal": 216,
        "seed": SEED,
        "four_digit": four,
        "four_fixed_points": fps4,
        "mc_4digit": mc,
        "three_digit": three,
        "three_fixed_points": fps3,
        "wrong_bound_max6_rejected": wrong_bound_rejected,
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
    determinism = (digest(r1) == digest(r2))
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("results_sha256={0}".format(digest(r1)))
    print("determinism_double_run={0}".format(determinism))
    sys.exit(0 if (r1["sim_ready"] and determinism) else 1)
