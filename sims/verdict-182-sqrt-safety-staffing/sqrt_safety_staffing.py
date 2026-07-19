#!/usr/bin/env python3
"""
Square-root safety staffing (Halfin-Whitt QED regime) -- a fleet capacity law.

HEAD
----
To hold the probability that an arriving unit must wait fixed at a target alpha,
an M/M/c fleet needs only
        c = R + beta * sqrt(R)
servers, where R = lambda/mu is the offered load and beta is the "service grade"
solving the Halfin-Whitt limit
        alpha = 1 / (1 + beta * Phi(beta) / phi(beta)).
Consequences that upend the "utilization must trade off against delay" folk
belief:
  * Safety headroom (c - R) grows only as sqrt(R): per-unit slack
    (c - R)/R = beta/sqrt(R) -> 0.
  * Utilization rho = R/c = 1 - beta/sqrt(R) -> 1 as the fleet grows.
  * Yet the probability of delay stays bounded near alpha, NOT near 1:
    LARGER FLEETS SAFELY RUN HOTTER at essentially the same service grade.

GROUNDING
---------
Gans, Koole & Mandelbaum, "Telephone Call Centers: Tutorial, Review, and
Research Prospects", sec. 4.1.1 "Square-Root Safety Staffing", eqs (14)-(15):
  https://www.columbia.edu/~ww2040/tutorial.pdf
Eq (15): N = R + beta*sqrt(R).  Eq (14): P{Wait>0} ~ [1 + beta*Phi/phi]^-1.

METHOD (two independent lines of evidence)
------------------------------------------
1. Exact closed-form Erlang-C at every load (deterministic, no sampling): the
   rigorous evidence. It carries the high-utilization claim because the
   discrete-event relaxation time of an M/M/c queue grows like 1/(1-rho)^2, so a
   finite simulation cannot reach steady state at rho ~ 0.98 -- only the closed
   form is trustworthy there.
2. An M/G/c FCFS discrete-event simulation with independent replications and a
   warmup discard, run ONLY at loads where it reaches steady state (moderate
   rho). Independent replications give a VALID standard error (per-arrival
   indicators are autocorrelated, so a naive Bernoulli SE would be wrong). The
   simulation (a) corroborates Erlang-C where reliable and (b) extends the result
   to NON-exponential (hyperexponential) service, which has no closed form.

Pre-registered gates (z_gate = 3.0):
  G1  pooling decoupling (deterministic, exact Erlang-C at R_max): the largest
      fleet runs at utilization rho >= 0.95 yet exact P{wait} <= alpha + 0.02,
      far below the P{wait} = rho a single un-pooled M/M/1 server at the same
      utilization would suffer (gap rho - P{wait} >= 0.40); per-unit slack
      (c-R)/R < 0.05.
  G2  square-root staffing form (deterministic identity): headroom/sqrt(R)
      converges to beta at scale, |headroom(R_max)/sqrt(R_max) - beta| < 0.05.
  G3  robustness under a shifted service distribution (>=3 sigma, replicated
      DES at a steady-state-reachable load): under hyperexponential service
      (SCV > 1, same mean) the decoupling survives -- rho - mean P{wait} is
      >=3 sigma positive across replications and delay stays unsaturated
      (mean P{wait} < 0.9).

Determinism: every replication draws from its own random.Random(<int seed>), so
output is byte-identical in-process AND across invocations. run() is called
twice and the two canonical dicts are asserted identical; the sha256 of the
canonical results dict is the disclosed digest.
Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY.

Stdlib only.
"""

import hashlib
import heapq
import json
import math
import random
import statistics

SEED = 20260717
Z_GATE = 3.0
ALPHA_TARGET = 0.5
LEDGER_LOADS = [16, 64, 256, 1024]
DES_LOADS = [16, 64]
R_ROBUST = 64
REPS = 15
WARMUP = 15000
COUNT = 25000


def r6(x):
    return round(float(x), 6)


def _phi(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _Phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def halfin_whitt_delay(beta):
    return 1.0 / (1.0 + beta * _Phi(beta) / _phi(beta))


def solve_beta(alpha):
    lo, hi = 1e-9, 20.0
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if halfin_whitt_delay(mid) > alpha:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def erlang_c(c, R):
    B = 1.0
    for n in range(1, c + 1):
        B = (R * B) / (n + R * B)
    rho = R / c
    return B / (1.0 - rho + rho * B)


def min_servers_for_alpha(R, alpha):
    c = int(math.floor(R)) + 1
    while erlang_c(c, R) > alpha:
        c += 1
    return c


def exp_service(rng):
    return rng.expovariate(1.0)


def hyperexp_service(rng):
    p, m1 = 0.9, 0.2
    m2 = (1.0 - p * m1) / (1.0 - p)
    if rng.random() < p:
        return rng.expovariate(1.0 / m1)
    return rng.expovariate(1.0 / m2)


def simulate(seed, R, c, warmup, count, service):
    rng = random.Random(seed)
    lam = R
    free = [0.0] * c
    heapq.heapify(free)
    t = 0.0
    waited = 0
    total_service = 0.0
    t_count_start = None
    for k in range(warmup + count):
        t += rng.expovariate(lam)
        earliest = heapq.heappop(free)
        start = t if earliest <= t else earliest
        counted = k >= warmup
        if counted:
            if t_count_start is None:
                t_count_start = t
            if earliest > t:
                waited += 1
        s = service(rng)
        if counted:
            total_service += s
        heapq.heappush(free, start + s)
    p_wait = waited / count
    horizon = (t - t_count_start) if t_count_start is not None else t
    util = total_service / (c * horizon) if horizon > 0 else 0.0
    return p_wait, util


def des_estimate(base_seed, R, c, service):
    ps, us = [], []
    for j in range(REPS):
        p, u = simulate(base_seed + 1009 * j, R, c, WARMUP, COUNT, service)
        ps.append(p)
        us.append(u)
    mean = statistics.fmean(ps)
    se = statistics.stdev(ps) / math.sqrt(REPS)
    return mean, se, statistics.fmean(us)


def run():
    beta = solve_beta(ALPHA_TARGET)

    def staff(R):
        return int(math.ceil(R + beta * math.sqrt(R)))

    ledger = []
    for R in LEDGER_LOADS:
        c = staff(R)
        pw = erlang_c(c, R)
        ledger.append({
            "R": R,
            "c": c,
            "c_tight_exact": min_servers_for_alpha(R, ALPHA_TARGET),
            "headroom": c - R,
            "headroom_over_sqrtR": r6((c - R) / math.sqrt(R)),
            "rho": r6(R / c),
            "erlangC_pwait": r6(pw),
            "mm1_pwait_same_rho": r6(R / c),
            "per_unit_slack": r6((c - R) / R),
        })

    des = []
    for i, R in enumerate(DES_LOADS):
        c = staff(R)
        exact = erlang_c(c, R)
        me, see, ue = des_estimate(SEED + 100 + 17 * i, R, c, exp_service)
        mh, seh, uh = des_estimate(SEED + 900 + 17 * i, R, c, hyperexp_service)
        des.append({
            "R": R,
            "c": c,
            "rho": r6(R / c),
            "erlangC_pwait": r6(exact),
            "des_exp_pwait": r6(me),
            "des_exp_se": r6(see),
            "z_exp_vs_erlangC": r6((me - exact) / see) if see > 0 else 0.0,
            "des_exp_util": r6(ue),
            "des_h2_pwait": r6(mh),
            "des_h2_se": r6(seh),
            "des_h2_util": r6(uh),
        })

    big = ledger[-1]
    eff1 = big["mm1_pwait_same_rho"] - big["erlangC_pwait"]
    g1 = (big["rho"] >= 0.95) and (big["erlangC_pwait"] <= ALPHA_TARGET + 0.02) \
        and (eff1 >= 0.40) and (big["per_unit_slack"] < 0.05)

    gap = abs(big["headroom_over_sqrtR"] - beta)
    g2 = gap < 0.05

    rob = next(d for d in des if d["R"] == R_ROBUST)
    eff3 = rob["rho"] - rob["des_h2_pwait"]
    z3 = eff3 / rob["des_h2_se"] if rob["des_h2_se"] > 0 else 0.0
    g3 = (z3 >= Z_GATE) and (rob["des_h2_pwait"] < 0.9)

    des_matches_exact = all(abs(d["z_exp_vs_erlangC"]) < Z_GATE for d in des)

    all_pass = bool(g1 and g2 and g3)

    return {
        "meta": {
            "head": "square-root safety staffing: safety headroom ~ beta*sqrt(R), so larger fleets safely run hotter at a fixed delay grade",
            "seed": SEED,
            "z_gate": Z_GATE,
            "alpha_target": ALPHA_TARGET,
            "beta": r6(beta),
            "ledger_loads": list(LEDGER_LOADS),
            "des_loads": list(DES_LOADS),
            "reps": REPS,
            "warmup": WARMUP,
            "count": COUNT,
            "grounding": "https://www.columbia.edu/~ww2040/tutorial.pdf (Gans-Koole-Mandelbaum sec 4.1.1, eqs 14-15)",
        },
        "erlangC_ledger": ledger,
        "des_replicated": des,
        "gates": {
            "G1_pooling_decoupling_exact": {
                "R": big["R"], "rho": big["rho"],
                "erlangC_pwait": big["erlangC_pwait"],
                "mm1_pwait_same_rho": big["mm1_pwait_same_rho"],
                "effect": r6(eff1), "per_unit_slack": big["per_unit_slack"],
                "pass": bool(g1),
            },
            "G2_sqrt_staffing_form": {
                "beta": r6(beta),
                "headroom_over_sqrtR_at_Rmax": big["headroom_over_sqrtR"],
                "gap": r6(gap), "pass": bool(g2),
            },
            "G3_hyperexp_robustness_replicated": {
                "R": rob["R"], "rho": rob["rho"],
                "des_h2_pwait": rob["des_h2_pwait"], "des_h2_se": rob["des_h2_se"],
                "effect": r6(eff3), "z": r6(z3), "pass": bool(g3),
            },
        },
        "des_matches_exact_within_3sigma": bool(des_matches_exact),
        "all_pass": all_pass,
    }


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r1 = run()
    r2 = run()
    assert canonical(r1) == canonical(r2), "non-deterministic run()"
    digest = hashlib.sha256(canonical(r1).encode("utf-8")).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + digest)
    assert r1["all_pass"], "gates did not all pass"


if __name__ == "__main__":
    main()
