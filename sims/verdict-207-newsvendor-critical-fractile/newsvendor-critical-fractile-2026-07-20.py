#!/usr/bin/env python3
"""Newsvendor critical fractile: to maximize profit, stock a high-margin product
ABOVE its expected demand. The profit-maximizing order quantity is the
critical-fractile QUANTILE of demand, Q* = smallest integer Q with
CDF(Q) >= (p-c)/(p-s), NOT the mean. For a high-margin good the critical ratio
exceeds 1/2, so the optimal stock sits strictly above the mean; for a low-margin
good it sits below; only at critical ratio = 1/2 does the optimum coincide with
the median. The folk rule "order what you expect to sell" is exactly wrong.

Stdlib only (hashlib, json, math, random, fractions). Deterministic: SEED pinned;
a fresh random.Random(SEED) is created at the start of EACH full run, so both an
in-process double-run and separate cross-invocation reproduce byte-identical
output.

Digest posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY -- the compact-canonical
results dict's own sha256 IS the digest; it is not a field inside the dict.
"""
import hashlib
import json
import math
import random
from fractions import Fraction

SEED = 20260717
N = 40                  # binomial trials -> demand support 0..N
Z_GATE = 3.0
T_MC = 200_000          # paired Monte-Carlo draws (G2)
ROUND_DP = 10           # fixed serialization precision for byte-stable floats
DENOM = 2 ** N          # 2^40, exact pmf denominator

# Exact pmf and CDF of D ~ Binomial(N, 1/2) as rationals.
PMF = [Fraction(math.comb(N, k), DENOM) for k in range(N + 1)]
CDF = []
_acc = Fraction(0)
for _k in range(N + 1):
    _acc += PMF[_k]
    CDF.append(_acc)  # CDF[Q] = P(D <= Q), exact Fraction
MEAN = N // 2           # 20
MEDIAN = N // 2         # 20 (symmetric binomial, even n)

# Three pinned economic cases (all salvage s = 0).
CASES = {
    "high": {"p": 10, "c": 2, "s": 0},   # CR = 4/5 -> Q* above mean
    "low":  {"p": 10, "c": 8, "s": 0},   # CR = 1/5 -> Q* below mean
    "mid":  {"p": 10, "c": 5, "s": 0},   # CR = 1/2 -> Q* = median
}


def crit_ratio(p, c, s):
    """Critical ratio (p-c)/(p-s) as an exact Fraction."""
    return Fraction(p - c, p - s)


def crit_fractile_Q(cr):
    """Smallest integer Q in [0, N] with CDF(Q) >= cr (exact)."""
    for q in range(N + 1):
        if CDF[q] >= cr:
            return q
    return N


def expected_profit(p, c, s, q):
    """Exact E[profit(Q=q)] = sum_d pmf(d) * (p*min(q,d) + s*max(q-d,0) - c*q)."""
    total = Fraction(0)
    for d in range(N + 1):
        prof = p * min(q, d) + s * max(q - d, 0) - c * q
        total += PMF[d] * prof
    return total  # exact Fraction


def enum_argmax_Q(p, c, s):
    """argmax over Q in [0, N] of exact E[profit(Q)]; ties -> smallest Q."""
    best_q = 0
    best_val = expected_profit(p, c, s, 0)
    for q in range(1, N + 1):
        val = expected_profit(p, c, s, q)
        if val > best_val:            # strict -> first (smallest) maximizer wins
            best_val = val
            best_q = q
    return best_q, best_val


def marginal_increment(p, c, s, q):
    """Enumerated ΔE(q) = E[profit(q+1)] - E[profit(q)] as an exact Fraction."""
    return expected_profit(p, c, s, q + 1) - expected_profit(p, c, s, q)


def marginal_closed_form(p, c, s, q, cr):
    """Closed form ΔE(q) = (p-s)*(CR - F(q)) as an exact Fraction."""
    return (p - s) * (cr - CDF[q])


def mean_sd(vals):
    """Sample mean and standard deviation (ddof=1)."""
    n = len(vals)
    m = math.fsum(vals) / n
    var = math.fsum((v - m) ** 2 for v in vals) / (n - 1)
    return m, math.sqrt(var)


def draw_demand(rng):
    """One draw of D ~ Binomial(N, 1/2) as a sum of N fair coin flips."""
    return sum(1 for _ in range(N) if rng.random() < 0.5)


def gate_g1():
    """Exactly-true: closed-form Q* == enumerated exact-profit argmax, per case."""
    per_case = {}
    ok = True
    for name, e in CASES.items():
        p, c, s = e["p"], e["c"], e["s"]
        cr = crit_ratio(p, c, s)
        q_star = crit_fractile_Q(cr)
        q_arg, _ = enum_argmax_Q(p, c, s)
        match = (q_star == q_arg)
        ok = ok and match
        per_case[name] = {
            "CR": str(cr),
            "Q_star_closed_form": q_star,
            "Q_argmax_enum": q_arg,
            "above_mean": q_star > MEAN,
            "below_mean": q_star < MEAN,
            "equals_median": q_star == MEDIAN,
            "exact_match": match,
        }
    return ok, per_case


def gate_g2(rng):
    """>=3sigma paired Monte-Carlo: HIGH-margin Q* beats mean-stocking Q=20."""
    e = CASES["high"]
    p, c, s = e["p"], e["c"], e["s"]
    cr = crit_ratio(p, c, s)
    q_star = crit_fractile_Q(cr)
    q_naive = MEAN  # 20

    def profit(q, d):
        return p * min(q, d) + s * max(q - d, 0) - c * q

    prof_star = []
    prof_naive = []
    diffs = []
    for _ in range(T_MC):
        d = draw_demand(rng)
        a = profit(q_star, d)
        b = profit(q_naive, d)
        prof_star.append(a)
        prof_naive.append(b)
        diffs.append(a - b)

    mean_diff, sd_diff = mean_sd(diffs)
    se_diff = sd_diff / math.sqrt(T_MC)
    z_meandiff = mean_diff / se_diff if se_diff > 0 else float("inf")

    m_star, sd_star = mean_sd(prof_star)
    m_naive, sd_naive = mean_sd(prof_naive)
    se_star = sd_star / math.sqrt(T_MC)
    se_naive = sd_naive / math.sqrt(T_MC)
    se_means = math.sqrt(se_star ** 2 + se_naive ** 2)
    z_means = (m_star - m_naive) / se_means if se_means > 0 else float("inf")

    ok = (
        mean_diff > 0.0 and z_meandiff >= Z_GATE
        and (m_star - m_naive) > 0.0 and z_means >= Z_GATE
    )
    detail = {
        "q_star": q_star,
        "q_naive": q_naive,
        "mean_profit_q_star": round(m_star, ROUND_DP),
        "mean_profit_q_naive": round(m_naive, ROUND_DP),
        "mean_diff": round(mean_diff, ROUND_DP),
        "z_meandiff": round(z_meandiff, ROUND_DP),
        "z_means": round(z_means, ROUND_DP),
    }
    return ok, detail


def gate_g3():
    """Robustness/shift: sweep CR via c=0..10 (s=0, p=10); Q*(CR) monotone
    non-decreasing AND Q*>median iff CR>1/2, <median iff CR<1/2, =median at 1/2."""
    p, s = 10, 0
    half = Fraction(1, 2)
    c_grid = list(range(0, 11))
    cr_grid = []
    q_grid = []
    iff_ok = True
    for c in c_grid:
        cr = crit_ratio(p, c, s)
        q = crit_fractile_Q(cr)
        cr_grid.append(str(cr))
        q_grid.append(q)
        if cr > half:
            iff_ok = iff_ok and (q > MEDIAN)
        elif cr < half:
            iff_ok = iff_ok and (q < MEDIAN)
        else:  # cr == 1/2
            iff_ok = iff_ok and (q == MEDIAN)
    # Sweep is over DECREASING c (c=0..10) => DECREASING CR; Q* must be
    # non-increasing along that direction, i.e. non-decreasing in CR.
    monotone = all(q_grid[i] >= q_grid[i + 1] for i in range(len(q_grid) - 1))
    ok = monotone and iff_ok
    detail = {
        "c_grid": c_grid,
        "CR_grid": cr_grid,
        "Q_star_grid": q_grid,
        "monotone_nondecreasing_in_CR": monotone,
        "iff_median_direction": iff_ok,
    }
    return ok, detail


def gate_g4():
    """Second exactly-true: marginal identity ΔE(Q)=(p-s)*(CR-F(Q)) exact for ALL
    Q, and ΔE>0 for Q<Q*, ΔE<=0 for Q>=Q*, per case."""
    per_case = {}
    ok = True
    for name, e in CASES.items():
        p, c, s = e["p"], e["c"], e["s"]
        cr = crit_ratio(p, c, s)
        q_star = crit_fractile_Q(cr)
        identity_ok = True
        sign_ok = True
        for q in range(0, N):  # ΔE(q) needs q+1 <= N
            enum_d = marginal_increment(p, c, s, q)
            closed_d = marginal_closed_form(p, c, s, q, cr)
            if enum_d != closed_d:            # exact Fraction equality
                identity_ok = False
            if q < q_star:
                if not (enum_d > 0):
                    sign_ok = False
            else:  # q >= q_star
                if not (enum_d <= 0):
                    sign_ok = False
        case_ok = identity_ok and sign_ok
        ok = ok and case_ok
        per_case[name] = {
            "CR": str(cr),
            "Q_star": q_star,
            "marginal_identity_exact": identity_ok,
            "sign_structure_ok": sign_ok,
        }
    return ok, per_case


def compute():
    # Fresh RNG per full run: reproducible in-process AND cross-invocation.
    rng = random.Random(SEED)

    g1_ok, g1 = gate_g1()
    g2_ok, g2 = gate_g2(rng)
    g3_ok, g3 = gate_g3()
    g4_ok, g4 = gate_g4()

    all_pass = g1_ok and g2_ok and g3_ok and g4_ok
    first_failing = None
    for gname, gok in (("G1", g1_ok), ("G2", g2_ok), ("G3", g3_ok), ("G4", g4_ok)):
        if not gok:
            first_failing = gname
            break

    return {
        "head": "newsvendor-critical-fractile",
        "seed": SEED,
        "constants": {
            "N": N, "demand_p": "1/2", "mean": MEAN, "median": MEDIAN,
            "z_gate": Z_GATE, "T_mc": T_MC,
        },
        "cases": {
            name: {"p": e["p"], "c": e["c"], "s": e["s"]}
            for name, e in CASES.items()
        },
        "g1_exact_argmax": g1,
        "g2_montecarlo": g2,
        "g3_shift_sweep": g3,
        "g4_marginal_identity": g4,
        "gates": {
            "G1_exact_argmax": g1_ok,
            "G2_montecarlo_3sigma": g2_ok,
            "G3_shift_monotone": g3_ok,
            "G4_marginal_identity": g4_ok,
        },
        "first_failing_gate": first_failing,
        "all_pass": all_pass,
    }


def canonical(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def main():
    r1 = compute()
    r2 = compute()
    assert canonical(r1) == canonical(r2), "non-deterministic: double-run diverged"
    digest = hashlib.sha256(canonical(r1).encode("utf-8")).hexdigest()
    print(json.dumps(r1, indent=2))
    print("double_run_identical=true")
    print("all_pass=%s" % ("true" if r1["all_pass"] else "false"))
    g2 = r1["g2_montecarlo"]
    print("G2_z_meandiff=%s" % g2["z_meandiff"])
    print("G2_z_means=%s" % g2["z_means"])
    print("G2_mean_diff=%s" % g2["mean_diff"])
    print("RESULTS_SHA256=%s" % digest)
    return 0 if r1["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
