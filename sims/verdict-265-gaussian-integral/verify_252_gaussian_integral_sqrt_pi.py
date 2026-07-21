#!/usr/bin/env python3
"""verify_252_gaussian_integral_sqrt_pi.py — firsthand verifier (stdlib only).

Claim (pure math, closed form): the Gaussian integral

    I = ∫_{-∞}^{∞} e^{-x^2} dx = sqrt(pi)          (EXACT closed form)

and, more generally, its even moments are

    M_{2m} = ∫_{-∞}^{∞} x^{2m} e^{-x^2} dx = sqrt(pi) · (2m-1)!! / 2^m ,

so the DIMENSIONLESS moment ratio R_m = M_{2m}/M_0 = (2m-1)!!/2^m = (2m)!/(4^m m!)
is EXACTLY RATIONAL (the irrational sqrt(pi) cancels). Integration by parts gives
the exact three-term recurrence M_{2m} = ((2m-1)/2) · M_{2m-2} (the boundary term
x^{2m-1} e^{-x^2} vanishes at ±∞), which the closed form must satisfy identically.

Four gates, each read in its OWN direction:

  G1 EXACT (fractions.Fraction, 0 mismatches) — the moment-ratio identity that
     UNDERLIES the Gaussian integral: for m = 0..M_MAX assert, exactly, that the
     recurrence route R_m = prod_{j=1}^m (2j-1)/2 equals the closed form
     (2m)!/(4^m m!) AND the double-factorial identity (2m-1)!! · 2^m · m! == (2m)!.
     Zero tolerance, zero mismatches. z = null / "exact".

  G2 MC AGREEMENT (|z| < 3) — estimate I = sqrt(pi) by Monte-Carlo integration:
     X ~ Uniform[-L, L], estimator g = 2L·e^{-X^2}, so E[g] = ∫_{-L}^{L} e^{-x^2}dx
     = sqrt(pi)·erf(L). At L=6, erf(6) = 1 - 2.2e-17, so the honest target is
     sqrt(pi)·erf(L) (zero truncation bias in the comparison) and equals sqrt(pi)
     to ~16 digits. iid draws → the plain iid standard error is honest (no batch
     means / thinning — that is only for autocorrelated sample paths, which this
     is not). Report z = (xbar - target)/SE.

  G3 INVARIANCE (own direction) — (a) EXACT scale invariance of the dimensionless
     ratio (Fraction, 0 mismatches): for several rational a>0, the scaled recurrence
     M_{2m}(a) = ((2m-1)/(2a)) · M_{2m-2}(a) gives a^m · (M_{2m}(a)/M_0(a)) ==
     (2m-1)!!/2^m independent of a. (b) MC scale + translation law (|z|<3):
     ∫e^{-a x^2}dx = sqrt(pi/a) so sqrt(a)·∫e^{-ax^2}dx = sqrt(pi); and
     ∫e^{-(x-mu)^2}dx = sqrt(pi) independent of mu. Every config agrees at small |z|.

  G4 FALSIFIABILITY (own direction, SAME MC sample as G2) — the plausible NAIVE
     foil confuses the Gaussian integral ∫e^{-x^2}dx = sqrt(pi) with the
     standard-normal normalization ∫e^{-x^2/2}dx = sqrt(2*pi) ≈ 2.5066 (this is
     also Stirling's constant). On the SAME sample the foil sqrt(2*pi) is REJECTED
     at |z_foil| >> Z_REJECT while the true sqrt(pi) AGREES at |z| < Z_ACCEPT.

Determinism: results dict -> canonical JSON (sorted keys) -> sha256 (full 64 hex,
never truncated). `main()` builds the results twice in-process and asserts byte
equality; `--selfcheck` prints "SELFCHECK: byte-identical"; a separate process
re-invocation reproduces the digest byte-for-byte. random.seed(SEED) is re-seeded
at the START of each Monte-Carlo gate so gate order cannot perturb the payload.
Stdlib only: json, hashlib, math, random, fractions, sys.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from fractions import Fraction

# ---------------------------------------------------------------------------
# Constants (all payload-affecting knobs are module-level and hardcoded).
# ---------------------------------------------------------------------------
SEED = 20260717
L = 6.0                 # half-width of the uniform importance window
N_MC = 400_000          # Monte-Carlo draws for the headline integral (G2/G4)
N_MC_INV = 200_000      # draws per config for the G3 invariance MC legs
M_MAX = 12              # highest moment index for the exact identity (m = 0..M_MAX)
Z_ACCEPT = 3.0
Z_REJECT = 50.0
# Rational scales for the EXACT G3 scale-invariance leg.
EXACT_SCALES = (Fraction(1), Fraction(2), Fraction(3), Fraction(5), Fraction(1, 2))
# (a, mu) configs for the MC G3 scale + translation legs.
MC_CONFIGS = ((1.0, 0.0), (2.0, 0.0), (0.5, 0.0), (1.0, 3.0), (1.0, -2.0), (3.0, 1.0))

SQRT_PI = math.sqrt(math.pi)
SQRT_2PI = math.sqrt(2.0 * math.pi)


# ---------------------------------------------------------------------------
# Exact rational machinery (no floats).
# ---------------------------------------------------------------------------
def factorial(n: int) -> int:
    return math.factorial(n)


def double_factorial_odd(m: int) -> int:
    """(2m-1)!! = product of the first m odd numbers; empty product = 1 for m=0."""
    out = 1
    for j in range(1, m + 1):
        out *= (2 * j - 1)
    return out


def moment_ratio_recurrence(m: int, a: Fraction = Fraction(1)) -> Fraction:
    """R_m(a) = M_{2m}(a)/M_0(a) built purely from the integration-by-parts
    recurrence M_{2m}(a) = ((2m-1)/(2a)) M_{2m-2}(a). Exact Fraction, no floats."""
    r = Fraction(1)
    for j in range(1, m + 1):
        r *= Fraction(2 * j - 1, 1) / (2 * a)
    return r


def moment_ratio_closed_form(m: int) -> Fraction:
    """Closed form R_m = (2m)!/(4^m m!) (equivalently (2m-1)!!/2^m)."""
    return Fraction(factorial(2 * m), (4 ** m) * factorial(m))


# ---------------------------------------------------------------------------
# G1 — EXACT moment-ratio identity (Fraction, zero tolerance).
# ---------------------------------------------------------------------------
def gate1_exact() -> dict:
    mismatches = 0
    checked = 0
    for m in range(0, M_MAX + 1):
        checked += 1
        r_rec = moment_ratio_recurrence(m)                       # recurrence route
        r_cf = moment_ratio_closed_form(m)                       # closed-form route
        r_df = Fraction(double_factorial_odd(m), 2 ** m)         # (2m-1)!!/2^m route
        if r_rec != r_cf or r_rec != r_df:
            mismatches += 1
        # Double-factorial <-> factorial integer identity: (2m-1)!! 2^m m! == (2m)!
        if double_factorial_odd(m) * (2 ** m) * factorial(m) != factorial(2 * m):
            mismatches += 1
    # A couple of exact spot values, disclosed in the results for a human reader.
    return {
        "checked": checked,
        "mismatches": mismatches,
        "R_1": str(moment_ratio_closed_form(1)),   # 1/2
        "R_2": str(moment_ratio_closed_form(2)),   # 3/4
        "R_3": str(moment_ratio_closed_form(3)),   # 15/8
        "R_6": str(moment_ratio_closed_form(6)),   # 10395/64
        "pass": mismatches == 0,
        "z": "exact",
    }


# ---------------------------------------------------------------------------
# Monte-Carlo estimator (shared shape).
# ---------------------------------------------------------------------------
def mc_integral(rng: random.Random, n: int, half_width: float, a: float, mu: float):
    """Estimate ∫_{mu-hw}^{mu+hw} e^{-a (x-mu)^2} dx by uniform importance sampling.
    Returns (mean, standard_error) of the estimator g = 2*hw*e^{-a (X-mu)^2},
    X ~ Uniform[mu-hw, mu+hw]. Sums kept in float (MC is intrinsically float)."""
    lo, hi = mu - half_width, mu + half_width
    width = hi - lo  # = 2*half_width
    s = 0.0
    s2 = 0.0
    for _ in range(n):
        x = rng.uniform(lo, hi)
        g = width * math.exp(-a * (x - mu) * (x - mu))
        s += g
        s2 += g * g
    mean = s / n
    # unbiased variance of the mean: Var(mean) = sample_var / n
    sample_var = (s2 - n * mean * mean) / (n - 1)
    se = math.sqrt(sample_var / n)
    return mean, se


# ---------------------------------------------------------------------------
# G2 (headline integral) + G4 (falsifiability) share ONE sample.
# ---------------------------------------------------------------------------
def gate2_and_gate4() -> tuple[dict, dict]:
    random.seed(SEED)
    rng = random.Random(SEED)
    mean, se = mc_integral(rng, N_MC, L, 1.0, 0.0)
    target = SQRT_PI * math.erf(L)          # honest target: no truncation bias
    z_true = (mean - target) / se
    z_foil = (mean - SQRT_2PI) / se         # naive foil: standard-normal normalizer
    g2 = {
        "N": N_MC,
        "L": f"{L:.1f}",
        "estimate": f"{mean:.6f}",
        "se": f"{se:.6f}",
        "target_sqrt_pi": f"{SQRT_PI:.6f}",
        "target_truncated": f"{target:.6f}",
        "erf_L_defect": f"{1.0 - math.erf(L):.3e}",
        "z": f"{z_true:.4f}",
        "pass": abs(z_true) < Z_ACCEPT,
    }
    g4 = {
        "foil": "sqrt(2*pi) — the standard-normal normalizer (Stirling's constant)",
        "foil_value": f"{SQRT_2PI:.6f}",
        "z_foil": f"{z_foil:.4f}",
        "z_true_same_sample": f"{z_true:.4f}",
        "rejected": abs(z_foil) > Z_REJECT,
        "true_accepted_same_sample": abs(z_true) < Z_ACCEPT,
        "pass": abs(z_foil) > Z_REJECT and abs(z_true) < Z_ACCEPT,
    }
    return g2, g4


# ---------------------------------------------------------------------------
# G3 — invariance (exact scale leg + MC scale/translation leg).
# ---------------------------------------------------------------------------
def gate3_invariance() -> dict:
    # (a) EXACT scale invariance of the dimensionless ratio (Fraction).
    exact_mismatches = 0
    exact_checked = 0
    baseline = [Fraction(double_factorial_odd(m), 2 ** m) for m in range(M_MAX + 1)]
    for a in EXACT_SCALES:
        for m in range(M_MAX + 1):
            exact_checked += 1
            # a^m * (M_{2m}(a)/M_0(a)) must be scale-independent == (2m-1)!!/2^m.
            val = (a ** m) * moment_ratio_recurrence(m, a)
            if val != baseline[m]:
                exact_mismatches += 1

    # (b) MC scale + translation law: sqrt(a)*∫e^{-a(x-mu)^2}dx == sqrt(pi).
    random.seed(SEED)
    rng = random.Random(SEED)
    configs = []
    max_abs_z = 0.0
    for a, mu in MC_CONFIGS:
        hw = L / math.sqrt(a)                       # keep erf(hw*sqrt(a)) = erf(L) ~ 1
        mean, se = mc_integral(rng, N_MC_INV, hw, a, mu)
        scaled_mean = math.sqrt(a) * mean
        scaled_se = math.sqrt(a) * se
        target = SQRT_PI * math.erf(L)
        z = (scaled_mean - target) / scaled_se
        max_abs_z = max(max_abs_z, abs(z))
        configs.append({
            "a": f"{a:.4f}",
            "mu": f"{mu:.4f}",
            "sqrt_a_times_estimate": f"{scaled_mean:.6f}",
            "z": f"{z:.4f}",
        })
    return {
        "exact_checked": exact_checked,
        "exact_mismatches": exact_mismatches,
        "mc_configs": configs,
        "mc_max_abs_z": f"{max_abs_z:.4f}",
        "pass": exact_mismatches == 0 and max_abs_z < Z_ACCEPT,
    }


# ---------------------------------------------------------------------------
# Assemble the whole payload.
# ---------------------------------------------------------------------------
def build_results() -> dict:
    g1 = gate1_exact()
    g2, g4 = gate2_and_gate4()
    g3 = gate3_invariance()
    all_pass = bool(g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"])
    first_failing = None
    for name, g in (("G1", g1), ("G2", g2), ("G3", g3), ("G4", g4)):
        if not g["pass"]:
            first_failing = name
            break
    return {
        "claim": "integral_{-inf}^{inf} e^{-x^2} dx = sqrt(pi); "
                 "even moments M_{2m} = sqrt(pi) (2m-1)!!/2^m",
        "seed": SEED,
        "constants": {
            "L": f"{L:.1f}",
            "N_MC": N_MC,
            "N_MC_INV": N_MC_INV,
            "M_MAX": M_MAX,
            "Z_ACCEPT": f"{Z_ACCEPT:.1f}",
            "Z_REJECT": f"{Z_REJECT:.1f}",
        },
        "G1_exact_moment_identity": g1,
        "G2_mc_agreement": g2,
        "G3_invariance": g3,
        "G4_falsifiability": g4,
        "all_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "PASS" if all_pass else "FAIL",
    }


def canonical_json(results: dict) -> str:
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def digest(results: dict) -> str:
    return hashlib.sha256(canonical_json(results).encode("utf-8")).hexdigest()


def main(argv: list[str]) -> int:
    selfcheck = "--selfcheck" in argv[1:]

    a = build_results()
    b = build_results()
    ja, jb = canonical_json(a), canonical_json(b)
    if ja != jb:
        print("ERROR: in-process double-run is NOT byte-identical", file=sys.stderr)
        return 1
    identical = "IDENTICAL"
    dig = digest(a)

    if selfcheck:
        print("SELFCHECK: byte-identical" if ja == jb else "SELFCHECK: MISMATCH")
        print(f"results_sha256 = {dig}")
        return 0

    print(json.dumps(a, sort_keys=True, indent=2))
    print()
    print(f"in_process_double_run: {identical}")
    print(f"G1_z = {a['G1_exact_moment_identity']['z']}")
    print(f"G2_z = {a['G2_mc_agreement']['z']}")
    print(f"G3_mc_max_abs_z = {a['G3_invariance']['mc_max_abs_z']} "
          f"(exact_mismatches={a['G3_invariance']['exact_mismatches']})")
    print(f"G4_z_foil = {a['G4_falsifiability']['z_foil']}  "
          f"(G4_z_true_same_sample = {a['G4_falsifiability']['z_true_same_sample']})")
    print(f"all_pass = {a['all_pass']}  decision = {a['decision']}")
    print(f"results_sha256 = {dig}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
