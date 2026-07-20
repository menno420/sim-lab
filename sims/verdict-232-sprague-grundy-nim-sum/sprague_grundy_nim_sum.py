#!/usr/bin/env python3
"""PROPOSAL 219 / VERDICT 232 (+13 offset) — round-52 GAME slot.

HEAD: In impartial combinatorial games, a disjunctive-sum position is a loss
for the player to move (a P-position) if and only if the XOR ("nim-sum") of its
component Grundy values is zero (Sprague-Grundy). For the single-heap
subtraction game Sub({1,...,k}) the Grundy value has the exact closed form
    G(n) = n mod (k+1),
and for plain Nim on d heaps drawn uniformly from a binary range {0,...,2^b-1}
the exact P-position density is 1/2^b (the nim-sum is uniform on the group).

Gate battery (each direction stated):
  G1 SIGNIFICANCE (MC, |z| < Z_GATE PASS): Monte-Carlo P-position density of
     random 3-heap Nim over {0,...,7} agrees with the exact 1/8 within 3 sigma.
  G2 EXACT (Fraction, equality): exhaustive count of P-positions among all 8^3
     triples equals 8^2, i.e. the exact density is Fraction(1,8) with no error.
  G3 EXACT-GRUNDY (zero mismatch): the mex recurrence for Sub({1,2,3}) yields
     G(n) == n mod 4 for every n in [0, 256].
  G4 SPRAGUE-GRUNDY SUM (zero mismatch): the Grundy value of the disjunctive
     sum of two Sub({1,2,3}) heaps, computed by mex over the joint move set,
     equals G(a) XOR G(b) for every (a,b) in [0,40]^2.
  G5 ROBUSTNESS (holds under variation): G(n) == n mod (k+1) for every
     subtraction set {1,...,k}, k in {2,3,4,5}, over n in [0, 200].
  G6 FALSIFIABILITY (naive REJECTED, |z| > Z_GATE): the plausible-but-wrong
     "total-parity" rule (loss iff a+b+c is even) predicts density 1/2; the same
     Monte-Carlo sample rejects that prediction at large z (direction != G1).

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. build_results() is a
pure function of SEED and the fixed parameters; it embeds no digest of itself.
main() runs it twice, asserts the canonical JSON forms are byte-identical, then
prints results_sha256 over the compact-canonical form. A separate re-invocation
must reproduce the identical 64-hex digest. Nothing is written to disk.
"""

import hashlib
import json
import math
import random
import sys
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0

NIM_BASE = 8          # heaps drawn from {0, ..., NIM_BASE-1}; NIM_BASE = 2^3
NIM_HEAPS = 3
N_DRAWS = 200_000     # Monte-Carlo sample size for G1/G6
GRUNDY_N = 256        # G3 range [0, GRUNDY_N]
SUM_BOUND = 40        # G4 grid [0, SUM_BOUND]^2
ROBUST_N = 200        # G5 range [0, ROBUST_N]
ROBUST_KS = (2, 3, 4, 5)


def r6(x):
    return round(float(x), 6)


def frac_pair(f):
    return [f.numerator, f.denominator]


def grundy_subtraction(k, upto):
    """Grundy value of Sub({1,...,k}) heaps 0..upto via the mex recurrence."""
    moves = list(range(1, k + 1))
    g = [0] * (upto + 1)
    for n in range(1, upto + 1):
        reach = {g[n - s] for s in moves if n - s >= 0}
        m = 0
        while m in reach:
            m += 1
        g[n] = m
    return g


def grundy_sum_grid(k, bound):
    """Grundy value of the disjunctive sum of two Sub({1,...,k}) heaps on
    [0,bound]^2, computed directly by mex over the joint move set."""
    moves = list(range(1, k + 1))
    g = [[0] * (bound + 1) for _ in range(bound + 1)]
    for a in range(bound + 1):
        for b in range(bound + 1):
            if a == 0 and b == 0:
                continue
            reach = set()
            for s in moves:
                if a - s >= 0:
                    reach.add(g[a - s][b])
                if b - s >= 0:
                    reach.add(g[a][b - s])
            m = 0
            while m in reach:
                m += 1
            g[a][b] = m
    return g


def exact_p_density(base, heaps):
    """Exact fraction of d-heap Nim positions over {0,...,base-1} with
    nim-sum zero, by exhaustive enumeration."""
    total = base ** heaps
    count = 0

    def rec(i, acc):
        nonlocal count
        if i == heaps:
            if acc == 0:
                count += 1
            return
        for v in range(base):
            rec(i + 1, acc ^ v)

    rec(0, 0)
    return count, total, Fraction(count, total)


def mc_p_density(base, heaps, n_draws, seed):
    """Monte-Carlo P-position rate for random d-heap Nim over {0,...,base-1}."""
    rng = random.Random(seed)
    hits = 0
    for _ in range(n_draws):
        acc = 0
        for _h in range(heaps):
            acc ^= rng.randrange(base)
        if acc == 0:
            hits += 1
    return hits


def zscore(hits, n, p0):
    phat = hits / n
    se = math.sqrt(p0 * (1.0 - p0) / n)
    return (phat - p0) / se, phat, se


def build_results():
    results = {
        "proposal": 219,
        "verdict": 232,
        "slot": "round-52 GAME (fleet->venture->game->unrelated)",
        "seed": SEED,
        "z_gate": Z_GATE,
        "params": {
            "nim_base": NIM_BASE,
            "nim_heaps": NIM_HEAPS,
            "n_draws": N_DRAWS,
            "grundy_n": GRUNDY_N,
            "sum_bound": SUM_BOUND,
            "robust_n": ROBUST_N,
            "robust_ks": list(ROBUST_KS),
        },
    }

    # --- G2 EXACT: exhaustive P-position density == Fraction(1, base) ---
    count, total, dens = exact_p_density(NIM_BASE, NIM_HEAPS)
    g2_pass = (dens == Fraction(1, NIM_BASE)) and (count == NIM_BASE ** (NIM_HEAPS - 1))
    results["G2_exact_density"] = {
        "count": count,
        "total": total,
        "density": frac_pair(dens),
        "expected": frac_pair(Fraction(1, NIM_BASE)),
        "expected_count": NIM_BASE ** (NIM_HEAPS - 1),
        "pass": g2_pass,
    }

    # --- G1 SIGNIFICANCE: MC density agrees with exact 1/base, |z| < Z_GATE ---
    hits = mc_p_density(NIM_BASE, NIM_HEAPS, N_DRAWS, SEED)
    p_true = 1.0 / NIM_BASE
    z_true, phat, se = zscore(hits, N_DRAWS, p_true)
    g1_pass = abs(z_true) < Z_GATE
    results["G1_mc_significance"] = {
        "hits": hits,
        "n": N_DRAWS,
        "p_true": r6(p_true),
        "phat": r6(phat),
        "z": r6(z_true),
        "pass": g1_pass,
    }

    # --- G3 EXACT-GRUNDY: Sub({1,2,3}) G(n) == n mod 4 on [0, GRUNDY_N] ---
    g = grundy_subtraction(3, GRUNDY_N)
    g3_mismatch = sum(1 for n in range(GRUNDY_N + 1) if g[n] != n % 4)
    results["G3_subtraction_grundy"] = {
        "k": 3,
        "modulus": 4,
        "range": [0, GRUNDY_N],
        "mismatches": g3_mismatch,
        "pass": g3_mismatch == 0,
    }

    # --- G4 SPRAGUE-GRUNDY SUM: G(sum) == G(a) XOR G(b) on [0,SUM_BOUND]^2 ---
    g1heap = grundy_subtraction(3, SUM_BOUND)
    gsum = grundy_sum_grid(3, SUM_BOUND)
    g4_mismatch = 0
    for a in range(SUM_BOUND + 1):
        for b in range(SUM_BOUND + 1):
            if gsum[a][b] != (g1heap[a] ^ g1heap[b]):
                g4_mismatch += 1
    results["G4_sprague_grundy_sum"] = {
        "grid": [0, SUM_BOUND],
        "checked": (SUM_BOUND + 1) ** 2,
        "mismatches": g4_mismatch,
        "pass": g4_mismatch == 0,
    }

    # --- G5 ROBUSTNESS: G(n) == n mod (k+1) for k in ROBUST_KS ---
    robust = {}
    robust_all_pass = True
    for k in ROBUST_KS:
        gk = grundy_subtraction(k, ROBUST_N)
        mm = sum(1 for n in range(ROBUST_N + 1) if gk[n] != n % (k + 1))
        robust[str(k)] = {"modulus": k + 1, "mismatches": mm}
        robust_all_pass = robust_all_pass and (mm == 0)
    results["G5_robustness"] = {
        "range": [0, ROBUST_N],
        "per_k": robust,
        "pass": robust_all_pass,
    }

    # --- G6 FALSIFIABILITY: naive total-parity rule (density 1/2) REJECTED ---
    p_naive = 0.5
    z_naive, _, _ = zscore(hits, N_DRAWS, p_naive)
    g6_pass = abs(z_naive) > Z_GATE
    results["G6_falsifiability"] = {
        "naive_rule": "loss iff (a+b+c) even -> predicts density 1/2",
        "p_naive": r6(p_naive),
        "phat": r6(phat),
        "z_naive": r6(z_naive),
        "rejected": g6_pass,
        "pass": g6_pass,
    }

    gates = {
        "G1": results["G1_mc_significance"]["pass"],
        "G2": results["G2_exact_density"]["pass"],
        "G3": results["G3_subtraction_grundy"]["pass"],
        "G4": results["G4_sprague_grundy_sum"]["pass"],
        "G5": results["G5_robustness"]["pass"],
        "G6": results["G6_falsifiability"]["pass"],
    }
    order = ["G1", "G2", "G3", "G4", "G5", "G6"]
    first_failing = next((k for k in order if not gates[k]), None)
    results["gates"] = gates
    results["first_failing_gate"] = first_failing
    results["all_pass"] = all(gates[k] for k in order)
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
    order = ["G1", "G2", "G3", "G4", "G5", "G6"]
    for k in order:
        print(f"{k}: {'PASS' if r1['gates'][k] else 'FAIL'}")
    print()
    print(f"all_pass: {r1['all_pass']}")
    print(f"results_sha256: {digest}")
    sys.exit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
