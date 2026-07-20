#!/usr/bin/env python3
"""PROPOSAL 224 / VERDICT 237 (+13 offset) — Cayley's formula via the Prufer bijection.

HEAD: The number of labeled trees on the vertex set {1..n} is EXACTLY

    T(n) = n^(n-2)   (n >= 2; T(1) = T(2) = 1).

Proof by the Prufer bijection: labeled trees on {1..n} are in one-to-one
correspondence with sequences in {1..n}^(n-2). The encode repeatedly removes the
smallest-labeled leaf and records its unique neighbor (length n-2); the decode is
the standard degree-count reconstruction. Since |{1..n}^(n-2)| = n^(n-2) and the
map is a bijection, T(n) = n^(n-2) exactly.

Monte-Carlo (uniform-tree) reading: a uniformly random labeled tree is a
uniformly random Prufer sequence in {1..n}^(n-2). Hence the appearance count of a
fixed vertex v is Binomial(n-2, 1/n) and degree(v) = appearances + 1, giving the
EXACT facts
    E[degree(v)] = (n-2)/n + 1 = 2(n-1)/n,
    P(specific unordered edge {i,j} present) = 2/n   (E[#edges]=n-1 over C(n,2)),
    P(v is a leaf) = P(deg=1) = ((n-1)/n)^(n-2).

Gate battery (each direction stated):
  G1 EXACT identity (headline, EQUALITY): brute-force count labeled trees for
     n=2,3,4,5,6 by enumerating every size-(n-1) subset of the C(n,2) candidate
     edges and testing tree-ness (acyclic + connected via union-find); assert each
     count == n^(n-2) exactly (integers, no float).
  G2 EXACT bijection roundtrip (EQUALITY): enumerate all 125 labeled trees at n=5;
     encode each to a Prufer sequence and decode back; assert decoded edge-set ==
     original for every tree AND the 125 produced sequences are exactly all 5^3=125
     distinct sequences (perfect bijection, no collision).
  G3 EXACT probabilities via Fraction (EQUALITY): over the full n=5 enumeration,
     assert P(edge {1,2}) == Fraction(2,5), mean degree of vertex 1 == Fraction(8,5),
     leaf probability of vertex 1 == Fraction(64,125). No float.
  G4 MC agreement (AGREEMENT, |z| < Z_GATE=3 PASS): at n=12 draw N_MC uniform
     Prufer sequences, decode, measure empirical P(edge {1,2}) vs 2/12=1/6 and
     empirical E[deg(1)] vs 11/6; z via the appropriate Binomial variance; PASS iff
     both |z| < 3 (>=3 sigma agreement).
  G5 Robustness (AGREEMENT across a grid): the EXACT identity T(n)=n^(n-2) holds
     for n=2..8 (n<=6 vs brute enumeration; n=7,8 vs Prufer roundtrip-consistency,
     every one of the n^(n-2) sequences decodes to a valid tree that re-encodes to
     itself, so the code is a bijection onto n^(n-2) distinct trees); AND edge-prob
     2/n confirmed by MC at n in {6,10,20}, each |z| < 3.
  G6 FALSIFIABILITY (REJECTION; rejection at large z / exact mismatch = PASS):
     (a) the enumerated counts for n=4,5,6 do NOT equal the plausible-wrong formulas
     n^(n-1), (n-1)!, or 2^(n-1) (exact strict inequality) — only n^(n-2) matches;
     (b) a naive "each edge present independently w.p. 1/2" predicts P(edge)=1/2,
     REJECTED by the n=12 MC at |z| >> 6; the naive P(edge)=1/n is REJECTED at large
     z too. The gate PASSES BECAUSE the wrong values are rejected (opposite polarity
     to G3/G4/G5).

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. build_results() is a
pure function of SEED and the fixed parameters; the results dict embeds no digest
of itself. main() runs it twice, asserts the canonical JSON forms are byte-
identical, then prints results_sha256 over the compact-canonical form. A separate
re-invocation must reproduce the identical 64-hex digest. Nothing is written to
disk. All EXACT work (G1/G2/G3 and the G6 formula rejections) uses integers and
fractions.Fraction; the ONE random.Random(SEED) is drawn sequentially across the
Monte-Carlo gates (G4 n=12, then G5 MC n=6, n=10, n=20) so the stream order is
fixed and deterministic; G6's MC leg reuses the G4 n=12 empirical estimate.
"""

import hashlib
import json
import math
import random
import sys
from fractions import Fraction
from itertools import combinations, product

SEED = 20260717
Z_GATE = 3.0
N_MC = 200_000
GRID = [2, 3, 4, 5, 6, 7, 8]


def r6(x):
    return round(float(x), 6)


def frac_str(f):
    return f"{f.numerator}/{f.denominator}"


# ---------------------------------------------------------------------------
# Tree enumeration + tree-ness test (union-find)
# ---------------------------------------------------------------------------
def is_tree(n, edge_subset):
    """True iff the n-1 distinct edges form a spanning tree on {1..n}
    (acyclic via union-find; n-1 acyclic edges are automatically connected)."""
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    comps = n
    for (u, v) in edge_subset:
        ru, rv = find(u), find(v)
        if ru == rv:
            return False
        parent[ru] = rv
        comps -= 1
    return comps == 1


def brute_count_trees(n):
    """Count labeled trees on {1..n} by enumerating size-(n-1) edge subsets."""
    all_edges = list(combinations(range(1, n + 1), 2))
    count = 0
    for subset in combinations(all_edges, n - 1):
        if is_tree(n, subset):
            count += 1
    return count


def enumerate_trees(n):
    """All labeled trees on {1..n} as frozenset-of-frozenset edge-sets."""
    all_edges = list(combinations(range(1, n + 1), 2))
    trees = []
    for subset in combinations(all_edges, n - 1):
        if is_tree(n, subset):
            trees.append(frozenset(frozenset(e) for e in subset))
    return trees


# ---------------------------------------------------------------------------
# Prufer bijection
# ---------------------------------------------------------------------------
def prufer_encode(n, edge_set):
    """Encode a labeled tree (set/frozenset of frozenset({u,v})) to its length
    n-2 Prufer sequence: repeatedly remove the smallest-labeled leaf, record its
    unique neighbor."""
    import heapq

    adj = {i: set() for i in range(1, n + 1)}
    for e in edge_set:
        u, v = tuple(e)
        adj[u].add(v)
        adj[v].add(u)
    degree = {i: len(adj[i]) for i in range(1, n + 1)}
    leaves = [i for i in range(1, n + 1) if degree[i] == 1]
    heapq.heapify(leaves)
    seq = []
    for _ in range(n - 2):
        leaf = heapq.heappop(leaves)
        neighbor = next(iter(adj[leaf]))
        seq.append(neighbor)
        adj[neighbor].discard(leaf)
        adj[leaf].discard(neighbor)
        degree[neighbor] -= 1
        if degree[neighbor] == 1:
            heapq.heappush(leaves, neighbor)
    return tuple(seq)


def prufer_decode(n, seq):
    """Standard degree-count reconstruction: return the tree as a set of
    frozenset({u,v}) edges from a length n-2 Prufer sequence."""
    import heapq

    degree = {i: 1 for i in range(1, n + 1)}
    for x in seq:
        degree[x] += 1
    leaves = [i for i in range(1, n + 1) if degree[i] == 1]
    heapq.heapify(leaves)
    edges = set()
    for x in seq:
        leaf = heapq.heappop(leaves)
        edges.add(frozenset((leaf, x)))
        degree[leaf] -= 1
        degree[x] -= 1
        if degree[x] == 1:
            heapq.heappush(leaves, x)
    remaining = [i for i in range(1, n + 1) if degree[i] == 1]
    edges.add(frozenset((remaining[0], remaining[1])))
    return edges


# ---------------------------------------------------------------------------
# Monte-Carlo helpers (uniform Prufer sequence == uniform labeled tree)
# ---------------------------------------------------------------------------
EDGE_12 = frozenset((1, 2))


def mc_edge_and_degree(n, N, rng):
    """Draw N uniform Prufer sequences at size n, decode each, and measure the
    empirical P(edge {1,2}) and E[deg(1)] from the decoded trees."""
    edge_count = 0
    deg_sum = 0
    for _ in range(N):
        seq = [rng.randint(1, n) for _ in range(n - 2)]
        edges = prufer_decode(n, seq)
        if EDGE_12 in edges:
            edge_count += 1
        deg_sum += sum(1 for e in edges if 1 in e)
    p_edge_emp = edge_count / N
    mean_deg = deg_sum / N
    return edge_count, p_edge_emp, mean_deg


def mc_edge_prob(n, N, rng):
    """Draw N uniform Prufer sequences at size n, decode, measure empirical
    P(edge {1,2}) and its z against the exact null 2/n."""
    edge_count = 0
    for _ in range(N):
        seq = [rng.randint(1, n) for _ in range(n - 2)]
        edges = prufer_decode(n, seq)
        if EDGE_12 in edges:
            edge_count += 1
    p_emp = edge_count / N
    p = 2.0 / n
    se = math.sqrt(p * (1.0 - p) / N)
    z = (p_emp - p) / se
    return p_emp, z


# ---------------------------------------------------------------------------
# build_results
# ---------------------------------------------------------------------------
def build_results():
    rng = random.Random(SEED)

    # brute counts reused across G1, G5, G6 (computed once)
    brute_counts = {n: brute_count_trees(n) for n in [2, 3, 4, 5, 6]}

    results = {
        "proposal": 224,
        "verdict": 237,
        "slot": "Cayley's formula / Prufer bijection (P224 -> V237, +13 offset)",
        "seed": SEED,
        "z_gate": Z_GATE,
        "n_mc": N_MC,
        "grid": list(GRID),
    }

    # --- G1 EXACT identity: brute count == n^(n-2) for n=2..6 -----------------
    g1_per_n = {}
    g1_pass = True
    for n in [2, 3, 4, 5, 6]:
        cnt = brute_counts[n]
        expected = n ** (n - 2)
        ok = (cnt == expected)
        g1_per_n[str(n)] = {
            "brute_count": cnt,
            "n_pow_n_minus_2": expected,
            "match": ok,
        }
        g1_pass = g1_pass and ok
    results["G1_exact_cayley_identity"] = {
        "n_values": [2, 3, 4, 5, 6],
        "per_n": g1_per_n,
        "pass": g1_pass,
    }

    # --- G2 EXACT bijection roundtrip at n=5 ----------------------------------
    trees5 = enumerate_trees(5)
    seqs_seen = set()
    roundtrip_ok = True
    for tree in trees5:
        seq = prufer_encode(5, tree)
        decoded = prufer_decode(5, seq)
        if frozenset(decoded) != tree:
            roundtrip_ok = False
        seqs_seen.add(seq)
    all_sequences = set(product(range(1, 6), repeat=3))
    covers_all = (seqs_seen == all_sequences)
    g2_pass = (
        len(trees5) == 125
        and len(seqs_seen) == 125
        and roundtrip_ok
        and covers_all
    )
    results["G2_exact_bijection_roundtrip"] = {
        "n": 5,
        "num_trees": len(trees5),
        "num_distinct_prufer": len(seqs_seen),
        "expected": 125,
        "all_roundtrip_ok": roundtrip_ok,
        "prufer_covers_all_sequences": covers_all,
        "pass": g2_pass,
    }

    # --- G3 EXACT probabilities via Fraction over the n=5 enumeration ----------
    total = len(trees5)  # 125
    edge12_count = sum(1 for t in trees5 if EDGE_12 in t)
    deg1_sum = sum(sum(1 for e in t if 1 in e) for t in trees5)
    leaf1_count = sum(1 for t in trees5 if sum(1 for e in t if 1 in e) == 1)
    edge12_prob = Fraction(edge12_count, total)
    mean_deg1 = Fraction(deg1_sum, total)
    leaf1_prob = Fraction(leaf1_count, total)
    exp_edge = Fraction(2, 5)
    exp_deg = Fraction(8, 5)
    exp_leaf = Fraction(4 ** 3, 5 ** 3)
    g3_pass = (
        edge12_prob == exp_edge
        and mean_deg1 == exp_deg
        and leaf1_prob == exp_leaf
    )
    results["G3_exact_probabilities"] = {
        "n": 5,
        "edge_12_count": edge12_count,
        "edge_12_prob": frac_str(edge12_prob),
        "edge_12_expected": frac_str(exp_edge),
        "mean_degree_v1": frac_str(mean_deg1),
        "mean_degree_expected": frac_str(exp_deg),
        "leaf_prob_v1": frac_str(leaf1_prob),
        "leaf_prob_expected": frac_str(exp_leaf),
        "pass": g3_pass,
    }

    # --- G4 MC agreement at n=12: P(edge {1,2}) vs 1/6, E[deg(1)] vs 11/6 ------
    n4 = 12
    edge_count4, p_edge_emp4, mean_deg4 = mc_edge_and_degree(n4, N_MC, rng)
    p_edge_theory4 = 2.0 / n4                       # 1/6
    se_edge4 = math.sqrt(p_edge_theory4 * (1.0 - p_edge_theory4) / N_MC)
    z_edge4 = (p_edge_emp4 - p_edge_theory4) / se_edge4
    mean_deg_theory4 = 2.0 * (n4 - 1) / n4          # 11/6
    var_deg4 = (n4 - 2) * (1.0 / n4) * (1.0 - 1.0 / n4)  # Binomial(n-2,1/n) var
    se_deg4 = math.sqrt(var_deg4 / N_MC)
    z_deg4 = (mean_deg4 - mean_deg_theory4) / se_deg4
    g4_pass = abs(z_edge4) < Z_GATE and abs(z_deg4) < Z_GATE
    results["G4_mc_agreement"] = {
        "n": n4,
        "n_draws": N_MC,
        "p_edge_theory": r6(p_edge_theory4),
        "p_edge_empirical": r6(p_edge_emp4),
        "z_edge": r6(z_edge4),
        "mean_deg_theory": r6(mean_deg_theory4),
        "mean_deg_empirical": r6(mean_deg4),
        "z_deg": r6(z_deg4),
        "pass": g4_pass,
    }

    # --- G5 Robustness: identity across n=2..8 + edge-prob MC at n in {6,10,20}
    identity_grid = {}
    identity_all = True
    for n in GRID:
        expected = n ** (n - 2)
        if n <= 6:
            cnt = brute_counts[n]
            method = "brute"
            match = (cnt == expected)
        else:
            # Prufer roundtrip-consistency: every one of the n^(n-2) sequences
            # decodes to a valid tree that re-encodes to itself -> the code is a
            # bijection onto exactly n^(n-2) distinct labeled trees.
            cnt = 0
            match = True
            for seq in product(range(1, n + 1), repeat=n - 2):
                edges = prufer_decode(n, seq)
                if len(edges) != n - 1 or not is_tree(n, [tuple(e) for e in edges]):
                    match = False
                if prufer_encode(n, edges) != seq:
                    match = False
                cnt += 1
            match = match and (cnt == expected)
            method = "prufer-roundtrip"
        identity_grid[str(n)] = {
            "count": cnt,
            "expected": expected,
            "method": method,
            "match": match,
        }
        identity_all = identity_all and match

    mc_edge = {}
    mc_all = True
    for n in [6, 10, 20]:
        p_emp, z = mc_edge_prob(n, N_MC, rng)
        ok = abs(z) < Z_GATE
        mc_edge[str(n)] = {
            "p_theory": r6(2.0 / n),
            "p_empirical": r6(p_emp),
            "z": r6(z),
            "pass": ok,
        }
        mc_all = mc_all and ok

    g5_pass = identity_all and mc_all
    results["G5_robustness_grid"] = {
        "identity_grid": identity_grid,
        "identity_all_match": identity_all,
        "mc_edge_prob": mc_edge,
        "mc_all_pass": mc_all,
        "pass": g5_pass,
    }

    # --- G6 FALSIFIABILITY: wrong formulas + naive edge-prob REJECTED ----------
    import math as _math
    wrong_per_n = {}
    all_unique = True
    for n in [4, 5, 6]:
        cnt = brute_counts[n]
        n_pow_nm2 = n ** (n - 2)
        n_pow_nm1 = n ** (n - 1)
        fact_nm1 = _math.factorial(n - 1)
        two_pow_nm1 = 2 ** (n - 1)
        unique = (
            cnt == n_pow_nm2
            and cnt != n_pow_nm1
            and cnt != fact_nm1
            and cnt != two_pow_nm1
        )
        wrong_per_n[str(n)] = {
            "true_count": cnt,
            "n_pow_n_minus_2": n_pow_nm2,
            "n_pow_n_minus_1": n_pow_nm1,
            "factorial_n_minus_1": fact_nm1,
            "two_pow_n_minus_1": two_pow_nm1,
            "unique_match": unique,
        }
        all_unique = all_unique and unique

    # naive-edge rejection reuses the G4 n=12 empirical estimate
    null_half = 0.5
    se_half = math.sqrt(null_half * (1.0 - null_half) / N_MC)
    z_half = (p_edge_emp4 - null_half) / se_half
    null_1n = 1.0 / n4                               # 1/12
    se_1n = math.sqrt(null_1n * (1.0 - null_1n) / N_MC)
    z_1n = (p_edge_emp4 - null_1n) / se_1n
    half_rejected = abs(z_half) > 6.0
    onen_rejected = abs(z_1n) > 6.0

    g6_pass = all_unique and half_rejected and onen_rejected
    results["G6_falsifiability"] = {
        "polarity_note": "REJECT wrong alternatives: this gate PASSES because the wrong values are rejected (exact strict inequality / large |z|), opposite polarity to G3/G4/G5",
        "wrong_formula_rejection": {
            "n_values": [4, 5, 6],
            "per_n": wrong_per_n,
            "all_unique": all_unique,
        },
        "naive_edge_half_rejected": {
            "null_p": r6(null_half),
            "empirical_p": r6(p_edge_emp4),
            "z": r6(z_half),
            "rejected": half_rejected,
        },
        "naive_edge_one_over_n_rejected": {
            "null_p": r6(null_1n),
            "empirical_p": r6(p_edge_emp4),
            "z": r6(z_1n),
            "rejected": onen_rejected,
        },
        "pass": g6_pass,
    }

    gates = {
        "G1": results["G1_exact_cayley_identity"]["pass"],
        "G2": results["G2_exact_bijection_roundtrip"]["pass"],
        "G3": results["G3_exact_probabilities"]["pass"],
        "G4": results["G4_mc_agreement"]["pass"],
        "G5": results["G5_robustness_grid"]["pass"],
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
