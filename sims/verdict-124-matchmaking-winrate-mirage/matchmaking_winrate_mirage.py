#!/usr/bin/env python3
"""
matchmaking_winrate_mirage.py — reference verifier for PROPOSAL 111
(round-25, game slot).

The "matchmaking win-rate mirage" in competitive skill-based matchmaking (SBMM).
Pair players by their current Elo rating, run a season whose game outcomes are
drawn from a logistic TRUE-SKILL win model, and update ratings with the symmetric
Elo rule. Each player's rating adjusts until their EXPECTED SCORE against the
matched near-rating pool is 0.5:

    E[score_i] = sigma((R_i - R_opp)/S) -> sigma(0) = 0.5   (rating-matched)

so the observed win rate is driven toward a skill-INDEPENDENT ~50% fixed point and
is COMPRESSED almost flat across skill. The counterintuitive core, shown by a
same-seed two-regime contrast on the SAME players and skills:

  * Under RANDOM matching (no matchmaking) the win rate is a near-perfect skill
    signal — a strong player beats random opponents far more than half the time,
    so corr(skill, win rate) is high and the top-vs-bottom decile win-rate gap is
    large.
  * Under SBMM the win rate collapses to a compressed MIRAGE — the top and bottom
    skill deciles win nearly the same fraction — even though the very same games'
    RATING recovers true skill almost perfectly. Matchmaking does not destroy the
    skill information; it moves it out of the win rate and into the rating.

Gates (all on the /se margin — z on the ESTIMATED MEAN via se = std / sqrt(TRIALS),
the P104/P105/P106/P107 convention):
  G1 win-rate compression (headline): the SBMM top-skill-decile minus
     bottom-skill-decile mean win-rate GAP is <= GAP_MAX by >= 3 sigma (best and
     worst players win nearly the same fraction under matchmaking).
  G2 matchmaking-causes-it (control): the RANDOM-matching decile win-rate gap is
     >= RANDOM_GAP_MIN AND exceeds the SBMM gap by >= DELTA_MIN, both by >= 3 sigma
     -- win rate DOES encode skill absent matchmaking, so the compression is caused
     by the pairing rule, not by the skill model.
  G3 rating-retains-skill mirage: the mean (corr(skill, final rating) -
     corr(skill, SBMM win rate)) is >= CONTRAST_MIN by >= 3 sigma, with
     corr(skill, rating) >= RATING_CORR_MIN -- the hidden rating keeps the skill
     signal the win rate loses.

stdlib only; fully deterministic under SEED.
"""
import random
import math
import json
import hashlib

SEED = 20260717        # proposal-owned pinned seed; SEEDLESS discipline
N_PLAYERS = 200        # players per season (even; decile = 20 players)
GAMES = 600            # SBMM rounds; each round every player plays one game
BURN_IN = 400          # SBMM rounds discarded before win-rate measurement
RANDOM_GAMES = 200     # rounds of the random-matching control regime
SKILL_SD = 250.0       # SD of true latent skill on the Elo (400-)logistic scale
ELO_SCALE = 400.0      # standard Elo denominator (log-10 logistic)
K_FACTOR = 16.0        # Elo update step
R0 = 1500.0            # common starting rating
MATCH_JITTER = 15.0    # per-round rating jitter (Elo pts) -> rotating near pool
TRIALS = 200           # independent replications -> mean +/- se over TRIALS
SIGMA_GATE = 3.0       # gate threshold in sigma
GAP_MAX = 0.12         # G1: max SBMM top-vs-bottom decile win-rate gap
RANDOM_GAP_MIN = 0.50  # G2: min random-matching decile win-rate gap
DELTA_MIN = 0.40       # G2: min (random gap - SBMM gap) compression
RATING_CORR_MIN = 0.90 # G3: min corr(true skill, final rating)
CONTRAST_MIN = 0.30    # G3: min (corr_rating - corr_winrate) informativeness gap


def win_prob(skill_a, skill_b):
    """Logistic TRUE-SKILL win probability (P a beats b), Elo 400-scale."""
    return 1.0 / (1.0 + 10.0 ** (-(skill_a - skill_b) / ELO_SCALE))


def expected_score(rating_a, rating_b):
    """Elo expected score of a vs b from current RATINGS (the update anchor)."""
    return 1.0 / (1.0 + 10.0 ** (-(rating_a - rating_b) / ELO_SCALE))


def pearson(xs, ys):
    """Pearson correlation; 0.0 if either series is constant."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sxx = syy = 0.0
    for x, y in zip(xs, ys):
        dx = x - mx
        dy = y - my
        sxy += dx * dy
        sxx += dx * dx
        syy += dy * dy
    denom = math.sqrt(sxx * syy)
    return sxy / denom if denom > 0 else 0.0


def decile_gap(values, order_by_skill, d):
    """Mean over the top skill-decile minus mean over the bottom skill-decile."""
    top = sum(values[p] for p in order_by_skill[-d:]) / d
    bottom = sum(values[p] for p in order_by_skill[:d]) / d
    return top - bottom


def simulate_replication(rng):
    """One replication: draw skills once, then run the SBMM season and the
    RANDOM-matching control on the SAME players/skills.

    Returns (corr_rating, corr_winrate_sbmm, sbmm_gap, random_gap,
    corr_winrate_random).
    """
    idx = list(range(N_PLAYERS))
    skill = [rng.gauss(0.0, SKILL_SD) for _ in idx]
    order_by_skill = sorted(idx, key=lambda p: skill[p])
    d = N_PLAYERS // 10

    # --- SBMM regime: rating-matched Elo season ---
    rating = [R0 for _ in idx]
    wins = [0 for _ in idx]
    played = [0 for _ in idx]
    for rnd in range(GAMES):
        counts = rnd >= BURN_IN
        order = sorted(idx, key=lambda p: rating[p] + rng.uniform(-MATCH_JITTER, MATCH_JITTER))
        for k in range(0, N_PLAYERS, 2):
            a = order[k]
            b = order[k + 1]
            a_wins = rng.random() < win_prob(skill[a], skill[b])
            e_a = expected_score(rating[a], rating[b])
            s_a = 1.0 if a_wins else 0.0
            rating[a] += K_FACTOR * (s_a - e_a)
            rating[b] += K_FACTOR * ((1.0 - s_a) - (1.0 - e_a))
            if counts:
                played[a] += 1
                played[b] += 1
                if a_wins:
                    wins[a] += 1
                else:
                    wins[b] += 1
    winrate = [wins[p] / played[p] if played[p] > 0 else 0.0 for p in idx]
    corr_rating = pearson(skill, rating)
    corr_winrate = pearson(skill, winrate)
    sbmm_gap = decile_gap(winrate, order_by_skill, d)

    # --- RANDOM-matching control: same skills, opponents drawn at random ---
    r_wins = [0 for _ in idx]
    r_played = [0 for _ in idx]
    for _ in range(RANDOM_GAMES):
        shuffled = idx[:]
        rng.shuffle(shuffled)
        for k in range(0, N_PLAYERS, 2):
            a = shuffled[k]
            b = shuffled[k + 1]
            a_wins = rng.random() < win_prob(skill[a], skill[b])
            r_played[a] += 1
            r_played[b] += 1
            if a_wins:
                r_wins[a] += 1
            else:
                r_wins[b] += 1
    r_winrate = [r_wins[p] / r_played[p] if r_played[p] > 0 else 0.0 for p in idx]
    corr_winrate_random = pearson(skill, r_winrate)
    random_gap = decile_gap(r_winrate, order_by_skill, d)

    return corr_rating, corr_winrate, sbmm_gap, random_gap, corr_winrate_random


def moments(values):
    """Return (mean, se) with se = sample-sd / sqrt(n) over the replications."""
    n = len(values)
    m = sum(values) / n
    var = max(sum(v * v for v in values) / n - m * m, 0.0)
    return m, math.sqrt(var / n)


def main():
    rng = random.Random(SEED)

    corr_ratings = []
    corr_winrates = []
    sbmm_gaps = []
    random_gaps = []
    corr_winrate_randoms = []
    contrasts = []
    gap_deltas = []
    for _ in range(TRIALS):
        cr, cw, sg, rg, rcw = simulate_replication(rng)
        corr_ratings.append(cr)
        corr_winrates.append(cw)
        sbmm_gaps.append(sg)
        random_gaps.append(rg)
        corr_winrate_randoms.append(rcw)
        contrasts.append(cr - cw)
        gap_deltas.append(rg - sg)

    mean_cr, se_cr = moments(corr_ratings)
    mean_cw, se_cw = moments(corr_winrates)
    mean_sg, se_sg = moments(sbmm_gaps)
    mean_rg, se_rg = moments(random_gaps)
    mean_rcw, se_rcw = moments(corr_winrate_randoms)
    mean_ct, se_ct = moments(contrasts)
    mean_gd, se_gd = moments(gap_deltas)

    # G1 — win-rate compression: SBMM decile gap <= GAP_MAX by >= 3 sigma.
    z_g1 = (GAP_MAX - mean_sg) / se_sg if se_sg > 0 else float("inf")
    g1 = (z_g1 >= SIGMA_GATE) and (mean_sg <= GAP_MAX)

    # G2 — matchmaking-causes-it: random gap large AND exceeds SBMM gap by >=3s.
    z_g2_level = (mean_rg - RANDOM_GAP_MIN) / se_rg if se_rg > 0 else float("inf")
    z_g2_delta = (mean_gd - DELTA_MIN) / se_gd if se_gd > 0 else float("inf")
    g2 = ((z_g2_level >= SIGMA_GATE) and (mean_rg >= RANDOM_GAP_MIN) and
          (z_g2_delta >= SIGMA_GATE) and (mean_gd >= DELTA_MIN))

    # G3 — rating-retains-skill mirage: (corr_rating - corr_winrate) >= CONTRAST_MIN
    #      by >= 3 sigma (paired se, within-season contrast), corr_rating high.
    z_g3 = (mean_ct - CONTRAST_MIN) / se_ct if se_ct > 0 else float("inf")
    g3 = (z_g3 >= SIGMA_GATE) and (mean_ct >= CONTRAST_MIN) and (mean_cr >= RATING_CORR_MIN)

    all_pass = g1 and g2 and g3

    results = {
        "params": {
            "SEED": SEED, "N_PLAYERS": N_PLAYERS, "GAMES": GAMES,
            "BURN_IN": BURN_IN, "RANDOM_GAMES": RANDOM_GAMES,
            "SKILL_SD": SKILL_SD, "ELO_SCALE": ELO_SCALE, "K_FACTOR": K_FACTOR,
            "R0": R0, "MATCH_JITTER": MATCH_JITTER, "TRIALS": TRIALS,
            "SIGMA_GATE": SIGMA_GATE, "GAP_MAX": GAP_MAX,
            "RANDOM_GAP_MIN": RANDOM_GAP_MIN, "DELTA_MIN": DELTA_MIN,
            "RATING_CORR_MIN": RATING_CORR_MIN, "CONTRAST_MIN": CONTRAST_MIN,
        },
        "sim": {
            "corr_rating": round(mean_cr, 6), "se_corr_rating": round(se_cr, 6),
            "corr_winrate_sbmm": round(mean_cw, 6), "se_corr_winrate_sbmm": round(se_cw, 6),
            "corr_winrate_random": round(mean_rcw, 6), "se_corr_winrate_random": round(se_rcw, 6),
            "sbmm_decile_gap": round(mean_sg, 6), "se_sbmm_decile_gap": round(se_sg, 6),
            "random_decile_gap": round(mean_rg, 6), "se_random_decile_gap": round(se_rg, 6),
            "contrast": round(mean_ct, 6), "se_contrast": round(se_ct, 6),
            "gap_delta": round(mean_gd, 6), "se_gap_delta": round(se_gd, 6),
        },
        "gates": {
            "G1_winrate_compression": {"z": round(z_g1, 4),
                                       "sbmm_decile_gap": round(mean_sg, 6),
                                       "GAP_MAX": GAP_MAX, "pass": g1},
            "G2_matchmaking_causes_it": {"z_level": round(z_g2_level, 4),
                                         "z_delta": round(z_g2_delta, 4),
                                         "random_decile_gap": round(mean_rg, 6),
                                         "gap_delta": round(mean_gd, 6),
                                         "pass": g2},
            "G3_rating_retains_skill": {"z": round(z_g3, 4),
                                        "contrast": round(mean_ct, 6),
                                        "corr_rating": round(mean_cr, 6),
                                        "corr_winrate_sbmm": round(mean_cw, 6),
                                        "CONTRAST_MIN": CONTRAST_MIN, "pass": g3},
        },
        "all_pass": all_pass,
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    results["results_sha256"] = digest

    with open("matchmaking_winrate_mirage_results.json", "w") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256:", digest)
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
