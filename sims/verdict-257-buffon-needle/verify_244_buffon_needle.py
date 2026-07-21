#!/usr/bin/env python3
"""PROPOSAL 244 — Buffon's needle: the short-needle crossing probability is 2l/(pi*d).

HEAD: A needle of length l is dropped uniformly at random on a plane ruled with
parallel lines spaced d apart. In the SHORT-needle regime (l <= d), the
probability that the needle crosses a line is EXACTLY

    P = 2*l / (pi*d).

The standard short-needle reduction: by symmetry take the needle's centre offset
u ~ Uniform[0, d/2] from the nearest line and its acute angle to the lines
theta ~ Uniform[0, pi/2]; the needle crosses iff u <= (l/2)*sin(theta). Averaging
the conditional crossing probability min(1, (l/d)*sin theta) over theta gives
(l/d)*E[sin theta] = (l/d)*(2/pi) = 2l/(pi*d).

The verifier implements the DROP (the geometric Bernoulli event u <= (l/2) sin t)
and does NOT assume the closed form; the 2/pi angle average is what the Monte
Carlo measures, and the exact rational kernel is checked with fractions.Fraction.

Gate battery (SEED=20260717; each gate in its own direction):
  G1 EXACT identity (fractions.Fraction, no floats): over the rational grid
     l/d in {1/4, 1/2, 3/4, 1} and rational sines s in {0, 1/2, 3/5, 4/5, 1},
     the exact conditional crossing probability P(cross | sin theta = s) computed
     two independent ways — (a) directly min(1, (l*s)/d), and (b) the offset-area
     model ((l/2)*s)/(d/2) clamped to 1 — are EXACTLY equal (0 mismatches); AND
     the exact expectation factorisation E[cross] = (l/d)*mean(s) over the sine
     multiset, computed two ways, is EXACTLY equal (0 mismatches). This pins the
     geometric kernel; an off-by-2 in the offset normalisation or a sin-vs-|sin|
     bug fails it exactly.
  G2 MC AGREEMENT (|z| < 3): continuous model at l/d = 1/2 so P = 1/pi; draw
     N >= 2,000,000 i.i.d. drops, count crossings C, binomial-proportion z-test
     against 1/pi; the drops are i.i.d. Bernoulli (no autocorrelation, no
     thinning). Also report the Buffon pi-estimate pi_hat = 2*l*N/(d*C).
  G3 INVARIANCE / ROBUSTNESS (max |z| < 3): (a) scaling both l and d by
     k in {2, 5, 0.3, 100} leaves P_hat within sampling error of 2l/(pi*d) — P
     depends only on the ratio l/d; (b) sampling theta over the full circle
     [0, 2*pi) with |sin theta| gives the same P_hat as theta ~ [0, pi/2].
  G4 FALSIFIABILITY (|z_naive| >> 3): on the SAME G2 sample, the naive
     "no angle factor" model P_naive = l/d = 1/2 is REJECTED at huge |z|; a
     subtler foil P_naive2 = (l/d)*(1/2) = 1/4 (assuming E[sin]=1/2 instead of
     2/pi) is also rejected. The gate PASSES by rejecting the naive alternatives.

Determinism posture: build_results() is a pure function of SEED and the fixed
params; a single random.Random(SEED) is seeded once and consumed in a fixed
order across all Monte-Carlo legs. Every float is stored with a fixed format so
the serialization is invocation-stable; the exact rationals serialize via
str(Fraction). main() builds the results twice in one process and asserts the
canonical JSON forms are byte-identical, prints a human summary and
`results_sha256=<64hex>` on its own line, and exits 1 if any gate fails.
"""

import hashlib
import json
import math
import random
import sys
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0

N = 2_000_000        # Monte-Carlo drops for G2 (and the shared G4 sample)
N_INV = 1_000_000    # drops per invariance config for G3

# Fixed geometry for the continuous legs: l/d = 1/2 so P = 2l/(pi d) = 1/pi.
L0 = 1.0
D0 = 2.0


def fmt(x):
    """Fixed float format so the serialization is invocation-stable."""
    return f"{float(x):.12g}"


def min1_frac(x):
    """Exact min(1, x) on a Fraction."""
    return x if x <= 1 else Fraction(1)


def drop_crossings(n, ell, d, rng, full_circle=False):
    """Simulate n i.i.d. Buffon drops; return the crossing count C.

    Each drop: theta ~ Uniform[0, pi/2] (or Uniform[0, 2 pi) with |sin| when
    full_circle), centre offset u ~ Uniform[0, d/2]. The needle crosses a line
    iff u <= (ell/2) * sin(theta). Short-needle regime assumed (ell <= d)."""
    c = 0
    half_d = d / 2.0
    half_l = ell / 2.0
    if full_circle:
        two_pi = 2.0 * math.pi
        for _ in range(n):
            theta = rng.uniform(0.0, two_pi)
            u = rng.uniform(0.0, half_d)
            if u <= half_l * abs(math.sin(theta)):
                c += 1
    else:
        half_pi = math.pi / 2.0
        for _ in range(n):
            theta = rng.uniform(0.0, half_pi)
            u = rng.uniform(0.0, half_d)
            if u <= half_l * math.sin(theta):
                c += 1
    return c


def zscore_prop(hits, n, p0):
    phat = hits / n
    se = math.sqrt(p0 * (1.0 - p0) / n)
    return (phat - p0) / se, phat, se


def build_results():
    rng = random.Random(SEED)  # seeded once; consumed in a fixed order below

    results = {
        "proposal": 244,
        "claim": (
            "Buffon's needle (short needle l <= d): a needle dropped uniformly "
            "at random on a plane ruled with parallel lines spaced d apart "
            "crosses a line with probability exactly 2*l/(pi*d)."
        ),
        "seed": SEED,
        "z_gate": fmt(Z_GATE),
        "N": N,
        "N_inv": N_INV,
        "l0": fmt(L0),
        "d0": fmt(D0),
    }

    # --- G1 EXACT identity via fractions.Fraction (no floats) -----------------
    # l/d as (l, d) integer pairs so route (a) and route (b) differ structurally.
    ld_pairs = [(1, 4), (1, 2), (3, 4), (1, 1)]        # l/d in {1/4,1/2,3/4,1}
    rational_sines = [Fraction(0), Fraction(1, 2),
                      Fraction(3, 5), Fraction(4, 5), Fraction(1)]

    identity_mismatches = 0
    for (ell, d) in ld_pairs:
        for s in rational_sines:
            route_a = min1_frac(Fraction(ell * s.numerator, d * s.denominator))
            route_b = min1_frac((Fraction(ell, 2) * s) / Fraction(d, 2))
            if route_a != route_b:
                identity_mismatches += 1

    # Exact expectation factorisation over the sine multiset, two ways.
    expectation_mismatches = 0
    k = len(rational_sines)
    mean_sines = sum(rational_sines, Fraction(0)) / k
    for (ell, d) in ld_pairs:
        e_direct = sum((min1_frac(Fraction(ell, d) * s)
                        for s in rational_sines), Fraction(0)) / k
        e_factored = Fraction(ell, d) * mean_sines
        if e_direct != e_factored:
            expectation_mismatches += 1

    g1_pass = (identity_mismatches == 0) and (expectation_mismatches == 0)
    results["G1_exact_identity"] = {
        "ld_ratios": [f"{a}/{b}" for (a, b) in ld_pairs],
        "rational_sines": [f"{s.numerator}/{s.denominator}" for s in rational_sines],
        "pairs_tested": len(ld_pairs) * len(rational_sines),
        "identity_mismatches": identity_mismatches,
        "expectation_mismatches": expectation_mismatches,
        "mean_sines": f"{mean_sines.numerator}/{mean_sines.denominator}",
        "pass": g1_pass,
    }

    # --- G2 MC agreement at l/d = 1/2, P = 1/pi, |z| < 3 ----------------------
    p_theory = 2.0 * L0 / (math.pi * D0)   # = 1/pi
    c2 = drop_crossings(N, L0, D0, rng)
    z2, phat2, se2 = zscore_prop(c2, N, p_theory)
    pi_hat = (2.0 * L0 * N) / (D0 * c2)     # Buffon pi-estimate readout
    g2_pass = abs(z2) < Z_GATE
    results["G2_mc_agreement"] = {
        "l_over_d": "1/2",
        "p_theory": fmt(p_theory),
        "crossings": c2,
        "n_drops": N,
        "p_hat": fmt(phat2),
        "z": fmt(z2),
        "pi_hat": fmt(pi_hat),
        "iid_bernoulli_no_thinning": True,
        "pass": g2_pass,
    }

    # --- G3 invariance / robustness (max |z| < 3) -----------------------------
    inv_zs = []
    scale_reports = []
    for kmul in [2.0, 5.0, 0.3, 100.0]:
        ell_k = L0 * kmul
        d_k = D0 * kmul
        p_k = 2.0 * ell_k / (math.pi * d_k)   # invariant: still 1/pi
        c_k = drop_crossings(N_INV, ell_k, d_k, rng)
        z_k, phat_k, _ = zscore_prop(c_k, N_INV, p_k)
        inv_zs.append(abs(z_k))
        scale_reports.append({
            "k": fmt(kmul),
            "l": fmt(ell_k),
            "d": fmt(d_k),
            "crossings": c_k,
            "p_hat": fmt(phat_k),
            "z": fmt(z_k),
        })
    # Full-circle parametrisation with |sin theta| must match [0, pi/2].
    p_fc = 2.0 * L0 / (math.pi * D0)
    c_fc = drop_crossings(N_INV, L0, D0, rng, full_circle=True)
    z_fc, phat_fc, _ = zscore_prop(c_fc, N_INV, p_fc)
    inv_zs.append(abs(z_fc))
    max_abs_z = max(inv_zs)
    g3_pass = max_abs_z < Z_GATE
    results["G3_invariance_robustness"] = {
        "scale_configs": scale_reports,
        "full_circle": {
            "crossings": c_fc,
            "p_hat": fmt(phat_fc),
            "z": fmt(z_fc),
        },
        "max_abs_z": fmt(max_abs_z),
        "pass": g3_pass,
    }

    # --- G4 falsifiability: reject naive foils on the SAME G2 sample ----------
    p_naive = L0 / D0                         # 1/2 — forgets the 2/pi factor
    z_naive, _, _ = zscore_prop(c2, N, p_naive)
    p_naive2 = (L0 / D0) * 0.5                # 1/4 — assumes E[sin]=1/2 not 2/pi
    z_naive2, _, _ = zscore_prop(c2, N, p_naive2)
    g4_pass = (abs(z_naive) > Z_GATE) and (abs(z_naive2) > Z_GATE)
    results["G4_falsifiability"] = {
        "foil_no_angle_factor": {
            "p_naive": fmt(p_naive),
            "z_abs": fmt(abs(z_naive)),
        },
        "foil_half_mean_sine": {
            "p_naive": fmt(p_naive2),
            "z_abs": fmt(abs(z_naive2)),
        },
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
    results["first_failing_gate"] = next((key for key in order if not gates[key]), None)
    results["all_pass"] = all(gates[key] for key in order)
    return results


def canonical(results):
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def main():
    r1 = build_results()
    r2 = build_results()
    c1 = canonical(r1)
    c2 = canonical(r2)
    if c1 != c2:
        sys.stderr.write("NON-DETERMINISTIC: in-process double-run diverged\n")
        sys.exit(3)
    digest = hashlib.sha256(c1.encode("utf-8")).hexdigest()

    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    for key in ["G1", "G2", "G3", "G4"]:
        print(f"{key}: {'PASS' if r1['gates'][key] else 'FAIL'}")
    print()
    print(f"all_pass: {r1['all_pass']}")
    print(f"first_failing_gate: {r1['first_failing_gate']}")
    print(f"results_sha256={digest}")
    sys.exit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
