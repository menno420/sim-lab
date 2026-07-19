#!/usr/bin/env python3
"""The bullwhip effect: ordering to a base-stock target AMPLIFIES order
variance. Even when customer demand is i.i.d. and stationary, a rational
order-up-to policy that forecasts lead-time demand with a p-period moving
average makes the variance of orders placed upstream exceed the variance of
demand by exactly

    Var(Q)/Var(D) = 1 + 2L/p + 2L^2/p^2 ,

a factor that GROWS with the replenishment lead time L and SHRINKS with the
forecast window p. The swing a supplier sees is manufactured by the ordering
policy, not by the customers -- and it compounds up a multi-echelon chain.

Head claim (bullwhip amplification): with i.i.d. demand and an order-up-to
policy Q_t = D_{t-1} + (L/p) * (D_{t-1} - D_{t-1-p}), the order-to-demand
variance ratio equals 1 + 2L/p + 2L^2/p^2 -- strictly greater than 1 for any
L >= 1, distribution-free in the demand's shape.

Method. Draw an i.i.d. demand stream, run the order-up-to recursion, measure
Var(Q)/Var(D) after warmup. Over R independent replications:
  G1  the ratio exceeds 1 (z >= 3 vs the null "orders are as stable as
      demand", ratio = 1)                              -- amplification is real
  G2  the measured ratio matches the closed form 1 + 2L/p + 2L^2/p^2, i.e.
      the relative error stays below 0.05 (z >= 3 below the ceiling)
                                                        -- it is the policy's law
  G3  the same relative error stays below 0.05 under a SHIFTED, heavy-tailed
      demand distribution and a shifted (L, p) (z >= 3 below the ceiling)
                                                        -- distribution-free

Grounded in the bullwhip effect (J. Forrester 1961; H. Lee, V. Padmanabhan,
S. Whang, "The Bullwhip Effect in Supply Chains", Sloan Mgmt Review 1997) and
its closed form (F. Chen, Z. Drezner, J. Ryan, D. Simchi-Levi, "Quantifying
the Bullwhip Effect in a Simple Supply Chain", Management Science 46(3), 2000).
The everyday fleet-ops lesson: order variance seen by spare-parts suppliers is
made by the replenishment policy (lead time + forecast smoothing), not by the
fleet's true consumption -- shortening lead time or lengthening the forecast
window cuts it; "just reorder what you used" does not.

Posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. SEED pinned; two in-process
runs asserted identical; results dict plus its sha256 printed. Stdlib only.
"""

import hashlib
import json
import math
import random

SEED = 20260717

# --- base config: i.i.d. Normal demand ---
D_MEAN = 100.0
D_SD = 20.0
LEAD = 4        # replenishment lead time L
WINDOW = 8      # moving-average forecast window p
N_PER = 40000   # order periods per replication
WARMUP = 8000   # discarded warm-up periods
R_REPS = 30     # independent replications

# --- shifted (robustness) config: heavy-tailed demand + shifted (L, p) ---
LEAD_SHIFT = 6
WINDOW_SHIFT = 4

G_MAX_RELERR = 0.05   # measured ratio must match the closed form within this
SIGMA = 3.0


def formula_ratio(lead, window):
    """Chen-Drezner-Ryan-Simchi-Levi bullwhip ratio for i.i.d. demand."""
    r = lead / window
    return 1.0 + 2.0 * r + 2.0 * r * r


def demand_normal(rng, n):
    return [rng.gauss(D_MEAN, D_SD) for _ in range(n)]


def demand_heavy(rng, n):
    """Heavy-tailed demand (exponential), same mean -- a deliberately
    non-Normal shape to test distribution-freeness."""
    return [rng.expovariate(1.0 / D_MEAN) for _ in range(n)]


def pvar(xs):
    n = len(xs)
    m = sum(xs) / n
    return sum((x - m) ** 2 for x in xs) / n


def order_ratio(demand, lead, window):
    """Run the order-up-to recursion and return Var(Q)/Var(D) post-warmup.

    Order-up-to with a p-period moving-average forecast of one-period demand:
    the base-stock target moves by (L/p) * (D_{t-1} - D_{t-1-p}), so the order
    placed is Q_t = D_{t-1} + (L/p) * (D_{t-1} - D_{t-1-p}). The constant
    safety-stock term cancels between successive targets."""
    r = lead / window
    orders = []
    kept_d = []
    n = len(demand)
    for t in range(window + 1, n):
        q = demand[t - 1] + r * (demand[t - 1] - demand[t - 1 - window])
        if t >= WARMUP:
            orders.append(q)
            kept_d.append(demand[t - 1])
    var_q = pvar(orders)
    var_d = pvar(kept_d)
    return var_q / var_d if var_d > 0 else float("inf")


def zstat(vals, h0):
    n = len(vals)
    m = sum(vals) / n
    var = sum((v - m) ** 2 for v in vals) / (n - 1)
    sd = math.sqrt(var)
    if sd == 0.0:
        return m, sd, float("inf")
    return m, sd, (m - h0) / (sd / math.sqrt(n))


def run_config(base_seed, gen, lead, window):
    ratios = []
    relerrs = []
    target = formula_ratio(lead, window)
    for rep in range(R_REPS):
        rng = random.Random(base_seed + rep)
        d = gen(rng, N_PER)
        ratio = order_ratio(d, lead, window)
        ratios.append(ratio)
        relerrs.append(abs(ratio - target) / target)
    return ratios, relerrs, target


def rnd(x):
    return round(x, 6)


def mean(xs):
    return sum(xs) / len(xs)


def run():
    base_ratios, base_relerrs, base_target = run_config(
        SEED, demand_normal, LEAD, WINDOW)
    shift_ratios, shift_relerrs, shift_target = run_config(
        SEED + 100000, demand_heavy, LEAD_SHIFT, WINDOW_SHIFT)

    r_mean, r_sd, r_z = zstat(base_ratios, 1.0)
    g1 = r_mean > 1.0 and r_z >= SIGMA

    e_mean, e_sd, e_z_raw = zstat(base_relerrs, G_MAX_RELERR)
    e_z = -e_z_raw
    g2 = e_mean < G_MAX_RELERR and e_z >= SIGMA

    se_mean, se_sd, se_z_raw = zstat(shift_relerrs, G_MAX_RELERR)
    se_z = -se_z_raw
    g3 = se_mean < G_MAX_RELERR and se_z >= SIGMA

    all_pass = g1 and g2 and g3
    order = [("G1", g1), ("G2", g2), ("G3", g3)]
    first_fail = next((name for name, ok in order if not ok), None)

    results = {
        "seed": SEED,
        "n_per": N_PER,
        "warmup": WARMUP,
        "reps": R_REPS,
        "d_mean": D_MEAN,
        "d_sd": D_SD,
        "lead": LEAD,
        "window": WINDOW,
        "formula_ratio_base": rnd(base_target),
        "ratio_mean": rnd(r_mean),
        "ratio_z": rnd(r_z),
        "relerr_mean": rnd(e_mean),
        "relerr_z": rnd(e_z),
        "shift_lead": LEAD_SHIFT,
        "shift_window": WINDOW_SHIFT,
        "formula_ratio_shift": rnd(shift_target),
        "shift_ratio_mean": rnd(mean(shift_ratios)),
        "shift_relerr_mean": rnd(se_mean),
        "shift_relerr_z": rnd(se_z),
        "g1_amplification_real": g1,
        "g2_matches_formula": g2,
        "g3_distribution_free": g3,
        "all_pass": all_pass,
        "first_failing_gate": first_fail,
    }
    return results


def main():
    results = run()
    again = run()
    assert results == again, "non-deterministic: in-process double run diverged"

    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    print("Bullwhip effect verifier -- order-up-to policy, i.i.d. demand, common seed")
    print(f"  base  : L={results['lead']} p={results['window']}  formula ratio={results['formula_ratio_base']:.6f}  measured={results['ratio_mean']:.6f}")
    print(f"  shift : L={results['shift_lead']} p={results['shift_window']}  formula ratio={results['formula_ratio_shift']:.6f}  measured={results['shift_ratio_mean']:.6f}")
    print(f"  G1 ratio_mean={results['ratio_mean']:.6f}  z={results['ratio_z']:+.6f}  (null ratio=1)")
    print(f"  G2 relerr_mean={results['relerr_mean']:.6f}  z={results['relerr_z']:+.6f}  (ceiling 0.05)")
    print(f"  G3 shift_relerr_mean={results['shift_relerr_mean']:.6f}  z={results['shift_relerr_z']:+.6f}  (ceiling 0.05)")
    print(f"  gates : G1={results['g1_amplification_real']}  G2={results['g2_matches_formula']}  G3={results['g3_distribution_free']}  all_pass={results['all_pass']}")
    print()
    print(json.dumps(results, indent=2, sort_keys=True))
    print(f"Results-JSON sha256: {digest}")
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
