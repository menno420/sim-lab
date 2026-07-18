#!/usr/bin/env python3
"""PROPOSAL 143 — rank-decay churn cliff: loss aversion inverts the decay lever
(round-33 GAME slot).

Phenomenon: a competitive ranked ladder applies RANK DECAY — an idle player
loses rank over time. The folk belief is that decay keeps the ladder healthy:
"if players lose rank when they stop, decay pressures them to keep playing, so
more decay = more activity." Model the ladder as an agent population and the
folk belief INVERTS once players are loss-averse.

Each of N players has a fixed true_rank and a moving current_rank (starts at
true_rank). Underranking = true_rank - current_rank; a player's per-match win
probability is p = clip(0.5 + K*underrank, 0.05, 0.95) — underranked players win
more (the folk "grind back" channel). Each period a player draws a fresh
per-match enjoyment u ~ Uniform[0, U_MAX] and forms the loss-averse subjective
match value

    v = u + DELTA*(p - LAMBDA*(1 - p)),

where a prospective rank GAIN of DELTA is valued +DELTA and a rank LOSS of DELTA
is valued -LAMBDA*DELTA (loss aversion, LAMBDA >= 1). If v > 0 the player PLAYS
one match (win w.p. p: current_rank += DELTA, else current_rank -= DELTA), counts
one unit of activity, and resets accumulated idle pain to 0. Otherwise the player
is idle: apply decay current_rank -= d (this RAISES future underranking and hence
future p — the folk recovery channel), accumulate loss-averse pain += LAMBDA*d,
and if pain > PATIENCE the player QUITS the game permanently (churn).

Two worlds — LAMBDA_CONTROL = 1.0 (no loss aversion) and LAMBDA_REAL = 2.25 (the
empirical Kahneman & Tversky prospect-theory coefficient) — are each run at two
decay levels: d = 0 (baseline) and d = D_HIGH (aggressive). Steady-state total
activity is the average matches played per period over the last half of T; the
paired reduction is baseline_activity - highdecay_activity (common random numbers
per trial), over R independent trials (per-trial seed offset from SEED).

Folk belief (inverted here): "rank decay keeps a ladder healthy; more decay = more
activity." Under loss aversion, aggressive decay instead pushes marginal players
to QUIT (pain crosses PATIENCE before the recovery channel pulls them back), so
beyond a small optimal decay rate raising the decay rate REDUCES total ladder
activity. The SIGN of decay's effect on activity depends on LAMBDA — with no loss
aversion decay is harmless (folk belief holds), with realistic loss aversion decay
backfires. A model-dependence result (the P024 discipline).

Anchor: prospect theory / loss aversion (Kahneman & Tversky 1979; loss-aversion
coefficient LAMBDA ~= 2.25 from Tversky & Kahneman 1992,
https://en.wikipedia.org/wiki/Loss_aversion).

Model note (declared): u is the per-MATCH enjoyment and is drawn fresh each period
(the "intrinsic per-match enjoyment" — day-to-day disposition to play), which is
what makes a no-decay ladder a LIVING population rather than a degenerate frozen
one; every other quantity is exactly as described above.

Pre-registered gates (APPROVE iff ALL hold, in order G1 -> G2 -> G3):
  G1  AGREEMENT : two independent halves of the R trials produce the SAME headline
                  reduction within noise — the half-vs-half difference has
                  |z| < SIGMA_GATE (NO significant disagreement). The estimator
                  is stable.
  G2  CONTROL   : in the LAMBDA_CONTROL = 1.0 world, aggressive decay does NOT
                  reduce activity — the reduction (baseline - highdecay) is NOT
                  significantly positive (z < SIGMA_GATE). Isolates that the
                  backfire needs loss aversion.
  G3  HEAD      : in the LAMBDA_REAL = 2.25 world, aggressive decay SIGNIFICANTLY
                  reduces activity — the reduction has z = reduction/se
                  >= SIGMA_GATE. The counterintuitive backfire.
"""

import hashlib
import json
import math
import random

SEED = 20260717
SIGMA_GATE = 3.0

N = 1000                 # players in the ladder
T = 200                  # periods (matches-worth of time)
R = 20                   # independent trials (per-trial seed offset from SEED)
K = 0.03                 # win-prob sensitivity to underranking
DELTA = 1.0              # rank change per match / per rank-gain-or-loss unit
U_MAX = 2.0              # per-match enjoyment ~ Uniform[0, U_MAX]
PATIENCE = 3.0           # accumulated loss-averse pain that triggers a quit
D_HIGH = 0.3             # aggressive decay rate (rank lost per idle period)

LAMBDA_CONTROL = 1.0     # no loss aversion (folk-belief control world)
LAMBDA_REAL = 2.25       # empirical prospect-theory loss-aversion coefficient

TRIAL_STRIDE = 7919      # per-trial seed offset multiplier (prime)


def simulate(d, lam, seed):
    """One ladder run: returns (steady_state_activity, surviving_population).

    steady_state_activity = average matches played per period over the last half
    of T; surviving_population = players who have not quit by the end.
    """
    rng = random.Random(seed)
    uniform = rng.uniform
    randf = rng.random
    current = [0.0] * N          # current_rank, starts at true_rank (= 0)
    pain = [0.0] * N
    alive = [True] * N
    half_from = T // 2
    total = 0
    for t in range(T):
        played = 0
        for i in range(N):
            if not alive[i]:
                continue
            # true_rank fixed at 0 -> underrank = -current_rank
            p = 0.5 - K * current[i]
            if p < 0.05:
                p = 0.05
            elif p > 0.95:
                p = 0.95
            u = uniform(0.0, U_MAX)                    # per-match enjoyment
            v = u + DELTA * (p - lam * (1.0 - p))      # loss-averse match value
            if v > 0.0:
                played += 1
                if randf() < p:
                    current[i] += DELTA                # win -> climb (over-rank)
                else:
                    current[i] -= DELTA                # loss -> drop (under-rank)
                pain[i] = 0.0
            else:
                current[i] -= d                        # decay: folk recovery channel
                pain[i] += lam * d                     # loss-averse idle pain
                if pain[i] > PATIENCE:
                    alive[i] = False                   # churn: quit permanently
        if t >= half_from:
            total += played
    return total / (T - half_from), sum(alive)


def _mean_se(values):
    """Sample mean and standard error of the mean."""
    n = len(values)
    mean = sum(values) / n
    if n > 1:
        var = sum((x - mean) ** 2 for x in values) / (n - 1)
    else:
        var = 0.0
    return mean, math.sqrt(var / n)


def _z(mean, se, null=0.0):
    return (mean - null) / se if se > 0 else float("inf")


def run_world(lam):
    """R paired trials at decay 0 (baseline) and D_HIGH (aggressive) for one lam.

    Common random numbers per trial (baseline and highdecay share the trial seed)
    for a low-variance paired reduction. Returns per-trial reductions plus the
    mean activities and surviving populations.
    """
    base_act = []
    high_act = []
    base_pop = []
    high_pop = []
    reductions = []
    for r in range(R):
        s = SEED + r * TRIAL_STRIDE
        ba, bp = simulate(0.0, lam, s)
        ha, hp = simulate(D_HIGH, lam, s)
        base_act.append(ba)
        high_act.append(ha)
        base_pop.append(bp)
        high_pop.append(hp)
        reductions.append(ba - ha)
    return {
        "reductions": reductions,
        "base_activity": sum(base_act) / R,
        "high_activity": sum(high_act) / R,
        "base_pop": sum(base_pop) / R,
        "high_pop": sum(high_pop) / R,
    }


def run():
    control = run_world(LAMBDA_CONTROL)
    real = run_world(LAMBDA_REAL)

    # --- G1: estimator agreement (halves of the LAMBDA_REAL headline reductions)
    red = real["reductions"]
    half = R // 2
    a_mean, a_se = _mean_se(red[:half])
    b_mean, b_se = _mean_se(red[half:])
    se_ab = math.sqrt(a_se * a_se + b_se * b_se)
    z_g1 = (a_mean - b_mean) / se_ab if se_ab > 0 else 0.0
    g1 = abs(z_g1) < SIGMA_GATE

    # --- G2: control world (no loss aversion) — reduction NOT significantly positive
    c_mean, c_se = _mean_se(control["reductions"])
    z_g2 = _z(c_mean, c_se)
    g2 = z_g2 < SIGMA_GATE

    # --- G3: head — realistic loss aversion, reduction significantly positive
    r_mean, r_se = _mean_se(red)
    z_g3 = _z(r_mean, r_se)
    g3 = (r_mean > 0.0) and (z_g3 >= SIGMA_GATE)

    first_failing = None
    if not g1:
        first_failing = "G1"
    elif not g2:
        first_failing = "G2"
    elif not g3:
        first_failing = "G3"
    all_pass = g1 and g2 and g3

    def r6(x):
        return round(float(x), 6)

    return {
        "proposal": 143,
        "seed": SEED,
        "sigma_gate": SIGMA_GATE,
        "n": N,
        "t": T,
        "r": R,
        "params": {
            "k": K,
            "delta": DELTA,
            "u_max": U_MAX,
            "patience": PATIENCE,
            "d_high": D_HIGH,
            "lambda_control": LAMBDA_CONTROL,
            "lambda_real": LAMBDA_REAL,
        },
        "control_base_activity": r6(control["base_activity"]),
        "control_high_activity": r6(control["high_activity"]),
        "control_base_pop": r6(control["base_pop"]),
        "control_high_pop": r6(control["high_pop"]),
        "real_base_activity": r6(real["base_activity"]),
        "real_high_activity": r6(real["high_activity"]),
        "real_base_pop": r6(real["base_pop"]),
        "real_high_pop": r6(real["high_pop"]),
        "g1_half_a_reduction": r6(a_mean),
        "g1_half_b_reduction": r6(b_mean),
        "g1_z": r6(z_g1),
        "g1_agreement": g1,
        "g2_control_reduction": r6(c_mean),
        "g2_se": r6(c_se),
        "g2_z": r6(z_g2),
        "g2_control": g2,
        "g3_head_reduction": r6(r_mean),
        "g3_se": r6(r_se),
        "g3_z": r6(z_g3),
        "g3_head": g3,
        "first_failing_gate": first_failing,
        "all_pass": all_pass,
    }


def main():
    results = run()
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    print(json.dumps(results, indent=2, sort_keys=True))
    print(f"Results-JSON sha256: {digest}")
    print(
        "G1 agreement    :",
        "PASS" if results["g1_agreement"] else "FAIL",
        f"(half_a-half_b, z={results['g1_z']:+.2f}, |z|<{SIGMA_GATE})",
    )
    print(
        "G2 control      :",
        "PASS" if results["g2_control"] else "FAIL",
        f"(lambda=1 reduction={results['g2_control_reduction']:+.4f}, "
        f"z={results['g2_z']:+.2f}, not-sig-positive z<{SIGMA_GATE})",
    )
    print(
        "G3 head         :",
        "PASS" if results["g3_head"] else "FAIL",
        f"(lambda=2.25 reduction={results['g3_head_reduction']:+.4f}, "
        f"z={results['g3_z']:+.2f}, z>={SIGMA_GATE})",
    )
    print("all_pass        :", results["all_pass"], "first_failing_gate:", results["first_failing_gate"])
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
