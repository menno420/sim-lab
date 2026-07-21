#!/usr/bin/env python3
"""verify_261_approximate_counting.py — firsthand verifier (stdlib only).

Claim (streaming / sketch lane): Morris's approximate counting algorithm
(base-2 Morris counter) is an EXACTLY unbiased estimator of a stream count,
with an exactly computable variance.

    A counter C starts at C_0 = 0. To process ONE stream item (an increment),
    draw u ~ Uniform(0,1); if u < 2^(-C) set C := C+1, else leave C unchanged.
    After n increments the estimator is  N_hat = 2^{C_n} - 1.

EXACT claim 1 (unbiasedness):   E[2^{C_n}] = n + 1  exactly,
                                hence E[N_hat] = E[2^{C_n} - 1] = n  exactly.
EXACT claim 2 (variance):       Var[N_hat] = Var[2^{C_n}] = n(n-1)/2  exactly,
                                from E[4^{C_n}] = 1 + 3 n(n+1)/2.

Proof (verified below in exact rational arithmetic, not merely trusted). Given
C_n = c, the one-step conditional moments are
    E[2^{C_{n+1}} | C_n = c] = 2^{-c} * 2^{c+1} + (1 - 2^{-c}) * 2^c
                             = 2 + 2^c - 1 = 2^c + 1,
    E[4^{C_{n+1}} | C_n = c] = 2^{-c} * 4^{c+1} + (1 - 2^{-c}) * 4^c
                             = 4 * 2^c + 4^c - 2^c = 4^c + 3 * 2^c.
Taking expectations: E[2^{C_{n+1}}] = E[2^{C_n}] + 1 with 2^{C_0} = 1, so
E[2^{C_n}] = n + 1; and E[4^{C_{n+1}}] = E[4^{C_n}] + 3 E[2^{C_n}] =
E[4^{C_n}] + 3(n+1) with 4^{C_0} = 1, so E[4^{C_n}] = 1 + 3 n(n+1)/2. Hence
Var[2^{C_n}] = (1 + 3 n(n+1)/2) - (n+1)^2 = (n^2 - n)/2 = n(n-1)/2.

Four gates, each read in its OWN direction:

  G1 EXACT (fractions.Fraction, no floats) — for n = 0..N_EXACT compute the FULL
     pmf of C_n by rational dynamic programming:
         P_0 = {0: 1};  P_{k+1}(c) = P_k(c)(1 - 2^{-c}) + P_k(c-1) 2^{-(c-1)}.
     From each exact pmf form E[2^C] = sum 2^c P(c), E[4^C] = sum 4^c P(c),
     E[N_hat] = E[2^C] - 1, Var[N_hat] = E[4^C] - (E[2^C])^2, all as exact
     Fractions, and assert with ZERO tolerance
         E[2^C] == n+1,  E[N_hat] == n,
         E[4^C] == 1 + 3 n(n+1)/2,  Var[N_hat] == Fraction(n(n-1), 2).
     Record checked count and mismatches (must be 0). z = "exact".

  G2 MC AGREEMENT (genuinely iid, |z| < 3) — n_mc = N_MC1 increments, M = M_REPL
     independent replicas. random.seed(SEED) first. Each replica: C = 0; for
     each of n_mc increments, if random.random() < 2^(-C) then C += 1; then
     est = 2^C - 1. Report the sample mean, target n_mc, and the honest iid
     standard error se = sample_sd / sqrt(M); z = (mean - n_mc)/se, assert
     |z| < 3. Cross-check the sample variance against the exact
     Var = n_mc(n_mc-1)/2 (ratio reported, not a hard gate). The replica
     sufficient statistics (sum of est, sum of est^2, sum of C, sum of C^2)
     are stored so G4 can reuse the SAME sample WITHOUT re-simulating.

  G3 INVARIANCE (0 violations + a second-scale MC) — (a) the EXACT
     martingale-increment invariance E[2^{C_{n+1}}] - E[2^{C_n}] == 1 for
     n = 0..N_EXACT-1 (0 violations) is the structural reason unbiasedness holds
     at EVERY n; (b) unbiasedness at a DIFFERENT scale: n_mc2 = N_MC2 increments,
     M2 = M_REPL2 iid replicas (re-seed random.seed(SEED)); z2 = (mean2 -
     n_mc2)/se2, assert |z2| < 3.

  G4 FALSIFIABILITY (teeth, |z| > 3, SAME n_mc = N_MC1 sample as G2) — primary
     foil "forgot the -1 correction": est_foil = 2^C, so its mean = mean_true + 1
     exactly and E = n+1 (biased high by 1); z_foil_primary = (mean_foil -
     n_mc)/se on the same se, asserted |z| > 3. Secondary foil "use the raw
     counter" est = C (E ~ log2(n) ~ 5.97 for n=63): its mean over the same
     replicas gives a hugely negative z, asserted |z| > 3. The TRUE estimator is
     confirmed accepted at |z| < 3 on the same sample.

Determinism: the results dict -> canonical JSON (sorted keys) -> sha256 (full 64
hex, never truncated). main() builds the results twice in-process and asserts
byte-equality; --selfcheck prints "SELFCHECK: byte-identical"; a separate process
re-invocation reproduces the digest byte-for-byte. random.seed(SEED) is re-seeded
at the START of each Monte-Carlo gate so gate order cannot perturb the payload.
The MC sufficient statistics are accumulated as EXACT Python integers (sum and
sum-of-squares), so no float summation-order instability enters the payload.
Stdlib only: argparse, hashlib, json, math, random, fractions, sys.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from fractions import Fraction

# ---------------------------------------------------------------------------
# Constants (all payload-affecting knobs are module-level and hardcoded).
# ---------------------------------------------------------------------------
SEED = 20260721
N_EXACT = 80          # exact rational DP for n = 0..N_EXACT
N_MC1 = 63            # G2/G4 shared Monte-Carlo scale (increments per replica)
M_REPL = 300_000      # G2/G4 number of iid replicas
N_MC2 = 31            # G3 second-scale Monte-Carlo (increments per replica)
M_REPL2 = 300_000     # G3 second-scale number of iid replicas
Z_ACCEPT = 3.0
Z_REJECT = 3.0


# ---------------------------------------------------------------------------
# Exact rational machinery (no floats).
# ---------------------------------------------------------------------------
def exact_pmf_sequence(nmax: int) -> list[dict[int, Fraction]]:
    """Return [P_0, P_1, ..., P_nmax], each an exact pmf of C_n as {c: Fraction}.

    P_0 = {0: 1};  P_{k+1}(c) = P_k(c)(1 - 2^{-c}) + P_k(c-1) 2^{-(c-1)}.
    """
    pmfs: list[dict[int, Fraction]] = []
    cur = {0: Fraction(1)}
    pmfs.append(dict(cur))
    for _ in range(nmax):
        nxt: dict[int, Fraction] = {}
        for c, p in cur.items():
            stay = Fraction(1) - Fraction(1, 2 ** c)     # prob of NOT incrementing
            inc = Fraction(1, 2 ** c)                    # prob of incrementing (to c+1)
            if stay != 0:
                nxt[c] = nxt.get(c, Fraction(0)) + p * stay
            nxt[c + 1] = nxt.get(c + 1, Fraction(0)) + p * inc
        cur = nxt
        pmfs.append(dict(cur))
    return pmfs


def moment_2c(pmf: dict[int, Fraction]) -> Fraction:
    return sum((Fraction(2 ** c) * p for c, p in pmf.items()), Fraction(0))


def moment_4c(pmf: dict[int, Fraction]) -> Fraction:
    return sum((Fraction(4 ** c) * p for c, p in pmf.items()), Fraction(0))


# ---------------------------------------------------------------------------
# G1 — EXACT unbiasedness + variance (Fraction, zero tolerance).
# ---------------------------------------------------------------------------
def gate1_exact(pmfs: list[dict[int, Fraction]]) -> dict:
    checked = 0
    mismatches = 0
    for n in range(len(pmfs)):
        pmf = pmfs[n]
        e2 = moment_2c(pmf)
        e4 = moment_4c(pmf)
        e_nhat = e2 - 1
        var_nhat = e4 - e2 * e2
        # exact targets
        t_e2 = Fraction(n + 1)
        t_e4 = Fraction(1) + Fraction(3 * n * (n + 1), 2)
        t_nhat = Fraction(n)
        t_var = Fraction(n * (n - 1), 2)
        # probabilities must sum to exactly 1 (a fifth independent check)
        total = sum(pmf.values(), Fraction(0))
        for got, want in (
            (e2, t_e2),
            (e_nhat, t_nhat),
            (e4, t_e4),
            (var_nhat, t_var),
            (total, Fraction(1)),
        ):
            checked += 1
            if got != want:
                mismatches += 1
    # a few witnessed exact values for the payload
    return {
        "n_range": f"0..{len(pmfs) - 1}",
        "checked": checked,
        "mismatches": mismatches,
        "E2_at_2": str(moment_2c(pmfs[2])),      # 3
        "E4_at_2": str(moment_4c(pmfs[2])),      # 10
        "Var_at_2": str(moment_4c(pmfs[2]) - moment_2c(pmfs[2]) ** 2),   # 1
        "Var_at_63": str(Fraction(63 * 62, 2)),  # 1953
        "pass": mismatches == 0,
        "z": "exact",
    }


# ---------------------------------------------------------------------------
# One iid Monte-Carlo batch of Morris replicas. Sufficient statistics are
# accumulated as EXACT integers so no float summation-order enters the payload.
# ---------------------------------------------------------------------------
def morris_batch(n_inc: int, replicas: int) -> dict:
    """Run `replicas` independent Morris runs of `n_inc` increments each.

    random.seed(SEED) is set HERE so the batch is order-independent. Returns
    exact-integer sufficient statistics for the true estimator est = 2^C - 1
    and for the raw counter C (reused by G4)."""
    random.seed(SEED)
    sum_est = 0            # sum of (2^C - 1)
    sum_est2 = 0           # sum of (2^C - 1)^2
    sum_c = 0              # sum of C
    sum_c2 = 0             # sum of C^2
    for _ in range(replicas):
        c = 0
        for _ in range(n_inc):
            if random.random() < 2.0 ** (-c):
                c += 1
        est = (1 << c) - 1          # 2^C - 1, exact int
        sum_est += est
        sum_est2 += est * est
        sum_c += c
        sum_c2 += c * c
    return {
        "n_inc": n_inc,
        "replicas": replicas,
        "sum_est": sum_est,
        "sum_est2": sum_est2,
        "sum_c": sum_c,
        "sum_c2": sum_c2,
    }


def mean_se_z(sum_x: int, sum_x2: int, m: int, target: float):
    """Sample mean, honest iid SE (sample_sd/sqrt(M)), and z from exact-int sums."""
    mean = sum_x / m
    # sample variance via the exact integer sums (Bessel-corrected)
    sample_var = (sum_x2 - Fraction(sum_x * sum_x, m)) / (m - 1)
    sample_var_f = float(sample_var)
    sd = math.sqrt(sample_var_f) if sample_var_f > 0 else 0.0
    se = sd / math.sqrt(m)
    z = (mean - target) / se if se > 0 else float("inf")
    return mean, sd, se, z, sample_var_f


# ---------------------------------------------------------------------------
# G2 — MC agreement (iid, |z| < 3). Produces the shared sample for G4.
# ---------------------------------------------------------------------------
def gate2_mc(batch: dict) -> dict:
    n = batch["n_inc"]
    m = batch["replicas"]
    mean, sd, se, z, sample_var = mean_se_z(batch["sum_est"], batch["sum_est2"], m, float(n))
    exact_var = float(Fraction(n * (n - 1), 2))
    var_ratio = sample_var / exact_var if exact_var > 0 else float("inf")
    return {
        "n_mc": n,
        "M": m,
        "mean": f"{mean:.6f}",
        "target": n,
        "sample_sd": f"{sd:.6f}",
        "se": f"{se:.6f}",
        "z": f"{z:.4f}",
        "sample_var": f"{sample_var:.4f}",
        "exact_var": f"{exact_var:.4f}",
        "var_ratio": f"{var_ratio:.4f}",
        "pass": abs(z) < Z_ACCEPT,
    }


# ---------------------------------------------------------------------------
# G3 — invariance: (a) exact martingale increment, (b) second-scale MC.
# ---------------------------------------------------------------------------
def gate3_invariance(pmfs: list[dict[int, Fraction]]) -> dict:
    # (a) EXACT martingale-increment invariance: E[2^{C_{n+1}}] - E[2^{C_n}] == 1.
    e2 = [moment_2c(p) for p in pmfs]
    violations = 0
    for n in range(len(e2) - 1):
        if e2[n + 1] - e2[n] != Fraction(1):
            violations += 1
    # (b) unbiasedness at a DIFFERENT scale (re-seeds inside morris_batch).
    batch2 = morris_batch(N_MC2, M_REPL2)
    n2 = batch2["n_inc"]
    m2 = batch2["replicas"]
    mean2, sd2, se2, z2, _ = mean_se_z(batch2["sum_est"], batch2["sum_est2"], m2, float(n2))
    return {
        "martingale_increment_range": f"0..{len(e2) - 2}",
        "martingale_violations": violations,
        "n_mc2": n2,
        "M2": m2,
        "mean2": f"{mean2:.6f}",
        "se2": f"{se2:.6f}",
        "z2": f"{z2:.4f}",
        "pass": violations == 0 and abs(z2) < Z_ACCEPT,
    }


# ---------------------------------------------------------------------------
# G4 — falsifiability (SAME sample as G2).
# ---------------------------------------------------------------------------
def gate4_falsifiability(batch: dict) -> dict:
    n = batch["n_inc"]
    m = batch["replicas"]
    # true estimator on the shared sample
    mean_true, sd, se, z_true, _ = mean_se_z(batch["sum_est"], batch["sum_est2"], m, float(n))

    # Primary foil: forgot the -1 correction, est_foil = 2^C = est + 1.
    # sum over replicas of (2^C) = sum_est + m ; its mean = mean_true + 1 exactly.
    sum_foil = batch["sum_est"] + m
    sum_foil2 = batch["sum_est2"] + 2 * batch["sum_est"] + m   # sum (est+1)^2
    mean_foil, _, se_foil, z_foil_primary, _ = mean_se_z(sum_foil, sum_foil2, m, float(n))

    # Secondary foil: raw counter est = C  (E ~ log2(n)).
    mean_c, _, se_c, z_c, _ = mean_se_z(batch["sum_c"], batch["sum_c2"], m, float(n))

    return {
        "primary_foil": "forgot the -1 correction: est = 2^C (E = n+1)",
        "mean_foil": f"{mean_foil:.6f}",
        "z_foil_primary": f"{z_foil_primary:.4f}",
        "secondary_foil": "raw counter: est = C (E ~ log2(n))",
        "mean_raw_counter": f"{mean_c:.6f}",
        "z_secondary_foil": f"{z_c:.4f}",
        "z_true_same_sample": f"{z_true:.4f}",
        "primary_rejected": abs(z_foil_primary) > Z_REJECT,
        "secondary_rejected": abs(z_c) > Z_REJECT,
        "true_accepted_same_sample": abs(z_true) < Z_ACCEPT,
        "pass": (abs(z_foil_primary) > Z_REJECT
                 and abs(z_c) > Z_REJECT
                 and abs(z_true) < Z_ACCEPT),
    }


# ---------------------------------------------------------------------------
# Assemble the whole payload.
# ---------------------------------------------------------------------------
def build_results() -> dict:
    pmfs = exact_pmf_sequence(N_EXACT)

    g1 = gate1_exact(pmfs)
    batch1 = morris_batch(N_MC1, M_REPL)     # shared G2/G4 sample (re-seeds inside)
    g2 = gate2_mc(batch1)
    g3 = gate3_invariance(pmfs)              # (b) re-seeds inside morris_batch
    g4 = gate4_falsifiability(batch1)

    all_pass = bool(g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"])
    first_failing = None
    for name, g in (("G1", g1), ("G2", g2), ("G3", g3), ("G4", g4)):
        if not g["pass"]:
            first_failing = name
            break
    return {
        "claim": "Morris approximate counting: E[2^{C_n}] = n+1 so E[N_hat=2^C-1] = n; "
                 "E[4^{C_n}] = 1 + 3n(n+1)/2 so Var[N_hat] = n(n-1)/2",
        "seed": SEED,
        "constants": {
            "N_EXACT": N_EXACT,
            "N_MC1": N_MC1,
            "M_REPL": M_REPL,
            "N_MC2": N_MC2,
            "M_REPL2": M_REPL2,
            "Z_ACCEPT": f"{Z_ACCEPT:.1f}",
            "Z_REJECT": f"{Z_REJECT:.1f}",
        },
        "G1_exact_unbiased_variance": g1,
        "G2_mc_agreement": g2,
        "G3_invariance": g3,
        "G4_falsifiability": g4,
        "all_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "PASS" if all_pass else "FAIL",
    }


def canonical_json(results: dict) -> str:
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def digest(results: dict) -> str:
    return hashlib.sha256(canonical_json(results).encode("utf-8")).hexdigest()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Morris approximate counting verifier")
    parser.add_argument("--selfcheck", action="store_true",
                        help="print byte-identity of an in-process double build + digest")
    args = parser.parse_args(argv[1:])

    a = build_results()
    b = build_results()
    ja, jb = canonical_json(a), canonical_json(b)
    if ja != jb:
        print("ERROR: in-process double-run is NOT byte-identical", file=sys.stderr)
        return 1
    dig = digest(a)

    if args.selfcheck:
        print("SELFCHECK: byte-identical" if ja == jb else "SELFCHECK: MISMATCH")
        print(f"results_sha256 = {dig}")
        return 0

    print(json.dumps(a, sort_keys=True, indent=2))
    print()
    print("in_process_double_run: IDENTICAL")
    print(f"G1_z = {a['G1_exact_unbiased_variance']['z']} "
          f"(checked={a['G1_exact_unbiased_variance']['checked']}, "
          f"mismatches={a['G1_exact_unbiased_variance']['mismatches']})")
    print(f"G2_z = {a['G2_mc_agreement']['z']}  (mean={a['G2_mc_agreement']['mean']})")
    print(f"G3_z2 = {a['G3_invariance']['z2']} "
          f"(martingale_violations={a['G3_invariance']['martingale_violations']})")
    print(f"G4_z_foil_primary = {a['G4_falsifiability']['z_foil_primary']}  "
          f"(z_secondary_foil = {a['G4_falsifiability']['z_secondary_foil']}, "
          f"z_true_same_sample = {a['G4_falsifiability']['z_true_same_sample']})")
    print(f"all_pass = {a['all_pass']}  decision = {a['decision']}")
    print(f"results_sha256 = {dig}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
