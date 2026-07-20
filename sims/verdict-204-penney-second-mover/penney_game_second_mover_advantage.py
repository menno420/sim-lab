#!/usr/bin/env python3
"""penney_game_second_mover_advantage.py — reference simulation for PROPOSAL 191.

Penney's game: two players each commit to a length-L binary (H=1 / T=0) pattern;
a fair coin is flipped repeatedly until one player's pattern appears as a run of
consecutive flips; that player wins. Claim: committing FIRST is a losing move.
For EVERY length-3 pattern the first player can pick, the second player has a
reply (the standard rule: complement of P1's 2nd symbol, then P1's first L-1
symbols) that wins strictly more than half the time. The game is non-transitive:
there is no best sequence; the advantage belongs to whoever chooses second.

Two independent computations agree:
  * exact_p2_winrate: exact absorption probability of an absorbing Markov chain
    over the last (L-1) flips, solved by stdlib Gaussian elimination. This is the
    EXACTLY-TRUE value (e.g. 2/3, 3/4, 7/8 for length 3).
  * mc_p2_winrate: a seeded Monte-Carlo coin-flip simulation — the reproducible
    dry-sim that confirms the exact value.

Gates (all_pass iff G1 AND G2 AND G3 AND G4, in order):
  G1 headline (>=3 sigma) : across all 2^L first-picks, the MINIMUM z of
                            (MC second-player winrate - 0.5) >= Z_GATE.
  G2 sign+magnitude       : EVERY first-pick favors player 2 (favor_frac >=
                            SIGN_FRAC) AND the minimum edge >= MIN_EDGE.
  G3 robust (shift L=4)   : repeat at L=4 under SEED+1; min z >= Z_GATE and every
                            first-pick still favors player 2 (same sign as base).
  G4 exactly-true         : for every first-pick, |MC winrate - exact Markov
                            winrate| <= EXACT_TOL (the surprising odds are exact).
"""
import random, math, json, hashlib

SEED = 20260717
BASE_L = 3
SHIFT_L = 4
TRIALS = 30000
P_HEADS = 0.5
Z_GATE = 3.0
SIGN_FRAC = 1.0
MIN_EDGE = 0.05
EXACT_TOL = 0.02


def optimal_reply(p):
    # Standard Penney reply: complement of p's 2nd symbol, then p's first L-1.
    return (1 - p[1],) + tuple(p[:len(p) - 1])


def all_patterns(L):
    pats = []
    for i in range(2 ** L):
        pats.append(tuple((i >> (L - 1 - j)) & 1 for j in range(L)))
    return pats


def all_states(L):
    states = []
    for m in range(L):  # lengths 0 .. L-1
        for i in range(2 ** m):
            states.append(tuple((i >> (m - 1 - j)) & 1 for j in range(m)))
    return states


def gauss_solve(A, b):
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        d = M[col][col]
        for j in range(col, n + 1):
            M[col][j] /= d
        for r in range(n):
            if r != col and M[r][col] != 0.0:
                f = M[r][col]
                for j in range(col, n + 1):
                    M[r][j] -= f * M[col][j]
    return [M[i][n] for i in range(n)]


def exact_p2_winrate(pa, pb, p_heads):
    """Exact P(pb appears before pa) via an absorbing Markov chain over the last
    L-1 flips. h_s = P(reach pb-absorb before pa-absorb | state s); answer h_()."""
    L = len(pa)
    states = all_states(L)
    idx = {s: k for k, s in enumerate(states)}
    n = len(states)
    A = [[0.0] * n for _ in range(n)]
    b = [0.0] * n
    for s in states:
        r = idx[s]
        A[r][r] += 1.0
        for bit, pr in ((1, p_heads), (0, 1.0 - p_heads)):
            t = s + (bit,)
            if len(t) == L and t == pa:
                pass                      # absorb into A -> contributes 0
            elif len(t) == L and t == pb:
                b[r] += pr                # absorb into B -> contributes prob 1
            else:
                nxt = t if len(t) < L else t[1:]
                A[r][idx[nxt]] -= pr
    h = gauss_solve(A, b)
    return h[idx[()]]


def mc_p2_winrate(rng, pa, pb, p_heads, trials):
    L = len(pa)
    wins = 0
    for _ in range(trials):
        window = ()
        while True:
            bit = 1 if rng.random() < p_heads else 0
            window = (window + (bit,))[-L:]
            if len(window) == L:
                if window == pb:
                    wins += 1
                    break
                if window == pa:
                    break
    return wins / trials


def run_regime(L, seed, p_heads):
    rng = random.Random(seed)
    rows = []
    for pa in all_patterns(L):
        pb = optimal_reply(pa)
        mc = mc_p2_winrate(rng, pa, pb, p_heads, TRIALS)
        ex = exact_p2_winrate(pa, pb, p_heads)
        se = math.sqrt(mc * (1.0 - mc) / TRIALS) if 0.0 < mc < 1.0 else 0.0
        z = (mc - 0.5) / se if se > 0 else 0.0
        rows.append({"edge": mc - 0.5, "z": z, "mc": mc, "exact": ex,
                     "dev": abs(mc - ex), "pa": pa, "pb": pb})
    worst = min(rows, key=lambda r: r["edge"])
    return {
        "L": L,
        "n_first_picks": len(rows),
        "min_z": min(r["z"] for r in rows),
        "min_edge": min(r["edge"] for r in rows),
        "min_winrate": min(r["mc"] for r in rows),
        "favor_frac": sum(1 for r in rows if r["edge"] > 0) / len(rows),
        "all_favor_p2": all(r["edge"] > 0 for r in rows),
        "max_dev_from_exact": max(r["dev"] for r in rows),
        "worst_pa": "".join(str(x) for x in worst["pa"]),
        "worst_pb": "".join(str(x) for x in worst["pb"]),
        "worst_mc": worst["mc"],
        "worst_exact": worst["exact"],
    }


def compute():
    base = run_regime(BASE_L, SEED, P_HEADS)
    shifted = run_regime(SHIFT_L, SEED + 1, P_HEADS)
    g1 = base["min_z"] >= Z_GATE
    g2 = (base["favor_frac"] >= SIGN_FRAC) and (base["min_edge"] >= MIN_EDGE)
    g3 = (shifted["min_z"] >= Z_GATE) and shifted["all_favor_p2"]
    g4 = (base["max_dev_from_exact"] <= EXACT_TOL) and \
         (shifted["max_dev_from_exact"] <= EXACT_TOL)
    all_pass = g1 and g2 and g3 and g4

    def rnd(d):
        return {k: (round(v, 6) if isinstance(v, float) else v) for k, v in d.items()}

    return {
        "seed": SEED,
        "base_L": BASE_L,
        "shift_L": SHIFT_L,
        "trials": TRIALS,
        "p_heads": P_HEADS,
        "z_gate": Z_GATE,
        "sign_frac_gate": SIGN_FRAC,
        "min_edge_gate": MIN_EDGE,
        "exact_tol": EXACT_TOL,
        "base": rnd(base),
        "shifted": rnd(shifted),
        "g1_headline_3sigma": g1,
        "g2_sign_magnitude": g2,
        "g3_robust_shift_l4": g3,
        "g4_exactly_true": g4,
        "all_pass": all_pass,
    }


def main():
    results = compute()
    results2 = compute()
    assert json.dumps(results, sort_keys=True) == json.dumps(results2, sort_keys=True), "non-deterministic"
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    print("G1 headline (>=3s):", "PASS" if results["g1_headline_3sigma"] else "FAIL",
          "min_z=%.4f" % results["base"]["min_z"])
    print("G2 sign+magnitude:", "PASS" if results["g2_sign_magnitude"] else "FAIL",
          "favor_frac=%.4f min_edge=%.4f" % (results["base"]["favor_frac"], results["base"]["min_edge"]))
    print("G3 robust (L=4)  :", "PASS" if results["g3_robust_shift_l4"] else "FAIL",
          "min_z=%.4f" % results["shifted"]["min_z"])
    print("G4 exactly-true  :", "PASS" if results["g4_exactly_true"] else "FAIL",
          "base_dev=%.5f shift_dev=%.5f" % (results["base"]["max_dev_from_exact"], results["shifted"]["max_dev_from_exact"]))
    print("ALL_PASS         :", results["all_pass"])
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
