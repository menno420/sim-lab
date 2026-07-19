#!/usr/bin/env python3
"""PROPOSAL 154 - round-36 VENTURE slot - growth-endurance dominance.

Head: for two SaaS companies matched on current ARR and current growth, a
marginal point of GROWTH ENDURANCE r (the fraction of last period's growth
that persists, g_k = g0 * r**k) buys strictly more terminal ARR than a
marginal point of CURRENT growth g0 -- because terminal log-scale runs on
the geometric sum ~ g0/(1-r), and r sits in the amplifying denominator
(sensitivity ratio ~ g0/(1-r)). Dominance holds for growth-stage companies
(g0 > 1-r); it crosses over for low-growth companies -- disclosed.

Grounding: growth persistence / net-dollar-retention compounding is the
field signature (Bessemer "State of the Cloud" growth-endurance benchmarks;
McKinsey "Grow fast or die slow", 2014). See the proposal doc.

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
N = 1500           # companies per trial
TRIALS = 300       # independent trials -> between-trial z-scores
HORIZON = 12       # years of ARR accumulation (terminal multiple)
DELTA = 0.05       # matched perturbation applied to g0 and to r
REL_NULL = 0.10    # G2 null: dominance margin must exceed a 10% relative effect


def log_terminal(g0, r, horizon=HORIZON):
    """log terminal ARR multiple under geometric growth decay g_k = g0*r**k."""
    lm = 0.0
    g = g0
    for _ in range(horizon):
        lm += math.log1p(g)
        g *= r
    return lm


def draw_base(rng):
    g0 = min(2.00, max(0.15, rng.lognormvariate(math.log(0.60), 0.40)))
    r = min(0.93, max(0.55, rng.normalvariate(0.78, 0.06)))
    return g0, r


def draw_shift(rng):
    # tighter market: lower endurance, higher headline growth
    g0 = min(2.50, max(0.20, rng.lognormvariate(math.log(0.90), 0.40)))
    r = min(0.90, max(0.50, rng.normalvariate(0.68, 0.06)))
    return g0, r


def one_company(g0, r):
    base = log_terminal(g0, r)
    sens_r = log_terminal(g0, min(0.999, r + DELTA)) - base
    sens_g = log_terminal(g0 + DELTA, r) - base
    return sens_r, sens_g


def trial(rng, draw):
    gap_sum = 0.0
    rel_sum = 0.0
    dom = 0
    for _ in range(N):
        g0, r = draw(rng)
        sens_r, sens_g = one_company(g0, r)
        gap_sum += (sens_r - sens_g)
        rel_sum += (sens_r / sens_g - 1.0)
        if sens_r > sens_g:
            dom += 1
    return gap_sum / N, rel_sum / N, dom / N


def summarize(trials, null=0.0):
    mu = statistics.fmean(trials)
    sd = statistics.pstdev(trials)
    se = sd / math.sqrt(len(trials))
    z = (mu - null) / se if se > 0 else float("inf")
    return mu, z


def run():
    rng = random.Random(SEED)
    g1_gaps = []
    g2_rels = []
    g1_fracs = []
    for _ in range(TRIALS):
        gap, rel, frac = trial(rng, draw_base)
        g1_gaps.append(gap)
        g2_rels.append(rel)
        g1_fracs.append(frac)
    g3_gaps = []
    g3_fracs = []
    for _ in range(TRIALS):
        gap, _, frac = trial(rng, draw_shift)
        g3_gaps.append(gap)
        g3_fracs.append(frac)

    g1_mean, g1_z = summarize(g1_gaps, 0.0)
    g2_mean, g2_z = summarize(g2_rels, REL_NULL)
    g3_mean, g3_z = summarize(g3_gaps, 0.0)
    g1_frac = statistics.fmean(g1_fracs)
    g3_frac = statistics.fmean(g3_fracs)

    g1_pass = g1_z >= 3.0 and g1_mean > 0.0
    g2_pass = g2_z >= 3.0 and g2_mean >= REL_NULL
    g3_pass = g3_z >= 3.0 and g3_mean > 0.0
    gates = [("G1_dominance_sign", g1_pass),
             ("G2_relative_effect", g2_pass),
             ("G3_shifted_robustness", g3_pass)]
    first_failing = next((name for name, ok in gates if not ok), None)

    return {
        "proposal": 154,
        "mechanism": "growth-endurance-dominance",
        "config": {"SEED": SEED, "N": N, "TRIALS": TRIALS, "HORIZON": HORIZON,
                   "DELTA": DELTA, "REL_NULL": REL_NULL},
        "G1_dominance_sign": {"gap_mean": round(g1_mean, 6), "z": round(g1_z, 6),
                              "frac_dominant": round(g1_frac, 6)},
        "G2_relative_effect": {"rel_mean": round(g2_mean, 6), "z": round(g2_z, 6),
                               "null": REL_NULL},
        "G3_shifted_robustness": {"gap_mean": round(g3_mean, 6), "z": round(g3_z, 6),
                                  "frac_dominant": round(g3_frac, 6)},
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
