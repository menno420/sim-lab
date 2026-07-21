#!/usr/bin/env python3
"""
verify_258_prophet_inequality_threshold.py

PROPOSAL 258 - Prophet inequality (single-threshold 1/2 guarantee).

Claim: for independent nonnegative random variables X_1..X_n revealed in order,
the single-threshold stopping rule ALG_tau that accepts the first X_i >= tau
(and takes the last variable X_n if none is accepted), with threshold
tau = E[max_i X_i] / 2, satisfies

        E[ALG_tau]  >=  (1/2) * E[max_i X_i].

The constant 1/2 is optimal: a one-parameter family drives the ratio
E[ALG]/E[max] down to 1/2 for every online rule, and greedy take-first can do
as badly as 1/10 while the threshold rule stays at or above 1/2.

Four gates, each in its own direction:
  G1 EXACT          exact Fraction enumeration: the guarantee holds across a
                    sweep of instances; the exact headline values reproduce;
                    threshold-necessity fact (take-first ratio 1/10) holds.
  G2 MC AGREEMENT   a seeded Monte-Carlo estimate of E[ALG_tau] agrees with the
                    exact value at |z| < 3 (iid draws -> honest plain SE).
  G3 INVARIANCE     positive-scale invariance of the ratio E[ALG_tau]/E[max]
                    under X -> lambda*X for lambda > 0 (exact).
  G4 FALSIFIABILITY the naive foil "the gambler matches the prophet"
                    (E[ALG_tau] == E[max]) is rejected at large |z| on the same
                    MC sample; the tight family confirms 1/2 cannot be improved.

stdlib only. Deterministic: in-process double run identical AND a separate
re-invocation byte-identical.
"""

from fractions import Fraction
import hashlib, itertools, json, math, random, sys

SEED = 20260721


def enumerate_support(vars_):
    """Yield (value_tuple, joint_prob) over the product support of independent vars."""
    for combo in itertools.product(*vars_):
        prob = Fraction(1)
        for _, p in combo:
            prob *= p
        yield tuple(v for v, _ in combo), prob


def emax(vars_):
    """Exact E[max_i X_i]."""
    return sum(prob * max(vals) for vals, prob in enumerate_support(vars_))


def alg_value(vals, tau):
    """Threshold rule: accept the first value >= tau, else take the last variable."""
    for v in vals:
        if v >= tau:
            return v
    return vals[-1]


def ealg(vars_, tau):
    """Exact E[ALG_tau]."""
    return sum(prob * alg_value(vals, tau) for vals, prob in enumerate_support(vars_))


def ealg_takefirst(vars_):
    """Foil policy: always accept the first offer X_1."""
    return sum(prob * vals[0] for vals, prob in enumerate_support(vars_))


def sample_var(rng, d):
    u = rng.random()
    acc = 0.0
    for v, p in d:
        acc += float(p)
        if u < acc:
            return v
    return d[-1][0]


def mc_ealg(vars_, tau, N, seed):
    """Seeded MC estimate of E[ALG_tau]; returns exact (mean, var) as Fractions."""
    rng = random.Random(seed)
    s = Fraction(0)
    s2 = Fraction(0)
    for _ in range(N):
        vals = tuple(sample_var(rng, d) for d in vars_)  # sample all vars, fixed order
        a = alg_value(vals, tau)
        s += a
        s2 += a * a
    mean = s / N
    var = s2 / N - mean * mean
    return mean, var


def fs(x):
    return "%d/%d" % (x.numerator, x.denominator)


ZERO = Fraction(0)


def generic_instance():
    return [
        [(Fraction(1), Fraction(1, 2)), (ZERO, Fraction(1, 2))],
        [(Fraction(2), Fraction(1, 2)), (ZERO, Fraction(1, 2))],
    ]


def tight_instance(M):
    return [
        [(Fraction(1), Fraction(1))],
        [(Fraction(M), Fraction(1, M)), (ZERO, Fraction(M - 1, M))],
    ]


def teeth_instance():
    # threshold necessity: 1 (sure) then 10 (sure)
    return [
        [(Fraction(1), Fraction(1))],
        [(Fraction(10), Fraction(1))],
    ]


def compute():
    results = {
        "claim": ("prophet inequality: single-threshold rule with tau=E[max]/2 "
                  "accepting the first X_i>=tau (else the last) satisfies "
                  "E[ALG]>=(1/2)E[max]; the constant 1/2 is optimal"),
        "seed": SEED,
    }

    # ---------- G1 EXACT ----------
    instances = ([("generic", generic_instance())]
                 + [("tight_M%d" % M, tight_instance(M)) for M in (2, 3, 4, 5)]
                 + [("teeth_1_then_10", teeth_instance())])
    g1_checks = []
    g1_ok = True
    for name, vs in instances:
        Mx = emax(vs)
        tau = Mx / 2
        A = ealg(vs, tau)
        guarantee = A >= Mx / 2
        g1_ok = g1_ok and guarantee
        g1_checks.append({
            "instance": name, "E_max": fs(Mx), "tau": fs(tau),
            "E_alg": fs(A), "ratio": fs(A / Mx), "guarantee_ge_half": guarantee,
        })
    # exact headline assertions
    gM = emax(generic_instance()); gA = ealg(generic_instance(), gM / 2)
    assert gM == Fraction(5, 4) and gA == Fraction(1) and gA / gM == Fraction(4, 5)
    t4M = emax(tight_instance(4)); t4A = ealg(tight_instance(4), t4M / 2)
    assert t4M == Fraction(7, 4) and t4A == Fraction(1) and t4A / t4M == Fraction(4, 7)
    teM = emax(teeth_instance()); teA = ealg(teeth_instance(), teM / 2)
    assert teM == Fraction(10) and teA == Fraction(10) and teA / teM == Fraction(1)
    # threshold necessity: greedy take-first is only 1/10 on the teeth instance
    tf_ratio = ealg_takefirst(teeth_instance()) / teM
    assert tf_ratio == Fraction(1, 10) and tf_ratio < Fraction(1, 2)
    results["G1_exact"] = {
        "pass": g1_ok, "checks": g1_checks,
        "threshold_necessity_takefirst_ratio": fs(tf_ratio),
    }

    # ---------- G2 MC AGREEMENT ----------
    N = 200000
    tau_g = gM / 2
    mean, var = mc_ealg(generic_instance(), tau_g, N, SEED)
    mean_f = float(mean)
    se = math.sqrt(float(var) / N)
    exact_A = float(gA)  # 1.0
    z = (mean_f - exact_A) / se
    g2_pass = abs(z) < 3
    results["G2_mc_agreement"] = {
        "instance": "generic", "N": N, "seed": SEED,
        "exact_E_alg": fs(gA), "mc_mean": "%.10f" % mean_f,
        "se": "%.10f" % se, "z": "%.6f" % z, "pass": g2_pass,
    }

    # ---------- G3 INVARIANCE (positive scale) ----------
    base_ratio = gA / gM  # 4/5
    g3_ok = True
    g3_lam = []
    for lam in (Fraction(2), Fraction(3), Fraction(100), Fraction(1, 7)):
        scaled = [[(v * lam, p) for v, p in d] for d in generic_instance()]
        sM = emax(scaled); sA = ealg(scaled, sM / 2)
        r = sA / sM
        ok = r == base_ratio
        g3_ok = g3_ok and ok
        g3_lam.append({"lambda": fs(lam), "ratio": fs(r), "ok": ok})
    results["G3_invariance"] = {
        "pass": g3_ok, "base_ratio": fs(base_ratio), "lambdas": g3_lam,
    }

    # ---------- G4 FALSIFIABILITY ----------
    foil_target = float(gM)  # 1.25: "gambler matches prophet"
    z_foil = (mean_f - foil_target) / se
    foil_rejected = abs(z_foil) > 6
    tight_ratios = []
    for M in (2, 3, 4, 5):
        vs = tight_instance(M); Mx = emax(vs); A = ealg(vs, Mx / 2)
        tight_ratios.append({"M": M, "ratio": fs(A / Mx)})
    r2 = ealg(tight_instance(2), emax(tight_instance(2)) / 2) / emax(tight_instance(2))
    r5 = ealg(tight_instance(5), emax(tight_instance(5)) / 2) / emax(tight_instance(5))
    monotone_toward_half = (r5 < r2) and (r5 > Fraction(1, 2)) and (r2 > Fraction(1, 2))
    g4_pass = foil_rejected and monotone_toward_half
    results["G4_falsifiability"] = {
        "foil": "gambler matches prophet: E[ALG]==E[max]",
        "foil_target": "%.10f" % foil_target, "z_foil": "%.6f" % z_foil,
        "foil_rejected": foil_rejected, "tight_family_ratios": tight_ratios,
        "monotone_toward_half": monotone_toward_half, "pass": g4_pass,
    }

    all_pass = g1_ok and g2_pass and g3_ok and g4_pass
    first_fail = None
    for k in ("G1_exact", "G2_mc_agreement", "G3_invariance", "G4_falsifiability"):
        if not results[k]["pass"]:
            first_fail = k
            break
    results["all_gates_pass"] = all_pass
    results["first_failing_gate"] = first_fail
    return results


def digest(results):
    blob = json.dumps(results, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def main():
    if "--selfcheck" in sys.argv:
        d1 = digest(compute())
        d2 = digest(compute())
        assert d1 == d2, "NON-DETERMINISTIC"
        print("selfcheck OK " + d1)
        return
    results = compute()
    print(json.dumps(results, sort_keys=True, indent=2))
    print("results_sha256=" + digest(results))


if __name__ == "__main__":
    main()
