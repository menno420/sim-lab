#!/usr/bin/env python3
"""PROPOSAL 118 - The sales-ramp capacity drag (growth/attrition interchangeability).

VENTURE-domain mechanism (round-27 venture slot). Sales-capacity planning /
go-to-market unit economics.

Trap / counterintuitive result
------------------------------
A new sales rep does not book at full quota on day one: productivity RAMPS from
zero to full quota Q over a ramp period R (onboarding, territory build,
pipeline maturation). Model the ramp as linear: a rep of tenure a books

    q(a) = Q * min(a / R, 1).

In a firm whose headcount GROWS at monthly rate g and whose reps leave at monthly
attrition rate d (delta), the steady-state tenure distribution of the CURRENTLY
ACTIVE force is exponential with rate beta = g + d (Lotka stable-population age
structure: cohort hired a months ago numbered ~ e^{g(t-a)}, survivors to now
~ e^{-d*a}, so active tenure density is (g+d)*e^{-(g+d)a}). Averaging q(a) over
that distribution gives the realized fraction of nominal quota the force actually
books:

    phi(beta) = E[min(a/R, 1)] = (1 - e^{-beta*R}) / (beta * R),   beta = g + d,

the classic (1 - e^{-x})/x form -- always < 1, and DECREASING in beta. So:

  1. Nominal capacity (headcount * quota) systematically OVERSTATES realized
     bookings by the factor 1/phi, and the overstatement WIDENS the faster you
     grow -- "hire ahead of the number" dilutes per-rep productivity because a
     larger share of the force is still ramping.

  2. Growth and attrition are INTERCHANGEABLE: phi depends only on beta = g + d,
     so an over-hiring problem (+Delta on g) and a retention problem (+Delta on d)
     inflict the IDENTICAL capacity drag. You cannot tell them apart from the
     aggregate productivity number -- the drag from growing Delta faster equals
     the drag from churning Delta faster, exactly.

The trap: leaders read a falling bookings-per-rep number as a coaching / talent
problem and pour in MORE hiring, which raises g, which lowers phi further. The
fix is to plan capacity on realized phi(g+d)*Q per rep (not nominal quota), cap
the hiring GROWTH RATE against the ramp R, and treat attrition reduction as
exactly equivalent to slowing over-hiring (same beta lever).

Gates (each an effect vs its threshold at >= SIGMA; z is on the ESTIMATED MEAN
via its standard error se = std/sqrt(TRIALS), the P104..P117 /se convention):
  G1  growth capacity drag (headline)  mean(phi_slow - phi_fast)        >= GAP_MIN
  G2  attrition-interchangeability     mean(phi_slow - phi_attr_hi)     >= GAP_MIN
      (a +Delta attrition bump, matched so beta == beta_fast, drags identically)
  G3  closed-form anchor MATCH         sim phi(beta_slow), phi(beta_fast)
                                       match (1-e^{-beta*R})/(beta*R)   (|z| < 3)

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
N_REPS = 20000      # reps sampled per trial (steady-state active force)

Q = 1.0             # full-ramp monthly quota (normalized; bookings as a fraction of quota)
R = 6.0             # ramp period in months (0 -> full productivity over R months)

DELTA_LOW = 0.03    # baseline monthly rep attrition (~30%/yr)
DELTA_HI = 0.10     # raised attrition for the interchangeability control (= DELTA_LOW + (G_FAST - G_SLOW))
G_SLOW = 0.01       # slow monthly headcount growth (~12.7%/yr)
G_FAST = 0.08       # fast monthly headcount growth (~2.6x/yr -- aggressive scale-up)

GAP_MIN = 0.05      # honest floor: the productivity drag must clear at least this many quota-fractions

# Total force-turnover rates beta = g + d (the only thing phi depends on).
BETA_SLOW = G_SLOW + DELTA_LOW    # 0.04
BETA_FAST = G_FAST + DELTA_LOW    # 0.11
BETA_ATTR = G_SLOW + DELTA_HI     # 0.11  (matched to BETA_FAST -> identical drag: growth<->attrition)


def phi_cf(beta):
    """Closed-form realized quota fraction: E[min(a/R,1)] for a ~ Exp(beta)."""
    x = beta * R
    return (1.0 - math.exp(-x)) / x


def phi_sample(beta):
    """One trial's sample realized productivity: mean over N_REPS active reps whose
    tenure a ~ Exp(beta), each booking Q*min(a/R,1)."""
    total = 0.0
    for _ in range(N_REPS):
        a = random.expovariate(beta)
        total += Q * (a / R if a < R else 1.0)
    return total / N_REPS


def mean_std(xs):
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var)


def run():
    random.seed(SEED)

    phi_slow, phi_fast, phi_attr = [], [], []
    for _ in range(TRIALS):
        # Fixed draw order per trial -> deterministic.
        phi_slow.append(phi_sample(BETA_SLOW))
        phi_fast.append(phi_sample(BETA_FAST))
        phi_attr.append(phi_sample(BETA_ATTR))

    def se(sd):
        return sd / math.sqrt(TRIALS)

    slow_m, slow_s = mean_std(phi_slow)
    fast_m, fast_s = mean_std(phi_fast)
    attr_m, attr_s = mean_std(phi_attr)
    slow_se, fast_se, attr_se = se(slow_s), se(fast_s), se(attr_s)

    # G1: growing faster strictly and substantially lowers realized productivity.
    g1_gap = [s - f for s, f in zip(phi_slow, phi_fast)]
    g1_m, g1_s = mean_std(g1_gap)
    g1_se = se(g1_s)
    z1 = (g1_m - GAP_MIN) / g1_se if g1_se > 0 else float("inf")
    g1 = g1_m >= GAP_MIN and z1 >= SIGMA

    # G2: a matched attrition bump (beta_attr == beta_fast) drags IDENTICALLY.
    g2_gap = [s - a for s, a in zip(phi_slow, phi_attr)]
    g2_m, g2_s = mean_std(g2_gap)
    g2_se = se(g2_s)
    z2 = (g2_m - GAP_MIN) / g2_se if g2_se > 0 else float("inf")
    g2 = g2_m >= GAP_MIN and z2 >= SIGMA

    # G3: sim phi matches the closed form (1-e^{-beta*R})/(beta*R) at both regimes.
    cf_slow = phi_cf(BETA_SLOW)
    cf_fast = phi_cf(BETA_FAST)
    z3a = abs(slow_m - cf_slow) / slow_se if slow_se > 0 else 0.0
    z3b = abs(fast_m - cf_fast) / fast_se if fast_se > 0 else 0.0
    g3 = z3a < SIGMA and z3b < SIGMA

    # Descriptive: growth<->attrition interchangeability -- fast and attr share beta.
    interchange_abs_diff = abs(fast_m - attr_m)

    results = {
        "proposal": 118,
        "domain": "venture",
        "slot": "round-27-venture",
        "seed": SEED,
        "trials": TRIALS,
        "sigma": SIGMA,
        "params": {
            "Q": Q, "R": R, "N_REPS": N_REPS,
            "delta_low": DELTA_LOW, "delta_hi": DELTA_HI,
            "g_slow": G_SLOW, "g_fast": G_FAST, "GAP_MIN": GAP_MIN,
            "beta_slow": round(BETA_SLOW, 6), "beta_fast": round(BETA_FAST, 6),
            "beta_attr": round(BETA_ATTR, 6),
        },
        "observed": {
            "phi_slow_mean": round(slow_m, 6), "phi_slow_se": round(slow_se, 6),
            "phi_fast_mean": round(fast_m, 6), "phi_fast_se": round(fast_se, 6),
            "phi_attr_mean": round(attr_m, 6), "phi_attr_se": round(attr_se, 6),
            "g1_growth_gap_mean": round(g1_m, 6), "g1_growth_gap_se": round(g1_se, 6),
            "g2_attrition_gap_mean": round(g2_m, 6), "g2_attrition_gap_se": round(g2_se, 6),
            "interchange_abs_diff": round(interchange_abs_diff, 6),
        },
        "closed_form": {
            "phi_slow_cf": round(cf_slow, 6),
            "phi_fast_cf": round(cf_fast, 6),
            "gap_cf": round(cf_slow - cf_fast, 6),
        },
        "gates": {
            "G1_growth_capacity_drag": {
                "stat": "mean_phi_slow_minus_fast", "mean": round(g1_m, 6),
                "se": round(g1_se, 6), "threshold": GAP_MIN,
                "z": round(z1, 4), "pass": g1,
            },
            "G2_attrition_interchangeability": {
                "stat": "mean_phi_slow_minus_attr_hi", "mean": round(g2_m, 6),
                "se": round(g2_se, 6), "threshold": GAP_MIN,
                "z": round(z2, 4), "pass": g2,
            },
            "G3_anchor_match": {
                "stat": "sim_vs_closed_form",
                "z_phi_slow": round(z3a, 4), "z_phi_fast": round(z3b, 4), "pass": g3,
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
        f"realized productivity: phi_slow(beta={results['params']['beta_slow']})={obs['phi_slow_mean']} "
        f"-> phi_fast(beta={results['params']['beta_fast']})={obs['phi_fast_mean']}  "
        f"(growing faster drags {obs['g1_growth_gap_mean']} of quota per rep)  |  "
        f"matched attrition bump drags {obs['g2_attrition_gap_mean']} (interchangeable; "
        f"fast vs attr differ by only {obs['interchange_abs_diff']})  |  closed-form gap {cf['gap_cf']}"
    )
    for name, g in results["gates"].items():
        print(f"{name}: pass={g['pass']}  {g}")
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
