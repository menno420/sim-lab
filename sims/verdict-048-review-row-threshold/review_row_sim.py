#!/usr/bin/env python3
"""VERDICT 048 — review-queue row-trigger threshold (idea-engine PROPOSAL 037).

Prices the fleet-manager review-queue auto-append rule's decide-and-flag
N = 50 row-trigger threshold on the registration's pinned merge-stream model.

Dual-arm, per the registration:
  Arm A — exact, seedless, platform-independent: every decision number a
          closed-form fractions.Fraction via geometric partial sums.
  Arm S — seeded event-driven MC of the stream + 6-h batch-drain queue,
          seeds 20261285 (main) / 20261286 (stability, half-M) /
          20261287 (reporting) / 20261288 (aux, reserved — zero draws),
          all strictly above the fleet seed high-water 20261284.

Hermetic: reads ONLY its own fixtures.json; writes results.json + stdout.
Deterministic: byte-identical stdout + results.json across process runs
under the pinned CPython minor (3.11).

Run: python3 sims/verdict-048-review-row-threshold/review_row_sim.py
"""

import json
import math
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- self-checks
CHECKS = {"passed": 0, "failed": 0}


def check(cond, label):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        print("SELF-CHECK FAIL: %s" % label)
    return cond


def F(s):
    return Fraction(s)


def fstr(fr):
    return "%d/%d" % (fr.numerator, fr.denominator)


def fdec(fr, places=5):
    """Exact decimal string (truncated) by integer long division."""
    neg = fr < 0
    fr = abs(fr)
    ip = fr.numerator // fr.denominator
    rem = fr.numerator - ip * fr.denominator
    digits = []
    for _ in range(places):
        rem *= 10
        digits.append(str(rem // fr.denominator))
        rem -= (rem // fr.denominator) * fr.denominator
    return ("-" if neg else "") + str(ip) + "." + "".join(digits)


def ffl(x):
    return "%.6f" % x


# ---------------------------------------------------------------- fixtures
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

check(sys.version_info[:2] == (3, 11),
      "CPython minor pinned 3.11 (running %d.%d)" % sys.version_info[:2])

P_C = F("1/12")
P_F = F("1/80")
OFFSET = FX["stream_model"]["feature_offset"]           # 40
Q1 = F(FX["defect_model"]["q1_pinned"])                  # 1/400
Q1_SENS = [F(x) for x in FX["defect_model"]["q1_sensitivity_reporting_only"]]
R = F(FX["flag_model"]["r_pinned"])                      # 3/10
R_SENS = [F(x) for x in FX["flag_model"]["r_sensitivity_reporting_only"]]
N_GRID = FX["N_grid"]                                    # [0,10,25,50,100,200]
N_LEGS = N_GRID + ["inf"]
PLANTED = FX["planted_N"]                                # 50
D_GRID = [F(x) for x in FX["drain_model"]["d_grid"]]
LAM = FX["drain_model"]["lambda_per_day"]                # 40
MIX_ORDER = ["BASE", "BUILD-HEAVY", "DOCS-HEAVY"]        # lexicographic
MIXES = {k: [F(x) for x in FX["stream_model"]["mix_profiles_w0_wc_wf"][k]]
         for k in MIX_ORDER}
REL_BAND = F(FX["bands"]["REL_band"])                    # 3/10
RHO_BAND = F(FX["bands"]["rho_band"])                    # 4/5
M_MAIN = FX["arm_S"]["M_days_per_cell_N"]                # 2000
M_STAB = FX["arm_S"]["stability_M_days"]                 # 1000
SEEDS = FX["arm_S"]["seeds"]
TOL_MUL = FX["tolerances"]["tol_sigma_multiplier"]       # 5.0
CELLS = [(d, mix) for d in D_GRID for mix in MIX_ORDER]  # lexicographic d, mix


def cell_name(cell):
    return "d=%s %s" % (fstr(cell[0]), cell[1])


# ---------------------------------------------------------------- Arm A exact
def arm_A_mix(mix, q1):
    """Exact per-mix quantities independent of N."""
    w0, wc, wf = MIXES[mix]
    a = 1 - q1
    kc = P_C * a / (1 - (1 - P_C) * a)
    bc = (1 - P_C) * a
    a40 = a ** OFFSET
    kf = P_F * a / (1 - (1 - P_F) * a)
    bf = (1 - P_F) * a
    dc = 1 - kc                      # P(defect | TWEAK)
    df = 1 - a40 * kf                # P(defect | FEATURE)
    p_def = wc * dc + wf * df
    return {"w0": w0, "wc": wc, "wf": wf, "a": a, "kc": kc, "bc": bc,
            "a40": a40, "kf": kf, "bf": bf, "dc": dc, "df": df,
            "p_def": p_def}


def arm_A_point(mx, N, r):
    """Exact (P_S_gt, X = P(def AND S<=N), REL, P_row) at one N leg."""
    wc, wf = mx["wc"], mx["wf"]
    if N == "inf":
        t_c = Fraction(0)
        t_f = Fraction(0)
        x_c = mx["dc"]
        x_f = mx["df"]
    else:
        t_c = (1 - P_C) ** N
        t_f = Fraction(1) if N <= OFFSET else (1 - P_F) ** (N - OFFSET)
        x_c = (1 - t_c) - mx["kc"] * (1 - mx["bc"] ** N)
        if N <= OFFSET:
            x_f = Fraction(0)
        else:
            m = N - OFFSET
            x_f = (1 - t_f) - mx["a40"] * mx["kf"] * (1 - mx["bf"] ** m)
    p_gt = wc * t_c + wf * t_f
    x = wc * x_c + wf * x_f
    rel = x / mx["p_def"]
    p_row = p_gt + r * x + (r / 3) * ((1 - p_gt) - x)
    return p_gt, x, rel, p_row


def arm_A_table(q1, r):
    """{(mix, Nleg): (p_gt, x, rel, p_row)} exact, all mixes, all N legs."""
    out = {}
    for mix in MIX_ORDER:
        mx = arm_A_mix(mix, q1)
        for N in N_LEGS:
            out[(mix, N)] = arm_A_point(mx, N, r)
    return out


A_PINNED = arm_A_table(Q1, R)
P_DEF = {mix: arm_A_mix(mix, Q1)["p_def"] for mix in MIX_ORDER}

# Exact-identity controls + monotonicity audits (exact arm; run invalid on fail)
for mix in MIX_ORDER:
    check(A_PINNED[(mix, 0)][2] == 0, "identity REL_A(0)==0 @ %s" % mix)
    check(A_PINNED[(mix, "inf")][2] == 1, "identity REL_A(inf)==1 @ %s" % mix)
    esc_inf = (1 - R) * A_PINNED[(mix, "inf")][2]
    check(esc_inf == 1 - R, "identity ESC_A(inf)==1-r @ %s" % mix)
    rels = [A_PINNED[(mix, N)][2] for N in N_LEGS]
    rows = [A_PINNED[(mix, N)][3] for N in N_LEGS]
    check(all(rels[i] <= rels[i + 1] for i in range(len(rels) - 1)),
          "monotone REL_A nondecreasing @ %s" % mix)
    check(all(rows[i] >= rows[i + 1] for i in range(len(rows) - 1)),
          "monotone P_row_A nonincreasing @ %s" % mix)

# ------------------------------------------------- tolerance pre-check (gate)
check(TOL_MUL >= 2.5,
      "tolerance multiplier %.1f >= 2.5 sigma pre-checked BEFORE any MC run"
      % TOL_MUL)
TOLS = {}
for cell in CELLS:
    d, mix = cell
    n_pr = M_MAIN * LAM
    for N in N_LEGS:
        _, _, rel, p_row = A_PINNED[(mix, N)]
        relf, prf, pdf = float(rel), float(p_row), float(P_DEF[mix])
        s_rel = math.sqrt(relf * (1 - relf) / (n_pr * pdf))
        s_rho = math.sqrt(prf * (1 - prf) / n_pr) / float(d)
        TOLS[(cell, N)] = (TOL_MUL * s_rel, TOL_MUL * s_rho)

# ---------------------------------------------------------------- Arm S (MC)
LN1M_C = math.log(1.0 - 1.0 / 12.0)
LN1M_F = math.log(1.0 - 1.0 / 80.0)
A_FLOAT = 1.0 - float(Q1)            # 0.9975
R_FLOAT = float(R)
R3_FLOAT = float(R / 3)


def stream_leg(seed, m_days, with_queue=False):
    """One MC leg over all cells x N legs, pinned loop order.

    Returns per-(cell, Nleg) estimates and, with_queue, latency/backlog stats.
    """
    rng = random.Random(seed)
    rnd = rng.random
    out = {}
    draws_total = 0
    for cell in CELLS:
        d, mix = cell
        w0, wc, _ = MIXES[mix]
        t0, t1 = float(w0), float(w0 + wc)
        d_f = float(d)
        cap_batch = int(d * LAM) // 4          # 6-h batch capacity (2/4/8)
        check((d * LAM) % 4 == 0,
              "batch capacity integer @ %s" % cell_name(cell))
        for N in N_LEGS:
            n_fin = None if N == "inf" else N
            n_pr = 0
            n_nondocs = 0
            n_def = 0
            n_def_le = 0
            n_row = 0
            draws = 0
            pending = []                        # sorted row arrival times
            drained_ages = []
            appended = 0
            drained_72h = 0
            for day in range(m_days):
                day_rows = []
                for _ in range(LAM):
                    n_pr += 1
                    u = rnd()
                    draws += 1
                    if u < t0:
                        s = 0
                    elif u < t1:
                        u2 = 1.0 - rnd()
                        draws += 1
                        s = 1 + int(math.log(u2) / LN1M_C)
                        n_nondocs += 1
                    else:
                        u2 = 1.0 - rnd()
                        draws += 1
                        s = OFFSET + 1 + int(math.log(u2) / LN1M_F)
                        n_nondocs += 1
                    defect = False
                    if s > 0:
                        draws += 1
                        defect = rnd() < (1.0 - A_FLOAT ** s)
                    draws += 1
                    flag = rnd() < (R_FLOAT if defect else R3_FLOAT)
                    if defect:
                        n_def += 1
                        if n_fin is None or s <= n_fin:
                            n_def_le += 1      # S <= inf holds for every S
                    row = flag or (n_fin is not None and s > n_fin)
                    if with_queue:
                        draws += 1
                        t_arr = day + rnd()     # arrival time, always drawn
                        if row:
                            day_rows.append(t_arr)
                    if row:
                        n_row += 1
                if with_queue:
                    day_rows.sort()
                    pending.extend(day_rows)
                    appended += len(day_rows)
                    for kb in range(1, 5):
                        t_b = day + 0.25 * kb
                        c = cap_batch
                        i = 0
                        while c > 0 and i < len(pending) and pending[i] <= t_b:
                            age = t_b - pending[i]
                            drained_ages.append(age)
                            if age <= 3.0:
                                drained_72h += 1
                            i += 1
                            c -= 1
                        if i:
                            del pending[:i]
            # per-leg draw-count sentinel
            expect = 2 * n_pr + 2 * n_nondocs + (n_pr if with_queue else 0)
            check(draws == expect,
                  "draw sentinel @ %s N=%s (%d==%d)"
                  % (cell_name(cell), N, draws, expect))
            draws_total += draws
            rel_s = n_def_le / n_def
            p_row_s = n_row / n_pr
            rec = {"rel": rel_s, "p_row": p_row_s, "rho": p_row_s / d_f,
                   "n_def": n_def}
            if with_queue:
                rec["appended"] = appended
                rec["backlog_end"] = len(pending)
                if drained_ages:
                    sa = sorted(drained_ages)
                    idx = max(0, math.ceil(0.95 * len(sa)) - 1)
                    rec["p95_age_h"] = sa[idx] * 24.0
                else:
                    rec["p95_age_h"] = None
                rec["share_72h"] = (drained_72h / appended) if appended else None
            out[(cell, N)] = rec
    return out, draws_total


# ------------------------------------------------- twin decision evaluators
def feas_table(rel_of, rho_of, rel_band, rho_band):
    return {cell: set(N for N in N_GRID
                      if rel_of(cell, N) <= rel_band
                      and rho_of(cell, N) <= rho_band)
            for cell in CELLS}


def evaluator_one(rel_of, rho_of, rel_band, rho_band):
    """Cell-major: build Feas sets, then apply the rules in order."""
    feas = feas_table(rel_of, rho_of, rel_band, rho_band)
    empty = sum(1 for cell in CELLS if not feas[cell])
    per_n = {N: sum(1 for cell in CELLS if N in feas[cell]) for N in N_GRID}
    if empty >= 5:
        return {"ruling": "REJECT", "empty_cells": empty, "per_N": per_n,
                "N_dagger": None, "feas": feas}
    cands = [N for N in N_GRID if per_n[N] >= 8]
    if cands:
        nd = min(cands)
        tier = None
        for d in D_GRID:
            if all(nd in feas[(d, mix)] for mix in MIX_ORDER):
                tier = d
                break
        return {"ruling": "APPROVE", "empty_cells": empty, "per_N": per_n,
                "N_dagger": nd, "tier": tier, "feas": feas}
    return {"ruling": "NULL", "empty_cells": empty, "per_N": per_n,
            "N_dagger": None, "feas": feas}


def evaluator_two(rel_of, rho_of, rel_band, rho_band):
    """N-major, list-based — written independently of evaluator_one."""
    feasible_pairs = []
    for N in N_GRID:
        for cell in CELLS:
            ok_rel = not (rel_of(cell, N) > rel_band)
            ok_rho = not (rho_of(cell, N) > rho_band)
            if ok_rel and ok_rho:
                feasible_pairs.append((N, cell))
    cells_with_any = set(c for (_, c) in feasible_pairs)
    empty = len(CELLS) - len(cells_with_any)
    per_n = {}
    for N in N_GRID:
        per_n[N] = len([1 for (n2, _) in feasible_pairs if n2 == N])
    ruling = None
    if empty >= 5:
        ruling = "REJECT"
        nd = None
    else:
        winners = sorted(N for N in N_GRID if per_n[N] >= 8)
        if winners:
            ruling = "APPROVE"
            nd = winners[0]
        else:
            ruling = "NULL"
            nd = None
    feas = {cell: set(n2 for (n2, c2) in feasible_pairs if c2 == cell)
            for cell in CELLS}
    out = {"ruling": ruling, "empty_cells": empty, "per_N": per_n,
           "N_dagger": nd, "feas": feas}
    if ruling == "APPROVE":
        tier = None
        for d in D_GRID:
            if all((nd, (d, mix)) in set(feasible_pairs) for mix in MIX_ORDER):
                tier = d
                break
        out["tier"] = tier
    return out


def evaluate_both(rel_of, rho_of, rel_band, rho_band, label):
    e1 = evaluator_one(rel_of, rho_of, rel_band, rho_band)
    e2 = evaluator_two(rel_of, rho_of, rel_band, rho_band)
    check(e1["ruling"] == e2["ruling"]
          and e1["empty_cells"] == e2["empty_cells"]
          and e1["per_N"] == e2["per_N"]
          and e1["N_dagger"] == e2["N_dagger"]
          and e1["feas"] == e2["feas"],
          "twin evaluators agree on %s" % label)
    return e1


# ---------------------------------------------------------------- run legs
print("=" * 78)
print("VERDICT 048 — review-queue row-trigger threshold (the decide-and-flag N = 50)")
print("idea-engine PROPOSAL 037 · fleet-manager docs/review-queue.md @ 06ce3cc")
print("=" * 78)
print("9 decision cells = d in {1/5, 2/5, 4/5} x mix {BASE, BUILD-HEAVY, DOCS-HEAVY}")
print("N grid %s + inf control · bands REL <= 3/10 AND rho <= 4/5" % N_GRID)
print("Arm A exact Fractions (54 decision points, zero sampling error)")
print("Arm S seeded MC: M=%d days x lambda=%d/day per (cell, N); seeds "
      "%d main / %d stability (half-M) / %d reporting / %d aux (reserved, 0 draws)"
      % (M_MAIN, LAM, SEEDS["main"], SEEDS["stability"], SEEDS["reporting"],
         SEEDS["aux"]))
print("fleet seed high-water before this run: 20261284 (all seeds strictly above)")
print("tolerance pre-check: %.1f sigma familywise (>= 2.5 sigma, asserted "
      "BEFORE any MC run)" % TOL_MUL)
print()

main_est, main_draws = stream_leg(SEEDS["main"], M_MAIN, with_queue=False)
stab_est, stab_draws = stream_leg(SEEDS["stability"], M_STAB, with_queue=False)
rep_est, rep_draws = stream_leg(SEEDS["reporting"], M_MAIN, with_queue=True)

# ---------------------------------------------------------------- gates: MC
for cell in CELLS:
    d, mix = cell
    for N in N_LEGS:
        _, _, rel_a, p_row_a = A_PINNED[(mix, N)]
        rho_a = p_row_a / d
        est = main_est[(cell, N)]
        tol_rel, tol_rho = TOLS[(cell, N)]
        check(abs(est["rel"] - float(rel_a)) <= tol_rel,
              "agreement |REL_S-REL_A| @ %s N=%s" % (cell_name(cell), N))
        check(abs(est["rho"] - float(rho_a)) <= tol_rho,
              "agreement |rho_S-rho_A| @ %s N=%s" % (cell_name(cell), N))
    # exact-identity controls on the MC arm
    check(main_est[(cell, 0)]["rel"] == 0.0,
          "identity REL_S(0)==0 @ %s" % cell_name(cell))
    check(main_est[(cell, "inf")]["rel"] == 1.0,
          "identity REL_S(inf)==1 @ %s" % cell_name(cell))

# MC monotonicity inversions — sampling diagnostics, reporting-only
mc_inversions = 0
for cell in CELLS:
    rels = [main_est[(cell, N)]["rel"] for N in N_LEGS]
    rows = [main_est[(cell, N)]["p_row"] for N in N_LEGS]
    mc_inversions += sum(1 for i in range(len(rels) - 1) if rels[i] > rels[i + 1])
    mc_inversions += sum(1 for i in range(len(rows) - 1) if rows[i] < rows[i + 1])

# ---------------------------------------------------------------- decision
def rel_A_of(cell, N):
    return A_PINNED[(cell[1], N)][2]


def rho_A_of(cell, N):
    return A_PINNED[(cell[1], N)][3] / cell[0]


DEC = evaluate_both(rel_A_of, rho_A_of, REL_BAND, RHO_BAND, "Arm A exact")

REL_BAND_F, RHO_BAND_F = float(REL_BAND), float(RHO_BAND)
DEC_MAIN = evaluate_both(lambda c, n: main_est[(c, n)]["rel"],
                         lambda c, n: main_est[(c, n)]["rho"],
                         REL_BAND_F, RHO_BAND_F, "Arm S main")
DEC_STAB = evaluate_both(lambda c, n: stab_est[(c, n)]["rel"],
                         lambda c, n: stab_est[(c, n)]["rho"],
                         REL_BAND_F, RHO_BAND_F, "Arm S stability")
check(DEC_MAIN["ruling"] == DEC["ruling"],
      "Arm S main leg reproduces the canonical ruling")
check(DEC_STAB["ruling"] == DEC["ruling"],
      "stability leg (seed %d, half-M) reproduces the canonical ruling"
      % SEEDS["stability"])

# ---------------------------------------------------------------- print tables
print("-" * 78)
print("ARM A — EXACT DECISION TABLE (REL per mix; rho per cell; feasible = "
      "REL<=3/10 AND rho<=4/5)")
print("-" * 78)
for mix in MIX_ORDER:
    print("mix %-11s P(defect)=%s (%s)"
          % (mix, fstr(P_DEF[mix]), fdec(P_DEF[mix])))
    for N in N_LEGS:
        p_gt, x, rel, p_row = A_PINNED[(mix, N)]
        print("  N=%-4s REL=%s (%s) · ESC=%s · P(row)=%s (%s)"
              % (N, fstr(rel), fdec(rel), fdec((1 - R) * rel),
                 fstr(p_row), fdec(p_row)))
print()
print("rho(N) = P(row)/d and per-cell feasibility:")
for cell in CELLS:
    d, mix = cell
    parts = []
    for N in N_GRID:
        rho = rho_A_of(cell, N)
        feas = "Y" if (rel_A_of(cell, N) <= REL_BAND and rho <= RHO_BAND) else "n"
        parts.append("N=%s:%s%s" % (N, fdec(rho, 4), feas))
    print("  %-18s %s" % (cell_name(cell), " ".join(parts)))
print()

print("-" * 78)
print("ARM S (seed %d, M=%d) vs ARM A — agreement gate (max |diff|/tol per cell)"
      % (SEEDS["main"], M_MAIN))
print("-" * 78)
for cell in CELLS:
    worst = 0.0
    for N in N_LEGS:
        d, mix = cell
        rel_a = float(A_PINNED[(mix, N)][2])
        rho_a = float(A_PINNED[(mix, N)][3] / d)
        tol_rel, tol_rho = TOLS[(cell, N)]
        if tol_rel > 0:
            worst = max(worst, abs(main_est[(cell, N)]["rel"] - rel_a) / tol_rel)
        worst = max(worst, abs(main_est[(cell, N)]["rho"] - rho_a) / tol_rho)
    print("  %-18s max |diff|/tol = %s  (gate: <= 1)" % (cell_name(cell), ffl(worst)))
print("MC monotonicity adjacent-pair inversions (reporting-only diagnostics,"
      " fresh draws per (cell, N)): %d" % mc_inversions)
print()

print("-" * 78)
print("PRE-REGISTERED DECISION RULE — evaluated IN ORDER (Arm A exact Fractions)")
print("-" * 78)
feas = DEC["feas"]
empties = [cell_name(c) for c in CELLS if not feas[c]]
print("Feas(cell) per cell:")
for cell in CELLS:
    print("  %-18s Feas = {%s}"
          % (cell_name(cell), ", ".join(str(n) for n in sorted(feas[cell]))))
print("1. REJECT iff Feas(cell) = EMPTY in >= 5 of 9 cells (checked FIRST):")
print("     empty cells: %d of 9 — %s"
      % (DEC["empty_cells"], ", ".join(empties) if empties else "none"))
print("   REJECT %s" % ("FIRES" if DEC["ruling"] == "REJECT" else "does not fire"))
print("2. APPROVE iff a single N-dagger is feasible in >= 8 of 9 cells,"
      " stability-reproduced:")
for N in N_GRID:
    print("     N=%-4s feasible in %d/9 cells" % (N, DEC["per_N"][N]))
print("   APPROVE %s" % ("FIRES (N-dagger=%s)" % DEC["N_dagger"]
                         if DEC["ruling"] == "APPROVE" else "does not fire"))
print("3. NULL otherwise%s." % (" — FIRES (conditional NULL)"
                                if DEC["ruling"] == "NULL" else ""))
print()
print("RULING: %s (stability leg seed %d reproduces: %s; main MC leg: %s)"
      % (DEC["ruling"], SEEDS["stability"], DEC_STAB["ruling"],
         DEC_MAIN["ruling"]))
print()

# NULL consequence: per-axis shares + medians + the conditional rule
def lower_median(vals):
    s = sorted(vals)
    return s[(len(s) - 1) // 2] if s else None


null_summary = {}
if DEC["ruling"] == "NULL":
    print("-" * 78)
    print("NULL CONSEQUENCE — the conditional per-tier/per-mix rule (pre-registered)")
    print("-" * 78)
    per_d = {}
    for d in D_GRID:
        cs = [(d, mix) for mix in MIX_ORDER]
        nonempty = [c for c in cs if feas[c]]
        med = lower_median([min(feas[c]) for c in nonempty])
        per_d[fstr(d)] = {"feasible_cell_share": "%d/3" % len(nonempty),
                          "median_min_feasible_N": med}
        print("  d=%-4s feasible-cell share %d/3 · median minimal feasible N: %s"
              % (fstr(d), len(nonempty), med))
    per_mix = {}
    for mix in MIX_ORDER:
        cs = [(d, mix) for d in D_GRID]
        nonempty = [c for c in cs if feas[c]]
        med = lower_median([min(feas[c]) for c in nonempty])
        per_mix[mix] = {"feasible_cell_share": "%d/3" % len(nonempty),
                        "median_min_feasible_N": med}
        print("  mix %-11s feasible-cell share %d/3 · median minimal feasible N: %s"
              % (mix, len(nonempty), med))
    print("  per-tier intersection of Feas across the three mixes:")
    cond_lines = []
    for d in D_GRID:
        inter = set(N_GRID)
        for mix in MIX_ORDER:
            inter &= feas[(d, mix)]
        planted_in = PLANTED in inter
        line = ("d=%s: common feasible N = {%s} · planted N=50 %s"
                % (fstr(d), ", ".join(str(n) for n in sorted(inter)),
                   "HOLDS in all mixes" if planted_in else "does NOT hold in all mixes"))
        cond_lines.append(line)
        print("    " + line)
    null_summary = {"per_d": per_d, "per_mix": per_mix,
                    "per_tier_common_feasible": cond_lines}
    print("  cheapest LIVE probes (named, zero new tooling — pre-registered):")
    for p in FX["decision_rules_pre_registered"]["NULL"]["named_live_probes"]:
        print("    - " + p)
    print()

# ---------------------------------------------------------------- reporting
print("-" * 78)
print("REPORTING-ONLY LEGS (cannot flip the decision)")
print("-" * 78)
print("Latency/backlog (seed %d, stream + 6-h batch FIFO drain, lambda=%d/day"
      " — the only lambda-pinned legs):" % (SEEDS["reporting"], LAM))
for cell in CELLS:
    d, mix = cell
    parts = []
    for N in N_GRID:
        rho_a = rho_A_of(cell, N)
        e = rep_est[(cell, N)]
        if rho_a < 1:
            p95 = "None" if e["p95_age_h"] is None else "%.1fh" % e["p95_age_h"]
            s72 = "None" if e["share_72h"] is None else "%.4f" % e["share_72h"]
            parts.append("N=%s[p95=%s <=72h=%s]" % (N, p95, s72))
        else:
            parts.append("N=%s[UNSTABLE rho_A=%s backlog_end=%d growth=%.2f/day]"
                         % (N, fdec(rho_a, 3), e["backlog_end"],
                            e["backlog_end"] / M_MAIN))
    print("  %-18s %s" % (cell_name(cell), " ".join(parts)))
print()
print("Ceremony-drown crossover (largest N in grid with rho > 1, per cell) and")
print("mid-size miss mass (defect mass in 25 < S <= N = REL_A(N) - REL_A(25)):")
crossovers = {}
for cell in CELLS:
    over = [N for N in N_GRID if rho_A_of(cell, N) > 1]
    crossovers[cell_name(cell)] = max(over) if over else None
    print("  %-18s crossover N = %s" % (cell_name(cell),
                                        max(over) if over else "none"))
miss_mass = {}
for mix in MIX_ORDER:
    row = {}
    for N in (50, 100, 200):
        mm = A_PINNED[(mix, N)][2] - A_PINNED[(mix, 25)][2]
        row[str(N)] = {"exact": fstr(mm), "dec": fdec(mm)}
    miss_mass[mix] = row
    print("  mix %-11s miss mass: N=50 %s · N=100 %s · N=200 %s"
          % (mix, row["50"]["dec"], row["100"]["dec"], row["200"]["dec"]))
print()

print("Sensitivity sweeps (exact Arm A recomputation; reporting-only):")
sens = {}
for q1v in Q1_SENS:
    tab = arm_A_table(q1v, R)
    e = evaluate_both(lambda c, n: tab[(c[1], n)][2],
                      lambda c, n: tab[(c[1], n)][3] / c[0],
                      REL_BAND, RHO_BAND, "sensitivity q1=%s" % fstr(q1v))
    sens["q1=%s" % fstr(q1v)] = {
        "ruling_if_it_were_binding": e["ruling"],
        "empty_cells": e["empty_cells"],
        "feas": {cell_name(c): sorted(e["feas"][c]) for c in CELLS}}
    print("  q1=%-6s (r=3/10): empty cells %d/9 · rule-shape %s"
          % (fstr(q1v), e["empty_cells"], e["ruling"]))
for rv in R_SENS:
    tab = arm_A_table(Q1, rv)
    e = evaluate_both(lambda c, n: tab[(c[1], n)][2],
                      lambda c, n: tab[(c[1], n)][3] / c[0],
                      REL_BAND, RHO_BAND, "sensitivity r=%s" % fstr(rv))
    sens["r=%s" % fstr(rv)] = {
        "ruling_if_it_were_binding": e["ruling"],
        "empty_cells": e["empty_cells"],
        "feas": {cell_name(c): sorted(e["feas"][c]) for c in CELLS}}
    print("  r=%-6s (q1=1/400): empty cells %d/9 · rule-shape %s"
          % (fstr(rv), e["empty_cells"], e["ruling"]))
print()

# ---------------------------------------------------------------- results.json
def a_point_json(mix, N):
    p_gt, x, rel, p_row = A_PINNED[(mix, N)]
    return {"P_S_gt_N": fstr(p_gt), "P_def_and_S_le_N": fstr(x),
            "REL": {"exact": fstr(rel), "dec": fdec(rel)},
            "ESC": {"exact": fstr((1 - R) * rel), "dec": fdec((1 - R) * rel)},
            "P_row": {"exact": fstr(p_row), "dec": fdec(p_row)}}


results = {
    "identity": FX["identity"],
    "ruling": DEC["ruling"],
    "decision": {
        "empty_cells": DEC["empty_cells"],
        "per_N_feasible_cells": {str(k): v for k, v in DEC["per_N"].items()},
        "N_dagger": DEC["N_dagger"],
        "feas_per_cell": {cell_name(c): sorted(feas[c]) for c in CELLS},
        "null_summary": null_summary,
        "rulings": {"arm_A_exact": DEC["ruling"],
                    "arm_S_main": DEC_MAIN["ruling"],
                    "arm_S_stability": DEC_STAB["ruling"]},
    },
    "arm_A": {mix: {str(N): a_point_json(mix, N) for N in N_LEGS}
              for mix in MIX_ORDER},
    "arm_A_P_defect": {mix: {"exact": fstr(P_DEF[mix]), "dec": fdec(P_DEF[mix])}
                       for mix in MIX_ORDER},
    "rho_exact": {cell_name(c): {str(N): {"exact": fstr(rho_A_of(c, N)),
                                          "dec": fdec(rho_A_of(c, N))}
                                 for N in N_GRID} for c in CELLS},
    "arm_S_main": {cell_name(c): {str(N): {
        "REL": ffl(main_est[(c, N)]["rel"]),
        "rho": ffl(main_est[(c, N)]["rho"]),
        "n_def": main_est[(c, N)]["n_def"]} for N in N_LEGS} for c in CELLS},
    "arm_S_stability": {cell_name(c): {str(N): {
        "REL": ffl(stab_est[(c, N)]["rel"]),
        "rho": ffl(stab_est[(c, N)]["rho"])} for N in N_LEGS} for c in CELLS},
    "reporting": {
        "latency_backlog": {cell_name(c): {str(N): {
            "stable_by_arm_A": bool(rho_A_of(c, N) < 1),
            "p95_age_h": (None if rep_est[(c, N)]["p95_age_h"] is None
                          else "%.2f" % rep_est[(c, N)]["p95_age_h"]),
            "share_drained_72h": (None if rep_est[(c, N)]["share_72h"] is None
                                  else "%.4f" % rep_est[(c, N)]["share_72h"]),
            "backlog_end": rep_est[(c, N)]["backlog_end"],
            "rows_appended": rep_est[(c, N)]["appended"]}
            for N in N_GRID} for c in CELLS},
        "ceremony_drown_crossover": crossovers,
        "mid_size_miss_mass": miss_mass,
        "sensitivities": sens,
        "mc_monotonicity_inversions": mc_inversions,
    },
    "draw_counts": {"main": main_draws, "stability": stab_draws,
                    "reporting": rep_draws,
                    "aux_seed_20261288": 0},
    "self_checks": CHECKS,
}

CHECKS_FINAL_OK = CHECKS["failed"] == 0
results["self_checks"] = {"passed": CHECKS["passed"],
                          "failed": CHECKS["failed"]}
with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=1, sort_keys=True)
    fh.write("\n")

print("draw counts: main=%d stability=%d reporting=%d aux(20261288)=0"
      % (main_draws, stab_draws, rep_draws))
print()
print("SELF-CHECKS: %d passed, %d failed" % (CHECKS["passed"], CHECKS["failed"]))
print("results.json written.")
if not CHECKS_FINAL_OK:
    print("RUN INVALID — at least one gate failed.")
    sys.exit(1)
