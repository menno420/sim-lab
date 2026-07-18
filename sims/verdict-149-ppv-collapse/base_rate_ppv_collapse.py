#!/usr/bin/env python3
"""PROPOSAL 136 — base-rate neglect / PPV collapse at low prevalence (round-31 UNRELATED slot).

Phenomenon (Bayesian inference, a fleet-external pure-mechanism head). A screening
test has sensitivity sens = P(positive | diseased) and specificity spec =
P(negative | healthy). Folk belief (inverted here): "a 99%-accurate test that comes
back positive means about a 99% chance you have the disease." Reality (Bayes): the
posterior probability of disease GIVEN a positive result — the positive predictive
value — is
    PPV = P(disease | positive)
        = (sens * prev) / (sens * prev + (1 - spec) * (1 - prev)),
which depends on the base rate prev, NOT on the test's accuracy alone. At
sens = spec = 0.99 and prevalence prev = 0.01 the posterior is EXACTLY 0.5 — a coin
flip, not 0.99 — because the true positives (mass ~ sens*prev) are exactly matched
by the false positives (mass ~ (1-spec)*(1-prev)). Push the prevalence down to
prev = 0.001 and the posterior COLLAPSES further to ~0.0901639: the rarer the
condition, the more a single positive is swamped by false positives. The collapse
deepens as prevalence falls — the base rate, not the "99% accurate" headline,
governs what a positive result means.

Anchors (sens = spec = 0.99, closed form, no RNG):
  Scenario A  prev = 0.01 : PPV0_A = sens*prev/(sens*prev+(1-spec)*(1-prev)) = 0.5 exactly;
              positive-rate p0_A = sens*prev + (1-spec)*(1-prev) = 0.0198.
  Scenario B  prev = 0.001: PPV0_B = 0.99*0.001/(0.99*0.001+0.01*0.999) = 0.0901639344...

Pre-registered gates (APPROVE iff ALL hold, in order G1 -> G2 -> G3):
  G1  POSTERIOR = 0.5 : the empirical PPV at prev=0.01 matches the closed-form
                        anchor 0.5 within z < 3 sigma. se = sqrt(PPV0*(1-PPV0)/n_pos)
                        (Bernoulli over the positives). A "99% accurate" positive is
                        a coin flip, not near-certainty.
  G2  POSITIVE-RATE : the empirical positive-rate at prev=0.01 matches the closed-form
                      anchor p0 = 0.0198 within z < 3 sigma. se = sqrt(p0*(1-p0)/N)
                      (Bernoulli over all N). Confirms the test firing rate is the
                      Bayes denominator, so the sim's tallies are the right object.
  G3  COLLAPSE DEEPENS : the empirical PPV at prev=0.001 matches the closed-form
                         anchor 0.0901639 within z < 3 sigma — as prevalence falls the
                         posterior collapses further (0.5 -> ~0.09), the base-rate
                         mechanism made quantitative. se = sqrt(PPV0_B*(1-PPV0_B)/n_pos)
                         (Bernoulli over the positives).
"""

import hashlib
import json
import math
import random

SEED = 20260717
N = 2_000_000                 # individuals Monte-Carlo'd per prevalence scenario
SENS = 0.99                   # P(positive | diseased)
SPEC = 0.99                   # P(negative | healthy)
PREV_A = 0.01                 # scenario A base rate -> PPV exactly 0.5
PREV_B = 0.001                # scenario B base rate -> PPV collapses to ~0.0901639
SIGMA_GATE = 3.0


def closed_form_ppv(sens, spec, prev):
    """Bayes PPV = P(disease | positive) = sens*prev/(sens*prev + (1-spec)*(1-prev))."""
    tp = sens * prev
    fp = (1.0 - spec) * (1.0 - prev)
    return tp / (tp + fp)


def closed_form_positive_rate(sens, spec, prev):
    """P(positive) = sens*prev + (1-spec)*(1-prev) — the Bayes denominator."""
    return sens * prev + (1.0 - spec) * (1.0 - prev)


def simulate(prev, n, sens, spec, rng):
    """Monte-Carlo n individuals at base rate prev off the pinned stream.

    Each individual is diseased with probability prev; a diseased individual tests
    positive with probability sens, a healthy one with probability (1-spec). Tally
    true/false positives and negatives. Returns (tp, fp, tn, fn).
    """
    tp = fp = tn = fn = 0
    for _ in range(n):
        diseased = rng.random() < prev
        if diseased:
            positive = rng.random() < sens
        else:
            positive = rng.random() < (1.0 - spec)
        if diseased and positive:
            tp += 1
        elif diseased and not positive:
            fn += 1
        elif (not diseased) and positive:
            fp += 1
        else:
            tn += 1
    return tp, fp, tn, fn


def run():
    rng = random.Random(SEED)

    # closed-form anchors (no RNG)
    ppv0_a = closed_form_ppv(SENS, SPEC, PREV_A)          # 0.5 exactly
    p0_a = closed_form_positive_rate(SENS, SPEC, PREV_A)  # 0.0198
    ppv0_b = closed_form_ppv(SENS, SPEC, PREV_B)          # 0.0901639344...

    # Monte-Carlo the two scenarios in fixed order off the single pinned stream
    tp_a, fp_a, tn_a, fn_a = simulate(PREV_A, N, SENS, SPEC, rng)
    tp_b, fp_b, tn_b, fn_b = simulate(PREV_B, N, SENS, SPEC, rng)

    n_pos_a = tp_a + fp_a
    n_pos_b = tp_b + fp_b
    emp_ppv_a = tp_a / n_pos_a
    emp_ppv_b = tp_b / n_pos_b
    emp_posrate_a = n_pos_a / N
    emp_posrate_b = n_pos_b / N

    # G1 — posterior = 0.5: empirical PPV at prev=0.01 vs the closed-form 0.5
    se_g1 = math.sqrt(ppv0_a * (1.0 - ppv0_a) / n_pos_a)
    z_g1 = (emp_ppv_a - ppv0_a) / se_g1 if se_g1 > 0 else float("inf")
    g1 = abs(z_g1) < SIGMA_GATE

    # G2 — positive-rate: empirical positive-rate at prev=0.01 vs the closed-form 0.0198
    se_g2 = math.sqrt(p0_a * (1.0 - p0_a) / N)
    z_g2 = (emp_posrate_a - p0_a) / se_g2 if se_g2 > 0 else float("inf")
    g2 = abs(z_g2) < SIGMA_GATE

    # G3 — collapse deepens: empirical PPV at prev=0.001 vs the closed-form ~0.0901639
    se_g3 = math.sqrt(ppv0_b * (1.0 - ppv0_b) / n_pos_b)
    z_g3 = (emp_ppv_b - ppv0_b) / se_g3 if se_g3 > 0 else float("inf")
    g3 = abs(z_g3) < SIGMA_GATE

    all_pass = g1 and g2 and g3

    return {
        "proposal": 136,
        "seed": SEED,
        "n": N,
        "sens": SENS,
        "spec": SPEC,
        "prev_a": PREV_A,
        "prev_b": PREV_B,
        "sigma_gate": SIGMA_GATE,
        "anchor_ppv_a": ppv0_a,
        "anchor_positive_rate_a": p0_a,
        "anchor_ppv_b": ppv0_b,
        "tp_a": tp_a,
        "fp_a": fp_a,
        "tn_a": tn_a,
        "fn_a": fn_a,
        "tp_b": tp_b,
        "fp_b": fp_b,
        "tn_b": tn_b,
        "fn_b": fn_b,
        "n_pos_a": n_pos_a,
        "n_pos_b": n_pos_b,
        "emp_ppv_a": emp_ppv_a,
        "emp_positive_rate_a": emp_posrate_a,
        "emp_ppv_b": emp_ppv_b,
        "emp_positive_rate_b": emp_posrate_b,
        "g1_posterior_half": g1,
        "g1_z": z_g1,
        "g1_se": se_g1,
        "g1_emp_ppv_a": emp_ppv_a,
        "g1_anchor_ppv_a": ppv0_a,
        "g2_positive_rate": g2,
        "g2_z": z_g2,
        "g2_se": se_g2,
        "g2_emp_positive_rate_a": emp_posrate_a,
        "g2_anchor_positive_rate_a": p0_a,
        "g3_collapse_deepens": g3,
        "g3_z": z_g3,
        "g3_se": se_g3,
        "g3_emp_ppv_b": emp_ppv_b,
        "g3_anchor_ppv_b": ppv0_b,
        "all_pass": all_pass,
    }


def main():
    results = run()
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    # in-process double-run: run() twice, compact-hash both, assert byte-identical
    results_2 = run()
    payload_2 = json.dumps(results_2, sort_keys=True, separators=(",", ":"))
    digest_2 = hashlib.sha256(payload_2.encode()).hexdigest()
    assert digest == digest_2, "non-deterministic: in-process double-run digests differ"

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    print(
        "G1 posterior=0.5   :",
        "PASS" if results["g1_posterior_half"] else "FAIL",
        f"(z={results['g1_z']:+.3f}, PPV(prev=0.01)={results['g1_emp_ppv_a']:.6f} "
        f"vs anchor {results['g1_anchor_ppv_a']:.6f})",
    )
    print(
        "G2 positive-rate   :",
        "PASS" if results["g2_positive_rate"] else "FAIL",
        f"(z={results['g2_z']:+.3f}, posrate(prev=0.01)={results['g2_emp_positive_rate_a']:.6f} "
        f"vs anchor {results['g2_anchor_positive_rate_a']:.6f})",
    )
    print(
        "G3 collapse deepens:",
        "PASS" if results["g3_collapse_deepens"] else "FAIL",
        f"(z={results['g3_z']:+.3f}, PPV(prev=0.001)={results['g3_emp_ppv_b']:.6f} "
        f"vs anchor {results['g3_anchor_ppv_b']:.6f})",
    )
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
