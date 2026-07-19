"""
PROPOSAL 160 — Cauchy no-averaging: the law of large numbers fails for infinite-variance data.

PHENOMENON: The sample mean of n independent standard-Cauchy measurements is itself
standard Cauchy for every n. Its dispersion does not shrink with n -- averaging never
concentrates. The 1/sqrt(n) error reduction the central limit theorem promises is a
finite-variance privilege; a distribution with no finite mean or variance forfeits it.

FOLK BELIEF (inverted here): "average more noisy readings and the estimate gets more
precise; the spread falls like 1/sqrt(n)." That is a theorem for finite variance; for a
heavy enough tail (Cauchy: undefined mean, infinite variance) it is simply false.

THESIS: Measured as a robust dispersion (half the interquartile range, IQR/2, which for
Cauchy(0, gamma) equals gamma exactly), the sample MEAN does not concentrate --
spread(mean, n) / spread(mean, 1) stays at 1, not 1/sqrt(n). By contrast the sample MEDIAN
does concentrate, its spread shrinking ~ 1/sqrt(n) (asymptotically pi/(2 sqrt(n)) in scale
units). Same data, same n: the estimator you pick decides whether averaging buys anything.

FORMAL MODEL: X_i ~ Cauchy(0, gamma) by inverse-CDF X = gamma * tan(pi * (U - 0.5)),
U ~ Uniform(0,1). Sample mean M_n = mean(X_1..X_n) ~ Cauchy(0, gamma) (stable, scale
invariant). Sample median has asymptotic law Normal(0, (pi*gamma)^2 / (4n)).

PRE-REGISTERED GATES (z_gate = 3.0, R = 30 replications, TRIALS sample-statistics each):
  G1  mean-does-not-concentrate: mean_ratio = spread(mean, n=100)/spread(mean, n=1)
      rejects the CLT-shrink null 1/sqrt(100)=0.1 at >=3 sigma (observed ~1, NOT 0.1).
  G2  median-does-concentrate: med_ratio = spread(median, n=100)/spread(median, n=1)
      rejects the no-concentration null 1.0 at >=3 sigma (observed ~1/sqrt(100), well
      below 1) -- the same sample, a concentrating estimator.
  G3  robust-under-shift: at gamma'=2.5, n'=200, mean-non-concentration (ratio rejects
      1/sqrt(200)) AND median-concentration (ratio rejects 1.0) both survive at >=3 sigma.

DIGEST POSTURE: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY (P127+ compact-canonical): the
results dict carries no digest field; its own canonical sha256 is printed to stdout after a
pretty indent=2 dump; nothing is written to disk.
"""
import math
import json
import hashlib
import random

SEED = 20260717
Z_GATE = 3.0
R = 30
TRIALS = 2000
GAMMA = 1.0
N_BASE = 1
N_AVG = 100
GAMMA_SHIFT = 2.5
N_SHIFT = 200


def _cauchy(rng, gamma):
    return gamma * math.tan(math.pi * (rng.random() - 0.5))


def _median(xs):
    ys = sorted(xs)
    m = len(ys)
    if m % 2 == 1:
        return ys[m // 2]
    return 0.5 * (ys[m // 2 - 1] + ys[m // 2])


def _spread(xs):
    ys = sorted(xs)
    m = len(ys)

    def q(p):
        idx = p * (m - 1)
        lo = int(math.floor(idx))
        hi = int(math.ceil(idx))
        if lo == hi:
            return ys[lo]
        frac = idx - lo
        return ys[lo] * (1.0 - frac) + ys[hi] * frac

    return 0.5 * (q(0.75) - q(0.25))


def _spread_of_mean(rng, n, gamma, trials):
    stats = []
    for _ in range(trials):
        s = 0.0
        for _ in range(n):
            s += _cauchy(rng, gamma)
        stats.append(s / n)
    return _spread(stats)


def _spread_of_median(rng, n, gamma, trials):
    stats = []
    for _ in range(trials):
        xs = [_cauchy(rng, gamma) for _ in range(n)]
        stats.append(_median(xs))
    return _spread(stats)


def _agg(vals):
    n = len(vals)
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / (n - 1)
    se = math.sqrt(var / n)
    return mean, se


def run():
    rng = random.Random(SEED)

    mean_ratios = []
    med_ratios = []
    for _ in range(R):
        sm1 = _spread_of_mean(rng, N_BASE, GAMMA, TRIALS)
        sm100 = _spread_of_mean(rng, N_AVG, GAMMA, TRIALS)
        sd1 = _spread_of_median(rng, N_BASE, GAMMA, TRIALS)
        sd100 = _spread_of_median(rng, N_AVG, GAMMA, TRIALS)
        mean_ratios.append(sm100 / sm1)
        med_ratios.append(sd100 / sd1)

    clt_null_avg = 1.0 / math.sqrt(N_AVG)
    mr_mean, mr_se = _agg(mean_ratios)
    g1_z = (mr_mean - clt_null_avg) / mr_se
    g1_pass = g1_z >= Z_GATE

    dr_mean, dr_se = _agg(med_ratios)
    g2_z = (1.0 - dr_mean) / dr_se
    g2_pass = g2_z >= Z_GATE

    shift_mean_ratios = []
    shift_med_ratios = []
    for _ in range(R):
        sm1 = _spread_of_mean(rng, N_BASE, GAMMA_SHIFT, TRIALS)
        smN = _spread_of_mean(rng, N_SHIFT, GAMMA_SHIFT, TRIALS)
        sd1 = _spread_of_median(rng, N_BASE, GAMMA_SHIFT, TRIALS)
        sdN = _spread_of_median(rng, N_SHIFT, GAMMA_SHIFT, TRIALS)
        shift_mean_ratios.append(smN / sm1)
        shift_med_ratios.append(sdN / sd1)

    clt_null_shift = 1.0 / math.sqrt(N_SHIFT)
    smr_mean, smr_se = _agg(shift_mean_ratios)
    g3_z_mean = (smr_mean - clt_null_shift) / smr_se
    sdr_mean, sdr_se = _agg(shift_med_ratios)
    g3_z_med = (1.0 - sdr_mean) / sdr_se
    g3_pass = (g3_z_mean >= Z_GATE) and (g3_z_med >= Z_GATE)

    median_scale_const = 0.6744897501960817 * math.pi / 2.0

    gates = [g1_pass, g2_pass, g3_pass]
    first_failing = None
    for i, gp in enumerate(gates, start=1):
        if not gp:
            first_failing = i
            break
    all_pass = first_failing is None

    results = {
        "proposal": 160,
        "slot": "round-37 UNRELATED (statistics-of-science / heavy-tailed inference)",
        "seed": SEED,
        "sigma_gate": Z_GATE,
        "params": {
            "R": R,
            "TRIALS": TRIALS,
            "gamma": GAMMA,
            "n_base": N_BASE,
            "n_avg": N_AVG,
            "gamma_shift": GAMMA_SHIFT,
            "n_shift": N_SHIFT,
        },
        "g1_mean_no_concentrate": {
            "mean_ratio": mr_mean,
            "se": mr_se,
            "clt_null": clt_null_avg,
            "z": g1_z,
            "pass": g1_pass,
        },
        "g2_median_concentrates": {
            "med_ratio": dr_mean,
            "se": dr_se,
            "no_concentration_null": 1.0,
            "clt_reference": clt_null_avg,
            "z": g2_z,
            "pass": g2_pass,
        },
        "g3_robust_shift": {
            "mean_ratio": smr_mean,
            "z_mean": g3_z_mean,
            "clt_null": clt_null_shift,
            "med_ratio": sdr_mean,
            "z_med": g3_z_med,
            "pass": g3_pass,
        },
        "readout": {
            "median_asymptotic_scale_const": median_scale_const,
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
