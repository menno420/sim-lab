#!/usr/bin/env python3
"""PROPOSAL 243 — Fibonacci nim (Whinihan's game) & the Zeckendorf strategy.

HEAD: In Fibonacci nim (one pile of n tokens; the first move removes any m with
1 <= m <= n-1; every later move removes 1 <= m <= 2*(the opponent's last
removal), capped at the tokens left; last token wins — normal play), the player
to move LOSES (the position is a P-position) if and only if n is a Fibonacci
number (1, 2, 3, 5, 8, 13, 21, ...) — Whinihan (1963). The optimal winning move
ties to Zeckendorf's theorem: every n has a unique representation as a sum of
non-consecutive Fibonacci numbers, and from a winning position removing the
SMALLEST Zeckendorf summand is always legal and leaves the opponent a
P-position.

The verifier implements the GAME (a memoized outcome oracle over states
(n, cap)) and does NOT assume the theorem; the Fibonacci/Zeckendorf structure is
built independently by integer recurrence, then the two are compared.

Gate battery (SEED=20260717; each gate in its own direction):
  G1 EXACT identity (integer arithmetic): for every n in [1,N],
     (loses(n) == True) iff (n in Fib); mismatches must be 0. ALSO the
     constructive Zeckendorf strategy — for every winning n the smallest
     Zeckendorf summand s is a legal first move (s <= n-1) and leaves the
     opponent a P-position (win(n-s, min(2s, n-s)) == False); violations 0.
  G2 MC AGREEMENT (|z| < 3): exact P-density p0 = |Fib cap [1,N]| / N; draw
     n_samples uniform ints in [1,N], classify each via the DP table; the
     sampled loss-rate agrees with p0 inside 3 sigma.
  G3 INVARIANCE / ROBUSTNESS: (a) a second independent horizon N2 reproduces the
     same P-position set on the overlap [1, min(N,N2)], byte-identical and equal
     to the Fibonacci prefix (discrepancies 0); (b) randomized-play robustness —
     from every winning start our DP player beats a uniformly-random opponent in
     every one of R games (optimal_player_losses 0).
  G4 FALSIFIABILITY (|z| > 3): the naive "P-positions are the multiples of 3"
     foil is rejected far outside 3 sigma; a secondary "powers of two" foil is
     rejected too.

Determinism posture: build_results() is a pure function of SEED and the fixed
params; no wall-clock, hostname, or unseeded randomness. Every float is stored
with a fixed format so the serialization is invocation-stable; p0 is stored as
the exact "a/b" fraction string. main() builds the results twice in one process
and asserts the canonical JSON forms are byte-identical, prints a human summary
and `results_sha256=<64hex>` on its own line, and exits 1 if any gate fails.
"""

import hashlib
import json
import math
import random
import sys
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0

N = 800               # exact-DP horizon (G1/G2/G4 range [1, N])
N2 = 1200             # second independent horizon for the invariance leg
N_SAMPLES = 200_000   # Monte-Carlo sample size for G2
R = 40                # randomized games per winning start for G3(b)


def fmt(x):
    """Fixed float format so the serialization is invocation-stable."""
    return f"{float(x):.12g}"


def build_win_table(nmax):
    """table[n][cap] = True iff the player to move from a pile of n tokens with
    a per-move removal cap of `cap` can win (normal play, last token wins).

    Bottom-up over n so recursion depth is never an issue. A move removes m in
    1..min(cap, n): m == n takes the last token (immediate win); otherwise the
    opponent faces (n-m, min(n-m, 2*m)). The mover wins iff some m leaves the
    opponent in a losing position. cap == 0 => no legal move => mover loses.
    """
    table = [None] * (nmax + 1)
    table[0] = [False]  # unused sentinel (n=0 is never a to-move state)
    for n in range(1, nmax + 1):
        row = [False] * (n + 1)  # index cap = 0..n ; cap 0 stays False (loss)
        for cap in range(1, n + 1):
            won = False
            hi = cap if cap < n else n
            for m in range(1, hi + 1):
                if m == n:
                    won = True
                    break
                opp_cap = 2 * m if 2 * m < (n - m) else (n - m)
                if not table[n - m][opp_cap]:
                    won = True
                    break
            row[cap] = won
        table[n] = row
    return table


def loses_starting(table, n):
    """True iff the player to move from a fresh pile of n loses (P-position).
    Starting first-move cap = n-1 (cannot take the whole pile); n=1 => cap 0."""
    return not table[n][n - 1]


def fib_set_upto(nmax):
    """Fibonacci numbers (Whinihan / Zeckendorf convention 1,2,3,5,8,...) <= nmax
    as a sorted list, by integer recurrence."""
    fibs = [1, 2]
    while True:
        nxt = fibs[-1] + fibs[-2]
        if nxt > nmax:
            break
        fibs.append(nxt)
    return [f for f in fibs if f <= nmax]


def zeckendorf_summands(n, fibs_desc):
    """Greedy Zeckendorf decomposition of n into non-consecutive Fibonacci
    summands (fibs_desc is the Fibonacci list in descending order)."""
    rep = []
    for f in fibs_desc:
        if f <= n:
            rep.append(f)
            n -= f
        if n == 0:
            break
    return rep


def pick_winning_move(table, n, cap):
    """Return the smallest m in 1..min(cap,n) that wins (takes the last token or
    leaves the opponent a P-position), or None if the position is lost."""
    hi = cap if cap < n else n
    for m in range(1, hi + 1):
        if m == n:
            return m
        opp_cap = 2 * m if 2 * m < (n - m) else (n - m)
        if not table[n - m][opp_cap]:
            return m
    return None


def play_random_opponent(table, n_start, rng):
    """Play one full game from a winning start: our player uses the DP to pick a
    winning move; the opponent removes a uniformly-random legal count. Returns
    True iff our (first) player takes the last token."""
    n = n_start
    cap = n_start - 1
    our_turn = True
    while True:
        hi = cap if cap < n else n
        if our_turn:
            m = pick_winning_move(table, n, cap)
            if m is None:  # should never happen from a winning start
                return False
        else:
            m = rng.randint(1, hi)
        n -= m
        if n == 0:
            return our_turn  # the mover just took the last token
        cap = 2 * m if 2 * m < n else n
        our_turn = not our_turn


def zscore_prop(hits, n, p0):
    phat = hits / n
    se = math.sqrt(p0 * (1.0 - p0) / n)
    return (phat - p0) / se, phat, se


def build_results():
    table = build_win_table(N)
    fibs = fib_set_upto(N)
    fib_set = set(fibs)
    fibs_desc = sorted(fibs, reverse=True)

    results = {
        "proposal": 243,
        "claim": (
            "Fibonacci nim (Whinihan): the player to move loses iff n is a "
            "Fibonacci number; from a winning position remove the smallest "
            "Zeckendorf summand to leave the opponent a P-position."
        ),
        "seed": SEED,
        "z_gate": fmt(Z_GATE),
        "N": N,
        "N2": N2,
        "n_samples": N_SAMPLES,
        "R": R,
        "fibonacci_upto_N": fibs,
    }

    # --- G1 EXACT identity + constructive Zeckendorf strategy -----------------
    mismatches = 0
    for n in range(1, N + 1):
        if (loses_starting(table, n)) != (n in fib_set):
            mismatches += 1
    zeck_violations = 0
    for n in range(1, N + 1):
        if n in fib_set:
            continue  # winning positions only
        s = min(zeckendorf_summands(n, fibs_desc))  # smallest Zeckendorf summand
        legal = s <= n - 1
        opp_cap = 2 * s if 2 * s < (n - s) else (n - s)
        leaves_p = (table[n - s][opp_cap] is False)
        if not (legal and leaves_p):
            zeck_violations += 1
    g1_pass = (mismatches == 0) and (zeck_violations == 0)
    results["G1_exact_identity"] = {
        "n_tested": N,
        "mismatches": mismatches,
        "zeckendorf_strategy_violations": zeck_violations,
        "pass": g1_pass,
    }

    # --- G2 MC agreement with exact P-density, |z| < 3 ------------------------
    p0_frac = Fraction(len(fibs), N)
    p0_float = float(p0_frac)
    rng = random.Random(SEED)
    losses = 0
    for _ in range(N_SAMPLES):
        n = rng.randint(1, N)
        if loses_starting(table, n):
            losses += 1
    z, phat, se = zscore_prop(losses, N_SAMPLES, p0_float)
    g2_pass = abs(z) < Z_GATE
    results["G2_mc_agreement"] = {
        "p0_fraction": f"{p0_frac.numerator}/{p0_frac.denominator}",
        "p0_float": fmt(p0_float),
        "losses": losses,
        "n_samples": N_SAMPLES,
        "p_hat": fmt(phat),
        "z": fmt(z),
        "pass": g2_pass,
    }

    # --- G3 invariance / robustness -------------------------------------------
    # (a) second horizon reproduces the P-set on the overlap, == Fibonacci prefix
    overlap = min(N, N2)
    table2 = build_win_table(N2)
    p_run1 = [n for n in range(1, overlap + 1) if loses_starting(table, n)]
    p_run2 = [n for n in range(1, overlap + 1) if loses_starting(table2, n)]
    fib_prefix = [f for f in fibs if f <= overlap]
    invariance_discrepancies = (
        sum(1 for a, b in zip(p_run1, p_run2) if a != b)
        + abs(len(p_run1) - len(p_run2))
        + (0 if p_run1 == fib_prefix else 1)
    )
    # (b) randomized-play robustness from every winning start
    rng2 = random.Random(SEED)
    games_played = 0
    optimal_player_losses = 0
    for n in range(1, N + 1):
        if n in fib_set:
            continue
        for _ in range(R):
            games_played += 1
            if not play_random_opponent(table, n, rng2):
                optimal_player_losses += 1
    g3_pass = (invariance_discrepancies == 0) and (optimal_player_losses == 0)
    results["G3_invariance_robustness"] = {
        "N2": N2,
        "overlap": overlap,
        "invariance_discrepancies": invariance_discrepancies,
        "games_played": games_played,
        "optimal_player_losses": optimal_player_losses,
        "pass": g3_pass,
    }

    # --- G4 falsifiability: naive foils rejected far outside 3 sigma ----------
    truth = [loses_starting(table, n) for n in range(1, N + 1)]

    def foil_stats(predicate):
        disagreements = sum(
            1 for i, n in enumerate(range(1, N + 1)) if predicate(n) != truth[i]
        )
        d = disagreements / N
        # z of the disagreement proportion against a null of exact agreement
        z_foil = d / math.sqrt(d * (1.0 - d) / N) if 0.0 < d < 1.0 else float("inf")
        return disagreements, z_foil

    powers_of_two = set()
    p = 1
    while p <= N:
        powers_of_two.add(p)
        p *= 2

    dis3, z3 = foil_stats(lambda n: n % 3 == 0)
    dis2, z2 = foil_stats(lambda n: n in powers_of_two)
    g4_pass = (abs(z3) > Z_GATE) and (abs(z2) > Z_GATE)
    results["G4_falsifiability"] = {
        "foil_multiples_of_3": {
            "disagreement_count": dis3,
            "z_abs": fmt(abs(z3)),
        },
        "foil_powers_of_two": {
            "disagreement_count": dis2,
            "z_abs": fmt(abs(z2)),
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
    results["first_failing_gate"] = next((k for k in order if not gates[k]), None)
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
    for k in ["G1", "G2", "G3", "G4"]:
        print(f"{k}: {'PASS' if r1['gates'][k] else 'FAIL'}")
    print()
    print(f"all_pass: {r1['all_pass']}")
    print(f"first_failing_gate: {r1['first_failing_gate']}")
    print(f"results_sha256={digest}")
    sys.exit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
