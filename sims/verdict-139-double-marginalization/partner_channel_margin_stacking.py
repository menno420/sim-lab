#!/usr/bin/env python3
"""PROPOSAL 126 - Partner-channel margin stacking (double marginalization).

VENTURE-domain mechanism (round-29 venture slot). Go-to-market / channel
economics: selling through an independent margin-setting partner.

Trap / counterintuitive result
------------------------------
The folk model of adding a channel partner (a distributor, reseller, VAR,
marketplace, or agency that buys at wholesale and re-sells at its own price) is
subtractive: "the partner takes a cut, so we keep list price minus their
margin." The reasoning treats the partner's margin as a transfer -- a slice of a
fixed pie handed to the partner in exchange for reach.

It is not a transfer. When TWO firms in series each independently set a
profit-maximizing markup -- the manufacturer picks a wholesale price w over its
cost C, then the reseller picks a retail price P over the wholesale price it now
faces as ITS cost -- the two markups STACK. Each firm marks up ignoring the
margin the other is already taking, so the end price lands ABOVE what a single
vertically-integrated seller (who marks up ONCE, from C to the monopoly price)
would charge. This is "double marginalization" (Cournot 1838; Spengler 1950).

Two facts the "the partner just takes a cut" instinct misses:

  1. The independent channel RAISES the end price above the integrated monopoly
     price. On linear demand with willingness-to-pay ~ Uniform[0, VMAX] and unit
     cost C, the integrated seller charges P_int = (VMAX + C)/2, but the
     decentralized manufacturer->reseller channel charges P_dec = (3*VMAX + C)/4
     > P_int. Two hands on the pricing lever push it PAST the monopoly optimum.

  2. It SHRINKS the total pie -- a deadweight loss, not a redistribution. The
     manufacturer's profit PLUS the reseller's profit is strictly LESS than the
     one integrated firm's profit: exactly 3/4 of it on this world, at exactly
     1/2 the quantity. Both channel firms COMBINED earn less than one integrated
     firm would, AND consumers pay more and buy less. The higher price destroys
     mutually-beneficial trades that the integrated firm would have kept.

The trap: an operator evaluates a channel partner as "list price minus their
margin" and under-books the damage -- the second independent markup lifts the
street price, cuts unit volume in half, and leaves the whole channel (vendor +
partner) with a smaller combined profit than going direct. The fix is to remove
the second independent markup: vertically integrate, or use a contract that
kills the double markup (impose a resale price / price ceiling, set a two-part
tariff -- wholesale AT COST plus a fixed franchise fee, or a revenue-share that
makes the partner price as if it owned the full margin). Adding margin LAYERS
(distributor -> VAR -> retailer, each independent) compounds the loss further;
every extra independent markup pushes price up and the combined pie down again.

Gates (each an effect vs its threshold at >= SIGMA; z is on the ESTIMATED MEAN
via its standard error se = std/sqrt(TRIALS), the P104..P122 /se convention):
  G1  channel price inflation (headline)  mean(P_dec - P_int)      >= PRICE_GAP_MIN
  G2  deadweight profit destruction       mean(pi_int - pi_channel) >= PROFIT_GAP_MIN
      (control: the combined channel pie SHRINKS vs the integrated firm, with the
       sign block pi_channel < pi_int AND P_dec > P_int AND Q_dec < Q_int)
  G3  double-marginalization anchor MATCH  realized profit ratio -> 3/4 and
      quantity ratio -> 1/2 (zero-centered deviations, |z| < 3)

Determinism: SEED pinned; a canonical results dict is hashed with sha256 and must
reproduce byte-for-byte across runs. Exit 0 iff all gates pass.

stdlib only: random, math, json, hashlib, bisect.
"""

import bisect
import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 400          # pinned Monte-Carlo trials
SIGMA = 3.0           # gate strength
N_CONSUMERS = 8000    # consumers sampled per trial (the market)

VMAX0 = 100.0         # mean willingness-to-pay ceiling (demand-intercept scale)
COST = 20.0           # marginal unit cost (the manufacturer's cost)
SHAPE = 64.0          # Gamma shape for the per-trial market-level multiplier
#                       (unit mean, CV = 1/sqrt(SHAPE) = 12.5% -- markets vary in size)

PRICE_GAP_MIN = 5.0   # honest floor: the retail-price inflation must clear this
PROFIT_GAP_MIN = 1.0  # honest floor: the combined-pie shrinkage must clear this
                      # (profits are normalized per potential consumer)

# Closed-form double-marginalization ratios (scale-free; the anchor targets).
PROFIT_RATIO_CF = 0.75  # pi_channel_total / pi_integrated = 3/4
QUANTITY_RATIO_CF = 0.5  # Q_decentralized / Q_integrated  = 1/2


def price_integrated(vmax):
    """Integrated monopolist: argmax_P (P-C)*(1 - P/vmax) -> P = (vmax + C)/2."""
    return (vmax + COST) / 2.0


def wholesale_decentralized(vmax):
    """Manufacturer wholesale w: argmax_w (w-C)*Q(P_ret(w)),
    retailer best-response P_ret(w) = (vmax + w)/2 -> w* = (vmax + C)/2."""
    return (vmax + COST) / 2.0


def price_decentralized(vmax):
    """Reseller retail under the two-stage channel:
    P_dec = P_ret(w*) = (vmax + w*)/2 = (3*vmax + C)/4."""
    return (3.0 * vmax + COST) / 4.0


def mean_std(xs):
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var)


def grid_argmax_confirms():
    """Descriptive (no RNG): confirm the closed-form equilibrium prices are the
    argmax of the true (expected) demand profits on a fine grid at VMAX0 -- the
    two-stage markup EMERGES from two independent optimizations, not asserted."""
    vmax = VMAX0
    gridn = 20000
    lo, hi = COST, vmax
    step = (hi - lo) / gridn

    def demand_true(p):
        return max(0.0, 1.0 - p / vmax)  # fraction of consumers with WTP >= p

    # Integrated: one markup from cost.
    best_p, best_v = lo, -1.0
    for i in range(gridn + 1):
        p = lo + i * step
        val = (p - COST) * demand_true(p)
        if val > best_v:
            best_v, best_p = val, p
    int_ok = abs(best_p - price_integrated(vmax)) <= step

    # Decentralized: manufacturer picks w; reseller best-responds P_ret(w).
    best_w, best_wv = lo, -1.0
    for i in range(gridn + 1):
        w = lo + i * step
        p_ret = (vmax + w) / 2.0
        val = (w - COST) * demand_true(p_ret)  # manufacturer earns on units sold
        if val > best_wv:
            best_wv, best_w = val, w
    dec_ok = abs(best_w - wholesale_decentralized(vmax)) <= step

    return bool(int_ok and dec_ok)


def run():
    random.seed(SEED)

    price_int, price_dec, price_gap = [], [], []
    pi_int, pi_channel, profit_gap = [], [], []
    q_int, q_dec = [], []
    profit_dev, quantity_dev = [], []  # zero-centered anchor deviations (G3)

    for _ in range(TRIALS):
        # Market-level size draw first (fixed order -> deterministic).
        vmax = VMAX0 * random.gammavariate(SHAPE, 1.0 / SHAPE)

        p_int = price_integrated(vmax)
        w_star = wholesale_decentralized(vmax)
        p_dec = price_decentralized(vmax)

        # Sample the market: each consumer's willingness-to-pay ~ Uniform[0, vmax].
        wtp = [random.random() * vmax for _ in range(N_CONSUMERS)]
        wtp.sort()

        def demand(p):
            # fraction of consumers with wtp >= p (they buy at price p)
            return (N_CONSUMERS - bisect.bisect_left(wtp, p)) / N_CONSUMERS

        qi = demand(p_int)
        qd = demand(p_dec)

        # Profits normalized per potential consumer.
        prof_int = (p_int - COST) * qi                 # integrated monopolist
        prof_manuf = (w_star - COST) * qd              # manufacturer (wholesale leg)
        prof_ret = (p_dec - w_star) * qd               # reseller (retail leg)
        prof_channel = prof_manuf + prof_ret           # = (p_dec - COST) * qd

        price_int.append(p_int)
        price_dec.append(p_dec)
        price_gap.append(p_dec - p_int)
        pi_int.append(prof_int)
        pi_channel.append(prof_channel)
        profit_gap.append(prof_int - prof_channel)
        q_int.append(qi)
        q_dec.append(qd)
        # G3 zero-centered anchors: pi_channel = 3/4 pi_int, q_dec = 1/2 q_int.
        profit_dev.append(prof_channel - PROFIT_RATIO_CF * prof_int)
        quantity_dev.append(qd - QUANTITY_RATIO_CF * qi)

    def se(sd):
        return sd / math.sqrt(TRIALS)

    pi_m, pi_s = mean_std(price_int)
    pd_m, pd_s = mean_std(price_dec)
    pit_m, pit_s = mean_std(pi_int)
    pic_m, pic_s = mean_std(pi_channel)
    qi_m, qi_s = mean_std(q_int)
    qd_m, qd_s = mean_std(q_dec)

    # G1: the independent channel raises the retail price above the monopoly price.
    g1_m, g1_s = mean_std(price_gap)
    g1_se = se(g1_s)
    z1 = (g1_m - PRICE_GAP_MIN) / g1_se if g1_se > 0 else float("inf")
    g1 = g1_m >= PRICE_GAP_MIN and z1 >= SIGMA

    # G2: the combined channel pie is strictly SMALLER than the integrated firm's
    # (deadweight loss), with the descriptive sign block.
    g2_m, g2_s = mean_std(profit_gap)
    g2_se = se(g2_s)
    z2 = (g2_m - PROFIT_GAP_MIN) / g2_se if g2_se > 0 else float("inf")
    sign_block = bool(pic_m < pit_m and pd_m > pi_m and qd_m < qi_m)
    g2 = g2_m >= PROFIT_GAP_MIN and z2 >= SIGMA and sign_block

    # G3: the realized quantities reproduce the exact double-marginalization
    # ratios (profit 3/4, quantity 1/2) -- zero-centered deviations within 3 sigma.
    pdev_m, pdev_s = mean_std(profit_dev)
    qdev_m, qdev_s = mean_std(quantity_dev)
    pdev_se, qdev_se = se(pdev_s), se(qdev_s)
    z3p = abs(pdev_m) / pdev_se if pdev_se > 0 else 0.0
    z3q = abs(qdev_m) / qdev_se if qdev_se > 0 else 0.0
    g3 = z3p < SIGMA and z3q < SIGMA

    grid_ok = grid_argmax_confirms()

    results = {
        "proposal": 126,
        "domain": "venture",
        "slot": "round-29-venture",
        "seed": SEED,
        "trials": TRIALS,
        "sigma": SIGMA,
        "params": {
            "N_CONSUMERS": N_CONSUMERS, "VMAX0": VMAX0, "COST": COST,
            "SHAPE": SHAPE, "PRICE_GAP_MIN": PRICE_GAP_MIN,
            "PROFIT_GAP_MIN": PROFIT_GAP_MIN,
            "profit_ratio_cf": PROFIT_RATIO_CF, "quantity_ratio_cf": QUANTITY_RATIO_CF,
        },
        "observed": {
            "price_int_mean": round(pi_m, 6), "price_int_se": round(se(pi_s), 6),
            "price_dec_mean": round(pd_m, 6), "price_dec_se": round(se(pd_s), 6),
            "pi_int_mean": round(pit_m, 6), "pi_int_se": round(se(pit_s), 6),
            "pi_channel_mean": round(pic_m, 6), "pi_channel_se": round(se(pic_s), 6),
            "q_int_mean": round(qi_m, 6), "q_int_se": round(se(qi_s), 6),
            "q_dec_mean": round(qd_m, 6), "q_dec_se": round(se(qd_s), 6),
            "g1_price_gap_mean": round(g1_m, 6), "g1_price_gap_se": round(g1_se, 6),
            "g2_profit_gap_mean": round(g2_m, 6), "g2_profit_gap_se": round(g2_se, 6),
            "profit_ratio_mean": round(pic_m / pit_m, 6),
            "quantity_ratio_mean": round(qd_m / qi_m, 6),
            "sign_block_pie_shrinks": sign_block,
            "grid_argmax_confirms_closed_form": grid_ok,
        },
        "gates": {
            "G1_channel_price_inflation": {
                "stat": "mean_price_dec_minus_price_int", "mean": round(g1_m, 6),
                "se": round(g1_se, 6), "threshold": PRICE_GAP_MIN,
                "z": round(z1, 4), "pass": g1,
            },
            "G2_deadweight_profit_destruction": {
                "stat": "mean_pi_int_minus_pi_channel", "mean": round(g2_m, 6),
                "se": round(g2_se, 6), "threshold": PROFIT_GAP_MIN,
                "z": round(z2, 4), "sign_block": sign_block, "pass": g2,
            },
            "G3_double_marginalization_anchor": {
                "stat": "zero_centered_ratio_deviations",
                "profit_dev_mean": round(pdev_m, 6), "z_profit": round(z3p, 4),
                "quantity_dev_mean": round(qdev_m, 6), "z_quantity": round(z3q, 4),
                "pass": g3,
            },
        },
        "all_pass": bool(g1 and g2 and g3),
    }
    return results


def main():
    results = run()
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    print(canonical)
    print("sha256:", digest)
    obs = results["observed"]
    print(
        f"P_int={obs['price_int_mean']} (integrated monopoly price)  ->  "
        f"P_dec={obs['price_dec_mean']} (decentralized channel, +{obs['g1_price_gap_mean']}: "
        f"two independent markups STACK past the monopoly price)  |  "
        f"pi_integrated={obs['pi_int_mean']}  >  pi_channel_total={obs['pi_channel_mean']} "
        f"(the combined pie SHRINKS by {obs['g2_profit_gap_mean']} -- deadweight loss)  |  "
        f"profit ratio {obs['profit_ratio_mean']} (~3/4), quantity ratio "
        f"{obs['quantity_ratio_mean']} (~1/2): double marginalization"
    )
    for name, g in results["gates"].items():
        print(f"{name}: pass={g['pass']}  {g}")
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
