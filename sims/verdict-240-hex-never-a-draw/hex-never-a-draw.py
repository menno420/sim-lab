#!/usr/bin/env python3
"""PROPOSAL 227 / VERDICT 240 (+13 offset) -- Hex is never a draw: exactly one
player connects, and under a uniform random fill P(first player wins) = 1/2 EXACTLY.

HEAD statement
--------------
On the n x n Hex rhombus, Red owns the top and bottom edges (connect row 0 to
row n-1) and Blue owns the left and right edges (connect column 0 to column n-1),
under the six-neighbour hex adjacency (r,c) ~ (r-1,c),(r+1,c),(r,c-1),(r,c+1),
(r-1,c+1),(r+1,c-1). The Hex theorem: for EVERY complete two-colouring of the
board exactly one player has a winning connection -- never both (Jordan-curve /
planarity) and never neither (Sperner / Brouwer). The transpose-and-colour-swap
map C -> (C transposed, colours swapped) is a measure-preserving bijection on the
2^(n^2) colourings carrying "Red connects" onto "Blue connects", so
  #{Red connects} = #{Blue connects} = 2^(n^2 - 1)   (EXACT integer identity),
and under a fair independent fill P(Red connects) = 1/2 EXACTLY.

Pre-registered gate battery (each in its own direction)
-------------------------------------------------------
G1  EQUALITY (exhaustive, exact): enumerate ALL 2^(n^2) colourings for
    n in {2,3,4}. Assert draws==0 and both_win==0 and
    red_wins==blue_wins==2^(n^2-1), and Fraction(red_wins, 2^(n^2))==Fraction(1,2).
G2  AGREEMENT |z|<3: Monte-Carlo fair fill on n=11, N_MC_MAIN samples; z of the
    red-win count vs N/2 must satisfy |z|<3, and draws==both==0 over all samples.
G3  INVARIANT + AGREEMENT: never-draw invariant draws==both==0 across sizes
    {5,7,9,11} x fill-probs {3/10,1/2,7/10}; complement symmetry
    P(red|p)+P(red|1-p) ~ 1 within |z|<3 at each size (p=3/10 vs 7/10).
G4  REJECTION |z|>6: on the SAME fair fills at n=7, the 4-neighbour square lattice
    DOES draw (square_draws>0) while hex draws==0; the naive hypothesis "hex draws
    at the square rate q" predicts N*q hex draws, observed 0 -> reject at |z|>6.

Determinism: single random.Random(SEED) consumed in the fixed order G2 -> G3 -> G4.
build_results() is a pure function of SEED + fixed constants; main() runs it twice
in-process (asserts byte-identical canonical form) and a separate re-invocation is
byte-identical. Digest = sha256 of the whole results dict (no self-field), stdout only.
"""
import sys
import json
import math
import hashlib
import random
from collections import deque
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0
Z_REJECT = 6.0
EXHAUSTIVE_SIZES = (2, 3, 4)
MC_SIZE = 11
N_MC_MAIN = 120_000
ROBUST_SIZES = (5, 7, 9, 11)
ROBUST_PROBS = (Fraction(3, 10), Fraction(1, 2), Fraction(7, 10))
N_MC_ROBUST = 15_000
FALS_SIZE = 7

HEX_DELTAS = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, -1))
SQ_DELTAS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def connects(board, n, color, axis, deltas):
    seen = [False] * (n * n)
    dq = deque()
    if axis == "row":
        for c in range(n):
            if board[c] == color:
                seen[c] = True
                dq.append(c)
    else:
        for r in range(n):
            idx = r * n
            if board[idx] == color:
                seen[idx] = True
                dq.append(idx)
    while dq:
        idx = dq.popleft()
        r, c = divmod(idx, n)
        if axis == "row" and r == n - 1:
            return True
        if axis == "col" and c == n - 1:
            return True
        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                nidx = nr * n + nc
                if not seen[nidx] and board[nidx] == color:
                    seen[nidx] = True
                    dq.append(nidx)
    return False


def classify(board, n, deltas):
    red = connects(board, n, 0, "row", deltas)
    blue = connects(board, n, 1, "col", deltas)
    return red, blue


def exhaustive(n):
    total = 1 << (n * n)
    red_w = blue_w = draws = both = 0
    for bits in range(total):
        board = [(bits >> k) & 1 for k in range(n * n)]
        red, blue = classify(board, n, HEX_DELTAS)
        if red and blue:
            both += 1
        elif red:
            red_w += 1
        elif blue:
            blue_w += 1
        else:
            draws += 1
    exact = (red_w == blue_w == total // 2 and draws == 0 and both == 0)
    return {
        "n": n, "colorings": total, "red_wins": red_w, "blue_wins": blue_w,
        "draws": draws, "both_win": both,
        "red_eq_half_exact": bool(exact),
        "P_red": str(Fraction(red_w, total)),
    }


def mc_phalf(rng, n, N):
    nn = n * n
    red_w = draws = both = 0
    for _ in range(N):
        board = [rng.getrandbits(1) for _ in range(nn)]
        red, blue = classify(board, n, HEX_DELTAS)
        if red:
            red_w += 1
        if red and blue:
            both += 1
        if (not red) and (not blue):
            draws += 1
    z = (red_w - N / 2.0) / math.sqrt(N / 4.0)
    return {"n": n, "samples": N, "red_wins": red_w, "draws": draws, "both": both,
            "p_hat": round(red_w / N, 6), "z": round(z, 6)}


def mc_biased(rng, n, p, N):
    nn = n * n
    red_w = draws = both = 0
    for _ in range(N):
        board = [0 if rng.random() < p else 1 for _ in range(nn)]
        red, blue = classify(board, n, HEX_DELTAS)
        if red:
            red_w += 1
        if red and blue:
            both += 1
        if (not red) and (not blue):
            draws += 1
    return {"samples": N, "red_wins": red_w, "draws": draws, "both": both,
            "red_rate": round(red_w / N, 6)}


def mc_square_vs_hex(rng, n, N):
    nn = n * n
    sq_draws = sq_both = hex_draws = hex_both = 0
    for _ in range(N):
        board = [rng.getrandbits(1) for _ in range(nn)]
        rh, bh = classify(board, n, HEX_DELTAS)
        rs, bs = classify(board, n, SQ_DELTAS)
        if (not rh) and (not bh):
            hex_draws += 1
        if rh and bh:
            hex_both += 1
        if (not rs) and (not bs):
            sq_draws += 1
        if rs and bs:
            sq_both += 1
    q = sq_draws / N
    if 0 < q < 1:
        z = (hex_draws - N * q) / math.sqrt(N * q * (1 - q))
    else:
        z = 0.0
    return {"n": n, "samples": N, "square_draws": sq_draws, "square_both": sq_both,
            "hex_draws": hex_draws, "hex_both": hex_both,
            "q_square_draw_rate": round(q, 6), "z_reject": round(z, 6)}


def build_results():
    r = {"proposal": 227, "verdict": 240, "slot": "round-54 GAME", "seed": SEED,
         "z_gate": Z_GATE, "z_reject": Z_REJECT,
         "n_mc_main": N_MC_MAIN, "n_mc_robust": N_MC_ROBUST}

    ex = [exhaustive(n) for n in EXHAUSTIVE_SIZES]
    g1_struct = all(e["red_eq_half_exact"] for e in ex)
    g1_frac = all(Fraction(e["red_wins"], e["colorings"]) == Fraction(1, 2) for e in ex)
    r["gate1_exhaustive_exact"] = {
        "direction": "EQUALITY", "sizes": list(EXHAUSTIVE_SIZES),
        "per_size": ex, "fraction_half_all": bool(g1_frac),
        "pass": bool(g1_struct and g1_frac)}

    rng = random.Random(SEED)

    g2 = mc_phalf(rng, MC_SIZE, N_MC_MAIN)
    g2_pass = (abs(g2["z"]) < Z_GATE) and g2["draws"] == 0 and g2["both"] == 0
    r["gate2_mc_half"] = {"direction": "AGREEMENT |z|<%.1f" % Z_GATE, **g2, "pass": bool(g2_pass)}

    ratebysize = {}
    robust = []
    for n in ROBUST_SIZES:
        ratebysize[n] = {}
        for p in ROBUST_PROBS:
            d = mc_biased(rng, n, float(p), N_MC_ROBUST)
            ratebysize[n][str(p)] = d
            robust.append({"n": n, "p": str(p), **d})
    draws_all_zero = all(x["draws"] == 0 and x["both"] == 0 for x in robust)
    sym = []
    for n in ROBUST_SIZES:
        a = ratebysize[n][str(Fraction(3, 10))]
        b = ratebysize[n][str(Fraction(7, 10))]
        s = a["red_rate"] + b["red_rate"]
        var = (a["red_rate"] * (1 - a["red_rate"]) / N_MC_ROBUST
               + b["red_rate"] * (1 - b["red_rate"]) / N_MC_ROBUST)
        z = (s - 1.0) / math.sqrt(var) if var > 0 else 0.0
        sym.append({"n": n, "sum": round(s, 6), "z": round(z, 6), "pass": bool(abs(z) < Z_GATE)})
    g3_pass = draws_all_zero and all(x["pass"] for x in sym)
    r["gate3_robustness"] = {
        "direction": "INVARIANT draws==0 + AGREEMENT symmetry |z|<%.1f" % Z_GATE,
        "draws_all_zero": bool(draws_all_zero), "per_cell": robust,
        "symmetry": sym, "pass": bool(g3_pass)}

    g4 = mc_square_vs_hex(rng, FALS_SIZE, N_MC_MAIN)
    g4_pass = (g4["hex_draws"] == 0) and (g4["square_draws"] > 0) and (abs(g4["z_reject"]) > Z_REJECT)
    r["gate4_falsifiability"] = {
        "direction": "REJECTION |z|>%.1f (naive: hex draws at square rate)" % Z_REJECT,
        **g4, "pass": bool(g4_pass)}

    gates = {"gate1": r["gate1_exhaustive_exact"]["pass"],
             "gate2": r["gate2_mc_half"]["pass"],
             "gate3": r["gate3_robustness"]["pass"],
             "gate4": r["gate4_falsifiability"]["pass"]}
    r["gates"] = gates
    r["first_failing_gate"] = next((k for k, v in gates.items() if not v), None)
    r["all_pass"] = bool(all(gates.values()))
    return r


def canonical(r):
    return json.dumps(r, sort_keys=True, separators=(",", ":"))


def main():
    r1 = build_results()
    r2 = build_results()
    c1 = canonical(r1)
    c2 = canonical(r2)
    if c1 != c2:
        sys.stderr.write("NON-DETERMINISTIC: in-process double-run diverged\n")
        sys.exit(3)
    print(json.dumps(r1, sort_keys=True, indent=2))
    print()
    for k in ("gate1", "gate2", "gate3", "gate4"):
        print("%s: %s" % (k, "PASS" if r1["gates"][k] else "FAIL"))
    print("all_pass: %s" % r1["all_pass"])
    print("results_sha256: %s" % hashlib.sha256(c1.encode()).hexdigest())
    sys.exit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
