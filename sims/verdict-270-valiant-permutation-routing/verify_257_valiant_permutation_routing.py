#!/usr/bin/env python3
"""verify_257_valiant_permutation_routing.py -- firsthand verifier (stdlib only).

Claim (exact combinatorial backbone): Valiant's two-phase (random-intermediate)
oblivious routing on the hypercube Q_n (N = 2^n nodes). Each packet is first
routed from its source s to a UNIFORMLY RANDOM intermediate node d, then on to
its true destination, by left-to-right bit-fixing. The exact phase-1 backbone:

    Phase-1 route length L = Hamming distance H(s, d), d uniform on {0,1}^n.
    Because d is uniform and independent of s, the XOR s^d is uniform on
    {0,1}^n, so L = popcount(s^d) is EXACTLY Binomial(n, 1/2):

        p_k = C(n,k) / 2^n ,   E[L] = n/2 ,   Var[L] = n/4 ,

    INDEPENDENT of the source s (this source-invariance is exactly why the
    random intermediate defeats adversarial permutations).

    Probability generating function  G(x) = E[x^L] = ((1+x)/2)^n  exactly.

    Average congestion over the N*n directed edges of Q_n
        = E[total edge-crossings] / (N*n)
        = (N * (n/2)) / (N * n) = 1/2   exactly.

Four gates, each read in its OWN direction:

  G1 EXACT (fractions.Fraction, 0 mismatches) -- the exact-rational backbone:
     (a) PGF identity sum_k C(n,k) x^k = (1+x)^n, hence G(x) = ((1+x)/2)^n,
         checked at several rational x for several n; (b) E[L] = n/2 = G'(1);
         (c) Var[L] = n/4 from G''(1) + G'(1) - G'(1)^2; (d) the pmf sums to 1
         and is symmetric p_k = p_{n-k}; (e) average directed-edge congestion
         = (N*(n/2))/(N*n) = 1/2 exact. Zero tolerance. z = "exact".

  G2 MC AGREEMENT (|z| < 3) -- draw N_MC uniform 12-bit pairs (s, d), route
     length = popcount(s^d), an iid Binomial(12, 1/2) draw. Empirical mean vs
     E[L] = 6.0. Because the draws are iid, the plain iid standard error
     SE = sqrt(sample_var / N_MC) is the honest one -- no batch-means/thinning
     is needed (that machinery is only for autocorrelated sample paths). Report
     z = (mean - 6.0)/SE. Also report the derived edge-congestion estimate
     mean/n vs 1/2 (the same statistic rescaled).

  G3 ROBUSTNESS / INVARIANCE (own direction) -- (a) SOURCE-PERMUTATION
     INVARIANCE (Valiant's core): re-estimate the mean route length with the
     sources taken from an ADVERSARIAL permutation -- the bit-reversal
     permutation of the node index -- paired with uniform-random intermediates.
     The adversary CANNOT inflate phase-1 length because the intermediate is
     uniform and independent of the source, so the mean still agrees with n/2 at
     |z| < 3. (b) n-INVARIANCE: E[L]/n = 1/2 (edge congestion 1/2) across
     n in {8, 10, 12, 14}, each |z| < 3.

  G4 FALSIFIABILITY (own direction, SAME MC sample as G2) -- the plausible naive
     foils. Primary: "every packet crosses all n dimensions, so route length =
     n = 12 / edge congestion = 1" predicts mean 12.0; on the SAME sample that
     AGREES with the true mean 6.0 at |z| < 3 it is REJECTED at |z_foil| >> 50.
     Secondary: "route length = n/2 but each edge is traversed deterministically
     so congestion = 1.0 not 1/2" -- congestion = 1.0 rejected vs the measured
     ~0.5 at large |z|.

Determinism: results dict -> canonical JSON (sorted keys) -> sha256 (full 64
hex, never truncated). All Monte-Carlo-derived floats (means, z-values, SEs) are
rounded to 6 decimals and every exact rational is serialized as str(Fraction)
BEFORE entering the hashed payload, so the digest is cross-platform stable.
main() builds the results twice in-process and asserts byte equality; --selfcheck
runs it twice in-process and prints "SELFCHECK: byte-identical"; a separate
process re-invocation reproduces the digest byte-for-byte. random.seed(SEED) is
re-seeded at the START of each Monte-Carlo gate so gate order cannot perturb the
payload. Stdlib only: json, hashlib, math, random, fractions, sys.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from fractions import Fraction

# ---------------------------------------------------------------------------
# Constants (all payload-affecting knobs are module-level and hardcoded).
# ---------------------------------------------------------------------------
SEED = 20260717
N_DIM = 12                     # primary hypercube dimension n (N = 2^n = 4096)
N_MC = 400_000                 # Monte-Carlo phase-1 route-length draws (G2/G4)
N_INV = 8                      # bits for the smallest n-invariance instance
SWEEP_N = (8, 10, 12, 14)      # n-invariance sweep
PGF_NS = (1, 2, 3, 8, 12)      # n values for the exact PGF / moment checks
PGF_XS = (Fraction(1), Fraction(2), Fraction(1, 2),
          Fraction(3), Fraction(-1, 3))     # rational x for the PGF identity
Z_ACCEPT = 3.0
Z_REJECT = 50.0


def r6(x: float) -> float:
    """Round a Monte-Carlo-derived float to 6 decimals before it enters the
    hashed payload (cross-platform stable digest)."""
    return round(float(x), 6)


def popcount(x: int) -> int:
    return bin(x).count("1")


def bit_reverse(x: int, n: int) -> int:
    """Reverse the low n bits of x -- the bit-reversal permutation of the node
    index, a standard adversarial (non-uniform-looking) source ordering."""
    r = 0
    for _ in range(n):
        r = (r << 1) | (x & 1)
        x >>= 1
    return r


# ---------------------------------------------------------------------------
# G1 -- EXACT rational backbone (fractions.Fraction, zero tolerance).
# ---------------------------------------------------------------------------
def pmf(n: int) -> list[Fraction]:
    """Exact Binomial(n, 1/2) pmf p_k = C(n,k)/2^n."""
    denom = Fraction(1, 2 ** n)
    return [Fraction(math.comb(n, k)) * denom for k in range(n + 1)]


def gate1_exact() -> dict:
    checked = 0
    mismatches = 0

    # (a) PGF identity sum_k C(n,k) x^k = (1+x)^n, hence G(x) = ((1+x)/2)^n.
    for n in PGF_NS:
        for x in PGF_XS:
            checked += 1
            lhs = sum(Fraction(math.comb(n, k)) * x ** k for k in range(n + 1))
            if lhs != (1 + x) ** n:
                mismatches += 1
            # G(x) = sum_k p_k x^k must equal ((1+x)/2)^n exactly.
            checked += 1
            p = pmf(n)
            gx = sum(p[k] * x ** k for k in range(n + 1))
            if gx != ((1 + x) / 2) ** n:
                mismatches += 1

    # (b) E[L] = n/2 = G'(1); (c) Var[L] = n/4 = G''(1)+G'(1)-G'(1)^2;
    # (d) pmf sums to 1 and is symmetric p_k = p_{n-k}.
    for n in PGF_NS:
        p = pmf(n)
        # (d) normalization
        checked += 1
        if sum(p) != 1:
            mismatches += 1
        # (d) symmetry
        checked += 1
        if any(p[k] != p[n - k] for k in range(n + 1)):
            mismatches += 1
        # (b) mean via the pmf and via G'(1) both equal n/2
        mean = sum(Fraction(k) * p[k] for k in range(n + 1))
        gp1 = Fraction(n, 2)                      # G'(1) = n * 1^(n-1) * 1/2
        checked += 1
        if mean != Fraction(n, 2) or mean != gp1:
            mismatches += 1
        # (c) variance via the pmf and via G''(1)+G'(1)-G'(1)^2 both equal n/4
        e2 = sum(Fraction(k * k) * p[k] for k in range(n + 1))
        var = e2 - mean * mean
        gpp1 = Fraction(n * (n - 1), 4)           # G''(1) = n(n-1)/4
        var_pgf = gpp1 + gp1 - gp1 * gp1
        checked += 1
        if var != Fraction(n, 4) or var_pgf != Fraction(n, 4):
            mismatches += 1

    # (e) average directed-edge congestion = (N*(n/2))/(N*n) = 1/2 exactly.
    for n in PGF_NS:
        N = 2 ** n
        checked += 1
        total_crossings = Fraction(N) * Fraction(n, 2)       # E[sum of L]
        directed_edges = Fraction(N * n)                     # n out-edges/node
        if total_crossings / directed_edges != Fraction(1, 2):
            mismatches += 1

    p12 = pmf(N_DIM)
    return {
        "checked": checked,
        "mismatches": mismatches,
        "n_primary": N_DIM,
        "E_L": str(sum(Fraction(k) * p12[k] for k in range(N_DIM + 1))),  # 6
        "Var_L": str(Fraction(N_DIM, 4)),                                 # 3
        "avg_congestion": str(Fraction(1, 2)),                            # 1/2
        "G_of_x": "((1+x)/2)^n",
        "pass": mismatches == 0,
        "z": "exact",
    }


# ---------------------------------------------------------------------------
# Monte-Carlo phase-1 route-length sampler.
# ---------------------------------------------------------------------------
def sample_route_lengths(rng: random.Random, n: int, draws: int):
    """Draw `draws` uniform pairs (s, d) in {0,1}^n and return
    (mean, sample_var) of the phase-1 route length L = popcount(s^d)."""
    mask = (1 << n) - 1
    s_ = 0.0
    s2 = 0.0
    for _ in range(draws):
        s = rng.getrandbits(n) & mask
        d = rng.getrandbits(n) & mask
        L = popcount(s ^ d)
        s_ += L
        s2 += L * L
    mean = s_ / draws
    sample_var = (s2 - draws * mean * mean) / (draws - 1)
    return mean, sample_var


def sample_adversarial(rng: random.Random, n: int, draws: int):
    """Sources from the bit-reversal permutation of a deterministic index sweep
    (an adversarial, non-uniform source ordering); intermediates uniform. Returns
    (mean, sample_var) of L = popcount(bitrev(i) ^ d)."""
    mask = (1 << n) - 1
    N = 1 << n
    s_ = 0.0
    s2 = 0.0
    for i in range(draws):
        s = bit_reverse(i % N, n)
        d = rng.getrandbits(n) & mask
        L = popcount(s ^ d)
        s_ += L
        s2 += L * L
    mean = s_ / draws
    sample_var = (s2 - draws * mean * mean) / (draws - 1)
    return mean, sample_var


# ---------------------------------------------------------------------------
# G2 (agreement) + G4 (falsifiability) share ONE sample.
# ---------------------------------------------------------------------------
def gate2_and_gate4() -> tuple[dict, dict]:
    random.seed(SEED)
    rng = random.Random(SEED)
    n = N_DIM
    mean, sample_var = sample_route_lengths(rng, n, N_MC)
    se = math.sqrt(sample_var / N_MC)
    true_mean = n / 2.0                       # E[L] = n/2 = 6.0
    z_true = (mean - true_mean) / se

    cong = mean / n                           # derived edge-congestion estimate
    se_cong = se / n
    z_cong = (cong - 0.5) / se_cong

    # Primary foil: "route length = n (all dimensions crossed)" -> mean = 12.0.
    foil_mean = float(n)
    z_foil = (mean - foil_mean) / se
    # Secondary foil: "congestion = 1.0 not 1/2".
    z_cong_foil = (cong - 1.0) / se_cong

    g2 = {
        "n": n,
        "N_nodes": 2 ** n,
        "N_mc": N_MC,
        "mean_len": r6(mean),
        "true_mean_E_L": r6(true_mean),
        "se": r6(se),
        "z": r6(z_true),
        "congestion_est": r6(cong),
        "congestion_true": 0.5,
        "z_congestion": r6(z_cong),
        "pass": abs(z_true) < Z_ACCEPT and abs(z_cong) < Z_ACCEPT,
    }
    g4 = {
        "primary_foil": "every packet crosses all n dimensions -> route length = n = 12",
        "primary_foil_mean": r6(foil_mean),
        "z_foil": r6(z_foil),
        "z_true_same_sample": r6(z_true),
        "secondary_foil": "each edge traversed deterministically -> congestion = 1.0 not 1/2",
        "secondary_foil_congestion": 1.0,
        "z_congestion_foil": r6(z_cong_foil),
        "congestion_true_same_sample": r6(cong),
        "primary_rejected": abs(z_foil) > Z_REJECT,
        "secondary_rejected": abs(z_cong_foil) > Z_REJECT,
        "true_accepted_same_sample": abs(z_true) < Z_ACCEPT,
        "pass": (abs(z_foil) > Z_REJECT
                 and abs(z_cong_foil) > Z_REJECT
                 and abs(z_true) < Z_ACCEPT),
    }
    return g2, g4


# ---------------------------------------------------------------------------
# G3 -- robustness (source-permutation invariance) + n-invariance.
# ---------------------------------------------------------------------------
def gate3_robustness() -> dict:
    n = N_DIM
    # (a) SOURCE-PERMUTATION INVARIANCE: adversarial (bit-reversal) sources,
    #     uniform intermediates -> mean still n/2.
    random.seed(SEED)
    rng = random.Random(SEED)
    adv_mean, adv_var = sample_adversarial(rng, n, N_MC)
    adv_se = math.sqrt(adv_var / N_MC)
    z_adv = (adv_mean - n / 2.0) / adv_se

    # (b) n-INVARIANCE: E[L]/n = 1/2 across the sweep.
    random.seed(SEED)
    rng = random.Random(SEED)
    sweep = []
    all_inv_pass = True
    for m in SWEEP_N:
        mean, var = sample_route_lengths(rng, m, N_MC)
        se = math.sqrt(var / N_MC)
        z = (mean - m / 2.0) / se
        cong = mean / m
        ok = abs(z) < Z_ACCEPT
        all_inv_pass = all_inv_pass and ok
        sweep.append({
            "n": m,
            "mean_len": r6(mean),
            "E_L": r6(m / 2.0),
            "ratio_mean_over_n": r6(cong),
            "z": r6(z),
            "pass": ok,
        })

    return {
        "adversarial_source_permutation": "bit-reversal of node index",
        "adv_mean_len": r6(adv_mean),
        "adv_true_mean_E_L": r6(n / 2.0),
        "adv_se": r6(adv_se),
        "adv_z": r6(z_adv),
        "adv_pass": abs(z_adv) < Z_ACCEPT,
        "n_invariance_sweep": sweep,
        "n_invariance_pass": all_inv_pass,
        "z": r6(z_adv),
        "pass": abs(z_adv) < Z_ACCEPT and all_inv_pass,
    }


# ---------------------------------------------------------------------------
# Assemble the whole payload.
# ---------------------------------------------------------------------------
def build_results() -> dict:
    g1 = gate1_exact()
    g2, g4 = gate2_and_gate4()
    g3 = gate3_robustness()
    all_pass = bool(g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"])
    first_failing = None
    for name, g in (("G1", g1), ("G2", g2), ("G3", g3), ("G4", g4)):
        if not g["pass"]:
            first_failing = name
            break
    return {
        "claim": "Valiant two-phase routing on Q_n: phase-1 route length "
                 "L = popcount(s^d) ~ Binomial(n,1/2); E[L]=n/2, Var[L]=n/4, "
                 "source-invariant; G(x)=((1+x)/2)^n; avg edge congestion = 1/2",
        "seed": SEED,
        "constants": {
            "N_DIM": N_DIM,
            "N_MC": N_MC,
            "SWEEP_N": list(SWEEP_N),
            "PGF_NS": list(PGF_NS),
            "Z_ACCEPT": f"{Z_ACCEPT:.1f}",
            "Z_REJECT": f"{Z_REJECT:.1f}",
        },
        "G1_exact_backbone": g1,
        "G2_mc_agreement": g2,
        "G3_robustness_invariance": g3,
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
    selfcheck = "--selfcheck" in argv[1:]

    a = build_results()
    b = build_results()
    ja, jb = canonical_json(a), canonical_json(b)
    if ja != jb:
        print("ERROR: in-process double-run is NOT byte-identical", file=sys.stderr)
        return 1
    dig = digest(a)

    if selfcheck:
        print("SELFCHECK: byte-identical" if ja == jb else "SELFCHECK: MISMATCH")
        print(f"results_sha256 = {dig}")
        return 0

    print(json.dumps(a, sort_keys=True, indent=2))
    print()
    print("in_process_double_run: IDENTICAL")
    print(f"G1_z = {a['G1_exact_backbone']['z']} "
          f"(checked={a['G1_exact_backbone']['checked']}, "
          f"mismatches={a['G1_exact_backbone']['mismatches']})")
    print(f"G2_z = {a['G2_mc_agreement']['z']}  "
          f"(congestion_est={a['G2_mc_agreement']['congestion_est']}, "
          f"z_congestion={a['G2_mc_agreement']['z_congestion']})")
    print(f"G3_adv_z = {a['G3_robustness_invariance']['adv_z']}  "
          f"(n_invariance_pass={a['G3_robustness_invariance']['n_invariance_pass']})")
    print(f"G4_z_foil = {a['G4_falsifiability']['z_foil']}  "
          f"z_congestion_foil = {a['G4_falsifiability']['z_congestion_foil']}  "
          f"(z_true_same_sample = {a['G4_falsifiability']['z_true_same_sample']})")
    print(f"all_pass = {a['all_pass']}  decision = {a['decision']}")
    print(f"results_sha256 = {dig}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
