#!/usr/bin/env python3
"""PROPOSAL 245 — open-addressing unsuccessful search: expected probes = (m+1)/(m-n+1).

HEAD: An open-addressing hash table under the UNIFORM-HASHING model (each key's
probe sequence is a uniformly random permutation of all m slots). With m slots
and n occupied (load factor alpha = n/m), the EXPECTED number of probes in an
UNSUCCESSFUL search is EXACTLY

    E_unsucc(m, n) = (m + 1) / (m - n + 1).

As m, n -> infinity at fixed alpha this increases monotonically to the classic
closed form 1/(1 - alpha).

WHY (exact combinatorial definition). An unsuccessful search probes slots in a
uniformly random order and stops at the first EMPTY slot (which certifies the
key is absent). The number of probes equals the position of the first empty slot
in the probe permutation. Writing the count as a sum of tail events,

    E = sum_{i>=0} P(first i probes all land on OCCUPIED slots)
      = sum_{i=0}^{n}  n/m * (n-1)/(m-1) * ... * (n-i+1)/(m-i+1)
      = sum_{i=0}^{n}  C(n, i) / C(m, i).

This finite sum equals (m+1)/(m-n+1). PROOF (exact, hockey-stick):
  C(n,i)/C(m,i) = C(m-i, n-i)/C(m,n)  (both equal n!(m-i)! / ((n-i)! m!)), so
    sum_{i=0}^{n} C(n,i)/C(m,i) = (1/C(m,n)) sum_{i=0}^{n} C(m-i, n-i)
                                = (1/C(m,n)) sum_{j=0}^{n} C(m-n+j, j)   (j=n-i)
                                = C(m+1, n) / C(m,n)                     (hockey-stick)
                                = (m+1)/(m-n+1).
The verifier checks the sum-of-products definition against (m+1)/(m-n+1) as exact
fractions.Fraction values (route (a) the finite sum, route (b) the closed form,
route (c) the hockey-stick ratio C(m+1,n)/C(m,n)) with ZERO tolerance.

Gate battery (SEED=20260717; each gate in its OWN direction):
  G1 EXACT identity (fractions.Fraction, zero tolerance): over a battery of (m,n)
     pairs the exact sum-of-products definition sum_i C(n,i)/C(m,i) equals
     (m+1)/(m-n+1) AND the hockey-stick ratio C(m+1,n)/C(m,n) — 0 mismatches,
     max discrepancy exactly 0 (z is not applicable and is reported null/"exact").
     The sanity anchors (1,0)->1, (2,1)->3/2, (3,2)->2, (10,7)->11/4 are pinned.
  G2 MC AGREEMENT (|z| < 3): simulate the ACTUAL uniform-hashing unsuccessful
     search — draw a uniformly random permutation of the m slots (random.sample
     with the seeded RNG), n of them occupied, count probes until the first empty
     slot; average over N i.i.d. trials. These trials are INDEPENDENT (exactly one
     probe-count per trial), so NO thinning is needed. z = (mean_hat - E_exact) /
     (s / sqrt(N)) using the sample std s. Headline (m=100, n=70), N=200000.
  G3 INVARIANCE / ROBUSTNESS (own direction): the expected probe count depends
     ONLY on (m,n), not on WHICH slots are occupied. Two occupancy configurations
     at the same (m,n) — occupied = the first n slots vs occupied = a fixed
     pseudo-random n-subset — both MC means agree with E_exact and with each other
     (two-sample difference z, |z| < 3). Robustness sub-check: E_unsucc(m, alpha*m)
     is monotone increasing in m at fixed alpha and converges to 1/(1-alpha),
     verified EXACTLY with Fractions.
  G4 FALSIFIABILITY (|z_naive| >> 3): the plausible naive alternative "expected
     probes = 1/(1-alpha) exactly at finite (m,n)" is FALSE for finite tables. On
     the SAME headline MC sample, z against the naive value 1/(1-alpha) must
     REJECT at large |z| (at m=100,n=70 exact=101/31~3.258 vs naive=10/3~3.333).
     The gate PASSES by rejecting the naive alternative while G2 agrees with exact.

Determinism posture: build_results() is a pure function of SEED and the fixed
module constants. A single random.Random(SEED) is seeded once and consumed in a
fixed order across all Monte-Carlo legs; the exact-Fraction kernel is deterministic
rational arithmetic. Every float serializes via a fixed format string and every
exact rational via str(Fraction), so no wall-clock / PID / unordered-set iteration
enters the hashed payload. main() builds the results twice in one process and
asserts the canonical JSON forms are byte-identical (in-process double-run guard),
supports a --selfcheck flag that prints "SELFCHECK: byte-identical", prints a human
summary and `results_sha256=<64hex>` on its own line, and exits 1 if any gate fails.
"""

import hashlib
import json
import math
import random
import sys
from fractions import Fraction

SEED = 20260717
Z_ACCEPT = 3.0   # G2 / G3 agreement band
Z_REJECT = 3.0   # G4 rejection threshold for the naive alternative

# Headline configuration for the shared G2 / G4 Monte-Carlo sample.
M_HEAD = 100
N_HEAD = 70
N_TRIALS = 200_000     # i.i.d. unsuccessful-search trials (one probe-count each)
N_INV = 200_000        # trials per occupancy configuration for G3


def fmt(x):
    """Fixed float format so the serialization is invocation-stable."""
    return f"{float(x):.10f}"


def comb(a, b):
    return math.comb(a, b)


def e_sum_of_products(m, n):
    """Exact E as the finite sum sum_{i=0}^{n} C(n,i)/C(m,i) (Fraction)."""
    total = Fraction(0)
    for i in range(0, n + 1):
        total += Fraction(comb(n, i), comb(m, i))
    return total


def e_closed_form(m, n):
    """Exact closed form (m+1)/(m-n+1) (Fraction)."""
    return Fraction(m + 1, m - n + 1)


def e_hockey_stick(m, n):
    """Exact C(m+1,n)/C(m,n) route (Fraction)."""
    return Fraction(comb(m + 1, n), comb(m, n))


def probes_to_first_empty(m, occ, rng):
    """One uniform-hashing unsuccessful search.

    Draw a uniformly random permutation of the m slots and walk it, counting
    probes until the first EMPTY slot. `occ` is a boolean list of length m
    (occ[s] is True when slot s is occupied). Returns the probe count (the
    terminating empty slot IS counted, so the minimum is 1)."""
    perm = rng.sample(range(m), m)   # uniformly random permutation of all m slots
    probes = 0
    for slot in perm:
        probes += 1
        if not occ[slot]:
            return probes
    return probes  # unreachable when m > n (there is always an empty slot)


def run_trials(m, occ, n_trials, rng):
    """Run n_trials i.i.d. searches; return (mean, sample_std, n)."""
    total = 0
    total_sq = 0
    for _ in range(n_trials):
        p = probes_to_first_empty(m, occ, rng)
        total += p
        total_sq += p * p
    mean = total / n_trials
    var = (total_sq - n_trials * mean * mean) / (n_trials - 1)
    if var < 0.0:
        var = 0.0
    return mean, math.sqrt(var), n_trials


def z_vs(mean, s, n, target):
    """z-score of the sample mean against a target value using the sample std."""
    se = s / math.sqrt(n)
    return (mean - target) / se


def build_results():
    rng = random.Random(SEED)  # seeded once; consumed in a fixed order below

    results = {
        "proposal": 245,
        "claim": (
            "Open-addressing hash table under uniform hashing (each key's probe "
            "sequence is a uniformly random permutation of all m slots): with m "
            "slots and n occupied (alpha=n/m), the expected probes in an "
            "UNSUCCESSFUL search is exactly (m+1)/(m-n+1), converging monotonically "
            "to 1/(1-alpha) as m,n -> infinity at fixed alpha."
        ),
        "seed": SEED,
        "z_accept": fmt(Z_ACCEPT),
        "z_reject": fmt(Z_REJECT),
        "m_head": M_HEAD,
        "n_head": N_HEAD,
        "n_trials": N_TRIALS,
        "n_inv": N_INV,
    }

    # --- G1 EXACT identity via fractions.Fraction (zero tolerance) -------------
    battery = [
        (1, 0), (2, 1), (3, 2), (5, 3), (10, 7), (13, 0),
        (16, 8), (23, 17), (50, 35), (100, 70), (128, 96), (257, 200),
    ]
    anchors = {
        "(1,0)": Fraction(1),
        "(2,1)": Fraction(3, 2),
        "(3,2)": Fraction(2),
        "(10,7)": Fraction(11, 4),
    }
    mismatches = 0
    anchor_mismatches = 0
    exact_rows = []
    for (m, n) in battery:
        e_sum = e_sum_of_products(m, n)
        e_cf = e_closed_form(m, n)
        e_hs = e_hockey_stick(m, n)
        if not (e_sum == e_cf == e_hs):
            mismatches += 1
        key = f"({m},{n})"
        if key in anchors and e_sum != anchors[key]:
            anchor_mismatches += 1
        exact_rows.append({
            "m": m, "n": n,
            "E": f"{e_sum.numerator}/{e_sum.denominator}",
            "E_float": fmt(e_sum),
        })
    # naive-vs-exact contrast pinned exactly at the headline (m=100, n=70).
    e_head_exact = e_closed_form(M_HEAD, N_HEAD)           # 101/31
    alpha_head = Fraction(N_HEAD, M_HEAD)                  # 7/10
    naive_head = Fraction(1) / (Fraction(1) - alpha_head)  # 10/3
    g1_pass = (mismatches == 0) and (anchor_mismatches == 0)
    results["G1_exact_identity"] = {
        "battery_size": len(battery),
        "mismatches": mismatches,
        "anchor_mismatches": anchor_mismatches,
        "max_discrepancy": "0",
        "z": None,                     # exact identity: z not applicable
        "z_note": "exact",
        "anchors": {k: f"{v.numerator}/{v.denominator}" for k, v in anchors.items()},
        "head_exact": f"{e_head_exact.numerator}/{e_head_exact.denominator}",
        "head_naive": f"{naive_head.numerator}/{naive_head.denominator}",
        "rows": exact_rows,
        "pass": g1_pass,
    }

    # --- G2 MC agreement at the headline (m=100, n=70), |z| < 3 ----------------
    # occupied = the first n slots; the walk uses a uniformly random probe order.
    occ_head = [s < N_HEAD for s in range(M_HEAD)]
    e_head = float(e_head_exact)
    mean2, s2, n2 = run_trials(M_HEAD, occ_head, N_TRIALS, rng)
    z2 = z_vs(mean2, s2, n2, e_head)
    g2_pass = abs(z2) < Z_ACCEPT
    results["G2_mc_agreement"] = {
        "m": M_HEAD, "n": N_HEAD,
        "E_exact": f"{e_head_exact.numerator}/{e_head_exact.denominator}",
        "E_exact_float": fmt(e_head),
        "n_trials": N_TRIALS,
        "mean_hat": fmt(mean2),
        "sample_std": fmt(s2),
        "z": fmt(z2),
        "iid_no_thinning": True,
        "pass": g2_pass,
    }

    # --- G3 invariance: mean depends only on (m,n), not WHICH slots occupied ---
    # config A: occupied = first n slots; config B: fixed pseudo-random n-subset.
    occ_A = [s < N_HEAD for s in range(M_HEAD)]
    subset_rng = random.Random(0xA55E7)   # FIXED, independent of the MC stream
    subset = set(subset_rng.sample(range(M_HEAD), N_HEAD))
    occ_B = [s in subset for s in range(M_HEAD)]
    meanA, sA, nA = run_trials(M_HEAD, occ_A, N_INV, rng)
    meanB, sB, nB = run_trials(M_HEAD, occ_B, N_INV, rng)
    zA = z_vs(meanA, sA, nA, e_head)
    zB = z_vs(meanB, sB, nB, e_head)
    se_diff = math.sqrt(sA * sA / nA + sB * sB / nB)
    z_AB = (meanA - meanB) / se_diff
    # robustness sub-check: EXACT monotone convergence to 1/(1-alpha) at fixed alpha.
    alpha = Fraction(7, 10)
    conv_ms = [10, 100, 1000, 10000, 100000]
    conv_vals = [e_closed_form(m, int(alpha * m)) for m in conv_ms]
    limit = Fraction(1) / (Fraction(1) - alpha)   # 10/3
    monotone_increasing = all(conv_vals[i] < conv_vals[i + 1]
                              for i in range(len(conv_vals) - 1))
    below_limit = all(v < limit for v in conv_vals)
    approaches = (limit - conv_vals[-1]) < (limit - conv_vals[0])
    g3_pass = (abs(zA) < Z_ACCEPT and abs(zB) < Z_ACCEPT and abs(z_AB) < Z_ACCEPT
               and monotone_increasing and below_limit and approaches)
    results["G3_invariance_robustness"] = {
        "config_A": {"occupied": "first_n_slots", "mean_hat": fmt(meanA), "z": fmt(zA)},
        "config_B": {"occupied": "fixed_pseudorandom_subset", "mean_hat": fmt(meanB), "z": fmt(zB)},
        "z_invariance_AB": fmt(z_AB),
        "convergence": {
            "alpha": f"{alpha.numerator}/{alpha.denominator}",
            "limit": f"{limit.numerator}/{limit.denominator}",
            "ms": conv_ms,
            "vals": [f"{v.numerator}/{v.denominator}" for v in conv_vals],
            "monotone_increasing": monotone_increasing,
            "below_limit": below_limit,
            "approaches_limit": approaches,
        },
        "pass": g3_pass,
    }

    # --- G4 falsifiability: reject naive 1/(1-alpha) on the SAME G2 sample -----
    naive_val = float(naive_head)   # 10/3 ~ 3.3333
    z_naive = z_vs(mean2, s2, n2, naive_val)
    g4_pass = abs(z_naive) > Z_REJECT
    results["G4_falsifiability"] = {
        "naive_claim": "expected probes = 1/(1-alpha) exactly at finite (m,n)",
        "naive_value": f"{naive_head.numerator}/{naive_head.denominator}",
        "naive_value_float": fmt(naive_val),
        "exact_value": f"{e_head_exact.numerator}/{e_head_exact.denominator}",
        "z_abs": fmt(abs(z_naive)),
        "rejected": g4_pass,
        "same_sample_agrees_exact": g2_pass,
        "pass": g4_pass,
    }

    gates = {
        "G1": results["G1_exact_identity"]["pass"],
        "G2": results["G2_mc_agreement"]["pass"],
        "G3": results["G3_invariance_robustness"]["pass"],
        "G4": results["G4_falsifiability"]["pass"],
    }
    order = ["G1", "G2", "G3", "G4"]
    results["gates"] = gates
    results["first_failing_gate"] = next((k for k in order if not gates[k]), None)
    results["all_pass"] = all(gates[k] for k in order)
    return results


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def compute_digest():
    r1 = build_results()
    r2 = build_results()
    c1 = canonical(r1)
    c2 = canonical(r2)
    identical = (c1 == c2)
    digest = hashlib.sha256(c1.encode("utf-8")).hexdigest()
    return r1, c1, identical, digest


def main():
    selfcheck = "--selfcheck" in sys.argv[1:]
    r1, c1, identical, digest = compute_digest()
    if not identical:
        sys.stderr.write("NON-DETERMINISTIC: in-process double-run diverged\n")
        sys.exit(3)

    if selfcheck:
        print("SELFCHECK: byte-identical")
        print(f"results_sha256={digest}")
        sys.exit(0 if r1["all_pass"] else 1)

    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    for key in ["G1", "G2", "G3", "G4"]:
        print(f"{key}: {'PASS' if r1['gates'][key] else 'FAIL'}")
    print()
    print(f"in_process_double_run: {'IDENTICAL' if identical else 'DIVERGED'}")
    print(f"all_pass: {r1['all_pass']}")
    print(f"first_failing_gate: {r1['first_failing_gate']}")
    print(f"results_sha256={digest}")
    sys.exit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
