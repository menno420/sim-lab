#!/usr/bin/env python3
"""verdict-031 — lease-renewal claim expiry (renewal-race model).

Settles idea-engine PROPOSAL 029 (control/outbox.md 2026-07-13T06:51:49Z,
status: sim-ready; idea ideas/substrate-kit/lease-renewal-claim-expiry-
2026-07-13.md, landed via idea-engine PR #297). Prices the mechanism
VERDICT 027 routed (the explicit `renewed:` stamp) on V027's own bands.
Hermetic: reads exactly ONE file (its own committed fixtures.json
pre-registration, cross-checked at start), no network, no repo state, no
wall clock. Arm A is exact and seedless (all 45 decision points, zero
sampling error); Arm S is stdlib random.Random event-driven MC under the
four pinned seeds 20260756-59. Deterministic: stdout and results.json are
byte-identical across process runs (verified by external diff). Progress
goes to stderr only.

Run: python3 sims/verdict-031-lease-renewal/lease_renewal_sim.py
Exit 0 iff every self-check passes.
"""
import json
import math
import os
import random
import sys
from fractions import Fraction

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

P_W = (2, 12, 24)
P_F = (0.02, 0.10, 0.25)
P_F_FRAC = {0.02: Fraction(1, 50), 0.10: Fraction(1, 10), 0.25: Fraction(1, 4)}
THETAS = (6, 12, 24, 48, 72)
H_C = 168
H_C_REP = (4, 24)
P_D = 0.10
LAM_T = 1.0 / 4.0
LAM_O = 1.0 / 12.0
LAM_C48 = 1.0 / 48.0
M_S = 4000
M_STAB = 1000
M_REP = 1000
M_AUX = 500
M_DIAG = 64000
SEED_MAIN, SEED_STAB, SEED_REP, SEED_AUX = 20260756, 20260757, 20260758, 20260759
T_MAX = 0.05
O95_MAX = 120.0
APPROVE_CELLS = 8
REJECT_CELLS = 5
GATE_T = 0.01
GATE_O_ABS = 4.0
GATE_O_REL = 0.05
SIGMA_MULT = 2.5
N_ALIVE_EXP = round((1.0 - P_D) * M_S)
N_DEAD_EXP = round(P_D * M_S)
LEG_E_PF = 0.10
LEG_E_GRACE = 1.08

check(sys.version_info[:2] == (3, 11), "CPython minor pinned to 3.11")
check(FX["model"]["p_w_grid_hours"] == list(P_W), "fixtures: p_w grid")
check(FX["model"]["p_f_grid"] == [0.02, 0.1, 0.25], "fixtures: p_f grid")
check(FX["model"]["theta_r_grid_hours"] == list(THETAS), "fixtures: theta_r grid")
check(FX["model"]["H_c_decision_hours"] == H_C, "fixtures: H_c 168")
check(FX["model"]["H_c_reporting_hours"] == list(H_C_REP), "fixtures: H_c reporting")
check(FX["model"]["p_d_pinned"] == P_D, "fixtures: p_d 0.10")
check(FX["model"]["p_d_sensitivity_reporting_only"] == [0.02, 0.30], "fixtures: p_d sensitivity")
check(FX["model"]["lambda_T_per_hour"] == LAM_T, "fixtures: lambda_T 1/4")
check(FX["model"]["lambda_O_per_hour"] == LAM_O, "fixtures: lambda_O 1/12")
check(FX["model"]["lambda_C48_reporting_per_hour"] == LAM_C48, "fixtures: lambda_C48 1/48")
check(FX["arm_S"]["M_S"] == M_S, "fixtures: M_S 4000")
check(FX["arm_S"]["seed"] == SEED_MAIN, "fixtures: main seed 20260756")
check(FX["arm_S"]["stability_leg"]["seed"] == SEED_STAB, "fixtures: stability seed 20260757")
check(FX["arm_S"]["stability_leg"]["M_S"] == M_STAB, "fixtures: stability M_S 1000")
check(FX["arm_S"]["reporting_only_legs"]["seed"] == SEED_REP, "fixtures: reporting seed 20260758")
check(FX["arm_S"]["reporting_only_legs"]["M_rep"] == M_REP, "fixtures: M_rep 1000")
check(FX["arm_S"]["aux_stream"]["seed"] == SEED_AUX, "fixtures: aux seed 20260759")
check(FX["arm_S"]["aux_stream"]["M_aux"] == M_AUX, "fixtures: M_aux 500")
check(FX["arm_S"]["aux_stream"]["M_diag"] == M_DIAG, "fixtures: M_diag 64000")
check(FX["decision_rule"]["band_constants"]["T_max"] == T_MAX, "fixtures: T band 0.05")
check(FX["decision_rule"]["band_constants"]["O95_max_hours"] == O95_MAX, "fixtures: O95 band 120")
LIFETIMES = FX["empirical_anchors_quoted_at_drafting"]["work_claim_lifetimes_hours_n11"]
GAPS19 = FX["empirical_anchors_quoted_at_drafting"]["heartbeat_restamp_gaps_hours_n19"]
check(len(LIFETIMES) == 11 and sorted(LIFETIMES)[5] == 2.65, "fixtures: lifetime multiset n=11 median 2.65")
check(len(GAPS19) == 19 and sorted(GAPS19)[9] == 1.08 and max(GAPS19) == 5.52,
      "fixtures: gap multiset n=19 median 1.08 max 5.52")

CELLS = [(pw, pf) for pw in P_W for pf in P_F]
N_OF = {2: 84, 12: 14, 24: 7}
for pw in P_W:
    check(H_C == N_OF[pw] * pw, "lattice N*p_w == H_c for p_w=%d" % pw)


# ---------------------------------------------------------------------------
# Arm A — exact T: factor-folding DP over the trailing-run state.
# A maximal run of j consecutive forgets exposes (j*p_w - theta_r)+ hours
# (registered formula; overdue convention, intake decisions 1-3).
# ---------------------------------------------------------------------------
def g_expo(j, pw, theta):
    return max(0, j * pw - theta)


def t_exact(pw, pf, theta, lam):
    return t_exact_n(N_OF[pw], pw, pf, theta, lam)


def t_exact_n(n, pw, pf, theta, lam):
    if n == 0:
        return 0.0
    if g_expo(n, pw, theta) <= 0:
        # even the maximal run (all N wakes forgotten) exposes zero hours,
        # so X == 0 with probability 1 and T = 0 EXACTLY (pin 4 derivation)
        return 0.0
    w = [0.0] * (n + 1)
    w[0] = 1.0
    for _ in range(n):
        nw = [0.0] * (n + 1)
        stamp_p = 1.0 - pf
        for j in range(n + 1):
            wj = w[j]
            if wj == 0.0:
                continue
            if j + 1 <= n:
                nw[j + 1] += wj * pf
            nw[0] += wj * stamp_p * math.exp(-lam * g_expo(j, pw, theta))
        w = nw
    e = 0.0
    for j in range(n + 1):
        if w[j] != 0.0:
            e += w[j] * math.exp(-lam * g_expo(j, pw, theta))
    return 1.0 - e


def t_dist(pw, pf, theta, lam):
    """Independent cross-arm: exposure-DISTRIBUTION DP over (trailing run,
    accumulated integer exposure), structurally different from t_exact."""
    n = N_OF[pw]
    dp = {(0, 0): 1.0}
    for _ in range(n):
        nd = {}
        for (j, x), pr in dp.items():
            k1 = (j + 1, x)
            nd[k1] = nd.get(k1, 0.0) + pr * pf
            xc = x + g_expo(j, pw, theta)
            k2 = (0, xc)
            nd[k2] = nd.get(k2, 0.0) + pr * (1.0 - pf)
        dp = nd
    dist = {}
    for (j, x), pr in dp.items():
        xc = x + g_expo(j, pw, theta)
        dist[xc] = dist.get(xc, 0.0) + pr
    e = 0.0
    for x in sorted(dist):
        e += dist[x] * math.exp(-lam * x)
    return 1.0 - e


def brute_patterns(n):
    """All 2^n forget patterns -> list of (num_forgets, run_lengths tuple)."""
    out = []
    for bits in range(1 << n):
        runs = []
        j = 0
        f = 0
        for i in range(n):
            if (bits >> i) & 1:
                j += 1
                f += 1
            else:
                if j:
                    runs.append(j)
                j = 0
        if j:
            runs.append(j)
        out.append((f, tuple(runs)))
    return out


def t_brute(n, pw, pf_frac, theta, lam, patterns):
    """Exact-Fraction-weighted 2^n enumeration (independent of both DPs)."""
    groups = {}
    for f, runs in patterns:
        x = 0
        for j in runs:
            x += g_expo(j, pw, theta)
        key = (f, x)
        groups[key] = groups.get(key, 0) + 1
    e = 0.0
    q_frac = 1 - pf_frac
    for (f, x) in sorted(groups):
        wgt = (pf_frac ** f) * (q_frac ** (n - f)) * groups[(f, x)]
        e += float(wgt) * math.exp(-lam * x)
    return 1.0 - e


# ---------------------------------------------------------------------------
# Arm A — exact O95: mixture quantile of (theta_r - A)+ + Exp(lam),
# A = m*p_w the lattice-valued renewal age at death.
# ---------------------------------------------------------------------------
def age_probs_closed(n, pf):
    """P(A = m*p_w) = (1/N) p_f^m (1 + (N-m-1)(1-p_f)), m = 0..N-1 (floats)."""
    return [(pf ** m) * (1.0 + (n - m - 1) * (1.0 - pf)) / n for m in range(n)]


def age_probs_direct_frac(n, pf_frac):
    """Independent derivation: double loop over death wake k and trailing run m."""
    probs = [Fraction(0)] * n
    q = 1 - pf_frac
    for k in range(1, n + 1):
        for m in range(k):
            if m <= k - 2:
                pm = (pf_frac ** m) * q
            else:
                pm = pf_frac ** (k - 1)
            probs[m] += Fraction(1, n) * pm
    return probs


def o95_exact(pw, pf, theta, lam, n=None):
    """Exact continuous p95 of (theta - A)+ + Exp(lam); returns
    (quantile, S_piece, density_at_quantile)."""
    n = N_OF[pw] if n is None else n
    probs = age_probs_closed(n, pf)
    acc = {}
    for m in range(n):
        d = max(0.0, theta - m * pw)
        acc[d] = acc.get(d, 0.0) + probs[m]
    items = sorted(acc.items())
    total = sum(p for _, p in items)
    check(abs(total - 1.0) <= 1e-12, "age distribution sums to 1")
    s = 0.0
    kk = 0.0
    for idx, (d, p) in enumerate(items):
        s += p
        kk += p * math.exp(lam * d)
        hi = items[idx + 1][0] if idx + 1 < len(items) else math.inf
        if s > 0.95:
            x = math.log(kk / (s - 0.95)) / lam
            if d - 1e-12 <= x <= hi + 1e-12:
                fcdf = sum(pj * (1.0 - math.exp(-lam * (x - dj)))
                           for dj, pj in items if dj <= x)
                check(abs(fcdf - 0.95) <= 1e-9, "O95 CDF bracket at quantile")
                fcdf_lo = sum(pj * (1.0 - math.exp(-lam * (x - 1e-6 - dj)))
                              for dj, pj in items if dj <= x - 1e-6)
                check(fcdf_lo < 0.95, "O95 CDF strictly below just under quantile")
                return x, s, lam * (s - 0.95)
    check(False, "O95 quantile solver found no segment")


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
# Arm S — event-driven MC on the deterministic lattice (pinned draw layout).
# ---------------------------------------------------------------------------
def windows_from_forgets(forgot, pw, theta):
    """Exposure windows per the registered convention: a maximal run of j
    forgets starting after the stamp at wake a (a=0 -> the t=0 claim stamp)
    opens ((a+1)*p_w + theta, (a+j+1)*p_w) when j*p_w > theta (terminal runs
    use the same formula, ending exactly at (N+1)*p_w)."""
    wins = []
    n = len(forgot)
    a = 0
    j = 0
    for i in range(1, n + 1):
        if forgot[i - 1]:
            j += 1
        else:
            if j * pw > theta:
                wins.append(((a + 1) * pw + theta, (a + j + 1) * pw))
            a = i
            j = 0
    if j * pw > theta:
        wins.append(((a + 1) * pw + theta, (a + j + 1) * pw))
    return wins


def sim_claim(st, pw, pf, theta, p_d, n):
    """One claim per the pinned layout. Returns ('alive', hits) or
    ('dead', latency) or ('dead-nowake', None) or ('dead-notakeover', None)."""
    dead = st.u() < p_d
    upos = st.u()  # ALWAYS consumed
    if not dead:
        if n == 0:
            return ("alive", 0)
        forgot = [st.u() < pf for _ in range(n)]
        if theta == math.inf:
            return ("alive", 0)
        wins = windows_from_forgets(forgot, pw, theta)
        if not wins:
            return ("alive", 0)
        horizon = (n + 1) * pw
        hits = 0
        c = 0.0
        while True:
            c += -math.log(1.0 - st.u()) / LAM_T
            if c >= horizon:
                break
            for lo, hi in wins:
                if lo < c < hi:
                    hits += 1
                    break
        return ("alive", hits)
    if n == 0:
        return ("dead-nowake", None)
    k = int(upos * n) + 1
    if k > n:  # unreachable guard (u() < 1.0 always)
        k = n
    m = 0
    trailing = True
    lastcoins = [st.u() < pf for _ in range(k - 1)]
    for i in range(k - 2, -1, -1):
        if lastcoins[i] and trailing:
            m += 1
        else:
            trailing = False
    if theta == math.inf:
        return ("dead-notakeover", None)
    d = max(0.0, theta - m * pw)
    c = 0.0
    while c <= d:
        c += -math.log(1.0 - st.u()) / LAM_O
    check(c > d, "dead latency past takeable point")
    return ("dead", c)


def p95_emp(xs):
    s = sorted(xs)
    n = len(s)
    check(n > 0, "p95 sample non-empty")
    return s[max(0, math.ceil(0.95 * n) - 1)]


def run_point(st, pw, pf, theta, p_d, n_claims, n_wakes=None):
    n = N_OF[pw] if n_wakes is None else n_wakes
    alive = dead = stolen = nowake_dead = 0
    lats = []
    hist = [0, 0, 0, 0]
    for _ in range(n_claims):
        kind, val = sim_claim(st, pw, pf, theta, p_d, n)
        if kind == "alive":
            alive += 1
            if val >= 1:
                stolen += 1
            hist[min(val, 3)] += 1
        elif kind == "dead":
            dead += 1
            lats.append(val)
        elif kind == "dead-nowake":
            nowake_dead += 1
        else:
            dead += 1
    check(alive + dead + nowake_dead == n_claims, "point partition")
    t_s = stolen / alive if alive else None
    o95_s = p95_emp(lats) if lats else None
    return {"n": n_claims, "alive": alive, "dead": dead, "no_wake_dead": nowake_dead,
            "stolen": stolen, "T_S": t_s, "O95_S": o95_s,
            "multi_steal_hist_0_1_2_3plus": hist}


# ---------------------------------------------------------------------------
# Reporting legs with drawn wake gaps (jitter / empirical-anchor).
# ---------------------------------------------------------------------------
def sim_claim_gapdraw(st, gap_draw, grace, pf, theta, p_d, h_c):
    """Leg-J/leg-E conventions (fixtures reporting_only_legs): wakes at
    cumulative drawn gaps < H_c; overdue rule t > last_stamp + grace + theta;
    terminal window closes at H_c + grace."""
    dead = st.u() < p_d
    upos = st.u()  # ALWAYS consumed
    wakes = []
    t = 0.0
    while True:
        gap = gap_draw(st)
        check(gap > 0.0, "gap positive")
        if t + gap >= h_c:
            break
        t += gap
        wakes.append(t)
    forgot = [st.u() < pf for _ in wakes]
    n = len(wakes)
    if dead and n > 0:
        k = int(upos * n) + 1
        if k > n:
            k = n
        last_stamp = 0.0
        for i in range(k - 1):
            if not forgot[i]:
                last_stamp = wakes[i]
        t_death = wakes[k - 1]
        d = max(0.0, last_stamp + grace + theta - t_death)
        c = 0.0
        while c <= d:
            c += -math.log(1.0 - st.u()) / LAM_O
        return ("dead", c)
    # alive (or dead with zero realized wakes -> counts alive, zero exposure)
    stamps = [0.0] + [wakes[i] for i in range(n) if not forgot[i]]
    wins = []
    end_cap = h_c + grace
    for idx, s in enumerate(stamps):
        nxt = stamps[idx + 1] if idx + 1 < len(stamps) else end_cap
        lo = s + grace + theta
        if lo < nxt:
            wins.append((lo, nxt))
    if not wins:
        return ("alive", 0)
    hits = 0
    c = 0.0
    while True:
        c += -math.log(1.0 - st.u()) / LAM_T
        if c >= end_cap:
            break
        for lo, hi in wins:
            if lo < c < hi:
                hits += 1
                break
    return ("alive", hits)


def run_point_gapdraw(st, gap_draw, grace, pf, theta, p_d, h_c, n_claims):
    alive = dead = stolen = 0
    lats = []
    for _ in range(n_claims):
        kind, val = sim_claim_gapdraw(st, gap_draw, grace, pf, theta, p_d, h_c)
        if kind == "alive":
            alive += 1
            if val >= 1:
                stolen += 1
        else:
            dead += 1
            lats.append(val)
    check(alive + dead == n_claims, "gap-draw point partition")
    return {"n": n_claims, "alive": alive, "dead": dead,
            "T_S": stolen / alive if alive else None,
            "O95_S": p95_emp(lats) if lats else None}


# ---------------------------------------------------------------------------
# Decision machinery (registered order: REJECT -> APPROVE -> NULL).
# ---------------------------------------------------------------------------
def cell_key(cell):
    return "pw%d-pf%s" % (cell[0], ("%.2f" % cell[1]))


def median(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0:
        return None
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def decide(table):
    """table[(cell, theta)] = (T, O95); None metrics cannot certify."""
    feas = {}
    for cell in CELLS:
        feas[cell] = [th for th in THETAS
                      if table[(cell, th)][0] is not None
                      and table[(cell, th)][1] is not None
                      and table[(cell, th)][0] <= T_MAX
                      and table[(cell, th)][1] <= O95_MAX]
    empty = [cell for cell in CELLS if not feas[cell]]
    coverage = {th: sum(1 for cell in CELLS if th in feas[cell]) for th in THETAS}
    daggers = [th for th in THETAS if coverage[th] >= APPROVE_CELLS]
    if len(empty) >= REJECT_CELLS:
        pattern = "REJECT"
        theta_dagger = None
    elif daggers:
        pattern = "APPROVE"
        theta_dagger = min(daggers)
    else:
        pattern = "NULL"
        theta_dagger = None
    theta_star = {cell: (min(feas[cell]) if feas[cell] else None) for cell in CELLS}
    per_pw = {}
    for pw in P_W:
        cs = [c for c in CELLS if c[0] == pw]
        per_pw["p_w=%d" % pw] = {
            "feasible_share": "%d/3" % sum(1 for c in cs if feas[c]),
            "median_theta_star": median([theta_star[c] for c in cs if theta_star[c] is not None]),
        }
    per_pf = {}
    for pf in P_F:
        cs = [c for c in CELLS if c[1] == pf]
        per_pf["p_f=%.2f" % pf] = {
            "feasible_share": "%d/3" % sum(1 for c in cs if feas[c]),
            "median_theta_star": median([theta_star[c] for c in cs if theta_star[c] is not None]),
        }
    return {
        "feas": {cell_key(c): feas[c] for c in CELLS},
        "theta_star": {cell_key(c): theta_star[c] for c in CELLS},
        "infeasible_cells": [cell_key(c) for c in empty],
        "infeasible_count": len(empty),
        "coverage_per_theta": {str(th): coverage[th] for th in THETAS},
        "theta_dagger": theta_dagger,
        "theta_daggers_all": daggers,
        "pattern_ruling": pattern,
        "per_cadence": per_pw,
        "per_compliance": per_pf,
        "_feas_raw": {cell_key(c): feas[c] for c in CELLS},
    }


def main():
    # --- CHAINED ANCHOR: V027 silence-keyed baseline (run invalid on mismatch)
    print("[anchor] V027 silence-baseline leg", file=sys.stderr)
    anc = FX["chained_anchor_V027"]
    v_regimes = [("R1", anc["regimes_verbatim_from_V027_fixtures"]["R1_burst"]),
                 ("R2", anc["regimes_verbatim_from_V027_fixtures"]["R2_daily"]),
                 ("R3", anc["regimes_verbatim_from_V027_fixtures"]["R3_weekend"])]
    v_cols = [("C4", 0.25), ("C12", 1.0 / 12.0), ("C48", 1.0 / 48.0)]
    check(anc["check_rates_per_hour"] == {"C4": 0.25, "C12": 1.0 / 12.0, "C48": 1.0 / 48.0},
          "anchor: V027 check rates verbatim")
    v_thetas = anc["theta_grid_hours"]
    anchor_table = {}
    anchor_feas = {}
    for rn, reg in v_regimes:
        w, mm, big_m = reg["w"], reg["m_hours"], reg["M"]
        for cn, lam in v_cols:
            feas_list = []
            for th in v_thetas:
                q = 0.0
                for wi, mi in zip(w, mm):
                    q += wi * math.exp(-th / mi) * (lam * mi) / (1.0 + lam * mi)
                t_a = 1.0 - (1.0 - q) ** big_m
                o_a = th + math.log(20.0) / lam
                anchor_table["%s-%s@%g" % (rn, cn, th)] = {"T": t_a, "O95": o_a}
                if t_a <= T_MAX and o_a <= O95_MAX:
                    feas_list.append(th)
            anchor_feas["%s-%s" % (rn, cn)] = feas_list
    committed = anc["committed_feas_map"]
    for cell, expect in committed.items():
        check(anchor_feas[cell] == expect,
              "anchor: Feas(%s) reproduces committed map" % cell)
    for cell, expect_star in anc["committed_theta_star"].items():
        check(min(anchor_feas[cell]) == expect_star, "anchor: theta*(%s)" % cell)
    check(sum(1 for v in anchor_feas.values() if not v) == anc["committed_infeasible_count"],
          "anchor: committed infeasible count 6")
    anchor_ok = True

    # --- Arm A: all 45 decision points, exact ------------------------------
    print("[arm A] exact DP + quantile", file=sys.stderr)
    arm_a = {}
    o95_meta = {}
    for cell in CELLS:
        pw, pf = cell
        prev_t = None
        prev_o = None
        for th in THETAS:
            t_a = t_exact(pw, pf, th, LAM_T)
            o_a, s_piece, dens = o95_exact(pw, pf, th, LAM_O)
            check(0.0 <= t_a <= 1.0, "T_A in [0,1]")
            if prev_t is not None:
                # 1e-12 absolute floor: DP float residue at true-T ~ 1e-60
                # rounds to ~1e-14-scale noise (disclosed; band margin 0.05)
                check(t_a <= prev_t + 1e-12, "T_A monotone nonincreasing in theta_r")
                check(o_a > prev_o, "O95_A monotone increasing in theta_r")
            prev_t, prev_o = t_a, o_a
            arm_a[(cell, th)] = (t_a, o_a)
            o95_meta[(cell, th)] = (s_piece, dens)
    # T_A monotone nondecreasing in p_f at fixed (p_w, theta)
    for pw in P_W:
        for th in THETAS:
            vals = [arm_a[((pw, pf), th)][0] for pf in P_F]
            check(vals[0] <= vals[1] + 1e-12 and vals[1] <= vals[2] + 1e-12,
                  "T_A monotone in p_f")

    # cross-arm A2: exposure-distribution DP on ALL 45 points
    print("[arm A] cross-check: distribution DP (45 points)", file=sys.stderr)
    for cell in CELLS:
        pw, pf = cell
        for th in THETAS:
            t_alt = t_dist(pw, pf, th, LAM_T)
            check(abs(t_alt - arm_a[(cell, th)][0]) <= 1e-9,
                  "cross-arm distribution DP agrees at %s@%g" % (cell_key(cell), th))
    # cross-arm A3: exact-Fraction brute force on every p_w in {12, 24} point
    print("[arm A] cross-check: 2^N Fraction brute force", file=sys.stderr)
    for pw in (12, 24):
        pats = brute_patterns(N_OF[pw])
        for pf in P_F:
            for th in THETAS:
                t_bf = t_brute(N_OF[pw], pw, P_F_FRAC[pf], th, LAM_T, pats)
                check(abs(t_bf - arm_a[((pw, pf), th)][0]) <= 1e-12,
                      "brute force agrees at pw%d pf%.2f theta %g" % (pw, pf, th))
    # age-distribution dual derivation, exact Fractions
    for pw in P_W:
        n = N_OF[pw]
        for pf in P_F:
            direct = age_probs_direct_frac(n, P_F_FRAC[pf])
            check(sum(direct) == 1, "age distribution sums to 1 exactly (Fractions)")
            closed = age_probs_closed(n, pf)
            for m in range(n):
                cf = (P_F_FRAC[pf] ** m) * (1 + (n - m - 1) * (1 - P_F_FRAC[pf])) * Fraction(1, n)
                check(direct[m] == cf, "age closed form == direct (Fractions)")
                check(abs(closed[m] - float(cf)) <= 1e-15, "age float matches Fraction")

    # hand pins (fixtures-committed derivations)
    pins = {p["name"]: p for p in FX["hand_derived_pins"]}
    p1 = pins["pin_1_single_full_run_identity"]
    check(abs(t_exact_n(7, 24, 0.25, 150, LAM_T) - p1["expected"]["T_A"]) <= p1["tolerance"],
          "pin 1 single-full-run identity")
    p2 = pins["pin_2_O95_pf0_closed_form"]
    o95_pf0, _, _ = o95_exact(24, 0.0, 24, LAM_O)
    check(abs(o95_pf0 - p2["expected"]["O95_A"]) <= p2["tolerance"], "pin 2 O95 at p_f=0")
    p3 = pins["pin_3_C48_renewal_side_identity"]
    check(abs(math.log(20.0) * 48.0 - p3["expected"]["ln20_times_48"]) <= 1e-12,
          "pin 3 constant")
    p4 = pins["pin_4_theta_inf_T_zero"]
    for cell in CELLS:
        check(t_exact(cell[0], cell[1], 1e9, LAM_T) == p4["expected"]["T_A"],
              "pin 4 T_A(theta->inf) == 0 exactly")
    # registered self-check: p_f = 0 AND alive => zero exposure exactly
    for pw in P_W:
        for th in THETAS:
            check(t_exact(pw, 0.0, th, LAM_T) == 0.0, "p_f=0 => T_A = 0 exactly")

    a_decision = decide(arm_a)

    # knife-edge flags (intake decision 9)
    knife = []
    for cell in CELLS:
        for th in THETAS:
            t_a, o_a = arm_a[(cell, th)]
            if abs(t_a - T_MAX) <= 0.002 or abs(o_a - O95_MAX) <= 0.5:
                knife.append({"point": "%s@%g" % (cell_key(cell), th),
                              "T_A": t_a, "O95_A": o_a})

    # C48 reporting column (exact, seedless) + pin-3 dominance assert
    c48 = {}
    for cell in CELLS:
        pw, pf = cell
        for th in THETAS:
            o_c48, _, _ = o95_exact(pw, pf, th, LAM_C48)
            check(o_c48 >= p3["expected"]["ln20_times_48"] - p3["tolerance"],
                  "pin 3 C48 renewal-side dominance")
            c48["%s@%g" % (cell_key(cell), th)] = o_c48
    # theta_r = 168 exclusion re-check (intake decision 12), exact
    excl168 = {}
    for cell in CELLS:
        pw, pf = cell
        o_168, _, _ = o95_exact(pw, pf, 168, LAM_O)
        check(o_168 > O95_MAX, "theta_r=168 busts the orphan band (exclusion holds)")
        excl168[cell_key(cell)] = o_168

    # --- gate pre-check (BEFORE any MC draw; registered >= 2.5 sigma rule) --
    precheck = {}
    for cell in CELLS:
        for th in THETAS:
            t_a, o_a = arm_a[(cell, th)]
            se_t = math.sqrt(max(t_a * (1.0 - t_a), 1e-300) / N_ALIVE_EXP)
            s_piece, dens = o95_meta[(cell, th)]
            se_o = math.sqrt(0.95 * 0.05 / N_DEAD_EXP) / dens
            tol_t_eff = max(GATE_T, SIGMA_MULT * se_t)
            tol_o_eff = max(GATE_O_ABS, GATE_O_REL * o_a, SIGMA_MULT * se_o)
            precheck["%s@%g" % (cell_key(cell), th)] = {
                "SE_T_pp": se_t * 100.0,
                "registered_T_tol_sigma": (GATE_T / se_t if se_t > 0 else None),
                "T_tol_eff_pp": tol_t_eff * 100.0,
                "T_raised": tol_t_eff > GATE_T,
                "SE_O95_h": se_o,
                "registered_O95_tol_sigma": max(GATE_O_ABS, GATE_O_REL * o_a) / se_o,
                "O95_tol_eff_h": tol_o_eff,
                "O95_raised": tol_o_eff > max(GATE_O_ABS, GATE_O_REL * o_a),
                "S_piece": s_piece,
            }

    # --- Arm S main leg (seed 20260756) -------------------------------------
    print("[arm S] main leg", file=sys.stderr)
    st = Stream(SEED_MAIN)
    arm_s_pts = {}
    for cell in CELLS:
        pw, pf = cell
        for th in THETAS:
            arm_s_pts[(cell, th)] = run_point(st, pw, pf, th, P_D, M_S)
        print("[arm S] %s done" % cell_key(cell), file=sys.stderr)
    check(st.sentinel_ok(), "main leg draw-count sentinel")
    main_draws = st.n

    gate_rows = {}
    failing_eff = []
    t_fail_reg = o_fail_reg = t_fail_eff = o_fail_eff = 0
    for key in sorted(arm_s_pts, key=lambda k: (k[0][0], k[0][1], k[1])):
        (cell, th) = key
        t_a, o_a = arm_a[key]
        pc = precheck["%s@%g" % (cell_key(cell), th)]
        pt = arm_s_pts[key]
        t_s, o_s = pt["T_S"], pt["O95_S"]
        dt = abs(t_s - t_a)
        do = abs(o_s - o_a)
        tol_o_reg = max(GATE_O_ABS, GATE_O_REL * o_a)
        t_ok_reg = dt <= GATE_T + 1e-12
        o_ok_reg = do <= tol_o_reg + 1e-9
        t_ok_eff = dt <= pc["T_tol_eff_pp"] / 100.0 + 1e-12
        o_ok_eff = do <= pc["O95_tol_eff_h"] + 1e-9
        se_t_r = math.sqrt(max(t_a * (1.0 - t_a), 1e-300) / pt["alive"]) if pt["alive"] else None
        se_o_r = pc["SE_O95_h"] * math.sqrt(N_DEAD_EXP / pt["dead"]) if pt["dead"] else None
        gate_rows["%s@%g" % (cell_key(cell), th)] = {
            "T_A": t_a, "T_S": t_s, "dT_pp": dt * 100.0,
            "T_gate_registered_ok": t_ok_reg, "T_gate_effective_ok": t_ok_eff,
            "T_tol_eff_pp": pc["T_tol_eff_pp"],
            "z_T": (dt / se_t_r if se_t_r and se_t_r > 0 else None),
            "O95_A": o_a, "O95_S": o_s, "dO95_h": do,
            "O95_tol_registered_h": tol_o_reg, "O95_tol_eff_h": pc["O95_tol_eff_h"],
            "O95_gate_registered_ok": o_ok_reg, "O95_gate_effective_ok": o_ok_eff,
            "z_O95": (do / se_o_r if se_o_r else None),
            "n_alive": pt["alive"], "n_dead": pt["dead"],
        }
        t_fail_reg += 0 if t_ok_reg else 1
        o_fail_reg += 0 if o_ok_reg else 1
        t_fail_eff += 0 if t_ok_eff else 1
        o_fail_eff += 0 if o_ok_eff else 1
        if not (t_ok_eff and o_ok_eff):
            failing_eff.append(key)
    gates_eff_all_pass = t_fail_eff == 0 and o_fail_eff == 0

    arm_s_table = {k: (v["T_S"], v["O95_S"]) for k, v in arm_s_pts.items()}
    s_decision = decide(arm_s_table)

    # --- stability leg (seed 20260757) --------------------------------------
    print("[arm S] stability leg", file=sys.stderr)
    st2 = Stream(SEED_STAB)
    stab_table = {}
    for cell in CELLS:
        pw, pf = cell
        for th in THETAS:
            pt = run_point(st2, pw, pf, th, P_D, M_STAB)
            stab_table[(cell, th)] = (pt["T_S"], pt["O95_S"])
    check(st2.sentinel_ok(), "stability leg draw-count sentinel")
    stab_decision = decide(stab_table)
    stability_reproduced = stab_decision["pattern_ruling"] == a_decision["pattern_ruling"]

    # --- reporting-only legs (seed 20260758, pinned stream order) -----------
    print("[reporting] legs J, H4, H24, D02, D30, E", file=sys.stderr)
    st3 = Stream(SEED_REP)
    rep = {}
    # leg J: exponential wake jitter at mean p_w
    leg = {}
    for cell in CELLS:
        pw, pf = cell
        for th in THETAS:
            def gap_exp(s, _pw=pw):
                return -_pw * math.log(1.0 - s.u())
            r = run_point_gapdraw(st3, gap_exp, pw, pf, th, P_D, H_C, M_REP)
            leg["%s@%g" % (cell_key(cell), th)] = r
    rep["leg_J_exp_wake_jitter"] = leg
    # legs H4 / H24: shorter claim holds on the deterministic lattice
    for h_c in H_C_REP:
        leg = {}
        for cell in CELLS:
            pw, pf = cell
            n_w = h_c // pw
            for th in THETAS:
                r = run_point(st3, pw, pf, th, P_D, M_REP, n_wakes=n_w)
                leg["%s@%g" % (cell_key(cell), th)] = r
        rep["leg_H%d" % h_c] = leg
    # legs D02 / D30: p_d sensitivity on the main machinery
    for pd_leg in (0.02, 0.30):
        leg = {}
        for cell in CELLS:
            pw, pf = cell
            for th in THETAS:
                r = run_point(st3, pw, pf, th, pd_leg, M_REP)
                leg["%s@%g" % (cell_key(cell), th)] = r
        rep["leg_D_p_d=%s" % pd_leg] = leg
    # leg E: empirical-anchor at the quoted multisets
    leg = {}
    for th in THETAS:
        def gap_emp(s):
            return GAPS19[int(s.u() * 19)]
        # per-claim H_c drawn inside a wrapper: emulate by a custom loop
        alive = dead = stolen = 0
        lats = []
        for _ in range(M_REP):
            u_hc = st3.u()
            h_c = LIFETIMES[int(u_hc * 11)]
            kind, val = sim_claim_gapdraw(st3, gap_emp, LEG_E_GRACE, LEG_E_PF,
                                          th, P_D, h_c)
            if kind == "alive":
                alive += 1
                if val >= 1:
                    stolen += 1
            else:
                dead += 1
                lats.append(val)
        leg["theta_r=%g" % th] = {
            "n": M_REP, "alive": alive, "dead": dead,
            "T_S": stolen / alive if alive else None,
            "O95_S": p95_emp(lats) if lats else None,
        }
    rep["leg_E_empirical_anchor"] = leg
    check(st3.sentinel_ok(), "reporting legs draw-count sentinel")

    # --- aux stream (seed 20260759): A1, A2, A3 ------------------------------
    print("[aux] A1/A2 identity legs", file=sys.stderr)
    st4 = Stream(SEED_AUX)
    a1_windows = 0
    a1_steals = 0
    for cell in CELLS:
        pw, _ = cell
        for _ in range(M_AUX):
            kind, val = sim_claim(st4, pw, 0.0, 24, P_D, N_OF[pw])
            if kind == "alive":
                if val >= 1:
                    a1_steals += 1
    check(a1_steals == 0, "aux A1: p_f=0 alive claims => zero steals exactly")
    check(t_exact(2, 0.0, 24, LAM_T) == 0.0, "aux A1: p_f=0 exact exposure zero")
    a2_steals = 0
    a2_takeovers = 0
    for cell in CELLS:
        pw, pf = cell
        for _ in range(M_AUX):
            kind, val = sim_claim(st4, pw, pf, math.inf, P_D, N_OF[pw])
            if kind == "alive" and val >= 1:
                a2_steals += 1
            if kind == "dead":
                a2_takeovers += 1
    check(a2_steals == 0, "aux A2: theta_r->inf => T = 0 exactly")
    check(a2_takeovers == 0, "aux A2: theta_r->inf => no takeovers")
    print("[aux] A3 gate diagnostics (%d failing points)" % len(failing_eff),
          file=sys.stderr)
    diagnostics = {}
    for key in sorted(failing_eff, key=lambda k: (k[0][0], k[0][1], k[1])):
        (cell, th) = key
        pw, pf = cell
        pt = run_point(st4, pw, pf, th, P_D, M_DIAG)
        t_a, o_a = arm_a[key]
        pc = precheck["%s@%g" % (cell_key(cell), th)]
        dt = abs(pt["T_S"] - t_a)
        do = abs(pt["O95_S"] - o_a)
        diagnostics["%s@%g" % (cell_key(cell), th)] = {
            "M_diag": M_DIAG,
            "T_S_16x": pt["T_S"], "dT_pp_16x": dt * 100.0,
            "T_within_eff_tol_at_16x": dt <= pc["T_tol_eff_pp"] / 100.0 + 1e-12,
            "O95_S_16x": pt["O95_S"], "dO95_h_16x": do,
            "O95_within_eff_tol_at_16x": do <= pc["O95_tol_eff_h"] + 1e-9,
        }
    check(st4.sentinel_ok(), "aux stream draw-count sentinel")
    diag_all_within = all(
        d["T_within_eff_tol_at_16x"] and d["O95_within_eff_tol_at_16x"]
        for d in diagnostics.values()) if diagnostics else True

    # --- final ruling (registered order REJECT -> APPROVE -> NULL;
    #     handling protocol: effective-gate breach or stability failure bars
    #     APPROVE only — fixtures gate_calibration_precheck item 3) ----------
    pattern = a_decision["pattern_ruling"]
    if pattern == "APPROVE" and not (gates_eff_all_pass and stability_reproduced):
        pattern = "NULL"
        ruling_label = "NULL (APPROVE barred by gate/stability condition)"
    else:
        ruling_label = pattern
    ruling = pattern

    # APPROVE row extras: compliance floor + per-cadence requirement
    approve_row = None
    if a_decision["theta_dagger"] is not None:
        td = a_decision["theta_dagger"]
        feas_raw = a_decision["_feas_raw"]
        floor = None
        for pf in P_F:
            if all(td in feas_raw[cell_key((pw, pf))] for pw in P_W):
                floor = pf
        per_cadence = {}
        for pw in P_W:
            ok_pfs = [pf for pf in P_F if td in feas_raw[cell_key((pw, pf))]]
            per_cadence["p_w=%d" % pw] = {
                "theta_dagger_feasible_at_p_f": ok_pfs,
                "max_tolerated_p_f": max(ok_pfs) if ok_pfs else None,
            }
        approve_row = {
            "theta_dagger_h": td,
            "coverage_at_dagger": a_decision["coverage_per_theta"][str(td)],
            "all_daggers_with_coverage_ge_8": a_decision["theta_daggers_all"],
            "compliance_floor_p_f": floor,
            "per_cadence_requirement": per_cadence,
            "planted_72_lies_at_dagger": (td == 72),
            "planted_72_coverage": a_decision["coverage_per_theta"]["72"],
        }

    for dec in (a_decision, s_decision, stab_decision):
        dec.pop("_feas_raw", None)

    out = {
        "proposal": FX["source"]["proposal"],
        "chained_anchor_V027": {
            "reproduced_committed_feas_map": anchor_ok,
            "recomputed_feas": anchor_feas,
            "table_9x6": anchor_table,
            "delta_feas_headline": {
                "renewal_nonempty_cells": 9 - a_decision["infeasible_count"],
                "silence_nonempty_cells": 9 - FX["chained_anchor_V027"]["committed_infeasible_count"],
                "note": "shared bands (T <= 0.05, O95 <= 120 h); axes differ by design (p_w x p_f vs regime x tempo) — cell-addressable comparison via the shipped tables",
            },
        },
        "arm_A": {
            "table": {"%s@%g" % (cell_key(c), th): {"T_A": arm_a[(c, th)][0],
                                                    "O95_A": arm_a[(c, th)][1]}
                      for c in CELLS for th in THETAS},
            "decision": a_decision,
            "knife_edge_points": knife,
        },
        "arm_S_main": {
            "seed": SEED_MAIN, "M_S": M_S, "draws": main_draws,
            "table": {"%s@%g" % (cell_key(c), th): {
                "T_S": arm_s_pts[(c, th)]["T_S"],
                "O95_S": arm_s_pts[(c, th)]["O95_S"],
                "n_alive": arm_s_pts[(c, th)]["alive"],
                "n_dead": arm_s_pts[(c, th)]["dead"]}
                for c in CELLS for th in THETAS},
            "decision_on_MC_values": s_decision,
        },
        "gates": {
            "registered": "|T_S - T_A| <= 1.0 pp AND |O95_S - O95_A| <= max(4 h, 5%), every point; effective tolerance = max(registered, 2.5 x predicted SE) per the fixtures pre-check rule",
            "precheck_before_any_run": precheck,
            "per_point": gate_rows,
            "registered_failures": {"T": t_fail_reg, "O95": o_fail_reg},
            "effective_failures": {"T": t_fail_eff, "O95": o_fail_eff},
            "all_effective_pass": gates_eff_all_pass,
        },
        "stability_leg": {
            "seed": SEED_STAB, "M_S": M_STAB,
            "decision": stab_decision,
            "reproduces_main_ruling": stability_reproduced,
        },
        "reporting_only": {
            "C48_column_exact_O95": c48,
            "C48_identity": FX["chained_anchor_V027"]["C48_identity"],
            "theta_168_exclusion_exact_O95": excl168,
            "legs": rep,
            "note": "registered as unable to flip the decision",
        },
        "aux": {
            "A1_pf0_alive_steals": a1_steals,
            "A2_theta_inf_steals": a2_steals,
            "A3_gate_diagnostics_16x": diagnostics,
            "A3_all_failing_points_within_eff_tolerance_at_16x": diag_all_within,
        },
        "ruling": ruling,
        "ruling_label": ruling_label,
        "approve_row": approve_row,
        "model_basis": FX["boundaries_registered"]["model_basis"],
        "self_checks_passed": None,
    }

    # Headline stdout (deterministic).
    print("verdict-031 lease-renewal — results")
    print("chained anchor: V027 committed Feas map reproduced: %s" % anchor_ok)
    print("arm A (exact): Feas per cell:")
    for c in CELLS:
        key = cell_key(c)
        print("  %s: Feas=%s theta*=%s" % (key, a_decision["feas"][key],
                                           a_decision["theta_star"][key]))
    print("arm A: infeasible cells %d/9: %s" % (a_decision["infeasible_count"],
                                                a_decision["infeasible_cells"]))
    print("arm A: coverage per theta_r: %s" % a_decision["coverage_per_theta"])
    print("arm A: theta_r-dagger: %s (APPROVE needs coverage >= 8/9; all daggers: %s)"
          % (a_decision["theta_dagger"], a_decision["theta_daggers_all"]))
    print("gates: registered failures T %d/45, O95 %d/45; EFFECTIVE failures T %d/45, O95 %d/45; all_effective_pass=%s"
          % (t_fail_reg, o_fail_reg, t_fail_eff, o_fail_eff, gates_eff_all_pass))
    print("arm S main: decision on MC values: %s (infeasible %d/9)"
          % (s_decision["pattern_ruling"], s_decision["infeasible_count"]))
    print("stability leg: %s (reproduces main: %s)"
          % (stab_decision["pattern_ruling"], stability_reproduced))
    print("aux A1 p_f=0 steals: %d ; aux A2 theta_r=inf steals: %d"
          % (a1_steals, a2_steals))
    print("aux A3: effective-gate failing points re-measured at 16x: %d ; all within eff tolerance at 16x: %s"
          % (len(diagnostics), diag_all_within))
    if approve_row:
        print("approve row: theta_r-dagger=%s h (coverage %s/9), compliance floor p_f=%s, planted 72 at dagger: %s (72 covers %s/9)"
              % (approve_row["theta_dagger_h"], approve_row["coverage_at_dagger"],
                 approve_row["compliance_floor_p_f"],
                 approve_row["planted_72_lies_at_dagger"],
                 approve_row["planted_72_coverage"]))
    print("RULING: %s" % ruling_label)

    out["self_checks_passed"] = CHECKS + 1  # + the final write-side check below
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    check(out["ruling"] in ("APPROVE", "REJECT", "NULL"), "ruling well-formed")
    print("SELF-CHECKS: %d passed, 0 failed" % CHECKS)


if __name__ == "__main__":
    main()
