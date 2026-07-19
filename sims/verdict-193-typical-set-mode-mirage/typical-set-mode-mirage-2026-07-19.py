#!/usr/bin/env python3
"""PROPOSAL 180 - Typical-set "mode mirage" (round-42 UNRELATED slot; information theory).

Head: for n i.i.d. Bernoulli(p) symbols with p != 1/2, the single most-probable
sequence (the mode: the all-majority-symbol string) is essentially never observed,
yet every observed sequence carries per-symbol surprisal concentrated at the Shannon
entropy H(p) -- and is therefore individually far LESS probable than the mode you
never see. Probability mass concentrates AWAY from the probability maximum: Shannon's
Asymptotic Equipartition Property (the typical set).

Grounding: Asymptotic Equipartition Property (Shannon 1948; Cover & Thomas, ch. 3).

Constraints: stdlib-only; SEED pinned; deterministic; in-process double-run asserted;
WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY digest (sha256 of the compact-canonical
results dict IS the digest; the dict is not self-referential; floats 6 dp).
"""

import hashlib
import json
import math
import random
import sys

SEED = 20260717
N = 1000        # symbols per sequence
M = 4000        # sequences sampled per distribution
EPS = 0.10      # bits; half-width of the typical band around H(p)
Z_GATE = 3.0


def entropy_bits(p):
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)


def mode_surprisal_bits(p):
    # per-symbol surprisal of the modal (all-majority-symbol) sequence
    return -math.log2(max(p, 1.0 - p))


def simulate(p, seed):
    """Draw M Bernoulli(p) sequences of length N. Return entropy-rate stats
    (bits/symbol) and the count of the exact modal sequence among the M draws."""
    rng = random.Random(seed)
    log2_p = math.log2(p)
    log2_q = math.log2(1.0 - p)
    majority_is_one = p >= 0.5
    H = entropy_bits(p)
    hrates = []
    mode_count = 0
    for _ in range(M):
        ones = 0
        for _ in range(N):
            if rng.random() < p:
                ones += 1
        zeros = N - ones
        hrate = -(ones * log2_p + zeros * log2_q) / N
        hrates.append(hrate)
        if (majority_is_one and ones == N) or ((not majority_is_one) and ones == 0):
            mode_count += 1
    mean = sum(hrates) / M
    var = sum((h - mean) ** 2 for h in hrates) / (M - 1)
    sd = math.sqrt(var)
    se = sd / math.sqrt(M)
    in_band = sum(1 for h in hrates if abs(h - H) <= EPS) / M
    return mean, sd, se, in_band, mode_count


def compute():
    # base distribution
    p0 = 0.7
    h0 = entropy_bits(p0)
    s0 = mode_surprisal_bits(p0)
    mean0, sd0, se0, band0, mode0 = simulate(p0, SEED)
    z_conc0 = abs(mean0 - h0) / se0
    z_sep0 = (mean0 - s0) / se0

    # shifted distribution (robustness under a distribution shift)
    p1 = 0.9
    h1 = entropy_bits(p1)
    s1 = mode_surprisal_bits(p1)
    mean1, sd1, se1, band1, mode1 = simulate(p1, SEED)
    z_conc1 = abs(mean1 - h1) / se1
    z_sep1 = (mean1 - s1) / se1

    g1 = (abs(mean0 - h0) <= EPS) and (band0 >= 0.99)
    g2 = (z_sep0 >= Z_GATE) and (mode0 == 0)
    g3 = (abs(mean1 - h1) <= EPS) and (band1 >= 0.99) and (z_sep1 >= Z_GATE) and (mode1 == 0)
    all_pass = bool(g1 and g2 and g3)

    return {
        "head": "typical-set mode mirage: the most-probable sequence is never observed",
        "seed": SEED,
        "n_symbols": N,
        "n_sequences": M,
        "eps_bits": round(EPS, 6),
        "z_gate": round(Z_GATE, 6),
        "base_p": round(p0, 6),
        "base_entropy_bits": round(h0, 6),
        "base_mode_surprisal_bits": round(s0, 6),
        "base_mean_hrate_bits": round(mean0, 6),
        "base_se_bits": round(se0, 6),
        "base_in_band_frac": round(band0, 6),
        "base_mode_count": mode0,
        "base_z_concentration": round(z_conc0, 6),
        "base_z_separation": round(z_sep0, 6),
        "shift_p": round(p1, 6),
        "shift_entropy_bits": round(h1, 6),
        "shift_mode_surprisal_bits": round(s1, 6),
        "shift_mean_hrate_bits": round(mean1, 6),
        "shift_se_bits": round(se1, 6),
        "shift_in_band_frac": round(band1, 6),
        "shift_mode_count": mode1,
        "shift_z_concentration": round(z_conc1, 6),
        "shift_z_separation": round(z_sep1, 6),
        "gate_g1_concentration_pass": bool(g1),
        "gate_g2_mode_mirage_pass": bool(g2),
        "gate_g3_robust_shift_pass": bool(g3),
        "all_pass": all_pass,
    }


def main():
    r1 = compute()
    r2 = compute()
    assert r1 == r2, "in-process double-run mismatch (non-determinism)"
    results = r1
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + digest)
    print("ALL_PASS: " + str(results["all_pass"]))
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
