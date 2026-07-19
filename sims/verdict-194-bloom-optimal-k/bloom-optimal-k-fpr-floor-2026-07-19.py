#!/usr/bin/env python3
"""PROPOSAL 181 - Bloom filter: past the optimum, more hash functions make false
positives WORSE, and no tuning beats the bits-per-element floor (round-43 FLEET slot).

Head: a Bloom filter's false-positive rate is convex (U-shaped) in the number of
hash functions k, minimized at k* = (m/n) ln 2 (m bits, n inserted elements).
Adding hashes past k* makes false positives climb again -- each extra hash sets
another bit and saturates the array faster, and past the optimum that fill cost
outweighs the extra checking. Moreover the achievable minimum is floored at
phi = (1/2)^{(m/n) ln 2} = ~0.6185^{m/n}, set by bits-per-element ALONE: no choice
of k crosses that floor; only more memory per element lowers it.

Folk belief: more hash functions = more independent checks = monotonically fewer
false positives.
Counterintuitive truth: FPR(k) = (1 - e^{-kn/m})^k is U-shaped in k; past the
optimum more hashes HURT, and the best rate is memory-bound, not tuning-bound.

Anchor: Bloom (1970); the optimal k = (m/n) ln 2 and FPR = (1 - e^{-kn/m})^k
(Wikipedia "Bloom filter"). Hash indices derived by Kirsch-Mitzenmacher double
hashing (h_i = g1 + i*g2), which the same source documents.

Pre-registered gates (>=3 sigma, each tests the head):
  G1  optimum dominance (c = m/n = 8): empirical FPR at k=1 AND at k=2k* each
      strictly exceed FPR at k*, both with z >= 3 -- both ends worse than optimum.
  G2  more-hashes-hurt (the head) + floor: the past-optimum penalty
      FPR(2k*) - FPR(k*) > 0 with z >= 3, AND the achieved optimum sits at the
      bits-per-element floor phi (|FPR(k*) - phi| <= TOL*phi and no tested k beats
      phi by more than TOL) -- tuning cannot cross the memory floor.
  G3  robustness under a shifted config (c = 12): dominance and the past-optimum
      penalty persist with z >= 3, and the optimum again matches its floor.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. sha256 of the
compact-canonical results dict IS the digest; stdout dump pretty indent=2, floats
6 dp. Deterministic: per-(config,trial) salts from SEED; in-process double-run
asserted; cross-invocation identical.
"""

import hashlib
import json
import math

SEED = 20260717
N = 1500            # elements inserted per trial
Q = 1500            # absent elements queried per trial
R = 150             # trials per (config, k)
Z_GATE = 3.0
TOL = 0.20          # relative tolerance for the bits-per-element floor match
LN2 = math.log(2.0)
CONFIG_STRIDE = 1_000_003
TRIAL_STRIDE = 7919


def predicted_fpr(c, k):
    # c = m/n ; kn/m = k/c
    return (1.0 - math.exp(-k / c)) ** k


def floor_fpr(c):
    # phi = (1/2)^{c ln2} = 0.6185...^c ; the minimum achievable FPR at optimal k
    return 0.5 ** (c * LN2)


def k_opt(c):
    # integer k >= 1 minimizing predicted FPR near (m/n) ln 2
    kstar = max(1, int(round(c * LN2)))
    best, bestf = kstar, predicted_fpr(c, kstar)
    for k in (kstar - 1, kstar + 1):
        if k >= 1:
            f = predicted_fpr(c, k)
            if f < bestf:
                best, bestf = k, f
    return best


def _g1g2(salt, x, m):
    d = hashlib.sha256(("%d:%d" % (salt, x)).encode()).digest()
    g1 = int.from_bytes(d[0:8], "big") % m
    g2 = (int.from_bytes(d[8:16], "big") % m) | 1   # odd stride
    return g1, g2


def _trial_fpr(c, k, salt):
    m = int(round(c * N))
    bits = bytearray(m)
    for x in range(N):                       # insert N present elements
        g1, g2 = _g1g2(salt, x, m)
        for i in range(k):
            bits[(g1 + i * g2) % m] = 1
    fp = 0
    for x in range(N, 2 * N):                # query N absent elements
        g1, g2 = _g1g2(salt, x, m)
        hit = True
        for i in range(k):
            if not bits[(g1 + i * g2) % m]:
                hit = False
                break
        if hit:
            fp += 1
    return fp / Q


def _mean_se(xs):
    n = len(xs)
    mean = sum(xs) / n
    var = sum((v - mean) ** 2 for v in xs) / (n - 1)
    return mean, math.sqrt(var / n)


def _z(diff, se_a, se_b):
    se = math.sqrt(se_a ** 2 + se_b ** 2)
    return diff / se if se > 0 else float("inf")


def _measure(c, config_idx):
    kstar = k_opt(c)
    klow, khigh = 1, 2 * kstar
    means, ses = {}, {}
    for tag, k in (("low", klow), ("opt", kstar), ("high", khigh)):
        vals = []
        for t in range(R):
            salt = SEED + config_idx * CONFIG_STRIDE + t * TRIAL_STRIDE
            vals.append(_trial_fpr(c, k, salt))
        m, se = _mean_se(vals)
        means[tag], ses[tag] = m, se
    z_low = _z(means["low"] - means["opt"], ses["low"], ses["opt"])
    z_high = _z(means["high"] - means["opt"], ses["high"], ses["opt"])
    phi = floor_fpr(c)
    min_emp = min(means["low"], means["opt"], means["high"])
    dom = (means["low"] - means["opt"] > 0 and z_low >= Z_GATE and
           means["high"] - means["opt"] > 0 and z_high >= Z_GATE)
    penalty = means["high"] - means["opt"]
    penalty_sig = penalty > 0 and z_high >= Z_GATE
    floor_ok = (abs(means["opt"] - phi) <= TOL * phi and min_emp >= phi * (1.0 - TOL))
    return {
        "bits_per_elem": c,
        "m_bits": int(round(c * N)),
        "k_low": klow, "k_opt": kstar, "k_high": khigh,
        "fpr_low": means["low"], "fpr_opt": means["opt"], "fpr_high": means["high"],
        "se_low": ses["low"], "se_opt": ses["opt"], "se_high": ses["high"],
        "z_low_vs_opt": z_low, "z_high_vs_opt": z_high,
        "fpr_opt_predicted": predicted_fpr(c, kstar),
        "floor_phi": phi,
        "penalty_high_minus_opt": penalty,
        "dom_pass": dom, "penalty_sig": penalty_sig, "floor_pass": floor_ok,
    }


def r6(x):
    return round(float(x), 6)


def compute():
    base = _measure(8, 0)
    shift = _measure(12, 1)
    g1 = base["dom_pass"]
    g2 = base["penalty_sig"] and base["floor_pass"]
    g3 = shift["dom_pass"] and shift["penalty_sig"] and shift["floor_pass"]
    all_pass = bool(g1 and g2 and g3)

    def pack(d):
        return {
            "bits_per_elem": d["bits_per_elem"],
            "m_bits": d["m_bits"],
            "k_low": d["k_low"], "k_opt": d["k_opt"], "k_high": d["k_high"],
            "fpr_low": r6(d["fpr_low"]), "fpr_opt": r6(d["fpr_opt"]),
            "fpr_high": r6(d["fpr_high"]),
            "se_low": r6(d["se_low"]), "se_opt": r6(d["se_opt"]),
            "se_high": r6(d["se_high"]),
            "z_low_vs_opt": r6(d["z_low_vs_opt"]),
            "z_high_vs_opt": r6(d["z_high_vs_opt"]),
            "fpr_opt_predicted": r6(d["fpr_opt_predicted"]),
            "floor_phi": r6(d["floor_phi"]),
            "penalty_high_minus_opt": r6(d["penalty_high_minus_opt"]),
            "dom_pass": d["dom_pass"], "penalty_sig": d["penalty_sig"],
            "floor_pass": d["floor_pass"],
        }

    return {
        "head": "bloom filter: past the optimum k*, more hash functions raise the false-positive rate; the minimum is floored by bits-per-element",
        "seed": SEED,
        "n_elements": N,
        "n_queries": Q,
        "trials": R,
        "z_gate": r6(Z_GATE),
        "tol": r6(TOL),
        "base_config_c8": pack(base),
        "shift_config_c12": pack(shift),
        "gate_g1_optimum_dominance_pass": bool(g1),
        "gate_g2_more_hashes_hurt_and_floor_pass": bool(g2),
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
    print("G1 optimum dominance:        " +
          ("PASS" if results["gate_g1_optimum_dominance_pass"] else "FAIL"))
    print("G2 more-hashes-hurt + floor: " +
          ("PASS" if results["gate_g2_more_hashes_hurt_and_floor_pass"] else "FAIL"))
    print("G3 robust (shifted config):  " +
          ("PASS" if results["gate_g3_robust_shift_pass"] else "FAIL"))
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
