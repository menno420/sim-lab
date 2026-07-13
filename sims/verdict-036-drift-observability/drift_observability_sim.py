#!/usr/bin/env python3
"""verdict-036 — drift-regime observability (idea-engine PROPOSAL 034).

Fully hermetic NUMERIC SIMULATION (rung 1): an operating-characteristic sweep
of 18 pre-registered cheap threshold detectors (trailing pinned-vol Sharpe /
up-share x window {63,126,252} x threshold position {0.3,0.5,0.7}) on a
pinned two-arm regime-switching return stream whose two states ARE V024's two
committed arms (state D basket-Sharpe 1.15, state Z zero drift), scored as
trust-misallocation removed vs the EXACT best-static-prior baseline
min(pi_D, pi_Z) per (occupancy, sojourn) cell. ZERO real market bars; no
dev-candidate is evaluated on any data; the owner-gated post-2026 protocol is
untouched (P022's harvest-hazard clause inherited verbatim).

Reads exactly ONE file: its own committed fixtures.json (the
pre-registration), cross-checked against in-code literals at start. No
network, no git, no wall clock. stdout and results.json are byte-identical
across process runs (verified by external diff). Progress goes to stderr
only (excluded from the byte-diff by construction).

Run: python3 sims/verdict-036-drift-observability/drift_observability_sim.py
Exit 0 iff all self-checks pass.
"""

import json
import math
import os
import random
import sys
from fractions import Fraction
from statistics import NormalDist

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- constants
DELTA = 1.15 / math.sqrt(252.0)          # 0.07244319066010188 (asserted)
T = 2595
SC0 = 252                                 # scoring start (0-indexed bar)
NSC = T - SC0                             # 2343 scored bars per path
S_GRID = (126, 252, 1008)
CELLS = [(a, b) for a in S_GRID for b in S_GRID]   # lexicographic
WS = (63, 126, 252)
LAMS = (0.3, 0.5, 0.7)
SQ252 = math.sqrt(252.0)
M_MAIN = 1000
M_STAB = 250
M_FROZEN = 500
M_OCC = 400
M_RHO = 50
SEED_MAIN = 20260772
SEED_STAB = 20260773
SEED_REPORT = 20260774
SEED_AUX = 20260775
WIN_MARGIN = 0.10                         # dE_oracle win line (exact 1/10)
REJECT_BAR = 3
APPROVE_BAR = 7
ICDF = NormalDist().inv_cdf              # exactly ONE uniform per normal;
                                          # a drawn 0.0 raises = run invalid.

# V024 panel machinery constants (occupancy leg, IID/rho=0.3 cell)
J_PANEL = 9
PB = 21
NP = 123
EVAL_P0 = 12
NEVAL = 111
SIGMA_ANN = 0.30
SIGMA_D = SIGMA_ANN / math.sqrt(252.0)
COST = 0.001
RHO_PANEL = 0.3
MU_D_PANEL = 1.15 * SIGMA_D * math.sqrt(RHO_PANEL + (1.0 - RHO_PANEL) / 9.0) \
    / math.sqrt(252.0)
G6 = [(L, k) for L in (63, 126, 252) for k in (2, 3)]   # mom, eq only
PHI_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
ANCHOR_Q99_PHI0 = 0.6041012959180625      # V024 IID/rho=.3/sbh=0   @ cd47c06
ANCHOR_Q99_PHI1 = 0.36690217335833175     # V024 IID/rho=.3/sbh=1.15 @ cd47c06
ANCHOR_COUNT_MAX = 12
SQRT12 = math.sqrt(12.0)

# derived detector constants
PD = 0.5 * (1.0 + math.erf(DELTA / math.sqrt(2.0)))
H_SR = {lam: lam * 1.15 for lam in LAMS}
U_UP = {lam: 0.5 + lam * (PD - 0.5) for lam in LAMS}
K_UP = {(w, lam): math.ceil(U_UP[lam] * w) for w in WS for lam in LAMS}
VARIANTS = [("SR", w, lam) for w in WS for lam in LAMS] + \
           [("UP", w, lam) for w in WS for lam in LAMS]
NV = len(VARIANTS)
SR_IDX = [i for i, v in enumerate(VARIANTS) if v[0] == "SR"]

N_CHECKS = 0


def check(cond, msg):
    global N_CHECKS
    if not cond:
        print("SELF-CHECK FAILED: " + msg, file=sys.stderr)
        print("SELF-CHECKS: FAILED — " + msg)
        sys.exit(1)
    N_CHECKS += 1


def log(msg):
    print(msg, file=sys.stderr)
    sys.stderr.flush()


# --------------------------------------------------------------- Arm A exact
def phi_cdf(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def binom_tail_ge(w, p, k):
    """P(Bin(w,p) >= k) — upper tail sum (routine 1)."""
    if k <= 0:
        return 1.0
    if k > w:
        return 0.0
    q = 1.0 - p
    return sum(math.comb(w, j) * (p ** j) * (q ** (w - j))
               for j in range(k, w + 1))


def binom_cdf_le(w, p, k):
    """P(Bin(w,p) <= k) — lower CDF sum, independently written (routine 2)."""
    if k < 0:
        return 0.0
    if k >= w:
        return 1.0
    tot = 0.0
    for j in range(0, k + 1):
        tot += math.comb(w, j) * (p ** j) * ((1.0 - p) ** (w - j))
    return tot


def arm_a_oc():
    """Exact pure-window operating characteristics for all 18 variants."""
    oc = []
    for (stat, w, lam) in VARIANTS:
        if stat == "SR":
            h = H_SR[lam]
            tpr = phi_cdf((1.15 - h) * math.sqrt(w / 252.0))
            fpr = phi_cdf(-h * math.sqrt(w / 252.0))
        else:
            k = K_UP[(w, lam)]
            tpr = binom_tail_ge(w, PD, k)
            fpr = binom_tail_ge(w, 0.5, k)
        oc.append((tpr, fpr))
    return oc


def chain_moments(sd, sz):
    """Exact occupancy/flip expectations and variances (fixture formulas)."""
    piD = Fraction(sd, sd + sz)
    pf = float(piD)
    ph = 1.0 - 1.0 / sd - 1.0 / sz
    s = 0.0
    pk = 1.0
    for g in range(1, T):
        pk *= ph
        s += (T - g) * pk
    var_occ = pf * (1 - pf) * (T + 2.0 * s)
    N = T - 1
    p = 1.0 / (sd + sz)
    s2 = 0.0
    pk = 1.0
    for g in range(1, N):
        s2 += (N - g) * pk
        pk *= ph
        if pk == 0.0:
            break
    var_f = N * p * (1 - p) - 2.0 * p * p * s2
    return piD, var_occ, (T - 1) / (sd + sz), var_f


# ------------------------------------------------------------ path machinery
def gen_path(rng, sd, sz):
    """Pinned draw order: chain pass (1 stationary + T-1 transitions), then
    return pass (T normals). Returns (states bytearray, x list, flips_dz,
    flips_zd, nD_bars_total)."""
    rr = rng.random
    piD = sd / (sd + sz)
    stay_d = 1.0 - 1.0 / sd
    stay_z = 1.0 - 1.0 / sz
    states = bytearray(T)
    st = 1 if rr() < piD else 0
    states[0] = st
    fdz = fzd = 0
    nd = st
    for t in range(1, T):
        u = rr()
        if st:
            if u >= stay_d:
                st = 0
                fdz += 1
        else:
            if u >= stay_z:
                st = 1
                fzd += 1
        states[t] = st
        nd += st
    x = [(DELTA if states[t] else 0.0) + ICDF(rr()) for t in range(T)]
    return states, x, fdz, fzd, nd


def path_stats(states, x, want_real=False):
    """Per-path detector counts. Returns (nD, per-variant list of
    (C, cTP), vals_by_w, counts_by_w, truth, real per-(w,lam) (C,cTP) or None).
    C = classified-on scored bars; cTP = classified-on among true-D bars."""
    P = [0.0] * (T + 1)
    s = 0.0
    for t in range(T):
        s += x[t]
        P[t + 1] = s
    U = [0] * (T + 1)
    c = 0
    for t in range(T):
        if x[t] > 0.0:
            c += 1
        U[t + 1] = c
    truth = states[SC0:]
    Didx = [i for i, d in enumerate(truth) if d]
    nD = len(Didx)
    vals_by_w = {}
    counts_by_w = {}
    if want_real:
        Q = [0.0] * (T + 1)
        s = 0.0
        for t in range(T):
            s += x[t] * x[t]
            Q[t + 1] = s
        real_by_w = {}
    for w in WS:
        sc = SQ252 / w
        vals_by_w[w] = [(a - b) * sc
                        for a, b in zip(P[SC0 + 1:], P[SC0 + 1 - w:T + 1 - w])]
        counts_by_w[w] = [a - b
                          for a, b in zip(U[SC0 + 1:], U[SC0 + 1 - w:T + 1 - w])]
        if want_real:
            rl = []
            ap = rl.append
            w1 = w - 1.0
            for a, b, qa, qb in zip(P[SC0 + 1:], P[SC0 + 1 - w:T + 1 - w],
                                    Q[SC0 + 1:], Q[SC0 + 1 - w:T + 1 - w]):
                m = (a - b) / w
                var = ((qa - qb) - w * m * m) / w1
                ap(m / math.sqrt(var) * SQ252)
            real_by_w[w] = rl
    per_var = []
    for (stat, w, lam) in VARIANTS:
        if stat == "SR":
            h = H_SR[lam]
            vals = vals_by_w[w]
            C = 0
            for v in vals:
                if v >= h:
                    C += 1
            cTP = 0
            for i in Didx:
                if vals[i] >= h:
                    cTP += 1
        else:
            k = K_UP[(w, lam)]
            counts = counts_by_w[w]
            C = 0
            for v in counts:
                if v >= k:
                    C += 1
            cTP = 0
            for i in Didx:
                if counts[i] >= k:
                    cTP += 1
        per_var.append((C, cTP))
    real = None
    if want_real:
        real = []
        for w in WS:
            for lam in LAMS:
                h = H_SR[lam]
                vals = real_by_w[w]
                C = 0
                for v in vals:
                    if v >= h:
                        C += 1
                cTP = 0
                for i in Didx:
                    if vals[i] >= h:
                        cTP += 1
                real.append((C, cTP))
    return nD, per_var, vals_by_w, counts_by_w, truth, real


def collect_lags(states, vals_by_w, counts_by_w, lag_store):
    """Post-flip detection lags (D7 conventions): flips at f in [SC0, T);
    lag = first t >= f with classification == new state, censored at the
    next flip or T. lag_store[vi][dir] -> (list of lags, censored count)."""
    flips = [f for f in range(max(SC0, 1), T) if states[f - 1] != states[f]]
    if not flips:
        return
    nexts = flips[1:] + [T]
    for vi, (stat, w, lam) in enumerate(VARIANTS):
        if stat == "SR":
            arr = vals_by_w[w]
            thr = H_SR[lam]
        else:
            arr = counts_by_w[w]
            thr = K_UP[(w, lam)]
        for f, nx in zip(flips, nexts):
            new = states[f]
            d = 0 if new == 0 else 1        # 1 = Z->D flip, 0 = D->Z flip
            found = -1
            for t in range(f, nx):
                cls = 1 if arr[t - SC0] >= thr else 0
                if cls == new:
                    found = t - f
                    break
            lags, cens = lag_store[vi][d]
            if found >= 0:
                lags.append(found)
            else:
                lag_store[vi][d] = (lags, cens + 1)


def quant(sorted_vals, q):
    """Left-continuous empirical quantile (V024's convention)."""
    return sorted_vals[math.ceil(q * len(sorted_vals)) - 1]


def med_p90(lags):
    if not lags:
        return None, None
    sv = sorted(lags)
    return quant(sv, 0.50), quant(sv, 0.90)


# ------------------------------------------------------ decision twin A / B
def wins_A(mis_table, n_scored):
    """Evaluator A: pure integer arithmetic. mis_table[ci][vi] = int.
    win iff min_pi - mis/N >= 1/10  <=>  10*(num*N - mis*den) >= den*N."""
    out = []
    for ci, (sd, sz) in enumerate(CELLS):
        num = min(sd, sz)
        den = sd + sz
        row = []
        for vi in range(NV):
            mis = mis_table[ci][vi]
            row.append(10 * (num * n_scored - mis * den) >= den * n_scored)
        out.append(row)
    return out


def ruling_A(win_rows):
    per_var = [sum(1 for ci in range(9) if win_rows[ci][vi])
               for vi in range(NV)]
    best = max(per_var)
    if best < REJECT_BAR:
        return "reject", per_var
    if best >= APPROVE_BAR:
        return "approve", per_var
    return "null", per_var


def wins_B(mis_table, n_scored):
    """Evaluator B: fractions.Fraction end to end (independent twin)."""
    line = Fraction(1, 10)
    out = []
    for ci, (sd, sz) in enumerate(CELLS):
        pi_d = Fraction(sd, sd + sz)
        min_pi = min(pi_d, 1 - pi_d)
        row = [min_pi - Fraction(mis_table[ci][vi], n_scored) >= line
               for vi in range(NV)]
        out.append(row)
    return out


def ruling_B(win_rows):
    counts = []
    for vi in range(NV):
        c = 0
        for ci in range(9):
            if win_rows[ci][vi]:
                c += 1
        counts.append(c)
    top = max(counts)
    if top < REJECT_BAR:
        return "reject", counts
    if top >= APPROVE_BAR:
        return "approve", counts
    return "null", counts


def sentinel_check(rng, seed, total_draws, leg_name):
    live_next = rng.random()
    fresh = random.Random(seed)
    fr = fresh.random
    for _ in range(total_draws):
        fr()
    check(fr() == live_next,
          "%s draw-count sentinel (%d draws)" % (leg_name, total_draws))


# ----------------------------------------------------- occupancy leg (G6)
def gen_panel_occ(rng, nblock):
    """V024 gen_panel, IID branch, rho=0.3, drift on the first nblock bars
    only. Pinned draw order: f_t (t asc), then z_{j,t} (j outer, t inner)."""
    rr = rng.random
    asd = SIGMA_D * math.sqrt(RHO_PANEL)
    bsd = SIGMA_D * math.sqrt(1.0 - RHO_PANEL)
    c = [(MU_D_PANEL if t < nblock else 0.0) + asd * ICDF(rr())
         for t in range(T)]
    prefs = []
    for _ in range(J_PANEL):
        s = 0.0
        row = [0.0] * (T + 1)
        for t in range(T):
            s += c[t] + bsd * ICDF(rr())
            row[t + 1] = s
        prefs.append(row)
    return prefs


def eval_g6(prefs):
    """V024's eval_panel arithmetic trimmed to the 6 G6 configs (momentum,
    equal-weight, k in {2,3}, L in {63,126,252}); returns Delta_max(G6)
    post-cost at 10 bp."""
    rj = range(J_PANEL)
    R = [[prefs[j][PB * (p + 1)] - prefs[j][PB * p] for j in rj]
         for p in range(NP)]
    n = float(NEVAL)
    Spre = [0.0] * 6
    Spre2 = [0.0] * 6
    Su = [0.0] * 6
    Su2 = [0.0] * 6
    Spu = [0.0] * 6
    Sb = 0.0
    Sb2 = 0.0
    prev = [None] * 6
    for p in range(EVAL_P0, NP):
        Rp = R[p]
        bas = sum(Rp) / J_PANEL
        Sb += bas
        Sb2 += bas * bas
        t = PB * p
        for Li, L in enumerate((63, 126, 252)):
            tl = t - L
            desc = sorted((-(prefs[j][t] - prefs[j][tl]), j) for j in rj)
            j0 = desc[0][1]
            j1 = desc[1][1]
            j2 = desc[2][1]
            r0 = Rp[j0]
            c2 = r0 + Rp[j1]
            c3 = c2 + Rp[j2]
            # k = 2
            i = Li * 2
            pv = prev[i]
            if pv is None:
                u = 0.0
                prev[i] = {j0, j1}
            else:
                repl = 2 - ((j0 in pv) + (j1 in pv))
                u = float(repl)
                if repl:
                    prev[i] = {j0, j1}
            xv = c2 * 0.5
            Spre[i] += xv
            Spre2[i] += xv * xv
            Su[i] += u
            Su2[i] += u * u
            Spu[i] += xv * u
            # k = 3
            i += 1
            pv = prev[i]
            if pv is None:
                u = 0.0
                prev[i] = {j0, j1, j2}
            else:
                repl = 3 - ((j0 in pv) + (j1 in pv) + (j2 in pv))
                u = repl * (2.0 / 3.0)
                if repl:
                    prev[i] = {j0, j1, j2}
            xv = c3 / 3.0
            Spre[i] += xv
            Spre2[i] += xv * xv
            Su[i] += u
            Su2[i] += u * u
            Spu[i] += xv * u
    mb = Sb / n
    vb = (Sb2 - n * mb * mb) / (n - 1.0)
    shb = mb / math.sqrt(vb) * SQRT12
    dmax = None
    for i in range(6):
        sx = Spre[i] - COST * Su[i]
        sx2 = Spre2[i] - 2.0 * COST * Spu[i] + COST * COST * Su2[i]
        mean = sx / n
        var = (sx2 - n * mean * mean) / (n - 1.0)
        d = mean / math.sqrt(var) * SQRT12 - shb
        if dmax is None or d > dmax:
            dmax = d
    return dmax


def twin_g6(prefs):
    """Independently written G6 evaluator (V024 twin_eval pattern): direct
    bar sums, statistics-module mean/stdev, explicit turnover sets."""
    import statistics as st
    r = [[prefs[j][t + 1] - prefs[j][t] for t in range(T)]
         for j in range(J_PANEL)]
    bas = []
    for p in range(EVAL_P0, NP):
        t = PB * p
        bas.append(sum(sum(r[j][t:t + PB]) for j in range(J_PANEL)) / J_PANEL)
    shb = st.mean(bas) / st.stdev(bas) * math.sqrt(12)
    dmax = None
    for (L, k) in G6:
        held = None
        rets = []
        for p in range(EVAL_P0, NP):
            t = PB * p
            scores = [(sum(r[j][t - L:t]), j) for j in range(J_PANEL)]
            order = sorted(scores, key=lambda s_: (-s_[0], s_[1]))
            sel = [j for _, j in order[:k]]
            xv = 0.0
            for j in sel:
                xv += sum(r[j][t:t + PB])
            xv /= k
            ns = set(sel)
            if held is not None:
                xv -= COST * 2.0 * len(ns - held) / k
            held = ns
            rets.append(xv)
        d = st.mean(rets) / st.stdev(rets) * math.sqrt(12) - shb
        if dmax is None or d > dmax:
            dmax = d
    return dmax


# ------------------------------------------------------------- fixtures
def fixture_crosscheck(oc):
    with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as f:
        fx = json.load(f)
    sm = fx["stream_model"]
    check(sm["delta"] == DELTA and DELTA == 0.07244319066010188,
          "fixtures delta == 1.15/sqrt(252) == 0.07244319066010188")
    check(sm["p_D"] == PD and PD == 0.528875393055249,
          "fixtures p_D == Phi(delta) == 0.528875393055249")
    check(sm["T"] == T and sm["scoring_start"] == SC0 and
          sm["scored_bars_per_path"] == NSC, "fixtures T/scoring frame")
    check(tuple(sm["S_grid"]) == S_GRID, "fixtures S grid")
    ls = fx["legs_and_seeds"]
    check(ls["main"]["seed"] == SEED_MAIN and ls["main"]["M_per_cell"] == M_MAIN
          and ls["stability"]["seed"] == SEED_STAB
          and ls["stability"]["M_per_cell"] == M_STAB
          and ls["reporting"]["seed"] == SEED_REPORT
          and ls["reporting"]["frozen_M_per_state"] == M_FROZEN
          and ls["reporting"]["occupancy_M_per_point"] == M_OCC
          and ls["aux"]["seed"] == SEED_AUX, "fixtures seeds/M")
    dr = fx["decision_rule"]
    check(dr["win_margin"] == WIN_MARGIN and dr["reject_bar_cells"] ==
          REJECT_BAR and dr["approve_bar_cells"] == APPROVE_BAR,
          "fixtures decision bands")
    va = fx["gates_run_invalid_on_any_failure"]["v024_anchors"]
    check(va["anchor_q99_phi0"] == ANCHOR_Q99_PHI0 and
          va["anchor_q99_phi1"] == ANCHOR_Q99_PHI1, "fixtures V024 anchors")
    # per-cell exact tables
    for i, cf in enumerate(sm["cells_lexicographic_S_D_then_S_Z"]):
        sd, sz = CELLS[i]
        piD, var_occ, exp_f, var_f = chain_moments(sd, sz)
        check(cf["S_D"] == sd and cf["S_Z"] == sz, "fixtures cell order %d" % i)
        check(cf["pi_D"] == float(piD), "fixtures pi_D cell %d" % i)
        check(cf["min_pi"] == float(min(piD, 1 - piD)),
              "fixtures min_pi cell %d" % i)
        check(abs(cf["var_occupancy_count_exact"] - var_occ) <=
              1e-9 * max(1.0, var_occ), "fixtures var_occ cell %d" % i)
        check(abs(cf["var_flip_count_each_dir_exact"] - var_f) <= 1e-9,
              "fixtures var_flip cell %d" % i)
        check(cf["expected_flips_each_direction"] == exp_f,
              "fixtures expected flips cell %d" % i)
    # pinned pure-window OCs
    for i, v in enumerate(fx["detectors"]["variants_pure_window_OC_pinned"]):
        stat, w, lam = VARIANTS[i]
        check(v["stat"] == stat and v["w"] == w and v["lam"] == lam,
              "fixtures variant order %d" % i)
        check(abs(v["TPR_inf"] - oc[i][0]) <= 1e-15 and
              abs(v["FPR_inf"] - oc[i][1]) <= 1e-15,
              "fixtures pure-window OC variant %d" % i)
        if stat == "UP":
            check(v["k_up"] == K_UP[(w, lam)], "fixtures k_up variant %d" % i)
    # frozen tolerances (recompute the pinned arithmetic)
    tols = fx["gates_run_invalid_on_any_failure"]["frozen_state"]["tolerances"]
    for i, (stat, w, lam) in enumerate(VARIANTS):
        for state, p in (("D", oc[i][0]), ("Z", oc[i][1])):
            key = "%s_w%d_lam%.1f_%s" % (stat, w, lam, state)
            want = 4.0 * math.sqrt(p * (1.0 - p) * (2 * w - 1) / NSC / M_FROZEN)
            check(abs(tols[key] - want) <= 1e-15,
                  "fixtures frozen tolerance %s" % key)
    # V024 mu_d / rho-invariance code-level identity
    for rho in (0.0, 0.3, 0.6):
        sig_b = SIGMA_D * math.sqrt(rho + (1.0 - rho) / 9.0)
        mu = 1.15 * sig_b / math.sqrt(252.0)
        check(abs(mu / sig_b - DELTA) <= 1e-15,
              "code-level identity: basket drift/vol == delta at rho=%.1f" % rho)
    # UP thresholds: w*u never integer at the registered grid
    for w in WS:
        for lam in LAMS:
            wu = U_UP[lam] * w
            check(wu != float(math.floor(wu)), "w*u non-integer w=%d" % w)
    return fx


def arm_a_gates(oc, fx):
    """Arm A exact identities (run invalid on failure)."""
    # SR swap: TPR(lam) == TNR(1-lam), FPR(lam) == FNR(1-lam)
    for w in WS:
        for lam in LAMS:
            i = VARIANTS.index(("SR", w, lam))
            j = VARIANTS.index(("SR", w, round(1.0 - lam, 1)))
            check(abs(oc[i][0] - (1.0 - oc[j][1])) <= 1e-12,
                  "Arm A SR swap TPR w=%d lam=%.1f" % (w, lam))
            check(abs(oc[i][1] - (1.0 - oc[j][0])) <= 1e-12,
                  "Arm A SR swap FPR w=%d lam=%.1f" % (w, lam))
    # UP mirror identity via two independently written binomial routines
    for w in WS:
        for lam in LAMS:
            k = K_UP[(w, lam)]
            check(abs(binom_tail_ge(w, PD, k) -
                      binom_cdf_le(w, 1.0 - PD, w - k)) <= 1e-12,
                  "Arm A UP mirror identity p_D w=%d lam=%.1f" % (w, lam))
            check(abs(binom_tail_ge(w, 0.5, k) -
                      binom_cdf_le(w, 0.5, w - k)) <= 1e-12,
                  "Arm A UP mirror identity 1/2 w=%d lam=%.1f" % (w, lam))
    # hand pin: BA ceiling at lam=0.5 equals Phi(0.575*sqrt(w/252))
    for w, want in ((63, 0.613135249031273), (126, 0.6578441059030129),
                    (252, 0.7173543515027994)):
        i = VARIANTS.index(("SR", w, 0.5))
        ba = 0.5 * (oc[i][0] + 1.0 - oc[i][1])
        check(abs(ba - want) <= 1e-15, "Arm A ceiling hand pin w=%d" % w)


# --------------------------------------------------------------- leg driver
def run_cells_leg(seed, M, leg_name, full=False):
    """Runs one 9-cell leg. Returns dict with per-cell aggregates and (full
    legs only) lag/realized-sd/swap data."""
    rng = random.Random(seed)
    total_draws = 0
    cells_out = []
    mis_table = []
    swap_data = []   # per cell: (nD_list, [ (cTP_list, cFP_list) per SR var ])
    for ci, (sd, sz) in enumerate(CELLS):
        agg_mis = [0] * NV
        agg_tp = [0] * NV
        agg_C = [0] * NV
        occ_sum = 0
        fdz_sum = 0
        fzd_sum = 0
        nD_list = []
        sr_lists = [([], []) for _ in SR_IDX] if full else None
        lag_store = [[([], 0), ([], 0)] for _ in range(NV)] if full else None
        real_agg = [[0, 0] for _ in range(9)] if full else None
        real_nD = 0
        for i in range(M):
            if i == 0:
                pre_state = rng.getstate()
            states, x, fdz, fzd, nd = gen_path(rng, sd, sz)
            total_draws += 2 * T
            nD, per_var, vals_by_w, counts_by_w, truth, real = \
                path_stats(states, x, want_real=full)
            if i == 0:
                post_state = rng.getstate()
                rng.setstate(pre_state)
                states_r, x_r, _, _, _ = gen_path(rng, sd, sz)
                _, per_var_r, _, _, _, _ = path_stats(states_r, x_r)
                check(per_var_r == per_var and x_r == x,
                      "%s cell %d determinism replay" % (leg_name, ci))
                rng.setstate(post_state)
            occ_sum += nd
            fdz_sum += fdz
            fzd_sum += fzd
            nZ = NSC - nD
            for vi in range(NV):
                C, cTP = per_var[vi]
                agg_C[vi] += C
                agg_tp[vi] += cTP
                agg_mis[vi] += (C - cTP) + (nD - cTP)
            if full:
                nD_list.append(nD)
                for si, vi in enumerate(SR_IDX):
                    C, cTP = per_var[vi]
                    sr_lists[si][0].append(cTP)
                    sr_lists[si][1].append(C - cTP)
                collect_lags(states, vals_by_w, counts_by_w, lag_store)
                for ri in range(9):
                    C, cTP = real[ri]
                    real_agg[ri][0] += C
                    real_agg[ri][1] += cTP
                real_nD += nD
        mis_table.append(agg_mis)
        piD, var_occ, exp_f, var_f = chain_moments(sd, sz)
        occ_share = occ_sum / (M * T)
        mean_fdz = fdz_sum / M
        mean_fzd = fzd_sum / M
        if full:
            occ_tol = 4.0 * math.sqrt(var_occ) / T / math.sqrt(M)
            flip_tol = 4.0 * math.sqrt(max(var_f, 0.0)) / math.sqrt(M)
            check(abs(occ_share - float(piD)) <= occ_tol,
                  "occupancy gate cell %d" % ci)
            check(abs(mean_fdz - exp_f) <= flip_tol,
                  "flip-count gate D->Z cell %d" % ci)
            check(abs(mean_fzd - exp_f) <= flip_tol,
                  "flip-count gate Z->D cell %d" % ci)
        scored_D = sum(nD_list) if full else None
        cells_out.append({
            "S_D": sd, "S_Z": sz, "M": M,
            "mean_occupancy_share": occ_share,
            "mean_flips_dz": mean_fdz, "mean_flips_zd": mean_fzd,
            "agg_mis": agg_mis, "agg_tp": agg_tp, "agg_C": agg_C,
            "scored_D_bars": scored_D,
        })
        if full:
            swap_data.append((nD_list, sr_lists))
            cells_out[-1]["lag_store"] = lag_store
            cells_out[-1]["real_agg"] = real_agg
        log("[%s] cell %d/9 S_D=%d S_Z=%d done (occ %.4f)"
            % (leg_name, ci + 1, sd, sz, occ_share))
    return {"cells": cells_out, "mis_table": mis_table,
            "swap_data": swap_data, "rng": rng, "draws": total_draws}


def swap_gate(main):
    """Arm S statistical swap gate, SR family (z=4.5, cluster-robust SE)."""
    n_points = 0
    max_z = 0.0
    for ci, (a, b) in enumerate(CELLS):
        cj = CELLS.index((b, a))
        for si, vi in enumerate(SR_IDX):
            stat, w, lam = VARIANTS[vi]
            lam2 = round(1.0 - lam, 1)
            vj = VARIANTS.index(("SR", w, lam2))
            sj = SR_IDX.index(vj)
            if (cj, sj) < (ci, si):
                continue    # each unordered pair once
            nD_i, sr_i = main["swap_data"][ci]
            nD_j, sr_j = main["swap_data"][cj]
            M = len(nD_i)
            # identity 1: TPR(ci, lam) == TNR(cj, 1-lam)
            # identity 2: FPR(ci, lam) == FNR(cj, 1-lam)
            for which in (0, 1):
                if which == 0:
                    c1 = sr_i[si][0]
                    n1 = nD_i
                    c2 = [(NSC - nd) - fp for fp, nd in
                          zip(sr_j[sj][1], nD_j)]      # TN = nZ - FP
                    n2 = [NSC - nd for nd in nD_j]
                else:
                    c1 = sr_i[si][1]
                    n1 = [NSC - nd for nd in nD_i]
                    c2 = [nd - tp for tp, nd in zip(sr_j[sj][0], nD_j)]  # FN
                    n2 = nD_j
                N1 = sum(n1)
                N2 = sum(n2)
                p1 = sum(c1) / N1
                p2 = sum(c2) / N2
                if ci == cj:
                    var = sum((( (c1[i] - p1 * n1[i]) / N1 )
                               - ( (c2[i] - p2 * n2[i]) / N2 )) ** 2
                              for i in range(M))
                else:
                    var = sum(((c1[i] - p1 * n1[i]) / N1) ** 2
                              for i in range(M)) + \
                          sum(((c2[i] - p2 * n2[i]) / N2) ** 2
                              for i in range(M))
                se = math.sqrt(var)
                diff = abs(p1 - p2)
                check(diff <= 4.5 * se or diff <= 1e-12,
                      "Arm S SR swap gate cell %d var %d id %d "
                      "(diff %.5f se %.5f)" % (ci, vi, which, diff, se))
                if se > 0:
                    max_z = max(max_z, diff / se)
                n_points += 1
    return n_points, max_z


# ------------------------------------------------------------------ main
def main():
    check(sys.version_info[:2] == (3, 11),
          "CPython minor pinned: need 3.11, got %d.%d" % sys.version_info[:2])
    oc = arm_a_oc()
    fx = fixture_crosscheck(oc)
    arm_a_gates(oc, fx)
    log("[arm A] exact OCs, identities, fixture crosscheck done")

    results = {"python": "cpython-%d.%d" % sys.version_info[:2],
               "seeds": {"main": SEED_MAIN, "stability": SEED_STAB,
                         "reporting": SEED_REPORT, "aux": SEED_AUX},
               "variants": ["%s w=%d lam=%.1f" % v for v in VARIANTS]}
    results["arm_A"] = {
        "pure_window_OC": [
            {"variant": "%s w=%d lam=%.1f" % VARIANTS[i],
             "TPR_inf": oc[i][0], "FPR_inf": oc[i][1],
             "BA_inf": 0.5 * (oc[i][0] + 1.0 - oc[i][1]),
             "E_inf_balanced": 0.5 * ((1.0 - oc[i][0]) + oc[i][1])}
            for i in range(NV)],
        "cells": [
            {"S_D": sd, "S_Z": sz,
             "pi_D": float(Fraction(sd, sd + sz)),
             "min_pi": float(min(Fraction(sd, sd + sz),
                                 1 - Fraction(sd, sd + sz))),
             "expected_flips_each_direction": (T - 1) / (sd + sz),
             "pure_window_E": [
                 float(Fraction(sd, sd + sz)) * (1.0 - oc[i][0]) +
                 (1.0 - float(Fraction(sd, sd + sz))) * oc[i][1]
                 for i in range(NV)]}
            for (sd, sz) in CELLS]}

    # ---------------- MAIN leg
    log("[main] starting M=%d x 9 cells, seed %d" % (M_MAIN, SEED_MAIN))
    main_leg = run_cells_leg(SEED_MAIN, M_MAIN, "main", full=True)
    check(main_leg["draws"] == M_MAIN * 9 * 2 * T, "main analytic draw count")
    sentinel_check(main_leg["rng"], SEED_MAIN, main_leg["draws"], "main")
    n_scored = M_MAIN * NSC
    winsA = wins_A(main_leg["mis_table"], n_scored)
    rulA, cntA = ruling_A(winsA)
    winsB = wins_B(main_leg["mis_table"], n_scored)
    rulB, cntB = ruling_B(winsB)
    check(winsA == winsB, "twin decision evaluators: win flags (main)")
    check(cntA == cntB, "twin decision evaluators: per-variant counts (main)")
    check(rulA == rulB, "twin decision evaluators: ruling (main)")
    n_swap, max_z_swap = swap_gate(main_leg)
    log("[main] swap gate: %d points, max |z| %.3f" % (n_swap, max_z_swap))

    # ---------------- STABILITY leg
    log("[stability] starting M=%d x 9 cells, seed %d" % (M_STAB, SEED_STAB))
    stab_leg = run_cells_leg(SEED_STAB, M_STAB, "stability", full=False)
    check(stab_leg["draws"] == M_STAB * 9 * 2 * T,
          "stability analytic draw count")
    sentinel_check(stab_leg["rng"], SEED_STAB, stab_leg["draws"], "stability")
    n_scored_s = M_STAB * NSC
    swinsA = wins_A(stab_leg["mis_table"], n_scored_s)
    srulA, scntA = ruling_A(swinsA)
    swinsB = wins_B(stab_leg["mis_table"], n_scored_s)
    srulB, scntB = ruling_B(swinsB)
    check(swinsA == swinsB and scntA == scntB and srulA == srulB,
          "twin decision evaluators (stability)")
    check(srulA == rulA,
          "VALIDITY GATE: stability leg (seed %d) reproduces the ruling"
          % SEED_STAB)

    # ---------------- FROZEN-STATE legs (seed 20260774, one stream)
    log("[frozen] starting D then Z, M=%d each, seed %d"
        % (M_FROZEN, SEED_REPORT))
    rng_f = random.Random(SEED_REPORT)
    frozen_rates = {}
    draws_f = 0
    tols = fx["gates_run_invalid_on_any_failure"]["frozen_state"]["tolerances"]
    for state_name, mu, is_d in (("D", DELTA, True), ("Z", 0.0, False)):
        agg_C = [0] * NV
        states = bytearray([1 if is_d else 0]) * T
        for i in range(M_FROZEN):
            x = [mu + ICDF(rng_f.random()) for _ in range(T)]
            draws_f += T
            _, per_var, _, _, _, _ = path_stats(states, x)
            for vi in range(NV):
                agg_C[vi] += per_var[vi][0]
        rates = [agg_C[vi] / (M_FROZEN * NSC) for vi in range(NV)]
        frozen_rates[state_name] = rates
        for vi, (stat, w, lam) in enumerate(VARIANTS):
            key = "%s_w%d_lam%.1f_%s" % (stat, w, lam, state_name)
            exact = oc[vi][0] if is_d else oc[vi][1]
            check(abs(rates[vi] - exact) <= tols[key],
                  "frozen-%s gate %s (got %.5f exact %.5f tol %.5f)"
                  % (state_name, key, rates[vi], exact, tols[key]))
        log("[frozen] state %s done" % state_name)
    check(draws_f == 2 * M_FROZEN * T, "frozen analytic draw count")
    sentinel_check(rng_f, SEED_REPORT, draws_f, "frozen")

    # ---------------- RHO-INVARIANCE leg (aux seed, cell (252,252))
    log("[rho-invariance] M=%d, seed %d" % (M_RHO, SEED_AUX))
    rng_r = random.Random(SEED_AUX)
    sig0 = 0.30 * math.sqrt(0.0 + 1.0 / 9.0) / math.sqrt(252.0)
    sig6 = 0.30 * math.sqrt(0.6 + 0.4 / 9.0) / math.sqrt(252.0)
    draws_r = 0
    for i in range(M_RHO):
        states, x, _, _, _ = gen_path(rng_r, 252, 252)
        draws_r += 2 * T
        base_bits = classification_bits(x)
        for sig in (sig0, sig6):
            y = [(sig * v) / sig for v in x]
            check(classification_bits(y) == base_bits,
                  "rho-invariance byte-identity path %d sigma %.6f" % (i, sig))
    check(draws_r == M_RHO * 2 * T, "rho-invariance analytic draw count")
    sentinel_check(rng_r, SEED_AUX, draws_r, "rho-invariance")

    # ---------------- OCCUPANCY-GRADED BAR leg (seed 20260774, fresh)
    log("[occupancy] starting 5 phi x M=%d, seed %d" % (M_OCC, SEED_REPORT))
    rng_o = random.Random(SEED_REPORT)
    occ_out = []
    draws_o = 0
    for phi in PHI_GRID:
        nblock = math.ceil(phi * T)
        dmaxes = []
        for i in range(M_OCC):
            prefs = gen_panel_occ(rng_o, nblock)
            draws_o += (J_PANEL + 1) * T
            d = eval_g6(prefs)
            if i == 0:
                tw = twin_g6(prefs)
                check(abs(tw - d) <= 1e-9,
                      "occupancy twin G6 evaluator phi=%.2f" % phi)
            dmaxes.append(d)
        srt = sorted(dmaxes)
        occ_out.append({
            "phi": phi, "n_block_bars": nblock, "M": M_OCC,
            "q50": quant(srt, 0.50), "q90": quant(srt, 0.90),
            "q99": quant(srt, 0.99),
            "n_exc_anchor_phi0": sum(1 for v in dmaxes
                                     if v > ANCHOR_Q99_PHI0),
            "n_exc_anchor_phi1": sum(1 for v in dmaxes
                                     if v > ANCHOR_Q99_PHI1)})
        log("[occupancy] phi=%.2f q99=%.4f" % (phi, occ_out[-1]["q99"]))
    check(draws_o == 5 * M_OCC * (J_PANEL + 1) * T,
          "occupancy analytic draw count")
    sentinel_check(rng_o, SEED_REPORT, draws_o, "occupancy")
    # chained anchors (tail-count gates, band pre-pinned in the fixture)
    n1 = occ_out[-1]["n_exc_anchor_phi1"]
    n0 = occ_out[0]["n_exc_anchor_phi0"]
    check(occ_out[-1]["phi"] == 1.0 and occ_out[0]["phi"] == 0.0,
          "occupancy leg phi endpoints present")
    check(n1 <= ANCHOR_COUNT_MAX,
          "V024 anchor gate phi=1 (N_exc=%d vs max %d)" % (n1, ANCHOR_COUNT_MAX))
    check(n0 <= ANCHOR_COUNT_MAX,
          "V024 anchor gate phi=0 (N_exc=%d vs max %d)" % (n0, ANCHOR_COUNT_MAX))

    # ---------------- assemble results
    key_cells = []
    for ci, (sd, sz) in enumerate(CELLS):
        cell = main_leg["cells"][ci]
        piD = Fraction(sd, sd + sz)
        min_pi = float(min(piD, 1 - piD))
        pi_z = 1.0 - float(piD)
        per_var = []
        scored_D = cell["scored_D_bars"]
        scored_Z = M_MAIN * NSC - scored_D
        for vi in range(NV):
            mis = cell["agg_mis"][vi]
            E = mis / n_scored
            tpr = cell["agg_tp"][vi] / scored_D
            fpr = (cell["agg_C"][vi] - cell["agg_tp"][vi]) / scored_Z
            lag = cell["lag_store"][vi]
            lag_out = {}
            for d, name in ((1, "Z_to_D"), (0, "D_to_Z")):
                lags, cens = lag[d]
                m, p90 = med_p90(lags)
                lag_out[name] = {"n": len(lags), "censored": cens,
                                 "median": m, "p90": p90,
                                 "censor_frac": cens / (len(lags) + cens)
                                 if (len(lags) + cens) > 0 else None}
            per_var.append({
                "variant": "%s w=%d lam=%.1f" % VARIANTS[vi],
                "mis": mis, "E": E,
                "TPR": tpr, "TNR": 1.0 - fpr,
                "BA": 0.5 * (tpr + 1.0 - fpr),
                "dE_oracle": min_pi - E,
                "dE_always": pi_z - E,
                "win": bool(winsA[ci][vi]),
                "lag": lag_out})
        real_out = []
        for ri, (w, lam) in enumerate([(w, l) for w in WS for l in LAMS]):
            C, cTP = cell["real_agg"][ri]
            tpr = cTP / scored_D
            fpr = (C - cTP) / scored_Z
            ba_real = 0.5 * (tpr + 1.0 - fpr)
            vi = VARIANTS.index(("SR", w, lam))
            ba_pin = per_var[vi]["BA"]
            real_out.append({"variant": "SRreal w=%d lam=%.1f" % (w, lam),
                             "BA": ba_real, "dBA_vs_pinned": ba_real - ba_pin,
                             "E": ((C - cTP) + (scored_D - cTP)) / n_scored})
        key_cells.append({
            "S_D": sd, "S_Z": sz, "pi_D": float(piD), "min_pi": min_pi,
            "mean_occupancy_share": cell["mean_occupancy_share"],
            "mean_flips_dz": cell["mean_flips_dz"],
            "mean_flips_zd": cell["mean_flips_zd"],
            "detectors": per_var,
            "realized_sd_reporting": real_out})

    # per-axis pass shares (pooled over variants; and for the best variant)
    best_vi = cntA.index(max(cntA))
    minpi_of = {ci: float(min(Fraction(a, a + b), 1 - Fraction(a, a + b)))
                for ci, (a, b) in enumerate(CELLS)}
    minsoj_of = {ci: min(a, b) for ci, (a, b) in enumerate(CELLS)}
    axes = {}
    for axis, mapping in (("min_pi", minpi_of), ("min_sojourn", minsoj_of)):
        vals = {}
        for kv in sorted(set(mapping.values())):
            idxs = [ci for ci in sorted(mapping) if mapping[ci] == kv]
            pooled = sum(1 for ci in idxs for vi in range(NV)
                         if winsA[ci][vi]) / (len(idxs) * NV)
            bestv = sum(1 for ci in idxs if winsA[ci][best_vi]) / len(idxs)
            vals["%g" % kv] = {"pass_share_all_variants": pooled,
                               "pass_share_best_variant": bestv,
                               "n_cells": len(idxs)}
        shares = [vals[k]["pass_share_all_variants"] for k in vals]
        axes[axis] = {"values": vals, "spread": max(shares) - min(shares)}

    results["main_leg"] = {"M": M_MAIN, "cells": key_cells}
    results["decision"] = {
        "rule": "REJECT iff NO variant wins (dE_oracle >= +0.10) in >= 3/9 "
                "cells (checked FIRST); APPROVE iff one variant wins >= 7/9, "
                "stability-reproduced; else NULL",
        "per_variant_cells_won": {
            "%s w=%d lam=%.1f" % VARIANTS[vi]: cntA[vi] for vi in range(NV)},
        "max_cells_won": max(cntA),
        "best_variant": "%s w=%d lam=%.1f" % VARIANTS[best_vi],
        "ruling": rulA,
        "axes_pass_shares": axes}
    results["stability_leg"] = {
        "M": M_STAB, "ruling": srulA,
        "per_variant_cells_won": {
            "%s w=%d lam=%.1f" % VARIANTS[vi]: scntA[vi]
            for vi in range(NV)},
        "reproduces_main": srulA == rulA}
    results["frozen_leg"] = {
        "M_per_state": M_FROZEN,
        "measured_TPR": frozen_rates["D"], "measured_FPR": frozen_rates["Z"],
        "exact_TPR": [oc[i][0] for i in range(NV)],
        "exact_FPR": [oc[i][1] for i in range(NV)],
        "gate_points": 36}
    results["swap_gate"] = {"points": n_swap, "max_abs_z": max_z_swap,
                            "z_tolerance": 4.5, "scope": "SR family (Arm S); "
                            "UP via exact Arm-A mirror identity (fixture D5)"}
    results["rho_invariance_leg"] = {"M": M_RHO, "cell": [252, 252],
                                     "pass": True,
                                     "sigma_daily": [sig0, sig6]}
    results["occupancy_bar_leg"] = {
        "spec": "V024 G6 machinery @ IID/rho=0.3, M=400/point, seed 20260774",
        "anchors": {"phi0_q99_committed": ANCHOR_Q99_PHI0,
                    "phi1_q99_committed": ANCHOR_Q99_PHI1,
                    "pin": "sims/verdict-024-keep-margins-noise/results.json "
                           "@ cd47c06", "tail_count_max": ANCHOR_COUNT_MAX,
                    "N_exc_phi1": n1, "N_exc_phi0": n0},
        "points": occ_out,
        "monotone_decreasing_q99": all(
            occ_out[i]["q99"] > occ_out[i + 1]["q99"]
            for i in range(len(occ_out) - 1))}
    results["draws"] = {"main": main_leg["draws"],
                        "stability": stab_leg["draws"],
                        "frozen": draws_f, "occupancy": draws_o,
                        "rho_invariance": draws_r}

    # ---------------- stdout report (byte-identical across runs)
    print("== verdict-036 — drift-regime observability "
          "(idea-engine PROPOSAL 034) ==")
    print("python: cpython-%d.%d   seeds: main %d / stability %d / "
          "reporting %d / aux %d"
          % (sys.version_info[0], sys.version_info[1], SEED_MAIN, SEED_STAB,
             SEED_REPORT, SEED_AUX))
    print("")
    print("ARM A — exact pure-window ceilings (18 variants):")
    print("variant           TPR_inf  FPR_inf  BA_inf   E_inf")
    for i, v in enumerate(VARIANTS):
        print("%-17s %.6f %.6f %.6f %.6f"
              % ("%s w=%d lam=%.1f" % v, oc[i][0], oc[i][1],
                 0.5 * (oc[i][0] + 1.0 - oc[i][1]),
                 0.5 * ((1.0 - oc[i][0]) + oc[i][1])))
    print("")
    print("MAIN LEG (M=%d per cell, seed %d) — dE_oracle per (cell, variant); "
          "win iff >= +0.10" % (M_MAIN, SEED_MAIN))
    hdr = "cell (S_D,S_Z) pi_D  min_pi |"
    for v in VARIANTS:
        hdr += " %s%d.%d" % (v[0][0], v[1], int(v[2] * 10))
    print(hdr)
    for ci, (sd, sz) in enumerate(CELLS):
        piD = float(Fraction(sd, sd + sz))
        min_pi = float(min(Fraction(sd, sd + sz), 1 - Fraction(sd, sd + sz)))
        row = "%4d (%4d,%4d) %.3f %.3f |" % (ci, sd, sz, piD, min_pi)
        for vi in range(NV):
            de = min_pi - main_leg["cells"][ci]["agg_mis"][vi] / n_scored
            row += " %+.3f" % de
        print(row)
    print("")
    print("PER-VARIANT CELLS WON (of 9; REJECT bar < 3 for ALL, APPROVE bar "
          ">= 7 for ONE):")
    for vi in range(NV):
        print("  %-17s %d/9" % ("%s w=%d lam=%.1f" % VARIANTS[vi], cntA[vi]))
    print("")
    print("DECISION (pre-registered order REJECT -> APPROVE -> NULL):")
    print("  max cells won by any variant: %d/9 (best: %s)"
          % (max(cntA), "%s w=%d lam=%.1f" % VARIANTS[best_vi]))
    print("  RULING: %s" % rulA.upper())
    print("  per-axis pass shares (pooled over variants):")
    for ax in axes:
        parts = []
        for k, d in axes[ax]["values"].items():
            parts.append("%s: %.3f" % (k, d["pass_share_all_variants"]))
        print("    %-11s (spread %.3f): %s"
              % (ax, axes[ax]["spread"], " | ".join(parts)))
    print("")
    print("STABILITY LEG (M=%d, seed %d): ruling %s — reproduces main: %s"
          % (M_STAB, SEED_STAB, srulA, srulA == rulA))
    print("  per-variant cells won: %s" % scntA)
    print("")
    print("FROZEN-STATE GATES: 36/36 within familywise tolerances "
          "(max |dev|/tol shown per family):")
    md = mz = 0.0
    for vi, (stat, w, lam) in enumerate(VARIANTS):
        kd = "%s_w%d_lam%.1f_D" % (stat, w, lam)
        kz = "%s_w%d_lam%.1f_Z" % (stat, w, lam)
        md = max(md, abs(frozen_rates["D"][vi] - oc[vi][0]) / tols[kd])
        mz = max(mz, abs(frozen_rates["Z"][vi] - oc[vi][1]) / tols[kz])
    print("  frozen-D max |dev|/tol = %.3f   frozen-Z max |dev|/tol = %.3f"
          % (md, mz))
    print("SWAP GATE (Arm S, SR family): %d points, max |z| = %.3f (tol 4.5)"
          % (n_swap, max_z_swap))
    print("RHO-INVARIANCE: %d paths x 2 scales, classifications "
          "byte-identical: PASS" % M_RHO)
    print("")
    print("OCCUPANCY-GRADED BAR LEG (V024 G6 @ IID/rho=0.3, M=%d/point, "
          "seed %d; reporting-only):" % (M_OCC, SEED_REPORT))
    print("  phi   q50      q90      q99      N>anchor0  N>anchor1")
    for o in occ_out:
        print("  %.2f  %+.4f  %+.4f  %+.4f  %9d  %9d"
              % (o["phi"], o["q50"], o["q90"], o["q99"],
                 o["n_exc_anchor_phi0"], o["n_exc_anchor_phi1"]))
    print("  chained anchors: N_exc(phi=1 vs 0.366902) = %d <= 12 PASS; "
          "N_exc(phi=0 vs 0.604101) = %d <= 12 PASS" % (n1, n0))
    print("  q99 monotone decreasing in phi: %s"
          % results["occupancy_bar_leg"]["monotone_decreasing_q99"])
    print("")
    results["self_checks"] = N_CHECKS + 1
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, sort_keys=True)
        f.write("\n")
    check(True, "results.json written")
    print("SELF-CHECKS: %d passed, 0 failed" % N_CHECKS)


def classification_bits(x):
    """All-18-variant classification bit-string over the scored bars —
    the rho-invariance byte-identity object."""
    P = [0.0] * (T + 1)
    s = 0.0
    for t in range(T):
        s += x[t]
        P[t + 1] = s
    U = [0] * (T + 1)
    c = 0
    for t in range(T):
        if x[t] > 0.0:
            c += 1
        U[t + 1] = c
    bits = []
    for w in WS:
        sc = SQ252 / w
        vals = [(a - b) * sc
                for a, b in zip(P[SC0 + 1:], P[SC0 + 1 - w:T + 1 - w])]
        counts = [a - b
                  for a, b in zip(U[SC0 + 1:], U[SC0 + 1 - w:T + 1 - w])]
        for lam in LAMS:
            h = H_SR[lam]
            bits.append(bytes(1 if v >= h else 0 for v in vals))
            k = K_UP[(w, lam)]
            bits.append(bytes(1 if v >= k else 0 for v in counts))
    return b"".join(bits)


if __name__ == "__main__":
    main()
