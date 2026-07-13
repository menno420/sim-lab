#!/usr/bin/env python3
"""verdict-024 — xsec KEEP margins vs selection noise (idea-engine PROPOSAL 022).

Fully hermetic NUMERIC SIMULATION (rung 1): the null distribution of the
trading lane's promote-on statistic — max over a nested config grid of
(strategy Sharpe − basket Sharpe) — on momentum-free synthetic panels matched
to the lane's protocol shape. ZERO real market bars; no dev-candidate is
evaluated on any data; the owner-gated post-2026 protocol is untouched.

Reads exactly ONE file: its own committed fixtures.json (the
pre-registration), cross-checked against in-code literals at start. No
network, no git, no wall clock. stdout and results.json are byte-identical
across process runs (verified by external diff). Progress/partial results go
to stderr only (excluded from the byte-diff by construction).

Run: python3 sims/verdict-024-keep-margins-noise/xsec_selection_noise_sim.py
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
J_MAIN = 9
T = 2595
PB = 21                      # bars per period (the lane's frozen interval)
NP = 123                     # full periods (123*21 = 2583 <= 2595; final 12 bars unused)
WARM = 12                    # warm-up periods (252 bars = max lookback)
EVAL_P0 = 12                 # first evaluation period
NEVAL = 111                  # evaluation periods 12..122
SIGMA_ANN = 0.30
SIGMA_D = SIGMA_ANN / math.sqrt(252.0)
COST = 0.001                 # 10 bp per side; charge COST*2*replaced/k per rebalance
P_CC, P_SS = 0.98, 0.94
VAR_CALM, VAR_STRESS = 0.6, 2.2
M_CALM, M_STRESS = math.sqrt(VAR_CALM), math.sqrt(VAR_STRESS)
PI_CALM = 0.75
RHOS = (0.0, 0.3, 0.6)
SBHS = (0.0, 1.15)
VOLS = ("IID", "RSV")
L_ALL = (21, 42, 63, 84, 105, 126, 189, 252)
K_ALL = (2, 3, 4)
MARGIN_BEST = 0.484
MARGIN_WEAK = 0.130
M_MAIN = 1000
M_STAB = 250
M_REPORT = 250
SEED_MAIN = 20260727
SEED_STAB = 20260728
SEED_REPORT = 20260729
SQRT12 = math.sqrt(12.0)
ICDF = NormalDist().inv_cdf   # exactly ONE uniform per normal (disclosure 1);
                              # a drawn 0.0 raises StatisticsError = run invalid.

# Config grid, pinned order: L asc, k asc, direction mom<rev, weighting eq<rl.
CONFIGS = [(L, k, d, w) for L in L_ALL for k in K_ALL
           for d in ("mom", "rev") for w in ("eq", "rl")]
NCFG = len(CONFIGS)
G6_SET = {(L, k, "mom", "eq") for L in (63, 126, 252) for k in (2, 3)}
G24_SET = {(L, k, d, "eq") for L in (21, 42, 63, 84, 126, 252)
           for k in (2, 3) for d in ("mom", "rev")}
G1_CFG = (63, 2, "mom", "eq")
IDX_G1 = CONFIGS.index(G1_CFG)
MASK6 = [c in G6_SET for c in CONFIGS]
MASK24 = [c in G24_SET for c in CONFIGS]
IDX6 = [i for i, m in enumerate(MASK6) if m]
IDX24 = [i for i, m in enumerate(MASK24) if m]

# 12 decision cells, pinned lexicographic order.
CELLS = [(v, r, s) for v in VOLS for r in RHOS for s in SBHS]

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


# ------------------------------------------------------------ panel machinery
def gen_panel(rng, J, rsv, rho, mu_d):
    """Pinned draw order: regime chain (RSV only: 1 stationary + T-1
    transitions), then f_t (t asc), then z_{j,t} (j outer, t inner).
    Returns (prefs, chain_stats): prefs[j] = prefix sums of r[j] (len T+1);
    chain_stats = (n_stress, n_cc, n_cs, n_sc, n_ss) or None for IID."""
    rr = rng.random
    sr = math.sqrt(rho)
    s1r = math.sqrt(1.0 - rho)
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
        for _ in range(J):
            s = 0.0
            row = [0.0] * (T + 1)
            for t in range(T):
                s += c[t] + b[t] * ICDF(rr())
                row[t + 1] = s
            prefs.append(row)
    else:
        asd = SIGMA_D * sr
        bsd = SIGMA_D * s1r
        c = [mu_d + asd * ICDF(rr()) for _ in range(T)]
        prefs = []
        for _ in range(J):
            s = 0.0
            row = [0.0] * (T + 1)
            for t in range(T):
                s += c[t] + bsd * ICDF(rr())
                row[t + 1] = s
            prefs.append(row)
    return prefs, chain_stats


def draws_per_panel(J, rsv):
    return (J + 1) * T + (T if rsv else 0)


def eval_panel(prefs, J):
    """The main strategy evaluator (prefix sums, incremental top-k cumsums).
    Returns (Spre, Spre2, Su, Su2, Spu, Sb, Sb2): per-config accumulators over
    the 111 evaluation periods of pre-cost period return x, turnover u =
    2*replaced/k (u=0 at the entry rebalance p=12), and the basket sums."""
    rj = range(J)
    # per-instrument per-period returns R[p][j]
    R = [[prefs[j][PB * (p + 1)] - prefs[j][PB * p] for j in rj]
         for p in range(NP)]
    Spre = [0.0] * NCFG
    Spre2 = [0.0] * NCFG
    Su = [0.0] * NCFG
    Su2 = [0.0] * NCFG
    Spu = [0.0] * NCFG
    Sb = 0.0
    Sb2 = 0.0
    prev = [None] * (len(L_ALL) * 2 * 3)   # per (L, dir, k) holding set
    for p in range(EVAL_P0, NP):
        Rp = R[p]
        bas = sum(Rp) / J
        Sb += bas
        Sb2 += bas * bas
        t = PB * p
        for Li, L in enumerate(L_ALL):
            tl = t - L
            vals = [prefs[j][t] - prefs[j][tl] for j in rj]
            asc = sorted((vals[j], j) for j in rj)      # reversal order (ties by j)
            desc = sorted((-vals[j], j) for j in rj)    # momentum order (ties by j)
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
                    u = float(repl)                     # 2*replaced/2
                    if repl:
                        prev[slot] = {j0, j1}
                x = c2 * 0.5
                i = base                                 # (L, 2, dir, eq)
                Spre[i] += x
                Spre2[i] += x * x
                Su[i] += u
                Su2[i] += u * u
                Spu[i] += x * u
                x = (r0 + c2) / 3.0                      # rank-linear (2/3, 1/3)
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
                i = base + 4                             # (L, 3, dir, eq)
                Spre[i] += x
                Spre2[i] += x * x
                Su[i] += u
                Su2[i] += u * u
                Spu[i] += x * u
                x = (r0 + c2 + c3) / 6.0                 # rank-linear (3,2,1)/6
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
                i = base + 8                             # (L, 4, dir, eq)
                Spre[i] += x
                Spre2[i] += x * x
                Su[i] += u
                Su2[i] += u * u
                Spu[i] += x * u
                x = (r0 + c2 + c3 + c4) * 0.1            # rank-linear (4,3,2,1)/10
                i += 1
                Spre[i] += x
                Spre2[i] += x * x
                Su[i] += u
                Su2[i] += u * u
                Spu[i] += x * u
    return Spre, Spre2, Su, Su2, Spu, Sb, Sb2


def deltas_from_stats(stats, rate):
    """Post-cost Delta per config at the given per-side cost rate."""
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
    d96 = max(deltas)
    d24 = max(deltas[i] for i in IDX24)
    d6 = max(deltas[i] for i in IDX6)
    d1 = deltas[IDX_G1]
    return d1, d6, d24, d96


# ------------------------------------------------------- independent twin
def twin_eval(prefs, J, rate):
    """Independently written evaluator: direct bar sums (no prefix reuse in
    the aggregation), its own sorts, explicit weight vectors, explicit
    turnover sets, statistics-module mean/stdev. Tests the STRATEGY layer;
    the generator is covered by the determinism replay + analytic gates."""
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
    """Gate (a): the k=J control config through real-machinery-style steps —
    momentum L=63, hold ALL J names equal-weight; zero turnover after free
    entry; must equal the zero-cost basket to 1e-12."""
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
    """Left-continuous empirical quantile (disclosure 5)."""
    return sorted_vals[math.ceil(q * len(sorted_vals)) - 1]


# --------------------------------------------------------------- leg driver
def run_leg(seed, M, cells, J, leg_name, gates_main=False,
            twin_idxs=(0,), rates=(COST,), k9_gate=True):
    """Runs one leg. Returns (per-cell results dict list, total_draws, rng).
    rates: extra cost rates evaluated (first must be the pinned 0.001 for
    decision numbers; others are reporting-only)."""
    rng = random.Random(seed)
    total_draws = 0
    out = []
    for ci, (vol, rho, sbh) in enumerate(cells):
        rsv = (vol == "RSV")
        mu_d = mu_d_for(rho, sbh, J)
        dpp = draws_per_panel(J, rsv)
        lists = {rate: {1: [], 6: [], 24: [], 96: []} for rate in rates}
        counts = {rate: [0, 0] for rate in rates}   # [count_484, count_130]
        gb_sum = [0.0] * NCFG   # gate (b) per-panel mean diffs
        gb_sum2 = [0.0] * NCFG
        gc_pre = [0.0] * NCFG   # gate (c) pooled pre-cost sums
        gc_pre2 = [0.0] * NCFG
        gc_b = 0.0
        gc_b2 = 0.0
        chain_tot = [0, 0, 0, 0, 0]
        shb_sum = 0.0
        for i in range(M):
            if i == 0:
                pre_state = rng.getstate()
            prefs, cs = gen_panel(rng, J, rsv, rho, mu_d)
            total_draws += dpp
            stats = eval_panel(prefs, J)
            deltas, shb = deltas_from_stats(stats, rates[0])
            if i == 0:
                # determinism replay: regenerate from the captured state
                post_state = rng.getstate()
                rng.setstate(pre_state)
                prefs_r, _ = gen_panel(rng, J, rsv, rho, mu_d)
                deltas_r, _ = deltas_from_stats(eval_panel(prefs_r, J), rates[0])
                check(deltas_r == deltas,
                      "%s cell %d determinism replay" % (leg_name, ci))
                rng.setstate(post_state)
            if cs is not None:
                for q in range(5):
                    chain_tot[q] += cs[q]
            if k9_gate and i < 10:
                check(abs(k9_delta(prefs, J)) <= 1e-12,
                      "%s cell %d panel %d gate(a) k=%d identity"
                      % (leg_name, ci, i, J))
            if i in twin_idxs:
                tw, tw_shb = twin_eval(prefs, J, rates[0])
                for cf in range(NCFG):
                    check(abs(tw[cf] - deltas[cf]) <= 1e-9,
                          "%s cell %d panel %d twin config %d" % (leg_name, ci, i, cf))
                td = dmaxes(tw)
                md = dmaxes(deltas)
                for a, b in zip(td, md):
                    check(abs(a - b) <= 1e-9, "%s twin dmax" % leg_name)
                check((td[1] >= MARGIN_BEST) == (md[1] >= MARGIN_BEST) and
                      (td[1] >= MARGIN_WEAK) == (md[1] >= MARGIN_WEAK),
                      "%s twin threshold indicators" % leg_name)
            shb_sum += shb
            check(all(map(math.isfinite, deltas)),
                  "%s cell %d panel %d finite deltas" % (leg_name, ci, i))
            for rate in rates:
                if rate == rates[0]:
                    dd = deltas
                else:
                    dd, _ = deltas_from_stats(stats, rate)
                d1, d6, d24, d96 = dmaxes(dd)
                if rate == rates[0]:
                    check(d1 <= d6, "%s mono d1<=d6" % leg_name)
                    check(d6 <= d24, "%s mono d6<=d24" % leg_name)
                    check(d24 <= d96, "%s mono d24<=d96" % leg_name)
                lists[rate][1].append(d1)
                lists[rate][6].append(d6)
                lists[rate][24].append(d24)
                lists[rate][96].append(d96)
                if d6 >= MARGIN_BEST:
                    counts[rate][0] += 1
                if d6 >= MARGIN_WEAK:
                    counts[rate][1] += 1
            if gates_main:
                n = float(NEVAL)
                mb = stats[5] / n
                for cf in range(NCFG):
                    d = stats[0][cf] / n - mb
                    gb_sum[cf] += d
                    gb_sum2[cf] += d * d
                    gc_pre[cf] += stats[0][cf]
                    gc_pre2[cf] += stats[1][cf]
                gc_b += stats[5]
                gc_b2 += stats[6]
        # ---- per-cell gates (main leg only)
        if gates_main and sbh == 0.0:
            for cf in range(NCFG):
                m_ = gb_sum[cf] / M
                sd = math.sqrt((gb_sum2[cf] - M * m_ * m_) / (M - 1))
                check(abs(m_) <= 4.0 * sd / math.sqrt(M),
                      "gate(b) exchangeability cell %d config %d" % (ci, cf))
        if gates_main and vol == "IID" and rho == 0.0 and sbh == 0.0:
            n_pool = float(M * NEVAL)
            mb = gc_b / n_pool
            sdb = math.sqrt((gc_b2 - n_pool * mb * mb) / (n_pool - 1.0))
            for cf, (L, k, dirn, wt) in enumerate(CONFIGS):
                m_ = gc_pre[cf] / n_pool
                sd = math.sqrt((gc_pre2[cf] - n_pool * m_ * m_) / (n_pool - 1.0))
                ratio = sd / sdb
                if wt == "eq":
                    target = math.sqrt(9.0 / k)
                    check(abs(ratio / target - 1.0) <= 0.02,
                          "gate(c) vol-ratio config %d (eq k=%d)" % (cf, k))
                else:
                    tot = k * (k + 1) / 2
                    sw2 = sum(((k + 1 - i) / tot) ** 2 for i in range(1, k + 1))
                    target = math.sqrt(9.0 * sw2)
                    check(abs(ratio / target - 1.0) <= 0.02,
                          "aux vol-ratio config %d (rl k=%d)" % (cf, k))
        if rsv and cells is CELLS:
            n_bars = M * T
            n_stress, ncc, ncs, nsc, nss = chain_tot
            phi = P_CC + P_SS - 1.0
            se = math.sqrt(0.25 * 0.75 / n_bars * (1.0 + phi) / (1.0 - phi))
            check(abs(n_stress / n_bars - 0.25) <= 4.0 * se,
                  "aux RSV stress share cell %d" % ci)
            nc = ncc + ncs
            check(abs(ncc / nc - P_CC) <= 4.0 * math.sqrt(P_CC * (1 - P_CC) / nc),
                  "aux RSV p_cc cell %d" % ci)
            ns_ = nss + nsc
            check(abs(nss / ns_ - P_SS) <= 4.0 * math.sqrt(P_SS * (1 - P_SS) / ns_),
                  "aux RSV p_ss cell %d" % ci)
        cell_res = {
            "vol": vol, "rho": rho, "sbh": sbh, "M": M,
            "mean_basket_sharpe": shb_sum / M,
            "rates": {},
        }
        for rate in rates:
            srt = {N: sorted(v) for N, v in lists[rate].items()}
            cell_res["rates"]["%.4f" % rate] = {
                "count_484": counts[rate][0],
                "count_130": counts[rate][1],
                "P_484": counts[rate][0] / M,
                "P_130": counts[rate][1] / M,
                "q": {str(N): {"q50": quant(srt[N], 0.50),
                               "q90": quant(srt[N], 0.90),
                               "q99": quant(srt[N], 0.99)}
                      for N in (1, 6, 24, 96)},
            }
        out.append(cell_res)
        log("[%s] cell %d/%d %s rho=%.1f sbh=%.2f done: count484=%d/%d "
            "count130=%d/%d q99(G6)=%.4f  (partial-results checkpoint)"
            % (leg_name, ci + 1, len(cells), vol, rho, sbh,
               counts[rates[0]][0], M, counts[rates[0]][1], M,
               cell_res["rates"]["%.4f" % rates[0]]["q"]["6"]["q99"]))
    return out, total_draws, rng


def sentinel_check(rng, seed, total_draws, leg_name):
    live_next = rng.random()
    fresh = random.Random(seed)
    fr = fresh.random
    for _ in range(total_draws):
        fr()
    check(fr() == live_next,
          "%s draw-count sentinel (%d draws)" % (leg_name, total_draws))


# --------------------------------------------------------- decision (twins)
def decide_A(counts, M):
    n_rej = sum(1 for c in counts if 10 * c >= M)
    if n_rej >= 6:
        ruling = "reject"
    elif all(100 * c <= M for c in counts):
        ruling = "approve"
    else:
        ruling = "null"
    axes = {}
    for name, sel in (("vol", lambda i: VOLS[0] if i < 6 else VOLS[1]),
                      ("rho", lambda i: RHOS[(i % 6) // 2]),
                      ("sbh", lambda i: SBHS[i % 2])):
        vals = {}
        keys = VOLS if name == "vol" else (RHOS if name == "rho" else SBHS)
        for v in keys:
            idxs = [i for i in range(12) if sel(i) == v]
            passes = sum(1 for i in idxs if 100 * counts[i] <= M)
            vals[str(v)] = {"approve_pass_share": passes / len(idxs),
                            "median_P": median(counts[i] / M for i in idxs)}
        shares = [vals[str(v)]["approve_pass_share"] for v in keys]
        axes[name] = {"values": vals, "spread": max(shares) - min(shares)}
    max_spread = max(a["spread"] for a in axes.values())
    flip = [n for n, a in axes.items() if a["spread"] == max_spread]
    return ruling, n_rej, axes, flip


def decide_B(counts, M):
    Ps = [Fraction(c, M) for c in counts]
    hot = [P >= Fraction(1, 10) for P in Ps]
    if sum(hot) >= 6:
        ruling = "reject"
    elif max(Ps) <= Fraction(1, 100):
        ruling = "approve"
    else:
        ruling = "null"
    meta = CELLS
    axes = {}
    for pos, name, keys in ((0, "vol", VOLS), (1, "rho", RHOS), (2, "sbh", SBHS)):
        vals = {}
        for v in keys:
            ps = [Ps[i] for i in range(12) if meta[i][pos] == v]
            share = Fraction(sum(1 for p in ps if p <= Fraction(1, 100)), len(ps))
            vals[str(v)] = {"approve_pass_share": float(share),
                            "median_P": float(median(ps))}
        shares = [Fraction(vals[str(v)]["approve_pass_share"]) for v in keys]
        axes[name] = {"values": vals, "spread": float(max(shares) - min(shares))}
    max_spread = max(a["spread"] for a in axes.values())
    flip = [n for n, a in axes.items() if a["spread"] == max_spread]
    return ruling, sum(hot), axes, flip


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
    """Exact-Fraction sample mean/std of a value multiset -> float Sharpe."""
    n = sum(c for _, c in pairs)
    mean = sum(Fraction(v) * c for v, c in pairs) / n
    var = sum((Fraction(v) - mean) ** 2 * c for v, c in pairs) / (n - 1)
    return float(mean) / math.sqrt(float(var)) * SQRT12


def run_pins():
    # ---- PIN1
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
    d1, d6, d24, d96 = dmaxes(deltas)
    check(abs(d1 - exp_eq) <= 1e-9 and abs(d6 - exp_eq) <= 1e-9,
          "PIN1 dmax(G1)=dmax(G6)")
    check(abs(d96 - exp_rl) <= 1e-9, "PIN1 dmax(G96) = k2 mom rank-linear")
    # ---- PIN2
    prefs = build_pin2()
    stats = eval_panel(prefs, J_MAIN)
    deltas, _ = deltas_from_stats(stats, COST)
    icfg = CONFIGS.index((21, 2, "mom", "eq"))
    # replaced == 1 at every rebalance p=13..122 -> u = 1.0 each, 110 periods
    check(stats[2][icfg] == 110.0, "PIN2 turnover sum == 110 (replaced=1 x 110)")
    check(stats[3][icfg] == 110.0, "PIN2 turnover sumsq == 110")
    # total cost charged = 110 * 0.001 exactly (u-sum * rate)
    check(abs(COST * stats[2][icfg] - 0.110) <= 1e-15, "PIN2 total cost 0.110")
    sh_strat = sharpe_of_multiset([
        (Fraction(-5, 10000), 1),      # -0.0005 x 1
        (Fraction(-215, 10000), 55),   # -0.0215 x 55
        (Fraction(-15, 10000), 55),    # -0.0015 x 55
    ])
    sh_bask = sharpe_of_multiset([
        (Fraction(1, 100), 56), (Fraction(-1, 100), 55)])
    check(abs(deltas[icfg] - (sh_strat - sh_bask)) <= 1e-9,
          "PIN2 Delta (21,2,mom,eq) vs exact multiset Sharpe")
    log("[pins] PIN1 + PIN2 pass")


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
    check(c["rsv"]["p_cc"] == P_CC and c["rsv"]["p_ss"] == P_SS and
          tuple(c["rsv"]["variance_multipliers"]) == (VAR_CALM, VAR_STRESS),
          "fixtures RSV constants")
    check(tuple(c["rho_grid"]) == RHOS and tuple(c["sbh_grid"]) == SBHS,
          "fixtures rho/sbh grids")
    check(c["tested_margins"]["best_keep"] == MARGIN_BEST and
          c["tested_margins"]["weakest_keep"] == MARGIN_WEAK,
          "fixtures tested margins")
    check(c["M_main"] == M_MAIN and c["M_stability"] == M_STAB and
          c["seed_main"] == SEED_MAIN and c["seed_stability"] == SEED_STAB and
          c["seed_reporting"] == SEED_REPORT, "fixtures M/seeds")
    # RSV normalization + stationary pi EXACT (gate d)
    check(Fraction(3, 4) * Fraction(3, 5) + Fraction(1, 4) * Fraction(11, 5)
          == 1, "gate(d) RSV unconditional unit variance exact")
    check(Fraction(2, 100) / (Fraction(2, 100) + Fraction(6, 100))
          == Fraction(1, 4), "gate(d) stationary pi = (3/4, 1/4) exact")
    # grid construction + nesting
    check(NCFG == 96 and len(IDX24) == 24 and len(IDX6) == 6,
          "grid sizes 96/24/6")
    check(G1_CFG in G6_SET and G6_SET <= G24_SET and
          G24_SET <= set(CONFIGS), "grid nesting G1<G6<G24<G96")
    # mu_d formula recomputation on the matched leg
    got = mu_d_for(0.3, 1.15, 9)
    want = 1.15 * (0.30 / math.sqrt(252.0)) * math.sqrt(0.3 + 0.7 / 9.0) \
        / math.sqrt(252.0)
    check(got == want, "mu_d formula recomputation")
    return fx


# ------------------------------------------------------------------ main
def main():
    check(sys.version_info[:2] == (3, 11),
          "CPython minor pinned: need 3.11, got %d.%d" % sys.version_info[:2])
    fixture_crosscheck()
    run_pins()

    results = {"python": "cpython-%d.%d" % sys.version_info[:2],
               "seeds": {"main": SEED_MAIN, "stability": SEED_STAB,
                         "reporting": SEED_REPORT},
               "configs": ["L=%d k=%d %s %s" % c for c in CONFIGS]}

    # ---------------- MAIN leg
    log("[main] starting M=%d x 12 cells, seed %d" % (M_MAIN, SEED_MAIN))
    main_cells, main_draws, rng = run_leg(
        SEED_MAIN, M_MAIN, CELLS, J_MAIN, "main", gates_main=True,
        twin_idxs=(0, 250, 500, 750))
    exp = M_MAIN * sum(draws_per_panel(J_MAIN, v == "RSV") for v, _, _ in CELLS)
    check(main_draws == exp, "main analytic draw count")
    sentinel_check(rng, SEED_MAIN, main_draws, "main")
    counts_main = [c["rates"]["%.4f" % COST]["count_484"] for c in main_cells]
    rulA = decide_A(counts_main, M_MAIN)
    rulB = decide_B(counts_main, M_MAIN)
    check(rulA[0] == rulB[0], "twin decision evaluators: ruling")
    check(rulA[1] == rulB[1], "twin decision evaluators: hot-cell count")
    check(rulA[3] == rulB[3], "twin decision evaluators: flip axis")
    for ax in ("vol", "rho", "sbh"):
        for v in rulA[2][ax]["values"]:
            a = rulA[2][ax]["values"][v]
            b = rulB[2][ax]["values"][v]
            check(abs(a["approve_pass_share"] - b["approve_pass_share"]) == 0.0
                  and abs(a["median_P"] - b["median_P"]) <= 1e-15,
                  "twin evaluators axis %s=%s" % (ax, v))
    ruling, n_hot, axes, flip = rulA

    # ---------------- STABILITY leg
    log("[stability] starting M=%d x 12 cells, seed %d" % (M_STAB, SEED_STAB))
    stab_cells, stab_draws, rng_s = run_leg(
        SEED_STAB, M_STAB, CELLS, J_MAIN, "stability", gates_main=False,
        twin_idxs=(0,))
    exp = M_STAB * sum(draws_per_panel(J_MAIN, v == "RSV") for v, _, _ in CELLS)
    check(stab_draws == exp, "stability analytic draw count")
    sentinel_check(rng_s, SEED_STAB, stab_draws, "stability")
    counts_stab = [c["rates"]["%.4f" % COST]["count_484"] for c in stab_cells]
    srulA = decide_A(counts_stab, M_STAB)
    srulB = decide_B(counts_stab, M_STAB)
    check(srulA[0] == srulB[0], "stability twin evaluators: ruling")
    check(srulA[0] == ruling,
          "VALIDITY GATE: stability leg (seed %d) reproduces the ruling"
          % SEED_STAB)

    # ---------------- REPORTING legs (seed 20260729 each; cannot flip)
    log("[report-J18] starting M=%d, seed %d" % (M_REPORT, SEED_REPORT))
    j18_cells, j18_draws, rng_j = run_leg(
        SEED_REPORT, M_REPORT, [("IID", 0.3, 1.15)], 18, "report-J18",
        gates_main=False, twin_idxs=(0,), k9_gate=False)
    check(j18_draws == M_REPORT * draws_per_panel(18, False),
          "J18 analytic draw count")
    sentinel_check(rng_j, SEED_REPORT, j18_draws, "report-J18")

    log("[report-cost] starting M=%d, seed %d" % (M_REPORT, SEED_REPORT))
    cost_cells, cost_draws, rng_c = run_leg(
        SEED_REPORT, M_REPORT, [("IID", 0.3, 1.15)], J_MAIN, "report-cost",
        gates_main=False, twin_idxs=(0,),
        rates=(COST, 0.0, 0.0025, 0.002))
    check(cost_draws == M_REPORT * draws_per_panel(J_MAIN, False),
          "cost-leg analytic draw count")
    sentinel_check(rng_c, SEED_REPORT, cost_draws, "report-cost")

    # sigma-scaling identity (disclosure 9): sigma 0.15 @ 10bp == sigma 0.30
    # @ 20bp, verified explicitly on the first 5 reporting panels.
    rng_v = random.Random(SEED_REPORT)
    mu_d = mu_d_for(0.3, 1.15, J_MAIN)
    for i in range(5):
        prefs, _ = gen_panel(rng_v, J_MAIN, False, 0.3, mu_d)
        d_scaled, _ = deltas_from_stats(
            eval_panel([[v * 0.5 for v in row] for row in prefs], J_MAIN), COST)
        d_rate2, _ = deltas_from_stats(eval_panel(prefs, J_MAIN), 0.002)
        for cf in range(NCFG):
            check(abs(d_scaled[cf] - d_rate2[cf]) <= 1e-12,
                  "sigma-scaling identity panel %d config %d" % (i, cf))

    # ---------------- assemble results
    results["main_leg"] = {"M": M_MAIN, "cells": main_cells,
                           "counts_484": counts_main}
    results["stability_leg"] = {"M": M_STAB, "cells": stab_cells,
                                "counts_484": counts_stab,
                                "ruling": srulA[0]}
    results["reporting_legs"] = {
        "J18": {"M": M_REPORT, "cells": j18_cells},
        "cost_sigma": {"M": M_REPORT, "cells": cost_cells,
                       "note": "rate 0.0020 row == sigma_ann 0.15 @ 10 bp by "
                               "the exact scaling identity (disclosure 9)"}}
    key = "%.4f" % COST
    burden = {}
    for N in (1, 6, 24, 96):
        burden[str(N)] = {
            "max_q90_over_cells": max(c["rates"][key]["q"][str(N)]["q90"]
                                      for c in main_cells),
            "max_q99_over_cells": max(c["rates"][key]["q"][str(N)]["q99"]
                                      for c in main_cells)}
    results["burden_bar"] = burden
    results["decision"] = {
        "rule": "REJECT iff P>=0.10 in >=6/12 cells (checked FIRST); "
                "APPROVE iff P<=0.01 in ALL 12; else NULL",
        "statistic": "P(Delta_max(G6) >= 0.484), main leg, post-cost 10 bp",
        "cells_P_ge_0.10": n_hot,
        "ruling": ruling,
        "axes": axes,
        "flip_axis": flip}
    results["draws"] = {"main": main_draws, "stability": stab_draws,
                        "J18": j18_draws, "cost_sigma": cost_draws}

    # ---------------- stdout report (byte-identical across runs)
    print("== verdict-024 — xsec KEEP margins vs selection noise "
          "(idea-engine PROPOSAL 022) ==")
    print("python: cpython-%d.%d   seeds: main %d / stability %d / reporting %d"
          % (sys.version_info[0], sys.version_info[1],
             SEED_MAIN, SEED_STAB, SEED_REPORT))
    print("")
    print("MAIN LEG (M=%d per cell, seed %d, post-cost 10 bp)" % (M_MAIN, SEED_MAIN))
    hdr = ("cell vol rho  sbh  | P(dmax6>=.484) P(>=.130) | " +
           " ".join("q50/q90/q99(N=%d)" % N for N in (1, 6, 24, 96)))
    print(hdr)
    for i, c in enumerate(main_cells):
        r = c["rates"][key]
        qs = "  ".join("%.3f/%.3f/%.3f" % (r["q"][str(N)]["q50"],
                                           r["q"][str(N)]["q90"],
                                           r["q"][str(N)]["q99"])
                       for N in (1, 6, 24, 96))
        print("%4d %-3s %.1f %5.2f |     %6.3f     %6.3f   | %s"
              % (i, c["vol"], c["rho"], c["sbh"], r["P_484"], r["P_130"], qs))
    print("")
    print("BURDEN BAR (max over the 12 cells — the conservative round-3 "
          "shortlist bar per N):")
    for N in (1, 6, 24, 96):
        print("  N=%3d : q90 %.4f   q99 %.4f"
              % (N, burden[str(N)]["max_q90_over_cells"],
                 burden[str(N)]["max_q99_over_cells"]))
    print("")
    print("DECISION (pre-registered order REJECT -> APPROVE -> NULL):")
    print("  cells with P >= 0.10: %d/12 (REJECT bar: >= 6)" % n_hot)
    print("  cells with P <= 0.01: %d/12 (APPROVE bar: 12)"
          % sum(1 for c in counts_main if 100 * c <= M_MAIN))
    print("  RULING: %s" % ruling.upper())
    print("  per-axis approve-pass shares / median P:")
    for ax in ("vol", "rho", "sbh"):
        parts = []
        for v, d in axes[ax]["values"].items():
            parts.append("%s: share %.3f medP %.3f"
                         % (v, d["approve_pass_share"], d["median_P"]))
        print("    %-3s (spread %.3f): %s" % (ax, axes[ax]["spread"],
                                              " | ".join(parts)))
    print("  flip axis (largest spread): %s" % ",".join(flip))
    print("")
    print("STABILITY LEG (M=%d, seed %d): ruling %s — reproduces main: %s"
          % (M_STAB, SEED_STAB, srulA[0], srulA[0] == ruling))
    print("  per-cell count_484/%d: %s" % (M_STAB, counts_stab))
    print("")
    print("REPORTING LEGS (seed %d, M=%d, IID/rho=0.3/S_bh=1.15 only; "
          "cannot flip the decision):" % (SEED_REPORT, M_REPORT))
    jr = j18_cells[0]["rates"][key]
    mr = main_cells[CELLS.index(("IID", 0.3, 1.15))]["rates"][key]
    print("  J=18: P484 %.3f P130 %.3f q99(G6) %.4f  (J=9 main-cell q99(G6) "
          "%.4f -> shift %+.4f)"
          % (jr["P_484"], jr["P_130"], jr["q"]["6"]["q99"],
             mr["q"]["6"]["q99"], jr["q"]["6"]["q99"] - mr["q"]["6"]["q99"]))
    for rate, label in ((0.0, "c=0bp     "), (COST, "c=10bp    "),
                        (0.0025, "c=25bp    "), (0.002, "sigma=0.15")):
        rr_ = cost_cells[0]["rates"]["%.4f" % rate]
        print("  %s: P484 %.3f P130 %.3f q99(G6) %.4f"
              % (label, rr_["P_484"], rr_["P_130"], rr_["q"]["6"]["q99"]))
    print("")
    results["self_checks"] = N_CHECKS + 1   # + the final json-write check
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1, sort_keys=True)
        f.write("\n")
    check(True, "results.json written")
    print("SELF-CHECKS: %d passed, 0 failed" % N_CHECKS)


if __name__ == "__main__":
    main()
