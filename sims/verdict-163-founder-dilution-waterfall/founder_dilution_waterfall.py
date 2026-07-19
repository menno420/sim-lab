#!/usr/bin/env python3
"""PROPOSAL 150 — venture slot (round-35) — sim-lab verifier.

Claim: between two term sheets that raise the SAME amount for the SAME company,
the one with the HIGHER headline pre-money valuation can leave founders with
LESS money at exit -- across a strict MAJORITY of realistic exit outcomes --
because it carries a PARTICIPATING preferred with a liquidation MULTIPLE, and
the participation drag (a fixed multiple off the top, then the investor ALSO
shares the remainder) dominates the founder-friendly effect of the lower
investor ownership fraction the higher valuation buys, everywhere except the
extreme upside tail. Founders who "take the higher valuation" optimise the one
number on the term sheet that is nearly irrelevant to their realised proceeds.

One company, one exit-value distribution, TWO term sheets evaluated on the SAME
exit draw (paired):
  Offer A -- LOWER headline valuation, CLEAN terms: pre 30, raise 10 (post 40,
             investor owns f_A = 0.25), 1x NON-PARTICIPATING preferred.
  Offer B -- HIGHER headline valuation, STACKED terms: pre 50, raise 10 (post 60,
             investor owns f_B = 1/6), 2x PARTICIPATING preferred (uncapped).

Founder (common) proceeds at exit X:
  A: investor takes max(1x preference, converts to f_A of X) capped at X;
     founder = X - investor.   (non-participating: EITHER preference OR common)
  B: investor takes 2x preference off the top, THEN participates for f_B of the
     remainder; founder = (1 - f_B) * max(0, X - 2*preference).

The analytic crossover is X* = 200: below it Offer A pays founders strictly more
(the participation multiple dominates); above it Offer B does (the lower
ownership fraction the higher valuation bought finally wins). Realistic exits
sit overwhelmingly below X*, so the higher-valuation sheet is a founder trap for
all but moonshot outcomes.

Three ordered gates on the /se convention (z = mean/se, z_gate = 3.0):
  G1 MAJORITY-INVERSION  -- fraction of exits with founder_A > founder_B exceeds
                            0.5 (binomial z), one-sided.
  G2 TYPICAL-OUTCOME GAP -- conditional on a non-moonshot exit (X < X*), the
                            paired proceeds gap founder_A - founder_B > 0 (z).
  G3 ROBUSTNESS          -- both effects survive under a SECOND, heavier-tailed
                            exit distribution (more moonshots -- the case most
                            favourable to the high-valuation sheet).

stdlib only (hashlib, json, math, random). Deterministic: one random.Random(SEED)
drawn in a single fixed-order stream (Dist A then Dist B). Digest posture:
WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY with the P127+ TWIST (compact canonical
hashed preimage, pretty indent=2 stdout dump, floats rounded 6 dp, no on-disk
JSON, in-process double-run byte-identity assertion). Exit 0 iff all gates pass.
"""

import hashlib
import json
import math
import random

SEED = 20260717            # fleet-pinned

# ---- pinned world (committed constants; sim-lab must reproduce exactly) ----
RAISE = 10.0               # $M raised -- identical across both term sheets
PRE_A = 30.0               # Offer A pre-money ($M) -- the LOWER headline valuation
PRE_B = 50.0               # Offer B pre-money ($M) -- the HIGHER headline valuation
MULT_A = 1.0               # Offer A liquidation multiple (1x)
MULT_B = 2.0               # Offer B liquidation multiple (2x)
PARTICIPATING_A = False    # Offer A: non-participating (either pref OR convert)
PARTICIPATING_B = True     # Offer B: participating (pref THEN share remainder)
X_CROSS = 200.0            # analytic founder-proceeds crossover ($M): A>B below

# exit-value distributions (log-normal, $M); Dist A primary, Dist B robustness
MED_A = 80.0               # Dist A median exit ($M)
SIG_A = 1.0                # Dist A log-sigma
MED_B = 120.0              # Dist B median exit ($M) -- heavier upside
SIG_B = 1.3                # Dist B log-sigma -- more moonshots (favours Offer B)

M_TRIALS = 20000           # exit draws per distribution
SIGMA = 3.0                # gate threshold (sigma)

F_A = RAISE / (PRE_A + RAISE)   # investor ownership fraction, Offer A
F_B = RAISE / (PRE_B + RAISE)   # investor ownership fraction, Offer B


def founder_nonparticipating(x, pref, frac):
    """Founder (common) proceeds under a NON-PARTICIPATING preferred: investor
    takes the GREATER of its liquidation preference or its as-converted common
    share, capped at the exit value; the founder gets the rest."""
    investor = min(x, max(pref, frac * x))
    return x - investor


def founder_participating(x, pref, frac):
    """Founder (common) proceeds under a PARTICIPATING preferred: investor takes
    its liquidation preference off the top, THEN participates pro-rata in the
    remainder; the founder gets the non-investor share of what's left."""
    if x <= pref:
        return 0.0
    return (1.0 - frac) * (x - pref)


def founder_A(x):
    return founder_nonparticipating(x, MULT_A * RAISE, F_A)


def founder_B(x):
    return founder_participating(x, MULT_B * RAISE, F_B)


def draw_exit(rng, med, sig):
    """Exit value ($M) ~ LogNormal with the given median and log-sigma."""
    return rng.lognormvariate(math.log(med), sig)


def zstat(vals, h0):
    """One-sample z of the mean against H0: z = (mean - h0) / (stdev/sqrt(n))."""
    n = len(vals)
    mean = sum(vals) / n
    if n < 2:
        return mean, 0.0, 0.0
    var = sum((v - mean) ** 2 for v in vals) / (n - 1)
    se = math.sqrt(var) / math.sqrt(n)
    z = (mean - h0) / se if se > 0 else 0.0
    return mean, se, z


def run_distribution(rng, med, sig):
    wins = []               # 1 if founder_A > founder_B else 0  (per exit)
    below_gap = []          # founder_A - founder_B for exits with X < X_CROSS
    fa_all = []
    fb_all = []
    n_below = 0
    for _ in range(M_TRIALS):
        x = draw_exit(rng, med, sig)
        a = founder_A(x)
        b = founder_B(x)
        fa_all.append(a)
        fb_all.append(b)
        wins.append(1.0 if a > b else 0.0)
        if x < X_CROSS:
            below_gap.append(a - b)
            n_below += 1
    win_mean, win_se, win_z = zstat(wins, 0.5)
    gap_mean, gap_se, gap_z = zstat(below_gap, 0.0)
    fa_sorted = sorted(fa_all)
    fb_sorted = sorted(fb_all)
    return {
        "win_rate": win_mean,
        "win_se": win_se,
        "win_z": win_z,
        "below_gap_mean": gap_mean,
        "below_gap_se": gap_se,
        "below_gap_z": gap_z,
        "frac_below_cross": n_below / M_TRIALS,
        "mean_founder_A": sum(fa_all) / M_TRIALS,
        "mean_founder_B": sum(fb_all) / M_TRIALS,
        "median_founder_A": fa_sorted[M_TRIALS // 2],
        "median_founder_B": fb_sorted[M_TRIALS // 2],
    }


def run():
    rng = random.Random(SEED)          # ONE stream, fixed order: Dist A then B
    a = run_distribution(rng, MED_A, SIG_A)
    b = run_distribution(rng, MED_B, SIG_B)

    g1_pass = (a["win_z"] >= SIGMA) and (a["win_rate"] > 0.5)
    g2_pass = (a["below_gap_z"] >= SIGMA) and (a["below_gap_mean"] > 0.0)
    g3_pass = ((b["win_z"] >= SIGMA) and (b["win_rate"] > 0.5)
               and (b["below_gap_z"] >= SIGMA) and (b["below_gap_mean"] > 0.0))

    all_pass = g1_pass and g2_pass and g3_pass
    first_fail = None
    if not g1_pass:
        first_fail = "G1_majority_inversion"
    elif not g2_pass:
        first_fail = "G2_typical_outcome_gap"
    elif not g3_pass:
        first_fail = "G3_robustness"

    def rnd(x):
        return round(x, 6)

    def dist_block(d):
        return {
            "win_rate": rnd(d["win_rate"]),
            "win_se": rnd(d["win_se"]),
            "win_z": rnd(d["win_z"]),
            "below_gap_mean": rnd(d["below_gap_mean"]),
            "below_gap_se": rnd(d["below_gap_se"]),
            "below_gap_z": rnd(d["below_gap_z"]),
            "frac_below_cross": rnd(d["frac_below_cross"]),
            "mean_founder_A": rnd(d["mean_founder_A"]),
            "mean_founder_B": rnd(d["mean_founder_B"]),
            "median_founder_A": rnd(d["median_founder_A"]),
            "median_founder_B": rnd(d["median_founder_B"]),
        }

    results = {
        "proposal": 150,
        "domain": "venture",
        "slot": "round-35 venture",
        "seed": SEED,
        "claim": "a higher headline pre-money valuation carrying a participating "
                 "preferred with a liquidation multiple leaves founders with less "
                 "at exit across a majority of realistic outcomes than a lower "
                 "valuation with clean 1x non-participating terms",
        "params": {
            "raise": RAISE,
            "pre_A": PRE_A,
            "pre_B": PRE_B,
            "mult_A": MULT_A,
            "mult_B": MULT_B,
            "participating_A": PARTICIPATING_A,
            "participating_B": PARTICIPATING_B,
            "f_A": rnd(F_A),
            "f_B": rnd(F_B),
            "x_cross": X_CROSS,
            "med_A": MED_A,
            "sig_A": SIG_A,
            "med_B": MED_B,
            "sig_B": SIG_B,
            "m_trials": M_TRIALS,
            "sigma": SIGMA,
        },
        "dist_A": dist_block(a),
        "dist_B": dist_block(b),
        "gates": {
            "G1_majority_inversion": {
                "win_rate": rnd(a["win_rate"]),
                "z": rnd(a["win_z"]),
                "threshold_sigma": SIGMA,
                "one_sided": True,
                "pass": bool(g1_pass),
            },
            "G2_typical_outcome_gap": {
                "gap_mean": rnd(a["below_gap_mean"]),
                "z": rnd(a["below_gap_z"]),
                "frac_below_cross": rnd(a["frac_below_cross"]),
                "threshold_sigma": SIGMA,
                "one_sided": True,
                "pass": bool(g2_pass),
            },
            "G3_robustness": {
                "win_rate_B": rnd(b["win_rate"]),
                "win_z_B": rnd(b["win_z"]),
                "gap_mean_B": rnd(b["below_gap_mean"]),
                "gap_z_B": rnd(b["below_gap_z"]),
                "threshold_sigma": SIGMA,
                "pass": bool(g3_pass),
            },
        },
        "first_failing_gate": first_fail,
        "all_pass": bool(all_pass),
    }
    return results


def main():
    results = run()
    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # in-process double-run determinism assertion
    results2 = run()
    payload2 = json.dumps(results2, sort_keys=True, separators=(",", ":"))
    digest2 = hashlib.sha256(payload2.encode("utf-8")).hexdigest()
    assert digest == digest2, "non-deterministic: %s != %s" % (digest, digest2)

    g = results["gates"]
    print("G1 majority-inversion : win_rate=%.4f z=%+.4f %s" % (
        g["G1_majority_inversion"]["win_rate"], g["G1_majority_inversion"]["z"],
        "PASS" if g["G1_majority_inversion"]["pass"] else "FAIL"))
    print("G2 typical-outcome gap: gap_mean=%+.4f z=%+.4f (frac_below=%.4f) %s" % (
        g["G2_typical_outcome_gap"]["gap_mean"], g["G2_typical_outcome_gap"]["z"],
        g["G2_typical_outcome_gap"]["frac_below_cross"],
        "PASS" if g["G2_typical_outcome_gap"]["pass"] else "FAIL"))
    print("G3 robustness (dist B): win_rate=%.4f z=%+.4f gap=%+.4f z=%+.4f %s" % (
        g["G3_robustness"]["win_rate_B"], g["G3_robustness"]["win_z_B"],
        g["G3_robustness"]["gap_mean_B"], g["G3_robustness"]["gap_z_B"],
        "PASS" if g["G3_robustness"]["pass"] else "FAIL"))
    print("descriptive: dist_A mean founder A=%.4f B=%.4f | median A=%.4f B=%.4f" % (
        results["dist_A"]["mean_founder_A"], results["dist_A"]["mean_founder_B"],
        results["dist_A"]["median_founder_A"], results["dist_A"]["median_founder_B"]))
    print("all_pass =", results["all_pass"], " first_failing_gate =",
          results["first_failing_gate"])
    print(json.dumps(results, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + digest)
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
