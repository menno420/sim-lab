#!/usr/bin/env python3
"""verdict-028 — round-3 breadth budget under the q99 bar (idea-engine PROPOSAL 026).

Fully hermetic NUMERIC SIMULATION (rung 1): the POWER complement of
VERDICT 024's null-side burden bar. Per-instrument epoch drifts of known
strength kappa and persistence horizon E are planted into V024's own
committed panel machinery (byte-reused from
sims/verdict-024-keep-margins-noise/ @ sim-lab 5e356ed), and the expected
true-keep yield Y(cell, N) each nested design grid G6 c G10 c G24 c G96
harvests under its own in-run kappa=0 null q99 bar is measured across
27 decision cells. ZERO real market bars; no dev-candidate is evaluated on
any data; the owner-gated post-2026 protocol is untouched.

Reads exactly ONE file: its own committed fixtures.json (the
pre-registration), cross-checked against in-code literals at start. No
network, no git, no wall clock. stdout and results.json are byte-identical
across process runs (verified by external diff). Progress goes to stderr
only (excluded from the byte-diff by construction).

Run: python3 sims/verdict-028-breadth-budget-power/breadth_budget_power_sim.py
Exit 0 iff all self-checks pass.
"""

import json
import math
import os
import random
import sys
from fractions import Fraction
from statistics import NormalDist, median

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- constants
# Parent machinery constants — byte-reused from V024 (sims/verdict-024-…).
J_MAIN = 9
T = 2595
PB = 21                      # bars per period (the lane's frozen interval)
NP = 123                     # full periods (123*21 = 2583 <= 2595)
WARM = 12                    # warm-up periods (252 bars = max lookback)
EVAL_P0 = 12                 # first evaluation period
NEVAL = 111                  # evaluation periods 12..122
SIGMA_ANN = 0.30
SIGMA_D = SIGMA_ANN / math.sqrt(252.0)
COST = 0.001                 # 10 bp per side; charge COST*2*replaced/k
P_CC, P_SS = 0.98, 0.94      # RSV constants (reporting arm only)
VAR_CALM, VAR_STRESS = 0.6, 2.2
M_CALM, M_STRESS = math.sqrt(VAR_CALM), math.sqrt(VAR_STRESS)
PI_CALM = 0.75
L_ALL = (21, 42, 63, 84, 105, 126, 189, 252)
K_ALL = (2, 3, 4)
SQRT12 = math.sqrt(12.0)
ICDF = NormalDist().inv_cdf   # one uniform per normal (V024 disclosure 1);
                              # a drawn 0.0 raises StatisticsError = invalid.

# This head's constants — from the idea file, cross-checked vs fixtures.json.
S_BH = 1.15
RHOS = (0.0, 0.3, 0.6)
KAPPAS = (0.5, 1.0, 2.0)
ES = (21, 63, 252)
NS = (6, 10, 24, 96)
M_NULL = 1000
M_CELL = 400
M_STAB = 200
M_VALID = 500
M_REPORT = 250
SEED_MAIN = 20260748
SEED_STAB = 20260749
SEED_VALREP = 20260750
SEED_AUX = 20260751
THETA_LINE = 0.10            # materiality (true-edge) line
ALPHA_AMP = SIGMA_D / math.sqrt(252.0)   # per-bar drift for kappa = 1
ANCHOR_TOL = 0.05
ANCHORS = {                  # V024 results.json, IID/S_bh=1.15, rate 0.0010
    0.0: {6: 0.3983240156544581, 24: 0.4915611654470813, 96: 0.5844755463006072},
    0.3: {6: 0.36690217335833175, 24: 0.42722598328634476, 96: 0.4548974486103219},
    0.6: {6: 0.301072200222968, 24: 0.3607737009873204, 96: 0.3909020558622308},
}
FAMILYWISE_C_MAX = 11        # |c/500 - 0.01| <= 3*sqrt(.01*.99/500) <=> c <= 11

# Config grid, pinned order (V024): L asc, k asc, direction mom<rev, eq<rl.
CONFIGS = [(L, k, d, w) for L in L_ALL for k in K_ALL
           for d in ("mom", "rev") for w in ("eq", "rl")]
NCFG = len(CONFIGS)
G6_SET = {(L, k, "mom", "eq") for L in (63, 126, 252) for k in (2, 3)}
G10_SET = G6_SET | {(L, k, "mom", "eq") for L in (21, 42) for k in (2, 3)}
G24_SET = {(L, k, d, "eq") for L in (21, 42, 63, 84, 126, 252)
           for k in (2, 3) for d in ("mom", "rev")}
IDX6 = [i for i, c in enumerate(CONFIGS) if c in G6_SET]
IDX10 = [i for i, c in enumerate(CONFIGS) if c in G10_SET]
IDX24 = [i for i, c in enumerate(CONFIGS) if c in G24_SET]
IDX96 = list(range(NCFG))
IDXN = {6: IDX6, 10: IDX10, 24: IDX24, 96: IDX96}
IDX_MOM63 = CONFIGS.index((63, 2, "mom", "eq"))
IDX_REV63 = CONFIGS.index((63, 2, "rev", "eq"))
EMATCH = {21: CONFIGS.index((21, 2, "mom", "eq")),
          63: IDX_MOM63,
          252: CONFIGS.index((252, 2, "mom", "eq"))}
MARG_CLASSES = (
    ("covered_horizon_duplicate", (84, 2, "mom", "eq")),
    ("uncovered_short_horizon", (21, 2, "mom", "eq")),
    ("direction_decoy", (63, 2, "rev", "eq")),
    ("weighting_variant", (63, 2, "mom", "rl")),
)
MARG_IDX = [CONFIGS.index(c) for _, c in MARG_CLASSES]

# 27 decision cells, pinned lexicographic order: kappa outer, then E, then rho.
PCELLS = [(k, e, r) for k in KAPPAS for e in ES for r in RHOS]

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


def mu_d_for(rho, sbh, J):
    return sbh * SIGMA_D * math.sqrt(rho + (1.0 - rho) / J) / math.sqrt(252.0)


def n_epochs(E):
    return -(-T // E)        # ceil(T/E); last partial epoch kept


# ------------------------------------------------------------ panel machinery
def gen_panel(rng, J, rsv, rho, mu_d, kappa=0.0, E=0, alphas=None):
    """V024's generator + the planted epoch-drift layer.

    Pinned draw order: alpha g_{j,e} (j outer, e inner; ZERO draws at
    kappa=0 or when alphas are injected), then regime chain (RSV only:
    1 stationary + T-1 transitions), then f_t (t asc), then z_{j,t}
    (j outer, t inner). Returns (prefs, chain_stats)."""
    rr = rng.random
    sr = math.sqrt(rho)
    s1r = math.sqrt(1.0 - rho)
    if alphas is None and kappa != 0.0:
        amp = kappa * ALPHA_AMP
        nep = n_epochs(E)
        alphas = [[amp * ICDF(rr()) for _ in range(nep)] for _ in range(J)]
    chain_stats = None
    if rsv:
        m = [0.0] * T
        st = 0 if rr() < PI_CALM else 1
        n_stress = st
        ncc = ncs = nsc = nss = 0
        mv = (M_CALM, M_STRESS)
        m[0] = mv[st]
        for t in range(1, T):
            u = rr()
            if st == 0:
                if u < P_CC:
                    ncc += 1
                else:
                    st = 1
                    ncs += 1
            else:
                if u < P_SS:
                    nss += 1
                else:
                    st = 0
                    nsc += 1
            n_stress += st
            m[t] = mv[st]
        chain_stats = (n_stress, ncc, ncs, nsc, nss)
        a = [mi * SIGMA_D * sr for mi in m]
        b = [mi * SIGMA_D * s1r for mi in m]
        c = [mu_d + a[t] * ICDF(rr()) for t in range(T)]
        prefs = []
        for j in range(J):
            aj = alphas[j] if alphas is not None else None
            s = 0.0
            row = [0.0] * (T + 1)
            if aj is None:
                for t in range(T):
                    s += c[t] + b[t] * ICDF(rr())
                    row[t + 1] = s
            else:
                for t in range(T):
                    s += c[t] + aj[t // E] + b[t] * ICDF(rr())
                    row[t + 1] = s
            prefs.append(row)
    else:
        asd = SIGMA_D * sr
        bsd = SIGMA_D * s1r
        c = [mu_d + asd * ICDF(rr()) for _ in range(T)]
        prefs = []
        for j in range(J):
            aj = alphas[j] if alphas is not None else None
            s = 0.0
            row = [0.0] * (T + 1)
            if aj is None:
                for t in range(T):
                    s += c[t] + bsd * ICDF(rr())
                    row[t + 1] = s
            else:
                for t in range(T):
                    s += c[t] + aj[t // E] + bsd * ICDF(rr())
                    row[t + 1] = s
            prefs.append(row)
    return prefs, chain_stats


def draws_per_panel(J, rsv, kappa=0.0, E=0):
    d = (J + 1) * T + (T if rsv else 0)
    if kappa != 0.0:
        d += J * n_epochs(E)
    return d


def eval_panel(prefs, J):
    """V024's main strategy evaluator, byte-reused (prefix sums, incremental
    top-k cumsums). Returns per-config accumulators over the 111 evaluation
    periods: (Spre, Spre2, Su, Su2, Spu, Sb, Sb2)."""
    rj = range(J)
    R = [[prefs[j][PB * (p + 1)] - prefs[j][PB * p] for j in rj]
         for p in range(NP)]
    Spre = [0.0] * NCFG
    Spre2 = [0.0] * NCFG
    Su = [0.0] * NCFG
    Su2 = [0.0] * NCFG
    Spu = [0.0] * NCFG
    Sb = 0.0
    Sb2 = 0.0
    prev = [None] * (len(L_ALL) * 2 * 3)
    for p in range(EVAL_P0, NP):
        Rp = R[p]
        bas = sum(Rp) / J
        Sb += bas
        Sb2 += bas * bas
        t = PB * p
        for Li, L in enumerate(L_ALL):
            tl = t - L
            vals = [prefs[j][t] - prefs[j][tl] for j in rj]
            asc = sorted((vals[j], j) for j in rj)
            desc = sorted((-vals[j], j) for j in rj)
            for di, order in ((0, desc), (1, asc)):
                j0 = order[0][1]
                j1 = order[1][1]
                j2 = order[2][1]
                j3 = order[3][1]
                r0 = Rp[j0]
                c2 = r0 + Rp[j1]
                c3 = c2 + Rp[j2]
                c4 = c3 + Rp[j3]
                slot = (Li * 2 + di) * 3
                base = Li * 12 + di * 2
                # k = 2
                pv = prev[slot]
                if pv is None:
                    u = 0.0
                    prev[slot] = {j0, j1}
                else:
                    repl = 2 - ((j0 in pv) + (j1 in pv))
                    u = float(repl)
                    if repl:
                        prev[slot] = {j0, j1}
                x = c2 * 0.5
                i = base
                Spre[i] += x
                Spre2[i] += x * x
                Su[i] += u
                Su2[i] += u * u
                Spu[i] += x * u
                x = (r0 + c2) / 3.0
                i += 1
                Spre[i] += x
                Spre2[i] += x * x
                Su[i] += u
                Su2[i] += u * u
                Spu[i] += x * u
                # k = 3
                pv = prev[slot + 1]
                if pv is None:
                    u = 0.0
                    prev[slot + 1] = {j0, j1, j2}
                else:
                    repl = 3 - ((j0 in pv) + (j1 in pv) + (j2 in pv))
                    u = repl * (2.0 / 3.0)
                    if repl:
                        prev[slot + 1] = {j0, j1, j2}
                x = c3 / 3.0
                i = base + 4
                Spre[i] += x
                Spre2[i] += x * x
                Su[i] += u
                Su2[i] += u * u
                Spu[i] += x * u
                x = (r0 + c2 + c3) / 6.0
                i += 1
                Spre[i] += x
                Spre2[i] += x * x
                Su[i] += u
                Su2[i] += u * u
                Spu[i] += x * u
                # k = 4
                pv = prev[slot + 2]
                if pv is None:
                    u = 0.0
                    prev[slot + 2] = {j0, j1, j2, j3}
                else:
                    repl = 4 - ((j0 in pv) + (j1 in pv) + (j2 in pv) + (j3 in pv))
                    u = repl * 0.5
                    if repl:
                        prev[slot + 2] = {j0, j1, j2, j3}
                x = c4 * 0.25
                i = base + 8
                Spre[i] += x
                Spre2[i] += x * x
                Su[i] += u
                Su2[i] += u * u
                Spu[i] += x * u
                x = (r0 + c2 + c3 + c4) * 0.1
                i += 1
                Spre[i] += x
                Spre2[i] += x * x
                Su[i] += u
                Su2[i] += u * u
                Spu[i] += x * u
    return Spre, Spre2, Su, Su2, Spu, Sb, Sb2


def deltas_from_stats(stats, rate):
    """Post-cost Delta per config at the given per-side cost rate (V024)."""
    Spre, Spre2, Su, Su2, Spu, Sb, Sb2 = stats
    n = float(NEVAL)
    mb = Sb / n
    vb = (Sb2 - n * mb * mb) / (n - 1.0)
    shb = mb / math.sqrt(vb) * SQRT12
    out = [0.0] * NCFG
    for i in range(NCFG):
        sx = Spre[i] - rate * Su[i]
        sx2 = Spre2[i] - 2.0 * rate * Spu[i] + rate * rate * Su2[i]
        mean = sx / n
        var = (sx2 - n * mean * mean) / (n - 1.0)
        out[i] = mean / math.sqrt(var) * SQRT12 - shb
    return out, shb


def dmaxes(deltas):
    d6 = max(deltas[i] for i in IDX6)
    d10 = max(deltas[i] for i in IDX10)
    d24 = max(deltas[i] for i in IDX24)
    d96 = max(deltas)
    return d6, d10, d24, d96


# ------------------------------------------------------- independent twin
def twin_eval(prefs, J, rate):
    """V024's independently written evaluator, byte-reused: direct bar sums,
    its own sorts, explicit weight vectors, explicit turnover sets,
    statistics-module mean/stdev."""
    import statistics as st
    r = [[prefs[j][t + 1] - prefs[j][t] for t in range(T)] for j in range(J)]
    bas = []
    for p in range(EVAL_P0, NP):
        t = PB * p
        bas.append(sum(sum(r[j][t:t + PB]) for j in range(J)) / J)
    shb = st.mean(bas) / st.stdev(bas) * math.sqrt(12)
    out = []
    for (L, k, dirn, wt) in CONFIGS:
        if wt == "eq":
            w = [1.0 / k] * k
        else:
            tot = k * (k + 1) / 2
            w = [(k + 1 - i) / tot for i in range(1, k + 1)]
        held = None
        rets = []
        for p in range(EVAL_P0, NP):
            t = PB * p
            scores = [(sum(r[j][t - L:t]), j) for j in range(J)]
            if dirn == "mom":
                order = sorted(scores, key=lambda s_: (-s_[0], s_[1]))
            else:
                order = sorted(scores, key=lambda s_: (s_[0], s_[1]))
            sel = [j for _, j in order[:k]]
            x = 0.0
            for wi, j in zip(w, sel):
                x += wi * sum(r[j][t:t + PB])
            ns = set(sel)
            if held is not None:
                x -= rate * 2.0 * len(ns - held) / k
            held = ns
            rets.append(x)
        out.append(st.mean(rets) / st.stdev(rets) * math.sqrt(12) - shb)
    return out, shb


def k9_delta(prefs, J):
    """V024 gate (a): the k=J control config; must equal the zero-cost
    basket to 1e-12."""
    prev = None
    rets = []
    brets = []
    for p in range(EVAL_P0, NP):
        t = PB * p
        order = sorted((-(prefs[j][t] - prefs[j][t - 63]), j) for j in range(J))
        sel = [j for _, j in order]
        x = 0.0
        for j in sel:
            x += prefs[j][PB * (p + 1)] - prefs[j][PB * p]
        x /= J
        ns = set(sel)
        if prev is not None:
            x -= COST * 2.0 * len(ns - prev) / J
        prev = ns
        rets.append(x)
        b = 0.0
        for j in range(J):
            b += prefs[j][PB * (p + 1)] - prefs[j][PB * p]
        brets.append(b / J)
    n = float(NEVAL)

    def sh(v):
        m = sum(v) / n
        va = sum((x - m) ** 2 for x in v) / (n - 1.0)
        return m / math.sqrt(va) * SQRT12

    return sh(rets) - sh(brets)


# ------------------------------------------------------------- quantiles
def quant(sorted_vals, q):
    """Left-continuous empirical quantile (V024 convention)."""
    return sorted_vals[math.ceil(q * len(sorted_vals)) - 1]


def sentinel_check(rng, seed, total_draws, leg_name):
    live_next = rng.random()
    fresh = random.Random(seed)
    fr = fresh.random
    for _ in range(total_draws):
        fr()
    check(fr() == live_next,
          "%s draw-count sentinel (%d draws)" % (leg_name, total_draws))


# --------------------------------------------------------------- null legs
def run_null_leg(rng, M, rho, leg_name, twin_panel0=True):
    """kappa = 0 null leg at one rho: collects sorted Delta_max lists for
    the four design grids and the four G7 marginal variants. Returns
    (dmax_lists, dmax7_lists, draws)."""
    mu_d = mu_d_for(rho, S_BH, J_MAIN)
    dpp = draws_per_panel(J_MAIN, False)
    lists = {N: [] for N in NS}
    lists7 = {name: [] for name, _ in MARG_CLASSES}
    draws = 0
    for i in range(M):
        if i == 0:
            pre_state = rng.getstate()
        prefs, _ = gen_panel(rng, J_MAIN, False, rho, mu_d)
        draws += dpp
        stats = eval_panel(prefs, J_MAIN)
        deltas, _ = deltas_from_stats(stats, COST)
        if i == 0:
            post_state = rng.getstate()
            rng.setstate(pre_state)
            prefs_r, _ = gen_panel(rng, J_MAIN, False, rho, mu_d)
            deltas_r, _ = deltas_from_stats(eval_panel(prefs_r, J_MAIN), COST)
            check(deltas_r == deltas, "%s determinism replay" % leg_name)
            rng.setstate(post_state)
            if twin_panel0:
                tw, _ = twin_eval(prefs, J_MAIN, COST)
                for cf in range(NCFG):
                    check(abs(tw[cf] - deltas[cf]) <= 1e-9,
                          "%s twin config %d" % (leg_name, cf))
        if i < 10:
            check(abs(k9_delta(prefs, J_MAIN)) <= 1e-12,
                  "%s panel %d gate k=9 identity" % (leg_name, i))
        check(all(map(math.isfinite, deltas)),
              "%s panel %d finite deltas" % (leg_name, i))
        d6, d10, d24, d96 = dmaxes(deltas)
        check(d6 <= d10 <= d24 <= d96,
              "%s mono d6<=d10<=d24<=d96" % leg_name)
        lists[6].append(d6)
        lists[10].append(d10)
        lists[24].append(d24)
        lists[96].append(d96)
        for (name, _), ci in zip(MARG_CLASSES, MARG_IDX):
            lists7[name].append(max(d6, deltas[ci]))
    for N in NS:
        lists[N].sort()
    for name, _ in MARG_CLASSES:
        lists7[name].sort()
    log("[%s] M=%d done, q99(G6)=%.4f q99(G10)=%.4f q99(G24)=%.4f q99(G96)=%.4f"
        % (leg_name, M, quant(lists[6], 0.99), quant(lists[10], 0.99),
           quant(lists[24], 0.99), quant(lists[96], 0.99)))
    return lists, lists7, draws


# ------------------------------------------------------------ planted cells
def run_planted_cell(rng, M, kappa, E, rho, rsv, sbh, bars, bars7, leg_name,
                     twin_idxs=(0,), k9_first=10, want_marg=False):
    """One planted cell: M panels, keep counts vs the four bars (and the four
    G7 bars when want_marg), per-config Delta sums for the oracle."""
    mu_d = mu_d_for(rho, sbh, J_MAIN)
    dpp = draws_per_panel(J_MAIN, rsv, kappa, E)
    sum_d = [0.0] * NCFG
    sum_d2 = [0.0] * NCFG
    p_sum = 0.0                  # paired per-panel Delta_mom63 - Delta_rev63
    p_sum2 = 0.0
    kc = {N: [0] * NCFG for N in NS}
    kc7 = {name: [0] * NCFG for name, _ in MARG_CLASSES} if want_marg else None
    draws = 0
    for i in range(M):
        if i == 0:
            pre_state = rng.getstate()
        prefs, _ = gen_panel(rng, J_MAIN, rsv, rho, mu_d, kappa, E)
        draws += dpp
        stats = eval_panel(prefs, J_MAIN)
        deltas, _ = deltas_from_stats(stats, COST)
        if i == 0:
            post_state = rng.getstate()
            rng.setstate(pre_state)
            prefs_r, _ = gen_panel(rng, J_MAIN, rsv, rho, mu_d, kappa, E)
            deltas_r, _ = deltas_from_stats(eval_panel(prefs_r, J_MAIN), COST)
            check(deltas_r == deltas, "%s determinism replay" % leg_name)
            rng.setstate(post_state)
        if i in twin_idxs:
            tw, _ = twin_eval(prefs, J_MAIN, COST)
            for cf in range(NCFG):
                check(abs(tw[cf] - deltas[cf]) <= 1e-9,
                      "%s panel %d twin config %d" % (leg_name, i, cf))
        if i < k9_first:
            check(abs(k9_delta(prefs, J_MAIN)) <= 1e-12,
                  "%s panel %d gate k=9 identity" % (leg_name, i))
        check(all(map(math.isfinite, deltas)),
              "%s panel %d finite deltas" % (leg_name, i))
        for cf in range(NCFG):
            d = deltas[cf]
            sum_d[cf] += d
            sum_d2[cf] += d * d
        dp = deltas[IDX_MOM63] - deltas[IDX_REV63]
        p_sum += dp
        p_sum2 += dp * dp
        for N in NS:
            bN = bars[N]
            kcN = kc[N]
            for cf in IDXN[N]:
                if deltas[cf] >= bN:
                    kcN[cf] += 1
        if want_marg:
            for (name, _), ci in zip(MARG_CLASSES, MARG_IDX):
                b7 = bars7[name]
                kk = kc7[name]
                for cf in IDX6:
                    if deltas[cf] >= b7:
                        kk[cf] += 1
                if deltas[ci] >= b7:
                    kk[ci] += 1
    theta = [sum_d[cf] / M for cf in range(NCFG)]
    se = [math.sqrt(max(0.0, (sum_d2[cf] - M * theta[cf] * theta[cf])
                        / (M - 1.0)) / M) for cf in range(NCFG)]
    p_mean = p_sum / M
    p_se = math.sqrt(max(0.0, (p_sum2 - M * p_mean * p_mean)
                         / (M - 1.0)) / M)
    for cf in range(NCFG):
        check(abs(theta[cf] - THETA_LINE) > 1e-9,
              "%s theta boundary clearance config %d" % (leg_name, cf))
    truth = [theta[cf] >= THETA_LINE for cf in range(NCFG)]
    SC = {N: sum(kc[N][cf] for cf in IDXN[N] if truth[cf]) for N in NS}
    FC = {N: sum(kc[N][cf] for cf in IDXN[N] if not truth[cf]) for N in NS}
    return {"theta": theta, "se": se, "truth": truth, "kc": kc, "kc7": kc7,
            "SC": SC, "FC": FC, "M": M, "draws": draws,
            "pair_mean": p_mean, "pair_se": p_se}


def cell_decision_stats(cell):
    """Exact integer N*/detectability from true-keep count sums."""
    SC = cell["SC"]
    M = cell["M"]
    max_sc = max(SC[N] for N in NS)
    detectable = 4 * max_sc >= M                     # max Y >= 0.25 exact
    nstar = None
    for N in NS:
        if 20 * SC[N] >= 19 * max_sc:                # Y(N) >= 0.95*maxY exact
            nstar = N
            break
    return detectable, nstar, max_sc


# --------------------------------------------------------- decision (twins)
def decide_A(cells_stats, M):
    """Float-arithmetic decision evaluator. cells_stats: list of
    (kappa, E, rho, detectable, nstar, SC6, SC96) in PCELLS order."""
    det = [c for c in cells_stats if c[3]]
    n_det = len(det)
    n_le10 = sum(1 for c in det if c[4] is not None and c[4] <= 10)
    n_ge24 = sum(1 for c in det if c[4] is not None and c[4] >= 24)
    spreads = [(c[6] - c[5]) / M for c in det]
    med_spread = median(spreads) if spreads else None
    if n_det < 8:
        ruling = "null"
        basis = "detectability floor: %d/27 detectable < 8" % n_det
    elif 5 * n_le10 >= 4 * n_det:
        ruling = "reject"
        basis = "N* <= 10 in %d/%d detectable cells (>= 80%%)" % (n_le10, n_det)
    elif 5 * n_ge24 >= 4 * n_det and med_spread is not None \
            and med_spread >= 0.25:
        ruling = "approve"
        basis = ("N* >= 24 in %d/%d detectable cells and median "
                 "Y(96)-Y(6) = %.4f >= 0.25" % (n_ge24, n_det, med_spread))
    else:
        ruling = "null"
        basis = ("neither band: N*<=10 share %d/%d, N*>=24 share %d/%d, "
                 "median Y(96)-Y(6) %s"
                 % (n_le10, n_det, n_ge24, n_det,
                    "%.4f" % med_spread if med_spread is not None else "n/a"))
    axes = {}
    for pos, name, keys in ((0, "kappa", KAPPAS), (1, "E", ES), (2, "rho", RHOS)):
        vals = {}
        shares = []
        for v in keys:
            dv = [c for c in det if c[pos] == v]
            n_all = sum(1 for c in cells_stats if c[pos] == v)
            if dv:
                s10 = sum(1 for c in dv if c[4] is not None and c[4] <= 10) / len(dv)
                s24 = sum(1 for c in dv if c[4] is not None and c[4] >= 24) / len(dv)
                ms = median((c[6] - c[5]) / M for c in dv)
                vals[str(v)] = {"n_detectable": len(dv), "n_cells": n_all,
                                "share_nstar_le10": s10,
                                "share_nstar_ge24": s24,
                                "median_Y96_minus_Y6": ms}
                shares.append(s10)
            else:
                vals[str(v)] = {"n_detectable": 0, "n_cells": n_all,
                                "share_nstar_le10": None,
                                "share_nstar_ge24": None,
                                "median_Y96_minus_Y6": None}
        spread = (max(shares) - min(shares)) if len(shares) >= 2 else 0.0
        axes[name] = {"values": vals, "spread_share_le10": spread}
    max_spread = max(a["spread_share_le10"] for a in axes.values())
    flip = [n for n, a in axes.items() if a["spread_share_le10"] == max_spread]
    return ruling, basis, n_det, n_le10, n_ge24, med_spread, axes, flip


def decide_B(cells_stats, M):
    """Independent Fraction-arithmetic decision evaluator."""
    det = [c for c in cells_stats if c[3]]
    n_det = len(det)
    n_le10 = sum(1 for c in det if c[4] is not None and c[4] <= 10)
    n_ge24 = sum(1 for c in det if c[4] is not None and c[4] >= 24)
    spreads = [Fraction(c[6] - c[5], M) for c in det]
    med_spread = median(spreads) if spreads else None
    if n_det < 8:
        ruling = "null"
    elif Fraction(n_le10, n_det) >= Fraction(4, 5):
        ruling = "reject"
    elif Fraction(n_ge24, n_det) >= Fraction(4, 5) and med_spread is not None \
            and med_spread >= Fraction(1, 4):
        ruling = "approve"
    else:
        ruling = "null"
    axes_spread = {}
    for pos, name, keys in ((0, "kappa", KAPPAS), (1, "E", ES), (2, "rho", RHOS)):
        shares = []
        for v in keys:
            dv = [c for c in det if c[pos] == v]
            if dv:
                shares.append(Fraction(
                    sum(1 for c in dv if c[4] is not None and c[4] <= 10),
                    len(dv)))
        spread = (max(shares) - min(shares)) if len(shares) >= 2 else Fraction(0)
        axes_spread[name] = spread
    max_spread = max(axes_spread.values())
    flip = [n for n, s in axes_spread.items() if s == max_spread]
    return ruling, n_det, n_le10, n_ge24, med_spread, flip


# ------------------------------------------------------------ hand pins
def build_pin1():
    prefs = []
    for j in range(J_MAIN):
        s = 0.0
        row = [0.0] * (T + 1)
        for t in range(T):
            s += j * 1e-4 + 0.01 * (1.0 if t % 2 == 0 else -1.0)
            row[t + 1] = s
        prefs.append(row)
    return prefs


def build_pin2():
    prefs = []
    for j in range(J_MAIN):
        s = 0.0
        row = [0.0] * (T + 1)
        for t in range(T):
            q = 1.0 if (t // PB) % 2 == 0 else -1.0
            common = 0.01 * (1.0 if t % 2 == 0 else -1.0)
            if j == 8:
                v = 1e-3 * q + common
            elif j == 7:
                v = -1e-3 * q + common
            else:
                v = common
            s += v
            row[t + 1] = s
        prefs.append(row)
    return prefs


def sharpe_of_multiset(pairs):
    n = sum(c for _, c in pairs)
    mean = sum(Fraction(v) * c for v, c in pairs) / n
    var = sum((Fraction(v) - mean) ** 2 * c for v, c in pairs) / (n - 1)
    return float(mean) / math.sqrt(float(var)) * SQRT12


def run_pins():
    # ---- PIN1 (V024, byte-reused: validates the shared evaluator)
    prefs = build_pin1()
    stats = eval_panel(prefs, J_MAIN)
    deltas, _ = deltas_from_stats(stats, COST)
    check(all(u == 0.0 for u in stats[2]), "PIN1 zero turnover on all configs")
    ratio = math.sqrt(12.0 * 1221.0 / 1232.0)
    exp_eq = 0.735 * ratio
    exp_rl = 0.77 * ratio
    check(abs(exp_eq - 2.534722617960395) <= 1e-12, "PIN1 committed float eq")
    check(abs(exp_rl - 2.6554236950061285) <= 1e-12, "PIN1 committed float rl")
    check(abs(deltas[CONFIGS.index((63, 2, "mom", "eq"))] - exp_eq) <= 1e-9,
          "PIN1 (63,2,mom,eq)")
    check(abs(deltas[CONFIGS.index((63, 2, "rev", "eq"))] + exp_eq) <= 1e-9,
          "PIN1 (63,2,rev,eq)")
    check(abs(deltas[CONFIGS.index((63, 2, "mom", "rl"))] - exp_rl) <= 1e-9,
          "PIN1 (63,2,mom,rl)")
    d6, d10, d24, d96 = dmaxes(deltas)
    check(abs(d6 - exp_eq) <= 1e-9 and abs(d10 - exp_eq) <= 1e-9,
          "PIN1 dmax(G6)=dmax(G10)")
    check(abs(d96 - exp_rl) <= 1e-9, "PIN1 dmax(G96) = k2 mom rank-linear")
    # ---- PIN2 (V024, byte-reused)
    prefs = build_pin2()
    stats = eval_panel(prefs, J_MAIN)
    deltas, _ = deltas_from_stats(stats, COST)
    icfg = CONFIGS.index((21, 2, "mom", "eq"))
    check(stats[2][icfg] == 110.0, "PIN2 turnover sum == 110")
    check(stats[3][icfg] == 110.0, "PIN2 turnover sumsq == 110")
    check(abs(COST * stats[2][icfg] - 0.110) <= 1e-15, "PIN2 total cost 0.110")
    sh_strat = sharpe_of_multiset([
        (Fraction(-5, 10000), 1),
        (Fraction(-215, 10000), 55),
        (Fraction(-15, 10000), 55),
    ])
    sh_bask = sharpe_of_multiset([
        (Fraction(1, 100), 56), (Fraction(-1, 100), 55)])
    check(abs(deltas[icfg] - (sh_strat - sh_bask)) <= 1e-9,
          "PIN2 Delta (21,2,mom,eq) vs exact multiset Sharpe")
    # ---- PIN3 (NEW): alpha-injection identity — a panel generated with
    # hand-pinned alphas must differ from the same-seed alphas=0 panel by
    # exactly the running alpha prefix sums (epoch map e(t) = t // E).
    E = 252
    nep = n_epochs(E)
    check(nep == 11, "PIN3 n_epochs(252) == 11")
    check(n_epochs(21) == 124 and n_epochs(63) == 42, "PIN3 epoch counts")
    A = [[((j + 1) * (e + 1) % 7 - 3) * 1e-4 for e in range(nep)]
         for j in range(J_MAIN)]
    Z = [[0.0] * nep for _ in range(J_MAIN)]
    mu_d = mu_d_for(0.3, S_BH, J_MAIN)
    p0, _ = gen_panel(random.Random(987654), J_MAIN, False, 0.3, mu_d,
                      kappa=1.0, E=E, alphas=Z)
    pA, _ = gen_panel(random.Random(987654), J_MAIN, False, 0.3, mu_d,
                      kappa=1.0, E=E, alphas=A)
    pP, _ = gen_panel(random.Random(987654), J_MAIN, False, 0.3, mu_d)
    check(pP == p0, "PIN3 zero-alpha panel == plain kappa=0 panel exactly")
    for j in range(J_MAIN):
        s = 0.0
        for t in range(T + 1):
            check(abs((pA[j][t] - p0[j][t]) - s) <= 1e-9,
                  "PIN3 alpha prefix identity j=%d t=%d" % (j, t))
            if t < T:
                s += A[j][t // E]
    log("[pins] PIN1 + PIN2 + PIN3 pass")


# ------------------------------------------------------------- fixtures
def fixture_crosscheck():
    with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as f:
        fx = json.load(f)
    c = fx["constants"]
    check(c["J"] == J_MAIN and c["T"] == T and c["period_bars"] == PB,
          "fixtures J/T/period")
    check(c["n_periods"] == NP and c["warmup_periods"] == WARM and
          c["eval_periods"] == NEVAL, "fixtures period frame")
    check(c["sigma_ann"] == SIGMA_ANN and c["cost_per_side"] == COST,
          "fixtures sigma/cost")
    check(tuple(c["rho_grid"]) == RHOS and tuple(c["kappa_grid"]) == KAPPAS
          and tuple(c["E_grid"]) == ES, "fixtures rho/kappa/E grids")
    check(c["sbh_decision"] == S_BH and c["sbh_stress_reporting_only"] == 0.0,
          "fixtures S_bh")
    check(c["n_decision_cells"] == 27 and len(PCELLS) == 27,
          "fixtures 27 cells")
    check(tuple(c["grids"]["N_grid"]) == NS, "fixtures N grid")
    check(c["M_null"] == M_NULL and c["M_cell"] == M_CELL and
          c["M_stability"] == M_STAB and c["M_validation"] == M_VALID and
          c["M_reporting"] == M_REPORT, "fixtures M per leg")
    check(c["seed_main"] == SEED_MAIN and c["seed_stability"] == SEED_STAB and
          c["seed_validation_reporting"] == SEED_VALREP and
          c["seed_aux"] == SEED_AUX, "fixtures seeds")
    check(c["oracle"]["true_edge_line"] == THETA_LINE and
          c["anchors"]["tolerance_abs"] == ANCHOR_TOL, "fixtures lines")
    av = c["anchors"]["values_full_precision"]
    for rho in RHOS:
        row = av["rho_%.1f" % rho]
        for N in (6, 24, 96):
            check(row["N%d" % N] == ANCHORS[rho][N],
                  "fixtures anchor rho=%.1f N=%d" % (rho, N))
    mc = c["reporting_only_legs"]["marginal_config_price_list"]["classes"]
    check(mc["covered_horizon_duplicate"].startswith("L=84") and
          mc["uncovered_short_horizon"].startswith("L=21") and
          mc["direction_decoy"].startswith("L=63") and
          mc["weighting_variant"].startswith("L=63"), "fixtures marg classes")
    # grid construction + nesting
    check(NCFG == 96 and len(IDX24) == 24 and len(IDX10) == 10 and
          len(IDX6) == 6, "grid sizes 96/24/10/6")
    check(G6_SET <= G10_SET and G10_SET <= G24_SET and
          G24_SET <= set(CONFIGS), "grid nesting G6<G10<G24<G96")
    # familywise gate integer bound re-derivation
    se3 = 3.0 * math.sqrt(0.01 * 0.99 / M_VALID)
    check(11 / M_VALID - 0.01 <= se3 < 12 / M_VALID - 0.01,
          "familywise c_max == 11 re-derivation")
    check(FAMILYWISE_C_MAX == 11, "familywise c_max pinned")
    # mu_d formula recomputation
    got = mu_d_for(0.3, 1.15, 9)
    want = 1.15 * (0.30 / math.sqrt(252.0)) * math.sqrt(0.3 + 0.7 / 9.0) \
        / math.sqrt(252.0)
    check(got == want, "mu_d formula recomputation")
    # E-matched configs exist
    for E in ES:
        check((E, 2, "mom", "eq") in set(CONFIGS), "E-matched config L=%d" % E)
    return fx


# ------------------------------------------------------------------ main
def main():
    check(sys.version_info[:2] == (3, 11),
          "CPython minor pinned: need 3.11, got %d.%d" % sys.version_info[:2])
    fixture_crosscheck()
    run_pins()

    results = {"python": "cpython-%d.%d" % sys.version_info[:2],
               "seeds": {"main": SEED_MAIN, "stability": SEED_STAB,
                         "validation_reporting": SEED_VALREP,
                         "aux": SEED_AUX},
               "configs": ["L=%d k=%d %s %s" % c for c in CONFIGS]}

    # ================= MAIN stream (seed 20260748): null legs then 27 cells
    rng = random.Random(SEED_MAIN)
    main_draws = 0
    bars = {}       # bars[rho][N]
    bars7 = {}      # bars7[rho][class]
    null_json = {}
    for rho in RHOS:
        lists, lists7, d = run_null_leg(rng, M_NULL, rho,
                                        "null rho=%.1f" % rho)
        main_draws += d
        bars[rho] = {N: quant(lists[N], 0.99) for N in NS}
        bars7[rho] = {name: quant(lists7[name], 0.99)
                      for name, _ in MARG_CLASSES}
        null_json["rho_%.1f" % rho] = {
            "q99": {str(N): bars[rho][N] for N in NS},
            "q90": {str(N): quant(lists[N], 0.90) for N in NS},
            "q50": {str(N): quant(lists[N], 0.50) for N in NS},
            "q99_G7": {name: bars7[rho][name] for name, _ in MARG_CLASSES},
        }
    # ---- ANCHOR GATE (run invalid on any failure)
    anchor_rows = []
    for rho in RHOS:
        for N in (6, 24, 96):
            got = bars[rho][N]
            want = ANCHORS[rho][N]
            diff = got - want
            check(abs(diff) <= ANCHOR_TOL,
                  "ANCHOR GATE rho=%.1f N=%d: got %.4f want %.4f (tol 0.05)"
                  % (rho, N, got, want))
            anchor_rows.append({"rho": rho, "N": N, "measured": got,
                                "v024_committed": want, "diff": diff})
    results["null_bars"] = null_json
    results["anchor_gate"] = {"tolerance_abs": ANCHOR_TOL,
                              "rows": anchor_rows, "passed": True}

    # ---- 27 planted decision cells
    main_cells = []
    for ci, (kappa, E, rho) in enumerate(PCELLS):
        cell = run_planted_cell(
            rng, M_CELL, kappa, E, rho, False, S_BH, bars[rho], bars7[rho],
            "main cell %d k=%.1f E=%d rho=%.1f" % (ci, kappa, E, rho),
            twin_idxs=(0, 200), want_marg=(rho == 0.3))
        main_draws += cell["draws"]
        detectable, nstar, max_sc = cell_decision_stats(cell)
        cell.update({"kappa": kappa, "E": E, "rho": rho,
                     "detectable": detectable, "nstar": nstar,
                     "max_sc": max_sc})
        main_cells.append(cell)
        log("[main cell %d/27] k=%.1f E=%d rho=%.1f: Y6=%.3f Y10=%.3f "
            "Y24=%.3f Y96=%.3f det=%s N*=%s"
            % (ci + 1, kappa, E, rho,
               cell["SC"][6] / M_CELL, cell["SC"][10] / M_CELL,
               cell["SC"][24] / M_CELL, cell["SC"][96] / M_CELL,
               detectable, nstar))
    sentinel_check(rng, SEED_MAIN, main_draws, "main stream")

    # ---- ORACLE SIGN GATES (run invalid on any failure).
    # Calibration per the fixtures gate_calibration_disclosure: at E = 21 the
    # epochs align exactly with the 21-bar rebalance frame, so every config's
    # expected theta is identical (exchangeability) — the strict inequality
    # is replaced by the matched two-sided noise band |diff| <= 4*SE_paired,
    # and the kappa-monotonicity check by |diff| <= 4*SE. At E in {63, 252}
    # both gates stay EXACTLY as registered.
    sign_rows = []
    for cell in main_cells:
        tm = cell["theta"][IDX_MOM63]
        tr = cell["theta"][IDX_REV63]
        if cell["E"] == 21:
            mode = "E21_equivalence_4SE_paired"
            ok = abs(cell["pair_mean"]) <= 4.0 * cell["pair_se"]
        else:
            mode = "strict_as_registered"
            ok = tr < tm
        check(ok, "SIGN GATE (%s) cell k=%.1f E=%d rho=%.1f: mom63 %.4f "
              "rev63 %.4f pairSE %.5f"
              % (mode, cell["kappa"], cell["E"], cell["rho"], tm, tr,
                 cell["pair_se"]))
        sign_rows.append({"kappa": cell["kappa"], "E": cell["E"],
                          "rho": cell["rho"], "mode": mode,
                          "theta_mom63": tm, "theta_rev63": tr,
                          "paired_diff_mean": cell["pair_mean"],
                          "paired_diff_se": cell["pair_se"], "passed": True})
    mono_rows = []
    by_key = {(c["kappa"], c["E"], c["rho"]): c for c in main_cells}
    for E in ES:
        cf = EMATCH[E]
        for rho in RHOS:
            for ka, kb in ((0.5, 1.0), (1.0, 2.0)):
                ca = by_key[(ka, E, rho)]
                cb = by_key[(kb, E, rho)]
                sed = math.sqrt(ca["se"][cf] ** 2 + cb["se"][cf] ** 2)
                if E == 21:
                    mode = "E21_equivalence_4SE"
                    ok = abs(cb["theta"][cf] - ca["theta"][cf]) <= 4.0 * sed
                else:
                    mode = "one_sided_2SE_as_registered"
                    ok = cb["theta"][cf] >= ca["theta"][cf] - 2.0 * sed
                check(ok, "SIGN GATE kappa-monotone (%s) E=%d rho=%.1f "
                      "%.1f->%.1f: %.4f -> %.4f (SEd %.5f)"
                      % (mode, E, rho, ka, kb, ca["theta"][cf],
                         cb["theta"][cf], sed))
                mono_rows.append({"E": E, "rho": rho, "kappa_from": ka,
                                  "kappa_to": kb, "mode": mode,
                                  "theta_from": ca["theta"][cf],
                                  "theta_to": cb["theta"][cf],
                                  "se_diff": sed, "passed": True})
    results["sign_gates"] = {"reversal_vs_momentum": sign_rows,
                             "kappa_monotonicity": mono_rows}

    # ---- DECISION (twin evaluators)
    cells_stats = [(c["kappa"], c["E"], c["rho"], c["detectable"], c["nstar"],
                    c["SC"][6], c["SC"][96]) for c in main_cells]
    rulA = decide_A(cells_stats, M_CELL)
    rulB = decide_B(cells_stats, M_CELL)
    check(rulA[0] == rulB[0], "twin decision evaluators: ruling")
    check(rulA[2] == rulB[1] and rulA[3] == rulB[2] and rulA[4] == rulB[3],
          "twin decision evaluators: counts")
    if rulA[5] is None:
        check(rulB[4] is None, "twin decision evaluators: median None")
    else:
        check(abs(rulA[5] - float(rulB[4])) <= 1e-12,
              "twin decision evaluators: median spread")
    check(rulA[7] == rulB[5], "twin decision evaluators: flip axis")
    ruling, basis, n_det, n_le10, n_ge24, med_spread, axes, flip = rulA

    # ================= STABILITY stream (seed 20260749)
    rng_s = random.Random(SEED_STAB)
    stab_draws = 0
    stab_cells = []
    for ci, (kappa, E, rho) in enumerate(PCELLS):
        cell = run_planted_cell(
            rng_s, M_STAB, kappa, E, rho, False, S_BH, bars[rho], bars7[rho],
            "stab cell %d" % ci, twin_idxs=(0,), want_marg=False)
        stab_draws += cell["draws"]
        detectable, nstar, max_sc = cell_decision_stats(cell)
        cell.update({"kappa": kappa, "E": E, "rho": rho,
                     "detectable": detectable, "nstar": nstar,
                     "max_sc": max_sc})
        stab_cells.append(cell)
    sentinel_check(rng_s, SEED_STAB, stab_draws, "stability stream")
    stab_stats = [(c["kappa"], c["E"], c["rho"], c["detectable"], c["nstar"],
                   c["SC"][6], c["SC"][96]) for c in stab_cells]
    srulA = decide_A(stab_stats, M_STAB)
    srulB = decide_B(stab_stats, M_STAB)
    check(srulA[0] == srulB[0], "stability twin evaluators: ruling")
    check(srulA[0] == ruling,
          "VALIDITY GATE: stability leg (seed %d) reproduces the ruling"
          % SEED_STAB)
    log("[stability] ruling %s reproduces main" % srulA[0])

    # ================= VALIDATION + REPORTING stream (seed 20260750)
    rng_v = random.Random(SEED_VALREP)
    vr_draws = 0
    # ---- independent-leg familywise gate (run invalid on any failure)
    fam_rows = []
    for rho in RHOS:
        mu_d = mu_d_for(rho, S_BH, J_MAIN)
        dpp = draws_per_panel(J_MAIN, False)
        counts = {N: 0 for N in NS}
        for i in range(M_VALID):
            if i == 0:
                pre_state = rng_v.getstate()
            prefs, _ = gen_panel(rng_v, J_MAIN, False, rho, mu_d)
            vr_draws += dpp
            deltas, _ = deltas_from_stats(eval_panel(prefs, J_MAIN), COST)
            if i == 0:
                post_state = rng_v.getstate()
                rng_v.setstate(pre_state)
                prefs_r, _ = gen_panel(rng_v, J_MAIN, False, rho, mu_d)
                deltas_r, _ = deltas_from_stats(
                    eval_panel(prefs_r, J_MAIN), COST)
                check(deltas_r == deltas,
                      "validation rho=%.1f determinism replay" % rho)
                rng_v.setstate(post_state)
                tw, _ = twin_eval(prefs, J_MAIN, COST)
                for cf in range(NCFG):
                    check(abs(tw[cf] - deltas[cf]) <= 1e-9,
                          "validation rho=%.1f twin config %d" % (rho, cf))
            if i < 10:
                check(abs(k9_delta(prefs, J_MAIN)) <= 1e-12,
                      "validation rho=%.1f panel %d k=9" % (rho, i))
            d6, d10, d24, d96 = dmaxes(deltas)
            for N, dN in ((6, d6), (10, d10), (24, d24), (96, d96)):
                if dN >= bars[rho][N]:
                    counts[N] += 1
        for N in NS:
            fam_rows.append({"rho": rho, "N": N, "false_keeps": counts[N],
                             "M": M_VALID, "rate": counts[N] / M_VALID})
        log("[validation rho=%.1f] false keeps per N: %s"
            % (rho, {N: counts[N] for N in NS}))

    # ---- reporting arms (cannot flip the decision)
    report_cells = []
    for arm, rsv, sbh in (("sbh0", False, 0.0), ("rsv", True, S_BH)):
        for rho in (0.0, 0.3):
            cell = run_planted_cell(
                rng_v, M_REPORT, 1.0, 63, rho, rsv, sbh,
                bars[rho], bars7[rho],
                "report %s rho=%.1f" % (arm, rho),
                twin_idxs=(0,), want_marg=False)
            vr_draws += cell["draws"]
            detectable, nstar, max_sc = cell_decision_stats(cell)
            cell.update({"arm": arm, "kappa": 1.0, "E": 63, "rho": rho,
                         "sbh": sbh, "detectable": detectable,
                         "nstar": nstar, "max_sc": max_sc})
            report_cells.append(cell)
            log("[report %s rho=%.1f] Y6=%.3f Y96=%.3f det=%s N*=%s"
                % (arm, rho, cell["SC"][6] / M_REPORT,
                   cell["SC"][96] / M_REPORT, detectable, nstar))
    sentinel_check(rng_v, SEED_VALREP, vr_draws, "validation+reporting stream")

    # ================= AUX stream (seed 20260751) — never read by decisions
    rng_a = random.Random(SEED_AUX)
    aux_draws = 0
    n_g = 50000
    gs = [ICDF(rng_a.random()) for _ in range(n_g)]
    aux_draws += n_g
    gm = sum(gs) / n_g
    gv = sum((x - gm) ** 2 for x in gs) / (n_g - 1)
    check(abs(gm) <= 4.0 / math.sqrt(n_g), "aux alpha-stream mean")
    check(abs(gv - 1.0) <= 4.0 * math.sqrt(2.0 / (n_g - 1)),
          "aux alpha-stream variance")
    for i in range(2):
        mu_d = mu_d_for(0.3, S_BH, J_MAIN)
        prefs, _ = gen_panel(rng_a, J_MAIN, False, 0.3, mu_d, 2.0, 63)
        aux_draws += draws_per_panel(J_MAIN, False, 2.0, 63)
        deltas, _ = deltas_from_stats(eval_panel(prefs, J_MAIN), COST)
        tw, _ = twin_eval(prefs, J_MAIN, COST)
        for cf in range(NCFG):
            check(abs(tw[cf] - deltas[cf]) <= 1e-9,
                  "aux planted twin panel %d config %d" % (i, cf))
    # ---- aux leg C: UNCONDITIONAL fresh kappa=0 null leg, M=2000 per rho —
    # the pinned familywise diagnostic (fixtures gate_calibration_disclosure)
    M_LEGC = 2000
    legc_counts = {}
    for rho in RHOS:
        mu_d = mu_d_for(rho, S_BH, J_MAIN)
        dpp = draws_per_panel(J_MAIN, False)
        counts = {N: 0 for N in NS}
        for i in range(M_LEGC):
            if i == 0:
                pre_state = rng_a.getstate()
            prefs, _ = gen_panel(rng_a, J_MAIN, False, rho, mu_d)
            aux_draws += dpp
            deltas, _ = deltas_from_stats(eval_panel(prefs, J_MAIN), COST)
            if i == 0:
                post_state = rng_a.getstate()
                rng_a.setstate(pre_state)
                prefs_r, _ = gen_panel(rng_a, J_MAIN, False, rho, mu_d)
                deltas_r, _ = deltas_from_stats(
                    eval_panel(prefs_r, J_MAIN), COST)
                check(deltas_r == deltas,
                      "aux legC rho=%.1f determinism replay" % rho)
                rng_a.setstate(post_state)
            d6, d10, d24, d96 = dmaxes(deltas)
            for N, dN in ((6, d6), (10, d10), (24, d24), (96, d96)):
                if dN >= bars[rho][N]:
                    counts[N] += 1
        legc_counts[rho] = counts
        log("[aux legC rho=%.1f] false keeps per N: %s" % (rho, counts))
    sentinel_check(rng_a, SEED_AUX, aux_draws, "aux stream")
    log("[aux] alpha moments + planted twins + leg C pass")

    # ---- INDEPENDENT-LEG FAMILYWISE GATE (run invalid on failure; the
    # pinned leg-C handling protocol from fixtures applies on an M=500
    # breach: re-read at leg C, c in [7, 33] at M=2000 <=> same 3-binomial-SE
    # rule; leg-C pass = recorded sampling-noise deviation, leg-C fail =
    # run invalid)
    n_breach = 0
    for r in fam_rows:
        rho, N, c = r["rho"], r["N"], r["false_keeps"]
        cC = legc_counts[rho][N]
        r["legC_false_keeps"] = cC
        r["legC_M"] = M_LEGC
        r["legC_rate"] = cC / M_LEGC
        if c <= FAMILYWISE_C_MAX:
            r["status"] = "pass"
            check(True, "FAMILYWISE GATE rho=%.1f N=%d: %d/%d (max 11)"
                  % (rho, N, c, M_VALID))
        else:
            n_breach += 1
            r["status"] = "breach_resolved_at_legC"
            check(7 <= cC <= 33,
                  "FAMILYWISE GATE rho=%.1f N=%d BREACH %d/%d — leg C "
                  "re-read %d/%d outside [7, 33]: run invalid"
                  % (rho, N, c, M_VALID, cC, M_LEGC))
    results["familywise_gate"] = {
        "rule": "|rate - 0.01| <= 3*sqrt(0.01*0.99/500) <=> count <= 11 at "
                "M=500; pinned leg-C handling (fixtures "
                "gate_calibration_disclosure): breach re-read at M=2000, "
                "pass iff count in [7, 33]",
        "rows": fam_rows, "n_breach_at_M500": n_breach, "passed": True}

    # ================= MARGINAL-CONFIG PRICE LIST (ships on EVERY outcome)
    marg = {}
    b6_03 = bars[0.3][6]
    for (name, cfg), ci in zip(MARG_CLASSES, MARG_IDX):
        b7 = bars7[0.3][name]
        rows = []
        dys = []
        for cell in main_cells:
            if cell["rho"] != 0.3:
                continue
            truth = cell["truth"]
            kc7 = cell["kc7"][name]
            y7 = sum(kc7[cf] for cf in (IDX6 + [ci])
                     if truth[cf]) / cell["M"]
            y6 = cell["SC"][6] / cell["M"]
            dy = y7 - y6
            dys.append(dy)
            rows.append({"kappa": cell["kappa"], "E": cell["E"],
                         "Y7": y7, "Y6": y6, "dY": dy})
        marg[name] = {"config": "L=%d k=%d %s %s" % cfg,
                      "bar_N7_rho0.3": b7,
                      "bar_increase_vs_G6": b7 - b6_03,
                      "per_cell_dY_rho0.3": rows,
                      "median_dY": median(dys)}

    # ================= assemble results.json
    def cell_json(c, with_theta=True):
        d = {"kappa": c["kappa"], "E": c["E"], "rho": c["rho"], "M": c["M"],
             "SC": {str(N): c["SC"][N] for N in NS},
             "FC": {str(N): c["FC"][N] for N in NS},
             "Y": {str(N): c["SC"][N] / c["M"] for N in NS},
             "F": {str(N): c["FC"][N] / c["M"] for N in NS},
             "n_true_configs": {str(N): sum(1 for cf in IDXN[N]
                                            if c["truth"][cf]) for N in NS},
             "detectable": c["detectable"],
             "nstar": c["nstar"],
             "Y96_minus_Y6": (c["SC"][96] - c["SC"][6]) / c["M"]}
        if with_theta:
            d["theta"] = c["theta"]
            d["theta_se"] = c["se"]
        return d

    results["main_leg"] = {"M": M_CELL,
                           "cells": [cell_json(c) for c in main_cells]}
    results["stability_leg"] = {
        "M": M_STAB, "ruling": srulA[0],
        "n_detectable": srulA[2], "n_nstar_le10": srulA[3],
        "n_nstar_ge24": srulA[4],
        "median_Y96_minus_Y6": srulA[5],
        "cells": [cell_json(c, with_theta=False) for c in stab_cells]}
    results["reporting_legs"] = {
        "note": "registered as unable to flip the decision; evaluated "
                "against the MAIN bars with their own oracle theta",
        "cells": [dict(cell_json(c), arm=c["arm"], sbh=c["sbh"])
                  for c in report_cells]}
    results["marginal_price_list"] = marg
    results["decision"] = {
        "rule": "detectability floor (>=8/27) -> REJECT (N*<=10 in >=80% of "
                "detectable) -> APPROVE (N*>=24 in >=80% AND median "
                "Y(96)-Y(6) >= +0.25) -> NULL",
        "n_detectable": n_det,
        "n_nstar_le10": n_le10,
        "n_nstar_ge24": n_ge24,
        "median_Y96_minus_Y6": med_spread,
        "ruling": ruling,
        "basis": basis,
        "axes": axes,
        "flip_axis": flip}
    results["draws"] = {"main": main_draws, "stability": stab_draws,
                        "validation_reporting": vr_draws, "aux": aux_draws}

    # ================= stdout report (byte-identical across runs)
    print("== verdict-028 — round-3 breadth budget under the q99 bar "
          "(idea-engine PROPOSAL 026) ==")
    print("python: cpython-%d.%d   seeds: main %d / stability %d / "
          "validation+reporting %d / aux %d"
          % (sys.version_info[0], sys.version_info[1], SEED_MAIN, SEED_STAB,
             SEED_VALREP, SEED_AUX))
    print("")
    print("NULL BARS b_N(rho) (q99 of Delta_max(G_N), kappa=0, M=%d per rho, "
          "seed %d) + ANCHOR GATE vs V024 (tol +/-%.2f):" %
          (M_NULL, SEED_MAIN, ANCHOR_TOL))
    for rho in RHOS:
        parts = []
        for N in NS:
            s = "N=%d %.4f" % (N, bars[rho][N])
            if N in ANCHORS[rho]:
                s += " (V024 %.4f, diff %+.4f)" % (
                    ANCHORS[rho][N], bars[rho][N] - ANCHORS[rho][N])
            parts.append(s)
        print("  rho=%.1f : %s" % (rho, " | ".join(parts)))
    print("  ANCHOR GATE: PASS (9/9 within +/-0.05)")
    print("")
    print("MAIN LEG (M=%d per cell, seed %d, post-cost 10 bp; bars from the "
          "in-run null legs):" % (M_CELL, SEED_MAIN))
    print("cell kappa   E rho | Y(6)  Y(10) Y(24) Y(96) | F(96) | "
          "Y96-Y6 | det N*")
    for ci, c in enumerate(main_cells):
        print("%4d  %4.1f %3d %.1f | %.3f %.3f %.3f %.3f | %.3f | %+.3f | "
              "%3s %s"
              % (ci, c["kappa"], c["E"], c["rho"],
                 c["SC"][6] / M_CELL, c["SC"][10] / M_CELL,
                 c["SC"][24] / M_CELL, c["SC"][96] / M_CELL,
                 c["FC"][96] / M_CELL,
                 (c["SC"][96] - c["SC"][6]) / M_CELL,
                 "yes" if c["detectable"] else "no",
                 str(c["nstar"]) if c["detectable"] else "-"))
    print("")
    print("DECISION (pre-registered order: detectability floor -> REJECT -> "
          "APPROVE -> NULL):")
    print("  detectable cells: %d/27 (floor: >= 8)" % n_det)
    print("  N* <= 10: %d/%d detectable (REJECT bar: >= 80%%)"
          % (n_le10, n_det))
    print("  N* >= 24: %d/%d detectable (APPROVE bar: >= 80%%)"
          % (n_ge24, n_det))
    print("  median Y(96)-Y(6) over detectable: %s (APPROVE band: >= +0.25)"
          % ("%.4f" % med_spread if med_spread is not None else "n/a"))
    print("  RULING: %s — %s" % (ruling.upper(), basis))
    print("  per-axis (over detectable cells): share N*<=10 / share N*>=24 / "
          "median Y96-Y6:")
    for ax in ("kappa", "E", "rho"):
        parts = []
        for v, d in axes[ax]["values"].items():
            if d["n_detectable"]:
                parts.append("%s: %d/%d det, %.3f / %.3f / %+.3f"
                             % (v, d["n_detectable"], d["n_cells"],
                                d["share_nstar_le10"], d["share_nstar_ge24"],
                                d["median_Y96_minus_Y6"]))
            else:
                parts.append("%s: 0/%d det" % (v, d["n_cells"]))
        print("    %-5s (spread %.3f): %s"
              % (ax, axes[ax]["spread_share_le10"], " | ".join(parts)))
    print("  flip axis (largest N*<=10 share spread): %s" % ",".join(flip))
    print("")
    print("STABILITY LEG (M=%d, seed %d): ruling %s — reproduces main: %s"
          % (M_STAB, SEED_STAB, srulA[0], srulA[0] == ruling))
    print("  detectable %d, N*<=10 %d, N*>=24 %d, median Y96-Y6 %s"
          % (srulA[2], srulA[3], srulA[4],
             "%.4f" % srulA[5] if srulA[5] is not None else "n/a"))
    print("")
    print("INDEPENDENT-LEG FAMILYWISE GATE (bars from leg A on fresh M=%d "
          "leg B, seed %d; pass iff count <= 11; pinned leg-C handling at "
          "M=%d: breach passes iff leg-C count in [7, 33]):"
          % (M_VALID, SEED_VALREP, M_LEGC))
    for rho in RHOS:
        row = [r for r in fam_rows if r["rho"] == rho]
        print("  rho=%.1f : %s"
              % (rho, " | ".join("N=%d %d/%d (%.3f) legC %d/%d %s"
                                 % (r["N"], r["false_keeps"], r["M"],
                                    r["rate"], r["legC_false_keeps"],
                                    r["legC_M"],
                                    "PASS" if r["status"] == "pass"
                                    else "BREACH->legC-PASS")
                                 for r in row)))
    print("  breaches at M=500: %d/12 (all leg-C resolved)" % n_breach
          if n_breach else "  breaches at M=500: 0/12")
    print("")
    print("ORACLE SIGN GATES: rev<mom strict at E in {63,252} (18/18 PASS), "
          "E=21 matched 4*SE_paired equivalence (9/9 PASS — epoch-rebalance "
          "alignment, see fixtures gate_calibration_disclosure); "
          "kappa-monotonicity 2SE at E in {63,252} + 4SE band at E=21 "
          "(18/18 PASS)")
    print("")
    print("REPORTING ARMS (M=%d each, seed %d, kappa=1.0/E=63; MAIN bars; "
          "cannot flip the decision):" % (M_REPORT, SEED_VALREP))
    for c in report_cells:
        print("  %s S_bh=%.2f rho=%.1f : Y6 %.3f Y10 %.3f Y24 %.3f Y96 %.3f "
              "det %s N* %s"
              % (c["arm"], c["sbh"], c["rho"],
                 c["SC"][6] / M_REPORT, c["SC"][10] / M_REPORT,
                 c["SC"][24] / M_REPORT, c["SC"][96] / M_REPORT,
                 "yes" if c["detectable"] else "no",
                 str(c["nstar"]) if c["detectable"] else "-"))
    print("")
    print("MARGINAL-CONFIG PRICE LIST (from G6, bar recomputed at N=7 on the "
          "rho=0.3 null leg; dY on the 9 rho=0.3 planted cells; ships on "
          "EVERY outcome):")
    for name, _ in MARG_CLASSES:
        m = marg[name]
        print("  %-26s (%s): bar %.4f (+%.4f vs G6) | median dY %+.4f | "
              "per-cell dY %s"
              % (name, m["config"], m["bar_N7_rho0.3"],
                 m["bar_increase_vs_G6"], m["median_dY"],
                 " ".join("%+.3f" % r["dY"] for r in m["per_cell_dY_rho0.3"])))
    print("")
    results["self_checks"] = N_CHECKS + 1   # + the final json-write check
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, sort_keys=True)
        f.write("\n")
    check(True, "results.json written")
    print("SELF-CHECKS: %d passed, 0 failed" % N_CHECKS)


if __name__ == "__main__":
    main()
