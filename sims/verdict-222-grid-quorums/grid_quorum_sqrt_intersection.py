#!/usr/bin/env python3
"""Maekawa grid quorums -- a sqrt(N) read/write set beats the majority.

Arrange N = k*k replicas on a k x k grid. The quorum for a cell = (all cells in
its ROW) union (all cells in its COLUMN), size 2k-1 ~ 2*sqrt(N). ANY two such
grid quorums intersect: a row and a column always cross at exactly one cell, so
mutual-exclusion / read-write intersection is guaranteed with a quorum ~2*sqrt(N)
instead of a majority ~N/2. Counterintuitive: people assume you need a majority
to guarantee intersection -- you don't. But STRUCTURE, not size, buys it: two
RANDOM subsets of the SAME size 2k-1 are disjoint with positive probability
(violating intersection), while grid quorums never are. This is the Maekawa grid
quorum.

Deterministic, stdlib-only. SEED = 20260717. All gates pre-registered AFTER a
feasibility probe of the true closed-form values (printed below before any
threshold is asserted).
"""
import hashlib
import itertools
import json
import random
from fractions import Fraction
from math import comb, sqrt

SEED = 20260717
K_MAIN = 6                       # main grid: N = 36, quorum size 2k-1 = 11
K_SHIFT = [4, 5, 6, 7, 8, 9, 10] # robustness sweep
T_MC = 2_000_000                 # Monte-Carlo draws for the disjoint-rate gates


def grid_quorum(cell, k):
    """Quorum for `cell` on a k x k grid: its row union its column (size 2k-1)."""
    r, c = divmod(cell, k)
    row = {r * k + j for j in range(k)}
    col = {j * k + c for j in range(k)}
    return row | col


def all_grid_quorums(k):
    return [grid_quorum(cell, k) for cell in range(k * k)]


def grid_intersection_fraction(k):
    """Fraction of unordered pairs of the k*k grid quorums that intersect (exact)."""
    quorums = all_grid_quorums(k)
    pairs = 0
    hit = 0
    for a, b in itertools.combinations(quorums, 2):
        pairs += 1
        if a & b:
            hit += 1
    return Fraction(hit, pairs)


def closed_form_disjoint_prob(n, s):
    """P(two independent uniform-random s-subsets of an N-set are disjoint), exact.
    Fix subset A of size s; a second independent s-subset avoids A iff it lies in
    the remaining N-s elements: C(N-s, s) / C(N, s)."""
    return Fraction(comb(n - s, s), comb(n, s))


def mc_disjoint_rate(n, s, t, rng):
    """Monte-Carlo estimate of the two-random-s-subset disjoint probability."""
    universe = range(n)
    hits = 0
    for _ in range(t):
        a = frozenset(rng.sample(universe, s))
        b = rng.sample(universe, s)
        if a.isdisjoint(b):
            hits += 1
    return hits, hits / t


def compute():
    k = K_MAIN
    n = k * k                    # 36
    s = 2 * k - 1                # 11

    # --- FEASIBILITY PROBE (closed-form, printed before thresholds asserted) ---
    p_closed = closed_form_disjoint_prob(n, s)      # exact Fraction
    p_closed_f = float(p_closed)

    # --- G1: EXACT pairwise intersection of grid quorums (exhaustive, k=6) ---
    g1_frac = grid_intersection_fraction(k)         # must be Fraction(1)

    # --- MC disjoint-rate (shared by G2 and G3) ---
    rng = random.Random(SEED)
    hits, rate = mc_disjoint_rate(n, s, T_MC, rng)

    # --- G2: MC agrees with the closed form (convergence gate, LOW |z|) ---
    se_closed = sqrt(p_closed_f * (1 - p_closed_f) / T_MC)
    z_converge = (rate - p_closed_f) / se_closed

    # --- G3: the same disjoint-rate is significantly > 0 (surprise, HIGH z) ---
    se_hat = sqrt(rate * (1 - rate) / T_MC)
    z_surprise = rate / se_hat

    # --- G4: robustness / shift across k in {4..10} (exact/deterministic) ---
    shift_rows = []
    prev_ratio = None
    ratio_decreasing = True
    all_exact = True
    all_beats_majority = True
    for kk in K_SHIFT:
        nn = kk * kk
        ss = 2 * kk - 1
        frac = grid_intersection_fraction(kk)
        majority = nn // 2 + 1
        ratio = Fraction(ss, nn)
        if frac != 1:
            all_exact = False
        if not (ss < majority):
            all_beats_majority = False
        if prev_ratio is not None and not (ratio < prev_ratio):
            ratio_decreasing = False
        prev_ratio = ratio
        shift_rows.append({
            "k": kk, "N": nn, "quorum_size_2k_minus_1": ss,
            "majority_size": majority, "grid_intersection_fraction": str(frac),
            "size_ratio_2k_minus_1_over_N": str(ratio),
        })

    return {
        "head": "grid-quorum-sqrt-intersection",
        "seed": SEED,
        "params": {"k_main": K_MAIN, "N_main": n, "quorum_size_main": s,
                   "k_shift": list(K_SHIFT), "t_mc": T_MC},
        "feasibility_probe": {
            "closed_form_disjoint_prob": str(p_closed),
            "closed_form_disjoint_prob_float": round(p_closed_f, 12),
            "note": "closed form computed FIRST; thresholds below are what this math meets",
        },
        "G1_exact_grid_intersection": {
            "k": k, "N": n, "num_grid_quorums": n,
            "num_pairs": comb(n, 2),
            "intersection_fraction": str(g1_frac),
            "pass": g1_frac == 1,
            "direction": "exact-equality (Fraction == 1): EVERY grid-quorum pair intersects",
        },
        "G2_mc_agrees_closed_form": {
            "mc_disjoint_rate": round(rate, 12),
            "closed_form_disjoint_prob": round(p_closed_f, 12),
            "se_closed": round(se_closed, 12),
            "z": round(z_converge, 4),
            "threshold": 3.0,
            "pass": abs(z_converge) < 3.0,
            "direction": "LOW |z| = CONVERGENCE (MC disjoint-rate agrees with the closed form)",
        },
        "G3_surprise_disjoint_positive": {
            "mc_disjoint_rate": round(rate, 12),
            "mc_disjoint_hits": hits,
            "se_hat": round(se_hat, 12),
            "z": round(z_surprise, 4),
            "threshold": 3.0,
            "pass": z_surprise >= 3.0,
            "direction": "HIGH z = SURPRISE (same-size RANDOM subsets genuinely fail to always intersect; STRUCTURE, not size, buys the guarantee)",
        },
        "G4_shift_robustness": {
            "k_range": [K_SHIFT[0], K_SHIFT[-1]],
            "rows": shift_rows,
            "all_grid_intersection_exact_1": all_exact,
            "all_quorum_beats_majority": all_beats_majority,
            "size_ratio_strictly_decreasing": ratio_decreasing,
            "pass": all_exact and all_beats_majority and ratio_decreasing,
            "direction": "exact-equality across k: grid always intersects, 2k-1 < majority, ratio (2k-1)/N strictly decreasing (savings scale with N)",
        },
    }


def main():
    r1 = compute()
    r2 = compute()
    identical = (r1 == r2)
    r1["G5_determinism"] = {
        "in_process_double_run": "IDENTICAL" if identical else "DIVERGED",
        "pass": identical,
    }
    gates = ["G1_exact_grid_intersection", "G2_mc_agrees_closed_form",
             "G3_surprise_disjoint_positive", "G4_shift_robustness",
             "G5_determinism"]
    r1["all_gates_pass"] = all(r1[g]["pass"] for g in gates)

    print(json.dumps(r1, indent=2, sort_keys=True))
    canon = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canon.encode()).hexdigest()

    fp = r1["feasibility_probe"]
    print()
    print("--- feasibility probe (closed form computed BEFORE thresholds) ---")
    print(f"closed_form_disjoint_prob(N=36,s=11) = {fp['closed_form_disjoint_prob']} "
          f"= {fp['closed_form_disjoint_prob_float']}")
    print("--- gate verdicts (direction stated) ---")
    print(f"G1 exact grid intersection : pass={r1['G1_exact_grid_intersection']['pass']} "
          f"fraction={r1['G1_exact_grid_intersection']['intersection_fraction']} "
          f"[exact-equality == 1]")
    print(f"G2 MC vs closed form       : pass={r1['G2_mc_agrees_closed_form']['pass']} "
          f"z={r1['G2_mc_agrees_closed_form']['z']} [LOW |z| convergence, <3]")
    print(f"G3 disjoint-rate surprise  : pass={r1['G3_surprise_disjoint_positive']['pass']} "
          f"z={r1['G3_surprise_disjoint_positive']['z']} [HIGH z surprise, >=3]")
    print(f"G4 shift/robustness        : pass={r1['G4_shift_robustness']['pass']} "
          f"[exact-equality across k, ratio strictly decreasing]")
    print(f"G5 determinism             : pass={r1['G5_determinism']['pass']} "
          f"[{r1['G5_determinism']['in_process_double_run']}]")
    print(f"all_gates_pass = {r1['all_gates_pass']}")
    print(f"results_sha256: {digest}")
    return 0 if r1["all_gates_pass"] else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
