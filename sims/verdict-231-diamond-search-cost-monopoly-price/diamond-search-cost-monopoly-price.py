#!/usr/bin/env python3
"""Verifier — Diamond paradox: a positive search cost makes the unique
equilibrium price the full monopoly price, for any number of sellers.

Head: with N identical sellers (marginal cost 0) selling to unit-value buyers
who must pay a strictly positive cost s to inspect each additional price, the
unique symmetric price equilibrium is p* = v (the buyer's reservation value =
the monopoly price) -- for EVERY N and every s > 0. Adding competitors does not
lower the price at all; the Bertrand march to marginal cost never starts. At
s = 0 exactly the market collapses to Bertrand (competitive price), so the
monopoly outcome is a discontinuity at zero friction.

Stdlib only. SEED=20260717. Deterministic across in-process double-run and a
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


def deviant_demand(pj, p_bg, N, s, v):
    """Expected demand (a Fraction of the unit buyer mass) for one seller pricing
    at pj when every other seller prices at the background p_bg. Marginal cost 0;
    buyers hold rational expectations that all sellers charge p_bg and each extra
    price inspection costs s.

    s > 0 (captive market): a buyer's free first sample is uniform over the N
    sellers. A buyer landing on this seller keeps buying here iff walking away
    (expected price p_bg, paid search cost s) is no better -- pj <= min(v,
    p_bg + s) -- and refuses above v (surplus < 0). Buyers who land elsewhere
    never search (they expect a uniform price and s > 0), so this seller captures
    none of them. Demand is exactly its 1/N first-visit share when
    pj <= min(v, p_bg + s), else 0.

    s == 0 (full information / Bertrand): search is free, so every buyer observes
    all prices and buys from a lowest-price seller (ties split), as long as that
    price <= v.
    """
    if s > 0:
        if pj <= min(v, p_bg + s):
            return Fraction(1, N)
        return Fraction(0)
    if pj > v:
        return Fraction(0)
    if pj < p_bg:
        return Fraction(1, 1)
    if pj == p_bg:
        return Fraction(1, N)
    return Fraction(0)


def best_response(p_bg, N, s, v, grid):
    """(best_price, best_profit) for one seller against background p_bg. Ties
    break toward the LOWEST price (conservative: never manufactures the result by
    preferring high prices)."""
    best_price = None
    best_profit = None
    for pj in grid:
        profit = pj * deviant_demand(pj, p_bg, N, s, v)
        if best_profit is None or profit > best_profit:
            best_profit = profit
            best_price = pj
    return best_price, best_profit


def is_symmetric_equilibrium(p, N, s, v, grid):
    """Symmetric profile at price p is Nash iff no seller has a strictly
    profitable unilateral deviation: p attains the best-response profit."""
    own_profit = p * deviant_demand(p, p, N, s, v)
    _, best_profit = best_response(p, N, s, v, grid)
    return own_profit == best_profit


def symmetric_equilibria(N, s, v, grid):
    return [p for p in grid if is_symmetric_equilibrium(p, N, s, v, grid)]


def gate_g1(rng):
    """EXACT: over a grid of (N, s>0, v), the closed-form prediction p* = v is the
    UNIQUE symmetric price equilibrium found by exhaustive best-response
    enumeration (Fraction-exact). Direction: unique-equilibrium-equals-v on 100%
    of problems."""
    problems = 0
    unique_eq_at_v = 0
    for _ in range(200):
        v = rng.randint(3, 20)
        N = rng.randint(2, 8)
        s = Fraction(rng.randint(1, v - 1))
        grid = [Fraction(k) for k in range(0, v + 1)]
        eqs = symmetric_equilibria(N, s, v, grid)
        problems += 1
        if eqs == [Fraction(v)]:
            unique_eq_at_v += 1
    return {
        "problems": problems,
        "unique_equilibrium_equals_monopoly_price_v": unique_eq_at_v,
        "pass": unique_eq_at_v == problems,
    }


def gate_g2(rng):
    """SURPRISE (>=3 sigma): across many random markets with genuine competition
    (N >= 2) and a small positive search cost, the equilibrium price -- solved by
    best-response enumeration, not assumed -- rejects the folk 'Bertrand'
    prediction that competition drives price to marginal cost (0) at z >= 3, and
    equals the monopoly price v in every market. Variance comes from random
    valuations. Direction: z_reject_folk high; per-market price == v exact."""
    M = 3000
    prices = []
    matches_v = 0
    for _ in range(M):
        v = rng.randint(2, 40)
        N = rng.randint(2, 400)
        s = Fraction(rng.randint(1, max(1, v // 4)))
        grid = [Fraction(k) for k in range(0, v + 1)]
        eqs = symmetric_equilibria(N, s, v, grid)
        assert len(eqs) == 1
        p_eq = eqs[0]
        prices.append(float(p_eq))
        if p_eq == Fraction(v):
            matches_v += 1
    mean = sum(prices) / M
    var = sum((x - mean) ** 2 for x in prices) / M
    se = (var / M) ** 0.5
    z_reject_folk = abs(mean - 0.0) / se if se > 0 else float("inf")
    sys.stderr.write(
        "G2-detail: mean_price=%.6f se=%.6f z_reject_folk=%.3f\n"
        % (mean, se, z_reject_folk)
    )
    return {
        "M": M,
        "mean_equilibrium_price_round3": round(mean, 3),
        "z_reject_folk_marginal_cost_round3": round(z_reject_folk, 3),
        "rejects_folk_at_3sigma": bool(z_reject_folk >= 3.0),
        "price_equals_monopoly_v_all_markets": bool(matches_v == M),
        "pass": bool(z_reject_folk >= 3.0 and matches_v == M),
    }


def gate_g3(rng):
    """ROBUSTNESS / shift + discontinuity: the equilibrium price is invariant to N
    and to every positive search cost s (always = v); and the monopoly price v is
    a symmetric equilibrium IFF s > 0 (at s = 0, full-information Bertrand
    undercutting destroys it). Direction: invariance on 100%; iff-s-positive on
    100%."""
    n = 0
    invariant = 0
    discontinuity = 0
    for _ in range(120):
        v = rng.randint(3, 15)
        grid = [Fraction(k) for k in range(0, v + 1)]
        ok_inv = True
        for N in (2, 3, 5, 10):
            for s in (Fraction(1), Fraction(2), Fraction(v - 1)):
                if symmetric_equilibria(N, s, v, grid) != [Fraction(v)]:
                    ok_inv = False
        n += 1
        if ok_inv:
            invariant += 1
        v_is_eq_pos = is_symmetric_equilibrium(Fraction(v), 5, Fraction(1), v, grid)
        v_is_eq_zero = is_symmetric_equilibrium(Fraction(v), 5, Fraction(0), v, grid)
        if v_is_eq_pos and not v_is_eq_zero:
            discontinuity += 1
    return {
        "problems": n,
        "equilibrium_invariant_to_N_and_positive_s_equals_v": invariant,
        "monopoly_price_is_equilibrium_iff_s_positive": discontinuity,
        "pass": invariant == n and discontinuity == n,
    }


def gate_g4(rng):
    """EXACT identity + FALSIFIABILITY: at the s>0 equilibrium each of the N
    sellers earns v/N and industry profit == v (the monopoly profit), invariant
    to N; and the folk Bertrand profile (every seller at marginal cost 0) is NOT a
    Nash equilibrium under s>0 -- a unilateral upward deviation is strictly
    profitable -- so the 'competition drives price to marginal cost' accounting is
    falsified. Direction: industry==v on 100%; folk falsified on 100%; true
    profile deviation-free on 100%."""
    n = 0
    industry_is_monopoly = 0
    folk_falsified = 0
    true_no_deviation = 0
    for _ in range(200):
        v = rng.randint(3, 20)
        N = rng.randint(2, 8)
        s = Fraction(rng.randint(1, v - 1))
        grid = [Fraction(k) for k in range(0, v + 1)]
        per_seller = Fraction(v) * deviant_demand(Fraction(v), Fraction(v), N, s, v)
        industry = N * per_seller
        n += 1
        if industry == Fraction(v) and per_seller == Fraction(v, N):
            industry_is_monopoly += 1
        folk_bg = Fraction(0)
        folk_own = folk_bg * deviant_demand(folk_bg, folk_bg, N, s, v)
        _, folk_best = best_response(folk_bg, N, s, v, grid)
        if folk_best > folk_own:
            folk_falsified += 1
        true_own = Fraction(v) * deviant_demand(Fraction(v), Fraction(v), N, s, v)
        _, true_best = best_response(Fraction(v), N, s, v, grid)
        if true_best == true_own:
            true_no_deviation += 1
    return {
        "problems": n,
        "industry_profit_equals_monopoly_v": industry_is_monopoly,
        "folk_bertrand_profile_falsified": folk_falsified,
        "true_monopoly_profile_no_profitable_deviation": true_no_deviation,
        "pass": (industry_is_monopoly == n and folk_falsified == n
                 and true_no_deviation == n),
    }


def battery():
    rng = random.Random(SEED)
    g1 = gate_g1(rng)
    g2 = gate_g2(rng)
    g3 = gate_g3(rng)
    g4 = gate_g4(rng)
    all_pass = g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"]
    return {
        "seed": SEED,
        "head": "diamond-paradox-positive-search-cost-monopoly-price",
        "G1_exact_unique_equilibrium": g1,
        "G2_surprise_reject_marginal_cost_3sigma": g2,
        "G3_robustness_invariance_and_discontinuity": g3,
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
