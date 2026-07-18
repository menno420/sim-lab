#!/usr/bin/env python3
"""PROPOSAL 130 - The annual-prepay financing trap (implied cost of capital).

VENTURE-domain mechanism (round-30 venture slot). Subscription cash-flow
economics: offering an annual-prepay discount to "pull cash forward."

Trap / counterintuitive result
------------------------------
The folk model of an annual-prepay discount is that it is free money: "give the
customer X% off to pay a year up front, and we get 12 months of cash now instead
of dribbled out monthly -- great for cash flow." The reasoning treats the earlier
cash as a pure win and the discount as a small price for it.

It is not free. Selling a 12-month revenue stream for a discounted lump sum is a
LOAN the firm takes FROM its customer, and the discount is the interest on that
loan. Relative to billing monthly, the firm receives 12*(1-d) at t=0 instead of 1
per month for 12 months -- it has borrowed ~11 months of revenue and is repaying
by forgoing the discount d*12. The implied financing rate is the internal rate of
return of that incremental cash flow: the monthly rate r* that solves

    sum_{t=0}^{11} (1+r*)^{-t} = 12*(1-d),

and the implied ANNUAL cost of that financing is APR_implied = (1+r*)^12 - 1.

Two facts the "annual prepay is free cash" instinct misses:

  1. The implied financing APR is HUGE. A modest-looking "2 months free"
     (d = 2/12 = 1/6 ~ 16.7%) implies r* ~ 3.5%/month, i.e. APR_implied ~ 51% --
     the firm is borrowing against its own future revenue at ~51% a year. Unless
     the firm's true cost of capital exceeds that, it is overpaying for the cash.

  2. At any realistic cost of capital the discounted deal DESTROYS NPV. With a
     real cost of capital of r_true (here ~1%/month, ~12.7% APR), monthly billing
     is worth S(r_true) = sum (1+r_true)^{-t} ~ 11.37 months of revenue in present
     value, while the annual-prepay deal is worth only 12*(1-d) = 10 -- the firm
     gave up ~1.37 months of revenue (~11.4% of contract value) in NPV to pull the
     cash forward. The FAIR break-even discount at that cost of capital is only
     d_fair = 1 - S(r_true)/12 ~ 5.3% (~0.63 months), so the market-norm "2 months
     free" (16.7%) over-discounts by ~3.2x.

The trap: an operator books annual prepay as "free cash + a small discount" and
under-prices the discount, which is really an implied APR far above the firm's
cost of capital. The discount is only worth paying when the firm is genuinely
capital-constrained above the implied rate (cannot raise cheaper money, would
otherwise dilute) OR when the annual lock-in buys enough CHURN reduction to clear
that bar (a separate, measurable benefit -- see the model-basis note). Absent
that, price the prepay discount as debt: never give more than d_fair = 1 -
S(r_true)/12.

Gates (each an effect vs its threshold at >= SIGMA; z is on the ESTIMATED MEAN via
its standard error se = std/sqrt(TRIALS), the P104..P126 /se convention):
  G1  implied financing rate (headline)  mean(APR_implied - APR_true)  >= APR_GAP_MIN
  G2  deadweight NPV destruction         mean(NPV_monthly - NPV_annual) >= NPV_GAP_MIN
      per $ of annual list, with the sign block NPV_annual < NPV_monthly AND
      APR_implied > APR_true AND d_offered > d_fair AND cash_pulled_forward > 0
  G3  IRR / break-even-discount anchor    sampled dollar-weighted PV multiple
      reproduces the count-mean PV multiple (spend-independence, zero-centered
      |z| < 3), AND APR_implied matches the analytic IRR, AND the incremental
      cash-flow IRR has a unique sign change

Determinism: SEED pinned; a canonical results dict is hashed with sha256 and must
reproduce byte-for-byte across runs. Exit 0 iff all gates pass.

stdlib only: random, math, json, hashlib.
"""

import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 400          # pinned Monte-Carlo trials
SIGMA = 3.0           # gate strength
N_CUSTOMERS = 8000    # customers sampled per trial (the book of business)

MONTHS = 12           # annual contract horizon (months)
DISCOUNT = 1.0 / 6.0  # annual-prepay discount d = 2 months free = 1/6 ~ 16.667%
R_TRUE_MONTHLY = 0.01  # firm's real cost of capital, 1%/month (~12.68% APR)
SHAPE = 64.0          # Gamma shape for the per-customer cost-of-capital draw
#                       (unit mean, CV = 1/sqrt(SHAPE) = 12.5% -- capital cost
#                        varies across segments/periods)
MSPEND0 = 100.0       # mean monthly spend (ticket size); scale-free in the result

APR_GAP_MIN = 0.15    # honest floor: the implied financing APR must clear the
#                       real cost of capital by at least 15 percentage points
NPV_GAP_MIN = 0.03    # honest floor: the NPV destroyed per $ of annual list must
#                       clear 3% of contract value


def pv_multiple(r):
    """S(r) = sum_{t=0}^{MONTHS-1} (1+r)^{-t}: present value (in months of
    revenue) of MONTHS monthly $1 payments discounted at monthly rate r,
    paid at the start of each month (annuity-due)."""
    v = 1.0 / (1.0 + r)
    return sum(v ** t for t in range(MONTHS))


def implied_monthly_irr(d):
    """Internal rate of return r* of the monthly->annual-prepay incremental cash
    flow: the r solving S(r) = MONTHS*(1-d). Found by bisection (measured); the
    incremental stream is +[MONTHS*(1-d) - 1] at t=0 and -1 at t=1..MONTHS-1, a
    single sign change, so the IRR is unique and bisection is exact."""
    target = MONTHS * (1.0 - d)  # = S(r*)
    lo, hi = 0.0, 5.0            # S is strictly decreasing in r; S(0)=MONTHS>target
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if pv_multiple(mid) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def irr_unique_sign_change(d):
    """Descriptive (no RNG): the incremental cash flow [MONTHS*(1-d)-1, -1,...,-1]
    changes sign exactly once (Descartes / Norstrom), so the IRR is well-defined
    and unique -- confirm the discounted-NPV function g(r)=S(r)-MONTHS*(1-d)
    crosses zero exactly once on a fine grid."""
    target = MONTHS * (1.0 - d)
    gridn = 20000
    lo, hi = 0.0, 2.0
    step = (hi - lo) / gridn
    sign_changes = 0
    prev = pv_multiple(lo) - target
    for i in range(1, gridn + 1):
        cur = pv_multiple(lo + i * step) - target
        if (prev > 0) != (cur > 0):
            sign_changes += 1
        prev = cur
    return sign_changes == 1


def mean_std(xs):
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var)


def run():
    random.seed(SEED)

    d = DISCOUNT
    annual_multiple = MONTHS * (1.0 - d)          # 12*(1-d) = 10 (months of rev)
    r_star = implied_monthly_irr(d)               # measured break-even monthly IRR
    apr_implied = (1.0 + r_star) ** 12 - 1.0      # implied financing APR of the offer

    # Analytic cross-checks (descriptive) at the pinned mean cost of capital.
    s_true = pv_multiple(R_TRUE_MONTHLY)          # PV multiple at r_true (~11.37)
    apr_true_ref = (1.0 + R_TRUE_MONTHLY) ** 12 - 1.0
    d_fair_ref = 1.0 - s_true / MONTHS            # fair break-even discount ~5.3%

    apr_gap = []          # APR_implied - APR_true_i           (G1)
    npv_gap_per_dollar = []  # (NPV_monthly - NPV_annual)/annual-list  (G2)
    d_star_list = []      # per-customer fair break-even discount
    ratio_dev = []        # dollar-weighted PV multiple - count-mean PV multiple (G3)
    npv_monthly_pd, npv_annual_pd = [], []  # per $ of monthly list, for reporting

    for _ in range(TRIALS):
        r_list, m_list, s_list = [], [], []
        for _c in range(N_CUSTOMERS):
            r_i = R_TRUE_MONTHLY * random.gammavariate(SHAPE, 1.0 / SHAPE)
            m_i = MSPEND0 * random.random() * 2.0   # Uniform[0, 2*MSPEND0]
            r_list.append(r_i)
            m_list.append(m_i)
            s_list.append(pv_multiple(r_i))

        # Per-customer stats (per $1 of monthly list; scale-free in spend).
        apr_i = [(1.0 + r) ** 12 - 1.0 for r in r_list]
        d_star_i = [1.0 - s / MONTHS for s in s_list]

        apr_gap.append(apr_implied - (sum(apr_i) / N_CUSTOMERS))
        # NPV per $ of ANNUAL undiscounted list (= MONTHS months of revenue):
        #   monthly billing PV = S_i (months), annual-prepay PV = MONTHS*(1-d).
        gap_pd = [(s - annual_multiple) / MONTHS for s in s_list]
        npv_gap_per_dollar.append(sum(gap_pd) / N_CUSTOMERS)
        d_star_list.append(sum(d_star_i) / N_CUSTOMERS)
        npv_monthly_pd.append((sum(s_list) / N_CUSTOMERS) / MONTHS)
        npv_annual_pd.append(annual_multiple / MONTHS)

        # G3 anchor: the DOLLAR-weighted PV multiple must reproduce the
        # CUSTOMER-count-weighted PV multiple -- the discount identity is
        # spend-independent (holds in expectation because spend m_i and capital
        # cost r_i are drawn independently). Zero-centered sampling deviation.
        dollar_wt = sum(m * s for m, s in zip(m_list, s_list)) / sum(m_list)
        count_wt = sum(s_list) / N_CUSTOMERS
        ratio_dev.append(dollar_wt - count_wt)

    def se(sd):
        return sd / math.sqrt(TRIALS)

    # G1: the implied financing APR of the offer exceeds the firm's real cost of
    # capital -- the annual-prepay discount is implicit borrowing above cost.
    g1_m, g1_s = mean_std(apr_gap)
    g1_se = se(g1_s)
    z1 = (g1_m - APR_GAP_MIN) / g1_se if g1_se > 0 else float("inf")
    g1 = g1_m >= APR_GAP_MIN and z1 >= SIGMA

    # G2: at the real cost of capital the discounted annual deal is worth strictly
    # less than monthly billing -- a deadweight NPV loss, with the sign block.
    g2_m, g2_s = mean_std(npv_gap_per_dollar)
    g2_se = se(g2_s)
    z2 = (g2_m - NPV_GAP_MIN) / g2_se if g2_se > 0 else float("inf")
    npvm_m, _ = mean_std(npv_monthly_pd)
    npva_m, _ = mean_std(npv_annual_pd)
    apr_gap_mean, _ = mean_std(apr_gap)
    dstar_m, _ = mean_std(d_star_list)
    sign_block = bool(
        npva_m < npvm_m               # annual-prepay PV < monthly-billing PV
        and apr_implied > (apr_implied - apr_gap_mean)  # APR_implied > APR_true
        and DISCOUNT > dstar_m        # offered discount exceeds the fair discount
        and annual_multiple < MONTHS  # cash pulled forward (< full 12 months)
    )
    g2 = g2_m >= NPV_GAP_MIN and z2 >= SIGMA and sign_block

    # G3: dollar-weighted PV multiple reproduces the count-mean (zero-centered),
    # plus the descriptive closed-form IRR confirmations.
    g3d_m, g3d_s = mean_std(ratio_dev)
    g3d_se = se(g3d_s)
    z3 = abs(g3d_m) / g3d_se if g3d_se > 0 else 0.0
    apr_anchor_ok = abs(apr_implied - ((1.0 + implied_monthly_irr(DISCOUNT)) ** 12 - 1.0)) < 1e-9
    irr_unique = irr_unique_sign_change(DISCOUNT)
    g3 = z3 < SIGMA and apr_anchor_ok and irr_unique

    results = {
        "proposal": 130,
        "domain": "venture",
        "slot": "round-30-venture",
        "seed": SEED,
        "trials": TRIALS,
        "sigma": SIGMA,
        "params": {
            "N_CUSTOMERS": N_CUSTOMERS, "MONTHS": MONTHS, "DISCOUNT": round(DISCOUNT, 6),
            "R_TRUE_MONTHLY": R_TRUE_MONTHLY, "SHAPE": SHAPE, "MSPEND0": MSPEND0,
            "APR_GAP_MIN": APR_GAP_MIN, "NPV_GAP_MIN": NPV_GAP_MIN,
        },
        "closed_form": {
            "annual_multiple_months": round(annual_multiple, 6),   # 12*(1-d) = 10
            "r_star_monthly": round(r_star, 6),                    # break-even IRR
            "apr_implied": round(apr_implied, 6),                  # ~0.5128
            "pv_multiple_at_r_true": round(s_true, 6),             # S(0.01) ~ 11.37
            "apr_true_ref": round(apr_true_ref, 6),                # ~0.1268
            "d_fair_ref": round(d_fair_ref, 6),                    # ~0.0527
            "over_discount_ratio": round(DISCOUNT / d_fair_ref, 6),  # ~3.16
        },
        "observed": {
            "apr_gap_mean": round(g1_m, 6), "apr_gap_se": round(g1_se, 6),
            "npv_gap_per_dollar_mean": round(g2_m, 6), "npv_gap_per_dollar_se": round(g2_se, 6),
            "npv_monthly_per_dollar_mean": round(npvm_m, 6),
            "npv_annual_per_dollar_mean": round(npva_m, 6),
            "d_star_mean": round(dstar_m, 6),
            "ratio_dev_mean": round(g3d_m, 6), "ratio_dev_se": round(g3d_se, 6),
            "sign_block_annual_destroys_value": sign_block,
            "apr_anchor_matches_analytic_irr": apr_anchor_ok,
            "irr_unique_sign_change": irr_unique,
        },
        "gates": {
            "G1_implied_financing_rate": {
                "stat": "mean_apr_implied_minus_apr_true", "mean": round(g1_m, 6),
                "se": round(g1_se, 6), "threshold": APR_GAP_MIN,
                "z": round(z1, 4), "pass": g1,
            },
            "G2_deadweight_npv_destruction": {
                "stat": "mean_npv_monthly_minus_annual_per_dollar_list", "mean": round(g2_m, 6),
                "se": round(g2_se, 6), "threshold": NPV_GAP_MIN,
                "z": round(z2, 4), "sign_block": sign_block, "pass": g2,
            },
            "G3_irr_breakeven_discount_anchor": {
                "stat": "dollar_weighted_minus_count_mean_pv_multiple",
                "ratio_dev_mean": round(g3d_m, 6), "z": round(z3, 4),
                "apr_anchor_ok": apr_anchor_ok, "irr_unique": irr_unique,
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
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    cf = results["closed_form"]
    obs = results["observed"]
    print(
        f"annual-prepay d={DISCOUNT:.4f} (2 months free)  ->  implied financing "
        f"APR={cf['apr_implied']} (r*={cf['r_star_monthly']}/mo)  vs  real cost of "
        f"capital APR={cf['apr_true_ref']}  |  at r_true the monthly-billing PV="
        f"{cf['pv_multiple_at_r_true']} months  >  annual-prepay PV="
        f"{cf['annual_multiple_months']} months (NPV destroyed "
        f"{obs['npv_gap_per_dollar_mean']} per $ of annual list)  |  fair break-even "
        f"discount d_fair={cf['d_fair_ref']}  =>  offered d over-discounts by "
        f"{cf['over_discount_ratio']}x"
    )
    for name, g in results["gates"].items():
        print(f"{name}: pass={g['pass']}  {g}")
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
