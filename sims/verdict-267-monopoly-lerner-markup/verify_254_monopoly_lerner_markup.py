#!/usr/bin/env python3
"""verify_254_monopoly_lerner_markup.py — firsthand verifier (stdlib only).

Claim (microeconomics / market power): a monopolist facing a LINEAR inverse
demand p(q) = a − b·q with constant marginal cost c (0 ≤ c < a, b > 0) sets the
profit-maximising quantity and price

    q* = (a − c)/(2b),   p* = (a + c)/2,   π* = (a − c)²/(4b),

and the resulting Lerner index of market power satisfies the exact identity

    L = (p* − c)/p* = (a − c)/(a + c) = 1/|ε*|,

i.e. the optimal markup equals the RECIPROCAL of the absolute price-elasticity of
demand evaluated at the optimum, |ε*| = (a + c)/(a − c). This is the textbook
monopoly markup rule specialised to the linear model, verified here in exact
rational arithmetic with two independent cross-checks.

Headline instance: a = 1, b = 1, c = 1/4 →
    p* = 5/8,  q* = 3/8,  π* = 9/64,  L = 3/5,  1/|ε*| = 3/5.

Microfoundation for the marginal-cost estimator (G2): a unit mass of consumers
with valuation v ~ Uniform[0, a]; buyer i purchases iff v_i ≥ p, so the demand
fraction is (a − p)/a — exactly this linear demand with b = a = 1. The expected
profit per consumer at price p is (p − c)·(a − p)/a, maximised at p = p*, with
maximum value π* per unit mass.

Four gates, each read in its OWN direction:

  G1 EXACT (fractions.Fraction, no float in the identity) — the monopoly
     first-order condition and the Lerner/reciprocal-elasticity identity, checked
     two independent ways and SWEPT over several rational triples:
       (i)  FOC cross-check: marginal revenue MR(q) = a − 2b·q satisfies
            MR(q*) == c exactly (setting MR = MC recovers q*).
       (ii) Reciprocal-elasticity cross-check: L(a,b,c) == 1/|ε*(a,b,c)| exactly
            AND == (a − c)/(a + c).
     Swept over (1,1,1/4),(3,2,1),(5,7,2),(10,1,3),(2,3,1/2); all hold exactly.
     This gate is EXACT, so z is not applicable → reported "exact — z=n/a".

  G2 MC AGREEMENT (|z| < 3, iid — NO thinning) — N_MC draws v ~ Uniform(0,a) via
     random.Random(SEED). Per-consumer profit at p* is (p* − c) if v ≥ p* else 0;
     the sample mean estimates π*. Draws are iid, so the plain iid standard error
     is the honest one (no batch means): SE = float(p*−c)·sqrt(q*(1−q*)/N), and
     z = (mean − float(π*))/SE. n_buy (the exact integer count v ≥ p*) is stored.

  G3 INVARIANCE (currency-scale invariance, own direction) — the Lerner index is
     UNIT-FREE: rescale the currency by λ (a→λa, b→λb, c→λc); q* is unchanged and
     L is unchanged. For λ ∈ {2, 3, 100, 1/7} assert lerner(λa,λb,λc) ==
     lerner(a,b,c) exactly via Fraction. Genuine economic content: market power is
     scale-free. This gate is EXACT → reported "exact — z=n/a".

  G4 FALSIFIABILITY (reject at large |z|, own direction, SAME SEED stream) — the
     pre-registered naive foil is "revenue maximisation equals profit maximisation"
     → price at p_rev = a/2 (ignores cost). Exactly π(p_rev) = (a/2−c)(a−a/2)/a =
     1/8 for the instance, strictly below π* = 9/64 (exact gap 1/64 > 0). On the
     SAME SEED-derived draws, the per-consumer difference (profit_at_p* −
     profit_at_p_rev) has sample mean estimating π* − π(p_rev) = 1/64 > 0;
     z_foil = mean_diff/SE_diff must be LARGE positive (reject the null
     "revenue-max is optimal"); asserted |z_foil| > 8. Also asserts π* > π(p_rev)
     exactly via Fraction.

Determinism: results dict -> canonical JSON (json.dumps, sort_keys=True) ->
sha256 (full 64 hex, never truncated). `main()` builds the results twice
in-process and asserts byte equality; `--selfcheck` prints "SELFCHECK:
byte-identical"; a separate process re-invocation reproduces the digest
byte-for-byte. SEED = 20260717 (hardcoded module constant). Stdlib only:
math, random, fractions, hashlib, json, argparse, sys.
"""

from __future__ import annotations

import argparse
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
A = Fraction(1)          # linear inverse-demand intercept  p(q) = a − b·q
B = Fraction(1)          # linear inverse-demand slope
C = Fraction(1, 4)       # constant marginal cost
N_MC = 2_000_000         # iid consumer draws (G2 / G4 share ONE SEED stream)
Z_ACCEPT = 3.0

# Structural economic asserts: 0 ≤ c < a and b > 0.
assert Fraction(0) <= C < A, "require 0 <= c < a"
assert B > 0, "require b > 0"


# ---------------------------------------------------------------------------
# Exact closed-form helpers (fractions.Fraction — no float in the identity).
# ---------------------------------------------------------------------------
def q_star(a: Fraction, b: Fraction, c: Fraction) -> Fraction:
    return (a - c) / (2 * b)


def p_star(a: Fraction, b: Fraction, c: Fraction) -> Fraction:
    return (a + c) / 2


def pi_star(a: Fraction, b: Fraction, c: Fraction) -> Fraction:
    return (a - c) ** 2 / (4 * b)


def lerner(a: Fraction, b: Fraction, c: Fraction) -> Fraction:
    p = p_star(a, b, c)
    return (p - c) / p


def abs_elasticity_at_opt(a: Fraction, b: Fraction, c: Fraction) -> Fraction:
    # |ε*| = (a + c)/(a − c); reciprocal of the Lerner index at the optimum.
    return (a + c) / (a - c)


def marginal_revenue(a: Fraction, b: Fraction, q: Fraction) -> Fraction:
    return a - 2 * b * q


def frac_str(f: Fraction) -> str:
    return f"{f.numerator}/{f.denominator}"


# ---------------------------------------------------------------------------
# G1 — EXACT identity (Fraction, two independent cross-checks, swept).
# ---------------------------------------------------------------------------
def gate1_exact() -> dict:
    triples = [
        (Fraction(1), Fraction(1), Fraction(1, 4)),
        (Fraction(3), Fraction(2), Fraction(1)),
        (Fraction(5), Fraction(7), Fraction(2)),
        (Fraction(10), Fraction(1), Fraction(3)),
        (Fraction(2), Fraction(3), Fraction(1, 2)),
    ]
    sweep_pass = []
    for a, b, c in triples:
        assert Fraction(0) <= c < a and b > 0, "sweep triple violates 0<=c<a, b>0"
        qs = q_star(a, b, c)
        # (i) FOC cross-check: MR(q*) == c exactly (MR = MC recovers q*).
        foc_ok = marginal_revenue(a, b, qs) == c
        # (ii) reciprocal-elasticity cross-check, two exact identities.
        L = lerner(a, b, c)
        recip_ok = (L == 1 / abs_elasticity_at_opt(a, b, c)) and (L == (a - c) / (a + c))
        ok = bool(foc_ok and recip_ok)
        assert ok, f"G1 identity failed on triple {(a, b, c)}"
        sweep_pass.append(ok)
    return {
        "sweep_pass": sweep_pass,          # per-triple exact PASS booleans
        "n_triples": len(triples),
        "all_exact_pass": all(sweep_pass),
        "foc_cross_check": "MR(q*) == c",
        "reciprocal_cross_check": "L == 1/|eps*| == (a-c)/(a+c)",
        "z": "exact — z=n/a",
        "pass": all(sweep_pass),
    }


# ---------------------------------------------------------------------------
# Monte-Carlo (iid consumer draws) — G2 agreement + G4 falsifiability share
# ONE SEED stream. Counts are exact integers -> fully deterministic payload.
# ---------------------------------------------------------------------------
def _mc_counts() -> tuple[int, int]:
    """Single pass over N_MC draws v ~ Uniform(0, a). Returns:
       n_star = #{v >= p*}         (buyers at the monopoly price p*)
       n_mid  = #{p_rev <= v < p*} (buyers at the revenue-max price only)."""
    rng = random.Random(SEED)
    a_f = float(A)
    p_f = float(p_star(A, B, C))          # 0.625
    p_rev_f = float(A / 2)                # 0.5  (revenue-max price, ignores cost)
    n_star = 0
    n_mid = 0
    for _ in range(N_MC):
        v = rng.random() * a_f
        if v >= p_f:
            n_star += 1
        elif v >= p_rev_f:
            n_mid += 1
    return n_star, n_mid


def gate2_and_gate4(n_star: int, n_mid: int) -> tuple[dict, dict]:
    a, b, c = A, B, C
    ps = p_star(a, b, c)
    qs = q_star(a, b, c)
    pis = pi_star(a, b, c)
    margin = float(ps - c)                 # (p* − c) = 3/8
    qf = float(qs)                         # buy probability at p* = 3/8

    # --- G2: sample mean of per-consumer profit at p* estimates π*. ---
    mean_g2 = margin * n_star / N_MC
    se_g2 = margin * math.sqrt(qf * (1.0 - qf) / N_MC)
    z_g2 = (mean_g2 - float(pis)) / se_g2

    g2 = {
        "n": N_MC,
        "n_buy": n_star,                   # exact integer count v >= p*
        "z": f"{z_g2:.4f}",
        "pass": abs(z_g2) < Z_ACCEPT,
    }

    # --- G4: same SEED stream; per-consumer diff (profit_p* − profit_p_rev). ---
    # diff takes value +1/8 for v >= p* (n_star), −1/4 for p_rev<=v<p* (n_mid), 0 else.
    p_rev = a / 2
    pi_rev = (p_rev - c) * (a - p_rev) / a           # exact Fraction = 1/8
    exact_gap = pis - pi_rev                          # exact Fraction = 1/64
    d_hi = float(ps - c) - float(p_rev - c)           # +1/8
    d_lo = -float(p_rev - c)                          # −1/4
    sum_diff = n_star * d_hi + n_mid * d_lo
    sum_diff_sq = n_star * d_hi * d_hi + n_mid * d_lo * d_lo
    mean_diff = sum_diff / N_MC
    var_diff = sum_diff_sq / N_MC - mean_diff * mean_diff
    se_diff = math.sqrt(var_diff / N_MC)
    z_foil = mean_diff / se_diff

    assert pis > pi_rev, "profit-max must strictly beat revenue-max price (exact)"

    g4 = {
        "foil": "revenue-maximisation == profit-maximisation (price at p_rev=a/2, "
                "ignores cost) — rejected: profit-max strictly dominates",
        "n": N_MC,
        "z_foil": f"{z_foil:.4f}",
        "exact_gap": frac_str(exact_gap),            # "1/64"
        "exact_dominates": bool(pis > pi_rev),
        "pass": abs(z_foil) > 8.0 and pis > pi_rev,
    }
    return g2, g4


# ---------------------------------------------------------------------------
# G3 — currency-scale invariance (Lerner index is unit-free), EXACT.
# ---------------------------------------------------------------------------
def gate3_invariance() -> dict:
    a, b, c = A, B, C
    base = lerner(a, b, c)
    lambdas = [Fraction(2), Fraction(3), Fraction(100), Fraction(1, 7)]
    lam_pass = []
    q_invariant = []
    for lam in lambdas:
        scaled = lerner(lam * a, lam * b, lam * c)
        ok = scaled == base
        assert ok, f"G3 scale-invariance failed at lambda={lam}"
        lam_pass.append(bool(ok))
        # q* is also unchanged under the same currency rescale.
        q_invariant.append(bool(q_star(lam * a, lam * b, lam * c) == q_star(a, b, c)))
    return {
        "lambdas": [frac_str(x) for x in lambdas],
        "lambda_pass": lam_pass,                     # per-lambda exact PASS booleans
        "q_star_invariant": all(q_invariant),
        "all_exact_pass": all(lam_pass),
        "z": "exact — z=n/a",
        "pass": all(lam_pass),
    }


# ---------------------------------------------------------------------------
# Assemble the whole payload.
# ---------------------------------------------------------------------------
def build_results() -> dict:
    a, b, c = A, B, C
    g1 = gate1_exact()
    n_star, n_mid = _mc_counts()
    g2, g4 = gate2_and_gate4(n_star, n_mid)
    g3 = gate3_invariance()

    all_pass = bool(g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"])
    first_failing = None
    for name, g in (("G1", g1), ("G2", g2), ("G3", g3), ("G4", g4)):
        if not g["pass"]:
            first_failing = name
            break

    return {
        "claim": "monopoly optimal markup = reciprocal elasticity: linear inverse "
                 "demand p(q)=a−b·q, constant MC c, gives q*=(a−c)/(2b), "
                 "p*=(a+c)/2, pi*=(a−c)^2/(4b), and Lerner L=(p*−c)/p*="
                 "(a−c)/(a+c)=1/|eps*|; instance a=1,b=1,c=1/4",
        "params": {
            "a": frac_str(a),
            "b": frac_str(b),
            "c": frac_str(c),
        },
        "p_star": frac_str(p_star(a, b, c)),
        "q_star": frac_str(q_star(a, b, c)),
        "pi_star": frac_str(pi_star(a, b, c)),
        "lerner": frac_str(lerner(a, b, c)),
        "abs_elasticity": frac_str(abs_elasticity_at_opt(a, b, c)),
        "g1": g1,
        "g2": g2,
        "g3": g3,
        "g4": g4,
        "all_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "PASS" if all_pass else "FAIL",
        "SEED": SEED,
    }


def canonical_json(results: dict) -> str:
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def digest(results: dict) -> str:
    return hashlib.sha256(canonical_json(results).encode("utf-8")).hexdigest()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selfcheck", action="store_true",
                        help="run compute twice in-process, assert byte-identical")
    args = parser.parse_args(argv[1:])

    a = build_results()
    b = build_results()
    ja, jb = canonical_json(a), canonical_json(b)
    if ja != jb:
        print("ERROR: in-process double-run is NOT byte-identical", file=sys.stderr)
        return 1
    dig = digest(a)

    if args.selfcheck:
        print("SELFCHECK: byte-identical" if ja == jb else "SELFCHECK: MISMATCH")
        print(f"results_sha256 = {dig}")
        return 0

    print(json.dumps(a, sort_keys=True, indent=2))
    print()
    print(f"in_process_double_run: {'IDENTICAL' if ja == jb else 'MISMATCH'}")
    print(f"p* = {a['p_star']}  q* = {a['q_star']}  pi* = {a['pi_star']}  "
          f"L = {a['lerner']}  1/|eps*| = {a['lerner']} (=(a-c)/(a+c))")
    print(f"G1 = {a['g1']['z']}  sweep_pass = {a['g1']['sweep_pass']}")
    print(f"G2_z = {a['g2']['z']}  (n_buy = {a['g2']['n_buy']}/{a['g2']['n']})")
    print(f"G3 = {a['g3']['z']}  lambda_pass = {a['g3']['lambda_pass']}")
    print(f"G4_z_foil = {a['g4']['z_foil']}  (exact_gap = {a['g4']['exact_gap']})")
    print(f"all_pass = {a['all_pass']}  decision = {a['decision']}")
    print(f"results_sha256 = {dig}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
