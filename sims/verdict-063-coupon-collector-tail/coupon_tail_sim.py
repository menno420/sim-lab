#!/usr/bin/env python3
"""VERDICT 063 — coupon collector's tail (idea-engine PROPOSAL 052).

Does "almost complete" mean "almost done"? Under the uniform coupon
collector (N distinct items, one uniform iid draw per tick), what fraction
phi(N) = H_m/H_N of the expected total draws E[T_N] = N*H_N does the LAST
m = ceil(N/10) of the set cost, over the pre-registered grid
N in {20, 50, 100, 200} (decision cell N = 50)?

Arm A (DECISION, seedless, exact): fractions.Fraction harmonic sums
re-derived from scratch — H_N by direct ascending sum AND by the
independently-structured stage-expectation accounting
(sum_{j=0..N-1} N/(N-j))/N, identical rationals required; E[T_N] = N*H_N,
E[tail_m] = N*H_m, phi = H_m/H_N, the last-single-coupon share 1/H_N, the
last-20% alternative column, and the inclusion-exclusion overshoot report
P(T_50 > 2*E[T_50]) = P(T_50 > 449) exact. The ruling rides Arm A alone.

Arm S (confirmation, seeded MC): N_runs = 200,000 draw-until-complete
trajectories per grid cell via random.Random(20261345); pinned cell order
N ascending, then the F5 control cells N in {2, 3}; pinned per-draw
primitive: ONE rng.random() call per draw, index = int(u*N). Agreement
gate per cell on E[T_N] AND phi: |mean_S - E_A|/E_A <= 1/100 AND
|mean_S - E_A| <= 4*SE (phi-hat = ratio of means, delta-method SE — both
conventions pinned in fixtures.json). Any breach invalidates the run.
Seeds 20261345 main / 20261346 stability (N = 20,000, ruling reproduced
through twin independently-written evaluators) / 20261347 reporting-only
legs (last-20% alternative; weighted rarity-tier collector, MC only) /
20261348 aux (reserved, NEVER read) — the ONLY four RNGs constructed, in
pinned order.

Decision rule, registered, applied IN ORDER: REJECT first (phi(50) >= 2/5
AND phi >= 2/5 in >= 3 of 4 cells AND Arm S confirms), then INVALID (any
control gate — every control is a hard self-check: failure exits 1 with no
ruling), then APPROVE (phi <= 1/5 at EVERY N AND stability reproduces),
else NULL (pre-registered axes). Reporting-only legs can NEVER flip the
decision.

Hermetic: reads only its own fixtures.json. Stdlib only. No wall-clock in
any output. Byte-identical stdout + results.json across process runs.

Run: python3 sims/verdict-063-coupon-collector-tail/coupon_tail_sim.py
"""

import itertools
import json
import math
import os
import platform
import random
import sys
from fractions import Fraction

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- self-checks
_CHECKS = {"passed": 0, "failed": 0}


def check(cond, label):
    if cond:
        _CHECKS["passed"] += 1
    else:
        _CHECKS["failed"] += 1
        print("SELF-CHECK FAIL: %s" % label)
        sys.exit(1)


def Fr(d):
    return Fraction(d["num"], d["den"])


def fr(x):
    return "%d/%d" % (x.numerator, x.denominator)


# ------------------------------------------------------------------- fixtures
with open(os.path.join(BASE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

# ------------------------------------------------------------- environment pin
check(platform.python_implementation() == "CPython", "interpreter is CPython")
check(list(sys.version_info[:2]) == FX["environment"]["cpython_minor"],
      "CPython minor version pinned in fixtures matches runner")

# --------------------------------------------------- transcription gates exact
GRID = list(FX["model"]["decision_grid_N"])
TAIL_M = list(FX["model"]["tail_m"])
CELL_N = FX["model"]["decision_cell_N"]
L20_M = list(FX["model"]["last20_alternative_m"])
T_STAR = FX["model"]["overshoot_report"]["t_star"]
BAND_R = Fr(FX["decision_rule"]["reject_band"])
BAND_A = Fr(FX["decision_rule"]["approve_band"])
CELLS_REQ = FX["decision_rule"]["reject_cells_required"]
TOL_REL = Fr(FX["decision_rule"]["agreement_tolerance"]["relative"])
SE_MULT = FX["decision_rule"]["agreement_tolerance"]["se_multiplier"]
SEED_MAIN = FX["arm_S"]["seed_main"]
SEED_STAB = FX["arm_S"]["seed_stability"]
SEED_REP = FX["arm_S"]["seed_reporting"]
SEED_AUX = FX["arm_S"]["seed_aux"]
N_MAIN = FX["arm_S"]["N_main"]
N_F5 = FX["arm_S"]["f5_control_N_runs"]
N_STAB = FX["arm_S"]["N_stability"]
N_REP = FX["arm_S"]["N_reporting"]
TIER_MASS = [Fr(d) for d in FX["weighted_rarity_tier"]["tier_mass"]]
TIER_COUNTS = {int(k): list(v) for k, v in
               FX["weighted_rarity_tier"]["tier_counts_by_N"].items()}
F5_T_LO, F5_T_HI = FX["gates"]["F5"]["t_range"]

check(GRID == [20, 50, 100, 200], "transcription: decision grid N")
check(TAIL_M == [2, 5, 10, 20] and
      TAIL_M == [(n + 9) // 10 for n in GRID],
      "transcription: tail m = ceil(N/10) = {2, 5, 10, 20}")
check(CELL_N == 50, "transcription: decision cell N = 50")
check(L20_M == [4, 10, 20, 40] and
      L20_M == [(n + 4) // 5 for n in GRID],
      "transcription: last-20% alternative m = ceil(N/5) = {4, 10, 20, 40}")
check(BAND_R == Fraction(2, 5) and BAND_A == Fraction(1, 5),
      "transcription: bands REJECT 2/5, APPROVE 1/5 (exact, disjoint)")
check(CELLS_REQ == 3, "transcription: REJECT needs >= 3 of 4 cells")
check(TOL_REL == Fraction(1, 100) and SE_MULT == 4,
      "transcription: agreement tolerance 1/100 relative AND 4*SE")
check([SEED_MAIN, SEED_STAB, SEED_REP, SEED_AUX] ==
      [20261345, 20261346, 20261347, 20261348],
      "transcription: seeds 20261345-348 in pinned order")
check(N_MAIN == 200000 and N_F5 == 200000 and N_STAB == 20000 and
      N_REP == 20000, "transcription: trajectory counts 200k/200k/20k/20k")
check(TIER_MASS == [Fraction(7, 10), Fraction(1, 4), Fraction(1, 20)],
      "transcription: tier masses 70%/25%/5%")
check(sum(TIER_MASS) == 1, "tier masses sum to 1 exactly")
for n in GRID:
    c1, c2, c3 = TIER_COUNTS[n]
    check(c1 == (7 * n) // 10 and c2 == n // 4 and c3 == n - c1 - c2
          and c3 >= 1,
          "transcription: tier integer split floor/floor/remainder at N=%d"
          % n)
check(TIER_COUNTS == {20: [14, 5, 1], 50: [35, 12, 3], 100: [70, 25, 5],
                      200: [140, 50, 10]},
      "transcription: pinned tier counts table")
check((F5_T_LO, F5_T_HI) == (1, 12), "transcription: F5 t range 1..12")
check(T_STAR == 449, "transcription: overshoot t* = 449")

# ============================================================ ARM A (DECISION)
NMAX = max(GRID)

# derivation ONE: direct ascending harmonic sums H[1..NMAX]
H = [None] * (NMAX + 1)
acc = Fraction(0)
for k in range(1, NMAX + 1):
    acc += Fraction(1, k)
    H[k] = acc


def stage_sum(N, j_lo, j_hi):
    """derivation TWO structure: sum of geometric stage expectations
    N/(N-j) for j in [j_lo, j_hi] — the linearity accounting."""
    s = Fraction(0)
    for j in range(j_lo, j_hi + 1):
        s += Fraction(N, N - j)
    return s


# F1 — harmonic re-derivation exact (twin structures identical rationals)
for n in sorted(set(GRID + [2, 3, 5, 10] + TAIL_M + L20_M)):
    check(H[n] == stage_sum(n, 0, n - 1) / n,
          "F1: H_%d direct sum == stage-sum re-derivation" % n)
check(H[5] == Fr(FX["gates"]["F1"]["H5"]), "F1: H_5 = 137/60 exact")
check(H[10] == Fr(FX["gates"]["F1"]["H10"]), "F1: H_10 = 7381/2520 exact")

# F2 — linearity identity + stage accounting, per grid cell
E_T = {}
E_TAIL = {}
PHI = {}
for n, m in zip(GRID, TAIL_M):
    tot = stage_sum(n, 0, n - 1)
    head = stage_sum(n, 0, n - m - 1)
    tail = stage_sum(n, n - m, n - 1)
    check(tot == n * H[n], "F2: E[T_%d] stage sum == N*H_N" % n)
    check(tail == n * H[m], "F2: E[tail_%d@N=%d] stage sum == N*H_m" % (m, n))
    check(head + tail == tot,
          "F2: stage accounting head+tail == total at N=%d" % n)
    E_T[n] = tot
    E_TAIL[n] = tail
    PHI[n] = H[m] / H[n]
    check(PHI[n] == tail / tot, "F2: phi == E[tail]/E[T] at N=%d" % n)

# F3 — boundary identities
for n in GRID:
    check(H[n] / H[n] == 1, "F3: phi(N=%d, m=N) == 1" % n)
    check(H[1] / H[n] == 1 / H[n], "F3: phi(N=%d, m=1) == 1/H_N" % n)

# F4 — monotonicity theorems
for n in GRID:
    prev = None
    for m in range(1, n + 1):
        cur = H[m] / H[n]
        if prev is not None:
            check(cur >= prev,
                  "F4a: phi non-decreasing in m at N=%d (m=%d)" % (n, m))
        prev = cur
for n in range(1, NMAX):
    check(n * H[n] < (n + 1) * H[n + 1],
          "F4b: E[T_N] strictly increasing at N=%d" % n)
for n in GRID:
    check(Fraction(n, n - (n - 1)) == n,
          "F4c: last-coupon stage expectation exactly N at N=%d" % n)

# inclusion-exclusion CDF (exact)
def cdf(N, t):
    s = Fraction(0)
    for j in range(N + 1):
        s += (-1) ** j * math.comb(N, j) * Fraction(N - j, N) ** t
    return s


# F5 — small-N exact CDF vs FULL ENUMERATION + expectation pins
F5_TABLE = {}
for n in (2, 3):
    rows = []
    for t in range(F5_T_LO, F5_T_HI + 1):
        cnt = 0
        for seq in itertools.product(range(n), repeat=t):
            if len(set(seq)) == n:
                cnt += 1
        p_enum = Fraction(cnt, n ** t)
        p_cdf = cdf(n, t)
        check(p_enum == p_cdf,
              "F5: enumeration == inclusion-exclusion at N=%d t=%d" % (n, t))
        rows.append({"t": t, "P_exact": fr(p_cdf),
                     "P_float": float(p_cdf), "enum_count": cnt})
    F5_TABLE[n] = rows
check(2 * H[2] == Fr(FX["gates"]["F5"]["E_T2"]), "F5: E[T_2] = 3 exact")
check(3 * H[3] == Fr(FX["gates"]["F5"]["E_T3"]), "F5: E[T_3] = 11/2 exact")
check(stage_sum(2, 0, 1) == 3 and stage_sum(3, 0, 2) == Fraction(11, 2),
      "F5: small-N expectations reproduce through the stage accounting")

# overshoot report (exact, reporting)
E_T50 = 50 * H[50]
check(math.floor(2 * E_T50) == T_STAR and (2 * E_T50) != T_STAR,
      "overshoot: t* = floor(2*E[T_50]) = 449 and 2E is not an integer")
P_OVER = 1 - cdf(50, T_STAR)
check(0 < P_OVER < 1, "overshoot: P(T_50 > 449) in (0, 1)")

# last-20% alternative column (exact, reporting)
PHI_L20 = {n: H[m] / H[n] for n, m in zip(GRID, L20_M)}
# last-single-coupon share (exact)
SHARE_1 = {n: 1 / H[n] for n in GRID}

# ===================================== twin independently-written evaluators
def eval_one(phi_tab):
    """evaluator ONE — procedural Fraction comparisons on the registered
    band arithmetic; returns (arith_class, over, under, phi50_ge)."""
    over = 0
    under = 0
    for n in GRID:
        if phi_tab[n] >= BAND_R:
            over += 1
        if phi_tab[n] <= BAND_A:
            under += 1
    phi50_ge = phi_tab[CELL_N] >= BAND_R
    if phi50_ge and over >= CELLS_REQ:
        cls = "REJECT_ARITH"
    elif under == len(GRID):
        cls = "APPROVE_ARITH"
    else:
        cls = "NULL_ARITH"
    return cls, over, under, phi50_ge


def eval_two(phi_tab):
    """evaluator TWO — pure-integer cross-multiplication, no Fraction
    comparison operators: p/q >= a/b  <=>  p*b >= a*q (q, b > 0)."""
    rn, rd = 2, 5
    an, ad = 1, 5
    over = 0
    under = 0
    phi50_ge = False
    for n in GRID:
        p, q = phi_tab[n].numerator, phi_tab[n].denominator
        if p * rd >= rn * q:
            over += 1
            if n == 50:
                phi50_ge = True
        if p * ad <= an * q:
            under += 1
    if phi50_ge and over >= 3:
        cls = "REJECT_ARITH"
    elif under == 4:
        cls = "APPROVE_ARITH"
    else:
        cls = "NULL_ARITH"
    return cls, over, under, phi50_ge


def eval_both(phi_tab, label):
    r1 = eval_one(phi_tab)
    r2 = eval_two(phi_tab)
    check(r1 == r2, "twin evaluators agree on table: %s" % label)
    return r1


ARITH = eval_both(PHI, "Arm A decision table")

# ======================================================== the ONLY four RNGs
class CountingRandom(random.Random):
    """The counting RNG wrapper — every random() call is tallied so the
    per-leg draw sentinels are checked against an actual call count."""

    def __init__(self, seed):
        super().__init__(seed)
        self.calls = 0

    def random(self):
        self.calls += 1
        return super().random()


# constructed in pinned order — the ONLY four
RNG_MAIN = CountingRandom(SEED_MAIN)
RNG_STAB = CountingRandom(SEED_STAB)
RNG_REP = CountingRandom(SEED_REP)
RNG_AUX = CountingRandom(SEED_AUX)


# ------------------------------------------------------------------ MC legs
def mc_uniform_leg(rng, N, m, n_runs, hist_tmax=0):
    """Draw-until-complete under the pinned primitive int(u*N); records the
    completion tick T and the tail draws T - mark (mark = tick of the
    (N-m)-th distinct acquisition; m = N -> mark = 0). Returns integer
    sums (exact) + optional T-histogram counts for the F5 CDF gate."""
    r = rng.random
    mark_at = N - m
    st = st2 = sq = sq2 = sxq = 0
    hist = [0] * (hist_tmax + 1) if hist_tmax else None
    calls_before = rng.calls
    for _ in range(n_runs):
        seen = bytearray(N)
        distinct = 0
        d = 0
        mark = 0
        while distinct < N:
            d += 1
            i = int(r() * N)
            if not seen[i]:
                seen[i] = 1
                distinct += 1
                if distinct == mark_at:
                    mark = d
        q = d - mark
        st += d
        st2 += d * d
        sq += q
        sq2 += q * q
        sxq += d * q
        if hist is not None and d <= hist_tmax:
            hist[d] += 1
    check(rng.calls - calls_before == st,
          "sentinel: leg N=%d m=%d n=%d — random() calls == recorded draws"
          % (N, m, n_runs))
    return {"st": st, "st2": st2, "sq": sq, "sq2": sq2, "sxq": sxq,
            "n": n_runs, "hist": hist}


def mc_weighted_leg(rng, N, counts, m, n_runs):
    """Weighted rarity-tier collector — the pinned one-call-per-draw tier
    construction from fixtures.json; MC only (disclosed)."""
    r = rng.random
    c1, c2, c3 = counts
    mark_at = N - m
    st = sq = 0
    calls_before = rng.calls
    for _ in range(n_runs):
        seen = bytearray(N)
        distinct = 0
        d = 0
        mark = 0
        while distinct < N:
            d += 1
            u = r()
            if u < 0.7:
                i = int((u / 0.7) * c1)
                if i >= c1:
                    i = c1 - 1
            elif u < 0.95:
                i = c1 + min(c2 - 1, int(((u - 0.7) / 0.25) * c2))
            else:
                i = c1 + c2 + min(c3 - 1, int(((u - 0.95) / 0.05) * c3))
            if not seen[i]:
                seen[i] = 1
                distinct += 1
                if distinct == mark_at:
                    mark = d
        st += d
        sq += d - mark
    check(rng.calls - calls_before == st,
          "sentinel: weighted leg N=%d n=%d — random() calls == recorded "
          "draws" % (N, n_runs))
    return {"st": st, "sq": sq, "n": n_runs}


def leg_stats(leg):
    """Exact means + float SEs under the pinned conventions."""
    n = leg["n"]
    mean_T = Fraction(leg["st"], n)
    phi_hat = Fraction(leg["sq"], leg["st"])
    denom = n * (n - 1)
    var_t = float(n * leg["st2"] - leg["st"] * leg["st"]) / denom
    se_T = math.sqrt(var_t / n)
    var_q = float(n * leg["sq2"] - leg["sq"] * leg["sq"]) / denom
    cov_qt = float(n * leg["sxq"] - leg["st"] * leg["sq"]) / denom
    ph = float(phi_hat)
    mt = leg["st"] / n
    inner = (var_q - 2.0 * ph * cov_qt + ph * ph * var_t) / n
    se_phi = math.sqrt(inner if inner > 0 else 0.0) / mt
    return mean_T, phi_hat, se_T, se_phi


def gate_leg(leg, E_exact, phi_exact, label):
    """The registered agreement gate — E[T] AND phi, 1/100 relative AND
    4*SE; any breach is a hard check (the INVALID landing)."""
    mean_T, phi_hat, se_T, se_phi = leg_stats(leg)
    dev_E = abs(mean_T - E_exact)
    check(dev_E / E_exact <= TOL_REL,
          "agreement gate E[T] relative <= 1/100: %s" % label)
    check(float(dev_E) <= SE_MULT * se_T,
          "agreement gate E[T] within 4*SE: %s" % label)
    dev_p = abs(phi_hat - phi_exact)
    check(dev_p / phi_exact <= TOL_REL,
          "agreement gate phi relative <= 1/100: %s" % label)
    check(float(dev_p) <= SE_MULT * se_phi,
          "agreement gate phi within 4*SE: %s" % label)
    return {"mean_T": fr(mean_T), "mean_T_float": float(mean_T),
            "phi_hat": fr(phi_hat), "phi_hat_float": float(phi_hat),
            "dev_E_float": float(dev_E), "four_se_T": SE_MULT * se_T,
            "dev_phi_float": float(dev_p), "four_se_phi": SE_MULT * se_phi,
            "draws": leg["st"]}


# ------------------------------- ARM S main (seed 20261345, pinned leg order)
main_legs = {}
for n, m in zip(GRID, TAIL_M):
    leg = mc_uniform_leg(RNG_MAIN, n, m, N_MAIN)
    main_legs[n] = (leg, gate_leg(leg, E_T[n], PHI[n],
                                  "main seed 20261345 N=%d" % n))
ARM_S_CONFIRMS = True  # every gate above is a hard check — reaching here
check(ARM_S_CONFIRMS, "Arm S confirms within tolerance on every grid cell")

# F5 control legs (main seed, after the grid cells — pinned order)
f5_legs = {}
for n in (2, 3):
    m = (n + 9) // 10
    check(m == 1, "F5 control tail m = ceil(N/10) = 1 at N=%d" % n)
    leg = mc_uniform_leg(RNG_MAIN, n, m, N_F5, hist_tmax=F5_T_HI)
    E_exact = n * H[n]
    mean_T, phi_hat, se_T, _ = leg_stats(leg)
    dev_E = abs(mean_T - E_exact)
    check(dev_E / E_exact <= TOL_REL,
          "F5 Arm S mean gate relative <= 1/100 at N=%d" % n)
    check(float(dev_E) <= SE_MULT * se_T,
          "F5 Arm S mean gate within 4*SE at N=%d" % n)
    cum = 0
    cdf_rows = []
    for t in range(F5_T_LO, F5_T_HI + 1):
        cum += leg["hist"][t]
        p_hat = Fraction(cum, N_F5)
        p_ex = cdf(n, t)
        dev = abs(p_hat - p_ex)
        se_b = math.sqrt(float(p_ex) * (1.0 - float(p_ex)) / N_F5)
        check(dev <= Fraction(1, 100),
              "F5 CDF point gate <= 1/100 at N=%d t=%d" % (n, t))
        check(float(dev) <= SE_MULT * se_b,
              "F5 CDF point gate within 4*SE at N=%d t=%d" % (n, t))
        cdf_rows.append({"t": t, "P_hat_float": float(p_hat),
                         "P_exact_float": float(p_ex),
                         "dev_float": float(dev),
                         "four_se": SE_MULT * se_b})
    f5_legs[n] = {"mean_T_float": float(mean_T),
                  "E_exact": fr(E_exact),
                  "dev_E_float": float(dev_E), "four_se_T": SE_MULT * se_T,
                  "phi_hat_float": float(phi_hat),
                  "draws": leg["st"], "cdf_points": cdf_rows}
MAIN_CALLS = RNG_MAIN.calls

# --------------------------- STABILITY leg (seed 20261346, twin evaluators)
stab_tab = {}
stab_report = {}
stab_worst = Fraction(0)
stab_worst_leg = ""
for n, m in zip(GRID, TAIL_M):
    leg = mc_uniform_leg(RNG_STAB, n, m, N_STAB)
    mean_T, phi_hat, se_T, se_phi = leg_stats(leg)
    stab_tab[n] = phi_hat
    dev = abs(phi_hat - PHI[n]) / PHI[n]
    if dev > stab_worst:
        stab_worst, stab_worst_leg = dev, "N=%d" % n
    stab_report[n] = {"phi_hat": fr(phi_hat),
                      "phi_hat_float": float(phi_hat),
                      "mean_T_float": float(mean_T),
                      "rel_dev_phi_float": float(dev), "draws": leg["st"]}
STAB_CLS = eval_both(stab_tab, "stability phi-hat table (seed 20261346)")
check(STAB_CLS[0] == ARITH[0],
      "stability leg reproduces the ruling class through twin evaluators")
STAB_CALLS = RNG_STAB.calls

# ----------------- REPORTING-ONLY legs (seed 20261347 — can NEVER flip)
# (a) last-20% alternative, uniform model, m = ceil(N/5)
l20_report = {}
for n, m in zip(GRID, L20_M):
    leg = mc_uniform_leg(RNG_REP, n, m, N_REP)
    mean_T, phi_hat, se_T, se_phi = leg_stats(leg)
    l20_report[n] = {"m": m, "phi_exact": fr(PHI_L20[n]),
                     "phi_exact_float": float(PHI_L20[n]),
                     "phi_hat_float": float(phi_hat),
                     "mean_T_float": float(mean_T),
                     "rel_dev_phi_float":
                         float(abs(phi_hat - PHI_L20[n]) / PHI_L20[n]),
                     "draws": leg["st"]}
L20_CLS = eval_both(PHI_L20, "last-20% exact table (reporting)")
# (b) weighted rarity-tier collector, m = ceil(N/10), MC only (disclosed)
wt_tab = {}
wt_report = {}
for n, m in zip(GRID, TAIL_M):
    leg = mc_weighted_leg(RNG_REP, n, TIER_COUNTS[n], m, N_REP)
    mean_T = Fraction(leg["st"], leg["n"])
    phi_hat = Fraction(leg["sq"], leg["st"])
    wt_tab[n] = phi_hat
    wt_report[n] = {"tier_counts": TIER_COUNTS[n],
                    "mean_T_float": float(mean_T),
                    "phi_hat_float": float(phi_hat),
                    "uniform_phi_float": float(PHI[n]),
                    "delta_vs_uniform_float": float(phi_hat - PHI[n]),
                    "draws": leg["st"]}
WT_CLS = eval_both(wt_tab, "weighted-tier phi-hat table (reporting)")
REP_CALLS = RNG_REP.calls

# ------------------------------------------------------------- sentinels/aux
check(RNG_AUX.calls == 0,
      "sentinel seed 20261348 (aux): 0 random() calls — reserved, never "
      "read by any decision number")
check(RNG_MAIN.calls == MAIN_CALLS and RNG_STAB.calls == STAB_CALLS and
      RNG_REP.calls == REP_CALLS,
      "sentinel: no RNG consumed outside its own pinned legs")

# ------------------------------------------ RULING (registered order, exact)
if ARITH[0] == "REJECT_ARITH" and ARM_S_CONFIRMS:
    FINAL = "reject"
    final_note = ("REJECT fires (checked FIRST): phi(50) >= 2/5 AND "
                  "phi >= 2/5 in %d of 4 cells (3 required) AND Arm S "
                  "confirms within tolerance on every grid cell"
                  % ARITH[1])
elif ARITH[0] == "APPROVE_ARITH" and STAB_CLS[0] == ARITH[0]:
    FINAL = "approve"
    final_note = ("APPROVE fires: phi <= 1/5 at every N and the stability "
                  "leg reproduces")
else:
    FINAL = "null"
    final_note = "NULL per 'anything else' — see axis flags"
# INVALID cannot be reached here: every control gate is a hard self-check
# (a failure prints SELF-CHECK FAIL and exits 1 with no ruling — the
# registered INVALID landing, evaluated between REJECT and APPROVE by
# construction: REJECT's own conjuncts are the arithmetic + the Arm-S
# agreement gate, which precede this point).

# NULL axis bookkeeping (reported always; binding only on NULL)
def band_pos(x):
    if x >= BAND_R:
        return "GE_2/5"
    if x <= BAND_A:
        return "LE_1/5"
    return "STRADDLE"


axis_flags = {
    "band_straddle_phi50_in_open_interval":
        BAND_A < PHI[CELL_N] < BAND_R,
    "N_sensitivity_phi_crosses_a_band_across_grid":
        len(set(band_pos(PHI[n]) for n in GRID)) > 1,
    "weight_sensitivity_weighted_leg_would_flip":
        WT_CLS[0] != ARITH[0],
    "arm_disagreement": False,  # gate passed or the run would have exited
}

# ------------------------------------------------------- drafter comparison
DRAFTER = FX["drafter_reference_never_gated"]
drafter_cmp = []
for e in DRAFTER["expected_phi"]:
    n = e["N"]
    meas = PHI[n]
    drafter_cmp.append({
        "N": n, "drafter_phi_approx": e["phi_approx"],
        "drafter_expr": e["phi_expr"],
        "measured_phi": fr(meas), "measured_phi_float": float(meas),
        "matches_within_1e-3": abs(float(meas) - e["phi_approx"]) <= 1e-3,
    })
drafter_class_match = ((DRAFTER["expected_class"] == "REJECT")
                       == (FINAL == "reject"))

# ------------------------------------------------------------------ output
out = []
out.append("VERDICT 063 — coupon collector's tail (idea-engine PROPOSAL 052)")
out.append("registration: %s" % FX["registration"]["proposal_header"])
out.append("environment: CPython %d.%d (pinned)" % tuple(sys.version_info[:2]))
out.append("")
out.append("ARM A (DECISION, exact Fractions, seedless) — the phi(N) grid, "
           "m = ceil(N/10):")
for n, m in zip(GRID, TAIL_M):
    out.append("  N=%-3d m=%-2d E[T]=%-12.4f E[tail]=%-11.4f phi=%.6f "
               "(exact %s) 1/H_N=%.6f"
               % (n, m, float(E_T[n]), float(E_TAIL[n]), float(PHI[n]),
                  fr(PHI[n])[:40] + ("..." if len(fr(PHI[n])) > 40 else ""),
                  float(SHARE_1[n])))
out.append("  overshoot: P(T_50 > 2*E[T_50]) = P(T_50 > %d) = %.6f (exact "
           "rational in results.json)" % (T_STAR, float(P_OVER)))
out.append("")
out.append("decision arithmetic @ bands 2/5|1/5 (twin evaluators agree): "
           "class=%s over=%d under=%d phi50_ge_2/5=%s"
           % (ARITH[0], ARITH[1], ARITH[2], ARITH[3]))
out.append("")
out.append("ARM S main (seed 20261345, N = 200,000/cell — agreement gate "
           "1/100 relative AND 4*SE on E[T] and phi, every cell):")
for n in GRID:
    g = main_legs[n][1]
    out.append("  N=%-3d mean_T=%-12.5f devE=%.5f (4SE %.5f) "
               "phi_hat=%.6f devPhi=%.6f (4SE %.6f) draws=%d"
               % (n, g["mean_T_float"], g["dev_E_float"], g["four_se_T"],
                  g["phi_hat_float"], g["dev_phi_float"], g["four_se_phi"],
                  g["draws"]))
out.append("F5 control legs (main seed, N = 200,000 each — mean gate + CDF "
           "point gate t = 1..12, all pass):")
for n in (2, 3):
    f = f5_legs[n]
    out.append("  N=%d mean_T=%.6f (exact %s) devE=%.6f (4SE %.6f) draws=%d"
               % (n, f["mean_T_float"], f["E_exact"], f["dev_E_float"],
                  f["four_se_T"], f["draws"]))
out.append("F5 exact CDF == full enumeration at N in {2, 3}, t = 1..12: "
           "all 24 identities exact (table in results.json)")
out.append("")
out.append("STABILITY (seed 20261346, N = 20,000/cell): class=%s over=%d "
           "under=%d — reproduces Arm A's %s; worst rel phi dev %.6f at %s"
           % (STAB_CLS[0], STAB_CLS[1], STAB_CLS[2], ARITH[0],
              float(stab_worst), stab_worst_leg))
out.append("")
out.append("REPORTING-ONLY (seed 20261347 — never flip the decision):")
out.append("  last-20%% alternative m = ceil(N/5), exact + MC confirm "
           "(arith class %s):" % L20_CLS[0])
for n in GRID:
    l = l20_report[n]
    out.append("    N=%-3d m=%-2d phi20_exact=%.6f phi20_hat=%.6f "
               "rel_dev=%.6f" % (n, l["m"], l["phi_exact_float"],
                                 l["phi_hat_float"],
                                 l["rel_dev_phi_float"]))
out.append("  weighted rarity-tier collector (pinned tiers, MC only — "
           "arith class %s):" % WT_CLS[0])
for n in GRID:
    w = wt_report[n]
    out.append("    N=%-3d tiers=%-14s mean_T=%-11.4f phi_w_hat=%.6f "
               "uniform_phi=%.6f delta=%+.6f"
               % (n, "/".join(str(c) for c in w["tier_counts"]),
                  w["mean_T_float"], w["phi_hat_float"],
                  w["uniform_phi_float"], w["delta_vs_uniform_float"]))
out.append("  (fixture-disclosed degeneracy: the registered tier masses "
           "equal the tier item-fractions, so the weighted pmf is exactly "
           "uniform at N in {20, 100, 200}; only the N = 50 integer split "
           "35/12/3 departs from uniform)")
out.append("  axis flags: %s" % json.dumps(axis_flags, sort_keys=True))
out.append("")
out.append("DRAFTER REFERENCE (disclosed, re-derived from scratch, compared "
           "NEVER gated): expected class %s, class match=%s"
           % (DRAFTER["expected_class"], drafter_class_match))
for c in drafter_cmp:
    out.append("  N=%-3d drafter phi~%.3f (%s) | measured phi=%.6f | "
               "within 1e-3=%s"
               % (c["N"], c["drafter_phi_approx"], c["drafter_expr"],
                  c["measured_phi_float"], c["matches_within_1e-3"]))
out.append("  sharpening: last single coupon share 1/H_50 = %.6f "
           "(drafter ~0.22)" % float(SHARE_1[50]))
out.append("")
out.append("SENTINELS: seed 20261345 calls=%d; seed 20261346 calls=%d; "
           "seed 20261347 calls=%d; seed 20261348 (aux) calls=%d (reserved, "
           "never read by any decision number)"
           % (RNG_MAIN.calls, RNG_STAB.calls, RNG_REP.calls, RNG_AUX.calls))
out.append("")
out.append("RULING (registered evaluation order REJECT -> INVALID -> "
           "APPROVE -> NULL): %s" % FINAL.upper())
out.append("  %s" % final_note)

RESULTS = {
    "verdict": "VERDICT 063",
    "registration": FX["registration"],
    "environment": {"cpython": list(sys.version_info[:2])},
    "arm_A": {
        "grid": [{"N": n, "m": m,
                  "H_N": fr(H[n]), "H_m": fr(H[m]),
                  "E_T": fr(E_T[n]), "E_T_float": float(E_T[n]),
                  "E_tail": fr(E_TAIL[n]), "E_tail_float": float(E_TAIL[n]),
                  "phi": fr(PHI[n]), "phi_float": float(PHI[n]),
                  "last_single_share": fr(SHARE_1[n]),
                  "last_single_share_float": float(SHARE_1[n]),
                  "band_position": band_pos(PHI[n])}
                 for n, m in zip(GRID, TAIL_M)],
        "arith_class": ARITH[0], "over": ARITH[1], "under": ARITH[2],
        "phi50_ge_reject_band": ARITH[3],
        "overshoot": {"t_star": T_STAR, "P": fr(P_OVER),
                      "P_float": float(P_OVER),
                      "two_E_T50": fr(2 * E_T50)},
        "last20_exact": [{"N": n, "m": m, "phi": fr(PHI_L20[n]),
                          "phi_float": float(PHI_L20[n])}
                         for n, m in zip(GRID, L20_M)],
        "F5_cdf_table": F5_TABLE,
    },
    "arm_S_main": {"seed": SEED_MAIN, "N_runs": N_MAIN,
                   "legs": {str(n): main_legs[n][1] for n in GRID},
                   "f5_control_legs": {str(n): f5_legs[n] for n in (2, 3)}},
    "stability": {"seed": SEED_STAB, "N_runs": N_STAB,
                  "class": STAB_CLS[0], "over": STAB_CLS[1],
                  "under": STAB_CLS[2],
                  "reproduces_ruling": STAB_CLS[0] == ARITH[0],
                  "worst_rel_dev_phi": float(stab_worst),
                  "worst_leg": stab_worst_leg,
                  "legs": {str(n): stab_report[n] for n in GRID}},
    "reporting_only": {
        "seed": SEED_REP, "N_runs": N_REP,
        "last20": {"arith_class": L20_CLS[0],
                   "legs": {str(n): l20_report[n] for n in GRID}},
        "weighted_tier": {"arith_class": WT_CLS[0],
                          "legs": {str(n): wt_report[n] for n in GRID}},
    },
    "axis_flags": axis_flags,
    "drafter_comparison_never_gated": {
        "expected_class": DRAFTER["expected_class"],
        "class_match": drafter_class_match,
        "cells": drafter_cmp,
    },
    "sentinels": {
        "seed_20261345_calls": RNG_MAIN.calls,
        "seed_20261346_calls": RNG_STAB.calls,
        "seed_20261347_calls": RNG_REP.calls,
        "seed_20261348_calls": RNG_AUX.calls,
    },
    "ruling": {"final": FINAL, "note": final_note,
               "evaluation_order": ["REJECT (checked FIRST)",
                                    "INVALID (controls — hard self-checks)",
                                    "APPROVE (with stability conjunct)",
                                    "NULL (pre-registered axes)"]},
}

res_json = json.dumps(RESULTS, indent=2, sort_keys=True) + "\n"
with open(os.path.join(BASE, "results.json"), "w", encoding="utf-8") as fh:
    fh.write(res_json)
check(len(res_json) > 1000, "results.json written")

out.append("SELF-CHECKS: %d passed, %d failed"
           % (_CHECKS["passed"], _CHECKS["failed"]))
body = "\n".join(out) + "\n"
sys.stdout.write(body)
