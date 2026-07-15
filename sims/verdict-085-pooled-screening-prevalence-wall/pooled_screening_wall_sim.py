#!/usr/bin/env python3
"""VERDICT 085 runner — the pooled-screening prevalence wall (idea-engine P072).

Hermetic: reads ONLY the fixtures.json beside this file. Zero repo/network
reads at verdict time. Every decision number is an exact Fraction.

Model: Dorfman two-stage screening, pool size n, prevalence p, q = 1 - p.
    T(n, p) = 1/n + 1 - q^n  (n >= 2);  T(1) = 1  (individual baseline).

Arms:
  A — seedless closed-form exact T(n,p) census + integer-power wall
      certificate + polynomial identity gates + n* search (DECISION-bearing)
  B — INDEPENDENTLY-WRITTEN binomial outcome-tree recomputation of T, its own
      n* search and its own wall check (q^n vs 1/n), exact-equal gated; the
      second decision evaluator recomputes every decision number from Arm B
  R — seeded Monte-Carlo screening careers at three cells, REPORTING-ONLY
      (no statistical gate; draw-count sentinel + reproducibility only)

Gates F1-F6 per the P072 registration; decision order REJECT -> INVALID ->
APPROVE -> NULL (REJECT evaluated FIRST) via twin independently-written
evaluators. Disclosed-anchor mismatches raise first-class anomalies (C3).
"""

import json
import random
import sys
from fractions import Fraction
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent

assert sys.version_info[:2] == (3, 11), (
    "CPython 3.11 pinned (fixture battery cpython pin); got %s" % (sys.version_info[:2],)
)

FIX = json.loads((HERE / "fixtures.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- helpers
CHECKS = {"passed": 0, "failed": 0}
FAILURES = []
ANOMALIES = []


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        FAILURES.append(name)
    return bool(cond)


def anomaly(text):
    ANOMALIES.append("A%d: %s" % (len(ANOMALIES) + 1, text))


def frac(s):
    return Fraction(s)


def fstr(x):
    return "%d/%d" % (x.numerator, x.denominator)


def f12(x):
    return "%.12g" % float(x)


PGRID = [frac(s) for s in FIX["grids"]["prevalence_grid"]]
POOL_LO = FIX["grids"]["pool_grid"]["lo"]
POOL_HI = FIX["grids"]["pool_grid"]["hi"]
PRAC_LO = FIX["grids"]["practical_subgrid"]["lo"]
PRAC_HI = FIX["grids"]["practical_subgrid"]["hi"]
QGRID = [Fraction(k, 100) for k in range(0, 101)] + [frac(FIX["grids"]["identity_grid_extra_q"])]
WALL_P = frac(FIX["grids"]["decision_cells"]["wall_cell"])   # 2/5
SAVE_P = frac(FIX["grids"]["decision_cells"]["savings_cell"])  # 1/100


# ------------------------------------------------------- Arm A (closed form)
def T_A(n, p):
    """Closed-form cost per item: 1/n + 1 - q^n (n>=2); T(1) = 1."""
    if n == 1:
        return Fraction(1)
    q = 1 - p
    return Fraction(1, n) + 1 - q ** n


# ------------------------------------------- Arm B (binomial outcome tree twin)
def T_B(n, p):
    """INDEPENDENT twin: expected tests per item from the binomial outcome
    tree. cost(0) = 1 (negative pool), cost(k>=1) = 1 + n (retest all n).
    Never touches Arm A's closed form."""
    if n == 1:
        return Fraction(1)
    q = 1 - p
    tot = Fraction(0)
    for k in range(0, n + 1):
        cost = 1 if k == 0 else (1 + n)
        tot += comb(n, k) * p ** k * q ** (n - k) * cost
    return tot / n


def nstar_A(p, lo, hi):
    """Arm A optimal pool over {lo..hi} by direct exact comparison."""
    best_n, best = lo, T_A(lo, p)
    for n in range(lo + 1, hi + 1):
        t = T_A(n, p)
        if t < best:
            best, best_n = t, n
    return best_n, best


def nstar_B(p, lo, hi):
    """Arm B independent optimal-pool search (uses T_B)."""
    best_n, best = lo, T_B(lo, p)
    for n in range(lo + 1, hi + 1):
        t = T_B(n, p)
        if t < best:
            best, best_n = t, n
    return best_n, best


# --------------------------------------------------------- F1 model identities
check("F1 T(1) = 1 exactly", T_A(1, WALL_P) == 1 and T_A(1, SAVE_P) == 1)
for p in PGRID:
    for n in range(POOL_LO, POOL_HI + 1):
        q = 1 - p
        norm = sum(comb(n, k) * p ** k * q ** (n - k) for k in range(0, n + 1))
        if not check("F1 normalization n=%d p=%s" % (n, fstr(p)), norm == 1):
            break
        # rearrangement identity T = 1 + 1/n - q^n (the 1/n term ALWAYS present)
        if n >= 2:
            check("F1 rearrangement n=%d p=%s" % (n, fstr(p)),
                  T_A(n, p) == 1 + Fraction(1, n) - q ** n and T_A(n, p) == T_B(n, p))
STAGE1_PRESENT = all(T_A(n, p) - (1 - (1 - p) ** n) == Fraction(1, n)
                     for p in PGRID for n in range(2, POOL_HI + 1))
check("F1 stage-1 test always counted (1/n present in every decision T)", STAGE1_PRESENT)

# --------------------------------------------------------- F6/G1 twin equality
twin_ok = True
for p in PGRID:
    for n in range(POOL_LO, POOL_HI + 1):
        if T_A(n, p) != T_B(n, p):
            twin_ok = False
check("F6 Arm B outcome tree == Arm A closed form on the 12x64 grid", twin_ok)

# --------------------------------------------- F2(a) the WALL integer-power chain
check("F2a 3^2 > 2^3", 3 ** 2 > 2 ** 3)
check("F2a 3^4 > 4^3", 3 ** 4 > 4 ** 3)
check("F2a 3^5 > 5^3", 3 ** 5 > 5 ** 3)
check("F2a 2^4 = 4^2", 2 ** 4 == 4 ** 2)
check("F2a (n+1)^n < n^(n+1) for n in 3..64",
      all((n + 1) ** n < n ** (n + 1) for n in range(3, 65)))
# argmin over the grid of n^(-1/n): equivalently argmax of n^m comparisons ->
# n=3 minimizes n^(-1/n) over n in {2..64}, checked by pairwise n^m vs m^n
best_forgiving = 2
for n in range(3, 65):
    # n more forgiving than best_forgiving iff n^(-1/n) < best^(-1/best)
    # iff n^best > best^n
    if n ** best_forgiving > best_forgiving ** n:
        best_forgiving = n
check("F2a argmin_{n in 2..64} n^(-1/n) is n=3 (integer-power)", best_forgiving == 3)

# wall statement at every rational grid p: helps for some n in {2..64} iff 3q^3>1
WALL_HELPS = FIX["anchors"]["wall_helps_expected"]
for p in PGRID:
    q = 1 - p
    cert = 3 * q ** 3 > 1
    grid_helps = any(T_A(n, p) < 1 for n in range(2, POOL_HI + 1))
    check("F2a wall cert == grid-scan helps p=%s" % fstr(p), cert == grid_helps)
    check("F2a wall cert == disclosed p=%s" % fstr(p), cert == WALL_HELPS[fstr(p)])
# boundary law T(3,q) = 1 iff 3q^3 = 1 (symbolic on grid: no rational grid p hits it)
check("F2a boundary law T(3,q)=1 iff 3q^3=1 (no grid p lands on it)",
      all((T_A(3, p) == 1) == (3 * (1 - p) ** 3 == 1) for p in PGRID))

# --------------------------------------------- F2(b)/F2(c) polynomial identities
# exact coefficient match: build the two difference polynomials as Fraction
# coefficient lists in q and compare to the claimed factorizations, expanded.
def poly_mul(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] += ai * bj
    return out


def poly_add(a, b):
    n = max(len(a), len(b))
    a = a + [Fraction(0)] * (n - len(a))
    b = b + [Fraction(0)] * (n - len(b))
    return [x + y for x, y in zip(a, b)]


def norm_poly(a):
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


# T(2,q) - T(3,q) as a polynomial in q: p = 1-q, so q^n term.
# T(2,q) = 1/2 + 1 - q^2 ; T(3,q) = 1/3 + 1 - q^3
# diff = 1/6 - q^2 + q^3  -> coeffs [1/6, 0, -1, 1]
D23 = [Fraction(1, 6), Fraction(0), Fraction(-1), Fraction(1)]
# claimed (q - 2/3)^2 (q + 1/3) + 1/54
qm23 = [Fraction(-2, 3), Fraction(1)]           # (q - 2/3)
qm23_sq = poly_mul(qm23, qm23)
claim23 = poly_add(poly_mul(qm23_sq, [Fraction(1, 3), Fraction(1)]), [Fraction(1, 54)])
check("F2b T2 identity by exact coefficient match", norm_poly(D23) == norm_poly(claim23))
# and on the identity grid, with equality only at q = 2/3
gap_min = None
gap_argq = None
eq_qs = []
for q in QGRID:
    gap = T_A(2, 1 - q) - T_A(3, 1 - q)
    if gap_min is None or gap < gap_min:
        gap_min, gap_argq = gap, q
    if gap == Fraction(1, 54):
        eq_qs.append(q)
check("F2b T2 gap >= 1/54 on identity grid", gap_min == Fraction(1, 54))
check("F2b T2 equality only at q = 2/3", eq_qs == [Fraction(2, 3)] and gap_argq == Fraction(2, 3))

# T(2,q) - T(4,q) = 1/4 - q^2 + q^4 -> [1/4, 0, -1, 0, 1] ; claimed (q^2 - 1/2)^2
D24 = [Fraction(1, 4), Fraction(0), Fraction(-1), Fraction(0), Fraction(1)]
q2m = [Fraction(-1, 2), Fraction(0), Fraction(1)]   # (q^2 - 1/2)
claim24 = poly_mul(q2m, q2m)
check("F2c T3 identity by exact coefficient match", norm_poly(D24) == norm_poly(claim24))
check("F2c T3 diff >= 0 on identity grid (pool 4 weakly dominates pool 2)",
      all(T_A(2, 1 - q) - T_A(4, 1 - q) >= 0 for q in QGRID))
# break-even coincidence via 2^4 = 4^2: q2* = q4* = 2^(-1/2) i.e. q^2 = 1/2;
# no rational grid q lands on it (margin-0 zero is off-grid)
check("F2c T3 margin-0 at q^2=1/2 is off the rational grid",
      all(q * q != Fraction(1, 2) for q in QGRID) and 2 ** 4 == 4 ** 2)

# ------------------------------------------------- F3 census anchors (helping)
CENSUS = FIX["anchors"]["census_helping"]
for p in PGRID:
    key = fstr(p)
    if key in CENSUS:
        na, ta = nstar_A(p, POOL_LO, POOL_HI)
        nb, tb = nstar_B(p, POOL_LO, POOL_HI)
        check("F3 n* twin p=%s" % key, (na, ta) == (nb, tb))
        check("F3 n*(%s) = %d" % (key, CENSUS[key]["n_star"]), na == CENSUS[key]["n_star"])
        check("F3 T*(%s) exact" % key, ta == frac(CENSUS[key]["T_star"]))
# the value at n=3 for the two above-wall cells IS a correct fact (just not the min)
check("F3 T(3,2/5) = 419/375 (value at n=3, exact)",
      T_A(3, WALL_P) == frac(FIX["anchors"]["T_at_n3_wall_cell"]))
check("F3 T(3,1/3) = 28/27 (value at n=3, exact)",
      T_A(3, Fraction(1, 3)) == frac(FIX["anchors"]["T_at_n3_p_third"]))
# grid-tail min at p=2/5 is n=64 (correct disclosure)
argmin_2_64_wall, min_2_64_wall = nstar_A(WALL_P, 2, POOL_HI)
check("F3 grid-tail argmin over {2..64} at p=2/5 is n=64",
      argmin_2_64_wall == 64 and min_2_64_wall == 1 + Fraction(1, 64) - (Fraction(3, 5)) ** 64)

# ---- disclosed above-wall summaries: re-derive and compare as REPORTING (C3)
DAW = FIX["anchors"]["disclosed_above_wall"]
# (1) practical-grid min over {2..8} at p = 2/5 : TRUE argmin/value
argmin_prac, min_prac = nstar_A(WALL_P, PRAC_LO, PRAC_HI)
disc_prac = DAW["wall_cell_practical_min"]
if not (argmin_prac == disc_prac["argmin_n"] and min_prac == frac(disc_prac["value"])):
    anomaly("disclosed practical-grid min at p=2/5 is a drafter slip: the "
            "registration claims '%s', but the TRUE min over {2..8} is "
            "T(%d, 2/5) = %s ~ %s at n = %d (the value 419/375 ~ 1.11733 is "
            "T(3,2/5), a LOCAL min, not the grid min). Cause pinned: above the "
            "wall T(n,2/5) = 1/n + 1 - (3/5)^n descends toward 1+ as n grows "
            "(1/n dominates the vanishing (3/5)^n), so the pool-grid minimum "
            "sits at the LARGEST n, not at the wall-optimal n=3. The R1 damage "
            "clause STILL FIRES on the true min (%s >= 21/20, margin x%s vs the "
            "disclosed x1.0641), so the ruling is untouched."
            % (disc_prac["claim"], argmin_prac, fstr(min_prac), f12(min_prac),
               argmin_prac, fstr(min_prac), f12(min_prac / Fraction(21, 20))))
# (2) grid min over {2..64} at p = 1/3
argmin_third, min_third = nstar_A(Fraction(1, 3), 2, POOL_HI)
disc_third = DAW["p_third_grid_min"]
if not (argmin_third == disc_third["argmin_n"] and min_third == frac(disc_third["value"])):
    anomaly("disclosed grid min at p=1/3 is the same-family slip: the "
            "registration (F3) claims '%s', but the TRUE min over {2..64} is "
            "T(%d, 1/3) = %s ~ %s at n = %d (28/27 ~ 1.03704 is T(3,1/3), the "
            "small-n LOCAL min; the tail dips below it from n=27 on and bottoms "
            "at n=64). Same mechanism as the p=2/5 slip: above the wall the "
            "pool-grid min sits at the largest n. This anchor is pure reporting "
            "(the 'double knife-edge' note); no decision clause reads it, so the "
            "ruling is untouched. The n=3 VALUE 28/27 and its status as a local "
            "min are both correct." % (disc_third["claim"], argmin_third,
                                       fstr(min_third), f12(min_third), argmin_third))
# (3) "best batch above the wall wastes 11.7%" -> the best practical batch (n=8)
best_waste_pct = float((min_prac - 1) * 100)
disc_waste = DAW["best_batch_waste_pct"]
if round(best_waste_pct, 1) != round(disc_waste["value_pct"], 1):
    anomaly("disclosed 'best batch above the wall wastes 11.7%%' inherits the "
            "same slip: the best PRACTICAL batch at p=2/5 is n=%d wasting "
            "%.2f%% (T=%s), not 11.7%% (which is n=3's waste); direction and "
            "order of magnitude stand." % (argmin_prac, best_waste_pct, fstr(min_prac)))

# ------------------------------------------------------------------ F4
hw = FIX["anchors"]["hand_world_F4"]
check("F4 hand world T(2,1/2) = 5/4 (both arms)",
      T_A(2, Fraction(1, 2)) == frac(hw["T"]) == T_B(2, Fraction(1, 2)))

# ------------------------------------------------------------------ F5
check("F5 p=0 -> T(n)=1/n all n", all(T_A(n, Fraction(0)) == Fraction(1, n) for n in range(2, POOL_HI + 1)))
check("F5 p=1 -> T(n)=1+1/n all n", all(T_A(n, Fraction(1)) == 1 + Fraction(1, n) for n in range(2, POOL_HI + 1)))
mono_ok = True
for n in range(2, POOL_HI + 1):
    seq = [T_A(n, q if False else Fraction(k, 100)) for k in range(0, 101)]
    if not all(seq[i] < seq[i + 1] for i in range(len(seq) - 1)):
        mono_ok = False
check("F5 T(n,p) strictly increasing in p at fixed n on the identity grid", mono_ok)

# ------------------------------------------ falsifiability world (C4, reporting)
def T_tilde(n, p):
    return 1 - (1 - p) ** n   # the 1/n term DELETED


falsify_all_lt1 = all(T_tilde(n, WALL_P) < 1 for n in range(2, POOL_HI + 1))
falsify_min = min(T_tilde(n, WALL_P) for n in range(2, POOL_HI + 1))
check("C4 falsifiability world: delete 1/n -> T~ < 1 for every n at p=2/5 (wall vanishes)",
      falsify_all_lt1)

# ------------------------------------------------ small-p sharpenings (reporting)
SHARP = FIX["anchors"]["small_p_sharpenings"]
sharp_rows = {}
for pk in ("1/400", "1/2500"):
    p = frac(pk)
    ns, ts = nstar_A(p, 1, 80)
    sharp_rows[pk] = {"n_star": ns, "T_star": f12(ts), "two_sqrt_p": f12(2 * float(p) ** 0.5)}
    check("sharpening n*(%s) = %d" % (pk, SHARP[pk]["n_star"]), ns == SHARP[pk]["n_star"])

# ------------------------------------------------- p = 3/10 straddle (reporting)
straddle_T3 = T_A(3, Fraction(3, 10))
check("straddle: p=3/10 T(3)=2971/3000 < 1 (last helping cell one step below wall)",
      straddle_T3 == Fraction(2971, 3000) and straddle_T3 < 1)

# --------------------------------------------------------- margin ledger (C5)
R1_min_prac = min_prac                       # true min over {2..8} at p=2/5
R2_floor = Fraction(1, 54)
R3_Tstar = frac(CENSUS["1/100"]["T_star"])
ledger = {
    "R1_practical_margin_x": f12(R1_min_prac / Fraction(21, 20)),
    "R1_practical_argmin_n": argmin_prac,
    "R1_practical_min": fstr(R1_min_prac),
    "R1_strict_note": "theorem: T(n,2/5) > 1 for every n in {2..64}; infimum over unbounded n is 1 (grid-bounded by design; n=64 tail = %s)" % f12(min_2_64_wall),
    "R2_floor_margin_x": "1.00 (equality at q=2/3, registered knife-edge)",
    "R2_floor": fstr(R2_floor),
    "R3_margin_x": f12((Fraction(1, 4)) / R3_Tstar),
    "T3_zero_note": "q^2 = 1/2 is the family's one true margin-0 cell; irrational, off every rational grid point (certified symbolically)",
}
# margin-0 census over the decision geometry: does ANY decision clause rest on 0?
margin0_clause = (R1_min_prac == Fraction(21, 20)) or (R2_floor == 0) or (R3_Tstar == Fraction(1, 4))
check("C5 no decision clause rests on a margin-0 cell", not margin0_clause)
# the two registered knife-edges are NOT decision clauses (disclosed, gated)
check("C5 R2 q=2/3 equality is a reporting knife-edge, not a decision clause "
      "(R2 uses the >= 1/54 floor over the grid, which holds strictly off q=2/3)",
      gap_min == Fraction(1, 54))

# --------------------------------------------------------- decision (twins)
def clause_R1(Tfn):
    strict = all(Tfn(n, WALL_P) > 1 for n in range(2, POOL_HI + 1))
    dmg = min(Tfn(n, WALL_P) for n in range(PRAC_LO, PRAC_HI + 1)) >= Fraction(21, 20)
    return strict and dmg


def clause_R2(Tfn):
    return all(Tfn(2, 1 - q) - Tfn(3, 1 - q) >= Fraction(1, 54) for q in QGRID)


def clause_R3(Tfn):
    ns, ts = (nstar_A if Tfn is T_A else nstar_B)(SAVE_P, POOL_LO, POOL_HI)
    return ts <= Fraction(1, 4)


def clause_APPROVE(Tfn):
    min_wall = min(Tfn(n, WALL_P) for n in range(2, POOL_HI + 1))
    pair_wins = any(Tfn(2, 1 - q) <= Tfn(3, 1 - q) for q in QGRID)
    return min_wall <= 1 and pair_wins


def evaluate(Tfn):
    r = clause_R1(Tfn) and clause_R2(Tfn) and clause_R3(Tfn)
    if r:
        return "REJECT"
    if CHECKS["failed"]:
        return "INVALID"
    if clause_APPROVE(Tfn):
        return "APPROVE"
    return "NULL"


ruling_A = evaluate(T_A)
ruling_B = evaluate(T_B)
check("F6 twin evaluators agree", ruling_A == ruling_B)
RULING = ruling_A if ruling_A == ruling_B else "INVALID"
# the falsifiability world genuinely flips to APPROVE (reporting)
falsify_ruling = evaluate(T_tilde) if False else ("APPROVE" if clause_APPROVE(T_tilde) else "not-APPROVE")

# ------------------------------------------------------- Arm R (reporting-only)
SEED_REGISTRY = []


def make_rng(seed):
    SEED_REGISTRY.append(seed)
    return random.Random(seed)


AR = FIX["arm_r"]


def arm_r_leg(rng, cells, N):
    """Simulate two-stage screening over N items per cell; return mean tests
    per item and the total Bernoulli draw count (n draws per pool)."""
    rows = {}
    draws_total = 0
    for cell in cells:
        p = float(frac(cell["p"]))
        n = cell["n"]
        tests = 0
        draws = 0
        pools = N // n
        for _ in range(pools):
            pos = False
            for _ in range(n):
                draws += 1
                if rng.random() < p:
                    pos = True
            tests += 1 + (n if pos else 0)
        items = pools * n
        rows[cell["p"] + "|n=" + str(n)] = {
            "mean_tests_per_item": tests / items,
            "exact_T": f12(T_A(n, frac(cell["p"]))),
            "items": items, "draws": draws}
        # draw-count sentinel: exactly n Bernoulli draws per pool
        check("F6 Arm-R draw sentinel %s (n per pool)" % cell["p"], draws == pools * n)
        draws_total += draws
    return rows, draws_total


rng_main = make_rng(AR["seed_main"])
r_main, draws_main = arm_r_leg(rng_main, AR["cells"], AR["main_N"])
rng_stab = make_rng(AR["seed_stability"])
r_stab, draws_stab = arm_r_leg(rng_stab, AR["cells"], AR["stability_N"])
# presentation seed read ONLY by a presentation leg (row order shuffle)
rng_pres = make_rng(AR["seed_presentation"])
pres_order = list(r_main.keys())
rng_pres.shuffle(pres_order)
check("F6 seed registry exact + order",
      SEED_REGISTRY == [AR["seed_main"], AR["seed_stability"], AR["seed_presentation"]])
check("F6 aux seed never read", AR["seed_aux_never_read"] not in SEED_REGISTRY)

# Arm-R preview beside the drafter's disclosed value (reporting; impl-dependent)
preview = r_main["1/10|n=4"]["mean_tests_per_item"]

# ------------------------------------------------------------------ output
results = {
    "verdict": RULING,
    "evaluators": [ruling_A, ruling_B],
    "decision_cells": {
        "wall_cell_p": fstr(WALL_P), "savings_cell_p": fstr(SAVE_P),
        "R1_strict_wall": all(T_A(n, WALL_P) > 1 for n in range(2, POOL_HI + 1)),
        "R1_practical_min_over_2_8": fstr(R1_min_prac),
        "R1_practical_min_float": f12(R1_min_prac),
        "R1_practical_argmin_n": argmin_prac,
        "R1_gridtail_min_over_2_64": f12(min_2_64_wall),
        "R2_identity": "T(2,q) - T(3,q) = (q - 2/3)^2 (q + 1/3) + 1/54; floor 1/54 at q=2/3",
        "R2_grid_floor": fstr(gap_min),
        "R3_Tstar_1_100": fstr(R3_Tstar), "R3_Tstar_float": f12(R3_Tstar),
        "R3_nstar_1_100": CENSUS["1/100"]["n_star"],
        "bands": {"reject": "R1 strict wall + min{2..8} >= 21/20; R2 gap >= 1/54; R3 T*(1/100) <= 1/4",
                  "approve": "min{2..64} T(n,2/5) <= 1 AND pair <= triple somewhere"}},
    "wall": {
        "p_star": "1 - 3^(-1/3) ~ 0.306566",
        "argmin_n_forgiving": best_forgiving,
        "helps_by_p": {fstr(p): (3 * (1 - p) ** 3 > 1) for p in PGRID},
        "certificate": "pooling helps at p for some n in {2..64} iff 3q^3 > 1"},
    "identities": {
        "T2_coeff_match": norm_poly(D23) == norm_poly(claim23),
        "T2_grid_floor": fstr(gap_min), "T2_equality_q": fstr(gap_argq),
        "T3_coeff_match": norm_poly(D24) == norm_poly(claim24),
        "T3_margin0": "q^2 = 1/2 (irrational, off grid)"},
    "census_helping": {fstr(p): {"n_star": nstar_A(p, POOL_LO, POOL_HI)[0],
                                 "T_star": fstr(nstar_A(p, POOL_LO, POOL_HI)[1]),
                                 "T_star_float": f12(nstar_A(p, POOL_LO, POOL_HI)[1])}
                       for p in PGRID if fstr(p) in CENSUS},
    "above_wall_corrected": {
        "wall_cell_p_2_5": {"true_min_over_2_8": fstr(R1_min_prac), "argmin_n": argmin_prac,
                            "disclosed": DAW["wall_cell_practical_min"]["claim"],
                            "value_at_n3": fstr(T_A(3, WALL_P))},
        "p_1_3": {"true_min_over_2_64": fstr(min_third), "argmin_n": argmin_third,
                  "disclosed": DAW["p_third_grid_min"]["claim"],
                  "value_at_n3": fstr(T_A(3, Fraction(1, 3)))}},
    "falsifiability_world": {
        "T_tilde_all_lt_1_at_p_2_5": falsify_all_lt1,
        "T_tilde_min_at_p_2_5": f12(falsify_min),
        "flips_to": falsify_ruling,
        "note": "delete the 1/n pool-test cost and the wall vanishes; the verdict flips to APPROVE outright"},
    "small_p_sharpenings": sharp_rows,
    "straddle_p_3_10": {"T3": fstr(straddle_T3), "T3_float": f12(straddle_T3), "helps": bool(straddle_T3 < 1)},
    "margin_ledger": ledger,
    "arm_r": {
        "main": {k: {"measured": f12(v["mean_tests_per_item"]), "exact": v["exact_T"], "items": v["items"]}
                 for k, v in r_main.items()},
        "stability": {k: {"measured": f12(v["mean_tests_per_item"]), "exact": v["exact_T"], "items": v["items"]}
                      for k, v in r_stab.items()},
        "preview_cell_1_10_n4": {"measured": f12(preview), "exact": "5939/10000",
                                 "disclosed_preview": FIX["anchors"]["arm_r_preview"]["measured_disclosed"]},
        "draws": {"main": draws_main, "stability": draws_stab},
        "presentation_order": pres_order,
        "seed_registry": SEED_REGISTRY, "aux_never_read": AR["seed_aux_never_read"],
        "note": "REPORTING-ONLY; no statistical gate rides Arm R"},
    "anomalies": ANOMALIES,
    "self_checks": {"passed": CHECKS["passed"], "failed": CHECKS["failed"], "failures": FAILURES},
}
(HERE / "results.json").write_text(
    json.dumps(results, sort_keys=True, ensure_ascii=True, indent=2) + "\n",
    encoding="utf-8", newline="\n")

out = []
out.append("VERDICT 085 runner — the pooled-screening prevalence wall (P072)")
out.append("ruling: %s (evaluators %s/%s)" % (RULING, ruling_A, ruling_B))
out.append("wall: pooling helps iff 3q^3 > 1 iff p < p* = 1 - 3^(-1/3) ~ 0.306566; "
           "argmin_n n^(-1/n) = %d (integer-power certified)" % best_forgiving)
out.append("  helps by p: %s" % {fstr(p): (3 * (1 - p) ** 3 > 1) for p in PGRID})
out.append("R1 (p=2/5): strict wall T(n)>1 all n in 2..64 = %s; TRUE min over {2..8} = %s ~ %s at n=%d "
           "(band >= 21/20, margin x%s); grid-tail min over {2..64} ~ %s at n=64"
           % (all(T_A(n, WALL_P) > 1 for n in range(2, POOL_HI + 1)), fstr(R1_min_prac),
              f12(R1_min_prac), argmin_prac, f12(R1_min_prac / Fraction(21, 20)), f12(min_2_64_wall)))
out.append("R2: T(2,q)-T(3,q) = (q-2/3)^2(q+1/3) + 1/54 (coeff-match %s); grid floor %s at q=%s (band >= 1/54)"
           % (norm_poly(D23) == norm_poly(claim23), fstr(gap_min), fstr(gap_argq)))
out.append("R3 (p=1/100): T*(1/100) = %s ~ %s at n*=%d (band <= 1/4, margin x%s)"
           % (fstr(R3_Tstar), f12(R3_Tstar), CENSUS["1/100"]["n_star"], f12(Fraction(1, 4) / R3_Tstar)))
out.append("T3 degeneracy: T(2,q)-T(4,q) = (q^2-1/2)^2 (coeff-match %s); margin-0 at q^2=1/2 off-grid; 2^4=4^2"
           % (norm_poly(D24) == norm_poly(claim24)))
out.append("census helping cells (n*, T*): %s"
           % {fstr(p): "%d,%s" % (nstar_A(p, POOL_LO, POOL_HI)[0], f12(nstar_A(p, POOL_LO, POOL_HI)[1]))
              for p in PGRID if fstr(p) in CENSUS})
out.append("above-wall CORRECTED: p=2/5 true min{2..8} = %s at n=%d (disclosed 419/375 at n=3); "
           "p=1/3 true min{2..64} = %s at n=%d (disclosed 28/27 at n=3)"
           % (fstr(R1_min_prac), argmin_prac, fstr(min_third), argmin_third))
out.append("falsifiability world (delete 1/n): T~ < 1 all n at p=2/5 = %s (min %s) -> flips to %s"
           % (falsify_all_lt1, f12(falsify_min), falsify_ruling))
out.append("straddle p=3/10: T(3) = %s < 1 (last helping cell, one grid step below the wall)" % fstr(straddle_T3))
out.append("margin ledger: R1 x%s (min at n=%d), R2 x1.00 at q=2/3 (registered knife-edge), R3 x%s; "
           "T3 zero q^2=1/2 off-grid; no decision clause margin-0"
           % (f12(R1_min_prac / Fraction(21, 20)), argmin_prac, f12(Fraction(1, 4) / R3_Tstar)))
out.append("arm R (reporting-only): main %s | stability %s | exact %s"
           % ({k: round(v["mean_tests_per_item"], 4) for k, v in r_main.items()},
              {k: round(v["mean_tests_per_item"], 4) for k, v in r_stab.items()},
              {k: v["exact_T"] for k, v in r_main.items()}))
out.append("  preview cell (p=1/10,n=4): measured %s vs exact 0.5939 (disclosed preview %s)"
           % (f12(preview), FIX["anchors"]["arm_r_preview"]["measured_disclosed"]))
out.append("anomalies: %s" % ("NONE" if not ANOMALIES else " | ".join(ANOMALIES)))
out.append("self-checks: %d passed, %d failed%s"
           % (CHECKS["passed"], CHECKS["failed"],
              "" if not FAILURES else " — " + "; ".join(FAILURES[:10])))
stdout_text = "\n".join(out) + "\n"
(HERE / "run-stdout.txt").write_text(stdout_text, encoding="utf-8", newline="\n")
sys.stdout.write(stdout_text)
# exit contract: the decision arms are exact and REJECT-first; no sim self-check
# is designed to fail (the disclosed above-wall slips are ANOMALIES via C3, not
# gate failures). Any check failure is a hard red.
sys.exit(0 if not FAILURES else 1)
