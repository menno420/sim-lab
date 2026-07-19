#!/usr/bin/env python3
"""
memoryless_pm_waste.py -- firsthand verifier for PROPOSAL 165 (round-39 FLEET slot).

PHENOMENON
    Age-based preventive replacement (PM) of a fleet component whose lifetime is
    memoryless (exponential, constant hazard) does NOT reduce the rate of
    unplanned failures -- it leaves it at exactly lambda -- while strictly raising
    the long-run cost rate. Every dollar spent on PM of a random-failure item is
    pure waste. Age replacement pays off ONLY for wear-out (increasing-hazard) units.

FOLK BELIEF
    "Preventive maintenance always reduces failures: swap the part before it
    breaks and you will see fewer unplanned outages." For a constant-hazard part
    this is false -- memorylessness means a survived unit is as good as new, so
    replacing it early buys nothing.

THESIS (head claim, directional)
    Under an exponential lifetime, an age-replacement policy at any finite
    threshold T:
      (a) costs strictly MORE per unit time than run-to-failure (>= 3 sigma), and
      (b) delivers ZERO reduction in the unplanned-failure rate -- a promised
          10%-of-lambda reduction is rejected at >= 3 sigma.
    Both hold under a shifted parameterisation (robustness). The paradox
    dissolves for a Weibull wear-out lifetime (disclosed crossover, non-gated).

FORMAL MODEL (age-replacement renewal reward)
    Lifetime L ~ Exp(lambda). Policy(T): renew at min(L, T). If L <= T the renewal
    is an unplanned failure (cost c_fail); else a planned replacement (cost c_plan),
    c_fail > c_plan. Long-run cost rate = E[cost per cycle]/E[cycle length];
    long-run failure rate = P(L<=T)/E[cycle length]. For the exponential,
    E[cycle]=(1-e^-{lambda T})/lambda and P(L<=T)=1-e^-{lambda T}, so the failure
    rate = lambda for EVERY T (invariance), while the cost rate strictly rises as
    T shrinks. Run-to-failure is the T->inf limit.

PRE-REGISTERED GATES (z_gate = 3.0)
    G1  cost penalty:   cost_rate(PM) - cost_rate(RTF) > 0 at >= 3 sigma.
    G2  benefit absent: a promised 10%-of-lambda failure-rate reduction is rejected;
                        (0.10*lambda - observed_reduction)/se >= 3 sigma.
    G3  robustness:     under a shifted (lambda', costs', T') exponential, G1 and G2
                        both still hold at >= 3 sigma.
    Non-gated diagnostic: Weibull(shape=2.5, same mean) admits a finite T* that
                        BEATS run-to-failure -- the crossover that bounds the claim.

DIGEST POSTURE
    WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY: run() twice in-process, assert the
    canonical sha256 of the rounded results dict is identical, print the dict
    (indent=2, sorted, 6 dp) and its sha256. No file writes.
"""

import math
import json
import hashlib
import random

SEED = 20260717
Z_GATE = 3.0

# --- baseline world (committed constants) ---
LAM = 1.0            # exponential failure rate (mean life = 1.0 time unit)
T_PM = 0.5           # age-replacement threshold (finite, < mean life)
C_PLAN = 1.0         # planned-replacement cost
C_FAIL = 5.0         # unplanned-failure cost (c_fail > c_plan)
DELTA_NULL = 0.10    # strawman: PM is "supposed" to cut failure rate by 10% of lambda

# --- shifted world for the robustness gate (different rate, costs, threshold) ---
LAM_S = 1.7
T_PM_S = 0.3
C_PLAN_S = 1.0
C_FAIL_S = 8.0

# --- Weibull wear-out contrast (non-gated crossover diagnostic) ---
WB_SHAPE = 2.5       # increasing hazard (wear-out)

N_CYCLES = 100_000   # renewal cycles per replicate
TRIALS = 30          # independent replicates -> sampling distribution


def _sim_policy(rng, n_cycles, lam, t_pm, c_plan, c_fail):
    """One replicate of the age-replacement policy. Returns (cost_rate, failure_rate)."""
    tot_time = 0.0
    tot_cost = 0.0
    tot_fail = 0
    for _ in range(n_cycles):
        life = rng.expovariate(lam)
        if life <= t_pm:
            tot_time += life
            tot_cost += c_fail
            tot_fail += 1
        else:
            tot_time += t_pm
            tot_cost += c_plan
    return tot_cost / tot_time, tot_fail / tot_time


def _sim_rtf(rng, n_cycles, lam, c_fail):
    """Run-to-failure: renew only at failure (T = inf)."""
    tot_time = 0.0
    tot_cost = 0.0
    tot_fail = 0
    for _ in range(n_cycles):
        life = rng.expovariate(lam)
        tot_time += life
        tot_cost += c_fail
        tot_fail += 1
    return tot_cost / tot_time, tot_fail / tot_time


def _mean_se(xs):
    n = len(xs)
    m = sum(xs) / n
    if n < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var / n)


def _world(rng, lam, t_pm, c_plan, c_fail):
    """TRIALS replicates of PM and RTF; return aggregate stats + z-margins."""
    pm_cost, pm_fail, rtf_cost, rtf_fail = [], [], [], []
    for _ in range(TRIALS):
        c, f = _sim_policy(rng, N_CYCLES, lam, t_pm, c_plan, c_fail)
        pm_cost.append(c)
        pm_fail.append(f)
        c, f = _sim_rtf(rng, N_CYCLES, lam, c_fail)
        rtf_cost.append(c)
        rtf_fail.append(f)
    pm_c_m, pm_c_se = _mean_se(pm_cost)
    rtf_c_m, rtf_c_se = _mean_se(rtf_cost)
    pm_f_m, pm_f_se = _mean_se(pm_fail)
    rtf_f_m, rtf_f_se = _mean_se(rtf_fail)

    dcost = pm_c_m - rtf_c_m
    dcost_se = math.sqrt(pm_c_se ** 2 + rtf_c_se ** 2)
    z_cost = dcost / dcost_se if dcost_se > 0 else float("inf")

    reduction = rtf_f_m - pm_f_m
    red_se = math.sqrt(pm_f_se ** 2 + rtf_f_se ** 2)
    promised = DELTA_NULL * lam
    z_benefit = (promised - reduction) / red_se if red_se > 0 else float("inf")

    return {
        "pm_cost_rate": pm_c_m,
        "rtf_cost_rate": rtf_c_m,
        "cost_penalty_pct": 100.0 * dcost / rtf_c_m,
        "z_cost": z_cost,
        "pm_failure_rate": pm_f_m,
        "rtf_failure_rate": rtf_f_m,
        "failure_rate_reduction": reduction,
        "promised_reduction": promised,
        "z_benefit": z_benefit,
    }


def _weibull_costrate(shape, lam_mean, t_pm, c_plan, c_fail):
    """Analytic long-run cost rate for a Weibull(shape) lifetime, mean matched to the
    exponential, age-replaced at t_pm. Trapezoid integration of E[cycle]."""
    scale = (1.0 / lam_mean) / math.gamma(1.0 + 1.0 / shape)

    def surv(t):
        return math.exp(-(t / scale) ** shape)

    steps = 20000
    h = t_pm / steps
    area = 0.5 * (surv(0.0) + surv(t_pm))
    for i in range(1, steps):
        area += surv(i * h)
    e_cycle = area * h
    ft = 1.0 - surv(t_pm)
    return (c_plan * surv(t_pm) + c_fail * ft) / e_cycle


def run():
    rng = random.Random(SEED)
    base = _world(rng, LAM, T_PM, C_PLAN, C_FAIL)
    shifted = _world(rng, LAM_S, T_PM_S, C_PLAN_S, C_FAIL_S)

    rtf_wb = LAM * C_FAIL
    best_t, best_rate = None, float("inf")
    t = 0.05
    while t <= 2.0 + 1e-9:
        r = _weibull_costrate(WB_SHAPE, LAM, t, C_PLAN, C_FAIL)
        if r < best_rate:
            best_rate, best_t = r, t
        t += 0.05
    weibull_beats_rtf = best_rate < rtf_wb

    g1 = base["z_cost"] >= Z_GATE and base["cost_penalty_pct"] > 0.0
    g2 = base["z_benefit"] >= Z_GATE
    g3 = (shifted["z_cost"] >= Z_GATE and shifted["z_benefit"] >= Z_GATE
          and shifted["cost_penalty_pct"] > 0.0)

    gates = {"G1_cost_penalty": g1, "G2_benefit_absent": g2, "G3_robustness": g3}
    order = ["G1_cost_penalty", "G2_benefit_absent", "G3_robustness"]
    first_failing = next((k for k in order if not gates[k]), None)

    return {
        "proposal": "PROPOSAL 165",
        "slot": "round-39 FLEET",
        "seed": SEED,
        "sigma_gate": Z_GATE,
        "params": {
            "lam": LAM, "t_pm": T_PM, "c_plan": C_PLAN, "c_fail": C_FAIL,
            "delta_null": DELTA_NULL, "lam_shift": LAM_S, "t_pm_shift": T_PM_S,
            "c_plan_shift": C_PLAN_S, "c_fail_shift": C_FAIL_S,
            "weibull_shape": WB_SHAPE, "n_cycles": N_CYCLES, "trials": TRIALS,
        },
        "base": base,
        "shifted": shifted,
        "theory": {
            "exp_failure_rate_invariant": LAM,
            "exp_pm_cost_rate": (C_PLAN * math.exp(-LAM * T_PM)
                                 + C_FAIL * (1 - math.exp(-LAM * T_PM)))
                                / ((1 - math.exp(-LAM * T_PM)) / LAM),
            "exp_rtf_cost_rate": LAM * C_FAIL,
        },
        "crossover": {
            "weibull_shape": WB_SHAPE,
            "weibull_best_t": best_t,
            "weibull_best_cost_rate": best_rate,
            "weibull_rtf_cost_rate": rtf_wb,
            "weibull_beats_rtf": weibull_beats_rtf,
        },
        "gates": gates,
        "first_failing_gate": first_failing,
        "all_pass": all(gates.values()),
    }


def _round_floats(o, ndigits=6):
    if isinstance(o, float):
        return round(o, ndigits)
    if isinstance(o, dict):
        return {k: _round_floats(v, ndigits) for k, v in o.items()}
    if isinstance(o, list):
        return [_round_floats(v, ndigits) for v in o]
    return o


def _canonical_sha256(o):
    return hashlib.sha256(
        json.dumps(o, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main():
    r1 = _round_floats(run())
    r2 = _round_floats(run())
    h1 = _canonical_sha256(r1)
    h2 = _canonical_sha256(r2)
    assert h1 == h2, "non-deterministic: %s != %s" % (h1, h2)
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + h1)
    raise SystemExit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
