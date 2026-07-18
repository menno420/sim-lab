#!/usr/bin/env python3
"""
PROPOSAL 144 — the hot-hand streak-selection bias (firsthand verifier).

Phenomenon (Miller & Sanjurjo, "Surprised by the Hot Hand Fallacy? A Truth in
the Law of Small Numbers", Econometrica 86(6):2019-2047, 2018).

Take a FINITE sequence of N fair (p=1/2, i.i.d.) coin flips. Select every flip
that immediately follows a run of K consecutive heads, and compute that
sequence's fraction of heads AMONG the selected flips. Average this per-sequence
fraction across sequences (conditioning on the sequences where at least one
selected flip exists). Naively the coin is memoryless, so the answer "should" be
0.5. It is not: the EXPECTED per-sequence fraction is strictly BELOW 0.5. Within
a finite sequence, choosing a flip because the previous K flips were heads makes
it slightly LESS likely (in expectation, across the ratio) that the chosen flip
is itself a head -- a selection/sampling bias, not any memory in the coin. A fair
memoryless process, read with the natural "what happens right after a streak?"
estimator, looks anti-streaky.

The exact finite-sequence expectation is a closed-form combinatorial quantity:
this verifier computes it by EXHAUSTIVE ENUMERATION of all 2^N sequences
(deterministic, no sampling) and treats that as the Miller-Sanjurjo reference.
A Monte-Carlo run over M random sequences must (a) land significantly below 0.5
and (b) agree with the exact expectation.

Pre-registered gates (ordered; each on the /se margin, one pinned SEED):
  G1  estimator-agreement: two independent halves of the M per-sequence
      fractions do NOT significantly disagree,           |z| < SIGMA_GATE
  G2  closed-form agreement: the MC mean is NOT significantly different from
      the exact enumerated Miller-Sanjurjo expectation,  |z| < SIGMA_GATE
  G3  head: the MC mean is SIGNIFICANTLY below 0.5,
      z = (0.5 - mean) / se >= SIGMA_GATE
APPROVE iff G1 and G2 and G3 all pass, in order.

Run:  python3 ideas/fleet/hot_hand_streak_selection_bias.py
Deterministic: same SEED -> identical results dict -> identical sha256.
Exit 0 iff all gates pass.
"""

import random
import math
import json
import hashlib

# ---- pinned world (committed constants) ----
SEED = 20260717
N_FLIPS = 15               # length of each finite coin-flip sequence
K_STREAK = 3               # select the flip that immediately follows K heads
M_SEQUENCES = 400000       # Monte-Carlo sequences
SIGMA_GATE = 3.0
ROUND_DP = 6               # every emitted float rounded to 6 dp (determinism)


def r6(x):
    return round(float(x), ROUND_DP)


def sequence_fraction(bits, n, k):
    """
    For one length-n sequence (bits = list of 0/1, 1 = heads), return
    (heads_after_streak, selected_count): among positions j in [k, n-1] whose k
    immediately-preceding flips bits[j-k..j-1] are ALL heads, count how many
    bits[j] are heads and how many were selected. Overlapping windows allowed
    (the Miller-Sanjurjo convention).
    """
    heads_after = 0
    selected = 0
    run = 0  # current trailing run of heads ending at position j-1
    for j in range(n):
        if run >= k:
            selected += 1
            if bits[j] == 1:
                heads_after += 1
        if bits[j] == 1:
            run += 1
        else:
            run = 0
    return heads_after, selected


def exact_expectation(n, k):
    """
    Exact finite-sequence Miller-Sanjurjo expectation: enumerate all 2^n equally
    likely sequences, take the per-sequence fraction where it is defined
    (>=1 selected flip), and average those fractions. Returns
    (E_exact, n_defined_sequences, total_sequences). Deterministic, no RNG.
    """
    total = 1 << n
    frac_sum = 0.0
    defined = 0
    for mask in range(total):
        bits = [(mask >> i) & 1 for i in range(n)]
        heads_after, selected = sequence_fraction(bits, n, k)
        if selected > 0:
            frac_sum += heads_after / selected
            defined += 1
    return frac_sum / defined, defined, total


def mean_se(xs):
    n = len(xs)
    mean = sum(xs) / n
    if n < 2:
        return mean, 0.0
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return mean, math.sqrt(var / n)


def main():
    rng = random.Random(SEED)

    # ---- exact closed-form reference (deterministic enumeration) ----
    e_exact, exact_defined, exact_total = exact_expectation(N_FLIPS, K_STREAK)

    # ---- Monte-Carlo over M finite sequences ----
    fractions = []  # per-sequence fraction, only for sequences with >=1 selected flip
    undefined = 0
    for _ in range(M_SEQUENCES):
        bits = [1 if rng.random() < 0.5 else 0 for _ in range(N_FLIPS)]
        heads_after, selected = sequence_fraction(bits, N_FLIPS, K_STREAK)
        if selected > 0:
            fractions.append(heads_after / selected)
        else:
            undefined += 1

    n_defined = len(fractions)
    mc_mean, mc_se = mean_se(fractions)

    # ---- G1 estimator-agreement: two independent halves must not disagree ----
    half = n_defined // 2
    first_half = fractions[:half]
    second_half = fractions[half:]
    m1, se1 = mean_se(first_half)
    m2, se2 = mean_se(second_half)
    se_diff = math.sqrt(se1 * se1 + se2 * se2)
    g1_z = (m1 - m2) / se_diff if se_diff > 0 else 0.0
    g1_pass = abs(g1_z) < SIGMA_GATE

    # ---- G2 closed-form agreement: MC mean vs exact expectation ----
    g2_z = (mc_mean - e_exact) / mc_se if mc_se > 0 else 0.0
    g2_pass = abs(g2_z) < SIGMA_GATE

    # ---- G3 head: MC mean significantly below 0.5 ----
    g3_z = (0.5 - mc_mean) / mc_se if mc_se > 0 else 0.0
    g3_pass = g3_z >= SIGMA_GATE

    gates_pass_in_order = g1_pass and g2_pass and g3_pass
    first_failing = None
    for name, ok in (("G1", g1_pass), ("G2", g2_pass), ("G3", g3_pass)):
        if not ok:
            first_failing = name
            break

    results = {
        "proposal": 144,
        "phenomenon": "hot-hand streak-selection bias (Miller-Sanjurjo finite-sequence selection bias)",
        "params": {
            "seed": SEED,
            "n_flips": N_FLIPS,
            "k_streak": K_STREAK,
            "m_sequences": M_SEQUENCES,
            "sigma_gate": SIGMA_GATE,
        },
        "exact": {
            "e_exact": r6(e_exact),
            "bias_vs_half": r6(e_exact - 0.5),
            "defined_sequences": exact_defined,
            "total_sequences": exact_total,
        },
        "mc": {
            "n_defined": n_defined,
            "undefined_dropped": undefined,
            "mc_mean": r6(mc_mean),
            "mc_se": r6(mc_se),
            "mc_bias_vs_half": r6(mc_mean - 0.5),
        },
        "gates": {
            "G1_estimator_agreement": {
                "stat": "z = (mean_firsthalf - mean_secondhalf) / se_diff",
                "mean_first_half": r6(m1),
                "mean_second_half": r6(m2),
                "z": r6(g1_z),
                "rule": "|z| < sigma_gate",
                "pass": g1_pass,
            },
            "G2_closed_form_agreement": {
                "stat": "z = (mc_mean - e_exact) / mc_se",
                "e_exact": r6(e_exact),
                "mc_mean": r6(mc_mean),
                "z": r6(g2_z),
                "rule": "|z| < sigma_gate",
                "pass": g2_pass,
            },
            "G3_head_below_half": {
                "stat": "z = (0.5 - mc_mean) / mc_se",
                "mc_mean": r6(mc_mean),
                "z": r6(g3_z),
                "rule": "z >= sigma_gate",
                "pass": g3_pass,
            },
        },
        "all_pass": gates_pass_in_order,
        "first_failing_gate": first_failing,
    }

    # WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY: hash the compact canonical dict
    # (no results_sha256 key inside it); print the pretty dump + the digest line.
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if gates_pass_in_order else 1


if __name__ == "__main__":
    raise SystemExit(main())
