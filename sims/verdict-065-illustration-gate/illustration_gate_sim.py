#!/usr/bin/env python3
"""VERDICT 065 — the illustration gate: PARK vs Commission/AI/AI-pilot (PROPOSAL 054).

Dual-arm hermetic sim per the registration (idea-engine PROPOSAL 054 @ main
ca71997; idea doc ideas/venture-lab/illustration-gate-park-vs-pilot-2026-07-14.md).
Arm A: seedless exact fractions.Fraction closed-form expected-value tree
(alone decision-bearing). Arm S: seeded common-random-numbers MC confirmation.
Reads ONLY its own fixtures.json. Stdlib only. No wall-clock in any output.
Run: python3 sims/verdict-065-illustration-gate/illustration_gate_sim.py
"""
import json
import os
import random
import sys
from fractions import Fraction as F
from math import sqrt

# ---------------------------------------------------------------- environment
assert sys.version_info[:2] == (3, 11), "CPython 3.11 pinned by the registration"

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "fixtures.json"), "r", encoding="utf-8") as fh:
    FIX = json.load(fh)

# ---------------------------------------------------------------- self-checks
CHECKS_PASSED = 0
RECORDED_FAILURES = []  # registered-gate outcomes whose failure is itself a finding


def check(name, ok):
    """Hard assert — structural/arithmetic invariants."""
    global CHECKS_PASSED
    if not ok:
        raise AssertionError("SELF-CHECK FAILED: " + name)
    CHECKS_PASSED += 1


def gate(name, ok):
    """Registered-gate outcome: recorded, feeds validity, never crashes
    (axis (v) of the registered NULL taxonomy requires a completed run)."""
    global CHECKS_PASSED
    if ok:
        CHECKS_PASSED += 1
    else:
        RECORDED_FAILURES.append(name)
    return ok


def fr(s):
    """Parse fixture rational strings like '7/20' or '30'."""
    return F(s)


# ---------------------------------------------------------------- constants
P_LIVE = [fr(x) for x in FIX["model"]["P_live"]]
OMEGA = [fr(x) for x in FIX["model"]["omega"]]
OMEGA_U = [fr(x) for x in FIX["model"]["omega_prime_uniform"]]
PI_ROWS = [("SKEPTIC", fr(FIX["model"]["pi_L_rows"]["SKEPTIC"])),
           ("NEUTRAL", fr(FIX["model"]["pi_L_rows"]["NEUTRAL"])),
           ("HOPEFUL", fr(FIX["model"]["pi_L_rows"]["HOPEFUL"]))]
C_COLS = [F(c) for c in FIX["model"]["c_columns"]]
R = fr(FIX["model"]["royalty_r"])
Q = fr(FIX["model"]["q_ai_quality"])
RHO = fr(FIX["model"]["rho_removal_risk"])
A_TOOL = F(FIX["model"]["a_ai_tool_cost_total"])
H = FIX["model"]["H_days"]
K = FIX["model"]["K_titles"]
W = FIX["model"]["W_pilot_days"]
M_MARGIN = F(FIX["decision_rule"]["margin_m_dollars"])
M_SWEEP = [F(m) for m in FIX["decision_rule"]["margin_sweep"]]
POLICIES = FIX["policies"]["order_pinned"]
FAMILY = dict(FIX["policies"]["family_map"])
SEED_MAIN, SEED_STAB, SEED_REPORT, SEED_AUX = FIX["arms"]["seeds_registered"]
N_MAIN = 200000
N_STAB = 20000
N_REPORT = 20000

# transcription gates — fixtures vs the registration echoed here
check("transcription: seeds 20261353-356", (SEED_MAIN, SEED_STAB, SEED_REPORT, SEED_AUX) == (20261353, 20261354, 20261355, 20261356))
check("transcription: grid K=5 H=365 W=90", (K, H, W) == (5, 365, 90))
check("transcription: c columns", C_COLS == [F(1500), F(3245), F(4950)])
check("transcription: r = 2097/500", R == F(2097, 500))
check("transcription: q rho a", (Q, RHO, A_TOOL) == (F(7, 10), F(1, 20), F(30)))
check("transcription: margin m = 100, sweep {25,400}", M_MARGIN == 100 and M_SWEEP == [F(25), F(400)])
check("transcription: pi rows 3/4,1/2,1/4", [p for _, p in PI_ROWS] == [F(3, 4), F(1, 2), F(1, 4)])
check("transcription: P_live", P_LIVE == [F(1, 60), F(1, 30), F(1, 10), F(1, 3), F(1)])
check("transcription: omega", OMEGA == [F(7, 20), F(3, 10), F(1, 5), F(1, 10), F(1, 20)])
check("transcription: 7 policies pinned order", POLICIES == ["PARK", "COMM-ALL", "COMM-PILOT-SALE", "COMM-PILOT-EV", "AI-ALL", "AI-PILOT-SALE", "AI-PILOT-EV"])

# ---------------------------------------------------------------- worlds
def world(name, *, K=K, H=H, W=W, q=Q, rho=RHO, a_line=A_TOOL, a_pilot=A_TOOL,
          omega=None, p_live=None, r=R):
    return {
        "name": name, "K": K, "H": H, "W": W, "q": q, "rho": rho,
        "a_line": a_line, "a_pilot": a_pilot,
        "omega": omega if omega is not None else OMEGA,
        "p_live": p_live if p_live is not None else P_LIVE,
        "r": r,
    }


HEADLINE = world("headline")
REPORT_WORLDS = [
    world("H180", H=180),
    world("H730", H=730),
    world("K7", K=7),
    world("omega_uniform", omega=OMEGA_U),
    world("q_1_2", q=F(1, 2)),
    world("q_9_10", q=F(9, 10)),
    world("rho_0", rho=F(0)),
    world("rho_1_10", rho=F(1, 10)),
    world("a_0", a_line=F(0), a_pilot=F(0)),
    world("a_150", a_line=F(150), a_pilot=F(30)),
    world("W45", W=45),
    world("W180", W=180),
]
HAND_WORLD = world("F4_hand", K=2, H=4, W=2, q=F(1, 2), rho=F(0),
                   a_line=F(1), a_pilot=F(1), omega=[F(1)], p_live=[F(1, 2)], r=F(1))


# ---------------------------------------------------------------- Arm A (exact)
def arm_a_cell(w, pi_l, c):
    """Exact NET per policy for one (belief, cost) cell — the expected-value tree.

    Per-title commissioned gross published day 0 given alive: B = mu*r*H
    (linearity over ~Bernoulli(f*p) days). Pilot commit prob given alive:
    1-(1-f*p)^W mixed over omega. On >=1 pilot sale the line is alive with
    certainty (dead lines cannot sell — exact Bayes below), so each of the
    K-1 continuation titles published day W is worth V_cont = mu*r*(H-W).
    """
    mu = sum(wi * pi for wi, pi in zip(w["omega"], w["p_live"]))
    B = mu * w["r"] * w["H"]
    v_cont = mu * w["r"] * (w["H"] - w["W"])
    p1 = sum(wi * (1 - (1 - pi) ** w["W"]) for wi, pi in zip(w["omega"], w["p_live"]))
    pq = sum(wi * (1 - (1 - w["q"] * pi) ** w["W"]) for wi, pi in zip(w["omega"], w["p_live"]))
    alpha = 1 - pi_l
    k, q, rho = w["K"], w["q"], w["rho"]
    a_l, a_p = w["a_line"], w["a_pilot"]
    ev_ok = v_cont > c  # the EV commit gate — exact
    cont = (k - 1) * (v_cont - c)
    nets = {
        "PARK": F(0),
        "COMM-ALL": k * alpha * B - k * c,
        "COMM-PILOT-SALE": -c + alpha * B + alpha * p1 * cont,
        "COMM-PILOT-EV": -c + alpha * B + (alpha * p1 * cont if ev_ok else F(0)),
        "AI-ALL": k * (1 - rho) * q * alpha * B - a_l,
        "AI-PILOT-SALE": -a_p + (1 - rho) * alpha * (q * B + pq * cont),
        "AI-PILOT-EV": -a_p + (1 - rho) * alpha * (q * B + (pq * cont if ev_ok else F(0))),
    }
    commit_prob = {
        "COMM-PILOT-SALE": alpha * p1,
        "COMM-PILOT-EV": alpha * p1 if ev_ok else F(0),
        "AI-PILOT-SALE": (1 - rho) * alpha * pq,
        "AI-PILOT-EV": (1 - rho) * alpha * pq if ev_ok else F(0),
    }
    aux = {"mu": mu, "B": B, "V_cont": v_cont, "P1": p1, "Pq": pq,
           "alpha": alpha, "ev_ok": ev_ok}
    return nets, commit_prob, aux


def arm_a_grid(w):
    """Full 9-cell grid for a world, row-major pinned order."""
    cells = []
    for row_name, pi_l in PI_ROWS:
        for c in C_COLS:
            nets, commit_prob, aux = arm_a_cell(w, pi_l, c)
            best = max((p for p in POLICIES if p != "PARK"), key=lambda p: nets[p])
            delta = nets[best] - nets["PARK"]
            cells.append({
                "row": row_name, "pi_L": pi_l, "c": c, "nets": nets,
                "commit_prob": commit_prob, "aux": aux,
                "argmax": best, "family": FAMILY[best], "delta": delta,
            })
    return cells


def posterior_alive_given_sale(w, pi_l):
    """Exact Bayes: P(alive | >=1 pilot sale in W) — dead lines cannot sell."""
    alpha = 1 - pi_l
    p1 = sum(wi * (1 - (1 - pi) ** w["W"]) for wi, pi in zip(w["omega"], w["p_live"]))
    p_sale_and_alive = alpha * p1
    p_sale_and_dead = pi_l * F(0)  # p = 0 for every title of a dead line
    if p_sale_and_alive + p_sale_and_dead == 0:
        return None
    return p_sale_and_alive / (p_sale_and_alive + p_sale_and_dead)


# ---------------------------------------------------------------- twin evaluators
def evaluator_fraction(deltas, families, skeptic_idx, m):
    """Twin evaluator 1 — procedural Fraction comparisons."""
    over = [i for i, d in enumerate(deltas) if d >= m]
    under = [i for i, d in enumerate(deltas) if d < m]
    fam_over = sorted({families[i] for i in over})
    reject_shape = len(over) >= 7 and len(fam_over) == 1
    approve_shape = len(under) >= 7 and sum(1 for i in under if i in skeptic_idx) >= 2
    return {"over": len(over), "under": len(under), "families_over": fam_over,
            "reject_shape": reject_shape, "approve_shape": approve_shape}


def evaluator_integer(deltas, families, skeptic_idx, m):
    """Twin evaluator 2 — independently written, pure-integer cross-multiplication.

    Each delta handled as a (num, den) pair with den > 0; d >= m iff
    num * m.den >= m.num * den. No Fraction comparison operators used.
    """
    m_n, m_d = m.numerator, m.denominator
    n_over = 0
    n_under = 0
    sk_under = 0
    fams = set()
    idx = 0
    for d in deltas:
        n, den = d.numerator, d.denominator
        if den < 0:
            n, den = -n, -den
        if n * m_d >= m_n * den:
            n_over += 1
            fams.add(families[idx])
        else:
            n_under += 1
            if idx in skeptic_idx:
                sk_under += 1
        idx += 1
    reject_shape = (n_over >= 7) and (len(fams) == 1)
    approve_shape = (n_under >= 7) and (sk_under >= 2)
    return {"over": n_over, "under": n_under, "families_over": sorted(fams),
            "reject_shape": reject_shape, "approve_shape": approve_shape}


def classify(shape, run_valid, stability_reproduces):
    """Registered rules IN ORDER (REJECT first) under the gate architecture:
    'Gates (run invalid on any failure)' — an invalid run cannot rule, and the
    registered NULL axis (v) exists precisely for the agreement-gate failure
    ('a defect is the finding, no ruling'); a ruling issued despite a failed
    registered gate would make axis (v) unreachable dead text."""
    if not run_valid:
        return "NULL"
    if shape["reject_shape"]:
        return "REJECT"
    if shape["approve_shape"] and stability_reproduces:
        return "APPROVE"
    return "NULL"


SKEPTIC_IDX = {0, 1, 2}  # row-major: first three cells are the SKEPTIC row


# ---------------------------------------------------------------- Arm S (seeded MC)
def mc_leg(w, rng, n_scen, cells_spec):
    """One MC leg: n_scen scenarios per cell, cells in pinned row-major order,
    common random numbers — each scenario replayed against all 7 policies.

    Pinned draw order per scenario: line-state -> K per-title p draws ->
    removal coins -> day-by-day Bernoulli trials (title-major, day-minor).
    Dead lines short-circuit at one draw (registered). Returns per-cell stats:
    integer sums of net_u (units 1/500 dollar) and net_u^2 per policy, draw
    counts, alive/dead tallies.
    """
    assert w["r"] == F(2097, 500)  # the integer-unit estimator rides r = 2097/500
    k, h, win = w["K"], w["H"], w["W"]
    q, rho = w["q"], w["rho"]
    a_l, a_p = int(w["a_line"]), int(w["a_pilot"])
    ev_ok = False  # V_cont > c is False at every registered world/column (asserted by caller)
    cum = []
    acc = F(0)
    for wi in w["omega"]:
        acc += wi
        cum.append(float(acc))
    p_f = [float(p) for p in w["p_live"]]
    qp_f = [float(q * p) for p in w["p_live"]]
    rho_f = float(rho)
    n_tiers = len(cum)
    out = []
    rnd = rng.random
    tail_days = h - win
    for row_name, pi_l in PI_ROWS:
        pi_f = float(pi_l)
        for c_frac in C_COLS:
            c = int(c_frac)
            s1_u = [0] * 7   # sums of net_u per policy, pinned order
            s2_u = [0] * 7
            draws = 0
            draws_coins = 0
            draws_trials = 0
            n_dead = 0
            n_alive = 0
            # dead-line constants (units 1/500 dollar) per policy
            dead_u = [0, -500 * k * c, -500 * c, -500 * c, -500 * a_l, -500 * a_p, -500 * a_p]
            for _ in range(n_scen):
                u = rnd()
                draws += 1
                if u < pi_f:
                    n_dead += 1
                    continue  # dead short-circuit: one draw, F3 constants added in bulk below
                n_alive += 1
                # K per-title p draws (categorical over omega)
                p_draws = [rnd() for _ in range(k)]
                draws += len(p_draws)
                idxs = []
                for u2 in p_draws:
                    i = 0
                    while i < n_tiers - 1 and u2 >= cum[i]:
                        i += 1
                    idxs.append(i)
                # removal coins — all K titles (the CRN union; AI-ALL AI-publishes all K)
                coin_draws = [rnd() for _ in range(k)]
                draws += len(coin_draws)
                draws_coins += len(coin_draws)
                rems = [u3 < rho_f for u3 in coin_draws]
                # day-by-day Bernoulli trials, title-major day-minor, all K titles x H days
                sum_n1 = 0
                sum_nq_live = 0
                sum_t1_rest = 0
                n1_0 = nq_0 = 0
                s1_0 = sq_0 = False
                for t in range(k):
                    pf = p_f[idxs[t]]
                    qpf = qp_f[idxs[t]]
                    n1 = nq = t1 = 0
                    seen1 = seenq = False
                    block1 = [rnd() for _ in range(win)]
                    for u4 in block1:
                        if u4 < pf:
                            n1 += 1
                            seen1 = True
                            if u4 < qpf:
                                nq += 1
                                seenq = True
                    block2 = [rnd() for _ in range(tail_days)]
                    for u4 in block2:
                        if u4 < pf:
                            n1 += 1
                            t1 += 1
                            if u4 < qpf:
                                nq += 1
                    draws += len(block1) + len(block2)
                    draws_trials += len(block1) + len(block2)
                    sum_n1 += n1
                    if not rems[t]:
                        sum_nq_live += nq
                    if t == 0:
                        n1_0, nq_0, s1_0, sq_0 = n1, nq, seen1, seenq
                    else:
                        sum_t1_rest += t1
                # per-policy net in integer units of 1/500 dollar (r = 2097/500)
                cont_u = 2097 * sum_t1_rest - 500 * (k - 1) * c
                v0 = 0
                v1 = 2097 * sum_n1 - 500 * k * c
                v2 = 2097 * n1_0 - 500 * c + (cont_u if s1_0 else 0)
                v3 = 2097 * n1_0 - 500 * c + (cont_u if (s1_0 and ev_ok) else 0)
                v4 = 2097 * sum_nq_live - 500 * a_l
                if rems[0]:
                    v5 = -500 * a_p
                    v6 = -500 * a_p
                else:
                    v5 = 2097 * nq_0 - 500 * a_p + (cont_u if sq_0 else 0)
                    v6 = 2097 * nq_0 - 500 * a_p + (cont_u if (sq_0 and ev_ok) else 0)
                vals = (v0, v1, v2, v3, v4, v5, v6)
                for j in range(7):
                    v = vals[j]
                    s1_u[j] += v
                    s2_u[j] += v * v
            # fold the dead-line constants in bulk (identical every dead scenario)
            for j in range(7):
                dv = dead_u[j]
                s1_u[j] += n_dead * dv
                s2_u[j] += n_dead * dv * dv
            # draw sentinels — recorded draws vs the structural formula
            expect = n_dead * 1 + n_alive * (1 + 2 * k + k * h)
            check("sentinel: total draws == structure (%s,%s,%d)" % (w["name"], row_name, c), draws == expect)
            check("sentinel: removal coins == AI-published titles (%s,%s,%d)" % (w["name"], row_name, c),
                  draws_coins == n_alive * k)  # AI-ALL AI-publishes all K per alive scenario (the CRN union); 0 for dead per the short-circuit
            check("sentinel: daily trials == published-title-days (%s,%s,%d)" % (w["name"], row_name, c),
                  draws_trials == n_alive * k * h)  # COMM-ALL publishes all K day 0, so the union is K*H per alive scenario
            check("sentinel: scenario tally (%s,%s,%d)" % (w["name"], row_name, c), n_alive + n_dead == n_scen)
            out.append({"row": row_name, "c": c, "s1": s1_u, "s2": s2_u,
                        "draws": draws, "n_dead": n_dead, "n_alive": n_alive})
    return out


def agreement(mc_cells, arma_cells, n_scen, abs_gate):
    """Per-(cell, policy) agreement legs: exact dev vs the registered absolute
    gate, the 4*SE headroom pre-check, and the statistical-consistency
    diagnostic. Returns per-leg records + gate booleans."""
    legs = []
    for mc, aa in zip(mc_cells, arma_cells):
        for j, pol in enumerate(POLICIES):
            mean_s = F(mc["s1"][j], 500 * n_scen)
            exact = aa["nets"][pol]
            dev = abs(mean_s - exact)
            sum1, sum2 = mc["s1"][j], mc["s2"][j]
            var_u = (sum2 - F(sum1 * sum1, n_scen)) / (n_scen - 1)
            sd_dollars = sqrt(float(var_u)) / 500.0
            se = sd_dollars / sqrt(n_scen)
            abs_ok = dev <= abs_gate
            headroom_ok = 4.0 * se <= float(abs_gate)
            stat_ok = float(dev) <= 4.0 * se or dev == 0
            legs.append({"row": mc["row"], "c": mc["c"], "policy": pol,
                         "dev": dev, "se": se, "sd": sd_dollars,
                         "abs_ok": abs_ok, "headroom_ok": headroom_ok,
                         "stat_ok": stat_ok, "mean_s": mean_s})
    gate_pass = all(l["abs_ok"] and l["headroom_ok"] for l in legs)
    stat_pass = all(l["stat_ok"] for l in legs)
    return legs, gate_pass, stat_pass


def mc_deltas(mc_cells, n_scen):
    """Delta-hat per cell from MC means (max non-PARK mean; PARK is exactly 0)."""
    deltas = []
    fams = []
    for mc in mc_cells:
        best_j = max(range(1, 7), key=lambda j: mc["s1"][j])
        deltas.append(F(mc["s1"][best_j], 500 * n_scen))
        fams.append(FAMILY[POLICIES[best_j]])
    return deltas, fams


# ---------------------------------------------------------------- gates F1-F5
def s(x):
    """Exact rational -> string for results.json."""
    x = F(x)
    return "%d/%d" % (x.numerator, x.denominator) if x.denominator != 1 else str(x.numerator)


def fl(x):
    return float(x)


results = {"registration": FIX["registration"], "gates": {}, "anomalies": []}

# F1 — normalization
check("F1: omega sums to 1", sum(OMEGA) == 1)
check("F1: omega' sums to 1", sum(OMEGA_U) == 1)
for name, p in PI_ROWS:
    check("F1: pi_L %s legal" % name, 0 <= p <= 1)
results["gates"]["F1"] = "pass"

# F2 — unit-economics recompute
r_re = F(60, 100) * F(1299, 100) - F(360, 100)
check("F2: r recompute = 2097/500", r_re == F(2097, 500) and r_re == R)
check("F2: |r - 419/100| = 1/250 <= 1/100", abs(R - F(419, 100)) == F(1, 250) <= F(1, 100))
results["gates"]["F2"] = "pass"

# headline Arm A
CELLS = arm_a_grid(HEADLINE)
MU = CELLS[0]["aux"]["mu"]
B_H = CELLS[0]["aux"]["B"]
V_CONT = CELLS[0]["aux"]["V_cont"]
P1_H = CELLS[0]["aux"]["P1"]
PQ_H = CELLS[0]["aux"]["Pq"]
check("mu_live = 143/1200", MU == F(143, 1200) and s(MU) == FIX["model"]["mu_live_expected"])
check("V_cont = mu*r*(H-W) exact", V_CONT == F(143, 1200) * R * 275 == F(1099527, 8000))
check("posterior alive-certainty on >=1 pilot sale (all rows)",
      all(posterior_alive_given_sale(HEADLINE, pl) == 1 for _, pl in PI_ROWS))
check("EV commit gate closed: V_cont < min c at headline", all(not cell["aux"]["ev_ok"] for cell in CELLS))

# F3 — dead-line identities at pi_L = 1
for c in C_COLS:
    nets, cp, _ = arm_a_cell(HEADLINE, F(1), c)
    check("F3: PARK 0 @ c=%d" % c, nets["PARK"] == 0)
    check("F3: AI-ALL -30 @ c=%d" % c, nets["AI-ALL"] == -30)
    check("F3: COMM-ALL -K*c @ c=%d" % c, nets["COMM-ALL"] == -K * c)
    check("F3: COMM pilots -c @ c=%d" % c, nets["COMM-PILOT-SALE"] == -c and nets["COMM-PILOT-EV"] == -c)
    check("F3: AI pilots -a @ c=%d" % c, nets["AI-PILOT-SALE"] == -30 and nets["AI-PILOT-EV"] == -30)
    check("F3: commit prob exactly 0 @ c=%d" % c, all(v == 0 for v in cp.values()))
results["gates"]["F3"] = "pass"

# F4 — hand world
hand_nets, _, hand_aux = arm_a_cell(HAND_WORLD, F(1, 2), F(3))
check("F4: hand E[p] = 1/4", (1 - F(1, 2)) * hand_aux["mu"] == F(1, 4))
check("F4: hand NET(AI-ALL) = 0 exactly", hand_nets["AI-ALL"] == 0)
results["gates"]["F4"] = "pass"

# F5(a) — COMM-ALL strictly decreasing in c
for ri in range(3):
    row = CELLS[3 * ri:3 * ri + 3]
    check("F5a: COMM-ALL strictly decreasing in c (row %d)" % ri,
          row[0]["nets"]["COMM-ALL"] > row[1]["nets"]["COMM-ALL"] > row[2]["nets"]["COMM-ALL"])
results["gates"]["F5a"] = "pass"

# F5(b) — registered universal form: EVERY policy's NET non-decreasing in
# alive share. Evaluated as registered over the grid rows (alpha 1/4 -> 3/4
# at fixed c), then the exact alpha-coefficients settle it analytically.
f5b_viol = []
for ci, c in enumerate(C_COLS):
    col = [CELLS[3 * ri + ci] for ri in (0, 1, 2)]  # rows SKEPTIC(1/4) NEUTRAL(1/2) HOPEFUL(3/4): alpha ascending
    for pol in POLICIES:
        seq = [cell["nets"][pol] for cell in col]
        if not (seq[0] <= seq[1] <= seq[2]):
            f5b_viol.append((pol, int(c)))
f5b_registered = gate("F5b (REGISTERED form): every policy non-decreasing in alive share", not f5b_viol)
# the corrected analytics — hard asserts making the defect reproducible:
coef_cps = {int(c): B_H + P1_H * (K - 1) * (V_CONT - c) for c in C_COLS}
coef_aps = {int(c): (1 - RHO) * (Q * B_H + PQ_H * (K - 1) * (V_CONT - c)) for c in C_COLS}
check("F5b-corrected: monotone policies non-decreasing in alpha",
      all((pol, int(c)) not in f5b_viol for pol in ("PARK", "COMM-ALL", "COMM-PILOT-EV", "AI-ALL", "AI-PILOT-EV") for c in C_COLS))
check("F5b-corrected: SALE pilots strictly DECREASING in alpha at every pinned c "
      "(alpha-coefficient B + P*(K-1)*(V_cont-c) < 0 — the sale-triggered commit "
      "to the strictly dominated channel converts good news into a bigger spend)",
      all(v < 0 for v in coef_cps.values()) and all(v < 0 for v in coef_aps.values())
      and sorted(set(p for p, _ in f5b_viol)) == ["AI-PILOT-SALE", "COMM-PILOT-SALE"])
if not f5b_registered:
    results["anomalies"].append({
        "id": "A1-F5b",
        "finding": "the registered F5(b) universal theorem ('every policy's NET "
                   "non-decreasing in the alive share') is FALSE at the pinned constants: "
                   "COMM-PILOT-SALE and AI-PILOT-SALE are strictly decreasing in alpha at "
                   "every pinned c. Proof from the registration's own pins: F3 forces "
                   "NET(COMM-PILOT-SALE)=-c at alpha=0, and the registered V_cont=137.44 < "
                   "min c=1500 makes the sale-triggered commit value-destroying, so more "
                   "alive => more committing => lower NET. alpha-coefficients (exact): "
                   "CPS " + ", ".join("c=%d: %s (~%.2f)" % (c, s(v), fl(v)) for c, v in coef_cps.items()) +
                   "; APS " + ", ".join("c=%d: %s (~%.2f)" % (c, s(v), fl(v)) for c, v in coef_aps.items()),
        "load_bearing": "registered gate (run invalid on any failure); decision numbers untouched (Delta rides AI-ALL, which is monotone)"})
results["gates"]["F5b_registered"] = "FAIL (registration defect A1-F5b)" if not f5b_registered else "pass"

# F5(c) — AI-ALL >= AI-PILOT-EV under shared-tool a=30 (all cells, and all alpha
# by the exact difference 4*(1-rho)*q*alpha*B >= 0); registered reverse under a=150.
for cell in CELLS:
    check("F5c: AI-ALL >= AI-PILOT-EV @ (%s,%d)" % (cell["row"], cell["c"]),
          cell["nets"]["AI-ALL"] >= cell["nets"]["AI-PILOT-EV"])
check("F5c: difference identity 4*(1-rho)*q*alpha*B", all(
    cell["nets"]["AI-ALL"] - cell["nets"]["AI-PILOT-EV"] == 4 * (1 - RHO) * Q * cell["aux"]["alpha"] * B_H
    for cell in CELLS))
A150 = [w for w in REPORT_WORLDS if w["name"] == "a_150"][0]
CELLS_A150 = arm_a_grid(A150)
rev_grid = [cell["nets"]["AI-PILOT-EV"] >= cell["nets"]["AI-ALL"] for cell in CELLS_A150]
f5c_registered = gate("F5c (REGISTERED reverse form under a=150): AI-PILOT-EV >= AI-ALL at the grid rows", all(rev_grid))
alpha_star = F(120) / (4 * (1 - RHO) * Q * B_H)
check("F5c-existence: dominance breaks by design under a=150 (alpha=0: -150 < -30; "
      "exact reversal threshold alpha* = " + s(alpha_star) + ")",
      arm_a_cell(A150, F(1), C_COLS[0])[0]["AI-PILOT-EV"] > arm_a_cell(A150, F(1), C_COLS[0])[0]["AI-ALL"]
      and alpha_star == F(240000000, 970482513) and alpha_star < F(1, 4))
skeptic_miss = CELLS_A150[0]["nets"]["AI-ALL"] - CELLS_A150[0]["nets"]["AI-PILOT-EV"]
check("F5c: SKEPTIC-row miss is exactly 10482513/8000000 (~$1.31)", skeptic_miss == F(10482513, 8000000))
if not f5c_registered:
    results["anomalies"].append({
        "id": "A2-F5c",
        "finding": "the registered F5(c) reverse assertion ('AI-ALL >= AI-PILOT-EV ... "
                   "asserted in reverse under the a=150 reporting world') FAILS at every "
                   "grid row: AI-ALL still beats AI-PILOT-EV by exactly 10482513/8000000 "
                   "(~$1.31) at SKEPTIC, ~$122.62 at NEUTRAL, ~$243.93 at HOPEFUL. The "
                   "dominance DOES break by design below the exact accounting threshold "
                   "alpha* = 240000000/970482513 (~0.24730) — a knife-edge 0.0027 BELOW "
                   "the SKEPTIC row's alpha=1/4. The 'breaks BY DESIGN' existence reading "
                   "holds; the grid-row reverse assertion as registered does not.",
        "load_bearing": "registered gate text (ambiguous between existence and grid-row form); reporting-side; decision numbers untouched"})
results["gates"]["F5c_registered_reverse"] = "FAIL (registration defect A2-F5c)" if not f5c_registered else "pass"
results["gates"]["F5c_shared_tool"] = "pass"
results["gates"]["F5a_note"] = "COMM-ALL strictly decreasing in c: pass on all rows"

# F5(d) — Delta column-independence, structural, whenever V_cont < min c
check("F5d: V_cont < min c at headline", V_CONT < min(C_COLS))
for ri in range(3):
    row = CELLS[3 * ri:3 * ri + 3]
    check("F5d: Delta row-constant / column-independent (row %d)" % ri,
          row[0]["delta"] == row[1]["delta"] == row[2]["delta"]
          and row[0]["argmax"] == row[1]["argmax"] == row[2]["argmax"] == "AI-ALL")
results["gates"]["F5d"] = "pass"

# ---------------------------------------------------------------- decision numbers (Arm A)
DELTAS = [cell["delta"] for cell in CELLS]
FAMS = [cell["family"] for cell in CELLS]
ev1 = evaluator_fraction(DELTAS, FAMS, SKEPTIC_IDX, M_MARGIN)
ev2 = evaluator_integer(DELTAS, FAMS, SKEPTIC_IDX, M_MARGIN)
check("twin evaluators agree (Arm A, m=100)", ev1 == ev2)
sweep = {}
for m in M_SWEEP:
    e1 = evaluator_fraction(DELTAS, FAMS, SKEPTIC_IDX, m)
    e2 = evaluator_integer(DELTAS, FAMS, SKEPTIC_IDX, m)
    check("twin evaluators agree (sweep m=%s)" % s(m), e1 == e2)
    sweep[int(m)] = e1

# break-even alive shares for AI-ALL (exact)
denom = K * (1 - RHO) * Q * B_H
be_margin = (A_TOOL + M_MARGIN) / denom
be_zero = A_TOOL / denom
check("AI-ALL break-even (margin) = 208000000/970482513", be_margin == F(208000000, 970482513))
check("AI-ALL break-even (zero) = 48000000/970482513", be_zero == F(48000000, 970482513))

# per-p conditional revenue split (given alive, per published title)
rev_split = [wi * pi / MU for wi, pi in zip(OMEGA, P_LIVE)]
check("per-p revenue split sums to 1", sum(rev_split) == 1)
check("per-p revenue split = 7/143,12/143,24/143,40/143,60/143",
      rev_split == [F(7, 143), F(12, 143), F(24, 143), F(40, 143), F(60, 143)])

# ---------------------------------------------------------------- reporting worlds (Arm A)
WORLD_CELLS = {}
WORLD_SHAPES = {}
for w in REPORT_WORLDS:
    wc = arm_a_grid(w)
    WORLD_CELLS[w["name"]] = wc
    check("EV commit gate closed in world %s (V_cont < min c)" % w["name"],
          all(not cell["aux"]["ev_ok"] for cell in wc))
    wd = [cell["delta"] for cell in wc]
    wf = [cell["family"] for cell in wc]
    we1 = evaluator_fraction(wd, wf, SKEPTIC_IDX, M_MARGIN)
    we2 = evaluator_integer(wd, wf, SKEPTIC_IDX, M_MARGIN)
    check("twin evaluators agree (world %s)" % w["name"], we1 == we2)
    WORLD_SHAPES[w["name"]] = we1

# ---------------------------------------------------------------- Arm S runs
RNG_MAIN = random.Random(SEED_MAIN)
MC_MAIN = mc_leg(HEADLINE, RNG_MAIN, N_MAIN, CELLS)
LEGS_MAIN, GATE_MAIN, STAT_MAIN = agreement(MC_MAIN, CELLS, N_MAIN, F(10))
gate("F6-agreement (REGISTERED): |dev| <= $10 AND 4*SE <= $10 on every (cell,policy), main leg", GATE_MAIN)
gate("F6-agreement diagnostic: arms statistically consistent (|dev| <= 4*SE) on all 63 main legs", STAT_MAIN)

RNG_STAB = random.Random(SEED_STAB)
MC_STAB = mc_leg(HEADLINE, RNG_STAB, N_STAB, CELLS)
LEGS_STAB, GATE_STAB, STAT_STAB = agreement(MC_STAB, CELLS, N_STAB, F(25))
gate("F6-agreement (REGISTERED): |dev| <= $25 AND 4*SE <= $25 on every (cell,policy), stability leg", GATE_STAB)
gate("F6-agreement diagnostic: arms statistically consistent on all 63 stability legs", STAT_STAB)

RNG_REPORT = random.Random(SEED_REPORT)
REPORT_MC = {}
for w in REPORT_WORLDS:
    mc = mc_leg(w, RNG_REPORT, N_REPORT, WORLD_CELLS[w["name"]])
    legs, _, stat_ok = agreement(mc, WORLD_CELLS[w["name"]], N_REPORT, F(25))
    gate("reporting world %s: arms statistically consistent (|dev| <= 4*SE, 63 legs)" % w["name"], stat_ok)
    REPORT_MC[w["name"]] = {"legs": legs, "mc": mc}

RNG_AUX = random.Random(SEED_AUX)  # constructed LAST, never read
check("aux seed 20261356 never read (state == fresh)", RNG_AUX.getstate() == random.Random(SEED_AUX).getstate())

# ---------------------------------------------------------------- stability reproduction
STAB_DELTAS, STAB_FAMS = mc_deltas(MC_STAB, N_STAB)
sev1 = evaluator_fraction(STAB_DELTAS, STAB_FAMS, SKEPTIC_IDX, M_MARGIN)
sev2 = evaluator_integer(STAB_DELTAS, STAB_FAMS, SKEPTIC_IDX, M_MARGIN)
check("twin evaluators agree (stability estimates)", sev1 == sev2)
MAIN_DELTAS_S, MAIN_FAMS_S = mc_deltas(MC_MAIN, N_MAIN)
mev1 = evaluator_fraction(MAIN_DELTAS_S, MAIN_FAMS_S, SKEPTIC_IDX, M_MARGIN)
mev2 = evaluator_integer(MAIN_DELTAS_S, MAIN_FAMS_S, SKEPTIC_IDX, M_MARGIN)
check("twin evaluators agree (main MC estimates)", mev1 == mev2)

# ---------------------------------------------------------------- classification
RUN_VALID = f5b_registered and f5c_registered and GATE_MAIN and GATE_STAB
stab_reproduces = (sev1["reject_shape"] == ev1["reject_shape"] and
                   sev1["approve_shape"] == ev1["approve_shape"])
check("stability leg reproduces the Arm-A shape through twin evaluators", stab_reproduces)
CLASS_1 = classify(ev1, RUN_VALID, stab_reproduces)
CLASS_2 = classify(ev2, RUN_VALID, stab_reproduces)
check("twin evaluators agree on the final class", CLASS_1 == CLASS_2)
CLASS_STAB_1 = classify(sev1, RUN_VALID, stab_reproduces)
CLASS_STAB_2 = classify(sev2, RUN_VALID, stab_reproduces)
check("stability leg lands the same class through both evaluators", CLASS_STAB_1 == CLASS_STAB_2 == CLASS_1)

# NULL-axis disposition (all six registered axes, evaluated honestly)
over_by_row = [sum(1 for i in range(3 * ri, 3 * ri + 3) if DELTAS[i] >= M_MARGIN) for ri in range(3)]
over_by_col = [sum(1 for ri in range(3) if DELTAS[3 * ri + ci] >= M_MARGIN) for ci in range(3)]
axes = {
    "belief-conditional": ev1["over"] < 9 and over_by_row[0] < 3,
    "cost-conditional": len(set(over_by_col)) > 1,
    "family-split": len(ev1["families_over"]) > 1,
    "margin-thin": sweep[25]["reject_shape"] != sweep[400]["reject_shape"],
    "arm-disagreement (agreement gate fails; the defect is the finding)": not (GATE_MAIN and GATE_STAB),
    "sensitivity-straddle": any(not WORLD_SHAPES[w["name"]]["reject_shape"] for w in REPORT_WORLDS),
}
BINDING_AXIS = ("arm-disagreement (agreement gate fails; the defect is the finding)"
                if not (GATE_MAIN and GATE_STAB) else
                next((k for k, v in axes.items() if v), "none"))

# agreement-gate summary + the A3 finding (composed before the drafter block
# so the defect list is complete)
worst_main = max(LEGS_MAIN, key=lambda l: fl(l["dev"]))
worst_head = max(LEGS_MAIN, key=lambda l: l["se"])
n_abs_fail = sum(1 for l in LEGS_MAIN if not l["abs_ok"])
n_head_fail = sum(1 for l in LEGS_MAIN if not l["headroom_ok"])
SALE_POLICIES = {"COMM-PILOT-SALE", "AI-PILOT-SALE"}
check("agreement pattern: headroom failures are exactly the 18 SALE-pilot legs (main)",
      n_head_fail == 18 and all(l["policy"] in SALE_POLICIES for l in LEGS_MAIN if not l["headroom_ok"]))
check("agreement pattern: every abs-clause breach is a SALE-pilot leg (main)",
      all(l["policy"] in SALE_POLICIES for l in LEGS_MAIN if not l["abs_ok"]))
check("agreement pattern: every DECISION-bearing AI-ALL leg passes the registered $10 clause with headroom",
      all(l["abs_ok"] and l["headroom_ok"] for l in LEGS_MAIN if l["policy"] == "AI-ALL"))
if not GATE_MAIN or not GATE_STAB:
    results["anomalies"].append({
        "id": "A3-agreement-gate",
        "finding": "the registered Arm-S agreement gate (|dev| <= $10 absolute on every "
                   "(cell,policy) with >= 4*SE headroom, main leg; <= $25 stability leg) is "
                   "unsatisfiable at the registered N for the two SALE-pilot policies: their "
                   "per-scenario net carries a +-(K-1)*(c-V_cont) commit jump (~$5,450 at "
                   "c=1500 up to ~$19,250 at c=4950), so the per-scenario SD reaches ~$9,000 "
                   "and 4*SE at N=200,000 reaches ~$80 >> $10 (headroom pre-check fails on "
                   "exactly the 18 SALE legs; %d main legs also breach the absolute clause). "
                   "The arms themselves are statistically consistent (|dev| <= 4*SE) on "
                   "%d/63 main and %d/63 stability legs, and every DECISION-bearing leg "
                   "(AI-ALL, the Delta carrier) passes the registered $10 clause with "
                   "headroom. The gate constant, not the arms, is the defect."
                   % (n_abs_fail,
                      sum(1 for l in LEGS_MAIN if l["stat_ok"]),
                      sum(1 for l in LEGS_STAB if l["stat_ok"])),
        "load_bearing": "registered invalidating gate — forces the NULL(axis v) classification"})

# drafter-reference comparison — never gated
DR = FIX["reporting_numbers"]["drafter_reference_never_gated"]
drafter = {
    "delta_SKEPTIC_matches": s(DELTAS[0]) == DR["delta_SKEPTIC"],
    "delta_NEUTRAL_matches": s(DELTAS[3]) == DR["delta_NEUTRAL"],
    "delta_HOPEFUL_matches": s(DELTAS[6]) == DR["delta_HOPEFUL"],
    "argmax_AI_ALL_9_of_9": all(cell["argmax"] == "AI-ALL" for cell in CELLS),
    "reject_shape_9_of_9": ev1["over"] == 9 and ev1["reject_shape"],
    "V_cont_matches_disclosed_2dp": abs(fl(V_CONT) - 137.44) < 0.005,
    "V_cont_exact": s(V_CONT),
    "ai_pilot_ev_skeptic": s(CELLS[0]["nets"]["AI-PILOT-EV"]),
    "ai_pilot_ev_skeptic_matches_033": abs(fl(CELLS[0]["nets"]["AI-PILOT-EV"]) - 0.33) < 0.005,
    "a150_world_6_of_9_matches": WORLD_SHAPES["a_150"]["over"] == 6,
    "q_half_world_6_of_9_matches": WORLD_SHAPES["q_1_2"]["over"] == 6,
    "undisclosed_H180_also_6_of_9": WORLD_SHAPES["H180"]["over"] == 6,
    "registered_gate_defects_found": [a["id"] for a in results["anomalies"]],
}

# ---------------------------------------------------------------- results.json
def leg_out(l):
    return {"row": l["row"], "c": l["c"], "policy": l["policy"],
            "dev_exact": s(l["dev"]), "dev": fl(l["dev"]), "se": l["se"], "sd": l["sd"],
            "abs_ok": l["abs_ok"], "headroom_ok": l["headroom_ok"], "stat_ok": l["stat_ok"],
            "mean_S": s(l["mean_s"])}


results.update({
    "environment": {"cpython": "3.11", "arm_A": "platform-independent exact rationals",
                    "stdlib_only": True, "hermetic": "reads only its own fixtures.json"},
    "arm_A": {
        "mu_live": s(MU), "B_per_title_day0": s(B_H), "V_cont_c_star": s(V_CONT),
        "P1_commit_given_alive": s(P1_H), "Pq_commit_given_alive": s(PQ_H),
        "table_9x7": [{
            "row": cell["row"], "pi_L": s(cell["pi_L"]), "c": int(cell["c"]),
            "nets": {p: s(cell["nets"][p]) for p in POLICIES},
            "nets_float": {p: round(fl(cell["nets"][p]), 6) for p in POLICIES},
            "delta": s(cell["delta"]), "delta_float": round(fl(cell["delta"]), 6),
            "argmax": cell["argmax"], "family": cell["family"],
            "commit_prob": {p: s(v) for p, v in cell["commit_prob"].items()},
        } for cell in CELLS],
        "break_even_alive_share_margin": s(be_margin),
        "break_even_alive_share_margin_float": fl(be_margin),
        "break_even_alive_share_zero": s(be_zero),
        "break_even_alive_share_zero_float": fl(be_zero),
        "per_p_revenue_split": [s(x) for x in rev_split],
        "f5b_alpha_coefficients": {"COMM-PILOT-SALE": {str(c): s(v) for c, v in coef_cps.items()},
                                   "AI-PILOT-SALE": {str(c): s(v) for c, v in coef_aps.items()}},
        "f5c_alpha_star_a150": s(alpha_star),
        "f5c_skeptic_miss_a150": s(skeptic_miss),
    },
    "decision": {
        "shape_evaluator_1": ev1, "shape_evaluator_2": ev2,
        "margin_sweep": {str(m): sweep[m] for m in (25, 400)},
        "run_valid": RUN_VALID,
        "validity_flags": {"F5b_registered": f5b_registered,
                           "F5c_registered_reverse": f5c_registered,
                           "agreement_gate_main": GATE_MAIN,
                           "agreement_gate_stability": GATE_STAB},
        "stability_reproduces_shape": stab_reproduces,
        "final_class": CLASS_1,
        "binding_null_axis": BINDING_AXIS,
        "null_axes_disposition": axes,
        "rules_applied_in_order": "REJECT checked first: its arithmetic shape holds "
            "(Delta >= 100 in 9/9 cells, family AI-led in every over-margin cell) but the "
            "registered validity gates fail (run invalid on any failure), so no ruling can "
            "issue; the registered NULL axis (v) carries the outcome with the defect as the finding.",
    },
    "arm_S": {
        "main": {"seed": SEED_MAIN, "N_per_cell": N_MAIN,
                 "gate_pass": GATE_MAIN, "stat_consistent": STAT_MAIN,
                 "legs": [leg_out(l) for l in LEGS_MAIN],
                 "mc_deltas": [s(d) for d in MAIN_DELTAS_S],
                 "mc_shape": mev1},
        "stability": {"seed": SEED_STAB, "N_per_cell": N_STAB,
                      "gate_pass": GATE_STAB, "stat_consistent": STAT_STAB,
                      "legs": [leg_out(l) for l in LEGS_STAB],
                      "mc_deltas": [s(d) for d in STAB_DELTAS],
                      "mc_shape": sev1, "class_through_twins": CLASS_STAB_1},
        "aux_seed_never_read": SEED_AUX,
    },
    "reporting_worlds": {w["name"]: {
        "shape_m100": WORLD_SHAPES[w["name"]],
        "table": [{"row": cell["row"], "c": int(cell["c"]),
                   "delta": s(cell["delta"]), "delta_float": round(fl(cell["delta"]), 6),
                   "argmax": cell["argmax"], "family": cell["family"]} for cell in WORLD_CELLS[w["name"]]],
        "arm_S_worst_dev": max((fl(l["dev"]) for l in REPORT_MC[w["name"]]["legs"])),
        "arm_S_stat_consistent": all(l["stat_ok"] for l in REPORT_MC[w["name"]]["legs"]),
    } for w in REPORT_WORLDS},
    "drafter_reference_comparison_never_gated": drafter,
})

results["arm_S"]["main"]["summary"] = {
    "worst_dev": fl(worst_main["dev"]), "worst_dev_leg": "%s/%s/%s" % (worst_main["row"], worst_main["c"], worst_main["policy"]),
    "worst_4se": 4 * worst_head["se"], "worst_4se_leg": "%s/%s/%s" % (worst_head["row"], worst_head["c"], worst_head["policy"]),
    "abs_gate_failures": n_abs_fail, "headroom_failures": n_head_fail,
}

# ---------------------------------------------------------------- stdout
print("VERDICT 065 SIM — illustration gate (PROPOSAL 054)")
print("cpython pinned: 3.11 | stdlib-only | hermetic (fixtures.json only)")
print("mu_live = %s | B = %s (~%.6f) | V_cont = c* = %s (~%.6f)" % (s(MU), s(B_H), fl(B_H), s(V_CONT), fl(V_CONT)))
print("P1 = %.9f | Pq = %.9f (exact rationals in results.json)" % (fl(P1_H), fl(PQ_H)))
print("")
print("ARM A 9x7 NET table (dollars, floats; exact Fractions in results.json):")
hdr = "cell            " + "".join("%16s" % p for p in POLICIES)
print(hdr)
for cell in CELLS:
    print("%-8s c=%-6d" % (cell["row"], cell["c"]) +
          "".join("%16.4f" % fl(cell["nets"][p]) for p in POLICIES))
print("")
for ri, (row_name, _) in enumerate(PI_ROWS):
    cell = CELLS[3 * ri]
    print("Delta %-8s = %s (~$%.4f), argmax %s [%s], row-constant across c" %
          (row_name, s(cell["delta"]), fl(cell["delta"]), cell["argmax"], cell["family"]))
print("AI-ALL break-even alive-share: margin %s (~%.6f), zero %s (~%.6f)" %
      (s(be_margin), fl(be_margin), s(be_zero), fl(be_zero)))
print("per-p revenue split (given alive): " + ", ".join(s(x) for x in rev_split))
print("")
print("REJECT-shape arithmetic (Arm A): over-margin %d/9, families %s -> shape %s (twins agree)" %
      (ev1["over"], ",".join(ev1["families_over"]), ev1["reject_shape"]))
print("margin sweep: m=25 reject-shape %s | m=400 reject-shape %s (over=%d)" %
      (sweep[25]["reject_shape"], sweep[400]["reject_shape"], sweep[400]["over"]))
print("")
print("ARM S main (seed %d, N=%d/cell): abs-gate failures %d/63, headroom failures %d/63," %
      (SEED_MAIN, N_MAIN, n_abs_fail, n_head_fail))
print("  statistically consistent (|dev|<=4*SE): %s | worst dev $%.4f @ %s | worst 4*SE $%.4f @ %s" %
      (STAT_MAIN, results["arm_S"]["main"]["summary"]["worst_dev"],
       results["arm_S"]["main"]["summary"]["worst_dev_leg"],
       results["arm_S"]["main"]["summary"]["worst_4se"],
       results["arm_S"]["main"]["summary"]["worst_4se_leg"]))
print("  REGISTERED gate (<=$10 AND 4*SE<=$10 on every leg): %s" % ("PASS" if GATE_MAIN else "FAIL"))
print("ARM S stability (seed %d, N=%d/cell): REGISTERED gate (<=$25): %s | stat consistent: %s | shape reproduces: %s" %
      (SEED_STAB, N_STAB, "PASS" if GATE_STAB else "FAIL", STAT_STAB, stab_reproduces))
print("reporting worlds (seed %d, N=%d/cell/world): all stat-consistent: %s" %
      (SEED_REPORT, N_REPORT, all(all(l["stat_ok"] for l in REPORT_MC[w["name"]]["legs"]) for w in REPORT_WORLDS)))
print("  over-margin counts per world: " + ", ".join("%s=%d" % (w["name"], WORLD_SHAPES[w["name"]]["over"]) for w in REPORT_WORLDS))
print("")
print("GATES: F1 pass | F2 pass | F3 pass | F4 pass | F5a pass | F5b-registered %s | F5c-shared-tool pass | F5c-registered-reverse(a150) %s | F5d pass | sentinels pass | twins pass" %
      ("FAIL" if not f5b_registered else "pass", "FAIL" if not f5c_registered else "pass"))
print("VALIDITY: run_valid=%s (registered 'run invalid on any failure')" % RUN_VALID)
print("")
print("DRAFTER COMPARISON (never gated): " + json.dumps(drafter, sort_keys=True))
print("")
print("FINAL CLASS (rules in order, REJECT first, twins agree): %s" % CLASS_1)
print("BINDING NULL AXIS: %s" % BINDING_AXIS)
print("anomalies: " + ", ".join(a["id"] for a in results["anomalies"]))
print("")
print("SELF-CHECKS: %d passed, %d failed (recorded registered-gate defects: %s)" %
      (CHECKS_PASSED, len(RECORDED_FAILURES), "; ".join(RECORDED_FAILURES) if RECORDED_FAILURES else "none"))

results["self_checks"] = {"passed": CHECKS_PASSED, "recorded_failures": RECORDED_FAILURES}

with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=1, sort_keys=True, default=str)
    fh.write("\n")
