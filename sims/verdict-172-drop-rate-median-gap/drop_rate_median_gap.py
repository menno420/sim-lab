#!/usr/bin/env python3
"""PROPOSAL 159 - drop-rate median gap (round-37 GAME slot).

PHENOMENON (one line)
    For an i.i.d. loot roll with per-attempt drop probability p, the number of
    attempts T until the first drop is Geometric(p): its MEAN is 1/p, but its
    MEDIAN is only ~ln2/p ~= 0.693/p and its MODE is 1. The "expected N tries"
    players anchor on is not the typical grind - it is the ~63rd percentile.

FOLK BELIEF (inverted here)
    "The drop rate is 1%, so it takes about 100 kills on average; if I have done
    100 and it has not dropped, I am exactly average / due for it."

GAME-DESIGN / ANALYTICS THESIS (reasoned to fuller form - Q-0254 duty)
    The Geometric(p) grind is heavily right-skewed. The typical (median) player
    gets the drop in ~0.693/p attempts - about 69% of the advertised mean - so
    at the mean itself a solid MAJORITY (P(T<=1/p) -> 1 - 1/e ~= 0.632) have
    already succeeded. The mean is dragged up by a fixed heavy tail:
    P(T > 3/p) -> e^-3 ~= 0.0498 - about 5% grind past triple the "expected"
    count no matter how the rate is tuned. All three landmarks (median/mean = ln2,
    mean-percentile = 1-1/e, tail = e^-k) are SCALE-FREE in p: rescaling the drop
    rate slides the whole distribution but never changes these ratios. And the
    process is memoryless - k prior misses do not raise the next roll above p, so
    "due" is a fallacy (disclosed as a crossover, not the head).

FORMAL MODEL (committed constants)
    T ~ Geometric(p) on {1,2,...}, P(T=k) = (1-p)^(k-1) * p.
    true_mean(p)    = 1/p
    exact_median(p) = ceil( ln2 / -ln(1-p) )                    (integer)
    P(T<=m)         = 1 - (1-p)^m                               (m = floor(1/p))
    Limits as p->0: median/mean -> ln2 = 0.6931..., P(T<=mean) -> 1-1/e = 0.6321...

PRE-REGISTERED GATES (APPROVE iff ALL hold, in order G1 -> G2 -> G3)
    G1 median-below-mean : MC (mean - median)/mean > 0 at >=3 sigma vs the
       symmetric null 0 (the grind is right-skewed), and the measured median/mean
       ratio matches the exact closed form within a 0.05 relative-error ceiling.
       Head: ratio ~= 0.69 (median is ~69% of the advertised mean).
    G2 mean-is-majority-percentile : MC fraction of grinds finishing by the true
       mean 1/p exceeds the 0.5 null at >=3 sigma (the "expected" count is already
       a majority outcome), and matches the exact P(T<=floor(1/p)) within a 0.05
       relative-error ceiling. Head: -> 1 - 1/e ~= 0.632 (the ~63rd percentile).
    G3 scale-free robustness : under a rarer shifted drop rate p'=0.005 both
       landmarks (median/mean ratio and mean-percentile) still hold at >=3 sigma -
       the skew is a property of the geometric law, not of one tuned rate.

DIGEST POSTURE
    WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY, P127+ compact-canonical twist: the
    results dict carries NO digest field; main() rounds every float to 6 dp,
    hashes the compact-canonical (sorted-keys, comma/colon-separated) JSON, and
    prints an indent=2 pretty dump then a `Results-JSON sha256:` line. In-process
    double-run must produce identical dicts (determinism assert). No JSON is
    written to disk. Reference: geometric / exponential distribution (mean vs
    median; CDF at the mean = 1 - 1/e).
"""
import math
import json
import hashlib
import random

SEED = 20260717
P_MAIN = 0.01           # advertised 1% drop
P_SHIFT = 0.005         # rarer shifted rate for the scale-free gate
TRIALS = 200000         # geometric draws per replication
R = 30                  # independent replications (for /se z-gates)
SIGMA_GATE = 3.0
CEILING = 0.05          # relative-error ceiling for the closed-form match gates


def geometric_draw(rng, p):
    # inverse-CDF geometric on {1,2,...}: k = ceil( ln(U) / ln(1-p) )
    u = rng.random()
    if u <= 0.0:
        u = 5e-324
    return int(math.ceil(math.log(u) / math.log1p(-p)))


def exact_median(p):
    return math.ceil(math.log(2.0) / (-math.log1p(-p)))


def exact_p_le_mean(p):
    m = math.floor(1.0 / p)
    return 1.0 - (1.0 - p) ** m


def _median(sorted_vals):
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 1:
        return float(sorted_vals[mid])
    return 0.5 * (sorted_vals[mid - 1] + sorted_vals[mid])


def _mean(vals):
    return sum(vals) / len(vals)


def _mean_se(vals):
    n = len(vals)
    mu = sum(vals) / n
    if n < 2:
        return mu, 0.0
    var = sum((v - mu) ** 2 for v in vals) / (n - 1)
    return mu, math.sqrt(var / n)


def _z(mu, se, null):
    if se == 0.0:
        return 0.0
    return (mu - null) / se


def measure(rng, p):
    true_mean = 1.0 / p
    ratio_reps = []       # median/mean per replication
    gap_reps = []         # (mean - median)/mean per replication
    frac_reps = []        # fraction of draws <= true_mean per replication
    for _ in range(R):
        draws = [geometric_draw(rng, p) for _ in range(TRIALS)]
        draws.sort()
        smean = _mean(draws)
        smed = _median(draws)
        ratio_reps.append(smed / smean)
        gap_reps.append((smean - smed) / smean)
        le = sum(1 for v in draws if v <= true_mean)
        frac_reps.append(le / TRIALS)
    ratio_mu, ratio_se = _mean_se(ratio_reps)
    gap_mu, gap_se = _mean_se(gap_reps)
    frac_mu, frac_se = _mean_se(frac_reps)
    return {
        "p": p,
        "true_mean": true_mean,
        "exact_median": exact_median(p),
        "exact_median_over_mean": exact_median(p) / true_mean,
        "exact_p_le_mean": exact_p_le_mean(p),
        "ratio_med_mean_mc": ratio_mu,
        "ratio_med_mean_se": ratio_se,
        "gap_mc": gap_mu,
        "gap_se": gap_se,
        "frac_le_mean_mc": frac_mu,
        "frac_le_mean_se": frac_se,
    }


def run():
    main_m = measure(random.Random(SEED), P_MAIN)
    shift_m = measure(random.Random(SEED + 1), P_SHIFT)

    g1_z = _z(main_m["gap_mc"], main_m["gap_se"], 0.0)
    g1_relerr = abs(main_m["ratio_med_mean_mc"] - main_m["exact_median_over_mean"]) / main_m["exact_median_over_mean"]
    g1_pass = (g1_z >= SIGMA_GATE) and (g1_relerr <= CEILING)

    g2_z = _z(main_m["frac_le_mean_mc"], main_m["frac_le_mean_se"], 0.5)
    g2_relerr = abs(main_m["frac_le_mean_mc"] - main_m["exact_p_le_mean"]) / main_m["exact_p_le_mean"]
    g2_pass = (g2_z >= SIGMA_GATE) and (g2_relerr <= CEILING)

    g3_z_skew = _z(shift_m["gap_mc"], shift_m["gap_se"], 0.0)
    g3_z_maj = _z(shift_m["frac_le_mean_mc"], shift_m["frac_le_mean_se"], 0.5)
    g3_relerr_ratio = abs(shift_m["ratio_med_mean_mc"] - shift_m["exact_median_over_mean"]) / shift_m["exact_median_over_mean"]
    g3_relerr_frac = abs(shift_m["frac_le_mean_mc"] - shift_m["exact_p_le_mean"]) / shift_m["exact_p_le_mean"]
    g3_z = min(g3_z_skew, g3_z_maj)
    g3_pass = (g3_z_skew >= SIGMA_GATE) and (g3_z_maj >= SIGMA_GATE) and (g3_relerr_ratio <= CEILING) and (g3_relerr_frac <= CEILING)

    gates = [
        {"id": "G1", "name": "median_below_mean", "pass": g1_pass, "z": g1_z},
        {"id": "G2", "name": "mean_is_majority_percentile", "pass": g2_pass, "z": g2_z},
        {"id": "G3", "name": "scale_free_robustness", "pass": g3_pass, "z": g3_z},
    ]
    first_failing = next((g["id"] for g in gates if not g["pass"]), None)
    all_pass = first_failing is None

    return {
        "proposal": 159,
        "slot": "round-37 GAME",
        "seed": SEED,
        "sigma_gate": SIGMA_GATE,
        "ceiling": CEILING,
        "params": {"p_main": P_MAIN, "p_shift": P_SHIFT, "trials": TRIALS, "replications": R},
        "limits": {
            "median_over_mean_ln2": math.log(2.0),
            "p_le_mean_1_minus_inv_e": 1.0 - math.exp(-1.0),
            "tail_3_over_p_inv_e3": math.exp(-3.0),
        },
        "main": main_m,
        "shift": shift_m,
        "g1_median_below_mean": {"z_skew": g1_z, "relerr_ratio": g1_relerr, "pass": g1_pass},
        "g2_mean_majority_percentile": {"z_majority": g2_z, "relerr_frac": g2_relerr, "pass": g2_pass},
        "g3_scale_free_robustness": {
            "z_skew": g3_z_skew,
            "z_majority": g3_z_maj,
            "relerr_ratio": g3_relerr_ratio,
            "relerr_frac": g3_relerr_frac,
            "pass": g3_pass,
        },
        "gates": gates,
        "first_failing_gate": first_failing,
        "all_pass": all_pass,
    }


def round_floats(o, ndigits=6):
    if isinstance(o, float):
        return round(o, ndigits)
    if isinstance(o, dict):
        return {k: round_floats(v, ndigits) for k, v in o.items()}
    if isinstance(o, list):
        return [round_floats(v, ndigits) for v in o]
    return o


def canonical_sha256(res):
    blob = json.dumps(round_floats(res, 6), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def main():
    res1 = run()
    res2 = run()
    h1 = canonical_sha256(res1)
    h2 = canonical_sha256(res2)
    assert h1 == h2, "non-deterministic: in-process double-run digests differ"
    print(json.dumps(round_floats(res1, 6), indent=2, sort_keys=True))
    print("Results-JSON sha256: " + h1)
    raise SystemExit(0 if res1["all_pass"] else 1)


if __name__ == "__main__":
    main()
