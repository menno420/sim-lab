#!/usr/bin/env python3
"""Revenue equivalence: first-price and second-price auctions yield the SAME
expected seller revenue, exactly (n-1)/(n+1) for n symmetric bidders with i.i.d.
Uniform(0,1) private values.

Stdlib-only. SEED=20260717; all randomness from a single random.Random(20260717)
consumed in a fixed, documented order (see run_battery). Each gate is read in its
own direction:

  G1  EXACT identity (fractions.Fraction): first-price expected revenue
      (n-1)/n * E[max] == second-price expected revenue E[2nd highest]
      == (n-1)/(n+1), derived by exact polynomial integration on [0,1].
      PASS = the two mechanism revenues are identical rationals for every n.

  G2  Monte-Carlo agreement: empirical mean revenue of each mechanism vs the exact
      (n-1)/(n+1). PASS = |z| < 3 for BOTH mechanisms AND the paired
      first-minus-second difference (empirical equivalence sits at zero).

  G3  Robustness: (a) sweep n; the exact revenue is strictly increasing toward 1
      and every MC mean agrees (|z|<3); (b) scale invariance: values ~ U(0,k)
      scale revenue by exactly k, equivalence preserved (exact + empirical).

  G4  Falsifiability: the naive belief "the seller captures the winner's value"
      predicts revenue = E[max] = n/(n+1). Observed second-price revenue sits a
      full information rent 1/(n+1) below it. PASS = naive model REJECTED at |z|>5.
"""

import hashlib
import json
import random
import sys
from fractions import Fraction

SEED = 20260717
Z_AGREE = 3.0     # agreement gates: PASS when |z| < Z_AGREE
Z_REJECT = 5.0    # falsifiability: PASS when the wrong model is |z| > Z_REJECT


def int_monomial(j):
    """Exact integral of x**j over [0,1] = 1/(j+1)."""
    return Fraction(1, j + 1)


def exact_max_mean(n):
    """E[max of n iid U(0,1)] = integral x * n*x**(n-1) dx = n/(n+1), exact."""
    return n * int_monomial(n)


def exact_second_mean(n):
    """E[2nd highest of n iid U(0,1)] via density n(n-1) x**(n-2)(1-x):
       n(n-1) * (int x**(n-1) - int x**n) = (n-1)/(n+1), exact."""
    return n * (n - 1) * (int_monomial(n - 1) - int_monomial(n))


def fpa_revenue_exact(n):
    """First-price: symmetric BNE bid b(v) = (n-1)/n * v; winner pays b(max).
       Expected revenue = (n-1)/n * E[max], exact."""
    return Fraction(n - 1, n) * exact_max_mean(n)


def spa_revenue_exact(n):
    """Second-price: truthful dominant bidding; winner pays 2nd highest value.
       Expected revenue = E[2nd highest], exact."""
    return exact_second_mean(n)


def gate1_exact_identity():
    ns = [2, 3, 5, 10, 20, 50]
    rows = []
    ok = True
    for n in ns:
        fpa = fpa_revenue_exact(n)
        spa = spa_revenue_exact(n)
        closed = Fraction(n - 1, n + 1)
        match = (fpa == spa == closed)
        ok = ok and match
        rows.append({
            "n": n,
            "fpa": [fpa.numerator, fpa.denominator],
            "spa": [spa.numerator, spa.denominator],
            "closed_form": [closed.numerator, closed.denominator],
            "identical": match,
        })
    return ok, {"claim": "fpa_revenue == spa_revenue == (n-1)/(n+1) exactly",
                "rows": rows}


def one_auction(rng, n, scale=1):
    """Draw n values ~ U(0,scale) (single rng, fixed order); return
       (fpa_revenue, spa_revenue) for this profile."""
    vals = [rng.random() * scale for _ in range(n)]
    vals.sort()
    top = vals[-1]
    second = vals[-2]
    fpa = (n - 1) / n * top
    spa = second
    return fpa, spa


def mc_mean_se(samples):
    N = len(samples)
    mean = sum(samples) / N
    var = sum((x - mean) ** 2 for x in samples) / (N - 1)
    se = (var / N) ** 0.5
    return mean, se, N


def gate2_montecarlo(rng, n=7, N=500000):
    fpa_s = []
    spa_s = []
    diff_s = []
    for _ in range(N):
        f, s = one_auction(rng, n)
        fpa_s.append(f)
        spa_s.append(s)
        diff_s.append(f - s)
    mu = float(Fraction(n - 1, n + 1))
    fmean, fse, _ = mc_mean_se(fpa_s)
    smean, sse, _ = mc_mean_se(spa_s)
    dmean, dse, _ = mc_mean_se(diff_s)
    zf = (fmean - mu) / fse
    zs = (smean - mu) / sse
    zd = (dmean - 0.0) / dse
    ok = abs(zf) < Z_AGREE and abs(zs) < Z_AGREE and abs(zd) < Z_AGREE
    return ok, {
        "n": n, "N": N, "mu_exact": mu,
        "fpa_mean": fmean, "z_fpa": zf,
        "spa_mean": smean, "z_spa": zs,
        "paired_diff_mean": dmean, "z_diff": zd,
        "pass_when": "|z_fpa|,|z_spa|,|z_diff| all < %.1f" % Z_AGREE,
    }


def gate3_robustness(rng):
    ns = [2, 5, 10, 50]
    prev = None
    monotone = True
    sweep = []
    N = 150000
    for n in ns:
        mu = float(Fraction(n - 1, n + 1))
        if prev is not None and not (mu > prev):
            monotone = False
        prev = mu
        samples = []
        for _ in range(N):
            _, s = one_auction(rng, n)
            samples.append(s)
        mean, se, _ = mc_mean_se(samples)
        z = (mean - mu) / se
        sweep.append({"n": n, "mu": mu, "spa_mean": mean, "z": z,
                      "agree": abs(z) < Z_AGREE})
    sweep_ok = monotone and all(r["agree"] for r in sweep)
    k = 5
    n = 6
    N2 = 150000
    fs = []
    ss = []
    for _ in range(N2):
        f, s = one_auction(rng, n, scale=k)
        fs.append(f)
        ss.append(s)
    mu_scaled = k * float(Fraction(n - 1, n + 1))
    fmean, fse, _ = mc_mean_se(fs)
    smean, sse, _ = mc_mean_se(ss)
    zf = (fmean - mu_scaled) / fse
    zs = (smean - mu_scaled) / sse
    exact_scaled = k * Fraction(n - 1, n + 1)
    exact_ok = (k * fpa_revenue_exact(n) == k * spa_revenue_exact(n) == exact_scaled)
    scale_ok = exact_ok and abs(zf) < Z_AGREE and abs(zs) < Z_AGREE
    ok = sweep_ok and scale_ok
    return ok, {
        "sweep": sweep, "monotone_increasing": monotone,
        "scale_k": k, "scale_n": n, "mu_scaled": mu_scaled,
        "fpa_mean_scaled": fmean, "z_fpa_scaled": zf,
        "spa_mean_scaled": smean, "z_spa_scaled": zs,
        "scale_exact_equiv": exact_ok,
        "pass_when": "monotone sweep agrees (|z|<3) AND scaled revenue "
                     "= k*(n-1)/(n+1) exactly and empirically",
    }


def gate4_falsifiability(rng, n=7, N=500000):
    """Naive: seller captures winner's value -> revenue = E[max] = n/(n+1).
       True second-price revenue is 1/(n+1) lower (winner's information rent).
       PASS = naive rejected at |z| > Z_REJECT while true model holds."""
    samples = []
    for _ in range(N):
        _, s = one_auction(rng, n)
        samples.append(s)
    mean, se, _ = mc_mean_se(samples)
    mu_naive = float(Fraction(n, n + 1))
    mu_true = float(Fraction(n - 1, n + 1))
    z_naive = (mean - mu_naive) / se
    z_true = (mean - mu_true) / se
    rent = float(Fraction(1, n + 1))
    ok = abs(z_naive) > Z_REJECT and abs(z_true) < Z_AGREE
    return ok, {
        "n": n, "N": N,
        "naive_model": "revenue = winner's value = n/(n+1)",
        "mu_naive": mu_naive, "z_vs_naive": z_naive,
        "mu_true": mu_true, "z_vs_true": z_true,
        "information_rent_1_over_np1": rent,
        "pass_when": "naive rejected |z|>%.1f while true model holds |z|<%.1f"
                     % (Z_REJECT, Z_AGREE),
    }


def run_battery():
    rng = random.Random(SEED)
    g1_ok, g1 = gate1_exact_identity()
    g2_ok, g2 = gate2_montecarlo(rng)
    g3_ok, g3 = gate3_robustness(rng)
    g4_ok, g4 = gate4_falsifiability(rng)
    gates = {"G1_exact_identity": g1_ok, "G2_montecarlo_agreement": g2_ok,
             "G3_robustness": g3_ok, "G4_falsifiability": g4_ok}
    results = {
        "proposal": 222,
        "verdict": 235,
        "seed": SEED,
        "claim": "First-price and second-price auctions yield identical expected "
                 "seller revenue (n-1)/(n+1) for n symmetric U(0,1) bidders.",
        "G1": g1, "G2": g2, "G3": g3, "G4": g4,
        "gates": gates,
        "sim_ready": all(gates.values()),
    }
    return results


def digest(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main():
    r1 = run_battery()
    r2 = run_battery()
    d1 = json.dumps(r1, sort_keys=True, separators=(",", ":"))
    d2 = json.dumps(r2, sort_keys=True, separators=(",", ":"))
    determinism = (d1 == d2)
    print(json.dumps(r1, indent=2, sort_keys=True))
    print("results_sha256={0}".format(digest(r1)))
    print("determinism_double_run={0}".format(determinism))
    print("sim_ready={0}".format(r1["sim_ready"]))
    sys.exit(0 if (r1["sim_ready"] and determinism) else 1)


if __name__ == "__main__":
    main()
