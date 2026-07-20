#!/usr/bin/env python3
"""intransitive_efron_dice.py — reference verifier for PROPOSAL 195.

Efron's dice: four six-sided dice A, B, C, D (Bradley Efron's canonical set)

    A: 4 4 4 4 0 0     B: 3 3 3 3 3 3     C: 6 6 2 2 2 2     D: 5 5 5 1 1 1

form an INTRANSITIVE cycle: A beats B beats C beats D beats A, and every one of
those four cyclic matchups is won by the earlier die with probability EXACTLY
2/3. So "which die is best?" has no answer — whichever die you pick, the reply
die that beats it two-thirds of the time is the one just before it in the cycle.
The "rolls-higher-more-than-half" relation is non-transitive: it contains a
directed 4-cycle, so there is no maximum element. (The two NON-cyclic pairs are
asymmetric-but-not-cyclic: C beats A with probability 5/9, and B vs D is a fair
1/2 — both closed forms are checked too.)

Two independent computations agree:
  * exact_win_prob : the win-probability of every ordered die pair computed by
    EXHAUSTIVE enumeration of all 6*6 = 36 face matchups, as an exact rational
    (fractions.Fraction). This is the EXACTLY-TRUE value — each cyclic pair is
    2/3 with ZERO ties, on the nose.
  * mc_win_prob    : a seeded Monte-Carlo dice race — the reproducible dry-sim
    that confirms the exact value at >=3 sigma.

Gates (all_pass iff G1 AND G2 AND G3, in order):
  G1 statistical (>=3 sigma) : across the four cyclic pairs, the MINIMUM z of
                               (MC earlier-die winrate - 0.5) >= Z_GATE and every
                               cyclic winrate > 0.5 (each cyclic edge is real).
  G2 exactly-true            : the exhaustively-enumerated win matrix equals the
                               closed forms EXACTLY (Fraction ==): every cyclic
                               pair == 2/3 with tie-prob == 0, the cycle
                               A>B>C>D>A holds (each cyclic prob > 1/2, reverse
                               < 1/2), C-over-A == 5/9, B-vs-D == 1/2; AND the MC
                               winrates agree with the exact values within
                               EXACT_TOL (the surprising odds are exact).
  G3 robustness/shift        : vary the match length k in {1,3,5,7} (best-of-k
                               majority). The exact cyclic dominance PERSISTS
                               (every cyclic pair wins > 1/2 at every k) and
                               STRENGTHENS (win-prob strictly monotone increasing
                               in k); a seeded MC best-of-7 confirms it at
                               min z >= Z_GATE. The paradox is not a single-roll
                               artefact — it survives and amplifies under longer
                               matches.
"""
import random, math, json, hashlib
from fractions import Fraction

SEED = 20260717
TRIALS = 200000
Z_GATE = 3.0
BEST_OF_KS = [1, 3, 5, 7]
SHIFT_K = 7            # the Monte-Carlo z leg of the robustness gate

# Efron's dice — Wikipedia "Intransitive dice" § Efron's dice (rev sha1
# b3fdd4b02fcf23195db6e6d217d34ef5b394a5c7, oldid 1357047248).
DICE = {
    "A": (4, 4, 4, 4, 0, 0),
    "B": (3, 3, 3, 3, 3, 3),
    "C": (6, 6, 2, 2, 2, 2),
    "D": (5, 5, 5, 1, 1, 1),
}
# The cycle: the earlier die beats the later die (each with prob 2/3).
CYCLE = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")]
ALL_ORDERED = [(x, y) for x in "ABCD" for y in "ABCD" if x != y]

EXACT_CYCLIC = Fraction(2, 3)
EXACT_C_OVER_A = Fraction(5, 9)
EXACT_B_VS_D = Fraction(1, 2)
EXACT_TOL = 0.01


def exact_win_tie(d1, d2):
    """Exact (P(d1 > d2), P(tie)) via full 36-pair enumeration, as Fractions."""
    faces1, faces2 = DICE[d1], DICE[d2]
    win = tie = total = 0
    for a in faces1:
        for b in faces2:
            total += 1
            if a > b:
                win += 1
            elif a == b:
                tie += 1
    return Fraction(win, total), Fraction(tie, total)


def mc_win_prob(rng, d1, d2, trials):
    """Seeded Monte-Carlo P(d1 > d2) over `trials` single rolls."""
    faces1, faces2 = DICE[d1], DICE[d2]
    wins = 0
    for _ in range(trials):
        if faces1[rng.randrange(6)] > faces2[rng.randrange(6)]:
            wins += 1
    return wins / trials


def best_of_k_exact(p, k):
    """Exact P(win a best-of-k majority) given per-round win prob p, no ties."""
    need = k // 2 + 1
    q = Fraction(1) - p
    return sum(Fraction(math.comb(k, j)) * p ** j * q ** (k - j)
               for j in range(need, k + 1))


def mc_best_of_k(rng, d1, d2, k, trials):
    """Seeded Monte-Carlo best-of-k majority win prob (cyclic pairs never tie)."""
    faces1, faces2 = DICE[d1], DICE[d2]
    wins = 0
    for _ in range(trials):
        s = 0
        for _r in range(k):
            a, b = faces1[rng.randrange(6)], faces2[rng.randrange(6)]
            s += 1 if a > b else -1
        if s > 0:
            wins += 1
    return wins / trials


def zscore(phat, p0, n):
    se = math.sqrt(p0 * (1.0 - p0) / n)
    return (phat - p0) / se if se > 0 else 0.0


def compute():
    rng = random.Random(SEED)

    # --- exact win/tie matrix over all 12 ordered pairs -------------------
    exact = {}
    tie = {}
    for x, y in ALL_ORDERED:
        w, t = exact_win_tie(x, y)
        exact[(x, y)] = w
        tie[(x, y)] = t

    # --- G1: statistical (single-roll Monte-Carlo on the four cyclic pairs)
    g1_pairs = []
    for x, y in CYCLE:
        mc = mc_win_prob(rng, x, y, TRIALS)
        g1_pairs.append({
            "pair": f"{x}>{y}",
            "mc_winrate": round(mc, 6),
            "z_vs_half": round(zscore(mc, 0.5, TRIALS), 6),
            "exact": str(exact[(x, y)]),
            "dev_from_exact": round(abs(mc - float(exact[(x, y)])), 6),
        })
    g1_min_z = min(p["z_vs_half"] for p in g1_pairs)
    g1_all_above_half = all(p["mc_winrate"] > 0.5 for p in g1_pairs)
    g1 = g1_min_z >= Z_GATE and g1_all_above_half

    # --- G2: exactly-true (closed forms == exhaustive enumeration) --------
    cyclic_all_two_thirds = all(exact[(x, y)] == EXACT_CYCLIC for x, y in CYCLE)
    no_ties_in_cycle = all(tie[(x, y)] == 0 for x, y in CYCLE)
    cycle_holds = all(exact[(x, y)] > Fraction(1, 2) for x, y in CYCLE) and \
        all(exact[(y, x)] < Fraction(1, 2) for x, y in CYCLE)
    c_over_a_ok = exact[("C", "A")] == EXACT_C_OVER_A
    a_over_c_ok = exact[("A", "C")] == Fraction(4, 9)
    b_vs_d_ok = exact[("B", "D")] == EXACT_B_VS_D and exact[("D", "B")] == EXACT_B_VS_D
    max_mc_dev = max(p["dev_from_exact"] for p in g1_pairs)
    mc_agrees = max_mc_dev <= EXACT_TOL
    g2 = (cyclic_all_two_thirds and no_ties_in_cycle and cycle_holds and
          c_over_a_ok and a_over_c_ok and b_vs_d_ok and mc_agrees)

    win_matrix = {f"{x}>{y}": str(exact[(x, y)]) for x, y in ALL_ORDERED}

    # --- G3: robustness/shift (best-of-k majority amplification) -----------
    g3_rows = []
    for k in BEST_OF_KS:
        probs = [best_of_k_exact(exact[(x, y)], k) for x, y in CYCLE]
        g3_rows.append({
            "k": k,
            "min_winprob": round(min(float(p) for p in probs), 6),
            "min_margin": round(min(float(p) - 0.5 for p in probs), 6),
            "all_above_half": all(p > Fraction(1, 2) for p in probs),
        })
    cycle_persists_all_k = all(r["all_above_half"] for r in g3_rows)
    # strict monotone increase of the per-pair win prob as k grows
    per_k_min = [r["min_winprob"] for r in g3_rows]
    monotone_in_k = all(per_k_min[i] < per_k_min[i + 1]
                        for i in range(len(per_k_min) - 1))
    mc_bo7 = []
    for x, y in CYCLE:
        mc = mc_best_of_k(rng, x, y, SHIFT_K, TRIALS)
        mc_bo7.append(round(zscore(mc, 0.5, TRIALS), 6))
    mc_bo7_min_z = min(mc_bo7)
    g3 = cycle_persists_all_k and monotone_in_k and mc_bo7_min_z >= Z_GATE

    all_pass = g1 and g2 and g3
    first_failing = None
    if not g1:
        first_failing = "G1"
    elif not g2:
        first_failing = "G2"
    elif not g3:
        first_failing = "G3"

    return {
        "seed": SEED,
        "trials": TRIALS,
        "z_gate": Z_GATE,
        "best_of_ks": BEST_OF_KS,
        "dice": {k: list(v) for k, v in DICE.items()},
        "cycle": [f"{x}>{y}" for x, y in CYCLE],
        "win_matrix_exact": win_matrix,
        "g1_pairs": g1_pairs,
        "g1_min_z": g1_min_z,
        "g1_all_above_half": g1_all_above_half,
        "g2_cyclic_all_two_thirds": cyclic_all_two_thirds,
        "g2_no_ties_in_cycle": no_ties_in_cycle,
        "g2_cycle_holds": cycle_holds,
        "g2_c_over_a": str(exact[("C", "A")]),
        "g2_a_over_c": str(exact[("A", "C")]),
        "g2_b_vs_d": str(exact[("B", "D")]),
        "g2_max_mc_dev_from_exact": max_mc_dev,
        "g3_best_of": g3_rows,
        "g3_cycle_persists_all_k": cycle_persists_all_k,
        "g3_monotone_in_k": monotone_in_k,
        "g3_mc_best_of7_z": mc_bo7,
        "g3_mc_best_of7_min_z": mc_bo7_min_z,
        "g1_statistical_3sigma": g1,
        "g2_exactly_true": g2,
        "g3_robustness_shift": g3,
        "all_pass": all_pass,
        "first_failing_gate": first_failing,
    }


def main():
    results = compute()
    results2 = compute()
    assert json.dumps(results, sort_keys=True) == json.dumps(results2, sort_keys=True), \
        "non-deterministic"
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    print("G1 statistical(>=3s):", "PASS" if results["g1_statistical_3sigma"] else "FAIL",
          "min_z=%.4f" % results["g1_min_z"])
    print("G2 exactly-true     :", "PASS" if results["g2_exactly_true"] else "FAIL",
          "cyclic=2/3 no-ties cycle-holds max_mc_dev=%.5f" % results["g2_max_mc_dev_from_exact"])
    print("G3 robustness/shift :", "PASS" if results["g3_robustness_shift"] else "FAIL",
          "min_bo7_z=%.4f monotone=%s" % (results["g3_mc_best_of7_min_z"], results["g3_monotone_in_k"]))
    print("ALL_PASS            :", results["all_pass"])
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
