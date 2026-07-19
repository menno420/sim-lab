#!/usr/bin/env python3
"""PROPOSAL 158 - round-37 VENTURE slot - marketplace take-rate disintermediation.

Head: a marketplace's net rake revenue is NON-MONOTONIC in the take-rate.
Raising the rake t is not a pure margin multiplier -- a seller whose
idiosyncratic switching cost c (the value of staying on-platform: discovery,
trust, payments, escrow) is below t transacts OFF-platform, so on-platform
GMV = GMV0 * S(t) with S(t)=P(c>=t) the switching-cost survival curve.
Platform revenue R(t) = t * S(t) * GMV0 is a hump: an interior revenue-optimal
rake t* exists and the aggressive "charge what you can" rake is strictly
dominated, with a large relative revenue loss for overshooting.

Grounding: Bill Gurley, "A Rake Too Far: Optimal Platform Pricing Strategy"
(2013) -- high rakes invite disintermediation; the optimal rake is lower than
"charge what the market bears" intuition. The rake-as-price /
leakage-as-demand structure is the monopoly-pricing identity R = p*Q(p); with
c ~ Uniform[0,C] the demand is linear and the argmax is t*=C/2 (closed form).
Model-dependence (the optimum LOCATION depends on the switching-cost law) is
disclosed; the SIGN and order of magnitude survive a shifted draw.

stdlib only. SEED pinned. Deterministic: reseeded per run; in-process
double-run asserts byte-identical results. Prints the results dict (JSON,
sorted keys) and its sha256 -- WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY.
"""
import math
import json
import hashlib
import random
import statistics

SEED = 20260717
N = 4000            # sellers per trial (each draws a switching cost c)
TRIALS = 300        # independent trials -> between-trial z-scores
C_MAX = 0.50        # base: c ~ Uniform[0, C_MAX]; linear-demand argmax t*=C_MAX/2
C_MAX_SHIFT = 0.35  # shifted (lower loyalty): c ~ Uniform[0, C_MAX_SHIFT]
T_STAR = C_MAX / 2.0               # 0.25 revenue-optimal rake (base)
T_STAR_SHIFT = C_MAX_SHIFT / 2.0   # 0.175 revenue-optimal rake (shifted)
T_MAX = 0.45        # an aggressive "charge what you can" rake
REL_NULL = 0.10     # G2 null: overshoot must cost more than a 10% relative revenue loss


def onplatform_fraction(costs, t):
    return sum(1 for c in costs if c >= t) / len(costs)


def revenue(costs, t):
    # revenue per unit potential GMV: rake t times the on-platform GMV fraction
    return t * onplatform_fraction(costs, t)


def draw_base(rng):
    return rng.uniform(0.0, C_MAX)


def draw_shift(rng):
    return rng.uniform(0.0, C_MAX_SHIFT)


def trial(rng, draw, t_star):
    costs = [draw(rng) for _ in range(N)]
    r_star = revenue(costs, t_star)
    r_max = revenue(costs, T_MAX)
    gap = r_star - r_max
    rel = (r_star - r_max) / r_star if r_star > 0 else 0.0
    dominant = 1 if r_star > r_max else 0
    return gap, rel, dominant, r_star, r_max


def summarize(values, null=0.0):
    mu = statistics.fmean(values)
    sd = statistics.pstdev(values)
    se = sd / math.sqrt(len(values))
    z = (mu - null) / se if se > 0 else float("inf")
    return mu, z


def run():
    rng = random.Random(SEED)
    g1_gaps, g2_rels, g1_fracs = [], [], []
    r_star_base, r_max_base = [], []
    for _ in range(TRIALS):
        gap, rel, dom, r_star, r_max = trial(rng, draw_base, T_STAR)
        g1_gaps.append(gap)
        g2_rels.append(rel)
        g1_fracs.append(dom)
        r_star_base.append(r_star)
        r_max_base.append(r_max)
    g3_gaps, g3_fracs, r_star_shift = [], [], []
    for _ in range(TRIALS):
        gap, rel, dom, r_star, r_max = trial(rng, draw_shift, T_STAR_SHIFT)
        g3_gaps.append(gap)
        g3_fracs.append(dom)
        r_star_shift.append(r_star)

    g1_mean, g1_z = summarize(g1_gaps, 0.0)
    g2_mean, g2_z = summarize(g2_rels, REL_NULL)
    g3_mean, g3_z = summarize(g3_gaps, 0.0)
    g1_frac = statistics.fmean(g1_fracs)
    g3_frac = statistics.fmean(g3_fracs)

    g1_pass = g1_z >= 3.0 and g1_mean > 0.0
    g2_pass = g2_z >= 3.0 and g2_mean >= REL_NULL
    g3_pass = g3_z >= 3.0 and g3_mean > 0.0
    gates = [("G1_domination_sign", g1_pass),
             ("G2_relative_effect", g2_pass),
             ("G3_shifted_robustness", g3_pass)]
    first_failing = next((name for name, ok in gates if not ok), None)

    return {
        "proposal": 158,
        "mechanism": "marketplace-take-rate-disintermediation",
        "config": {"SEED": SEED, "N": N, "TRIALS": TRIALS, "C_MAX": C_MAX,
                   "C_MAX_SHIFT": C_MAX_SHIFT, "T_STAR": T_STAR,
                   "T_STAR_SHIFT": T_STAR_SHIFT, "T_MAX": T_MAX,
                   "REL_NULL": REL_NULL},
        "G1_domination_sign": {"gap_mean": round(g1_mean, 6), "z": round(g1_z, 6),
                               "frac_dominant": round(g1_frac, 6)},
        "G2_relative_effect": {"rel_mean": round(g2_mean, 6), "z": round(g2_z, 6),
                               "null": REL_NULL},
        "G3_shifted_robustness": {"gap_mean": round(g3_mean, 6), "z": round(g3_z, 6),
                                  "frac_dominant": round(g3_frac, 6)},
        "descriptive": {"r_star_base_mean": round(statistics.fmean(r_star_base), 6),
                        "r_max_base_mean": round(statistics.fmean(r_max_base), 6),
                        "r_star_shift_mean": round(statistics.fmean(r_star_shift), 6)},
        "all_pass": g1_pass and g2_pass and g3_pass,
        "first_failing_gate": first_failing,
    }


def main():
    a = run()
    b = run()
    assert a == b, "non-deterministic: in-process double-run diverged"
    payload = json.dumps(a, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    print(payload)
    print("sha256:" + digest)
    print("all_pass:" + str(a["all_pass"]))
    return 0 if a["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
