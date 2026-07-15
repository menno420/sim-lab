#!/usr/bin/env python3
"""VERDICT 087 — the bundle over a floorless PWYW (idea-engine PROPOSAL 074).

Prices the committed Ship-It triple (kit a = $49 fixed, pack PWYW s = $19
suggested with floor f UNCOMMITTED, bundle p = $59 fixed, FAQ "saves $9 and
one checkout") at its one open degree of freedom: the PWYW floor. Three
exact structure theorems (T1 basis gap = s - f; T2 coherence window
p in [a, a+f] mapping V040's anchors {59, 64, 68} -> floors {10, 15, 19};
T3 affine fee invariant, seller +$9.51 / buyer -$10 / f-independent $0.80)
ride as gates. Pre-registered rule, registered order REJECT -> INVALID ->
APPROVE -> NULL. Hermetic: reads ONLY its own fixtures.json.

Arms:
  A  seedless exact-Fraction closed forms (DECISION-bearing)
  B  INDEPENDENTLY-WRITTEN twin: literal integer-cent enumeration (path
     costs by direct min() over enumerated w, w* by upward scan, window
     membership by scanning candidate bundle prices, gap by direct
     subtraction, fee layer in integer milli-dollars); powers the second
     decision evaluator
  R  seeded, REPORTING-ONLY buyer-type draws at the decision cell (no
     statistical gate)

CPython 3.11 pinned and asserted. Stdlib only. stdout + results.json are
byte-identical across process runs (canonical serialization, C9).
"""

import json
import os
import random
import sys
from fractions import Fraction

# ---------------------------------------------------------------- plumbing

CHECKS = {"passed": 0, "failed": 0}
FAILURES = []
ANOMALIES = []


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        FAILURES.append(name)
    return cond


def anomaly(text):
    ANOMALIES.append(text)


def fr(a, b=1):
    return Fraction(a, b)


def fstr(x):
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    return "%d/%d" % (x.numerator, x.denominator)


# seed constructor registry (C7)
SEED_REGISTRY = []


class RegisteredRandom(random.Random):
    def __init__(self, seed):
        SEED_REGISTRY.append(seed)
        super().__init__(seed)
        self.draws = 0

    def random(self):
        self.draws += 1
        return super().random()


# ================================================================ Arm A
# Seedless exact Fractions/ints. DECISION-bearing. Closed forms.

def A_sigma_adv(a, s, p):
    return fr(a) + fr(s) - fr(p)


def A_sigma_ach(a, f, p):
    return fr(a) + fr(f) - fr(p)


def A_pi(a, f, p):
    return max(fr(0), fr(p) - fr(a) - fr(f))


def A_coherent(a, f, p):
    return fr(a) <= fr(p) <= fr(a) + fr(f)


def A_fstar(a, p):
    return fr(p) - fr(a)


def A_wstar(a, p):
    return fr(p) - fr(a)


def A_net(P, alpha, beta):
    return alpha * fr(P) - beta


def A_delta(a, f, p, alpha, beta):
    # bundle-minus-strategic-separate seller net, direct via net()
    return A_net(p, alpha, beta) - (A_net(a, alpha, beta) + A_net(f, alpha, beta))


def A_min_f_for_saving(a, p, d):
    # smallest integer f >= 0 with sigma_ach >= d (closed form: p - a + d)
    f = 0
    while A_sigma_ach(a, f, p) < fr(d):
        f += 1
        if f > 1000:
            raise RuntimeError("A_min_f_for_saving runaway")
    return f


# ================================================================ Arm B
# INDEPENDENTLY WRITTEN twin (C2). Integer cents for paths, integer
# milli-dollars for the fee layer. No closed-form reuse: direct min() over
# enumerated w, upward scans, candidate-price window scans, direct
# subtraction.

W_SCAN_MAX_C = 3001   # enumerate intended payments w in [0, $30] cents
Q_SCAN_MAX_C = 12001  # candidate bundle prices q in [0, $120] cents

_CHEAPEST_CACHE = {}


def B_separate_cost_c(A_c, F_c, w_c):
    # two checkouts: kit + pack payment (floor binds)
    return A_c + (w_c if w_c > F_c else F_c)


def B_cheapest_separate_c(A_c, F_c):
    # literal enumeration: min over every intended payment w (memoized —
    # the enumeration itself is unchanged, each (A, F) pair runs once)
    key = (A_c, F_c)
    if key in _CHEAPEST_CACHE:
        return _CHEAPEST_CACHE[key]
    best = None
    for w_c in range(0, W_SCAN_MAX_C):
        c = B_separate_cost_c(A_c, F_c, w_c)
        if best is None or c < best:
            best = c
    _CHEAPEST_CACHE[key] = best
    return best


def B_sigma_adv_c(A_c, S_c, P_c):
    return (A_c + S_c) - P_c


def B_sigma_ach_c(A_c, F_c, P_c):
    return B_cheapest_separate_c(A_c, F_c) - P_c


def B_pi_c(A_c, F_c, P_c):
    extra = P_c - B_cheapest_separate_c(A_c, F_c)
    return extra if extra > 0 else 0


def B_wstar_scan_c(A_c, F_c, P_c):
    # upward scan: smallest intended payment w at which the bundle is
    # weakly cheaper than the separate path
    for w_c in range(0, W_SCAN_MAX_C):
        if P_c <= B_separate_cost_c(A_c, F_c, w_c):
            return w_c
    return None


def B_window_c(A_c, F_c):
    # scan candidate bundle prices q; coherent iff q neither undercuts the
    # kit alone nor charges the strategic both-buyer a premium
    cheapest_sep = B_cheapest_separate_c(A_c, F_c)
    coherent = []
    for q_c in range(0, Q_SCAN_MAX_C):
        undercuts_kit = q_c < A_c
        strategic_premium = q_c > cheapest_sep
        if not undercuts_kit and not strategic_premium:
            coherent.append(q_c)
    return coherent


def B_member_c(A_c, F_c, P_c):
    cheapest_sep = B_cheapest_separate_c(A_c, F_c)
    return (P_c >= A_c) and (P_c <= cheapest_sep)


def B_fstar_scan_c(A_c, P_c, quantum_c=1):
    # upward floor scan on the quantum lattice: smallest floor making the
    # committed price coherent
    F_c = 0
    while not B_member_c(A_c, F_c, P_c):
        F_c += quantum_c
        if F_c > 100000:
            return None
    return F_c


def B_min_f_for_saving_scan_c(A_c, P_c, d_c):
    # upward floor scan: smallest integer-dollar floor with sigma_ach >= d
    F_c = 0
    while B_sigma_ach_c(A_c, F_c, P_c) < d_c:
        F_c += 100
        if F_c > 100000:
            return None
    return F_c


def B_net_md(P_usd):
    # committed fee layer in integer milli-dollars (871/1000, 4/5 = 800 md)
    return 871 * P_usd - 800


def B_delta_md(a_usd, f_usd, p_usd):
    return B_net_md(p_usd) - (B_net_md(a_usd) + B_net_md(f_usd))


# ================================================================ Arm R
# REPORTING-ONLY buyer-type draws at the decision cell. One uniform per
# episode; cumulative-pmf mapping; ties to bundle. No statistical gate.

def R_trace(seed, episodes, pmf_order, pmf_cum, a_usd, p_usd, wstar_usd):
    rng = RegisteredRandom(seed)
    bundle_take = 0
    outlay_sum = 0
    for _ in range(episodes):
        u = rng.random()
        w = None
        for cum, val in zip(pmf_cum, pmf_order):
            if u < cum:
                w = val
                break
        if w is None:
            w = pmf_order[-1]
        # decision cell f = 0: separate path costs a + w; ties to bundle
        if w >= wstar_usd:
            bundle_take += 1
            outlay_sum += p_usd
        else:
            outlay_sum += a_usd + w
    return {"seed": seed, "episodes": episodes, "draws": rng.draws,
            "bundle_take": bundle_take, "outlay_sum": outlay_sum}


# ================================================================ run

def main():
    check("cpython 3.11 pinned", sys.version_info[:2] == (3, 11))

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "fixtures.json"), "r", encoding="utf-8") as fh:
        FX = json.load(fh)

    cc = FX["committed_constants"]
    a, s, p = cc["a_kit_usd"], cc["s_suggested_usd"], cc["p_bundle_usd"]
    anchors = cc["anchor_family_p"]
    f_grid = cc["floor_grid_f"]
    alpha = Fraction(cc["fee_affine"]["alpha"])
    beta = Fraction(cc["fee_affine"]["beta"])
    dcell = FX["decision_cell"]
    check("decision cell matches committed constants",
          (dcell["a"], dcell["s"], dcell["p"], dcell["f"]) == (a, s, p, 0))

    A_c, S_c = a * 100, s * 100

    # ---------------------------------------------------------- Arm A grid
    armA = {}
    for pp in anchors:
        for f in f_grid:
            armA[(pp, f)] = {
                "coherent": A_coherent(a, f, pp),
                "sigma_ach": A_sigma_ach(a, f, pp),
                "pi": A_pi(a, f, pp),
                "gap": A_sigma_adv(a, s, pp) - A_sigma_ach(a, f, pp),
                "delta": A_delta(a, f, pp, alpha, beta),
            }
    sigma_adv_A = A_sigma_adv(a, s, p)
    fstar_A = {pp: A_fstar(a, pp) for pp in anchors}
    wstar_A = A_wstar(a, p)

    # ---------------------------------------------------------- Arm B grid
    armB = {}
    for pp in anchors:
        P_c = pp * 100
        for f in f_grid:
            F_c = f * 100
            armB[(pp, f)] = {
                "coherent": B_member_c(A_c, F_c, P_c),
                "sigma_ach_c": B_sigma_ach_c(A_c, F_c, P_c),
                "pi_c": B_pi_c(A_c, F_c, P_c),
                "gap_c": B_sigma_adv_c(A_c, S_c, P_c) - B_sigma_ach_c(A_c, F_c, P_c),
                "delta_md": B_delta_md(a, f, pp),
            }
    sigma_adv_B_c = B_sigma_adv_c(A_c, S_c, p * 100)
    fstar_B_c = {pp: B_fstar_scan_c(A_c, pp * 100) for pp in anchors}
    wstar_B_c = B_wstar_scan_c(A_c, 0, p * 100)

    # ------------------------------------------------- F6 twin exact-equal
    for pp in anchors:
        for f in f_grid:
            ra, rb = armA[(pp, f)], armB[(pp, f)]
            check("twin coherent (%d,%d)" % (pp, f), ra["coherent"] == rb["coherent"])
            check("twin sigma_ach (%d,%d)" % (pp, f),
                  ra["sigma_ach"] * 100 == rb["sigma_ach_c"])
            check("twin pi (%d,%d)" % (pp, f), ra["pi"] * 100 == rb["pi_c"])
            check("twin gap (%d,%d)" % (pp, f), ra["gap"] * 100 == rb["gap_c"])
            check("twin delta (%d,%d)" % (pp, f), ra["delta"] * 1000 == rb["delta_md"])
    check("twin sigma_adv", sigma_adv_A * 100 == sigma_adv_B_c)
    for pp in anchors:
        check("twin fstar %d" % pp, fstar_A[pp] * 100 == fstar_B_c[pp])
    check("twin wstar", wstar_A * 100 == wstar_B_c)

    # ------------------------------------------------- F1 identities + anchors
    ea = {}
    for P in (49, 19, 59, 64, 68):
        ea["net_%d" % P] = A_net(P, alpha, beta)
    check("F1 sigma_adv = 9 (the committed copy number)", sigma_adv_A == 9)
    check("F1 net(49) = 41879/1000", ea["net_49"] == fr(41879, 1000))
    check("F1 net(59) = 50589/1000", ea["net_59"] == fr(50589, 1000))
    check("F1 net(64) = 54944/1000", ea["net_64"] == fr(54944, 1000))
    check("F1 net(68) = 58428/1000", ea["net_68"] == fr(58428, 1000))
    plus080 = ea["net_68"] - (ea["net_49"] + ea["net_19"])
    check("F1 +0.80 row = 4/5", plus080 == fr(4, 5))
    bar = ea["net_59"] / ea["net_64"]
    check("F1 retention bar = 50589/54944", bar == fr(50589, 54944))
    delta19 = A_delta(a, 19, p, alpha, beta)
    check("F1 nudge cost Delta(19) = -7039/1000", delta19 == fr(-7039, 1000))
    check("F1 w* = f* identity at p - a", wstar_A == fstar_A[p] == fr(p - a))
    # Arm-B side of the five anchors (milli-dollars)
    check("F1B net_md five anchors",
          [B_net_md(x) for x in (49, 59, 64, 68)] == [41879, 50589, 54944, 58428])
    check("F1B +0.80 row md", B_net_md(68) - (B_net_md(49) + B_net_md(19)) == 800)
    check("F1B Delta(19) md", B_delta_md(a, 19, p) == -7039)

    # ------------------------------------------------- F2 theorems
    # T1 basis gap = s - f exactly, committed grid AND perturbed controls
    t1c = FX["t1_independence_controls"]
    for pp in anchors:
        for f in f_grid:
            check("T1 gap = s-f (%d,%d)" % (pp, f), armA[(pp, f)]["gap"] == fr(s - f))
            check("T1B gap = s-f (%d,%d)" % (pp, f),
                  armB[(pp, f)]["gap_c"] == (s - f) * 100)
    for aa in t1c["perturbed_a"]:
        for pq in t1c["perturbed_p"]:
            for f in f_grid:
                gA = A_sigma_adv(aa, s, pq) - A_sigma_ach(aa, f, pq)
                check("T1 control gap A a=%d p=%d f=%d" % (aa, pq, f), gA == fr(s - f))
                gB = (B_sigma_adv_c(aa * 100, S_c, pq * 100)
                      - B_sigma_ach_c(aa * 100, f * 100, pq * 100))
                check("T1 control gap B a=%d p=%d f=%d" % (aa, pq, f),
                      gB == (s - f) * 100)
    # T2 coherence window
    check("T2 f* table {59:10, 64:15, 68:19}",
          {pp: fstar_A[pp] for pp in anchors} == {59: fr(10), 64: fr(15), 68: fr(19)})
    check("T2 f*(68) = s EXACTLY (registered margin-0 must-equal)",
          fstar_A[68] == fr(s))
    ratio_2019 = fstar_A[59] / (fr(s) / 2)
    check("T2 f*(59) > s/2 strictly", fstar_A[59] > fr(s) / 2)
    check("T2 ratio f*(59)/(s/2) = 20/19", ratio_2019 == fr(20, 19))
    win0 = B_window_c(A_c, 0)
    check("T2 window at f=0 is the single point {49} (cent scan)",
          win0 == [4900])
    for f in f_grid:
        wf = B_window_c(A_c, f * 100)
        check("T2 window [a, a+f] contiguous f=%d" % f,
              wf == list(range(A_c, A_c + f * 100 + 1)))
    law = FX["census_anchors_F3"]["strict_discount_law"]
    strict_vals_A = [A_min_f_for_saving(a, p, d) for d in law["checked_at_d"]]
    strict_vals_B = [B_min_f_for_saving_scan_c(A_c, p * 100, d * 100) // 100
                     for d in law["checked_at_d"]]
    check("T2 strict-discount law f(d) = 10+d at d in {1,9}",
          strict_vals_A == law["values"] == [11, 19])
    check("T2B strict-discount law (floor scan)", strict_vals_B == law["values"])
    check("T2 committed '$9' needs f = 19 = s", strict_vals_A[1] == s == 19)
    # T3 affine fee invariant, whole (alpha, beta) family
    t3 = FX["t3_affine_family_check"]
    for al_s in t3["alpha_grid"]:
        for be_s in t3["beta_grid"]:
            al, be = Fraction(al_s), Fraction(be_s)
            for pp in anchors:
                for f in f_grid:
                    lhs = A_delta(a, f, pp, al, be)
                    rhs = al * (fr(pp) - fr(a) - fr(f)) + be
                    check("T3 affine a=%s b=%s (%d,%d)" % (al_s, be_s, pp, f),
                          lhs == rhs)
    check("T3 decision-cell seller fork +951/100",
          A_delta(a, 0, p, alpha, beta) == fr(951, 100))
    check("T3 decision-cell buyer fork -10", A_sigma_ach(a, 0, p) == fr(-10))
    for f in f_grid:
        if f < 10:
            check("T3 simultaneous-strict f=%d (seller>0, buyer<0)" % f,
                  armA[(p, f)]["delta"] > 0 and armA[(p, f)]["sigma_ach"] < 0)
        check("T3 f-invariant beta residue f=%d" % f,
              armA[(p, f)]["delta"] - alpha * (fr(p) - fr(a) - fr(f)) == beta)

    # ------------------------------------------------- F3 census anchors
    tbl = FX["census_anchors_F3"]["f_grid_table_at_p59"]["rows"]
    for row in tbl:
        f, coh_s, sach, pi_v, gap_v, delta_s = row
        ra = armA[(59, f)]
        check("F3 row f=%d coherent" % f, ra["coherent"] == (coh_s == "yes"))
        check("F3 row f=%d sigma_ach" % f, ra["sigma_ach"] == fr(sach))
        check("F3 row f=%d pi" % f, ra["pi"] == fr(pi_v))
        check("F3 row f=%d gap" % f, ra["gap"] == fr(gap_v))
        check("F3 row f=%d Delta" % f, ra["delta"] == Fraction(delta_s))
    ftab = FX["census_anchors_F3"]["fstar_table"]
    check("F3 f* table verbatim",
          {int(k): fr(v) for k, v in ftab.items()} == fstar_A)
    check("F3 mirror cell pi(1) = 9 = sigma_adv",
          armA[(59, 1)]["pi"] == fr(9) == sigma_adv_A)
    check("F3 Delta(0) = 951/100", armA[(59, 0)]["delta"] == fr(951, 100))
    check("F3 sibling committed $3 floor leaves a $7 premium",
          armA[(59, 3)]["pi"] == fr(7) and not armA[(59, 3)]["coherent"])

    # ------------------------------------------------- F4 hand world
    hw = FX["hand_world_F4"]
    ha, hs, hp, hf = hw["a"], hw["s"], hw["p"], hw["f"]
    check("F4 w* = 1", A_wstar(ha, hp) == fr(hw["wstar"]))
    check("F4 f* = 1", A_fstar(ha, hp) == fr(hw["fstar"]))
    check("F4 gap = 2 = s",
          A_sigma_adv(ha, hs, hp) - A_sigma_ach(ha, hf, hp) == fr(hw["gap"]) == fr(hs))
    check("F4 pi = 1", A_pi(ha, hf, hp) == fr(hw["pi"]))
    hwin = B_window_c(ha * 100, hf * 100)
    check("F4 window = {3} (cent scan)", hwin == [300])
    hw_wstar_c = B_wstar_scan_c(ha * 100, hf * 100, hp * 100)
    check("F4 Arm-B cent-scan w* = 100 cents",
          hw_wstar_c == hw["armB_cent_scan_wstar_cents"] == 100)

    # ------------------------------------------------- F5 degeneracies + controls
    check("F5 f=s: gap 0, coherent, sigma_ach = sigma_adv = 9",
          armA[(59, 19)]["gap"] == 0 and armA[(59, 19)]["coherent"]
          and armA[(59, 19)]["sigma_ach"] == sigma_adv_A == fr(9))
    for f in f_grid:
        check("F5 p=a coherent at every f (f=%d)" % f, A_coherent(a, f, a))
        check("F5 p=a pi=0 (f=%d)" % f, A_pi(a, f, a) == 0)
    check("F5 p=a is the only coherent price at f=0 (window scan)",
          B_window_c(A_c, 0) == [A_c])
    check("F5 p=a+s=68 -> f* = s", A_fstar(a, 68) == fr(s))
    # C11 floor-granularity control: quanta 1 cent and 99 cents
    gran = {}
    for q_c in (1, 99):
        got = {}
        for pp in anchors:
            th = B_fstar_scan_c(A_c, pp * 100, quantum_c=q_c)
            exact_c = (pp - a) * 100
            got[pp] = th
            check("F5 granularity q=%dc p=%d shifts < one quantum" % (q_c, pp),
                  th is not None and 0 <= th - exact_c < q_c)
            check("F5 granularity q=%dc p=%d integer thresholds non-flipping"
                  % (q_c, pp),
                  (th + 99) // 100 >= (pp - a) and th < (pp - a + 1) * 100)
        gran["q%dc" % q_c] = {str(pp): got[pp] for pp in anchors}
    # C12 APPROVE/R1 mutual exclusivity on the full grid
    for pp in anchors:
        for f in f_grid:
            ra = armA[(pp, f)]
            r1_cell = (not ra["coherent"]) and ra["sigma_ach"] <= -(fr(pp) - fr(a))
            ap_cell = ra["coherent"] and ra["sigma_ach"] >= 0
            check("C12 exclusivity (%d,%d)" % (pp, f), not (r1_cell and ap_cell))

    # ------------------------------------------------- decision evaluators
    def evaluate_A():
        r1 = ((not armA[(p, 0)]["coherent"])
              and armA[(p, 0)]["sigma_ach"] <= -(fr(p) - fr(a))
              and sigma_adv_A == 9)
        r2 = ({pp: fstar_A[pp] for pp in anchors}
              == {59: fr(10), 64: fr(15), 68: fr(19)}
              and fstar_A[68] == fr(s)
              and fstar_A[59] > fr(s) / 2)
        r3 = (armA[(p, 10)]["sigma_ach"] == 0
              and strict_vals_A == [11, 19]
              and strict_vals_A[1] == s)
        approve = armA[(p, 0)]["coherent"] and armA[(p, 0)]["sigma_ach"] >= 0
        if r1 and r2 and r3:
            return "REJECT", (r1, r2, r3)
        if FAILURES:
            return "INVALID", (r1, r2, r3)
        if approve:
            return "APPROVE", (r1, r2, r3)
        return "NULL", (r1, r2, r3)

    def evaluate_B():
        P_c = p * 100
        b0 = armB[(p, 0)]
        r1 = ((not b0["coherent"])
              and b0["sigma_ach_c"] <= -(P_c - A_c)
              and sigma_adv_B_c == 900)
        r2 = (fstar_B_c == {59: 1000, 64: 1500, 68: 1900}
              and fstar_B_c[68] == S_c
              and 2 * fstar_B_c[59] > S_c)
        r3 = (armB[(p, 10)]["sigma_ach_c"] == 0
              and strict_vals_B == [11, 19]
              and strict_vals_B[1] * 100 == S_c)
        approve = b0["coherent"] and b0["sigma_ach_c"] >= 0
        if r1 and r2 and r3:
            return "REJECT", (r1, r2, r3)
        if FAILURES:
            return "INVALID", (r1, r2, r3)
        if approve:
            return "APPROVE", (r1, r2, r3)
        return "NULL", (r1, r2, r3)

    # APPROVE liveness witnesses (C4 — registered clause, no new code path)
    approve_live = [f for f in f_grid
                    if armA[(p, f)]["coherent"] and armA[(p, f)]["sigma_ach"] >= 0]
    check("APPROVE liveness: exactly the f >= 10 cells",
          approve_live == [10, 15, 19])

    # Robustness note (reporting-only, C5): R1 without the margin-0 cell
    r1_alone = ((not armA[(p, 0)]["coherent"])
                and armA[(p, 0)]["sigma_ach"] <= -(fr(p) - fr(a))
                and sigma_adv_A == 9)
    check("C5 robustness: R1 fires independent of the f*(68)=s contact", r1_alone)

    # ------------------------------------------------- margin ledger (C5, typed)
    ledger = []

    def must_equal(name, lhs, rhs):
        ok = lhs == rhs
        check("ledger must-equal: " + name, ok)
        ledger.append({"row": name, "type": "must-equal",
                       "lhs": fstr(lhs), "rhs": fstr(rhs), "ok": ok})

    def must_clear(name, value, note):
        ok = value > 0
        check("ledger must-clear: " + name, ok)
        ledger.append({"row": name, "type": "must-clear",
                       "margin": fstr(value), "note": note, "ok": ok})

    must_equal("sigma_adv = copy number 9", sigma_adv_A, fr(9))
    must_equal("sigma_ach(0) = -(p-a) = -10",
               armA[(p, 0)]["sigma_ach"], -(fr(p) - fr(a)))
    must_equal("f*(68) = s (registered margin-0 contact)", fstar_A[68], fr(s))
    must_equal("mirror pi(1) = sigma_adv", armA[(59, 1)]["pi"], sigma_adv_A)
    must_equal("sigma_ach(10) = 0 (repair threshold)",
               armA[(p, 10)]["sigma_ach"], fr(0))
    must_equal("f(d=9) = s", fr(strict_vals_A[1]), fr(s))
    must_equal("Delta(19) = -7039/1000 (V040 nudge cost)",
               delta19, fr(-7039, 1000))
    must_clear("f*(59) - s/2 (ratio 20/19)", fstar_A[59] - fr(s) / 2,
               "ratio " + fstr(ratio_2019))
    must_clear("pi(0) - 0 vs sigma_adv (ratio 10/9)", armA[(59, 0)]["pi"],
               "ratio " + fstr(armA[(59, 0)]["pi"] / sigma_adv_A))
    for f in (0, 1, 3, 5):
        must_clear("incoherence margin f=%d: p-(a+f)" % f,
                   fr(p) - fr(a) - fr(f), "strict exclusion")
    for f in (15, 19):
        must_clear("coherence margin f=%d: (a+f)-p" % f,
                   fr(a) + fr(f) - fr(p), "strict inclusion")

    # ------------------------------------------------- Arm R (reporting only)
    ar = FX["arm_R"]
    pmf_fh_order = [0, 10, 19]
    pmf_fh_cum = [fr(3, 5), fr(4, 5), fr(1)]
    pmf_sa_order = [19, 10, 0]
    pmf_sa_cum = [fr(3, 5), fr(4, 5), fr(1)]
    wstar_usd = p - a
    tr_main = R_trace(ar["main"]["seed"], ar["main"]["episodes"],
                      pmf_fh_order, [float(x) for x in pmf_fh_cum],
                      a, p, wstar_usd)
    tr_stab = R_trace(ar["stability"]["seed"], ar["stability"]["episodes"],
                      pmf_sa_order, [float(x) for x in pmf_sa_cum],
                      a, p, wstar_usd)
    check("F6 Arm-R draw sentinel main (50,000)",
          tr_main["draws"] == 50000 == tr_main["episodes"])
    check("F6 Arm-R draw sentinel stability (20,000)",
          tr_stab["draws"] == 20000 == tr_stab["episodes"])
    mean_main = fr(tr_main["outlay_sum"], tr_main["episodes"])
    mean_stab = fr(tr_stab["outlay_sum"], tr_stab["episodes"])
    take_main = fr(tr_main["bundle_take"], tr_main["episodes"])
    take_stab = fr(tr_stab["bundle_take"], tr_stab["episodes"])
    # presentation shuffle (presentation leg only)
    pres_rng = RegisteredRandom(ar["presentation_shuffle_seed"])
    pres_rows = [str(f) for f in f_grid]
    pres_rng.shuffle(pres_rows)
    check("C7 seed registry exactly [20261660, 20261661, 20261662]",
          SEED_REGISTRY == [20261660, 20261661, 20261662])
    check("C7 aux 20261663 never read",
          ar["aux_seed_never_read"] == 20261663
          and 20261663 not in SEED_REGISTRY)

    # ------------------------------------------------- ruling
    rulA, clausesA = evaluate_A()
    rulB, clausesB = evaluate_B()
    check("F6 twin decision evaluators agree", rulA == rulB)
    check("F6 clause vectors agree", clausesA == clausesB)
    ruling = rulA if rulA == rulB else "INVALID"
    if FAILURES and ruling != "INVALID":
        ruling = "INVALID"
    check("exactly one ruling token",
          ruling in ("REJECT", "INVALID", "APPROVE", "NULL"))

    # ------------------------------------------------- results
    results = {
        "anomalies": ANOMALIES,
        "arm_R": {
            "main": {
                "pmf": "FLOOR_HEAVY",
                "seed": tr_main["seed"],
                "episodes": tr_main["episodes"],
                "draws": tr_main["draws"],
                "bundle_take": tr_main["bundle_take"],
                "bundle_take_fraction": fstr(take_main),
                "mean_outlay": fstr(mean_main),
                "exact_expectation_take": "2/5",
                "exact_expectation_mean": 53,
            },
            "stability": {
                "pmf": "SUGGESTED_ANCHORED",
                "seed": tr_stab["seed"],
                "episodes": tr_stab["episodes"],
                "draws": tr_stab["draws"],
                "bundle_take": tr_stab["bundle_take"],
                "bundle_take_fraction": fstr(take_stab),
                "mean_outlay": fstr(mean_stab),
                "exact_expectation_take": "4/5",
                "exact_expectation_mean": 57,
            },
            "presentation_row_order": pres_rows,
            "statistical_gate": "none (reporting-only)",
        },
        "census_f_grid_at_p59": {
            str(f): {
                "coherent": armA[(59, f)]["coherent"],
                "sigma_ach": fstr(armA[(59, f)]["sigma_ach"]),
                "pi": fstr(armA[(59, f)]["pi"]),
                "gap": fstr(armA[(59, f)]["gap"]),
                "Delta": fstr(armA[(59, f)]["delta"]),
            } for f in f_grid
        },
        "clauses": {"R1": clausesA[0], "R2": clausesA[1], "R3": clausesA[2]},
        "committed_triple": {"a": a, "s": s, "p": p, "copy_claim": 9},
        "decision_cell": {"f": 0, "window": "{49}", "sigma_adv": "9",
                          "sigma_ach": "-10", "pi": "10",
                          "seller_delta": "951/100"},
        "external_anchors": {
            # printed over the registered denominator 1000 (same exact
            # rationals; Fraction() reduces 54944/1000 and 58428/1000)
            "net_49": "%d/1000" % B_net_md(49),
            "net_59": "%d/1000" % B_net_md(59),
            "net_64": "%d/1000" % B_net_md(64),
            "net_68": "%d/1000" % B_net_md(68),
            "plus_080_row": fstr(plus080),
            "retention_bar": fstr(bar),
            "nudge_cost_Delta19": fstr(delta19),
        },
        "falsifiability": {
            "approve_liveness_cells": approve_live,
            "basis_reading": "on the vs-suggested reading the copy is TRUE; "
                             "the gap table s - f ships as the NULL-axis finding",
            "r1_independent_of_margin0_cell": r1_alone,
            "sibling_3_floor": {"pi": fstr(armA[(59, 3)]["pi"]),
                                "coherent": armA[(59, 3)]["coherent"]},
        },
        "fstar_table": {str(pp): fstr(fstar_A[pp]) for pp in anchors},
        "granularity_thresholds_cents": gran,
        "margin_ledger": ledger,
        "ruling": ruling,
        "ruling_twin": {"arm_A": rulA, "arm_B": rulB},
        "seeds": {"registry": SEED_REGISTRY, "aux_never_read": 20261663},
        "self_checks": {"passed": CHECKS["passed"], "failed": CHECKS["failed"]},
        "strict_discount_law": {"d": [1, 9], "f_of_d": strict_vals_A},
        "wstar": fstr(wstar_A),
    }

    out_path = os.path.join(here, "results.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)
        fh.write("\n")

    # ------------------------------------------------- stdout
    print("VERDICT 087 — bundle-PWYW floor lattice (P074)")
    print("ruling: %s (twin evaluators %s / %s)" % (ruling, rulA, rulB))
    print("committed triple: a=49 kit, s=19 suggested PWYW, p=59 bundle; "
          "copy claims +$9; floor f UNCOMMITTED (decision cell f=0)")
    for f in f_grid:
        ra = armA[(59, f)]
        print("census f=%-2d: coherent=%-3s sigma_ach=%-3s pi=%-2s gap=%-2s "
              "Delta=%s" % (f, "yes" if ra["coherent"] else "no",
                            fstr(ra["sigma_ach"]), fstr(ra["pi"]),
                            fstr(ra["gap"]), fstr(ra["delta"])))
    print("f* table: 59->10 64->15 68->19 (f*(68)=19=s registered margin-0 "
          "must-equal; f*(59)/(s/2)=%s; pi(0)/sigma_adv=%s)"
          % (fstr(ratio_2019), fstr(armA[(59, 0)]["pi"] / sigma_adv_A)))
    print("repair law: f(d)=10+d at d in {1,9} -> %s; committed $9 needs "
          "f=19=s (PWYW extinct)" % strict_vals_A)
    print("fee fork @ f=0: seller %s, buyer %s; f-invariant saving = %s "
          "(the seller's saved second fee)"
          % (fstr(armA[(59, 0)]["delta"]), fstr(armA[(59, 0)]["sigma_ach"]),
             fstr(beta)))
    print("external anchors: net49=%d/1000 net59=%d/1000 net64=%d/1000 "
          "net68=%d/1000 +080row=%s bar=%s Delta19=%s"
          % (B_net_md(49), B_net_md(59), B_net_md(64), B_net_md(68),
             fstr(plus080), fstr(bar), fstr(delta19)))
    print("hand world (3,2,4): w*=1 f*=1 gap=2 window={3} pi=1 "
          "(armB cent-scan w*=%d cents)" % hw_wstar_c)
    print("approve liveness (f>=10 cells fire APPROVE): %s" % approve_live)
    print("granularity thresholds (cents): %s"
          % json.dumps(gran, sort_keys=True))
    print("arm R main (FLOOR-HEAVY, %d): bundle=%d/%d (%s; exact 2/5) "
          "mean=%s (exact 53)"
          % (tr_main["seed"], tr_main["bundle_take"], tr_main["episodes"],
             fstr(take_main), fstr(mean_main)))
    print("arm R stability (SUGGESTED-ANCHORED, %d): bundle=%d/%d (%s; "
          "exact 4/5) mean=%s (exact 57)"
          % (tr_stab["seed"], tr_stab["bundle_take"], tr_stab["episodes"],
             fstr(take_stab), fstr(mean_stab)))
    print("presentation row order (seed 20261662): %s" % ",".join(pres_rows))
    print("seed registry: %s (aux 20261663 never read)" % SEED_REGISTRY)
    if ANOMALIES:
        print("anomalies (%d):" % len(ANOMALIES))
        for a_ in ANOMALIES:
            print("  " + a_)
    else:
        print("anomalies: none")
    print("self-checks: %d passed, %d failed"
          % (CHECKS["passed"], CHECKS["failed"]))
    if FAILURES:
        for f in FAILURES:
            print("  FAILED: " + f)
    # C13 exit contract
    sys.exit(0 if not FAILURES and ruling in
             ("REJECT", "APPROVE", "NULL", "INVALID") else 1)


if __name__ == "__main__":
    main()
