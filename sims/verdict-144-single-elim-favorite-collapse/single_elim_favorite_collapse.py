#!/usr/bin/env python3
"""PROPOSAL 131 — single-elimination favorite-collapse (round-30 GAME slot).

Phenomenon: in a single-elimination bracket the strongest entrant must win
EVERY round, so its title probability is the product of its per-match win
probabilities — a quantity that shrinks geometrically as the bracket grows.
Folk belief (inverted here): "a bigger/longer tournament is a truer test that
rewards the best player." Reality: each added round is an independent
coin-weighted haircut that can only LOWER the favorite's title odds, making a
non-favorite title MORE likely.

Model (Bradley-Terry, paired): N = 2**R entrants — exactly one favorite of
strength f > 1 and N-1 identical "normal" entrants of strength 1. A match
between strengths a and b is won by a with probability a/(a+b). Because all
normals are indistinguishable, the favorite faces a normal in EVERY round under
ANY seeding, so its per-match win probability is the constant
    p = f/(f+1)
and its exact title probability is the closed form
    P_title(R) = p**R.

Literature anchors: Bradley & Terry (1952); David (1959) "Tournaments and paired
comparisons"; Ryvkin & Ortmann (2008) "The predictive power of three prominent
tournament formats", Management Science 54(3) — single-elimination is the least
selection-efficient common format; Schwenk (2000) on seeded-bracket fairness.

Pre-registered gates (APPROVE iff ALL hold, in order G1 -> G2 -> G3):
  G1  SIM CORRECT : at R=8 (256 entrants) the Monte-Carlo favorite title
                    frequency matches the closed form p**8 within z < 3 sigma.
  G2  GEOMETRIC   : the multiplicative per-round haircut is constant — the MC
                    ratio P_title(8)/P_title(4) matches p**4 within z < 3 sigma
                    (delta method); each added round is the SAME haircut.
  G3  INVERSION   : at R=6 (64-entrant esports bracket) a 3x favorite is
                    dethroned in the MAJORITY of runs — MC P(favorite loses)
                    > 0.5 AND matches 1 - p**6 within z < 3 sigma. The
                    "bigger tournament rewards the best" belief is reversed.
"""

import hashlib
import json
import math
import random

SEED = 20260717
TRIALS = 200_000
FAVORITE_STRENGTH = 3.0          # 3x the field
ROUNDS = (2, 4, 6, 8)            # N = 4, 16, 64, 256
SIGMA_GATE = 3.0

P_MATCH = FAVORITE_STRENGTH / (FAVORITE_STRENGTH + 1.0)   # 0.75


def _favorite_wins_match(rng):
    # favorite (strength f) vs a normal (strength 1): Bradley-Terry draw.
    return rng.random() < P_MATCH


def simulate_favorite_title_freq(rounds, trials, rng):
    """Fraction of `trials` runs the favorite wins all `rounds` knockout matches.

    Every opponent is an (indistinguishable) normal, so the favorite's path is
    `rounds` i.i.d. Bradley-Terry matches at p=P_MATCH. We simulate the actual
    match sequence rather than the closed form, so the gate is a genuine
    falsification test of the coin-weighted-rounds claim.
    """
    wins = 0
    for _ in range(trials):
        survived = True
        for _r in range(rounds):
            if not _favorite_wins_match(rng):
                survived = False
                break
        if survived:
            wins += 1
    return wins / trials


def _z_prop(phat, p0, trials):
    """z-score of an observed proportion vs a null proportion p0."""
    se = math.sqrt(p0 * (1.0 - p0) / trials)
    return (phat - p0) / se if se > 0 else float("inf")


def run():
    rng = random.Random(SEED)

    freqs = {}
    for r in ROUNDS:
        freqs[r] = simulate_favorite_title_freq(r, TRIALS, rng)

    closed = {r: P_MATCH ** r for r in ROUNDS}

    # G1 — sim correct at R=8
    z_g1 = _z_prop(freqs[8], closed[8], TRIALS)
    g1 = abs(z_g1) < SIGMA_GATE

    # G2 — constant geometric haircut: ratio P(8)/P(4) == p**4
    ratio_mc = freqs[8] / freqs[4]
    ratio_anchor = P_MATCH ** 4
    var4 = closed[4] * (1.0 - closed[4]) / TRIALS
    var8 = closed[8] * (1.0 - closed[8]) / TRIALS
    se_ratio = ratio_anchor * math.sqrt(
        var8 / closed[8] ** 2 + var4 / closed[4] ** 2
    )
    z_g2 = (ratio_mc - ratio_anchor) / se_ratio if se_ratio > 0 else float("inf")
    g2 = abs(z_g2) < SIGMA_GATE

    # G3 — inversion at R=6: favorite dethroned in the majority
    p_fav_loses = 1.0 - freqs[6]
    anchor_loses = 1.0 - closed[6]
    z_g3 = _z_prop(p_fav_loses, anchor_loses, TRIALS)
    g3_matches = abs(z_g3) < SIGMA_GATE
    g3_majority = p_fav_loses > 0.5
    g3 = g3_matches and g3_majority

    all_pass = g1 and g2 and g3

    return {
        "proposal": 131,
        "seed": SEED,
        "trials": TRIALS,
        "favorite_strength": FAVORITE_STRENGTH,
        "p_match": P_MATCH,
        "rounds": list(ROUNDS),
        "mc_title_freq": {str(r): freqs[r] for r in ROUNDS},
        "closed_form_title_prob": {str(r): closed[r] for r in ROUNDS},
        "g1_sim_correct": g1,
        "g1_z": z_g1,
        "g2_geometric_haircut": g2,
        "g2_ratio_mc": ratio_mc,
        "g2_ratio_anchor": ratio_anchor,
        "g2_z": z_g2,
        "g3_inversion": g3,
        "g3_p_favorite_loses_r6": p_fav_loses,
        "g3_anchor": anchor_loses,
        "g3_majority": g3_majority,
        "g3_z": z_g3,
        "sigma_gate": SIGMA_GATE,
        "all_pass": all_pass,
    }


def main():
    results = run()
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    print(
        "G1 sim-correct  :",
        "PASS" if results["g1_sim_correct"] else "FAIL",
        f"(z={results['g1_z']:+.3f})",
    )
    print(
        "G2 geometric    :",
        "PASS" if results["g2_geometric_haircut"] else "FAIL",
        f"(z={results['g2_z']:+.3f})",
    )
    print(
        "G3 inversion    :",
        "PASS" if results["g3_inversion"] else "FAIL",
        f"(z={results['g3_z']:+.3f}, P(fav loses)={results['g3_p_favorite_loses_r6']:.4f})",
    )
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
