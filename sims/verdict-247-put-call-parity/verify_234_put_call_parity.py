#!/usr/bin/env python3
"""PROPOSAL 234 - Put-call parity in a no-arbitrage binomial market.

Claim (exact, closed-form): In an n-period recombining binomial market with
spot S0, strike K, up/down factors u > d > 0, and per-period gross risk-free
return R with d < R < u (no arbitrage), the risk-neutral prices of a European
call C and put P (same strike K, same maturity n) satisfy put-call parity
EXACTLY:

        C - P == S0 - K * R**(-n)

independently of u, d, and of the option values themselves. For the reference
market S0=100, K=100, u=2, d=1/2, R=5/4, n=2 (risk-neutral prob q=1/2) the
exact prices are C=48, P=12, so C-P = 36 == S0 - K*R**-2 = 100 - 64 = 36.

SEED = 20260717. Deterministic: build_results() is a pure function of SEED and
the module constants (per-gate random.Random(SEED); no wall-clock / PID /
unordered-set iteration in the hashed payload), so an in-process double-run and
a separate re-invocation are byte-identical; results_sha256 is the sha256 of
the canonical results dict.

Four gates, each in its own direction:
  G1 EXACT      - parity holds as an exact Fraction identity, and each price
                  matches the closed-form binomial pricing sum (path
                  enumeration == combinatorial formula) across a panel of
                  rational no-arbitrage markets.
  G2 MC AGREE   - a Monte-Carlo estimate of E[R^-n (call_payoff - put_payoff)]
                  agrees with the exact target S0 - K R^-n at |z| < Z_ACCEPT.
  G3 INVARIANCE - (a) the difference C-P is invariant to the volatility pair
                  (u,d) though C and P each move; (b) options are homogeneous
                  of degree 1: scaling (S0,K) by lambda scales C-P and the
                  parity target identically. Both exact via Fraction.
  G4 FALSIFY    - on the SAME MC sample, the plausible naive rule
                  "C - P == S0 - K" (undiscounted strike) is rejected at
                  |z| >= Z_REJECT.

Stdlib only: json, hashlib, math, random, fractions, itertools.
"""

import json
import hashlib
import math
import random
from fractions import Fraction
from itertools import product

SEED = 20260717

# ---- reference market (all rational) --------------------------------------
S0 = Fraction(100)
K = Fraction(100)
U = Fraction(2)
D = Fraction(1, 2)
R = Fraction(5, 4)
N = 2

# ---- gate constants -------------------------------------------------------
MC_TRIALS = 400_000
Z_ACCEPT = 3.0
Z_REJECT = 6.0

# panel of no-arbitrage markets (d < R < u) for the exact gate
PANEL = [
    (Fraction(100), Fraction(100), Fraction(2), Fraction(1, 2), Fraction(5, 4), 2),
    (Fraction(80), Fraction(100), Fraction(3, 2), Fraction(2, 3), Fraction(11, 10), 3),
    (Fraction(120), Fraction(90), Fraction(5, 3), Fraction(3, 5), Fraction(21, 20), 4),
    (Fraction(50), Fraction(50), Fraction(4, 3), Fraction(3, 4), Fraction(1), 5),
]


def q_rn(u, d, r):
    """Risk-neutral up-probability q = (R - d) / (u - d)."""
    return (r - d) / (u - d)


def price_by_enumeration(s0, k, u, d, r, n):
    """Exact European call & put prices by enumerating all 2**n up/down paths."""
    q = q_rn(u, d, r)
    disc = r ** (-n)
    c = Fraction(0)
    p = Fraction(0)
    for path in product((True, False), repeat=n):  # True = up move
        st = s0
        prob = Fraction(1)
        for up in path:
            if up:
                st *= u
                prob *= q
            else:
                st *= d
                prob *= (1 - q)
        c += prob * max(st - k, Fraction(0))
        p += prob * max(k - st, Fraction(0))
    return disc * c, disc * p


def price_by_formula(s0, k, u, d, r, n):
    """Same prices via the explicit combinatorial binomial sum (cross-check)."""
    q = q_rn(u, d, r)
    disc = r ** (-n)
    c = Fraction(0)
    p = Fraction(0)
    for j in range(n + 1):  # j up-moves
        weight = Fraction(math.comb(n, j)) * (q ** j) * ((1 - q) ** (n - j))
        st = s0 * (u ** j) * (d ** (n - j))
        c += weight * max(st - k, Fraction(0))
        p += weight * max(k - st, Fraction(0))
    return disc * c, disc * p


def gate1_exact():
    """G1: exact put-call parity + path-enum == combinatorial-formula."""
    ok = True
    rows = []
    for (s0, k, u, d, r, n) in PANEL:
        assert d < r < u, "market violates no-arbitrage d < R < u"
        c_e, p_e = price_by_enumeration(s0, k, u, d, r, n)
        c_f, p_f = price_by_formula(s0, k, u, d, r, n)
        lhs = c_e - p_e
        rhs = s0 - k * r ** (-n)
        enum_eq_formula = (c_e == c_f and p_e == p_f)
        parity_exact = (lhs == rhs)
        this = enum_eq_formula and parity_exact
        ok = ok and this
        rows.append({
            "market": f"S0={s0} K={k} u={u} d={d} R={r} n={n}",
            "C": str(c_e), "P": str(p_e),
            "C_minus_P": str(lhs), "S0_minus_K_disc": str(rhs),
            "enum_eq_formula": enum_eq_formula,
            "parity_exact": parity_exact,
        })
    return ok, {"panel": rows}


def _mc_sample():
    """One risk-neutral MC sample of X = R^-n (call_payoff - put_payoff).

    Per path, call_payoff - put_payoff = max(S_T-K,0) - max(K-S_T,0) = S_T - K
    identically, so X = R^-n (S_T - K) with E[X] = S0 - K R^-n exactly.
    """
    rng = random.Random(SEED)
    q = float(q_rn(U, D, R))
    u, d = float(U), float(D)
    disc = float(R ** (-N))
    k, s0 = float(K), float(S0)
    xs = []
    for _ in range(MC_TRIALS):
        st = s0
        for _ in range(N):
            st *= u if rng.random() < q else d
        xs.append(disc * (st - k))
    n = len(xs)
    mean = math.fsum(xs) / n
    var = math.fsum((x - mean) ** 2 for x in xs) / (n - 1)
    se = math.sqrt(var / n)
    return mean, se, n


def gate2_mc_agreement(sample):
    """G2: MC estimate of C-P agrees with the exact parity target, |z| < 3."""
    mean, se, n = sample
    target = float(S0 - K * R ** (-N))
    z = (mean - target) / se
    return abs(z) < Z_ACCEPT, {
        "trials": n,
        "mc_mean": round(mean, 6),
        "target": round(target, 6),
        "z": round(z, 6),
        "z_accept": Z_ACCEPT,
        "pass_if": "abs(z) < Z_ACCEPT",
    }


def gate3_invariance():
    """G3: (a) C-P invariant to (u,d); (b) degree-1 homogeneity in (S0,K)."""
    ok = True
    s0, k, r, n = Fraction(100), Fraction(100), Fraction(5, 4), 2
    target = s0 - k * r ** (-n)

    vol_rows = []
    for (u, d) in [(Fraction(2), Fraction(1, 2)),
                   (Fraction(3, 2), Fraction(2, 3)),
                   (Fraction(5, 3), Fraction(3, 5)),
                   (Fraction(9, 5), Fraction(5, 9))]:
        assert d < r < u
        c, p = price_by_enumeration(s0, k, u, d, r, n)
        exact = (c - p == target)
        ok = ok and exact
        vol_rows.append({"u": str(u), "d": str(d), "C": str(c), "P": str(p),
                         "C_minus_P": str(c - p), "matches_target": exact})

    base_u, base_d = Fraction(2), Fraction(1, 2)
    c0, p0 = price_by_enumeration(s0, k, base_u, base_d, r, n)
    base_diff = c0 - p0
    scale_rows = []
    for lam in [Fraction(3), Fraction(7, 2), Fraction(1, 5)]:
        c, p = price_by_enumeration(lam * s0, lam * k, base_u, base_d, r, n)
        exact = ((c - p == lam * base_diff)
                 and (c - p == lam * s0 - lam * k * r ** (-n)))
        ok = ok and exact
        scale_rows.append({"lambda": str(lam), "C_minus_P": str(c - p),
                           "lambda_times_base": str(lam * base_diff),
                           "matches": exact})

    return ok, {"target": str(target),
                "volatility_invariance": vol_rows,
                "scale_homogeneity": scale_rows}


def gate4_falsify(sample):
    """G4: refute the naive 'C - P == S0 - K' (undiscounted strike), |z| >= 6."""
    mean, se, n = sample
    naive_target = float(S0 - K)  # forgets to discount the strike
    z = (mean - naive_target) / se
    return abs(z) >= Z_REJECT, {
        "naive_claim": "C - P == S0 - K (undiscounted strike)",
        "naive_target": round(naive_target, 6),
        "mc_mean": round(mean, 6),
        "z_naive": round(z, 6),
        "z_reject": Z_REJECT,
        "pass_if": "abs(z_naive) >= Z_REJECT (naive rule refuted)",
    }


def build_results():
    """Pure function of SEED + constants; returns the canonical results dict."""
    c_ref, p_ref = price_by_enumeration(S0, K, U, D, R, N)
    sample = _mc_sample()

    g1_ok, g1 = gate1_exact()
    g2_ok, g2 = gate2_mc_agreement(sample)
    g3_ok, g3 = gate3_invariance()
    g4_ok, g4 = gate4_falsify(sample)

    gates = {
        "G1_exact_parity_identity": {"pass": g1_ok, **g1},
        "G2_montecarlo_agreement": {"pass": g2_ok, **g2},
        "G3_invariance_robustness": {"pass": g3_ok, **g3},
        "G4_falsifiability_naive": {"pass": g4_ok, **g4},
    }
    order = ["G1_exact_parity_identity", "G2_montecarlo_agreement",
             "G3_invariance_robustness", "G4_falsifiability_naive"]
    first_failing = next((g for g in order if not gates[g]["pass"]), None)
    all_pass = first_failing is None

    return {
        "claim": "put_call_parity_binomial: C - P == S0 - K * R**-n",
        "seed": SEED,
        "reference_market": {
            "S0": str(S0), "K": str(K), "u": str(U), "d": str(D),
            "R": str(R), "n": N, "q_riskneutral": str(q_rn(U, D, R)),
            "C": str(c_ref), "P": str(p_ref),
            "C_minus_P": str(c_ref - p_ref),
            "S0_minus_K_disc": str(S0 - K * R ** (-N)),
        },
        "gates": gates,
        "all_gates_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "sim-ready" if all_pass else "needs-more-grooming",
    }


def canonical(r):
    return json.dumps(r, sort_keys=True, separators=(",", ":"))


def main():
    c1 = canonical(build_results())
    c2 = canonical(build_results())
    assert c1 == c2, "NON-DETERMINISTIC: in-process double-run diverged"
    digest = hashlib.sha256(c1.encode()).hexdigest()
    results = build_results()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("in_process_double_run: IDENTICAL")
    print("results_sha256: " + digest)
    print("decision: " + results["decision"])
    raise SystemExit(0 if results["all_gates_pass"] else 1)


if __name__ == "__main__":
    main()
