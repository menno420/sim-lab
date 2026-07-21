#!/usr/bin/env python3
"""verify_253_bft_committee_sortition.py — firsthand verifier (stdlib only).

Claim (coordination / consensus over a fleet of agents): committee-sortition
safety in a Byzantine fleet. A fleet of N=64 agents contains B=21 Byzantine
agents. Note 64 = 3*21 + 1, so the FULL system sits EXACTLY at the classical
BFT safety bound n >= 3f+1 with f = 21 (it tolerates 21 Byzantine agents). A
committee of K=16 agents is drawn UNIFORMLY WITHOUT REPLACEMENT (sortition). A
committee is UNSAFE iff it contains >= T = floor(K/3)+1 = 6 Byzantine members
(a K-node BFT quorum tolerates floor((K-1)/3) = 5 Byzantine members, so 6 breaks
it). The number of Byzantine members in a sortition committee is therefore
Hypergeometric(N, B, K), and the committee-failure probability is the EXACT
hypergeometric UPPER TAIL

    P = sum_{i=T}^{K} C(B,i)*C(N-B, K-i) / C(N,K),   N=64, B=21, N-B=43, K=16, T=6.

The insight: a GLOBALLY-safe fleet still produces UNSAFE sub-committees a large
fraction of the time. The expected Byzantine count per committee is
K*B/N = 16*21/64 = 5.25, just below the threshold of 6, because sortition
CONCENTRATES Byzantine nodes into some committees — which is exactly why
committee-BFT protocols must SIZE committees to bound the sortition failure
probability.

Four gates, each read in its OWN direction:

  G1 EXACT (fractions.Fraction, no float in the identity) — the hypergeometric
     upper tail computed exactly, cross-checked two independent ways:
       (A) the full pmf sums to 1 exactly (Vandermonde's identity
           sum_{i} C(B,i) C(N-B,K-i) = C(N,K)); residual == 0.
       (B) the tail equals 1 minus the exact lower partial sum:
           P == 1 - sum_{i=0}^{T-1} pmf_i; 0 mismatch.
     P recorded as an exact "num/den" string and its float.

  G2 MC AGREEMENT (|z| < 3, iid — NO thinning) — each committee is a FRESH
     independent random.sample of K distinct agents, so the per-committee UNSAFE
     indicators are iid Bernoulli(P). (Contrast: a queue-occupancy sample path is
     autocorrelated and would need batch means; independent committee draws do
     NOT — the plain iid binomial standard error is the honest one.) Draw MC_N
     committees, p_hat = (#unsafe)/MC_N, z = (p_hat - P)/sqrt(P(1-P)/MC_N).

  G3 INVARIANCE (Byzantine-identity invariance, own direction) — the exact value
     depends only on the COUNTS (N,B,K,T), not on WHICH agents are Byzantine.
     Structurally this is true by construction (P is a function of counts only).
     Demonstrated EMPIRICALLY too: a SECOND MC block uses a DIFFERENT Byzantine
     set of the same size B (byz2 = {(i*3) % N : i in range(B)}, distinct because
     gcd(3,64)=1) -> p_hat2, z2 against the SAME exact P. PASS iff |z2| < 3.

  G4 FALSIFIABILITY (reject the naive WITH-replacement binomial, own direction,
     SAME true without-replacement sample as G2) — the naive foil models the
     committee as K iid draws with replacement at rate p = B/N:
       P_binom = sum_{i=T}^{K} C(K,i) p^i (1-p)^{K-i}.
     This IGNORES the finite-population NEGATIVE correlation of without-replacement
     sampling, so it OVERSTATES the tail. On the SAME true (without-replacement)
     MC sample, z_foil = (p_hat - P_binom)/sqrt(P_binom(1-P_binom)/MC_N) must be
     |z_foil| >> 3 (REJECTED) while the hypergeometric P is ACCEPTED at |z| < 3.

Determinism: results dict -> canonical JSON (json.dumps, sort_keys=True) ->
sha256 (full 64 hex, never truncated). `main()` builds the results twice
in-process and asserts byte equality; `--selfcheck` prints "SELFCHECK:
byte-identical"; a separate process re-invocation reproduces the digest
byte-for-byte. SEED = 20260717 (hardcoded module constant). Stdlib only:
math, random, fractions, hashlib, json, argparse, sys.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from fractions import Fraction
from math import comb

# ---------------------------------------------------------------------------
# Constants (all payload-affecting knobs are module-level and hardcoded).
# ---------------------------------------------------------------------------
SEED = 20260717
N = 64                  # fleet size
B = 21                  # Byzantine agents
K = 16                  # committee size (sortition draw, without replacement)
T = K // 3 + 1          # unsafe threshold = floor(K/3)+1 = 6
MC_N = 400_000          # independent committee draws (G2/G3/G4)
Z_ACCEPT = 3.0

# Structural BFT check: the full fleet sits EXACTLY at the classical bound n>=3f+1.
assert N == 3 * B + 1, "fleet must sit exactly at the BFT bound N = 3B+1"
assert T == 6, "threshold T must be floor(K/3)+1 = 6"


# ---------------------------------------------------------------------------
# G1 — EXACT hypergeometric upper tail (fractions.Fraction, no float).
# ---------------------------------------------------------------------------
def pmf_exact(i: int) -> Fraction:
    """Exact hypergeometric pmf P(X=i) = C(B,i) C(N-B,K-i) / C(N,K)."""
    return Fraction(comb(B, i) * comb(N - B, K - i), comb(N, K))


def gate1_exact() -> dict:
    # Exact upper tail P = sum_{i=T}^{K} pmf_i.
    p_exact = sum((pmf_exact(i) for i in range(T, K + 1)), Fraction(0))

    # Cross-check A: full pmf sums to 1 exactly (Vandermonde).
    full = sum((pmf_exact(i) for i in range(0, K + 1)), Fraction(0))
    residual_A = full - Fraction(1)

    # Cross-check B: tail two ways — P == 1 - lower partial sum.
    lower = sum((pmf_exact(i) for i in range(0, T)), Fraction(0))
    p_via_complement = Fraction(1) - lower
    mismatch_B = 0 if p_exact == p_via_complement else 1

    return {
        "P_num_den": f"{p_exact.numerator}/{p_exact.denominator}",
        "P_float": f"{float(p_exact):.6f}",
        "vandermonde_residual": str(residual_A),     # exact "0"
        "tail_complement_mismatch": mismatch_B,       # 0
        "pass": residual_A == 0 and mismatch_B == 0,
        "z": "exact",
        "_p_exact": p_exact,  # popped before hashing; float taken from P_float
    }


# ---------------------------------------------------------------------------
# Monte-Carlo committee sortition (independent draws => iid Bernoulli).
# ---------------------------------------------------------------------------
def mc_unsafe_fraction(rng: random.Random, byz: set, n_trials: int) -> float:
    """Fraction of n_trials independent sortition committees that are UNSAFE
    (contain >= T Byzantine members). Each committee is a fresh random.sample of
    K distinct agents, so the UNSAFE indicators are iid Bernoulli."""
    pool = range(N)
    unsafe = 0
    for _ in range(n_trials):
        committee = rng.sample(pool, K)
        if sum(1 for a in committee if a in byz) >= T:
            unsafe += 1
    return unsafe / n_trials


def z_binom(p_hat: float, p0: float, n_trials: int) -> float:
    return (p_hat - p0) / math.sqrt(p0 * (1.0 - p0) / n_trials)


# ---------------------------------------------------------------------------
# G2 (MC agreement) + G4 (falsifiability) share ONE without-replacement sample.
# ---------------------------------------------------------------------------
def gate2_and_gate4(p0: float) -> tuple[dict, dict]:
    rng = random.Random(SEED)
    byz = set(range(B))                       # canonical Byzantine set {0..B-1}
    p_hat = mc_unsafe_fraction(rng, byz, MC_N)
    z = z_binom(p_hat, p0, MC_N)

    # Naive WITH-replacement binomial foil at rate p = B/N.
    p = B / N
    p_binom = sum(comb(K, i) * p ** i * (1.0 - p) ** (K - i) for i in range(T, K + 1))
    z_foil = z_binom(p_hat, p_binom, MC_N)

    g2 = {
        "MC_N": MC_N,
        "p_hat": f"{p_hat:.6f}",
        "P_float": f"{p0:.6f}",
        "z": f"{z:.4f}",
        "pass": abs(z) < Z_ACCEPT,
    }
    g4 = {
        "foil": "with-replacement Binomial(K, B/N) — ignores finite-population "
                "negative correlation, overstates the tail",
        "p_binom": f"{p_binom:.6f}",
        "z_foil": f"{z_foil:.4f}",
        "z_true_same_sample": f"{z:.4f}",
        "binom_differs_from_exact": abs(p_binom - p0) > 1e-9,
        "rejected": abs(z_foil) > Z_ACCEPT,
        "true_accepted_same_sample": abs(z) < Z_ACCEPT,
        "pass": abs(z_foil) > Z_ACCEPT and abs(z) < Z_ACCEPT
        and abs(p_binom - p0) > 1e-9,
    }
    return g2, g4


# ---------------------------------------------------------------------------
# G3 — Byzantine-identity invariance (different Byzantine set, same counts).
# ---------------------------------------------------------------------------
def gate3_invariance(p0: float) -> dict:
    # A DIFFERENT Byzantine set of the same size B, spread across the fleet.
    byz2 = {(i * 3) % N for i in range(B)}     # distinct: gcd(3,64)=1
    assert len(byz2) == B, "byz2 must have exactly B distinct members"
    rng = random.Random(SEED)
    p_hat2 = mc_unsafe_fraction(rng, byz2, MC_N)
    z2 = z_binom(p_hat2, p0, MC_N)
    return {
        "byz2_size": len(byz2),
        "byz2_differs_from_canonical": byz2 != set(range(B)),
        "structural_counts_only": True,   # P is a function of (N,B,K,T) only
        "p_hat2": f"{p_hat2:.6f}",
        "P_float": f"{p0:.6f}",
        "z2": f"{z2:.4f}",
        "pass": abs(z2) < Z_ACCEPT,
    }


# ---------------------------------------------------------------------------
# Assemble the whole payload.
# ---------------------------------------------------------------------------
def build_results() -> dict:
    g1 = gate1_exact()
    p_exact = g1.pop("_p_exact")          # keep exact Fraction out of the payload
    p0 = float(p_exact)                    # single source of the MC target float
    g2, g4 = gate2_and_gate4(p0)
    g3 = gate3_invariance(p0)

    all_pass = bool(g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"])
    first_failing = None
    for name, g in (("G1", g1), ("G2", g2), ("G3", g3), ("G4", g4)):
        if not g["pass"]:
            first_failing = name
            break

    return {
        "claim": "committee sortition safety in a Byzantine fleet: "
                 "P(>=T Byzantine in a size-K sortition committee) = "
                 "hypergeometric upper tail, N=64,B=21,K=16,T=6, N=3B+1 (BFT bound)",
        "seed": SEED,
        "constants": {
            "N": N,
            "B": B,
            "K": K,
            "T": T,
            "MC_N": MC_N,
            "Z_ACCEPT": f"{Z_ACCEPT:.1f}",
            "N_eq_3B_plus_1": N == 3 * B + 1,
            "expected_byz_per_committee": f"{K * B / N:.6f}",  # 5.25
        },
        "G1_exact_hypergeometric_tail": g1,
        "G2_mc_agreement": g2,
        "G3_byzantine_identity_invariance": g3,
        "G4_falsifiability_binomial_foil": g4,
        "all_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "PASS" if all_pass else "FAIL",
    }


def canonical_json(results: dict) -> str:
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def digest(results: dict) -> str:
    return hashlib.sha256(canonical_json(results).encode("utf-8")).hexdigest()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selfcheck", action="store_true",
                        help="run compute twice in-process, assert byte-identical")
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
    print(f"in_process_double_run: {'IDENTICAL' if ja == jb else 'MISMATCH'}")
    print(f"P_exact = {a['G1_exact_hypergeometric_tail']['P_num_den']} "
          f"= {a['G1_exact_hypergeometric_tail']['P_float']}")
    print(f"G2_z = {a['G2_mc_agreement']['z']}")
    print(f"G3_z2 = {a['G3_byzantine_identity_invariance']['z2']}")
    print(f"G4_z_foil = {a['G4_falsifiability_binomial_foil']['z_foil']}  "
          f"(P_binom = {a['G4_falsifiability_binomial_foil']['p_binom']}; "
          f"z_true_same_sample = "
          f"{a['G4_falsifiability_binomial_foil']['z_true_same_sample']})")
    print(f"all_pass = {a['all_pass']}  decision = {a['decision']}")
    print(f"results_sha256 = {dig}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
