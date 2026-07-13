#!/usr/bin/env python3
"""verdict-027 — claim-expiry horizons vs lane death (silence-expiry race).

Settles idea-engine PROPOSAL 025 (control/outbox.md 2026-07-13T04:49:44Z,
status: sim-ready; idea ideas/substrate-kit/claim-expiry-horizon-lane-death-
2026-07-13.md, landed via idea-engine PR #291). Hermetic: reads exactly ONE
file (its own committed fixtures.json pre-registration, cross-checked at
start), no network, no repo state, no wall clock. Arm A is seedless exact
closed forms (covers all 54 decision points with zero sampling error); Arm S
is stdlib random.Random event-driven MC under the four pinned seeds
20260744-47. Deterministic: stdout and results.json are byte-identical across
process runs (verified by external diff). Progress goes to stderr only.

Run: python3 sims/verdict-027-claim-expiry/claim_expiry_sim.py
Exit 0 iff every self-check passes.
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

CHECKS = 0


def check(cond, label):
    global CHECKS
    if not cond:
        print("SELF-CHECK FAILED: %s" % label, file=sys.stderr)
        sys.exit(1)
    CHECKS += 1


# ---------------------------------------------------------------------------
# Pre-registration cross-check (gate: fixtures literals match the runner's)
# ---------------------------------------------------------------------------
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

REGIMES = [
    ("R1", (0.9, 0.1), (1.5, 12.0), 6),
    ("R2", (0.7, 0.3), (6.0, 24.0), 4),
    ("R3", (0.6, 0.4), (12.0, 48.0), 3),
]
COLS = [("C4", 1.0 / 4.0), ("C12", 1.0 / 12.0), ("C48", 1.0 / 48.0)]
THETAS = (6.0, 12.0, 24.0, 48.0, 72.0, 168.0)
P_D = 0.10
M_S = 4000
M_STAB = 1000
M_REP = 1000
M_AUX = 500
M_DIAG = 64000
CHAIN_CAP = 200
SEED_MAIN, SEED_STAB, SEED_REP, SEED_AUX = 20260744, 20260745, 20260746, 20260747
T_MAX = 0.05
O95_MAX = 120.0
APPROVE_CELLS = 8
REJECT_CELLS = 5
GATE_T = 0.01
GATE_O_ABS = 4.0
GATE_O_REL = 0.05

check(sys.version_info[:2] == (3, 11), "CPython minor pinned to 3.11")
check(FX["arm_S"]["M_S"] == M_S, "fixtures: M_S 4000")
check(FX["arm_S"]["seed"] == SEED_MAIN, "fixtures: main seed 20260744")
check(FX["arm_S"]["stability_leg"]["seed"] == SEED_STAB, "fixtures: stability seed 20260745")
check(FX["arm_S"]["stability_leg"]["M_S"] == M_STAB, "fixtures: stability M_S 1000")
check(FX["arm_S"]["reporting_only_legs"]["seed"] == SEED_REP, "fixtures: reporting seed 20260746")
check(FX["arm_S"]["aux_stream"]["seed"] == SEED_AUX, "fixtures: aux seed 20260747")
check(FX["model"]["theta_grid_hours"] == list(THETAS), "fixtures: theta grid")
check(FX["model"]["p_d_pinned"] == P_D, "fixtures: p_d 0.10")
check(FX["model"]["p_d_sensitivity_reporting_only"] == [0.02, 0.30], "fixtures: p_d sensitivity")
check(FX["decision_rule"]["band_constants"]["T_max"] == T_MAX, "fixtures: T band 0.05")
check(FX["decision_rule"]["band_constants"]["O95_max_hours"] == O95_MAX, "fixtures: O95 band 120")
_r = FX["model"]["regimes"]
check(_r["R1_burst"]["w"] == [0.9, 0.1] and _r["R1_burst"]["m_hours"] == [1.5, 12.0]
      and _r["R1_burst"]["M"] == 6, "fixtures: R1 mixture")
check(_r["R2_daily"]["w"] == [0.7, 0.3] and _r["R2_daily"]["m_hours"] == [6.0, 24.0]
      and _r["R2_daily"]["M"] == 4, "fixtures: R2 mixture")
check(_r["R3_weekend"]["w"] == [0.6, 0.4] and _r["R3_weekend"]["m_hours"] == [12.0, 48.0]
      and _r["R3_weekend"]["M"] == 3, "fixtures: R3 mixture")


# ---------------------------------------------------------------------------
# Arm A — exact closed forms.
# ---------------------------------------------------------------------------
def t_closed(w, m, big_m, lam, theta):
    q = 0.0
    for wi, mi in zip(w, m):
        q += wi * math.exp(-theta / mi) * (lam * mi) / (1.0 + lam * mi)
    return 1.0 - (1.0 - q) ** big_m


def o95_closed(lam, theta):
    return theta + math.log(20.0) / lam


# ---------------------------------------------------------------------------
# Counted PRNG stream (per-leg draw audit).
# ---------------------------------------------------------------------------
class Stream:
    def __init__(self, seed):
        self.seed = seed
        self._r = random.Random(seed)
        self.n = 0

    def u(self):
        self.n += 1
        return self._r.random()

    def sentinel_ok(self):
        fresh = random.Random(self.seed)
        for _ in range(self.n):
            fresh.random()
        return fresh.random() == self._r.random()


# ---------------------------------------------------------------------------
# Event-driven single-claim simulation (pinned draw layout — fixtures item 2).
# ---------------------------------------------------------------------------
def sim_claim(st, w, m, big_m, lam, theta, p_d):
    """Returns ('alive', qualifying_check_count) or ('dead', latency) or
    ('dead-notakeover', None) for the theta=inf aux leg."""
    dead = st.u() < p_d
    k = int(st.u() * big_m)  # death position 0..M-1; always consumed
    if k >= big_m:  # unreachable guard (u() < 1.0 always)
        k = big_m - 1
    times = [0.0]
    t = 0.0
    for _ in range(big_m):
        u1 = st.u()
        u2 = st.u()
        mi = m[0] if u1 < w[0] else m[1]
        g = -mi * math.log(1.0 - u2)
        check(g > 0.0, "gap positive")
        t += g
        times.append(t)
    if not dead:
        t_end = times[big_m]
        hits = 0
        c = 0.0
        while True:
            c += -math.log(1.0 - st.u()) / lam
            if c >= t_end:
                break
            last = 0.0
            for te in times:
                if te <= c:
                    last = te
                else:
                    break
            if c - last > theta:
                hits += 1
        return ("alive", hits)
    t_death = times[k]
    if theta == math.inf:
        return ("dead-notakeover", None)
    limit = t_death + theta
    c = 0.0
    while c <= limit:
        c += -math.log(1.0 - st.u()) / lam
    lat = c - t_death
    check(lat > theta, "dead latency > theta")
    return ("dead", lat)


def p95(xs):
    s = sorted(xs)
    n = len(s)
    check(n > 0, "p95 sample non-empty")
    return s[max(0, math.ceil(0.95 * n) - 1)]


def run_point(st, w, m, big_m, lam, theta, p_d, n):
    alive = dead = stolen = 0
    hits_hist = [0, 0, 0, 0]  # 0, 1, 2, >=3 qualifying checks per alive claim
    lats = []
    for _ in range(n):
        kind, val = sim_claim(st, w, m, big_m, lam, theta, p_d)
        if kind == "alive":
            alive += 1
            if val >= 1:
                stolen += 1
            hits_hist[min(val, 3)] += 1
        else:
            dead += 1
            if kind == "dead":
                lats.append(val)
    check(alive + dead == n, "point partition")
    t_s = stolen / alive if alive else None
    o95_s = p95(lats) if lats else None
    return {"n": n, "alive": alive, "dead": dead, "stolen": stolen,
            "T_S": t_s, "O95_S": o95_s, "multi_steal_hist": hits_hist}


def sim_chain(st, w, m, big_m, lam, theta, p_d):
    """Takeover chain: dead lanes hand over at first qualifying check; the
    taker restarts with fresh work. Returns (time_to_done, lanes, wasted)."""
    t0 = 0.0
    lanes = 1
    wasted = 0
    for _ in range(CHAIN_CAP):
        dead = st.u() < p_d
        k = int(st.u() * big_m)
        if k >= big_m:
            k = big_m - 1
        times = [t0]
        t = t0
        for _ in range(big_m):
            u1 = st.u()
            u2 = st.u()
            mi = m[0] if u1 < w[0] else m[1]
            t += -mi * math.log(1.0 - u2)
            times.append(t)
        if not dead:
            t_end = times[big_m]
            c = t0
            seg_stolen = False
            while True:
                c += -math.log(1.0 - st.u()) / lam
                if c >= t_end:
                    break
                last = times[0]
                for te in times:
                    if te <= c:
                        last = te
                    else:
                        break
                if c - last > theta:
                    seg_stolen = True
            if seg_stolen:
                wasted += 1
            return (t_end, lanes, wasted)
        t_death = times[k]
        limit = t_death + theta
        c = t0
        while c <= limit:
            c += -math.log(1.0 - st.u()) / lam
        t0 = c
        lanes += 1
    check(False, "chain depth cap hit")


# ---------------------------------------------------------------------------
# Decision machinery (registered order: APPROVE -> REJECT -> NULL).
# ---------------------------------------------------------------------------
CELLS = [(rn, cn) for rn, _, _, _ in REGIMES for cn, _ in COLS]


def median(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0:
        return None
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def decide(table):
    """table[(cell, theta)] = (T, O95) with possible None (tiny legs).
    A point with a None metric cannot certify feasibility."""
    feas = {}
    for cell in CELLS:
        feas[cell] = [th for th in THETAS
                      if table[(cell, th)][0] is not None
                      and table[(cell, th)][1] is not None
                      and table[(cell, th)][0] <= T_MAX
                      and table[(cell, th)][1] <= O95_MAX]
    empty = [cell for cell in CELLS if not feas[cell]]
    coverage = {th: sum(1 for cell in CELLS if th in feas[cell]) for th in THETAS}
    dagger = [th for th in THETAS if coverage[th] >= APPROVE_CELLS]
    if dagger:
        pattern = "APPROVE"
        theta_dagger = min(dagger)
    elif len(empty) >= REJECT_CELLS:
        pattern = "REJECT"
        theta_dagger = None
    else:
        pattern = "NULL"
        theta_dagger = None
    theta_star = {cell: (min(feas[cell]) if feas[cell] else None) for cell in CELLS}
    per_regime = {}
    for rn, _, _, _ in REGIMES:
        cs = [c for c in CELLS if c[0] == rn]
        per_regime[rn] = {
            "feasible_share": "%d/3" % sum(1 for c in cs if feas[c]),
            "median_theta_star": median([theta_star[c] for c in cs if theta_star[c] is not None]),
        }
    per_col = {}
    for cn, _ in COLS:
        cs = [c for c in CELLS if c[1] == cn]
        per_col[cn] = {
            "feasible_share": "%d/3" % sum(1 for c in cs if feas[c]),
            "median_theta_star": median([theta_star[c] for c in cs if theta_star[c] is not None]),
        }
    return {
        "feas": {"%s-%s" % c: feas[c] for c in CELLS},
        "theta_star": {"%s-%s" % c: theta_star[c] for c in CELLS},
        "infeasible_cells": ["%s-%s" % c for c in empty],
        "infeasible_count": len(empty),
        "coverage_per_theta": {str(th): coverage[th] for th in THETAS},
        "theta_dagger": theta_dagger,
        "pattern_ruling": pattern,
        "per_regime": per_regime,
        "per_check_rate": per_col,
    }


def main():
    # --- Arm A ------------------------------------------------------------
    arm_a = {}
    for rn, w, m, big_m in REGIMES:
        for cn, lam in COLS:
            prev_t = None
            prev_o = None
            for th in THETAS:
                t_a = t_closed(w, m, big_m, lam, th)
                o_a = o95_closed(lam, th)
                check(0.0 <= t_a <= 1.0, "T_A in [0,1]")
                if prev_t is not None:
                    check(t_a <= prev_t, "T_A monotone decreasing in theta")
                    check(o_a > prev_o, "O95_A monotone increasing in theta")
                prev_t, prev_o = t_a, o_a
                arm_a[((rn, cn), th)] = (t_a, o_a)
    # hand pins (fixtures-committed derivations)
    pins = {p["name"]: p for p in FX["hand_derived_pins"]}
    p1 = pins["pin_1_T_A_R1_C4_theta12"]
    check(abs(t_closed((0.9, 0.1), (1.5, 12.0), 6, 0.25, 12.0)
              - p1["expected"]["T_A"]) <= p1["tolerance"], "pin 1 T_A")
    p2 = pins["pin_2_O95_A_C12_theta24"]
    check(abs(o95_closed(1.0 / 12.0, 24.0) - p2["expected"]["O95_A"]) <= p2["tolerance"],
          "pin 2 O95_A")
    p3 = pins["pin_3_C48_structural_infeasibility"]
    check(abs(math.log(20.0) * 48.0 - p3["expected"]["ln20_times_48"]) <= p3["tolerance"],
          "pin 3 constant")
    check(all(o95_closed(1.0 / 48.0, th) > O95_MAX for th in THETAS),
          "pin 3 C48 column O95-infeasible at every theta")
    # theta -> infinity closed-form identity: T_A(1e9) == 0.0 exactly (exp underflow)
    for rn, w, m, big_m in REGIMES:
        for cn, lam in COLS:
            check(t_closed(w, m, big_m, lam, 1e9) == 0.0, "T_A(theta->inf) == 0 exactly")

    a_decision = decide(arm_a)

    # --- Arm S main leg (seed 20260744) ------------------------------------
    print("[arm S] main leg", file=sys.stderr)
    st = Stream(SEED_MAIN)
    arm_s_pts = {}
    for rn, w, m, big_m in REGIMES:
        for cn, lam in COLS:
            for th in THETAS:
                arm_s_pts[((rn, cn), th)] = run_point(st, w, m, big_m, lam, th, P_D, M_S)
            print("[arm S] %s-%s done" % (rn, cn), file=sys.stderr)
    check(st.sentinel_ok(), "main leg draw-count sentinel")
    main_draws = st.n

    # gates + predicted SEs
    gate_rows = {}
    failing = []
    t_fail = o_fail = 0
    for key in sorted(arm_s_pts, key=lambda k: (k[0][0], k[0][1], k[1])):
        (cell, th) = key
        t_a, o_a = arm_a[key]
        pt = arm_s_pts[key]
        t_s, o_s = pt["T_S"], pt["O95_S"]
        dt = abs(t_s - t_a)
        do = abs(o_s - o_a)
        tol_o = max(GATE_O_ABS, GATE_O_REL * o_a)
        t_ok = dt <= GATE_T + 1e-12
        o_ok = do <= tol_o + 1e-9
        lam = dict(COLS)[cell[1]]
        se_t = math.sqrt(t_a * (1.0 - t_a) / pt["alive"]) if pt["alive"] else None
        se_o = (math.sqrt(0.95 * 0.05 / pt["dead"]) / (0.05 * lam)) if pt["dead"] else None
        gate_rows["%s-%s@%g" % (cell[0], cell[1], th)] = {
            "T_A": t_a, "T_S": t_s, "dT_pp": dt * 100.0, "T_gate_ok": t_ok,
            "SE_T_pp": (se_t * 100.0 if se_t else None),
            "z_T": (dt / se_t if se_t else None),
            "O95_A": o_a, "O95_S": o_s, "dO95_h": do, "O95_tol_h": tol_o,
            "O95_gate_ok": o_ok,
            "SE_O95_h": se_o, "z_O95": (do / se_o if se_o else None),
            "n_alive": pt["alive"], "n_dead": pt["dead"],
        }
        if not t_ok:
            t_fail += 1
        if not o_ok:
            o_fail += 1
        if not (t_ok and o_ok):
            failing.append(key)
    gates_all_pass = t_fail == 0 and o_fail == 0

    arm_s_table = {k: (v["T_S"], v["O95_S"]) for k, v in arm_s_pts.items()}
    s_decision = decide(arm_s_table)

    # --- stability leg (seed 20260745) --------------------------------------
    print("[arm S] stability leg", file=sys.stderr)
    st2 = Stream(SEED_STAB)
    stab_table = {}
    for rn, w, m, big_m in REGIMES:
        for cn, lam in COLS:
            for th in THETAS:
                pt = run_point(st2, w, m, big_m, lam, th, P_D, M_STAB)
                stab_table[((rn, cn), th)] = (pt["T_S"], pt["O95_S"])
    check(st2.sentinel_ok(), "stability leg draw-count sentinel")
    stab_decision = decide(stab_table)
    stability_reproduced = stab_decision["pattern_ruling"] == a_decision["pattern_ruling"]

    # --- reporting-only legs (seed 20260746, sequential) --------------------
    print("[reporting] p_d legs + chains", file=sys.stderr)
    st3 = Stream(SEED_REP)
    rep = {}
    for pd_leg in (0.02, 0.30, 0.10):
        leg = {}
        for rn, w, m, big_m in REGIMES:
            for cn, lam in COLS:
                for th in THETAS:
                    pt = run_point(st3, w, m, big_m, lam, th, pd_leg, M_REP)
                    leg["%s-%s@%g" % (rn, cn, th)] = {
                        "T_S": pt["T_S"], "O95_S": pt["O95_S"],
                        "n_alive": pt["alive"], "n_dead": pt["dead"],
                        "multi_steal_hist_0_1_2_3plus": pt["multi_steal_hist"],
                        "wasted_sessions": pt["stolen"],
                    }
        rep["p_d=%s" % pd_leg] = leg
    chains = {}
    for rn, w, m, big_m in REGIMES:
        for cn, lam in COLS:
            for th in THETAS:
                done = []
                lanes_tot = 0
                wasted_tot = 0
                for _ in range(M_REP):
                    ttd, lanes, wasted = sim_chain(st3, w, m, big_m, lam, th, P_D)
                    done.append(ttd)
                    lanes_tot += lanes
                    wasted_tot += wasted
                chains["%s-%s@%g" % (rn, cn, th)] = {
                    "mean_time_to_done_h": sum(done) / len(done),
                    "p95_time_to_done_h": p95(done),
                    "mean_chain_length": lanes_tot / M_REP,
                    "false_takeovers_on_alive_segments": wasted_tot,
                }
    check(st3.sentinel_ok(), "reporting legs draw-count sentinel")

    # --- aux stream (seed 20260747): A1, A2, then A3 diagnostics ------------
    print("[aux] A1/A2 identity legs", file=sys.stderr)
    st4 = Stream(SEED_AUX)
    orphan_events = 0
    for rn, w, m, big_m in REGIMES:
        for cn, lam in COLS:
            pt = run_point(st4, w, m, big_m, lam, 24.0, 0.0, M_AUX)
            orphan_events += pt["dead"]
    check(orphan_events == 0, "aux A1: p_d=0 leg produced zero orphan events")
    a2_steals = 0
    a2_takeovers = 0
    for rn, w, m, big_m in REGIMES:
        for cn, lam in COLS:
            for _ in range(M_AUX):
                kind, val = sim_claim(st4, w, m, big_m, lam, math.inf, P_D)
                if kind == "alive" and val >= 1:
                    a2_steals += 1
                if kind == "dead":
                    a2_takeovers += 1
    check(a2_steals == 0, "aux A2: theta->inf leg produced T = 0 exactly")
    check(a2_takeovers == 0, "aux A2: theta->inf leg produced no takeovers")
    print("[aux] A3 gate diagnostics (%d failing points)" % len(failing), file=sys.stderr)
    diagnostics = {}
    for key in sorted(failing, key=lambda k: (k[0][0], k[0][1], k[1])):
        (cell, th) = key
        rn, cn = cell
        w, m, big_m = next((wr, mr, Mr) for (n2, wr, mr, Mr) in REGIMES if n2 == rn)
        lam = dict(COLS)[cn]
        pt = run_point(st4, w, m, big_m, lam, th, P_D, M_DIAG)
        t_a, o_a = arm_a[key]
        dt = abs(pt["T_S"] - t_a)
        do = abs(pt["O95_S"] - o_a)
        tol_o = max(GATE_O_ABS, GATE_O_REL * o_a)
        diagnostics["%s-%s@%g" % (rn, cn, th)] = {
            "M_diag": M_DIAG,
            "T_S_16x": pt["T_S"], "dT_pp_16x": dt * 100.0,
            "T_within_tol_at_16x": dt <= GATE_T + 1e-12,
            "O95_S_16x": pt["O95_S"], "dO95_h_16x": do,
            "O95_within_tol_at_16x": do <= tol_o + 1e-9,
        }
    check(st4.sentinel_ok(), "aux stream draw-count sentinel")
    diag_all_within = all(
        d["T_within_tol_at_16x"] and d["O95_within_tol_at_16x"]
        for d in diagnostics.values()) if diagnostics else True

    # --- final ruling (registered evaluation order; fixtures
    #     gate_calibration_disclosure item 3) --------------------------------
    pattern = a_decision["pattern_ruling"]
    if pattern == "APPROVE" and not (gates_all_pass and stability_reproduced):
        # APPROVE alone conditions on gates + stability (registered text);
        # re-evaluate the remaining order without the APPROVE branch.
        pattern = ("REJECT" if a_decision["infeasible_count"] >= REJECT_CELLS
                   else "NULL")
        ruling_label = pattern + " (APPROVE barred by gate/stability condition)"
    else:
        ruling_label = pattern
    ruling = pattern

    out = {
        "proposal": FX["source"]["proposal"],
        "arm_A": {
            "table": {"%s-%s@%g" % (c[0], c[1], th): {"T_A": arm_a[(c, th)][0],
                                                      "O95_A": arm_a[(c, th)][1]}
                      for c in CELLS for th in THETAS},
            "decision": a_decision,
        },
        "arm_S_main": {
            "seed": SEED_MAIN, "M_S": M_S, "draws": main_draws,
            "table": {"%s-%s@%g" % (c[0], c[1], th): {
                "T_S": arm_s_pts[(c, th)]["T_S"],
                "O95_S": arm_s_pts[(c, th)]["O95_S"],
                "n_alive": arm_s_pts[(c, th)]["alive"],
                "n_dead": arm_s_pts[(c, th)]["dead"]}
                for c in CELLS for th in THETAS},
            "decision_on_MC_values": s_decision,
        },
        "gates": {
            "registered": "|T_S - T_A| <= 1.0 pp AND |O95_S - O95_A| <= max(4 h, 5% of O95_A), every point",
            "per_point": gate_rows,
            "T_gate_failures": t_fail,
            "O95_gate_failures": o_fail,
            "all_pass": gates_all_pass,
            "calibration_note": FX["gate_calibration_disclosure"]["arithmetic"],
        },
        "stability_leg": {
            "seed": SEED_STAB, "M_S": M_STAB,
            "decision": stab_decision,
            "reproduces_main_ruling": stability_reproduced,
        },
        "reporting_only": {
            "p_d_sensitivity_and_multi_steal": rep,
            "takeover_chains": chains,
            "note": "registered as unable to flip the decision",
        },
        "aux": {
            "A1_pd0_orphan_events": orphan_events,
            "A2_theta_inf_steals": a2_steals,
            "A3_gate_diagnostics_16x": diagnostics,
            "A3_all_failing_points_within_tolerance_at_16x": diag_all_within,
        },
        "ruling": ruling,
        "ruling_label": ruling_label,
        "theta_dagger": a_decision["theta_dagger"],
        "planted_constant_readings": {
            "WORK_CLAIM_STALE_HOURS_72": {
                "feasible_in_cells": [c for c, f in a_decision["feas"].items() if 72.0 in f],
                "coverage": a_decision["coverage_per_theta"]["72.0"],
            },
            "CLAIM_STALE_HOURS_24_order_class_reading": {
                "feasible_in_cells": [c for c, f in a_decision["feas"].items() if 24.0 in f],
                "coverage": a_decision["coverage_per_theta"]["24.0"],
                "note": "read against the burst-regime columns per the registered boundary (reading, not sweep)",
            },
        },
        "model_basis": FX["boundaries_registered"]["model_basis"],
        "self_checks_passed": None,
    }

    # Headline stdout (deterministic).
    print("verdict-027 claim-expiry — results")
    print("arm A (exact): Feas per cell:")
    for c in CELLS:
        key = "%s-%s" % c
        print("  %s: Feas=%s theta*=%s" % (key, a_decision["feas"][key],
                                           a_decision["theta_star"][key]))
    print("arm A: infeasible cells %d/9: %s" % (a_decision["infeasible_count"],
                                                a_decision["infeasible_cells"]))
    print("arm A: coverage per theta: %s" % a_decision["coverage_per_theta"])
    print("arm A: theta-dagger: %s (APPROVE needs coverage >= 8/9)" % a_decision["theta_dagger"])
    print("arm S main: T gate failures %d/54, O95 gate failures %d/54, all_pass=%s"
          % (t_fail, o_fail, gates_all_pass))
    print("arm S main: decision on MC values: %s (infeasible %d/9)"
          % (s_decision["pattern_ruling"], s_decision["infeasible_count"]))
    print("stability leg: %s (reproduces main: %s)"
          % (stab_decision["pattern_ruling"], stability_reproduced))
    print("aux A1 orphan events (p_d=0): %d ; aux A2 steals (theta=inf): %d"
          % (orphan_events, a2_steals))
    print("aux A3: failing points re-measured at 16x: %d ; all within tolerance at 16x: %s"
          % (len(diagnostics), diag_all_within))
    print("RULING: %s" % ruling_label)

    out["self_checks_passed"] = CHECKS + 1  # + the final write-side check below
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    check(out["ruling"] in ("APPROVE", "REJECT", "NULL"), "ruling well-formed")
    print("SELF-CHECKS: %d passed, 0 failed" % CHECKS)


if __name__ == "__main__":
    main()
