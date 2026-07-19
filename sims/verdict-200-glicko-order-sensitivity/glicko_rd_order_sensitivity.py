#!/usr/bin/env python3
"""glicko_rd_order_sensitivity.py — reference simulation for PROPOSAL 187.

Glicko-1 order-sensitivity: an identical win/loss record against an identical
opponent field yields a DIFFERENT final rating depending on the ORDER in which
the games are processed, because the rating deviation (RD) shrinks after each
rated game and so weights early games more than late ones. Streak order (all
wins, then all losses) ends materially BELOW alternating order (W,L,W,L,...)
for the same 6W-6L record. Stdlib-only (random, math, json, hashlib).

Anchor: Mark E. Glickman, "The Glicko system" (glicko.net/glicko/glicko.pdf) —
the RD-weighted rating update g(RD), E(...), and the RD-shrinking step.

Gates (all_pass iff G1 AND G2 AND G3, in order):
  G1 order-effect   : base regime mean(streak - alt) nonzero at |z| >= Z_GATE.
  G2 sign+magnitude : same-sign fraction >= SIGN_FRAC AND |mean| >= MIN_POINTS.
  G3 robust (shift) : +200 shifted opponent field, |z| >= Z_GATE AND same sign.
"""
import random, math, json, hashlib

SEED = 20260717
TRIALS = 5000
N_GAMES = 12
R0 = 1500.0
RD0 = 350.0
OPP_RD = 30.0
OPP_SD = 200.0
BASE_MEAN = 1500.0
SHIFT_MEAN = 1700.0
Z_GATE = 3.0
SIGN_FRAC = 0.90
MIN_POINTS = 5.0
Q = math.log(10.0) / 400.0


def g(RD):
    return 1.0 / math.sqrt(1.0 + 3.0 * Q * Q * RD * RD / (math.pi * math.pi))


def expected(r, r_j, RD_j):
    return 1.0 / (1.0 + 10.0 ** (-g(RD_j) * (r - r_j) / 400.0))


def update_one(r, RD, r_j, RD_j, s):
    gj = g(RD_j)
    ej = expected(r, r_j, RD_j)
    d2 = 1.0 / (Q * Q * gj * gj * ej * (1.0 - ej))
    denom = 1.0 / (RD * RD) + 1.0 / d2
    new_RD = math.sqrt(1.0 / denom)
    new_r = r + (Q / denom) * gj * (s - ej)
    return new_r, new_RD


def process(games):
    r, RD = R0, RD0
    for (r_j, RD_j, s) in games:
        r, RD = update_one(r, RD, r_j, RD_j, s)
    return r


def run_regime(opp_mean, seed):
    rng = random.Random(seed)
    effects = []
    for _ in range(TRIALS):
        opps = [rng.gauss(opp_mean, OPP_SD) for _ in range(N_GAMES)]
        pairs = [(opps[i], OPP_RD, (1.0 if i % 2 == 0 else 0.0)) for i in range(N_GAMES)]
        alt_order = list(pairs)
        streak_order = [pairs[i] for i in range(N_GAMES) if i % 2 == 0] + \
                       [pairs[i] for i in range(N_GAMES) if i % 2 == 1]
        effects.append(process(streak_order) - process(alt_order))
    n = len(effects)
    mean = sum(effects) / n
    var = sum((x - mean) ** 2 for x in effects) / (n - 1)
    sd = math.sqrt(var)
    se = sd / math.sqrt(n)
    z = mean / se if se > 0 else 0.0
    same_sign = sum(1 for x in effects if (x > 0) == (mean > 0)) / n
    return {"mean": mean, "sd": sd, "se": se, "z": z, "same_sign_frac": same_sign}


def compute():
    base = run_regime(BASE_MEAN, SEED)
    shifted = run_regime(SHIFT_MEAN, SEED + 1)
    g1 = abs(base["z"]) >= Z_GATE
    g2 = (base["same_sign_frac"] >= SIGN_FRAC) and (abs(base["mean"]) >= MIN_POINTS)
    g3 = (abs(shifted["z"]) >= Z_GATE) and ((shifted["mean"] > 0) == (base["mean"] > 0))
    all_pass = g1 and g2 and g3

    def rnd(d):
        return {k: round(v, 6) for k, v in d.items()}

    return {
        "seed": SEED,
        "trials": TRIALS,
        "n_games": N_GAMES,
        "r0": R0,
        "rd0": RD0,
        "opp_rd": OPP_RD,
        "opp_sd": OPP_SD,
        "base_opp_mean": BASE_MEAN,
        "shift_opp_mean": SHIFT_MEAN,
        "z_gate": Z_GATE,
        "sign_frac_gate": SIGN_FRAC,
        "min_points_gate": MIN_POINTS,
        "base": rnd(base),
        "shifted": rnd(shifted),
        "g1_order_effect": g1,
        "g2_sign_magnitude": g2,
        "g3_robust_shift": g3,
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
    print("G1 order-effect   :", "PASS" if results["g1_order_effect"] else "FAIL", "z=%.4f" % results["base"]["z"])
    print("G2 sign+magnitude :", "PASS" if results["g2_sign_magnitude"] else "FAIL",
          "same_sign=%.4f mean=%.4f" % (results["base"]["same_sign_frac"], results["base"]["mean"]))
    print("G3 robust (shift) :", "PASS" if results["g3_robust_shift"] else "FAIL", "z=%.4f" % results["shifted"]["z"])
    print("ALL_PASS          :", results["all_pass"])
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
