#!/usr/bin/env python3
"""PROPOSAL 110 - The discount-depth breakeven trap.

VENTURE-domain mechanism (round-25 venture slot). Retail / DTC promotional-pricing
unit economics.

Trap / counterintuitive result
------------------------------
A price cut of depth d (fraction off the full price P0) on a product with gross
margin m requires a unit-volume UPLIFT of exactly

    u*(d) = d / (m - d)

just to hold gross profit constant. This breakeven uplift is CONVEX in d and
explodes as d -> m; for any d >= m it is undefined / infinite (you would be
selling at or below cost, so NO volume can break even). Because operators judge a
promotion by "did unit sales go up", they miss that the required uplift is far
larger than any realistic demand response on an inelastic curve. On the pinned
world a 20%-off promo at a 40% margin needs +100% units to break even, realizes
only ~+10% (exponential WTP, elasticity 0.5 at P0), and so DESTROYS ~45% of gross
profit even though unit sales rose. Reading higher promo volume as success is a
margin-dilution mirage.

    GP(d) / GP(0) = e^{lambda * P0 * d} * (m - d) / m

is the exact gross-profit ratio under exponential willingness-to-pay
D(P) = e^{-lambda*P} (point elasticity lambda*P). The discount is profit-neutral
only when the realized uplift factor e^{lambda*P0*d} equals the breakeven factor
m/(m-d); below the breakeven elasticity the same discount destroys profit, above
it the same discount helps. Design fix: size a promotion against the CONVEX
breakeven uplift d/(m-d) for the product's margin and measured elasticity - never
against "units went up".

Gates (each an effect >= 3 sigma from its threshold, over TRIALS pinned trials;
z is computed on the ESTIMATED MEAN via its standard error se = std/sqrt(TRIALS),
the P104/P105/P106/P107/P108/P109 /se convention):
  G1  margin-dilution erosion (headline)   mean(1 - GP_ratio) at inelastic lambda   >= EROSION_MIN
  G2  elasticity-necessity control         mean GP_ratio at elastic lambda          >  1  (discount HELPS)
  G3  closed-form anchor MATCH             sim GP ratios + realized uplift match closed forms (|z| < 3)

Determinism: SEED pinned; a canonical results dict is hashed with sha256 and
must reproduce byte-for-byte across runs. Exit 0 iff all gates pass.

stdlib only: random, math, json, hashlib.
"""

import hashlib
import json
import math
import random

SEED = 20260717
N = 200000        # buyers drawn per trial (WTP population)
TRIALS = 400      # pinned Monte-Carlo trials
SIGMA = 3.0       # gate strength

P0 = 1.0          # full (list) price, normalized
MARGIN = 0.40     # gross margin at full price -> unit cost C = P0*(1-MARGIN)
DISCOUNT = 0.20   # promotional depth d: discounted price = P0*(1-DISCOUNT)
LAMBDA_LO = 0.5   # inelastic demand: WTP ~ Exp(rate LAMBDA_LO); point elasticity lambda*P0 = 0.5
LAMBDA_HI = 5.0   # elastic control demand: elasticity 5.0

EROSION_MIN = 0.10  # honest floor: the inelastic discount must destroy at least this fraction of gross profit

C = P0 * (1.0 - MARGIN)          # unit cost = 0.60
P_DISC = P0 * (1.0 - DISCOUNT)   # discounted price = 0.80
UNIT_MARGIN_FULL = P0 - C        # = m*P0     = 0.40
UNIT_MARGIN_DISC = P_DISC - C    # = (m-d)*P0 = 0.20


def _binomial(n, p):
    """Binomial(n, p): exact Bernoulli sum for small n, normal approx for large n."""
    if n <= 0:
        return 0
    if p <= 0.0:
        return 0
    if p >= 1.0:
        return n
    if n <= 80:
        return sum(1 for _ in range(n) if random.random() < p)
    val = int(round(random.gauss(n * p, math.sqrt(n * p * (1.0 - p)))))
    return 0 if val < 0 else (n if val > n else val)


def gp_ratio_cf(lam):
    """Closed-form gross-profit ratio GP(d)/GP(0) under exponential WTP."""
    return math.exp(lam * P0 * DISCOUNT) * (MARGIN - DISCOUNT) / MARGIN


def uplift_cf(lam):
    """Closed-form realized unit-volume uplift factor - 1 from P0 down to P_DISC."""
    return math.exp(lam * P0 * DISCOUNT) - 1.0


def breakeven_uplift(d):
    """Closed-form volume uplift needed just to hold gross profit at depth d."""
    return d / (MARGIN - d)


def simulate_trial(lam):
    """One trial for a demand curve WTP ~ Exp(lam).

    Buyers are NESTED: everyone who buys at the discounted (lower) price P_DISC is a
    superset of those who buy at the full price P0. Draw n_disc = #{WTP >= P_DISC},
    then n_full = #{WTP >= P0} among them with conditional probability
    P(WTP >= P0 | WTP >= P_DISC) = e^{-lam*(P0 - P_DISC)} = e^{-lam*P0*d}.

    Returns (gp_ratio, realized_uplift) for this trial.
    """
    p_disc = math.exp(-lam * P_DISC)
    cond = math.exp(-lam * (P0 - P_DISC))   # = e^{-lam*P0*d}
    n_disc = _binomial(N, p_disc)
    n_full = _binomial(n_disc, cond)
    if n_full <= 0:
        # degenerate (should not happen on the pinned world); guard for determinism
        return 0.0, 0.0
    gp_full = n_full * UNIT_MARGIN_FULL
    gp_disc = n_disc * UNIT_MARGIN_DISC
    gp_ratio = gp_disc / gp_full
    realized_uplift = n_disc / n_full - 1.0
    return gp_ratio, realized_uplift


def mean_std(xs):
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var)


def run():
    random.seed(SEED)
    ratio_lo, uplift_lo, ratio_hi = [], [], []
    for _ in range(TRIALS):
        r, u = simulate_trial(LAMBDA_LO)
        ratio_lo.append(r)
        uplift_lo.append(u)
    for _ in range(TRIALS):
        r, _u = simulate_trial(LAMBDA_HI)
        ratio_hi.append(r)

    rlo_m, rlo_s = mean_std(ratio_lo)
    ulo_m, ulo_s = mean_std(uplift_lo)
    rhi_m, rhi_s = mean_std(ratio_hi)
    erosion = [1.0 - r for r in ratio_lo]
    ero_m, ero_s = mean_std(erosion)

    def se(sd):
        return sd / math.sqrt(TRIALS)

    ero_se = se(ero_s)
    rlo_se = se(rlo_s)
    ulo_se = se(ulo_s)
    rhi_se = se(rhi_s)

    cf_ratio_lo = gp_ratio_cf(LAMBDA_LO)
    cf_ratio_hi = gp_ratio_cf(LAMBDA_HI)
    cf_uplift_lo = uplift_cf(LAMBDA_LO)
    breakeven = breakeven_uplift(DISCOUNT)

    # G1: margin-dilution erosion (headline) -- the inelastic discount destroys
    # >= EROSION_MIN of gross profit by >= 3 sigma, despite unit sales rising.
    z1 = (ero_m - EROSION_MIN) / ero_se if ero_se > 0 else float("inf")
    g1 = ero_m >= EROSION_MIN and z1 >= SIGMA

    # G2: elasticity-necessity control -- the SAME discount at the SAME margin on
    # ELASTIC demand RAISES gross profit (ratio > 1) by >= 3 sigma, proving the
    # erosion is the margin/elasticity breakeven, not discounting per se.
    z2 = (rhi_m - 1.0) / rhi_se if rhi_se > 0 else float("inf")
    g2 = rhi_m > 1.0 and z2 >= SIGMA

    # G3: closed-form anchor MATCH -- simulated GP ratios (both segments) and the
    # realized inelastic uplift reproduce the exact closed forms (|z| < 3 each).
    z3a = abs(rlo_m - cf_ratio_lo) / rlo_se if rlo_se > 0 else 0.0
    z3b = abs(rhi_m - cf_ratio_hi) / rhi_se if rhi_se > 0 else 0.0
    z3c = abs(ulo_m - cf_uplift_lo) / ulo_se if ulo_se > 0 else 0.0
    g3 = z3a < SIGMA and z3b < SIGMA and z3c < SIGMA

    results = {
        "proposal": 110,
        "domain": "venture",
        "slot": "round-25-venture",
        "seed": SEED,
        "N": N,
        "trials": TRIALS,
        "sigma": SIGMA,
        "params": {
            "P0": P0, "margin": MARGIN, "discount": DISCOUNT,
            "cost": round(C, 6), "price_disc": round(P_DISC, 6),
            "lambda_lo": LAMBDA_LO, "lambda_hi": LAMBDA_HI,
            "EROSION_MIN": EROSION_MIN,
        },
        "observed": {
            "gp_ratio_lo_mean": round(rlo_m, 6), "gp_ratio_lo_se": round(rlo_se, 6),
            "erosion_lo_mean": round(ero_m, 6), "erosion_lo_se": round(ero_se, 6),
            "realized_uplift_lo_mean": round(ulo_m, 6), "realized_uplift_lo_se": round(ulo_se, 6),
            "gp_ratio_hi_mean": round(rhi_m, 6), "gp_ratio_hi_se": round(rhi_se, 6),
        },
        "closed_form": {
            "gp_ratio_lo": round(cf_ratio_lo, 6),
            "gp_ratio_hi": round(cf_ratio_hi, 6),
            "realized_uplift_lo": round(cf_uplift_lo, 6),
            "breakeven_uplift": round(breakeven, 6),
            "breakeven_table": [
                {"d": 0.10, "u_star": round(breakeven_uplift(0.10), 6)},
                {"d": 0.20, "u_star": round(breakeven_uplift(0.20), 6)},
                {"d": 0.30, "u_star": round(breakeven_uplift(0.30), 6)},
            ],
        },
        "gates": {
            "G1_margin_dilution_erosion": {
                "stat": "mean_gross_profit_erosion", "mean": round(ero_m, 6),
                "se": round(ero_se, 6), "threshold": EROSION_MIN,
                "z": round(z1, 4), "pass": g1,
            },
            "G2_elasticity_necessity": {
                "stat": "mean_gp_ratio_elastic", "mean": round(rhi_m, 6),
                "se": round(rhi_se, 6), "threshold": 1.0,
                "z": round(z2, 4), "pass": g2,
            },
            "G3_anchor_match": {
                "stat": "sim_vs_closed_form",
                "z_ratio_lo": round(z3a, 4), "z_ratio_hi": round(z3b, 4),
                "z_uplift_lo": round(z3c, 4), "pass": g3,
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
    cf = results["closed_form"]
    print(
        f"inelastic: GP_ratio={obs['gp_ratio_lo_mean']} (erosion {obs['erosion_lo_mean']}), "
        f"realized uplift +{obs['realized_uplift_lo_mean']} vs breakeven +{cf['breakeven_uplift']} "
        f"needed  |  elastic control: GP_ratio={obs['gp_ratio_hi_mean']} (discount HELPS)"
    )
    for name, g in results["gates"].items():
        print(f"{name}: pass={g['pass']}  {g}")
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
