#!/usr/bin/env python3
"""VERDICT 021 — backlog low-water signal threshold (idea-engine PROPOSAL 019).

Pre-registered reorder-point sim for never-idle lane backlogs. Fully hermetic:
stdlib only, no network, no git, no wall clock, no hash(); the only file read
is the committed pre-registration (fixtures.json, same directory), and the
runner cross-checks its own literals against it at start. Deterministic:
the only randomness is random.Random(<pinned seed>) consumed in the pinned
loop order; stdout and results.json are byte-identical across process runs.

Run: python3 sims/verdict-021-backlog-low-water/backlog_low_water_sim.py
Exit 0 iff every self-check passes.
"""

import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Pinned constants (cross-checked against the committed fixtures.json below).
# ---------------------------------------------------------------------------
H_PRIMARY = 2000
B0_PRIMARY = 6
R_PRIMARY = 4
PC_GRID = (0.6, 1.0)
N_GRID = (0, 1, 2, 3, 4, 6)
L_GRID = (1, 2, 4)
M_PRIMARY = 300
SEED_PRIMARY = 20260719
SEED_STABILITY = 20260720
M_STABILITY = 50
M_SENS = 50
SEED_SENS = 20260719

REGIMES = (
    ("A1", 0.30, (1, 2, 3)),
    ("A2", 0.10, (2, 4, 5, 11)),
    ("A3", 0.05, (2, 3, 4)),
)

D_MAX = Fraction(1, 20)          # dry-wake band: D <= 0.05
S_MAX = Fraction(25, 1)          # alarm band: S <= 25 signals per 100 wakes
DD_APPROVE_MIN = Fraction(1, 10)  # median dD >= 0.10
SHARE_80 = Fraction(4, 5)
SHARE_50 = Fraction(1, 2)
N_STAR_CANDIDATES = (1, 2, 3, 4, 6)

SENS_LEGS = (
    ("sens-R2", {"R": 2}),
    ("sens-R8", {"R": 8}),
    ("sens-b3", {"b0": 3}),
    ("sens-b12", {"b0": 12}),
    ("sens-H500", {"H": 500}),
)

CHECKS = {"passed": 0, "failed": 0}
FAILURES = []


def check(cond, label):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        FAILURES.append(label)


# ---------------------------------------------------------------------------
# The pinned wake loop (primary implementation).
# ---------------------------------------------------------------------------
def run_rep(rng, H, b0, R, pc, q, batches, N, L, trace=None):
    """One replication. Returns (dry, demand, consumed, signals, landed,
    arrived, fires, final_b, sum_b, min_gap). Pinned per-wake order:
    (1) due replenishment lands; (2) consumption; (3) organic arrival;
    (4) signal policy (one outstanding). Draw order per wake: consumption,
    arrival-fire, batch-size (batch drawn only when the arrival fires)."""
    b = b0
    due = 0  # wake index at which the in-flight replenishment lands; 0 = none
    dry = demand = consumed = 0
    signals = landed = arrived = fires = 0
    sum_b = 0
    last_sig = 0
    min_gap = 0  # 0 = fewer than two signals
    rnd = rng.random
    rrange = rng.randrange
    nb = len(batches)
    tr = trace
    for t in range(1, H + 1):
        # (1) landing
        if due == t:
            b += R
            landed += 1
            due = 0
        # (2) consumption
        d = rnd()
        if tr is not None:
            tr.append(("c", d))
        if d < pc:
            demand += 1
            if b > 0:
                b -= 1
                consumed += 1
            else:
                dry += 1
        # (3) organic arrival
        a = rnd()
        if tr is not None:
            tr.append(("a", a))
        if a < q:
            fires += 1
            gi = rrange(nb)
            if tr is not None:
                tr.append(("g", gi))
            g = batches[gi]
            b += g
            arrived += g
        # (4) signal policy
        if N > 0 and b <= N and due == 0:
            signals += 1
            due = t + L
            if last_sig:
                gap = t - last_sig
                if min_gap == 0 or gap < min_gap:
                    min_gap = gap
            last_sig = t
        sum_b += b
    return dry, demand, consumed, signals, landed, arrived, fires, b, sum_b, min_gap


# ---------------------------------------------------------------------------
# Independent re-implementation (validity check): replays a recorded draw
# trace through a differently-structured simulator (dict state, pending-
# replenishment list, no early exits) and must agree exactly.
# ---------------------------------------------------------------------------
def replay_independent(trace, H, b0, R, pc, q, batches, N, L):
    state = {"backlog": b0, "pending": [], "dry": 0, "demand": 0,
             "signals": 0, "landed": 0, "sum_b": 0}
    pos = 0
    for wake in range(1, H + 1):
        landing_now = [p for p in state["pending"] if p == wake]
        for _ in landing_now:
            state["backlog"] += R
            state["landed"] += 1
        state["pending"] = [p for p in state["pending"] if p != wake]
        kind, val = trace[pos]
        pos += 1
        assert kind == "c"
        if val < pc:
            state["demand"] += 1
            if state["backlog"] == 0:
                state["dry"] += 1
            else:
                state["backlog"] = state["backlog"] - 1
        kind, val = trace[pos]
        pos += 1
        assert kind == "a"
        if val < q:
            kind, gi = trace[pos]
            pos += 1
            assert kind == "g"
            state["backlog"] += batches[gi]
        outstanding = len([p for p in state["pending"] if p > wake]) > 0
        if N != 0 and state["backlog"] <= N and not outstanding:
            state["signals"] += 1
            state["pending"].append(wake + L)
        state["sum_b"] += state["backlog"]
    return (state["dry"], state["demand"], state["signals"], state["landed"],
            state["backlog"], state["sum_b"], pos)


# ---------------------------------------------------------------------------
# Leg runner: full 18-cell x 6-N grid, one shared RNG stream, pinned order.
# ---------------------------------------------------------------------------
def cells_lexicographic():
    out = []
    for rid, q, batches in REGIMES:
        for pc in PC_GRID:
            for L in L_GRID:
                out.append((rid, q, batches, pc, L))
    return out


def cell_key(rid, pc, L):
    return "%s|pc%.1f|L%d" % (rid, pc, L)


def run_leg(leg_id, seed, M, H, b0, R, trace_stride=0):
    rng = random.Random(seed)
    first_draws = None
    total_draws = 0
    total_fires = 0
    results = {}
    traces_checked = 0
    pair_index = 0
    for (rid, q, batches, pc, L) in cells_lexicographic():
        ck = cell_key(rid, pc, L)
        per_n = {}
        for N in N_GRID:
            dry = demand = signals = 0
            sum_b_total = 0
            take_trace = trace_stride and (pair_index % trace_stride == 0)
            for rep in range(M):
                trace = [] if (take_trace and rep == 0) else None
                out = run_rep(rng, H, b0, R, pc, q, batches, N, L, trace)
                (d_dry, d_dem, d_con, d_sig, d_land, d_arr, d_fires,
                 d_fb, d_sb, d_gap) = out
                if first_draws is None and trace is not None:
                    first_draws = [trace[0][1], trace[1][1]]
                total_draws += 2 * H + d_fires
                total_fires += d_fires
                # --- per-rep self-checks (validity gate: conservation etc.)
                check(d_fb == b0 + d_land * R + d_arr - d_con,
                      "conservation %s N=%d rep=%d leg=%s" % (ck, N, rep, leg_id))
                check(d_dry + d_con == d_dem,
                      "dry+consumed==demand %s N=%d rep=%d leg=%s" % (ck, N, rep, leg_id))
                check(d_fb >= 0, "backlog>=0 %s N=%d rep=%d" % (ck, N, rep))
                check(d_land <= d_sig,
                      "landed<=signals %s N=%d rep=%d" % (ck, N, rep))
                if pc == 1.0:
                    check(d_dem == H, "pc=1 demand==H %s N=%d rep=%d" % (ck, N, rep))
                if N == 0:
                    check(d_sig == 0, "N=0 no signals %s rep=%d" % (ck, rep))
                else:
                    check(d_sig <= 1 + (H - 1) // L,
                          "signal count bound %s N=%d rep=%d" % (ck, N, rep))
                    check(d_gap == 0 or d_gap >= L,
                          "signal spacing >= L %s N=%d rep=%d" % (ck, N, rep))
                if trace is not None:
                    ind = replay_independent(trace, H, b0, R, pc, q, batches, N, L)
                    check(ind == (d_dry, d_dem, d_sig, d_land, d_fb, d_sb, len(trace)),
                          "independent replay %s N=%d leg=%s" % (ck, N, leg_id))
                    traces_checked += 1
                dry += d_dry
                demand += d_dem
                signals += d_sig
                sum_b_total += d_sb
            wakes = M * H
            D = Fraction(dry, demand) if demand else None
            check(demand > 0, "demand>0 %s N=%d leg=%s" % (ck, N, leg_id))
            S = Fraction(signals * 100, wakes)
            mean_b = Fraction(sum_b_total, wakes)
            per_n[N] = {"dry": dry, "demand": demand, "signals": signals,
                        "D": D, "S": S, "mean_b": mean_b}
            pair_index += 1
        results[ck] = per_n
    # RNG seeding + draw-count accounting
    fresh = random.Random(seed)
    if first_draws is not None:
        check(fresh.random() == first_draws[0] and fresh.random() == first_draws[1],
              "fresh Random(seed) reproduces the first draws leg=%s" % leg_id)
    n_pairs = len(results) * len(N_GRID)
    check(total_draws == 2 * H * M * n_pairs + total_fires,
          "draw-count accounting leg=%s" % leg_id)
    return results, traces_checked


# ---------------------------------------------------------------------------
# Decision rule (pre-registered; exact Fractions, evaluated in pinned order).
# ---------------------------------------------------------------------------
def median_fracs(vals):
    vs = sorted(vals)
    n = len(vs)
    if n == 0:
        return None
    if n % 2 == 1:
        return vs[n // 2]
    return (vs[n // 2 - 1] + vs[n // 2]) / 2


def decide(leg):
    cells = list(leg.keys())
    n_cells = len(cells)
    d0_pass = [c for c in cells if leg[c][0]["D"] <= D_MAX]
    n_star = {}
    dd = {}
    for c in cells:
        star = None
        for N in N_STAR_CANDIDATES:
            if leg[c][N]["D"] <= D_MAX and leg[c][N]["S"] <= S_MAX:
                star = N
                break
        n_star[c] = star
        if star is not None:
            dd[c] = leg[c][0]["D"] - leg[c][star]["D"]
    exists = [c for c in cells if n_star[c] is not None]
    med_dd = median_fracs(list(dd.values()))
    med_star = median_fracs([Fraction(n_star[c]) for c in exists])
    # evaluation order: REJECT-a, APPROVE, REJECT-b, NULL
    if Fraction(len(d0_pass), n_cells) >= SHARE_80:
        ruling = "REJECT-a"
    elif (Fraction(len(exists), n_cells) >= SHARE_80
          and med_dd is not None and med_dd >= DD_APPROVE_MIN):
        ruling = "APPROVE"
    elif Fraction(len(exists), n_cells) < SHARE_50:
        ruling = "REJECT-b"
    else:
        ruling = "NULL"
    within = None
    if med_star is not None:
        within = abs(Fraction(3) - med_star) <= 1
    # per-axis N*-exists shares + median dD (for the NULL axis-naming duty,
    # reported on every outcome)
    axes = {}
    axis_defs = (
        ("regime", lambda c: c.split("|")[0], ["A1", "A2", "A3"]),
        ("p_c", lambda c: c.split("|")[1], ["pc0.6", "pc1.0"]),
        ("L", lambda c: c.split("|")[2], ["L1", "L2", "L4"]),
    )
    for aname, keyf, values in axis_defs:
        per_val = {}
        shares = []
        for v in values:
            sub = [c for c in cells if keyf(c) == v]
            sub_exists = [c for c in sub if n_star[c] is not None]
            share = Fraction(len(sub_exists), len(sub))
            sub_dd = median_fracs([dd[c] for c in sub_exists if c in dd])
            per_val[v] = {"exists_share": share, "median_dd": sub_dd,
                          "n_star_values": sorted(
                              n_star[c] for c in sub_exists)}
            shares.append(share)
        per_val["_spread"] = max(shares) - min(shares)
        axes[aname] = per_val
    return {"ruling": ruling, "d0_pass_cells": sorted(d0_pass),
            "d0_pass_count": len(d0_pass), "n_cells": n_cells,
            "n_star": n_star, "dd": dd, "exists_count": len(exists),
            "median_dd": med_dd, "grid_median_n_star": med_star,
            "three_within_pm1": within, "axes": axes}


def decide_independent(leg):
    """Second, independently-written decision evaluator (percent integers on
    pooled counts, string flow) — must agree with decide() on the ruling,
    the per-cell N* map, and the headline medians."""
    stars = {}
    deltas = {}
    d0_ok = 0
    for ck in leg:
        row0 = leg[ck][0]
        # D <= 0.05  <=>  20*dry <= demand
        if 20 * row0["dry"] <= row0["demand"]:
            d0_ok += 1
        found = "none"
        for cand in (1, 2, 3, 4, 6):
            r = leg[ck][cand]
            ok_d = 20 * r["dry"] <= r["demand"]
            ok_s = r["S"] <= 25  # S is the exact pooled Fraction, signals*100/(M*H)
            if ok_d and ok_s:
                found = cand
                break
        stars[ck] = found
        if found != "none":
            rs = leg[ck][found]
            deltas[ck] = (Fraction(row0["dry"], row0["demand"])
                          - Fraction(rs["dry"], rs["demand"]))
    n = len(leg)
    exists = sum(1 for v in stars.values() if v != "none")
    med = median_fracs(list(deltas.values()))
    if d0_ok * 5 >= n * 4:
        ruling = "REJECT-a"
    elif exists * 5 >= n * 4 and med is not None and med * 10 >= 1:
        ruling = "APPROVE"
    elif exists * 2 < n:
        ruling = "REJECT-b"
    else:
        ruling = "NULL"
    med_star = median_fracs([Fraction(v) for v in stars.values() if v != "none"])
    return ruling, stars, med, med_star


# ---------------------------------------------------------------------------
# Fixture cross-check.
# ---------------------------------------------------------------------------
def cross_check_fixtures():
    with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as f:
        fx = json.load(f)
    c = fx["constants"]
    check(c["H"] == H_PRIMARY, "fixture H")
    check(c["b0"] == B0_PRIMARY, "fixture b0")
    check(c["R"] == R_PRIMARY, "fixture R")
    check(tuple(c["p_c_grid"]) == PC_GRID, "fixture p_c grid")
    check(tuple(c["N_grid"]) == N_GRID, "fixture N grid")
    check(tuple(c["L_grid"]) == L_GRID, "fixture L grid")
    check(c["M"] == M_PRIMARY, "fixture M")
    check(c["seed_primary"] == SEED_PRIMARY, "fixture primary seed")
    check(c["seed_stability"] == SEED_STABILITY, "fixture stability seed")
    for rid, q, batches in REGIMES:
        r = c["regimes"][rid]
        check(r["q"] == q, "fixture %s q" % rid)
        check(tuple(r["batches"]) == batches, "fixture %s batches" % rid)
        mean = Fraction(str(r["mean_inflow_per_wake"]))
        got = Fraction(str(q)) * Fraction(sum(batches), len(batches))
        check(mean == got, "fixture %s mean inflow" % rid)
    b = fx["band_constants"]
    check(Fraction(b["D_MAX"]) == D_MAX, "fixture D_MAX")
    check(Fraction(b["S_MAX_PER_100"]) == S_MAX, "fixture S_MAX")
    check(Fraction(b["DELTA_D_APPROVE_MIN"]) == DD_APPROVE_MIN, "fixture dD min")
    check(Fraction(b["REJECT_A_CELL_SHARE"]) == SHARE_80, "fixture 80% share (a)")
    check(Fraction(b["APPROVE_EXISTS_SHARE"]) == SHARE_80, "fixture 80% share (approve)")
    check(Fraction(b["REJECT_B_EXISTS_SHARE"]) == SHARE_50, "fixture 50% share (b)")
    sl = fx["sensitivity_legs"]
    check(sl["sens_M"] == M_SENS, "fixture sens M")
    check(sl["sens_seed"] == SEED_SENS, "fixture sens seed")
    check(sl["stability_leg"]["M"] == M_STABILITY, "fixture stability M")
    got_legs = tuple((l["id"], tuple(sorted(l["override"].items())))
                     for l in sl["legs"])
    want_legs = tuple((lid, tuple(sorted(ov.items()))) for lid, ov in SENS_LEGS)
    check(got_legs == want_legs, "fixture sensitivity leg set")
    check(fx["cpython_pin"] == "3.11", "fixture cpython pin")
    check(sys.version_info[:2] == (3, 11), "running on pinned cpython 3.11")
    return fx


def run_hand_pins(fx):
    for name in ("HAND-1", "HAND-2"):
        pin = fx["hand_pins"][name]
        p = pin["params"]
        rng = random.Random(0)  # q=0 and p_c=1.0: draws exist but decide nothing
        out = run_rep(rng, p["H"], p["b0"], p["R"], p["p_c"], p["q"],
                      (1,), p["N"], p["L"])
        dry, demand, consumed, signals, landed, arrived, fires, fb, sb, gap = out
        e = pin["expect"]
        check(demand == e["demand"], "%s demand" % name)
        check(dry == e["dry"], "%s dry" % name)
        check(signals == e["signals"], "%s signals" % name)
        check(landed == e["landed"], "%s landed" % name)
        check(fb == e["final_b"], "%s final backlog" % name)
        check(sb == e["sum_b"], "%s sum backlog" % name)
        check(fires == 0 and arrived == 0, "%s no arrivals at q=0" % name)
    # HAND-2 exercises the tight spacing bound: gap == L exactly
    p = fx["hand_pins"]["HAND-2"]["params"]
    out = run_rep(random.Random(0), p["H"], p["b0"], p["R"], p["p_c"], p["q"],
                  (1,), p["N"], p["L"])
    check(out[9] == p["L"], "HAND-2 signal gap == L (bound tight)")


# ---------------------------------------------------------------------------
# Serialization helpers (deterministic).
# ---------------------------------------------------------------------------
def frac_str(fr):
    if fr is None:
        return None
    return "%d/%d" % (fr.numerator, fr.denominator)


def f6(fr):
    if fr is None:
        return None
    return round(fr.numerator / fr.denominator, 6)


def leg_table(leg, full=False):
    out = {}
    for ck in sorted(leg.keys()):
        row = {}
        for N in N_GRID:
            r = leg[ck][N]
            if full:
                row[str(N)] = {
                    "D": frac_str(r["D"]), "D_f": f6(r["D"]),
                    "S": frac_str(r["S"]), "S_f": f6(r["S"]),
                    "mean_b_f": f6(r["mean_b"]),
                    "dry": r["dry"], "demand": r["demand"],
                    "signals": r["signals"],
                }
            else:
                row[str(N)] = [f6(r["D"]), f6(r["S"]), f6(r["mean_b"])]
        out[ck] = row
    return out


def decision_block(dec):
    axes = {}
    for aname, per_val in dec["axes"].items():
        block = {}
        for k, v in per_val.items():
            if k == "_spread":
                block["spread"] = f6(v)
            else:
                block[k] = {"exists_share": frac_str(v["exists_share"]),
                            "exists_share_f": f6(v["exists_share"]),
                            "median_dd_f": f6(v["median_dd"]),
                            "n_star_values": v["n_star_values"]}
        axes[aname] = block
    return {
        "ruling": dec["ruling"],
        "d0_pass_count": dec["d0_pass_count"],
        "d0_pass_cells": dec["d0_pass_cells"],
        "n_cells": dec["n_cells"],
        "n_star_per_cell": {c: dec["n_star"][c] for c in sorted(dec["n_star"])},
        "n_star_exists_count": dec["exists_count"],
        "dd_per_cell_f": {c: f6(dec["dd"][c]) for c in sorted(dec["dd"])},
        "median_dd": frac_str(dec["median_dd"]),
        "median_dd_f": f6(dec["median_dd"]),
        "grid_median_n_star": frac_str(dec["grid_median_n_star"]),
        "grid_median_n_star_f": f6(dec["grid_median_n_star"]),
        "bullet_tilde3_within_pm1": dec["three_within_pm1"],
        "axes": axes,
    }


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main():
    fx = cross_check_fixtures()
    run_hand_pins(fx)

    legs_out = {}
    decisions = {}

    # primary decision leg
    primary, traced = run_leg("primary", SEED_PRIMARY, M_PRIMARY,
                              H_PRIMARY, B0_PRIMARY, R_PRIMARY, trace_stride=7)
    check(traced == 16, "primary trace coverage (16 strided (cell,N) pairs)")
    dec = decide(primary)
    ind_ruling, ind_stars, ind_med, ind_med_star = decide_independent(primary)
    check(ind_ruling == dec["ruling"], "independent decision: ruling agrees")
    check(all((ind_stars[c] == "none") == (dec["n_star"][c] is None)
              and (ind_stars[c] == "none" or ind_stars[c] == dec["n_star"][c])
              for c in ind_stars), "independent decision: N* map agrees")
    check(ind_med == dec["median_dd"], "independent decision: median dD agrees")
    check(ind_med_star == dec["grid_median_n_star"],
          "independent decision: grid-median N* agrees")
    legs_out["primary"] = leg_table(primary, full=True)
    decisions["primary"] = decision_block(dec)

    # stability leg (must reproduce the ruling — done-when)
    stab, traced_s = run_leg("stability", SEED_STABILITY, M_STABILITY,
                             H_PRIMARY, B0_PRIMARY, R_PRIMARY, trace_stride=7)
    check(traced_s == 16, "stability trace coverage")
    dec_stab = decide(stab)
    check(dec_stab["ruling"] == dec["ruling"],
          "stability leg (M=50, seed 20260720) reproduces the ruling")
    legs_out["stability"] = leg_table(stab)
    decisions["stability"] = decision_block(dec_stab)

    # sensitivity legs (reporting-only; scored under the same rule for report)
    for lid, ov in SENS_LEGS:
        H = ov.get("H", H_PRIMARY)
        b0 = ov.get("b0", B0_PRIMARY)
        R = ov.get("R", R_PRIMARY)
        leg, traced_l = run_leg(lid, SEED_SENS, M_SENS, H, b0, R, trace_stride=7)
        check(traced_l == 16, "%s trace coverage" % lid)
        legs_out[lid] = leg_table(leg)
        decisions[lid] = decision_block(decide(leg))

    ok = CHECKS["failed"] == 0
    results = {
        "sim": "verdict-021-backlog-low-water",
        "proposal": "idea-engine control/outbox.md PROPOSAL 019 · 2026-07-13T01:34:28Z · status: sim-ready",
        "python": "%d.%d" % sys.version_info[:2],
        "ruling": dec["ruling"],
        "decision_detail": decisions,
        "tables": legs_out,
        "self_checks": {"passed": CHECKS["passed"], "failed": CHECKS["failed"]},
        "failures": FAILURES[:50],
    }
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, sort_keys=True)
        f.write("\n")

    p = decisions["primary"]
    print("VERDICT-021 backlog low-water signal — PROPOSAL 019")
    print("ruling: %s" % dec["ruling"])
    print("D(0)<=0.05 cells: %d/%d (REJECT-a needs >=80%%: %s)"
          % (p["d0_pass_count"], p["n_cells"],
             "yes" if Fraction(p["d0_pass_count"], p["n_cells"]) >= SHARE_80 else "no"))
    print("N* exists: %d/%d cells; per-cell N*: %s"
          % (p["n_star_exists_count"], p["n_cells"],
             json.dumps(p["n_star_per_cell"], sort_keys=True)))
    print("median dD: %s (~%s); grid-median N*: %s; '~3' within +-1: %s"
          % (p["median_dd"], p["median_dd_f"], p["grid_median_n_star_f"],
             p["bullet_tilde3_within_pm1"]))
    for aname in ("regime", "p_c", "L"):
        ax = p["axes"][aname]
        vals = {k: v["exists_share_f"] for k, v in ax.items() if k != "spread"}
        print("axis %-6s exists-shares %s spread %s"
              % (aname, json.dumps(vals, sort_keys=True), ax["spread"]))
    print("stability leg ruling: %s" % decisions["stability"]["ruling"])
    for lid, _ov in SENS_LEGS:
        print("sensitivity %-9s ruling-under-rule: %s (reporting-only)"
              % (lid, decisions[lid]["ruling"]))
    print("SELF-CHECKS: %d passed, %d failed"
          % (CHECKS["passed"], CHECKS["failed"]))
    if not ok:
        for fl in FAILURES[:20]:
            print("FAILED: %s" % fl)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
