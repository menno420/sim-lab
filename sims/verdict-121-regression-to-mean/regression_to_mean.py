#!/usr/bin/env python3
"""
regression_to_mean.py — reference verifier for PROPOSAL 108 (round-24, UNRELATED
slot closer). Domain: statistics / experimental design / measurement — Galton's
regression to the mean (1886) and the selection-on-extremes illusion.
Fleet-external pure-mechanism head.

The "spurious treatment effect" trap. Take a noisy repeated measurement: a pre
score X and a post score Y of the SAME unit, with test-retest reliability (the
correlation of the two noisy reads of one fixed latent ability) rho < 1, and
NOTHING done between the two reads. Select the "underperformers" -- every unit
with X below a fixed cutoff c (e.g. more than one SD below the mean) -- apply an
inert intervention (literally nothing), and re-measure Y. The selected group's
mean IMPROVES, strongly and reproducibly, purely from regression to the mean:
their extreme-low X was partly bad luck, and luck does not repeat, so Y drifts
back toward the population mean. The apparent improvement is exactly
Delta* = (rho - 1) * E[X | X < c], which is strictly POSITIVE for rho < 1 and
c < 0 -- a large, hundred-sigma "effect" from an intervention that does nothing.
The whole population, meanwhile, shows zero change (no time trend), and the
top-tail (over-performers) shows a symmetric spurious DECLINE.

E[X | X < c] = -phi(c)/Phi(c) (mean of a left-truncated standard normal, the
inverse Mills ratio), computed in stdlib via math.erf. E[Y | X < c] = rho * m
because (X, Y) is standard bivariate normal with correlation rho, so the anchor
Delta* = rho*m - m = (rho - 1)*m is closed-form and exact.

Gates (all on the /se margin, the P104/P105/P106/P107 convention -- z on the
estimated MEAN via its standard error se = std / sqrt(TRIALS)):
  G1 spurious-improvement headline: the selected underperformers' mean
     improvement Delta_sel >= IMPROVE_MIN by >= 3 sigma AND Delta_sel > 0 -- an
     inert intervention on the bottom tail shows a large, significant "effect".
  G2 selection-necessity control: the WHOLE-population before/after change
     Delta_pop is within 3 sigma of 0 (|z| < 3) -- there is no global time
     trend, so G1's effect is 100% selection-on-extremes + regression, not drift.
  G3 closed-form anchor MATCH: Delta_sel matches the exact regression prediction
     Delta* = (rho - 1) * (-phi(c)/Phi(c)) within 3 sigma (|z| < 3) -- reproduces
     Galton's regression coefficient, so the effect is the RTM mechanism itself.

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717        # proposal-owned pinned seed; SEEDLESS discipline
RHO = 0.5              # test-retest reliability (correlation of the two noisy reads)
C_THRESH = -1.0        # selection cutoff: "underperformers" > 1 SD below the mean
N_UNITS = 20000        # units per trial (each has a pre score X and post score Y)
TRIALS = 400           # independent experiments (the /se convention averages over these)
SIGMA_GATE = 3.0       # pre-registered gate threshold (sigma)
IMPROVE_MIN = 0.50     # G1 floor on the spurious improvement (SD units)


def std_norm_pdf(x):
    """phi(x): standard-normal density."""
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def std_norm_cdf(x):
    """Phi(x): standard-normal CDF via the error function (stdlib math.erf)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def left_truncated_mean(c):
    """E[X | X < c] for standard normal = -phi(c)/Phi(c) (inverse Mills ratio)."""
    return -std_norm_pdf(c) / std_norm_cdf(c)


def right_truncated_mean(c):
    """E[X | X > c] for standard normal = phi(c)/(1-Phi(c))."""
    return std_norm_pdf(c) / (1.0 - std_norm_cdf(c))


def run_trial(rng):
    """One experiment on N_UNITS units, NO intervention applied.

    Each unit has a pre score X ~ N(0,1) and a post score Y = rho*X + sqrt(1-rho^2)*Z,
    Z ~ N(0,1) independent -- so (X,Y) is standard bivariate normal with correlation
    rho and NO real change between reads. Returns (delta_sel, delta_pop, delta_top):
      delta_sel = mean(Y)-mean(X) over the selected underperformers (X < C_THRESH),
      delta_pop = mean(Y)-mean(X) over the whole population (the no-selection control),
      delta_top = mean(Y)-mean(X) over the over-performers (X > -C_THRESH), descriptive.
    """
    root = math.sqrt(1.0 - RHO * RHO)
    top_c = -C_THRESH
    sum_x_sel = sum_y_sel = 0.0
    n_sel = 0
    sum_x_pop = sum_y_pop = 0.0
    sum_x_top = sum_y_top = 0.0
    n_top = 0
    for _ in range(N_UNITS):
        x = rng.gauss(0.0, 1.0)
        z = rng.gauss(0.0, 1.0)
        y = RHO * x + root * z
        sum_x_pop += x
        sum_y_pop += y
        if x < C_THRESH:
            sum_x_sel += x
            sum_y_sel += y
            n_sel += 1
        if x > top_c:
            sum_x_top += x
            sum_y_top += y
            n_top += 1
    delta_sel = (sum_y_sel - sum_x_sel) / n_sel if n_sel > 0 else 0.0
    delta_pop = (sum_y_pop - sum_x_pop) / N_UNITS
    delta_top = (sum_y_top - sum_x_top) / n_top if n_top > 0 else 0.0
    return delta_sel, delta_pop, delta_top


def mean_se(xs):
    """Sample mean and standard error of the mean (se = std / sqrt(n))."""
    k = len(xs)
    m = sum(xs) / k
    var = sum((x - m) ** 2 for x in xs) / k
    se = math.sqrt(var / k)
    return m, se


def main():
    rng = random.Random(SEED)

    m_sel = left_truncated_mean(C_THRESH)         # E[X | X < c], the selection gap
    m_top = right_truncated_mean(-C_THRESH)       # E[X | X > -c], the over-performer gap
    delta_star = (RHO - 1.0) * m_sel              # closed-form spurious improvement
    delta_top_star = (RHO - 1.0) * m_top          # closed-form spurious decline (top tail)

    sels, pops, tops = [], [], []
    for _ in range(TRIALS):
        d_sel, d_pop, d_top = run_trial(rng)
        sels.append(d_sel)
        pops.append(d_pop)
        tops.append(d_top)

    delta_sel, se_sel = mean_se(sels)
    delta_pop, se_pop = mean_se(pops)
    delta_top, se_top = mean_se(tops)

    # G1 spurious-improvement headline: Delta_sel exceeds the floor by >= 3 sigma.
    z_g1 = (delta_sel - IMPROVE_MIN) / se_sel if se_sel > 0 else float("inf")
    g1 = (z_g1 >= SIGMA_GATE) and (delta_sel > 0.0)

    # G2 selection-necessity control: whole-population change consistent with 0.
    z_g2 = abs(delta_pop) / se_pop if se_pop > 0 else float("inf")
    g2 = z_g2 < SIGMA_GATE

    # G3 closed-form anchor MATCH: Delta_sel == (rho-1)*E[X|X<c] within 3 sigma.
    z_g3 = abs(delta_sel - delta_star) / se_sel if se_sel > 0 else float("inf")
    g3 = z_g3 < SIGMA_GATE

    all_pass = g1 and g2 and g3

    results = {
        "params": {"SEED": SEED, "RHO": RHO, "C_THRESH": C_THRESH,
                   "N_UNITS": N_UNITS, "TRIALS": TRIALS, "SIGMA_GATE": SIGMA_GATE,
                   "IMPROVE_MIN": IMPROVE_MIN},
        "anchor": {"m_sel_selection_gap": round(m_sel, 6),
                   "m_top_overperformer_gap": round(m_top, 6),
                   "delta_star_spurious_improvement": round(delta_star, 6),
                   "delta_top_star_spurious_decline": round(delta_top_star, 6)},
        "sim": {
            "delta_sel": round(delta_sel, 6), "se_sel": round(se_sel, 6),
            "delta_pop": round(delta_pop, 6), "se_pop": round(se_pop, 6),
            "delta_top": round(delta_top, 6), "se_top": round(se_top, 6),
        },
        "gates": {
            "G1_spurious_improvement": {"z": round(z_g1, 4), "pass": g1},
            "G2_population_control": {"z": round(z_g2, 4), "pass": g2},
            "G3_anchor_match": {"z": round(z_g3, 4), "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("regression_to_mean_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
