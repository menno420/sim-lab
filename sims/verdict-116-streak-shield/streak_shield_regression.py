#!/usr/bin/env python3
"""PROPOSAL 103 verifier — streak-shield variance amplification.

Claim: a "streak shield" (after W consecutive true wins, bank a shield that
negates the next loss, counting it as a win) is REGRESSIVE — it boosts the
rating of an already-high-skill cohort more than the low-skill cohort it is
marketed to protect. We show the shield's mean rating uplift for the
high-skill cohort exceeds that of the low-skill cohort by >= 3 sigma, using a
paired Monte Carlo (same per-game outcomes scored with and without the shield).

Stdlib only. Deterministic under the pinned seed. Prints a compact results
dict and its sha256; exits 0 on PASS (>=3 sigma and both cohorts positive).
"""
import hashlib
import json
import math
import random

SEED = 20260717
N_PER_COHORT = 10000
GAMES = 200
STREAK_W = 3          # consecutive true wins to bank one shield
LOW_P = 0.45          # low-skill per-game win probability
HIGH_P = 0.55         # high-skill per-game win probability
SIGMA_GATE = 3.0


def play(outcomes, use_shield):
    """Score a fixed list of true win/loss outcomes; return net rating."""
    wins = losses = streak = shields = 0
    for won in outcomes:
        if won:
            wins += 1
            streak += 1
            if streak >= STREAK_W:
                shields += 1
                streak = 0
        else:
            if use_shield and shields > 0:
                shields -= 1     # shield absorbs the loss
                wins += 1        # loss scored as a win
                streak = 0       # shield consumed
            else:
                losses += 1
                streak = 0
    return wins - losses


def cohort_uplift(rng, p):
    """Paired mean uplift (shield minus no-shield) and its standard error."""
    diffs = []
    for _ in range(N_PER_COHORT):
        outcomes = [rng.random() < p for _ in range(GAMES)]
        diffs.append(play(outcomes, True) - play(outcomes, False))
    n = len(diffs)
    mean = sum(diffs) / n
    var = sum((d - mean) ** 2 for d in diffs) / (n - 1)
    return mean, math.sqrt(var / n)


def main():
    rng = random.Random(SEED)
    low_mean, low_se = cohort_uplift(rng, LOW_P)
    high_mean, high_se = cohort_uplift(rng, HIGH_P)
    gap = high_mean - low_mean
    gap_se = math.sqrt(low_se ** 2 + high_se ** 2)
    z = gap / gap_se
    passed = z >= SIGMA_GATE and low_mean > 0 and high_mean > low_mean
    results = {
        "seed": SEED,
        "n_per_cohort": N_PER_COHORT,
        "games": GAMES,
        "streak_w": STREAK_W,
        "low_p": LOW_P,
        "high_p": HIGH_P,
        "low_uplift_mean": round(low_mean, 6),
        "low_uplift_stderr": round(low_se, 6),
        "high_uplift_mean": round(high_mean, 6),
        "high_uplift_stderr": round(high_se, 6),
        "uplift_gap": round(gap, 6),
        "uplift_gap_sigma": round(z, 4),
        "sigma_gate": SIGMA_GATE,
        "regressive": bool(high_mean > low_mean),
        "passed": bool(passed),
    }
    blob = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(blob.encode()).hexdigest()
    print(blob)
    print("sha256:" + digest)
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
