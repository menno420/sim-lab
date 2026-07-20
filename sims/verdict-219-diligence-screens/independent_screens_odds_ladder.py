#!/usr/bin/env python3
"""independent_screens_odds_ladder.py — stdlib verifier for PROPOSAL 206.

Head: at a low base rate, TWO independent symmetric screens flag a shortlist
that even one far-more-accurate single screen cannot match, because independent
positives MULTIPLY the odds. For k conditionally-independent symmetric screens
(sensitivity = specificity = a) under the AND rule (a candidate passes only if
ALL k screens flag it), the posterior precision after k positives is

    PPV_k = p*a^k / ( p*a^k + (1-p)(1-a)^k ),

which in ODDS form is  posterior_odds = prior_odds * (a/(1-a))^k  with
prior_odds = p/(1-p) and per-screen likelihood ratio LR = a/(1-a). Majority-good
(PPV_k > 1/2) holds iff (a/(1-a))^k > (1-p)/p, i.e. each of k screens need only
clear a/(1-a) > ((1-p)/p)^(1/k): the k-th-ROOT ladder. The gain is exactly as
real as the screens' independence — it vanishes when they are redundant.

Posture: WHOLE-DICT / NO-SELF-FIELD / STDOUT-ONLY. compute() builds a results
dict that does NOT carry its own sha256; main() runs compute() twice, asserts
the canonical (compact) JSON strings are identical, prints the indented dict,
then the digest of the compact canonical string on stdout only. Stdlib only
(json, hashlib, math, random, fractions). ONE random.Random(SEED) is created
inside compute(), consumed in a fixed documented order.
"""

import json
import hashlib
import math
import random
from fractions import Fraction as F

SEED = 20260717


# ---------------------------------------------------------------------------
# Closed forms (exact, Fraction)
# ---------------------------------------------------------------------------
def ppv_direct(p, a, k):
    """Direct Bayes formula PPV_k = p*a^k / (p*a^k + (1-p)(1-a)^k)."""
    good = p * a ** k
    bad = (1 - p) * (1 - a) ** k
    return good / (good + bad)


def ppv_odds(p, a, k):
    """Odds-form: posterior_odds = (p/(1-p)) * (a/(1-a))^k, PPV = odds/(1+odds)."""
    odds = (p / (1 - p)) * (a / (1 - a)) ** k
    return odds / (1 + odds)


def ppv_enum(p, a, k):
    """Exhaustive integer-population enumeration.

    N = den(p)*den(a)^k makes every count an integer:
      good=p*N, good_pass=good*a^k, bad=(1-p)*N, bad_pass=bad*(1-a)^k.
    """
    nump, denp = p.numerator, p.denominator
    numa, dena = a.numerator, a.denominator
    good_pass = nump * numa ** k                       # p*N * a^k
    bad_pass = (denp - nump) * (dena - numa) ** k       # (1-p)*N * (1-a)^k
    return F(good_pass, good_pass + bad_pass)


def clears_majority(p, a, k):
    """Polynomial (root-free) majority test: p*a^k > (1-p)(1-a)^k."""
    return p * a ** k > (1 - p) * (1 - a) ** k


# ---------------------------------------------------------------------------
# G1 — EXACTLY-TRUE: direct == odds-form == exhaustive enumeration
# ---------------------------------------------------------------------------
def gate_g1():
    ps = [F(1, 100), F(1, 50), F(1, 10)]
    accs = [F(9, 10), F(91, 100), F(95, 100)]
    ks = [1, 2, 3]
    cells = 0
    mismatches = 0
    for p in ps:
        for a in accs:
            for k in ks:
                cells += 1
                d = ppv_direct(p, a, k)
                o = ppv_odds(p, a, k)
                e = ppv_enum(p, a, k)
                if not (d == o == e):
                    mismatches += 1
    ok = mismatches == 0 and cells > 0
    return ok, {
        "cells_total": cells,
        "mismatches": mismatches,
        "direction": "direct == odds-form == exhaustive-enumeration exact in 100% of cells (mismatches==0)",
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# G2 — EXACT k-th-root ladder threshold + strictly-decreasing clearing accuracy
# ---------------------------------------------------------------------------
def gate_g2():
    ps = [F(1, 100), F(1, 50), F(1, 10)]
    accs = [F(9, 10), F(91, 100), F(95, 100), F(83, 100)]
    ks = [1, 2, 3]
    cells = 0
    violations = 0
    for p in ps:
        for a in accs:
            for k in ks:
                cells += 1
                poly = clears_majority(p, a, k)
                half = ppv_direct(p, a, k) > F(1, 2)
                if poly != half:
                    violations += 1
    # Ladder exhibit at p = 1/100: minimal integer-percent accuracy clearing
    # majority-good for k = 1, 2, 3 (search a in {1/100..100/100}).
    p = F(1, 100)
    clearing = []
    for k in ks:
        found = None
        for perc in range(1, 101):
            a = F(perc, 100)
            if clears_majority(p, a, k):
                found = perc
                break
        clearing.append(found)
    strictly_decreasing = all(
        clearing[i] is not None and clearing[i + 1] is not None
        and clearing[i] > clearing[i + 1]
        for i in range(len(clearing) - 1)
    )
    ok = violations == 0 and strictly_decreasing
    return ok, {
        "cells_total": cells,
        "boolean_violations": violations,
        "clearing_accuracy_percent_k1_k2_k3": clearing,
        "clearing_strictly_decreasing_in_k": strictly_decreasing,
        "direction": "exact boolean [poly>] == [PPV>1/2] in 100% of cells AND clearing accuracy strictly decreasing in k (violations==0)",
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# G3 — >=3 sigma vs folk belief, Monte Carlo (headline scenario)
# ---------------------------------------------------------------------------
def gate_g3(rng):
    p = F(1, 100)
    a = F(95, 100)
    M = 400000
    pf = float(p)
    af = float(a)
    passed_total = 0
    good_pass = 0
    # Fixed draw order per candidate: (1) good?, (2) screen1, (3) screen2.
    for _ in range(M):
        is_good = rng.random() < pf
        flag_p = af if is_good else (1.0 - af)
        s1 = rng.random() < flag_p
        s2 = rng.random() < flag_p
        if s1 and s2:
            passed_total += 1
            if is_good:
                good_pass += 1
    ppv_emp = good_pass / passed_total
    se = math.sqrt(ppv_emp * (1.0 - ppv_emp) / passed_total)
    z_majority = (ppv_emp - 0.5) / se
    ppv2_closed = float(F(361, 460))
    ppv1_single = float(F(19, 118))
    within_3se_of_closed = abs(ppv_emp - ppv2_closed) <= 3.0 * se
    ok = (z_majority >= 3.0) and within_3se_of_closed
    return ok, {
        "M": M,
        "passed_total": passed_total,
        "good_pass": good_pass,
        "PPV_emp": round(ppv_emp, 6),
        "SE": round(se, 6),
        "z_majority": round(z_majority, 6),
        "PPV_2_closed": round(ppv2_closed, 6),
        "PPV_1_single_screen_contrast": round(ppv1_single, 6),
        "emp_within_3se_of_closed": within_3se_of_closed,
        "direction": "two-independent-screen empirical PPV exceeds 1/2 by >=3 sigma (z_majority>=3) while one screen of the same accuracy is far minority (PPV_1~0.161)",
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# G4 — robustness / correlation-shift (independence is load-bearing)
# ---------------------------------------------------------------------------
def ppv_two_with_correlation(p, a, rho):
    """Two screens; with prob rho screen-2 is a perfect COPY of screen-1's
    verdict (redundant), else independent. Closed form after two positives."""
    pg = rho * a + (1 - rho) * a ** 2            # P(both flag | good)
    pb = rho * (1 - a) + (1 - rho) * (1 - a) ** 2  # P(both flag | bad)
    return (p * pg) / (p * pg + (1 - p) * pb)


def gate_g4():
    p = F(1, 100)
    a = F(95, 100)
    # (a) correlation nullification
    rhos = [F(0), F(1, 4), F(1, 2), F(3, 4), F(1)]
    ppv_by_rho = []
    for rho in rhos:
        ppv_by_rho.append(ppv_two_with_correlation(p, a, rho))
    rho1_equals_ppv1 = ppv_two_with_correlation(p, a, F(1)) == ppv_direct(p, a, 1)
    strictly_decreasing = all(
        ppv_by_rho[i] > ppv_by_rho[i + 1] for i in range(len(ppv_by_rho) - 1)
    )
    corr_violations = 0 if (rho1_equals_ppv1 and strictly_decreasing) else 1

    # (b) odds-multiplication identity under asymmetric screens + base-rate shift
    sens = (F(9, 10), F(4, 5), F(85, 100))
    spec = (F(19, 20), F(7, 10), F(9, 10))       # 1-spec = (1/20, 3/10, 1/10)
    ps = [F(1, 2), F(1, 5), F(1, 100), F(1, 1000)]
    ident_cells = 0
    ident_mismatches = 0
    for p_i in ps:
        for kk in (1, 2, 3):
            ident_cells += 1
            prod_sens = F(1)
            prod_fp = F(1)
            odds = p_i / (1 - p_i)
            for i in range(kk):
                prod_sens *= sens[i]
                prod_fp *= (1 - spec[i])
                odds *= sens[i] / (1 - spec[i])
            ppv_form = odds / (1 + odds)
            ppv_dir = (p_i * prod_sens) / (p_i * prod_sens + (1 - p_i) * prod_fp)
            if ppv_form != ppv_dir:
                ident_mismatches += 1

    # k-needed monotone in p at fixed symmetric a
    a_sym = F(95, 100)
    p_seq = [F(1, 2), F(1, 10), F(1, 100), F(1, 1000)]
    k_needed = []
    for p_i in p_seq:
        k = 1
        while not clears_majority(p_i, a_sym, k):
            k += 1
        k_needed.append(k)
    k_monotone = all(k_needed[i] <= k_needed[i + 1] for i in range(len(k_needed) - 1))
    ident_violations = 0 if (ident_mismatches == 0 and k_monotone) else 1

    ok = (corr_violations == 0) and (ident_violations == 0)
    return ok, {
        "correlation_nullification": {
            "rho_grid": ["0", "1/4", "1/2", "3/4", "1"],
            "ppv_by_rho": [str(v) for v in ppv_by_rho],
            "ppv_by_rho_float": [round(float(v), 6) for v in ppv_by_rho],
            "ppv_at_rho1_equals_ppv1": rho1_equals_ppv1,
            "ppv_strictly_decreasing_in_rho": strictly_decreasing,
            "violations": corr_violations,
        },
        "odds_multiplication_identity": {
            "cells_total": ident_cells,
            "mismatches": ident_mismatches,
            "k_needed_over_decreasing_p": k_needed,
            "k_needed_nondecreasing": k_monotone,
            "violations": ident_violations,
        },
        "direction": "redundancy exactly nullifies the second screen (PPV(rho=1)==PPV_1) and PPV strictly decreasing in correlation; odds = prior * prod(LR_i) exact in 100% of cells and k-needed monotone in p (violations==0)",
        "ok": ok,
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def compute():
    rng = random.Random(SEED)  # ONE stream, consumed only by G3, fixed order
    g1_ok, g1 = gate_g1()
    g2_ok, g2 = gate_g2()
    g3_ok, g3 = gate_g3(rng)
    g4_ok, g4 = gate_g4()
    gates = {"G1": g1_ok, "G2": g2_ok, "G3": g3_ok, "G4": g4_ok}
    decision = "sim-ready" if all(gates.values()) else "needs-more-grooming"
    return {
        "seed": SEED,
        "head": "independent positives MULTIPLY the odds: k conditionally-independent symmetric screens (AND rule) compose by likelihood-ratio product; the k-th screen need only clear (odds-against)^(1/k); two 95% screens beat one 99% at 1% base rate; the gain vanishes when screens are redundant",
        "pinned_world": {
            "p_base_rate": "1/100",
            "a_accuracy": "95/100",
            "k_grid": [1, 2, 3],
            "PPV_1": "19/118",
            "PPV_2": "361/460",
            "ladder_threshold": "(a/(1-a))^k > (1-p)/p",
        },
        "G1_exactly_true": g1,
        "G2_kth_root_ladder": g2,
        "G3_three_sigma_vs_folk": g3,
        "G4_correlation_robustness": g4,
        "gates": gates,
        "decision": decision,
    }


def canonical(r):
    return json.dumps(r, sort_keys=True, separators=(",", ":"))


def main():
    r1 = compute()
    r2 = compute()
    c1 = canonical(r1)
    c2 = canonical(r2)
    assert c1 == c2, "NON-DETERMINISTIC: in-process double-run diverged"
    digest = hashlib.sha256(c1.encode()).hexdigest()
    print(json.dumps(r1, indent=2, sort_keys=True))
    print()
    print("in_process_double_run: IDENTICAL")
    print(f"results_sha256: {digest}")
    print(f"decision: {r1['decision']}")


if __name__ == "__main__":
    main()
