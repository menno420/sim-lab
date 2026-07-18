#!/usr/bin/env python3
"""PROPOSAL 122 - The NRR composition mirage (dollar-weighting hides logo churn).

VENTURE-domain mechanism (round-28 venture slot). SaaS retention / revenue-quality
metrics.

Trap / counterintuitive result
------------------------------
Net Revenue Retention (NRR, a.k.a. net dollar retention) is the headline SaaS
health metric: the fraction of last period's recurring revenue you still have
this period after expansion, contraction, and churn, aggregated ACROSS the
customer base. It is DOLLAR-weighted:

    NRR = sum_i r_i * m_i / sum_i r_i,

where r_i is account i's starting revenue and m_i its retained-revenue MULTIPLE
this period (0 if it churned, the expansion factor if it survived and grew). An
NRR above 100% ("negative net churn") is treated as best-in-class -- proof that
you keep and grow customers.

But NRR is dollar-weighted, so it is a REVENUE-CONCENTRATION statistic, not a
customer-retention one. When revenue is concentrated in a few large accounts
(the usual heavy-tailed SaaS book) and those whales expand while a long tail of
small accounts churns, the whales' dollars DOMINATE the numerator and the
blended NRR reads > 100% -- even though the MAJORITY OF LOGOS were lost. This is
Simpson's paradox in a weighted mean: the aggregate points the opposite way from
the accounts. Two facts the ">100% NRR = we retain customers" instinct misses:

  1. NRR and logo retention DIVERGE. Dollar-weighted NRR can sit far above the
     fraction of customers actually retained; a 118%-NRR book can be losing a
     third of its logos. "Negative net churn" says nothing about how many
     customers stayed.

  2. The >100% is the WEIGHTING, not the retention. Strip the revenue weights --
     give every account equal weight (equal-weighted NRR = mean_i m_i, the
     "typical account's" retention) -- and the same book reads BELOW 100%: it is
     contracting per logo. The headline was manufactured by concentration.

The trap: operators read NRR > 100% as customer-retention health and under-invest
in the small-account base that is quietly bleeding out (until the whale
concentration itself becomes the risk). The fix is to report NRR ALONGSIDE logo
(count-weighted) retention and an equal-weighted NRR, and to read a gap between
them as revenue concentration -- NRR measures whose dollars you kept, logo
retention measures whether customers stay.

Gates (each an effect vs its threshold at >= SIGMA; z is on the ESTIMATED MEAN
via its standard error se = std/sqrt(TRIALS), the P104..P121 /se convention):
  G1  NRR-vs-logo divergence (headline)  mean(NRR_dollar - logo_retention) >= GAP_MIN
  G2  concentration control              mean(NRR_dollar - NRR_equal)      >= GAP_MIN
      (equal-weighting collapses NRR below 100%: NRR_equal < 1 < NRR_dollar)
  G3  closed-form anchor MATCH           sim NRR_dollar, NRR_equal match the
                                         revenue-/equal-weighted closed forms (|z| < 3)

Determinism: SEED pinned; a canonical results dict is hashed with sha256 and must
reproduce byte-for-byte across runs. Exit 0 iff all gates pass.

stdlib only: random, math, json, hashlib.
"""

import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 400        # pinned Monte-Carlo trials
SIGMA = 3.0         # gate strength
N_ACCOUNTS = 20000  # accounts sampled per trial (the book of business)

F_WHALE = 0.10      # fraction of LOGOS that are large ("whale") accounts
R_BIG = 100.0       # starting revenue of a whale account
R_SMALL = 1.0       # starting revenue of a small ("minnow") account

P_WHALE = 0.95      # whale survival probability this period (low churn)
EXP_WHALE = 1.30    # surviving-whale expansion multiple (they grow)
P_MINNOW = 0.60     # minnow survival probability (high churn, the bleeding tail)
EXP_MINNOW = 1.00   # surviving-minnow multiple (flat: keep, no expansion)

GAP_MIN = 0.05      # honest floor: the divergence must clear at least this much

# Expected retained-revenue multiple per segment: E[m] = survival * expansion.
EM_WHALE = P_WHALE * EXP_WHALE     # 1.235
EM_MINNOW = P_MINNOW * EXP_MINNOW  # 0.60

# Whale share of TOTAL revenue (the dollar weight that dominates NRR).
W_WHALE = (F_WHALE * R_BIG) / (F_WHALE * R_BIG + (1.0 - F_WHALE) * R_SMALL)


def nrr_dollar_cf():
    """Closed-form dollar-weighted NRR = revenue-share-weighted mean of E[m]."""
    return W_WHALE * EM_WHALE + (1.0 - W_WHALE) * EM_MINNOW


def nrr_equal_cf():
    """Closed-form equal-weighted NRR = logo-share-weighted mean of E[m]."""
    return F_WHALE * EM_WHALE + (1.0 - F_WHALE) * EM_MINNOW


def logo_ret_cf():
    """Closed-form logo (count-weighted) retention = logo-share-weighted survival."""
    return F_WHALE * P_WHALE + (1.0 - F_WHALE) * P_MINNOW


def one_trial():
    """One period over N_ACCOUNTS accounts. Returns (NRR_dollar, logo_ret, NRR_equal)."""
    rev_start = 0.0
    rev_retained = 0.0
    logos_kept = 0
    mult_sum = 0.0
    for _ in range(N_ACCOUNTS):
        # Fixed draw order per account -> deterministic: assignment, then survival.
        whale = random.random() < F_WHALE
        r = R_BIG if whale else R_SMALL
        p = P_WHALE if whale else P_MINNOW
        exp = EXP_WHALE if whale else EXP_MINNOW
        survived = random.random() < p
        m = exp if survived else 0.0        # retained-revenue multiple for this account
        rev_start += r
        rev_retained += r * m
        logos_kept += 1 if survived else 0
        mult_sum += m
    nrr_dollar = rev_retained / rev_start       # dollar-weighted NRR
    logo_ret = logos_kept / N_ACCOUNTS          # count-weighted retention
    nrr_equal = mult_sum / N_ACCOUNTS           # equal-weighted NRR (typical account)
    return nrr_dollar, logo_ret, nrr_equal


def mean_std(xs):
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var)


def run():
    random.seed(SEED)

    nrr_d, logo_r, nrr_e = [], [], []
    for _ in range(TRIALS):
        d, lr, e = one_trial()
        nrr_d.append(d)
        logo_r.append(lr)
        nrr_e.append(e)

    def se(sd):
        return sd / math.sqrt(TRIALS)

    d_m, d_s = mean_std(nrr_d)
    lr_m, lr_s = mean_std(logo_r)
    e_m, e_s = mean_std(nrr_e)
    d_se, lr_se, e_se = se(d_s), se(lr_s), se(e_s)

    # G1: dollar-NRR massively overstates the fraction of customers retained.
    g1_gap = [d - lr for d, lr in zip(nrr_d, logo_r)]
    g1_m, g1_s = mean_std(g1_gap)
    g1_se = se(g1_s)
    z1 = (g1_m - GAP_MIN) / g1_se if g1_se > 0 else float("inf")
    g1 = g1_m >= GAP_MIN and z1 >= SIGMA

    # G2: equal-weighting collapses NRR below 100% -> the >100% is concentration.
    g2_gap = [d - e for d, e in zip(nrr_d, nrr_e)]
    g2_m, g2_s = mean_std(g2_gap)
    g2_se = se(g2_s)
    z2 = (g2_m - GAP_MIN) / g2_se if g2_se > 0 else float("inf")
    # Descriptive sign flip: equal-weighted below 1.0, dollar-weighted above 1.0.
    sign_flip = bool(e_m < 1.0 < d_m)
    g2 = g2_m >= GAP_MIN and z2 >= SIGMA and sign_flip

    # G3: sim NRR_dollar and NRR_equal match the weighted closed forms.
    cf_d = nrr_dollar_cf()
    cf_e = nrr_equal_cf()
    z3a = abs(d_m - cf_d) / d_se if d_se > 0 else 0.0
    z3b = abs(e_m - cf_e) / e_se if e_se > 0 else 0.0
    g3 = z3a < SIGMA and z3b < SIGMA

    results = {
        "proposal": 122,
        "domain": "venture",
        "slot": "round-28-venture",
        "seed": SEED,
        "trials": TRIALS,
        "sigma": SIGMA,
        "params": {
            "N_ACCOUNTS": N_ACCOUNTS, "F_WHALE": F_WHALE,
            "R_BIG": R_BIG, "R_SMALL": R_SMALL,
            "P_WHALE": P_WHALE, "EXP_WHALE": EXP_WHALE,
            "P_MINNOW": P_MINNOW, "EXP_MINNOW": EXP_MINNOW,
            "GAP_MIN": GAP_MIN,
            "whale_revenue_share": round(W_WHALE, 6),
            "em_whale": round(EM_WHALE, 6), "em_minnow": round(EM_MINNOW, 6),
        },
        "observed": {
            "nrr_dollar_mean": round(d_m, 6), "nrr_dollar_se": round(d_se, 6),
            "logo_ret_mean": round(lr_m, 6), "logo_ret_se": round(lr_se, 6),
            "nrr_equal_mean": round(e_m, 6), "nrr_equal_se": round(e_se, 6),
            "g1_divergence_mean": round(g1_m, 6), "g1_divergence_se": round(g1_se, 6),
            "g2_concentration_mean": round(g2_m, 6), "g2_concentration_se": round(g2_se, 6),
            "sign_flip_equal_below_1_dollar_above_1": sign_flip,
        },
        "closed_form": {
            "nrr_dollar_cf": round(cf_d, 6),
            "nrr_equal_cf": round(cf_e, 6),
            "logo_ret_cf": round(logo_ret_cf(), 6),
        },
        "gates": {
            "G1_nrr_vs_logo_divergence": {
                "stat": "mean_nrr_dollar_minus_logo_ret", "mean": round(g1_m, 6),
                "se": round(g1_se, 6), "threshold": GAP_MIN,
                "z": round(z1, 4), "pass": g1,
            },
            "G2_concentration_control": {
                "stat": "mean_nrr_dollar_minus_nrr_equal", "mean": round(g2_m, 6),
                "se": round(g2_se, 6), "threshold": GAP_MIN,
                "z": round(z2, 4), "sign_flip": sign_flip, "pass": g2,
            },
            "G3_anchor_match": {
                "stat": "sim_vs_closed_form",
                "z_nrr_dollar": round(z3a, 4), "z_nrr_equal": round(z3b, 4), "pass": g3,
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
        f"NRR_dollar={obs['nrr_dollar_mean']} (>1.0, 'negative net churn')  "
        f"but logo retention={obs['logo_ret_mean']}  "
        f"(dollar-NRR overstates customer retention by {obs['g1_divergence_mean']})  |  "
        f"equal-weighted NRR={obs['nrr_equal_mean']} (<1.0: contracting per logo) -> "
        f"the >100% is concentration, gap {obs['g2_concentration_mean']}  |  "
        f"closed forms NRR_dollar={cf['nrr_dollar_cf']} NRR_equal={cf['nrr_equal_cf']}"
    )
    for name, g in results["gates"].items():
        print(f"{name}: pass={g['pass']}  {g}")
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
