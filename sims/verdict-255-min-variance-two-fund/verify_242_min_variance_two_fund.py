#!/usr/bin/env python3
"""PROPOSAL 242 - Markowitz global minimum-variance portfolio & two-fund separation.

Claim (exact). For n risky assets with a positive-definite covariance matrix
Sigma, the global minimum-variance (GMV) portfolio -- the fully-invested
(weights sum to 1) portfolio of least return variance -- has weights
w* = Sigma^{-1} 1 / (1^T Sigma^{-1} 1) and variance sigma*^2 = 1/(1^T Sigma^{-1} 1).
Equivalently every asset's marginal contribution to variance is equalised at the
optimum: (Sigma w*)_i = sigma*^2 for every i. For two assets (variances s1^2,
s2^2, covariance s12): w1* = (s2^2 - s12)/(s1^2 + s2^2 - 2 s12) and
sigma*^2 = (s1^2 s2^2 - s12^2)/(s1^2 + s2^2 - 2 s12).

Headline exact rationals for Sigma = [[4, 1/2], [1/2, 1]] (s1^2=4, s2^2=1,
s12=1/2, correlation 1/4): w* = (1/8, 7/8) and sigma*^2 = 15/16. The GMV
variance 15/16 is STRICTLY BELOW even the lower-variance single asset (asset 2,
variance 1) and far below the naive equal-weight portfolio (variance 3/2).

Refutes two naive foils, each on the SAME Monte-Carlo sample:
  (F1) "equal weights 1/n are optimal (naive diversification)" -- the 1/2:1/2
       portfolio has variance 3/2 != 15/16;
  (F2) "just hold the single lowest-variance asset" -- asset 2 has variance
       1 > 15/16, so the diversified GMV strictly dominates it.

Two-fund separation (G3): the mean-variance efficient weight vector w(m) at
target mean return m is AFFINE in m, w(m) = g + h m, so any efficient portfolio
is an exact affine combination of two fixed funds.

SEED = 20260717. build_results() is a pure function of SEED and the module
constants: the Monte-Carlo sample is drawn from a fresh random.Random(SEED) in a
fixed order, exact rationals serialize via str(Fraction) and every float via a
fixed f"{v:.10f}" string, and no wall-clock / PID / unordered-set iteration
enters the hashed payload -- so an in-process double-run and a separate
re-invocation are byte-identical. The returns are iid independent draws (not a
correlated sample path), so the Gaussian sample-variance standard error
SE = sigma^2 * sqrt(2/N) is honest with no thinning required.

Four gates, each in its own direction:
  G1 EXACT      - two independent exact routes to (w*, sigma*^2) agree bit-for-
                  bit (fractions.Fraction): the two-asset closed form and the
                  general matrix form via an exact Fraction linear solve; across
                  a 2/3/4-asset SPD panel the FOC (Sigma w*)_i == sigma*^2 for
                  all i holds exactly. error_count must be 0.
  G2 MC AGREE   - draw N iid return vectors with covariance exactly Sigma
                  (Cholesky map of iid standard normals); the realised sample
                  variance of the GMV portfolio agrees with sigma*^2 at
                  |z| < Z_ACCEPT.
  G3 INVARIANCE - (i) scale-equivariance: Sigma -> k Sigma leaves w* identical
                  and scales sigma*^2 by exactly k (Fraction), and the MC z is
                  byte-identical under the sqrt(k) sample-path rescaling;
                  (ii) two-fund separation: w(m) affine in m, verified exactly
                  by w(m_C) == alpha w(m_A) + (1-alpha) w(m_B), and the GMV is
                  recovered on the frontier at m = B/A.
  G4 FALSIFY    - on the SAME MC sample, "equal weights are optimal" (variance
                  3/2) and "hold the single lowest-variance asset" (variance 1)
                  are both rejected against sigma*^2 at |z| >= Z_REJECT; and
                  exactly 3/2 != 15/16 and 1 != 15/16.

Stdlib only: json, hashlib, math, random, fractions.
"""

import json
import hashlib
import math
import random
from fractions import Fraction

SEED = 20260717

SIGMA2 = [[Fraction(4), Fraction(1, 2)],
          [Fraction(1, 2), Fraction(1)]]
SIGMA3 = [[Fraction(2), Fraction(1), Fraction(0)],
          [Fraction(1), Fraction(2), Fraction(1)],
          [Fraction(0), Fraction(1), Fraction(2)]]
SIGMA4 = [[Fraction(5), Fraction(1), Fraction(1), Fraction(0)],
          [Fraction(1), Fraction(4), Fraction(1), Fraction(1)],
          [Fraction(1), Fraction(1), Fraction(3), Fraction(1)],
          [Fraction(0), Fraction(1), Fraction(1), Fraction(2)]]
MU3 = [Fraction(1), Fraction(2), Fraction(3)]
SCALE_K = Fraction(4)
MC_N = 200_000
Z_ACCEPT = 3.0
Z_REJECT = 6.0


def mat_vec(M, v):
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def solve(M, b):
    """Solve M x = b exactly (Fraction) by Gauss-Jordan."""
    n = len(M)
    A = [[M[i][j] for j in range(n)] + [b[i]] for i in range(n)]
    for col in range(n):
        piv = next(r for r in range(col, n) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [x / pv for x in A[col]]
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [A[r][k] - f * A[col][k] for k in range(n + 1)]
    return [A[i][n] for i in range(n)]


def gmv(Sigma):
    n = len(Sigma)
    ones = [Fraction(1)] * n
    x = solve(Sigma, ones)
    A = sum(x)
    w = [xi / A for xi in x]
    var = Fraction(1) / A
    return w, var


def gmv_two_asset(s1sq, s2sq, s12):
    D = s1sq + s2sq - 2 * s12
    w1 = (s2sq - s12) / D
    var = (s1sq * s2sq - s12 * s12) / D
    return w1, var


def _stdnorm_stream(rng, count):
    out = []
    while len(out) < count:
        u1 = rng.random()
        u2 = rng.random()
        if u1 <= 0.0:
            u1 = 1e-16
        r = math.sqrt(-2.0 * math.log(u1))
        out.append(r * math.cos(2.0 * math.pi * u2))
        out.append(r * math.sin(2.0 * math.pi * u2))
    return out[:count]


def mc_portfolio_sample(seed, n):
    """iid 2-asset returns with covariance exactly SIGMA2 via Cholesky
    L=[[2,0],[1/4, sqrt(15)/4]]; second moments (mean 0 known) of the GMV,
    equal-weight, and single-asset-2 portfolios from the SAME draws."""
    rng = random.Random(seed)
    L11, L21, L22 = 2.0, 0.25, math.sqrt(15.0) / 4.0
    zs = _stdnorm_stream(rng, 2 * n)
    w1, w2 = 1.0 / 8.0, 7.0 / 8.0
    sum_gmv = sum_eq = sum_a2 = 0.0
    for i in range(n):
        z1 = zs[2 * i]
        z2 = zs[2 * i + 1]
        r1 = L11 * z1
        r2 = L21 * z1 + L22 * z2
        x_gmv = w1 * r1 + w2 * r2
        x_eq = 0.5 * r1 + 0.5 * r2
        x_a2 = r2
        sum_gmv += x_gmv * x_gmv
        sum_eq += x_eq * x_eq
        sum_a2 += x_a2 * x_a2
    return {"s2_gmv": sum_gmv / n, "s2_eq": sum_eq / n,
            "s2_a2": sum_a2 / n, "n": n}


def _zvar(s2_hat, sigma2, n):
    se = sigma2 * math.sqrt(2.0 / n)
    return (s2_hat - sigma2) / se


def _f(v):
    return f"{v:.10f}"


def gate1_exact():
    error_count = 0
    s1sq, s2sq, s12 = SIGMA2[0][0], SIGMA2[1][1], SIGMA2[0][1]
    w_cf1, var_cf = gmv_two_asset(s1sq, s2sq, s12)
    w_m, var_m = gmv(SIGMA2)
    cf_matches = (w_m[0] == w_cf1) and (w_m[1] == 1 - w_cf1) and (var_m == var_cf)
    if not cf_matches:
        error_count += 1
    panel = []
    for name, Sig in [("2asset", SIGMA2), ("3asset", SIGMA3), ("4asset", SIGMA4)]:
        w, var = gmv(Sig)
        Sw = mat_vec(Sig, w)
        foc_ok = all(x == var for x in Sw) and (sum(w) == 1)
        if not foc_ok:
            error_count += 1
        panel.append({"matrix": name, "w": [str(x) for x in w], "var": str(var),
                      "Sigma_w": [str(x) for x in Sw], "foc_equalised": foc_ok,
                      "weights_sum_one": (sum(w) == 1)})
    ok = (error_count == 0)
    return ok, {"closed_form_matches_matrix_2asset": cf_matches,
                "w1_star": str(w_cf1), "w2_star": str(1 - w_cf1),
                "sigma_star_sq": str(var_cf), "panel": panel,
                "error_count": error_count,
                "pass_if": "closed form == matrix form AND (Sigma w*)_i == sigma*^2 for all i, all panels"}


def gate2_mc_agreement(sample):
    var_gmv = float(gmv(SIGMA2)[1])
    z = _zvar(sample["s2_gmv"], var_gmv, sample["n"])
    ok = abs(z) < Z_ACCEPT
    return ok, {"sigma_star_sq_float": _f(var_gmv), "s2_gmv_hat": _f(sample["s2_gmv"]),
                "n": sample["n"], "z": _f(z), "z_accept": Z_ACCEPT, "ok": ok,
                "pass_if": "abs(z) < Z_ACCEPT (GMV sample variance agrees with sigma*^2)"}


def gate3_invariance(sample):
    w_base, var_base = gmv(SIGMA2)
    Sig_scaled = [[SCALE_K * SIGMA2[i][j] for j in range(2)] for i in range(2)]
    w_scaled, var_scaled = gmv(Sig_scaled)
    weights_identical = (w_scaled == w_base)
    var_scales = (var_scaled == SCALE_K * var_base)
    scale_ok = weights_identical and var_scales
    k = float(SCALE_K)
    var_gmv = float(var_base)
    z_base = _zvar(sample["s2_gmv"], var_gmv, sample["n"])
    z_scaled = _zvar(k * sample["s2_gmv"], k * var_gmv, sample["n"])
    mc_scale_identical = (_f(z_base) == _f(z_scaled))
    xu = solve(SIGMA3, [Fraction(1)] * 3)
    xr = solve(SIGMA3, MU3)
    A = sum(xu)
    B = dot([Fraction(1)] * 3, xr)
    C = dot(MU3, xr)
    Dd = A * C - B * B
    g = [(C * xu[i] - B * xr[i]) / Dd for i in range(3)]
    h = [(A * xr[i] - B * xu[i]) / Dd for i in range(3)]
    def wfront(m):
        return [g[i] + h[i] * m for i in range(3)]
    mA, mB, mC = Fraction(1), Fraction(3), Fraction(2)
    wA, wB, wC = wfront(mA), wfront(mB), wfront(mC)
    alpha = (mC - mB) / (mA - mB)
    combo = [alpha * wA[i] + (1 - alpha) * wB[i] for i in range(3)]
    twofund_ok = all(combo[i] == wC[i] for i in range(3)) and \
                 all(sum(wfront(m)) == 1 for m in [mA, mB, mC])
    w_gmv_front = wfront(B / A)
    w_gmv_direct, _ = gmv(SIGMA3)
    gmv_on_frontier = all(w_gmv_front[i] == w_gmv_direct[i] for i in range(3))
    ok = scale_ok and mc_scale_identical and twofund_ok and gmv_on_frontier
    return ok, {"scale": {"weights_identical_under_kSigma": weights_identical,
                          "var_scales_by_k": var_scales, "k": str(SCALE_K),
                          "w_base": [str(x) for x in w_base], "var_base": str(var_base),
                          "var_scaled": str(var_scaled), "mc_z_base": _f(z_base),
                          "mc_z_scaled": _f(z_scaled), "mc_scale_identical": mc_scale_identical},
                "two_fund": {"affine_combo_exact": twofund_ok, "alpha": str(alpha),
                             "w_target_mC": [str(x) for x in wC],
                             "w_combo": [str(x) for x in combo],
                             "gmv_recovered_on_frontier": gmv_on_frontier},
                "pass_if": "scale-equivariance exact + MC z identical AND two-fund affine exact AND GMV on frontier"}


def gate4_falsify(sample):
    var_gmv_exact = gmv(SIGMA2)[1]
    var_gmv = float(var_gmv_exact)
    n = sample["n"]
    eq_var_exact = Fraction(3, 2)
    a2_var_exact = Fraction(1)
    eq_distinct = (eq_var_exact != var_gmv_exact)
    a2_distinct = (a2_var_exact != var_gmv_exact)
    z_eq = _zvar(sample["s2_eq"], var_gmv, n)
    z_a2 = _zvar(sample["s2_a2"], var_gmv, n)
    eq_rejected = abs(z_eq) >= Z_REJECT
    a2_rejected = abs(z_a2) >= Z_REJECT
    ok = eq_distinct and a2_distinct and eq_rejected and a2_rejected
    return ok, {"naive_equal_weight": {"claim": "equal weights 1/n achieve the minimum variance",
                                       "eq_var_exact": str(eq_var_exact), "gmv_var_exact": str(var_gmv_exact),
                                       "distinct": eq_distinct, "s2_eq_hat": _f(sample["s2_eq"]),
                                       "z_vs_gmv": _f(z_eq), "z_reject": Z_REJECT, "rejected": eq_rejected},
                "naive_single_asset": {"claim": "hold the single lowest-variance asset (asset 2, var 1)",
                                       "asset_var_exact": str(a2_var_exact), "gmv_var_exact": str(var_gmv_exact),
                                       "distinct": a2_distinct, "s2_a2_hat": _f(sample["s2_a2"]),
                                       "z_vs_gmv": _f(z_a2), "z_reject": Z_REJECT, "rejected": a2_rejected},
                "pass_if": "eq_var != gmv AND asset_var != gmv AND both |z| >= Z_REJECT on same sample"}


def build_results():
    sample = mc_portfolio_sample(SEED, MC_N)
    g1_ok, g1 = gate1_exact()
    g2_ok, g2 = gate2_mc_agreement(sample)
    g3_ok, g3 = gate3_invariance(sample)
    g4_ok, g4 = gate4_falsify(sample)
    gates = {"G1_exact_identity": {"name": "closed form == matrix GMV; FOC equalised (exact Fraction)", "ok": g1_ok, **g1},
             "G2_montecarlo_agreement": {"name": "GMV sample variance agrees with sigma*^2", "ok": g2_ok, **g2},
             "G3_invariance": {"name": "scale-equivariance + two-fund separation", "ok": g3_ok, **g3},
             "G4_falsifiability": {"name": "equal-weight and single-asset both rejected", "ok": g4_ok, **g4}}
    order = ["G1_exact_identity", "G2_montecarlo_agreement", "G3_invariance", "G4_falsifiability"]
    first_failing = next((g for g in order if not gates[g]["ok"]), None)
    all_pass = first_failing is None
    w2, var2 = gmv(SIGMA2)
    return {"claim": ("min_variance_two_fund: for n assets with SPD covariance Sigma the global "
                      "minimum-variance portfolio is w*=Sigma^-1 1/(1^T Sigma^-1 1) with variance "
                      "1/(1^T Sigma^-1 1); for Sigma=[[4,1/2],[1/2,1]] w*=(1/8,7/8), sigma*^2=15/16; "
                      "beats equal-weight (3/2) and the best single asset (1); efficient weights are "
                      "affine in target return (two-fund separation)"),
            "seed": SEED,
            "params": {"sigma2": [[str(x) for x in row] for row in SIGMA2], "mc_n": MC_N,
                       "z_accept": Z_ACCEPT, "z_reject": Z_REJECT, "scale_k": str(SCALE_K)},
            "exact": {"w1_star": str(w2[0]), "w2_star": str(w2[1]), "sigma_star_sq": str(var2)},
            "gates": gates, "all_gates_pass": all_pass,
            "first_failing_gate": first_failing, "decision": "PASS" if all_pass else "FAIL"}


def canonical(r):
    return json.dumps(r, sort_keys=True, separators=(",", ":"))


def main():
    import sys
    selfcheck = "--selfcheck" in sys.argv
    results = build_results()
    c1 = canonical(results)
    c2 = canonical(build_results())
    assert c1 == c2, "NON-DETERMINISTIC: in-process double-run diverged"
    digest = hashlib.sha256(c1.encode()).hexdigest()
    if selfcheck:
        print("SELFCHECK: byte-identical")
        print("results_sha256: " + digest)
        raise SystemExit(0 if results["all_gates_pass"] else 1)
    print(json.dumps(results, indent=2, sort_keys=True))
    print("in_process_double_run: IDENTICAL")
    print("results_sha256: " + digest)
    print("decision: " + results["decision"])
    raise SystemExit(0 if results["all_gates_pass"] else 1)


if __name__ == "__main__":
    main()
