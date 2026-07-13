#!/usr/bin/env python3
"""verdict-026 — Braess's paradox added-edge frequency on the pinned diamond.

Settles idea-engine PROPOSAL 024 (control/outbox.md 2026-07-13T04:21:12Z,
status: sim-ready; idea ideas/fleet/braess-paradox-added-edge-2026-07-13.md,
landed via idea-engine PR #290). Hermetic: reads exactly ONE file (its own
committed fixtures.json pre-registration, cross-checked at start), no network,
no repo state, no wall clock. Arm A is exact fractions.Fraction end to end
(platform-independent rationals); Arm S is stdlib random.Random under the four
pinned seeds with a documented float tolerance. Deterministic: stdout and
results.json are byte-identical across process runs (verified by external
diff). Progress goes to stderr only.

Run: python3 sims/verdict-026-braess-added-edge/braess_added_edge_sim.py
Exit 0 iff every self-check passes.
"""
import itertools
import json
import os
import random
import sys
from fractions import Fraction as Fr

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

SEEDS = [20260740, 20260741, 20260742, 20260743]
N_DRAWS = 25000
TOL_REL = 1e-9
TOL_ABS = 1e-12
VI_TOL = 1e-9
TWIN_STRIDE = 199
TWIN_AGREE = 1e-6

check(sys.version_info[:2] == (3, 11), "g5 CPython minor pinned to 3.11")
check(FX["arm_S"]["seeds"] == SEEDS, "fixtures: seeds 20260740-43")
check(FX["arm_S"]["n_draws_per_seed"] == N_DRAWS, "fixtures: n_draws 25000")
check(FX["arm_A"]["raw_fixture_count"] == 26244, "fixtures: raw census 26244")
check(FX["decision_rule"]["APPROVE"].startswith("f_A >= 0.15 OR median-r-among-paradox >= 1.15"),
      "fixtures: APPROVE band constants")
check(FX["decision_rule"]["REJECT"].startswith("f_A <= 0.03 AND max-r <= 1.05"),
      "fixtures: REJECT band constants")
check("1.0 pp" in FX["decision_rule"]["arm_agreement_gate"], "fixtures: arm gate 1.0 pp")

# Band constants (exact for Arm A, float for Arm S — same numbers).
BAND_FA_APPROVE = Fr(15, 100)
BAND_MEDR_APPROVE = Fr(115, 100)
BAND_FA_REJECT = Fr(3, 100)
BAND_MAXR_REJECT = Fr(105, 100)
ARM_GATE_PP = Fr(1, 100)

# Fixture tuple layout: (a1,b1, a2,b2, a3,b3, a4,b4, a5,b5).
# Route flows (f1 on R1=s->a->t, f2 on R2=s->b->t, f3 on R3=s->a->b->t),
# f2 = 1 - f1 - f3. Edge flows: x1=f1+f3, x2=f1, x3=f2, x4=f2+f3=1-f1, x5=f3.


# ---------------------------------------------------------------------------
# Primary solver — Beckmann candidate enumeration + Wardrop verification.
# Works in exact Fractions (div=Fr division) or floats (div=float division).
# ---------------------------------------------------------------------------
def route_latencies(co, f1, f3):
    a1, b1, a2, b2, a3, b3, a4, b4, a5, b5 = co
    x1 = f1 + f3
    x2 = f1
    x3 = 1 - f1 - f3
    x4 = 1 - f1
    x5 = f3
    l1 = a1 * x1 + b1
    l2 = a2 * x2 + b2
    l3 = a3 * x3 + b3
    l4 = a4 * x4 + b4
    l5 = a5 * x5 + b5
    return (l1 + l2, l3 + l4, l1 + l5 + l4)


def total_cost(co, f1, f3):
    a1, b1, a2, b2, a3, b3, a4, b4, a5, b5 = co
    xs = (f1 + f3, f1, 1 - f1 - f3, 1 - f1, f3)
    ab = ((a1, b1), (a2, b2), (a3, b3), (a4, b4), (a5, b5))
    c = 0
    for (a, b), x in zip(ab, xs):
        c += x * (a * x + b)
    return c


def phi2(co, f1, f3):
    """Twice the Beckmann potential (avoids division): sum a*x^2 + 2*b*x."""
    a1, b1, a2, b2, a3, b3, a4, b4, a5, b5 = co
    xs = (f1 + f3, f1, 1 - f1 - f3, 1 - f1, f3)
    ab = ((a1, b1), (a2, b2), (a3, b3), (a4, b4), (a5, b5))
    v = 0
    for (a, b), x in zip(ab, xs):
        v += a * x * x + 2 * b * x
    return v


def grad(co, f1, f3):
    """(dPhi/df1, dPhi/df3) = (L1 - L2, L3 - L2) — affine in (f1, f3)."""
    L1, L2, L3 = route_latencies(co, f1, f3)
    return (L1 - L2, L3 - L2)


def solve_with_bridge(co, div):
    """Wardrop equilibrium of the bridged network: argmin Phi over the
    simplex {f1>=0, f3>=0, f1+f3<=1}, by candidate enumeration."""
    cands = [(0, 0), (1, 0), (0, 1)]
    g00 = grad(co, 0, 0)
    g10 = grad(co, 1, 0)
    g01 = grad(co, 0, 1)
    a11 = g10[0] - g00[0]
    a12 = g01[0] - g00[0]
    a21 = g10[1] - g00[1]
    a22 = g01[1] - g00[1]
    det = a11 * a22 - a12 * a21
    if det != 0:
        c1, c2 = -g00[0], -g00[1]
        f1 = div(c1 * a22 - c2 * a12, det)
        f3 = div(a11 * c2 - a21 * c1, det)
        if f1 >= 0 and f3 >= 0 and f1 + f3 <= 1:
            cands.append((f1, f3))
    # Boundary edges: directional derivative is affine in t; root is a
    # candidate only when its slope is positive (else min is at endpoints,
    # already in cands as vertices).
    for point, deriv in (
        (lambda t: (t, 0), lambda t: grad(co, t, 0)[0]),            # f3 = 0
        (lambda t: (0, t), lambda t: grad(co, 0, t)[1]),            # f1 = 0
        (lambda t: (1 - t, t),
         lambda t: grad(co, 1 - t, t)[1] - grad(co, 1 - t, t)[0]),  # f2 = 0
    ):
        d0 = deriv(0)
        slope = deriv(1) - d0
        if slope > 0:
            t = div(-d0, slope)
            if 0 <= t <= 1:
                cands.append(point(t))
    return min(cands, key=lambda p: phi2(co, p[0], p[1]))


def solve_without_bridge(co, div):
    """Wardrop equilibrium of the base network (f3 pinned to 0)."""
    cands = [(0, 0), (1, 0)]
    d0 = grad(co, 0, 0)[0]
    slope = grad(co, 1, 0)[0] - d0
    if slope > 0:
        t = div(-d0, slope)
        if 0 <= t <= 1:
            cands.append((t, 0))
    return min(cands, key=lambda p: phi2(co, p[0], p[1]))


def vi_holds(co, f1, f3, with_bridge, tol):
    """Wardrop variational condition: every route with positive flow has
    minimal latency. tol=0 -> exact; tol>0 -> float tolerance."""
    L1, L2, L3 = route_latencies(co, f1, f3)
    f2 = 1 - f1 - f3
    if with_bridge:
        used = ((f1, L1), (f2, L2), (f3, L3))
        lmin = min(L1, L2, L3)
    else:
        used = ((f1, L1), (f2, L2))
        lmin = min(L1, L2)
    feas = f1 >= -tol and f2 >= -tol and f3 >= -tol
    return feas and all(L - lmin <= tol for f, L in used if f > tol)


# ---------------------------------------------------------------------------
# Twin evaluator — independently written support enumeration. Enumerates
# route-support patterns, solves latency-equalization linear systems, screens
# by feasibility + Wardrop, and returns EVERY equilibrium cost it finds.
# Underdetermined systems are skipped: every extreme equilibrium then lies on
# a smaller support, and singleton supports are always solvable.
# ---------------------------------------------------------------------------
ROUTE_EDGES = {1: (0, 1), 2: (2, 3), 3: (0, 4, 3)}  # route -> edge indices


def twin_edge_flows(fl):
    f1, f2, f3 = fl
    return (f1 + f3, f1, f2, f2 + f3, f3)


def twin_route_lat(co, xs, r):
    lat = 0
    for ei in ROUTE_EDGES[r]:
        lat += co[2 * ei] * xs[ei] + co[2 * ei + 1]
    return lat


def twin_cost(co, fl):
    xs = twin_edge_flows(fl)
    return sum(x * (co[2 * i] * x + co[2 * i + 1]) for i, x in enumerate(xs))


def twin_is_eq(co, fl, routes, tol):
    if any(f < -tol for f in fl):
        return False
    xs = twin_edge_flows(fl)
    lats = {r: twin_route_lat(co, xs, r) for r in routes}
    lmin = min(lats.values())
    for r in routes:
        if fl[r - 1] > tol and lats[r] - lmin > tol:
            return False
    return True


def twin_flows(support, values):
    fl = [0, 0, 0]
    for r, v in zip(support, values):
        fl[r - 1] = v
    return tuple(fl)


def twin_solve(co, routes, div, tol):
    """All equilibrium costs found via unique-solution support systems."""
    costs = []
    rl = list(routes)
    for m in range(1, 1 << len(rl)):
        support = [rl[i] for i in range(len(rl)) if m >> i & 1]
        sols = []
        if len(support) == 1:
            sols.append(twin_flows(support, (1,)))
        elif len(support) == 2:
            # one unknown u on support[0], 1-u on support[1]; equalize.
            ra, rb = support
            d_at = []
            for u in (0, 1):
                fl = twin_flows(support, (u, 1 - u))
                xs = twin_edge_flows(fl)
                d_at.append(twin_route_lat(co, xs, ra) - twin_route_lat(co, xs, rb))
            slope = d_at[1] - d_at[0]
            if slope != 0:
                u = div(-d_at[0], slope)
                if 0 <= u <= 1:
                    sols.append(twin_flows(support, (u, 1 - u)))
        else:
            # unknowns (u, v) on R1, R2; R3 gets 1-u-v. Equalize L1=L3, L2=L3.
            def dvec(u, v):
                fl = (u, v, 1 - u - v)
                xs = twin_edge_flows(fl)
                l3 = twin_route_lat(co, xs, 3)
                return (twin_route_lat(co, xs, 1) - l3,
                        twin_route_lat(co, xs, 2) - l3)
            e00, e10, e01 = dvec(0, 0), dvec(1, 0), dvec(0, 1)
            m11, m12 = e10[0] - e00[0], e01[0] - e00[0]
            m21, m22 = e10[1] - e00[1], e01[1] - e00[1]
            det = m11 * m22 - m12 * m21
            if det != 0:
                u = div(-e00[0] * m22 + e00[1] * m12, det)
                v = div(-m11 * e00[1] + m21 * e00[0], det)
                if u >= 0 and v >= 0 and u + v <= 1:
                    sols.append((u, v, 1 - u - v))
        for fl in sols:
            if twin_is_eq(co, fl, routes, tol):
                costs.append(twin_cost(co, fl))
    return costs


def div_exact(p, q):
    return Fr(p) / Fr(q)


def div_float(p, q):
    return p / q


# ---------------------------------------------------------------------------
# Arm A — exhaustive integer census, exact.
# ---------------------------------------------------------------------------
def run_arm_a():
    print("[arm A] census starting", file=sys.stderr)
    pair3 = list(itertools.product((0, 1, 2), repeat=2))
    pair2 = list(itertools.product((0, 1), repeat=2))
    results = {}  # co -> (cost_without, cost_with)
    n_eff = 0
    skipped = 0
    paradox = 0
    improved = 0
    ratios = []
    bridge_cells = {bc: [0, 0] for bc in pair2}  # (a5,b5) -> [paradox, n_eff]
    count = 0
    for e1 in pair3:
        for e2 in pair3:
            for e3 in pair3:
                for e4 in pair3:
                    for e5 in pair2:
                        co = e1 + e2 + e3 + e4 + e5
                        p0 = solve_without_bridge(co, div_exact)
                        c0 = total_cost(co, p0[0], p0[1])
                        p1 = solve_with_bridge(co, div_exact)
                        c1 = total_cost(co, p1[0], p1[1])
                        # g1 — Wardrop verification, exact, both networks.
                        check(vi_holds(co, p0[0], p0[1], False, 0),
                              "g1 VI without-bridge %r" % (co,))
                        check(vi_holds(co, p1[0], p1[1], True, 0),
                              "g1 VI with-bridge %r" % (co,))
                        # g4 — unused-bridge invariance, both directions.
                        if c1 != c0:
                            check(p1[1] > 0, "g4 cost moved with x5==0 %r" % (co,))
                        L3_at_p0 = route_latencies(co, p0[0], 0)[2]
                        Lmin_p0 = min(route_latencies(co, p0[0], 0)[:2])
                        if L3_at_p0 >= Lmin_p0:
                            check(c1 == c0,
                                  "g4 unattractive bridge changed cost %r" % (co,))
                        # twin — full census, both networks.
                        tw0 = twin_solve(co, (1, 2), div_exact, 0)
                        tw1 = twin_solve(co, (1, 2, 3), div_exact, 0)
                        check(len(tw0) >= 1 and all(c == c0 for c in tw0),
                              "twin without-bridge %r" % (co,))
                        check(len(tw1) >= 1 and all(c == c1 for c in tw1),
                              "twin with-bridge %r" % (co,))
                        results[co] = (c0, c1)
                        if c0 == 0:
                            skipped += 1
                        else:
                            n_eff += 1
                            bridge_cells[e5][1] += 1
                            if c1 > c0:
                                paradox += 1
                                bridge_cells[e5][0] += 1
                                r = Fr(c1) / Fr(c0)
                                # g2 — affine Braess bound, exact.
                                check(r <= Fr(4, 3),
                                      "g2 r > 4/3 %r" % (co,))
                                ratios.append(r)
                            elif c1 < c0:
                                improved += 1
                        count += 1
                        if count % 4374 == 0:
                            print("[arm A] %d / 26244" % count, file=sys.stderr)
    check(count == 26244, "census size 26244")
    check(n_eff + skipped == 26244, "census partition")
    # g3 — reversal-symmetry involution over the full census.
    for co, (c0, c1) in results.items():
        sco = co[6:8] + co[4:6] + co[2:4] + co[0:2] + co[8:10]
        check(results[sco] == (c0, c1), "g3 reversal symmetry %r" % (co,))
    # Hand-derived pins.
    for pin in FX["hand_derived_pins"]:
        f = pin["fixture"]
        co = tuple(f["e1"] + f["e2"] + f["e3"] + f["e4"] + f["e5"])
        c0, c1 = results[co]
        exp = pin["expected"]
        check(c0 == Fr(exp["cost_without"]), "%s cost_without" % pin["name"])
        check(c1 == Fr(exp["cost_with"]), "%s cost_with" % pin["name"])
        check((c1 > c0) == exp["paradox"], "%s paradox flag" % pin["name"])
        if "r" in exp:
            check(Fr(c1) / Fr(c0) == Fr(exp["r"]), "%s ratio" % pin["name"])
    ratios.sort()
    npar = len(ratios)
    check(npar == paradox, "ratio list complete")
    if npar % 2 == 1:
        med = ratios[npar // 2]
    else:
        med = (ratios[npar // 2 - 1] + ratios[npar // 2]) / 2
    f_a = Fr(paradox, n_eff)
    return {
        "results": results,
        "n_eff": n_eff,
        "skipped": skipped,
        "paradox": paradox,
        "improved": improved,
        "f_A": f_a,
        "median_r": med,
        "max_r": ratios[-1],
        "bridge_cells": bridge_cells,
    }


# ---------------------------------------------------------------------------
# Arm S — seeded continuous robustness, floats under documented tolerance.
# ---------------------------------------------------------------------------
def run_arm_s():
    print("[arm S] seeded legs starting", file=sys.stderr)
    per_seed = []
    pooled_n = 0
    pooled_paradox = 0
    skipped = 0
    twin_checked = 0
    ratios = []
    for seed in SEEDS:
        rng = random.Random(seed)
        uniforms = 0
        s_n = 0
        s_par = 0
        for i in range(N_DRAWS):
            co = tuple(2.0 * rng.random() for _ in range(10))
            uniforms += 10
            p0 = solve_without_bridge(co, div_float)
            c0 = total_cost(co, p0[0], p0[1])
            check(vi_holds(co, p0[0], p0[1], False, VI_TOL),
                  "g1 VI without (S) seed=%d i=%d" % (seed, i))
            if c0 <= TOL_ABS:
                skipped += 1
                continue
            p1 = solve_with_bridge(co, div_float)
            c1 = total_cost(co, p1[0], p1[1])
            check(vi_holds(co, p1[0], p1[1], True, VI_TOL),
                  "g1 VI with (S) seed=%d i=%d" % (seed, i))
            s_n += 1
            if c1 > c0 * (1.0 + TOL_REL) + TOL_ABS:
                s_par += 1
                ratios.append(c1 / c0)
            if i % TWIN_STRIDE == 0:
                tw0 = twin_solve(co, (1, 2), div_float, VI_TOL)
                tw1 = twin_solve(co, (1, 2, 3), div_float, VI_TOL)
                check(tw0 and min(abs(c - c0) for c in tw0) <= TWIN_AGREE,
                      "twin (S) without seed=%d i=%d" % (seed, i))
                check(tw1 and min(abs(c - c1) for c in tw1) <= TWIN_AGREE,
                      "twin (S) with seed=%d i=%d" % (seed, i))
                twin_checked += 1
        # g6 — exact draw-count sentinel.
        check(uniforms == 10 * N_DRAWS, "g6 uniform count seed=%d" % seed)
        fresh = random.Random(seed)
        for _ in range(10 * N_DRAWS):
            fresh.random()
        check(fresh.random() == rng.random(), "g6 stream position seed=%d" % seed)
        per_seed.append({"seed": seed, "n": s_n, "paradox": s_par})
        pooled_n += s_n
        pooled_paradox += s_par
        print("[arm S] seed %d done" % seed, file=sys.stderr)
    ratios.sort()
    npar = len(ratios)
    if npar % 2 == 1:
        med = ratios[npar // 2]
    else:
        med = (ratios[npar // 2 - 1] + ratios[npar // 2]) / 2
    return {
        "per_seed": per_seed,
        "pooled_n": pooled_n,
        "skipped": skipped,
        "pooled_paradox": pooled_paradox,
        "f_S": pooled_paradox / pooled_n,
        "median_r_S": med,
        "max_r_S": ratios[-1],
        "twin_checked": twin_checked,
    }


# ---------------------------------------------------------------------------
# Decision — the pre-registered bands, evaluated per arm + the agreement gate.
# ---------------------------------------------------------------------------
def band_call(f, med_r, max_r):
    if f >= BAND_FA_APPROVE or med_r >= BAND_MEDR_APPROVE:
        return "APPROVE"
    if f <= BAND_FA_REJECT and max_r <= BAND_MAXR_REJECT:
        return "REJECT"
    return "NULL"


def main():
    a = run_arm_a()
    s = run_arm_s()

    call_a = band_call(a["f_A"], a["median_r"], a["max_r"])
    call_s = band_call(Fr(s["pooled_paradox"], s["pooled_n"]),
                       Fr(s["median_r_S"]), Fr(s["max_r_S"]))
    gap = abs(Fr(s["pooled_paradox"], s["pooled_n"]) - a["f_A"])
    gate_gap_ok = gap <= ARM_GATE_PP
    gate_same_call = call_a == call_s
    arms_agree = gate_gap_ok and gate_same_call
    ruling = call_a if arms_agree else "NULL"
    ruling_label = ruling if arms_agree else "NULL-by-arm-disagreement"
    if arms_agree and ruling == "NULL":
        ruling_label = "NULL (the straddle, arms agreeing)"

    bridge_rows = {}
    for (a5, b5), (par, n) in sorted(a["bridge_cells"].items()):
        key = "a5=%d,b5=%d" % (a5, b5)
        bridge_rows[key] = {
            "n": n, "paradox": par,
            "f": str(Fr(par, n)), "f_float": float(Fr(par, n)),
        }

    out = {
        "proposal": FX["source"]["proposal"],
        "arm_A": {
            "raw_census": 26244,
            "skipped_zero_cost_without": a["skipped"],
            "N_effective": a["n_eff"],
            "paradox_count": a["paradox"],
            "improved_count_reporting_only": a["improved"],
            "unchanged_count_reporting_only": a["n_eff"] - a["paradox"] - a["improved"],
            "f_A_exact": str(a["f_A"]),
            "f_A": float(a["f_A"]),
            "median_r_exact": str(a["median_r"]),
            "median_r": float(a["median_r"]),
            "max_r_exact": str(a["max_r"]),
            "max_r": float(a["max_r"]),
            "call": call_a,
            "paradox_by_bridge_cell_reporting_only": bridge_rows,
        },
        "arm_S": {
            "per_seed": s["per_seed"],
            "pooled_n": s["pooled_n"],
            "degenerate_skipped": s["skipped"],
            "pooled_paradox": s["pooled_paradox"],
            "f_S": s["f_S"],
            "median_r_S": s["median_r_S"],
            "max_r_S": s["max_r_S"],
            "twin_draws_checked": s["twin_checked"],
            "call": call_s,
        },
        "arm_agreement": {
            "abs_gap": float(gap),
            "abs_gap_exact": str(gap),
            "gap_within_1pp": gate_gap_ok,
            "same_call": gate_same_call,
            "met": arms_agree,
        },
        "bands": {
            "APPROVE": "f_A >= 0.15 OR median-r >= 1.15",
            "REJECT": "f_A <= 0.03 AND max-r <= 1.05",
            "NULL": "the straddle, or arm disagreement",
        },
        "ruling": ruling,
        "ruling_label": ruling_label,
        "model_basis": FX["model_basis"],
        "self_checks_passed": None,  # filled below
    }

    # Headline stdout (deterministic).
    print("verdict-026 braess-added-edge — results")
    print("arm A: raw 26244, skipped %d, N %d" % (a["skipped"], a["n_eff"]))
    print("arm A: paradox %d, f_A = %s = %r" % (a["paradox"], a["f_A"], float(a["f_A"])))
    print("arm A: median r = %s = %r ; max r = %s = %r" %
          (a["median_r"], float(a["median_r"]), a["max_r"], float(a["max_r"])))
    print("arm A: improved %d, unchanged %d (reporting-only)" %
          (a["improved"], a["n_eff"] - a["paradox"] - a["improved"]))
    print("arm A call: %s" % call_a)
    print("arm S: pooled n %d (skipped %d), paradox %d, f_S = %r" %
          (s["pooled_n"], s["skipped"], s["pooled_paradox"], s["f_S"]))
    print("arm S: median r = %r ; max r = %r ; call: %s" %
          (s["median_r_S"], s["max_r_S"], call_s))
    print("arm gate: |f_S - f_A| = %r (<= 0.01: %s), same call: %s" %
          (float(gap), gate_gap_ok, gate_same_call))
    print("RULING: %s" % ruling_label)

    out["self_checks_passed"] = CHECKS + 1  # + the final write-side check below
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    check(out["ruling"] in ("APPROVE", "REJECT", "NULL"), "ruling well-formed")
    print("SELF-CHECKS: %d passed, 0 failed" % CHECKS)


if __name__ == "__main__":
    main()
