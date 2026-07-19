#!/usr/bin/env python3
"""
PROPOSAL 161 -- Palm's theorem / M/G/inf repair-pipeline insensitivity: the
spares you must hold depend on the MEAN repair time, not its variance.

PHENOMENON: In an M/G/inf queue (Poisson unit-failure arrivals at rate lam,
each failed unit independently in repair for an i.i.d. time S), the stationary
number of units in repair N is Poisson with mean lam*E[S] -- INSENSITIVE to the
shape of the repair-time distribution beyond its mean (Palm's theorem, 1938;
the foundation of Sherbrooke's METRIC spares model, 1968). So the pipeline you
stock spares against is fixed by the offered load lam*E[S] alone; cutting
repair-time VARIABILITY while holding the mean fixed does NOT reduce the spares
you need -- only the mean repair time (or the failure rate) moves the pipeline.

FOLK BELIEF (inverted here): "erratic, high-variance repair times force you to
hold more spares -- smooth the repair process and you can stock fewer." For a
WAITING line (finite servers, M/G/1) variance does tax you: Pollaczek-Khinchine
wait ~ (1+CV^2)/2. But the ample-server REPAIR PIPELINE is variance-insensitive:
same mean, same Poisson pipeline, same spares.

PRE-REGISTERED GATES (z_gate=3.0, R=30 replications, relerr ceiling 0.05):
  G1 pipeline-is-load: measured E[N] matches the offered load lam*E[S] within
     the ceiling at >=3 sigma (Little's law for the M/G/inf pipeline).
  G2 variance-insensitivity (the head): under a HIGH-variance repair law
     (lognormal, CV=3), the pipeline's index of dispersion Var(N)/E[N] stays at
     the Poisson value 1.0 within the ceiling at >=3 sigma -- repair variability
     does NOT inflate the pipeline. Readout: the M/G/1 wait multiplier
     (1+CV^2)/2 for the same CV, which the pipeline shows none of.
  G3 distribution-free: across three repair laws of IDENTICAL mean
     (deterministic CV=0, exponential CV=1, lognormal CV=3), the pipeline mean
     AND dispersion index agree within the ceiling at >=3 sigma -- the spares
     requirement is the same for all three.

DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. SEED pinned; two
in-process runs asserted identical; results dict plus its compact-canonical
sha256 printed to stdout (floats 6 dp); nothing written to disk. Stdlib only.
"""

import hashlib
import json
import math
import random

SEED = 20260717
Z_GATE = 3.0
R = 30
LAM = 1.0          # Poisson unit-failure arrival rate
MEAN_S = 10.0      # mean repair time E[S]
HORIZON = 60000    # integer observation horizon
WARMUP = 8000      # discarded warm-up instants
CV_HI = 3.0        # coefficient of variation of the high-variance repair law
CEIL = 0.05        # relative-error ceiling for the match gates

LOAD = LAM * MEAN_S   # offered load = pipeline mean E[N] (Palm: Poisson(LOAD))


def _repair_det(rng):
    return MEAN_S


def _repair_exp(rng):
    return rng.expovariate(1.0 / MEAN_S)


def _repair_logn(rng):
    # lognormal with mean MEAN_S and coefficient of variation CV_HI
    sigma2 = math.log(1.0 + CV_HI * CV_HI)
    sigma = math.sqrt(sigma2)
    mu = math.log(MEAN_S) - 0.5 * sigma2
    return rng.lognormvariate(mu, sigma)


def _pipeline_stats(seed, repair):
    """Simulate an M/G/inf repair pipeline; return (mean_N, var_N, disp) for
    the number in repair sampled at integer instants post-warmup."""
    rng = random.Random(seed)
    diff = [0] * (HORIZON + 2)
    t = 0.0
    while True:
        t += rng.expovariate(LAM)
        if t >= HORIZON:
            break
        s = repair(rng)
        lo = int(math.ceil(t))
        hi = int(math.ceil(t + s)) - 1   # last integer instant k with k < t+s
        if hi < 0:
            continue
        if lo < 0:
            lo = 0
        if lo > HORIZON:
            continue
        if hi > HORIZON:
            hi = HORIZON
        diff[lo] += 1
        diff[hi + 1] -= 1
    n = 0
    cnt = 0
    s1 = 0.0
    s2 = 0.0
    for k in range(HORIZON + 1):
        n += diff[k]
        if k >= WARMUP:
            cnt += 1
            s1 += n
            s2 += n * n
    mean_n = s1 / cnt
    var_n = s2 / cnt - mean_n * mean_n
    disp = var_n / mean_n if mean_n > 0 else float("inf")
    return mean_n, var_n, disp


def _agg(vals):
    m = len(vals)
    mean = sum(vals) / m
    var = sum((v - mean) ** 2 for v in vals) / (m - 1)
    se = math.sqrt(var / m)
    return mean, se


def _rnd(x):
    return round(x, 6)


def run():
    load_relerrs = []      # G1: exp law, |mean_N - LOAD| / LOAD
    disp_hi_relerrs = []   # G2: logn CV=3 law, |disp - 1|
    g3_metrics = []        # G3: max cross-law spread (mean + disp) vs targets
    for rep in range(R):
        base = SEED + rep * 101
        m_det, _, d_det = _pipeline_stats(base + 1, _repair_det)
        m_exp, _, d_exp = _pipeline_stats(base + 2, _repair_exp)
        m_log, _, d_log = _pipeline_stats(base + 3, _repair_logn)

        load_relerrs.append(abs(m_exp - LOAD) / LOAD)
        disp_hi_relerrs.append(abs(d_log - 1.0))

        means = [m_det, m_exp, m_log]
        disps = [d_det, d_exp, d_log]
        mean_spread = (max(means) - min(means)) / LOAD
        disp_gap = max(abs(d - 1.0) for d in disps)
        g3_metrics.append(max(mean_spread, disp_gap))

    l_mean, l_se = _agg(load_relerrs)
    g1_z = (CEIL - l_mean) / l_se
    g1 = l_mean < CEIL and g1_z >= Z_GATE

    d_mean, d_se = _agg(disp_hi_relerrs)
    g2_z = (CEIL - d_mean) / d_se
    g2 = d_mean < CEIL and g2_z >= Z_GATE

    g3_mean, g3_se = _agg(g3_metrics)
    g3_z = (CEIL - g3_mean) / g3_se
    g3 = g3_mean < CEIL and g3_z >= Z_GATE

    wait_tax = 0.5 * (1.0 + CV_HI * CV_HI)   # M/G/1 Pollaczek-Khinchine multiplier

    gates = [g1, g2, g3]
    first_fail = None
    for i, ok in enumerate(gates, start=1):
        if not ok:
            first_fail = i
            break
    all_pass = first_fail is None

    results = {
        "proposal": 161,
        "slot": "round-38 FLEET (fleet-ops spares / maintenance pipeline)",
        "seed": SEED,
        "sigma_gate": Z_GATE,
        "params": {
            "R": R,
            "lam": LAM,
            "mean_s": MEAN_S,
            "horizon": HORIZON,
            "warmup": WARMUP,
            "cv_hi": CV_HI,
            "ceiling": CEIL,
            "load": LOAD,
        },
        "g1_pipeline_is_load": {
            "load_relerr_mean": _rnd(l_mean),
            "se": _rnd(l_se),
            "ceiling": CEIL,
            "z": _rnd(g1_z),
            "pass": g1,
        },
        "g2_variance_insensitive": {
            "disp_relerr_mean": _rnd(d_mean),
            "se": _rnd(d_se),
            "ceiling": CEIL,
            "z": _rnd(g2_z),
            "pass": g2,
        },
        "g3_distribution_free": {
            "spread_mean": _rnd(g3_mean),
            "se": _rnd(g3_se),
            "ceiling": CEIL,
            "z": _rnd(g3_z),
            "pass": g3,
        },
        "readout": {
            "mg1_wait_tax_multiplier": _rnd(wait_tax),
        },
        "gates": gates,
        "first_failing_gate": first_fail,
        "all_pass": all_pass,
    }
    return results


def main():
    results = run()
    again = run()
    assert results == again, "non-deterministic: in-process double run diverged"

    payload = json.dumps(results, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()

    print("Palm / M/G/inf repair-pipeline insensitivity verifier -- stdlib, SEED pinned")
    print(f"  load (E[N]=lam*E[S]) = {LOAD:.6f}")
    print(f"  G1 pipeline-is-load     load_relerr_mean={results['g1_pipeline_is_load']['load_relerr_mean']:.6f}  z={results['g1_pipeline_is_load']['z']:+.6f}  (ceiling {CEIL})")
    print(f"  G2 variance-insensitive disp_relerr_mean={results['g2_variance_insensitive']['disp_relerr_mean']:.6f}  z={results['g2_variance_insensitive']['z']:+.6f}  (ceiling {CEIL})")
    print(f"  G3 distribution-free    spread_mean={results['g3_distribution_free']['spread_mean']:.6f}  z={results['g3_distribution_free']['z']:+.6f}  (ceiling {CEIL})")
    print(f"  M/G/1 wait tax at CV={CV_HI}: (1+CV^2)/2 = {results['readout']['mg1_wait_tax_multiplier']:.6f}x  (the pipeline shows NONE of it)")
    print(f"  gates: G1={results['gates'][0]} G2={results['gates'][1]} G3={results['gates'][2]}  all_pass={results['all_pass']}")
    print()
    print(json.dumps(results, indent=2, sort_keys=True))
    print(f"Results-JSON sha256: {digest}")
    return 0 if results["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
