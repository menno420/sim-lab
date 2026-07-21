#!/usr/bin/env python3
"""PROPOSAL 259 — Moore's Nim (Nim_k): a position is a P-position IFF every binary column-sum ≡ 0 (mod k+1).

HEAD: Moore's Nim (Nim_k), normal play (last player to move wins). A position is
a multiset of heap sizes (a_1,...,a_m). A move selects between 1 and k heaps
inclusive and removes a POSITIVE number of tokens from EACH selected heap.

MOORE'S THEOREM (established firsthand here): write every heap in binary; for
each bit-position j let c_j = Σ_i bit_j(a_i) be the column-sum of that bit across
all heaps. The position is a P-position (the player to move loses) IF AND ONLY
IF c_j ≡ 0 (mod k+1) for EVERY bit-position j. For k = 1 the modulus is 2, so the
criterion collapses to "every binary column-sum is even" — i.e. the nim-sum
(XOR) of the heaps is 0 — which is exactly ordinary Nim (Bouton's theorem).

The verifier proves the claim by building an INDEPENDENT from-scratch game oracle
— a memoized outcome recursion over sorted-tuple canonical states that knows
nothing of the theorem — and forcing it to agree with the CLOSED-FORM predicate
through FOUR gates, each in its own direction with real teeth:

  G1 EXACT (exhaustive, 0 mismatches): for k in {1,2,3}, enumerate ALL positions
     with m heaps (m = 1..M) and each heap in [0,H) — (k=1: M=4,H=8; k=2: M=4,H=6;
     k=3: M=4,H=5) — and assert moore_predicate(heaps,k) == (outcome_oracle is P)
     for EVERY position. Direction: theorem <=> true game outcome.

  G2 MONTE-CARLO agreement (|z| < 3): with (k,m,b) = (2,5,6), heaps uniform in
     [0,2^b). The EXACT analytic P-fraction is derived independently: for modulus
     q = k+1 each of the b bit-columns is a sum of m iid Bernoulli(1/2) bits, so
     P(one column-sum ≡ 0 mod q) = (Σ_{i≡0 mod q} C(m,i)) / 2^m as a Fraction, and
     the columns are independent so f = that ** b. Draw N iid positions with
     rng = random.Random(SEED), count how many satisfy moore_predicate -> p̂;
     z = (p̂ - f) / sqrt(f(1-f)/N). Direction: sampled frequency vs an
     independently-derived exact probability (genuine sampling variance).

  G3 INVARIANCE / robustness (0 violations): (a) k=1 collapse — over an
     exhaustive range assert moore_predicate(heaps,1) == (XOR of heaps == 0) for
     every position (ties the theorem to the classical Nim invariant). (b)
     permutation + zero-pad invariance — for many random positions assert
     moore_predicate AND outcome_oracle are unchanged under a random permutation
     of the heaps and under appending zero heaps. Direction: structural symmetry.

  G4 FALSIFIABILITY (reject a plausible-but-wrong rule at |z| > 3): the naive
     foil applies the ordinary-Nim rule (predict P <=> nim-sum XOR == 0, i.e.
     columns mod 2) to Moore's Nim with k=2 (whose true modulus is 3). Over N
     random k=2 positions with SMALL heaps (so the oracle is affordable), count
     foil misclassifications d against the TRUE outcome oracle -> error rate
     ê = d/N; z = (ê - 0)/sqrt(ê(1-ê)/N). PASS iff |z| > 3 (the foil is rejected).
     The true theorem predicate is recorded to make 0 errors on the same sample.
     Direction: refute a plausible-but-wrong rule.

Determinism: build_results() is a pure function of SEED and fixed params; every
sampling gate draws from a fresh random.Random(SEED[+offset]) so gate order
cannot perturb the payload; every heap multiset is canonicalised to a SORTED
tuple; every float enters the payload via a fixed 6-dp format string and every
count as an int; fractions are stored as "num/den". The whole results dict ->
canonical JSON (sort_keys) -> sha256 (FULL 64 hex, never truncated). An
in-process double-run is asserted byte-identical, and a separate re-invocation
reproduces the same digest. SEED = 20260717 (hardcoded module constant). Stdlib
only: argparse, functools, hashlib, itertools, json, math, random, sys, fractions.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import math
import random
import sys
from fractions import Fraction

SEED = 20260717


# ---------------------------------------------------------------------------
# CLOSED-FORM predicate (Moore's theorem). Does NOT reference the game oracle.
# ---------------------------------------------------------------------------
def moore_predicate(heaps, k: int) -> bool:
    """True iff for EVERY bit-position the column-sum of that bit across all
    heaps is ≡ 0 (mod k+1). This is Moore's P-position criterion for Nim_k."""
    q = k + 1
    nonzero = [h for h in heaps if h > 0]
    if not nonzero:
        return True  # all-zero position: every column-sum is 0
    width = max(h.bit_length() for h in nonzero)
    for j in range(width):
        col = 0
        for h in nonzero:
            col += (h >> j) & 1
        if col % q != 0:
            return False
    return True


def xor_all(heaps) -> int:
    acc = 0
    for h in heaps:
        acc ^= h
    return acc


# ---------------------------------------------------------------------------
# INDEPENDENT from-scratch game oracle (knows nothing of the theorem).
# A position is canonicalised to a sorted tuple of the POSITIVE heap sizes.
# A move selects 1..k of the (nonzero) heaps and removes a positive number of
# tokens from each selected heap (i.e. replaces each chosen heap value v by any
# new value in [0, v)). Terminal (all zero / empty) = P (the mover loses).
# A position is N (win) iff SOME legal move leads to a P-position; else P.
# ---------------------------------------------------------------------------
def canon(heaps) -> tuple:
    """Canonical state: sorted tuple of the strictly-positive heap sizes."""
    return tuple(sorted(h for h in heaps if h > 0))


def successors(state: tuple, k: int):
    """Yield every canonical successor of `state` under a legal Nim_k move."""
    n = len(state)
    idxs = range(n)
    for r in range(1, min(k, n) + 1):
        for chosen in itertools.combinations(idxs, r):
            ranges = [range(state[i]) for i in chosen]  # new value in [0, v)
            for newvals in itertools.product(*ranges):
                lst = list(state)
                for pos, nv in zip(chosen, newvals):
                    lst[pos] = nv
                yield tuple(sorted(v for v in lst if v > 0))


@functools.lru_cache(maxsize=None)
def _is_P(state: tuple, k: int) -> bool:
    """GROUND-TRUTH outcome via memoized recursion. True iff `state` is a
    P-position (the player to move loses). Terminal (empty) is a P-position."""
    if not state:
        return True
    for succ in successors(state, k):
        if _is_P(succ, k):
            return False  # a move to a P-position exists -> this is an N-position
    return True


def outcome_oracle(heaps, k: int) -> str:
    """True game outcome label: 'P' (mover loses) or 'N' (mover wins)."""
    return "P" if _is_P(canon(heaps), k) else "N"


# ---------------------------------------------------------------------------
# G1 — EXACT exhaustive: theorem <=> true game outcome for k in {1,2,3}.
# ---------------------------------------------------------------------------
G1_PARAMS = {1: (4, 8), 2: (4, 6), 3: (4, 5)}  # k -> (M heaps, H exclusive bound)


def gate_g1() -> dict:
    per_k = {}
    total_checked = 0
    total_mismatches = 0
    for k in (1, 2, 3):
        M, H = G1_PARAMS[k]
        checked = 0
        mismatches = 0
        for m in range(1, M + 1):
            for heaps in itertools.product(range(H), repeat=m):
                pred_p = moore_predicate(heaps, k)
                true_p = outcome_oracle(heaps, k) == "P"
                checked += 1
                if pred_p != true_p:
                    mismatches += 1
        per_k[str(k)] = {"M_heaps": M, "H_bound": H,
                         "positions_checked": checked, "mismatches": mismatches}
        total_checked += checked
        total_mismatches += mismatches
        assert mismatches == 0, f"G1 mismatch at k={k}"
    return {
        "per_k": per_k,
        "positions_checked": total_checked,
        "mismatches": total_mismatches,
        "direction": "theorem <=> true game outcome (exhaustive, k in {1,2,3})",
        "pass": total_mismatches == 0,
    }


# ---------------------------------------------------------------------------
# G2 — Monte-Carlo agreement vs an independently-derived exact P-fraction.
# ---------------------------------------------------------------------------
G2_K = 2
G2_M = 5
G2_B = 6
G2_N = 200_000


def _exact_p_fraction(k: int, m: int, b: int) -> Fraction:
    """Exact P-fraction f for m heaps uniform in [0,2^b), modulus q=k+1.
    Each bit-column is a sum of m iid Bernoulli(1/2) bits; per column
    P(sum ≡ 0 mod q) = (Σ_{i≡0 mod q} C(m,i)) / 2^m; columns independent -> **b."""
    q = k + 1
    num = sum(math.comb(m, i) for i in range(0, m + 1) if i % q == 0)
    per_col = Fraction(num, 1 << m)
    return per_col ** b


def gate_g2() -> dict:
    rng = random.Random(SEED)
    f = _exact_p_fraction(G2_K, G2_M, G2_B)
    ff = float(f)
    hi = 1 << G2_B
    hits = 0
    for _ in range(G2_N):
        heaps = [rng.randrange(hi) for _ in range(G2_M)]
        if moore_predicate(heaps, G2_K):
            hits += 1
    p_hat = hits / G2_N
    se = math.sqrt(ff * (1.0 - ff) / G2_N)
    z = (p_hat - ff) / se
    return {
        "k": G2_K, "m": G2_M, "b": G2_B, "N": G2_N,
        "f_frac": f"{f.numerator}/{f.denominator}",
        "f_float": f"{ff:.6f}",
        "hits": hits,
        "p_hat": f"{p_hat:.6f}",
        "z": f"{z:.6f}",
        "direction": "sampled moore_predicate frequency vs independent exact P-fraction",
        "pass": abs(z) < 3.0,
    }


# ---------------------------------------------------------------------------
# G3 — invariance / robustness.
# ---------------------------------------------------------------------------
G3A_PARAMS = (4, 8)  # k=1 collapse: m=1..4, heaps in [0,8)
G3B_POSITIONS = 400
G3B_MAX_M = 4
G3B_H = 6
G3B_PAD_MAX = 3


def gate_g3() -> dict:
    # (a) k=1 collapse: moore_predicate(heaps,1) == (XOR of heaps == 0), exhaustive
    M, H = G3A_PARAMS
    collapse_checked = 0
    collapse_violations = 0
    for m in range(1, M + 1):
        for heaps in itertools.product(range(H), repeat=m):
            collapse_checked += 1
            if moore_predicate(heaps, 1) != (xor_all(heaps) == 0):
                collapse_violations += 1
    assert collapse_violations == 0

    # (b) permutation + zero-pad invariance of BOTH moore_predicate and outcome_oracle
    rng = random.Random(SEED + 7)
    perm_violations = 0
    pad_violations = 0
    positions = 0
    for _ in range(G3B_POSITIONS):
        k = rng.choice((1, 2, 3))
        m = rng.randint(1, G3B_MAX_M)
        heaps = [rng.randrange(G3B_H) for _ in range(m)]
        positions += 1

        base_pred = moore_predicate(heaps, k)
        base_out = outcome_oracle(heaps, k)

        permuted = heaps[:]
        rng.shuffle(permuted)
        if moore_predicate(permuted, k) != base_pred:
            perm_violations += 1
        if outcome_oracle(permuted, k) != base_out:
            perm_violations += 1

        padded = heaps + [0] * rng.randint(1, G3B_PAD_MAX)
        if moore_predicate(padded, k) != base_pred:
            pad_violations += 1
        if outcome_oracle(padded, k) != base_out:
            pad_violations += 1
    assert perm_violations == 0 and pad_violations == 0

    total_violations = collapse_violations + perm_violations + pad_violations
    return {
        "collapse_checked": collapse_checked,
        "collapse_violations": collapse_violations,
        "invariance_positions": positions,
        "perm_violations": perm_violations,
        "pad_violations": pad_violations,
        "total_violations": total_violations,
        "direction": "structural symmetries (k=1 collapse to X=0; permutation + zero-pad)",
        "pass": total_violations == 0,
    }


# ---------------------------------------------------------------------------
# G4 — falsifiability: reject the ordinary-Nim (mod 2) foil applied to k=2.
# ---------------------------------------------------------------------------
G4_K = 2
G4_M = 4
G4_H = 4       # SMALL heaps (0..3) so the true oracle is affordable
G4_N = 5000


def gate_g4() -> dict:
    rng = random.Random(SEED)
    foil_errors = 0        # foil (nim-sum==0 => P) misclassifications vs true outcome
    theorem_errors = 0     # Moore predicate errors vs true outcome (must be 0)
    for _ in range(G4_N):
        heaps = [rng.randrange(G4_H) for _ in range(G4_M)]
        true_p = outcome_oracle(heaps, G4_K) == "P"
        foil_p = (xor_all(heaps) == 0)          # ordinary-Nim rule (mod 2)
        theo_p = moore_predicate(heaps, G4_K)   # true rule (mod 3)
        if foil_p != true_p:
            foil_errors += 1
        if theo_p != true_p:
            theorem_errors += 1
    assert theorem_errors == 0, "Moore predicate disagreed with the true oracle"

    e_hat = foil_errors / G4_N
    if e_hat <= 0.0 or e_hat >= 1.0:
        # SE floor / rule-of-three convention if the rate rounds SE to 0
        se = math.sqrt((3.0 / G4_N) * (1.0 - 3.0 / G4_N) / G4_N)
    else:
        se = math.sqrt(e_hat * (1.0 - e_hat) / G4_N)
    z = (e_hat - 0.0) / se
    return {
        "k": G4_K, "m": G4_M, "H_bound": G4_H, "N": G4_N,
        "foil": "ordinary-Nim rule: predict P <=> nim-sum XOR == 0 (columns mod 2)",
        "foil_errors": foil_errors,
        "foil_error_rate": f"{e_hat:.6f}",
        "z_foil": f"{z:.6f}",
        "theorem_errors": theorem_errors,
        "direction": "refute a plausible-but-wrong rule (ordinary Nim applied to k=2)",
        "pass": abs(z) > 3.0 and theorem_errors == 0,
    }


# ---------------------------------------------------------------------------
# Anchors — a few illustrative positions with theorem vs true outcome.
# ---------------------------------------------------------------------------
ANCHORS = [
    ((3, 5, 7), 1),   # ordinary Nim: XOR = 1 != 0  -> N
    ((1, 1, 1), 2),   # bit0 column-sum = 3 ≡ 0 mod 3 -> P
    ((2, 2, 2), 2),   # bit1 column-sum = 3 ≡ 0 mod 3 -> P
    ((1, 1), 2),      # bit0 column-sum = 2 ≢ 0 mod 3 -> N
    ((7, 7, 7), 2),   # every column-sum = 3 ≡ 0 mod 3 -> P
    ((1, 2, 3), 3),   # modulus 4 -> N
]


def build_anchors() -> dict:
    out = {}
    for heaps, k in ANCHORS:
        pred_p = moore_predicate(heaps, k)
        outcome = outcome_oracle(heaps, k)
        assert pred_p == (outcome == "P"), f"anchor mismatch {heaps} k={k}"
        key = f"{'-'.join(map(str, heaps))}|k{k}"
        out[key] = {
            "heaps": list(heaps),
            "k": k,
            "moore_predicate_P": pred_p,
            "outcome": outcome,
            "agree": pred_p == (outcome == "P"),
        }
    return out


# ---------------------------------------------------------------------------
# Orchestration.
# ---------------------------------------------------------------------------
def build_results() -> dict:
    g1 = gate_g1()
    g2 = gate_g2()
    g3 = gate_g3()
    g4 = gate_g4()
    anchors = build_anchors()

    order = [("G1", g1), ("G2", g2), ("G3", g3), ("G4", g4)]
    all_pass = all(g["pass"] for _, g in order)
    first_failing = next((name for name, g in order if not g["pass"]), None)

    return {
        "proposal": 259,
        "claim": "Moore's Nim (Nim_k), normal play: a position is a P-position "
                 "IFF every binary column-sum c_j = Σ_i bit_j(a_i) ≡ 0 (mod k+1); "
                 "for k=1 this is ordinary Nim (nim-sum XOR == 0)",
        "SEED": SEED,
        "anchors": anchors,
        "G1": g1,
        "G2": g2,
        "G3": g3,
        "G4": g4,
        "all_gates_pass": all_pass,
        "first_failing_gate": first_failing,
        "decision": "PASS" if all_pass else "FAIL",
    }


def canonical_json(results: dict) -> str:
    return json.dumps(results, sort_keys=True, separators=(",", ":"))


def digest_of(results: dict) -> str:
    return hashlib.sha256(canonical_json(results).encode("utf-8")).hexdigest()


def print_summary(results: dict, d: str) -> None:
    for name in ("G1", "G2", "G3", "G4"):
        print(f"{name}: {'PASS' if results[name]['pass'] else 'FAIL'}")
    print()
    print("anchors (heaps | k -> moore_predicate_P / true outcome):")
    for key, a in results["anchors"].items():
        print(f"  {key:>14}: moore_P={str(a['moore_predicate_P']):>5} "
              f"outcome={a['outcome']}  agree={a['agree']}")
    print()
    g1 = results["G1"]
    print(f"G1: positions_checked={g1['positions_checked']} "
          f"mismatches={g1['mismatches']} "
          f"(k1={g1['per_k']['1']['positions_checked']}, "
          f"k2={g1['per_k']['2']['positions_checked']}, "
          f"k3={g1['per_k']['3']['positions_checked']})")
    g2 = results["G2"]
    print(f"G2: f={g2['f_frac']} (~{g2['f_float']}) p_hat={g2['p_hat']} "
          f"z={g2['z']} (N={g2['N']})")
    g3 = results["G3"]
    print(f"G3: collapse_violations={g3['collapse_violations']} "
          f"perm_violations={g3['perm_violations']} "
          f"pad_violations={g3['pad_violations']}")
    g4 = results["G4"]
    print(f"G4: foil_error_rate={g4['foil_error_rate']} z_foil={g4['z_foil']} "
          f"theorem_errors={g4['theorem_errors']} (N={g4['N']})")
    print()
    print(f"all_gates_pass={results['all_gates_pass']} "
          f"first_failing_gate={results['first_failing_gate']} "
          f"decision={results['decision']}")
    print()
    print(json.dumps(results, indent=2, sort_keys=True))
    print()
    print(f"results_sha256 = {d}")


def main(argv) -> int:
    parser = argparse.ArgumentParser(description="Moore's Nim (Nim_k) verifier (PROPOSAL 259).")
    parser.add_argument("--selfcheck", action="store_true",
                        help="run compute twice in-process, assert byte-identical digests")
    args = parser.parse_args(argv)

    if args.selfcheck:
        r1 = build_results()
        d1 = digest_of(r1)
        r2 = build_results()
        d2 = digest_of(r2)
        ok = d1 == d2
        print("SELFCHECK: byte-identical" if ok else "SELFCHECK: MISMATCH")
        print(f"results_sha256 = {d1}")
        return 0 if ok else 1

    results = build_results()
    d = digest_of(results)

    # in-process double-run determinism self-check
    results2 = build_results()
    d2 = digest_of(results2)
    identical = (d == d2)
    assert identical, "in-process double-run produced a different digest"

    print_summary(results, d)
    print()
    print(f"determinism: in-process double-run identical = {identical}")
    return 0 if results["all_gates_pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
