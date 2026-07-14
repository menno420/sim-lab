#!/usr/bin/env python3
"""VERDICT 064 — the healthcheck blind window (idea-engine PROPOSAL 053).

What does the websites repo's shipped 6-hourly point-probe liveness net
(cron "17 */6 * * *" — the T = 360 min cell) actually SEE of the pinned
transient-outage mix, and does the backlog's "up to 6 hours" hard window
survive the workflow's own delay-or-drop caveat once priced?

Pinned model (all integer minutes, all probabilities exact Fractions on
equiprobable integer lattices): probe cadence grid T in {60, 180, 360,
720, 1440}, fires scheduled at k*T, k = 0, 1, 2, ... (the wall-clock
minute-17 phase cancels under the uniform onset phase); per-fire delivery
noise: independent drop q = 1/20, delay d ~ uniform integer {0..30}
(sensitivity pairs q in {0, 1/10} and delay {0}/{0..60}, REPORTING ONLY);
transient outages D in {5, 30, 60, 180, 360} at onset phase phi ~ uniform
integer {0..T-1}, occupying [phi, phi+D), DETECTED iff some non-dropped
fire executes inside the window; persistent faults: L = earliest
successful execution at/after onset minus onset, WINDOW(T) = P(L > 360).

Arm A (DECISION, seedless, exact): full lattice enumeration — for each
(T, D) and each phi the exact product over the finitely many fires whose
delayed execution could intersect the window; every probability an exact
fractions.Fraction. The ruling rides Arm A alone. Independent second
structure at the shipped cell: full per-fire outcome enumeration
(({DROP} + {d = 0..30})^2 = 1024 outcomes per phi, exact integer weights)
must equal the product form on every DET(360, D) cell and WINDOW(360).

Arm B (VALIDATION, seeded MC): N = 200,000 scenario draws (u_phi, then
K = 9 pairs (u_drop, u_delay)), pinned draw order, COMMON RANDOM NUMBERS
across all five T cells. Agreement gate per reported cell (all 25
DET(T,D), all DET_mix(T) under the three registered mixes, all 5
WINDOW(T)): |EST - EXACT| <= 1/100 absolute AND <= 4*SE with
SE = sqrt(Var_exact/N) from Arm A. Any breach is INVALID.

Seeds (the ONLY four RNGs constructed, pinned order): 20261349 headline
MC / 20261350 zero-noise identity control (q = 0, d == 0: MISS(T,D) =
(T-D)/T for D <= T and 0 for D >= T, incl. MISS(360,180) = 1/2;
WINDOW(360) = 0; WINDOW(720) = 359/720 — asserted exactly in Arm A and
per-draw in Arm B) / 20261351 sensitivity reporting worlds (q-sweep under
common random numbers, delay {0} and {0..60}; N = 20,000 each; never
decision-bearing) / 20261352 stability leg (N = 20,000, ruling class
reproduced through twin independently-written decision evaluators).

Decision rule, registered, applied IN ORDER on Arm A exact Fractions at
the shipped cell T = 360 under the headline pins: REJECT first
(DET_mix(360) < 1/2 OR WINDOW(360) > 1/20), then INVALID (zero-noise
identities / monotonicity theorems (DET(T,D) non-decreasing in D at fixed
T; DET_mix(T) non-increasing in T; WINDOW(T) non-decreasing in q under
CRN) / agreement gate — every control is a hard self-check: failure exits
1 with no ruling), then APPROVE (DET_mix(360) >= 3/4 AND WINDOW(360) <=
1/100 AND stability reproduces), else NULL (pre-registered axes:
band-straddle; stability non-reproduction; sensitivity straddle — named,
never ruling). Reporting-only legs can NEVER flip the decision.

Hermetic: reads only its own fixtures.json. Stdlib only. No wall-clock in
any output. Byte-identical stdout + results.json across process runs.

Run: python3 sims/verdict-064-healthcheck-blind-window/healthcheck_blind_window_sim.py
"""

import json
import math
import os
import platform
import random
import sys
from fractions import Fraction

BASE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- self-checks
_CHECKS = {"passed": 0, "failed": 0}


def check(cond, label):
    if cond:
        _CHECKS["passed"] += 1
    else:
        _CHECKS["failed"] += 1
        print("SELF-CHECK FAIL: %s" % label)
        print("RULING: INVALID (control gate failed — report, no ruling)")
        sys.exit(1)


def Fr(d):
    return Fraction(d["num"], d["den"])


def fr(x):
    x = Fraction(x)
    return "%d/%d" % (x.numerator, x.denominator)


def fl(x):
    return "%.10g" % float(x)


def show(x):
    return "%s (%s)" % (fr(x), fl(x))


# ------------------------------------------------------------------- fixtures
with open(os.path.join(BASE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

MODEL = FX["model"]
T_GRID = MODEL["T_grid_minutes"]
D_GRID = MODEL["D_grid_minutes"]
T_SHIP = MODEL["T_shipped"]
WIN_THR = MODEL["window_threshold_minutes"]
Q_HEAD = Fr(MODEL["q_drop_headline"])
Q_SENS = [Fr(d) for d in MODEL["q_drop_sensitivity"]]
W_HEAD = MODEL["delay_support_headline"]["hi"]
W_SENS = [d["hi"] for d in MODEL["delay_support_sensitivity"]]
MIXES = {
    "equiprobable": [Fraction(w, MODEL["mix_headline"]["den"]) for w in MODEL["mix_headline"]["weights"]],
    "short_heavy": [Fraction(w, MODEL["mix_short_heavy"]["den"]) for w in MODEL["mix_short_heavy"]["weights"]],
    "long_heavy": [Fraction(w, MODEL["mix_long_heavy"]["den"]) for w in MODEL["mix_long_heavy"]["weights"]],
}
BANDS = FX["decision_rule"]["bands"]
B_REJ_DM = Fr(BANDS["reject_detmix_lt"])
B_REJ_W = Fr(BANDS["reject_window_gt"])
B_APP_DM = Fr(BANDS["approve_detmix_ge"])
B_APP_W = Fr(BANDS["approve_window_le"])
GATE_ABS = Fr(FX["agreement_gate"]["abs_tolerance"])
GATE_SE = FX["agreement_gate"]["se_multiplier"]
NS = FX["N"]
SEEDS = FX["seeds"]
KFIRE = FX["fixture_level_choices_disclosed_before_runner"]["K_fire_variates_per_scenario"]
SENTINEL = FX["fixture_level_choices_disclosed_before_runner"]["draw_sentinels"]
DRAFTER = FX["drafter_reference_never_gated"]

# transcription gates (registered constants, re-stated here independently)
check(T_GRID == [60, 180, 360, 720, 1440], "transcription: T grid")
check(D_GRID == [5, 30, 60, 180, 360], "transcription: D grid")
check(T_SHIP == 360 and WIN_THR == 360, "transcription: shipped cell + window threshold")
check(Q_HEAD == Fraction(1, 20) and Q_SENS == [Fraction(0), Fraction(1, 10)], "transcription: q pins")
check(W_HEAD == 30 and W_SENS == [0, 60], "transcription: delay pins")
check(sum(MIXES["equiprobable"]) == 1 and sum(MIXES["short_heavy"]) == 1 and sum(MIXES["long_heavy"]) == 1, "transcription: mixes normalized")
check(MIXES["short_heavy"] == [Fraction(w, 15) for w in [5, 4, 3, 2, 1]] and MIXES["long_heavy"] == [Fraction(w, 15) for w in [1, 2, 3, 4, 5]], "transcription: sensitivity mixes")
check(B_REJ_DM == Fraction(1, 2) and B_REJ_W == Fraction(1, 20) and B_APP_DM == Fraction(3, 4) and B_APP_W == Fraction(1, 100), "transcription: bands")
check(GATE_ABS == Fraction(1, 100) and GATE_SE == 4, "transcription: agreement gate")
check(sorted(SEEDS) == ["20261349", "20261350", "20261351", "20261352"], "transcription: seeds")
check(NS == {"headline": 200000, "stability": 20000, "sensitivity_per_world": 20000, "control": 20000}, "transcription: N values")
check(KFIRE == 9, "transcription: K fire variates")
check(Fr(FX["zero_noise_identities"]["MISS_360_180"]) == Fraction(1, 2) and Fr(FX["zero_noise_identities"]["WINDOW_360"]) == 0 and Fr(FX["zero_noise_identities"]["WINDOW_720"]) == Fraction(359, 720), "transcription: zero-noise identities")

# environment pin
check(platform.python_version_tuple()[:2] == ("3", "11"), "cpython 3.11 pinned (Arm B pin; Arm A is platform-independent exact rationals)")

# K coverage: no fire beyond index K-1 can reach any registered window
for T in T_GRID:
    check(KFIRE * T > (T - 1) + WIN_THR, "K coverage at T=%d" % T)

RESULTS = {}

# =====================================================================
# Arm A — DECISION (seedless, exact)
# =====================================================================


def surv(T, phi, x, q, W):
    """P(no successful execution in [phi, phi+x]) — exact product over fires k*T."""
    s = Fraction(1)
    M = W + 1
    k = 0
    one = Fraction(1)
    while k * T <= phi + x:
        lo = phi - k * T
        if lo < 0:
            lo = 0
        hi = phi + x - k * T
        if hi > W:
            hi = W
        if hi >= lo:
            s *= one - (one - q) * Fraction(hi - lo + 1, M)
        k += 1
    return s


# interval value vectors per mix: val[i] = sum of weights w_j with j >= i
MIXVALS = {}
for name, ws in MIXES.items():
    vals = []
    for i in range(6):
        vals.append(sum(ws[i:], Fraction(0)))
    MIXVALS[name] = vals

XCUTS = [D - 1 for D in D_GRID]  # survival abscissae 4,29,59,179,359


def world_exact(q, W):
    """Exact tables for one (q, W) world: DET, mixes (mean+var), WINDOW, interval pmf."""
    out = {"det": {}, "mix": {}, "mixvar": {}, "window": {}, "detvar": {}, "winvar": {}}
    for T in T_GRID:
        sv_sum = [Fraction(0)] * 5
        win_sum = Fraction(0)
        ex = {name: Fraction(0) for name in MIXES}
        ex2 = {name: Fraction(0) for name in MIXES}
        for phi in range(T):
            svs = [surv(T, phi, x, q, W) for x in XCUTS]
            for i in range(5):
                sv_sum[i] += svs[i]
            win_sum += surv(T, phi, WIN_THR, q, W)
            # interval pmf: i = #{D <= L_min}
            pmf = [1 - svs[0], svs[0] - svs[1], svs[1] - svs[2], svs[2] - svs[3], svs[3] - svs[4], svs[4]]
            for name in MIXES:
                vals = MIXVALS[name]
                for i in range(6):
                    ex[name] += pmf[i] * vals[i]
                    ex2[name] += pmf[i] * vals[i] * vals[i]
        dets = [1 - sv_sum[i] / T for i in range(5)]
        out["det"][T] = dets
        out["detvar"][T] = [p * (1 - p) for p in dets]
        w = win_sum / T
        out["window"][T] = w
        out["winvar"][T] = w * (1 - w)
        for name in MIXES:
            mean = ex[name] / T
            var = ex2[name] / T - mean * mean
            # internal consistency: E[X_w] must equal the weighted DET column
            check(mean == sum(MIXES[name][j] * dets[j] for j in range(5)), "mix mean == weighted DET column (T=%d, %s, q=%s, W=%d)" % (T, name, fr(q), W))
            out["mix"].setdefault(name, {})[T] = mean
            out["mixvar"].setdefault(name, {})[T] = var
    return out


WORLDS = {
    "headline": (Q_HEAD, W_HEAD),
    "q0_W30": (Q_SENS[0], W_HEAD),
    "q10_W30": (Q_SENS[1], W_HEAD),
    "q5_W0": (Q_HEAD, W_SENS[0]),
    "q5_W60": (Q_HEAD, W_SENS[1]),
    "zero_noise": (Fraction(0), 0),
}
EXACT = {name: world_exact(q, W) for name, (q, W) in WORLDS.items()}

HEAD = EXACT["headline"]
ZN = EXACT["zero_noise"]

# --- zero-noise identities (INVALID gates), Arm A ---
for ti, T in enumerate(T_GRID):
    for di, D in enumerate(D_GRID):
        miss = 1 - ZN["det"][T][di]
        expect = Fraction(T - D, T) if D <= T else Fraction(0)
        check(miss == expect, "zero-noise identity MISS(%d,%d) == %s" % (T, D, fr(expect)))
check(1 - ZN["det"][360][3] == Fraction(1, 2), "zero-noise identity MISS(360,180) == 1/2")
check(ZN["window"][360] == 0, "zero-noise identity WINDOW(360) == 0")
check(ZN["window"][720] == Fraction(359, 720), "zero-noise identity WINDOW(720) == 359/720")

# --- monotonicity theorems (INVALID gates), Arm A ---
for wname, ex in EXACT.items():
    for T in T_GRID:
        dets = ex["det"][T]
        check(all(dets[i] <= dets[i + 1] for i in range(4)), "monotonicity: DET(T=%d, D) non-decreasing in D [%s]" % (T, wname))
    for mname in MIXES:
        col = [ex["mix"][mname][T] for T in T_GRID]
        check(all(col[i] >= col[i + 1] for i in range(4)), "monotonicity: DET_mix(T) non-increasing in T [%s, %s]" % (wname, mname))
for T in T_GRID:
    w0 = EXACT["q0_W30"]["window"][T]
    w5 = EXACT["headline"]["window"][T]
    w10 = EXACT["q10_W30"]["window"][T]
    check(w0 <= w5 <= w10, "monotonicity: WINDOW(T=%d) non-decreasing in q (exact arm)" % T)

# --- independent second structure at the shipped cell: brute-force outcome enumeration ---


def brute_shipped():
    """Full enumeration over ({DROP} + {d})^2 outcomes of fires 0 and 1 at T=360,
    exact integer weights: DROP -> q*den, delay d -> (den-num) each, per-fire
    denominator q_den*(W+1). Only fires 0,1 can reach any registered window at
    T = 360 (fire 2 executes at >= 720 > (T-1) + 360 = 719)."""
    T = 360
    qn, qd = Q_HEAD.numerator, Q_HEAD.denominator
    M = W_HEAD + 1
    per_den = qd * M  # 620
    w_drop = qn * M  # 31
    w_exec = qd - qn  # 19 per delay value
    outcomes = [(w_drop, None)] + [(w_exec, d) for d in range(M)]
    den_total = T * per_den * per_den
    det_acc = [0] * 5
    win_acc = 0
    for phi in range(T):
        lim = phi + WIN_THR
        for w0, d0 in outcomes:
            e0 = d0 if d0 is not None else None
            for w1, d1 in outcomes:
                wgt = w0 * w1
                lmin = 10 ** 9
                if e0 is not None and e0 >= phi and e0 - phi < lmin:
                    lmin = e0 - phi
                if d1 is not None:
                    e1 = T + d1
                    if e1 >= phi and e1 - phi < lmin:
                        lmin = e1 - phi
                for j, D in enumerate(D_GRID):
                    if lmin < D:
                        det_acc[j] += wgt
                if lmin > WIN_THR:
                    win_acc += wgt
        del lim
    dets = [Fraction(a, den_total) for a in det_acc]
    win = Fraction(win_acc, den_total)
    return dets, win


BF_DETS, BF_WIN = brute_shipped()
for j, D in enumerate(D_GRID):
    check(BF_DETS[j] == HEAD["det"][360][j], "brute-force == product form: DET(360,%d)" % D)
check(BF_WIN == HEAD["window"][360], "brute-force == product form: WINDOW(360)")

# --- E[L] exact (reporting): first-catch decomposition with closed geometric tail ---


def expected_L(T, q, W):
    check(W < T, "E[L] ordering premise W < T (T=%d, W=%d)" % (T, W))
    tot = Fraction(0)
    M = W + 1
    tail_geo = T * q / (1 - q) if q else Fraction(0)
    for phi in range(T):
        prefix = Fraction(1)
        acc = Fraction(0)
        k = 0
        while True:
            if k * T >= phi:
                acc += prefix * ((k * T - phi + Fraction(W, 2)) + tail_geo)
                break
            lo = phi - k * T
            if lo <= W:
                m = W - lo + 1
                p = (1 - q) * Fraction(m, M)
                acc += prefix * p * Fraction(W - lo, 2)
                prefix *= 1 - p
            k += 1
        tot += acc
    return tot / T


EL_ROWS = {
    "zero_noise(q=0,d=0)": {T: expected_L(T, Fraction(0), 0) for T in T_GRID},
    "q=0,W=30": {T: expected_L(T, Fraction(0), W_HEAD) for T in T_GRID},
    "q=1/20,W=30": {T: expected_L(T, Q_HEAD, W_HEAD) for T in T_GRID},
    "q=1/10,W=30": {T: expected_L(T, Q_SENS[1], W_HEAD) for T in T_GRID},
}
# derived zero-noise closed form (model theorem): E[L] = (T-1)/2 — L(phi=0)=0 is
# forced by the registered WINDOW(720) = 359/720 identity (the onset-coincident
# fire counts). The REGISTERED sanity row says (T+1)/2: checked and reported as
# a drafter anomaly below, reporting-only, NOT an INVALID gate.
for T in T_GRID:
    check(EL_ROWS["zero_noise(q=0,d=0)"][T] == Fraction(T - 1, 2), "derived zero-noise E[L](T=%d) == (T-1)/2" % T)
    el0, el5, el10 = EL_ROWS["q=0,W=30"][T], EL_ROWS["q=1/20,W=30"][T], EL_ROWS["q=1/10,W=30"][T]
    check(el0 < el5 < el10, "E[L](T=%d) strictly increasing in q" % T)
EL_SANITY_REGISTERED_MATCHES = all(EL_ROWS["zero_noise(q=0,d=0)"][T] == Fraction(T + 1, 2) for T in T_GRID)

# --- per-phi conditional at the shipped cell (headline, reporting) ---
PER_PHI = []
for phi in range(T_SHIP):
    row = [1 - surv(T_SHIP, phi, x, Q_HEAD, W_HEAD) for x in XCUTS]
    PER_PHI.append(row)
# consistency: column means must equal the DET(360, D) cells
for j in range(5):
    check(sum(r[j] for r in PER_PHI) / T_SHIP == HEAD["det"][360][j], "per-phi column mean == DET(360,%d)" % D_GRID[j])

# --- decision numbers (Arm A alone), FROZEN before any RNG exists ---
DM_360 = HEAD["mix"]["equiprobable"][360]
W_360 = HEAD["window"][360]
ARM_A_FROZEN = (DM_360, W_360)


def twin_eval_fraction(dm, w, stability_ok):
    """Twin evaluator 1: Fraction comparisons, registered order (REJECT first;
    INVALID rides the hard self-checks; then APPROVE; else NULL)."""
    if dm < B_REJ_DM or w > B_REJ_W:
        return "REJECT"
    if dm >= B_APP_DM and w <= B_APP_W and stability_ok:
        return "APPROVE"
    return "NULL"


def twin_eval_int(dm_num, dm_den, w_num, w_den, stability_ok):
    """Twin evaluator 2: pure integer cross-multiplication, independently coded.
    Bands: dm < 1/2 | w > 1/20 -> REJECT; dm >= 3/4 & w <= 1/100 & stable -> APPROVE."""
    if 2 * dm_num < dm_den or 20 * w_num > w_den:
        return "REJECT"
    if 4 * dm_num >= 3 * dm_den and 100 * w_num <= w_den and stability_ok:
        return "APPROVE"
    return "NULL"


CLASS_A_1 = twin_eval_fraction(DM_360, W_360, True)
CLASS_A_2 = twin_eval_int(DM_360.numerator, DM_360.denominator, W_360.numerator, W_360.denominator, True)
check(CLASS_A_1 == CLASS_A_2, "twin evaluators agree on the Arm A class")
CLASS_A = CLASS_A_1

# =====================================================================
# Arm B — VALIDATION (seeded MC)
# =====================================================================


class CountingRandom(random.Random):
    def __init__(self, seed):
        super().__init__(seed)
        self.calls = 0

    def random(self):
        self.calls += 1
        return super().random()


RNG_ORDER = []


def make_rng(seed):
    RNG_ORDER.append(str(seed))
    return CountingRandom(seed)


INF = 10 ** 9


def draw_scenario(rng):
    u_phi = rng.random()
    fires = [(rng.random(), rng.random()) for _ in range(KFIRE)]
    return u_phi, fires


def eval_lmin(u_phi, fires, T, qf, W):
    """L_min = min{e - phi : e = k*T + d >= phi, fire not dropped, e <= phi+360-horizon};
    fires beyond the horizon cannot change any reported indicator."""
    phi = int(u_phi * T)
    M = W + 1
    lim = phi + WIN_THR
    lmin = INF
    for k in range(KFIRE):
        kT = k * T
        if kT > lim:
            break
        ud, ude = fires[k]
        if ud < qf:
            continue
        e = kT + int(ude * M)
        if phi <= e and e - phi < lmin:
            lmin = e - phi
    return phi, lmin


def interval_of(lmin):
    if lmin < 5:
        return 0
    if lmin < 30:
        return 1
    if lmin < 60:
        return 2
    if lmin < 180:
        return 3
    if lmin < 360:
        return 4
    return 5


def leg_accumulate(rng, N, qf, W):
    """Run N scenarios, all five T cells (CRN). Returns per-T interval counts + window counts."""
    cnt = {T: [0] * 6 for T in T_GRID}
    win = {T: 0 for T in T_GRID}
    for _ in range(N):
        u_phi, fires = draw_scenario(rng)
        for T in T_GRID:
            phi, lmin = eval_lmin(u_phi, fires, T, qf, W)
            cnt[T][interval_of(lmin)] += 1
            if lmin > WIN_THR:
                win[T] += 1
    return cnt, win


def estimates_from_counts(cnt, win, N):
    est = {"det": {}, "mix": {}, "window": {}}
    for T in T_GRID:
        c = cnt[T]
        est["det"][T] = [Fraction(sum(c[: j + 1]), N) for j in range(5)]
        est["window"][T] = Fraction(win[T], N)
        for name in MIXES:
            vals = MIXVALS[name]
            est["mix"].setdefault(name, {})[T] = sum(Fraction(c[i]) * vals[i] for i in range(6)) / N
    return est


GATE_LOG = []


def gate_cell(est, exact, var_exact, N, label):
    dev = abs(est - exact)
    se = math.sqrt(float(var_exact) / N)
    GATE_LOG.append((label, fr(est), fr(exact), fl(dev), fl(GATE_SE * se)))
    check(dev <= GATE_ABS, "agreement abs<=1/100: %s (dev %s)" % (label, fl(dev)))
    check(float(dev) <= GATE_SE * se, "agreement <=4*SE: %s (dev %s vs %s)" % (label, fl(dev), fl(GATE_SE * se)))


def gate_world(tag, est, ex, N):
    for T in T_GRID:
        for j, D in enumerate(D_GRID):
            gate_cell(est["det"][T][j], ex["det"][T][j], ex["detvar"][T][j], N, "%s DET(%d,%d)" % (tag, T, D))
        for name in MIXES:
            gate_cell(est["mix"][name][T], ex["mix"][name][T], ex["mixvar"][name][T], N, "%s DET_mix(%d) [%s]" % (tag, T, name))
        gate_cell(est["window"][T], ex["window"][T], ex["winvar"][T], N, "%s WINDOW(%d)" % (tag, T))


# ---- leg 1: headline (seed 20261349), N = 200,000, CRN across the T grid ----
rng_head = make_rng(20261349)
QF_HEAD = float(Q_HEAD)
cnt_h, win_h = leg_accumulate(rng_head, NS["headline"], QF_HEAD, W_HEAD)
check(rng_head.calls == SENTINEL["20261349"] == NS["headline"] * (1 + 2 * KFIRE), "draw sentinel seed 20261349 == %d" % SENTINEL["20261349"])
EST_HEAD = estimates_from_counts(cnt_h, win_h, NS["headline"])
gate_world("headline", EST_HEAD, HEAD, NS["headline"])

# ---- leg 2: zero-noise identity control (seed 20261350), per-draw exactness ----
rng_ctrl = make_rng(20261350)
Nc = NS["control"]
cnt_c = {T: [0] * 6 for T in T_GRID}
win_c = {T: 0 for T in T_GRID}
iden_det = {T: True for T in T_GRID}
iden_L = {T: True for T in T_GRID}
for _ in range(Nc):
    u_phi, fires = draw_scenario(rng_ctrl)
    for T in T_GRID:
        phi, lmin = eval_lmin(u_phi, fires, T, 0.0, 0)
        cnt_c[T][interval_of(lmin)] += 1
        if lmin > WIN_THR:
            win_c[T] += 1
        expect_L = 0 if phi == 0 else T - phi
        if expect_L <= WIN_THR:
            if lmin != expect_L:
                iden_L[T] = False
        else:
            if lmin <= WIN_THR:
                iden_L[T] = False
        for D in D_GRID:
            det_sim = lmin < D
            det_theory = (D >= T) or (phi == 0) or (phi > T - D)
            if det_sim != det_theory:
                iden_det[T] = False
check(rng_ctrl.calls == SENTINEL["20261350"] == Nc * (1 + 2 * KFIRE), "draw sentinel seed 20261350 == %d" % SENTINEL["20261350"])
for T in T_GRID:
    check(iden_det[T], "control per-draw transient identity, all scenarios (T=%d)" % T)
    check(iden_L[T], "control per-draw latency identity, all scenarios (T=%d)" % T)
EST_CTRL = estimates_from_counts(cnt_c, win_c, Nc)
gate_world("zero-noise-control", EST_CTRL, ZN, Nc)

# ---- leg 3: sensitivity worlds (seed 20261351), reporting-only ----
rng_sens = make_rng(20261351)
Nw = NS["sensitivity_per_world"]
# world (1): q-sweep at W = 30 under common random numbers (one scenario set,
# evaluated at q in {0, 1/20, 1/10} by thresholding the shared u_drop draws)
Q_SWEEP = [Q_SENS[0], Q_HEAD, Q_SENS[1]]
cnt_q = {fr(q): {T: [0] * 6 for T in T_GRID} for q in Q_SWEEP}
win_q = {fr(q): {T: 0 for T in T_GRID} for q in Q_SWEEP}
mono_crn = True
for _ in range(Nw):
    u_phi, fires = draw_scenario(rng_sens)
    for T in T_GRID:
        lmins = []
        for q in Q_SWEEP:
            phi, lmin = eval_lmin(u_phi, fires, T, float(q), W_HEAD)
            cnt_q[fr(q)][T][interval_of(lmin)] += 1
            if lmin > WIN_THR:
                win_q[fr(q)][T] += 1
            lmins.append(lmin)
        if not (lmins[0] <= lmins[1] <= lmins[2]):
            mono_crn = False
check(mono_crn, "CRN per-scenario monotonicity in q: L_min non-decreasing in q on every scenario x T")
for q, wname in [(Q_SWEEP[0], "q0_W30"), (Q_SWEEP[1], "headline"), (Q_SWEEP[2], "q10_W30")]:
    est = estimates_from_counts(cnt_q[fr(q)], win_q[fr(q)], Nw)
    gate_world("sens-q=%s" % fr(q), est, EXACT[wname], Nw)
    if wname == "q0_W30":
        EST_Q0 = est
    elif wname == "q10_W30":
        EST_Q10 = est
# MC-arm q-monotonicity of WINDOW estimates (guaranteed by the per-scenario CRN assert)
for T in T_GRID:
    check(win_q[fr(Q_SWEEP[0])][T] <= win_q[fr(Q_SWEEP[1])][T] <= win_q[fr(Q_SWEEP[2])][T], "monotonicity: WINDOW(T=%d) non-decreasing in q (MC arm, CRN)" % T)
# world (2): delay {0} at q = 1/20; world (3): delay {0..60} at q = 1/20
cnt_w0, win_w0 = leg_accumulate(rng_sens, Nw, QF_HEAD, W_SENS[0])
EST_W0 = estimates_from_counts(cnt_w0, win_w0, Nw)
gate_world("sens-W=0", EST_W0, EXACT["q5_W0"], Nw)
cnt_w60, win_w60 = leg_accumulate(rng_sens, Nw, QF_HEAD, W_SENS[1])
EST_W60 = estimates_from_counts(cnt_w60, win_w60, Nw)
gate_world("sens-W=60", EST_W60, EXACT["q5_W60"], Nw)
check(rng_sens.calls == SENTINEL["20261351"] == 3 * Nw * (1 + 2 * KFIRE), "draw sentinel seed 20261351 == %d" % SENTINEL["20261351"])

# ---- leg 4: stability (seed 20261352), N = 20,000, twin evaluators ----
rng_stab = make_rng(20261352)
Nst = NS["stability"]
cnt_s, win_s = leg_accumulate(rng_stab, Nst, QF_HEAD, W_HEAD)
check(rng_stab.calls == SENTINEL["20261352"] == Nst * (1 + 2 * KFIRE), "draw sentinel seed 20261352 == %d" % SENTINEL["20261352"])
EST_STAB = estimates_from_counts(cnt_s, win_s, Nst)
DM_STAB = EST_STAB["mix"]["equiprobable"][360]
W_STAB = EST_STAB["window"][360]
CLASS_S_1 = twin_eval_fraction(DM_STAB, W_STAB, True)
CLASS_S_2 = twin_eval_int(DM_STAB.numerator, DM_STAB.denominator, W_STAB.numerator, W_STAB.denominator, True)
check(CLASS_S_1 == CLASS_S_2, "twin evaluators agree on the stability-leg class")
STABILITY_REPRODUCES = CLASS_S_1 == CLASS_A

# seed-role audit
check(RNG_ORDER == ["20261349", "20261350", "20261351", "20261352"], "the ONLY four RNGs, constructed in pinned order")
check(ARM_A_FROZEN == (DM_360, W_360), "decision numbers frozen before any RNG existed (no seed feeds a decision number)")

# =====================================================================
# Ruling (registered order) + reporting
# =====================================================================
FINAL_1 = twin_eval_fraction(DM_360, W_360, STABILITY_REPRODUCES)
FINAL_2 = twin_eval_int(DM_360.numerator, DM_360.denominator, W_360.numerator, W_360.denominator, STABILITY_REPRODUCES)
check(FINAL_1 == FINAL_2 == CLASS_A, "final class stable through twin evaluators")
RULING = FINAL_1

REJ_C1 = DM_360 < B_REJ_DM
REJ_C2 = W_360 > B_REJ_W
STRADDLE_DM = B_REJ_DM <= DM_360 < B_APP_DM
STRADDLE_W = B_APP_W < W_360 <= B_REJ_W

# sensitivity straddles (named, never ruling): a reporting-only world landing a
# primary conjunct across a band edge relative to the headline side
SENS_STRADDLES = []
for wname in ["q0_W30", "q10_W30", "q5_W0", "q5_W60", "zero_noise"]:
    dmw = EXACT[wname]["mix"]["equiprobable"][360]
    ww = EXACT[wname]["window"][360]
    if (dmw < B_REJ_DM) != REJ_C1:
        SENS_STRADDLES.append("%s: DET_mix(360) = %s crosses the 1/2 edge (headline side: %s)" % (wname, show(dmw), "below" if REJ_C1 else "at/above"))
    if (ww > B_REJ_W) != REJ_C2:
        SENS_STRADDLES.append("%s: WINDOW(360) = %s crosses the 1/20 edge (headline side: %s)" % (wname, show(ww), "above" if REJ_C2 else "at/below"))

# drafter-reference comparison (never gated)
DRAFTER_CMP = {
    "DET_mix(360)": (DM_360, Fr(DRAFTER["DET_mix_360"])),
    "WINDOW(360)": (W_360, Fr(DRAFTER["WINDOW_360"])),
    "zero-noise DET_mix(360)": (ZN["mix"]["equiprobable"][360], Fr(DRAFTER["zero_noise_DET_mix_360"])),
    "zero-noise WINDOW(360)": (ZN["window"][360], Fr(DRAFTER["zero_noise_WINDOW_360"])),
}
for j, D in enumerate(D_GRID):
    DRAFTER_CMP["DET(360,%d)" % D] = (HEAD["det"][360][j], Fr(DRAFTER["DET_360_by_D"][str(D)]))

ANOMALIES = []
if not EL_SANITY_REGISTERED_MATCHES:
    ANOMALIES.append(
        "A1 (drafter, reporting-only): the registered zero-noise E[L] sanity row (T+1)/2 does NOT hold under the pinned model — "
        "the model forces E[L] = (T-1)/2 (verified exactly at every grid T). Proof of the drafter's internal inconsistency: the "
        "registered decision-side identity WINDOW(720) = 359/720 requires the onset-coincident fire to count (L(phi=0) = 0), "
        "which gives E[L] = (T-1)/2; the (T+1)/2 row would require it NOT to count, which would force WINDOW(720) = 360/720. "
        "The registered INVALID gates (MISS/WINDOW identities) hold exactly; only the reporting-row closed form is off by one."
    )
W60_EXACT = EXACT["headline"]["window"][60]
if abs(float(W60_EXACT) - DRAFTER["T60_WINDOW_approx"]) > DRAFTER["T60_WINDOW_approx"]:
    ANOMALIES.append(
        "A2 (drafter, reporting-only): the disclosed T=60 exhibit 'WINDOW ~ 3.7e-11' is off by three orders of magnitude — "
        "exact WINDOW(60) = %s = %s (~3.74e-08; the mantissa matches, the exponent does not). Direction of the falsifiability "
        "claim (WINDOW(60) tiny, far below every band) is unaffected." % (fr(W60_EXACT), fl(W60_EXACT))
    )
W0_WIN = EXACT["q5_W0"]["window"][360]
if B_APP_W < W0_WIN <= B_REJ_W:
    ANOMALIES.append(
        "A3 (finding, reporting-only): the delay-{0} sensitivity world lands WINDOW(360) = %s knife-edge BELOW the 1/20 REJECT "
        "edge (1/20 - %s = %s short) — with q = 1/20 but zero delay spread the 'up to 6 hours' claim just barely holds; the "
        "headline delay {0..30} pushes it over. A named sensitivity straddle, never ruling." % (show(W0_WIN), fr(B_REJ_W - W0_WIN), fl(B_REJ_W - W0_WIN))
    )

# ------------------------------------------------------------------ stdout
print("VERDICT 064 — the healthcheck blind window (idea-engine PROPOSAL 053)")
print("Arm A (DECISION, exact, seedless) — headline pins q = 1/20, d ~ uniform{0..30}")
print()
print("DET(T, D) table (exact Fractions; rows T, cols D; runs/day = 1440/T):")
hdr = "T\\D      " + "".join("%-24s" % ("D=%d" % D) for D in D_GRID) + "DET_mix(equi)           WINDOW(T)               runs/day"
print(hdr)
for T in T_GRID:
    row = "T=%-6d " % T
    for j in range(5):
        row += "%-24s" % show(HEAD["det"][T][j])
    row += "%-24s" % show(HEAD["mix"]["equiprobable"][T])
    row += "%-24s" % show(HEAD["window"][T])
    row += fr(Fraction(1440, T))
    print(row)
print()
print("Mixes at the shipped cell T=360: equiprobable %s | short-heavy %s | long-heavy %s" % (show(HEAD["mix"]["equiprobable"][360]), show(HEAD["mix"]["short_heavy"][360]), show(HEAD["mix"]["long_heavy"][360])))
print()
print("E[L] per T x q (exact; minutes):")
for rname, row in EL_ROWS.items():
    print("  %-22s " % rname + "  ".join("T=%d: %s" % (T, show(row[T])) for T in T_GRID))
print("  derived zero-noise closed form: E[L] = (T-1)/2 at every grid T; registered sanity row (T+1)/2 matches: %s" % EL_SANITY_REGISTERED_MATCHES)
print()
print("Sensitivity worlds at the shipped cell T=360 (exact, reporting-only):")
for wname in ["q0_W30", "q10_W30", "q5_W0", "q5_W60", "zero_noise"]:
    ex = EXACT[wname]
    print("  %-12s DET_mix(360) = %-24s WINDOW(360) = %s" % (wname, show(ex["mix"]["equiprobable"][360]), show(ex["window"][360])))
print()
print("Arm B (seeded MC, CRN) — agreement gates: %d cells gated, all passed (|EST-EXACT| <= 1/100 AND <= 4*SE)" % (len(GATE_LOG)))
worst = max(GATE_LOG, key=lambda g: float(g[3]))
print("  worst absolute deviation: %s dev=%s (allowance 1/100 and 4SE=%s)" % (worst[0], worst[3], worst[4]))
print("  headline (seed 20261349, N=200000): DET_mix(360) est %s exact %s | WINDOW(360) est %s exact %s" % (show(EST_HEAD["mix"]["equiprobable"][360]), fr(DM_360), show(EST_HEAD["window"][360]), fr(W_360)))
print("  zero-noise control (seed 20261350, N=20000): per-draw transient + latency identities exact on every scenario x T")
print("  sensitivity (seed 20261351, 3 worlds x N=20000): q-sweep under CRN with per-scenario q-monotonicity exact; delay {0} and {0..60} worlds gated")
print("  stability (seed 20261352, N=20000): DET_mix(360) est %s | WINDOW(360) est %s -> class %s through both twin evaluators; reproduces Arm A class: %s" % (show(DM_STAB), show(W_STAB), CLASS_S_1, STABILITY_REPRODUCES))
print("  draw sentinels: 20261349=%d 20261350=%d 20261351=%d 20261352=%d (exact)" % (SENTINEL["20261349"], SENTINEL["20261350"], SENTINEL["20261351"], SENTINEL["20261352"]))
print()
print("Drafter-reference comparison (never gated):")
AGREE_ALL = True
for k in sorted(DRAFTER_CMP):
    mine, theirs = DRAFTER_CMP[k]
    eq = mine == theirs
    AGREE_ALL = AGREE_ALL and eq
    print("  %-26s computed %-22s drafter %-22s exact-equal: %s" % (k, fr(mine), fr(theirs), eq))
print("  all disclosed exact Fractions reproduce: %s" % AGREE_ALL)
print("  approx exhibits: T=60 DET_mix computed %s (drafter ~0.685) | T=60 WINDOW computed %s (drafter ~3.7e-11: see anomaly A2) | q=0,W=30 WINDOW(360) computed %s (drafter ~0.013)" % (fl(HEAD["mix"]["equiprobable"][60]), fl(W60_EXACT), fl(EXACT["q0_W30"]["window"][360])))
print()
print("Anomalies (first-class, reporting-only):")
if ANOMALIES:
    for a in ANOMALIES:
        print("  - " + a)
else:
    print("  - none")
print()
print("Decision (Arm A exact Fractions alone, registered order REJECT -> INVALID -> APPROVE -> NULL):")
print("  DET_mix(360) = %s ; < 1/2: %s" % (show(DM_360), REJ_C1))
print("  WINDOW(360)  = %s ; > 1/20: %s" % (show(W_360), REJ_C2))
print("  band-straddle axis (reporting): DET_mix in [1/2,3/4): %s ; WINDOW in (1/100,1/20]: %s" % (STRADDLE_DM, STRADDLE_W))
print("  sensitivity straddles (named, never ruling):")
for s in SENS_STRADDLES:
    print("    * " + s)
print()
print("RULING: %s" % RULING)
print("SELF-CHECKS: %d passed, %d failed" % (_CHECKS["passed"], _CHECKS["failed"]))

# ------------------------------------------------------------------ results.json
def frs(x):
    return fr(x)


RESULTS = {
    "verdict": "VERDICT 064",
    "proposal": "PROPOSAL 053",
    "environment": {"python": ".".join(platform.python_version_tuple()[:2]), "note": "Arm A platform-independent exact rationals; Arm B pinned to this CPython minor"},
    "ruling": RULING,
    "decision": {
        "DET_mix_360": frs(DM_360),
        "WINDOW_360": frs(W_360),
        "reject_conjunct_detmix_lt_half": REJ_C1,
        "reject_conjunct_window_gt_one_twentieth": REJ_C2,
        "band_straddle_detmix": STRADDLE_DM,
        "band_straddle_window": STRADDLE_W,
        "stability_reproduces": STABILITY_REPRODUCES,
        "twin_evaluator_classes": {"arm_A": [CLASS_A_1, CLASS_A_2], "stability": [CLASS_S_1, CLASS_S_2]},
    },
    "arm_A": {
        wname: {
            "q": frs(WORLDS[wname][0]),
            "delay_hi": WORLDS[wname][1],
            "DET": {str(T): [frs(x) for x in EXACT[wname]["det"][T]] for T in T_GRID},
            "DET_mix": {mname: {str(T): frs(EXACT[wname]["mix"][mname][T]) for T in T_GRID} for mname in MIXES},
            "WINDOW": {str(T): frs(EXACT[wname]["window"][T]) for T in T_GRID},
        }
        for wname in WORLDS
    },
    "runs_per_day": {str(T): frs(Fraction(1440, T)) for T in T_GRID},
    "E_L_minutes": {rname: {str(T): frs(v) for T, v in row.items()} for rname, row in EL_ROWS.items()},
    "E_L_zero_noise_derived_closed_form": "(T-1)/2",
    "E_L_registered_sanity_row_matches": EL_SANITY_REGISTERED_MATCHES,
    "per_phi_DET_360": [[frs(x) for x in row] for row in PER_PHI],
    "brute_force_shipped_cell": {"DET_360": [frs(x) for x in BF_DETS], "WINDOW_360": frs(BF_WIN), "equals_product_form": True},
    "arm_B": {
        "headline_seed_20261349": {"N": NS["headline"], "DET_mix_360_est": frs(EST_HEAD["mix"]["equiprobable"][360]), "WINDOW_360_est": frs(EST_HEAD["window"][360]), "interval_counts": {str(T): cnt_h[T] for T in T_GRID}, "window_counts": {str(T): win_h[T] for T in T_GRID}},
        "control_seed_20261350": {"N": NS["control"], "per_draw_identities_exact": True},
        "sensitivity_seed_20261351": {"N_per_world": Nw, "worlds": ["q-sweep {0,1/20,1/10} @ W=30 (CRN)", "W=0 @ q=1/20", "W=60 @ q=1/20"], "crn_q_monotonicity_exact": True},
        "stability_seed_20261352": {"N": Nst, "DET_mix_360_est": frs(DM_STAB), "WINDOW_360_est": frs(W_STAB), "class": CLASS_S_1},
        "agreement_gates": {"cells_gated": len(GATE_LOG), "all_passed": True, "worst_abs_dev": {"cell": worst[0], "dev": worst[3], "four_se": worst[4]}},
        "draw_sentinels": {k: SENTINEL[k] for k in sorted(SENTINEL)},
    },
    "drafter_comparison_never_gated": {k: {"computed": frs(v[0]), "drafter": frs(v[1]), "exact_equal": v[0] == v[1]} for k, v in sorted(DRAFTER_CMP.items())},
    "sensitivity_straddles_named_never_ruling": SENS_STRADDLES,
    "anomalies": ANOMALIES,
    "self_checks": {"passed": _CHECKS["passed"], "failed": _CHECKS["failed"]},
}

with open(os.path.join(BASE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(RESULTS, fh, indent=1, sort_keys=True)
    fh.write("\n")
