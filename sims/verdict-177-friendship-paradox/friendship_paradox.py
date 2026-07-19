"""
PROPOSAL 164 — friendship paradox: your friends have more friends than you do, and the gap is exactly the degree variance-to-mean ratio.

PHENOMENON: Pick a random person in a social network, then pick a random one of
their friends. On average that friend has strictly MORE friends than the random
person does. Averaged over the endpoints of a uniformly random friendship, a
person's degree is E[k] + Var(k)/E[k] -- the mean degree plus the degree
variance divided by the mean -- which exceeds the mean degree E[k] whenever the
degrees are not all equal (Feld 1991, "Why Your Friends Have More Friends Than
You Do").

FOLK BELIEF (inverted here): "I am about as popular as my friends; on average my
friend count and my friends' friend counts are the same." False for every
network with any degree spread. Popular people are over-represented among the
friends of others (a high-degree node is a friend of many), so sampling a person
BY FOLLOWING A FRIENDSHIP is size-biased toward high degree -- the same
length/inspection-bias mechanism as the waiting-time paradox. The bias is not a
rounding error; it is exactly Var(k)/E[k].

THESIS: For a degree sequence {k_i}, the mean degree of a random PERSON is
mu = mean(k). The mean degree of a random FRIEND (a uniformly random endpoint of
a uniformly random edge) is nu = sum(k_i^2)/sum(k_i) = <k^2>/<k> = mu + Var/mu.
The friendship-paradox gap nu - mu = Var(k)/mu is >= 0, strict for Var > 0, and
GROWS with the heaviness of the degree tail -- the same network, two sampling
rules, a systematic gap set by the variance-to-mean ratio.

FORMAL MODEL: N node degrees k_i = max(1, round(scale * Pareto(alpha))) drawn iid
(a heavy-tailed but finite-variance social degree distribution, alpha > 2). A
random friend is drawn size-biased: node i with probability k_i / sum(k_j), which
is the exact law of a uniformly random edge-endpoint. mu, nu, and Var are
population functionals of the drawn sequence; the size-biased Monte-Carlo mean
estimates nu with genuine sampling noise.

PRE-REGISTERED GATES (z_gate = 3.0, R independent networks of N nodes each):
  G1  paradox-positive: across R networks the friend-mean-minus-person-mean gap
      nu - mu is reliably > 0, rejecting the equal-popularity null at >= 3 sigma
      (every network's gap > 0; z = mean(gap)/SE well past 3).
  G2  mechanism-is-size-bias: a size-biased Monte-Carlo estimate of the friend
      mean (TRIALS random edge-endpoints per network) matches the closed form
      <k^2>/<k> within sampling error, |z| < 3 -- validating that the paradox IS
      length-biased sampling, not an artifact of the closed form.
  G3  robust-under-shift: with a HEAVIER-tailed distribution (smaller alpha) the
      paradox survives at >= 3 sigma AND the gap is strictly LARGER than the base
      condition -- the gap scales with the variance-to-mean ratio as predicted.

DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (P127+ compact-canonical):
the results dict carries no digest field; its own canonical sha256 is printed to
stdout after a pretty indent=2 dump; nothing is written to disk.
"""
import math
import json
import hashlib
import random

SEED = 20260717
Z_GATE = 3.0
R = 40
N = 4000
TRIALS = 20000
ALPHA_BASE = 3.5
ALPHA_SHIFT = 2.6
DEG_SCALE = 2.0


def _degrees(rng, n, alpha, scale):
    ds = []
    for _ in range(n):
        d = int(round(scale * rng.paretovariate(alpha)))
        if d < 1:
            d = 1
        ds.append(d)
    return ds


def _moments(ds):
    n = len(ds)
    s1 = 0
    s2 = 0
    for d in ds:
        s1 += d
        s2 += d * d
    mu = s1 / n
    nu = s2 / s1  # sum(k^2)/sum(k) = <k^2>/<k>
    var = s2 / n - mu * mu
    return mu, nu, var, s1


def _third_moment_ratio(ds, s1):
    s3 = 0
    for d in ds:
        s3 += d * d * d
    return s3 / s1  # <k^3>/<k>, the 2nd moment of the size-biased law


def _sizebiased_mean(rng, ds, trials):
    picks = rng.choices(ds, weights=ds, k=trials)
    return sum(picks) / trials


def _agg(vals):
    n = len(vals)
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / (n - 1)
    se = math.sqrt(var / n)
    return mean, se


def run():
    rng = random.Random(SEED)

    # --- base condition (alpha = ALPHA_BASE) ---
    gaps = []
    varmu = []
    identity_resid = []
    g2_zparts = []
    for _ in range(R):
        ds = _degrees(rng, N, ALPHA_BASE, DEG_SCALE)
        mu, nu, var, s1 = _moments(ds)
        gaps.append(nu - mu)
        varmu.append(var / mu)
        identity_resid.append(abs((nu - mu) - var / mu))
        sb = _sizebiased_mean(rng, ds, TRIALS)
        m3 = _third_moment_ratio(ds, s1)
        var_sb = m3 - nu * nu
        se_sb = math.sqrt(var_sb / TRIALS)
        g2_zparts.append((sb - nu) / se_sb)

    g1_mean, g1_se = _agg(gaps)
    g1_z = g1_mean / g1_se
    g1_all_positive = all(g > 0.0 for g in gaps)
    g1_pass = (g1_z >= Z_GATE) and g1_all_positive

    varmu_mean, _ = _agg(varmu)
    identity_max_resid = max(identity_resid)

    # G2: mean standardized residual of the size-biased estimate vs closed form nu
    g2_z = (sum(g2_zparts) / R) * math.sqrt(R)
    g2_pass = abs(g2_z) < Z_GATE

    # --- G3: heavier-tailed shift (alpha = ALPHA_SHIFT) ---
    gaps_s = []
    for _ in range(R):
        ds = _degrees(rng, N, ALPHA_SHIFT, DEG_SCALE)
        mu, nu, var, s1 = _moments(ds)
        gaps_s.append(nu - mu)

    g3_mean, g3_se = _agg(gaps_s)
    g3_z = g3_mean / g3_se
    g3_all_positive = all(g > 0.0 for g in gaps_s)
    g3_bigger = g3_mean > g1_mean
    g3_pass = (g3_z >= Z_GATE) and g3_all_positive and g3_bigger

    gates = [g1_pass, g2_pass, g3_pass]
    first_failing = None
    for i, gp in enumerate(gates, start=1):
        if not gp:
            first_failing = i
            break
    all_pass = first_failing is None

    results = {
        "proposal": 164,
        "slot": "round-38 UNRELATED (network science / social-network sampling)",
        "seed": SEED,
        "sigma_gate": Z_GATE,
        "params": {
            "R": R,
            "N": N,
            "TRIALS": TRIALS,
            "alpha_base": ALPHA_BASE,
            "alpha_shift": ALPHA_SHIFT,
            "deg_scale": DEG_SCALE,
        },
        "g1_paradox_positive": {
            "gap_mean": g1_mean,
            "gap_se": g1_se,
            "equal_popularity_null": 0.0,
            "all_networks_positive": g1_all_positive,
            "z": g1_z,
            "pass": g1_pass,
        },
        "g2_mechanism_size_bias": {
            "mean_std_residual_z": g2_z,
            "closed_form": "nu = sum(k^2)/sum(k) = <k^2>/<k>",
            "note": "two-sided match test; PASS when |z| < 3",
            "pass": g2_pass,
        },
        "g3_robust_shift": {
            "gap_mean": g3_mean,
            "gap_se": g3_se,
            "gap_mean_base": g1_mean,
            "heavier_tail_bigger_gap": g3_bigger,
            "all_networks_positive": g3_all_positive,
            "z": g3_z,
            "pass": g3_pass,
        },
        "theory": {
            "gap_equals_var_over_mean": "nu - mu = Var(k)/mu",
            "var_over_mean_mean_base": varmu_mean,
            "identity_max_abs_residual": identity_max_resid,
        },
        "gates": gates,
        "first_failing_gate": first_failing,
        "all_pass": all_pass,
    }
    return results


def _round_floats(o, ndigits=6):
    if isinstance(o, float):
        return round(o, ndigits)
    if isinstance(o, dict):
        return {k: _round_floats(v, ndigits) for k, v in o.items()}
    if isinstance(o, list):
        return [_round_floats(v, ndigits) for v in o]
    return o


def _canonical_sha256(o):
    payload = json.dumps(o, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main():
    r1 = _round_floats(run())
    r2 = _round_floats(run())
    h1 = _canonical_sha256(r1)
    h2 = _canonical_sha256(r2)
    assert h1 == h2, "non-deterministic: digests differ across in-process double-run"
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("Results-JSON sha256: " + h1)
    raise SystemExit(0 if r1["all_pass"] else 1)


if __name__ == "__main__":
    main()
