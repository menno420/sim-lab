#!/usr/bin/env python3
"""PROPOSAL 106 - The retention-survivorship mirage.

VENTURE-domain mechanism (round-24 venture slot). Subscription / SaaS churn-cohort
unit economics.

Trap / counterintuitive result
------------------------------
A subscriber base is a MIXTURE of heterogeneous customers, each with a CONSTANT
monthly retention hazard: a loyal segment retains at r_A and a churny segment at
r_B < r_A. No individual customer ever gets stickier. Yet the OBSERVED cohort
month-over-month retention rate R(t) - the fraction of this-month survivors who
are still active next month - RISES monotonically with tenure t, purely because
the churny segment burns off first and the aging cohort is increasingly made of
loyal survivors. The headline retention curve climbs from R(0) toward the loyal
segment's rate r_A even though the firm did NOTHING and no customer improved.

  R(t) = ( w_A * r_A^(t+1) + w_B * r_B^(t+1) ) / ( w_A * r_A^t + w_B * r_B^t )

is a survivor-weighted average of r_A and r_B whose weight shifts toward r_A as
t grows, so R(t) increases in t and R(t) -> max(r_A, r_B). Reading the rising
curve as "our retention is improving / the product is getting stickier / this
cohort is higher quality" is a SURVIVORSHIP-BIAS artifact of a static mixture -
the mover-stayer / heterogeneity effect (Blumen-Kogan-McCarthy 1955; Vaupel
frailty; Fader-Hardie shifted-beta-geometric). Design fix: measure retention
WITHIN homogeneous segments (or fit a heterogeneity model), never read a rising
aggregate cohort curve as a hazard improvement.

Gates (each an effect >= 3 sigma from its threshold, over TRIALS pinned trials;
z is computed on the ESTIMATED MEAN via its standard error se = std/sqrt(TRIALS),
the P104/P105 /se convention):
  G1  survivorship lift (headline)   mean(R_late - R_early)   >= LIFT_MIN
  G2  individual-constant control    pooled seg retention matches r_A AND r_B (|z| < 3)
  G3  closed-form anchor MATCH       mean R_obs(t) matches R_cf(t) at t=0 and t=late (|z| < 3)

Determinism: SEED pinned; a canonical results dict is hashed with sha256 and
must reproduce byte-for-byte across runs. Exit 0 iff all gates pass.

stdlib only: random, math, json, hashlib.
"""

import hashlib
import json
import math
import random

SEED = 20260717
N = 200000        # customers per cohort trial
T = 24            # months of observation
TRIALS = 400      # pinned Monte-Carlo cohorts
SIGMA = 3.0       # gate strength
T_LATE = 12       # late tenure at which the survivorship lift is read

W_A = 0.5         # loyal-segment share
R_A = 0.97        # loyal-segment constant monthly retention
R_B = 0.55        # churny-segment constant monthly retention
# W_B = 1 - W_A, R_B as above.

LIFT_MIN = 0.05   # honest floor: observed retention must rise by at least this much

# Exact integer split so the mixture weights are pinned and match the closed form.
N_A = int(round(W_A * N))
N_B = N - N_A
WA_EFF = N_A / N
WB_EFF = N_B / N


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


def r_cf(t):
    """Closed-form observed cohort month-over-month retention at tenure t."""
    num = WA_EFF * R_A ** (t + 1) + WB_EFF * R_B ** (t + 1)
    den = WA_EFF * R_A ** t + WB_EFF * R_B ** t
    return num / den


def simulate_cohort():
    """One cohort: track alive counts per segment month by month.

    Returns (R_early, R_late, pooledA, pooledB) where R_* are observed aggregate
    month-over-month retention rates and pooled* are the tenure-pooled observed
    retention within each segment (the constant-hazard control).
    """
    a = N_A
    b = N_B
    survivedA_by_t = []
    survivedB_by_t = []
    atriskA = 0
    survA = 0
    atriskB = 0
    survB = 0
    agg_alive = [a + b]          # A_0
    agg_surv = []                # S_t = survivors from month t to t+1
    for t in range(T):
        sA = _binomial(a, R_A)
        sB = _binomial(b, R_B)
        atriskA += a
        survA += sA
        atriskB += b
        survB += sB
        agg_surv.append(sA + sB)
        a, b = sA, sB
        agg_alive.append(a + b)
    # aggregate observed retention R_obs(t) = S_t / A_t
    r_early = agg_surv[0] / agg_alive[0]
    r_late = agg_surv[T_LATE] / agg_alive[T_LATE]
    pooledA = survA / atriskA if atriskA else 0.0
    pooledB = survB / atriskB if atriskB else 0.0
    return r_early, r_late, pooledA, pooledB


def mean_std(xs):
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var)


def run():
    random.seed(SEED)
    early, late, lift, pA, pB = [], [], [], [], []
    for _ in range(TRIALS):
        re_, rl_, ppa, ppb = simulate_cohort()
        early.append(re_)
        late.append(rl_)
        lift.append(rl_ - re_)
        pA.append(ppa)
        pB.append(ppb)

    e_m, e_s = mean_std(early)
    l_m, l_s = mean_std(late)
    d_m, d_s = mean_std(lift)
    pa_m, pa_s = mean_std(pA)
    pb_m, pb_s = mean_std(pB)

    def se(sd):
        return sd / math.sqrt(TRIALS)

    d_se = se(d_s)
    e_se = se(e_s)
    l_se = se(l_s)
    pa_se = se(pa_s)
    pb_se = se(pb_s)

    cf0 = r_cf(0)
    cf_late = r_cf(T_LATE)

    # G1: survivorship lift (headline) -- mean observed lift >= LIFT_MIN by >=3 sigma
    z1 = (d_m - LIFT_MIN) / d_se if d_se > 0 else float("inf")
    g1 = d_m >= LIFT_MIN and z1 >= SIGMA

    # G2: individual-constant control -- pooled within-segment retention matches the
    # constant hazard r_A and r_B (|z| < 3): no customer's retention rises with tenure.
    z2a = abs(pa_m - R_A) / pa_se if pa_se > 0 else 0.0
    z2b = abs(pb_m - R_B) / pb_se if pb_se > 0 else 0.0
    g2 = z2a < SIGMA and z2b < SIGMA

    # G3: closed-form anchor MATCH -- observed R_obs(t) matches the mixture formula
    # R_cf(t) at t=0 and t=T_LATE (|z| < 3): the rise is exactly the survivor mixture.
    z3a = abs(e_m - cf0) / e_se if e_se > 0 else 0.0
    z3b = abs(l_m - cf_late) / l_se if l_se > 0 else 0.0
    g3 = z3a < SIGMA and z3b < SIGMA

    results = {
        "proposal": 106,
        "domain": "venture",
        "slot": "round-24-venture",
        "seed": SEED,
        "N": N,
        "T": T,
        "trials": TRIALS,
        "sigma": SIGMA,
        "t_late": T_LATE,
        "params": {
            "W_A": WA_EFF, "W_B": WB_EFF, "R_A": R_A, "R_B": R_B,
            "N_A": N_A, "N_B": N_B, "LIFT_MIN": LIFT_MIN,
        },
        "observed": {
            "R_early_mean": round(e_m, 6), "R_early_se": round(e_se, 6),
            "R_late_mean": round(l_m, 6), "R_late_se": round(l_se, 6),
            "lift_mean": round(d_m, 6), "lift_se": round(d_se, 6),
            "pooled_A_mean": round(pa_m, 6), "pooled_A_se": round(pa_se, 6),
            "pooled_B_mean": round(pb_m, 6), "pooled_B_se": round(pb_se, 6),
        },
        "closed_form": {
            "R_cf_0": round(cf0, 6),
            "R_cf_late": round(cf_late, 6),
            "lift_cf": round(cf_late - cf0, 6),
            "asymptote": max(R_A, R_B),
        },
        "gates": {
            "G1_survivorship_lift": {
                "stat": "mean_observed_lift", "mean": round(d_m, 6),
                "se": round(d_se, 6), "threshold": LIFT_MIN,
                "z": round(z1, 4), "pass": g1,
            },
            "G2_individual_constant": {
                "stat": "pooled_segment_retention",
                "z_A": round(z2a, 4), "z_B": round(z2b, 4),
                "r_A": R_A, "r_B": R_B, "pass": g2,
            },
            "G3_anchor_match": {
                "stat": "R_obs_vs_R_cf",
                "z_t0": round(z3a, 4), "z_late": round(z3b, 4), "pass": g3,
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
        f"R_early={obs['R_early_mean']} -> R_late(t={T_LATE})={obs['R_late_mean']} "
        f"lift={obs['lift_mean']}  (closed-form {cf['R_cf_0']} -> {cf['R_cf_late']}, "
        f"asymptote {cf['asymptote']})"
    )
    for name, g in results["gates"].items():
        print(f"{name}: pass={g['pass']}  {g}")
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
