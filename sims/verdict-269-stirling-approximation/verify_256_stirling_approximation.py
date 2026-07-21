#!/usr/bin/env python3
"""verify_256_stirling_approximation.py — firsthand verifier (stdlib only).

Claim (pure math, closed form): Stirling's approximation for the factorial.

    lim_{n->inf} n! / ( sqrt(2*pi*n) * (n/e)^n ) = 1                 (the limit)

Write r_n = n! / ( sqrt(2*pi*n) * (n/e)^n ). Then ln(r_n) has the EXACT
asymptotic expansion (the Stirling series in log form)

    ln(r_n) = sum_{k>=1} c_k / n^(2k-1),
              c_k = B_{2k} / ( 2k(2k-1) ),

with B_{2k} the Bernoulli numbers, so the leading correction terms are the exact
rationals c_1 = 1/12, c_2 = -1/360, c_3 = 1/1260, c_4 = -1/1680, ...  The ratio
itself expands as r_n ~ sum_{k>=0} a_k / n^k with the exact Stirling-series
coefficients a_0 = 1, a_1 = 1/12, a_2 = 1/288, a_3 = -139/51840, ...  Robbins'
theorem (1955) gives the EXACT two-sided rational bracket, valid for every n>=1,

    1/(12n+1) < ln(r_n) < 1/(12n).                                   (Robbins)

Four gates, each read in its OWN direction:

  G1 EXACT (fractions.Fraction, 0 mismatches) — the exact-rational backbone of the
     Stirling series: (i) the Bernoulli numbers B_0..B_14 from the exact recurrence
     sum_{k=0}^{m} C(m+1,k) B_k = 0 match their known values; (ii) the log-series
     correction coefficients c_k = B_{2k}/(2k(2k-1)) match {1/12,-1/360,1/1260,
     -1/1680,1/1188,-691/360360,1/156}; (iii) the ratio-series coefficients
     a_0..a_6, built exactly by the exp-of-series recurrence a_k = (1/k) sum_j
     j*l_j*a_{k-j} from the log-series, satisfy the INVERSE (log-of-series) that
     recovers l_j back with 0 residual AND match the known {1,1/12,1/288,
     -139/51840,...}. Zero tolerance, zero mismatches. z = "exact".

  G2 MC AGREEMENT (|z| < 3) — estimate n! by Monte-Carlo integration of the Gamma
     representation n! = integral_0^inf x^n e^{-x} dx via importance sampling from
     a Gamma(shape=n, scale=1) proposal (stdlib random.gammavariate). The proposal
     normaliser is the EXACT integer (n-1)! (not the answer n!), so the per-draw
     estimator (n-1)! * x is a genuine unbiased estimator of n! with E[x]=n. Form
     the ratio r_hat = (n-1)! * xbar / D, D = sqrt(2*pi*n)(n/e)^n, and compare it to
     the closed-form Stirling prediction r_stir = exp(sum c_k/n^(2k-1)). iid draws
     => the plain iid standard error is honest. Report z = (r_hat - r_stir)/SE.

  G3 ROBUSTNESS / INVARIANCE (own direction) — (a) Robbins' EXACT rational bracket
     1/(12n+1) < ln(r_n) < 1/(12n) holds for the whole sweep n=1..SWEEP_MAX, checked
     in high-precision Decimal (0 violations); report the tightest upper/lower gaps.
     (b) Estimator invariance (numeric z): the SAME r_n is re-estimated with a
     DIFFERENT importance proposal Gamma(shape=n+2), whose per-draw estimator is
     (n+1)! / x; the estimate is invariant to that nuisance proposal and agrees with
     r_stir at z_inv, reported as G3's numeric z.

  G4 FALSIFIABILITY (own direction, SAME MC sample as G2) — the plausible NAIVE
     foils. Primary: the sqrt(pi*n) prefactor (the factor-of-2-under-the-root error,
     sqrt(pi*n) instead of sqrt(2*pi*n)) predicts r = 1/sqrt(2) = 0.7071; on the SAME
     sample it is REJECTED at |z_foil| >> Z_REJECT while the true r AGREES at |z|<3.
     Secondary corroboration: dropping the 1/(12n) correction (r = 1 exactly) is
     rejected at |z| > Z_ACCEPT on the same sample.

Determinism: results dict -> canonical JSON (sorted keys) -> sha256 (full 64 hex,
never truncated). main() builds the results twice in-process and asserts byte
equality; --selfcheck prints "SELFCHECK: byte-identical"; a separate process
re-invocation reproduces the digest byte-for-byte. random.seed(SEED) is re-seeded
at the START of each Monte-Carlo gate so gate order cannot perturb the payload.
Stdlib only: json, hashlib, math, random, fractions, decimal, sys.
"""

from __future__ import annotations

import decimal
import hashlib
import json
import math
import random
import sys
from decimal import Decimal
from fractions import Fraction

# ---------------------------------------------------------------------------
# Constants (all payload-affecting knobs are module-level and hardcoded).
# ---------------------------------------------------------------------------
SEED = 20260717
N_STIRLING = 10          # the fixed n for the Monte-Carlo factorial estimate
N_MC = 400_000           # Monte-Carlo draws for the headline ratio (G2/G4)
N_MC_INV = 400_000       # draws for the G3 estimator-invariance leg
K_MAX = 7                # number of log-series correction coefficients c_1..c_K
A_MAX = 6                # highest ratio-series coefficient a_0..a_A_MAX
SWEEP_MAX = 64           # Robbins bracket sweep n = 1..SWEEP_MAX
DPS = 60                 # Decimal working precision for the Robbins sweep
KTERMS = 4               # correction terms used in the closed-form target r_stir
Z_ACCEPT = 3.0
Z_REJECT = 50.0

# pi to 60 significant digits (for the high-precision Robbins sweep).
PI_STR = "3.14159265358979323846264338327950288419716939937510582097494"

# Known exact values for the EXACT gate (independent literals to check against).
BERNOULLI_KNOWN = {
    0: Fraction(1, 1), 2: Fraction(1, 6), 4: Fraction(-1, 30),
    6: Fraction(1, 42), 8: Fraction(-1, 30), 10: Fraction(5, 66),
    12: Fraction(-691, 2730), 14: Fraction(7, 6),
}
C_KNOWN = [
    Fraction(1, 12), Fraction(-1, 360), Fraction(1, 1260), Fraction(-1, 1680),
    Fraction(1, 1188), Fraction(-691, 360360), Fraction(1, 156),
]
A_KNOWN = [
    Fraction(1), Fraction(1, 12), Fraction(1, 288), Fraction(-139, 51840),
    Fraction(-571, 2488320), Fraction(163879, 209018880),
    Fraction(5246819, 75246796800),
]


# ---------------------------------------------------------------------------
# Exact rational machinery (no floats).
# ---------------------------------------------------------------------------
def binomial(n: int, k: int) -> int:
    return math.comb(n, k)


def bernoulli(upto: int) -> list[Fraction]:
    """B_0..B_upto by the recurrence sum_{k=0}^{m} C(m+1,k) B_k = 0 (B_0 = 1)."""
    B = [Fraction(0)] * (upto + 1)
    B[0] = Fraction(1)
    for m in range(1, upto + 1):
        s = Fraction(0)
        for k in range(m):
            s += binomial(m + 1, k) * B[k]
        B[m] = -s / (m + 1)
    return B


def log_series_coeffs(B: list[Fraction], kmax: int) -> list[Fraction]:
    """c_k = B_{2k} / (2k(2k-1)) for k = 1..kmax (exact)."""
    return [B[2 * k] / (2 * k * (2 * k - 1)) for k in range(1, kmax + 1)]


def ratio_series_coeffs(c: list[Fraction], amax: int) -> list[Fraction]:
    """a_0..a_amax with r_n ~ sum a_k / n^k, built exactly from ln(r_n) = sum
    c_k / n^(2k-1) by the exp-of-series recurrence a_k = (1/k) sum_{j=1}^k j l_j
    a_{k-j}, where l_j is the coeff of u^j in the log-series (l_j = c_{(j+1)/2}
    for odd j, else 0). a_0 = 1."""
    l = [Fraction(0)] * (amax + 1)
    for k in range(1, len(c) + 1):
        j = 2 * k - 1                     # log-series has only odd powers
        if j <= amax:
            l[j] = c[k - 1]
    a = [Fraction(0)] * (amax + 1)
    a[0] = Fraction(1)
    for k in range(1, amax + 1):
        acc = Fraction(0)
        for j in range(1, k + 1):
            acc += j * l[j] * a[k - j]
        a[k] = acc / k
    return a, l


def recover_log_from_ratio(a: list[Fraction], amax: int) -> list[Fraction]:
    """Inverse (log-of-series): recover l_k from the ratio-series a_k via
    l_k = a_k - (1/k) sum_{j=1}^{k-1} j l_j a_{k-j}. Must return the l used to
    build a (exact self-consistency of exp then log)."""
    l = [Fraction(0)] * (amax + 1)
    for k in range(1, amax + 1):
        acc = Fraction(0)
        for j in range(1, k):
            acc += j * l[j] * a[k - j]
        l[k] = a[k] - acc / k
    return l


# ---------------------------------------------------------------------------
# G1 — EXACT Stirling-series backbone (Fraction, zero tolerance).
# ---------------------------------------------------------------------------
def gate1_exact() -> dict:
    mismatches = 0
    checked = 0

    B = bernoulli(2 * K_MAX)
    # (i) Bernoulli numbers match their known values.
    for m, known in BERNOULLI_KNOWN.items():
        checked += 1
        if B[m] != known:
            mismatches += 1

    # (ii) log-series correction coefficients c_k match known rationals.
    c = log_series_coeffs(B, K_MAX)
    for got, known in zip(c, C_KNOWN):
        checked += 1
        if got != known:
            mismatches += 1

    # (iii) ratio-series coefficients a_k: build by exp-recurrence, verify the
    #       inverse log-of-series recovers l_j exactly, and match known a_k.
    a, l = ratio_series_coeffs(c, A_MAX)
    l_back = recover_log_from_ratio(a, A_MAX)
    for k in range(A_MAX + 1):
        checked += 1
        if l_back[k] != l[k]:
            mismatches += 1
    for got, known in zip(a, A_KNOWN):
        checked += 1
        if got != known:
            mismatches += 1

    return {
        "checked": checked,
        "mismatches": mismatches,
        "c_1": str(c[0]),      # 1/12
        "c_2": str(c[1]),      # -1/360
        "c_3": str(c[2]),      # 1/1260
        "c_4": str(c[3]),      # -1/1680
        "a_1": str(a[1]),      # 1/12
        "a_2": str(a[2]),      # 1/288
        "a_3": str(a[3]),      # -139/51840
        "pass": mismatches == 0,
        "z": "exact",
    }


# ---------------------------------------------------------------------------
# Closed-form Stirling ratio prediction r_stir(n) = exp(sum c_k / n^(2k-1)).
# ---------------------------------------------------------------------------
def stirling_ratio_closed_form(n: int, c: list[Fraction], kterms: int) -> float:
    s = 0.0
    for k in range(1, kterms + 1):
        s += float(c[k - 1]) / (n ** (2 * k - 1))
    return math.exp(s)


# ---------------------------------------------------------------------------
# Monte-Carlo estimator of the ratio r_n via the Gamma representation.
# ---------------------------------------------------------------------------
def log_denom(n: int) -> float:
    """ln D, D = sqrt(2*pi*n) (n/e)^n = the Stirling scaffold."""
    return 0.5 * math.log(2.0 * math.pi * n) + n * math.log(n) - n


def mc_ratio(rng: random.Random, n: int, shape: int, draws: int):
    """Importance-sample n! = integral x^n e^{-x} dx with proposal Gamma(shape,1).
    Per-draw weight w(x) = x^n e^{-x} / q(x) = Gamma(shape) * x^(n-shape+1), whose
    mean estimates n!. Return (r_hat, se) for r = n!/D formed in log-space so no
    huge integer/float overflows. `shape` = n gives estimator (n-1)! * x; shape =
    n+2 gives estimator (n+1)! / x. The constant C = Gamma(shape)/D is exact via
    lgamma; the random part carries the variance."""
    lnC = math.lgamma(shape) - log_denom(n)     # ln( Gamma(shape) / D )
    C = math.exp(lnC)
    power = n - shape + 1                        # exponent on x in the weight
    s = 0.0
    s2 = 0.0
    for _ in range(draws):
        x = rng.gammavariate(shape, 1.0)
        m = x ** power                           # random part of the weight
        s += m
        s2 += m * m
    mean = s / draws
    sample_var = (s2 - draws * mean * mean) / (draws - 1)
    se_mean = math.sqrt(sample_var / draws)
    return C * mean, C * se_mean


# ---------------------------------------------------------------------------
# G2 (headline ratio) + G4 (falsifiability) share ONE sample.
# ---------------------------------------------------------------------------
def gate2_and_gate4(c: list[Fraction]) -> tuple[dict, dict]:
    random.seed(SEED)
    rng = random.Random(SEED)
    n = N_STIRLING
    r_hat, se = mc_ratio(rng, n, n, N_MC)          # shape = n  ->  (n-1)! * x
    r_stir = stirling_ratio_closed_form(n, c, KTERMS)
    z_true = (r_hat - r_stir) / se

    # Primary foil: sqrt(pi*n) prefactor (missing factor 2 under the root) predicts
    # the ratio n!/(sqrt(2*pi*n)(n/e)^n) equals sqrt(pi*n)/sqrt(2*pi*n) = 1/sqrt(2).
    foil_val = 1.0 / math.sqrt(2.0)
    z_foil = (r_hat - foil_val) / se
    # Secondary foil: dropping the 1/(12n) correction predicts r = 1 exactly.
    z_nocorr = (r_hat - 1.0) / se

    g2 = {
        "n": n,
        "N": N_MC,
        "shape": n,
        "r_hat": f"{r_hat:.6f}",
        "se": f"{se:.6f}",
        "r_stir_closed_form": f"{r_stir:.6f}",
        "z": f"{z_true:.4f}",
        "pass": abs(z_true) < Z_ACCEPT,
    }
    g4 = {
        "foil": "sqrt(pi*n) prefactor (factor-2-under-root error) -> ratio = 1/sqrt(2)",
        "foil_value": f"{foil_val:.6f}",
        "z_foil": f"{z_foil:.4f}",
        "z_true_same_sample": f"{z_true:.4f}",
        "secondary_foil": "drop the 1/(12n) correction -> ratio = 1",
        "z_secondary_foil": f"{z_nocorr:.4f}",
        "rejected": abs(z_foil) > Z_REJECT,
        "secondary_rejected": abs(z_nocorr) > Z_ACCEPT,
        "true_accepted_same_sample": abs(z_true) < Z_ACCEPT,
        "pass": (abs(z_foil) > Z_REJECT
                 and abs(z_nocorr) > Z_ACCEPT
                 and abs(z_true) < Z_ACCEPT),
    }
    return g2, g4


# ---------------------------------------------------------------------------
# G3 — robustness (Robbins exact bracket sweep) + estimator invariance.
# ---------------------------------------------------------------------------
def gate3_robustness(c: list[Fraction]) -> dict:
    # (a) Robbins' exact rational bracket 1/(12n+1) < ln(r_n) < 1/(12n) over the
    #     whole sweep, in high-precision Decimal.
    ctx = decimal.Context(prec=DPS)
    pi = ctx.create_decimal(PI_STR)
    violations = 0
    tight_upper = None      # min over n of ( U_n - ln_r_n )
    tight_lower = None      # min over n of ( ln_r_n - L_n )
    fact = 1
    for n in range(1, SWEEP_MAX + 1):
        fact *= n                                       # n! exact integer
        nd = ctx.create_decimal(n)
        ln_fact = ctx.create_decimal(fact).ln(ctx)
        ln_D = (ctx.create_decimal(2) * pi * nd).ln(ctx) / 2 + nd * nd.ln(ctx) - nd
        ln_r = ln_fact - ln_D
        U = ctx.create_decimal(1) / ctx.create_decimal(12 * n)
        L = ctx.create_decimal(1) / ctx.create_decimal(12 * n + 1)
        if not (L < ln_r < U):
            violations += 1
        up = U - ln_r
        lo = ln_r - L
        tight_upper = up if tight_upper is None or up < tight_upper else tight_upper
        tight_lower = lo if tight_lower is None or lo < tight_lower else tight_lower

    # (b) estimator invariance: re-estimate the SAME r_n with a DIFFERENT proposal
    #     Gamma(shape = n+2), per-draw estimator (n+1)! / x.
    random.seed(SEED)
    rng = random.Random(SEED)
    n = N_STIRLING
    r_hat2, se2 = mc_ratio(rng, n, n + 2, N_MC_INV)
    r_stir = stirling_ratio_closed_form(n, c, KTERMS)
    z_inv = (r_hat2 - r_stir) / se2

    return {
        "robbins_sweep_max": SWEEP_MAX,
        "robbins_violations": violations,
        "robbins_tightest_upper_gap": f"{float(tight_upper):.3e}",
        "robbins_tightest_lower_gap": f"{float(tight_lower):.3e}",
        "invariance_shape": n + 2,
        "invariance_r_hat": f"{r_hat2:.6f}",
        "invariance_se": f"{se2:.6f}",
        "z": f"{z_inv:.4f}",
        "pass": violations == 0 and abs(z_inv) < Z_ACCEPT,
    }


# ---------------------------------------------------------------------------
# Assemble the whole payload.
# ---------------------------------------------------------------------------
def build_results() -> dict:
    B = bernoulli(2 * K_MAX)
    c = log_series_coeffs(B, K_MAX)

    g1 = gate1_exact()
    g2, g4 = gate2_and_gate4(c)
    g3 = gate3_robustness(c)
    all_pass = bool(g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"])
    first_failing = None
    for name, g in (("G1", g1), ("G2", g2), ("G3", g3), ("G4", g4)):
        if not g["pass"]:
            first_failing = name
            break
    return {
        "claim": "lim n!/(sqrt(2*pi*n)(n/e)^n) = 1; "
                 "ln(r_n) = sum B_{2k}/(2k(2k-1)) n^{-(2k-1)}; "
                 "Robbins 1/(12n+1) < ln(r_n) < 1/(12n)",
        "seed": SEED,
        "constants": {
            "N_STIRLING": N_STIRLING,
            "N_MC": N_MC,
            "N_MC_INV": N_MC_INV,
            "K_MAX": K_MAX,
            "A_MAX": A_MAX,
            "SWEEP_MAX": SWEEP_MAX,
            "DPS": DPS,
            "KTERMS": KTERMS,
            "Z_ACCEPT": f"{Z_ACCEPT:.1f}",
            "Z_REJECT": f"{Z_REJECT:.1f}",
        },
        "G1_exact_stirling_series": g1,
        "G2_mc_agreement": g2,
        "G3_robustness_invariance": g3,
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
    print(f"G1_z = {a['G1_exact_stirling_series']['z']} "
          f"(checked={a['G1_exact_stirling_series']['checked']}, "
          f"mismatches={a['G1_exact_stirling_series']['mismatches']})")
    print(f"G2_z = {a['G2_mc_agreement']['z']}")
    print(f"G3_z = {a['G3_robustness_invariance']['z']} "
          f"(robbins_violations={a['G3_robustness_invariance']['robbins_violations']})")
    print(f"G4_z_foil = {a['G4_falsifiability']['z_foil']}  "
          f"(G4_z_true_same_sample = {a['G4_falsifiability']['z_true_same_sample']})")
    print(f"all_pass = {a['all_pass']}  decision = {a['decision']}")
    print(f"results_sha256 = {dig}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
