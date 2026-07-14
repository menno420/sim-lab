#!/usr/bin/env python3
"""VERDICT 067 — the inspection paradox at equal means (idea-engine PROPOSAL 056).

Dual-arm, hermetic, stdlib-only, deterministic.

Arm A (DECISION, seedless): exact fractions.Fraction moment arithmetic per
committed equal-mean cell; geometric moments via closed forms cross-checked
against exact rational partial sums to K = 500 plus exact tail formulas
(memoryless shift identity). Alone decision-bearing.

Arm S (confirmation, seeded): per stochastic cell a K = 100,000-interval
renewal trajectory via random.Random(20261361), pinned draw order
JITTER -> SPREAD -> MEMORYLESS -> BUNCHED, all intervals before any landing
(per cell), geometric as count-of-Bernoulli(q)-trials (no float log),
N = 200,000 uniform landings with bisect waits and containing-gap lengths.
Agreement gate |est - exact|/exact <= 1/100 AND |est - exact| <= 4*SE, on
E[W] and on P(W > 10), per cell.

Stability leg seed 20261362 (K = 20,000, N = 50,000; twin evaluators).
Reporting leg seed 20261363 (median/P90 rows; never decision-bearing).
Aux seed 20261364 reserved, NEVER read.

Decision rules executed in the REGISTERED order: REJECT -> INVALID ->
APPROVE -> NULL. Reads ONLY its own fixtures.json. No wall-clock in output.
"""

import bisect
import json
import math
import os
import random
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- self-checks
PASSED = 0
FAILURES = []


def check(cond, label):
    global PASSED
    if cond:
        PASSED += 1
    else:
        FAILURES.append(label)
    return bool(cond)


# ------------------------------------------------------------------- fixtures
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

REG = FX["registration"]
CHOICES = FX["fixture_level_choices_disclosed"]

check(sys.version_info[:2] == (3, 11),
      "cpython-3.11 pin (got %d.%d)" % sys.version_info[:2])

MU = Fr(REG["mu_pin"])
GRID_W = [int(w) for w in REG["exceedance_grid_w"]]
CELLS_ALL = ["CLOCKWORK", "JITTER", "SPREAD", "MEMORYLESS", "BUNCHED"]
CELLS_STOCH = list(REG["stochastic_cells"])
Q_GEO = Fr(REG["cells"]["MEMORYLESS"]["q"])
R_GEO = 1 - Q_GEO
KSUM = int(REG["geometric_crosscheck"]["partial_sum_K"])

BANDS = REG["bands"]
B_BUNCH = Fr(BANDS["reject_bunched_rho_min"])          # 2
B_CELL = Fr(BANDS["reject_cell_rho_min"])              # 11/10
B_NEED = int(BANDS["reject_cells_needed_of_4"])        # 3
B_APPR = Fr(BANDS["approve_rho_max"])                  # 21/20
G_REL = Fr(BANDS["agreement_gate_rel"])                # 1/100
G_SEM = int(BANDS["agreement_gate_se_mult"])           # 4

SEED_HEAD = int(REG["arm_s"]["seed_headline"])         # 20261361
SEED_STAB = int(REG["stability_leg"]["seed"])          # 20261362
SEED_REPT = int(REG["reporting_leg"]["seed"])          # 20261363
SEED_AUX = int(REG["aux_seed"]["value"])               # 20261364
K_HEAD, N_HEAD = int(REG["arm_s"]["K_intervals"]), int(REG["arm_s"]["N_landings"])
K_STAB, N_STAB = int(REG["stability_leg"]["K_intervals"]), int(REG["stability_leg"]["N_landings"])
K_REPT, N_REPT = 20000, 50000  # disclosed fixture choice (reporting leg size)

RNG_REGISTRY = []  # every seed ever handed to random.Random, in order


# ------------------------------------------------------------- Arm A (exact)
def pmf_finite(cell):
    """Return list of (value:int, weight:Fraction) for a finite cell."""
    spec = REG["cells"][cell]
    if spec["type"] == "pmf":
        return list(zip([int(v) for v in spec["support"]],
                        [Fr(w) for w in spec["weights"]]))
    if spec["type"] == "uniform_int":
        lo, hi = int(spec["lo"]), int(spec["hi"])
        n = hi - lo + 1
        return [(k, Fr(1, n)) for k in range(lo, hi + 1)]
    raise ValueError(cell)


def geo_closed_moment(m):
    """Closed-form E[X^m] for X ~ Geom(q) on {1,2,...}."""
    q = Q_GEO
    if m == 1:
        return 1 / q
    if m == 2:
        return (2 - q) / q ** 2
    if m == 3:
        return (6 - 6 * q + q ** 2) / q ** 3
    raise ValueError(m)


def geo_tail_moment(m, K):
    """Exact tail sum_{k>K} k^m p(k) via the shift identity r^K * E[(K+Y)^m]."""
    rK = R_GEO ** K
    e1, e2, e3 = geo_closed_moment(1), geo_closed_moment(2), geo_closed_moment(3)
    if m == 1:
        return rK * (K + e1)
    if m == 2:
        return rK * (K * K + 2 * K * e1 + e2)
    if m == 3:
        return rK * (K ** 3 + 3 * K * K * e1 + 3 * K * e2 + e3)
    raise ValueError(m)


def geo_partial_plus_tail(m):
    """Exact rational partial sum to KSUM plus exact tail formula."""
    p = Q_GEO  # P(X=k) = r^(k-1) q
    total = Fr(0)
    rk = Fr(1)  # r^(k-1)
    for k in range(1, KSUM + 1):
        total += (k ** m) * rk * p
        rk *= R_GEO
    return total + geo_tail_moment(m, KSUM)


def geo_epos_closed(w):
    """E[(X-w)^+] = r^w / q for integer w >= 0 (memorylessness)."""
    return (R_GEO ** w) / Q_GEO


def geo_epos_partial_plus_tail(w):
    """E[(X-w)^+] via partial sum to KSUM plus exact shift-identity tail."""
    p = Q_GEO
    total = Fr(0)
    rk = R_GEO ** w  # r^(k-1) at k = w+1
    for k in range(w + 1, KSUM + 1):
        total += (k - w) * rk * p
        rk *= R_GEO
    tail = (R_GEO ** KSUM) * (KSUM - w + geo_closed_moment(1))
    return total + tail


def arm_a_cell(cell):
    """Exact per-cell quantities. Returns dict of Fractions."""
    if REG["cells"][cell]["type"] == "geometric":
        ex = geo_closed_moment(1)
        ex2 = geo_closed_moment(2)
        ex3 = geo_closed_moment(3)
        # registered cross-check: closed forms vs partial sums + exact tails
        check(ex == geo_partial_plus_tail(1), "F1 geo E[X] closed==partial+tail")
        check(ex2 == geo_partial_plus_tail(2), "F1 geo E[X^2] closed==partial+tail")
        check(ex3 == geo_partial_plus_tail(3), "geo E[X^3] closed==partial+tail")
        epos = {w: geo_epos_closed(w) for w in GRID_W}
        for w in GRID_W:
            check(epos[w] == geo_epos_partial_plus_tail(w),
                  "geo E[(X-%d)+] closed==partial+tail" % w)
        # second, independent route to E[L]: sum k * (k p(k) / E[X]) partial+tail
        el_size_biased = geo_partial_plus_tail(2) / geo_partial_plus_tail(1)
    else:
        pmf = pmf_finite(cell)
        mass = sum(wt for _, wt in pmf)
        check(mass == 1, "F1 %s pmf mass == 1" % cell)
        ex = sum(k * wt for k, wt in pmf)
        ex2 = sum(k * k * wt for k, wt in pmf)
        ex3 = sum(k ** 3 * wt for k, wt in pmf)
        epos = {w: sum((k - w) * wt for k, wt in pmf if k > w) for w in GRID_W}
        # second, independent route to E[L]: expectation under the size-biased pmf
        el_size_biased = sum(k * (k * wt / ex) for k, wt in pmf)
    var = ex2 - ex * ex
    ew = ex2 / (2 * ex)
    el = ex2 / ex
    rho = ex2 / (ex * ex)
    ew2 = ex3 / (3 * ex)          # E[W^2] = E[L^2]/3, uniform position in gap
    varw = ew2 - ew * ew
    pw = {w: epos[w] / ex for w in GRID_W}
    return {"E_X": ex, "E_X2": ex2, "E_X3": ex3, "Var": var, "E_W": ew,
            "E_L": el, "E_L_size_biased": el_size_biased, "rho": rho,
            "Var_W": varw, "P_W_gt": pw}


A = {cell: arm_a_cell(cell) for cell in CELLS_ALL}

# --- F1: pmf re-derivation — mass, mean, variances exact
for cell in CELLS_ALL:
    check(A[cell]["E_X"] == MU, "F1 %s mean == 10" % cell)
    check(A[cell]["Var"] == Fr(REG["cells"][cell]["registered_var"]),
          "F1 %s variance registered" % cell)
check(sorted(a["Var"] for a in A.values()) == [0, 4, 10, 90, 256],
      "F1 variance set {0,4,10,90,256}")

# --- F2: size-bias identities — E[L] two independent ways, E[W] = E[L]/2
for cell in CELLS_ALL:
    check(A[cell]["E_L"] == A[cell]["E_L_size_biased"],
          "F2 %s E[L] two ways" % cell)
    check(A[cell]["E_W"] == A[cell]["E_L"] / 2, "F2 %s E[W] == E[L]/2" % cell)

# --- F3: CLOCKWORK degenerate
check(A["CLOCKWORK"]["rho"] == 1, "F3 CLOCKWORK rho == 1")
check(A["CLOCKWORK"]["P_W_gt"][10] == 0, "F3 CLOCKWORK P(W>10) == 0")
check(A["CLOCKWORK"]["E_W"] == 5, "F3 CLOCKWORK E[W] == 5")

# --- F4: monotonicity
for cell in CELLS_ALL:
    check(A[cell]["rho"] == 1 + A[cell]["Var"] / 100,
          "F4 %s rho == 1 + Var/100" % cell)
by_var = sorted(CELLS_ALL, key=lambda c: A[c]["Var"])
check([A[c]["Var"] for c in by_var] == sorted(A[c]["Var"] for c in CELLS_ALL)
      and [A[c]["rho"] for c in by_var] == sorted(A[c]["rho"] for c in CELLS_ALL),
      "F4 mean-preserving-spread ordering on rho (rank by Var == rank by rho)")
for cell in CELLS_ALL:
    seq = [A[cell]["P_W_gt"][w] for w in GRID_W]
    check(all(seq[i] >= seq[i + 1] for i in range(len(seq) - 1)),
          "F4 %s P(W>w) non-increasing in w" % cell)

# --- F5: hand identities
F5 = REG["F5_hand_identities"]
check(A["JITTER"]["P_W_gt"][8] == Fr(F5["JITTER_P_W_gt_8"]), "F5 JITTER P(W>8) == 1/5")
check(A["JITTER"]["E_W"] == Fr(F5["JITTER_E_W"]), "F5 JITTER E[W] == 26/5")
rider_share_42 = (42 * Fr(REG["cells"]["BUNCHED"]["weights"][1])) / A["BUNCHED"]["E_X"]
check(rider_share_42 == Fr(F5["BUNCHED_rider_share_in_42_gap"]),
      "F5 BUNCHED rider share in 42-gap == 21/25")
check(Fr(REG["cells"]["BUNCHED"]["weights"][1]) == Fr(F5["BUNCHED_interval_share_42"]),
      "F5 BUNCHED interval share of 42-gaps == 1/5")
check(A["BUNCHED"]["P_W_gt"][10] == Fr(F5["BUNCHED_P_W_gt_10"]), "F5 BUNCHED P(W>10) == 16/25")
check(A["MEMORYLESS"]["P_W_gt"][10] == Fr(9, 10) ** 10, "F5 MEMORYLESS P(W>10) == (9/10)^10")

F_GATES_ALL_PASS = not FAILURES  # F1-F5 booleans feed the INVALID rule


# ------------------------------------------------ exact quantiles (reporting)
def exact_quantile(cell, tail_target):
    """Solve G(w) = tail_target on the piecewise-linear exact exceedance
    G(w) = E[(X-w)^+]/E[X] (linear between integer breakpoints). Fraction."""
    spec = REG["cells"][cell]
    if spec["type"] == "geometric":
        def gval(j):  # G at integer j is r^j exactly
            return R_GEO ** j
        j = 0
        while gval(j + 1) > tail_target:
            j += 1
    else:
        pmf = pmf_finite(cell)
        ex = A[cell]["E_X"]

        def gval(j):
            return sum((k - j) * wt for k, wt in pmf if k > j) / ex
        j = 0
        while gval(j + 1) > tail_target:
            j += 1
    g0, g1 = gval(j), gval(j + 1)
    return j + (g0 - tail_target) / (g0 - g1)


EXACT_MEDIAN = {c: exact_quantile(c, Fr(1, 2)) for c in CELLS_ALL}
EXACT_P90 = {c: exact_quantile(c, Fr(1, 10)) for c in CELLS_ALL}
check(EXACT_MEDIAN["CLOCKWORK"] == 5 and EXACT_P90["CLOCKWORK"] == 9,
      "exact quantiles CLOCKWORK median 5 / P90 9")
check(EXACT_MEDIAN["BUNCHED"] == 17 and EXACT_P90["BUNCHED"] == 37,
      "exact quantiles BUNCHED median 17 / P90 37")


# ------------------------------------------------------------- Arm S (seeded)
class CountingRandom:
    """random.Random wrapper counting random() draws; registry-audited."""

    def __init__(self, seed):
        RNG_REGISTRY.append(seed)
        self._r = random.Random(seed)
        self.draws = 0

    def u(self):
        self.draws += 1
        return self._r.random()


def draw_interval(cell, rng):
    u = rng.u()
    if cell == "JITTER":
        return 8 if u < 0.5 else 12
    if cell == "SPREAD":
        return 5 + int(u * 11)
    if cell == "BUNCHED":
        return 2 if u < 0.8 else 42
    if cell == "MEMORYLESS":
        # count-of-Bernoulli(q)-trials, no float log
        k = 1
        while not (u < 0.1):
            u = rng.u()
            k += 1
        return k
    raise ValueError(cell)


def run_leg(seed, K, N, want_quantiles=False):
    """One MC leg: pinned cell order, all intervals before any landing (per
    cell), N uniform landings via bisect. Returns per-cell dict."""
    rng = CountingRandom(seed)
    out = {}
    for cell in CELLS_STOCH:
        d0 = rng.draws
        intervals = [draw_interval(cell, rng) for _ in range(K)]
        interval_draws = rng.draws - d0
        cum = []
        t = 0
        for x in intervals:
            t += x
            cum.append(t)
        T = t
        expect_draws = T if cell == "MEMORYLESS" else K
        check(interval_draws == expect_draws,
              "sentinel %s seed %d interval draws == %s" %
              (cell, seed, "T" if cell == "MEMORYLESS" else "K"))
        d1 = rng.draws
        sw = 0.0
        sl = 0.0
        exceed = {w: 0 for w in GRID_W}
        waits = [] if want_quantiles else None
        for _ in range(N):
            t_land = rng.u() * T
            idx = bisect.bisect_right(cum, t_land)
            w_wait = cum[idx] - t_land
            sw += w_wait
            sl += intervals[idx]
            for w in GRID_W:
                if w_wait > w:
                    exceed[w] += 1
            if waits is not None:
                waits.append(w_wait)
        check(rng.draws - d1 == N, "sentinel %s seed %d landing draws == N" % (cell, seed))
        rec = {
            "T": T,
            "interval_draws": interval_draws,
            "mean_W": sw / N,
            "mean_L": sl / N,
            "P_W_gt": {w: exceed[w] / N for w in GRID_W},
            "exceed_counts": {w: exceed[w] for w in GRID_W},
        }
        if waits is not None:
            waits.sort()
            rec["median_W"] = waits[math.ceil(N / 2) - 1]
            rec["P90_W"] = waits[math.ceil(9 * N / 10) - 1]
        out[cell] = rec
    return out


def gate_cell(cell, est, N):
    """Registered agreement gate on one cell: rel <= 1/100 AND abs <= 4*SE,
    on E[W] AND on P(W > 10). Returns (pass, detail)."""
    exact_ew = A[cell]["E_W"]
    exact_p = A[cell]["P_W_gt"][10]
    se_ew = math.sqrt(A[cell]["Var_W"] / N)
    se_p = math.sqrt(exact_p * (1 - exact_p) / N)
    dev_ew = abs(est["mean_W"] - float(exact_ew))
    dev_p = abs(est["P_W_gt"][10] - float(exact_p))
    rel_ew = dev_ew / float(exact_ew)
    rel_p = dev_p / float(exact_p)
    ok_ew_rel = rel_ew <= float(G_REL)
    ok_ew_se = dev_ew <= G_SEM * se_ew
    ok_p_rel = rel_p <= float(G_REL)
    ok_p_se = dev_p <= G_SEM * se_p
    ok = ok_ew_rel and ok_ew_se and ok_p_rel and ok_p_se
    return ok, {
        "E_W_exact": str(exact_ew), "E_W_est": est["mean_W"],
        "E_W_dev": dev_ew, "E_W_rel": rel_ew, "E_W_SE": se_ew,
        "E_W_dev_over_SE": dev_ew / se_ew if se_ew else 0.0,
        "E_W_rel_ok": ok_ew_rel, "E_W_4SE_ok": ok_ew_se,
        "P_W_gt_10_exact": str(exact_p), "P_W_gt_10_est": est["P_W_gt"][10],
        "P_dev": dev_p, "P_rel": rel_p, "P_SE": se_p,
        "P_dev_over_SE": dev_p / se_p if se_p else 0.0,
        "P_rel_ok": ok_p_rel, "P_4SE_ok": ok_p_se,
        "pass": ok,
    }


HEAD = run_leg(SEED_HEAD, K_HEAD, N_HEAD)
GATE_HEAD = {c: gate_cell(c, HEAD[c], N_HEAD) for c in CELLS_STOCH}

STAB = run_leg(SEED_STAB, K_STAB, N_STAB)
GATE_STAB = {c: gate_cell(c, STAB[c], N_STAB) for c in CELLS_STOCH}

REPT = run_leg(SEED_REPT, K_REPT, N_REPT, want_quantiles=True)

# aux seed 20261364: NEVER read by any decision number
check(SEED_AUX not in RNG_REGISTRY, "aux seed 20261364 never read")
check(RNG_REGISTRY == [SEED_HEAD, SEED_STAB, SEED_REPT],
      "RNG registry == [20261361, 20261362, 20261363] in pinned order")


# ----------------------------------------------------------- twin evaluators
def evaluator_te1(rho, f_ok, gate_ok, stability_reproduces):
    """TE1: fractions.Fraction comparisons, registered order."""
    n_ge = sum(1 for c in CELLS_STOCH if rho[c] >= B_CELL)
    gate_all = all(gate_ok[c] for c in CELLS_STOCH)
    if rho["BUNCHED"] >= B_BUNCH and n_ge >= B_NEED and gate_all:
        return "REJECT"
    if (not f_ok) or (not gate_all):
        return "INVALID"
    if all(rho[c] <= B_APPR for c in CELLS_STOCH) and stability_reproduces:
        return "APPROVE"
    return "NULL"


def evaluator_te2(rho, f_ok, gate_ok, stability_reproduces):
    """TE2: independently written; pure integer cross-multiplication over
    (numerator, denominator) pairs. Registered order."""
    pairs = {c: (rho[c].numerator, rho[c].denominator) for c in CELLS_STOCH}
    bn, bd = pairs["BUNCHED"]
    # rho(BUNCHED) >= 2  <=>  bn >= 2*bd   (denominators positive)
    cond_bunched = bn * B_BUNCH.denominator >= B_BUNCH.numerator * bd
    # rho >= 11/10  <=>  10*n >= 11*d
    hits = 0
    for c in CELLS_STOCH:
        n, d = pairs[c]
        if n * B_CELL.denominator >= B_CELL.numerator * d:
            hits += 1
    gates = True
    for c in CELLS_STOCH:
        gates = gates and bool(gate_ok[c])
    if cond_bunched and hits >= B_NEED and gates:
        return "REJECT"
    if (not f_ok) or (not gates):
        return "INVALID"
    approve_all = True
    for c in CELLS_STOCH:
        n, d = pairs[c]
        # rho <= 21/20  <=>  20*n <= 21*d
        if n * B_APPR.denominator > B_APPR.numerator * d:
            approve_all = False
    if approve_all and stability_reproduces:
        return "APPROVE"
    return "NULL"


RHO = {c: A[c]["rho"] for c in CELLS_STOCH}
GOK_HEAD = {c: GATE_HEAD[c][0] for c in CELLS_STOCH}
GOK_STAB = {c: GATE_STAB[c][0] for c in CELLS_STOCH}

# stability leg: full registered rule order with the stability estimates in
# the Arm-S slot (its APPROVE stability-conjunct is vacuous here by
# construction; REJECT/INVALID never consult it)
stab_te1 = evaluator_te1(RHO, F_GATES_ALL_PASS, GOK_STAB, True)
stab_te2 = evaluator_te2(RHO, F_GATES_ALL_PASS, GOK_STAB, True)
check(stab_te1 == stab_te2, "twin evaluators agree on stability class")

# headline ruling: registered order, stability_reproduces known only after
# the headline class exists -> evaluate headline with each candidate; the
# APPROVE conjunct is the only consumer. Two-pass fixpoint, deterministic.
head_te1_pass1 = evaluator_te1(RHO, F_GATES_ALL_PASS, GOK_HEAD, False)
STAB_REPRODUCES = (stab_te1 == head_te1_pass1)
head_te1 = evaluator_te1(RHO, F_GATES_ALL_PASS, GOK_HEAD, STAB_REPRODUCES)
head_te2 = evaluator_te2(RHO, F_GATES_ALL_PASS, GOK_HEAD, STAB_REPRODUCES)
check(head_te1 == head_te2, "twin evaluators agree on headline class")
STAB_REPRODUCES = (stab_te1 == head_te1)

RULING = head_te1
if RULING == "REJECT":
    RULE_FIRED = ("REJECT — checked FIRST: rho(BUNCHED) = %s >= 2 AND rho >= 11/10 in "
                  "%d of 4 stochastic cells (need >= 3) AND the Arm-S agreement gate "
                  "passed on every stochastic cell"
                  % (RHO["BUNCHED"], sum(1 for c in CELLS_STOCH if RHO[c] >= B_CELL)))
elif RULING == "INVALID":
    RULE_FIRED = "INVALID — controls misbehaving (F-gate or Arm-S agreement gate failure); report, no ruling"
elif RULING == "APPROVE":
    RULE_FIRED = "APPROVE — rho <= 21/20 at every stochastic cell AND stability reproduces"
else:
    RULE_FIRED = "NULL — none of REJECT/INVALID/APPROVE fired"

# ------------------------------------------------------------------ anomalies
ANOMALIES = []
if FAILURES:
    ANOMALIES.append("SELF-CHECK FAILURES: " + "; ".join(FAILURES))
for c in CELLS_STOCH:
    if not GOK_HEAD[c]:
        ANOMALIES.append("headline Arm-S agreement gate FAILED on %s: %s" % (c, GATE_HEAD[c][1]))
    if not GOK_STAB[c]:
        ANOMALIES.append("stability-leg agreement gate FAILED on %s (stability class %s)" % (c, stab_te1))
if not STAB_REPRODUCES:
    ANOMALIES.append("stability leg does NOT reproduce the headline ruling (%s vs %s)" % (stab_te1, head_te1))

# drafter-reference comparison — never gated
DRAFT = REG["drafter_reference_never_gated"]
DRAFT_CMP = {}
for c in CELLS_ALL:
    DRAFT_CMP[c] = (A[c]["rho"] == Fr(DRAFT["rho"][c]))
DRAFT_CMP["BUNCHED_E_W"] = (A["BUNCHED"]["E_W"] == Fr(DRAFT["BUNCHED_E_W"]))
if not all(DRAFT_CMP.values()):
    ANOMALIES.append("drafter-disclosed reference values NOT all reproduced: %s"
                     % {k: v for k, v in DRAFT_CMP.items() if not v})

# --------------------------------------------------------------------- output
def frs(x):
    return "%s" % x  # Fraction -> 'n/d' or integer string


RESULTS = {
    "verdict": RULING,
    "rule_fired": RULE_FIRED,
    "decision_order_executed": REG["decision_rules_order"],
    "arm_a_exact": {
        c: {
            "E_X": frs(A[c]["E_X"]), "E_X2": frs(A[c]["E_X2"]), "E_X3": frs(A[c]["E_X3"]),
            "Var": frs(A[c]["Var"]), "E_W": frs(A[c]["E_W"]), "E_L": frs(A[c]["E_L"]),
            "rho": frs(A[c]["rho"]), "rho_float": float(A[c]["rho"]),
            "Var_W": frs(A[c]["Var_W"]),
            "P_W_gt": {str(w): frs(A[c]["P_W_gt"][w]) for w in GRID_W},
            "exact_median_W": frs(EXACT_MEDIAN[c]), "exact_P90_W": frs(EXACT_P90[c]),
        } for c in CELLS_ALL
    },
    "folk_rule_vs_exact": {
        "folk_E_W": "5",
        "BUNCHED_E_W": frs(A["BUNCHED"]["E_W"]),
        "BUNCHED_rho": frs(A["BUNCHED"]["rho"]),
        "rider_vs_operator_BUNCHED": {
            "interval_share_42_gaps": frs(Fr(REG["cells"]["BUNCHED"]["weights"][1])),
            "rider_share_in_42_gap": frs(rider_share_42),
        },
    },
    "arm_s_headline_seed_20261361": {
        c: {
            "T": HEAD[c]["T"], "interval_draws": HEAD[c]["interval_draws"],
            "mean_W": repr(HEAD[c]["mean_W"]), "mean_L": repr(HEAD[c]["mean_L"]),
            "P_W_gt": {str(w): repr(HEAD[c]["P_W_gt"][w]) for w in GRID_W},
            "gate": {k: (repr(v) if isinstance(v, float) else v)
                     for k, v in GATE_HEAD[c][1].items()},
        } for c in CELLS_STOCH
    },
    "stability_seed_20261362": {
        "class_te1": stab_te1, "class_te2": stab_te2,
        "reproduces_headline": STAB_REPRODUCES,
        "cells": {
            c: {
                "mean_W": repr(STAB[c]["mean_W"]),
                "P_W_gt_10": repr(STAB[c]["P_W_gt"][10]),
                "gate": {k: (repr(v) if isinstance(v, float) else v)
                         for k, v in GATE_STAB[c][1].items()},
            } for c in CELLS_STOCH
        },
    },
    "reporting_seed_20261363": {
        c: {"median_W": repr(REPT[c]["median_W"]), "P90_W": repr(REPT[c]["P90_W"]),
            "exact_median_W": frs(EXACT_MEDIAN[c]), "exact_P90_W": frs(EXACT_P90[c])}
        for c in CELLS_STOCH
    },
    "rng_registry": RNG_REGISTRY,
    "aux_seed_20261364_read": SEED_AUX in RNG_REGISTRY,
    "f_gates_all_pass": F_GATES_ALL_PASS,
    "twin_evaluators": {"headline_te1": head_te1, "headline_te2": head_te2,
                        "stability_te1": stab_te1, "stability_te2": stab_te2},
    "drafter_reference_comparison_never_gated": {k: bool(v) for k, v in DRAFT_CMP.items()},
    "anomalies": ANOMALIES if ANOMALIES else ["none"],
    "boundaries_registered": REG["boundaries_registered"],
    "cpython": "%d.%d" % sys.version_info[:2],
}

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(RESULTS, fh, indent=1, sort_keys=True)
    fh.write("\n")

print("VERDICT 067 — inspection paradox at equal means (PROPOSAL 056)")
print("ruling: %s" % RULING)
print("rule fired: %s" % RULE_FIRED)
print()
print("Arm A (exact, DECISION): cell | Var | E[W] | E[L] | rho | P(W>10) | med | P90")
for c in CELLS_ALL:
    print("  %-10s | %4s | %6s | %6s | %6s = %s | %s | %s | %s" %
          (c, frs(A[c]["Var"]), frs(A[c]["E_W"]), frs(A[c]["E_L"]), frs(A[c]["rho"]),
           repr(float(A[c]["rho"])), frs(A[c]["P_W_gt"][10]),
           frs(EXACT_MEDIAN[c]), frs(EXACT_P90[c])))
print("exceedance table P(W>w), w in %s:" % GRID_W)
for c in CELLS_ALL:
    print("  %-10s | %s" % (c, " | ".join(frs(A[c]["P_W_gt"][w]) for w in GRID_W)))
print()
print("Arm S headline (seed %d, K=%d, N=%d):" % (SEED_HEAD, K_HEAD, N_HEAD))
for c in CELLS_STOCH:
    g = GATE_HEAD[c][1]
    print("  %-10s mean_W=%s (exact %s, rel %s, dev/SE %s) P(W>10)=%s (exact %s, rel %s, dev/SE %s) gate=%s" %
          (c, repr(HEAD[c]["mean_W"]), g["E_W_exact"], repr(g["E_W_rel"]),
           repr(g["E_W_dev_over_SE"]), repr(HEAD[c]["P_W_gt"][10]), g["P_W_gt_10_exact"],
           repr(g["P_rel"]), repr(g["P_dev_over_SE"]), "PASS" if GATE_HEAD[c][0] else "FAIL"))
print("stability (seed %d, K=%d, N=%d): class TE1=%s TE2=%s reproduces=%s" %
      (SEED_STAB, K_STAB, N_STAB, stab_te1, stab_te2, STAB_REPRODUCES))
for c in CELLS_STOCH:
    print("  %-10s mean_W=%s P(W>10)=%s gate=%s" %
          (c, repr(STAB[c]["mean_W"]), repr(STAB[c]["P_W_gt"][10]),
           "PASS" if GATE_STAB[c][0] else "FAIL"))
print("reporting (seed %d, K=%d, N=%d): median/P90 (MC vs exact):" %
      (SEED_REPT, K_REPT, N_REPT))
for c in CELLS_STOCH:
    print("  %-10s median %s (exact %s) P90 %s (exact %s)" %
          (c, repr(REPT[c]["median_W"]), frs(EXACT_MEDIAN[c]),
           repr(REPT[c]["P90_W"]), frs(EXACT_P90[c])))
print("rng registry: %s (aux 20261364 read: %s)" %
      (RNG_REGISTRY, SEED_AUX in RNG_REGISTRY))
print("anomalies: %s" % ("; ".join(ANOMALIES) if ANOMALIES else "none"))
print()
print("SELF-CHECKS: %d passed, %d failed" % (PASSED, len(FAILURES)))
for f in FAILURES:
    print("  FAILED: %s" % f)
sys.exit(1 if FAILURES else 0)
