#!/usr/bin/env python3
"""
arcsine_lead_illusion.py — reference verifier for PROPOSAL 116 (round-26,
UNRELATED slot closer). Domain: probability theory / stochastic processes —
the Levy-Feller arcsine law of the lead in a FAIR game. Fleet-external
pure-mechanism head.

The "a fair game is a level game" trap. Play a perfectly FAIR contest as an
unbiased +/-1 random walk of N_STEPS steps (each step a fair coin, zero edge,
zero drift). Intuition says the two sides should trade the lead evenly, so each
player is ahead about HALF the time and the fraction-of-time-in-the-lead
concentrates near 1/2. The truth is the OPPOSITE (Levy's first arcsine law): the
fraction of time one side leads follows the ARCSINE distribution, whose density
1/(pi*sqrt(x(1-x))) is U-SHAPED -- it PILES UP at 0 and 1 and is MINIMIZED at
1/2. So the MOST likely outcomes are one side leading almost the WHOLE game; a
close see-saw (each ahead ~half the time) is the RAREST outcome, not the typical
one. The game is fair in EXPECTATION (mean lead-fraction = 1/2 exactly) yet its
DISTRIBUTION is bimodal at the extremes -- leadership is not shared fairly.

Discrete arcsine law (exact, Feller Vol. 1 III.4). For a symmetric +/-1 walk of
2n steps, segment i (from S_{i-1} to S_i) lies ABOVE the axis iff S_{i-1}+S_i>0
(the two endpoints differ by 1 so the sum is odd, never 0 -- the side is always
defined). The number T of above-axis segments is always even, and

    P(T = 2k) = u_{2k} * u_{2(n-k)},   u_{2j} = C(2j, j) / 4^j,   k = 0..n

EXACTLY (a product of two "return" probabilities), the discrete arcsine law; its
n->inf limit is the continuous P(fraction <= x) -> (2/pi)*arcsin(sqrt(x)). All
anchors below are the EXACT discrete law, summed in stdlib from math.comb -- no
asymptotic approximation, no third-party.

Gates (all on the /se margin, the P104..P115 convention -- z on the estimated
MEAN via its standard error se = std / sqrt(TRIALS)):
  G1 extreme-lead headline: the measured probability that one side leads for an
     EXTREME share of the game (lead-fraction <= LEAD_LO or >= LEAD_HI) is at or
     above EXT_MIN by >= 3 sigma -- in a fair game one side is ahead almost the
     whole time far more often than the naive 50/50 picture allows.
  G2 fair-mean + middle-is-rare control: (a) the mean lead-fraction is within
     3 sigma of 1/2 (|z| < 3) -- the walk is genuinely UNBIASED, so G1's
     concentration is the arcsine U-shape, not a drift; AND (b) the BALANCED
     outcome (lead-fraction in [BAL_LO, BAL_HI], a roughly even see-saw) is rare,
     P_balanced <= BAL_MAX by >= 3 sigma, AND the extreme-minus-balanced gap
     (P_extreme - P_balanced) >= GAP_MIN by >= 3 sigma -- the extremes strictly
     BEAT the middle, inverting the naive "concentrates at 1/2" belief.
  G3 closed-form anchor MATCH: the measured extreme-lead probability matches the
     exact discrete-arcsine anchor within 3 sigma AND the measured lower-tail
     P(fraction <= LEAD_LO) matches its exact anchor within 3 sigma (|z| < 3
     each) -- reproduces the Levy-Feller arcsine law itself.

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717        # proposal-owned pinned seed; SEEDLESS discipline
N_STEPS = 500          # steps in the fair contest (2n; n = N_STEPS/2 = 250)
N_WALKS = 4000         # simulated fair games per trial (the per-trial-mean batch)
TRIALS = 200           # independent experiments (the /se convention averages over these)
SIGMA_GATE = 3.0       # pre-registered gate threshold (sigma)
LEAD_LO = 0.10         # lower extreme cut on the lead-fraction
LEAD_HI = 0.90         # upper extreme cut (symmetric: 1 - LEAD_LO)
BAL_LO = 0.40          # balanced-band lower cut (roughly even see-saw)
BAL_HI = 0.60          # balanced-band upper cut
EXT_MIN = 0.30         # G1 floor on the extreme-lead probability
BAL_MAX = 0.20         # G2 ceiling on the balanced probability
GAP_MIN = 0.15         # G2 floor on the (extreme - balanced) gap


def u_return(twoj):
    """u_{2j} = C(2j, j) / 4^j -- the probability a symmetric walk is at 0 after 2j steps."""
    j = twoj // 2
    return math.comb(twoj, j) / (4.0 ** j)


def arcsine_pmf(n):
    """Exact discrete arcsine law over a 2n-step walk: pmf[k] = P(T = 2k) =
    u_{2k}*u_{2(n-k)} for k = 0..n, where T is the number of above-axis segments."""
    return [u_return(2 * k) * u_return(2 * (n - k)) for k in range(n + 1)]


def exact_anchors(n):
    """Exact P(extreme lead), P(fraction <= LEAD_LO), P(balanced) from the discrete law."""
    pmf = arcsine_pmf(n)
    p_low = p_high = p_bal = 0.0
    for k in range(n + 1):
        frac = (2 * k) / (2 * n)          # lead-fraction = T / N_STEPS
        p = pmf[k]
        if frac <= LEAD_LO:
            p_low += p
        if frac >= LEAD_HI:
            p_high += p
        if BAL_LO <= frac <= BAL_HI:
            p_bal += p
    return {"p_low": p_low, "p_extreme": p_low + p_high, "p_balanced": p_bal}


def run_trial(rng, n):
    """One experiment over N_WALKS fair 2n-step games. Returns (mean_lead_fraction,
    p_extreme, p_low, p_balanced) measured over the batch. Each game is a symmetric
    +/-1 walk; a segment i is above the axis iff S_{i-1}+S_i > 0, and the lead-fraction
    is the count of above-axis segments divided by the 2n steps."""
    two_n = 2 * n
    sum_frac = 0.0
    n_extreme = n_low = n_balanced = 0
    for _ in range(N_WALKS):
        s = 0            # current partial sum S_i
        above = 0        # count of above-axis segments so far
        for _ in range(two_n):
            step = 1 if rng.random() < 0.5 else -1
            s_prev = s
            s += step
            if s_prev + s > 0:            # segment lies above the axis (sum is odd, never 0)
                above += 1
        frac = above / two_n
        sum_frac += frac
        if frac <= LEAD_LO or frac >= LEAD_HI:
            n_extreme += 1
        if frac <= LEAD_LO:
            n_low += 1
        if BAL_LO <= frac <= BAL_HI:
            n_balanced += 1
    inv = 1.0 / N_WALKS
    return (sum_frac * inv, n_extreme * inv, n_low * inv, n_balanced * inv)


def mean_se(xs):
    """Sample mean and standard error of the mean (se = std / sqrt(n))."""
    k = len(xs)
    m = sum(xs) / k
    var = sum((x - m) ** 2 for x in xs) / k
    se = math.sqrt(var / k)
    return m, se


def main():
    rng = random.Random(SEED)
    n = N_STEPS // 2

    anch = exact_anchors(n)
    anchor_extreme = anch["p_extreme"]
    anchor_low = anch["p_low"]
    anchor_balanced = anch["p_balanced"]

    fracs, extremes, lows, balanced = [], [], [], []
    for _ in range(TRIALS):
        mf, pe, pl, pb = run_trial(rng, n)
        fracs.append(mf)
        extremes.append(pe)
        lows.append(pl)
        balanced.append(pb)

    mean_frac, se_frac = mean_se(fracs)
    p_extreme, se_extreme = mean_se(extremes)
    p_low, se_low = mean_se(lows)
    p_balanced, se_balanced = mean_se(balanced)

    # G1 extreme-lead headline: P(extreme) >= EXT_MIN by >= 3 sigma.
    z_g1 = (p_extreme - EXT_MIN) / se_extreme if se_extreme > 0 else float("inf")
    g1 = z_g1 >= SIGMA_GATE

    # G2 fair-mean + middle-is-rare control.
    z_g2_mean = abs(mean_frac - 0.5) / se_frac if se_frac > 0 else float("inf")
    z_g2_bal = (BAL_MAX - p_balanced) / se_balanced if se_balanced > 0 else float("inf")
    gap = p_extreme - p_balanced
    se_gap = math.sqrt(se_extreme ** 2 + se_balanced ** 2)
    z_g2_gap = (gap - GAP_MIN) / se_gap if se_gap > 0 else float("inf")
    g2 = (z_g2_mean < SIGMA_GATE) and (z_g2_bal >= SIGMA_GATE) and (z_g2_gap >= SIGMA_GATE)

    # G3 closed-form anchor MATCH: extreme + lower-tail match the exact discrete law.
    z_g3_extreme = abs(p_extreme - anchor_extreme) / se_extreme if se_extreme > 0 else float("inf")
    z_g3_low = abs(p_low - anchor_low) / se_low if se_low > 0 else float("inf")
    g3 = (z_g3_extreme < SIGMA_GATE) and (z_g3_low < SIGMA_GATE)

    all_pass = g1 and g2 and g3

    results = {
        "params": {"SEED": SEED, "N_STEPS": N_STEPS, "N_WALKS": N_WALKS,
                   "TRIALS": TRIALS, "SIGMA_GATE": SIGMA_GATE,
                   "LEAD_LO": LEAD_LO, "LEAD_HI": LEAD_HI,
                   "BAL_LO": BAL_LO, "BAL_HI": BAL_HI,
                   "EXT_MIN": EXT_MIN, "BAL_MAX": BAL_MAX, "GAP_MIN": GAP_MIN},
        "anchor": {"arcsine_extreme": round(anchor_extreme, 6),
                   "arcsine_low_tail": round(anchor_low, 6),
                   "arcsine_balanced": round(anchor_balanced, 6),
                   "continuous_extreme_2_over_pi": round(
                       2.0 * (2.0 / math.pi) * math.asin(math.sqrt(LEAD_LO)), 6)},
        "sim": {
            "mean_lead_fraction": round(mean_frac, 6), "se_mean_frac": round(se_frac, 6),
            "p_extreme": round(p_extreme, 6), "se_extreme": round(se_extreme, 6),
            "p_low_tail": round(p_low, 6), "se_low": round(se_low, 6),
            "p_balanced": round(p_balanced, 6), "se_balanced": round(se_balanced, 6),
            "gap_extreme_minus_balanced": round(gap, 6), "se_gap": round(se_gap, 6),
        },
        "gates": {
            "G1_extreme_lead": {"z": round(z_g1, 4), "pass": g1},
            "G2_fair_mean_middle_rare": {
                "z_mean": round(z_g2_mean, 4), "z_balanced": round(z_g2_bal, 4),
                "z_gap": round(z_g2_gap, 4), "pass": g2},
            "G3_anchor_match": {
                "z_extreme": round(z_g3_extreme, 4), "z_low": round(z_g3_low, 4),
                "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("arcsine_lead_illusion_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
