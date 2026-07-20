#!/usr/bin/env python3
"""Vickrey second-price auction: truthful bidding is a weakly dominant strategy.

Firsthand deterministic reference simulation (stdlib-only) for PROPOSAL 199.
SEED = 20260717.

Gate battery (each direction stated):
  G1  EXHAUSTIVE weak dominance (integer-exact, wants 0 mismatches): over EVERY
      opponent bid profile and every focal value on a discrete grid, the
      truthful bid b = v weakly dominates every alternative bid in a Vickrey
      auction -> zero strictly-profitable deviations, truthful optimal on 100%
      of profiles, and non-vacuous (truthful strictly beats some lie).
  G2  EXACT-EXPECTATION contrast (Fraction-exact closed-form, wants sign match):
      over the full value grid, E[shade-truthful] > 0 in first-price but <= 0 in
      Vickrey, and E[truthful first-price surplus] == 0 EXACTLY (closed form).
  G3  MONTE-CARLO surprise (wants high z for first-price, z<=0 for Vickrey):
      against truthful rivals, the symmetric first-price shade v*(n-1)/n STRICTLY
      helps in first-price (z >= 3 sigma) but never helps in Vickrey (z <= 0).
  G4  ROBUSTNESS / shift (wants 0 mismatches): G1 dominance holds under shifted
      grids (n, ranges) and the G3 contrast persists under a shifted value range.
Determinism: in-process double-run must be byte-identical (guarded).
"""
import hashlib
import json
import math
import sys
from fractions import Fraction
from itertools import product
import random

SEED = 20260717
Z_GATE = 3.0


def vickrey_utility(focal_bid, focal_value, opp_bids):
    """Second-price: focal (index 0, wins ties) pays the highest opponent bid."""
    max_opp = max(opp_bids)
    if focal_bid >= max_opp:
        return focal_value - max_opp
    return 0


def first_price_utility(focal_bid, focal_value, opp_bids):
    """First-price: focal (index 0, wins ties) pays its own bid."""
    max_opp = max(opp_bids)
    if focal_bid >= max_opp:
        return focal_value - focal_bid
    return 0


def shade_bid(value, n):
    """Symmetric first-price equilibrium shade for uniform values: v*(n-1)/n."""
    return (value * (n - 1)) // n


def g1_dominance(n, val_max, bid_max):
    num_opp = n - 1
    dev_strict = 0
    truthful_strict = 0
    profiles = 0
    truthful_optimal = 0
    for v in range(val_max + 1):
        for opp in product(range(bid_max + 1), repeat=num_opp):
            profiles += 1
            u_true = vickrey_utility(v, v, opp)
            best_other = None
            for b in range(bid_max + 1):
                u_b = vickrey_utility(b, v, opp)
                if u_b > u_true:
                    dev_strict += 1
                if u_true > u_b:
                    truthful_strict += 1
                if best_other is None or u_b > best_other:
                    best_other = u_b
            if u_true >= best_other:
                truthful_optimal += 1
    return {
        "config": {"n": n, "val_max": val_max, "bid_max": bid_max},
        "profiles": profiles,
        "deviations_strictly_better": dev_strict,
        "truthful_strictly_better_instances": truthful_strict,
        "profiles_truthful_optimal": truthful_optimal,
        "profiles_truthful_optimal_frac": round(truthful_optimal / profiles, 6),
    }


def g2_exact_expectation(n, val_max):
    num = (val_max + 1) ** n
    tot_fp = Fraction(0)
    tot_vk = Fraction(0)
    tot_truthful_fp = Fraction(0)
    for prof in product(range(val_max + 1), repeat=n):
        v = prof[0]
        opp = prof[1:]
        s = shade_bid(v, n)
        d_fp = first_price_utility(s, v, opp) - first_price_utility(v, v, opp)
        d_vk = vickrey_utility(s, v, opp) - vickrey_utility(v, v, opp)
        tot_fp += Fraction(d_fp)
        tot_vk += Fraction(d_vk)
        tot_truthful_fp += Fraction(first_price_utility(v, v, opp))
    E_fp = tot_fp / num
    E_vk = tot_vk / num
    E_tf = tot_truthful_fp / num
    return {
        "config": {"n": n, "val_max": val_max, "profiles": num},
        "E_delta_firstprice": [E_fp.numerator, E_fp.denominator],
        "E_delta_firstprice_float": round(float(E_fp), 6),
        "E_delta_vickrey": [E_vk.numerator, E_vk.denominator],
        "E_delta_vickrey_float": round(float(E_vk), 6),
        "E_truthful_firstprice_surplus": [E_tf.numerator, E_tf.denominator],
        "E_truthful_firstprice_surplus_float": round(float(E_tf), 6),
    }


def g3_montecarlo(n, val_max, draws, seed):
    rng = random.Random(seed)

    def zstat(sum_, sumsq, k):
        mean = sum_ / k
        var = sumsq / k - mean * mean
        if var < 0:
            var = 0.0
        sd = math.sqrt(var)
        if sd == 0.0:
            return mean, sd, 0.0
        return mean, sd, mean / (sd / math.sqrt(k))

    s_fp = ss_fp = 0.0
    s_vk = ss_vk = 0.0
    for _ in range(draws):
        v = rng.randint(0, val_max)
        opp = [rng.randint(0, val_max) for _ in range(n - 1)]
        s = shade_bid(v, n)
        d_fp = first_price_utility(s, v, opp) - first_price_utility(v, v, opp)
        d_vk = vickrey_utility(s, v, opp) - vickrey_utility(v, v, opp)
        s_fp += d_fp
        ss_fp += d_fp * d_fp
        s_vk += d_vk
        ss_vk += d_vk * d_vk
    m_fp, sd_fp, z_fp = zstat(s_fp, ss_fp, draws)
    m_vk, sd_vk, z_vk = zstat(s_vk, ss_vk, draws)
    return {
        "config": {"n": n, "val_max": val_max, "draws": draws, "seed": seed},
        "mean_delta_firstprice": round(m_fp, 6),
        "z_firstprice": round(z_fp, 6),
        "mean_delta_vickrey": round(m_vk, 6),
        "z_vickrey": round(z_vk, 6),
    }


def build_results():
    g1 = g1_dominance(3, 4, 6)
    g2 = g2_exact_expectation(3, 6)
    g3 = g3_montecarlo(3, 12, 200000, SEED)
    g1_shift_a = g1_dominance(2, 6, 8)
    g1_shift_b = g1_dominance(4, 3, 5)
    g3_shift = g3_montecarlo(4, 20, 200000, SEED)

    gates = {}
    gates["G1_exhaustive_dominance"] = bool(
        g1["deviations_strictly_better"] == 0
        and g1["profiles_truthful_optimal"] == g1["profiles"]
        and g1["truthful_strictly_better_instances"] > 0
    )
    E_fp = Fraction(*g2["E_delta_firstprice"])
    E_vk = Fraction(*g2["E_delta_vickrey"])
    E_tf = Fraction(*g2["E_truthful_firstprice_surplus"])
    gates["G2_exact_expectation_contrast"] = bool(E_fp > 0 and E_vk <= 0 and E_tf == 0)
    gates["G3_montecarlo_surprise"] = bool(
        g3["z_firstprice"] >= Z_GATE and g3["z_vickrey"] <= 0.0
    )
    gates["G4_robustness_shift"] = bool(
        g1_shift_a["deviations_strictly_better"] == 0
        and g1_shift_a["profiles_truthful_optimal"] == g1_shift_a["profiles"]
        and g1_shift_b["deviations_strictly_better"] == 0
        and g1_shift_b["profiles_truthful_optimal"] == g1_shift_b["profiles"]
        and g3_shift["z_firstprice"] >= Z_GATE
        and g3_shift["z_vickrey"] <= 0.0
    )
    all_pass = all(gates.values())
    return {
        "seed": SEED,
        "z_gate": Z_GATE,
        "g1_dominance": g1,
        "g2_exact_expectation": g2,
        "g3_montecarlo": g3,
        "g1_shift_a": g1_shift_a,
        "g1_shift_b": g1_shift_b,
        "g3_shift": g3_shift,
        "gates": gates,
        "all_pass": bool(all_pass),
    }


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def main():
    results = build_results()
    results_2 = build_results()
    payload = canonical(results)
    if canonical(results_2) != payload:
        print("NON-DETERMINISTIC: in-process double-run diverged", file=sys.stderr)
        sys.exit(3)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    print(json.dumps(results, sort_keys=True, indent=2))
    print()
    for name, ok in sorted(results["gates"].items()):
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
    print(f"all_pass: {results['all_pass']}")
    print(f"results_sha256: {digest}")
    sys.exit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
