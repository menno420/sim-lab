#!/usr/bin/env python3
"""VERDICT 071 — noisy reciprocity (idea-engine PROPOSAL 060, INTAKE 060).

Hermetic, stdlib-only, deterministic. Reads ONLY its own fixtures.json.
Arm A (DECISION, seedless): exact fractions.Fraction Gaussian-elimination
       stationary solves — 4 grid eps x 256 ordered pairs — plus the eps = 0
       orbit-cycle evaluator and the eps = 1/2 degeneracy check.
Arm B (twin, seedless): independently-written Cramer/adjugate evaluator; must
       reproduce every Arm-A v(i,j) EXACTLY at every grid eps.
Arm R (seeded, REPORTING-ONLY, no statistical gate): finite-horizon tournament
       at eps = 1/100 — main seed 20261377 (T = 4000), stability 20261378
       (T = 1000), presentation shuffle 20261379; aux 20261380 NEVER read.
Pre-registered rule evaluated IN ORDER: REJECT -> INVALID -> APPROVE -> NULL.
Run: python3 noisy_reciprocity_sim.py   (from anywhere; paths self-anchor)
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


def F(s):
    return Fraction(s)


def fstr(x):
    """Canonical lowest-terms 'p/q' string (C7)."""
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    return "%d/%d" % (x.numerator, x.denominator)


# ---------------------------------------------------------------- fixtures
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

check("cpython-minor-pinned-3.11",
      sys.version_info[:2] == tuple(FX["cpython_minor_pinned"]))

SG = FX["stage_game"]
U = {(1, 1): F(SG["u_CC"]), (1, 0): F(SG["u_CD"]),
     (0, 1): F(SG["u_DC"]), (0, 0): F(SG["u_DD"])}
UINT = {k: int(v) for k, v in U.items()}
T_, R_, P_, S_ = F(SG["T"]), F(SG["R"]), F(SG["P"]), F(SG["S"])

# F1: PD preconditions
check("F1-pd-precondition-T>R>P>S", T_ > R_ > P_ > S_)
check("F1-pd-precondition-2R>T+S", 2 * R_ > T_ + S_)

# C1: states pinned (my executed, opp executed), C = 1, D = 0
STATES = [(1, 1), (1, 0), (0, 1), (0, 0)]
SIDX = {s: i for i, s in enumerate(STATES)}

# C1: rule index k -> bits (c_CC, c_CD, c_DC, c_DD)
RULES = [((k >> 3) & 1, (k >> 2) & 1, (k >> 1) & 1, k & 1) for k in range(16)]
check("F1-field-complete-16-distinct", sorted(set(RULES)) == sorted(
    [(a, b, c, d) for a in (0, 1) for b in (0, 1) for c in (0, 1) for d in (0, 1)]))

NAMED = {name: tuple(bits) for name, bits in FX["strategy_space"]["named_rules"].items()}
IDX = {name: RULES.index(bits) for name, bits in NAMED.items()}
check("F1-named-TFT-(1,0,1,0)", RULES[IDX["TFT"]] == (1, 0, 1, 0) and IDX["TFT"] == 10)
check("F1-named-WSLS-(1,0,0,1)", RULES[IDX["WSLS"]] == (1, 0, 0, 1) and IDX["WSLS"] == 9)
check("F1-named-ALLC-(1,1,1,1)", RULES[IDX["ALLC"]] == (1, 1, 1, 1) and IDX["ALLC"] == 15)
check("F1-named-ALLD-(0,0,0,0)", RULES[IDX["ALLD"]] == (0, 0, 0, 0) and IDX["ALLD"] == 0)
TFT, WSLS, ALLC, ALLD = IDX["TFT"], IDX["WSLS"], IDX["ALLC"], IDX["ALLD"]


def move(rule, a, b):
    """Intended move of a rule given last round's executed (my a, opp b)."""
    if a == 1 and b == 1:
        return rule[0]
    if a == 1 and b == 0:
        return rule[1]
    if a == 0 and b == 1:
        return rule[2]
    return rule[3]


GRID = [F(s) for s in FX["noise"]["grid_pinned_order"]]
GRID_STR = list(FX["noise"]["grid_pinned_order"])
DEC = F(FX["noise"]["decision_cell"])
DEC_STR = FX["noise"]["decision_cell"]
EPS_HALF = F(FX["noise"]["control_cells"]["degeneracy"])

GAP_FLOOR = F(FX["decision_constants"]["reject_gap_floor"])       # 2/5
ECHO_VAL = F(FX["decision_constants"]["echo_identity_value"])     # 9/4
WSLS_FLOOR = F(FX["decision_constants"]["wsls_selfplay_floor"])   # 14/5


# ---------------------------------------------------------------- chain builder
def transition(i, j, eps):
    """P[s][t]: 4x4 exact transition matrix of the executed-pair chain for
    ordered pair (row rule i, col rule j) at noise eps."""
    P = [[Fraction(0)] * 4 for _ in range(4)]
    for si, (a, b) in enumerate(STATES):
        mi = move(RULES[i], a, b)
        mj = move(RULES[j], b, a)
        for ti, (x, y) in enumerate(STATES):
            qx = (1 - eps) if x == mi else eps
            qy = (1 - eps) if y == mj else eps
            P[si][ti] = qx * qy
    return P


# ---------------------------------------------------------------- Arm A (C3)
def stationary_gauss(P):
    """Gaussian elimination on (P^T - I) with LAST row replaced by ones,
    RHS (0,0,0,1). Exact Fractions."""
    n = 4
    A = [[P[c][r] - (1 if r == c else 0) for c in range(n)] for r in range(n)]
    A[n - 1] = [Fraction(1)] * n
    rhs = [Fraction(0)] * (n - 1) + [Fraction(1)]
    M = [A[r][:] + [rhs[r]] for r in range(n)]
    for col in range(n):
        piv = None
        for r in range(col, n):
            if M[r][col] != 0:
                piv = r
                break
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [x - f * y for x, y in zip(M[r], M[col])]
    return [M[r][n] for r in range(n)]


# ---------------------------------------------------------------- Arm B (C4)
def _det(m):
    n = len(m)
    if n == 1:
        return m[0][0]
    total = Fraction(0)
    sign = 1
    for c in range(n):
        if m[0][c] != 0:
            minor = [row[:c] + row[c + 1:] for row in m[1:]]
            total += sign * m[0][c] * _det(minor)
        sign = -sign
    return total


def stationary_cramer(P):
    """Twin: all-ones normalization row FIRST, then rows 0..2 of (P^T - I)
    (row 3 dropped); Cramer with recursive cofactor determinants."""
    n = 4
    M = [[Fraction(1)] * n]
    for r in range(n - 1):
        M.append([P[c][r] - (1 if r == c else 0) for c in range(n)])
    rhs = [Fraction(1)] + [Fraction(0)] * (n - 1)
    d = _det(M)
    pi = []
    for k in range(n):
        Mk = [[rhs[r] if c == k else M[r][c] for c in range(n)] for r in range(n)]
        pi.append(_det(Mk) / d)
    return pi


def value_of(pi):
    return sum(pi[s] * U[STATES[s]] for s in range(4))


def value_of_col(pi):
    """Column-player accounting on the SAME chain states (a = row, b = col):
    the column player's payoff in state (a, b) is u(b, a)."""
    return sum(pi[s] * U[(STATES[s][1], STATES[s][0])] for s in range(4))


# ---------------------------------------------------------------- orbit (C5)
def orbit_value(i, j):
    """eps = 0: deterministic map from initial executed state (C,C); exact
    average of u over the limit cycle only (transient excluded)."""
    state = (1, 1)
    seen = {}
    seq = []
    while state not in seen:
        seen[state] = len(seq)
        seq.append(state)
        a, b = state
        state = (move(RULES[i], a, b), move(RULES[j], b, a))
    cyc = seq[seen[state]:]
    return Fraction(sum(U[s] for s in cyc), 1) / len(cyc)


# ---------------------------------------------------------------- solve grid
VA = {}     # VA[eps_str][i][j] exact value, Arm A
VB_OK = {}  # per-eps Arm B exact equality
F1_OK = {}
F4_OK = {}
for es, eps in zip(GRID_STR, GRID):
    tblA = [[None] * 16 for _ in range(16)]
    tblB_eq = True
    f1_ok = True
    piA_store = {}
    for i in range(16):
        for j in range(16):
            P = transition(i, j, eps)
            piA = stationary_gauss(P)
            piB = stationary_cramer(P)
            # F1 solve identities (exact)
            if not (all(p >= 0 for p in piA) and sum(piA) == 1):
                f1_ok = False
            resid = [sum(piA[s] * P[s][t] for s in range(4)) - piA[t] for t in range(4)]
            if any(r != 0 for r in resid):
                f1_ok = False
            if piA != piB:
                tblB_eq = False
            tblA[i][j] = value_of(piA)
            piA_store[(i, j)] = piA
    VA[es] = tblA
    VB_OK[es] = tblB_eq
    F1_OK[es] = f1_ok
    check("F1-solve-identities-eps-%s" % es, f1_ok)
    check("F6-armB-exact-equal-eps-%s" % es, tblB_eq)
    # F2 echo theorem at this eps
    piTT = piA_store[(TFT, TFT)]
    check("F2-echo-uniform-stationary-eps-%s" % es,
          piTT == [Fraction(1, 4)] * 4)
    check("F2-echo-v-9/4-eps-%s" % es, tblA[TFT][TFT] == ECHO_VAL)
    # F4 transpose conservation (all 256 ordered pairs, exact)
    f4_ok = True
    for i in range(16):
        for j in range(16):
            if value_of_col(piA_store[(j, i)]) != tblA[i][j]:
                f4_ok = False
    F4_OK[es] = f4_ok
    check("F4-transpose-conservation-eps-%s" % es, f4_ok)
    # F3 closed-form anchors at this eps
    e = eps
    a_allc = 3 * (1 - e) ** 2 + 5 * e * (1 - e) + e ** 2
    a_alld = (1 - e) ** 2 + 5 * e * (1 - e) + 3 * e ** 2
    a_dc = 5 * (1 - e) ** 2 + 3 * e * (1 - e) + e * (1 - e)
    check("F3-anchor-ALLC-ALLC-eps-%s" % es, tblA[ALLC][ALLC] == a_allc)
    check("F3-anchor-ALLD-ALLD-eps-%s" % es, tblA[ALLD][ALLD] == a_alld)
    check("F3-anchor-ALLD-ALLC-eps-%s" % es, tblA[ALLD][ALLC] == a_dc)

# F3 pinned references at the decision cell
refs = [F(s) for s in FX["gates"]["F3_anchors"]["reference_at_1_100"]]
check("F3-reference-29899/10000", VA[DEC_STR][ALLC][ALLC] == refs[0])
check("F3-reference-10299/10000", VA[DEC_STR][ALLD][ALLD] == refs[1])
check("F3-reference-49401/10000", VA[DEC_STR][ALLD][ALLC] == refs[2])

# F5: eps = 1/2 degeneracy — every pairwise value 9/4, uniform stationary
f5_ok = True
for i in range(16):
    for j in range(16):
        P = transition(i, j, EPS_HALF)
        piA = stationary_gauss(P)
        if piA != [Fraction(1, 4)] * 4 or value_of(piA) != ECHO_VAL:
            f5_ok = False
check("F5-eps-1/2-degeneracy-all-256-values-9/4", f5_ok)

# eps = 0 orbit table + hand anchors (F6)
V0 = [[orbit_value(i, j) for j in range(16)] for i in range(16)]
OA = FX["orbit_hand_anchors"]
check("F6-orbit-anchor-v0(TFT,ALLD)=1", V0[TFT][ALLD] == F(OA["v0_TFT_ALLD"]))
check("F6-orbit-anchor-v0(WSLS,ALLD)=1/2", V0[WSLS][ALLD] == F(OA["v0_WSLS_ALLD"]))
check("F6-orbit-anchor-v0(TFT,TFT)=3", V0[TFT][TFT] == F(OA["v0_TFT_TFT"]))
check("F6-orbit-anchor-v0(WSLS,WSLS)=3", V0[WSLS][WSLS] == F(OA["v0_WSLS_WSLS"]))


# ---------------------------------------------------------------- scores/ranks
def scores_of(tbl):
    return [sum(tbl[i][j] for j in range(16)) / 16 for i in range(16)]


def dense_ranks(scores):
    """C2: dense rank by exact comparison — 1 + #(distinct values > mine)."""
    distinct = sorted(set(scores), reverse=True)
    pos = {v: k + 1 for k, v in enumerate(distinct)}
    return [pos[s] for s in scores]


SCORES = {es: scores_of(VA[es]) for es in GRID_STR}
RANKS = {es: dense_ranks(SCORES[es]) for es in GRID_STR}
SCORES0 = scores_of(V0)
RANKS0 = dense_ranks(SCORES0)

GAP = {es: SCORES[es][WSLS] - SCORES[es][TFT] for es in GRID_STR}
GAP0 = SCORES0[WSLS] - SCORES0[TFT]


# ---------------------------------------------------------------- decision rule
def evaluate_token_1(V, scores, ranks, gates_all_pass):
    """Twin evaluator 1 (Arm-A tables), registered order REJECT->INVALID->APPROVE->NULL."""
    c_gap = (scores[DEC_STR][WSLS] - scores[DEC_STR][TFT]) >= GAP_FLOOR
    c_echo = all(V[es][TFT][TFT] == ECHO_VAL for es in GRID_STR)
    c_rank = all(ranks[es][TFT] > ranks[es][WSLS] for es in GRID_STR)
    c_wsls = V[DEC_STR][WSLS][WSLS] >= WSLS_FLOOR
    if c_gap and c_echo and c_rank and c_wsls:
        return "REJECT", {"gap": c_gap, "echo": c_echo, "rank": c_rank, "wsls_floor": c_wsls}
    if not gates_all_pass:
        return "INVALID", {"gap": c_gap, "echo": c_echo, "rank": c_rank, "wsls_floor": c_wsls}
    if ranks[DEC_STR][TFT] == 1 and all(ranks[es][TFT] <= ranks[es][WSLS] for es in GRID_STR):
        return "APPROVE", {"gap": c_gap, "echo": c_echo, "rank": c_rank, "wsls_floor": c_wsls}
    return "NULL", {"gap": c_gap, "echo": c_echo, "rank": c_rank, "wsls_floor": c_wsls}


def evaluate_token_2(gates_all_pass):
    """Twin evaluator 2: independently recomputes scores/ranks/values from a
    FRESH Cramer (Arm-B) pass and walks the registered order differently."""
    vb = {}
    for es, eps in zip(GRID_STR, GRID):
        t = {}
        for i in range(16):
            for j in range(16):
                t[(i, j)] = value_of(stationary_cramer(transition(i, j, eps)))
        vb[es] = t
    sc = {es: [sum(vb[es][(i, j)] for j in range(16)) / Fraction(16)
               for i in range(16)] for es in GRID_STR}
    rk = {}
    for es in GRID_STR:
        vals = sc[es]
        rk[es] = [1 + len(set(v for v in vals if v > vals[i])) for i in range(16)]
    reject = True
    if sc[DEC_STR][WSLS] - sc[DEC_STR][TFT] < GAP_FLOOR:
        reject = False
    for es in GRID_STR:
        if vb[es][(TFT, TFT)] != ECHO_VAL:
            reject = False
        if not rk[es][TFT] > rk[es][WSLS]:
            reject = False
    if vb[DEC_STR][(WSLS, WSLS)] < WSLS_FLOOR:
        reject = False
    if reject:
        return "REJECT"
    if not gates_all_pass:
        return "INVALID"
    approve = rk[DEC_STR][TFT] == 1
    for es in GRID_STR:
        if rk[es][TFT] > rk[es][WSLS]:
            approve = False
    if approve:
        return "APPROVE"
    return "NULL"


# ---------------------------------------------------------------- Arm R (seeded)
SEEDS = FX["seeds"]
CONSTRUCTED = []


class CountedRNG(object):
    def __init__(self, seed):
        CONSTRUCTED.append(seed)
        self._r = random.Random(seed)
        self.calls = 0

    def random(self):
        self.calls += 1
        return self._r.random()

    def shuffle(self, x):
        self._r.shuffle(x)


def play_game(i, j, T, eps, rng):
    """C6: round 1 both INTEND C; every round consumes exactly 2 uniforms
    (row first); executed = intended flipped iff draw < eps (strict)."""
    total_i = 0
    total_j = 0
    state = None
    for t in range(T):
        if t == 0:
            mi, mj = 1, 1
        else:
            a, b = state
            mi = move(RULES[i], a, b)
            mj = move(RULES[j], b, a)
        u1 = rng.random()
        u2 = rng.random()
        x = (1 - mi) if u1 < eps else mi
        y = (1 - mj) if u2 < eps else mj
        state = (x, y)
        total_i += UINT[(x, y)]
        total_j += UINT[(y, x)]
    return Fraction(total_i, T), Fraction(total_j, T)


ARM_R_EPS = F(FX["arm_r"]["eps"])
ARM_R_EPS_STR = FX["arm_r"]["eps"]
T_MAIN = FX["arm_r"]["T_main"]
T_STAB = FX["arm_r"]["T_stability"]
PAIRS = [(i, j) for i in range(16) for j in range(i, 16)]
check("armR-136-unordered-pairs", len(PAIRS) == 136)

rng_main = CountedRNG(SEEDS["main"])
arm_r_main = {}
for (i, j) in PAIRS:
    vi, vj = play_game(i, j, T_MAIN, ARM_R_EPS, rng_main)
    arm_r_main[(i, j)] = (vi, vj)
check("F6-armR-main-draw-sentinel-2T-per-game",
      rng_main.calls == len(PAIRS) * 2 * T_MAIN)

rng_stab = CountedRNG(SEEDS["stability"])
arm_r_stab = {}
for (i, j) in PAIRS:
    vi, vj = play_game(i, j, T_STAB, ARM_R_EPS, rng_stab)
    arm_r_stab[(i, j)] = (vi, vj)
check("F6-armR-stability-draw-sentinel-2T-per-game",
      rng_stab.calls == len(PAIRS) * 2 * T_STAB)

# C9: presentation shuffle — seed 20261379 read by presentation legs ONLY
rng_pres = CountedRNG(SEEDS["presentation"])
pres_order = ["%d-%d" % p for p in PAIRS]
rng_pres.shuffle(pres_order)

check("F6-aux-seed-20261380-never-read",
      SEEDS["aux_never_read"] not in CONSTRUCTED)
check("F6-constructed-seeds-pinned-order",
      CONSTRUCTED == list(SEEDS["pinned_construction_order"]))

# Arm R reporting: max |finite-horizon estimate - exact stationary value|
exact_dec = VA[ARM_R_EPS_STR]
max_dev_main = Fraction(0)
max_dev_pair = None
for (i, j) in PAIRS:
    vi, vj = arm_r_main[(i, j)]
    for est, exact, tag in ((vi, exact_dec[i][j], "row"), (vj, exact_dec[j][i], "col")):
        d = abs(est - exact)
        if d > max_dev_main:
            max_dev_main = d
            max_dev_pair = "%d-%d-%s" % (i, j, tag)


# ---------------------------------------------------------------- gates + ruling
GATES_ALL = (CHECKS["failed"] == 0)
token1, conj = evaluate_token_1(VA, SCORES, RANKS, GATES_ALL)
token2 = evaluate_token_2(GATES_ALL)
check("F6-twin-decision-evaluators-agree", token1 == token2)
GATES_ALL = (CHECKS["failed"] == 0)
RULING = token1

# NULL axis naming (reporting)
null_axis = None
if RULING == "NULL":
    if conj["rank"] and Fraction(0) < GAP[DEC_STR] < GAP_FLOOR:
        null_axis = "margin-straddle"
    elif RANKS["1/1000"][TFT] < RANKS["1/1000"][WSLS]:
        null_axis = "noise-floor-conditional"
    elif not conj["echo"]:
        null_axis = "echo-identity-failure-with-gates-passing"
    else:
        null_axis = "other"

# ------------------------------------------------- drafter comparison (NEVER gated)
DISCLOSED = {
    "v_WSLS_WSLS_grid": ["187188187/62500000", "737773/250000", "5553/2000", "1301/500"],
    "score_TFT_dec": "66320495249/30396000000",
    "score_WSLS_dec": "152492158669156561/57041072808000000",
    "gap_dec": "9345083308624553/19013690936000000",
    "rank_TFT": 10, "rank_WSLS": 5,
    "score_ALLD_dec": "597/200",
    "v_TFT_ALLD_dec": "510001/500000",
    "v_WSLS_ALLD_dec": "107/200",
    "orbit_gap": "1/12",
}
drafter_cmp = {
    "v_WSLS_WSLS_grid_match": [
        fstr(VA[es][WSLS][WSLS]) == d
        for es, d in zip(GRID_STR, DISCLOSED["v_WSLS_WSLS_grid"])],
    "score_TFT_dec_match": fstr(SCORES[DEC_STR][TFT]) == DISCLOSED["score_TFT_dec"],
    "score_WSLS_dec_match": fstr(SCORES[DEC_STR][WSLS]) == DISCLOSED["score_WSLS_dec"],
    "gap_dec_match": fstr(GAP[DEC_STR]) == DISCLOSED["gap_dec"],
    "ranks_match_all_grid": all(
        RANKS[es][TFT] == DISCLOSED["rank_TFT"] and RANKS[es][WSLS] == DISCLOSED["rank_WSLS"]
        for es in GRID_STR),
    "score_ALLD_dec_match": fstr(SCORES[DEC_STR][ALLD]) == DISCLOSED["score_ALLD_dec"],
    "ALLD_tops_every_noisy_table": all(RANKS[es][ALLD] == 1 for es in GRID_STR),
    "v_TFT_ALLD_dec_match": fstr(VA[DEC_STR][TFT][ALLD]) == DISCLOSED["v_TFT_ALLD_dec"],
    "v_WSLS_ALLD_dec_match": fstr(VA[DEC_STR][WSLS][ALLD]) == DISCLOSED["v_WSLS_ALLD_dec"],
    "orbit_gap_match": fstr(GAP0) == DISCLOSED["orbit_gap"],
}

# ------------------------------------------------- reporting tables
NICE = [i for i in range(16) if RULES[i][0] == 1]  # C8: c_CC = 1
nice_tables = {}
for es in GRID_STR:
    sc = [sum(VA[es][i][j] for j in NICE) / Fraction(len(NICE)) for i in NICE]
    rk = [1 + len(set(v for v in sc if v > sc[k])) for k in range(len(NICE))]
    nice_tables[es] = {
        "rules": ["%d" % i for i in NICE],
        "scores": [fstr(v) for v in sc],
        "scores_float": [repr(float(v)) for v in sc],
        "ranks": rk,
    }


def tbl_str(tbl):
    return [[fstr(tbl[i][j]) for j in range(16)] for i in range(16)]


results = {
    "verdict": {
        "class": RULING,
        "twin_tokens": [token1, token2],
        "null_axis": null_axis,
        "conjuncts": {
            "gap_ge_2/5_at_1/100": conj["gap"],
            "echo_9/4_every_grid_eps": conj["echo"],
            "rank_TFT_worse_than_WSLS_every_grid_eps": conj["rank"],
            "v_WSLS_WSLS_ge_14/5_at_1/100": conj["wsls_floor"],
        },
        "decision_numbers": {
            "score_TFT_dec": fstr(SCORES[DEC_STR][TFT]),
            "score_WSLS_dec": fstr(SCORES[DEC_STR][WSLS]),
            "gap_dec": fstr(GAP[DEC_STR]),
            "gap_dec_float": repr(float(GAP[DEC_STR])),
            "v_TFT_TFT_grid": [fstr(VA[es][TFT][TFT]) for es in GRID_STR],
            "v_WSLS_WSLS_dec": fstr(VA[DEC_STR][WSLS][WSLS]),
            "rank_TFT_grid": [RANKS[es][TFT] for es in GRID_STR],
            "rank_WSLS_grid": [RANKS[es][WSLS] for es in GRID_STR],
        },
    },
    "gates": {
        "F1_solve_identities_per_eps": {es: F1_OK[es] for es in GRID_STR},
        "F4_transpose_per_eps": {es: F4_OK[es] for es in GRID_STR},
        "F5_half_degeneracy": f5_ok,
        "F6_armB_exact_equal_per_eps": {es: VB_OK[es] for es in GRID_STR},
        "all_pass": GATES_ALL,
    },
    "tables": {
        es: {
            "values": tbl_str(VA[es]),
            "scores": [fstr(s) for s in SCORES[es]],
            "scores_float": [repr(float(s)) for s in SCORES[es]],
            "ranks": RANKS[es],
        } for es in GRID_STR
    },
    "orbit_eps0": {
        "values": tbl_str(V0),
        "scores": [fstr(s) for s in SCORES0],
        "ranks": RANKS0,
        "gap0": fstr(GAP0),
        "v0_TFT_TFT": fstr(V0[TFT][TFT]),
        "discontinuity_note": "v(TFT,TFT) = 3 at eps = 0 orbit vs exactly 9/4 for every grid eps > 0 — singular perturbation (reporting)",
    },
    "gap_vs_eps_curve": {
        "grid": GRID_STR,
        "gap": [fstr(GAP[es]) for es in GRID_STR],
        "gap_float": [repr(float(GAP[es])) for es in GRID_STR],
        "gap_orbit_eps0": fstr(GAP0),
        "below_2/5_at": [es for es in GRID_STR if GAP[es] < GAP_FLOOR],
    },
    "vs_ALLD_column": {
        "eps0_orbit": {"TFT": fstr(V0[TFT][ALLD]), "WSLS": fstr(V0[WSLS][ALLD])},
        "grid": {es: {"TFT": fstr(VA[es][TFT][ALLD]), "WSLS": fstr(VA[es][WSLS][ALLD])}
                 for es in GRID_STR},
    },
    "nice_subfield_reporting": nice_tables,
    "arm_r": {
        "role": "reporting-only — no statistical gate",
        "eps": ARM_R_EPS_STR,
        "main": {
            "seed": SEEDS["main"], "T": T_MAIN,
            "draw_count": rng_main.calls,
            "estimates": {"%d-%d" % p: [fstr(arm_r_main[p][0]), fstr(arm_r_main[p][1])]
                          for p in PAIRS},
            "max_abs_dev_from_exact": fstr(max_dev_main),
            "max_abs_dev_float": repr(float(max_dev_main)),
            "max_abs_dev_pair": max_dev_pair,
        },
        "stability": {
            "seed": SEEDS["stability"], "T": T_STAB,
            "draw_count": rng_stab.calls,
            "max_abs_dev_from_exact": fstr(max(
                max(abs(arm_r_stab[p][0] - exact_dec[p[0]][p[1]]),
                    abs(arm_r_stab[p][1] - exact_dec[p[1]][p[0]]))
                for p in PAIRS)),
        },
        "presentation_order_seed_20261379": pres_order,
    },
    "drafter_disclosed_comparison_NEVER_gated": drafter_cmp,
    "self_checks": {"passed": CHECKS["passed"], "failed": CHECKS["failed"],
                    "failures": FAILURES},
}

out_path = os.path.join(HERE, "results.json")
with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(results, fh, indent=1, sort_keys=True)
    fh.write("\n")

# ---------------------------------------------------------------- stdout summary
print("VERDICT 071 — noisy reciprocity (INTAKE 060)")
print("RULING: %s (twin tokens: %s / %s)" % (RULING, token1, token2))
print("conjuncts: gap>=2/5:%s echo-9/4:%s rank-inversion:%s wsls>=14/5:%s"
      % (conj["gap"], conj["echo"], conj["rank"], conj["wsls_floor"]))
print("gap at 1/100 = %s ~ %s" % (fstr(GAP[DEC_STR]), repr(float(GAP[DEC_STR]))))
print("gap curve: %s" % " ".join("%s:%s" % (es, repr(float(GAP[es]))) for es in GRID_STR))
print("v(TFT,TFT) grid: %s | orbit eps0: %s" %
      (" ".join(fstr(VA[es][TFT][TFT]) for es in GRID_STR), fstr(V0[TFT][TFT])))
print("v(WSLS,WSLS) grid: %s" % " ".join(fstr(VA[es][WSLS][WSLS]) for es in GRID_STR))
print("ranks TFT: %s | WSLS: %s | ALLD: %s" %
      ([RANKS[es][TFT] for es in GRID_STR],
       [RANKS[es][WSLS] for es in GRID_STR],
       [RANKS[es][ALLD] for es in GRID_STR]))
print("vs-ALLD at 1/100: TFT %s WSLS %s | orbit: TFT %s WSLS %s" %
      (fstr(VA[DEC_STR][TFT][ALLD]), fstr(VA[DEC_STR][WSLS][ALLD]),
       fstr(V0[TFT][ALLD]), fstr(V0[WSLS][ALLD])))
print("arm-R (reporting-only): max |est-exact| main = %s (pair %s), draws %d + %d"
      % (repr(float(max_dev_main)), max_dev_pair, rng_main.calls, rng_stab.calls))
print("drafter comparison (never gated): %s" %
      json.dumps(drafter_cmp, sort_keys=True))
print("SELF-CHECKS: %d passed, %d failed" % (CHECKS["passed"], CHECKS["failed"]))
if CHECKS["failed"]:
    print("FAILURES: %s" % FAILURES)
sys.exit(1 if CHECKS["failed"] else 0)
