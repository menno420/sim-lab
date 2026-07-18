#!/usr/bin/env python3
"""
stein_shrinkage_dominance.py -- reference verifier for PROPOSAL 128 (round-29,
UNRELATED slot closer). Domain: mathematical statistics / decision theory --
STEIN'S PARADOX: for p >= 3 simultaneous normal-mean estimation problems the
James-Stein shrinkage estimator STRICTLY DOMINATES the sample mean (the MLE) in
total expected squared error, no matter what the true means are and even when the
p problems are completely UNRELATED. Fleet-external pure-mechanism head.

The "estimate each thing by its own measurement" trap. You observe p quantities,
each once, with unit-variance noise: X_i ~ Normal(theta_i, 1). The obvious answer
is the sample value itself -- the maximum-likelihood, unbiased estimator
theta_hat_i = X_i. Intuition says you cannot do better, and that borrowing
strength across UNRELATED coordinates (a batting average, the price of tea, a
proton mass) is meaningless. Stein (1956) / James-Stein (1961) proved that for
p >= 3 the MLE is INADMISSIBLE: the estimator

    theta_hat_JS = target + (1 - (p-2)/S) * (X - target),   S = ||X - target||^2

(shrinking every coordinate toward a common fixed point `target`) has strictly
SMALLER total risk R(theta_hat, theta) = E[ sum_i (theta_hat_i - theta_i)^2 ] than
the MLE for EVERY theta. The counterintuitive core: pooling p unrelated estimation
problems through one scalar shrinkage factor beats solving each separately.

Closed-form risks (unit noise, shrink toward the origin, lambda = ||theta||^2):
  R_MLE(theta)  = p                    (constant risk, every theta)
  R_JS(theta)   = p - (p-2)^2 * E[1/S],  S ~ noncentral chi-square_p(lambda)
                = p - (p-2)^2 * sum_k Pois(k; lambda/2) / (p + 2k - 2)   (p >= 3)
so R_JS < p for all theta when p >= 3, and at theta = 0 (lambda = 0) it collapses
to R_JS = p - (p-2) = 2 for EVERY dimension p -- ten unit-noise coordinates
estimated at total squared-error 2 instead of 10.

Gates (all on the /se margin, the P104..P127 convention -- z on an estimated
statistic via its standard error se = std / sqrt(TRIALS)):
  G1 existence (dominance headline): at p = DIM the paired advantage
     (risk_MLE - risk_JS, SAME X drives both estimators) EXCEEDS 0 by >= 3 sigma
     -- shrinkage strictly beats the sample mean in total squared error.
  G2 dose-response (more simultaneous estimates => bigger gain): the mean advantage
     GROWS from a low dimension DIM_LO to a high dimension DIM_HI by >= 3 sigma
     -- the shrinkage gain scales with the number of coordinates pooled.
  G3 specificity (the p >= 3 boundary is exact): at p = DIM_BOUNDARY = 2 the
     shrinkage factor 1 - (p-2)/S = 1 identically, so the James-Stein estimator
     EQUALS the MLE every trial and the advantage is EXACTLY 0 -- the dominance
     switches OFF precisely at the p < 3 boundary (a placebo control: no effect
     when the (p-2) coefficient zeroes the shrinkage).

Plus a closed-form ANCHOR cross-check (reported, not a gate): the simulated MLE
risk reproduces p and the simulated JS risk reproduces the noncentral-chi-square
closed form p - (p-2)^2 E[1/S] -- both to within 3 sigma.

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717          # proposal-owned pinned seed; SEEDLESS discipline
TRIALS = 200000          # independent trials per dimension (/se averages over these)
DIM = 10                 # headline dimension (p >= 3): the dominance measurement
DIM_LO = 3               # low dimension (the exact p >= 3 threshold) for the dose
DIM_HI = 20              # high dimension for the dose (gain grows with coordinates)
DIM_BOUNDARY = 2         # below-threshold control: (p-2)=0 => JS == MLE, advantage == 0
TAU = 1.0                # sd of each true mean theta_i (an "unrelated" spread vector)
NOISE_SD = 1.0           # per-coordinate observation noise sd (the unit-variance setup)
TARGET = 0.0             # common shrinkage target (shrink toward the origin)
SIGMA_GATE = 3.0         # pre-registered gate threshold (sigma)


def js_estimate(x, p, target):
    """James-Stein estimate: shrink every coordinate toward `target` by the scalar
    factor 1 - (p-2)/S, S = ||x - target||^2. At p=2 the factor is exactly 1 (JS==MLE)."""
    s = sum((xi - target) ** 2 for xi in x)
    factor = 0.0 if s == 0.0 else 1.0 - (p - 2) / s
    return [target + factor * (xi - target) for xi in x]


def run_dim(rng, theta, p):
    """TRIALS trials at dimension p with fixed true means theta[:p]. Each trial draws
    X ~ Normal(theta, NOISE_SD^2), then measures the total squared error of the MLE
    (X itself) and of the James-Stein estimate (paired: SAME X). Returns per-trial
    advantage (risk_MLE - risk_JS) list plus the mean MLE and JS risks."""
    th = theta[:p]
    adv = []
    sum_mle = 0.0
    sum_js = 0.0
    max_abs_adv = 0.0
    for _ in range(TRIALS):
        x = [rng.gauss(th[i], NOISE_SD) for i in range(p)]
        risk_mle = sum((x[i] - th[i]) ** 2 for i in range(p))
        js = js_estimate(x, p, TARGET)
        risk_js = sum((js[i] - th[i]) ** 2 for i in range(p))
        a = risk_mle - risk_js
        adv.append(a)
        sum_mle += risk_mle
        sum_js += risk_js
        if abs(a) > max_abs_adv:
            max_abs_adv = abs(a)
    return adv, sum_mle / TRIALS, sum_js / TRIALS, max_abs_adv


def mean_se(xs):
    """Sample mean and standard error of the mean (se = std / sqrt(n))."""
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / n
    se = math.sqrt(var / n)
    return m, se


def js_risk_anchor(p, lam, kmax=400):
    """Closed-form James-Stein risk shrinking toward the origin at true-mean norm^2
    lambda: R_JS = p - (p-2)^2 * E[1/S], S ~ noncentral chi-square_p(lambda),
    E[1/S] = sum_k Pois(k; lambda/2) / (p + 2k - 2). Poisson series truncated at kmax."""
    half = lam / 2.0
    # log-Poisson weights for numerical stability at moderate lambda
    e1s = 0.0
    log_w = -half  # k=0 term: exp(-half) * half^0 / 0!
    for k in range(0, kmax + 1):
        w = math.exp(log_w)
        e1s += w / (p + 2 * k - 2)
        log_w += math.log(half) - math.log(k + 1) if half > 0 else -math.inf
        if half == 0.0:
            break  # only k=0 contributes when lambda == 0
    return p - (p - 2) ** 2 * e1s, e1s


def main():
    rng = random.Random(SEED)

    # Fixed "unrelated" true means: DIM_HI independent draws ~ Normal(0, TAU^2),
    # drawn ONCE up front and then held constant (risk is over the X-noise only).
    theta = [rng.gauss(0.0, TAU) for _ in range(DIM_HI)]

    # Measurements (deterministic order): headline DIM, then DIM_LO, DIM_HI, boundary.
    adv_dim, mle_dim, js_dim, _ = run_dim(rng, theta, DIM)
    adv_lo, mle_lo, js_lo, _ = run_dim(rng, theta, DIM_LO)
    adv_hi, mle_hi, js_hi, _ = run_dim(rng, theta, DIM_HI)
    adv_b, mle_b, js_b, max_abs_adv_b = run_dim(rng, theta, DIM_BOUNDARY)

    mean_adv, se_adv = mean_se(adv_dim)
    mean_lo, se_lo = mean_se(adv_lo)
    mean_hi, se_hi = mean_se(adv_hi)

    # Closed-form anchors (shrink toward origin).
    lam_dim = sum(t * t for t in theta[:DIM])
    r_js_anchor_dim, _ = js_risk_anchor(DIM, lam_dim)
    r_mle_anchor_dim = float(DIM)
    lam_lo = sum(t * t for t in theta[:DIM_LO])
    r_js_anchor_lo, _ = js_risk_anchor(DIM_LO, lam_lo)
    # theta=0 special case (analytic, reported): R_JS(0) = 2 for every p >= 3.
    r_js_theta0, _ = js_risk_anchor(DIM, 0.0)

    # Anchor z on the paired ADVANTAGE (closed-form and simulated share the SAME
    # standard error se_adv): advantage closed form = R_MLE - R_JS
    #   = p - (p - (p-2)^2 E[1/S]) = (p-2)^2 E[1/S].
    _, e1s_dim = js_risk_anchor(DIM, lam_dim)
    adv_anchor_dim = (DIM - 2) ** 2 * e1s_dim
    z_adv_anchor = (mean_adv - adv_anchor_dim) / se_adv if se_adv > 0 else float("inf")

    # G1 existence: paired advantage at p=DIM exceeds 0 by >= 3 sigma.
    z_g1 = mean_adv / se_adv if se_adv > 0 else float("inf")
    g1 = z_g1 >= SIGMA_GATE

    # G2 dose-response: mean advantage grows DIM_LO -> DIM_HI by >= 3 sigma (unpaired).
    dose = mean_hi - mean_lo
    se_dose = math.sqrt(se_hi ** 2 + se_lo ** 2)
    z_g2 = dose / se_dose if se_dose > 0 else float("inf")
    g2 = z_g2 >= SIGMA_GATE

    # G3 specificity: at the p=2 boundary the advantage is EXACTLY 0 every trial.
    g3 = (max_abs_adv_b == 0.0)

    all_pass = g1 and g2 and g3

    results = {
        "params": {"SEED": SEED, "TRIALS": TRIALS, "DIM": DIM, "DIM_LO": DIM_LO,
                   "DIM_HI": DIM_HI, "DIM_BOUNDARY": DIM_BOUNDARY, "TAU": TAU,
                   "NOISE_SD": NOISE_SD, "TARGET": TARGET, "SIGMA_GATE": SIGMA_GATE},
        "theta_norm2": {"DIM": round(lam_dim, 6), "DIM_LO": round(lam_lo, 6)},
        "anchor": {
            "R_MLE_DIM": round(r_mle_anchor_dim, 6),
            "R_JS_DIM_closed_form": round(r_js_anchor_dim, 6),
            "R_JS_DIM_LO_closed_form": round(r_js_anchor_lo, 6),
            "R_JS_theta0_all_p": round(r_js_theta0, 6),
            "advantage_DIM_closed_form": round(adv_anchor_dim, 6),
            "advantage_DIM_anchor_z": round(z_adv_anchor, 4),
        },
        "sim": {
            "mean_mle_risk_DIM": round(mle_dim, 6),
            "mean_js_risk_DIM": round(js_dim, 6),
            "mean_advantage_DIM": round(mean_adv, 6), "se_advantage_DIM": round(se_adv, 6),
            "mean_advantage_DIM_LO": round(mean_lo, 6), "se_advantage_DIM_LO": round(se_lo, 6),
            "mean_advantage_DIM_HI": round(mean_hi, 6), "se_advantage_DIM_HI": round(se_hi, 6),
            "dose_hi_minus_lo": round(dose, 6), "se_dose": round(se_dose, 6),
            "mean_mle_risk_boundary": round(mle_b, 6),
            "mean_js_risk_boundary": round(js_b, 6),
            "max_abs_advantage_boundary": round(max_abs_adv_b, 12),
        },
        "gates": {
            "G1_shrinkage_dominates_mle": {"z": round(z_g1, 4), "pass": g1},
            "G2_gain_grows_with_dimension": {"z": round(z_g2, 4), "pass": g2},
            "G3_boundary_exactly_zero_at_p2": {"max_abs_adv": round(max_abs_adv_b, 12), "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    print("ALL_PASS:", all_pass)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
