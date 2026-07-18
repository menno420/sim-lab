#!/usr/bin/env python3
"""guild_volunteer_dilemma.py — reference simulation for PROPOSAL 127.

A guild/raid "someone-must-do-it" chore (soak a mechanic, farm the reagent,
staff the event, hit a shared contribution threshold) is a VOLUNTEER'S DILEMMA:
the collective reward is provided iff AT LEAST ONE member pays a private cost c
for a common benefit b (0 < c < b). The folk belief is "more members => more
likely someone does it." The symmetric mixed-strategy Nash equilibrium says the
opposite: each member volunteers with probability p*(N) = 1 - (c/b)^(1/(N-1)),
so the probability NOBODY volunteers is P_fail(N) = (c/b)^(N/(N-1)), which
INCREASES in N toward c/b — the bystander effect / diffusion of responsibility
emerging from rational play, not apathy. Stdlib-only (random, math, json,
hashlib).

Anchor: A. Diekmann, "Volunteer's Dilemma", Journal of Conflict Resolution
29(4), 1985; the bystander effect (Darley & Latane 1968).

Model (paired, common random numbers):
  - N members, each independently volunteers w.p. p*(N) (the symmetric eq).
  - Provision fails iff no member volunteers.
  - Fixed-rate CONTROL: every member volunteers at the SMALL-GROUP rate
    p0 = p*(N_LO) regardless of N (non-re-optimizing players); its failure
    rate (1-p0)^N DECREASES in N (the folk belief) — the sign-flip specificity.
  - A shared per-trial uniform vector u (length N_MAX) drives every N and both
    the strategic and control measurements (common random numbers => the paired
    dose differences are coupled / low variance).

Gates (APPROVE iff G1 AND G2 AND G3, in order):
  G1 existence   : mean(fail[N_HI] - fail[N_LO]) > 0 with z = mean/se >= SIGMA
                   (the bystander effect: adding members raises P(nobody acts)).
  G2 control     : the fixed-rate control FLIPS the sign —
                   mean(fail0[N_HI] - fail0[N_LO]) < 0 with z <= -SIGMA
                   (more members lowers failure ONLY without strategic
                   re-optimization; the rise is caused by equilibrium dilution,
                   not by group size per se).
  G3 anchor      : the strategic failure rate reproduces the exact equilibrium
                   closed form P_fail(N) = (c/b)^(N/(N-1)) at N_LO/N_STAR/N_HI
                   (each |z| < SIGMA), the mean volunteer count at N_HI matches
                   N_HI * p*(N_HI) (|z| < SIGMA) and stays ~constant near
                   -ln(c/b) (total effort does not scale with the roster), and
                   the failure rate is monotone increasing across N_GRID.
"""
import random, math, json, hashlib

SEED = 20260717
TRIALS = 200_000
BENEFIT = 1.0
COST = 0.5
R = COST / BENEFIT            # = c/b, the pivotal-cost ratio (0 < R < 1)
N_LO = 2
N_STAR = 10
N_HI = 20
N_GRID = [2, 3, 5, 8, 10, 15, 20]
N_MAX = max(N_GRID)
SIGMA_GATE = 3.0


def p_star(n):
    """Symmetric mixed-strategy volunteer probability at group size n."""
    return 1.0 - R ** (1.0 / (n - 1))


def p_fail_theory(n):
    """Equilibrium probability that NOBODY volunteers = (c/b)^(n/(n-1))."""
    return R ** (n / (n - 1))


def run():
    rng = random.Random(SEED)
    p_eq = {n: p_star(n) for n in N_GRID}
    p0 = p_star(N_LO)  # fixed control rate (small-group equilibrium rate)

    sum_fail = {n: 0.0 for n in N_GRID}     # strategic failure indicator
    sum_fail0 = {n: 0.0 for n in N_GRID}    # fixed-rate control failure indicator
    sum_vol = {n: 0.0 for n in N_GRID}      # strategic volunteer count
    sumsq_vol = {n: 0.0 for n in N_GRID}
    sum_g1 = sumsq_g1 = 0.0                 # paired fail[N_HI]-fail[N_LO] (strategic)
    sum_g2 = sumsq_g2 = 0.0                 # paired fail0[N_HI]-fail0[N_LO] (control)

    for _ in range(TRIALS):
        u = [rng.random() for _ in range(N_MAX)]
        fail_lo = fail_hi = fail0_lo = fail0_hi = 0.0
        for n in N_GRID:
            thr = p_eq[n]
            vol = 0
            for i in range(n):
                if u[i] < thr:
                    vol += 1
            fail = 1.0 if vol == 0 else 0.0
            sum_fail[n] += fail
            sum_vol[n] += vol
            sumsq_vol[n] += vol * vol
            # fixed-rate control: same shared u, constant threshold p0
            vol0 = 0
            for i in range(n):
                if u[i] < p0:
                    vol0 += 1
            fail0 = 1.0 if vol0 == 0 else 0.0
            sum_fail0[n] += fail0
            if n == N_LO:
                fail_lo, fail0_lo = fail, fail0
            if n == N_HI:
                fail_hi, fail0_hi = fail, fail0
        d1 = fail_hi - fail_lo
        sum_g1 += d1
        sumsq_g1 += d1 * d1
        d2 = fail0_hi - fail0_lo
        sum_g2 += d2
        sumsq_g2 += d2 * d2

    n = TRIALS

    def mean_se(s, ss):
        mean = s / n
        var = max(ss / n - mean * mean, 0.0)
        se = math.sqrt(var / n)
        return mean, se

    def frac_mean_se(s):
        mean = s / n
        var = max(mean - mean * mean, 0.0)  # Bernoulli: E[X^2]=E[X]
        se = math.sqrt(var / n)
        return mean, se

    g1_mean, g1_se = mean_se(sum_g1, sumsq_g1)
    z_g1 = g1_mean / g1_se if g1_se > 0 else 0.0
    g2_mean, g2_se = mean_se(sum_g2, sumsq_g2)
    z_g2 = g2_mean / g2_se if g2_se > 0 else 0.0

    # G3 (a) closed-form failure-rate anchors at N_LO/N_STAR/N_HI
    anchor = {}
    max_abs_anchor_z = 0.0
    for n_ in (N_LO, N_STAR, N_HI):
        m, se = frac_mean_se(sum_fail[n_])
        th = p_fail_theory(n_)
        z = (m - th) / se if se > 0 else 0.0
        anchor[n_] = (round(m, 8), round(th, 8), round(z, 4))
        if abs(z) > max_abs_anchor_z:
            max_abs_anchor_z = abs(z)

    # G3 (b) constant-effort: mean volunteer count at N_HI vs N_HI*p*(N_HI)
    vol_hi_mean, vol_hi_se = mean_se(sum_vol[N_HI], sumsq_vol[N_HI])
    vol_hi_theory = N_HI * p_eq[N_HI]
    z_vol = (vol_hi_mean - vol_hi_theory) / vol_hi_se if vol_hi_se > 0 else 0.0

    # G3 (c) monotone increasing failure rate across the grid
    fail_curve = {n_: round(sum_fail[n_] / n, 8) for n_ in N_GRID}
    seq = [fail_curve[n_] for n_ in N_GRID]
    grid_monotone_increasing = all(seq[i + 1] > seq[i] for i in range(len(seq) - 1))

    g1 = (g1_mean > 0.0) and (z_g1 >= SIGMA_GATE)
    g2 = (g2_mean < 0.0) and (z_g2 <= -SIGMA_GATE)
    g3 = (max_abs_anchor_z < SIGMA_GATE) and (abs(z_vol) < SIGMA_GATE) and grid_monotone_increasing
    all_pass = g1 and g2 and g3

    return {
        "seed": SEED,
        "trials": TRIALS,
        "benefit": BENEFIT,
        "cost": COST,
        "r_ratio": round(R, 8),
        "sigma_gate": SIGMA_GATE,
        "n_grid": N_GRID,
        "n_lo": N_LO,
        "n_star": N_STAR,
        "n_hi": N_HI,
        "p_star_lo": round(p_eq[N_LO], 8),
        "p_star_star": round(p_eq[N_STAR], 8),
        "p_star_hi": round(p_eq[N_HI], 8),
        "fail_curve": fail_curve,
        "fail_lo": round(sum_fail[N_LO] / n, 8),
        "fail_star": round(sum_fail[N_STAR] / n, 8),
        "fail_hi": round(sum_fail[N_HI] / n, 8),
        "g1_bystander_mean": round(g1_mean, 8),
        "z_g1_existence": round(z_g1, 4),
        "g2_control_mean": round(g2_mean, 8),
        "z_g2_control": round(z_g2, 4),
        "anchor_lo": anchor[N_LO],
        "anchor_star": anchor[N_STAR],
        "anchor_hi": anchor[N_HI],
        "max_abs_anchor_z": round(max_abs_anchor_z, 4),
        "vol_hi_mean": round(vol_hi_mean, 8),
        "vol_hi_theory": round(vol_hi_theory, 8),
        "z_vol_hi": round(z_vol, 4),
        "neg_ln_r": round(-math.log(R), 8),
        "grid_monotone_increasing": grid_monotone_increasing,
        "g1_existence": g1,
        "g2_control": g2,
        "g3_anchor": g3,
        "all_pass": all_pass,
    }


def main():
    results = run()
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    print("G1 existence :", "PASS" if results["g1_existence"] else "FAIL", "z=%.4f" % results["z_g1_existence"])
    print("G2 control   :", "PASS" if results["g2_control"] else "FAIL", "z=%.4f" % results["z_g2_control"])
    print("G3 anchor    :", "PASS" if results["g3_anchor"] else "FAIL",
          "max|anchor z|=%.4f" % results["max_abs_anchor_z"], "z_vol=%.4f" % results["z_vol_hi"])
    print("ALL_PASS     :", results["all_pass"])
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
