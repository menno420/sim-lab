#!/usr/bin/env python3
"""Reservoir sampling (Algorithm R) uniform inclusion - firsthand verifier (PROPOSAL 221).

Counterintuitive-but-exactly-true: a single streaming pass that never revisits an
item and never knows the stream length n in advance nonetheless leaves EVERY one
of the n items in the size-k reservoir with probability EXACTLY k/n - the same
k/n whether the item arrived first, in the fill, or dead last. Algorithm R
(Waterman; Knuth TAOCP Vol.2; Vitter):

    for i in 1..n:
        if i <= k: reservoir[i-1] = item_i             # fill the first k slots
        else:
            j = uniform integer in [1, i]
            if j <= k: reservoir[j-1] = item_i         # replace slot j (accept iff j<=k)

The inclusion probability is proven here FIRSTHAND as a LITERAL product of
fractions.Fraction (multiplied out in a loop, NOT hardcoded to the telescoped
k/n):
  item i<=k: survival = prod_{t=k+1..n} (t-1)/t              == k/n
  item i>k:  (k/i) * prod_{t=i+1..n} (t-1)/t = (k/i)*(i/n)   == k/n

Stdlib-only. SEED=20260717, all randomness from a single random.Random(20260717)
consumed in a fixed, documented order: G2 draws MC_TRIALS Algorithm-R runs per
config (in CONFIGS order), then G3 draws the shuffled-order MC and the subset
tally, then G4 draws the buggy-model MC - back-to-back, no interleaving.
Deterministic across in-process double-run and separate cross-invocation.

Gate battery (each read in ITS OWN direction):
  G1 EXACT identity (Fraction, equality). Direction: any analytic inclusion
     probability != k/n => FAIL. For each config, for EVERY item i in 1..n the
     inclusion probability is the literal Fraction product above; assert
     == Fraction(k, n). PASS = exact equality for all i.
  G2 MONTE-CARLO agreement (|z| < 3 PASS). Direction: max |z| >= 3 over the
     probe set => FAIL. For each config the empirical inclusion frequency of the
     probe items {1, k, k+1, n} over MC_TRIALS runs agrees with p=k/n within 3
     sigma, z = (freq - p)/sqrt(p(1-p)/T).
  G3 ROBUSTNESS. Direction: dependence on stream order OR non-uniform k-subsets
     => FAIL. (a) shuffling the arrival order of item identities leaves probe
     inclusion within |z|<3; (b) over SUBSET_TRIALS runs the C(6,3)=20 distinct
     reservoir subsets are uniform by chi-square < 43.8 (df=19, ~0.001 crit).
  G4 FALSIFIABILITY (wrong model REJECTED at max |z| >= 6). Direction: PASS iff
     the plausible-but-wrong "unconditional-replace" bug (for i>k pick j uniform
     in [1,k] and ALWAYS replace, dropping the j<=i acceptance gate) deviates
     from k/n at max |z| >= 6, so k/n is correctly rejected for the buggy model.
     A second analytic "first-k" naive model (1 for i<=k, else 0) is recorded as
     rejected too.
"""
import hashlib
import json
import math
import random
from fractions import Fraction

SEED = 20260717
CONFIGS = [(40, 8), (25, 5)]        # (n, k) probe configs for G1 / G2
MC_TRIALS = 80000                   # Monte-Carlo runs per config (G2, G3a)
SUBSET_CFG = (6, 3)                 # (n, k) for the subset-uniformity chi-square
SUBSET_TRIALS = 150000             # runs for the C(6,3)=20 subset tally (G3b)
UR_CFG = (40, 8)                    # (n, k) for the unconditional-replace bug (G4)
UR_TRIALS = 40000                   # runs for the buggy-model rejection (G4)
Z_AGREE = 3.0                       # G2/G3a two-sided agreement band
Z_REJECT = 6.0                      # G4 falsifiability rejection floor
CHISQ_CRIT = 43.8                   # df=19 chi-square ~0.001 critical value (G3b)


def frac_str(f):
    return "{0}/{1}".format(f.numerator, f.denominator)


def probe_items(n, k):
    """The probe set = sorted distinct {1, k, k+1, n}."""
    return sorted({1, k, k + 1, n})


# ---- exact inclusion probability, LITERAL Fraction product (no telescoping) --
def inclusion_prob_exact(i, n, k):
    """Inclusion probability of item i after all n items, computed as a literal
    product of Fractions multiplied out in a loop - NOT hardcoded to k/n.
      i <= k: prod_{t=k+1..n} (t-1)/t
      i >  k: (k/i) * prod_{t=i+1..n} (t-1)/t
    """
    if i <= k:
        prob = Fraction(1)
        for t in range(k + 1, n + 1):
            prob *= Fraction(t - 1, t)
        return prob
    prob = Fraction(k, i)
    for t in range(i + 1, n + 1):
        prob *= Fraction(t - 1, t)
    return prob


# ---- Algorithm R (correct) and the unconditional-replace bug (G4) -----------
def algorithm_r(rng, n, k, order):
    """Run Algorithm R. order[i-1] is the item identity arriving at stream
    position i. Returns the final reservoir as a list of item identities."""
    reservoir = [0] * k
    for i in range(1, n + 1):
        item = order[i - 1]
        if i <= k:
            reservoir[i - 1] = item
        else:
            j = rng.randint(1, i)          # uniform integer in [1, i]
            if j <= k:                     # ACCEPTANCE gate: replace iff j<=k
                reservoir[j - 1] = item
    return reservoir


def algorithm_r_buggy(rng, n, k, order):
    """The unconditional-replace BUG: for i>k pick j uniform in [1,k] and ALWAYS
    replace reservoir[j-1] (the j<=i acceptance gate is omitted). Over-replaces,
    so late items are over-represented and inclusion deviates from k/n."""
    reservoir = [0] * k
    for i in range(1, n + 1):
        item = order[i - 1]
        if i <= k:
            reservoir[i - 1] = item
        else:
            j = rng.randint(1, k)          # BUG: uniform in [1,k], ALWAYS replace
            reservoir[j - 1] = item
    return reservoir


def mc_inclusion(rng, n, k, order, probes, T, run):
    """Empirical inclusion counts for the probe identities over T runs of `run`
    (algorithm_r or algorithm_r_buggy)."""
    counts = {p: 0 for p in probes}
    for _ in range(T):
        res = run(rng, n, k, order)
        rs = set(res)
        for p in probes:
            if p in rs:
                counts[p] += 1
    return counts


def z_score(freq, p, T):
    """Two-sided binomial z of empirical frequency freq vs target p over T runs."""
    se = math.sqrt(p * (1.0 - p) / T)
    return (freq - p) / se, se


# ---- G1: EXACT identity - every item's Fraction product == k/n --------------
def gate_g1():
    per_config = {}
    ok = True
    for (n, k) in CONFIGS:
        target = Fraction(k, n)
        all_eq = True
        for i in range(1, n + 1):
            if inclusion_prob_exact(i, n, k) != target:
                all_eq = False
        ok = ok and all_eq
        # concrete sampled fractions at the structurally interesting positions
        sample = {}
        for i in probe_items(n, k):
            f = inclusion_prob_exact(i, n, k)
            sample[str(i)] = {"prob": frac_str(f), "equals_k_over_n": (f == target)}
        per_config["{0},{1}".format(n, k)] = {
            "n": n,
            "k": k,
            "target_k_over_n": frac_str(target),
            "items_checked": n,
            "all_items_equal_k_over_n": all_eq,
            "sample": sample,
        }
    return ok, per_config


# ---- G2: Monte-Carlo agreement, |z| < 3 for every probe ---------------------
def gate_g2(rng):
    per_config = {}
    ok = True
    for (n, k) in CONFIGS:
        order = list(range(1, n + 1))
        probes = probe_items(n, k)
        p = k / n
        counts = mc_inclusion(rng, n, k, order, probes, MC_TRIALS, algorithm_r)
        max_abs_z = 0.0
        per_probe = {}
        for pr in probes:
            freq = counts[pr] / MC_TRIALS
            z, se = z_score(freq, p, MC_TRIALS)
            good = abs(z) < Z_AGREE
            ok = ok and good
            max_abs_z = max(max_abs_z, abs(z))
            per_probe[str(pr)] = {
                "freq": round(freq, 9),
                "z": round(z, 6),
                "within_3sigma": good,
            }
        per_config["{0},{1}".format(n, k)] = {
            "n": n,
            "k": k,
            "p_k_over_n": round(p, 9),
            "trials": MC_TRIALS,
            "se": round(math.sqrt(p * (1.0 - p) / MC_TRIALS), 12),
            "probes": probes,
            "per_probe": per_probe,
            "max_abs_z": round(max_abs_z, 6),
            "all_within_3sigma": all(v["within_3sigma"] for v in per_probe.values()),
        }
    return ok, per_config


# ---- G3: robustness - order-independence (a) + subset uniformity (b) ---------
def gate_g3(rng):
    # (a) order-independence: one fixed shuffled arrival order, probe inclusion
    #     of each identity must still land within |z|<3.
    n, k = UR_CFG
    order = list(range(1, n + 1))
    rng.shuffle(order)
    probes = probe_items(n, k)
    p = k / n
    counts = mc_inclusion(rng, n, k, order, probes, MC_TRIALS, algorithm_r)
    order_ok = True
    a_probe = {}
    a_max_abs_z = 0.0
    for pr in probes:
        freq = counts[pr] / MC_TRIALS
        z, se = z_score(freq, p, MC_TRIALS)
        good = abs(z) < Z_AGREE
        order_ok = order_ok and good
        a_max_abs_z = max(a_max_abs_z, abs(z))
        a_probe[str(pr)] = {
            "freq": round(freq, 9),
            "z": round(z, 6),
            "within_3sigma": good,
        }
    order_independence = {
        "config": [n, k],
        "arrival_order_shuffled": True,
        "trials": MC_TRIALS,
        "probes": probes,
        "per_probe": a_probe,
        "max_abs_z": round(a_max_abs_z, 6),
        "all_within_3sigma": order_ok,
    }

    # (b) subset uniformity: tally the C(6,3)=20 distinct reservoir subsets,
    #     chi-square vs uniform expectation T/20.
    sn, sk = SUBSET_CFG
    sorder = list(range(1, sn + 1))
    tally = {}
    for _ in range(SUBSET_TRIALS):
        res = algorithm_r(rng, sn, sk, sorder)
        key = tuple(sorted(res))
        tally[key] = tally.get(key, 0) + 1
    num_subsets = math.comb(sn, sk)
    expected = SUBSET_TRIALS / num_subsets
    chisq = sum((c - expected) ** 2 / expected for c in tally.values())
    # subsets that never appeared still contribute (0-expected)^2/expected each
    chisq += (num_subsets - len(tally)) * (expected ** 2 / expected)
    counts_list = list(tally.values())
    subset_ok = (len(tally) == num_subsets) and (chisq < CHISQ_CRIT)
    subset_uniformity = {
        "config": [sn, sk],
        "distinct_subsets_possible": num_subsets,
        "distinct_subsets_observed": len(tally),
        "trials": SUBSET_TRIALS,
        "expected_per_subset": round(expected, 6),
        "min_count": min(counts_list),
        "max_count": max(counts_list),
        "chi_square": round(chisq, 6),
        "chi_square_crit_0p001_df19": CHISQ_CRIT,
        "uniform_within_crit": subset_ok,
    }

    ok = order_ok and subset_ok
    return ok, {
        "order_independence": order_independence,
        "subset_uniformity": subset_uniformity,
        "both_hold": ok,
    }


# ---- G4: falsifiability - the unconditional-replace bug REJECTED at |z|>=6 ---
def gate_g4(rng):
    n, k = UR_CFG
    order = list(range(1, n + 1))
    probes = probe_items(n, k)
    p = k / n
    counts = mc_inclusion(rng, n, k, order, probes, UR_TRIALS, algorithm_r_buggy)
    per_probe = {}
    max_abs_z = 0.0
    for pr in probes:
        freq = counts[pr] / UR_TRIALS
        z, se = z_score(freq, p, UR_TRIALS)
        max_abs_z = max(max_abs_z, abs(z))
        per_probe[str(pr)] = {
            "freq": round(freq, 9),
            "z": round(z, 6),
            "deviates_from_k_over_n": abs(z) >= Z_REJECT,
        }
    buggy_rejected = max_abs_z >= Z_REJECT

    # second rejected alternative: analytic "first-k" naive model, inclusion
    # {1 for i<=k, 0 for i>k}, which contradicts the exact k/n for every i>k
    # (and for i<=k whenever k<n). Purely analytic - no rng.
    target = Fraction(k, n)
    naive_probe = {}
    naive_rejected = True
    for pr in probes:
        naive_val = Fraction(1) if pr <= k else Fraction(0)
        neq = (naive_val != target)
        naive_rejected = naive_rejected and neq
        naive_probe[str(pr)] = {
            "naive_inclusion": frac_str(naive_val),
            "true_k_over_n": frac_str(target),
            "naive_neq_true": neq,
        }

    ok = buggy_rejected and naive_rejected
    return ok, {
        "unconditional_replace_bug": {
            "model": "for i>k pick j uniform in [1,k] and ALWAYS replace (no j<=i gate)",
            "config": [n, k],
            "trials": UR_TRIALS,
            "p_k_over_n": round(p, 9),
            "probes": probes,
            "per_probe": per_probe,
            "max_abs_z": round(max_abs_z, 6),
            "rejected_at_z_ge_6": buggy_rejected,
        },
        "first_k_naive_model": {
            "model": "inclusion = 1 for i<=k, 0 for i>k",
            "per_probe": naive_probe,
            "rejected": naive_rejected,
        },
        "both_wrong_models_rejected": ok,
    }


def run_battery():
    rng = random.Random(SEED)
    g1_ok, g1 = gate_g1()
    g2_ok, g2 = gate_g2(rng)
    g3_ok, g3 = gate_g3(rng)
    g4_ok, g4 = gate_g4(rng)

    gates = {"G1": g1_ok, "G2": g2_ok, "G3": g3_ok, "G4": g4_ok}
    sim_ready = all(gates.values())
    return {
        "proposal": "PROPOSAL 221",
        "verdict": 234,
        "theorem": "Reservoir sampling Algorithm R - uniform k/n inclusion",
        "algorithm": "R (Waterman / Knuth TAOCP Vol.2 / Vitter)",
        "seed": SEED,
        "configs": [list(c) for c in CONFIGS],
        "g1_exact_identity": g1,
        "g2_montecarlo": g2,
        "g3_robustness": g3,
        "g4_falsifiability": g4,
        "gates": gates,
        "sim_ready": sim_ready,
    }


def digest(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


if __name__ == "__main__":
    import sys

    r1 = run_battery()
    r2 = run_battery()
    d1 = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    d2 = json.dumps(r2, sort_keys=True, separators=(",", ":"))
    determinism = (d1 == d2)
    sim_ready = r1["sim_ready"]
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("results_sha256={0}".format(digest(r1)))
    print("determinism_double_run={0}".format(determinism))
    print("sim_ready={0}".format(sim_ready))
    sys.exit(0 if (sim_ready and determinism) else 1)
