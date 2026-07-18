#!/usr/bin/env python3
"""PROPOSAL 148 — The Will Rogers phenomenon (stage migration): reclassifying
members across a group boundary can raise the mean of BOTH groups at once while
the population mean is EXACTLY unchanged — no member's value changes (round-34
UNRELATED slot).

Named for Will Rogers' quip: "When the Okies left Oklahoma and moved to
California, they raised the average intelligence level in both states." The
serious version is the medical STAGE-MIGRATION artifact (Feinstein, Sosin &
Wells, NEJM 1985): when finer diagnostics reclassify borderline patients from an
EARLY (better-prognosis) stage into a LATE (worse-prognosis) stage, the
stage-specific survival of BOTH stages rises — because the migrated patients were
the WORST of the early stage (below its mean) yet BETTER than the average late
patient (above its mean) — even though not one patient's actual outcome changed.

The folk belief: "if the average outcome improves within EVERY subgroup, the
population as a whole must have improved — you cannot make every part better
without making the whole better." This is the intuition every stage-specific /
segment-specific dashboard rests on.

The counterintuitive truth: moving a member x from group HI (higher mean) to
group LO (lower mean), where LO_mean < x < HI_mean, RAISES both group means at
once (LO loses nothing and gains an above-its-mean member; HI sheds a
below-its-mean member) while the pooled mean is IDENTICALLY conserved — the
member was only RELABELLED, its value never touched. Every subgroup can improve
while the whole does not move a hair.

Object (humblest form): N members each with a FIXED real value v ~ Uniform[0, 1]
(read "normalised survival / quality — higher is better"). A COARSE classifier
splits them at threshold T_COARSE into LOW (v < T_COARSE) and HIGH (v >=
T_COARSE); HIGH's mean exceeds LOW's by construction. A FINER classifier then
MIGRATES the bottom slice of HIGH — members with T_COARSE <= v < T_FINE — down
into LOW (the "stage migration": borderline members reclassified into the group
whose mean they beat). Nothing but the LABEL changes.

  Closed form (Uniform[0,1], T_COARSE=0.5, T_FINE=0.6):
    LOW  mean : 0.25 (v<0.5)  ->  0.30 (v<0.6)   improvement +0.05
    HIGH mean : 0.75 (v>=0.5) ->  0.80 (v>=0.6)  improvement +0.05
    pooled mean: 0.5 -> 0.5  (conserved EXACTLY — relabel only)

A model-dependence result (the P024 discipline): "every subgroup improved" and
"the population improved" are DIFFERENT claims — they coincide only when group
membership is fixed. Let the boundary move and both subgroup means can rise on a
population that did not change at all.

Pre-registered gates (APPROVE iff ALL hold, in order G1 -> G2 -> G3):
  G1  AGREEMENT : two independent halves of the R low-group improvements produce
                  the SAME headline within noise — the half-vs-half difference has
                  |z| < SIGMA_GATE (NO significant disagreement). Estimator stable.
  G2  CONTROL   : the POOLED population mean does NOT improve — conservation holds
                  (max relative pooled-mean change <= CONS_TOL, a relabelling
                  identity) and the pooled change is NOT significantly positive
                  (z = mean/se < SIGMA_GATE). There is NO real aggregate gain.
  G3  HEAD      : BOTH subgroup means rise SIGNIFICANTLY — the smaller of the two
                  improvement z-scores (LOW, HIGH) is >= SIGMA_GATE and both means
                  are positive. Every subgroup improves at >=3 sigma even though
                  G2 proved the whole did not move.
"""

import hashlib
import json
import math
import random

SEED = 20260717
SIGMA_GATE = 3.0

N = 4000                 # members in the population
R = 40                   # independent trials (per-trial seed offset from SEED)
T_COARSE = 0.5           # coarse classifier split (LOW: v < T_COARSE, HIGH: v >= T_COARSE)
T_FINE = 0.6             # finer classifier: migrate HIGH members with T_COARSE <= v < T_FINE into LOW
CONS_TOL = 1e-9          # pooled-mean conservation tolerance (relabelling identity)

TRIAL_STRIDE = 7919      # per-trial seed offset multiplier (prime)


def _mean(values):
    return sum(values) / len(values) if values else 0.0


def simulate(seed):
    """One population: draw N fixed values, partition COARSELY, then MIGRATE the
    bottom slice of HIGH into LOW (the finer classifier). Returns the before/after
    group means and the pooled mean computed identically before and after.

    Migration is a pure RELABELLING: the value list is never modified, so the
    pooled mean is conserved by construction (the two partitions are a permutation
    of the same multiset).
    """
    rng = random.Random(seed)
    values = [rng.random() for _ in range(N)]  # v ~ Uniform[0, 1], FIXED per member

    low_before = [v for v in values if v < T_COARSE]
    high_before = [v for v in values if v >= T_COARSE]

    # finer classifier: HIGH members in [T_COARSE, T_FINE) migrate DOWN into LOW
    migrated = [v for v in high_before if v < T_FINE]
    high_after = [v for v in high_before if v >= T_FINE]
    low_after = low_before + migrated

    # pooled mean computed from the SAME full value list both times -> exact conservation
    pooled_before = _mean(values)
    pooled_after = (sum(low_after) + sum(high_after)) / N

    return {
        "low_before": _mean(low_before),
        "high_before": _mean(high_before),
        "low_after": _mean(low_after),
        "high_after": _mean(high_after),
        "pooled_before": pooled_before,
        "pooled_after": pooled_after,
        "n_migrated": len(migrated),
        "count_conserved": (len(low_after) + len(high_after)) == N,
    }


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
    """z on the /se convention. A zero-mean zero-variance quantity carries no
    signal, so its z is 0 (not an infinity) — used by the exact-conservation
    control where the pooled change is identically 0."""
    if se == 0.0:
        return 0.0 if mean == null else float("inf")
    return (mean - null) / se


def run():
    low_impr = []      # per-trial LOW-group mean improvement (after - before)
    high_impr = []     # per-trial HIGH-group mean improvement (after - before)
    pooled_impr = []   # per-trial pooled-mean change (identically 0 — relabel only)
    cons_rel = []      # per-trial relative pooled-mean change
    migrated = []
    counts_ok = True
    low_b = []
    high_b = []
    low_a = []
    high_a = []
    for r in range(R):
        out = simulate(SEED + r * TRIAL_STRIDE)
        low_impr.append(out["low_after"] - out["low_before"])
        high_impr.append(out["high_after"] - out["high_before"])
        pooled_impr.append(out["pooled_after"] - out["pooled_before"])
        denom = out["pooled_before"] if out["pooled_before"] != 0.0 else 1.0
        cons_rel.append(abs(out["pooled_after"] - out["pooled_before"]) / denom)
        migrated.append(out["n_migrated"])
        counts_ok = counts_ok and out["count_conserved"]
        low_b.append(out["low_before"])
        high_b.append(out["high_before"])
        low_a.append(out["low_after"])
        high_a.append(out["high_after"])

    # --- G1: estimator agreement (halves of the LOW-group improvements)
    half = R // 2
    a_mean, a_se = _mean_se(low_impr[:half])
    b_mean, b_se = _mean_se(low_impr[half:])
    se_ab = math.sqrt(a_se * a_se + b_se * b_se)
    z_g1 = (a_mean - b_mean) / se_ab if se_ab > 0 else 0.0
    g1 = abs(z_g1) < SIGMA_GATE

    # --- G2: conservation control — the POOLED mean does NOT improve
    p_mean, p_se = _mean_se(pooled_impr)
    z_g2 = _z(p_mean, p_se)
    cons_max_rel = max(cons_rel)
    g2 = counts_ok and (cons_max_rel <= CONS_TOL) and (z_g2 < SIGMA_GATE)

    # --- G3: head — BOTH subgroup means rise significantly (min z >= gate)
    l_mean, l_se = _mean_se(low_impr)
    h_mean, h_se = _mean_se(high_impr)
    z_low = _z(l_mean, l_se)
    z_high = _z(h_mean, h_se)
    head_z = min(z_low, z_high)
    g3 = (l_mean > 0.0) and (h_mean > 0.0) and (head_z >= SIGMA_GATE)

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
        "proposal": 148,
        "seed": SEED,
        "sigma_gate": SIGMA_GATE,
        "n": N,
        "r": R,
        "params": {
            "t_coarse": T_COARSE,
            "t_fine": T_FINE,
            "cons_tol": CONS_TOL,
        },
        "closed_form": {
            "low_before": 0.25,
            "low_after": 0.3,
            "high_before": 0.75,
            "high_after": 0.8,
            "low_improvement": 0.05,
            "high_improvement": 0.05,
            "pooled": 0.5,
        },
        "mean_low_before": r6(_mean(low_b)),
        "mean_low_after": r6(_mean(low_a)),
        "mean_high_before": r6(_mean(high_b)),
        "mean_high_after": r6(_mean(high_a)),
        "mean_n_migrated": r6(_mean(migrated)),
        "count_conserved": counts_ok,
        "g1_half_a_impr": r6(a_mean),
        "g1_half_b_impr": r6(b_mean),
        "g1_z": r6(z_g1),
        "g1_agreement": g1,
        "g2_pooled_impr": r6(p_mean),
        "g2_cons_max_rel": r6(cons_max_rel),
        "g2_z": r6(z_g2),
        "g2_control": g2,
        "g3_low_impr": r6(l_mean),
        "g3_low_z": r6(z_low),
        "g3_high_impr": r6(h_mean),
        "g3_high_z": r6(z_high),
        "g3_head_z": r6(head_z),
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
        f"(low half_a-half_b, z={results['g1_z']:+.2f}, |z|<{SIGMA_GATE})",
    )
    print(
        "G2 control      :",
        "PASS" if results["g2_control"] else "FAIL",
        f"(pooled impr={results['g2_pooled_impr']:+.6f}, "
        f"cons_max_rel={results['g2_cons_max_rel']:.2e}, "
        f"z={results['g2_z']:+.2f}, not-sig-positive z<{SIGMA_GATE})",
    )
    print(
        "G3 head         :",
        "PASS" if results["g3_head"] else "FAIL",
        f"(low impr={results['g3_low_impr']:+.4f} z={results['g3_low_z']:+.2f}, "
        f"high impr={results['g3_high_impr']:+.4f} z={results['g3_high_z']:+.2f}, "
        f"min z={results['g3_head_z']:+.2f}>={SIGMA_GATE})",
    )
    print("all_pass        :", results["all_pass"], "first_failing_gate:", results["first_failing_gate"])
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
