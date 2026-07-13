#!/usr/bin/env python3
"""VERDICT 053 — channel concentration vs diversification at fixed build budget.

Serves idea-engine PROPOSAL 042 (control/outbox.md @ 94fd30c, PR #333; idea doc
ideas/venture-lab/channel-concentration-vs-diversification-2026-07-13.md @ 8aad290).

Arm A (DECISION arm): seedless exact fractions.Fraction enumeration.
Arm S (confirmation arm): seeded Monte Carlo, seeds 20261305 (main) /
20261306 (stability) / 20261307 (reporting) / 20261308 (aux, NEVER read).

Hermetic: reads only its own fixtures.json. Stdlib only. Deterministic:
stdout + results.json byte-identical across process runs (no wall-clock
anywhere). Decision rule pre-registered, evaluated in order, REJECT FIRST.

MC note (disclosed): outcome/rate draws compare random.random() floats against
float(p) thresholds — a <= 2^-53 threshold rounding (~1e-16), negligible against
the 5/1000 agreement gate; Arm A is exact rationals and alone decision-bearing.
"""
import itertools
import json
import os
import platform
import random
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = json.load(open(os.path.join(HERE, "fixtures.json")))

# ---------------------------------------------------------------- self-checks
_PASS = [0]


def gate(cond, label):
    if not cond:
        print("GATE FAIL: %s" % label)
        print("SELF-CHECKS: %d passed, 1 failed" % _PASS[0])
        sys.exit(1)
    _PASS[0] += 1


ANOMALIES = []


def anomaly(line):
    ANOMALIES.append(line)
    print("!! FIRST-CLASS ANOMALY: %s" % line)


# ---------------------------------------------------------------- constants
gate(".".join(platform.python_version_tuple()[:2]) == FIX["cpython_minor"],
     "CPython minor pinned %s" % FIX["cpython_minor"])

RATES = [F(x) for x in FIX["rate_grid"]]
NR = len(RATES)
PRIORS = {k: [F(x) for x in v] for k, v in FIX["priors"].items()}
PRIOR_ORDER = FIX["prior_order"]
N_INC_AXIS = FIX["n_inc_axis"]
for name in PRIOR_ORDER:
    gate(sum(PRIORS[name]) == 1, "pmf %s sums to 1" % name)

T = FIX["budget"]["T_tokens"]
C_INC = FIX["budget"]["c_inc"]
C_NEW = FIX["budget"]["c_new"]
C_NEW_SENS = FIX["budget"]["c_new_sensitivity"]
H_BASE = FIX["budget"]["H_cycles"]
H_SENS = FIX["budget"]["H_sensitivity"]
K = FIX["K_untested"]
MARGIN = F(FIX["decision_rule"]["margin"])
SEEDS = FIX["seeds"]
N_MAIN = FIX["trajectories"]["main_per_cell"]
N_STAB = FIX["trajectories"]["stability_per_cell"]
N_REP = FIX["trajectories"]["reporting_per_cell"]
GATE_MAIN = F(FIX["agreement_gates"]["main_abs"])
GATE_WIDE = F(FIX["agreement_gates"]["stability_abs"])

CELLS = [(pn, n) for pn in PRIOR_ORDER for n in N_INC_AXIS]  # pinned order
CHANNELS = ["inc", "u1", "u2", "u3"]
POLICIES = ["CONCENTRATE", "SPLIT", "ETC"]


def cell_id(pn, n):
    return "%s/n%d" % (pn, n)


# ---------------------------------------------------------------- Arm A core
def e_fail(pmf, n):
    """E[(1-p)^n] under pmf over RATES."""
    return sum(w * (1 - p) ** n for w, p in zip(pmf, RATES))


def posterior_zero(pmf, n):
    """pmf conditioned on 0 successes in n exposures."""
    w = [wi * (1 - p) ** n for wi, p in zip(pmf, RATES)]
    tot = sum(w)
    return [x / tot for x in w]


def mean_p(pmf):
    return sum(w * p for w, p in zip(pmf, RATES))


def post_mean_unnorm(weights):
    tot = sum(weights)
    if tot == 0:
        return F(0)  # zero-probability branch; callers skip such patterns
    return sum(w * p for w, p in zip(weights, RATES)) / tot


def tie_argmax(means):
    """Argmax over CHANNELS order inc -> u1 -> u2 -> u3, status-quo-first."""
    best_i, best_m = 0, means[0]
    for i in range(1, len(means)):
        if means[i] > best_m:
            best_i, best_m = i, means[i]
    return best_i


def committer(prior, n_inc, xs):
    """Committed channel from ALL evidence. xs: {channel: 0/1} for probed
    channels only; unprobed u-channels carry the bare prior."""
    def lik(x, p):
        return p if x else (1 - p)
    w_inc = [wi * (1 - p) ** n_inc for wi, p in zip(prior, RATES)]
    if "inc" in xs:
        w_inc = [w * lik(xs["inc"], p) for w, p in zip(w_inc, RATES)]
    means = [post_mean_unnorm(w_inc)]
    for u in ("u1", "u2", "u3"):
        if u in xs:
            w = [wi * lik(xs[u], p) for wi, p in zip(prior, RATES)]
            means.append(post_mean_unnorm(w))
        else:
            means.append(mean_p(prior))
    return CHANNELS[tie_argmax(means)]


def split_seq(H, c_new):
    """Round-robin build sequence u1,u2,u3,u1,... — (T//c_new)*H builds."""
    total = (T // c_new) * H
    return ["u%d" % (i % K + 1) for i in range(total)]


def etc_schedule(H, c_new):
    """Generalized ETC probe packing (reduces to the pinned schedule at the
    registered base c_new=90k, H=4: cycle1 u1+u2; cycle2 u3+inc, 30k lost;
    commit cycles 3-4). Returns (probes in launch order, commit_cycles)."""
    queue = ["u1", "u2", "u3", "inc"]
    launched = []
    cyc = 0
    while queue and cyc < H:
        budget = T
        rest = []
        for item in queue:
            cost = C_INC if item == "inc" else c_new
            if cost <= budget:
                budget -= cost
                launched.append(item)
            else:
                rest.append(item)
        queue = rest
        cyc += 1
    commit_cycles = (H - cyc) if not queue else 0
    return launched, commit_cycles


def per_cycle_builds(channel, c_new):
    return (T // C_INC) if channel == "inc" else (T // c_new)


def conc_exact(prior, n_inc, H):
    n = (T // C_INC) * H
    p_any = 1 - e_fail(prior, n_inc + n) / e_fail(prior, n_inc)
    e_hits = n * mean_p(posterior_zero(prior, n_inc))
    return p_any, e_hits


def split_exact(prior, H, c_new):
    seq = split_seq(H, c_new)
    counts = [seq.count("u%d" % (j + 1)) for j in range(K)]
    p_none = F(1)
    for c in counts:
        p_none *= e_fail(prior, c)
    e_hits = len(seq) * mean_p(prior)
    return 1 - p_none, e_hits, counts


def etc_exact(prior, n_inc, H, c_new):
    probes, commit_cycles = etc_schedule(H, c_new)
    post0 = posterior_zero(prior, n_inc)
    npr = len(probes)
    commit_of = {}
    if commit_cycles > 0:
        for pat in range(2 ** npr):
            xs = {probes[i]: (pat >> i) & 1 for i in range(npr)}
            commit_of[pat] = committer(prior, n_inc, xs)
    # power cache: pow1m[rate_idx][exponent]
    maxm = commit_cycles * max(T // C_INC, T // c_new) if commit_cycles else 0
    pow1m = [[(1 - RATES[i]) ** e for e in range(maxm + 1)] for i in range(NR)]
    p_none = F(0)
    e_hits = F(0)
    commit_dist = dict((c, F(0)) for c in CHANNELS)
    weights = {"inc": post0, "u1": prior, "u2": prior, "u3": prior}
    for combo in itertools.product(range(NR), repeat=4):
        w = post0[combo[0]] * prior[combo[1]] * prior[combo[2]] * prior[combo[3]]
        if w == 0:
            continue
        prate = dict(zip(CHANNELS, (RATES[i] for i in combo)))
        pidx = dict(zip(CHANNELS, combo))
        for pat in range(2 ** npr):
            prob = F(1)
            nsucc = 0
            for i, lab in enumerate(probes):
                x = (pat >> i) & 1
                prob *= prate[lab] if x else (1 - prate[lab])
                nsucc += x
            if prob == 0:
                continue
            if commit_cycles > 0:
                c = commit_of[pat]
                m = commit_cycles * per_cycle_builds(c, c_new)
                commit_dist[c] += w * prob
                e_hits += w * prob * (nsucc + m * prate[c])
                if nsucc == 0:
                    p_none += w * prob * pow1m[pidx[c]][m]
            else:
                e_hits += w * prob * nsucc
                if nsucc == 0:
                    p_none += w * prob
    return 1 - p_none, e_hits, commit_dist, probes, commit_cycles


def arm_a_tables(H, c_new):
    """Full 9-cell x 3-policy exact tables at a configuration."""
    out = {}
    for pn, n_inc in CELLS:
        prior = PRIORS[pn]
        ca, ch = conc_exact(prior, n_inc, H)
        sa, sh, scounts = split_exact(prior, H, c_new)
        ea, eh, cdist, probes, ccyc = etc_exact(prior, n_inc, H, c_new)
        out[cell_id(pn, n_inc)] = {
            "CONCENTRATE": {"P_any": ca, "E_hits": ch},
            "SPLIT": {"P_any": sa, "E_hits": sh, "counts": scounts},
            "ETC": {"P_any": ea, "E_hits": eh, "commit_dist": cdist,
                    "probes": probes, "commit_cycles": ccyc},
        }
    return out


# ---------------------------------------------------------------- hand fixture
HF = FIX["hand_fixture"]
# F1 — SKEPTIC n=1 posterior
f1 = posterior_zero(PRIORS["SKEPTIC"], 1)
gate(f1 == [F(x) for x in HF["F1_skeptic_n1_posterior"]], "F1 SKEPTIC/n1 posterior (800,392,180,75,50)/1497")
# F2 — NEUTRAL fresh channel, 2 exposures
gate(e_fail(PRIORS["NEUTRAL"], 2) == F(HF["F2_neutral_2exp"]["P_none"]), "F2 NEUTRAL 2-exposure P_none = 35829/50000")
gate(1 - e_fail(PRIORS["NEUTRAL"], 2) == F(HF["F2_neutral_2exp"]["P_any"]), "F2 NEUTRAL 2-exposure P_any = 14171/50000")
# F3 — committer tie -> incumbent (direct tie rule + end-to-end point-mass tie)
gate(CHANNELS[tie_argmax([F(1, 7)] * 4)] == "inc", "F3 tie rule returns incumbent")
_point_tenth = [F(0), F(0), F(1), F(0), F(0)]  # point mass at p = 1/10
gate(committer(_point_tenth, 7, {"inc": 0, "u1": 0, "u2": 0, "u3": 0}) == "inc",
     "F3 end-to-end: point-mass all-fail pattern commits incumbent")
# F4 — SPLIT allocation (3, 3, 2)
_seq = split_seq(H_BASE, C_NEW)
gate([_seq.count("u%d" % j) for j in (1, 2, 3)] == HF["F4_split_counts_H4"], "F4 SPLIT counts (3,3,2)")
# F5 — budget arithmetic
gate(T // C_INC == HF["F5_budget"]["builds_inc_per_cycle"], "F5 floor(180/60) = 3")
gate(T // C_NEW == HF["F5_budget"]["builds_new_per_cycle"], "F5 floor(180/90) = 2")
_probes, _cc = etc_schedule(H_BASE, C_NEW)
gate(_probes == ["u1", "u2", "u3", "inc"] and _cc == 2, "F5 ETC pinned schedule: probes u1,u2|u3,inc; commit cycles 3-4")
gate(2 * C_NEW == T and C_NEW + C_INC == HF["F5_budget"]["etc_cycle2_spend"]
     and T - (C_NEW + C_INC) == HF["F5_budget"]["etc_cycle2_lost"], "F5 ETC cycle-2 spend 150k, 30k lost")
# F6 — point-prior identity
_ca, _ = conc_exact(_point_tenth, 7, H_BASE)
gate(_ca == 1 - F(9, 10) ** 12, "F6 point-prior CONCENTRATE P_any = 1 - (9/10)^12")
# Degenerate-zero gate
_point_zero = [F(1), F(0), F(0), F(0), F(0)]
_ca0, _ch0 = conc_exact(_point_zero, 7, H_BASE)
_sa0, _sh0, _ = split_exact(_point_zero, H_BASE, C_NEW)
_ea0, _eh0, _, _, _ = etc_exact(_point_zero, 7, H_BASE, C_NEW)
gate(_ca0 == 0 and _ch0 == 0 and _sa0 == 0 and _sh0 == 0 and _ea0 == 0 and _eh0 == 0,
     "degenerate-zero: point mass at 0 gives exact P_any = E_hits = 0, all policies")

# ---------------------------------------------------------------- Arm A runs
ARM_A = {}
ARM_A["base"] = arm_a_tables(H_BASE, C_NEW)
ARM_A["cnew_60k"] = arm_a_tables(H_BASE, C_NEW_SENS[0])
ARM_A["cnew_120k"] = arm_a_tables(H_BASE, C_NEW_SENS[1])
ARM_A["H_2"] = arm_a_tables(H_SENS[0], C_NEW)
ARM_A["H_8"] = arm_a_tables(H_SENS[1], C_NEW)

# horizon monotonicity gate (exact, Arm A)
for cid in (cell_id(pn, n) for pn, n in CELLS):
    for pol in POLICIES:
        h2 = ARM_A["H_2"][cid][pol]["P_any"]
        h4 = ARM_A["base"][cid][pol]["P_any"]
        h8 = ARM_A["H_8"][cid][pol]["P_any"]
        gate(h2 <= h4 <= h8, "horizon monotonicity (Arm A) %s %s" % (cid, pol))

# equal-cost direction check (reporting — flagged loudly on surprise)
for pn in PRIOR_ORDER:
    cid = cell_id(pn, 7)
    s = ARM_A["cnew_60k"][cid]["SPLIT"]["P_any"]
    c = ARM_A["cnew_60k"][cid]["CONCENTRATE"]["P_any"]
    if s < c:
        anomaly("equal-cost direction check: SPLIT < CONCENTRATE in %s at c_new=60k" % cid)
_PASS[0] += 1  # direction check executed (reporting)


def con_div(table, cid):
    con = table[cid]["CONCENTRATE"]["P_any"]
    div = max(table[cid]["SPLIT"]["P_any"], table[cid]["ETC"]["P_any"])
    return con, div


# ---------------------------------------------------------------- Arm S
class RNG:
    def __init__(self, seed):
        self._r = random.Random(seed)
        self.calls = 0

    def u(self):
        self.calls += 1
        return self._r.random()


def pmf_cum_float(pmf):
    acc, out = F(0), []
    for w in pmf:
        acc += w
        out.append(float(acc))
    out[-1] = 1.0
    return out


def draw_rate_idx(rng, cum):
    x = rng.u()
    for i, c in enumerate(cum):
        if x < c:
            return i
    return len(cum) - 1


def mc_leg(seed, n_traj, H, c_new, nested_H=None):
    """One MC leg. Returns per-cell results. If nested_H is a list of horizons
    (ascending, containing H as max), P_any is evaluated at every horizon via
    prefix draws (monotone by construction)."""
    rng = RNG(seed)
    horizons = nested_H or [H]
    Hmax = max(horizons)
    results = {}
    expected_calls = 0
    for pn, n_inc in CELLS:
        prior = PRIORS[pn]
        post0 = posterior_zero(prior, n_inc)
        cum_post = pmf_cum_float(post0)
        cum_prior = pmf_cum_float(prior)
        pf = [float(p) for p in RATES]
        probes, commit_cycles_max = etc_schedule(Hmax, c_new)
        commit_of = {}
        if commit_cycles_max > 0:
            for pat in range(2 ** len(probes)):
                xs = {probes[i]: (pat >> i) & 1 for i in range(len(probes))}
                commit_of[pat] = committer(prior, n_inc, xs)
        cc_by_h = {h: etc_schedule(h, c_new)[1] for h in horizons}
        seq = split_seq(Hmax, c_new)
        n_conc = (T // C_INC) * Hmax
        any_ct = {h: {pol: 0 for pol in POLICIES} for h in horizons}
        hits_sum = {pol: 0 for pol in POLICIES}  # at horizon H (leg config)
        commit_ct = dict((c, 0) for c in CHANNELS)
        for _ in range(n_traj):
            i_inc = draw_rate_idx(rng, cum_post)
            iu = [draw_rate_idx(rng, cum_prior) for _ in range(K)]
            expected_calls += 4
            pr = {"inc": pf[i_inc], "u1": pf[iu[0]], "u2": pf[iu[1]], "u3": pf[iu[2]]}
            # CONCENTRATE
            csucc = [1 if rng.u() < pr["inc"] else 0 for _ in range(n_conc)]
            expected_calls += n_conc
            # SPLIT
            ssucc = [1 if rng.u() < pr[lab] else 0 for lab in seq]
            expected_calls += len(seq)
            # ETC probes (launch order)
            psucc = [1 if rng.u() < pr[lab] else 0 for lab in probes]
            expected_calls += len(probes)
            pat = sum(b << i for i, b in enumerate(psucc))
            if commit_cycles_max > 0:
                cch = commit_of[pat]
                m_max = commit_cycles_max * per_cycle_builds(cch, c_new)
                msucc = [1 if rng.u() < pr[cch] else 0 for _ in range(m_max)]
                expected_calls += m_max
            else:
                cch, msucc = None, []
            for h in horizons:
                nc = (T // C_INC) * h
                ns = (T // c_new) * h
                cc = cc_by_h[h]
                m_h = cc * per_cycle_builds(cch, c_new) if (cch and cc > 0) else 0
                if any(csucc[:nc]):
                    any_ct[h]["CONCENTRATE"] += 1
                if any(ssucc[:ns]):
                    any_ct[h]["SPLIT"] += 1
                if any(psucc) or any(msucc[:m_h]):
                    any_ct[h]["ETC"] += 1
            # hits at the leg's own H
            cc_h = cc_by_h[H]
            m_h = cc_h * per_cycle_builds(cch, c_new) if (cch and cc_h > 0) else 0
            hits_sum["CONCENTRATE"] += sum(csucc[:(T // C_INC) * H])
            hits_sum["SPLIT"] += sum(ssucc[:(T // c_new) * H])
            hits_sum["ETC"] += sum(psucc) + sum(msucc[:m_h])
            if cch and cc_by_h[H] > 0:
                commit_ct[cch] += 1
        results[cell_id(pn, n_inc)] = {
            "P_any": {h: {pol: F(any_ct[h][pol], n_traj) for pol in POLICIES} for h in horizons},
            "E_hits": {pol: F(hits_sum[pol], n_traj) for pol in POLICIES},
            "commit_ct": commit_ct,
        }
    return results, rng.calls, expected_calls


def agree(arm_s_cell, arm_a_table, cid, h, bound, label):
    for pol in POLICIES:
        d = abs(arm_s_cell["P_any"][h][pol] - arm_a_table[cid][pol]["P_any"])
        gate(d <= bound, "%s agreement %s %s |d|=%s" % (label, cid, pol, float(d)))


# main leg — seed 20261305, 200k/cell, base config
S_MAIN, calls_main, exp_main = mc_leg(SEEDS["main"], N_MAIN, H_BASE, C_NEW)
gate(calls_main == exp_main, "draw-count sentinel main leg (%d)" % calls_main)
for pn, n in CELLS:
    agree(S_MAIN[cell_id(pn, n)], ARM_A["base"], cell_id(pn, n), H_BASE, GATE_MAIN, "main(5/1000)")

# stability leg — seed 20261306, 20k/cell, base config, widened gate
S_STAB, calls_stab, exp_stab = mc_leg(SEEDS["stability"], N_STAB, H_BASE, C_NEW)
gate(calls_stab == exp_stab, "draw-count sentinel stability leg (%d)" % calls_stab)
for pn, n in CELLS:
    agree(S_STAB[cell_id(pn, n)], ARM_A["base"], cell_id(pn, n), H_BASE, GATE_WIDE, "stability(15/1000)")

# reporting legs — seed 20261307, 20k each, pinned order:
# (1) c_new=60k, (2) c_new=120k, (3) nested-H {2,4,8}, (4) E_hits base confirm
rep_rng_seed = SEEDS["reporting"]
S_R60, c1, e1 = mc_leg(rep_rng_seed, N_REP, H_BASE, C_NEW_SENS[0])
gate(c1 == e1, "draw-count sentinel reporting c_new=60k (%d)" % c1)
S_R120, c2, e2 = mc_leg(rep_rng_seed, N_REP, H_BASE, C_NEW_SENS[1])
gate(c2 == e2, "draw-count sentinel reporting c_new=120k (%d)" % c2)
S_RH, c3, e3 = mc_leg(rep_rng_seed, N_REP, max(H_SENS), C_NEW, nested_H=[H_SENS[0], H_BASE, H_SENS[1]])
gate(c3 == e3, "draw-count sentinel reporting nested-H (%d)" % c3)
S_RE, c4, e4 = mc_leg(rep_rng_seed, N_REP, H_BASE, C_NEW)
gate(c4 == e4, "draw-count sentinel reporting E_hits (%d)" % c4)
for pn, n in CELLS:
    cid = cell_id(pn, n)
    agree(S_R60[cid], ARM_A["cnew_60k"], cid, H_BASE, GATE_WIDE, "rep-60k(15/1000)")
    agree(S_R120[cid], ARM_A["cnew_120k"], cid, H_BASE, GATE_WIDE, "rep-120k(15/1000)")
    agree(S_RH[cid], ARM_A["H_2"], cid, H_SENS[0], GATE_WIDE, "rep-H2(15/1000)")
    agree(S_RH[cid], ARM_A["base"], cid, H_BASE, GATE_WIDE, "rep-H4(15/1000)")
    agree(S_RH[cid], ARM_A["H_8"], cid, H_SENS[1], GATE_WIDE, "rep-H8(15/1000)")
    agree(S_RE[cid], ARM_A["base"], cid, H_BASE, GATE_WIDE, "rep-Ehits-base(15/1000)")
    # MC horizon monotonicity — by construction (prefix draws), asserted
    for pol in POLICIES:
        pa = S_RH[cid]["P_any"]
        gate(pa[H_SENS[0]][pol] <= pa[H_BASE][pol] <= pa[H_SENS[1]][pol],
             "horizon monotonicity (Arm S nested) %s %s" % (cid, pol))
    # E_hits confirmation (reporting; loud anomaly beyond 6/100)
    for pol in POLICIES:
        d = abs(S_RE[cid]["E_hits"][pol] - ARM_A["base"][cid][pol]["E_hits"])
        if d > F(6, 100):
            anomaly("E_hits confirm delta > 6/100 in %s %s (d=%s)" % (cid, pol, float(d)))
_PASS[0] += 1  # E_hits confirmation executed (reporting)

# aux seed 20261308 — reserved, NEVER read
AUX_DRAWS = 0
gate(AUX_DRAWS == 0, "aux seed 20261308 never read (0 draws)")

# ---------------------------------------------------------------- decision
N1_CELLS = set(cell_id(pn, 1) for pn in PRIOR_ORDER)


def eval_A(cells_con_div):
    """Evaluator A — Fractions, comprehension-style."""
    below = sum(1 for cid, (con, div) in cells_con_div.items() if div - con < MARGIN)
    above = sum(1 for cid, (con, div) in cells_con_div.items() if div - con >= MARGIN)
    above_n1 = sum(1 for cid, (con, div) in cells_con_div.items()
                   if cid in N1_CELLS and div - con >= MARGIN)
    if below >= 7:
        return "REJECT-CELLS"
    if above >= 7 and above_n1 >= 2:
        return "APPROVE-CELLS"
    return "NULL-CELLS"


def eval_B(cells_con_div):
    """Evaluator B — independently written: integer cross-multiplication on
    normalized numerators/denominators, explicit loop, margin = 1/100 as
    100*num >= den."""
    n_below = 0
    n_above = 0
    n_above_n1 = 0
    for cid in sorted(cells_con_div.keys()):
        con, div = cells_con_div[cid]
        diff = div - con  # Fraction, normalized, den > 0
        num, den = diff.numerator, diff.denominator
        # diff >= 1/100  <=>  100*num >= den
        if 100 * num >= den:
            n_above += 1
            if cid in N1_CELLS:
                n_above_n1 += 1
        else:
            n_below += 1
    if n_below >= 7:
        return "REJECT-CELLS"
    if n_above >= 7 and n_above_n1 >= 2:
        return "APPROVE-CELLS"
    return "NULL-CELLS"


def table_con_div(table):
    return dict((cid, con_div(table, cid)) for cid in (cell_id(pn, n) for pn, n in CELLS))


def mc_con_div(mc, h):
    out = {}
    for pn, n in CELLS:
        cid = cell_id(pn, n)
        con = mc[cid]["P_any"][h]["CONCENTRATE"]
        div = max(mc[cid]["P_any"][h]["SPLIT"], mc[cid]["P_any"][h]["ETC"])
        out[cid] = (con, div)
    return out


CD_A = table_con_div(ARM_A["base"])
CD_STAB = mc_con_div(S_STAB, H_BASE)

ruling_A_1, ruling_A_2 = eval_A(CD_A), eval_B(CD_A)
gate(ruling_A_1 == ruling_A_2, "twin evaluators agree on Arm A (%s)" % ruling_A_1)
ruling_S_1, ruling_S_2 = eval_A(CD_STAB), eval_B(CD_STAB)
gate(ruling_S_1 == ruling_S_2, "twin evaluators agree on stability leg (%s)" % ruling_S_1)


def null_axis(cd):
    """Named NULL axis, pre-registered candidates, checked in registration order."""
    winners = {}
    for cid, (con, div) in cd.items():
        winners[cid] = "DIV" if div - con >= MARGIN else "CON"
    # (i) prior-straddle: flip across optimism within a fixed n_inc row
    for n in N_INC_AXIS:
        row = set(winners[cell_id(pn, n)] for pn in PRIOR_ORDER)
        if len(row) > 1:
            return "prior-straddle (n_inc=%d row)" % n
    # (ii) evidence-straddle: flip across n_inc within a fixed optimism row
    for pn in PRIOR_ORDER:
        row = set(winners[cell_id(pn, n)] for n in N_INC_AXIS)
        if len(row) > 1:
            return "evidence-straddle (%s row)" % pn
    return "margin-thin"


verdict = None
verdict_axis = ""
if ruling_A_1 == "REJECT-CELLS":
    verdict = "reject"
elif ruling_A_1 == "APPROVE-CELLS":
    if ruling_S_1 == "APPROVE-CELLS":
        verdict = "approve"
    else:
        verdict = "null"
        verdict_axis = "margin-thin (stability leg failed to reproduce the APPROVE cell conditions)"
else:
    verdict = "null"
    verdict_axis = null_axis(CD_A)

# sensitivity-straddle report (reporting-only — CANNOT flip the decision)
SENS_RULINGS = {}
for key in ("cnew_60k", "cnew_120k", "H_2", "H_8"):
    SENS_RULINGS[key] = eval_A(table_con_div(ARM_A[key]))
sens_straddle = [k for k, v in SENS_RULINGS.items() if v != ruling_A_1]

# ---------------------------------------------------------------- output


def fs(x):
    return "%s (~%.6f)" % (x, float(x))


def serialize_arm_a(table):
    out = {}
    for cid, row in table.items():
        out[cid] = {}
        for pol in POLICIES:
            e = {"P_any": str(row[pol]["P_any"]),
                 "P_any_approx": "%.6f" % float(row[pol]["P_any"]),
                 "E_hits": str(row[pol]["E_hits"]),
                 "E_hits_approx": "%.6f" % float(row[pol]["E_hits"])}
            if pol == "SPLIT":
                e["counts_u1_u2_u3"] = row[pol]["counts"]
            if pol == "ETC":
                e["commit_dist"] = dict((c, str(v)) for c, v in row[pol]["commit_dist"].items())
                e["probes"] = row[pol]["probes"]
                e["commit_cycles"] = row[pol]["commit_cycles"]
            out[cid][pol] = e
    return out


def serialize_mc(mc):
    out = {}
    for cid, row in mc.items():
        out[cid] = {
            "P_any": {str(h): dict((pol, str(v)) for pol, v in d.items())
                      for h, d in row["P_any"].items()},
            "E_hits": dict((pol, str(v)) for pol, v in row["E_hits"].items()),
            "commit_ct": row["commit_ct"],
        }
    return out


results = {
    "verdict_053": {
        "class": verdict,
        "null_axis": verdict_axis,
        "rule_trace": {
            "REJECT_checked_first": ruling_A_1 == "REJECT-CELLS",
            "arm_a_cells_ruling": ruling_A_1,
            "stability_cells_ruling": ruling_S_1,
            "twin_evaluators": "agree (A: comprehension/Fraction, B: integer cross-multiplication)",
        },
        "cells_con_div": dict(
            (cid, {"CON": str(con), "DIV": str(div), "DIV_minus_CON": str(div - con),
                   "DIV_minus_CON_approx": "%.6f" % float(div - con),
                   "DIV_carrier": ("SPLIT" if ARM_A["base"][cid]["SPLIT"]["P_any"] >=
                                   ARM_A["base"][cid]["ETC"]["P_any"] else "ETC")})
            for cid, (con, div) in CD_A.items()),
        "sensitivity_rulings_reporting_only": SENS_RULINGS,
        "sensitivity_straddle": sens_straddle,
    },
    "arm_a": dict((k, serialize_arm_a(v)) for k, v in ARM_A.items()),
    "arm_s": {
        "main_seed_20261305": serialize_mc(S_MAIN),
        "stability_seed_20261306": serialize_mc(S_STAB),
        "reporting_seed_20261307": {
            "cnew_60k": serialize_mc(S_R60),
            "cnew_120k": serialize_mc(S_R120),
            "nested_H": serialize_mc(S_RH),
            "ehits_base": serialize_mc(S_RE),
        },
        "draw_counts": {"main": calls_main, "stability": calls_stab,
                        "rep_cnew60": c1, "rep_cnew120": c2, "rep_nestedH": c3,
                        "rep_ehits": c4, "aux_20261308": AUX_DRAWS},
    },
    "anomalies": ANOMALIES,
    "self_checks_passed": None,  # filled below
}

print("=" * 72)
print("VERDICT 053 — channel concentration vs diversification (PROPOSAL 042)")
print("=" * 72)
print("Arm A decision table (exact; CON = P_any(CONCENTRATE), DIV = max(SPLIT, ETC)):")
for pn, n in CELLS:
    cid = cell_id(pn, n)
    con, div = CD_A[cid]
    carrier = "SPLIT" if ARM_A["base"][cid]["SPLIT"]["P_any"] >= ARM_A["base"][cid]["ETC"]["P_any"] else "ETC"
    print("  %-12s CON=%.6f DIV=%.6f (%s) DIV-CON=%.6f %s" % (
        cid, float(con), float(div), carrier, float(div - con),
        ">=1/100" if div - con >= MARGIN else "<1/100"))
print("Arm A exact decision-cell fractions:")
for pn, n in CELLS:
    cid = cell_id(pn, n)
    con, div = CD_A[cid]
    print("  %-12s CON=%s DIV=%s" % (cid, con, div))
print("ETC committed-channel distribution (Arm A, base):")
for pn, n in CELLS:
    cid = cell_id(pn, n)
    d = ARM_A["base"][cid]["ETC"]["commit_dist"]
    print("  %-12s " % cid + " ".join("%s=%.4f" % (c, float(v)) for c, v in d.items()))
print("Sensitivity rulings (reporting-only, cannot flip): %s" % SENS_RULINGS)
if sens_straddle:
    print("Sensitivity straddle (named, reporting-only): %s" % sens_straddle)
print("Stability leg (seed 20261306) cells ruling: %s" % ruling_S_1)
print("Anomalies: %s" % (ANOMALIES if ANOMALIES else "none"))
print("RULING (pre-registered order, REJECT first): %s%s" % (
    verdict.upper(), (" — axis: " + verdict_axis) if verdict_axis else ""))
results["self_checks_passed"] = _PASS[0]
print("SELF-CHECKS: %d passed, 0 failed" % _PASS[0])

with open(os.path.join(HERE, "results.json"), "w") as f:
    json.dump(results, f, indent=1, sort_keys=False)
    f.write("\n")
