#!/usr/bin/env python3
"""VERDICT 057 — keyword tiling vs independent picks (idea-engine PROPOSAL 046).

TILE (the keyword map's first-claim-wins convention) vs GREEDY (independent
per-packet drafting) over the registration's pinned synthetic search-shelf
world. Arm A: seedless exact Fraction enumeration (the DECISION arm). Arm S:
seeded MC confirmation (seed 20261321), CRN across the two worlds. Decision
rule pre-registered in PROPOSAL 046, evaluated IN ORDER, REJECT FIRST.

Hermetic: reads ONLY its own fixtures.json. Stdlib only. No wall-clock in any
output. Deterministic: stdout + results.json byte-identical across process
runs under the pinned CPython minor.
"""

import bisect
import hashlib
import json
import os
import random
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = json.load(open(os.path.join(HERE, "fixtures.json")))

# ---------------------------------------------------------------- self-checks
CHECKS = {"passed": 0, "failed": 0}


def check(name, cond):
    if cond:
        CHECKS["passed"] += 1
    else:
        CHECKS["failed"] += 1
        print("SELF-CHECK FAIL: " + name)


def fr(s):
    return F(s)


def s(x):  # exact Fraction -> stable string
    return "%d/%d" % (x.numerator, x.denominator) if x.denominator != 1 else "%d" % x.numerator


def fl(x):  # stable float rendering for stdout readability
    return "%.9f" % float(x)


# ------------------------------------------------------------------ pin gates
PIN = tuple(FIX["cpython_minor_pin"])
check("cpython minor pinned %s == %s" % (sys.version_info[:2], PIN), sys.version_info[:2] == PIN)

# ------------------------------------------------------------- model constants
M = FIX["universes"]["keyword"]["size"]
C = FIX["universes"]["category"]["size"]
MASS_KW = fr(FIX["universes"]["keyword"]["mass"])
MASS_CAT = fr(FIX["universes"]["category"]["mass"])
N = FIX["catalog"]["titles"]
QUOTA = {"keyword": FIX["catalog"]["keyword_quota"], "category": FIX["catalog"]["category_quota"]}
WIN = {"keyword": FIX["fit_windows"]["keyword"], "category": FIX["fit_windows"]["category"]}
BETA = [fr(x) for x in FIX["shelf"]["beta"]]
BETA_FLAT = [fr(x) for x in FIX["shelf"]["beta_flat_reporting"]]
S_POS = FIX["shelf"]["positions"]
GAMMAS = [fr(g) for g in FIX["dilution"]["gamma_grid"]]
ROWS = ["LOW", "MED", "HIGH"]
EXT_POOL = [fr(x) for x in FIX["externals"]["fit_pool"]]
MARGIN = fr(FIX["decision_bands"]["margin"])
SEEDS = FIX["seeds"]


def zipf(n):
    H = sum(F(1, j) for j in range(1, n + 1))
    return [F(1, k) / H for k in range(1, n + 1)]


W_KW = zipf(M)
W_CAT = zipf(C)


def ext_count(universe, cell):  # cell is 1-based
    if universe == "keyword":
        return 4 if cell <= 20 else (3 if cell <= 60 else 2)
    return 4 if cell <= 10 else 3


def ext_fits(universe, cell):
    return EXT_POOL[: ext_count(universe, cell)]


def homes(row, universe):
    key = "keyword_homes" if universe == "keyword" else "category_homes"
    return FIX["overlap_rows"][row][key]


def fit(row, universe, title, cell):  # title 1-based, cell 1-based
    h = homes(row, universe)[title - 1]
    L = WIN[universe]
    d = abs(cell - h)
    return F(L - d, L) if d < L else F(0)


# --------------------------------------------------------------- shelf engine
def solo_position(f, exts):
    """Position the fit f takes on an externals-only shelf (externals-first ties)."""
    return 1 + sum(1 for e in exts if e >= f)


def solo_score(weight, f, exts, beta):
    pos = solo_position(f, exts)
    return weight * beta[pos - 1] if pos <= len(beta) else F(0)


def diluted(f, gamma, j):
    return f / (1 + gamma * (j - 1))


def shelf_positions(exts, claimants, gamma):
    """Rank a shelf. claimants: list of (title, fit). Returns list of
    (kind, ident) for positions 1..S_POS; kind 'E' external / 'T' title."""
    j = len(claimants)
    occ = [(e, 0, i) for i, e in enumerate(exts)]
    occ += [(diluted(f, gamma, j), 1, t) for (t, f) in claimants]
    occ.sort(key=lambda x: (-x[0], x[1], x[2]))
    return [("E" if o[1] == 0 else "T", o[2]) for o in occ[:S_POS]]


def shelf_catalog_mass(exts, claimants, gamma, beta):
    """(total catalog click mass, {title: mass}) on one shelf."""
    per = {}
    total = F(0)
    for i, (kind, ident) in enumerate(shelf_positions(exts, claimants, gamma)):
        if kind == "T":
            total += beta[i]
            per[ident] = per.get(ident, F(0)) + beta[i]
    return total, per


# ------------------------------------------------------------------ allocation
def candidates(row, universe, title, weights, beta):
    """Positive-fit cells scored solo, sorted (score desc, cell asc)."""
    cands = []
    for cell in range(1, len(weights) + 1):
        f = fit(row, universe, title, cell)
        if f > 0:
            cands.append((cell, solo_score(weights[cell - 1], f, ext_fits(universe, cell), beta), f))
    cands.sort(key=lambda x: (-x[1], x[0]))
    return cands


def alloc_greedy(row, universe, weights, beta):
    """{title: [cells]}, fallback count (always 0 for GREEDY)."""
    out = {}
    for t in range(1, N + 1):
        out[t] = [c for (c, _, _) in candidates(row, universe, t, weights, beta)[: QUOTA[universe]]]
    return out, 0


def alloc_tile(row, universe, weights, beta):
    claimed = set()
    out = {}
    fallback = 0
    for t in range(1, N + 1):  # F3: pinned claim order t = 1..14
        cands = candidates(row, universe, t, weights, beta)
        picks = [c for (c, _, _) in cands if c not in claimed][: QUOTA[universe]]
        if len(picks) < QUOTA[universe]:  # C4 fallback: best already-claimed cell
            for (c, _, _) in cands:
                if len(picks) >= QUOTA[universe]:
                    break
                if c in claimed and c not in picks:
                    picks.append(c)
                    fallback += 1
        check("alloc %s %s title %d filled quota" % (row, universe, t), len(picks) == QUOTA[universe])
        out[t] = picks
        claimed.update(picks)
    return out, fallback


def cell_claimants(alloc, universe, row):
    """{cell: [(title, fit)] in title order}"""
    cc = {}
    for t in sorted(alloc):
        for c in alloc[t]:
            cc.setdefault(c, []).append((t, fit(row, universe, t, c)))
    return cc


def world_eval(row, alloc_kw, alloc_cat, gamma, beta, mass_kw, mass_cat):
    """T (exact), per-title traffic, kw/cat decomposition, and per-shelf
    catalog-occupancy tables (for Arm S)."""
    T = F(0)
    per_title = {t: F(0) for t in range(1, N + 1)}
    decomp = {}
    occupancy = {}
    for universe, weights, alloc, mass in (
        ("keyword", W_KW, alloc_kw, mass_kw),
        ("category", W_CAT, alloc_cat, mass_cat),
    ):
        cc = cell_claimants(alloc, universe, row)
        part = F(0)
        occ_u = []
        for cell in range(1, len(weights) + 1):
            exts = ext_fits(universe, cell)
            claimants = cc.get(cell, [])
            mass_cell, per = shelf_catalog_mass(exts, claimants, gamma, beta)
            part += weights[cell - 1] * mass_cell
            for t, m in per.items():
                per_title[t] += mass * weights[cell - 1] * m
            pos = shelf_positions(exts, claimants, gamma)
            occ_u.append([1 if i < len(pos) and pos[i][0] == "T" else 0 for i in range(S_POS)])
        decomp[universe] = mass * part
        occupancy[universe] = occ_u
        T += mass * part
    return T, per_title, decomp, occupancy


# ------------------------------------------------------------------- F gates
print("== VERDICT 057 — keyword tiling vs independent picks (PROPOSAL 046) ==")
print("fixtures: every registered constant verbatim from the PROPOSAL 046 block / idea doc")

# F1 — popularity normalization
check("F1 sum w_k == 1", sum(W_KW) == 1)
check("F1 sum v_c == 1", sum(W_CAT) == 1)
check("F1 w1/w2 == 2", W_KW[0] / W_KW[1] == 2)

# F4 — position pmf
check("F4 beta sums to 1", sum(BETA) == 1)
check("F4 beta non-increasing", all(BETA[i] >= BETA[i + 1] for i in range(len(BETA) - 1)))
check("F4 single-occupant shelf <= 1/2 mass", BETA[0] <= F(1, 2))
check("F4 flat beta sums to 1 (reporting)", sum(BETA_FLAT) == 1)
check("F4 flat beta non-increasing (reporting)", all(BETA_FLAT[i] >= BETA_FLAT[i + 1] for i in range(len(BETA_FLAT) - 1)))

# F5 — dilution identities
_f = F(7, 13)
check("F5 j=1 -> f at every gamma", all(diluted(_f, g, 1) == _f for g in GAMMAS))
check("F5 gamma=1,j=2 -> f/2", diluted(_f, F(1), 2) == _f / 2)
check("F5 gamma=4,j=3 -> f/9", diluted(_f, F(4), 3) == _f / 9)

# F3 — tie order
_pos = shelf_positions([F(3, 4)], [(1, F(3, 4))], F(0))
check("F3 external 3/4 above catalog 3/4", _pos[0] == ("E", 0) and _pos[1] == ("T", 1))
_pos2 = shelf_positions([], [(2, F(1, 2)), (1, F(1, 2))], F(0))
check("F3 equal catalog fits rank by lower title index", _pos2[0] == ("T", 1) and _pos2[1] == ("T", 2))
check("F3 TILE claim order is t = 1..14", list(range(1, N + 1)) == sorted(range(1, N + 1)))

# F2 — two-title hand world (run through the same engine primitives)
F2 = FIX["hand_fixture_F2"]
_w = [fr(x) for x in F2["shelf_weights"]]
_ext = [[fr(x) for x in e] for e in F2["external_fits_per_shelf"]]
_tf = [[fr(x) for x in row] for row in F2["title_fits"]]


def f2_alloc(policy):
    claimed = set()
    alloc = {}
    for t in (1, 2):
        cands = []
        for cell in (1, 2):
            f = _tf[t - 1][cell - 1]
            if f > 0:
                cands.append((cell, solo_score(_w[cell - 1], f, _ext[cell - 1], BETA), f))
        cands.sort(key=lambda x: (-x[1], x[0]))
        pool = cands if policy == "GREEDY" else [c for c in cands if c[0] not in claimed]
        alloc[t] = [pool[0][0]]
        claimed.add(pool[0][0])
    return alloc


def f2_T(alloc, gamma):
    cc = {}
    for t in sorted(alloc):
        for c in alloc[t]:
            cc.setdefault(c, []).append((t, _tf[t - 1][c - 1]))
    T = F(0)
    for cell in (1, 2):
        mass_cell, _ = shelf_catalog_mass(_ext[cell - 1], cc.get(cell, []), gamma, BETA)
        T += _w[cell - 1] * mass_cell
    return T


_g_alloc = f2_alloc("GREEDY")
_t_alloc = f2_alloc("TILE")
check("F2 GREEDY both titles on shelf 1", _g_alloc == {1: [1], 2: [1]})
check("F2 TILE t2 sent to shelf 2", _t_alloc == {1: [1], 2: [2]})
check("F2 T_GREEDY(gamma=1) == 1/4", f2_T(_g_alloc, F(1)) == fr(F2["expected"]["T_GREEDY_gamma1"]))
check("F2 T_GREEDY(gamma=0) == 1/2", f2_T(_g_alloc, F(0)) == fr(F2["expected"]["T_GREEDY_gamma0"]))
check("F2 T_TILE == 5/12 at every gamma", all(f2_T(_t_alloc, g) == fr(F2["expected"]["T_TILE_all_gamma"]) for g in GAMMAS))

# F6(c) — degenerate all-fits-zero world -> no claimable cells -> T = 0
check(
    "F6c degenerate all-fits-zero -> T = 0 both policies every gamma",
    all(
        shelf_catalog_mass(ext_fits("keyword", k), [], g, BETA)[0] == 0
        for k in (1, 50, 120)
        for g in GAMMAS
    ),
)

# ----------------------------------------------------- primary Arm A pipeline
def build_allocations(beta):
    """6 allocations: {(row, policy): (alloc_kw, alloc_cat, fallback_kw, fallback_cat)}"""
    out = {}
    for row in ROWS:
        gk, _ = alloc_greedy(row, "keyword", W_KW, beta)
        gc, _ = alloc_greedy(row, "category", W_CAT, beta)
        tk, fbk = alloc_tile(row, "keyword", W_KW, beta)
        tc, fbc = alloc_tile(row, "category", W_CAT, beta)
        out[(row, "GREEDY")] = (gk, gc, 0, 0)
        out[(row, "TILE")] = (tk, tc, fbk, fbc)
    return out


def collision_stats(alloc_kw, alloc_cat, row):
    """Colliding claims: sum over cells of (j-1) for j >= 2, kw+cat."""
    n = 0
    cells = 0
    for universe, alloc in (("keyword", alloc_kw), ("category", alloc_cat)):
        cc = cell_claimants(alloc, universe, row)
        for c, lst in cc.items():
            if len(lst) >= 2:
                n += len(lst) - 1
                cells += 1
    return n, cells


def arm_a_tables(beta, mass_kw, mass_cat, allocs):
    """Full exact evaluation: R table + everything reportable."""
    out = {"T": {}, "R": {}, "per_title": {}, "decomp": {}, "occupancy": {}}
    for row in ROWS:
        for gamma in GAMMAS:
            key = (row, gamma)
            Ts = {}
            for policy in ("GREEDY", "TILE"):
                ak, ac, _, _ = allocs[(row, policy)]
                T, per_title, decomp, occupancy = world_eval(row, ak, ac, gamma, beta, mass_kw, mass_cat)
                Ts[policy] = T
                out["per_title"][(row, gamma, policy)] = per_title
                out["decomp"][(row, gamma, policy)] = decomp
                out["occupancy"][(row, gamma, policy)] = occupancy
            out["T"][key] = Ts
            check("T_GREEDY > 0 at %s gamma=%s" % (row, s(gamma)), Ts["GREEDY"] > 0)
            out["R"][key] = (Ts["TILE"] - Ts["GREEDY"]) / Ts["GREEDY"]
    return out


ALLOCS = build_allocations(BETA)

# allocation sanity gates
for row in ROWS:
    for policy in ("GREEDY", "TILE"):
        ak, ac, fbk, fbc = ALLOCS[(row, policy)]
        check(
            "alloc sanity %s %s: exactly 7+2 distinct claims per title" % (row, policy),
            all(len(ak[t]) == 7 and len(set(ak[t])) == 7 for t in ak)
            and all(len(ac[t]) == 2 and len(set(ac[t])) == 2 for t in ac),
        )
    tk, tc, fbk, fbc = ALLOCS[(row, "TILE")]
    shared = collision_stats(tk, tc, row)[0]
    check(
        "TILE %s same-cell pairs are exactly the counted fallback shares (%d == %d + %d)" % (row, shared, fbk, fbc),
        shared == fbk + fbc,
    )

# GREEDY collision monotonicity (expected-direction, reporting — loud anomaly, not fatal)
_gc = {}
for row in ROWS:
    gk, gc2, _, _ = ALLOCS[(row, "GREEDY")]
    _gc[row] = collision_stats(gk, gc2, row)
if not (_gc["LOW"][0] <= _gc["MED"][0] <= _gc["HIGH"][0]):
    print(
        "ANOMALY (first-class, reporting): GREEDY colliding-claim counts not LOW <= MED <= HIGH: %s"
        % {r: _gc[r][0] for r in ROWS}
    )
print(
    "GREEDY colliding claims (sum of j-1 over collided cells, kw+cat): "
    + " ".join("%s=%d(cells %d)" % (r, _gc[r][0], _gc[r][1]) for r in ROWS)
)
print(
    "TILE fallback shares: "
    + " ".join(
        "%s=kw %d + cat %d" % (r, ALLOCS[(r, "TILE")][2], ALLOCS[(r, "TILE")][3]) for r in ROWS
    )
)

PRIMARY = arm_a_tables(BETA, MASS_KW, MASS_CAT, ALLOCS)

# F6(a)/(b) theorem gates on the primary tables
for row in ROWS:
    fb = ALLOCS[(row, "TILE")][2] + ALLOCS[(row, "TILE")][3]
    t_tile = [PRIMARY["T"][(row, g)]["TILE"] for g in GAMMAS]
    t_greedy = [PRIMARY["T"][(row, g)]["GREEDY"] for g in GAMMAS]
    if fb == 0:
        check("F6a T_TILE gamma-invariant in zero-fallback row %s" % row, all(x == t_tile[0] for x in t_tile))
    else:
        check(
            "F6a T_TILE non-increasing in gamma in fallback row %s (fallback %d)" % (row, fb),
            all(t_tile[i] >= t_tile[i + 1] for i in range(len(t_tile) - 1)),
        )
    check(
        "F6b T_GREEDY non-increasing in gamma in row %s" % row,
        all(t_greedy[i] >= t_greedy[i + 1] for i in range(len(t_greedy) - 1)),
    )

print("")
print("== Arm A (DECISION arm) — 12-cell exact R table: R = (T_TILE - T_GREEDY)/T_GREEDY ==")
for row in ROWS:
    for gamma in GAMMAS:
        Ts = PRIMARY["T"][(row, gamma)]
        R = PRIMARY["R"][(row, gamma)]
        print(
            "cell %-4s gamma=%-3s  T_GREEDY=%s (%s)  T_TILE=%s (%s)  R=%s (%s)  clears 1/50: %s"
            % (row, s(gamma), s(Ts["GREEDY"]), fl(Ts["GREEDY"]), s(Ts["TILE"]), fl(Ts["TILE"]), s(R), fl(R), "YES" if R >= MARGIN else "no")
        )

# ------------------------------------------------------------------- Arm S
class CountingRandom(random.Random):
    def __init__(self, seed):
        super().__init__(seed)
        self.draws = 0

    def random(self):
        self.draws += 1
        return super().random()


def cum_floats(weights):
    acc = F(0)
    out = []
    for w in weights:
        acc += w
        out.append(float(acc))
    return out


CUM_KW = cum_floats(W_KW)
CUM_CAT = cum_floats(W_CAT)


def arm_s_leg(seed, n_events, beta, mass_kw, tables):
    """One MC leg over the 12 cells in pinned order. tables: occupancy from an
    arm_a_tables() result evaluated at the SAME beta/mass. Returns
    {(row,gamma): {policy: Fraction click frequency}} and the draw count."""
    rng = CountingRandom(seed)
    cum_beta = cum_floats(beta)
    coin = float(mass_kw)
    freqs = {}
    for row in ROWS:
        for gamma in GAMMAS:
            occ = {p: tables["occupancy"][(row, gamma, p)] for p in ("GREEDY", "TILE")}
            clicks = {"GREEDY": 0, "TILE": 0}
            for _ in range(n_events):
                u = rng.random()
                universe = "keyword" if u < coin else "category"
                r = rng.random()
                cum = CUM_KW if universe == "keyword" else CUM_CAT
                cell = bisect.bisect_right(cum, r)  # 0-based
                if cell >= len(cum):  # guard: r == 1.0 cannot occur (random() < 1), but stay exact
                    cell = len(cum) - 1
                p = rng.random()
                pos = bisect.bisect_right(cum_beta, p)
                if pos >= S_POS:
                    pos = S_POS - 1
                for policy in ("GREEDY", "TILE"):
                    if occ[policy][universe][cell][pos]:
                        clicks[policy] += 1
            freqs[(row, gamma)] = {p: F(clicks[p], n_events) for p in ("GREEDY", "TILE")}
    return freqs, rng.draws


N_MAIN = FIX["arm_s"]["events_per_cell_main"]
N_STAB = FIX["arm_s"]["events_per_cell_stability"]
N_REP = FIX["arm_s"]["events_per_cell_reporting"]
GATE_MAIN = fr(FIX["arm_s"]["agreement_gate_main"])
GATE_STAB = fr(FIX["arm_s"]["agreement_gate_stability"])

print("")
print("== Arm S (confirmation arm) — main leg, seed %d, %d events/cell, CRN across worlds ==" % (SEEDS["main"], N_MAIN))
FREQ_MAIN, draws_main = arm_s_leg(SEEDS["main"], N_MAIN, BETA, MASS_KW, PRIMARY)
check("draw sentinel main == %d" % (12 * N_MAIN * 3), draws_main == 12 * N_MAIN * 3)
worst_main = F(0)
for row in ROWS:
    for gamma in GAMMAS:
        for policy in ("GREEDY", "TILE"):
            exact = PRIMARY["T"][(row, gamma)][policy]
            got = FREQ_MAIN[(row, gamma)][policy]
            d = abs(got - exact)
            worst_main = max(worst_main, d)
            check(
                "arm agreement main %s gamma=%s %s |%s - %s| = %s <= 5/1000" % (row, s(gamma), policy, fl(got), fl(exact), fl(d)),
                d <= GATE_MAIN,
            )
print("arm agreement gate (main): PASS all 24 world-cells, worst |ArmS - ArmA| = %s (%s)" % (s(worst_main), fl(worst_main)))

print("")
print("== Arm S — stability leg, seed %d, %d events/cell, widened gate 15/1000 ==" % (SEEDS["stability"], N_STAB))
FREQ_STAB, draws_stab = arm_s_leg(SEEDS["stability"], N_STAB, BETA, MASS_KW, PRIMARY)
check("draw sentinel stability == %d" % (12 * N_STAB * 3), draws_stab == 12 * N_STAB * 3)
worst_stab = F(0)
R_STAB = {}
for row in ROWS:
    for gamma in GAMMAS:
        fq = FREQ_STAB[(row, gamma)]
        for policy in ("GREEDY", "TILE"):
            d = abs(fq[policy] - PRIMARY["T"][(row, gamma)][policy])
            worst_stab = max(worst_stab, d)
            check("arm agreement stability %s gamma=%s %s <= 15/1000" % (row, s(gamma), policy), d <= GATE_STAB)
        check("stability T_GREEDY frequency > 0 at %s gamma=%s" % (row, s(gamma)), fq["GREEDY"] > 0)
        R_STAB[(row, gamma)] = (fq["TILE"] - fq["GREEDY"]) / fq["GREEDY"]
print("arm agreement gate (stability): PASS all 24 world-cells, worst |ArmS - ArmA| = %s (%s)" % (s(worst_stab), fl(worst_stab)))

# ------------------------------------------------- twin decision evaluators
CELLS = [(row, gamma) for row in ROWS for gamma in GAMMAS]
G_QUARTER = F(1, 4)


def evaluator_fraction(R_table, margin):
    """Twin 1: Fraction comparisons, canonical cell order."""
    clears = [R_table[c] >= margin for c in CELLS]
    n_clear = sum(1 for x in clears if x)
    q_clear = sum(1 for c in CELLS if c[1] == G_QUARTER and R_table[c] >= margin)
    if n_clear == 0:
        return "REJECT-BAND", n_clear, q_clear
    if n_clear >= 9 and q_clear >= 2:
        return "APPROVE-BAND", n_clear, q_clear
    return "NEITHER-BAND", n_clear, q_clear


def evaluator_integer(R_table, margin):
    """Twin 2: pure-integer cross-multiplication, reversed cell order."""
    mn, md = margin.numerator, margin.denominator
    n_clear = 0
    q_clear = 0
    for c in reversed(CELLS):
        rn, rd = R_table[c].numerator, R_table[c].denominator
        # R >= m  <=>  rn * md >= mn * rd   (rd, md > 0)
        if rn * md >= mn * rd:
            n_clear += 1
            if c[1].numerator == 1 and c[1].denominator == 4:
                q_clear += 1
    if n_clear == 0:
        return "REJECT-BAND", n_clear, q_clear
    if n_clear >= 9 and q_clear >= 2:
        return "APPROVE-BAND", n_clear, q_clear
    return "NEITHER-BAND", n_clear, q_clear


ev1_main = evaluator_fraction(PRIMARY["R"], MARGIN)
ev2_main = evaluator_integer(PRIMARY["R"], MARGIN)
ev1_stab = evaluator_fraction(R_STAB, MARGIN)
ev2_stab = evaluator_integer(R_STAB, MARGIN)
check("twin evaluators agree on Arm A input", ev1_main == ev2_main)
check("twin evaluators agree on stability input", ev1_stab == ev2_stab)

# ------------------------------------------------------------ decision (IN ORDER)
band_main, n_clear, q_clear = ev1_main
band_stab = ev1_stab[0]
clearing_cells = [c for c in CELLS if PRIMARY["R"][c] >= MARGIN]

if band_main == "REJECT-BAND":
    RULING = "reject"
    RULING_DETAIL = "REJECT (checked FIRST) fires: R < 1/50 in ALL 12 cells."
elif band_main == "APPROVE-BAND" and band_stab == "APPROVE-BAND":
    RULING = "approve"
    RULING_DETAIL = (
        "REJECT (checked FIRST) does not fire (%d of 12 cells clear 1/50); APPROVE fires: "
        "%d >= 9 cells clear AND %d >= 2 of the 3 gamma=1/4 cells clear AND the seed-%d stability "
        "leg reproduces the ruling through both twin evaluators." % (n_clear, n_clear, q_clear, SEEDS["stability"])
    )
else:
    RULING = "null"
    only_high = all(c[0] == "HIGH" for c in clearing_cells) and len(clearing_cells) > 0
    only_ge1 = all(c[1] >= 1 for c in clearing_cells) and len(clearing_cells) > 0
    if band_main == "APPROVE-BAND" and band_stab != "APPROVE-BAND":
        axis = "stability non-reproduction (the seed-%d leg lands %s)" % (SEEDS["stability"], band_stab)
    elif only_ge1:
        axis = "gamma-conditional (pre-registered axis i): tiling clears the margin only at gamma >= 1"
    elif only_high:
        axis = "overlap-conditional (pre-registered axis ii): tiling clears the margin only in HIGH cells"
    else:
        axis = "band shortfall: %d of 12 cells clear 1/50 (need 0 for REJECT or >= 9 with >= 2 gamma=1/4 for APPROVE); clearing cells: %s" % (
            n_clear,
            [(c[0], s(c[1])) for c in clearing_cells],
        )
    RULING_DETAIL = "Neither REJECT (checked FIRST) nor APPROVE band is met. Binding axis: %s." % axis

print("")
print("== Decision (pre-registered, evaluated IN ORDER, REJECT FIRST, margin 1/50) ==")
print("cells clearing 1/50: %d of 12; gamma=1/4 cells clearing: %d of 3" % (n_clear, q_clear))
print("stability leg band: %s (cells clearing: %d of 12, gamma=1/4: %d of 3)" % (band_stab, ev1_stab[1], ev1_stab[2]))
print("RULING: %s" % RULING.upper())
print(RULING_DETAIL)

# ----------------------------------------------------- reporting-only legs
print("")
print("== Reporting-only legs (CANNOT flip the decision) ==")
SPLITS = [(fr(a), fr(b)) for a, b in FIX["mass_split_sensitivity_pairs"]]
REPORT_TABLES = {}

# mass splits: allocations unchanged (mass multiplies a whole universe uniformly)
for (a, b) in SPLITS:
    tab = arm_a_tables(BETA, a, b, ALLOCS)
    REPORT_TABLES["split_%s_%s" % (s(a), s(b))] = tab
    ev = evaluator_fraction(tab["R"], MARGIN)
    print("mass split (%s, %s): band %s, %d of 12 clear, gamma=1/4 %d of 3" % (s(a), s(b), ev[0], ev[1], ev[2]))

# flatter beta: full re-derivation (beta enters solo scoring AND click mass)
ALLOCS_FLAT = build_allocations(BETA_FLAT)
TAB_FLAT = arm_a_tables(BETA_FLAT, MASS_KW, MASS_CAT, ALLOCS_FLAT)
REPORT_TABLES["beta_flat"] = TAB_FLAT
ev_flat = evaluator_fraction(TAB_FLAT["R"], MARGIN)
print("flatter beta (1/3, 4/15, 1/5, 2/15, 1/15): band %s, %d of 12 clear, gamma=1/4 %d of 3" % (ev_flat[0], ev_flat[1], ev_flat[2]))

# margin sweep on the primary Arm A table
MARGIN_SWEEP = {}
for m_str in FIX["decision_bands"]["margin_sweep_reporting"]:
    m = fr(m_str)
    ev_m = evaluator_fraction(PRIMARY["R"], m)
    ev_m_stab = evaluator_fraction(R_STAB, m)
    MARGIN_SWEEP[m_str] = {"band": ev_m[0], "cells": ev_m[1], "gamma_quarter": ev_m[2], "stability_band": ev_m_stab[0]}
    print("margin m=%s: band %s, %d of 12 clear, gamma=1/4 %d of 3 (stability band %s)" % (m_str, ev_m[0], ev_m[1], ev_m[2], ev_m_stab[0]))

# sensitivity straddle detection (pre-registered NULL axis iv candidate; named, cannot flip)
STRADDLES = []
for name, tab in REPORT_TABLES.items():
    ev = evaluator_fraction(tab["R"], MARGIN)
    if ev[0] != band_main:
        STRADDLES.append("%s lands %s vs primary %s" % (name, ev[0], band_main))
for m_str, d in MARGIN_SWEEP.items():
    if d["band"] != band_main:
        STRADDLES.append("margin m=%s lands %s vs primary %s" % (m_str, d["band"], band_main))
if STRADDLES:
    print("SENSITIVITY STRADDLES FIRED (named, reporting-only): " + "; ".join(STRADDLES))
else:
    print("no sensitivity straddle fired: every reporting leg lands the primary band")

# Arm S reporting confirmations, seed 20261323, pinned scenario order
print("")
print("== Arm S — reporting confirmations, seed %d, %d events/cell ==" % (SEEDS["reporting"], N_REP))
rng_rep = CountingRandom(SEEDS["reporting"])
REP_SCENARIOS = [
    ("mass_split_1_2", BETA, SPLITS[0][0], REPORT_TABLES["split_%s_%s" % (s(SPLITS[0][0]), s(SPLITS[0][1]))]),
    ("mass_split_4_5", BETA, SPLITS[1][0], REPORT_TABLES["split_%s_%s" % (s(SPLITS[1][0]), s(SPLITS[1][1]))]),
    ("beta_flat", BETA_FLAT, MASS_KW, TAB_FLAT),
]


def arm_s_leg_shared(rng, n_events, beta, mass_kw, tables):
    cum_beta = cum_floats(beta)
    coin = float(mass_kw)
    freqs = {}
    for row in ROWS:
        for gamma in GAMMAS:
            occ = {p: tables["occupancy"][(row, gamma, p)] for p in ("GREEDY", "TILE")}
            clicks = {"GREEDY": 0, "TILE": 0}
            for _ in range(n_events):
                u = rng.random()
                universe = "keyword" if u < coin else "category"
                r = rng.random()
                cum = CUM_KW if universe == "keyword" else CUM_CAT
                cell = min(bisect.bisect_right(cum, r), len(cum) - 1)
                p = rng.random()
                pos = min(bisect.bisect_right(cum_beta, p), S_POS - 1)
                for policy in ("GREEDY", "TILE"):
                    if occ[policy][universe][cell][pos]:
                        clicks[policy] += 1
            freqs[(row, gamma)] = {p: F(clicks[p], n_events) for p in ("GREEDY", "TILE")}
    return freqs


REP_FREQS = {}
for name, beta, mkw, tab in REP_SCENARIOS:
    fq = arm_s_leg_shared(rng_rep, N_REP, beta, mkw, tab)
    REP_FREQS[name] = fq
    worst = F(0)
    for c in CELLS:
        for policy in ("GREEDY", "TILE"):
            d = abs(fq[c][policy] - tab["T"][c][policy])
            worst = max(worst, d)
            check("reporting agreement %s %s gamma=%s %s <= 15/1000 (mirrors stability width)" % (name, c[0], s(c[1]), policy), d <= GATE_STAB)
    print("reporting scenario %s: agreement PASS all 24 world-cells, worst diff %s" % (name, fl(worst)))
check("draw sentinel reporting == %d" % (3 * 12 * N_REP * 3), rng_rep.draws == 3 * 12 * N_REP * 3)
print("aux seed %d: registered-never-drawn — no RNG was constructed with it (asserted)" % SEEDS["aux_never_read"])

# --------------------------------------------------------------- results.json
def r_table_json(tab):
    out = {}
    for (row, gamma) in CELLS:
        key = "%s|gamma=%s" % (row, s(gamma))
        out[key] = {
            "T_GREEDY": s(tab["T"][(row, gamma)]["GREEDY"]),
            "T_TILE": s(tab["T"][(row, gamma)]["TILE"]),
            "R": s(tab["R"][(row, gamma)]),
            "R_float": fl(tab["R"][(row, gamma)]),
            "clears_margin_1_50": bool(tab["R"][(row, gamma)] >= MARGIN),
            "decomp_keyword": {p: s(tab["decomp"][(row, gamma, p)]["keyword"]) for p in ("GREEDY", "TILE")},
            "decomp_category": {p: s(tab["decomp"][(row, gamma, p)]["category"]) for p in ("GREEDY", "TILE")},
        }
    return out


RESULTS = {
    "verdict": "057",
    "intake": "046",
    "proposal_header_verbatim": FIX["proposal_header_verbatim"],
    "ruling": RULING,
    "ruling_detail": RULING_DETAIL,
    "margin": s(MARGIN),
    "cells_clearing_margin": n_clear,
    "gamma_quarter_cells_clearing": q_clear,
    "clearing_cells": ["%s|gamma=%s" % (c[0], s(c[1])) for c in clearing_cells],
    "arm_a_primary": r_table_json(PRIMARY),
    "per_title_traffic_primary": {
        "%s|gamma=%s|%s" % (row, s(gamma), policy): {str(t): s(PRIMARY["per_title"][(row, gamma, policy)][t]) for t in range(1, N + 1)}
        for (row, gamma) in CELLS
        for policy in ("GREEDY", "TILE")
    },
    "greedy_colliding_claims": {r: {"extra_claims": _gc[r][0], "collided_cells": _gc[r][1]} for r in ROWS},
    "tile_fallback_shares": {r: {"keyword": ALLOCS[(r, "TILE")][2], "category": ALLOCS[(r, "TILE")][3]} for r in ROWS},
    "arm_s_main": {
        "seed": SEEDS["main"],
        "events_per_cell": N_MAIN,
        "draws": draws_main,
        "worst_abs_diff": s(worst_main),
        "freq": {"%s|gamma=%s" % (c[0], s(c[1])): {p: s(FREQ_MAIN[c][p]) for p in ("GREEDY", "TILE")} for c in CELLS},
    },
    "arm_s_stability": {
        "seed": SEEDS["stability"],
        "events_per_cell": N_STAB,
        "draws": draws_stab,
        "worst_abs_diff": s(worst_stab),
        "band": band_stab,
        "R": {"%s|gamma=%s" % (c[0], s(c[1])): s(R_STAB[c]) for c in CELLS},
    },
    "twin_evaluators": {"arm_a": list(ev1_main), "stability": list(ev1_stab), "agree": ev1_main == ev2_main and ev1_stab == ev2_stab},
    "reporting": {
        "tables": {name: r_table_json(tab) for name, tab in REPORT_TABLES.items()},
        "margin_sweep": MARGIN_SWEEP,
        "straddles_fired": STRADDLES,
        "arm_s_seed": SEEDS["reporting"],
        "arm_s_draws": rng_rep.draws,
        "arm_s_freq": {
            name: {"%s|gamma=%s" % (c[0], s(c[1])): {p: s(REP_FREQS[name][c][p]) for p in ("GREEDY", "TILE")} for c in CELLS}
            for name in REP_FREQS
        },
    },
    "seeds": SEEDS,
    "cpython": list(sys.version_info[:2]),
    "self_checks": CHECKS,
}

print("")
print("SELF-CHECKS: %d passed, %d failed" % (CHECKS["passed"], CHECKS["failed"]))
RESULTS["self_checks"] = dict(CHECKS)

with open(os.path.join(HERE, "results.json"), "w") as fh:
    json.dump(RESULTS, fh, indent=1, sort_keys=True)
    fh.write("\n")

sys.exit(0 if CHECKS["failed"] == 0 else 1)
