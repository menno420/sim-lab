#!/usr/bin/env python3
"""verdict-032 — adaptive versioning on early signal: two-stage produce->observe->version
vs V020's mode-conditional static fork.

Answers idea-engine PROPOSAL 030 (control/outbox.md 2026-07-13T07:25:14Z, idea
ideas/venture-lab/adaptive-versioning-early-signal-2026-07-13.md, landed via idea-engine
PR #298). Parent: sim-lab sims/verdict-020-book-versioning @ 76dc487 (model inherited
VERBATIM; committed ruling row and Arm A quadrature values are chained anchors).

Fully hermetic: every constant is a pinned fixture in fixtures.json (committed BEFORE this
runner), copied verbatim from the idea file. stdlib only. No network, no git, no wall
clock, no hash(), no unseeded RNG. One uniform per normal (NormalDist().inv_cdf).
stdout and results.json are byte-identical across process runs (external diff).

Run: python3 sims/verdict-032-adaptive-versioning/adaptive_versioning_sim.py
Exit 0 iff all self-checks pass AND every pre-registered validity gate holds.
"""

import json
import math
import os
import random
import sys
from statistics import NormalDist

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- self-checks
_CHECKS = {"passed": 0, "failed": 0}
_FAILURES = []


def check(cond, msg):
    if cond:
        _CHECKS["passed"] += 1
    else:
        _CHECKS["failed"] += 1
        _FAILURES.append(msg)
        print("SELF-CHECK FAILED: %s" % msg)


# ------------------------------------------------------------------- fixtures
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FX = json.load(fh)

MD = FX["model"]
B_HEAD = MD["B_headline"]
B_REP = MD["B_reporting"]
B4_HEAD = MD["B4_headline"]
B4_REP = MD["B4_reporting"]
C_GRID = MD["c_grid"]
C4_GRID = MD["c4_grid_qu"]
SV_GRID = MD["sigma_v_grid"]
SM_GRID = MD["sigma_m_grid"]
F_GRID = MD["f_grid"]
S_GRID = MD["s_grid"]
SE_GRID = MD["sigma_e_grid"]
SE_PERFECT = MD["sigma_e_perfect_reporting"]
OM_GRID = MD["omega_grid"]
K_CAP = MD["K_cap"]
K_CAP_REP = MD["K_cap_reporting"]
K_GRID = MD["K_grid_static"]

M_MAIN = FX["M"]["main"]
M_STAB = FX["M"]["stability"]
M_REP = FX["M"]["reporting"]
M_ANCH = FX["M"]["anchor_titles"]
M_DEG = FX["M"]["degeneracy"]

SEED_MAIN = FX["seeds"]["main"]
SEED_STAB = FX["seeds"]["stability"]
SEED_REP = FX["seeds"]["reporting"]
SEED_AUX = FX["seeds"]["aux"]

BANDS = FX["bands"]
REJ_MAX = BANDS["reject_median_max"]
APP_MIN = BANDS["approve_median_min"]
OR_FLOOR = BANDS["oracle_floor"]
OR_SHARE = BANDS["oracle_pass_share"]

ANCH = FX["chained_anchor_row_verbatim"]
V020_F1 = FX["v020_arm_A_f1_slice_verbatim"]["rows"]
TOL = FX["pre_checked_tolerances"]

Q_LO = FX["quadrature"]["lo"]
Q_HI = FX["quadrature"]["hi"]
Q_STEP = FX["quadrature"]["step"]

# fixture pins re-asserted (belt and braces, the parent's discipline)
check(B_HEAD == 12 and B_REP == 6 and B4_HEAD == 48 and B4_REP == 24,
      "fixture pin: B=12 headline (B4=48), B=6 reporting (B4=24)")
check(C_GRID == [0.25, 0.5, 0.75] and C4_GRID == [1, 2, 3],
      "fixture pin: c grid / quarter-unit costs")
check(SV_GRID == [0.2, 0.5, 1.0] and SM_GRID == [0.5, 1.5, 2.5],
      "fixture pin: sigma_v / sigma_m grids")
check(F_GRID == [0.2, 0.6, 1.0] and S_GRID == [0.0, 0.5, 1.0],
      "fixture pin: f / s grids")
check(SE_GRID == [0.25, 1.0] and SE_PERFECT == 0.0,
      "fixture pin: sigma_e grid + perfect-signal reporting leg")
check(OM_GRID == [0.5, 0.75] and K_CAP == 4 and K_CAP_REP == 6,
      "fixture pin: omega grid, K_cap=4 (reporting 6)")
check(K_GRID == [1, 2, 3, 4, 6], "fixture pin: static K grid (V020's)")
check((M_MAIN, M_STAB, M_REP, M_ANCH, M_DEG) == (8000, 2000, 8000, 8000, 8000),
      "fixture pin: M values")
check((SEED_MAIN, SEED_STAB, SEED_REP, SEED_AUX)
      == (20260760, 20260761, 20260762, 20260763),
      "fixture pin: seeds 20260760-63 (above the P029 high-water 20260759)")
check((REJ_MAX, APP_MIN, OR_FLOOR, OR_SHARE) == (0.02, 0.10, -0.02, 0.80),
      "fixture pin: band constants")
check((ANCH["mode_P_share_kstar_eq1"], ANCH["mode_P_median_dR"],
       ANCH["mode_A_share_kstar_ge2"], ANCH["mode_A_median_dR"])
      == (0.851851852, 0.0, 0.888888889, 0.40621411),
      "fixture pin: V020 ruling row verbatim")
check((Q_LO, Q_HI, Q_STEP) == (-10.0, 10.0, 0.001),
      "fixture pin: parent quadrature constants")
check(sys.version_info[:2] == (3, 11),
      "CPython minor version pin: 3.11 (got %d.%d)" % sys.version_info[:2])

EHALF = math.exp(0.5)
SQRT2 = math.sqrt(2.0)
INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)
INV = NormalDist().inv_cdf
TINY_U = 2.0 ** -53


# ------------------------------------------------- Arm-analytic: quadrature
# (the parent's I_quad, inherited verbatim: E[exp(sigma*M_K)], M_K = max of K
# iid std normals — composite Simpson over [Q_LO, Q_HI] at step Q_STEP)
def norm_phi(x):
    return INV_SQRT_2PI * math.exp(-0.5 * x * x)


def norm_Phi(x):
    return 0.5 * (1.0 + math.erf(x / SQRT2))


_I_CACHE = {}


def I_quad(K, sigma):
    key = (K, sigma)
    if key in _I_CACHE:
        return _I_CACHE[key]
    n = int(round((Q_HI - Q_LO) / Q_STEP))
    km1 = K - 1
    terms = []
    for i in range(n + 1):
        x = Q_LO + i * Q_STEP
        v = math.exp(sigma * x) * K * norm_phi(x) * (norm_Phi(x) ** km1)
        if i == 0 or i == n:
            w = 1.0
        elif i % 2 == 1:
            w = 4.0
        else:
            w = 2.0
        terms.append(w * v)
    val = math.fsum(terms) * Q_STEP / 3.0
    _I_CACHE[key] = val
    return val


check(int(round((Q_HI - Q_LO) / Q_STEP)) % 2 == 0, "Simpson interval count even")
_SIGMA_COMBINED = sorted(set(
    round(math.sqrt(sv * sv + sm * sm), 15) for sv in SV_GRID for sm in SM_GRID))
for _sg in list(SV_GRID) + _SIGMA_COMBINED:
    _exact = math.exp(0.5 * _sg * _sg)
    check(abs(I_quad(1, _sg) / _exact - 1.0) < TOL["quadrature_identity_tol_rel"],
          "quadrature identity I(1,%.6g) vs exp(sigma^2/2)" % _sg)
    _prev = I_quad(1, _sg)
    for _K in K_GRID[1:]:
        _cur = I_quad(_K, _sg)
        check(_cur > _prev, "I(K,%.6g) strictly increasing at K=%d" % (_sg, _K))
        _prev = _cur


def m_P(sv, f, K):
    """Exact E[R_title(K)] Mode P (sigma_m inert: E[exp(L)]=1)."""
    return EHALF * (f * I_quad(K, sv) + (1.0 - f) * math.exp(0.5 * sv * sv))


def m_A(sv, sm, s, K):
    """Exact E[R_title(K)] Mode A."""
    sc = math.sqrt(sv * sv + sm * sm)
    return EHALF * ((1.0 - s) * math.exp(-0.5 * sm * sm) * I_quad(K, sc)
                    + s * K * math.exp(0.5 * sv * sv))


# ----------------------------------------------------- night plans (exact qu)
def static_plan(B4, c4, K):
    """(titles list of version counts, discarded qu). S(K): floor full titles
    + one partial (1 version + as many extras as it affords)."""
    full_cost = 4 + c4 * (K - 1)
    n_full = B4 // full_cost
    rem = B4 - n_full * full_cost
    if rem >= 4:
        k_p = 1 + (rem - 4) // c4
        disc = rem - (4 + c4 * (k_p - 1))
    else:
        k_p = 0
        disc = rem
    titles = [K] * n_full + ([k_p] if k_p else [])
    return titles, disc


def ad_plan(B4, B, omega, c4, kcap):
    """(T1, kbyrank, discarded qu, n_extras). Stage 1: T1 = round(omega*B)
    one-version titles; stage 2: y-descending round-robin extras at cost c4,
    cap kcap versions per title."""
    T1 = round(omega * B)
    rem = B4 - 4 * T1
    n_ex = min(rem // c4, T1 * (kcap - 1))
    disc = rem - n_ex * c4
    q, rmd = divmod(n_ex, T1)
    kbyrank = [q + (1 if r < rmd else 0) for r in range(T1)]
    return T1, kbyrank, disc, n_ex


# pinned T1 values (intake decision 4: Python 3 banker's rounding)
check(round(0.5 * 12) == 6 and round(0.75 * 12) == 9, "T1 pins B=12")
check(round(0.5 * 6) == 3 and round(0.75 * 6) == 4, "T1 pins B=6 (round(4.5)=4)")

# intake decision 10 claim: K_cap=6 changes the allocation ONLY at
# (B=12, omega=0.5, c=0.25)
for _B4, _B in ((B4_HEAD, B_HEAD), (B4_REP, B_REP)):
    for _om in OM_GRID:
        for _c4 in C4_GRID:
            _p4 = ad_plan(_B4, _B, _om, _c4, K_CAP)
            _p6 = ad_plan(_B4, _B, _om, _c4, K_CAP_REP)
            _differs = _p4[1] != _p6[1]
            _expected = (_om == 0.5 and _c4 == 1)
            check(_differs == _expected,
                  "K_cap=6 plan-difference map at (B4=%d, omega=%g, c4=%d)"
                  % (_B4, _om, _c4))


# ------------------------------------------------------------- counting RNG
class CR(random.Random):
    """random.Random with a uniform-draw counter (one uniform per normal)."""

    def __init__(self, seed):
        random.Random.__init__(self, seed)
        self.n = 0

    def u(self):
        self.n += 1
        r = self.random()
        return r if r > 0.0 else TINY_U


# --------------------------------------------------------------- static legs
def run_static_leg(mode, rng, M, B4, c4, sv, sm, fs, K):
    """One static (mode, cell, K) leg. Parent's per-title CE/CV estimators
    (theta / pick / Mode-P L integrated out). Returns (value, se_rel)."""
    titles, _ = static_plan(B4, c4, K)
    B = B4 / 4.0
    Ev = math.exp(0.5 * sv * sv)
    mu_L = -0.5 * sm * sm
    mexp = math.exp
    u = rng.u
    one_minus = (1.0 - fs)
    s1 = 0.0
    s2 = 0.0
    if mode == "P":
        f = fs
        for _ in range(M):
            tot = 0.0
            for Kt in titles:
                kev = Kt * Ev
                eps = [sv * INV(u()) for _ in range(Kt)]
                ex = [mexp(e) for e in eps]
                nx = [mexp(-e) for e in eps]
                a = 0.5 * ((kev - (sum(ex) - max(ex)))
                           + (kev - (sum(nx) - max(nx))))
                tot += EHALF * (f * a + one_minus * Ev)
            night = tot / B
            s1 += night
            s2 += night * night
    else:
        s = fs
        for _ in range(M):
            tot = 0.0
            for Kt in titles:
                kev = Kt * Ev
                eps = [sv * INV(u()) for _ in range(Kt)]
                g = [mexp(eps[i] + mu_L + sm * INV(u())) for i in range(Kt)]
                tot += EHALF * (kev - (1.0 - s) * (sum(g) - max(g)))
            night = tot / B
            s1 += night
            s2 += night * night
    mean = s1 / M
    var = max(0.0, s2 / M - mean * mean)
    se_rel = math.sqrt(var / M) / mean if mean > 0.0 else 0.0
    return mean, se_rel


def static_analytic(mode, B4, c4, sv, sm, fs, K):
    titles, _ = static_plan(B4, c4, K)
    B = B4 / 4.0
    if mode == "P":
        return sum(m_P(sv, fs, Kt) for Kt in titles) / B
    return sum(m_A(sv, sm, fs, Kt) for Kt in titles) / B


def static_draws_per_night(mode, B4, c4, K):
    titles, _ = static_plan(B4, c4, K)
    nv = sum(titles)
    return nv * (2 if mode == "A" else 1)


# ------------------------------------------------------------------- AD legs
def run_ad_leg(mode, rng, M, B4, B, T1, kbyrank, sv, sm, fs, sig_e, beta,
               y_mode="signal"):
    """One adaptive AD(omega) leg. y_mode: 'signal' (y = theta+eps_1+eta),
    'noise' (y = eta alone), 'uniform' (allocation in title-index order).
    Returns (value, se_rel, cv_mean, cv_se)."""
    Ev = math.exp(0.5 * sv * sv)
    mu_L = -0.5 * sm * sm
    mexp = math.exp
    u = rng.u
    t1eh = T1 * EHALF
    Bf = float(B)
    s1 = 0.0
    s2 = 0.0
    c1 = 0.0
    c2 = 0.0
    rng_T1 = range(T1)
    is_P = (mode == "P")
    f = fs if is_P else 0.0
    one_minus_f = 1.0 - f
    s_ = fs if not is_P else 0.0
    one_minus_s = 1.0 - s_
    for _ in range(M):
        th = [INV(u()) for _ in rng_T1]
        e1 = [sv * INV(u()) for _ in rng_T1]
        et = [sig_e * INV(u()) for _ in rng_T1]
        if y_mode == "signal":
            keyed = sorted((-(th[t] + e1[t] + et[t]), t) for t in rng_T1)
            order = [t for _, t in keyed]
        elif y_mode == "noise":
            keyed = sorted((-et[t], t) for t in rng_T1)
            order = [t for _, t in keyed]
        else:  # uniform: title-index order
            order = list(rng_T1)
        kext = [0] * T1
        for r, t in enumerate(order):
            kext[t] = kbyrank[r]
        epss = []
        for t in rng_T1:
            lst = [e1[t]]
            for _j in range(kext[t]):
                lst.append(sv * INV(u()))
            epss.append(lst)
        X = 0.0
        sth = 0.0
        if is_P:
            for t in rng_T1:
                eps = epss[t]
                Kt = 1 + kext[t]
                base = mexp(e1[t]) + (Kt - 1) * Ev
                if Kt == 1:
                    mhat = base
                    uhat = base
                else:
                    ex = [mexp(e) for e in eps]
                    ls_pos = sum(ex) - max(ex)
                    nx = [ex[0]] + [1.0 / v for v in ex[1:]]
                    ls_neg = sum(nx) - max(nx)
                    mhat = base - 0.5 * (ls_pos + ls_neg)
                    uhat = base / Kt
                eth = mexp(th[t])
                sth += eth
                X += eth * (f * mhat + one_minus_f * uhat)
        else:
            for t in rng_T1:
                eps = epss[t]
                Kt = 1 + kext[t]
                g = [mexp(eps[i] + mu_L + sm * INV(u())) for i in range(Kt)]
                eth = mexp(th[t])
                sth += eth
                X += eth * (mexp(e1[t]) + (Kt - 1) * Ev
                            - one_minus_s * (sum(g) - max(g)))
        cv = (sth - t1eh) / Bf
        night = X / Bf - beta * cv
        s1 += night
        s2 += night * night
        c1 += cv
        c2 += cv * cv
    mean = s1 / M
    var = max(0.0, s2 / M - mean * mean)
    se_rel = math.sqrt(var / M) / mean if mean > 0.0 else 0.0
    cvm = c1 / M
    cvv = max(0.0, c2 / M - cvm * cvm)
    return mean, se_rel, cvm, math.sqrt(cvv / M)


def ad_beta(mode, sv, sm, fs, T1, kbyrank):
    if mode == "P":
        tot = sum(m_P(sv, fs, 1 + k) for k in kbyrank)
    else:
        tot = sum(m_A(sv, sm, fs, 1 + k) for k in kbyrank)
    return tot / (T1 * EHALF)


def ad_analytic_signal_free(mode, B, sv, sm, fs, kbyrank):
    if mode == "P":
        return sum(m_P(sv, fs, 1 + k) for k in kbyrank) / B
    return sum(m_A(sv, sm, fs, 1 + k) for k in kbyrank) / B


def ad_draws_per_night(mode, T1, n_ex):
    nv = 3 * T1 + n_ex
    if mode == "A":
        nv += T1 + n_ex
    return nv


# ----------------------------------------------------------------- base cells
def base_cells(mode):
    last = F_GRID if mode == "P" else S_GRID
    return [(c4, sv, sm, x) for c4 in C4_GRID for sv in SV_GRID
            for sm in SM_GRID for x in last]


C_OF = {1: 0.25, 2: 0.5, 3: 0.75}


# ------------------------------------------------------------- leg batteries
def run_static_battery(rng, M, B4):
    """Static grids both modes. Returns {mode: {bc: {K: (value, se)}}}."""
    out = {}
    for mode in ("P", "A"):
        grid = {}
        for bc in base_cells(mode):
            c4, sv, sm, fs = bc
            per_k = {}
            for K in K_GRID:
                before = rng.n
                val, se = run_static_leg(mode, rng, M, B4, c4, sv, sm, fs, K)
                check(rng.n - before == M * static_draws_per_night(mode, B4, c4, K),
                      "draw sentinel static mode %s B4=%d cell %s K=%d"
                      % (mode, B4, bc, K))
                per_k[K] = (val, se)
            grid[bc] = per_k
        out[mode] = grid
    return out


def run_ad_battery(rng, M, B4, B, kcap, se_values, cells_filter=None):
    """AD grids both modes x omega x sigma_e. Returns
    {mode: {(bc, se_, om): (value, se_rel, cv_mean, cv_se)}}."""
    out = {}
    for mode in ("P", "A"):
        legs = {}
        for bc in base_cells(mode):
            c4, sv, sm, fs = bc
            if cells_filter is not None and not cells_filter(bc):
                continue
            for se_ in se_values:
                for om in OM_GRID if kcap == K_CAP else [0.5]:
                    T1, kbr, disc, n_ex = ad_plan(B4, B, om, c4, kcap)
                    beta = ad_beta(mode, sv, sm, fs, T1, kbr)
                    before = rng.n
                    val, se_rel, cvm, cvse = run_ad_leg(
                        mode, rng, M, B4, B, T1, kbr, sv, sm, fs, se_, beta)
                    check(rng.n - before == M * ad_draws_per_night(mode, T1, n_ex),
                          "draw sentinel AD mode %s B4=%d cell %s se=%g om=%g"
                          % (mode, B4, bc, se_, om))
                    check(abs(cvm) <= 6.0 * cvse + 1e-12,
                          "theta-CV term mean within 6 SE of 0 (mode %s cell %s "
                          "se=%g om=%g)" % (mode, bc, se_, om))
                    if len(set(kbr)) == 1:
                        ana = ad_analytic_signal_free(mode, B, sv, sm, fs, kbr)
                        dev = abs(val / ana - 1.0)
                        check(dev <= max(0.01, 6.0 * se_rel),
                              "signal-free AD leg unbiasedness dev %.5f (mode %s "
                              "B4=%d cell %s se=%g om=%g)"
                              % (dev, mode, B4, bc, se_, om))
                    legs[(bc, se_, om)] = (val, se_rel, cvm, cvse)
        out[mode] = legs
    return out


# -------------------------------------------------- comparisons + band rule
def build_rows(static_grid, ad_legs, se_values):
    """Per (mode, bc, sigma_e, omega): Delta_cond, Delta_or.
    R_cond: Mode P S(1), Mode A S(6). R_or = max_K static."""
    rows = {}
    for mode in ("P", "A"):
        cond_K = 1 if mode == "P" else 6
        for bc in base_cells(mode):
            st = static_grid[mode][bc]
            r_cond = st[cond_K][0]
            r_or = max(st[K][0] for K in K_GRID)
            k_or = min(K for K in K_GRID if st[K][0] == r_or)
            for se_ in se_values:
                for om in OM_GRID:
                    key = (bc, se_, om)
                    if key not in ad_legs[mode]:
                        continue
                    r_ad, se_rel, _, _ = ad_legs[mode][key]
                    rows[(mode, bc, se_, om)] = {
                        "r_ad": r_ad, "se_rel": se_rel, "r_cond": r_cond,
                        "r_or": r_or, "k_or": k_or,
                        "d_cond": r_ad / r_cond - 1.0,
                        "d_or": r_ad / r_or - 1.0}
    return rows


def median81(vals):
    check(len(vals) == 81, "group has 81 cells")
    return sorted(vals)[40]


def group_stats(rows):
    """Per (mode, omega, sigma_e): median d_cond + oracle pass share."""
    out = {}
    for mode in ("P", "A"):
        for om in OM_GRID:
            for se_ in SE_GRID:
                sel = [r for (m, bc, s_, o), r in rows.items()
                       if m == mode and s_ == se_ and o == om]
                dcs = [r["d_cond"] for r in sel]
                n_pass = sum(1 for r in sel if r["d_or"] >= OR_FLOOR)
                out[(mode, om, se_)] = {
                    "median_d_cond": median81(dcs),
                    "oracle_pass_share": n_pass / len(sel),
                    "n_cells": len(sel)}
    return out


def decide_v1(gs):
    """Evaluator 1 (procedural). Registered order: REJECT first."""
    reject = True
    for om in OM_GRID:
        for se_ in SE_GRID:
            for mode in ("P", "A"):
                if gs[(mode, om, se_)]["median_d_cond"] > REJ_MAX:
                    reject = False
    if reject:
        return "REJECT"
    for om in OM_GRID:
        ok = True
        for se_ in SE_GRID:
            for mode in ("P", "A"):
                g = gs[(mode, om, se_)]
                if g["median_d_cond"] < APP_MIN:
                    ok = False
                if g["oracle_pass_share"] < OR_SHARE:
                    ok = False
        if ok:
            return "APPROVE"
    return "NULL"


def decide_v2(gs):
    """Evaluator 2 (independent styling — comprehensions over the same table)."""
    groups = [gs[(m, o, s_)] for m in ("P", "A") for o in OM_GRID
              for s_ in SE_GRID]
    if all(g["median_d_cond"] <= REJ_MAX for g in groups):
        return "REJECT"
    approving = [o for o in OM_GRID
                 if all(gs[(m, o, s_)]["median_d_cond"] >= APP_MIN
                        and gs[(m, o, s_)]["oracle_pass_share"] >= OR_SHARE
                        for m in ("P", "A") for s_ in SE_GRID)]
    return "APPROVE" if approving else "NULL"


def axis_tables(rows):
    """Intake decision 13: per-axis medians + pass shares (pooled over omega,
    and over modes for shared axes)."""
    def slice_stats(sel):
        dcs = sorted(r["d_cond"] for r in sel)
        n = len(sel)
        med = (dcs[n // 2] if n % 2 == 1
               else 0.5 * (dcs[n // 2 - 1] + dcs[n // 2]))
        return {"n_rows": n, "median_d_cond": med,
                "share_d_cond_ge_approve": sum(
                    1 for r in sel if r["d_cond"] >= APP_MIN) / n,
                "share_d_or_ge_floor": sum(
                    1 for r in sel if r["d_or"] >= OR_FLOOR) / n}

    allr = list(rows.items())
    out = {}
    out["mode"] = {m: slice_stats([r for (mm, bc, s_, o), r in allr if mm == m])
                   for m in ("P", "A")}
    out["sigma_e"] = {"%g" % s_: slice_stats(
        [r for (mm, bc, ss, o), r in allr if ss == s_]) for s_ in SE_GRID}
    out["c"] = {"%g" % C_OF[c4]: slice_stats(
        [r for (mm, bc, s_, o), r in allr if bc[0] == c4]) for c4 in C4_GRID}
    out["sigma_v"] = {"%g" % sv: slice_stats(
        [r for (mm, bc, s_, o), r in allr if bc[1] == sv]) for sv in SV_GRID}
    out["sigma_m"] = {"%g" % sm: slice_stats(
        [r for (mm, bc, s_, o), r in allr if bc[2] == sm]) for sm in SM_GRID}
    out["f_mode_P"] = {"%g" % f: slice_stats(
        [r for (mm, bc, s_, o), r in allr if mm == "P" and bc[3] == f])
        for f in F_GRID}
    out["s_mode_A"] = {"%g" % s: slice_stats(
        [r for (mm, bc, s_, o), r in allr if mm == "A" and bc[3] == s])
        for s in S_GRID}
    return out


# ------------------------------------------------------------------ anchor
def run_anchor(rng):
    """Chained-anchor leg: the parent's per-title-expectation machinery at a
    fresh seed (aux stream); fractional value = mean/(1+c(K-1))."""
    res = {}
    for mode in ("P", "A"):
        cells = []
        for bc in base_cells(mode):
            c4, sv, sm, fs = bc
            c = C_OF[c4]
            Ev = math.exp(0.5 * sv * sv)
            mu_L = -0.5 * sm * sm
            u = rng.u
            mexp = math.exp
            values = {}
            for K in K_GRID:
                kev = K * Ev
                before = rng.n
                s1 = 0.0
                if mode == "P":
                    f = fs
                    omf = 1.0 - f
                    for _ in range(M_ANCH):
                        eps = [sv * INV(u()) for _ in range(K)]
                        ex = [mexp(e) for e in eps]
                        nx = [mexp(-e) for e in eps]
                        a = 0.5 * ((kev - (sum(ex) - max(ex)))
                                   + (kev - (sum(nx) - max(nx))))
                        s1 += EHALF * (f * a + omf * Ev)
                else:
                    s = fs
                    oms = 1.0 - s
                    for _ in range(M_ANCH):
                        eps = [sv * INV(u()) for _ in range(K)]
                        g = [mexp(eps[i] + mu_L + sm * INV(u()))
                             for i in range(K)]
                        s1 += EHALF * (kev - oms * (sum(g) - max(g)))
                check(rng.n - before == M_ANCH * K * (2 if mode == "A" else 1),
                      "draw sentinel anchor mode %s cell %s K=%d" % (mode, bc, K))
                values[K] = (s1 / M_ANCH) / (1.0 + c * (K - 1))
            kstar = K_GRID[0]
            for K in K_GRID[1:]:
                if values[K] > values[kstar]:
                    kstar = K
            cells.append({"cell": bc, "values": values, "kstar": kstar,
                          "dR": values[kstar] / values[1] - 1.0})
        n = len(cells)
        check(n == 81, "anchor mode %s grid 81 cells" % mode)
        share_eq1 = sum(1 for r in cells if r["kstar"] == 1) / n
        share_ge2 = sum(1 for r in cells if r["kstar"] >= 2) / n
        med = sorted(r["dR"] for r in cells)[40]
        res[mode] = {"share_kstar_eq1": share_eq1, "share_kstar_ge2": share_ge2,
                     "median_dR": med}
    # gates (pre-checked tolerances from fixtures)
    check(abs(res["P"]["share_kstar_eq1"] - ANCH["mode_P_share_kstar_eq1"])
          <= TOL["anchor_mode_P_share_tol"],
          "PRE-REGISTERED GATE chained anchor: Mode P share(K*=1) %.9f vs %.9f"
          % (res["P"]["share_kstar_eq1"], ANCH["mode_P_share_kstar_eq1"]))
    check(res["P"]["median_dR"] == 0.0,
          "PRE-REGISTERED GATE chained anchor: Mode P median dR == 0.0 exactly")
    check(abs(res["A"]["share_kstar_ge2"] - ANCH["mode_A_share_kstar_ge2"])
          <= TOL["anchor_mode_A_share_tol"],
          "PRE-REGISTERED GATE chained anchor: Mode A share(K*>=2) %.9f vs %.9f"
          % (res["A"]["share_kstar_ge2"], ANCH["mode_A_share_kstar_ge2"]))
    check(abs(res["A"]["median_dR"] - ANCH["mode_A_median_dR"])
          <= TOL["anchor_mode_A_median_dR_tol"],
          "PRE-REGISTERED GATE chained anchor: Mode A median dR %.6f vs %.6f"
          % (res["A"]["median_dR"], ANCH["mode_A_median_dR"]))
    return res


def anchor_analytic_subgate():
    """Seedless analytic reproduction of the parent's grid (sub-gate)."""
    out = {}
    for mode in ("P", "A"):
        n1 = 0
        ge2 = 0
        drs = []
        for bc in base_cells(mode):
            c4, sv, sm, fs = bc
            c = C_OF[c4]
            values = {}
            for K in K_GRID:
                mean = m_P(sv, fs, K) if mode == "P" else m_A(sv, sm, fs, K)
                values[K] = mean / (1.0 + c * (K - 1))
            kstar = K_GRID[0]
            for K in K_GRID[1:]:
                if values[K] > values[kstar]:
                    kstar = K
            if kstar == 1:
                n1 += 1
            else:
                ge2 += 1
            drs.append(values[kstar] / values[1] - 1.0)
        med = sorted(drs)[40]
        out[mode] = {"n_kstar_eq1": n1, "n_kstar_ge2": ge2, "median_dR": med}
    check(out["P"]["n_kstar_eq1"] == 69,
          "anchor analytic sub-gate: Mode P K*=1 count 69/81")
    check(out["A"]["n_kstar_ge2"] == 72,
          "anchor analytic sub-gate: Mode A K*>=2 count 72/81")
    check(out["P"]["median_dR"] == 0.0,
          "anchor analytic sub-gate: Mode P median dR 0.0 exactly")
    check(abs(out["A"]["median_dR"] - ANCH["mode_A_median_dR"]) <= 0.005,
          "anchor analytic sub-gate: Mode A median dR %.6f within 0.005 of %.6f"
          % (out["A"]["median_dR"], ANCH["mode_A_median_dR"]))
    return out


# ------------------------------------------------------------- f=1 slice gate
def f1_slice_gate():
    got_rows = []
    n_checked = 0
    for row in V020_F1:
        c = row["c"]
        sv = row["sigma_v"]
        ours = {}
        for K in K_GRID:
            v = EHALF * I_quad(K, sv) / (1.0 + c * (K - 1))
            v9 = float("%.9g" % v)
            committed = row["by_K"][str(K)]
            check(v9 == committed,
                  "PRE-REGISTERED GATE f=1 slice: c=%g sv=%g K=%d %.9g == %.9g"
                  % (c, sv, K, v9, committed))
            ours[str(K)] = v9
            n_checked += 1
        got_rows.append({"c": c, "sigma_v": sv, "by_K": ours})
    check(n_checked == 45, "f=1 slice gate covered 45 values")
    return got_rows


# ------------------------------------------------------------------ main run
def main():
    print("verdict-032 adaptive-versioning sim — PROPOSAL 030 pre-registered run")
    print("CPython %d.%d (pinned minor 3.11)" % sys.version_info[:2])

    # ---- seedless gates first
    f1_rows = f1_slice_gate()
    ana_sub = anchor_analytic_subgate()

    # K=1 identity + s=1 additivity on the analytic layer (exact)
    for sv in SV_GRID:
        ident = math.exp(0.5 * (1.0 + sv * sv))
        for fs in F_GRID:
            check(abs(m_P(sv, fs, 1) / ident - 1.0)
                  < TOL["quadrature_identity_tol_rel"],
                  "analytic K=1 identity Mode P sv=%g f=%g" % (sv, fs))
        for sm in SM_GRID:
            for s in S_GRID:
                check(abs(m_A(sv, sm, s, 1) / ident - 1.0)
                      < TOL["quadrature_identity_tol_rel"],
                      "analytic K=1 identity Mode A sv=%g sm=%g s=%g"
                      % (sv, sm, s))
            for K in K_GRID:
                check(abs(m_A(sv, sm, 1.0, K) / (K * ident) - 1.0) < 1e-12,
                      "analytic s=1 additivity sv=%g sm=%g K=%d" % (sv, sm, K))

    # ---- main stream: decision legs
    rng_main = CR(SEED_MAIN)
    static_main = run_static_battery(rng_main, M_MAIN, B4_HEAD)
    ad_main = run_ad_battery(rng_main, M_MAIN, B4_HEAD, B_HEAD, K_CAP, SE_GRID)
    n_main_draws = rng_main.n

    # prefix replay (intake decision 15): first two legs, fresh stream
    rng_rep = CR(SEED_MAIN)
    bc0 = base_cells("P")[0]
    for K in K_GRID[:2]:
        v_new, _ = run_static_leg("P", rng_rep, M_MAIN, B4_HEAD, bc0[0],
                                  bc0[1], bc0[2], bc0[3], K)
        check(v_new == static_main["P"][bc0][K][0],
              "prefix replay bit-identical (static P cell0 K=%d)" % K)

    # MC K=1 identity / s=1 additivity (exact zero-variance estimators)
    for mode in ("P", "A"):
        for bc in base_cells(mode):
            c4, sv, sm, fs = bc
            ident = math.exp(0.5 * (1.0 + sv * sv))
            v1, se1 = static_main[mode][bc][1]
            check(abs(v1 / ident - 1.0) <= TOL["k1_identity_tol_rel"],
                  "PRE-REGISTERED GATE K=1 identity (MC exact) mode %s cell %s"
                  % (mode, bc))
            check(se1 < 1e-7, "K=1 estimator zero-variance mode %s %s" % (mode, bc))
            if mode == "A" and fs == 1.0:
                for K in K_GRID:
                    vK, seK = static_main[mode][bc][K]
                    titles, _ = static_plan(B4_HEAD, c4, K)
                    ana = sum(Kt * ident for Kt in titles) / (B4_HEAD / 4.0)
                    check(abs(vK / ana - 1.0) <= TOL["s1_additivity_tol_rel"],
                          "PRE-REGISTERED GATE s=1 additivity (MC exact) %s K=%d"
                          % (bc, K))
                    check(seK < 1e-7, "s=1 estimator zero-variance %s K=%d" % (bc, K))

    # static diagnostic layer (parent's tolerance)
    max_dev_static = 0.0
    for mode in ("P", "A"):
        for bc in base_cells(mode):
            c4, sv, sm, fs = bc
            for K in K_GRID:
                val, se = static_main[mode][bc][K]
                ana = static_analytic(mode, B4_HEAD, c4, sv, sm, fs, K)
                dev = abs(val / ana - 1.0)
                max_dev_static = max(max_dev_static, dev)
                check(dev <= max(0.01, 6.0 * se),
                      "static diagnostic dev %.5f mode %s cell %s K=%d"
                      % (dev, mode, bc, K))

    # ---- comparisons + rule
    rows = build_rows(static_main, ad_main, SE_GRID)
    check(len(rows) == 324 * 2, "comparison table has 648 (cell, omega) rows")
    gs = group_stats(rows)
    ruling1 = decide_v1(gs)
    ruling2 = decide_v2(gs)
    check(ruling1 == ruling2,
          "twin decision evaluators agree (%s vs %s)" % (ruling1, ruling2))
    ruling = ruling1
    axes = axis_tables(rows)

    # ---- reporting stream
    rng_r = CR(SEED_REP)
    ad_se0 = run_ad_battery(rng_r, M_REP, B4_HEAD, B_HEAD, K_CAP, [SE_PERFECT])
    ad_kcap6 = run_ad_battery(rng_r, M_REP, B4_HEAD, B_HEAD, K_CAP_REP, [0.25],
                              cells_filter=lambda bc: bc[0] == 1)
    static_b6 = run_static_battery(rng_r, M_REP, B4_REP)
    ad_b6 = run_ad_battery(rng_r, M_REP, B4_REP, B_REP, K_CAP, SE_GRID)
    n_rep_draws = rng_r.n
    rows_se0 = build_rows(static_main, ad_se0, [SE_PERFECT])
    rows_b6 = build_rows(static_b6, ad_b6, SE_GRID)

    # ---- aux stream: chained anchor + degeneracy
    rng_x = CR(SEED_AUX)
    anchor = run_anchor(rng_x)
    degeneracy = {}
    for mode, fs in (("P", 0.6), ("A", 0.5)):
        c4, sv, sm = 2, 0.5, 1.5
        se_ = 0.25
        om = 0.75
        T1, kbr, _, n_ex = ad_plan(B4_HEAD, B_HEAD, om, c4, K_CAP)
        beta = ad_beta(mode, sv, sm, fs, T1, kbr)
        before = rng_x.n
        va, sa, _, _ = run_ad_leg(mode, rng_x, M_DEG, B4_HEAD, B_HEAD, T1, kbr,
                                  sv, sm, fs, se_, beta, y_mode="noise")
        check(rng_x.n - before == M_DEG * ad_draws_per_night(mode, T1, n_ex),
              "draw sentinel degeneracy noise-y mode %s" % mode)
        before = rng_x.n
        vb, sb, _, _ = run_ad_leg(mode, rng_x, M_DEG, B4_HEAD, B_HEAD, T1, kbr,
                                  sv, sm, fs, se_, beta, y_mode="uniform")
        check(rng_x.n - before == M_DEG * ad_draws_per_night(mode, T1, n_ex),
              "draw sentinel degeneracy uniform-order mode %s" % mode)
        ratio = va / vb - 1.0
        check(abs(ratio) <= TOL["degeneracy_tol"],
              "PRE-REGISTERED GATE signal-degeneracy mode %s |%.5f| <= %.3f"
              % (mode, ratio, TOL["degeneracy_tol"]))
        degeneracy[mode] = {"noise_y": va, "se_noise": sa, "uniform": vb,
                            "se_uniform": sb, "rel_diff": ratio}
    n_aux_draws = rng_x.n

    # ---- stability stream (intake decision 18)
    rng_s = CR(SEED_STAB)
    static_stab = run_static_battery(rng_s, M_STAB, B4_HEAD)
    ad_stab = run_ad_battery(rng_s, M_STAB, B4_HEAD, B_HEAD, K_CAP, SE_GRID)
    n_stab_draws = rng_s.n
    rows_stab = build_rows(static_stab, ad_stab, SE_GRID)
    gs_stab = group_stats(rows_stab)
    ruling_stab = decide_v1(gs_stab)
    check(decide_v2(gs_stab) == ruling_stab, "twin evaluators agree (stability)")
    check(ruling_stab == ruling,
          "PRE-REGISTERED GATE: stability leg (M=%d, seed %d) reproduces the "
          "ruling (%s vs %s)" % (M_STAB, SEED_STAB, ruling_stab, ruling))

    # ---- discarded-budget fractions (deterministic)
    discarded = {}
    for B4, B in ((B4_HEAD, B_HEAD), (B4_REP, B_REP)):
        for om in OM_GRID:
            for c4 in C4_GRID:
                for kcap in (K_CAP, K_CAP_REP):
                    T1, kbr, disc, n_ex = ad_plan(B4, B, om, c4, kcap)
                    discarded["AD B=%d omega=%g c=%g kcap=%d"
                              % (B, om, C_OF[c4], kcap)] = disc / B4
        for c4 in C4_GRID:
            for K in K_GRID:
                _, disc = static_plan(B4, c4, K)
                discarded["S B=%d c=%g K=%d" % (B, C_OF[c4], K)] = disc / B4

    # ------------------------------------------------------------- output
    def bc_key(mode, bc):
        c4, sv, sm, fs = bc
        return "c=%g,sv=%g,sm=%g,%s=%g" % (C_OF[c4], sv, sm,
                                           "f" if mode == "P" else "s", fs)

    def static_json(grid, B4):
        out = {}
        for mode in ("P", "A"):
            cells = []
            for bc in base_cells(mode):
                per = grid[mode][bc]
                r_or = max(per[K][0] for K in K_GRID)
                cells.append({
                    "cell": bc_key(mode, bc),
                    "value_by_K": {str(K): per[K][0] for K in K_GRID},
                    "se_rel_by_K": {str(K): per[K][1] for K in K_GRID},
                    "R_cond": per[1 if mode == "P" else 6][0],
                    "R_or": r_or,
                    "K_or": min(K for K in K_GRID if per[K][0] == r_or)})
            out[mode] = cells
        return out

    def rows_json(rows):
        out = []
        for (mode, bc, se_, om) in sorted(rows.keys(), key=lambda k: (
                k[0], k[1], k[2], k[3])):
            r = rows[(mode, bc, se_, om)]
            out.append({"mode": mode, "cell": bc_key(mode, bc),
                        "sigma_e": se_, "omega": om, "R_AD": r["r_ad"],
                        "se_rel": r["se_rel"], "R_cond": r["r_cond"],
                        "R_or": r["r_or"], "K_or": r["k_or"],
                        "delta_cond": r["d_cond"], "delta_or": r["d_or"]})
        return out

    results = {
        "sim": "verdict-032-adaptive-versioning",
        "proposal": FX["source"]["proposal"],
        "cpython": "%d.%d" % sys.version_info[:2],
        "gates": {
            "f1_slice_vs_v020_committed": {"n_checked": 45, "match": "exact after %.9g rounding"},
            "anchor_analytic_subgate": ana_sub,
            "chained_anchor_fresh_seed": anchor,
            "static_diagnostic_max_rel_dev": max_dev_static,
            "signal_degeneracy": degeneracy,
        },
        "static_B12": static_json(static_main, B4_HEAD),
        "ad_rows_B12": rows_json(rows),
        "group_stats": {"%s omega=%g sigma_e=%g" % (m, o, s_): gs[(m, o, s_)]
                        for (m, o, s_) in sorted(gs.keys())},
        "axis_tables": axes,
        "reporting": {
            "sigma_e_0_upper_bound": rows_json(rows_se0),
            "K_cap_6": {m: [{"cell": bc_key(m, bc), "sigma_e": se_, "omega": om,
                             "R_AD": v[0], "se_rel": v[1]}
                            for (bc, se_, om), v in sorted(
                                ad_kcap6[m].items(),
                                key=lambda kv: (kv[0][0], kv[0][1], kv[0][2]))]
                        for m in ("P", "A")},
            "static_B6": static_json(static_b6, B4_REP),
            "ad_rows_B6": rows_json(rows_b6),
            "discarded_budget_fractions": discarded,
        },
        "stability_leg": {
            "M": M_STAB, "seed": SEED_STAB, "ruling": ruling_stab,
            "matches_main": ruling_stab == ruling,
            "group_stats": {"%s omega=%g sigma_e=%g" % (m, o, s_):
                            gs_stab[(m, o, s_)]
                            for (m, o, s_) in sorted(gs_stab.keys())}},
        "ruling": {
            "decision": ruling,
            "rule": {"REJECT": BANDS["REJECT"], "APPROVE": BANDS["APPROVE"],
                     "NULL": BANDS["NULL"],
                     "evaluation_order": BANDS["evaluation_order"]},
            "twin_evaluators_agree": ruling1 == ruling2,
        },
        "draw_totals": {"main": n_main_draws, "reporting": n_rep_draws,
                        "aux": n_aux_draws, "stability": n_stab_draws},
    }

    def round_floats(obj):
        if isinstance(obj, float):
            return float("%.9g" % obj)
        if isinstance(obj, dict):
            return {k: round_floats(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [round_floats(v) for v in obj]
        return obj

    results["self_checks"] = {"counted_at_dump": _CHECKS["passed"],
                              "failed_at_dump": _CHECKS["failed"]}
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(round_floats(results), fh, indent=1, sort_keys=True)
        fh.write("\n")

    # ------------------------------------------------------------- stdout
    print("f=1 slice gate: 45/45 committed V020 Arm A values matched exactly "
          "(after 9-sig-digit rounding)")
    print("anchor analytic sub-gate: Mode P 69/81 K*=1 (median dR %.6f), "
          "Mode A 72/81 K*>=2 (median dR %.6f)"
          % (ana_sub["P"]["median_dR"], ana_sub["A"]["median_dR"]))
    print("chained anchor (fresh seed %d): Mode P share(K*=1) %.9f / median dR "
          "%.6f; Mode A share(K*>=2) %.9f / median dR %.6f"
          % (SEED_AUX, anchor["P"]["share_kstar_eq1"], anchor["P"]["median_dR"],
             anchor["A"]["share_kstar_ge2"], anchor["A"]["median_dR"]))
    print("static diagnostic layer max rel dev: %.5f" % max_dev_static)
    for mode in ("P", "A"):
        d = degeneracy[mode]
        print("signal-degeneracy mode %s: noise-y/uniform-order rel diff %+.5f "
              "(tol %.3f)" % (mode, d["rel_diff"], TOL["degeneracy_tol"]))
    for (m, o, s_) in sorted(gs.keys()):
        g = gs[(m, o, s_)]
        print("group mode %s omega=%.2f sigma_e=%.2f: median delta_cond %+.4f; "
              "oracle pass share %.4f"
              % (m, o, s_, g["median_d_cond"], g["oracle_pass_share"]))
    print("stability leg (M=%d seed %d): ruling %s (matches main: %s)"
          % (M_STAB, SEED_STAB, ruling_stab, ruling_stab == ruling))
    print("draw totals: main %d, reporting %d, aux %d, stability %d"
          % (n_main_draws, n_rep_draws, n_aux_draws, n_stab_draws))
    print("PRE-REGISTERED RULING: %s" % ruling)
    print("SELF-CHECKS: %d passed, %d failed"
          % (_CHECKS["passed"], _CHECKS["failed"]))
    if _CHECKS["failed"]:
        for msg in _FAILURES[:50]:
            print("  FAILED: %s" % msg)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
