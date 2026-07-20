#!/usr/bin/env python3
"""PROPOSAL 230 / VERDICT 243 (+13 offset) -- Myerson-Satterthwaite via the
Chatterjee-Samuelson k=1/2 bilateral double auction. Buyer value v and seller
cost c are independent Uniform[0,1]. The unique linear Bayes-Nash equilibrium is
buyer bid b(v)=(2/3)v+1/12 and seller ask s(c)=(2/3)c+1/4; trade occurs iff
b(v)>=s(c), which reduces EXACTLY to v-c>=1/4. The expected realized gains from
trade are exactly 9/64, versus the first-best (efficient) gains 1/6, so the
strategic mechanism captures exactly 27/32 of the achievable surplus and forgoes
a deadweight of exactly 5/192 -- the concrete signature of the Myerson-
Satterthwaite impossibility (no efficient, individually-rational, budget-balanced,
incentive-compatible mechanism exists for bilateral trade with these priors).

Pre-registered gate battery (each gate scored in its own direction):
  G1 EXACT EQUALITY (fractions.Fraction, RNG-free): exact rational integration of
     the surplus (v-c) over the equilibrium trade region reproduces realized
     gains 9/64, first-best 1/6, efficiency 27/32, deadweight 5/192, trade
     probability 9/32, and the trade threshold offset 1/4 derived from the
     parallel offer functions.
  G2 MC AGREEMENT (|z|<3): N draws of (v,c) under the equilibrium trading rule;
     the sample mean of realized gains agrees with 9/64 and the trade frequency
     agrees with 9/32.
  G3 INVARIANCE/ROBUSTNESS: (a) a grid best-response check confirms the closed-
     form buyer bid and seller ask are each the payoff-maximising deviation; (b)
     a second independent exact route (integrating over the difference density
     f_D(d)=1-d) reproduces 9/64.
  G4 FALSIFIABILITY (REJECTION |z|>6): on the SAME sample the efficient rule
     (trade iff v>=c) agrees with 1/6, while the equilibrium rule's realized
     gains REJECT the naive "the double auction is efficient (=1/6)" claim.

Determinism: SEED=20260717, stdlib only. build_results() is a pure function of
SEED and the module constants; a single random.Random(SEED) is consumed in a
fixed gate order. In-process double-run byte-identity is asserted (exit 3 on
divergence); separate re-invocation is byte-identical.
"""
import sys
import json
import math
import hashlib
import random
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0
Z_REJECT = 6.0
N_MC_MAIN = 200_000
BR_V_POINTS = (Fraction(2, 5), Fraction(3, 5), Fraction(7, 10), Fraction(9, 10))
BR_C_POINTS = (Fraction(1, 10), Fraction(3, 10), Fraction(1, 2), Fraction(7, 10))
BR_GRID_STEPS = 1000

# Linear-equilibrium offer functions (Chatterjee-Samuelson, uniform priors).
B_SLOPE = Fraction(2, 3)
B_INT = Fraction(1, 12)   # buyer bid  b(v)=2v/3+1/12
S_SLOPE = Fraction(2, 3)
S_INT = Fraction(1, 4)    # seller ask s(c)=2c/3+1/4


def poly_integral(coeffs, lo, hi):
    """Exact definite integral of sum(coeffs[k]*x**k) over [lo,hi], all Fraction."""
    total = Fraction(0)
    for k, a in enumerate(coeffs):
        total += a * (hi ** (k + 1) - lo ** (k + 1)) / (k + 1)
    return total


def zscore(p_hat, p, N):
    return (p_hat - p) / math.sqrt(p * (1.0 - p) / N)


def build_results():
    r = {"proposal": 230, "verdict": 243, "slot": "round-56 VENTURE", "seed": SEED,
         "z_gate": Z_GATE, "z_reject": Z_REJECT, "n_mc_main": N_MC_MAIN}

    # ----- Gate 1: exact rational integration (RNG-free) -----
    assert B_SLOPE == S_SLOPE  # parallel offers => constant trade threshold
    delta = (S_INT - B_INT) / B_SLOPE            # (1/4 - 1/12)/(2/3) = 1/4
    L = 1 - delta                                # upper limit of c for trade
    # realized gains = int_{c=0}^{L} ((1-c)^2 - delta^2)/2 dc
    # inner integrand in c: (1-delta^2)/2 - c + c^2/2
    inner = [(1 - delta * delta) / 2, Fraction(-1), Fraction(1, 2)]
    realized = poly_integral(inner, Fraction(0), L)
    fb_inner = [Fraction(1, 2), Fraction(-1), Fraction(1, 2)]  # delta=0 case
    first_best = poly_integral(fb_inner, Fraction(0), Fraction(1))
    trade_prob = L * L / 2
    efficiency = realized / first_best
    deadweight = first_best - realized
    g1_pass = (delta == Fraction(1, 4) and realized == Fraction(9, 64)
               and first_best == Fraction(1, 6) and efficiency == Fraction(27, 32)
               and deadweight == Fraction(5, 192) and trade_prob == Fraction(9, 32))
    r["gate1_exact_equality"] = {
        "direction": "EQUALITY (exact Fraction integration)",
        "delta": str(delta), "realized_gains": str(realized),
        "first_best": str(first_best), "efficiency_ratio": str(efficiency),
        "deadweight": str(deadweight), "trade_prob": str(trade_prob),
        "pass": bool(g1_pass)}

    # ----- Gate 2: Monte-Carlo agreement (shared sample, reused by G4) -----
    rng = random.Random(SEED)
    delta_f = float(delta)
    n = N_MC_MAIN
    eq_sum = 0.0
    eq_sqsum = 0.0
    eq_trades = 0
    eff_sum = 0.0
    eff_sqsum = 0.0
    for _ in range(n):
        v = rng.random()
        c = rng.random()
        d = v - c
        s_eq = d if d >= delta_f else 0.0
        eq_sum += s_eq
        eq_sqsum += s_eq * s_eq
        if d >= delta_f:
            eq_trades += 1
        s_eff = d if d >= 0.0 else 0.0
        eff_sum += s_eff
        eff_sqsum += s_eff * s_eff
    eq_mean = eq_sum / n
    eq_var = eq_sqsum / n - eq_mean * eq_mean
    eff_mean = eff_sum / n
    eff_var = eff_sqsum / n - eff_mean * eff_mean
    realized_f = float(realized)
    fb_f = float(first_best)
    tp_f = float(trade_prob)
    z_gains = (eq_mean - realized_f) / math.sqrt(eq_var / n)
    p_trade = eq_trades / n
    z_trade = zscore(p_trade, tp_f, n)
    g2_pass = abs(z_gains) < Z_GATE and abs(z_trade) < Z_GATE
    r["gate2_mc_agreement"] = {
        "direction": "AGREEMENT |z|<%.1f" % Z_GATE,
        "samples": n, "target_gains": round(realized_f, 8),
        "mean_gains": round(eq_mean, 6), "z_gains": round(z_gains, 6),
        "target_trade_prob": round(tp_f, 8), "p_hat_trade": round(p_trade, 6),
        "z_trade": round(z_trade, 6), "pass": bool(g2_pass)}

    # ----- Gate 3: invariance / robustness (RNG-free) -----
    def buyer_payoff(v, b):
        cm = (b - S_INT) / S_SLOPE
        if cm <= 0:
            return Fraction(0)
        if cm > 1:
            cm = Fraction(1)
        a0 = v - b / 2 - S_INT / 2
        a1 = -S_SLOPE / 2
        return poly_integral([a0, a1], Fraction(0), cm)

    def seller_payoff(c, a):
        vmn = (a - B_INT) / B_SLOPE
        if vmn >= 1:
            return Fraction(0)
        if vmn < 0:
            vmn = Fraction(0)
        a0 = a / 2 + B_INT / 2 - c
        a1 = B_SLOPE / 2
        return poly_integral([a0, a1], vmn, Fraction(1))

    grid = [Fraction(i, BR_GRID_STEPS) for i in range(BR_GRID_STEPS + 1)]
    buyer_ok = True
    buyer_detail = []
    for v in BR_V_POINTS:
        best = max(grid, key=lambda b: buyer_payoff(v, b))
        bstar = B_SLOPE * v + B_INT
        ok = abs(best - bstar) <= Fraction(1, BR_GRID_STEPS)
        buyer_ok = buyer_ok and ok
        buyer_detail.append({"v": str(v), "grid_argmax": str(best),
                             "closed_form": str(bstar), "pass": bool(ok)})
    seller_ok = True
    seller_detail = []
    for c in BR_C_POINTS:
        best = max(grid, key=lambda a: seller_payoff(c, a))
        sstar = S_SLOPE * c + S_INT
        ok = abs(best - sstar) <= Fraction(1, BR_GRID_STEPS)
        seller_ok = seller_ok and ok
        seller_detail.append({"c": str(c), "grid_argmax": str(best),
                              "closed_form": str(sstar), "pass": bool(ok)})
    route2 = poly_integral([Fraction(0), Fraction(1), Fraction(-1)], delta, Fraction(1))
    route2_ok = (route2 == realized)
    g3_pass = buyer_ok and seller_ok and route2_ok
    r["gate3_robustness"] = {
        "direction": "INVARIANCE best-response argmax == closed form AND second exact route agrees",
        "buyer_best_response": buyer_detail, "seller_best_response": seller_detail,
        "route2_difference_density": str(route2), "route2_matches": bool(route2_ok),
        "pass": bool(g3_pass)}

    # ----- Gate 4: falsifiability (uses the shared G2 sample) -----
    z_eff = (eff_mean - fb_f) / math.sqrt(eff_var / n)
    z_eq_vs_fb = (eq_mean - fb_f) / math.sqrt(eq_var / n)
    g4_pass = abs(z_eff) < Z_GATE and abs(z_eq_vs_fb) > Z_REJECT
    r["gate4_falsifiability"] = {
        "direction": "REJECTION |z|>%.1f (naive: the double auction is efficient => gains 1/6)" % Z_REJECT,
        "samples": n, "first_best_target": round(fb_f, 8),
        "efficient_rule_mean": round(eff_mean, 6), "z_efficient_vs_fb": round(z_eff, 6),
        "equilibrium_mean": round(eq_mean, 6), "z_equilibrium_vs_fb": round(z_eq_vs_fb, 6),
        "naive_rejected": bool(abs(z_eq_vs_fb) > Z_REJECT), "pass": bool(g4_pass)}

    gates = {"gate1": r["gate1_exact_equality"]["pass"],
             "gate2": r["gate2_mc_agreement"]["pass"],
             "gate3": r["gate3_robustness"]["pass"],
             "gate4": r["gate4_falsifiability"]["pass"]}
    r["gates"] = gates
    r["first_failing_gate"] = next((k for k, v in gates.items() if not v), None)
    r["all_pass"] = bool(all(gates.values()))
    return r


def canonical(r):
    return json.dumps(r, sort_keys=True, separators=(",", ":"))


def main():
    r1 = build_results()
    r2 = build_results()
    c1 = canonical(r1)
    c2 = canonical(r2)
    if c1 != c2:
        sys.stderr.write("NON-DETERMINISTIC: in-process double-run diverged\n")
        sys.exit(3)
    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    for k in ("gate1", "gate2", "gate3", "gate4"):
        print("%s: %s" % (k, "PASS" if r1["gates"][k] else "FAIL"))
    print("all_pass: %s" % r1["all_pass"])
    print("results_sha256: %s" % hashlib.sha256(c1.encode()).hexdigest())
    sys.exit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
