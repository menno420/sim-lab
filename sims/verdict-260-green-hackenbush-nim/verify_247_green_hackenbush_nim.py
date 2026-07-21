#!/usr/bin/env python3
"""PROPOSAL 247 — Green Hackenbush IS Nim (the colon principle).

HEAD: In Green Hackenbush a rooted forest of "green" edges hangs from a single
ground vertex (id 0). A move removes any one edge; every edge no longer
connected to the ground is then deleted. Normal play: the player who cannot
move loses. The Sprague-Grundy value of a position is the mex over successor
values. The colon principle gives a closed form:

    sub(v, parent) = XOR over children c of v (c != parent) of ( 1 + sub(c, v) )
    sub(leaf)      = 0
    value(forest)  = XOR over ground(0)'s neighbours r of ( 1 + sub(r, 0) )

Consequence: a bamboo forest of stalk-lengths (a1,...,ak) has value
a1 XOR ... XOR ak -- Green Hackenbush IS Nim -- a first-player win iff the
nim-sum is non-zero. Sanity: a single path of n edges has value n; the "Y"
tree {0-1,1-2,1-3} has value 1.

The verifier implements the GAME as a memoized mex-DP outcome oracle (grundy)
that does NOT assume the theorem, and independently the CLOSED FORM
(colon_value). The two are compared; the game engine alone drives every
Monte-Carlo classification.

Gate battery (SEED=20260717; each gate its own direction, real teeth):
  G1 EXACT identity (integer/XOR only): over an EXHAUSTIVE enumeration of all
     rooted trees with <= 7 edges PLUS a random battery of larger trees and
     forests (up to 14 edges), colon_value(pos) == grundy(pos) for every
     position; mismatches must be 0.
  G2 MC AGREEMENT (|z| < 3): fix the finite model of k=3 bamboo forests each
     stalk length uniform in {1..8} (512 equally-likely forests). Solve ALL
     512 with the GROUND-TRUTH engine for the exact P-density p0 (Fraction);
     draw N=200000 iid forests, classify P/N via the same engine, estimate
     p_hat; binomial z must sit inside 3 sigma.
  G3 INVARIANCE / ROBUSTNESS (two clean sub-checks): (a) relabel/child-order
     invariance -- both grundy and colon_value survive a random vertex
     relabeling fixing 0; discrepancies 0. (b) optimal-play robustness -- the
     theory-optimal player (moves to a grundy-0 successor found via the engine)
     beats a random opponent in every game; optimal_play_losses 0.
  G4 FALSIFIABILITY (|z| > 5 each): on the SAME model, reject two plausible Nim
     mistakes (arithmetic instead of XOR) -- Foil A "sum parity" and Foil B
     "sum mod 3" -- against the engine's true P-density, far outside 5 sigma.

Determinism: build_results() is a pure function of SEED and fixed params (no
wall clock, no hostname, no unseeded randomness); random is reseeded at the
start of every sampling gate so results are position-independent. Every float
is rounded to 10 decimals before hashing. --selfcheck runs the whole
computation twice in one process and asserts byte-identical digests.
"""

import hashlib
import itertools
import json
import math
import random
import sys
from fractions import Fraction

SEED = 20260717
GROUND = 0

# ------------------------------ core engine ------------------------------

def norm_edge(u, v):
    return (u, v) if u < v else (v, u)


def ground_component(edges):
    """Edges (both endpoints) reachable from the ground vertex 0."""
    adj = {}
    for (a, b) in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    if GROUND not in adj:
        return frozenset()
    seen = {GROUND}
    stack = [GROUND]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return frozenset(e for e in edges if e[0] in seen and e[1] in seen)


_GRUNDY_MEMO = {}


def grundy(edges):
    """GROUND-TRUTH Sprague-Grundy value via memoized mex-DP over positions."""
    edges = edges if isinstance(edges, frozenset) else frozenset(edges)
    if not edges:
        return 0
    cached = _GRUNDY_MEMO.get(edges)
    if cached is not None:
        return cached
    vals = set()
    for e in edges:
        succ = ground_component(edges - {e})
        vals.add(grundy(succ))
    m = 0
    while m in vals:
        m += 1
    _GRUNDY_MEMO[edges] = m
    return m


def colon_value(edges):
    """CLOSED FORM value via the colon-principle sub()/XOR recursion."""
    adj = {}
    for (a, b) in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)

    def sub(v, parent):
        total = 0
        for c in adj.get(v, ()):
            if c != parent:
                total ^= (1 + sub(c, v))
        return total

    total = 0
    for r in adj.get(GROUND, ()):
        total ^= (1 + sub(r, GROUND))
    return total


# --------------------------- tree/forest builders ---------------------------

def random_tree(n_edges):
    """Grow a random rooted tree: attach each new vertex to a uniformly-random
    existing vertex (ground 0 is vertex 0)."""
    edges = set()
    for new in range(1, n_edges + 1):
        p = random.randint(0, new - 1)
        edges.add(norm_edge(p, new))
    return frozenset(edges)


def random_forest(n_components, comp_edges_max):
    """A forest hanging from ground: several random subtrees with distinct
    vertex ids, each rooted at a child of 0."""
    edges = set()
    base = 1
    for _ in range(n_components):
        ne = random.randint(1, comp_edges_max)
        local = {0: 0}
        nxt = base
        for new in range(1, ne + 1):
            p = random.randint(0, new - 1)
            gp = 0 if p == 0 else local[p]
            local[new] = nxt
            edges.add(norm_edge(gp, nxt))
            nxt += 1
        base = nxt
    return frozenset(edges)


def bamboo_forest(lengths):
    """k stalks (paths) of the given lengths, all hanging from ground 0, with
    distinct vertex ids per stalk."""
    edges = set()
    nxt = 1
    for L in lengths:
        prev = 0
        for _ in range(L):
            edges.add(norm_edge(prev, nxt))
            prev = nxt
            nxt += 1
    return frozenset(edges)


def random_bamboo_forest(k, maxlen):
    lengths = tuple(random.randint(1, maxlen) for _ in range(k))
    return bamboo_forest(lengths), lengths


def canon(edges):
    """AHU canonical form of a rooted tree (rooted at ground 0)."""
    adj = {}
    for (a, b) in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)

    def enc(v, parent):
        subs = sorted(enc(c, v) for c in adj.get(v, ()) if c != parent)
        return "(" + "".join(subs) + ")"

    return enc(GROUND, -1)


def enumerate_rooted_trees(max_edges):
    """All distinct rooted trees with up to max_edges edges (<= max_edges+1
    vertices), rooted at ground 0. Generate-by-parent-array, dedup by AHU."""
    seen = set()
    result = []
    for nv in range(1, max_edges + 2):  # vertices 0..nv-1
        ranges = [range(v) for v in range(1, nv)]  # parent of vertex v in 0..v-1
        for parents in itertools.product(*ranges):
            edges = frozenset(norm_edge(v, parents[v - 1]) for v in range(1, nv))
            c = canon(edges)
            if c not in seen:
                seen.add(c)
                result.append(edges)
    return result


# ------------------------------- helpers -------------------------------

def rnd(x):
    return round(float(x), 10)


_BAMBOO_GRUNDY = {}


def bamboo_grundy(lengths):
    """Engine grundy of a bamboo forest, cached by the exact lengths tuple."""
    cached = _BAMBOO_GRUNDY.get(lengths)
    if cached is not None:
        return cached
    g = grundy(bamboo_forest(lengths))
    _BAMBOO_GRUNDY[lengths] = g
    return g


# -------------------------------- gates --------------------------------

def gate_g1():
    random.seed(SEED)
    n_checked = 0
    mismatches = 0
    max_edges = 0

    # (a) exhaustive enumeration of all rooted trees with <= 7 edges
    exhaustive = enumerate_rooted_trees(7)
    for edges in exhaustive:
        cv = colon_value(edges)
        gv = grundy(edges)
        if cv != gv:
            mismatches += 1
        n_checked += 1
        if len(edges) > max_edges:
            max_edges = len(edges)
    n_exhaustive = len(exhaustive)

    # (b) random battery of larger trees and forests
    R_TREES = 300
    for _ in range(R_TREES):
        ne = random.randint(1, 14)
        edges = random_tree(ne)
        if colon_value(edges) != grundy(edges):
            mismatches += 1
        n_checked += 1
        max_edges = max(max_edges, len(edges))

    R_FORESTS = 150
    for _ in range(R_FORESTS):
        edges = random_forest(random.randint(2, 4), 5)
        if colon_value(edges) != grundy(edges):
            mismatches += 1
        n_checked += 1
        max_edges = max(max_edges, len(edges))

    R_BAMBOO = 150
    for _ in range(R_BAMBOO):
        edges, _lengths = random_bamboo_forest(random.randint(2, 5), 8)
        if colon_value(edges) != grundy(edges):
            mismatches += 1
        n_checked += 1
        max_edges = max(max_edges, len(edges))

    return {
        "n_positions_checked": n_checked,
        "n_exhaustive_trees": n_exhaustive,
        "mismatches": mismatches,
        "max_edges_reached": max_edges,
        "pass": mismatches == 0,
    }


# k=3 bamboo model, stalk length uniform in {1..8}
G2_K = 3
G2_MAXLEN = 8
G2_N = 200_000


def _exact_p0():
    """Exact P-density over the 512 forests using the GROUND-TRUTH engine."""
    count = 0
    total = 0
    for combo in itertools.product(range(1, G2_MAXLEN + 1), repeat=G2_K):
        total += 1
        if bamboo_grundy(combo) == 0:
            count += 1
    return count, total


def gate_g2():
    random.seed(SEED)
    p0_count, total = _exact_p0()
    p0 = Fraction(p0_count, total)

    hits = 0
    for _ in range(G2_N):
        combo = tuple(random.randint(1, G2_MAXLEN) for _ in range(G2_K))
        if bamboo_grundy(combo) == 0:
            hits += 1
    p_hat = hits / G2_N

    p0f = float(p0)
    z = (p_hat - p0f) / math.sqrt(p0f * (1.0 - p0f) / G2_N)

    return {
        "model": {"k": G2_K, "maxlen": G2_MAXLEN, "n_forests": total},
        "p0_frac": f"{p0.numerator}/{p0.denominator}",
        "p0_float": rnd(p0f),
        "p0_count": p0_count,
        "N": G2_N,
        "hits": hits,
        "p_hat": rnd(p_hat),
        "z": rnd(z),
        "pass": abs(z) < 3.0,
    }


def relabel(edges, perm):
    return frozenset(norm_edge(perm[a], perm[b]) for (a, b) in edges)


def _winning_move(cur):
    """Return a grundy-0 successor if one exists (theory guarantees it when the
    position value is non-zero), else None. Found purely via the game engine."""
    for e in sorted(cur):
        s = ground_component(cur - {e})
        if grundy(s) == 0:
            return s
    return None


def _play_game(edges, optimal_is_first):
    """Play a full game; 'optimal' moves to a grundy-0 successor when possible,
    'random' moves uniformly. Return True iff the optimal player wins."""
    cur = edges
    turn_optimal = optimal_is_first
    while True:
        if not cur:
            # player to move cannot move -> loses
            return not turn_optimal  # optimal wins iff it is NOT the one stuck
        if turn_optimal:
            nxt = _winning_move(cur)
            if nxt is None:
                elist = sorted(cur)
                nxt = ground_component(cur - {elist[0]})
            cur = nxt
        else:
            elist = sorted(cur)
            e = elist[random.randrange(len(elist))]
            cur = ground_component(cur - {e})
        turn_optimal = not turn_optimal


def gate_g3():
    # (a) relabel / child-order invariance
    random.seed(SEED)
    relabel_discrepancies = 0
    n_relabel = 200
    for _ in range(n_relabel):
        ne = random.randint(1, 12)
        edges = random_tree(ne)
        g0 = grundy(edges)
        c0 = colon_value(edges)
        verts = sorted({x for e in edges for x in e} - {GROUND})
        shuffled = verts[:]
        random.shuffle(shuffled)
        perm = {GROUND: GROUND}
        for a, b in zip(verts, shuffled):
            perm[a] = b
        r_edges = relabel(edges, perm)
        if grundy(r_edges) != g0 or colon_value(r_edges) != c0:
            relabel_discrepancies += 1

    # (b) optimal-play robustness
    random.seed(SEED + 1)
    games_played = 0
    optimal_play_losses = 0
    n_positions = 120
    games_per_pos = 3
    for _ in range(n_positions):
        ne = random.randint(1, 10)
        edges = random_tree(ne)
        val = grundy(edges)
        # optimal is first when position is winning (val != 0), else second
        optimal_first = (val != 0)
        for _g in range(games_per_pos):
            won = _play_game(edges, optimal_first)
            games_played += 1
            if not won:
                optimal_play_losses += 1

    return {
        "relabel_discrepancies": relabel_discrepancies,
        "n_relabel_trees": n_relabel,
        "games_played": games_played,
        "optimal_play_losses": optimal_play_losses,
        "pass": relabel_discrepancies == 0 and optimal_play_losses == 0,
    }


def gate_g4(p_hat):
    """Reject naive foils against the engine's true P-density p_hat (from G2)."""
    total = 0
    even_sum = 0
    mod3_sum = 0
    for combo in itertools.product(range(1, G2_MAXLEN + 1), repeat=G2_K):
        total += 1
        s = sum(combo)
        if s % 2 == 0:
            even_sum += 1
        if s % 3 == 0:
            mod3_sum += 1
    q_A = Fraction(even_sum, total)   # Foil A: P iff sum even
    q_B = Fraction(mod3_sum, total)   # Foil B: P iff sum % 3 == 0

    def zf(q):
        qf = float(q)
        return (p_hat - qf) / math.sqrt(qf * (1.0 - qf) / G2_N)

    z_A = zf(q_A)
    z_B = zf(q_B)

    # true-vs-exact agreement (should equal G2's small z)
    p0_count, tot = _exact_p0()
    p0 = float(Fraction(p0_count, tot))
    z_true = (p_hat - p0) / math.sqrt(p0 * (1.0 - p0) / G2_N)

    return {
        "q_A_frac": f"{q_A.numerator}/{q_A.denominator}",
        "q_B_frac": f"{q_B.numerator}/{q_B.denominator}",
        "q_A": rnd(float(q_A)),
        "q_B": rnd(float(q_B)),
        "z_A": rnd(z_A),
        "z_B": rnd(z_B),
        "z_true_agreement": rnd(z_true),
        "pass": abs(z_A) > 5.0 and abs(z_B) > 5.0,
    }


# ------------------------------- anchors -------------------------------

def anchors():
    out = {}

    # bamboo (3,5,7)
    b = bamboo_forest((3, 5, 7))
    bg, bc = grundy(b), colon_value(b)
    assert bg == bc == (3 ^ 5 ^ 7) == 1, (bg, bc)
    out["bamboo_3_5_7"] = {"grundy": bg, "colon": bc, "xor": 3 ^ 5 ^ 7}

    # Y tree {(0,1),(1,2),(1,3)}
    y = frozenset([(0, 1), (1, 2), (1, 3)])
    yg, yc = grundy(y), colon_value(y)
    assert yg == yc == 1, (yg, yc)
    out["y_tree"] = {"grundy": yg, "colon": yc}

    # a larger explicit tree: path 0-1-2-3 with branches 1-4,4-5 and 2-6
    big = frozenset([(0, 1), (1, 2), (2, 3), (1, 4), (4, 5), (2, 6)])
    gg, gc = grundy(big), colon_value(big)
    assert gg == gc, (gg, gc)
    out["explicit_tree"] = {
        "edges": sorted(list(e) for e in big),
        "grundy": gg,
        "colon": gc,
    }
    return out


# ---------------------------- orchestration ----------------------------

def build_results():
    g1 = gate_g1()
    g2 = gate_g2()
    g3 = gate_g3()
    # G4 uses the engine's true P-density estimate from G2
    g4 = gate_g4(float(g2["p_hat"]))
    anch = anchors()

    order = [("G1", g1), ("G2", g2), ("G3", g3), ("G4", g4)]
    all_pass = all(g["pass"] for _, g in order)
    first_failing = next((name for name, g in order if not g["pass"]), None)

    return {
        "proposal": 247,
        "claim": "Green Hackenbush == Nim (colon principle)",
        "SEED": SEED,
        "anchors": anch,
        "G1": g1,
        "G2": g2,
        "G3": g3,
        "G4": g4,
        "all_gates_pass": all_pass,
        "first_failing_gate": first_failing,
    }


def digest_of(results):
    blob = json.dumps(results, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()


def main(argv):
    if "--selfcheck" in argv:
        r1 = build_results()
        d1 = digest_of(r1)
        r2 = build_results()
        d2 = digest_of(r2)
        assert d1 == d2, f"SELFCHECK FAILED: {d1} != {d2}"
        print("SELFCHECK OK")
        print(f"results_sha256={d1}")
        return 0

    results = build_results()
    d = digest_of(results)

    for name in ("G1", "G2", "G3", "G4"):
        g = results[name]
        print(f"{name}: {'PASS' if g['pass'] else 'FAIL'}")
    print()
    a = results["anchors"]
    print("anchors:")
    print(f"  bamboo(3,5,7) grundy={a['bamboo_3_5_7']['grundy']} "
          f"colon={a['bamboo_3_5_7']['colon']} xor={a['bamboo_3_5_7']['xor']}")
    print(f"  Y-tree        grundy={a['y_tree']['grundy']} "
          f"colon={a['y_tree']['colon']}")
    print(f"  explicit tree grundy={a['explicit_tree']['grundy']} "
          f"colon={a['explicit_tree']['colon']}")
    print()
    print(f"all_gates_pass={results['all_gates_pass']} "
          f"first_failing_gate={results['first_failing_gate']}")
    print()
    print(json.dumps(results, indent=2, sort_keys=True))
    print()
    print(f"results_sha256={d}")
    return 0 if results["all_gates_pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
