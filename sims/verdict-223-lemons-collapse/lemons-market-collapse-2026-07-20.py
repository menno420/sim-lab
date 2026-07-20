#!/usr/bin/env python3
"""Akerlof lemons market collapse: a market in which EVERY possible trade
strictly benefits both buyer and seller can still collapse to a vanishing
fraction of its potential volume -- quality uncertainty alone, with no
transaction cost and no irrationality, destroys nearly all the gains from trade.

Discrete exact Akerlof "Market for Lemons" instantiation:
- Quality grid Q = {1,...,N}, uniform prior.
- Seller reservation for quality q = q (won't sell below own value).
- Buyer valuation for quality q = beta*q, with 1 < beta < 2 (Fraction).
  Every trade is mutually beneficial since beta*q > q for all q > 0.
- At integer price p, offered set S(p) = {q in Q : q <= p}. Rational competitive
  buyers pay p iff p <= beta*E[q | q in S(p)]. With the uniform grid,
  E[q | S(p)] = (p+1)/2 for 1 <= p <= N.
- Equilibrium max trading price p*(beta,N) = max{ p in {0..N} : p <= beta*(p+1)/2 }.
  Cars with q <= p* trade; q > p* do not.
- Closed form: p <= beta*(p+1)/2  <=>  p(2-beta) <= beta  <=>  p <= beta/(2-beta),
  so p*_closed = min(N, floor(beta/(2-beta))) with EXACT Fraction floor.
- Potential gains-from-trade: GFT_pot = (beta-1)*N(N+1)/2.
- Realized gains-from-trade: GFT_real = (beta-1)*p*(p*+1)/2.
- Destroyed fraction D(beta,N) = 1 - p*(p*+1)/(N(N+1)).

Stdlib only (hashlib, json, math, random, fractions). Deterministic: SEED pinned;
a fresh random.Random(SEED) is created at the start of EACH full run, so both an
in-process double-run and a separate cross-invocation reproduce byte-identical
output.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY -- the compact-canonical
results dict's own sha256 IS the digest; it is not a field inside the dict.
"""
import hashlib
import json
import math
import random
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0
M_MC = 200_000            # Monte-Carlo draws (G2)
ROUND_DP = 10            # fixed serialization precision for byte-stable floats

# (beta, N) batteries (sorted deterministically).
BETA_BATTERY = [
    Fraction(11, 10), Fraction(5, 4), Fraction(4, 3), Fraction(3, 2),
    Fraction(5, 3), Fraction(7, 4), Fraction(9, 5), Fraction(19, 10),
]
N_BATTERY = [50, 100, 500, 1000, 5000]

# Pinned world.
PIN_BETA = Fraction(3, 2)
PIN_N = 1000


def fr(x):
    """Serialize a Fraction as the canonical 'num/den' string."""
    return "%d/%d" % (x.numerator, x.denominator)


def p_star_closed(beta, N):
    """Closed form p* = min(N, floor(beta/(2-beta))), exact Fraction floor."""
    r = beta / (2 - beta)                 # exact Fraction, positive since beta < 2
    fl = r.numerator // r.denominator     # exact floor for positive rational
    return min(N, fl)


def willing(beta, p):
    """Exact rational test: is integer price p supported? p <= beta*(p+1)/2."""
    return Fraction(p) <= beta * Fraction(p + 1, 2)


def p_star_scan(beta, N):
    """Exhaustive scan p=0..N: max p passing the exact willingness test."""
    best = 0
    for p in range(N + 1):
        if willing(beta, p):
            best = p
    return best


def sum_1_to(m):
    """Explicit exact integer sum 1+2+...+m (m>=0)."""
    total = 0
    for q in range(1, m + 1):
        total += q
    return total


def destroyed_closed(beta, N):
    """D(beta,N) = 1 - p*(p*+1)/(N(N+1)) via the closed p* and closed ratio."""
    ps = p_star_closed(beta, N)
    return 1 - Fraction(ps * (ps + 1), N * (N + 1))


def destroyed_measured(beta, N):
    """D via realized/potential GFT with the (beta-1) factor carried explicitly,
    p* from the closed form, GFT sums from explicit summation."""
    ps = p_star_closed(beta, N)
    gft_real = (beta - 1) * Fraction(sum_1_to(ps))
    gft_pot = (beta - 1) * Fraction(sum_1_to(N))
    return 1 - gft_real / gft_pot


def gate_g1():
    """EXACT (direction: exact agreement, expect discrepancies=0): closed-form
    p*_closed == exhaustive-scan p*_scan over the whole (beta,N) battery."""
    discrepancies = 0
    table = {}
    for beta in BETA_BATTERY:
        row = {}
        for N in N_BATTERY:
            pc = p_star_closed(beta, N)
            psn = p_star_scan(beta, N)
            if pc != psn:
                discrepancies += 1
            row[str(N)] = {"p_star_closed": pc, "p_star_scan": psn}
        table[fr(beta)] = row
    ok = (discrepancies == 0)
    return ok, {
        "direction": "exact-agreement-expect-0-discrepancies",
        "discrepancies": discrepancies,
        "p_star_table": table,
    }


def gate_g2(rng):
    """SURPRISE (direction: HIGH z, gate z>=3.0): Monte-Carlo on the pinned world.
    Full-info trade always happens (rate 1); asymmetric-info trade happens iff
    q <= p*. r_hat = realized-trade rate. H0 strawman: >= half the market
    survives (rate 0.5). z = (0.5 - r_hat)/se."""
    beta, N = PIN_BETA, PIN_N
    ps = p_star_closed(beta, N)
    hits = 0
    for _ in range(M_MC):
        q = rng.randint(1, N)             # q uniform on {1..N}
        if q <= ps:
            hits += 1
    r_hat = hits / M_MC
    if r_hat <= 0.0:
        se = 1.0 / M_MC                   # guard degenerate r_hat=0
    else:
        se = math.sqrt(r_hat * (1.0 - r_hat) / M_MC)
    z = (0.5 - r_hat) / se
    predicted_rate = Fraction(ps, N)      # exact p*/N
    ok = (z >= Z_GATE)
    return ok, {
        "direction": "high-z-gate>=3.0",
        "beta": fr(beta),
        "N": N,
        "p_star": ps,
        "M": M_MC,
        "hits": hits,
        "r_hat": round(r_hat, ROUND_DP),
        "predicted_rate_exact": fr(predicted_rate),
        "predicted_rate": round(float(predicted_rate), ROUND_DP),
        "H0_survival_rate": 0.5,
        "se": round(se, ROUND_DP),
        "z": round(z, ROUND_DP),
    }


def gate_g3():
    """ROBUSTNESS/SHIFT (direction: persistence; monotone + near-total collapse):
    (i) for each beta, D weakly increasing in N; (ii) exact residual
    |D_measured - D_closed| == 0 everywhere; (iii) min over all beta of
    D(beta,N=5000) >= 0.99."""
    monotone_ok = True
    residual_discrepancies = 0
    d_table = {}
    min_d = None
    min_corner = None
    for beta in BETA_BATTERY:
        row = {}
        prev = None
        for N in N_BATTERY:
            d_closed = destroyed_closed(beta, N)
            d_meas = destroyed_measured(beta, N)
            if d_meas != d_closed:
                residual_discrepancies += 1
            if prev is not None and d_closed < prev:
                monotone_ok = False
            prev = d_closed
            row[str(N)] = fr(d_closed)
            if N == 5000:
                if min_d is None or d_closed < min_d:
                    min_d = d_closed
                    min_corner = {"beta": fr(beta), "N": N}
        d_table[fr(beta)] = row
    collapse_ok = (min_d is not None and min_d >= Fraction(99, 100))
    ok = monotone_ok and (residual_discrepancies == 0) and collapse_ok
    return ok, {
        "direction": "persistence-monotone+near-total-collapse-residual-0",
        "monotone_weakly_increasing_in_N": monotone_ok,
        "residual_discrepancies": residual_discrepancies,
        "min_D_at_N5000_exact": fr(min_d),
        "min_D_at_N5000": round(float(min_d), ROUND_DP),
        "min_D_corner": min_corner,
        "collapse_min_ge_0_99": collapse_ok,
        "D_table": d_table,
    }


def gate_g4():
    """EXACT identity (direction: exact, expect discrepancies=0): across the
    battery, D closed form == 1 - (explicit sum_{q<=p*} q)/(explicit sum_{q<=N} q)."""
    discrepancies = 0
    for beta in BETA_BATTERY:
        for N in N_BATTERY:
            ps = p_star_closed(beta, N)
            d_closed = 1 - Fraction(ps * (ps + 1), N * (N + 1))
            d_ident = 1 - Fraction(sum_1_to(ps), sum_1_to(N))
            if d_closed != d_ident:
                discrepancies += 1
    ok = (discrepancies == 0)
    return ok, {
        "direction": "exact-expect-0-discrepancies",
        "discrepancies": discrepancies,
    }


def compute():
    # Fresh RNG per full run: reproducible in-process AND cross-invocation.
    rng = random.Random(SEED)

    g1_ok, g1 = gate_g1()
    g2_ok, g2 = gate_g2(rng)
    g3_ok, g3 = gate_g3()
    g4_ok, g4 = gate_g4()

    all_pass = g1_ok and g2_ok and g3_ok and g4_ok
    first_failing = None
    for gname, gok in (("G1", g1_ok), ("G2", g2_ok), ("G3", g3_ok), ("G4", g4_ok)):
        if not gok:
            first_failing = gname
            break

    pin_ps = p_star_closed(PIN_BETA, PIN_N)
    pin_d = destroyed_closed(PIN_BETA, PIN_N)

    return {
        "head": "lemons-market-collapse",
        "seed": SEED,
        "constants": {
            "z_gate": Z_GATE,
            "M_mc": M_MC,
            "beta_battery": [fr(b) for b in BETA_BATTERY],
            "N_battery": list(N_BATTERY),
        },
        "pinned_world": {
            "beta": fr(PIN_BETA),
            "N": PIN_N,
            "p_star": pin_ps,
            "predicted_trade_rate_exact": fr(Fraction(pin_ps, PIN_N)),
            "predicted_trade_rate": round(float(Fraction(pin_ps, PIN_N)), ROUND_DP),
            "destroyed_fraction_exact": fr(pin_d),
            "destroyed_fraction": round(float(pin_d), ROUND_DP),
        },
        "g1_exact_p_star": g1,
        "g2_surprise_montecarlo": g2,
        "g3_robustness_shift": g3,
        "g4_exact_identity": g4,
        "gates": {
            "G1_exact_p_star": g1_ok,
            "G2_surprise_3sigma": g2_ok,
            "G3_robustness_shift": g3_ok,
            "G4_exact_identity": g4_ok,
        },
        "first_failing_gate": first_failing,
        "all_pass": all_pass,
    }


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r1 = compute()
    r2 = compute()
    assert canonical(r1) == canonical(r2), "non-deterministic: double-run diverged"
    digest = hashlib.sha256(canonical(r1).encode("utf-8")).hexdigest()
    print(json.dumps(r1, indent=2))
    print("double_run_identical=true")
    print("all_pass=%s" % ("true" if r1["all_pass"] else "false"))
    g2 = r1["g2_surprise_montecarlo"]
    print("G2_z=%s" % g2["z"])
    print("G2_r_hat=%s" % g2["r_hat"])
    print("pinned_p_star=%s" % r1["pinned_world"]["p_star"])
    print("pinned_destroyed_fraction=%s" % r1["pinned_world"]["destroyed_fraction"])
    print("RESULTS_SHA256=%s" % digest)
    return 0 if r1["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
