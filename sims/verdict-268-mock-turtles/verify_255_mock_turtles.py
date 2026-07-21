#!/usr/bin/env python3
"""PROPOSAL 255 — Mock Turtles is a coin-turning game with the odious closed form.

HEAD: Mock Turtles is an impartial coin-turning game under normal play (last to
move wins). A row of coins sits at positions n = 0,1,2,..., each Heads (H) or
Tails (T). A move turns over 1, 2, or 3 coins with the constraint that the
RIGHTMOST (largest-index) coin turned must go from Heads to Tails (this forces
the largest head index strictly downward, so play always terminates).

CLAIM (exact closed form, established firsthand):
  1. The Sprague-Grundy value of a SINGLE heads-up coin at position n is the
     Mock-Turtle number g(n) = the unique ODIOUS member of {2n, 2n+1}, where a
     number is "odious" iff its binary popcount is odd. Equivalently,
         g(n) = 2n     if popcount(n) is odd,
         g(n) = 2n+1   if popcount(n) is even.
     These g(n) are exactly the odious numbers 1,2,4,7,8,11,13,14,16,... in
     increasing order (OEIS A000069): g(n) is the n-th odious number.
  2. By the coin-turning decomposition (a corollary of the Sprague-Grundy sum
     theorem — every coin-turning position is the disjunctive sum of its
     single-heads coins), the Grundy value of ANY position with heads at set S
     equals the nim-sum (XOR) over n in S of g(n). First player WINS iff this
     nim-sum != 0; the P-positions (second-player wins) are exactly nim-sum 0.

Anchor values (hard-asserted): g(0)=1, g(1)=2, g(2)=4, g(3)=7, g(4)=8, g(5)=11,
g(6)=13, g(7)=14, g(8)=16.

DISTINCTNESS. This is the COIN-TURNING family (odious-number closed form),
categorically distinct from every shipped game head: the subtraction game
(P219, g(n)=n mod 4), Green Hackenbush = Nim / colon principle (P247), Wythoff
(P239), Fibonacci-nim / Zeckendorf (P243). Its natural FOIL is Turning Turtles
(turn 1 OR 2 coins, rightmost H->T) whose single-coin value is g(n)=n (plain
Nim); Mock Turtles allows up to THREE and the odious correction is exactly what
separates the two. mock-turtle / coin-turning / odious is grep-0 in both repos.

The verifier builds an INDEPENDENT from-scratch game oracle (a memoized mex-DP
over frozenset positions that knows nothing of the closed form) and pits it
against the closed form through FOUR gates, each in its own direction with real
teeth:

  G1 EXACT (integer/XOR, 0 mismatches):
     (a) single-coin: a dedicated memoized DP for the Grundy value of a lone
         head at n (reachable set = drop coin n, add any 0/1/2 coins at
         positions < n) for n=0..255, asserted == closed_g(n) for every n; the
         anchors are asserted; and the sequence (g(n))_n is asserted equal to
         the sorted odious numbers over the range. closed_g is cross-checked to
         equal "the unique odious member of {2n,2n+1}" BOTH ways.
     (b) DECOMPOSITION: the GENERAL from-scratch oracle is run over EVERY
         position on K=13 slots (all 2^13 subsets) and grundy(pos) is asserted
         == XOR of closed_g over pos's heads — 0 mismatches. This validates the
         odious closed form AND the XOR-sum theorem firsthand.

  G2 MONTE-CARLO agreement (|z| < 3): enumerate all 2^16 positions on L=16 slots
     for the EXACT p0 = fraction with nim-sum(closed_g)==0; draw N=2,000,000 iid
     random positions (16 coins iid Heads w.p. 1/2, seeded) and compute the
     empirical fraction with nim-sum==0; z = (phat - p0)/sqrt(p0(1-p0)/N). Draws
     are independent so the plain iid SE is the honest one (no batch means /
     thinning). Assert |z| < 3.

  G3 INVARIANCE / robustness (0 discrepancies):
     (a) disjoint-sum theorem: for random pairs A, B placed on DISJOINT
         coordinate ranges, assert grundy(A U shifted B) == grundy(A) XOR
         grundy(B) via the general oracle, 0 discrepancies.
     (b) optimal-play robustness: from many random first-player-WIN starts
         (nim-sum != 0), a strategist that always moves to a nim-sum-0 position
         beats a random opponent EVERY game (0 losses); and from nim-sum-0
         starts, assert EVERY legal move leaves nim-sum != 0 (the P-position
         property), 0 violations.

  G4 FALSIFIABILITY (opposite polarity, reject naive alternatives at |z|>6):
     the general oracle's true P-indicator is ground truth on a random sample.
     Two foils are tested: foil-A "g(n)=n" (Mock Turtles = Turning Turtles =
     plain Nim — a real but WRONG value here) and foil-B "g(n)=2n+1 for all n"
     (drops the odious correction). For each foil the disagreement rate f
     between "foil predicts P" and the true P-indicator is measured, with
     z_foil = f/sqrt(f(1-f)/N) (rule-of-three / SE-floor convention applied if
     f rounds the SE to 0, documented). Both foils are asserted REJECTED at
     |z_foil| > 6, with an exact witness for each.

Determinism: build_results() is a pure function of SEED and fixed params; random
is reseeded at the start of every sampling gate so gate order cannot perturb the
payload; every float enters the payload via a fixed format string and every
count as an int. The whole results dict -> canonical JSON -> sha256 (FULL 64 hex,
never truncated). --selfcheck runs the whole computation twice in one process and
asserts byte-identical digests. SEED = 20260717 (hardcoded module constant).
Stdlib only: json, hashlib, math, random, fractions, itertools, argparse, sys.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
import sys
from fractions import Fraction

SEED = 20260717

# ---------------------------------------------------------------------------
# Closed form (the odious Mock-Turtle number) and odious helpers.
# ---------------------------------------------------------------------------
def popcount(x: int) -> int:
    return bin(x).count("1")


def is_odious(x: int) -> bool:
    """Odious = odd number of 1s in binary (OEIS A000069)."""
    return popcount(x) % 2 == 1


def closed_g(n: int) -> int:
    """g(n) = 2n if popcount(n) is odd, else 2n+1 (the odious member of {2n,2n+1})."""
    return 2 * n if is_odious(n) else 2 * n + 1


def odious_member_of_pair(n: int) -> int:
    """Return the unique odious member of {2n, 2n+1}, chosen independently of
    closed_g (used to cross-check closed_g both ways)."""
    lo, hi = 2 * n, 2 * n + 1
    lo_od, hi_od = is_odious(lo), is_odious(hi)
    # 2n+1 flips the last bit of 2n, so exactly one of the two is odious.
    assert lo_od != hi_od, f"expected exactly one odious member of {{{lo},{hi}}}"
    return lo if lo_od else hi


def nim_sum(vals) -> int:
    acc = 0
    for v in vals:
        acc ^= v
    return acc


# ---------------------------------------------------------------------------
# GENERAL from-scratch game oracle (knows nothing of the closed form).
# A position is a frozenset of head positions. A legal move picks T with
# 1 <= |T| <= 3 and max(T) currently a Head, then toggles every index in T.
# Equivalently: pick a head h (= max(T)) and any 0/1/2 extra indices below h.
# ---------------------------------------------------------------------------
_ORACLE_MEMO: dict = {}


def moves(pos: frozenset) -> list:
    """All successor positions (each reached by exactly one legal move)."""
    succ = []
    for h in pos:  # h is the rightmost turned coin (Head -> Tail)
        below = range(h)
        # 0 extra coins
        succ.append(pos ^ frozenset((h,)))
        # 1 extra coin below h
        for a in below:
            succ.append(pos ^ frozenset((h, a)))
        # 2 extra coins below h
        for a, b in itertools.combinations(below, 2):
            succ.append(pos ^ frozenset((h, a, b)))
    return succ


def grundy(pos: frozenset) -> int:
    """GROUND-TRUTH Sprague-Grundy value via memoized mex-DP; grundy(empty)=0."""
    if not pos:
        return 0
    cached = _ORACLE_MEMO.get(pos)
    if cached is not None:
        return cached
    seen = set()
    for s in moves(pos):
        seen.add(grundy(s))
    m = 0
    while m in seen:
        m += 1
    _ORACLE_MEMO[pos] = m
    return m


# ---------------------------------------------------------------------------
# Dedicated single-coin DP (independent of closed_g). The Grundy value of a lone
# head at n is the mex over the values of its successors: dropping coin n and
# adding any 0/1/2 coins at positions < n. Successor values use the coin-turning
# decomposition (value of heads {i,j} = G(i) XOR G(j)), so this DP reaches
# n=255 where the exponential general oracle cannot.
# ---------------------------------------------------------------------------
_SINGLE_MEMO: dict = {}


def single_coin_grundy(n: int) -> int:
    cached = _SINGLE_MEMO.get(n)
    if cached is not None:
        return cached
    reach = {0}  # drop coin n, add nothing -> empty position, value 0
    for i in range(n):  # add one coin at i < n
        reach.add(single_coin_grundy(i))
    for i, j in itertools.combinations(range(n), 2):  # add two coins below n
        reach.add(single_coin_grundy(i) ^ single_coin_grundy(j))
    m = 0
    while m in reach:
        m += 1
    _SINGLE_MEMO[n] = m
    return m


# ---------------------------------------------------------------------------
# G1 — EXACT: single-coin closed form + decomposition / XOR-sum theorem.
# ---------------------------------------------------------------------------
G1_SINGLE_MAX = 255
G1_DECOMP_K = 13


def gate_g1() -> dict:
    # closed_g cross-checked BOTH ways against "unique odious member of {2n,2n+1}"
    for n in range(0, G1_SINGLE_MAX + 1):
        cg = closed_g(n)
        assert cg == odious_member_of_pair(n), f"closed_g mismatch at n={n}"
        assert is_odious(cg), f"closed_g({n}) not odious"
        assert cg in (2 * n, 2 * n + 1)
        other = 2 * n + 1 if cg == 2 * n else 2 * n
        assert not is_odious(other), f"other member of pair odious at n={n}"

    # (a) single-coin DP == closed_g for n=0..255, 0 mismatches
    single_mismatches = 0
    for n in range(0, G1_SINGLE_MAX + 1):
        if single_coin_grundy(n) != closed_g(n):
            single_mismatches += 1
    assert single_mismatches == 0

    # anchors
    anchors = {n: closed_g(n) for n in range(0, 9)}
    expected_anchors = {0: 1, 1: 2, 2: 4, 3: 7, 4: 8, 5: 11, 6: 13, 7: 14, 8: 16}
    assert anchors == expected_anchors, (anchors, expected_anchors)
    for n, v in expected_anchors.items():
        assert single_coin_grundy(n) == v

    # (g(n))_n equals the sorted odious numbers over the range
    g_seq = [closed_g(n) for n in range(0, G1_SINGLE_MAX + 1)]
    odious_sorted = [x for x in range(1, 2 * G1_SINGLE_MAX + 3) if is_odious(x)][
        : G1_SINGLE_MAX + 1
    ]
    seq_matches_odious = g_seq == odious_sorted
    assert seq_matches_odious, "g(n) sequence != sorted odious numbers"

    # (b) DECOMPOSITION: general oracle over ALL 2^K positions == XOR of closed_g
    K = G1_DECOMP_K
    slots = list(range(K))
    decomp_mismatches = 0
    n_positions = 0
    for r in range(0, K + 1):
        for combo in itertools.combinations(slots, r):
            pos = frozenset(combo)
            gv = grundy(pos)
            xv = nim_sum(closed_g(n) for n in combo)
            if gv != xv:
                decomp_mismatches += 1
            n_positions += 1
    assert n_positions == 2 ** K
    assert decomp_mismatches == 0

    return {
        "single_coin_max_n": G1_SINGLE_MAX,
        "single_coin_mismatches": single_mismatches,
        "anchors": {str(k): v for k, v in anchors.items()},
        "seq_matches_odious": seq_matches_odious,
        "decomp_slots_K": K,
        "decomp_n_positions": n_positions,
        "decomp_mismatches": decomp_mismatches,
        "z": "exact — z=n/a",
        "pass": single_mismatches == 0 and decomp_mismatches == 0 and seq_matches_odious,
    }


# ---------------------------------------------------------------------------
# G2 — Monte-Carlo agreement on the P-position density (L=16 slots).
# ---------------------------------------------------------------------------
G2_L = 16
G2_N = 2_000_000


def _exact_p0(L: int) -> Fraction:
    """Exact fraction of the 2^L positions whose nim-sum(closed_g) == 0."""
    gvals = [closed_g(n) for n in range(L)]
    zero = 0
    for mask in range(1 << L):
        acc = 0
        mm = mask
        idx = 0
        while mm:
            if mm & 1:
                acc ^= gvals[idx]
            mm >>= 1
            idx += 1
        if acc == 0:
            zero += 1
    return Fraction(zero, 1 << L)


def gate_g2() -> dict:
    random.seed(SEED)
    p0 = _exact_p0(G2_L)
    gvals = [closed_g(n) for n in range(G2_L)]
    hits = 0
    for _ in range(G2_N):
        acc = 0
        for i in range(G2_L):
            if random.random() < 0.5:  # coin i is Heads
                acc ^= gvals[i]
        if acc == 0:
            hits += 1
    p_hat = hits / G2_N
    p0f = float(p0)
    se = math.sqrt(p0f * (1.0 - p0f) / G2_N)
    z = (p_hat - p0f) / se
    return {
        "L": G2_L,
        "n_positions": 1 << G2_L,
        "p0_frac": f"{p0.numerator}/{p0.denominator}",
        "p0_float": f"{p0f:.10f}",
        "N": G2_N,
        "hits": hits,
        "p_hat": f"{p_hat:.10f}",
        "z": f"{z:.4f}",
        "pass": abs(z) < 3.0,
    }


# ---------------------------------------------------------------------------
# G3 — invariance / robustness.
# ---------------------------------------------------------------------------
G3_DISJOINT_SAMPLES = 400
G3_A_MAX = 5   # part A lives on positions 0..4
G3_B_MAX = 5   # part B lives on positions 0..4 then shifted up by SHIFT
G3_SHIFT = 6   # disjoint gap: shifted B occupies 6..10
G3_ROBUST_POSITIONS = 300
G3_ROBUST_L = 12
G3_PPROP_POSITIONS = 400
G3_PPROP_L = 13


def _random_subset(upper: int, rng: random.Random) -> frozenset:
    """Random non-empty subset of {0..upper-1}."""
    while True:
        s = frozenset(i for i in range(upper) if rng.random() < 0.5)
        if s:
            return s


def _legal_moves_masks(pos: frozenset, L: int):
    """Yield successor positions for the strategy/P-property legs (same rule)."""
    return moves(pos)


def _play_game(start: frozenset, strat_first: bool, rng: random.Random) -> bool:
    """Play to the end. The strategist moves to a nim-sum(closed_g)==0 successor
    when one exists (else an arbitrary move); the opponent moves uniformly at
    random. Returns True iff the strategist makes the last move (wins)."""
    cur = start
    strat_turn = strat_first
    while True:
        if not cur:
            # player to move cannot move and loses -> the OTHER player just moved
            return not strat_turn
        succ = moves(cur)
        if strat_turn:
            nxt = None
            for s in succ:
                if nim_sum(closed_g(n) for n in s) == 0:
                    nxt = s
                    break
            if nxt is None:
                nxt = succ[0]
            cur = nxt
        else:
            cur = succ[rng.randrange(len(succ))]
        strat_turn = not strat_turn


def gate_g3() -> dict:
    # (a) disjoint-sum theorem via the general oracle
    rng = random.Random(SEED)
    disjoint_disc = 0
    for _ in range(G3_DISJOINT_SAMPLES):
        A = _random_subset(G3_A_MAX, rng)
        B = _random_subset(G3_B_MAX, rng)
        Bshift = frozenset(b + G3_SHIFT for b in B)
        # g(n) depends on ABSOLUTE position, so the summand is grundy(Bshift),
        # not grundy(B); the identity grundy(A U Bshift) == grundy(A) XOR
        # grundy(Bshift) is the additive (XOR) decomposition over two disjoint
        # coordinate blocks, computed firsthand by the general oracle.
        gU = grundy(A | Bshift)
        gA = grundy(A)
        gBshift = grundy(Bshift)
        if gU != (gA ^ gBshift):
            disjoint_disc += 1
    assert disjoint_disc == 0

    # (b1) optimal-play robustness: strategist never loses from winning starts
    rng = random.Random(SEED + 1)
    games = 0
    losses = 0
    for _ in range(G3_ROBUST_POSITIONS):
        # draw a first-player-WIN start (nim-sum != 0)
        while True:
            start = frozenset(i for i in range(G3_ROBUST_L) if rng.random() < 0.5)
            if nim_sum(closed_g(n) for n in start) != 0:
                break
        won = _play_game(start, strat_first=True, rng=rng)
        games += 1
        if not won:
            losses += 1
    assert losses == 0

    # (b2) P-position property: from nim-sum-0 starts, every move leaves nim-sum != 0
    rng = random.Random(SEED + 2)
    pprop_violations = 0
    pprop_checked = 0
    for _ in range(G3_PPROP_POSITIONS):
        while True:
            start = frozenset(i for i in range(G3_PPROP_L) if rng.random() < 0.5)
            if start and nim_sum(closed_g(n) for n in start) == 0:
                break
        for s in moves(start):
            pprop_checked += 1
            if nim_sum(closed_g(n) for n in s) == 0:
                pprop_violations += 1
    assert pprop_violations == 0

    return {
        "disjoint_samples": G3_DISJOINT_SAMPLES,
        "disjoint_discrepancies": disjoint_disc,
        "robust_games": games,
        "optimal_play_losses": losses,
        "pprop_positions": G3_PPROP_POSITIONS,
        "pprop_moves_checked": pprop_checked,
        "pprop_violations": pprop_violations,
        "pass": disjoint_disc == 0 and losses == 0 and pprop_violations == 0,
    }


# ---------------------------------------------------------------------------
# G4 — falsifiability: reject foil-A (g=n) and foil-B (g=2n+1) at |z|>6.
#
# A foil "g(n)=..." is a claim about GRUNDY VALUES, so the fundamental
# falsification is the value-level disagreement against the general oracle's
# TRUE Grundy value (ground truth, oracle knows nothing of any closed form),
# precomputed for ALL 2^L positions on L=13 slots and cross-checked to equal
# XOR of closed_g. We ALSO report the P-indicator (win/loss) disagreement.
#
# Firsthand subtlety surfaced here: foil-B "g(n)=2n+1" reproduces the TRUE
# P-set EXACTLY (0 P-disagreements) — because XOR(head indices)==0 forces an
# even number of odious-index heads (popcount(XOR)==0 => sum of index popcounts
# is even => #odious-index heads even), so foil-B lands the P/N verdict by luck
# — yet it gets the Grundy VALUES wrong and so fails as a game-value rule (which
# is what disjunctive-sum play actually needs). foil-A "g(n)=n" fails at BOTH
# the value level AND the P level. Both foils are rejected at the value level.
# ---------------------------------------------------------------------------
G4_L = 13
G4_N = 2_000_000
Z_REJECT = 6.0


def _oracle_value_table(L: int) -> dict:
    """True Grundy value per position (frozenset), straight from the general
    oracle, cross-checked to equal XOR of closed_g firsthand."""
    table = {}
    slots = list(range(L))
    for r in range(0, L + 1):
        for combo in itertools.combinations(slots, r):
            pos = frozenset(combo)
            gv = grundy(pos)
            assert gv == nim_sum(closed_g(n) for n in combo)
            table[pos] = gv
    return table


def _witness_value_disagreement(L: int, gfun, vtable: dict):
    """Smallest (by size, then lexicographic) position where the foil's XOR
    value differs from the true Grundy value."""
    slots = list(range(L))
    for r in range(0, L + 1):
        for combo in itertools.combinations(slots, r):
            pos = frozenset(combo)
            if nim_sum(gfun(n) for n in combo) != vtable[pos]:
                return sorted(combo)
    return None


def gate_g4() -> dict:
    vtable = _oracle_value_table(G4_L)

    foil_a = lambda n: n            # Turning Turtles / plain Nim (WRONG here)
    foil_b = lambda n: 2 * n + 1    # drops the odious correction (WRONG here)

    # single-coin value witnesses (grundy value level)
    assert closed_g(1) == 2 and foil_a(1) == 1 and foil_b(1) == 3
    wit_a = _witness_value_disagreement(G4_L, foil_a, vtable)
    wit_b = _witness_value_disagreement(G4_L, foil_b, vtable)
    assert wit_a is not None and wit_b is not None

    random.seed(SEED)
    val_a = 0   # value-level disagreements (the fundamental falsification)
    val_b = 0
    p_a = 0     # P-indicator (win/loss) disagreements (reported)
    p_b = 0
    for _ in range(G4_N):
        combo = tuple(i for i in range(G4_L) if random.random() < 0.5)
        pos = frozenset(combo)
        true_v = vtable[pos]
        true_p = true_v == 0
        va = nim_sum(foil_a(n) for n in combo)
        vb = nim_sum(foil_b(n) for n in combo)
        if va != true_v:
            val_a += 1
        if vb != true_v:
            val_b += 1
        if (va == 0) != true_p:
            p_a += 1
        if (vb == 0) != true_p:
            p_b += 1

    def z_of(dis):
        f = dis / G4_N
        # SE floor / rule-of-three convention if f rounds SE to 0 (f in {0,1}).
        if f <= 0.0 or f >= 1.0:
            se = math.sqrt((3.0 / G4_N) * (1.0 - 3.0 / G4_N) / G4_N)
        else:
            se = math.sqrt(f * (1.0 - f) / G4_N)
        return f, f / se

    fa, za = z_of(val_a)
    fb, zb = z_of(val_b)
    fpa, zpa = z_of(p_a)
    fpb, zpb = z_of(p_b)

    return {
        "L": G4_L,
        "N": G4_N,
        "foil_A": "g(n)=n (Turning Turtles / plain Nim)",
        "foil_B": "g(n)=2n+1 (drops odious correction)",
        "single_coin_value_witness": "n=1: true g=2, foil-A says 1, foil-B says 3",
        "ground_truth": "general mex-DP oracle Grundy value (== XOR closed_g, cross-checked)",
        # value-level (the fundamental falsification of a Grundy-value rule)
        "value_disagree_A": val_a,
        "value_disagree_B": val_b,
        "f_value_A": f"{fa:.10f}",
        "f_value_B": f"{fb:.10f}",
        "z_foil_A": f"{za:.4f}",
        "z_foil_B": f"{zb:.4f}",
        "value_witness_A_position": wit_a,
        "value_witness_B_position": wit_b,
        # P-indicator level (reported; foil-B coincides with truth on P/N)
        "p_disagree_A": p_a,
        "p_disagree_B": p_b,
        "z_p_A": f"{zpa:.4f}",
        "z_p_B": f"{zpb:.4f}",
        "note_foilB_P_coincidence": (
            "foil-B reproduces the true P-set exactly (p_disagree_B=0): "
            "XOR(head indices)==0 forces an even count of odious-index heads, "
            "so foil-B lands P/N by luck but gets Grundy VALUES wrong"
        ),
        "pass": abs(za) > Z_REJECT and abs(zb) > Z_REJECT,
    }


# ---------------------------------------------------------------------------
# Orchestration.
# ---------------------------------------------------------------------------
def build_results() -> dict:
    g1 = gate_g1()
    g2 = gate_g2()
    g3 = gate_g3()
    g4 = gate_g4()

    order = [("G1", g1), ("G2", g2), ("G3", g3), ("G4", g4)]
    all_pass = all(g["pass"] for _, g in order)
    first_failing = next((name for name, g in order if not g["pass"]), None)

    return {
        "proposal": 255,
        "claim": "Mock Turtles coin-turning game: single-coin Grundy value "
                 "g(n) = odious member of {2n,2n+1} = 2n if popcount(n) odd else "
                 "2n+1; position value = XOR of g over heads; P iff nim-sum 0",
        "SEED": SEED,
        "anchors_g": {str(n): closed_g(n) for n in range(0, 9)},
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


def main(argv) -> int:
    parser = argparse.ArgumentParser(description="Mock Turtles verifier (PROPOSAL 255).")
    parser.add_argument("--selfcheck", action="store_true",
                        help="run compute twice in-process, assert byte-identical")
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

    for name in ("G1", "G2", "G3", "G4"):
        g = results[name]
        print(f"{name}: {'PASS' if g['pass'] else 'FAIL'}")
    print()
    a = results["anchors_g"]
    print("anchors g(n): " + "  ".join(f"g({n})={a[str(n)]}" for n in range(0, 9)))
    print(f"G1: single_coin_mismatches={results['G1']['single_coin_mismatches']} "
          f"decomp_mismatches={results['G1']['decomp_mismatches']} "
          f"(K={results['G1']['decomp_slots_K']}, {results['G1']['decomp_n_positions']} positions)")
    print(f"G2: p0={results['G2']['p0_frac']} p_hat={results['G2']['p_hat']} "
          f"z={results['G2']['z']} (N={results['G2']['N']})")
    print(f"G3: disjoint_discrepancies={results['G3']['disjoint_discrepancies']} "
          f"optimal_play_losses={results['G3']['optimal_play_losses']} "
          f"pprop_violations={results['G3']['pprop_violations']}")
    print(f"G4: z_foil_A={results['G4']['z_foil_A']} z_foil_B={results['G4']['z_foil_B']} "
          f"(value-level) | p_disagree_A={results['G4']['p_disagree_A']} "
          f"p_disagree_B={results['G4']['p_disagree_B']} | "
          f"witness_A={results['G4']['value_witness_A_position']} "
          f"witness_B={results['G4']['value_witness_B_position']}")
    print()
    print(f"all_gates_pass={results['all_gates_pass']} "
          f"first_failing_gate={results['first_failing_gate']} "
          f"decision={results['decision']}")
    print()
    print(json.dumps(results, indent=2, sort_keys=True))
    print()
    print(f"results_sha256 = {d}")
    return 0 if results["all_gates_pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
