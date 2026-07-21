#!/usr/bin/env python3
"""PROPOSAL 239 - Wythoff's game: the cold (P) positions are EXACTLY the
golden-ratio Beatty pairs.

Claim (exact, closed-form). For Wythoff's game (two piles; a move removes
k>=1 from one pile, or removes the SAME k>=1 from both piles; last to move
wins), the P-positions (cold / previous-player-wins positions, i.e. the
Sprague-Grundy value 0 positions) are exactly

        P_n = (a_n, b_n),   a_n = floor(n*phi),  b_n = floor(n*phi^2),

for n = 0, 1, 2, ..., with phi = (1 + sqrt 5) / 2 the golden ratio, and the
EXACT integer identity

        b_n = a_n + n.

The two sequences {a_n} (lower Wythoff, OEIS A000201) and {b_n} (upper
Wythoff, A001950) PARTITION the positive integers (Beatty's theorem, because
1/phi + 1/phi^2 = 1): every positive integer appears in exactly one of them.
The lower sequence therefore has natural density 1/phi ~ 0.618034, NOT 1/2.

Exact floor without floats:  a_n = (n + isqrt(5*n*n)) // 2,  b_n = a_n + n.
Sanity anchors (n = 0..8): (0,0),(1,2),(3,5),(4,7),(6,10),(8,13),(9,15),
(11,18),(12,20).

SEED = 20260717. build_results() is a pure function of SEED and the module
constants (one seeded random.Random(SEED) consumed in fixed order; no
wall-clock / PID / unordered-set iteration in the hashed payload), so an
in-process double-run and a separate re-invocation are byte-identical;
results_sha256 is the sha256 of the canonical results dict.

Four gates, each in its own direction:
  G1 EXACT      - integer/exact arithmetic (fractions.Fraction where a ratio
                  appears): the Grundy-0 board positions from a mex-DP equal
                  EXACTLY the isqrt-Beatty pairs; b_n - a_n == n for all n;
                  and {a_n} u {b_n} partitions 1..M exactly (no gap, no
                  overlap). error_count must be 0.
  G2 MC AGREE   - a uniform random integer in [1, M] lands in the lower
                  Wythoff set {a_n} with probability estimated p_hat; it
                  agrees with the theoretical density 1/phi at |z| < Z_ACCEPT.
  G3 INVARIANCE - two independent P-position generators (isqrt-Beatty vs the
                  greedy mex construction a_n = mex{a_i,b_i : i<n}, b_n =
                  a_n + n) agree exactly; and the Grundy table is pile-swap
                  symmetric G(x,y) == G(y,x). mismatch_count must be 0.
  G4 FALSIFY    - on the SAME MC sample, the naive foil F2 "lower density =
                  1/2 (even split)" is rejected at |z_reject| >= Z_REJECT;
                  and the naive UNIVERSAL foil F1 "every P-position is (k, 2k),
                  i.e. b_n == 2*a_n" is refuted exactly (it holds only at the
                  two coincidental fits n=0 (0,0) and n=1 (1,2), and breaks at
                  n=2 -> (3,5) and every n >= 2 thereafter).

Stdlib only: json, hashlib, math, random, fractions.
"""

import json
import hashlib
import math
import random
from fractions import Fraction

SEED = 20260717

# ---- gate constants -------------------------------------------------------
BOARD_PANEL = [30, 60, 90]        # Grundy mex-DP board sizes (G1/G3)
PARTITION_PANEL = [1_000, 100_000, 1_000_000]  # exact-partition M values (G1)
N_IDENTITY = 200_000              # range of n over which b_n == a_n + n is checked
MC_M = 1_000_000                  # MC universe [1, M]
MC_K = 200_000                    # MC sample size
Z_ACCEPT = 3.0
Z_REJECT = 6.0

# phi = (1 + sqrt 5) / 2 ; 1/phi = phi - 1 = (sqrt 5 - 1) / 2 (density target)
SQRT5 = math.sqrt(5.0)
INV_PHI = (SQRT5 - 1.0) / 2.0     # 1/phi ~ 0.6180339887498949


# ---- exact Beatty closed form (integer arithmetic, no floats) -------------
def a_of(n):
    """Lower Wythoff a_n = floor(n*phi) = (n + isqrt(5 n^2)) // 2 (exact)."""
    return (n + math.isqrt(5 * n * n)) // 2


def b_of(n):
    """Upper Wythoff b_n = floor(n*phi^2) = a_n + n (exact)."""
    return a_of(n) + n


# ---- Sprague-Grundy mex-DP over the Wythoff board -------------------------
def grundy_table(N):
    """G[x][y] for 0<=x,y<=N. Moves from (x,y): remove k>=1 from one pile
    (x-k,y) or (x,y-k); remove k>=1 from both (x-k,y-k). G = mex of reachable."""
    G = [[0] * (N + 1) for _ in range(N + 1)]
    for x in range(N + 1):
        for y in range(N + 1):
            seen = set()
            for xp in range(x):
                seen.add(G[xp][y])
            for yp in range(y):
                seen.add(G[x][yp])
            k = 1
            while x - k >= 0 and y - k >= 0:
                seen.add(G[x - k][y - k])
                k += 1
            m = 0
            while m in seen:
                m += 1
            G[x][y] = m
    return G


def dp_cold_positions(N):
    """Sorted list of (x,y) with x<=y, both in [0,N], Grundy value 0."""
    G = grundy_table(N)
    cold = []
    for x in range(N + 1):
        for y in range(x, N + 1):
            if G[x][y] == 0:
                cold.append((x, y))
    return sorted(cold), G


def formula_cold_positions(N):
    """Sorted list of (a_n, b_n) with b_n <= N from the isqrt-Beatty form."""
    cold = []
    n = 0
    while True:
        a, b = a_of(n), b_of(n)
        if b > N:
            break
        cold.append((a, b))
        n += 1
    return sorted(cold)


# ---- greedy mex generator (independent of the isqrt form) ------------------
def greedy_cold_positions(count):
    """a_n = mex{a_i, b_i : i<n}, b_n = a_n + n, for n = 0..count-1."""
    used = set()
    a_seq, b_seq = [], []
    for n in range(count):
        m = 0
        while m in used:
            m += 1
        a = m
        b = a + n
        a_seq.append(a)
        b_seq.append(b)
        used.add(a)
        used.add(b)
    return a_seq, b_seq


# ---- lower-Wythoff membership set up to M ----------------------------------
def lower_set_upto(M):
    """Set {a_n : a_n <= M} via the exact isqrt floor."""
    s = set()
    n = 1
    while True:
        a = a_of(n)
        if a > M:
            break
        s.add(a)
        n += 1
    return s


# ---- gates ----------------------------------------------------------------
def gate1_exact():
    error_count = 0
    rows = []

    # (a) Grundy-0 board positions == isqrt-Beatty pairs, EXACT set identity.
    for N in BOARD_PANEL:
        dp_cold, _ = dp_cold_positions(N)
        fm_cold = formula_cold_positions(N)
        set_equal = (dp_cold == fm_cold)
        if not set_equal:
            error_count += 1
        # genuine ratio: closed-form count vs mex-DP count, via Fraction.
        count_equal = (Fraction(len(dp_cold)) == Fraction(len(fm_cold)))
        if not count_equal:
            error_count += 1
        rows.append({
            "N": N,
            "dp_cold_count": len(dp_cold),
            "formula_cold_count": len(fm_cold),
            "set_identity": set_equal,
            "count_ratio_equal_fraction": count_equal,
        })

    # (b) b_n - a_n == n exactly for all n in range.
    identity_errors = 0
    for n in range(N_IDENTITY + 1):
        if b_of(n) - a_of(n) != n:
            identity_errors += 1
    if identity_errors:
        error_count += identity_errors

    # (c) exact Beatty PARTITION: {a_n} u {b_n} hits every integer 1..M once.
    partition_rows = []
    for M in PARTITION_PANEL:
        lower = set()
        upper = set()
        n = 1
        while True:
            a = a_of(n)
            if a <= M:
                lower.add(a)
            b = b_of(n)
            if b <= M:
                upper.add(b)
            # a_n grows ~ n*phi, b_n ~ n*phi^2; stop when both exceed M.
            if a > M and b > M:
                break
            n += 1
        overlap = lower & upper
        union = lower | upper
        target = set(range(1, M + 1))
        no_overlap = (len(overlap) == 0)
        covers_all = (union == target)
        # exact rational count identity: |lower| + |upper| == M
        counts_partition = (Fraction(len(lower) + len(upper)) == Fraction(M))
        exact_partition = no_overlap and covers_all and counts_partition
        if not exact_partition:
            error_count += 1
        # empirical lower density on 1..M as an exact reduced Fraction (report).
        lower_density = Fraction(len(lower), M)
        partition_rows.append({
            "M": M,
            "lower_count": len(lower),
            "upper_count": len(upper),
            "overlap_count": len(overlap),
            "no_overlap": no_overlap,
            "covers_1..M": covers_all,
            "counts_sum_equals_M_fraction": counts_partition,
            "exact_partition": exact_partition,
            "lower_density_fraction": str(lower_density),
            "lower_density_float": round(float(lower_density), 6),
        })

    ok = (error_count == 0)
    return ok, {
        "board_set_identity": rows,
        "b_minus_a_equals_n": {"n_range": N_IDENTITY, "errors": identity_errors},
        "beatty_partition": partition_rows,
        "error_count": error_count,
        "pass_if": "error_count == 0",
    }


def _mc_sample():
    """Draw MC_K uniform ints in [1, MC_M]; count membership in lower set."""
    lower = lower_set_upto(MC_M)
    rng = random.Random(SEED)
    hits = 0
    for _ in range(MC_K):
        v = rng.randint(1, MC_M)
        if v in lower:
            hits += 1
    return hits, MC_K


def gate2_mc_agreement(sample):
    hits, K = sample
    p_hat = hits / K
    p = INV_PHI
    se = math.sqrt(p * (1.0 - p) / K)
    z = (p_hat - p) / se
    return abs(z) < Z_ACCEPT, {
        "M": MC_M, "K": K, "hits": hits,
        "p_hat": round(p_hat, 6),
        "target_density_inv_phi": round(p, 6),
        "z": round(z, 6),
        "z_accept": Z_ACCEPT,
        "pass_if": "abs(z) < Z_ACCEPT",
    }


def gate3_invariance():
    mismatch_count = 0
    rows = []

    # (i) two independent P-position generators agree exactly.
    for N in BOARD_PANEL:
        fm_cold = formula_cold_positions(N)      # isqrt-Beatty
        count = len(fm_cold)
        ga, gb = greedy_cold_positions(count)    # greedy mex
        greedy_cold = sorted(zip(ga, gb))
        agree = (greedy_cold == fm_cold)
        if not agree:
            mismatch_count += 1
        rows.append({
            "N": N, "positions": count,
            "isqrt_vs_greedy_mex_identical": agree,
        })

    # (ii) pile-swap symmetry G(x,y) == G(y,x) over the board.
    swap_rows = []
    for N in BOARD_PANEL:
        _, G = dp_cold_positions(N)
        asym = 0
        for x in range(N + 1):
            for y in range(N + 1):
                if G[x][y] != G[y][x]:
                    asym += 1
        if asym:
            mismatch_count += asym
        swap_rows.append({"N": N, "asymmetric_cells": asym})

    ok = (mismatch_count == 0)
    return ok, {
        "generator_agreement": rows,
        "pile_swap_symmetry": swap_rows,
        "mismatch_count": mismatch_count,
        "pass_if": "mismatch_count == 0",
    }


def gate4_falsify(sample):
    hits, K = sample
    p_hat = hits / K

    # F2: naive "lower density = 1/2 (even split)" -- reject on SAME sample.
    p0 = 0.5
    se0 = math.sqrt(0.25 / K)
    z_reject = (p_hat - p0) / se0
    f2_rejected = abs(z_reject) >= Z_REJECT

    # F1: naive UNIVERSAL rule "every P-position is (k, 2k), i.e. b_n==2*a_n".
    # Refuted by exhibiting counterexamples: b_n==2*a_n forces n==a_n, which
    # (since a_n=floor(n*phi)>n for all n>=2) holds ONLY at the two smallest
    # positions n=0 (0,0) and n=1 (1,2). Every n>=2 is a counterexample.
    f1_fits = []          # P-positions that coincidentally satisfy b_n==2*a_n
    f1_counterexamples = 0
    f1_first_counterexample = None
    for n in range(N_IDENTITY + 1):
        a, b = a_of(n), b_of(n)
        if b == 2 * a:
            f1_fits.append([a, b])
        else:
            f1_counterexamples += 1
            if f1_first_counterexample is None:
                f1_first_counterexample = [n, a, b]
    # The universal rule is refuted iff there is at least one P-position not of
    # the form (k, 2k) -- and it breaks immediately at n=2 -> (3,5).
    f1_refuted = (f1_counterexamples >= 1 and f1_first_counterexample == [2, 3, 5])

    ok = f2_rejected and f1_refuted
    return ok, {
        "F2_naive_even_split": {
            "claim": "lower Wythoff density == 1/2",
            "p_hat": round(p_hat, 6),
            "z_reject": round(z_reject, 6),
            "z_reject_threshold": Z_REJECT,
            "rejected": f2_rejected,
        },
        "F1_naive_k_2k": {
            "claim": "every P-position is (k, 2k), i.e. b_n == 2*a_n (universal)",
            "coincidental_fits": f1_fits,
            "n_range": N_IDENTITY,
            "counterexample_count": f1_counterexamples,
            "first_counterexample_n_a_b": f1_first_counterexample,
            "refuted": f1_refuted,
        },
        "pass_if": "abs(z_reject) >= Z_REJECT and F1 has counterexamples (first at n=2 -> (3,5))",
    }


def build_results():
    sample = _mc_sample()

    g1_ok, g1 = gate1_exact()
    g2_ok, g2 = gate2_mc_agreement(sample)
    g3_ok, g3 = gate3_invariance()
    g4_ok, g4 = gate4_falsify(sample)

    gates = {
        "G1_exact_beatty": {"name": "Grundy-0 == isqrt-Beatty; b-a==n; exact partition",
                            "ok": g1_ok, **g1},
        "G2_montecarlo_density": {"name": "MC lower density agrees with 1/phi",
                                  "ok": g2_ok, **g2},
        "G3_invariance": {"name": "isqrt vs greedy-mex agree; pile-swap symmetry",
                          "ok": g3_ok, **g3},
        "G4_falsifiability": {"name": "even-split foil rejected; (k,2k) foil refuted",
                              "ok": g4_ok, **g4},
    }
    order = ["G1_exact_beatty", "G2_montecarlo_density",
             "G3_invariance", "G4_falsifiability"]
    first_failing = next((g for g in order if not gates[g]["ok"]), None)
    all_pass = first_failing is None

    return {
        "claim": ("wythoff_beatty: P-positions == (floor(n*phi), floor(n*phi^2)) "
                  "with b_n == a_n + n; {a_n},{b_n} partition Z+; density 1/phi"),
        "seed": SEED,
        "params": {
            "board_panel": BOARD_PANEL,
            "partition_panel": PARTITION_PANEL,
            "n_identity_range": N_IDENTITY,
            "mc_M": MC_M,
            "mc_K": MC_K,
            "z_accept": Z_ACCEPT,
            "z_reject": Z_REJECT,
        },
        "anchors": [[a_of(n), b_of(n)] for n in range(9)],
        "gates": gates,
        "all_gates_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "PASS" if all_pass else "FAIL",
    }


def canonical(r):
    return json.dumps(r, sort_keys=True, separators=(",", ":"))


def main():
    c1 = canonical(build_results())
    c2 = canonical(build_results())
    assert c1 == c2, "NON-DETERMINISTIC: in-process double-run diverged"
    digest = hashlib.sha256(c1.encode()).hexdigest()
    results = build_results()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("in_process_double_run: IDENTICAL")
    print("results_sha256: " + digest)
    print("decision: " + results["decision"])
    raise SystemExit(0 if results["all_gates_pass"] else 1)


if __name__ == "__main__":
    main()
