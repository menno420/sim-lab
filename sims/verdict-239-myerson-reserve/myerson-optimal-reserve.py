"""
VERDICT 239 verifier - Myerson optimal reserve price for iid Uniform[0,1] bidders.
Reproduces PROPOSAL 226.

HEAD CLAIM
  Sell one item to n bidders with valuations iid Uniform[0,1]. The Myerson
  revenue-maximizing mechanism is a second-price auction with reserve
  r* = 1/2, the SAME for every n, and its expected revenue is the exact rational
        R*(n) = 2n/(n+1) - 1 + (1/2)^n/(n+1),
  so R*(2) = 5/12, strictly above the no-reserve second-price revenue 1/3
  (an extra 1/12 of surplus captured by the reserve).

GATES (each evaluated in its own direction)
  G1 EQUALITY    virtual value psi(v)=2v-1 vanishes exactly at r*=1/2 (Fraction).
  G2 EQUALITY    three independent exact routes to R*(n) agree for n in
                 {1,2,3,4,5}: closed form == virtual-surplus integral ==
                 sell-decomposition (all fractions.Fraction).
  G3 EQUALITY    R*(2)=5/12, no-reserve revenue=1/3, reserve gain=1/12 (Fraction).
  G4 AGREEMENT   Monte-Carlo revenue of the reserve-1/2 auction (n=2) agrees
                 with 5/12 at |z|<3.
  G5 AGREEMENT   Monte-Carlo revenue of the reserve-1/2 auction (n=3) agrees
                 with R*(3) at |z|<3.
  G6 ROBUSTNESS  on a dyadic reserve grid, exact revenue R(n,r) is maximized at
                 r=1/2 for n in {2,3,5} (no grid reserve beats it).
  G7 REJECTION   the naive "no reserve is optimal" alternative is rejected:
                 paired MC (n=2) gives E[rev(r=1/2) - rev(r=0)] > 0 at z >> 3.

DETERMINISM / DIGEST
  build_results() is a pure function of SEED and fixed params and holds no
  digest of itself. main() builds it twice and asserts byte-identical canonical
  JSON (in-process determinism guard, exit 3 on divergence), then prints
  results_sha256 over the whole dict. Nothing is written to disk. A separate
  re-invocation reproduces the same stdout byte-for-byte.
"""

import hashlib
import json
import random
from fractions import Fraction

SEED = 20260717
Z_GATE = 3.0
N_MC = 200_000


def R_closed(n):
    return Fraction(2 * n, n + 1) - 1 + Fraction(1, 2) ** n / (n + 1)


def R_integral(n, r):
    r = Fraction(r)
    return (Fraction(2 * n, n + 1) - 1) - Fraction(2 * n, n + 1) * r ** (n + 1) + r ** n


def R_decomp(n, r):
    r = Fraction(r)
    one_bidder = r * n * (1 - r) * r ** (n - 1)

    def F(x):
        x = Fraction(x)
        return x ** n / n - x ** (n + 1) / (n + 1)

    two_plus = n * (n - 1) * (F(1) - F(r))
    return one_bidder + two_plus


def build_results():
    rng = random.Random(SEED)

    r_star = Fraction(1, 2)
    psi_at_rstar = 2 * r_star - 1

    ns = [1, 2, 3, 4, 5]
    routes_agree = {}
    Rstar = {}
    for n in ns:
        a = R_closed(n)
        b = R_integral(n, Fraction(1, 2))
        c = R_decomp(n, Fraction(1, 2))
        routes_agree[n] = (a == b == c)
        Rstar[n] = a

    R2 = Rstar[2]
    no_reserve_2 = R_integral(2, Fraction(0))
    gain_2 = R2 - no_reserve_2

    grid = [Fraction(k, 8) for k in range(0, 9)]
    grid_opt = {}
    for n in [2, 3, 5]:
        best_r = max(grid, key=lambda rr: R_integral(n, rr))
        grid_opt[n] = (best_r == Fraction(1, 2))

    tot_res = 0.0
    tot_res_sq = 0.0
    tot_diff = 0.0
    tot_diff_sq = 0.0
    for _ in range(N_MC):
        a = rng.random()
        b = rng.random()
        top1 = a if a > b else b
        top2 = b if a > b else a
        r = 0.5
        if top1 < r:
            rev_res = 0.0
        elif top2 < r:
            rev_res = r
        else:
            rev_res = top2
        rev_no = top2
        tot_res += rev_res
        tot_res_sq += rev_res * rev_res
        d = rev_res - rev_no
        tot_diff += d
        tot_diff_sq += d * d
    mean_res2 = tot_res / N_MC
    var_res2 = tot_res_sq / N_MC - mean_res2 * mean_res2
    z_n2 = (mean_res2 - float(R2)) / ((var_res2 / N_MC) ** 0.5)

    mean_diff = tot_diff / N_MC
    var_diff = tot_diff_sq / N_MC - mean_diff * mean_diff
    z_paired = mean_diff / ((var_diff / N_MC) ** 0.5)

    tot3 = 0.0
    tot3_sq = 0.0
    for _ in range(N_MC):
        vs = [rng.random(), rng.random(), rng.random()]
        vs.sort(reverse=True)
        top1, top2 = vs[0], vs[1]
        r = 0.5
        if top1 < r:
            rev = 0.0
        elif top2 < r:
            rev = r
        else:
            rev = top2
        tot3 += rev
        tot3_sq += rev * rev
    mean_res3 = tot3 / N_MC
    var_res3 = tot3_sq / N_MC - mean_res3 * mean_res3
    z_n3 = (mean_res3 - float(Rstar[3])) / ((var_res3 / N_MC) ** 0.5)

    gates = {
        "G1_psi_zero_at_half": (psi_at_rstar == 0),
        "G2_three_routes_agree": all(routes_agree[n] for n in ns),
        "G3_R2_5_12_gain_1_12": (
            R2 == Fraction(5, 12)
            and no_reserve_2 == Fraction(1, 3)
            and gain_2 == Fraction(1, 12)
        ),
        "G4_mc_n2_agrees": (abs(z_n2) < Z_GATE),
        "G5_mc_n3_agrees": (abs(z_n3) < Z_GATE),
        "G6_grid_opt_at_half": all(grid_opt[n] for n in [2, 3, 5]),
        "G7_reject_no_reserve": (z_paired > 10.0),
    }
    order = [
        "G1_psi_zero_at_half",
        "G2_three_routes_agree",
        "G3_R2_5_12_gain_1_12",
        "G4_mc_n2_agrees",
        "G5_mc_n3_agrees",
        "G6_grid_opt_at_half",
        "G7_reject_no_reserve",
    ]
    first_failing = next((k for k in order if not gates[k]), None)

    results = {
        "seed": SEED,
        "z_gate": Z_GATE,
        "n_mc": N_MC,
        "r_star": str(r_star),
        "Rstar": {str(n): str(Rstar[n]) for n in ns},
        "no_reserve_2": str(no_reserve_2),
        "gain_2": str(gain_2),
        "routes_agree": {str(n): routes_agree[n] for n in ns},
        "grid_opt": {str(n): grid_opt[n] for n in [2, 3, 5]},
        "mc_n2_mean": repr(mean_res2),
        "mc_n2_z": repr(z_n2),
        "mc_n3_mean": repr(mean_res3),
        "mc_n3_z": repr(z_n3),
        "paired_gain_mean": repr(mean_diff),
        "paired_gain_z": repr(z_paired),
        "gates": gates,
        "first_failing_gate": first_failing,
        "all_pass": all(gates.values()),
    }
    return results


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r1 = build_results()
    r2 = build_results()
    if canonical(r1) != canonical(r2):
        print("NONDETERMINISM: build_results() diverged across calls")
        raise SystemExit(3)
    results = r1
    digest = hashlib.sha256(canonical(results).encode()).hexdigest()
    print(json.dumps(results, indent=2, sort_keys=True))
    print("results_sha256:", digest)
    print("all_pass:", results["all_pass"])
    raise SystemExit(0 if results["all_pass"] else 1)


if __name__ == "__main__":
    main()
