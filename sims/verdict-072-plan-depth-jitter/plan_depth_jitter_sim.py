#!/usr/bin/env python3
"""VERDICT 072 — plan-depth refill jitter (idea-engine PROPOSAL 061, INTAKE 061).

Hermetic, stdlib-only, deterministic. Reads ONLY its own fixtures.json.
Arm A (DECISION, seedless): exact fractions.Fraction binomial tails +
       negative-binomial drained-span sums over the lag-pair lattice —
       full p_dry(S, q, mix) surface, safe-depth scan, span/arrival tables.
Arm B (twin, seedless): INDEPENDENTLY-WRITTEN queue-level DP event-walk
       stepping PR-by-PR through every published (pair, S, q) cell; must
       reproduce every Arm-A number EXACTLY.
Arm R (seeded, REPORTING-ONLY, no statistical gate): mechanism trace of the
       LITERAL counter/marker/trigger system at the decision cell — main
       seed 20261381 (N = 100,000 cycles), stability 20261382 (N = 20,000),
       presentation shuffle 20261383; aux 20261384 NEVER read (asserted).
Pre-registered rule evaluated IN ORDER: REJECT -> INVALID -> APPROVE -> NULL.
Run: python3 plan_depth_jitter_sim.py   (from anywhere; paths self-anchor)
"""

import json
import os
import random
import sys
from fractions import Fraction
from math import comb

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


F0, F1_ = Fraction(0), Fraction(1)


def fstr(x):
    """Canonical lowest-terms 'p/q' string (C7)."""
    x = Fraction(x)
    if x.denominator == 1:
        return str(x.numerator)
    return "%d/%d" % (x.numerator, x.denominator)


def ffl(x):
    """Float rendering via repr (C7)."""
    return repr(float(Fraction(x)))


# ---------------------------------------------------------------- fixtures
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

check("cpython-minor-pinned-3.11",
      sys.version_info[:2] == tuple(FX["cpython_minor_pinned"]))

K = int(FX["cadence"]["K"])
S_GRID = [int(s) for s in FX["S_grid"]]
S_DEC = int(FX["S_decision"])
Q_GRID = [F(s) for s in FX["q_grid"]]
Q_DEC = F(FX["q_decision"])
MIXES = {name: {int(l): F(p) for l, p in mix.items()}
         for name, mix in FX["lag_mixes"].items()}
MIX_NAMES = sorted(MIXES)  # canonical order: HEAVY, L0, PROMPT
MIX_DEC = FX["mix_decision"]
SAFE_LINE = F(FX["safe_depth_scan"]["line"])
S_LO, S_HI = int(FX["safe_depth_scan"]["S_lo"]), int(FX["safe_depth_scan"]["S_hi"])

check("fixture-K-30", K == 30)
check("fixture-decision-cell", S_DEC == 30 and Q_DEC == F("9/10") and MIX_DEC == "L0")

# ------------------------------------------------------- F1: model identities
for name in MIX_NAMES:
    mix = MIXES[name]
    check("F1-lag-pmf-sums-1-%s" % name, sum(mix.values()) == F1_)
    check("F1-single-band-support-%s" % name, all(0 <= l < K for l in mix))


def window_dist(mix, kk):
    """C1: exact window pmf {W: P(W)} over the i.i.d. lag pair."""
    wd = {}
    for lp, pp in mix.items():
        for lc, pc in mix.items():
            w = kk - lp + lc
            wd[w] = wd.get(w, F0) + pp * pc
    return wd


WDIST = {name: window_dist(MIXES[name], K) for name in MIX_NAMES}
for name in MIX_NAMES:
    check("F1-window-pmf-sums-1-%s" % name, sum(WDIST[name].values()) == F1_)
    check("F1-mean-window-conservation-%s" % name,
          sum(p * w for w, p in WDIST[name].items()) == K)


def trigger_walk_window(lp, lc, base, kk):
    """C5: direct event-walk of the VERBATIM committed trigger arithmetic.

    marker := landing count (the reset-to-latest convention); the next pass
    is due at the first count with  latest // kk > marker // kk  (verbatim
    `latest // STEP > marker // STEP`); it lands lc PRs later.
    """
    marker = kk * base + lp   # previous pass landed lp PRs after its crossing
    latest = marker
    while not (latest // kk > marker // kk):
        latest += 1
    crossing = latest
    landing = crossing + lc
    return landing - marker


_walk_ok = True
for name in MIX_NAMES:
    for lp in MIXES[name]:
        for lc in MIXES[name]:
            for base in (1, 33):
                if trigger_walk_window(lp, lc, base, K) != K - lp + lc:
                    _walk_ok = False
check("F1-trigger-walk-reproduces-window-law-every-pair-two-bases", _walk_ok)

# ------------------------------------------------------------------- Arm A
def binom_pmf(w, q, j):
    return Fraction(comb(w, j)) * q ** j * (1 - q) ** (w - j)


def pdry_A_W(w, s, q):
    """P(Bin(w, q) >= s + 1) exact (C3)."""
    if s + 1 > w:
        return F0
    return sum(binom_pmf(w, q, j) for j in range(s + 1, w + 1))


def span_A_W(w, s, q):
    """E[max(0, w - T_s)], T_s = arrival index of the s-th consuming PR (C3)."""
    if s == 0:
        return Fraction(w)
    if s > w:
        return F0
    return sum(Fraction(w - t) * Fraction(comb(t - 1, s - 1)) * q ** s
               * (1 - q) ** (t - s) for t in range(s, w + 1))


def arrivals_A_W(w, s, q):
    """E[max(0, Bin(w, q) - s)] exact (C3)."""
    if s + 1 > w:
        return F0
    return sum(Fraction(j - s) * binom_pmf(w, q, j) for j in range(s + 1, w + 1))


def agg_A(fn, mixname, s, q):
    return sum(p * fn(w, s, q) for w, p in sorted(WDIST[mixname].items()))


# binomial rows sum to 1 (F1) over every window in play at every grid q
_rows_ok = True
ALL_W = sorted(set(w for name in MIX_NAMES for w in WDIST[name]))
for q in Q_GRID:
    for w in ALL_W:
        if sum(binom_pmf(w, q, j) for j in range(w + 1)) != F1_:
            _rows_ok = False
check("F1-binomial-rows-sum-1-every-window-every-grid-q", _rows_ok)

# ------------------------------------------------------------------- Arm B
def cell_B(w, s, q):
    """C4: independently-written queue-level DP event-walk (twin).

    States: levels 1..s alive, ZERO (level 0, never dry-consumed), DRY
    (absorbing: at least one consuming arrival hit an empty queue).
    Walk the w PRs one by one carrying the exact state distribution.
    Returns (p_dry, E[drained span], E[dry consuming-arrivals]).
    """
    alive = {s: F1_} if s >= 1 else {0: F1_}
    dry = F0
    espan = F0
    earr = F0
    for _ in range(w):
        zero_like = alive.get(0, F0) + dry
        espan += zero_like            # queue empty at the start of this PR
        earr += q * zero_like         # a consuming arrival here is stranded
        new_alive = {}
        for lvl, p in alive.items():
            if lvl == 0:
                new_alive[0] = new_alive.get(0, F0) + p * (1 - q)
            else:
                new_alive[lvl - 1] = new_alive.get(lvl - 1, F0) + p * q
                new_alive[lvl] = new_alive.get(lvl, F0) + p * (1 - q)
        dry = dry + alive.get(0, F0) * q
        alive = new_alive
    return dry, espan, earr


def agg_B(mixname, s, q):
    pd = sp = ar = F0
    for w, p in sorted(WDIST[mixname].items()):
        d, e, a = cell_B(w, s, q)
        pd += p * d
        sp += p * e
        ar += p * a
    return pd, sp, ar


# --------------------------------------------------- the published surface
SURFACE = {}          # (mix, q, S) -> dict of exact metrics (Arm A)
_b_pdry_ok = _b_span_ok = _b_arr_ok = True
for name in MIX_NAMES:
    for q in Q_GRID:
        for s in S_GRID:
            pd = agg_A(pdry_A_W, name, s, q)
            sp = agg_A(span_A_W, name, s, q)
            ar = agg_A(arrivals_A_W, name, s, q)
            SURFACE[(name, q, s)] = {"p_dry": pd, "span": sp, "arrivals": ar}
            bpd, bsp, bar = agg_B(name, s, q)
            _b_pdry_ok &= (bpd == pd)
            _b_span_ok &= (bsp == sp)
            _b_arr_ok &= (bar == ar)
check("F6-armB-exact-equal-surface-p_dry-84-cells", _b_pdry_ok)
check("F6-armB-exact-equal-surface-span-84-cells", _b_span_ok)
check("F6-armB-exact-equal-surface-arrivals-84-cells", _b_arr_ok)

# --------------------------------------------------------- safe-depth scans
def scan_A(mixname, q):
    """C8: S*(q, mix) = min{S in [S_LO, S_HI] : p_dry(S) <= 1/100}, Arm A."""
    col = {}
    sstar = None
    for s in range(S_LO, S_HI + 1):
        col[s] = agg_A(pdry_A_W, mixname, s, q)
        if sstar is None and col[s] <= SAFE_LINE:
            sstar = s
    return sstar, col


SSTAR = {}            # (mix, q) -> (S*, bracket cells)
SCAN_COLS = {}        # decision-q columns published in full
_scan_found_all = True
_b_bracket_ok = True
for name in MIX_NAMES:
    for q in Q_GRID:
        sstar, col = scan_A(name, q)
        _scan_found_all &= (sstar is not None)
        below = col[sstar - 1] if sstar and sstar > S_LO else None
        SSTAR[(name, q)] = (sstar, below, col[sstar])
        if q == Q_DEC:
            SCAN_COLS[name] = col
        # F6: Arm B must reproduce both published bracket cells exactly
        bpd_at = agg_B(name, sstar, q)[0]
        _b_bracket_ok &= (bpd_at == col[sstar])
        if below is not None:
            _b_bracket_ok &= (agg_B(name, sstar - 1, q)[0] == below)
check("scan-S*-found-within-[0,60]-all-12-(q,mix)", _scan_found_all)
check("F6-armB-exact-equal-scan-bracket-cells-all-12", _b_bracket_ok)

# Arm-B twin scan at the decision q for all three mixes (powers evaluator 2)
SSTAR_B = {}
_b_scan_col_ok = True
for name in MIX_NAMES:
    sstar_b = None
    for s in range(S_LO, S_HI + 1):
        bpd = agg_B(name, s, Q_DEC)[0]
        _b_scan_col_ok &= (bpd == SCAN_COLS[name][s])
        if sstar_b is None and bpd <= SAFE_LINE:
            sstar_b = s
    SSTAR_B[name] = sstar_b
check("F6-armB-exact-equal-decision-q-scan-columns-3x61", _b_scan_col_ok)

# ------------------------------------------------- F2: forgiveness theorem
F2_LAGS = [int(c) for c in FX["gates"]["F2_constant_lags"]]
_f2_ok = True
F2_TABLE = {}
for c in F2_LAGS:
    for q in Q_GRID:
        # constant lag c: every window is exactly K
        pd_a = pdry_A_W(K, S_DEC, q)
        pd_b = cell_B(K, S_DEC, q)[0]
        F2_TABLE["c=%d|q=%s" % (c, fstr(q))] = pd_a
        _f2_ok &= (pd_a == F0 and pd_b == F0)
check("F2-forgiveness-p_dry(30)=0-every-constant-lag-every-grid-q", _f2_ok)

# ---------------------------------------------------- F3: the q = 1 identity
F3_REF = {name: F(v) for name, v in FX["gates"]["F3_reference"].items()}
_f3_ok = True
F3_VALS = {}
for name in MIX_NAMES:
    mix = MIXES[name]
    p_grew = sum(pp * pc for lp, pp in mix.items()
                 for lc, pc in mix.items() if lc > lp)
    pd_q1 = agg_A(pdry_A_W, name, S_DEC, F1_)
    F3_VALS[name] = pd_q1
    _f3_ok &= (pd_q1 == p_grew == F3_REF[name])
check("F3-q1-identity-p_dry=P(lag-grew)=references-all-mixes", _f3_ok)

# ------------------------------------------- F4: the committed-incident anchor
F4 = FX["gates"]["F4"]
f4_span_q = span_A_W(int(F4["constant_lag_window"]), int(F4["S"]), F(F4["q_band"]))
f4_span_1 = span_A_W(int(F4["constant_lag_window"]), int(F4["S"]), F(F4["q_exact"]))
check("F4-incident-span-S9-W30-q9/10-in-[18,22]",
      F(F4["band_lo"]) <= f4_span_q <= F(F4["band_hi"]))
check("F4-incident-span-S9-W30-q1-exactly-21", f4_span_1 == F(F4["exact_value_at_q1"]))
check("F6-armB-exact-equal-F4-cells",
      cell_B(30, 9, F("9/10"))[1] == f4_span_q and cell_B(30, 9, F1_)[1] == f4_span_1)

# ------------------------------------------------------- F5: the hand world
H = FX["gates"]["F5_hand_world"]
HK, HS, HQ = int(H["K"]), int(H["S"]), F(H["q"])
HMIX = {int(l): F(p) for l, p in H["lag_mix"].items()}
hwd = window_dist(HMIX, HK)
check("F5-hand-windows", hwd == {int(w): F(p) for w, p in H["windows"].items()})
check("F5-hand-tails",
      all(pdry_A_W(int(w), HS, HQ) == F(p) for w, p in H["tails"].items()))
hp_a = sum(p * pdry_A_W(w, HS, HQ) for w, p in sorted(hwd.items()))
hp_b = sum(p * cell_B(w, HS, HQ)[0] for w, p in sorted(hwd.items()))
check("F5-hand-p_dry-5/16-both-arms", hp_a == F(H["p_dry"]) == hp_b)
_hand_walk_ok = all(trigger_walk_window(lp, lc, base, HK) == HK - lp + lc
                    for lp in HMIX for lc in HMIX for base in (1, 33))
check("F5-hand-trigger-walk-matches-window-law", _hand_walk_ok)

# -------------------------------------------------------- decision numbers
PD_DEC_A = SURFACE[(MIX_DEC, Q_DEC, S_DEC)]["p_dry"]
SPANFRAC_DEC_A = SURFACE[(MIX_DEC, Q_DEC, S_DEC)]["span"] / K
SSTAR_DEC_A = SSTAR[(MIX_DEC, Q_DEC)][0]
ARR_DEC_A = SURFACE[(MIX_DEC, Q_DEC, S_DEC)]["arrivals"]

PD_DEC_B, SPAN_DEC_B, ARR_DEC_B = agg_B(MIX_DEC, S_DEC, Q_DEC)
SPANFRAC_DEC_B = SPAN_DEC_B / K
SSTAR_DEC_B = SSTAR_B[MIX_DEC]

BANDS = FX["decision_bands"]
REJ_PD = F(BANDS["REJECT"]["p_dry_min"])
REJ_SSTAR = int(BANDS["REJECT"]["S_star_min"])
REJ_SF = F(BANDS["REJECT"]["dry_span_fraction_min"])
APP_PD = F(BANDS["APPROVE"]["p_dry_max"])
APP_SSTAR = int(BANDS["APPROVE"]["S_star_max"])
APP_SF = F(BANDS["APPROVE"]["dry_span_fraction_max"])


def evaluate_token_1(pd, sstar, sf, gates_ok):
    """Registered rule, evaluator 1 (Arm-A numbers). Order: REJECT first."""
    if pd >= REJ_PD and sstar >= REJ_SSTAR and sf >= REJ_SF:
        return "REJECT"
    if not gates_ok:
        return "INVALID"
    if pd <= APP_PD and sstar <= APP_SSTAR and sf <= APP_SF:
        return "APPROVE"
    return "NULL"


def evaluate_token_2(pd, sstar, sf, gates_ok):
    """Registered rule, evaluator 2 (independently coded, Arm-B numbers)."""
    reject_conjuncts = [pd - REJ_PD >= 0, REJ_SSTAR - sstar <= 0, sf - REJ_SF >= 0]
    if False not in reject_conjuncts:
        return "REJECT"
    if gates_ok is not True:
        return "INVALID"
    approve_conjuncts = [APP_PD - pd >= 0, sstar - APP_SSTAR <= 0, APP_SF - sf >= 0]
    if False not in approve_conjuncts:
        return "APPROVE"
    return "NULL"


# --------------------------------------------------------------- Arm R (C6)
class CountedRNG:
    def __init__(self, seed):
        self._rng = random.Random(seed)
        self.count = 0

    def u(self):
        self.count += 1
        return self._rng.random()


SEEDS_CONSTRUCTED = []


def lag_from_u(u, mix):
    """Invert one uniform through the pinned lag cdf, ascending lag order."""
    uf = Fraction(u)
    cum = F0
    lags = sorted(mix)
    for lag in lags:
        cum += mix[lag]
        if uf < cum:
            return lag
    return lags[-1]


def arm_r_leg(seed, n_cycles, s, q, mixname, kk):
    """Mechanism trace of the LITERAL counter/marker/trigger system (C6)."""
    SEEDS_CONSTRUCTED.append(seed)
    rng = CountedRNG(seed)
    mix = MIXES[mixname]
    l_init = lag_from_u(rng.u(), mix)
    marker = kk * 31 + l_init
    dry_cycles = 0
    total_span = 0
    total_arr = 0
    total_w = 0
    for _ in range(n_cycles):
        latest = marker
        while not (latest // kk > marker // kk):   # verbatim due rule
            latest += 1
        crossing = latest
        lag = lag_from_u(rng.u(), mix)
        landing = crossing + lag
        w = landing - marker
        level = s                                   # order-up-to refill
        went_dry = False
        for _t in range(w):
            if level == 0:
                total_span += 1
            if Fraction(rng.u()) < q:               # strict <, consume
                if level == 0:
                    went_dry = True
                    total_arr += 1
                else:
                    level -= 1
        if went_dry:
            dry_cycles += 1
        total_w += w
        marker = landing                            # reset-to-latest
    return {
        "seed": seed, "N": n_cycles, "draws": rng.count,
        "expected_draws": 1 + n_cycles + total_w, "total_W": total_w,
        "p_dry_hat": Fraction(dry_cycles, n_cycles),
        "span_frac_hat": Fraction(total_span, kk * n_cycles),
        "arrivals_hat": Fraction(total_arr, n_cycles),
        "mean_W_hat": Fraction(total_w, n_cycles),
    }


AR = FX["arm_r"]
R_MAIN = arm_r_leg(int(AR["seed_main"]), int(AR["N_main"]), S_DEC, Q_DEC, MIX_DEC, K)
R_STAB = arm_r_leg(int(AR["seed_stability"]), int(AR["N_stability"]), S_DEC, Q_DEC,
                   MIX_DEC, K)
check("F6-armR-draw-sentinel-main", R_MAIN["draws"] == R_MAIN["expected_draws"])
check("F6-armR-draw-sentinel-stability", R_STAB["draws"] == R_STAB["expected_draws"])

# presentation shuffle (C9): row order of ONE stdout listing only
SEEDS_CONSTRUCTED.append(int(AR["seed_presentation"]))
_pres = random.Random(int(AR["seed_presentation"]))
PRES_ROWS = ["%s|q=%s|S=%d" % (name, fstr(q), s)
             for name in MIX_NAMES for q in Q_GRID for s in S_GRID]
_pres.shuffle(PRES_ROWS)

check("F6-aux-seed-20261384-never-read",
      int(AR["seed_aux_reserved_never_read"]) not in SEEDS_CONSTRUCTED)
check("F6-constructed-seeds-registry-pinned-order",
      SEEDS_CONSTRUCTED == [int(AR["seed_main"]), int(AR["seed_stability"]),
                            int(AR["seed_presentation"])])

# --------------------------------------------------------- gates + ruling
GATES_OK = (CHECKS["failed"] == 0)

TOKEN_1 = evaluate_token_1(PD_DEC_A, SSTAR_DEC_A, SPANFRAC_DEC_A, GATES_OK)
TOKEN_2 = evaluate_token_2(PD_DEC_B, SSTAR_DEC_B, SPANFRAC_DEC_B, GATES_OK)
check("F6-twin-decision-evaluators-agree", TOKEN_1 == TOKEN_2)
RULING = TOKEN_1

REJ_CONJ = {"p_dry>=1/20": bool(PD_DEC_A >= REJ_PD),
            "S*>=33": bool(SSTAR_DEC_A >= REJ_SSTAR),
            "span-fraction>=1/50": bool(SPANFRAC_DEC_A >= REJ_SF)}

# NULL-axis reporting (ungated, named)
NULL_AXES = {
    "band-straddle": bool(APP_PD < PD_DEC_A < REJ_PD or SSTAR_DEC_A in (31, 32)
                          or APP_SF < SPANFRAC_DEC_A < REJ_SF),
    "prompt-cell-inversion": bool(SURFACE[("PROMPT", Q_DEC, S_DEC)]["p_dry"] >= REJ_PD),
    "forgiveness-failure-without-gate-failure": bool(
        any(v != F0 for v in F2_TABLE.values()) and GATES_OK),
    "twin-arm-disagreement": bool(TOKEN_1 != TOKEN_2),
}

# --------------------------------------- drafter comparison (NEVER gated)
D = FX["drafter_disclosed_never_gated"]
ARR_PER_DRY_A = ARR_DEC_A / PD_DEC_A
DRAFTER_CMP = {
    "p_dry_decision_exact_match": fstr(PD_DEC_A) == D["p_dry_decision_cell"],
    "S_star_L0_match": SSTAR_DEC_A == int(D["S_star_L0"]),
    "scan_bracket_38_39_floats_match": (
        round(float(SCAN_COLS[MIX_DEC][38]), 6) == D["scan_bracket"]["p_dry_38"]
        and round(float(SCAN_COLS[MIX_DEC][39]), 6) == D["scan_bracket"]["p_dry_39"]),
    "dry_span_fraction_float_match":
        round(float(SPANFRAC_DEC_A), 6) == D["dry_span_fraction"],
    "PROMPT_p_dry_30_float_match":
        round(float(SURFACE[("PROMPT", Q_DEC, S_DEC)]["p_dry"]), 6)
        == D["PROMPT_p_dry_30"],
    "S_star_PROMPT_match": SSTAR[("PROMPT", Q_DEC)][0] == int(D["S_star_PROMPT"]),
    "S_star_HEAVY_match": SSTAR[("HEAVY", Q_DEC)][0] == int(D["S_star_HEAVY"]),
    "q_3_5_p_dry_30_approve_side_match":
        bool(SURFACE[(MIX_DEC, F("3/5"), S_DEC)]["p_dry"] < APP_PD),
    "S9_drained_span_approx_20":
        abs(float(SURFACE[(MIX_DEC, Q_DEC, 9)]["span"]) - D["S9_drained_span"]) < 0.5,
    "S9_dry_share_float_match":
        round(float(SURFACE[(MIX_DEC, Q_DEC, 9)]["p_dry"]), 7) == D["S9_dry_share"],
    "S20_dry_share_approx_match":
        round(float(SURFACE[(MIX_DEC, Q_DEC, 20)]["p_dry"]), 3) == D["S20_dry_share"],
    "arrivals_0.751_is_PER_CYCLE_unconditional":
        round(float(ARR_DEC_A), 3) == D["dry_consuming_arrivals_decision"],
    "arrivals_per_DRY_cycle_is_NOT_0.751":
        round(float(ARR_PER_DRY_A), 3) != D["dry_consuming_arrivals_decision"],
    "expected_landing_match": RULING == "REJECT"
        and D["expected_landing"] == "REJECT on all three conjuncts",
}

# ----------------------------------------------------------- results.json
def cellkey(name, q, s):
    return "%s|q=%s|S=%d" % (name, fstr(q), s)


RESULTS = {
    "verdict": "VERDICT 072",
    "intake": "INTAKE 061",
    "proposal_header": FX["_provenance"]["proposal_header_verbatim"],
    "ruling": RULING,
    "twin_tokens": [TOKEN_1, TOKEN_2],
    "reject_conjuncts": REJ_CONJ,
    "null_axes_report": NULL_AXES,
    "decision_cell": {
        "p_dry": fstr(PD_DEC_A), "p_dry_float": ffl(PD_DEC_A),
        "S_star": SSTAR_DEC_A,
        "dry_span_fraction": fstr(SPANFRAC_DEC_A),
        "dry_span_fraction_float": ffl(SPANFRAC_DEC_A),
        "drained_span": fstr(SURFACE[(MIX_DEC, Q_DEC, S_DEC)]["span"]),
        "dry_arrivals_per_cycle": fstr(ARR_DEC_A),
        "dry_arrivals_per_cycle_float": ffl(ARR_DEC_A),
        "dry_arrivals_per_dry_cycle": fstr(ARR_PER_DRY_A),
        "dry_arrivals_per_dry_cycle_float": ffl(ARR_PER_DRY_A),
    },
    "surface": {
        cellkey(name, q, s): {
            "p_dry": fstr(SURFACE[(name, q, s)]["p_dry"]),
            "p_dry_float": ffl(SURFACE[(name, q, s)]["p_dry"]),
            "drained_span": fstr(SURFACE[(name, q, s)]["span"]),
            "drained_span_float": ffl(SURFACE[(name, q, s)]["span"]),
            "dry_span_fraction": fstr(SURFACE[(name, q, s)]["span"] / K),
            "dry_arrivals": fstr(SURFACE[(name, q, s)]["arrivals"]),
        }
        for name in MIX_NAMES for q in Q_GRID for s in S_GRID
    },
    "safe_depth_table": {
        "%s|q=%s" % (name, fstr(q)): {
            "S_star": SSTAR[(name, q)][0],
            "p_dry_at_S_star_minus_1":
                (fstr(SSTAR[(name, q)][1]) if SSTAR[(name, q)][1] is not None
                 else None),
            "p_dry_at_S_star": fstr(SSTAR[(name, q)][2]),
            "p_dry_at_S_star_float": ffl(SSTAR[(name, q)][2]),
        }
        for name in MIX_NAMES for q in Q_GRID
    },
    "decision_q_scan_columns": {
        name: {str(s): fstr(SCAN_COLS[name][s]) for s in range(S_LO, S_HI + 1)}
        for name in MIX_NAMES
    },
    "F2_constant_lag_table": {k: fstr(v) for k, v in sorted(F2_TABLE.items())},
    "F3_q1_identity": {name: fstr(F3_VALS[name]) for name in MIX_NAMES},
    "F4_incident_anchor": {"span_S9_W30_q9/10": fstr(f4_span_q),
                           "span_S9_W30_q9/10_float": ffl(f4_span_q),
                           "span_S9_W30_q1": fstr(f4_span_1)},
    "F5_hand_world": {"p_dry": fstr(hp_a)},
    "mean_window": {name: fstr(sum(p * w for w, p in WDIST[name].items()))
                    for name in MIX_NAMES},
    "arm_r_reporting_only": {
        leg: {
            "seed": r["seed"], "N": r["N"], "draws": r["draws"],
            "p_dry_hat": fstr(r["p_dry_hat"]),
            "p_dry_abs_err_float": ffl(abs(r["p_dry_hat"] - PD_DEC_A)),
            "span_frac_hat": fstr(r["span_frac_hat"]),
            "span_frac_abs_err_float": ffl(abs(r["span_frac_hat"]
                                               - SPANFRAC_DEC_A)),
            "arrivals_hat": fstr(r["arrivals_hat"]),
            "mean_W_hat": fstr(r["mean_W_hat"]),
            "mean_W_abs_err_float": ffl(abs(r["mean_W_hat"] - K)),
        }
        for leg, r in (("main", R_MAIN), ("stability", R_STAB))
    },
    "seeds": {"constructed_in_order": SEEDS_CONSTRUCTED,
              "aux_never_read": int(AR["seed_aux_reserved_never_read"])},
    "drafter_comparison_never_gated": DRAFTER_CMP,
    "self_checks": {"passed": CHECKS["passed"], "failed": CHECKS["failed"],
                    "failures": FAILURES},
}

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8",
          newline="\n") as fh:
    json.dump(RESULTS, fh, indent=1, sort_keys=True)
    fh.write("\n")

# ---------------------------------------------------------- stdout summary
print("VERDICT 072 — plan-depth refill jitter (INTAKE 061)")
print("RULING: %s (twin tokens: %s / %s)" % (RULING, TOKEN_1, TOKEN_2))
print("conjuncts: %s" % " ".join("%s:%s" % (k, v) for k, v in REJ_CONJ.items()))
print("decision cell (S=30, q=9/10, L0): p_dry = %s ~ %s" % (fstr(PD_DEC_A),
                                                             ffl(PD_DEC_A)))
print("safe depth: S*(9/10, L0) = %d | bracket p_dry(38) = %s ~ %s | "
      "p_dry(39) = %s ~ %s" % (SSTAR_DEC_A, fstr(SCAN_COLS[MIX_DEC][38]),
                               ffl(SCAN_COLS[MIX_DEC][38]),
                               fstr(SCAN_COLS[MIX_DEC][39]),
                               ffl(SCAN_COLS[MIX_DEC][39])))
print("dry-span fraction = %s ~ %s | drained span = %s ~ %s PRs/cycle"
      % (fstr(SPANFRAC_DEC_A), ffl(SPANFRAC_DEC_A),
         fstr(SURFACE[(MIX_DEC, Q_DEC, S_DEC)]["span"]),
         ffl(SURFACE[(MIX_DEC, Q_DEC, S_DEC)]["span"])))
print("dry arrivals: %s ~ %s per cycle | %s ~ %s per DRY cycle"
      % (fstr(ARR_DEC_A), ffl(ARR_DEC_A), fstr(ARR_PER_DRY_A),
         ffl(ARR_PER_DRY_A)))
print("S* table (q=9/10): L0 = %d, PROMPT = %d, HEAVY = %d | q=1: L0 = %d"
      % (SSTAR[("L0", Q_DEC)][0], SSTAR[("PROMPT", Q_DEC)][0],
         SSTAR[("HEAVY", Q_DEC)][0], SSTAR[("L0", F1_)][0]))
print("PROMPT p_dry(30) = %s ~ %s (holds the committed bar: %s)"
      % (fstr(SURFACE[("PROMPT", Q_DEC, S_DEC)]["p_dry"]),
         ffl(SURFACE[("PROMPT", Q_DEC, S_DEC)]["p_dry"]),
         SURFACE[("PROMPT", Q_DEC, S_DEC)]["p_dry"] <= APP_PD))
print("q=3/5 p_dry(30, L0) = %s ~ %s (APPROVE-side: %s)"
      % (fstr(SURFACE[(MIX_DEC, F("3/5"), S_DEC)]["p_dry"]),
         ffl(SURFACE[(MIX_DEC, F("3/5"), S_DEC)]["p_dry"]),
         SURFACE[(MIX_DEC, F("3/5"), S_DEC)]["p_dry"] < APP_PD))
print("old worlds: S=9 dries %s ~ %s of cycles (span %s ~ %s) | S=20 dries "
      "%s ~ %s" % (fstr(SURFACE[(MIX_DEC, Q_DEC, 9)]["p_dry"]),
                   ffl(SURFACE[(MIX_DEC, Q_DEC, 9)]["p_dry"]),
                   fstr(SURFACE[(MIX_DEC, Q_DEC, 9)]["span"]),
                   ffl(SURFACE[(MIX_DEC, Q_DEC, 9)]["span"]),
                   fstr(SURFACE[(MIX_DEC, Q_DEC, 20)]["p_dry"]),
                   ffl(SURFACE[(MIX_DEC, Q_DEC, 20)]["p_dry"])))
print("theorems: F2 forgiveness zeros (all constant lags x grid q): %s | "
      "F3 q=1 identity %s | E[W]=30 on all mixes: %s"
      % (_f2_ok, " ".join("%s:%s" % (n, fstr(F3_VALS[n])) for n in MIX_NAMES),
         all(sum(p * w for w, p in WDIST[n].items()) == K for n in MIX_NAMES)))
print("F4 incident: span(S=9, W=30, q=9/10) = %s ~ %s in [18,22]; q=1: %s"
      % (fstr(f4_span_q), ffl(f4_span_q), fstr(f4_span_1)))
print("F5 hand world p_dry = %s" % fstr(hp_a))
print("arm-R (reporting-only): main |p_dry err| = %s, |span-frac err| = %s, "
      "draws %d; stability |p_dry err| = %s, draws %d"
      % (ffl(abs(R_MAIN["p_dry_hat"] - PD_DEC_A)),
         ffl(abs(R_MAIN["span_frac_hat"] - SPANFRAC_DEC_A)), R_MAIN["draws"],
         ffl(abs(R_STAB["p_dry_hat"] - PD_DEC_A)), R_STAB["draws"]))
print("null axes (report): %s" % json.dumps(NULL_AXES, sort_keys=True))
print("presentation-shuffled surface row order (seed 20261383): %s"
      % " ".join(PRES_ROWS[:6]) + " ...")
print("drafter comparison (never gated): %s"
      % json.dumps(DRAFTER_CMP, sort_keys=True))
print("SELF-CHECKS: %d passed, %d failed" % (CHECKS["passed"], CHECKS["failed"]))
sys.exit(1 if CHECKS["failed"] else 0)
