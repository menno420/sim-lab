#!/usr/bin/env python3
"""verdict-020 — book breadth vs versioning depth: fixed-budget allocation sweep.

Answers idea-engine PROPOSAL 018 (control/outbox.md 2026-07-13T01:15:34Z, idea
ideas/venture-lab/book-versioning-breadth-depth-allocation-2026-07-13.md @ cb2b6ee,
landed via idea-engine PR #283).

Fully hermetic (the PROPOSAL 017 precedent): every constant is a pinned fixture in
grid.json, copied verbatim from the idea file. stdlib only. No network, no git, no
wall clock, no hash(), no unseeded RNG. stdout and results.json are byte-identical
across process runs (external diff).

MODEL (pinned): a production night is budget B=12 (size leg B=6, hit legs only —
the fractional-T_eff headline is B-invariant by linearity). New title costs 1;
each extra version costs c in {0.25,0.5,0.75}. Policy K in {1,2,3,4,6};
T_eff = B/(1+c*(K-1)). Title appeal theta~N(0,1); version i quality
q_i = theta+eps_i, eps_i~N(0,sigma_v^2), sigma_v in {0.2,0.5,1.0}. A published
book with quality q earns exp(q+L), L~N(-sigma_m^2/2, sigma_m^2) (E[exp(L)]=1),
sigma_m in {0.5,1.5,2.5}. Mode P (pick-best): publish 1 of K, true-best picked
with prob f in {0.2,0.6,1.0} else uniform. Mode A (publish-all): all K listed,
R = (1-s)*max_i r_i + s*sum_i r_i, r_i = exp(theta+eps_i+L_i), s in {0,0.5,1}.

HEADLINE per cell: K* = argmax_K E[revenue per unit budget]
= E[R_title(K)]/(1+c*(K-1)), and dR = value(K*)/value(K=1) - 1.

ARMS (pre-registered):
  Arm A — analytic, seedless: Mode P f=1 slice, E[R_title(K)] = e^{1/2} *
    I(K, sigma_v), I(K,sigma) = Simpson quadrature of
    exp(sigma*x)*K*phi(x)*Phi(x)^(K-1) over [-10,10] step 0.001 (math.erf).
  Arm S — seeded MC: M=20,000 titles per (mode, cell, K);
    random.Random(20260716) Mode P / random.Random(20260717) Mode A; cells
    lexicographic ((c, sigma_v, sigma_m, f|s), axes ascending), K ascending,
    titles sequential. Per-title draw order (pinned here, per the proposal):
      Mode P: theta; eps_1..eps_K; u_pick = rng.random();
              j_uniform = rng.randrange(K) (always drawn); L.
      Mode A: theta; eps_1..eps_K; L_1..L_K.
    All normals via rng.normalvariate (CPython 3.11 stream semantics pinned).
  Stability leg — M=2,000, ONE random.Random(20260718): full Mode P grid, then
    full Mode A grid; must reproduce the same APPROVE/REJECT/NULL ruling.
  Gate — Arm S must agree with Arm A within 1.5% on every f=1 cell (checked per
    (cell, K)) or the run is invalid.

ESTIMATORS (disclosed; the spec pins model/grids/seeds/M/draw order, not the
estimator formula — the raw exp(q+L) sample mean has relative SE ~26% at
sigma_m=2.5 and could never satisfy the pre-registered 1.5% gate at M=20,000):
unbiased conditional-expectation / control-variate estimators over exactly the
pinned draws:
  Mode P: Xhat = e^{1/2} * (f*A(eps) + (1-f)*e^{sigma_v^2/2}), where A(eps) is
    the sign-flip-antithetic loser-sum control-variate estimator of
    E[exp(max_i eps_i)]:
      A(eps) = 1/2 * [ (K*e^{sigma_v^2/2} - (sum_i exp(eps_i) - max_i exp(eps_i)))
                     + (K*e^{sigma_v^2/2} - (sum_i exp(-eps_i) - max_i exp(-eps_i))) ]
    (theta, L, the pick draw, and the uniform-pick branch integrated out
    analytically; the CV uses the exact identity E[sum exp(eps)] =
    K*e^{sigma_v^2/2}; the sign flip is valid by N(0,sigma_v) symmetry;
    zero-variance at K=1).
  Mode A: Xhat = e^{1/2} * (K*e^{sigma_v^2/2} - (1-s)*sum_{i != argmax g} g_i),
    g_i = exp(eps_i+L_i) (theta integrated out; beta=1 control variate on the
    exact identity E[sum g] = K*e^{sigma_v^2/2}; zero-variance at K=1).
Raw revenues (with theta and L exactly as drawn) feed the distributional
hit-probability legs unchanged.

ANALYTIC DIAGNOSTIC LAYER (self-checks only; arms and ruling unchanged): the
pinned model's full mean structure is closed form via the same quadrature —
  Mode P: E[R_title] = e^{1/2} * (f*I(K,sigma_v) + (1-f)*e^{sigma_v^2/2})
    (sigma_m provably inert in Mode P means: E[exp(L)]=1, L independent of pick).
  Mode A: E[R_title] = e^{1/2} * ((1-s)*e^{-sigma_m^2/2}*I(K,sigma_c)
    + s*K*e^{sigma_v^2/2}), sigma_c = sqrt(sigma_v^2+sigma_m^2)
    (eps_i+L_i are iid N(-sigma_m^2/2, sigma_c^2); max is monotone under exp).

DECISION RULE (pre-registered, applied mechanically to the Arm S grids):
  APPROVE iff BOTH modes: K*>=2 share >= 0.80 AND median dR >= +0.10.
  REJECT  iff BOTH modes: K*=1 share >= 0.80.
  NULL    otherwise — name the flip axis per mode via per-value K*>=2
          cell-shares (largest max-min spread; ties broken by axis order).

Run: python3 sims/verdict-020-book-versioning/book_versioning_sim.py
Exit 0 iff all self-checks pass AND the pre-registered validity gates hold.
"""

import json
import math
import os
import random
import sys

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
with open(os.path.join(HERE, "grid.json"), "r", encoding="utf-8") as fh:
    GRID = json.load(fh)

FX = GRID["fixtures"]
B_HEAD = FX["B_headline"]
B_SIZE = FX["B_size_leg"]
C_GRID = FX["c_grid"]
K_GRID = FX["K_grid"]
SV_GRID = FX["sigma_v_grid"]
SM_GRID = FX["sigma_m_grid"]
F_GRID = FX["f_grid"]
S_GRID = FX["s_grid"]
M_MAIN = FX["M_main"]
M_STAB = FX["M_stability"]
SEED_P = FX["seed_mode_P"]
SEED_A = FX["seed_mode_A"]
SEED_STAB = FX["seed_stability"]
AGREE_TOL = FX["arm_agreement_rel_tol"]
Q_LO = FX["quadrature"]["lo"]
Q_HI = FX["quadrature"]["hi"]
Q_STEP = FX["quadrature"]["step"]

CELL_SHARE_T = GRID["bands"]["cell_share_threshold"]
MEDIAN_DR_T = GRID["bands"]["median_dR_threshold"]

# fixture pins copied verbatim from the idea file — belt-and-braces re-assert
check(B_HEAD == 12 and B_SIZE == 6, "fixture pin: B=12 headline, B=6 size leg")
check(C_GRID == [0.25, 0.5, 0.75], "fixture pin: c grid")
check(K_GRID == [1, 2, 3, 4, 6], "fixture pin: K grid")
check(SV_GRID == [0.2, 0.5, 1.0], "fixture pin: sigma_v grid")
check(SM_GRID == [0.5, 1.5, 2.5], "fixture pin: sigma_m grid")
check(F_GRID == [0.2, 0.6, 1.0], "fixture pin: f grid")
check(S_GRID == [0.0, 0.5, 1.0], "fixture pin: s grid")
check(M_MAIN == 20000 and M_STAB == 2000, "fixture pin: M values")
check((SEED_P, SEED_A, SEED_STAB) == (20260716, 20260717, 20260718),
      "fixture pin: seeds")
check(AGREE_TOL == 0.015, "fixture pin: 1.5% Arm A/S gate")
check((Q_LO, Q_HI, Q_STEP) == (-10.0, 10.0, 0.001), "fixture pin: quadrature")
check(sys.version_info[:2] == (3, 11),
      "CPython minor version pin: 3.11 (got %s.%s)" % sys.version_info[:2])

EHALF = math.exp(0.5)
SQRT2 = math.sqrt(2.0)
INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


# ------------------------------------------------------- Arm A: quadrature
def norm_phi(x):
    return INV_SQRT_2PI * math.exp(-0.5 * x * x)


def norm_Phi(x):
    return 0.5 * (1.0 + math.erf(x / SQRT2))


_I_CACHE = {}


def I_quad(K, sigma):
    """E[exp(sigma * M_K)], M_K = max of K iid std normals — composite Simpson
    of exp(sigma*x)*K*phi(x)*Phi(x)^(K-1) over [Q_LO, Q_HI] at step Q_STEP."""
    key = (K, sigma)
    if key in _I_CACHE:
        return _I_CACHE[key]
    n = int(round((Q_HI - Q_LO) / Q_STEP))  # 20000 intervals (even)
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


check(int(round((Q_HI - Q_LO) / Q_STEP)) % 2 == 0,
      "Simpson interval count is even")
check(abs(norm_Phi(0.0) - 0.5) < 1e-15, "Phi(0) = 0.5")
check(abs(norm_Phi(10.0) - 1.0) < 1e-12, "Phi(10) ~= 1")
check(abs(norm_phi(1.0) - norm_phi(-1.0)) < 1e-18, "phi symmetric")

# quadrature identity: I(1, sigma) == exp(sigma^2/2) exactly (to quadrature)
_SIGMA_COMBINED = sorted(set(
    round(math.sqrt(sv * sv + sm * sm), 15) for sv in SV_GRID for sm in SM_GRID))
for sg in list(SV_GRID) + _SIGMA_COMBINED:
    exact = math.exp(0.5 * sg * sg)
    got = I_quad(1, sg)
    check(abs(got / exact - 1.0) < 1e-9,
          "quadrature identity I(1,%.6g) vs exp(sigma^2/2)" % sg)
    prev = got
    for K in K_GRID[1:]:
        cur = I_quad(K, sg)
        check(cur > prev, "I(K,%.6g) strictly increasing at K=%d" % (sg, K))
        prev = cur


def analytic_mean_P(sv, f, K):
    """Exact E[R_title] for Mode P (sigma_m inert: E[exp(L)]=1)."""
    return EHALF * (f * I_quad(K, sv) + (1.0 - f) * math.exp(0.5 * sv * sv))


def analytic_mean_A(sv, sm, s, K):
    """Exact E[R_title] for Mode A."""
    sc = math.sqrt(sv * sv + sm * sm)
    return EHALF * ((1.0 - s) * math.exp(-0.5 * sm * sm) * I_quad(K, sc)
                    + s * K * math.exp(0.5 * sv * sv))


# ------------------------------------------------------------- Arm S machinery
class CountingRandom(random.Random):
    """random.Random with API-level draw counters (audit only — the stream is
    untouched)."""

    def __init__(self, seed):
        random.Random.__init__(self, seed)
        self.n_nv = 0
        self.n_u = 0
        self.n_ri = 0

    def normalvariate(self, mu, sigma):
        self.n_nv += 1
        return random.Random.normalvariate(self, mu, sigma)

    def random_u(self):
        self.n_u += 1
        return self.random()

    def randrange_i(self, k):
        self.n_ri += 1
        return self.randrange(k)

    def counts(self):
        return (self.n_nv, self.n_u, self.n_ri)


def cells_P():
    return [(c, sv, sm, f) for c in C_GRID for sv in SV_GRID
            for sm in SM_GRID for f in F_GRID]


def cells_A():
    return [(c, sv, sm, s) for c in C_GRID for sv in SV_GRID
            for sm in SM_GRID for s in S_GRID]


def run_leg_P(rng, M, sv, sm, f, K):
    """One Mode P (cell, K) leg. Returns (mean_est, se_rel, raw_revs)."""
    nv = rng.normalvariate
    mexp = math.exp
    mu_L = -0.5 * sm * sm
    est_sum = 0.0
    est_sumsq = 0.0
    revs = []
    one_minus_f = 1.0 - f
    ev = math.exp(0.5 * sv * sv)
    kev = K * ev
    for _ in range(M):
        theta = nv(0.0, 1.0)
        eps = [nv(0.0, sv) for _ in range(K)]
        u_pick = rng.random_u()
        j_uni = rng.randrange_i(K)
        L = nv(mu_L, sm)
        best_i = 0
        if K > 1:
            for i in range(1, K):
                if eps[i] > eps[best_i]:
                    best_i = i
        exps = [mexp(e) for e in eps]
        nexps = [mexp(-e) for e in eps]
        a_pos = kev - (sum(exps) - max(exps))
        a_neg = kev - (sum(nexps) - max(nexps))
        est = EHALF * (f * 0.5 * (a_pos + a_neg) + one_minus_f * ev)
        est_sum += est
        est_sumsq += est * est
        picked = best_i if u_pick < f else j_uni
        revs.append(mexp(theta + eps[picked] + L))
    mean = est_sum / M
    var = max(0.0, est_sumsq / M - mean * mean)
    se_rel = math.sqrt(var / M) / mean if mean > 0.0 else 0.0
    return mean, se_rel, revs


def run_leg_A(rng, M, sv, sm, s, K):
    """One Mode A (cell, K) leg. Returns (mean_est, se_rel, raw_revs)."""
    nv = rng.normalvariate
    mexp = math.exp
    mu_L = -0.5 * sm * sm
    kev = K * math.exp(0.5 * sv * sv)
    one_minus_s = 1.0 - s
    est_sum = 0.0
    est_sumsq = 0.0
    revs = []
    for _ in range(M):
        theta = nv(0.0, 1.0)
        eps = [nv(0.0, sv) for _ in range(K)]
        Ls = [nv(mu_L, sm) for _ in range(K)]
        g = [mexp(eps[i] + Ls[i]) for i in range(K)]
        sg = math.fsum(g)
        mg = max(g)
        est = EHALF * (kev - one_minus_s * (sg - mg))
        est_sum += est
        est_sumsq += est * est
        revs.append(mexp(theta) * (one_minus_s * mg + s * sg))
    mean = est_sum / M
    var = max(0.0, est_sumsq / M - mean * mean)
    se_rel = math.sqrt(var / M) / mean if mean > 0.0 else 0.0
    return mean, se_rel, revs


def p90_nearest_rank(sorted_vals):
    m = len(sorted_vals)
    return sorted_vals[int(math.ceil(0.9 * m)) - 1]


def hit_legs(c, K, p_single):
    out = {}
    for B in (B_SIZE, B_HEAD):
        T = int(math.floor(B / (1.0 + c * (K - 1))))
        out["B%d" % B] = 1.0 - (1.0 - p_single) ** T
    return out


def run_mode(mode, rng, M, with_hits):
    """Run the full 81-cell grid for one mode on stream rng.

    Returns list of per-cell dicts (pinned lexicographic order)."""
    cells = cells_P() if mode == "P" else cells_A()
    out = []
    for cell in cells:
        c, sv, sm, last = cell
        values = {}
        se_rels = {}
        p_singles = {}
        hits = {}
        p90_k1 = None
        for K in K_GRID:
            before = rng.counts()
            if mode == "P":
                mean, se_rel, revs = run_leg_P(rng, M, sv, sm, last, K)
                d_nv, d_u, d_ri = (M * (K + 2), M, M)
            else:
                mean, se_rel, revs = run_leg_A(rng, M, sv, sm, last, K)
                d_nv, d_u, d_ri = (M * (2 * K + 1), 0, 0)
            after = rng.counts()
            check((after[0] - before[0], after[1] - before[1],
                   after[2] - before[2]) == (d_nv, d_u, d_ri),
                  "draw-count audit mode %s cell %s K=%d" % (mode, cell, K))
            value = mean / (1.0 + c * (K - 1))
            values[K] = value
            se_rels[K] = se_rel
            if with_hits:
                if K == 1:
                    revs_sorted = sorted(revs)
                    p90_k1 = p90_nearest_rank(revs_sorted)
                n_beat = 0
                for r in revs:
                    if r > p90_k1:
                        n_beat += 1
                p_single = n_beat / M
                p_singles[K] = p_single
                hits[K] = hit_legs(c, K, p_single)
        kstar = K_GRID[0]
        vstar = values[K_GRID[0]]
        for K in K_GRID[1:]:
            if values[K] > vstar:  # strictly greater: smallest K wins ties
                kstar = K
                vstar = values[K]
        dR = vstar / values[1] - 1.0
        check(dR >= 0.0, "dR >= 0 mode %s cell %s" % (mode, cell))
        check(all(v > 0.0 for v in values.values()),
              "positive values mode %s cell %s" % (mode, cell))
        rec = {"c": c, "sigma_v": sv, "sigma_m": sm,
               ("f" if mode == "P" else "s"): last,
               "values": values, "se_rel": se_rels,
               "kstar": kstar, "dR": dR}
        if with_hits:
            check(abs(p_singles[1] - 0.1) < 1e-12,
                  "K=1 p_single == 0.1 exactly mode %s cell %s" % (mode, cell))
            check(all(0.0 <= h <= 1.0 for K in K_GRID
                      for h in hits[K].values()),
                  "hit probabilities in [0,1] mode %s cell %s" % (mode, cell))
            rec["p_single"] = p_singles
            rec["hits"] = hits
        out.append(rec)
    return out


def grid_stats(cells, mode):
    n = len(cells)
    check(n == 81, "mode %s grid has 81 cells" % mode)
    n_ge2 = sum(1 for r in cells if r["kstar"] >= 2)
    n_eq1 = sum(1 for r in cells if r["kstar"] == 1)
    check(n_ge2 + n_eq1 == n, "K* partition mode %s" % mode)
    drs = sorted(r["dR"] for r in cells)
    median_dr = drs[40]  # 81 odd — exact lower==upper median
    kstar_counts = {}
    for K in K_GRID:
        kstar_counts[str(K)] = sum(1 for r in cells if r["kstar"] == K)
    check(sum(kstar_counts.values()) == n, "K* counts sum mode %s" % mode)
    last_axis = "f" if mode == "P" else "s"
    axes = [("c", C_GRID), ("sigma_v", SV_GRID), ("sigma_m", SM_GRID),
            (last_axis, F_GRID if mode == "P" else S_GRID)]
    axis_shares = {}
    spreads = []
    for name, gridvals in axes:
        shares = {}
        for v in gridvals:
            sub = [r for r in cells if r[name] == v]
            check(len(sub) == 27, "axis slice %s=%s has 27 cells" % (name, v))
            shares["%g" % v] = sum(1 for r in sub if r["kstar"] >= 2) / 27.0
        axis_shares[name] = shares
        vals = list(shares.values())
        spreads.append((max(vals) - min(vals), name))
    best_spread = max(sp for sp, _ in spreads)
    # tie-aware: the pre-registered rule says "largest spread = the named
    # boundary" without a tie-break — exact ties are all named
    flip_axes = [nm for sp, nm in spreads if sp == best_spread]
    return {"n_cells": n, "share_kstar_ge2": n_ge2 / n,
            "share_kstar_eq1": n_eq1 / n, "median_dR": median_dr,
            "kstar_counts": kstar_counts, "axis_kstar_ge2_shares": axis_shares,
            "flip_axes": flip_axes, "flip_axis_spread": best_spread}


def apply_rule(stats_P, stats_A):
    approve = (stats_P["share_kstar_ge2"] >= CELL_SHARE_T
               and stats_P["median_dR"] >= MEDIAN_DR_T
               and stats_A["share_kstar_ge2"] >= CELL_SHARE_T
               and stats_A["median_dR"] >= MEDIAN_DR_T)
    reject = (stats_P["share_kstar_eq1"] >= CELL_SHARE_T
              and stats_A["share_kstar_eq1"] >= CELL_SHARE_T)
    check(not (approve and reject), "APPROVE and REJECT mutually exclusive")
    if approve:
        return "APPROVE"
    if reject:
        return "REJECT"
    return "NULL"


# ------------------------------------------------------------------ main run
def main():
    print("verdict-020 book-versioning sim — PROPOSAL 018 pre-registered run")
    print("CPython %d.%d (pinned minor 3.11)" % sys.version_info[:2])

    # ---- Arm A (analytic, seedless): Mode P f=1 slice
    arm_A = {}
    for c in C_GRID:
        for sv in SV_GRID:
            values = {K: analytic_mean_P(sv, 1.0, K) / (1.0 + c * (K - 1))
                      for K in K_GRID}
            kstar = K_GRID[0]
            for K in K_GRID[1:]:
                if values[K] > values[kstar]:
                    kstar = K
            arm_A[(c, sv)] = {"values": values, "kstar": kstar,
                              "dR": values[kstar] / values[1] - 1.0}

    # ---- Arm S main pass
    rng_P = CountingRandom(SEED_P)
    cells_main_P = run_mode("P", rng_P, M_MAIN, with_hits=True)
    rng_A = CountingRandom(SEED_A)
    cells_main_A = run_mode("A", rng_A, M_MAIN, with_hits=True)

    # in-process prefix replay: first 6 cells per mode, fresh streams, must be
    # bit-identical (the V017 committed-subset re-evaluation discipline)
    rng_P2 = CountingRandom(SEED_P)
    replay_P = run_mode_prefix("P", rng_P2, M_MAIN, 6)
    rng_A2 = CountingRandom(SEED_A)
    replay_A = run_mode_prefix("A", rng_A2, M_MAIN, 6)
    for i in range(6):
        for K in K_GRID:
            check(replay_P[i]["values"][K] == cells_main_P[i]["values"][K],
                  "prefix replay bit-identical mode P cell %d K %d" % (i, K))
            check(replay_A[i]["values"][K] == cells_main_A[i]["values"][K],
                  "prefix replay bit-identical mode A cell %d K %d" % (i, K))

    # ---- analytic diagnostic layer (estimator unbiasedness, both modes)
    max_dev_P = 0.0
    for r in cells_main_P:
        for K in K_GRID:
            a = analytic_mean_P(r["sigma_v"], r["f"], K) / (1.0 + r["c"] * (K - 1))
            dev = abs(r["values"][K] / a - 1.0)
            max_dev_P = max(max_dev_P, dev)
            tol = max(0.01, 6.0 * r["se_rel"][K])
            check(dev <= tol,
                  "Mode P diagnostic dev %.5f <= %.5f cell %s K=%d"
                  % (dev, tol, (r["c"], r["sigma_v"], r["sigma_m"], r["f"]), K))
        check(r["se_rel"][1] < 1e-6,
              "Mode P K=1 zero-variance estimator (constant), cell %s"
              % ((r["c"], r["sigma_v"], r["sigma_m"], r["f"]),))
    max_dev_A = 0.0
    for r in cells_main_A:
        for K in K_GRID:
            a = analytic_mean_A(r["sigma_v"], r["sigma_m"], r["s"], K) \
                / (1.0 + r["c"] * (K - 1))
            dev = abs(r["values"][K] / a - 1.0)
            max_dev_A = max(max_dev_A, dev)
            tol = max(0.01, 6.0 * r["se_rel"][K])
            check(dev <= tol,
                  "Mode A diagnostic dev %.5f <= %.5f cell %s K=%d"
                  % (dev, tol, (r["c"], r["sigma_v"], r["sigma_m"], r["s"]), K))
        if 1 in r["values"]:
            a1 = EHALF * math.exp(0.5 * r["sigma_v"] ** 2)
            check(abs(r["values"][1] * (1.0) / a1 - 1.0) < 1e-9,
                  "Mode A K=1 zero-variance estimator exact, cell %s"
                  % ((r["c"], r["sigma_v"], r["sigma_m"], r["s"]),))
            check(r["se_rel"][1] < 1e-6,
                  "Mode A K=1 zero-variance estimator (constant, up to "
                  "float-cancellation residue in the variance accumulator), "
                  "cell %s" % ((r["c"], r["sigma_v"], r["sigma_m"], r["s"]),))

    # ---- sigma_m inertness in Mode P (estimator is sigma_m-free; across-cell
    # differences are pure MC stream noise)
    for c in C_GRID:
        for sv in SV_GRID:
            for f in F_GRID:
                group = [r for r in cells_main_P
                         if r["c"] == c and r["sigma_v"] == sv and r["f"] == f]
                check(len(group) == 3, "sigma_m group size (c,sv,f)")
                for K in K_GRID:
                    vals = [r["values"][K] for r in group]
                    spread = max(vals) / min(vals) - 1.0
                    check(spread < 0.05,
                          "Mode P sigma_m-inertness spread %.4f (c=%g sv=%g "
                          "f=%g K=%d)" % (spread, c, sv, f, K))

    # ---- pre-registered Arm A/S gate: every f=1 cell, per K, within 1.5%
    max_agree_dev = 0.0
    n_agree = 0
    for r in cells_main_P:
        if r["f"] != 1.0:
            continue
        ref = arm_A[(r["c"], r["sigma_v"])]["values"]
        for K in K_GRID:
            dev = abs(r["values"][K] / ref[K] - 1.0)
            max_agree_dev = max(max_agree_dev, dev)
            n_agree += 1
            check(dev <= AGREE_TOL,
                  "PRE-REGISTERED GATE: Arm S vs Arm A dev %.5f <= 1.5%% "
                  "(c=%g sv=%g sm=%g K=%d)"
                  % (dev, r["c"], r["sigma_v"], r["sigma_m"], K))
    check(n_agree == 135, "agreement gate covered 27 f=1 cells x 5 K")

    # Arm A vs Arm S K*-side agreement on the f=1 slice (report-only: near-ties
    # between K>=2 neighbours may flip; the decision-relevant K*>=2 flag is
    # reported alongside)
    f1_kstar_match = 0
    f1_ge2_match = 0
    n_f1 = 0
    for r in cells_main_P:
        if r["f"] != 1.0:
            continue
        n_f1 += 1
        a = arm_A[(r["c"], r["sigma_v"])]
        if a["kstar"] == r["kstar"]:
            f1_kstar_match += 1
        if (a["kstar"] >= 2) == (r["kstar"] >= 2):
            f1_ge2_match += 1

    # ---- grid stats + pre-registered decision rule
    stats_P = grid_stats(cells_main_P, "P")
    stats_A = grid_stats(cells_main_A, "A")
    ruling = apply_rule(stats_P, stats_A)

    # independent recount of the headline shares (second code path)
    check(stats_P["share_kstar_ge2"] ==
          len([1 for r in cells_main_P if r["kstar"] > 1]) / 81.0,
          "Mode P K*>=2 share recount")
    check(stats_A["share_kstar_ge2"] ==
          len([1 for r in cells_main_A if r["kstar"] > 1]) / 81.0,
          "Mode A K*>=2 share recount")

    # ---- stability leg: ONE stream, M=2000, Mode P grid then Mode A grid
    rng_S = CountingRandom(SEED_STAB)
    stab_P = run_mode("P", rng_S, M_STAB, with_hits=False)
    stab_A = run_mode("A", rng_S, M_STAB, with_hits=False)
    stats_SP = grid_stats(stab_P, "P")
    stats_SA = grid_stats(stab_A, "A")
    ruling_stab = apply_rule(stats_SP, stats_SA)
    check(ruling_stab == ruling,
          "PRE-REGISTERED GATE: stability leg (M=2000, seed 20260718) "
          "reproduces the ruling (%s vs %s)" % (ruling_stab, ruling))

    # ---------------------------------------------------------------- output
    def cellrec(r, mode):
        d = {"c": r["c"], "sigma_v": r["sigma_v"], "sigma_m": r["sigma_m"],
             ("f" if mode == "P" else "s"): r["f" if mode == "P" else "s"],
             "value_per_budget_by_K": {str(K): r["values"][K] for K in K_GRID},
             "kstar": r["kstar"], "dR": r["dR"]}
        if "hits" in r:
            d["p_single_by_K"] = {str(K): r["p_single"][K] for K in K_GRID}
            d["hit_prob_by_K"] = {str(K): r["hits"][K] for K in K_GRID}
        return d

    results = {
        "sim": "verdict-020-book-versioning",
        "proposal": GRID["source"]["proposal"],
        "cpython": "%d.%d" % sys.version_info[:2],
        "arm_A_f1_slice": [
            {"c": c, "sigma_v": sv,
             "value_per_budget_by_K": {str(K): arm_A[(c, sv)]["values"][K]
                                       for K in K_GRID},
             "kstar": arm_A[(c, sv)]["kstar"], "dR": arm_A[(c, sv)]["dR"]}
            for c in C_GRID for sv in SV_GRID],
        "mode_P": {"cells": [cellrec(r, "P") for r in cells_main_P],
                   "stats": stats_P},
        "mode_A": {"cells": [cellrec(r, "A") for r in cells_main_A],
                   "stats": stats_A},
        "agreement_gate_f1": {"n_checked": n_agree,
                              "max_rel_dev": max_agree_dev,
                              "tol": AGREE_TOL,
                              "pass": max_agree_dev <= AGREE_TOL},
        "arm_A_vs_S_kstar_f1_slice": {"n_cells": n_f1,
                                      "kstar_exact_match": f1_kstar_match,
                                      "kstar_ge2_match": f1_ge2_match},
        "diagnostic_layer": {"mode_P_max_rel_dev": max_dev_P,
                             "mode_A_max_rel_dev": max_dev_A},
        "stability_leg": {"M": M_STAB, "seed": SEED_STAB,
                          "ruling": ruling_stab,
                          "matches_main": ruling_stab == ruling,
                          "mode_P_stats": stats_SP, "mode_A_stats": stats_SA},
        "ruling": {
            "decision": ruling,
            "rule": GRID["bands"],
            "mode_P": {"share_kstar_ge2": stats_P["share_kstar_ge2"],
                       "share_kstar_eq1": stats_P["share_kstar_eq1"],
                       "median_dR": stats_P["median_dR"],
                       "flip_axes": stats_P["flip_axes"],
                       "flip_axis_spread": stats_P["flip_axis_spread"]},
            "mode_A": {"share_kstar_ge2": stats_A["share_kstar_ge2"],
                       "share_kstar_eq1": stats_A["share_kstar_eq1"],
                       "median_dR": stats_A["median_dR"],
                       "flip_axes": stats_A["flip_axes"],
                       "flip_axis_spread": stats_A["flip_axis_spread"]},
        },
        "self_checks": dict(_CHECKS),
    }

    def round_floats(obj):
        if isinstance(obj, float):
            return float("%.9g" % obj)
        if isinstance(obj, dict):
            return {k: round_floats(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [round_floats(v) for v in obj]
        return obj

    # self_checks count is finalized AFTER dumping — pin the pre-dump count
    results["self_checks"] = {"counted_at_dump": _CHECKS["passed"],
                              "failed_at_dump": _CHECKS["failed"]}
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(round_floats(results), fh, indent=1, sort_keys=True)
        fh.write("\n")

    # ------------------------------------------------------------- stdout
    print("Arm A/S agreement gate (27 f=1 cells x 5 K): max rel dev %.5f "
          "(tol 0.015) -> %s" % (max_agree_dev,
                                 "PASS" if max_agree_dev <= AGREE_TOL
                                 else "FAIL — RUN INVALID"))
    print("diagnostic layer max rel dev: Mode P %.5f, Mode A %.5f"
          % (max_dev_P, max_dev_A))
    print("f=1 slice K*: exact match %d/%d, K*>=2 flag match %d/%d (Arm A vs S)"
          % (f1_kstar_match, n_f1, f1_ge2_match, n_f1))
    for mode, st in (("P", stats_P), ("A", stats_A)):
        print("Mode %s: K*>=2 in %.4f of cells; K*=1 in %.4f; median dR "
              "%+.4f; K* counts %s; flip axes %s (spread %.4f)"
              % (mode, st["share_kstar_ge2"], st["share_kstar_eq1"],
                 st["median_dR"], st["kstar_counts"], st["flip_axes"],
                 st["flip_axis_spread"]))
        print("  per-axis K*>=2 shares: %s" % st["axis_kstar_ge2_shares"])
    print("stability leg (M=2000 seed 20260718): ruling %s (matches main: %s)"
          % (ruling_stab, ruling_stab == ruling))
    print("PRE-REGISTERED RULING: %s" % ruling)
    print("SELF-CHECKS: %d passed, %d failed"
          % (_CHECKS["passed"], _CHECKS["failed"]))
    if _CHECKS["failed"]:
        for msg in _FAILURES[:50]:
            print("  FAILED: %s" % msg)
        return 1
    return 0


def run_mode_prefix(mode, rng, M, n_cells):
    """First n_cells cells of a mode grid (stream prefix replay)."""
    cells = (cells_P() if mode == "P" else cells_A())[:n_cells]
    out = []
    for cell in cells:
        c, sv, sm, last = cell
        values = {}
        for K in K_GRID:
            if mode == "P":
                mean, _, _ = run_leg_P(rng, M, sv, sm, last, K)
            else:
                mean, _, _ = run_leg_A(rng, M, sv, sm, last, K)
            values[K] = mean / (1.0 + c * (K - 1))
        out.append({"values": values})
    return out


if __name__ == "__main__":
    sys.exit(main())
