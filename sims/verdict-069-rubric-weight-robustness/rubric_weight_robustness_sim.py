#!/usr/bin/env python3
"""VERDICT 069 — rubric weight-robustness (idea-engine PROPOSAL 058, INTAKE 058).

Hermetic, stdlib-only, deterministic. Reads ONLY its own fixtures.json.
Arm A: seedless exact fractions.Fraction linear-fractional 32-vertex arithmetic
       (decision-bearing for the x* clauses; powers gates F2/F3/F4).
Arm S: seeded MC (main 20261369, stability 20261370; cross-seed gate 1/50 abs).
Reporting: seed 20261371 (Dirichlet worlds kappa in {100, 400}); aux 20261372
       is NEVER read (asserted).
Pre-registered rule evaluated IN ORDER: REJECT -> INVALID -> APPROVE -> NULL.
Run: python3 rubric_weight_robustness_sim.py   (from anywhere; paths self-anchor)
"""

import json
import os
import random
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- self-checks
CHECKS = {"passed": 0, "failed": 0}
FAILURES = []


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        FAILURES.append(name)
        print("SELF-CHECK FAIL: %s" % name)
    return bool(cond)


def frac(s):
    return Fraction(s)


# ---------------------------------------------------------------- fixtures
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

check("cpython-minor-pinned-3.11", sys.version_info[:2] == (3, 11))

S = [[frac(s) for s in c["scores"]] for c in FX["score_table_S"]["concepts"]]
NAMES = [c["name"] for c in FX["score_table_S"]["concepts"]]
W0 = [frac(s) for s in FX["weights_w0"]]
PUB = [frac(s) for s in FX["published_totals_identity_row"]]
EDGE_LO = frac(FX["bands"]["no_build_edge"])       # 3
EDGE_HI = frac(FX["bands"]["best_edge"])           # 7/2
B0 = FX["bands"]["baseline_partition_B0"]
GRID = [frac(s) for s in FX["jitter"]["radius_grid_pinned_order"]]
DECISION_X = frac(FX["jitter"]["decision_cell"])
REJECT_P_FLOOR = frac(FX["decision_constants"]["reject_p_floor"])      # 1/10
APPROVE_P_CEIL = frac(FX["decision_constants"]["approve_p_ceiling"])   # 1/20
XSTAR_THRESH = frac(FX["decision_constants"]["x_star_threshold"])      # 1/20
CROSS_SEED_GATE = frac(FX["gates"]["cross_seed_agreement_gate_abs"])   # 1/50
F2_OFF = frac(FX["gates"]["F2_probe_offset"])                          # 1/1000
F4_TOL = float(FX["gates"]["F4_tolerance_abs"])                        # 1e-9
SEEDS = FX["seeds"]
N_MAIN = FX["draw_counts"]["main_N_per_radius"]
N_STAB = FX["draw_counts"]["stability_N_per_radius"]
N_REP = FX["draw_counts"]["reporting_N_per_world"]
KAPPAS = FX["dirichlet_reporting_worlds"]["kappas"]

NC = len(S)          # 7 concepts
NA = len(W0)         # 5 axes

# aux-seed hygiene: the aux seed value exists in fixtures but no RNG is ever
# constructed from it. RNG_CONSTRUCTED records every seed passed to
# random.Random this process — asserted at the end.
RNG_CONSTRUCTED = []


def make_rng(seed):
    RNG_CONSTRUCTED.append(seed)
    assert seed != SEEDS["aux_reserved_never_read"], "aux seed must NEVER be read"
    return CountingRandom(seed)


class CountingRandom(random.Random):
    """random.Random with a core random() call counter (F6 sentinel)."""

    def __init__(self, seed):
        super().__init__(seed)
        self.calls = 0

    def random(self):
        self.calls += 1
        return super().random()


# ---------------------------------------------------------------- band logic
def band_frac(t):
    """Exact band of a Fraction total (registered reading)."""
    if t < EDGE_LO:
        return "no-build"
    if t <= EDGE_HI:
        return "borderline"
    return "best"


EDGE_LO_F = float(EDGE_LO)
EDGE_HI_F = float(EDGE_HI)


def band_float(t):
    """Float band for MC legs (C2)."""
    if t < EDGE_LO_F:
        return 0  # no-build
    if t <= EDGE_HI_F:
        return 1  # borderline
    return 2      # best


BAND_CODE = {"no-build": 0, "borderline": 1, "best": 2}

# ---------------------------------------------------------------- Arm A exact
PATTERNS = []
for m in range(32):
    PATTERNS.append(tuple(1 if (m >> j) & 1 else -1 for j in range(NA)))

# per concept: a0 = sum w0_j S_ij  (baseline total)
A0 = [sum(W0[j] * S[i][j] for j in range(NA)) for i in range(NC)]


def vertex_total(i, pattern, x):
    """Exact t_i at the jitter-box vertex given by pattern, radius x."""
    num = sum(W0[j] * (1 + pattern[j] * x) * S[i][j] for j in range(NA))
    den = sum(W0[j] * (1 + pattern[j] * x) for j in range(NA))
    return num / den


def vertex_range(i, x):
    """Exact reachable [min, max] of t_i over the box at radius x
    (linear-fractional box extrema sit at vertices)."""
    vals = [vertex_total(i, p, x) for p in PATTERNS]
    return min(vals), max(vals)


def critical_radius(i):
    """Exact x*_i: min positive solution in (0,1) of t_P(x) = e over all
    32 patterns and both edges; returns (x*, crossed_edge, pattern)."""
    best = None
    for p in PATTERNS:
        a1 = sum(p[j] * W0[j] * S[i][j] for j in range(NA))
        b1 = sum(p[j] * W0[j] for j in range(NA))
        for e in (EDGE_LO, EDGE_HI):
            den = a1 - e * b1
            if den == 0:
                continue
            x = (e - A0[i]) / den
            if 0 < x < 1:
                if best is None or x < best[0]:
                    best = (x, e, p)
    return best


# F1 — identity
check("F1-weights-sum-1", sum(W0) == 1)
for i in range(NC):
    check("F1-total-%d" % (i + 1), A0[i] == PUB[i])
BASE_BANDS = [band_frac(A0[i]) for i in range(NC)]
check("F1-baseline-partition", BASE_BANDS == B0)

# x* table
XSTAR = []
for i in range(NC):
    r = critical_radius(i)
    check("xstar-%d-exists" % (i + 1), r is not None)
    XSTAR.append(r)

X_VALS = [r[0] for r in XSTAR]
MIN_XSTAR = min(X_VALS)

# F2 — critical-radius self-consistency
for i in range(NC):
    xs, edge, _pat = XSTAR[i]
    lo_m, hi_m = vertex_range(i, xs - F2_OFF)
    inside = band_frac(lo_m) == BASE_BANDS[i] and band_frac(hi_m) == BASE_BANDS[i]
    # strictly inside: neither extreme may sit ON a boundary edge either
    strict = inside and lo_m != EDGE_LO and hi_m != EDGE_LO and lo_m != EDGE_HI and hi_m != EDGE_HI
    check("F2-below-%d" % (i + 1), strict)
    lo_p, hi_p = vertex_range(i, xs + F2_OFF)
    check("F2-above-%d" % (i + 1), lo_p <= edge <= hi_p)
check("F2-probe-legal", MIN_XSTAR - F2_OFF > 0)

# F3 (exact half) — 1/50 < min x*, recomputed
check("F3-exact-1/50-lt-min-xstar", Fraction(1, 50) < MIN_XSTAR)

# F5 — hand world
HW = FX["gates"]["F5_hand_world"]
hw_w = [frac(s) for s in HW["weights"]]
hw_s = [frac(s) for s in HW["scores"]]
hw_total = sum(hw_w[j] * hw_s[j] for j in range(2))
check("F5-hand-total", hw_total == frac(HW["expected_total"]))
x10 = Fraction(1, 10)
hw_vals = []
for m in range(4):
    p = tuple(1 if (m >> j) & 1 else -1 for j in range(2))
    num = sum(hw_w[j] * (1 + p[j] * x10) * hw_s[j] for j in range(2))
    den = sum(hw_w[j] * (1 + p[j] * x10) for j in range(2))
    hw_vals.append(num / den)
check("F5-hand-range",
      min(hw_vals) == frac(HW["expected_range_at_x_1_10"][0])
      and max(hw_vals) == frac(HW["expected_range_at_x_1_10"][1]))

# exact vertex ranges per (concept, radius) — powers F4 and the report
RANGES = {}
for x in GRID:
    RANGES[x] = [vertex_range(i, x) for i in range(NC)]

# ---------------------------------------------------------------- Arm S MC
S_FLOAT = [[float(v) for v in row] for row in S]
W0_FLOAT = [float(v) for v in W0]
B0_CODE = [BAND_CODE[b] for b in B0]


def mc_leg(seed, n_draws, label):
    """One uniform-jitter MC leg over the full radius grid. Returns per-radius
    stats. Draw order pinned: per draw, 5 core random() calls in criterion
    order (C1: u_j = (1-x) + 2x*r)."""
    rng = make_rng(seed)
    leg = {"label": label, "seed": seed, "N": n_draws, "radii": []}
    for x in GRID:
        xf = float(x)
        lo = 1.0 - xf
        span = 2.0 * xf
        ranges_f = [(float(RANGES[x][i][0]), float(RANGES[x][i][1])) for i in range(NC)]
        calls_before = rng.calls
        flips = 0
        band_changes = [0] * NC
        edge_hits = 0
        containment_ok = True
        for _ in range(n_draws):
            u = [lo + span * rng.random() for _ in range(NA)]
            wden = 0.0
            wj = [0.0] * NA
            for j in range(NA):
                wv = W0_FLOAT[j] * u[j]
                wj[j] = wv
                wden += wv
            flipped = False
            for i in range(NC):
                row = S_FLOAT[i]
                t = (wj[0] * row[0] + wj[1] * row[1] + wj[2] * row[2]
                     + wj[3] * row[3] + wj[4] * row[4]) / wden
                if t == EDGE_LO_F or t == EDGE_HI_F:
                    edge_hits += 1
                rlo, rhi = ranges_f[i]
                if t < rlo - F4_TOL or t > rhi + F4_TOL:
                    containment_ok = False
                if band_float(t) != B0_CODE[i]:
                    band_changes[i] += 1
                    flipped = True
            if flipped:
                flips += 1
        calls = rng.calls - calls_before
        check("F6-sentinel-%s-x=%s" % (label, x), calls == 5 * n_draws)
        check("F4-containment-%s-x=%s" % (label, x), containment_ok)
        if x == Fraction(1, 50):
            check("F3-zero-flip-%s" % label, flips == 0 and sum(band_changes) == 0)
        leg["radii"].append({
            "x": str(x),
            "flips": flips,
            "p_hat": flips / n_draws,
            "band_changes_per_concept": band_changes,
            "edge_hits": edge_hits,
            "core_random_calls": calls,
        })
    return leg


MAIN = mc_leg(SEEDS["main"], N_MAIN, "main")
STAB = mc_leg(SEEDS["stability"], N_STAB, "stability")

# cross-seed agreement gate
gate_f = float(CROSS_SEED_GATE)
for k, x in enumerate(GRID):
    dev = abs(MAIN["radii"][k]["p_hat"] - STAB["radii"][k]["p_hat"])
    check("cross-seed-gate-x=%s" % x, dev <= gate_f)

# ---------------------------------------------------------------- reporting
def dirichlet_leg(rng, kappa, n_draws):
    """Dirichlet reporting world (seed 20261371 only; never decision-bearing).
    5 gammavariate calls per draw in criterion order (C5)."""
    alphas = [kappa * w for w in W0_FLOAT]
    gcalls = 0
    flips = 0
    band_changes = [0] * NC
    for _ in range(n_draws):
        g = [rng.gammavariate(a, 1.0) for a in alphas]
        gcalls += NA
        gden = sum(g)
        flipped = False
        for i in range(NC):
            row = S_FLOAT[i]
            t = (g[0] * row[0] + g[1] * row[1] + g[2] * row[2]
                 + g[3] * row[3] + g[4] * row[4]) / gden
            if band_float(t) != B0_CODE[i]:
                band_changes[i] += 1
                flipped = True
        if flipped:
            flips += 1
    return {"kappa": kappa, "N": n_draws, "flips": flips,
            "p_hat": flips / n_draws,
            "band_changes_per_concept": band_changes,
            "gammavariate_calls": gcalls}


REP_RNG = make_rng(SEEDS["reporting"])
DIRICHLET = [dirichlet_leg(REP_RNG, k, N_REP) for k in KAPPAS]
for d in DIRICHLET:
    check("C5-gamma-call-count-kappa=%d" % d["kappa"], d["gammavariate_calls"] == 5 * N_REP)

# aux hygiene
check("aux-seed-never-read", SEEDS["aux_reserved_never_read"] not in RNG_CONSTRUCTED)
check("only-registered-rngs",
      RNG_CONSTRUCTED == [SEEDS["main"], SEEDS["stability"], SEEDS["reporting"]])

# ---------------------------------------------------------------- twin evaluators
DEC_IDX = GRID.index(DECISION_X)
P_MAIN_DEC = Fraction(MAIN["radii"][DEC_IDX]["flips"], N_MAIN)
P_STAB_DEC = Fraction(STAB["radii"][DEC_IDX]["flips"], N_STAB)


def gates_all_green():
    return CHECKS["failed"] == 0


def evaluator_one(p_dec, x_vals, controls_green):
    """Twin evaluator #1: literal transcription of the registered order."""
    if p_dec >= REJECT_P_FLOOR and x_vals[0] <= XSTAR_THRESH and x_vals[5] <= XSTAR_THRESH:
        return "reject"
    if not controls_green:
        return "invalid"
    if p_dec <= APPROVE_P_CEIL and all(v > XSTAR_THRESH for v in x_vals):
        return "approve"
    return "null"


def evaluator_two(p_dec, x_vals, controls_green):
    """Twin evaluator #2: independently structured — classify each clause
    side first, then walk the registered order over the flags."""
    flags = {
        "p_ge_reject": not (p_dec < REJECT_P_FLOOR),
        "c1_knife": not (x_vals[0] > XSTAR_THRESH),
        "c6_knife": not (x_vals[5] > XSTAR_THRESH),
        "p_le_approve": not (p_dec > APPROVE_P_CEIL),
        "all_robust": sum(1 for v in x_vals if v > XSTAR_THRESH) == len(x_vals),
        "controls": controls_green,
    }
    for rule in ("REJECT", "INVALID", "APPROVE", "NULL"):
        if rule == "REJECT" and flags["p_ge_reject"] and flags["c1_knife"] and flags["c6_knife"]:
            return "reject"
        if rule == "INVALID" and not flags["controls"]:
            return "invalid"
        if rule == "APPROVE" and flags["p_le_approve"] and flags["all_robust"]:
            return "approve"
        if rule == "NULL":
            return "null"
    raise AssertionError("unreachable")


CONTROLS_GREEN_PRE = gates_all_green()
CLASS_1 = evaluator_one(P_MAIN_DEC, X_VALS, CONTROLS_GREEN_PRE)
CLASS_2 = evaluator_two(P_MAIN_DEC, X_VALS, CONTROLS_GREEN_PRE)
check("twin-evaluators-agree-headline", CLASS_1 == CLASS_2)
STAB_CLASS_1 = evaluator_one(P_STAB_DEC, X_VALS, CONTROLS_GREEN_PRE)
STAB_CLASS_2 = evaluator_two(P_STAB_DEC, X_VALS, CONTROLS_GREEN_PRE)
check("twin-evaluators-agree-stability", STAB_CLASS_1 == STAB_CLASS_2)
check("stability-reproduces-ruling", STAB_CLASS_1 == CLASS_1)

# final class: re-evaluate with the FINAL controls state (the late checks above
# can only flip controls_green to False, routing to INVALID; REJECT precedes
# INVALID in the registered order, so a REJECT stands regardless).
CONTROLS_GREEN = gates_all_green()
FINAL_CLASS = evaluator_one(P_MAIN_DEC, X_VALS, CONTROLS_GREEN)
FINAL_CLASS_2 = evaluator_two(P_MAIN_DEC, X_VALS, CONTROLS_GREEN)
assert FINAL_CLASS == FINAL_CLASS_2

# drafter-reference comparison (REPORTED, never gated)
DRAFTER_X = [frac(s) for s in FX["drafter_disclosed_reference_never_gated"]["x_star"]]
DRAFTER_MATCH = [X_VALS[i] == DRAFTER_X[i] for i in range(NC)]

# ---------------------------------------------------------------- results
RESULTS = {
    "verdict": "VERDICT 069",
    "intake": "INTAKE 058",
    "class": FINAL_CLASS,
    "cpython": "%d.%d" % sys.version_info[:2],
    "arm_a": {
        "baseline_totals": [str(v) for v in A0],
        "baseline_partition": BASE_BANDS,
        "x_star": [
            {
                "concept": i + 1,
                "name": NAMES[i],
                "x_star": str(XSTAR[i][0]),
                "x_star_float": float(XSTAR[i][0]),
                "crossed_edge": str(XSTAR[i][1]),
                "vertex_pattern": list(XSTAR[i][2]),
                "matches_drafter_disclosure": DRAFTER_MATCH[i],
            }
            for i in range(NC)
        ],
        "min_x_star": str(MIN_XSTAR),
        "vertex_ranges_per_radius": {
            str(x): [[str(RANGES[x][i][0]), str(RANGES[x][i][1])] for i in range(NC)]
            for x in GRID
        },
    },
    "arm_s": {"main": MAIN, "stability": STAB},
    "cross_seed_gate": {
        "abs_bound": str(CROSS_SEED_GATE),
        "per_radius_abs_dev": [
            abs(MAIN["radii"][k]["p_hat"] - STAB["radii"][k]["p_hat"])
            for k in range(len(GRID))
        ],
    },
    "reporting_dirichlet": DIRICHLET,
    "decision": {
        "p_hat_main_at_decision_cell": {"num": P_MAIN_DEC.numerator, "den": P_MAIN_DEC.denominator, "float": float(P_MAIN_DEC)},
        "p_hat_stability_at_decision_cell": {"num": P_STAB_DEC.numerator, "den": P_STAB_DEC.denominator, "float": float(P_STAB_DEC)},
        "reject_conjuncts": {
            "p_main_ge_1_10": bool(P_MAIN_DEC >= REJECT_P_FLOOR),
            "x_star_1_le_1_20": bool(X_VALS[0] <= XSTAR_THRESH),
            "x_star_6_le_1_20": bool(X_VALS[5] <= XSTAR_THRESH),
        },
        "twin_evaluators": {"headline": [CLASS_1, CLASS_2], "stability": [STAB_CLASS_1, STAB_CLASS_2]},
        "evaluation_order": "REJECT -> INVALID -> APPROVE -> NULL",
    },
    "rngs_constructed_in_order": RNG_CONSTRUCTED,
    "aux_seed_never_read": SEEDS["aux_reserved_never_read"] not in RNG_CONSTRUCTED,
    "self_checks": {"passed": CHECKS["passed"], "failed": CHECKS["failed"], "failures": FAILURES},
}

out = json.dumps(RESULTS, indent=2, sort_keys=True)
with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    fh.write(out + "\n")

print("VERDICT 069 — rubric weight-robustness (INTAKE 058 / idea-engine PROPOSAL 058)")
print("class: %s" % FINAL_CLASS)
print("x* table (exact):")
for row in RESULTS["arm_a"]["x_star"]:
    print("  concept %d %-34s x* = %-6s (%.6f) edge %s  drafter-match=%s"
          % (row["concept"], NAMES[row["concept"] - 1], row["x_star"],
             row["x_star_float"], row["crossed_edge"], row["matches_drafter_disclosure"]))
print("p_hat main   per radius: %s" % ["%s: %.6f" % (r["x"], r["p_hat"]) for r in MAIN["radii"]])
print("p_hat stab   per radius: %s" % ["%s: %.6f" % (r["x"], r["p_hat"]) for r in STAB["radii"]])
print("dirichlet    (reporting): %s" % ["kappa=%d: %.6f" % (d["kappa"], d["p_hat"]) for d in DIRICHLET])
print("attribution  main x=1/10: %s" % MAIN["radii"][DEC_IDX]["band_changes_per_concept"])
print("edge hits total: %d" % sum(r["edge_hits"] for r in MAIN["radii"] + STAB["radii"]))
print("rngs constructed (order): %s ; aux %d never read: %s"
      % (RNG_CONSTRUCTED, SEEDS["aux_reserved_never_read"], RESULTS["aux_seed_never_read"]))
print("SELF-CHECKS: %d passed, %d failed" % (CHECKS["passed"], CHECKS["failed"]))
sys.exit(0 if CHECKS["failed"] == 0 else 1)
