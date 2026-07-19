#!/usr/bin/env python3
"""PROPOSAL 155 - speedrun record drought (harmonic-law record slowdown).

PHENOMENON (one line)
    In any i.i.d. sequence of speedrun attempt times, the k-th attempt sets a new
    personal-best record (a strictly-new running minimum, lower=better) with
    probability EXACTLY 1/k - independent of how fast or how variable the runner
    is. So after N attempts the expected number of PB records is the harmonic
    number H_N = sum_{k=1}^N 1/k (~ ln N + gamma). Records accumulate only
    LOGARITHMICALLY: squaring the attempt count (x100) multiplies PB records by
    only ~H(N2)/H(N1) (~1.887), not by 100 - and the cadence is distribution-free.

FOLK BELIEF
    "PBs dry up because I'm plateauing / the game got harder / I lost motivation."
    A drought of new records feels like a signal about the RUNNER. False, under
    the i.i.d.-stationary null: even a perfectly stationary runner whose skill and
    variance never change sees records arrive at rate 1/k - the k-th attempt has
    only a 1/k chance of beating all k-1 before it. The drought is the DEFAULT, a
    property of running minima of exchangeable draws, not evidence of a plateau.
    The right baseline for "am I actually improving" is the harmonic law, not a
    linear expectation of "more attempts -> proportionally more PBs."

GAME-DESIGN / ANALYTICS THESIS (reasoned to fuller form - Q-0254 duty)
    Model an attempt log as N i.i.d. draws from any continuous base time
    distribution. A PB is a strictly-new running minimum; attempt 1 is the first
    PB by definition. The indicator "attempt k is a record" has probability 1/k
    and the indicators are INDEPENDENT across k (Renyi 1962), because whether the
    minimum of the first k draws falls in position k is a statement about the RANK
    of an exchangeable sequence and ignores the values entirely. Hence the record
    COUNT after N is a sum of independent Bernoulli(1/k), with mean H_N and
    variance H_N - sum 1/k^2. Two consequences a leaderboard/telemetry designer
    must price in: (1) PB cadence is LOGARITHMIC - to double a runner's lifetime
    PB count they must SQUARE their attempts, so a "records per week" metric decays
    like 1/t and a drought is expected, not alarming; (2) the law is
    DISTRIBUTION-FREE - a heavy-tailed grind (Pareto) and a light-tailed one
    (Exponential) produce the SAME expected record count H_N, so a PB-rate baseline
    needs no fit to the runner's time distribution. Measure a real improving player
    as a DEVIATION ABOVE this stationary harmonic null, not against a linear one.

FORMAL MODEL (committed constants)
    Per Monte-Carlo trial, draw N2 i.i.d. attempt times from a base distribution;
    record = strictly-new running minimum (attempt 1 always counts). Capture the
    record count at checkpoint k=N1 and at k=N2 within the SAME sequence (no extra
    draws). H(n) = exact sum_{k=1}^n 1/k. G1/G2 use Exponential(1.0); G3 uses a
    heavy-tailed Pareto(2.5) - a genuinely different shape, same running-min logic.

PRE-REGISTERED GATES (APPROVE iff ALL hold, in order G1 -> G2 -> G3)
    G1 harmonic-law: mean(count@N2) matches H(N2) within |z| < 3, where
        z = (mean - H(N2)) / (sample_sd / sqrt(TRIALS)). The expected lifetime PB
        count is the harmonic number, not the attempt count.
    G2 log-slowdown (HEADLINE): the linear-accumulation null calibrated at N1
        predicts mean(count@N1) * (N2/N1) records at N2. PASS iff (a) observed
        mean(count@N2) is >= 3 sigma BELOW that linear prediction
        (z_linear = (linear_pred - mean@N2)/se(mean@N2) >= 3), AND (b) the observed
        ratio mean(count@N2)/mean(count@N1) matches H(N2)/H(N1) within |z| < 3 via
        the delta method - count@N1 and (count@N2 - count@N1) are INDEPENDENT
        (records in disjoint index ranges), so Cov(count@N1, count@N2) =
        Var(count@N1). Headline: squaring attempts (x100) multiplies records by
        only ~H(N2)/H(N1) (~1.887).
    G3 distribution-free: mean(count@N2) under the Pareto base matches the SAME
        H(N2) within |z| < 3. The cadence does not depend on the time distribution.

DIGEST POSTURE
    WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY, P127+ compact-canonical twist:
    the results dict carries NO digest field; main() rounds every float to 6 dp,
    hashes the compact-canonical (sorted-keys, comma/colon-separated) JSON, and
    prints an indent=2 pretty dump then a `Results-JSON sha256:` line. In-process
    double-run must produce identical dicts (determinism assert). No JSON is written
    to disk. Reference: theory of records - Renyi 1962; Glick 1978 ("Breaking
    Records and Breaking Boards," Amer. Math. Monthly); Arnold-Balakrishnan-Nagaraja
    1998 ("Records").
"""
import math
import json
import hashlib
import random

SEED = 20260717

N1 = 100
N2 = 10000          # N2 = N1 ** 2
TRIALS = 4000
SIGMA_GATE = 3.0

DIST_G1G2 = "exponential(1.0)"
DIST_G3 = "pareto(2.5)"


def harmonic(n):
    """Exact H_n = sum_{k=1}^n 1/k."""
    s = 0.0
    for k in range(1, n + 1):
        s += 1.0 / k
    return s


def record_counts(rng, draw):
    """One trial: draw N2 i.i.d. times, count strictly-new running minima; return
    (count@N1, count@N2) captured within the SAME sequence."""
    cur_min = math.inf
    count = 0
    c1 = 0
    for k in range(1, N2 + 1):
        x = draw(rng)
        if x < cur_min:
            cur_min = x
            count += 1
        if k == N1:
            c1 = count
    return c1, count


def moments(values):
    """(mean, sample_variance) with the n-1 (unbiased) denominator."""
    n = len(values)
    m = sum(values) / n
    var = sum((v - m) ** 2 for v in values) / (n - 1)
    return m, var


def covariance(xs, ys, mx, my):
    """Sample covariance with the n-1 denominator."""
    n = len(xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n - 1)


def mc_pass(rng, draw):
    """Run TRIALS trials under one draw fn; return per-trial c1/c2 lists."""
    c1s = []
    c2s = []
    for _ in range(TRIALS):
        c1, c2 = record_counts(rng, draw)
        c1s.append(c1)
        c2s.append(c2)
    return c1s, c2s


def draw_exp(rng):
    return rng.expovariate(1.0)


def draw_pareto(rng):
    return rng.paretovariate(2.5)


def run():
    rng = random.Random(SEED)
    res = {}
    res["params"] = {
        "seed": SEED,
        "N1": N1,
        "N2": N2,
        "trials": TRIALS,
        "sigma_gate": SIGMA_GATE,
        "dist_g1g2": DIST_G1G2,
        "dist_g3": DIST_G3,
    }

    h_n1 = harmonic(N1)
    h_n2 = harmonic(N2)
    res["harmonic"] = {
        "H_N1": h_n1,
        "H_N2": h_n2,
        "ratio_H_N2_over_H_N1": h_n2 / h_n1,
    }

    # --- Exponential pass (feeds G1 and G2) ---
    exp_c1, exp_c2 = mc_pass(rng, draw_exp)
    mean_c1, var_c1 = moments(exp_c1)
    mean_c2, var_c2 = moments(exp_c2)
    cov_12 = covariance(exp_c1, exp_c2, mean_c1, mean_c2)
    se_c1 = math.sqrt(var_c1 / TRIALS)
    se_c2 = math.sqrt(var_c2 / TRIALS)
    sd_c2 = math.sqrt(var_c2)

    res["exp_pass"] = {
        "mean_count_N1": mean_c1,
        "sd_count_N1": math.sqrt(var_c1),
        "se_count_N1": se_c1,
        "mean_count_N2": mean_c2,
        "sd_count_N2": sd_c2,
        "se_count_N2": se_c2,
        "cov_count_N1_N2": cov_12,
        "var_count_N1_identity": var_c1,  # Cov(c1,c2)=Var(c1) since disjoint ranges
    }

    # G1 harmonic-law: mean(count@N2) matches H(N2) within |z| < 3.
    z_g1 = (mean_c2 - h_n2) / se_c2
    g1 = abs(z_g1) < SIGMA_GATE
    res["g1_harmonic_law"] = {
        "mean_count_N2": mean_c2,
        "H_N2": h_n2,
        "se": se_c2,
        "z": z_g1,
        "pass": g1,
    }

    # G2 log-slowdown (HEADLINE).
    # (a) linear-accumulation null calibrated at N1.
    linear_pred = mean_c1 * (N2 / N1)
    z_linear = (linear_pred - mean_c2) / se_c2
    # (b) observed ratio matches H(N2)/H(N1) via the delta method.
    ratio_obs = mean_c2 / mean_c1
    ratio_null = h_n2 / h_n1
    var_x1 = var_c1 / TRIALS  # Var of the sample mean count@N1
    var_x2 = var_c2 / TRIALS  # Var of the sample mean count@N2
    cov_x = cov_12 / TRIALS   # Cov of the two sample means
    # delta method for R = X2 / X1
    var_ratio = (
        var_x2 / (mean_c1 ** 2)
        + (mean_c2 ** 2) * var_x1 / (mean_c1 ** 4)
        - 2.0 * mean_c2 * cov_x / (mean_c1 ** 3)
    )
    se_ratio = math.sqrt(var_ratio)
    z_ratio = (ratio_obs - ratio_null) / se_ratio
    g2 = (z_linear >= SIGMA_GATE) and (abs(z_ratio) < SIGMA_GATE)
    res["g2_log_slowdown"] = {
        "linear_pred_count_N2": linear_pred,
        "mean_count_N2": mean_c2,
        "z_linear": z_linear,
        "ratio_observed": ratio_obs,
        "ratio_null_H_N2_over_H_N1": ratio_null,
        "se_ratio": se_ratio,
        "z_ratio": z_ratio,
        "headline_x100_attempts_multiplies_records_by": ratio_null,
        "pass": g2,
    }

    # --- Pareto pass (feeds G3) ---
    par_c1, par_c2 = mc_pass(rng, draw_pareto)
    mean_pc2, var_pc2 = moments(par_c2)
    se_pc2 = math.sqrt(var_pc2 / TRIALS)
    z_g3 = (mean_pc2 - h_n2) / se_pc2
    g3 = abs(z_g3) < SIGMA_GATE
    res["g3_distribution_free"] = {
        "dist": DIST_G3,
        "mean_count_N2": mean_pc2,
        "H_N2": h_n2,
        "se": se_pc2,
        "z": z_g3,
        "pass": g3,
    }

    gates = [
        {"id": "G1", "name": "harmonic_law", "pass": g1, "z": z_g1},
        {"id": "G2", "name": "log_slowdown", "pass": g2, "z": z_linear},
        {"id": "G3", "name": "distribution_free", "pass": g3, "z": z_g3},
    ]
    res["gates"] = gates
    res["all_pass"] = all(x["pass"] for x in gates)
    res["first_failing_gate"] = next((x["id"] for x in gates if not x["pass"]), None)
    return res


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
