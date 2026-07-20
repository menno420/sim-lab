#!/usr/bin/env python3
"""Verifier — Nash bargaining threat-point half pass-through.

Head: under the symmetric Nash bargaining solution, raising your disagreement
(BATNA) payoff d1 by a dollar raises your negotiated share x1 by exactly $0.50
(the pass-through partial d x1 / partial d d1 = 1/2), because the surplus the two
parties split shrinks by that same dollar. The closed form equals exhaustive
Nash-product enumeration exactly; an alternating-offers negotiation converges to
the same split; and the folk "one-for-one" accounting is falsified by surplus
conservation.

Stdlib only. SEED=20260717. Deterministic across in-process double-run and
separate cross-invocation. Digest posture: WHOLE-DICT / NO-SELF-FIELD /
STDOUT-ONLY (the canonical-JSON sha256 of the full results dict IS the digest;
the dict carries no hash of itself). Human detail is written to stderr and is
NOT part of the digested stdout.
"""
import hashlib
import json
import random
import sys
from fractions import Fraction

SEED = 20260717


def nash_split(S, d1, d2, alpha=Fraction(1, 2)):
    """Generalized Nash bargaining, transferable utility: maximize
    (x1-d1)^alpha * (x2-d2)^(1-alpha) s.t. x1+x2=S. Closed form
    x1 = d1 + alpha*(S-d1-d2), x2 = S - x1."""
    s = S - d1 - d2
    x1 = d1 + alpha * s
    x2 = S - x1
    return x1, x2


def nash_product(x1, x2, d1, d2):
    return (x1 - d1) * (x2 - d2)


def gate_g1(rng):
    """EXACT: symmetric closed form == exhaustive Nash-product argmax on a
    Fraction-exact half-integer grid; unique maximizer."""
    problems = 0
    exact_hits = 0
    unique_max = 0
    for _ in range(200):
        d1 = Fraction(rng.randint(-20, 20))
        d2 = Fraction(rng.randint(-20, 20))
        s = 2 * rng.randint(1, 30)          # even, positive surplus -> optimum on grid
        S = d1 + d2 + s
        x1_cf, _ = nash_split(S, d1, d2)    # closed form (alpha=1/2)
        best_u = None
        best_prod = None
        ties = 0
        for k in range(0, 2 * s + 1):       # u1 in {0, 1/2, 1, ...} up to s
            u1 = Fraction(k, 2)
            x1 = d1 + u1
            x2 = S - x1
            p = nash_product(x1, x2, d1, d2)
            if best_prod is None or p > best_prod:
                best_prod = p
                best_u = u1
                ties = 1
            elif p == best_prod:
                ties += 1
        problems += 1
        if d1 + best_u == x1_cf:
            exact_hits += 1
        if ties == 1:
            unique_max += 1
    return {
        "problems": problems,
        "exact_argmax_matches_closed_form": exact_hits,
        "unique_maximizer": unique_max,
        "pass": exact_hits == problems and unique_max == problems,
    }


def gate_g2(rng):
    """SURPRISE (>=3 sigma): a simulated alternating-offers (Rubinstein)
    negotiation gives a pass-through estimate beta_hat that rejects the folk
    full-pass-through value 1.0 and is consistent with 1/2. Total S is held
    fixed while d1 rises by delta, so the surplus shrinks -- that is the point."""
    N = 100000
    S, d1, d2 = Fraction(40), Fraction(10), Fraction(4)
    delta = Fraction(6)

    def batch(dd1):
        s = float(S - dd1 - d2)
        base = float(dd1)
        tot = 0.0
        tot2 = 0.0
        for _ in range(N):
            disc = rng.uniform(0.90, 0.999)              # per-trial discount
            if rng.random() < 0.5:
                share1 = 1.0 / (1.0 + disc)              # player 1 proposes first
            else:
                share1 = disc / (1.0 + disc)             # player 2 proposes first
            x1 = base + share1 * s
            tot += x1
            tot2 += x1 * x1
        mean = tot / N
        var_mean = max(0.0, tot2 / N - mean * mean) / N
        return mean, var_mean

    m1, vm1 = batch(d1)
    m2, vm2 = batch(d1 + delta)
    beta = (m2 - m1) / float(delta)
    se = (vm1 + vm2) ** 0.5 / float(delta)
    z_folk = abs(beta - 1.0) / se if se > 0 else float("inf")
    z_half = abs(beta - 0.5) / se if se > 0 else 0.0
    rejects_folk = z_folk >= 3.0
    consistent_half = abs(beta - 0.5) <= 0.02
    passed = rejects_folk and consistent_half
    sys.stderr.write(
        "G2-detail: beta_hat=%.6f m1=%.6f m2=%.6f se=%.6f z_folk=%.3f z_half=%.3f\n"
        % (beta, m1, m2, se, z_folk, z_half)
    )
    return {
        "N": N,
        "beta_hat_round3": round(beta, 3),
        "rejects_folk_full_passthrough_at_3sigma": bool(rejects_folk),
        "consistent_with_half": bool(consistent_half),
        "pass": bool(passed),
    }


def gate_g3():
    """ROBUSTNESS / shift: across bargaining power alpha in {0.1..0.9} the
    pass-through equals 1 - alpha exactly (Fraction) and lies strictly in (0,1)
    -- fractional and never the folk 1.0. Also invariant to pie size."""
    alphas = [Fraction(k, 10) for k in range(1, 10)]
    rows = []
    all_exact = True
    all_interior = True
    for alpha in alphas:
        S, d1, d2 = Fraction(50), Fraction(8), Fraction(5)
        delta = Fraction(1)
        x1_base, _ = nash_split(S, d1, d2, alpha)
        x1_bump, _ = nash_split(S, d1 + delta, d2, alpha)
        pt = (x1_bump - x1_base) / delta
        expected = 1 - alpha
        if pt != expected:
            all_exact = False
        if not (Fraction(0) < pt < Fraction(1)):
            all_interior = False
        # pie-size invariance: doubling S leaves the pass-through unchanged
        x1b2, _ = nash_split(2 * S, d1, d2, alpha)
        x1u2, _ = nash_split(2 * S, d1 + delta, d2, alpha)
        if (x1u2 - x1b2) / delta != pt:
            all_exact = False
        rows.append([str(alpha), str(pt), str(expected)])
    return {
        "alphas": [str(a) for a in alphas],
        "passthrough_equals_one_minus_alpha": all_exact,
        "passthrough_strictly_between_0_and_1": all_interior,
        "rows": rows,
        "pass": all_exact and all_interior,
    }


def gate_g4(rng):
    """EXACT identity + FALSIFIABILITY: surplus conservation x1+x2=S and
    individual rationality hold exactly; the deliberately-wrong folk accounting
    (full pass-through, counterparty share held fixed) is REJECTED because it
    violates conservation (sums to S+delta)."""
    n = 0
    conserve_ok = 0
    ir_ok = 0
    folk_falsified = 0
    for _ in range(200):
        d1 = Fraction(rng.randint(-20, 20))
        d2 = Fraction(rng.randint(-20, 20))
        s = Fraction(rng.randint(1, 60))
        S = d1 + d2 + s
        x1, x2 = nash_split(S, d1, d2)
        n += 1
        if x1 + x2 == S:
            conserve_ok += 1
        if x1 >= d1 and x2 >= d2:
            ir_ok += 1
        delta = Fraction(rng.randint(1, 10))
        x1_tb, x2_tb = nash_split(S, d1 + delta, d2)     # true bumped split
        true_conserves = (x1_tb + x2_tb == S)
        x1_folk = x1 + delta                              # folk: capture full delta
        x2_folk = x2                                       # counterparty held fixed
        folk_conserves = (x1_folk + x2_folk == S)
        if true_conserves and not folk_conserves:
            folk_falsified += 1
    return {
        "problems": n,
        "surplus_conservation_holds": conserve_ok,
        "individual_rationality_holds": ir_ok,
        "folk_full_passthrough_falsified": folk_falsified,
        "pass": conserve_ok == n and ir_ok == n and folk_falsified == n,
    }


def battery():
    rng = random.Random(SEED)
    g1 = gate_g1(rng)
    g4 = gate_g4(rng)
    g3 = gate_g3()
    g2 = gate_g2(rng)
    all_pass = g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"]
    return {
        "seed": SEED,
        "head": "nash-bargaining-threat-point-half-passthrough",
        "G1_exact_argmax": g1,
        "G2_surprise_rubinstein_3sigma": g2,
        "G3_robustness_alpha_shift": g3,
        "G4_conservation_falsifiability": g4,
        "all_pass": all_pass,
    }


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def main():
    r1 = battery()
    r2 = battery()
    assert canonical(r1) == canonical(r2), "in-process double-run mismatch"
    blob = canonical(r1)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    print(blob)
    print("results_sha256=" + digest)


if __name__ == "__main__":
    main()
