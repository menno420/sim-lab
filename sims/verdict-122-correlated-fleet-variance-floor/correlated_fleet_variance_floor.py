#!/usr/bin/env python3
"""PROPOSAL 109 - The correlated-fleet variance floor.

FLEET-domain mechanism (round-25 fleet slot). Multi-agent estimation /
wisdom-of-crowds economics.

Trap / counterintuitive result
------------------------------
A fleet of N agents each estimates a common truth theta (WLOG theta=0). Agent
i's error is

    eps_i = sqrt(rho) * C  +  sqrt(1-rho) * Z_i

with a SHARED common-mode draw C ~ N(0, sigma^2) (identical for every agent -
same config, same upstream, same training prior) and an idiosyncratic
Z_i ~ N(0, sigma^2) iid. Then Var(eps_i)=sigma^2 and Corr(eps_i,eps_j)=rho.

Naive "wisdom of crowds": averaging N estimates cuts the error variance to
sigma^2 / N -> 0, so a big fleet is an arbitrarily accurate fleet. It is not.
The fleet-mean error is E = sqrt(rho)*C + sqrt(1-rho)*mean(Z), whose variance is
the exact equicorrelation formula

    MSE_N(rho) = rho*sigma^2 + (1-rho)*sigma^2 / N   ->  rho*sigma^2   (N->inf)

so the aggregate mean-squared error FLOORS at rho*sigma^2 no matter how many
agents you add, and the effective independent count saturates at

    N_eff = sigma^2 / MSE_N  ->  1 / rho.

On the pinned world (rho=0.25, N=400, sigma=1) the floor is 0.251875 while
independence predicts 0.0025: a fleet of 400 correlated agents is worth only
~3.97 independent ones, and ~99% of the promised variance reduction never
materializes. Adding agents past N ~ 1/rho buys essentially nothing.

Gates (each an effect >= 3 sigma on the /se margin, over T pinned trials):
  G1  correlated floor        mean(MSE_corr)             >= 0.10   (headline)
  G2  correlation-necessity   mean(MSE_indep) vs sigma^2/N   |z| < 3 (control)
  G3  closed-form anchor       mean(MSE_corr) vs rho*s^2+(1-rho)*s^2/N  |z| < 3

G2 is the isolating control: with rho=0 (no shared component) the SAME fleet
size collapses to sigma^2/N, so the floor in G1 is 100% the common-mode
correlation, not fleet size or a sim artifact. Gate z-scores are computed on
the ESTIMATED MEAN via its standard error (se=std/sqrt(TRIALS)) - the
P104/P105/P106/P107/P108 /se convention.

Determinism: SEED pinned; a canonical results dict is hashed with sha256 and
must reproduce byte-for-byte across runs. Exit 0 iff all gates pass.
"""

import hashlib
import json
import math
import random

SEED = 20260717
SIGMA_ERR = 1.0     # per-agent error std (sigma); sigma^2 = 1
RHO = 0.25          # equicorrelation of agent errors (shared common-mode share)
N_FLEET = 400       # agents in the fleet
TRIALS = 400        # pinned outer Monte-Carlo trials
BATCH = 200         # fleet realizations averaged per trial
SIGMA = 3.0         # gate strength

G1_FLOOR = 0.10     # correlated-MSE floor (headline)

# closed-form anchors (sigma^2 = SIGMA_ERR**2)
S2 = SIGMA_ERR ** 2
MSE_CORR_CF = RHO * S2 + (1.0 - RHO) * S2 / N_FLEET          # 0.251875
MSE_INDEP_CF = S2 / N_FLEET                                  # 0.0025
NEFF_CF = S2 / MSE_CORR_CF                                   # ~3.9702  (-> 1/rho)


def fleet_mse_trial(rng, rho, n, batch):
    """Mean squared aggregate error of a rho-equicorrelated N-agent fleet.

    One trial = mean of E^2 over `batch` independent fleet realizations, where
    E = sqrt(rho)*C + sqrt(1-rho)*mean(Z_1..Z_n) is the fleet-mean error
    (truth theta=0). Idiosyncratic errors are averaged EXPLICITLY over the n
    agents, so the 1/n variance reduction emerges from the fleet, not asserted.
    """
    a = math.sqrt(rho)
    b = math.sqrt(1.0 - rho)
    inv_n = 1.0 / n
    acc = 0.0
    for _ in range(batch):
        c = rng.gauss(0.0, SIGMA_ERR)          # shared common-mode draw
        zsum = 0.0
        for _ in range(n):
            zsum += rng.gauss(0.0, SIGMA_ERR)  # idiosyncratic per-agent error
        zbar = zsum * inv_n
        e = a * c + b * zbar                   # fleet-mean error
        acc += e * e
    return acc / batch


def mean_std(xs):
    m = sum(xs) / len(xs)
    if len(xs) < 2:
        return m, 0.0
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return m, math.sqrt(var)


def run():
    rng = random.Random(SEED)

    # correlated fleet (rho > 0) -- primary
    corr = [fleet_mse_trial(rng, RHO, N_FLEET, BATCH) for _ in range(TRIALS)]
    # independent control (rho = 0), SAME fleet size
    indep = [fleet_mse_trial(rng, 0.0, N_FLEET, BATCH) for _ in range(TRIALS)]

    corr_m, corr_s = mean_std(corr)
    ind_m, ind_s = mean_std(indep)

    corr_se = corr_s / math.sqrt(TRIALS)
    ind_se = ind_s / math.sqrt(TRIALS)

    # G1: correlated floor bounded away from G1_FLOOR from ABOVE
    z1 = (corr_m - G1_FLOOR) / corr_se if corr_se > 0 else float("inf")
    g1 = corr_m >= G1_FLOOR and z1 >= SIGMA

    # G2: control -- rho=0 MSE matches sigma^2/N (floor vanishes), |z| < 3
    z2 = (ind_m - MSE_INDEP_CF) / ind_se if ind_se > 0 else float("inf")
    g2 = abs(z2) < SIGMA

    # G3: closed-form anchor -- correlated MSE matches equicorrelation formula
    z3 = (corr_m - MSE_CORR_CF) / corr_se if corr_se > 0 else float("inf")
    g3 = abs(z3) < SIGMA

    neff_sim = S2 / corr_m if corr_m > 0 else float("inf")

    results = {
        "proposal": 109,
        "domain": "fleet",
        "slot": "round-25-fleet",
        "seed": SEED,
        "sigma_err": SIGMA_ERR,
        "rho": RHO,
        "N_fleet": N_FLEET,
        "trials": TRIALS,
        "batch": BATCH,
        "sigma": SIGMA,
        "gates": {
            "G1_correlated_floor": {
                "stat": "mean_mse_corr", "mean": round(corr_m, 6),
                "std": round(corr_s, 6), "se": round(corr_se, 6),
                "threshold": G1_FLOOR, "z": round(z1, 4), "pass": g1,
            },
            "G2_correlation_necessity": {
                "stat": "mean_mse_indep", "mean": round(ind_m, 6),
                "std": round(ind_s, 6), "se": round(ind_se, 6),
                "anchor": round(MSE_INDEP_CF, 6), "z": round(z2, 4), "pass": g2,
            },
            "G3_closed_form_anchor": {
                "stat": "mean_mse_corr", "mean": round(corr_m, 6),
                "std": round(corr_s, 6), "se": round(corr_se, 6),
                "anchor": round(MSE_CORR_CF, 6), "z": round(z3, 4), "pass": g3,
            },
        },
        "theory": {
            "mse_corr_closed_form": round(MSE_CORR_CF, 6),
            "mse_indep_closed_form": round(MSE_INDEP_CF, 6),
            "neff_closed_form": round(NEFF_CF, 6),
            "neff_asymptote": round(1.0 / RHO, 6),
            "neff_sim": round(neff_sim, 6),
        },
        "all_pass": bool(g1 and g2 and g3),
    }
    return results


def main():
    results = run()
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    out = {"results": results, "sha256": digest}
    with open("correlated_fleet_variance_floor_results.json", "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(canonical)
    print("sha256:", digest)
    for name, g in results["gates"].items():
        print(f"{name}: mean={g['mean']} z={g['z']} pass={g['pass']}")
    print("N_eff(sim):", results["theory"]["neff_sim"],
          "-> asymptote 1/rho =", results["theory"]["neff_asymptote"])
    print("ALL_PASS:", results["all_pass"])
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
